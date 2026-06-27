"""flexisette shell assembly — PCB(bottom) + spacer + PCB(top).

Usage:  python3 machine.py [head|dummy]   (default: head)
Exports positioned assembly parts + a raw spacer (at origin) for clean part renders,
plus a combined STEP. Stack Z datums are param-derived (the layout owns them).
"""
import os
import sys
from build123d import Compound, Pos, export_stl, export_step
import machine_params as M
import pcb_half
import spacer


def assembly(spacer_variant="head"):
    return [
        ("pcb_bottom", Pos(0, 0, 0) * pcb_half.part()),
        ("spacer",     Pos(0, 0, M.PCB_T) * spacer.part(spacer_variant)),
        ("pcb_top",    Pos(0, 0, M.PCB_T + M.SPACER_GAP) * pcb_half.part()),
    ]


if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "head"
    here = os.path.dirname(os.path.abspath(__file__))
    bdir = os.path.join(here, "build")
    os.makedirs(bdir, exist_ok=True)

    # raw spacer at origin — for clean single-part renders / printing
    export_stl(spacer.part(variant), os.path.join(bdir, f"spacer_{variant}.stl"))

    parts = assembly(variant)
    suffix = "" if variant == "head" else f"_{variant}"   # head keeps default names (render_shell.py)
    print(f"MANIFEST (flexisette shell, spacer={variant})")
    for name, p in parts:
        bb = p.bounding_box()
        print(f"  {name:11s} bbox={tuple(round(v,2) for v in bb.size)}  z=[{bb.min.Z:.2f},{bb.max.Z:.2f}]")
        export_stl(p, os.path.join(bdir, f"{name}{suffix}.stl"))

    comp = Compound(children=[p for _, p in parts])
    bb = comp.bounding_box()
    print(f"  {'TOTAL':11s} bbox={tuple(round(v,2) for v in bb.size)}")
    export_step(comp, os.path.join(bdir, f"flexisette_shell_{variant}.step"))
    print("exported ->", bdir)
