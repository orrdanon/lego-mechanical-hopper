"""Phase 4 §8.6 -- the assembly framework itself, plus the cut list."""

import pytest

from assembly import COLOURS, GROUPS, assembly
from cut_list import write_cut_list
from export import export_all
from params import BELT_SPACING, PLATE_LENGTH, PLATE_STATIONS, PLATE_WIDTH, SLAT_COUNT


def test_assembly_builds_every_group_by_default():
    assert set(assembly().keys()) == set(GROUPS)


def test_assembly_builds_only_named_groups():
    assert set(assembly("frame").keys()) == {"frame"}


def test_assembly_rejects_unknown_group():
    with pytest.raises(ValueError) as exc:
        assembly("hopper")
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
    """drivetrain-spec §14.5. Bought parts and reference/ are never written."""
    paths = export_all()
    assert sorted(path.stem for path in paths) == [
        "guide_coupon", "ring_coupon", "shaft_set", "slat_cleated", "slat_plain",
    ]
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
