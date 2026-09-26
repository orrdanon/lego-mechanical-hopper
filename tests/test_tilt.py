"""spec-tilt §8.2 -- the incline as a parameter, the hinge, cross-member,
clevis and prop. T1 is the rest of the suite passing unchanged at
incline=INCLINE; T6's sweep is tests/test_drivetrain.py's whole-loop test,
which now runs at every TILT_CHECK_ANGLES."""

import pytest
from build123d import Align, Box, Location, Pos, Rot
from pytest import approx

import geometry as g
import params as p
from assembly import (
    COLOURS, PLACEHOLDERS, assembly, belts_group, drivetrain_group, frame_group, plates_group, report, slats_group,
    tilt_base_parts, tilt_frame_parts, tilt_group, tilt_prop_parts,
)
from cut_list import write_cut_list
from parts.base_ref import base_ref
from parts.frame import cross_member, frame
from parts.hinge import hinge_block, hinge_bracket
from parts.prop import base_pin_block, frame_clevis, knob, prop_body, prop_foot
from utils import bbox_size, clash, contains

ANGLES = p.TILT_CHECK_ANGLES
TAKEUPS = (p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX)
GRID = [p.TILT_MIN + 0.5 * i for i in range(int((p.TILT_MAX - p.TILT_MIN) / 0.5) + 1)]


def by_label(parts) -> dict:
    return {part.label: part for part in parts}


# --- §2 The incline is a parameter; the machine frame does not move --------------


def test_default_incline_is_todays_machine():
    assert (g.run_direction(p.INCLINE) - g.run_direction()).length == 0.0
    assert (g.loop_at(100.0, incline=p.INCLINE).position - g.loop_at(100.0).position).length == 0.0
    assert frame(p.INCLINE).bounding_box().max.Y == frame().bounding_box().max.Y


@pytest.mark.parametrize("incline", ANGLES)
def test_conveyor_rotates_about_the_machine_origin(incline):
    assert g.at(0, incline=incline).position.length == approx(0.0, abs=1e-12)
    assert g.shaft_axis("head", incline).length == approx(p.CENTRE_DIST)
    assert g.run_direction(incline).dot(g.run_normal(incline)) == approx(0.0, abs=1e-12)
    assert g.at(10.0, incline=incline).y_axis.direction.Y == approx(g.run_normal(incline).Y)


@pytest.mark.parametrize("incline", ANGLES)
def test_base_frame_is_level_and_under_the_hinge(incline):
    base, hinge = g.base_frame(incline), g.hinge_axis(incline)
    assert base.position.X == approx(hinge.X)
    assert g.height_above_base(hinge, incline) == approx(p.HINGE_HEIGHT)
    assert g.base_z(incline) == approx(hinge.Y - p.HINGE_HEIGHT)
    assert (base.x_axis.direction.X, base.y_axis.direction.Y, base.z_axis.direction.Z) == approx((1.0, 1.0, 1.0))


def test_hinge_axis_is_on_the_rail_centreline_and_ignores_the_takeup():
    assert p.HINGE_OFFSET == approx(g.rail_top_offset() - p.FRAME_PROFILE / 2) == approx(-67.0)
    assert p.HINGE_T - p.FRAME_T_START == approx(10.0)
    assert p.PROP_PIN_A_OFFSET == approx(-87.0)
    nominal, slid = by_label(tilt_group().children), by_label(tilt_group(takeup=p.TAIL_TAKEUP_MAX).children)
    for label in ("hinge bracket +z", "hinge block -z", "prop body"):
        assert (nominal[label].center() - slid[label].center()).length == approx(0.0, abs=1e-9)


# --- T2, T3: the base -------------------------------------------------------------------


@pytest.mark.parametrize("incline", ANGLES)
@pytest.mark.parametrize("takeup", TAKEUPS)
def test_everything_that_tilts_clears_the_base(incline, takeup):
    base = by_label(tilt_base_parts(incline))["base_ref"]
    moving = tilt_frame_parts(incline)
    for group in (frame_group, plates_group, drivetrain_group, belts_group, slats_group):
        moving += list(group(takeup=takeup, incline=incline).children)
    for part in moving:
        assert part.distance_to(base) >= p.BASE_CLEARANCE_MIN, part.label


@pytest.mark.parametrize("incline", ANGLES)
def test_a_raised_base_is_hit_by_the_rail_tail_corner(incline):
    """Negative control. The corner rides about 6 above the base."""
    base = by_label(tilt_base_parts(incline))["base_ref"]
    assert 5.0 < frame(incline).distance_to(base) < 7.0
    assert clash(frame(incline), base.moved(Location((0, 10.0, 0))), tol=1.0)


@pytest.mark.parametrize("incline", ANGLES)
@pytest.mark.parametrize("takeup", TAKEUPS)
def test_tail_shaft_height(incline, takeup):
    lo, hi = p.TAIL_SHAFT_HEIGHT_RANGE
    axis = g.at(g.tail_shaft_t(takeup), 0, incline=incline).position
    assert lo <= g.height_above_base(axis, incline) <= hi


def test_head_shaft_height():
    """T12, report only in checks.py."""
    heights = [g.height_above_base(g.shaft_axis("head", a), a) for a in ANGLES]
    assert heights == approx([251.0, 331.0, 389.0], abs=1.0)


def test_base_ref_is_a_slab_under_the_base_plane():
    slab = base_ref()
    box = slab.bounding_box()
    assert (box.min.X, box.max.X) == approx((-p.BASE_REF_BEHIND, p.BASE_REF_AHEAD))
    assert (box.min.Y, box.max.Y) == approx((-p.BASE_REF_THK, 0.0))
    assert (box.min.Z, box.max.Z) == approx((-p.BASE_REF_HALF_WIDTH, p.BASE_REF_HALF_WIDTH))


# --- T4: hinge ----------------------------------------------------------------------------


@pytest.mark.parametrize("incline", ANGLES)
def test_hinge_parts_do_not_clash(incline):
    on_frame, on_base, f = by_label(tilt_frame_parts(incline)), by_label(tilt_base_parts(incline)), frame(incline)
    for side in ("+z", "-z"):
        bracket, block = on_frame[f"hinge bracket {side}"], on_base[f"hinge block {side}"]
        assert not clash(bracket, block) and not clash(bracket, f) and not clash(block, f)
        assert bracket.distance_to(block) >= 0.8
        assert bracket.distance_to(block) == approx(p.HINGE_GAP, abs=1e-3)
        assert bracket.distance_to(f) < 0.01          # bolted to the rail face


def test_hinge_bracket():
    b = hinge_bracket(1)
    assert b.is_valid and len(b.solids()) == 1
    assert bbox_size(b) == approx((42.0, 24.0, p.HINGE_BRKT_THK), abs=0.02)   # plate -10..30, boss 2.0 proud
    assert b.bounding_box().min.Z == approx(0.0)          # origin on the rail-contact face
    assert p.HINGE_HEIGHT - p.HINGE_BOSS_R == approx(8.0)   # boss's lowest point, at every angle
    assert not contains(b, (0, 0, 8.0))                   # pin hole
    assert not contains(b, (0, 6.0, 2.0)) and contains(b, (0, 6.0, 8.0))     # hex pocket, open to the rail face only
    assert not contains(b, (15.0, 0, 2.0)) and not contains(b, (15.0, 3.5, 8.0)) and contains(b, (15.0, 3.5, 2.0))   # counterbored M5
    assert contains(b, (28.0, 8.0, 5.0))


def test_hinge_bracket_is_a_mirror_pair():
    right, left = hinge_bracket(1), hinge_bracket(-1)
    assert left.volume == approx(right.volume)
    assert left.bounding_box().max.Z == approx(0.0) and left.bounding_box().min.Z == approx(-p.HINGE_BRKT_THK)
    assert not contains(left, (0, 6.0, -2.0))             # its pocket faces its own rail
    with pytest.raises(ValueError):
        hinge_bracket(0)


def test_hinge_block():
    b = hinge_block(1)
    assert b.is_valid and len(b.solids()) == 1
    assert bbox_size(b) == approx((p.HINGE_FOOT_LEN, 35.0, p.HINGE_BLOCK_THK + p.HINGE_FOOT_WIDTH), abs=0.02)
    assert b.bounding_box().min.Y == approx(0.0, abs=1e-6) and b.bounding_box().min.Z == approx(0.0)
    assert not contains(b, (0, p.HINGE_HEIGHT, 10.0))     # bushing, right through
    assert contains(b, (0, p.HINGE_HEIGHT + p.HINGE_BUSH_HOLE / 2 + 4.0, 10.0))
    assert p.HINGE_BLOCK_WIDTH / 2 - p.HINGE_BUSH_HOLE / 2 >= p.HINGE_BLOCK_MIN_WALL
    assert contains(b, (28.0, 2.5, 30.0)) and not contains(b, (28.0, 2.5, 10.0))    # flange is outboard only
    assert not contains(b, (22.5, 2.5, 30.0))             # base fixing hole
    assert hinge_block(-1).bounding_box().max.Z == approx(0.0)


# --- T5, T6: cross-member ---------------------------------------------------------------


def test_cross_member_clears_both_plates_along_the_run():
    assert g.xmember_plate_clearance() >= p.XMEMBER_PLATE_CLEAR
    assert g.xmember_plate_clearance() == approx(11.5)


def test_cross_member_at_190_is_over_a_plate():
    """Negative control. It overlaps the plate at 177 by 19.5 (the spec says
    10; its plates are 45 along the run)."""
    assert g.xmember_plate_clearance(190.0) == approx(-19.5)


def test_cross_member_fits_between_the_rails_under_the_return_run():
    xm, f = by_label(tilt_frame_parts())["cross-member"], frame()
    assert bbox_size(cross_member()) == approx((p.FRAME_PROFILE, p.FRAME_PROFILE, p.XMEMBER_LEN), abs=0.02)
    assert not clash(xm, f, tol=1.0) and xm.distance_to(f) < 0.01
    assert all(not clash(xm, plate) for plate in plates_group().children)
    assert -g.cleat_tip_radius() - g.rail_top_offset() >= p.XMEMBER_RETURN_CLEAR


# --- T7, T8: prop clearances --------------------------------------------------------------


def _prop_hits(incline, pin_b_x=p.PROP_PIN_B_X):
    on_frame, on_base = by_label(tilt_frame_parts(incline)), by_label(tilt_base_parts(incline))
    fixed = list(frame(incline).children) + list(plates_group(incline=incline).children)
    fixed += [on_frame["cross-member"], on_base["base_ref"]]
    return [(part.label, other.label) for part in tilt_prop_parts(incline, pin_b_x) for other in fixed if clash(part, other)]


def _prop_underside_gap(incline):
    to_clevis = g.at(p.XMEMBER_T, p.RAIL_UNDERSIDE_OFFSET, incline=incline).inverse()
    body = by_label(tilt_prop_parts(incline))["prop body"].moved(to_clevis)
    bounds = frame_clevis().bounding_box()
    far = 4 * p.PROP_BODY_LEN
    inside = Pos(bounds.min.X, 0, 0) * Box(bounds.size.X, far, far, align=(Align.MIN, Align.CENTER, Align.CENTER))
    return -(body - inside).bounding_box().max.Y


@pytest.mark.parametrize("incline", ANGLES)
def test_prop_clears_the_frame(incline):
    assert _prop_hits(incline) == []
    assert _prop_underside_gap(incline) >= p.PROP_UNDERSIDE_CLEAR


def test_prop_with_pin_b_at_300_hits_the_frame_underside():
    """Negative control, confirmed as spec-tilt §8.2 asks: the prop is then
    111 long, shorter than its own rod, which comes up through pin A into
    the cross-member."""
    assert g.prop_length(p.TILT_MIN, 300.0) < p.ROD_LEN
    assert _prop_hits(p.TILT_MIN, pin_b_x=300.0) == [("prop rod", "cross-member")]


@pytest.mark.parametrize("incline", [p.TILT_MIN, p.TILT_MAX])
def test_prop_swings_free_in_both_clevises(incline):
    on_frame, on_base, prop = (by_label(f(incline)) for f in (tilt_frame_parts, tilt_base_parts, tilt_prop_parts))
    for part, holder in ((prop["prop body"], on_frame["frame clevis"]), (prop["prop foot"], on_base["base pin block"])):
        assert not clash(part, holder)
        assert part.distance_to(holder) == approx(p.CLEVIS_SIDE_CLEAR, abs=1e-3)   # nothing nearer than the cheeks


def test_prop_would_foul_a_clevis_flange_that_was_not_open():
    """Negative control for the swing check, and the reason for the clevis's
    shape: pin A is nearer the cross-member than the eye's radius plus a flange."""
    closed = Box(2 * p.CLEVIS_CHEEK_R, p.CLEVIS_BASE_THK, p.CLEVIS_GAP, align=(Align.CENTER, Align.MAX, Align.CENTER))
    closed = closed.moved(g.at(p.XMEMBER_T, p.RAIL_UNDERSIDE_OFFSET, incline=p.TILT_MIN))
    assert clash(by_label(tilt_prop_parts(p.TILT_MIN))["prop body"], closed, tol=1.0)


# --- T9, T10, T11: numbers ------------------------------------------------------------------


def test_prop_length_table():
    assert [g.prop_length(a) for a in ANGLES] == approx([164.1, 189.6, 220.5], abs=0.5)
    assert [g.prop_lean(a) for a in ANGLES] == approx([51.8, 30.2, 12.3], abs=1.0)
    assert [g.height_above_base(g.prop_pin_a(a), a) for a in ANGLES] == approx([116.4, 178.9, 230.5], abs=0.5)
    assert g.prop_length(p.TILT_MAX) - g.prop_length(p.TILT_MIN) == approx(56.4, abs=0.1)
    assert g.prop_turns(p.TILT_MIN) == 0.0 and g.prop_turns(p.TILT_MAX) == approx(45.0, abs=0.5)


def test_prop_length_is_strictly_increasing():
    assert all(g.prop_length(a) < g.prop_length(b) for a, b in zip(GRID, GRID[1:]))


def test_params_closed_form_agrees_with_geometry():
    for incline in GRID:
        assert p.prop_length_at(incline) == approx(g.prop_length(incline), abs=1e-9)
    assert p.prop_length_at(p.TILT_MIN, 300.0) == approx(g.prop_length(p.TILT_MIN, 300.0), abs=1e-9)


def test_incline_for_length_inverts_prop_length():
    for incline in ANGLES + (33.3,):
        assert g.incline_for_length(g.prop_length(incline)) == approx(incline, abs=0.05)
    with pytest.raises(ValueError):
        g.incline_for_length(g.prop_length(p.TILT_MAX) + 1.0)


def test_length_budget():
    engaged, clear_of_pin_a, stack = p.prop_budget()
    assert engaged >= 0 and clear_of_pin_a >= 0 and stack >= 0
    assert p.ROD_LEN - engaged == approx(130.5, abs=0.1)          # the window the spec quotes
    assert p.ROD_LEN + clear_of_pin_a == approx(142.1, abs=0.1)
    assert stack == approx(16.5, abs=0.1)
    assert p.FOOT_STACK == approx(29.6)


def test_a_160_rod_reaches_pin_a():
    """Negative control: condition 2 fails, and only condition 2."""
    engaged, clear_of_pin_a, stack = p.prop_budget(rod_len=160.0)
    assert clear_of_pin_a < -1.0
    assert engaged >= 0 and stack >= 0


def test_exposed_rod_is_the_stack_clearance_plus_the_spare_at_minimum():
    assert g.prop_exposed_rod(p.TILT_MIN) == approx(p.STACK_CLEARANCE + p.prop_budget()[2])
    assert g.prop_exposed_rod(p.TILT_MAX) - g.prop_exposed_rod(p.TILT_MIN) == approx(56.4, abs=0.1)


def test_prop_force():
    assert [g.prop_force(a) for a in ANGLES] == approx([98.0, 58.0, 37.0], abs=1.0)
    assert all(0 < g.prop_force(a) < p.PROP_FORCE_MAX for a in GRID)


@pytest.mark.xfail(strict=True, reason="spec-tilt §5.4 contradicts itself: 98 N doubles to 196 N, over PROP_FORCE_MAX -- README 'Prop force at doubled weight'")
def test_prop_force_at_doubled_weight():
    assert all(g.prop_force(a, 2 * p.TILT_WEIGHT_N) < p.PROP_FORCE_MAX for a in GRID)


# --- Printed prop parts -------------------------------------------------------------------


def test_frame_clevis():
    c = frame_clevis()
    assert c.is_valid and len(c.solids()) == 1
    assert c.bounding_box().max.Y == approx(0.0, abs=1e-6)          # nothing proud of the contact face
    assert c.bounding_box().min.Y == approx(-p.CLEVIS_PIN_DROP - p.CLEVIS_CHEEK_R)
    assert p.CLEVIS_GAP == approx(12.6)
    cheek = p.CLEVIS_GAP / 2 + p.CLEVIS_CHEEK_THK / 2
    assert contains(c, (0, -2.0, cheek)) and contains(c, (0, -p.CLEVIS_PIN_DROP - 6.0, -cheek))
    assert not contains(c, (0, -p.CLEVIS_PIN_DROP, cheek))          # pin hole
    assert not contains(c, (0, -2.0, 0)) and not contains(c, (-8.0, -2.0, 0))   # open for the eye
    assert not contains(c, (0, -2.0, 25.0))                          # open for the pin's head, washer and nut
    assert contains(c, (13.0, -2.0, 0)) and contains(c, (13.0, -2.0, 25.0))     # joined on the head side
    assert contains(c, (5.0, -2.0, 47.0)) and not contains(c, (0, -2.0, p.CLEVIS_BOLT_Z))   # flange, M5 hole


def test_prop_body():
    b = prop_body()
    assert b.is_valid and len(b.solids()) == 1
    assert bbox_size(b) == approx((p.PROP_BODY_DIA, p.PROP_BODY_DIA, p.PROP_BODY_LEN + p.PROP_BODY_DIA / 2), abs=0.02)
    assert not contains(b, (0, 0, 0))                                # eye
    assert contains(b, (0, 0, 8.0)) and not contains(b, (7.0, 0, 8.0))   # flat eye, solid above the bore
    assert not contains(b, (0, 0, 13.0)) and contains(b, (7.0, 0, 13.0))   # bore from 12.0 below pin A; round body
    assert not contains(b, (5.5, 0, 85.0)) and contains(b, (5.5, 0, 89.4))   # nut pocket, closed below
    assert contains(b, (5.5, 0, 80.0))                               # bridged ceiling takes the thrust


def test_prop_foot():
    f = prop_foot()
    assert f.is_valid and len(f.solids()) == 1
    assert f.bounding_box().max.Z == approx(p.FOOT_LEN)
    assert not contains(f, (0, 0, 0)) and contains(f, (0, 0, 6.0))   # eye, and the floor above it
    assert not contains(f, (6.0, 0, 15.0)) and contains(f, (0, 10.0, 15.0))   # round pocket, walled on +y
    assert not contains(f, (0, -10.0, 15.0))                         # window on -y
    assert contains(f, (6.0, 0, 25.0)) and not contains(f, (0, 0, 25.0))      # top wall, rod hole
    assert not contains(f, (9.0, 0, 5.0))                            # still a flat eye inside the cheeks
    assert p.FOOT_LEN - p.FOOT_WALL_THK - p.FOOT_POCKET_LEN > p.PIN_BLOCK_CHEEK_R


def test_knob_and_base_pin_block():
    k = knob()
    assert k.is_valid and len(k.solids()) == 1
    assert bbox_size(k)[2] == approx(p.KNOB_THK) and bbox_size(k)[0] <= p.KNOB_DIA
    assert not contains(k, (p.KNOB_DIA / 2 - 1.0, 0, 6.0)) and contains(k, (14.0, 0, 6.0))   # a scallop; the web
    assert not contains(k, (5.5, 0, 10.0)) and contains(k, (5.5, 0, 3.0))                     # nut pocket in the top
    b = base_pin_block()
    assert b.is_valid and len(b.solids()) == 1
    assert bbox_size(b) == approx((p.PIN_BLOCK_LEN, p.PROP_PIN_B_Y + p.PIN_BLOCK_CHEEK_R, p.PIN_BLOCK_WIDTH), abs=0.02)
    assert b.bounding_box().min.Y == approx(0.0, abs=1e-6)
    assert not contains(b, (0, p.PROP_PIN_B_Y, 9.0)) and contains(b, (0, 8.0, 9.0)) and not contains(b, (0, 8.0, 0))
    assert not contains(b, (p.PIN_BLOCK_HOLE_X, 2.5, p.PIN_BLOCK_HOLE_Z))


# --- §8.1, §8.3, §8.4: assembly, report, outputs --------------------------------------------


def test_tilt_group():
    group = tilt_group()
    assert "tilt" in COLOURS and set(PLACEHOLDERS) == {"base_ref"}
    labels = [child.label for child in group.children]
    assert len(labels) == len(set(labels))
    for label in ("hinge bracket +z", "hinge bracket -z", "hinge block +z", "hinge block -z", "cross-member",
                  "frame clevis", "base pin block", "base_ref", "prop body", "prop rod", "lock nut", "knob", "prop foot"):
        assert label in labels
    for part in group.children:
        assert part.is_valid and len(part.solids()) == 1, part.label


@pytest.mark.parametrize("incline", ANGLES)
def test_prop_is_strung_between_its_pins(incline):
    on_frame, prop = by_label(tilt_frame_parts(incline)), by_label(tilt_prop_parts(incline))
    assert prop["prop body"].distance_to(prop["lock nut"]) < 0.01     # locked up against the body
    assert on_frame["frame clevis"].distance_to(on_frame["cross-member"]) < 0.01
    pin_a, pin_b = g.prop_pin_a(incline), g.prop_pin_b(incline)
    assert not contains(prop["prop body"], tuple(pin_a)) and not contains(prop["prop foot"], tuple(pin_b))   # eyes on the pins
    assert contains(on_frame["pin A"], tuple(pin_a))


def test_assembly_takes_an_incline():
    tilted = assembly("frame", "tilt", incline=p.TILT_MAX)
    assert tilted["frame"].bounding_box().max.Y > assembly("frame")["frame"].bounding_box().max.Y


def test_report_flags_the_placeholder_and_lists_the_hardware():
    text = "\n".join(report())
    assert "base_ref   ** PLACEHOLDER" in text
    assert f"M8 threaded rod, {p.ROD_LEN:g} long" in text and "Base fasteners" in text


def test_setting_up_table():
    from checks import tilt_report

    text = "\n".join(tilt_report())
    for incline in (25.0, 27.5, 40.0, 55.0):
        assert f"{incline:7.1f}   {g.prop_length(incline):10.1f}   {g.prop_exposed_rod(incline):11.1f}" in text


def test_cut_list_has_the_cross_member_and_rod():
    text = write_cut_list().read_text()
    assert f"{p.XMEMBER_LEN:g} mm, ends square" in text and f"{p.ROD_LEN:g} mm" in text


@pytest.mark.parametrize("part, rotation, height", [
    (hinge_bracket(1), p.PRINT_ROT_HINGE_BRACKET[1], p.HINGE_BRKT_THK),
    (hinge_bracket(-1), p.PRINT_ROT_HINGE_BRACKET[-1], p.HINGE_BRKT_THK),
    (hinge_block(-1), p.PRINT_ROT_HINGE_BLOCK, p.HINGE_HEIGHT + p.HINGE_BLOCK_WIDTH / 2),
    (frame_clevis(), p.PRINT_ROT_CLEVIS, p.CLEVIS_PIN_DROP + p.CLEVIS_CHEEK_R),
    (base_pin_block(), p.PRINT_ROT_PIN_BLOCK, p.PROP_PIN_B_Y + p.PIN_BLOCK_CHEEK_R),
    (knob(), p.PRINT_ROT_KNOB, p.KNOB_THK),
])
def test_print_rotation_puts_the_mating_face_on_the_bed(part, rotation, height):
    box = (Rot(*rotation) * part).bounding_box()
    assert (box.min.Z, box.max.Z) == approx((0.0, height), abs=1e-6)


def test_prop_body_prints_eye_up():
    box = (Rot(*p.PRINT_ROT_PROP_BODY) * prop_body()).bounding_box()
    assert box.min.Z == approx(-p.PROP_BODY_LEN) and box.max.Z == approx(p.PROP_BODY_DIA / 2)
