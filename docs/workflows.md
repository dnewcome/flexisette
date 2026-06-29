# Workflows — task recipes

The common tasks, as copy-paste recipes. Run PCB tasks from `pcb/`, CAD/render tasks from the repo root
(unless noted). Full target/script list in [reference.md](reference.md).

## Preview the circuit (schematic + PCB)

```
cd pcb
make build                       # build the composed board → dist/index/ (circuit.json, pcb.svg)
make dev                         # live viewer at https://localhost:3020 (3D tab too)
make render                      # dist PCB SVGs → PNGs in build/
```

## Iterate the floorplan fast (pre-routing)

The core early-design loop — drag parts visually, round-trip to data. See [placement.md](placement.md).

```
cd pcb
make untangle                    # auto-orient parts to shorten the ratsnest (good starting point)
make place                       # opens pcbnew on a throwaway board; drag/rotate parts vs the ratsnest
make sync                        # pull your moves back into placement/default.json
make outline                     # gate: every part inside the outline, off the cutouts
```

Add `VARIANT=glow` to any of these to work on a different release's floorplan.

## Route the board

```
cd pcb
bash scripts/route.sh            # full pipeline: export → apply placement → merge nets → keepout cutouts
                                 #   → Freerouting → relaunch pcbnew → GND plane → IPC-inject SES → DRC
python3 scripts/drc_check.py index.circuit.kicad_pcb     # triage: shorts / edge-over-cut / unconnected / cosmetic
```

(There is no `make route` — the pipeline is `scripts/route.sh`. `make freeroute` is the standalone
router-only path.) Note the placement→DSN gap in [placement.md](placement.md) before routing a *changed*
placement.

## Generate fab files

```
cd pcb
make fab                         # fab/flexisette_jlcpcb.zip (gerbers+drill) + bom.csv + cpl.csv
```

Then upload the zip (and BOM/CPL for assembly) to JLCPCB — see [fabrication.md](fabrication.md).

## Make a release variant (a unique board)

```
cd pcb
make variant V=glow              # fork placement/default.json → placement/glow.json
make place VARIANT=glow          # lay it out differently; make sync VARIANT=glow to save
# route/fab it by pointing route.sh / make fab at the glow placement (set VARIANT)
```

Same circuit, different floorplan → a different physical board per drop.

## 3D fit-check (board vs printed shell)

```
cd pcb
make fit                         # builds pcb.stl (bare) + pcb_pop.stl (populated) + oled.stl, renders:
                                 #   cad/build/fit_iso.png  (exploded), fit_top.png (alignment),
                                 #   fit_pop.png (component bodies)
make show                        # open the renders + print the 3D-model paths
```

See [3d-fit-and-renders.md](3d-fit-and-renders.md). The importer prints a board-outline-vs-shell delta
(it currently flags a +1.7 mm overhang — a real param mismatch, see [roadmap.md](roadmap.md)).

## Build the printed cassette parts

```
# from repo root
python3 cad/machine.py [head|dummy]      # the assembly: per-part STLs + a combined STEP → cad/build/
python3 cad/frame.py                     # an individual part
make <target>                            # top-level Makefile has CAD + Blender-render targets (see reference.md)
```

See [cad-enclosure.md](cad-enclosure.md).

## Render the full assembly (beauty shot)

```
# OpenSCAD (here, flat-shaded): produced by `make fit` → cad/build/fit_iso.png
# Blender (photoreal): needs a GPU box (OPTIX)
python3 render/render_assembly.py        # → render/out/flexisette_assembly.png  (real board + frame + panel + insert + OLED)
```

Set `EXPL = 0` near the top of `render_assembly.py` for a closed-up cassette instead of slightly exploded.

## Add the OLED to the GLB

```
cd pcb && tsci export index.circuit.tsx -f glb -o build/3d/flexisette.glb   # board + CDN component bodies
python3 ../cad/merge_oled_glb.py                                            # + OLED → build/3d/flexisette_oled.glb
```

(The GLB isn't wired into `make fit` — regenerate it manually after a layout change. See [roadmap.md](roadmap.md).)

## See / open the generated files

Everything lands in **gitignored `build/`, `dist/`, `fab/` dirs** — real files, just not committed.

```
cd pcb && make show              # opens the fit renders + prints GLB/STL paths
```

- **Renders (PNG):** `cad/build/fit_*.png`, `render/out/*.png` → any image viewer.
- **3D (GLB):** `pcb/build/3d/flexisette_oled.glb` → drag into https://gltf-viewer.donmccurdy.com, or
  Blender / the OS 3D viewer.
- **3D (STL/STEP):** `cad/build/*.stl`, `pcb/build/3d/*.step` → a 3D/CAD viewer.
- **Live interactive 3D of the board:** `cd pcb && tsci dev` → localhost:3020, 3D tab.

## Run the tests

```
cd pcb && make test              # node --test tests/*.test.mjs  (autoplace + untangle pure cores)
```
