# flexisette documentation

Start with **[architecture.md](architecture.md)** for the big picture, then dive into a subsystem.

| Doc | What it covers |
|---|---|
| **[architecture.md](architecture.md)** | The whole system: the three subsystems (PCB / placement / CAD), the fit-check seam, the data flow, the four coordinate frames, the repo map, and the reproducibility principles. **Read first.** |
| [pcb-toolchain.md](pcb-toolchain.md) | The board: modular `<subcircuit>` architecture, the parts/nets/cutouts, and the tscircuit→KiCad place→route→IPC-inject pipeline (`route.sh` + helpers). |
| [placement.md](placement.md) | The fast early-design loop: positions-as-data, the `place`/`sync`/`variant` round-trip, the auto-untangle (rotation), block autoplace, the placement gates, and the planned constraint layer. |
| [cad-enclosure.md](cad-enclosure.md) | The 3D-printed cassette shell (build123d): the sandwich stack, `machine_params.py`, each part, the head insert + screw bosses, and the assembly. |
| [3d-fit-and-renders.md](3d-fit-and-renders.md) | The seam + the pictures: bare vs populated board into 3D, the coordinate transforms, the OLED model, the OpenSCAD fit-check, the GLB merge, and the Blender beauty render. |
| [fabrication.md](fabrication.md) | Gerbers + assembly BOM/CPL (`make fab`), uploading to JLCPCB, and what the DFM does/doesn't catch. |
| [workflows.md](workflows.md) | Task recipes — copy-paste commands for the common things (route, fab, variant, fit-check, render, see the files). |
| [reference.md](reference.md) | Exhaustive reference: every make target, every script, every generated artifact, every data-file format. |
| [roadmap.md](roadmap.md) | Known gaps + discrepancies + the (grounded) future-work directions. |
| [placement-constraints.md](placement-constraints.md) | Design (plan only) for the per-part lock / move / rotate constraint layer. |

## Orientation for a newcomer

- The object is a **cassette-shaped PCB** in a **3D-printed cassette shell**, with an OLED behind the
  tape window. It regenerates entirely from source — see *reproducibility principles* in
  [architecture.md](architecture.md).
- **PCB work** is in `pcb/` (run make targets from there); **mechanical CAD** is in `cad/` (run from the
  repo root). The two meet in the **3D fit-check** (`make fit`).
- If you just want to *see* the current design: `cd pcb && make show`, or `make fit` then open
  `cad/build/fit_iso.png`.
- If something says "where's the file?" — generated artifacts live in **gitignored `build/`/`dist/`/`fab/`**
  dirs (real files, not committed); the map is in [reference.md](reference.md).
