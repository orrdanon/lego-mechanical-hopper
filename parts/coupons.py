"""The calibration coupons: ring and guide (drivetrain-spec §10), and
bearing (spec-pillow-blocks §3.4). Printed and exported. Each is made by the
same functions as the real part, so it calibrates the real part.

Local frame, ring and guide: axis along z, origin on the axis at
mid-thickness. Bearing coupon: origin at the centre of the bed (lip) face,
+z up through the part, pockets along x.
"""

import sys
from pathlib import Path

# Allow `python parts/coupons.py` to find the project-root modules: Python
# only puts the script's own directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Location, Part, Pos, Rot, Text, extrude

import params as p
from geometry import guide_rim_radius
from parts.pillow_block import bearing_pocket
from parts.shaft_set import bore, guide_groove
from profile import pulley_section


def ring_coupon() -> Part:
    """pulley_section() extruded 3.0 thick, with a plain bore of
    PULLEY_BORE + PULLEY_BORE_CLEARANCE. Tests the real groove and the
    real pitch together, and sets PULLEY_GROOVE_COMP and PULLEY_OD_COMP."""
    ring = extrude(pulley_section(), amount=p.RING_COUPON_THICKNESS / 2, both=True)
    return ring - Cylinder((p.PULLEY_BORE + p.PULLEY_BORE_CLEARANCE) / 2, p.RING_COUPON_THICKNESS)


def guide_coupon() -> Part:
    """The guide wheel zone of shaft_set() alone, with its groove and bore.
    Paired with one printed slat to check lug entry and centring."""
    wheel = Cylinder(guide_rim_radius(), p.GUIDE_WIDTH)
    return wheel - guide_groove() - bore(p.GUIDE_WIDTH)


def bearing_coupon_pocket_x(index: int) -> float:
    """x of pocket `index` of the bearing coupon, BC_RIB_TIP_DIAS order."""
    return (index - (len(p.BC_RIB_TIP_DIAS) - 1) / 2) * p.BC_POCKET_PITCH


def bearing_coupon() -> Part:
    """A bar of the pillow block's section with one pocket per
    BC_RIB_TIP_DIAS, each cut by bearing_pocket() lip down and opening on
    the top face exactly as in the block, and its rib-tip diameter engraved
    beside it in the label strip. Prints the way the block does, lip face
    down, because hole size depends on it; sets PB_RIB_TIP_DIA."""
    bar = Box(p.BC_LENGTH, p.BC_WIDTH, p.BC_THICKNESS, align=(Align.CENTER, Align.CENTER, Align.MIN))
    pocket_y = -p.BC_WIDTH / 2 + p.BC_POCKET_EDGE
    label_y = (pocket_y + p.BC_POCKET_EDGE + p.BC_WIDTH / 2) / 2   # middle of the strip past the pockets
    lip_down = Pos(0, 0, p.PB_OUTBOARD_FACE_Z) * Rot(0, 180, 0)   # block z -> coupon z, lip face on z = 0
    for i, dia in enumerate(p.BC_RIB_TIP_DIAS):
        x = bearing_coupon_pocket_x(i)
        bar -= Pos(x, pocket_y, 0) * lip_down * bearing_pocket(dia)
        label = Text(f"{dia:.1f}", p.BC_TEXT_SIZE)
        bar -= Pos(x, label_y, p.BC_THICKNESS - p.BC_TEXT_DEPTH) * extrude(label, amount=2 * p.BC_TEXT_DEPTH)
    return bar


if __name__ == "__main__":
    from ocp_vscode import show

    show(ring_coupon(), guide_coupon().moved(Location((2.5 * guide_rim_radius(), 0, 0))), bearing_coupon())
