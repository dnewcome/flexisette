"""head_frame.py — flexisette monolithic head-holes spacer FRAME with PCB screw bosses.

A single watertight body: a cassette-outline perimeter frame at the inter-PCB gap height
(parametric: SPACER_GAP = CASSETTE_T - 2*PCB_T), with a head-access window in the front wall
and four corner bosses ("tabs") bored for M2 heat-set inserts so the top & bottom PCB halves
screw to it. Head geometry is parametric (matched to the measured insert), not the literal mesh.

    python3 cad/head_frame.py        -> build/head_frame.stl + build/head_frame.step
"""
import os
from build123d import *
import machine_params as M

W, H, R = M.SHELL_W, M.SHELL_H, M.CORNER_R
WALL, GAP = M.WALL, M.SPACER_GAP
BX, BY = W / 2 - M.SCREW_INSET, H / 2 - M.SCREW_INSET          # boss centres (corners)
BOSSES = [(BX, BY), (-BX, BY), (BX, -BY), (-BX, -BY)]


def part():
    with BuildPart() as bp:
        # --- perimeter frame (one extrude) ---
        with BuildSketch():
            RectangleRounded(W, H, R)
            RectangleRounded(W - 2 * WALL, H - 2 * WALL, max(R - WALL, 0.6), mode=Mode.SUBTRACT)
        extrude(amount=GAP)

        # --- corner screw bosses, fused in the same context (they overlap the corner walls) ---
        with BuildSketch():
            with Locations(*BOSSES):
                Circle(M.SCREW_BOSS_D / 2)
        extrude(amount=GAP)

        # --- head-access window through the front wall (front = -Y) ---
        with Locations((0, M.FRONT_Y, GAP / 2)):
            Box(M.HEAD_WIN_W, WALL * 3, M.HEAD_WIN_H, mode=Mode.SUBTRACT)

        # --- capstan / guide clearance holes through the front wall (axis along Y) ---
        with Locations((M.CAPSTAN_DX, M.FRONT_Y, GAP / 2), (-M.CAPSTAN_DX, M.FRONT_Y, GAP / 2)):
            Cylinder(M.CAPSTAN_D / 2, WALL * 3, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # --- M2 heat-set bores through the bosses (overshoot both faces) ---
        with Locations(*[(x, y, GAP / 2) for (x, y) in BOSSES]):
            Cylinder(M.SCREW_HEATSET_D / 2, GAP + 2, mode=Mode.SUBTRACT)

    return bp.part


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    bdir = os.path.join(here, "build")
    os.makedirs(bdir, exist_ok=True)
    p = part()
    stl = os.path.join(bdir, "head_frame.stl")
    export_stl(p, stl)
    export_step(p, os.path.join(bdir, "head_frame.step"))
    import trimesh
    m = trimesh.load(stl)
    print("head_frame:", (m.bounds[1] - m.bounds[0]).round(2),
          "bodies:", len(m.split(only_watertight=False)),
          "watertight:", m.is_watertight,
          "| PCB_T", M.PCB_T, "GAP", round(GAP, 2), "CASSETTE_T", M.CASSETTE_T)
