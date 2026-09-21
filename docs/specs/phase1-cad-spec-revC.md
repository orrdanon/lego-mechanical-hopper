# Phase 1 — revision C

Supersedes `phase1-cad-spec-revB.md`. Apply this as a **revision to the existing code**,
not a rewrite. Everything in rev B not called out below stands unchanged.

Read §2 first. If any change there contradicts something already implemented, this
document wins.

---

## 1. Why this revision exists

The belt rev B left provisional (`BELT_LOOP_LENGTH = 900.0`, "replace with the stock
length actually purchased") has been identified: a 5 mm HTD-pitch, 9 mm wide, 390 mm
pitch length, 78-tooth timing belt, locally available. Plugging its real length in
exposes two things the placeholder had been hiding:

- 78 teeth is not divisible by 4, so `SLAT_PITCH = 20` (rev B's "4 belt teeth") no
  longer divides `BELT_LOOP_LENGTH` evenly — rev B §5.1's own consistency assertion
  would fail.
- `CENTRE_DIST` derives from `BELT_LOOP_LENGTH` per rev B changelog #10. The 900 mm
  placeholder was itself back-solved to hold `CENTRE_DIST` at rev A's old fixed 390 mm.
  The real belt gives `CENTRE_DIST = 135.0` mm — under half that span.

The second point is **not resolved by this revision**. A 135 mm pulley span may be too
short a run for the hopper/discharge layout; that is a machine-layout question, not a
CAD-parameter one, and it needs a real answer before phase 2, not a guess baked into
`params.py`. This revision fixes the belt and slat numbers so the model stays internally
consistent while that layout question is open — see §8.

---

## 2. Changelog

| # | Change | From | To | Reason |
|---|---|---|---|---|
| 1 | `BELT_LOOP_LENGTH` | 900.0, provisional | **390.0** | Real stock belt identified: 78T × 5 mm pitch = 390 mm pitch length, 9 mm wide. No longer a placeholder. |
| 2 | `CENTRE_DIST` | derived, 390.0 | **derived, 135.0** | Follows from #1. Unconfirmed against the hopper/discharge layout — see §8. |
| 3 | `SLAT_PITCH` | 20.0 (4 belt teeth) | **15.0 (3 belt teeth)** | 78 teeth isn't divisible by 4; 3 teeth/slat (15 mm) divides 390 mm evenly (26 slats). See §5.1. |
| 4 | `SLAT_WIDTH` | 18.0 | **13.0** | Follows from #3: must stay under the new `SLAT_PITCH` with the same 2 mm inter-slat gap rev B used (`20 - 18 = 2`; here `15 - 13 = 2`). See `sorter/README.md` "Slat pitch and width, rev C". |
| 5 | `SLAT_COUNT` | derived, 45 | **derived, 26** | Follows from #1 and #3. |
| 6 | Cleated slat count | 15 | **9** | `sum(is_cleated(i) for i in range(26))` with `CLEAT_EVERY = 3` unchanged. |
| 7 | Slat bounding boxes | (18.0, 9.0, 80.0) / (18.0, 21.0, 80.0) | **(13.0, 9.0, 80.0) / (13.0, 21.0, 80.0)** | Follows from #4; the y and z extents don't depend on `SLAT_WIDTH`. |
| 8 | Volume ranges | 4.6–5.8 / 10.2–12.6 cm³ | **recomputed, see §5** | Follows from #4. |

Nothing else in rev B's parameter table, slat geometry, saddle, or cleat sections
changes.

---

## 3. Revised parameter table

Only the rows that changed. Everything else in rev B §3 stands.

### Belt and drive

| Name | Value | Unit | Note |
|---|---|---|---|
| `BELT_LOOP_LENGTH` | 390.0 | mm | real stock belt, no longer provisional |
| `CENTRE_DIST` | derived | mm | `(BELT_LOOP_LENGTH - pi*PULLEY_PD)/2` = 135.0 — unconfirmed against machine layout, see §8 |

### Slat

| Name | Value | Unit | Note |
|---|---|---|---|
| `SLAT_PITCH` | 15.0 | mm | changed; 3 belt teeth |
| `SLAT_COUNT` | derived | — | `BELT_LOOP_LENGTH / SLAT_PITCH` = 26 |
| `SLAT_WIDTH` | 13.0 | mm | changed; keeps the 2 mm inter-slat gap |

---

## 4. Revised slat geometry

Only the body's x-extent changes; y and z are unchanged from rev B §4.1, and the
saddle (§4.2) and cleat (§4.3) sections are unaffected since none of their dimensions
are derived from `SLAT_WIDTH` or `SLAT_PITCH`.

### 4.1 Body

- x ∈ [−6.5, +6.5]
- y ∈ [0, 3]  (unchanged)
- z ∈ [−40, +40]  (unchanged)

---

## 5. Revised acceptance criteria

Replaces the affected lines of rev B §5. Everything else in rev B §5 stands unchanged
in form; only the numbers below differ because `BELT_LOOP_LENGTH`, `SLAT_PITCH`, and
`SLAT_WIDTH` changed.

### 5.1 Parameter consistency

```
assert BELT_LOOP_LENGTH % BELT_PITCH == 0        # 390 % 5 == 0
assert BELT_LOOP_LENGTH % SLAT_PITCH == 0        # 390 % 15 == 0
assert SLAT_COUNT == 26
```

### 5.4 Geometry module

```
assert slat_t(3) == approx(45.0)         # was 60.0; 3 * SLAT_PITCH = 3 * 15
assert sum(is_cleated(i) for i in range(26)) == 9
```

### 5.5 Bounding box

```
assert bbox_size(slat(False)) == approx((13.0, 9.0, 80.0), abs=0.02)
assert bbox_size(slat(True))  == approx((13.0, 21.0, 80.0), abs=0.02)
```

### 5.6 Volume

Recompute from the built geometry at the new `SLAT_WIDTH` rather than guessing —
narrowing the body by 5 mm shrinks the body volume but leaves the saddle tabs and
cleat (which don't scale with `SLAT_WIDTH`) unchanged, so the old ranges don't simply
scale linearly. Whatever `checks.py`/`tests/` assert must be the value actually
produced by `slat()`, with headroom for print-orientation float noise as before.

### 5.7 Probe points

One probe point changes because it depended on the old half-width:

```
c = slat(True)
assert not contains(c, (6, 8, 0))        # was (7, 8, 0); 7 now falls outside the
                                          # body entirely at the new SLAT_WIDTH = 13,
                                          # which would no longer test cleat narrowness
```

All other probe points are unaffected — none of them depend on `SLAT_WIDTH` or
`SLAT_PITCH`.

---

## 6. Still out of scope

Unchanged from rev B §6.

---

## 7. Definition of done for this revision

1. `params.py` matches §3 above (all other values unchanged from rev B).
2. Every assertion in rev B §5 still passes with the numbers substituted per §5 above.
3. `pytest` green, `python checks.py` exits 0.
4. `export.py` writes two STLs at the new dimensions.
5. `sorter/README.md` records why `SLAT_WIDTH`/`SLAT_PITCH` changed (same pattern as
   its existing "Saddle tab z-positions" section) and flags the unconfirmed
   `CENTRE_DIST` per §8.

---

## 8. What is still open

`CENTRE_DIST = 135.0` mm is arithmetically consistent but **not validated against the
actual machine layout** — whether a 135 mm pulley span gives enough carrying length
between the hopper and discharge is unanswered. Unlike `SHAFT_HEIGHT_ABOVE_PLATE`
(rev B §8, provisional pending a part measurement), this isn't a missing measurement;
it's an unmade layout decision that a longer belt, an idler pulley, or a different
frame position could each resolve differently. Do not treat `CENTRE_DIST` as final
until that decision is made.

Everything rev B §8 says about `SADDLE_INTERFERENCE` and `CLEAT_HEIGHT` being
unvalidated guesses, and the physical test-fit being the real gate, still stands
unchanged.
