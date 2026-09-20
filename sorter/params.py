"""Single source of truth for every dimension in this project.

No numeric dimension may appear anywhere else in the codebase. Every part,
geometry function, and check must import its numbers from here. If a value
needed elsewhere is missing, add it to this file rather than hard-coding it
at the call site.

Units are millimetres and degrees everywhere.

Implements phase1-cad-spec-revB.md plus phase1-cad-spec-revC.md (repo root).
One value remains provisional pending real hardware: `SHAFT_HEIGHT_ABOVE_PLATE`
(see the note beside it). `BELT_LOOP_LENGTH` is now the real belt bought (rev
C), but the `CENTRE_DIST` that follows from it is an open machine-layout
question, not a guess -- see rev C §8 and `sorter/README.md`.
"""

import math

# --- Belt and drive ---------------------------------------------------

BELT_PROFILE = "HTD-5M"          # informational
BELT_PITCH = 5.0                 # mm, tooth pitch
BELT_LOOP_LENGTH = 390.0         # mm, stock closed loop, 78 teeth -- real belt bought, HTD-5M x 9mm (rev C)
BELT_WIDTH = 9.0                 # mm
BELT_THICKNESS = 3.8             # mm, tooth tip to back
BELT_PLD = 0.5715                # mm, pitch line differential, HTD-5M
PULLEY_TEETH = 24
PULLEY_FACE_WIDTH = 5.0          # mm, narrower than the belt, deliberately; printed part
BELT_SPACING = 60.0              # mm, centre to centre of the two belts

PULLEY_PD = PULLEY_TEETH * BELT_PITCH / math.pi   # mm, 38.1972...
CENTRE_DIST = (BELT_LOOP_LENGTH - math.pi * PULLEY_PD) / 2   # mm, 135.0 -- short span, unconfirmed against machine layout, see rev C §8

# --- Tooth profile (HTD-5M) -- phase3-cad-spec-revB.md -----------------
# Closed-form: a single flank arc reaching the apex directly, blended into
# the land by a root fillet on each side. No separate tip arc, no solver.

FLANK_RADIUS = 1.49       # mm -- APPROXIMATE, tune per revB §7
ROOT_RADIUS = 0.43        # mm -- APPROXIMATE, tune per revB §7
FLANK_CENTRE_Y = 0.5715   # mm, flank arc centre height above the land

# FLANK_CENTRE_Y and BELT_PLD are the same physical offset (the belt's pitch
# line differential is, by definition, where the tooth's crown arc is
# centred). If this ever fails, the profile and the belt geometry have
# drifted apart -- that's a real bug to investigate, not a tolerance to
# widen. See revB §3.
assert FLANK_CENTRE_Y == BELT_PLD, "FLANK_CENTRE_Y must equal BELT_PLD -- see revB §3"

TOOTH_HEIGHT = FLANK_CENTRE_Y + FLANK_RADIUS   # mm, derived, 2.0615
assert abs(TOOTH_HEIGHT - 2.06) < 0.01, "TOOTH_HEIGHT drifted from the published HTD-5M figure"

LAND_WIDTH = BELT_PITCH - 2 * math.sqrt(
    (FLANK_RADIUS + ROOT_RADIUS) ** 2 - (ROOT_RADIUS - FLANK_CENTRE_Y) ** 2
)   # mm, derived, 1.17 -- see revB §3 for the root-fillet-centre construction

GROOVE_CLEARANCE = 0.10   # mm, tune on the printer

# --- Pulley (printed) -- phase3-cad-spec.md §4 --------------------------

PULLEY_OD = PULLEY_PD - 2 * BELT_PLD   # mm, derived, 37.054...
PULLEY_BORE = 8.0                 # mm
PULLEY_BORE_CLEARANCE = 0.15      # mm, printed hole runs undersize
PULLEY_HUB_DIA = 22.0             # mm
PULLEY_HUB_LENGTH = 10.0          # mm, beyond the toothed face
PULLEY_GRUB_M = 4.0               # mm, M4, into a heat-set insert
PULLEY_INSERT_DIA = 5.6           # mm
PULLEY_INSERT_DEPTH = 8.0         # mm

# --- Belt (derived, phase 3) --------------------------------------------

BELT_BACK_THICKNESS = BELT_THICKNESS - TOOTH_HEIGHT   # mm, derived, 1.74
assert BELT_PLD < BELT_BACK_THICKNESS, "pitch line must fall inside the belt's backing"

# --- Calibration coupon -- phase3-cad-spec.md §7 ------------------------

COUPON_LENGTH = 40.0       # mm
COUPON_GROOVE_COUNT = 5    # count

# --- Machine ------------------------------------------------------------

INCLINE = 40.0        # deg, from horizontal
SHAFT_DIA = 8.0        # mm
SHAFT_LENGTH = 145.0   # mm
BEARING_SPACING = 100.0           # mm, pillow block centres
SHAFT_HEIGHT_ABOVE_PLATE = 48.0   # mm -- PROVISIONAL, depends on the pillow blocks actually bought; measure before modelling the standoff
SHAFT_SPEED = 30.0     # rpm, gives 60 mm/s belt speed

# --- Frame -- existing, uncut ---------------------------------------------
# Recorded so later phases can position against it. Nothing in phase 1 uses these.

FRAME_LENGTH = 552.0       # mm
FRAME_WIDTH = 274.0        # mm, overall
FRAME_PROFILE = 20.0       # mm, 2020
FRAME_INNER_WIDTH = FRAME_WIDTH - 2 * FRAME_PROFILE   # mm, 234.0
FRAME_SLOT_WIDTH = 6.0     # mm, standard T-nut

# --- Slat -----------------------------------------------------------------

SLAT_PITCH = 15.0      # mm, 3 belt teeth -- rev C, was 4 teeth/20mm; 78-tooth belt isn't divisible by 4
SLAT_LENGTH = 80.0     # mm, across the machine, local z
SLAT_WIDTH = 13.0      # mm, along the run, local x -- rev C, keeps the 2mm inter-slat gap
SLAT_THICKNESS = 3.0   # mm, local y
CLEAT_EVERY = 3        # every third slat is cleated
CLEAT_HEIGHT = 12.0    # mm, above the slat top face
CLEAT_WIDTH_ROOT = 10.0    # mm, along local x, at the slat surface
CLEAT_WIDTH_TIP = 4.0      # mm, along local x, at the top -- drafted for printing
CLEAT_LENGTH = 74.0        # mm, along local z, centred
CLEAT_ROOT_FILLET = 1.0    # mm, both sides

SLAT_COUNT = BELT_LOOP_LENGTH / SLAT_PITCH   # count, 26
assert SLAT_COUNT == int(SLAT_COUNT), "BELT_LOOP_LENGTH must be an integer multiple of SLAT_PITCH"
SLAT_COUNT = int(SLAT_COUNT)

# --- Saddle -----------------------------------------------------------------
# Tab z-positions derive from BELT_WIDTH and SADDLE_INTERFERENCE alone (no
# separate clearance parameter -- see parts/slat.py _saddle_pair()).

SADDLE_TAB_THICKNESS = 2.5    # mm, along local z
SADDLE_TAB_DEPTH = 6.0        # mm, into negative local y
SADDLE_TAB_LENGTH = 12.0      # mm, along local x, centred
SADDLE_INTERFERENCE = 0.2     # mm, total, so nominal gap = BELT_WIDTH - 0.2
SADDLE_LIP_PROJECTION = 0.8   # mm, inward, at the tab tip
SADDLE_LIP_HEIGHT = 1.0       # mm, along local y

# --- Skirts -- recorded, not built in phase 1 ------------------------------

SKIRT_HEIGHT = 28.0    # mm, above slat top
SKIRT_GAP = 1.5        # mm, skirt bottom to slat top
SKIRT_INSET = 38.0     # mm, from centreline

# --- Printing -----------------------------------------------------------------

PRINT_ROT_PLAIN = (180.0, 0.0, 0.0)     # deg, top face down, tabs up
PRINT_ROT_CLEATED = (180.0, 0.0, 0.0)   # deg, cleat tip down, tabs up
PRINT_ROT_PULLEY = (0.0, 0.0, 0.0)      # deg, hub end down, axis vertical -- native orientation
PRINT_ROT_COUPON = (0.0, 0.0, 0.0)      # deg, flat on the bed -- native orientation
EDGE_CHAMFER = 0.5    # mm, general outer edges

# --- Tolerances -----------------------------------------------------------
# Not physical dimensions -- used only for float-safe geometric comparisons
# (e.g. selecting edges by position) in part code.

EDGE_MATCH_TOLERANCE = 1e-6   # mm
