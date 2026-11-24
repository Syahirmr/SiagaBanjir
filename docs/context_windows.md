# Context Recovery Snapshot — SiagaBanjir

> **Status Dokumen:** Draft v0.3 *(Revisi Pembagian Peran Final & Git Bootstrap M0)*  
> **Terakhir Diperbarui:** 24 November 2026  
> **Referensi Utama:** [PRD.md](./PRD.md) (v0.3) | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (v0.5) | [TODO.md](./TODO.md) (v0.4) | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) (v0.2)  
> **Repository GitHub:** [Syahirmr/SiagaBanjir](https://github.com/Syahirmr/SiagaBanjir)

> **Aturan Pemeliharaan:** Wajib perbarui file ini setiap kali terjadi perubahan keputusan penting, penutupan *Open Decision* (`OD-01`–`OD-05`), perubahan status milestone (`M0`–`M9`, `M-OPT`), atau perubahan blocker utama.

---

## 1. Aturan Wajib untuk AI / Agent *(Cold-Start Protocol)*

Sebelum melakukan pekerjaan apa pun pada sesi baru, AI/agent **wajib**:
1. Membaca secara berurutan: `docs/context_windows.md` (file ini) → [PRD.md](./PRD.md) → [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) → [TODO.md](./TODO.md) → [DATA_DICTIONARY.md](./DATA_DICTIONARY.md).
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
  - Tersedia: [PRD.md](./PRD.md) (v0.3), [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (v0.5), [TODO.md](./TODO.md) (v0.4), [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) (v0.2 — artefak audit awal siap review Ramadan), [context_windows.md](./context_windows.md) (v0.3), serta referensi `BIG PROJECT.jpeg`.
  - *Planned Documents* (belum dibuat): `ARCHITECTURE.md` (`M1` — PIC Syahir), `EVALUATION_PLAN.md` (`M7`).
- **Folder & File Root:**
  - `data/raw/` — sudah ada (**8 berkas mentah: 2 edukasi + 6 Excel BNPB**); **read-only, tidak boleh ditimpa**.
  - `data/processed/` — belum dibuat secara fisik; lokasi konvensi untuk hasil ekstraksi/korpus mulai `WF-012` (`M3`, PIC Ramadan).
  - `.gitignore` — aktif; mengabaikan `.env`, `.env.*`, `.streamlit/secrets.toml`, `venv/`, cache Python; melacak `.env.example` (`!.env.example`).
  - `audit_data.py` (*read-only*, aman; keterbatasan: belum scan `.txt` & Excel masih `header=0`), `prep_step1.py` (**jangan dijalankan** karena menimpa `data/raw/`), `venv/` — tidak diubah.

---

## 6. Pembagian Peran FINAL & Strategi Git

- **Member A (Syahir) — LLM & Application Engineering** *(Branch: `syahir` | 13 tugas solo)*: `WF-004` (`ARCHITECTURE.md`), `WF-006` (protokol *safety*/log), `WF-015`–`WF-017` (setup `.env.example`, tes Gemini & Groq API, pemilihan model `OD-02`), `WF-019`–`WF-020` (*pipeline* RAG & jalur *Baseline*), `WF-022`–`WF-025` (UI Streamlit lokal, protokol darurat, *error handling*, *logger*), serta `WF-030`–`WF-031` (eksekusi eksperimen Baseline vs RAG). *(Opsional: `WF-OPT-02`, `WF-OPT-04`.)*
- **Member B (Ramadan) — Data & Knowledge Preparation** *(Branch: `ramadan` | 11 tugas solo)*: `WF-005` (kontrak metadata), `WF-007`–`WF-014` (pengumpulan/verifikasi sumber, *physical audit* meninjau draf awal `DATA_DICTIONARY.md`, ekstraksi & pembersihan, *spot-check*, finalisasi `DATA_DICTIONARY.md` / `OD-03`), `WF-018` (*chunking* & `corpus_manifest` dengan koordinasi integrasi bersama Syahir), serta `WF-026` (QA independen lintas perangkat atas MVP Syahir). *(Opsional: `WF-OPT-01`, `WF-OPT-03`.)*
- **Tanggung Jawab Bersama (14 tugas):** `WF-001`–`WF-003` (fondasi M0), `WF-021` (verifikasi *retrieval* & *corpus freeze*), `WF-027`–`WF-029` (30 soal, *ground truth* & rubrik), `WF-032`–`WF-034` (penilaian independen, rekonsiliasi, *error analysis*), `WF-035`–`WF-038` (dokumentasi final, Poster Ilmiah, gladi demo, audit kelulusan).
- **Aturan Git Inti:** Remote `https://github.com/Syahirmr/SiagaBanjir.git`; branch `master` (*stable*), `syahir`, `ramadan` (*lowercase*). Dilarang *commit* langsung ke `master`; kerja & *push* hanya ke branch pribadi; sinkronisasi dari `master` sebelum/sesudah kerja; prefix *commit* `docs:`/`feat:`/`fix:`/`data:`/`test:`/`chore:`; merge ke `master` wajib lewat Pull Request & review partner; dilarang *force push*/*destructive reset*.

---

## 7. Status Terakhir Milestone, Work ID, Audit Fisik & Blocker *(per 24 Nov 2026)*

- **Milestone:** `M0`, `M1`, `M2`, `M3` = **`In Progress`** *(draf awal `WF-005` & `WF-007`–`WF-011` tersedia di `DATA_DICTIONARY.md` v0.2 untuk ditinjau Ramadan; menunggu penutupan persetujuan `M0` & `WF-004` Syahir)*; `M4`–`M9` & `M-OPT` = **`Not Started`**.
- **Work ID (42 total):** `9` `In Progress` (`WF-001`–`WF-003`, `WF-005`, `WF-007`–`WF-011`), `33` `Not Started`, `0` `Blocked`, `0` `Completed`.
- **Hasil Terverifikasi Audit Fisik (`DATA_DICTIONARY.md` v0.2, *read-only*, dipertahankan utuh untuk review Ramadan):**
  - `SRC-EDU-001` (`Buku Saku BNPB 2018.pdf`, 86 hal.): **100% *born-digital* (no OCR)**, 7 hal. <50 char = non-konten; mencakup 3 fase banjir (hal. PDF 40–47, selisih `+2` dari hal. cetak) + Tas Siaga Bencana (hal. PDF 16–20); status `layak_dengan_pembersihan` (URL asal resmi perlu dilengkapi).
  - `SRC-EDU-002` (`artikel_se_bnpb_4_2026.txt`): resmi BNPB (`2026-11-01`), bersih UTF-8, fokus kebijakan daerah + istilah (`InaRISK`/`DIBI`/`DSP`/`pentahelix`), perlu hapus artefak web; `siaran_pers_bmkg_nov_2026.txt` tidak ada di `data/raw/`.
  - 6 Excel BNPB (`SRC-TAB-001`–`006`, header asli Row 1): 3 layak bersyarat `FR-12` (`SRC-TAB-001` banjir nasional 2010–2024, `SRC-TAB-002` prov 2024 `1.420`, `SRC-TAB-003` prov 2025 `2.009` tanpa tanggal *cut-off*); 1 selisih total lintas kab/kota (`SRC-TAB-004`: `1.428` vs `1.420`); **2 ditolak** (`SRC-TAB-005`–`006`) karena hanya total semua bencana gabungan (bukan khusus banjir). Rekomendasi: **`FR-12` tetap opsional di luar MVP**.
- **Keamanan Lokal:** `.gitignore` aktif; 0 file `.env`/`.streamlit/secrets.toml` dan 0 API key *hardcoded* ditemukan di workspace (luar `venv/`).
- **Status Git & Blocker Aktif:**
  1. **Persetujuan manusia M0 belum tercatat:** Syahir dan Ramadan belum mencatat persetujuan resmi atas `PRD.md` v0.3 & `TEAM_WORKFLOW.md` v0.5 pada `TODO.md` Bagian 5.1.
  2. **Review Ramadan atas artefak audit awal & akses branch `ramadan`:** Ramadan perlu *clone* repository, mengaktifkan branch `ramadan`, meninjau `DATA_DICTIONARY.md` v0.2 (`WF-005`, `WF-007`–`WF-011`), dan melengkapi URL asal `SRC-EDU-001`.
  3. **Desain Arsitektur Syahir (`M1`):** `WF-004` & `WF-006` (`ARCHITECTURE.md`) belum dimulai oleh Syahir (menunggu penutupan persetujuan M0).

---

## 8. Keputusan Final vs Masih Tertunda

- **Sudah Final:** Domain disetujui dosen, tim 2 mahasiswa, **pembagian peran final (Syahir: LLM & App; Ramadan: Data & Knowledge)**, target pengguna non-ahli Indonesia, cakupan umum Indonesia, Gemini (utama) + Groq (cadangan), RAG utama + LangChain selektif, Streamlit lokal, 30 soal (10+10+5+5) + Baseline vs RAG + penilaian independen 2 anggota, *corpus versioning & freeze*, statistik BNPB bersyarat, Git branching (`master`/`syahir`/`ramadan`).
- **Masih Tertunda (*Open Decisions* & Persetujuan):**
  - Persetujuan resmi Syahir & Ramadan atas M0 (`PRD.md` v0.3 & `TEAM_WORKFLOW.md` v0.5).
  - `OD-01`: Judul akademik final (target: `WF-035` / Hari 6).
  - `OD-02`: Model spesifik & parameter API Gemini/Groq menunggu tes API oleh Syahir (target: `WF-017` / Hari 2).
  - `OD-03`: Daftar sumber final & kelayakan statistik BNPB menunggu review & finalisasi Ramadan (target: `WF-014` / Hari 3).
  - `OD-04` *(parsial)*: Tanggal kalender resmi UAS/deadline perkuliahan (Sprint 7 Hari bersifat target relatif mulai Hari 1).
  - `OD-05`: Detail rubrik penilaian, skala skor, & ambang evaluasi menunggu penyusunan 30 pertanyaan (target: `WF-029` / Hari 4).

---

## 9. Langkah Konkret Berikutnya

1. **Syahir & Ramadan (Tutup `M0`):** Catat persetujuan resmi atas `PRD.md` v0.3 & `TEAM_WORKFLOW.md` v0.5 di [TODO.md](./TODO.md) Bagian 5.1; Ramadan melakukan `git clone` dan berpindah ke branch `ramadan`, Syahir berpindah ke branch `syahir`.
2. **Syahir (Branch `syahir` — `M1` & `M4` Paralel):** Susun `docs/ARCHITECTURE.md` (`WF-004`, `WF-006`) selaras dengan kontrak metadata pada [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 1, lalu jalankan setup `.env.example` & tes aktual Gemini/Groq API (`WF-015`–`WF-017`, `OD-02`).
3. **Ramadan (Branch `ramadan` — Review `M1`–`M3a` & Lanjut `M3b`):** Tinjau & finalisasi `WF-005` & `WF-007`–`WF-011` pada [DATA_DICTIONARY.md](./DATA_DICTIONARY.md), lengkapi URL resmi `SRC-EDU-001` (dan putuskan bersama soal tambahan sumber terbaru), lalu kerjakan `WF-012`–`WF-014` (ekstraksi bersih ke `data/processed/`) dan `WF-018` (*chunking*/manifest koordinasi dgn Syahir).
4. Perbarui [TODO.md](./TODO.md) dan `docs/context_windows.md` setelah `M0` resmi `Completed` dan `M1` berjalan.
