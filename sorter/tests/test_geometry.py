import math

from pytest import approx

from geometry import at, belt_back_radius, is_cleated, run_direction, run_normal, shaft_axis, slat_t
from params import CENTRE_DIST, INCLINE, SLAT_COUNT


def test_run_direction_is_unit():
    assert run_direction().length == approx(1.0)


def test_run_normal_is_unit():
    assert run_normal().length == approx(1.0)


def test_run_direction_and_normal_are_orthogonal():
    assert run_direction().dot(run_normal()) == approx(0.0, abs=1e-9)


def test_run_direction_and_normal_are_right_handed():
    cross = run_direction().cross(run_normal())
    assert cross.X == approx(0.0, abs=1e-9)
    assert cross.Y == approx(0.0, abs=1e-9)
    assert cross.Z == approx(1.0)


def test_belt_back_radius():
    assert belt_back_radius() == approx(22.327, abs=0.01)


def test_shaft_axis_tail_is_origin():
    tail = shaft_axis("tail")
    assert (tail.X, tail.Y, tail.Z) == approx((0.0, 0.0, 0.0))


def test_shaft_axis_head_is_centre_dist_along_run():
    head = shaft_axis("head")
    expected = run_direction() * CENTRE_DIST
    assert head.X == approx(expected.X)
    assert head.Y == approx(expected.Y)
    assert head.Z == approx(expected.Z)


def test_shaft_axis_rejects_bad_end():
    try:
        shaft_axis("middle")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_at_zero_matches_incline_projection():
    assert at(0).position.Y == approx(belt_back_radius() * math.cos(math.radians(INCLINE)), abs=0.01)


def test_at_orientation_axes():
    loc = at(0)
    x_dir = loc.x_axis.direction
    z_dir = loc.z_axis.direction
    rd = run_direction()
    assert x_dir.X == approx(rd.X, abs=1e-6)
    assert x_dir.Y == approx(rd.Y, abs=1e-6)
    assert x_dir.Z == approx(rd.Z, abs=1e-6)
    assert z_dir.X == approx(0.0, abs=1e-6)
    assert z_dir.Y == approx(0.0, abs=1e-6)
    assert z_dir.Z == approx(1.0, abs=1e-6)


def test_at_lateral_offset():
    loc = at(0, lateral=10.0)
    assert loc.position.Z == approx(10.0)


def test_slat_t_zero():
    assert slat_t(0) == 0.0


def test_slat_t_three():
    assert slat_t(3) == approx(45.0)


def test_is_cleated_pattern():
    assert is_cleated(0) and not is_cleated(1) and not is_cleated(2) and is_cleated(3)


def test_is_cleated_count():
    assert sum(is_cleated(i) for i in range(SLAT_COUNT)) == 9
