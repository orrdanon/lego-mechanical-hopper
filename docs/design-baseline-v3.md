# Feed elevator: design baseline, v3

Status as of 2026-09-26, commit `ca50e1a`. All dimensions are millimetres and
degrees.

This document describes what has been built and decided so far, so that
specifications for the **remaining parts of the machine** can be written
against it: side skirts and their posts, pillow-block standoffs, the tail
take-up, the motor mount and coupler, the hopper, the discharge and the base.
It is self-contained: it replaces `design-baseline-v2.md` (and v1) and the
specification files as the reference for new work. Where a number here and
an older document disagree, this document (and `params.py`, which it is taken
from) is correct.

**What changed since v2.** v2 was the input to the tilt specification. That
work is now built in CAD. Nothing on the conveyor moved (every v2 number in
§2 to §6 still holds at 40°), but four things are new:

1. **The incline is adjustable, 25° .. 55°**, by hand. 40° is now the
   nominal setting, not a fixed value. Every datum that depends on the incline
   is a function of it (§2).
2. **The frame hinges** at its bottom tail corner on an axis 20 above a
   **base**, and a screw **prop** under the machine centreline holds it up
   (§7). The base itself is still **open**.
3. **There is a second coordinate frame, the base frame**, for anything that
   stands on the base and therefore does not tilt (§2.4). New parts must say
   which of the two they belong to.
4. **Space is now taken** under the frame (a 2020 cross-member at t = 211 ..
   231, the prop) and at the tail end, outboard of the rails (the hinge). §8
   lists what that means for each part still to be specified.

Every value is labelled one of:

- **fixed** - decided and implemented; changing it invalidates built and tested geometry
- **catalogue** - a published figure for a bought part, not yet measured on the real one
- **provisional** - a starting guess, expected to be tuned; §9 says what settles each
- **open** - not decided; input wanted

**Nothing has been printed or physically tested yet.** Everything below is
CAD that passes its own checks. §9 lists the physical tests, in order, that
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
- Each 8 mm shaft runs in two pillow-block bearings bolted to a plywood
  bridge plate, which bolts to the top of an aluminium 2020 extrusion frame.
  The whole frame is inclined with the run.
- The frame **hinges** on two M8 bolts near its bottom tail corner, in
  printed blocks on the base. A single **screw prop** between a cross-member
  under the frame and a block on the base sets the angle: turning a knob
  changes its length, about 45 turns over the whole range, and a lock nut
  holds the setting.
- The **tail bridge plate slides** along the frame's T-slots. That is the
  belt take-up. The mechanism that pushes it has not been designed.
- The head shaft is driven; target 30 rpm, which gives 60 mm/s belt speed.

| Item | Status |
|---|---|
| Slat, plain and cleated, with guide lug | modelled, checked, STL exported; not yet printed |
| Tooth profile: belt tooth and standard pulley groove | built; groove verified against a manufacturer's model |
| Shaft set (2 pulleys + guide wheel), two off | modelled, checked, STL exported; not yet printed |
| Shafts, belts | modelled as reference solids (bought parts) |
| Calibration coupons, two | modelled, STL exported; not yet printed |
| 2020 frame | modelled as a reference solid (owned hardware) |
| Bridge plates, five | modelled as reference solids with frame bolt holes; cut list generated |
| Tilt: hinge brackets and blocks (2 mirror pairs), frame clevis, prop body, foot, knob, base pin block | modelled, checked, STL exported; not yet printed |
| Tilt: cross-member (2020, cut), M8 rod | reference solids; on the cut list |
| Tilt: M8 bolts, nuts, washers | reference solids; listed by `assembly.py --report` |
| Assembly | frame, plates, drivetrain, belts, all 46 slats round the whole loop, and the tilt, at any incline |
| **Base** | **open; a placeholder slab for clearance checks only** |
| **Pillow blocks and their standoffs** | **not modelled; blocks not yet measured** |
| **Tail take-up mechanism (jacking screw)** | **travel decided and clash-checked; mechanism not designed** |
| **Side skirts and skirt posts** | **specified once (phase 2) against superseded numbers; not built; needs re-specifying, see §8** |
| **Motor mount, coupler** | **not designed** |
| **Hopper, brush mounts, discharge** | **not designed** |

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
| Bridge plate top faces (pillow blocks mount here) | -48.0 | provisional, see §6 |
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
Bridge plate: centre of its top face.

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
| Prop pin B (base-fixed) | (125.0, 15.0) | (125.0, 15.0) | (125.0, 15.0) |

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
until the saddle and guide fits in §9 pass; but nothing new should be
specified that requires changing it.

### 4.1 Body and cleat

| | Value | |
|---|---|---|
| Slat pitch along the belt | 18.0 = 6 belt teeth; 46 slats round the loop | fixed |
| Slat body | 17.0 along the run × 3.0 thick × 80.0 across the machine | width provisional |
| Gap between adjacent slats on a straight run | 1.0 | provisional, follows the width |
| Gap between adjacent slats round a pulley | opens to 2.96 at the bottom corners, 5.7 at the top faces | derived |
| Cleat | every 2nd slat; 12.0 high, 10.0 wide at the root tapering to 4.0 at the tip, 74.0 long, 1.0 root fillets | height provisional |
| Edge chamfer | 0.5 | fixed |
| Bounding box, plain / cleated | 17 × 7 × 80 / 17 × 19 × 80 | derived |
| Volume, plain / cleated | 4.54 / 10.76 cm³ | derived |
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

The lug is engaged only while a slat is on a pulley, about three slats per
shaft at any moment. **Along the straight runs nothing constrains the slats
laterally except the belts' own stiffness.** Whether the carrying run needs
more than that is untested, and is a question for the skirt work (§8).

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

Both grubs bear on the one flat. They carry the torque and set the shaft
set's axial position; there is no shoulder, collar or circlip. **Both shaft
sets must sit at the same z**, because the two guide grooves define where
every slat runs; this is set by caliper from the pillow blocks at assembly.

### 5.4 Calibration coupons

Two small printed parts, made by the same code as the shaft set so that they
calibrate it: a **ring coupon** (the real 40-groove outline, 3.0 thick, 8.15
bore) and a **guide coupon** (the guide wheel zone alone, 16.0 thick).

---

## 6. Shafts, bearings and structure

| Parameter | Value | |
|---|---|---|
| Incline | 25° .. 55° from horizontal, set by hand; 40° nominal (§7) | range provisional |
| Shaft | 8.0 dia × 145.0 long, two off, with the flat of §5.3 | fixed |
| Pillow-block bearing centres | 100.0 (z = ±50) | fixed |
| Shaft axis above the bridge plate top face | 48.0 | **provisional** - depends on the pillow blocks actually bought and a standoff not yet designed |
| Shaft speed | 30 rpm → 60 mm/s | fixed target |
| Frame | 2020 extrusion rectangle, 552 long × 274 wide overall, 234 between rails | fixed, owned, uncut |
| Frame position along the run | from t = -60 to t = 492; 138 of frame beyond the head shaft, reserved for the motor | fixed |
| Bridge plates | five, 9 plywood, 45 along the run × 274 across, on top of both rails, M5 into T-nuts at x = ±12, z = ±127 | fixed |
| Plate stations | t = 0, 88.5, 177, 265.5, 354; the end two carry the pillow blocks, the middle three are free for skirt posts | fixed |
| Tail take-up travel | `TAIL_TAKEUP_MIN` .. `_MAX` = -4.0 (toward the head, to fit the belt) .. +2.0 (away, to tension) | provisional |

**Along each shaft, from the centre outwards:**

```
guide wheel        0 .. 8.0
shaft set body     to 29.5      (pulley face 24.5 .. 29.5)
belt               19.5 .. 34.5
outer tab          to 36.9
slat end           40.0   <- everything inside this rotates or travels
bearing centre     50.0
shaft end          72.5
```

So there is 10.0 between the slat ends and the bearing centre plane, less
half a pillow block, and 22.5 of shaft beyond each bearing centre for a
coupler. Which end of the head shaft is driven is **open**; the shaft is
symmetric.

**Take-up.** The tail bridge plate, the tail pillow blocks, the tail shaft
and its shaft set move together along the run. The assembly is built at
take-up 0 (354.0 centres). Slat, drivetrain, plate and tilt clearances have
been clash-checked at -4.0, 0 and +2.0, each at 25°, 40° and 55°. With the tail plate at -4.0 it is 39.5
clear of the next plate. What pushes the plate is **open**: a jacking screw
in a block bolted to the frame is the intent. It must stay off the rails'
outer faces from t = -60 to -20 and out of the space outboard of them: the
hinge is there (§7.1).

**Returning-run clearance.** Cleats on the returning (lower) run point at the
bridge plates. Cleat tip radius is 34.947 against a 48.0 shaft height, so
**13.05** of clearance; the check requires > 5.0. If the measured pillow
blocks bring the shaft height down, this is what it eats.

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
  prop body    printed, Ø18, 90 from pin A to its bottom face; M8 nut captured 8 above that face; 9.0 rod bore above
  lock nut     run up against the body bottom to lock the setting
  M8 rod       136 long; turns in the body's nut, does not slide in the foot
  jam nut
  knob         printed, Ø40 × 12, 8 finger scallops, captured M8 nut, on a washer on the foot's top wall
  foot         printed swivel, 28 from pin B to its top face; two nuts jammed on the rod in a pocket under the 5.0 wall
pin B (base pin block, bx = 125, by = 15)
```

The prop is in compression. Its thrust goes rod → knob → washer → foot top
wall. The body does not turn (it is pinned at the top). The foot has a 14 wide
side window, facing up and tailward, to fit and jam its two nuts. The **base
pin block** is printed: cheeks 12.6 apart, solid below pin B, on a 70 × 50 × 5
plate with 4 × 5.0 holes, fastener **open**.

`geometry.py` gives `prop_pin_a(incline)`, `prop_pin_b(incline)`,
`prop_length(incline)` (pin to pin), its inverse `incline_for_length(L)`,
`prop_turns`, `prop_lean`, `prop_exposed_rod` and `prop_force`.

| Incline | Prop length, pin to pin | Exposed rod (lock nut to jam nut) | Turns from 25° | Lean from vertical | Prop force at 34 N |
|---|---|---|---|---|---|
| 25° | 164.1 | 19.5 | 0 | 51.8° | 98 N |
| 30° | 171.8 | 27.2 | 6.1 | | |
| 35° | 180.3 | 35.7 | 13.0 | | |
| 40° | 189.6 | 45.0 | 20.4 | 30.2° | 58 N |
| 45° | 199.6 | 55.0 | 28.3 | | |
| 50° | 209.9 | 65.3 | 36.6 | | |
| 55° | 220.5 | 75.9 | 45.1 | 12.3° | 37 N |

`checks.py` prints this every 2.5°; the exposed-rod column is what gets
measured with calipers to set an angle on the real machine. Prop length is
strictly increasing over the range.

**Length budget** (asserted in `params.py`, margins at the current values):
rod still 2.0 into the captured nut at 55° (5.5 spare); rod tip 12.0 clear of
pin A at 25° (6.1 spare); the stack on the foot (washer, knob, jam nut, 3.0,
lock nut = 29.6) clear of the body at 25° (16.5 spare). Moving pin A or pin B
re-checks all three.

**Loads.** The prop force is the weight's moment about the hinge divided by
the prop's lever arm. The weight is an **estimate**: `TILT_WEIGHT_N` = 34 N at
t = 220, offset -40, until the frame is weighed. The worst case is 25°. The
ceiling `PROP_FORCE_MAX` is 250 N, and double the estimated weight must pass
too (195.5 N at 25°, about 2 MPa of M8 pin on a 12 wide printed eye). **Any
mass a later spec hangs on the frame, the motor above all, raises this and
must be added to the weight and centre of gravity.**

### 7.4 The base and hardware

The base is **open**: a board, an extrusion frame, or the bench. In the CAD
it is `base_ref`, a placeholder slab for clearance checks only (top face =
the base plane, 20 thick, from 120 behind the hinge axis to 600 ahead, z =
±200), never exported. Everything that tilts clears it by ≥ 4.0 at every angle
and take-up; the closest point is the frame's tail corner, about 6 above it.

Bought: 4 × M8 × 45 hex bolts (2 hinge, pins A and B), 4 nylocks, 5 washers,
6 hex nuts, 136 of M8 rod, 6 × M5 × 12 + T-nuts, 4 × 2020 corner brackets
with M5 × 10 + T-nuts, 234 of 2020. Base fasteners (12) are open.

**Out of scope, but keep possible:** a motorised prop, a bought linear
actuator between the same pins A and B. `PROP_PIN_B_X` and `XMEMBER_T` are
parameters behind the length budget so they can move to suit one. An angle
scale is not planned; the table above replaces it.

---

## 8. What is known about the parts still to be specified

### 8.1 Side skirts and posts

An earlier specification (phase 2) exists for plywood side skirts on posts
standing on the three middle bridge plates. **It was written before the belt
was changed, before the belt-back correction and before the guide was added,
and none of it is built.** Treat it as intent, not as numbers. What carries
over:

| Parameter | Name | Value | |
|---|---|---|---|
| Skirt height above the slat top | `SKIRT_HEIGHT` | 28.0 | provisional |
| Skirt bottom edge to slat top | `SKIRT_GAP` | 1.5 | provisional; may open to 2.0 |
| Skirt inner face from the centreline | `SKIRT_INSET` | 38.0, so each skirt overlaps the slat end by 2.0 | provisional |

What is new and must be allowed for:

- The skirts **no longer guide anything**. The V-guide does. A skirt is only
  a wall to keep LEGO on the slats.
- Slats have **±0.71 of lateral play**, so the slat ends run anywhere in
  z = ±(39.29 .. 40.71).
- The slat top is at offset **22.947**, not v1's 24.118, and the cleat tips
  at **34.947**. Cleats are 74.0 long (z = ±37), inside the 38.0 skirt inset
  by 1.0 per side, less the lateral play: **0.29 worst case.** This is tight
  and should be revisited.
- Posts must clear the **returning** run as well: slats pass under the
  shafts at offsets -19.947 to -34.947, 80 wide plus play.
- The tail bridge plate slides (§6); nothing fixed to the frame may assume
  it stays at t = 0.
- The skirts ride on the frame and tilt with it, so their geometry is the
  same at every angle. What changes with the angle is how hard LEGO presses
  on them and slides back over the cleats; the 12.0 cleat height was chosen
  with 40° in mind and is untested at 55°.
- Under the frame, the cross-member occupies t = 211 .. 231 between the
  rails and the clevis hangs below it at z = 0 (§7.2). Posts on the middle
  plates (t = 88.5, 177, 265.5) sit above the rails and do not meet either.

### 8.2 Pillow blocks and standoffs

Not modelled, deliberately, until the real blocks are measured. The numbers
that depend on them: shaft height 48.0 above the plate top (provisional),
bearing centres at z = ±50, and at least the returning-run clearance above.

The shaft height also sets where the frame is relative to the shaft axes
(the rail centreline is at offset -(48.0 + 9 + 10) = -67.0), so changing it
moves the whole conveyor relative to the frame, hinge and base. The prop's
length table does not change (pin A and the hinge are both on the frame), but
the tail shaft's height above the base does, one for one near enough, and the
check holds it to 94 .. 108 (currently 97.7 .. 106.0). The returning cleats'
clearance to the cross-member (22.05, ≥ 15.0 required) moves with it too.

### 8.3 Motor mount and coupler

Nothing decided beyond: the head shaft is driven at 30 rpm, 22.5 of shaft
projects beyond each bearing centre, and 138 of frame beyond the head shaft
is reserved. Load is light (loose LEGO on a 60 mm/s belt). Motor, reduction
and coupler are all **open**.

What the tilt adds:

- The motor rides on the frame and tilts with it through 30°. Whatever holds
  it must do so at every angle, and cable routing must allow the swing.
- It sits at the far end of the frame from the hinge, so its mass counts
  heavily against the prop: include it in `TILT_WEIGHT_N` / `TILT_CG_T` /
  `TILT_CG_OFFSET` and re-run the force check (§7.3). The ceiling is 250 N
  with the weight doubled.
- At 25° the frame's head end is 240 above the base at its underside and
  495 ahead of the hinge; at 55°, 458 up and 319 ahead (§2.4). Anything
  hanging below the frame there must clear the base at 25°, where it comes
  lowest, by the same 4.0 as everything else.

### 8.4 Hopper, brush mounts and discharge

Not designed. The hopper wraps the tail end, so it must clear the swept radii
in §2.3, let the tail assembly slide through the take-up range, and leave
the tail shaft set's grub screws reachable.

The tilt makes the first decision **which frame the hopper belongs to**:

- **On the frame**, it tilts with the conveyor; its geometry relative to the
  tail pulley is constant, but its walls change angle by 30° and it must
  still hold parts at 25° and at 55°. It must clear the base (the frame's
  tail corner is only about 6 above it) and the hinge blocks outboard.
- **On the base**, it stays level, but the tail shaft moves 43 horizontally
  and about 8 vertically under it over the tilt range and take-up (§2.4), so
  the seal against the belt has to accept that motion.

Either way, the space outboard of the rails from t = -60 to -20, down to the
base, is taken by the hinge (§7.1), and the prop stands on the base from
pin B at bx = 125 up to pin A under the frame.

The **discharge** at the head end moves with the angle: the carrying surface
over the head shaft is at (bx, by) = (328, 272) at 25° and (158, 403) at
55°. Whatever takes the parts from the elevator (a chute, the next stage of
the sorter) has to accept a discharge point that moves 170 horizontally and
130 vertically, or the tilt range has to be narrowed.

---

## 9. Physical tests still to be done, in order

Nothing in the CAD checks can tell whether the model matches the real belt
and the real printer. These can, and each gates the next.

| # | Test | Settles |
|---|---|---|
| 1 | Measure the belt: thickness at several points, width | `BELT_THICKNESS` (2.4 or 2.44), `BELT_WIDTH` |
| 2 | Ring coupon: caliper across opposite lands, then wrap real belt 180° round it | `PULLEY_OD_COMP`, then `PULLEY_GROOVE_COMP` |
| 3 | Saddle fit: one plain slat on real belt; caliper the slat's printed width | `SADDLE_TAB_DEPTH`, `SADDLE_INTERFERENCE`, `SLAT_WIDTH` |
| 4 | Guide coupon with that slat: lug enters from a 1 mm offset and re-centres | lug and groove parameters, `GUIDE_WIDTH` |
| 5 | First shaft set | `DRUM_DIA`, `PULLEY_SKIRT_R`, `GRUB_Z`, `PULLEY_INSERT_DEPTH` |
| 6 | Assembly: set both shaft sets to the same z; tension until a finger press at mid-span deflects the belt about 5 mm | `TAIL_TAKEUP_MIN` / `_MAX` |
| 7 | Creep test: mark slats against belt teeth, run 1000 revolutions (~35 min), check drift | whether friction alone holds the slats |

If slats creep, the named fallback is a printed pin through a hole punched in
the belt's land, one per slat end. It is not to be built unless test 7 fails.
At assembly, each slat is placed **against the belt teeth** (centred on every
sixth land), never spaced from its neighbour, or print-width error
accumulates round the loop.

Also still to be done, independent of the above:

- Measure the pillow-block shaft height (`SHAFT_HEIGHT_ABOVE_PLATE`).
- Weigh the assembled frame and find its balance point along the run:
  `TILT_WEIGHT_N`, `TILT_CG_T`, `TILT_CG_OFFSET`. Until then the prop force
  is an estimate.
- Tilt fit: hinge pin running free in the printed bushing, prop eyes in their
  clevises, knob turning the rod under load. All are provisional printed
  clearances (8.4 bushing, 12.6 clevis gaps, 8.2 pin holes).

---

## 10. The CAD project a specification has to fit

Python, [build123d](https://github.com/gumyr/build123d) 0.11 (OpenCascade),
at the repo root. Layers, each importing only from the ones above it in this
table:

| Layer | Holds | Returns |
|---|---|---|
| `params.py` | every dimension, plus assertions tying them together | numbers |
| `geometry.py` | datums and placement: run direction, shaft axes, `at(t, offset, lateral, incline)`, `loop_at(s, takeup, incline)`, `tail_shaft_t(takeup)`, the radial stations of §2.3 as functions, `is_cleated(i)`, plate and frame datums; for the tilt `hinge_axis`, `base_frame`, `base_z`, `height_above_base` and the prop functions of §7.3 | numbers, transforms; never a solid |
| `profile.py` | the belt tooth and the standard pulley groove; `pulley_section()` is the only thing that makes teeth | 2D edges and faces; never a solid |
| `parts/*.py` | one module per part: `slat`, `shaft_set`, `shaft`, `belt`, `coupons`, `frame` (with the cut `cross_member`), `bridge_plate`, `hinge`, `prop`, `hardware` (bought M8 parts), `base_ref` | a solid in its own local frame; never a machine position |
| `assembly.py` | named groups of positioned parts: `frame`, `plates`, `drivetrain`, `belts`, `slats`, `tilt`; every group takes `takeup` and `incline` | positioned compounds |

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
   pytest test. Currently 38 checks and 214 tests, all passing.
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
   STL in a stated print orientation (so far: both slats, the shaft set, two
   coupons, and nine tilt parts); bought or cut parts are reference solids
   only; plywood and cut metal (the cross-member, the M8 rod) go on the cut
   list; bought hardware is listed by `assembly.py --report`.
10. Adding a part to the machine is one group function in `assembly.py`, one
   entry in its group table and one colour. If a part needs more than that,
   say so in the spec.

Helpers already available for checks: bounding-box size, volume in cm³,
point-in-solid, minimum distance between solids, and solid-solid clash with a
volume tolerance. A whole-loop sweep (every real slat against every fixed
part, at three take-ups × three inclines, nine cases) already exists and new
fixed parts should be added to it. `checks.py` takes about two minutes, most
of it that sweep.

---

## 11. Open questions for the next specifications

1. **Skirts.** Given §8.1: inset, gap and height against the corrected slat
   top and the ±0.71 play; whether the 0.29 worst-case cleat-to-skirt
   clearance is acceptable or the cleat length or skirt inset should move;
   and how the skirts end at the head (discharge) and tail (hopper).
2. **Lateral support on the carrying run.** The guide acts only at the two
   pulleys, 354 apart. Is that enough under a side load from LEGO piling
   against one skirt, or does the carrying run need a mid-span guide or a
   slider bed under the belts?
3. **Belt support.** Nothing supports the carrying run between the shafts.
   With light load and 5 mm mid-span deflection at the set tension this may
   be fine; a recommendation is wanted.
4. **Pillow blocks and standoffs.** Which blocks, the resulting shaft height,
   and the standoff that sets it, keeping > 5.0 returning-run clearance, the
   cross-member clearance and the tail shaft height above the base (§8.2).
5. **Take-up mechanism.** A jacking screw for the tail plate within the
   -4.0 .. +2.0 travel: where its block bolts to the frame, how the plate is
   locked once set, and how the two sides are kept square so the tail shaft
   stays parallel to the head shaft. It must stay out of the hinge's space
   (§7.1).
6. **Axial location of the shaft sets.** Two grub screws on a flat is all
   that holds each one in z, and both must agree to keep the guide grooves
   aligned. Is a positive stop (collar, spacer tube to the bearing) wanted?
7. **Drive.** Motor, reduction, coupler and mount for 30 rpm at light load,
   on whichever end of the head shaft, within 138 of frame and 22.5 of shaft,
   working at every incline, with its mass added to the prop force (§8.3).
8. **Hopper.** Frame-mounted or base-mounted (§8.4), then geometry round the
   tail end against the swept radii of §2.3, sealing against 1.0 slat gaps
   that open to 5.7 on the tail pulley, and access to the tail grub screws
   and take-up.
9. **Pinch at the head.** Slat tops open to 5.7 going over the head pulley
   and close again onto the return run. Whether a part can be carried into
   that gap and pinched, and whether discharge needs a stripper or brush.
10. **Discharge.** Where the parts go from the head end, given that the
    discharge point moves 170 × 130 over the tilt range (§8.4). Whether that
    argues for a narrower range.
11. **The base.** What the machine stands on (board, extrusion frame, bench),
    its footprint (the hinge blocks stand at z = ±148 .. ±168, the frame's
    head end reaches 495 ahead of the hinge at 25°), and how the two hinge
    blocks and the pin block fasten to it: 12 × 5.0 holes, fastener open.
12. **Tilt range.** 25° .. 55° is provisional. Narrowing it shortens the
    prop's travel, lowers the worst-case force (at 25°) and shrinks the
    discharge and tail movement. What incline the sorter actually needs is
    not known yet.
