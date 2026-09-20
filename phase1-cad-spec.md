# Phase 1 — CAD foundation and the slat

Implementation spec for a build123d parametric model of a LEGO-sorter feed elevator.
Hand this whole document to the coding agent. It is the complete requirement for phase 1.

---

## 1. Purpose

Build the foundation of a parametric CAD project: the shared parameter module, the
geometry datum module that every future part will position itself against, export and
verification tooling, and exactly one real part — the conveyor slat, in two variants.

**Phase 1 is deliberately narrow.** The slat is the part whose dimensions are least
certain and which must be physically test-fitted before anything else is modelled. The
purpose of this phase is to produce two printable STLs and a verified geometry module,
not a machine.

### In scope

- `params.py`, `geometry.py`, `utils.py`, `export.py`, `checks.py`
- `parts/slat.py` — plain and cleated variants
- Viewer integration so any single file can be run and displayed
- A test suite that passes

### Explicitly out of scope — do not create these

- Any other part module (bearing blocks, brush mounts, hopper, motor mounts)
- An assembly module
- Joints, mates, or kinematics
- Drawings, BOM generation, or rendering
- A CLI, config files, or a package installer
- Any GUI

If a task seems to require one of these, stop and say so rather than building it.

---

## 2. Environment

- Python 3.11 or newer
- `build123d` (current release)
- `ocp_vscode` for viewing
- `pytest` for the test suite
- Nothing else. Do not add dependencies without asking.

Provide a `requirements.txt` and a short `README.md` with setup and run instructions.

---

## 3. Hard rules

1. **Units are millimetres and degrees.** Everywhere, without exception. Never introduce
   inches, metres, or radians into any public interface. Internal trig may use radians
   but must convert at the boundary.

2. **Never invent a dimension.** Every number in the model must come from `params.py`.
   If something needed to build the geometry is not in the parameter table in §7, do not
   guess a plausible value — raise `NotImplementedError` with a message naming the
   missing parameter, and list it in the README under "Missing parameters".

3. **No magic numbers in part code.** `parts/slat.py` must contain no numeric literals
   other than `0`, `1`, `2`, and small integers used for counting or indexing. Every
   dimension is a named import from `params`.

4. **Parts are functions, not module-level objects.** A part module defines a function
   that returns a `Part`. Importing the module must not build any geometry.

5. **Every part module ends with a viewer block:**
   ```python
   if __name__ == "__main__":
       from ocp_vscode import show
       show(slat(cleated=True))
   ```
   so any file can be opened and run on its own.

6. **Deterministic output.** Calling a part function twice with the same arguments must
   produce identical geometry. No randomness, no global mutable state, no caching that
   changes results.

---

## 4. Coordinate conventions

This section is the most important in the document. Get it wrong and every future part
will be modelled in its own private frame.

### 4.1 Machine frame

- **Origin** is on the tail shaft axis, at the midpoint between the two belts.
- **+X** is horizontal, pointing from the tail end toward the head end.
- **+Y** is vertically up.
- **+Z** is across the machine, completing a right-handed set (X × Y = Z).
- The machine is symmetric about the plane Z = 0.

### 4.2 The belt run

The belt centreline lies in the XY plane, inclined at `INCLINE` from +X.

- `run_dir` = (cos θ, sin θ, 0) — unit vector up the run, the direction of travel
- `run_normal` = (−sin θ, cos θ, 0) — unit vector perpendicular to the run, pointing
  **out of the carrying face** (upwards, away from the machine)

The **run parameter `t`** is the distance in mm measured along the run from the tail
shaft axis, in the `run_dir` direction. `t = 0` is the tail shaft. `t = CENTRE_DIST` is
the head shaft. Every station on the machine is identified by its `t`.

### 4.3 Radial offsets

Measured from the shaft axis outward along `run_normal`:

| Surface | Expression | Value |
|---|---|---|
| Pulley outside diameter | `PULLEY_PD/2 − BELT_PLD` | 18.527 |
| Belt tooth tips (inner face) | same | 18.527 |
| Belt back (outer, smooth face) | `PULLEY_PD/2 − BELT_PLD + BELT_THICKNESS` | 22.327 |
| Slat top surface | belt back + `SLAT_THICKNESS` | 25.327 |
| Cleat tip | slat top + `CLEAT_HEIGHT` | 37.327 |

The belt back radius is the one parts care about, because it is the surface slats sit on.

### 4.4 Slat local frame

A slat is modelled in its own frame, then placed by the assembly in a later phase.

- **Local origin** is the centre of the slat's belt-contact face, mid-span.
- **+x** is along the run, the direction of travel.
- **+y** is away from the belt, i.e. the direction the cleat points.
- **+z** is across the machine, matching machine Z.

So the slat body occupies y ∈ [0, `SLAT_THICKNESS`], the saddle tabs hang into negative
y, and the cleat rises above `SLAT_THICKNESS`.

---

## 5. File layout

```
sorter/
  README.md
  requirements.txt
  params.py
  geometry.py
  utils.py
  export.py
  checks.py
  parts/
    __init__.py
    slat.py
  tests/
    test_geometry.py
    test_slat.py
  out/            # gitignored, STL output
```

---

## 6. Module specifications

### 6.1 `params.py`

Flat module of module-level constants. No classes, no functions, no imports except
`math`. Group with comment headers in the order of §7. Derived values are computed here,
not duplicated: e.g. `PULLEY_PD = PULLEY_TEETH * BELT_PITCH / math.pi`.

Include a module docstring stating that this file is the single source of truth and that
no dimension may appear anywhere else in the project.

### 6.2 `geometry.py`

Pure functions returning geometric datums. No solids, no part imports. Depends only on
`params` and build123d's math types.

```python
def run_direction() -> Vector:
    """Unit vector along the belt run, in machine coordinates."""

def run_normal() -> Vector:
    """Unit vector perpendicular to the run, out of the carrying face."""

def belt_back_radius() -> float:
    """Distance from a shaft axis to the belt's smooth outer face, mm."""

def shaft_axis(end: str) -> Vector:
    """Point on the tail ('tail') or head ('head') shaft axis at Z = 0.
    Raises ValueError for any other value."""

def at(t: float, offset: float = 0.0, lateral: float = 0.0) -> Location:
    """A Location on the carrying run.

    t        distance along the run from the tail shaft axis, mm
    offset   distance outward from the belt back face along run_normal, mm
    lateral  distance along machine Z, mm

    The returned Location is oriented so that its local +x points along
    run_direction(), its local +y along run_normal(), and its local +z
    along machine +Z. Multiplying a part modelled in the slat local frame
    by this Location places it correctly on the belt.
    """

def slat_t(index: int) -> float:
    """Run parameter of slat `index`, counting from 0 at the tail."""

def is_cleated(index: int) -> bool:
    """True if slat `index` carries a cleat."""
```

`at()` is the function the whole project hangs off. Write its test first.

### 6.3 `utils.py`

```python
def contains(part: Part, point: tuple[float, float, float], eps: float = 0.05) -> bool:
    """True if `point` lies inside the solid. Implement by intersecting a small
    box of side 2*eps centred on the point and testing for non-zero volume."""

def volume_cm3(part: Part) -> float:
    """Volume in cubic centimetres, for readable assertions."""

def bbox_size(part: Part) -> tuple[float, float, float]:
    """Bounding box extents as (x, y, z)."""

def clash(a: Part, b: Part, tol: float = 1e-6) -> bool:
    """True if the two solids overlap by more than `tol` mm³."""
```

### 6.4 `parts/slat.py`

```python
def slat(cleated: bool = False) -> Part:
    """One conveyor slat, modelled in the slat local frame of §4.4."""

def pulley_envelope() -> Part:
    """A cylinder representing one pulley's swept volume, positioned in the
    slat local frame as it sits when the slat is at a shaft. Used only for
    clearance checking — not a manufactured part."""
```

`pulley_envelope()` exists so `checks.py` can prove the saddle clears the pulley. Build
it as a cylinder of radius `PULLEY_PD/2 − BELT_PLD`, length `PULLEY_FACE_WIDTH`, axis
along local z, centred at local (0, −belt_back_radius, +`BELT_SPACING`/2).

### 6.5 `export.py`

```python
def export_part(part: Part, name: str, print_rotation: tuple[float, float, float]) -> Path:
    """Rotate into print orientation, write out/<name>.stl, return the path."""

def export_all() -> list[Path]:
    """Export both slat variants with their print rotations from params."""
```

Print orientation is applied here and nowhere else. Parts are always modelled in their
natural frame.

### 6.6 `checks.py`

A `run_checks()` function that builds every part, runs every assertion in §9, and prints
a pass/fail line per check. It must exit non-zero on failure so it can be used as a
pre-export gate. The same assertions are also expressed as pytest tests under `tests/`;
`checks.py` is the human-facing runner, pytest is the machine-facing one.

---

## 7. Parameter table

This is the source of truth. Transcribe it into `params.py` exactly.

### Belt and drive

| Name | Value | Unit | Note |
|---|---|---|---|
| `BELT_PROFILE` | `"HTD-5M"` | — | informational |
| `BELT_PITCH` | 5.0 | mm | tooth pitch |
| `BELT_LOOP_LENGTH` | 900.0 | mm | stock closed loop, 180 teeth |
| `BELT_WIDTH` | 15.0 | mm | |
| `BELT_THICKNESS` | 3.8 | mm | tooth tip to back |
| `BELT_PLD` | 0.5715 | mm | pitch line differential, HTD-5M |
| `PULLEY_TEETH` | 24 | — | |
| `PULLEY_FACE_WIDTH` | 9.0 | mm | **narrower than the belt, deliberately** |
| `PULLEY_PD` | derived | mm | `PULLEY_TEETH * BELT_PITCH / pi` = 38.1972 |
| `CENTRE_DIST` | derived | mm | `(BELT_LOOP_LENGTH - pi*PULLEY_PD)/2` = 390.0 |
| `BELT_SPACING` | 100.0 | mm | centre to centre of the two belts |

Note that `pi * PULLEY_PD` reduces exactly to `PULLEY_TEETH * BELT_PITCH` = 120.0.
Compute it, don't hard-code 120.

### Machine

| Name | Value | Unit | Note |
|---|---|---|---|
| `INCLINE` | 40.0 | deg | from horizontal |
| `SHAFT_DIA` | 8.0 | mm | |
| `SHAFT_SPEED` | 30.0 | rpm | gives 60 mm/s belt speed |

### Slat

| Name | Value | Unit | Note |
|---|---|---|---|
| `SLAT_PITCH` | 20.0 | mm | 4 belt teeth |
| `SLAT_COUNT` | derived | — | `BELT_LOOP_LENGTH / SLAT_PITCH` = 45, assert integer |
| `SLAT_LENGTH` | 128.0 | mm | across the machine, local z |
| `SLAT_WIDTH` | 18.0 | mm | along the run, local x |
| `SLAT_THICKNESS` | 3.0 | mm | local y |
| `CLEAT_EVERY` | 3 | — | every third slat is cleated |
| `CLEAT_HEIGHT` | 12.0 | mm | above the slat top face |
| `CLEAT_WIDTH_ROOT` | 10.0 | mm | along local x, at the slat surface |
| `CLEAT_WIDTH_TIP` | 4.0 | mm | along local x, at the top — drafted for printing |
| `CLEAT_LENGTH` | 104.0 | mm | along local z, centred |
| `CLEAT_ROOT_FILLET` | 1.0 | mm | both sides |

### Saddle

| Name | Value | Unit | Note |
|---|---|---|---|
| `SADDLE_TAB_THICKNESS` | 2.5 | mm | along local z |
| `SADDLE_TAB_DEPTH` | 6.0 | mm | into negative local y |
| `SADDLE_TAB_LENGTH` | 12.0 | mm | along local x, centred |
| `SADDLE_INTERFERENCE` | 0.2 | mm | total, so nominal gap = `BELT_WIDTH - 0.2` |
| `SADDLE_LIP_PROJECTION` | 0.8 | mm | inward, at the tab tip |
| `SADDLE_LIP_HEIGHT` | 1.0 | mm | along local y |
| `SADDLE_TAB_CLEARANCE` | 0.1 | mm | between tab inner face and belt edge, per side |

### Printing

| Name | Value | Unit | Note |
|---|---|---|---|
| `PRINT_ROT_PLAIN` | (180, 0, 0) | deg | top face down, tabs up |
| `PRINT_ROT_CLEATED` | (180, 0, 0) | deg | cleat tip down, tabs up |
| `EDGE_CHAMFER` | 0.5 | mm | general outer edges |

---

## 8. Slat geometry

All coordinates in the slat local frame of §4.4. Dimensions are named parameters; the
numbers below are given only so you can check your arithmetic.

### 8.1 Body

A box spanning:

- x ∈ [−`SLAT_WIDTH`/2, +`SLAT_WIDTH`/2] → [−9, +9]
- y ∈ [0, `SLAT_THICKNESS`] → [0, 3]
- z ∈ [−`SLAT_LENGTH`/2, +`SLAT_LENGTH`/2] → [−64, +64]

Chamfer `EDGE_CHAMFER` on the four edges parallel to z on the top face, and on the two
end faces' outer edges. Do not chamfer the y = 0 face — it is the belt contact face and
must stay flat.

### 8.2 Saddle

Two saddles, mirrored about z = 0. Each grips one belt.

The belt sits centred at z = ±`BELT_SPACING`/2 = ±50, occupying a 15 mm band, so
z ∈ [42.5, 57.5] on the positive side.

Each saddle is a pair of tabs straddling that band, hanging into negative y:

- **Inner tab**: z ∈ [39.9, 42.4] — that is, `SADDLE_TAB_THICKNESS` thick, with its
  inner face `SADDLE_TAB_CLEARANCE` outside the belt edge, minus half the interference.
  Derive it; do not hard-code.
- **Outer tab**: mirrored about the belt centre, z ∈ [57.6, 60.1]
- Both: y ∈ [−`SADDLE_TAB_DEPTH`, 0] → [−6, 0]
- Both: x ∈ [−`SADDLE_TAB_LENGTH`/2, +`SADDLE_TAB_LENGTH`/2] → [−6, +6]

The nominal internal gap between the two tabs' facing surfaces must equal
`BELT_WIDTH − SADDLE_INTERFERENCE` = 14.8 mm, so the belt is gripped.

Each tab carries a **retention lip** at its tip: a `SADDLE_LIP_PROJECTION` inward
projection, `SADDLE_LIP_HEIGHT` tall, occupying y ∈ [−6, −5]. The belt snaps past these
lips and is then captured.

Note that the outer tab's outer face at z = 60.1 sits 3.9 mm inside the slat end at
z = 64, leaving a rim. That is intentional.

### 8.3 Cleat (cleated variant only)

A drafted rib running along z:

- Cross-section is a trapezoid: `CLEAT_WIDTH_ROOT` wide at y = `SLAT_THICKNESS`,
  tapering to `CLEAT_WIDTH_TIP` at y = `SLAT_THICKNESS + CLEAT_HEIGHT`
- Centred on x = 0
- z ∈ [−`CLEAT_LENGTH`/2, +`CLEAT_LENGTH`/2] → [−52, +52]
- `CLEAT_ROOT_FILLET` fillet where each flank meets the slat top face
- `EDGE_CHAMFER` on the tip edges

The draft is not decorative. It makes the part printable tip-down without support and
strengthens the root.

### 8.4 Why the pulley is narrower than the belt

`PULLEY_FACE_WIDTH` is 9 mm against a 15 mm belt, so the belt overhangs the pulley by
3 mm on each side. The saddle tabs grip exactly that overhang. If the pulley were the
full belt width there would be nowhere for the tabs to go, and the design would not
work. Any change to `BELT_WIDTH` or `PULLEY_FACE_WIDTH` must preserve at least 2 mm of
overhang per side; assert this in `checks.py`.

---

## 9. Acceptance criteria

Every one of these must pass. They are the definition of correct, not a suggestion.

### 9.1 Parameter consistency

```
assert BELT_LOOP_LENGTH % SLAT_PITCH == 0
assert SLAT_COUNT == 45
assert abs(2*CENTRE_DIST + pi*PULLEY_PD - BELT_LOOP_LENGTH) < 1e-6
assert (BELT_WIDTH - PULLEY_FACE_WIDTH) / 2 >= 2.0      # overhang per side
assert CLEAT_LENGTH < SLAT_LENGTH
assert SADDLE_TAB_LENGTH <= SLAT_WIDTH
assert SADDLE_TAB_LENGTH / BELT_PITCH <= 2.5            # grips ≤ 2.5 teeth
```

### 9.2 Geometry module

```
assert run_direction().length == approx(1.0)
assert run_normal().length == approx(1.0)
assert run_direction().dot(run_normal()) == approx(0.0, abs=1e-9)
assert belt_back_radius() == approx(22.327, abs=0.01)
assert at(0).position.Y == approx(belt_back_radius() * cos(radians(INCLINE)), abs=0.01)
assert slat_t(0) == 0.0
assert slat_t(3) == approx(60.0)
assert is_cleated(0) and not is_cleated(1) and not is_cleated(2) and is_cleated(3)
assert sum(is_cleated(i) for i in range(SLAT_COUNT)) == 15
```

### 9.3 Slat bounding box

```
plain = bbox_size(slat(False))
assert plain == approx((18.0, 9.0, 128.0), abs=0.02)

cleated = bbox_size(slat(True))
assert cleated == approx((18.0, 21.0, 128.0), abs=0.02)
```

The y extent is `SADDLE_TAB_DEPTH + SLAT_THICKNESS` for plain, plus `CLEAT_HEIGHT` for
cleated. A wrong y extent means the saddle or cleat is in the wrong place.

### 9.4 Volume

These bands catch the single most common failure, a part that came out as a solid block
because a cut silently missed.

```
assert 6.9 <= volume_cm3(slat(False)) <= 8.4
assert 15.0 <= volume_cm3(slat(True)) <= 18.0
assert volume_cm3(slat(True)) > volume_cm3(slat(False))
```

### 9.5 Probe points

```
s = slat(False)
assert contains(s, (0, 1.5, 0))           # mid body, solid
assert contains(s, (0, -3, 41.2))         # inside the inner tab
assert contains(s, (0, -3, 58.9))         # inside the outer tab
assert not contains(s, (0, -3, 50))       # saddle mouth, must be hollow
assert not contains(s, (0, -3, 0))        # no material below the body mid-span
assert not contains(s, (0, 8, 0))         # no cleat on the plain variant

c = slat(True)
assert contains(c, (0, 8, 0))             # inside the cleat
assert contains(c, (0, 14, 40))           # cleat still present near its end
assert not contains(c, (0, 8, 60))        # cleat stops short of the slat end
assert not contains(c, (7, 8, 0))         # cleat is narrow in x
```

### 9.6 Clearance

```
assert not clash(slat(False), pulley_envelope())
assert not clash(slat(True), pulley_envelope())
```

This is the check the whole design rests on. If it fails, either the tabs are too deep
or the pulley face is too wide.

### 9.7 Manifold and export

```
assert slat(False).is_valid()
assert slat(True).is_valid()
```

`export_all()` must write two STLs into `out/` and both must load without error in
`trimesh` or equivalent — but do not add trimesh as a dependency; simply assert the
files exist and are non-empty.

---

## 10. Definition of done

1. `pytest` passes with no failures and no skips.
2. `python checks.py` prints all checks passing and exits 0.
3. `python export.py` writes `out/slat_plain.stl` and `out/slat_cleated.stl`.
4. `python parts/slat.py` opens the viewer showing a cleated slat.
5. `README.md` explains setup, how to view a part, how to run checks, how to export,
   and lists any parameter that had to be raised as missing.
6. No numeric literal outside `params.py` other than 0, 1, 2 and loop indices.

---

## 11. Notes for the implementer

**Build order.** Write `params.py` first, then `geometry.py` with its tests, and only
then the slat. The geometry module is small and everything depends on it, so prove it
before building solids on top of it.

**If a fillet fails.** OCC will sometimes refuse a fillet on an edge that looks fine.
Select the edge more precisely rather than reducing the radius to zero, and if it still
fails, leave the fillet out, raise a warning, and say so in the README. Do not silently
drop it.

**Do not optimise.** Two parts is not a performance problem. Readability matters more
than speed at this stage.

**When something is ambiguous,** stop and ask rather than choosing. The dimensions here
have been reasoned through; if one of them appears to contradict another, that is a real
error worth surfacing, not something to paper over.

---

## 12. What happens next

Phase 1 output gets printed and physically test-fitted onto a real belt. Expect
`SADDLE_INTERFERENCE`, `SADDLE_TAB_DEPTH` and `CLEAT_HEIGHT` to change as a result.
Phase 2 specs the bearing blocks and the slotted tensioner against a geometry module
that by then will have been proven against reality.

Which is why phase 1 stops here.
