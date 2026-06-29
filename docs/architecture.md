# flexisette — architecture

How the whole thing fits together. Start here; the subsystem docs go deep.

## What it is

flexisette is a **flex-PCB cassette-tape multimedia object**: a board the size and shape of a compact
cassette that plays its own baked-in music out a small speaker while a 0.96″ OLED animates where the
tape window would be. ESP32-S3 brain, USB-C charging, LiPo power. It lives inside a **3D-printed
cassette shell**, and the OLED glows through the shell's central window.

**North star — reproducible "drops":** the entire object regenerates from source. The circuit, the
board placement, the routing inputs, the enclosure parts, the fab outputs, and the renders are all
produced by code + data in this repo. Shipping a different version is editing data, not redrawing.

## The three subsystems + the seam

```
        ┌──────────────────────────────┐        ┌──────────────────────────────┐
        │  PCB  (electronics)          │        │  CAD  (mechanical)           │
        │  code-driven, pcb/           │        │  parametric, cad/            │
        │                              │        │                              │
        │  tscircuit .tsx  ──► KiCad   │        │  build123d .py  ──► STL/STEP │
        │  generate + place   route    │        │  shell: frame/panel/insert/  │
        │                              │        │         spacer  +  assembly  │
        └───────────────┬──────────────┘        └───────────────┬──────────────┘
                        │                                        │
                        │     shared geometry: cassette outline, │
                        │     tape window, 2 reels, 4 screw holes │
                        ▼                                        ▼
              ┌─────────────────────────────────────────────────────────┐
              │  SEAM: the 3D fit-check  (cad/import_pcb + render_fit)   │
              │  bring the routed board INTO the printed-part assembly,  │
              │  co-register, render, gate placement on alignment       │
              └─────────────────────────────────────────────────────────┘
                        │
                        ▼
        ┌──────────────────────────────┐        ┌──────────────────────────────┐
        │  Firmware (display/, early)  │        │  Outputs                     │
        │  tape-winding animation      │        │  fab (gerbers/BOM/CPL),      │
        │  on the SSD1306              │        │  renders (OpenSCAD + Blender)│
        └──────────────────────────────┘        └──────────────────────────────┘
```

- **PCB** — [pcb-toolchain.md](pcb-toolchain.md): tscircuit (React/TSX) *generates + places* the board
  from code; KiCad *routes* it (the autorouter via Freerouting, injected back over the IPC API). The
  north-star belief is **routing difficulty is set by placement**, so the effort goes into placement.
- **Placement** — [placement.md](placement.md): the fast early-design loop. Positions live as **data**
  (`pcb/placement/<variant>.json`), round-trip between KiCad and the source, get auto-untangled by a
  rotation pass, and drive per-release **variants**.
- **CAD enclosure** — [cad-enclosure.md](cad-enclosure.md): the printed cassette shell as a build123d
  sandwich (PCB-half + spacer + PCB-half ≈ 9 mm), with the head-access insert, screw bosses, and the
  window/reel/screw features that must line up with the board.
- **3D fit + renders** — [3d-fit-and-renders.md](3d-fit-and-renders.md): the seam. Export the board to
  3D (bare KiCad STL or populated tscircuit GLB), seat it in the shell assembly, render the fit-check
  (OpenSCAD) or a beauty shot (Blender). The OLED — which has no CDN 3D model — is modeled here.
- **Fabrication** — [fabrication.md](fabrication.md): Gerbers + drill + assembly BOM/CPL for JLCPCB, and
  what their DFM does and doesn't catch.
- **Reference** — [reference.md](reference.md): every make target, script, artifact, and data file.
- **Workflows** — [workflows.md](workflows.md): task recipes. **Roadmap + known issues** —
  [roadmap.md](roadmap.md). **Planned constraint layer** — [placement-constraints.md](placement-constraints.md).

## Data flow (source → object)

```
SOURCE (committed)                 GENERATED (gitignored build/)        OUTPUT
─────────────────                  ────────────────────────────         ──────
pcb/*.circuit.tsx  ──tsci export──► pcb/index.circuit.kicad_pcb ──route──► fab/  (gerbers, BOM, CPL)
pcb/placement/*.json ──apply──────►  (placement on the board)
                                    pcb/build/3d/*.glb,*.step   ─────────► glTF viewers
cad/*.py           ──build123d────► cad/build/*.stl, *.step    ──render──► cad/build/fit_*.png  (OpenSCAD)
                                                               ──render──► render/out/*.png     (Blender)
```

Everything in `build/`, `dist/`, `fab/` is **regenerated, gitignored, never committed** — real files on
disk you can open, just not in git. The committed source of truth is the `.tsx`, the `.py`, the
`placement/*.json`, and `lib/*.json`. See [reference.md](reference.md) for the full artifact map.

## Coordinate frames (the thing that bites)

Four frames are in play; conversions are the subtle part (full detail in
[3d-fit-and-renders.md](3d-fit-and-renders.md) and [placement.md](placement.md)):

| Frame | Origin / up | Notes |
|---|---|---|
| **tscircuit** (design) | board-centred, **Y-up** | the `.tsx` `pcbX/pcbY`; window at (0, +3) |
| **KiCad** (`.kicad_pcb`) | offset to ≈(100,100), **Y-down** | `tx = kx−100, ty = 100−ky` |
| **cad / OpenSCAD** | board-centred, **Z-up** | build123d parts; fit render frame |
| **glTF (GLB)** | board-centred, **Y-up** (thickness=Y) | tscircuit (x,y) → GLB (x, −z) |

The board-outline bbox centre is what reconciles tscircuit↔KiCad (it's at (100,100) for this board).
KiCad→cad needs a **Y-mirror**; cad→GLB needs a **−90° rotation about X**.

## The repository

```
flexisette/
  README.md, PARTS.md          project overview + bill of materials
  Makefile                     top-level: CAD builds + Blender renders
  cad/                         parametric cassette shell (build123d) + the 3D fit-check + OLED model
  pcb/                         the tscircuit board, its scripts, Makefile, placement data, fab outputs
    modules/                   the functional blocks (mcu/power/audio/display) as <subcircuit>s
    scripts/                   the place→route→fab pipeline (route.sh + the helpers)
    lib/, imports/             fab params, helpers, imported JLC parts, cassette outline/holes JSON
    placement/<variant>.json   positions-as-data (the round-trip floorplan)
    tests/                     unit tests for the placement tooling (autoplace, untangle)
  render/                      Blender beauty-render pipeline (needs a GPU box)
  display/                     firmware-side OLED animation (early)
  docs/                        this documentation set
  assets/                      vendor cassette-shell source files (STL/PDF)
```

## Reproducibility principles

1. **Generate, don't draw.** The board comes from `.tsx`; the shell from `.py`. No hand-placed XML.
2. **Positions are data.** The floorplan lives in `placement/<variant>.json`, round-tripped from KiCad
   — so a layout is reproducible and a *variant is a different data file*, not a forked circuit.
3. **One source of truth per dimension.** `cad/machine_params.py` holds every shared shell dimension;
   parts derive from it. (Caveat: a few values have drifted — see [roadmap.md](roadmap.md).)
4. **The fit-check is a gate, not a picture.** Connector/cutout/screw alignment between board and shell
   is verified in 3D and treated like a DRC rule.
5. **Tools over heroics.** Routing is hard, so design for trivial routing (modular blocks, ground
   pours, deliberate placement, auto-untangle) and hand-finish the tail.
