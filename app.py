"""Antarmuka chat Streamlit lokal SiagaBanjir — diadaptasi dari starter Multazam.

Menjalankan:
    streamlit run app.py

Basis adaptasi:
- Mempertahankan pola starter dosen (`multazam_chatbot.py`): `st.title`,
  `st.markdown`, `st.session_state["chat_history"]` berbasis `SystemMessage` /
  `HumanMessage` / `AIMessage`, loop `st.chat_message()`, dan `st.chat_input()`.
- Mendelegasikan pemrosesan inti ke `ChatService` (`SafetyGuard`, `Retriever` +
  `Evidence Gate`, `Prompt Builder` berversi `prompt_version`, `LLMProviderAdapter`
  Gemini utama / Groq fallback demo via LangChain `invoke()` selektif, verifikasi
  sitasi deterministik, dan `StructuredJsonlLogger`).
- Mendukung dua mode terpisah: `rag` (korpus resmi) dan `baseline` (tanpa
  retrieval; tetap dapat diuji meskipun korpus Ramadan belum tersedia).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.config import AppConfig, get_file_mtime, load_config, resolve_env_path
from src.llm.client import LLMProviderAdapter
from src.llm.prompts import BASE_SYSTEM_INSTRUCTION
from src.logging.eval_logger import StructuredJsonlLogger
from src.pipeline.chat_service import ChatService
from src.retrieval.retriever import BM25CorpusRetriever
from src.safety.guard import SafetyGuard
from src.schemas import ChatRequest, ChatResponse, ModeType

try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    USING_LANGCHAIN_MESSAGES = True
except ImportError:  # Fallback ringan bila langchain-core belum terpasang di venv

    @dataclass
    class _BaseMessage:
        content: str

        @property
        def text(self) -> str:
            return self.content

    class SystemMessage(_BaseMessage):
        pass

    class HumanMessage(_BaseMessage):
        pass

    class AIMessage(_BaseMessage):
        pass

    USING_LANGCHAIN_MESSAGES = False


CORPUS_UNAVAILABLE_LABEL = "Belum tersedia (menunggu korpus frozen dari Ramadan)"

PERMANENT_SAFETY_DISCLAIMER = (
    "**SiagaBanjir** adalah prototipe akademik untuk **edukasi kesiapsiagaan "
    "banjir di Indonesia** (sebelum, saat, dan setelah banjir). Chatbot ini "
    "**bukan layanan darurat, bukan sistem peringatan dini resmi, dan bukan "
    "pengganti petugas atau otoritas berwenang**. Dalam kondisi darurat nyata, "
    "segera ikuti arahan petugas setempat dan hubungi **BPBD**, **BNPB**, "
    "**Basarnas (115)**, atau **112** *(jika layanan tersedia di wilayah Anda)*."
)


def extract_message_text(message: Any) -> str:
    """Membaca teks pesan secara aman lintas versi LangChain (`.text` / `.content`)."""
    text = getattr(message, "text", None)
    if isinstance(text, str) and text:
        return text
    content = getattr(message, "content", "")
    return str(content)


def init_chat_history() -> list[Any]:
    """Inisialisasi riwayat chat mengikuti pola starter Multazam (`SystemMessage` awal)."""
    return [SystemMessage(content=BASE_SYSTEM_INSTRUCTION)]


def corpus_status_label(config: AppConfig, retriever: BM25CorpusRetriever | None) -> str:
    """Menampilkan versi korpus aktif atau status jujur jika korpus belum tersedia."""
    if not config.corpus_manifest_path.is_file() or not config.corpus_chunks_path.is_file():
        return CORPUS_UNAVAILABLE_LABEL
    version = retriever.corpus_version if retriever is not None else None
    return version or CORPUS_UNAVAILABLE_LABEL


def format_assistant_markdown(response: ChatResponse) -> str:
    """Memformat respons akhir beserta badge mode, sitasi deterministik & notice."""
    mode_badge = (
        "**[Mode Baseline — Tanpa Retrieval]**"
        if response.mode == "baseline"
        else "**[Mode RAG — Korpus Resmi]**"
    )
    sections = [f"{mode_badge}\n\n{response.answer_text.strip()}"]
    if response.citations:
        cite_lines = "\n".join(f"- {c}" for c in response.citations)
        sections.append(f"**Rujukan Sumber Resmi:**\n{cite_lines}")
    if response.user_notice:
        sections.append(f"*{response.user_notice}*")
    return "\n\n".join(part for part in sections if part)


def build_runtime_service(config: AppConfig) -> ChatService:
    """Merakit ChatService lokal dengan logger demo terisolasi."""
    date_tag = datetime.now(timezone.utc).strftime("%Y%m%d")
    logger = StructuredJsonlLogger(
        log_path=config.log_dir / f"demo_{date_tag}.jsonl",
        known_secrets=config.known_secrets(),
    )
    retriever = BM25CorpusRetriever(
        manifest_path=config.corpus_manifest_path,
        chunks_path=config.corpus_chunks_path,
        top_k=config.retrieval_top_k,
        min_score=config.evidence_min_score,
    )
    adapter = LLMProviderAdapter(config=config)
    return ChatService(
        config=config,
        llm_adapter=adapter,
        retriever=retriever,
        safety_guard=SafetyGuard(),
        logger=logger,
    )


def run_app(
    st_module: Any | None = None,
    config_override: AppConfig | None = None,
    service_override: ChatService | None = None,
) -> None:
    """Entry point UI Streamlit berbasis pola starter Multazam (dapat diuji via mock)."""
    if st_module is None:
        try:
            import streamlit as st_module  # type: ignore[no-redef]
        except ImportError as exc:
            raise SystemExit(
                "Streamlit belum terpasang pada lingkungan Python ini. "
                "Jalankan `pip install -r requirements.txt` lalu `streamlit run app.py`."
            ) from exc
    st = st_module

    if hasattr(st, "set_page_config"):
        st.set_page_config(
            page_title="SiagaBanjir — Edukasi Kesiapsiagaan Banjir",
            page_icon="🌊",
            layout="centered",
        )

    if config_override is not None and service_override is not None:
        config, service = config_override, service_override
    else:
        env_mtime = get_file_mtime(resolve_env_path(".env"))
        cfg_preview = load_config()
        manifest_mtime = get_file_mtime(cfg_preview.corpus_manifest_path)

        @st.cache_resource
        def _get_service(_env_mtime: float, _manifest_mtime: float) -> tuple[AppConfig, ChatService]:
            cfg = load_config()
            return cfg, build_runtime_service(cfg)

        config, service = _get_service(env_mtime, manifest_mtime)

    corpus_available = (
        config.corpus_manifest_path.is_file() and config.corpus_chunks_path.is_file()
    )
    corpus_label = corpus_status_label(config, service.retriever)

    # Header & disclaimer (adaptasi langsung dari pola st.title + st.markdown Multazam)
    st.title("SiagaBanjir")
    st.markdown(
        "Prototipe Chatbot Edukasi Kesiapsiagaan Banjir Berbasis LLM & RAG — "
        "Cakupan Umum Indonesia"
    )
    st.warning(PERMANENT_SAFETY_DISCLAIMER)

    # Pola st.session_state["chat_history"] dari starter Multazam
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = init_chat_history()

    with st.sidebar:
        st.subheader("Pengaturan & Status Sistem")
        selected_mode: ModeType = st.radio(
            "Mode Eksekusi",
            options=["rag", "baseline"],
            index=0 if corpus_available else 1,
            format_func=lambda m: (
                "RAG (Korpus Resmi)" if m == "rag" else "Baseline (Tanpa Retrieval)"
            ),
        )
        st.markdown(f"- **Status Korpus:** `{corpus_label}`")
        st.markdown(f"- **Provider Utama:** `{config.primary_provider}`")
        st.markdown(f"- **Model Utama (Lokal):** `{config.primary_model}`")
        st.markdown(f"- **Provider Cadangan (Demo):** `{config.fallback_provider}`")
        st.markdown(f"- **Model Cadangan (Demo):** `{config.fallback_model}`")
        st.markdown(f"- **Versi Prompt:** `{config.prompt_version}`")
        st.caption(
            "Catatan: Penetapan model final (OD-02) menunggu persetujuan tim; "
            "eksperimen Baseline vs RAG tetap menonaktifkan fallback diam-diam."
        )

        issues = config.validate_for_runtime(require_corpus=(selected_mode == "rag"))
        if issues:
            st.info(
                "Catatan kesiapan:\n" + "\n".join(f"- {item}" for item in issues)
            )
        if st.button("Bersihkan Riwayat Chat"):
            st.session_state["chat_history"] = init_chat_history()
            st.session_state["last_selected_mode"] = selected_mode
            st.rerun()

    # Beri tahu pengguna jika berpindah mode sementara riwayat lama masih tampil
    prev_mode = st.session_state.get("last_selected_mode")
    has_prior_turns = len(st.session_state["chat_history"]) > 1
    if prev_mode is not None and prev_mode != selected_mode and has_prior_turns:
        st.info(
            f"Mode berubah dari **{prev_mode.upper()}** ke **{selected_mode.upper()}**. "
            "Pesan lama di bawah tetap menampilkan label modenya masing-masing; "
            "klik **Bersihkan Riwayat Chat** di sidebar bila ingin memulai sesi bersih."
        )
    st.session_state["last_selected_mode"] = selected_mode

    # Render histori percakapan (lewati SystemMessage seperti di Multazam)
    for chat in st.session_state["chat_history"]:
        if isinstance(chat, SystemMessage):
            continue
        elif isinstance(chat, HumanMessage):
            role = "user"
        elif isinstance(chat, AIMessage):
            role = "assistant"
        else:
            continue
        with st.chat_message(name=role):
            st.markdown(body=extract_message_text(chat))

    # Terima input pengguna (pola st.chat_input + st.stop Multazam)
    user_prompt = st.chat_input(
        placeholder="Tanyakan persiapan sebelum, saat, atau setelah banjir di Indonesia..."
    )
    if user_prompt is None:
        st.stop()
        return

    with st.chat_message(name="user"):
        st.markdown(body=user_prompt if user_prompt.strip() else "*(input kosong)*")

    st.session_state["chat_history"].append(HumanMessage(content=user_prompt))

    # Delegasi ke ChatService (single-turn terkontrol: SafetyGuard -> RAG/Baseline -> Logger)
    req = ChatRequest(
        request_id=f"demo_{uuid.uuid4().hex[:10]}",
        user_query=user_prompt,
        mode=selected_mode,
        run_context="demo",
        allow_fallback=True,
    )
    with st.spinner("Memproses pertanyaan..."):
        response = service.handle_request(req)

    formatted_reply = format_assistant_markdown(response)
    st.session_state["chat_history"].append(AIMessage(content=formatted_reply))

    with st.chat_message(name="assistant"):
        st.markdown(body=formatted_reply)


def main() -> None:
    run_app()


if __name__ == "__main__":
    main()
