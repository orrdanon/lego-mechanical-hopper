"""Human-facing pre-export gate: runs every acceptance assertion from the
CAD spec and prints a pass/fail line per check. The same assertions are
expressed as pytest tests under tests/; this is the manual runner."""

import math
import sys

from itertools import combinations

import geometry as g
import params as p
from assembly import COLOURS, GROUPS, assembly
from parts.bridge_plate import bridge_plate
from parts.frame import frame
from parts.slat import pulley_envelope, slat
from utils import bbox_size, clash, contains, volume_cm3


def _check_parameter_consistency():
    assert p.BELT_LOOP_LENGTH % p.BELT_PITCH == 0
    assert p.BELT_LOOP_LENGTH % p.SLAT_PITCH == 0
    assert p.SLAT_COUNT == 46
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
    assert abs(g.belt_back_radius() - 21.118) < tol
    assert abs(g.at(0).position.Y) < 1e-9                      # offset origin is the shaft axis
    assert abs(g.at(0, g.belt_back_radius()).position.Y - g.belt_back_radius() * math.cos(math.radians(p.INCLINE))) < tol
    assert g.slat_t(0) == 0.0
    assert abs(g.slat_t(3) - 54.0) < 1e-9
    assert g.is_cleated(0) and not g.is_cleated(1) and g.is_cleated(2) and not g.is_cleated(3)
    assert sum(g.is_cleated(i) for i in range(p.SLAT_COUNT)) == 23


def _check_slat_bounding_box():
    tol = 0.02
    plain = bbox_size(slat(False))
    assert all(abs(a - b) < tol for a, b in zip(plain, (16.0, 9.0, 80.0)))
    cleated = bbox_size(slat(True))
    assert all(abs(a - b) < tol for a, b in zip(cleated, (16.0, 21.0, 80.0)))


def _check_volume():
    assert 3.9 <= volume_cm3(slat(False)) <= 4.6
    assert 10.0 <= volume_cm3(slat(True)) <= 11.0
    assert volume_cm3(slat(True)) > volume_cm3(slat(False))


def _check_probe_points():
    s = slat(False)
    assert contains(s, (0, 1.5, 0))
    assert contains(s, (0, -3, 18.35))      # inner tab
    assert contains(s, (0, -3, 35.65))      # outer tab
    assert not contains(s, (0, -3, 27))     # saddle mouth, hollow
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


# --- Phase 4: frame, bridge plates, assembly framework ---------------------


def _placed_plate(i: int):
    return bridge_plate(g.plate_role(i)).moved(g.at(g.plate_t(i), g.plate_top_offset()))


def _check_frame_geometry():
    assert abs(g.rail_top_offset() - (-57.0)) < 1e-9
    assert abs(g.rail_lateral() - 127.0) < 1e-9
    assert abs(g.plate_t(0)) < 1e-9
    assert abs(g.plate_t(p.PLATE_STATIONS - 1) - p.CENTRE_DIST) < 1e-9
    assert [g.plate_role(i) for i in range(p.PLATE_STATIONS)] == ["bearing", "support", "support", "support", "bearing"]
    try:
        g.plate_t(p.PLATE_STATIONS)
    except IndexError:
        pass
    else:
        raise AssertionError("plate_t must raise IndexError past the last station")


def _check_frame():
    f = frame()
    assert f.is_valid
    assert len(f.solids()) == 4
    theta = math.radians(p.INCLINE)
    longest = p.FRAME_LENGTH * math.cos(theta) + p.FRAME_PROFILE * math.sin(theta)
    assert abs(sorted(bbox_size(f))[-1] - longest) < 0.5     # inclined, see README "Frame bounding box"
    local = f.moved(g.at(g.frame_t_centre(), g.rail_top_offset()).inverse())
    assert all(abs(a - b) < 0.02 for a, b in zip(bbox_size(local), (p.FRAME_LENGTH, p.FRAME_PROFILE, p.FRAME_WIDTH)))


def _check_plates_sit_on_rails():
    f = frame()
    for i in range(p.PLATE_STATIONS):
        plate = _placed_plate(i)
        assert not clash(plate, f, tol=1.0)
        assert plate.distance_to(f) < 0.01                    # touching, not floating


def _check_plates_span_rails():
    assert abs(bbox_size(bridge_plate())[2] - p.PLATE_LENGTH) < 0.02
    assert p.PLATE_LENGTH > 2 * g.rail_lateral()
    f = frame()
    for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X):
        for z in (-p.PLATE_BOLT_Z, p.PLATE_BOLT_Z):
            probe = g.at(g.plate_t(0) + x, g.rail_top_offset() - p.FRAME_SLOT_DEPTH / 2, lateral=z).position
            assert not contains(f, (probe.X, probe.Y, probe.Z))   # hole sits over an open slot


def _check_plates_dont_collide():
    placed = [_placed_plate(i) for i in range(p.PLATE_STATIONS)]
    for a, b in combinations(placed, 2):
        assert not clash(a, b)


def _check_assembly_framework():
    assert set(assembly().keys()) == set(GROUPS)
    assert set(assembly("frame").keys()) == {"frame"}
    assert set(COLOURS) == set(GROUPS)
    try:
        assembly("drivetrain")
    except ValueError:
        pass
    else:
        raise AssertionError("assembly() must reject unknown group names")
    assert assembly("plates")["plates"].is_valid


# Checks known to fail for a recorded reason. A check listed here counts as
# XFAIL when it fails and as a failure of the run when it unexpectedly
# passes -- at which point remove it from this table. Empty since rev D
# closed the CENTRE_DIST question.
_EXPECTED_FAILURES: dict[str, str] = {}

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
    ("frame geometry", _check_frame_geometry),
    ("frame", _check_frame),
    ("plates sit on rails", _check_plates_sit_on_rails),
    ("plates span rails", _check_plates_span_rails),
    ("plates don't collide with each other", _check_plates_dont_collide),
    ("assembly framework", _check_assembly_framework),
]


def run_checks() -> bool:
    all_passed = True
    for label, fn in _CHECKS:
        expected_failure = _EXPECTED_FAILURES.get(label)
        try:
            fn()
        except AssertionError as exc:
            if expected_failure:
                print(f"XFAIL {label}: {expected_failure}")
            else:
                print(f"FAIL  {label}: {exc}")
                all_passed = False
        else:
            if expected_failure:
                print(f"XPASS {label}: now passes -- remove it from _EXPECTED_FAILURES")
                all_passed = False
            else:
                print(f"PASS  {label}")
    return all_passed


if __name__ == "__main__":
    sys.exit(0 if run_checks() else 1)
