"""The printed pillow block: a 608ZZ press-fit housing that is its own
standoff, from the bridge plate up to the bearing (spec-pillow-blocks §3.1).
PETG, four off, identical; the two on a shaft are the same part turned
end for end, each with its retaining lip outboard.

Local frame: origin on the underside of the foot (the face that mates with
the bridge plate), directly under the bearing axis, in the bearing centre
plane. +x along the run, +y up along the run normal, +z outboard. The
bearing axis is the line (0, SHAFT_HEIGHT_ABOVE_PLATE, z). So the +z block
goes at `at(t, plate_top_offset(), BEARING_Z)` and the -z block at
`at(t, plate_top_offset(), -BEARING_Z)` turned 180 deg about local y. The
part is symmetric in x.

Print outboard (lip) face down, so the pocket is a vertical cylinder opening
upward and the lip is the first layers; no support. The insert pockets are
then horizontal, which suits heat-set inserts. Suggested, not enforced:
PETG, 4 perimeters, 40 % infill.
"""

import sys
from functools import cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import (
    Axis, Box, Circle, Cylinder, Location, Part, Plane, Polygon, Pos, Rectangle, Rot, extrude, fillet, revolve,
)

import params as p


def _revolved(points: list[tuple[float, float]]) -> Part:
    """Revolve an (r, z) outline about the local z axis."""
    return revolve(Plane.XZ * Polygon(*points, align=None), Axis.Z)


def _rib(angle: float, tip_r: float) -> Part:
    """One trapezoidal rib's solid, running the full pocket depth, centred
    on `angle` in the xy plane (deg from +x), its tip flat at radius
    `tip_r`. Its flanks carry on past the
    pocket wall by PB_POCKET_MOUTH_CHAMFER so it is joined to the wall
    across its whole base, not along a chord just inside it."""
    wall = p.PB_POCKET_DIA / 2
    tip, base = p.PB_RIB_TIP_WIDTH / 2, p.PB_RIB_BASE_WIDTH / 2
    outer_r = wall + p.PB_POCKET_MOUTH_CHAMFER
    outer = tip + (base - tip) * (outer_r - tip_r) / (wall - tip_r)
    section = Polygon((-tip, tip_r), (tip, tip_r), (outer, outer_r), (-outer, outer_r), align=None)
    rib = Pos(0, 0, p.PB_INBOARD_FACE_Z) * extrude(section, amount=p.PB_POCKET_DEPTH)
    return Rot(0, 0, angle - 90.0) * rib


def bearing_pocket(rib_tip_dia: float = p.PB_RIB_TIP_DIA) -> Part:
    """The cutter for the pocket, its ribs and the lip hole (steps 4-6),
    about the local z axis in the block's z: mouth at PB_INBOARD_FACE_Z,
    lip face at PB_OUTBOARD_FACE_Z. Ribs tipped on `rib_tip_dia`, each
    ramping from the wall to full height over PB_RIB_LEAD_IN from the mouth.
    The bearing coupon is cut with this same function."""
    wall, tip_r = p.PB_POCKET_DIA / 2, rib_tip_dia / 2
    mouth, floor, out = p.PB_INBOARD_FACE_Z, p.PB_INBOARD_FACE_Z + p.PB_POCKET_DEPTH, p.PB_OUTBOARD_FACE_Z
    over = p.PB_LIP_THICKNESS   # past both faces, so no boolean leaves a coplanar skin
    c = p.PB_POCKET_MOUTH_CHAMFER
    pocket = _revolved([(0.0, mouth - over), (wall, mouth - over), (wall, floor), (0.0, floor)])
    ribs = [_rib(p.PB_RIB_ANGLE_0 + i * 360.0 / p.PB_RIB_COUNT, tip_r) for i in range(p.PB_RIB_COUNT)]
    core = _revolved([
        (0.0, mouth - over), (wall, mouth - over), (wall, mouth),
        (tip_r, mouth + p.PB_RIB_LEAD_IN), (tip_r, floor), (0.0, floor),
    ])
    chamfer = _revolved([
        (0.0, mouth - over), (wall + c, mouth - over), (wall + c, mouth), (wall, mouth + c), (0.0, mouth + c),
    ])
    lip_hole = _revolved([(0.0, floor - over), (p.PB_LIP_HOLE_DIA / 2, floor - over),
                          (p.PB_LIP_HOLE_DIA / 2, out + over), (0.0, out + over)])
    return (pocket - ribs) + core + chamfer + lip_hole


def _body() -> Part:
    """Foot and tower with the tower-to-foot fillets (steps 1-3)."""
    z_in, z_out = p.PB_INBOARD_FACE_Z, p.PB_OUTBOARD_FACE_Z
    foot_z = p.PB_OUTBOARD_FACE_Z - p.PB_FOOT_INBOARD_Z
    foot = Pos(0, p.PB_FOOT_HEIGHT / 2, (p.PB_FOOT_INBOARD_Z + z_out) / 2) * Box(
        p.PB_FOOT_LENGTH, p.PB_FOOT_HEIGHT, foot_z
    )
    rise = p.SHAFT_HEIGHT_ABOVE_PLATE - p.PB_FOOT_HEIGHT
    profile = Pos(0, p.PB_FOOT_HEIGHT + rise / 2) * Rectangle(p.PB_TOWER_WIDTH, rise)
    profile += Pos(0, p.SHAFT_HEIGHT_ABOVE_PLATE) * Circle(p.PB_BOSS_RADIUS)
    tower = Pos(0, 0, z_in) * extrude(profile, amount=z_out - z_in)
    body = foot + tower

    def at(value: float, target: float) -> bool:
        return abs(value - target) < p.EDGE_MATCH_TOLERANCE

    concave = [
        e for e in body.edges()
        if at(e.center().Y, p.PB_FOOT_HEIGHT) and (
            at(abs(e.center().X), p.PB_TOWER_WIDTH / 2)   # both sides in x, running along z
            or (at(e.center().Z, z_in) and at(e.center().X, 0.0))   # the inboard corner, running along x
        )
    ]
    assert len(concave) == 3, f"expected 3 tower-to-foot edges, found {len(concave)}"
    return fillet(concave, p.PB_FILLET)


def _insert_pocket(x: float) -> Part:
    """A blind heat-set insert pocket PB_INSERT_POCKET_DEPTH up from the
    underside at (x, PB_BOLT_Z); centred on y = 0, so it overshoots below."""
    return Pos(x, 0, p.PB_BOLT_Z) * Rot(90, 0, 0) * Cylinder(p.PB_INSERT_DIA / 2, 2 * p.PB_INSERT_POCKET_DEPTH)


@cache
def _build(rib_tip_dia: float) -> Part:
    body = _body()
    body -= Pos(0, p.SHAFT_HEIGHT_ABOVE_PLATE, 0) * bearing_pocket(rib_tip_dia)
    body -= [_insert_pocket(x) for x in (-p.PB_BOLT_X, p.PB_BOLT_X)]
    return body


def pillow_block(rib_tip_dia: float = p.PB_RIB_TIP_DIA) -> Part:
    """One pillow block. `rib_tip_dia` exists for the press-fit controls
    (spec-pillow-blocks §5.2); the real part uses PB_RIB_TIP_DIA. See the
    module docstring for the local frame."""
    # The solid is cached; moved() hands each caller its own wrapper.
    return _build(rib_tip_dia).moved(Location())


if __name__ == "__main__":
    from ocp_vscode import show

    show(pillow_block())
