"""The carrying-run support rail under the hopper, and the bridge that holds
it up off the bridge plate at 88.5 (hopper-spec §3.5, §4.7). Both printed.

The rail is the guide wheel's rim zone run out straight: lands at the
guide-wheel-rim station, 0.5 under the slats' contact face, and the wheel's
own V-groove, cut by the same `guide_groove_section()`, for the lugs. At
nominal tension the slats run clear of it; under the pile the belt sags onto
the lands and the rail carries the load, and the lug in the groove holds the
carrying run to the pulleys' +/-0.71 of lateral play.

Local frames:

- `carry_rail`: origin on the land plane, on the centre plane, at the rail's
  tail end; +x along the run, +y along the run normal (the body is in -y),
  +z across. Placed with at(RAIL_T0, guide_rim_radius()).
- `rail_bridge`: origin on the pads' bottom face, on the centre plane, at
  the arm's centre along the run; the same axes. Placed with
  at(RAIL_ARM_T_CENTRE, plate_top_offset()).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Plane, Polygon, Pos, Rot, extrude

import params as p
from geometry import guide_groove_bottom_radius, guide_rim_radius, plate_top_offset
from parts.shaft_set import guide_groove_section

_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def _along_y(radius: float, length: float) -> Part:
    """A cylinder from y = 0 to y = `length`, its axis along local y."""
    return Rot(-90, 0, 0) * Cylinder(radius, length, align=_UP)


def carry_rail(raise_by: float = 0.0) -> Part:
    """RAIL_T0 .. RAIL_T1 of the guide wheel's rim zone: GUIDE_WIDTH wide,
    lands at the rim station, a flat bottom at RAIL_BOTTOM_OFFSET, the
    guide groove along its length, and a RAIL_END_CHAMFER lead-in at each
    end down to the groove bottom, for lugs arriving from the tail wheel.
    Two M3 heat-set insert pockets in the bottom over the bridge's arm.

    `raise_by` lifts the lands and the groove together, the body's bottom
    staying put; it exists for the negative control of hopper-spec C3."""
    rim = guide_rim_radius()
    length = p.RAIL_T1 - p.RAIL_T0
    height = rim + raise_by - p.RAIL_BOTTOM_OFFSET
    body = Box(length, height, p.GUIDE_WIDTH, align=(Align.MIN, Align.MAX, Align.CENTER))
    body = Pos(0, raise_by, 0) * body
    # The groove section is (r, z) about a shaft axis; on the straight run r
    # is the offset, so y = r - rim.
    groove = Plane.ZY * Polygon(*[(z, r - rim + raise_by) for r, z in guide_groove_section()], align=None)
    cutters = [Pos(length / 2, 0, 0) * extrude(groove, amount=length / 2 + p.CUTTER_OVERSHOOT, both=True)]
    depth = rim - guide_groove_bottom_radius()
    run = depth / math.tan(math.radians(p.RAIL_END_CHAMFER))
    for x0, sign in ((0.0, 1), (length, -1)):
        wedge = Polygon((x0, raise_by - depth), (x0 + sign * run, raise_by), (x0, raise_by), align=None)
        cutters.append(extrude(wedge, amount=p.GUIDE_WIDTH, both=True))
    arm_x = p.RAIL_ARM_T_CENTRE - p.RAIL_T0
    bottom = p.RAIL_BOTTOM_OFFSET - rim
    for dx in (-p.RAIL_INSERT_X, p.RAIL_INSERT_X):
        cutters.append(Pos(arm_x + dx, bottom, 0) * _along_y(p.M3_INSERT_DIA / 2, p.M3_INSERT_DEPTH))
    rail = body - cutters
    rail.label = "carry rail"
    return rail


def rail_bridge() -> Part:
    """An arm between the carrying and returning runs, RAIL_ARM_LEN along
    the run and 2 x RAIL_ARM_HALF_W across, on two posts outboard of the
    returning slats, each post on a pad bolted through the plate with 2 x
    M4. The rail sits on the arm's top face with 2 x M3 up through it,
    counterbored from below so no head hangs toward the returning lugs.
    Printed on its headward face: the whole part is one section extruded
    along the run."""
    plate = plate_top_offset()
    arm_lo, arm_hi = p.RAIL_ARM_OFFSET[0] - plate, p.RAIL_ARM_OFFSET[1] - plate
    post_in, post_out = p.RAIL_POST_Z
    half = []   # the section for z >= 0, in (z, y), from the centre plane round
    half += [(0.0, arm_hi), (p.RAIL_ARM_HALF_W, arm_hi), (post_out, p.RAIL_PAD_THK), (p.RAIL_PAD_Z, p.RAIL_PAD_THK)]
    half += [(p.RAIL_PAD_Z, 0.0), (post_in, 0.0), (post_in, arm_lo), (0.0, arm_lo)]
    outline = half + [(-z, y) for z, y in reversed(half)]
    section = Plane.ZY * Polygon(*outline, align=None)
    bridge = Pos(-p.RAIL_ARM_LEN / 2, 0, 0) * extrude(section, amount=p.RAIL_ARM_LEN)
    cutters = []
    for dx in (-p.RAIL_INSERT_X, p.RAIL_INSERT_X):
        cutters.append(Pos(dx, arm_lo, 0) * _along_y(p.M3_CLEARANCE_DIA / 2, arm_hi - arm_lo))
        cutters.append(Pos(dx, arm_lo, 0) * _along_y(p.M3_CBORE_DIA / 2, arm_hi - arm_lo - p.RAIL_ARM_GRIP))
    for dx in (-p.RAIL_PAD_BOLT_X, p.RAIL_PAD_BOLT_X):
        for z in (-p.RAIL_PAD_BOLT_Z, p.RAIL_PAD_BOLT_Z):
            cutters.append(Pos(dx, 0, z) * _along_y(p.M4_CLEARANCE_DIA / 2, p.RAIL_PAD_THK))
    bridge -= cutters
    bridge.label = "rail bridge"
    return bridge


if __name__ == "__main__":
    from ocp_vscode import show

    bridge_to_rail = p.RAIL_ARM_OFFSET[1] - plate_top_offset() + guide_rim_radius() - p.RAIL_BOTTOM_OFFSET
    show(rail_bridge(), Pos(p.RAIL_T0 - p.RAIL_ARM_T_CENTRE, bridge_to_rail, 0) * carry_rail())
