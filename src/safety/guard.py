"""Safety Pre-Check Guard untuk SiagaBanjir (FR-01, FR-05, FR-07, FR-08).

Menjalankan deteksi deterministik sebelum retrieval dan LLM agar penanganan
situasi darurat akut, permintaan prediksi real-time, input kosong/ambigu, dan
pertanyaan jelas di luar domain banjir tidak bergantung pada memori bebas LLM.

Batas tanggung jawab (ARCHITECTURE.md Bag. 4 & 11):
- Tidak menggantikan Evidence Gate maupun evaluasi groundedness.
- Wajib diuji false positive & false negative (tests/test_safety_guard.py).
"""

from __future__ import annotations

import re

from src.schemas import SafetyCheckResult

EMPTY_INPUT_MESSAGE = (
    "Pertanyaan masih kosong. Silakan tuliskan pertanyaan seputar kesiapsiagaan "
    "banjir di Indonesia, misalnya persiapan sebelum banjir, langkah aman saat "
    "banjir, atau pemulihan setelah banjir."
)

EMERGENCY_OVERRIDE_MESSAGE = (
    "**PERINGATAN SITUASI DARURAT:**\n"
    "SiagaBanjir adalah prototipe chatbot edukasi akademik dan **bukan layanan "
    "darurat maupun pengganti petugas resmi**. Chatbot ini tidak dapat memberikan "
    "rute atau keputusan evakuasi untuk lokasi Anda secara langsung.\n\n"
    "Segera utamakan keselamatan diri Anda dan orang di sekitar, ikuti arahan "
    "petugas di lapangan, dan hubungi layanan darurat atau otoritas resmi setempat:\n"
    "- **112** — Nomor Darurat Nasional *(jika layanan tersedia di wilayah Anda)*\n"
    "- **115** — Basarnas (pencarian dan pertolongan)\n"
    "- **BPBD** (Badan Penanggulangan Bencana Daerah) atau **BNPB** setempat\n"
    "- Perangkat RT/RW, relawan, atau aparat keamanan terdekat di lokasi Anda."
)

PREDICTION_REFUSAL_MESSAGE = (
    "SiagaBanjir adalah prototipe edukasi kesiapsiagaan banjir dan **tidak "
    "memiliki data cuaca, ketinggian sungai, maupun sistem peringatan dini "
    "real-time**, sehingga tidak dapat memprediksi apakah atau kapan suatu "
    "wilayah akan mengalami banjir.\n\n"
    "Untuk prakiraan cuaca, peringatan dini banjir, dan status siaga terkini, "
    "silakan memantau langsung kanal resmi:\n"
    "- **BMKG** (peringatan dini cuaca dan curah hujan)\n"
    "- **BPBD** setempat dan **BNPB** (informasi status kebencanaan daerah)."
)

CLARIFICATION_MESSAGE = (
    "Pertanyaan Anda masih terlalu singkat atau umum sehingga belum jelas bagian "
    "mana yang ingin Anda ketahui. Mohon perjelas apakah Anda ingin menanyakan "
    "topik:\n"
    "1. **Sebelum banjir** (misalnya persiapan rumah tangga atau isi Tas Siaga Bencana)\n"
    "2. **Saat banjir** (misalnya langkah keselamatan edukatif jika air mulai masuk rumah)\n"
    "3. **Setelah banjir** (misalnya pembersihan rumah dan kewaspadaan kelistrikan/kesehatan)\n"
    "4. **Istilah kebencanaan resmi** (misalnya InaRISK, DIBI, atau BNPB)\n\n"
    "Contoh pertanyaan: *\"Apa saja isi Tas Siaga Bencana untuk menghadapi banjir?\"*"
)

OUT_OF_DOMAIN_MESSAGE = (
    "Maaf, pertanyaan tersebut berada di luar cakupan **SiagaBanjir**. "
    "SiagaBanjir difokuskan khusus untuk **edukasi kesiapsiagaan banjir di "
    "Indonesia** (sebelum banjir, saat banjir, setelah banjir, serta istilah "
    "kebencanaan terkait).\n\n"
    "Silakan ajukan pertanyaan yang berkaitan dengan kesiapsiagaan banjir, "
    "misalnya persiapan sebelum musim hujan, isi Tas Siaga Bencana, atau "
    "langkah aman setelah banjir surut."
)

# Pola pertanyaan edukatif umum (untuk mencegah false positive darurat akut)
_EDUCATIONAL_FRAMING_RE = re.compile(
    r"\b("
    r"apa saja|apa yang harus dilakukan|bagaimana cara|tips|panduan|langkah|"
    r"edukasi|penjelasan|jelaskan|mengapa|kenapa|apa arti|apa maksud|"
    r"apa perbedaan|sebutkan|contoh|siapkan|persiapan|tas siaga|jika air mulai"
    r")\b",
    re.IGNORECASE,
)

# 1. Pola situasi darurat akut (FR-07): bahaya langsung sedang berlangsung
_ACUTE_EMERGENCY_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "acute_trapped",
        re.compile(
            r"\b(terjebak|terkepung|tidak bisa keluar|ga bisa keluar|gak bisa keluar)\b"
            r".{0,40}\b(banjir|air|atap|genteng|rumah|lantai|sekarang|tolong|sini)\b"
            r"|\b(banjir|air|atap|genteng|rumah)\b.{0,45}"
            r"\b(terjebak|terkepung|tidak bisa keluar|ga bisa keluar|gak bisa keluar)\b"
            r"|\b(di atap|di genteng|naik ke atap)\b.{0,30}\b(tolong|sekarang|terjebak|banjir)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "acute_water_level_now",
        re.compile(
            r"\b(air|banjir)\b.{0,30}\b(sudah|udah|lagi|sedang)\b.{0,25}"
            r"\b(sedada|seleher|sepinggang|sepinggul|setinggi dada|setinggi leher|"
            r"masuk deras|naik cepat|meluap ke rumah|menenggelamkan)\b"
            r"|\b(air|banjir)\b.{0,20}\b(masuk deras|naik cepat|meluap deras)\b"
            r".{0,35}\b(sekarang|saat ini|rumah saya|rumah kami|tolong)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "acute_evacuation_now",
        re.compile(
            r"\b(tolong|bantu|butuh|minta)\b.{0,25}\b(evakuasi|selamatkan|penyelamatan|sar|perahu karet)\b"
            r"|\b(harus evakuasi ke mana sekarang|rute evakuasi sekarang|evakuasi sekarang)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "acute_life_threat_now",
        re.compile(
            r"\b(ada yang|orang|anak saya|keluarga saya|tetangga saya|saya|kami)\b.{0,30}"
            r"\b(hanyut|tenggelam|kesetrum|tersengat listrik|luka parah|pingsan|hilang terbawa arus)\b"
            r"|\b(tersengat listrik|kesetrum|hanyut)\b.{0,20}\b(sekarang|saat ini|barusan|tolong)\b",
            re.IGNORECASE,
        ),
    ),
)

# 2. Pola permintaan prediksi / peringatan dini operasional real-time (FR-07)
_PREDICTION_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "prediction_will_flood",
        re.compile(
            r"\b(apakah|apa|kira[- ]?kira|bakal|akan|prediksi|ramalan|prakiraan)\b.{0,35}"
            r"\b(besok|hari ini|malam ini|nanti malam|minggu ini|sebentar lagi|sekarang|jam berapa)\b.{0,35}"
            r"\b(banjir|meluap|hujan deras|air naik|genangan|siaga)\b"
            r"|\b(apakah|apa)\b.{0,35}\b(banjir|meluap)\b.{0,25}\b(besok|hari ini|malam ini|nanti|sekarang)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "prediction_early_warning_live",
        re.compile(
            r"\b(peringatan dini|status siaga|tinggi muka air|ketinggian air sungai|debit air|pintu air)\b"
            r".{0,30}\b(sekarang|hari ini|saat ini|terkini|real[- ]?time|wilayah saya|daerah saya|live)\b"
            r"|\b(jam berapa|kapan)\b.{0,30}\b(sungai|kali|bendungan|banjir)\b.{0,25}\b(meluap|surut|datang|terjadi)\b"
            r"|\b(prediksi banjir|ramalkan banjir|kasih peringatan dini)\b",
            re.IGNORECASE,
        ),
    ),
)

# 3. Pola input sangat singkat / ambigu (FR-08)
_AMBIGUOUS_EXACT: frozenset[str] = frozenset(
    {
        "banjir",
        "bahaya",
        "siaga",
        "bantuan",
        "evakuasi",
        "darurat",
        "air",
        "hujan",
        "bencana",
        "harus bagaimana",
        "gimana",
        "bagaimana",
        "apa ya",
        "bingung",
        "info",
        "info banjir",
        "tentang banjir",
        "banjir gimana",
        "banjir bagaimana",
        "tolong bantu",
        "halo",
        "hai",
        "tes",
        "test",
    }
)

# 4. Kata kunci spesifik domain banjir (bukan istilah bencana umum seperti "evakuasi")
_FLOOD_DOMAIN_RE = re.compile(
    r"\b("
    r"banjir|genangan|hujan|hidrometeorologi|"
    r"tas siaga|tsb|bnpb|bpbd|bmkg|basarnas|inarisk|dibi|pentahelix|dana siap pakai|dsp|"
    r"saluran air|drainase|selokan|sungai|tanggul|arus deras|"
    r"pascabanjir|pasca banjir|surut|leptospirosis"
    r")\b",
    re.IGNORECASE,
)

# Kata kunci topik non-banjir yang jelas di luar domain (FR-05)
_OUT_OF_DOMAIN_RE = re.compile(
    r"\b("
    r"resep|masak|nasi goreng|rendang|kue|kopi|restoran|"
    r"coding|koding|python|javascript|html|css|sql|algoritma|bug|"
    r"sepak bola|bola|badminton|nba|moto ?gp|skor pertandingan|liga|"
    r"presiden|pemilu|partai|saham|kripto|bitcoin|forex|investasi|"
    r"film|lagu|musik|artis|gosip|game|mlbb|valorant|"
    r"wisata|tiket pesawat|hotel|pacar|cinta|puisi|pantun|"
    r"matematika|integral|turunan|fisika kuantum|"
    r"gempa bumi|tsunami|gunung meletus|erupsi|karhutla|kebakaran hutan|puting beliung|kekeringan"
    r")\b",
    re.IGNORECASE,
)


def _normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


class SafetyGuard:
    """Penjaga gerbang keselamatan pra-retrieval & pra-LLM (WF-006 / WF-023)."""

    def check(self, user_query: str) -> SafetyCheckResult:
        """Mengevaluasi input pengguna secara deterministik."""
        if user_query is None or not str(user_query).strip():
            return SafetyCheckResult(
                category="empty_input",
                bypass_llm=True,
                override_message=EMPTY_INPUT_MESSAGE,
                matched_rule="empty_or_whitespace",
            )

        raw = str(user_query).strip()
        norm = _normalize_text(raw)

        # 1. Prioritas tertinggi: Situasi darurat akut (FR-07)
        # Kecualikan kalimat yang murni framing edukatif tanpa kata "sekarang/tolong/terjebak"
        is_educational_only = bool(_EDUCATIONAL_FRAMING_RE.search(raw)) and not bool(
            re.search(
                r"\b(sekarang|saat ini|tolong|terjebak|terkepung|barusan|saya di atap|sedada|seleher)\b",
                raw,
                re.IGNORECASE,
            )
        )
        if not is_educational_only:
            for rule_name, pattern in _ACUTE_EMERGENCY_RULES:
                if pattern.search(raw):
                    return SafetyCheckResult(
                        category="acute_emergency",
                        bypass_llm=True,
                        override_message=EMERGENCY_OVERRIDE_MESSAGE,
                        matched_rule=rule_name,
                    )

        # 2. Permintaan prediksi / peringatan dini operasional real-time (FR-07)
        for rule_name, pattern in _PREDICTION_RULES:
            if pattern.search(raw):
                return SafetyCheckResult(
                    category="prediction_request",
                    bypass_llm=True,
                    override_message=PREDICTION_REFUSAL_MESSAGE,
                    matched_rule=rule_name,
                )

        # 3. Input sangat singkat / ambigu (FR-08)
        tokens = norm.split()
        if not tokens:
            return SafetyCheckResult(
                category="empty_input",
                bypass_llm=True,
                override_message=EMPTY_INPUT_MESSAGE,
                matched_rule="punctuation_only",
            )
        if norm in _AMBIGUOUS_EXACT or (
            len(tokens) <= 2 and not _OUT_OF_DOMAIN_RE.search(raw)
        ):
            return SafetyCheckResult(
                category="ambiguous",
                bypass_llm=True,
                override_message=CLARIFICATION_MESSAGE,
                matched_rule="short_or_ambiguous_input",
            )

        # 4. Pertanyaan jelas di luar domain banjir (FR-05)
        has_flood_term = bool(_FLOOD_DOMAIN_RE.search(raw))
        has_ood_term = bool(_OUT_OF_DOMAIN_RE.search(raw))
        if has_ood_term and not has_flood_term:
            return SafetyCheckResult(
                category="out_of_domain",
                bypass_llm=True,
                override_message=OUT_OF_DOMAIN_MESSAGE,
                matched_rule="explicit_out_of_domain",
            )

        return SafetyCheckResult(
            category="normal",
            bypass_llm=False,
            override_message=None,
            matched_rule=None,
        )
