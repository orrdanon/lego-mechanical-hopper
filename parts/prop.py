"""The prop that holds the frame at its incline (spec-tilt §4.2, §5), and
the two clevises it is pinned between. All printed.

    pin A   frame_clevis, under the cross-member
      |     prop_body    top eye on pin A, M8 nut captured near the bottom
      |     (lock nut, M8 rod, jam nut -- parts/hardware.py)
      |     knob         captured M8 nut, bears on a washer on the foot
      |     prop_foot    swivel on pin B; the rod turns in its top wall
    pin B   base_pin_block, on the base

Local frames:

- `frame_clevis`: origin on the cross-member contact face, above pin A, at
  z = 0; +x along the run, +y along the run normal (the body hangs into
  -y), +z across. Pin A is at (0, -CLEVIS_PIN_DROP, 0), along z.
- `prop_body`: origin at pin A's centre; +z along the prop axis toward the
  body's bottom face, +x along the pin.
- `prop_foot`: origin at pin B's centre; +z along the prop axis toward pin
  A, +x along the pin. The nut window opens to -y.
- `knob`: centre of its bottom face, on the rod axis (z).
- `base_pin_block`: origin on the base top face directly under pin B;
  base-frame axes (+y up). Pin B is at (0, PROP_PIN_B_Y, 0), along z.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Cylinder, Part, PolarLocations, Pos, Rot

import params as p
from parts.hardware import hex_prism

_UP = (Align.CENTER, Align.CENTER, Align.MIN)


def _along_x(radius: float, length: float) -> Part:
    """A cylinder centred on the origin with its axis along local x."""
    return Rot(0, 90, 0) * Cylinder(radius, length)


def _cheeks(gap: float, thickness: float, profile: Part) -> list[Part]:
    """`profile`, a solid spanning z = 0..1, stretched to `thickness` and
    set either side of a `gap` centred on z = 0."""
    return [
        Pos(0, 0, z0) * profile.scale((1, 1, thickness))
        for z0 in (gap / 2, -gap / 2 - thickness)
    ]


def frame_clevis() -> Part:
    """Two cheeks hanging from a flange bolted under the cross-member.

    Pin A is only CLEVIS_PIN_DROP below the cross-member, less than the
    prop's eye radius plus any flange, and its bolt head, washer and nut
    are wider than that again. So the flange is open tailward of
    CLEVIS_WINDOW_X, both between the cheeks (for the eye, and for the body
    as it swings) and outboard of them to CLEVIS_WINDOW_Z (for the pin's
    hardware); the cheeks are joined by a wall on the head side, where the
    prop never goes. See README.md "Frame clevis"."""
    outer = p.CLEVIS_GAP / 2 + p.CLEVIS_CHEEK_THK
    x0 = -p.CLEVIS_CHEEK_R
    length = p.CLEVIS_HEAD_X - x0
    flange = Pos(x0, 0, 0) * Box(length, p.CLEVIS_BASE_THK, p.CLEVIS_WIDTH, align=(Align.MIN, Align.MAX, Align.CENTER))
    window = Pos(x0, 0, 0) * Box(
        p.CLEVIS_WINDOW_X - x0, p.CLEVIS_BASE_THK, 2 * p.CLEVIS_WINDOW_Z, align=(Align.MIN, Align.MAX, Align.CENTER)
    )
    wall = Pos(p.CLEVIS_WINDOW_X, 0, 0) * Box(
        p.CLEVIS_HEAD_X - p.CLEVIS_WINDOW_X, p.CLEVIS_PIN_DROP, 2 * outer, align=(Align.MIN, Align.MAX, Align.CENTER)
    )
    # The nose is a half-disc: CLEVIS_CHEEK_R is more than CLEVIS_PIN_DROP,
    # so a whole disc would stand proud of the contact face.
    nose = Pos(0, -p.CLEVIS_PIN_DROP, 0) * (
        Cylinder(p.CLEVIS_CHEEK_R, 1, align=_UP)
        & Box(2 * p.CLEVIS_CHEEK_R, p.CLEVIS_CHEEK_R, 1, align=(Align.CENTER, Align.MAX, Align.MIN))
    )
    profile = Pos(x0, 0, 0) * Box(length, p.CLEVIS_PIN_DROP, 1, align=(Align.MIN, Align.MAX, Align.MIN)) + nose
    cutters = [Pos(0, -p.CLEVIS_PIN_DROP, 0) * Cylinder(p.CLEVIS_PIN_HOLE / 2, 2 * outer)]
    for z in (p.CLEVIS_BOLT_Z, -p.CLEVIS_BOLT_Z):
        hole = Rot(90, 0, 0) * Cylinder(p.M5_CLEARANCE_DIA / 2, p.CLEVIS_BASE_THK, align=_UP)   # axis along -y
        cutters.append(Pos(0, 0, z) * hole)
    clevis = flange - window + wall + _cheeks(p.CLEVIS_GAP, p.CLEVIS_CHEEK_THK, profile) - cutters
    clevis.label = "frame clevis"
    return clevis


def prop_body() -> Part:
    """A flat eye PROP_EYE_W wide on pin A, becoming a round body of
    PROP_BODY_DIA at PROP_EYE_LEN. An M8 nut is captured with its top face
    PROP_NUT_TOP above the bottom face, in a closed hex pocket (fit it at a
    print pause); the rod's thrust goes through it into the pocket's
    bridged ceiling. Above it a clearance bore takes the rod as it screws
    in, stopping PROP_ROD_BORE_STOP below pin A."""
    radius = p.PROP_BODY_DIA / 2
    eye = _along_x(radius, p.PROP_EYE_W) + Box(p.PROP_EYE_W, p.PROP_BODY_DIA, p.PROP_EYE_LEN, align=_UP)
    shank = Pos(0, 0, p.PROP_EYE_LEN) * Cylinder(radius, p.PROP_BODY_LEN - p.PROP_EYE_LEN, align=_UP)
    cutters = [
        _along_x(p.PROP_EYE_HOLE / 2, p.PROP_EYE_W),
        Pos(0, 0, p.PROP_ROD_BORE_STOP) * Cylinder(p.PROP_ROD_BORE / 2, p.PROP_BODY_LEN - p.PROP_ROD_BORE_STOP, align=_UP),
        Pos(0, 0, p.PROP_BODY_LEN - p.PROP_NUT_TOP) * hex_prism(p.M8_HEX_AF + p.HEX_POCKET_CLEAR, p.NUT_POCKET_DEPTH),
    ]
    body = eye + shank - cutters
    body.label = "prop body"
    return body


def prop_foot() -> Part:
    """A flat eye on pin B, widening past the pin block's cheeks to a round
    head of FOOT_DIA. The rod passes through the head's top wall, which
    takes the prop's thrust from the knob; two nuts jammed on the rod in the
    round pocket below the wall stop it lifting out, and turn with it. A
    window in the -y side lets them in -- README.md "Prop foot"."""
    floor = p.FOOT_LEN - p.FOOT_WALL_THK - p.FOOT_POCKET_LEN
    eye = _along_x(p.PROP_BODY_DIA / 2, p.PROP_EYE_W) + Box(p.PROP_EYE_W, p.PROP_BODY_DIA, floor, align=_UP)
    head = Pos(0, 0, floor) * Cylinder(p.FOOT_DIA / 2, p.FOOT_LEN - floor, align=_UP)
    cutters = [
        _along_x(p.PROP_EYE_HOLE / 2, p.PROP_EYE_W),
        Pos(0, 0, floor) * Cylinder(p.FOOT_POCKET_DIA / 2, p.FOOT_POCKET_LEN, align=_UP),
        Pos(0, 0, floor) * Box(p.FOOT_WINDOW_W, p.FOOT_DIA / 2, p.FOOT_POCKET_LEN, align=(Align.CENTER, Align.MAX, Align.MIN)),
        Pos(0, 0, floor) * Cylinder(p.FOOT_WALL_HOLE / 2, p.FOOT_LEN - floor, align=_UP),
    ]
    foot = eye + head - cutters
    foot.label = "prop foot"
    return foot


def knob() -> Part:
    """KNOB_DIA x KNOB_THK with KNOB_LOBES finger scallops in the rim, a
    rod hole, and an M8 nut captured in a hex pocket in the top face, where
    the jam nut holds it down."""
    scallops = PolarLocations(p.KNOB_DIA / 2, p.KNOB_LOBES) * Cylinder(p.KNOB_SCALLOP_R, p.KNOB_THK, align=_UP)
    cutters = [
        Cylinder(p.FOOT_WALL_HOLE / 2, p.KNOB_THK, align=_UP),
        Pos(0, 0, p.KNOB_THK - p.NUT_POCKET_DEPTH) * hex_prism(p.M8_HEX_AF + p.HEX_POCKET_CLEAR, p.NUT_POCKET_DEPTH),
    ]
    result = Cylinder(p.KNOB_DIA / 2, p.KNOB_THK, align=_UP) - scallops - cutters
    result.label = "knob"
    return result


def base_pin_block() -> Part:
    """Two cheeks on a foot plate, carrying pin B. The prop pushes the pin
    down into the cheeks, so they are solid below it and only a nose of
    PIN_BLOCK_CHEEK_R above, small enough for the foot's head to clear."""
    outer = p.PIN_BLOCK_GAP / 2 + p.PIN_BLOCK_CHEEK_THK
    plate = Box(p.PIN_BLOCK_LEN, p.PIN_BLOCK_THK, p.PIN_BLOCK_WIDTH, align=(Align.CENTER, Align.MIN, Align.CENTER))
    profile = Box(2 * p.PIN_BLOCK_CHEEK_R, p.PROP_PIN_B_Y, 1, align=(Align.CENTER, Align.MIN, Align.MIN)) + Pos(
        0, p.PROP_PIN_B_Y, 0
    ) * Cylinder(p.PIN_BLOCK_CHEEK_R, 1, align=_UP)
    cutters = [Pos(0, p.PROP_PIN_B_Y, 0) * Cylinder(p.PIN_BLOCK_PIN_HOLE / 2, 2 * outer)]
    for x in (p.PIN_BLOCK_HOLE_X, -p.PIN_BLOCK_HOLE_X):
        for z in (p.PIN_BLOCK_HOLE_Z, -p.PIN_BLOCK_HOLE_Z):
            hole = Rot(-90, 0, 0) * Cylinder(p.BASE_FIXING_HOLE / 2, p.PIN_BLOCK_THK, align=_UP)   # axis along +y
            cutters.append(Pos(x, 0, z) * hole)
    block = plate + _cheeks(p.PIN_BLOCK_GAP, p.PIN_BLOCK_CHEEK_THK, profile) - cutters
    block.label = "base pin block"
    return block


if __name__ == "__main__":
    from ocp_vscode import show

    show(frame_clevis(), Pos(0, -p.CLEVIS_PIN_DROP, 0) * Rot(0, 90, 0) * Rot(0, 0, 90) * prop_body())
