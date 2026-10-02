"""Human-facing pre-export gate: runs every acceptance assertion from the
CAD spec and prints a pass/fail line per check. The same assertions are
expressed as pytest tests under tests/; this is the manual runner."""

import math
import sys

from functools import cache
from itertools import combinations

from build123d import Align, Box, Cylinder, GeomType, Location, Pos, Rot

import geometry as g
import params as p
from export import printed_parts
from assembly import (
    COLOURS, GROUPS, assembly, bearings_group, belts_group, drive_group, drivetrain_group, frame_group,
    pillow_blocks_group, plates_group, slats_group, spacers_group, tilt_base_parts, tilt_frame_parts, tilt_group,
    tilt_prop_parts,
    hopper_cavity_placed, hopper_group, hopper_parts,
)
from parts.bearing import bearing
from parts.belt import belt_band, belt_segment, belt_wrapped
from parts.bridge_plate import bridge_plate
from parts.coupler import coupler
from parts.coupons import bearing_coupon, bearing_coupon_pocket_x, guide_coupon, ring_coupon
from parts.frame import frame
from parts.motor import motor
from parts.motor_bracket import motor_bracket, motor_hole_centres, slot_z
from parts.pillow_block import pillow_block
from parts.prop import frame_clevis
from parts.shaft import shaft
from parts.shaft_set import shaft_set, shaft_set_with
from parts.slat import pulley_envelope, slat
from parts.spacer import spacer
from profile import groove_half, groove_junctions, pulley_section, tooth_face, tooth_half
from utils import _box_gap, _overlap_volume, bbox_size, clash, contains, distance_within, level_fill, mass_properties, min_distance, volume_cm3


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
        assembly("skirts")
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


_TAKEUPS = (p.TAIL_TAKEUP_MIN, 0.0, p.TAIL_TAKEUP_MAX)


def _check_whole_loop_clearances():
    """The expensive one. Real slat geometry, every slat, against every
    drivetrain part, plate, tilt part, pillow block and spacer, the
    drive on either side, and every hopper part but the bristles, across
    the take-up range and the tilt range (spec-tilt §8.1, which is also
    its T6; spec-pillow-blocks §4; spec-drive §8.12, §8.15; hopper-spec C1)."""
    for incline in p.TILT_CHECK_ANGLES:
        for takeup in _TAKEUPS:
            fixed = [
                part
                for group in (drivetrain_group, plates_group, tilt_group, pillow_blocks_group, spacers_group)
                for part in group(takeup=takeup, incline=incline).children
            ] + _drive_parts(takeup, incline) + hopper_fixed(incline)
            for s in slats_group(detail=True, takeup=takeup, incline=incline).children:
                for part in fixed:
                    assert not clash(s, part), f"{s.label} hits {part.label} at takeup {takeup}, incline {incline}"


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


# --- Tilt: hinge, cross-member, clevis, prop -- spec-tilt §8.2 -----------------
# T1 is the rest of this file passing; T6's sweep is the whole-loop check.


def _by_label(parts) -> dict:
    return {part.label: part for part in parts}


def _check_tilt_geometry():
    assert (g.run_direction(p.TILT_MIN) - g.at(0, incline=p.TILT_MIN).x_axis.direction).length < 1e-9
    assert (g.at(0, incline=p.TILT_MAX).position).length < 1e-9           # the machine origin does not move
    assert (g.loop_at(0, incline=p.INCLINE).position - g.loop_at(0).position).length < 1e-12   # 40 deg is today's machine
    for incline in p.TILT_CHECK_ANGLES:
        base = g.base_frame(incline)
        assert abs(g.height_above_base(g.hinge_axis(incline), incline) - p.HINGE_HEIGHT) < 1e-9
        assert abs(base.position.X - g.hinge_axis(incline).X) < 1e-9
        assert abs(base.x_axis.direction.X - 1.0) < 1e-9 and abs(base.y_axis.direction.Y - 1.0) < 1e-9
        assert abs(g.height_above_base(g.prop_pin_b(incline), incline) - p.PROP_PIN_B_Y) < 1e-9


def _check_frame_clears_base():
    """T2, with its control: a base 10 higher is penetrated by the rails'
    tail corner, which rides about 6 above the real one."""
    for incline in p.TILT_CHECK_ANGLES:
        base = _by_label(tilt_base_parts(incline))["base_ref"]
        for takeup in _TAKEUPS:
            moving = tilt_frame_parts(incline)
            for group in (frame_group, plates_group, drivetrain_group, belts_group, slats_group,
                          pillow_blocks_group, bearings_group, spacers_group):
                moving += list(group(takeup=takeup, incline=incline).children)
            moving += _drive_parts(takeup, incline)
            for part in moving:
                gap = part.distance_to(base)
                assert gap >= p.BASE_CLEARANCE_MIN, f"{part.label} is {gap:.2f} from the base at incline {incline}, takeup {takeup}"
        assert clash(frame(incline), base.moved(Location((0, 10.0, 0))), tol=1.0)


def _check_tail_shaft_height():
    lo, hi = p.TAIL_SHAFT_HEIGHT_RANGE
    for incline in p.TILT_CHECK_ANGLES:
        for takeup in _TAKEUPS:
            axis = g.at(g.tail_shaft_t(takeup), 0, incline=incline).position
            assert lo <= g.height_above_base(axis, incline) <= hi


def _check_hinge_parts():
    for incline in p.TILT_CHECK_ANGLES:
        on_frame, on_base, f = _by_label(tilt_frame_parts(incline)), _by_label(tilt_base_parts(incline)), frame(incline)
        for side in ("+z", "-z"):
            bracket, block = on_frame[f"hinge bracket {side}"], on_base[f"hinge block {side}"]
            assert not clash(bracket, block) and not clash(bracket, f) and not clash(block, f)
            assert bracket.distance_to(block) >= 0.8
            assert bracket.distance_to(f) < 0.01                  # bolted to the rail face, not floating
    assert abs(p.HINGE_HEIGHT - p.HINGE_BOSS_R - 8.0) < 1e-9      # the boss's lowest point, at every angle
    assert abs(p.HINGE_BOSS_R - p.FRAME_PROFILE / 2 - 2.0) < 1e-9   # and it stands 2.0 proud of the rail


def _check_cross_member():
    assert g.xmember_plate_clearance() >= p.XMEMBER_PLATE_CLEAR
    assert g.xmember_plate_clearance(190.0) <= 0               # control: over the plate at 177
    assert -g.cleat_tip_radius() - g.rail_top_offset() >= p.XMEMBER_RETURN_CLEAR
    xm, f = _by_label(tilt_frame_parts())["cross-member"], frame()
    assert not clash(xm, f, tol=1.0) and xm.distance_to(f) < 0.01     # square between the rails' inner faces
    for plate in plates_group().children:
        assert not clash(xm, plate)


def _prop_underside_gap(incline: float, pin_b_x: float = p.PROP_PIN_B_X) -> float:
    """Least distance from the prop body to the rail underside plane, not
    counting the part of it inside the clevis."""
    to_clevis = g.at(p.XMEMBER_T, p.RAIL_UNDERSIDE_OFFSET, incline=incline).inverse()
    body = _by_label(tilt_prop_parts(incline, pin_b_x))["prop body"].moved(to_clevis)
    bounds = frame_clevis().bounding_box()
    far = 4 * p.PROP_BODY_LEN
    inside = Pos(bounds.min.X, 0, 0) * Box(bounds.size.X, far, far, align=(Align.MIN, Align.CENTER, Align.CENTER))
    return -(body - inside).bounding_box().max.Y


def _prop_hits(incline: float, pin_b_x: float = p.PROP_PIN_B_X) -> list[str]:
    on_frame, on_base = _by_label(tilt_frame_parts(incline)), _by_label(tilt_base_parts(incline))
    fixed = list(frame(incline).children) + list(plates_group(incline=incline).children)
    fixed += [on_frame["cross-member"], on_base["base_ref"]]
    return [
        f"{part.label} / {other.label}"
        for part in tilt_prop_parts(incline, pin_b_x) for other in fixed if clash(part, other)
    ]


def _check_prop_clears_frame():
    """T7. Control: with pin B at 300 the prop is shorter than its own rod,
    which comes up through pin A into the cross-member."""
    for incline in p.TILT_CHECK_ANGLES:
        assert _prop_hits(incline) == []
        assert _prop_underside_gap(incline) >= p.PROP_UNDERSIDE_CLEAR
    assert _prop_hits(p.TILT_MIN, pin_b_x=300.0) == ["prop rod / cross-member"]


def _check_prop_swing():
    """T8. The eyes run CLEVIS_SIDE_CLEAR from the cheeks; anything nearer
    is the body or foot swinging into a flange, a cheek or the head wall."""
    for incline in (p.TILT_MIN, p.TILT_MAX):
        on_frame, on_base, prop = (_by_label(f(incline)) for f in (tilt_frame_parts, tilt_base_parts, tilt_prop_parts))
        for part, holder in ((prop["prop body"], on_frame["frame clevis"]), (prop["prop foot"], on_base["base pin block"])):
            assert not clash(part, holder)
            assert part.distance_to(holder) >= p.CLEVIS_SIDE_CLEAR - 1e-3


def _check_prop_length_table():
    for incline, length, lean in zip(p.TILT_CHECK_ANGLES, (152.6, 182.6, 217.9), (48.4, 26.1, 8.4)):   # pin B at 140, README
        assert abs(g.prop_length(incline) - length) < 0.5
        assert abs(g.prop_length(incline) - p.prop_length_at(incline)) < 1e-9
        assert abs(g.prop_lean(incline) - lean) < 1.0
        assert abs(g.incline_for_length(g.prop_length(incline)) - incline) < 0.05
    assert all(g.prop_length(a) < g.prop_length(b) for a, b in zip(_TILT_GRID, _TILT_GRID[1:]))
    assert abs(g.prop_length(p.TILT_MAX) - g.prop_length(p.TILT_MIN) - 65.2) < 0.1
    assert abs(g.prop_turns(p.TILT_MAX) - 52.2) < 0.5


def _check_length_budget():
    assert all(margin >= 0 for margin in p.prop_budget())
    assert abs(p.prop_budget()[2] - 3.0) < 0.1
    engaged, clear_of_pin_a, stack = p.prop_budget(rod_len=160.0)   # control
    assert clear_of_pin_a < -1.0 and engaged >= 0 and stack >= 0
    assert abs(p.FOOT_STACK - 29.6) < 1e-9


_TILT_GRID = [p.TILT_MIN + 0.5 * i for i in range(int((p.TILT_MAX - p.TILT_MIN) / 0.5) + 1)]


def _check_prop_force():
    """With the drive's weight added at the head shaft (spec-drive §7); the
    frame alone gave spec-tilt's 98 / 58 / 37."""
    for incline in _TILT_GRID:
        assert 0 < g.prop_force(incline) < p.PROP_FORCE_MAX
    for incline, force in zip(p.TILT_CHECK_ANGLES, (94.7, 57.9, 37.0)):
        assert abs(g.prop_force(incline) - force) < 1.0


def _check_prop_force_doubled():
    """The guard on the weight estimate, frame and drive together
    (spec-drive §8.14): PROP_FORCE_MAX was set so this passes. See README.md
    "Prop force at doubled weight"."""
    worst = max(g.prop_force(incline, g.doubled(g.machine_loads())) for incline in _TILT_GRID)
    assert worst <= p.PROP_FORCE_MAX, f"{worst:.0f} N"
    assert abs(worst - 189.3) < 0.5, f"{worst:.1f} N"


def _check_tilt_parts():
    for part in tilt_group().children:
        assert part.is_valid and len(part.solids()) == 1, part.label
    for incline in p.TILT_CHECK_ANGLES:
        on_frame, prop = _by_label(tilt_frame_parts(incline)), _by_label(tilt_prop_parts(incline))
        assert prop["prop body"].distance_to(prop["lock nut"]) < 0.01       # locked up against the body
        assert on_frame["frame clevis"].distance_to(on_frame["cross-member"]) < 0.01


# --- Pillow blocks, bearings, spacers -- spec-pillow-blocks §5 ----------------


def _check_pillow_block():
    """§5.1, 1-8."""
    b = pillow_block()
    assert b.is_valid and len(b.solids()) == 1
    assert all(abs(a - e) < 0.01 for a, e in zip(bbox_size(b), (44.0, 63.0, 21.0)))
    assert 16.15 <= volume_cm3(b) <= 17.15                         # 16.65 built, +/-3 %; spec range 15..18
    h = p.SHAFT_HEIGHT_ABOVE_PLATE
    assert not contains(b, (0, h, 0))                               # pocket centre
    rib = 11.05
    assert contains(b, (0, h + rib, 0))                             # on the +y rib
    between = math.radians(360 / p.PB_RIB_COUNT / 2)
    assert not contains(b, (rib * math.sin(between), h + rib * math.cos(between), 0))   # between ribs
    assert contains(b, (0, h + 10.3, 4.25)) and not contains(b, (0, h + 7.0, 4.25))      # lip ledge, lip hole
    assert not contains(b, (0, h, -3.4))                            # open on the inboard face
    assert not contains(b, (p.PB_BOLT_X, 3.0, p.PB_BOLT_Z)) and contains(b, (p.PB_BOLT_X, 6.8, p.PB_BOLT_Z))


def _bearing_clash(rib_tip_dia: float) -> float:
    return _overlap_volume(pillow_block(rib_tip_dia), Pos(0, p.SHAFT_HEIGHT_ABOVE_PLATE, 0) * bearing())


def _check_bearing_press_fit():
    """§5.2, 9-11: the ribs and nothing else grip the bearing."""
    assert 3.24 <= _bearing_clash(p.PB_RIB_TIP_DIA) <= 3.44         # 3.34 built; spec range 1..10
    clear = pillow_block(22.2)
    seated = Pos(0, p.SHAFT_HEIGHT_ABOVE_PLATE, 0) * bearing()
    assert _overlap_volume(clear, seated) == 0.0
    assert clear.distance_to(seated) <= 0.01                        # on the lip
    volumes = [_bearing_clash(d) for d in (21.6, 21.8, 22.0)]
    assert volumes[0] > volumes[1] > volumes[2]


def _check_spacer_and_bearing():
    """§5.3, 12-13."""
    s = spacer()
    assert s.is_valid and all(abs(a - e) < 0.01 for a, e in zip(bbox_size(s), (11.0, 11.0, 16.8)))
    assert 0.64 <= volume_cm3(s) <= 0.70
    b = bearing()
    assert b.is_valid and all(abs(a - e) < 0.01 for a, e in zip(bbox_size(b), (22.0, 22.0, 7.0)))
    assert 2.25 <= volume_cm3(b) <= 2.32


def _check_bearing_coupon():
    """§3.4: each pocket is the block's pocket at its own rib-tip diameter."""
    c = bearing_coupon()
    assert c.is_valid and len(c.solids()) == 1
    assert all(abs(a - e) < 0.01 for a, e in zip(bbox_size(c), (p.BC_LENGTH, p.BC_WIDTH, p.BC_THICKNESS)))
    assert abs(c.bounding_box().min.Z) < 1e-6
    y = -p.BC_WIDTH / 2 + p.BC_POCKET_EDGE
    for i, dia in enumerate(p.BC_RIB_TIP_DIAS):
        seated = Pos(bearing_coupon_pocket_x(i), y, p.BEARING_WIDTH / 2 + p.PB_LIP_THICKNESS) * bearing()
        assert abs(_overlap_volume(c, seated) - _bearing_clash(dia)) < 1e-3


def _sweep_min(parts_of, limit: float, shifts=(0.0,)) -> float:
    """Least distance from any real slat, shifted across the machine by
    each of `shifts`, to any member of `parts_of(takeup)`, over the three
    take-ups; distances from `limit` up are only known to be >= limit.
    The parts move by -shift instead of the slats by +shift: the same
    relative motion, and moving a real slat copies it."""
    least = math.inf
    for takeup in _TAKEUPS:
        slats = slats_group(detail=True, takeup=takeup).children
        for shift in shifts:
            parts = [part.moved(Location((0, 0, -shift))) for part in parts_of(takeup=takeup).children]
            least = min(least, *(min_distance(s, parts, limit) for s in slats))
    return least


def _check_slats_clear_pillow_blocks():
    """§5.4, 14-16. The slats slide across the machine by their lug play,
    which is what brings the slat ends toward the towers (5.79)."""
    play = g.slat_lateral_play()
    blocks = _sweep_min(pillow_blocks_group, 10.0, shifts=(play, -play))
    assert blocks >= p.PB_SLAT_CLEAR_MIN and abs(blocks - 5.79) < 0.01, f"{blocks:.3f}"
    assert p.SHAFT_HEIGHT_ABOVE_PLATE - g.cleat_tip_radius() - p.PB_FOOT_HEIGHT > p.PB_SLAT_CLEAR_MIN   # 6.05
    spacers = _sweep_min(spacers_group, 15.0)
    assert spacers >= p.PB_SLAT_CLEAR_MIN and abs(spacers - (g.tab_tip_radius() - p.SPACER_OD / 2)) < 0.01, f"{spacers:.3f}"


def _check_bearing_parts_clear_drivetrain():
    """§5.4, 17-18. The spacer faces the shaft set's end across half the
    end play, so that pair is held to 18's gap instead of 17's 1.0."""
    for takeup in _TAKEUPS:
        others = list(belts_group(takeup=takeup).children)
        others += [c for c in drivetrain_group(takeup=takeup).children if c.label.endswith("shaft set")]
        for group in (pillow_blocks_group, bearings_group, spacers_group):
            for part in group(takeup=takeup).children:
                for other in others:
                    assert not clash(part, other), f"{part.label} / {other.label}"
                    gap = distance_within(part, other, 1.0)
                    if part.label.split()[1] == "spacer" and other.label == f"{part.label.split()[0]} shaft set":
                        assert abs(gap - p.SHAFT_END_PLAY / 2) < 0.01, f"{part.label} {gap:.3f}"
                    else:
                        assert gap >= 1.0, f"{part.label} / {other.label} {gap:.3f}"


def _check_blocks_on_plates():
    """§5.4, 19-22."""
    for takeup in _TAKEUPS:
        plates = plates_group(takeup=takeup).children
        shafts = {c.label: c for c in drivetrain_group(takeup=takeup).children}
        for block in pillow_blocks_group(takeup=takeup).children:
            end, _, side = block.label.split()
            plate = plates[0] if end == "tail" else plates[-1]
            assert not clash(block, plate) and block.distance_to(plate) < 1e-6              # 19
            local = block.moved(plate.location.inverse()).bounding_box()
            assert abs(local.min.Y) < 1e-6
            assert -p.PLATE_WIDTH / 2 <= local.min.X and local.max.X <= p.PLATE_WIDTH / 2
            assert -p.PLATE_LENGTH / 2 <= local.min.Z and local.max.Z <= p.PLATE_LENGTH / 2
            for x in (-p.PB_BOLT_X, p.PB_BOLT_X):                                           # 20
                hole = (block.location * Location((x, -p.PLATE_THICKNESS / 2, p.PB_BOLT_Z))).position
                assert not contains(plate, (hole.X, hole.Y, hole.Z))
            sign = 1 if side == "+z" else -1                                                # 21
            axis = (block.location * Location((0, p.SHAFT_HEIGHT_ABOVE_PLATE, 0))).position
            on_shaft = shafts[f"{end} shaft"].location.position
            assert math.hypot(axis.X - on_shaft.X, axis.Y - on_shaft.Y) < 0.01
            assert abs(axis.Z - sign * p.BEARING_Z) < 0.01
            box = block.bounding_box()                                                      # 22
            assert abs((box.max.Z if sign > 0 else -box.min.Z) - 55.0) < 0.01
            tower = g.at(g.tail_shaft_t(takeup) if end == "tail" else p.CENTRE_DIST, 13.0).position
            for dz, inside in ((0.05, True), (-0.05, False)):
                probe = (tower.X, tower.Y, sign * (46.5 + dz))
                assert contains(block, probe) == inside


def _check_end_plate_holes():
    bearing_plate, support_plate = bridge_plate("bearing"), bridge_plate("support")
    z = p.BEARING_Z + p.PB_BOLT_Z
    assert abs(z - 40.25) < 1e-9
    for x in (-p.PB_BOLT_X, p.PB_BOLT_X):
        for sz in (-z, z):
            assert not contains(bearing_plate, (x, -p.PLATE_THICKNESS / 2, sz))
            assert contains(support_plate, (x, -p.PLATE_THICKNESS / 2, sz))


# --- Drive: motor, coupler, motor bracket -- spec-drive §8 ---------------------


_DRIVE_SIDES = (1, -1)


def _drive_parts(takeup: float = 0.0, incline: float = p.INCLINE) -> list:
    """The drive on both sides, and the head shaft turned for -1: every part
    that DRIVE_SIDE moves, labelled with its side (§8.15)."""
    parts = []
    for side in _DRIVE_SIDES:
        tag = "+z" if side > 0 else "-z"
        for part in drive_group(takeup=takeup, incline=incline, drive_side=side).children:
            parts.append(part.moved(Location()))
            parts[-1].label = f"{part.label} {tag}"
    head = _by_label(drivetrain_group(takeup=takeup, incline=incline, drive_side=-1).children)["head shaft"]
    head.label = "head shaft -z"
    return parts + [head]


def _check_drive_parameters():
    """§8, 1-6, and the §2 sizing."""
    assert p.HEAD_SHAFT_DRIVE_EXT >= p.PILLOW_BLOCK_HALF_W + p.COUPLER_BLOCK_GAP + p.COUPLER_ENGAGE        # 1
    assert p.COUPLER_ENGAGE <= p.HEAD_SHAFT_ENGAGE <= p.COUPLER_ENGAGE_MAX                                 # 2
    motor_engage = p.COUPLER_Z + p.COUPLER_LEN - (p.MOTOR_FACE_Z - p.MOTOR_SHAFT_LEN)
    assert p.COUPLER_ENGAGE <= motor_engage <= p.COUPLER_ENGAGE_MAX
    assert p.COUPLER_TIP_GAP >= p.COUPLER_TIP_GAP_MIN                                                      # 3
    assert p.MOTOR_SCREW_LEN - p.FACE_PLATE_T <= p.MOTOR_SCREW_MAX_ENGAGE                                  # 4
    assert p.DRIVE_TORQUE_AVAIL / p.DRIVE_TORQUE_EST >= p.DRIVE_TORQUE_MARGIN_MIN                          # 5
    assert abs(p.DRIVE_TORQUE_AVAIL / p.DRIVE_TORQUE_EST - 1.66) < 0.01
    bottom = p.SHAFT_HEIGHT_ABOVE_PLATE - p.MOTOR_SQUARE / 2                                                # 6
    assert bottom >= p.BRACKET_FOOT_T + p.M5_HEAD_H + p.MOTOR_HEAD_CLEAR
    assert abs(p.DRIVE_TORQUE_EST - 0.153) < 1e-3 and abs(p.DRIVE_SKIP_PULL_N - 13.3) < 0.05
    assert p.DRIVE_STEP_RATE == 1600.0
    assert p.COUPLER_RATED_TORQUE > p.MOTOR_HOLD_TORQUE
    # the stack, with the printed block (README "Drive resolutions")
    assert (p.HEAD_SHAFT_LEN, p.HEAD_SHAFT_DRIVE_EXT, p.COUPLER_Z, p.MOTOR_FACE_Z) == (140.0, 17.5, 57.0, 95.5)
    assert abs(p.HEAD_SHAFT_ENGAGE - 10.5) < 1e-9 and abs(p.COUPLER_TIP_GAP - 4.5) < 1e-9
    assert p.MOTOR_FACE_Z + p.MOTOR_BODY_LEN <= p.FRAME_WIDTH / 2                  # motor back inside the frame's face


def _placed_in_bracket(part):
    """A motor on the bracket's face plate, in the bracket's local frame."""
    return part.moved(Location((0, p.SHAFT_HEIGHT_ABOVE_PLATE, p.FACE_PLATE_T), (0, 180, 0)))


def _check_motor_bracket():
    """§8, 7-10."""
    b = motor_bracket()
    assert b.is_valid and len(b.solids()) == 1                                                             # 7
    assert all(abs(a - e) < 0.5 for a, e in zip(bbox_size(b), (45.0, 72.0, 66.0))), bbox_size(b)   # 57 in the spec, README
    assert 25.0 <= volume_cm3(b) <= 45.0
    assert abs(volume_cm3(b) - 30.47) < 0.03 * 30.47                                                       # pinned, first build
    h = p.SHAFT_HEIGHT_ABOVE_PLATE
    mid = p.FACE_PLATE_T / 2
    assert not contains(b, (0, h, mid))                                                                    # 8
    assert all(not contains(b, (x, y, mid)) for x, y in motor_hole_centres())
    assert all(not contains(b, (x, p.BRACKET_FOOT_T / 2, slot_z())) for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X))
    assert contains(b, (0, 30, 2.5))                                                                        # 9
    seated = _placed_in_bracket(motor())
    assert not clash(b, seated) and b.distance_to(seated) < 1e-6          # on the face plate, boss free in the bore
    tight = motor_bracket(pilot_bore=21.9)                                                                  # 10
    assert _overlap_volume(tight, seated) > 1.0


def _check_drive_parts():
    """The reference solids, and the shafts sitting in the coupler's bores."""
    m, c = motor(), coupler()
    assert m.is_valid and all(abs(a - e) < 0.01 for a, e in zip(bbox_size(m), (42.3, 42.3, 63.5)))
    assert c.is_valid and all(abs(a - e) < 0.01 for a, e in zip(bbox_size(c), (20.0, 20.0, 25.0)))
    head = shaft(p.HEAD_SHAFT_DRIVE_EXT)
    assert head.is_valid and all(abs(a - e) < 0.01 for a, e in zip(bbox_size(head), (8.0, 8.0, 140.0)))
    assert abs(head.bounding_box().min.Z + p.SHAFT_LENGTH / 2) < 1e-6        # non-drive end unchanged
    assert not contains(head, (3.8, 0, 0)) and contains(head, (3.8, 0, 30.0))  # flat still centred on z = 0
    for side in _DRIVE_SIDES:
        drive = _by_label(drive_group(drive_side=side).children)
        train = _by_label(drivetrain_group(drive_side=side).children)
        shaft_end = train["head shaft"].bounding_box().max.Z if side > 0 else -train["head shaft"].bounding_box().min.Z
        assert abs(shaft_end - (p.BEARING_Z + p.HEAD_SHAFT_DRIVE_EXT)) < 1e-6
        assert not clash(drive["coupler"], train["head shaft"]) and not clash(drive["coupler"], drive["motor"])
        assert drive["coupler"].distance_to(train["head shaft"]) < 1e-6     # the shaft is in the bore
        assert not clash(drive["motor"], drive["motor bracket"])
        assert drive["motor"].distance_to(drive["motor bracket"]) < 1e-6     # seated on the face plate


def _check_coupler_clearances():
    """§8.11, at every check angle, both sides."""
    for incline in p.TILT_CHECK_ANGLES:
        plates = plates_group(incline=incline).children
        blocks = [b for b in pillow_blocks_group(incline=incline).children if b.label.startswith("head")]
        for side in _DRIVE_SIDES:
            drive = _by_label(drive_group(incline=incline, drive_side=side).children)
            swept = drive["coupler"].moved(Location())   # a cylinder already: the bores are inside it
            block = min(swept.distance_to(b) for b in blocks)
            assert block >= p.COUPLER_CLEAR_BLOCK and abs(block - p.COUPLER_BLOCK_GAP) < 1e-6, f"{block:.3f}"
            assert swept.distance_to(drive["motor bracket"]) >= p.COUPLER_CLEAR_BRACKET
            assert min(swept.distance_to(plate) for plate in plates) >= p.COUPLER_CLEAR_BRACKET


def _check_drive_clears_drivetrain():
    """§8.12 for the belts and shaft sets; the slats are in the whole-loop
    sweep. The bracket stands on the head plate and nothing else."""
    for takeup in _TAKEUPS:
        others = list(belts_group(takeup=takeup).children) + [
            c for c in drivetrain_group(takeup=takeup).children if c.label.endswith("shaft set")
        ] + list(pillow_blocks_group(takeup=takeup).children) + list(bearings_group(takeup=takeup).children)
        plates = plates_group(takeup=takeup).children
        for part in _drive_parts(takeup):
            if part.label.startswith("head shaft"):
                continue
            for other in others:
                assert not clash(part, other), f"{part.label} / {other.label}"
            for plate in plates:
                assert not clash(part, plate), f"{part.label} / {plate.label}"
    for side in _DRIVE_SIDES:
        bracket, head_plate = _by_label(drive_group(drive_side=side).children)["motor bracket"], plates_group().children[-1]
        assert bracket.distance_to(head_plate) < 1e-6
        for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X):   # the slots are over the plate's M5 holes
            probe = g.at(p.CENTRE_DIST + x, g.plate_top_offset() + p.BRACKET_FOOT_T / 2, side * p.PLATE_BOLT_Z).position
            assert not contains(bracket, (probe.X, probe.Y, probe.Z))
            hole = g.at(p.CENTRE_DIST + x, g.plate_top_offset() - p.PLATE_THICKNESS / 2, side * p.PLATE_BOLT_Z).position
            assert not contains(head_plate, (hole.X, hole.Y, hole.Z))


def _check_drive_clears_base():
    """§8.13. T2 holds everything to BASE_CLEARANCE_MIN; this also pins how
    far they really are at 25 deg: the motor 223.4 (the spec's "about 225"),
    the bracket's foot, lower down on the plate, 198.4."""
    for incline in p.TILT_CHECK_ANGLES:
        base = _by_label(tilt_base_parts(incline))["base_ref"]
        for part in _drive_parts(incline=incline):
            assert part.distance_to(base) >= p.BASE_CLEARANCE_MIN, part.label
    base = _by_label(tilt_base_parts(p.TILT_MIN))["base_ref"]
    drive = _by_label(drive_group(incline=p.TILT_MIN).children)
    assert abs(drive["motor"].distance_to(base) - 223.4) < 0.1
    assert abs(drive["motor bracket"].distance_to(base) - 198.4) < 0.1


def tilt_report() -> list[str]:
    """The setting-up table (spec-tilt §8.3) and the informational numbers
    of §5.4 and T12. This is how the angle gets set by hand."""
    lines = ["", "Setting up: prop length against incline", "  incline   pin to pin   exposed rod   turns from min"]
    steps = int((p.TILT_MAX - p.TILT_MIN) / p.SETUP_TABLE_STEP)
    for incline in (p.TILT_MIN + p.SETUP_TABLE_STEP * i for i in range(steps + 1)):
        lines.append(
            f"  {incline:7.1f}   {g.prop_length(incline):10.1f}   {g.prop_exposed_rod(incline):11.1f}   {g.prop_turns(incline):14.1f}"
        )
    lines.append("  (exposed rod: bare thread between the knob's jam nut and the lock nut run up to the body)")
    lines += ["", f"Prop force at {p.TILT_TOTAL_WEIGHT_N:.1f} N (frame {p.TILT_WEIGHT_N:g}, an estimate until weighed, "
                  f"+ drive {p.DRIVE_WEIGHT_N:.1f}), and head shaft height above the base"]
    for incline in p.TILT_CHECK_ANGLES:
        head = g.height_above_base(g.shaft_axis("head", incline), incline)
        lines.append(f"  {incline:7.1f}   {g.prop_force(incline):6.0f} N   lean {g.prop_lean(incline):5.1f}   head shaft {head:6.1f}")
    return lines


# --- Hopper -- hopper-spec-v1.md §8 ---------------------------------------------------
# The slats and everything on the frame turn together, so a distance between
# them does not depend on the incline. Those are measured with the run laid
# along x (incline 0), where bounding boxes are tight and the sweeps cheap;
# the no-clash sweep above, and everything against the base, the hinge and
# the prop, runs at all nine cases -- README "Hopper checks".

_RUN = 0.0   # deg, lays the run along machine x; a frame of reference, not a machine setting
_PHASES = tuple(p.SLAT_PITCH * i / 4 for i in range(4))   # belt positions within one slat pitch
_HOPPER_GRID = [
    p.TILT_MIN + p.HOPPER_TABLE_STEP * i for i in range(int((p.TILT_MAX - p.TILT_MIN) / p.HOPPER_TABLE_STEP) + 1)
]
PLYWOOD = ("side panel", "back wall", "front wall")   # the hopper members cut from plywood; the rest print in PETG


def hopper_fixed(incline: float = p.INCLINE, **kwargs) -> list:
    """The hopper parts every slat must clear: all but the bristles, which
    are meant to touch them (C1, C4)."""
    return [part for part in hopper_parts(incline, **kwargs) if "bristles" not in part.label]


def in_hopper(part, incline: float = p.INCLINE):
    """`part`, placed at `incline`, moved into hopper coordinates (t, h, z)."""
    return part.moved(g.at(0, g.hopper_offset(0), 0, incline).inverse())


def _top_band():
    """The top of a slat's body, below the edge chamfers, where it is its
    full SLAT_WIDTH: the same on every slat, cleated or not."""
    return slat(False) & Pos(0, p.SLAT_THICKNESS, 0) * Box(
        2 * p.SLAT_WIDTH, p.EDGE_CHAMFER, 2 * p.SLAT_LENGTH, align=(Align.CENTER, Align.MAX, Align.CENTER)
    )


def slat_top_gaps(takeup: float = 0.0, phase: float = 0.0) -> list[tuple[float, float]]:
    """(t, gap) of neighbouring slats on the carrying side of the loop, from
    the tail arc to the front wall's outer face: t of the middle of the
    pair, and the gap between their top bands (A2). `phase` moves the belt
    on, so a sweep of phases sees every pair at every point of the tail arc."""
    spread = g.loop_length(takeup) / p.BELT_LOOP_LENGTH
    t_max = p.HOPPER_FRONT_T + p.WALL_THICKNESS
    band = _top_band()
    placed = {}
    for i in range(p.SLAT_COUNT):
        loc = g.loop_at(i * p.SLAT_PITCH * spread + phase, takeup, _RUN)
        t, offset, _ = g.run_coords(loc.position, _RUN)
        if offset > 0 and -2 * p.SLAT_PITCH < t < t_max + p.SLAT_PITCH:
            placed[i] = band.moved(loc)
    gaps = []
    for i, a in placed.items():
        b = placed.get((i + 1) % p.SLAT_COUNT)
        if b is not None:
            t = g.run_coords((a.center() + b.center()) / 2, _RUN)[0]
            if t <= t_max:
                gaps.append((t, a.distance_to(b)))
    return gaps


@cache
def hopper_slat_clearance(takeup: float = 0.0, shift: float = 0.0) -> tuple[float, str, str]:
    """(distance, slat, part) of the nearest slat to any hopper part but the
    bristles, with every slat moved `shift` across the machine (C1). With a
    shift, the carry rail is left out: it is the guide, and its groove's
    flank is what stops a slat at slat_lateral_play()."""
    # The parts move the other way rather than the slats: a slat in a group
    # is a child of its Compound, and moved() would copy the whole group.
    parts = [
        part.moved(Location((0, 0, -shift)))
        for part in hopper_fixed(_RUN) if not (shift and part.label == "carry rail")
    ]
    parts = [(part, part.bounding_box(optimal=False)) for part in parts]
    slats = [(s, s.bounding_box(optimal=False)) for s in slats_group(detail=True, takeup=takeup, incline=_RUN).children]
    pairs = sorted(
        ((_box_gap(slat_box, box), s, part) for s, slat_box in slats for part, box in parts),
        key=lambda pair: pair[0],
    )   # nearest boxes first, so the exact distances stop early
    best = (math.inf, "", "")
    for apart, s, part in pairs:
        if apart >= best[0]:
            break
        d = s.distance_to(part)
        if d < best[0]:
            best = (d, s.label, part.label)
    return best


def slats_over_rail(takeup: float = 0.0, incline: float = p.INCLINE) -> list:
    """The carrying-run slats whose lugs lie wholly over the carry rail."""
    over = []
    for s in slats_group(detail=True, takeup=takeup, incline=incline).children:
        t, offset, _ = g.run_coords(s.location.position, incline)
        if offset > 0 and p.RAIL_T0 <= t - p.LUG_LENGTH / 2 and t + p.LUG_LENGTH / 2 <= p.RAIL_T1:
            over.append(s)
    return over


def contact_faces(s) -> list:
    """The planar faces of a placed slat on its belt-contact face."""
    loc = s.location
    down = -loc.y_axis.direction
    return [
        face for face in s.faces()
        if face.geom_type == GeomType.PLANE and face.normal_at().dot(down) > 1 - 1e-9
        and abs((face.center() - loc.position).dot(down)) < 1e-6
    ]


@cache
def hopper_mass() -> tuple[float, float, float]:
    """(kg, t, offset) of the hopper, its rail and bridge: every solid at its
    material's density, the brushes as BRUSH_MASS each, and the loose
    hardware as HOPPER_HARDWARE_MASS at the solids' centre (§7.1, D1)."""
    parts = hopper_parts(_RUN)
    solids = [part for part in parts if "brush" not in part.label]
    densities = [p.PLY_DENSITY if part.label.startswith(PLYWOOD) else p.PETG_DENSITY for part in solids]
    _, centre = mass_properties(solids, densities)
    brushes = [(p.BRUSH_MASS, part.center()) for part in parts if part.label.endswith("brush backing")]
    mass, centre = mass_properties(solids, densities, brushes + [(p.HOPPER_HARDWARE_MASS, centre)])
    t, offset, _ = g.run_coords(centre, _RUN)
    return mass, t, offset


@cache
def hopper_fill(incline: float = p.INCLINE, rim_front_h: float = p.RIM_FRONT_H) -> tuple[float, float, float]:
    """(litres, t, offset) of the level fill at `incline` (§6, B1)."""
    litres, centroid = level_fill(hopper_cavity_placed(incline, rim_front_h))
    t, offset, _ = g.run_coords(centroid, incline)
    return litres, t, offset


def prop_loads(incline: float = p.INCLINE, full: bool = True) -> list[tuple[float, float, float]]:
    """The frame, the drive, the hopper and, if `full`, its level fill of LEGO at
    LOAD_BULK_DENSITY, as prop_force() loads (§7.3)."""
    loads = g.machine_loads() + [hopper_mass()]
    if full:
        litres, t, offset = hopper_fill(incline)
        loads.append((litres * p.LOAD_BULK_DENSITY, t, offset))
    return loads


def rim_heights(incline: float = p.INCLINE) -> tuple[float, float]:
    """Height of the rim above the base top face at the front wall and at
    the back wall, on their inner faces."""
    back_h = g.back_wall_rim_h()
    front = g.at(p.HOPPER_FRONT_T, g.hopper_offset(p.RIM_FRONT_H), incline=incline).position
    back = g.at(g.back_wall_t(back_h), g.hopper_offset(back_h), incline=incline).position
    return g.height_above_base(front, incline), g.height_above_base(back, incline)


def _hopper_by_label(incline: float = p.INCLINE, **kwargs) -> dict:
    return _by_label(hopper_parts(incline, **kwargs))


def _check_hopper_parameters():
    """A1, A3's parameters, A6, and the derived values of §3."""
    assert p.HOPPER_SEAL_T >= p.HOPPER_SEAL_T_MIN
    assert abs(p.HOPPER_SEAL_T_MIN - (g.tail_shaft_t(p.TAIL_TAKEUP_MIN) + p.SLAT_PITCH + 3.0)) < 1e-9
    assert abs(p.HOPPER_SEAL_T_MIN - 25.0) < 1e-9 and abs(p.HOPPER_TAIL_KEEPOUT_T - 10.0) < 1e-9
    assert p.SEAL_ROOT_H - p.CLEAT_HEIGHT >= p.SEAL_CLEAT_CLEAR
    assert abs(p.SEAL_ROOT_H - 22.148) < 1e-3 and abs(p.SEAL_ROOT_T - 21.530) < 1e-3
    assert p.RIM_FRONT_H >= p.FLARE_TOP_H + 5.0
    assert abs(p.FLARE_TOP_H - 98.0) < 1e-9 and abs(p.FRONT_NOTCH_H - 63.0) < 1e-9 and p.BRUSH_LEN == 75.0
    assert abs(g.hopper_offset(0) - 22.947) < 1e-3
    assert abs(g.back_wall_t(0) - 19.59) < 0.01 and abs(g.back_wall_t(g.back_wall_rim_h()) - 36.1) < 0.05
    assert abs(g.back_wall_rim_h() - 188.8) < 0.05


def _check_hopper_gap_closure():
    """A2, and its control: with the seal at t = 0 at the shortest take-up,
    slats still open on the tail arc would be under it."""
    for takeup in _TAKEUPS:
        # Slats spread evenly round a longer loop, so the straight-run gap
        # grows with the take-up: closed means no wider than that plus the
        # spec's 0.05 -- README "Hopper resolutions".
        limit = p.HOPPER_GAP_CLOSED + p.SLAT_PITCH * (g.loop_length(takeup) / p.BELT_LOOP_LENGTH - 1)
        for phase in _PHASES:
            for t, width in slat_top_gaps(takeup, phase):
                if t >= p.HOPPER_SEAL_T:
                    assert width <= limit, f"{width:.2f} at t {t:.1f}, takeup {takeup}"
    widest = max(width for phase in _PHASES for t, width in slat_top_gaps(p.TAIL_TAKEUP_MIN, phase) if t >= 0.0)
    assert widest > p.HOPPER_GAP_OPEN, f"{widest:.2f}"


def _check_seal_clamp_height():
    """A3: the seal clamp's lowest point."""
    clamp = in_hopper(_hopper_by_label()["seal clamp"])
    assert clamp.bounding_box().min.Y >= p.CLEAT_HEIGHT + p.SEAL_CLEAT_CLEAR
    assert abs(clamp.bounding_box().min.Y - p.SEAL_CLAMP_LOW_H) < 1e-6


def _check_wall_slopes():
    """A4, and the slopes' own definitions checked against the solids at 40."""
    for incline in _HOPPER_GRID:
        assert g.flare_slope(incline) >= p.FLARE_SLOPE_MIN and g.back_wall_slope(incline) >= p.BACK_WALL_SLOPE_MIN
    assert abs(min(map(g.flare_slope, _HOPPER_GRID)) - 50.1) < 0.05 and min(map(g.back_wall_slope, _HOPPER_GRID)) == 40.0
    liner, wall = (_hopper_by_label()[name] for name in ("liner +z", "back wall"))
    flare = max((face for face in liner.faces() if face.geom_type == GeomType.PLANE), key=lambda face: face.area)
    assert abs(math.degrees(math.acos(abs(flare.normal_at().Y))) - g.flare_slope()) < 1e-6
    inner = max((face for face in wall.faces() if face.geom_type == GeomType.PLANE), key=lambda face: face.area)
    assert abs(math.degrees(math.acos(abs(inner.normal_at().Y))) - g.back_wall_slope()) < 1e-6


def rim_edge_angle(incline: float = p.INCLINE) -> float:
    """Angle from horizontal, deg, of the +z side panel's rim edge (A5)."""
    panel = _hopper_by_label(incline)["side panel +z"]
    in_face = [edge for edge in panel.edges().filter_by(GeomType.LINE) if abs((edge @ 1 - edge @ 0).Z) < 1e-6]
    rim = max(in_face, key=lambda edge: edge.center().Y)
    d = rim @ 1 - rim @ 0
    return math.degrees(math.atan2(d.Y, math.hypot(d.X, d.Z)))


def _check_rim_is_level():
    """A5."""
    assert abs(rim_edge_angle(p.RIM_LEVEL_INCLINE)) < p.RIM_LEVEL_TOL
    assert abs(abs(rim_edge_angle(p.TILT_MIN)) - (p.RIM_LEVEL_INCLINE - p.TILT_MIN)) < p.RIM_LEVEL_TOL


def _check_hopper_parts():
    """A7, A8."""
    for part in hopper_group().children:
        assert part.is_valid and len(part.solids()) == 1, part.label
    parts = _hopper_by_label()
    liner = in_hopper(parts["liner +z"])
    assert all(abs(a - b) < 1.5 for a, b in zip(bbox_size(liner), (110.0, 109.0, 70.0)))
    assert 35.0 <= volume_cm3(liner) <= 55.0
    assert abs(volume_cm3(parts["liner -z"]) - volume_cm3(liner)) < 1e-6
    rail = in_hopper(parts["carry rail"])
    assert all(abs(a - b) < 0.02 for a, b in zip(bbox_size(rail), (110.0, 15.447, 16.0)))
    assert 18.0 <= volume_cm3(rail) <= 28.0
    assert 40.0 <= volume_cm3(parts["rail bridge"]) <= 80.0


def _check_capacity():
    """B1, and B2's control: a rim at 60 holds too little at 55."""
    for incline in p.TILT_CHECK_ANGLES:
        assert hopper_fill(incline)[0] >= p.HOPPER_CAPACITY[0], f"{hopper_fill(incline)[0]:.2f} L at {incline}"
    assert hopper_fill(p.INCLINE)[0] <= p.HOPPER_CAPACITY[1]
    assert hopper_fill(p.TILT_MAX, p.HOPPER_CONTROL_RIM_H)[0] < p.HOPPER_CAPACITY[0]


def _check_hopper_clears_slats():
    """C1: nearest slat to any hopper part at every take-up, and with the
    slats pushed across by their play; the tight pair is cleat and liner."""
    for takeup in _TAKEUPS:
        d, s, part = hopper_slat_clearance(takeup)
        assert d >= p.HOPPER_SLAT_CLEAR, f"{s} is {d:.2f} from {part} at takeup {takeup}"
    for shift in (g.slat_lateral_play(), -g.slat_lateral_play()):
        d, s, part = hopper_slat_clearance(0.0, shift)
        assert d >= p.HOPPER_SLAT_CLEAR, f"{s} is {d:.2f} from {part} pushed {shift:+.2f}"
        assert part.startswith("liner") and abs(d - (p.SKIRT_INSET - p.CLEAT_LENGTH / 2 - g.slat_lateral_play())) < 1e-3


def _check_carry_rail():
    """C2 and C3: lugs run clear in the rail's groove, the contact faces run
    0.5 over its lands, and a rail 1.0 higher bites into the slats."""
    for takeup in _TAKEUPS:
        rail = _hopper_by_label(_RUN)["carry rail"]
        over = slats_over_rail(takeup, _RUN)
        assert len(over) >= 5
        assert not any(clash(s, rail) for s in over)
    rail = _hopper_by_label()["carry rail"]
    for s in slats_over_rail():
        d = min(face.distance_to(rail) for face in contact_faces(s))
        assert p.RAIL_LAND_GAP[0] <= d <= p.RAIL_LAND_GAP[1], f"{s.label}: {d:.3f}"
    raised = _hopper_by_label(rail_raise=1.0)["carry rail"]
    assert any(clash(s, raised, tol=1.0) for s in slats_over_rail())


def _check_brushes():
    """C4: the bristles' tip lines, and the metering clamp's whole range."""
    parts = _hopper_by_label()
    for name, want in (("seal", -p.SEAL_BRUSH_INTERFERENCE), ("metering", p.METER_GAP)):
        bristles = in_hopper(parts[f"{name} brush bristles"])
        tip = min(bristles.faces().filter_by(GeomType.PLANE), key=lambda face: face.center().Y)
        assert abs(tip.center().Y - want) < 0.1, name
    bolts = [
        g.at(p.HOPPER_FRONT_T, g.hopper_offset(p.METER_BOLT_H), z) * Rot(0, 90, 0) * Cylinder(p.M4_CLEARANCE_DIA / 2 - 0.25, 3 * p.METER_CLAMP_T)
        for z in p.METER_BOLT_Z
    ]
    for setting in (p.METER_GAP_MIN, p.METER_GAP, p.METER_GAP_MAX):
        clamp = _hopper_by_label(meter_gap=setting)["metering clamp"]
        assert not any(clash(bolt, clamp) for bolt in bolts), f"bolts outside the slots at {setting}"
        assert in_hopper(clamp).bounding_box().max.Y >= p.FRONT_NOTCH_H + p.METER_CLAMP_LAP
    over = _hopper_by_label(meter_gap=p.METER_GAP_MAX + 1.0)["metering clamp"]
    assert all(clash(bolt, over) for bolt in bolts)


def _tail_sweep(takeup: float):
    """The cleat tips' swept cylinder about the tail axis, as wide as the
    cleats with their play, and the part of the world it applies to: above
    the slat top plane and inside that width. Below the plane, inside the
    loop, no cleat ever goes; the rail and bridge live there, and C1 and C10
    check them against the real slats -- README "Hopper resolutions" (C5)."""
    span = p.CLEAT_LENGTH / 2 + g.slat_lateral_play()
    sweep = Cylinder(g.cleat_corner_radius(), 2 * span).moved(g.at(g.tail_shaft_t(takeup), 0, incline=_RUN))
    above = Pos(0, g.slat_top_radius(), 0) * Box(
        3 * p.FRAME_LENGTH, 3 * p.FRAME_LENGTH, 2 * span, align=(Align.CENTER, Align.MIN, Align.CENTER)
    )
    return sweep, above


def _check_hopper_tail():
    """C5, C6, C7: the tail shaft set, the cleat sweep, the keep-out, and
    the pillow blocks, bearings and spacers, at every take-up. C7 names a
    provisional envelope for the blocks; they are built now, so the check
    is against the real ones -- README "Hopper resolutions"."""
    parts = [part for part in hopper_parts(_RUN) if "bristles" not in part.label]
    for takeup in _TAKEUPS:
        shaft_set_ = _by_label(drivetrain_group(takeup=takeup, incline=_RUN).children)["tail shaft set"]
        sweep, above = _tail_sweep(takeup)
        blocks = [
            part
            for group in (pillow_blocks_group, bearings_group, spacers_group)
            for part in group(takeup=takeup, incline=_RUN).children
        ]
        for part in parts:
            assert distance_within(part, shaft_set_, p.HOPPER_CLEAR) >= p.HOPPER_CLEAR, part.label
            inside = part & above
            if inside.volume > 0:
                assert distance_within(inside, sweep, p.HOPPER_CLEAR) >= p.HOPPER_CLEAR, part.label
            assert min_distance(part, blocks, p.HOPPER_CLEAR) >= p.HOPPER_CLEAR, part.label
    for part in hopper_parts(_RUN):
        assert part.bounding_box().min.X >= p.HOPPER_TAIL_KEEPOUT_T, part.label


def _check_hopper_plates():
    """C8: feet to the plates along the run, panels to the plate tops and
    to the plates' M5 heads."""
    parts = _hopper_by_label(_RUN)
    feet = [part for label, part in parts.items() if label.startswith("hopper foot")]
    panels = [parts["side panel +z"], parts["side panel -z"]]
    radius, height = p.PLATE_BOLT_HEAD[0] / 2, p.PLATE_BOLT_HEAD[1]
    for takeup in _TAKEUPS:
        plates = plates_group(takeup=takeup, incline=_RUN).children
        for plate in plates:
            box = plate.bounding_box()
            for foot in feet:
                along = max(box.min.X - foot.bounding_box().max.X, foot.bounding_box().min.X - box.max.X)
                assert along >= p.HOPPER_CLEAR, f"{foot.label} is {along:.2f} from {plate.label}"
            t = g.run_coords(box.center(), _RUN)[0]
            heads = [
                g.at(t + x, g.plate_top_offset(), z, _RUN) * Rot(-90, 0, 0) * Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
                for x in (-p.PLATE_BOLT_X, p.PLATE_BOLT_X) for z in (-p.PLATE_BOLT_Z, p.PLATE_BOLT_Z)
            ]
            for panel in panels:
                assert distance_within(panel, plate, p.HOPPER_CLEAR) >= p.HOPPER_CLEAR - 1e-6, f"{panel.label} over {plate.label}"
                assert all(distance_within(panel, head, p.HOPPER_CLEAR) >= p.HOPPER_CLEAR for head in heads)


def _check_hopper_tilt():
    """C9 at all nine cases: the base, the hinge and the prop. The hopper
    does not move with the take-up, so the three take-ups are one case."""
    for incline in p.TILT_CHECK_ANGLES:
        others = tilt_frame_parts(incline) + tilt_base_parts(incline) + tilt_prop_parts(incline)
        for part in hopper_parts(incline):
            for other in others:
                need = p.BASE_CLEARANCE_MIN if other.label == "base_ref" else p.HOPPER_CLEAR
                assert distance_within(part, other, need) >= need, f"{part.label} / {other.label} at {incline}"


def _check_rail_bridge():
    """C10: the bridge against the returning run, at all nine cases."""
    for incline in p.TILT_CHECK_ANGLES:
        bridge = _hopper_by_label(incline)["rail bridge"]
        for takeup in _TAKEUPS:
            loop = slats_group(detail=True, takeup=takeup, incline=incline).children + belts_group(incline=incline).children
            for part in loop:
                assert distance_within(bridge, part, p.HOPPER_CLEAR) >= p.HOPPER_CLEAR, f"{part.label} at {incline}, {takeup}"


def _check_print_bed():
    """C11, for every printed part, not only the hopper's: each fits
    PRINT_BED in its print orientation."""
    for part, name, rotation in printed_parts():
        size = bbox_size(Rot(*rotation) * part)
        assert all(a <= b for a, b in zip(size, p.PRINT_BED)), f"{name}: {size}"


def _check_hopper_loads():
    """D1, D2, D3."""
    assert p.HOPPER_MASS_RANGE[0] <= hopper_mass()[0] <= p.HOPPER_MASS_RANGE[1], f"{hopper_mass()[0]:.3f} kg"
    for incline in _HOPPER_GRID:
        worst = g.prop_force(incline, g.doubled(prop_loads(incline)))
        assert worst <= p.PROP_FORCE_MAX, f"{worst:.0f} N doubled at {incline}"
        for full in (False, True):
            assert g.prop_force(incline, prop_loads(incline, full)) >= p.PROP_FORCE_MIN, f"at {incline}"


def hopper_report() -> list[str]:
    """The tables hopper-spec §8 asks to be printed: wall slopes (A4),
    capacity (B1), the prop force with the hopper (D2), and C1's tight pair."""
    lines = ["", "Hopper: wall slopes from horizontal, level fill, and the prop force with the hopper"]
    lines.append("  incline   flare   back wall   level fill   load at (t, offset)   rim over base front / back   prop empty / full / doubled")
    for incline in _HOPPER_GRID:
        litres, t, offset = hopper_fill(incline)
        front, back = rim_heights(incline)
        forces = [g.prop_force(incline, prop_loads(incline, False)), g.prop_force(incline, prop_loads(incline))]
        forces.append(g.prop_force(incline, g.doubled(prop_loads(incline))))
        lines.append(
            f"  {incline:7.1f}   {g.flare_slope(incline):5.1f}   {g.back_wall_slope(incline):9.1f}   {litres:8.2f} L"
            f"   ({t:5.1f}, {offset:5.1f})        {front:6.1f} / {back:6.1f}             "
            + " / ".join(f"{force:5.1f}" for force in forces) + " N"
        )
    mass, t, offset = hopper_mass()
    margin = p.PROP_FORCE_MAX - g.prop_force(p.TILT_MIN, g.doubled(prop_loads(p.TILT_MIN)))
    d, s, part = hopper_slat_clearance(0.0, g.slat_lateral_play())
    lines += [
        f"  hopper {mass:.3f} kg at t {t:.1f}, offset {offset:.1f}; LEGO at {p.LOAD_BULK_DENSITY:g} kg/L",
        f"  margin under PROP_FORCE_MAX, doubled, at {p.TILT_MIN:g} deg: {margin:.2f} N",
        f"  tightest slat clearance, slats pushed their full play: {d:.2f}, {s} / {part}",
    ]
    return lines


# Checks known to fail for a recorded reason. A check listed here counts as
# XFAIL when it fails and as a failure of the run when it unexpectedly
# passes -- at which point remove it from this table. Empty since
# PROP_FORCE_MAX was raised to meet the doubled-weight guard.
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
    ("tilt: geometry and base frame", _check_tilt_geometry),
    ("tilt T2: frame clears the base", _check_frame_clears_base),
    ("tilt T3: tail shaft height", _check_tail_shaft_height),
    ("tilt T4: hinge parts", _check_hinge_parts),
    ("tilt T5/T6: cross-member", _check_cross_member),
    ("tilt T7: prop clears the frame", _check_prop_clears_frame),
    ("tilt T8: prop swing", _check_prop_swing),
    ("tilt T9: prop length table", _check_prop_length_table),
    ("tilt T10: length budget", _check_length_budget),
    ("tilt T11: prop force", _check_prop_force),
    ("tilt T11: prop force at doubled weight", _check_prop_force_doubled),
    ("tilt: parts", _check_tilt_parts),
    ("pillow block", _check_pillow_block),
    ("pillow block: bearing press fit and controls", _check_bearing_press_fit),
    ("spacer and bearing", _check_spacer_and_bearing),
    ("bearing coupon", _check_bearing_coupon),
    ("end plates: pillow block holes", _check_end_plate_holes),
    ("pillow blocks and spacers clear every slat", _check_slats_clear_pillow_blocks),
    ("pillow blocks, bearings, spacers clear belts and shaft sets", _check_bearing_parts_clear_drivetrain),
    ("pillow blocks on their plates, on their shafts", _check_blocks_on_plates),
    ("drive: parameters and stack", _check_drive_parameters),
    ("drive: motor bracket and pilot-bore control", _check_motor_bracket),
    ("drive: motor, coupler, head shaft", _check_drive_parts),
    ("drive: coupler clearances", _check_coupler_clearances),
    ("drive: clears belts, shaft sets, blocks, plates", _check_drive_clears_drivetrain),
    ("drive: clears the base", _check_drive_clears_base),
    ("hopper A1/A3/A6: parameters", _check_hopper_parameters),
    ("hopper A2: slat gaps closed under the seal", _check_hopper_gap_closure),
    ("hopper A3: seal clamp above the cleats", _check_seal_clamp_height),
    ("hopper A4: wall slopes", _check_wall_slopes),
    ("hopper A5: rim level at 40", _check_rim_is_level),
    ("hopper A7/A8: parts", _check_hopper_parts),
    ("hopper B1/B2: capacity", _check_capacity),
    ("hopper C1: slat clearance", _check_hopper_clears_slats),
    ("hopper C2/C3: carry rail", _check_carry_rail),
    ("hopper C4: brushes", _check_brushes),
    ("hopper C5/C6/C7: tail", _check_hopper_tail),
    ("hopper C8: plates", _check_hopper_plates),
    ("hopper C9: base, hinge and prop", _check_hopper_tilt),
    ("hopper C10: rail bridge", _check_rail_bridge),
    ("print bed: every printed part (hopper C11)", _check_print_bed),
    ("hopper D1-D3: loads", _check_hopper_loads),
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
    passed = run_checks()
    print("\n".join(tilt_report() + hopper_report()))
    sys.exit(0 if passed else 1)
