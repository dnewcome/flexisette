# Spec A — "The Deck" (full-size, 2 rigid boards + 3D-printed spacers)

**One-liner:** A full cassette-dimensioned device — two rigid PCBs sandwiched around a 3D-printed internal frame — that is self-contained *and* can be dropped into a real tape deck and played.

This is the maximal version: most capable, biggest battery, and the only build that delivers the **plays-in-a-real-deck** payoff.

## Dimensions / stack-up
Target envelope: **100.5 × 64 × 12 mm** (compact-cassette nominal). The 12 mm Z budget, front to back:

```
 front board (1.0–1.6 mm) + display module (~2–3 mm, recessed behind window)
 ── 3D-printed spacer frame ── (houses LiPo 5 mm + transmit head + auto-stop gear)
 main board (1.6 mm)
                                              ≈ 11–12 mm total
```

## Boards
- **Front board (per-drop candidate):** display window + AMOLED mount, capacitive-touch pads / tactile buttons, status LEDs, top-copper J-card-style art, speaker grille. Can be a cheap cosmetic respin per drop — *or* leave it minimal and push art onto a flex J-card (Spec D).
- **Main board (frozen engine):** ESP32-S3, audio (MAX98357A + PCM5102A), storage, charger + power, USB-C (native), NFC (NTAG I²C plus), the **tape-head driver amp**, and the board-to-board connector.
- **Interconnect:** Hirose DF40 mezzanine (0.4 mm, pick stack height to fit) or a short FFC between the two boards.

## 3D-printed spacer parts (the heart of this spec)
A printed frame does five jobs at once:
1. Holds the two boards at correct spacing and registration (standoffs/snap features).
2. **LiPo pocket** (LP503562, 5 mm) in the central cavity.
3. **Bottom-edge cassette geometry** — head-access window, capstan holes, pinch-roller cutouts, alignment/registration boss, write-protect notches — so it **loads and seats in a real deck** and in the Norelco case.
4. **Transmit-head mount** at the head window (from a harvested adapter head — see PARTS §11), sprung to the right contact height.
5. **Auto-stop defeat** — a capstan-driven dummy-hub gear so the deck doesn't stop on "no tape motion." (Harvest this whole mechanism from the donor adapter.)

## Tape-deck playability — ✅ yes
This is the variant designed for it. The same audio engine has three output destinations: onboard speaker (MAX98357A), 3.5 mm jack (PCM5102A), and the **transmit head** (line-out → small amp → head). Mono, lo-fi, on-brand.

## Drops / parametric story
Frozen main board + frozen engine BOM. Per drop you vary: the **flex J-card / front-board art**, the **content pack** on storage, and optionally reprint the **spacer** for shape tweaks. The expensive board never respins.

## Pros / cons
- ➕ Most capable; ~7–9 h battery; real-deck playback; room for a speaker cavity; robust.
- ➖ Thickest/heaviest; most parts; two-board assembly; 3D-print tolerances on the bottom-edge mechanism are the fiddliest engineering.

## Open risks
- Auto-stop gear + head alignment precision (mitigated by harvesting the donor adapter's mechanism wholesale).
- Z-budget is tight — verify display + LiPo + both boards actually close to ≤12 mm before committing.
- Magnetic neighbors: keep the transmit head and NFC coil away from the LiPo.
