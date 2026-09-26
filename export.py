"""STL export. Print orientation is applied here and nowhere else -- parts
are always modelled in their natural frame."""

from pathlib import Path

from build123d import Part, Rot, export_stl

import params as p
from parts.coupons import guide_coupon, ring_coupon
from parts.hinge import hinge_block, hinge_bracket
from parts.prop import base_pin_block, frame_clevis, knob, prop_body, prop_foot
from parts.shaft_set import shaft_set
from parts.slat import slat

OUT_DIR = Path(__file__).resolve().parent / "out"


def export_part(part: Part, name: str, print_rotation: tuple[float, float, float]) -> Path:
    """Rotate into print orientation, write out/<name>.stl, return the path."""
    OUT_DIR.mkdir(exist_ok=True)
    oriented = Rot(*print_rotation) * part
    path = OUT_DIR / f"{name}.stl"
    export_stl(oriented, str(path))
    return path


def export_all() -> list[Path]:
    """Export every printed part with its print rotation from params: both
    slat variants, the shaft set, the two calibration coupons and the tilt
    mechanism's printed parts (spec-tilt §8.4; R is the machine's +z side,
    the right-hand one looking from tail to head). Bought parts (shafts,
    belts, the cross-member, bolts, nuts, the rod), the base reference and
    reference/ are never written."""
    return [
        export_part(slat(cleated=False), "slat_plain", p.PRINT_ROT_PLAIN),
        export_part(slat(cleated=True), "slat_cleated", p.PRINT_ROT_CLEATED),
        export_part(shaft_set(), "shaft_set", p.PRINT_ROT_SHAFT_SET),
        export_part(ring_coupon(), "ring_coupon", p.PRINT_ROT_COUPON),
        export_part(guide_coupon(), "guide_coupon", p.PRINT_ROT_COUPON),
        export_part(hinge_bracket(1), "hinge_bracket_R", p.PRINT_ROT_HINGE_BRACKET[1]),
        export_part(hinge_bracket(-1), "hinge_bracket_L", p.PRINT_ROT_HINGE_BRACKET[-1]),
        export_part(hinge_block(1), "hinge_block_R", p.PRINT_ROT_HINGE_BLOCK),
        export_part(hinge_block(-1), "hinge_block_L", p.PRINT_ROT_HINGE_BLOCK),
        export_part(frame_clevis(), "frame_clevis", p.PRINT_ROT_CLEVIS),
        export_part(prop_body(), "prop_body", p.PRINT_ROT_PROP_BODY),
        export_part(prop_foot(), "prop_foot", p.PRINT_ROT_PROP_FOOT),
        export_part(knob(), "knob", p.PRINT_ROT_KNOB),
        export_part(base_pin_block(), "base_pin_block", p.PRINT_ROT_PIN_BLOCK),
    ]


if __name__ == "__main__":
    for path in export_all():
        print(f"wrote {path}")
