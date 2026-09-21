from pytest import approx

from export import export_all
from parts.slat import pulley_envelope, slat
from utils import bbox_size, clash, contains, volume_cm3


def test_plain_bbox():
    assert bbox_size(slat(False)) == approx((17.0, 7.0, 80.0), abs=0.02)   # the 4.0 lug now sets the depth


def test_cleated_bbox():
    assert bbox_size(slat(True)) == approx((17.0, 19.0, 80.0), abs=0.02)


def test_plain_volume():
    assert 4.20 <= volume_cm3(slat(False)) <= 4.90   # recomputed for the lug, the 3.6 tabs and the 17.0 width


def test_cleated_volume():
    assert 10.25 <= volume_cm3(slat(True)) <= 11.25


def test_cleated_heavier_than_plain():
    assert volume_cm3(slat(True)) > volume_cm3(slat(False))


def test_plain_probe_points():
    s = slat(False)
    assert contains(s, (0, 1.5, 0))
    assert contains(s, (0, -3, 18.35))      # inner tab
    assert contains(s, (0, -3, 35.65))      # outer tab
    assert not contains(s, (0, -3, 27))     # saddle mouth, hollow
    assert not contains(s, (0, -3, 10))     # between the lug and the inner tab
    assert not contains(s, (0, 8, 0))


def test_guide_lug_probe_points():
    """drivetrain-spec §6.3, on both variants."""
    for s in (slat(False), slat(True)):
        assert contains(s, (0, -2, 0))
        assert contains(s, (0, -3.8, 0))
        assert not contains(s, (0, -2, 5.0))    # lug flank tapers
        assert not contains(s, (0, -4.5, 0))    # below the lug tip
        assert not contains(s, (6.0, -2, 0))    # lug is short along the run


def test_lips_sit_just_under_the_belt():
    """drivetrain-spec §6.2: the lip's upper face is 0.2 under a 2.4 belt."""
    s = slat(False)
    assert contains(s, (0, -2.7, 19.9))         # lip, just below the belt's teeth
    assert not contains(s, (0, -2.5, 19.9))     # the belt's edge, above the lip


def test_cleated_probe_points():
    c = slat(True)
    assert contains(c, (0, 8, 0))
    assert contains(c, (0, 14, 30))
    assert not contains(c, (0, 8, 39))      # cleat stops short of the end
    assert not contains(c, (6, 8, 0))       # cleat is narrow in x


def test_plain_clears_pulley():
    assert not clash(slat(False), pulley_envelope())


def test_cleated_clears_pulley():
    assert not clash(slat(True), pulley_envelope())


def test_plain_is_manifold():
    assert slat(False).is_valid


def test_cleated_is_manifold():
    assert slat(True).is_valid


def test_slat_is_deterministic():
    a = slat(True)
    b = slat(True)
    assert volume_cm3(a) == volume_cm3(b)
    assert bbox_size(a) == bbox_size(b)


def test_export_writes_both_slat_stls():
    paths = [path for path in export_all() if path.stem.startswith("slat_")]
    assert len(paths) == 2
    for path in paths:
        assert path.exists()
        assert path.stat().st_size > 0
