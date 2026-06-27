# flexisette — Downloaded Model Files (provenance log)

Running log of 3D models pulled from the web: source, author, license, and where the files live in this repo. **Append new downloads here.**

> ⚠️ Printables pages can't be auto-fetched by the assistant (the server returns oversized headers → "header overflow"). So **license/author fields below are TBD until confirmed on the source page.** Verify before redistributing or any commercial use.

---

## Cassette shells

### 1. Cassette Shell — Sides A + B   ✅ downloaded & extracted
- **Source:** https://www.printables.com/model/176745-cassette-shell-sides-a-b
- **Author:** eric c
- **License:** TBD (verify on Printables)
- **Downloaded:** 2026-06-25 — zip `cassette-shell-sides-a-b-model_files.zip`
- **Local:** `assets/cassette-shell/`
- **Files:**
  - `cassette_tape_-_side_a.stl` — half-shell A (mesh)
  - `cassette_tape_-_side_b.stl` — half-shell B (mesh)
  - `cassette_tape_-_side_1.step` — half-shell (editable CAD)
  - `cassette_tape_-_side_2.step` — half-shell (editable CAD)
  - `176745-…-.pdf` — model spec sheet
- **Measured (side_a):** bbox **102.25 × 8.8 × 63.75 mm**; single solid; the **tape-head window + capstan/pinch openings are molded into the bottom edge of each half** — there is *no* separate head-holes part in this model.

### 2. Minecraft Soundtrack Cassette Shell (remix)   ✅ downloaded & extracted
- **Source:** https://www.printables.com/model/836410-minecraft-soundtrack-cassette-shell-remix
- **Author:** TBD (verify on Printables)
- **License:** TBD (verify on Printables)
- **Downloaded:** 2026-06-25 — zip `minecraft-soundtrack-cassette-shell-remix-model_files.zip`
- **Local:** `assets/cassette-shell-minecraft/`
- **Files:**
  - `side-1-insert.stl` — ⭐ **THE HEAD-HOLES BRIDGE PART** — front-edge insert with the tape-head window, capstan holes, pinch-roller openings + registration tabs. **70.15 × 8.8 × 16.0 mm.** Standalone & printable; this is the "third part."
  - `side-2-insert.stl` — ⭐ mating insert for the other side. **70.15 × 9.05 × 16.0 mm.**
  - `side-1-plain.stl`, `side-2-plain.stl` — plain shell halves (insert removed; the insert snaps into these)
  - `Minecraft/alpha-side-1.stl`, `alpha-side-2.stl`, `beta-side-1.stl`, `beta-side-2.stl` — Minecraft-art full shells (two variants)
  - `cassettes-remix.step` — full editable CAD assembly
  - `836410-…-.pdf` — model spec sheet
  - `insert-persp.png`, `insert-front.png` — reference renders of the insert (assistant-generated)
- **Key insight:** this remix splits the cassette into **plain shell + snap-in front insert**, where the insert *is* the head-holes bridge. That maps directly onto **flexisette Spec A's printed bottom-edge bridge** — use `side-1-insert.stl` as-is, or as the dimensional reference to model flexisette's own bridge (which additionally has to mount the transmit head + auto-stop gear).

---

## How to add a download
1. Save the zip/files into `assets/<model-slug>/`.
2. Add a section here: source URL, author, license, files, local path, date, notes.
3. Ping me to inspect/measure/convert it.
