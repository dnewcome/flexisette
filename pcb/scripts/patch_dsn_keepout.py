#!/usr/bin/env python3
"""patch_dsn_keepout.py — add a keepout rect to a Specctra DSN so Freerouting avoids it.

tscircuit's <cutout> exports ONLY as an Edge.Cuts hole, NOT as a routing keepout — so
Freerouting happily routes traces straight across a board window (e.g. the OLED tape-window
cutout). Insert the cutout as a per-layer keepout in the DSN before `freert` and it stays clear.

Coords are tscircuit FRAME mm (the same numbers as the <cutout> pcbX/pcbY/width/height).
DSN placement scale is auto-detected (tscircuit exports placement at ~1000 units/mm).

Usage:
  python3 patch_dsn_keepout.py <dsn> <cx_mm> <cy_mm> <w_mm> <h_mm> [--margin MM] [--scale N]
"""
import sys, re

def opt(flag, default):
    return float(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default

def detect_scale(txt):
    # boundary is the board outline; its max |coord| / (board half-size in mm) ~ scale.
    m = re.search(r'\(boundary\s*\(path \S+ \S+\s+([-\d.\s]+)\)', txt)
    if not m:
        return 1000.0
    nums = [abs(float(x)) for x in m.group(1).split()]
    mx = max(nums) if nums else 0
    # tscircuit placement DSNs come out at 1000 u/mm (a 50mm half-board => ~50000).
    return 10000.0 if mx > 250000 else 1000.0

def main():
    if len(sys.argv) < 6:
        print(__doc__); sys.exit(1)
    dsn = sys.argv[1]
    cx, cy, w, h = (float(sys.argv[i]) for i in range(2, 6))
    margin = opt("--margin", 0.5)
    txt = open(dsn).read()
    scale = opt("--scale", 0) or detect_scale(txt)

    x1 = int((cx - w/2 - margin) * scale); x2 = int((cx + w/2 + margin) * scale)
    y1 = int((cy - h/2 - margin) * scale); y2 = int((cy + h/2 + margin) * scale)

    # signal copper layers (from the structure section, before placement)
    head = txt[:txt.index("(placement")] if "(placement" in txt else txt
    layers = re.findall(r'\(layer (\S+)', head)
    layers = [l for l in dict.fromkeys(layers) if l.endswith(".Cu")]

    # find the (boundary ...) block end by paren matching, insert keepouts right after it
    i = txt.index("(boundary"); depth = 0; j = i
    while j < len(txt):
        if txt[j] == "(": depth += 1
        elif txt[j] == ")":
            depth -= 1
            if depth == 0: break
        j += 1
    ko = "".join(f'\n    (keepout "cutout_{l}" (rect {l} {x1} {y1} {x2} {y2}))' for l in layers)
    txt = txt[:j+1] + ko + txt[j+1:]
    open(dsn, "w").write(txt)
    print(f"added keepout on {layers} @ scale {scale:g}: rect [{x1},{y1} {x2},{y2}] "
          f"(= frame {cx}±{w/2}, {cy}±{h/2} mm + {margin} margin)")

if __name__ == "__main__":
    main()
