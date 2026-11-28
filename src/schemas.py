"""Kontrak struktur data (I/O) antar komponen SiagaBanjir.

Mengacu pada docs/ARCHITECTURE.md (Bagian 8 & 12) dan rancangan awal
kontrak metadata WF-005 di docs/DATA_DICTIONARY.md (menunggu persetujuan
final Member B / Ramadan).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ModeType = Literal["rag", "baseline"]
RunContextType = Literal["demo", "experiment"]
SafetyCategoryType = Literal[
    "normal",
    "empty_input",
    "acute_emergency",
    "prediction_request",
    "ambiguous",
    "out_of_domain",
]
RetrievalStatusType = Literal[
    "ok",
    "empty",
    "error",
    "bypassed_safety",
    "not_applicable",
]
OutcomeType = Literal[
    "answered_grounded",
    "answered_baseline",
    "emergency_override",
    "prediction_refused",
    "clarification_requested",
    "abstention_insufficient_evidence",
    "out_of_domain_refused",
    "api_error",
    "retrieval_error",
]
ApiStatusType = Literal["success", "error", "bypassed"]
ErrorType = Literal[
    "config_error",
    "timeout",
    "rate_limit",
    "auth_error",
    "network_error",
    "provider_error",
    "index_error",
]


@dataclass(frozen=True)
class ChatRequest:
    """Permintaan masuk seragam dari Streamlit UI atau Evaluation Runner."""

    request_id: str
    user_query: str
    mode: ModeType = "rag"
    run_context: RunContextType = "demo"
    allow_fallback: bool = True
    test_id: str | None = None

    def __post_init__(self) -> None:
        if self.mode not in ("rag", "baseline"):
            raise ValueError(f"Mode tidak valid: {self.mode!r}")
        if self.run_context not in ("demo", "experiment"):
            raise ValueError(f"run_context tidak valid: {self.run_context!r}")
        # Aturan keras eksperimen (ARCHITECTURE.md Bag. 5.2 & 12.3):
        # Dilarang silent fallback pada mode eksperimen.
        if self.run_context == "experiment" and self.allow_fallback:
            raise ValueError(
                "allow_fallback wajib False ketika run_context='experiment'."
            )


@dataclass(frozen=True)
class RetrievedChunk:
    """Satu potongan teks korpus beserta metadata sitasi (rancangan awal WF-005)."""

    chunk_id: str
    corpus_version: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_log_dict(self) -> dict[str, Any]:
        """Ringkasan metadata chunk untuk log evaluasi (FR-11)."""
        md = self.metadata
        return {
            "chunk_id": self.chunk_id,
            "source_id": md.get("source_id"),
            "title": md.get("title"),
            "source_date": md.get("source_date"),
            "retrieved_date": md.get("retrieved_date"),
            "region_scope": md.get("region_scope"),
            "page_pdf": md.get("page_pdf"),
            "page_label": md.get("page_label"),
            "score": round(float(self.score), 4),
        }

    def format_citation(self) -> str:
        """Menghasilkan teks sitasi deterministik dari metadata asli chunk."""
        md = self.metadata
        if md.get("citation_text"):
            return str(md["citation_text"]).strip()
        parts: list[str] = []
        publisher = md.get("publisher")
        source_date = md.get("source_date")
        if publisher and source_date:
            parts.append(f"{publisher} ({source_date})")
        elif publisher:
            parts.append(str(publisher))
        if md.get("title"):
            parts.append(str(md["title"]))
        if md.get("section_title"):
            parts.append(str(md["section_title"]))
        page_label = md.get("page_label")
        page_pdf = md.get("page_pdf")
        if page_label and page_pdf is not None:
            parts.append(f"hal. cetak {page_label} (hal. PDF {page_pdf})")
        elif page_label:
            parts.append(f"bagian {page_label}")
        elif page_pdf is not None:
            parts.append(f"hal. PDF {page_pdf}")
        return ", ".join(parts) if parts else f"Sumber korpus ({self.chunk_id})"


@dataclass(frozen=True)
class RetrievalResult:
    """Hasil operasi retrieval & Evidence Gate."""

    status: RetrievalStatusType
    corpus_version: str | None = None
    chunks: list[RetrievedChunk] = field(default_factory=list)
    error_message: str | None = None


@dataclass(frozen=True)
class SafetyCheckResult:
    """Hasil evaluasi gerbang keselamatan pra-retrieval (WF-006 / WF-023)."""

    category: SafetyCategoryType
    bypass_llm: bool
    override_message: str | None = None
    matched_rule: str | None = None


@dataclass(frozen=True)
class LLMCallResult:
    """Hasil pemanggilan adapter LLM provider (Gemini / Groq)."""

    provider_requested: str
    provider_actual: str | None
    model_requested: str
    model_actual: str | None
    parameters: dict[str, Any]
    raw_text: str | None
    api_status: ApiStatusType
    fallback_used: bool = False
    fallback_reason: str | None = None
    error_type: ErrorType | None = None
    error_message_sanitized: str | None = None
    latency_sec: float = 0.0


@dataclass(frozen=True)
class ChatResponse:
    """Respons akhir seragam untuk UI Streamlit dan Evaluation Runner."""

    request_id: str
    mode: ModeType
    outcome_type: OutcomeType
    answer_text: str
    citations: list[str] = field(default_factory=list)
    retrieved_sources: list[dict[str, Any]] = field(default_factory=list)
    citation_anomalies: list[str] = field(default_factory=list)
    safety_category: SafetyCategoryType = "normal"
    corpus_version: str | None = None
    prompt_version: str | None = None
    provider_actual: str | None = None
    model_actual: str | None = None
    fallback_used: bool = False
    api_status: ApiStatusType = "bypassed"
    error_type: ErrorType | None = None
    latency_sec: float = 0.0
    user_notice: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
