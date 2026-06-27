"""panel.py — flexisette printed face panel (a 3D-printed stand-in for a PCB on one side).

Same real cassette-face profile as the frame (extracted from the vendor plain shell), with the
reel holes + tape window + the 4 corner screw holes. Thickness = PANEL_T (defaults to a PCB so
the stack stays panel + frame + PCB = 9 mm). Caps the frame on one face; a PCB goes on the other.
Print the cassette art as a multicolor first layer, like the vendor.

Source: Printables #836410 (see assets/DOWNLOADS.md).

    python3 cad/panel.py -> build/panel.stl + build/panel.step
"""
import os
import trimesh
from shapely.geometry import Polygon as SPoly
from build123d import BuildPart, BuildSketch, Polygon, extrude, export_stl, export_step, Mode
import machine_params as M

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets", "cassette-shell-minecraft", "side-1-plain.stl")
PANEL_T = M.PANEL_T
SIMP = 0.4


def _rings():
    m = trimesh.load(SRC)
    p = m.projected(normal=[0, 1, 0])
    outer = max(p.polygons_full, key=lambda g: g.area)
    b = outer.bounds
    ch, cw = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    xy = lambda ring: [(a1 - cw, a0 - ch) for (a0, a1) in ring]
    ext = xy(list(SPoly(outer.exterior).simplify(SIMP).exterior.coords))[:-1]
    holes = [xy(list(SPoly(r).simplify(SIMP * 0.5).exterior.coords))[:-1] for r in outer.interiors]
    return ext, holes


def part():
    ext, holes = _rings()
    with BuildPart() as bp:
        with BuildSketch():
            Polygon(*ext, align=None)
            for h in holes:
                Polygon(*h, align=None, mode=Mode.SUBTRACT)
        extrude(amount=PANEL_T)
    return bp.part


if __name__ == "__main__":
    bdir = os.path.join(HERE, "build")
    os.makedirs(bdir, exist_ok=True)
    e, holes = _rings()
    p = part()
    stl = os.path.join(bdir, "panel.stl")
    export_stl(p, stl)
    export_step(p, os.path.join(bdir, "panel.step"))
    import trimesh as tm
    mm = tm.load(stl)
    print("panel:", (mm.bounds[1] - mm.bounds[0]).round(2),
          "bodies", len(mm.split(only_watertight=False)),
          "watertight", mm.is_watertight,
          f"| holes {len(holes)}  thickness {PANEL_T:.2f}mm")
