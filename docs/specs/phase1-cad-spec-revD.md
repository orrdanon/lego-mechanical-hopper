# Phase 1 — revision D

Supersedes `phase1-cad-spec-revC.md`. Like rev C, this is a diff: it lists what changes
against rev C and leaves everything else as rev B/rev C state it. Read rev A, rev B and
rev C first.

Rev D also renumbers the belt-dependent tables of `phase2-cad-spec.md`,
`phase3-cad-spec-revB.md` and `phase4-cad-spec.md` (see §6), because all three were
written against a belt that is no longer the one being used.

---

## 1. Why this revision exists

Rev C fixed the belt as the locally available HTD-5M × 9 mm × 390 mm loop and left one
thing open (rev C §8): the 135 mm centre distance that belt forces was never confirmed
against the machine layout. Phase 4 made the problem physical — five 45 mm bridge plates
cannot fit in a 135 mm run — and the decision was taken to change the belt rather than the
layout.

The belt is now an **HTD-3M × 15 mm × 828 mm** closed loop, 276 teeth
(4project.co.il, "3mm HTD pitch timing belt, 15mm width, 828mm pitch length, 276 tooth").
Finer pitch, wider, and more than twice the length. This revision follows every parameter
that depends on it.

Standard HTD-3M dimensions used below (belt thickness 2.4 mm, tooth height 1.17 mm, pitch
line differential 0.381 mm) are published catalogue figures, not measurements of this belt.
Caliper the belt when it arrives; `BELT_THICKNESS` in particular is quoted as 2.40 or 2.44
depending on the sheet.

---

## 2. Changelog

| # | Parameter | Rev C | Rev D | Reason |
|---|---|---|---|---|
| 1 | `BELT_PROFILE` | `"HTD-5M"` | **`"HTD-3M"`** | new belt |
| 2 | `BELT_PITCH` | 5.0 | **3.0** | new belt |
| 3 | `BELT_LOOP_LENGTH` | 390.0 | **828.0** | new belt, 276 teeth |
| 4 | `BELT_WIDTH` | 9.0 | **15.0** | new belt |
| 5 | `BELT_THICKNESS` | 3.8 | **2.4** | HTD-3M catalogue figure |
| 6 | `BELT_PLD` | 0.5715 | **0.381** | HTD-3M catalogue figure |
| 7 | `PULLEY_TEETH` | 24 | **40** | 40 × 3 = 24 × 5 = 120 mm: the pitch diameter (38.197) is unchanged, so the pulley envelope, belt back radius and every clearance derived from them barely move |
| 8 | `CENTRE_DIST` | 135.0 (derived) | **354.0 (derived)** | `(828 − π·38.197)/2`. Closes rev C §8 |
| 9 | `BELT_SPACING` | 60.0 | **54.0** | a 15 mm belt's outer saddle tab would end 0.1 mm from the slat end at 60 mm; 54 mm restores a 3.1 mm rim against the 2 mm minimum. Chosen over lengthening the slat so the slat, cleat and phase 2 skirt numbers all stay put |
| 10 | `SLAT_PITCH` | 15.0 (3 teeth) | **18.0 (6 teeth)** | must be a whole number of 3 mm teeth dividing 828. 18 gives 46 slats; the alternative, 12 mm, gives 69 slats with a 10 mm slat that leaves no margin around the 10 mm cleat root |
| 11 | `SLAT_WIDTH` | 13.0 | **16.0** | keeps the 2 mm inter-slat gap (rev C's rule) |
| 12 | `SLAT_COUNT` | 26 (derived) | **46 (derived)** | `828 / 18` |
| 13 | `CLEAT_EVERY` | 3 | **2** | 46 is not divisible by 3, so "every third" would put slats 45 and 0 both cleated, 18 mm apart at the seam. Every second gives 23 cleats at 36 mm and alternates cleanly across the seam |
| 14 | `SADDLE_TAB_LENGTH` | 12.0 | **7.0** | rev B §5.1's `SADDLE_TAB_LENGTH / BELT_PITCH <= 2.5` caps the tab at 7.5 mm for a 3 mm pitch |
| 15 | `FLANK_RADIUS` (phase 3) | 1.49 | **0.79** | so `TOOTH_HEIGHT = BELT_PLD + FLANK_RADIUS` = 1.171, the published HTD-3M tooth height. Still approximate; still tuned per phase 3 §7 |
| 16 | `ROOT_RADIUS` (phase 3) | 0.43 | **0.26** | scaled 3/5 from the 5M guess. Approximate |
| 17 | `FLANK_CENTRE_Y` (phase 3) | 0.5715 | **0.381** | must equal `BELT_PLD` (phase 3 rev B §3) |

Unchanged and worth saying so: `PULLEY_FACE_WIDTH` (5.0; overhang per side is now 5 mm,
still ≥ 2), `SLAT_LENGTH` (80), `SLAT_THICKNESS`, all cleat dimensions, the other saddle
dimensions, `SHAFT_HEIGHT_ABOVE_PLATE`, `BEARING_SPACING`, and everything in the frame and
plate tables.

New assertion in `params.py`: `SLAT_COUNT % CLEAT_EVERY == 0`, so the cleat pattern can
never again land unevenly on the seam.

---

## 3. Revised parameter table

Only rows that differ from rev C §3.

### Belt and drive

| Name | Value | Unit | Note |
|---|---|---|---|
| `BELT_PROFILE` | `"HTD-3M"` | — | informational |
| `BELT_PITCH` | 3.0 | mm | |
| `BELT_LOOP_LENGTH` | 828.0 | mm | 276 teeth, the belt chosen |
| `BELT_WIDTH` | 15.0 | mm | |
| `BELT_THICKNESS` | 2.4 | mm | catalogue; caliper it |
| `BELT_PLD` | 0.381 | mm | catalogue |
| `PULLEY_TEETH` | 40 | — | |
| `PULLEY_PD` | derived | mm | 38.1972, unchanged |
| `CENTRE_DIST` | derived | mm | 354.0 |
| `BELT_SPACING` | 54.0 | mm | |

### Slat

| Name | Value | Unit | Note |
|---|---|---|---|
| `SLAT_PITCH` | 18.0 | mm | 6 belt teeth |
| `SLAT_WIDTH` | 16.0 | mm | |
| `SLAT_COUNT` | derived | — | 46 |
| `CLEAT_EVERY` | 2 | — | 23 cleated slats |

### Saddle

| Name | Value | Unit | Note |
|---|---|---|---|
| `SADDLE_TAB_LENGTH` | 7.0 | mm | ≤ 2.5 teeth |

### Tooth profile (phase 3 rev B §4, renumbered)

| Name | Value | Unit | Confidence |
|---|---|---|---|
| `FLANK_RADIUS` | 0.79 | mm | approximate, tune |
| `ROOT_RADIUS` | 0.26 | mm | approximate, tune |
| `FLANK_CENTRE_Y` | 0.381 | mm | fixed, = `BELT_PLD` |
| `TOOTH_HEIGHT` | derived | mm | 1.171 |
| `LAND_WIDTH` | derived | mm | 0.914 |

---

## 4. Revised slat geometry

The saddle construction is unchanged in form. With the new numbers, each belt's tabs sit
at (for the +z belt, centred at z = 27):

- inner tab z ∈ [17.1, 19.6], outer tab z ∈ [34.4, 36.9]
- nominal gap between facing surfaces `BELT_WIDTH − SADDLE_INTERFERENCE` = 14.8 mm
- rim beyond the outer tab: 40 − 36.9 = 3.1 mm (≥ 2.0)
- tab clearance to the pulley face: 7.4 − 2.5 = 4.9 mm (≥ 1.5)
- tabs x ∈ [−3.5, +3.5]

---

## 5. Revised acceptance criteria

Every rev B §5 assertion still applies in form. Substituted numbers:

```
assert BELT_LOOP_LENGTH % BELT_PITCH == 0        # 828 % 3 == 0
assert BELT_LOOP_LENGTH % SLAT_PITCH == 0        # 828 % 18 == 0
assert SLAT_COUNT == 46
assert SLAT_COUNT % CLEAT_EVERY == 0             # new
assert belt_back_radius() == approx(21.118, abs=0.01)
assert slat_t(3) == approx(54.0)
assert is_cleated(0) and not is_cleated(1) and is_cleated(2) and not is_cleated(3)
assert sum(is_cleated(i) for i in range(SLAT_COUNT)) == 23
assert bbox_size(slat(False)) == approx((16.0, 9.0, 80.0), abs=0.02)
assert bbox_size(slat(True))  == approx((16.0, 21.0, 80.0), abs=0.02)
assert 3.9 <= volume_cm3(slat(False)) <= 4.6     # built: 4.26
assert 10.0 <= volume_cm3(slat(True)) <= 11.0    # built: 10.48
# probe points move with the tabs:
assert contains(slat(False), (0, -3, 18.35))     # inner tab
assert contains(slat(False), (0, -3, 35.65))     # outer tab
assert not contains(slat(False), (0, -3, 27))    # saddle mouth
```

Volume bands were taken from the built geometry, as in rev C, not scaled from rev C's.

Phase 4 §8.5 (plates don't collide with each other) now passes and is no longer an
expected failure: the plate pitch is 88.5 mm against a 45 mm plate.

---

## 6. Effect on later phases

- **Phase 2**: `POST_SPACING = CENTRE_DIST / 4` = 88.5 mm. Skirt numbers unchanged
  (`SLAT_LENGTH` did not move). `SKIRT_LENGTH` = 420 still overruns the 354 mm centre
  distance. Not yet built.
- **Phase 3**: profile parameters as in §3 above. The pulley is 40 teeth. The coupon and
  meshing checks are unchanged in form. Not yet built beyond parameters.
- **Phase 4**: `FRAME_T_START + FRAME_LENGTH` = 492 > `CENTRE_DIST + 60` = 414, so the
  552 mm frame is now the right length rather than four times too long. §8.5 passes.

---

## 7. What is still open

- `SHAFT_HEIGHT_ABOVE_PLATE` remains provisional (rev B §8).
- `SADDLE_INTERFERENCE`, `SADDLE_TAB_DEPTH` and `CLEAT_HEIGHT` remain unvalidated guesses
  until a printed plain + cleated slat pair is clipped to this belt. The saddle tab depth
  (6 mm) was sized around a 3.8 mm belt and now wraps a 2.4 mm one; expect it to change.
- The phase 3 profile radii are starting points for the §7 calibration coupon.

The `CENTRE_DIST` question of rev C §8 is closed.
