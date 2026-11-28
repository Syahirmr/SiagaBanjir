"""Skrip pengujian aktual Gemini API & Groq API untuk SiagaBanjir (WF-016 / OD-02).

Prinsip:
- Tidak mengunci nama model sebelum pengujian aktual dijalankan.
- Membaca kredensial hanya dari `.env` lokal / environment variable.
- Menyimpan hasil uji (status, latensi, ringkasan respons, error tersanitasi)
  ke berkas JSONL tanpa pernah menuliskan API key.

Contoh penggunaan:
    python scripts/test_api.py --dry-run
    python scripts/test_api.py --gemini-models <model_a>,<model_b> --groq-models <model_c>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import AppConfig, load_config
from src.llm.client import LLMProviderAdapter
from src.llm.prompts import build_baseline_messages

SAMPLE_PROBES: tuple[dict[str, str], ...] = (
    {
        "probe_id": "PROBE-01",
        "query": "Sebutkan tiga langkah persiapan rumah tangga sebelum musim hujan untuk mencegah dampak banjir.",
    },
    {
        "probe_id": "PROBE-02",
        "query": "Apa saja yang perlu diperhatikan terkait kelistrikan jika air mulai masuk ke dalam rumah saat banjir?",
    },
)


def run_provider_probes(
    base_config: AppConfig,
    provider: str,
    models: list[str],
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Menjalankan pertanyaan uji pada daftar kandidat model untuk satu provider."""
    results: list[dict[str, Any]] = []
    for model_id in models:
        cfg = AppConfig(
            primary_provider=provider,
            fallback_provider=provider,
            primary_model=model_id,
            fallback_model=model_id,
            llm_temperature=base_config.llm_temperature,
            llm_max_tokens=base_config.llm_max_tokens,
            llm_timeout_sec=base_config.llm_timeout_sec,
            prompt_version=base_config.prompt_version,
            gemini_api_key=base_config.gemini_api_key,
            groq_api_key=base_config.groq_api_key,
        )
        adapter = LLMProviderAdapter(config=cfg)
        for probe in SAMPLE_PROBES:
            if dry_run:
                results.append(
                    {
                        "timestamp_utc": datetime.now(timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "provider": provider,
                        "model_id": model_id,
                        "probe_id": probe["probe_id"],
                        "api_status": "dry_run",
                        "has_key": (
                            cfg.has_gemini_key
                            if provider == "gemini"
                            else cfg.has_groq_key
                        ),
                        "latency_sec": 0.0,
                        "response_chars": 0,
                        "error_type": None,
                        "error_message_sanitized": None,
                    }
                )
                continue

            messages = build_baseline_messages(probe["query"], cfg.prompt_version)
            res = adapter.generate(messages=messages, allow_fallback=False)
            print(
                f"  [{provider} | {model_id} | {probe['probe_id']}] "
                f"status={res.api_status} latency={res.latency_sec}s "
                f"chars={len(res.raw_text or '')} err={res.error_type}",
                flush=True,
            )
            results.append(
                {
                    "timestamp_utc": datetime.now(timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "provider": provider,
                    "model_id": model_id,
                    "probe_id": probe["probe_id"],
                    "api_status": res.api_status,
                    "latency_sec": res.latency_sec,
                    "response_chars": len(res.raw_text or ""),
                    "response_preview": (res.raw_text or "")[:160],
                    "error_type": res.error_type,
                    "error_message_sanitized": res.error_message_sanitized,
                }
            )
    return results


def _split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Uji aktual Gemini API & Groq API untuk SiagaBanjir (WF-016)."
    )
    parser.add_argument("--env-file", default=".env", help="Path file .env lokal.")
    parser.add_argument(
        "--gemini-models",
        default="",
        help="Daftar kandidat model Gemini dipisah koma.",
    )
    parser.add_argument(
        "--groq-models",
        default="",
        help="Daftar kandidat model Groq dipisah koma.",
    )
    parser.add_argument(
        "--output",
        default="logs/api_test_results.jsonl",
        help="Lokasi output log JSONL hasil uji API.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validasi konfigurasi tanpa memanggil API eksternal.",
    )
    args = parser.parse_args(argv)

    cfg = load_config(env_file=args.env_file)
    gemini_models = _split_csv(args.gemini_models)
    groq_models = _split_csv(args.groq_models)

    if not gemini_models and cfg.is_primary_model_configured and cfg.primary_provider == "gemini":
        gemini_models = [cfg.primary_model]
    if not groq_models and cfg.is_fallback_model_configured and cfg.fallback_provider == "groq":
        groq_models = [cfg.fallback_model]

    summary = cfg.safe_summary()
    print("Konfigurasi aman:", json.dumps(summary, ensure_ascii=False))

    if not gemini_models and not groq_models:
        print(
            "Belum ada kandidat model diberikan. Gunakan --gemini-models dan/atau "
            "--groq-models untuk menjalankan pengujian WF-016."
        )
        return 0 if args.dry_run else 2

    all_rows: list[dict[str, Any]] = []
    if gemini_models:
        all_rows.extend(run_provider_probes(cfg, "gemini", gemini_models, dry_run=args.dry_run))
    if groq_models:
        all_rows.extend(run_provider_probes(cfg, "groq", groq_models, dry_run=args.dry_run))

    if not args.dry_run:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("a", encoding="utf-8") as fh:
            for row in all_rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"Tersimpan {len(all_rows)} baris hasil uji API ke {out_path}.")
    else:
        print(f"Dry-run selesai ({len(all_rows)} skenario tervalidasi, 0 API call).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
