"""Runner eksperimen pembanding Baseline vs RAG SiagaBanjir (WF-030 & WF-031).

Aturan eksperimen (PRD v0.3 Bag. 12 & ARCHITECTURE.md v0.2 Bag. 12.3):
- Kondisi A (`baseline`) dan Kondisi B (`rag`) memakai provider, model,
  `prompt_version`, parameter, dan 30 pertanyaan uji yang 100% identik.
- `run_context="experiment"` dan `allow_fallback=False` dikunci keras (melarang
  *silent fallback* ke Groq).
- Kasus uji keselamatan darurat (FR-07) dijalankan terpisah pada mode RAG.
- Menjalankan verifikasi integritas log otomatis pra-penilaian (WF-032).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import AppConfig, load_config
from src.llm.client import LLMProviderAdapter
from src.logging.eval_logger import StructuredJsonlLogger, validate_experiment_logs
from src.pipeline.chat_service import ChatService
from src.retrieval.retriever import BM25CorpusRetriever
from src.safety.guard import SafetyGuard
from src.schemas import ChatRequest, ModeType


def load_questions_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Memuat berkas pertanyaan uji berformat JSONL (`test_id`, `query`)."""
    items: list[dict[str, Any]] = []
    for line_no, raw in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(), start=1
    ):
        s = raw.strip()
        if not s:
            continue
        obj = json.loads(s)
        if "test_id" not in obj or "query" not in obj:
            raise ValueError(
                f"Baris {line_no} pada {path} wajib memuat 'test_id' dan 'query'."
            )
        items.append(obj)
    return items


def run_batch(
    config: AppConfig,
    llm_adapter: LLMProviderAdapter,
    questions: list[dict[str, Any]],
    mode: ModeType,
    output_log_path: str | Path,
    retriever: BM25CorpusRetriever | None = None,
) -> list[dict[str, Any]]:
    """Menjalankan batch pertanyaan untuk satu mode eksperimen dengan fallback mati."""
    out_path = Path(output_log_path)
    if out_path.exists():
        out_path.unlink()

    logger = StructuredJsonlLogger(
        log_path=out_path,
        known_secrets=config.known_secrets(),
    )
    service = ChatService(
        config=config,
        llm_adapter=llm_adapter,
        retriever=retriever if mode == "rag" else None,
        safety_guard=SafetyGuard(),
        logger=logger,
    )

    summaries: list[dict[str, Any]] = []
    for idx, item in enumerate(questions, start=1):
        tid = str(item["test_id"])
        req = ChatRequest(
            request_id=f"exp_{mode}_{idx:03d}_{tid}",
            user_query=str(item["query"]),
            mode=mode,
            run_context="experiment",
            allow_fallback=False,
            test_id=tid,
        )
        resp = service.handle_request(req)
        summaries.append(
            {
                "test_id": tid,
                "mode": mode,
                "outcome_type": resp.outcome_type,
                "api_status": resp.api_status,
                "latency_sec": resp.latency_sec,
            }
        )
    return summaries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Runner eksperimen Baseline vs RAG SiagaBanjir (WF-030..WF-031)."
    )
    parser.add_argument("--env-file", default=".env", help="Path file .env lokal.")
    parser.add_argument(
        "--questions",
        required=True,
        help="Path dataset 30 pertanyaan uji (JSONL dengan field test_id & query).",
    )
    parser.add_argument(
        "--emergency-questions",
        default=None,
        help="Opsional: path dataset kasus uji darurat FR-07 terpisah (JSONL).",
    )
    parser.add_argument(
        "--mode",
        choices=("both", "baseline", "rag"),
        default="both",
        help=(
            "Mode eksperimen: 'both' (Baseline + RAG), 'baseline' (dapat diuji "
            "tanpa korpus), atau 'rag' (membutuhkan korpus frozen)."
        ),
    )
    parser.add_argument(
        "--out-dir",
        default="logs/experiment",
        help="Direktori output log JSONL Kondisi A, Kondisi B, dan uji darurat.",
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=30,
        help="Jumlah pertanyaan inti yang diharapkan untuk validasi log (default: 30).",
    )
    args = parser.parse_args(argv)

    cfg = load_config(env_file=args.env_file)
    need_corpus = args.mode in ("both", "rag")
    issues = cfg.validate_for_runtime(require_corpus=need_corpus)
    if issues:
        print("Prasyarat eksperimen belum terpenuhi:")
        for issue in issues:
            print(f"- {issue}")
        return 2

    questions = load_questions_jsonl(args.questions)
    out_dir = Path(args.out_dir)
    baseline_log = out_dir / "condition_a_baseline.jsonl"
    rag_log = out_dir / "condition_b_rag.jsonl"

    adapter = LLMProviderAdapter(config=cfg)
    retriever = (
        BM25CorpusRetriever(
            manifest_path=cfg.corpus_manifest_path,
            chunks_path=cfg.corpus_chunks_path,
            top_k=cfg.retrieval_top_k,
            min_score=cfg.evidence_min_score,
        )
        if need_corpus
        else None
    )

    if args.mode in ("both", "baseline"):
        run_batch(cfg, adapter, questions, mode="baseline", output_log_path=baseline_log)
    if args.mode in ("both", "rag"):
        run_batch(
            cfg,
            adapter,
            questions,
            mode="rag",
            output_log_path=rag_log,
            retriever=retriever,
        )

    if args.emergency_questions and need_corpus:
        em_questions = load_questions_jsonl(args.emergency_questions)
        em_log = out_dir / "safety_emergency_verification.jsonl"
        run_batch(
            cfg,
            adapter,
            em_questions,
            mode="rag",
            output_log_path=em_log,
            retriever=retriever,
        )

    if args.mode == "both":
        validation_issues = validate_experiment_logs(
            baseline_log_path=baseline_log,
            rag_log_path=rag_log,
            expected_count=args.expected_count,
        )
        if validation_issues:
            print("PERINGATAN — Validasi log pra-penilaian menemukan masalah:")
            for v in validation_issues:
                print(f"- {v}")
            return 1

    print(
        f"Eksperimen mode='{args.mode}' selesai "
        f"({len(questions)} pertanyaan diproses, allow_fallback=False)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
