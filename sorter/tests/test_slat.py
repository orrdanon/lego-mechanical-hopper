from pytest import approx

from export import export_all
from parts.slat import pulley_envelope, slat
from utils import bbox_size, clash, contains, volume_cm3


def test_plain_bbox():
    assert bbox_size(slat(False)) == approx((16.0, 9.0, 80.0), abs=0.02)


def test_cleated_bbox():
    assert bbox_size(slat(True)) == approx((16.0, 21.0, 80.0), abs=0.02)


def test_plain_volume():
    assert 3.9 <= volume_cm3(slat(False)) <= 4.6


def test_cleated_volume():
    assert 10.0 <= volume_cm3(slat(True)) <= 11.0


def test_cleated_heavier_than_plain():
    assert volume_cm3(slat(True)) > volume_cm3(slat(False))


def test_plain_probe_points():
    s = slat(False)
    assert contains(s, (0, 1.5, 0))
    assert contains(s, (0, -3, 18.35))      # inner tab
    assert contains(s, (0, -3, 35.65))      # outer tab
    assert not contains(s, (0, -3, 27))     # saddle mouth, hollow
    assert not contains(s, (0, -3, 0))
    assert not contains(s, (0, 8, 0))


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


def test_export_writes_both_stls():
    paths = export_all()
    assert len(paths) == 2
    for path in paths:
        assert path.exists()
        assert path.stat().st_size > 0
