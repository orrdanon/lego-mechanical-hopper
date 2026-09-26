"""The base -- OPEN (spec-tilt §6): a board, an extrusion frame or the bench.
Until that is decided it is a reference slab whose top face is the base
plane, used only for clearance checks. A placeholder: never exported, not
on the cut list.

Local frame: `geometry.base_frame()` -- origin on the top face directly
below the hinge axis, +x horizontal toward the head, +y up, +z across.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Part, Pos

import params as p


def base_ref() -> Part:
    """BASE_REF_THK thick, from BASE_REF_BEHIND behind the hinge axis to
    BASE_REF_AHEAD ahead of it, z = +/- BASE_REF_HALF_WIDTH."""
    slab = Pos(-p.BASE_REF_BEHIND, 0, 0) * Box(
        p.BASE_REF_BEHIND + p.BASE_REF_AHEAD,
        p.BASE_REF_THK,
        2 * p.BASE_REF_HALF_WIDTH,
        align=(Align.MIN, Align.MAX, Align.CENTER),
    )
    slab.label = "base_ref"
    return slab


if __name__ == "__main__":
    from ocp_vscode import show

    show(base_ref())
