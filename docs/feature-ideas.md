# flexisette — feature ideas (product-level TODO)

Cross-cutting features (mechanical + electrical + firmware), distinct from the PCB
[roadmap.md](roadmap.md) (which is about finishing the *current* board). Each is captured enough to
pick up later; status notes whether it's being designed now or parked.

---

## Tape-deck playback — hub-encoder speed sync + head-emulation coil  *(planned — design later)*

**The vision:** drop the flexisette into a *real* cassette deck and "play" it — the deck spins the
hubs and reads a head, and the cassette behaves like a magnetic tape, **speed-coupled to the deck's
transport.** Play / FF / REW / pause on the deck would control the audio.

Two subsystems make it work:

1. **Head-emulation coil (the cassette-adapter trick, in reverse).** A small coil sits in the insert at
   the exact spot a deck's playback head contacts the tape (the head-gap window). The ESP32 drives the
   coil with the audio signal so it **induces flux into the deck's own playback head** — the deck then
   plays the flexisette's audio through its normal electronics + speakers. (This is how Bluetooth/aux
   "cassette adapters" couple into a deck, run backwards: we emit instead of receive.)

2. **Hub-rotation encoder (the speed-control novelty).** An encoder reads the **reel/hub spin** — the
   deck's reel drive turns the hubs as if it were winding tape. The ESP32 **syncs the playback rate to
   the measured hub speed + direction**, so the deck's transport drives the audio: normal speed on play,
   fast/garbled on FF/REW, stop on pause, even reverse. Effectively the flexisette *is* the tape.

**Why it's worth it:** it turns the object from "a board that plays a clip" into "a cassette that any
deck can play," with authentic transport feel — a strong demo and a real differentiator.

**Open design questions (for the later pass):**
- *Encoder:* reflective-optical on a patterned hub vs. a hall sensor + magnet on the hub vs. a printed
  quadrature pattern. Resolution needed for smooth speed; **direction** sensing (quadrature) is required
  for REW.
- *Head coil:* turns / core / footprint / exact position to couple into a standard head gap; the drive
  path (DAC → coil driver, or a small audio transformer); output level vs. a real tape's flux; whether
  to apply tape **playback EQ** (NAB/IEC) so it sounds right through the deck.
- *Mechanical:* the coil embedded in the **insert** at the head-contact line; the encoder at a **reel
  hub**; the hubs must be **free-spinning** and engage the deck's reel drive (today's reels are cutouts —
  they'd become real rotating hubs).
- *Firmware:* resample stored audio to the hub-derived clock; handle stop / reverse / wow-and-flutter;
  a control loop from hub-tachometer → playback rate.
- *Interplay with the rest:* the reels (currently board cutouts) become moving parts; the insert gains
  the coil; this competes for the same insert volume as the **bass-reflex speaker** below — they may
  need to share or trade the insert space.

---

## Bass-reflex micro-speaker in the head insert  *(in design now)*

A tuned micro-enclosure in the ~6–8 cm³ head-insert region: a **slim oval driver firing through the
24×6 mm head-access slot**, with a **folded/labyrinth port** to extend the low end. At this volume the
tuning lands in the low-mids (~300–500 Hz), not true bass — but far fuller/louder than a bare
micro-speaker. Approach: model the driver + box + folded port as a Thiele-Small equivalent circuit in
ngspice (the **circuit-sim** skill), tune it, then CAD the enclosure into the insert (build123d).
*Note the contention with the head-emulation coil above for the same insert volume.*

---

## Parking lot (one-liners, unplanned)
- Multi-device / sync play across several flexisettes (the original brief mentioned multi-device).
- A simple game / interaction on the OLED + the two tact buttons.
