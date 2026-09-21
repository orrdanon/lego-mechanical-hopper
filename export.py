"""STL export. Print orientation is applied here and nowhere else -- parts
are always modelled in their natural frame."""

from pathlib import Path

from build123d import Part, Rot, export_stl

import params as p
from parts.coupons import guide_coupon, ring_coupon
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
    slat variants, the shaft set and the two calibration coupons. Bought
    parts (shaft, belt) and reference/ are never written."""
    return [
        export_part(slat(cleated=False), "slat_plain", p.PRINT_ROT_PLAIN),
        export_part(slat(cleated=True), "slat_cleated", p.PRINT_ROT_CLEATED),
        export_part(shaft_set(), "shaft_set", p.PRINT_ROT_SHAFT_SET),
        export_part(ring_coupon(), "ring_coupon", p.PRINT_ROT_COUPON),
        export_part(guide_coupon(), "guide_coupon", p.PRINT_ROT_COUPON),
    ]


if __name__ == "__main__":
    for path in export_all():
        print(f"wrote {path}")
