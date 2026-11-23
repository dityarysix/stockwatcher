# Cek Saham

Tayang di https://ceksaham.live. Koreksi data: info@ceksaham.live

Ringkasan keterbukaan informasi 100 emiten Bursa Efek Indonesia sejak 1 Januari 2026, diambil dari **situs resmi masing-masing emiten**. Isinya dibagi tiga bagian:

1. **Aksi korporasi:** dividen, buyback, akuisisi, rights issue, dan lainnya
2. **Laporan keuangan:** aset, pendapatan, beban usaha, laba/rugi, dan utang (total liabilitas)
3. **Perubahan manajemen:** direksi dan komisaris

## Struktur

| Lokasi | Isi |
|---|---|
| `data/daftar_emiten.csv` | Daftar 100 emiten |
| `data/emiten/KODE.json` | Data per emiten (sumber utama) |
| `scripts/validate.py`, `scripts/crosscheck.py` | Pemeriksa struktur data dan pencocokan angka dengan dokumen sumber |
| `PANDUAN_PENGUMPULAN.md` | Aturan pengumpulan data dan prosedur pembaruan bulanan |
| `scripts/build.py` | Menggabungkan semua data menjadi `docs/data/semua.json` |
| `docs/` | Website statis (GitHub Pages) |

Setelah mengubah data, jalankan:

```bash
python3 scripts/build.py
```

## Aturan sumber

- Hanya situs resmi emiten. Setiap entri mencantumkan tautan dokumen asli dan tanggal akses.
- Hanya ringkasan dengan kata-kata sendiri. Dokumen asli tidak disalin ke repo ini.
- Tidak mengambil data dari idx.co.id secara otomatis, karena Syarat Penggunaan IDX melarang scraping/crawling.

Bukan saran investasi. Proyek pribadi non-komersial dan tidak berafiliasi dengan PT Bursa Efek Indonesia maupun emiten mana pun.
