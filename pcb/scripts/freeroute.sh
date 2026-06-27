#!/usr/bin/env bash
# freeroute.sh <board.dsn | circuit.tsx> — route a board with FREEROUTING.
#
# THE working KiCad flow (the .ses WILL import) — 3 steps, two are GUI:
#   1. KiCad GUI:  File > Export > Specctra DSN          -> board.dsn
#        (headless `pcbnew.ExportSpecctraDSN` returns False — it needs the GUI app
#         context — and `kicad-cli` has no specctra, so this step is manual.)
#   2. bash scripts/freeroute.sh board.dsn               -> build/board.ses   (this)
#   3. KiCad GUI:  File > Import > Specctra Session > build/board.ses
#   KiCad's SES import ONLY accepts a session from a DSN KiCad ITSELF exported.
#   A SES routed from tscircuit's DSN has foreign ids and WILL NOT import.
#
# MEASUREMENT-ONLY mode (compare routers; does NOT produce an importable board):
#   bash scripts/freeroute.sh index.circuit.tsx   # exports tscircuit DSN + routes
#
# Freerouting = real maze router (ripup-retry, 45 deg). Needs freert
# (~/.local/bin/freert, Java; override FREERT=).
set -u
cd "$(dirname "$0")/.." || exit 1
export PATH="$HOME/.bun/bin:$PATH"
FREERT=${FREERT:-$HOME/.local/bin/freert}
arg=${1:-index.circuit.tsx}
mkdir -p build; LOG=build/freeroute.log
[ -x "$FREERT" ] || { echo "freerouting CLI not at $FREERT (set FREERT=)"; exit 1; }

case "$arg" in
  *.dsn)
    dsn="$arg"; base=$(basename "$dsn" .dsn); mode="KiCad DSN -> importable" ;;
  *)
    base=$(basename "$arg" | sed -E 's/\.circuit\.tsx$//; s/\.tsx$//')
    echo "NOTE: tscircuit DSN = completion MEASUREMENT ONLY (won't import to KiCad)."
    echo "      For an importable board, export the DSN from KiCad and pass the .dsn."
    timeout 200 ./node_modules/.bin/tsci export "$arg" -f specctra-dsn > "$LOG" 2>&1
    dsn=$(ls -t *.dsn 2>/dev/null | head -1); mode="tscircuit DSN -> measurement only" ;;
esac
[ -f "$dsn" ] || { echo "no DSN found ($dsn) — see $LOG"; exit 1; }

# .dsn mode (KiCad's own DSN) -> importable .ses; .tsx mode -> ".measure.ses"
# (a deliberately different name so it can't be mistaken for an importable file).
case "$arg" in *.dsn) ses="build/$base.ses";; *) ses="build/$base.measure.ses";; esac
echo "freerouting $dsn  [$mode] ..."
JAVA_TOOL_OPTIONS="-Djava.awt.headless=true" timeout 360 "$FREERT" -de "$dsn" -do "$ses" >> "$LOG" 2>&1
# Freerouting writes an empty "(host_version )"; KiCad's specctra parser rejects it
# ("expecting a symbol or number" at that line). Patch so the .ses will import.
[ -f "$ses" ] && sed -i 's/(host_version )/(host_version "freerouting")/' "$ses"
last=$(grep -oE 'with the score of [0-9.]+ \([^)]*\)' "$LOG" | tail -1)
inc=$(grep -oE '"incomplete_count": *[0-9]+' "$LOG" | tail -1 | grep -oE '[0-9]+$')
vias=$(grep -oE '"via_count": *[0-9]+' "$LOG" | tail -1 | grep -oE '[0-9]+$')
echo "  ${last:-see $LOG}"
echo "  unrouted: ${inc:-?}   vias: ${vias:-?}   ->  $ses"
case "$arg" in
  *.dsn) echo "  next: KiCad  File > Import > Specctra Session > $ses" ;;
  *)     echo "  (measurement only — re-run on a KiCad-exported .dsn to get an importable board)" ;;
esac
