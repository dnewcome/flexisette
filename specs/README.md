# flexisette — Form-Factor Specs

Four construction options for the same product. They **share one frozen electrical engine** (see [`../PARTS.md`](../PARTS.md)) — what differs is the *physical build*. The discipline throughout: **freeze the electronics, vary the cosmetics + content**, so a "drop" is cheap.

> A cassette is **~100.5 × 64 × 12 mm**. The Norelco case + a paper (or flex) J-card is the package. The engine BOM is one line:
> ESP32-S3-WROOM-1-N16R8 · 1.91" RM67162 QSPI AMOLED · MAX98357A+speaker / PCM5102A+jack · microSD or W25Q512 · NTAG I²C plus · LP503562 1200mAh · MCP73831 + USB-C native.

## The four

| # | Name | Form | Boards | Thickness | Plays in a real deck? | Battery / runtime | Per-drop cost | Best for |
|---|---|---|---|---|---|---|---|---|
| [A](A-the-deck.md) | **The Deck** | full cassette | 2 rigid + 3D-printed spacers | ~12 mm | ✅ **yes** | 1200 mAh / ~7–9 h | medium | the full "it really plays in a tape deck" object |
| [B](B-the-slim.md) | **The Slim** | cassette outline | 1 rigid | ~5–7 mm | ✖ (needs a carrier) | 500 mAh / ~3 h | high (whole-board respin) | elegant ultra-thin PCB-as-art player |
| [C](C-the-flex.md) | **The Flex** | cassette, flex/rigid-flex | rigid islands + flex | thin–12 mm | partial | island-dependent | high fab | the most distinctive substrate; original "flex cassette" vision |
| [D](D-flex-jcard.md) | **The Flex J-card** | J-card insert | 1 plain flex | <0.5 mm folded | n/a (it's the insert) | none (or NFC-harvest) | **very low (~$1–3)** | the per-drop art/NFC layer — pairs with A/B/C |

## How they relate
- **A, B, C are mutually exclusive device bodies** — pick one to build.
- **D is not a competitor — it's the per-drop skin.** The flex J-card (D) is the cheap, swappable art + NFC + touch layer that any of A/B/C uses as its insert/front. It *is* the parametric mechanism; A/B/C are just how deep the electronics go behind it.
- **Recommended first build:** prototype the engine on a breadboard (the "first slice"), then realize it as **A (The Deck)** — it's the only one that delivers the tape-deck-playback payoff — with **D** as its art layer. B and C are alternate editions to explore later.
