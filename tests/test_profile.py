"""drivetrain-spec §4.4 -- the belt tooth and the standard pulley groove."""

import math

import pytest
from build123d import GeomType
from pytest import approx

import params as p
from profile import groove_half, groove_junctions, pulley_section, tooth_face, tooth_half

# Read from the manufacturer's B-rep (reference/htd3m_40t_40015040.stp). If
# the rebuild misses them the construction is wrong, not the tolerance.
FILE_JUNCTIONS = [
    (0.2381, 17.4994),   # A bottom / flank arc
    (0.9408, 18.1019),   # B flank arc / straight
    (0.9992, 18.5174),   # C straight / tip arc
    (1.2006, 18.6815),   # D tip arc / OD
]


def _assert_tangent_chain(edges):
    for a, b in zip(edges, edges[1:]):
        assert (a @ 1 - b @ 0).length < 1e-6
        assert (a % 1).get_angle(b % 0) < 0.5


# --- Belt tooth ---------------------------------------------------------------


def test_flank_centre_is_the_pitch_line_differential():
    assert p.FLANK_CENTRE_Y == p.BELT_PLD   # exact equality, not approx: one physical quantity


def test_tooth_height_and_land_width():
    assert p.TOOTH_HEIGHT == approx(1.171, abs=1e-3)
    assert p.LAND_WIDTH == approx(0.914, abs=1e-3)


def test_tooth_face_is_valid_and_one_tooth_high():
    face = tooth_face()
    assert face.is_valid
    assert face.bounding_box().max.Y == approx(p.TOOTH_HEIGHT)
    assert face.bounding_box().min.Y == approx(0.0, abs=1e-9)


def test_tooth_half_is_a_tangent_chain_spanning_half_a_pitch():
    edges = tooth_half()
    assert len(edges) == 3
    _assert_tangent_chain(edges)
    assert (edges[0] @ 0).Y == approx(p.TOOTH_HEIGHT)
    assert (edges[-1] @ 1).X == approx(p.BELT_PITCH / 2)


# --- Pulley groove, against the manufacturer's geometry ---------------------------


def test_groove_junctions_match_the_manufacturer_model():
    assert p.PULLEY_GROOVE_COMP == 0.0 and p.PULLEY_OD_COMP == 0.0, "junction data is for the uncompensated groove"
    for got, want in zip(groove_junctions(), FILE_JUNCTIONS):
        assert math.dist(got, want) < 0.005


def test_groove_half_is_a_tangent_chain():
    edges = groove_half()
    assert len(edges) == 4
    _assert_tangent_chain(edges)


def test_groove_half_ends_tangent_to_bottom_and_od():
    edges = groove_half()
    assert (edges[0] @ 0).X == approx(0.0, abs=1e-9)
    assert (edges[0] @ 0).Y == approx(p.PULLEY_GROOVE_BOTTOM_R)
    assert (edges[-1] @ 1).length == approx(p.PULLEY_OD / 2)


def test_straight_flank_is_about_eight_degrees_off_radial():
    _, b, c, _ = groove_junctions()
    assert math.degrees(math.atan2(c[0] - b[0], c[1] - b[1])) == approx(8.0, abs=0.1)


def test_groove_depth():
    assert p.PULLEY_GROOVE_DEPTH == approx(1.2165, abs=1e-4)
    assert abs(p.PULLEY_GROOVE_DEPTH - 1.219) < 0.005   # agrees with the file


def test_groove_mouth_and_land():
    mouth = 2 * groove_junctions()[3][0]
    assert mouth == approx(2.40, abs=0.005)
    assert math.pi * p.PULLEY_OD / p.PULLEY_TEETH - mouth == approx(0.537, abs=0.005)


def test_pulley_section_has_forty_grooves():
    ps = pulley_section()
    assert ps.is_valid
    arcs = [e for e in ps.outer_wire().edges() if e.geom_type == GeomType.CIRCLE]
    assert sum(abs(e.radius - p.PULLEY_GROOVE_TIP_R) < 1e-6 for e in arcs) == 80
    assert sum(abs(e.radius - p.PULLEY_GROOVE_FLANK_R) < 1e-6 for e in arcs) == 80


def test_pulley_section_extrudes_towards_plus_z():
    assert pulley_section().normal_at().Z == approx(1.0)
    assert tooth_face().normal_at().Z == approx(1.0)


def test_pulley_section_refuses_other_tooth_counts():
    with pytest.raises(ValueError):
        pulley_section(24)


def test_groove_compensation_widens_the_groove_and_stays_tangent(monkeypatch):
    standard = groove_junctions()
    monkeypatch.setattr(p, "PULLEY_GROOVE_COMP", 0.05)
    grown = groove_junctions()
    assert math.hypot(*grown[0]) == approx(p.PULLEY_GROOVE_BOTTOM_R - 0.05)   # deeper
    assert grown[1][0] > standard[1][0] and grown[2][0] > standard[2][0]      # wider
    assert math.hypot(*grown[3]) == approx(p.PULLEY_OD / 2)                   # still meets the OD
    _assert_tangent_chain(groove_half())
    assert pulley_section().is_valid


def test_od_compensation_shrinks_the_od(monkeypatch):
    monkeypatch.setattr(p, "PULLEY_OD_COMP", 0.1)
    assert math.hypot(*groove_junctions()[3]) == approx((p.PULLEY_OD - 0.1) / 2)
    _assert_tangent_chain(groove_half())
