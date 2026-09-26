"""spec-drive §8 -- the stepper, coupler and printed motor bracket on the
head shaft, and the head shaft lengthened for them. The whole-loop sweep
(8.12, slats) is tests/test_drivetrain.py's, and T2 (8.13, base) and the
prop force (8.14) are tests/test_tilt.py's; each now includes the drive."""

import pytest
from build123d import Location, Rot
from pytest import approx

import geometry as g
import params as p
from assembly import (
    bearings_group, belts_group, drive_group, drivetrain_group, pillow_blocks_group, plates_group, report,
    tilt_base_parts,
)
from cut_list import write_cut_list
from parts.coupler import coupler
from parts.motor import motor
from parts.motor_bracket import motor_bracket, motor_hole_centres, slot_z
from parts.shaft import shaft
from utils import _overlap_volume, bbox_size, clash, contains, volume_cm3

SIDES = (1, -1)
TAKEUPS = (p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX)
H = p.SHAFT_HEIGHT_ABOVE_PLATE


def by_label(parts) -> dict:
    return {part.label: part for part in parts}


def drive_parts(side: int, takeup: float = 0.0, incline: float = p.INCLINE) -> dict:
    return by_label(drive_group(takeup=takeup, incline=incline, drive_side=side).children)


def head_shaft(side: int):
    return by_label(drivetrain_group(drive_side=side).children)["head shaft"]


# --- §8 1-6, params.py assertions, and the §2 sizing ---------------------------------


def test_head_shaft_reaches_the_coupler():
    assert p.HEAD_SHAFT_DRIVE_EXT >= p.PILLOW_BLOCK_HALF_W + p.COUPLER_BLOCK_GAP + p.COUPLER_ENGAGE


def test_engagement_of_each_shaft_in_the_coupler():
    motor_engage = p.COUPLER_Z + p.COUPLER_LEN - (p.MOTOR_FACE_Z - p.MOTOR_SHAFT_LEN)
    for engage in (p.HEAD_SHAFT_ENGAGE, motor_engage):
        assert p.COUPLER_ENGAGE <= engage <= p.COUPLER_ENGAGE_MAX


def test_shaft_tips_do_not_meet():
    assert p.COUPLER_TIP_GAP >= p.COUPLER_TIP_GAP_MIN
    assert p.COUPLER_TIP_GAP == approx(4.5)


def test_m3_screws_stop_short_in_the_motor():
    assert p.MOTOR_SCREW_LEN - p.FACE_PLATE_T <= p.MOTOR_SCREW_MAX_ENGAGE


def test_torque_margin():
    assert p.DRIVE_TORQUE_AVAIL / p.DRIVE_TORQUE_EST >= p.DRIVE_TORQUE_MARGIN_MIN
    assert p.DRIVE_TORQUE_AVAIL / p.DRIVE_TORQUE_EST == approx(1.66, abs=0.01)
    assert p.DRIVE_TORQUE_EST == approx(0.153, abs=1e-3)
    assert p.DRIVE_SKIP_PULL_N == approx(13.3, abs=0.05)
    assert p.DRIVE_STEP_RATE == 1600.0
    assert p.COUPLER_RATED_TORQUE > p.MOTOR_HOLD_TORQUE


def test_motor_sits_clear_of_the_m5_heads():
    assert H - p.MOTOR_SQUARE / 2 >= p.BRACKET_FOOT_T + p.M5_HEAD_H + p.MOTOR_HEAD_CLEAR


def test_stack_with_the_printed_block():
    """README 'Drive resolutions': the spec's stack moved 9 inboard."""
    assert p.PILLOW_BLOCK_HALF_W == p.PB_OUTBOARD_FACE_Z
    assert (p.HEAD_SHAFT_LEN, p.HEAD_SHAFT_DRIVE_EXT, p.COUPLER_Z, p.MOTOR_FACE_Z, p.FACE_PLATE_Z) == (
        140.0, 17.5, 57.0, 95.5, 90.5,
    )
    assert p.MOTOR_FACE_Z + p.MOTOR_BODY_LEN <= p.FRAME_WIDTH / 2


# --- §8 7-10, the bracket alone ---------------------------------------------------------


def seated_motor():
    """A motor on the bracket's face plate, in the bracket's local frame."""
    return motor().moved(Location((0, H, p.FACE_PLATE_T), (0, 180, 0)))


def test_bracket_is_valid_one_solid():
    b = motor_bracket()
    assert b.is_valid and len(b.solids()) == 1


def test_bracket_bbox_and_volume():
    b = motor_bracket()
    assert bbox_size(b) == approx((45.0, 72.0, 66.0), abs=0.5)   # 57 across in the spec -- README
    assert 25.0 <= volume_cm3(b) <= 45.0
    assert volume_cm3(b) == approx(30.47, rel=0.03)              # pinned on the first build


def test_bracket_holes_are_open():
    b, mid = motor_bracket(), p.FACE_PLATE_T / 2
    assert not contains(b, (0, H, mid))
    for x, y in motor_hole_centres():
        assert not contains(b, (x, y, mid))
    for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X):
        assert not contains(b, (x, p.BRACKET_FOOT_T / 2, slot_z()))


def test_face_plate_is_solid():
    assert contains(motor_bracket(), (0, 30, 2.5))


def test_motor_seats_on_the_face_plate():
    b, m = motor_bracket(), seated_motor()
    assert not clash(b, m)
    assert b.distance_to(m) == approx(0.0, abs=1e-6)


def test_tight_pilot_bore_clashes_with_the_boss():
    """Negative control: a real overlap, not contact."""
    assert _overlap_volume(motor_bracket(pilot_bore=21.9), seated_motor()) > 1.0


# --- The reference solids and the head shaft ----------------------------------------


def test_motor_and_coupler():
    assert motor().is_valid and bbox_size(motor()) == approx((42.3, 42.3, 63.5), abs=0.01)
    assert coupler().is_valid and bbox_size(coupler()) == approx((20.0, 20.0, 25.0), abs=0.01)


def test_head_shaft_is_longer_on_its_drive_end_only():
    s = shaft(p.HEAD_SHAFT_DRIVE_EXT)
    assert s.is_valid
    assert bbox_size(s) == approx((8.0, 8.0, p.HEAD_SHAFT_LEN), abs=0.01)
    assert s.bounding_box().min.Z == approx(-p.SHAFT_LENGTH / 2)
    assert not contains(s, (3.8, 0, 0)) and contains(s, (3.8, 0, 30.0))   # flat still centred on z = 0
    assert bbox_size(shaft()) == approx((8.0, 8.0, p.SHAFT_LENGTH), abs=0.01)   # tail unchanged


@pytest.mark.parametrize("side", SIDES)
def test_head_shaft_long_end_is_on_the_drive_side(side):
    box = head_shaft(side).bounding_box()
    drive_end, other_end = (box.max.Z, -box.min.Z) if side > 0 else (-box.min.Z, box.max.Z)
    assert drive_end == approx(p.BEARING_Z + p.HEAD_SHAFT_DRIVE_EXT)
    assert other_end == approx(p.SHAFT_LENGTH / 2)


@pytest.mark.parametrize("side", SIDES)
def test_shafts_sit_in_the_coupler_bores(side):
    d = drive_parts(side)
    assert not clash(d["coupler"], head_shaft(side)) and d["coupler"].distance_to(head_shaft(side)) < 1e-6
    assert not clash(d["coupler"], d["motor"])
    assert not clash(d["motor"], d["motor bracket"]) and d["motor"].distance_to(d["motor bracket"]) < 1e-6


# --- §8 11-13, 15 in the machine, both sides ------------------------------------------


@pytest.mark.parametrize("side", SIDES)
@pytest.mark.parametrize("incline", p.TILT_CHECK_ANGLES)
def test_coupler_clearances(side, incline):
    d = drive_parts(side, incline=incline)
    blocks = [b for b in pillow_blocks_group(incline=incline).children if b.label.startswith("head")]
    gap = min(d["coupler"].distance_to(b) for b in blocks)
    assert gap >= p.COUPLER_CLEAR_BLOCK and gap == approx(p.COUPLER_BLOCK_GAP, abs=1e-6)
    assert d["coupler"].distance_to(d["motor bracket"]) >= p.COUPLER_CLEAR_BRACKET
    assert min(d["coupler"].distance_to(pl) for pl in plates_group(incline=incline).children) >= p.COUPLER_CLEAR_BRACKET


@pytest.mark.parametrize("side", SIDES)
@pytest.mark.parametrize("takeup", TAKEUPS)
def test_drive_clears_belts_shaft_sets_blocks_and_plates(side, takeup):
    others = list(belts_group(takeup=takeup).children) + list(plates_group(takeup=takeup).children)
    others += [c for c in drivetrain_group(takeup=takeup).children if c.label.endswith("shaft set")]
    others += list(pillow_blocks_group(takeup=takeup).children) + list(bearings_group(takeup=takeup).children)
    for part in drive_parts(side, takeup).values():
        for other in others:
            assert not clash(part, other), f"{part.label} / {other.label}"


@pytest.mark.parametrize("side", SIDES)
def test_bracket_stands_on_the_head_plate_over_its_m5_holes(side):
    bracket, plate = drive_parts(side)["motor bracket"], plates_group().children[-1]
    assert bracket.distance_to(plate) == approx(0.0, abs=1e-6)
    for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X):
        slot = g.at(p.CENTRE_DIST + x, g.plate_top_offset() + p.BRACKET_FOOT_T / 2, side * p.PLATE_BOLT_Z).position
        hole = g.at(p.CENTRE_DIST + x, g.plate_top_offset() - p.PLATE_THICKNESS / 2, side * p.PLATE_BOLT_Z).position
        assert not contains(bracket, (slot.X, slot.Y, slot.Z)) and not contains(plate, (hole.X, hole.Y, hole.Z))


@pytest.mark.parametrize("side", SIDES)
@pytest.mark.parametrize("incline", p.TILT_CHECK_ANGLES)
def test_drive_clears_the_base(side, incline):
    base = by_label(tilt_base_parts(incline))["base_ref"]
    for part in drive_parts(side, incline=incline).values():
        assert part.distance_to(base) >= p.BASE_CLEARANCE_MIN, part.label


def test_drive_base_clearance_at_the_lowest_angle():
    """The spec's 'about 225' is the motor; the bracket's foot is lower."""
    base = by_label(tilt_base_parts(p.TILT_MIN))["base_ref"]
    d = drive_parts(p.DRIVE_SIDE, incline=p.TILT_MIN)
    assert d["motor"].distance_to(base) == approx(223.4, abs=0.1)
    assert d["motor bracket"].distance_to(base) == approx(198.4, abs=0.1)


# --- Output -------------------------------------------------------------------------------


def test_bracket_prints_foot_down():
    box = (Rot(*p.PRINT_ROT_MOTOR_BRACKET) * motor_bracket()).bounding_box()
    assert (box.min.Z, box.max.Z) == approx((0.0, 72.0), abs=1e-6)   # foot on the bed, face plate standing up


def test_report_lists_the_drive():
    text = "\n".join(report())
    assert "4P-6813" in text and "A4988" in text and f"8 mm shaft, {p.HEAD_SHAFT_LEN:g} long" in text


def test_cut_list_has_both_shafts():
    text = write_cut_list().read_text()
    assert f"tail     : {p.SHAFT_LENGTH:g} mm" in text and f"head     : {p.HEAD_SHAFT_LEN:g} mm" in text
