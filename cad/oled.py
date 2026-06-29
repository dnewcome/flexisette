"""oled.py — 0.96" SSD1306 OLED module, as a render/fit prop for the cassette assembly.

tscircuit can't draw this part in 3D (the 0.96" module has no CDN 3D model), so we model it: the
blue module PCB + the dark glass screen + the 4-pin header. It mounts on the BACK of the board,
screen facing out through the tape-window cutout. Exports two STLs so the render can colour the
screen separately from the board:
    cad/build/oled.stl        — module PCB + header (blue)
    cad/build/oled_screen.stl — the glass/active area (near-black)

Origin: module centred in XY; back-of-module at z=0; screen on the +Z face (so place it screen-up
behind the board). The header sits at the module's -Y edge (where it solders to the board).

    py/bin/python cad/oled.py  ->  cad/build/oled.stl + oled_screen.stl
"""
import os
from build123d import *

MOD_W, MOD_H, MOD_T = 27.0, 27.0, 1.2          # module PCB (matches the 27x27 silk body)
GLASS_W, GLASS_H, GLASS_T = 25.5, 16.5, 1.4    # display glass
GLASS_DY = 0.0                                   # active area centred on the module = on the tape window
ACT_W, ACT_H, ACT_T = 21.7, 10.9, 0.3          # 128x64 active area (the lit rectangle)
HDR_W, HDR_H, HDR_T = 10.5, 2.6, 2.6           # 4-pin header at the -Y edge, on the BACK (-Z)


def module():
    pcb = Box(MOD_W, MOD_H, MOD_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hdr = Pos(0, -MOD_H / 2 + HDR_H / 2, -HDR_T) * Box(HDR_W, HDR_H, HDR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return pcb.fuse(hdr)


def screen():
    glass = Pos(0, GLASS_DY, MOD_T) * Box(GLASS_W, GLASS_H, GLASS_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    act = Pos(0, GLASS_DY, MOD_T + GLASS_T) * Box(ACT_W, ACT_H, ACT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return glass.fuse(act)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "build"), exist_ok=True)
    for name, solid in (("oled", module()), ("oled_screen", screen())):
        p = os.path.join(here, "build", f"{name}.stl")
        export_stl(solid, p)
        import trimesh
        m = trimesh.load(p)
        print(f"{name}: {tuple((m.bounds[1]-m.bounds[0]).round(1))} mm  watertight={m.is_watertight}")
