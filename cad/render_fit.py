"""render_fit.py — 3D fit-check of the routed PCB against the printed cassette parts.

Stacks the REAL board (cad/build/pcb.stl, from import_pcb.py) with the printed spacer frame,
top panel, and head insert at the machine_params Z datums, and renders two OpenSCAD views:
  build/fit_iso.png  — exploded iso (layers read apart, board cutouts vs frame visible)
  build/fit_top.png  — straight top-down (window/reels/screws alignment check)

This is the placement-time 3D check: connector/window/reel positions on the board are only
right if they line up with the printed shell openings. Run it after each place/route pass:
    py/bin/python cad/import_pcb.py && py/bin/python cad/render_fit.py
"""
import os, subprocess, sys
import machine_params as M

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
PCB_T, GAP = M.PCB_T, M.SPACER_GAP
TOP_Z = PCB_T + GAP                       # top layer datum (== machine.py)

LAYERS = [   # (stl, z_mm, [r,g,b], explode_factor)
    ("pcb.stl",   0.0,    [0.10, 0.45, 0.20], -1.0),   # real board (green) — bottom
    ("frame.stl", PCB_T,  [0.62, 0.63, 0.66],  0.0),   # printed spacer frame (grey)
    ("panel.stl", TOP_Z,  [0.83, 0.34, 0.06], +1.0),   # printed top panel (warm)
]


def scad(explode):
    lines = ["$fn=48;"]
    for stl, z, c, ef in LAYERS:
        p = os.path.join(B, stl)
        if not os.path.exists(p):
            continue
        lines.append(f'color([{c[0]},{c[1]},{c[2]}]) translate([0,0,{z + ef*explode:.3f}]) import("{p}");')
    ins = os.path.join(B, "insert.stl")          # head insert: thickness->Z, head face -> -Y, front edge
    if os.path.exists(ins):
        lines.append(f'color([0.45,0.06,0.06]) translate([0,{-M.SHELL_H/2:.2f},{PCB_T:.2f}]) '
                     f'rotate([90,0,0]) import("{ins}");')
    return "\n".join(lines)


def render(name, cam, explode):
    s = os.path.join(B, f"_fit_{name}.scad")
    open(s, "w").write(scad(explode))
    out = os.path.join(B, f"fit_{name}.png")
    subprocess.run(["openscad", "-o", out, "--imgsize=1200,800", "--colorscheme=Tomorrow",
                    f"--camera={cam}", "--autocenter", "--viewall", s], capture_output=True)
    print("  ->", out, "OK" if os.path.exists(out) else "FAILED")


def render_pop():
    """populated board (tscircuit, with component bodies) under the spacer frame — connector /
    display protrusion + clearance vs the shell openings."""
    p = os.path.join(B, "pcb_pop.stl")
    if not os.path.exists(p):
        return
    f = os.path.join(B, "frame.stl")
    lines = ['$fn=48;', f'color([0.10,0.42,0.20]) import("{p}");']
    if os.path.exists(f):
        lines.append(f'%color([0.6,0.62,0.66]) translate([0,0,{PCB_T:.2f}]) import("{f}");')  # ghosted
    s = os.path.join(B, "_fit_pop.scad"); open(s, "w").write("\n".join(lines))
    out = os.path.join(B, "fit_pop.png")
    subprocess.run(["openscad", "-o", out, "--imgsize=1200,800", "--colorscheme=Tomorrow",
                    "--camera=0,0,0,62,0,25,400", "--autocenter", "--viewall", s], capture_output=True)
    print("  ->", out, "OK (populated: component bodies)" if os.path.exists(out) else "FAILED")


def main():
    os.makedirs(B, exist_ok=True)
    expl = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
    print(f"fit-check render (explode={expl}mm):")
    render("iso", "0,0,0,58,0,22,420", expl)      # exploded iso (bare board layers)
    render("top", "0,0,0,0,0,0,420", 0.0)          # top-down alignment (no explode)
    render_pop()                                   # populated board (component bodies) if present


if __name__ == "__main__":
    main()
