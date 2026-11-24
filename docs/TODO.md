# Project Progress Tracker (TODO) — SiagaBanjir

> **Status Dokumen:** Draft v0.4 (Revisi Pembagian Peran Final & Penyelarasan Git Bootstrap)  
> **Tanggal Pembuatan:** 24 November 2026  
> **Tim:** 2 mahasiswa — **Member A (Syahir — LLM & Application Engineering)** & **Member B (Ramadan — Data & Knowledge Preparation)**  
> **Acuan Kebutuhan:** [PRD.md](./PRD.md) (Draft v0.3)  
> **Acuan Alur Kerja & Git:** [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (Draft v0.5)  
> **Data Dictionary & Audit:** [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) (Draft v0.2)  
> **Context Recovery:** [context_windows.md](./context_windows.md) (Draft v0.3)  
> **Repository GitHub:** [Syahirmr/SiagaBanjir](https://github.com/Syahirmr/SiagaBanjir)

**Aturan Status Tugas:**
- `Not Started` — Belum dimulai.
- `In Progress` — Sedang dikerjakan atau persiapan teknis sudah berjalan namun masih menunggu verifikasi/persetujuan.
- `Blocked` — Terhambat oleh dependensi, akses data/API, atau keputusan tertunda.
- `Completed` — Seluruh kriteria selesai terbukti secara objektif dan lulus *cross-review* (*tidak boleh ditandai selesai tanpa bukti*).

---

## 1. Ringkasan Progres Milestone

Total pekerjaan terdaftar: **42 Work ID** (**38 tugas inti** `WF-001`–`WF-038` + **4 tugas opsional/bersyarat** `WF-OPT-01`–`WF-OPT-04`).  
Pembagian peran final: **Syahir (13 tugas solo)**, **Ramadan (11 tugas solo)**, **Bersama (14 tugas kolaboratif)** + 4 opsional.

| Milestone | Nama Milestone | Fase | Work ID | PIC Utama | Status | Catatan Progres / Gate |
|---|---|---|---|---|---|---|
| `M0` | Project Foundation Locked | Fase 1 | `WF-001`–`WF-003` | Bersama (Koord: Syahir) | `In Progress` | *Awaiting Team Approval* (Syahir & Ramadan) + verifikasi bootstrap branch (`master`/`syahir`/`ramadan`). |
| `M1` | Technical Plan Approved | Fase 2 | `WF-004`–`WF-006` | Syahir & Ramadan | `In Progress` | Draf awal `WF-005` tersedia di `DATA_DICTIONARY.md` untuk direview Ramadan; menunggu `M0` & `WF-004`/`WF-006` Syahir. |
| `M2` | Data Sources Collected & Verified | Fase 3 | `WF-007`–`WF-009` | Ramadan | `In Progress` | Inventaris awal 8 berkas `data/raw/` terdokumentasi di `DATA_DICTIONARY.md`; menunggu review Ramadan, kelengkapan URL asal & `M1`. |
| `M3` | Raw Data Audited & Prepared | Fase 4–5 | `WF-010`–`WF-014` | Ramadan | `In Progress` | Audit fisik awal *read-only* `WF-010`–`WF-011` tersedia di `DATA_DICTIONARY.md` untuk direview Ramadan; `WF-012`–`WF-014` belum dimulai. |
| `M4` | API & Model Configuration Validated | Fase 6 *(Paralel)* | `WF-015`–`WF-017` | Syahir | `Not Started` | Menunggu `M1` (paralel dengan `M2`–`M3`). |
| `M5` | RAG Pipeline Operational & Corpus Frozen | Fase 7 | `WF-018`–`WF-021` | Syahir & Ramadan | `Not Started` | Menunggu `M3` dan `M4` (`WF-018` Ramadan koordinasi dgn Syahir). |
| `M6` | MVP Chatbot Functional | Fase 8 | `WF-022`–`WF-026` | Syahir (QA: Ramadan) | `Not Started` | Menunggu `M5`. |
| `M7` | Evaluation Dataset & Ground Truth Ready | Fase 9 *(Paralel)* | `WF-027`–`WF-029` | Bersama | `Not Started` | Menunggu `M5` (*corpus frozen*; paralel dengan `M6`). |
| `M8` | Baseline vs RAG Evaluation Completed | Fase 10–11 | `WF-030`–`WF-034` | Bersama | `Not Started` | Menunggu `M6` dan `M7`. |
| `M9` | Academic Deliverables Completed | Fase 12 | `WF-035`–`WF-038` | Bersama | `Not Started` | Menunggu `M6` dan `M8`. |
| `M-OPT` | *(Bersyarat)* Statistik BNPB Demo Ready | Jalur Bersyarat | `WF-OPT-01`–`WF-OPT-03` | Ramadan & Syahir | `Not Started` | Hanya aktif jika `M6` stabil, audit `WF-011` Layak, dan tidak ganggu `M7`–`M9`. |
| *Opsional* | *(Could)* Konteks Percakapan *Multi-Turn* | Di luar jalur kritis | `WF-OPT-04` | Syahir | `Not Started` | Hanya dipertimbangkan bila `M8` selesai lebih awal tanpa ganggu `M9`. |

---

## 2. Sprint Plan 7 Hari (Target MVP, Evaluasi & Luaran Akademik)

> **Prinsip Sprint 7 Hari:** Seluruh 38 tugas inti (`WF-001`–`WF-038`) dijadwalkan paralel untuk **Member A (Syahir — LLM & App)** dan **Member B (Ramadan — Data & Knowledge)** agar MVP chatbot + evaluasi komparatif 30 pertanyaan + Poster Ilmiah selesai dalam 7 hari kalender. **Statistik BNPB (`FR-12`, `WF-OPT-01`–`WF-OPT-03`) dan *multi-turn* (`FR-13`, `WF-OPT-04`) tetap opsional** dan tidak dimasukkan ke jalur wajib 7 hari.

### 2.1 Jadwal Eksekusi Harian (Hari 1–7)

| Hari | Target Terukur | Work ID & Paralelisme (PIC / Reviewer) | Dependensi | Output Wajib | Acceptance Criteria Harian | Risiko & Fallback |
|---|---|---|---|---|---|---|
| **Hari 1** | Tutup `M0`, selesaikan desain arsitektur (`M1`), dan mulai paralel data (`M2`) + setup API (`M4`). | **Bersama:** `WF-001`–`WF-003` (tutup `M0`).<br>**Paralel `M1`:** Syahir=`WF-004`, `WF-006` (Rev: Ramadan); Ramadan=`WF-005` review draf `DATA_DICTIONARY.md` (Rev: Syahir).<br>**Paralel awal:** Ramadan=`WF-007`; Syahir=`WF-015`. | Persetujuan Syahir & Ramadan + branch Git aktif (blocker M0). | Persetujuan M0, branch `master`/`syahir`/`ramadan` terverifikasi, `ARCHITECTURE.md` + kontrak metadata + skema log (`M1`), review awal berkas resmi (`WF-007`), `.env.example` (`WF-015`). | `M0` & `M1` lulus *Exit Gate*; jalur paralel Syahir (`M4`) dan Ramadan (`M2`) berjalan tanpa saling menunggu. | Jika persetujuan tertunda di pagi hari, tetap susun draf `ARCHITECTURE.md` & review audit lokal di branch pribadi; tutup `M0` sebelum merge ke `master`. |
| **Hari 2** | Selesaikan verifikasi sumber (`M2`), *Physical Data Audit* (`M3a`), dan validasi API/model (`M4`). | **Ramadan (`M2`→`M3a`):** review & finalisasi `WF-007`–`WF-011` pada `DATA_DICTIONARY.md` (Rev: Syahir).<br>**Syahir (`M4`, paralel penuh):** `WF-016`, `WF-017` (Rev: Ramadan). | `M1` selesai. | Inventaris sumber resmi lengkap dgn URL (`M2`), persetujuan *Physical Data Audit* PDF & BNPB (`WF-010`, `WF-011`), laporan tes Gemini/Groq + keputusan model `OD-02` (`M4`). | 100% kandidat punya `source_date` & `retrieved_date`; 3 fase banjir tercakup; Gemini & Groq terbukti merespons nyata. | Jika perlu sumber tambahan terbaru, pilih PDF digital resmi terbaca (tolak OCR besar). Jika BNPB tidak memadai (`WF-011`), **tangguhkan `FR-12`** segera. |
| **Hari 3** | Selesaikan korpus bersih (`M3b`), bangun RAG & *Baseline*, dan kunci ***Corpus Freeze*** (`M5`). | **Pagi paralel:** Ramadan=`WF-012`, `WF-013`, `WF-014` (tutup `M3`); Syahir=`WF-020` (modul *Baseline* + kerangka RAG).<br>**Siang–Sore (`M5`):** Ramadan=`WF-018` (*chunking*/manifest, koordinasi dgn Syahir); Syahir=`WF-019`; Bersama=`WF-021`. | `M2`+`WF-010` (untuk `M3`); `M3`+`M4` (untuk `M5`). | Korpus teks bersih di `data/processed/` + `DATA_DICTIONARY.md` final (`OD-03`), `corpus_manifest` (`v1.0-frozen`), *pipeline* RAG & mode *Baseline* operasional (`M5`). | RAG mengambil konteks relevan dengan sitasi cocok metadata; *Baseline* pakai model/parameter identik; *corpus freeze* disetujui bersama. | Jika *retrieval* belum relevan, perbaiki *chunk*/param maksimal pagi Hari 4 sebelum *freeze*; jangan bekukan korpus cacat. |
| **Hari 4** | Selesaikan Streamlit MVP + *Safety* (`M6`) **paralel** dengan 30 soal uji, *Ground Truth* & rubrik (`M7`). | **Syahir (`M6`):** `WF-022`–`WF-025` (UI, darurat `FR-07`, *abstention*, ambigu, *error handling*, *logger*).<br>**Ramadan (`M7`, paralel pasca-`M5`):** draf `WF-027`–`WF-029`.<br>**Sore silang:** Ramadan=`WF-026` (QA lintas perangkat, tutup `M6`); Bersama finalisasi `WF-027`–`WF-029` (tutup `M7`). | `M5` (*corpus frozen*). | Aplikasi Streamlit lokal lulus QA di 2 perangkat (`M6`); `EVALUATION_PLAN.md`, 30 soal (10+10+5+5) + kasus darurat + *ground truth* + rubrik `OD-05` terkunci (`M7`). | 100% `FR-01`–`FR-11` lulus uji di 2 perangkat; komposisi tepat 10+10+5+5 terverifikasi pada korpus *frozen*; rubrik terkunci sebelum eksperimen. | Jika QA `WF-026` menemukan bug *safety*/UI, perbaiki maksimal pagi Hari 5 sebelum `WF-030`; bekukan seluruh fitur opsional. |
| **Hari 5** | Eksekusi eksperimen **Baseline vs RAG** (`M8a`) dan jalankan penilaian independen 2 anggota (`WF-032`). | **Pagi:** Syahir=`WF-030` (30 *Baseline*), `WF-031` (30 *RAG* + kasus darurat); Ramadan=audit kelengkapan log.<br>**Siang–Sore (paralel terpisah):** Syahir & Ramadan=`WF-032` (Lembar Skor A & Lembar Skor B independen). | `M6` dan `M7` selesai. | Log mentah terverifikasi (30 *Baseline*, 30 *RAG*, kasus darurat) lengkap `provider`/`model_id`/`corpus_version`/`source_dates`; 2 lembar skor independen. | Kedua kondisi memakai model, parameter, & 30 soal identik; kedua lembar skor terisi 100% sebelum diskusi rekonsiliasi. | Jika kuota Gemini terkena *rate limit*, gunakan jeda *throttling* atau jalankan ulang **kedua kondisi** pada model Groq cadangan yang sama agar adil. |
| **Hari 6** | Selesaikan rekonsiliasi & *Error Analysis* (`M8`), sinkronisasi dokumen, dan draf lengkap Poster Ilmiah (`M9` awal). | **Pagi (Bersama — tutup `M8`):** `WF-033` (rekonsiliasi & metrik aktual), `WF-034` (*Error Analysis*, koord: Ramadan).<br>**Siang–Sore (`M9` paralel):** Syahir=`WF-035` (judul final `OD-01` & sinkronisasi `docs/`); Ramadan=referensi resmi & tabel metrik → Bersama=`WF-036` (draf penuh Poster). | `WF-032` selesai. | Laporan Evaluasi Aktual & *Error Analysis* (`M8`), judul akademik final (`OD-01`), paket `docs/` sinkron, draf Poster Ilmiah 5 komponen. | Seluruh angka poster cocok 100% dengan tabel `WF-033`; *error analysis* jujur; bebas klaim "lebih pintar/lengkap dari AI umum". | Jika rekonsiliasi memakan waktu lebih lama, **pangkas 100% fitur opsional (`FR-12`, `FR-13`)**; jangan kurangi kualitas analisis evaluasi. |
| **Hari 7** | Finalisasi Poster Ilmiah, gladi demonstrasi lokal, dan audit kelulusan akhir (`M9`). | **Pagi (Bersama):** finalisasi `WF-036` (Poster 5 komponen wajib).<br>**Siang (Bersama — Op: Syahir, Verif: Ramadan):** `WF-037` (gladi demo live: parafrase, sitasi, darurat, *out-of-scope*, cadangan Groq).<br>**Sore (Bersama):** `WF-038` (*Final Completion Checklist* + cek `.gitignore`/Git + update `context_windows.md`). | `M6` dan `M8` selesai. | Poster Ilmiah final siap kumpul, catatan gladi demo lintas perangkat, *Final Completion Checklist* terverifikasi (`M9`). | Seluruh 5 komponen Poster lengkap berbasis data aktual; demo Streamlit stabil; 0 kebocoran kredensial; semua dokumen sinkron. | Jika jaringan/kuota terganggu saat gladi, verifikasi jalur cadangan Groq dan siapkan log eksperimen terekam sebagai bukti pendamping. |

### 2.2 Penilaian Realisme 7 Hari, Bottleneck & Aturan Pemangkasan
- **Kelayakan:** Target **7 hari kalender ketat namun realistis** untuk MVP (`FR-01`–`FR-11`), evaluasi komparatif 30 pertanyaan, dan Poster Ilmiah **hanya jika** (1) `M0` ditutup di awal Hari 1, (2) korpus dokumen edukasi resmi berformat PDF digital terbaca selesai dikurasi pada Hari 2, dan (3) kedua anggota menjalankan jalur paralel secara disiplin.
- **Bottleneck Kritis:**
  1. Penundaan persetujuan M0 oleh kedua anggota (menahan awal Hari 1).
  2. Iterasi *retrieval* berulang sebelum *corpus freeze* (`M3`→`M5`).
  3. Kuota/*rate limit* API dan durasi penilaian independen atas 60 respons (`30` Baseline + `30` RAG) pada Hari 5–6.
- **Rekomendasi Pemangkasan jika Terlambat (Urutan Prioritas):**
  1. **Pangkas pertama:** `WF-OPT-04` (*multi-turn* `FR-13`) — langsung dibekukan.
  2. **Pangkas kedua:** `WF-OPT-01`–`WF-OPT-03` (Statistik BNPB `FR-12`) — resmi ditangguhkan dan dicatat jujur sebagai keterbatasan ruang lingkup/waktu.
  3. **Pangkas ketiga:** Kustomisasi kosmetik antarmuka Streamlit (pertahankan UI bersih, sitasi, dan *disclaimer* keselamatan).
  4. **DILARANG DIPANGKAS:** Integrasi nyata API LLM, *corpus freeze*, protokol respons khusus darurat (`FR-07`), komposisi 30 pertanyaan (10+10+5+5), eksperimen Baseline vs RAG terkontrol, penilaian independen 2 anggota, *error analysis*, dan 5 komponen wajib Poster Ilmiah.

---

## 3. Status Verifikasi M0 & Hal yang Masih Dibutuhkan

| Syarat M0 | Status Teknis | Bukti / Catatan |
|---|---|---|
| 1. `PRD.md` v0.3 menjadi acuan | Siap teknis (menunggu persetujuan kedua anggota) | [PRD.md](./PRD.md) Draft v0.3 tersedia; persetujuan eksplisit Syahir & Ramadan belum dicatat. |
| 2. `TEAM_WORKFLOW.md` memuat peran final & aturan Git | Siap teknis (menunggu persetujuan kedua anggota) | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) Draft v0.5 memuat peran final (Syahir: LLM & App; Ramadan: Data & Knowledge) & Git strategy (`master`, `syahir`, `ramadan`). |
| 3. `TODO.md` memuat 42 task & semua milestone | Siap | Dokumen ini memuat `WF-001`–`WF-038`, `WF-OPT-01`–`WF-OPT-04`, `M0`–`M9`, `M-OPT`. |
| 4. Konvensi folder terdokumentasi | Siap | Terdokumentasi di `TEAM_WORKFLOW.md` Bagian M.5 (`docs/`, `data/raw/`, `data/processed/`). |
| 5. `.env` & kredensial aman dari Git | Siap secara lokal | `.gitignore` melindungi `.env`, `.env.*`, `.streamlit/secrets.toml`, `venv/` dan melacak `.env.example`; 0 file `.env` / API key hardcoded ditemukan. |
| 6. Bootstrap branch (`master`, `syahir`, `ramadan`) | Dijalankan pada sesi bootstrap M0 *(verifikasi aktual di laporan & `git branch -vv`)* | Remote `https://github.com/Syahirmr/SiagaBanjir.git` kosong; menunggu konfirmasi clone/pull Ramadan pada branch `ramadan`. |
| 7. Pembagian kerja 2 anggota tersedia | Siap teknis (menunggu persetujuan kedua anggota) | Pembagian final Syahir (13 solo) & Ramadan (11 solo) + 14 bersama pada `TEAM_WORKFLOW.md` v0.5. |

**Syarat agar `M0` dapat diubah ke `Completed`:**
1. **Persetujuan eksplisit Member A (Syahir)** dan **Member B (Ramadan)** atas [PRD.md](./PRD.md) v0.3 dan [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) v0.5 (dicatat pada Bagian 5.1 di bawah).
2. **Verifikasi aktif branch `master`, `syahir`, dan `ramadan`** pada remote `[Syahirmr/SiagaBanjir](https://github.com/Syahirmr/SiagaBanjir)` termasuk konfirmasi akses & *clone* oleh Ramadan.

---

## 4. Daftar Tugas Lengkap (WBS — 42 Work ID)

### Fase 1 — Project Setup & Documentation Alignment (`M0`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-001` | Review & penguncian acuan `PRD.md` v0.3 | Bersama (Koord: Syahir) | Ramadan | `M0` | `In Progress` | [PRD.md](./PRD.md) (Draft v0.3) | *Awaiting Team Approval:* menunggu persetujuan resmi Syahir & Ramadan. |
| `WF-002` | Persetujuan workflow, peran final & Git strategy | Bersama (Koord: Syahir) | Ramadan | `M0` | `In Progress` | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (Draft v0.5) | *Awaiting Team Approval:* dokumen siap secara teknis, menunggu persetujuan Syahir & Ramadan. |
| `WF-003` | Inisiasi `TODO.md`, konvensi folder, `.gitignore` & bootstrap branch Git | Bersama (Koord: Syahir) | Ramadan | `M0` | `In Progress` | [TODO.md](./TODO.md), `../.gitignore`, status Git bootstrap | `.gitignore` & `TODO.md` siap; menunggu verifikasi clone/branch `ramadan` dan persetujuan M0. |

### Fase 2 — Technical Planning & Architecture Design (`M1`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-004` | Penyusunan `ARCHITECTURE.md` (RAG & LangChain selektif) | Member A (Syahir) | Member B (Ramadan) | `M1` | `Not Started` | `ARCHITECTURE.md` *(planned)* | Menunggu `M0` *Completed*. |
| `WF-005` | Penetapan kontrak skema metadata & chunk korpus | Member B (Ramadan) | Member A (Syahir) | `M1` | `In Progress` | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 1 | Draf kontrak awal tersedia (disusun Syahir); menunggu review/adopsi Ramadan, `WF-004`, dan `M0`. |
| `WF-006` | Desain protokol safety darurat & skema log reproducibility | Member A (Syahir) | Member B (Ramadan) | `M1` | `Not Started` | Spesifikasi *safety prompt* & skema log di `ARCHITECTURE.md` *(planned)* | Menunggu `WF-004`. |

### Fase 3 — Data Collection & Source Verification (`M2`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-007` | Pengumpulan kandidat dokumen edukasi resmi Indonesia | Member B (Ramadan) | Member A (Syahir) | `M2` | `In Progress` | `data/raw/` (2 berkas: PDF BNPB 2018 + TXT SE BNPB 4/2026) & [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 2.1 | 3 fase banjir tercakup di PDF 2018; `siaran_pers_bmkg_nov_2026.txt` tidak ada di `data/raw/`; menunggu review Ramadan soal perlu/tidaknya tambahan sumber BMKG/terbaru. |
| `WF-008` | Verifikasi sumber & pencatatan metadata awal | Member B (Ramadan) | Member A (Syahir) | `M2` | `In Progress` | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 2.1 | Metadata 2 berkas tercatat; URL resmi asal PDF 2018 perlu dilengkapi Ramadan lalu di-review Syahir. |
| `WF-009` | Pengumpulan terpisah kandidat dataset statistik BNPB *(opsional)* | Member B (Ramadan) | Member A (Syahir) | `M2` | `In Progress` | `data/raw/` (6 berkas `.xlsx` BNPB) & [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 2.2 | Terpisah dari korpus edukasi MVP; URL asal DIBI/BNPB perlu dilengkapi saat review Ramadan. |

### Fase 4 & 5 — Physical Data Audit, Preparation & Quality Validation (`M3`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-010` | Physical audit dokumen edukasi (ekstraksi & keterbacaan) | Member B (Ramadan) | Member A (Syahir) | `M3` | `In Progress` | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 3 (`audit_data.py` + inspeksi halaman) | Bukti audit awal *read-only* lengkap (PDF 2018 100% *born-digital*, no OCR; TXT 2026 perlu *cleaning*); diserahkan untuk ditinjau & dikonfirmasi Ramadan. |
| `WF-011` | Physical audit kandidat dataset statistik BNPB *(bersyarat)* | Member B (Ramadan) | Member A (Syahir) | `M3` | `In Progress` | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 4 | Bukti audit awal *read-only* 6 `.xlsx` lengkap (3 layak bersyarat, 1 selisih `1.428` vs `1.420`, 2 **ditolak** bukan khusus banjir); menunggu review Ramadan. |
| `WF-012` | Ekstraksi teks & pembersihan korpus edukasi | Member B (Ramadan) | Member A (Syahir) | `M3` | `Not Started` | Kumpulan teks bersih ber-metadata di `data/processed/` | Menunggu `WF-010`, `WF-005`. |
| `WF-013` | Validasi kualitas teks (*spot-check* terhadap dokumen asli) | Member B (Ramadan) | Member A (Syahir) | `M3` | `Not Started` | Catatan hasil *spot-check* ekstraksi & halaman | Menunggu `WF-012`. |
| `WF-014` | Finalisasi `DATA_DICTIONARY.md` & daftar sumber final (`OD-03`) | Member B (Ramadan) | Member A (Syahir) | `M3` | `Not Started` | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) final & penutupan `OD-03` | Menunggu `WF-010`–`WF-013`. |

### Fase 6 — API Testing & Model Selection — Jalur Paralel (`M4`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-015` | Setup lingkungan & pengelolaan API key aman (`.env.example`) | Member A (Syahir) | Member B (Ramadan) | `M4` | `Not Started` | `.env.example`, modul pemuat konfigurasi `.env` | Menunggu `M1`; berjalan paralel dengan `M2`–`M3`. |
| `WF-016` | Pengujian aktual Gemini API (utama) & Groq API (cadangan) | Member A (Syahir) | Member B (Ramadan) | `M4` | `Not Started` | Log & tabel perbandingan tes API aktual | Menunggu `WF-015`; jangan mengunci model sebelum bukti tes. |
| `WF-017` | Penetapan model spesifik & konfigurasi terkendali (`OD-02`) | Member A (Syahir) | Member B (Ramadan) | `M4` | `Not Started` | Catatan keputusan `OD-02` di `ARCHITECTURE.md` *(planned)* | Menunggu `WF-016`. |

### Fase 7 — Corpus Preparation, RAG Development & Corpus Freeze (`M5`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-018` | Chunking korpus & penyusunan `corpus_manifest` berversi | Member B (Ramadan) | Member A (Syahir) | `M5` | `Not Started` | Dataset *chunk* ber-metadata & `corpus_manifest` berversi | Menunggu `M3` (`WF-012`, `WF-014`); koordinasi integrasi bersama Syahir. |
| `WF-019` | Implementasi indeks retrieval & pipeline RAG (LangChain selektif) | Member A (Syahir) | Member B (Ramadan) | `M5` | `Not Started` | Modul *retriever* & *pipeline* RAG operasional | Menunggu `WF-018` dan `M4` (`WF-017`). |
| `WF-020` | Implementasi jalur Baseline LLM (tanpa retrieval) | Member A (Syahir) | Member B (Ramadan) | `M5` | `Not Started` | Modul/mode eksekusi *Baseline* LLM identik parameter | Menunggu `M4` (`WF-017`), `WF-019`. |
| `WF-021` | Verifikasi kualitas retrieval, kesiapan Baseline & Corpus Freeze | Bersama (Koord: Ramadan) | Kedua anggota | `M5` | `Not Started` | Catatan uji internal & persetujuan `corpus_v1.0-frozen` | Menunggu `WF-018`, `WF-019`, `WF-020`. |

### Fase 8 — Streamlit Integration & Safety Implementation (`M6`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-022` | Pengembangan antarmuka chat Streamlit lokal & transparansi UI | Member A (Syahir) | Member B (Ramadan) | `M6` | `Not Started` | Aplikasi Streamlit lokal (`FR-01`, `FR-10`) | Menunggu `M5`. |
| `WF-023` | Implementasi protokol darurat akut, abstention & ambiguitas | Member A (Syahir) | Member B (Ramadan) | `M6` | `Not Started` | Logika *safety* & *prompt* (`FR-05`, `FR-07`, `FR-08`) | Menunggu `WF-006`, `WF-019`, `WF-022`. |
| `WF-024` | Implementasi error handling & fallback Groq API | Member A (Syahir) | Member B (Ramadan) | `M6` | `Not Started` | Mekanisme *error handling* & konfigurasi cadangan (`FR-09`) | Menunggu `WF-022`, `M4`. |
| `WF-025` | Implementasi logger reproducibility & evaluasi (`FR-11`) | Member A (Syahir) | Member B (Ramadan) | `M6` | `Not Started` | Modul/skrip log (`provider`, `model_id`, `corpus_version`, `source_dates`) | Menunggu `WF-006`, `WF-019`, `WF-020`. |
| `WF-026` | Uji fungsional end-to-end, negative testing & lintas perangkat | Member B (Ramadan) | Member A (Syahir) | `M6` | `Not Started` | Laporan QA MVP & bukti jalan di perangkat kedua anggota | Menunggu `WF-022`–`WF-025`. |

### Fase 9 — Test Dataset & Ground Truth Preparation (`M7` — Paralel Pasca-`M5`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-027` | Penyusunan 30 pertanyaan uji (10+10+5+5) & kasus darurat | Bersama | Silang (A ↔ B) | `M7` | `Not Started` | Dataset 30 pertanyaan uji + daftar kasus uji darurat | Menunggu `M5` (*corpus frozen*); komposisi tetap. |
| `WF-028` | Penyusunan ground truth bersama berbasis korpus frozen | Bersama | Silang (A ↔ B) | `M7` | `Not Started` | Dataset *ground truth* terkunci dengan rujukan dokumen asli | Menunggu `WF-027`, `M5`. |
| `WF-029` | Penyusunan `EVALUATION_PLAN.md` & rubrik penilaian (`OD-05`) | Bersama (Koord: Ramadan) | Kedua anggota | `M7` | `Not Started` | `EVALUATION_PLAN.md` *(planned)* & penutupan `OD-05` | Menunggu `WF-028`; dikunci sebelum eksperimen. |

### Fase 10 & 11 — Baseline vs RAG Experiment, Scoring & Error Analysis (`M8`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-030` | Eksekusi eksperimen Kondisi A (Baseline LLM tanpa retrieval) | Member A (Syahir) | Member B (Ramadan) | `M8` | `Not Started` | File log mentah 30 respons Kondisi A | Menunggu `M6`, `M7`, `WF-020`. |
| `WF-031` | Eksekusi eksperimen Kondisi B (SiagaBanjir RAG) & uji darurat | Member A (Syahir) | Member B (Ramadan) | `M8` | `Not Started` | File log mentah 30 respons Kondisi B + log kasus darurat | Menunggu `M6`, `M7`, `WF-030` (model/parameter identik). |
| `WF-032` | Penilaian independen oleh Member A dan Member B | Syahir & Ramadan (terpisah) | Rekonsiliasi di `WF-033` | `M8` | `Not Started` | 2 lembar penilaian independen terpisah (Lembar A & Lembar B) | Menunggu `WF-030`, `WF-031`, `WF-029`. |
| `WF-033` | Rekonsiliasi skor & kompilasi metrik aktual Baseline vs RAG | Bersama | Kedua anggota | `M8` | `Not Started` | Tabel skor terekonsiliasi + catatan kesepakatan/selisih | Menunggu `WF-032`, `WF-028`. |
| `WF-034` | Analisis kesalahan (*error analysis*) & dokumentasi keterbatasan | Bersama (Koord: Ramadan) | Member A (Syahir) | `M8` | `Not Started` | Laporan evaluasi aktual & *Error Analysis* | Menunggu `WF-033`, `WF-030`, `WF-031`. |

### Fase 12 — Final Documentation, Poster & Demonstration (`M9`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-035` | Penetapan judul akademik final (`OD-01`) & sinkronisasi dokumen | Bersama (Koord: Syahir) | Member B (Ramadan) | `M9` | `Not Started` | Judul final & paket dokumentasi `docs/` tersinkronisasi | Menunggu `M8`. |
| `WF-036` | Penyusunan konten & desain Poster Ilmiah (5 komponen wajib) | Bersama | Kedua anggota | `M9` | `Not Started` | File Poster Ilmiah final berbasis hasil aktual Baseline vs RAG | Menunggu `WF-034`, `WF-035`. |
| `WF-037` | Gladi demonstrasi lokal Streamlit & uji skenario live | Bersama (Op: Syahir; Verif: Ramadan) | Kedua anggota | `M9` | `Not Started` | Daftar skenario demo & catatan hasil gladi bersih | Menunggu `M6`, `WF-035`. |
| `WF-038` | Audit akhir checklist kelulusan & keamanan kredensial | Bersama | Kedua anggota | `M9` | `Not Started` | *Final Completion Checklist* terverifikasi + cek `.gitignore`/Git | Menunggu `WF-035`–`WF-037`. |

### Jalur Tambahan Bersyarat (`M-OPT`) & Opsional (`Could`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-OPT-01` | Pembersihan & validasi dataset tabular BNPB | Member B (Ramadan) | Member A (Syahir) | `M-OPT` | `Not Started` | Dataset BNPB bersih + skema di `DATA_DICTIONARY.md` | Bersyarat: hanya jika `M6` stabil & `WF-011` Layak. |
| `WF-OPT-02` | Implementasi modul statistik deterministik & integrasi demo UI | Member A (Syahir) | Member B (Ramadan) | `M-OPT` | `Not Started` | Modul Pandas deterministik + tab/opsi terpisah di Streamlit | Menunggu `WF-OPT-01`, `M6`. |
| `WF-OPT-03` | Verifikasi kecocokan angka & uji non-regresi MVP | Member B (Ramadan) | Member A (Syahir) | `M-OPT` | `Not Started` | Bukti 100% kecocokan angka & cek non-regresi MVP | Menunggu `WF-OPT-02`. |
| `WF-OPT-04` | Konteks percakapan *multi-turn* (`FR-13` — `Could`) | Member A (Syahir) | Member B (Ramadan) | Opsional (`Could`) | `Not Started` | Dukungan *multi-turn* teruji di sesi Streamlit | Di luar jalur kritis; hanya jika `M8` tuntas lebih awal tanpa ganggu `M9`. |

---

## 5. Catatan Keputusan & Pelacakan Persetujuan

### 5.1 Log Persetujuan M0 *(Diisi Langsung oleh Anggota Tim)*
| Anggota | Peran Final | Persetujuan `PRD.md` v0.3 | Persetujuan `TEAM_WORKFLOW.md` v0.5 | Tanggal | Catatan |
|---|---|---|---|---|---|
| **Member A (Syahir)** | LLM & Application Engineering | *Belum dicatat* | *Belum dicatat* | — | Konfirmasi manual diperlukan untuk menutup `M0`. |
| **Member B (Ramadan)** | Data & Knowledge Preparation | *Belum dicatat* | *Belum dicatat* | — | Konfirmasi manual diperlukan untuk menutup `M0`. |

### 5.2 Catatan Keputusan & Open Decisions (`OD-01`–`OD-05`)
| Tanggal | ID / Topik | Status | Ringkasan Keputusan / Catatan | Dampak Dokumen |
|---|---|---|---|---|
| 24 Nov 2026 | Domain & keputusan inti tim | Final | Domain disetujui dosen; 2 mahasiswa; Gemini API utama & Groq cadangan; RAG + LangChain selektif; Streamlit lokal; 30 soal Baseline vs RAG; statistik BNPB bersyarat. | [PRD.md](./PRD.md) v0.3 |
| 24 Nov 2026 | Revisi pembagian peran final & Git bootstrap | Final (peran) / Bootstrap M0 | **Syahir (Member A): LLM & Application Engineering** (13 solo); **Ramadan (Member B): Data & Knowledge Preparation** (11 solo termasuk `WF-018` koordinasi dgn Syahir & QA `WF-026`); 14 bersama. Artefak audit awal `DATA_DICTIONARY.md` dipertahankan untuk review Ramadan. | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) v0.5, [TODO.md](./TODO.md) v0.4, [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) v0.2, [context_windows.md](./context_windows.md) v0.3 |
| 24 Nov 2026 | Sprint Plan 7 Hari & Context Recovery | Siap Teknis *(target operasional relatif)* | Jadwal paralel Hari 1–7 untuk 38 tugas inti + catatan bottleneck/pemangkasan fitur opsional serta pembuatan `context_windows.md`. | [TODO.md](./TODO.md) v0.4, [context_windows.md](./context_windows.md) v0.3 |
| 24 Nov 2026 | Draf Kontrak Metadata (`WF-005`) & Physical Audit *Read-Only* (`WF-007`–`WF-011`) | Draf Awal *(review Ramadan)* | Audit fisik seluruh 8 berkas `data/raw/`: PDF BNPB 2018 100% *born-digital* (no OCR), TXT SE BNPB 4/2026 layak perlu *cleaning*, 2 Excel BNPB ditolak (bukan khusus banjir), 1 Excel kab/kota selisih total (`1.428` vs `1.420`), 3 Excel layak bersyarat (`FR-12` tetap opsional). | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) v0.2, [TODO.md](./TODO.md) v0.4 |
| — | `OD-01` Judul akademik final | Open | Ditetapkan pada `WF-035` (`M9`). | `PRD.md`, Poster |
| — | `OD-02` Model spesifik & konfigurasi API | Open | Ditetapkan setelah tes aktual Gemini/Groq pada `WF-017` (`M4`). | `ARCHITECTURE.md` |
| — | `OD-03` Daftar sumber final & kelayakan BNPB | Open | Ditetapkan setelah *data collection* & *physical audit* pada `WF-014` (`M3`). | `DATA_DICTIONARY.md` |
| — | `OD-04` Jadwal kalender spesifik *milestone* | Open *(parsial)* | Pembagian kerja & Sprint 7 Hari selesai; tanggal kalender UAS menunggu konfirmasi tim. | `TEAM_WORKFLOW.md`, `TODO.md` |
| — | `OD-05` Rubrik & ambang evaluasi | Open | Ditetapkan setelah penyusunan 30 pertanyaan uji pada `WF-029` (`M7`). | `EVALUATION_PLAN.md` |
