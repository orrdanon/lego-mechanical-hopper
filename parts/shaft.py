"""The 8 mm shaft. Bought, reference solid only, never exported
(drivetrain-spec §7). Same part at both ends; the head shaft's drive end is
simply whichever end the motor goes on.

Local frame: axis along z, origin at its centre, which is the centre plane
of the shaft set it carries, so placement is `at(t, 0)`.
"""

import sys
from pathlib import Path

# Allow `python parts/shaft.py` to find the project-root modules: Python only
# puts the script's own directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos

import params as p


def shaft() -> Part:
    """8.0 dia x 145.0, axis along local z, origin at its centre.
    Flat of SHAFT_FLAT_DEPTH x SHAFT_FLAT_LENGTH centred at z = 0,
    facing local +x."""
    radius = p.SHAFT_DIA / 2
    filed = Pos(radius - p.SHAFT_FLAT_DEPTH, 0, 0) * Box(
        p.SHAFT_FLAT_DEPTH,
        p.SHAFT_DIA,
        p.SHAFT_FLAT_LENGTH,
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    )
    return Cylinder(radius, p.SHAFT_LENGTH) - filed


if __name__ == "__main__":
    from ocp_vscode import show

    show(shaft())
