# PCB toolchain — design, generation, and routing

This document covers how the **flexisette** PCB is described in code, generated, and
routed: the tscircuit (React/TSX) source, the modular-subcircuit architecture, and the
`route.sh` place → route → inject pipeline that lands a fully-routed `*.kicad_pcb`.

It is scoped to *getting a routed board*. It deliberately does **not** cover:

- the round-trip floorplan loop (`make place` / `make sync`) or the auto-orient pass
  (`make untangle`) — see `docs/placement.md`.
- Gerbers / drill / BOM / CPL export — see `docs/fabrication.md` (`make fab`).

Everything lives under `pcb/`. Paths below are relative to that directory unless noted.

---

## 1. Modular-subcircuit architecture

### Why monoliths choke tscircuit

tscircuit's `sequential-trace` autorouter routes the *whole* board as one problem. A
single flat board with the ESP32-S3 (49 pads), USB-C, charger, amp, and OLED all in one
net graph blows up the router's search: it stalls, spins past the per-block timeout, and
leaves nets unrouted. The fix is to **route each functional block in isolation** and only
bridge the handful of buses that cross blocks.

### The four blocks

Each functional block is a `<subcircuit>` with **its own `autorouter="sequential-trace"`**
and its own GND pour. A subcircuit routes as a self-contained board, so the router only
ever sees one block's worth of nets at a time.

| Block | Component / file | Exports |
|---|---|---|
| `McuBlock` | `modules/mcu.circuit.tsx` | `McuBlock`, default `<board>` wrapper |
| `PowerBlock` | `modules/power.circuit.tsx` | `PowerBlock`, default `<board>` wrapper |
| `AudioBlock` | `modules/audio.circuit.tsx` | `AudioBlock`, default `<board>` wrapper |
| `DisplayBlock` | `modules/display.circuit.tsx` | `DisplayBlock`, default `<board>` wrapper |

Each module file exports **two** things: the named block component (composed into the
real board) and a default `() => <board>…</board>` wrapper so the block can be built and
route-checked *standalone* (`make modules`, `make routecheck`). The standalone wrapper
gives each block a small dummy board size (e.g. `40mm × 40mm` for mcu).

Every block takes `name`, `pcbX`, `pcbY` props so the top level can position it, and
spreads `{...JLCPCB}` (see §6) onto its `<subcircuit>` — the board-level fab prop does
**not** reach traces/vias drawn *inside* a subcircuit, because each subcircuit autoroutes
independently.

### Buses cross blocks via *named nets*

Inside a block, signals that leave the block are wired only to a **named net**
(`net.SDA`, `net.BCK`, `net.V3V3`, …) on the chip pin — not to the other block. For
example, in `mcu.circuit.tsx`:

```tsx
<trace from="U1.IO8" to="net.SDA" />  <trace from="U1.IO9" to="net.SCL" />
<trace from="U1.IO5" to="net.BCK" />  <trace from="U1.IO6" to="net.WS" />
```

tscircuit **scopes `net.X` per subcircuit**, so `net.SDA` in the mcu block and `net.SDA`
in the display block are *not* automatically the same node. The top-level board
(`index.circuit.tsx`) makes the cross-block link explicit by bridging each end to the
*board-level* net:

```tsx
<trace from=".mcu .U1 .IO8" to="net.SDA" /><trace from=".display .OLED .SDA" to="net.SDA" />
```

Power and ground are bridged the same way, each via one known cap/connector pin per block:

```tsx
<trace from=".power .C_OUT .pin1" to="net.V3V3" /><trace from=".power .C_OUT .pin2" to="net.GND" />
<trace from=".mcu .C_BULK .pin1" to="net.V3V3" /><trace from=".mcu .C_BULK .pin2" to="net.GND" />
<trace from=".audio .C3 .pin1" to="net.V3V3" /><trace from=".audio .C3 .pin2" to="net.GND" />
<trace from=".display .OLED .VCC" to="net.V3V3" /><trace from=".display .OLED .GND" to="net.GND" />
```

The consequence: after export, each of these shared signals appears under **several net
codes that all reduce to the same name** (one per subcircuit scope plus the bridge). KiCad
treats those as false shorts. `merge_nets.py` (§4, §5) reconciles them back into one flat
netlist *before* routing — recovering the clean netlist you would have had if the board
were a non-modular monolith, without paying the monolith's routing cost.

---

## 2. The board

`index.circuit.tsx` composes the four blocks onto the real cassette face:

```tsx
<board outline={outline} layers={2} autorouter="sequential-trace" {...JLCPCB}>
```

### Floorplan

Blocks are placed by signal flow, keeping the tape window and reels clear:

| Block | `pcbX, pcbY` | Rationale |
|---|---|---|
| `McuBlock` "mcu" | `-38, 2` | left end, pulled in to clear the left reel |
| `PowerBlock` "power" | `2, 20` | top band |
| `AudioBlock` "audio" | `24, -9` | right end, in the narrow column |
| `DisplayBlock` "display" | `-2, -12` | strip just below the tape window |

### Parts table

**MCU — `modules/mcu.circuit.tsx`** (pin map in the file header: I2C `SDA=IO8 SCL=IO9` |
I2S `BCK=IO5 WS=IO6 DIN=IO7` | amp `SD=IO4` | buttons `BTN_A=IO10 BTN_B=IO11` |
`boot=IO0 reset=EN`). Native USB on `IO19=D-`, `IO20=D+` — there is **no** USB-UART
bridge; the ROM enumerates as USB-CDC for flashing and audio upload.

| Ref | Part | JLC | Notes |
|---|---|---|---|
| `U1` | ESP32-S3-WROOM-1-N16R8 | C2913202 | 16 MB flash / 8 MB PSRAM; pins 41–49 are the EPAD, all tied to GND |
| `C1` | 100 nF (0402) | — | bottom-side decap, placed by `Decap` helper on the `3V3` pin |
| `R_EN` / `C_EN` | 10 k / 100 nF | — | EN reset pull-up + cap |
| `R_BOOT` | 10 k | — | IO0 boot pull-up (no boot/reset *buttons* — USB-CDC esptool resets over USB) |
| `C_BULK` | 22 µF (0805) | — | 3V3 bulk; `pin1/pin2` are the V3V3/GND bridge to the board |
| `SW_A` / `SW_B` | TS_1187A_B_A_B tactile | C318884 | user buttons (play/pause, next) |

**Power — `modules/power.circuit.tsx`** (USB-C 5 V → TP4056 LiPo charger → AO3401 load-share
→ ME6211 LDO 3V3; VSYS = USB through Schottky D1 when plugged, else battery through P-FET Q1):

| Ref | Part | JLC | Notes |
|---|---|---|---|
| `USBC` | TYPE-C-31-M-12 receptacle | C165948 | VBUS/GND/shield, CC, D+/D- (both orientations tied) |
| `R_CC1` / `R_CC2` | 5.1 k (0402) | — | CC1/CC2 pulldowns (advertise UFP) |
| `U_CHG` | TP4056 (ESOP8) | C16581 | charger; EPAD + `GV_CHG` via stitch GND to bottom pour |
| `R_PROG` | 2 k | — | charge-current program |
| `C_BAT` | 10 µF (0805) | — | battery cap |
| `J_BAT` | S2B-PH JST 2-pin | C295747 | LiPo connector (VBAT/GND) |
| `D1` | B5819W_SL Schottky | C8598 | USB → VSYS |
| `Q1` | AO3401A P-FET | C347476 | BAT → VSYS when USB off; body diode oriented so it can't back-charge |
| `R_G` | 100 k | — | Q1 gate |
| `U_LDO` | ME6211C33M5G | C82942 | LDO 3V3 out |
| `C_IN` / `C_OUT` / `C5` | 1 µF / 1 µF / 22 µF | — | LDO in/out + bulk |

**Audio — `modules/audio.circuit.tsx`** (MAX98357A I2S class-D amp straight into a speaker,
no DAC; mono via `SD_MODE` biased > 1.4 V = Left; powered from V3V3 ≈ 1 W/4 Ω):

| Ref | Part | JLC | Notes |
|---|---|---|---|
| `U2` | MAX98357AETE_T | C910544 | I2S amp; EPAD to GND; GAIN_SLOT left floating = 9 dB |
| `C3` | 10 µF (0805) | — | VDD bulk; `pin1/pin2` are the V3V3/GND bridge |
| `C2` | 100 nF (0402) | — | VDD bypass |
| `R3` | 100 k | — | SD_MODE pulldown (amp off at boot) |
| `J_SPK` | S2B-PH JST 2-pin | C295747 | speaker out (OUTP/OUTN) |

**Display — `modules/display.circuit.tsx`** (0.96" SSD1306 OLED on I2C, mounted on the
**back** so it glows through the tape-window cutout):

| Ref | Part | Notes |
|---|---|---|
| `OLED` | SSD1306 0.96" module | placed as a 4-pin `<chip>` on `layer="bottom"` with a hand-written footprint: 4 plated holes (`GND/VCC/SCL/SDA`) + a 27×27 mm silkscreen body over the window |
| `R1` / `R2` | 4.7 k (0402) | I2C pull-ups on SDA/SCL |

### Nets

| Net | Role | Crosses blocks? |
|---|---|---|
| `V3V3`, `GND` | power rails | yes — bridged from every block (GND also gets a bottom pour) |
| `USB_DP`, `USB_DM` | native USB D+/D- | power (USB-C) ↔ mcu |
| `SDA`, `SCL` | I2C | mcu ↔ display |
| `BCK`, `WS`, `DIN`, `SD` | I2S + amp shutdown | mcu ↔ audio |
| `VBUS`, `VBAT`, `VSYS` | power-internal | no — single net code, untouched by `merge_nets.py` |

### Outline and interior cutouts

The board outline is the **real cassette face**, a 36-point polygon in
`lib/cassette_outline.json`, spanning x ∈ [-51.125, 51.125] (≈ 102 mm) and
y ∈ [-31.875, 31.875] (≈ 64 mm), including the bottom-centre head-notch. It is passed
straight to `<board outline={outline}>`.

The interior holes come from `lib/cassette_holes.json` (`outer` + 7 `holes`), recovered
from the CAD source (`cad/panel._rings()`, cassette STL). `index.circuit.tsx` maps each
hole to a tscircuit `<cutout>` — which exports as an Edge.Cuts polygon — classifying by
bounding-box width:

| Hole class | Count | `<cutout>` | Width test |
|---|---|---|---|
| Tape window | 1 | `shape="rect"` (`WIN*`) | `w > 18` (≈ 21 × 12 mm; OLED glows through it) |
| Reel / drive holes | 2 | `shape="circle"` (`REEL*`) | `5 ≤ w ≤ 18` (≈ 11 mm, centred ±21, 3) |
| Corner screw holes | 4 | `shape="circle"` (`SCREW*`) | `w < 5` (≈ 2.5 mm) |

Each cutout is centred on its hole's bbox center (`pcbX/pcbY` = center, matching the rect
convention). These cutouts are **routing obstacles** the Freerouting step must avoid — see
`add_cutout_keepouts.py` (§4).

The GND copper pour is declared with `<copperpour connectsTo="net.GND" layer="bottom" />`,
but note this is **dropped by the kicad_pcb exporter** — the real pour is added later by
`add_plane.py` (§3, §4).

---

## 3. The place → route → inject pipeline

`scripts/route.sh` is the repeatable, placement-first pipeline. It exports the board,
reconciles nets, keeps out the holes, routes with Freerouting, then injects the result
into a live KiCad via the IPC API and triages DRC. It is run **directly** (there is no
`make route` target):

```bash
bash scripts/route.sh                  # full run, fast router cap
MP=100 OIT=20 bash scripts/route.sh    # (see caveat below — v2.1.0 ignores MP/OIT)
DISPLAY=:0 bash scripts/route.sh       # X display the relaunched pcbnew runs on
VARIANT=glow bash scripts/route.sh     # apply a non-default saved placement
```

Prerequisites: `tsci` (via bun), `freert` (Freerouting CLI at `~/.local/bin/freert`),
`kipy`, and a KiCad with `api.enable_server=true`.

### Steps, in order

| # | Action | Tool / command |
|---|---|---|
| 1 | Export placement to `index.circuit.kicad_pcb` | `tsci export -f kicad_pcb index.circuit.tsx -o index.circuit.kicad_pcb` |
| 2 | Apply the saved floorplan on top of the `.tsx` defaults | `apply_placement.py <VARIANT> index.circuit.kicad_pcb` (see `docs/placement.md`) |
| 3 | **Placement gate** — fail if any part is off-outline / in a hole | `outline-check.mjs index.circuit.tsx` |
| 4 | Reconcile fragmented cross-subcircuit nets | `merge_nets.py index.circuit.kicad_pcb --write` |
| 5 | Export the Specctra DSN | `tsci export -f specctra-dsn index.circuit.tsx -o build/index.dsn` |
| 6 | Keepout the interior holes in the DSN | `add_cutout_keepouts.py index.circuit.kicad_pcb build/index.dsn` |
| 7 | Route with Freerouting → `build/index.ses` | `freeroute.sh build/index.dsn` |
| 8 | (Re)launch pcbnew on the fresh board | `pkill` old pcbnew, `rm /tmp/kicad/api.sock`, `setsid pcbnew …`, wait for `kipy` |
| 9 | Add the GND pour (`<copperpour>` doesn't export) | `add_plane.py GND B.Cu --replace` |
| 10 | IPC-inject the SES tracks/vias into the live board | `apply_ses_ipc.py build/index.ses --save --clear` |
| 11 | DRC triage | `drc_check.py index.circuit.kicad_pcb` |

The **placement gate** (step 3) is load-bearing: tscircuit has no keep-in, so a part can
sit in the head-notch, off the edge, or on a reel/screw hole. Routing a bad floorplan only
hides the problem, so the gate exits non-zero and aborts (override with `FORCE=1`).

For a **4-layer** board, after step 8 add inner-plane zones and route signals only:

```bash
python3 scripts/add_plane.py GND  In1.Cu --replace
python3 scripts/add_plane.py V3V3 In2.Cu --replace --priority 1
```

> **Note on step numbering.** The `route.sh` echo labels are internally inconsistent
> (steps print `[1/8]`, `[2/8]`, then `[3/8]`, `[3/7]`, `[4/7]` … `[7/7]`, with `[3/…]`
> appearing twice). The *sequence* above is what actually runs; the printed `n/N` labels
> are cosmetic and stale.

### Standalone Freerouting (`make freeroute`)

`make freeroute` is the *measure/route a board on its own* path and is distinct from the
full `route.sh`. It calls `freeroute.sh` on the `.tsx` (which exports its own DSN), not on
the keepout-patched DSN, and stops at the SES:

```bash
make freeroute                  # FILE=index.circuit.tsx by default
make freeroute FILE=modules/mcu.circuit.tsx
```

---

## 4. KiCad-IPC reality

### Why IPC injection (the GUI rejects the SES)

The obvious path — KiCad GUI *File ▸ Import ▸ Specctra Session* — **rejects a SES routed
from tscircuit's DSN**: it chokes on the foreign component/padstack ids tscircuit emits.
`apply_ses_ipc.py` does what that GUI import does, but **headless against a running
pcbnew** through the IPC API, so the foreign ids never matter.

### The kipy API

`apply_ses_ipc.py` and `add_plane.py` both drive KiCad through `kipy`
(`import kipy; b = kipy.KiCad().get_board()`), which talks to pcbnew over a socket at
`/tmp/kicad/api.sock`. KiCad must be launched with `api.enable_server=true`. The board
object exposes `get_nets`, `get_footprints`, `get_pads`, `get_shapes`, `get_zones`,
`create_items`, `remove_items`, `refill_zones`, and `save`.

`apply_ses_ipc.py` is clean where the older SWIG injector (`apply_ses.py`, still in
`scripts/` as the deprecated path) was not, because **net assignment is authoritative,
not geometric** — so there are no V3V3/GND mislabel shorts:

| SES net name | Mapped to |
|---|---|
| `Net-(REF-PadN)` | the kipy net of pad `(REF, N)` (a `_source_component_<n>` infix is stripped) |
| `NAME_source_net_<n>` | the kipy net named `NAME` (GND / V3V3 / SCL / SDA / USB_*) |

The DSN→KiCad coordinate transform is fixed and verified exact on flexisette
(`resolution = (um 10)` ⇒ 10000 units/mm; board placed at +100, +100 mm; Specctra Y is up,
KiCad Y is down):

```
x_nm = u*100 + 100_000_000
y_nm = 100_000_000 - u*100
w_nm = w*100
```

`--save` writes the board (default is a dry-run report); `--clear` rips up existing
tracks/vias first for a clean re-route. After creating items it calls `refill_zones()` and
`save()`. Geometry is injected **verbatim** — an experiment that snapped endpoints to pad
centres added crossings/shorts without reducing unconnected, so the residual unconnected
tail is the genuine route tail, not off-pad slop.

### `add_plane.py` — the GND pour the exporter drops

`tsci export -f kicad_pcb` silently drops `<copperpour>` (the exported board has 0 zones),
so the ground pour is added back via IPC. `add_plane.py GND B.Cu --replace` builds a
rectangular zone from the board bbox; KiCad clips it to the real Edge.Cuts on fill, so the
pour follows the cassette outline and window cutout automatically. It warns if the filled
zone is not a single unbroken island (orphaned regions). Because GND lives on a real pour,
injected GND tracks are redundant copper — a missed GND stub can't orphan a pad.

### Freerouting v2.1.0 — the pin and its quirks

`freeroute.sh` pins **Freerouting v2.1.0** (the version that works for tscircuit DSNs):

- **`-mp` / `-oit` are ignored**, as is `router.max_passes` in `freerouting.json`. v2.1.0
  runs to its built-in default (9999 passes); you cannot cap passes. The only bound is the
  wall timeout `MAXT` (default 120 s). *(Caveat: the `route.sh` header's
  `MP=100 OIT=20 … final grind` example therefore has no effect — those vars are passed
  but ignored.)*
- It writes the `.ses` **only on convergence** (no improvement for a while). A routable
  board converges in seconds; a board it can't fully route (e.g. a keepout that strands a
  net) **oscillates forever and never writes** — so on a timeout you get a log but **no
  SES**. For *measuring* a placement, run a short `MAXT` and read the unrouted count from
  `build/freeroute.log`, not from the SES.
- It emits an empty `(host_version )` that KiCad's parser rejects; `freeroute.sh` patches
  it to `(host_version "freerouting")` with `sed`.
- **Do not upgrade to v2.2.x** for this flow: it needs Java 25 *and* its stricter DSN
  parser rejects the tscircuit DSN (`padstack name expected at 'V3V3'`).

---

## 5. Net reconciliation, DRC triage, and fab rules

### `merge_nets.py` — collapse fragmented nets by name

Because `net.X` is per-subcircuit (§1), a shared signal exports as several net codes that
all reduce to the same base name (SDA appears ~5×, V3V3 as ~9 codes). Routed, KiCad flags
these as false `shorting_items`. `merge_nets.py` collapses every signal to **one canonical
net by name**, *before* routing, giving the modular flow the same flat netlist a monolith
would have. It groups codes by a canonical base:

| Net-table name pattern | Canonical base |
|---|---|
| `<anything> to net.<X>` | `X` (tscircuit's 2-point auto-name) |
| `<X>_source_net_<n>` | `X` (per-scope source net) |
| `<X>` | `X` (already clean; multiple scopes share it) |

Any base with **> 1 code** is merged to one canonical net named `<base>`; single-code nets
(VBUS/VBAT/VSYS) are left untouched. Run it on the freshly-exported board, before opening
in KiCad:

```bash
python3 scripts/merge_nets.py index.circuit.kicad_pcb          # dry run (report only)
python3 scripts/merge_nets.py index.circuit.kicad_pcb --write  # apply
```

### `add_cutout_keepouts.py` — keep the router out of the holes

Freerouting will happily route across the tape window, reels, and screw holes. This script
finds every **closed interior** Edge.Cuts shape in the `.kicad_pcb` (`gr_circle`,
`gr_poly`, or `gr_line` loops joined by union-find), leaves the largest (the outer
outline) alone, and writes a per-copper-layer `(keepout …)` rect for each interior hole
into the DSN. The kicad(mm) → DSN(units) transform is derived by matching the outer
Edge.Cuts bbox to the DSN boundary bbox (handles the +100 mm offset, the scale, and the
Specctra Y-flip). Default margin 0.3 mm (`--margin`).

```bash
python3 scripts/add_cutout_keepouts.py index.circuit.kicad_pcb build/index.dsn
```

### `drc_check.py` — triage buckets

`drc_check.py` runs `kicad-cli pcb drc --format json` and **sorts** the violations so a
clean board is obvious and noise can't hide a real defect. It exits non-zero if any
*blocking* issue remains, so it gates the pipeline.

| Bucket | DRC type | Meaning / fix |
|---|---|---|
| **PLACEMENT** | `courtyards_overlap` | parts physically collide — fix `pcbX/pcbY` |
| **ROUTING (real short)** | `shorting_items`, *distinct* base nets | genuine copper short — reroute / move a part |
| **FALSE short** | `shorting_items`, *same* base net | net fragmentation not reconciled — run `merge_nets.py` |
| **ROUTING (other)** | `tracks_crossing`, `track_dangling`, `unconnected` | crossings block; dangling/unconnected reported |
| **EDGE — over the cut** | `copper_edge_clearance`, actual gap ≤ 0.05 mm | copper at/over the board cut — a **real** defect (milled off / shorted to the routed edge) |
| **RULE / FAB / COSMETIC** | `via_diameter`, `annular_width`, silk/mask/text, `clearance`, edge-*near* | global-fix or ignorable (see `apply_fab_rules.py`) |

The real-vs-false short split reuses the same `base_of()` logic as `merge_nets.py`: two
nets with the same base are an unreconciled fragment (false), different bases are a real
short. **Blocking** = placement + real shorts + false shorts + crossings + edge-over-cut.

```bash
python3 scripts/drc_check.py index.circuit.kicad_pcb
```

### `apply_fab_rules.py` — JLCPCB minimums

KiCad's default DRC rules are stricter than any cheap fab, so a perfectly fabbable board
shows "hundreds of violations" that are pure rule-mismatch. These rules live in the
**`.kicad_pro`** project file (not the `.kicad_pcb`), so this patches them there;
`kicad-cli pcb drc` then reads them (reload the project in the GUI to see it there too).

```bash
python3 scripts/apply_fab_rules.py index.circuit.kicad_pro            # default --fab jlcpcb
python3 scripts/apply_fab_rules.py index.circuit.kicad_pro --fab oshpark
```

JLCPCB minimums applied: clearance 0.127 mm, track 0.15 mm, via 0.6 mm / drill 0.3 mm,
copper-edge 0.2 mm, min text 0.25 mm, hole-to-hole 0.5 mm. Cosmetic checks that don't apply
to a generated board (`lib_footprint_mismatch`, silk overlaps, back-layer text, text
height/thickness, mask bridges) are downgraded to `ignore`/`warning` — the *real* checks
(shorts, unconnected, courtyard) are never touched. These numbers mirror the `JLCPCB`
preset in `lib/fab.tsx` (§6).

---

## 6. Fab presets (`lib/fab.tsx`)

`lib/fab.tsx` exports per-fab routing props that make the **generated** geometry legal for
a fab, so `tsci export -f kicad_pcb` needs no KiCad rule cleanup. Spread the preset into
**every** `<board>` *and* `<subcircuit>` (the board-level prop alone won't reach
within-block traces/vias, because each subcircuit autoroutes independently):

```tsx
<subcircuit {...JLCPCB} name="mcu" pcbX={…} pcbY={…}>
```

| Preset | `minTraceWidth` | `defaultTraceWidth` | `viaHoleDiameter` | `viaPadDiameter` |
|---|---|---|---|---|
| `JLCPCB` (default) | 0.15 mm | 0.2 mm | 0.3 mm | 0.6 mm (→ 0.15 mm annular ring) |
| `PCBWAY` | 0.15 mm | 0.2 mm | 0.3 mm | 0.6 mm |
| `OSHPARK` | 0.1524 mm | 0.2032 mm | 0.33 mm | 0.7 mm |

`JLCPCB` is the preset spread throughout flexisette. It pairs with the KiCad-side
`rules/<fab>.kicad_dru` shipped in the `pcb-layout` skill (same numbers, for checking an
already-routed board) and with `apply_fab_rules.py` (§5).

> Watch the via size: tscircuit's `viaPadDiameter` is the via **pad** (0.6 mm), and
> `viaHoleDiameter` is the **drill** (0.3 mm) — giving a 0.15 mm annular ring, above JLC's
> 0.13 mm min.

---

## 7. Make targets

The Makefile (`pcb/Makefile`) wraps the common steps. `make` with no target prints the
help. The targets relevant to *generating and routing* a board:

| Target | What it does |
|---|---|
| `make build` | build the composed board → `dist/` (`tsci build index.circuit.tsx --pcb-only`) |
| `make modules` | build every block standalone (`tsci build modules/*.circuit.tsx --disable-parts-engine --pcb-only`) |
| `make outline` | the placement gate — flag parts off the outline / in a cutout (`outline-check.mjs`) |
| `make routecheck [MODS="mcu audio"]` | the measured loop: per-block **UNROUTED** count + build **TIME** + PASS (`routecheck.sh`) |
| `make freeroute [FILE=…]` | route a board standalone with Freerouting → `.ses` (`freeroute.sh`) |
| `make export` | hand off to KiCad for hand-routing — placement + pours + ratsnest (`tsci export -f kicad_pcb index.circuit.tsx`) |
| `make dev [FILE=…]` | live tscircuit viewer at https://localhost:3020 |

`make routecheck` is the convergence metric for the modular flow: it builds each module
under a timeout (`TIMEOUT`, default 120 s) and reports, per block, the **UNROUTED** count
(`grep -c 'Could not find a route'` — the log is ground truth, not trace counts), the wall
**TIME**, and PASS (unrouted == 0 *and* clean exit). Drive UNROUTED → 0 and TIME down by
refining placement.

```bash
make modules                       # build every block standalone
make routecheck                    # all modules — unrouted + time per block
make routecheck MODS="mcu audio"   # a subset
make outline                       # placement gate before routing
make freeroute                     # standalone Freerouting on index.circuit.tsx
make export                        # KiCad handoff for hand-routing
```

The full automated route (export → reconcile → keepout → Freerouting → IPC-inject → DRC)
is **`bash scripts/route.sh`**, *not* a make target (see §3).

> **Related, out of scope here:** the round-trip floorplan loop (`make place` / `make sync`
> / `make variant`) and the auto-orient pass (`make untangle`) are documented in
> `docs/placement.md`; Gerbers/drill/BOM/CPL (`make fab`) in `docs/fabrication.md`; and the
> 3D enclosure fit-check (`make fit`) in the `pcb-enclosure-fit` skill.
