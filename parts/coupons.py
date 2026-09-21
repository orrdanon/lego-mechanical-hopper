"""The two calibration coupons (drivetrain-spec §10). Printed and exported.
Each is made by the same functions as the real part, so it calibrates the
real part.

Local frame, both: axis along z, origin on the axis at mid-thickness.
"""

import sys
from pathlib import Path

# Allow `python parts/coupons.py` to find the project-root modules: Python
# only puts the script's own directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Cylinder, Location, Part, extrude

import params as p
from geometry import guide_rim_radius
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


if __name__ == "__main__":
    from ocp_vscode import show

    show(ring_coupon(), guide_coupon().moved(Location((2.5 * guide_rim_radius(), 0, 0))))
