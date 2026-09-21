"""Human-facing pre-export gate: runs every acceptance assertion from the
CAD spec and prints a pass/fail line per check. The same assertions are
expressed as pytest tests under tests/; this is the manual runner."""

import math
import sys

from itertools import combinations

from build123d import GeomType, Location

import geometry as g
import params as p
from assembly import COLOURS, GROUPS, assembly, drivetrain_group, plates_group, slats_group
from parts.belt import belt_band, belt_segment, belt_wrapped
from parts.bridge_plate import bridge_plate
from parts.coupons import guide_coupon, ring_coupon
from parts.frame import frame
from parts.shaft import shaft
from parts.shaft_set import shaft_set, shaft_set_with
from parts.slat import pulley_envelope, slat
from profile import groove_half, groove_junctions, pulley_section, tooth_face, tooth_half
from utils import bbox_size, clash, contains, volume_cm3


def _check_parameter_consistency():
    assert p.BELT_LOOP_LENGTH % p.BELT_PITCH == 0
    assert p.BELT_LOOP_LENGTH % p.SLAT_PITCH == 0
    assert p.SLAT_COUNT == 46
    assert abs(2 * p.CENTRE_DIST + math.pi * p.PULLEY_PD - p.BELT_LOOP_LENGTH) < 1e-6
    assert (p.BELT_WIDTH - p.PULLEY_FACE_WIDTH) / 2 >= 2.0
    assert p.CLEAT_LENGTH < p.SLAT_LENGTH
    assert p.SADDLE_TAB_LENGTH / p.BELT_PITCH <= 2.5
    assert p.SLAT_WIDTH < p.SLAT_PITCH                          # slats must not touch
    assert p.SLAT_PITCH - p.SLAT_WIDTH <= 3.0                   # gap smaller than a 1x1 plate
    assert p.BEARING_SPACING > p.BELT_SPACING + p.BELT_WIDTH
    assert p.SHAFT_LENGTH > p.BEARING_SPACING + 40


def _check_returning_run_clearance():
    """The clearance that caused rev B: the returning run's cleats must not
    strike the mounting plate."""
    assert p.SHAFT_HEIGHT_ABOVE_PLATE > g.cleat_tip_radius() + 5.0


def _check_saddle_clearances():
    tab_inner_face = (p.BELT_WIDTH - p.SADDLE_INTERFERENCE) / 2
    assert tab_inner_face - p.PULLEY_FACE_WIDTH / 2 >= 1.5             # tab vs pulley
    tab_outer_face = tab_inner_face + p.SADDLE_TAB_THICKNESS
    assert p.SLAT_LENGTH / 2 - (p.BELT_SPACING / 2 + tab_outer_face) >= 2.0   # rim


def _check_geometry_module():
    tol = 0.01
    assert abs(g.run_direction().length - 1.0) < 1e-9
    assert abs(g.run_normal().length - 1.0) < 1e-9
    assert abs(g.run_direction().dot(g.run_normal())) < 1e-9
    assert abs(g.belt_back_radius() - 19.947) < tol              # corrected, drivetrain-spec §0
    assert abs(g.at(0).position.Y) < 1e-9                      # offset origin is the shaft axis
    assert abs(g.at(0, g.belt_back_radius()).position.Y - g.belt_back_radius() * math.cos(math.radians(p.INCLINE))) < tol
    assert g.slat_t(0) == 0.0
    assert abs(g.slat_t(3) - 54.0) < 1e-9
    assert g.is_cleated(0) and not g.is_cleated(1) and g.is_cleated(2) and not g.is_cleated(3)
    assert sum(g.is_cleated(i) for i in range(p.SLAT_COUNT)) == 23


def _check_slat_bounding_box():
    tol = 0.02
    plain = bbox_size(slat(False))
    assert all(abs(a - b) < tol for a, b in zip(plain, (17.0, 7.0, 80.0)))
    cleated = bbox_size(slat(True))
    assert all(abs(a - b) < tol for a, b in zip(cleated, (17.0, 19.0, 80.0)))


def _check_volume():
    assert 4.20 <= volume_cm3(slat(False)) <= 4.90             # recomputed for the lug, the 3.6 tabs and the 17.0 width
    assert 10.25 <= volume_cm3(slat(True)) <= 11.25
    assert volume_cm3(slat(True)) > volume_cm3(slat(False))


def _check_probe_points():
    s = slat(False)
    assert contains(s, (0, 1.5, 0))
    assert contains(s, (0, -3, 18.35))      # inner tab
    assert contains(s, (0, -3, 35.65))      # outer tab
    assert not contains(s, (0, -3, 27))     # saddle mouth, hollow
    assert not contains(s, (0, -3, 10))     # between the lug and the inner tab
    assert not contains(s, (0, 8, 0))
    assert contains(s, (0, -2, 0))          # guide lug, drivetrain-spec §6.3
    assert contains(s, (0, -3.8, 0))
    assert not contains(s, (0, -2, 5.0))    # lug flank tapers
    assert not contains(s, (0, -4.5, 0))    # below the lug tip
    assert not contains(s, (6.0, -2, 0))    # lug is short along the run

    c = slat(True)
    assert contains(c, (0, 8, 0))
    assert contains(c, (0, 14, 30))
    assert not contains(c, (0, 8, 39))      # cleat stops short of the end
    assert not contains(c, (6, 8, 0))       # cleat is narrow in x


def _check_clearance():
    assert not clash(slat(False), pulley_envelope())
    assert not clash(slat(True), pulley_envelope())


def _check_manifold():
    assert slat(False).is_valid
    assert slat(True).is_valid


# --- Phase 4: frame, bridge plates, assembly framework ---------------------


def _placed_plate(i: int):
    return bridge_plate(g.plate_role(i)).moved(g.at(g.plate_t(i), g.plate_top_offset()))


def _check_frame_geometry():
    assert abs(g.rail_top_offset() - (-57.0)) < 1e-9
    assert abs(g.rail_lateral() - 127.0) < 1e-9
    assert abs(g.plate_t(0)) < 1e-9
    assert abs(g.plate_t(p.PLATE_STATIONS - 1) - p.CENTRE_DIST) < 1e-9
    assert [g.plate_role(i) for i in range(p.PLATE_STATIONS)] == ["bearing", "support", "support", "support", "bearing"]
    try:
        g.plate_t(p.PLATE_STATIONS)
    except IndexError:
        pass
    else:
        raise AssertionError("plate_t must raise IndexError past the last station")


def _check_frame():
    f = frame()
    assert f.is_valid
    assert len(f.solids()) == 4
    theta = math.radians(p.INCLINE)
    longest = p.FRAME_LENGTH * math.cos(theta) + p.FRAME_PROFILE * math.sin(theta)
    assert abs(sorted(bbox_size(f))[-1] - longest) < 0.5     # inclined, see README "Frame bounding box"
    local = f.moved(g.at(g.frame_t_centre(), g.rail_top_offset()).inverse())
    assert all(abs(a - b) < 0.02 for a, b in zip(bbox_size(local), (p.FRAME_LENGTH, p.FRAME_PROFILE, p.FRAME_WIDTH)))


def _check_plates_sit_on_rails():
    f = frame()
    for i in range(p.PLATE_STATIONS):
        plate = _placed_plate(i)
        assert not clash(plate, f, tol=1.0)
        assert plate.distance_to(f) < 0.01                    # touching, not floating


def _check_plates_span_rails():
    assert abs(bbox_size(bridge_plate())[2] - p.PLATE_LENGTH) < 0.02
    assert p.PLATE_LENGTH > 2 * g.rail_lateral()
    f = frame()
    for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X):
        for z in (-p.PLATE_BOLT_Z, p.PLATE_BOLT_Z):
            probe = g.at(g.plate_t(0) + x, g.rail_top_offset() - p.FRAME_SLOT_DEPTH / 2, lateral=z).position
            assert not contains(f, (probe.X, probe.Y, probe.Z))   # hole sits over an open slot


def _check_plates_dont_collide():
    placed = [_placed_plate(i) for i in range(p.PLATE_STATIONS)]
    for a, b in combinations(placed, 2):
        assert not clash(a, b)


def _check_assembly_framework():
    assert set(assembly().keys()) == set(GROUPS)
    assert set(assembly("frame").keys()) == {"frame"}
    assert set(COLOURS) == set(GROUPS)
    try:
        assembly("hopper")
    except ValueError:
        pass
    else:
        raise AssertionError("assembly() must reject unknown group names")
    assert assembly("plates")["plates"].is_valid


# --- Drivetrain: profile, shaft set, belt, guide, loop -- drivetrain-spec §4.4, §12


# Read from the manufacturer's B-rep (reference/htd3m_40t_40015040.stp). If
# the rebuild misses them the construction is wrong, not the tolerance.
_FILE_JUNCTIONS = [
    (0.2381, 17.4994),   # A bottom / flank arc
    (0.9408, 18.1019),   # B flank arc / straight
    (0.9992, 18.5174),   # C straight / tip arc
    (1.2006, 18.6815),   # D tip arc / OD
]


def _assert_tangent_chain(edges):
    for a, b in zip(edges, edges[1:]):
        assert (a @ 1 - b @ 0).length < 1e-6
        assert (a % 1).get_angle(b % 0) < 0.5


def _check_belt_tooth():
    assert p.FLANK_CENTRE_Y == p.BELT_PLD                       # exact: one physical quantity
    assert abs(p.TOOTH_HEIGHT - 1.171) < 1e-3
    assert abs(p.LAND_WIDTH - 0.914) < 1e-3
    assert tooth_face().is_valid
    _assert_tangent_chain(tooth_half())


def _check_pulley_groove():
    assert p.PULLEY_GROOVE_COMP == 0.0 and p.PULLEY_OD_COMP == 0.0, "junction data is for the uncompensated groove"
    for got, want in zip(groove_junctions(), _FILE_JUNCTIONS):
        assert math.dist(got, want) < 0.005
    _assert_tangent_chain(groove_half())
    assert abs(p.PULLEY_GROOVE_DEPTH - 1.2165) < 1e-4
    assert abs(p.PULLEY_GROOVE_DEPTH - 1.219) < 0.005           # agrees with the file
    ps = pulley_section()
    assert ps.is_valid
    arcs = [e for e in ps.outer_wire().edges() if e.geom_type == GeomType.CIRCLE]
    assert sum(abs(e.radius - p.PULLEY_GROOVE_TIP_R) < 1e-6 for e in arcs) == 80
    assert sum(abs(e.radius - p.PULLEY_GROOVE_FLANK_R) < 1e-6 for e in arcs) == 80
    try:
        pulley_section(24)
    except ValueError:
        pass
    else:
        raise AssertionError("pulley_section must refuse any tooth count but 40")


def _check_belt_radius_correction():
    assert abs(g.belt_back_radius() - (p.PULLEY_OD / 2 + p.BELT_BACK_THICKNESS)) < 1e-9
    assert abs(g.belt_back_radius() - 19.947) < 1e-3
    assert abs(g.belt_back_radius() - g.belt_tooth_tip_radius() - p.BELT_THICKNESS) < 1e-9
    assert g.belt_tooth_tip_radius() < p.PULLEY_OD / 2             # teeth sit in grooves
    assert p.PULLEY_OD / 2 < p.PULLEY_PD / 2 < g.belt_back_radius()   # pitch line inside backing
    assert p.PULLEY_GROOVE_BOTTOM_R < g.belt_tooth_tip_radius()    # teeth don't bottom out


def _check_radial_envelope():
    assert g.tab_tip_radius() >= p.DRUM_DIA / 2 + p.DRUM_TAB_CLEAR
    assert g.belt_tooth_tip_radius() >= p.PULLEY_SKIRT_R + p.BELT_TOOTH_CLEAR
    assert g.guide_groove_bottom_radius() > p.DRUM_DIA / 2
    assert p.SHAFT_HEIGHT_ABOVE_PLATE - g.cleat_tip_radius() > 5.0
    assert abs(g.guide_rim_radius() - 19.447) < 1e-3
    assert abs(g.guide_groove_bottom_radius() - 14.447) < 1e-3
    assert abs(g.tab_tip_radius() - 16.347) < 1e-3
    assert abs(g.cleat_tip_radius() - 34.947) < 1e-3


def _check_shaft_set():
    ss = shaft_set()
    assert ss.is_valid
    assert all(abs(a - b) < 0.05 for a, b in zip(bbox_size(ss), (38.894, 38.894, 59.0)))
    assert 38.0 <= volume_cm3(ss) <= 52.0
    bore_radius = (p.PULLEY_BORE + p.PULLEY_BORE_CLEARANCE) / 2
    assert p.PULLEY_INSERT_DEPTH <= p.DRUM_DIA / 2 - bore_radius - p.PULLEY_INSERT_MIN_WALL

    assert contains(ss, (0, 14.0, 0))          # wheel, below the groove
    assert not contains(ss, (0, 17.0, 0))      # inside the guide groove
    assert contains(ss, (0, 19.0, 7.0))        # wheel rim land beside the groove
    assert not contains(ss, (0, 14.0, 17.5))   # tab running zone, outside drum
    assert contains(ss, (0, 18.5, 27.0))       # pulley land, on +y by phase
    assert not contains(ss, (1.3966, 17.7451, 27.0))   # pulley groove, r 17.8 at 4.5 deg
    assert contains(ss, (1.3573, 17.2467, 27.0))       # below groove bottom, r 17.3
    assert not contains(ss, (0, 3.9, 0))       # bore
    assert contains(ss, (0, 18.5, -27.0))      # the other pulley, in phase
    assert not contains(ss, (1.3966, 17.7451, -27.0))
    assert not contains(ss, (10.0, 0, p.GRUB_Z)) and not contains(ss, (10.0, 0, -p.GRUB_Z))   # insert pockets, +x
    assert not contains(ss, (5.5, 0, p.GRUB_Z))                                                # through to the bore
    assert contains(ss, (-10.0, 0, p.GRUB_Z))


def _check_shaft_and_coupons():
    s = shaft()
    assert s.is_valid
    assert all(abs(a - b) < 0.02 for a, b in zip(bbox_size(s), (8.0, 8.0, 145.0)))
    assert not contains(s, (3.8, 0, 0)) and contains(s, (-3.8, 0, 0))   # the flat faces +x
    assert contains(s, (3.8, 0, 30.0))                                   # and ends at +/-22.5
    assert not clash(s, shaft_set())
    ring = ring_coupon()
    assert ring.is_valid
    assert all(abs(a - b) < 0.02 for a, b in zip(bbox_size(ring), (p.PULLEY_OD, p.PULLEY_OD, 3.0)))
    assert contains(ring, (0, 18.5, 0)) and not contains(ring, (1.3966, 17.7451, 0))
    guide = guide_coupon()
    assert guide.is_valid
    assert all(abs(a - b) < 0.05 for a, b in zip(bbox_size(guide), (38.894, 38.894, 16.0)))
    assert not contains(guide, (0, 17.0, 0)) and contains(guide, (0, 19.0, 7.0))


def _check_belt_mesh():
    """The groove is the standard and is not in question; this checks that
    the belt model is a fair representation of a belt sitting in it."""
    on_pulley = Location((0, 0, p.BELT_SPACING / 2))
    w = belt_wrapped(8).moved(on_pulley)
    assert not clash(w, shaft_set())
    assert g.belt_tooth_tip_radius() - p.PULLEY_GROOVE_BOTTOM_R < 0.1   # not shrunken to pass
    half_pitch = Location((0, 0, 0), (0, 0, math.degrees(p.BELT_PITCH / p.PULLEY_PD)))
    assert clash(belt_wrapped(8).moved(on_pulley * half_pitch), shaft_set())   # teeth on lands must collide
    seg = belt_segment(8)
    assert seg.is_valid
    assert all(abs(a - b) < 0.02 for a, b in zip(bbox_size(seg), (24.0, 2.4, 15.0)))
    band = belt_band()
    assert band.is_valid
    assert abs(bbox_size(band)[0] - (p.CENTRE_DIST + 2 * g.belt_back_radius())) < 0.02


def _check_lug_in_groove():
    c = p.CENTRE_DIST
    mid_head_arc = c + math.pi * p.PULLEY_PD / 4
    s = slat(False).moved(g.loop_at(mid_head_arc))
    assert not clash(s, shaft_set().moved(g.at(c, 0)))
    # Negative control. A zero-clearance groove only touches the straight lug
    # along lines, sharing no volume, so the control groove is tighter than
    # the lug by the nominal clearances -- see README.md "Lug-in-groove control".
    tight = shaft_set_with(groove_flank_clear=-p.GROOVE_FLANK_CLEAR, groove_tip_clear=-p.GROOVE_TIP_CLEAR)
    assert clash(s, tight.moved(g.at(c, 0)))
    # And the guide guides: the slat is free inside its lateral play and
    # stopped by a flank just beyond it.
    play = p.GROOVE_FLANK_CLEAR / math.cos(math.radians(p.LUG_ANGLE / 2))
    assert abs(play - 0.707) < 1e-3
    for sign in (1, -1):
        assert not clash(s.moved(Location((0, 0, sign * 0.9 * play))), shaft_set().moved(g.at(c, 0)))
        assert clash(s.moved(Location((0, 0, sign * 1.1 * play))), shaft_set().moved(g.at(c, 0)))


def _check_whole_loop_clearances():
    """The expensive one. Real slat geometry, every slat, against every
    drivetrain part and plate, across the take-up range."""
    for takeup in (p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX):
        fixed = list(drivetrain_group(takeup=takeup).children) + list(plates_group(takeup=takeup).children)
        for s in slats_group(detail=True, takeup=takeup).children:
            for part in fixed:
                assert not clash(s, part), f"{s.label} hits {part.label} at takeup {takeup}"


def _check_slat_gap():
    """Slats sit outside the pitch line, so they fan apart round a pulley:
    the gap between neighbours is never less than on the straight runs."""
    nominal = p.SLAT_PITCH - p.SLAT_WIDTH
    assert abs(nominal - 1.0) < 1e-9
    for phase in (0.0, p.SLAT_PITCH / 2):
        slats = [
            slat(g.is_cleated(i)).moved(g.loop_at(i * p.SLAT_PITCH + phase))
            for i in range(p.SLAT_COUNT)
        ]
        for a, b in zip(slats, slats[1:] + slats[:1]):
            assert a.distance_to(b) > nominal - 1e-6


def _check_loop_geometry():
    c = p.CENTRE_DIST
    back = g.belt_back_radius()
    assert (g.loop_at(0).position - g.at(0, back).position).length < 1e-9
    assert (g.loop_at(c / 2).position - g.at(c / 2, back).position).length < 1e-9
    assert (g.loop_at(p.BELT_LOOP_LENGTH - 1e-9).position - g.loop_at(0).position).length < 1e-6
    assert abs(2 * c + math.pi * p.PULLEY_PD - p.BELT_LOOP_LENGTH) < 1e-9
    assert abs(math.pi * p.PULLEY_PD / 2 - 60.0) < 1e-9          # each arc is 20 teeth of pitch line
    for s in (c, c + 60.0, 2 * c + 60.0):                          # continuous through every station
        assert (g.loop_at(s - 1e-9).position - g.loop_at(s + 1e-9).position).length < 1e-6
    mid_return = g.loop_at(c + 60.0 + c / 2)
    assert (mid_return.position - g.at(c / 2, -back).position).length < 1e-9
    assert (mid_return.x_axis.direction + g.run_direction()).length < 1e-9   # travelling tailward
    assert (mid_return.y_axis.direction + g.run_normal()).length < 1e-9      # belt back faces the plates
    assert g.tail_shaft_t() == 0.0 and g.tail_shaft_t(p.TAIL_TAKEUP_MAX) == -p.TAIL_TAKEUP_MAX
    for bad in (p.TAIL_TAKEUP_MIN - 0.1, p.TAIL_TAKEUP_MAX + 0.1):
        try:
            g.tail_shaft_t(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("tail_shaft_t must reject a takeup outside its range")


# Checks known to fail for a recorded reason. A check listed here counts as
# XFAIL when it fails and as a failure of the run when it unexpectedly
# passes -- at which point remove it from this table. Empty since rev D
# closed the CENTRE_DIST question.
_EXPECTED_FAILURES: dict[str, str] = {}

_CHECKS = [
    ("parameter consistency", _check_parameter_consistency),
    ("returning run clearance", _check_returning_run_clearance),
    ("saddle clearances", _check_saddle_clearances),
    ("geometry module", _check_geometry_module),
    ("slat bounding box", _check_slat_bounding_box),
    ("volume", _check_volume),
    ("probe points", _check_probe_points),
    ("clearance", _check_clearance),
    ("manifold", _check_manifold),
    ("frame geometry", _check_frame_geometry),
    ("frame", _check_frame),
    ("plates sit on rails", _check_plates_sit_on_rails),
    ("plates span rails", _check_plates_span_rails),
    ("plates don't collide with each other", _check_plates_dont_collide),
    ("assembly framework", _check_assembly_framework),
    ("belt tooth", _check_belt_tooth),
    ("pulley groove vs manufacturer", _check_pulley_groove),
    ("belt radius correction", _check_belt_radius_correction),
    ("radial envelope", _check_radial_envelope),
    ("shaft set", _check_shaft_set),
    ("shaft and coupons", _check_shaft_and_coupons),
    ("mesh: belt in pulley", _check_belt_mesh),
    ("guide: lug in groove", _check_lug_in_groove),
    ("whole-loop clearances", _check_whole_loop_clearances),
    ("slat gap round the loop", _check_slat_gap),
    ("loop geometry", _check_loop_geometry),
]


def run_checks() -> bool:
    all_passed = True
    for label, fn in _CHECKS:
        expected_failure = _EXPECTED_FAILURES.get(label)
        try:
            fn()
        except AssertionError as exc:
            if expected_failure:
                print(f"XFAIL {label}: {expected_failure}")
            else:
                print(f"FAIL  {label}: {exc}")
                all_passed = False
        else:
            if expected_failure:
                print(f"XPASS {label}: now passes -- remove it from _EXPECTED_FAILURES")
                all_passed = False
            else:
                print(f"PASS  {label}")
    return all_passed


if __name__ == "__main__":
    sys.exit(0 if run_checks() else 1)
