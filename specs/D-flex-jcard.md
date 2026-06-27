# Spec D — "The Flex J-card" (pre-creased flex insert that replaces the paper J-card)

**One-liner:** A plain flex PCB shaped and pre-creased like a J-card — the per-drop swappable art + interface + NFC surface. It replaces the paper insert and folds reliably into a Norelco case. **This is the core parametric mechanism**, and it pairs with any device body (A/B/C).

## Geometry
A J-card unfolds to a strip ~63 mm tall (just under cassette height), folded at two lines into a "J":

```
 ┌───────────────────────────┬──────┬─────────┐
 │  FRONT PANEL ~100 mm wide │SPINE │ TUCK    │   height ≈ 63 mm
 │  (art / display window /  │~12mm │ FLAP    │
 │   touch / LEDs)           │      │ ~15 mm  │
 └───────────────────────────┴──────┴─────────┘
        fold line 1 ↑            fold line 2 ↑
```
*(Verify exact panel dims against a physical Norelco case before fab.)*

## What it carries
- Copper / silkscreen / **ENIG-gold** art — the liner-note aesthetic, *as the board*.
- Capacitive-touch pads (the polyimide coverlay is the touch dielectric — free).
- LEDs back-lighting the art through the coverlay.
- **NFC antenna coil** (single-layer, over a ferrite film, away from the LiPo, with a C0G trim-cap footprint).
- Optional display window / cutout; optional FFC tail to the engine.

## Two roles
- **D1 — Smart liner card (standalone):** NFC-only (NTAG / NTAG I²C plus), no wire to the engine. A gorgeous insert that taps to the drop's web experience. Works as the package for **any** of A/B/C. Cheapest, purest art + NFC.
- **D2 — Interface skin:** plugs into the engine via the 0.5 mm FFC/ZIF and becomes the device's touch/LED/art front. This is the per-drop "Board B."

## Pre-creasing — the manufacturing question
Flex is **elastic** — it won't take a crisp permanent crease like paper. Reliable approaches, cheapest first:
1. **Defined bend areas + case retention (recommended):** at each fold line keep copper out (or run only perpendicular, hatched/curved traces), single-layer in the bend, coverlay bend-relief; inside bend radius ≥ ~6–10× material thickness. The flex *wants* to fold there; the **Norelco case holds it folded**. Cheap on plain JLCPCB/PCBWay flex.
2. **Laser-score / half-etch the polyimide** at the fold so it takes a set — possible, but risks cracking copper; keep copper well clear of the score line.
3. **Rigid-flex panels + flex hinges (premium):** discrete rigid art panels joined by flex hinge strips fold flat *and stay flat* — the most reliable "pre-creased" feel, but priced like rigid-flex.

**Recommendation:** defined bend areas + case retention for normal drops; reserve rigid-flex hinges for a premium edition. Specify the bend regions explicitly in the fab notes, and stiffeners only where the FFC contacts/connector sit.

## Drops / parametric story
**This is the cheapest per-drop artifact of everything** — plain flex ~$1–3/unit at 50–100, fully art-variable, optional NFC per drop, hand-swappable via the ZIF. The whole "limited-run drops" concept rides on this layer.

## Open risks
- Fold reliability vs. cost (bend-area design + case retention is the sweet spot).
- NFC coil keep-out from the LiPo + copper pours (needs ferrite; see PARTS §6).
- Registration of the display window / touch pads to the engine behind it.
