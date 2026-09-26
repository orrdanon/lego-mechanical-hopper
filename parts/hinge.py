"""The tilt hinge (spec-tilt §3): a bracket on the outer face of each side
rail carrying an M8 bolt as the hinge pin, and a block on the base holding
that pin in a plain printed bushing. Both printed, both mirror pairs.

`side` is +1 for the part on the machine's +z side and -1 for its mirror
in z. Both share one local frame, so the -z part's body lies in -z.

Local frames:

- `hinge_bracket`: origin on the rail-contact face, on the hinge axis; +x
  along the run, +y along the run normal, +z across the machine (outboard
  for side +1). Placed with at(HINGE_T, HINGE_OFFSET, +/-FRAME_WIDTH/2).
- `hinge_block`: origin on the base top face, directly under the hinge axis,
  at the block's inner face; base-frame axes (+y up).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, Plane, Pos, Rot, mirror

import params as p
from parts.hardware import hex_prism

_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def _sided(part: Part, side: int, label: str) -> Part:
    if side not in (1, -1):
        raise ValueError(f"side must be +1 or -1, got {side!r}")
    if side == -1:
        part = mirror(part, Plane.XY)
    part.label = f"{label} {'+z' if side == 1 else '-z'}"
    return part


def hinge_bracket(side: int = 1) -> Part:
    """A plate HINGE_BRKT_THK thick over the rail's full height from
    HINGE_BRKT_T0 to HINGE_BRKT_T1, with a boss of HINGE_BOSS_R round the
    axis. The hinge bolt goes in from the rail side before the bracket is
    bolted on: its head sits in a hex pocket open to the rail face, trapped
    against the rail, and its shank points outboard. Two counterbored M5
    holes at HINGE_BRKT_BOLT_T fix it to the rail's outer slot."""
    x0, x1 = p.HINGE_BRKT_T0 - p.HINGE_T, p.HINGE_BRKT_T1 - p.HINGE_T
    plate = Pos(x0, 0, 0) * Box(x1 - x0, p.FRAME_PROFILE, p.HINGE_BRKT_THK, align=(Align.MIN, Align.CENTER, Align.MIN))
    body = plate + Cylinder(p.HINGE_BOSS_R, p.HINGE_BRKT_THK, align=_UP)
    cutters = [
        Cylinder(p.HINGE_PIN_HOLE / 2, p.HINGE_BRKT_THK, align=_UP),
        hex_prism(p.M8_HEX_AF + p.HEX_POCKET_CLEAR, p.HINGE_HEAD_POCKET_DEPTH),
    ]
    for t in p.HINGE_BRKT_BOLT_T:
        cutters.append(Pos(t - p.HINGE_T, 0, 0) * Cylinder(p.M5_CLEARANCE_DIA / 2, p.HINGE_BRKT_THK, align=_UP))
        cutters.append(
            Pos(t - p.HINGE_T, 0, p.HINGE_BRKT_THK - p.M5_CBORE_DEPTH)
            * Cylinder(p.M5_CBORE_DIA / 2, p.M5_CBORE_DEPTH, align=_UP)
        )
    return _sided(body - cutters, side, "hinge bracket")


def hinge_block(side: int = 1) -> Part:
    """An upright HINGE_BLOCK_WIDTH x HINGE_BLOCK_THK, half-round on top
    about the hinge axis, bored HINGE_BUSH_HOLE for the bolt to turn in,
    with a foot flange on its outboard side. Outboard of it go a washer and
    a nylock, snug, not tight."""
    half = p.HINGE_BLOCK_WIDTH / 2
    upright = Box(p.HINGE_BLOCK_WIDTH, p.HINGE_HEIGHT, p.HINGE_BLOCK_THK, align=(Align.CENTER, Align.MIN, Align.MIN))
    crown = Pos(0, p.HINGE_HEIGHT, 0) * Cylinder(half, p.HINGE_BLOCK_THK, align=_UP)
    foot = Pos(0, 0, p.HINGE_BLOCK_THK) * Box(
        p.HINGE_FOOT_LEN, p.HINGE_FOOT_THK, p.HINGE_FOOT_WIDTH, align=(Align.CENTER, Align.MIN, Align.MIN)
    )
    cutters = [Pos(0, p.HINGE_HEIGHT, 0) * Cylinder(p.HINGE_BUSH_HOLE / 2, p.HINGE_BLOCK_THK, align=_UP)]
    for x in p.HINGE_FOOT_HOLE_X:
        hole = Rot(-90, 0, 0) * Cylinder(p.BASE_FIXING_HOLE / 2, p.HINGE_FOOT_THK, align=_UP)   # axis along +y
        cutters.append(Pos(x, 0, p.HINGE_BLOCK_THK + p.HINGE_FOOT_WIDTH / 2) * hole)
    return _sided(upright + crown + foot - cutters, side, "hinge block")


if __name__ == "__main__":
    from ocp_vscode import show

    show(hinge_bracket(), Pos(0, -p.HINGE_HEIGHT, p.HINGE_BRKT_THK + p.HINGE_GAP) * hinge_block())
