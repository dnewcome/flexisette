# flexisette — build the mechanical CAD parts and their renders.
#
#   make             # build every part + render each + the assembly
#   make cad         # build123d -> STL/STEP for frame, panel, insert
#   make parts       # render frame, panel, insert, and the stacked assembly
#   make frame|panel|insert|assembly   # one render
#   make concepts    # the early A/B/C/D concept hero renders + contact sheet
#   make blend-frame|blend-panel|blend-assembly   # open a scene in Blender's GUI
#   make verify      # watertight/validity self-checks
#   make clean       # remove generated STL/STEP/PNG
#   make view        # open the render output folder
#
# Overridable:  make SAMPLES=320   make BLENDER=/path/to/blender   make ATTEMPTS=8

BLENDER ?= /opt/blender-5.0.1-linux-x64/blender
PY      ?= python3
SAMPLES ?= 180
ATTEMPTS ?= 5
# RUN wraps headless renders with LC_ALL=C + retries (flaky OpenColorIO segfault in Blender 5.0)
RUN      = BLENDER="$(BLENDER)" ATTEMPTS=$(ATTEMPTS) render/blender_render.sh
BL_GUI   = LC_ALL=C $(BLENDER) --factory-startup -P

CAD   := cad
BUILD := cad/build
REN   := render
OUT   := render/out
SHELL_STL := assets/cassette-shell-minecraft/side-1-plain.stl
INSERTS   := assets/cassette-shell-minecraft/side-1-insert.stl assets/cassette-shell-minecraft/side-2-insert.stl
RF        := $(REN)/render_frame.py render/blender_render.sh

.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.PHONY: all cad parts concepts frame panel insert assembly specs sheet freecad \
        blend-frame blend-panel blend-assembly verify clean view help

all: parts
parts: frame panel insert assembly
concepts: specs sheet

# ---- CAD (build123d, profiles extracted from the real vendor shell) ----
cad: $(BUILD)/frame.stl $(BUILD)/panel.stl $(BUILD)/insert.stl

$(BUILD)/frame.stl: $(CAD)/frame.py $(CAD)/machine_params.py $(SHELL_STL)
	cd $(CAD) && $(PY) frame.py
$(BUILD)/panel.stl: $(CAD)/panel.py $(CAD)/machine_params.py $(SHELL_STL)
	cd $(CAD) && $(PY) panel.py
$(BUILD)/insert.stl: $(CAD)/insert.py $(INSERTS)
	cd $(CAD) && $(PY) insert.py

$(OUT):
	mkdir -p $(OUT)

# ---- part renders (render_frame.py auto-centres any STL passed as arg 2) ----
frame:      $(OUT)/flexisette_frame.png
panel:      $(OUT)/flexisette_panel.png
insert: $(OUT)/flexisette_insert.png
assembly:   $(OUT)/flexisette_assembly.png

$(OUT)/flexisette_frame.png: $(RF) $(BUILD)/frame.stl | $(OUT)
	$(RUN) $(REN)/render_frame.py "$@" $(BUILD)/frame.stl
$(OUT)/flexisette_panel.png: $(RF) $(BUILD)/panel.stl | $(OUT)
	$(RUN) $(REN)/render_frame.py "$@" $(BUILD)/panel.stl
$(OUT)/flexisette_insert.png: $(RF) $(BUILD)/insert.stl | $(OUT)
	$(RUN) $(REN)/render_frame.py "$@" $(BUILD)/insert.stl
$(OUT)/flexisette_assembly.png: $(REN)/render_assembly.py render/blender_render.sh $(BUILD)/panel.stl $(BUILD)/frame.stl $(BUILD)/insert.stl | $(OUT)
	$(RUN) $(REN)/render_assembly.py "$@"

# ---- early A/B/C/D concept hero renders + 2x2 contact sheet ----
SPECS := A B C D
SPEC_PNGS := $(addprefix $(OUT)/flexisette_,$(addsuffix .png,$(SPECS)))
specs: $(SPEC_PNGS)
$(SPEC_PNGS): $(OUT)/flexisette_%.png: $(REN)/build_render.py render/blender_render.sh | $(OUT)
	$(RUN) $(REN)/build_render.py $* "$@" $(SAMPLES)
sheet: $(OUT)/flexisette_contact_sheet.png
$(OUT)/flexisette_contact_sheet.png: $(SPEC_PNGS)
	montage $(SPEC_PNGS) -tile 2x2 -geometry +6+6 -background '#15151a' \
		-label '%f' -pointsize 18 -fill '#bbb' "$@"

# ---- interactive Blender (GUI) ----
blend-frame:
	$(BL_GUI) $(REN)/render_frame.py -- "$(OUT)/flexisette_frame.png" $(BUILD)/frame.stl
blend-panel:
	$(BL_GUI) $(REN)/render_frame.py -- "$(OUT)/flexisette_panel.png" $(BUILD)/panel.stl
blend-assembly:
	$(BL_GUI) $(REN)/render_assembly.py -- "$(OUT)/flexisette_assembly.png"

# ---- editable FreeCAD feature trees (via the featuretree skill; needs FreeCAD AppImage) ----
freecad:
	cd $(CAD) && $(PY) freecad_export.py

# ---- utility ----
verify:
	cd $(CAD) && $(PY) frame.py && $(PY) panel.py && $(PY) insert.py

clean:
	rm -f $(BUILD)/*.stl $(BUILD)/*.step $(BUILD)/*.FCStd $(BUILD)/*.ir.json $(OUT)/*.png $(OUT)/*.blend

view:
	xdg-open $(OUT) >/dev/null 2>&1 || echo "open $(OUT)/ to see renders"

help:
	@echo "flexisette make targets:"
	@echo "  make             build all parts + renders (frame, panel, insert, assembly)"
	@echo "  make cad         build123d -> STL/STEP for every part"
	@echo "  make parts       render each part + the stacked assembly"
	@echo "  make frame|panel|insert|assembly   one render"
	@echo "  make concepts    early A/B/C/D concept hero renders + contact sheet"
	@echo "  make freecad     editable .FCStd feature trees for frame + panel (featuretree skill)"
	@echo "  make blend-frame|blend-panel|blend-assembly   open a scene in Blender GUI"
	@echo "  make verify      watertight/validity self-checks"
	@echo "  make clean       remove generated STL/STEP/PNG"
	@echo "  make view        open render/out/"
	@echo "  overridable: SAMPLES=320  BLENDER=/path  ATTEMPTS=8"
