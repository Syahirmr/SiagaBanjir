# Data Dictionary, Metadata Contract & Physical Data Audit — SiagaBanjir

> **Status Dokumen:** Draft v0.2 *(Revisi Kepemilikan Peran Final — Artefak Audit Awal Diserahkan ke Ramadan untuk Review & Lanjutan)*  
> **Tanggal Audit Fisik:** 24 November 2026  
> **PIC (Peran Final):** Member B (Ramadan — Data & Knowledge Preparation)  
> **Disusun Awal oleh:** Member A (Syahir — LLM & Application Engineering; seluruh bukti audit fisik dipertahankan utuh untuk ditinjau & dilanjutkan Ramadan)  
> **Reviewer Integrasi Pipeline:** Member A (Syahir — LLM & Application Engineering)  
> **Acuan Utama:** [PRD.md](./PRD.md) (v0.3) | [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) (v0.5) | [TODO.md](./TODO.md) (v0.4)  
> **Cakupan Work ID:** `WF-005`, `WF-007`, `WF-008`, `WF-009`, `WF-010`, `WF-011`

> **Status Kelayakan & Integritas Data:** Seluruh pemeriksaan pada dokumen ini dilakukan secara ***read-only*** terhadap `data/raw/` (0 berkas mentah diubah/ditimpa). Dokumen ini **belum menetapkan korpus final maupun *corpus freeze*** (`M5`); hasil audit fisik awal ini diserahkan untuk ditinjau dan dilanjutkan oleh Member B (Ramadan — PIC Data & Knowledge Preparation) bersama sinkronisasi `WF-004` (`ARCHITECTURE.md` — PIC Syahir) serta penutupan persetujuan `M0`.

---

## 1. Kontrak Skema Metadata & Chunk Korpus (`WF-005`)

Kontrak ini dirancang agar output pra-pemrosesan **Member B (Ramadan)** (`data/processed/`, Fase 5 / `WF-012` & `WF-018`) dapat langsung dikonsumsi oleh *pipeline* RAG, pembuat sitasi (`FR-04`), kontrol cakupan wilayah (`FR-05`), dan *logger* *reproducibility* (`FR-11`) milik **Member A (Syahir)** dalam `ARCHITECTURE.md` (*planned*).

### 1.1 Skema Manifest Sumber (`corpus_manifest.json`)
Setiap sumber resmi yang lolos *physical audit* dan masuk ke korpus wajib memiliki satu entri pada manifest berversi:

| Field | Tipe | Wajib | Aturan / Nilai Valid | Tujuan PRD |
|---|---|---|---|---|
| `corpus_version` | `string` | Ya | Pola `corpus_v<major>.<minor>[-frozen]` (mis. `corpus_v1.0-frozen`). | *Corpus versioning & freeze* (`FR-11`, Bag. 11.4). |
| `source_id` | `string` | Ya | ID unik stabil: `SRC-EDU-XXX` (korpus edukasi MVP) atau `SRC-TAB-XXX` (statistik bersyarat). | Pelacakan & sitasi (`FR-04`). |
| `title` | `string` | Ya | Judul resmi publikasi/dataset. | Tampilan sitasi pengguna awam (`FR-04`). |
| `publisher` | `string` | Ya | Nama instansi penerbit resmi (mis. `BNPB`, `BMKG`, `BPBD`). | Verifikasi otoritas sumber. |
| `doc_type` | `string` | Ya | Enum: `buku_saku`, `artikel_resmi`, `siaran_pers`, `pedoman`, `dataset_tabular`. | Pemisahan jalur korpus edukasi vs tabular. |
| `source_date` | `string` | Ya | Tanggal/tahun publikasi resmi (`YYYY-MM-DD` atau `YYYY`). | Pencatatan tanggal sumber (`FR-11`). |
| `retrieved_date` | `string` | Ya | Tanggal pengambilan berkas (`YYYY-MM-DD`). | *Reproducibility* & audit kebaruan. |
| `source_url` | `string \| null` | Ya | URL resmi perolehan; isi `null` dengan catatan di `limitations` bila belum terkonfirmasi (jangan dikarang). | Keterlacakan asal sumber. |
| `raw_filename` | `string` | Ya | Nama berkas persis di `data/raw/` (relatif, tanpa mengubah berkas asli). | Audit fisik ulang (*read-only*). |
| `format` | `string` | Ya | Enum: `pdf`, `txt`, `xlsx`, `csv`. | Pemilihan *parser*. |
| `region_scope` | `string` | Ya | Enum: `nasional_umum`, `provinsi`, `kabupaten_kota`, `spesifik_daerah`. | Penegakan aturan batas wilayah (`FR-05`). |
| `flood_phases` | `list[string]` | Ya | Subset dari `["sebelum", "saat", "setelah", "umum_kesiapsiagaan", "istilah_kebijakan", "statistik"]`. | Pemetaan cakupan 3 fase (`FR-06`). |
| `audit_status` | `string` | Ya | Enum: `layak_mvp`, `layak_dengan_pembersihan`, `layak_bersyarat_fr12`, `perlu_verifikasi`, `ditolak`. | Gerbang kualitas data (`M3`). |
| `limitations` | `string` | Ya | Catatan jujur keterbatasan (tahun terbit, cakupan, artefak, metode hitung). | Transparansi UI & Poster (`NFR`). |

### 1.2 Skema Chunk Korpus RAG (`chunks.jsonl` — Handoff `WF-018` Ramadan → `WF-019` Syahir)
Setiap baris pada berkas *chunk* (`JSON Lines`, UTF-8) yang diserahkan oleh **Member B (Ramadan)** ke *retriever* **Member A (Syahir)** wajib memuat struktur datar (*flat metadata*) berikut agar kompatibel langsung dengan `Document(page_content, metadata)` pada **LangChain** secara selektif:

```json
{
  "chunk_id": "SRC-EDU-001_p044_c01",
  "corpus_version": "corpus_v1.0-frozen",
  "text": "Teks bersih hasil ekstraksi dan pembersihan tanpa mengubah makna prosedur...",
  "metadata": {
    "source_id": "SRC-EDU-001",
    "title": "Buku Saku Tanggap Tangkas Tangguh Menghadapi Bencana (Edisi 2018)",
    "publisher": "BNPB",
    "source_date": "2018",
    "retrieved_date": "2026-11-20",
    "source_url": null,
    "section_title": "Bab III.D Banjir — Saat Bencana",
    "flood_phase": "saat",
    "region_scope": "nasional_umum",
    "page_pdf": 44,
    "page_label": "42",
    "citation_text": "BNPB (2018), Buku Saku Tanggap Tangkas Tangguh Menghadapi Bencana, Bab III.D Banjir — Saat Bencana, hal. cetak 42 (hal. PDF 44)."
  }
}
```

**Catatan Koordinasi Kritis untuk Pipeline Syahir (`WF-004` / `WF-006` / `WF-019`):**
1. **Pembedaan `page_pdf` vs `page_label`:** Audit fisik PDF BNPB 2018 membuktikan nomor halaman PDF berbeda `+2` dari nomor halaman cetak (serta beberapa *running header* lampiran keliru tercetak `71`). Menyimpan keduanya mencegah sitasi meleset saat diperiksa manual. Untuk berkas `.txt`, gunakan `page_pdf: null` dan `page_label: "paragraf X"` atau `"bagian utama"`.
2. **Field Siap Logger (`FR-11`):** Dari `metadata` *chunk* terambil, *logger* Syahir dapat langsung mengekstrak `corpus_version`, `source_id`, `source_date`, `retrieved_date`, dan `citation_text` tanpa *parsing* ulang.
3. **Kontrol Batas Wilayah (`FR-05`):** Field `region_scope` memberi sinyal eksplisit kepada *prompt* RAG agar tidak menyamaratakan informasi daerah tertentu menjadi klaim nasional atau sebaliknya.
4. **Pemisahan Ketat Korpus:** Dataset tabular (`SRC-TAB-*`) **tidak pernah** dimasukkan ke `chunks.jsonl` RAG; bila fitur `FR-12` diaktifkan nanti, data tabular hanya diakses lewat fungsi deterministik Pandas/openpyxl.

---

## 2. Inventaris & Verifikasi Sumber `data/raw/` (`WF-007`–`WF-009`)

Pemeriksaan *read-only* terhadap `data/raw/` pada `24 November 2026` menemukan **8 berkas** (2 kandidat korpus edukasi MVP + 6 kandidat dataset tabular statistik BNPB yang dipisahkan dari jalur MVP).

### 2.1 Kandidat Korpus Edukasi MVP (`WF-007` & `WF-008`)

| ID | Nama Berkas di `data/raw/` | Instansi | Format & Ukuran | `source_date` | `retrieved_date` | URL Resmi | Cakupan Fase Banjir | Status Verifikasi Awal |
|---|---|---|---|---|---|---|---|---|
| `SRC-EDU-001` | `Buku Saku Tanggap Tangkas Tangguh Menghadapi Bencana, Edisi 2018.pdf` | BNPB (Pusdatinmas, ISBN `978-602-5693-05-2`) | PDF (`6.537.674` byte, 86 hal.) | `2018` *(PDF mod: 2018-10-03)* | `2026-11-20` *(mtime lokal)* | *Belum tercatat di file lokal* *(perlu dilengkapi)* | Sebelum, Saat, Setelah, Kesiapsiagaan Umum/TSB, Istilah | **Terverifikasi Resmi** *(perlu lengkapi URL resmi asal)* |
| `SRC-EDU-002` | `artikel_se_bnpb_4_2026.txt` | BNPB (Berita resmi, SE Kepala BNPB No. 4/2026) | TXT UTF-8 (`4.128` byte, 20 baris) | `2026-11-01` *(SE: 2026-10-30)* | `2026-11-20` *(mtime lokal)* | `https://www.bnpb.go.id/berita/bnpb-terbitkan-delapan-langkah-kesiapsiagaan-hadapi-musim-hujan-2026-2027` | Sebelum / Kebijakan Kesiapsiagaan & Istilah (InaRISK, DIBI, DSP, pentahelix) | **Terverifikasi Resmi** |

> **Temuan Kesenjangan Sumber (`WF-007`/`WF-008`):**
> - Berkas `siaran_pers_bmkg_nov_2026.txt` yang tercantum pada `prep_step1.py` **tidak ditemukan** di `data/raw/` (kemungkinan gagal ekstrak atau belum disimpan).
> - Saat ini hanya ada **2 berkas edukasi** di `data/raw/`. Meski `SRC-EDU-001` sudah mencakup fase sebelum, saat, dan setelah banjir + Tas Siaga Bencana, edisinya tahun **2018** dan belum ada publikasi edukatif resmi dari BMKG. Tim disarankan mengevaluasi (saat review `M2`) apakah perlu menambah 1–2 dokumen edukasi resmi terbaru (mis. edukasi hidrometeorologi BMKG atau buku saku/panduan banjir BNPB edisi terbaru) sebelum `M3` dikunci.

### 2.2 Kandidat Dataset Statistik BNPB — Jalur Bersyarat (`WF-009`, Terpisah dari MVP)

| ID | Nama Berkas di `data/raw/` | Instansi | Format & Ukuran | Periode Data | `retrieved_date` | URL Resmi | Keterangan Singkat |
|---|---|---|---|---|---|---|---|
| `SRC-TAB-001` | `jumlah-kejadian-bencana-menurut-jenis-bencana-tahun-2010-2024.xlsx` | BNPB *(Juklak No. 7/2023 di sheet Keterangan)* | XLSX (`12.134` byte) | `2010–2024` | `2026-11-20` | *Belum tercatat* | Rekap nasional menurut 9 jenis bencana (termasuk `BANJIR`). |
| `SRC-TAB-002` | `jumlah-kejadian-bencana-menurut-provinsi-2024.xlsx` | BNPB | XLSX (`18.861` byte) | `2024` | `2026-11-20` | *Belum tercatat* | Rekap 38 provinsi + `INDONESIA` menurut jenis bencana (`BANJIR`). |
| `SRC-TAB-003` | `jumlah-kejadian-bencana-menurut-provinsi-2025.xlsx` | BNPB | XLSX (`18.980` byte) | `2025` *(cut-off tidak tertulis)* | `2026-11-20` | *Belum tercatat* | Rekap 38 provinsi + `INDONESIA` menurut jenis bencana (`BANJIR`). |
| `SRC-TAB-004` | `jumlah-kejadian-bencana-menurut-kabupaten-2024.xlsx` | BNPB | XLSX (`76.499` byte) | `2024` | `2026-11-20` | *Belum tercatat* | Rekap 450 kab/kota + `INDONESIA` menurut jenis bencana (`BANJIR`). |
| `SRC-TAB-005` | `jumlah-kejadian-bencana-menurut-provinsi-tahun-2010-2024.xlsx` | BNPB | XLSX (`47.432` byte) | `2010–2024` | `2026-11-20` | *Belum tercatat* | Total **semua bencana gabungan** per provinsi (tanpa kolom `BANJIR`). |
| `SRC-TAB-006` | `jumlah-kejadian-bencana-menurut-kabupaten-tahun-2010-2024.xlsx` | BNPB | XLSX (`105.234` byte) | `2010–2024` | `2026-11-20` | *Belum tercatat* | Total **semua bencana gabungan** per kab/kota (tanpa kolom `BANJIR`). |

---

## 3. Laporan Physical Data Audit — Dokumen Edukasi (`WF-010`)

Audit fisik dijalankan secara *read-only* menggunakan `audit_data.py` (PyMuPDF) dan inspeksi teks halaman per halaman:

### 3.1 `SRC-EDU-001` — Buku Saku BNPB Edisi 2018 (PDF)
- **Bukti Fisik Ekstraksi:** Total **86 halaman PDF** (`Adobe InDesign CS6`, tanpa enkripsi); **79 halaman** memiliki ≥ 50 karakter non-spasi dan **7 halaman** memiliki < 50 karakter (hal. PDF `2, 8, 15, 21, 83, 84, 85`).
- **Hasil Pemeriksaan Manual 7 Halaman < 50 Karakter:**
  - Hal. PDF `2` & `85`: kosong (sampul dalam).
  - Hal. PDF `8`, `15`, `21`: halaman pembatas judul bab (`BAB 1 ANCAMAN BENCANA DI INDONESIA`, `BAB 2 KESIAPSIAGAAN`, `BAB 3 SIAGA BENCANA`).
  - Hal. PDF `83` & `84`: halaman kosong hanya berisi *running header* (`TANGGAP TANGKAS TANGGUH Menghadapi Bencana`).
  - **Kesimpulan Keterbacaan:** **100% *born-digital* terbaca, tidak memerlukan OCR.**
- **Pemetaan Bagian Relevan untuk Korpus SiagaBanjir (Cakupan Umum Indonesia):**
  - Hal. PDF `11`: Karakteristik ancaman bencana hidrometeorologi Indonesia.
  - Hal. PDF `16–20`: Bab II Kesiapsiagaan Umum, Rencana Kesiapsiagaan, dan **Tas Siaga Bencana (TSB)**.
  - Hal. PDF `40–47`: **Bab III.D Banjir** — penyebab & sifat lokal banjir (hal. PDF `40–41`), **Prabencana/Sebelum** (hal. PDF `42–43`), **Saat Bencana** (hal. PDF `44–45`), **Pascabencana** (hal. PDF `46–47`).
  - Hal. PDF `81`: Daftar singkatan/istilah resmi (BNPB, BMKG, dll.).
  - *(Halaman di luar banjir & kesiapsiagaan umum — mis. Gempa, Tsunami, Gunungapi, Karhutla, Kekeringan pada hal. PDF 22–39 & 48–70 — tidak perlu dimasukkan ke korpus MVP agar retrieval tetap fokus domain banjir.)*
- **Temuan Kualitas & Keterbatasan:**
  1. **Selisih penomoran halaman (`+2`):** Halaman cetak Daftar Isi menulis `D. Banjir = 38`, sedangkan di file PDF berada di halaman PDF `40–47`.
  2. **Artefak karakter & *running header*:** Terdapat ligatur font (`ﬁ` pada `geograﬁs`), *running header/footer* berulang, serta salah cetak nomor halaman `71` berulang di lampiran (hal. PDF `75, 77, 79`).
  3. **Tahun terbit 2018:** Daftar aplikasi gawai/kontak edisi 2018 (hal. PDF `80`) berisiko usang sehingga **tidak direkomendasikan** masuk korpus tanpa verifikasi terkini; prinsip keselamatan darurat tetap mengacu pada otoritas resmi setempat (BPBD, BNPB, Basarnas, 112).
- **Keputusan Audit (`WF-010`):** **`layak_dengan_pembersihan` (Inti MVP)** — wajib seleksi bagian relevan banjir + kesiapsiagaan umum, normalisasi ligatur, hapus *running header/footer*, dan catat `page_pdf` + `page_label` pada `WF-012`.

### 3.2 `SRC-EDU-002` — Artikel SE Kepala BNPB No. 4 Tahun 2026 (TXT)
- **Bukti Fisik Ekstraksi:** Berkas UTF-8 utuh (`4.128` byte, 20 baris), teks Bahasa Indonesia bersih dan terbaca penuh tanpa karakter rusak.
- **Relevansi:** Tinggi untuk kesiapsiagaan musim hujan 2026/2027, peran pemantauan cuaca BMKG, pembersihan saluran/normalisasi sungai, evakuasi mandiri/perlindungan kelompok rentan, serta penjelasan istilah resmi (`InaRISK`, `DIBI`, `Dana Siap Pakai / DSP`, `pentahelix`).
- **Temuan Kualitas & Keterbatasan:**
  1. Mayoritas fokusnya adalah instruksi BNPB ke **pemerintah daerah (gubernur/bupati/wali kota/BPBD)**, bukan panduan langkah teknis rumah tangga saat/pasca-banjir.
  2. Terdapat artefak *scraping* web pada baris 4 (`01 Nov 2026 11:31 WIB | Dilihat 4.824 kali`), baris 5 (`Foto : ...`), dan baris 20 (`Admin`) yang wajib dibersihkan saat `WF-012`.
- **Keputusan Audit (`WF-010`):** **`layak_dengan_pembersihan` (Pendukung MVP — Pra-bencana & Istilah Resmi)**.

---

## 4. Laporan Physical Data Audit — 6 Kandidat Statistik BNPB (`WF-011`)

Audit fisik dijalankan pada seluruh 6 workbook `.xlsx` menggunakan `header=1` (karena Row 0 adalah baris judul) beserta pemeriksaan penuh sheet `Keterangan`, duplikasi, *missing values*, keberadaan kategori `BANJIR`, dan uji konsistensi penjumlahan total.

### 4.1 Temuan Struktural Umum pada Seluruh 6 Workbook
1. **Baris header tidak di Row 0:** Row 0 adalah banner judul tabel; header kolom asli berada pada **Row 1**. Pembacaan default `pd.read_excel()` tanpa `header=1` menghasilkan nama kolom `Unnamed: *`.
2. **Definisi resmi & *typo* di sheet `Keterangan`:** Merujuk *Juklak BNPB No. 7 Tahun 2023* dengan ambang kejadian jelas (≥ 1 meninggal, ≥ 50 terdampak/mengungsi, ≥ 5 rumah/fasilitas rusak, ≥ 1 ha lahan rusak, permintaan bantuan/status darurat). **Catatan kualitas:** sheet `Keterangan` memiliki *typo* bawaan dari sumber di mana keterangan `Provinsi` dan `Kabupaten` tertukar, dan **tidak mencantumkan tanggal rilis/*cut-off* data** (khususnya kritis untuk data tahun `2025`).
3. **Aturan metodologi hitung lintas wilayah (KRITIS):** Sheet `Keterangan` menegaskan bahwa 1 kejadian lintas wilayah dihitung **1 secara nasional**, namun dihitung di **setiap provinsi/kabupaten terdampak** pada level wilayah — sehingga **penjumlahan antar-kabupaten TIDAK otomatis sama dengan angka nasional**.

### 4.2 Hasil Audit Fisik per Berkas

| ID | Berkas | Shape (`header=1`) | Duplikat | Missing | Ada Data Khusus `BANJIR`? | Uji Konsistensi Total `BANJIR` | Keputusan Audit (`WF-011`) |
|---|---|---|---|---|---|---|---|
| `SRC-TAB-001` | `jenis-bencana-tahun-2010-2024.xlsx` | `(9, 16)` | `0` | `0` | **Ya** (baris `BANJIR`, 2010–2024) | 2024 = **`1.420`** (cocok dgn `INDONESIA` di `SRC-TAB-002` & `SRC-TAB-004`). | **`layak_bersyarat_fr12`** *(tren banjir nasional 2010–2024)*. |
| `SRC-TAB-002` | `provinsi-2024.xlsx` | `(39, 14)` *(38 prov + `INDONESIA`)* | `0` | `4` *(hanya di baris `INDONESIA`)* | **Ya** (kolom `BANJIR`) | Sum 38 prov = **`1.420`** == baris `INDONESIA` (**Cocok**). | **`layak_bersyarat_fr12`** *(wajib pisahkan baris `INDONESIA` agar tidak double count)*. |
| `SRC-TAB-003` | `provinsi-2025.xlsx` | `(39, 14)` *(38 prov + `INDONESIA`)* | `0` | `4` *(hanya di baris `INDONESIA`)* | **Ya** (kolom `BANJIR`) | Sum 38 prov = **`2.009`** == baris `INDONESIA` (**Cocok**). | **`layak_bersyarat_fr12` (dgn catatan)** *(tanggal cut-off 2025 tidak tertulis di workbook; wajib diberi disclaimer)*. |
| `SRC-TAB-004` | `kabupaten-2024.xlsx` | `(451, 14)` *(450 kab/kota + `INDONESIA`)* | `0` | `4` *(hanya di baris `INDONESIA`)* | **Ya** (kolom `BANJIR`) | **TIDAK SAMA:** Sum 450 kab/kota = **`1.428`** vs baris `INDONESIA` = **`1.420`** (selisih +8 akibat kejadian lintas kab/kota; ~64 kab/kota dengan 0 kejadian tidak tercantum). | **`perlu_verifikasi` / Tidak direkomendasikan untuk agregasi** *(rawan salah hitung total provinsi/nasional)*. |
| `SRC-TAB-005` | `provinsi-tahun-2010-2024.xlsx` | `(38, 20)` | `0` | `0` | **TIDAK** *(hanya total semua bencana gabungan)* | Tidak dapat diverifikasi khusus banjir. | **`ditolak`** *(bukan data khusus banjir; berisiko menyesatkan pengguna)*. |
| `SRC-TAB-006` | `kabupaten-tahun-2010-2024.xlsx` | `(510, 20)` | `0` | `0` | **TIDAK** *(hanya total semua bencana gabungan)* | Tidak dapat diverifikasi khusus banjir. | **`ditolak`** *(bukan data khusus banjir; berisiko menyesatkan pengguna)*. |

### 4.3 Rekomendasi Objektif untuk Fitur Statistik BNPB (`FR-12`)
1. **Jangan masukkan ke MVP wajib:** Pertahankan status `FR-12` sebagai **fitur tambahan bersyarat (`Should`)** sesuai [PRD.md](./PRD.md) v0.3 dan Sprint Plan 7 Hari.
2. **Seleksi ketat bila `M-OPT` diaktifkan nanti:** Hanya **`SRC-TAB-001`**, **`SRC-TAB-002`**, dan **`SRC-TAB-003`** yang layak dipertimbangkan untuk komputasi deterministik (dengan pemisahan baris ringkasan `INDONESIA` serta *disclaimer* metode hitung dan status *cut-off* 2025). **`SRC-TAB-005` dan `SRC-TAB-006` resmi ditolak**, sedangkan **`SRC-TAB-004`** tidak direkomendasikan untuk agregasi.
3. **Prioritas Sprint 7 Hari:** Fokuskan kapasitas 2 mahasiswa pada MVP edukasi (`M5`–`M6`), evaluasi 30 pertanyaan Baseline vs RAG (`M7`–`M8`), dan Poster Ilmiah (`M9`); tangguhkan `M-OPT` apabila waktu tidak tersisa setelah `M8`.

---

## 5. Audit Skrip Eksisting (`audit_data.py` & `prep_step1.py`) & Tindak Lanjut

### 5.1 Hasil Inspeksi Skrip Lokal *(Tidak Diubah)*
- **`audit_data.py`** (`489` baris): **Aman (*read-only* terhadap `data/raw/`)** dan berjalan baik di `venv`. Keterbatasan yang ditemukan: (a) hanya memindai `.pdf`, `.xlsx`, `.csv` sehingga melewatkan `.txt` (`SRC-EDU-002`), (b) membaca Excel dengan `header=0` default sehingga header asli di Row 1 terbaca sebagai `Unnamed: *` dan tahun tidak terdeteksi, (c) memunculkan `FutureWarning` impor `fitz`. Tidak diubah saat ini; audit tambahan dilakukan *read-only* tanpa mengubah skrip.
- **`prep_step1.py`** (`40` baris): **Peringatan keamanan `data/raw/`** — bagian 1 melakukan *scraping* web dan **menulis/menimpa file langsung ke `data/raw/`** (`write_text`). Skrip **tidak dijalankan dan tidak diubah** demi menjaga aturan `data/raw/` *read-only*.

### 5.2 Rekomendasi Tindak Lanjut Sebelum Menutup `M1`, `M2`, dan `M3`
1. **Tutup Persetujuan `M0`:** Catat persetujuan resmi **Syahir** dan **Ramadan** atas `PRD.md` v0.3 & `TEAM_WORKFLOW.md` v0.5 pada [TODO.md](./TODO.md) Bagian 5.1.
2. **Review & Integrasi `WF-005` (`M1`):** Member B (Ramadan) meninjau dan menyetujui kontrak metadata pada Bagian 1 dokumen ini; Member A (Syahir) mengintegrasikannya ke `docs/ARCHITECTURE.md` (`WF-004`, `WF-006`).
3. **Review `M2` & Kelengkapan Sumber (`WF-007`–`WF-009`):** Member B (Ramadan) meninjau inventaris 8 berkas `data/raw/`, melengkapi URL resmi asal `SRC-EDU-001` (BNPB 2018), serta memutuskan bersama Syahir apakah perlu menambahkan 1–2 sumber edukasi resmi terbaru (mis. BMKG/BNPB) sebelum masuk ke Fase 5.
4. **Penutupan `WF-010`–`WF-011` & Lanjutan `M3`:** Setelah Ramadan meninjau hasil audit fisik Bagian 3–4 dan Syahir melakukan *cross-review*, Ramadan melanjutkan `WF-012` (ekstraksi teks bersih ke `data/processed/`), `WF-013` (*spot-check*), `WF-014` (`OD-03`), dan `WF-018` (*chunking*/manifest, koordinasi dengan Syahir).
