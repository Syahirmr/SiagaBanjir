"""Safety Pre-Check & Post-Check Guard untuk SiagaBanjir (FR-01, FR-05, FR-07, FR-08).

Menjalankan deteksi deterministik kontekstual (pre-check sebelum LLM dan
post-check S3 setelah LLM) agar penanganan situasi darurat akut, permintaan
prediksi real-time, input kosong/ambigu, kebocoran prompt/hoaks palsu, dan
pertanyaan jelas di luar domain banjir tidak bergantung pada memori bebas LLM.

Batas tanggung jawab (ARCHITECTURE.md Bag. 4 & 11):
- Tidak menggantikan Evidence Gate maupun evaluasi groundedness.
- Menangani variasi bahasa/slang Indonesia, konteks, dan negasi agar pertanyaan
  edukasi yang aman tidak ikut terblokir (anti false positive & false negative).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

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
    "**Tindakan penyelamatan utama sekarang:**\n"
    "1. **Segera hubungi bantuan darurat** dan sampaikan **alamat/lokasi jelas "
    "serta jumlah orang yang terjebak atau membutuhkan bantuan**:\n"
    "   - **112** — Nomor Darurat Nasional *(jika layanan tersedia di wilayah Anda)*\n"
    "   - **115** — Basarnas (pencarian dan pertolongan)\n"
    "   - **BPBD** (Badan Penanggulangan Bencana Daerah), **BNPB**, atau RT/RW setempat.\n"
    "2. **Pertahankan posisi di tempat tinggi yang aman** dan beri tanda "
    "keberadaan (senter, kain terang, atau peluit) bila aman.\n"
    "3. **Jangan memasuki air/arus banjir untuk menyelamatkan diri**, **jangan "
    "masuk ke loteng tertutup tanpa akses keluar**, **jangan otomatis naik ke "
    "atap/genteng** tanpa kondisi aman/arahan petugas, dan jauhi instalasi "
    "listrik yang basah atau terendam. **Ikuti instruksi petugas penyelamat.**"
)

EMERGENCY_LPG_MESSAGE = (
    "**PERINGATAN DARURAT KEBOCORAN GAS / LPG:**\n"
    "SiagaBanjir adalah prototipe edukasi dan **bukan layanan darurat maupun "
    "pengganti petugas resmi**.\n\n"
    "**Tindakan penyelamatan utama sekarang:**\n"
    "1. **Jangan menyalakan api, korek, atau mengoperasikan sakelar/peralatan "
    "listrik** (jangan menyalakan maupun mematikan sakelar yang bisa memicu percikan).\n"
    "2. **Segera keluar dan jauhkan seluruh keluarga ke ruang terbuka** berudara "
    "segar, menjauh dari sumber bau gas.\n"
    "3. **Hubungi petugas darurat dari luar area aman**: **112** *(jika layanan "
    "tersedia di wilayah Anda)*, pemadam kebakaran, **BPBD**, atau **BNPB**/RT setempat."
)

EMERGENCY_ELECTRICAL_MESSAGE = (
    "**PERINGATAN DARURAT LISTRIK / KABEL JATUH:**\n"
    "SiagaBanjir adalah prototipe edukasi dan **bukan layanan darurat maupun "
    "pengganti petugas resmi**.\n\n"
    "**Tindakan penyelamatan utama sekarang:**\n"
    "1. **Jangan mendekati, menyentuh, atau memindahkan** kabel listrik jatuh/"
    "putus, panel/MCB/stopkontak yang basah atau terendam, maupun korban yang "
    "masih berada di area beraliran listrik.\n"
    "2. **Segera jauhi area genangan** di sekitar sumber listrik dan peringatkan "
    "orang sekitar agar tetap menjauh.\n"
    "3. **Hubungi segera PLN dan layanan darurat**: **112** *(jika layanan "
    "tersedia di wilayah Anda)*, **Basarnas (115)**, atau **BPBD**/**BNPB** setempat."
)

EMERGENCY_DROWNING_MESSAGE = (
    "**PERINGATAN DARURAT MEDIS (TENGGELAM / TIDAK BERNAPAS NORMAL):**\n"
    "SiagaBanjir adalah prototipe edukasi dan **bukan layanan darurat maupun "
    "pengganti tenaga medis/petugas resmi**.\n\n"
    "**Tindakan penyelamatan utama sekarang:**\n"
    "1. **Prioritaskan bantuan medis darurat segera**: hubungi **112** *(jika "
    "layanan tersedia di wilayah Anda)* atau segera bawa/hubungi **IGD/faskes "
    "terdekat** sambil menyebutkan lokasi jelas. Jika korban masih berada di air "
    "atau membutuhkan penyelamatan/evakuasi, hubungi layanan **SAR/evakuasi** "
    "(**Basarnas 115** atau **BPBD** setempat).\n"
    "2. **Jangan menekan perut atau membalikkan korban** untuk mengeluarkan air "
    "karena berbahaya dan menunda pertolongan medis.\n"
    "3. **Utamakan keselamatan penolong** — jangan terjun ke arus deras tanpa "
    "alat/keahlian; pindahkan korban ke tempat aman jika aman dilakukan dan "
    "ikuti arahan tenaga medis."
)

EMERGENCY_POST_DROWNING_MEDICAL_MESSAGE = (
    "**PERINGATAN EVALUASI MEDIS SEGERA (PASCATENGGELAM — KORBAN SADAR):**\n"
    "SiagaBanjir adalah prototipe edukasi dan **bukan pengganti tenaga medis**.\n\n"
    "**Tindakan utama sekarang:**\n"
    "1. **Bawa segera untuk evaluasi medis** ke **IGD, puskesmas, atau fasilitas "
    "kesehatan terdekat** (atau hubungi bantuan medis darurat **112** *jika "
    "layanan tersedia di wilayah Anda*). Meskipun korban/anak sudah sadar dan "
    "bernapas, gejala seperti **batuk, lemas, muntah, atau napas cepat** setelah "
    "sempat tenggelam tetap berisiko menimbulkan gangguan pernapasan lanjutan.\n"
    "2. **Jangan menekan perut atau membalikkan korban** untuk mengeluarkan air.\n"
    "3. **Pantau napas dan kesadaran terus-menerus** — bila napas menjadi tidak "
    "normal, sesak berat, membiru, atau kesadaran menurun, segera cari bantuan "
    "medis gawat darurat *(layanan medis berbeda dari SAR/evakuasi)*."
)

EMERGENCY_CO_GENERATOR_MESSAGE = (
    "**PERINGATAN DARURAT ASAP GENSET / PAPARAN KARBON MONOKSIDA (CO):**\n"
    "SiagaBanjir adalah prototipe edukasi dan **bukan layanan darurat maupun "
    "pengganti tenaga medis/petugas resmi**.\n\n"
    "**Tindakan penyelamatan utama sekarang:**\n"
    "1. **Segera bawa seluruh penghuni keluar ke udara terbuka** menjauh dari "
    "ruangan tertutup/semi-tertutup. **Jangan mendekati atau kembali ke unit "
    "genset** jika area berasap, pengap, atau berisiko.\n"
    "2. **Jangan mengoperasikan genset** di dalam rumah, garasi, ruangan "
    "semi-tertutup, atau dekat pintu/jendela/ventilasi.\n"
    "3. Jika muncul gejala paparan CO (pusing, mual, muntah, lemas, sesak "
    "napas, atau penurunan kesadaran), **segera rujuk ke bantuan medis** "
    "(**IGD/faskes terdekat** atau **112** *jika layanan tersedia di wilayah "
    "Anda* — rujukan medis berbeda dari layanan SAR/evakuasi)."
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

FAKE_ANNOUNCEMENT_REFUSAL_MESSAGE = (
    "SiagaBanjir tidak dapat membuat pengumuman palsu, hoaks, atau simulasi "
    "penetapan status darurat atas nama instansi resmi mana pun.\n\n"
    "Untuk informasi resmi mengenai status darurat, peringatan dini, dan "
    "prakiraan cuaca, silakan merujuk langsung ke kanal resmi **BNPB** (Badan "
    "Nasional Penanggulangan Bencana), **BPBD** setempat, dan **BMKG**."
)

PROMPT_INJECTION_REFUSAL_MESSAGE = (
    "Maaf, saya tidak dapat mengabaikan aturan keselamatan kebencanaan maupun "
    "mengungkapkan instruksi sistem internal SiagaBanjir.\n\n"
    "Silakan ajukan pertanyaan seputar edukasi kesiapsiagaan banjir yang aman "
    "(sebelum, saat, atau setelah banjir). Untuk kondisi darurat nyata, hubungi "
    "**BPBD**, **BNPB**, **Basarnas (115)**, atau **112** *(jika layanan "
    "tersedia di wilayah Anda)*."
)

# Framing edukatif / hipotetis (untuk mencegah false positive darurat akut)
_EDUCATIONAL_FRAMING_RE = re.compile(
    r"\b("
    r"apa saja|apa yang harus dilakukan|bagaimana cara|tips|panduan|langkah|"
    r"edukasi|penjelasan|jelaskan|mengapa|kenapa|apa arti|apa maksud|"
    r"apa bahaya|apa risiko|apa gejala|apa tanda|ciri[- ]?ciri|apa perbedaan|sebutkan|contoh|siapkan|persiapan|"
    r"tas siaga|jika air mulai|benarkah|mitos|fakta|bolehkah|apakah boleh|"
    r"apakah aman|kalau nanti|misalnya|seandainya|jika seseorang"
    r")\b",
    re.IGNORECASE,
)

# Indikator kuat situasi aktif berlangsung sekarang / dialami langsung
_ACTIVE_URGENCY_RE = re.compile(
    r"\b("
    r"sekarang|saat ini|barusan|tadi|tolong|darurat|cepat|gawat|"
    r"saya terjebak|kami terjebak|saya terkepung|kami terkepung|"
    r"saya di atap|kami di atap|di rumah saya|di rumah kami|di depan rumah|"
    r"rumah saya|rumah kami|keluarga saya|anak saya|bayi saya|ibu saya|"
    r"bapak saya|ayah saya|adik saya|kakak saya|tetangga saya|sekeluarga|"
    r"tidak bisa keluar|ga bisa keluar|gak bisa keluar|"
    r"gak napas|ga napas|tidak bernapas|tak bernapas|"
    r"sedada|seleher|sepinggang|nih|dong"
    r")\b",
    re.IGNORECASE,
)

# Penanda genset belum dinyalakan / masih berupa rencana (bahaya potensial, bukan paparan akut)
_GENERATOR_NOT_RUNNING_RE = re.compile(
    r"\b("
    r"belum dinyalakan|belum nyala|belum hidup|belum dipakai|belum digunakan|"
    r"belum saya nyalakan|belum kami nyalakan|tidak dinyalakan|tidak sedang menyala|"
    r"rencana|berencana|mau menyalakan|ingin menyalakan|akan menyalakan|"
    r"bolehkah|apakah boleh|apakah aman"
    r")\b",
    re.IGNORECASE,
)

# Penanda gejala paparan CO aktif
_ACTIVE_CO_SYMPTOM_OR_SMOKE_RE = re.compile(
    r"\b(pusing|mual|muntah|lemas|sesak|pingsan|tidak sadar|asap|pengap|bau asap|bau knalpot)\b",
    re.IGNORECASE,
)

# Penanda korban tidak bernapas normal / tidak sadar (prioritas darurat medis kritis)
_NON_BREATHING_OR_UNCONSCIOUS_RE = re.compile(
    r"\b(gak napas|ga napas|nggak napas|tidak bernapas|tak bernapas|henti napas|"
    r"napas tidak normal|tidak bernapas normal|megap[- ]?megap|pingsan|gak sadar|ga sadar|tidak sadar)\b",
    re.IGNORECASE,
)

# 1. Pola situasi darurat akut (FR-07): berbasis konteks & slang Indonesia
# Format tuple: (rule_name, regex, override_message)
_ACUTE_EMERGENCY_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "acute_drowning_or_no_breath",
        re.compile(
            r"\b(gak napas|ga napas|nggak napas|tidak bernapas|tak bernapas|henti napas|"
            r"napas tidak normal|tidak bernapas normal|megap[- ]?megap)\b"
            r"|\b(tenggelam|hanyut|kelep|kelelep)\b.{0,50}"
            r"\b(pingsan|gak sadar|ga sadar|tidak sadar|gak napas|ga napas|tidak bernapas|napas tidak normal|megap[- ]?megap)\b"
            r"|\b(ada yang|orang|korban|bayi|anak|adik|kakak|ibu|bapak|ayah|keluarga|tetangga|teman)\b.{0,35}"
            r"\b(hanyut|hilang terbawa arus|pingsan)\b"
            r"|\b(tolong)\b.{0,35}\b(tenggelam|hanyut|kelep|kelelep)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_DROWNING_MESSAGE,
    ),
    (
        "acute_drowning_conscious_symptomatic",
        re.compile(
            r"\b(sempat tenggelam|habis tenggelam|baru tenggelam|tadi tenggelam|tercebur|tenggelam|kelelep)\b.{0,70}"
            r"\b(batuk|lemas|muntah|menggigil|sesak|sadar)\b"
            r"|\b(anak|bayi|korban|orang|adik|kakak)\b.{0,30}\b(sempat tenggelam|tenggelam|kelelep)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_POST_DROWNING_MEDICAL_MESSAGE,
    ),
    (
        "acute_lpg_leak",
        re.compile(
            r"\b(bau elpiji|bau lpg|bau gas|elpiji bocor|lpg bocor|tabung gas bocor|gas bocor|gas mendesis)\b"
            r"(?:.{0,50}\b(sekarang|saat ini|tolong|dapur|rumah|banjir|menyengat|kamar|garasi|nih)\b)?"
            r"|\b(bocor|mendesis)\b.{0,30}\b(elpiji|lpg|tabung gas)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_LPG_MESSAGE,
    ),
    (
        "acute_electrical_or_fallen_wire",
        re.compile(
            r"\b(kesetrum|tersengat listrik|tersetrum)\b"
            r"|\b(kabel listrik|kabel pln|tiang listrik)\b.{0,40}\b(jatuh|putus|roboh|terkelupas|masuk air|di genangan|memercik|percikan)\b"
            r"|\b(jatuh|putus|roboh)\b.{0,30}\b(kabel listrik|kabel pln|tiang listrik)\b"
            r"|\b(panel listrik|mcb|stopkontak|sakelar|colokan)\b.{0,35}\b(percikan|konslet|korslet|keluar api|berasap)\b"
            r"|\b(panel listrik|mcb|stopkontak)\b.{0,35}\b(terendam|tergenang)\b.{0,30}\b(sekarang|saat ini|tolong|rumah saya)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_ELECTRICAL_MESSAGE,
    ),
    (
        "acute_generator_co",
        re.compile(
            r"\b(genset|generator)\b.{0,55}\b(pusing|mual|muntah|lemas|sesak|pingsan|tidak sadar|asap|pengap|bau asap|bau knalpot)\b"
            r"|\b(pusing|mual|muntah|lemas|sesak|pingsan|asap|pengap)\b.{0,55}\b(genset|generator)\b"
            r"|\b(sedang menyala|lagi menyala|sedang hidup|lagi hidup|sudah dinyalakan|sudah nyala|kami menyalakan|saya menyalakan|baru dinyalakan)\b.{0,40}\b(genset|generator)\b.{0,50}\b(dalam rumah|dalam garasi|di garasi|garasi|ruang tertutup|semi[- ]?tertutup|dalam ruangan|teras tertutup)\b"
            r"|\b(genset|generator)\b.{0,35}\b(sedang menyala|lagi menyala|sedang hidup|lagi hidup|sudah nyala|sudah dinyalakan)\b.{0,50}\b(dalam rumah|dalam garasi|di garasi|garasi|ruang tertutup|semi[- ]?tertutup|dalam ruangan|teras tertutup)\b"
            r"|\b(keracunan co|keracunan karbon monoksida|asap genset)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_CO_GENERATOR_MESSAGE,
    ),
    (
        "acute_trapped",
        re.compile(
            r"\b(terjebak|terkepung|kejebak|tidak bisa keluar|ga bisa keluar|gak bisa keluar)\b"
            r".{0,45}\b(banjir|air|atap|genteng|plafon|loteng|rumah|lantai|kamar|sekarang|tolong|sini)\b"
            r"|\b(banjir|air|atap|genteng|plafon|loteng|rumah|lantai)\b.{0,45}"
            r"\b(terjebak|terkepung|kejebak|tidak bisa keluar|ga bisa keluar|gak bisa keluar)\b"
            r"|\b(di atap|di genteng|naik ke atap|di plafon|di loteng)\b.{0,30}\b(tolong|sekarang|terjebak|kejebak|banjir)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_OVERRIDE_MESSAGE,
    ),
    (
        "acute_water_level_now",
        re.compile(
            r"\b(air|banjir)\b.{0,30}\b(sedada|seleher|sepinggang|sepinggul|setinggi dada|setinggi leher|menenggelamkan)\b"
            r"|\b(air|banjir)\b.{0,30}\b(sudah|udah|lagi|sedang)\b.{0,25}\b(masuk deras|naik cepat|meluap ke rumah)\b"
            r"|\b(air|banjir)\b.{0,20}\b(masuk deras|naik cepat|meluap deras)\b.{0,35}\b(sekarang|saat ini|rumah saya|rumah kami|tolong)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_OVERRIDE_MESSAGE,
    ),
    (
        "acute_evacuation_now",
        re.compile(
            r"\b(tolong|bantu|butuh|minta)\b.{0,25}\b(evakuasi|selamatkan|penyelamatan|sar|perahu karet)\b"
            r"|\b(harus evakuasi ke mana sekarang|rute evakuasi sekarang|evakuasi sekarang)\b",
            re.IGNORECASE,
        ),
        EMERGENCY_OVERRIDE_MESSAGE,
    ),
)

# 2. Pola permintaan prediksi / peringatan dini operasional real-time (FR-07)
_PREDICTION_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "prediction_will_flood",
        re.compile(
            r"\b(apakah|apa|kira[- ]?kira|bakal|akan|prediksi|ramalan|prakiraan|"
            r"bisakah|bisa|dapatkah|memastikan|pastikan|menjamin|pasti)\b.{0,40}"
            r"\b(besok|hari ini|malam ini|nanti malam|minggu ini|sebentar lagi|sekarang|jam berapa)\b.{0,40}"
            r"\b(banjir|meluap|hujan deras|air naik|genangan|siaga)\b"
            r"|\b(apakah|apa|bisakah|bisa|dapatkah|memastikan|pastikan)\b.{0,35}"
            r"\b(banjir|meluap)\b.{0,25}\b(besok|hari ini|malam ini|nanti|sekarang)\b"
            r"|\b(besok|hari ini|malam ini|nanti malam|minggu ini)\b.{0,35}"
            r"\b(jam berapa|kapan|pasti|bakal|akan|prediksi)\b.{0,35}"
            r"\b(banjir|meluap|hujan deras|air naik)\b",
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

# 2b. Pola permintaan pembuatan pengumuman resmi palsu / hoaks instansi
_FAKE_ANNOUNCEMENT_RE = re.compile(
    r"\b(buat|buatkan|bikinkan|tulis|tuliskan|karang|susun)\b.{0,45}"
    r"\b(pengumuman|peringatan|berita|pesan|siaran pers|surat|status darurat)\b.{0,35}"
    r"\b(palsu|hoaks|hoax|bohong|seolah[- ]?olah|mengatasnamakan)\b"
    r"|\b(pengumuman palsu|hoaks|hoax|peringatan palsu)\b.{0,45}"
    r"\b(bnpb|bpbd|bmkg|basarnas|pemerintah|darurat|banjir)\b",
    re.IGNORECASE,
)

# 2c. Pola ekstraksi system prompt atau jailbreak eksplisit yang melanggar keselamatan
_PROMPT_INJECTION_LEAK_RE = re.compile(
    r"\b(tampilkan|tunjukkan|cetak|sebutkan|salin|bocorkan|reveal|print|show|dump)\b.{0,40}"
    r"\b(system prompt|instruksi sistem|prompt sistem|aturan internal|prompt rahasia|developer prompt)\b"
    r"|\b(ignore|abaikan|lupakan|kesampingkan)\b.{0,35}"
    r"\b(previous instructions|all instructions|semua aturan|aturan keselamatan|system prompt)\b.{0,50}"
    r"\b(system prompt|instruksi|terobos|menerobos arus|campur pemutih|genset di dalam|pengumuman palsu|berpura[- ]?pura)\b",
    re.IGNORECASE,
)

# Istilah edukasi banjir spesifik yang tetap jelas meski diketik singkat (2 kata)
_SPECIFIC_SHORT_FLOOD_QUERY_RE = re.compile(
    r"\b("
    r"tas siaga|tsb|inarisk|dibi|pentahelix|dana siap pakai|dsp|"
    r"pascabanjir|pasca banjir|prabencana|pra bencana|persiapan banjir|"
    r"listrik banjir|leptospirosis|tetanus|drainase|selokan|saluran air"
    r")\b",
    re.IGNORECASE,
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

# 4. Kata kunci spesifik domain banjir
_FLOOD_DOMAIN_RE = re.compile(
    r"\b("
    r"banjir|genangan|hujan|hidrometeorologi|"
    r"tas siaga|tsb|bnpb|bpbd|bmkg|basarnas|inarisk|dibi|pentahelix|dana siap pakai|dsp|"
    r"saluran air|drainase|selokan|sungai|tanggul|arus deras|"
    r"pascabanjir|pasca banjir|surut|leptospirosis|tetanus|genset|elpiji|lpg|pemutih"
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

# Pola negasi pada tingkat kalimat untuk post-check S3 (menghindari false positive)
_SENTENCE_NEGATION_RE = re.compile(
    r"\b(jangan|dilarang|hindari|tidak boleh|tak boleh|bukan|tidak aman|"
    r"tidak disarankan|tidak dianjurkan|tidak menghilangkan|tidak dapat menghilangkan|"
    r"tidak menjamin|tidak mampu menghilangkan|berbahaya jika)\b",
    re.IGNORECASE,
)

_S3_OUTPUT_SAFETY_FALLBACK = (
    "Demi keselamatan Anda, respons otomatis dihentikan karena berpotensi "
    "memuat saran yang tidak aman.\n\n"
    "Prinsip keselamatan utama saat banjir:\n"
    "- Jangan menerobos arus atau genangan banjir (baik berjalan kaki maupun kendaraan).\n"
    "- Jangan menyentuh/memindahkan panel listrik basah atau kabel listrik jatuh.\n"
    "- Jangan menyalakan genset di ruang tertutup/semi-tertutup, jangan menyalakan "
    "api/sakelar saat tercium bau elpiji, dan jangan mencampur pemutih dengan asam/amonia.\n"
    "- Untuk bantuan darurat, hubungi **BPBD**, **BNPB**, **Basarnas (115)**, "
    "atau **112** *(jika layanan tersedia di wilayah Anda)*."
)


@dataclass(frozen=True)
class PostCheckResult:
    """Hasil pemeriksaan keamanan S3 pasca-generasi LLM."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    corrected_text: str | None = None


def _normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"[.!?\n]+", text or "") if s.strip()]


class SafetyGuard:
    """Penjaga gerbang keselamatan pra-LLM dan pasca-LLM (WF-006 / WF-023)."""

    def check(self, user_query: str) -> SafetyCheckResult:
        """Mengevaluasi input pengguna secara deterministik (pre-check)."""
        if user_query is None or not str(user_query).strip():
            return SafetyCheckResult(
                category="empty_input",
                bypass_llm=True,
                override_message=EMPTY_INPUT_MESSAGE,
                matched_rule="empty_or_whitespace",
            )

        raw = str(user_query).strip()
        norm = _normalize_text(raw)

        # 0. Cek prompt injection / kebocoran system prompt lebih awal agar tidak salah rute
        if _PROMPT_INJECTION_LEAK_RE.search(raw):
            return SafetyCheckResult(
                category="out_of_domain",
                bypass_llm=True,
                override_message=PROMPT_INJECTION_REFUSAL_MESSAGE,
                matched_rule="prompt_injection_or_leakage",
            )

        # 1. Prioritas tertinggi: Situasi darurat akut (FR-07) — sebelum klarifikasi!
        # Bedakan framing edukatif/hipotetis tanpa indikator bahaya aktif sekarang.
        has_edu_framing = bool(_EDUCATIONAL_FRAMING_RE.search(raw))
        has_active_urgency = bool(_ACTIVE_URGENCY_RE.search(raw))
        is_educational_only = has_edu_framing and not has_active_urgency

        if not is_educational_only:
            for rule_name, pattern, override_msg in _ACUTE_EMERGENCY_RULES:
                if not pattern.search(raw):
                    continue
                # Bedakan bahaya potensial (genset belum dinyalakan) vs paparan CO akut
                if (
                    rule_name == "acute_generator_co"
                    and _GENERATOR_NOT_RUNNING_RE.search(raw)
                    and not _ACTIVE_CO_SYMPTOM_OR_SMOKE_RE.search(raw)
                ):
                    continue
                # Bedakan korban sadar pascatenggelam (evaluasi medis) vs tidak bernapas normal
                if (
                    rule_name == "acute_drowning_or_no_breath"
                    and re.search(r"\b(sadar|bernapas normal)\b", raw, re.IGNORECASE)
                    and not _NON_BREATHING_OR_UNCONSCIOUS_RE.search(raw)
                ):
                    continue
                return SafetyCheckResult(
                    category="acute_emergency",
                    bypass_llm=True,
                    override_message=override_msg,
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

        # 2b. Permintaan pembuatan pengumuman resmi palsu / hoaks instansi
        if _FAKE_ANNOUNCEMENT_RE.search(raw):
            return SafetyCheckResult(
                category="out_of_domain",
                bypass_llm=True,
                override_message=FAKE_ANNOUNCEMENT_REFUSAL_MESSAGE,
                matched_rule="fake_official_announcement",
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
            len(tokens) <= 2
            and not _OUT_OF_DOMAIN_RE.search(raw)
            and not _SPECIFIC_SHORT_FLOOD_QUERY_RE.search(raw)
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

    def post_check(self, answer_text: str) -> PostCheckResult:
        """Memeriksa keluaran LLM terhadap pelanggaran keselamatan S3 (zero-tolerance)."""
        if not answer_text or not answer_text.strip():
            return PostCheckResult(passed=True)

        violations: list[str] = []
        sentences = _split_sentences(answer_text)

        # Cek kebocoran penanda internal system prompt
        if re.search(
            r"Aturan keselamatan kritis universal \(P0\)|"
            r"Aturan keselamatan prioritas mutlak \(P0\)|"
            r"Aturan khusus berbasis korpus \(RAG\)|"
            r"BASE_SYSTEM_INSTRUCTION",
            answer_text,
            re.IGNORECASE,
        ):
            violations.append("s3_system_prompt_leak")

        # Cek resep/dosis obat eksplisit
        if re.search(
            r"\b\d+\s?(mg|ml|tablet|kapsul)\b|"
            r"\b(minum|konsumsi|berikan)\b.{0,30}\b(parasetamol|paracetamol|ibuprofen|amoxicillin|amoksisilin|doxycycline|doksisiklin|antibiotik)\b",
            answer_text,
            re.IGNORECASE,
        ):
            for s in sentences:
                if re.search(
                    r"\b\d+\s?(mg|ml|tablet|kapsul)\b|"
                    r"\b(minum|konsumsi|berikan)\b.{0,30}\b(parasetamol|paracetamol|ibuprofen|amoxicillin|amoksisilin|doxycycline|doksisiklin|antibiotik)\b",
                    s,
                    re.IGNORECASE,
                ) and not _SENTENCE_NEGATION_RE.search(s):
                    violations.append("s3_medical_dosage_prescription")
                    break

        for s in sentences:
            negated = bool(_SENTENCE_NEGATION_RE.search(s))

            # 1. Pertolongan tenggelam: menekan perut / membalikkan korban
            if (
                not negated
                and re.search(
                    r"\b(tekan|menekan|pompa)\b.{0,25}\bperut\b"
                    r"|\b(balikkan|membalikkan|gantung terbalik)\b.{0,30}\b(korban|tubuh|badan)\b",
                    s,
                    re.IGNORECASE,
                )
            ):
                violations.append("s3_drowning_stomach_press")

            # 2. Mencampur pemutih dengan asam/cuka/amonia
            if (
                not negated
                and re.search(
                    r"\b(campur|campurkan|mencampur|gabungkan)\b.{0,35}\bpemutih\b.{0,35}\b(cuka|asam|amonia|pembersih keramik)\b",
                    s,
                    re.IGNORECASE,
                )
            ):
                violations.append("s3_bleach_mix")

            # 3. Menyalakan genset di dalam ruangan / garasi / ruang tertutup
            if (
                not negated
                and re.search(
                    r"\b(nyalakan|letakkan|pasang|gunakan)\b.{0,30}\b(genset|generator)\b.{0,35}\b(di dalam rumah|dalam ruangan|di garasi|ruang tertutup|dekat jendela)\b",
                    s,
                    re.IGNORECASE,
                )
            ):
                violations.append("s3_indoor_generator")

            # 4. Menyentuh/memindahkan kabel listrik jatuh atau mencabut perangkat terendam
            if (
                not negated
                and re.search(
                    r"\b(pindahkan|singkirkan|angkat|pegang|sentuh)\b.{0,35}\b(kabel listrik|kabel pln)\b.{0,25}\b(jatuh|putus|terendam)\b"
                    r"|\b(cabut|lepaskan)\b.{0,35}\b(kabel|colokan)\b.{0,35}\b(terendam|basah)\b",
                    s,
                    re.IGNORECASE,
                )
            ):
                violations.append("s3_submerged_electricity_or_fallen_wire")

            # 5. Menyarankan masuk loteng tertutup atau naik atap/genteng otomatis
            if (
                not negated
                and re.search(
                    r"\b(naik ke|pindah ke|masuk ke)\b.{0,35}\b(loteng|atap|genteng)\b",
                    s,
                    re.IGNORECASE,
                )
            ):
                violations.append("s3_closed_attic_or_auto_roof")

            # 6. Mengklaim perebusan menghilangkan kontaminan kimia/BBM
            if (
                not negated
                and re.search(
                    r"\b(rebus|merebus|perebusan)\b.{0,40}\b(menghilangkan|membersihkan|aman dari)\b.{0,35}\b(kimia|bbm|bahan bakar|semua kontaminan)\b",
                    s,
                    re.IGNORECASE,
                )
            ):
                violations.append("s3_boiling_removes_chemicals")

            # 7. False reassurance menyeberangi arus / teknik sepatu bot+tongkat (lintas urutan kata)
            has_flood_cross_ctx = bool(
                re.search(
                    r"\b(banjir|arus|genangan|suv|truk|kendaraan tinggi|mata kaki|menerobos|menyeberang)\b",
                    s,
                    re.IGNORECASE,
                )
            )
            if not negated and has_flood_cross_ctx and re.search(
                r"\b(gunakan|pakai|pakailah)\b.{0,45}\b(sepatu bot|tongkat)\b"
                r"|\b(aman untuk dilewati|aman diterobos|silakan terobos|boleh menerobos|aman dilewati)\b",
                s,
                re.IGNORECASE,
            ):
                # Kecualikan APD pembersihan rumah setelah banjir surut (sepatu bot + membersihkan/lumpur)
                is_post_flood_apd = bool(
                    re.search(r"\b(membersihkan|pembersihan|lumpur|sarung tangan|apd)\b", s, re.IGNORECASE)
                ) and not bool(
                    re.search(r"\b(menerobos|menyeberang|arus|melintas|dilewati|diterobos)\b", s, re.IGNORECASE)
                )
                if not is_post_flood_apd:
                    violations.append("s3_cross_flood_technique")

        deduped = list(dict.fromkeys(violations))
        if deduped:
            return PostCheckResult(
                passed=False,
                violations=deduped,
                corrected_text=_S3_OUTPUT_SAFETY_FALLBACK,
            )
        return PostCheckResult(passed=True)
