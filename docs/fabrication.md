# Fabrication — Gerbers, assembly, and DFM

Turning the routed board into something JLCPCB will build. Generation is one command; the rest is
knowing what the fab does and doesn't check.

## One command

```
make fab        # in pcb/
```

Produces, in `pcb/fab/` (gitignored):

| file | what | from |
|---|---|---|
| `flexisette_jlcpcb.zip` | Gerbers (all layers) + Excellon drill | `kicad-cli pcb export gerbers` + `… drill` |
| `bom.csv` | assembly BOM: Comment, Designator, Footprint, LCSC Part # | `scripts/gen_bom_cpl.py` ← `dist/index/circuit.json` |
| `cpl.csv` | placement (pick-and-place): Designator, Mid X/Y, Layer, Rotation | `scripts/gen_bom_cpl.py` ← `kicad-cli pcb export pos` |
| `bom_unassigned.csv` | parts with **no** LCSC number (hand-assemble) | same |

`gen_bom_cpl.py` reads the **LCSC part numbers tscircuit resolved from the imports** (29/30 parts carry
one; it takes the first/preferred of each part's candidate list — the JLC UI flags Basic vs Extended so
you can swap). Parts with no LCSC (the OLED module) go to `bom_unassigned.csv` rather than being dropped
silently. The CPL comes from `kicad-cli pcb export pos`, in the **same coordinate origin as the Gerbers**,
so JLC aligns them automatically.

## Uploading to JLCPCB

1. **jlcpcb.com → Order now** (or **Add Gerber File**; or the standalone **Gerber Viewer** to just look).
2. Upload **`flexisette_jlcpcb.zip`** (the zip itself). It auto-detects 2 layers + the ~102×64 mm size.
3. **Check the preview** — confirm the interior cutouts (OLED window, 2 reels, 4 screw holes) render as
   openings (JLC reads them from `Edge_Cuts.gm1`; internal cutouts sometimes need a confirm/fee/note).
4. For **assembly** (parts soldered): also upload `bom.csv` + `cpl.csv` in the SMT step. Expect to nudge
   a few part rotations (KiCad↔JLC rotation conventions differ); JLC's preview lets you.

## What JLC's DFM does — and doesn't — catch

The DFM check is **manufacturability** (can we build this copper: trace/space mins, hole sizes, annular
rings, board-edge clearance). It is **NOT a netlist/connectivity check** — it will faithfully fabricate
an *unrouted* net as open. So **passing DFM ≠ the board works**.

A subtle, important point: **JLC's DFM reads the raw Gerbers and ignores your `.kicad_pro` rules.**
`apply_fab_rules.py` downgrades cosmetic checks so KiCad's own DRC is readable, but that changes nothing
about what JLC sees. The DFM is the real fab gate; KiCad DRC (`drc_check.py`) is for triage.

## flexisette's DFM status

From an actual JLC PCB-DFM run on the current board:

- **Clean / structural ✓** — *trace-to-board-edge* is Good (the U1 re-floorplan fixed earlier edge
  spills), plus trace width, pad spacing, soldermask bridge, via-in-pad.
- **Real, deferred to a production pass:**
  - **PTH → trace, 0.04 mm (Danger ×3):** `GND`/`VBUS` traces hugging the USB-C mounting holes — reroute.
  - **Pad → board-edge, 0.07 mm (Danger ×2):** two pads tight to an edge/cutout — locate in the GUI + nudge.
  - The **~10 unconnected nets** (the decoupling-cap cluster + DIN) — the genuine routing tail.
- **Loud but auto-handled (accept):** silkscreen-on-pad / -on-hole and 0.1 mm silk line width — JLC
  auto-trims silk off pads and prints thin lines; cosmetic. Annular-ring and trace-spacing warnings are
  within JLC capability.

**Bottom line:** the board is **prototype-ready** (order it for a fit/mechanical check), but a working
production board wants the routing tail finished + the two USB-C-area dangers fixed. Tracked in
[roadmap.md](roadmap.md).

## Fab rules

`scripts/apply_fab_rules.py <board.kicad_pro> [--fab jlcpcb]` sets the project's net-class clearances +
design rules to a fab's real minimums (JLCPCB: 0.127 mm clearance, 0.15 mm track, 0.6/0.3 via, 0.2 mm
copper-edge, 0.25 mm min text) and downgrades non-fab cosmetic checks. The same numbers live in
`lib/fab.tsx` (the `JLCPCB` props spread onto every board/subcircuit). KiCad's default rules are stricter
than any cheap fab, so without this a perfectly fabbable board shows "hundreds of violations."
