"""The machine assembly: what goes where.

Top of the four-layer stack (phase 4 §2.1). This module is the only place
that combines parts with positions from `geometry`. Each named *group* is a
function returning a Compound already placed in the machine frame, and
`GROUPS` is the extension point: a later phase adds a group function and
one `GROUPS` entry, and nothing else in the project changes.

Usage:

    python assembly.py                 # everything
    python assembly.py frame           # just the frame
    python assembly.py frame plates    # both
    python assembly.py plates --detail
    python assembly.py frame plates drivetrain belts slats
    python assembly.py "drivetrain:tail shaft" "drivetrain:tail shaft set"
    python assembly.py drivetrain belts "slats:slat ?" --detail   # slats 0-9 only
    python assembly.py --incline=55    # tilted; INCLINE if not given
    python assembly.py --report        # what is in each group, and the tilt's bought hardware

Every group also takes `takeup`, the slide of the tail bridge plate
(drivetrain-spec §9.3), and `incline` (spec-tilt §2.1). The assembly is
built at takeup 0; that argument exists for the whole-loop clearance checks.
"""

import sys
from fnmatch import fnmatchcase
from typing import Callable

from build123d import Box, Compound, Location, Pos

import params as p
from geometry import (
    at, base_frame, is_cleated, loop_at, loop_length, plate_role, plate_t, plate_top_offset, prop_body_frame,
    prop_foot_frame, prop_length, rail_top_offset, tail_shaft_t,
)
from parts.base_ref import base_ref
from parts.belt import belt_band, belt_loop
from parts.bridge_plate import bridge_plate
from parts.frame import cross_member, frame
from parts.hardware import hex_nut, pin_bolt, threaded_rod, washer
from parts.hinge import hinge_block, hinge_bracket
from parts.prop import base_pin_block, frame_clevis, knob, prop_body, prop_foot
from parts.shaft import shaft
from parts.shaft_set import shaft_set
from parts.slat import slat


def _group(label: str, children: list) -> Compound:
    group = Compound(children=children)
    group.label = label
    return group


def _labelled(part, label: str):
    part.label = label
    return part


def frame_group(detail: bool = False, takeup: float = 0.0, incline: float = p.INCLINE) -> Compound:
    """The aluminium frame, as owned. `detail` and `takeup` are ignored."""
    return frame(incline)


def plates_group(detail: bool = False, takeup: float = 0.0, incline: float = p.INCLINE) -> Compound:
    """Five bridge plates at plate_t(0..PLATE_STATIONS-1), each placed with
    at(plate_t(i), plate_top_offset()); the tail plate slides with `takeup`.
    `detail` is ignored."""
    plates = []
    for i in range(p.PLATE_STATIONS):
        role = plate_role(i)
        t = tail_shaft_t(takeup) if i == 0 else plate_t(i)
        plate = bridge_plate(role).moved(at(t, plate_top_offset(), incline=incline))
        plate.label = f"plate {i} ({role})"
        plates.append(plate)
    return _group("plates", plates)


def drivetrain_group(detail: bool = False, takeup: float = 0.0, incline: float = p.INCLINE) -> Compound:
    """Two shafts and two shaft sets at at(0, 0) and at(CENTRE_DIST, 0), the
    tail pair sliding with `takeup`. `detail` is ignored."""
    parts = []
    for end, t in (("tail", tail_shaft_t(takeup)), ("head", p.CENTRE_DIST)):
        parts.append(_labelled(shaft().moved(at(t, 0, incline=incline)), f"{end} shaft"))
        parts.append(_labelled(shaft_set().moved(at(t, 0, incline=incline)), f"{end} shaft set"))
    return _group("drivetrain", parts)


def belts_group(detail: bool = False, takeup: float = 0.0, incline: float = p.INCLINE) -> Compound:
    """Two belt_band() at z = +/- BELT_SPACING/2. Toothed loops if detail.
    `takeup` is ignored: the belt is modelled at its nominal length."""
    belt = belt_loop() if detail else belt_band()
    return _group("belts", [
        _labelled(belt.moved(at(0, 0, sign * p.BELT_SPACING / 2, incline)), f"belt {name}")
        for name, sign in (("+z", 1), ("-z", -1))
    ])


def _slat_box(cleated: bool) -> Box:
    """A plain box of the slat's bounding box, in the slat's local frame."""
    bounds = slat(cleated).bounding_box()
    return Pos(*bounds.center()) * Box(*bounds.size)


def slats_group(detail: bool = False, takeup: float = 0.0, incline: float = p.INCLINE) -> Compound:
    """46 slats at loop_at(i * SLAT_PITCH), cleated where is_cleated(i).
    Plain boxes of the slat bounding box unless detail. With a takeup the
    slats stay evenly spread round the longer or shorter loop."""
    make = slat if detail else _slat_box
    solids = {cleated: make(cleated) for cleated in (False, True)}
    spread = loop_length(takeup) / p.BELT_LOOP_LENGTH
    return _group("slats", [
        _labelled(solids[is_cleated(i)].moved(loop_at(i * p.SLAT_PITCH * spread, takeup, incline)), f"slat {i}")
        for i in range(p.SLAT_COUNT)
    ])


def tilt_frame_parts(incline: float = p.INCLINE) -> list:
    """The tilt parts that move with the frame: hinge brackets and their
    pins, cross-member, frame clevis and pin A."""
    parts = [
        _labelled(cross_member().moved(at(p.XMEMBER_T, rail_top_offset(), incline=incline)), "cross-member"),
        _labelled(frame_clevis().moved(at(p.XMEMBER_T, p.RAIL_UNDERSIDE_OFFSET, incline=incline)), "frame clevis"),
    ]
    cheek = p.CLEVIS_GAP / 2 + p.CLEVIS_CHEEK_THK
    pin_a = at(p.PROP_PIN_A_T, p.PROP_PIN_A_OFFSET, cheek, incline) * Location((0, 0, 0), (180, 0, 0))
    parts.append(_labelled(pin_bolt(2 * cheek).moved(pin_a), "pin A"))
    grip = p.HINGE_BRKT_THK - p.HINGE_HEAD_POCKET_DEPTH + p.HINGE_GAP + p.HINGE_BLOCK_THK
    for name, side in (("+z", 1), ("-z", -1)):
        face = at(p.HINGE_T, p.HINGE_OFFSET, side * p.FRAME_WIDTH / 2, incline)
        turn = Location((0, 0, 0), (0 if side == 1 else 180, 0, 0))
        parts.append(hinge_bracket(side).moved(face))
        parts.append(_labelled(pin_bolt(grip).moved(face * Pos(0, 0, side * p.HINGE_HEAD_POCKET_DEPTH) * turn), f"hinge pin {name}"))
    return parts


def tilt_base_parts(incline: float = p.INCLINE) -> list:
    """The tilt parts that stay on the base: hinge blocks, base pin block
    and pin B, and the base reference slab, which is a placeholder."""
    base = base_frame(incline)
    inner = p.FRAME_WIDTH / 2 + p.HINGE_BRKT_THK + p.HINGE_GAP
    cheek = p.PIN_BLOCK_GAP / 2 + p.PIN_BLOCK_CHEEK_THK
    pin_b = base * Location((p.PROP_PIN_B_X, p.PROP_PIN_B_Y, cheek), (180, 0, 0))
    return [
        hinge_block(1).moved(base * Pos(0, 0, inner)),
        hinge_block(-1).moved(base * Pos(0, 0, -inner)),
        base_pin_block().moved(base * Pos(p.PROP_PIN_B_X, 0, 0)),
        _labelled(pin_bolt(2 * cheek).moved(pin_b), "pin B"),
        base_ref().moved(base),
    ]


def tilt_prop_parts(incline: float = p.INCLINE, pin_b_x: float = p.PROP_PIN_B_X) -> list:
    """The prop, along the line from pin B to pin A. The rod does not slide
    in the foot, so everything but the body and its lock nut sits at a fixed
    height on the foot; the body's place is set by prop_length().
    `pin_b_x` is for the prop-clearance negative control."""
    foot = prop_foot_frame(incline, pin_b_x)
    body_bottom = prop_length(incline, pin_b_x) - p.PROP_BODY_LEN
    knob_z = p.FOOT_LEN + p.M8_WASHER_THK
    nuts_top = p.FOOT_LEN - p.FOOT_WALL_THK - p.FOOT_POCKET_PLAY
    on_foot = [
        (prop_foot(), 0.0, "prop foot"),
        (threaded_rod(), p.ROD_BOTTOM_Z, "prop rod"),
        (hex_nut(), nuts_top - 2 * p.M8_NUT_THK, "foot nut lower"),
        (hex_nut(), nuts_top - p.M8_NUT_THK, "foot nut upper"),
        (washer(), p.FOOT_LEN, "knob washer"),
        (knob(), knob_z, "knob"),
        (hex_nut(), knob_z + p.KNOB_THK - p.NUT_POCKET_DEPTH, "knob nut"),
        (hex_nut(), knob_z + p.KNOB_THK, "jam nut"),
        (hex_nut(), body_bottom - p.M8_NUT_THK, "lock nut"),
        (hex_nut(), body_bottom + p.PROP_NUT_TOP - p.M8_NUT_THK, "body nut"),
    ]
    parts = [_labelled(part.moved(foot * Pos(0, 0, z)), label) for part, z, label in on_foot]
    parts.append(prop_body().moved(prop_body_frame(incline, pin_b_x)))
    return parts


def tilt_group(detail: bool = False, takeup: float = 0.0, incline: float = p.INCLINE) -> Compound:
    """The hinge, cross-member, clevis, prop and base (spec-tilt §8.1).
    `detail` is ignored, and so is `takeup`: the hinge is fixed to the
    frame, not to the tail plate."""
    return _group("tilt", tilt_frame_parts(incline) + tilt_base_parts(incline) + tilt_prop_parts(incline))


GROUPS: dict[str, Callable[..., Compound]] = {
    "frame": frame_group,
    "plates": plates_group,
    "drivetrain": drivetrain_group,
    "belts": belts_group,
    "slats": slats_group,
    "tilt": tilt_group,
}

# Fixed colour per group, so a group keeps its colour between runs.
COLOURS: dict[str, str] = {
    "frame": "#8a8f98",    # anodised grey
    "plates": "#d9a441",   # plywood amber
    "drivetrain": "#2f6fb5",   # PETG blue
    "belts": "#2b2b2b",    # neoprene black
    "slats": "#e8732a",    # printed orange
    "tilt": "#3f9b6d",     # printed green
}

# Members shown in a colour of their own, and flagged in the report.
PLACEHOLDERS: dict[str, str] = {
    "base_ref": "#b9b4a8",   # muted: the base is OPEN, this is only its top plane
}


def _group_of(name: str) -> str:
    """The group part of a 'group' or 'group:pattern' name."""
    return name.partition(":")[0]


def assembly(*names: str, detail: bool = False, incline: float = p.INCLINE) -> dict[str, Compound]:
    """Build the named groups, or every group if none are named.
    Returns a mapping so the viewer can name and colour them.

    A name is a group, or 'group:pattern' for only the members of that
    group whose label matches the glob pattern -- 'drivetrain:tail shaft',
    'drivetrain:*shaft set', 'slats:slat 1?'. Unknown groups, and patterns
    matching nothing, raise ValueError listing the valid ones."""
    wanted = names or tuple(GROUPS)
    unknown = [n for n in wanted if _group_of(n) not in GROUPS]
    if unknown:
        raise ValueError(
            f"unknown group(s) {unknown}; valid groups are {sorted(GROUPS)}"
        )
    built = {}
    for name in wanted:
        group = GROUPS[_group_of(name)](detail=detail, incline=incline)
        pattern = name.partition(":")[2]
        if pattern:
            members = [child for child in group.children if fnmatchcase(child.label, pattern)]
            if not members:
                raise ValueError(
                    f"nothing in {_group_of(name)!r} matches {pattern!r}; "
                    f"its members are {[child.label for child in group.children]}"
                )
            group = Compound(children=members)
        group.label = name
        built[name] = group
    return built


def show_assembly(*names: str, detail: bool = False, incline: float = p.INCLINE) -> None:
    """Build and display, one colour per group, names shown in the tree.
    Placeholders are split out and shown in their own muted colour."""
    from ocp_vscode import show

    shown, shown_names, colours = [], [], []
    for name, group in assembly(*names, detail=detail, incline=incline).items():
        real = [child for child in group.children if child.label not in PLACEHOLDERS]
        if real:
            shown.append(Compound(children=real))
            shown_names.append(name)
            colours.append(COLOURS.get(_group_of(name)))
        for child in group.children:
            if child.label in PLACEHOLDERS:
                shown.append(child)
                shown_names.append(f"{name}:{child.label} (placeholder)")
                colours.append(PLACEHOLDERS[child.label])
    show(*shown, names=shown_names, colors=colours)


def report(incline: float = p.INCLINE) -> list[str]:
    """What is in each group, with placeholders flagged, and the bought
    hardware for the tilt (spec-tilt §6, §7) -- the project has no BOM."""
    lines = [f"Assembly at incline {incline:g} deg, prop {prop_length(incline):.1f} pin to pin", ""]
    for name, group in assembly(incline=incline).items():
        lines.append(f"{name} ({len(group.children)})")
        labels = [child.label for child in group.children]
        if len(labels) < p.SLAT_COUNT:
            lines += [
                f"  {label}" + ("   ** PLACEHOLDER: the base is open, not a part **" if label in PLACEHOLDERS else "")
                for label in labels
            ]
        else:
            lines.append(f"  {labels[0]} .. {labels[-1]}")
    lines += ["", "Bought hardware, tilt"]
    lines += [f"  {quantity:>2} x {item:40s} {use}" for item, quantity, use in p.TILT_HARDWARE]
    return lines


def _main(argv: list[str]) -> None:
    detail = "--detail" in argv
    incline = p.INCLINE
    for arg in argv:
        if arg.startswith("--incline="):
            incline = float(arg.partition("=")[2])
    if "--report" in argv:
        print("\n".join(report(incline)))
        return
    names = [a for a in argv if not a.startswith("--")]
    show_assembly(*names, detail=detail, incline=incline)


if __name__ == "__main__":
    _main(sys.argv[1:])
