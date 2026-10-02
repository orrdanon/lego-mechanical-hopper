"""Phase 4 §8.6 -- the assembly framework itself, plus the cut list."""

import pytest

from assembly import COLOURS, GROUPS, assembly
from cut_list import write_cut_list
from export import export_all
from params import BELT_SPACING, LUG_DEPTH, PLATE_LENGTH, PLATE_STATIONS, PLATE_WIDTH, SADDLE_TAB_DEPTH, SLAT_COUNT


def test_assembly_builds_every_group_by_default():
    assert set(assembly().keys()) == set(GROUPS)


def test_assembly_builds_only_named_groups():
    assert set(assembly("frame").keys()) == {"frame"}


def test_assembly_rejects_unknown_group():
    with pytest.raises(ValueError) as exc:
        assembly("skirts")
    assert "frame" in str(exc.value) and "plates" in str(exc.value)


def test_plates_group_is_valid_and_labelled():
    plates = assembly("plates")["plates"]
    assert plates.is_valid
    assert plates.label == "plates"
    assert len(plates.children) == PLATE_STATIONS


def test_detail_flag_is_accepted_by_every_group():
    assert set(assembly(detail=True).keys()) == set(GROUPS)


def test_every_group_has_a_fixed_colour():
    assert set(COLOURS) == set(GROUPS)


def test_cut_list_lists_the_plate():
    text = write_cut_list().read_text()
    assert f"{PLATE_LENGTH:g} x {PLATE_WIDTH:g}" in text
    assert f"x{PLATE_STATIONS}" in text


def test_export_writes_every_printed_part():
    """drivetrain-spec §14.5, spec-tilt §8.4, spec-pillow-blocks §1, spec-drive §8, hopper-spec §9.9.
    Bought parts, plywood, the base reference, the hopper's cavity and
    reference/ are never written."""
    paths = export_all()
    assert sorted(path.stem for path in paths) == [
        "base_pin_block", "bearing_coupon", "carry_rail", "corner_cleat", "frame_clevis", "guide_coupon",
        "hinge_block_L", "hinge_block_R", "hinge_bracket_L", "hinge_bracket_R", "hopper_foot_L", "hopper_foot_R",
        "hopper_liner_L", "hopper_liner_R", "knob", "metering_clamp", "motor_bracket", "pillow_block", "prop_body",
        "prop_foot", "rail_bridge", "ring_coupon", "seal_clamp", "shaft_set", "slat_cleated", "slat_plain", "spacer",
    ]   # with the printed parts of spec-tilt §8.4, spec-pillow-blocks §1, spec-drive §8 and hopper-spec §9.9
    for path in paths:
        assert path.parent.name == "out"
        assert path.stat().st_size > 0


# --- Drivetrain groups -- drivetrain-spec §11 ------------------------------------


def test_drivetrain_group_is_two_shafts_and_two_shaft_sets():
    group = assembly("drivetrain")["drivetrain"]
    assert group.is_valid
    assert sorted(child.label for child in group.children) == [
        "head shaft", "head shaft set", "tail shaft", "tail shaft set",
    ]


def test_belts_group_is_two_bands_at_the_belt_spacing():
    group = assembly("belts")["belts"]
    assert group.is_valid
    centres = sorted(child.bounding_box().center().Z for child in group.children)
    assert centres == pytest.approx([-BELT_SPACING / 2, BELT_SPACING / 2])


def test_slats_group_places_every_slat_alternately_cleated():
    group = assembly("slats")["slats"]
    assert len(group.children) == SLAT_COUNT
    volumes = [child.volume for child in group.children]
    assert all(volumes[i] > volumes[i + 1] for i in range(0, SLAT_COUNT, 2))   # boxes: cleated, plain, ...


def test_slats_group_detail_uses_real_slats():
    from parts.slat import slat

    group = assembly("slats", detail=True)["slats"]
    assert group.children[0].volume == pytest.approx(slat(True).volume)
    assert group.children[1].volume == pytest.approx(slat(False).volume)



# --- Picking single members: 'group:pattern' ------------------------------------------


def test_assembly_picks_members_by_label():
    built = assembly("drivetrain:tail shaft", "drivetrain:*shaft set", "slats:slat 1?")
    assert [c.label for c in built["drivetrain:tail shaft"].children] == ["tail shaft"]
    assert sorted(c.label for c in built["drivetrain:*shaft set"].children) == ["head shaft set", "tail shaft set"]
    assert len(built["slats:slat 1?"].children) == 10


def test_assembly_rejects_a_pattern_matching_nothing():
    with pytest.raises(ValueError) as exc:
        assembly("drivetrain:pulley")
    assert "tail shaft set" in str(exc.value)


def test_slat_stand_ins_touch_only_what_the_real_slats_touch():
    """The default slats are quick boxes for the viewer. They must not show
    clashes the real slats don't have: with the hopper's liners and carry
    rail in particular, which one bounding box per slat ran into."""
    from assembly import belts_group, hopper_parts, slats_group
    from utils import _overlap_volume

    others = hopper_parts() + list(belts_group().children)
    stand_ins, real = slats_group().children, slats_group(detail=True).children
    for box, true in zip(stand_ins, real):
        for other in others:
            if _overlap_volume(box, other) > 1e-3:
                assert _overlap_volume(true, other) > 1e-3, f"{box.label} / {other.label}"


def test_slat_stand_in_keeps_the_real_slats_extent():
    """Same length, width and top as the real slat; the bottom is the tab
    tips, 0.4 above the lug's, which points into the loop."""
    from assembly import _slat_box
    from parts.slat import slat

    for cleated in (False, True):
        box, true = _slat_box(cleated).bounding_box(), slat(cleated).bounding_box()
        assert (box.size.X, box.size.Z, box.max.Y) == pytest.approx((true.size.X, true.size.Z, true.max.Y))
        assert box.min.Y - true.min.Y == pytest.approx(LUG_DEPTH - SADDLE_TAB_DEPTH)
