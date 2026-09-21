"""The aluminium 2020 frame -- owned hardware, not a printed part.

A reference solid: modelled so other things can be positioned against it
and clash-tested, never exported as STL.

`rail()` follows the local-frame rule (phase 4 §2.3): origin at the centre
of the top face, length along local x, FRAME_PROFILE along local z, and the
body extending FRAME_PROFILE into -y.

`frame()` is the one exception to rule 2.2 ("parts hold no positions"): it
returns a Compound already positioned in the machine frame, because the
frame *is* a fixed piece of the world rather than a repeatable part, and
there is exactly one of it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Compound, Part, Pos, Rot

import params as p
from geometry import at, frame_t_centre, frame_t_end, rail_lateral, rail_top_offset


def _slot(length: float) -> Part:
    """A cosmetic T-slot groove: RAIL_SLOT_WIDTH wide, RAIL_SLOT_DEPTH deep,
    running the full length along local x, centred on the origin."""
    return Box(length, p.FRAME_SLOT_DEPTH, p.FRAME_SLOT_WIDTH)


def rail(length: float) -> Part:
    """A length of 2020 extrusion. Local origin at the centre of the top
    face; length along local x, FRAME_PROFILE along local z, extending
    FRAME_PROFILE into negative local y.

    Modelled as a plain square prism with a rectangular groove centred on
    each of the four long faces. The grooves are cosmetic -- they show
    which faces take T-nuts -- and the internal T profile is not modelled.
    """
    half = p.FRAME_PROFILE / 2
    body = Box(length, p.FRAME_PROFILE, p.FRAME_PROFILE, align=(Align.CENTER, Align.MAX, Align.CENTER))
    depth = p.FRAME_SLOT_DEPTH / 2
    grooves = [
        Pos(0.0, -depth, 0.0) * _slot(length),                      # top face  (y = 0)
        Pos(0.0, -p.FRAME_PROFILE + depth, 0.0) * _slot(length),    # bottom    (y = -20)
        Pos(0.0, -half, half - depth) * Rot(90.0, 0.0, 0.0) * _slot(length),    # +z side
        Pos(0.0, -half, -half + depth) * Rot(90.0, 0.0, 0.0) * _slot(length),   # -z side
    ]
    return body - grooves


def frame() -> Compound:
    """The complete rectangle: two rails of FRAME_LENGTH at
    lateral = +/- rail_lateral(), and two end members of FRAME_END_LENGTH
    spanning between them at each end. All four top faces are coplanar at
    rail_top_offset().

    Exception to phase 4 rule 2.2: this Compound is returned already
    positioned in the machine frame (see module docstring).
    """
    long_rail = rail(p.FRAME_LENGTH)
    # An end member is the same rail with its length turned to run along
    # local z: rotate 90 degrees about local y inside the local frame.
    end_member = Rot(0.0, 90.0, 0.0) * rail(p.FRAME_END_LENGTH)

    inset = p.FRAME_PROFILE / 2   # end members sit just inside the rail ends
    members = [
        ("rail +z", long_rail.moved(at(frame_t_centre(), rail_top_offset(), lateral=rail_lateral()))),
        ("rail -z", long_rail.moved(at(frame_t_centre(), rail_top_offset(), lateral=-rail_lateral()))),
        ("end tail", end_member.moved(at(p.FRAME_T_START + inset, rail_top_offset()))),
        ("end head", end_member.moved(at(frame_t_end() - inset, rail_top_offset()))),
    ]
    children = []
    for label, solid in members:
        solid.label = label
        children.append(solid)
    result = Compound(children=children)
    result.label = "frame"
    return result


if __name__ == "__main__":
    from ocp_vscode import show

    show(frame())
