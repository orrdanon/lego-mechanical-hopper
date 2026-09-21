"""Phase 4 §8.6 -- the assembly framework itself, plus the cut list."""

import pytest

from assembly import COLOURS, GROUPS, assembly
from cut_list import write_cut_list
from export import export_all
from params import PLATE_LENGTH, PLATE_STATIONS, PLATE_WIDTH


def test_assembly_builds_every_group_by_default():
    assert set(assembly().keys()) == set(GROUPS)


def test_assembly_builds_only_named_groups():
    assert set(assembly("frame").keys()) == {"frame"}


def test_assembly_rejects_unknown_group():
    with pytest.raises(ValueError) as exc:
        assembly("drivetrain")
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


def test_export_still_writes_only_the_slats():
    names = sorted(path.stem for path in export_all())
    assert names == ["slat_cleated", "slat_plain"]
