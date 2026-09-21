"""2D tooth geometry: the belt tooth and the standard pulley groove.

Two constructions, deliberately separate (drivetrain-spec §4). The pulley
groove is the published HTD-3M groove for 40 teeth, rebuilt in closed form
from five values read out of a manufacturer model, and is the part that must
work. The belt tooth is an approximation used only for the belt reference
solid, and is checked against the groove -- never the other way round.

Sits beside `geometry` in the layer stack: imports only `params`, builds
edges and faces but no solids and no positions.
"""

import math

from build123d import Edge, Face, Line, ThreePointArc, Wire

import params as p

Point = tuple[float, float]


def _facing_up(face: Face) -> Face:
    """The face with its normal along +z, whichever way its wire was wound,
    so that extruding it by a positive amount always goes towards +z."""
    return face if face.normal_at().Z > 0 else -face


def _arc(centre: Point, start: Point, end: Point) -> Edge:
    """The minor circular arc about `centre` from `start` to `end`."""
    a0 = math.atan2(start[1] - centre[1], start[0] - centre[0])
    a1 = math.atan2(end[1] - centre[1], end[0] - centre[0])
    sweep = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    radius = math.dist(centre, start)
    mid = (centre[0] + radius * math.cos(a0 + sweep / 2), centre[1] + radius * math.sin(a0 + sweep / 2))
    return ThreePointArc(start, mid, end)


# --- Belt tooth -- for the belt model only (drivetrain-spec §4.1) -------------
# Belt profile frame: land on y = 0, tooth rising in +y, centred on x = 0.


def _root_fillet_x() -> float:
    """x of the root fillet's centre, which is also where it meets the land."""
    return math.sqrt((p.FLANK_RADIUS + p.ROOT_RADIUS) ** 2 - (p.ROOT_RADIUS - p.FLANK_CENTRE_Y) ** 2)


def _tooth_points(sign: int) -> tuple[Point, Point, Point, Point, Point]:
    """Apex, flank/fillet tangent point, fillet centre, fillet/land point and
    the land's end, for the half of the tooth with x of the given sign."""
    x_f = _root_fillet_x()
    flank_centre = (0.0, p.FLANK_CENTRE_Y)
    fillet_centre = (sign * x_f, p.ROOT_RADIUS)
    k = p.FLANK_RADIUS / (p.FLANK_RADIUS + p.ROOT_RADIUS)   # the arcs are externally tangent
    tangent = (
        flank_centre[0] + k * (fillet_centre[0] - flank_centre[0]),
        flank_centre[1] + k * (fillet_centre[1] - flank_centre[1]),
    )
    return (0.0, p.TOOTH_HEIGHT), tangent, fillet_centre, (sign * x_f, 0.0), (sign * p.BELT_PITCH / 2, 0.0)


def tooth_half() -> list[Edge]:
    """Flank arc, root fillet and land for x >= 0, belt profile frame."""
    apex, tangent, fillet_centre, foot, land_end = _tooth_points(1)
    return [
        _arc((0.0, p.FLANK_CENTRE_Y), apex, tangent),
        _arc(fillet_centre, tangent, foot),
        Line(foot, land_end),
    ]


def tooth_face() -> Face:
    """One belt tooth spanning one pitch, closed along the land.

    The face covers the tooth between its two root fillets; the lands either
    side of it out to +/-BELT_PITCH/2 have no area, so they bound nothing
    and are left to the belt's backing."""
    apex, r_tangent, r_centre, r_foot, _ = _tooth_points(1)
    _, l_tangent, l_centre, l_foot, _ = _tooth_points(-1)
    flank_centre = (0.0, p.FLANK_CENTRE_Y)
    return _facing_up(Face(Wire([
        _arc(l_centre, l_foot, l_tangent),
        _arc(flank_centre, l_tangent, apex),
        _arc(flank_centre, apex, r_tangent),
        _arc(r_centre, r_tangent, r_foot),
        Line(r_foot, l_foot),
    ])))


# --- Pulley groove -- the HTD-3M standard for 40 teeth (drivetrain-spec §4.2) --
# Groove frame: origin on the pulley axis, v radial along the groove
# centreline, u tangential. Symmetric in u.


def _od_radius() -> float:
    return (p.PULLEY_OD - p.PULLEY_OD_COMP) / 2


def _groove_geometry() -> tuple[Point, Point, list[Point]]:
    """Flank arc centre, tip arc centre, and the junctions [A, B, C, D] of the
    half-groove with u >= 0, printer compensation applied.

    PULLEY_GROOVE_COMP moves every groove edge into the material: the bottom
    arc's radius shrinks and the concave flank arc's grows by it, about
    unchanged centres, which keeps them tangent. The convex tip arc shrinks
    by it and keeps its tangential offset, but its centre moves radially to
    stay tangent to the OD, which has its own compensation. See README.md
    "Groove compensation"."""
    bottom_r = p.PULLEY_GROOVE_BOTTOM_R - p.PULLEY_GROOVE_COMP
    flank_r = p.PULLEY_GROOVE_FLANK_R + p.PULLEY_GROOVE_COMP
    tip_r = p.PULLEY_GROOVE_TIP_R - p.PULLEY_GROOVE_COMP

    c1_dist = p.PULLEY_GROOVE_BOTTOM_R + p.PULLEY_GROOVE_FLANK_R   # tangent to the bottom arc
    c1 = (p.PULLEY_GROOVE_FLANK_U, math.sqrt(c1_dist ** 2 - p.PULLEY_GROOVE_FLANK_U ** 2))
    c2_dist = _od_radius() - tip_r                                  # tangent to the OD
    c2 = (p.PULLEY_GROOVE_TIP_U, math.sqrt(c2_dist ** 2 - p.PULLEY_GROOVE_TIP_U ** 2))

    a = (bottom_r * c1[0] / c1_dist, bottom_r * c1[1] / c1_dist)
    d = (_od_radius() * c2[0] / c2_dist, _od_radius() * c2[1] / c2_dist)

    # Internal common tangent: unit normal n with n.(c2 - c1) = -(flank_r + tip_r),
    # so the circles lie on opposite sides. Of the two, the one with v_A < v_B < v_C.
    gap = math.dist(c1, c2)
    w = ((c2[0] - c1[0]) / gap, (c2[1] - c1[1]) / gap)
    q = (flank_r + tip_r) / gap
    h = math.sqrt(1 - q ** 2)
    for side in (1, -1):
        n = (-q * w[0] - side * h * w[1], -q * w[1] + side * h * w[0])
        b = (c1[0] - flank_r * n[0], c1[1] - flank_r * n[1])
        c = (c2[0] + tip_r * n[0], c2[1] + tip_r * n[1])
        if a[1] < b[1] < c[1]:
            return c1, c2, [a, b, c, d]
    raise ValueError("no internal tangent runs up the groove flank -- the PULLEY_GROOVE_ values are inconsistent")


def groove_junctions() -> list[Point]:
    """(u, v) of the four junctions A, B, C, D of the half-groove, u >= 0."""
    return _groove_geometry()[2]


def _groove_half_points(sign: int, to_xy) -> list[Edge]:
    """The half-groove on the given side of its centreline, bottom outward,
    with every (u, v) point passed through `to_xy`."""
    c1, c2, (a, b, c, d) = _groove_geometry()
    bottom_r = p.PULLEY_GROOVE_BOTTOM_R - p.PULLEY_GROOVE_COMP

    def at(point: Point) -> Point:
        return to_xy((sign * point[0], point[1]))

    return [
        _arc(to_xy((0.0, 0.0)), to_xy((0.0, bottom_r)), at(a)),
        _arc(at(c1), at(a), at(b)),
        Line(at(b), at(c)),
        _arc(at(c2), at(c), at(d)),
    ]


def groove_half() -> list[Edge]:
    """Bottom arc, flank arc, straight flank, tip arc for u >= 0, groove frame."""
    return _groove_half_points(1, lambda point: point)


def _reversed(edges: list[Edge]) -> list[Edge]:
    return [e.reversed() for e in reversed(edges)]


def pulley_section(teeth: int = p.PULLEY_TEETH) -> Face:
    """The full toothed 2D outline: OD circle with `teeth` grooves at
    PULLEY_GROOVE_PHASE + k*360/teeth, compensation applied. Raises
    ValueError if teeth != 40, since the groove values are only valid for 40.

    Angles are measured from +y towards +x. This is the single source for
    the shaft set's teeth and the ring coupon; nothing else cuts grooves."""
    if teeth != p.PULLEY_GROOVE_TEETH:
        raise ValueError(
            f"the PULLEY_GROOVE_ values describe a {p.PULLEY_GROOVE_TEETH}-tooth pulley only, got {teeth}"
        )
    d = groove_junctions()[3]
    edges = []
    for k in range(teeth):
        def to_xy(point: Point, k: int = k, turn: int = 0) -> Point:
            theta = math.radians(p.PULLEY_GROOVE_PHASE + (k + turn) * 360.0 / teeth)
            u, v = point
            return (u * math.cos(theta) + v * math.sin(theta), -u * math.sin(theta) + v * math.cos(theta))

        edges += _reversed(_groove_half_points(-1, to_xy))
        edges += _groove_half_points(1, to_xy)
        next_start = to_xy((-d[0], d[1]), turn=1)
        edges.append(_arc((0.0, 0.0), to_xy(d), next_start))   # the land
    return _facing_up(Face(Wire(edges)))
