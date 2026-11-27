# Context Recovery Snapshot — SiagaBanjir

> **Status Dokumen:** Draft v0.8 *(Track Syahir Siap Cross-Review: Keamanan `.env` Terverifikasi, 22/22 Test Lulus, Live API & E2E Baseline Teruji — Menunggu Ramadan & `OD-02`)*  
> **Terakhir Diperbarui:** 27 November 2026  
> **Referensi Utama:** [PRD.md](./PRD.md) (v0.3) | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (v0.6) | [TODO.md](./TODO.md) (v0.9) | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) (v0.2) | [ARCHITECTURE.md](./ARCHITECTURE.md) (v0.2)  
> **Repository GitHub:** [Syahirmr/SiagaBanjir](https://github.com/Syahirmr/SiagaBanjir)

> **Aturan Pemeliharaan:** Wajib perbarui file ini setiap kali terjadi perubahan keputusan penting, penutupan *Open Decision* (`OD-01`–`OD-05`), perubahan status milestone (`M0`–`M9`, `M-OPT`), atau perubahan blocker utama.

---

## 1. Aturan Wajib untuk AI / Agent *(Cold-Start Protocol)*

Sebelum melakukan pekerjaan apa pun pada sesi baru, AI/agent **wajib**:
1. Membaca secara berurutan: `docs/context_windows.md` (file ini) → [PRD.md](./PRD.md) → [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) → [TODO.md](./TODO.md) → [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) → [ARCHITECTURE.md](./ARCHITECTURE.md).
2. Memperlakukan [PRD.md](./PRD.md) v0.3 sebagai *Source of Truth* kebutuhan dan ruang lingkup.
3. **Dilarang mengarang status** (`Completed` hanya sah jika bukti artefak aktual terverifikasi) dan **dilarang mengklaim persetujuan anggota manusia** (Syahir atau Ramadan) apabila belum dicatat langsung.
4. **Dilarang mengubah ruang lingkup PRD**, jumlah/komposisi 30 pertanyaan uji, atau keputusan keselamatan tanpa persetujuan kedua anggota dan pembaruan `PRD.md`.
5. **Dilarang mengunci nama model LLM spesifik** sebelum tes API aktual (`WF-016`/`WF-017`), dan **dilarang mengklaim data sudah tervalidasi final** sebelum *cross-review* dan `M3`.
6. **Dilarang menjalankan perintah Git destruktif**, memodifikasi `data/raw/`, atau membocorkan isi `.env`/API key.

---

## 2. Identitas, Tujuan, Positioning & Batasan Proyek

- **Proyek:** SiagaBanjir — Big Project mata kuliah Sains Data (*LLM-Based AI Chatbot Development*).
- **Domain:** Mitigasi Bencana — Edukasi Kesiapsiagaan Banjir (**sudah disetujui dosen**; berbeda dari kelompok lain).
- **Tim:** **2 mahasiswa** (memenuhi ketentuan dosen 2–3 mahasiswa): **Member A (Syahir)** dan **Member B (Ramadan)**.
- **Target Pengguna Utama:** Masyarakat umum non-ahli di Indonesia (cakupan edukasi umum Indonesia; klaim wilayah tertentu wajib didukung sumber teraudit).
- **Positioning vs AI Generatif Umum:** Tidak diklaim lebih pintar/lebih lengkap dari AI umum. Lima pembeda terukur: (1) korpus resmi terkurasi, (2) keterlacakan sitasi sumber, (3) domain khusus kesiapsiagaan banjir, (4) *abstention* eksplisit saat bukti kurang, dan (5) *safety boundary* kebencanaan.
- **Batasan Keselamatan Mutlak:** Prototipe akademik edukatif, **bukan layanan darurat, bukan sistem peringatan dini resmi, dan tidak boleh menjadi pengganti petugas atau otoritas resmi** (BPBD, BNPB, BMKG, Basarnas, 112).

---

## 3. Scope MVP vs Fitur Opsional vs Out of Scope

- **MVP Wajib (`Must` — `FR-01` s.d. `FR-11`):**
  - Antarmuka chat **Streamlit lokal** dengan *disclaimer* keselamatan & info versi korpus (`FR-01`, `FR-10`).
  - Integrasi nyata dengan API LLM (**Gemini API utama**, **Groq API cadangan**) menggunakan **RAG sebagai pendekatan utama** dan **LangChain selektif** (`FR-02`, `FR-03`).
  - Edukasi 3 fase banjir (sebelum, saat, setelah) berbasis korpus resmi berversi yang telah di-*freeze* disertai sitasi terlacak (`FR-04`, `FR-06`).
  - Kontrol keselamatan: *abstention* untuk *out-of-scope*/klaim wilayah tanpa sumber (`FR-05`), **respons khusus situasi darurat akut** & penolakan prediksi (`FR-07`), klarifikasi pertanyaan ambigu (`FR-08`), dan *error handling* + *fallback* Groq (`FR-09`).
  - *Logging* *reproducibility*: `provider`, `model_id`, `corpus_version`, `source_dates`, konteks terambil, jawaban, sitasi, status API, latensi (`FR-11`).
  - Evaluasi komparatif **Baseline LLM tanpa *retrieval* vs SiagaBanjir RAG** pada **30 pertanyaan uji** (`10` faktual, `10` prosedural, `5` *out-of-scope*, `5` ambigu) + kasus uji darurat terpisah, *ground truth* bersama, **penilaian independen 2 anggota**, rekonsiliasi, dan *error analysis*.
  - Luaran wajib dosen: Prototipe siap demo, dokumentasi lengkap, dan **Poster Ilmiah** (5 komponen wajib berbasis hasil evaluasi aktual, bukan promosi fitur).
- **Fitur Opsional / Bersyarat (Tidak Boleh Mengorbankan MVP atau Evaluasi):**
  - `FR-12` (`Should`, `M-OPT`): **Statistik BNPB deterministik** — hanya boleh masuk demonstrasi jika `M6` stabil, audit fisik membuktikan kelayakan, dan tidak mengganggu `M7`–`M9`.
  - `FR-13` (`Could`, `WF-OPT-04`): Konteks percakapan *multi-turn* — di luar jalur kritis.
- **Out of Scope:** *Agent* kompleks, *live web search* (DuckDuckGo, dll.), OCR skala besar atas PDF *scan* rusak, prediksi/peringatan dini operasional, pelacakan GPS, autentikasi/deployment produksi.

---

## 4. Stack & Keputusan Teknis yang Disepakati

| Komponen | Keputusan | Status |
|---|---|---|
| Bahasa & UI Demo | Python + **Streamlit lokal** | Final |
| Provider LLM | **Gemini API** (utama) & **Groq API** (cadangan) | Final *(model spesifik: `OD-02`)* |
| Pendekatan & Orkestrasi | **RAG utama** + **LangChain selektif** (tanpa *agent* kompleks) | Final |
| Tata Kelola Korpus | *Physical audit* wajib + ***corpus versioning* & *corpus freeze*** sebelum evaluasi | Final |
| Evaluasi | 30 soal (10+10+5+5) + uji darurat; Baseline vs RAG pada model/parameter identik; skor independen 2 anggota | Final *(rubrik detail: `OD-05`)* |
| Statistik Tabular | Pandas & openpyxl secara deterministik (bukan tebakan LLM) | Bersyarat (`FR-12`) |

---

## 5. Struktur Dokumen & Folder Penting

- **Dokumen `docs/`:**
  - Tersedia: [PRD.md](./PRD.md) (v0.3), [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (v0.6 — memuat aturan operasional *handoff*/eksekusi Bag. `G.4`), [TODO.md](./TODO.md) (v0.9 — memuat *Execution Readiness & Dependency Map* 42 Work ID di Bag. 6 & status track Syahir), [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) (v0.2 — artefak audit awal siap review Ramadan), [ARCHITECTURE.md](./ARCHITECTURE.md) (v0.2 — draf revisi `WF-004` & `WF-006` oleh Syahir, siap review Ramadan), [context_windows.md](./context_windows.md) (v0.8), `pert14/` (`tugas pertemuan 14.docx` terisi & `JAWABAN_PERTEMUAN14_SIAGABANJIR.md`), serta referensi `BIG PROJECT.jpeg`.
  - *Planned Document* (belum dibuat): `EVALUATION_PLAN.md` (`M7`).
- **Folder & File Root:**
  - `data/raw/` — sudah ada (**8 berkas mentah: 2 edukasi + 6 Excel BNPB**); **read-only, tidak boleh ditimpa**.
  - `data/processed/` — **belum ada** (`chunks.jsonl` & `corpus_manifest.json` belum tersedia; menunggu `WF-012`–`WF-018` PIC Ramadan sehingga mode **RAG belum dapat berjalan pada korpus nyata**).
  - `.gitignore` — aktif; mengabaikan `.env`, `.env.*`, `.streamlit/secrets.toml`, `venv/`, cache Python, dan `logs/demo_*.jsonl`; melacak `.env.example` (`!.env.example`).
  - `.env.example`, `requirements.txt`, `app.py` (diadaptasi langsung dari starter Multazam `multazam_chatbot.py` memakai `st.session_state["chat_history"]`, `SystemMessage`/`HumanMessage`/`AIMessage`, `st.chat_input`, `st.chat_message`, `ChatService`, pemilih mode RAG/Baseline), `src/` (`config.py`, `schemas.py`, `safety/guard.py`, `retrieval/retriever.py`, `llm/prompts.py`, `llm/client.py`, `logging/eval_logger.py`, `pipeline/chat_service.py`), `scripts/` (`test_api.py`, `run_eval.py --mode both|baseline|rag`), `tests/` (4 suite, **22 total test**).
  - `audit_data.py` (*read-only*, aman), `prep_step1.py` (**jangan dijalankan** karena menimpa `data/raw/`), `venv/` (Python `3.14.0`; seluruh paket `requirements.txt` sudah terpasang: `streamlit`, `langchain_core`, `langchain_google_genai`, `langchain_groq`, `requests`, `python-dotenv`, `pymupdf`).

---

## 6. Pembagian Peran FINAL & Strategi Git

- **Member A (Syahir) — LLM & Application Engineering** *(Branch: `syahir` | 13 tugas solo)*: `WF-004` (`ARCHITECTURE.md`), `WF-006` (protokol *safety*/log), `WF-015`–`WF-017` (setup `.env.example`, tes Gemini & Groq API, pemilihan model `OD-02`), `WF-019`–`WF-020` (*pipeline* RAG & jalur *Baseline*), `WF-022`–`WF-025` (UI Streamlit lokal, protokol darurat, *error handling*, *logger*), serta `WF-030`–`WF-031` (eksekusi eksperimen Baseline vs RAG). *(Opsional: `WF-OPT-02`, `WF-OPT-04`.)*
- **Member B (Ramadan) — Data & Knowledge Preparation** *(Branch: `ramadan` | 11 tugas solo)*: `WF-005` (kontrak metadata), `WF-007`–`WF-014` (pengumpulan/verifikasi sumber, *physical audit* meninjau draf awal `DATA_DICTIONARY.md`, ekstraksi & pembersihan, *spot-check*, finalisasi `DATA_DICTIONARY.md` / `OD-03`), `WF-018` (*chunking* & `corpus_manifest` dengan koordinasi integrasi bersama Syahir), serta `WF-026` (QA independen lintas perangkat atas MVP Syahir). *(Opsional: `WF-OPT-01`, `WF-OPT-03`.)*
- **Tanggung Jawab Bersama (14 tugas):** `WF-001`–`WF-003` (fondasi M0), `WF-021` (verifikasi *retrieval* & *corpus freeze*), `WF-027`–`WF-029` (30 soal, *ground truth* & rubrik), `WF-032`–`WF-034` (penilaian independen, rekonsiliasi, *error analysis*), `WF-035`–`WF-038` (dokumentasi final, Poster Ilmiah, gladi demo, audit kelulusan).
- **Aturan Git Inti:** Remote `https://github.com/Syahirmr/SiagaBanjir.git`; branch `master` (*stable*), `syahir`, `ramadan` (*lowercase*). Dilarang *commit* langsung ke `master`; kerja & *push* hanya ke branch pribadi; sinkronisasi dari `master` sebelum/sesudah kerja; prefix *commit* `docs:`/`feat:`/`fix:`/`data:`/`test:`/`chore:`; merge ke `master` wajib lewat Pull Request & review partner; dilarang *force push*/*destructive reset*.

---

## 7. Status Terakhir Milestone, Work ID, Implementasi & Blocker *(per 27 Nov 2026)*

- **Git & Branch:** Terpublikasi di [Syahirmr/SiagaBanjir](https://github.com/Syahirmr/SiagaBanjir) dengan `master`, `syahir`, dan `ramadan` pada commit fondasi `c870f71`. Perubahan lokal di branch **`syahir`** mencakup `M .gitignore`, `M docs/TEAM_WORKFLOW.md`, `M docs/TODO.md`, `M docs/context_windows.md`, serta untracked `.env.example`, `app.py`, `requirements.txt`, `docs/ARCHITECTURE.md`, `docs/pert14/`, `scripts/`, `src/`, `tests/` *(belum di-commit/push)*.
- **Milestone:** `M0`–`M6` = **`In Progress`** *(M4–M6 baru tahap implementasi modul independen Syahir; belum lulus Exit Gate)*; `M7`–`M9` & `M-OPT` = **`Not Started`**.
- **Work ID (42 total):**
  - *Progress Status:* `20` `In Progress` (`WF-001`–`WF-011`, plus 9 item track Syahir: `WF-015`–`WF-017`, `WF-019`–`WF-020`, `WF-022`–`WF-025`), `22` `Not Started`, `0` `Blocked`, `0` `Completed`.
  - *Execution Readiness (`TODO.md` Bag. 6):* `3` `Joint-Gate` (`WF-001`–`003`), `8` `Ready-Coordination`, `31` `Blocked` (menunggu `M0`/`M1` Exit Gate, penguncian `OD-02`, & handoff Ramadan).
- **Hasil Uji Suite & Audit Aktual (`27 Nov 2026`):**
  - `compileall` (`app.py`, `src/`, `scripts/`, `tests/`): **lulus**.
  - `unittest` (4 suite di `tests/`): **22/22 lulus (`0.097s`)** setelah `.env` lokal aktif dan `.env.example` kembali menjadi placeholder bersih.
- **Hasil Uji Live API via `.env` Lokal & Rekomendasi `OD-02` (`WF-016`–`WF-017` — `27 Nov 2026`, 0 kredensial tertulis; `OD-02` belum dikunci):**
  - **Batch & Verifikasi `.env`:** Gemini `gemini-3.5-flash-lite` = **3/3 sukses** (`2.51s–7.26s`, Bahasa Indonesia natural & patuh disclaimer; *catatan:* LangChain memperingatkan model memakai *fixed sampling defaults* sehingga `temperature` diabaikan); `gemini-3.8-flash` = `503 UNAVAILABLE`; `gemini-2.5-*` = `404 NOT_FOUND`. Groq `openai/gpt-oss-20b` = **3/3 sukses** (`1.52s–2.06s`); `qwen/qwen3.8-27b` = **2/2 sukses** (`1.43s–2.13s`); `llama-3.*` = `404 model_not_found`.
  - **Uji Live E2E Baseline (`ChatService`, Gemini `gemini-3.5-flash-lite`, `allow_fallback=False`, `prompt_version="prompt_v1.0"`):** lulus (`outcome=answered_baseline`, `latency=1.792s`, `1.215` char Bahasa Indonesia, log JSONL 27 field pada `logs/demo_baseline_e2e.jsonl` terabaikan `.gitignore`, `secret_leaked=False`).
  - **Rekomendasi Usulan `OD-02` (Menunggu Persetujuan Ramadan):** Primary = `gemini-3.5-flash-lite` (dengan dokumentasi transparan *fixed sampling defaults*) & Fallback demo = `openai/gpt-oss-20b`. Eksperimen Baseline vs RAG tetap wajib model/parameter identik dan `allow_fallback=False`.
- **Verifikasi Streamlit Lokal (`WF-022` — `27 Nov 2026`):**
  - `streamlit==1.67.0`, `langchain-core==1.8.5`, `langchain-google-genai==4.5.3`, `langchain-groq==1.2.1`, `requests==2.34.2`, `python-dotenv==1.2.4`, `pymupdf==2.1` terpasang di `venv`.
  - `streamlit.testing.v1.AppTest` pada `app.py` lulus tanpa exception (judul `SiagaBanjir`, *disclaimer* permanen tampil, status korpus jujur *"Belum tersedia"*, bypass darurat `112`/`115` tanpa API call, dan mode `baseline` berjalan tanpa korpus); server lokal `python -m streamlit run app.py` merespons **`HTTP 200: ok`** pada `/_stcore/health`.
- **Implementasi Independen Syahir (`27 Nov 2026` — Basis Starter Multazam + `venv` Python 3.14):**
  - `.env.example`, `requirements.txt`, `src/config.py`, `src/schemas.py` (`WF-015`): pemuat `.env` aman, `__repr__`/`safe_summary` bebas kredensial, `sanitize_secret_text()`, serta blokir keras `allow_fallback=True` pada `run_context="experiment"`.
  - `src/safety/guard.py` (`WF-023`): deteksi deterministik `empty_input`, `acute_emergency` (112 bersyarat wilayah / Basarnas 115 / BPBD / BNPB), `prediction_request` (BMKG/BPBD), `ambiguous`, & `out_of_domain` + 6/6 suite uji FP/FN lulus (termasuk nol false positive pada pertanyaan edukatif saat banjir).
  - `src/retrieval/retriever.py`, `src/llm/prompts.py`, `src/llm/client.py`, `src/pipeline/chat_service.py` (`WF-019`, `WF-020`, `WF-024`): BM25 *retriever* read-only (`corpus_manifest.json` + `chunks.jsonl`) dengan *Evidence Gate*, paritas instruksi dasar Baseline–RAG + `<retrieved_context>`, `LLMProviderAdapter` (LangChain selektif / HTTP `requests`, kontrol `allow_fallback` ketat), verifikasi sitasi deterministik (`retrieved_sources` vs `citations_returned` + deteksi anomali `[SUMBER k]`), serta pemisahan `api_error` vs `retrieval_error` vs `abstention_insufficient_evidence`.
  - `src/logging/eval_logger.py` (`WF-025`): JSONL logger + masking PII demo + `validate_experiment_logs()` untuk cek paritas pra-`WF-032`.
  - `app.py` (`WF-022` — diadaptasi langsung dari starter Multazam), `scripts/test_api.py` (`WF-016`), `scripts/run_eval.py` (`WF-030`–`WF-031`, mendukung `--mode both|baseline|rag`): seluruh dependensi (`streamlit`, `langchain-core`, `langchain-google-genai`, `langchain-groq`, `python-dotenv`, `requests`, `pymupdf`) kini **terpasang** di `venv`; mode Baseline dapat dijalankan tanpa korpus, sedangkan mode RAG jujur menampilkan status korpus *belum tersedia* hingga handoff `WF-018` dari Ramadan.
- **Progres Teknis Terbaru (`ARCHITECTURE.md` v0.2 — `WF-004` & `WF-006`):**
  - Arsitektur RAG + LangChain selektif (tanpa *agent* kompleks), diagram komponen Mermaid, alur end-to-end Mode Baseline vs Mode RAG dengan paritas instruksi dasar + pelacakan `prompt_version`, pemetaan `FR-01`–`FR-11`, struktur kode (`src/`, `app.py`, `scripts/` — sudah diimplementasikan modular), dan kontrak I/O komponen (kontrak metadata/*chunk* `WF-005` tetap menunggu persetujuan final Ramadan).
  - **Safety Protocol (`WF-006`):** *bypass* prioritas keselamatan untuk darurat akut (`112` bergantung ketersediaan wilayah / Basarnas `115` / BPBD / BNPB — diverifikasi per Nov 2026), penolakan prediksi real-time (BMKG/BPBD), klarifikasi ambigu, *Evidence Gate* dua lapis (*abstention* saat bukti kurang), penolakan *out-of-domain*, pembedaan `retrieved_sources` vs `citations_returned` + batas verifikasi format metadata, isolasi `<retrieved_context>` sebagai mitigasi berlapis (bukan jaminan absolut), serta kewajiban uji FP/FN `Safety Guard` pada `WF-023`.
  - **Logging & Experiment Control (`WF-006`):** skema JSONL lengkap (contoh pada dokumen ditandai **data sintetis** bertanggal `2026-11-24`, termasuk `prompt_version`, `provider_actual`, `model_actual`, `parameters`, `corpus_version`, `retrieved_sources`, `citations_returned`, `outcome_type`, `latency_sec`), sanitasi privasi tanpa API key/kredensial, larangan *silent fallback* (`allow_fallback=False`) saat eksperimen, serta pemisahan tegas `api_error` vs `retrieval_error` vs `abstention_insufficient_evidence`.
  - **Keputusan Teknis Terbuka Baru:** `TD-01` (model spesifik Gemini/Groq & parameter — `OD-02`), `TD-02` (*retriever* FAISS vs BM25 vs *hybrid*), `TD-03` (ukuran *chunk*/`top-k`/ambang *Evidence Gate*), `TD-04` (finalisasi kontrak `WF-005` oleh Ramadan), `TD-05` (detail pola *Safety Guard*), `TD-06` (konfirmasi struktur folder kode).
- **Hasil Terverifikasi Audit Fisik (`DATA_DICTIONARY.md` v0.2, *read-only*, dipertahankan utuh untuk review Ramadan):**
  - `SRC-EDU-001` (`Buku Saku BNPB 2018.pdf`, 86 hal.): **100% *born-digital* (no OCR)**, 7 hal. <50 char = non-konten; mencakup 3 fase banjir (hal. PDF 40–47, selisih `+2` dari hal. cetak) + Tas Siaga Bencana (hal. PDF 16–20); status `layak_dengan_pembersihan` (URL asal resmi perlu dilengkapi).
  - `SRC-EDU-002` (`artikel_se_bnpb_4_2026.txt`): resmi BNPB (`2026-11-01`), bersih UTF-8, fokus kebijakan daerah + istilah (`InaRISK`/`DIBI`/`DSP`/`pentahelix`), perlu hapus artefak web; `siaran_pers_bmkg_nov_2026.txt` tidak ada di `data/raw/`.
  - 6 Excel BNPB (`SRC-TAB-001`–`006`, header asli Row 1): 3 layak bersyarat `FR-12` (`SRC-TAB-001` banjir nasional 2010–2024, `SRC-TAB-002` prov 2024 `1.420`, `SRC-TAB-003` prov 2025 `2.009` tanpa tanggal *cut-off*); 1 selisih total lintas kab/kota (`SRC-TAB-004`: `1.428` vs `1.420`); **2 ditolak** (`SRC-TAB-005`–`006`) karena hanya total semua bencana gabungan (bukan khusus banjir). Rekomendasi: **`FR-12` tetap opsional di luar MVP**.
- **Keamanan Lokal (TERVERIFIKASI AMAN):** `.env` lokal aktif berisi `GEMINI_API_KEY` & `GROQ_API_KEY` dan terabaikan `.gitignore` (`.gitignore:2:.env`), `logs/demo_*.jsonl` terabaikan `.gitignore`, `.env.example` bersih berisi placeholder, `0` kebocoran kredensial pada seluruh file workspace/log, dan `0` file sensitif pada seluruh riwayat Git (`git log --all`).
- **Blocker Aktif (Membutuhkan Ramadan / Keputusan Bersama):**
  1. **Persetujuan Ramadan atas `M0` belum tercatat:** Syahir sudah menyetujui `PRD.md` v0.3 & `TEAM_WORKFLOW.md` v0.5 (`24 Nov 2026`), namun konfirmasi Ramadan & verifikasi clone branch `ramadan` belum tersedia.
  2. **Cross-review Ramadan atas `M1`–`M3a` & Track Syahir:** Ramadan perlu meninjau [ARCHITECTURE.md](./ARCHITECTURE.md) v0.2 (`WF-004`, `WF-006`), mengonfirmasi [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) v0.2 (`WF-005`, `WF-007`–`WF-011`), dan menyetujui usulan model `OD-02` (`WF-017`: Primary `gemini-3.5-flash-lite`, Fallback `openai/gpt-oss-20b`).
  3. **Handoff Korpus *Frozen* (`WF-018`):** `data/processed/chunks.jsonl` dan `corpus_manifest.json` belum tersedia; mode RAG menunggu hasil ekstraksi & *chunking* Ramadan (`WF-012`–`WF-014`, `WF-018`) sebelum `M5` (*corpus freeze*) dan QA lintas perangkat (`WF-026`).
  4. **Keputusan terbuka `TD-01`–`TD-06` & `OD-01`–`OD-05`:** Termasuk penetapan 30 soal uji + *ground truth* + rubrik (`M7`).

---

## 8. Keputusan Final vs Masih Tertunda

- **Sudah Final:** Domain disetujui dosen, tim 2 mahasiswa, **pembagian peran final (Syahir: LLM & App; Ramadan: Data & Knowledge)**, target pengguna non-ahli Indonesia, cakupan umum Indonesia, Gemini (utama) + Groq (cadangan), RAG utama + LangChain selektif, Streamlit lokal, 30 soal (10+10+5+5) + Baseline vs RAG + penilaian independen 2 anggota, *corpus versioning & freeze*, statistik BNPB bersyarat, Git branching (`master`/`syahir`/`ramadan`).
- **Masih Tertunda (*Open Decisions* & Persetujuan):**
  - Persetujuan resmi **Ramadan** atas `M0` (`PRD.md` v0.3 & `TEAM_WORKFLOW.md` v0.5/v0.6) dan verifikasi clone branch `ramadan` *(Syahir sudah menyetujui `24 Nov 2026`)*.
  - `OD-01`: Judul akademik final (target: `WF-035` / Hari 6).
  - `OD-02`: Model spesifik & parameter API Gemini/Groq menunggu tes API oleh Syahir (target: `WF-017` / Hari 2).
  - `OD-03`: Daftar sumber final & kelayakan statistik BNPB menunggu review & finalisasi Ramadan (target: `WF-014` / Hari 3).
  - `OD-04` *(parsial)*: Tanggal kalender resmi UAS/deadline perkuliahan (Sprint 7 Hari bersifat target relatif mulai Hari 1).
  - `OD-05`: Detail rubrik penilaian, skala skor, & ambang evaluasi menunggu penyusunan 30 pertanyaan (target: `WF-029` / Hari 4).

---

## 9. Langkah Konkret Berikutnya

1. **Syahir (Siap Commit & Push Branch `syahir` untuk Cross-Review):** Branch `syahir` sudah bersih dari kebocoran kredensial dan lulus 22/22 test + live verifikasi; Syahir dapat melakukan *commit* & *push* ke `origin/syahir`, membuka Pull Request ke `master`, lalu mengirim permintaan *cross-review* ke Ramadan (mencakup `ARCHITECTURE.md` v0.2, implementasi `app.py`/`src/`/`scripts/`/`tests/`, serta usulan `OD-02`: Primary `gemini-3.5-flash-lite` & Fallback `openai/gpt-oss-20b`).
2. **Ramadan (Tutup `M0`, Review `M1`–`M3a` & Handoff Korpus `WF-018` di branch `ramadan`):** Lakukan `git clone`, berpindah ke `ramadan`, catat persetujuan `M0` di [TODO.md](./TODO.md) Bag. 5.1, tinjau PR Syahir & konfirmasi `OD-02`, finalisasi [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) (`WF-005`, `WF-007`–`WF-011`), lalu selesaikan `WF-012`–`WF-014` & `WF-018` (`data/processed/chunks.jsonl` + `corpus_manifest.json`).
3. **Integrasi `M5` (*Corpus Freeze*) → `M6`–`M8`:** Begitu korpus Ramadan tersedia, hubungkan ke `BM25CorpusRetriever`, lakukan uji internal *retrieval* & *corpus freeze* (`WF-021`), lanjutkan QA lintas perangkat (`WF-026`), kunci 30 soal + rubrik (`M7`), dan jalankan eksperimen Baseline vs RAG (`scripts/run_eval.py`).
