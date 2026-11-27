"""Logger JSONL terstruktur, sanitasi privasi, dan verifikator log (FR-11 / WF-025).

Mengacu pada docs/ARCHITECTURE.md v0.2 Bagian 12:
- 1 baris JSON UTF-8 per request.
- Zero credentials: menyaring API key/header auth sebelum menulis ke disk.
- Minimisasi PII pada `run_context="demo"` (masking email & nomor telepon).
- Validator paritas eksperimen (`validate_experiment_logs`) untuk gate WF-031 -> WF-032.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import sanitize_secret_text
from src.schemas import (
    ChatRequest,
    ChatResponse,
    LLMCallResult,
    RetrievalResult,
)

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+62|62|0)8[1-9][0-9\-\s]{6,13}(?!\d)")


def mask_pii_for_demo(text: str | None) -> str | None:
    """Menyamarkan pola email dan nomor ponsel yang mungkin diketik pengguna di demo."""
    if text is None:
        return None
    masked = _EMAIL_RE.sub("[EMAIL_MASKED]", text)
    masked = _PHONE_RE.sub("[PHONE_MASKED]", masked)
    return masked


class StructuredJsonlLogger:
    """Menulis record evaluasi & demo ke berkas JSONL terstruktur tanpa kredensial."""

    def __init__(
        self,
        log_path: str | Path,
        known_secrets: tuple[str | None, ...] = (),
        strict_demo_privacy: bool = False,
    ) -> None:
        self.log_path = Path(log_path)
        self._secrets = known_secrets
        self._strict_demo_privacy = strict_demo_privacy

    def build_record(
        self,
        request: ChatRequest,
        response: ChatResponse,
        retrieval: RetrievalResult | None = None,
        llm_result: LLMCallResult | None = None,
        timestamp_utc: str | None = None,
    ) -> dict[str, Any]:
        """Membentuk 1 record JSONL sesuai skema ARCHITECTURE.md Bag. 12.1."""
        ts = timestamp_utc or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        query_logged: str | None = sanitize_secret_text(
            request.user_query, self._secrets
        )
        response_logged: str | None = sanitize_secret_text(
            response.answer_text, self._secrets
        )
        if request.run_context == "demo":
            if self._strict_demo_privacy:
                query_logged = "[OMITTED_STRICT_PRIVACY]"
            else:
                query_logged = mask_pii_for_demo(query_logged)
            response_logged = mask_pii_for_demo(response_logged)

        retrieval_status = (
            retrieval.status
            if retrieval is not None
            else ("not_applicable" if request.mode == "baseline" else "bypassed_safety")
        )

        error_msg = None
        if llm_result and llm_result.error_message_sanitized:
            error_msg = sanitize_secret_text(
                llm_result.error_message_sanitized, self._secrets
            )
        elif retrieval and retrieval.error_message:
            error_msg = sanitize_secret_text(retrieval.error_message, self._secrets)

        return {
            "request_id": request.request_id,
            "timestamp_utc": ts,
            "run_context": request.run_context,
            "test_id": request.test_id,
            "mode": request.mode,
            "prompt_version": response.prompt_version,
            "provider_requested": llm_result.provider_requested if llm_result else None,
            "provider_actual": response.provider_actual,
            "model_requested": llm_result.model_requested if llm_result else None,
            "model_actual": response.model_actual,
            "parameters": llm_result.parameters if llm_result else None,
            "allow_fallback": request.allow_fallback,
            "fallback_used": response.fallback_used,
            "fallback_reason": llm_result.fallback_reason if llm_result else None,
            "corpus_version": response.corpus_version,
            "retrieval_status": retrieval_status,
            "retrieved_sources": response.retrieved_sources,
            "citations_returned": response.citations,
            "citation_anomalies": response.citation_anomalies,
            "safety_category": response.safety_category,
            "outcome_type": response.outcome_type,
            "api_status": response.api_status,
            "error_type": response.error_type,
            "error_message_sanitized": error_msg,
            "latency_sec": round(float(response.latency_sec), 4),
            "query_text": query_logged,
            "response_text": response_logged,
        }

    def log(
        self,
        request: ChatRequest,
        response: ChatResponse,
        retrieval: RetrievalResult | None = None,
        llm_result: LLMCallResult | None = None,
    ) -> dict[str, Any]:
        """Menulis 1 baris JSONL ke disk dan mengembalikan record yang ditulis."""
        record = self.build_record(
            request=request,
            response=response,
            retrieval=retrieval,
            llm_result=llm_result,
        )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s:
            rows.append(json.loads(s))
    return rows


def validate_experiment_logs(
    baseline_log_path: str | Path,
    rag_log_path: str | Path,
    expected_count: int = 30,
) -> list[str]:
    """Memverifikasi paritas Kondisi A (Baseline) vs Kondisi B (RAG) pra-WF-032.

    Mengembalikan daftar pelanggaran (kosong berarti log sah dan siap dinilai).
    """
    issues: list[str] = []
    b_path = Path(baseline_log_path)
    r_path = Path(rag_log_path)
    if not b_path.is_file():
        return [f"File log Baseline tidak ditemukan: {b_path}"]
    if not r_path.is_file():
        return [f"File log RAG tidak ditemukan: {r_path}"]

    b_rows = _load_jsonl(b_path)
    r_rows = _load_jsonl(r_path)

    if len(b_rows) != expected_count:
        issues.append(
            f"Jumlah baris Baseline ({len(b_rows)}) != target ({expected_count})."
        )
    if len(r_rows) != expected_count:
        issues.append(f"Jumlah baris RAG ({len(r_rows)}) != target ({expected_count}).")

    b_ids = [row.get("test_id") for row in b_rows]
    r_ids = [row.get("test_id") for row in r_rows]
    if b_ids != r_ids:
        issues.append("Urutan/daftar test_id antara Baseline dan RAG tidak identik.")

    for label, rows, expected_mode in (
        ("Baseline", b_rows, "baseline"),
        ("RAG", r_rows, "rag"),
    ):
        for row in rows:
            tid = row.get("test_id")
            if row.get("mode") != expected_mode:
                issues.append(f"{label} {tid}: mode={row.get('mode')!r} != {expected_mode!r}.")
            if row.get("run_context") != "experiment":
                issues.append(f"{label} {tid}: run_context bukan 'experiment'.")
            if row.get("allow_fallback") is not False:
                issues.append(f"{label} {tid}: allow_fallback harus False.")
            if row.get("fallback_used") is True:
                issues.append(f"{label} {tid}: terdeteksi fallback_used=True saat eksperimen.")
            if expected_mode == "baseline" and row.get("retrieval_status") != "not_applicable":
                issues.append(f"Baseline {tid}: retrieval_status harus 'not_applicable'.")
            if expected_mode == "rag" and row.get("outcome_type") == "answered_grounded":
                if not row.get("corpus_version"):
                    issues.append(f"RAG {tid}: corpus_version kosong pada jawaban grounded.")

    # Verifikasi paritas model, provider, prompt_version, dan parameters lintas kondisi
    b_llm_rows = [r for r in b_rows if r.get("api_status") == "success"]
    r_llm_rows = [r for r in r_rows if r.get("api_status") == "success"]
    if b_llm_rows and r_llm_rows:
        b_sigs = {
            (
                r.get("provider_actual"),
                r.get("model_actual"),
                r.get("prompt_version"),
                json.dumps(r.get("parameters"), sort_keys=True),
            )
            for r in b_llm_rows
        }
        r_sigs = {
            (
                r.get("provider_actual"),
                r.get("model_actual"),
                r.get("prompt_version"),
                json.dumps(r.get("parameters"), sort_keys=True),
            )
            for r in r_llm_rows
        }
        if len(b_sigs) > 1 or len(r_sigs) > 1 or b_sigs != r_sigs:
            issues.append(
                f"Ketidakcocokan variabel kontrol model/prompt/parameter: "
                f"Baseline={b_sigs} vs RAG={r_sigs}."
            )

    return issues
