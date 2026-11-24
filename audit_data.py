#!/usr/bin/env python3
"""Audit fisik dokumen PDF dan skema dataset untuk proyek SiagaBanjir.

Struktur folder yang diharapkan:
project-root/
├── audit_data.py
└── data/
    └── raw/
        ├── dokumen.pdf
        ├── dataset.xlsx
        └── dataset.csv

Jalankan dari folder project atau lokasi mana pun:
    python audit_data.py

Catatan:
- Deteksi halaman PDF dengan < 50 karakter non-whitespace adalah heuristik.
  Halaman kosong, cover, atau halaman berisi gambar juga bisa terdeteksi.
- Skrip ini tidak menjalankan OCR. Halaman yang terindikasi scan perlu OCR
  atau pemeriksaan manual sebelum dimasukkan ke pipeline RAG.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pandas as pd


# Folder data/raw dihitung relatif terhadap lokasi file audit_data.py.
PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PDF_TEXT_THRESHOLD = 50
PDF_SAMPLE_LENGTH = 200
UNIQUE_VALUE_LIMIT = 50

# BNPB pada beberapa workbook memakai format wide: tiap jenis bencana
# menjadi kolom sendiri (contoh: BANJIR, CUACA EKSTREM, TANAH LONGSOR).
KNOWN_DISASTER_HEADERS = {
    "banjir",
    "banjir bandang",
    "cuaca ekstrem",
    "erupsi gunung api",
    "gelombang pasang dan abrasi",
    "gempabumi",
    "gempa bumi",
    "kebakaran hutan dan lahan",
    "kekeringan",
    "tanah longsor",
    "tsunami",
}

YEAR_HEADER_PATTERN = re.compile(r"^(?:19|20)\d{2}(?:\.0)?$")
YEAR_VALUE_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")


def normalise_name(value: Any) -> str:
    """Normalisasi nama kolom hanya untuk pencarian; nama asli tidak diubah."""
    return re.sub(r"[^a-z0-9]+", " ", str(value).strip().lower()).strip()


def clean_sample(text: str, limit: int = PDF_SAMPLE_LENGTH) -> str:
    """Rapikan whitespace agar sampel PDF mudah dibaca di terminal."""
    compact = re.sub(r"\s+", " ", text).strip()
    return compact[:limit] if compact else "[tidak ada teks yang berhasil diekstrak]"


def audit_pdfs(raw_dir: Path) -> list[dict[str, Any]]:
    """Audit seluruh PDF secara rekursif dan kembalikan metadata ringkas."""
    pdf_files = sorted(
        path for path in raw_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )
    results: list[dict[str, Any]] = []

    print("\n" + "=" * 88)
    print("AUDIT PDF — PyMuPDF")
    print("=" * 88)

    if not pdf_files:
        print("Tidak ditemukan file .pdf di data/raw/.")
        return results

    for pdf_path in pdf_files:
        relative_path = pdf_path.relative_to(raw_dir)
        print(f"\n[PDF] {relative_path}")

        try:
            document = fitz.open(pdf_path)
            page_count = document.page_count
            low_text_pages: list[int] = []
            page_char_counts: list[int] = []
            extracted_parts: list[str] = []

            for page_index in range(page_count):
                page = document.load_page(page_index)
                page_text = page.get_text("text") or ""
                # Hitung karakter non-whitespace agar baris baru/spasi tidak
                # membuat halaman scan tampak memiliki teks yang cukup.
                char_count = len(re.sub(r"\s+", "", page_text))
                page_char_counts.append(char_count)
                if char_count < PDF_TEXT_THRESHOLD:
                    low_text_pages.append(page_index + 1)  # nomor halaman mulai 1
                if page_text.strip():
                    extracted_parts.append(page_text)

            document.close()

            combined_text = "\n".join(extracted_parts)
            extractable_pages = sum(
                count >= PDF_TEXT_THRESHOLD for count in page_char_counts
            )
            likely_scan_pages = len(low_text_pages)

            print(f"  Total halaman                 : {page_count}")
            print(f"  Halaman teks >= {PDF_TEXT_THRESHOLD} karakter : {extractable_pages}")
            print(f"  Halaman < {PDF_TEXT_THRESHOLD} karakter      : {likely_scan_pages}")
            if low_text_pages:
                shown_pages = ", ".join(map(str, low_text_pages[:40]))
                suffix = " ..." if len(low_text_pages) > 40 else ""
                print(f"  Nomor halaman terindikasi scan/kosong: {shown_pages}{suffix}")
            else:
                print("  Indikasi scan berdasarkan ambang     : tidak ada")

            print(f"  Sampel {PDF_SAMPLE_LENGTH} karakter pertama : {clean_sample(combined_text)}")

            results.append(
                {
                    "file": str(relative_path),
                    "pages": page_count,
                    "extractable_pages": extractable_pages,
                    "low_text_pages": low_text_pages,
                    "sample": clean_sample(combined_text),
                    "error": None,
                }
            )
        except Exception as exc:  # lanjutkan audit file berikutnya
            message = f"{type(exc).__name__}: {exc}"
            print(f"  GAGAL MEMBACA PDF: {message}")
            results.append(
                {
                    "file": str(relative_path),
                    "pages": None,
                    "extractable_pages": None,
                    "low_text_pages": [],
                    "sample": "",
                    "error": message,
                }
            )

    return results


def find_year_range(df: pd.DataFrame) -> tuple[int | None, int | None, list[int]]:
    """Deteksi rentang tahun pada kolom tahun/periode dan header tahun wide-format."""
    years: set[int] = set()

    # Format wide: nama kolom berisi tahun, misalnya 2010, 2011, ..., 2024.
    for column in df.columns:
        header = str(column).strip()
        if YEAR_HEADER_PATTERN.fullmatch(header):
            years.add(int(float(header)))

    # Format long: ada kolom bernama Tahun/Year/Periode/Tanggal, dsb.
    for column in df.columns:
        name = normalise_name(column)
        is_year_like = (
            name in {"tahun", "year", "periode", "period", "tahun kejadian", "year of event"}
            or "tahun" in name
            or "year" in name
            or name in {"tanggal", "date", "waktu kejadian", "event date"}
        )
        if not is_year_like:
            continue

        series = df[column].dropna()
        for value in series:
            # Tangani angka tahun yang tersimpan sebagai integer/float.
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if math.isfinite(float(value)) and 1900 <= float(value) <= 2100:
                    if float(value).is_integer():
                        years.add(int(value))
                    continue

            # Tangani string seperti "2020", "Tahun 2020", atau tanggal ISO.
            for match in YEAR_VALUE_PATTERN.findall(str(value)):
                year = int(match)
                if 1900 <= year <= 2100:
                    years.add(year)

    sorted_years = sorted(years)
    if not sorted_years:
        return None, None, []
    return sorted_years[0], sorted_years[-1], sorted_years


def find_disaster_type_columns(df: pd.DataFrame) -> list[Any]:
    """Cari kolom kategori bencana pada format long tanpa mengubah nama asli."""
    candidates: list[Any] = []
    for column in df.columns:
        name = normalise_name(column)
        has_disaster = "bencana" in name or "disaster" in name
        has_type = "jenis" in name or "type" in name or "kategori" in name
        if (has_disaster and has_type) or name in {"bencana", "disaster type"}:
            candidates.append(column)
    return candidates


def find_wide_disaster_columns(df: pd.DataFrame) -> list[Any]:
    """Deteksi jenis bencana yang disimpan sebagai nama kolom (format wide)."""
    candidates: list[Any] = []
    for column in df.columns:
        name = normalise_name(column)
        if name in KNOWN_DISASTER_HEADERS:
            candidates.append(column)
    return candidates


def read_csv_robustly(csv_path: Path) -> tuple[pd.DataFrame, str]:
    """Baca CSV dengan deteksi delimiter dan fallback encoding umum."""
    encodings = ["utf-8-sig", "cp1252", "latin1"]
    last_error: Exception | None = None

    for encoding in encodings:
        try:
            frame = pd.read_csv(
                csv_path,
                sep=None,  # deteksi koma/titik koma/tab secara otomatis
                engine="python",
                encoding=encoding,
            )
            return frame, encoding
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Gagal membaca CSV dengan encoding umum: {last_error}")


def inspect_dataframe(
    file_label: str,
    sheet_label: str,
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Cetak skema, tahun, nilai jenis bencana, dan missing values."""
    print(f"\n  [TABEL] {file_label} | sheet: {sheet_label}")
    print(f"  Ukuran data (baris, kolom): {df.shape}")

    print("  Nama kolom persis dan tipe data:")
    if len(df.columns) == 0:
        print("    [tidak ada kolom]")
    else:
        for column, dtype in df.dtypes.items():
            print(f"    - {column!r}: {dtype}")

    year_min, year_max, years = find_year_range(df)
    if years:
        print(f"  Rentang tahun terdeteksi: {year_min}–{year_max}")
        if len(years) <= 30:
            print(f"  Tahun yang ditemukan     : {years}")
        else:
            print(f"  Contoh tahun              : {years[:10]} ... {years[-5:]}")
    else:
        print("  Rentang tahun terdeteksi: tidak ditemukan otomatis")

    disaster_columns = find_disaster_type_columns(df)
    wide_disaster_columns = find_wide_disaster_columns(df)
    disaster_values: dict[str, list[str]] = {}
    if disaster_columns:
        print("  Kandidat kolom jenis bencana (format long) dan contoh nilai unik (case-sensitive):")
        for column in disaster_columns:
            values = df[column].dropna().astype(str).str.strip()
            unique_values = values.drop_duplicates().tolist()
            shown_values = unique_values[:UNIQUE_VALUE_LIMIT]
            # repr() mempertahankan visibilitas ejaan dan spasi tepi.
            print(f"    - {column!r}: {[repr(v) for v in shown_values]}")
            if len(unique_values) > UNIQUE_VALUE_LIMIT:
                print(f"      ... {len(unique_values) - UNIQUE_VALUE_LIMIT} nilai unik lainnya")
            disaster_values[str(column)] = unique_values
    else:
        print("  Kolom nilai kategori jenis bencana (format long): tidak terdeteksi.")

    if wide_disaster_columns:
        print("  Kategori bencana yang menjadi nama kolom (format wide):")
        for column in wide_disaster_columns:
            values = df[column].dropna().astype(str).str.strip().drop_duplicates().tolist()
            print(f"    - {column!r} [nilai kolom contoh: {values[:8]}]")
    else:
        print("  Kolom kategori bencana format wide: tidak terdeteksi otomatis.")

    missing_counts = df.isna().sum()
    total_missing = int(missing_counts.sum())
    print(f"  Missing values total: {total_missing}")
    print("  Missing values per kolom:")
    if len(missing_counts) == 0:
        print("    [tidak ada kolom]")
    else:
        for column, count in missing_counts.items():
            percentage = (count / len(df) * 100) if len(df) else 0.0
            print(f"    - {column!r}: {int(count)} ({percentage:.2f}%)")

    return {
        "file": file_label,
        "sheet": sheet_label,
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "schema": [(str(column), str(dtype)) for column, dtype in df.dtypes.items()],
        "year_min": year_min,
        "year_max": year_max,
        "years": years,
        "disaster_columns": disaster_columns,
        "wide_disaster_columns": wide_disaster_columns,
        "disaster_values": disaster_values,
        "missing_total": total_missing,
        "missing_by_column": {str(col): int(count) for col, count in missing_counts.items()},
    }


def audit_spreadsheets(raw_dir: Path) -> list[dict[str, Any]]:
    """Audit XLSX dan CSV; semua sheet workbook Excel diperiksa."""
    excel_files = sorted(
        path for path in raw_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".xlsx", ".xlsm"}
    )
    csv_files = sorted(
        path for path in raw_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".csv"
    )
    results: list[dict[str, Any]] = []

    print("\n" + "=" * 88)
    print("AUDIT SPREADSHEET — Pandas")
    print("=" * 88)

    if not excel_files and not csv_files:
        print("Tidak ditemukan file .xlsx, .xlsm, atau .csv di data/raw/.")
        return results

    for excel_path in excel_files:
        relative_path = str(excel_path.relative_to(raw_dir))
        print(f"\n[EXCEL] {relative_path}")
        try:
            workbook = pd.ExcelFile(excel_path)
            print(f"  Daftar sheet: {workbook.sheet_names}")
            for sheet_name in workbook.sheet_names:
                try:
                    frame = pd.read_excel(workbook, sheet_name=sheet_name)
                    result = inspect_dataframe(relative_path, str(sheet_name), frame)
                    result["format"] = "Excel"
                    results.append(result)
                except Exception as exc:
                    message = f"{type(exc).__name__}: {exc}"
                    print(f"  GAGAL membaca sheet {sheet_name!r}: {message}")
                    results.append(
                        {
                            "file": relative_path,
                            "sheet": str(sheet_name),
                            "error": message,
                            "format": "Excel",
                        }
                    )
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            print(f"  GAGAL membuka workbook: {message}")
            results.append(
                {"file": relative_path, "sheet": "[workbook]", "error": message, "format": "Excel"}
            )

    for csv_path in csv_files:
        relative_path = str(csv_path.relative_to(raw_dir))
        print(f"\n[CSV] {relative_path}")
        try:
            frame, encoding = read_csv_robustly(csv_path)
            print(f"  Encoding yang berhasil digunakan: {encoding}")
            result = inspect_dataframe(relative_path, "CSV", frame)
            result["format"] = "CSV"
            results.append(result)
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            print(f"  GAGAL membaca CSV: {message}")
            results.append(
                {"file": relative_path, "sheet": "CSV", "error": message, "format": "CSV"}
            )

    return results


def print_mini_prd_summary(
    pdf_results: list[dict[str, Any]],
    table_results: list[dict[str, Any]],
) -> None:
    """Cetak ringkasan padat yang bisa ditempel ke dokumen mini-PRD."""
    print("\n" + "=" * 88)
    print("[RINGKASAN SKEMA DATA UNTUK MINI-PRD]")
    print("=" * 88)

    print("\n1. KNOWLEDGE BASE PDF")
    if not pdf_results:
        print("- Tidak ada PDF ditemukan.")
    for item in pdf_results:
        if item.get("error"):
            print(f"- {item['file']}: ERROR — {item['error']}")
            continue
        low_pages = item["low_text_pages"]
        status = "perlu pemeriksaan scan/OCR" if low_pages else "teks terdeteksi pada semua halaman"
        print(
            f"- {item['file']}: {item['pages']} halaman; "
            f"{item['extractable_pages']} halaman dengan >= {PDF_TEXT_THRESHOLD} karakter; "
            f"{len(low_pages)} halaman < {PDF_TEXT_THRESHOLD} karakter ({status})."
        )

    print("\n2. DATA TABULAR UNTUK PANDAS TOOL-CALLING")
    valid_tables = [item for item in table_results if "error" not in item]
    if not valid_tables:
        print("- Tidak ada tabel yang berhasil dibaca.")

    for item in table_results:
        if item.get("error"):
            print(f"- {item['file']} [{item['sheet']}]: ERROR — {item['error']}")
            continue

        year_text = (
            f"{item['year_min']}–{item['year_max']}"
            if item["year_min"] is not None
            else "tidak terdeteksi"
        )
        print(
            f"\n- File: {item['file']} | Sheet: {item['sheet']} | "
            f"Format: {item.get('format', 'N/A')} | "
            f"Shape: ({item['rows']}, {item['columns_count']}) | Tahun: {year_text} | "
            f"Missing: {item['missing_total']}"
        )
        print("  Skema persis:")
        if item["schema"]:
            for column, dtype in item["schema"]:
                print(f"    * {column!r}: {dtype}")
        else:
            print("    * [tidak ada kolom]")

        if item["disaster_columns"]:
            print("  Nilai unik jenis bencana (format long):")
            for column in item["disaster_columns"]:
                values = item["disaster_values"].get(str(column), [])
                print(f"    * {str(column)!r}: {[repr(v) for v in values[:UNIQUE_VALUE_LIMIT]]}")
        if item["wide_disaster_columns"]:
            print(f"  Kategori jenis bencana (format wide): {[str(c) for c in item['wide_disaster_columns']]}")
        if not item["disaster_columns"] and not item["wide_disaster_columns"]:
            print("  Nilai/kategori jenis bencana: kolom tidak terdeteksi otomatis; cek skema/pivot.")

        if item["missing_by_column"]:
            print("  Missing per kolom:")
            for column, count in item["missing_by_column"].items():
                print(f"    * {column!r}: {count}")

    print("\n3. CATATAN UNTUK DESAIN PIPELINE")
    print("- RAG: pastikan halaman PDF dengan teks < 50 karakter diperiksa; OCR belum dilakukan skrip ini.")
    print("- Pandas: gunakan nama kolom persis seperti hasil audit; jangan mengasumsikan nama kolom seragam.")
    print("- Data tahun: hasil deteksi otomatis perlu dicocokkan dengan metadata dan isi workbook.")
    print("- Jenis bencana: normalisasi label seperti 'BANJIR'/'Banjir' dilakukan pada tahap preprocessing,")
    print("  bukan dengan mengubah file sumber mentah.")
    print("=" * 88)


def main() -> int:
    print("SIAGABANJIR — PHYSICAL DATA AUDIT")
    print(f"Lokasi data mentah: {RAW_DIR}")

    if not RAW_DIR.exists():
        print("Folder data/raw/ belum ada. Membuat folder tersebut sekarang...")
        RAW_DIR.mkdir(parents=True, exist_ok=True)

    pdf_results = audit_pdfs(RAW_DIR)
    table_results = audit_spreadsheets(RAW_DIR)
    print_mini_prd_summary(pdf_results, table_results)

    print("\nAudit selesai.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nAudit dihentikan oleh pengguna.")
        raise SystemExit(130)
