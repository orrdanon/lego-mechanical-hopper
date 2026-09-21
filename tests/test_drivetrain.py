"""drivetrain-spec §12 -- the correction, the radial envelope, the belt in
the pulley, the lug in the groove, whole-loop clearances and loop geometry."""

import math

import pytest
from build123d import Location
from pytest import approx

import geometry as g
import params as p
from assembly import drivetrain_group, plates_group, slats_group
from parts.belt import belt_band, belt_loop, belt_segment, belt_wrapped
from parts.shaft_set import shaft_set, shaft_set_with
from parts.slat import slat
from utils import bbox_size, clash, contains

C = p.CENTRE_DIST
ARC = math.pi * p.PULLEY_PD / 2   # pitch-line length of each arc, 60.0


# --- §12.1 The correction ---------------------------------------------------------


def test_belt_back_is_od_plus_backing():
    assert g.belt_back_radius() == approx(p.PULLEY_OD / 2 + p.BELT_BACK_THICKNESS, abs=1e-9)
    assert g.belt_back_radius() == approx(19.947, abs=1e-3)


def test_belt_is_one_thickness_from_tooth_tip_to_back():
    assert g.belt_back_radius() - g.belt_tooth_tip_radius() == approx(p.BELT_THICKNESS)


def test_belt_teeth_sit_in_the_grooves():
    assert g.belt_tooth_tip_radius() < p.PULLEY_OD / 2


def test_pitch_line_is_inside_the_backing():
    assert p.PULLEY_OD / 2 < p.PULLEY_PD / 2 < g.belt_back_radius()


def test_belt_teeth_do_not_bottom_out():
    assert p.PULLEY_GROOVE_BOTTOM_R < g.belt_tooth_tip_radius()


# --- §12.2 Radial envelope, all from §9.1 -------------------------------------------


def test_radial_stations():
    assert g.belt_tooth_tip_radius() == approx(17.547, abs=1e-3)
    assert g.tab_tip_radius() == approx(16.347, abs=1e-3)
    assert g.cleat_tip_radius() == approx(34.947, abs=1e-3)
    assert g.guide_rim_radius() == approx(19.447, abs=1e-3)
    assert g.guide_groove_bottom_radius() == approx(14.447, abs=1e-3)


def test_tabs_clear_the_drum():
    assert g.tab_tip_radius() >= p.DRUM_DIA / 2 + p.DRUM_TAB_CLEAR


def test_overhanging_belt_teeth_clear_the_flare():
    assert g.belt_tooth_tip_radius() >= p.PULLEY_SKIRT_R + p.BELT_TOOTH_CLEAR


def test_guide_groove_stays_above_the_drum():
    assert g.guide_groove_bottom_radius() > p.DRUM_DIA / 2


def test_returning_cleats_clear_the_plates():
    assert p.SHAFT_HEIGHT_ABOVE_PLATE - g.cleat_tip_radius() > 5.0
    assert p.SHAFT_HEIGHT_ABOVE_PLATE - g.cleat_tip_radius() == approx(13.05, abs=0.01)


# --- §12.4 Mesh: belt in pulley -------------------------------------------------------

ON_PULLEY = Location((0, 0, p.BELT_SPACING / 2))


def test_belt_model_meshes_with_the_standard_groove():
    assert not clash(belt_wrapped(8).moved(ON_PULLEY), shaft_set())


def test_belt_model_is_not_shrunken_to_pass():
    assert g.belt_tooth_tip_radius() - p.PULLEY_GROOVE_BOTTOM_R < 0.1
    assert g.belt_tooth_tip_radius() - p.PULLEY_GROOVE_BOTTOM_R == approx(0.046, abs=1e-3)


def test_belt_half_a_pitch_out_of_phase_collides():
    half_pitch = Location((0, 0, 0), (0, 0, math.degrees(p.BELT_PITCH / p.PULLEY_PD)))
    assert clash(belt_wrapped(8).moved(ON_PULLEY * half_pitch), shaft_set())


def test_belt_segment():
    seg = belt_segment(8)
    assert seg.is_valid
    assert bbox_size(seg) == approx((8 * p.BELT_PITCH, p.BELT_THICKNESS, p.BELT_WIDTH), abs=0.02)
    assert seg.bounding_box().min.Y == approx(-p.TOOTH_HEIGHT, abs=1e-6)
    assert contains(seg, (1.5, -0.6, 0))       # a tooth, half a pitch from the centre
    assert not contains(seg, (0, -0.6, 0))     # the land between teeth


def test_belt_band_is_backing_only_round_the_whole_loop():
    band = belt_band()
    assert band.is_valid
    assert bbox_size(band) == approx((C + 2 * g.belt_back_radius(), 2 * g.belt_back_radius(), p.BELT_WIDTH), abs=0.02)
    assert contains(band, (C / 2, p.PULLEY_PD / 2, 0))             # pitch line, carrying run
    assert contains(band, (C / 2, -p.PULLEY_PD / 2, 0))            # return run
    assert not contains(band, (C / 2, g.belt_tooth_tip_radius() + 0.5, 0))   # no teeth
    assert not clash(band.moved(ON_PULLEY), shaft_set())           # rests on the OD, doesn't cut it


def test_belt_loop_carries_every_tooth():
    loop = belt_loop()
    assert loop.is_valid
    tooth_volume = (loop.volume - belt_band().volume) / (p.BELT_LOOP_LENGTH / p.BELT_PITCH)
    assert tooth_volume == approx(belt_segment(1).volume - p.BELT_PITCH * p.BELT_BACK_THICKNESS * p.BELT_WIDTH, rel=0.05)
    assert not clash(loop.moved(ON_PULLEY), shaft_set())           # meshes with the tail pulley as placed


# --- §12.5 Guide: lug in groove ---------------------------------------------------------


def _slat_mid_head_arc():
    return slat(False).moved(g.loop_at(C + ARC / 2))


def test_lug_runs_clear_in_the_groove():
    assert not clash(_slat_mid_head_arc(), shaft_set().moved(g.at(C, 0)))


def test_zero_clearance_groove_only_touches_the_lug():
    """Why the spec's control can't be used as written: a straight lug in a
    revolved groove of its own section meets it along lines, not in volume.
    See README.md "Lug-in-groove control"."""
    flush = shaft_set_with(groove_flank_clear=0.0, groove_tip_clear=0.0).moved(g.at(C, 0))
    assert not clash(_slat_mid_head_arc(), flush)
    assert _slat_mid_head_arc().distance_to(flush) < 1e-6


def test_tighter_groove_collides_with_the_lug():
    tight = shaft_set_with(groove_flank_clear=-p.GROOVE_FLANK_CLEAR, groove_tip_clear=-p.GROOVE_TIP_CLEAR)
    assert clash(_slat_mid_head_arc(), tight.moved(g.at(C, 0)))


@pytest.mark.parametrize("sign", [1, -1])
def test_guide_allows_its_lateral_play_and_no_more(sign):
    play = p.GROOVE_FLANK_CLEAR / math.cos(math.radians(p.LUG_ANGLE / 2))
    assert play == approx(0.707, abs=1e-3)
    head = shaft_set().moved(g.at(C, 0))
    assert not clash(_slat_mid_head_arc().moved(Location((0, 0, sign * 0.9 * play))), head)
    assert clash(_slat_mid_head_arc().moved(Location((0, 0, sign * 1.1 * play))), head)


# --- §12.6 Whole-loop clearances ------------------------------------------------------------


@pytest.mark.parametrize("takeup", [p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX])
def test_every_slat_clears_the_drivetrain_and_plates(takeup):
    """The expensive test. Real slat geometry; the tail plate, shaft and shaft
    set slide together and the slats follow the loop."""
    fixed = list(drivetrain_group(takeup=takeup).children) + list(plates_group(takeup=takeup).children)
    slats = slats_group(detail=True, takeup=takeup).children
    assert len(slats) == p.SLAT_COUNT
    for s in slats:
        for part in fixed:
            assert not clash(s, part), f"{s.label} hits {part.label} at takeup {takeup}"


@pytest.mark.parametrize("phase", [0.0, p.SLAT_PITCH / 2])
def test_neighbouring_slats_never_close_up(phase):
    """Slats sit outside the pitch line, so they fan apart round a pulley:
    the gap between neighbours is never less than on the straight runs."""
    nominal = p.SLAT_PITCH - p.SLAT_WIDTH
    assert nominal == approx(1.0)
    solids = {cleated: slat(cleated) for cleated in (False, True)}
    slats = [solids[g.is_cleated(i)].moved(g.loop_at(i * p.SLAT_PITCH + phase)) for i in range(p.SLAT_COUNT)]
    gaps = [a.distance_to(b) for a, b in zip(slats, slats[1:] + slats[:1])]
    assert min(gaps) == approx(nominal, abs=1e-6)
    assert max(gaps) > 2 * nominal          # and it opens on the pulleys, 2.96 between the bottom corners


def test_takeup_moves_the_tail_plate_shaft_and_shaft_set_together():
    takeup = p.TAIL_TAKEUP_MAX
    shift = g.at(g.tail_shaft_t(takeup), 0).position - g.at(0, 0).position
    assert shift.length == approx(takeup)
    for group in (drivetrain_group, plates_group):
        moved, nominal = group(takeup=takeup).children, group().children
        assert (moved[0].center() - nominal[0].center() - shift).length < 1e-6     # the tail end slides
        assert (moved[-1].center() - nominal[-1].center()).length < 1e-6           # the head end doesn't


# --- §12.7 Loop geometry ------------------------------------------------------------------------


def test_loop_agrees_with_at_on_the_carrying_run():
    back = g.belt_back_radius()
    assert (g.loop_at(0).position - g.at(0, back).position).length < 1e-9
    assert (g.loop_at(C / 2).position - g.at(C / 2, back).position).length < 1e-9
    assert (g.loop_at(C / 2).x_axis.direction - g.run_direction()).length < 1e-9


def test_loop_closes():
    assert (g.loop_at(p.BELT_LOOP_LENGTH - 1e-9).position - g.loop_at(0).position).length < 1e-6


def test_loop_length_is_the_belt():
    assert 2 * C + math.pi * p.PULLEY_PD == approx(p.BELT_LOOP_LENGTH, abs=1e-9)
    assert ARC == approx(60.0, abs=1e-9)   # each arc is exactly 20 teeth of pitch line


@pytest.mark.parametrize("station", [C, C + ARC, 2 * C + ARC])
def test_loop_is_continuous_through_every_station(station):
    before, after = g.loop_at(station - 1e-9), g.loop_at(station + 1e-9)
    assert (before.position - after.position).length < 1e-6
    assert (before.x_axis.direction - after.x_axis.direction).length < 1e-6


def test_loop_arcs_are_about_the_shaft_axes_at_the_belt_back():
    for s, end in ((C + ARC / 2, "head"), (2 * C + 1.5 * ARC, "tail")):
        frame = g.loop_at(s)
        radial = frame.position - g.shaft_axis(end)
        assert radial.length == approx(g.belt_back_radius())
        assert (frame.y_axis.direction - radial.normalized()).length < 1e-9   # +y out of the belt back
    assert (g.loop_at(C + ARC / 2).y_axis.direction - g.run_direction()).length < 1e-9


def test_return_run_travels_tailward_with_its_back_to_the_plates():
    frame = g.loop_at(C + ARC + C / 2)
    assert (frame.position - g.at(C / 2, -g.belt_back_radius()).position).length < 1e-9
    assert (frame.x_axis.direction + g.run_direction()).length < 1e-9
    assert (frame.y_axis.direction + g.run_normal()).length < 1e-9
    assert frame.z_axis.direction.Z == approx(1.0)


def test_tail_shaft_t():
    assert g.tail_shaft_t() == 0.0
    assert g.tail_shaft_t(p.TAIL_TAKEUP_MAX) == approx(-p.TAIL_TAKEUP_MAX)   # positive is away from the head
    assert g.tail_shaft_t(p.TAIL_TAKEUP_MIN) == approx(-p.TAIL_TAKEUP_MIN)
    for bad in (p.TAIL_TAKEUP_MIN - 0.1, p.TAIL_TAKEUP_MAX + 0.1):
        with pytest.raises(ValueError):
            g.tail_shaft_t(bad)


def test_takeup_changes_both_runs_and_the_loop_still_closes():
    for takeup in (p.TAIL_TAKEUP_MIN, p.TAIL_TAKEUP_MAX):
        assert g.loop_length(takeup) == approx(p.BELT_LOOP_LENGTH + 2 * takeup)
        start, end = g.loop_at(0, takeup), g.loop_at(g.loop_length(takeup) - 1e-9, takeup)
        assert (start.position - end.position).length < 1e-6
        assert (start.position - g.at(g.tail_shaft_t(takeup), g.belt_back_radius()).position).length < 1e-9
