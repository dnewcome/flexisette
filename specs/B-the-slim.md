# Spec B — "The Slim" (single ultra-thin board, cassette profile)

**One-liner:** One rigid PCB cut to the cassette outline, made as thin as physically possible — "a circuit board that happens to be cassette-shaped." An object you display, not a gadget you operate.

This is the elegant, minimal version. It trades capability and deck-compatibility for thinness and a pure PCB-as-art read.

## Dimensions / stack-up
Outline: cassette silhouette **~100 × 64 mm**; usable copper ~98 × 62 mm. Thin:

```
 display module (~2 mm, front)
 single PCB (1.0–1.6 mm) — all components on the back, low-profile SMD
 thin LiPo (~3–4 mm) in a back pocket / adhered
                                              ≈ 5–7 mm total  (half a cassette)
```

## Board
A single board carries everything: ESP32-S3, AMOLED, audio, NFC coil along an edge, USB-C, storage. **Likely no onboard speaker** (no cavity at this thickness) — favor a 3.5 mm jack and/or the transmit head, or a bone-conduction exciter (#1674) using the case as a diaphragm.

## Battery
Smaller, thinner cell — LP503035 500 mAh (~3 h) or a custom thin pouch. Runtime is the main casualty of thinness.

## Tape-deck playability — ✖ (not natively)
At 5–7 mm it won't seat/load in a deck. If wanted, add an optional **3D-printed cassette-thickness carrier shell** the slim board drops into — but that's bolting on Spec A's idea; not this spec's purpose.

## Drops / parametric story
The catch: it's all *one board*, so a per-drop change = a **full board respin** (more than a cosmetic-only respin). Mitigate by freezing component placement and varying only **soldermask + silkscreen + copper-art layers** + the content pack. Or pair with a flex J-card (Spec D) so the *art* lives on the cheap swappable insert and the slim board stays visually constant.

## Pros / cons
- ➕ Thinnest and most elegant; cheapest assembly (single board, single-sided); strongest PCB-as-art statement; can ship as a bare beautiful object.
- ➖ Small battery; no speaker cavity; doesn't work in a deck without a carrier; per-drop board respin is the priciest parametric path of the four.

## Open risks
- Thin LiPo sourcing + runtime acceptability.
- Single-board respin economics for frequent drops — lean on Spec D to keep drops cheap.
- Component height: everything must stay low-profile to hold the ~5–7 mm target.
