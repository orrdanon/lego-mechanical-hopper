"""The carrying-run support rails (hopper-spec §3.5, spec-skirts §4.1).
Printed. Rail A runs under the hopper from RAIL_T0 to the joint on the
station at 177; rail B from the joint to RAIL_B_T1, short of the head
wheel. The stations that carry them are in parts/station.py.

A rail is the guide wheel's rim zone run out straight: lands at the
guide-wheel-rim station, 0.5 under the slats' contact face, and the wheel's
own V-groove, cut by the same `guide_groove_section()`, for the lugs. At
nominal tension the slats run clear of it; under load the belt sags onto
the lands and the rail carries it, and the lug in the groove holds the
carrying run to the pulleys' +/-0.71 of lateral play.

Local frame: origin on the land plane, on the centre plane, at the rail's
tail end (t0); +x along the run, +y along the run normal (the body is in
-y), +z across. Placed with at(t0, guide_rim_radius()).
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Axis, Box, Cylinder, Part, Plane, Polygon, Pos, Rot, chamfer, extrude

import params as p
from geometry import guide_groove_bottom_radius, guide_rim_radius
from parts.shaft_set import guide_groove_section

RAIL_A = (p.RAIL_T0, p.RAIL_T1, (True, False))     # (t0, t1, free_ends): the hopper's, joint at its head end
RAIL_B = (p.RAIL_B_T0, p.RAIL_B_T1, (False, True))   # joint at its tail end


def rail_insert_t(t0: float, t1: float) -> list[float]:
    """Run parameters of a rail's side inserts: every station centre +/-
    RAIL_INSERT_X that lies on t0 .. t1 at least RAIL_INSERT_EDGE from both
    ends (spec-skirts §3.2)."""
    return [
        t
        for station in p.STATION_T for t in (station - p.RAIL_INSERT_X, station + p.RAIL_INSERT_X)
        if t0 + p.RAIL_INSERT_EDGE <= t <= t1 - p.RAIL_INSERT_EDGE
    ]


def carry_rail(
    t0: float = RAIL_A[0], t1: float = RAIL_A[1], free_ends: tuple[bool, bool] = RAIL_A[2], raise_by: float = 0.0,
) -> Part:
    """t0 .. t1 of the guide wheel's rim zone: GUIDE_WIDTH wide, lands at the
    rim station, a flat bottom at RAIL_BOTTOM_OFFSET, the guide groove along
    its length. A free end (`free_ends`, tail then head) gets a
    RAIL_END_CHAMFER lead-in down to the groove bottom, for lugs arriving
    from a wheel; a joint end only RAIL_JOINT_RELIEF on its top edges. M3
    heat-set insert pockets in the +z side face at rail_insert_t(), for the
    screws through the station arm's cheek. The defaults are rail A.

    `raise_by` lifts the lands and the groove together, the body's bottom
    staying put; it exists for the negative control of hopper-spec C3."""
    rim = guide_rim_radius()
    length = t1 - t0
    height = rim + raise_by - p.RAIL_BOTTOM_OFFSET
    body = Box(length, height, p.GUIDE_WIDTH, align=(Align.MIN, Align.MAX, Align.CENTER))
    body = Pos(0, raise_by, 0) * body
    # The groove section is (r, z) about a shaft axis; on the straight run r
    # is the offset, so y = r - rim.
    groove = Plane.ZY * Polygon(*[(z, r - rim + raise_by) for r, z in guide_groove_section()], align=None)
    rail = body - Pos(length / 2, 0, 0) * extrude(groove, amount=length / 2 + p.CUTTER_OVERSHOOT, both=True)
    bottom = p.RAIL_BOTTOM_OFFSET - rim
    joint_ends = [x0 for x0, free in zip((0.0, length), free_ends) if not free]
    if joint_ends:
        edges = [
            edge
            for x0 in joint_ends
            for edge in rail.edges()
            if abs(edge.center().X - x0) < p.EDGE_MATCH_TOLERANCE and abs((edge @ 1 - edge @ 0).X) < p.EDGE_MATCH_TOLERANCE
            and edge.center().Y > bottom + p.EDGE_MATCH_TOLERANCE
            and abs(abs(edge.center().Z) - p.GUIDE_WIDTH / 2) > p.EDGE_MATCH_TOLERANCE
        ]
        rail = chamfer(edges, p.RAIL_JOINT_RELIEF)
    cutters = []
    depth = rim - guide_groove_bottom_radius()
    run = depth / math.tan(math.radians(p.RAIL_END_CHAMFER))
    for (x0, sign), free in zip(((0.0, 1), (length, -1)), free_ends):
        if free:
            wedge = Polygon((x0, raise_by - depth), (x0 + sign * run, raise_by), (x0, raise_by), align=None)
            cutters.append(extrude(wedge, amount=p.GUIDE_WIDTH, both=True))
    y = p.RAIL_SIDE_INSERT_OFFSET - rim
    for t in rail_insert_t(t0, t1):
        pocket = Cylinder(p.M3_INSERT_DIA / 2, p.M3_INSERT_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MAX))
        cutters.append(Pos(t - t0, y, p.GUIDE_WIDTH / 2) * pocket)
    if cutters:
        rail -= cutters
    rail.label = "carry rail" if free_ends == RAIL_A[2] else "carry rail B"
    return rail


def carry_rail_b(raise_by: float = 0.0) -> Part:
    """Rail B, from the joint at 177 to RAIL_B_T1 (spec-skirts §4.1)."""
    return carry_rail(*RAIL_B, raise_by=raise_by)


if __name__ == "__main__":
    from ocp_vscode import show

    show(carry_rail(), Pos(p.RAIL_B_T0 - p.RAIL_T0, 0, 0) * carry_rail_b())
