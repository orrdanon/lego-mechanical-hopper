# Feed elevator: tilt mechanism specification

Written against `design-baseline-v2.md` (commit `ad71c0e`). All dimensions are
millimetres and degrees. Status labels are the baseline's: **fixed**,
**catalogue**, **provisional**, **open**. Every number in this document goes
into `params.py`; none may appear as a literal anywhere else.

---

## 1. What this adds

The baseline fixes the incline at 40°. This work makes it adjustable by hand
over **25° .. 55°**, and adds the parts that hold the machine at that angle:

- The frame **hinges at its bottom tail corner**, on an axis across the
  machine, 20 above the base.
- A single **prop** under the machine centreline holds the frame up. It is
  pinned at both ends: to a 2020 cross-member bolted between the rails, and to
  a block on the base. Its length sets the angle.
- The prop's length is set by turning an **M8 threaded rod** into a nut
  captured in a printed body. A knob turns the rod; a lock nut holds it.
- There are no bearings. Every pivot is an M8 bolt in a printed hole.

Nothing on the conveyor itself changes. At 40° every existing part must land
exactly where it does today, and every existing check must still pass.

A future motorised version replaces the prop with a bought linear actuator
between the same two pins. That is **out of scope** here; see §9.

| Item | Made how | Off |
|---|---|---|
| Hinge bracket, frame side | printed, left and right (mirror pair) | 2 |
| Hinge block, base side | printed, left and right (mirror pair) | 2 |
| Cross-member | 2020 extrusion, cut to 234 | 1 |
| Frame clevis | printed | 1 |
| Prop body | printed | 1 |
| Prop foot (swivel) | printed | 1 |
| Knob | printed | 1 |
| Base pin block | printed | 1 |
| Base | **open**; a reference plane only in this work | - |
| Hardware | bought; see §7 | - |

---

## 2. Datums and coordinates

### 2.1 The incline becomes a parameter

| Parameter | Name | Value | |
|---|---|---|---|
| Nominal incline | `INCLINE` | 40.0 | fixed (unchanged meaning: the default) |
| Minimum incline | `TILT_MIN` | 25.0 | provisional |
| Maximum incline | `TILT_MAX` | 55.0 | provisional |
| Incline samples for checks | `TILT_CHECK_ANGLES` | (25.0, 40.0, 55.0) | fixed |

Thread an `incline` argument through `geometry.py` and `assembly.py` the same
way `takeup` was threaded: every function that uses the run direction, the run
normal, the head shaft position or `loop_at` takes `incline=INCLINE`. Every
assembly group accepts `incline`. The run direction becomes
`(cos incline, sin incline, 0)` and the run normal `(-sin incline, cos incline, 0)`.

**The machine frame does not move.** Its origin stays on the tail shaft axis at
nominal take-up, +X horizontal, +Y up. Changing `incline` rotates the conveyor
about that origin. The base, which physically stays put, is what moves in
machine coordinates (§2.2). This keeps every existing datum and part
placement valid.

### 2.2 Hinge axis and base frame

| Parameter | Name | Value | |
|---|---|---|---|
| Hinge axis, along the run | `HINGE_T` | -50.0 (10 in from the frame's tail end) | provisional |
| Hinge axis, offset | `HINGE_OFFSET` | -67.0 (rail centreline) | fixed |
| Hinge axis above the base top face | `HINGE_HEIGHT` | 20.0 | provisional |

The hinge axis is parallel to z and fixed to the **frame**, not to the take-up.
Moving the tail bridge plate does not move it.

New `geometry.py` functions, numbers and transforms only:

- `hinge_axis(incline)`: the point `at(HINGE_T, HINGE_OFFSET, 0, incline)` in
  machine coordinates.
- `base_frame(incline)`: a location whose origin is on the base top face
  directly below the hinge axis (`hinge_axis - (0, HINGE_HEIGHT, 0)`), with
  machine axes (+x horizontal toward the head, +y up, +z across). **Every
  base-fixed part is placed with this.**
- `base_z(incline)`: machine y of the base top face.

In base-frame coordinates, horizontal distance from the hinge axis is `bx` and
height above the base is `by`; the hinge axis is at `(0, 20)`.

---

## 3. Hinge

### 3.1 Frame-side hinge bracket (printed, mirror pair)

A plate on the **outer face** of each side rail, carrying a hex-head M8 bolt
that acts as the hinge pin.

| Parameter | Name | Value | |
|---|---|---|---|
| Plate, along the run | `HINGE_BRKT_T0` .. `_T1` | t = -60.0 .. -20.0 | provisional |
| Plate, offset | | -77.0 .. -57.0 (the rail's full height) | fixed |
| Plate thickness | `HINGE_BRKT_THK` | 10.0 (z = ±137 .. ±147) | provisional |
| Boss round the axis | `HINGE_BOSS_R` | 12.0 | provisional |
| Pin hole | `HINGE_PIN_HOLE` | 8.0 | provisional |
| Bolt-head pocket, rail side | `HINGE_HEAD_POCKET` | M8 hex, 13.0 AF + 0.3, 5.5 deep, open to the rail face | provisional |
| Frame fixing | | 2 × M5, counterbored, into T-nuts in the rail's outer slot at t = -35.0 and -25.0, offset -67.0 | provisional |
| Print orientation | | rail face down | fixed |

The M8 bolt goes in from the rail side before the bracket is bolted on. Its
head sits in the hex pocket, trapped between the bracket and the rail face, so
it cannot turn or fall out. The shank points outboard along ±z.

The boss extends 2.0 beyond the rail top and bottom and 2.0 beyond the rail's
tail end. Its lowest point is 8.0 above the base at every angle.

Local frame: origin on the rail-contact face, on the hinge axis; +x along the
run, +y along the run normal, +z outboard. The left-hand part is the mirror in z.

### 3.2 Base-side hinge block (printed, mirror pair)

An upright on the base, holding the hinge pin in a plain printed bushing.

| Parameter | Name | Value | |
|---|---|---|---|
| Gap to the frame bracket | `HINGE_GAP` | 1.0 (block inner face at z = ±148) | provisional |
| Block thickness | `HINGE_BLOCK_THK` | 20.0 (z = ±148 .. ±168) | provisional |
| Upright width, along x | | 30.0, centred on the axis | provisional |
| Bushing hole | `HINGE_BUSH_HOLE` | 8.4 (running fit) | provisional |
| Material round the hole, above | | ≥ 8.0 | provisional |
| Foot flange | | 60.0 along x × 20.0 across × 5.0 thick, outboard side | provisional |
| Base fixing | | 4 × 5.0 through-holes; fastener **open** (depends on the base) | open |
| Print orientation | | foot down | fixed |

Outboard of the block: an M8 washer and an M8 nylock, snug, not tight. The
bolt must turn freely in the block.

Local frame: origin on the base top face, directly under the hinge axis, at
the block's inner face; axes as `base_frame`, +z outboard.

**Space reservation.** The take-up mechanism (baseline §10 item 5) is not
designed. The hinge brackets occupy the rail outer faces from t = -60 to -20,
and the hinge blocks stand outboard of them. The take-up must not use that
space.

---

## 4. Cross-member and frame clevis

### 4.1 Cross-member (2020, cut)

| Parameter | Name | Value | |
|---|---|---|---|
| Length | `XMEMBER_LEN` | 234.0, between the rails' inner faces | fixed by the frame |
| Centre, along the run | `XMEMBER_T` | 221.0 (t = 211 .. 231) | provisional |
| Offset | | -77.0 .. -57.0, flush with the rails | fixed |
| Fixing | | 4 × 2020 corner brackets on the underside, M5 into T-nuts | catalogue |

`XMEMBER_T` sits in the gap between the bridge plates at t = 177 and 265.5.
Assert that it clears both plate footprints by **≥ 5.0 along the run**.

Leaves the project as a reference solid and a cut-list entry
("2020, 234 long, ends square").

### 4.2 Frame clevis (printed)

Bolts to the underside of the cross-member at z = 0 and carries the prop's
top pin, pin A.

| Parameter | Name | Value | |
|---|---|---|---|
| Pin A, along the run | `PROP_PIN_A_T` | = `XMEMBER_T` = 221.0 | provisional |
| Pin A, offset | `PROP_PIN_A_OFFSET` | -87.0 (10.0 below the rail underside) | provisional |
| Cheek inner gap | `CLEVIS_GAP` | 12.6 (prop eye 12.0 + 0.3 each side) | provisional |
| Cheek thickness | | 6.0 each | provisional |
| Pin hole | `CLEVIS_PIN_HOLE` | 8.2 | provisional |
| Material below pin A | | ≥ 7.0 | provisional |
| Fixing to the cross-member | | 2 × M5 into T-nuts in its bottom slot, at z = ±15.0 | provisional |
| Print orientation | | cross-member face down | fixed |

The cheeks must allow the prop to swing through its full lean range (§5.3)
without the prop body touching the clevis base. Assert this at 25° and 55°.

Local frame: origin on the cross-member contact face, above pin A, at z = 0;
axes as the run (+x along, +y along the normal, +z across).

---

## 5. Prop

### 5.1 How it works

```
pin A (frame clevis)
  |
  prop body       - printed; top eye on pin A; M8 nut captured at the bottom;
  |                 a clearance bore above the nut takes the rod as it screws in
  |
  lock nut        - jammed up against the body bottom to lock the setting
  M8 rod          - threads into the body's nut; turns, does not slide in the foot
  jam nut
  knob            - printed, captured M8 nut, sits on a washer on the foot's top face
  foot            - printed swivel on pin B; the rod passes through its top wall
  two nuts, jammed, in the foot's pocket below the wall (stop the rod lifting out)
  |
pin B (base pin block)
```

The prop is in compression. The rod's thrust goes through the knob and washer
onto the foot's top wall. Turning the knob screws the rod into or out of the
body and changes the prop length. The body does not turn: it is pinned at the
top. To lock the setting, run the lock nut up against the body bottom.

### 5.2 Pins and lengths

| Parameter | Name | Value | |
|---|---|---|---|
| Pin B, horizontal from the hinge axis | `PROP_PIN_B_X` | 125.0 | provisional |
| Pin B, above the base | `PROP_PIN_B_Y` | 15.0 | provisional |
| M8 pitch | `M8_PITCH` | 1.25 | catalogue |
| Pin A to body bottom face | `PROP_BODY_LEN` | 90.0 | provisional |
| Body outer diameter | `PROP_BODY_DIA` | 18.0 | provisional |
| Body eye width (across z) | `PROP_EYE_W` | 12.0 | provisional |
| Body eye hole | `PROP_EYE_HOLE` | 8.4 | provisional |
| Captured nut pocket | `PROP_NUT_POCKET` | M8 hex 13.0 AF + 0.3, 6.8 deep; nut top 8.0 above the body bottom face | provisional |
| Rod clearance bore | `PROP_ROD_BORE` | 9.0, from the nut top to 12.0 below pin A | provisional |
| Pin B to foot top face | `FOOT_LEN` | 28.0 | provisional |
| Rod bottom end above pin B | `ROD_BOTTOM_Z` | 10.0 (inside the foot pocket) | provisional |
| Foot pocket | | 16.0 dia × 15.0 tall, round, so the two jammed nuts turn freely; 0.3 axial play to the wall | provisional |
| Foot top wall | | 5.0 thick, 8.6 hole | provisional |
| Stack on the rod above the foot | `FOOT_STACK` | washer 1.6 + knob 12.0 + jam nut 6.5 + clearance 3.0 + lock nut 6.5 = 29.6 | derived |
| Knob | `KNOB_DIA` / `KNOB_THK` | 40.0 / 12.0, knurled or lobed rim, captured M8 nut | provisional |
| Rod length | `ROD_LEN` | 136.0 | provisional, see the window below |

**Geometry (in the base frame; `geometry.py` implements these):**

- `prop_pin_a(incline)`: `at(PROP_PIN_A_T, PROP_PIN_A_OFFSET, 0, incline)`.
- `prop_pin_b(incline)`: `base_frame(incline) * (PROP_PIN_B_X, PROP_PIN_B_Y, 0)`.
- `prop_length(incline)`: the distance between them.
- `incline_for_length(L)`: the inverse, by bisection on `[TILT_MIN, TILT_MAX]`.
- `prop_turns(incline)`: `(prop_length(incline) - prop_length(TILT_MIN)) / M8_PITCH`.

Expected values, which the tests pin to ±0.5 (length) and ±1.0 (angle):

| Incline | Prop length | Lean from vertical (toward the head at the top) | Pin A above base | Prop force (§5.4) |
|---|---|---|---|---|
| 25° | 164.1 | 51.8 | 116.4 | about 98 N |
| 40° | 189.6 | 30.2 | 178.9 | about 58 N |
| 55° | 220.5 | 12.3 | 230.5 | about 37 N |

Length change over the range: **56.4**, about 45 turns. `prop_length` must be
strictly increasing over the range (so turning the knob one way always raises
the frame). Assert this on a 0.5° grid.

### 5.3 Length budget (assertions in `params.py`)

These three conditions make the prop buildable. They are in terms of the
parameters above, so moving a pin re-checks them automatically.

1. **Rod stays engaged at full length.** At `prop_length(TILT_MAX)`, the rod
   tip is at least 2.0 above the captured nut's top face:
   `ROD_BOTTOM_Z + ROD_LEN ≥ L_max - PROP_BODY_LEN + 8.0 + 2.0`.
2. **Rod clears pin A at minimum length.** At `prop_length(TILT_MIN)`, the rod
   tip is at least 12.0 below pin A:
   `ROD_BOTTOM_Z + ROD_LEN ≤ L_min - 12.0`.
3. **The stack fits.** At minimum length, the body bottom is above the top of
   the stack on the foot:
   `L_min - PROP_BODY_LEN ≥ FOOT_LEN + FOOT_STACK`.

With the values above: condition 1 needs a rod of at least 130.5, condition 2
allows at most 142.1, and condition 3 leaves 16.5 spare. `ROD_LEN = 136.0`
sits mid-window.

### 5.4 Loads (informational, reported by `checks.py`)

Assume 34 N total weight acting at t = 220, offset -40
(`TILT_WEIGHT_N`, `TILT_CG_T`, `TILT_CG_OFFSET`; **provisional**, an estimate
until weighed). Prop force = the weight's moment about the hinge axis divided
by the perpendicular distance from the hinge axis to the prop line. The report
prints the force at each check angle. Assert only that it stays under 150 N
(`PROP_FORCE_MAX`) over the range. A doubled weight must still pass, which
guards the estimate.

### 5.5 Printed prop parts

| Part | Local frame origin | Print orientation |
|---|---|---|
| Prop body | pin A centre; +z along the prop axis, from pin A toward the body bottom; +x along the pin | body bottom face down, eye up; nut pocket printed as a bridged hex |
| Foot | pin B centre; +z along the prop axis toward pin A; +x along the pin | top wall up |
| Knob | centre of its bottom face, on the rod axis | flat face down |

### 5.6 Base pin block (printed)

| Parameter | Name | Value | |
|---|---|---|---|
| Position | | centred on pin B, at z = 0 | fixed by §5.2 |
| Cheek inner gap | | foot eye width 12.0 + 0.3 each side = 12.6 | provisional |
| Cheek thickness | | 6.0 each | provisional |
| Pin hole | | 8.2 | provisional |
| Foot plate | | 70.0 along x × 50.0 across × 5.0 thick | provisional |
| Base fixing | | 4 × 5.0 through-holes; fastener **open** | open |
| Print orientation | | plate down | fixed |

Local frame: origin on the base top face directly under pin B, with base-frame
axes.

---

## 6. The base (reference only)

The base is **open**: a board, an extrusion frame, or the bench. For this work
it is a reference slab whose top face is the base plane: 20 thick, from 120
behind the hinge axis to 600 ahead of it, z = ±200. It is used only for
clearance checks. It is not exported and not on the cut list. Name it
`base_ref`, and have the assembly report flag it as a placeholder.

---

## 7. Hardware

| Item | Qty | Use |
|---|---|---|
| M8 × 45 hex bolt | 2 | hinge pins (head in the bracket pocket) |
| M8 × 45 hex bolt | 2 | pins A and B |
| M8 nylock nut | 4 | one per pin |
| M8 washer | 5 | hinge × 2, pins A and B × 2, under the knob × 1 |
| M8 threaded rod, 136 long | 1 | prop adjuster (cut from stock) |
| M8 hex nut | 6 | body (captured), lock, knob (captured), knob jam, two jammed in the foot pocket |
| M5 × 12 + T-nut | 6 | hinge brackets × 4, clevis × 2 |
| 2020 corner bracket + M5 × 10 + T-nut | 4 | cross-member |
| 2020, 234 long | 1 | cross-member |
| Base fasteners | 12 | **open**; depends on the base |

Add these to the BOM output if the project has one; otherwise list them in the
assembly report.

---

## 8. Assembly, checks and tests

### 8.1 Assembly group

One new group, `tilt`, taking `incline` and `takeup`. It holds the hinge
brackets, cross-member and frame clevis (placed with the frame), the hinge
blocks, base pin block and base reference (placed with `base_frame`), and the
prop body, rod, nuts, knob and foot (placed along the line from pin B to pin A,
with the rod's position set by `prop_length`). Give it one colour. The base
reference gets its own muted colour and is excluded from any export.

Add the tilt group's frame-mounted parts to the existing **whole-loop sweep**
(every real slat against every fixed part, at three take-ups). Run that sweep
at all three `TILT_CHECK_ANGLES`. The slats and prop move relative to each
other only through `incline`, so 3 × 3 = 9 sweep cases.

### 8.2 Checks

Each check goes in `checks.py` and as a pytest test. Radial and offset
clearances use named stations and parameters, never literals. "All
angles × take-ups" means `TILT_CHECK_ANGLES` × (`TAIL_TAKEUP_MIN`, 0, `TAIL_TAKEUP_MAX`).

| # | Check | Criterion | Cases |
|---|---|---|---|
| T1 | Regression | every existing check and test passes unchanged at `incline=INCLINE` | 40° |
| T2 | Frame clears the base | min distance from the frame, plates, drivetrain, belts, slats and the tilt group's frame-mounted parts to `base_ref` ≥ 4.0 | all angles × take-ups |
| T3 | Tail shaft height | tail shaft axis 94.0 .. 108.0 above the base plane | all angles × take-ups |
| T4 | Hinge parts do not clash | bracket vs block, bracket vs rail, block vs rail: no volume overlap; bracket-to-block min distance ≥ 0.8 | all angles |
| T5 | Cross-member clear of plates | min distance along the run to the plates at t = 177 and 265.5 ≥ 5.0 | nominal |
| T6 | Cross-member clears the return run | in the whole-loop sweep; also its top face at least 15.0 below `-cleat_tip_radius()` | all angles × take-ups |
| T7 | Prop clears the frame | prop body, rod, nuts and knob: no overlap with the rails, cross-member, plates or base; prop body min distance to the rail underside plane ≥ 3.0 except inside the clevis | all angles |
| T8 | Prop swing in the clevis and base block | prop body and foot do not touch the clevis base or the base pin block plate | 25°, 55° |
| T9 | Prop length table | `prop_length` at 25 / 40 / 55 = 164.1 / 189.6 / 220.5 ± 0.5; strictly increasing on a 0.5° grid; `incline_for_length(prop_length(a)) = a ± 0.05` | - |
| T10 | Length budget | the three conditions of §5.3 | - |
| T11 | Force | prop force < `PROP_FORCE_MAX` over the range, also at 2 × `TILT_WEIGHT_N` | - |
| T12 | Head shaft height (report only) | print head shaft axis height above the base at each check angle: expect 251 / 331 / 389 ± 1 at take-up 0 | all angles |

**Negative controls.** Each must make its check fail with real volume or
distance, not a touch:

- **T2:** raise `base_ref` by 10.0. The rail's tail corner (about 6 above the
  base) must penetrate it.
- **T5:** set `XMEMBER_T = 190`. It overlaps the plate at 177 along the run by
  10; the min distance must report 0 or overlap.
- **T10:** set `ROD_LEN = 160`. Condition 2 must fail.
- **T7:** move `PROP_PIN_B_X` to 300. The prop must hit the frame underside
  at 25°. Confirm that it does before relying on this control; if it doesn't,
  choose a pin B position that does and record it.

### 8.3 Setting-up table

`checks.py` prints a table of prop length (pin to pin) against incline, every
2.5° from `TILT_MIN` to `TILT_MAX`. It also prints the **exposed rod length**
between the lock nut and the knob at each angle, because that is what can be
measured with calipers on the real machine. This table is how the angle gets
set by hand.

### 8.4 Exports

| Part | Export |
|---|---|
| Hinge bracket L, R | STL, rail face down |
| Hinge block L, R | STL, foot down |
| Frame clevis | STL, cross-member face down |
| Prop body | STL, eye up |
| Foot | STL, top wall up |
| Knob | STL, flat face down |
| Base pin block | STL, plate down |
| Cross-member | cut list: 2020, 234, ends square |
| Rod | cut list: M8 threaded rod, 136 |
| Base reference, bolts, nuts, rod | reference solids only |

---

## 9. Out of scope, and what to keep possible

- **Motorising.** The intended path is a bought linear actuator between pins A
  and B. Nothing here is designed for it. When it happens, `PROP_PIN_B_X` and
  `XMEMBER_T` will move to suit the actuator's retracted length and stroke,
  which is why both are parameters with a length-budget check rather than
  numbers baked into the parts.
- **Angle scale.** The table of §8.3 replaces a printed scale for now.
- **The base itself**, and how the hinge blocks and pin block fasten to it.
- **Take-up mechanism.** Must stay out of the hinge's space (§3.2).

## 10. Open points for the user

1. **Weight.** The prop force uses an estimated 34 N. Weigh the frame once it
   is assembled and update `TILT_WEIGHT_N`.
2. **Base.** Decide what the machine stands on. That fixes the hinge block and
   pin block fasteners.
3. **Tilt range.** 25° .. 55° is assumed. Narrowing it shortens the prop's
   length change and lowers the worst-case force, which is at 25°.
