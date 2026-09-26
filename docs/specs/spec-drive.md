# Feed elevator: drive specification, v1

Motor, coupler and motor bracket for the head shaft. Written against
`design-baseline-v3.md` (commit `ca50e1a`); its coordinate system, datums,
labels (**fixed / catalogue / provisional / open**) and rules in §10 apply
unchanged. All dimensions are millimetres and degrees.

Catalogue figures for 4project parts were read on 2026-09-26 from the product
pages; none has been measured on a real part yet (§9).

---

## 1. Decisions

| Decision | Status |
|---|---|
| The **head shaft** is driven, directly, with no reduction stage | fixed |
| Motor: **NEMA 17 stepper**, Waveshare 42.3 × 40, 1.8°, 1.7 A (4project 4P-748700 / WS-15948) | fixed |
| Motor axis on the head shaft axis; motor outboard of one pillow block | fixed |
| Coupling: **flexible (helical) coupler, 5 × 8**, aluminium (4project 4P-6813) | fixed |
| Motor held by a **printed bracket** bolted to the head bridge plate, sharing that plate's two outboard M5 frame bolts on the drive side | provisional |
| Head shaft **lengthened on the drive end only**; tail shaft unchanged | fixed |
| Driver: Pololu A4988 (4project product 1146), 1/16 microstepping, current-limited | provisional |
| Which side is driven: `DRIVE_SIDE` = +1 (+z) or -1 (-z) | **open**; everything below is built for +z and mirrored |

Why a stepper at 30 rpm with no gearbox: brushless and rated for continuous
running; speed exact and set in software (stop, start, trim from the sorter's
controller); and when overloaded it **skips steps instead of pushing harder**,
which protects the slats, whose grip on the belt is friction only (baseline
§4.2). A geared DC motor strong enough to be safe on torque stalls at hundreds
of newtons of belt pull.

---

## 2. Load and motor sizing

| Parameter | Name | Value | |
|---|---|---|---|
| Belt pull, estimate | `DRIVE_PULL_EST_N` | 8.0 N: 300 g of LEGO lifted at 55° (2.4 N) + hopper drag (≈4 N) + skirt, guide, bearing friction (≈1.5 N) | provisional; hopper drag is the uncertain term |
| Pitch radius | | `PULLEY_PD / 2` = 19.099 | derived |
| Shaft torque, estimate | `DRIVE_TORQUE_EST` | 0.153 N·m | derived |
| Shaft power at 30 rpm | | 0.48 W | derived |
| Motor holding torque at 1.7 A | `MOTOR_HOLD_TORQUE` | 0.449 N·m (4.58 kg·cm) | catalogue |
| Driver current limit | `DRIVE_CURRENT_A` | 1.2 A | provisional; §9 test D3 |
| Holding torque at that current | | 0.317 N·m (scaled linearly) | derived |
| Usable running torque at 30 rpm | `DRIVE_TORQUE_AVAIL` | 0.8 × holding = 0.254 N·m | provisional factor |
| Belt pull at which the motor skips | | 13.3 N | derived |
| Margin over estimate | | 1.66 (assert ≥ 1.5) | derived |
| Step rate | | 30 rpm × 200 × 16 / 60 = 1600 Hz | derived |

The current is deliberately below the motor's 1.7 A rating. The motor runs
continuously and touches a PETG bracket (glass transition ≈ 80 °C); at 1.2 A
peak and 2.4 Ω per coil it dissipates about 3.5 W. If the hopper drag turns
out larger than estimated, raise the current towards 1.5 A and re-check
temperature (§9, D3) rather than changing the motor.

The coupler (0.6 N·m rated) is stronger than the motor at any current, so it
is never the weak link.

---

## 3. Bought parts

### 3.1 Motor (reference solid, `parts/motor.py`)

| Parameter | Name | Value | |
|---|---|---|---|
| Body, square × length | `MOTOR_SQUARE`, `MOTOR_BODY_LEN` | 42.3 × 40.0 | catalogue |
| Pilot boss | `MOTOR_PILOT_DIA`, `MOTOR_PILOT_H` | 22.0 × 2.0 | provisional (NEMA 17 standard; the listing does not give it) |
| Mounting holes | `MOTOR_HOLE_SPACING`, `MOTOR_HOLE_M` | 4 × M3 on a 31.0 square | provisional (standard; listing silent) |
| Max screw engagement into the motor | `MOTOR_SCREW_MAX_ENGAGE` | 3.0 (the store warns longer screws can damage the motor) | catalogue |
| Shaft | `MOTOR_SHAFT_DIA`, `MOTOR_SHAFT_LEN` | 5.0 D-shaft, 23.5 long, **measured from the mounting face** | catalogue length; datum to be measured |
| Mass | `MOTOR_MASS_KG` | 0.30 (the store's shipping weight, so an upper bound) | catalogue |
| Connector | | 6-pin JST on the body; position to be measured | catalogue |

Local frame: origin at the centre of the mounting face, +z along the shaft
(out of the face), x and y across the face. The shaft and boss are at +z; the
body is at -z.

### 3.2 Coupler (reference solid, `parts/coupler.py`)

| Parameter | Name | Value | |
|---|---|---|---|
| Size | `COUPLER_DIA`, `COUPLER_LEN` | 20.0 × 25.0 | catalogue |
| Bores | | 5.0 and 8.0 | catalogue |
| Rated / max torque | | 0.6 / 1.2 N·m | catalogue |
| Engagement per shaft | `COUPLER_ENGAGE` | 10.0 target, 11.0 max | provisional; bore depths to be measured |
| Minimum gap between shaft tips inside it | `COUPLER_TIP_GAP_MIN` | 2.0 | provisional |
| Clamping | | set screw or clamp; the listing says only that an Allen key is needed | **open until measured** |

Local frame: origin on the axis at the 8-bore end face, +z towards the 5-bore
end.

### 3.3 Hardware

| Item | Qty | Notes |
|---|---|---|
| M3 × 8 socket head | 4 | motor to bracket; 8 = `FACE_PLATE_T` 5.0 + 3.0 into the motor (asserted ≤ `MOTOR_SCREW_MAX_ENGAGE`) |
| M5 × 20 socket head | 2 | replace the head bridge plate's two drive-side M5 at (t = 354 ± 12, z = +127); stack = foot 6 + plate 9 + T-nut about 5. Check against the length now used there |
| A4988 driver, JST 6-pin adapter cable (4project product 6500) | 1 each | electrical; not modelled |

---

## 4. Head shaft change

The shaft set, the flat and the tail shaft do not change. The head shaft
gains length on the drive end only, just enough for the coupler.

| Parameter | Name | Value | |
|---|---|---|---|
| Pillow block axial width, half | `PILLOW_BLOCK_HALF_W` | 14.0 | **provisional**, deliberately generous (a wide eccentric-collar insert); measure (§9, D1) |
| Gap, block face to coupler | `COUPLER_BLOCK_GAP` | 2.0 | provisional |
| Drive-end extension past the bearing centre | `HEAD_SHAFT_DRIVE_EXT` | `PILLOW_BLOCK_HALF_W + COUPLER_BLOCK_GAP + COUPLER_ENGAGE` = 26.0, rounded up with the length | derived |
| Head shaft length | `HEAD_SHAFT_LEN` | 72.5 + 50.0 + 26.0 = 148.5, **cut 149.0** | derived, rounded up to whole mm |
| Drive-end extension as cut | | 26.5 | derived |
| Non-drive end | | unchanged, 72.5 from z = 0 | fixed |
| Flat | | unchanged: 0.5 × 45.0, **centred on z = 0**, i.e. 72.5 from the non-drive end (not centred on the shaft) | fixed |
| Drive-end flat for the coupler | `HEAD_SHAFT_DRIVE_FLAT` | 0.5 deep × 10.0, only if the coupler uses set screws | open |

The head shaft is no longer symmetric, so it has a direction. `parts/shaft.py`
takes a `drive_ext` argument; the assembly places it with the long end at
`DRIVE_SIDE`. The tail shaft stays `shaft(drive_ext=None)`, 145.0.

This changes a value the baseline labels fixed. The shaft is a reference
solid, so nothing printed changes. Drivetrain checks that use the shaft
length must be re-run.

---

## 5. Axial stack on the drive side

Distances along the head shaft axis from the machine centre plane, for
`DRIVE_SIDE` = +1, at the provisional block width. All are derived in
`params.py` from the values above. Nothing here depends on incline or
take-up.

```
slat end                       40.0    (baseline §6)
bearing centre                 50.0
pillow block outer face        64.0    PILLOW_BLOCK_HALF_W
coupler, 8-bore end            66.0    + COUPLER_BLOCK_GAP
head shaft end                 76.5    engagement 10.5
motor shaft tip                81.0    engagement 10.0; tip gap 4.5
coupler, 5-bore end            91.0    + COUPLER_LEN
M3 heads                       96.5 .. 99.5
face plate, inboard face       99.5
motor mounting face           104.5    = 91.0 + (23.5 - 10.0)
motor body, back              144.5
connector                     beyond 144.5, to be measured
```

- The coupler sits in an open window between the pillow block and the face
  plate, so its screws can be reached from above.
- The motor body ends 7.5 outboard of the frame's outer face (z = 137).
  That is the machine's widest point at the head. The hinge blocks at the
  tail reach z = 168.
- If the measured block is narrower, `PILLOW_BLOCK_HALF_W` shrinks and the
  whole stack, shaft length included, moves inboard. No other number
  changes.

---

## 6. Motor bracket (printed, `parts/motor_bracket.py`)

Frame-fixed: it rides on the head bridge plate and tilts with the conveyor.

**Local frame.** Origin on the foot's underside (the bridge plate's top face)
at the head shaft station along the run and at the face plate's inboard face
across the machine. +x along the run, +y out of the plate (along the run
normal), +z outboard. Placed with
`at(t=HEAD_T, offset=-SHAFT_HEIGHT_ABOVE_PLATE, lateral=DRIVE_SIDE * FACE_PLATE_Z, incline=incline)`,
mirrored in z for `DRIVE_SIDE` = -1.

| Feature | Name | Value | |
|---|---|---|---|
| Width along the run | `BRACKET_W` | 45.0 = bridge plate width, centred on t = 354 | derived |
| Foot | `BRACKET_FOOT_T` | 6.0 thick, from local z = -19.5 (machine z 80.0) to +37.5 (z 137.0, plate edge) | provisional |
| Face plate | `FACE_PLATE_T`, `FACE_PLATE_Z` | 5.0 thick, local z 0 .. 5.0 (machine z 99.5 .. 104.5) | provisional |
| Face plate height | | from the plate top to 24.0 above the shaft axis: 48.0 + 24.0 = 72.0 | derived from `SHAFT_HEIGHT_ABOVE_PLATE` |
| Pilot bore | `BRACKET_PILOT_BORE` | 22.4 through, on the shaft axis | provisional; 0.4 clearance, tuned on the first print |
| Motor screw holes | | 4 × 3.4 on the 31.0 square, heads inboard | derived |
| Frame bolt slots | `BRACKET_SLOT_TRAVEL` | 2 × 5.5 wide, at local x = ±12.0, z = 27.5 (machine z 127), slotted ±1.5 along the run | provisional |
| Root fillet, foot to face plate, both sides | | R 5.0 | provisional |
| Cable-tie slot in the foot, outboard end | | 4 × 2, for the motor lead | provisional |
| Print orientation | | **face plate down** (its outboard face is the motor's seat); foot vertical; all holes print vertical | fixed |
| Material, mass | | PETG, about 40 g | derived |

**Alignment.** Height comes from print accuracy and
`SHAFT_HEIGHT_ABOVE_PLATE`. The run-direction slots give ±1.5 to line the
motor axis up with the shaft. The flexible coupler takes what is left. The
coupler's allowed misalignment is not published; assume 0.2 parallel until
measured.

**Assembly order.** Bolt the bracket to the plate first: the motor sits over
the two M5 heads. Then fit the motor, then the coupler.

**Dependence on the pillow blocks.** The face plate's z position and its
height are derived from `PILLOW_BLOCK_HALF_W` and `SHAFT_HEIGHT_ABOVE_PLATE`.
The bracket is reprinted once the blocks are measured. That is expected, and
it is why this part is provisional.

---

## 7. Tilt load

| Parameter | Name | Value | |
|---|---|---|---|
| Drive mass: motor + coupler + bracket + screws | `DRIVE_MASS_KG` | 0.30 + 0.02 + 0.04 + 0.01 = 0.37 → 3.6 N | derived, conservative (shipping weight) |
| Drive CG | | t = 354, offset 0 (on the head shaft axis); its z does not affect the prop | derived |
| New `TILT_WEIGHT_N` | | 34.0 + 3.6 = 37.6 | derived, still an estimate |
| New `TILT_CG_T` / `TILT_CG_OFFSET` | | 232.8 / -36.2 | derived |
| Prop force at 25°, estimate | | ≈ 113 N (was 98 N); doubled ≈ 226 N against the 250 N ceiling | to be confirmed by `checks.py` |

Add the drive to the weight as a separate term (`DRIVE_MASS_KG`, `DRIVE_CG_T`),
not by editing the 34 N, so that weighing the frame later replaces only the
estimate.

---

## 8. Acceptance checks

Each goes in `checks.py` and as a pytest test. The drive parts join the
whole-loop sweep (three take-ups × three inclines) as fixed parts.

**`params.py` assertions**

1. `HEAD_SHAFT_DRIVE_EXT ≥ PILLOW_BLOCK_HALF_W + COUPLER_BLOCK_GAP + COUPLER_ENGAGE`.
2. Engagement of each shaft in the coupler is between 10.0 and 11.0.
3. Gap between the two shaft tips inside the coupler ≥ `COUPLER_TIP_GAP_MIN`.
4. `M3 length - FACE_PLATE_T ≤ MOTOR_SCREW_MAX_ENGAGE`.
5. `DRIVE_TORQUE_AVAIL / DRIVE_TORQUE_EST ≥ 1.5`.
6. Motor body bottom (shaft axis - 21.15) above the plate top ≥ foot + M5 head height + 5.0.

**Solids**

7. Bracket: valid solid; bounding box 45.0 × 72.0 × 57.0 ± 0.5; volume 25 .. 45 cm³.
8. Points outside the bracket: pilot bore centre; the four M3 hole centres; both slot centres.
9. Point inside the bracket: the face plate at (0, 30, 2.5), local.
10. Negative control: a bracket with `BRACKET_PILOT_BORE` = 21.9 **clashes** with the motor's pilot boss (real overlap, not contact).

**Assembly, at 25°, 40° and 55°**

11. The coupler's swept cylinder (Ø20.0) is ≥ 1.5 from the pillow block (once modelled) and ≥ 2.0 from the bracket and the bridge plate.
12. No clash between motor, coupler or bracket and any slat, belt or shaft set anywhere round the loop.
13. Motor and bracket clear the base by ≥ 4.0 (expected about 225 at 25°; asserted anyway).
14. The prop-force check passes with the new weight and CG, doubled, ≤ 250 N.
15. The whole drive builds and passes checks 7 to 14 with `DRIVE_SIDE` = -1 as well.

**Output.** The bracket is exported as STL in the stated orientation. Motor
and coupler are reference solids. The head shaft goes on the cut list at
149.0. Motor, coupler, driver, cable and screws are listed by
`assembly.py --report`.

---

## 9. Physical tests

| # | Test | Settles |
|---|---|---|
| D1 | Measure the pillow block's axial width; the motor shaft length and whether it is measured from the face or the boss; the pilot boss; the coupler's bore depths and clamping type | `PILLOW_BLOCK_HALF_W`, `MOTOR_SHAFT_LEN`, `MOTOR_PILOT_*`, `COUPLER_ENGAGE`, `HEAD_SHAFT_DRIVE_FLAT` |
| D2 | Print the bracket; fit motor and coupler to the head shaft; turn by hand and check the coupler does not visibly wobble | `BRACKET_PILOT_BORE`, alignment |
| D3 | Run 60 min at 30 rpm, loaded; measure motor case temperature | `DRIVE_CURRENT_A`; target case < 60 °C |
| D4 | Pull a cleat back with a spring scale while running: the motor must skip **before** the slat moves on the belt | that the stepper protects the slats; if not, lower `DRIVE_CURRENT_A` |
| D5 | Fill the hopper and measure the current at which the belt stops skipping | replaces `DRIVE_PULL_EST_N` with a measured value |

D4 and D5 pull against each other: D5 wants enough current to run a full
hopper, D4 wants little enough that a jam does not tear a slat. If no current
satisfies both, the fallback is the slat pin from baseline §9, not a stronger
motor.

---

## 10. Open

1. `DRIVE_SIDE`: which side the motor goes, decided with the electronics and the discharge.
2. Supply voltage for the driver: 12 V assumed (the A4988 accepts 8 to 35 V).
3. Whether the exposed coupler needs a cover. It turns at 30 rpm with 0.25 N·m, so a cover is optional.
4. How the controller drives the stepper (step/direction from the sorter's main controller or a separate board): outside this spec.

---

## 11. Bill of materials (4project, prices incl. VAT, 2026-09-26)

| Part | Catalogue no. | Qty | Price |
|---|---|---|---|
| Stepper NEMA 17, 42.3 × 40, 1.7 A, JST | 4P-748700 / WS-15948 | 1 | 37.40 ₪ |
| Flexible coupler 5 × 8 | 4P-6813 | 1 | 29.90 ₪ |
| JST 6-pin adapter cable | product 6500 | 1 | check |
| A4988 stepper driver (Pololu) | product 1146 | 1 | check |
| 8 mm shaft, 149.0 cut | (existing stock) | 1 | |
| M3 × 8, M5 × 20 | | 4, 2 | |
