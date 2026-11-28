# Project Progress Tracker (TODO) — SiagaBanjir

> **Status Dokumen:** Draft v0.14 *(Final Project Audit & Baseline v1.3 FREEZE: `prompt_v1.3`, Paritas `SafetyGuard` 2×2, 37/37 Unit Test & 50/50 EV-50 Offline Lulus — Siap Push & PR Cross-Review Ramadan)*<br>
> **Tanggal Pembuatan:** 24 November 2026 *(Diperbarui: 28 November 2026)*<br>
> **Tim:** 2 mahasiswa — **Member A (Syahir — LLM & Application Engineering)** & **Member B (Ramadan — Data & Knowledge Preparation)**<br>
> **Acuan Kebutuhan:** [PRD.md](./PRD.md) (Draft v0.3)<br>
> **Acuan Alur Kerja & Git:** [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (Draft v0.6)<br>
> **Arsitektur & Safety/Log:** [ARCHITECTURE.md](./ARCHITECTURE.md) (Draft v0.3)<br>
> **Data Dictionary & Audit:** [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) (Draft v0.2)<br>
> **Context Recovery:** [context_windows.md](./context_windows.md) (Draft v0.14)<br>
> **Repository GitHub:** [Syahirmr/SiagaBanjir](https://github.com/Syahirmr/SiagaBanjir)

**Aturan Status Progres (`Progress Status` — terpisah dari `Execution Readiness` pada Bagian 6):**
- `Not Started` — Belum dimulai.
- `In Progress` — Sedang dikerjakan atau persiapan teknis sudah berjalan namun masih menunggu verifikasi/persetujuan.
- `Blocked` — Terhambat oleh dependensi, akses data/API, atau keputusan tertunda.
- `Completed` — Seluruh kriteria selesai terbukti secara objektif dan lulus *cross-review* (*tidak boleh ditandai selesai tanpa bukti*).

> **Panduan Mulai Kerja:** Sebelum memulai Work ID apa pun, periksa **Bagian 6 (*Execution Readiness & Dependency Map*)** untuk memastikan apakah tugas berstatus `Ready`, `Ready-Coordination`, `Joint-Gate`, atau `Blocked` beserta pembuka dan aturan *handoff*-nya.

---

## 1. Ringkasan Progres Milestone

Total pekerjaan terdaftar: **42 Work ID** (**38 tugas inti** `WF-001`–`WF-038` + **4 tugas opsional/bersyarat** `WF-OPT-01`–`WF-OPT-04`).<br>
Pembagian peran final: **Syahir (13 tugas solo)**, **Ramadan (11 tugas solo)**, **Bersama (14 tugas kolaboratif)** + 4 opsional.

| Milestone | Nama Milestone | Fase | Work ID | PIC Utama | Status | Catatan Progres / Gate |
|---|---|---|---|---|---|---|
| `M0` | Project Foundation Locked | Fase 1 | `WF-001`–`WF-003` | Bersama (Koord: Syahir) | `In Progress` | Persetujuan Syahir tercatat (`24 Nov 2026`) & branch `master`/`syahir`/`ramadan` terpublikasi; **menunggu persetujuan Ramadan** & verifikasi clone `ramadan`. |
| `M1` | Technical Plan Approved | Fase 2 | `WF-004`–`WF-006` | Syahir & Ramadan | `In Progress` | Draf `WF-004`/`WF-006` ([ARCHITECTURE.md](./ARCHITECTURE.md) v0.3 + [BASELINE_SAFETY_AUDIT.md](./BASELINE_SAFETY_AUDIT.md)) & draf awal `WF-005` ([DATA_DICTIONARY.md](./DATA_DICTIONARY.md) v0.2) tersedia; menunggu penutupan `M0` & *cross-review* Ramadan. |
| `M2` | Data Sources Collected & Verified | Fase 3 | `WF-007`–`WF-009` | Ramadan | `In Progress` | Inventaris awal 8 berkas `data/raw/` terdokumentasi di `DATA_DICTIONARY.md`; menunggu review Ramadan, kelengkapan URL asal & `M1`. |
| `M3` | Raw Data Audited & Prepared | Fase 4–5 | `WF-010`–`WF-014` | Ramadan | `In Progress` | Audit fisik awal *read-only* `WF-010`–`WF-011` tersedia di `DATA_DICTIONARY.md` untuk direview Ramadan; `WF-012`–`WF-014` belum dimulai. |
| `M4` | API & Model Configuration Validated | Fase 6 *(Paralel)* | `WF-015`–`WF-017` | Syahir | `In Progress` | `.env` lokal aktif & terabaikan Git, `.env.example` bersih placeholder, tes live via `.env` lulus (`gemini-3.5-flash-lite` & `openai/gpt-oss-20b`), rekomendasi `OD-02` (`LAYAK BERSYARAT`) tersusun; **menunggu `M0`/`M1` & persetujuan `OD-02` Ramadan**. |
| `M5` | RAG Pipeline Operational & Corpus Frozen | Fase 7 | `WF-018`–`WF-021` | Syahir & Ramadan | `In Progress` | **Baseline v1.3 FREEZE** (`prompt_v1.3`, paritas `SafetyGuard` 2×2 & `max_tokens=1400`) terverifikasi + modul RAG teruji pada *fixture*; **menunggu handoff korpus Ramadan (`WF-018`) & `M4`**. |
| `M6` | MVP Chatbot Functional | Fase 8 | `WF-022`–`WF-026` | Syahir (QA: Ramadan) | `In Progress` | `app.py` (basis Multazam) lolos `AppTest`, server lokal `HTTP 200 ok`, **37/37 unit/regresi test lulus**, & **50/50 EV-50 offline PASS (`S3=29/29`, `FP=0`, `FN=0`)**; **menunggu `M5` (korpus *frozen*) & QA lintas perangkat Ramadan (`WF-026`)**. |
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
| 1. `PRD.md` v0.3 menjadi acuan | Menunggu persetujuan Ramadan | [PRD.md](./PRD.md) v0.3 **disetujui Syahir** (`24 Nov 2026`); menunggu konfirmasi Ramadan. |
| 2. `TEAM_WORKFLOW.md` memuat peran final & aturan Git | Menunggu persetujuan Ramadan | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) v0.5 **disetujui Syahir** (`24 Nov 2026`); menunggu konfirmasi Ramadan. |
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
| `WF-001` | Review & penguncian acuan `PRD.md` v0.3 | Bersama (Koord: Syahir) | Ramadan | `M0` | `In Progress` | [PRD.md](./PRD.md) (Draft v0.3) | Disetujui Syahir (`24 Nov 2026`); *Awaiting Ramadan Approval*. |
| `WF-002` | Persetujuan workflow, peran final & Git strategy | Bersama (Koord: Syahir) | Ramadan | `M0` | `In Progress` | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (Draft v0.5) | Disetujui Syahir (`24 Nov 2026`); *Awaiting Ramadan Approval*. |
| `WF-003` | Inisiasi `TODO.md`, konvensi folder, `.gitignore` & bootstrap branch Git | Bersama (Koord: Syahir) | Ramadan | `M0` | `In Progress` | [TODO.md](./TODO.md), `../.gitignore`, commit `c870f71` (`master`/`syahir`/`ramadan`) | Branch `master`/`syahir`/`ramadan` terpublikasi di GitHub (`c870f71`); menunggu verifikasi clone & akses branch `ramadan` oleh Ramadan. |

### Fase 2 — Technical Planning & Architecture Design (`M1`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-004` | Penyusunan `ARCHITECTURE.md` (RAG & LangChain selektif) | Member A (Syahir) | Member B (Ramadan) | `M1` | `In Progress` | [ARCHITECTURE.md](./ARCHITECTURE.md) (Draft v0.3, Bag. 1–10 & 13) | Draf teknis lengkap oleh Syahir + revisi paritas `SafetyGuard` 2×2 & Baseline v1.3 (`57cbf57`); menunggu penutupan `M0` & *cross-review* Ramadan sebelum `Completed`. |
| `WF-005` | Penetapan kontrak skema metadata & chunk korpus | Member B (Ramadan) | Member A (Syahir) | `M1` | `In Progress` | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 1 & [ARCHITECTURE.md](./ARCHITECTURE.md) Bag. 8 | Draf kontrak awal tersedia (belum dikunci sepihak); menunggu review/persetujuan final Ramadan & penutupan `M0`. |
| `WF-006` | Desain protokol safety darurat & skema log reproducibility | Member A (Syahir) | Member B (Ramadan) | `M1` | `In Progress` | [ARCHITECTURE.md](./ARCHITECTURE.md) (Draft v0.3, Bag. 11–12) & [BASELINE_SAFETY_AUDIT.md](./BASELINE_SAFETY_AUDIT.md) | Protokol keselamatan, pre/post-check 2×2, skema log JSONL (`prompt_version`), & uji FP/FN `WF-023` (`37/37` + `50/50` EV-50 offline) selesai; menunggu penutupan `M0` & *cross-review* Ramadan sebelum `Completed`. |

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
| `WF-015` | Setup lingkungan & pengelolaan API key aman (`.env.example`) | Member A (Syahir) | Member B (Ramadan) | `M4` | `In Progress` | `.env.example` (placeholder bersih), `.gitignore`, `requirements.txt`, `src/config.py`, `src/schemas.py` | Keamanan terverifikasi (`.env` aktif & diabaikan Git, 0 kebocoran di repo/log/riwayat Git, 5/5 test keamanan lulus); menunggu `M0`/`M1` & *cross-review* Ramadan sebelum `Completed`. |
| `WF-016` | Pengujian aktual Gemini API (utama) & Groq API (cadangan) | Member A (Syahir) | Member B (Ramadan) | `M4` | `In Progress` | `scripts/test_api.py`, `logs/api_test_results.jsonl` + verifikasi ulang via `.env` lokal | **Teruji live via `.env` (27 Nov):** Gemini `gemini-3.5-flash-lite` sukses (`2.5–7.3s`, *fixed sampling defaults*), `gemini-3.8-flash` 503, `gemini-2.5-*` 404; Groq `openai/gpt-oss-20b` sukses (`1.5–2.1s`), `qwen/qwen3.8-27b` sukses (`1.4–2.1s`), `llama-3.*` 404. Menunggu *cross-review* Ramadan & `M0`/`M1`. |
| `WF-017` | Penetapan model spesifik & konfigurasi terkendali (`OD-02`) | Member A (Syahir) | Member B (Ramadan) | `M4` | `In Progress` | Rekomendasi `OD-02` di Bag. 5.2, [BASELINE_SAFETY_AUDIT.md](./BASELINE_SAFETY_AUDIT.md) & [context_windows.md](./context_windows.md) v0.14 | **Keputusan sementara (`LAYAK BERSYARAT`, belum dikunci):** Primary `gemini-3.5-flash-lite` + Fallback `openai/gpt-oss-20b` (catatan: Gemini memakai *fixed sampling defaults* sehingga `temperature` diabaikan; eksperimen wajib model/parameter identik & `allow_fallback=False`). Menunggu persetujuan Ramadan. |

### Fase 7 — Corpus Preparation, RAG Development & Corpus Freeze (`M5`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-018` | Chunking korpus & penyusunan `corpus_manifest` berversi | Member B (Ramadan) | Member A (Syahir) | `M5` | `Not Started` | Dataset *chunk* ber-metadata & `corpus_manifest` berversi | Menunggu `M3` (`WF-012`, `WF-014`); koordinasi integrasi bersama Syahir. |
| `WF-019` | Implementasi indeks retrieval & pipeline RAG (LangChain selektif) | Member A (Syahir) | Member B (Ramadan) | `M5` | `In Progress` | `src/retrieval/retriever.py`, `src/llm/prompts.py` (`prompt_v1.3`), `src/llm/client.py`, `src/pipeline/chat_service.py`, `tests/test_safety_v1_3_suite.py` | Paritas instruksi dasar `prompt_v1.3`, `SafetyGuard` 2×2, & `max_tokens=1400` dengan Baseline terverifikasi + teruji pada *fixture* korpus sintetis & *mock* LLM; **menunggu handoff `WF-018` (`data/processed/`) & `M4`** untuk integrasi korpus nyata & kalibrasi `TD-03`. |
| `WF-020` | Implementasi jalur Baseline LLM (tanpa retrieval) | Member A (Syahir) | Member B (Ramadan) | `M5` | `In Progress` | `src/llm/prompts.py` (`prompt_v1.3` + `prompt_v1.2`), `src/config.py` (`max_tokens=1400`), `src/pipeline/chat_service.py` (`mode="baseline"`) | **FREEZE Baseline v1.3** (`LAYAK BERSYARAT`, commit `57cbf57`): paritas 2×2 lulus, `37/37` test & `50/50` EV-50 offline PASS, live log `#48`–`#60` (`prompt_v1.2`) & `#73`–`#77` (`prompt_v1.3`); menunggu penguncian final `OD-02` (`WF-017`). |
| `WF-021` | Verifikasi kualitas retrieval, kesiapan Baseline & Corpus Freeze | Bersama (Koord: Ramadan) | Kedua anggota | `M5` | `Not Started` | Catatan uji internal & persetujuan `corpus_v1.0-frozen` | Menunggu `WF-018`, `WF-019`, `WF-020`. |

### Fase 8 — Streamlit Integration & Safety Implementation (`M6`)

| Work ID | Nama Pekerjaan | PIC | Reviewer | Milestone | Status | Referensi Output / Bukti | Blocker / Catatan |
|---|---|---|---|---|---|---|---|
| `WF-022` | Pengembangan antarmuka chat Streamlit lokal & transparansi UI | Member A (Syahir) | Member B (Ramadan) | `M6` | `In Progress` | `app.py` (adaptasi starter Multazam), `requirements.txt`, `tests/test_app_multazam_integration.py` | Fix P0 live Baseline + verifikasi `AppTest` & **37/37 test lulus** (`57cbf57`): invalidasi cache `.env`/manifest via mtime, auto-default Baseline saat korpus belum ada, badge mode & tombol *Bersihkan Riwayat Chat*; menunggu `M5` & QA Ramadan (`WF-026`). |
| `WF-023` | Implementasi protokol darurat akut, abstention & ambiguitas | Member A (Syahir) | Member B (Ramadan) | `M6` | `In Progress` | `src/safety/guard.py`, `scripts/run_safety_regression.py`, `tests/safety_suite_ev50.py`, `tests/test_safety_v1_3_suite.py` | Pre-check kontekstual/slang & post-check S3 zero-tolerance aktif identik 2×2; **50/50 EV-50 offline PASS (`S3=29/29`, `FP=0`, `FN=0`)** + regresi kalibrasi genset/CO, tenggelam sadar vs tidak bernapas normal, & prediksi; menunggu integrasi `M5` & review Ramadan. |
| `WF-024` | Implementasi error handling & fallback Groq API | Member A (Syahir) | Member B (Ramadan) | `M6` | `In Progress` | `src/schemas.py`, `src/llm/client.py`, `src/pipeline/chat_service.py` | Klasifikasi `config_error` terpisah dari `network_error`/`rate_limit`/`timeout`/`provider_error` & pemisahan pesan korpus belum tersedia vs error indeks; menunggu integrasi `M5` & review Ramadan. |
| `WF-025` | Implementasi logger reproducibility & evaluasi (`FR-11`) | Member A (Syahir) | Member B (Ramadan) | `M6` | `In Progress` | `src/logging/eval_logger.py`, `tests/test_pipeline_and_logging.py` | Skema JSONL 27 field terverifikasi pada request live E2E Baseline (0 kebocoran kredensial, masking PII demo, `validate_experiment_logs` lulus); menunggu integrasi `M5`. |
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
| `WF-030` | Eksekusi eksperimen Kondisi A (Baseline LLM tanpa retrieval) | Member A (Syahir) | Member B (Ramadan) | `M8` | `Not Started` | `scripts/run_eval.py` *(runner siap & teruji mock)*; file log 30 respons belum dijalankan | Menunggu `M6`, `M7`, `WF-020` (model & 30 soal terkunci). |
| `WF-031` | Eksekusi eksperimen Kondisi B (SiagaBanjir RAG) & uji darurat | Member A (Syahir) | Member B (Ramadan) | `M8` | `Not Started` | `scripts/run_eval.py` *(runner siap & teruji mock)*; file log 30 respons belum dijalankan | Menunggu `M6`, `M7`, `WF-030` (model/parameter identik & korpus *frozen*). |
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
| **Member A (Syahir)** | LLM & Application Engineering | **Disetujui** | **Disetujui** | 24 Nov 2026 | Dikonfirmasi langsung oleh Syahir. |
| **Member B (Ramadan)** | Data & Knowledge Preparation | *Belum dicatat* | *Belum dicatat* | — | Menunggu konfirmasi langsung Ramadan untuk menutup `M0`. |

### 5.2 Catatan Keputusan & Open Decisions (`OD-01`–`OD-05`)
| Tanggal | ID / Topik | Status | Ringkasan Keputusan / Catatan | Dampak Dokumen |
|---|---|---|---|---|
| 24 Nov 2026 | Domain & keputusan inti tim | Final | Domain disetujui dosen; 2 mahasiswa; Gemini API utama & Groq cadangan; RAG + LangChain selektif; Streamlit lokal; 30 soal Baseline vs RAG; statistik BNPB bersyarat. | [PRD.md](./PRD.md) v0.3 |
| 24 Nov 2026 | Revisi pembagian peran final & Git bootstrap | Final (peran) / Bootstrap M0 | **Syahir (Member A): LLM & Application Engineering** (13 solo); **Ramadan (Member B): Data & Knowledge Preparation** (11 solo termasuk `WF-018` koordinasi dgn Syahir & QA `WF-026`); 14 bersama. Commit fondasi `c870f71` terpublikasi di `master`, `syahir`, `ramadan`. | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) v0.5, [TODO.md](./TODO.md) v0.5, [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) v0.2, [context_windows.md](./context_windows.md) v0.4 |
| 24 Nov 2026 | Draf Arsitektur RAG, Safety Protocol & Logging (`WF-004`, `WF-006`) | Draf v0.2 *(menunggu review Ramadan & M0)* | Rancangan teknis RAG + LangChain selektif, paritas instruksi dasar Baseline vs RAG (`prompt_version`), bypass darurat akut (112 bergantung wilayah, Basarnas 115), batas verifikasi sitasi, isolasi `<retrieved_context>` sebagai mitigasi berlapis, skema log JSONL (contoh sintetis `2026-11-24`), & kewajiban uji FP/FN `WF-023` (`TD-01`–`TD-06` terbuka). | [ARCHITECTURE.md](./ARCHITECTURE.md) v0.2, [TODO.md](./TODO.md) v0.6, [context_windows.md](./context_windows.md) v0.5 |
| 24 Nov 2026 | Peta Dependensi 42 Work ID & Aturan Operasional Handoff | Aktif *(Acuan Eksekusi)* | Penambahan *Execution Readiness & Dependency Map* 42 Work ID (`Bagian 6`) dan penyelarasan aturan operasional *handoff*, *cross-review*, pencatatan keputusan WhatsApp → repo, serta *non-claim rule*. | [TODO.md](./TODO.md) v0.6, [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) v0.6, [context_windows.md](./context_windows.md) v0.5 |
| 28 Nov 2026 | Final Project Audit, Baseline v1.3 FREEZE & Model Verdict (`OD-02`) | **FREEZE Baseline v1.3** *(LAYAK BERSYARAT — Siap PR Cross-Review Ramadan)* | Audit lintas modul, log live `#48`–`#60` (`prompt_v1.2`) & `#73`–`#77` (`prompt_v1.3`), serta kalibrasi akhir: (1) genset belum menyala vs sedang menyala/gejala CO; (2) korban tenggelam sadar batuk/lemas (evaluasi medis segera) vs tidak bernapas normal & pemisahan rujukan medis vs SAR/evakuasi; (3) perbaikan FN `_PREDICTION_RULES` untuk `"Besok jam berapa daerah saya pasti banjir?"`; (4) paritas `SafetyGuard` pre/post-check 2×2 disinkronkan di [ARCHITECTURE.md](./ARCHITECTURE.md) v0.3. **Model Verdict:** `gemini-3.5-flash-lite` **LAYAK BERSYARAT** (*fixed sampling defaults* mengabaikan `temperature`, wajib didokumentasikan; menunggu persetujuan Ramadan `OD-02`). Hasil validasi: `compileall` OK, **37/37 unit test OK**, **50/50 EV-50 offline PASS (`S3=29/29`, `FP=0`, `FN=0`)**, `git diff --check` 0 error. | [ARCHITECTURE.md](./ARCHITECTURE.md) v0.3, [BASELINE_SAFETY_AUDIT.md](./BASELINE_SAFETY_AUDIT.md), [TODO.md](./TODO.md) v0.14, [context_windows.md](./context_windows.md) v0.14, `src/safety/guard.py`, `src/llm/prompts.py`, `tests/test_safety_v1_3_suite.py` |
| 28 Nov 2026 | Baseline Safety Hardening v1.2 → v1.3 (`prompt_v1.3`, `SafetyGuard` Pre/Post-Check, Suite EV-50) | Terverifikasi Offline (`36/36` unit test & `50/50` EV-50 offline; live API 0/50 belum dijalankan) | Audit end-to-end ([BASELINE_SAFETY_AUDIT.md](./BASELINE_SAFETY_AUDIT.md)) mengonfirmasi 15 celah P0/P1/P2 (slang darurat akut Indonesia, genset/CO, LPG, kabel jatuh, loteng tertutup, tenggelam tekan perut, campur pemutih+asam/amonia, anti-*false-reassurance* kendaraan tinggi/orang lain, batas medis/red flags, kelompok rentan, abstention hoaks/regulasi baru, *prompt leak*, serta demo pre/post-check Baseline). Diperbaiki dengan `prompt_v1.3` (`prompt_v1.2` dipertahankan di `PROMPT_REGISTRY`), `SafetyGuard` pre-check & post-check S3 zero-tolerance, paritas keselamatan identik di seluruh 2×2 (`mode=baseline|rag` × `run_context=demo|experiment`) di `ChatService` (perbedaan eksperimen hanya *retrieval* & sitasi, `allow_fallback=False` tetap terkunci), serta suite tambahan 50 skenario turunan `EV-01`–`EV-50` (`scripts/run_safety_regression.py --mode offline`: **50/50 PASS, S3=29/29, FP=0, FN=0**). Parameter Gemini tidak diubah. | [BASELINE_SAFETY_AUDIT.md](./BASELINE_SAFETY_AUDIT.md), [TODO.md](./TODO.md) v0.13, [context_windows.md](./context_windows.md) v0.13, `src/llm/prompts.py`, `src/safety/guard.py`, `src/pipeline/chat_service.py`, `src/config.py`, `.env.example`, `scripts/run_safety_regression.py`, `tests/` |
| 28 Nov 2026 | Targeted Safety Correction & QA v1.2 (`prompt_v1.2`) | Terverifikasi Live *(tanpa ubah PRD/scope)* | Audit 20 pengujian Baseline (`logs/demo_20261127.jsonl` #20–#39: **7 PASS, 7 PARTIAL, 6 FAIL**) menemukan 5 kegagalan P0 (urutan listrik sebelum jiwa/evakuasi saat air masuk rumah, teknik sepatu bot+tongkat di air mata kaki, saran naik atap/loteng & panggilan bantuan di urutan terakhir saat terjebak lantai dua, anjuran cabut kabel perangkat terendam & pemeriksaan teknisi sekadar "sebaiknya", klaim air sumur tercemar aman setelah dijernihkan & direbus) serta 6 temuan P1 (esai panjang pada input `"Banjir."`, mi instan remuk tanpa kompor, larangan mutlak dokumen asli, klaim "banyak penelitian" perilaku hewan, typo `BNBP`). Diperbaiki di `src/llm/prompts.py` (`prompt_v1.2`), `src/safety/guard.py` (pesan darurat terjebak, FN prediksi `"memastikan besok"`, penolakan pengumuman palsu `BNPB`), `src/config.py`, `.env.example`, `tests/test_response_quality.py`, dan `tests/test_safety_v1_2_regression.py` (12 uji regresi semantik wajib). Hasil: `compileall` lulus, **32/32 test lulus**, `AppTest` v1.2 lulus, 1 live Baseline terkontrol (`gemini-3.5-flash-lite`, `prompt_v1.2`, `4.69s`, 1.017 char) lulus prioritas 1→4. *Catatan:* `.env` lokal tidak disentuh; perlu pembaruan manual `PROMPT_VERSION=prompt_v1.2` & `LLM_MAX_TOKENS=1400`. | [TODO.md](./TODO.md) v0.12, [context_windows.md](./context_windows.md) v0.12, `src/llm/prompts.py`, `src/safety/guard.py`, `src/config.py`, `.env.example`, `tests/test_safety_v1_2_regression.py` |
| 28 Nov 2026 | Response Quality Improvement (`prompt_v1.1` & Paritas `max_tokens=1400`) | Terverifikasi Live *(tanpa ubah PRD/scope)* | Audit `logs/demo_20261127.jsonl` (#10–#14) menemukan pengulangan salam/disclaimer pada setiap giliran, *truncation* di tengah kalimat pada soal 3 fase (`max_tokens=768`), dan angka kedalaman air tanpa sumber (`15 cm`). Pembaruan di `src/llm/prompts.py` (`prompt_v1.1`), `src/config.py` & `.env.example` (`LLM_MAX_TOKENS=1400` identik untuk Baseline & RAG), `src/safety/guard.py` (darurat panel listrik terendam/percikan aktif), dan `tests/test_response_quality.py` (7 kasus regresi wajib). Hasil: **28/28 test lulus (`0.100s`)**, `AppTest` lulus, uji live multi-fase Baseline (`gemini-3.5-flash-lite`, `4.67s`, 2.381 char) menghasilkan 3 fase utuh tanpa salam/disclaimer berulang dan keselamatan listrik konservatif. *Catatan:* `.env` lokal tidak diubah otomatis; perlu pembaruan manual `LLM_MAX_TOKENS=1400` & `PROMPT_VERSION=prompt_v1.1` oleh pengguna. | [TODO.md](./TODO.md) v0.11, [context_windows.md](./context_windows.md) v0.11, `src/llm/prompts.py`, `src/config.py`, `.env.example`, `src/safety/guard.py`, `tests/test_response_quality.py` |
| 28 Nov 2026 | Debug & Fix P0 Live Chat Baseline Streamlit | Terverifikasi Live *(OD-02 tetap usulan)* | Akar masalah dari log `demo_20261127.jsonl`: `.env` lokal masih `TBD_AFTER_WF016`, `@st.cache_resource` tidak memantau mtime `.env`, `config_error` disamarkan sebagai error koneksi/kuota generik, dan riwayat error RAG sebelumnya tercampur tanpa badge mode. Diperbaiki di `app.py`, `src/config.py`, `src/schemas.py`, `src/llm/client.py`, `src/pipeline/chat_service.py`, `src/safety/guard.py`, serta `.env` lokal sementara (`gemini-3.5-flash-lite` / `openai/gpt-oss-20b`; `.env.example` tetap `TBD_AFTER_WF016`). Hasil: **24/24 test lulus**, live Streamlit `AppTest` Baseline (`4.55s`, 2.693 char) & `ChatService` (`2.93s`, 2.483 char) lulus, RAG tetap menunggu korpus Ramadan. | [TODO.md](./TODO.md) v0.10, [context_windows.md](./context_windows.md) v0.10, `app.py`, `src/`, `tests/` |
| 27 Nov 2026 | Finalisasi Track Syahir, Verifikasi `.env`, Live E2E Baseline & Rekomendasi `OD-02` | Siap Cross-Review *(OD-02 belum dikunci)* | Keamanan `.env` terverifikasi (`.env` aktif & diabaikan `.gitignore`, `.env.example` bersih placeholder, 0 kebocoran di repo/log/riwayat Git). Live probe via `.env` lulus untuk Gemini `gemini-3.5-flash-lite` & Groq `openai/gpt-oss-20b`; E2E Baseline `ChatService` lulus (`1.79s`, 1.215 char Bahasa Indonesia, JSONL 27 field bebas kredensial); Streamlit `HTTP 200 ok`, `AppTest` lulus, dan **22/22 unit/smoke test lulus**. Rekomendasi `OD-02`: Primary `gemini-3.5-flash-lite` (catatan: *fixed sampling defaults* mengabaikan `temperature`) + Fallback `openai/gpt-oss-20b`; menunggu persetujuan Ramadan. | [TODO.md](./TODO.md) v0.9, [context_windows.md](./context_windows.md) v0.8, `logs/api_test_results.jsonl` |
| 24 Nov 2026 | Sprint Plan 7 Hari & Context Recovery | Siap Teknis *(target operasional relatif)* | Jadwal paralel Hari 1–7 untuk 38 tugas inti + catatan bottleneck/pemangkasan fitur opsional serta pembuatan `context_windows.md`. | [TODO.md](./TODO.md) v0.4, [context_windows.md](./context_windows.md) v0.3 |
| 24 Nov 2026 | Draf Kontrak Metadata (`WF-005`) & Physical Audit *Read-Only* (`WF-007`–`WF-011`) | Draf Awal *(review Ramadan)* | Audit fisik seluruh 8 berkas `data/raw/`: PDF BNPB 2018 100% *born-digital* (no OCR), TXT SE BNPB 4/2026 layak perlu *cleaning*, 2 Excel BNPB ditolak (bukan khusus banjir), 1 Excel kab/kota selisih total (`1.428` vs `1.420`), 3 Excel layak bersyarat (`FR-12` tetap opsional). | [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) v0.2, [TODO.md](./TODO.md) v0.4 |
| — | `OD-01` Judul akademik final | Open | Ditetapkan pada `WF-035` (`M9`). | `PRD.md`, Poster |
| — | `OD-02` Model spesifik & konfigurasi API | Open *(Rekomendasi Syahir siap review)* | Usulan berbasis bukti `WF-016`: Primary `gemini-3.5-flash-lite` (*fixed sampling defaults*, `temperature` diabaikan) & Fallback `openai/gpt-oss-20b`; eksperimen wajib model/parameter identik & `allow_fallback=False`. Menunggu konfirmasi Ramadan pada `WF-017`. | `ARCHITECTURE.md` |
| — | `OD-03` Daftar sumber final & kelayakan BNPB | Open | Ditetapkan setelah *data collection* & *physical audit* pada `WF-014` (`M3`). | `DATA_DICTIONARY.md` |
| — | `OD-04` Jadwal kalender spesifik *milestone* | Open *(parsial)* | Pembagian kerja & Sprint 7 Hari selesai; tanggal kalender UAS menunggu konfirmasi tim. | `TEAM_WORKFLOW.md`, `TODO.md` |
| — | `OD-05` Rubrik & ambang evaluasi | Open | Ditetapkan setelah penyusunan 30 pertanyaan uji pada `WF-029` (`M7`). | `EVALUATION_PLAN.md` |

---

## 6. Execution Readiness & Dependency Map (Seluruh 42 Work ID)

Bagian ini menjadi acuan operasional bagi **Member A (Syahir)** dan **Member B (Ramadan)** untuk mengetahui tugas mana yang dapat dikerjakan mandiri, paralel, membutuhkan koordinasi, atau wajib menunggu *handoff*/*Exit Gate*.

### 6.1 Definisi Tipe Dependensi & Status Kesiapan Eksekusi

**4 Tipe Dependensi (`Tipe Dep`):**
- `INDEPENDENT` — PIC dapat memulai dan menyelesaikan sendiri setelah *hard prerequisite* terpenuhi.
- `PARALLEL-COORDINATION` — Dapat dikerjakan bersamaan dengan jalur partner; kontrak/parameter tertentu wajib disinkronkan sebelum finalisasi atau integrasi.
- `HANDOFF-BLOCKED` — Tidak dapat dimulai sebelum artefak *handoff* dari PIC sebelumnya tersedia dan diterima reviewer.
- `JOINT` — Membutuhkan keputusan, persetujuan, atau pekerjaan bersama kedua anggota (`Syahir` & `Ramadan`).

**4 Status Kesiapan Eksekusi (`Readiness` — terpisah dari `Progress Status` di Bagian 4):**
- `Ready` — Seluruh *hard prerequisite* terpenuhi; PIC dapat langsung mengeksekusi.
- `Ready-Coordination` — Draf awal (*provisional*) atau tinjauan di branch pribadi dapat langsung dikerjakan, namun perubahan status menjadi `Completed` menunggu sinkronisasi kontrak/penutupan *gate* dan *cross-review*.
- `Blocked` — Terkunci menunggu *Exit Gate*, artefak *handoff*, atau kondisi bersyarat (*lihat kolom Blocked Reason & Pembuka*).
- `Joint-Gate` — Gerbang persetujuan/keputusan bersama yang terbuka hanya setelah kedua anggota menyelesaikan bagiannya.

### 6.2 Peta Jalur Kritis (*Critical Path*) & Jalur Paralel

- **Jalur Kritis (*Critical Path*):** `M0` (`WF-001`–`003`) → `M1` (`WF-004`–`006`) → `M2` (`WF-007`–`008`) → `M3` (`WF-010`, `WF-012`–`014`) → `M5` (`WF-018`–`021`) → `M6` (`WF-022`–`026`) → `M8` (`WF-030`–`034`) → `M9` (`WF-035`–`038`), dengan **cabang paralel kritis** `M5` → `M7` (`WF-027`–`029`) → `M8` yang bertemu di `WF-030`.
- **4 Jalur Paralel yang Diizinkan:**
  1. **Saat M0–M1 (*Provisional*):** Syahir menyempurnakan draf `WF-004`/`WF-006` (`ARCHITECTURE.md`) **paralel** dengan Ramadan meninjau `WF-005` & audit awal `WF-007`–`WF-011` (`DATA_DICTIONARY.md`); `M1` tetap terkunci hingga `M0` lulus *Exit Gate*.
  2. **Pasca-`M1`:** Syahir mengerjakan `M4` (`WF-015`→`WF-016`→`WF-017`) **paralel penuh** dengan Ramadan mengerjakan `M2`–`M3` (`WF-007`–`WF-014`); bertemu di `M5`.
  3. **Pasca-`M5` (*Corpus Freeze*):** Syahir mengerjakan `M6` (`WF-022`–`WF-025`, lalu QA Ramadan `WF-026`) **paralel** dengan penyusunan `M7` (`WF-027`–`WF-029`); bertemu di `M8`.
  4. **Penilaian Independen (`WF-032`):** Syahir dan Ramadan menilai 30 Baseline + 30 RAG + uji darurat secara terpisah sebelum rekonsiliasi `WF-033`.

### 6.3 Ringkasan Siap Dikerjakan Sekarang (*Actionable Now*) & Daftar *Blocked* *(per 28 Nov 2026)*

**Rekap Kesiapan 42 Work ID:** `0 Ready` | `3 Joint-Gate` | `8 Ready-Coordination` | `31 Blocked` *(Progress aktual: `20 In Progress` [11 `WF-001`–`011` + 9 implementasi track Syahir `WF-015`–`017`, `WF-019`–`020`, `WF-022`–`025` sudah dipush di `origin/syahir` `57cbf57` dan siap cross-review], `22 Not Started`, `0 Completed`)*.

| Kelompok | Status Kesiapan | Work ID | Aksi Konkret / Pembuka |
|---|---|---|---|
| **Bersama (`M0`)** | `Joint-Gate` (3) | `WF-001`, `WF-002`, `WF-003` | Persetujuan Syahir sudah tercatat (`24 Nov 2026`) & branch `master`/`syahir`/`ramadan` sudah dipublikasi (`c870f71`). **Pembuka `M0`:** Ramadan mencatat persetujuan di Bag. 5.1 & mengonfirmasi clone/akses branch `ramadan`. |
| **Syahir (`Member A`)** | `Ready-Coordination` (2) | `WF-004`, `WF-006` | [ARCHITECTURE.md](./ARCHITECTURE.md) v0.3 & [BASELINE_SAFETY_AUDIT.md](./BASELINE_SAFETY_AUDIT.md) sudah di-commit/push di `origin/syahir` (`57cbf57`); **tinggal buka PR `syahir → master`** dan ajukan *cross-review* ke Ramadan. |
| **Ramadan (`Member B`)** | `Ready-Coordination` (6) | `WF-005`, `WF-007`, `WF-008`, `WF-009`, `WF-010`, `WF-011` | Review & finalisasi kontrak metadata (`WF-005`) di [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) Bag. 1; lengkapi URL asal `SRC-EDU-001` & BNPB, putuskan kebutuhan sumber terbaru (`WF-007`–`009`), dan konfirmasi hasil audit fisik awal (`WF-010`–`011`). |
| **Syahir — `Blocked`** | `Blocked` (13) | `WF-015`–`017`, `WF-019`–`020`, `WF-022`–`025`, `WF-030`–`031`, `WF-OPT-02`, `WF-OPT-04` | `WF-015`–`017` dibuka oleh `M0`+`M1`; `WF-019`–`020` oleh `WF-018`+`M4`; `WF-022`–`025` oleh `M5`; `WF-030`–`031` oleh `M6`+`M7`; `WF-OPT-02` oleh `WF-OPT-01`; `WF-OPT-04` hanya jika `M8` selesai lebih awal tanpa ganggu `M9`. |
| **Ramadan — `Blocked`** | `Blocked` (7) | `WF-012`–`014`, `WF-018`, `WF-026`, `WF-OPT-01`, `WF-OPT-03` | `WF-012`–`014` dibuka oleh `WF-005`+`WF-010`; `WF-018` oleh `M3`+koordinasi Syahir; `WF-026` oleh `WF-022`–`025` (`H5`); `WF-OPT-01` oleh `M6`+`WF-011` Layak; `WF-OPT-03` oleh `WF-OPT-02`. |
| **Bersama — `Blocked`** | `Blocked` (11) | `WF-021`, `WF-027`–`029`, `WF-032`–`038` | `WF-021` dibuka oleh `WF-018`–`020`; `WF-027`–`029` oleh `M5`; `WF-032`–`034` oleh `WF-030`–`031`+`WF-029`; `WF-035`–`038` oleh `M8`+`M6`. |

### 6.4 Tabel Dependency Map Lengkap (42 Work ID — DAG Tanpa Siklus)

| Work ID | PIC | Tipe Dep | Hard Prerequisite | Readiness | Paralel Dengan | Handoff / Cross-Review Gate | Blocked Reason & Pembuka |
|---|---|---|---|---|---|---|---|
| `WF-001` | Bersama (Koord: Syahir) | `JOINT` | `PRD.md` v0.3 | `Joint-Gate` | `WF-002`, `WF-003` | Rev Ramadan; Gate `M0` | Syahir setuju (`24 Nov`); **terbuka jika Ramadan mencatat persetujuan di Bag. 5.1**. |
| `WF-002` | Bersama (Koord: Syahir) | `JOINT` | `WF-001` | `Joint-Gate` | `WF-001`, `WF-003` | Rev Ramadan; Gate `M0` | Syahir setuju (`24 Nov`); **terbuka jika Ramadan mencatat persetujuan di Bag. 5.1**. |
| `WF-003` | Bersama (Koord: Syahir) | `JOINT` | `WF-002` | `Joint-Gate` | `WF-001`, `WF-002` | Rev Ramadan; Gate `M0` | Branch `master`/`syahir`/`ramadan` aktif (`c870f71`); **terbuka jika Ramadan verifikasi clone `ramadan`**. |
| `WF-004` | Member A (Syahir) | `PARALLEL-COORDINATION` | `M0` *(draf provisional di branch `syahir`)* | `Ready-Coordination` | `WF-005`, `WF-006` | Handoff `H1` → Rev Ramadan; Gate `M1` | Draf `ARCHITECTURE.md` v0.2 siap review; `Completed` menunggu `M0` lulus & *cross-review* Ramadan. |
| `WF-005` | Member B (Ramadan) | `PARALLEL-COORDINATION` | `M0` *(sinkron dgn draf `WF-004`)* | `Ready-Coordination` | `WF-004`, `WF-006` | Handoff `H1` → Rev Syahir; Gate `M1` | Draf kontrak awal tersedia di `DATA_DICTIONARY.md` Bag. 1; `Completed` menunggu review Ramadan, `M0`, & *cross-review* Syahir. |
| `WF-006` | Member A (Syahir) | `PARALLEL-COORDINATION` | `WF-004`, `M0` | `Ready-Coordination` | `WF-004`, `WF-005` | Handoff `H1` → Rev Ramadan; Gate `M1` | Draf safety & log (`ARCHITECTURE.md` Bag. 11–12) siap review; `Completed` menunggu `M0` & *cross-review* Ramadan. |
| `WF-007` | Member B (Ramadan) | `INDEPENDENT` | `M1` *(review awal provisional tersedia)* | `Ready-Coordination` | `WF-008`, `WF-009`, `M4` (pasca-`M1`) | Rev Syahir; Gate `M2` | Inventaris awal 2 berkas edukasi siap ditinjau Ramadan; penutupan menunggu `M1` & review Syahir. |
| `WF-008` | Member B (Ramadan) | `INDEPENDENT` | `WF-007`, `WF-005` | `Ready-Coordination` | `WF-007`, `WF-009`, `M4` (pasca-`M1`) | Rev Syahir; Gate `M2` | Lengkapi URL resmi `SRC-EDU-001` secara provisional; finalisasi menunggu `WF-005` & `M1`. |
| `WF-009` | Member B (Ramadan) | `INDEPENDENT` | `M1` | `Ready-Coordination` | `WF-007`, `WF-008`, `M4` (pasca-`M1`) | Rev Syahir; Gate `M2` | Inventaris awal 6 Excel BNPB siap direview (lengkapi URL DIBI); finalisasi menunggu `M1`. |
| `WF-010` | Member B (Ramadan) | `INDEPENDENT` | `M2` (`WF-007`, `WF-008`) | `Ready-Coordination` | `WF-011`, `M4` (pasca-`M1`) | Rev Syahir; bagian `M3` | Audit fisik awal *read-only* tersedia di `DATA_DICTIONARY.md` Bag. 3; `Completed` menunggu `M2` & konfirmasi Ramadan/Syahir. |
| `WF-011` | Member B (Ramadan) | `INDEPENDENT` | `WF-009` | `Ready-Coordination` | `WF-010`, `M4` (pasca-`M1`) | Rev Syahir; gerbang kelayakan `M-OPT` | Audit fisik awal 6 Excel tersedia di `DATA_DICTIONARY.md` Bag. 4; `Completed` menunggu `WF-009`/`M2` & konfirmasi. |
| `WF-012` | Member B (Ramadan) | `INDEPENDENT` | `WF-010`, `WF-005` | `Blocked` | `M4` (`WF-015`–`WF-017`) | Rev Syahir; bagian `H2`/`M3` | Menunggu `WF-005` (kontrak metadata final) & `WF-010` (keputusan audit & tambahan sumber) lulus review. |
| `WF-013` | Member B (Ramadan) | `INDEPENDENT` | `WF-012` | `Blocked` | `M4` (`WF-015`–`WF-017`) | Rev Syahir; bagian `H2`/`M3` | Menunggu output teks bersih di `data/processed/` hasil `WF-012`. |
| `WF-014` | Member B (Ramadan) | `INDEPENDENT` | `WF-010`, `WF-011`, `WF-012`, `WF-013` | `Blocked` | `M4` (`WF-015`–`WF-017`) | Handoff `H2` → Rev Syahir; tutup `M3` & `OD-03` | Menunggu `WF-010`–`WF-013` tuntas untuk mengunci daftar sumber final (`OD-03`). |
| `WF-015` | Member A (Syahir) | `INDEPENDENT` | `M1`, `WF-003` | `Blocked` | `M2`–`M3` (`WF-007`–`WF-014`) | Rev Ramadan; bagian `M4` | Menunggu *Exit Gate* `M0` & `M1` sebelum membuat `.env.example` dan modul konfigurasi. |
| `WF-016` | Member A (Syahir) | `INDEPENDENT` | `WF-015` | `Blocked` | `M2`–`M3` (`WF-007`–`WF-014`) | Rev Ramadan; bagian `M4` | Menunggu `WF-015` selesai & API key lokal Gemini/Groq siap di `.env`. |
| `WF-017` | Member A (Syahir) | `INDEPENDENT` | `WF-016` | `Blocked` | `M2`–`M3` (`WF-007`–`WF-014`) | Handoff `H3` → Rev Ramadan; tutup `M4` & `OD-02` | Menunggu bukti tes API aktual `WF-016` (model dilarang dikunci sebelum tes). |
| `WF-018` | Member B (Ramadan) | `PARALLEL-COORDINATION` | `M3` (`WF-012`, `WF-014`), `WF-005` | `Blocked` | Kerangka `WF-020` (pasca-`M4`) | Handoff `H4` (koord. integrasi dgn Syahir) → Rev Syahir | Menunggu `M3` selesai (`data/processed/` bersih + `DATA_DICTIONARY.md` final) & kesepakatan param *chunk* (`TD-03`). |
| `WF-019` | Member A (Syahir) | `HANDOFF-BLOCKED` | `WF-018` (`H4`), `M4` (`WF-017`) | `Blocked` | — | Rev Ramadan; bagian `M5` | Menunggu *handoff* `chunks.jsonl` & `corpus_manifest.json` (`WF-018`) serta penutupan `M4`. |
| `WF-020` | Member A (Syahir) | `INDEPENDENT` | `M4` (`WF-017`), `WF-019` | `Blocked` | Persiapan modul pasca-`M4` | Rev Ramadan; bagian `M5` | Menunggu `M4` (`WF-017`) & penyelarasan `prompt_version`/parameter identik dengan `WF-019`. |
| `WF-021` | Bersama (Koord: Ramadan) | `JOINT` | `WF-018`, `WF-019`, `WF-020` | `Blocked` | — | Persetujuan bersama; tutup `M5` (*corpus freeze*) | Menunggu `WF-018`, `WF-019`, dan `WF-020` operasional untuk uji internal & penguncian `corpus_v1.0-frozen`. |
| `WF-022` | Member A (Syahir) | `INDEPENDENT` | `M5` (`WF-019`), `WF-004` | `Blocked` | `M7` (`WF-027`–`WF-029`) | Rev Ramadan; bagian `M6` | Menunggu `M5` (*pipeline* RAG operasional & korpus *frozen*). |
| `WF-023` | Member A (Syahir) | `INDEPENDENT` | `WF-006`, `WF-019`, `WF-022` | `Blocked` | `WF-024`, `WF-025`, `M7` | Rev Ramadan; bagian `M6` (+ uji FP/FN Safety Guard) | Menunggu `WF-022` & finalisasi desain keselamatan `WF-006`. |
| `WF-024` | Member A (Syahir) | `INDEPENDENT` | `WF-022`, `M4` | `Blocked` | `WF-023`, `WF-025`, `M7` | Rev Ramadan; bagian `M6` | Menunggu `WF-022` & konfigurasi cadangan Groq dari `M4`. |
| `WF-025` | Member A (Syahir) | `INDEPENDENT` | `WF-006`, `WF-019`, `WF-020` | `Blocked` | `WF-022`–`WF-024`, `M7` | Rev Ramadan; bagian `M6` | Menunggu `WF-006` (skema log final) & `M5` (`WF-019`, `WF-020`). |
| `WF-026` | Member B (Ramadan) | `HANDOFF-BLOCKED` | `WF-022`, `WF-023`, `WF-024`, `WF-025` | `Blocked` | Finalisasi `M7` | Handoff `H5` (Syahir → Ramadan QA) → Rev Syahir; tutup `M6` | Menunggu seluruh komponen MVP (`WF-022`–`WF-025`) diserahkan Syahir untuk QA independen lintas perangkat. |
| `WF-027` | Bersama | `JOINT` | `M5` (*corpus frozen*) | `Blocked` | `M6` (`WF-022`–`WF-025`) | Silang (A ↔ B); bagian `M7` | Menunggu `M5` (`corpus_v1.0-frozen`) agar 30 soal (10+10+5+5) + kasus darurat terjangkar korpus beku. |
| `WF-028` | Bersama | `JOINT` | `WF-027`, `M5` | `Blocked` | `M6` (`WF-022`–`WF-025`) | Silang (A ↔ B); bagian `M7` | Menunggu 30 pertanyaan uji (`WF-027`) dan manifest `M5`. |
| `WF-029` | Bersama (Koord: Ramadan) | `JOINT` | `WF-028` | `Blocked` | `WF-026` | Handoff `H6` (Persetujuan bersama); tutup `M7` & `OD-05` | Menunggu *ground truth* (`WF-028`) untuk mengunci `EVALUATION_PLAN.md` & rubrik sebelum eksperimen. |
| `WF-030` | Member A (Syahir) | `HANDOFF-BLOCKED` | `M6`, `M7` (`H6`), `WF-020` | `Blocked` | — | Audit log oleh Ramadan; bagian `M8` | Menunggu `M6` (MVP & logger lulus QA) dan `M7` (30 soal + rubrik terkunci). |
| `WF-031` | Member A (Syahir) | `INDEPENDENT` | `M6`, `M7`, `WF-030` | `Blocked` | — | Handoff `H7` → Audit log & korpus oleh Ramadan; bagian `M8` | Menunggu `WF-030` selesai agar Kondisi B berjalan pada model, `prompt_version`, & parameter 100% identik. |
| `WF-032` | Syahir & Ramadan (terpisah) | `PARALLEL-COORDINATION` | `WF-030`, `WF-031` (`H7`), `WF-029` | `Blocked` | Penilaian A ∥ Penilaian B (independen) | 2 lembar skor terpisah → masuk `WF-033` | Menunggu log terverifikasi `H7` (`WF-030`–`WF-031`) & rubrik terkunci `WF-029`. |
| `WF-033` | Bersama | `JOINT` | `WF-032`, `WF-028` | `Blocked` | — | Persetujuan bersama; bagian `M8` | Menunggu kedua lembar penilaian independen (`WF-032`) terisi 100%. |
| `WF-034` | Bersama (Koord: Ramadan) | `JOINT` | `WF-033`, `WF-030`, `WF-031` | `Blocked` | — | Rev Syahir; tutup `M8` | Menunggu skor terekonsiliasi (`WF-033`) untuk menyusun *error analysis* aktual. |
| `WF-035` | Bersama (Koord: Syahir) | `JOINT` | `M8` (`WF-034`) | `Blocked` | Persiapan bahan `WF-036` | Rev Ramadan; tutup `OD-01` | Menunggu hasil evaluasi aktual `M8` untuk menetapkan judul final & menyinkronkan seluruh `docs/`. |
| `WF-036` | Bersama | `JOINT` | `WF-034`, `WF-035` | `Blocked` | `WF-037` | Review bersama; bagian `M9` | Menunggu hasil aktual `WF-034` & judul final `WF-035`. |
| `WF-037` | Bersama (Op: Syahir; Verif: Ramadan) | `JOINT` | `M6`, `WF-035` | `Blocked` | `WF-036` | Verifikasi bersama; bagian `M9` | Menunggu `M6` & sinkronisasi panduan setup lokal `WF-035`. |
| `WF-038` | Bersama | `JOINT` | `WF-035`, `WF-036`, `WF-037` | `Blocked` | — | Audit final bersama; tutup `M9` | Menunggu seluruh luaran `WF-035`–`WF-037` selesai. |
| `WF-OPT-01` | Member B (Ramadan) | `INDEPENDENT` | `M6`, `WF-011` (Layak), izin jadwal | `Blocked` | Pasca-`M6` (tidak ganggu `M7`–`M9`) | Handoff `H8` → Rev Syahir; bagian `M-OPT` | Bersyarat: menunggu `M6` stabil, konfirmasi kelayakan `WF-011` (`SRC-TAB-001`–`003`), & tidak mengganggu `M7`–`M9`. |
| `WF-OPT-02` | Member A (Syahir) | `HANDOFF-BLOCKED` | `WF-OPT-01` (`H8`), `M6` | `Blocked` | — | Rev Ramadan; bagian `M-OPT` | Menunggu dataset tabular BNPB bersih tervalidasi dari Ramadan (`WF-OPT-01`). |
| `WF-OPT-03` | Member B (Ramadan) | `HANDOFF-BLOCKED` | `WF-OPT-02` | `Blocked` | — | Rev Syahir; tutup `M-OPT` | Menunggu modul statistik deterministik & integrasi UI dari Syahir (`WF-OPT-02`). |
| `WF-OPT-04` | Member A (Syahir) | `INDEPENDENT` | `M8` selesai lebih awal & tidak ganggu `M9` | `Blocked` | — | Rev Ramadan; Opsional `Could` | Di luar jalur kritis; hanya dibuka jika `M8` tuntas lebih awal tanpa mengganggu `M9`. |
