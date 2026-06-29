# CAD: the 3D-printed cassette shell

This document covers the parametric CAD of flexisette's physical enclosure — the 3D-printed
cassette shell that the flex PCB lives inside. Everything here is build123d (Python) plus a couple
of `trimesh` / `shapely` helpers for pulling geometry off the vendor STLs, all under
[`cad/`](../cad/). If you need to change a dimension, change it in **one** file
([`cad/machine_params.py`](../cad/machine_params.py)) and rebuild — that is the whole design
philosophy.

---

## 1. Concept: the cassette is a sandwich

A real Compact Cassette is a flat box about **100.5 × 64 × ~9 mm**. flexisette reproduces that box
as a **three-layer sandwich** stacked along Z (the thin axis):

```
  +Z  ┌──────────────────────────┐  ← top half      (PCB or printed panel)   PCB_T   = 1.57 mm
      │                          │
      │     spacer / frame       │  ← middle         (printed, sets the gap)  SPACER_GAP = 5.86 mm
      │                          │
  0   └──────────────────────────┘  ← bottom half    (the real flex PCB)      PCB_T   = 1.57 mm
                                                                              ─────────────────────
                                                                     CASSETTE_T = 9.00 mm total
```

* The **bottom half is the real PCB** — the cassette-shaped flex board (ESP32-S3 + OLED + audio).
* The **middle is a printed spacer/frame** that sets the inter-board gap and carries the head
  features and the screw bosses.
* The **top half** is either a second PCB or a 3D-printed face **panel** (`panel.py`) that stands in
  for a PCB so the stack still totals a standard cassette thickness.

The board outline, the tape window, the two reel windows, and the four corner screw holes are
**shared geometry**: the same cassette-face silhouette drives both the printed parts (projected off
the vendor shell) and the PCB outline, so the shell's openings land exactly over the board's
cutouts. That alignment is the whole point of the enclosure and is verified by the fit-check
(§9).

### Two part families

There are deliberately **two families** of geometry in `cad/`, and it matters which one you are
touching:

| Family | Files | Outline source | Used by |
|---|---|---|---|
| **Idealized / parametric** | `pcb_half.py`, `spacer.py`, `machine.py` | `RectangleRounded(SHELL_W, SHELL_H, CORNER_R)` — a clean rounded rectangle | the mate-based `machine.py` stack + MuJoCo/quick checks |
| **Vendor-extracted / production** | `frame.py`, `panel.py`, `insert.py`, `head_frame.py` | the **true silhouette** projected from the vendor STL (`side-1-plain.stl` / `side-1-insert.stl`) — angled bottom, real screw bosses, head cutouts | `make`, the Blender renders, `freecad_export.py`, the fit-check |

The parametric family is the simple conceptual stack (great for assembly logic and mates). The
vendor-extracted family is what you actually print, because it inherits the real cassette outline
(the angled "trapezoidal" bottom band, the head-holes region, the molded screw posts) that a deck
expects.

---

## 2. Conventions

These follow the repo's two build123d skills:

* **build123d-part** — each part file exposes a `part()` that returns one **watertight, single-body**
  solid, and a `__main__` block that exports it and prints a self-check
  (`bbox / bodies / watertight`). `pcb_half.py`, `spacer.py`, `frame.py`, `panel.py`,
  `head_frame.py`, `oled.py` all follow this.
* **build123d-machine** — `machine.py` is the **assembly**: it places parts in the stack and prints
  a manifest. Parts expose **named mate points** (`MATES`) rather than magic positions, so the
  assembler snaps `pcb_top` onto the spacer's `pcb_top` mate instead of hard-coding a Z.
* **Stack/Z convention** (from `pcb_half.py`): *+Z points OUT along the joining direction; the part
  origin sits on the contact face.* `MATES["outer"] = Pos(0,0,0)` (cassette exterior),
  `MATES["inner"] = Pos(0,0,T)` (face that touches the spacer).
* **Front edge**: `FRONT_Y = -SHELL_H/2` is the **head-holes edge** (the bottom of the cassette where
  the tape head and capstans poke through). All head/capstan/window features are placed relative to
  `FRONT_Y`.

---

## 3. `machine_params.py` — the single source of truth

Every dimension is a **named constant, derived rather than hand-tuned**. The thickness stack is the
clearest example: you set the target cassette thickness `CASSETTE_T`, and the frame thickness
`SPACER_GAP` *follows* by subtracting the two PCB halves — change `CASSETTE_T` and the spacer, frame,
panel datums, and insert thickness all move together. No part file contains a bare number that
should have been a parameter.

```python
CASSETTE_T = 9.0                     # nominal shell thickness  <-- tune this
PCB_T      = 1.57                    # each PCB half (0.062" board)
SPACER_GAP = CASSETTE_T - 2 * PCB_T  # frame height, DERIVED (= 5.86 mm)
```

### Footprint

| Const | Value | Meaning |
|---|---|---|
| `SHELL_W` | 100.5 mm | cassette width (X) |
| `SHELL_H` | 64.0 mm | cassette height (Y) |
| `CORNER_R` | 4.0 mm | outline corner radius |

### Thickness stack (Z)

| Const | Value | Meaning |
|---|---|---|
| `PCB_T` | 1.57 mm | each PCB half (standard 0.062" board) |
| `PANEL_T` | `= PCB_T` | printed face panel — subs for a PCB on one side |
| `CASSETTE_T` | 9.0 mm | target total shell thickness (**tune this one knob**) |
| `SPACER_GAP` | `CASSETTE_T - 2*PCB_T` = 5.86 mm | frame thickness, derived |

### Spacer walls

| Const | Value | Meaning |
|---|---|---|
| `WALL` | 3.0 mm | head-variant perimeter wall |
| `DUMMY_WALL` | 5.0 mm | dummy-variant wall (beefier, prints mostly solid) |

### Magnetic-head bay (head variant only — placeholder dims, refine against a real head)

| Const | Value | Meaning |
|---|---|---|
| `HEAD_BAY_D` | 9.0 mm | depth of the head shelf behind the front window (+Y) |
| `HEAD_POCKET_W` | 16.0 mm | head pocket width (X) |
| `HEAD_POCKET_H` | 6.0 mm | head pocket height (Z) — *intended* `< SPACER_GAP` (see §10) |

### Head-access window / capstans (used by `head_frame.py`)

| Const | Value | Meaning |
|---|---|---|
| `HEAD_WIN_W` | 24.0 mm | head-access window width in the front wall (matches insert mouth) |
| `HEAD_WIN_H` | 6.0 mm | head-access window height — *intended* `<= SPACER_GAP` (see §10) |
| `CAPSTAN_D` | 2.6 mm | capstan / guide clearance hole diameter |
| `CAPSTAN_DX` | 19.0 mm | capstan holes at ±this X from centre |

### Corner screws & bosses

The corner-screw strategy is **M2 thread-forming, tapped straight into the plastic** — a
non-structural cap, no heat-set, no backing nut, no through hole. The top and bottom PCB each tap a
**blind pilot from their own face**, and the pilots are short enough that they never meet in the
middle. Corners are thickened into **bosses** so the pilot clears the wall.

| Const | Value | Meaning |
|---|---|---|
| `SCREW_CLEAR_D` | 2.4 mm | M2 clearance (drilled in the PCB halves) |
| `SCREW_PILOT_D` | 1.7 mm | M2 thread-forming pilot bore in the plastic |
| `SCREW_PILOT_DEPTH` | 2.5 mm | blind pilot depth per face (`< GAP/2` so the two don't meet) |
| `SCREW_BOSS_D` | 7.0 mm | corner boss diameter |
| `SCREW_HEATSET_D` | 3.2 mm | *legacy* — kept for `head_frame.py` / older spacer variant |
| `SCREW_INSET` | 5.0 mm | *legacy* — boss inset for the parametric `head_frame` variant |

### 2-piece print: thin frame + separate tape-head protrusion

An alternative where the head protrusion prints separately and the PCBs notch to clear it.

| Const | Value | Meaning |
|---|---|---|
| `PROTR_W` | 70.2 mm | tape-head protrusion width (= vendor insert width) |
| `PROTR_CLEAR` | 0.8 mm | clearance around the protrusion (frame slot + PCB notch) |
| `NOTCH_H` | 18.0 mm | PCB bottom-edge notch depth (clears the ~16 mm protrusion) |
| `REEL_D` | 11.0 mm | reel window diameter in the PCB |
| `REEL_DX` | 20.0 mm | reel windows at ±this X from centre |

### Head-holes insert (measured from `side-1-insert.stl`)

| Const | Value | Meaning |
|---|---|---|
| `INSERT_W` | 70.2 mm | width along cassette X |
| `INSERT_H` | 16.0 mm | height along cassette Y (the front band) |
| `INSERT_T` | `= SPACER_GAP` | thickness, meant to equal the inter-PCB gap |
| `FRONT_Y` | `-SHELL_H/2` | the head-holes edge (front of the cassette) |

`machine_params.py` also re-exports `Location, Pos, Rot` from build123d and defines a small
`place(solid, frm, onto)` helper that snaps a part so its local mate `frm` lands on a world target
`onto` (`(onto * frm.inverse()) * solid`).

---

## 4. Part catalog

| Part | File | Family | What it is | Thickness | Outline source |
|---|---|---|---|---|---|
| **PCB half** | `pcb_half.py` | parametric | plain cassette-outline plate, used as top **and** bottom of the sandwich | `PCB_T` | `RectangleRounded` |
| **Spacer (head/dummy)** | `spacer.py` | parametric | the middle frame that sets the gap; `head` adds the head bay + insert slot | `SPACER_GAP` | `RectangleRounded` |
| **Frame** | `frame.py` | vendor-extracted | production spacer frame with the *real* outline + corner bosses + blind screw pilots | `SPACER_GAP` | `side-1-plain.stl` silhouette |
| **Panel** | `panel.py` | vendor-extracted | printed face that subs for the top PCB; carries reel holes + tape window + screw holes | `PANEL_T` | `side-1-plain.stl` silhouette |
| **Insert** | `insert.py` | vendor-extracted | the trapezoidal tape-head bridge at the cassette's front edge | ~8.8 mm (mesh) | fused `side-1/2-insert.stl` |
| **Head frame** | `head_frame.py` | vendor-extracted (legacy) | monolithic head-holes frame with heat-set bosses (older approach) | `SPACER_GAP` | `RectangleRounded` + parametric head |
| **OLED prop** | `oled.py` | render/fit prop | a modeled 0.96" SSD1306 module (no CDN 3D model exists) for the fit-check | — | hand-dimensioned |

### 4.1 `pcb_half.py`

The simplest part: `RectangleRounded(SHELL_W, SHELL_H, CORNER_R)` extruded `PCB_T`. It is the stand-in
for an actual PCB in the parametric stack, used for **both** the top and bottom of the sandwich. It
defines the canonical mate convention (`MATES = {"outer": Pos(0,0,0), "inner": Pos(0,0,T)}`) that the
rest of the assembly snaps against.

### 4.2 `spacer.py` — the parametric middle, two variants

`part(variant)` extrudes a rounded-rectangle perimeter frame of height `SPACER_GAP`, wall thickness
chosen by variant:

* **`variant="dummy"`** — beefier closed frame (`DUMMY_WALL = 5.0`), no openings. The plain
  structural body; prints mostly-solid with slicer infill. Use it when you don't need real deck
  playback.
* **`variant="head"`** (default) — `WALL = 3.0`, plus three head features cut/fused at the front
  (`FRONT_Y`) edge:
  1. a **front slot** (`Box(INSERT_W, WALL*2.5, GAP+0.2)`, subtract) to receive the head-holes
     insert;
  2. a **head-bay shelf**: a cross-bar spanning the inner width that fuses to both side walls, set
     `WALL + HEAD_BAY_D/2` behind the front (the `bay_y` datum);
  3. a **head pocket** cut into that bar (`HEAD_POCKET_W × HEAD_POCKET_H`) so a harvested magnetic
     transmit head can seat behind the window and play in a real deck.

`MATES(variant)` returns `pcb_bottom` (`Pos(0,0,0)`), `pcb_top` (`Pos(0,0,GAP)`), and — for the head
variant — `insert_seat` and `head_seat` mate points at the front edge.

### 4.3 `frame.py` — production spacer (the one you print)

This is the vendor-extracted counterpart of the head spacer. `_extract()` does the geometry lift:

1. `trimesh.load(side-1-plain.stl)` and `.projected(normal=[0,1,0])` to get the **face-on silhouette**
   (the true cassette outline, including the angled bottom and the protrusion cutout).
2. take the largest polygon, recentre it on its bbox centre, and remap projection coords
   `(a0=height, a1=width)` into frame coords `(x=width, y=height)`.
3. find the **four corner screw centroids** from the small interior rings (`area < 15`).
4. build the **cavity** as the outline inset by `WALL` (mitre join), then **subtract a `BOSS_D`-wide
   disc at each screw** so the corners stay solid — those discs become the screw bosses.

`part()` extrudes `outline − cavity` to `SPACER_GAP`, then drills **blind thread-forming pilots from
both faces** (`Cylinder(PILOT_D/2, PILOT_DEPTH*2)` at `z=GAP` and at `z=0`). `SIMP = 0.4 mm` is the
outline simplification tolerance.

### 4.4 `panel.py` — printed face panel

Same `side-1-plain.stl` silhouette as the frame, but it keeps **all** the interior rings as holes:
the two reel windows, the central tape window, and the four corner screw holes (`_rings()` returns
`ext` plus every interior). `part()` subtracts those from the face and extrudes `PANEL_T` (= `PCB_T`,
so panel + frame + PCB still equals 9 mm). It caps the frame on one face while a PCB goes on the
other; the intent is to print the cassette art as a multicolor first layer like the vendor model.

### 4.5 `insert.py` — the tape-head bridge

The vendor split the front trapezoidal head piece into two color-halves for multicolor first-layer
printing (`side-1-insert.stl` + `side-2-insert.stl`). `solid()`:

1. loads both halves, recentres each on its bounding-box centroid;
2. rotates `side-2` **180° about Z** (the vendor halves mate open-face-to-open-face, one flipped);
3. `trimesh.boolean.union(..., engine="manifold")` into one closed trapezoidal shell.

It prints solid (slicer infill). The trapezoidal footprint clears the PCB/frame cutouts and seats
into the frame's trapezoidal bottom section. This is the literal mesh; the **parametric**, editable
version of the same shape is reconstructed in `freecad_export.py` (§7) by projecting the front
silhouette and padding it.

### 4.6 `head_frame.py` — legacy monolithic head frame

An **older, all-parametric** alternative to `frame.py` (note: it does *not* use the vendor outline —
it builds from `RectangleRounded`). One watertight body: a perimeter frame at `SPACER_GAP`, four
corner bosses at `±(W/2 - SCREW_INSET, H/2 - SCREW_INSET)` fused in, a parametric head-access window
in the front wall (`HEAD_WIN_W × HEAD_WIN_H`), two capstan clearance holes (axis along Y), and **M2
heat-set bores** through the bosses (`SCREW_HEATSET_D`). It is kept for reference but superseded by
the `frame.py` blind-pilot approach (no heat-set inserts). If you are choosing one, use `frame.py`.

### 4.7 `oled.py` — display fit prop

Not a printed part — it models the 0.96" SSD1306 module (blue PCB + dark glass + 4-pin header)
because tscircuit has no CDN 3D model for it. It exports `oled.stl` (module, blue) and
`oled_screen.stl` (glass + lit area, near-black) so the fit-check can colour the screen separately.
Origin: module centred in XY, back at `z=0`, **screen on +Z**, so it mounts on the back of the board
with the screen facing out through the tape window. Module body is `27×27×1.2`, glass `25.5×16.5`,
active area `21.7×10.9` (the 128×64 lit rectangle).

---

## 5. Screws, bosses, head bay — strategy notes

* **Why blind thread-forming pilots (current, `frame.py`):** an M2 screw self-taps into a `1.7 mm`
  pilot in PLA. Each PCB half drills an M2 clearance hole (`SCREW_CLEAR_D = 2.4`) and screws into the
  frame from its own side; the two pilots (`SCREW_PILOT_DEPTH = 2.5` each) stay short of meeting in a
  `5.86 mm` gap. No heat-set inserts, no nuts, no through holes. The corner is thickened to
  `SCREW_BOSS_D = 7.0` so the pilot has wall around it — `frame.py` carves the cavity *around* a boss
  disc at each screw so the corners stay solid.
* **Why this matters for the board:** the PCB's four corner clearance holes must sit on the same
  centres `_extract()` pulls from the vendor shell. Those centres are shared geometry; if you move a
  screw on the board, move it in the shell outline too (or vice versa).
* **Head bay (head spacer only):** the cross-bar shelf fuses to both side walls for rigidity and
  gives the magnetic head a pocket to seat in, set just behind the front window so the head face
  lines up with the head-access opening. These dims (`HEAD_BAY_D`, `HEAD_POCKET_*`) are placeholders
  to be refined against a real harvested head.

---

## 6. Assembly: `machine.py`

`machine.py` builds the conceptual sandwich from the **parametric** family (`pcb_half` + `spacer`):

```python
def assembly(spacer_variant="head"):
    return [
        ("pcb_bottom", Pos(0, 0, 0)                    * pcb_half.part()),
        ("spacer",     Pos(0, 0, M.PCB_T)              * spacer.part(spacer_variant)),
        ("pcb_top",    Pos(0, 0, M.PCB_T + M.SPACER_GAP) * pcb_half.part()),
    ]
```

The Z datums are **param-derived** (the layout owns them — bottom at 0, spacer at `PCB_T`, top at
`PCB_T + SPACER_GAP`). Running it:

* exports a **raw spacer at the origin** (`spacer_<variant>.stl`) for clean single-part renders /
  printing;
* exports each **positioned** assembly part (`pcb_bottom.stl`, `spacer.stl`, `pcb_top.stl`; the
  `head` variant keeps the default unsuffixed names so the render scripts find them, `dummy` gets a
  `_dummy` suffix);
* prints a **MANIFEST** of each part's bbox and Z range, plus the `TOTAL`;
* exports a **combined STEP** (`flexisette_shell_<variant>.step`) via a build123d `Compound`.

Example manifest (head variant): `pcb_bottom`, `spacer`, `pcb_top` each `100.5 × 64.0` in XY, total
Z range `[0, 9.0]`.

---

## 7. Building

All build123d scripts are run from inside `cad/` (they `import machine_params` by sibling path and
write to `cad/build/`).

### Per-part

```bash
cd cad
python3 pcb_half.py        # prints a validity / bbox self-check (no file export)
python3 spacer.py          # prints bbox for both dummy + head variants
python3 frame.py           # -> build/frame.stl + build/frame.step
python3 panel.py           # -> build/panel.stl + build/panel.step
python3 insert.py          # -> build/insert.stl
python3 head_frame.py      # -> build/head_frame.stl + build/head_frame.step  (legacy)
python3 oled.py            # -> build/oled.stl + build/oled_screen.stl
```

### Assembly

```bash
cd cad
python3 machine.py          # default = head
python3 machine.py head     # spacer with head bay + insert slot
python3 machine.py dummy    # plain structural spacer
# -> build/{pcb_bottom,spacer,pcb_top}.stl + build/flexisette_shell_head.step (+ spacer_head.stl)
```

### Editable FreeCAD trees

```bash
cd cad && python3 freecad_export.py     # -> build/{frame,panel,insert}.FCStd
```

`freecad_export.py` re-expresses `frame`, `panel`, and `insert` as `featuretree` IR (reusing the
*same* extracted geometry the build123d scripts use) and emits `.FCStd` files that open in FreeCAD
with their operations in the left-panel tree — sketch → pad → pockets, instead of a frozen STEP
lump. Notably it reconstructs the insert **parametrically**: it projects the fused vendor mesh's
front silhouette (trapezoid + head/capstan openings) and pads it, giving an editable solid insert in
one step. Requires the FreeCAD AppImage (see the `featuretree` skill).

### Makefile (parts + Blender renders)

The top-level [`Makefile`](../Makefile) wraps the production family and the renders:

| Target | Does |
|---|---|
| `make` / `make parts` | build + render frame, panel, insert, and the stacked assembly |
| `make cad` | build123d → STL/STEP for frame, panel, insert |
| `make frame` / `panel` / `insert` / `assembly` | one render |
| `make verify` | re-run `frame.py`, `panel.py`, `insert.py` watertight/validity self-checks |
| `make freecad` | the `.FCStd` feature trees |
| `make clean` | remove generated STL/STEP/FCStd/PNG |

Note `make cad` only builds the vendor-extracted parts (`frame`, `panel`, `insert`); the parametric
`spacer`/`pcb_half` stack and the `machine.py` assembly are run directly with `python3`.

### Outputs

Everything lands in **`cad/build/`**: per-part `*.stl` / `*.step`, the combined
`flexisette_shell_<variant>.step`, the `*.FCStd` editable trees, the OLED props, and the fit-check
`fit_*.png` / `_fit_*.scad` (§9). Blender PNGs go to `render/out/`.

---

## 8. Vendor sources

The production parts are derived from two purchased/remixed cassette models (full provenance in
[`assets/DOWNLOADS.md`](../assets/DOWNLOADS.md)):

* **`assets/cassette-shell-minecraft/`** — *Minecraft Soundtrack Cassette Shell remix*
  (Printables #836410). This is the one the CAD reads:
  * `side-1-plain.stl` — plain shell half, the **silhouette source** for `frame.py` and `panel.py`.
  * `side-1-insert.stl` / `side-2-insert.stl` — the front **head-holes bridge** (tape-head window,
    capstan holes, pinch-roller openings, registration tabs), `70.15 × 8.8 × 16.0 mm`. This is the
    "third part" `insert.py` fuses, and the dimensional reference behind `INSERT_W/H/T`.
* **`assets/cassette-shell/`** — *Cassette Shell Sides A+B* (Printables #176745). A reference
  full-shell model (side_a measured `102.25 × 8.8 × 63.75 mm`) with no separate head-holes part —
  kept for comparison, not currently read by the CAD.

> Licenses/authors for both are **TBD** until confirmed on the Printables pages (the assistant can't
> auto-fetch those pages — see the warning in `DOWNLOADS.md`). Verify before any redistribution.

---

## 9. How the shell connects to the PCB

The enclosure only "works" if its openings line up with the board, so the shell and the board are
co-designed against a **shared cassette-face profile** and checked in 3D. Two scripts bridge the
`pcb/` and `cad/` subsystems (this is the `pcb-enclosure-fit` workflow; see also
[`docs/3d-fit-and-renders.md`](./3d-fit-and-renders.md)):

* **`cad/import_pcb.py`** brings the board in as an STL, dispatching on extension:
  * `*.kicad_pcb` → `kicad-cli ... export step` → the **routed but bare** board (tscircuit
    footprints carry no KiCad 3D models). It is **Y-mirrored** (KiCad is Y-down; the CAD is Y-up),
    centred in XY, and lowest point set to `z=0` → `build/pcb.stl`. Best for layer registration. It
    also prints an `outline vs shell` check (`dX` overhang against `SHELL_W × SHELL_H`).
  * `*.tsx` → `tsci export -f step` → the **populated** board (component bodies from EasyEDA CDN
    models) → `build/pcb_pop.stl`. Best for connector / display-protrusion clearance.
* **`cad/render_fit.py`** stacks the real board with the printed parts at the **same
  `machine_params` Z datums** as `machine.py` (`pcb` at 0, `frame` at `PCB_T`, `panel` at
  `PCB_T + SPACER_GAP`), drops the `oled` prop behind the board at the window, and seats the
  `insert` at `FRONT_Y`, then renders three OpenSCAD views:
  * `build/fit_iso.png` — exploded iso (board cutouts vs frame read apart);
  * `build/fit_top.png` — straight top-down **window / reels / screws alignment** check;
  * `build/fit_pop.png` — the populated board ghosted under the frame (connector clearance).

The placement-time loop is:

```bash
py/bin/python cad/import_pcb.py ../pcb/index.circuit.kicad_pcb   # bare, routed -> pcb.stl
py/bin/python cad/render_fit.py                                  # iso + top + pop fit images
```

Treat connector/cutout/screw alignment as a **placement gate**: the shell's window, reels, and screw
bosses are constraints on where parts go on the board. If the top-down image shows the OLED off its
window or a screw off its boss, the fix is to move it on the board (or adjust the shared outline) —
not to nudge the shell independently.

---

## 10. Known discrepancies / gotchas

These are real mismatches found while documenting; flag for whoever next edits the params:

1. **Stale "~12 mm / 8.8 mm" comments vs `CASSETTE_T = 9.0`.** The `machine_params.py` module
   docstring says *"total thickness = a standard cassette (~12 mm)"* and the `INSERT_T = SPACER_GAP`
   comment says *"8.8 mm thickness == the inter-PCB gap"* — both describe an **earlier** target where
   `CASSETTE_T ≈ 12` (→ `SPACER_GAP ≈ 8.86 ≈` the vendor's 8.8 mm insert). With the current
   `CASSETTE_T = 9.0`, **`SPACER_GAP` is actually 5.86 mm**, so `INSERT_T = 5.86 mm`, *not* 8.8 mm.
   The vendor insert mesh is still ~8.8 mm thick, so `insert.py`'s physical part is thicker than the
   gap the frame provides — reconcile `CASSETTE_T`/`INSERT_T` against the real insert before relying
   on it.
2. **Head features exceed the gap.** `HEAD_POCKET_H = 6.0` and `HEAD_WIN_H = 6.0` are both commented
   *"must be `< / <= SPACER_GAP`"*, but `SPACER_GAP = 5.86 mm`, so both are **slightly too tall** for
   the current 9 mm stack. `spacer.py`'s head pocket / `head_frame.py`'s window will punch the full
   height (effectively breaking through). Either trim these to `≤ 5.8` or bump `CASSETTE_T`.
3. **Two outline sources can drift.** The parametric family uses `RectangleRounded(SHELL_W, SHELL_H)`
   while the production family uses the projected vendor silhouette (which measures ~102 mm wide, not
   100.5). `import_pcb.py`'s own check expects the board to match `SHELL_W × SHELL_H = 100.5 × 64`.
   When validating fit, prefer the vendor-extracted parts (`frame`/`panel`) — they carry the real
   outline and screw centres.
4. **`INSERT_W = 70.2` vs measured `70.15`** and **`PROTR_W = 70.2`** — rounded; harmless but note the
   `DOWNLOADS.md` measurement is `70.15`.
5. **`head_frame.py` is legacy** (heat-set bosses, non-vendor outline) and is superseded by
   `frame.py` (blind thread-forming pilots, real outline). `SCREW_HEATSET_D` / `SCREW_INSET` exist
   only for it.
