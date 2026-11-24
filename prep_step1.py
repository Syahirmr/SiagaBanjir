import requests
import trafilatura
import pandas as pd
from pathlib import Path

raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

# 1. Scrape otomatis 2 artikel web BNPB & BMKG ke .txt
urls = {
    "artikel_se_bnpb_4_2026.txt": "https://www.bnpb.go.id/berita/bnpb-terbitkan-delapan-langkah-kesiapsiagaan-hadapi-musim-hujan-2026-2027",
    "siaran_pers_bmkg_nov_2026.txt": "https://www.bmkg.go.id/siaran-pers/jelang-dan-selama-musim-hujan-bmkg-ajak-masyarakat-tingkatkan-kesiapsiagaan-bencana-hidrometeorologi"
}

for filename, url in urls.items():
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    text = trafilatura.extract(resp.text)
    if text:
        (raw_dir / filename).write_text(f"SUMBER URL: {url}\n\n{text}", encoding="utf-8")
        print(f"[OK] Tersimpan: {filename} ({len(text)} karakter)")
    else:
        print(f"[GAGAL] Gagal ekstrak: {filename}")

# 2. Intip 5 baris pertama Excel utama untuk cek baris header asli
excel_samples = [
    "jumlah-kejadian-bencana-menurut-jenis-bencana-tahun-2010-2024.xlsx",
    "jumlah-kejadian-bencana-menurut-kabupaten-2024.xlsx",
    "jumlah-kejadian-bencana-menurut-provinsi-2024.xlsx",
    "jumlah-kejadian-bencana-menurut-provinsi-2025.xlsx",
]

for fname in excel_samples:
    fpath = raw_dir / fname
    if fpath.exists():
        print("\n" + "="*60)
        print(f"PREVIEW 5 BARIS PERTAMA: {fname}")
        xl = pd.ExcelFile(fpath)
        data_sheet = [s for s in xl.sheet_names if s != "Keterangan"][0]
        df_preview = pd.read_excel(fpath, sheet_name=data_sheet, header=None, nrows=5)
        print(df_preview.to_string())