# Feed elevator: design baseline for the belt and pulley work

Status as of 2026-09-21, commit `98f4fb1`. All dimensions are millimetres and
degrees.

This document describes what has been built and decided so far, so that a
specification for the **timing belt model** and the **printed timing pulley**
can be written against it. It is self-contained: it replaces the earlier
phase specification files as the reference for this work. Where a number here
and an older spec disagree, this document (and `params.py`, which it
is taken from) is correct.

Every value is labelled one of:

- **fixed** - decided and implemented; changing it invalidates built and tested geometry
- **catalogue** - a published figure for the bought part, not yet measured on the real one
- **provisional** - a starting guess, expected to be tuned
- **open** - not decided; input wanted

---

## 1. The machine

A feed elevator for a LEGO-sorting machine: a cleated slat conveyor inclined
at 40 degrees that lifts loose LEGO parts out of a hopper and drops them off
the head end.

- Two identical closed-loop timing belts run side by side, 54 mm apart, over
  a tail shaft and a head shaft.
- 46 printed slats clip across the *backs* of both belts and form the
  carrying surface. Every second slat carries a cleat.
- The belts are driven teeth-inward by printed pulleys, two per shaft, four
  in total, all the same part.
- Each 8 mm shaft runs in two pillow-block bearings bolted to plywood bridge
  plates, which bolt to the top of an aluminium 2020 extrusion frame. The
  whole frame is inclined with the run.
- The head shaft is driven; target 30 rpm, which gives 60 mm/s belt speed.

| Item | Status |
|---|---|
| Slat, plain and cleated | modelled, checked, STL exported; not yet test-fitted on a real belt |
| 2020 frame | modelled as a reference solid (owned hardware) |
| Bridge plates, five | modelled as reference solids with frame bolt holes; cut list generated |
| Assembly framework | built; frame and plates are its two groups |
| **Belt** | **chosen and bought-in; parameters recorded; no CAD model yet** |
| **Pulley** | **key dimensions decided; parameters recorded; no CAD model yet** |
| Tooth profile | closed-form construction chosen, radii provisional; no code yet |
| Side skirts, skirt posts, pillow-block standoffs, motor mount, coupler, hopper | not designed |

---

## 2. Coordinate system and datums

Machine frame: origin on the **tail shaft axis** at the machine centre plane.
+X horizontal towards the head end, +Y up, +Z across the machine along the
shaft axes. Both shaft axes are parallel to Z.

| Datum | Value |
|---|---|
| Run direction (unit) | (cos 40°, sin 40°, 0) |
| Run normal (unit), out of the carrying face | (-sin 40°, cos 40°, 0) |
| Tail shaft axis | (0, 0, z) |
| Head shaft axis | (271.18, 227.55, z), i.e. 354.0 along the run |
| Belt centrelines | z = +27 and z = -27 |

Positions along the conveyor are given as `(t, offset, lateral)`:

- `t` - distance along the run from the tail shaft axis
- `offset` - distance from the **shaft axis** along the run normal; positive
  is outward through the carrying run, negative is down towards the frame
- `lateral` - z

So `offset = 0` is on the shaft centreline, and these are the radial stations
that matter, all measured from a shaft axis:

| Surface | Offset / radius | |
|---|---|---|
| Frame rail top faces | -57.0 | fixed |
| Bridge plate top faces (pillow blocks mount here) | -48.0 | provisional, see §6 |
| Saddle tab tips (slat on a pulley) | 15.118 | fixed |
| Pulley OD (tooth tips of the pulley) | 18.718 | derived |
| Belt pitch line | 19.099 | derived |
| Belt back = slat contact face | 21.118 | derived |
| Slat top face | 24.118 | fixed |
| Cleat tip | 36.118 | fixed |

**Local frame convention for parts.** Anything placed on the run is modelled
with local +x along the run, +y out along the run normal, +z across the
machine, and its origin on the face it mates with, so that placing it is a
single transform with no corrective offset. The slat's origin is the centre
of its belt-contact face.

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

The belt's role in the CAD project is a **reference solid**: something to
position slats and pulleys against and to clash-test, never exported. Belt
and pulley grooves are intended to come from one shared tooth-profile
function, so the two models cannot drift apart.

---

## 4. The slat-to-belt interface (built, and the main constraint on the pulley)

The slats are finished and tested geometry. Anything specified for the belt
or pulley has to live with them as they are.

### 4.1 Slat

| | Value |
|---|---|
| Slat pitch along the belt | 18.0 = 6 belt teeth; 46 slats around the loop |
| Slat body | 16.0 along the run × 3.0 thick × 80.0 across the machine |
| Gap between adjacent slats on a straight run | 2.0 |
| Cleat | every 2nd slat (23 of 46); 12.0 high, 10.0 wide at the root tapering to 4.0 at the tip, 74.0 long, 1.0 root fillets |
| Edge chamfer | 0.5 |
| Bounding box, plain / cleated | 16 × 9 × 80 / 16 × 21 × 80 |
| Print orientation | top face down, tabs up |

The slat count must stay an integer (`828 / 18 = 46`) and even, so the
cleat pattern closes across the belt seam; both are asserted in `params.py`.

### 4.2 Saddle: how a slat holds a belt

Each slat has two saddles, one per belt. A saddle is a pair of tabs hanging
from the belt-contact face that grip the two **edges** of the belt. There is
no fastener and nothing engages the belt teeth.

| Parameter | Value | |
|---|---|---|
| Tab length along the run | 7.0 (≤ 2.5 belt pitches, so a tab stays short on the pulley arc) | fixed |
| Tab thickness across the machine | 2.5 | fixed |
| Tab depth below the belt-contact face | 6.0 | provisional, see below |
| Gap between the facing tab faces | 14.8 = belt width - 0.2 interference | provisional |
| Retention lip at each tab tip | projects 0.8 inward, 1.0 high | fixed |
| Clear opening between the two lips | 13.2 | derived |

Tab faces in slat-local z, for the +z belt (mirror for the other):

```
inner tab   17.1 .. 19.6
belt        19.6 .. 34.4   (nominal 15.0 belt squeezed into 14.8)
outer tab   34.4 .. 36.9
slat end    40.0           (3.1 of slat beyond the outer tab)
```

Things to know:

- The belt is gripped by 0.2 total interference on its edges and trapped by
  the lips. The lips' upper faces sit 5.0 below the belt-contact face, and
  the belt is only 2.4 thick, so there is **2.6 of free height under the
  belt inside the saddle**. The 6.0 tab depth was sized for a 3.8 thick
  belt before the belt was changed and has not been revisited.
- The interference, the tab depth and the cleat height are unvalidated until
  a printed plain + cleated pair has been run on real belt stock round a
  pulley. That physical test has not been done yet.

### 4.3 What this leaves for the pulley

As a slat goes round a shaft its tabs reach radially inward to **r = 15.118**,
well inside the pulley OD of r = 18.718. The tabs therefore straddle the
pulley, and the pulley has to fit between them:

| Constraint on the pulley | Value |
|---|---|
| Toothed face width | 5.0, centred on the belt centreline (belt overhangs 5.0 each side) |
| Axial clearance, pulley face to tab inner face | 4.9 each side |
| Axial clearance, pulley face to lip | 4.1 each side |
| Envelope for anything wider than ±6.6 from the belt centreline | must stay inside r ≈ 15.1, less running clearance |
| Flanges | **none** - the only space beside the toothed face is where the tabs run |
| Gap between the two inner tabs, across the machine centre | 34.2 (z = -17.1 .. +17.1) |

So lateral belt tracking is not done by the pulley. It is done by the slats:
every slat ties the two belts together at a fixed 54.0 spacing. Whether that
is sufficient is an assumption, not a tested result.

The implemented clearance check models each pulley as a plain cylinder of
r = 18.718 × 5.0 wide at the belt centreline and asserts that neither slat
variant intersects it. Asserted margins: tab to pulley face ≥ 1.5, outer tab
to slat end ≥ 2.0, belt overhang beyond the pulley face ≥ 2.0 per side.

---

## 5. The pulley: what is decided so far

Printed part, four off, identical, no flanges.

| Parameter | Name in `params.py` | Value | |
|---|---|---|---|
| Teeth | `PULLEY_TEETH` | 40 | fixed |
| Pitch diameter | `PULLEY_PD` | 38.197 = 40 × 3 / π (120.0 pitch circumference) | derived |
| Outside diameter | `PULLEY_OD` | 37.435 = PD - 2 × PLD | derived |
| Toothed face width | `PULLEY_FACE_WIDTH` | 5.0 | fixed (§4.3) |
| Bore | `PULLEY_BORE` | 8.0 | fixed |
| Bore clearance | `PULLEY_BORE_CLEARANCE` | 0.15 (printed holes run undersize) | provisional |
| Hub diameter | `PULLEY_HUB_DIA` | 22.0 (r = 11.0, clears the tab tips by 4.1 radially) | provisional |
| Hub length beyond the toothed face | `PULLEY_HUB_LENGTH` | 10.0 | provisional |
| Fixing | `PULLEY_GRUB_M` | one M4 grub screw into a heat-set insert in the hub | provisional |
| Insert pocket | `PULLEY_INSERT_DIA` / `_DEPTH` | 5.6 dia × 8.0 deep | provisional |
| Groove clearance over the belt tooth | `GROOVE_CLEARANCE` | 0.10 | provisional, tune on the printer |
| Print orientation | `PRINT_ROT_PULLEY` | hub end down, axis vertical | fixed |

40 teeth was chosen because it keeps a 120 mm pitch circumference, which the
slat clearances and the returning-run clearance (§6) were all worked out
around.

### Tooth profile (shared by belt and pulley)

The intended construction is closed-form, with no iterative solver: a single
circular **flank arc** that reaches the tooth apex directly, blended into the
flat land between teeth by a **root fillet** on each side. There is no
separate tip arc.

| Parameter | Name | Value | |
|---|---|---|---|
| Flank arc radius | `FLANK_RADIUS` | 0.79 | provisional |
| Root fillet radius | `ROOT_RADIUS` | 0.26 | provisional |
| Flank arc centre height above the land | `FLANK_CENTRE_Y` | 0.381 | fixed equal to `BELT_PLD`, asserted |
| Tooth height | `TOOTH_HEIGHT` | 1.171 = centre height + flank radius | derived |
| Land width between teeth | `LAND_WIDTH` | 0.914 | derived |

`LAND_WIDTH = pitch - 2·sqrt((R_flank + R_root)² - (R_root - y_centre)²)`.

These radii are approximations to the HTD-3M form chosen to hit the published
tooth height; they are not taken from a standard. The plan is to correct them
empirically with a printed **calibration coupon**: a flat 40 mm bar with five
grooves cut by the same profile function at the same clearance
(`COUPON_LENGTH`, `COUPON_GROOVE_COUNT`), into which a scrap of the real belt
is pressed, before any pulley is printed.

---

## 6. Shafts, bearings and structure

| Parameter | Value | |
|---|---|---|
| Incline | 40° from horizontal | fixed |
| Shaft | 8.0 dia × 145.0 long, two off | fixed |
| Pillow-block bearing centres | 100.0 (z = ±50) | fixed |
| Shaft axis above the bridge plate top face | 48.0 | **provisional** - depends on the pillow blocks actually bought and a standoff not yet designed |
| Shaft speed | 30 rpm → 60 mm/s | fixed target |
| Frame | 2020 extrusion rectangle, 552 long × 274 wide overall, 234 between rails | fixed, owned, uncut |
| Frame position along the run | from t = -60 to t = 492; 138 of frame beyond the head shaft, reserved for the motor | fixed |
| Bridge plates | five, 9 plywood, 45 along the run × 274 across, on top of both rails, M5 into T-nuts | fixed |
| Plate stations | t = 0, 88.5, 177, 265.5, 354; the end two carry the pillow blocks, the middle three will carry skirt posts | fixed |

Along each shaft, from the centre outwards: inner tabs to z = 17.1, pulley
face z = 24.5 .. 29.5, outer tabs to z = 36.9, slat end z = 40, bearing
centre z = 50, shaft end z = 72.5. A pulley hub therefore has 4.9 + 2.5 of
tab zone beside it on either side and must stay under r ≈ 15 there.

**Returning-run clearance.** Cleats on the returning (lower) run point at the
bridge plates. Cleat tip radius is 36.118 against a 48.0 shaft height, so
11.9 of clearance; the check requires > 5.0. This is the clearance most
sensitive to pulley diameter and belt thickness: anything that increases the
belt-back radius of 21.118 eats into it directly.

---

## 7. The CAD project the specification has to fit

Python, [build123d](https://github.com/gumyr/build123d) 0.11 (OpenCascade),
at the repo root. Four layers, each importing only from the ones above it in
this table:

| Layer | Holds | Returns |
|---|---|---|
| `params.py` | every dimension, plus assertions tying them together | numbers |
| `geometry.py` | datums and placement: run direction, shaft axes, `at(t, offset, lateral)`, `belt_back_radius()`, `slat_t(i)`, `is_cleated(i)`, plate and frame datums | numbers, transforms; never a solid |
| `parts/*.py` | one module per part: `slat.py`, `frame.py`, `bridge_plate.py` | a solid in its own local frame; never a machine position |
| `assembly.py` | named groups of positioned parts (`frame`, `plates` so far) | positioned compounds |

Rules a new part specification should respect:

1. **No numeric dimension outside `params.py`.** A spec should give a
   parameter table with names, values and units, and say which values are
   derived and from what.
2. **State the local frame and origin** of each part, with the origin on its
   mating surface.
3. **Give acceptance criteria as checkable assertions with numbers**:
   bounding boxes, volume ranges, points that must be inside or outside the
   solid, pairs of solids that must not intersect, validity of the solid.
   Each one is implemented twice, in `checks.py` (pass/fail report) and as a
   pytest test. Currently 15 checks and 58 tests, all passing.
4. **Say how each part leaves the project**: printed parts are exported as
   STL in a stated print orientation; bought or cut parts are reference
   solids only.
5. Adding a part to the machine is one group function in `assembly.py`. No
   belt, pulley or slat group exists in the assembly yet.

Helpers already available for checks: bounding-box size, volume in cm³,
point-in-solid, and solid-solid clash with a volume tolerance.

Modules the belt and pulley work is expected to add: a tooth-profile module,
`parts/pulley.py`, `parts/belt.py`, a coupon part, and their export and
check entries. None exist yet; only their parameters do.

---

## 8. Open questions for the belt and pulley specification

1. **Tooth form.** Is the single-flank-arc-plus-root-fillet construction in
   §5 an adequate approximation of HTD-3M for a printed 40-tooth pulley at
   30 rpm and light load, and what should the radii and the pulley groove
   form be? Should the groove be the belt tooth offset by a uniform
   clearance, or a distinct pulley-groove profile?
2. **Printed tolerances.** Groove clearance, OD compensation for a printed
   pulley, and the calibration procedure (coupon) that fixes them.
3. **Belt tracking with no flanges**, a 5 mm face under a 15 mm belt, and the
   slats as the only lateral constraint. Is this workable, and if not, what
   fits inside the envelope of §4.3 (crowning is not available on a toothed
   pulley)?
4. **Tensioning.** Centre distance is fixed at exactly 354.0 by the stock
   belt length, and no take-up mechanism has been designed. Pillow blocks
   bolt to plywood plates, which bolt to T-slots along the run, so there is
   some adjustment available in principle.
5. **Tail pulleys.** All four pulleys are currently assumed identical and
   toothed. Should the tail pair be toothed, fixed to the shaft, or free to
   idle? The two belts must stay in phase because the slats tie them
   together.
6. **Shaft fixing.** One M4 grub screw on a round 8 mm shaft, in a printed
   hub with a heat-set insert: enough for the drive pair, and how should the
   two pulleys on one shaft be kept in angular phase with each other?
7. **Hub design** within the constraints of §4.3 and §6: hub on which side,
   length, and whether 22 mm diameter should change.
8. **Saddle fit on the 2.4 mm belt** (§4.2): the 2.6 mm of free height under
   the belt, and whether the tab depth should come down. This touches the
   finished slat, so a recommendation is wanted rather than an assumption.
9. **Chordal effects.** 16 mm rigid slats on an 18 mm pitch going round a
   21.1 mm radius: whether the belt back is asked to do anything it will
   not tolerate over the 7 mm gripped by each tab.
10. **Belt model fidelity.** How much of the belt needs modelling for it to
    be a useful reference solid: full toothed loop, or straight toothed
    spans plus plain arcs.

Still to be measured on real hardware, independent of the above: the belt's
actual thickness and width, and the pillow-block shaft height.
