# Baseline Safety Audit & Source Validation Report (v1.2 → v1.3) — SiagaBanjir

> **Tanggal Audit:** 28 November 2026<br>
> **Branch:** `syahir` (basis commit `b67f40a` + modifikasi lokal `app.py`)<br>
> **Target:** Hardening **Baseline Gemini tanpa RAG** (`prompt_v1.2` → `prompt_v1.3`), penguatan `SafetyGuard` (pre-check & post-check), serta *safety regression suite* 50 skenario (`EV-01`–`EV-50`) tanpa mengubah arsitektur eksperimen (`PRD.md` v0.3 & `ARCHITECTURE.md` v0.2).

---

## 1. Trace Alur End-to-End Aktual (Baseline vs RAG)

```text
Input Pengguna (app.py / scripts/run_eval.py)
  -> ChatRequest(mode="baseline"|"rag", run_context="demo"|"experiment", allow_fallback)
  -> ChatService.handle_request() [src/pipeline/chat_service.py]
       |-- Mode "rag":
       |     1. SafetyGuard.check(user_query) [pre-check deterministik]
       |     2. BM25CorpusRetriever.retrieve() + Evidence Gate
       |     3. build_rag_messages(..., prompt_version)
       |     4. LLMProviderAdapter.generate() [src/llm/client.py]
       |     5. SafetyGuard.post_check() [v1.3] + verify_and_extract_citations()
       |     6. StructuredJsonlLogger.log() [src/logging/eval_logger.py]
       |
       |-- Mode "baseline":
             - Kondisi v1.2 (sebelum hardening):
               LANGSUNG _handle_baseline() -> hanya cek empty_input ->
               build_baseline_messages() -> LLMProviderAdapter.generate() -> Logger.
               (Tidak ada SafetyGuard pre-check di demo, tidak ada post-check S3.)
             - Kondisi v1.3 (setelah hardening & paritas keselamatan eksperimen):
               * run_context="demo" & "experiment": SafetyGuard.check() (pre-check) +
                 build_baseline_messages() + LLMProviderAdapter.generate() +
                 SafetyGuard.post_check() (S3 guard) -> Logger (identik dengan RAG;
                 perbedaan eksperimen hanya retrieval context & perilaku sitasi,
                 sementara allow_fallback=False tetap dikunci pada experiment dan
                 masking PII tetap khusus demo).
```

---

## 2. Matriks Audit Celah (Terbukti vs Sudah Tertangani)

Seluruh temuan diverifikasi langsung terhadap kode aktual (`src/llm/prompts.py`, `src/safety/guard.py`, `src/pipeline/chat_service.py`, `src/config.py`, `src/llm/client.py`, `app.py`) serta log 20 pengujian Baseline (`logs/demo_20261127.jsonl` baris `#20`–`#39`).

### 2.1 Celah Terkonfirmasi (*Proven Gaps*)

| ID | Area | File & Baris/Fungsi | Kondisi Saat Ini (v1.2) | Risiko | Severity | Tindakan v1.3 |
|---|---|---|---|---|---|---|
| `GAP-01` | Baseline & Experiment Pre-Check & Post-Check | `src/pipeline/chat_service.py` (`_handle_baseline`, L321–L386 & RAG L295) | Mode `baseline` melewati `SafetyGuard` sepenuhnya dan mode `experiment` sempat melewati `post_check`. | Input darurat akut atau keluaran S3 berbahaya bisa lolos tanpa proteksi dan merusak paritas keselamatan Baseline vs RAG. | **P0 / S3** | Aktifkan `SafetyGuard.check()` dan `SafetyGuard.post_check()` secara identik pada `mode=baseline|rag` × `run_context=demo|experiment`; pembeda eksperimen hanya retrieval & sitasi. |
| `GAP-02` | Slang & Variasi Bahaya Akut Indonesia | `src/safety/guard.py` (`_ACUTE_EMERGENCY_RULES`, L80–L122; `check`, L238–L253) | Belum mendeteksi `bau elpiji`/`gas bocor`, `gak napas`/`tidak bernapas`, `kabel listrik jatuh`/`tiang roboh`, `terjebak plafon`/`loteng`/`kamar`, `asap genset`/`pusing CO`, serta `air sedada` tanpa kata `sudah/lagi` dan `kesetrum` tanpa subjek terbatas. | *False negative* pada kondisi mengancam nyawa; input pendek seperti `"air sedada"`, `"bau elpiji"`, atau `"gak napas"` jatuh ke `ambiguous` (*over-clarification*). | **P0 / S3** | Perluas deteksi berbasis konteks & variasi slang (bukan kata kunci tunggal) + pisahkan konteks edukatif/hipotetis/negasi agar tidak *false positive*. |
| `GAP-03` | Emergency Override Spesifik Bahaya (1–3 Aksi) | `src/safety/guard.py` (`EMERGENCY_OVERRIDE_MESSAGE`, L24–L41) & `prompts.py` (L59–L67) | Pesan darurat seragam untuk semua kondisi; belum memberi 1–3 tindakan penyelamatan spesifik sebelum klarifikasi untuk kebocoran LPG, korban tidak bernapas/tenggelam, kabel listrik jatuh/kesetrum, atau paparan asap genset (CO). | Pengguna pada bahaya gas/listrik/CO/tenggelam tidak langsung mendapat larangan kritis (mis. jangan tekan perut korban tenggelam, jangan nyalakan sakelar saat bau elpiji). | **P0 / S3** | Tambahkan pesan *Emergency Override* terarah per kategori bahaya akut (1–3 aksi inti + rujukan resmi) & tegaskan Mode Krisis di `prompt_v1.3`. |
| `GAP-04` | Anti-False-Reassurance (Kendaraan Tinggi & Orang Lain) | `src/llm/prompts.py` (`BASE_SYSTEM_INSTRUCTION`, aturan #4) | Sudah melarang teknik sepatu bot/tongkat & klaim air mata kaki aman, tetapi belum secara eksplisit menolak rasionalisasi *"kendaraan tinggi/SUV/truk"* atau *"orang lain juga lewat"*. | Pengguna tetap terdorong menerobos arus dengan SUV/motor/mengikuti warga lain. | **P0 / S3** | Pertegas di `prompt_v1.3` larangan menyetujui penyeberangan meski air dangkal, memakai kendaraan tinggi, atau orang lain melakukannya. |
| `GAP-05` | Syarat Kering Menyeluruh MCB & Kabel Jatuh | `src/llm/prompts.py` (aturan #5–#6) | Menyebut *"sakelar/MCB masih kering"*, belum menegaskan **tangan, lantai, DAN panel** harus seluruhnya kering serta belum menyebut **kabel listrik jatuh/putus**. | Pengguna menyentuh panel kering saat berdiri di lantai basah, atau memindahkan kabel jatuh sendiri. | **P0 / S3** | Perbarui aturan listrik di `prompt_v1.3`: MCB hanya bila tangan, lantai, dan panel kering; larang mendekati/menyentuh/memindahkan kabel listrik jatuh. |
| `GAP-06` | Genset & Risiko Karbon Monoksida (CO) | `src/llm/prompts.py` & `src/safety/guard.py` | Sama sekali belum tercakup. | Keracunan CO fatal akibat pemakaian genset di ruang tertutup, garasi, teras tertutup, atau dekat jendela/pintu/ventilasi. | **P0 / S3** | Tambahkan aturan larangan genset di ruang tertutup/semi-tertutup/dekat bukaan rumah di `prompt_v1.3`, deteksi darurat CO di `SafetyGuard`, dan *post-check* S3. |
| `GAP-07` | Kebocoran Gas / LPG di Luar Pembersihan | `src/llm/prompts.py` (aturan #8) & `src/safety/guard.py` | Baru disebut singkat pada konteks pembersihan rumah; belum mencakup istilah `elpiji`/`LPG`, larangan sumber percikan/sakelar secara umum, serta jalur darurat akut. | Ledakan/kebakaran saat pengguna menyalakan sakelar lampu atau kompor saat tercium bau elpiji. | **P0 / S3** | Pisahkan aturan LPG yang tegas di `prompt_v1.3` + deteksi darurat LPG di `SafetyGuard` + *post-check* S3. |
| `GAP-08` | Jebakan Loteng Tertutup Tanpa Akses Keluar | `src/llm/prompts.py` (aturan #7) & `src/safety/guard.py` | Melarang otomatis naik ke atap/genteng, belum secara eksplisit melarang masuk ke **loteng tertutup tanpa akses keluar**. | Korban terperangkap di plafon/loteng saat air terus naik. | **P0 / S3** | Tambahkan larangan masuk ke loteng tertutup tanpa akses keluar di `prompt_v1.3` dan `EMERGENCY_OVERRIDE_MESSAGE`. |
| `GAP-09` | Pertolongan Pertama Tenggelam | `src/llm/prompts.py` & `src/safety/guard.py` | Sama sekali belum tercakup. | Mitos menekan perut/membalikkan korban tenggelam menunda pertolongan medis dan memicu aspirasi. | **P0 / S3** | Tambahkan larangan menekan perut/membalikkan korban tenggelam & prioritas bantuan medis di `prompt_v1.3`, `SafetyGuard` (pre-check & post-check). |
| `GAP-10` | Larangan Pencampuran Pemutih + Asam/Amonia | `src/llm/prompts.py` & `src/safety/guard.py` | Sama sekali belum tercakup. | Gas klorin/kloramin beracun saat membersihkan rumah pascabanjir. | **P0 / S3** | Tambahkan larangan mencampur pemutih dengan asam/cuka/amonia di `prompt_v1.3` dan *post-check* S3. |
| `GAP-11` | Batas Medis (Diagnosis Pasti & Red Flags) | `src/llm/prompts.py` (aturan #8) | Sudah melarang dosis/terapi/obat generik, namun belum melarang **diagnosis pasti** maupun menegaskan kewaspadaan *red flags* medis umum. | Chatbot memberi diagnosis definitif atau melewatkan tanda bahaya (sesak napas, penurunan kesadaran, dehidrasi berat, kaku otot). | **P0 / S3** | Tegaskan larangan diagnosis pasti & resep/dosis; arahkan kenali *red flags* dan segera ke faskes di `prompt_v1.3` + *post-check*. |
| `GAP-12` | Larangan Mengarang Nomor Lokal / Jaminan Layanan | `src/llm/prompts.py` (aturan #7) | Menyebut `112` bersyarat wilayah, tetapi belum melarang eksplisit mengarang nomor telepon lokal atau menjamin layanan daerah selalu aktif. | Halusinasi nomor BPBD/PLN/puskesmas lokal yang tidak aktif atau salah. | **P0 / S2** | Tegaskan di `prompt_v1.3` agar tidak mengarang nomor lokal atau menjamin layanan daerah selalu aktif. |
| `GAP-13` | Kelompok Rentan, Risiko Pascabanjir, Hoaks & Abstention | `src/llm/prompts.py` (aturan #8–#10) | Belum menyebut eksplisit **ibu hamil**, **penyakit kronis**, risiko **tetanus/diare-dehidrasi/luka/jamur/hewan berbahaya**, *abstention* untuk **mengonfirmasi/membantah hoaks real-time tanpa sumber**, serta larangan mengklaim tahu dokumen/regulasi terbaru. | Informasi tidak lengkap bagi kelompok rentan atau overclaiming terhadap kabar viral/regulasi baru. | **P1 / S2** | Perkuat aturan ringkas P1 di `prompt_v1.3` (detail panjang disimpan di dokumen ini agar prompt tetap ramping). |
| `GAP-14` | Kebocoran System Prompt & Prompt Injection | `src/safety/guard.py` & `src/llm/prompts.py` | `SafetyGuard` belum menyaring permintaan ekstraksi *system prompt*/*jailbreak* eksplisit; `prompt_v1.2` belum melarang pengungkapan instruksi sistem secara eksplisit. | Kebocoran instruksi internal atau *override* aturan keselamatan. | **P0 / S3** | Tambahkan deteksi *prompt leakage / unsafe jailbreak* di `SafetyGuard` (pre-check & post-check) dan larangan di `prompt_v1.3`. |
| `GAP-15` | Pelestarian Versi Prompt (`prompt_v1.2` vs `prompt_v1.3`) | `src/llm/prompts.py` (L14–L160) | Hanya menyimpan satu string `BASE_SYSTEM_INSTRUCTION`; parameter `prompt_version` pada `build_baseline_messages()`/`build_rag_messages()` sebelumnya diabaikan (`_ = prompt_version`). | Tidak dapat mereproduksi `prompt_v1.2` secara akurat untuk pembanding historis. | **P2 / Maintainability** | Tambahkan `PROMPT_REGISTRY` yang mempertahankan `prompt_v1.2` utuh dan menetapkan `prompt_v1.3` sebagai default. |

### 2.2 Komponen yang Sudah Terverifikasi Baik (*No-Gap / Tidak Perlu Refactor*)

| Area | File & Bukti | Status |
|---|---|---|
| Pemisahan error `config_error` / `auth_error` / `rate_limit` / `timeout` / `network_error` / `provider_error` / `index_error` | `src/llm/client.py`, `src/pipeline/chat_service.py` (L64–L106), teruji di `tests/test_app_multazam_integration.py` | **Terkonfirmasi baik** — tidak diubah. |
| Larangan *silent fallback* saat eksperimen (`allow_fallback=False`) | `src/schemas.py` (`ChatRequest.__post_init__`), `src/logging/eval_logger.py` (`validate_experiment_logs`) | **Terkonfirmasi baik** — tidak diubah. |
| Sanitasi kredensial `.env`, masking PII demo, zero citation di Baseline | `src/config.py`, `src/logging/eval_logger.py`, `tests/test_config_and_security.py` | **Terkonfirmasi baik** — tidak diubah. |
| Pembedaan risiko mikrobiologis vs kimia pada perebusan air minum | `src/llm/prompts.py` (`prompt_v1.2` aturan #8) | **Sudah ada di v1.2** — dipertahankan & dilengkapi *post-check* S3 di v1.3. |
| Konfigurasi Gemini & parameter decoding (`temperature=0.1`, `max_tokens=1400`, `timeout_sec=30`) | `src/config.py`, `src/llm/client.py` | **Terkonfirmasi baik** — tidak diubah (hanya default `prompt_version` dinaikkan ke `prompt_v1.3`). |

---

## 3. Validasi Sumber & Daftar Klaim `NEEDS_VERIFICATION` (Phase 2)

### 3.1 Prinsip Keselamatan Terverifikasi yang Diadopsi ke `prompt_v1.3` & `SafetyGuard`
- **Penyeberangan banjir & kendaraan** (BNPB, FEMA *Turn Around Don't Drown*, CDC): Tidak ada kedalaman air banjir mengalir yang dijamin aman untuk pejalan kaki maupun kendaraan tinggi; hindari arus dan cari jalur kering/bantuan petugas.
- **Kelistrikan & kabel jatuh** (PLN, CDC, FEMA): Mematikan MCB hanya dilakukan bila tangan, lantai, dan panel seluruhnya kering; jauhi kabel listrik jatuh/putus dan jangan pernah menyentuh atau memindahkannya; pemulihan pascabanjir wajib diperiksa teknisi kompeten/PLN.
- **Genset & CO** (CDC, FEMA, WHO): Karbon monoksida tidak berbau/berwarna; jangan menyalakan genset di dalam ruangan, garasi, ruangan semi-tertutup, atau dekat pintu/jendela/ventilasi rumah.
- **Kebocoran LPG** (BNPB, IFRC, praktik keselamatan gas umum): Jangan menyalakan api, korek, sumber percikan, atau mengoperasikan sakelar listrik; segera keluar ke udara terbuka dan lapor petugas.
- **Terjebak banjir & loteng tertutup** (FEMA, IFRC): Jangan masuk ke loteng tertutup tanpa akses keluar; pertahankan posisi tinggi yang aman, beri tanda keberadaan bila aman, lapor alamat & jumlah orang, jangan masuk air, jangan otomatis naik ke atap/genteng.
- **Pertolongan pertama tenggelam** (WHO, IFRC): Jangan menekan perut atau membalikkan korban untuk mengeluarkan air; segera panggil bantuan medis darurat dan lakukan penyelamatan hanya bila aman bagi penolong.
- **Pembersihan rumah** (CDC, WHO): Gunakan APD (sepatu bot karet, sarung tangan, masker); jangan mencampur pemutih klorin dengan asam (mis. cuka/pembersih keramik) atau amonia karena menghasilkan gas beracun.
- **Air minum pascabanjir** (WHO, CDC, Kemenkes): Perebusan membantu mengurangi patogen mikrobiologis tetapi tidak menghilangkan kontaminan kimia/BBM; bila tercemar gunakan air kemasan/sumber aman & ikuti arahan otoritas.
- **Pascabanjir medis & kelompok rentan** (Kemenkes, WHO, CDC): Waspadai leptospirosis (demam + nyeri betis), tetanus/infeksi luka, diare/dehidrasi, jamur, hewan berbahaya; prioritaskan bayi, ibu hamil, lansia, disabilitas, dan penderita penyakit kronis; kenali *red flags* dan rujuk faskes tanpa diagnosis pasti atau resep/dosis obat.
- **Keamanan LLM** (OWASP LLM Top 10, NIST AI RMF): Tahan terhadap *prompt injection*, *jailbreak*, dan ekstraksi *system prompt*.

### 3.2 Daftar Klaim yang Ditandai `NEEDS_VERIFICATION` (Tidak Di-hardcode ke Prompt/Kode)

| No | Klaim / Parameter | Status | Alasan & Penanganan Aman di v1.3 |
|---|---|---|---|
| 1 | Cakupan aktif nomor darurat `112` dan `PSC 119` di setiap kabupaten/kota Indonesia | `NEEDS_VERIFICATION` | Tidak semua daerah memiliki layanan `112`/`119` aktif 24 jam. Di prompt & `SafetyGuard`, `112` wajib disertai kualifikasi *(jika layanan tersedia di wilayah Anda)* dan tidak menjamin aktif di semua daerah. |
| 2 | Nomor kontak spesifik BPBD daerah, puskesmas lokal, atau nomor call center utilitas lokal selain kanal resmi nasional umum | `NEEDS_VERIFICATION` | Berbeda per daerah dan dapat berubah; sistem dilarang mengarang nomor lokal atau URL deep-link. |
| 3 | Jarak aman numerik spesifik penempatan genset di luar rumah (mis. "20 kaki / 6 meter" dari panduan FEMA/CDC AS) | `NEEDS_VERIFICATION` | Angka standar AS belum tentu relevan secara spasial untuk permukiman padat Indonesia; prompt menggunakan prinsip aman universal (*"di luar ruangan terbuka, jauh dari pintu, jendela, dan ventilasi"*). |
| 4 | Ambang kedalaman air numerik spesifik untuk pejalan kaki/kendaraan (mis. "15 cm / 30 cm / 60 cm" dari NOAA/FEMA) | `NEEDS_VERIFICATION` | Berisiko disalahartikan bahwa kedalaman di bawah angka tersebut aman; prompt menegaskan tidak ada ketinggian air yang dijamin aman. |
| 5 | Rasio konsentrasi larutan pemutih/disinfektan atau prosedur RJP/CPR langkah rinci medis | `NEEDS_VERIFICATION` | Prosedur teknis/klinis rinci tidak boleh diimprovisasi chatbot edukasi non-klinis tanpa panduan resmi terkurasi di korpus; diarahkan ke tenaga medis/otoritas kesehatan. |
| 6 | Regulasi terbaru BNPB/BPBD/BMKG pasca-dokumen yang ada atau statistik kejadian banjir wilayah tertentu | `NEEDS_VERIFICATION` | Baseline tidak memiliki akses korpus maupun internet *real-time*; wajib *abstention* dan merujuk kanal resmi BNPB/BPBD/BMKG. |
| 7 | Teks verbatim 50 kasus evaluasi asli dari laporan riset eksternal | `NEEDS_VERIFICATION` | Dokumen laporan riset eksternal tidak tersedia di repositori ini; suite 50 kasus (`EV-01`–`EV-50`) disusun secara transparan sebagai **kasus turunan** yang mencakup seluruh 8 kategori dan ketentuan rubric pada spesifikasi tugas. |

---

## 4. Final Baseline v1.3 Freeze & Model Adequacy Verdict *(28 November 2026)*

### 4.1 Keputusan Baseline & Status Freeze
- **Baseline Verdict:** **`LAYAK BERSYARAT` — FREEZE Baseline v1.3** (`prompt_v1.3` + `SafetyGuard` pre-check & post-check paritas 2×2).
- **Alasan & Bukti:**
  - Seluruh aturan keselamatan P0/P1/P2 dan kalibrasi kontekstual (genset belum dinyalakan vs sedang menyala/gejala CO, korban tenggelam sadar batuk/lemas vs tidak bernapas normal, rujukan medis vs SAR/evakuasi, prediksi real-time lintas urutan kata) telah lulus uji deterministik: `37/37` unit test lulus, `50/50` EV-50 offline (`S3=29/29 zero_tolerance=True`, `FP=0`, `FN=0`), dan `AppTest` lulus.
  - Paritas eksperimen 2×2 (`mode=baseline|rag` × `run_context=demo|experiment`) terverifikasi: kedua mode berbagi `SafetyGuard` dan `BASE_SYSTEM_INSTRUCTION` (`prompt_v1.3`) identik; pembeda eksperimen murni hanya *retrieval context* dan perilaku sitasi; `allow_fallback=False` tetap terkunci pada eksperimen.
  - Uji live Baseline (`logs/demo_20261127.jsonl` baris `#48`–`#60` pada `prompt_v1.2` [13/13 sukses] dan `#73`–`#77` pada `prompt_v1.3` [3/3 LLM sukses + 2 bypass yang telah dikalibrasi ulang & diuji regresi], serta `demo_safety_v12_live.jsonl`) membuktikan respons Bahasa Indonesia natural, terstruktur, patuh batas keselamatan, 0 sitasi buatan, dan latensi `1.45s–4.69s`.
- **Tidak perlu optimasi tambahan pada Baseline:** Baseline adalah kontrol eksperimen akademik; fokus berikutnya adalah korpus RAG (`WF-018` Ramadan), *corpus freeze* (`M5`), QA lintas perangkat (`WF-026`), dan evaluasi 30 soal (`M7`–`M8`).

### 4.2 Keputusan Kelayakan Model Utama (`OD-02` — `gemini-3.5-flash-lite`)
- **Model Verdict:** **`LAYAK BERSYARAT`** (direkomendasikan untuk dikunci pada `OD-02` bersama Ramadan; fallback demo: Groq `openai/gpt-oss-20b`).
- **Kelemahan & Keterbatasan yang Wajib Didokumentasikan:**
  1. **Fixed Sampling Defaults:** `langchain-google-genai` mengeluarkan `UserWarning` bahwa `gemini-3.5-flash-lite` mengabaikan parameter `temperature` (`temperature=0.1` tidak aktif di sisi provider), sedangkan `max_output_tokens=1400` dan `timeout=30` diterapkan. Keterbatasan ini tetap adil untuk eksperimen karena Kondisi A (Baseline) dan Kondisi B (RAG) memakai model dan konfigurasi identik.
  2. **Cakupan Uji Live `prompt_v1.3`:** Bukti live LLM pada `prompt_v1.3` baru mencakup 3 pertanyaan generatif + 14 live `prompt_v1.2`; 50 kasus EV-01..EV-50 baru dijalankan pada mode **offline deterministik** (0 panggilan API berbiaya) dan tidak boleh diklaim sebagai bukti generatif live 50 kasus.
  3. **Diksi minor generatif:** Model sesekali menghasilkan ketidaksempurnaan diksi minor (mis. `"kerontokan kesadaran"` pada Log #58, `"kebencangan"` pada Log #77 — kini Log #77 juga tertangkap deterministik oleh `SafetyGuard` `prediction_request`).
  4. **Status `OD-02` belum final:** Tetap menunggu persetujuan resmi Ramadan pada `WF-017` sebelum eksperimen resmi 30 soal (`WF-030`–`WF-031`).

### 4.3 Risiko Tersisa
1. Korpus RAG nyata (`data/processed/chunks.jsonl` & `corpus_manifest.json`) belum tersedia menunggu handoff `WF-018` Ramadan.
2. Evaluasi kualitas generatif penuh tetap wajib melalui penilaian independen 2 anggota pada 30 pertanyaan uji (`M7`–`M8`), bukan mengandalkan *post-check* deterministik semata.
3. Ketersediaan nomor darurat regional (`112`/`119`/BPBD lokal) tetap berstatus `NEEDS_VERIFICATION` dan tidak pernah dijamin aktif di semua daerah.
