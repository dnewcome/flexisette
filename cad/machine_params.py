"""flexisette — single source of truth for the shell assembly.

The shell is a sandwich: PCB half (bottom) + spacer frame + PCB half (top),
total thickness = a standard cassette (~12 mm). The spacer's front edge carries
(or receives) the head-holes insert — see assets/cassette-shell-minecraft/side-1-insert.stl.
"""
from build123d import Location, Pos, Rot  # noqa: F401  (re-exported for assembly scripts)

# --- cassette shell footprint (mm) ---
SHELL_W = 100.5     # cassette width
SHELL_H = 64.0      # cassette height
CORNER_R = 4.0      # outline corner radius

# --- thickness stack (Z), fully parametric ---
# Set CASSETTE_T to your target standard cassette thickness; the frame height follows.
PCB_T = 1.57                        # each PCB half (standard 0.062" board = 1.57 mm)
PANEL_T = PCB_T                     # printed face panel — subs for a PCB on one side (keeps 9 mm)
CASSETTE_T = 9.0                    # nominal shell thickness  <-- tune this
SPACER_GAP = CASSETTE_T - 2 * PCB_T # frame thickness, derived (= 5.86 mm: 9 - 2x1.57)

# --- spacer frame ---
WALL = 3.0                          # head-variant perimeter wall thickness
DUMMY_WALL = 5.0                    # dummy-variant: beefier, prints mostly-solid (infill)

# --- magnetic-head bay (head variant only) ---
# placeholder dims for a head harvested from a cassette adapter; refine against the real head
HEAD_BAY_D = 9.0                    # depth of the head shelf behind the front window (along +Y)
HEAD_POCKET_W = 16.0                # head pocket width (X)
HEAD_POCKET_H = 6.0                 # head pocket height (Z), must be < SPACER_GAP

# --- head_frame.py: monolithic head-holes frame with PCB screw bosses ---
HEAD_WIN_W = 24.0                   # head-access window width in the front wall (matches insert mouth)
HEAD_WIN_H = 6.0                    # head-access window height (must be <= SPACER_GAP)
CAPSTAN_D = 2.6                     # capstan / guide clearance hole diameter
CAPSTAN_DX = 19.0                   # capstan holes at +/- this X from centre
# Corner screws: M2 thread-forming, tapped straight into the plastic (non-structural cap).
# Blind pilot from EACH face (top + bottom PCB each tap in from their own side) — no through
# hole, no heat-set, no backing nut. Corners are thickened into bosses so the hole clears.
SCREW_CLEAR_D = 2.4                 # M2 clearance (drilled in the PCB halves)
SCREW_PILOT_D = 1.7                # M2 thread-forming pilot bore in the plastic
SCREW_PILOT_DEPTH = 2.5            # blind pilot depth from each face (< GAP/2 so they don't meet)
SCREW_BOSS_D = 7.0                 # corner boss diameter (thickened around the hole)
SCREW_HEATSET_D = 3.2             # (kept for the older head_frame/spacer variants)
SCREW_INSET = 5.0                  # (legacy) boss inset for the parametric head_frame variant

# --- 2-piece print: thin frame + separate tape-head protrusion; PCBs notch to clear it ---
PROTR_W = 70.2                      # tape-head protrusion width (= vendor insert width)
PROTR_CLEAR = 0.8                  # clearance around the protrusion (frame slot + PCB notch)
NOTCH_H = 18.0                     # PCB bottom-edge notch depth, clears the ~16 mm-tall protrusion
REEL_D = 11.0                      # reel window diameter in the PCB (cassette look, per reference)
REEL_DX = 20.0                     # reel windows at +/- this X from centre

# --- head-holes insert (measured from side-1-insert.stl) ---
INSERT_W = 70.2                     # width along cassette X
INSERT_H = 16.0                     # height along cassette Y (front band)
INSERT_T = SPACER_GAP              # 8.8 mm thickness == the inter-PCB gap

FRONT_Y = -SHELL_H / 2              # the head-holes edge (front of the cassette)


def place(solid, frm: Location, onto: Location):
    """Snap a part so its local mate `frm` coincides with world target `onto`."""
    return (onto * frm.inverse()) * solid
