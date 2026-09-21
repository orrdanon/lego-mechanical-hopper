"""The conveyor slat, in plain and cleated variants.

Modelled in the slat local frame of the CAD spec (S4.4): local origin at the
centre of the belt-contact face, mid-span; +x along the run; +y away from
the belt; +z across the machine.
"""

import sys
from pathlib import Path

# Allow `python parts/slat.py` to find the project-root modules: Python only
# puts the script's own directory on sys.path, not the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Axis, Box, Cylinder, Part, Polygon, Pos, chamfer, extrude, fillet

import params as p
from geometry import belt_back_radius


def _near(value: float, target: float, tol: float = p.EDGE_MATCH_TOLERANCE) -> bool:
    return abs(value - target) < tol


def _body() -> Part:
    body = Box(
        p.SLAT_WIDTH,
        p.SLAT_THICKNESS,
        p.SLAT_LENGTH,
        align=(Align.CENTER, Align.MIN, Align.CENTER),
    )
    top_edges = [
        e for e in body.edges().filter_by(Axis.Z) if _near(e.center().Y, p.SLAT_THICKNESS)
    ]
    end_edges = body.edges().filter_by(Axis.Y)
    return chamfer(top_edges + end_edges, p.EDGE_CHAMFER)


def _tab(z_facing: float, z_far: float) -> Part:
    """One saddle tab with its retention lip.

    `z_facing` is the tab's belt-gripping face (nearer the belt); `z_far` is
    its opposite, outer face.
    """
    z_lo, z_hi = sorted((z_facing, z_far))
    tab = Pos(0, 0, (z_lo + z_hi) / 2) * Box(
        p.SADDLE_TAB_LENGTH,
        p.SADDLE_TAB_DEPTH,
        z_hi - z_lo,
        align=(Align.CENTER, Align.MAX, Align.CENTER),
    )
    lip_dir = 1 if z_facing > z_far else -1
    lip_z_lo, lip_z_hi = sorted((z_facing, z_facing + lip_dir * p.SADDLE_LIP_PROJECTION))
    lip = Pos(0, -p.SADDLE_TAB_DEPTH, (lip_z_lo + lip_z_hi) / 2) * Box(
        p.SADDLE_TAB_LENGTH,
        p.SADDLE_LIP_HEIGHT,
        lip_z_hi - lip_z_lo,
        align=(Align.CENTER, Align.MIN, Align.CENTER),
    )
    return tab + lip


def _saddle_pair(sign: int) -> Part:
    """Both tabs gripping one belt, `sign` selecting which of the two belts."""
    belt_centre = sign * p.BELT_SPACING / 2
    half_gap = (p.BELT_WIDTH - p.SADDLE_INTERFERENCE) / 2

    inner_facing = belt_centre - sign * half_gap
    inner_far = inner_facing - sign * p.SADDLE_TAB_THICKNESS
    outer_facing = belt_centre + sign * half_gap
    outer_far = outer_facing + sign * p.SADDLE_TAB_THICKNESS

    return _tab(inner_facing, inner_far) + _tab(outer_facing, outer_far)


def _saddles() -> Part:
    return _saddle_pair(1) + _saddle_pair(-1)


def _cleat() -> Part:
    half_root = p.CLEAT_WIDTH_ROOT / 2
    half_tip = p.CLEAT_WIDTH_TIP / 2
    profile = Polygon(
        (-half_root, p.SLAT_THICKNESS),
        (half_root, p.SLAT_THICKNESS),
        (half_tip, p.SLAT_THICKNESS + p.CLEAT_HEIGHT),
        (-half_tip, p.SLAT_THICKNESS + p.CLEAT_HEIGHT),
    )
    return extrude(profile, amount=p.CLEAT_LENGTH / 2, both=True)


def _body_with_cleat() -> Part:
    half_root = p.CLEAT_WIDTH_ROOT / 2
    half_tip = p.CLEAT_WIDTH_TIP / 2

    combined = _body() + _cleat()

    root_edges = [
        e
        for e in combined.edges().filter_by(Axis.Z)
        if _near(e.center().Y, p.SLAT_THICKNESS) and _near(abs(e.center().X), half_root)
    ]
    combined = fillet(root_edges, p.CLEAT_ROOT_FILLET)

    tip_edges = [
        e
        for e in combined.edges().filter_by(Axis.Z)
        if _near(e.center().Y, p.SLAT_THICKNESS + p.CLEAT_HEIGHT)
        and _near(abs(e.center().X), half_tip)
    ]
    return chamfer(tip_edges, p.EDGE_CHAMFER)


def slat(cleated: bool = False) -> Part:
    """One conveyor slat, modelled in the slat local frame of S4.4."""
    body = _body_with_cleat() if cleated else _body()
    return body + _saddles()


def pulley_envelope() -> Part:
    """A cylinder representing one pulley's swept volume, positioned in the
    slat local frame as it sits when the slat is at a shaft. Used only for
    clearance checking -- not a manufactured part."""
    radius = p.PULLEY_PD / 2 - p.BELT_PLD
    return Pos(0, -belt_back_radius(), p.BELT_SPACING / 2) * Cylinder(radius, p.PULLEY_FACE_WIDTH)


if __name__ == "__main__":
    from ocp_vscode import show

    show(slat(cleated=False))
