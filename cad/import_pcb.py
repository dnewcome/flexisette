"""import_pcb.py — bring the board into the cad assembly as an STL, two ways.

Dispatches on the source extension:
  *.kicad_pcb  -> kicad-cli STEP (the ROUTED board, but BARE — tscircuit footprints carry no
                  KiCad 3D models). Y-mirrored (KiCad is Y-down). -> build/pcb.stl
                  Clean flat plate — best for layer registration (outline/cutouts/screws vs frame).
  *.tsx        -> tsci export -f step (the POPULATED board — 30 cad_components with real EasyEDA
                  3D models from the CDN: USB-C, ESP32, amp + generic passives). Already centered
                  + Y-up, no flip. -> build/pcb_pop.stl
                  Carries component BODIES — best for connector/display protrusion + clearance.

Both are centered on the cassette origin. Run after each place/route pass:
    python3 import_pcb.py ../pcb/index.circuit.kicad_pcb   # bare, for the stack
    python3 import_pcb.py ../pcb/index.circuit.tsx         # populated, for connector bodies
"""
import subprocess, os, sys
from build123d import import_step, export_stl, Pos, mirror, Plane
import machine_params as M

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
STEP = "/tmp/_pcb_fit.step"


def export_step(src):
    src = os.path.abspath(src)
    if src.endswith(".tsx"):
        pcb = os.path.join(HERE, "..", "pcb")
        env = {**os.environ, "PATH": f"{os.environ['HOME']}/.bun/bin:{os.environ.get('PATH','')}"}
        tsci = os.path.join(pcb, "node_modules", ".bin", "tsci")
        # tsci mangles an absolute -o; write relative to pcb/ (the copperpour async warning is benign)
        subprocess.run([tsci, "export", src, "-f", "step", "-o", "build/_pop.step"],
                       cwd=pcb, env=env, capture_output=True, text=True, timeout=240)
        p = os.path.join(pcb, "build", "_pop.step")
        return p if os.path.exists(p) else None
    subprocess.run(["kicad-cli", "pcb", "export", "step", "--subst-models", "--no-dnp",
                    "-o", STEP, src], capture_output=True, text=True)   # nonzero on warnings; trust the file
    return STEP if os.path.exists(STEP) else None


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "pcb", "index.circuit.kicad_pcb")
    populated = src.endswith(".tsx")
    os.makedirs(B, exist_ok=True)

    step = export_step(src)
    if not step:
        sys.exit(f"3D export produced no file for {src}")
    s = import_step(step)
    bb = s.bounding_box()
    cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
    s = Pos(-cx, -cy, -bb.min.Z) * s          # center XY, lowest point -> z=0
    if not populated:
        s = mirror(s, Plane.XZ)               # KiCad Y-down -> cad Y-up (tscircuit is already Y-up)

    out = os.path.join(B, "pcb_pop.stl" if populated else "pcb.stl")
    export_stl(s, out)
    b = s.bounding_box()
    print(f"{'populated (tscircuit, +bodies)' if populated else 'bare (kicad, routed)'}: "
          f"{b.size.X:.1f} x {b.size.Y:.1f} x {b.size.Z:.2f} mm -> {out}")
    if not populated:
        dx = b.size.X - M.SHELL_W
        print(f"  outline vs shell {M.SHELL_W}x{M.SHELL_H}: "
              f"{'MATCH' if abs(dx) < 1 else f'dX={dx:+.1f}mm overhang'}")


if __name__ == "__main__":
    main()
