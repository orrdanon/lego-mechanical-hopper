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

Every group also takes `takeup`, the slide of the tail bridge plate
(drivetrain-spec §9.3). The assembly is built at takeup 0; the argument
exists for the whole-loop clearance checks.
"""

import sys
from fnmatch import fnmatchcase
from typing import Callable

from build123d import Box, Compound, Pos

import params as p
from geometry import at, is_cleated, loop_at, loop_length, plate_role, plate_t, plate_top_offset, tail_shaft_t
from parts.belt import belt_band, belt_loop
from parts.bridge_plate import bridge_plate
from parts.frame import frame
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


def frame_group(detail: bool = False, takeup: float = 0.0) -> Compound:
    """The aluminium frame, as owned. `detail` and `takeup` are ignored."""
    return frame()


def plates_group(detail: bool = False, takeup: float = 0.0) -> Compound:
    """Five bridge plates at plate_t(0..PLATE_STATIONS-1), each placed with
    at(plate_t(i), plate_top_offset()); the tail plate slides with `takeup`.
    `detail` is ignored."""
    plates = []
    for i in range(p.PLATE_STATIONS):
        role = plate_role(i)
        t = tail_shaft_t(takeup) if i == 0 else plate_t(i)
        plate = bridge_plate(role).moved(at(t, plate_top_offset()))
        plate.label = f"plate {i} ({role})"
        plates.append(plate)
    return _group("plates", plates)


def drivetrain_group(detail: bool = False, takeup: float = 0.0) -> Compound:
    """Two shafts and two shaft sets at at(0, 0) and at(CENTRE_DIST, 0), the
    tail pair sliding with `takeup`. `detail` is ignored."""
    parts = []
    for end, t in (("tail", tail_shaft_t(takeup)), ("head", p.CENTRE_DIST)):
        parts.append(_labelled(shaft().moved(at(t, 0)), f"{end} shaft"))
        parts.append(_labelled(shaft_set().moved(at(t, 0)), f"{end} shaft set"))
    return _group("drivetrain", parts)


def belts_group(detail: bool = False, takeup: float = 0.0) -> Compound:
    """Two belt_band() at z = +/- BELT_SPACING/2. Toothed loops if detail.
    `takeup` is ignored: the belt is modelled at its nominal length."""
    belt = belt_loop() if detail else belt_band()
    return _group("belts", [
        _labelled(belt.moved(at(0, 0, lateral=sign * p.BELT_SPACING / 2)), f"belt {name}")
        for name, sign in (("+z", 1), ("-z", -1))
    ])


def _slat_box(cleated: bool) -> Box:
    """A plain box of the slat's bounding box, in the slat's local frame."""
    bounds = slat(cleated).bounding_box()
    return Pos(*bounds.center()) * Box(*bounds.size)


def slats_group(detail: bool = False, takeup: float = 0.0) -> Compound:
    """46 slats at loop_at(i * SLAT_PITCH), cleated where is_cleated(i).
    Plain boxes of the slat bounding box unless detail. With a takeup the
    slats stay evenly spread round the longer or shorter loop."""
    make = slat if detail else _slat_box
    solids = {cleated: make(cleated) for cleated in (False, True)}
    spread = loop_length(takeup) / p.BELT_LOOP_LENGTH
    return _group("slats", [
        _labelled(solids[is_cleated(i)].moved(loop_at(i * p.SLAT_PITCH * spread, takeup)), f"slat {i}")
        for i in range(p.SLAT_COUNT)
    ])


GROUPS: dict[str, Callable[..., Compound]] = {
    "frame": frame_group,
    "plates": plates_group,
    "drivetrain": drivetrain_group,
    "belts": belts_group,
    "slats": slats_group,
}

# Fixed colour per group, so a group keeps its colour between runs.
COLOURS: dict[str, str] = {
    "frame": "#8a8f98",    # anodised grey
    "plates": "#d9a441",   # plywood amber
    "drivetrain": "#2f6fb5",   # PETG blue
    "belts": "#2b2b2b",    # neoprene black
    "slats": "#e8732a",    # printed orange
}


def _group_of(name: str) -> str:
    """The group part of a 'group' or 'group:pattern' name."""
    return name.partition(":")[0]


def assembly(*names: str, detail: bool = False) -> dict[str, Compound]:
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
        group = GROUPS[_group_of(name)](detail=detail)
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


def show_assembly(*names: str, detail: bool = False) -> None:
    """Build and display, one colour per group, names shown in the tree."""
    from ocp_vscode import show

    built = assembly(*names, detail=detail)
    show(
        *built.values(),
        names=list(built),
        colors=[COLOURS.get(_group_of(name)) for name in built],
    )


def _main(argv: list[str]) -> None:
    detail = "--detail" in argv
    names = [a for a in argv if not a.startswith("--")]
    show_assembly(*names, detail=detail)


if __name__ == "__main__":
    _main(sys.argv[1:])
