#!/usr/bin/env python3
"""freecad_export.py — emit EDITABLE FreeCAD feature trees for the flexisette parts.

Expresses each part's build123d operations as `featuretree` IR (reusing the SAME extracted
geometry the build123d scripts use), then emits <part>.FCStd via the featuretree skill — so the
parts open in FreeCAD with their operations in the left-panel tree, alongside the STEP exports.

    python3 cad/freecad_export.py
"""
import os
import sys

SKILL = os.path.expanduser("~/.claude/skills/featuretree")
sys.path.insert(0, SKILL)
import ir                      # noqa: E402  (featuretree DSL)
from gen import emit          # noqa: E402  (IR -> .FCStd via freecadcmd)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import machine_params as M     # noqa: E402
import frame as FR             # noqa: E402
import panel as PA             # noqa: E402
import insert as INS           # noqa: E402
import trimesh                 # noqa: E402
from shapely.geometry import Polygon as SPoly  # noqa: E402


def frame_spec():
    """profile (outline - cavity) -> pad -> blind tap pilots from each face."""
    ext, cav, screws = FR._extract()
    pr, dep = M.SCREW_PILOT_D / 2, M.SCREW_PILOT_DEPTH
    return ir.part(
        "frame",
        ir.sketch("profile", polys=[ext, cav]),
        ir.pad("body", "profile", length=M.SPACER_GAP),
        ir.sketch("pilots_top", on={"face_of": "body", "side": "top"},
                  circles=[(x, y, pr) for x, y in screws]),
        ir.pocket("tap_top", "pilots_top", through=False, length=dep),
        ir.sketch("pilots_bot", on={"face_of": "body", "side": "bottom"},
                  circles=[(x, y, pr) for x, y in screws]),
        ir.pocket("tap_bot", "pilots_bot", through=False, length=dep),
    )


def panel_spec():
    """face profile with reel/window/screw holes (all wires in one sketch) -> pad."""
    ext, holes = PA._rings()
    return ir.part(
        "panel",
        ir.sketch("face", polys=[ext] + holes),
        ir.pad("body", "face", length=M.PANEL_T),
    )


def insert_spec():
    """Reverse-engineered from the fused vendor mesh: project the front silhouette (the
    trapezoid + the head/capstan through-openings), then pad it. A padded profile is solid,
    so this also fills the hollow shell — the editable, solid insert in one step."""
    m = INS.solid()                                  # the fused mesh (rotZ mate of both halves)
    p = m.projected(normal=[0, 1, 0])                # front silhouette -> (X, Z)
    outer = max(p.polygons_full, key=lambda g: g.area)
    b = outer.bounds
    cx, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    xy = lambda ring: [(x - cx, z - cz) for (x, z) in ring]
    ext = xy(list(SPoly(outer.exterior).simplify(0.4).exterior.coords))[:-1]
    holes = [xy(list(SPoly(r).simplify(0.3).exterior.coords))[:-1]
             for r in outer.interiors if SPoly(r).area > 0.5]
    thick = float(m.extents[1])                      # Y thickness (~9 mm)
    return ir.part(
        "insert",
        ir.sketch("profile", polys=[ext] + holes),
        ir.pad("body", "profile", length=thick),
    )


if __name__ == "__main__":
    bdir = os.path.join(HERE, "build")
    os.makedirs(bdir, exist_ok=True)
    for name, spec in (("frame", frame_spec()), ("panel", panel_spec()), ("insert", insert_spec())):
        res = emit(spec, os.path.join(bdir, f"{name}.FCStd"))
        tree = " > ".join(t[0] for t in res["tree"])
        print(f"{name}.FCStd  vol {res['volume']} mm^3  tree: {tree}")
