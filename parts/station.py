"""The support stations on the three middle bridge plates (spec-skirts
§4.2-4.4), all printed: two posts on the plate outboard of the returning
run, an arm bolted across them between the runs that carries the rail
ends, and at 177 and 265.5 a skirt upright on each end of the arm.

The station is split so it can be closed round the belt: posts first, the
belt on, then the arm slid in sideways between the runs onto the post tops.
A one-piece bridge bolted to its plate is a ring the belt loop passes
through, and could only go in with the belt off.

Local frames, +x along the run, +y along the run normal, +z across:

- `station_post`: origin on the pad's bottom face, at the column's inner
  face, centred on the station; +z outboard. Placed with
  at(T, plate_top_offset(), +/-RAIL_POST_Z[0]), the -z one turned 180 deg
  about y (the post is symmetric in x, so one part serves both sides).
- `station_arm`: origin on its bottom face, on the centre plane, centred on
  the station. Placed with at(T, RAIL_ARM_OFFSET[0]).
- `skirt_upright`: origin on its bottom face, at its inner face, centred on
  the station; +z outboard. Placed with at(T, RAIL_ARM_OFFSET[1],
  +/-RAIL_POST_Z[0]), turned like the post.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos, Rot

import params as p
from geometry import hopper_offset, plate_top_offset

_UP = (Align.CENTER, Align.CENTER, Align.MIN)
_ARM_THICKNESS = p.RAIL_ARM_OFFSET[1] - p.RAIL_ARM_OFFSET[0]   # 16.0


def _along_y(radius: float, length: float) -> Part:
    """A cylinder from y = 0 to y = `length`, its axis along local y."""
    return Rot(-90, 0, 0) * Cylinder(radius, length, align=_UP)


def _along_z(radius: float, length: float) -> Part:
    """A cylinder from z = 0 to z = `length`, its axis along local z."""
    return Cylinder(radius, length, align=_UP)


def post_height() -> float:
    """Plate top to the arm's underside, 36.0."""
    return p.RAIL_ARM_OFFSET[0] - plate_top_offset()


def upright_height() -> float:
    """Arm top to the skirt top, 46.947."""
    return hopper_offset(p.SKIRT_HEIGHT) - p.RAIL_ARM_OFFSET[1]


def upright_cbore_depth() -> float:
    """Counterbore of the long M3s from the upright's top, so that a
    UPRIGHT_SCREW_LEN screw runs through upright and arm and engages the
    post's whole insert: 7.947."""
    return upright_height() + _ARM_THICKNESS + p.M3_INSERT_DEPTH - p.UPRIGHT_SCREW_LEN


def station_post() -> Part:
    """A column RAIL_ARM_LEN along the run across RAIL_POST_Z, from the plate
    top to the arm's underside, on a pad RAIL_PAD_THK thick reaching
    outboard to RAIL_PAD_Z: the built rail bridge's post and pad. Two M4
    through the pad and the plate; two M3 heat-set insert pockets down from
    the column top for the arm (and, at 177 and 265.5, the upright)."""
    inner = p.RAIL_POST_Z[0]
    column = Box(p.RAIL_ARM_LEN, post_height(), p.RAIL_POST_Z[1] - inner, align=(Align.CENTER, Align.MIN, Align.MIN))
    pad = Pos(0, 0, p.RAIL_POST_Z[1] - inner) * Box(
        p.RAIL_ARM_LEN, p.RAIL_PAD_THK, p.RAIL_PAD_Z - p.RAIL_POST_Z[1], align=(Align.CENTER, Align.MIN, Align.MIN)
    )
    post = column + pad
    cutters = []
    for x in (-p.RAIL_PAD_BOLT_X, p.RAIL_PAD_BOLT_X):
        cutters.append(Pos(x, 0, p.RAIL_PAD_BOLT_Z - inner) * _along_y(p.M4_CLEARANCE_DIA / 2, p.RAIL_PAD_THK))
    for x in (-p.STATION_POST_INSERT_X, p.STATION_POST_INSERT_X):
        top = post_height() - p.M3_INSERT_DEPTH
        cutters.append(Pos(x, top, p.STATION_POST_INSERT_Z - inner) * _along_y(p.M3_INSERT_DIA / 2, p.M3_INSERT_DEPTH))
    post -= cutters
    post.label = "station post"
    return post


def station_arm() -> Part:
    """The built bridge's arm, RAIL_ARM_LEN x RAIL_ARM_OFFSET x z
    +/-RAIL_ARM_HALF_W, with two cheeks on its top either side of the rail,
    RAIL_CHEEK_CLEAR off its sides, up to RAIL_CHEEK_TOP_OFFSET. Four M3
    down through its ends onto the post inserts, counterbored from the top;
    two M3 along z through the +z cheek onto the rail's side inserts.
    Nothing hangs below it toward the returning lugs."""
    arm = Box(p.RAIL_ARM_LEN, _ARM_THICKNESS, 2 * p.RAIL_ARM_HALF_W, align=(Align.CENTER, Align.MIN, Align.CENTER))
    cheek_h = p.RAIL_CHEEK_TOP_OFFSET - p.RAIL_ARM_OFFSET[1]
    cheek_in = p.GUIDE_WIDTH / 2 + p.RAIL_CHEEK_CLEAR
    for side in (1, -1):
        arm += Pos(0, _ARM_THICKNESS, side * (cheek_in + p.RAIL_CHEEK_T / 2)) * Box(
            p.RAIL_ARM_LEN, cheek_h, p.RAIL_CHEEK_T, align=(Align.CENTER, Align.MIN, Align.CENTER)
        )
    cutters = []
    for x in (-p.STATION_POST_INSERT_X, p.STATION_POST_INSERT_X):
        for z in (-p.STATION_POST_INSERT_Z, p.STATION_POST_INSERT_Z):
            cutters.append(Pos(x, 0, z) * _along_y(p.M3_CLEARANCE_DIA / 2, _ARM_THICKNESS))
            cutters.append(Pos(x, _ARM_THICKNESS - p.STATION_ARM_CBORE_DEPTH, z) * _along_y(p.M3_CBORE_DIA / 2, p.STATION_ARM_CBORE_DEPTH))
    y = p.RAIL_SIDE_INSERT_OFFSET - p.RAIL_ARM_OFFSET[0]
    for x in (-p.RAIL_INSERT_X, p.RAIL_INSERT_X):
        cutters.append(Pos(x, y, cheek_in) * _along_z(p.M3_CLEARANCE_DIA / 2, p.RAIL_CHEEK_T))
    arm -= cutters
    arm.label = "station arm"
    return arm


def skirt_upright() -> Part:
    """A block RAIL_ARM_LEN along the run across RAIL_POST_Z, from the arm
    top to the skirt top. Two M3 top to bottom over the post inserts,
    counterbored upright_cbore_depth(); two M4 along z at SKIRT_BOLT_H for
    the skirt, a nylock on the outboard face."""
    width = p.RAIL_POST_Z[1] - p.RAIL_POST_Z[0]
    upright = Box(p.RAIL_ARM_LEN, upright_height(), width, align=(Align.CENTER, Align.MIN, Align.MIN))
    z = p.STATION_POST_INSERT_Z - p.RAIL_POST_Z[0]
    cutters = []
    for x in (-p.STATION_POST_INSERT_X, p.STATION_POST_INSERT_X):
        cutters.append(Pos(x, 0, z) * _along_y(p.M3_CLEARANCE_DIA / 2, upright_height()))
        depth = upright_cbore_depth()
        cutters.append(Pos(x, upright_height() - depth, z) * _along_y(p.M3_CBORE_DIA / 2, depth))
    for h in p.SKIRT_BOLT_H:
        cutters.append(Pos(0, hopper_offset(h) - p.RAIL_ARM_OFFSET[1], 0) * _along_z(p.M4_CLEARANCE_DIA / 2, width))
    upright -= cutters
    upright.label = "skirt upright"
    return upright


if __name__ == "__main__":
    from ocp_vscode import show

    up = p.RAIL_ARM_OFFSET[0] - plate_top_offset()
    show(
        station_post(), Rot(0, 180, 0) * station_post(),
        Pos(0, up, -p.RAIL_POST_Z[0]) * station_arm(),
        Pos(0, up + _ARM_THICKNESS, 0) * skirt_upright(),
    )
