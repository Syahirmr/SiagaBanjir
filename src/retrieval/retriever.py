"""Retriever leksikal BM25 read-only & Evidence Gate untuk SiagaBanjir (FR-03, FR-05).

Batas integrasi dengan pekerjaan Member B / Ramadan (WF-005 & WF-018):
- Membaca `corpus_manifest.json` dan `chunks.jsonl` secara READ-ONLY.
- Tidak pernah mengubah `data/raw/` maupun `data/processed/`.
- Implementasi BM25 berbasis stdlib + math (zero dependency tambahan, cepat di
  laptop tanpa GPU — salah satu kandidat TD-02) yang dapat diswap atau diperluas
  ke dense/hybrid pada WF-021 tanpa mengubah kontrak ChatService.
- Memisahkan secara tegas `retrieval_status`:
  * "ok": ada >= 1 chunk melampaui ambang `min_score` (Evidence Gate lulus).
  * "empty": indeks sehat, tetapi tidak ada bukti cukup -> `abstention_insufficient_evidence`.
  * "error": kegagalan teknis memuat manifest/chunks -> `retrieval_error`.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.schemas import RetrievalResult, RetrievedChunk

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Stopwords ringkas Bahasa Indonesia agar skor BM25 fokus pada kata kunci bermakna
_ID_STOPWORDS: frozenset[str] = frozenset(
    {
        "yang",
        "dan",
        "di",
        "ke",
        "dari",
        "untuk",
        "pada",
        "dengan",
        "atau",
        "adalah",
        "itu",
        "ini",
        "apa",
        "bagaimana",
        "saja",
        "harus",
        "bisa",
        "dapat",
        "agar",
        "jika",
        "bila",
        "kalau",
        "saat",
        "ketika",
        "dalam",
        "oleh",
        "tidak",
        "akan",
        "sudah",
        "telah",
        "saya",
        "kami",
        "kita",
        "anda",
        "mereka",
        "juga",
        "lebih",
        "ada",
        "jadi",
        "sebagai",
        "tentang",
        "perlu",
    }
)


def tokenize_indonesian(text: str) -> list[str]:
    """Tokenisasi ringan huruf kecil + penghapusan stopwords umum Bahasa Indonesia."""
    tokens = _TOKEN_RE.findall(text.lower())
    filtered = [t for t in tokens if len(t) > 1 and t not in _ID_STOPWORDS]
    return filtered if filtered else [t for t in tokens if len(t) > 1]


class BM25CorpusRetriever:
    """Retriever BM25 read-only berbasis `corpus_manifest.json` & `chunks.jsonl`."""

    def __init__(
        self,
        manifest_path: str | Path,
        chunks_path: str | Path,
        top_k: int = 4,
        min_score: float = 0.15,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.chunks_path = Path(chunks_path)
        self.top_k = max(1, int(top_k))
        self.min_score = float(min_score)
        self.k1 = float(k1)
        self.b = float(b)

        self._loaded = False
        self._load_error: str | None = None
        self._corpus_version: str | None = None
        self._manifest_sources: dict[str, dict[str, Any]] = {}
        self._chunks: list[dict[str, Any]] = []
        self._doc_term_freqs: list[Counter[str]] = []
        self._doc_lengths: list[int] = []
        self._avgdl: float = 1.0
        self._idf: dict[str, float] = {}

    @property
    def corpus_version(self) -> str | None:
        if not self._loaded:
            self._ensure_loaded()
        return self._corpus_version

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            if not self.manifest_path.is_file():
                raise FileNotFoundError(
                    f"File manifest korpus tidak ditemukan: {self.manifest_path}"
                )
            if not self.chunks_path.is_file():
                raise FileNotFoundError(
                    f"File chunks korpus tidak ditemukan: {self.chunks_path}"
                )

            manifest_raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            self._parse_manifest(manifest_raw)

            loaded_chunks: list[dict[str, Any]] = []
            for line_no, raw_line in enumerate(
                self.chunks_path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                line = raw_line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if "chunk_id" not in obj or "text" not in obj:
                    raise ValueError(
                        f"Format chunk tidak valid pada baris {line_no}: "
                        "field 'chunk_id' dan 'text' wajib tersedia."
                    )
                if not self._corpus_version and obj.get("corpus_version"):
                    self._corpus_version = str(obj["corpus_version"])
                loaded_chunks.append(obj)

            if not loaded_chunks:
                raise ValueError("File chunks.jsonl kosong (0 chunk tersedia).")

            self._chunks = loaded_chunks
            self._build_bm25_index()
            self._load_error = None
        except Exception as exc:
            self._load_error = f"{type(exc).__name__}: {exc}"
            self._chunks = []

    def _parse_manifest(self, manifest_raw: Any) -> None:
        """Mendukung dua bentuk manifest WF-005 (dict dengan key `sources` atau list)."""
        if isinstance(manifest_raw, dict):
            if manifest_raw.get("corpus_version"):
                self._corpus_version = str(manifest_raw["corpus_version"])
            sources = manifest_raw.get("sources")
            if isinstance(sources, list):
                for item in sources:
                    if isinstance(item, dict) and item.get("source_id"):
                        self._manifest_sources[str(item["source_id"])] = item
                        if not self._corpus_version and item.get("corpus_version"):
                            self._corpus_version = str(item["corpus_version"])
            elif manifest_raw.get("source_id"):
                self._manifest_sources[str(manifest_raw["source_id"])] = manifest_raw
        elif isinstance(manifest_raw, list):
            for item in manifest_raw:
                if isinstance(item, dict) and item.get("source_id"):
                    self._manifest_sources[str(item["source_id"])] = item
                    if not self._corpus_version and item.get("corpus_version"):
                        self._corpus_version = str(item["corpus_version"])
        else:
            raise ValueError("Struktur corpus_manifest.json harus berupa object atau list.")

    def _build_bm25_index(self) -> None:
        doc_freqs: Counter[str] = Counter()
        self._doc_term_freqs = []
        self._doc_lengths = []

        for chunk in self._chunks:
            md = chunk.get("metadata") or {}
            searchable = " ".join(
                str(part)
                for part in (
                    chunk.get("text", ""),
                    md.get("section_title", ""),
                    md.get("title", ""),
                    md.get("flood_phase", ""),
                )
                if part
            )
            tokens = tokenize_indonesian(searchable)
            tf = Counter(tokens)
            self._doc_term_freqs.append(tf)
            self._doc_lengths.append(len(tokens))
            for term in tf:
                doc_freqs[term] += 1

        n_docs = len(self._chunks)
        total_len = sum(self._doc_lengths)
        self._avgdl = (total_len / n_docs) if n_docs > 0 and total_len > 0 else 1.0
        self._idf = {
            term: math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
            for term, df in doc_freqs.items()
        }

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> RetrievalResult:
        """Mengambil top-k chunk relevan dan menerapkan Evidence Gate."""
        self._ensure_loaded()
        if self._load_error is not None:
            return RetrievalResult(
                status="error",
                corpus_version=self._corpus_version,
                chunks=[],
                error_message=self._load_error,
            )

        q_tokens = tokenize_indonesian(query)
        if not q_tokens:
            return RetrievalResult(
                status="empty",
                corpus_version=self._corpus_version,
                chunks=[],
            )

        k_limit = self.top_k if top_k is None else max(1, int(top_k))
        threshold = self.min_score if min_score is None else float(min_score)

        scored: list[tuple[float, int]] = []
        unique_q = set(q_tokens)
        max_possible_idf = sum(self._idf.get(t, 0.0) for t in unique_q)

        for idx, tf in enumerate(self._doc_term_freqs):
            dl = self._doc_lengths[idx]
            if dl == 0:
                continue
            bm25_raw = 0.0
            matched_terms = 0
            for term in unique_q:
                freq = tf.get(term, 0)
                if freq <= 0:
                    continue
                matched_terms += 1
                idf = self._idf.get(term, 0.0)
                denom = freq + self.k1 * (1.0 - self.b + self.b * (dl / self._avgdl))
                bm25_raw += idf * ((freq * (self.k1 + 1.0)) / denom)

            if bm25_raw <= 0.0:
                continue
            # Normalisasi skor ke rentang [0, 1] berdasarkan rasio kecocokan kata kunci
            # dan kekuatan BM25 agar ambang Evidence Gate stabil lintas ukuran korpus.
            coverage = matched_terms / len(unique_q)
            bm25_norm = (
                bm25_raw / (max_possible_idf * (self.k1 + 1.0))
                if max_possible_idf > 0
                else 0.0
            )
            combined_score = min(1.0, 0.65 * coverage + 0.35 * bm25_norm)
            if combined_score >= threshold:
                scored.append((combined_score, idx))

        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        top_hits = scored[:k_limit]

        if not top_hits:
            return RetrievalResult(
                status="empty",
                corpus_version=self._corpus_version,
                chunks=[],
            )

        result_chunks: list[RetrievedChunk] = []
        for score, idx in top_hits:
            raw_chunk = self._chunks[idx]
            md = dict(raw_chunk.get("metadata") or {})
            src_id = md.get("source_id")
            if src_id and str(src_id) in self._manifest_sources:
                manifest_entry = self._manifest_sources[str(src_id)]
                for field_name in (
                    "title",
                    "publisher",
                    "source_date",
                    "retrieved_date",
                    "source_url",
                    "region_scope",
                ):
                    md.setdefault(field_name, manifest_entry.get(field_name))

            result_chunks.append(
                RetrievedChunk(
                    chunk_id=str(raw_chunk["chunk_id"]),
                    corpus_version=str(
                        raw_chunk.get("corpus_version")
                        or self._corpus_version
                        or "unknown"
                    ),
                    text=str(raw_chunk["text"]),
                    score=round(score, 4),
                    metadata=md,
                )
            )

        return RetrievalResult(
            status="ok",
            corpus_version=self._corpus_version,
            chunks=result_chunks,
        )
