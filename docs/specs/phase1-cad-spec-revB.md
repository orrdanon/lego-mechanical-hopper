# Phase 1 — revision B

Supersedes `phase1-cad-spec.md`. Apply this as a **revision to the existing code**, not a
rewrite. The module structure, coordinate conventions and interfaces of rev A are all
unchanged; what changed is the parameter table, the slat's dimensions that follow from
it, and the acceptance criteria that check them.

Read §2 first. If any change there contradicts something already implemented, this
document wins.

---

## 1. Why this revision exists

Between rev A and now, the machine was re-sourced around parts actually obtainable in
Israel, and a side-view section exposed two interferences that a plan view had hidden.
Nothing in the concept changed. The numbers did.

---

## 2. Changelog

| # | Change | From | To | Reason |
|---|---|---|---|---|
| 1 | `BELT_WIDTH` | 15.0 | **9.0** | 15 mm HTD-5M is not locally stocked. Width was never a strength requirement; the belt carries about 5 N. |
| 2 | `PULLEY_FACE_WIDTH` | 9.0 | **5.0** | The overhang the saddle grips is what matters, not the belt width. Narrowing the pulley gives the same 2 mm per side. The pulley becomes a printed part. |
| 3 | `BELT_SPACING` | 100.0 | **60.0** | Frame is narrower; shorter shaft span, less deflection, better metering. |
| 4 | `SLAT_LENGTH` | 128.0 | **80.0** | Follows from `BELT_SPACING`. |
| 5 | `CLEAT_LENGTH` | 104.0 | **74.0** | Follows from `SLAT_LENGTH`, then widened to close the gap against the new side skirts. |
| 6 | Bearings | printed blocks, 608 press fit | **bought pillow blocks, 8 mm bore** | Removes the press-fit tolerance problem entirely. Printed blocks were the weakest part of rev A. |
| 7 | `SHAFT_HEIGHT_ABOVE_PLATE` | — | **48.0, new** | A side section showed the returning run's cleats striking the mounting plate. Cleat tips reach 37.3 mm from the shaft axis; a bare pillow block gives only ~25 mm. |
| 8 | Side skirts | — | **new, deferred to phase 2** | Nothing stopped bricks sliding off the sides of the belt. |
| 9 | Frame | 2020 cut to length | **existing 552 × 274 frame, uncut** | Already owned. Shafts mount on bridge plates that bolt into the T-slots. |
| 10 | `CENTRE_DIST` | fixed 390 | **derived from the belt actually bought** | T-slots give continuous positioning, so no quantisation. |

---

## 3. Revised parameter table

Complete replacement for §7 of rev A. Transcribe exactly.

### Belt and drive

| Name | Value | Unit | Note |
|---|---|---|---|
| `BELT_PROFILE` | `"HTD-5M"` | — | informational |
| `BELT_PITCH` | 5.0 | mm | |
| `BELT_LOOP_LENGTH` | 900.0 | mm | **Provisional.** Replace with the stock length actually purchased. |
| `BELT_WIDTH` | 9.0 | mm | changed |
| `BELT_THICKNESS` | 3.8 | mm | tooth tip to back |
| `BELT_PLD` | 0.5715 | mm | pitch line differential |
| `PULLEY_TEETH` | 24 | — | |
| `PULLEY_FACE_WIDTH` | 5.0 | mm | changed; printed part |
| `PULLEY_PD` | derived | mm | `PULLEY_TEETH * BELT_PITCH / pi` = 38.1972 |
| `CENTRE_DIST` | derived | mm | `(BELT_LOOP_LENGTH - pi*PULLEY_PD)/2` = 390.0 |
| `BELT_SPACING` | 60.0 | mm | changed |

### Machine

| Name | Value | Unit | Note |
|---|---|---|---|
| `INCLINE` | 40.0 | deg | |
| `SHAFT_DIA` | 8.0 | mm | |
| `SHAFT_LENGTH` | 145.0 | mm | new |
| `BEARING_SPACING` | 100.0 | mm | new; pillow block centres |
| `SHAFT_HEIGHT_ABOVE_PLATE` | 48.0 | mm | new; see changelog #7 |
| `SHAFT_SPEED` | 30.0 | rpm | 60 mm/s belt speed |

### Frame — existing, uncut

Recorded so later phases can position against it. Nothing in phase 1 uses these.

| Name | Value | Unit | Note |
|---|---|---|---|
| `FRAME_LENGTH` | 552.0 | mm | |
| `FRAME_WIDTH` | 274.0 | mm | overall |
| `FRAME_PROFILE` | 20.0 | mm | 2020 |
| `FRAME_INNER_WIDTH` | derived | mm | `FRAME_WIDTH - 2*FRAME_PROFILE` = 234.0 |
| `FRAME_SLOT_WIDTH` | 6.0 | mm | standard T-nut |

### Slat

| Name | Value | Unit | Note |
|---|---|---|---|
| `SLAT_PITCH` | 20.0 | mm | 4 belt teeth |
| `SLAT_COUNT` | derived | — | `BELT_LOOP_LENGTH / SLAT_PITCH` = 45 |
| `SLAT_LENGTH` | 80.0 | mm | changed |
| `SLAT_WIDTH` | 18.0 | mm | |
| `SLAT_THICKNESS` | 3.0 | mm | |
| `CLEAT_EVERY` | 3 | — | |
| `CLEAT_HEIGHT` | 12.0 | mm | |
| `CLEAT_WIDTH_ROOT` | 10.0 | mm | |
| `CLEAT_WIDTH_TIP` | 4.0 | mm | drafted for printing |
| `CLEAT_LENGTH` | 74.0 | mm | changed |
| `CLEAT_ROOT_FILLET` | 1.0 | mm | |

### Saddle

`SADDLE_TAB_CLEARANCE` from rev A is **deleted**. Tab positions now derive from
`BELT_WIDTH` and `SADDLE_INTERFERENCE` alone, which removes a redundant parameter that
could contradict the others.

| Name | Value | Unit | Note |
|---|---|---|---|
| `SADDLE_TAB_THICKNESS` | 2.5 | mm | |
| `SADDLE_TAB_DEPTH` | 6.0 | mm | |
| `SADDLE_TAB_LENGTH` | 12.0 | mm | |
| `SADDLE_INTERFERENCE` | 0.2 | mm | total |
| `SADDLE_LIP_PROJECTION` | 0.8 | mm | |
| `SADDLE_LIP_HEIGHT` | 1.0 | mm | |

### Skirts — recorded, not built in phase 1

| Name | Value | Unit |
|---|---|---|
| `SKIRT_HEIGHT` | 28.0 | mm above slat top |
| `SKIRT_GAP` | 1.5 | mm skirt bottom to slat top |
| `SKIRT_INSET` | 38.0 | mm from centreline |

### Printing — unchanged

`PRINT_ROT_PLAIN`, `PRINT_ROT_CLEATED` both (180, 0, 0). `EDGE_CHAMFER` 0.5.

---

## 4. Revised slat geometry

Only the numbers below changed. The construction, local frame and print orientation from
rev A §8 all stand.

### 4.1 Body

- x ∈ [−9, +9]
- y ∈ [0, 3]
- z ∈ [−40, +40]

### 4.2 Saddle

Belt centred at z = ±`BELT_SPACING`/2 = ±30, occupying z ∈ [25.5, 34.5] on the positive
side.

The two tabs of a pair have their facing surfaces `BELT_WIDTH − SADDLE_INTERFERENCE`
= 8.8 mm apart, centred on the belt centre. So on the positive side:

- **Inner tab**: z ∈ [23.1, 25.6]
- **Outer tab**: z ∈ [34.4, 36.9]
- Both: y ∈ [−6, 0], x ∈ [−6, +6]
- Retention lips as rev A, y ∈ [−6, −5], projecting 0.8 mm inward

Derive these from the parameters. The figures above are for checking your arithmetic.

Two clearances fall out and both are now asserted:

- Outer tab outer face at 36.9 leaves a 3.1 mm rim before the slat end at 40.
- Inner tab inner face at 25.6 against the pulley face edge at 27.5 gives 1.9 mm.

### 4.3 Cleat

- Trapezoid, 10 mm at the root tapering to 4 mm at the tip, `CLEAT_HEIGHT` tall
- Centred on x = 0
- z ∈ [−37, +37]

Note the cleat now extends over the outer saddle tabs. That is intentional and not a
conflict — the cleat is on the +y face, the tabs on the −y face.

---

## 5. Revised acceptance criteria

Replaces rev A §9 entirely.

### 5.1 Parameter consistency

```
assert BELT_LOOP_LENGTH % BELT_PITCH == 0
assert BELT_LOOP_LENGTH % SLAT_PITCH == 0
assert SLAT_COUNT == int(SLAT_COUNT)
assert abs(2*CENTRE_DIST + pi*PULLEY_PD - BELT_LOOP_LENGTH) < 1e-6
assert (BELT_WIDTH - PULLEY_FACE_WIDTH) / 2 >= 2.0
assert CLEAT_LENGTH < SLAT_LENGTH
assert SADDLE_TAB_LENGTH / BELT_PITCH <= 2.5
assert SLAT_WIDTH < SLAT_PITCH                      # slats must not touch
assert SLAT_PITCH - SLAT_WIDTH <= 3.0               # gap smaller than a 1x1 plate
assert BEARING_SPACING > BELT_SPACING + BELT_WIDTH
assert SHAFT_LENGTH > BEARING_SPACING + 40
```

### 5.2 The clearance that caused this revision

```
belt_back = PULLEY_PD/2 - BELT_PLD + BELT_THICKNESS      # 22.327
cleat_tip = belt_back + SLAT_THICKNESS + CLEAT_HEIGHT    # 37.327
assert SHAFT_HEIGHT_ABOVE_PLATE > cleat_tip + 5.0
```

If this fails, the returning run's cleats hit the mounting plate. It is the single most
expensive mistake available in this design, because it is invisible until assembly.

### 5.3 Saddle clearances

```
tab_inner_face = (BELT_WIDTH - SADDLE_INTERFERENCE) / 2
assert tab_inner_face - PULLEY_FACE_WIDTH/2 >= 1.5       # tab vs pulley
tab_outer_face = tab_inner_face + SADDLE_TAB_THICKNESS
assert SLAT_LENGTH/2 - (BELT_SPACING/2 + tab_outer_face) >= 2.0   # rim
```

### 5.4 Geometry module

```
assert belt_back_radius() == approx(22.327, abs=0.01)
assert slat_t(3) == approx(60.0)
assert sum(is_cleated(i) for i in range(int(SLAT_COUNT))) == 15
```

Everything else in rev A §9.2 stands unchanged.

### 5.5 Bounding box

```
assert bbox_size(slat(False)) == approx((18.0, 9.0, 80.0), abs=0.02)
assert bbox_size(slat(True))  == approx((18.0, 21.0, 80.0), abs=0.02)
```

### 5.6 Volume

```
assert 4.6 <= volume_cm3(slat(False)) <= 5.8
assert 10.2 <= volume_cm3(slat(True)) <= 12.6
assert volume_cm3(slat(True)) > volume_cm3(slat(False))
```

### 5.7 Probe points

```
s = slat(False)
assert contains(s, (0, 1.5, 0))
assert contains(s, (0, -3, 24.4))        # inner tab
assert contains(s, (0, -3, 35.6))        # outer tab
assert not contains(s, (0, -3, 30))      # saddle mouth, hollow
assert not contains(s, (0, -3, 0))
assert not contains(s, (0, 8, 0))        # no cleat on the plain variant

c = slat(True)
assert contains(c, (0, 8, 0))
assert contains(c, (0, 14, 30))
assert not contains(c, (0, 8, 39))       # cleat stops short of the end
assert not contains(c, (7, 8, 0))        # cleat is narrow in x
```

### 5.8 Clearance and validity

```
assert not clash(slat(False), pulley_envelope())
assert not clash(slat(True), pulley_envelope())
assert slat(False).is_valid()
assert slat(True).is_valid()
```

`pulley_envelope()` must be updated: radius unchanged, but length becomes
`PULLEY_FACE_WIDTH` = 5.0 and it is centred at local z = +`BELT_SPACING`/2 = +30.

---

## 6. Still out of scope

Do not build these in phase 1, even though their parameters now appear in `params.py`:

- **Bridge plate** ×2 — spans the frame's inner width, bolts into the T-slots, carries
  two pillow blocks. Tail one slotted for tensioning, head one plain.
- **Pillow block standoff** ×4 — sets `SHAFT_HEIGHT_ABOVE_PLATE`. Height depends on the
  pillow blocks actually bought; measure before modelling.
- **HTD-5M pulley**, 24 tooth, 5 mm face, 8 mm bore ×4 — real HTD tooth profile, not a
  triangular approximation.
- **Side skirt** ×2 — runs from inside the hopper to near the discharge.
- Motor mount, coupler, hopper, brush mounts.

---

## 7. Definition of done for this revision

1. `params.py` matches §3 exactly, including the deleted `SADDLE_TAB_CLEARANCE`.
2. Every assertion in §5 passes.
3. `pytest` green, `python checks.py` exits 0.
4. `export.py` writes two STLs with the new dimensions.
5. The README notes which parameters are provisional — `BELT_LOOP_LENGTH` and
   `SHAFT_HEIGHT_ABOVE_PLATE` — and why.

---

## 8. What is still a guess

`SADDLE_INTERFERENCE` at 0.2 mm has still never met a real belt. Neither has
`CLEAT_HEIGHT`. Both will change after the first test fit, and that test fit is still
the gate on phase 2. Nothing here alters that: print one plain slat and one cleated,
clip them to a scrap of 9 mm HTD-5M, and run them round a pulley twenty times before
anything else gets modelled.
