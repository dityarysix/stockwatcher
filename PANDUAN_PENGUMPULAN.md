# Panduan pengumpulan data emiten (Stockwatcher)

Tugasmu: untuk setiap emiten yang ditugaskan, kumpulkan informasi sejak **1 Januari 2026** sampai hari ini (23 November 2026) dari **situs resmi emiten itu saja**, lalu tulis satu file JSON per emiten di `data/emiten/KODE.json`.

Contoh file yang sudah benar dan menjadi acuan format serta gaya: `data/emiten/BBCA.json`. Baca dulu sebelum mulai.

## Aturan sumber (wajib)

1. **Hanya situs resmi emiten**: domain milik perusahaan atau grupnya, termasuk subdomain/CDN dokumen resminya (misalnya pustaka.bca.co.id untuk BCA). Tidak boleh: idx.co.id, media massa, situs agregator saham, Wikipedia.
2. **JANGAN akses idx.co.id sama sekali**, karena Syarat Penggunaan IDX melarang scraping/crawling. Kalau situs emiten hanya menautkan ke idx.co.id, jangan ikuti tautannya.
3. **Jangan menembus proteksi.** Kalau situs membalas 403, Cloudflare challenge, captcha, atau timeout berulang, berhenti untuk situs itu. Jangan memalsukan user-agent browser, jangan memakai browser headless untuk melewati blokir, dan jangan mencari cara lain. Catat sebagai `"status_data": "tidak_dapat_diakses"` atau `"sebagian"` dan jelaskan di `catatan`.
4. Pakai `curl` dengan user-agent jujur: `-A "stockwatcher-research/0.1 (non-commercial; summaries with source links)"`. Beri jeda wajar dan jangan mengunduh massal; ambil hanya dokumen yang relevan.
5. **WebSearch** boleh dipakai untuk MENEMUKAN halaman atau PDF, sebaiknya dengan `allowed_domains` berisi domain resmi emiten. Tapi angka dan fakta harus kamu **verifikasi dari dokumen aslinya** (unduh PDF lalu `pdftotext -layout`, atau baca HTML-nya). Jangan pernah menulis angka yang hanya berasal dari ringkasan hasil pencarian.
6. Jangan mengarang. Kalau tidak ketemu, biarkan kosong (`[]` atau `null`) dan jelaskan di `catatan`. Data kosong yang jujur lebih baik daripada data yang salah.
7. Tulis ringkasan dengan kata-katamu sendiri dalam Bahasa Indonesia. Jangan menyalin paragraf panjang.
8. Simpan file mentah (PDF/HTML) di folder sementara di luar repo (misalnya scratchpad sesi) dengan subfolder per KODE, **bukan** di repo.
9. **Jangan** menjalankan git (commit/push) dan jangan mengubah file selain `data/emiten/KODE.json` milik emiten yang ditugaskan kepadamu.

## Apa yang dicari

Tempat umum: menu "Hubungan Investor" / "Investor Relations", "Keterbukaan Informasi", "Laporan Keuangan", "RUPS", "Dividen", "Siaran Pers", "Manajemen".

### 1. `aksi_korporasi` (sejak 1 Jan 2026)
`jenis` pilih salah satu: `Dividen`, `Buyback`, `Akuisisi`, `Divestasi`, `Rights issue`, `Private placement`, `Stock split`, `Obligasi/sukuk`, `Merger`, `Transaksi material`, `Lainnya`.
- Dividen: nilai per saham, tahun buku, dan tanggal penting (cum/recording/pembayaran) jika ada.
- RUPS sendiri BUKAN aksi korporasi. Ambil keputusannya (dividen, buyback, dan sebagainya) sebagai entri terpisah.
- `tanggal` = tanggal pengumuman/keputusan (format YYYY-MM-DD).

### 2. `laporan_keuangan` (satu laporan terbaru, idealnya 30 September 2026)
- `pos` berisi `[nilai_periode_ini, nilai_pembanding]` dalam satuan yang tertulis di laporan (isi `satuan`, misalnya "juta rupiah", "miliar rupiah", "ribu USD", "USD").
  - `aset`, `liabilitas`: pembanding = akhir tahun buku sebelumnya (31 Des 2025), sesuai kolom neraca.
  - `pendapatan`, `beban_usaha`, `laba_bersih`: pembanding = periode yang sama tahun lalu.
- `laba_bersih` = laba (rugi) periode berjalan **yang dapat diatribusikan kepada pemilik entitas induk**, kalau tersedia. Sebutkan di `label`. Rugi ditulis sebagai angka negatif.
- `beban_usaha`:
  - Perusahaan umum: "beban usaha" / "beban operasi" (penjualan + umum & administrasi), **bukan** beban pokok pendapatan. Kalau laporan tidak memisahkannya, jelaskan apa yang kamu pakai di `label` dan `catatan`.
  - Bank (`"format": "bank"`): pendapatan = pendapatan bunga (dan syariah: pendapatan pengelolaan dana/bagi hasil); beban usaha = beban operasional lainnya (tenaga kerja + umum/administrasi + promosi + lainnya, tanpa beban bunga dan tanpa CKPN). Jelaskan cara menjumlahnya di `catatan`.
- Gunakan angka **konsolidasian**. Isi `audit` (misalnya "Tidak diaudit (konsolidasian)").
- Laporan Q3 2026 biasanya terbit akhir Oktober. Kalau belum ada di situs, pakai laporan terbaru yang ada (Juni 2026), lalu sesuaikan `periode` dan pembandingnya.
- Hitung ulang penjumlahan dengan `python3` dan periksa kembali setiap angka terhadap teks PDF.

### 3. `perubahan_manajemen` (sejak 1 Jan 2026)
`jenis`: `Pengangkatan`, `Pengangkatan kembali`, `Pengunduran diri`, `Pemberhentian`, `Tidak menjabat lagi`, `Perubahan jabatan`, `Meninggal dunia`, `Susunan baru`.
- Satu entri per orang yang berubah, ditambah satu entri `Susunan baru` yang merangkum Presiden Komisaris dan Presiden Direktur setelah RUPS, jika ada.
- Pengangkatan kembali seluruh pengurus tanpa perubahan orang cukup satu entri `Susunan baru`.

## Format JSON

Ikuti persis struktur BBCA.json: `kode`, `nama`, `sektor`, `situs_resmi` (URL halaman Hubungan Investor), `status_data` (`lengkap` | `sebagian` | `tidak_dapat_diakses`), `catatan`, `aksi_korporasi`, `laporan_keuangan` (objek atau `null`), `perubahan_manajemen`. Setiap entri wajib punya `sumber`: daftar `{judul, url, diakses: "2026-11-23"}` yang menunjuk dokumen asli di situs resmi.

Setelah menulis file, validasi dengan:

```bash
python3 -m json.tool FILE > /dev/null
```

## Laporan akhir

Balas dengan tabel singkat per emiten: status_data, jumlah aksi korporasi, periode laporan keuangan, jumlah perubahan manajemen, dan kendala. Sebutkan juga angka yang kamu ragukan.

## Tambahan (gelombang emiten 51–100)

- Untuk perusahaan non-bank, isi `"format": "umum"`.
- Jangan memakai API internal situs yang membutuhkan kunci/app key yang diambil dari JavaScript situs.
- Kalau sebuah entri **disimpulkan** (misalnya orang tidak lagi tercantum di susunan baru, atau hanya berdasar judul dokumen/siaran pers tanpa isi), tulis kalimat pertama `ringkasan` dengan jelas, misalnya "Disimpulkan dari ..." atau "Berdasarkan judul dokumen saja ...".
- Nilai per saham ditulis dengan koma desimal Indonesia dan dibulatkan wajar (contoh: "sekitar Rp114,51 per saham"), jangan tiga angka di belakang koma yang bisa terbaca ribuan.
- Untuk tanggal yang tidak pasti, pakai tanggal dokumen sumber dan sebutkan di ringkasan.
- File mentah: simpan di folder sementara per KODE di luar repo, dan untuk PDF laporan keuangan simpan juga hasil `pdftotext -layout` sebagai `.txt` di folder yang sama (dipakai untuk pengecekan silang otomatis).

## Pembaruan berkala (akhir bulan)

1. Untuk setiap emiten di `data/daftar_emiten.csv`, cari dokumen baru di situs resminya yang terbit sejak pembaruan terakhir: laporan keuangan periode yang lebih baru, keputusan RUPS, dividen, buyback, akuisisi, dan perubahan pengurus.
2. Tambahkan entri baru ke file emiten yang sudah ada. Jangan menghapus entri lama kecuali terbukti salah, dan jelaskan koreksinya di `catatan`.
3. Ganti `laporan_keuangan` hanya jika ada periode yang lebih baru.
4. Coba lagi emiten berstatus `tidak_dapat_diakses` satu kali; jika masih diblokir, biarkan.
5. Jangan menyentuh `data/manual/` (berisi data dari file yang diunduh manual oleh pemilik proyek).
6. Jalankan `python3 scripts/validate.py`, `python3 scripts/crosscheck.py FOLDER_MENTAH`, dan `python3 scripts/build.py`.
7. Commit ke branch baru lalu buka pull request ke `main`. Jangan merge sendiri; pemilik proyek yang memutuskan.
8. Batas: maksimal 2 agen bersamaan (sesi utama + 1 sub-agen).
