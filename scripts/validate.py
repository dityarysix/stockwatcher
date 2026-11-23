"""Periksa data/emiten/*.json: struktur, sumber, dan larangan domain."""
import json, pathlib, re, sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
TERLARANG = re.compile(r"(^|\.)(idx\.co\.id|idx\.id|wikipedia\.org|kontan\.co\.id|bisnis\.com|cnbcindonesia\.com|kompas\.com|detik\.com|idnfinancials\.com|emitennews\.com|investing\.com|stockbit\.com)$")
STATUS = {"lengkap", "sebagian", "tidak_dapat_diakses"}
POS = {"aset", "pendapatan", "beban_usaha", "laba_bersih", "liabilitas"}
TGL = re.compile(r"^2026-\d{2}-\d{2}$")

def cek(path):
    err, warn = [], []
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JSON tidak valid: {e}"], []
    if d.get("kode") != path.stem:
        err.append(f"kode '{d.get('kode')}' tidak sama dengan nama file")
    if d.get("status_data") not in STATUS:
        err.append(f"status_data tidak dikenal: {d.get('status_data')}")

    def cek_sumber(src, where):
        if not src:
            err.append(f"{where}: tidak ada sumber")
            return
        for s in src:
            host = urlparse(s.get("url", "")).hostname or ""
            if not host:
                err.append(f"{where}: URL sumber kosong/tidak valid")
            elif TERLARANG.search(host):
                err.append(f"{where}: sumber dari domain terlarang ({host})")

    for key in ("aksi_korporasi", "perubahan_manajemen"):
        for i, x in enumerate(d.get(key) or []):
            w = f"{key}[{i}]"
            if not TGL.match(x.get("tanggal", "")):
                err.append(f"{w}: tanggal '{x.get('tanggal')}' bukan 2026-MM-DD")
            for f in (("judul", "ringkasan") if key == "aksi_korporasi" else ("nama", "jabatan", "ringkasan")):
                if not x.get(f):
                    err.append(f"{w}: '{f}' kosong")
            cek_sumber(x.get("sumber"), w)

    lk = d.get("laporan_keuangan")
    if lk:
        for f in ("periode", "satuan", "pos"):
            if not lk.get(f):
                err.append(f"laporan_keuangan: '{f}' kosong")
        for k, v in (lk.get("pos") or {}).items():
            if k not in POS:
                err.append(f"laporan_keuangan.pos: kunci tidak dikenal '{k}'")
            elif not (isinstance(v, list) and len(v) == 2 and all(n is None or isinstance(n, (int, float)) for n in v)):
                err.append(f"laporan_keuangan.pos.{k}: harus [angka, angka]")
        p = lk.get("pos") or {}
        if p.get("aset") and p.get("liabilitas") and p["liabilitas"][0] and p["aset"][0] and p["liabilitas"][0] > p["aset"][0] * 1.5:
            warn.append("liabilitas jauh di atas aset; periksa satuan")
        cek_sumber(lk.get("sumber"), "laporan_keuangan")
    elif d.get("status_data") == "lengkap":
        warn.append("status 'lengkap' tetapi laporan_keuangan kosong")
    return err, warn

def main():
    files = sorted((ROOT / "data/emiten").glob("*.json"))
    bad = 0
    for f in files:
        err, warn = cek(f)
        if err or warn:
            print(f"== {f.stem}")
            for e in err: print("  GALAT  ", e)
            for w in warn: print("  CATATAN", w)
        bad += bool(err)
    print(f"{len(files)} file diperiksa, {bad} bermasalah")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
