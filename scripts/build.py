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
    d.update({"no": int(row["no"]), "kode": row["kode"], "nama": row["nama"], "sektor": d.get("sektor") or row["sektor"]})
    out.append(d)
(ROOT / "docs/data").mkdir(parents=True, exist_ok=True)
(ROOT / "docs/data/semua.json").write_text(json.dumps(
    {"dibangun": datetime.date.today().isoformat(), "emiten": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{sum(1 for d in out if d['status_data'] != 'belum_dikumpulkan')}/{len(out)} emiten berisi data")
