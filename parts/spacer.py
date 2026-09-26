"""The spacer tube between a bearing's inner ring and the shaft set
(spec-pillow-blocks §3.3). Printed, PETG, four off, identical; prints axis
vertical, either end down.

Local frame: axis along z, origin on the axis at the face that mates with
the bearing's inner ring; +z runs along the tube toward the shaft set. So
the -z spacer goes at `at(t, 0, -(BEARING_Z - BEARING_WIDTH/2))` and the
+z one at the mirror position turned end for end.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Axis, Part, Plane, Polygon, revolve

import params as p


def spacer() -> Part:
    """SPACER_BORE x SPACER_OD x SPACER_LENGTH, SPACER_CHAMFER on all four
    circular edges."""
    ri, ro, length, c = p.SPACER_BORE / 2, p.SPACER_OD / 2, p.SPACER_LENGTH, p.SPACER_CHAMFER
    outline = [
        (ri + c, 0.0), (ro - c, 0.0), (ro, c), (ro, length - c),
        (ro - c, length), (ri + c, length), (ri, length - c), (ri, c),
    ]
    return revolve(Plane.XZ * Polygon(*outline, align=None), Axis.Z)


if __name__ == "__main__":
    from ocp_vscode import show

    show(spacer())
