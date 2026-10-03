"""Cut list for everything sawn rather than printed: the plywood bridge
plates, the tilt mechanism's cross-member and threaded rod (spec-tilt
§8.4), the two shafts, which differ since the drive (spec-drive §8),
the hopper's side panels and walls (hopper-spec §9.9) and the skirt
strips (spec-skirts §4.5). Writes
out/cut_list.txt -- the sizes and hole positions you actually need at the
saw. None of these is exported as STL (phase 2 §8.6, phase 4 §9.6)."""

from pathlib import Path

import geometry as g
import params as p
from parts.hopper import back_wall_outline, front_wall_outline, side_panel_outline
from parts.skirt import skirt_height, skirt_holes, skirt_length

OUT_DIR = Path(__file__).resolve().parent / "out"


def bridge_plate_lines() -> list[str]:
    """Human-readable cut instructions for one bridge plate."""
    x_from_end = p.PLATE_WIDTH / 2 - p.PLATE_BOLT_X
    z_from_end = p.PLATE_LENGTH / 2 - p.PLATE_BOLT_Z
    pb_z = p.BEARING_Z + p.PB_BOLT_Z
    return [
        f"Bridge plate  x{p.PLATE_STATIONS}  ({p.PLATE_COUNT_BEARING} bearing + {p.PLATE_COUNT_SUPPORT} support)",
        f"  material : {p.PLATE_THICKNESS:g} mm plywood",
        f"  rectangle: {p.PLATE_LENGTH:g} x {p.PLATE_WIDTH:g} mm  (across the machine x along the run)",
        f"  holes    : 4 x {p.PLATE_BOLT_CLEARANCE_DIA:g} mm (M{p.PLATE_BOLT_M:g} clearance), one per corner,",
        f"             {z_from_end:g} mm in from each short edge, {x_from_end:g} mm in from each long edge",
        f"             (centres {2 * p.PLATE_BOLT_Z:g} mm apart across, {2 * p.PLATE_BOLT_X:g} mm apart along the run;",
        f"             across-spacing matches the frame rails' top-slot centrelines)",
        "  bearing plates only (tail and head), for the pillow blocks' M4 screws:",
        f"  holes    : 4 x {p.PLATE_PB_HOLE_DIA:g} mm, centres {2 * pb_z:g} mm apart across, {2 * p.PB_BOLT_X:g} mm apart along the run,",
        f"             about the plate centre ({p.PLATE_LENGTH / 2 - pb_z:g} mm in from each short edge,",
        f"             {p.PLATE_WIDTH / 2 - p.PB_BOLT_X:g} mm in from each long edge)",
    ]


def tilt_lines() -> list[str]:
    """The two cut lengths of the tilt mechanism."""
    return [
        "Cross-member  x1",
        f"  material : {p.FRAME_PROFILE:g}{p.FRAME_PROFILE:g} aluminium extrusion",
        f"  length   : {p.XMEMBER_LEN:g} mm, ends square  (fits between the rails' inner faces)",
        "",
        "Prop rod  x1",
        f"  material : M{p.M8_DIA:g} threaded rod",
        f"  length   : {p.ROD_LEN:g} mm  (deburr both ends so the nuts start)",
    ]


def shaft_lines() -> list[str]:
    """The two 8 mm shafts: the head one is longer on its drive end only
    (spec-drive §4), so its flat is not central."""
    tail_to_flat = p.SHAFT_LENGTH / 2 - p.SHAFT_FLAT_LENGTH / 2
    return [
        "Shafts  x2",
        f"  material : {p.SHAFT_DIA:g} mm steel rod",
        f"  tail     : {p.SHAFT_LENGTH:g} mm, flat {p.SHAFT_FLAT_DEPTH:g} deep x {p.SHAFT_FLAT_LENGTH:g} long, centred",
        f"  head     : {p.HEAD_SHAFT_LEN:g} mm, flat {p.SHAFT_FLAT_DEPTH:g} deep x {p.SHAFT_FLAT_LENGTH:g} long, starting",
        f"             {tail_to_flat:g} mm from the non-drive end (not centred); the long end goes to the motor",
    ]


def _polygon_lines(title: str, thickness: float, outline, holes, origin: str, to_cut) -> list[str]:
    """One plywood part as a dimensioned polygon: its corners in order and
    its holes, each mapped by `to_cut` from the part's own 2D frame to
    distances from the corner named in `origin`."""
    corners = [to_cut(a, b) for a, b in outline]
    lines = [title, f"  material : {thickness:g} mm plywood", f"  corners  : in order, mm from {origin}"]
    lines += [f"             ({x:7.1f}, {y:7.1f})" for x, y in corners]
    lines.append("  holes    : diameter at (x, y), same origin")
    lines += [f"             {dia:g} at ({x:7.1f}, {y:7.1f})" for x, y, dia in ((*to_cut(a, b), dia) for a, b, dia in holes)]
    return lines


def hopper_lines() -> list[str]:
    """The hopper's four plywood parts. Every edge is cut square to the
    face; the back wall stands at BACK_WALL_ANGLE to the run, and its top
    and bottom edges are square to its own face."""
    front = p.WALL_THICKNESS   # the panel's front edge, in its own frame
    lines = []
    for side, name in ((1, "+z (right, looking from tail to head)"), (-1, "-z (left)")):
        outline, holes = side_panel_outline(side)
        lines += _polygon_lines(
            f"Hopper side panel {name}  x1", p.PANEL_THICKNESS, outline, holes,
            "the bottom front corner, x back along the bottom edge, y up the front edge, seen from inside",
            lambda a, b: (front - a, b),
        ) + [""]
    lines[-1:] = ["  (the two panels share the outline; only the corner cleat holes differ)", ""]
    bottom = g.back_wall_u(p.SKIRT_GAP)
    outline, holes = back_wall_outline()
    lines += _polygon_lines(
        "Hopper back wall  x1", p.WALL_THICKNESS, outline, holes,
        "the bottom edge's midpoint, x across (to the right seen from the tail end), y up the face",
        lambda a, b: (a, b - bottom),
    ) + [""]
    outline, holes = front_wall_outline()
    lines += _polygon_lines(
        "Hopper front wall  x1", p.WALL_THICKNESS, outline, holes,
        "the bottom edge's midpoint, x across (to the right seen from the tail end), y up the face",
        lambda a, b: (a, b - p.SKIRT_GAP),
    )
    return lines


def skirt_lines() -> list[str]:
    """The two skirt strips (spec-skirts §4.5): mirror images, the
    countersinks on each one's inner (channel) face."""
    lines = [
        "Skirt strips  x2  (one +z, right looking from tail to head; one -z, left; mirror images)",
        f"  material : {p.SKIRT_THICKNESS:g} mm plywood",
        f"  rectangle: {skirt_length():g} x {skirt_height():g} mm  (along the run x height)",
        f"  edge     : {p.SKIRT_EDGE_CHAMFER:g} mm x 45 deg on the bottom long edge of the inner face",
        f"  holes    : {len(skirt_holes())} x {p.M4_CLEARANCE_DIA:g} mm, countersunk {p.M4_CSK_DIA:g} mm x 90 deg from the inner face,",
        "             at (x, y) mm from the tail end (the end against the hopper's front wall) and the bottom edge:",
    ]
    lines += [f"             ({x:6.1f}, {y:5.1f})" for x, y in skirt_holes()]
    lines.append("  the inner face is the one with the chamfer; on the -z strip it faces the other way")
    return lines


def write_cut_list() -> Path:
    OUT_DIR.mkdir(exist_ok=True)
    path = OUT_DIR / "cut_list.txt"
    lines = ["Cut list -- all dimensions mm", ""] + bridge_plate_lines() + [""] + tilt_lines() + [""] + shaft_lines() + [""]
    lines += hopper_lines() + [""] + skirt_lines() + [""]
    path.write_text("\n".join(lines))
    return path


if __name__ == "__main__":
    print(f"wrote {write_cut_list()}")
