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

# --- Tilt: hinge, cross-member, clevis, prop -- spec-tilt.md ---------------
# INCLINE above stays the default; the conveyor rotates about the machine
# origin and the base moves in machine coordinates (spec-tilt §2.1).

TILT_MIN = 25.0                   # deg -- PROVISIONAL
TILT_MAX = 55.0                   # deg -- PROVISIONAL
TILT_CHECK_ANGLES = (25.0, 40.0, 55.0)   # deg, the inclines every tilt check samples
assert TILT_MIN <= INCLINE <= TILT_MAX and TILT_CHECK_ANGLES[0] == TILT_MIN and TILT_CHECK_ANGLES[-1] == TILT_MAX

RAIL_CENTRE_OFFSET = -(SHAFT_HEIGHT_ABOVE_PLATE + PLATE_THICKNESS + FRAME_PROFILE / 2)   # mm, -67.0, rail centreline from the shaft axis
RAIL_UNDERSIDE_OFFSET = RAIL_CENTRE_OFFSET - FRAME_PROFILE / 2                          # mm, -77.0

# Bought hardware, catalogue sizes.
M8_PITCH = 1.25                   # mm
M8_DIA = 8.0                      # mm, bolt shank and threaded rod
M8_HEX_AF = 13.0                  # mm, bolt head and nut, across flats
M8_HEAD_THK = 5.3                 # mm, hex bolt head
M8_NUT_THK = 6.5                  # mm, plain hex nut
M8_NYLOCK_THK = 8.0               # mm
M8_WASHER_OD = 16.0               # mm
M8_WASHER_THK = 1.6               # mm
M8_PIN_BOLT_LEN = 45.0            # mm, all four pivot bolts
M5_CLEARANCE_DIA = 5.5            # mm
M5_CBORE_DIA = 9.0                # mm, socket head 8.5
M5_CBORE_DEPTH = 5.0              # mm
HEX_POCKET_CLEAR = 0.3            # mm, added to the across-flats of every printed hex pocket
NUT_POCKET_DEPTH = 6.8            # mm, captured M8 nut, prop body and knob
BASE_FIXING_HOLE = 5.0            # mm, through-holes in every base-side foot; fastener OPEN

# Hinge -- spec-tilt §2.2, §3
HINGE_T = -50.0                   # mm -- PROVISIONAL, 10 in from the frame's tail end; fixed to the frame, not the take-up
HINGE_OFFSET = RAIL_CENTRE_OFFSET   # mm, -67.0
HINGE_HEIGHT = 20.0               # mm -- PROVISIONAL, hinge axis above the base top face
HINGE_BRKT_T0 = FRAME_T_START     # mm, -60.0 -- PROVISIONAL, bracket plate along the run
HINGE_BRKT_T1 = -20.0             # mm -- PROVISIONAL
HINGE_BRKT_THK = 10.0             # mm -- PROVISIONAL, outboard of the rail face
HINGE_BOSS_R = 12.0               # mm -- PROVISIONAL, 2.0 proud of the rail top, bottom and tail end
HINGE_PIN_HOLE = 8.0              # mm -- PROVISIONAL, the bolt is fixed in the bracket
HINGE_HEAD_POCKET_DEPTH = 5.5     # mm -- PROVISIONAL, hex pocket open to the rail face
HINGE_BRKT_BOLT_T = (-35.0, -25.0)   # mm -- PROVISIONAL, 2 x M5 into the rail's outer slot
HINGE_GAP = 1.0                   # mm -- PROVISIONAL, bracket to block
HINGE_BLOCK_THK = 20.0            # mm -- PROVISIONAL, across the machine
HINGE_BLOCK_WIDTH = 30.0          # mm -- PROVISIONAL, upright along x; its top is a half-round of this diameter on the axis
HINGE_BUSH_HOLE = 8.4             # mm -- PROVISIONAL, running fit on the M8 bolt
HINGE_BLOCK_MIN_WALL = 8.0        # mm, least material above the bushing
HINGE_FOOT_LEN = 60.0             # mm -- PROVISIONAL, flange along x
HINGE_FOOT_WIDTH = 20.0           # mm -- PROVISIONAL, flange across, outboard of the upright
HINGE_FOOT_THK = 5.0              # mm -- PROVISIONAL
HINGE_FOOT_HOLE_X = (-22.5, -7.5, 7.5, 22.5)   # mm -- PROVISIONAL, one row down the flange centreline
assert HINGE_BOSS_R < HINGE_HEIGHT, "hinge boss would touch the base"
assert HINGE_BLOCK_WIDTH / 2 - HINGE_BUSH_HOLE / 2 >= HINGE_BLOCK_MIN_WALL, "too little hinge block above the bushing"

# Cross-member and frame clevis -- spec-tilt §4
XMEMBER_LEN = FRAME_INNER_WIDTH   # mm, 234.0, between the rails' inner faces
XMEMBER_T = 221.0                 # mm -- PROVISIONAL, centre, in the gap between the plates at 177 and 265.5
XMEMBER_PLATE_CLEAR = 5.0         # mm, minimum along the run to either plate footprint
PROP_PIN_A_T = XMEMBER_T          # mm -- PROVISIONAL
CLEVIS_PIN_DROP = 10.0            # mm -- PROVISIONAL, pin A below the rail underside
PROP_PIN_A_OFFSET = RAIL_UNDERSIDE_OFFSET - CLEVIS_PIN_DROP   # mm, -87.0
PROP_EYE_W = 12.0                 # mm -- PROVISIONAL, body and foot eye width, along the pin
CLEVIS_SIDE_CLEAR = 0.3           # mm, each side of an eye, frame clevis and base pin block
CLEVIS_GAP = PROP_EYE_W + 2 * CLEVIS_SIDE_CLEAR   # mm, 12.6
CLEVIS_CHEEK_THK = 6.0            # mm -- PROVISIONAL
CLEVIS_PIN_HOLE = 8.2             # mm -- PROVISIONAL
CLEVIS_PIN_WALL = 7.0             # mm -- PROVISIONAL, material below pin A
CLEVIS_CHEEK_R = CLEVIS_PIN_HOLE / 2 + CLEVIS_PIN_WALL   # mm, 11.1, cheek nose radius about pin A
CLEVIS_BASE_THK = 5.0             # mm -- PROVISIONAL, flange against the cross-member
CLEVIS_WINDOW_X = M8_WASHER_OD / 2 + 2.0   # mm, 10.0, the flange is open tailward of this -- README "Frame clevis"
CLEVIS_HEAD_X = 16.0              # mm -- PROVISIONAL, head-side end of the flange and of the wall joining the cheeks
CLEVIS_WINDOW_Z = 35.0            # mm -- PROVISIONAL, the pin A bolt, washer and nut live inside this
CLEVIS_BOLT_Z = 42.0              # mm -- PROVISIONAL, 2 x M5, +/-; spec-tilt has 15.0 -- README "Frame clevis"
CLEVIS_WIDTH = 100.0              # mm -- PROVISIONAL, across the machine
assert CLEVIS_WINDOW_Z > M8_PIN_BOLT_LEN - (CLEVIS_GAP / 2 + CLEVIS_CHEEK_THK), "pin A bolt end outside its window"
assert CLEVIS_BOLT_Z - M5_CBORE_DIA / 2 > CLEVIS_WINDOW_Z, "clevis fixing bolt breaks into the pin A window"

# Prop -- spec-tilt §5
PROP_PIN_B_X = 125.0              # mm -- PROVISIONAL, horizontal from the hinge axis
PROP_PIN_B_Y = 15.0               # mm -- PROVISIONAL, above the base
PROP_BODY_LEN = 90.0              # mm -- PROVISIONAL, pin A to the body's bottom face
PROP_BODY_DIA = 18.0              # mm -- PROVISIONAL
PROP_EYE_HOLE = 8.4               # mm -- PROVISIONAL, body and foot
PROP_EYE_LEN = 12.0               # mm -- PROVISIONAL, pin A to where the flat eye becomes the round body
PROP_NUT_TOP = 8.0                # mm -- PROVISIONAL, captured nut's top face above the body bottom
PROP_ROD_BORE = 9.0               # mm -- PROVISIONAL
PROP_ROD_BORE_STOP = 12.0         # mm -- PROVISIONAL, the bore ends this far below pin A
PROP_ROD_ENGAGE_MIN = 2.0         # mm, rod tip above the captured nut at full length
FOOT_LEN = 28.0                   # mm -- PROVISIONAL, pin B to the foot's top face
FOOT_DIA = 24.0                   # mm -- PROVISIONAL, round the pocket
FOOT_POCKET_DIA = 16.0            # mm -- PROVISIONAL, the two jammed nuts turn freely in it
FOOT_POCKET_LEN = 15.0            # mm -- PROVISIONAL
FOOT_POCKET_PLAY = 0.3            # mm, jammed nuts to the underside of the top wall
FOOT_WALL_THK = 5.0               # mm -- PROVISIONAL, takes the prop's thrust
FOOT_WALL_HOLE = 8.6              # mm -- PROVISIONAL, also the knob's rod hole
FOOT_WINDOW_W = 14.0              # mm -- PROVISIONAL, side window to fit and jam the nuts -- README "Prop foot"
ROD_BOTTOM_Z = 10.0               # mm -- PROVISIONAL, rod end above pin B
ROD_LEN = 136.0                   # mm -- PROVISIONAL, mid-window of the length budget below
KNOB_DIA = 40.0                   # mm -- PROVISIONAL
KNOB_THK = 12.0                   # mm -- PROVISIONAL
KNOB_LOBES = 8                    # count -- PROVISIONAL
KNOB_SCALLOP_R = 5.0              # mm -- PROVISIONAL, finger scallops centred on the rim
STACK_CLEARANCE = 3.0             # mm, jam nut to lock nut at minimum length
FOOT_STACK = M8_WASHER_THK + KNOB_THK + M8_NUT_THK + STACK_CLEARANCE + M8_NUT_THK   # mm, derived, 29.6
PIN_BLOCK_GAP = CLEVIS_GAP        # mm, 12.6
PIN_BLOCK_CHEEK_THK = 6.0         # mm -- PROVISIONAL
PIN_BLOCK_PIN_HOLE = 8.2          # mm -- PROVISIONAL
PIN_BLOCK_CHEEK_R = 7.0           # mm -- PROVISIONAL, nose radius above pin B; the foot widens just past it
PIN_BLOCK_LEN = 70.0              # mm -- PROVISIONAL, foot plate along x
PIN_BLOCK_WIDTH = 50.0            # mm -- PROVISIONAL, across
PIN_BLOCK_THK = 5.0               # mm -- PROVISIONAL
PIN_BLOCK_HOLE_X = 27.0           # mm -- PROVISIONAL, +/-, 4 base fixing holes
PIN_BLOCK_HOLE_Z = 18.0           # mm -- PROVISIONAL, +/-
assert FOOT_LEN - FOOT_WALL_THK - FOOT_POCKET_LEN > PIN_BLOCK_CHEEK_R, "foot widens inside the pin block's cheeks"
assert FOOT_POCKET_LEN >= 2 * M8_NUT_THK + FOOT_POCKET_PLAY, "foot pocket too short for two jammed nuts"


def prop_length_at(incline: float, pin_b_x: float = PROP_PIN_B_X) -> float:
    """Pin A to pin B at `incline`, closed form, for the budget below.
    geometry.prop_length() is the same distance built from at() and
    base_frame(), and the tests hold the two together."""
    theta = math.radians(incline)
    dt, do = PROP_PIN_A_T - HINGE_T, PROP_PIN_A_OFFSET - HINGE_OFFSET
    ax = dt * math.cos(theta) - do * math.sin(theta)
    ay = dt * math.sin(theta) + do * math.cos(theta)
    return math.hypot(ax - pin_b_x, ay - (PROP_PIN_B_Y - HINGE_HEIGHT))


def prop_budget(rod_len: float = ROD_LEN) -> tuple[float, float, float]:
    """Margins, mm, of the three conditions that make the prop buildable
    (spec-tilt §5.3); each must be >= 0. In order: rod still engaged in the
    captured nut at full length, rod tip clear of pin A at minimum length,
    and the stack on the foot clear of the body at minimum length."""
    l_min, l_max = prop_length_at(TILT_MIN), prop_length_at(TILT_MAX)
    rod_tip = ROD_BOTTOM_Z + rod_len
    return (
        rod_tip - (l_max - PROP_BODY_LEN + PROP_NUT_TOP + PROP_ROD_ENGAGE_MIN),
        (l_min - PROP_ROD_BORE_STOP) - rod_tip,
        (l_min - PROP_BODY_LEN) - (FOOT_LEN + FOOT_STACK),
    )


assert prop_budget()[0] >= 0, "rod leaves the captured nut at TILT_MAX"
assert prop_budget()[1] >= 0, "rod reaches pin A at TILT_MIN"
assert prop_budget()[2] >= 0, "the stack on the foot does not fit under the body at TILT_MIN"

# Loads -- spec-tilt §5.4, informational
TILT_WEIGHT_N = 34.0              # N -- PROVISIONAL, an estimate until weighed
TILT_CG_T = 220.0                 # mm -- PROVISIONAL
TILT_CG_OFFSET = -40.0            # mm -- PROVISIONAL
PROP_FORCE_MAX = 250.0            # N, ceiling for the prop and its printed pivots; was spec-tilt's 150, which its own doubled-weight guard could not meet -- README "Prop force at doubled weight"

# Base -- OPEN; a reference slab whose top face is the base plane (spec-tilt §6)
BASE_REF_THK = 20.0               # mm
BASE_REF_BEHIND = 120.0           # mm, behind the hinge axis
BASE_REF_AHEAD = 600.0            # mm, ahead of it
BASE_REF_HALF_WIDTH = 200.0       # mm
BASE_CLEARANCE_MIN = 4.0          # mm, everything that tilts, to the base
TAIL_SHAFT_HEIGHT_RANGE = (94.0, 108.0)   # mm, tail shaft axis above the base over all angles and take-ups
XMEMBER_RETURN_CLEAR = 15.0       # mm, cross-member top face below the returning cleat tips
PROP_UNDERSIDE_CLEAR = 3.0        # mm, prop body to the rail underside plane, outside the clevis
SETUP_TABLE_STEP = 2.5            # deg, the setting-up table's rows

# Bought hardware for the tilt, (item, quantity, use) -- spec-tilt §7
TILT_HARDWARE = (
    (f"M8 x {M8_PIN_BOLT_LEN:g} hex bolt", 2, "hinge pins (head in the bracket pocket)"),
    (f"M8 x {M8_PIN_BOLT_LEN:g} hex bolt", 2, "pins A and B"),
    ("M8 nylock nut", 4, "one per pin"),
    ("M8 washer", 5, "hinge x 2, pins A and B x 2, under the knob x 1"),
    (f"M8 threaded rod, {ROD_LEN:g} long", 1, "prop adjuster (cut from stock)"),
    ("M8 hex nut", 6, "body (captured), lock, knob (captured), knob jam, two jammed in the foot pocket"),
    ("M5 x 12 + T-nut", 6, "hinge brackets x 4, clevis x 2"),
    ("2020 corner bracket + M5 x 10 + T-nut", 4, "cross-member"),
    (f"2020, {XMEMBER_LEN:g} long", 1, "cross-member"),
    ("Base fasteners", 12, "OPEN; depends on the base"),
)

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
PRINT_ROT_HINGE_BRACKET = {1: (0.0, 0.0, 0.0), -1: (180.0, 0.0, 0.0)}   # deg, by side: rail face down -- native for +z, turned over for its mirror
PRINT_ROT_HINGE_BLOCK = (90.0, 0.0, 0.0)     # deg, foot down: local +y (up) to the bed's +z
PRINT_ROT_PIN_BLOCK = (90.0, 0.0, 0.0)       # deg, plate down
PRINT_ROT_CLEVIS = (-90.0, 0.0, 0.0)         # deg, cross-member face down: the body hangs into local -y
PRINT_ROT_PROP_BODY = (180.0, 0.0, 0.0)      # deg, bottom face down, eye up; the nut pocket bridges
PRINT_ROT_PROP_FOOT = (0.0, 0.0, 0.0)        # deg, top wall up -- native orientation
PRINT_ROT_KNOB = (0.0, 0.0, 0.0)             # deg, flat face down -- native orientation
EDGE_CHAMFER = 0.5    # mm, general outer edges

# --- Tolerances -----------------------------------------------------------
# Not physical dimensions -- used only for float-safe geometric comparisons
# (e.g. selecting edges by position) in part code.

EDGE_MATCH_TOLERANCE = 1e-6   # mm
