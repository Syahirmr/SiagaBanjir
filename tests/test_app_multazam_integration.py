"""Smoke tests integrasi UI app.py berbasis starter Multazam (tanpa server live)."""

from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from app import (
    AIMessage,
    CORPUS_UNAVAILABLE_LABEL,
    HumanMessage,
    SystemMessage,
    corpus_status_label,
    extract_message_text,
    run_app,
)
from scripts.run_eval import run_batch
from src.config import AppConfig
from src.llm.client import LLMProviderAdapter
from src.logging.eval_logger import StructuredJsonlLogger
from src.pipeline.chat_service import ChatService
from src.retrieval.retriever import BM25CorpusRetriever
from src.schemas import ChatRequest


class _FakeStreamlit:
    """Stub minimal API Streamlit yang dipakai starter Multazam & app.py."""

    def __init__(self, mode: str = "rag", prompt: str | None = None) -> None:
        self.mode = mode
        self.prompt = prompt
        self.session_state: dict[str, Any] = {}
        self.titles: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.chat_renders: list[tuple[str, str]] = []
        self._current_role: str | None = None
        self.stopped = False
        self.sidebar = nullcontext()

    def set_page_config(self, **kwargs: Any) -> None:
        _ = kwargs

    def title(self, text: str) -> None:
        self.titles.append(text)

    def subheader(self, text: str) -> None:
        _ = text

    def caption(self, text: str) -> None:
        _ = text

    def warning(self, text: str) -> None:
        self.warnings.append(text)

    def info(self, text: str) -> None:
        self.infos.append(text)

    def radio(self, label: str, options: list[str], index: int = 0, **kwargs: Any) -> str:
        _ = (label, options, index, kwargs)
        return self.mode

    def button(self, label: str) -> bool:
        _ = label
        return False

    def rerun(self) -> None:
        pass

    def chat_message(self, name: str):
        parent = self

        class _Ctx:
            def __enter__(self_inner):
                parent._current_role = name
                return parent

            def __exit__(self_inner, exc_type, exc, tb):
                parent._current_role = None
                return False

        return _Ctx()

    def markdown(self, body: str = "", **kwargs: Any) -> None:
        _ = kwargs
        if self._current_role is not None:
            self.chat_renders.append((self._current_role, body))

    def chat_input(self, placeholder: str = "") -> str | None:
        _ = placeholder
        return self.prompt

    def spinner(self, text: str):
        _ = text
        return nullcontext()

    def stop(self) -> None:
        self.stopped = True


class TestAppMultazamIntegration(unittest.TestCase):
    def test_app_reports_unavailable_corpus_honestly_and_stops_on_no_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = AppConfig(
                corpus_manifest_path=Path(tmp) / "missing_manifest.json",
                corpus_chunks_path=Path(tmp) / "missing_chunks.jsonl",
            )
            ret = BM25CorpusRetriever(cfg.corpus_manifest_path, cfg.corpus_chunks_path)
            self.assertEqual(corpus_status_label(cfg, ret), CORPUS_UNAVAILABLE_LABEL)

            adapter = LLMProviderAdapter(cfg, transport=lambda *a: "unused")
            svc = ChatService(cfg, adapter, retriever=ret)
            fake_st = _FakeStreamlit(mode="rag", prompt=None)
            run_app(st_module=fake_st, config_override=cfg, service_override=svc)

            self.assertTrue(fake_st.stopped)
            self.assertEqual(fake_st.titles, ["SiagaBanjir"])
            self.assertEqual(len(fake_st.warnings), 1)
            self.assertIsInstance(fake_st.session_state["chat_history"][0], SystemMessage)

    def test_app_baseline_mode_runs_without_corpus_using_multazam_history_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cfg = AppConfig(
                primary_model="mock-model",
                fallback_model="mock-fallback",
                corpus_manifest_path=tmp_path / "missing_manifest.json",
                corpus_chunks_path=tmp_path / "missing_chunks.jsonl",
            )
            log_path = tmp_path / "demo_baseline.jsonl"
            logger = StructuredJsonlLogger(log_path)
            adapter = LLMProviderAdapter(
                cfg, transport=lambda *a: "Siapkan dokumen penting sebelum hujan deras."
            )
            svc = ChatService(cfg, adapter, retriever=None, logger=logger)

            fake_st = _FakeStreamlit(
                mode="baseline", prompt="Apa persiapan sebelum musim hujan?"
            )
            run_app(st_module=fake_st, config_override=cfg, service_override=svc)

            history = fake_st.session_state["chat_history"]
            self.assertEqual(len(history), 3)
            self.assertIsInstance(history[0], SystemMessage)
            self.assertIsInstance(history[1], HumanMessage)
            self.assertIsInstance(history[2], AIMessage)
            self.assertIn("dokumen penting", extract_message_text(history[2]))
            self.assertIn("Mode Baseline", extract_message_text(history[2]))
            logged = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(logged["mode"], "baseline")
            self.assertEqual(logged["retrieval_status"], "not_applicable")
            self.assertEqual(logged["outcome_type"], "answered_baseline")

    def test_config_error_and_retrieval_error_messages_are_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = AppConfig(
                primary_model="TBD_AFTER_WF016",
                corpus_manifest_path=Path(tmp) / "missing_manifest.json",
                corpus_chunks_path=Path(tmp) / "missing_chunks.jsonl",
            )
            ret = BM25CorpusRetriever(cfg.corpus_manifest_path, cfg.corpus_chunks_path)
            adapter = LLMProviderAdapter(cfg)
            svc = ChatService(cfg, adapter, retriever=ret)

            rag_resp = svc.handle_request(
                ChatRequest(
                    request_id="rag_no_corpus",
                    user_query="Apa saja isi Tas Siaga Bencana untuk menghadapi banjir?",
                    mode="rag",
                    run_context="demo",
                    allow_fallback=False,
                )
            )
            self.assertEqual(rag_resp.outcome_type, "retrieval_error")
            self.assertEqual(rag_resp.error_type, "index_error")
            self.assertIn("belum tersedia", rag_resp.answer_text.lower())

            base_resp = svc.handle_request(
                ChatRequest(
                    request_id="base_tbd_model",
                    user_query="Apa saja isi Tas Siaga Bencana untuk menghadapi banjir?",
                    mode="baseline",
                    run_context="demo",
                    allow_fallback=False,
                )
            )
            self.assertEqual(base_resp.outcome_type, "api_error")
            self.assertEqual(base_resp.error_type, "config_error")
            self.assertIn("belum ditetapkan", base_resp.answer_text.lower())
            self.assertNotIn("korpus", base_resp.answer_text.lower())

    def test_app_rag_mode_emergency_bypasses_llm_even_without_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = AppConfig(
                primary_model="mock-model",
                corpus_manifest_path=Path(tmp) / "missing_manifest.json",
                corpus_chunks_path=Path(tmp) / "missing_chunks.jsonl",
            )
            called = {"count": 0}

            def fail_if_called(*args):
                called["count"] += 1
                raise AssertionError("LLM tidak boleh dipanggil pada situasi darurat akut!")

            adapter = LLMProviderAdapter(cfg, transport=fail_if_called)
            svc = ChatService(cfg, adapter, retriever=None)

            fake_st = _FakeStreamlit(
                mode="rag",
                prompt="Tolong air sudah sedada di rumah saya sekarang, terjebak di atap!",
            )
            run_app(st_module=fake_st, config_override=cfg, service_override=svc)
            self.assertEqual(called["count"], 0)
            reply = extract_message_text(fake_st.session_state["chat_history"][-1])
            self.assertIn("112", reply)
            self.assertIn("115", reply)

    def test_baseline_batch_experiment_runs_independently_without_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cfg = AppConfig(primary_model="mock-baseline-model")
            adapter = LLMProviderAdapter(
                cfg, transport=lambda *a: "Respons baseline uji."
            )
            b_log = tmp_path / "baseline_only.jsonl"
            summaries = run_batch(
                cfg,
                adapter,
                [{"test_id": "Q-01", "query": "Apa isi tas siaga bencana?"}],
                mode="baseline",
                output_log_path=b_log,
                retriever=None,
            )
            self.assertEqual(summaries[0]["outcome_type"], "answered_baseline")
            row = json.loads(b_log.read_text(encoding="utf-8").splitlines()[0])
            self.assertFalse(row["allow_fallback"])
            self.assertEqual(row["prompt_version"], cfg.prompt_version)


if __name__ == "__main__":
    unittest.main()
