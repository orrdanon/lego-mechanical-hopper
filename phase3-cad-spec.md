# Phase 3 — tooth profile, belt and pulley

Depends on `phase1-cad-spec.md`, `phase1-cad-spec-revB.md` and `phase2-cad-spec.md`.
Coordinate conventions, hard rules and module structure from those apply unchanged.

---

## 1. Purpose

Build one parametric curvilinear tooth profile, then derive both the belt and the pulley
from it. Neither part gets its own independent geometry. If the profile is wrong, both
are wrong in the same way, and correcting one corrects the other.

This matters because the pulley is a printed part and the belt is bought. The only thing
guaranteeing they mesh is that the model of the bought part and the model of the printed
part come from one source.

### In scope

- `profile.py` — the tooth profile, as a solved 2D construction
- `parts/belt.py` — straight and wrapped toothed segments, plus a smooth loop for assembly
- `parts/pulley.py` — the printed pulley
- Parameter additions
- A meshing verification test

### Out of scope

Motor mount, coupler, hopper, brush, standoffs.

---

## 2. Design rule

**No point lists.** The profile is defined by named radii and lengths, joined by tangency,
and solved. Every dimension in it must be a tunable parameter, because the starting
values in §4 are approximations and will be corrected against a real belt.

**No separate pulley tooth standard.** A pulley is a cylinder with belt teeth subtracted
from its rim. There is exactly one tooth shape in this project.

---

## 3. The profile construction

### 3.1 Frame

Work in 2D. For one tooth:

- **x** runs along the belt, tooth centred on x = 0
- **y = 0** is the **land** — the flat surface between teeth, which is also the surface
  that sits on the pulley's outside diameter
- The tooth projects in **+y** for construction purposes. The belt and pulley modules
  each orient it as they need.

The construction is symmetric about x = 0, so build the half-profile for x ≥ 0 and
mirror.

### 3.2 The four arcs

Traced from the apex outward:

1. **Apex** at (0, `TOOTH_HEIGHT`).
2. **Tip arc** — radius `TIP_RADIUS`, centre (0, `TOOTH_HEIGHT` − `TIP_RADIUS`). Sweeps
   from the apex through an angle `tip_sweep` to a point P1. Convex.
3. **Flank arc** — radius `FLANK_RADIUS`, tangent to the tip arc at P1. Convex, curving
   outward and down to P2. Its centre lies on the line through the tip arc centre and P1,
   at distance `TIP_RADIUS` + `FLANK_RADIUS` from the tip arc centre.
4. **Root fillet** — radius `ROOT_RADIUS`, concave, tangent to the flank arc at P2 and
   tangent to the land at (x_root, 0). Its centre is at height `ROOT_RADIUS` and at
   distance `FLANK_RADIUS` + `ROOT_RADIUS` from the flank arc centre.
5. **Land** — straight from (x_root, 0) to (`BELT_PITCH`/2, 0).

### 3.3 The solve

`tip_sweep` is the one free variable. Everything else is fixed by the parameters, and
each choice of `tip_sweep` produces some x_root. Solve for the value that gives

```
x_root == BELT_PITCH/2 - LAND_WIDTH/2
```

x_root increases monotonically with `tip_sweep` over the useful range, so plain bisection
on `tip_sweep` ∈ (1°, 89°) converges in about 40 iterations. Write it in pure Python; do
not add a solver dependency.

```python
def solve_tip_sweep(tol: float = 1e-9) -> float:
    """Bisect for the tip sweep angle, in degrees, that puts the root
    fillet's land tangency at BELT_PITCH/2 - LAND_WIDTH/2.
    Raises ValueError if the parameters admit no solution — which means
    the tooth is geometrically impossible, not that the solver failed."""
```

That last point matters. If someone sets `TOOTH_HEIGHT` larger than
`FLANK_RADIUS` allows, there is no valid tooth and the right behaviour is a clear
exception naming the offending parameter, not a silently degenerate face.

### 3.4 Interface

```python
def tooth_half() -> list[Edge]:
    """The four arcs and the land, x >= 0, in the profile frame."""

def tooth_profile(clearance: float = 0.0) -> Face:
    """One full tooth plus its two half-lands, spanning x in
    [-BELT_PITCH/2, +BELT_PITCH/2]. `clearance` offsets the tooth outline
    outward by that amount, leaving the land untouched — used by the pulley
    to cut a groove slightly larger than the tooth."""

def tooth_width_at(y: float) -> float:
    """Full width of the tooth at height y. Used by the checks."""
```

---

## 4. Parameter additions

### Tooth profile — HTD-5M

| Name | Value | Unit | Confidence |
|---|---|---|---|
| `TOOTH_HEIGHT` | 2.06 | mm | good |
| `TIP_RADIUS` | 0.43 | mm | **approximate, tune** |
| `FLANK_RADIUS` | 1.49 | mm | **approximate, tune** |
| `ROOT_RADIUS` | 0.43 | mm | **approximate, tune** |
| `LAND_WIDTH` | 1.20 | mm | **approximate, tune** |
| `GROOVE_CLEARANCE` | 0.10 | mm | tune on the printer |

The four marked values are a starting shape, not a specification. They produce a tooth of
the right family and roughly the right proportions. §7 is how they get corrected.

### Pulley

| Name | Value | Unit | Note |
|---|---|---|---|
| `PULLEY_OD` | derived | mm | `PULLEY_PD - 2*BELT_PLD` = 37.054 |
| `PULLEY_BORE` | 8.0 | mm | |
| `PULLEY_BORE_CLEARANCE` | 0.15 | mm | printed hole runs undersize |
| `PULLEY_HUB_DIA` | 22.0 | mm | |
| `PULLEY_HUB_LENGTH` | 10.0 | mm | beyond the toothed face |
| `PULLEY_GRUB_M` | 4.0 | mm | M4, into a heat-set insert |
| `PULLEY_INSERT_DIA` | 5.6 | mm | |
| `PULLEY_INSERT_DEPTH` | 8.0 | mm | |

### Belt

| Name | Value | Unit | Note |
|---|---|---|---|
| `BELT_BACK_THICKNESS` | derived | mm | `BELT_THICKNESS - TOOTH_HEIGHT` = 1.74 |

Assert that `BELT_PLD` < `BELT_BACK_THICKNESS`, i.e. the pitch line falls inside the
belt's backing. If it doesn't, one of the two is wrong.

---

## 5. Parts

### 5.1 `parts/pulley.py`

```python
def pulley(teeth: int = PULLEY_TEETH,
           face: float = PULLEY_FACE_WIDTH,
           bore: float = PULLEY_BORE) -> Part:
```

Construction:

1. Cylinder, diameter `PULLEY_OD`, length `face`.
2. For each of `teeth` positions at 360/`teeth`° apart: take
   `tooth_profile(clearance=GROOVE_CLEARANCE)`, place it so its **land lies on the OD
   circle** and its tooth points inward (toward the axis), extrude through the face, and
   subtract.
3. Hub: cylinder `PULLEY_HUB_DIA` × `PULLEY_HUB_LENGTH` on one end face.
4. Bore: `bore` + `PULLEY_BORE_CLEARANCE` through everything.
5. Grub screw: radial hole through the hub for the insert, `PULLEY_INSERT_DIA` ×
   `PULLEY_INSERT_DEPTH`, then `PULLEY_GRUB_M` clearance the rest of the way to the bore.
6. 0.4 mm chamfer on both ends of the bore.

**No flanges.** They are geometrically impossible here — the only free space beside the
pulley is where the saddle tabs grip the belt overhang, and a flange there would have to
grow up through the belt. This is a hard constraint of the design, not an omission.

Print orientation: hub end down, axis vertical. Teeth print as vertical walls.

### 5.2 `parts/belt.py`

```python
def belt_segment(teeth: int, width: float = BELT_WIDTH) -> Part:
    """Straight toothed segment, teeth pointing in -y, land at y=0,
    back face at y = BELT_BACK_THICKNESS. Length = teeth * BELT_PITCH."""

def belt_wrapped(teeth: int, pulley_teeth: int = PULLEY_TEETH) -> Part:
    """The same teeth, arranged radially around a pulley's pitch circle as
    they sit when meshed. For the meshing check only."""

def belt_loop() -> Part:
    """The full closed loop as a smooth band with NO teeth — two straights
    and two half-circles, at the belt's radial offsets. For assembly views
    and for clash checks against slats and skirts."""
```

`belt_loop()` is deliberately untoothed. Forty-five slats plus 180 belt teeth will make
the viewer unusable, and nothing in the assembly depends on tooth geometry.

---

## 6. Acceptance criteria

### 6.1 Profile sanity

```
assert 0 < solve_tip_sweep() < 90
prof = tooth_profile()
assert prof.is_valid()
assert bbox_size(prof)[0] == approx(BELT_PITCH, abs=1e-6)
assert bbox_size(prof)[1] == approx(TOOTH_HEIGHT, abs=1e-6)
assert 2.0 <= tooth_width_at(0.2) <= 3.6          # near the root
assert tooth_width_at(TOOTH_HEIGHT - 0.05) < 1.0  # near the tip
assert tooth_width_at(0.2) > tooth_width_at(1.5)  # monotonic taper
```

The width band is loose on purpose. It catches a profile that came out as a spike or a
rectangle, which is what a broken tangency solve produces, without pretending to know the
exact HTD figure.

### 6.2 Tangency

Walk the half-profile's edges and check that consecutive edges share an endpoint and that
their tangent directions there agree:

```
for e1, e2 in zip(edges, edges[1:]):
    assert (e1 @ 1 - e2 @ 0).length < 1e-6
    assert (e1 % 1).get_angle(e2 % 0) < 0.5      # degrees
```

A curvilinear profile with a kink in it is the most likely failure mode of this
construction, and it is invisible in the viewer at this scale.

### 6.3 Pulley

```
p = pulley()
assert p.is_valid()
assert bbox_size(p)[0] == approx(PULLEY_OD, abs=0.02)
assert bbox_size(p)[2] == approx(PULLEY_FACE_WIDTH + PULLEY_HUB_LENGTH, abs=0.02)

plain = Cylinder(PULLEY_OD/2, PULLEY_FACE_WIDTH).volume
assert 0.72 * plain < pulley_toothed_section_volume() < 0.92 * plain
```

That volume band is the check that the grooves were actually cut. A pulley that came out
as a plain cylinder passes every dimensional test and fails this one.

### 6.4 Meshing — the check this phase exists for

```
belt = belt_wrapped(teeth=6)
pul  = pulley()

# with clearance, they must not interfere
assert not clash(belt, pul)

# with zero clearance, they must touch — otherwise the tooth is simply
# too small and "no clash" proves nothing
tight = pulley_with(clearance=0.0)
assert clash(belt, tight)
```

The second assertion is the important one. It is easy to write a profile that passes a
clash test because the teeth are far too small for the grooves, and that pulley would
ratchet immediately. Proving that zero clearance *does* interfere proves the tooth fills
the groove.

### 6.5 Pitch accuracy

```
# tooth tip positions around the pulley, measured on the pitch circle
for i in range(PULLEY_TEETH):
    assert angular_position(i) == approx(i * 360/PULLEY_TEETH, abs=1e-9)
assert pi * PULLEY_PD == approx(PULLEY_TEETH * BELT_PITCH, abs=1e-9)
```

Profile shape is forgiving; pitch is not. A tooth shape 0.2 mm off will still run. A
pitch 0.2 mm off accumulates over 24 teeth and will not.

---

## 7. Calibration, once the belt arrives

The four approximate parameters get corrected empirically, in this order.

1. Print a **flat coupon**: a 40 mm bar with five grooves cut by the same
   `tooth_profile()`, at the same `GROOVE_CLEARANCE`. Ten minutes on the printer.
2. Press a scrap of real belt into it. You are looking for full seating with no rocking
   and no force needed.
3. If the belt sits proud, the grooves are too shallow — raise `TOOTH_HEIGHT`.
4. If it rocks side to side, the grooves are too wide — reduce `GROOVE_CLEARANCE` first,
   then `LAND_WIDTH`.
5. If it binds at the tooth tips, raise `ROOT_RADIUS`.
6. If it binds at the flanks partway down, adjust `FLANK_RADIUS`.

Reprint the coupon after each change. Only when a coupon seats cleanly should the four
real pulleys be printed.

Record the final values in the README with the date and a note that they were measured
rather than derived. Future-you will want to know which numbers came from a standard and
which came from a caliper.

---

## 8. Definition of done

1. All phase 1 and phase 2 assertions still pass.
2. All §6 assertions pass, including both halves of the meshing test.
3. `python parts/pulley.py` shows a pulley in the viewer with visibly curved,
   non-triangular grooves.
4. `python parts/belt.py` shows a six-tooth wrapped segment sitting in a pulley.
5. `export.py` writes `out/pulley_24t.stl` and `out/tooth_coupon.stl`.
6. The README lists the four approximate parameters under "to be calibrated", with §7 as
   the procedure.

---

## 9. Note

Nothing in this phase can be verified against reality until a belt exists. Everything
here is internally consistent — the belt model and the pulley model agree with each other
because they come from one profile — but both could be uniformly wrong. The coupon in §7
is what turns internal consistency into correctness, and it costs ten minutes.
