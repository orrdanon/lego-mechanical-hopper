"""The NEMA 17 stepper, Waveshare 42.3 x 40 (spec-drive §3.1). Bought,
reference solid only, never exported: body, pilot boss and shaft. The
shaft's D-flat, the tapped M3 holes and the connector are not modelled.

Local frame: origin at the centre of the mounting face, +z along the shaft,
out of the face; x and y across the face. The boss and shaft are at +z, the
body at -z. So on the drive side the shaft points inboard, and the motor
goes at the mounting face, `at(CENTRE_DIST, 0, DRIVE_SIDE * MOTOR_FACE_Z)`,
turned to face -DRIVE_SIDE.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part

import params as p

_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def motor() -> Part:
    """Body MOTOR_SQUARE square x MOTOR_BODY_LEN behind the face, boss
    MOTOR_PILOT_DIA x MOTOR_PILOT_H and shaft MOTOR_SHAFT_DIA x
    MOTOR_SHAFT_LEN in front of it, the shaft measured from the face."""
    body = Box(p.MOTOR_SQUARE, p.MOTOR_SQUARE, p.MOTOR_BODY_LEN, align=(Align.CENTER, Align.CENTER, Align.MAX))
    boss = Cylinder(p.MOTOR_PILOT_DIA / 2, p.MOTOR_PILOT_H, align=_UP)
    shaft = Cylinder(p.MOTOR_SHAFT_DIA / 2, p.MOTOR_SHAFT_LEN, align=_UP)
    return body + boss + shaft


if __name__ == "__main__":
    from ocp_vscode import show

    show(motor())
