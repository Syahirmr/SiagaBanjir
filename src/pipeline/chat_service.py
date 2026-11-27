"""Orkestrator linear end-to-end SiagaBanjir (WF-019, WF-020, WF-023, WF-024).

Alur deterministik sesuai docs/ARCHITECTURE.md v0.2:
  Validator -> Safety Guard -> Mode Router (rag / baseline)
    - rag: Retriever -> Evidence Gate -> Prompt Builder -> LLM Adapter -> Citation Verifier -> Logger
    - baseline: Prompt Builder (tanpa retrieval) -> LLM Adapter -> Logger

Memisahkan secara tegas 3 kategori kegagalan:
- `api_error`
- `retrieval_error`
- `abstention_insufficient_evidence`
"""

from __future__ import annotations

import re
import time

from src.config import AppConfig
from src.llm.client import LLMProviderAdapter
from src.llm.prompts import build_baseline_messages, build_rag_messages
from src.logging.eval_logger import StructuredJsonlLogger
from src.retrieval.retriever import BM25CorpusRetriever
from src.safety.guard import SafetyGuard
from src.schemas import (
    ChatRequest,
    ChatResponse,
    LLMCallResult,
    OutcomeType,
    RetrievalResult,
    RetrievedChunk,
)

_CITATION_MARKER_RE = re.compile(r"\[SUMBER\s+(\d+)\]", re.IGNORECASE)

ABSTENTION_NO_EVIDENCE_MESSAGE = (
    "Maaf, informasi yang Anda tanyakan belum tersedia atau tidak memiliki bukti "
    "yang cukup di dalam korpus dokumen resmi SiagaBanjir saat ini.\n\n"
    "Agar tidak memberikan informasi yang tidak akurat, SiagaBanjir tidak "
    "menjawab di luar dokumen sumber. Untuk informasi lebih lanjut atau detail "
    "wilayah tertentu, silakan merujuk langsung ke kanal resmi **BNPB**, "
    "**BPBD** setempat, atau **BMKG**."
)

RETRIEVAL_CORPUS_UNAVAILABLE_MESSAGE = (
    "Korpus dokumen resmi SiagaBanjir belum tersedia pada lingkungan lokal ini "
    "(berkas `corpus_manifest.json` / `chunks.jsonl` belum tersedia). "
    "Untuk menguji percakapan tanpa korpus, silakan pilih mode "
    "**Baseline (Tanpa Retrieval)** pada sidebar."
)

RETRIEVAL_ERROR_MESSAGE = (
    "Maaf, sistem mengalami kendala teknis saat memuat indeks korpus lokal "
    "sehingga pertanyaan belum dapat diproses berbasis sumber resmi. "
    "Silakan periksa format berkas korpus atau gunakan mode **Baseline**."
)

API_ERROR_MESSAGE = (
    "Maaf, layanan model bahasa sedang mengalami kendala pemrosesan. "
    "Silakan periksa konfigurasi atau coba beberapa saat lagi."
)


def format_api_error_message(error_type: str | None, provider: str | None) -> str:
    """Menyusun pesan error ramah pengguna sesuai penyebab aktual tanpa membocorkan secret."""
    prov_label = provider or "LLM"
    if error_type == "config_error":
        return (
            f"Konfigurasi model untuk provider `{prov_label}` belum ditetapkan "
            "pada berkas `.env` lokal (`PRIMARY_MODEL` masih placeholder). "
            "Atur nama model yang valid pada `.env` lokal lalu coba lagi."
        )
    if error_type == "auth_error":
        return (
            f"Autentikasi ke provider `{prov_label}` gagal. Pastikan API key "
            "sudah terisi dengan benar pada berkas `.env` lokal."
        )
    if error_type == "rate_limit":
        return (
            f"Batas kuota (rate limit) provider `{prov_label}` sementara tercapai. "
            "Silakan tunggu sejenak lalu coba kembali."
        )
    if error_type == "timeout":
        return (
            f"Permintaan ke provider `{prov_label}` melebihi batas waktu tunggu "
            "(timeout). Silakan coba beberapa saat lagi."
        )
    if error_type == "network_error":
        return (
            f"Tidak dapat terhubung ke layanan `{prov_label}` karena gangguan "
            "koneksi jaringan. Periksa koneksi internet Anda lalu coba lagi."
        )
    if error_type == "provider_error":
        return (
            f"Layanan provider `{prov_label}` sedang mengalami kendala sementara "
            "(misalnya server sibuk atau model tidak tersedia). Silakan coba lagi."
        )
    return API_ERROR_MESSAGE


def format_retrieval_error_message(error_message: str | None) -> str:
    """Membedakan korpus belum tersedia vs kerusakan teknis indeks."""
    if error_message and "FileNotFoundError" in error_message:
        return RETRIEVAL_CORPUS_UNAVAILABLE_MESSAGE
    return RETRIEVAL_ERROR_MESSAGE

_SAFETY_OUTCOME_MAP: dict[str, OutcomeType] = {
    "empty_input": "clarification_requested",
    "acute_emergency": "emergency_override",
    "prediction_request": "prediction_refused",
    "ambiguous": "clarification_requested",
    "out_of_domain": "out_of_domain_refused",
}


def verify_and_extract_citations(
    answer_text: str,
    retrieved_chunks: list[RetrievedChunk],
) -> tuple[list[str], list[str]]:
    """Memetakan `[SUMBER n]` pada jawaban ke metadata chunk secara deterministik.

    Mengembalikan `(citations_returned, citation_anomalies)`:
    - `citations_returned`: daftar teks sitasi valid yang benar-benar dirujuk
      dalam jawaban (dibedakan dari seluruh `retrieved_sources`).
    - `citation_anomalies`: penanda `[SUMBER k]` di luar rentang konteks yang
      dikirim (indikasi percobaan fabrikasi sitasi oleh model).
    """
    citations_returned: list[str] = []
    seen_indices: set[int] = set()
    anomalies: list[str] = []

    for match in _CITATION_MARKER_RE.finditer(answer_text or ""):
        num = int(match.group(1))
        if 1 <= num <= len(retrieved_chunks):
            if num not in seen_indices:
                seen_indices.add(num)
                citations_returned.append(retrieved_chunks[num - 1].format_citation())
        else:
            marker = f"[SUMBER {num}]"
            if marker not in anomalies:
                anomalies.append(marker)

    return citations_returned, anomalies


class ChatService:
    """Layanan inti pemrosesan pesan untuk UI Streamlit & Evaluation Runner."""

    def __init__(
        self,
        config: AppConfig,
        llm_adapter: LLMProviderAdapter,
        retriever: BM25CorpusRetriever | None = None,
        safety_guard: SafetyGuard | None = None,
        logger: StructuredJsonlLogger | None = None,
    ) -> None:
        self.config = config
        self.llm_adapter = llm_adapter
        self.retriever = retriever
        self.safety_guard = safety_guard or SafetyGuard()
        self.logger = logger

    def handle_request(self, request: ChatRequest) -> ChatResponse:
        """Menjalankan 1 permintaan secara end-to-end dan mencatat log jika aktif."""
        started = time.perf_counter()

        # 1. Jalur Baseline (Kondisi A Eksperimen — tanpa retrieval & tanpa safety override khusus RAG)
        if request.mode == "baseline":
            return self._handle_baseline(request, started)

        # 2. Jalur RAG: Safety Pre-Check Guard sebelum retrieval/LLM (FR-01, FR-05, FR-07, FR-08)
        safety = self.safety_guard.check(request.user_query)
        if safety.bypass_llm:
            outcome = _SAFETY_OUTCOME_MAP[safety.category]
            retrieval_bypass = RetrievalResult(
                status="bypassed_safety",
                corpus_version=self.retriever.corpus_version if self.retriever else None,
                chunks=[],
            )
            response = ChatResponse(
                request_id=request.request_id,
                mode="rag",
                outcome_type=outcome,
                answer_text=safety.override_message or "",
                citations=[],
                retrieved_sources=[],
                safety_category=safety.category,
                corpus_version=retrieval_bypass.corpus_version,
                prompt_version=self.config.prompt_version,
                provider_actual=None,
                model_actual=None,
                fallback_used=False,
                api_status="bypassed",
                error_type=None,
                latency_sec=round(time.perf_counter() - started, 4),
            )
            self._write_log(request, response, retrieval=retrieval_bypass, llm_result=None)
            return response

        # 3. Retrieval korpus frozen & Evidence Gate (FR-03, FR-05)
        if self.retriever is None:
            retrieval = RetrievalResult(
                status="error",
                corpus_version=None,
                chunks=[],
                error_message="Retriever belum diinisialisasi.",
            )
        else:
            retrieval = self.retriever.retrieve(request.user_query)

        if retrieval.status == "error":
            response = ChatResponse(
                request_id=request.request_id,
                mode="rag",
                outcome_type="retrieval_error",
                answer_text=format_retrieval_error_message(retrieval.error_message),
                citations=[],
                retrieved_sources=[],
                safety_category="normal",
                corpus_version=retrieval.corpus_version,
                prompt_version=self.config.prompt_version,
                provider_actual=None,
                model_actual=None,
                fallback_used=False,
                api_status="bypassed",
                error_type="index_error",
                latency_sec=round(time.perf_counter() - started, 4),
            )
            self._write_log(request, response, retrieval=retrieval, llm_result=None)
            return response

        if retrieval.status == "empty" or not retrieval.chunks:
            response = ChatResponse(
                request_id=request.request_id,
                mode="rag",
                outcome_type="abstention_insufficient_evidence",
                answer_text=ABSTENTION_NO_EVIDENCE_MESSAGE,
                citations=[],
                retrieved_sources=[],
                safety_category="normal",
                corpus_version=retrieval.corpus_version,
                prompt_version=self.config.prompt_version,
                provider_actual=None,
                model_actual=None,
                fallback_used=False,
                api_status="bypassed",
                error_type=None,
                latency_sec=round(time.perf_counter() - started, 4),
            )
            self._write_log(request, response, retrieval=retrieval, llm_result=None)
            return response

        # 4. Prompt Builder (isolasi <retrieved_context>) & panggilan LLM (FR-02, FR-09)
        messages = build_rag_messages(
            user_query=request.user_query,
            chunks=retrieval.chunks,
            prompt_version=self.config.prompt_version,
        )
        llm_res = self.llm_adapter.generate(
            messages=messages,
            allow_fallback=request.allow_fallback,
        )
        retrieved_summary = [c.to_log_dict() for c in retrieval.chunks]

        if llm_res.api_status != "success" or not llm_res.raw_text:
            err_kind = llm_res.error_type or "provider_error"
            response = ChatResponse(
                request_id=request.request_id,
                mode="rag",
                outcome_type="api_error",
                answer_text=format_api_error_message(err_kind, llm_res.provider_actual),
                citations=[],
                retrieved_sources=retrieved_summary,
                safety_category="normal",
                corpus_version=retrieval.corpus_version,
                prompt_version=self.config.prompt_version,
                provider_actual=llm_res.provider_actual,
                model_actual=llm_res.model_actual,
                fallback_used=llm_res.fallback_used,
                api_status="error",
                error_type=err_kind,
                latency_sec=round(time.perf_counter() - started, 4),
            )
            self._write_log(request, response, retrieval=retrieval, llm_result=llm_res)
            return response

        # 5. Verifikasi sitasi deterministik (FR-04)
        citations_returned, anomalies = verify_and_extract_citations(
            answer_text=llm_res.raw_text,
            retrieved_chunks=retrieval.chunks,
        )
        notice = None
        if llm_res.fallback_used:
            notice = (
                f"Catatan: Respons dilayani oleh provider cadangan "
                f"({llm_res.provider_actual}) karena provider utama sedang terkendala."
            )

        response = ChatResponse(
            request_id=request.request_id,
            mode="rag",
            outcome_type="answered_grounded",
            answer_text=llm_res.raw_text,
            citations=citations_returned,
            retrieved_sources=retrieved_summary,
            citation_anomalies=anomalies,
            safety_category="normal",
            corpus_version=retrieval.corpus_version,
            prompt_version=self.config.prompt_version,
            provider_actual=llm_res.provider_actual,
            model_actual=llm_res.model_actual,
            fallback_used=llm_res.fallback_used,
            api_status="success",
            error_type=None,
            latency_sec=round(time.perf_counter() - started, 4),
            user_notice=notice,
        )
        self._write_log(request, response, retrieval=retrieval, llm_result=llm_res)
        return response

    def _handle_baseline(self, request: ChatRequest, started: float) -> ChatResponse:
        retrieval_na = RetrievalResult(
            status="not_applicable", corpus_version=None, chunks=[]
        )
        if not request.user_query or not request.user_query.strip():
            response = ChatResponse(
                request_id=request.request_id,
                mode="baseline",
                outcome_type="clarification_requested",
                answer_text="Pertanyaan kosong.",
                safety_category="empty_input",
                corpus_version=None,
                prompt_version=self.config.prompt_version,
                api_status="bypassed",
                latency_sec=round(time.perf_counter() - started, 4),
            )
            self._write_log(request, response, retrieval=retrieval_na, llm_result=None)
            return response

        messages = build_baseline_messages(
            user_query=request.user_query,
            prompt_version=self.config.prompt_version,
        )
        llm_res = self.llm_adapter.generate(
            messages=messages,
            allow_fallback=request.allow_fallback,
        )
        if llm_res.api_status != "success" or not llm_res.raw_text:
            err_kind = llm_res.error_type or "provider_error"
            response = ChatResponse(
                request_id=request.request_id,
                mode="baseline",
                outcome_type="api_error",
                answer_text=format_api_error_message(err_kind, llm_res.provider_actual),
                safety_category="normal",
                corpus_version=None,
                prompt_version=self.config.prompt_version,
                provider_actual=llm_res.provider_actual,
                model_actual=llm_res.model_actual,
                fallback_used=llm_res.fallback_used,
                api_status="error",
                error_type=err_kind,
                latency_sec=round(time.perf_counter() - started, 4),
            )
            self._write_log(request, response, retrieval=retrieval_na, llm_result=llm_res)
            return response

        response = ChatResponse(
            request_id=request.request_id,
            mode="baseline",
            outcome_type="answered_baseline",
            answer_text=llm_res.raw_text,
            citations=[],
            retrieved_sources=[],
            safety_category="normal",
            corpus_version=None,
            prompt_version=self.config.prompt_version,
            provider_actual=llm_res.provider_actual,
            model_actual=llm_res.model_actual,
            fallback_used=llm_res.fallback_used,
            api_status="success",
            error_type=None,
            latency_sec=round(time.perf_counter() - started, 4),
        )
        self._write_log(request, response, retrieval=retrieval_na, llm_result=llm_res)
        return response

    def _write_log(
        self,
        request: ChatRequest,
        response: ChatResponse,
        retrieval: RetrievalResult | None,
        llm_result: LLMCallResult | None,
    ) -> None:
        if self.logger is not None:
            self.logger.log(
                request=request,
                response=response,
                retrieval=retrieval,
                llm_result=llm_result,
            )
