"""The plywood bridge plate -- a reference solid for clearance checking, cut
at the saw (see cut_list.py), never printed or exported as STL.

Local frame (phase 4 §2.3):

- local origin at the centre of the **top** face, the surface the pillow
  blocks and skirt posts bolt to
- +x along the run (PLATE_WIDTH)
- +y away from the frame; the body extends PLATE_THICKNESS into -y
- +z across the machine (PLATE_LENGTH)

Placing it is `bridge_plate(role).moved(at(plate_t(i), plate_top_offset()))`
with no corrective offset. The part itself knows nothing about stations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos, Rot

import params as p


def _bolt_hole(x: float, z: float) -> Part:
    """An M5 clearance cutter through the full plate thickness at local
    (x, z), axis along local y. Twice the plate thickness so it overshoots
    both faces rather than leaving coplanar end caps for the boolean."""
    cutter = Cylinder(p.PLATE_BOLT_CLEARANCE_DIA / 2, 2 * p.PLATE_THICKNESS)   # axis along z
    return Pos(x, -p.PLATE_THICKNESS / 2, z) * Rot(90.0, 0.0, 0.0) * cutter   # axis now along y


def bridge_plate(role: str = "support") -> Part:
    """A plywood bridge plate. Local origin at the centre of the top face.
    Length PLATE_LENGTH along local z, PLATE_WIDTH along local x,
    PLATE_THICKNESS into negative local y.

    Four M5 clearance holes, two at each end, at local x = ±PLATE_BOLT_X and
    local z = ±PLATE_BOLT_Z, which lands them on the rails' top-slot
    centrelines.

    role='bearing' or 'support' -- identical body, different hole pattern.
    Both patterns are empty in this phase; phase 5 adds them.
    """
    if role not in ("bearing", "support"):
        raise ValueError(f"role must be 'bearing' or 'support', got {role!r}")
    body = Box(
        p.PLATE_WIDTH,
        p.PLATE_THICKNESS,
        p.PLATE_LENGTH,
        align=(Align.CENTER, Align.MAX, Align.CENTER),
    )
    holes = [
        _bolt_hole(x, z)
        for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X)
        for z in (-p.PLATE_BOLT_Z, p.PLATE_BOLT_Z)
    ]
    plate = body - holes
    plate.label = f"bridge_plate ({role})"
    return plate


if __name__ == "__main__":
    from ocp_vscode import show

    show(bridge_plate())
