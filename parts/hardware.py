"""Bought M8 hardware for the tilt mechanism (spec-tilt §7). Reference
solids only, never exported. Threads are not modelled: a bolt and the rod
are plain M8_DIA cylinders and a nut has a plain M8_DIA bore.

Every part's axis is local z, with its origin where it seats:

- `hex_nut`, `washer`: centre of the bottom face
- `threaded_rod`: centre of the bottom end
- `pin_bolt`: centre of the underside of the head, shank into +z
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Cylinder, Part, Pos, RegularPolygon, extrude

import params as p

_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def hex_prism(across_flats: float, height: float) -> Part:
    """A hexagonal prism from z = 0 to `height`, two flats facing local
    +/-y. Also the cutter for every printed hex pocket."""
    return extrude(RegularPolygon(across_flats / 2, 6, major_radius=False), height)


def hex_nut(thickness: float = p.M8_NUT_THK) -> Part:
    """An M8 nut, M8_NUT_THK thick, or M8_NYLOCK_THK for a nylock."""
    return hex_prism(p.M8_HEX_AF, thickness) - Cylinder(p.M8_DIA / 2, thickness, align=_UP)


def washer() -> Part:
    return Cylinder(p.M8_WASHER_OD / 2, p.M8_WASHER_THK, align=_UP) - Cylinder(p.M8_DIA / 2, p.M8_WASHER_THK, align=_UP)


def threaded_rod(length: float = p.ROD_LEN) -> Part:
    return Cylinder(p.M8_DIA / 2, length, align=_UP)


def pin_bolt(grip: float) -> Part:
    """An M8 x M8_PIN_BOLT_LEN hex bolt with its washer and nylock run up to
    `grip` from the underside of the head, as one solid."""
    head = Pos(0, 0, -p.M8_HEAD_THK) * hex_prism(p.M8_HEX_AF, p.M8_HEAD_THK)
    shank = Cylinder(p.M8_DIA / 2, p.M8_PIN_BOLT_LEN, align=_UP)
    nut = Pos(0, 0, grip + p.M8_WASHER_THK) * hex_prism(p.M8_HEX_AF, p.M8_NYLOCK_THK)
    return head + shank + Pos(0, 0, grip) * Cylinder(p.M8_WASHER_OD / 2, p.M8_WASHER_THK, align=_UP) + nut


if __name__ == "__main__":
    from ocp_vscode import show

    show(pin_bolt(p.CLEVIS_GAP + 2 * p.CLEVIS_CHEEK_THK))
