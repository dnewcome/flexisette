"""pcb/board_outline.py — flexisette PCB board edge + OLED window, from the real cassette profile.

Single source of truth = cad/panel.py's extracted cassette outline. We add the OLED cutout exactly
where the cassette's central tape window is (21.2 x 12 mm), so a 0.96" 128x64 SSD1306 mounts behind
the board and lights up in the window. Emits, into pcb/build/:
  - board_outline.dxf  : Edge.Cuts outline + OLED window + drills, for KiCad DXF import
  - board_outline.png  : annotated preview (board, window, OLED active area, reels, mounts)

    python3 pcb/board_outline.py
"""
import os
import sys

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from shapely.geometry import Polygon as SPoly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cad"))
import panel  # noqa: E402  (reuse the extracted cassette rings)

# --- OLED: 0.96" 128x64 SSD1306 -------------------------------------------------
OLED_ACTIVE = (21.7, 10.9)        # visible/lit area (mm)  ~ matches the 21.2x12 window
OLED_CUT = (22.5, 13.0)           # PCB cutout WxH: clears active area + glass margin
WIN_C = (0.0, 3.0)                # tape-window center, frame coords (where the cutout goes)
OLED_MOUNT = 11.5                 # M2 standoff holes at +-this around the window (module ~27mm)
MOUNT_D = 2.2                     # M2 clearance


def classify(holes):
    """Split the profile's interior rings into: tape window, reel holes, screw/corner holes."""
    win, reels, screws = None, [], []
    for h in holes:
        p = SPoly(h)
        c, a = p.centroid, p.area
        if a > 150:
            win = h
        elif a > 40 and abs(c.x) > 15:
            reels.append((c.x, c.y, (p.bounds[2] - p.bounds[0]) / 2))
        else:
            screws.append((c.x, c.y, (p.bounds[2] - p.bounds[0]) / 2))
    return win, reels, screws


def oled_cut_poly():
    w, h = OLED_CUT
    cx, cy = WIN_C
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
            (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]


def write_dxf(ext, cut, mounts, screws, path):
    doc = ezdxf.new("R2010")
    doc.layers.add("Edge.Cuts", color=5)
    doc.layers.add("Drill", color=1)
    msp = doc.modelspace()
    msp.add_lwpolyline(ext, close=True, dxfattribs={"layer": "Edge.Cuts"})
    msp.add_lwpolyline(cut, close=True, dxfattribs={"layer": "Edge.Cuts"})
    for (x, y, r) in mounts:
        msp.add_circle((x, y), r, dxfattribs={"layer": "Drill"})
    for (x, y, r) in screws:
        msp.add_circle((x, y), r, dxfattribs={"layer": "Drill"})
    doc.saveas(path)


def preview(ext, cut, reels, screws, mounts, path):
    fig, ax = plt.subplots(figsize=(9, 6))
    xs, ys = zip(*(ext + [ext[0]]))
    ax.plot(xs, ys, "k-", lw=1.8, label="board edge (Edge.Cuts)")
    cxs, cys = zip(*(cut + [cut[0]]))
    ax.plot(cxs, cys, "r-", lw=1.6, label="OLED cutout 22.5x13")
    aw, ah = OLED_ACTIVE
    ax.add_patch(Rectangle((WIN_C[0] - aw / 2, WIN_C[1] - ah / 2), aw, ah,
                           fill=True, fc="#ff8800", ec="#aa5500", alpha=0.35,
                           label="OLED active 21.7x10.9"))
    for (x, y, r) in reels:
        ax.add_patch(Circle((x, y), r, fill=False, ec="0.6", ls="--"))
    for (x, y, r) in screws:
        ax.add_patch(Circle((x, y), max(r, 1.0), fill=True, fc="#3366cc"))
    for (x, y, r) in mounts:
        ax.add_patch(Circle((x, y), r, fill=True, fc="#33aa66"))
    ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_title("flexisette PCB v0 — board edge + OLED in the tape window")
    ax.legend(loc="lower center", ncol=2, fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


if __name__ == "__main__":
    bdir = os.path.join(HERE, "build")
    os.makedirs(bdir, exist_ok=True)
    ext, holes = panel._rings()
    win, reels, screws = classify(holes)
    cut = oled_cut_poly()
    mounts = [(sx * OLED_MOUNT, WIN_C[1] + sy * OLED_MOUNT, MOUNT_D / 2)
              for sx in (-1, 1) for sy in (-1, 1)]
    write_dxf(ext, cut, mounts, screws, os.path.join(bdir, "board_outline.dxf"))
    preview(ext, cut, reels, screws, mounts, os.path.join(bdir, "board_outline.png"))
    bx = [p[0] for p in ext]; by = [p[1] for p in ext]
    print(f"board {max(bx)-min(bx):.1f} x {max(by)-min(by):.1f} mm | "
          f"window {'found' if win else 'MISSING'} | reels {len(reels)} | "
          f"screws {len(screws)} | OLED cut {OLED_CUT[0]}x{OLED_CUT[1]} at {WIN_C}")
    print("wrote board_outline.dxf + board_outline.png")
