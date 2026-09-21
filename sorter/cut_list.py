"""Cut list for the plywood parts. Writes out/cut_list.txt -- the rectangle
sizes and hole positions you actually need at the saw. Plywood parts are
never exported as STL (phase 2 §8.6, phase 4 §9.6)."""

from pathlib import Path

import params as p

OUT_DIR = Path(__file__).resolve().parent / "out"


def bridge_plate_lines() -> list[str]:
    """Human-readable cut instructions for one bridge plate."""
    x_from_end = p.PLATE_WIDTH / 2 - p.PLATE_BOLT_X
    z_from_end = p.PLATE_LENGTH / 2 - p.PLATE_BOLT_Z
    return [
        f"Bridge plate  x{p.PLATE_STATIONS}  ({p.PLATE_COUNT_BEARING} bearing + {p.PLATE_COUNT_SUPPORT} support, identical in this phase)",
        f"  material : {p.PLATE_THICKNESS:g} mm plywood",
        f"  rectangle: {p.PLATE_LENGTH:g} x {p.PLATE_WIDTH:g} mm  (across the machine x along the run)",
        f"  holes    : 4 x {p.PLATE_BOLT_CLEARANCE_DIA:g} mm (M{p.PLATE_BOLT_M:g} clearance), one per corner,",
        f"             {z_from_end:g} mm in from each short edge, {x_from_end:g} mm in from each long edge",
        f"             (centres {2 * p.PLATE_BOLT_Z:g} mm apart across, {2 * p.PLATE_BOLT_X:g} mm apart along the run;",
        f"             across-spacing matches the frame rails' top-slot centrelines)",
    ]


def write_cut_list() -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "cut_list.txt"
    lines = ["Plywood cut list -- all dimensions mm", ""] + bridge_plate_lines() + [""]
    path.write_text("\n".join(lines))
    return path


if __name__ == "__main__":
    print(f"wrote {write_cut_list()}")
