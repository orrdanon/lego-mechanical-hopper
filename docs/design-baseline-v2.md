# Feed elevator: design baseline, v2

Status as of 2026-09-21, commit `ad71c0e`. All dimensions are millimetres and
degrees.

This document describes what has been built and decided so far, so that
specifications for the **remaining parts of the machine** can be written
against it: side skirts and their posts, pillow-block standoffs, the tail
take-up, the motor mount and coupler, and the hopper. It is self-contained: it
replaces `design-baseline-v1.md` and the phase specification files as the
reference for new work. Where a number here and an older document disagree,
this document (and `params.py`, which it is taken from) is correct.

**What changed since v1.** v1 was the input to the drivetrain specification.
That work is now built in CAD, and it changed three things a reader of v1 must
un-learn:

1. **The belt-back radius was wrong in v1** (21.118). It is **19.947**. The
   belt's land rests on the pulley OD and its teeth sit in the grooves; v1 had
   the tooth tips on the OD. Every radial station in §2 moved inward by one
   tooth height, 1.171.
2. **There are no separate pulleys.** Each shaft carries one printed **shaft
   set**: both toothed pulleys and a central guide wheel in one part.
3. **The slat changed**: a guide lug was added, the saddle tabs are shallower
   (6.0 → 3.6), and the slat is wider (16 → 17, a 1 mm gap between slats).

Every value is labelled one of:

- **fixed** - decided and implemented; changing it invalidates built and tested geometry
- **catalogue** - a published figure for a bought part, not yet measured on the real one
- **provisional** - a starting guess, expected to be tuned; §8 says what settles each
- **open** - not decided; input wanted

**Nothing has been printed or physically tested yet.** Everything below is
CAD that passes its own checks. §8 lists the physical tests, in order, that
stand between this model and a working machine.

---

## 1. The machine

A feed elevator for a LEGO-sorting machine: a cleated slat conveyor inclined
at 40 degrees that lifts loose LEGO parts out of a hopper and drops them off
the head end.

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
| Assembly | frame, plates, drivetrain, belts and all 46 slats placed round the whole loop |
| **Pillow blocks and their standoffs** | **not modelled; blocks not yet measured** |
| **Tail take-up mechanism (jacking screw)** | **travel decided and clash-checked; mechanism not designed** |
| **Side skirts and skirt posts** | **specified once (phase 2) against superseded numbers; not built; needs re-specifying, see §7** |
| **Motor mount, coupler** | **not designed** |
| **Hopper, brush mounts** | **not designed** |

---

## 2. Coordinate system and datums

Machine frame: origin on the **tail shaft axis** at the machine centre plane.
+X horizontal towards the head end, +Y up, +Z across the machine along the
shaft axes. Both shaft axes are parallel to Z.

| Datum | Value |
|---|---|
| Run direction (unit) | (cos 40°, sin 40°, 0) |
| Run normal (unit), out of the carrying face | (-sin 40°, cos 40°, 0) |
| Tail shaft axis | (0, 0, z) at nominal take-up |
| Head shaft axis | (271.18, 227.55, z), i.e. 354.0 along the run |
| Belt centrelines | z = +27 and z = -27 |
| Guide groove centre plane | z = 0 |

### 2.1 Positions on the straight run: `at(t, offset, lateral)`

- `t` - distance along the run from the tail shaft axis
- `offset` - distance from the **shaft axis** along the run normal; positive
  is outward through the carrying run, negative is down towards the frame
- `lateral` - z

So `offset = 0` is on the shaft centreline.

### 2.2 Positions on the belt: `loop_at(s)`

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
until the saddle and guide fits in §8 pass; but nothing new should be
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
more than that is untested, and is a question for the skirt work (§7).

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
| Incline | 40° from horizontal | fixed |
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
take-up 0 (354.0 centres). Slat, drivetrain and plate clearances have been
clash-checked at -4.0, 0 and +2.0. With the tail plate at -4.0 it is 39.5
clear of the next plate. What pushes the plate is **open**: a jacking screw
in a block bolted to the frame is the intent.

**Returning-run clearance.** Cleats on the returning (lower) run point at the
bridge plates. Cleat tip radius is 34.947 against a 48.0 shaft height, so
**13.05** of clearance; the check requires > 5.0. If the measured pillow
blocks bring the shaft height down, this is what it eats.

---

## 7. What is known about the parts still to be specified

### 7.1 Side skirts and posts

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

### 7.2 Pillow blocks and standoffs

Not modelled, deliberately, until the real blocks are measured. The numbers
that depend on them: shaft height 48.0 above the plate top (provisional),
bearing centres at z = ±50, and at least the returning-run clearance above.

### 7.3 Motor mount and coupler

Nothing decided beyond: the head shaft is driven at 30 rpm, 22.5 of shaft
projects beyond each bearing centre, and 138 of frame beyond the head shaft
is reserved. Load is light (loose LEGO on a 60 mm/s belt). Motor, reduction
and coupler are all **open**.

### 7.4 Hopper and brush mounts

Not designed. The hopper wraps the tail end, so it must clear the swept radii
in §2.3, let the tail assembly slide through the take-up range, and leave
the tail shaft set's grub screws reachable.

---

## 8. Physical tests still to be done, in order

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

Also still to be measured, independent of the above: the pillow-block shaft
height.

---

## 9. The CAD project a specification has to fit

Python, [build123d](https://github.com/gumyr/build123d) 0.11 (OpenCascade),
at the repo root. Layers, each importing only from the ones above it in this
table:

| Layer | Holds | Returns |
|---|---|---|
| `params.py` | every dimension, plus assertions tying them together | numbers |
| `geometry.py` | datums and placement: run direction, shaft axes, `at(t, offset, lateral)`, `loop_at(s, takeup)`, `tail_shaft_t(takeup)`, the radial stations of §2.3 as functions, `is_cleated(i)`, plate and frame datums | numbers, transforms; never a solid |
| `profile.py` | the belt tooth and the standard pulley groove; `pulley_section()` is the only thing that makes teeth | 2D edges and faces; never a solid |
| `parts/*.py` | one module per part: `slat`, `shaft_set`, `shaft`, `belt`, `coupons`, `frame`, `bridge_plate` | a solid in its own local frame; never a machine position |
| `assembly.py` | named groups of positioned parts: `frame`, `plates`, `drivetrain`, `belts`, `slats` | positioned compounds |

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
   pytest test. Currently 26 checks and 133 tests, all passing.
5. **A negative control must be able to fail.** One drivetrain check asked
   that a zero-clearance guide groove collide with the lug; a straight lug
   only *touches* a revolved groove of its own section, sharing no volume, so
   the control had to be redesigned. Prefer controls with real interference.
6. **Anything near the tail must be checked across the take-up range**, not
   only at nominal. Every assembly group accepts a `takeup` argument for this.
7. **Say how each part leaves the project**: printed parts are exported as
   STL in a stated print orientation (so far: both slats, the shaft set, two
   coupons); bought or cut parts are reference solids only, and plywood parts
   go on the cut list.
8. Adding a part to the machine is one group function in `assembly.py`, one
   entry in its group table and one colour. If a part needs more than that,
   say so in the spec.

Helpers already available for checks: bounding-box size, volume in cm³,
point-in-solid, minimum distance between solids, and solid-solid clash with a
volume tolerance. A whole-loop sweep (every real slat against every fixed
part, at three take-ups) already exists and new fixed parts should be added
to it.

---

## 10. Open questions for the next specifications

1. **Skirts.** Given §7.1: inset, gap and height against the corrected slat
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
   and the standoff that sets it, keeping > 5.0 returning-run clearance.
5. **Take-up mechanism.** A jacking screw for the tail plate within the
   -4.0 .. +2.0 travel: where its block bolts to the frame, how the plate is
   locked once set, and how the two sides are kept square so the tail shaft
   stays parallel to the head shaft.
6. **Axial location of the shaft sets.** Two grub screws on a flat is all
   that holds each one in z, and both must agree to keep the guide grooves
   aligned. Is a positive stop (collar, spacer tube to the bearing) wanted?
7. **Drive.** Motor, reduction, coupler and mount for 30 rpm at light load,
   on whichever end of the head shaft, within 138 of frame and 22.5 of shaft.
8. **Hopper.** Geometry round the tail end against the swept radii of §2.3,
   sealing against 1.0 slat gaps that open to 5.7 on the tail pulley, and
   access to the tail grub screws and take-up.
9. **Pinch at the head.** Slat tops open to 5.7 going over the head pulley
   and close again onto the return run. Whether a part can be carried into
   that gap and pinched, and whether discharge needs a stripper or brush.
