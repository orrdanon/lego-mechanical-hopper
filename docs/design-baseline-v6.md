# Feed elevator: design baseline, v6

Status as of 2026-10-03, commit `3a08dce` (the merge of branch `skirts`).
All dimensions are millimetres and degrees.

This document describes what has been built and decided so far, so that
specifications for the **remaining parts of the machine** can be written
against it: the tail take-up, the discharge and the base. It is
self-contained: it replaces `design-baseline-v5.md` (and v4 .. v1) and the
specification files as the reference for new work. Where a number here and
an older document disagree, this document (and `params.py`, which it is
taken from) is correct.

**What changed since v5.** The side skirts are built
(`docs/specs/spec-skirts.md`, §9), and with them:

1. **Side skirts** continue the hopper's channel unchanged (inset 38, gap
   1.5 over the slat top, 28 high) from the front wall's outer face,
   t = 136, to t = 350: 6 ply strips on printed uprights.
2. **The carry rail runs the whole carrying run**, as rail A (the hopper's,
   now 30 .. 176.75) and rail B (177.25 .. 330), joined on the station at
   177. The slats' lugs are in a groove everywhere but on and next to the
   wheels, so the ±0.71 lateral play holds along the whole run.
3. **Support stations are split**: two posts on the plate, an arm across
   them between the runs, slid in sideways with the belt on. The hopper's
   one-piece rail bridge at 88.5 was replaced by one. The rails are fixed
   by side screws through the arms' cheeks, not from below.
4. **`CLEAT_LENGTH` is 73.0** (was 74.0): the cleat ends clear the skirts
   and the hopper's liners by 1.5, **0.79** at worst-case play (was 0.29).
5. **The skirts weigh 0.315 kg**, in the prop force: doubled at 25°,
   **224.2 N, 25.8 N of margin** (was 209.7 N, 40.3 N).

Nothing else on the conveyor moved: every other datum of v5 still holds.

Every value is labelled one of:

- **fixed** - decided and implemented; changing it invalidates built and tested geometry
- **catalogue** - a published figure for a bought part, not yet measured on the real one
- **provisional** - a starting guess, expected to be tuned; §11 says what settles each
- **open** - not decided; input wanted

**Nothing has been printed or physically tested yet.** Everything below is
CAD that passes its own checks. §11 lists the physical tests, in order, that
stand between this model and a working machine.

---

## 1. The machine

A feed elevator for a LEGO-sorting machine: a cleated slat conveyor, inclined
at an adjustable 25° .. 55° (nominally 40°), that lifts loose LEGO parts out
of a hopper and drops them off the head end.

- Two identical closed-loop HTD-3M timing belts run side by side, 54 mm
  apart, teeth inward, over a tail shaft and a head shaft 354 mm apart.
- 46 printed slats clip across the *backs* of both belts and form the
  carrying surface. Every second slat carries a cleat.
- Each shaft carries one printed **shaft set**, fixed to it: two toothed
  pulleys, one per belt, and between them a V-grooved **guide wheel**. A lug
  under every slat runs in that groove. The slats hold the two belts at their
  spacing; the guide holds the slats on the machine centreline. There are no
  pulley flanges.
- Both shafts rotate. The tail shaft set is identical to the head one and is
  fixed to its shaft, so the two belts are tied in phase through a shaft at
  both ends, not only through the slats.
- Each 8 mm shaft runs in two 608ZZ bearings pressed into printed pillow
  blocks bolted to a plywood bridge plate, which bolts to the top of an
  aluminium 2020 extrusion frame. The whole frame is inclined with the run.
- The frame **hinges** on two M8 bolts near its bottom tail corner, in
  printed blocks on the base. A single **screw prop** between a cross-member
  under the frame and a block on the base sets the angle: turning a knob
  changes its length, about 52 turns over the whole range, and a lock nut
  holds the setting.
- The **tail bridge plate slides** along the frame's T-slots. That is the
  belt take-up. The mechanism that pushes it has not been designed.
- The head shaft is driven directly by a NEMA 17 stepper through a flexible
  coupler, at a target 30 rpm, which gives 60 mm/s belt speed.
- A **hopper** on the frame, over the carrying run near the tail, holds 1.9 ..
  2.4 L of loose LEGO; the cleats draw parts out from under the pile and a
  metering brush lets one cleat pocket's worth past at a time.
- From the hopper to the head, **side skirts** keep parts on the slats, and
  a **carry rail** under the whole carrying run supports the slats and
  guides their lugs, on printed **support stations** on the three middle
  bridge plates.

| Item | Status |
|---|---|
| Slat, plain and cleated, with guide lug | modelled, checked, STL exported; not yet printed |
| Tooth profile: belt tooth and standard pulley groove | built; groove verified against a manufacturer's model |
| Shaft set (2 pulleys + guide wheel), two off | modelled, checked, STL exported; not yet printed |
| Shafts, belts | modelled as reference solids (bought parts) |
| Calibration coupons, three (ring, guide, bearing) | modelled, STL exported; not yet printed |
| 2020 frame | modelled as a reference solid (owned hardware) |
| Bridge plates, five | modelled as reference solids with frame bolt holes, and the pillow-block holes in the end two; cut list generated |
| Pillow blocks (4, identical) and spacer tubes (4) | modelled, checked, STL exported; not yet printed |
| 608ZZ bearings (4) | reference solids (bought); listed by `assembly.py --report` |
| Tilt: hinge brackets and blocks (2 mirror pairs), frame clevis, prop body, foot, knob, base pin block | modelled, checked, STL exported; not yet printed |
| Tilt: cross-member (2020, cut), M8 rod | reference solids; on the cut list |
| Tilt: M8 bolts, nuts, washers | reference solids; listed by `assembly.py --report` |
| Drive: motor bracket | modelled, checked, STL exported; not yet printed |
| Drive: NEMA 17 stepper, flexible coupler | reference solids (bought); listed by `assembly.py --report` |
| Hopper: liners (mirror pair), seal and metering clamps, feet (2 mirror pairs), corner cleats (8), carry rail A | modelled, checked, STL exported; not yet printed |
| Hopper: side panels (2), back wall, front wall | plywood; reference solids; on the cut list as corner and hole coordinates |
| Hopper: strip brushes (2) | reference solids (bought); listed by `assembly.py --report` |
| Skirts: carry rail B, station posts (6) and arms (3, one the hopper's at 88.5), skirt uprights (4) | modelled, checked, STL exported; not yet printed |
| Skirts: two strips, 6 ply | plywood; reference solids; on the cut list |
| Assembly | frame, plates, drivetrain, belts, all 46 slats round the whole loop, the tilt, pillow blocks, bearings and spacers, the drive, the hopper, the skirts, at any incline |
| **Base** | **open; a placeholder slab for clearance checks only** |
| **Tail take-up mechanism (jacking screw)** | **travel decided and clash-checked; mechanism not designed** |
| **Discharge** | **not designed** |
| **`DRIVE_SIDE`** | **open; both sides are built and checked** |

---

## 2. Coordinate system and datums

Machine frame: origin on the **tail shaft axis** at the machine centre plane.
+X horizontal towards the head end, +Y up, +Z across the machine along the
shaft axes. Both shaft axes are parallel to Z.

**The machine frame does not tilt.** Changing the incline θ rotates the
conveyor, frame and everything on them about the machine origin; the base,
which physically stays put, is what moves in machine coordinates (§2.4). So
every position given in this document in run coordinates (t, offset) is valid
at every incline, and every part on the frame keeps its placement.

| Datum | Value |
|---|---|
| Incline θ | `INCLINE` = 40° nominal; `TILT_MIN` .. `TILT_MAX` = 25° .. 55° |
| Run direction (unit) | (cos θ, sin θ, 0) |
| Run normal (unit), out of the carrying face | (-sin θ, cos θ, 0) |
| Tail shaft axis | (0, 0, z) at nominal take-up, at every θ |
| Head shaft axis | 354.0 along the run: (271.18, 227.55, z) at 40°; (320.83, 149.61) at 25°; (203.05, 289.98) at 55° |
| Belt centrelines | z = +27 and z = -27 |
| Guide groove centre plane | z = 0 |

### 2.1 Positions on the straight run: `at(t, offset, lateral, incline)`

- `t` - distance along the run from the tail shaft axis
- `offset` - distance from the **shaft axis** along the run normal; positive
  is outward through the carrying run, negative is down towards the frame
- `lateral` - z
- `incline` - θ, default 40°

So `offset = 0` is on the shaft centreline.

### 2.2 Positions on the belt: `loop_at(s, takeup, incline)`

Anything that rides the belt is placed by distance `s` round the loop,
measured **along the belt's pitch line**, because that is where tooth pitch,
and therefore slat pitch, is defined. The position returned is on the belt
back, where a slat sits. Local +x is the direction of travel, +y points out
of the belt back, +z is machine z.

| s | Stretch |
|---|---|
| 0 .. 354 | carrying run; `loop_at(s)` equals `at(s, 19.947)` |
| 354 .. 414 | head arc, 60.0 of pitch line = 20 teeth |
| 414 .. 768 | return run, travelling tailward, belt back facing the plates |
| 768 .. 828 | tail arc |

Slat `i` sits at `loop_at(18 · i)`; slats with even `i` are cleated.

### 2.3 Radial stations

All measured from a shaft axis. On the straight runs the same numbers are
offsets from the line joining the shaft axes: positive on the carrying side,
negative on the return side.

| Surface | Radius / offset | |
|---|---|---|
| Frame rail underside, cross-member underside | -77.0 | fixed |
| Frame rail centreline, hinge axis | -67.0 | fixed |
| Frame rail top faces | -57.0 | fixed |
| Bridge plate top faces (pillow blocks mount here) | -48.0 | fixed, set by the pillow block |
| Pillow block foot top face | -41.0 | provisional (`PB_FOOT_HEIGHT`) |
| Shaft surface | 4.0 | fixed |
| Drum of the shaft set, between wheel and pulleys | 13.0 | provisional |
| Guide groove bottom | 14.447 | derived |
| Guide lug tip | 15.947 | derived |
| Saddle tab tips | 16.347 | derived |
| Pulley groove bottom | 17.501 | catalogue |
| Belt tooth tips | 17.547 | derived |
| Pulley OD = belt land | 18.718 | derived |
| Belt pitch line | 19.099 | derived |
| Guide wheel rim | 19.447 | derived |
| **Belt back = slat contact face** | **19.947** | derived |
| Slat top face = carrying surface | 22.947 | derived |
| Cleat tip | 34.947 | derived |

Swept radii round a shaft, for anything that has to stay clear of the ends of
the conveyor (hopper walls, guards, a discharge chute):

| Swept by | Radius |
|---|---|
| Top-face corners of a slat | 24.47 |
| Cleat tip corners | 35.00 |

**Local frame convention for parts.** Anything placed on the run is modelled
with local +x along the run, +y out along the run normal, +z across the
machine, and its origin on the face it mates with, so that placing it is a
single transform with no corrective offset. Slat: centre of its belt-contact
face. Shaft set and shaft: on the axis at the guide groove's centre plane.
Bridge plate: centre of its top face. Pillow block: underside of its foot,
under the bearing axis, in the bearing centre plane, +z outboard (the -z
block is the same part turned 180° about y). Bearing: on the axis at mid-width.
Spacer: on the axis at the face that meets the bearing. Hopper parts are
laid out in **hopper coordinates** (t, h, z), h above the slat top face, and
placed with `at(t, hopper_offset(h), z)` (§8). Station post and skirt
upright: bottom face at the inner face (z = ±44), centred on the station,
+z outboard (the -z one turned 180° about y); station arm: bottom face,
centre plane; rail: land plane, centre plane, at its tail end; skirt: inner
face at its bottom edge, at t = 136 (the -z strip a mirror image) (§9).

### 2.4 The base frame: `base_frame(incline)`

Anything standing on the base is placed in the **base frame**: origin on the
base top face directly below the hinge axis, with machine axes (+x horizontal
toward the head, +y up, +z across). Its horizontal coordinate is written `bx`
and its height above the base `by`; the hinge axis is at (0, 20). Base-fixed
parts are placed with `base_frame(incline)` and never rotated; frame-fixed
parts are placed with `at(..., incline=incline)`.

The hinge axis is at t = -50.0, offset -67.0 (rail centreline), fixed to the
frame, not the take-up. Where the machine sits over the base, in (bx, by), at
take-up 0 unless stated:

| | 25° | 40° | 55° |
|---|---|---|---|
| Tail shaft axis | (17.0, 101.9) | (-4.8, 103.5) | (-26.2, 99.4) |
| Tail shaft height, over take-up -4.0 .. +2.0 | 103.5 .. 101.0 | 106.0 .. 102.2 | 102.7 .. 97.7 |
| Head shaft axis | (337.8, 251.5) | (266.4, 331.0) | (176.8, 389.4) |
| Carrying surface (slat top) over the head shaft | (328.1, 272.3) | (251.7, 348.6) | (158.0, 402.5) |
| Frame tail end, bottom corner | (-4.8, 6.7) | (-1.2, 5.9) | (2.5, 6.1) |
| Frame head end, rail underside | (495.4, 240.0) | (421.6, 360.7) | (319.1, 458.2) |
| Frame head end, rail top | (487.0, 258.1) | (408.8, 376.1) | (302.7, 469.7) |
| Prop pin B (base-fixed) | (140.0, 15.0) | (140.0, 15.0) | (140.0, 15.0) |
| Motor (drive), envelope bx / by | 309.7 .. 365.9 / 223.4 .. 279.6 | 236.6 .. 296.2 / 301.2 .. 360.8 | 147.4 .. 206.3 / 359.9 .. 418.8 |
| Hopper rim above the base, front / back wall | 277.3 / 309.0 | 288.9 / 288.9 | 282.1 / 250.4 |
| Tail pillow blocks, envelope bx / by, over the take-up | 0.2 .. 60.8 / 48.2 .. 118.5 | -21.3 .. 46.0 / 51.3 .. 121.0 | -42.4 .. 28.0 / 52.2 .. 117.7 |
| Head pillow blocks, envelope bx / by | 322.8 .. 378.1 / 198.7 .. 266.5 | 251.4 .. 314.1 / 280.1 .. 346.0 | 161.8 .. 228.8 / 343.8 .. 404.4 |

So over the tilt range the **tail shaft moves 43 horizontally** and stays
98 .. 106 above the base, while the **head shaft moves 161 horizontally and
138 vertically**. The frame's tail corner stays about 6 above the base.

---

## 3. The belt

A stock closed-loop belt, bought, not made.

| Parameter | Name in `params.py` | Value | |
|---|---|---|---|
| Profile | `BELT_PROFILE` | HTD-3M | fixed |
| Pitch | `BELT_PITCH` | 3.0 | fixed |
| Pitch length | `BELT_LOOP_LENGTH` | 828.0 (276 teeth) | fixed |
| Width | `BELT_WIDTH` | 15.0 | fixed |
| Overall thickness, tooth tip to back | `BELT_THICKNESS` | 2.4 | catalogue (some sheets give 2.44) |
| Pitch line differential | `BELT_PLD` | 0.381 | catalogue |
| Tooth height | `TOOTH_HEIGHT` | 1.171 | derived, pinned to the published 1.17 |
| Backing thickness | `BELT_BACK_THICKNESS` | 1.229 | derived, thickness - tooth height |
| Belt centre spacing | `BELT_SPACING` | 54.0 | fixed |
| Quantity | | 2 | fixed |

Layout that follows from it:

- Centre distance `CENTRE_DIST = (828 - π · PD) / 2 = 354.0`, exactly 118
  pitches per straight span. It is a derived value, not an input.
- 180° wrap on each pulley, 20 teeth in mesh.
- Loop = 118 + 118 + 20 + 20 = 276 teeth.
- Each belt occupies z = ±19.5 .. ±34.5. It overhangs its 5.0 pulley face by
  5.0 on each side.

In the CAD project the belt is a **reference solid**, never exported: a smooth
backing band for the assembly, and toothed segments for checking that the
belt model sits in the pulley groove.

---

## 4. The slat

Printed, 46 off: 23 plain and 23 cleated. **Do not treat the slat as frozen**
until the saddle and guide fits in §11 pass; but nothing new should be
specified that requires changing it.

### 4.1 Body and cleat

| | Value | |
|---|---|---|
| Slat pitch along the belt | 18.0 = 6 belt teeth; 46 slats round the loop | fixed |
| Slat body | 17.0 along the run × 3.0 thick × 80.0 across the machine | width provisional |
| Gap between adjacent slats on a straight run | 1.0 | provisional, follows the width |
| Gap between adjacent slats round a pulley | opens to 2.96 at the bottom corners, 5.7 at the top faces | derived |
| Cleat | every 2nd slat; 12.0 high, 10.0 wide at the root tapering to 4.0 at the tip, **73.0 long** (z = ±36.5; was 74.0, spec-skirts), 1.0 root fillets | height provisional |
| Edge chamfer | 0.5 | fixed |
| Bounding box, plain / cleated | 17 × 7 × 80 / 17 × 19 × 80 | derived |
| Volume, plain / cleated | 4.54 / 10.68 cm³ | derived |
| Print orientation | top face down; tabs and lug up | fixed |

The slat count must stay an integer (`828 / 18 = 46`) and even, so the cleat
pattern closes across the belt seam; both are asserted in `params.py`.

**The gap is not what lets slats go round the pulleys.** Slats sit on the belt
back, outside the pitch line, so they fan apart on an arc; the gap is never
smaller than on the straight runs. It is 1.0 rather than the earlier 2.0 so
that thin LEGO elements cannot wedge edge-on between slats. The specs' older
rule still holds too: the gap must stay under 3.0 so that a 1×1 plate cannot
drop through.

### 4.2 Saddle: how a slat holds a belt

Each slat has two saddles, one per belt. A saddle is a pair of tabs hanging
from the belt-contact face that grip the two **edges** of the belt. There is
no fastener and **nothing engages the belt teeth**, so a slat's position
along the belt is set by hand at assembly and held by friction alone.

| Parameter | Value | |
|---|---|---|
| Tab length along the run | 7.0 (≤ 2.5 belt pitches) | fixed |
| Tab thickness across the machine | 2.5 | fixed |
| Tab depth below the belt-contact face | 3.6 = belt 2.4 + 0.2 gap + lip 1.0 | provisional |
| Gap between the facing tab faces | 14.8 = belt width - 0.2 interference | provisional |
| Retention lip at each tab tip | projects 0.8 inward, 1.0 high; upper face 0.2 under the belt | fixed |

Tab faces in slat-local z, for the +z belt (mirror for the other):

```
guide lug   -5.5 .. 5.5    (at the contact face; 3.0 wide at its tip)
inner tab   17.1 .. 19.6   (lip to 20.4)
belt        19.6 .. 34.4   (nominal 15.0 belt squeezed into 14.8)
outer tab   34.4 .. 36.9   (lip from 33.6)
slat end    40.0           (3.1 of slat beyond the outer tab)
```

### 4.3 Guide lug

A trapezoidal ridge under every slat, centred on z = 0, that runs in the
V-groove of each shaft set's guide wheel. It is the machine's only lateral
constraint: the slats locate the belts, the guide locates the slats.

| Parameter | Name | Value | |
|---|---|---|---|
| Depth below the contact face | `LUG_DEPTH` | 4.0 | provisional |
| Width at the tip / at the contact face | `LUG_TIP_WIDTH` / `LUG_TOP_WIDTH` | 3.0 / 11.0 | provisional / derived |
| Included angle | `LUG_ANGLE` | 90° (45° flanks, so both lug and groove print unsupported) | fixed |
| Length along the run | `LUG_LENGTH` | 8.0 | provisional |
| Lead-in chamfer, both ends, tip and flanks | `LUG_END_CHAMFER` | 1.0 | fixed |
| Clearance to the groove, normal to each flank | `GROOVE_FLANK_CLEAR` | 0.5 | provisional |
| **Lateral play of a slat before a flank engages** | | **±0.71** | derived |

The lug runs in a wheel groove while its slat is on a pulley, and **along
the carrying run in the carry rails' groove**, from t = 30 to 330 (§9), the
same section cut by the same code, so the play is the same ±0.71. It is
free only on the returning run and for about 25 between each wheel and the
end of a rail, where the belts' stiffness holds it.

---

## 5. The drivetrain

### 5.1 Shaft set

One printed part per shaft, two off, identical head and tail. Symmetric about
z = 0, so it goes on the shaft either way round and prints either end down.
PETG, axis vertical, no support.

Profile by zone, for z ≥ 0 and mirrored:

| Zone | z from | z to | Radius | What runs beside it |
|---|---|---|---|---|
| Guide wheel | 0 | 8.0 | 19.447 rim | slat underside at 19.947; lug in the groove |
| Wheel chamfer | 8.0 | 14.447 | 45° cone, 19.447 → 13.0 | nothing |
| Drum | 14.447 | 20.7 | 13.0 | inner saddle tabs and lips, tips at r = 16.347 |
| Flare | 20.7 | 24.5 | 45° cone, 13.0 → 16.8 | overhanging belt teeth at r ≥ 17.547 |
| Pulley | 24.5 | 29.5 | 18.718 OD, 40 grooves | the belt |

| Parameter | Name | Value | |
|---|---|---|---|
| Overall | | 38.894 dia × 59.0 long, 44.9 cm³ | derived |
| Teeth | `PULLEY_TEETH` | 40 | fixed |
| Pitch diameter | `PULLEY_PD` | 38.197 = 40 × 3 / π | derived |
| Outside diameter | `PULLEY_OD` | 37.435 = PD - 2 × PLD | derived |
| Toothed face width | `PULLEY_FACE_WIDTH` | 5.0, centred on each belt | fixed |
| Drum diameter | `DRUM_DIA` | 26.0 | provisional |
| Flare radius under each pulley face | `PULLEY_SKIRT_R` | 16.8 (nothing to do with the side skirts) | provisional |
| Guide wheel width | `GUIDE_WIDTH` | 16.0 | provisional |
| Guide groove | | bottom r = 14.447, 11.4 wide at the rim, 2.3 land each side | derived |
| End chamfer | `END_CHAMFER` | 0.3, outer edge of both end faces | fixed |
| Bore | `PULLEY_BORE` + `_CLEARANCE` | 8.0 + 0.15, chamfered 0.4 | clearance provisional |

Both pulleys are one print, so their teeth are in phase by construction. A
land, not a groove, lies on the part's local +y.

### 5.2 Tooth form

The pulley groove is **the standard HTD-3M groove for a 40-tooth pulley**,
rebuilt in closed form from five values read out of a manufacturer's model
(CADENAS PARTsolutions 40015040; licence CC BY-ND 4.0, credit CADENAS). It is
valid for 40 teeth only. The rebuild is tested against four junction points
read from that model and meets them to 0.0025.

| Parameter | Name | Value | |
|---|---|---|---|
| Bottom arc radius, about the pulley axis | `PULLEY_GROOVE_BOTTOM_R` | 17.501 | catalogue |
| Flank arc radius, concave | `PULLEY_GROOVE_FLANK_R` | 0.700 | catalogue |
| Flank arc centre, tangential offset | `PULLEY_GROOVE_FLANK_U` | 0.2476 | catalogue |
| Tip radius onto the OD, convex | `PULLEY_GROOVE_TIP_R` | 0.191 | catalogue |
| Tip arc centre, tangential offset | `PULLEY_GROOVE_TIP_U` | 1.1883 | catalogue |
| Groove depth | `PULLEY_GROOVE_DEPTH` | 1.2165 | derived |
| Printer compensation, groove / OD | `PULLEY_GROOVE_COMP` / `PULLEY_OD_COMP` | 0.0 / 0.0 | provisional, set from the ring coupon |

The groove is 2.40 wide at the OD, leaving a 0.537 land, and already contains
the standard's designed running clearance. The only tuning is printer
compensation.

The **belt tooth** is a separate, approximate construction (one flank arc of
radius 0.79 plus root fillets of 0.26) used for the belt reference solid
only. Nothing printed depends on it. It is checked to sit in the standard
groove without overlap, clearing the bottom by 0.046.

### 5.3 Fixing to the shaft

| Parameter | Name | Value | |
|---|---|---|---|
| Grub screws | `PULLEY_GRUB_M` | two M4, radial, same angular position | fixed |
| Grub planes | `GRUB_Z` | z = ±17.5, in the drum zones | provisional |
| Heat-set insert pocket | `PULLEY_INSERT_DIA` / `_DEPTH` | 5.6 dia × 6.0 deep, 2.9 of wall left over the bore | provisional |
| Flat filed on the shaft | `SHAFT_FLAT_DEPTH` / `_LENGTH` | 0.5 deep × 45.0 long, centred | fixed |

Both grubs bear on the one flat and carry the torque. Axially, the shaft set
is slid until both spacer tubes (§6.1) are snug, backed off to leave
`SHAFT_END_PLAY` = 0.4, and then the grubs are tightened. **Both shaft sets
sit at the same z** because both are referenced to identical blocks at
z = ±50, not because they were measured.

### 5.4 Calibration coupons

Two small printed parts, made by the same code as the shaft set so that they
calibrate it: a **ring coupon** (the real 40-groove outline, 3.0 thick, 8.15
bore) and a **guide coupon** (the guide wheel zone alone, 16.0 thick). A third,
the **bearing coupon**, is made by the pillow block's pocket code (§6.1).

---

## 6. Shafts, bearings and structure

| Parameter | Value | |
|---|---|---|
| Incline | 25° .. 55° from horizontal, set by hand; 40° nominal (§7) | range provisional |
| Shafts | 8.0 dia, with the flat of §5.3: tail 145.0, centred; head 140.0, 17.5 past the bearing on the drive end, the flat still centred on the shaft set | fixed |
| Bearing centres | 100.0 (z = ±50) | fixed |
| Shaft axis above the bridge plate top face | 48.0 | fixed, by the printed pillow block (§6.1) |
| Shaft speed | 30 rpm → 60 mm/s | fixed target |
| Frame | 2020 extrusion rectangle, 552 long × 274 wide overall, 234 between rails | fixed, owned, uncut |
| Frame position along the run | from t = -60 to t = 492; 138 of frame beyond the head shaft | fixed |
| Bridge plates | five, 9 plywood, 45 along the run × 274 across, on top of both rails, M5 into T-nuts at x = ±12, z = ±127; the end two also have 4 × Ø5.0 at x = ±14, z = ±40.25 for the pillow blocks | fixed |
| Plate stations | t = 0, 88.5, 177, 265.5, 354; the end two carry the pillow blocks, the head one the motor bracket too; the middle three carry the support stations (§9), the one at 88.5 inside the hopper | fixed |
| Tail take-up travel | `TAIL_TAKEUP_MIN` .. `_MAX` = -4.0 (toward the head, to fit the belt) .. +2.0 (away, to tension) | provisional |

**Along each shaft, from the centre outwards:**

```
guide wheel           0 .. 8.0
shaft set body        to 29.5      (pulley face 24.5 .. 29.5)
end play              29.5 .. 29.7 (0.2 each side at nominal)
spacer tube           29.7 .. 46.5 (rotates with the shaft; Ø11.0)
belt                  19.5 .. 34.5
pillow block foot     from 34.0    (below the run: top face at offset -41.0)
outer tab             to 36.9
slat end              40.0 (± 0.71 play)  <- everything inside this rotates or travels
block inboard face    46.5   = bearing inner face
bearing centre        50.0
bearing outer face    53.5   (the block's lip beyond it, 1.5 thick)
block outboard face   55.0
shaft end             72.5  (tail, and the head's non-drive end)
head shaft, drive end 67.5  -> coupler 57.0 .. 82.0, motor face 95.5, motor back 135.5
```

So the slat ends run 5.79 from the block towers at worst-case play. The
head shaft's drive end runs 12.5 past the block's outboard face into the
coupler (§6.2); which end that is, is **open**.

**Take-up.** The tail bridge plate, the tail pillow blocks, bearings and
spacers, the tail shaft and its shaft set move together along the run. The
assembly is built at take-up 0 (354.0 centres). Slat, drivetrain, plate,
pillow-block, spacer and tilt clearances have been clash-checked at -4.0, 0
and +2.0, each at 25°, 40° and 55°. With the tail plate at -4.0 it is 39.5
clear of the next plate. What pushes the plate is **open**: a jacking screw
in a block bolted to the frame is the intent. It must stay off the rails'
outer faces from t = -60 to -20 and out of the space outboard of them: the
hinge is there (§7.1).

**Returning-run clearance.** Cleats on the returning (lower) run point at the
bridge plates. Cleat tip radius is 34.947 against a 48.0 shaft height, 13.05
to the plate; but the pillow blocks' feet reach inboard under the slats (to
z = ±34, and the cleats run to z = ±37), 7.0 high, so the governing clearance
is **6.05, foot top to cleat tips**; the check requires > 5.0. Raising
`PB_FOOT_HEIGHT` or `CLEAT_HEIGHT` eats it directly.

### 6.1 Pillow blocks, bearings and spacers

Four identical printed PETG pillow blocks, two per shaft, each on an end
bridge plate with its bearing centre at z = ±50. The two on a shaft are the
same part turned end for end, each with a retaining **lip on its outboard
side only**. A printed spacer tube between each bearing's inner ring and the
shaft set means an axial push on the shaft set goes through one spacer and
one bearing into one lip: the shaft is captured between the two lips and
neither press fit carries axial load. **No shaft collars**: one would push a
bearing toward its open side against the press fit alone.

| Parameter | Name | Value | |
|---|---|---|---|
| Bearing | `BEARING_BORE` × `_OD` × `_WIDTH` | 608ZZ, 8 × 22 × 7; inner ring face Ø12.1 | catalogue |
| Block, overall | | 44 along the run × 63 high × 21 across (z = ±34 .. ±55), 16.6 cm³ | derived |
| Foot | `PB_FOOT_LENGTH` × `_HEIGHT`, `PB_FOOT_INBOARD_Z` | 44 × 7.0, from z = ±34.0 to ±55.0 | provisional |
| Tower | `PB_TOWER_WIDTH`, `PB_BOSS_RADIUS` | 30 wide, capped by R 15.0 about the bearing axis (top at offset +15.0), z = ±46.5 .. ±55.0; R 3.0 fillets to the foot | provisional |
| Pocket | `PB_POCKET_DIA` × `_DEPTH` | 22.4 × 7.0, open inboard, 0.5 mouth chamfer; the bearing ends flush with the inboard face | provisional |
| Press fit | `PB_RIB_TIP_DIA` | six crush ribs, 2.0 → 0.8 wide, tips on Ø21.8, first on +y, 1.0 lead-in | **provisional: the one fit parameter, set by the bearing coupon** |
| Lip | `PB_LIP_THICKNESS`, `PB_LIP_HOLE_DIA` | 1.5 thick, Ø16.0 hole: bears on the outer ring only | provisional |
| Fixing | `PB_BOLT_X`, `PB_BOLT_Z` | two M4 heat-set inserts (the shaft set's type) up from the underside at x = ±14, z = ±40.25; M4 × 16 up through Ø5.0 plate holes, which give ±0.5 of alignment float | provisional |
| Spacer tube | `SPACER_BORE` × `_OD` × `_LENGTH` | 8.3 × 11.0 × 16.8, z = ±29.7 .. ±46.5 | provisional / derived |
| Axial end play | `SHAFT_END_PLAY` | 0.4 total, 0.2 each side at nominal | provisional |
| Print orientation, block | | lip face down, pocket opening up; no support; insert pockets horizontal | fixed |

The **bearing coupon** is a 150 × 40 × 8.5 bar with five pockets cut by the
same code as the block at rib tips 21.6 .. 22.0, labelled, printed lip down
like the block. It is test B1 (§11).

Bought per machine: 4 (buy 6) × 608ZZ, 8 × M4 heat-set inserts, 8 × M4 × 16
socket-head screws, 8 × M4 washers.

**Space taken:** on each end plate, z = ±34 .. ±55 and t = ±22 about the
shaft, up to offset +15.0 (the boss top); the foot fills the plate's width
along the run to within 0.5 each end. Below the plate, the M4 heads at
z = ±40.25. The tail pair moves with the take-up.

### 6.2 Drive

The head shaft is driven directly, no reduction. Everything here is on the
frame and ignores the take-up; `DRIVE_SIDE` (+1 = +z) is **open**, and the
`drive` and `drivetrain` groups take `drive_side`, so every check builds
both sides.

| Parameter | Value | |
|---|---|---|
| Motor | NEMA 17, 42.3 square × 40 body, 200 steps, 0.449 N m holding at 1.7 A; 5.0 D-shaft 23.5 from the mounting face | catalogue |
| Driver | A4988, 16 microsteps, current limited to 1.2 A: 1600 steps/s at 30 rpm | provisional (test D3, D5) |
| Torque | 0.254 N m available against 0.153 estimated (8 N of belt pull), 1.66 × margin; the motor skips at about 13.3 N of pull, **meant to protect the slats** (test D4) | derived |
| Coupler | 5 × 8 flexible, Ø20 × 25, bored 11 deep each end; 10.5 of head shaft and 10.0 of motor shaft in it, 4.5 between the tips | catalogue / derived |
| Stack along z, drive side | block outboard face 55.0, 2.0 gap, coupler 57.0 .. 82.0, motor face 95.5, motor back 135.5 (inside the frame's 137) | derived |
| Motor bracket | printed, on the head bridge plate, 45 × 72 × 66, 30.5 cm³; face plate 5.0 thick at z = 90.5 .. 95.5 with a 22.4 pilot bore and 4 × M3; foot 6.0 to the plate edge, on the plate's two drive-side M5 (now M5 × 20); prints foot down | provisional |
| Mass | 0.37 kg at the head shaft, in the prop force (§7.3) | estimate |

**Space taken:** on the drive side of the head plate, z = 71 .. 137 (the
bracket's foot) and z = 55 .. 135.5 along the shaft axis, up to 24 above it
(the face plate's top) and the motor's 42.3 square round it.

---

## 7. Tilt: hinge, cross-member, prop

Everything here is **modelled and checked; nothing is printed**. There are no
bearings: every pivot is an M8 bolt in a printed hole. Printed parts are
PETG like the rest.

### 7.1 Hinge

| Parameter | Name | Value | |
|---|---|---|---|
| Hinge axis, along the run / offset | `HINGE_T` / `HINGE_OFFSET` | -50.0 / -67.0 (rail centreline), 10 in from the frame's tail end | provisional / fixed |
| Hinge axis above the base top face | `HINGE_HEIGHT` | 20.0 | provisional |
| **Hinge bracket** (printed, mirror pair) | | plate on each rail's **outer face**, t = -60 .. -20, rail's full height, 10.0 thick (z = ±137 .. ±147); boss R 12.0 round the axis; 2 × M5 into the rail's outer slot at t = -35, -25 | provisional |
| Hinge pin | | M8 × 45 hex bolt, head trapped in a hex pocket between bracket and rail, shank outboard | fixed |
| **Hinge block** (printed, mirror pair) | | upright on the base, 1.0 gap to the bracket, 20.0 thick (z = ±148 .. ±168), 30.0 wide, 8.4 running-fit bushing; foot flange 60 × 20 × 5 outboard; washer and nylock outboard, snug | provisional |
| Hinge block base fixing | | 4 × 5.0 through-holes; fastener **open** | open |

**Space taken at the tail:** the rails' outer faces from t = -60 to -20, and
everything outboard of them down to the base, out to z = ±168 plus the nut.

### 7.2 Cross-member and frame clevis

| Parameter | Name | Value | |
|---|---|---|---|
| Cross-member | `XMEMBER_LEN`, `XMEMBER_T` | 2020, cut 234 long, between the rails, flush with them (offset -77 .. -57), t = 211 .. 231; 4 corner brackets on its underside | provisional position |
| Clearance to the plates at 177 and 265.5 | | 11.5 along the run (≥ 5.0 asserted) | derived |
| Clearance to the returning cleat tips | | its top face 22.05 below them (≥ 15.0 asserted) | derived |
| **Frame clevis** (printed) | | under the cross-member at z = 0, carries **pin A** at t = 221.0, offset -87.0 (10 below the rail underside); cheeks 6.0 thick, 12.6 apart, 8.2 hole; 100 wide across z; 2 × M5 at z = ±42 into the cross-member's bottom slot | provisional |

The clevis flange is open on the tail side of pin A, where the prop swings,
and the cheeks hang from a wall on the head side. The prop's load is carried
by the cheeks' top faces straight into the cross-member; the M5 only locate.

### 7.3 Prop

```
pin A (frame clevis, t = 221, offset -87)
  prop body    printed, Ø18, 92 from pin A to its bottom face; M8 nut captured 8 above that face; 9.0 rod bore above
  lock nut     run up against the body bottom to lock the setting
  M8 rod       128 long; turns in the body's nut, does not slide in the foot
  jam nut
  knob         printed, Ø40 × 12, 8 finger scallops, captured M8 nut, on a washer on the foot's top wall
  foot         printed swivel, 28 from pin B to its top face; two nuts jammed on the rod in a pocket under the 5.0 wall
pin B (base pin block, bx = 140, by = 15)
```

The prop is in compression. Its thrust goes rod → knob → washer → foot top
wall. The body does not turn (it is pinned at the top). The foot has a 14 wide
side window, facing up and tailward, to fit and jam its two nuts. The **base
pin block** is printed: cheeks 12.6 apart, solid below pin B, on a 70 × 50 × 5
plate with 4 × 5.0 holes, fastener **open**. The prop leaves pin A 17 .. 27°
below the run, on the clevis's open side.

`geometry.py` gives `prop_pin_a(incline)`, `prop_pin_b(incline)`,
`prop_length(incline)` (pin to pin), its inverse `incline_for_length(L)`,
`prop_turns`, `prop_lean`, `prop_exposed_rod` and `prop_force`.

| Incline | Prop length, pin to pin | Exposed rod (lock nut to jam nut) | Turns from 25° | Lean from vertical | Prop force, frame and drive | With the hopper (full) and skirts |
|---|---|---|---|---|---|---|
| 25° | 152.6 | 6.0 | 0 | 48.4° | 95 N | 112 N |
| 30° | 161.7 | 15.1 | 7.2 | | 79 N | 91 N |
| 35° | 171.7 | 25.1 | 15.3 | | 67 N | 74 N |
| 40° | 182.6 | 36.0 | 24.0 | 26.1° | 58 N | 61 N |
| 45° | 194.0 | 47.4 | 33.1 | | 50 N | 50 N |
| 50° | 205.8 | 59.2 | 42.5 | | 43 N | 41 N |
| 55° | 217.9 | 71.3 | 52.2 | 8.4° | 37 N | 32 N |

`checks.py` prints this every 2.5°; the exposed-rod column is what gets
measured with calipers to set an angle on the real machine. Prop length is
strictly increasing over the range.

**Length budget** (asserted in `params.py`, margins at the current values):
rod still 2.0 into the captured nut at 55° (2.1 spare); rod tip 12.0 clear of
pin A at 25° (2.6 spare); the stack on the foot (washer, knob, jam nut, 3.0,
lock nut = 29.6) clear of the body at 25° (3.0 spare). The rod must be cut to
125.9 .. 130.6. The screw prop's stroke can be at most its body less 22, and
its shortest length must leave 57.6 under the body; with pin B much past 145
the two cannot both hold, and moving it further needs a new prop design.

**Loads.** The prop force is the moment of the loads about the hinge divided
by the prop's lever arm (97 at 25°, was 81 with pin B at 125).
`prop_force(incline, loads)` takes a list of (mass, t, offset); its default
is the frame and the drive:

| Load | Mass | At (t, offset) | |
|---|---|---|---|
| Frame | 3.47 kg (`TILT_WEIGHT_N` = 34 N) | (220, -40) | **estimate**, until the frame is weighed |
| Drive | 0.37 kg | (354, 0), the head shaft | estimate |
| Hopper, rail A, its station, brushes, hardware | 0.956 kg | (79.6, 61.6), from the solids | PETG solid, 0.60 g/cm³ plywood |
| LEGO, level fill | 0.94 .. 1.20 kg (0.50 kg/L) | its centroid at each angle (§8) | provisional density |
| Skirts, rail B, two stations, uprights, hardware | 0.315 kg | (229.0, 4.7), from the solids | PETG solid, 0.60 g/cm³ plywood |

The worst case is 25°. The ceiling `PROP_FORCE_MAX` is 250 N, and every
load doubled must pass it: **224.2 N** with a full hopper and the skirts
(209.7 N without the skirts, 189.3 N for the frame and drive alone), so
**25.8 N of margin**. The prop stays in compression at every angle, empty
or full: least 32 N, at 55° full (≥ 10 asserted). **Any mass a later
spec hangs on the frame ahead of the hinge eats that margin** and must be
added to the loads.

### 7.4 The base and hardware

The base is **open**: a board, an extrusion frame, or the bench. In the CAD
it is `base_ref`, a placeholder slab for clearance checks only (top face =
the base plane, 20 thick, from 120 behind the hinge axis to 600 ahead, z =
±200), never exported. Everything that tilts clears it by ≥ 4.0 at every angle
and take-up; the closest point is the frame's tail corner, about 6 above it.

Bought: 4 × M8 × 45 hex bolts (2 hinge, pins A and B), 4 nylocks, 5 washers,
6 hex nuts, 128 of M8 rod, 6 × M5 × 12 + T-nuts, 4 × 2020 corner brackets
with M5 × 10 + T-nuts, 234 of 2020. Base fasteners (12) are open.

**Out of scope, but keep possible:** a motorised prop, a bought linear
actuator between the same pins A and B. `PROP_PIN_B_X` and `XMEMBER_T` are
parameters behind the length budget so they can move to suit one. An angle
scale is not planned; the table above replaces it.

---

## 8. The hopper

Specified in `docs/specs/hopper-spec-v1.md`, built in CAD, nothing printed.
**On the frame**: it tilts with the conveyor and is placed with
`at(..., incline)`, never with `base_frame()`. None of it is on the tail
plate, so the take-up does not move it, and nothing of it is tailward of
t = 10 (`HOPPER_TAIL_KEEPOUT_T`): the tail arc, tail plate, take-up and the
tail grub screws are untouched.

Heights in the hopper are **h, above the slat top face** (offset 22.947):
`geometry.hopper_offset(h)` turns one into an offset.

| Item | Value | |
|---|---|---|
| Extent along the run | back wall at t = 19.6 (h = 0) leaning to 36.1 at the rim; front wall inner face t = 130, outer 136 | provisional |
| Channel | the liners' lower walls, z = ±38 (`SKIRT_INSET`), from h = 1.5 (`SKIRT_GAP`) to 28 (`SKIRT_HEIGHT`): **the first section of side skirt**, continued by the skirts (§9); cleat to liner 1.5, 0.79 at worst-case play | provisional, inherited by name |
| Flare | 45° from the run normal out to the side panels at z = ±108; 50.1° from horizontal at 25°, 66.1° at 55° | provisional |
| Back wall | 85° to the run (55° from horizontal at 40°, 40° at 55°), through the seal brush's root line | provisional |
| Rim | horizontal at 40°: h = 110 at the front wall, 188.8 at the back | provisional |
| Seal brush | strip brush, tips at t = 28, 2.0 below the slat top, raked 15° headward; root 10.15 above the cleat tips | provisional |
| Metering brush | tips 14.0 above the slat top (cleats pass 2.0 under), slotted clamp 6 .. 26 | provisional |
| Carry rail A | t = 30 .. 176.75, the guide wheel's rim zone and groove run straight (same code), lands 0.5 under the slats; joint with rail B on the station at 177 (§9) | provisional |
| Station at 88.5 | the split station of §9: two posts at z = ±44 .. ±54 bolted through the plate, an arm between the runs at offset -12 .. +4, t = 76.5 .. 100.5; replaced the one-piece rail bridge | provisional |
| Feet | 4, printed, on the rail top faces at t = 46 and 126, z = ±105 .. ±137, each holding a side panel's bottom edge in a slot, M5 into the rail's top slot | provisional |
| Capacity, level fill | 2.04 L at 25°, 2.40 at 40°, 1.87 at 55° | derived |
| Mass | 0.956 kg with rail A, its station, brushes and hardware | derived |

**Space taken:** on the frame from t = 12 to 140; up to the rim, 250 .. 310
above the base; across to z = ±117 above the rail tops, and the feet to
z = ±137 on them; inside the loop, the station's arm at 88.5 between the
runs.

Bought: two strip brushes (nylon door sweep, cut to 75), M5 × 12 + T-nuts,
M4 and M3 screws, inserts and grubs (`assembly.py --report`). Plywood: two
side panels (9), back and front walls (6), on the cut list.

---

## 9. Side skirts, carry rails and support stations

Specified in `docs/specs/spec-skirts.md`, built in CAD, nothing printed or
cut. **On the frame**, placed with `at(..., incline)`; none of it is on the
tail plate. The `skirts` group holds rail B, the stations at 177 and 265.5
with their uprights, and both skirts; rail A and the station at 88.5 are
the `hopper` group's.

| Item | Value | |
|---|---|---|
| Skirts | 6 ply strips, 214 × 26.5, t = 136 .. 350; inner face z = ±38 (`SKIRT_INSET`), h = 1.5 (`SKIRT_GAP`) to 28 (`SKIRT_HEIGHT`), so they continue the hopper's channel exactly; outer face at z = ±44; 0.5 chamfer on the inner bottom edge | provisional |
| Skirt fixing | 2 × M4 countersunk per upright, heads flush in the channel face, at h = 7 and 21, nylocks outboard | provisional |
| Slat end under the skirt | 2.0 nominal, **1.29** at worst-case play (slat ends z = ±39.29 .. ±40.71) | derived |
| Cleat end to skirt or liner | 1.5 nominal, **0.79** at worst-case play | derived |
| Skirt head end | t = 350: slats rounding the head pass 0.53 under it | provisional |
| Rail A / rail B | t = 30 .. 176.75 / 177.25 .. 330, 0.5 joint gap on the station at 177; free ends lead in at 45°, joint ends a 0.5 relief | provisional |
| Rail fixing | M3 heat-set inserts in the rails' +z side face at 6 either side of each station (rail A 82.5, 94.5, 171; rail B 183, 259.5, 271.5); M3 × 8 through the arm's cheek | provisional |
| Rail B to the head guide wheel | 4.9 (≥ 3.0 asserted) | derived |
| Stations | on the plates at 88.5, 177, 265.5. **Posts**, 6: z = ±44 .. ±54, plate top to offset -12, pads to ±64 through-bolted 2 × M4; 2 × M3 inserts in each post top. **Arms**, 3: offset -12 .. +4, t ±12, z ±54, with two cheeks 2.5 thick at z = ±8.2 .. ±10.7 up to offset 12, 0.2 off the rail sides | provisional |
| Skirt uprights | 4, at 177 and 265.5: z = ±44 .. ±54 on the arm ends, offset 4 to 50.95; one M3 × 60 each side clamps upright, arm and post | provisional |
| Returning run | posts and arms ≥ 3.0 from every returning slat, cleat and belt; the arms' underside 3.95 above the returning lug tips | derived |
| Mass | 0.315 kg at (229.0, 4.7), in the prop force (§7.3) | derived |

**Fitting, with the belt on** (spec-skirts §5.2). Posts on the plates; belt
on and tensioned; each arm slid in sideways between the runs onto its posts
(at 88.5 with the hopper's +z side panel, its liner and feet off); rail A
lowered between the belts 3.0 headward of its place, with the metering
clamp off and the slats over it unclipped, then slid back under the seal
clamp, which reaches t = 32.3; rail B straight down; slats back, against
the teeth; uprights; skirts. A one-piece bridge is a ring the belt loop
passes through, so it can only go in with the belt off.

**Space taken:** above the slats, z = ±38 .. ±54 from t = 136 to 350 up to
h = 28 (the skirts and uprights); inside the loop, the rails at |z| ≤ 10.7
from t = 30 to 330 and the arms at the three stations; on the plates at
88.5, 177 and 265.5, z = ±44 .. ±64. Nothing of it reaches the head plate,
the pillow blocks or the drive (≥ 3.0, both drive sides).

Bought: M4 and M3 screws, inserts and nylocks (`assembly.py --report`,
`SKIRTS_HARDWARE`). Plywood: the two skirt strips, on the cut list.

---

## 10. What is known about the parts still to be specified

### 10.1 Discharge

The discharge at the head end moves with the angle: the carrying surface
over the head shaft is at (bx, by) = (328, 272) at 25° and (158, 403) at
55°. Whatever takes the parts from the elevator (a chute, the next stage of
the sorter) has to accept a discharge point that moves 170 horizontally and
130 vertically, or the tilt range has to be narrowed. On the drive side the
motor stands out to z = 135.5 at the head shaft (§6.2).

---

## 11. Physical tests still to be done, in order

Nothing in the CAD checks can tell whether the model matches the real belt
and the real printer. These can, and each gates the next.

| # | Test | Settles |
|---|---|---|
| 1 | Measure the belt: thickness at several points, width | `BELT_THICKNESS` (2.4 or 2.44), `BELT_WIDTH` |
| 2 | Ring coupon: caliper across opposite lands, then wrap real belt 180° round it | `PULLEY_OD_COMP`, then `PULLEY_GROOVE_COMP` |
| 3 | Saddle fit: one plain slat on real belt; caliper the slat's printed width | `SADDLE_TAB_DEPTH`, `SADDLE_INTERFERENCE`, `SLAT_WIDTH` |
| 4 | Guide coupon with that slat: lug enters from a 1 mm offset and re-centres | lug and groove parameters, `GUIDE_WIDTH` |
| 5 | First shaft set | `DRUM_DIA`, `PULLEY_SKIRT_R`, `GRUB_Z`, `PULLEY_INSERT_DEPTH` |
| 6 | Assembly: slide each shaft set until both spacers are snug, back off to ~0.2 end play, tighten the grubs (no collars); tension until a finger press at mid-span deflects the belt about 5 mm | `TAIL_TAKEUP_MIN` / `_MAX`, `SHAFT_END_PLAY` |
| 7 | Creep test: mark slats against belt teeth, run 1000 revolutions (~35 min), check drift | whether friction alone holds the slats |

If slats creep, the named fallback is a printed pin through a hole punched in
the belt's land, one per slat end. It is not to be built unless test 7 fails.
At assembly, each slat is placed **against the belt teeth** (centred on every
sixth land), never spaced from its neighbour, or print-width error
accumulates round the loop.

Also still to be done, independent of the above:

- Pillow blocks, **independent of the belt, so they can run first**:

  | # | Test | Settles |
  |---|---|---|
  | B1 | Bearing coupon: press a bearing into each pocket, loosest first (vise, M12 washer on the outer ring only); pick the tightest pocket where it seats flat on the lip, stays in inverted and spins as freely as new | `PB_RIB_TIP_DIA` |
  | B2 | That bearing, pressed in, spins freely with the lip face flat on a table (lip bears on the outer ring only) | `PB_LIP_HOLE_DIA` |
  | B3 | First block, insert fitted, bolted to scrap 9 plywood; push the shaft sideways and axially by hand | `PB_FOOT_*`, `PB_BOSS_RADIUS` |
  | B4 | After the first week of running (with test 7): no outer ring turning in its pocket; if one does, epoxy at the pocket mouth | whether the PETG press fit holds |
- Drive (spec-drive §9): **D1** measure the pillow block, motor and coupler;
  **D2** print the bracket, fit motor and coupler, turn by hand; **D3** 60 min
  at 30 rpm, case under 60 °C; **D4** the motor must skip before a held cleat
  moves on the belt; **D5** find the current that runs a full hopper.
  `DRIVE_SIDE` is chosen with the base and the discharge.
- Hopper (hopper-spec §11), after test 7. **Measure the strip brush before
  printing either clamp.** **H1** feeler-gauge the liners' 1.5 over the
  slats; **H2** lugs into and out of the carry rail with no catch, slats
  landing on it under load; **H3** 10 min with 1 L of parts at 25, 40, 55,
  nothing past the seal, creep marks rechecked; **H4** parts per minute and
  jams through the metering brush with the largest screened parts; **H5** a
  2 L bucket dumped at each angle, nothing spills; **H6** weigh the hopper
  empty and with 2 L; **H7** the thinnest parts, nothing under the liners or
  wedged at the seal.
- Skirts (spec-skirts §11), after H2: **S1** slide the arms in and drop
  both rails in with the belt tensioned; **S2** lugs across the joint at
  177 with no click; **S3** press rail B's span, slats land on it and lift
  clear; **S4** feeler-gauge the 1.5 under the skirts and the cleat ends
  (1.5, 0.79 least); **S5** 1 L for 10 min at three angles, nothing over,
  under or wedged, and H7's thin parts again; **S6** weigh the parts, rerun
  the prop force.
- Weigh the assembled frame and find its balance point along the run:
  `TILT_WEIGHT_N`, `TILT_CG_T`, `TILT_CG_OFFSET`, and a level litre of mixed
  parts (`LOAD_BULK_DENSITY`). Until then the prop force is an estimate, and
  its 26 N of margin at 25° is only as good as these.
- Tilt fit: hinge pin running free in the printed bushing, prop eyes in their
  clevises, knob turning the rod under load. All are provisional printed
  clearances (8.4 bushing, 12.6 clevis gaps, 8.2 pin holes).

---

## 12. The CAD project a specification has to fit

Python, [build123d](https://github.com/gumyr/build123d) 0.11 (OpenCascade),
at the repo root. Layers, each importing only from the ones above it in this
table:

| Layer | Holds | Returns |
|---|---|---|
| `params.py` | every dimension, plus assertions tying them together | numbers |
| `geometry.py` | datums and placement: run direction, shaft axes, `at(t, offset, lateral, incline)`, `loop_at(s, takeup, incline)`, `tail_shaft_t(takeup)`, the radial stations of §2.3 as functions, `is_cleated(i)`, plate and frame datums; for the tilt `hinge_axis`, `base_frame`, `base_z`, `height_above_base` and the prop functions of §7.3, with `machine_loads()` for the force; for the hopper `hopper_offset(h)`, `rim_h`, the back wall plane, the wall slopes and `run_coords`; `slat_lateral_play()` | numbers, transforms; never a solid |
| `profile.py` | the belt tooth and the standard pulley groove; `pulley_section()` is the only thing that makes teeth | 2D edges and faces; never a solid |
| `parts/*.py` | one module per part: `slat`, `shaft_set`, `shaft`, `belt`, `coupons`, `frame` (with the cut `cross_member`), `bridge_plate`, `hinge`, `prop`, `hardware` (bought M8 parts), `base_ref`, `pillow_block`, `bearing`, `spacer`, `motor`, `coupler`, `motor_bracket`, `hopper` (its printed and plywood parts and the cavity), `carry_rail` (both rails), `brush`, `station` (post, arm, skirt upright), `skirt` | a solid in its own local frame; never a machine position |
| `assembly.py` | named groups of positioned parts: `frame`, `plates`, `drivetrain`, `belts`, `slats`, `tilt`, `pillow_blocks`, `bearings`, `spacers`, `drive`, `hopper`, `skirts`; every group takes `takeup` and `incline` | positioned compounds |

Rules a new part specification should respect:

1. **No numeric dimension outside `params.py`.** A spec should give a
   parameter table with names, values and units, and say which values are
   derived and from what.
2. **State the local frame and origin** of each part, with the origin on its
   mating surface.
3. **Radial clearances are asserted against the named stations** of §2.3
   (`belt_back_radius()`, `cleat_tip_radius()`, ...), never against literals.
   A literal is how v1's 1.171 error went unnoticed.
4. **Give acceptance criteria as checkable assertions with numbers**:
   bounding boxes, volume ranges, points that must be inside or outside the
   solid, pairs of solids that must not intersect, validity of the solid.
   Each one is implemented twice, in `checks.py` (pass/fail report) and as a
   pytest test. Currently 81 checks and 467 tests, all passing.
5. **A negative control must be able to fail.** One drivetrain check asked
   that a zero-clearance guide groove collide with the lug; a straight lug
   only *touches* a revolved groove of its own section, sharing no volume, so
   the control had to be redesigned. Prefer controls with real interference.
6. **Anything near the tail must be checked across the take-up range**, not
   only at nominal. Every assembly group accepts a `takeup` argument for this.
7. **Anything that could meet the base, the prop or a base-fixed part must be
   checked across the tilt range**, at 25°, 40° and 55°
   (`TILT_CHECK_ANGLES`), combined with the three take-ups where the tail is
   involved. Every assembly group accepts an `incline` argument.
8. **Say which frame each part belongs to.** Parts on the frame are placed
   with `at(..., incline=incline)`; parts on the base with
   `base_frame(incline)`, never rotated. Never move the machine origin.
9. **Say how each part leaves the project**: printed parts are exported as
   STL in a stated print orientation (so far: both slats, the shaft set,
   three coupons, nine tilt parts, the pillow block, the spacer, the motor
   bracket, eight hopper parts and four skirts parts), and must fit `PRINT_BED`, a Bambu Lab
   P1S, 256 × 256 × 256; bought or cut parts are reference solids only;
   plywood and cut metal (the cross-member, the M8 rod, the shafts, the
   hopper's boards, the skirt strips) go on the cut list; bought hardware is listed by
   `assembly.py --report`.
10. Adding a part to the machine is one group function in `assembly.py`, one
   entry in its group table and one colour. If a part needs more than that,
   say so in the spec.

Helpers already available for checks: bounding-box size, volume in cm³,
point-in-solid, minimum distance between solids (with a bounding-box
short-cut, `min_distance`, for sweeps), and solid-solid clash with a volume
tolerance; `level_fill()` for what a cavity holds at an incline and
`mass_properties()` for a mass and centre of gravity from solids and
densities. A whole-loop sweep (every real slat against every fixed part, at
three take-ups × three inclines, nine cases) already exists and new fixed
parts should be added to it. `geometry.slat_lateral_play()` (0.707) is the
slats' sideways play, for distance checks at worst case. A distance between
two things that both ride the frame does not depend on the incline, so such
sweeps can run with the run along x (incline 0), where bounding boxes are
tight. `checks.py` takes about four minutes, most of it the sweep. Moving a
real slat copies it and is slow; shift the other part instead.

---

## 13. Open questions for the next specifications

1. ~~Skirts.~~ **Built** (§9): the hopper's inset, gap and height carried
   on to t = 350, the cleats shortened to 73 for 0.79 at worst-case play.
   How they meet the discharge is part of Q10.
2. ~~Lateral support on the carrying run.~~ **Closed**: the carry rails'
   groove from t = 30 to 330 (§9).
3. ~~Belt support.~~ **Closed**: the rails' lands, 0.5 under the slats,
   over the same span (§9). Physical tests S2, S3 confirm it.
4. ~~Pillow blocks and standoffs.~~ **Closed**: printed blocks, shaft
   height fixed at 48.0 (§6.1).
5. **Take-up mechanism.** A jacking screw for the tail plate within the
   -4.0 .. +2.0 travel: where its block bolts to the frame, how the plate is
   locked once set, and how the two sides are kept square so the tail shaft
   stays parallel to the head shaft. It must stay out of the hinge's space
   (§7.1).
6. ~~Axial location of the shaft sets.~~ **Closed**: spacer tubes to the
   bearings' inner rings, lips outboard, 0.4 end play (§6.1).
7. ~~Drive.~~ **Built** (§6.2). `DRIVE_SIDE` is still open; choose it with
   the base and the discharge.
8. ~~Hopper.~~ **Built** (§8), frame-mounted, on the straight run clear of
   the tail. What remains is physical: the brush, the bulk density, and
   tests H1 .. H7.
9. **Pinch at the head.** Slat tops open to 5.7 going over the head pulley
   and close again onto the return run. Whether a part can be carried into
   that gap and pinched, and whether discharge needs a stripper or brush.
10. **Discharge.** Where the parts go from the head end, given that the
    discharge point moves 170 × 130 over the tilt range (§10.1). Whether that
    argues for a narrower range.
11. **The base.** What the machine stands on (board, extrusion frame, bench),
    its footprint (the hinge blocks stand at z = ±148 .. ±168, the frame's
    head end reaches 495 ahead of the hinge at 25°), and how the two hinge
    blocks and the pin block fasten to it: 12 × 5.0 holes, fastener open.
12. **Tilt range.** 25° .. 55° is provisional. Narrowing it shortens the
    prop's travel, lowers the worst-case force (at 25°) and shrinks the
    discharge and tail movement. What incline the sorter actually needs is
    not known yet.
13. **Prop margin.** 26 N under the 250 N ceiling at 25°, doubled, on
    estimated masses. Anything added ahead of the hinge spends it; beyond
    pin B at about 145 the screw prop cannot follow, so a bigger need means a
    new prop design, a stronger printed eye (a higher ceiling) or a higher
    `TILT_MIN`.
