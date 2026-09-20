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
EDGE_CHAMFER = 0.5    # mm, general outer edges

# --- Tolerances -----------------------------------------------------------
# Not physical dimensions -- used only for float-safe geometric comparisons
# (e.g. selecting edges by position) in part code.

EDGE_MATCH_TOLERANCE = 1e-6   # mm
