# Product Requirements Document (PRD) — SiagaBanjir

> **Status Dokumen:** Draft v0.3 (Finalisasi Keputusan Inti Tim — Siap Menjadi Dasar Penyusunan `TEAM_WORKFLOW.md`)  
> **Tanggal:** 24 November 2026  
> **Mata Kuliah:** Sains Data (Big Project)  
> **Jenis Proyek:** LLM-Based AI Chatbot Development  
> **Domain:** Mitigasi Bencana — Edukasi Kesiapsiagaan Banjir *(Disetujui dosen)*  
> **Judul Akademik Final:** *(Open Decision — belum ditetapkan)*  
> **Tim:** 2 mahasiswa

**Klasifikasi status informasi dalam dokumen ini:**
- **Ketetapan Tugas:** Persyaratan wajib Big Project dari dosen yang harus dipenuhi.
- **Keputusan Final Tim:** Keputusan ruang lingkup, arsitektur, teknologi, dan metode evaluasi yang telah disepakati tim.
- **Asumsi:** Kondisi operasional yang diperkirakan berlaku selama pengerjaan dan perlu diverifikasi saat implementasi.
- **Open Decision:** Hal yang sengaja belum dikunci karena menunggu tes API, pengumpulan & audit fisik data, penyusunan dataset uji, atau pembahasan bersama di `TEAM_WORKFLOW.md`.

---

## 1. Ringkasan Produk

**SiagaBanjir** adalah prototipe chatbot edukasi berbahasa Indonesia berbasis *Large Language Model* (LLM) dengan pendekatan utama *Retrieval-Augmented Generation* (RAG) untuk membantu masyarakat umum non-ahli di Indonesia memahami kesiapsiagaan banjir berdasarkan korpus dokumen kebencanaan resmi yang terkurasi.

Chatbot difokuskan pada edukasi kesiapsiagaan banjir bersifat umum untuk Indonesia — mencakup persiapan sebelum banjir, tindakan keselamatan edukatif saat banjir, dan pemulihan setelah banjir — dengan menyertakan rujukan sumber yang dapat ditelusuri. Klaim terkait wilayah tertentu hanya disajikan apabila didukung langsung oleh sumber teraudit.

SiagaBanjir merupakan **prototipe akademik** yang didemonstrasikan secara lokal menggunakan Streamlit. Produk ini **bukan layanan darurat, bukan sistem peringatan dini resmi, dan tidak boleh menjadi pengganti petugas atau otoritas kebencanaan resmi**. Domain *Mitigasi Bencana (Edukasi Kesiapsiagaan Banjir)* telah memperoleh persetujuan dosen.

---

## 2. Latar Belakang, Identifikasi Masalah, dan Positioning

### 2.1 Konteks Masalah
Panduan kesiapsiagaan banjir dari lembaga kebencanaan resmi Indonesia tersedia dalam berbagai dokumen panjang (buku saku, pedoman PDF, dan publikasi terpisah lintas instansi). Bagi masyarakat umum non-ahli, mencari jawaban cepat yang relevan dengan situasi spesifik di tengah dokumen yang panjang dan tersebar bukanlah hal yang praktis.

Di sisi lain, penggunaan **AI generatif umum tanpa korpus terkurasi** untuk pertanyaan kebencanaan memiliki keterbatasan penting: jawaban cenderung bersifat umum (*generic*), tidak secara konsisten merujuk dokumen resmi Indonesia yang dapat diverifikasi, berisiko mencampur konteks di luar Indonesia atau asumsi pengetahuan umum model tanpa pengakuan batas bukti, serta tidak menjamin batas keselamatan (*safety boundary*) yang seragam untuk skenario kebencanaan.

### 2.2 Permasalahan yang Ditangani
**Permasalahan inti (fokus MVP):**
1. **Fragmentasi panduan resmi:** Informasi persiapan sebelum banjir, tindakan saat banjir, dan langkah pascabanjir tersebar dalam publikasi resmi yang terpisah.
2. **Hambatan akses bagi pengguna non-ahli:** Masyarakat umum kesulitan menemukan bagian panduan yang sesuai dengan pertanyaannya serta memahami istilah teknis kebencanaan secara cepat.
3. **Keterbatasan keterlacakan dan kendali sumber pada AI generatif umum:** Pengguna membutuhkan jawaban berbahasa Indonesia yang terjangkar pada dokumen resmi Indonesia, disertai sitasi yang dapat diperiksa ulang, serta pengakuan jujur apabila sumber tidak mencukupi.
4. **Kebutuhan batas keselamatan kebencanaan:** Pada topik yang menyangkut keselamatan jiwa, sistem harus secara tegas membedakan edukasi dari penanganan darurat dan mengarahkan pengguna ke otoritas resmi pada kondisi darurat akut.

**Permasalahan sekunder/bersyarat *(bukan fokus MVP)*:**
5. **Penyajian konteks statistik bencana:** Angka kejadian atau dampak banjir dari data statistik (mis. BNPB) mudah disalahartikan apabila tidak disertai cakupan wilayah, periode, dan definisi data. Masalah ini hanya akan diangkat sebagai fitur demonstrasi tambahan apabila hasil audit fisik data membuktikan kelayakannya.

### 2.3 Positioning Terhadap AI Generatif Umum
SiagaBanjir **tidak diklaim lebih pintar atau lebih lengkap dibandingkan AI generatif umum**. Alih-alih bersaing dalam keluasan pengetahuan umum, nilai pembeda SiagaBanjir terletak pada lima karakteristik yang terkendali dan dapat diuji:
1. **Korpus resmi terkurasi:** Jawaban dijangkarkan pada kumpulan dokumen edukasi kebencanaan resmi Indonesia yang telah melalui audit fisik dan *corpus versioning/freeze*.
2. **Keterlacakan sumber (*traceability*):** Setiap jawaban berbasis korpus menyertakan sitasi dokumen/bagian pendukung yang dapat diverifikasi oleh pengguna.
3. **Domain khusus:** Ruang lingkup difokuskan secara sempit pada edukasi kesiapsiagaan banjir (cakupan umum Indonesia; klaim wilayah spesifik wajib didukung sumber).
4. **Pengakuan keterbatasan (*explicit abstention*):** Sistem dirancang menyatakan secara eksplisit apabila bukti dalam korpus tidak cukup atau pertanyaan berada di luar cakupan, bukan menebak seolah-olah pasti.
5. **Batas keselamatan (*safety boundary*):** Sistem menerapkan respons khusus untuk situasi darurat akut, menolak prediksi/peringatan dini operasional, dan menegaskan bukan pengganti petugas atau otoritas resmi.

Untuk menguji nilai tambah pendekatan ini secara objektif, proyek menyertakan **eksperimen pembanding** antara *baseline* LLM tanpa *retrieval* dan LLM dengan *retrieval* korpus SiagaBanjir menggunakan model dan pertanyaan uji yang sama (Bagian 12).

---

## 3. Tujuan Produk dan Bukti Keberhasilan

### 3.1 Tujuan Utama
Merancang, membangun, menguji secara komparatif, dan mendokumentasikan prototipe chatbot edukasi kesiapsiagaan banjir berbasis LLM dengan pendekatan utama RAG yang didemonstrasikan secara lokal melalui Streamlit, mengutamakan keselamatan serta keterlacakan sumber resmi, dan menyajikan hasil evaluasi aktual dalam dokumentasi teknis serta poster ilmiah sesuai ketentuan Big Project Sains Data.

### 3.2 Tujuan Khusus dan Cara Pembuktian

| ID | Tujuan Khusus | Kategori | Cara Pembuktian |
|---|---|---|---|
| OBJ-01 | Menyediakan antarmuka percakapan lokal berbasis Streamlit untuk edukasi kesiapsiagaan banjir berbahasa Indonesia bagi masyarakat non-ahli. | Inti (MVP) | Demonstrasi lokal Streamlit dan pengujian skenario *end-to-end*. |
| OBJ-02 | Mengintegrasikan chatbot secara nyata dengan API LLM (Gemini API utama, Groq API cadangan) melalui pendekatan utama RAG dengan pemanfaatan LangChain secara selektif. | Inti (Wajib Tugas) | Dokumentasi arsitektur, log pemanggilan API (provider, model, latensi, status), dan demo live dengan pertanyaan baru/parafrase. |
| OBJ-03 | Menghasilkan jawaban yang terjangkar pada korpus resmi teraudit, menampilkan sitasi yang dapat ditelusuri, dan menjaga kepatuhan batas keselamatan (termasuk respons khusus situasi darurat). | Inti (MVP) | Evaluasi terstruktur pada 30 pertanyaan uji, uji keselamatan darurat, dan inspeksi silang sitasi terhadap konteks terambil. |
| OBJ-04 | Mengevaluasi secara objektif perbandingan *baseline* LLM tanpa *retrieval* melawan SiagaBanjir RAG menggunakan model, korpus *frozen*, dan 30 pertanyaan uji yang sama. | Inti (MVP) | Laporan eksperimen pembanding berbasis penilaian independen 2 anggota tim beserta analisis kesalahan (*error analysis*). |
| OBJ-05 | Menyediakan demonstrasi eksplorasi statistik BNPB yang akurat dengan konteks wilayah dan periode *(bersyarat)*. | Tambahan (`Should`) | Audit fisik data BNPB membuktikan kelayakan + verifikasi perhitungan deterministik terhadap dataset. |
| OBJ-06 | Menyusun dokumentasi teknologi, alur kerja, *reproducibility*, hasil evaluasi aktual, serta poster ilmiah sesuai ketentuan dosen. | Inti (Wajib Tugas) | Tersedianya dokumentasi lengkap dan poster ilmiah 5 komponen wajib berbasis data pengujian aktual. |

---

## 4. Target Pengguna

### 4.1 Pengguna Utama *(Keputusan Final Tim)*
**Masyarakat umum non-ahli di Indonesia** (termasuk warga dan anggota rumah tangga) yang membutuhkan panduan edukatif praktis berbahasa Indonesia mengenai kesiapsiagaan sebelum, saat, dan setelah banjir tanpa harus membaca dokumen kebencanaan yang panjang dan teknis.

### 4.2 Pengguna Sekunder
- **Pelajar atau mahasiswa** yang mempelajari mitigasi bencana atau mencari ringkasan edukatif dari publikasi kebencanaan resmi.
- **Publik umum** yang ingin memahami istilah atau imbauan kebencanaan resmi disertai rujukan dokumen aslinya.

### 4.3 Kebutuhan dan Karakteristik Pengguna
- Bahasa Indonesia yang lugas, non-teknis, dan mudah diikuti oleh pengguna awam.
- Informasi bersifat umum untuk Indonesia; apabila menyangkut wilayah tertentu, pengguna membutuhkan kejelasan sumber pendukung dan cakupan wilayahnya.
- Sitasi sumber yang mudah diperiksa serta batas keselamatan yang jelas bahwa chatbot bukan pengganti petugas atau otoritas resmi.

---

## 5. Batasan Ruang Lingkup dan Kelayakan Tim (2 Mahasiswa)

Untuk menjaga fokus kualitas bagi **2 mahasiswa** dalam durasi perkuliahan, ruang lingkup memisahkan secara tegas antara **MVP Wajib**, **Fitur Tambahan Bersyarat**, dan **Di Luar Ruang Lingkup**.

### 5.1 Ruang Lingkup Inti / MVP (`In Scope — Must`)
1. Prototipe chatbot lokal menggunakan **Streamlit** dengan antarmuka percakapan berbahasa Indonesia (tanya jawab *single-turn* berbasis konteks sumber).
2. Integrasi nyata dengan API LLM (**Gemini API** sebagai provider utama; **Groq API** sebagai cadangan) menggunakan **RAG sebagai pendekatan utama** dan **LangChain secara selektif**.
3. Pengumpulan, audit fisik & kualitas, *versioning*, dan *freeze* korpus dokumen edukasi kesiapsiagaan banjir resmi Indonesia (cakupan umum Indonesia).
4. Mekanisme *retrieval* konteks dari korpus *frozen* dan penyajian jawaban bersitasi yang dapat ditelusuri.
5. Mekanisme keselamatan dan keandalan: *abstention* untuk pertanyaan di luar cakupan, **respons khusus situasi darurat akut**, penolakan prediksi/peringatan dini, penanganan pertanyaan ambigu, serta *error handling* terkendali.
6. Pencatatan (*logging*) untuk *reproducibility*: provider, model spesifik, versi korpus, tanggal sumber, konteks terambil, jawaban, status API, dan waktu respons.
7. Evaluasi sistematis pada **30 pertanyaan uji** (10 faktual, 10 prosedural, 5 di luar cakupan, 5 ambigu) + uji verifikasi situasi darurat, mencakup **eksperimen pembanding Baseline LLM tanpa *retrieval* vs SiagaBanjir RAG** dengan *ground truth* bersama dan penilaian independen oleh 2 anggota tim.
8. Dokumentasi teknologi, alur kerja, panduan reproduksi lokal, analisis hasil & kesalahan, serta **Poster Ilmiah** sesuai ketentuan dosen.

### 5.2 Fitur Tambahan Bersyarat (`In Scope — Should / Could`)
Fitur berikut **bukan MVP wajib** dan **tidak boleh menghambat penyelesaian MVP, evaluasi komparatif, maupun Poster Ilmiah**:
1. **Statistik BNPB (`Should` — Bersyarat):** Hanya boleh masuk sebagai fitur demonstrasi apabila (a) seluruh kebutuhan MVP telah stabil, dan (b) hasil **audit fisik data** membuktikan dataset BNPB layak, bersih, dan konsisten secara struktur.
2. **Konteks percakapan *multi-turn* (`Could`):** Mempertahankan riwayat pertanyaan lanjutan dalam satu sesi percakapan apabila waktu masih mencukupi setelah evaluasi inti tuntas.

### 5.3 Di Luar Ruang Lingkup (`Out of Scope`)
- Arsitektur *agent* kompleks (*autonomous multi-step/tool-using agents*) — tidak wajib dan tidak masuk MVP; RAG adalah pendekatan utama.
- Penggantian peran petugas, layanan darurat, BPBD, BNPB, BMKG, Basarnas, atau keputusan evakuasi otoritatif.
- Layanan peringatan dini resmi atau prediksi operasional lokasi, waktu, ketinggian air, maupun dampak banjir.
- Pengumpulan lokasi presisi (GPS) pengguna secara otomatis.
- Pencarian web terbuka secara langsung (*live web search*, mis. DuckDuckGo Search) pada MVP.
- Pembangunan *pipeline* OCR skala besar untuk dokumen *scan* rusak (kurasi memprioritaskan dokumen digital yang teksnya terbaca).
- Klaim informasi *real-time* atau klaim cakupan seluruh wilayah spesifik Indonesia tanpa dukungan sumber teraudit.
- Sistem akun pengguna, autentikasi, atau *deployment* layanan publik skala produksi (demonstrasi dilakukan dengan Streamlit lokal).

### 5.4 Prinsip Kelayakan Tim 2 Mahasiswa
Proyek dirancang agar realistis dikerjakan oleh **2 mahasiswa** melalui disiplin *MVP-first*, arsitektur RAG yang ramping, dan kolaborasi wajib pada tahap kritis (*ground truth* bersama, penilaian evaluasi independen, gladi demo, serta penyusunan Poster Ilmiah). Detail pembagian tanggung jawab modul, alur kolaborasi, dan jadwal *milestone* ditetapkan terpisah dalam dokumen `TEAM_WORKFLOW.md` (`OD-04`).

---

## 6. Skenario Penggunaan Utama

| ID | Kategori Skenario | Gambaran Interaksi | Cakupan |
|---|---|---|---|
| SC-01 | Persiapan sebelum banjir | Pengguna menanyakan langkah persiapan rumah tangga, tas siaga, atau pengamanan dokumen sebelum banjir. Sistem menjawab berbasis korpus resmi beserta rujukan. | Must (MVP) |
| SC-02 | Tindakan edukatif saat banjir | Pengguna menanyakan panduan keselamatan umum saat air mulai masuk rumah (mis. mematikan listrik, menghindari arus deras). Sistem menjawab berbasis korpus disertai rujukan. | Must (MVP) |
| SC-03 | Langkah setelah banjir | Pengguna menanyakan hal yang perlu diperhatikan setelah banjir surut (kebersihan, kelistrikan, kesehatan). Sistem menjawab berbasis korpus disertai rujukan. | Must (MVP) |
| SC-04 | Penjelasan istilah/imbauan | Pengguna meminta penjelasan istilah atau imbauan dari publikasi kebencanaan resmi. Sistem menjelaskan secara ringkas untuk pengguna awam sesuai sumber. | Must (MVP) |
| SC-05 | Pertanyaan di luar cakupan sumber | Pengguna menanyakan topik di luar domain banjir, klaim wilayah spesifik tanpa sumber, atau detail yang tidak tersedia di korpus. Sistem menyatakan keterbatasan secara eksplisit tanpa mengarang. | Must (MVP) |
| SC-06 | Situasi darurat akut & permintaan prediksi | Pengguna mengindikasikan kondisi bahaya/darurat langsung saat ini atau meminta prediksi/peringatan dini *real-time*. Sistem memberikan **respons khusus situasi darurat** / penolakan prediksi dan mengarahkan ke petugas atau otoritas resmi. | Must (MVP) |
| SC-07 | Pertanyaan ambigu | Pengguna mengirim pertanyaan terlalu singkat atau bermakna ganda (mis. *"banjir"* atau *"harus bagaimana?"*). Sistem meminta klarifikasi fase/konteks atau menawarkan contoh topik yang didukung. | Must (MVP) |
| SC-08 | Statistik kejadian banjir BNPB | Pengguna menanyakan ringkasan statistik kejadian banjir dari data BNPB *(hanya aktif jika lolos audit fisik & masuk demonstrasi tambahan)*. Sistem menampilkan angka terhitung deterministik lengkap dengan wilayah, periode, dan batasan data. | Should (Tambahan Bersyarat) |

---

## 7. Kebutuhan Fungsional

Skema prioritas MoSCoW:
- **Must:** Wajib selesai dan berfungsi pada MVP, evaluasi komparatif, serta demonstrasi lokal Streamlit.
- **Should:** Fitur tambahan bersyarat; hanya dikerjakan setelah MVP stabil dan syarat kelayakan audit data terpenuhi.
- **Could:** Opsional bila waktu tersisa tanpa mengganggu evaluasi dan Poster Ilmiah.

| ID | Kebutuhan Fungsional | Prioritas | Kriteria Penerimaan yang Dapat Diuji (Acceptance Criteria) |
|---|---|---|---|
| FR-01 | **Antarmuka Chat Lokal Streamlit:** Pengguna dapat mengirim pertanyaan teks dan membaca respons pada aplikasi Streamlit lokal. | Must | 1) Aplikasi berjalan lokal melalui Streamlit, menerima input teks valid, dan menampilkan indikator pemrosesan hingga respons tampil.<br>2) Input kosong/spasi ditolak dengan pesan panduan singkat tanpa memicu panggilan API. |
| FR-02 | **Integrasi Nyata dengan API LLM:** Respons dihasilkan melalui pemanggilan API LLM aktif (Gemini API utama, Groq API cadangan). | Must | 1) Setiap pertanyaan valid memicu pemanggilan API LLM nyata (bukan jawaban statis/hardcoded).<br>2) Log mencatat minimal provider, nama model spesifik yang dipakai, status API, dan waktu respons.<br>3) Pada demo live, sistem menjawab variasi parafrase pertanyaan baru di luar daftar tetap. |
| FR-03 | **Retrieval Berbasis Korpus Terkurasi (RAG Utama):** Sistem mengambil potongan konteks relevan dari korpus resmi berversi yang telah di-*freeze* sebelum menghasilkan jawaban. | Must | 1) Pertanyaan uji dalam cakupan mengambil potongan konteks beserta metadata sumber dari korpus aktif.<br>2) Konteks terambil dapat diinspeksi pada log evaluasi untuk memeriksa *groundedness*. |
| FR-04 | **Penyajian Rujukan Sumber:** Jawaban berbasis korpus menampilkan sitasi sumber yang dapat ditelusuri. | Must | 1) Setiap jawaban berbasis korpus mencantumkan minimal nama dokumen/instansi, tanggal/tahun sumber bila tersedia, dan penanda bagian/halaman/URL dari metadata.<br>2) Sitasi cocok dengan konteks yang benar-benar diambil sistem (tidak mengarang rujukan). |
| FR-05 | **Penanganan Pertanyaan Di Luar Cakupan (*Abstention*) & Batas Wilayah:** Sistem menolak mengarang saat bukti tidak cukup, di luar domain banjir, atau menyangkut wilayah spesifik tanpa sumber. | Must | 1) Pada skenario uji *out-of-scope* dan pertanyaan tanpa dukungan korpus, sistem menyatakan eksplisit bahwa informasi tidak ditemukan/tidak cukup pada korpus.<br>2) Sistem tidak mengarang prosedur, angka, regulasi, klaim wilayah spesifik, atau sitasi. |
| FR-06 | **Cakupan Edukasi 3 Fase Banjir (Umum Indonesia):** Sistem menjawab pertanyaan edukasi sebelum, saat, dan setelah banjir serta istilah kebencanaan bagi masyarakat non-ahli. | Must | Skenario uji faktual dan prosedural untuk ketiga fase menghasilkan jawaban Bahasa Indonesia yang lugas, relevan, dan selaras dengan korpus sumber resmi. |
| FR-07 | **Respons Khusus Situasi Darurat Akut & Permintaan Prediksi:** Sistem merespons aman terhadap kondisi darurat langsung atau permintaan peringatan dini/prediksi operasional. | Must | 1) Pada input situasi darurat akut (mis. terjebak banjir, air naik cepat, butuh evakuasi segera), sistem memicu **respons khusus darurat**: menegaskan bukan layanan darurat/pengganti petugas, tidak mengarang instruksi evakuasi spesifik lokasi, serta mengarahkan segera mengikuti arahan petugas setempat dan menghubungi otoritas/layanan darurat resmi (BPBD, BNPB, Basarnas, nomor darurat 112).<br>2) Pada permintaan prediksi/peringatan dini *real-time*, sistem menolak memprediksi dan merujuk kanal resmi (BMKG/BPBD). |
| FR-08 | **Penanganan Pertanyaan Ambigu:** Sistem merespons pertanyaan yang terlalu umum atau bermakna ganda dengan permintaan klarifikasi. | Must | Pada 5 pertanyaan uji ambigu, sistem meminta klarifikasi fase/konteks pertanyaan atau menawarkan opsi topik yang tersedia tanpa menebak maksud secara sembarang. |
| FR-09 | **Penanganan Kesalahan (*Error Handling*) & Cadangan Provider:** Sistem menangani kegagalan API, batas kuota, *timeout*, atau konteks kosong secara terkendali. | Must | Ketika API utama gagal/timeout/kuota habis atau indeks kosong, aplikasi Streamlit tidak *crash*, menampilkan pesan kesalahan informatif tanpa membocorkan kredensial/*stack trace*, dan mendukung pengalihan konfigurasi ke Groq API cadangan bila diperlukan. |
| FR-10 | **Transparansi Identitas & Batasan di UI:** Antarmuka Streamlit menampilkan identitas prototipe, cakupan, dan *disclaimer* keselamatan secara jelas. | Must | Pengguna dapat langsung melihat keterangan bahwa SiagaBanjir adalah prototipe edukasi akademik (bukan pengganti petugas/layanan darurat/peringatan dini), cakupan umum Indonesia, serta informasi versi korpus aktif. |
| FR-11 | **Pencatatan (*Logging*) untuk Reproducibility & Evaluasi Komparatif:** Sistem/skrip evaluasi mencatat seluruh jejak eksekusi pengujian secara terstruktur. | Must | Setiap eksekusi uji (baik *baseline* maupun RAG) menyimpan minimal: `test_id`, mode (`baseline`/`rag`), `provider`, `model_id`, `corpus_version`, `source_dates` (tanggal publikasi & pengambilan sumber yang dirujuk), pertanyaan, konteks terambil, jawaban, sitasi, status API, dan waktu respons (detik). |
| FR-12 | **Demonstrasi Statistik BNPB *(Fitur Tambahan Bersyarat)*:** Sistem menyajikan statistik kejadian banjir dari data BNPB apabila layak secara audit fisik. | Should | 1) **Prasyarat mutlak:** hanya masuk demonstrasi jika hasil audit fisik data BNPB membuktikan kelayakan dan MVP telah stabil.<br>2) Angka dihasilkan melalui komputasi deterministik (bukan tebakan bebas LLM) dan cocok dengan dataset acuan.<br>3) Jawaban wajib mencantumkan cakupan wilayah, periode, sumber BNPB, tanggal data, dan keterbatasan dataset. |
| FR-13 | **Konteks Percakapan *Multi-Turn*:** Sistem mempertahankan konteks pertanyaan lanjutan dalam satu sesi. | Could | Pertanyaan lanjutan dalam sesi yang sama tetap mengambil konteks sumber relevan serta mempertahankan kepatuhan sitasi dan batas keselamatan. |

---

## 8. Kebutuhan Non-Fungsional

| Aspek | Kebutuhan | Cara Verifikasi |
|---|---|---|
| **Akurasi & Groundedness** | Klaim faktual dan prosedural dalam mode RAG konsisten dengan konteks korpus terambil tanpa fabrikasi. | Penilaian independen 2 anggota tim berbasis rubrik terhadap *ground truth* dan konteks log. |
| **Keterlacakan (*Traceability*)** | Setiap jawaban berbasis korpus dapat ditelusuri ke nama dokumen, tanggal sumber, dan lokasi rujukan sesuai metadata. | Audit silang sitasi pada hasil pengujian aktual. |
| **Keandalan & Kesiapan Demo Lokal** | Aplikasi Streamlit lokal stabil pada kondisi normal maupun gagal (API error, input kosong, sumber tidak ada) dan dapat beralih ke Groq API cadangan jika Gemini API terkendala. | Uji kasus negatif (*negative testing*) dan gladi demo lokal. |
| **Kinerja (Waktu Respons)** | Waktu respons diukur aktual (detik) pada mode *baseline* dan RAG tanpa menetapkan target angka sembarang sebelum uji API dan *benchmark* awal. | Pencatatan otomatis latensi pada log pengujian. |
| **Kemudahan Penggunaan** | Antarmuka Streamlit ringkas, berbahasa Indonesia awam, dengan *disclaimer* keselamatan yang terlihat jelas. | Tinjauan antarmuka oleh kedua anggota tim dari sudut pandang pengguna non-ahli. |
| **Keamanan Kredensial** | API key Gemini dan Groq disimpan di *environment variable* (`.env` lokal yang diabaikan Git), tidak pernah *hardcoded* di kode sumber atau repositori. | Inspeksi kode sumber dan `.gitignore`. |
| **Reproduksibilitas** | Seluruh pengujian mencatat `provider`, `model_id`, `corpus_version` (*frozen*), dan tanggal sumber; lingkungan Python dan langkah menjalankan Streamlit terdokumentasi jelas. | Uji coba menjalankan ulang aplikasi dan skrip evaluasi dari dokumentasi pada perangkat anggota tim lain. |
| **Transparansi** | Keterbatasan korpus, status prototipe akademik, posisi terhadap AI umum, dan kegagalan pengujian dilaporkan secara jujur di UI, dokumentasi, dan poster ilmiah. | Pemeriksaan konten UI, dokumentasi, dan draf poster ilmiah. |

---

## 9. Arsitektur LLM, RAG, dan Keputusan Teknologi

### 9.1 Pendekatan Utama LLM & RAG *(Ketetapan Tugas & Keputusan Final Tim)*
Sesuai catatan kritis dosen, **chatbot wajib benar-benar terintegrasi dengan LLM** (bukan *rule-based*, bukan pencarian kata kunci murni, dan bukan jawaban statis). Keputusan arsitektur yang ditetapkan tim:
1. **RAG sebagai Pendekatan Utama:** Pertanyaan pengguna diproses untuk mengambil potongan teks relevan beserta metadatanya dari korpus resmi yang telah di-*freeze*, kemudian dikirim bersama *system prompt* keselamatan dan sitasi ke API LLM untuk menyintesis jawaban berbahasa Indonesia.
2. **LangChain Secara Selektif (Tanpa Agent Kompleks):** LangChain digunakan secara selektif hanya pada komponen yang benar-benar membantu (mis. pemuatan/pemecahan dokumen, integrasi *retriever*, atau antarmuka *chain* LLM), **tanpa membangun *autonomous agent* kompleks** yang menambah kompleksitas *debugging* dan risiko ketidakstabilan bagi tim 2 mahasiswa.
3. **Pemisahan Komputasi untuk Fitur Tambahan:** Apabila fitur tambahan statistik BNPB (`FR-12`) lolos audit fisik dan diaktifkan, seluruh agregasi angka wajib dihitung secara deterministik oleh kode pengolahan data — **LLM dilarang mengarang atau menghitung statistik secara bebas**.
4. **Bukti Verifikasi Integrasi LLM & Reproducibility:** Dibuktikan melalui (a) dokumentasi alur *request–response*, (b) log teknis lengkap (`provider`, `model_id`, `corpus_version`, tanggal sumber, latensi, status API), dan (c) demonstrasi live di Streamlit lokal menggunakan pertanyaan baru/parafrase.

### 9.2 Stack Teknologi *(Keputusan Final Tim vs Open Decision)*

| Komponen | Pilihan / Kandidat | Status | Catatan |
|---|---|---|---|
| **Bahasa Pemrograman** | Python | Keputusan Final Tim | Ekosistem utama untuk pengolahan dokumen, RAG, dan evaluasi. |
| **Antarmuka Demonstrasi** | Streamlit (lokal) | Keputusan Final Tim | Digunakan untuk demonstrasi lokal prototipe chatbot. |
| **Provider LLM Utama** | Gemini API | Keputusan Final Tim *(model spesifik: Open Decision)* | Provider utama untuk RAG dan eksperimen pembanding; nama model spesifik menunggu hasil tes API (`OD-02`). |
| **Provider LLM Cadangan** | Groq API | Keputusan Final Tim *(model spesifik: Open Decision)* | Cadangan apabila Gemini API mengalami kendala kuota/gangguan; nama model spesifik menunggu hasil tes API (`OD-02`). |
| **Orkestrasi RAG** | LangChain *(selektif)* | Keputusan Final Tim | Dipakai secara terarah untuk alur RAG inti; *agent* kompleks tidak wajib dan tidak masuk MVP. |
| **Ekstraksi PDF & Retrieval** | PyMuPDF / *loader* teks & FAISS / *retriever* ringan | Kandidat Implementasi | Detail konfigurasi mengikuti hasil *physical audit* korpus (`OD-03`) dan desain teknis. |
| **Pengolahan Data Tabular** | Pandas & openpyxl | Bersyarat (`Should` — `FR-12`) | Hanya digunakan untuk audit fisik dan komputasi deterministik jika statistik BNPB lolos audit kelayakan. |
| **Live Web Search** | DuckDuckGo Search, dsb. | Di Luar MVP | Tidak digunakan pada MVP demi keterlacakan sumber resmi dan kendali evaluasi. |

---

## 10. Prinsip Keselamatan Informasi Kebencanaan (Safety)

Keselamatan pengguna merupakan prioritas utama. Chatbot **tidak boleh menjadi pengganti petugas atau otoritas resmi** dan wajib menerapkan aturan berikut:

1. **Protokol Respons Khusus Situasi Darurat Akut:** Apabila pengguna mengindikasikan sedang mengalami bahaya langsung (mis. terjebak banjir, air naik cepat, luka/ancaman jiwa, atau meminta keputusan evakuasi langsung), sistem wajib:
   - Segera menampilkan peringatan tegas bahwa SiagaBanjir adalah prototipe edukasi dan **bukan layanan darurat maupun pengganti petugas resmi**;
   - Tidak memberikan instruksi evakuasi otoritatif atau rute spesifik lokasi yang dikarang;
   - Mengarahkan pengguna segera mengikuti arahan petugas di lapangan serta menghubungi layanan darurat/otoritas resmi setempat (BPBD, BNPB, Basarnas, atau nomor darurat 112).
2. **Penolakan Prediksi & Peringatan Dini:** Informasi edukasi tidak boleh diposisikan sebagai peringatan dini resmi atau prakiraan banjir; permintaan semacam itu diarahkan ke kanal resmi seperti BMKG dan BPBD.
3. **Pelestarian Identitas & Tanggal Sumber:** Nama dokumen, instansi penerbit, tanggal publikasi/periode, tanggal pengambilan, dan lokasi rujukan dipertahankan dari ekstraksi hingga jawaban.
4. **Larangan Fabrikasi:** Sistem tidak boleh mengarang nomor regulasi, prosedur keselamatan, angka statistik, klaim wilayah spesifik, atau kutipan sumber.
5. **Abstention Eksplisit & Batas Cakupan Indonesia Umum:** Jika korpus tidak memuat bukti yang cukup atau pertanyaan menuntut detail wilayah tertentu yang tidak didukung dokumen teraudit, sistem menyatakannya secara eksplisit daripada mengisi kekosongan dengan tebakan model.
6. **Transparansi Perbedaan Sumber & Batasan Data:** Perbedaan antar-dokumen resmi tidak boleh disatukan secara diam-diam. Apabila fitur statistik BNPB (`Should`) aktif, jawaban wajib mencantumkan wilayah, periode, sumber, tanggal data, dan keterbatasan dataset.
7. **Kepatuhan Batas Domain:** Pertanyaan di luar domain mitigasi/kesiapsiagaan banjir ditolak secara sopan agar sistem tetap berada pada cakupan tugas.

---

## 11. Kebutuhan Data, Audit Fisik, dan Corpus Versioning

> **Status Data Saat Ini:** Belum ada dokumen maupun dataset yang ditetapkan final atau dinyatakan tervalidasi. Seluruh kandidat sumber — termasuk dokumen edukasi resmi dan kandidat data statistik BNPB — menunggu tahap ***data collection* dan *physical audit*** (`OD-03`) sebelum boleh digunakan dalam sistem.

### 11.1 Kategori Sumber Kandidat *(Menunggu Collection & Physical Audit)*
1. **Dokumen edukasi kesiapsiagaan banjir resmi Indonesia** (buku saku, panduan PDF, atau publikasi resmi instansi seperti BNPB, BPBD, atau kementerian/lembaga terkait untuk cakupan umum Indonesia).
2. **Publikasi edukatif resmi BMKG** terkait informasi hidrometeorologi/banjir (hanya bersifat edukatif, bukan *feed* peringatan dini *real-time*).
3. **Dataset statistik kejadian/dampak banjir BNPB** *(khusus fitur tambahan bersyarat `FR-12` — bukan MVP wajib; hanya digunakan untuk demonstrasi jika lulus audit fisik)*.

### 11.2 Metadata Minimal Wajib per Sumber
Setiap sumber yang lolos audit fisik wajib dicatat dalam manifest korpus dengan metadata minimal:
- `source_id` dan judul dokumen/dataset.
- Instansi penerbit.
- **Tanggal/tahun publikasi sumber** atau periode cakupan data (`source_date`).
- URL resmi atau lokasi asal perolehan dan **tanggal pengambilan** (`retrieved_date`).
- Format berkas (PDF/teks/CSV/XLSX).
- Status audit fisik, catatan kualitas, cakupan wilayah (umum Indonesia vs spesifik), dan keterbatasan sumber.

### 11.3 Kriteria Kelayakan Audit Fisik Data
- **Korpus Dokumen Edukasi (MVP):** Berasal dari instansi resmi/kredibel yang dapat diverifikasi, dapat digunakan secara sah untuk tujuan akademik, teks dapat diekstrak secara utuh dan terbaca (bukan *scan* rusak yang kehilangan struktur makna), serta relevan dengan edukasi sebelum/saat/setelah banjir.
- **Kandidat Dataset Statistik BNPB (Bersyarat `FR-12`):** Wajib lolos audit fisik atas struktur *header*, tipe data, *missing values*, duplikasi, definisi indikator/satuan, cakupan wilayah/periode, dan konsistensi agregasi/total. Jika audit fisik tidak membuktikan kelayakan yang memadai, fitur statistik **tidak dimasukkan ke demonstrasi** dan alasannya didokumentasikan secara transparan.

### 11.4 Corpus Versioning, Freeze, dan Reproduksibilitas *(Keputusan Final Tim)*
- Tim wajib menerapkan ***corpus versioning*** (mis. `corpus_v1.0`) yang mencatat daftar lengkap dokumen, metadata, dan tanggal sumber pada setiap versi.
- Sebelum penyusunan final *ground truth* dan eksekusi evaluasi final, korpus wajib dibekukan (***corpus freeze***) sehingga tidak ada penambahan, penghapusan, atau perubahan dokumen di tengah pengujian.
- Setiap log pengujian, laporan evaluasi, dan rujukan pada Poster Ilmiah wajib mencantumkan **versi korpus *frozen*, tanggal sumber, serta provider dan model LLM** yang digunakan agar eksperimen dapat direproduksi.

---

## 12. Rencana Pengujian, Eksperimen Pembanding, dan Evaluasi

Evaluasi dirancang untuk mengukur kinerja aktual secara objektif — **bukan mengklaim keunggulan sebelum pengujian dijalankan** — dan menghasilkan data empiris yang valid untuk dokumentasi serta **Poster Ilmiah**.

### 12.1 Desain Eksperimen Pembanding *(Baseline vs SiagaBanjir RAG)*
Untuk mengevaluasi dampak nyata pemanfaatan korpus resmi terkurasi, proyek menjalankan eksperimen pembanding terkontrol:
- **Kondisi A — Baseline LLM (tanpa *retrieval*):** Pertanyaan dikirim langsung ke LLM tanpa konteks korpus SiagaBanjir (dengan instruksi dasar peran edukasi banjir).
- **Kondisi B — SiagaBanjir RAG (dengan *retrieval* korpus *frozen*):** Pertanyaan diproses melalui alur RAG penuh menggunakan korpus resmi teraudit, sitasi, dan *prompt* keselamatan.
- **Kontrol Eksperimen:** Kedua kondisi wajib menggunakan **provider, model spesifik, konfigurasi parameter terkendali, dan kumpulan 30 pertanyaan uji yang sama persis**.
- **Prinsip Objektivitas:** PRD ini **tidak menetapkan atau mengasumsikan hasil eksperimen sebelum pengujian dijalankan**. Baik peningkatan kualitas maupun keterbatasan/kelemahan RAG (mis. kegagalan *retrieval*, tambahan latensi, atau *over-abstention*) wajib dilaporkan secara jujur.

### 12.2 Komposisi Dataset Evaluasi Awal *(Keputusan Final Tim)*
Dataset evaluasi inti berjumlah **30 pertanyaan uji** yang disusun berdasarkan korpus *frozen* dengan komposisi tetap:
1. **10 pertanyaan faktual:** Jawabannya tercantum secara eksplisit pada dokumen sumber teraudit.
2. **10 pertanyaan prosedural:** Langkah edukasi kesiapsiagaan untuk fase sebelum, saat, dan setelah banjir.
3. **5 pertanyaan di luar cakupan (*out-of-scope*):** Topik di luar domain banjir, detail yang tidak didukung korpus, atau klaim wilayah spesifik tanpa sumber untuk menguji *abstention*.
4. **5 pertanyaan ambigu:** Input singkat/umum atau bermakna ganda untuk menguji permintaan klarifikasi.

**Pengujian Verifikasi Tambahan (di luar komposisi 30 pertanyaan inti):**
- **Uji Verifikasi Keselamatan Darurat (Wajib MVP):** Sejumlah kasus uji khusus situasi darurat akut dan permintaan prediksi/peringatan dini untuk memverifikasi `FR-07` (respons khusus darurat & pengalihan ke otoritas resmi).
- **Uji Verifikasi Statistik BNPB (Hanya jika `FR-12` aktif):** Kasus uji hitungan deterministik terhadap dataset BNPB teraudit.

### 12.3 Protokol *Ground Truth* dan Penilaian Independen *(Keputusan Final Tim)*
1. **Penyusunan *Ground Truth* Bersama:** Kedua anggota tim menyusun 30 pertanyaan uji beserta jawaban acuan (*poin kunci jawaban*, `sumber_acuan`, dan `ekspektasi_perilaku`) secara bersama berdasarkan korpus yang telah di-*freeze*.
2. **Penilaian Independen:** Setelah sistem menghasilkan respons untuk Kondisi A (*Baseline*) dan Kondisi B (*RAG*), **kedua anggota tim melakukan penilaian secara independen** menggunakan rubrik yang telah ditetapkan (`OD-05`) sebelum membandingkan hasil.
3. **Rekonsiliasi & Analisis Kesalahan:** Perbedaan skor antar-penilai didiskusikan berbasis bukti dokumen sumber dan dicatat secara transparan. Evaluasi wajib menyertakan **analisis kesalahan (*error analysis*)** atas kasus yang gagal, kurang tepat, atau berhalusinasi.

### 12.4 Metrik Evaluasi dan Reproduksibilitas
| Metrik | Definisi / Tujuan | Cakupan Pengukuran |
|---|---|---|
| **Answer Correctness** | Kesesuaian isi jawaban dengan *ground truth* berbasis sumber resmi. | Baseline vs RAG (penilaian independen 2 anggota). |
| **Groundedness** | Sejauh mana klaim jawaban didukung bukti konteks terambil (mendeteksi halusinasi). | Utama pada RAG (dan pencatatan klaim tanpa sumber pada Baseline). |
| **Citation Accuracy** | Ketepatan dan keabsahan sitasi terhadap sumber pendukung sebenarnya. | Utama pada RAG (serta observasi ada/tidaknya sitasi terverifikasi pada Baseline). |
| **Relevance** | Ketepatan jawaban dalam menjawab maksud pertanyaan pengguna awam. | Baseline vs RAG (penilaian independen 2 anggota). |
| **Abstention & Clarification Quality** | Ketepatan pengakuan keterbatasan pada 5 soal *out-of-scope* dan ketepatan klarifikasi pada 5 soal ambigu. | Baseline vs RAG pada kategori terkait. |
| **Safety Compliance (Darurat & Prediksi)** | Kepatuhan respons khusus darurat, penolakan prediksi, dan pengalihan ke otoritas resmi. | Kasus uji verifikasi keselamatan darurat (`FR-07`). |
| **Response Time** | Waktu pemrosesan respons per pertanyaan (detik). | Otomatis dari log eksekusi (Baseline vs RAG). |

> **Catatan Metodologis:** Detail rubrik skor, skala penilaian, dan ambang batas (*threshold*) keberhasilan evaluasi **belum ditetapkan** di PRD ini dan akan difinalisasi setelah penyusunan 30 pertanyaan uji (`OD-05`). Seluruh eksekusi evaluasi wajib mencatat **provider, model spesifik, versi korpus *frozen*, dan tanggal sumber** demi *reproducibility*.

---

## 13. Luaran Akademik (Academic Deliverables)

Seluruh persyaratan Big Project Sains Data diwujudkan dalam empat luaran berikut:

1. **Persetujuan Domain & Usulan Proyek** *(Status: Domain disetujui dosen; judul akademik final pada `OD-01`)*
   - Domain *Mitigasi Bencana — Edukasi Kesiapsiagaan Banjir* telah disetujui dosen dan berbeda dari kelompok lain.
2. **Prototipe Chatbot Terintegrasi LLM (Streamlit Lokal)**
   - Prototipe berbasis RAG yang berjalan stabil secara lokal di Streamlit, benar-benar terintegrasi dengan API LLM (Gemini API utama, Groq API cadangan), dapat didemonstrasikan langsung, dan dapat diuji dengan pertanyaan baru.
3. **Dokumentasi Teknologi, Alur Kerja, dan Evaluasi**
   - Mencakup arsitektur RAG dan pemakaian LangChain selektif, laporan audit fisik & manifest versi korpus *frozen*, konfigurasi & log integrasi LLM, panduan menjalankan ulang prototipe, hasil eksperimen pembanding Baseline vs RAG (penilaian independen 2 anggota + *error analysis*), serta keterbatasan sistem.
4. **Poster Ilmiah *(Wajib — Ketetapan Tugas)***
   Poster ilmiah harus bersifat objektif dan evaluatif (**menyajikan hasil pengujian aktual, bukan sekadar promosi fitur**) dan wajib memuat lima komponen berikut:
   - **Judul, latar belakang, dan tujuan** proyek (termasuk positioning terhadap AI generatif umum).
   - **Metodologi dan pendekatan LLM** (pendekatan utama RAG, kurasi & *freeze* korpus, protokol 30 pertanyaan uji, eksperimen pembanding Baseline vs RAG, dan penilaian independen).
   - **Arsitektur / cara kerja chatbot** (alur input Streamlit, *retrieval* korpus teraudit, pemanggilan API LLM, kontrol keselamatan & sitasi).
   - **Hasil pengujian dan evaluasi respons** (hasil aktual komparasi Baseline vs RAG pada metrik evaluasi, kepatuhan keselamatan, *error analysis*, dan keterbatasan).
   - **Kesimpulan dan referensi** (daftar pustaka metodologi dan sumber kebencanaan resmi berversi yang digunakan).

---

## 14. Risiko dan Mitigasi Awal

| Risiko | Dampak | Mitigasi |
|---|---|---|
| **Halusinasi atau jawaban menyimpang dari korpus** | Informasi kebencanaan menyesatkan pengguna non-ahli | Terapkan RAG pada korpus teraudit, *system prompt* grounded & *abstention* ketat, serta uji *groundedness* komparatif. |
| **Kegagalan respons pada situasi darurat akut** | Pengguna mengandalkan chatbot sebagai layanan darurat | Implementasikan protokol respons khusus situasi darurat (`FR-07`), *disclaimer* permanen di UI, dan uji keselamatan khusus. |
| **Kuota Gemini API habis atau gangguan jaringan saat demo/uji** | Chatbot gagal merespons | Terapkan *error handling* (`FR-09`), uji kuota sejak tes API (`OD-02`), dan siapkan **Groq API sebagai provider cadangan**. |
| **Kualitas ekstraksi PDF korpus buruk** | Konteks terpotong atau kehilangan makna | Lakukan *physical audit* ekstraksi teks sebelum memasukkan dokumen ke korpus; sisihkan PDF *scan* rusak. |
| **Dataset statistik BNPB tidak konsisten/tidak layak** | Statistik menyesatkan atau menyita waktu MVP | Tetapkan statistik BNPB sebagai fitur tambahan bersyarat (`Should`); hanya masuk demo bila lolos audit fisik penuh. |
| **Hasil evaluasi tidak dapat direproduksi** | Temuan pada laporan dan poster diragukan | Terapkan *corpus versioning*, *corpus freeze*, serta pencatatan wajib provider, model spesifik, versi korpus, dan tanggal sumber. |
| **Beban kerja berlebih bagi tim 2 mahasiswa** | MVP, evaluasi 30 soal, atau poster tidak selesai | Batasi ruang lingkup secara ketat (*RAG utama*, tanpa *agent* kompleks, *MVP-first*) dan atur jadwal rinci di `TEAM_WORKFLOW.md`. |
| **Bias penilaian pada tim kecil (2 orang)** | Skor evaluasi kurang objektif | Terapkan penyusunan *ground truth* bersama namun **penilaian respons secara independen** sebelum rekonsiliasi. |

---

## 15. Batasan Proyek dan Asumsi

### 15.1 Batasan Tetap (*Constraints*)
- **Ukuran tim:** Proyek dikerjakan oleh **2 mahasiswa** dalam lingkup Big Project Sains Data (memenuhi ketentuan dosen 2–3 mahasiswa).
- **Status domain:** Domain *Mitigasi Bencana — Edukasi Kesiapsiagaan Banjir* telah disetujui dosen.
- **Lingkungan demo:** Demonstrasi menggunakan **Streamlit secara lokal** (bukan *deployment* produksi publik).
- **Cakupan konten:** Edukasi bersifat umum untuk Indonesia; klaim wilayah tertentu wajib didukung sumber teraudit.
- **Batas keselamatan:** Prototipe akademik edukatif, tidak boleh menggantikan petugas, layanan darurat, atau otoritas resmi.

### 15.2 Asumsi Kerja (*Assumptions*)
- Dokumen edukasi kesiapsiagaan banjir resmi Indonesia dapat dikumpulkan dalam format digital yang terbaca dan lolos *physical audit*.
- Gemini API (utama) dan Groq API (cadangan) dapat diakses dengan kuota yang memadai untuk tes API, eksperimen 30 pertanyaan (Baseline & RAG), dan demonstrasi lokal.
- Kedua anggota tim memiliki lingkungan Python lokal yang kompatibel untuk menjalankan Streamlit dan mereproduksi pengujian.

---

## 16. Kriteria Keberhasilan Proyek

Proyek dinyatakan memenuhi sasaran minimum Big Project apabila **seluruh** kriteria berikut tercapai:

1. **Kesesuaian Domain & Cakupan:** Prototipe tetap selaras dengan domain *Mitigasi Bencana (Edukasi Kesiapsiagaan Banjir)* yang telah disetujui dosen, dengan cakupan umum Indonesia dan klaim wilayah berbasis sumber.
2. **Prototipe Streamlit Lokal Fungsional:** Antarmuka chat lokal berjalan stabil, menampilkan *disclaimer* keselamatan jelas, dan menangani kesalahan API secara terkendali (`FR-01`, `FR-09`, `FR-10`).
3. **Integrasi LLM & RAG Terverifikasi:** Chatbot terbukti benar-benar terintegrasi dengan API LLM (Gemini utama / Groq cadangan) menggunakan RAG sebagai pendekatan utama dan LangChain selektif, dibuktikan lewat log teknis (`provider`, `model_id`, `corpus_version`, tanggal sumber) dan demonstrasi live (`FR-02`, `FR-03`, `FR-11`).
4. **Keterlacakan Sumber & Keselamatan:** Jawaban edukasi 3 fase banjir menyertakan sitasi yang dapat diverifikasi (`FR-04`, `FR-06`), menerapkan *abstention* untuk *out-of-scope* (`FR-05`), klarifikasi untuk pertanyaan ambigu (`FR-08`), dan **respons khusus situasi darurat** yang menegaskan bukan pengganti petugas/otoritas resmi (`FR-07`).
5. **Evaluasi Komparatif Aktual & Reproducible:** Korpus telah di-*versioning* dan di-*freeze*; eksperimen pembanding **Baseline LLM tanpa *retrieval* vs SiagaBanjir RAG** dijalankan pada **30 pertanyaan uji** (10 faktual, 10 prosedural, 5 *out-of-scope*, 5 ambigu) + uji verifikasi darurat menggunakan *ground truth* bersama dan penilaian independen oleh 2 anggota tim, disertai *error analysis* objektif.
6. **Dokumentasi Lengkap:** Dokumentasi arsitektur, audit fisik data, konfigurasi LLM, panduan reproduksi lokal, dan laporan evaluasi aktual tersedia.
7. **Poster Ilmiah Memenuhi Ketentuan Dosen:** Poster ilmiah selesai disusun dengan kelima komponen wajib serta menyajikan hasil pengujian dan evaluasi respons aktual (termasuk hasil komparasi Baseline vs RAG dan keterbatasan — bukan sekadar promosi fitur).

---

## 17. Keputusan yang Belum Final (Open Decisions)

Bagian ini **hanya** memuat keputusan yang memang belum dikunci dan tidak boleh dikarang sebelum tahap pendukungnya selesai:

| ID | Keputusan Terbuka | Dasar Penentuan | Penentu | Tahap Target |
|---|---|---|---|---|
| OD-01 | **Judul akademik final** proyek (untuk dokumentasi dan Poster Ilmiah). | Keselarasan dengan domain disetujui, ruang lingkup RAG, dan evaluasi komparatif. | Tim & konfirmasi Dosen (bila perlu) | Sebelum penyusunan dokumentasi akhir & poster |
| OD-02 | **Model spesifik dan konfigurasi API** untuk Gemini API (utama) dan Groq API (cadangan) — termasuk model ID, parameter *temperature*, batas token, dan strategi *fallback*. | Hasil **tes API aktual** (ketersediaan, kuota, stabilitas, latensi, dan kualitas Bahasa Indonesia). | Tim | Tahap uji API awal / desain teknis |
| OD-03 | **Daftar sumber data final** (dokumen edukasi resmi yang masuk korpus MVP *frozen* serta keputusan kelayakan data statistik BNPB untuk demonstrasi tambahan `FR-12`). | Hasil ***data collection* dan *physical audit*** atas keterbacaan, metadata, struktur, dan kelayakan data. | Tim | Setelah tahap *data collection* & *physical audit* |
| OD-04 | **Detail pembagian kerja dan jadwal *milestone*** untuk tim 2 mahasiswa (termasuk kepemilikan modul dan target waktu hingga poster). | Kesepakatan teknis dan kapasitas mingguan kedua anggota tim. | Tim | Disusun dalam **`TEAM_WORKFLOW.md`** |
| OD-05 | **Detail rubrik penilaian, skala skor, ambang evaluasi (*threshold*), dan prosedur rekonsiliasi** untuk penilaian independen 2 anggota. | Ditetapkan setelah penyusunan 30 pertanyaan uji dan *ground truth* pada korpus *frozen*. | Tim | Setelah penyusunan dataset 30 pertanyaan uji |

---

## 18. Riwayat Perubahan

| Versi | Tanggal | Perubahan |
|---|---|---|
| 0.1 | 23 November 2026 | Draft awal PRD: ringkasan produk, latar belakang, tujuan, target pengguna, ruang lingkup, kebutuhan awal, prinsip keselamatan, evaluasi, risiko, dan keputusan terbuka. |
| 0.2 | 23 November 2026 | Hasil audit & penyempurnaan menyeluruh: koreksi tim menjadi 2 mahasiswa; klasifikasi status informasi; gerbang persetujuan dosen; penambahan luaran wajib Poster Ilmiah; penguatan *acceptance criteria* agar dapat diuji; penyesuaian scope untuk 2 orang; penambahan kriteria audit data & protokol evaluasi; restrukturisasi *Open Decisions*. |
| 0.3 | 24 November 2026 | Finalisasi keputusan inti tim: pembaruan status domain menjadi **disetujui dosen**; penetapan target pengguna utama (*masyarakat umum non-ahli di Indonesia*) dan cakupan edukasi umum Indonesia (klaim wilayah wajib didukung sumber); penguatan *problem statement* dan *positioning* 5 pembeda terhadap AI generatif umum tanpa klaim berlebih; penetapan Gemini API (utama) + Groq API (cadangan) tanpa mengunci nama model sebelum tes API; penegasan RAG sebagai pendekatan utama dengan LangChain selektif (tanpa *agent* kompleks) dan demo lokal Streamlit; penegasan statistik BNPB sebagai fitur tambahan bersyarat yang hanya masuk demonstrasi jika lolos audit fisik; penambahan **eksperimen pembanding Baseline LLM tanpa *retrieval* vs RAG** pada **30 pertanyaan uji** (10 faktual, 10 prosedural, 5 *out-of-scope*, 5 ambigu) dengan *ground truth* bersama dan penilaian independen 2 anggota; penetapan *corpus versioning*, *corpus freeze*, serta aturan pencatatan provider/model/versi korpus/tanggal sumber untuk *reproducibility*; penguatan protokol **respons khusus situasi darurat**; dan perampingan *Open Decisions* hanya pada 5 hal yang benar-benar belum diputuskan (siap menjadi dasar `TEAM_WORKFLOW.md`). |

---

**Catatan Penutup:** PRD Draft v0.3 ini mencerminkan keputusan final inti tim 2 mahasiswa dan siap digunakan sebagai dasar penyusunan `TEAM_WORKFLOW.md` serta dokumen teknis berikutnya (*data collection & physical audit*, desain RAG, tes API, evaluasi komparatif, dan Poster Ilmiah).
