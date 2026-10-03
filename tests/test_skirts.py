"""spec-skirts.md §8 -- the skirts, rail B and the split support stations.
The measuring helpers are checks.py's own, so the two stay in step; the
whole-loop no-clash sweep with the skirts in it is tests/test_drivetrain.py's."""

import pytest
from build123d import Rot
from pytest import approx

import geometry as g
import params as p
from assembly import COLOURS, GROUPS, hopper_parts, plates_group, report, skirts_group, skirts_parts
from checks import (
    RAIL_A, RAIL_B, SKIRT_PLYWOOD, _check_arm_fitting_path, _check_rail_b, _check_rail_fitting_path, _check_rail_joint,
    _check_rails_clear_the_wheels, _check_rails_in_the_cheeks, _check_skirt_continuity, _check_skirt_parameters,
    _check_skirts_clear_the_head, _check_skirts_loads, _check_skirts_parts, _check_uprights_clear_the_slat_ends,
    arm_path, arm_path_obstacles, contact_faces, head_arc_skirt_clearance, rail_path, rail_shaft_set_clearance,
    skirt_slat_clearance, skirts_mass, slats_over_rail,
)
from cut_list import write_cut_list
from parts.carry_rail import carry_rail, carry_rail_b, rail_insert_t
from parts.skirt import skirt, skirt_holes
from parts.station import skirt_upright, station_arm, station_post, upright_cbore_depth, upright_height
from utils import bbox_size, clash, contains, volume_cm3

TAKEUPS = (p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX)


def by_label(incline=p.INCLINE, **kwargs) -> dict:
    return {part.label: part for part in skirts_parts(incline, **kwargs)}


# --- S parameters ------------------------------------------------------------------------


def test_s1_cleat_end_to_skirt():
    assert p.CLEAT_LENGTH == 73.0
    assert p.SKIRT_INSET - p.CLEAT_LENGTH / 2 - g.slat_lateral_play() == approx(0.79, abs=0.01)
    assert p.SKIRT_INSET - p.CLEAT_LENGTH / 2 - g.slat_lateral_play() >= p.SKIRT_CLEAT_CLEAR_MIN


def test_s2_slat_end_always_runs_under_the_skirt():
    assert p.SLAT_LENGTH / 2 - g.slat_lateral_play() - p.SKIRT_INSET == approx(1.29, abs=0.01)
    assert p.SLAT_LENGTH / 2 - g.slat_lateral_play() - p.SKIRT_INSET >= p.SKIRT_SLAT_LAP_MIN


def test_s3_s4_derived_parameters():
    _check_skirt_parameters()
    assert p.STATION_T == approx((88.5, 177.0, 265.5)) and p.SKIRT_STATIONS == approx((177.0, 265.5))
    assert (p.RAIL_T1, p.RAIL_B_T0) == approx((176.75, 177.25))
    assert p.SKIRT_T0 == approx(136.0) and p.SKIRT_INSET + p.SKIRT_THICKNESS == p.RAIL_POST_Z[0]
    assert rail_insert_t(*RAIL_A[:2]) == approx([82.5, 94.5, 171.0])
    assert rail_insert_t(*RAIL_B[:2]) == approx([183.0, 259.5, 271.5])
    assert upright_height() == approx(46.947, abs=1e-3) and upright_cbore_depth() == approx(7.947, abs=1e-3)


# --- R rails --------------------------------------------------------------------------------


def test_r1_r2_rail_b():
    _check_rail_b()


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_r1_lugs_run_clear_in_rail_b(takeup):
    rail = by_label(0.0)["carry rail B"]
    over = slats_over_rail(takeup, 0.0, RAIL_B)
    assert len(over) >= 7
    assert not any(clash(s, rail) for s in over)


def test_r1_slats_run_half_a_millimetre_over_rail_b():
    rail = by_label()["carry rail B"]
    for s in slats_over_rail(rail=RAIL_B):
        assert min(f.distance_to(rail) for f in contact_faces(s)) == approx(p.GUIDE_RIM_GAP, abs=0.05)


def test_r2_a_raised_rail_b_bites():
    raised = by_label(rail_raise=1.0)["carry rail B"]
    assert any(clash(s, raised, tol=1.0) for s in slats_over_rail(rail=RAIL_B))


def test_r3_r4_joint_and_coverage():
    _check_rail_joint()


def test_r5_rails_clear_the_wheels():
    _check_rails_clear_the_wheels()
    assert rail_shaft_set_clearance() == approx(4.88, abs=0.05)   # rail B's bottom corner to the head guide wheel


def test_r5_control_rail_b_too_long():
    assert rail_shaft_set_clearance(0.0, p.RAIL_B_T1_CONTROL) < p.RAIL_WHEEL_CLEAR


def test_r6_rails_sit_between_the_cheeks():
    _check_rails_in_the_cheeks()


def test_rail_b_part():
    rail = carry_rail_b()
    length = p.RAIL_B_T1 - p.RAIL_B_T0
    assert rail.is_valid and len(rail.solids()) == 1
    assert bbox_size(rail) == approx((length, 15.447, 16.0), abs=0.02)
    assert 28.0 <= volume_cm3(rail) <= 37.0
    assert contains(rail, (1.0, -0.2, 7.0)) and not contains(rail, (0.1, -0.2, 7.0))    # joint relief at the tail
    assert not contains(rail, (length - 0.5, -0.5, 7.0))                                 # lead-in at the head
    y = p.RAIL_SIDE_INSERT_OFFSET - g.guide_rim_radius()
    for t in rail_insert_t(*RAIL_B[:2]):
        assert not contains(rail, (t - p.RAIL_B_T0, y, p.GUIDE_WIDTH / 2 - 1.0))


def test_both_rails_share_the_section():
    """The same groove: a slice through either rail is the same area."""
    a, b = carry_rail(), carry_rail_b()
    assert volume_cm3(a) / (p.RAIL_T1 - p.RAIL_T0) == approx(volume_cm3(b) / (p.RAIL_B_T1 - p.RAIL_B_T0), rel=0.01)


# --- K skirts ------------------------------------------------------------------------------


def test_k1_channel_continues_from_the_front_wall():
    _check_skirt_continuity()


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_k2_nearest_slat_is_the_rail(takeup):
    d, s, part = skirt_slat_clearance(takeup)
    assert d >= p.HOPPER_SLAT_CLEAR
    assert d == approx(p.GUIDE_RIM_GAP) and part.startswith("carry rail")


def test_k2_slats_rounding_the_head_clear_the_skirt_ends():
    """0.53, not the 0.31 a sharp corner would give: the slat's edge
    chamfers -- README "Skirt resolutions"."""
    assert head_arc_skirt_clearance() >= p.HOPPER_SLAT_CLEAR
    assert head_arc_skirt_clearance() == approx(0.53, abs=0.02)


@pytest.mark.parametrize("sign", [1, -1])
def test_k3_tight_pair_is_a_cleat_end(sign):
    d, s, part = skirt_slat_clearance(0.0, sign * g.slat_lateral_play())
    assert d == approx(p.SKIRT_INSET - p.CLEAT_LENGTH / 2 - g.slat_lateral_play(), abs=0.01)
    side = "+z" if sign > 0 else "-z"
    assert part in (f"liner {side}", f"skirt {side}") and g.is_cleated(int(s.split()[1]))


def test_k4_t5_head_end_and_hopper():
    _check_skirts_clear_the_head()


def test_skirt_part():
    right, left = skirt(1), skirt(-1)
    assert bbox_size(right) == approx((214.0, 26.5, 6.0))
    assert right.bounding_box().min.Z == approx(0.0) and left.bounding_box().max.Z == approx(0.0)
    assert volume_cm3(left) == approx(volume_cm3(right))
    assert not contains(right, (100.0, 0.2, 0.2)) and contains(right, (100.0, 0.2, 1.0))    # inner bottom edge chamfer
    for x, y in skirt_holes():
        assert not contains(right, (x, y, 3.0)) and not contains(right, (x + 3.0, y, 0.5))   # hole, and its countersink
        assert contains(right, (x + 3.0, y, 5.5))                                         # no sink on the outer face


def test_skirt_bolts_line_up_with_the_uprights():
    parts = by_label(0.0)
    for side in ("+z", "-z"):
        for t in p.SKIRT_STATIONS:
            upright = parts[f"skirt upright {side} at {t:g}"]
            assert upright.distance_to(parts[f"skirt {side}"]) < 1e-6
            for h in p.SKIRT_BOLT_H:
                z = (p.SKIRT_INSET + p.SKIRT_THICKNESS + 1.0) * (1 if side == "+z" else -1)
                point = g.at(t, g.hopper_offset(h), z, 0.0).position
                assert not contains(upright, tuple(point)), (side, t, h)


# --- T stations -------------------------------------------------------------------------------


def test_t2_uprights_clear_the_slat_ends():
    _check_uprights_clear_the_slat_ends()


def test_t3_arms_slide_in_with_the_belt_on():
    _check_arm_fitting_path()


def test_t3_control_the_hopper_panel_blocks_the_arm_at_88_5():
    path = arm_path(p.STATION_T[0])
    blocked = {part.label for part in arm_path_obstacles(p.STATION_T[0], panel_on=True) if clash(path, part, tol=1.0)}
    assert "side panel +z" in blocked


def test_t4_rails_go_in_from_above():
    _check_rail_fitting_path()


def test_t4_control_rail_a_in_its_own_place_meets_the_seal_clamp():
    clamp = {part.label: part for part in hopper_parts(0.0)}["seal clamp"]
    assert clash(rail_path(RAIL_A), clamp, tol=0.01)
    assert not clash(rail_path(RAIL_A, p.RAIL_FIT_SHIFT), clamp, tol=0.01)


def test_posts_stand_on_their_plates():
    parts = by_label(0.0)
    plates = {c.label: c for c in plates_group(incline=0.0).children}
    for i, t in ((2, 177.0), (3, 265.5)):
        plate = next(plate for label, plate in plates.items() if label.startswith(f"plate {i}"))
        for side in ("+z", "-z"):
            post = parts[f"station post {side} at {t:g}"]
            assert post.distance_to(plate) < 1e-6 and not clash(post, plate, tol=1e-3)


def test_mating_parts_touch_and_do_not_clash():
    parts = by_label()
    for t in p.SKIRT_STATIONS:
        for side in ("+z", "-z"):
            for a, b in [
                (f"station arm at {t:g}", f"station post {side} at {t:g}"),
                (f"skirt upright {side} at {t:g}", f"station arm at {t:g}"),
                (f"skirt upright {side} at {t:g}", f"skirt {side}"),
            ]:
                assert parts[a].distance_to(parts[b]) < 1e-6, (a, b)
    labels = list(parts)
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            assert not clash(parts[a], parts[b], tol=1e-3), (a, b)
    hopper = {part.label: part for part in hopper_parts()}
    for name in SKIRT_PLYWOOD:
        assert not clash(parts[name], hopper["front wall"], tol=1e-3)


def test_upright_screw_engages_the_whole_insert():
    """The long M3: from its counterbore's floor through upright and arm to
    the bottom of the post's insert is exactly UPRIGHT_SCREW_LEN."""
    arm = p.RAIL_ARM_OFFSET[1] - p.RAIL_ARM_OFFSET[0]
    assert (upright_height() - upright_cbore_depth()) + arm + p.M3_INSERT_DEPTH == approx(p.UPRIGHT_SCREW_LEN)


# --- V parts ---------------------------------------------------------------------------------


def test_v1_v2_parts():
    _check_skirts_parts()


def test_station_post():
    post = station_post()
    assert post.is_valid and len(post.solids()) == 1
    assert bbox_size(post) == approx((p.RAIL_ARM_LEN, 36.0, 20.0))
    assert contains(post, (0, 20.0, 5.0)) and contains(post, (0, 2.0, 18.0))           # column, pad
    assert not contains(post, (p.RAIL_PAD_BOLT_X, 2.0, p.RAIL_PAD_BOLT_Z - p.RAIL_POST_Z[0]))   # pad bolt
    insert_z = p.STATION_POST_INSERT_Z - p.RAIL_POST_Z[0]
    assert not contains(post, (p.STATION_POST_INSERT_X, 35.0, insert_z))              # insert pocket
    assert contains(post, (p.STATION_POST_INSERT_X, 30.0, insert_z))                  # blind


def test_station_arm():
    arm = station_arm()
    assert arm.is_valid and len(arm.solids()) == 1
    assert bbox_size(arm) == approx((p.RAIL_ARM_LEN, 24.0, 2 * p.RAIL_ARM_HALF_W))
    cheek = p.GUIDE_WIDTH / 2 + p.RAIL_CHEEK_CLEAR + p.RAIL_CHEEK_T / 2
    assert contains(arm, (0, 20.0, cheek)) and contains(arm, (0, 20.0, -cheek))       # the cheeks
    assert not contains(arm, (0, 20.0, 0.0))                                           # the rail goes between
    y = p.RAIL_SIDE_INSERT_OFFSET - p.RAIL_ARM_OFFSET[0]
    assert not contains(arm, (p.RAIL_INSERT_X, y, cheek)) and contains(arm, (p.RAIL_INSERT_X, y, -cheek))   # +z cheek only
    for z in (-p.STATION_POST_INSERT_Z, p.STATION_POST_INSERT_Z):
        assert not contains(arm, (p.STATION_POST_INSERT_X, 8.0, z))                    # the post bolts
    assert contains(arm, (p.RAIL_INSERT_X, 2.0, 0.0))     # nothing under the arm for the rail any more


def test_skirt_upright():
    upright = skirt_upright()
    assert upright.is_valid and len(upright.solids()) == 1
    assert bbox_size(upright) == approx((p.RAIL_ARM_LEN, upright_height(), 10.0))
    z = p.STATION_POST_INSERT_Z - p.RAIL_POST_Z[0]
    assert not contains(upright, (p.STATION_POST_INSERT_X, 1.0, z))                    # the long M3, top to bottom
    assert contains(upright, (p.STATION_POST_INSERT_X + 2.5, 1.0, z))                  # clearance, not the counterbore
    assert not contains(upright, (p.STATION_POST_INSERT_X + 2.5, upright_height() - 1.0, z))


@pytest.mark.parametrize("part, rotation, bottom", [
    (station_post(), p.PRINT_ROT_STATION, -p.RAIL_ARM_LEN / 2),
    (station_arm(), p.PRINT_ROT_STATION, -p.RAIL_ARM_LEN / 2),
    (skirt_upright(), p.PRINT_ROT_UPRIGHT, 0.0),
    (carry_rail_b(), p.PRINT_ROT_CARRY_RAIL, p.RAIL_BOTTOM_OFFSET - g.guide_rim_radius()),
])
def test_print_rotation_puts_the_stated_face_down(part, rotation, bottom):
    assert (Rot(*rotation) * part).bounding_box().min.Z == approx(bottom)


# --- M loads ------------------------------------------------------------------------------------


def test_m1_mass():
    _check_skirts_loads()
    mass, t, offset = skirts_mass()
    assert mass == approx(0.315, abs=0.01)
    assert (t, offset) == approx((229.0, 4.7), abs=1.0)


# --- framework -----------------------------------------------------------------------------------


def test_skirts_is_a_group_with_a_colour():
    assert "skirts" in GROUPS and "skirts" in COLOURS


def test_skirts_ignore_the_takeup():
    nominal, slid = skirts_group().children, skirts_group(takeup=p.TAIL_TAKEUP_MAX).children
    assert all((a.center() - b.center()).length < 1e-9 for a, b in zip(nominal, slid))


def test_skirts_group_members():
    labels = sorted(part.label for part in skirts_group().children)
    assert len(labels) == 1 + 2 * 5 + 2
    assert labels.count("carry rail B") == 1 and set(SKIRT_PLYWOOD) <= set(labels)


def test_report_lists_the_skirts_hardware():
    lines = report()
    assert "Bought hardware, skirts" in lines
    assert any("countersunk" in line for line in lines)


def test_cut_list_has_the_skirt_strips():
    text = write_cut_list().read_text()
    assert "Skirt strips  x2" in text and "214 x 26.5" in text
