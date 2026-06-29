# flexisette

A **flex-PCB cassette-tape multimedia object** — a parametric, cassette-shaped board that plays its
own music with a tiny animated display where the tape window would be. Designed as reproducible
"drops": the whole thing regenerates from source (CAD, PCB, renders, firmware).

> Status: work in progress. The mechanical CAD and the PCB design are functional and fabbable; the
> on-device firmware is early.

## The idea

It's the size and shape of a compact cassette. A **0.96″ OLED** sits behind the cassette's central
**tape window** and plays a looping tape-winding animation — the one spot on a cassette where you
expect to see motion. An **ESP32-S3** plays the baked-in audio out a small speaker; it charges over
USB-C and runs off a LiPo.

| Block | Part |
|---|---|
| MCU | ESP32-S3-WROOM-1-N16R8 (native USB) |
| Display | 0.96″ SSD1306 OLED (I²C), in the tape window |
| Audio | MAX98357A I²S class-D amp → speaker |
| Power | USB-C → TP4056 charger → LiPo → ME6211 3V3 |

All parts are JLCPCB/LCSC-stocked for turnkey assembly.

## Repository layout

```
cad/        parametric CAD (build123d) of the physical parts — frame, panel, insert, spacer —
            extracted from real vendor cassette STLs; mate-based assembly + MuJoCo sim
pcb/        the electronics PCB, code-driven with tscircuit (modules/ -> index.circuit.tsx),
            finished in KiCad. Includes the encoded place->route->measure tooling (scripts/)
            and per-fab DRC rule files (rules/)
display/    the 128x64 tape-winding animation for the OLED (display/tape_anim.py)
render/     Blender product renders / .blend files
assets/     vendor cassette shell STLs the CAD is derived from (see assets/DOWNLOADS.md for sources)
specs/      design specs
PARTS.md    component sourcing / BOM notes
```

## Building

- **CAD:** `make` (or run the `cad/*.py` build123d scripts) → STL/STEP/FCStd in `cad/build/`.
- **PCB:** in `pcb/`, `npm install` then `make build` (tscircuit) → `index.circuit.kicad_pcb`; place
  with `make outline` / `make routecheck`, route with Freerouting (`make freeroute`) or in KiCad, and
  apply a fab rule set from `pcb/rules/`. The board outline is the real cassette face (derived from the
  same profile as the CAD).
- **Animation:** `python3 display/tape_anim.py` → a 128×64 GIF preview.

The PCB workflow follows the code-driven, placement-first approach (modular subcircuits, deterministic
placement, ground pours, then route) — see [docs/pcb-toolchain.md](docs/pcb-toolchain.md) and
[docs/workflows.md](docs/workflows.md).

## Documentation

Full documentation lives in **[`docs/`](docs/)** — start with
**[docs/architecture.md](docs/architecture.md)** for the big picture, then:

- [PCB toolchain](docs/pcb-toolchain.md) · [Placement (the fast loop)](docs/placement.md) ·
  [CAD enclosure](docs/cad-enclosure.md)
- [3D fit-check + renders](docs/3d-fit-and-renders.md) · [Fabrication (JLCPCB)](docs/fabrication.md)
- [Workflows — task recipes](docs/workflows.md) · [Reference — every target/script/artifact](docs/reference.md)
- [Roadmap & known issues](docs/roadmap.md) · [Planned placement constraints](docs/placement-constraints.md)

*Project started June 25, 2026.*

## License

TBD. Vendor cassette assets under `assets/` retain their original licenses — see
`assets/DOWNLOADS.md` for attribution.
