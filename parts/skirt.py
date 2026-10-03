"""The side skirt (spec-skirts §4.5): plywood, cut list, a reference solid
here. One strip a side continues the hopper's channel from the front
wall's outer face to SKIRT_T1: inner face at SKIRT_INSET, from h =
SKIRT_GAP over the slat top to SKIRT_HEIGHT, SKIRT_THICKNESS thick
outboard, so its outer face lands on the skirt uprights.

Local frame: origin on the inner face, at the bottom edge, at SKIRT_T0;
+x along the run, +y along the run normal (up the strip), +z outboard for
side +1. Placed with at(SKIRT_T0, hopper_offset(SKIRT_GAP), side *
SKIRT_INSET). The -z strip is the mirror image, not a turned copy: its
countersinks are on its inner face too and the holes are not symmetric
along it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cone, Cylinder, Part, Plane, Pos, chamfer, mirror

import params as p

_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def skirt_length() -> float:
    """SKIRT_T0 to SKIRT_T1, 214.0."""
    return p.SKIRT_T1 - p.SKIRT_T0


def skirt_height() -> float:
    """SKIRT_GAP to SKIRT_HEIGHT, 26.5."""
    return p.SKIRT_HEIGHT - p.SKIRT_GAP


def skirt_holes() -> list[tuple[float, float]]:
    """(x, y) of the M4 holes in the strip's own frame: from the tail end
    and from the bottom edge, at each upright."""
    return [(t - p.SKIRT_T0, h - p.SKIRT_GAP) for t in p.SKIRT_STATIONS for h in p.SKIRT_BOLT_H]


def skirt(side: int = 1) -> Part:
    """The strip, SKIRT_EDGE_CHAMFER on its inner bottom edge, with an M4
    clearance hole at each of skirt_holes(), countersunk M4_CSK_DIA from
    the inner face so the heads lie flush on the channel wall."""
    strip = Box(skirt_length(), skirt_height(), p.SKIRT_THICKNESS, align=(Align.MIN, Align.MIN, Align.MIN))
    edge = [
        e for e in strip.edges()
        if abs(e.center().Y) < p.EDGE_MATCH_TOLERANCE and abs(e.center().Z) < p.EDGE_MATCH_TOLERANCE
    ]
    strip = chamfer(edge, p.SKIRT_EDGE_CHAMFER)
    sink = (p.M4_CSK_DIA - p.M4_CLEARANCE_DIA) / 2   # 90 deg: as deep as it is wide
    cutters = []
    for x, y in skirt_holes():
        cutters.append(Pos(x, y, 0) * Cylinder(p.M4_CLEARANCE_DIA / 2, p.SKIRT_THICKNESS, align=_UP))
        cutters.append(Pos(x, y, 0) * Cone(p.M4_CSK_DIA / 2, p.M4_CLEARANCE_DIA / 2, sink, align=_UP))
    strip -= cutters
    if side < 0:
        strip = mirror(strip, Plane.XY)
    strip.label = f"skirt {'+z' if side > 0 else '-z'}"
    return strip


if __name__ == "__main__":
    from ocp_vscode import show

    show(skirt(1), Pos(0, 0, -2 * p.SKIRT_INSET) * skirt(-1))
