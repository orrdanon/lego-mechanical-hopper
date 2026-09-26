"""spec-pillow-blocks §5 -- the printed pillow block, the 608ZZ, the spacer
tube and the bearing coupon, alone and in the machine."""

import math

import pytest
from build123d import Location, Pos, Rot
from pytest import approx

import geometry as g
import params as p
from assembly import (
    bearings_group, belts_group, drivetrain_group, pillow_blocks_group, plates_group, report, slats_group,
    spacers_group,
)
from cut_list import write_cut_list
from parts.bearing import bearing
from parts.bridge_plate import bridge_plate
from parts.coupons import bearing_coupon, bearing_coupon_pocket_x
from parts.pillow_block import pillow_block
from parts.spacer import spacer
from utils import _overlap_volume, bbox_size, clash, contains, distance_within, min_distance, volume_cm3

TAKEUPS = (p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX)
H = p.SHAFT_HEIGHT_ABOVE_PLATE


# --- §2 Parameters ------------------------------------------------------------------


def test_derived_parameters():
    assert p.BEARING_Z == approx(50.0)
    assert (p.PB_INBOARD_FACE_Z, p.PB_OUTBOARD_FACE_Z) == approx((-3.5, 5.0))
    assert p.SPACER_LENGTH == approx(16.8)
    assert p.BC_LENGTH == approx(150.0) and p.BC_THICKNESS == approx(8.5)
    assert p.PB_INSERT_DIA == p.PULLEY_INSERT_DIA
    assert p.BEARING_Z + p.PB_BOLT_Z == approx(40.25)


# --- §5.1 Pillow block, alone ------------------------------------------------------


def test_pillow_block_is_valid_and_one_solid():
    b = pillow_block()
    assert b.is_valid
    assert len(b.solids()) == 1


def test_pillow_block_bbox():
    assert bbox_size(pillow_block()) == approx((44.0, 63.0, 21.0), abs=0.01)
    assert bbox_size(pillow_block())[1] == approx(p.SHAFT_HEIGHT_ABOVE_PLATE + p.PB_BOSS_RADIUS)


def test_pillow_block_volume():
    assert 15.0 <= volume_cm3(pillow_block()) <= 18.0
    assert volume_cm3(pillow_block()) == approx(16.65, rel=0.03)   # pinned on the first build


def test_pocket_centre_is_empty():
    assert not contains(pillow_block(), (0, H, 0))


def test_rib_count_and_phase():
    b, r = pillow_block(), 11.05
    assert contains(b, (0, H + r, 0))                  # on the +y rib
    for i in range(p.PB_RIB_COUNT):
        on = math.radians(i * 360 / p.PB_RIB_COUNT)
        between = on + math.radians(180 / p.PB_RIB_COUNT)
        assert contains(b, (r * math.sin(on), H + r * math.cos(on), 0))
        assert not contains(b, (r * math.sin(between), H + r * math.cos(between), 0))


def test_lip():
    b = pillow_block()
    assert contains(b, (0, H + 10.3, 4.25))            # the ledge
    assert not contains(b, (0, H + 7.0, 4.25))         # the lip hole


def test_pocket_is_open_on_the_inboard_face():
    assert not contains(pillow_block(), (0, H, -3.4))


def test_insert_pockets_are_blind():
    b = pillow_block()
    for x in (-p.PB_BOLT_X, p.PB_BOLT_X):
        assert not contains(b, (x, 3.0, p.PB_BOLT_Z))
        assert contains(b, (x, 6.8, p.PB_BOLT_Z))      # the skin above


def test_ribs_ramp_in_from_the_mouth():
    b, r = pillow_block(), 11.05
    assert not contains(b, (0, H + r, p.PB_INBOARD_FACE_Z + 0.2), eps=0.02)   # still inside the wall at the mouth
    assert contains(b, (0, H + r, p.PB_INBOARD_FACE_Z + p.PB_RIB_LEAD_IN + 0.1), eps=0.02)


# --- §5.2 Bearing in block ------------------------------------------------------------


def seated() -> object:
    return Pos(0, H, 0) * bearing()


def test_bearing_press_fit_is_rib_interference_only():
    volume = _overlap_volume(pillow_block(), seated())
    assert 1.0 <= volume <= 10.0
    assert volume == approx(3.34, rel=0.03)            # pinned on the first build


def test_negative_control_clear_ribs_only_touch_the_lip():
    clear = pillow_block(22.2)
    assert _overlap_volume(clear, seated()) == 0.0
    assert clear.distance_to(seated()) == approx(0.0, abs=0.01)


def test_clash_volume_falls_as_the_ribs_open():
    volumes = [_overlap_volume(pillow_block(d), seated()) for d in (21.6, 21.8, 22.0)]
    assert volumes[0] > volumes[1] > volumes[2]


# --- §5.3 Spacer and bearing ------------------------------------------------------------


def test_spacer():
    s = spacer()
    assert s.is_valid
    assert bbox_size(s) == approx((11.0, 11.0, 16.8), abs=0.01)
    assert 0.64 <= volume_cm3(s) <= 0.70
    assert s.bounding_box().min.Z == approx(0.0)        # origin on the bearing face


def test_bearing():
    b = bearing()
    assert b.is_valid
    assert bbox_size(b) == approx((22.0, 22.0, 7.0), abs=0.01)
    assert 2.25 <= volume_cm3(b) <= 2.32


# --- §3.4 Bearing coupon ------------------------------------------------------------------


def test_bearing_coupon():
    c = bearing_coupon()
    assert c.is_valid and len(c.solids()) == 1
    assert bbox_size(c) == approx((p.BC_LENGTH, p.BC_WIDTH, p.BC_THICKNESS), abs=0.01)
    assert c.bounding_box().min.Z == approx(0.0, abs=1e-6)


def test_bearing_coupon_pockets_are_the_blocks_pockets():
    """Same cutter, so each pocket grips a bearing as a block at that rib-tip
    diameter would, lip on the bed."""
    c = bearing_coupon()
    y = -p.BC_WIDTH / 2 + p.BC_POCKET_EDGE
    for i, dia in enumerate(p.BC_RIB_TIP_DIAS):
        x = bearing_coupon_pocket_x(i)
        pocket_bearing = Pos(x, y, p.BEARING_WIDTH / 2 + p.PB_LIP_THICKNESS) * bearing()
        assert _overlap_volume(c, pocket_bearing) == approx(_overlap_volume(pillow_block(dia), seated()), abs=1e-3)
        assert contains(c, (x, y + 10.3, 0.75)) and not contains(c, (x, y + 7.0, 0.75))   # lip on the bed


# --- §2.5 End plates ------------------------------------------------------------------


def test_end_plates_carry_the_pillow_block_holes():
    z = p.BEARING_Z + p.PB_BOLT_Z
    for x in (-p.PB_BOLT_X, p.PB_BOLT_X):
        for sz in (-z, z):
            assert not contains(bridge_plate("bearing"), (x, -p.PLATE_THICKNESS / 2, sz))
            assert contains(bridge_plate("support"), (x, -p.PLATE_THICKNESS / 2, sz))


def test_cut_list_has_the_pillow_block_holes():
    text = write_cut_list().read_text()
    assert f"4 x {p.PLATE_PB_HOLE_DIA:g} mm, centres {2 * (p.BEARING_Z + p.PB_BOLT_Z):g} mm apart across" in text


def test_report_lists_the_pillow_block_hardware():
    text = "\n".join(report())
    assert "608ZZ bearing" in text and "pillow_blocks (4)" in text and "spacers (4)" in text


# --- §5.4 In the machine ------------------------------------------------------------------


def sweep_min(parts_of, takeup: float, limit: float, shift: float = 0.0) -> float:
    """Least distance from any real slat, shifted `shift` across the machine,
    to any member of `parts_of(takeup)`. The parts move by -shift instead:
    the same relative motion, and moving a real slat copies it."""
    parts = [part.moved(Location((0, 0, -shift))) for part in parts_of(takeup=takeup).children]
    return min(min_distance(s, parts, limit) for s in slats_group(detail=True, takeup=takeup).children)


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_slats_clear_the_blocks_at_worst_case_play(takeup):
    """14: the slat ends toward the towers across the lug's play (5.79), and
    the foot top to the returning cleat tips (6.05)."""
    play = g.slat_lateral_play()
    least = min(sweep_min(pillow_blocks_group, takeup, 10.0, shift) for shift in (play, -play))
    assert least >= p.PB_SLAT_CLEAR_MIN
    assert least == approx(6.5 - play, abs=0.01)
    assert sweep_min(pillow_blocks_group, takeup, 10.0) == approx(6.05, abs=0.01)


def test_returning_run_clears_the_foot():
    """15."""
    assert p.SHAFT_HEIGHT_ABOVE_PLATE - g.cleat_tip_radius() - p.PB_FOOT_HEIGHT > p.PB_SLAT_CLEAR_MIN
    assert p.SHAFT_HEIGHT_ABOVE_PLATE - g.cleat_tip_radius() - p.PB_FOOT_HEIGHT == approx(6.05, abs=0.01)


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_slats_clear_the_spacers(takeup):
    """16: nearest are the saddle tab tips."""
    least = sweep_min(spacers_group, takeup, 15.0)
    assert least >= p.PB_SLAT_CLEAR_MIN
    assert least == approx(g.tab_tip_radius() - p.SPACER_OD / 2, abs=0.01)


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_bearing_parts_clear_the_belts_and_shaft_sets(takeup):
    """17, and 18 for the one designed near-contact: each spacer faces its
    shaft set's end across half the end play."""
    others = list(belts_group(takeup=takeup).children)
    others += [c for c in drivetrain_group(takeup=takeup).children if c.label.endswith("shaft set")]
    for group in (pillow_blocks_group, bearings_group, spacers_group):
        for part in group(takeup=takeup).children:
            end, kind = part.label.split()[:2]
            for other in others:
                assert not clash(part, other), f"{part.label} / {other.label}"
                gap = distance_within(part, other, 1.0)
                if kind == "spacer" and other.label == f"{end} shaft set":
                    assert gap == approx(p.SHAFT_END_PLAY / 2, abs=0.01)
                else:
                    assert gap >= 1.0, f"{part.label} / {other.label}"


def by_label(parts) -> dict:
    return {part.label: part for part in parts}


def block_cases():
    return [(takeup, end, side) for takeup in TAKEUPS for end in ("tail", "head") for side in ("+z", "-z")]


@pytest.mark.parametrize("takeup, end, side", block_cases())
def test_block_sits_on_its_plate(takeup, end, side):
    """19, 20."""
    block = by_label(pillow_blocks_group(takeup=takeup).children)[f"{end} block {side}"]
    plates = plates_group(takeup=takeup).children
    plate = plates[0] if end == "tail" else plates[-1]
    assert not clash(block, plate)
    assert block.distance_to(plate) == approx(0.0, abs=1e-6)
    local = block.moved(plate.location.inverse()).bounding_box()
    assert local.min.Y == approx(0.0, abs=1e-6)                    # coplanar with the top face
    assert -p.PLATE_WIDTH / 2 <= local.min.X and local.max.X <= p.PLATE_WIDTH / 2
    assert -p.PLATE_LENGTH / 2 <= local.min.Z and local.max.Z <= p.PLATE_LENGTH / 2
    for x in (-p.PB_BOLT_X, p.PB_BOLT_X):
        hole = (block.location * Location((x, -p.PLATE_THICKNESS / 2, p.PB_BOLT_Z))).position
        assert not contains(plate, (hole.X, hole.Y, hole.Z))


@pytest.mark.parametrize("takeup, end, side", block_cases())
def test_bearing_axis_is_the_shaft_axis(takeup, end, side):
    """21."""
    block = by_label(pillow_blocks_group(takeup=takeup).children)[f"{end} block {side}"]
    shaft = by_label(drivetrain_group(takeup=takeup).children)[f"{end} shaft"].location.position
    sign = 1 if side == "+z" else -1
    for z in (-1.0, 1.0):   # two points, so the axis direction too
        point = (block.location * Location((0, H, z))).position
        assert math.hypot(point.X - shaft.X, point.Y - shaft.Y) < 0.01
        assert point.Z == approx(sign * (p.BEARING_Z + z), abs=0.01)


@pytest.mark.parametrize("end", ["tail", "head"])
def test_blocks_on_a_shaft_are_mirror_images(end):
    """22: lips outboard at +/-55.0, inboard faces at +/-46.5."""
    blocks = by_label(pillow_blocks_group().children)
    t = 0.0 if end == "tail" else p.CENTRE_DIST
    tower = g.at(t, 13.0).position
    for side, sign in (("+z", 1), ("-z", -1)):
        block = blocks[f"{end} block {side}"]
        box = block.bounding_box()
        assert (box.max.Z if sign > 0 else -box.min.Z) == approx(55.0, abs=0.01)
        assert contains(block, (tower.X, tower.Y, sign * 46.55))
        assert not contains(block, (tower.X, tower.Y, sign * 46.45))
        assert contains(block, (tower.X, tower.Y, sign * 54.95))
        assert not contains(block, (tower.X, tower.Y, sign * 55.05))


def test_tail_parts_move_with_the_takeup_and_head_parts_do_not():
    for group in (pillow_blocks_group, bearings_group, spacers_group):
        nominal, slid = by_label(group().children), by_label(group(takeup=p.TAIL_TAKEUP_MAX).children)
        for label in nominal:
            moved = (nominal[label].center() - slid[label].center()).length
            assert moved == approx(p.TAIL_TAKEUP_MAX if label.startswith("tail") else 0.0, abs=1e-9)


# --- Printing ---------------------------------------------------------------------------


def test_pillow_block_prints_lip_face_down():
    box = (Rot(*p.PRINT_ROT_PILLOW_BLOCK) * pillow_block()).bounding_box()
    assert box.min.Z == approx(-p.PB_OUTBOARD_FACE_Z)
    assert box.max.Z == approx(-p.PB_FOOT_INBOARD_Z)
