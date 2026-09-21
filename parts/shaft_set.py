"""The shaft set: both toothed pulleys and the central guide wheel of one
shaft, printed as one part (drivetrain-spec §5). Two off, identical, head
and tail.

Local frame: z along the shaft axis, which is machine z; x and y radial.
Origin on the axis at the centre plane of the guide groove, which is where
it mates with the shaft and with the slats' lugs, so placement is
`at(0, 0)` for the tail and `at(CENTRE_DIST, 0)` for the head. The part is
symmetric about z = 0, so it goes on the shaft either way round and prints
either end down. A pulley land lies on local +y; the grub screws are along
local +x.
"""

import math
import sys
from functools import cache
from pathlib import Path

# Allow `python parts/shaft_set.py` to find the project-root modules: Python
# only puts the script's own directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Axis, Cylinder, Location, Part, Plane, Polygon, Pos, Rot, extrude, revolve

import params as p
from geometry import belt_back_radius, guide_rim_radius
from profile import pulley_section


def _cone_run(step: float) -> float:
    """Axial length of a SHAFTSET_CONE_ANGLE cone climbing `step` in radius."""
    return step / math.tan(math.radians(p.SHAFTSET_CONE_ANGLE))


def _revolved(points: list[tuple[float, float]]) -> Part:
    """Revolve an (r, z) outline about the local z axis."""
    return revolve(Plane.XZ * Polygon(*points, align=None), Axis.Z)


def _mirrored(half: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """An (r, z) outline for z >= 0, running outward from the axis, closed
    through its mirror image in z = 0."""
    return half + [(r, -z) for r, z in reversed(half)]


def _core() -> Part:
    """Guide wheel, wheel chamfer, drum and flare (drivetrain-spec §5.3),
    out to the inner face of each pulley. No teeth, groove or bore yet."""
    rim = guide_rim_radius()
    drum = p.DRUM_DIA / 2
    wheel_z = p.GUIDE_WIDTH / 2
    drum_z = wheel_z + _cone_run(rim - drum)
    pulley_z = p.BELT_SPACING / 2 - p.PULLEY_FACE_WIDTH / 2
    flare_z = pulley_z - _cone_run(p.PULLEY_SKIRT_R - drum)
    return _revolved(_mirrored([
        (0.0, pulley_z),
        (p.PULLEY_SKIRT_R, pulley_z),
        (drum, flare_z),
        (drum, drum_z),
        (rim, wheel_z),
    ]))


def _pulley(sign: int) -> Part:
    """One toothed pulley zone, on the +z or -z end: pulley_section()
    extruded across PULLEY_FACE_WIDTH, with END_CHAMFER on the outer edge
    of its end face. The chamfer is cut by intersecting with a coned
    envelope, so it breaks the lands and leaves the groove walls vertical."""
    inner_z = p.BELT_SPACING / 2 - p.PULLEY_FACE_WIDTH / 2
    outer_z = p.SHAFTSET_LENGTH / 2
    od = (p.PULLEY_OD - p.PULLEY_OD_COMP) / 2
    teeth = Pos(0, 0, inner_z) * extrude(pulley_section(), amount=p.PULLEY_FACE_WIDTH)
    envelope = _revolved([
        (0.0, inner_z),
        (od, inner_z),
        (od, outer_z - p.END_CHAMFER),
        (od - p.END_CHAMFER, outer_z),
        (0.0, outer_z),
    ])
    pulley = teeth & envelope
    return pulley if sign > 0 else pulley.mirror(Plane.XY)


def guide_groove(flank_clear: float = p.GROOVE_FLANK_CLEAR, tip_clear: float = p.GROOVE_TIP_CLEAR) -> Part:
    """The V-groove's cutter (drivetrain-spec §5.5): the lug's cross-section
    offset outward by `flank_clear` normal to each flank and deepened by
    `tip_clear`, revolved about the axis. It overshoots the rim."""
    half_angle = math.radians(p.LUG_ANGLE / 2)
    bottom = belt_back_radius() - p.LUG_DEPTH - tip_clear
    top = belt_back_radius()
    shift = flank_clear / math.cos(half_angle)   # a normal offset, measured across the machine

    def half_width(r: float) -> float:
        lug = p.LUG_TIP_WIDTH / 2 + (r - (belt_back_radius() - p.LUG_DEPTH)) * math.tan(half_angle)
        return lug + shift

    return _revolved([
        (bottom, -half_width(bottom)),
        (top, -half_width(top)),
        (top, half_width(top)),
        (bottom, half_width(bottom)),
    ])


def bore(length: float = p.SHAFTSET_LENGTH) -> Part:
    """The through bore's cutter, PULLEY_BORE + PULLEY_BORE_CLEARANCE, with
    PULLEY_BORE_CHAMFER at each end of a part `length` long centred on z = 0."""
    r = (p.PULLEY_BORE + p.PULLEY_BORE_CLEARANCE) / 2
    end = length / 2
    return _revolved(_mirrored([
        (0.0, end),
        (r + p.PULLEY_BORE_CHAMFER, end),
        (r, end - p.PULLEY_BORE_CHAMFER),
    ]))


def _grub(z: float) -> Part:
    """One grub screw's cutter, radial along local +x at height z: the
    heat-set insert pocket sunk PULLEY_INSERT_DEPTH into the drum, then M4
    clearance through to the bore."""
    drum = p.DRUM_DIA / 2
    pocket_floor = drum - p.PULLEY_INSERT_DEPTH
    pocket = Cylinder(p.PULLEY_INSERT_DIA / 2, guide_rim_radius() - pocket_floor)
    through = Cylinder(p.PULLEY_GRUB_CLEARANCE_DIA / 2, pocket_floor)
    along_x = Rot(0, 90, 0)
    return (
        Pos((guide_rim_radius() + pocket_floor) / 2, 0, z) * along_x * pocket
        + Pos(pocket_floor / 2, 0, z) * along_x * through
    )


@cache
def _build(flank_clear: float, tip_clear: float) -> Part:
    body = _core() + _pulley(1) + _pulley(-1)
    body -= guide_groove(flank_clear, tip_clear)
    body -= bore()
    body -= _grub(p.GRUB_Z) + _grub(-p.GRUB_Z)
    return body


def shaft_set_with(
    groove_flank_clear: float = p.GROOVE_FLANK_CLEAR,
    groove_tip_clear: float = p.GROOVE_TIP_CLEAR,
) -> Part:
    """shaft_set() with the guide groove's clearances overridden. Exists for
    the negative control of the lug-in-groove check (drivetrain-spec §12.5)."""
    # The solid is cached; moved() hands each caller its own wrapper.
    return _build(groove_flank_clear, groove_tip_clear).moved(Location())


def shaft_set() -> Part:
    """Two pulleys and a guide wheel, one printed part. See the module
    docstring for the local frame."""
    return shaft_set_with()


if __name__ == "__main__":
    from ocp_vscode import show

    show(shaft_set())
