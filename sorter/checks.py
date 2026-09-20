"""Human-facing pre-export gate: runs every acceptance assertion from the
CAD spec and prints a pass/fail line per check. The same assertions are
expressed as pytest tests under tests/; this is the manual runner."""

import math
import sys

import geometry as g
import params as p
from parts.slat import pulley_envelope, slat
from utils import bbox_size, clash, contains, volume_cm3


def _check_parameter_consistency():
    assert p.BELT_LOOP_LENGTH % p.BELT_PITCH == 0
    assert p.BELT_LOOP_LENGTH % p.SLAT_PITCH == 0
    assert p.SLAT_COUNT == 26
    assert abs(2 * p.CENTRE_DIST + math.pi * p.PULLEY_PD - p.BELT_LOOP_LENGTH) < 1e-6
    assert (p.BELT_WIDTH - p.PULLEY_FACE_WIDTH) / 2 >= 2.0
    assert p.CLEAT_LENGTH < p.SLAT_LENGTH
    assert p.SADDLE_TAB_LENGTH / p.BELT_PITCH <= 2.5
    assert p.SLAT_WIDTH < p.SLAT_PITCH                          # slats must not touch
    assert p.SLAT_PITCH - p.SLAT_WIDTH <= 3.0                   # gap smaller than a 1x1 plate
    assert p.BEARING_SPACING > p.BELT_SPACING + p.BELT_WIDTH
    assert p.SHAFT_LENGTH > p.BEARING_SPACING + 40


def _check_returning_run_clearance():
    """The clearance that caused rev B: the returning run's cleats must not
    strike the mounting plate."""
    belt_back = p.PULLEY_PD / 2 - p.BELT_PLD + p.BELT_THICKNESS
    cleat_tip = belt_back + p.SLAT_THICKNESS + p.CLEAT_HEIGHT
    assert p.SHAFT_HEIGHT_ABOVE_PLATE > cleat_tip + 5.0


def _check_saddle_clearances():
    tab_inner_face = (p.BELT_WIDTH - p.SADDLE_INTERFERENCE) / 2
    assert tab_inner_face - p.PULLEY_FACE_WIDTH / 2 >= 1.5             # tab vs pulley
    tab_outer_face = tab_inner_face + p.SADDLE_TAB_THICKNESS
    assert p.SLAT_LENGTH / 2 - (p.BELT_SPACING / 2 + tab_outer_face) >= 2.0   # rim


def _check_geometry_module():
    tol = 0.01
    assert abs(g.run_direction().length - 1.0) < 1e-9
    assert abs(g.run_normal().length - 1.0) < 1e-9
    assert abs(g.run_direction().dot(g.run_normal())) < 1e-9
    assert abs(g.belt_back_radius() - 22.327) < tol
    assert abs(g.at(0).position.Y - g.belt_back_radius() * math.cos(math.radians(p.INCLINE))) < tol
    assert g.slat_t(0) == 0.0
    assert abs(g.slat_t(3) - 45.0) < 1e-9
    assert g.is_cleated(0) and not g.is_cleated(1) and not g.is_cleated(2) and g.is_cleated(3)
    assert sum(g.is_cleated(i) for i in range(p.SLAT_COUNT)) == 9


def _check_slat_bounding_box():
    tol = 0.02
    plain = bbox_size(slat(False))
    assert all(abs(a - b) < tol for a, b in zip(plain, (13.0, 9.0, 80.0)))
    cleated = bbox_size(slat(True))
    assert all(abs(a - b) < tol for a, b in zip(cleated, (13.0, 21.0, 80.0)))


def _check_volume():
    assert 3.5 <= volume_cm3(slat(False)) <= 4.2
    assert 9.6 <= volume_cm3(slat(True)) <= 10.6
    assert volume_cm3(slat(True)) > volume_cm3(slat(False))


def _check_probe_points():
    s = slat(False)
    assert contains(s, (0, 1.5, 0))
    assert contains(s, (0, -3, 24.4))       # inner tab
    assert contains(s, (0, -3, 35.6))       # outer tab
    assert not contains(s, (0, -3, 30))     # saddle mouth, hollow
    assert not contains(s, (0, -3, 0))
    assert not contains(s, (0, 8, 0))

    c = slat(True)
    assert contains(c, (0, 8, 0))
    assert contains(c, (0, 14, 30))
    assert not contains(c, (0, 8, 39))      # cleat stops short of the end
    assert not contains(c, (6, 8, 0))       # cleat is narrow in x


def _check_clearance():
    assert not clash(slat(False), pulley_envelope())
    assert not clash(slat(True), pulley_envelope())


def _check_manifold():
    assert slat(False).is_valid
    assert slat(True).is_valid


_CHECKS = [
    ("parameter consistency", _check_parameter_consistency),
    ("returning run clearance", _check_returning_run_clearance),
    ("saddle clearances", _check_saddle_clearances),
    ("geometry module", _check_geometry_module),
    ("slat bounding box", _check_slat_bounding_box),
    ("volume", _check_volume),
    ("probe points", _check_probe_points),
    ("clearance", _check_clearance),
    ("manifold", _check_manifold),
]


def run_checks() -> bool:
    all_passed = True
    for label, fn in _CHECKS:
        try:
            fn()
            print(f"PASS  {label}")
        except AssertionError as exc:
            print(f"FAIL  {label}: {exc}")
            all_passed = False
    return all_passed


if __name__ == "__main__":
    sys.exit(0 if run_checks() else 1)
