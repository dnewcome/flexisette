# flexisette PCB — roadmap & known gaps (planning)

> Where we are: the board is **prototype-ready** (0 shorts / 0 crossings / 0 copper-over-cut, keepouts
> clean) with a **fast round-trip floorplan loop** (`make place`/`sync`/`variant`), an **auto-untangle**
> (rotation pass, measured 29% fewer ratsnest crossings / 14% shorter signal wirelength), 3D fit-check
> (`make fit`), and JLCPCB fab + assembly output (`make fab`). Guiding rule: **we're close — add value
> without regressing the working board.**

## Known gaps (found, not yet fixed)

1. **Round-trip placement doesn't reach the routing DSN.** `route.sh` applies `placement/<V>.json` to
   the *kicad_pcb*, but the DSN it routes comes from `tsci export -f specctra-dsn` at the **.tsx default
   positions**. When a placement equals the defaults (today) it's fine; once a variant/untangle *changes*
   placement, the SES would be routed for the wrong coordinates → injected tracks miss the moved pads.
   **Fix:** teach `apply_placement` to also patch the DSN `(place …)` section (x/y/side/rot in DSN units),
   or route from the placed board. **This blocks routing any non-default placement** — do it before the
   untangle/variants feed a real route. *(This is also why untangle was validated by crossings, not a route.)*
2. **Route-based validation of untangle.** Once gap #1 is closed: route default vs untangled, confirm
   the **unrouted count** drops (crossings already say it should). Add a `make place-quality` that reports
   crossings + wirelength for a variant (the throwaway `build/validate.mjs` is the prototype).
3. **The routing tail** (~10 unconnected): the LDO-output decoupling cluster + DIN. Best finished with
   the interactive router; tracked in task #6.

## Production-clean pass (deferred from the prototype run; from JLC DFM)

- **USB-C PTH ↔ trace, 0.04 mm (Danger ×3):** reroute `GND`/`VBUS` off the USB-C mounting holes.
- **Pad ↔ board-edge, 0.07 mm (Danger ×2):** locate in the GUI (KiCad's measure differs from JLC's), nudge.
- **Silkscreen** (Danger counts, but JLC auto-trims): optional — thicken silk to ≥0.15 mm + move
  ref-designators off pads for crisp labels.
- **Connector-edge pass:** place every connector at its proper shell-slot edge with outward rotation
  (now easy via the round-trip + the `anchor` constraint once built). Ties into **pcb-enclosure-fit**.

## Placement algorithm directions (state-of-the-art, grounded)

Current: block-level simulated annealing (`autoplace.mjs`, HPWL + hard gates) + part-level rotation
untangle (`untangle.mjs`, crossing/wirelength). Natural next steps, cheapest-first:

- **[planned] Constraint layer** — lock / move-radius / rotate-set / edge-anchor. See
  [placement-constraints.md](placement-constraints.md). The highest-leverage next build: it makes every
  other placer *usable* by letting the human pin what's settled.
- **Crossing-aware objective.** Untangle minimizes wirelength as a proxy; optimize **crossings directly**
  (we already compute them) for orientation *and* position. More faithful to routability.
- **Force-directed / analytical seed.** Replace random-restart annealing's cold start with a
  spring-model seed (attract by net, repel on overlap), then anneal to legalize. Standard in modern
  placers; better minima, fewer restarts.
- **Net-weighting by criticality.** Weight diff-pairs / clocks (USB DM/DP, I2S) heavier so they place
  short + straight; deweight slow/poured nets (already drop power/ground).
- **Channel/escape awareness.** Score not just wirelength but whether each part's pins can *escape*
  toward their nets (the real reason dense QFNs fail). Cheap heuristic: penalize pins pointing into a
  neighbor.
- **Legalize-then-detail.** Keep the two-phase shape: global (annealing/force) → legalization (snap off
  overlaps/cutouts, the gate we have) → detail (rotation untangle, decap snapping). Each phase already
  exists in pieces; formalize the pipeline.

**Explicitly not now:** ML-guided placement, full analytical (quadratic) placers, or a from-scratch
router. They're real SOTA but heavy, and the marginal board here doesn't need them — the constraint
layer + crossing objective + the round-trip will carry the next several boards.

## Suggested order

1. Constraint layer MVP (`lock` + `rotate`, KiCad-locked-flag import) — unblocks human steering.
2. Close gap #1 (placement → DSN) — unblocks routing any variant.
3. Route-validate untangle; add `make place-quality`.
4. Production-clean pass (USB-C PTH, pad-edge) when committing to a real order.
5. Crossing-aware objective + force-directed seed — when a denser board needs it.
