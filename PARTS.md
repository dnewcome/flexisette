# flexisette — Master Parts List (sourced 2026-06)

Consolidated from the component sourcing pass. Prices are indicative single-unit unless noted; pull live break pricing at order time. **Bold** = recommended pick for the frozen engine. Distributor stock moves fast — re-verify before a BOM lock.

Envelope reference: compact-cassette **~100.5 × 64 × 12 mm**; visible front face ~64 × 100 mm; usable PCB outline inside the shell ~98 × 62 mm.

---

## 1. MCU / SoC

| Part | Key spec | Source | ~Price (1 / vol) |
|---|---|---|---|
| **ESP32-S3-WROOM-1-N16R8** | 2×LX7 @240MHz, 16MB flash, **8MB Octal PSRAM**, BLE5, 2×I²S, QSPI LCD, 14× cap-touch, native USB | LCSC C2913202 / DigiKey | **$5.41 / $3.66** |
| ESP32-S3-WROOM-1-N8R8 | 8MB flash / 8MB Octal PSRAM | LCSC | ~$4.70 / $3.37 |
| ESP32-S3-WROOM-1U-N16R8 | external-antenna variant (for metal/shielded shell) | DigiKey | — |
| ESP32-S3R8 (bare) | 8MB Octal PSRAM in-package, no flash | LCSC C2913194 | $2.23 |
| ESP32-P4NRW32 + ESP32-C6-MINI-1-N4 | RISC-V @400MHz, 2D/JPEG accel, MIPI-DSI, 32MB PSRAM — **NO radio**, add C6 for BLE | LCSC C22387510 / C5736265 | $5.87 + $2.51 |
| RP2350A (+ Pico 2 W) | 2×M33 @150 + FPU/DSP, QSPI PSRAM; radio via CYW43439 (immature BLE) | LCSC C42411118 | $1.10 / $0.80 |
| nRF52840 / nRF5340 | best low-power BLE, weak for media (no PSRAM) — **BLE co-processor only** | DigiKey | $6.78 / $9.74 |

**Pick:** ESP32-S3-WROOM-1-N16R8 — the only single chip that does software audio decode + live visuals + game + BLE. Octal PSRAM is the enabler. Pin decode → core 0, visuals → core 1.

## 2. Display — MOTION path (rigid color)

| Part | Size / res | Controller / IF | Source | ~Price |
|---|---|---|---|---|
| **1.91" QSPI AMOLED** | 240×536 letterbox (tape-window) | RM67162 / QSPI | LILYGO T-Display-S3 AMOLED / Waveshare ESP32-S3-AMOLED-1.91 | **~$30** (dev board); bare FPC panel sourceable |
| 2.0" SPI IPS (budget fallback) | 240×320 | ST7789 / SPI | Adafruit #4311 / Waveshare | $14–20 |
| 1.9" SPI IPS | 170×320 letterbox | ST7789V2 / SPI | Waveshare | $12–13 |
| 2.41" QSPI AMOLED | 450×600 full-face | RM690B0 / QSPI | Waveshare ESP32-S3-Touch-AMOLED-2.41 | ~$45–50 |
| 1.8" QSPI AMOLED | 368×448 | SH8601 / QSPI | Waveshare / Makerfabs | $36–43 |
| 1.28" round LCD ("reel") | 240×240 | GC9A01 / SPI | Waveshare / Adafruit #6178 | $5–15 |
| 1.43" round AMOLED ("reel") | 466×466 | CO5300 / QSPI | Waveshare | $39–43 |
| 2.4" SPI IPS | 240×320 biggest cheap face | ILI9341/ST7789 / SPI | Waveshare | $14–15 |

**Avoid:** bare MIPI-DSI AMOLED panels — not drivable from ESP32-S3 (would require ESP32-P4).
**Pick:** 1.91" RM67162 QSPI AMOLED — tape-window shape, emissive, ~1mm thin, 60Hz tear-free w/ TE line.

## 3. Display — STATIC / FLEXIBLE path (e-paper)

| Part | Size / res | Notes | Source | ~Price |
|---|---|---|---|---|
| **2.9" flexible e-paper** | 296×128 **mono**, flexible (~10mm bend R) | full ~3s / partial ~0.3s; holds image at 0W; FPC tail must stay flat | Adafruit #4262 / Waveshare 2.9 e-Paper D / Pimoroni | **~$25** |
| 2.13" flexible e-paper | 212×104 mono, flexible | same tech, smaller | Crystalfontz CFAP104212D1-0213 / Waveshare | $17 |
| 4" Spectra 6 color (**rigid**) | 600×400, 6-color | static stills, ~19s/frame, **no partial**, rigid glass | Waveshare 4" e-Paper (E) | $52.99 |
| Driver board (if not integrated) | — | UC8151/IL0373 controller | Adafruit eInk Breakout #4224 / Waveshare HAT | — |

**Reality:** flexible color e-paper & small flexible OLED are **not buyable** in maker qty in 2026. Flexible = mono + slow + static only (no motion/game). Use only for a special "static edition" drop.

## 4. Audio — amp / DAC / speaker

| Part | Function | Source | ~Price |
|---|---|---|---|
| **MAX98357A** | mono I²S Class-D amp + DAC (no MCLK, 3 wires) | LCSC C910544 / Adafruit #3006 | **$1.34 / $5.95** |
| NS4168 | I²S Class-D, MAX98357A cost-down | LCSC C910588 | $0.38 |
| AW88298 | I²S smart amp + boost (louder off 1 cell) | LCSC C5162557 | $0.6–1 |
| TAS2505 | I²S speaker amp **+ headphone driver + DSP/EQ** (covers both out paths in one chip) | TI | — |
| **PCM5102A** | I²S DAC, 112dB, PLL 3-wire → line/HP out | LCSC C107671 / Adafruit #6250 | **$0.65 / $4.95** |
| CS4344 | cheap I²S DAC (needs MCLK) | LCSC C8952 | $0.41 |
| **Adafruit Mini Oval #3923** | speaker 30×20×**5mm**, 8Ω 1W | Adafruit | **$1.95** |
| Same Sky CMS-151125-078S | speaker 15×11×**2.5mm** (lowest profile) | Same Sky | $1–2 |
| Adafruit Bone Conductor #1674 | shell-as-diaphragm exciter (dodges speaker-box problem) | Adafruit | ~$8 |

**Decode (software, free):** ESP32-audioI2S (Helix MP3 + faad2 AAC), ESP8266Audio, libhelix, esp-adf. Target: MP3 ≤320k + AAC-LC real-time; Opus/Vorbis OK with PSRAM.
**Pick:** MAX98357A → Mini Oval for onboard sound; PCM5102A → 3.5mm jack, share one I²S bus, jack-detect mutes the amp.

## 5. Storage (content packs)

| Part | Cap | Type | Source | ~Price |
|---|---|---|---|---|
| W25Q256JV | 32MB | QSPI NOR, XIP | LCSC C2682312 | $5.18 |
| **W25Q512JV** | 64MB | QSPI NOR, XIP (~2h Opus) | LCSC C7389628 | **$9.60** |
| W25N01GV | 128MB | SPI NAND (needs FTL/littlefs) | DigiKey | $3.57 |
| **GCT MEM2075** | — | microSD socket, **1.40mm** push-push | DigiKey | **$1.38** |
| Hirose DM3AT-SF-PEJM5 | — | microSD socket, 1.68mm workhorse | DigiKey | $2.06 |

Capacity ref: MP3 128k ≈ 1MB/min; Opus 64k ≈ 2min/MB. One rich drop ≈ 25–50MB.
**Two coherent paths:** (1) **microSD-as-cartridge** (GCT MEM2075, SPI mode) = the cassette-swap ritual + trivial PC authoring; (2) **sealed W25Q512 NOR** = rugged, XIP, USB-C/Wi-Fi updates. Skip NAND unless carrying many packs resident.

## 6. NFC

| Mode | Part | Notes | Source | ~Price |
|---|---|---|---|---|
| Passive tag | NTAG213 inlay | tap→URL, no MCU pin; 144B | shopNFC / Seritag | €0.10–0.40 |
| Passive auth | NTAG 424 DNA inlay | AES-128 + SUN, clone-proof, app-free | shopNFC / GoToTags | €0.60–1.29 |
| **Connected** | **NTAG I²C plus 2k (NT3H2211)** | MCU writes via I²C, phone reads; 64B pass-through SRAM; **5mA harvest / tap-to-wake**; 50pF (easy flex coil) | LCSC C710403 / DigiKey | **$0.73** |
| Connected (big mem) | ST25DV64K-IER6T3 | 8KB EEPROM, 256B mailbox, 1MHz I²C, ISO15693 | LCSC C1852797 | $1.62 |
| Reader / P2P | ST25R3916B | reader + card-emu + **cassette-to-cassette P2P**; auto antenna tuning (fixes flex detune) | DigiKey | $5.98 |
| Reader (cheap) | PN532 module | battle-tested libs | Elechouse | ~$22 |
| Antenna ferrite | Würth WE-FSFS 364004 / TDK IFL04-100NB300X200 | between coil & LiPo (prevents detune) | DigiKey | $13 / $18 |

Antenna: single-layer etched coil on flex, **no ground pour behind it**, ferrite film toward the LiPo, C0G trim-cap footprint. App notes: NXP AN11276, ST AN2972, NXP NFC Antenna Design Hub.
**Pick:** NTAG I²C plus 2k. Upgrade to NTAG 424 DNA (authenticity), ST25DV64K (payloads), or ST25R3916B (tap-to-tap).

## 7. Battery (1S LiPo, slim)

| Cell | Dim T×W×L (mm) | Cap | Source | ~Price | Note |
|---|---|---|---|---|---|
| **PKCell LP503562** | **5.0 × 34 × 62** | 1200mAh | Adafruit #258 / PKCell | **$9.95** | best fit, ~7–9h, PCM included |
| PKCell LP503035 | 5.0 × 30 × 35 | 500mAh | Adafruit #1578 | $7.95 | for the slim build, ~3h |
| spec-order LP504050/505060 | 4.5–5.0 × ~50 × ~60 | ~1500–1800mAh | PKCell / AliExpress | $5–9 | verify datasheet |

**Avoid (too thick, >5mm):** Adafruit #2011 (7mm), PKCell LP803860 (8mm).
Safety: confirm cell ships **with PCM**, or add DW01+FS8205. Charge CC/CV ≤0.5–1C.

## 8. Power management

| Part | Function | Source | ~Price |
|---|---|---|---|
| **MCP73831T-2ATI/OT** | 500mA single-cell charger, SOT-23-5 | LCSC C14879 | **$0.50** |
| BQ24074RGTR | charger **with power-path** (runs while charging / dead battery) | LCSC C54313 | $0.63 |
| TP4056 | 1A charger, cheapest (**no protection** — needs cell PCM) | LCSC C382139 | $0.066 |
| **AP2112K-3.3 / ME6211** | 3.3V LDO (no boost needed; amp+backlight off VBAT) | LCSC | ~$0.05–0.10 |
| TYPE-C-31-M-12 | USB-C connector (16-contact SMD) + **2× 5.1kΩ CC pulldowns** | LCSC C165948 | $0.097 |
| MAX17048 | fuel gauge (optional; else read VBAT via ADC) | LCSC C2682616 | $1.38 |

USB-C wires to ESP32-S3 **native USB** (GPIO19/20) — no CP2102/CH340 bridge needed.

## 9. Interconnect (engine ↔ flex J-card)

| Approach | Stack height | Swap per drop | Source | ~Price |
|---|---|---|---|---|
| **0.5mm FFC/FPC ZIF** | **~0.9–1.2mm** | trivial (flip latch) | Kyocera 6277 / JAE FF03 / Hirose FH12 / generic | $0.11–0.17 |
| Hirose DF40 mezzanine, 0.4mm | 1.5–4.0mm | plug/unplug (needs FR4 backer on flex) | LCSC DF40C series | $0.15–0.76 |
| Solder flex tail direct | ~0.2mm | none (desolder) | — | ~$0 |

**Pick:** 0.5mm FFC/FPC ZIF — lowest profile that's still hand-swappable. Flex tail needs a 0.2–0.3mm stiffener at the contacts.

## 10. PCB / flex fabrication

| Fab | Product | Notes | ~Cost |
|---|---|---|---|
| **JLCPCB flex** | 1–2L plain flex, ENIG gold, yellow/black coverlay, white silk | 5pc MOQ, 4–5 day; NFC coil + cap-touch = free copper | **~$1–3/unit @50–100** |
| PCBWay | flex + **rigid-flex**, more colors, impedance | rigid-flex from ~$1500/5pc (low qty) | — |
| OSH Park flex | 2L flex, US ENIG gold | ~21 day, multiples of 3 | $15/sq-in (3 copies) |

**Engine = normal rigid FR4. J-card = plain JLCPCB flex. Avoid rigid-flex at drop quantities** (5–10× cost vs flex + connector).

## 11. Tape head (reverse cassette-adapter playback)

Use case: drive a small tape head with audio so a real deck's playback head magnetically couples to it ("cassette adapter in reverse"). Mono is fine. No bias circuitry — just AC audio into the coil.

| Source | What you get | ~Price | Where |
|---|---|---|---|
| **Harvest a wired cassette→3.5mm adapter** ← best bet | sprung, correctly-positioned head **+ dummy-reel/auto-stop gear + spring** in one teardown | **$7–9** | DIGITNOW (Amazon B081DVQN9Z), Reshow (B07FKFMRGF), Arsvita (B07N2KPTGW), Aluratek $9.99 |
| AliExpress bare head (current production) | new stereo/mono play/record head, often on an L-bracket w/ leads; 200–300Ω | $4–8 | aliexpress "cassette tape heads"; DYNY62 240Ω, mono 3-pack ~$7.80 ea |
| Amazon Toyvian bare head | dual-channel head, fast US shipping | ~$8 | Amazon B0CXQPMJ76 |
| eBay / VintageAudioCart RH-M-01 | NOS mono ferrite head (thin stock) | ~$6 | ebay Tape-Recorder-Head category |
| **Avoid** | TASCAM/JRF/Nortronics pro deck heads | $160+ | overkill |

**Driving it:** head is low-Z (~200–600Ω DC, ~10mH record / ~100–150mH play); drive like a tiny voice coil from a small amp (**PAM8403 / LM386**) or even the PCM5102A line-out buffered. Play vs record head doesn't matter (reciprocal); stereo head → wire gaps in parallel or drive one for mono. **No HF bias needed.**

**Why harvest wins:** the adapter *is* a reverse-cassette device already — head + spring + the auto-stop-defeating gear train are exactly what Spec A's 3D-printed bottom-edge module needs. Buy 2–3 (leads are fragile on teardown). New heads are still made in China (same supply chain as FiiO CP13 / We Are Rewind decks), so "new production" is real, not just NOS.

**The user has some of these already on hand** — check those first before ordering.

---

## Recommended frozen-engine stack (one line)
ESP32-S3-WROOM-1-N16R8 · 1.91" RM67162 QSPI AMOLED · MAX98357A + Mini Oval speaker · PCM5102A + 3.5mm jack · microSD (GCT MEM2075) or W25Q512 NOR · NTAG I²C plus 2k · PKCell LP503562 1200mAh · MCP73831 + AP2112K-3.3 + USB-C native · 0.5mm FFC/ZIF to a JLCPCB plain-flex J-card.
