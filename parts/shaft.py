"""The 8 mm shaft. Bought, reference solid only, never exported
(drivetrain-spec §7). The tail shaft is SHAFT_LENGTH, symmetric; the head
shaft is cut longer on its drive end only, far enough into the coupler
(spec-drive §4), so it has a direction.

Local frame: axis along z, origin on the axis in the centre plane of the
shaft set it carries, so placement is `at(t, 0)`. The drive end, if any,
is at +z; the head shaft is turned end for end about local x for
DRIVE_SIDE = -1, which keeps the flat facing +x.
"""

import sys
from pathlib import Path

# Allow `python parts/shaft.py` to find the project-root modules: Python only
# puts the script's own directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos

import params as p


def shaft(drive_ext: float | None = None) -> Part:
    """8.0 dia, axis along local z, origin in the shaft set's centre plane.
    With `drive_ext` None, SHAFT_LENGTH (145.0) centred on the origin -- the
    tail shaft. Otherwise the -z end stays at SHAFT_LENGTH/2 and the +z end
    runs `drive_ext` past the bearing centre at BEARING_Z -- the head shaft,
    HEAD_SHAFT_DRIVE_EXT for HEAD_SHAFT_LEN overall. Flat of
    SHAFT_FLAT_DEPTH x SHAFT_FLAT_LENGTH centred at z = 0 either way,
    facing local +x."""
    radius = p.SHAFT_DIA / 2
    back = p.SHAFT_LENGTH / 2
    front = back if drive_ext is None else p.BEARING_Z + drive_ext
    filed = Pos(radius - p.SHAFT_FLAT_DEPTH, 0, 0) * Box(
        p.SHAFT_FLAT_DEPTH,
        p.SHAFT_DIA,
        p.SHAFT_FLAT_LENGTH,
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    )
    body = Pos(0, 0, -back) * Cylinder(radius, back + front, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body - filed


if __name__ == "__main__":
    from ocp_vscode import show

    show(shaft(p.HEAD_SHAFT_DRIVE_EXT))
