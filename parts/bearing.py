"""The 608ZZ ball bearing. Bought, reference solid only, never exported
(spec-pillow-blocks §3.2). No internal detail: an annulus with its edges
broken.

Local frame: axis along z, origin on the axis at the mid-width plane, so
placement is `at(t, 0, +/-BEARING_Z)`.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Axis, Part, Plane, Polygon, revolve

import params as p


def bearing() -> Part:
    """BEARING_BORE x BEARING_OD x BEARING_WIDTH, BEARING_EDGE_CHAMFER on
    all four circular edges."""
    ri, ro, h, c = p.BEARING_BORE / 2, p.BEARING_OD / 2, p.BEARING_WIDTH / 2, p.BEARING_EDGE_CHAMFER
    outline = [
        (ri + c, -h), (ro - c, -h), (ro, -h + c), (ro, h - c),
        (ro - c, h), (ri + c, h), (ri, h - c), (ri, -h + c),
    ]
    return revolve(Plane.XZ * Polygon(*outline, align=None), Axis.Z)


if __name__ == "__main__":
    from ocp_vscode import show

    show(bearing())
