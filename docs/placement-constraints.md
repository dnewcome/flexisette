# Placement constraints — design (PLAN ONLY, not built)

> Status: **proposed.** Nothing here is implemented. The goal is a per-part constraint layer that
> the placement tools (`untangle.mjs`, `autoplace.mjs`) and the round-trip loop respect — so the
> designer steers the optimizer instead of fighting it. **Additive and opt-in:** with no constraints
> file, behaviour is exactly today's. We are *not* rewriting the placers or chasing a global optimum —
> this is about **control + incremental refinement** as a layout converges.

## Why

The auto-placers are good at the bulk but wrong on the specifics only the human knows: "this MCU is
where I want it — leave it," "the USB-C must stay on the top edge," "this cap may shift a little but
not flip." Today everything is movable/rotatable within the hard gate (outline + cutouts). We want to
**lock down what's settled and bound what isn't**, both *up front* and *as we go*.

## Data model

Keep **constraints separate from positions**. Positions are per-variant (`placement/<variant>.json`);
constraints are mostly variant-independent (a connector pinned to an edge is pinned in every release).

```
placement/
  default.json            # positions per variant: { ref: {x,y,rot,side} }   (exists)
  glow.json               # another release's positions
  constraints.json        # NEW, shared: { ref: <constraint> }
  constraints.glow.json   # NEW, optional per-variant override
```

Per-ref constraint (all fields optional; omitting a field = the permissive default):

```jsonc
{
  "U1":   { "lock": true },                          // frozen: never moved or rotated
  "USBC": { "anchor": "top", "rotate": [0,180], "move": 2 },  // stay on top edge, ±2mm slide, half-turns only
  "R_EN": { "move": 5 },                             // may drift up to 5mm from its anchor; any rotation
  "C2":   { "rotate": [] }                           // position free, rotation frozen
}
```

| field    | type                         | meaning                                                                 |
|----------|------------------------------|-------------------------------------------------------------------------|
| `lock`   | bool                         | fully frozen — position *and* rotation fixed at its current value.      |
| `move`   | number (mm)                  | max displacement **radius** from the anchor (its `placement` position). `0` = position-locked, rotation still free. |
| `rotate` | array⊆`[0,90,180,270]`       | allowed orientations. `[]` = no rotation; omit = all four.              |
| `anchor` | `top\|bottom\|left\|right`   | keep the part on that board edge (connectors); combine with `move` to slide along it. |
| `side`   | `top\|bottom`                | lock the copper layer.                                                  |
| `group`  | string                       | parts sharing a group move/rotate as one rigid cluster (Phase 3).       |

The **hard gate always wins**: outline + cutout legality (`fitsRot`) is non-negotiable; user
constraints only *further* restrict. If a constraint set is infeasible, warn and relax (never silently
place illegally).

## How each tool reads it

- **`untangle.mjs`** (part rotation): `bestRot` iterates only `rotate[ref] ?? [0,90,180,270]`, skips the
  part entirely if `lock`. `fitsRot` gate still applies on top. (Smallest change — untangle is the
  active tool, so this is the MVP.)
- **`autoplace.mjs`** (block position + rot): already supports `--lock`; generalize to read
  `constraints.json` — `lock`→locked block, `move`→clamp `(cx,cy)` within the radius of the anchor each
  proposal, `rotate`→restrict the `rot` flip.
- **round-trip `sync`/`apply`**: positions only; constraints are an *optimizer* input, not a sync
  concern — **except** the lock-read below.

## Workflow: lock as you go (the nice part)

KiCad footprints already carry a native `(locked yes)` flag (right-click ▸ Locked in pcbnew). So
"lock this part, I'm happy with it" needs **no new UX**: lock it in pcbnew, and `make sync` reads the
flag → writes `{"lock": true}` into `constraints.json`. The next `make untangle` / `autoplace` leaves
it alone. A tiny `scripts/constrain.mjs` CLI covers the rest (`constrain USBC --anchor top --rotate 0,180`,
`constrain R_EN --move 5`) for the constraints KiCad can't express.

Up front: pre-seed `constraints.json` (connectors `anchor`ed to edges, the MCU `lock`ed) before the
first auto-pass, so the optimizer starts inside your intent.

## Phasing (ship value early, don't regress)

1. **MVP** — `lock` + `rotate`, read by `untangle.mjs`; `sync` imports KiCad's native locked flag.
   (One small file + ~20 lines in `bestRot`/`untangle`. Biggest value: freeze what you've hand-placed.)
2. **`move` radius** in `autoplace.mjs` (and untangle if it ever gains a position step).
3. **`anchor`/`side`** — edge pinning (ties into the **pcb-enclosure-fit** skill: a connector's anchor
   edge is its shell-slot edge) + layer lock.
4. **`group`** rigid clusters; a `constrain.mjs` CLI; per-variant constraint overrides.

## Open questions

- Constraints file vs annotating `placement/<variant>.json` — recommend separate (variant-independent).
- `move` as a radius (circle) vs a box — radius is simplest; box if edge-slide needs it.
- `anchor` semantics: distance-from-edge + allowed slide range; reconcile with enclosure slot coords.
- Feasibility handling: detect over-constrained sets, report which constraint to relax.

## Non-goals

- No placer rewrite; constraints are an input layer. No file ⇒ today's behaviour, bit-for-bit.
- Not a global-optimal placer. This is steering + incremental lock-down, deliberately.
- Don't block the current "we're close" state on this — it's additive future work.
