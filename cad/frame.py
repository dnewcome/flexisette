"""frame.py — flexisette thin frame, profile extracted from the real vendor shell.

Projects the plain shell face (Printables #836410, see assets/DOWNLOADS.md) to get the true
cassette outline — including the angled bottom and the protrusion cutout — plus the 4 corner
screw positions, then builds a perimeter frame of thickness SPACER_GAP (= 9 - 2x1.57 = 5.86 mm)
with the screw holes drilled.

    python3 cad/frame.py -> build/frame.stl + build/frame.step
"""
import os
import trimesh
from shapely.geometry import Polygon as SPoly, Point
from build123d import BuildPart, BuildSketch, Polygon, Cylinder, Locations, extrude, export_stl, export_step, Mode
import machine_params as M

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets", "cassette-shell-minecraft", "side-1-plain.stl")
WALL, GAP = M.WALL, M.SPACER_GAP
PILOT_D, PILOT_DEPTH, BOSS_D = M.SCREW_PILOT_D, M.SCREW_PILOT_DEPTH, M.SCREW_BOSS_D
SIMP = 0.4                          # outline simplify tolerance (mm)


def _extract():
    m = trimesh.load(SRC)
    p = m.projected(normal=[0, 1, 0])                       # face-on silhouette
    outer = max(p.polygons_full, key=lambda g: g.area)
    b = outer.bounds
    ch, cw = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2           # geometric centre (proj a0=height, a1=width)
    xy = lambda ring: [(a1 - cw, a0 - ch) for (a0, a1) in ring]   # -> frame (x=width, y=height)

    # screw centroids in projection coords (a0, a1)
    screws_proj = [(SPoly(r).centroid.x, SPoly(r).centroid.y)
                   for r in outer.interiors if SPoly(r).area < 15]

    ext_pts = xy(list(SPoly(outer.exterior).simplify(SIMP).exterior.coords))[:-1]

    # cavity = inset perimeter, MINUS a boss disc at each screw so the corners stay solid/thick
    cav = SPoly(outer.exterior).buffer(-WALL, join_style="mitre")
    for (a0, a1) in screws_proj:
        cav = cav.difference(Point(a0, a1).buffer(BOSS_D / 2))
    if cav.geom_type == "MultiPolygon":
        cav = max(cav.geoms, key=lambda g: g.area)
    cav_pts = xy(list(cav.simplify(SIMP).exterior.coords))[:-1]

    screws = [(a1 - cw, a0 - ch) for (a0, a1) in screws_proj]   # -> frame coords
    return ext_pts, cav_pts, screws


def part():
    ext_pts, cav_pts, screws = _extract()
    with BuildPart() as bp:
        with BuildSketch():
            Polygon(*ext_pts, align=None)
            Polygon(*cav_pts, align=None, mode=Mode.SUBTRACT)
        extrude(amount=GAP)
        # blind thread-forming pilots from BOTH faces (top + bottom PCB each tap in)
        with Locations(*[(x, y, GAP) for (x, y) in screws]):
            Cylinder(PILOT_D / 2, PILOT_DEPTH * 2, mode=Mode.SUBTRACT)
        with Locations(*[(x, y, 0) for (x, y) in screws]):
            Cylinder(PILOT_D / 2, PILOT_DEPTH * 2, mode=Mode.SUBTRACT)
    return bp.part


if __name__ == "__main__":
    bdir = os.path.join(HERE, "build")
    os.makedirs(bdir, exist_ok=True)
    e, i, s = _extract()
    p = part()
    stl = os.path.join(bdir, "frame.stl")
    export_stl(p, stl)
    export_step(p, os.path.join(bdir, "frame.step"))
    import trimesh as tm
    mm = tm.load(stl)
    print("frame:", (mm.bounds[1] - mm.bounds[0]).round(2),
          "bodies", len(mm.split(only_watertight=False)),
          "watertight", mm.is_watertight,
          f"| outline_pts {len(e)}  screws {len(s)}  thickness {GAP:.2f}mm")
