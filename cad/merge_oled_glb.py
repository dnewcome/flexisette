"""merge_oled_glb.py — add the modeled OLED into tscircuit's GLB (which omits it: no CDN 3D model).

tscircuit's `tsci export -f glb` bakes in the 30 CDN component models but not the SSD1306 (it has
none). This drops our cad/build/oled.stl into that GLB at the tape window, behind the board, and
writes a combined GLB you can open in any glTF viewer.

GLB frame is Y-up (gltf): X=width, Y=thickness/up, Z=depth. tscircuit (x,y) -> GLB (x,-z); the
bottom layer is Y<0. Our STL is build123d Z-up (screen on +Z), so rotate -90deg about X (screen->+Y)
then seat the screen just under the board at the window.

    python3 cad/merge_oled_glb.py [in.glb=build/3d/flexisette.glb] [out=build/3d/flexisette_oled.glb]
"""
import sys, os
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix, translation_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, "..", "pcb")
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PCB, "build/3d/flexisette.glb")
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PCB, "build/3d/flexisette_oled.glb")

scene = trimesh.load(src)
n0 = len(scene.geometry)

# screen +Z -> +Y (up), then seat screen at the board underside (y~0) over the window (z=-3)
M = translation_matrix([0, -2.9, -3]) @ rotation_matrix(-np.pi / 2, [1, 0, 0])
for name, stl, color in [("OLED", "oled.stl", [40, 60, 140, 255]),
                         ("OLED_screen", "oled_screen.stl", [10, 10, 18, 255])]:
    m = trimesh.load(os.path.join(HERE, "build", stl))
    m.apply_transform(M)
    m.visual.face_colors = color
    scene.add_geometry(m, node_name=name, geom_name=name)

scene.export(out)
ob = trimesh.load(os.path.join(HERE, "build", "oled.stl")).apply_transform(M).bounds
print(f"merged OLED into GLB: {n0} -> {len(scene.geometry)} meshes")
print(f"  OLED bbox in GLB frame: x[{ob[0][0]:.1f},{ob[1][0]:.1f}] y[{ob[0][1]:.1f},{ob[1][1]:.1f}] z[{ob[0][2]:.1f},{ob[1][2]:.1f}]")
print(f"  -> {out}")
