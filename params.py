"""Single source of truth for every dimension in this project.

No numeric dimension may appear anywhere else in the codebase. Every part,
geometry function, and check must import its numbers from here. If a value
needed elsewhere is missing, add it to this file rather than hard-coding it
at the call site.

Units are millimetres and degrees everywhere.

Implements docs/specs/phase1-cad-spec.md through -revD.md, the parameter
tables of phase3-cad-spec-revB.md renumbered for the rev D belt, the
frame/bridge-plate subset of phase2-cad-spec.md needed by phase4-cad-spec.md,
and docs/specs/drivetrain-spec.md rev B §3, which supersedes phase 3's pulley.
One value remains provisional pending real hardware: `SHAFT_HEIGHT_ABOVE_PLATE`
(see the note beside it). The belt is the HTD-3M x 15mm x 828mm loop chosen
in rev D; `CENTRE_DIST` follows from it and is no longer an open question.
"""

import math

# --- Belt and drive ---------------------------------------------------

BELT_PROFILE = "HTD-3M"          # informational -- rev D, was HTD-5M
BELT_PITCH = 3.0                 # mm, tooth pitch
BELT_LOOP_LENGTH = 828.0         # mm, stock closed loop, 276 teeth -- the belt chosen in rev D, HTD-3M x 15mm
BELT_WIDTH = 15.0                # mm
BELT_THICKNESS = 2.4             # mm, tooth tip to back, published HTD-3M figure (some sheets say 2.44) -- caliper it
BELT_PLD = 0.381                 # mm, pitch line differential, HTD-3M
PULLEY_TEETH = 40                # 40 x 3mm = 120mm circumference, the same PD as rev C's 24 x 5mm
PULLEY_FACE_WIDTH = 5.0          # mm, narrower than the belt, deliberately; printed part
BELT_SPACING = 54.0              # mm, centre to centre of the two belts -- rev D, was 60; keeps the 15mm belt's tabs 2mm inside the slat ends

PULLEY_PD = PULLEY_TEETH * BELT_PITCH / math.pi   # mm, 38.1972...
CENTRE_DIST = (BELT_LOOP_LENGTH - math.pi * PULLEY_PD) / 2   # mm, 354.0 -- rev D; the rev C layout question is closed

# --- Tooth profile (HTD-3M) -- phase3-cad-spec-revB.md, renumbered by rev D --
# Closed-form: a single flank arc reaching the apex directly, blended into
# the land by a root fillet on each side. No separate tip arc, no solver.
# Rev D starting values: FLANK_RADIUS chosen so TOOTH_HEIGHT hits the
# published 3M tooth height (1.17), ROOT_RADIUS scaled 3/5 from the 5M guess.

# Since drivetrain-spec rev B these shape the belt reference solid only.
# Nothing printed depends on them; tune them only if the belt model stops
# fitting the standard groove (drivetrain-spec §12.4).

FLANK_RADIUS = 0.79       # mm -- APPROXIMATE, belt model only
ROOT_RADIUS = 0.26        # mm -- APPROXIMATE, belt model only
FLANK_CENTRE_Y = 0.381    # mm, flank arc centre height above the land

# FLANK_CENTRE_Y and BELT_PLD are the same physical offset (the belt's pitch
# line differential is, by definition, where the tooth's crown arc is
# centred). If this ever fails, the profile and the belt geometry have
# drifted apart -- that's a real bug to investigate, not a tolerance to
# widen. See revB §3.
assert FLANK_CENTRE_Y == BELT_PLD, "FLANK_CENTRE_Y must equal BELT_PLD -- see revB §3"

TOOTH_HEIGHT = FLANK_CENTRE_Y + FLANK_RADIUS   # mm, derived, 1.171
assert abs(TOOTH_HEIGHT - 1.17) < 0.01, "TOOTH_HEIGHT drifted from the published HTD-3M figure"

LAND_WIDTH = BELT_PITCH - 2 * math.sqrt(
    (FLANK_RADIUS + ROOT_RADIUS) ** 2 - (ROOT_RADIUS - FLANK_CENTRE_Y) ** 2
)   # mm, derived, 0.91 -- see revB §3 for the root-fillet-centre construction

# --- Belt (derived, phase 3) --------------------------------------------

BELT_BACK_THICKNESS = BELT_THICKNESS - TOOTH_HEIGHT   # mm, derived, 1.229
assert BELT_PLD < BELT_BACK_THICKNESS, "pitch line must fall inside the belt's backing"

# --- Pulley (printed) -- drivetrain-spec.md §3.3, §5.6 -------------------

PULLEY_OD = PULLEY_PD - 2 * BELT_PLD   # mm, derived, 37.435...
PULLEY_BORE = 8.0                 # mm
PULLEY_BORE_CLEARANCE = 0.15      # mm, printed hole runs undersize
PULLEY_BORE_CHAMFER = 0.4         # mm, both ends of the bore
PULLEY_GRUB_M = 4.0               # mm, M4, into a heat-set insert
PULLEY_GRUB_CLEARANCE_DIA = 4.5   # mm, standard M4 clearance hole, insert pocket through to the bore
PULLEY_INSERT_DIA = 5.6           # mm
PULLEY_INSERT_DEPTH = 6.0         # mm -- PROVISIONAL, was 8.0, which broke into the bore (drivetrain-spec §5.6)
PULLEY_INSERT_MIN_WALL = 2.0      # mm, least material between the insert pocket and the bore

# Standard HTD-3M pulley groove, read from CADENAS model 40015040
# (reference/htd3m_40t_40015040.stp). VALID FOR 40 TEETH ONLY -- the standard
# groove varies with tooth count. Catalogue values: never tune these to make
# a print or a check fit (drivetrain-spec §4.2, §12.4).

PULLEY_GROOVE_TEETH = 40          # count, the only tooth count the values below describe
PULLEY_GROOVE_BOTTOM_R = 17.501   # mm, bottom arc radius, about the pulley axis
PULLEY_GROOVE_FLANK_R = 0.700     # mm, concave flank arc
PULLEY_GROOVE_FLANK_U = 0.2476    # mm, flank arc centre, tangential offset from the groove centreline
PULLEY_GROOVE_TIP_R = 0.191       # mm, convex tip radius onto the OD land
PULLEY_GROOVE_TIP_U = 1.1883      # mm, tip arc centre, tangential offset
PULLEY_GROOVE_DEPTH = PULLEY_OD / 2 - PULLEY_GROOVE_BOTTOM_R   # mm, derived, 1.2165 (file: 1.219, from its rounded OD)
PULLEY_GROOVE_PHASE = 4.5         # deg, first groove centre from local +y towards +x, so a land lies on +y
assert PULLEY_TEETH == PULLEY_GROOVE_TEETH, "the PULLEY_GROOVE_ values are only valid for a 40-tooth pulley"

# Printer compensation, both set from the ring coupon (drivetrain-spec §13).

PULLEY_GROOVE_COMP = 0.0          # mm -- PROVISIONAL, uniform outward offset of every groove edge
PULLEY_OD_COMP = 0.0              # mm -- PROVISIONAL, subtracted from the modelled OD (a diameter)
assert PULLEY_GROOVE_COMP < PULLEY_GROOVE_TIP_R, "compensation would consume the groove's tip radius"

# --- Shaft set (printed): two pulleys and a guide wheel -- drivetrain-spec.md §5

SHAFTSET_LENGTH = 2 * (BELT_SPACING / 2 + PULLEY_FACE_WIDTH / 2)   # mm, derived, 59.0
DRUM_DIA = 26.0                   # mm -- PROVISIONAL, between the guide wheel and each pulley
DRUM_TAB_CLEAR = 1.0              # mm, minimum radial running clearance, drum to tab tip
PULLEY_SKIRT_R = 16.8             # mm -- PROVISIONAL, radius the drum flares to under the pulley face
BELT_TOOTH_CLEAR = 0.5            # mm, minimum, flare to overhanging belt teeth
SHAFTSET_CONE_ANGLE = 45.0        # deg, from the axis; every outward step is a cone this steep, to print unsupported
END_CHAMFER = 0.3                 # mm, on both end faces, against elephant's foot
GRUB_Z = 17.5                     # mm -- PROVISIONAL, +/-, the two grub screw planes
SHAFT_FLAT_DEPTH = 0.5            # mm, filed on the shaft
SHAFT_FLAT_LENGTH = 45.0          # mm, centred on the shaft set

# --- Guide: lug on every slat, V-groove on each shaft set -- drivetrain-spec.md §5.5, §6.1

LUG_DEPTH = 4.0                   # mm -- PROVISIONAL, below the slat contact face
LUG_TIP_WIDTH = 3.0               # mm -- PROVISIONAL, across the machine
LUG_ANGLE = 90.0                  # deg, included; 45 deg flanks print, the 40 deg industrial V would not
LUG_TOP_WIDTH = LUG_TIP_WIDTH + 2 * LUG_DEPTH * math.tan(math.radians(LUG_ANGLE / 2))   # mm, derived, 11.0
LUG_LENGTH = 8.0                  # mm -- PROVISIONAL, along the run, centred on the slat
LUG_END_CHAMFER = 1.0             # mm, leading and trailing ends, for groove entry
GUIDE_WIDTH = 16.0                # mm -- PROVISIONAL, wheel face, across the machine
GUIDE_RIM_GAP = 0.5               # mm, rim radius = belt back - this
GROOVE_FLANK_CLEAR = 0.5          # mm -- PROVISIONAL, normal to each flank
GROOVE_TIP_CLEAR = 1.5            # mm, below the lug tip; the lug never bottoms

# --- Take-up: the tail bridge plate slides in its T-slots -- drivetrain-spec.md §9.3

TAIL_TAKEUP_MIN = -4.0            # mm -- PROVISIONAL, tail plate toward the head, for fitting the belt
TAIL_TAKEUP_MAX = 2.0             # mm -- PROVISIONAL, away from the head, for tension and belt tolerance

# --- Calibration coupons -- drivetrain-spec.md §10 -----------------------

RING_COUPON_THICKNESS = 3.0       # mm

# --- Machine ------------------------------------------------------------

INCLINE = 40.0        # deg, from horizontal
SHAFT_DIA = 8.0        # mm
SHAFT_LENGTH = 145.0   # mm
BEARING_SPACING = 100.0           # mm, pillow block centres
SHAFT_HEIGHT_ABOVE_PLATE = 48.0   # mm -- PROVISIONAL, depends on the pillow blocks actually bought; measure before modelling the standoff
SHAFT_SPEED = 30.0     # rpm, gives 60 mm/s belt speed

# --- Frame -- existing, uncut ---------------------------------------------
# Owned hardware, modelled as a reference solid in phase 4 (phase4-cad-spec.md
# §5), never exported.

FRAME_LENGTH = 552.0       # mm
FRAME_WIDTH = 274.0        # mm, overall
FRAME_PROFILE = 20.0       # mm, 2020
FRAME_INNER_WIDTH = FRAME_WIDTH - 2 * FRAME_PROFILE   # mm, 234.0
FRAME_SLOT_WIDTH = 6.0     # mm, standard T-nut
FRAME_SLOT_DEPTH = 6.0     # mm, cosmetic groove depth; the real T profile isn't modelled
FRAME_END_LENGTH = FRAME_INNER_WIDTH   # mm, 234.0, end members span between the rails
FRAME_T_START = -60.0      # mm, run parameter at the frame's tail end (phase 4 §3)

# The frame must overhang the head shaft far enough to carry the motor.
assert FRAME_T_START + FRAME_LENGTH > CENTRE_DIST + 60, "frame too short to carry the motor past the head shaft"

# --- Bridge plates -- phase2-cad-spec.md §4, phase4-cad-spec.md §6 ----------
# Plywood, cut not printed. PLATE_LENGTH is FRAME_WIDTH, not FRAME_INNER_WIDTH
# as phase 2 §4 tabulates -- see README.md "Bridge plate length".

PLATE_THICKNESS = 9.0      # mm, plywood
PLATE_WIDTH = 45.0         # mm, along the run
PLATE_LENGTH = FRAME_WIDTH   # mm, 274.0, across the machine, resting on both rail tops
PLATE_COUNT_BEARING = 2    # count, tail and head, carry the pillow blocks
PLATE_COUNT_SUPPORT = 3    # count, evenly spaced between, carry the skirt posts
PLATE_STATIONS = PLATE_COUNT_BEARING + PLATE_COUNT_SUPPORT   # count, 5
PLATE_BOLT_M = 5.0         # mm, M5 into frame T-nuts
PLATE_BOLT_CLEARANCE_DIA = 5.5   # mm, standard M5 clearance hole
PLATE_BOLT_X = 12.0        # mm, hole offset from the plate's centreline, along the run
PLATE_BOLT_Z = FRAME_WIDTH / 2 - FRAME_PROFILE / 2   # mm, 127.0, on the rails' top-slot centrelines

# --- Slat -----------------------------------------------------------------

SLAT_PITCH = 18.0      # mm, 6 belt teeth -- rev D; divides the 828mm belt into 46 slats
SLAT_LENGTH = 80.0     # mm, across the machine, local z
SLAT_WIDTH = 17.0      # mm, along local x -- PROVISIONAL, was 16 (rev D); a 1mm inter-slat gap so thin parts cannot wedge edge-on. Set from the printed width at calibration step 3
SLAT_THICKNESS = 3.0   # mm, local y
CLEAT_EVERY = 2        # every second slat is cleated -- rev D; 46 isn't divisible by 3
CLEAT_HEIGHT = 12.0    # mm, above the slat top face
CLEAT_WIDTH_ROOT = 10.0    # mm, along local x, at the slat surface
CLEAT_WIDTH_TIP = 4.0      # mm, along local x, at the top -- drafted for printing
CLEAT_LENGTH = 74.0        # mm, along local z, centred
CLEAT_ROOT_FILLET = 1.0    # mm, both sides

SLAT_COUNT = BELT_LOOP_LENGTH / SLAT_PITCH   # count, 46
assert SLAT_COUNT == int(SLAT_COUNT), "BELT_LOOP_LENGTH must be an integer multiple of SLAT_PITCH"
SLAT_COUNT = int(SLAT_COUNT)
assert SLAT_COUNT % CLEAT_EVERY == 0, "cleat pattern must repeat cleanly across the belt seam"

# --- Saddle -----------------------------------------------------------------
# Tab z-positions derive from BELT_WIDTH and SADDLE_INTERFERENCE alone (no
# separate clearance parameter -- see parts/slat.py _saddle_pair()).

SADDLE_TAB_THICKNESS = 2.5    # mm, along local z
SADDLE_TAB_DEPTH = 3.6        # mm, into negative local y -- PROVISIONAL, drivetrain-spec §6.2, was 6.0; = belt 2.4 + 0.2 gap + lip 1.0
SADDLE_TAB_LENGTH = 7.0       # mm, along local x, centred -- rev D, was 12; must grip <= 2.5 teeth (7.5mm at 3mm pitch)
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
PRINT_ROT_SHAFT_SET = (0.0, 0.0, 0.0)   # deg, axis vertical, either end down -- native orientation
PRINT_ROT_COUPON = (0.0, 0.0, 0.0)      # deg, both coupons, axis vertical, flat on the bed -- native orientation
EDGE_CHAMFER = 0.5    # mm, general outer edges

# --- Tolerances -----------------------------------------------------------
# Not physical dimensions -- used only for float-safe geometric comparisons
# (e.g. selecting edges by position) in part code.

EDGE_MATCH_TOLERANCE = 1e-6   # mm
