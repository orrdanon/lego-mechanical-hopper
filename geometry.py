"""Geometric datums shared by every part.

Pure functions only -- no solids are built here. Every future part positions
itself against `at()`, so its correctness is the foundation the rest of the
project stands on.
"""

import math

from build123d import Location, Plane, Vector

import params


def run_direction(incline: float = params.INCLINE) -> Vector:
    """Unit vector along the belt run, in machine coordinates.

    `incline` here and everywhere below is the tilt of the run from
    horizontal, TILT_MIN..TILT_MAX, INCLINE by default. The machine frame
    does not move: changing it rotates the conveyor about the origin, and it
    is the base that moves in machine coordinates (spec-tilt §2.1)."""
    theta = math.radians(incline)
    return Vector(math.cos(theta), math.sin(theta), 0.0)


def run_normal(incline: float = params.INCLINE) -> Vector:
    """Unit vector perpendicular to the run, out of the carrying face."""
    theta = math.radians(incline)
    return Vector(-math.sin(theta), math.cos(theta), 0.0)


# --- Radial stations about a shaft axis -- drivetrain-spec §9.1 -----------------
# Everything that asserts a radial clearance uses these, never literals.


def belt_back_radius() -> float:
    """Distance from a shaft axis to the belt's smooth outer face, which is
    the slat contact face, mm. The belt's land rests on the pulley OD and
    its teeth sit down in the grooves, so this is the OD plus the backing
    alone -- not plus the whole belt thickness, the phase 1 error corrected
    by drivetrain-spec §0. = PULLEY_OD/2 + BELT_BACK_THICKNESS = 19.947"""
    return params.PULLEY_OD / 2 + params.BELT_BACK_THICKNESS


def belt_tooth_tip_radius() -> float:
    """Radius of the belt's tooth tips when meshed, inside the pulley OD.
    = belt_back_radius() - BELT_THICKNESS = 17.547"""
    return belt_back_radius() - params.BELT_THICKNESS


def tab_tip_radius() -> float:
    """Radius of the saddle tab tips on a slat wrapped on a pulley.
    = belt_back_radius() - SADDLE_TAB_DEPTH = 16.347"""
    return belt_back_radius() - params.SADDLE_TAB_DEPTH


def cleat_tip_radius() -> float:
    """Radius swept by the cleat tips round a pulley, and their reach below
    the shaft axis on the returning run.
    = belt_back_radius() + SLAT_THICKNESS + CLEAT_HEIGHT = 34.947"""
    return belt_back_radius() + params.SLAT_THICKNESS + params.CLEAT_HEIGHT


def guide_rim_radius() -> float:
    """Radius of the guide wheel's rim, just under the slat contact face.
    = belt_back_radius() - GUIDE_RIM_GAP = 19.447"""
    return belt_back_radius() - params.GUIDE_RIM_GAP


def guide_groove_bottom_radius() -> float:
    """Radius of the guide groove's bottom, below the lug tip.
    = belt_back_radius() - LUG_DEPTH - GROOVE_TIP_CLEAR = 14.447"""
    return belt_back_radius() - params.LUG_DEPTH - params.GROOVE_TIP_CLEAR


def shaft_axis(end: str, incline: float = params.INCLINE) -> Vector:
    """Point on the tail ('tail') or head ('head') shaft axis at Z = 0.
    Raises ValueError for any other value."""
    if end == "tail":
        return Vector(0.0, 0.0, 0.0)
    if end == "head":
        return run_direction(incline) * params.CENTRE_DIST
    raise ValueError(f"end must be 'tail' or 'head', got {end!r}")


def at(t: float, offset: float = 0.0, lateral: float = 0.0, incline: float = params.INCLINE) -> Location:
    """A Location on the carrying run.

    t        distance along the run from the tail shaft axis, mm
    offset   distance from the shaft axis along run_normal, mm; positive is
             outward through the belt, negative is down towards the plates
    lateral  distance along machine Z, mm
    incline  tilt of the run from horizontal, deg

    `offset` is measured from the shaft axis, not the belt back face, so
    `at(t, 0)` is on the shaft and a slat on the carrying run is placed at
    `at(t, belt_back_radius())`. Every *_offset() datum below shares this
    origin. See README.md "Offset origin".

    The returned Location is oriented so that its local +x points along
    run_direction(), its local +y along run_normal(), and its local +z
    along machine +Z. Multiplying a part modelled in the spec's local frame
    (+x along the run, +y out along the normal, +z across) by this Location
    places it correctly with no extra rotation.
    """
    position = (
        shaft_axis("tail", incline)
        + run_direction(incline) * t
        + run_normal(incline) * offset
        + Vector(0.0, 0.0, 1.0) * lateral
    )
    plane = Plane(origin=position, x_dir=run_direction(incline), z_dir=Vector(0.0, 0.0, 1.0))
    return Location(plane)


# --- The belt loop and the take-up -- drivetrain-spec §9.2, §9.3 ----------------


def tail_shaft_t(takeup: float = 0.0) -> float:
    """Run position of the tail shaft with the tail plate slid by takeup,
    TAIL_TAKEUP_MIN <= takeup <= TAIL_TAKEUP_MAX. Positive takeup is away
    from the head, so this is -takeup. Raises ValueError outside the range."""
    if not params.TAIL_TAKEUP_MIN <= takeup <= params.TAIL_TAKEUP_MAX:
        raise ValueError(
            f"takeup must be in {params.TAIL_TAKEUP_MIN}..{params.TAIL_TAKEUP_MAX}, got {takeup}"
        )
    return -takeup


def loop_length(takeup: float = 0.0) -> float:
    """Pitch-line length of the loop round the two shafts. BELT_LOOP_LENGTH
    at takeup 0; each run grows by the takeup."""
    return params.BELT_LOOP_LENGTH - 2 * tail_shaft_t(takeup)


def loop_local(s: float, offset: float, takeup: float = 0.0) -> tuple[float, float, float]:
    """(t, offset_out, turn) of the loop in the run frame: the point at
    pitch-line distance s round the loop and `offset` from the shaft axes,
    as a run parameter and an offset for at(), plus the clockwise angle in
    degrees through which the belt's travel has turned from run_direction().

    See loop_at() for the stations. s is taken modulo the loop length."""
    pitch_radius = params.PULLEY_PD / 2
    arc = math.pi * pitch_radius
    t_tail = tail_shaft_t(takeup)
    run = params.CENTRE_DIST - t_tail
    s = s % (2 * run + 2 * arc)
    if s < run:
        return (t_tail + s, offset, 0.0)
    if s < run + arc:
        turn = (s - run) / pitch_radius
        centre = params.CENTRE_DIST
    elif s < 2 * run + arc:
        return (params.CENTRE_DIST - (s - run - arc), -offset, 180.0)
    else:
        turn = math.pi + (s - 2 * run - arc) / pitch_radius
        centre = t_tail
    return (centre + offset * math.sin(turn), offset * math.cos(turn), math.degrees(turn))


def loop_at(s: float, takeup: float = 0.0, incline: float = params.INCLINE) -> Location:
    """Frame on the belt back at distance s around the loop, measured
    along the pitch line, 0 <= s < BELT_LOOP_LENGTH.

    s = 0 is the tail tangent point at the start of the carrying run.
      0     .. C        carrying run
      C     .. C + 60   head arc
      C+60  .. 2C + 60  return run, travelling tailward
      2C+60 .. 828      tail arc

    Local +x is the direction of belt travel, +y points out of the belt
    back away from the loop, +z is machine z. On the carrying run this
    agrees exactly with at(s, belt_back_radius()).

    Distance is on the pitch line because that is where tooth pitch, and so
    SLAT_PITCH, is defined; position is reported at the belt-back radius,
    where the slat sits. With a non-zero takeup the tail shaft moves to
    tail_shaft_t(takeup), both runs change length by the takeup and the
    loop is loop_length(takeup) long -- see README.md "Take-up and the loop"."""
    t, offset, turn = loop_local(s, belt_back_radius(), takeup)
    return at(t, offset, incline=incline) * Location((0.0, 0.0, 0.0), (0.0, 0.0, -turn))


def slat_t(index: int) -> float:
    """Run parameter of slat `index`, counting from 0 at the tail. Also its
    distance round the loop for loop_at(), which is how slats are placed."""
    return index * params.SLAT_PITCH


def is_cleated(index: int) -> bool:
    """True if slat `index` carries a cleat."""
    return index % params.CLEAT_EVERY == 0


# --- Bridge plates and frame -- phase 2 §5, phase 4 §4 -----------------------


def plate_top_offset() -> float:
    """Offset of the bridge plates' top faces from the shaft axis, along
    run_normal. Negative, since the plates are below the shafts.
    = -SHAFT_HEIGHT_ABOVE_PLATE = -48.0"""
    return -params.SHAFT_HEIGHT_ABOVE_PLATE


def rail_top_offset() -> float:
    """Offset of the frame rails' top faces from the shaft axis, along
    run_normal. Negative. = plate_top_offset() - PLATE_THICKNESS = -57.0"""
    return plate_top_offset() - params.PLATE_THICKNESS


def rail_lateral() -> float:
    """Z of a rail's centreline. = FRAME_WIDTH/2 - FRAME_PROFILE/2 = 127.0"""
    return params.FRAME_WIDTH / 2 - params.FRAME_PROFILE / 2


def frame_t_centre() -> float:
    """Run parameter at the frame's midpoint."""
    return params.FRAME_T_START + params.FRAME_LENGTH / 2


def frame_t_end() -> float:
    """Run parameter at the frame's head end."""
    return params.FRAME_T_START + params.FRAME_LENGTH


def plate_t(index: int) -> float:
    """Run parameter of bridge plate `index`, 0 at the tail shaft through
    PLATE_STATIONS-1 (4) at the head shaft, evenly spaced.
    Raises IndexError outside that range."""
    if not 0 <= index < params.PLATE_STATIONS:
        raise IndexError(f"plate index must be in 0..{params.PLATE_STATIONS - 1}, got {index}")
    return index * params.CENTRE_DIST / (params.PLATE_STATIONS - 1)


def plate_role(index: int) -> str:
    """'bearing' for the end plates (0 and PLATE_STATIONS-1), 'support'
    for the ones between. Raises IndexError outside 0..PLATE_STATIONS-1."""
    plate_t(index)   # range check
    if index in (0, params.PLATE_STATIONS - 1):
        return "bearing"
    return "support"


# --- Tilt: hinge, base frame and prop -- spec-tilt §2.2, §5.2, §5.4 ------------
# The hinge axis is fixed to the frame, so none of these take a takeup.


def hinge_axis(incline: float = params.INCLINE) -> Vector:
    """Point on the hinge axis at Z = 0, machine coordinates: the frame's
    bottom tail corner, on the rail centreline."""
    return at(params.HINGE_T, params.HINGE_OFFSET, incline=incline).position


def base_frame(incline: float = params.INCLINE) -> Location:
    """The frame every base-fixed part is placed with. Origin on the base
    top face directly below the hinge axis; machine axes, +x horizontal
    toward the head, +y up, +z across. In it the hinge axis is at
    (0, HINGE_HEIGHT)."""
    return Location(hinge_axis(incline) - Vector(0.0, params.HINGE_HEIGHT, 0.0))


def base_z(incline: float = params.INCLINE) -> float:
    """Machine y of the base top face."""
    return base_frame(incline).position.Y


def height_above_base(point: Vector, incline: float = params.INCLINE) -> float:
    """Height of a machine-frame point above the base top face."""
    return point.Y - base_z(incline)


def prop_pin_a(incline: float = params.INCLINE) -> Vector:
    """Centre of the prop's top pin, in the frame clevis."""
    return at(params.PROP_PIN_A_T, params.PROP_PIN_A_OFFSET, incline=incline).position


def prop_pin_b(incline: float = params.INCLINE, pin_b_x: float = params.PROP_PIN_B_X) -> Vector:
    """Centre of the prop's bottom pin, in the base pin block. `pin_b_x`
    exists for the prop-clearance negative control."""
    return (base_frame(incline) * Location((pin_b_x, params.PROP_PIN_B_Y, 0.0))).position


def prop_length(incline: float = params.INCLINE, pin_b_x: float = params.PROP_PIN_B_X) -> float:
    """Pin A to pin B, mm. Strictly increasing over TILT_MIN..TILT_MAX, so
    turning the knob one way always raises the frame."""
    return (prop_pin_a(incline) - prop_pin_b(incline, pin_b_x)).length


def incline_for_length(length: float) -> float:
    """The incline a prop of `length` holds, by bisection on
    TILT_MIN..TILT_MAX. Raises ValueError for a length outside that range."""
    lo, hi = params.TILT_MIN, params.TILT_MAX
    if not prop_length(lo) <= length <= prop_length(hi):
        raise ValueError(f"length must be in {prop_length(lo):.1f}..{prop_length(hi):.1f}, got {length}")
    while hi - lo > 1e-9:
        mid = (lo + hi) / 2
        if prop_length(mid) < length:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def prop_turns(incline: float = params.INCLINE) -> float:
    """Turns of the knob up from TILT_MIN."""
    return (prop_length(incline) - prop_length(params.TILT_MIN)) / params.M8_PITCH


def prop_lean(incline: float = params.INCLINE) -> float:
    """Angle of the prop from vertical, deg, positive toward the head at the top."""
    axis = prop_pin_a(incline) - prop_pin_b(incline)
    return math.degrees(math.atan2(axis.X, axis.Y))


def prop_exposed_rod(incline: float = params.INCLINE) -> float:
    """Bare rod between the knob's jam nut and the lock nut run up against
    the body, mm: what calipers can reach on the real machine."""
    return prop_length(incline) - params.PROP_BODY_LEN - params.FOOT_LEN - params.FOOT_STACK + params.STACK_CLEARANCE


def prop_force(incline: float = params.INCLINE, weight: float = params.TILT_WEIGHT_N) -> float:
    """Compression in the prop, N: the weight's moment about the hinge axis
    over the perpendicular distance from the hinge axis to the prop line.
    Informational -- TILT_WEIGHT_N is an estimate (spec-tilt §5.4)."""
    hinge = hinge_axis(incline)
    centroid = at(params.TILT_CG_T, params.TILT_CG_OFFSET, incline=incline).position
    pin_b = prop_pin_b(incline)
    axis = (prop_pin_a(incline) - pin_b).normalized()
    arm = abs((pin_b - hinge).cross(axis).Z)
    return weight * (centroid.X - hinge.X) / arm


def prop_foot_frame(incline: float = params.INCLINE, pin_b_x: float = params.PROP_PIN_B_X) -> Location:
    """Frame of everything that rides on the foot: origin at pin B, local +z
    along the prop axis toward pin A, +x along the pin (machine +z), so +y
    faces down and headward and -y is the side a hand reaches."""
    pin_b = prop_pin_b(incline, pin_b_x)
    return Location(Plane(origin=pin_b, x_dir=Vector(0.0, 0.0, 1.0), z_dir=prop_pin_a(incline) - pin_b))


def prop_body_frame(incline: float = params.INCLINE, pin_b_x: float = params.PROP_PIN_B_X) -> Location:
    """Frame of the prop body: origin at pin A, local +z along the prop axis
    toward pin B, +x along the pin (machine +z)."""
    pin_a = prop_pin_a(incline)
    return Location(Plane(origin=pin_a, x_dir=Vector(0.0, 0.0, 1.0), z_dir=prop_pin_b(incline, pin_b_x) - pin_a))


def xmember_plate_clearance(xmember_t: float = params.XMEMBER_T) -> float:
    """Least distance along the run from the cross-member to a bridge plate
    footprint at nominal take-up, mm; negative is an overlap."""
    return min(
        abs(plate_t(i) - xmember_t) - params.PLATE_WIDTH / 2 - params.FRAME_PROFILE / 2
        for i in range(params.PLATE_STATIONS)
    )
