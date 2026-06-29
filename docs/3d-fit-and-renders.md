# 3D fit-check and render pipelines

This subsystem is the mechanical seam between the **routed PCB** (KiCad / tscircuit) and the
**3D-printed cassette parts** (build123d). It does two jobs:

1. **Fit-check** — bring the real board into the printed-part assembly, co-register both on a
   shared datum, and render the stack so that connector / cutout / screw / window alignment can be
   read by eye. Alignment is treated as a *placement gate*: a connector or the OLED window is only
   in the right place on the board if it lines up with the matching opening in the shell.
2. **Beauty renders** — Blender/Cycles hero shots of the full assembly for the README / devlog.

It implements the [`pcb-enclosure-fit`](../../.claude/skills/pcb-enclosure-fit/SKILL.md) skill for
this project. The north star from that skill: *a board and its enclosure are ONE design — connector,
cutout, and screw positions only exist correctly if they line up in 3D. Params lie; the rendered
overlay does not.* This doc covers the flexisette-specific wiring of that idea.

Repo root: `/home/dan/sandbox/dnewcome/flexisette`. All scripts here live under `cad/` and
`render/`; the driving Make targets live in `pcb/Makefile`.

---

## The loop at a glance

```
route board ──▶ kicad-cli export step ──▶ import_pcb.py ──▶ render_fit.py ──▶ eyeball overlay
     ▲              tsci export -f step      (pcb.stl /        (fit_iso/top/pop)      │
     │                                        pcb_pop.stl)                            │
     └──────────── nudge connector/display placement to the shell openings ◀─────────┘
```

Run the whole loop after each place/route pass:

```bash
cd pcb && make fit      # import both board sources + model the OLED + render the 3 fit views
cd pcb && make show     # open fit_top.png + fit_iso.png and print the 3D/GLB/STL paths
```

`make fit` expands to (`pcb/Makefile`):

```make
fit:
	python3 ../cad/import_pcb.py index.circuit.kicad_pcb    # bare routed board (layer registration)
	python3 ../cad/import_pcb.py index.circuit.tsx          # populated board (component bodies)
	python3 ../cad/oled.py                                  # OLED module (no CDN 3D model — modeled here)
	python3 ../cad/render_fit.py 6
```

> The printed parts themselves (`frame.stl`, `panel.stl`, `insert.stl`) are produced by the
> top-level `Makefile` (`make cad`) from build123d; the fit loop consumes them, it does not build
> them. If `cad/build/` is empty, run `make cad` from the repo root first.

---

## Coordinate frames (get this right or nothing aligns)

There are four frames in play. Co-registration is the one thing the whole subsystem hinges on.

| Frame | Up axis | Origin | Notes |
|-------|---------|--------|-------|
| **KiCad** (`*.kicad_pcb` STEP) | Z-up, **Y-down** (screen) | arbitrary; for this board the Edge.Cuts bbox centre is **(100, 100) mm** | needs a Y-mirror to enter the cad frame |
| **tscircuit** (`*.tsx` STEP/GLB) | Z-up, **Y-up**, origin-centred | (0, 0) | already in the cad convention; no mirror |
| **cad / OpenSCAD** (build123d, `render_fit.py`) | **Z-up**, Y-up | cassette centre | the working frame for the fit stack |
| **glTF / GLB** | **Y-up** | scene | tscircuit `(x, y)` → GLB `(x, −z)`; bottom layer at `Y < 0` |

### KiCad → cad transform

`import_pcb.py` co-registers by **bbox-centre**, computed live from the imported solid:

```python
bb = s.bounding_box()
cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
s = Pos(-cx, -cy, -bb.min.Z) * s     # center XY, drop lowest point to z=0
if not populated:
    s = mirror(s, Plane.XZ)          # KiCad Y-down -> cad Y-up
```

For flexisette the Edge.Cuts bbox centre is exactly **(100, 100) mm** in the KiCad frame, so the
net mapping from a KiCad coordinate `(kx, ky)` to the cad frame `(tx, ty)` is:

```
tx =  kx - 100
ty =  100 - ky      # the minus is the Y-mirror; without it the head/front edge and every
                    # asymmetric cutout (the head notch, the off-window OLED) land on the wrong side
```

The centre is *derived from the live bounding box*, not hard-coded — it just happens to be (100, 100)
because that is where tscircuit's KiCad export lands this outline. The mirror is the load-bearing
part: verify it by a known asymmetric feature (the bottom-centre head notch must stay at the front
edge `−Y`).

The tscircuit STEP is already centred and Y-up, so the `mirror` step is **skipped** for `.tsx`
sources.

---

## Two board-into-3D sources — `cad/import_pcb.py`

One script, two paths, dispatched on the source file extension. Both center the result on the
cassette origin and drop the board's lowest point to `z = 0`.

| | `*.kicad_pcb` source | `*.tsx` source |
|---|---|---|
| Exporter | `kicad-cli pcb export step --subst-models --no-dnp` | `tsci export -f step` |
| What you get | **ROUTED but BARE** — outline + every cutout + drill barrels. tscircuit footprints carry no *KiCad* 3D models, so there are no component bodies. | **POPULATED** — ~30 `cad_component` bodies (USB-C, ESP32, amp, generic passives) with real EasyEDA/JLCPCB models pulled from `modelcdn.tscircuit.com`. |
| Frame | KiCad Y-down → **mirror `Plane.XZ`** | already centred + Y-up → **no mirror** |
| Output | `cad/build/pcb.stl` | `cad/build/pcb_pop.stl` |
| Best for | **layer registration** — a clean flat plate to check outline / cutouts / screws against the frame | **connector / display protrusion + clearance** vs the shell openings |
| Caveats | `kicad-cli` returns **nonzero on benign warnings** — the STEP is still written; the code trusts the *file*, not `$?`. | needs **network** (CDN fetch); a `<copperpour>` throws a benign async warning during 3D render; `tsci` **mangles an absolute `-o`**, so the script writes `build/_pop.step` relative to `pcb/` and reads it back. Reflects tscircuit **placement, not KiCad routing** (fine for mechanical fit). |

Invoke directly:

```bash
python3 cad/import_pcb.py ../pcb/index.circuit.kicad_pcb   # bare, for the stack -> pcb.stl
python3 cad/import_pcb.py ../pcb/index.circuit.tsx         # populated, for bodies -> pcb_pop.stl
```

For the bare board the script also prints an **outline-vs-shell delta** so param drift gets caught:

```python
dx = b.size.X - M.SHELL_W
print(f"  outline vs shell {M.SHELL_W}x{M.SHELL_H}: "
      f"{'MATCH' if abs(dx) < 1 else f'dX={dx:+.1f}mm overhang'}")
```

> **Live drift (2026-06-28):** the routed outline is **102.24 mm** wide against `SHELL_W = 100.5`,
> so `import_pcb.py` currently reports **`dX=+1.7mm overhang`**. This is exactly the failure mode the
> skill warns about — a param can't catch a geometry that disagrees with it. Reconcile in
> `machine_params.py` (or the board outline), do not leave the render to keep re-flagging it.

The intermediate STEP for the KiCad path is written to `/tmp/_pcb_fit.step`.

---

## The OLED model — `cad/oled.py`

Neither tscircuit nor KiCad ships a 3D model for the 0.96" SSD1306 module (it has no CDN model), so
the fit/render pipeline models it from scratch as a prop. It mounts on the **back** of the board with
the screen facing out through the tape-window cutout.

Two STLs are emitted so the renderers can colour the dark screen separately from the blue module:

| STL | Contents | Colour role |
|-----|----------|-------------|
| `cad/build/oled.stl` | module PCB + 4-pin header (`module()`) | blue module body |
| `cad/build/oled_screen.stl` | glass + 128×64 active area (`screen()`) | near-black glass |

Key dimensions (`oled.py` constants, mm):

| Const | Value | Meaning |
|-------|-------|---------|
| `MOD_W, MOD_H, MOD_T` | 27.0, 27.0, 1.2 | module PCB (matches the 27×27 silk body) |
| `GLASS_W, GLASS_H, GLASS_T` | 25.5, 16.5, 1.4 | display glass |
| `ACT_W, ACT_H, ACT_T` | 21.7, 10.9, 0.3 | 128×64 lit rectangle |
| `HDR_W, HDR_H, HDR_T` | 10.5, 2.6, 2.6 | 4-pin header at the `−Y` edge, on the back (`−Z`) |

**Origin convention:** the module is centred in XY; the **back of the module is at `z = 0`**; the
**screen is on the `+Z` face**. So it is placed screen-up *behind* the board, and the header sits at
the `−Y` edge where it solders.

```bash
python3 cad/oled.py    # -> cad/build/oled.stl + cad/build/oled_screen.stl (prints bbox + watertight)
```

In the render frame the module is seated at the tape-window centre **`WIN = (0, 3)`** (the board
cutout and the cad assembly share this point).

---

## The OpenSCAD fit-check — `cad/render_fit.py`

This is the always-available previewer (OpenSCAD renders headless anywhere; Blender is the beauty
shot). It stacks the **real** board STLs with the printed parts at the `machine_params` Z datums and
emits three PNGs.

### Z datums (from `machine_params.py`)

```
PCB_T      = 1.57                       # each board / panel half
CASSETTE_T = 9.0                        # nominal shell thickness
SPACER_GAP = CASSETTE_T - 2*PCB_T = 5.86   # frame thickness, derived
TOP_Z      = PCB_T + SPACER_GAP   = 7.43    # top-layer datum
SHELL_W, SHELL_H = 100.5, 64.0
```

### Layer stack (`render_fit.py` `LAYERS`)

| STL | Z (mm) | Colour | Explode factor | Role |
|-----|--------|--------|----------------|------|
| `pcb.stl` | 0.0 | green | **−1.0** | real routed board (bottom) |
| `frame.stl` | `PCB_T` = 1.57 | grey | 0.0 | printed spacer frame |
| `panel.stl` | `TOP_Z` = 7.43 | warm orange | **+1.0** | printed top panel |
| `oled.stl` / `oled_screen.stl` | `0 − 4 − 2·explode` | blue / near-black | (explodes down) | OLED behind the board at `WIN = (0, 3)` |
| `insert.stl` | `z = PCB_T`, `y = −SHELL_H/2` (= −32), `rotate([90,0,0])` | maroon | — | head insert at the front edge |

The explode model is `z + ef*explode`: the board pulls down, the panel pushes up, the frame stays
put, and the OLED drops further below the board (`−4 − 2·explode`) so it reads apart. The `explode`
argument defaults to **6.0 mm** (`render_fit.py 6` in `make fit`); pass `0` for a closed stack.

Insert orientation in this quick stack is **cosmetic** for the alignment check — the load-bearing
read is the board-cutout ↔ shell-opening overlay, not the prettiness of the insert.

### The three views

| Output | Function | Camera (`x,y,z,rotx,roty,rotz,dist`) | Explode | Reads |
|--------|----------|--------------------------------------|---------|-------|
| `cad/build/fit_iso.png` | `render("iso", …)` | `0,0,0,58,0,22,420` | 6.0 | exploded iso — layers apart, board cutouts vs frame |
| `cad/build/fit_top.png` | `render("top", …)` | `0,0,0,0,0,0,420` | 0.0 | straight top-down — window / reels / screw alignment, OLED through the window |
| `cad/build/fit_pop.png` | `render_pop()` | `0,0,0,62,0,25,400` | n/a | **populated** board (`pcb_pop.stl`) with the frame ghosted (`%`) — connector / display protrusion + clearance |

All views render via:

```bash
openscad -o <out.png> --imgsize=1200,800 --colorscheme=Tomorrow \
         --camera=<cam> --autocenter --viewall <scene.scad>     # $fn=48
```

`render_pop()` quietly skips itself if `pcb_pop.stl` is absent, and every layer skips if its STL is
missing — so a partial `cad/build/` still renders what it can.

```bash
python3 cad/render_fit.py            # explode = 6.0 (default)
python3 cad/render_fit.py 0          # closed stack
```

---

## The GLB merge — `cad/merge_oled_glb.py`

`tsci export -f glb` bakes in the 30 CDN component models but **omits the SSD1306** (no model
exists). This script drops the modeled OLED STLs into that GLB at the tape window, behind the board,
and writes a combined GLB you can open in any glTF viewer.

The transform handles the cad-Z-up → glTF-Y-up frame change:

```python
# GLB frame is Y-up: tscircuit (x,y) -> GLB (x,-z); bottom layer is Y<0.
# Our STL is build123d Z-up (screen on +Z) -> rotate -90deg about X (screen -> +Y),
# then seat the screen just under the board (y ~ 0) over the window (z = -3).
M = translation_matrix([0, -2.9, -3]) @ rotation_matrix(-np.pi/2, [1, 0, 0])
```

Both `oled.stl` (blue) and `oled_screen.stl` (near-black) are transformed, colour-tagged, and added
as named nodes.

```bash
python3 cad/merge_oled_glb.py [in.glb=pcb/build/3d/flexisette.glb] \
                              [out=pcb/build/3d/flexisette_oled.glb]
```

| | Path |
|---|---|
| Input GLB (from `tsci export -f glb`) | `pcb/build/3d/flexisette.glb` |
| Output (OLED merged in) | `pcb/build/3d/flexisette_oled.glb` |

> **Not wired into a Make target.** `make fit` does not regenerate the GLB or run this merge, and
> `make show` only *points at* `flexisette_oled.glb`. The GLB path is manual: run
> `cd pcb && tsci export index.circuit.tsx -f glb -o build/3d/flexisette.glb`, then
> `python3 cad/merge_oled_glb.py`. Because nothing in the fit loop rebuilds it, **the GLB can go
> stale relative to the routed board** — regenerate it before sharing.

---

## The Blender beauty render — `render/render_assembly.py`

The Cycles hero shot of the full assembly: the real `pcb.stl` + `frame` + `panel` + `insert` +
OLED, in a studio with soft lights, floor, AgX tone-mapping and depth-of-field.

| Aspect | Setting |
|--------|---------|
| Engine / device | Cycles, **GPU `OPTIX`** (requires a GPU box — **not the dev machine**) |
| Samples / denoise | `samples = 220`, denoising on |
| Resolution | 1792 × 1120 |
| View transform | AgX, "Medium High Contrast", exposure −0.6 |
| Scale | `S = 0.001` (STL mm → Blender m) |
| Stack centring | `ZC = −0.0045` (centres the 9 mm stack about `z = 0`) |
| Explode | `EXPL = 0.0016` m — small, so layers read; **set `EXPL = 0` for a closed view** |
| Outputs | `render/out/flexisette_assembly.png` + a sibling `.blend` |

Z placement mirrors `render_fit.py` (in metres, scaled, offset by `ZC`):

| Part | `place(...)` Z | Explode |
|------|----------------|---------|
| `pcb.stl` (falls back to `panel.stl` as a stand-in if absent) | 0.0 | −EXPL |
| OLED (`oled.stl` + `oled_screen.stl`) | `(0, 3 mm, −4 mm + ZC − EXPL)` — window, behind board, screen up | — |
| `frame.stl` | 1.57 | 0 |
| `panel.stl` | 7.43 | +EXPL |
| `insert.stl` | recentred, `rotate −90° X`, `(0, −0.0245, ZC + 0.0045)` | — |

Run it headless through the retry wrapper (Blender 5.0's bundled OpenColorIO has a ~15% flaky
segfault on this machine — each attempt is a fresh process, `LC_ALL=C` + retries clears it):

```bash
# from the repo root (top-level Makefile):
make assembly                       # render/out/flexisette_assembly.png
make blend-assembly                 # open the scene in the Blender GUI instead

# or directly via the wrapper:
BLENDER=/opt/blender-5.0.1-linux-x64/blender ATTEMPTS=5 \
  render/blender_render.sh render/render_assembly.py render/out/flexisette_assembly.png
```

The script saves the `.blend` first and only renders when `bpy.app.background` is true, so the GUI
path (`make blend-assembly`) builds the scene without auto-rendering — press F12 to render manually.

Sibling render scripts (`render/render_shell.py`, `render/render_frame.py`,
`render/render_spacers.py`) follow the same studio recipe for the printed parts in isolation; the
top-level `make frame|panel|insert|spacers|shell` targets drive them. Those do not consume the PCB —
only `render_assembly.py` and `render_fit.py` pull the routed board in.

---

## How to run and view — quick reference

| Goal | Command | Output |
|------|---------|--------|
| Full fit-check (both boards + OLED + 3 views) | `cd pcb && make fit` | `cad/build/fit_{iso,top,pop}.png` |
| Open the fit renders + print 3D paths | `cd pcb && make show` | opens `fit_top.png`, `fit_iso.png` |
| Just the bare board STL | `python3 cad/import_pcb.py ../pcb/index.circuit.kicad_pcb` | `cad/build/pcb.stl` |
| Just the populated board STL | `python3 cad/import_pcb.py ../pcb/index.circuit.tsx` | `cad/build/pcb_pop.stl` |
| Re-model the OLED | `python3 cad/oled.py` | `cad/build/oled*.stl` |
| Re-render the fit views | `python3 cad/render_fit.py [explode]` | `cad/build/fit_*.png` |
| Merge OLED into the GLB | `python3 cad/merge_oled_glb.py` | `pcb/build/3d/flexisette_oled.glb` |
| Blender beauty render (GPU box) | `make assembly` (repo root) | `render/out/flexisette_assembly.png` |
| Interactive 3D in the browser | `cd pcb && tsci dev` → 3D tab | live, `https://localhost:3020` |
| Open a GLB in a viewer | drag `flexisette_oled.glb` into <https://gltf-viewer.donmccurdy.com> | — |

`make show` prints, verbatim, where everything lives:

```
renders : cad/build/fit_{top,iso,pop}.png   (image viewer)
3D GLB  : pcb/build/3d/flexisette_oled.glb   (drag into https://gltf-viewer.donmccurdy.com, or Blender / OS 3D viewer)
STLs    : cad/build/*.stl    |    live 3D: cd pcb && tsci dev  (localhost:3020, 3D tab)
```

---

## Outputs all live in gitignored `build/` dirs

`.gitignore` excludes `**/build/`, so **none of these artifacts are committed** — they are real
files, regenerated on demand:

- `cad/build/` — `pcb.stl`, `pcb_pop.stl`, `oled.stl`, `oled_screen.stl`, `frame.stl`, `panel.stl`,
  `insert.stl`, the generated `_fit_*.scad`, and the `fit_*.png` renders.
- `pcb/build/3d/` — `flexisette.glb` (tscircuit), `flexisette_oled.glb` (merged), `flexisette.step`.
- `render/out/` — the Blender PNGs + `.blend` files (this dir is **not** under a `build/`, so its
  contents are not gitignored by the `build/` rule — they live under `render/out/`).

Always **re-export the board each pass** — a stale `pcb.stl` silently hides a moved connector. The
fit loop (`make fit`) regenerates the STLs and PNGs together; the GLB does not (see the merge note).

---

## Drift / staleness caveats found while documenting

- **Outline overhang is live, not reconciled.** The routed Edge.Cuts bbox is **102.24 × 63.76 mm**;
  `machine_params.SHELL_W = 100.5`, so the board overhangs the shell by **~1.7 mm in X** and
  `import_pcb.py` prints `dX=+1.7mm overhang` every run. Fix the outline or the param.
- **The GLB pipeline is out of the loop.** `make fit` never rebuilds `flexisette.glb` /
  `flexisette_oled.glb`; `make show` only opens them. Regenerate manually (`tsci export -f glb` +
  `merge_oled_glb.py`) or the shared GLB drifts from the current board.
- **Co-registration is dynamic, not anchored to holes.** `import_pcb.py` centres on the live bbox
  centre + Y-mirror — correct *only while board outline == shell outline*. The skill's preferred
  datum is the 4 corner mounting holes; this project uses the quicker bbox path, which the 1.7 mm
  overhang above will bias by ~0.85 mm until reconciled.
- **`render_assembly.py` needs a GPU box.** It hard-selects `OPTIX`; on a CPU-only dev machine the
  device setup yields no usable device. Use the OpenSCAD fit views for day-to-day work and reserve
  the Blender render for the GPU host. It also renders slightly exploded (`EXPL = 0.0016`) — set
  `EXPL = 0` for a closed product shot.
- **Insert orientation in `render_fit.py` is cosmetic.** A wrong rotate sign there flips the insert
  through the board but does not invalidate the board↔opening alignment read; the Blender assembly is
  where the insert pose is dialed in.
