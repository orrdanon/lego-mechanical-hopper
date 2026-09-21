# Phase 3 — revision B

Supersedes `phase3-cad-spec.md`. Apply this as a **revision to the spec**, not a
rewrite — nothing has been implemented against phase 3 yet, so there is no code to
migrate, but the diff format is kept anyway for consistency with how phase 1's
revisions are recorded (`phase1-cad-spec.md` → `phase1-cad-spec-revB.md`).

Everything in phase3-cad-spec.md not touched below stands unchanged: the purpose
(§1), the design rule (§2), the frame (§3.1), the pulley/belt part specs (§5) other
than the pulley-groove construction note in §5.1, the calibration procedure (§7),
and the definition of done (§8).

Read §2 first. Where this document's construction contradicts §3 of the base
document, this document wins.

---

## 1. Why this revision exists

A review of the base spec's tooth profile came back before any code was written
against it. The four-arc construction (apex, a separate tip arc, a flank arc
tangent to it, a root fillet — solved by bisecting `tip_sweep` until the root
fillet lands the land tangency at the right x) works, but for the actual HTD-5M
numbers involved the tip arc's sweep comes out small enough that it isn't buying
anything: the same tooth family is produced by a strictly simpler construction
with no iteration at all.

Dropping the tip arc also removes the one piece of numerical machinery
(`solve_tip_sweep`'s bisection) from what is otherwise a closed-form module, and
it surfaces a consistency check that the four-arc version had no natural place
for: the flank arc's centre height above the land is the same physical offset as
`BELT_PLD`, the belt's own pitch-line differential. Making that identity an
explicit assertion means the profile and the belt geometry can't quietly drift
apart from each other.

---

## 2. Changelog

| # | Change | From | To | Reason |
|---|---|---|---|---|
| 1 | Tooth construction | 4 arcs (apex, tip, flank, root fillet), solved by bisection | **3 edges (land, root fillet, flank-to-apex), closed-form** | Tip arc's contribution is negligible at real HTD-5M dimensions; no iteration needed. |
| 2 | `TIP_RADIUS` | 0.43 mm | **deleted** | No longer a construction input. |
| 3 | `solve_tip_sweep()` | bisection, `tip_sweep ∈ (1°,89°)` | **deleted** | Nothing left to solve for. |
| 4 | `FLANK_CENTRE_Y` | — | **0.5715 mm, new** | Height of the flank arc's centre above the land. Physically the same offset as `BELT_PLD`; see §3. |
| 5 | `TOOTH_HEIGHT` | 2.06 mm, input | **derived: `FLANK_CENTRE_Y + FLANK_RADIUS`** = 2.0615 | No longer independent of the arc geometry — it falls out of it. |
| 6 | `LAND_WIDTH` | 1.20 mm, input | **derived**, see §3 formula, = 1.17 | Same reasoning as `TOOTH_HEIGHT`. |
| 7 | §6.2 tangency check | walks all 3 joints across 4 edges | **walks the 2 flank-to-fillet joints only** | Land-to-fillet tangency is now guaranteed algebraically by construction (a circle of radius R centred at height R is automatically tangent to y=0); testing it adds nothing. The flank-to-fillet joint is the one actually determined by the solve, on each mirrored side. |

`GROOVE_CLEARANCE` is unchanged. The pulley groove construction in §5.1 of the base
document is unchanged in substance — it still subtracts `tooth_profile(clearance=
GROOVE_CLEARANCE)`, the same one tooth shape used by the belt, per §2's "no separate
pulley tooth standard" rule. It is simply cheaper to build now, since the profile
it's built from has one fewer edge.

---

## 3. Revised construction

Frame and symmetry (base document §3.1) are unchanged: 2D, x along the belt,
tooth centred on x=0, y=0 is the land, tooth projects in +y, build the half-profile
for x ≥ 0 and mirror.

Traced from the land outward to the apex:

1. **Land** — straight, from (`BELT_PITCH`/2, 0) to (`x_root`, 0).
2. **Root fillet** — radius `ROOT_RADIUS`, concave, tangent to the land at
   (`x_root`, 0) and tangent to the flank arc at P1. Its centre is at height
   `ROOT_RADIUS`, at distance `FLANK_RADIUS + ROOT_RADIUS` from the flank arc's
   centre — this is the same external-tangency relation the base document used,
   just written the other direction.
3. **Flank arc** — radius `FLANK_RADIUS`, centre at (0, `FLANK_CENTRE_Y`), on the
   tooth centreline. Convex. Runs from P1 up to the **apex** at
   (0, `TOOTH_HEIGHT`), which is the flank arc's own topmost point — its tangent
   there is horizontal by construction, so the crown is smooth without a separate
   tip arc.

### The solve — there isn't one

Given the flank arc's centre and radius are both fixed parameters, `x_root` and
P1 fall straight out of the tangency condition, with no bisection:

```
x_root = sqrt((FLANK_RADIUS + ROOT_RADIUS)**2 - (ROOT_RADIUS - FLANK_CENTRE_Y)**2)
```

(root fillet centre at `(x_root, ROOT_RADIUS)`; tangent to the land directly below
its own centre, at x = `x_root`). P1 is the point at distance `FLANK_RADIUS` from
the flank centre, on the line through the flank centre and the root fillet centre.

This requires `(FLANK_RADIUS + ROOT_RADIUS)**2 >= (ROOT_RADIUS - FLANK_CENTRE_Y)**2`
for a real solution to exist — same spirit as the base document's "geometrically
impossible tooth" case, just checked directly instead of by a failed bisection.
`tooth_half()` (interface unchanged from the base document, still returns
`list[Edge]`) should raise `ValueError` naming the offending parameters if it
doesn't hold.

### `FLANK_CENTRE_Y` and `BELT_PLD` are the same quantity

`FLANK_CENTRE_Y` = 0.5715 mm and `BELT_PLD` = 0.5715 mm (already in `params.py`)
are not a coincidence — the flank arc's centre height above the land, and the
belt's pitch-line differential, are the same physical offset by definition of
what "pitch line" means for a curvilinear timing profile. `params.py` must assert
this directly:

```python
assert FLANK_CENTRE_Y == BELT_PLD
```

**This must stay an exact equality, not a tolerance.** If it ever fires, the
profile and the belt geometry have drifted apart from each other — that is a real
bug to find, not noise to average out. Do not "fix" a failure here by loosening
the assertion.

### Derived values

```
TOOTH_HEIGHT = FLANK_CENTRE_Y + FLANK_RADIUS
LAND_WIDTH   = BELT_PITCH - 2 * x_root
             = BELT_PITCH - 2*sqrt((FLANK_RADIUS+ROOT_RADIUS)**2 - (ROOT_RADIUS-FLANK_CENTRE_Y)**2)
```

With `FLANK_RADIUS = 1.49`, `ROOT_RADIUS = 0.43`, `FLANK_CENTRE_Y = 0.5715`:
`TOOTH_HEIGHT` = 2.0615 (assert within 0.01 of the published 2.06),
`LAND_WIDTH` = 1.17.

### Interface

Unchanged from the base document's §3.4:

```python
def tooth_half() -> list[Edge]:
    """Land, root fillet, flank-to-apex, x >= 0, in the profile frame."""

def tooth_profile(clearance: float = 0.0) -> Face:
    """One full tooth plus its two half-lands, spanning x in
    [-BELT_PITCH/2, +BELT_PITCH/2]. `clearance` offsets the flank and root
    fillet outward by that amount; the land is left untouched."""

def tooth_width_at(y: float) -> float:
    """Full width of the tooth at height y. Used by the checks."""
```

---

## 4. Revised parameters

Replaces the "Tooth profile — HTD-5M" table in base document §4.

| Name | Value | Unit | Confidence |
|---|---|---|---|
| `FLANK_RADIUS` | 1.49 | mm | **approximate, tune** |
| `ROOT_RADIUS` | 0.43 | mm | **approximate, tune** |
| `FLANK_CENTRE_Y` | 0.5715 | mm | fixed — must equal `BELT_PLD`, see §3 |
| `TOOTH_HEIGHT` | derived | mm | `FLANK_CENTRE_Y + FLANK_RADIUS` = 2.0615 |
| `LAND_WIDTH` | derived | mm | see §3 formula = 1.17 |
| `GROOVE_CLEARANCE` | 0.10 | mm | tune on the printer, unchanged |

`TIP_RADIUS` no longer exists. The three marked values that remain approximate
(`FLANK_RADIUS`, `ROOT_RADIUS`, and by extension the two values derived from them)
go through the same §7 calibration procedure as before — it is unaffected by this
revision, since it calibrates against a printed coupon and a real belt, not
against the construction method.

The Pulley and Belt parameter tables in base document §4 are unchanged.

---

## 5. Revised acceptance criteria

Replaces §6.1 and §6.2 of the base document. §6.3, §6.4, §6.5 are unchanged.

### 5.1 Profile sanity (replaces §6.1)

```
prof = tooth_profile()
assert prof.is_valid()
assert bbox_size(prof)[0] == approx(BELT_PITCH, abs=1e-6)
assert bbox_size(prof)[1] == approx(TOOTH_HEIGHT, abs=1e-6)
assert 2.0 <= tooth_width_at(0.2) <= 3.6          # near the root
assert tooth_width_at(TOOTH_HEIGHT - 0.05) < 1.0  # near the tip
assert tooth_width_at(0.2) > tooth_width_at(1.5)  # monotonic taper
```

Same bands as the base document — they were chosen to catch a broken tangency
solve, not to encode the exact HTD figure, and that's equally true of this
construction.

### 5.2 Tangency (replaces §6.2)

Only the two flank-to-fillet joints (one per mirrored side) are checked — see
changelog #7 for why the land-to-fillet joint is skipped:

```
for e1, e2 in flank_fillet_joints(edges):   # 2 joints, not 3
    assert (e1 @ 1 - e2 @ 0).length < 1e-6
    assert (e1 % 1).get_angle(e2 % 0) < 0.5      # degrees
```

---

## 6. Definition of done for this revision

Same as base document §8, with "profile sanity" and "tangency" read as this
document's §5.1/§5.2, and with no `solve_tip_sweep` reference anywhere in the
implementation or its tests.
