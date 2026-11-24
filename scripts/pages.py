"""Bangun halaman statis dari docs/data/semua.json.

Menghasilkan:
- docs/emiten/<kode>/index.html  (satu halaman per emiten, dapat diindeks mesin pencari)
- docs/tentang/index.html dan docs/kebijakan-privasi/index.html
- docs/sitemap.xml dan docs/robots.txt
- Menyisipkan kepala halaman bersama (Analytics + persetujuan cookie) dan footer ke docs/index.html

Dipanggil otomatis oleh scripts/build.py.
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = "https://ceksaham.live"
EMAIL = "info@ceksaham.live"

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
POS = [("aset", "Total aset"), ("pendapatan", "Pendapatan"), ("beban_usaha", "Beban usaha"),
       ("laba_bersih", "Laba (rugi) bersih"), ("liabilitas", "Utang (total liabilitas)")]
STATUS = {"lengkap": "Lengkap", "sebagian": "Sebagian", "tidak_dapat_diakses": "Situs tidak dapat diakses",
          "belum_dikumpulkan": "Belum dikumpulkan"}

e = lambda s: html.escape(str(s or ""), quote=True)


def tgl(iso):
    if not iso:
        return ""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {BULAN[m - 1]} {y}"


def angka(x, digits):
    s = f"{x:,.{digits}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def money(v, satuan):
    if v is None:
        return "–"
    s = (satuan or "").lower()
    usd = any(k in s for k in ("usd", "dolar", "dollar", "us$"))
    mult = 1e12 if "triliun" in s else 1e9 if ("miliar" in s or "billion" in s) else 1e6 if ("juta" in s or "million" in s) else 1e3 if ("ribu" in s or "thousand" in s) else 1
    x = v * mult
    a, sign = abs(x), ("−" if x < 0 else "")
    if usd:
        if a >= 1e9: return f"{sign}US${angka(a / 1e9, 2)} miliar"
        if a >= 1e6: return f"{sign}US${angka(a / 1e6, 1)} juta"
        return f"{sign}US${angka(a / 1e3, 0)} ribu"
    if a >= 1e12: return f"{sign}Rp{angka(a / 1e12, 2)} T"
    if a >= 1e9: return f"{sign}Rp{angka(a / 1e9, 1)} M"
    return f"{sign}Rp{angka(a / 1e6, 0)} jt"


def change(cur, prev, colored):
    if cur is None or prev in (None, 0):
        return ""
    p = (cur - prev) / abs(prev) * 100
    cls = "flat" if not colored else ("up" if p >= 0 else "down")
    return f'<span class="d {cls}">{"+" if p >= 0 else "−"}{angka(abs(p), 1)}%</span>'


def sumber(arr):
    if not arr:
        return ""
    items = "".join(f'<li>Sumber: <a href="{e(s.get("url"))}" target="_blank" rel="noopener">{e(s.get("judul"))}</a>, diakses {e(tgl(s.get("diakses")))}</li>' for s in arr)
    return f'<ul class="src">{items}</ul>'


HEAD = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="/consent.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">"""

FOOT_NAV = """<ul class="foot-nav">
    <li><a href="/tentang/">Tentang</a></li>
    <li><a href="/kebijakan-privasi/">Kebijakan privasi</a></li>
    <li><button type="button" onclick="window.cekSahamCookieSettings &amp;&amp; window.cekSahamCookieSettings()">Pengaturan cookie</button></li>
    <li><a href="mailto:""" + EMAIL + """">""" + EMAIL + """</a></li>
  </ul>"""

FOOT_TEXT = """<p>Sumber: situs resmi masing-masing emiten. Beberapa laporan keuangan diambil dari file laporan keuangan di situs IDX yang diunduh manual. Setiap entri menautkan dokumen aslinya beserta tanggal akses. Angka laporan keuangan disalin dari laporan publikasi perusahaan; periksa dokumen aslinya sebelum mengambil keputusan.</p>
  <p>Menemukan data yang keliru atau kurang lengkap? Kirim koreksi beserta tautan sumbernya ke <a href="mailto:""" + EMAIL + """">""" + EMAIL + """</a>.</p>
  <p>Bukan saran investasi. Cek Saham dikelola secara independen, dapat menampilkan iklan, dan tidak berafiliasi dengan PT Bursa Efek Indonesia maupun emiten mana pun.</p>"""


def page(title, desc, path, body, current=""):
    tabs = [("/", "ringkasan", "Ringkasan", ""), ("/#/aksi", "aksi", "Aksi korporasi", "c-aksi"),
            ("/#/keuangan", "keuangan", "Laporan keuangan", "c-keu"), ("/#/manajemen", "manajemen", "Perubahan manajemen", "c-man")]
    nav = "".join(f'<a href="{h}" class="{c}"{" aria-current=\"page\"" if t == current else ""}>{l}</a>' for h, t, l, c in tabs)
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
{HEAD}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
</head>
<body>
<header class="site">
  <div class="wrap bar">
    <a href="/" class="brand"><span class="mark" aria-hidden="true">CS</span>Cek Saham</a>
    <form class="cari" action="/" method="get" role="search">
      <input type="search" name="q" placeholder="Cari kode atau nama emiten" aria-label="Cari emiten" autocomplete="off">
    </form>
  </div>
  <div class="wrap">
    <nav class="tabs" aria-label="Bagian">{nav}</nav>
  </div>
</header>
<main class="wrap" id="app" tabindex="-1">
{body}
</main>
<footer class="wrap foot">
  {FOOT_NAV}
  {FOOT_TEXT}
</footer>
</body>
</html>
"""


def entries(items, key, cls):
    items = sorted(items, key=lambda x: x.get("tanggal") or "", reverse=True)
    out = []
    for x in items:
        judul = f'{x.get("nama")}, {x.get("jabatan")}' if key == "perubahan_manajemen" else x.get("judul")
        out.append(f"""<li class="entry"><time datetime="{e(x.get('tanggal'))}">{e(tgl(x.get('tanggal')))}</time>
      <div><span class="kind {cls}">{e(x.get('jenis'))}</span>
        <h3>{e(judul)}</h3>
        <p>{e(x.get('ringkasan'))}</p>{sumber(x.get('sumber'))}</div></li>""")
    return f'<ol class="entries">{"".join(out)}</ol>'


def emiten_page(d):
    kode, lk = d["kode"], d.get("laporan_keuangan")
    blocked = d.get("status_data") == "tidak_dapat_diakses" or d.get("situs_diblokir")
    note = ""
    if d.get("status_data") != "lengkap":
        msg = {"sebagian": "Situs resmi emiten ini tidak dapat dibaca otomatis, jadi aksi korporasi dan perubahan manajemen belum tersedia." if d.get("situs_diblokir") else "Data emiten ini belum lengkap.",
               "tidak_dapat_diakses": "Situs resmi emiten ini tidak dapat dibaca otomatis saat pengumpulan data.",
               "belum_dikumpulkan": "Data emiten ini belum dikumpulkan."}.get(d.get("status_data"), "")
        note = f'<p class="notice">{e(msg)} {e(d.get("catatan"))}</p>'

    def sec(key, cls, title, empty):
        arr = d.get(key) or []
        inner = entries(arr, key, cls) if arr else f'<p class="empty">{"Situs resmi tidak dapat diakses." if blocked else empty}</p>'
        return f'<section class="section s-{cls.split("-")[1]}"><h2>{title}</h2>{inner}</section>'

    if lk:
        rows = []
        for k, l in POS:
            v = (lk.get("pos") or {}).get(k)
            lab = (lk.get("label") or {}).get(k) or l
            cmp_ = lk.get("pembanding_neraca") if k in ("aset", "liabilitas") else lk.get("pembanding_lr")
            col = k in ("laba_bersih", "pendapatan")
            rows.append(f'<tr><th scope="row">{e(lab)}</th><td class="num">{money(v[0], lk.get("satuan")) if v else "–"}</td>'
                        f'<td class="num">{money(v[1], lk.get("satuan")) if v else "–"}<span class="co">{e(cmp_)}</span></td>'
                        f'<td class="num">{change(v[0], v[1], col) if v else ""}</td></tr>')
        fin = f"""<table class="kv"><thead><tr><th scope="col">Pos</th><th scope="col" class="num">{e(lk.get('periode'))}</th><th scope="col" class="num">Pembanding</th><th scope="col" class="num">Perubahan</th></tr></thead>
      <tbody>{''.join(rows)}</tbody></table>
      <p class="unit-note">{e(lk.get('audit'))}. Satuan di laporan asli: {e(lk.get('satuan'))}. {e(lk.get('catatan'))}</p>{sumber(lk.get('sumber'))}"""
    else:
        fin = '<p class="empty">Laporan keuangan terbaru belum tersedia.</p>'

    host = re.sub(r"^https?://([^/]+).*$", r"\1", d.get("situs_resmi") or "")
    situs = f'Situs resmi: <a href="{e(d.get("situs_resmi"))}" target="_blank" rel="noopener">{e(host)}</a>' if d.get("situs_resmi") else ""
    body = f"""<p class="crumb"><a href="/">Ringkasan</a> / {e(kode)}</p>
<div class="detail-head"><span class="big">{e(kode)}</span><h1>{e(d.get('nama'))}</h1></div>
<p class="detail-meta">{e(d.get('sektor'))}. Status data: {e(STATUS.get(d.get('status_data'), d.get('status_data')))}. {situs}</p>
{note}
{sec('aksi_korporasi', 'k-aksi', 'Aksi korporasi', 'Tidak ada aksi korporasi yang ditemukan di situs resmi sejak 1 Januari 2026.')}
<section class="section s-keu"><h2>Laporan keuangan</h2>{fin}</section>
{sec('perubahan_manajemen', 'k-man', 'Perubahan manajemen', 'Tidak ada perubahan manajemen yang ditemukan di situs resmi sejak 1 Januari 2026.')}"""

    bagian = []
    if lk and (lk.get("pos") or {}).get("laba_bersih"):
        lb = lk["pos"]["laba_bersih"][0]
        bagian.append(f"laba bersih {money(lb, lk.get('satuan'))} ({lk.get('periode')})")
    n_ak, n_mn = len(d.get("aksi_korporasi") or []), len(d.get("perubahan_manajemen") or [])
    bagian.append(f"{n_ak} aksi korporasi dan {n_mn} perubahan manajemen sejak Januari 2026")
    desc = f"{d.get('nama')} ({kode}): " + ", ".join(bagian) + ". Ringkasan dari situs resmi emiten beserta sumbernya."
    title = f"{kode} {d.get('nama')}: aksi korporasi, laporan keuangan, manajemen | Cek Saham"
    return page(title, desc, f"/emiten/{kode.lower()}/", body)


TENTANG = f"""<div class="prose">
<h1>Tentang Cek Saham</h1>
<p>Cek Saham merangkum keterbukaan informasi emiten Bursa Efek Indonesia ke dalam tiga bagian: aksi korporasi (dividen, pembelian kembali saham, akuisisi, penambahan modal, dan lainnya), laporan keuangan (aset, pendapatan, beban usaha, laba atau rugi, dan utang), serta perubahan direksi dan komisaris. Cakupan saat ini adalah 100 emiten sejak 1 Januari 2026.</p>
<h2>Dari mana datanya</h2>
<ul>
<li>Sumber utama adalah situs resmi masing-masing emiten, misalnya halaman hubungan investor, laporan keuangan, dan ringkasan risalah RUPS.</li>
<li>Untuk sebagian emiten, laporan keuangan diambil dari file laporan keuangan di situs Bursa Efek Indonesia yang diunduh secara manual.</li>
<li>Setiap entri mencantumkan tautan ke dokumen asli dan tanggal akses. Isi ditulis ulang sebagai ringkasan; dokumen asli tidak disalin.</li>
<li>Entri yang merupakan simpulan, misalnya pengurus yang tidak lagi tercantum dalam susunan baru, ditandai di ringkasannya.</li>
<li>Angka laporan keuangan dicocokkan secara otomatis dengan teks dokumen sumbernya sebelum ditayangkan.</li>
</ul>
<h2>Batasan</h2>
<ul>
<li>Sebagian situs emiten tidak dapat dibaca secara otomatis. Emiten tersebut ditandai dan datanya bisa belum lengkap.</li>
<li>Data diperbarui secara berkala setiap akhir bulan, sehingga informasi terbaru bisa belum tercantum.</li>
<li>Cek Saham bukan saran investasi. Selalu periksa dokumen asli sebelum mengambil keputusan.</li>
</ul>
<h2>Kontak dan koreksi</h2>
<p>Menemukan data yang keliru atau kurang lengkap? Kirim koreksi beserta tautan sumbernya ke <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<p>Cek Saham dikelola secara independen, dapat menampilkan iklan, dan tidak berafiliasi dengan PT Bursa Efek Indonesia maupun emiten mana pun.</p>
</div>"""

PRIVASI = f"""<div class="prose">
<h1>Kebijakan privasi</h1>
<p class="muted">Berlaku sejak 23 November 2026.</p>
<p>Kebijakan ini menjelaskan data apa yang dikumpulkan saat Anda mengunjungi ceksaham.live, untuk apa data itu dipakai, dan pilihan yang Anda miliki.</p>
<h2>Data yang kami kumpulkan</h2>
<ul>
<li><strong>Statistik kunjungan (Google Analytics).</strong> Jika Anda menyetujui cookie, Google Analytics mencatat halaman yang dibuka, perkiraan lokasi tingkat kota atau negara, jenis perangkat dan peramban, serta sumber kunjungan. Kami memakai data ini hanya untuk memahami penggunaan situs dan memperbaikinya.</li>
<li><strong>Iklan (Google AdSense), jika ditampilkan.</strong> Google dan mitranya dapat memakai cookie untuk menampilkan iklan berdasarkan kunjungan Anda ke situs ini dan situs lain. Iklan yang dipersonalisasi hanya aktif jika Anda menyetujui cookie.</li>
<li><strong>Email yang Anda kirim.</strong> Jika Anda menghubungi {EMAIL}, kami menyimpan alamat email dan isi pesan untuk menjawab dan menindaklanjuti koreksi.</li>
</ul>
<p>Cek Saham tidak memiliki fitur akun atau formulir, dan tidak meminta nama, nomor telepon, atau data keuangan pribadi Anda.</p>
<h2>Persetujuan cookie</h2>
<p>Saat pertama kali berkunjung, Anda dapat memilih <em>Setuju</em> atau <em>Tolak</em>. Sebelum Anda setuju, Google Analytics dan iklan berjalan dalam mode persetujuan terbatas: cookie analitik dan iklan tidak dipasang, dan Google hanya menerima sinyal tanpa cookie. Pilihan Anda disimpan di peramban Anda dan dapat diubah kapan saja melalui tautan <em>Pengaturan cookie</em> di bagian bawah setiap halaman.</p>
<h2>Pihak ketiga</h2>
<ul>
<li>Google LLC sebagai penyedia Google Analytics dan Google AdSense. Penggunaan data oleh Google dijelaskan di <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">Cara Google menggunakan informasi dari situs yang memakai layanannya</a>.</li>
<li>Anda dapat mengatur iklan yang dipersonalisasi di <a href="https://adssettings.google.com" target="_blank" rel="noopener">Setelan Iklan Google</a>.</li>
<li>Huruf (font) dimuat dari Google Fonts.</li>
<li>Situs ini dihosting di GitHub Pages, yang dapat mencatat alamat IP pengunjung untuk keperluan keamanan dan operasional.</li>
</ul>
<h2>Hak Anda</h2>
<p>Sesuai Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi, Anda dapat meminta akses, koreksi, atau penghapusan data pribadi yang kami simpan, serta menarik persetujuan kapan saja. Kirim permintaan ke <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Perubahan kebijakan</h2>
<p>Kebijakan ini dapat diperbarui. Tanggal berlaku di bagian atas halaman akan ikut diubah.</p>
</div>"""


def patch_index():
    p = DOCS / "index.html"
    s = p.read_text(encoding="utf-8")
    meta = ("<title>Cek Saham: keterbukaan informasi emiten BEI</title>\n"
            "<meta name=\"description\" content=\"Ringkasan aksi korporasi, laporan keuangan, dan perubahan manajemen 100 emiten "
            "Bursa Efek Indonesia sejak Januari 2026, diambil dari situs resmi emiten beserta sumbernya.\">\n"
            f"<link rel=\"canonical\" href=\"{SITE}/\">")
    s = re.sub(r"<head>.*?</head>", lambda m: f"<head>\n{HEAD}\n{meta}\n</head>", s, count=1, flags=re.S)
    s = re.sub(r'<footer class="wrap foot">.*?<p class="muted" id="built"></p>',
               lambda m: f'<footer class="wrap foot">\n  {FOOT_NAV}\n  {FOOT_TEXT}\n  <p class="muted" id="built"></p>', s, count=1, flags=re.S)
    s = s.replace('<script src="app.js"></script>', '<script src="/app.js"></script>')
    p.write_text(s, encoding="utf-8")


def main():
    data = json.loads((DOCS / "data/semua.json").read_text(encoding="utf-8"))
    urls = [f"{SITE}/", f"{SITE}/tentang/", f"{SITE}/kebijakan-privasi/"]
    for d in data["emiten"]:
        out = DOCS / "emiten" / d["kode"].lower() / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(emiten_page(d), encoding="utf-8")
        urls.append(f"{SITE}/emiten/{d['kode'].lower()}/")
    for slug, title, desc, body in (
        ("tentang", "Tentang Cek Saham", "Apa itu Cek Saham, dari mana datanya, dan bagaimana mengirim koreksi.", TENTANG),
        ("kebijakan-privasi", "Kebijakan privasi | Cek Saham", "Data yang dikumpulkan ceksaham.live, penggunaan cookie Google Analytics dan iklan, serta hak Anda.", PRIVASI),
    ):
        out = DOCS / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(title, desc, f"/{slug}/", body), encoding="utf-8")
    lastmod = data["dibangun"]
    (DOCS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    patch_index()
    print(f"{len(urls)} halaman di sitemap")


if __name__ == "__main__":
    main()
