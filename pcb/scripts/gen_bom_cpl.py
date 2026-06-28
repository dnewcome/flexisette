"""gen_bom_cpl.py — JLCPCB assembly files (BOM + CPL/pick-and-place) for a tscircuit->KiCad board.

  BOM  <- dist/<base>/circuit.json   (LCSC part numbers tscircuit resolved from the imports)
  CPL  <- kicad-cli pcb export pos   (placement in the SAME origin as the Gerbers)

JLCPCB matches parts by the LCSC number; Comment/Footprint are human reference. tscircuit gives a
LIST of candidate LCSC numbers per part — we take the first (usually the preferred/basic part); the
JLC upload UI flags Basic vs Extended so you can swap. Parts with no LCSC (e.g. a bare module/header)
are written to bom_unassigned.csv to hand-assemble — NOT dropped silently.

    python3 scripts/gen_bom_cpl.py [base=index]   ->  fab/bom.csv  fab/cpl.csv  [fab/bom_unassigned.csv]
"""
import json, csv, subprocess, os, sys, tempfile

base = sys.argv[1] if len(sys.argv) > 1 else "index"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
os.makedirs("fab", exist_ok=True)


def fmt(e):
    r, c = e.get("resistance"), e.get("capacitance")
    if r is not None:
        for d, s in ((1e6, "M"), (1e3, "k"), (1, "")):
            if r >= d: return f"{r/d:g}{s}".rstrip(".") + ("Ω" if s == "" else "")
    if c is not None:
        for d, s in ((1e-6, "uF"), (1e-9, "nF"), (1e-12, "pF")):
            if c >= d: return f"{c/d:g}{s}"
    return e.get("display_value") or e.get("name") or ""


arr = json.load(open(f"dist/{base}/circuit.json"))
parts = {}   # designator -> (comment, lcsc)
for e in arr:
    if e.get("type") != "source_component":
        continue
    name = e.get("name")
    if not name:
        continue
    jlc = (e.get("supplier_part_numbers") or {}).get("jlcpcb") or []
    parts[name] = (fmt(e), jlc[0] if jlc else None)

# CPL from kicad-cli (same origin as the gerbers)
pos = tempfile.mktemp(suffix=".csv")
subprocess.run(["kicad-cli", "pcb", "export", "pos", "--format", "csv", "--units", "mm",
                "--side", "both", "-o", pos, f"{base}.circuit.kicad_pcb"], capture_output=True)
rows = list(csv.DictReader(open(pos)))
pkg = {r["Ref"]: r["Package"] for r in rows if r["Ref"]}

# --- CPL (JLCPCB columns) ---
with open("fab/cpl.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    n = 0
    for r in rows:
        if not r["Ref"]:
            continue
        w.writerow([r["Ref"], f'{float(r["PosX"]):.4f}', f'{float(r["PosY"]):.4f}',
                    "top" if r["Side"] == "top" else "bottom", f'{float(r["Rot"]):.0f}'])
        n += 1

# --- BOM (group designators by LCSC) ---
grp, unassigned = {}, []
for ref, (comment, lcsc) in sorted(parts.items()):
    if lcsc is None:
        unassigned.append((ref, comment, pkg.get(ref, "")))
    else:
        grp.setdefault(lcsc, [comment, pkg.get(ref, ""), []])[2].append(ref)
with open("fab/bom.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for lcsc, (comment, fp, refs) in sorted(grp.items(), key=lambda kv: kv[1][2][0]):
        w.writerow([comment, ",".join(sorted(refs)), fp, lcsc])
if unassigned:
    with open("fab/bom_unassigned.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["Designator", "Comment", "Footprint"])
        for row in unassigned: w.writerow(row)

print(f"fab/cpl.csv : {n} placements")
print(f"fab/bom.csv : {len(grp)} unique parts ({sum(len(v[2]) for v in grp.values())} designators)")
if unassigned:
    print(f"fab/bom_unassigned.csv : {len(unassigned)} hand-assemble (no LCSC): "
          f"{', '.join(r[0] for r in unassigned)}")
