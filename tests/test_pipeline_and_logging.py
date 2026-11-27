"""Integration tests untuk Retriever, Prompts, LLM Adapter, ChatService, Logger & Runner.

Seluruh pengujian menggunakan fixture korpus sintetis di direktori sementara
(`tempfile.TemporaryDirectory`) dan mock LLM transport — tidak menyentuh
`data/raw/`, `data/processed/`, maupun API eksternal.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import format_assistant_markdown
from scripts.run_eval import run_batch
from scripts.test_api import main as test_api_main
from src.config import AppConfig
from src.llm.client import LLMProviderAdapter, ProviderCallError
from src.llm.prompts import build_baseline_messages, build_rag_messages
from src.logging.eval_logger import (
    StructuredJsonlLogger,
    mask_pii_for_demo,
    validate_experiment_logs,
)
from src.pipeline.chat_service import ChatService, verify_and_extract_citations
from src.retrieval.retriever import BM25CorpusRetriever
from src.schemas import ChatRequest, RetrievedChunk


def _create_synthetic_corpus(tmp_dir: Path) -> tuple[Path, Path]:
    manifest_path = tmp_dir / "corpus_manifest.json"
    chunks_path = tmp_dir / "chunks.jsonl"
    manifest = {
        "corpus_version": "corpus_v0.0-test-fixture",
        "sources": [
            {
                "source_id": "SRC-TEST-001",
                "title": "Buku Saku Uji Kesiapsiagaan Banjir",
                "publisher": "BNPB",
                "source_date": "2018",
                "retrieved_date": "2026-11-20",
                "region_scope": "nasional_umum",
            }
        ],
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    chunks = [
        {
            "chunk_id": "SRC-TEST-001_p044_c01",
            "corpus_version": "corpus_v0.0-test-fixture",
            "text": (
                "Saat air banjir mulai masuk ke dalam rumah, segera matikan aliran "
                "listrik dari sakelar utama dan pindahkan barang penting ke tempat tinggi."
            ),
            "metadata": {
                "source_id": "SRC-TEST-001",
                "section_title": "Bab III.D Banjir — Saat Bencana",
                "flood_phase": "saat",
                "page_pdf": 44,
                "page_label": "42",
                "citation_text": (
                    "BNPB (2018), Buku Saku Uji Kesiapsiagaan Banjir, "
                    "Bab III.D Banjir — Saat Bencana, hal. cetak 42 (hal. PDF 44)."
                ),
            },
        },
        {
            "chunk_id": "SRC-TEST-001_p018_c01",
            "corpus_version": "corpus_v0.0-test-fixture",
            "text": (
                "Tas Siaga Bencana (TSB) berisi dokumen penting dalam plastik kedap air, "
                "obat-obatan P3K, air minum, makanan tahan lama, senter, dan peluit."
            ),
            "metadata": {
                "source_id": "SRC-TEST-001",
                "section_title": "Bab II — Tas Siaga Bencana",
                "flood_phase": "sebelum",
                "page_pdf": 18,
                "page_label": "16",
                "citation_text": (
                    "BNPB (2018), Buku Saku Uji Kesiapsiagaan Banjir, "
                    "Bab II — Tas Siaga Bencana, hal. cetak 16 (hal. PDF 18)."
                ),
            },
        },
    ]
    chunks_path.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
        encoding="utf-8",
    )
    return manifest_path, chunks_path


class TestPipelineAndLogging(unittest.TestCase):
    def test_retriever_ok_empty_and_error_separation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path, chunks_path = _create_synthetic_corpus(Path(tmp))
            ret = BM25CorpusRetriever(manifest_path, chunks_path, top_k=2, min_score=0.2)

            hit = ret.retrieve("Apa isi Tas Siaga Bencana untuk menghadapi banjir?")
            self.assertEqual(hit.status, "ok")
            self.assertEqual(hit.corpus_version, "corpus_v0.0-test-fixture")
            self.assertEqual(hit.chunks[0].chunk_id, "SRC-TEST-001_p018_c01")

            miss = ret.retrieve("Bagaimana prosedur sertifikasi kapal kargo internasional?")
            self.assertEqual(miss.status, "empty")
            self.assertEqual(miss.chunks, [])

            broken = BM25CorpusRetriever(Path(tmp) / "missing.json", chunks_path)
            err = broken.retrieve("Apa isi Tas Siaga Bencana?")
            self.assertEqual(err.status, "error")
            self.assertIsNotNone(err.error_message)

    def test_citation_verifier_separates_cited_vs_retrieved_and_catches_anomalies(self) -> None:
        chunks = [
            RetrievedChunk(
                chunk_id="c1",
                corpus_version="v1",
                text="Teks 1",
                score=0.9,
                metadata={"citation_text": "Sitasi Valid 1"},
            ),
            RetrievedChunk(
                chunk_id="c2",
                corpus_version="v1",
                text="Teks 2",
                score=0.5,
                metadata={"citation_text": "Sitasi Valid 2"},
            ),
        ]
        cites, anomalies = verify_and_extract_citations(
            "Matikan listrik segera [SUMBER 1]. Klaim aneh [SUMBER 9].", chunks
        )
        self.assertEqual(cites, ["Sitasi Valid 1"])
        self.assertEqual(anomalies, ["[SUMBER 9]"])

    def test_prompt_builder_parity_and_data_isolation(self) -> None:
        chunk = RetrievedChunk("c1", "v1", "Matikan listrik.", 0.8, {"source_id": "S1"})
        base_msgs = build_baseline_messages("Langkah saat banjir?", "prompt_v1.0")
        rag_msgs = build_rag_messages("Langkah saat banjir?", [chunk], "prompt_v1.0")
        self.assertNotIn("<retrieved_context>", base_msgs[1]["content"])
        self.assertIn("<retrieved_context>", rag_msgs[1]["content"])
        self.assertIn("DATA referensi semata", rag_msgs[0]["content"])
        self.assertTrue(rag_msgs[0]["content"].startswith(base_msgs[0]["content"]))

    def test_fallback_allowed_in_demo_but_blocked_in_experiment(self) -> None:
        cfg = AppConfig(
            primary_provider="gemini",
            fallback_provider="groq",
            primary_model="mock-primary",
            fallback_model="mock-fallback",
            gemini_api_key="AIzaSyFakeSecret123456",
            groq_api_key="gsk_FakeSecret123456",
        )

        def flaky_transport(provider, model, messages, params):
            if provider == "gemini":
                raise ProviderCallError("rate_limit", "429 key=AIzaSyFakeSecret123456")
            return "Jawaban dari Groq cadangan [SUMBER 1]."

        adapter = LLMProviderAdapter(cfg, transport=flaky_transport)
        msgs = build_baseline_messages("Apa isi tas siaga?")

        demo_res = adapter.generate(msgs, allow_fallback=True)
        self.assertEqual(demo_res.api_status, "success")
        self.assertTrue(demo_res.fallback_used)
        self.assertEqual(demo_res.provider_actual, "groq")

        exp_res = adapter.generate(msgs, allow_fallback=False)
        self.assertEqual(exp_res.api_status, "error")
        self.assertFalse(exp_res.fallback_used)
        self.assertEqual(exp_res.error_type, "rate_limit")
        assert exp_res.error_message_sanitized is not None
        self.assertNotIn("AIzaSyFakeSecret123456", exp_res.error_message_sanitized)

    def test_chat_service_end_to_end_and_demo_pii_masking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path, chunks_path = _create_synthetic_corpus(tmp_path)
            cfg = AppConfig(
                primary_model="mock-model",
                fallback_model="mock-fallback",
                corpus_manifest_path=manifest_path,
                corpus_chunks_path=chunks_path,
                gemini_api_key="AIzaSySecretKey999999",
            )
            log_path = tmp_path / "demo_test.jsonl"
            logger = StructuredJsonlLogger(log_path, known_secrets=cfg.known_secrets())
            retriever = BM25CorpusRetriever(manifest_path, chunks_path, min_score=0.2)
            adapter = LLMProviderAdapter(
                cfg,
                transport=lambda p, m, msgs, params: (
                    "Segera matikan aliran listrik dari sakelar utama [SUMBER 1]."
                ),
            )
            svc = ChatService(cfg, adapter, retriever=retriever, logger=logger)

            req = ChatRequest(
                request_id="demo_001",
                user_query=(
                    "Jika air banjir masuk rumah hubungi 081234567890 atau user@example.com, "
                    "apa langkah aman listriknya?"
                ),
                mode="rag",
                run_context="demo",
                allow_fallback=True,
            )
            resp = svc.handle_request(req)
            self.assertEqual(resp.outcome_type, "answered_grounded")
            self.assertEqual(len(resp.citations), 1)
            self.assertIn("hal. cetak 42 (hal. PDF 44)", resp.citations[0])
            md_out = format_assistant_markdown(resp)
            self.assertIn("Rujukan Sumber Resmi:", md_out)

            logged = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("[PHONE_MASKED]", logged["query_text"])
            self.assertIn("[EMAIL_MASKED]", logged["query_text"])
            self.assertNotIn("AIzaSySecretKey999999", json.dumps(logged))
            self.assertEqual(mask_pii_for_demo("Kontak +62812-3456-7890"), "Kontak [PHONE_MASKED]")

    def test_experiment_runner_and_log_parity_validator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path, chunks_path = _create_synthetic_corpus(tmp_path)
            cfg = AppConfig(
                primary_model="mock-experiment-model",
                fallback_model="mock-groq",
                corpus_manifest_path=manifest_path,
                corpus_chunks_path=chunks_path,
            )
            retriever = BM25CorpusRetriever(manifest_path, chunks_path, min_score=0.2)
            adapter = LLMProviderAdapter(
                cfg,
                transport=lambda p, m, msgs, params: "Jawaban uji [SUMBER 1].",
            )
            questions = [
                {"test_id": "Q-01", "query": "Apa isi Tas Siaga Bencana untuk banjir?"},
                {"test_id": "Q-02", "query": "Apa langkah aman mematikan listrik saat banjir masuk rumah?"},
                {"test_id": "Q-03", "query": "banjir"},
            ]
            b_log = tmp_path / "baseline.jsonl"
            r_log = tmp_path / "rag.jsonl"
            run_batch(cfg, adapter, questions, mode="baseline", output_log_path=b_log)
            run_batch(cfg, adapter, questions, mode="rag", output_log_path=r_log, retriever=retriever)

            issues = validate_experiment_logs(b_log, r_log, expected_count=3)
            self.assertEqual(issues, [])

            # Uji deteksi pelanggaran paritas jika model RAG diubah berbeda
            bad_cfg = AppConfig(primary_model="different-model")
            bad_adapter = LLMProviderAdapter(
                bad_cfg, transport=lambda p, m, msgs, params: "Jawaban beda [SUMBER 1]."
            )
            r_bad_log = tmp_path / "rag_bad.jsonl"
            run_batch(bad_cfg, bad_adapter, questions, mode="rag", output_log_path=r_bad_log, retriever=retriever)
            bad_issues = validate_experiment_logs(b_log, r_bad_log, expected_count=3)
            self.assertTrue(any("variabel kontrol" in msg for msg in bad_issues))

    def test_api_script_dry_run(self) -> None:
        code = test_api_main(["--env-file", ".env.example", "--dry-run"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
