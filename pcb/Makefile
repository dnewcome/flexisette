# flexisette PCB — tscircuit generate + the encoded place->route->measure loop.
# (pcb-layout flow: deterministic placement, route-in-isolation blocks, hand-finish in KiCad.)
#
#   make dev [FILE=modules/mcu.circuit.tsx]      live viewer (https://localhost:3020)
#   make build                                   build composed board -> dist/
#   make modules                                 build every block standalone
#   make routecheck [MODS="mcu audio"]           MEASURED LOOP: unrouted + time per block
#   make sweep MOD=mcu REF=U2 POS="-2,11 3,9"    move a part, report unrouted per spot
#   make module NAME=power                       scaffold a new subcircuit block
#   make pinmap                                  regenerate lib/pinmap.json from imports/
#   make render                                  dist PCB SVGs -> PNGs in build/
#   make export                                  composed board -> KiCad (.kicad_pcb)
#   make clean

BUN_BIN := $(HOME)/.bun/bin
TSCI    := PATH="$(BUN_BIN):$$PATH" ./node_modules/.bin/tsci
FILE    ?= index.circuit.tsx
MODS    ?=

.DEFAULT_GOAL := help
.PHONY: help dev build modules outline routecheck freeroute autoplace test sweep module pinmap render export clean

# Autoplace the subcircuit blocks (anneal HPWL under outline/cutout/courtyard gates).
autoplace:
	@node scripts/autoplace.mjs $(FILE) $(AP)

# Unit tests for the tooling (the autoplacer core).
test:
	@node --test tests/*.test.mjs

help:
	@grep -E '^#   make' $(MAKEFILE_LIST) | sed 's/^# //'

dev:
	$(TSCI) dev $(FILE)

build:
	$(TSCI) build index.circuit.tsx --pcb-only

modules:
	@for f in modules/*.circuit.tsx; do echo "== $$f =="; \
	  $(TSCI) build $$f --disable-parts-engine --pcb-only; done

# Board-outline rule — flag parts OUTSIDE the outline or INSIDE a cutout
# (tscircuit has no keep-in; pcbX/pcbY is manual). Run before routing.
outline:
	@node scripts/outline-check.mjs $(FILE)

# THE loop — drive UNROUTED -> 0 and TIME down. Ground truth, not trace counts.
routecheck:
	@bash scripts/routecheck.sh $(MODS)

# Route the whole board with Freerouting (DSN -> freert -> .ses). Import the
# .ses into KiCad to get a fully-routed board (45 degree). Often reaches 0
# unrouted where sequential-trace stalls.
freeroute:
	@bash scripts/freeroute.sh $(FILE)

# Semi-automate the edge-aware search for one part.
sweep:
	@node scripts/place-sweep.mjs $(MOD) $(REF) $(POS)

# Stamp a new route-in-isolation subcircuit block.
module:
	@bash scripts/module-scaffold.sh $(NAME)

# Rebuild the footprint pin-coordinate map the Decap helper reads.
pinmap:
	@node tools/genpinmap.mjs

render:
	@mkdir -p build; for svg in $$(find dist -name 'pcb.svg'); do \
	  name=$$(echo $$svg | sed 's|dist/||; s|/pcb.svg||; s|/|_|g'); \
	  convert -background black -density 150 $$svg build/$${name}_pcb.png \
	    && echo "wrote build/$${name}_pcb.png"; done

# Hand off placement + pours + ratsnest to KiCad for hand-routing.
export:
	$(TSCI) export -f kicad_pcb index.circuit.tsx

clean:
	rm -rf dist build/routecheck build/*_pcb.png
