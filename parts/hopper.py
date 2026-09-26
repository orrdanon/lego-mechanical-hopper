"""The hopper (hopper-spec-v1.md §4.1-4.6): a V-trough on the straight
carrying run, between a back wall leaning over the rising slats and a front
wall where a metering brush lets out one cleat pocket of parts at a time.

    side panels   plywood 9, cut list, one each side at z = +/-HOPPER_HALF_W
    liners        printed mirror pair: the channel's lower walls (the first
                  section of side skirt), the 45 deg flare, a flange on the panel
    back wall     plywood 6, cut list, at BACK_WALL_ANGLE through the seal brush root
    front wall    plywood 6, cut list, notched over the channel for the metering brush
    seal clamp    printed, holds the seal brush in the back wall's notch
    meter clamp   printed, slides on the front wall to set METER_GAP
    feet          printed, two mirror pairs on the rail top faces, holding the panels
    corner cleat  printed, 8 identical angles joining panels to walls
    cavity        reference solid for the capacity check, never exported

The carry rail and its bridge are in parts/carry_rail.py, the brushes in
parts/brush.py.

Hopper coordinates. Everything here is laid out in (t, h, z): t along the
run, h above the slat top face (so h = offset - slat_top_radius()), z across
-- the run frame of at() shifted up to the carrying surface. Each part is
built in them and then moved so that its local origin, on its mating face,
is at 0; the docstrings give that origin as a hopper point (t, h, z), and
assembly.py places the part with at(t, hopper_offset(h), z). Axes are the
run frame's throughout, so there is never a rotation to add, except for the
corner cleats (see corner_cleat_places()).

`side` is +1 for the machine's +z side and -1 for its mirror in z.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import (
    Align, Box, Cylinder, Location, Part, Plane, Polygon, Pos, Rot, Vector, extrude, mirror,
)

import params as p
from geometry import (
    back_wall_in, back_wall_point, back_wall_rim_h, back_wall_t, back_wall_u, back_wall_up, hopper_offset, rim_h,
    rail_lateral, rail_top_offset,
)

_BIG = 4 * p.FRAME_LENGTH   # the size of a half-space cutter, bigger than the machine


# --- Shared geometry --------------------------------------------------------------


def _v(t: float, h: float, z: float = 0.0) -> Vector:
    return Vector(t, h, z)


def _sided(part: Part, side: int, label: str) -> Part:
    if side not in (1, -1):
        raise ValueError(f"side must be +1 or -1, got {side!r}")
    if side == -1:
        part = mirror(part, Plane.XY)
    part.label = f"{label} {'+z' if side == 1 else '-z'}"
    return part


def _hole(centre: Vector, axis: Vector, dia: float, length: float = 4 * p.PANEL_THICKNESS) -> Part:
    """A cylindrical cutter of `dia` centred on `centre`, along `axis`."""
    return Location(Plane(origin=centre, z_dir=axis)) * Cylinder(dia / 2, length)


def _prism(plane: Plane, outline: list[tuple[float, float]], thickness: float, direction: Vector) -> Part:
    """A plate: `outline` in `plane`'s 2D coordinates, `thickness` along `direction`."""
    return extrude(plane * Polygon(*outline, align=None), amount=thickness, dir=direction)


def _mirrored(half: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """A (z, v) outline for z >= 0, running from the centre plane round,
    closed through its mirror image in z = 0, without the corners that are
    only points on a straight edge (the two on the centre plane)."""
    ring = half + [(-z, v) for z, v in reversed(half) if z != 0.0]
    corners = []
    for i, (z, v) in enumerate(ring):
        (z0, v0), (z1, v1) = ring[i - 1], ring[(i + 1) % len(ring)]
        if abs((z - z0) * (v1 - v0) - (v - v0) * (z1 - z0)) > 1e-9:
            corners.append((z, v))
    return corners


def _flare_h(z: float, out: float = 0.0) -> float:
    """Height at which the liner flare's inner face reaches z, or the plane
    `out` beyond it, measured normal to it."""
    f = math.radians(p.FLARE_ANGLE)
    return p.SKIRT_HEIGHT + (z - p.SKIRT_INSET - out / math.cos(f)) / math.tan(f)


def liner_inner(side_chamfer: bool = True) -> list[tuple[float, float]]:
    """The +z liner's inner face, (z, h), bottom to top: the lower wall at
    SKIRT_INSET from SKIRT_GAP to SKIRT_HEIGHT, the flare at FLARE_ANGLE out
    to the flange, the flange's inner face, and its chamfered top. This is
    the channel wall the pile sees; the cavity is bounded by it too.
    `side_chamfer` adds the bottom edge's 0.5 chamfer on the inner side."""
    flange_in = p.HOPPER_HALF_W - p.LINER_THICKNESS
    bottom = [(p.SKIRT_INSET + p.EDGE_CHAMFER, p.SKIRT_GAP), (p.SKIRT_INSET, p.SKIRT_GAP + p.EDGE_CHAMFER)]
    if not side_chamfer:
        bottom = [(p.SKIRT_INSET, p.SKIRT_GAP)]
    return bottom + [
        (p.SKIRT_INSET, p.SKIRT_HEIGHT),
        (flange_in, _flare_h(flange_in)),
        (flange_in, p.LINER_FLANGE_TOP_H - p.LINER_FLANGE_CHAMFER),
        (flange_in + p.LINER_FLANGE_CHAMFER, p.LINER_FLANGE_TOP_H),
    ]


def liner_outer() -> list[tuple[float, float]]:
    """The +z liner's outer face, (z, h), top to bottom: against the panel
    down to where the flare's underside meets it, the flare's underside, and
    the lower wall's outer face. The walls' outlines follow it."""
    lower = p.SKIRT_INSET + p.LINER_THICKNESS
    return [
        (p.HOPPER_HALF_W, p.LINER_FLANGE_TOP_H),
        (p.HOPPER_HALF_W, _flare_h(p.HOPPER_HALF_W, p.LINER_THICKNESS)),
        (lower, _flare_h(lower, p.LINER_THICKNESS)),
        (lower, p.SKIRT_GAP),
    ]


def _back_wall_plane() -> Plane:
    """The back wall's inner face in hopper coordinates, 2D (z, u) with u up
    the wall from the seal brush root line; its normal points into the wall."""
    (in_t, in_h), (up_t, up_h) = back_wall_in(), back_wall_up()
    plane = Plane(origin=_v(p.SEAL_ROOT_T, p.SEAL_ROOT_H), x_dir=(0, 0, 1), z_dir=(-in_t, -in_h, 0))
    assert (plane.y_dir - Vector(up_t, up_h, 0)).length < 1e-9
    return plane


def _headward_of_back_wall() -> Part:
    """Everything on the hopper side of the back wall's inner face."""
    (in_t, in_h) = back_wall_in()
    face = Plane(origin=_v(p.SEAL_ROOT_T, p.SEAL_ROOT_H), x_dir=(0, 0, 1), z_dir=(in_t, in_h, 0))
    return Location(face) * Box(_BIG, _BIG, _BIG, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _below_rim(rim_front_h: float = p.RIM_FRONT_H) -> Part:
    """Everything below the rim line, which is horizontal at RIM_LEVEL_INCLINE."""
    a = math.radians(p.RIM_LEVEL_INCLINE)
    down = Vector(-math.sin(a), -math.cos(a), 0)
    rim = Plane(origin=_v(p.HOPPER_FRONT_T, rim_front_h), x_dir=(0, 0, 1), z_dir=down)
    return Location(rim) * Box(_BIG, _BIG, _BIG, align=(Align.CENTER, Align.CENTER, Align.MIN))


# --- Corner cleats: where they go, which the panels and walls drill for ---------


def _cleat_frame_holes(origin: Vector, x_dir: Vector, z_dir: Vector) -> list[tuple[Vector, Vector]]:
    """(centre on the mating face, bolt axis) of a corner cleat's two holes,
    for a cleat placed at `origin` with local x and z along `x_dir` and
    `z_dir`: the x = 0 face's at a third of the length, the z = 0 face's at
    two thirds."""
    y_dir = z_dir.cross(x_dir)
    d = (p.CORNER_CLEAT_LEG + p.CORNER_CLEAT_T) / 2
    return [
        (origin + y_dir * (p.CORNER_CLEAT_LEN / 3) - z_dir * d, x_dir),
        (origin + y_dir * (2 * p.CORNER_CLEAT_LEN / 3) + x_dir * d, z_dir),
    ]


def corner_cleat_places() -> list[tuple[str, Vector, Vector, Vector]]:
    """(name, origin, x_dir, z_dir) of each corner cleat in hopper
    coordinates: where corner_cleat()'s origin goes and which way its local
    x (away from the wall, into the hopper) and z (along the panel's inward
    normal, reversed) point. Its y then runs along the corner, up or down,
    and the origin is at that end. The front pair sit under the flare, the
    back pair above the liner's flange.

    One part serves every corner, turned, never mirrored, so on the -z side
    the panel's bolt is the upper one of the pair where on the +z side it
    is the lower: the two panels differ in their cleat holes."""
    places = []
    up_t, up_h = back_wall_up()
    for name, heights, wall_in, up in (
        ("front", p.CORNER_CLEAT_FRONT_H, Vector(-1, 0, 0), Vector(0, 1, 0)),
        ("back", p.CORNER_CLEAT_BACK_H, Vector(*back_wall_in(), 0), Vector(up_t, up_h, 0)),
    ):
        for side in (1, -1):
            z_dir = Vector(0, 0, side)
            for i, h in enumerate(heights):
                if name == "front":
                    bottom = _v(p.HOPPER_FRONT_T, h, side * p.HOPPER_HALF_W)
                else:
                    t, hh = back_wall_point(back_wall_u(h))
                    bottom = _v(t, hh, side * p.HOPPER_HALF_W)
                origin = bottom if z_dir.cross(wall_in).dot(up) > 0 else bottom + up * p.CORNER_CLEAT_LEN
                places.append((f"corner cleat {name} {'+z' if side == 1 else '-z'} {i}", origin, wall_in, z_dir))
    return places


def _cleat_holes(leg: str) -> list[tuple[str, Vector, Vector]]:
    """(cleat name, hole centre on the mating face, bolt axis) of every
    corner cleat's bolt into its wall (leg 'wall') or its panel ('panel')."""
    holes = []
    for name, origin, x_dir, z_dir in corner_cleat_places():
        wall_hole, panel_hole = _cleat_frame_holes(origin, x_dir, z_dir)
        holes.append((name, *(wall_hole if leg == "wall" else panel_hole)))
    return holes


def corner_cleat() -> Part:
    """A 90 deg angle, CORNER_CLEAT_LEG each way, CORNER_CLEAT_T thick,
    CORNER_CLEAT_LEN long, with one M4 through each leg (bolt and nylock).
    Local origin at one end of the outer corner line: the wall mates with
    the x = 0 face and the panel with the z = 0 face; the angle lies in +x
    and -z and runs along +y. The two holes are at a third and two thirds of
    the length, so the two bolts' nuts pass each other."""
    leg, thk, length = p.CORNER_CLEAT_LEG, p.CORNER_CLEAT_T, p.CORNER_CLEAT_LEN
    body = Box(thk, length, leg, align=(Align.MIN, Align.MIN, Align.MAX)) + Box(
        leg, length, thk, align=(Align.MIN, Align.MIN, Align.MAX)
    )
    body -= [_hole(c, axis, p.M4_CLEARANCE_DIA) for c, axis in _cleat_frame_holes(Vector(), Vector(1, 0, 0), Vector(0, 0, 1))]
    body.label = "corner cleat"
    return body


# --- Side panel ----------------------------------------------------------------------


def side_panel_outline(side: int = 1) -> tuple[list[tuple[float, float]], list[tuple[float, float, float]]]:
    """The side panel as cut, in its own plane: (outline, holes). 2D (x, y)
    are the panel's local x and y (run and run normal, from its origin);
    holes are (x, y, diameter). See side_panel() for the outline. The two
    panels differ only in their corner cleat holes (corner_cleat_places())."""
    x0, y0 = p.HOPPER_FRONT_T, p.PANEL_BOTTOM_OFFSET
    front = p.HOPPER_FRONT_T + p.WALL_THICKNESS
    wall_out = -p.WALL_THICKNESS
    top_h = back_wall_rim_h(wall_out)
    points = [
        (p.PANEL_REAR_T_MIN, p.PANEL_BOTTOM_OFFSET),
        (front, p.PANEL_BOTTOM_OFFSET),
        (front, hopper_offset(rim_h(front))),
        (back_wall_t(top_h, wall_out), hopper_offset(top_h)),
        (back_wall_t(p.FLARE_TOP_H, wall_out), hopper_offset(p.FLARE_TOP_H)),
        (p.PANEL_REAR_T_MIN, hopper_offset(p.FLARE_TOP_H)),
    ]
    holes = [
        (t + dx - x0, p.HOPPER_FOOT_TOP_OFFSET - p.HOPPER_FOOT_SLOT_DEPTH / 2 - y0, p.M4_CLEARANCE_DIA)
        for t in p.HOPPER_FOOT_T
        for dx in (-p.HOPPER_FOOT_M4_X, p.HOPPER_FOOT_M4_X)
    ]
    holes += [
        (c.X - x0, hopper_offset(c.Y) - y0, p.M4_CLEARANCE_DIA)
        for name, c, axis in _cleat_holes("panel") if (c.Z > 0) == (side > 0)
    ]
    return [(t - x0, off - y0) for t, off in points], holes


def side_panel(side: int = 1) -> Part:
    """Plywood, PANEL_THICKNESS, two off, the -z one the same outline turned
    over, with its own corner cleat holes. Bottom edge at PANEL_BOTTOM_OFFSET from
    PANEL_REAR_T_MIN to the front wall's outer face; the front edge square
    to the run up to the rim; the top edge on the rim line; the rear edge
    down the back wall's outer face to the flare top, then square to the run
    at PANEL_REAR_T_MIN down to the bottom. Two M4 per foot and one per
    corner cleat.

    Local origin on the inner face, on the bottom edge, at HOPPER_FRONT_T
    -- (t, offset, z) = (HOPPER_FRONT_T, PANEL_BOTTOM_OFFSET, HOPPER_HALF_W);
    this one is placed by offset, not h. The board lies in +z."""
    outline, holes = side_panel_outline(side)
    panel = _prism(Plane.XY, outline, p.PANEL_THICKNESS, Vector(0, 0, 1))
    panel -= [_hole(Vector(x, y, 0), Vector(0, 0, 1), dia) for x, y, dia in holes]
    return _sided(panel, side, "side panel")


# --- Liner ----------------------------------------------------------------------


def liner(side: int = 1) -> Part:
    """The channel wall, flare and flange as one printed PETG part, a mirror
    pair, LINER_THICKNESS throughout: the section of liner_inner() and
    liner_outer() run from the back wall's inner face, cut to follow it, to
    HOPPER_FRONT_T. Two triangular ribs tie the flare's underside to the
    panel, and three M3 wood screws go through the flange into the panel.

    Local origin on the lower wall's inner face, at its bottom edge, at
    HOPPER_FRONT_T -- hopper point (HOPPER_FRONT_T, SKIRT_GAP, SKIRT_INSET)
    for the +z liner. It prints on the flange's outer face."""
    section = liner_inner() + liner_outer()
    t0 = back_wall_t(0.0) - p.LINER_THICKNESS   # the wall leans headward: its foot is furthest tailward
    length = p.HOPPER_FRONT_T - t0
    body = Pos(t0, 0, 0) * extrude(Plane.ZY * Polygon(*section, align=None), amount=length, dir=(1, 0, 0))
    rib_top = _flare_h(p.HOPPER_HALF_W, p.LINER_THICKNESS)
    rib = [
        (p.HOPPER_HALF_W, rib_top),
        (p.HOPPER_HALF_W, rib_top - p.LINER_RIB_LEG),
        (p.HOPPER_HALF_W - p.LINER_RIB_LEG, rib_top - p.LINER_RIB_LEG),
    ]
    for t in p.LINER_RIB_T:
        body += Pos(t - p.LINER_THICKNESS / 2, 0, 0) * extrude(
            Plane.ZY * Polygon(*rib, align=None), amount=p.LINER_THICKNESS, dir=(1, 0, 0)
        )
    body &= _headward_of_back_wall()
    body -= [
        _hole(_v(t, p.LINER_SCREW_H, p.HOPPER_HALF_W), Vector(0, 0, 1), p.M3_CLEARANCE_DIA)
        for t in p.LINER_SCREW_T
    ]
    body = Pos(-p.HOPPER_FRONT_T, -p.SKIRT_GAP, -p.SKIRT_INSET) * body
    return _sided(body, side, "liner")


# --- Back wall and seal clamp -------------------------------------------------------


def _seal_clamp_screws() -> list[tuple[float, float]]:
    """(z, u) of the seal clamp's M4 screws, on the back wall's inner face."""
    u = back_wall_u(p.BACK_NOTCH_H) + p.SEAL_CLAMP_LAP / 2
    return [(z, u) for z in p.SEAL_CLAMP_SCREW_Z]


def back_wall_outline() -> tuple[list[tuple[float, float]], list[tuple[float, float, float]]]:
    """The back wall as cut, in its own plane: (outline, holes), 2D (z, u)
    with u up the inner face from the seal brush root line. The outline is
    the liner's outer boundary (the cavity section grown by the liner
    thickness) up to the rim, with the channel notched up to BACK_NOTCH_H
    for the seal clamp; its bottom edge beside the notch is at SKIRT_GAP,
    behind the liner ends. Holes are (z, u, diameter)."""
    top = back_wall_u(back_wall_rim_h())
    half = [(0.0, back_wall_u(p.BACK_NOTCH_H)), (p.SKIRT_INSET, back_wall_u(p.BACK_NOTCH_H))]
    half += [(p.SKIRT_INSET, back_wall_u(p.SKIRT_GAP))]
    half += [(z, back_wall_u(h)) for z, h in reversed(liner_outer())][:-1]   # bottom up, to the flange's foot
    half += [(p.HOPPER_HALF_W, top), (0.0, top)]
    holes = [(z, u, p.M4_CLEARANCE_DIA) for z, u in _seal_clamp_screws()]
    plane = _back_wall_plane()
    for name, c, axis in _cleat_holes("wall"):
        if "back" in name:
            local = plane.to_local_coords(c)
            holes.append((local.X, local.Y, p.M4_CLEARANCE_DIA))
    return _mirrored(half), holes


def back_wall() -> Part:
    """Plywood, WALL_THICKNESS, one off: back_wall_outline() on the plane
    through the seal brush root line at BACK_WALL_ANGLE to the run.

    Local origin on the inner face, on the centre plane, at the brush root
    line -- hopper point (SEAL_ROOT_T, SEAL_ROOT_H, 0), where the wall
    itself is notched away."""
    outline, holes = back_wall_outline()
    plane = _back_wall_plane()
    wall = _prism(plane, outline, p.WALL_THICKNESS, plane.z_dir)
    wall -= [_hole(plane.from_local_coords((z, u)), plane.z_dir, dia) for z, u, dia in holes]
    wall = Pos(-p.SEAL_ROOT_T, -p.SEAL_ROOT_H, 0) * wall
    wall.label = "back wall"
    return wall


def _brush_slot(root: Vector, rake: float, below: float) -> Part:
    """The cutter for a brush backing's slot: BRUSH_BACKING_W +
    BRUSH_SLOT_CLEAR wide, from `below` under the root line to
    BRUSH_BACKING_H above it, raked `rake` deg with the tips headward, and
    HOPPER_CLAMP_LEN plus a margin long."""
    width = p.BRUSH_BACKING_W + p.BRUSH_SLOT_CLEAR
    slot = Box(width, below + p.BRUSH_BACKING_H, p.HOPPER_CLAMP_LEN + 2 * p.CUTTER_OVERSHOOT, align=(Align.CENTER, Align.MIN, Align.CENTER))
    return Pos(root) * Rot(0, 0, rake) * Pos(0, -below, 0) * slot


def seal_clamp() -> Part:
    """The bar that holds the seal brush in the back wall's notch, printed
    PETG, one off, HOPPER_CLAMP_LEN long between the liners.

    Below the notch top it fills the notch, SEAL_CLAMP_BACK into and behind
    the wall and SEAL_CLAMP_FRONT out of it; above, it laps SEAL_CLAMP_LAP
    up the wall's inner face, with three M4 heat-set inserts for screws from
    behind the wall. The brush slot is raked SEAL_BRUSH_RAKE with the root
    line on the wall's inner face; its lower face is at SEAL_CLAMP_LOW_H,
    9.15 above the cleat tips. Two M3 grub screws come in from the back face
    onto the backing. README "Brush clamps".

    Local origin on the face that mates with the back wall, on the centre
    plane, at its bottom edge -- the inner face at the notch top, hopper
    point back_wall_point(back_wall_u(BACK_NOTCH_H))."""
    back, front = -p.SEAL_CLAMP_BACK, p.SEAL_CLAMP_FRONT
    notch = back_wall_u(p.BACK_NOTCH_H)
    top = notch + p.SEAL_CLAMP_LAP
    section = [
        back_wall_point(back_wall_u(p.SEAL_CLAMP_LOW_H, back), back),
        back_wall_point(back_wall_u(p.SEAL_CLAMP_LOW_H, front), front),
        back_wall_point(top, front),
        back_wall_point(top, 0.0),
        back_wall_point(notch, 0.0),
        back_wall_point(notch, back),
    ]
    clamp = extrude(Polygon(*section, align=None), amount=p.HOPPER_CLAMP_LEN / 2, both=True)
    root = _v(p.SEAL_ROOT_T, p.SEAL_ROOT_H)
    clamp -= _brush_slot(root, p.SEAL_BRUSH_RAKE, p.SEAL_ROOT_H)
    plane = _back_wall_plane()
    for z, u in _seal_clamp_screws():
        pocket = Location(Plane(origin=plane.from_local_coords((z, u)), z_dir=-plane.z_dir))
        clamp -= pocket * Cylinder(p.PULLEY_INSERT_DIA / 2, p.M4_INSERT_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN))
    rake = math.radians(p.SEAL_BRUSH_RAKE)
    along, across = Vector(-math.sin(rake), math.cos(rake), 0), Vector(math.cos(rake), math.sin(rake), 0)
    for z in p.SEAL_CLAMP_GRUB_Z:
        start = root + along * (p.BRUSH_BACKING_H / 2) - across * ((p.BRUSH_BACKING_W + p.BRUSH_SLOT_CLEAR) / 2) + Vector(0, 0, z)
        grub = Location(Plane(origin=start, z_dir=-across)) * Cylinder(
            p.M3_TAP_DIA / 2, 2 * p.SEAL_CLAMP_BACK, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        clamp -= Pos(across * p.CUTTER_OVERSHOOT) * grub   # starting inside the slot
    t0, h0 = back_wall_point(notch)
    clamp = Pos(-t0, -h0, 0) * clamp
    clamp.label = "seal clamp"
    return clamp


# --- Front wall and metering clamp ----------------------------------------------------


def front_wall_outline() -> tuple[list[tuple[float, float]], list[tuple[float, float, float]]]:
    """The front wall as cut, in its own plane: (outline, holes), 2D (z, h).
    Across the whole hopper, from SKIRT_GAP to RIM_FRONT_H, with the
    channel notched up to FRONT_NOTCH_H for the metering brush. Wider below
    the flare than the spec's outline, which leaves the front corner cleats
    nothing to bolt to -- README "Front wall". Holes are (z, h, diameter)."""
    half = [
        (0.0, p.FRONT_NOTCH_H), (p.SKIRT_INSET, p.FRONT_NOTCH_H), (p.SKIRT_INSET, p.SKIRT_GAP),
        (p.HOPPER_HALF_W, p.SKIRT_GAP), (p.HOPPER_HALF_W, p.RIM_FRONT_H), (0.0, p.RIM_FRONT_H),
    ]
    holes = [(z, p.METER_BOLT_H, p.M4_CLEARANCE_DIA) for z in p.METER_BOLT_Z]
    holes += [(c.Z, c.Y, p.M4_CLEARANCE_DIA) for name, c, axis in _cleat_holes("wall") if "front" in name]
    return _mirrored(half), holes


def front_wall() -> Part:
    """Plywood, WALL_THICKNESS, one off, its inner face square to the run at
    HOPPER_FRONT_T: front_wall_outline(), with the metering clamp's two
    M4 and the front corner cleats' bolts.

    Local origin on the inner face, on the centre plane, at the slat top --
    hopper point (HOPPER_FRONT_T, 0, 0). The board lies in +x."""
    outline, holes = front_wall_outline()
    plane = Plane(origin=(0, 0, 0), x_dir=(0, 0, 1), z_dir=(-1, 0, 0))   # 2D (z, h)
    wall = _prism(plane, outline, p.WALL_THICKNESS, Vector(1, 0, 0))
    wall -= [_hole(Vector(0, h, z), Vector(1, 0, 0), dia) for z, h, dia in holes]
    wall.label = "front wall"
    return wall


def _stadium(length: float, dia: float, depth: float) -> Part:
    """A slot along local y, `length` between its end centres, through
    `depth` along x, centred on the origin."""
    end = Rot(0, 90, 0) * Cylinder(dia / 2, depth)
    return Box(depth, length, dia) + Pos(0, length / 2, 0) * end + Pos(0, -length / 2, 0) * end


def meter_clamp() -> Part:
    """A plate on the front wall's inner face that holds the metering brush
    over the notch, printed PETG, one off, HOPPER_CLAMP_LEN wide between the
    liners. The brush hangs from a slot in its lower edge at METER_RAKE; two
    vertical slots, each METER_GAP_MAX - METER_GAP_MIN long, ride on the
    wall's two M4, so the plate slides to set METER_GAP and closes the notch
    above the brush at every setting. Two M3 grub screws from the hopper
    side hold the backing. README "Brush clamps".

    Local origin on the mating face, on the centre plane, at the brush tip
    line -- hopper point (HOPPER_FRONT_T, METER_GAP, 0) at the nominal
    setting. The plate lies in -x."""
    base = p.BRUSH_FREE_LEN
    plate = Pos(0, base, 0) * Box(
        p.METER_CLAMP_T, p.METER_CLAMP_H, p.HOPPER_CLAMP_LEN, align=(Align.MAX, Align.MIN, Align.CENTER)
    )
    root = Vector(-p.METER_CLAMP_T / 2, base, 0)
    plate -= _brush_slot(root, p.METER_RAKE, p.CUTTER_OVERSHOOT)
    lo, hi = p.METER_BOLT_H - p.METER_GAP_MAX, p.METER_BOLT_H - p.METER_GAP_MIN
    for z in p.METER_BOLT_Z:
        plate -= Pos(-p.METER_CLAMP_T / 2, (lo + hi) / 2, z) * _stadium(hi - lo, p.M4_CLEARANCE_DIA, p.METER_CLAMP_T + 2 * p.CUTTER_OVERSHOOT)
    for z in p.METER_GRUB_Z:
        grub = Pos(-p.METER_CLAMP_T - p.CUTTER_OVERSHOOT, base + p.BRUSH_BACKING_H / 2, z) * Rot(0, 90, 0)
        plate -= grub * Cylinder(p.M3_TAP_DIA / 2, p.METER_CLAMP_T / 2 + p.CUTTER_OVERSHOOT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plate.label = "metering clamp"
    return plate


# --- Feet -------------------------------------------------------------------------


def hopper_foot(side: int = 1) -> Part:
    """A block standing on a rail's top face that carries a side panel's
    bottom edge in a slot, printed PETG, two mirror pairs. HOPPER_FOOT_LEN
    along the run, from the rail's outer face HOPPER_FOOT_INNER_Z inboard,
    up to HOPPER_FOOT_TOP_OFFSET. One counterbored M5 + T-nut into the
    rail's top slot; two M4 across through the slot's cheeks and the panel.

    Local origin on the bottom face, on the M5 axis -- (t, offset, z) =
    (HOPPER_FOOT_T[i], rail_top_offset(), +/-rail_lateral()). It prints on
    its bottom face."""
    height = p.HOPPER_FOOT_TOP_OFFSET - rail_top_offset()
    z_in, z_out = p.HOPPER_FOOT_INNER_Z - rail_lateral(), p.FRAME_WIDTH / 2 - rail_lateral()
    foot = Pos(0, 0, z_in) * Box(p.HOPPER_FOOT_LEN, height, z_out - z_in, align=(Align.CENTER, Align.MIN, Align.MIN))
    panel_mid = p.HOPPER_HALF_W + p.PANEL_THICKNESS / 2 - rail_lateral()
    foot -= Pos(0, height, panel_mid) * Box(
        p.HOPPER_FOOT_LEN + 2 * p.CUTTER_OVERSHOOT, 2 * p.HOPPER_FOOT_SLOT_DEPTH, p.HOPPER_FOOT_SLOT_W
    )
    foot -= _hole(Vector(0, 0, 0), Vector(0, 1, 0), p.M5_CLEARANCE_DIA, 4 * height)
    foot -= Pos(0, p.HOPPER_FOOT_CBORE_FLOOR, 0) * Rot(-90, 0, 0) * Cylinder(
        p.M5_CBORE_DIA / 2, height, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    for x in (-p.HOPPER_FOOT_M4_X, p.HOPPER_FOOT_M4_X):
        foot -= _hole(Vector(x, height - p.HOPPER_FOOT_SLOT_DEPTH / 2, 0), Vector(0, 0, 1), p.M4_CLEARANCE_DIA, 4 * height)
    return _sided(foot, side, "hopper foot")


# --- Cavity -----------------------------------------------------------------------


def hopper_cavity(rim_front_h: float = p.RIM_FRONT_H) -> Part:
    """What the hopper holds, for the capacity check (hopper-spec §6): the
    space bounded by the slat top plane, the back wall, the liners, the
    panels, the front wall with its notch treated as closed, and the rim.
    The liners' 1.5 gap over the slats is treated as closed too. A
    reference solid, never exported. `rim_front_h` exists for the negative
    control of B2, which puts the rim lower than params allows.

    Local origin at the front wall's inner face, on the centre plane, on the
    slat top -- hopper point (HOPPER_FRONT_T, 0, 0), like front_wall()."""
    high = 2 * rim_h(p.HOPPER_TAIL_KEEPOUT_T, rim_front_h)
    wall = [(p.SKIRT_INSET, 0.0)] + liner_inner(side_chamfer=False)[1:]
    half = [(0.0, 0.0)] + wall + [(p.HOPPER_HALF_W, high), (0.0, high)]
    t0 = back_wall_t(0.0) - p.WALL_THICKNESS
    section = Plane.ZY * Polygon(*_mirrored(half), align=None)
    cavity = Pos(t0, 0, 0) * extrude(section, amount=p.HOPPER_FRONT_T - t0, dir=(1, 0, 0))
    cavity = cavity & _headward_of_back_wall() & _below_rim(rim_front_h)
    cavity = Pos(-p.HOPPER_FRONT_T, 0, 0) * cavity
    cavity.label = "hopper cavity"
    return cavity


if __name__ == "__main__":
    from ocp_vscode import show

    show(liner(1), liner(-1), back_wall(), front_wall())
