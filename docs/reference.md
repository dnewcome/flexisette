# flexisette — Reference

A flex-PCB cassette-tape multimedia object: a parametric, cassette-shaped board that plays
its own baked-in audio (ESP32-S3 → MAX98357A → speaker) with a 0.96″ SSD1306 OLED behind the
cassette's tape window playing a looping tape-winding animation, charged over USB-C off a LiPo.
The whole object regenerates from source — mechanical CAD, the PCB, the renders, and the display
animation — and lives inside a 3D-printed cassette shell.

This document is the fast lookup for "what command does X". Every make target, every script, and
every generated-artifact path below was read from the actual source files.

Repo root: `/home/dan/sandbox/dnewcome/flexisette`

## Layout at a glance

| Dir | What it holds |
|---|---|
| `cad/` | Parametric build123d CAD of the physical parts (frame, panel, insert, spacer, OLED prop) + the PCB↔enclosure 3D fit-check. Output → `cad/build/`. |
| `pcb/` | Code-driven PCB with tscircuit (`modules/*.circuit.tsx` → `index.circuit.tsx`), finished in KiCad. Place→route→measure tooling in `pcb/scripts/`, per-fab DRC rules in `pcb/rules/`. |
| `render/` | Headless Blender product renders (`render/*.py` + `blender_render.sh`). Output → `render/out/`. |
| `display/` | The 128×64 1-bit tape-winding OLED animation (`display/tape_anim.py`). Output → `display/build/`. |
| `assets/` | Vendor cassette-shell STL/STEP the CAD is derived from (provenance in `assets/DOWNLOADS.md`). |
| `specs/` | Early design specs A/B/C/D (the deck / slim / flex / flex-jcard). |
| `PARTS.md` | Component sourcing / BOM notes. |

There are **two Makefiles**: the **top-level** `Makefile` (mechanical CAD + Blender renders) and
**`pcb/Makefile`** (the PCB generate→place→route→fab flow). Run `pcb/` targets from inside `pcb/`.

---

## 1. Make targets

### Top-level `Makefile` (mechanical CAD + Blender renders)

`make` from the repo root. Overridable vars: `SAMPLES` (Cycles samples, default 180),
`BLENDER` (path, default `/opt/blender-5.0.1-linux-x64/blender`), `ATTEMPTS` (render retries,
default 5), `PY` (default `python3`).

| target | what it does | key vars |
|---|---|---|
| `all` *(default)* | Alias for `parts` — build every CAD part + render each + the assembly. | |
| `parts` | Render `frame`, `panel`, `insert`, and the stacked `assembly`. | SAMPLES |
| `cad` | build123d → STL+STEP for frame, panel, insert (`cad/build/*.stl/.step`). | PY |
| `frame` | Render `render/out/flexisette_frame.png` (builds `frame.stl` first). | BLENDER, ATTEMPTS |
| `panel` | Render `render/out/flexisette_panel.png`. | BLENDER, ATTEMPTS |
| `insert` | Render `render/out/flexisette_insert.png`. | BLENDER, ATTEMPTS |
| `assembly` | Render the exploded stack `render/out/flexisette_assembly.png` (+ `.blend`). | BLENDER, ATTEMPTS |
| `concepts` | Alias for `specs` + `sheet` — the early A/B/C/D concept hero renders + contact sheet. | SAMPLES |
| `specs` | Render `render/out/flexisette_{A,B,C,D}.png` from `build_render.py`. | SAMPLES |
| `sheet` | Montage the 4 spec PNGs into `render/out/flexisette_contact_sheet.png` (needs ImageMagick `montage`). | |
| `freecad` | Emit editable FreeCAD feature trees (`cad/build/*.FCStd`) via `freecad_export.py` (featuretree skill; needs FreeCAD AppImage). | PY |
| `blend-frame` | Open the frame scene in the **Blender GUI** (interactive). | BLENDER |
| `blend-panel` | Open the panel scene in the Blender GUI. | BLENDER |
| `blend-assembly` | Open the assembly scene in the Blender GUI. | BLENDER |
| `verify` | Watertight/validity self-checks (re-runs `frame.py` + `panel.py` + `insert.py`). | PY |
| `clean` | Remove generated STL/STEP/FCStd/ir.json in `cad/build/` and PNG/blend in `render/out/`. | |
| `view` | `xdg-open render/out/` (the render output folder). | |
| `help` | Print the target summary. | |

### `pcb/Makefile` (tscircuit generate → place → route → fab)

Run from `pcb/`. Default goal is `help`. `tsci` is invoked as `./node_modules/.bin/tsci` with
`~/.bun/bin` on PATH. Common vars: `FILE` (default `index.circuit.tsx`), `MODS`, `VARIANT`
(default `default`), `MOD`/`REF`/`POS`, `NAME`, `V`, `BOARD`/`BOARD` (default
`index.circuit.kicad_pcb`), `AP`, plus router env `MAXT`/`MP`/`OIT`/`TIMEOUT`/`DISPLAY`.

| target | what it does | key vars |
|---|---|---|
| `help` *(default)* | Print the `#   make …` usage lines from the Makefile. | |
| `dev` | `tsci dev $(FILE)` — live viewer at `https://localhost:3020` (3D tab too). | FILE |
| `build` | `tsci build index.circuit.tsx --pcb-only` → `dist/index/{circuit.json,pcb.svg}`. | |
| `modules` | Build every `modules/*.circuit.tsx` standalone (`--disable-parts-engine --pcb-only`). | |
| `outline` | **Board-outline rule**: `outline-check.mjs` flags parts outside the outline or inside a cutout. Exit 1 if any. | FILE |
| `routecheck` | **The measured loop**: `routecheck.sh` builds each module, reports per-block UNROUTED / TIME / PASS. | MODS, TIMEOUT |
| `freeroute` | Route the whole board with Freerouting (`freeroute.sh`: DSN → `freert` → `.ses`). | FILE, MAXT |
| `autoplace` | `autoplace.mjs` — anneal subcircuit-block positions (HPWL) under outline/cutout/courtyard gates. | FILE, AP |
| `untangle` | `untangle.mjs` — rotate each part to shorten the ratsnest (gate-safe) → `placement/$(VARIANT).json`. | VARIANT |
| `test` | `node --test tests/*.test.mjs` — unit tests for the autoplacer + untangle core. | |
| `sweep` | `place-sweep.mjs` — move one part across candidate spots, report unrouted per spot. | MOD, REF, POS |
| `module` | `module-scaffold.sh` — stamp a new `modules/<NAME>.circuit.tsx` route-in-isolation block. | NAME |
| `pinmap` | `tools/genpinmap.mjs` — regenerate `lib/pinmap.json` from `imports/`. | |
| `render` | Convert every `dist/**/pcb.svg` → `build/<name>_pcb.png` (ImageMagick `convert`). | |
| `place` | Floorplan loop: export throwaway `build/floorplan.kicad_pcb`, snap placement, open in `pcbnew` to drag parts. | VARIANT |
| `sync` | Pull hand-moved positions from `build/floorplan.kicad_pcb` back into `placement/$(VARIANT).json`. | VARIANT |
| `variant` | Fork current placement into a new release: `cp placement/$(VARIANT).json placement/$(V).json`. | VARIANT, V |
| `fit` | **3D fit-check** (pcb-enclosure-fit): import routed + populated board, model OLED, render `cad/build/fit_{iso,top,pop}.png`. | |
| `show` | Open the latest fit PNGs + print the 3D-model paths (GLB/STL). | |
| `export` | `tsci export -f kicad_pcb index.circuit.tsx` — placement + pours + ratsnest → KiCad for hand-routing. | |
| `fab` | Full JLCPCB package: Gerbers + drill (zip) + `gen_bom_cpl.py` (BOM + CPL) → `fab/`. | BOARD |
| `clean` | `rm -rf dist build/routecheck build/*_pcb.png`. | |

> Not a make target but the single most complete PCB command: **`bash scripts/route.sh`** runs the
> whole export → reconcile nets → keepout holes → Freerouting → inject-into-KiCad → DRC pipeline.

---

## 2. Scripts

### `pcb/scripts/` — place / route / measure / fab tooling

| path | lang | purpose | invoked by |
|---|---|---|---|
| `pcb/scripts/route.sh` | bash | The repeatable export→reconcile-nets→keepout-holes→fast-Freerouting→inject-into-KiCad→DRC pipeline. | `bash scripts/route.sh` (`MP=100 OIT=20 …` for final grind); not wired to a make target |
| `pcb/scripts/routecheck.sh` | bash | Build each module standalone under a timeout; report per-block UNROUTED / TIME / PASS (ground truth = the log). | `make routecheck [MODS="mcu audio"]` |
| `pcb/scripts/freeroute.sh` | bash | Route a board (or `.tsx`) with Freerouting v2.1.0 → `.ses`; reads unrouted count from `build/freeroute.log`. | `make freeroute` |
| `pcb/scripts/module-scaffold.sh` | bash | Stamp `modules/<name>.circuit.tsx` with the canonical subcircuit skeleton (sequential-trace, J_ header, GND pour, standalone export). | `make module NAME=<n>` |
| `pcb/scripts/outline-check.mjs` | node | The board-outline rule: flag parts off the outline / inside a cutout; exit 1 if any. | `make outline` |
| `pcb/scripts/autoplace.mjs` | node | Block-level autoplacer: simulated-annealing of subcircuit blocks (min HPWL) under overlap/cutout/outline gates; `--write` applies. | `make autoplace` |
| `pcb/scripts/untangle.mjs` | node | Part-rotation untangle: try each part at 0/90/180/270, keep the orientation that shortens its nets; `--write` → `placement/<variant>.json`. | `make untangle` |
| `pcb/scripts/place-sweep.mjs` | node | Sweep one part `name="<ref>"` across candidate `x,y` positions; rebuild + count unrouted per spot, then restore the file. | `make sweep MOD= REF= POS=` |
| `pcb/scripts/apply_placement.py` | python | Snap a freshly-exported KiCad board to `placement/<variant>.json` (the apply half of the round-trip). | `make place`; `route.sh` |
| `pcb/scripts/sync_positions.py` | python | Read hand-placed positions OUT of a KiCad board back into `placement/<variant>.json` (the sync half). | `make sync` |
| `pcb/scripts/merge_nets.py` | python | Reconcile tscircuit per-subcircuit net fragments to one canonical net by NAME before routing (kills false `shorting_items`); `--write`. | `route.sh` |
| `pcb/scripts/add_plane.py` | python | Add a copper plane/pour zone to the LIVE KiCad board via the IPC API (the way to get GND/PWR planes that `<copperpour>` export drops). | `route.sh` (4-layer step); manual |
| `pcb/scripts/add_cutout_keepouts.py` | python | Auto-keepout every interior closed Edge.Cuts shape (window/reels/screws) into the DSN so Freerouting never crosses a board hole. | `route.sh` |
| `pcb/scripts/patch_dsn_keepout.py` | python | Add one rectangular keepout to a Specctra DSN (a `<cutout>` exports only as Edge.Cuts, not a routing keepout). | `route.sh` / manual |
| `pcb/scripts/apply_ses.py` | python | Write a Freerouting `.ses` into a KiCad board headless via SWIG `pcbnew`; net assignment by union-find over the routing graph. | manual / older path |
| `pcb/scripts/apply_ses_ipc.py` | python | Inject a Freerouting `.ses` into the LIVE KiCad board via the IPC API (authoritative net mapping); `--save` / `--clear`. | `route.sh`; `make freeroute` follow-up |
| `pcb/scripts/apply_fab_rules.py` | python | Set a board's DRC rules in the `.kicad_pro` to a fab's real minimums (default JLCPCB); downgrade cosmetic checks. | `route.sh` / manual |
| `pcb/scripts/drc_check.py` | python | Repeatable DRC triage: run `kicad-cli pcb drc` and sort violations PLACEMENT/ROUTING/FALSE/RULE-FAB; non-zero exit gates a pipeline. | `route.sh` / manual |
| `pcb/scripts/gen_bom_cpl.py` | python | JLCPCB assembly files: BOM (LCSC# from `dist/<base>/circuit.json`) + CPL (`kicad-cli pcb export pos`) → `fab/`. | `make fab` |
| `pcb/tools/genpinmap.mjs` | node | Parse `imports/*.tsx` → emit `lib/pinmap.json` (footprint-relative pin coordinates the `Decap` helper reads). | `make pinmap` |
| `pcb/board_outline.py` | python | Board edge + OLED tape-window cutout from the real cassette profile → `build/board_outline.{dxf,png}`. | `python3 pcb/board_outline.py` |

### `cad/` — parametric build123d parts + the 3D fit-check

| path | lang | purpose | invoked by |
|---|---|---|---|
| `cad/frame.py` | python | Thin perimeter spacer frame (cassette outline projected from the vendor shell) with 4 corner screw holes → `build/frame.{stl,step}`. | `make cad`/`frame`/`verify` |
| `cad/panel.py` | python | Printed face panel (cassette profile + reel holes + tape window + 4 screw holes), thickness `PANEL_T` → `build/panel.{stl,step}`. | `make cad`/`panel`/`verify` |
| `cad/insert.py` | python | Tape-head trapezoidal insert: unions the two vendor color-halves into one watertight body → `build/insert.stl`. | `make cad`/`insert`/`verify` |
| `cad/spacer.py` | python | Spacer frame module — variants `"head"` (head bay + insert slot) and `"dummy"` (closed, beefier). Imported by `machine.py`. | `machine.py` |
| `cad/head_frame.py` | python | Monolithic head-holes spacer frame with head-access window + 4 corner M2 bosses → `build/head_frame.{stl,step}`. | `python3 cad/head_frame.py` |
| `cad/pcb_half.py` | python | A cassette-outline plate used as both top & bottom of the PCB sandwich; defines `MATES`. | `machine.py` |
| `cad/machine.py` | python | Shell assembly PCB(bottom)+spacer+PCB(top): positioned parts + raw spacer + combined STEP. `python3 machine.py [head\|dummy]`. | `python3 cad/machine.py` |
| `cad/machine_params.py` | python | **Single source of truth** for all shell dims (shell W/H, thickness stack, screws, head bay, reels, insert) + `place()` mate helper. Imported everywhere. | imported by CAD scripts |
| `cad/freecad_export.py` | python | Emit editable FreeCAD feature trees (`<part>.FCStd`) from the same extracted geometry via the featuretree skill. | `make freecad` |
| `cad/import_pcb.py` | python | Bring the board into the CAD assembly as STL: `*.kicad_pcb`→bare `build/pcb.stl`; `*.tsx`→populated `build/pcb_pop.stl`. | `make fit` (in pcb/) |
| `cad/oled.py` | python | Model the 0.96″ SSD1306 OLED prop → `build/oled.stl` (blue PCB+header) + `build/oled_screen.stl` (glass). | `make fit` (in pcb/) |
| `cad/render_fit.py` | python | 3D fit-check: stack real board + frame + panel + insert at the param Z datums, render `build/fit_{iso,top,pop}.png` (OpenSCAD). `python3 render_fit.py [N]`. | `make fit` (in pcb/) |
| `cad/merge_oled_glb.py` | python | Drop the modeled OLED into tscircuit's GLB (which omits it) at the window → `pcb/build/3d/flexisette_oled.glb`. | `python3 cad/merge_oled_glb.py` |

### `render/` — headless Blender product renders

| path | lang | purpose | invoked by |
|---|---|---|---|
| `render/blender_render.sh` | bash | Headless Blender wrapper with `LC_ALL=C` + retry guard (works around Blender 5.0's flaky OpenColorIO segfault). `blender_render.sh <script.py> [-- args]`. | top-level `Makefile` (`RUN`) |
| `render/build_render.py` | python | Parametric Blender builder for the A/B/C/D concept hero shots. `blender … -P build_render.py -- <A\|B\|C\|D> <out.png> [samples]`. | `make specs`/`concepts` |
| `render/render_frame.py` | python | Render a single part (auto-centres any STL passed as arg 2) front-3/4 hero. `… -- <out.png> <part.stl>`. | `make frame/panel/insert` + `blend-*` |
| `render/render_assembly.py` | python | Render the exploded panel+frame+PCB+insert 9 mm-stack hero. `… -- <out.png>`. | `make assembly`/`blend-assembly` |
| `render/render_shell.py` | python | Render the shell assembly (PCB+spacer+PCB+insert) exploded hero. (standalone; not wired to a make target.) | `blender … -P render/render_shell.py` |
| `render/render_spacers.py` | python | Render the two spacer variants (dummy vs head-ready) side by side. (standalone.) | `blender … -P render/render_spacers.py` |

### `display/`

| path | lang | purpose | invoked by |
|---|---|---|---|
| `display/tape_anim.py` | python | The 128×64 1-bit two-reel tape-winding animation (look/source-of-truth for the OLED) → `build/tape_winddown.gif` + `tape_still.png`. | `python3 display/tape_anim.py` |

*(Counts: 40 make targets — 18 top-level + 22 in `pcb/`. 41 scripts documented — 21 under `pcb/`
incl. `tools/` and `board_outline.py`, 13 in `cad/`, 6 in `render/`, 1 in `display/`.)*

---

## 3. Generated artifacts

All of these are **gitignored** (`**/build/`, `**/dist/`, `pcb/fab/`, `*.dsn`, `*.ses`, `*.log`) —
they are reproducible from source, never committed.

### PCB (`pcb/`)

| path | what it is | regenerate with | view/use |
|---|---|---|---|
| `pcb/dist/index/circuit.json` | Full built circuit (parts, pads, nets, bboxes, LCSC#) for the composed board. | `make build` | input to `gen_bom_cpl.py`, `autoplace.mjs`, `untangle.mjs`, `outline-check.mjs` |
| `pcb/dist/index/pcb.svg` | Rendered board SVG (composed). | `make build` | `make render` → PNG; or open in a browser |
| `pcb/dist/modules/<name>/{circuit.json,pcb.svg}` | Per-module standalone build. | `make modules` | per-block inspection |
| `pcb/build/<name>_pcb.png` | PNG of each `dist/**/pcb.svg`. | `make render` (ImageMagick `convert`) | image viewer |
| `pcb/build/board_outline.dxf` | Edge.Cuts outline + OLED window + drills for KiCad DXF import. | `python3 pcb/board_outline.py` | KiCad File ▸ Import ▸ DXF |
| `pcb/build/board_outline.png` | Annotated outline preview (board, window, OLED active area, reels, mounts). | `python3 pcb/board_outline.py` | image viewer |
| `pcb/build/floorplan.kicad_pcb` | THROWAWAY board for the drag-in-KiCad floorplan loop (index board never at risk). | `make place` | `pcbnew`; then `make sync` |
| `pcb/index.circuit.dsn` / `pcb/build/*.dsn` | Specctra DSN (board → router) ± injected keepouts. | `tsci export -f specctra` / `route.sh` | input to `freert` |
| `pcb/build/index.ses` (+ `.fixed.ses`) | Freerouting session (routed traces/vias). | `make freeroute` / `route.sh` | inject with `apply_ses_ipc.py` |
| `pcb/build/freeroute.log` | Router log — read the UNROUTED count here (a stuck board never writes a `.ses`). | `make freeroute` | grep `Could not find a route` |
| `pcb/index.circuit.kicad_pcb` | The composed, placed (and routed) KiCad board — the deliverable. | `make export` / `bash scripts/route.sh` | `kicad index.circuit.kicad_pcb` (see `KICAD_FINISH.md`) |
| `pcb/fab/index.circuit-*.{gtl,gbl,gts,…}` + `.drl` | Gerbers + Excellon drill. | `make fab` | upload to JLCPCB |
| `pcb/fab/flexisette_jlcpcb.zip` | Zipped Gerbers + drill for upload. | `make fab` | jlcpcb.com order |
| `pcb/fab/bom.csv` / `bom_unassigned.csv` | Assembly BOM (LCSC#); parts with no LCSC split out for hand-assembly. | `make fab` (`gen_bom_cpl.py`) | JLCPCB BOM upload |
| `pcb/fab/cpl.csv` | Pick-and-place / placement, same origin as the Gerbers. | `make fab` | JLCPCB CPL upload |
| `pcb/build/3d/flexisette.glb` | Populated board in 3D (30 CDN component models; OLED omitted). | `tsci export -f glb index.circuit.tsx -o build/3d/flexisette.glb` | any glTF viewer / Blender |
| `pcb/build/3d/flexisette_oled.glb` | The above GLB with the modeled OLED dropped in at the window. | `python3 cad/merge_oled_glb.py` | gltf-viewer.donmccurdy.com |
| `pcb/build/3d/flexisette.step` | Populated board as STEP. | `tsci export -f step …` | CAD / mechanical fit |
| `pcb/build/drc*.json`, `drc.rpt` | DRC triage output. | `python3 scripts/drc_check.py <board>` | read the sorted summary |

### CAD (`cad/build/`)

| path | what it is | regenerate with | view/use |
|---|---|---|---|
| `cad/build/frame.{stl,step}` | Printed spacer frame. | `make cad` / `cd cad && python3 frame.py` | slicer / `make frame` render |
| `cad/build/panel.{stl,step}` | Printed face panel. | `make cad` / `python3 cad/panel.py` | slicer / `make panel` render |
| `cad/build/insert.stl` | Tape-head insert (unioned halves). | `make cad` / `python3 cad/insert.py` | slicer / `make insert` render |
| `cad/build/head_frame.{stl,step}` | Monolithic head-holes frame variant. | `python3 cad/head_frame.py` | slicer |
| `cad/build/{frame,panel,insert}.FCStd` + `*.ir.json` | Editable FreeCAD feature trees + the IR they came from. | `make freecad` | FreeCAD |
| `cad/build/oled.stl`, `oled_screen.stl` | OLED module render/fit prop (PCB+header, glass). | `python3 cad/oled.py` | fit render / GLB merge |
| `cad/build/pcb.stl` | Bare routed board (from `.kicad_pcb`, Y-mirrored) — for layer registration. | `python3 cad/import_pcb.py …kicad_pcb` (via `make fit`) | fit render |
| `cad/build/pcb_pop.stl` | Populated board (from `.tsx`, real component bodies). | `python3 cad/import_pcb.py …tsx` (via `make fit`) | connector/clearance check |
| `cad/build/fit_iso.png`, `fit_top.png`, `fit_pop.png` | 3D fit-check renders (exploded iso, top-down, populated). | `make fit` (in `pcb/`) / `python3 cad/render_fit.py` | image viewer / `make show` |

### Renders (`render/out/`) and display (`display/build/`)

| path | what it is | regenerate with | view/use |
|---|---|---|---|
| `render/out/flexisette_{frame,panel,insert}.png` | Single-part hero renders. | `make frame`/`panel`/`insert` | image viewer / `make view` |
| `render/out/flexisette_assembly.png` (+ `.blend`/`.blend1`) | Exploded stack hero + saved scene. | `make assembly` | image viewer / `make blend-assembly` |
| `render/out/flexisette_frame.blend` | Saved Blender scene for the frame. | `make frame` | `make blend-frame` |
| `render/out/flexisette_{A,B,C,D}.png` | Concept hero shots. | `make specs` / `make concepts` | image viewer |
| `render/out/flexisette_contact_sheet.png` | 2×2 montage of the concept shots. | `make sheet` / `make concepts` | image viewer |
| `display/build/tape_winddown.gif` | Looping 128×64 tape-winding animation (×4 NEAREST preview). | `python3 display/tape_anim.py` | image viewer / OLED firmware source |
| `display/build/tape_still.png` | Single still frame of the animation. | `python3 display/tape_anim.py` | image viewer |

---

## 4. Data files (committed source data)

### `pcb/placement/<variant>.json` — round-trip floorplan

One object keyed by **reference designator** (e.g. `U1`, `OLED`, `C_BULK`, `J_SPK`). Each value:

| key | meaning |
|---|---|
| `x` | X position, **mm**, in the tscircuit design frame (board centred at origin, Y-up). Maps to KiCad mm via the board-outline bbox centre. |
| `y` | Y position, mm, same frame. |
| `rot` | Rotation in degrees (set by `untangle.mjs` / hand edits). |
| `side` | `"top"` or `"bottom"` — informational; SIDE is owned by the `.tsx` `layer=` (a real flip needs footprint mirroring in code, not here). |

`placement/default.json` is the committed default (35 parts). Written by `make sync` /
`untangle.mjs`, consumed by `apply_placement.py`. Fork a variant with `make variant V=<name>`.

### `pcb/lib/cassette_outline.json` — board edge

A JSON array of `{x, y}` points (mm, board-centred frame) tracing the real cassette face outline
(angled bottom + head-notch). Imported by `index.circuit.tsx` as the `<board outline={…}>` and
reused by `cad/panel.py`/`board_outline.py`. This is the single source for the board edge.

### `pcb/lib/cassette_holes.json` — interior cutouts

`{ "outer": [[x,y],…], "holes": [ [[x,y],…], … ] }` — the outer outline plus every interior
closed loop recovered from the CAD/cassette STL: the **tape window** (OLED glows through it,
~22×13 mm rect), **2 reel/drive holes** (~11 mm circles), and **4 corner screw holes**
(~2.5 mm circles). `index.circuit.tsx` maps each hole to a `<cutout>` (rect if width > 18 mm,
else circle), classifying `WIN*` / `REEL*` / `SCREW*` by size.

### `pcb/lib/pinmap.json` — footprint pin coordinates

`{ "<ComponentFile>": { "<PIN_LABEL>": { "x": …, "y": … }, … }, … }` — footprint-relative pin
positions (mm) for every part in `imports/*.tsx`. Generated by `make pinmap`
(`tools/genpinmap.mjs`), read by the `Decap` placement helper in `lib/place.tsx`.

### `pcb/rules/<fab>.kicad_dru` — KiCad custom DRC rule sets

`jlcpcb.kicad_dru`, `oshpark.kicad_dru`, `pcbway.kicad_dru` — paste-into-KiCad / `kicad-cli pcb drc`
rule files matching each fab's minimums (track/clearance/via/edge). Mirror the numbers in
`apply_fab_rules.py` and `lib/fab.tsx`'s `JLCPCB` preset.

### Other committed source (not generated)

| path | what it is |
|---|---|
| `pcb/index.circuit.tsx` | Composed board: 4 `<subcircuit>` blocks + the inter-block buses + GND copperpour. |
| `pcb/modules/{mcu,power,audio,display}.circuit.tsx` | The four route-in-isolation functional blocks. |
| `pcb/imports/*.tsx` | tscircuit footprints/parts for each component (carry the LCSC `supplierPartNumbers.jlcpcb`). |
| `pcb/lib/{place,fab}.tsx` | `Decap` placement helper; the per-fab routing-prop presets (`JLCPCB`). |
| `pcb/tests/{autoplace,untangle}.test.mjs` | Unit tests for the autoplacer + untangle pure functions (`make test`). |
| `cad/machine_params.py` | The shared dimensional source of truth for every CAD part. |
| `assets/cassette-shell*/` | Vendor cassette STL/STEP the CAD profiles are extracted from (provenance: `assets/DOWNLOADS.md`). |
| `pcb/KICAD_FINISH.md`, `pcb/docs/{roadmap,placement-constraints}.md`, `specs/*.md`, `PARTS.md` | Design/process docs. |

---

## Quick recipes

| I want to… | run |
|---|---|
| See the board live (3D) | `cd pcb && make dev` (https://localhost:3020) |
| Build the board JSON/SVG | `cd pcb && make build` |
| Check placement is legal | `cd pcb && make outline` |
| Measure routing convergence | `cd pcb && make routecheck` |
| Auto-route the whole board | `cd pcb && make freeroute` (or full loop: `bash scripts/route.sh`) |
| Get JLCPCB fab files | `cd pcb && make fab` |
| Floorplan by dragging in KiCad | `cd pcb && make place` → drag → `make sync` |
| 3D-check board vs printed shell | `cd pcb && make fit` then `make show` |
| Build + render the printed parts | `make` (repo root) |
| Preview the OLED animation | `python3 display/tape_anim.py` |
