"""Regression tests untuk kualitas respons, prompt parity, multi-fase, & safety (7 kasus wajib)."""

from __future__ import annotations

import unittest

from src.config import AppConfig, load_config
from src.llm.client import LLMProviderAdapter
from src.llm.prompts import (
    BASE_SYSTEM_INSTRUCTION,
    DEFAULT_PROMPT_VERSION,
    build_baseline_messages,
    build_rag_messages,
)
from src.pipeline.chat_service import ChatService
from src.safety.guard import SafetyGuard
from src.schemas import ChatRequest, RetrievedChunk


class TestResponseQualityAndRegression(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = SafetyGuard()

    def test_prompt_v1_2_enforces_natural_conversation_and_conservative_safety(self) -> None:
        self.assertEqual(DEFAULT_PROMPT_VERSION, "prompt_v1.3")
        low = BASE_SYSTEM_INSTRUCTION.lower()
        # Tidak mengulang salam/disclaimer & langsung jawab
        self.assertIn("jangan mengulang salam pembuka", low)
        self.assertIn("disclaimer panjang", low)
        self.assertIn("langsung jawab inti pertanyaan", low)
        # Klarifikasi input ambigu 1 kata (FR-08)
        self.assertIn("klarifikasi singkat", low)
        # Keselamatan P0: air banjir, urutan evakuasi, listrik, terjebak lantai atas, air minum
        self.assertIn("panel", low)
        self.assertIn("basah/terendam", low)
        self.assertIn("jangan otomatis naik ke atap/genteng", low)
        self.assertIn("jangan mengklaim perebusan menghilangkan kontaminan kimia", low)
        # Larangan angka/dosis/sitasi palsu tanpa bukti & P1 akurasi
        self.assertIn("tidak ada ketinggian air", low)
        self.assertIn("resep/dosis", low)
        self.assertIn("jangan menyarankan mi instan", low)
        self.assertIn("jangan mencantumkan [sumber n]", low)
        # Multi-fase terstruktur
        self.assertIn("sebelum banjir, saat banjir, setelah banjir", low)

    def test_baseline_and_rag_share_identical_base_prompt_and_max_tokens(self) -> None:
        cfg = load_config(env_file=".env.example", environ={})
        self.assertEqual(cfg.llm_max_tokens, 1400)
        self.assertGreaterEqual(cfg.llm_max_tokens, 1200)
        self.assertLessEqual(cfg.llm_max_tokens, 1500)
        self.assertEqual(cfg.prompt_version, DEFAULT_PROMPT_VERSION)

        chunk = RetrievedChunk("c1", "v1", "Matikan listrik bila masih kering.", 0.9, {"source_id": "S1"})
        base_msgs = build_baseline_messages("Apa isi Tas Siaga Bencana?", cfg.prompt_version)
        rag_msgs = build_rag_messages("Apa isi Tas Siaga Bencana?", [chunk], cfg.prompt_version)

        self.assertTrue(rag_msgs[0]["content"].startswith(base_msgs[0]["content"]))
        self.assertNotIn("<retrieved_context>", base_msgs[1]["content"])
        self.assertIn("<retrieved_context>", rag_msgs[1]["content"])

    def test_seven_mandatory_regression_cases_intent_and_safety_routing(self) -> None:
        # 1-5: Pertanyaan edukatif (sebelum, saat, setelah, 3 fase, panel listrik) -> normal (lanjut ke LLM)
        educational_cases = [
            "Apa saja isi Tas Siaga Bencana untuk menghadapi banjir?",
            "Apa yang harus dilakukan jika air mulai masuk ke rumah?",
            "Bagaimana membersihkan rumah setelah banjir?",
            (
                "Jelaskan langkah kesiapsiagaan sebelum banjir, saat banjir, "
                "dan setelah banjir secara ringkas."
            ),
            "Apa yang harus dilakukan jika air banjir sudah merendam panel listrik?",
        ]
        for query in educational_cases:
            res = self.guard.check(query)
            self.assertEqual(res.category, "normal", msg=f"Salah blokir pada: {query!r} -> {res}")
            self.assertFalse(res.bypass_llm)

        # 6: Di luar domain -> out_of_domain (bypass)
        ood = self.guard.check("Tolong berikan resep rendang daging sapi yang empuk.")
        self.assertEqual(ood.category, "out_of_domain")
        self.assertTrue(ood.bypass_llm)

        # 7: Darurat akut -> acute_emergency (bypass + 112 bersyarat & 115)
        em = self.guard.check("Tolong, air banjir sudah sedada di rumah saya sekarang dan kami terjebak di atap!")
        self.assertEqual(em.category, "acute_emergency")
        self.assertTrue(em.bypass_llm)
        assert em.override_message is not None
        self.assertIn("112", em.override_message)
        self.assertIn("115", em.override_message)

        # Darurat akut panel listrik terendam saat ini -> tetap acute_emergency
        em_panel = self.guard.check("Tolong, panel listrik rumah saya terendam air dan muncul percikan sekarang!")
        self.assertEqual(em_panel.category, "acute_emergency")
        self.assertTrue(em_panel.bypass_llm)

    def test_baseline_never_returns_citations_and_preserves_multiphase_structure(self) -> None:
        cfg = AppConfig(primary_model="mock-model", llm_max_tokens=1400, prompt_version="prompt_v1.2")
        mock_multiphase = (
            "**Sebelum Banjir**\n- Siapkan Tas Siaga Bencana untuk sekitar 3 hari.\n\n"
            "**Saat Banjir**\n- Jauhi instalasi listrik yang tergenang air.\n\n"
            "**Setelah Banjir**\n- Bersihkan lumpur dengan alas kaki dan sarung tangan."
        )
        seen_params = {}

        def transport(provider, model, messages, params):
            seen_params.update(params)
            return mock_multiphase

        svc = ChatService(cfg, LLMProviderAdapter(cfg, transport=transport), retriever=None)
        resp = svc.handle_request(
            ChatRequest(
                request_id="reg_mp_001",
                user_query="Jelaskan langkah sebelum banjir, saat banjir, dan setelah banjir.",
                mode="baseline",
                run_context="experiment",
                allow_fallback=False,
                test_id="Q-MP-01",
            )
        )
        self.assertEqual(resp.outcome_type, "answered_baseline")
        self.assertEqual(resp.citations, [])
        self.assertEqual(resp.retrieved_sources, [])
        self.assertEqual(seen_params["max_tokens"], 1400)
        self.assertIn("Sebelum Banjir", resp.answer_text)
        self.assertIn("Saat Banjir", resp.answer_text)
        self.assertIn("Setelah Banjir", resp.answer_text)


if __name__ == "__main__":
    unittest.main()
