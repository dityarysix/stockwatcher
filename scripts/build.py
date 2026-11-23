"""Gabungkan data/emiten/*.json menjadi docs/data/semua.json untuk website."""
import csv, json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
daftar = list(csv.DictReader(open(ROOT / "data/daftar_emiten.csv", encoding="utf-8")))
out = []
for row in daftar:
    f = ROOT / "data/emiten" / f"{row['kode']}.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
    else:
        d = {"status_data": "belum_dikumpulkan", "aksi_korporasi": [], "laporan_keuangan": None, "perubahan_manajemen": []}
    m = ROOT / "data/manual" / f"{row['kode']}.json"
    if m.exists():
        # Data dari file yang diunduh manual oleh pemilik proyek (misalnya laporan keuangan IDX) menimpa bagian yang sama.
        manual = json.loads(m.read_text(encoding="utf-8"))
        d.update(manual)
        if d.get("status_data") == "tidak_dapat_diakses":
            d["situs_diblokir"] = True
        if d.get("status_data") in (None, "belum_dikumpulkan", "tidak_dapat_diakses"):
            d["status_data"] = "sebagian"
            d["catatan"] = ((d.get("catatan") or "") + " Laporan keuangan diambil dari file yang diunduh manual dari IDX.").strip()
    d.update({"no": int(row["no"]), "kode": row["kode"], "nama": row["nama"], "sektor": d.get("sektor") or row["sektor"]})
    out.append(d)
(ROOT / "docs/data").mkdir(parents=True, exist_ok=True)
(ROOT / "docs/data/semua.json").write_text(json.dumps(
    {"dibangun": datetime.date.today().isoformat(), "emiten": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{sum(1 for d in out if d['status_data'] != 'belum_dikumpulkan')}/{len(out)} emiten berisi data")

# Halaman statis (per emiten, tentang, kebijakan privasi), sitemap, dan robots.txt.
import importlib.util as _u
_s = _u.spec_from_file_location("pages", ROOT / "scripts/pages.py"); _m = _u.module_from_spec(_s); _s.loader.exec_module(_m); _m.main()
