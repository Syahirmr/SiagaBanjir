"""Pemuat konfigurasi lingkungan (.env) dan utilitas sanitasi kredensial (WF-015).

Aturan keamanan (PRD NFR & ARCHITECTURE.md Bag. 5.2, 12.2):
- API key hanya dibaca dari environment / `.env` lokal.
- Kredensial tidak pernah dicetak di __repr__, log, atau pesan error UI.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

PLACEHOLDER_MODEL_PREFIX = "TBD_"
PLACEHOLDER_KEY_MARKERS = ("your_", "replace_me", "changeme", "example")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_env_path(env_file: str | Path | None = ".env") -> Path | None:
    """Menyelesaikan path `.env` secara konsisten terhadap root proyek."""
    if env_file is None:
        return None
    p = Path(env_file)
    if p.is_absolute():
        return p
    if p.is_file():
        return p.resolve()
    return (PROJECT_ROOT / p).resolve()


def get_file_mtime(path: Path | None) -> float:
    """Mengembalikan mtime berkas untuk invalidasi cache Streamlit (0.0 jika tidak ada)."""
    if path is None or not path.is_file():
        return 0.0
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0

_SECRET_PATTERNS = (
    re.compile(r"AIza[0-9A-Za-z_\-]{10,}"),
    re.compile(r"gsk_[0-9A-Za-z_\-]{10,}"),
    re.compile(r"(?i)(api[_-]?key|authorization|bearer)\s*[:=]\s*['\"]?[^\s'\",;]+"),
)


def parse_env_file(env_path: Path) -> dict[str, str]:
    """Mem-parsing file `.env` sederhana secara aman tanpa dependency tambahan."""
    values: dict[str, str] = {}
    if not env_path.is_file():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        if key:
            values[key] = val
    return values


def _is_usable_secret(value: str | None) -> bool:
    if not value:
        return False
    low = value.strip().lower()
    if not low:
        return False
    return not any(low.startswith(marker) for marker in PLACEHOLDER_KEY_MARKERS)


def sanitize_secret_text(
    text: str | None,
    secrets: tuple[str | None, ...] = (),
) -> str | None:
    """Menyaring pola API key / header auth serta nilai kredensial eksplisit."""
    if text is None:
        return None
    sanitized = str(text)
    for secret in secrets:
        if secret and len(secret.strip()) >= 6:
            sanitized = sanitized.replace(secret.strip(), "[REDACTED]")
    for pattern in _SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


@dataclass(frozen=True)
class AppConfig:
    """Konfigurasi terpusat aplikasi SiagaBanjir tanpa membocorkan kredensial."""

    primary_provider: str = "gemini"
    fallback_provider: str = "groq"
    primary_model: str = "TBD_AFTER_WF016"
    fallback_model: str = "TBD_AFTER_WF016"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1400
    llm_timeout_sec: int = 30
    prompt_version: str = "prompt_v1.3"
    corpus_manifest_path: Path = Path("data/processed/corpus_manifest.json")
    corpus_chunks_path: Path = Path("data/processed/chunks.jsonl")
    retrieval_top_k: int = 4
    evidence_min_score: float = 0.15
    log_dir: Path = Path("logs")
    gemini_api_key: str | None = field(default=None, repr=False)
    groq_api_key: str | None = field(default=None, repr=False)

    @property
    def has_gemini_key(self) -> bool:
        return _is_usable_secret(self.gemini_api_key)

    @property
    def has_groq_key(self) -> bool:
        return _is_usable_secret(self.groq_api_key)

    @property
    def is_primary_model_configured(self) -> bool:
        return bool(self.primary_model) and not self.primary_model.startswith(
            PLACEHOLDER_MODEL_PREFIX
        )

    @property
    def is_fallback_model_configured(self) -> bool:
        return bool(self.fallback_model) and not self.fallback_model.startswith(
            PLACEHOLDER_MODEL_PREFIX
        )

    def llm_parameters(self) -> dict[str, float | int]:
        return {
            "temperature": self.llm_temperature,
            "max_tokens": self.llm_max_tokens,
            "timeout_sec": self.llm_timeout_sec,
        }

    def known_secrets(self) -> tuple[str | None, ...]:
        return (self.gemini_api_key, self.groq_api_key)

    def validate_for_runtime(self, require_corpus: bool = True) -> list[str]:
        """Mengembalikan daftar masalah konfigurasi tanpa membocorkan nilai key."""
        issues: list[str] = []
        if self.primary_provider == "gemini" and not self.has_gemini_key:
            issues.append("GEMINI_API_KEY belum terisi pada environment/.env lokal.")
        if self.primary_provider == "groq" and not self.has_groq_key:
            issues.append("GROQ_API_KEY belum terisi pada environment/.env lokal.")
        if not self.is_primary_model_configured:
            issues.append(
                f"PRIMARY_MODEL masih placeholder ({self.primary_model}); "
                "lakukan pengujian API (WF-016) sebelum mengunci model."
            )
        if require_corpus:
            if not self.corpus_manifest_path.is_file():
                issues.append(
                    f"Manifest korpus belum ditemukan di {self.corpus_manifest_path}."
                )
            if not self.corpus_chunks_path.is_file():
                issues.append(
                    f"Dataset chunk korpus belum ditemukan di {self.corpus_chunks_path}."
                )
        return issues

    def safe_summary(self) -> dict[str, object]:
        """Ringkasan konfigurasi yang aman ditampilkan di UI atau log diagnostik."""
        return {
            "primary_provider": self.primary_provider,
            "fallback_provider": self.fallback_provider,
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "parameters": self.llm_parameters(),
            "prompt_version": self.prompt_version,
            "has_gemini_key": self.has_gemini_key,
            "has_groq_key": self.has_groq_key,
            "corpus_manifest_path": str(self.corpus_manifest_path),
            "corpus_chunks_path": str(self.corpus_chunks_path),
            "retrieval_top_k": self.retrieval_top_k,
            "evidence_min_score": self.evidence_min_score,
        }


def _parse_float(raw: str | None, default: float) -> float:
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw.strip())
    except ValueError:
        return default


def _parse_int(raw: str | None, default: int) -> int:
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def load_config(
    env_file: str | Path | None = ".env",
    environ: Mapping[str, str] | None = None,
) -> AppConfig:
    """Memuat AppConfig dari environment dengan fallback file `.env` lokal.

    Prioritas: variabel lingkungan proses > file `.env` > default aman.
    """
    file_vals: dict[str, str] = {}
    resolved_env = resolve_env_path(env_file)
    if resolved_env is not None:
        file_vals = parse_env_file(resolved_env)

    env_source = os.environ if environ is None else environ

    def get(key: str, default: str | None = None) -> str | None:
        if key in env_source and env_source[key].strip() != "":
            return env_source[key].strip()
        if key in file_vals and file_vals[key].strip() != "":
            return file_vals[key].strip()
        return default

    return AppConfig(
        primary_provider=(get("PRIMARY_PROVIDER", "gemini") or "gemini").lower(),
        fallback_provider=(get("FALLBACK_PROVIDER", "groq") or "groq").lower(),
        primary_model=get("PRIMARY_MODEL", "TBD_AFTER_WF016") or "TBD_AFTER_WF016",
        fallback_model=get("FALLBACK_MODEL", "TBD_AFTER_WF016") or "TBD_AFTER_WF016",
        llm_temperature=_parse_float(get("LLM_TEMPERATURE"), 0.1),
        llm_max_tokens=_parse_int(get("LLM_MAX_TOKENS"), 1400),
        llm_timeout_sec=_parse_int(get("LLM_TIMEOUT_SEC"), 30),
        prompt_version=get("PROMPT_VERSION", "prompt_v1.3") or "prompt_v1.3",
        corpus_manifest_path=Path(
            get("CORPUS_MANIFEST_PATH", "data/processed/corpus_manifest.json")
            or "data/processed/corpus_manifest.json"
        ),
        corpus_chunks_path=Path(
            get("CORPUS_CHUNKS_PATH", "data/processed/chunks.jsonl")
            or "data/processed/chunks.jsonl"
        ),
        retrieval_top_k=_parse_int(get("RETRIEVAL_TOP_K"), 4),
        evidence_min_score=_parse_float(get("EVIDENCE_MIN_SCORE"), 0.15),
        log_dir=Path(get("LOG_DIR", "logs") or "logs"),
        gemini_api_key=get("GEMINI_API_KEY"),
        groq_api_key=get("GROQ_API_KEY"),
    )
