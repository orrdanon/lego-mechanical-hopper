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
"""

import sys
from typing import Callable

from build123d import Compound

import params as p
from geometry import at, plate_role, plate_t, plate_top_offset
from parts.bridge_plate import bridge_plate
from parts.frame import frame


def frame_group(detail: bool = False) -> Compound:
    """The aluminium frame, as owned. `detail` is ignored."""
    return frame()


def plates_group(detail: bool = False) -> Compound:
    """Five bridge plates at plate_t(0..PLATE_STATIONS-1), each placed with
    at(plate_t(i), plate_top_offset()). `detail` is ignored."""
    plates = []
    for i in range(p.PLATE_STATIONS):
        role = plate_role(i)
        plate = bridge_plate(role).moved(at(plate_t(i), plate_top_offset()))
        plate.label = f"plate {i} ({role})"
        plates.append(plate)
    group = Compound(children=plates)
    group.label = "plates"
    return group


GROUPS: dict[str, Callable[..., Compound]] = {
    "frame": frame_group,
    "plates": plates_group,
}

# Fixed colour per group, so a group keeps its colour between runs.
COLOURS: dict[str, str] = {
    "frame": "#8a8f98",    # anodised grey
    "plates": "#d9a441",   # plywood amber
}


def assembly(*names: str, detail: bool = False) -> dict[str, Compound]:
    """Build the named groups, or every group if none are named.
    Returns a mapping so the viewer can name and colour them.
    Unknown names raise ValueError listing the valid ones."""
    wanted = names or tuple(GROUPS)
    unknown = [n for n in wanted if n not in GROUPS]
    if unknown:
        raise ValueError(
            f"unknown group(s) {unknown}; valid groups are {sorted(GROUPS)}"
        )
    built = {}
    for name in wanted:
        group = GROUPS[name](detail=detail)
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
        colors=[COLOURS.get(name) for name in built],
    )


def _main(argv: list[str]) -> None:
    detail = "--detail" in argv
    names = [a for a in argv if not a.startswith("--")]
    show_assembly(*names, detail=detail)


if __name__ == "__main__":
    _main(sys.argv[1:])
