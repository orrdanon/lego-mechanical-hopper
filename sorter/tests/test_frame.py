"""Phase 4 §8.2 -- the aluminium frame reference solid."""

import math

from pytest import approx

from geometry import at, frame_t_centre, rail_lateral, rail_top_offset
from params import FRAME_END_LENGTH, FRAME_LENGTH, FRAME_PROFILE, FRAME_SLOT_DEPTH, FRAME_T_START, FRAME_WIDTH, INCLINE
from parts.frame import frame, rail
from utils import bbox_size, contains


def test_rail_local_frame():
    r = rail(FRAME_END_LENGTH)
    assert r.is_valid
    assert bbox_size(r) == approx((FRAME_END_LENGTH, FRAME_PROFILE, FRAME_PROFILE), abs=0.02)
    bb = r.bounding_box()
    assert bb.max.Y == approx(0.0)                 # origin on the top face
    assert bb.min.Y == approx(-FRAME_PROFILE)      # body extends into -y
    assert bb.min.X == approx(-FRAME_END_LENGTH / 2)


def test_rail_has_a_groove_on_each_face():
    r = rail(100.0)
    half = FRAME_PROFILE / 2
    inside = FRAME_SLOT_DEPTH / 2
    assert not contains(r, (0, -inside, 0))                    # top groove
    assert not contains(r, (0, -FRAME_PROFILE + inside, 0))    # bottom groove
    assert not contains(r, (0, -half, half - inside))          # +z side groove
    assert not contains(r, (0, -half, -half + inside))         # -z side groove
    assert contains(r, (0, -half, 0))                          # solid core


def test_frame_is_valid_with_four_solids():
    f = frame()
    assert f.is_valid
    assert len(f.solids()) == 4


def test_frame_longest_extent_is_the_inclined_projection():
    # The frame is inclined, so its axis-aligned box is not FRAME_LENGTH long
    # (phase 4 §8.2 assumed it was -- see README "Frame bounding box").
    theta = math.radians(INCLINE)
    expected_x = FRAME_LENGTH * math.cos(theta) + FRAME_PROFILE * math.sin(theta)
    bb = bbox_size(frame())
    assert sorted(bb)[-1] == approx(expected_x, abs=0.5)
    assert bb[2] == approx(FRAME_WIDTH, abs=0.02)


def test_frame_in_its_own_local_frame():
    # Undo the placement of the frame's midpoint and the box is exact.
    local = frame().moved(at(frame_t_centre(), rail_top_offset()).inverse())
    assert bbox_size(local) == approx((FRAME_LENGTH, FRAME_PROFILE, FRAME_WIDTH), abs=0.02)
    bb = local.bounding_box()
    assert bb.max.Y == approx(0.0, abs=0.01)            # all four top faces coplanar
    assert bb.min.X == approx(-FRAME_LENGTH / 2, abs=0.01)


def test_frame_rails_and_end_members_are_where_geometry_says():
    local = frame().moved(at(frame_t_centre(), rail_top_offset()).inverse())
    half = FRAME_PROFILE / 2
    assert contains(local, (0, -half, rail_lateral()))
    assert contains(local, (0, -half, -rail_lateral()))
    assert contains(local, (-FRAME_LENGTH / 2 + half, -half, 0))    # tail end member
    assert contains(local, (FRAME_LENGTH / 2 - half, -half, 0))     # head end member
    assert not contains(local, (0, -half, 0))                       # open in the middle
