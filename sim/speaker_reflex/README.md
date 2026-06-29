# speaker_reflex — bass-reflex micro-speaker sim

Thiele-Small lumped **acoustical equivalent circuit** of the flexisette insert speaker: the slim oval
driver + the ~6 cm³ head-insert box + the folded slot port. The enclosure *is* in the model — the box
is an acoustic compliance (capacitor `Cab`), the folded port an acoustic mass + loss (inductor `Lmap`
+ `Rap`). ngspice solves it; an independent numpy complex-impedance solve verifies the deck.

```
python3 reflex.py          # -> response.png (SPL / excursion / port velocity / impedance), reflex.cir
```

Representative driver T-S (Sd 1.5 cm², Fs 500 Hz, Vas 25 cm³, Qts 0.9, Re 8 Ω); box Vb 6 cm³; folded
slot port 8×1.2 mm. **Refine with the real driver's params** — the conclusions hinge on Vas.

## Verification (the deck is trustworthy)
- ngspice vs analytic |Ud|: **0.00 %** error.
- Sealed resonance **Fc = 1137 Hz** = `Fs·√(1+Vas/Vb)` ✓.
- Vented electrical impedance = **twin humps with a dip at Fb ≈ 412 Hz** (the textbook ported signature) ✓.
- LF physics: front + port cancel below Fb (acoustic short) → steep rolloff (radiated sum is `Ud − Up`, not `Ud + Up`).

## Findings (representative driver — non-obvious, this is why we simulate)
1. **At this extreme miniaturization, ported ≈ sealed.** The 6 cm³ box is ~4× smaller than the driver
   wants (Vas/Vb ≈ 4), so the port gives only a **small bump at ~400 Hz**, paid back by a steeper
   rolloff below it — **net ~0 dB median** vs a sealed box of the same volume. A *sealed* box may be the
   pragmatic call (nearly as good, no folded port to tune/print) **unless the real driver's Vas is low**
   enough to make the port clearly worthwhile. Re-run with real params before committing to the port.
2. **The limit is EXCURSION, not power or the box.** The micro driver hits ~0.3 mm Xmax at only
   **~13 mW**; clean output caps around **~70 dB @1m**. The MAX98357A amp has headroom the driver can't
   use — push it and it distorts/bottoms out, it doesn't get louder cleanly. A bigger driver / more
   volume is the only real lever for more output.
3. **The folded port is realizable and quiet.** ~30 mm of 8×1.2 mm slot tunes 400 Hz; port air velocity
   at clean levels is ~6 m/s, well under the ~17 m/s chuffing threshold (it only chuffs at absurd power).

## Next
- Pick a real oval module, get/measure its T-S, re-run → decide **sealed vs ported** on real numbers.
- If ported survives that, CAD the folded-port enclosure into the insert (build123d), port length as a
  printed-and-tuned variable.
- (TODO) emit a Falstad netlist for interactive intuition — the deck is passive RLC, imports cleanly.
