# Spec C — "The Flex" (flex / rigid-flex construction)

**One-liner:** The device built *on* flex — rigid islands carry the silicon, flex carries the shape, art, antenna, and touch. The most literal realization of the original "a flex PCB that looks like a cassette" vision.

## Construction
**Rigid-flex:** 2–3 rigid islands (an **MCU/audio island**, a **display island**, a **power/battery island**) joined by flex. Two sub-modes:

- **C1 — Folded:** the flex folds the rigid islands on top of each other into the 12 mm cassette envelope (origami-style). Gets a multi-layer stack **with no board-to-board connectors** — the flex *is* the interconnect.
- **C2 — Flat:** a cassette-shaped flexible *sheet* with electronics on islands and the silhouette/art across the flex. The closest thing to "a cassette made of circuit board" — thin, conformable, a flat object (a cassette-shaped card).

The NFC antenna coil, cap-touch electrodes, and LED art integrate natively into the flex regions (free copper).

## Battery
Keep the LiPo on a **rigid island**, never on bare flex (flex + battery = cracked joints). LP503562 in C1-folded; a thinner cell for C2-flat.

## Tape-deck playability
- C1-folded: possible with a printed spacer (like Spec A), but cramped.
- C2-flat: no.

## Drops / parametric story — the catch
Rigid-flex is **expensive at low volume (~5–10× plain flex + connector)**. Respinning it per drop kills the parametric economics. So even here: **freeze the rigid-flex**, and push per-drop art onto a separate cheap **plain-flex J-card (Spec D)**. The rigid-flex is the *body*; D is the *skin*.

## Pros / cons
- ➕ Most distinctive; antenna/touch/art baked into the substrate; can be very thin; no inter-board connectors (C1).
- ➖ Highest fab cost; harder to design + assemble; flex fatigue if any region is repeatedly flexed (design folds as fold-*once*); battery must stay on a rigid island.

## Open risks
- Rigid-flex cost vs. drop quantity — likely only worth it for a flagship/premium edition.
- Stack-up + bend-radius engineering (minimum inside radius, copper-free bend zones).
- This is the highest-complexity build of the four — not the first one to attempt.
