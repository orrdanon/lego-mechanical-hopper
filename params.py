"""Single source of truth for every dimension in this project.

No numeric dimension may appear anywhere else in the codebase. Every part,
geometry function, and check must import its numbers from here. If a value
needed elsewhere is missing, add it to this file rather than hard-coding it
at the call site.

Units are millimetres and degrees everywhere.

Implements docs/specs/phase1-cad-spec.md through -revD.md, the parameter
tables of phase3-cad-spec-revB.md renumbered for the rev D belt, the
frame/bridge-plate subset of phase2-cad-spec.md needed by phase4-cad-spec.md,
docs/specs/drivetrain-spec.md rev B §3, which supersedes phase 3's pulley,
spec-tilt.md, spec-pillow-blocks.md §2, whose printed pillow block
fixes `SHAFT_HEIGHT_ABOVE_PLATE`, spec-drive.md, and hopper-spec-v1.md §3.
The belt is the HTD-3M x 15mm x 828mm loop chosen
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
SHAFT_HEIGHT_ABOVE_PLATE = 48.0   # mm, fixed by the printed pillow block, which is its own standoff (spec-pillow-blocks §2.2)
SHAFT_SPEED = 30.0     # rpm, gives 60 mm/s belt speed

# --- Bearings, pillow blocks, spacers -- spec-pillow-blocks.md §2 -----------
# The spec's SHAFT_HEIGHT is SHAFT_HEIGHT_ABOVE_PLATE and its BEARING_Z is
# half BEARING_SPACING; both existed already. Pillow-block z is local: 0 at
# the bearing centre plane, +z outboard.

BEARING_BORE = 8.0                # mm, 608ZZ, catalogue
BEARING_OD = 22.0                 # mm, catalogue
BEARING_WIDTH = 7.0               # mm, catalogue
BEARING_INNER_RACE_OD = 12.1      # mm, catalogue, the inner ring's face; clearance assertions only
BEARING_EDGE_CHAMFER = 0.3        # mm, catalogue, reference solid only
BEARING_Z = BEARING_SPACING / 2   # mm, 50.0, bearing centres at machine z = +/-50

PB_POCKET_DIA = 22.4              # mm -- PROVISIONAL, pocket wall between the ribs
PB_POCKET_DEPTH = BEARING_WIDTH   # mm, derived, the bearing ends flush with the inboard face
PB_RIB_COUNT = 6                  # count
PB_RIB_ANGLE_0 = 90.0             # deg, first rib on local +y, the rest at 360/PB_RIB_COUNT steps
PB_RIB_TIP_DIA = 21.8             # mm -- PROVISIONAL, the one fit parameter, set by the bearing coupon
PB_RIB_BASE_WIDTH = 2.0           # mm -- PROVISIONAL, where the rib meets the pocket wall
PB_RIB_TIP_WIDTH = 0.8            # mm -- PROVISIONAL, flat at the rib tip
PB_RIB_LEAD_IN = 1.0              # mm, each rib ramps from the wall to full height over this, from the mouth
PB_POCKET_MOUTH_CHAMFER = 0.5     # mm, 45 deg, pocket edge on the inboard face
PB_LIP_THICKNESS = 1.5            # mm -- PROVISIONAL
PB_LIP_HOLE_DIA = 16.0            # mm -- PROVISIONAL, the lip bears on the outer ring only
PB_BOSS_RADIUS = 15.0             # mm -- PROVISIONAL, 3.8 of wall outside the pocket
PB_TOWER_WIDTH = 2 * PB_BOSS_RADIUS                       # mm, derived, 30.0, along the run
PB_INBOARD_FACE_Z = -BEARING_WIDTH / 2                    # mm, derived, -3.5
PB_OUTBOARD_FACE_Z = BEARING_WIDTH / 2 + PB_LIP_THICKNESS   # mm, derived, 5.0
PB_FOOT_LENGTH = 44.0             # mm -- PROVISIONAL, along the run
PB_FOOT_HEIGHT = 7.0              # mm -- PROVISIONAL, limited by the returning-run clearance
PB_FOOT_INBOARD_Z = -16.0         # mm -- PROVISIONAL, machine z = +/-34
PB_FILLET = 3.0                   # mm -- PROVISIONAL, tower-to-foot concave edges
PB_INSERT_DIA = PULLEY_INSERT_DIA   # mm, 5.6, the same M4 heat-set insert as the shaft set
PB_INSERT_POCKET_DEPTH = 6.5      # mm -- PROVISIONAL, blind from the underside, 0.5 skin
PB_BOLT_X = 14.0                  # mm -- PROVISIONAL, +/-, along the run
PB_BOLT_Z = -9.75                 # mm -- PROVISIONAL, local, inboard of the tower; machine z = +/-40.25
PB_SLAT_CLEAR_MIN = 5.0           # mm, every slat to a block or spacer, and the foot top to the returning cleat tips

assert PB_RIB_TIP_DIA < BEARING_OD < PB_POCKET_DIA, "ribs must interfere and the pocket wall clear"
assert PB_LIP_HOLE_DIA / 2 - BEARING_INNER_RACE_OD / 2 >= 1.5, "lip would touch the inner ring"
assert PB_LIP_HOLE_DIA < BEARING_OD - 2.0, "less than 1.0 of lip ledge per side"
assert PB_BOSS_RADIUS <= SHAFT_HEIGHT_ABOVE_PLATE - PB_FOOT_HEIGHT, "boss dips into the foot"
assert abs(PB_BOLT_Z) + PB_INSERT_DIA / 2 + 1.5 <= abs(PB_FOOT_INBOARD_Z), "insert pocket breaks out of the foot's inboard end"
assert PB_BOLT_X + PB_INSERT_DIA / 2 + 1.5 <= PB_FOOT_LENGTH / 2, "insert pocket breaks out of the foot's ends"

SPACER_BORE = 8.3                 # mm -- PROVISIONAL, slides on the round part of the shaft
SPACER_OD = 11.0                  # mm -- PROVISIONAL, lands on the inner ring only
SHAFT_END_PLAY = 0.4              # mm -- PROVISIONAL, total, per shaft
SPACER_CHAMFER = 0.3              # mm, all four circular edges

BC_RIB_TIP_DIAS = (21.6, 21.7, 21.8, 21.9, 22.0)   # mm -- PROVISIONAL, one pocket each, tightest first
BC_POCKET_PITCH = 30.0            # mm -- PROVISIONAL
BC_LENGTH = len(BC_RIB_TIP_DIAS) * BC_POCKET_PITCH   # mm, derived, 150.0
BC_WIDTH = 40.0                   # mm -- PROVISIONAL, 30 for the pockets + 10 label strip
BC_POCKET_EDGE = 15.0             # mm, pocket centres in from one long edge
BC_THICKNESS = BEARING_WIDTH + PB_LIP_THICKNESS   # mm, derived, 8.5, the block's section
BC_TEXT_SIZE = 5.0                # mm -- PROVISIONAL
BC_TEXT_DEPTH = 0.6               # mm -- PROVISIONAL, engraved on the top face
assert PB_RIB_TIP_DIA in BC_RIB_TIP_DIAS, "the coupon must include the block's own fit"

PLATE_PB_HOLE_DIA = 5.0           # mm -- PROVISIONAL, M4 clearance plus +/-0.5 of alignment float, end plates only

# Bought hardware for the pillow blocks, (item, quantity, use) -- spec-pillow-blocks §1
PILLOW_BLOCK_HARDWARE = (
    ("608ZZ bearing", 6, "4 fitted, 2 spare for the coupon test (B1)"),
    ("M4 heat-set insert", 8, "2 per block, the shaft set's type"),
    ("M4 x 16 socket-head screw", 8, "up through the end plates"),
    ("M4 flat washer", 8, "under the screw heads"),
    ("M12 flat washer", 1, "pressing tool: on the outer ring in the vise"),
)

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

# The pillow block's foot on its end plate, 0.5 to spare at each end, and
# the spacer's length from the shaft set it butts against.
assert PB_FOOT_LENGTH <= PLATE_WIDTH - 1.0, "pillow block foot overhangs its plate"
SPACER_LENGTH = (BEARING_Z - BEARING_WIDTH / 2) - SHAFTSET_LENGTH / 2 - SHAFT_END_PLAY / 2   # mm, derived, 16.8
assert SPACER_OD <= BEARING_INNER_RACE_OD - 1.0, "spacer would touch the shield or outer ring"
assert SPACER_OD / 2 >= (PULLEY_BORE + PULLEY_BORE_CLEARANCE) / 2 + PULLEY_BORE_CHAMFER + 0.8, "spacer lands on the shaft set's bore chamfer"
assert SHAFTSET_LENGTH / 2 + SHAFT_END_PLAY / 2 > SHAFT_FLAT_LENGTH / 2, "spacer rides on the shaft flat"

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
PROP_PIN_B_X = 140.0              # mm -- PROVISIONAL, horizontal from the hinge axis; was 125, moved for the prop force with the hopper -- README "Pin B at 140"
PROP_PIN_B_Y = 15.0               # mm -- PROVISIONAL, above the base
PROP_BODY_LEN = 92.0              # mm -- PROVISIONAL, pin A to the body's bottom face; was 90, widens the rod window at pin B 140
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
ROD_LEN = 128.0                   # mm -- PROVISIONAL, mid-window of the length budget below (125.9 .. 130.6)
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

# --- Drive: stepper, coupler, motor bracket -- spec-drive.md ------------------
# The head shaft is driven directly. Everything is built for DRIVE_SIDE = +1
# and mirrored; z below is machine z on the drive side, from the centre plane.

DRIVE_SIDE = 1                    # +1 (+z) or -1 (-z) -- OPEN, spec-drive §10.1

# Load and motor sizing -- §2
GRAVITY = 9.81                    # m/s^2
DRIVE_PULL_EST_N = 8.0            # N -- PROVISIONAL, 300 g of LEGO at 55 deg 2.4 + hopper drag ~4 + friction ~1.5
DRIVE_TORQUE_EST = DRIVE_PULL_EST_N * PULLEY_PD / 2 / 1000   # N m, derived, 0.153
MOTOR_RATED_CURRENT_A = 1.7       # A, catalogue
MOTOR_HOLD_TORQUE = 0.449         # N m at the rated current, catalogue (4.58 kg cm)
MOTOR_STEPS_PER_REV = 200         # count, 1.8 deg
DRIVE_CURRENT_A = 1.2             # A -- PROVISIONAL, driver current limit, test D3
DRIVE_MICROSTEPS = 16             # count, A4988 -- PROVISIONAL
DRIVE_RUN_FACTOR = 0.8            # running torque at 30 rpm over holding -- PROVISIONAL
DRIVE_TORQUE_AVAIL = DRIVE_RUN_FACTOR * MOTOR_HOLD_TORQUE * DRIVE_CURRENT_A / MOTOR_RATED_CURRENT_A   # N m, derived, 0.254
DRIVE_SKIP_PULL_N = DRIVE_TORQUE_AVAIL / (PULLEY_PD / 2 / 1000)   # N, derived, 13.3, belt pull at which the motor skips
DRIVE_STEP_RATE = SHAFT_SPEED * MOTOR_STEPS_PER_REV * DRIVE_MICROSTEPS / 60   # Hz, derived, 1600
DRIVE_TORQUE_MARGIN_MIN = 1.5     # available over estimated torque

# Motor, Waveshare NEMA 17 42.3 x 40 -- §3.1. Local origin at the centre of
# the mounting face, +z along the shaft.
MOTOR_SQUARE = 42.3               # mm, catalogue
MOTOR_BODY_LEN = 40.0             # mm, catalogue
MOTOR_PILOT_DIA = 22.0            # mm -- PROVISIONAL, NEMA 17 standard, the listing is silent
MOTOR_PILOT_H = 2.0               # mm -- PROVISIONAL
MOTOR_HOLE_SPACING = 31.0         # mm -- PROVISIONAL, 4 x M3 on this square
MOTOR_HOLE_M = 3.0                # mm, M3
MOTOR_SCREW_MAX_ENGAGE = 3.0      # mm, catalogue: longer screws can damage the motor
MOTOR_SHAFT_DIA = 5.0             # mm, catalogue, a D-shaft; the flat is not modelled
MOTOR_SHAFT_LEN = 23.5            # mm, catalogue, from the mounting face -- datum to be measured (D1)
MOTOR_MASS_KG = 0.30              # kg, the store's shipping weight, an upper bound

# Coupler, flexible 5 x 8 -- §3.2. Local origin on the axis at the 8-bore end.
COUPLER_DIA = 20.0                # mm, catalogue
COUPLER_LEN = 25.0                # mm, catalogue
COUPLER_BORE_BIG = SHAFT_DIA      # mm, 8.0, catalogue, the head shaft's end
COUPLER_BORE_SMALL = MOTOR_SHAFT_DIA   # mm, 5.0, catalogue, the motor's end
COUPLER_RATED_TORQUE = 0.6        # N m, catalogue (max 1.2)
COUPLER_ENGAGE = 10.0             # mm -- PROVISIONAL, target, per shaft
COUPLER_ENGAGE_MAX = 11.0         # mm -- PROVISIONAL, bore depths to be measured (D1)
COUPLER_BORE_DEPTH = COUPLER_ENGAGE_MAX   # mm, each bore, reference solid only
COUPLER_TIP_GAP_MIN = 2.0         # mm -- PROVISIONAL, between the shaft tips inside it
COUPLER_MASS_KG = 0.02            # kg

# Axial stack -- §4, §5. The spec's PILLOW_BLOCK_HALF_W (14.0, for a bought
# insert block) is the printed block's lip face -- README "Drive resolutions".
PILLOW_BLOCK_HALF_W = PB_OUTBOARD_FACE_Z   # mm, 5.0, bearing centre to the block's outboard face
COUPLER_BLOCK_GAP = 2.0           # mm -- PROVISIONAL, block face to coupler
HEAD_SHAFT_DRIVE_EXT_MIN = PILLOW_BLOCK_HALF_W + COUPLER_BLOCK_GAP + COUPLER_ENGAGE   # mm, 17.0, past the bearing centre
HEAD_SHAFT_LEN = float(math.ceil(SHAFT_LENGTH / 2 + BEARING_Z + HEAD_SHAFT_DRIVE_EXT_MIN))   # mm, 140.0, cut to whole mm
HEAD_SHAFT_DRIVE_EXT = HEAD_SHAFT_LEN - SHAFT_LENGTH / 2 - BEARING_Z   # mm, 17.5 as cut; the non-drive end stays SHAFT_LENGTH/2
COUPLER_Z = BEARING_Z + PILLOW_BLOCK_HALF_W + COUPLER_BLOCK_GAP   # mm, 57.0, the coupler's 8-bore end
HEAD_SHAFT_ENGAGE = BEARING_Z + HEAD_SHAFT_DRIVE_EXT - COUPLER_Z   # mm, 10.5
MOTOR_FACE_Z = COUPLER_Z + COUPLER_LEN - COUPLER_ENGAGE + MOTOR_SHAFT_LEN   # mm, 95.5, the motor's mounting face
COUPLER_TIP_GAP = (MOTOR_FACE_Z - MOTOR_SHAFT_LEN) - (BEARING_Z + HEAD_SHAFT_DRIVE_EXT)   # mm, 4.5

# Motor bracket, printed -- §6. Local origin on the foot's underside at the
# head shaft station, at the face plate's inboard face; +z outboard.
FACE_PLATE_T = 5.0                # mm -- PROVISIONAL
FACE_PLATE_Z = MOTOR_FACE_Z - FACE_PLATE_T   # mm, 90.5, machine z of the face plate's inboard face
FACE_PLATE_ABOVE_AXIS = 24.0      # mm, the face plate's top above the shaft axis
BRACKET_W = PLATE_WIDTH           # mm, 45.0, along the run, centred on the head shaft
BRACKET_FOOT_T = 6.0              # mm -- PROVISIONAL
BRACKET_FOOT_INBOARD = 19.5       # mm -- PROVISIONAL, the foot's reach inboard of the face plate
BRACKET_FOOT_OUTBOARD = FRAME_WIDTH / 2 - FACE_PLATE_Z   # mm, 46.5, to the plate edge
BRACKET_PILOT_BORE = 22.4         # mm -- PROVISIONAL, 0.4 clearance, tuned on the first print (D2)
MOTOR_HOLE_DIA = 3.4              # mm, M3 clearance
BRACKET_SLOT_W = M5_CLEARANCE_DIA   # mm, 5.5
BRACKET_SLOT_TRAVEL = 1.5         # mm -- PROVISIONAL, +/-, along the run, to line the motor up with the shaft
BRACKET_FILLET = 5.0              # mm -- PROVISIONAL, foot to face plate, both sides
BRACKET_TIE_SLOT = (4.0, 2.0)     # mm -- PROVISIONAL, cable-tie slot through the foot, along the run x across
BRACKET_TIE_SLOT_INSET = 3.0      # mm -- PROVISIONAL, its centre in from the foot's outboard end
BRACKET_MASS_KG = 0.04            # kg, PETG
M5_HEAD_H = 5.0                   # mm, socket head, catalogue
MOTOR_HEAD_CLEAR = 5.0            # mm, motor body above the M5 heads it sits over
MOTOR_SCREW_LEN = 8.0             # mm, M3 x 8, motor to bracket
BRACKET_M5_LEN = 20.0             # mm, M5 x 20, replaces the head plate's two drive-side bolts
M5_TNUT_T = 5.0                   # mm, about, the frame T-nut
COUPLER_CLEAR_BLOCK = 1.5         # mm, coupler to the pillow block (spec-drive §8.11)
COUPLER_CLEAR_BRACKET = 2.0       # mm, coupler to the bracket and the bridge plate
DRIVE_SCREWS_MASS_KG = 0.01       # kg

assert DRIVE_SIDE in (1, -1)
assert DRIVE_TORQUE_AVAIL / DRIVE_TORQUE_EST >= DRIVE_TORQUE_MARGIN_MIN, "motor too weak for the estimated pull"
assert COUPLER_RATED_TORQUE > MOTOR_HOLD_TORQUE, "the coupler must never be the weak link"
assert HEAD_SHAFT_DRIVE_EXT >= HEAD_SHAFT_DRIVE_EXT_MIN, "head shaft too short for the coupler"
assert COUPLER_ENGAGE <= HEAD_SHAFT_ENGAGE <= COUPLER_ENGAGE_MAX, "head shaft engagement in the coupler"
assert COUPLER_TIP_GAP >= COUPLER_TIP_GAP_MIN, "shaft tips meet inside the coupler"
assert MOTOR_SCREW_LEN - FACE_PLATE_T <= MOTOR_SCREW_MAX_ENGAGE, "M3 screws reach too far into the motor"
assert SHAFT_HEIGHT_ABOVE_PLATE - MOTOR_SQUARE / 2 >= BRACKET_FOOT_T + M5_HEAD_H + MOTOR_HEAD_CLEAR, "motor sits on the M5 heads"
assert BRACKET_M5_LEN >= BRACKET_FOOT_T + PLATE_THICKNESS + M5_TNUT_T, "M5 too short to reach through the T-nut"
assert FACE_PLATE_ABOVE_AXIS >= MOTOR_SQUARE / 2, "face plate shorter than the motor"
assert BRACKET_PILOT_BORE > MOTOR_PILOT_DIA, "pilot bore must clear the boss"

# Tilt load -- §7. The drive is a separate term so that weighing the frame
# replaces only TILT_WEIGHT_N. Its CG is on the head shaft axis.
DRIVE_MASS_KG = MOTOR_MASS_KG + COUPLER_MASS_KG + BRACKET_MASS_KG + DRIVE_SCREWS_MASS_KG   # kg, 0.37
DRIVE_WEIGHT_N = DRIVE_MASS_KG * GRAVITY   # N, 3.6
DRIVE_CG_T = CENTRE_DIST          # mm, on the head shaft
DRIVE_CG_OFFSET = 0.0             # mm
TILT_TOTAL_WEIGHT_N = TILT_WEIGHT_N + DRIVE_WEIGHT_N   # N, 37.6
TILT_TOTAL_CG_T = (TILT_WEIGHT_N * TILT_CG_T + DRIVE_WEIGHT_N * DRIVE_CG_T) / TILT_TOTAL_WEIGHT_N   # mm, 232.9
TILT_TOTAL_CG_OFFSET = (TILT_WEIGHT_N * TILT_CG_OFFSET + DRIVE_WEIGHT_N * DRIVE_CG_OFFSET) / TILT_TOTAL_WEIGHT_N   # mm, -36.1

# Bought parts for the drive, (item, quantity, use) -- spec-drive §3, §11
DRIVE_HARDWARE = (
    ("NEMA 17 stepper 42.3 x 40, 1.7 A (4P-748700)", 1, "drives the head shaft"),
    ("Flexible coupler 5 x 8 (4P-6813)", 1, "motor to head shaft"),
    (f"M3 x {MOTOR_SCREW_LEN:g} socket head", 4, "motor to bracket"),
    (f"M5 x {BRACKET_M5_LEN:g} socket head + T-nut", 2, "bracket and head plate to the rail, drive side"),
    ("Pololu A4988 driver (product 1146)", 1, f"{DRIVE_CURRENT_A:g} A limit, 1/{DRIVE_MICROSTEPS} step, 12 V assumed"),
    ("JST 6-pin adapter cable (product 6500)", 1, "motor lead"),
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

# --- Hopper -- hopper-spec-v1.md §3 ----------------------------------------
# Frame-mounted: every part is placed with at(..., incline=incline) and none
# on the tail plate, so the take-up does not move it. The spec gives heights
# as h, above the slat top face; code converts them with
# geometry.hopper_offset(h), never with the 22.947 literal.

# §3.1 Position along the run. The largest tail_shaft_t() is at
# TAIL_TAKEUP_MIN (tail_shaft_t = -takeup); params cannot import geometry.
HOPPER_SEAL_T = 28.0              # mm -- PROVISIONAL, where the seal brush tips touch the slat tops
HOPPER_SEAL_T_MIN = -TAIL_TAKEUP_MIN + SLAT_PITCH + 3.0   # mm, derived, 25.0, a slat pitch past the tail tangent point, plus 3
HOPPER_FRONT_T = 130.0            # mm -- PROVISIONAL, front wall inner face
HOPPER_TAIL_KEEPOUT_T = -TAIL_TAKEUP_MIN + 6.0   # mm, derived, 10.0, no hopper point tailward of this
assert HOPPER_SEAL_T >= HOPPER_SEAL_T_MIN, "the seal would meet slats whose gaps are still open"

# §3.2 Channel, inherited by name from the skirts
HOPPER_CHANNEL_W = 2 * SKIRT_INSET   # mm, derived, 76.0

# §3.3 Walls and rim
LINER_THICKNESS = 3.0             # mm -- PROVISIONAL, printed PETG
FLARE_ANGLE = 45.0                # deg -- PROVISIONAL, liner flare from the run normal, outward
HOPPER_HALF_W = 108.0             # mm -- PROVISIONAL, side-panel inner face, +/-z
FLARE_TOP_H = SKIRT_HEIGHT + (HOPPER_HALF_W - SKIRT_INSET) / math.tan(math.radians(FLARE_ANGLE))   # mm, derived, 98.0
BACK_WALL_ANGLE = 85.0            # deg -- PROVISIONAL, run (headward) to back wall inner face
RIM_FRONT_H = 110.0               # mm -- PROVISIONAL, rim height at the front wall
RIM_LEVEL_INCLINE = INCLINE       # deg -- PROVISIONAL, the rim is horizontal at this incline
PANEL_THICKNESS = 9.0             # mm -- PROVISIONAL, plywood, as the bridge plates
WALL_THICKNESS = 6.0              # mm -- PROVISIONAL, plywood, back and front walls
PANEL_BOTTOM_OFFSET = -45.0       # mm -- PROVISIONAL, an offset, not h: 3.0 above the plate top faces
PANEL_REAR_T_MIN = 34.0           # mm -- PROVISIONAL, panel stays headward of this below the flare top
LINER_FLANGE_H = 12.0             # mm, vertical flange against the panel, from FLARE_TOP_H
LINER_FLANGE_TOP_H = FLARE_TOP_H + LINER_FLANGE_H   # mm, derived, 110.0
LINER_FLANGE_CHAMFER = 2.0        # mm, 45 deg on the flange's top inner edge, so it is no ledge -- README "Liner"
LINER_SCREW_T = (40.0, 85.0, 125.0)   # mm -- PROVISIONAL, 3 x M3 wood screws, flange to panel
LINER_SCREW_H = FLARE_TOP_H + LINER_FLANGE_H / 2   # mm, derived, 104.0
LINER_RIB_T = (50.0, 110.0)       # mm -- PROVISIONAL, two triangular ribs under the flare
LINER_RIB_LEG = 20.0              # mm -- PROVISIONAL, each leg, along the panel and the flare
assert RIM_FRONT_H >= FLARE_TOP_H + 5.0, "rim too close to the flare top"
assert LINER_FLANGE_TOP_H <= RIM_FRONT_H + 1e-9, "liner flange stands above the rim"

# §3.4 Brushes: bought strip brush (nylon door sweep) cut to length
BRUSH_BACKING_W = 6.0             # mm -- PROVISIONAL, measure: backing thickness
BRUSH_BACKING_H = 8.0             # mm -- PROVISIONAL, measure: backing height
BRUSH_FREE_LEN = 25.0             # mm -- PROVISIONAL, measure: bristle length out of the backing
BRUSH_BRISTLE_T = 3.0             # mm -- PROVISIONAL, measure: thickness of the bristle tuft, reference solid only
BRUSH_SIDE_CLEAR = 0.5            # mm, brush end to liner, each side
BRUSH_LEN = HOPPER_CHANNEL_W - 2 * BRUSH_SIDE_CLEAR   # mm, derived, 75.0
BRUSH_SLOT_CLEAR = 0.3            # mm, clamp slot over the backing thickness
SEAL_BRUSH_INTERFERENCE = 2.0     # mm -- PROVISIONAL, undeflected tip below the slat top
SEAL_BRUSH_RAKE = 15.0            # deg -- PROVISIONAL, from the run normal, tips headward of the root
SEAL_ROOT_H = BRUSH_FREE_LEN * math.cos(math.radians(SEAL_BRUSH_RAKE)) - SEAL_BRUSH_INTERFERENCE   # mm, derived, 22.148
SEAL_ROOT_T = HOPPER_SEAL_T - BRUSH_FREE_LEN * math.sin(math.radians(SEAL_BRUSH_RAKE))              # mm, derived, 21.530
METER_GAP = 14.0                  # mm -- PROVISIONAL, metering brush tip above the slat top
METER_GAP_MIN = 6.0               # mm -- PROVISIONAL, clamp slot range
METER_GAP_MAX = 26.0              # mm -- PROVISIONAL
METER_RAKE = 0.0                  # deg -- PROVISIONAL, bristles along the run normal
SEAL_CLEAT_CLEAR = 5.0            # mm, least seal brush root and clamp above the cleat tips (A3)
assert SEAL_ROOT_H >= CLEAT_HEIGHT + SEAL_CLEAT_CLEAR, "seal brush root too close to the cleat tips"
assert METER_GAP_MIN <= METER_GAP <= METER_GAP_MAX

# The two brush clamps sit between the liners, not 10 beyond the channel
# each side as the spec has it -- README "Brush clamps".
HOPPER_CLAMP_LEN = BRUSH_LEN      # mm, derived, 75.0, the brush's own 0.5 to each liner
BACK_NOTCH_H = SEAL_ROOT_H + BRUSH_BACKING_H + 4.0   # mm, derived, 34.148, back wall's bottom edge over the channel
SEAL_CLAMP_LOW_H = SEAL_ROOT_H - 1.0   # mm, derived, 21.148, the clamp's lower face (spec §4.4)
SEAL_CLAMP_FRONT = 8.0            # mm -- PROVISIONAL, headward of the back wall inner face
SEAL_CLAMP_BACK = 9.0             # mm -- PROVISIONAL, tailward of it, below the notch: 3.0 behind the wall
SEAL_CLAMP_LAP = 20.0             # mm -- PROVISIONAL, up the wall's inner face above the notch
SEAL_CLAMP_SCREW_Z = (-25.0, 0.0, 25.0)   # mm -- PROVISIONAL, 3 x M4 through the wall into inserts
SEAL_CLAMP_GRUB_Z = (-20.0, 20.0)  # mm -- PROVISIONAL, 2 x M3 grub screws onto the backing
FRONT_NOTCH_H = METER_GAP_MAX + BRUSH_FREE_LEN + BRUSH_BACKING_H + 4.0   # mm, derived, 63.0
METER_CLAMP_T = 12.0              # mm -- PROVISIONAL, plate thickness along the run, 2.85 each side of the slot
METER_CLAMP_H = 48.0              # mm -- PROVISIONAL, plate height above the brush root
METER_CLAMP_LAP = 10.0            # mm, least lap of the plate over the wall above the notch
METER_BOLT_H = 72.0               # mm -- PROVISIONAL, the two M4 through the front wall, fixed
METER_BOLT_Z = (-20.0, 20.0)      # mm -- PROVISIONAL
METER_GRUB_Z = (-20.0, 20.0)      # mm -- PROVISIONAL, 2 x M3 grub screws onto the backing
assert METER_CLAMP_T >= BRUSH_BACKING_W + BRUSH_SLOT_CLEAR + 3.0, "metering clamp too thin round its slot"
assert METER_GAP_MIN + BRUSH_FREE_LEN + METER_CLAMP_H >= FRONT_NOTCH_H + METER_CLAMP_LAP, "clamp leaves the notch open at its lowest"

# §3.5 Carrying-run support rail and its bridge
RAIL_T0 = 30.0                    # mm -- PROVISIONAL
RAIL_T1 = 140.0                   # mm -- PROVISIONAL, 10 past the front wall
RAIL_BOTTOM_OFFSET = 4.0          # mm -- PROVISIONAL, an offset, not h
RAIL_END_CHAMFER = 45.0           # deg, lead-in at both ends, down to the groove bottom
RAIL_ARM_T_CENTRE = CENTRE_DIST / (PLATE_STATIONS - 1)   # mm, derived, 88.5, plate 1
RAIL_ARM_LEN = 24.0               # mm -- PROVISIONAL, along the run
RAIL_ARM_T = (RAIL_ARM_T_CENTRE - RAIL_ARM_LEN / 2, RAIL_ARM_T_CENTRE + RAIL_ARM_LEN / 2)   # mm, derived, 76.5 .. 100.5
RAIL_ARM_OFFSET = (-12.0, RAIL_BOTTOM_OFFSET)   # mm -- PROVISIONAL, between the runs
RAIL_ARM_HALF_W = 54.0            # mm -- PROVISIONAL
RAIL_POST_Z = (44.0, RAIL_ARM_HALF_W)   # mm -- PROVISIONAL, +/-
RAIL_PAD_Z = 64.0                 # mm -- PROVISIONAL, pads reach outboard of the posts to this
RAIL_PAD_THK = 5.0                # mm -- PROVISIONAL
RAIL_PAD_BOLT_Z = 59.0            # mm -- PROVISIONAL, +/-, 2 x M4 per pad through the plate
RAIL_PAD_BOLT_X = 7.0             # mm -- PROVISIONAL, +/- along the run from the plate centre
RAIL_INSERT_X = 6.0               # mm -- PROVISIONAL, +/- from the arm centre, 2 x M3 into the rail
RAIL_ARM_GRIP = 3.0               # mm, arm left under the counterbored M3 heads

# §3.6 Mounting
HOPPER_FOOT_T = (46.0, 126.0)     # mm -- PROVISIONAL, foot centres
HOPPER_FOOT_LEN = 24.0            # mm -- PROVISIONAL, along the run
HOPPER_FOOT_INNER_Z = HOPPER_HALF_W - 3.0   # mm, derived, 105.0, inner cheek 2.8 thick
HOPPER_FOOT_TOP_OFFSET = -27.0    # mm -- PROVISIONAL
HOPPER_FOOT_SLOT_W = PANEL_THICKNESS + 0.4   # mm, derived, 9.4
HOPPER_FOOT_SLOT_DEPTH = HOPPER_FOOT_TOP_OFFSET - PANEL_BOTTOM_OFFSET   # mm, derived, 18.0, the panel stands on its floor
HOPPER_FOOT_M4_X = 8.5            # mm -- PROVISIONAL, +/- along the run, clear of the M5 counterbore
HOPPER_FOOT_CBORE_FLOOR = 5.0     # mm, foot left under the M5 head
HOPPER_CLEAR = 3.0                # mm, every hopper part to the plates, pillow blocks, hinge, prop and tail
PLATE_BOLT_HEAD = (10.0, 5.0)     # mm, envelope of an M5 head on a plate top: diameter, height

# §4.6 Corner cleats: a 15 x 15 angle, 30 long, joining a panel to a wall.
# The front pair go under the flare -- README "Front wall".
CORNER_CLEAT_LEG = 15.0           # mm -- PROVISIONAL
CORNER_CLEAT_T = 5.0              # mm -- PROVISIONAL, leg thickness
CORNER_CLEAT_LEN = 30.0           # mm -- PROVISIONAL
CORNER_CLEAT_FRONT_H = (10.0, 45.0)    # mm -- PROVISIONAL, bottom ends, front wall joints
CORNER_CLEAT_BACK_H = (118.0, 152.0)   # mm -- PROVISIONAL, bottom ends, back wall joints, above the liner flange

# Hardware sizes
M4_CLEARANCE_DIA = 4.5            # mm
M4_INSERT_DEPTH = 6.0             # mm, the shaft set's M4 insert (PULLEY_INSERT_DIA)
M3_CLEARANCE_DIA = 3.4            # mm
M3_TAP_DIA = 2.5                  # mm, grub screws tap straight into the print
M3_CBORE_DIA = 6.0                # mm
M3_INSERT_DIA = 4.0               # mm
M3_INSERT_DEPTH = 5.0             # mm

# §3.7 Mass and load
PLY_DENSITY = 0.60                # g/cm^3 -- PROVISIONAL, weigh a plate offcut
PETG_DENSITY = 1.27               # g/cm^3, catalogue; infill ignored, which is conservative
BRUSH_MASS = 0.025                # kg -- PROVISIONAL, each, weigh
HOPPER_HARDWARE_MASS = 0.060      # kg -- PROVISIONAL
LOAD_BULK_DENSITY = 0.50          # kg/L -- PROVISIONAL, weigh a level litre of mixed LEGO

# §8 acceptance limits
HOPPER_GAP_CLOSED = 1.05          # mm, most top-face gap between slats under the hopper (A2)
HOPPER_GAP_OPEN = 1.5             # mm, some gap must exceed this with the seal at t = 0 (A2's control)
HOPPER_SLAT_CLEAR = 0.25          # mm, least slat to hopper part (C1)
RAIL_LAND_GAP = (0.45, 0.55)      # mm, slat contact face to the rail lands (C2)
FLARE_SLOPE_MIN = 45.0            # deg (A4)
BACK_WALL_SLOPE_MIN = 35.0        # deg (A4)
RIM_LEVEL_TOL = 0.1               # deg (A5)
HOPPER_CAPACITY = (1.50, 2.60)    # L, least at every check angle, most at INCLINE (B1)
HOPPER_MASS_RANGE = (0.6, 1.0)    # kg (D1)
PROP_FORCE_MIN = 10.0             # N, the prop stays in compression (D3)
PRINT_BED = (220.0, 220.0, 250.0)   # mm -- PROVISIONAL, x, y, z (C11)
HOPPER_TABLE_STEP = 2.5           # deg, the slope, capacity and prop force tables' rows (A4, B1, D2)
HOPPER_CONTROL_RIM_H = 60.0       # mm, a rim too low, for B2's control; below what RIM_FRONT_H may be

# Bought hardware for the hopper, (item, quantity, use) -- hopper-spec §4.8
HOPPER_HARDWARE = (
    (f"Strip brush, cut to {BRUSH_LEN:g}", 2, "seal and metering (nylon door sweep)"),
    ("M5 x 12 + T-nut", 4, "hopper feet into the rails' top slots"),
    ("M4 x 40 + nylock + 2 washers", 8, "feet, through the slot cheeks and the side panel (grip 32)"),
    ("M4 x 25 + nylock + 2 washers", 16, "corner cleats, one per leg (grip 11 on a wall, 14 on a panel)"),
    ("M4 x 25 + nylock + 2 washers", 4, "rail bridge pads, through the plate at 88.5 (grip 14)"),
    ("M4 x 12 + washer", 3, "seal clamp, through the back wall into the inserts; longer comes out of the clamp"),
    ("M4 heat-set insert", 3, "seal clamp"),
    ("M4 x 30 + 2 washers + wing nut", 2, "metering clamp, through the front wall and its slots (grip 18)"),
    ("M3 x 8 socket head", 2, "rail to bridge, from below: 3 of arm, 5 into the insert"),
    ("M3 heat-set insert", 2, "rail"),
    ("M3 x 6 grub screw", 4, "brush backings, two per clamp"),
    ("M3 x 12 wood screw", 6, "liner flanges to the side panels"),
)

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
PRINT_ROT_PILLOW_BLOCK = (180.0, 0.0, 0.0)   # deg, outboard (lip) face down, pocket opening up
PRINT_ROT_SPACER = (0.0, 0.0, 0.0)           # deg, axis vertical, either end down -- native orientation
PRINT_ROT_MOTOR_BRACKET = (90.0, 0.0, 0.0)   # deg, foot down: local +y (up) to the bed's +z; spec-drive's face-plate-down is not a flat face, README "Drive resolutions"
PRINT_ROT_LINER = {1: (180.0, 0.0, 0.0), -1: (0.0, 0.0, 0.0)}   # deg, by side: the flange's outer face down, flare a 45 deg overhang
PRINT_ROT_SEAL_CLAMP = (0.0, 0.0, 0.0)       # deg, on an end, section flat -- README "Brush clamps"
PRINT_ROT_METER_CLAMP = (0.0, 90.0, 0.0)     # deg, mating face down; the brush slot bridges
PRINT_ROT_HOPPER_FOOT = (90.0, 0.0, 0.0)     # deg, bottom face down
PRINT_ROT_CORNER_CLEAT = (90.0, 0.0, 0.0)    # deg, on an end, the angle section flat
PRINT_ROT_CARRY_RAIL = (90.0, 0.0, 0.0)      # deg, bottom face down, groove up; 45 deg flanks
PRINT_ROT_RAIL_BRIDGE = (0.0, 90.0, 0.0)     # deg, headward face down, the section flat
EDGE_CHAMFER = 0.5    # mm, general outer edges

# --- Tolerances -----------------------------------------------------------
# Not physical dimensions -- used only for float-safe geometric comparisons
# (e.g. selecting edges by position) in part code.

EDGE_MATCH_TOLERANCE = 1e-6   # mm
CUTTER_OVERSHOOT = 1.0        # mm, how far a cutter runs past the face it opens, so no coplanar skin is left
