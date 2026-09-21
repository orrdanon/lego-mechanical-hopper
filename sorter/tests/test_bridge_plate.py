"""Phase 4 §8.3 - §8.5 -- the bridge plate and how it sits on the frame."""

from itertools import combinations

import pytest
from pytest import approx

from geometry import at, plate_role, plate_t, plate_top_offset, rail_lateral, rail_top_offset
from params import (
    CENTRE_DIST,
    FRAME_SLOT_DEPTH,
    PLATE_BOLT_CLEARANCE_DIA,
    PLATE_BOLT_X,
    PLATE_BOLT_Z,
    PLATE_LENGTH,
    PLATE_STATIONS,
    PLATE_THICKNESS,
    PLATE_WIDTH,
)
from parts.bridge_plate import bridge_plate
from parts.frame import frame
from utils import bbox_size, clash, contains, volume_cm3


def _placed(i: int):
    return bridge_plate(plate_role(i)).moved(at(plate_t(i), plate_top_offset()))


def test_plate_local_frame():
    p = bridge_plate()
    assert p.is_valid
    assert bbox_size(p) == approx((PLATE_WIDTH, PLATE_THICKNESS, PLATE_LENGTH), abs=0.02)
    bb = p.bounding_box()
    assert bb.max.Y == approx(0.0)              # origin on the top face
    assert bb.min.Y == approx(-PLATE_THICKNESS)


def test_plate_spans_the_rails():
    # Full frame width, so it rests on both rail tops -- see README "Bridge plate length".
    assert bbox_size(bridge_plate())[2] == approx(PLATE_LENGTH, abs=0.02)
    assert PLATE_LENGTH > 2 * rail_lateral()


def test_plate_has_four_clearance_holes():
    p = bridge_plate()
    mid = -PLATE_THICKNESS / 2
    for x in (-PLATE_BOLT_X, PLATE_BOLT_X):
        for z in (-PLATE_BOLT_Z, PLATE_BOLT_Z):
            assert not contains(p, (x, mid, z))
    assert contains(p, (0, mid, 0))
    solid = PLATE_WIDTH * PLATE_THICKNESS * PLATE_LENGTH / 1000
    hole = 3.141592653589793 * (PLATE_BOLT_CLEARANCE_DIA / 2) ** 2 * PLATE_THICKNESS / 1000
    assert volume_cm3(p) == approx(solid - 4 * hole, abs=0.05)


def test_both_roles_share_a_body():
    assert volume_cm3(bridge_plate("bearing")) == approx(volume_cm3(bridge_plate("support")))
    with pytest.raises(ValueError):
        bridge_plate("motor")


def test_plates_sit_on_the_rails():
    f = frame()
    for i in range(PLATE_STATIONS):
        p = _placed(i)
        assert not clash(p, f, tol=1.0)             # no overlap ...
        assert p.distance_to(f) == approx(0.0, abs=0.01)   # ... but touching


def test_bolt_holes_land_in_the_rail_slots():
    # Directly under each plate hole, the rail's top groove must be open.
    f = frame()
    for i in range(PLATE_STATIONS):
        for x in (-PLATE_BOLT_X, PLATE_BOLT_X):
            for z in (-PLATE_BOLT_Z, PLATE_BOLT_Z):
                probe = at(plate_t(i) + x, rail_top_offset() - FRAME_SLOT_DEPTH / 2, lateral=z).position
                assert not contains(f, (probe.X, probe.Y, probe.Z))


@pytest.mark.xfail(
    strict=True,
    reason=(
        f"CENTRE_DIST = {CENTRE_DIST:g} puts {PLATE_STATIONS} plates of PLATE_WIDTH = {PLATE_WIDTH:g} "
        f"at a {CENTRE_DIST / (PLATE_STATIONS - 1):g} mm pitch, so neighbours overlap. "
        "Open layout question, rev C §8 -- resolves itself once CENTRE_DIST is settled."
    ),
)
def test_plates_do_not_collide_with_each_other():
    placed = [_placed(i) for i in range(PLATE_STATIONS)]
    for a, b in combinations(placed, 2):
        assert not clash(a, b)


def test_plates_do_not_collide_with_the_frame_ends():
    f = frame()
    for i in range(PLATE_STATIONS):
        assert not clash(_placed(i), f, tol=1.0)
