# Finishing flexisette in KiCad

Open the board:  `kicad index.circuit.kicad_pcb`  (say "yes" to create a project so settings save).

tscircuit gave you **placement + ground pours + ~80% routing + the ratsnest**. The auto-routed traces
are low quality and several "shorts" are just export net-naming artifacts (a bus net touching the
global net of the same node). So the plan is: **keep placement, rip up routing, re-route clean.**

## How to SEE what's left
- **Ratsnest** — the thin white "airwires" between pads. Every airwire = one unrouted connection.
  Route until there are none.
- **DRC panel** — `Inspect ▸ Design Rules Checker ▸ Run DRC`. Lists *Unconnected items* (route them)
  and *Violations* (fix them). Drive both to 0. Right now: **14 unconnected, 338 violations** (most of
  which collapse once you do steps 1–3).

## 1. Board Setup → fab rules (kills ~216 of the violations)
`File ▸ Board Setup ▸ Design Rules ▸ Constraints` — set to JLCPCB 2-layer:
| min clearance | min track | min annular | min via / hole | min through-hole | hole-to-hole | copper-to-edge |
|---|---|---|---|---|---|---|
| 0.15 mm | 0.15 mm | 0.13 mm | 0.45 / 0.30 mm | 0.30 mm | 0.50 mm | **0.30 mm** |

`Net Classes ▸ Default`: track **0.2 mm**, clearance **0.15 mm**, via **0.6 / 0.3 mm**.
(Optional: `Custom Rules ▸ paste` `rules/jlcpcb.kicad_dru`.)
This clears the 72×3 via_diameter/drill/annular + most clearance + the 5 edge-clearance violations.

## 2. Resize the vias (the source can't — see note)
`Edit ▸ Select All Tracks & Vias` (or Selection Filter → only Vias) → `Properties` → set **0.6 / 0.3 mm**.
tscircuit exports 0.3/0.2 mm vias regardless of props; 0.2 mm drill is below JLC's 0.3 mm min, so this
is a real fix.

## 3. Rip up the auto-routing, keep placement + pours
- Selection Filter (right panel): enable **Tracks** only (disable Footprints/Zones/Pads).
- `Edit ▸ Select All` → `Delete`. (Footprints + the GND zones stay put.)
- This removes every short + crossing + the net-naming tangle at once.

## 4. Re-route from the ratsnest
- Route ▸ **Route Single Track** (hotkey `X`). Click a pad, follow the airwire, double-click to end.
- Order: **power/GND first** (or rely on the pours for GND), then the buses
  (I²C SDA/SCL → OLED, I²S BCK/WS/DIN/SD → audio, USB D±  power→MCU), then the rest.
- Two layers: signals on F.Cu (top), let the **bottom GND pour** carry ground (drop a via to GND near
  each GND pad). `B` refills zones; check the pour is unbroken.
- ~26 signal nets total — with this placement it's ~20 min of routing.

## 5. DRC to zero
`Inspect ▸ DRC ▸ Run`. Triage: *unconnected* → route it; *clearance/track* → already handled by step 1;
*courtyards_overlap* (7) → two parts too close, nudge one. Re-run until 0.

## 6. Fab outputs for JLCPCB
```bash
kicad-cli pcb export gerbers --output fab/  index.circuit.kicad_pcb
kicad-cli pcb export drill   --output fab/  index.circuit.kicad_pcb
kicad-cli pcb export pos     --format csv --units mm --output fab/cpl.csv index.circuit.kicad_pcb
# zip fab/*.gbr + drill → upload to jlcpcb.com; cpl.csv = assembly placement.
```
For the **assembly BOM** (designator → LCSC#), the LCSC numbers live in `imports/*.tsx`
(`supplierPartNumbers.jlcpcb`); tscircuit's `tsci dev index.circuit.tsx` has a one-click
Gerber/BOM/CPL export panel that already carries them.

## Tip: want a cleaner start?
Re-export with the autorouter off → a *placed but unrouted* board (no bad traces to rip up):
route everything fresh in KiCad. Ask and I'll generate it.
