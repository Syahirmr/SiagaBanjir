"""Unit tests SafetyGuard termasuk pengujian False Positive & False Negative (WF-023).

Memverifikasi persyaratan ARCHITECTURE.md v0.2 Bag. 11.1:
- Kasus darurat akut & prediksi tidak boleh lolos (anti false negative).
- Pertanyaan edukatif normal (termasuk fase saat banjir) tidak boleh salah
  terblokir sebagai darurat akut atau out-of-domain (anti false positive).
"""

from __future__ import annotations

import unittest

from src.safety.guard import SafetyGuard


class TestSafetyGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = SafetyGuard()

    def test_empty_and_whitespace_inputs(self) -> None:
        for query in ("", "   ", "\n\t", "???"):
            res = self.guard.check(query)
            self.assertEqual(res.category, "empty_input", msg=f"query={query!r}")
            self.assertTrue(res.bypass_llm)

    def test_acute_emergency_true_positives_no_false_negatives(self) -> None:
        emergencies = [
            "Tolong, air banjir sudah sedada di rumah saya sekarang!",
            "Saya terjebak di atap rumah karena banjir, tolong evakuasi sekarang.",
            "Ada tetangga saya hanyut terbawa arus banjir saat ini!",
            "Kami butuh bantuan penyelamatan perahu karet sekarang juga.",
            "Anak saya tersengat listrik saat banjir barusan, tolong!",
            "Air masuk deras sekali ke rumah saya sekarang, tidak bisa keluar.",
        ]
        for query in emergencies:
            res = self.guard.check(query)
            self.assertEqual(res.category, "acute_emergency", msg=f"FN on: {query!r}")
            self.assertTrue(res.bypass_llm)
            assert res.override_message is not None
            self.assertIn("bukan layanan darurat", res.override_message.lower())
            self.assertIn("112", res.override_message)
            self.assertIn("jika layanan tersedia di wilayah anda", res.override_message.lower())
            self.assertIn("115", res.override_message)
            self.assertIn("BPBD", res.override_message)

    def test_educational_flood_queries_no_false_positives(self) -> None:
        educational = [
            "Apa saja yang perlu disiapkan sebelum musim hujan dan banjir?",
            "Apa isi Tas Siaga Bencana yang disarankan BNPB untuk banjir?",
            "Apa yang harus dilakukan jika air banjir mulai masuk ke dalam rumah?",
            "Bagaimana cara aman mematikan listrik saat banjir terjadi?",
            "Langkah pemulihan apa yang perlu dilakukan setelah banjir surut?",
            "Apa arti istilah InaRISK dan DIBI dalam kesiapsiagaan banjir?",
            "Mengapa tidak boleh berjalan menerobos arus deras saat banjir?",
            "Bagaimana panduan menyelamatkan dokumen penting sebelum banjir?",
        ]
        for query in educational:
            res = self.guard.check(query)
            self.assertEqual(res.category, "normal", msg=f"FP on: {query!r} -> {res}")
            self.assertFalse(res.bypass_llm)

    def test_prediction_requests_refused_with_bmkg_referral(self) -> None:
        predictions = [
            "Apakah besok Bekasi akan banjir?",
            "Jam berapa sungai Ciliwung meluap malam ini?",
            "Kasih peringatan dini banjir untuk wilayah saya sekarang.",
            "Kira-kira hari ini hujan deras bikin banjir tidak?",
            "Berapa tinggi muka air pintu air sekarang secara real-time?",
        ]
        for query in predictions:
            res = self.guard.check(query)
            self.assertEqual(res.category, "prediction_request", msg=f"FN on: {query!r}")
            self.assertTrue(res.bypass_llm)
            assert res.override_message is not None
            self.assertIn("BMKG", res.override_message)
            self.assertIn("BPBD", res.override_message)

    def test_ambiguous_inputs_request_clarification(self) -> None:
        ambiguous_inputs = [
            "banjir",
            "bahaya",
            "harus bagaimana?",
            "siaga",
            "info banjir",
        ]
        for query in ambiguous_inputs:
            res = self.guard.check(query)
            self.assertEqual(res.category, "ambiguous", msg=f"query={query!r}")
            self.assertTrue(res.bypass_llm)
            assert res.override_message is not None
            self.assertIn("Sebelum banjir", res.override_message)
            self.assertIn("Saat banjir", res.override_message)
            self.assertIn("Setelah banjir", res.override_message)

    def test_out_of_domain_queries_politely_refused(self) -> None:
        ood_queries = [
            "Tolong berikan resep nasi goreng spesial yang enak.",
            "Bagaimana cara memperbaiki bug coding Python di fungsi rekursif?",
            "Berapa skor pertandingan sepak bola liga tadi malam?",
            "Apa langkah evakuasi saat gunung meletus dan tsunami?",
        ]
        for query in ood_queries:
            res = self.guard.check(query)
            self.assertEqual(res.category, "out_of_domain", msg=f"query={query!r}")
            self.assertTrue(res.bypass_llm)


if __name__ == "__main__":
    unittest.main()
