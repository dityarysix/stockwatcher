"""Cocokkan angka laporan keuangan di data/emiten/*.json dengan teks dokumen sumber.

Pemakaian: python3 scripts/crosscheck.py FOLDER_MENTAH [KODE ...]
FOLDER_MENTAH berisi subfolder per KODE dengan file .pdf/.txt/.html sumber.
"""
import json, pathlib, re, subprocess, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
R = pathlib.Path(sys.argv[1])
ONLY = set(sys.argv[2:])
def corpus(kode):
    txt = []
    d = R / kode
    if not d.exists(): return ""
    for f in d.rglob("*"):
        if f.suffix.lower() == ".txt": txt.append(f.read_text(errors="ignore"))
        elif f.suffix.lower() == ".pdf" and not f.with_suffix(".txt").exists():
            try: txt.append(subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True, timeout=60).stdout)
            except Exception: pass
        elif f.suffix.lower() in (".html", ".htm", ".json"): txt.append(f.read_text(errors="ignore"))
    t = "\n".join(txt)
    return re.sub(r"[.,\s]", "", t)  # digits only comparison
for f in sorted(pathlib.Path("data/emiten").glob("*.json")):
    if ONLY and f.stem not in ONLY: continue
    d = json.loads(f.read_text()); lk = d.get("laporan_keuangan")
    if not lk: continue
    c = corpus(f.stem)
    if not c: print(f"{f.stem}: tidak ada file mentah"); continue
    miss = []
    for k, v in lk["pos"].items():
        if k == "beban_usaha" or not v: continue
        for i, n in enumerate(v):
            if n is None: continue
            s = str(abs(int(n))) if float(n).is_integer() else None
            if s and len(s) >= 4 and s not in c: miss.append(f"{k}[{i}]={n}")
    print(f"{f.stem}: {'OK' if not miss else 'TIDAK DITEMUKAN: ' + ', '.join(miss)}")
