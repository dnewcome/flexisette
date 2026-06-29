# Placement — the fast early-design loop

The north star of the whole PCB effort: **routing difficulty is decided at placement time, and every
autorouter is immature.** So the time goes into placement, and the tooling here makes placement *fast*
(visual, round-trippable), *reproducible* (positions as data), *variant-able* (a layout per release),
and *cheap to untangle* (an automatic rotation pass). Routing itself is in [pcb-toolchain.md](pcb-toolchain.md).

## Positions are data

A board's floorplan lives in **`pcb/placement/<variant>.json`** — not buried in `.tsx` `pcbX/pcbY`
literals. One object per part:

```json
{ "U1": { "x": -38, "y": 2, "rot": 0, "side": "top" }, ... }
```

- Coordinates are in the **tscircuit-centred design frame** (board centred at origin, Y-up). The
  KiCad↔design transform is derived from the board-outline bbox centre (for this board, (100,100), so
  `tx = kx−100, ty = 100−ky`). `rot` is degrees (0/90/180/270); `side` is `top`/`bottom`.
- `placement/default.json` is the current working floorplan. A **variant** is just another file
  (`placement/glow.json`); same circuit, different layout — the clean way to ship a unique board per drop.
- **SIDE lives in code** (`layer=` on the part); the round-trip only carries x/y/rot. A hand flip needs
  footprint mirroring — keep that in the `.tsx`.

## The round-trip loop

The early loop is **pre-routing** and runs on a **throwaway board** (`build/floorplan.kicad_pcb`) so the
routed board is never at risk:

```
make place   [VARIANT=glow]   # tsci export → apply placement/<V>.json → open pcbnew
   ── drag + rotate parts by eye against the ratsnest / DRC ──
make sync    [VARIANT=glow]   # read the board's footprint (at x y rot) → placement/<V>.json
make variant V=glow           # fork the current placement into a new release
make untangle [VARIANT=glow]  # auto-orient parts to shorten the ratsnest (seed before hand-tuning)
```

Two scripts are the round-trip pair:

| script | direction | what it does |
|---|---|---|
| `scripts/apply_placement.py <variant> [board]` | data → board | patch each footprint's `(at x y rot)` from the JSON |
| `scripts/sync_positions.py <variant> [board]`  | board → data | read footprint positions back into the JSON |

Verified **faithful** (30/30 parts, 0 drift): sync → fresh export → apply → re-sync reproduces the
positions exactly. **Format gotcha:** a *fresh* `tsci export` writes `(layer F.Cu)` (unquoted, name on
the next line); a KiCad-*saved* board writes `(layer "F.Cu")`. The scripts parse the footprint's **first
`(at)`** (it precedes all pad/property `(at)`s) and accept either layer form.

`route.sh` calls `apply_placement` right after the kicad_pcb export, so the saved floorplan feeds the
real route (see the gap note below).

## Auto-untangle (rotation) — `make untangle`

The cheap pre-routing win the autorouter can't give you: hold positions fixed and rotate each part to
the orientation that **stops the ratsnest from crossing**. `scripts/untangle.mjs`:

- For each part, tries **0 / 90 / 180 / 270** and keeps the one that minimises its **signal** nets'
  half-perimeter wirelength; iterates to convergence (greedy sweeps).
- **Power/ground nets are dropped** by fanout (>6 pads) — they're poured, and would otherwise drag
  everything to the board centre.
- **Every rotation is gate-checked** (`fitsRot`): a rotation that pushes the part off the outline or
  onto a cutout is rejected, even if it would shorten wire.
- Writes the chosen rotations straight to `placement/<variant>.json` (positions untouched) → seeds the
  round-trip loop.

**Measured on flexisette:** ratsnest crossings **51 → 36 (29% fewer)**, signal wirelength **943 → 815 mm
(14% shorter)**, 11 parts reoriented. Crossings are the direct cause of routing difficulty, so this
predicts a lower unrouted count. HPWL is a proxy — validate the winner with a fast route.

Pure core (`netHPWL`, `padAt`, `fitsRot`, `bestRot`, `untangle`, `extract`) is unit-tested in
`tests/untangle.test.mjs`.

## Block autoplace — `make autoplace`

`scripts/autoplace.mjs` is the **block-level** placer (the part-level untangle's bigger sibling): it
positions the `<subcircuit>` blocks by **simulated annealing** to minimise inter-block wirelength
(HPWL), under hard penalties for the three placement gates — block-block overlap, block-on-cutout, and
block-outside-outline (point-in-polygon, incl. the head-notch). It reads `circuit.json` (block bboxes,
cutouts, outline, and connectivity via `subcircuit_connectivity_map_key`) and rewrites the block
`pcbX/pcbY/pcbRotation` in the source.

```
node scripts/autoplace.mjs [circuit.tsx] [--scramble] [--lock a,b] [--iters N] [--restarts N]
```

It also rotates blocks (0/90). Pure geometry/cost/anneal functions are tested in
`tests/autoplace.test.mjs`. **Always validate the winner** with `outline-check` + a fast route — HPWL is
only a proxy.

## Placement gates (always enforced)

| gate | tool | rule |
|---|---|---|
| in-outline / off-cutout | `scripts/outline-check.mjs` (`make outline`) | every part inside the board outline, clear of the interior cutouts (tscircuit has **no keep-in**) |
| rotation legality | `fitsRot` in `untangle.mjs` | a rotated part's bbox stays in-outline and off cutouts |
| courtyard | `drc_check.py` | parts don't physically collide |

`ALLOW_IN_CUTOUT` (default `OLED`) exempts a part intentionally placed over a cutout (the display behind
the window).

## Known gap — placement → routing DSN

`route.sh` applies `placement/<variant>.json` to the **`.kicad_pcb`**, but the DSN it routes is exported
fresh from the `.tsx` at the **default** positions. When a placement equals the defaults (today) this is
fine; once a variant/untangle *changes* placement, the SES is routed for the wrong coordinates and the
injected tracks would miss the moved pads. **Closing this** (patch the DSN `(place …)` too, or route
from the placed board) is the prerequisite before any non-default placement can route — see
[roadmap.md](roadmap.md).

## Planned: a constraint layer

A per-part **lock / move-radius / rotate-set / edge-anchor** layer the placers respect — so you can
freeze what you've hand-placed and bound what you haven't, with KiCad's native footprint-locked flag
imported via `sync`. Designed, not built: [placement-constraints.md](placement-constraints.md).
