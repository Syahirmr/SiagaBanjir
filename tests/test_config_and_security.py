"""Unit tests untuk konfigurasi, keamanan kredensial, dan kontrak request (WF-015)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.config import AppConfig, load_config, parse_env_file, sanitize_secret_text
from src.schemas import ChatRequest


class TestConfigAndSecurity(unittest.TestCase):
    def test_parse_env_file_handles_comments_quotes_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nonexistent.env"
            self.assertEqual(parse_env_file(missing), {})

            env_file = Path(tmp) / ".env"
            env_file.write_text(
                "# komentar\n"
                "PRIMARY_PROVIDER=gemini\n"
                "LLM_TEMPERATURE='0.2'\n"
                'PROMPT_VERSION="prompt_v1.0"\n'
                "export LLM_MAX_TOKENS=512\n",
                encoding="utf-8",
            )
            parsed = parse_env_file(env_file)
            self.assertEqual(parsed["PRIMARY_PROVIDER"], "gemini")
            self.assertEqual(parsed["LLM_TEMPERATURE"], "0.2")
            self.assertEqual(parsed["PROMPT_VERSION"], "prompt_v1.0")
            self.assertEqual(parsed["LLM_MAX_TOKENS"], "512")

    def test_secrets_never_appear_in_repr_or_safe_summary(self) -> None:
        fake_gem = "AIzaSyFAKEKEY1234567890ABCDEF"
        fake_groq = "gsk_FAKEGROQKEY1234567890ABCDEF"
        cfg = AppConfig(
            gemini_api_key=fake_gem,
            groq_api_key=fake_groq,
        )
        self.assertTrue(cfg.has_gemini_key)
        self.assertTrue(cfg.has_groq_key)
        self.assertNotIn(fake_gem, repr(cfg))
        self.assertNotIn(fake_groq, repr(cfg))
        summary_str = str(cfg.safe_summary())
        self.assertNotIn(fake_gem, summary_str)
        self.assertNotIn(fake_groq, summary_str)

    def test_sanitize_secret_text_redacts_keys_and_headers(self) -> None:
        fake_gem = "AIzaSySecretToken999999999"
        fake_groq = "gsk_SecretGroqToken99999999"
        raw = (
            f"HTTP 401 Authorization: Bearer {fake_groq} "
            f"url=https://api.test?key={fake_gem}"
        )
        cleaned = sanitize_secret_text(raw, (fake_gem, fake_groq))
        assert cleaned is not None
        self.assertNotIn(fake_gem, cleaned)
        self.assertNotIn(fake_groq, cleaned)
        self.assertIn("[REDACTED]", cleaned)

    def test_placeholder_keys_and_models_rejected_by_validator(self) -> None:
        cfg = load_config(
            env_file=".env.example",
            environ={},
        )
        self.assertFalse(cfg.has_gemini_key)
        self.assertFalse(cfg.has_groq_key)
        self.assertFalse(cfg.is_primary_model_configured)
        issues = cfg.validate_for_runtime(require_corpus=False)
        self.assertGreaterEqual(len(issues), 2)

    def test_chat_request_blocks_fallback_in_experiment_mode(self) -> None:
        with self.assertRaises(ValueError):
            ChatRequest(
                request_id="req_1",
                user_query="Apa isi tas siaga bencana?",
                mode="rag",
                run_context="experiment",
                allow_fallback=True,
                test_id="Q-01",
            )


if __name__ == "__main__":
    unittest.main()
