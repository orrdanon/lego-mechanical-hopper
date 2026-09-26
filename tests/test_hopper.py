"""hopper-spec-v1.md §8 -- the hopper, its brushes, the carry rail and its
bridge. The measuring helpers are checks.py's own, so the two stay in step;
the whole-loop no-clash sweep with the hopper in it is
tests/test_drivetrain.py's."""

import math

import pytest
from build123d import Box, GeomType, Pos, Rot
from pytest import approx

import geometry as g
import params as p
from assembly import COLOURS, GROUPS, hopper_cavity_placed, hopper_group, hopper_parts, plates_group, report, slats_group
from checks import (
    PLYWOOD, _check_brushes, _check_hopper_plates, _check_hopper_tail, _check_hopper_tilt, _check_rail_bridge,
    contact_faces, hopper_fill, hopper_fixed, hopper_mass, hopper_slat_clearance, in_hopper, prop_loads,
    rim_edge_angle, rim_heights, slat_top_gaps, slats_over_rail,
)
from cut_list import write_cut_list
from export import hopper_prints
from parts.brush import brush_backing, brush_bristles
from parts.carry_rail import carry_rail, rail_bridge
from parts.hopper import (
    back_wall, corner_cleat, corner_cleat_places, front_wall, hopper_cavity, hopper_foot, liner, meter_clamp,
    seal_clamp, side_panel,
)
from parts.shaft_set import guide_groove_section
from utils import bbox_size, clash, contains, distance_within, level_fill, mass_properties, volume_cm3

TAKEUPS = (p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX)
GRID = [p.TILT_MIN + p.HOPPER_TABLE_STEP * i for i in range(int((p.TILT_MAX - p.TILT_MIN) / p.HOPPER_TABLE_STEP) + 1)]
PHASES = [p.SLAT_PITCH * i / 4 for i in range(4)]


def by_label(incline=p.INCLINE, **kwargs) -> dict:
    return {part.label: part for part in hopper_parts(incline, **kwargs)}


# --- §3 parameters, A1, A3, A6 ---------------------------------------------------------


def test_derived_parameters():
    assert p.HOPPER_SEAL_T_MIN == approx(g.tail_shaft_t(p.TAIL_TAKEUP_MIN) + p.SLAT_PITCH + 3.0) == approx(25.0)
    assert p.HOPPER_TAIL_KEEPOUT_T == approx(10.0)
    assert p.HOPPER_CHANNEL_W == approx(76.0) and p.BRUSH_LEN == approx(75.0)
    assert p.FLARE_TOP_H == approx(98.0) and p.LINER_FLANGE_TOP_H == approx(110.0)
    assert p.SEAL_ROOT_H == approx(22.148, abs=1e-3) and p.SEAL_ROOT_T == approx(21.530, abs=1e-3)
    assert p.BACK_NOTCH_H == approx(34.148, abs=1e-3) and p.FRONT_NOTCH_H == approx(63.0)
    assert p.RAIL_ARM_T == approx((76.5, 100.5)) and p.RAIL_ARM_T_CENTRE == approx(g.plate_t(1))
    assert p.HOPPER_FOOT_SLOT_DEPTH == approx(18.0) and p.HOPPER_FOOT_INNER_Z == approx(105.0)


def test_a1_seal_is_past_the_open_gaps():
    assert p.HOPPER_SEAL_T >= p.HOPPER_SEAL_T_MIN


def test_a3_seal_root_clears_the_cleats():
    assert p.SEAL_ROOT_H - p.CLEAT_HEIGHT == approx(10.15, abs=0.01)
    assert p.SEAL_ROOT_H - p.CLEAT_HEIGHT >= p.SEAL_CLEAT_CLEAR


def test_a6_rim_is_above_the_flare():
    assert p.RIM_FRONT_H >= p.FLARE_TOP_H + 5.0


# --- §2, §3 geometry -----------------------------------------------------------------------


def test_hopper_offset_is_measured_from_the_slat_top():
    assert g.slat_top_radius() == approx(22.947, abs=1e-3)
    assert g.hopper_offset(0.0) == approx(g.belt_back_radius() + p.SLAT_THICKNESS)
    assert g.hopper_offset(p.RIM_FRONT_H) - g.hopper_offset(0.0) == approx(p.RIM_FRONT_H)


def test_back_wall_plane():
    assert g.back_wall_t(0.0) == approx(19.59, abs=0.01)
    assert g.back_wall_rim_h() == approx(188.8, abs=0.05) and g.back_wall_t(g.back_wall_rim_h()) == approx(36.1, abs=0.05)
    assert g.back_wall_point(0.0) == approx((p.SEAL_ROOT_T, p.SEAL_ROOT_H))   # contains the root line
    up, into = g.back_wall_up(), g.back_wall_in()
    assert math.degrees(math.atan2(up[1], up[0])) == approx(p.BACK_WALL_ANGLE)
    assert up[0] * into[0] + up[1] * into[1] == approx(0.0, abs=1e-12) and into[0] > 0
    assert g.back_wall_t(0.0, -p.WALL_THICKNESS) == approx(g.back_wall_t(0.0) - p.WALL_THICKNESS / math.sin(math.radians(p.BACK_WALL_ANGLE)))
    for h in (0.0, 50.0, 150.0):
        assert g.back_wall_u(h) == approx(math.hypot(g.back_wall_t(h) - p.SEAL_ROOT_T, h - p.SEAL_ROOT_H) * math.copysign(1, h - p.SEAL_ROOT_H))


def test_rim_line():
    assert g.rim_h(p.HOPPER_FRONT_T) == approx(p.RIM_FRONT_H)
    assert g.rim_h(p.HOPPER_FRONT_T - 10.0) - p.RIM_FRONT_H == approx(10.0 * math.tan(math.radians(p.RIM_LEVEL_INCLINE)))
    assert g.rim_h(g.back_wall_t(g.back_wall_rim_h())) == approx(g.back_wall_rim_h(), abs=1e-6)


def test_run_coords_inverts_at():
    for incline in p.TILT_CHECK_ANGLES:
        point = g.at(123.0, -45.6, 7.8, incline).position
        assert g.run_coords(point, incline) == approx((123.0, -45.6, 7.8))


# --- A2 gaps under the seal -----------------------------------------------------------------


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_a2_slat_gaps_are_closed_under_the_hopper(takeup):
    straight = p.SLAT_PITCH * g.loop_length(takeup) / p.BELT_LOOP_LENGTH - p.SLAT_WIDTH
    limit = p.HOPPER_GAP_CLOSED + straight - (p.SLAT_PITCH - p.SLAT_WIDTH)   # README "Hopper resolutions"
    under = [width for phase in PHASES for t, width in slat_top_gaps(takeup, phase) if t >= p.HOPPER_SEAL_T]
    assert len(under) >= 4 * 5
    assert max(under) <= limit
    assert min(under) == approx(straight, abs=1e-6)          # every one of them is the straight-run gap


def test_a2_gaps_open_on_the_tail_arc():
    """Negative control: with the seal at t = 0 and the tail plate slid
    headward, the pairs still on the tail arc would be under it."""
    widest = max(width for phase in PHASES for t, width in slat_top_gaps(p.TAIL_TAKEUP_MIN, phase) if t >= 0.0)
    assert widest > p.HOPPER_GAP_OPEN


# --- A3, A4, A5 --------------------------------------------------------------------------------


def test_a3_seal_clamp_lowest_point():
    clamp = in_hopper(by_label()["seal clamp"])
    assert clamp.bounding_box().min.Y == approx(p.SEAL_CLAMP_LOW_H)
    assert clamp.bounding_box().min.Y >= p.CLEAT_HEIGHT + p.SEAL_CLEAT_CLEAR


def test_a4_wall_slopes_shed_parts_at_every_angle():
    assert [g.flare_slope(a) for a in p.TILT_CHECK_ANGLES] == approx([50.1, 57.2, 66.1], abs=0.05)
    assert [g.back_wall_slope(a) for a in p.TILT_CHECK_ANGLES] == approx([70.0, 55.0, 40.0])
    assert all(g.flare_slope(a) >= p.FLARE_SLOPE_MIN and g.back_wall_slope(a) >= p.BACK_WALL_SLOPE_MIN for a in GRID)


def test_a4_slopes_agree_with_the_solids():
    for incline in p.TILT_CHECK_ANGLES:
        parts = by_label(incline)
        flare = max((f for f in parts["liner +z"].faces() if f.geom_type == GeomType.PLANE), key=lambda f: f.area)
        inner = max((f for f in parts["back wall"].faces() if f.geom_type == GeomType.PLANE), key=lambda f: f.area)
        assert math.degrees(math.acos(abs(flare.normal_at().Y))) == approx(g.flare_slope(incline))
        assert math.degrees(math.acos(abs(inner.normal_at().Y))) == approx(g.back_wall_slope(incline))


def test_a5_rim_is_level_at_its_incline():
    assert rim_edge_angle(p.RIM_LEVEL_INCLINE) == approx(0.0, abs=p.RIM_LEVEL_TOL)
    assert [rim_edge_angle(a) for a in (p.TILT_MIN, p.TILT_MAX)] == approx([15.0, -15.0], abs=1e-6)


# --- A7, A8 parts ------------------------------------------------------------------------------


def test_a7_every_part_is_one_valid_solid():
    group = hopper_group()
    assert len(group.children) == 26
    for part in group.children:
        assert part.is_valid and len(part.solids()) == 1, part.label


def test_a8_liner():
    right, left = liner(1), liner(-1)
    assert bbox_size(right) == approx((110.28, 108.5, 70.0), abs=0.02)   # the spec's "about 110 x 109 x 70"
    assert 35.0 <= volume_cm3(right) <= 55.0 and volume_cm3(left) == approx(volume_cm3(right))
    assert right.bounding_box().min.Z == approx(0.0) and left.bounding_box().max.Z == approx(0.0)
    assert contains(right, (-50.0, 10.0, 1.5))                 # lower wall, 3.0 thick from the origin
    assert not contains(right, (-50.0, 10.0, -0.5)) and not contains(right, (-50.0, 10.0, 3.5))
    assert contains(right, (-50.0, 60.0, 35.5))                 # flare: its inner face is at 33.5 at this height
    assert not contains(right, (-50.0, 60.0, 32.5))
    assert contains(right, (-50.0, 102.0, 68.5)) and not contains(right, (-50.0, 102.0, 65.0))   # flange on the panel
    assert not contains(right, (0.2 - 0.5, 0.2, 0.2))          # bottom edge chamfered on the inner side


def test_a8_carry_rail():
    rail = carry_rail()
    assert bbox_size(rail) == approx((110.0, 15.447, 16.0), abs=0.02)
    assert 18.0 <= volume_cm3(rail) <= 28.0
    rim = g.guide_rim_radius()
    assert contains(rail, (50.0, -1.0, 7.0))                   # land
    assert not contains(rail, (50.0, -1.0, 0.0))               # groove
    assert contains(rail, (50.0, g.guide_groove_bottom_radius() - rim - 0.2, 0.0))
    assert not contains(rail, (0.5, -0.5, 7.0)) and contains(rail, (6.0, -0.5, 7.0))   # 45 deg lead-in at each end
    assert not contains(rail, (109.5, -0.5, 7.0))
    arm_x = p.RAIL_ARM_T_CENTRE - p.RAIL_T0
    assert not contains(rail, (arm_x + p.RAIL_INSERT_X, p.RAIL_BOTTOM_OFFSET - rim + 1.0, 0.0))   # M3 insert pocket


def test_rail_groove_is_the_guide_wheels():
    """The rail is cut by the shaft set's own section, so the two grooves
    are the same shape: the lug has the same play in each."""
    rail = carry_rail()
    rim = g.guide_rim_radius()
    for r, z in guide_groove_section():
        if r < rim:
            inset = 0.05 * (1 if z < 0 else -1)
            assert not contains(rail, (50.0, r - rim + 0.05, z + inset), eps=0.02)


def test_a8_rail_bridge():
    bridge = rail_bridge()
    assert bridge.is_valid and len(bridge.solids()) == 1
    assert 40.0 <= volume_cm3(bridge) <= 80.0
    assert bbox_size(bridge) == approx((p.RAIL_ARM_LEN, p.RAIL_ARM_OFFSET[1] - g.plate_top_offset(), 2 * p.RAIL_PAD_Z))
    assert contains(bridge, (0, 45.0, 0)) and not contains(bridge, (0, 20.0, 0))    # arm; nothing between the posts
    assert contains(bridge, (0, 20.0, 49.0)) and contains(bridge, (0, 2.0, 62.0))   # post, pad
    assert not contains(bridge, (p.RAIL_PAD_BOLT_X, 2.0, p.RAIL_PAD_BOLT_Z))       # pad bolt hole
    assert not contains(bridge, (p.RAIL_INSERT_X, 40.0, 0)) and not contains(bridge, (p.RAIL_INSERT_X, 50.5, 0.0))
    assert contains(bridge, (p.RAIL_INSERT_X, 50.5, 2.5))   # M3 clearance through the grip, counterbore below it


def test_plywood_parts():
    panel, wall, front = side_panel(1), back_wall(), front_wall()
    assert bbox_size(panel)[2] == approx(p.PANEL_THICKNESS)
    assert panel.bounding_box().min.Y == approx(0.0) and panel.bounding_box().max.X == approx(p.WALL_THICKNESS)
    assert side_panel(-1).bounding_box().max.Z == approx(0.0)
    assert bbox_size(front) == approx((p.WALL_THICKNESS, p.RIM_FRONT_H - p.SKIRT_GAP, 2 * p.HOPPER_HALF_W))
    assert not contains(front, (3.0, 30.0, 0.0)) and contains(front, (3.0, 30.0, 60.0))   # the notch
    assert bbox_size(wall)[2] == approx(2 * p.HOPPER_HALF_W)
    assert not contains(wall, (0.0, 0.0, 0.0), eps=0.02)                 # notched away at its origin


def test_brush_clamps():
    seal, meter = seal_clamp(), meter_clamp()
    for clamp in (seal, meter):
        assert clamp.is_valid and len(clamp.solids()) == 1
        assert bbox_size(clamp)[2] == approx(p.HOPPER_CLAMP_LEN)
    assert bbox_size(meter)[:2] == approx((p.METER_CLAMP_T, p.METER_CLAMP_H))
    assert meter.bounding_box().max.X == approx(0.0) and meter.bounding_box().min.Y == approx(p.BRUSH_FREE_LEN)
    assert not contains(meter, (-p.METER_CLAMP_T / 2, p.BRUSH_FREE_LEN + 4.0, 30.0))   # brush slot
    assert not contains(meter, (-p.METER_CLAMP_T / 2, p.METER_BOLT_H - p.METER_GAP, p.METER_BOLT_Z[0]))   # bolt slot


def test_feet_and_cleat():
    right, left = hopper_foot(1), hopper_foot(-1)
    assert bbox_size(right) == approx((p.HOPPER_FOOT_LEN, 30.0, 32.0))
    assert right.bounding_box().min.Y == approx(0.0) and left.volume == approx(right.volume)
    assert not contains(right, (0, 20.0, -14.5))                         # the panel slot
    assert not contains(right, (0, 2.0, 0)) and not contains(right, (0, 10.0, 3.0))   # M5 and its counterbore
    cleat = corner_cleat()
    assert bbox_size(cleat) == approx((p.CORNER_CLEAT_LEG, p.CORNER_CLEAT_LEN, p.CORNER_CLEAT_LEG))
    assert contains(cleat, (1.0, 5.0, -12.0)) and not contains(cleat, (10.0, 5.0, -10.0))
    assert len(corner_cleat_places()) == 8


def test_cleat_holes_line_up_with_the_panels_and_walls():
    """Every cleat's two holes are drilled in the board it bolts to."""
    parts = by_label(0.0)
    for name, *_ in corner_cleat_places():
        cleat = parts[name]
        wall = parts["front wall" if "front" in name else "back wall"]
        panel = parts["side panel +z" if "+z" in name else "side panel -z"]
        assert cleat.distance_to(wall) < 1e-6 and cleat.distance_to(panel) < 1e-6
        bolts = [e for e in cleat.edges() if e.geom_type == GeomType.CIRCLE]
        for edge in bolts:
            centre = edge.arc_center
            on_board = [board for board in (wall, panel) if board.distance_to(centre) < 1e-6]
            for board in on_board:
                assert not contains(board, tuple(centre), eps=0.05), f"{name}: no hole in {board.label}"


def test_mating_parts_touch_and_do_not_clash():
    parts = by_label()
    for a, b in [
        ("side panel +z", "hopper foot +z at 46"), ("side panel -z", "hopper foot -z at 126"),
        ("side panel +z", "liner +z"), ("side panel +z", "back wall"), ("side panel -z", "front wall"),
        ("back wall", "seal clamp"), ("front wall", "metering clamp"), ("carry rail", "rail bridge"),
        ("liner +z", "back wall"), ("liner -z", "front wall"), ("seal brush backing", "seal clamp"),
    ]:
        assert parts[a].distance_to(parts[b]) < 1e-6, (a, b)
    labels = list(parts)
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            assert not clash(parts[a], parts[b], tol=1e-3), (a, b)


# --- B capacity -------------------------------------------------------------------------------


def test_b1_capacity():
    fills = [hopper_fill(a) for a in p.TILT_CHECK_ANGLES]
    assert [f[0] for f in fills] == approx([2.05, 2.41, 1.87], abs=0.03)      # the spec's grid estimate
    assert all(f[0] >= p.HOPPER_CAPACITY[0] for f in fills) and fills[1][0] <= p.HOPPER_CAPACITY[1]
    assert [(round(f[1]), round(f[2])) for f in fills] == [(74, 103), (73, 114), (66, 106)]


def test_b1_rim_above_the_base():
    assert [rim_heights(a) for a in p.TILT_CHECK_ANGLES] == [
        approx((277.0, 309.0), abs=1.0), approx((289.0, 289.0), abs=1.0), approx((282.0, 250.0), abs=1.0),
    ]


def test_b2_a_low_rim_holds_too_little():
    """Negative control, the rim at 60, which params would refuse."""
    assert hopper_fill(p.TILT_MAX, p.HOPPER_CONTROL_RIM_H)[0] < p.HOPPER_CAPACITY[0]
    assert hopper_fill(p.TILT_MAX, p.HOPPER_CONTROL_RIM_H)[0] == approx(0.97, abs=0.1)   # the spec's estimate


def test_level_fill_of_a_box():
    """The helper on a solid with a known answer: a 100 x 100 x 100 open
    box tipped 45 deg about z holds half of itself."""
    cube = Rot(0, 0, 45) * Box(100, 100, 100)
    litres, centroid = level_fill(cube)
    assert litres == approx(0.5)
    assert centroid.X == approx(0.0, abs=1e-6) and centroid.Y < 0


def test_level_fill_uses_the_rim():
    """The cavity's rim is its most upward-facing face at every angle."""
    for incline in p.TILT_CHECK_ANGLES:
        cavity = hopper_cavity_placed(incline)
        up = sorted((f.normal_at().Y for f in cavity.faces() if f.geom_type == GeomType.PLANE), reverse=True)
        assert up[0] > up[1] + 0.1


def test_cavity_is_bounded_by_the_walls():
    cavity = hopper_cavity()
    assert cavity.is_valid and len(cavity.solids()) == 1
    parts = by_label(0.0)
    placed = hopper_cavity_placed(0.0)
    for label in ("liner +z", "liner -z", "back wall", "front wall", "side panel +z"):
        assert not clash(placed, parts[label], tol=1.0), label


# --- C clearances -----------------------------------------------------------------------------


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_c1_nearest_slat(takeup):
    d, s, part = hopper_slat_clearance(takeup)
    assert d >= p.HOPPER_SLAT_CLEAR
    assert d == approx(p.GUIDE_RIM_GAP) and part == "carry rail"   # the lands and the groove flanks, both 0.5


@pytest.mark.parametrize("sign", [1, -1])
def test_c1_slats_pushed_their_play_come_nearest_the_liner(sign):
    d, s, part = hopper_slat_clearance(0.0, sign * g.slat_lateral_play())
    assert d >= p.HOPPER_SLAT_CLEAR
    assert d == approx(p.SKIRT_INSET - p.CLEAT_LENGTH / 2 - g.slat_lateral_play(), abs=1e-3)   # 0.29, inherited from the skirts
    assert part == ("liner +z" if sign > 0 else "liner -z") and g.is_cleated(int(s.split()[1]))


def test_c1_incline_does_not_change_a_slat_clearance():
    """Why C1 is measured with the run along x: slats and hopper turn together."""
    distances = []
    for incline in (0.0, p.TILT_MIN, p.TILT_MAX):
        slat = {c.label: c for c in slats_group(detail=True, incline=incline).children}["slat 4"]
        distances.append(slat.distance_to(by_label(incline)["liner +z"]))
    assert distances == approx([distances[0]] * 3, abs=1e-6)


@pytest.mark.parametrize("takeup", TAKEUPS)
def test_c2_lugs_run_clear_in_the_rail(takeup):
    rail = by_label(0.0)["carry rail"]
    over = slats_over_rail(takeup, 0.0)
    assert len(over) >= 5
    assert not any(clash(s, rail) for s in over)


def test_c2_slats_run_half_a_millimetre_over_the_lands():
    rail = by_label()["carry rail"]
    for s in slats_over_rail():
        faces = contact_faces(s)
        assert len(faces) == 1
        assert p.RAIL_LAND_GAP[0] <= min(f.distance_to(rail) for f in faces) <= p.RAIL_LAND_GAP[1]


def test_c3_a_raised_rail_bites_into_the_slats():
    """Negative control: real interference, not a touch."""
    raised = by_label(rail_raise=1.0)["carry rail"]
    assert any(clash(s, raised, tol=1.0) for s in slats_over_rail())


def test_c4_brushes():
    _check_brushes()
    parts = by_label()
    seal = in_hopper(parts["seal brush bristles"])
    tip = min(seal.faces().filter_by(GeomType.PLANE), key=lambda f: f.center().Y)
    assert tip.center().Y == approx(-p.SEAL_BRUSH_INTERFERENCE)
    assert tip.center().X == approx(p.HOPPER_SEAL_T)            # the seal line
    meter = in_hopper(parts["metering brush bristles"])
    assert meter.bounding_box().min.Y == approx(p.METER_GAP)
    assert meter.bounding_box().min.Y - p.CLEAT_HEIGHT == approx(2.0)   # the cleats pass under it
    for setting in (p.METER_GAP_MIN, p.METER_GAP_MAX):
        moved = in_hopper(by_label(meter_gap=setting)["metering brush bristles"])
        assert moved.bounding_box().min.Y == approx(setting)


def test_c4_bristles_are_the_only_parts_that_touch_slats():
    slats = slats_group(detail=True).children
    parts = by_label()
    touching = {part for part in parts if any(clash(s, parts[part]) for s in slats)}
    assert touching == {"seal brush bristles"}


def test_c5_c6_c7_tail():
    _check_hopper_tail()


def test_c6_nothing_tailward_of_the_keepout():
    assert min(part.bounding_box().min.X for part in hopper_parts(0.0)) == approx(
        g.back_wall_t(p.SEAL_CLAMP_LOW_H, -p.SEAL_CLAMP_BACK), abs=1e-6
    )
    assert g.back_wall_t(p.SEAL_CLAMP_LOW_H, -p.SEAL_CLAMP_BACK) >= p.HOPPER_TAIL_KEEPOUT_T


def test_c8_plates():
    _check_hopper_plates()
    parts = by_label(0.0)
    plates = {c.label: c for c in plates_group(incline=0.0).children}
    assert parts["side panel +z"].distance_to(plates["plate 1 (support)"]) == approx(p.HOPPER_CLEAR)
    assert parts["hopper foot +z at 126"].distance_to(plates["plate 1 (support)"]) == approx(3.0)
    assert parts["rail bridge"].distance_to(plates["plate 1 (support)"]) < 1e-6    # it stands on it


def test_feet_stand_on_the_rails():
    from parts.frame import frame

    f = frame(0.0)
    for label, part in by_label(0.0).items():
        if label.startswith("hopper foot"):
            assert part.distance_to(f) < 1e-6 and not clash(part, f, tol=1e-3)


def test_c9_base_hinge_and_prop():
    _check_hopper_tilt()


def test_c10_rail_bridge_clears_the_returning_run():
    _check_rail_bridge()


def test_c10_bridge_clearance_is_the_returning_lugs():
    bridge = by_label(0.0)["rail bridge"]
    nearest = min(distance_within(bridge, s, 10.0) for s in slats_group(detail=True, incline=0.0).children)
    lug_tip = g.belt_back_radius() - p.LUG_DEPTH
    assert nearest == approx(lug_tip + p.RAIL_ARM_OFFSET[0], abs=1e-3)   # 3.95, under the arm


@pytest.mark.parametrize("part, name, rotation", hopper_prints(), ids=[name for _, name, _ in hopper_prints()])
def test_c11_every_printed_part_fits_the_bed(part, name, rotation):
    size = bbox_size(Rot(*rotation) * part)
    assert all(a <= b for a, b in zip(size, p.PRINT_BED))


@pytest.mark.parametrize("part, rotation, bottom", [
    (liner(1), p.PRINT_ROT_LINER[1], -70.0), (liner(-1), p.PRINT_ROT_LINER[-1], -70.0),   # the flange's outer face
    (meter_clamp(), p.PRINT_ROT_METER_CLAMP, 0.0),                                         # its mating face
    (hopper_foot(1), p.PRINT_ROT_HOPPER_FOOT, 0.0), (corner_cleat(), p.PRINT_ROT_CORNER_CLEAT, 0.0),
    (rail_bridge(), p.PRINT_ROT_RAIL_BRIDGE, -p.RAIL_ARM_LEN / 2),                         # its headward face
])
def test_print_rotation_puts_the_stated_face_down(part, rotation, bottom):
    assert (Rot(*rotation) * part).bounding_box().min.Z == approx(bottom)


def test_carry_rail_prints_groove_up():
    box = (Rot(*p.PRINT_ROT_CARRY_RAIL) * carry_rail()).bounding_box()
    assert box.max.Z == approx(0.0) and box.min.Z == approx(p.RAIL_BOTTOM_OFFSET - g.guide_rim_radius())


# --- D loads -------------------------------------------------------------------------------------


def test_d1_hopper_mass():
    mass, t, offset = hopper_mass()
    assert p.HOPPER_MASS_RANGE[0] <= mass <= p.HOPPER_MASS_RANGE[1]
    assert (t, offset) == approx((78.3, 61.9), abs=1.0)


def test_mass_properties_of_two_boxes():
    a, b = Box(10, 10, 10), Pos(100, 0, 0) * Box(10, 10, 10)
    mass, centre = mass_properties([a, b], [1.0, 3.0], [(0.004, Pos(0, 50, 0).position)])
    assert mass == approx(0.001 + 0.003 + 0.004)
    assert (centre.X, centre.Y) == approx((300 / 8, 200 / 8))


def test_d2_doubled_load_is_under_the_ceiling():
    """Frame, drive, hopper and a full load, doubled. The hopper spec left
    about 30 N at 25 deg for a motor; the drive takes 30.2 of it, so the
    margin is 0.04 N -- README "Hopper and drive together"."""
    forces = [g.prop_force(a, g.doubled(prop_loads(a))) for a in GRID]
    assert max(forces) <= p.PROP_FORCE_MAX
    assert forces[0] == max(forces) == approx(250.0, abs=0.1)
    assert g.prop_force(p.TILT_MIN, g.doubled([g.drive_load()])) == approx(30.2, abs=0.1)


def test_d2_the_load_helps_at_steep_angles():
    """The load's centroid is behind the hinge's line of action at 55. The
    spec's 98 -> 110 N at 25 and about 29 N at 55 were before the drive;
    with it, 112.8 -> 125.0 and 33.9."""
    assert g.prop_force(p.TILT_MIN, prop_loads(p.TILT_MIN)) == approx(125.0, abs=1.0)
    assert g.prop_force(p.TILT_MAX, prop_loads(p.TILT_MAX)) == approx(33.9, abs=1.0)
    assert g.prop_force(p.TILT_MAX, prop_loads(p.TILT_MAX)) < g.prop_force(p.TILT_MAX, prop_loads(p.TILT_MAX, False))


def test_d3_prop_stays_in_compression():
    for incline in GRID:
        for full in (False, True):
            assert g.prop_force(incline, prop_loads(incline, full)) >= p.PROP_FORCE_MIN


def test_prop_force_takes_a_list_of_loads():
    machine = g.prop_force(p.INCLINE)
    assert g.prop_force(p.INCLINE, g.machine_loads()) == machine
    assert g.prop_force(p.INCLINE, g.doubled(g.machine_loads())) == approx(2 * machine)
    split = [(m / 2, t, o) for m, t, o in g.machine_loads()] * 2
    assert g.prop_force(p.INCLINE, split) == approx(machine)
    assert g.frame_load()[0] * p.GRAVITY == approx(p.TILT_WEIGHT_N)
    assert g.drive_load()[0] * p.GRAVITY == approx(p.DRIVE_WEIGHT_N)


def test_the_two_machine_loads_are_the_drive_specs_combined_weight():
    """spec-drive §7 folds the frame and the drive into TILT_TOTAL_WEIGHT_N at
    one centre of gravity; the moment is linear, so two entries agree."""
    (m1, t1, o1), (m2, t2, o2) = g.machine_loads()
    assert (m1 + m2) * p.GRAVITY == approx(p.TILT_TOTAL_WEIGHT_N)
    assert (m1 * t1 + m2 * t2) / (m1 + m2) == approx(p.TILT_TOTAL_CG_T)
    assert (m1 * o1 + m2 * o2) / (m1 + m2) == approx(p.TILT_TOTAL_CG_OFFSET)
    total = [((m1 + m2), p.TILT_TOTAL_CG_T, p.TILT_TOTAL_CG_OFFSET)]
    for incline in p.TILT_CHECK_ANGLES:
        assert g.prop_force(incline) == approx(g.prop_force(incline, total))


# --- §9 framework ---------------------------------------------------------------------------------


def test_hopper_is_a_group_with_a_colour():
    assert "hopper" in GROUPS and "hopper" in COLOURS


def test_hopper_ignores_the_takeup():
    nominal, slid = hopper_group().children, hopper_group(takeup=p.TAIL_TAKEUP_MAX).children
    assert all((a.center() - b.center()).length < 1e-9 for a, b in zip(nominal, slid))


def test_materials():
    plywood = [part.label for part in hopper_parts() if part.label.startswith(PLYWOOD)]
    assert sorted(plywood) == ["back wall", "front wall", "side panel +z", "side panel -z"]


def test_whole_loop_set_leaves_out_only_the_bristles():
    assert {part.label for part in hopper_parts()} - {part.label for part in hopper_fixed()} == {
        "seal brush bristles", "metering brush bristles",
    }


def test_report_lists_the_hopper_hardware():
    lines = report()
    assert "Bought hardware, hopper" in lines
    assert any("Strip brush" in line for line in lines)


def test_cut_list_has_the_hopper_boards():
    text = write_cut_list().read_text()
    for title in ("Hopper side panel +z", "Hopper side panel -z", "Hopper back wall", "Hopper front wall"):
        assert title in text
