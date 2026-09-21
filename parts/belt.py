"""The HTD-3M belt. Bought, reference solids only, never exported
(drivetrain-spec §8).

The assembly needs the belt's position, not its teeth, so `belt_band()` is
what normally goes in; the teeth exist for the mesh check against the
standard pulley groove and, as `belt_loop()`, behind the assembly's detail
flag. Every tooth is `profile.tooth_face()`, placed rigidly: teeth are
stiff, and a belt bends in its lands.

Local frames: `belt_segment()` has the land on y = 0 and is centred on
x = 0 and z = 0. `belt_wrapped()` is about the pulley axis, local z, centred
on local +y like the pulley's own phase datum. `belt_band()` and
`belt_loop()` have the tail shaft axis as local z through the origin and +x
along the run, so placement is `at(0, 0, lateral)`.
"""

import math
import sys
from pathlib import Path

# Allow `python parts/belt.py` to find the project-root modules: Python only
# puts the script's own directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Circle, Face, Part, Pos, Rectangle, Rot, Sketch, extrude

import params as p
from geometry import belt_back_radius, loop_local
from profile import tooth_face


def _solid(section: Sketch | Face) -> Part:
    """A 2D belt section extruded to BELT_WIDTH, centred on z = 0."""
    return extrude(section, amount=p.BELT_WIDTH / 2, both=True)


def _stadium(radius: float) -> Sketch:
    """The outline at `radius` from both shaft axes, tail axis at the origin."""
    return (
        Circle(radius)
        + Pos(p.CENTRE_DIST, 0) * Circle(radius)
        + Rectangle(p.CENTRE_DIST, 2 * radius, align=(Align.MIN, Align.CENTER))
    )


def _band_section() -> Sketch:
    return _stadium(belt_back_radius()) - _stadium(p.PULLEY_OD / 2)


def _tooth_at(s: float) -> Face:
    """One tooth hanging inward from the land at pitch-line distance s."""
    t, offset, turn = loop_local(s, p.PULLEY_OD / 2)
    return Pos(t, offset) * Rot(0, 0, 180.0 - turn) * tooth_face()


def _tooth_stations(teeth: int) -> list[float]:
    """Pitch-line positions of `teeth` teeth, symmetric about zero, a land
    at the centre for an even count to match PULLEY_GROOVE_PHASE."""
    return [(k - (teeth - 1) / 2) * p.BELT_PITCH for k in range(teeth)]


def belt_segment(teeth: int) -> Part:
    """Straight, toothed. Land on y = 0, teeth in -y to -TOOTH_HEIGHT,
    back at +BELT_BACK_THICKNESS. BELT_WIDTH across. For mesh checks."""
    backing = Rectangle(teeth * p.BELT_PITCH, p.BELT_BACK_THICKNESS, align=(Align.CENTER, Align.MIN))
    hanging = [Pos(x, 0) * Rot(0, 0, 180.0) * tooth_face() for x in _tooth_stations(teeth)]
    return _solid(backing + hanging)


def belt_wrapped(teeth: int) -> Part:
    """The same teeth wrapped on the pitch circle as meshed on a pulley,
    centred on local +y. For mesh checks only."""
    pitch_radius = p.PULLEY_PD / 2
    half_wrap = math.degrees(teeth * p.BELT_PITCH / 2 / pitch_radius)
    reach = 2 * belt_back_radius()
    ring = Circle(belt_back_radius()) - Circle(p.PULLEY_OD / 2)
    # keep the sector within half_wrap of +y: cut away the half-plane beyond each end
    for sign in (1, -1):
        ring -= Rot(0, 0, -sign * half_wrap) * Rectangle(
            reach, 2 * reach, align=(Align.MIN if sign > 0 else Align.MAX, Align.CENTER)
        )
    hanging = [
        Rot(0, 0, -math.degrees(s / pitch_radius)) * Pos(0, p.PULLEY_OD / 2) * Rot(0, 0, 180.0) * tooth_face()
        for s in _tooth_stations(teeth)
    ]
    return _solid(ring + hanging)


def belt_band() -> Part:
    """The full loop as backing only, no teeth: land to back, following the
    loop path. For the assembly and for clash checks against slats."""
    return _solid(_band_section())


def belt_loop() -> Part:
    """The full loop with every tooth. Slow to build and to draw; only for
    the assembly's detail flag."""
    count = round(p.BELT_LOOP_LENGTH / p.BELT_PITCH)
    teeth = [_tooth_at((k + 0.5) * p.BELT_PITCH) for k in range(count)]
    return _solid(_band_section() + teeth)


if __name__ == "__main__":
    from ocp_vscode import show

    show(belt_wrapped(8), belt_segment(8).moved(Pos(0, 2 * belt_back_radius(), 0)))
