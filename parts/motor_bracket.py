"""The printed motor bracket (spec-drive §6): a foot bolted to the head
bridge plate through the plate's two drive-side M5, and a face plate the
motor bolts to, its pilot boss in the face plate's bore. PETG, one off.
Frame-fixed: it rides on the head plate and tilts with the conveyor.

Local frame: origin on the foot's underside (the bridge plate's top face),
at the head shaft station along the run and at the face plate's inboard
face across the machine. +x along the run, +y up along the run normal, +z
outboard. The shaft axis is the line (0, SHAFT_HEIGHT_ABOVE_PLATE, z). So
it goes at `at(CENTRE_DIST, plate_top_offset(), DRIVE_SIDE * FACE_PLATE_Z)`,
turned 180 deg about local y for DRIVE_SIDE = -1; the part is symmetric in
x, so one design serves both sides.

The foot crosses under the face plate -- it reaches the M5 outboard of it
and runs on inboard -- so the face plate's outboard face, the spec's print
face, has part on both sides of it. It prints foot down instead, with no
support: the slots print vertical, the pilot bore and the M3 holes
horizontal. README "Drive resolutions".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Pos, Rot, SlotCenterToCenter, extrude, fillet

import params as p

_THROUGH = 4 * p.FACE_PLATE_ABOVE_AXIS   # cutter length, well past any face


def _hole_z(x: float, y: float, dia: float) -> Part:
    """A through hole along z at local (x, y)."""
    return Pos(x, y, p.FACE_PLATE_T / 2) * Cylinder(dia / 2, _THROUGH)


def _slot_y(x: float, z: float, travel: float, width: float) -> Part:
    """A through slot along y at local (x, z), `travel` either way along x."""
    return Pos(x, 0, z) * Rot(90, 0, 0) * extrude(SlotCenterToCenter(2 * travel, width), amount=_THROUGH, both=True)


def face_plate_top() -> float:
    """Local y of the face plate's top: the shaft axis plus FACE_PLATE_ABOVE_AXIS, 72.0."""
    return p.SHAFT_HEIGHT_ABOVE_PLATE + p.FACE_PLATE_ABOVE_AXIS


def slot_z() -> float:
    """Local z of the frame-bolt slots: the rails' top-slot centreline, 36.5."""
    return p.PLATE_BOLT_Z - p.FACE_PLATE_Z


def motor_hole_centres() -> list[tuple[float, float]]:
    """(x, y) of the four M3 holes, on MOTOR_HOLE_SPACING about the shaft axis."""
    h, r = p.SHAFT_HEIGHT_ABOVE_PLATE, p.MOTOR_HOLE_SPACING / 2
    return [(sx * r, h + sy * r) for sx in (-1, 1) for sy in (-1, 1)]


def motor_bracket(pilot_bore: float = p.BRACKET_PILOT_BORE) -> Part:
    """The bracket. `pilot_bore` exists for the boss-clash negative control
    (spec-drive §8.10); the real part uses BRACKET_PILOT_BORE. See the
    module docstring for the local frame."""
    foot_len = p.BRACKET_FOOT_INBOARD + p.BRACKET_FOOT_OUTBOARD
    foot = Pos(0, 0, -p.BRACKET_FOOT_INBOARD) * Box(
        p.BRACKET_W, p.BRACKET_FOOT_T, foot_len, align=(Align.CENTER, Align.MIN, Align.MIN)
    )
    plate = Box(p.BRACKET_W, face_plate_top(), p.FACE_PLATE_T, align=(Align.CENTER, Align.MIN, Align.MIN))
    body = foot + plate
    roots = [
        e for e in body.edges()
        if abs(e.center().Y - p.BRACKET_FOOT_T) < p.EDGE_MATCH_TOLERANCE
        and min(abs(e.center().Z), abs(e.center().Z - p.FACE_PLATE_T)) < p.EDGE_MATCH_TOLERANCE
    ]
    assert len(roots) == 2, f"expected 2 foot-to-face-plate edges, found {len(roots)}"
    body = fillet(roots, p.BRACKET_FILLET)

    body -= _hole_z(0, p.SHAFT_HEIGHT_ABOVE_PLATE, pilot_bore)
    body -= [_hole_z(x, y, p.MOTOR_HOLE_DIA) for x, y in motor_hole_centres()]
    body -= [_slot_y(x, slot_z(), p.BRACKET_SLOT_TRAVEL, p.BRACKET_SLOT_W) for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X)]
    tie_x, tie_z = p.BRACKET_TIE_SLOT
    body -= Pos(0, 0, p.BRACKET_FOOT_OUTBOARD - p.BRACKET_TIE_SLOT_INSET) * Box(tie_x, _THROUGH, tie_z)
    return body


if __name__ == "__main__":
    from ocp_vscode import show

    show(motor_bracket())
