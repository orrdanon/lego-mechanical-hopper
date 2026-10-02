"""STL export. Print orientation is applied here and nowhere else -- parts
are always modelled in their natural frame."""

from pathlib import Path

from build123d import Part, Rot, export_stl

import params as p
from parts.carry_rail import carry_rail, rail_bridge
from parts.coupons import bearing_coupon, guide_coupon, ring_coupon
from parts.hinge import hinge_block, hinge_bracket
from parts.motor_bracket import motor_bracket
from parts.pillow_block import pillow_block
from parts.hopper import corner_cleat, hopper_foot, liner, meter_clamp, seal_clamp
from parts.prop import base_pin_block, frame_clevis, knob, prop_body, prop_foot
from parts.shaft_set import shaft_set
from parts.slat import slat
from parts.spacer import spacer

OUT_DIR = Path(__file__).resolve().parent / "out"


def export_part(part: Part, name: str, print_rotation: tuple[float, float, float]) -> Path:
    """Rotate into print orientation, write out/<name>.stl, return the path."""
    OUT_DIR.mkdir(exist_ok=True)
    oriented = Rot(*print_rotation) * part
    path = OUT_DIR / f"{name}.stl"
    export_stl(oriented, str(path))
    return path


def hopper_prints() -> list[tuple[Part, str, tuple[float, float, float]]]:
    """(part, name, print rotation) of every printed hopper part
    (hopper-spec §9.9). R and L as for the tilt: R is the machine's +z side.
    Print two of each foot and eight corner cleats."""
    return [
        (liner(1), "hopper_liner_R", p.PRINT_ROT_LINER[1]),
        (liner(-1), "hopper_liner_L", p.PRINT_ROT_LINER[-1]),
        (seal_clamp(), "seal_clamp", p.PRINT_ROT_SEAL_CLAMP),
        (meter_clamp(), "metering_clamp", p.PRINT_ROT_METER_CLAMP),
        (hopper_foot(1), "hopper_foot_R", p.PRINT_ROT_HOPPER_FOOT),
        (hopper_foot(-1), "hopper_foot_L", p.PRINT_ROT_HOPPER_FOOT),
        (corner_cleat(), "corner_cleat", p.PRINT_ROT_CORNER_CLEAT),
        (carry_rail(), "carry_rail", p.PRINT_ROT_CARRY_RAIL),
        (rail_bridge(), "rail_bridge", p.PRINT_ROT_RAIL_BRIDGE),
    ]


def printed_parts() -> list[tuple[Part, str, tuple[float, float, float]]]:
    """(part, name, print rotation) of every printed part: both slat
    variants, the shaft set, the three calibration coupons, the tilt
    mechanism's printed parts (spec-tilt §8.4; R is the machine's +z side,
    the right-hand one looking from tail to head), the pillow block and
    spacer (spec-pillow-blocks §1; four of each), the motor bracket
    (spec-drive §8) and the hopper's (hopper_prints()). Bought parts
    (shafts, bearings, motor, coupler, belts, brushes, the cross-member,
    bolts, nuts, the rod), plywood, the base reference, the hopper's cavity
    and reference/ are never written."""
    return [
        (slat(cleated=False), "slat_plain", p.PRINT_ROT_PLAIN),
        (slat(cleated=True), "slat_cleated", p.PRINT_ROT_CLEATED),
        (shaft_set(), "shaft_set", p.PRINT_ROT_SHAFT_SET),
        (ring_coupon(), "ring_coupon", p.PRINT_ROT_COUPON),
        (guide_coupon(), "guide_coupon", p.PRINT_ROT_COUPON),
        (hinge_bracket(1), "hinge_bracket_R", p.PRINT_ROT_HINGE_BRACKET[1]),
        (hinge_bracket(-1), "hinge_bracket_L", p.PRINT_ROT_HINGE_BRACKET[-1]),
        (hinge_block(1), "hinge_block_R", p.PRINT_ROT_HINGE_BLOCK),
        (hinge_block(-1), "hinge_block_L", p.PRINT_ROT_HINGE_BLOCK),
        (frame_clevis(), "frame_clevis", p.PRINT_ROT_CLEVIS),
        (prop_body(), "prop_body", p.PRINT_ROT_PROP_BODY),
        (prop_foot(), "prop_foot", p.PRINT_ROT_PROP_FOOT),
        (knob(), "knob", p.PRINT_ROT_KNOB),
        (base_pin_block(), "base_pin_block", p.PRINT_ROT_PIN_BLOCK),
        (pillow_block(), "pillow_block", p.PRINT_ROT_PILLOW_BLOCK),
        (spacer(), "spacer", p.PRINT_ROT_SPACER),
        (bearing_coupon(), "bearing_coupon", p.PRINT_ROT_COUPON),
        (motor_bracket(), "motor_bracket", p.PRINT_ROT_MOTOR_BRACKET),
    ] + hopper_prints()


def export_all() -> list[Path]:
    """Export every printed_parts() entry in its print orientation."""
    return [export_part(*printed) for printed in printed_parts()]


if __name__ == "__main__":
    for path in export_all():
        print(f"wrote {path}")
