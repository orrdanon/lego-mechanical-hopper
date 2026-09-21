"""drivetrain-spec §12.3 -- the shaft set, plus the shaft (§7) and the two
coupons (§10) that are made from the same functions."""

from pytest import approx

import params as p
from geometry import guide_rim_radius
from parts.coupons import guide_coupon, ring_coupon
from parts.shaft import shaft
from parts.shaft_set import shaft_set
from utils import bbox_size, clash, contains, volume_cm3


def test_shaft_set_is_valid_and_one_solid():
    ss = shaft_set()
    assert ss.is_valid
    assert len(ss.solids()) == 1


def test_shaft_set_bbox():
    assert bbox_size(shaft_set()) == approx((38.894, 38.894, 59.0), abs=0.05)
    assert bbox_size(shaft_set())[0] == approx(2 * guide_rim_radius(), abs=0.02)   # the wheel rim sets it


def test_shaft_set_volume():
    assert 38.0 <= volume_cm3(shaft_set()) <= 52.0


def test_insert_pocket_leaves_a_wall_over_the_bore():
    bore_radius = (p.PULLEY_BORE + p.PULLEY_BORE_CLEARANCE) / 2
    assert p.PULLEY_INSERT_DEPTH <= p.DRUM_DIA / 2 - bore_radius - p.PULLEY_INSERT_MIN_WALL


def test_shaft_set_envelope_is_derived_as_tabulated():
    """drivetrain-spec §5.3's zone boundaries."""
    assert p.SHAFTSET_LENGTH == approx(59.0)
    assert contains(shaft_set(), (0, 12.9, 17.5)) and not contains(shaft_set(), (0, 13.1, 17.5))    # drum at 13.0
    assert contains(shaft_set(), (0, 16.7, 24.4)) and not contains(shaft_set(), (0, 16.9, 24.4))    # flare tops out at 16.8
    assert contains(shaft_set(), (0, 16.0, 11.3)) and not contains(shaft_set(), (0, 16.3, 11.5))    # 45 deg wheel chamfer


def test_shaft_set_probe_points():
    ss = shaft_set()
    assert contains(ss, (0, 14.0, 0))          # wheel, below the groove
    assert not contains(ss, (0, 17.0, 0))      # inside the guide groove
    assert contains(ss, (0, 19.0, 7.0))        # wheel rim land beside the groove
    assert not contains(ss, (0, 14.0, 17.5))   # tab running zone, outside drum
    assert contains(ss, (0, 18.5, 27.0))       # pulley land, on +y by phase
    assert not contains(ss, (1.3966, 17.7451, 27.0))   # pulley groove, r 17.8 at 4.5 deg
    assert contains(ss, (1.3573, 17.2467, 27.0))       # below groove bottom, r 17.3
    assert not contains(ss, (0, 3.9, 0))       # bore


def test_both_pulleys_are_in_phase():
    ss = shaft_set()
    for z in (27.0, -27.0):
        assert contains(ss, (0, 18.5, z))
        assert not contains(ss, (1.3966, 17.7451, z))
        assert not contains(ss, (-1.3966, 17.7451, z))


def test_grub_screws_are_along_plus_x_in_both_planes():
    ss = shaft_set()
    for z in (p.GRUB_Z, -p.GRUB_Z):
        assert not contains(ss, (10.0, 0, z))   # insert pocket
        assert not contains(ss, (5.5, 0, z))    # clearance through to the bore
        assert contains(ss, (-10.0, 0, z))      # nothing opposite
        assert contains(ss, (0, 10.0, z))


def test_end_faces_are_chamfered():
    ss = shaft_set()
    assert contains(ss, (0, 18.6, 29.0), eps=0.01)
    assert not contains(ss, (0, 18.6, 29.45), eps=0.01)   # END_CHAMFER breaks the land's outer edge
    assert not contains(ss, (0, 4.3, 29.4), eps=0.01)     # bore chamfer
    assert contains(ss, (0, 4.6, 29.4), eps=0.01)


def test_shaft_set_is_symmetric_about_its_centre_plane():
    ss = shaft_set()
    box = ss.bounding_box()
    assert box.min.Z == approx(-box.max.Z, abs=1e-6)
    assert ss.center().Z == approx(0.0, abs=1e-3)


# --- Shaft ---------------------------------------------------------------------


def test_shaft():
    s = shaft()
    assert s.is_valid
    assert bbox_size(s) == approx((p.SHAFT_DIA, p.SHAFT_DIA, p.SHAFT_LENGTH), abs=0.02)


def test_shaft_flat_faces_plus_x_under_both_grubs():
    s = shaft()
    assert not contains(s, (3.8, 0, 0)) and contains(s, (-3.8, 0, 0))
    assert not contains(s, (3.8, 0, p.GRUB_Z)) and not contains(s, (3.8, 0, -p.GRUB_Z))
    assert contains(s, (3.8, 0, 30.0))      # the flat is 45 long, ends at +/-22.5
    assert p.SHAFT_FLAT_LENGTH / 2 > p.GRUB_Z


def test_shaft_runs_in_the_bore():
    assert not clash(shaft(), shaft_set())


# --- Coupons ---------------------------------------------------------------------


def test_ring_coupon():
    ring = ring_coupon()
    assert ring.is_valid
    assert bbox_size(ring) == approx((p.PULLEY_OD, p.PULLEY_OD, 3.0), abs=0.02)
    assert contains(ring, (0, 18.5, 0))                    # a land on +y, the same phase as the pulley
    assert not contains(ring, (1.3966, 17.7451, 0))        # a real groove
    assert not contains(ring, (0, 3.9, 0))                 # bore


def test_guide_coupon_is_the_guide_wheel_zone():
    guide = guide_coupon()
    assert guide.is_valid
    assert bbox_size(guide) == approx((38.894, 38.894, p.GUIDE_WIDTH), abs=0.05)
    for point in ((0, 14.0, 0), (0, 17.0, 0), (0, 19.0, 7.0), (0, 3.9, 0)):
        assert contains(guide, point) == contains(shaft_set(), point)
