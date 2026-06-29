# speaker_reflex — sealed face-firing micro-speaker sim

Thiele-Small lumped **acoustical equivalent circuit** of the flexisette speaker. The design (decided):
a slim **face-firing micro-driver** in a **sealed** back-volume carved from the cassette interior — the
cassette is only 9mm thick, so a forward-firing driver through the head slot doesn't fit; lying flat and
firing out the face does. (The model still supports a vented port; we A/B'd it and chose sealed.)

The enclosure *is* the model: the box is an acoustic compliance `Cab = Vb/ρc²`. ngspice solves the
circuit; an independent numpy complex-impedance solve verifies the deck.

```
python3 reflex.py        # -> sealed.png (SPL vs Vb, excursion, Fc&Qtc vs Vb, impedance), reflex.cir
```

**Driver: PUI Audio AS01808AO** (18×13mm, 3mm thick, 8Ω, 1W). `Fs=320 Hz` and impedance are PUBLISHED;
`Sd, Vas, Qts, Xmax` are **ESTIMATED from the cone size — measure before finalizing** (a DATS, or a DIY
two-resistor impedance sweep on the board's own amp). The whole "boomy vs flat" question hangs on Qts.

## Verification
- sealed ngspice vs analytic |Ud|: **0.00 %**.
- sealed impedance = single hump (vs the vented twin-hump we confirmed earlier).

## Findings (AS01808, estimated Vas/Qts)
1. **The real driver's low Fs (320 Hz) drops the box knee to ~450–550 Hz** — a genuine low-mid lift,
   far below the 1.1 kHz of the pessimistic placeholder. Sealed in the cassette gives real low-mids.
2. **Qtc is high (~1.3–2.0)** with the estimated `Qts=1.0` → a resonant **peak/boom at Fc**, not a flat
   response. The *real* Qts decides whether that's a pleasant bump or a one-note boom — **measure it.**
   If it's high, a touch of stuffing (raises effective Vb, lowers Qtc) or a lower-Qts driver tames it.
3. **More back-volume always helps** (lower Fc *and* lower Qtc) — `Fc 640→413 Hz` and `Qtc 2.0→1.3` as
   `Vb 4→18 cm³`. **Carve as much interior as possible** (~10–12 cm³ → Fc ~450 Hz); diminishing past that.
4. **Excursion-limited, not power-limited:** ~0.7 mm @1W vs ~0.35 mm Xmax → ~**250 mW clean → ~70 dB@1m**.
   The MAX98357A has headroom the micro driver can't use. (Absolute SPL is uncertain on estimates.)

## Next
- **Measure the AS01808's T-S** (Qts especially) and re-run → lock the response / decide if stuffing is
  needed. The DIY rig: drive the driver through a known series R off the board's amp, log V across each,
  derive Z(f) → Fs, Qts (added-mass trick for Vas).
- **CAD the sealed chamber** (build123d) behind the face-firing driver, sealing as much cassette
  interior as the PCB/battery allow as back-volume; the driver lies flat (3mm) under a grille.
