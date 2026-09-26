"""The flexible 5 x 8 coupler (spec-drive §3.2). Bought, reference solid
only, never exported: a cylinder with a blind bore from each end,
COUPLER_BORE_DEPTH deep, so the shafts sit in it without clashing. The
helical cut and the clamping, which is open until measured, are not
modelled.

Local frame: origin on the axis at the 8-bore end face, +z toward the
5-bore end. So it goes at `at(CENTRE_DIST, 0, DRIVE_SIDE * COUPLER_Z)`,
turned to run outboard for DRIVE_SIDE = -1.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Cylinder, Part, Pos

import params as p

_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def coupler() -> Part:
    """COUPLER_DIA x COUPLER_LEN, bores COUPLER_BORE_BIG at z = 0 and
    COUPLER_BORE_SMALL at z = COUPLER_LEN, each COUPLER_BORE_DEPTH deep."""
    over = p.COUPLER_LEN   # the bore cutters overshoot the end faces
    body = Cylinder(p.COUPLER_DIA / 2, p.COUPLER_LEN, align=_UP)
    big = Pos(0, 0, -over) * Cylinder(p.COUPLER_BORE_BIG / 2, over + p.COUPLER_BORE_DEPTH, align=_UP)
    small = Pos(0, 0, p.COUPLER_LEN - p.COUPLER_BORE_DEPTH) * Cylinder(
        p.COUPLER_BORE_SMALL / 2, p.COUPLER_BORE_DEPTH + over, align=_UP
    )
    return body - big - small


if __name__ == "__main__":
    from ocp_vscode import show

    show(coupler())
