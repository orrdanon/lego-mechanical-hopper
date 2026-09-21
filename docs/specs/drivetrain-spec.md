# Drivetrain: tooth profile, belt, shaft set and shafts

Written against `design-baseline.md` at commit `98f4fb1`. That document is the
reference; this one changes it only where stated, and every change is listed in
§3 with its reason.

All dimensions millimetres and degrees. Status labels as in the baseline:
**fixed**, **catalogue**, **provisional**, **open**.

**Revision B.** The pulley groove is now the published HTD-3M groove for
40 teeth, rebuilt parametrically from a manufacturer model, instead of the belt
tooth grown by a clearance. Rev A's approach was wrong: the belt is made to
mesh with standard grooves, and the belt-tooth radii were only an
approximation. Affected: §1, §2 (decisions 1 and 2), §3, §4, §5.4, §10, §12.1,
§12.3, §12.4, §13, §14. Everything else is unchanged from rev A.

---

## 0. Read first: a correction to the baseline

**`belt_back_radius()` is 1.171 mm too large.** It currently evaluates

```
PULLEY_PD/2 - BELT_PLD + BELT_THICKNESS  =  19.099 - 0.381 + 2.4  =  21.118
```

That places the belt's **tooth tips** on the pulley OD. Physically it is the
belt's **land** — the flat between its teeth — that rests on the pulley OD, and
the teeth sit down inside the pulley's grooves. The correct expression is

```
PULLEY_OD/2 + BELT_BACK_THICKNESS  =  18.718 + 1.229  =  19.947
```

The error is one tooth height, and it originated in the phase 1 spec, not in the
implementation. It does not touch the slat's own geometry, which lives in its
local frame. It moves every radial station in baseline §2:

| Surface | Baseline | Corrected |
|---|---|---|
| Pulley groove bottom (standard, rev B) | (not listed) | 17.501 |
| Belt tooth tips | (not listed) | 17.547 |
| Pulley OD / belt land | 18.718 | 18.718 |
| Belt pitch line | 19.099 | 19.099 |
| **Belt back = slat contact face** | 21.118 | **19.947** |
| Slat top face | 24.118 | 22.947 |
| Cleat tip | 36.118 | 34.947 |
| Saddle tab tips, current 6.0 depth | 15.118 | 13.947 |

Two consequences worth stating plainly:

- The returning-run clearance to the bridge plates **improves**, from 11.9 to
  13.05.
- The radial envelope beside each pulley **shrinks**. The tabs reach 1.171
  closer to the axis than the baseline believes. The 22 mm hub the baseline
  proposes would clear them by 2.9, not 4.1. §6.2 recovers this.

The implemented slat-vs-pulley clash check still passes, because the tabs lie
outside the 5 mm pulley face in z. It passes for the right reason by accident.
Fix the formula before anything in this spec is built on it, and add the
assertion in §12.1 so it cannot regress.

---

## 1. Scope

### Builds

- `profile.py` — the belt tooth (for the belt model) and the standard pulley
  groove (for the pulley), as two separate constructions
- `parts/shaft_set.py` — **one printed part per shaft**: both pulleys and a
  central guide wheel. Replaces the four separate pulleys.
- `parts/shaft.py` — reference solid for the bought 8 mm shaft
- `parts/belt.py` — reference solids for the belt
- `parts/coupons.py` — two calibration coupons
- `reference/htd3m_40t_40015040.stp` — manufacturer model, stored unmodified
- Two changes to `parts/slat.py`: a guide lug, and a shallower saddle
- `geometry.py` additions, notably `loop_at(s)`
- Three new assembly groups: `drivetrain`, `belts`, `slats`

### Does not build

Pillow blocks, standoffs, motor mount, coupler, tensioning jack, skirts, hopper.
Pillow blocks in particular stay unmodelled until the real ones are measured.

---

## 2. Decisions on the baseline's open questions

| # | Question | Decision | § |
|---|---|---|---|
| 1 | Tooth form, and groove form | **Two constructions.** The pulley groove is the **standard HTD-3M groove for 40 teeth**, rebuilt from dimensions read out of a manufacturer model. The single-flank-arc belt tooth is kept for the belt reference solid only, and is checked against the groove, never the other way round. | 4 |
| 2 | Printed tolerances | The standard groove already contains the designed running clearance, so the only tuning left is **printer compensation**: a uniform offset on the groove and an OD correction, both fixed by one ring coupon before a pulley is printed. | 4, 10, 13 |
| 3 | Tracking without flanges | **Add a V-guide.** A lug on every slat runs in a grooved wheel on each shaft. The slats stay the only lateral constraint on the belts; the guide becomes the only lateral constraint on the slats. | 5.5, 6.1 |
| 4 | Tensioning | The **tail bridge plate slides** in its T-slots. That is the take-up. Travel is checked here; the jacking screw is a later part. | 9.3 |
| 5 | Tail pulleys | **Toothed, fixed to a rotating tail shaft.** Identical to the head. | 5.1 |
| 6 | Shaft fixing and phase | Both pulleys on a shaft are **one printed part**, so they are in phase by construction. Fixed by two M4 grub screws onto a filed flat. | 5.6 |
| 7 | Hub design | The hub becomes a **drum** between the pulleys and the guide wheel, 26 mm, sized against the corrected tab radius. | 5.3 |
| 8 | Saddle on the 2.4 mm belt | **Reduce tab depth from 6.0 to 3.6** so the lips actually sit under the belt. This changes the slat. | 6.2 |
| 9 | Chordal effects | Benign for the belt: the slat never presses on its back. The real risk is slow **creep** of slats along the belt; it gets a physical test and a named fallback. | 13 |
| 10 | Belt model fidelity | Smooth backing band for the assembly; short toothed segments for mesh checks; full toothed loop only behind the detail flag. | 8 |

---

## 3. Parameter changes

### 3.1 Corrected

| Name | Was | Now |
|---|---|---|
| `belt_back_radius()` | `PULLEY_PD/2 - BELT_PLD + BELT_THICKNESS` | `PULLEY_OD/2 + BELT_BACK_THICKNESS` |

### 3.2 Changed

| Name | Was | Now | Status | Reason |
|---|---|---|---|---|
| `SADDLE_TAB_DEPTH` | 6.0 | **3.6** | provisional | = belt 2.4 + 0.2 gap + lip 1.0. The lips now retain the belt instead of sitting 2.6 below it. |
| `FLANK_RADIUS`, `ROOT_RADIUS` | shape both belt and groove | **shape the belt model only** | provisional | They no longer affect anything printed. Tune them only if the belt model disagrees with the standard groove in §12.4. |

### 3.3 New

**Standard pulley groove.** Read from CADENAS model 40015040, a 40-tooth
HTD-3M pulley; see §4.2. **Valid for 40 teeth only** — the standard groove
varies with tooth count. The `PULLEY_GROOVE_` prefix keeps these apart from
the guide groove's clearances below.

| Name | Value | Status | Note |
|---|---|---|---|
| `PULLEY_GROOVE_BOTTOM_R` | 17.501 | catalogue | bottom arc radius, about the pulley axis |
| `PULLEY_GROOVE_FLANK_R` | 0.700 | catalogue | concave flank arc |
| `PULLEY_GROOVE_FLANK_U` | 0.2476 | catalogue | flank arc centre, tangential offset from the groove centreline |
| `PULLEY_GROOVE_TIP_R` | 0.191 | catalogue | convex tip radius onto the OD land |
| `PULLEY_GROOVE_TIP_U` | 1.1883 | catalogue | tip arc centre, tangential offset |
| `PULLEY_GROOVE_DEPTH` | derived | | `PULLEY_OD/2 − PULLEY_GROOVE_BOTTOM_R` = 1.2165 (file: 1.219, from its rounded OD) |
| `PULLEY_GROOVE_PHASE` | 4.5 | fixed | degrees; first groove centre from local +y, so a land lies on +y |

**Printer compensation**

| Name | Value | Status | Note |
|---|---|---|---|
| `PULLEY_GROOVE_COMP` | 0.0 | provisional | uniform outward offset of every groove edge, set from the ring coupon |
| `PULLEY_OD_COMP` | 0.0 | provisional | subtracted from the modelled OD, set from the ring coupon |

**Shaft set envelope** — all are radii or z positions in the shaft set's local
frame (§5.2), mirrored about z = 0.

| Name | Value | Status | Note |
|---|---|---|---|
| `SHAFTSET_LENGTH` | derived | | `2*(BELT_SPACING/2 + PULLEY_FACE_WIDTH/2)` = 59.0 |
| `DRUM_DIA` | 26.0 | provisional | replaces `PULLEY_HUB_DIA` |
| `DRUM_TAB_CLEAR` | 1.0 | fixed | minimum radial running clearance, drum to tab tip |
| `PULLEY_SKIRT_R` | 16.8 | provisional | radius the drum flares to under the pulley face |
| `BELT_TOOTH_CLEAR` | 0.5 | fixed | minimum, flare to overhanging belt teeth |
| `END_CHAMFER` | 0.3 | fixed | on both end faces, against elephant's foot |

**Guide**

| Name | Value | Status | Note |
|---|---|---|---|
| `LUG_DEPTH` | 4.0 | provisional | below the slat contact face |
| `LUG_TIP_WIDTH` | 3.0 | provisional | across the machine |
| `LUG_ANGLE` | 90.0 | fixed | included; see §5.5 for why not 40 |
| `LUG_TOP_WIDTH` | derived | | `LUG_TIP_WIDTH + 2*LUG_DEPTH*tan(LUG_ANGLE/2)` = 11.0 |
| `LUG_LENGTH` | 8.0 | provisional | along the run, centred on the slat |
| `LUG_END_CHAMFER` | 1.0 | fixed | leading and trailing ends, for groove entry |
| `GUIDE_WIDTH` | 16.0 | provisional | wheel face, across the machine |
| `GUIDE_RIM_GAP` | 0.5 | fixed | rim radius = belt back − this = 19.447 |
| `GROOVE_FLANK_CLEAR` | 0.5 | provisional | normal to each flank |
| `GROOVE_TIP_CLEAR` | 1.5 | fixed | below the lug tip; the lug never bottoms |

**Fixing**

| Name | Value | Status | Note |
|---|---|---|---|
| `GRUB_Z` | 17.5 | provisional | ±, the two grub screw planes |
| `PULLEY_INSERT_DEPTH` | **6.0** | provisional | was 8.0; see §5.6 |
| `SHAFT_FLAT_DEPTH` | 0.5 | fixed | filed on the shaft |
| `SHAFT_FLAT_LENGTH` | 45.0 | fixed | centred on the shaft set |

**Take-up**

| Name | Value | Status | Note |
|---|---|---|---|
| `TAIL_TAKEUP_MIN` | −4.0 | provisional | tail plate toward the head, for fitting the belt |
| `TAIL_TAKEUP_MAX` | 2.0 | provisional | away from the head, for tension and belt tolerance |

### 3.4 Removed

`PULLEY_HUB_DIA`, `PULLEY_HUB_LENGTH`. The hub is replaced by the drum.

`GROOVE_CLEARANCE`, and with it `COUPON_LENGTH` and `COUPON_GROOVE_COUNT`.
Its old meaning — a clearance added to the belt tooth to make a groove — no
longer exists, and reusing the name for printer compensation would invite
exactly the confusion that caused rev A. `PULLEY_GROOVE_COMP` replaces it.

---

## 4. `profile.py` — belt tooth and pulley groove

Two constructions, deliberately separate. The pulley groove is a published
standard and is the part that must work. The belt tooth is an approximation,
used only for the belt reference solid, and is checked against the groove.

### 4.1 Belt tooth — for the belt model only

Unchanged from the baseline's §5 and closed-form. In a 2D frame with the land
on y = 0 and the tooth rising in +y:

- **Flank arc** — radius `FLANK_RADIUS`, centre (0, `FLANK_CENTRE_Y`). Reaches
  the apex at (0, `TOOTH_HEIGHT`) directly.
- **Root fillets** — radius `ROOT_RADIUS`, concave, tangent to the flank arc
  and to the land, centres at (±x_f, `ROOT_RADIUS`) where
  `x_f = sqrt((FLANK_RADIUS + ROOT_RADIUS)**2 - (ROOT_RADIUS - FLANK_CENTRE_Y)**2)`.
- **Land** — straight, from x_f to `BELT_PITCH`/2.

Nothing printed depends on this construction any more.

### 4.2 Pulley groove — the HTD-3M standard for 40 teeth

**Source.** `reference/htd3m_40t_40015040.stp`, a CADENAS PARTsolutions model
of a 40-tooth HTD-3M pulley for 15 mm belt. The file is stored unmodified; its
header gives the licence as CC BY-ND 4.0, credit CADENAS. Only its groove is
used. Its flanges, 6 mm pilot bore, 19 mm face and hub are irrelevant.

The five catalogue values in §3.3 were read from the file's B-rep. The groove
is not imported at run time: it is rebuilt from those values, and the file is
kept as the reference the rebuild is tested against.

**Frame.** For one groove: origin on the pulley axis, **v** radial along the
groove centreline, **u** tangential. The groove is symmetric in u; build the
half with u ≥ 0 and mirror.

**Construction**, from the bottom outward:

1. **Bottom arc** — radius `PULLEY_GROOVE_BOTTOM_R` about the origin, i.e.
   concentric with the pulley.
2. **Flank arc** — concave, radius `PULLEY_GROOVE_FLANK_R`, centre
   c1 = (`PULLEY_GROOVE_FLANK_U`, v1) on the circle of radius
   `PULLEY_GROOVE_BOTTOM_R + PULLEY_GROOVE_FLANK_R`. That radius is what makes
   it tangent to the bottom arc; the tangent point lies on the ray from the
   origin through c1.
3. **Straight flank** — the **internal** common tangent of the flank arc and
   the tip arc: the two circles lie on opposite sides of it. Of the two
   internal tangents, take the one whose tangent points B on the flank arc and
   C on the tip arc satisfy v_A < v_B < v_C. It sits about 8.0° off radial.
4. **Tip arc** — convex, radius `PULLEY_GROOVE_TIP_R`, centre
   c2 = (`PULLEY_GROOVE_TIP_U`, v2) on the circle of radius
   `(PULLEY_OD − PULLEY_OD_COMP)/2 − PULLEY_GROOVE_TIP_R`, which makes it
   tangent to the OD; that tangent point lies on the ray through c2.
5. **Land** — the OD circle, to the next groove.

Every junction is closed-form. There is no solver.

**Printer compensation.** `PULLEY_GROOVE_COMP` offsets every groove edge
outward — the bottom and flank arcs grow, the tip arc shrinks — about unchanged
centres. At the default of 0.0 the groove is exactly the standard.

**What the standard already contains.** The groove is 1.2165 deep against a
belt tooth of 1.171, so there is designed tip clearance built in, and the
mouth is 2.40 wide at the OD, leaving a 0.537 land. None of that is a tuning
parameter; it is the standard.

### 4.3 Interface

```python
# belt model only
def tooth_half() -> list[Edge]:
    """Flank arc, root fillet and land for x >= 0, belt profile frame."""
def tooth_face() -> Face:
    """One belt tooth spanning one pitch, closed along the land."""

# pulley
def groove_half() -> list[Edge]:
    """Bottom arc, flank arc, straight flank, tip arc for u >= 0, groove frame."""
def groove_junctions() -> list[tuple[float, float]]:
    """(u, v) of the four junctions A, B, C, D of the half-groove, u >= 0."""
def pulley_section(teeth: int = PULLEY_TEETH) -> Face:
    """The full toothed 2D outline: OD circle with `teeth` grooves at
    PULLEY_GROOVE_PHASE + k*360/teeth, compensation applied. Raises
    ValueError if teeth != 40, since the groove values are only valid for 40."""
```

`pulley_section()` is the single source for the shaft set's teeth and the ring
coupon. Nothing else cuts grooves.

### 4.4 Checks

**Belt tooth**

```
assert FLANK_CENTRE_Y == BELT_PLD               # exact equality, not approx
assert TOOTH_HEIGHT == approx(1.171, abs=1e-3)
assert LAND_WIDTH == approx(0.914, abs=1e-3)
assert tooth_face().is_valid()
e = tooth_half()
assert (e[0] @ 1 - e[1] @ 0).length < 1e-6
assert (e[0] % 1).get_angle(e[1] % 0) < 0.5
```

**Pulley groove — against the manufacturer's geometry**

With `PULLEY_GROOVE_COMP = PULLEY_OD_COMP = 0`:

```
FILE_JUNCTIONS = [(0.2381, 17.4994),   # A bottom / flank arc
                  (0.9408, 18.1019),   # B flank arc / straight
                  (0.9992, 18.5174),   # C straight / tip arc
                  (1.2006, 18.6815)]   # D tip arc / OD
for got, want in zip(groove_junctions(), FILE_JUNCTIONS):
    assert dist(got, want) < 0.005
```

These four points were read from the manufacturer's B-rep. They are the best
acceptance data in the project. The rebuild meets them to 0.0025; the residual
is entirely the file rounding its OD to 37.440 against the derived 37.435.

```
e = groove_half()
for a, b in zip(e, e[1:]):
    assert (a @ 1 - b @ 0).length < 1e-6
    assert (a % 1).get_angle(b % 0) < 0.5        # every junction tangent
assert PULLEY_GROOVE_DEPTH == approx(1.2165, abs=1e-4)
assert abs(PULLEY_GROOVE_DEPTH - 1.219) < 0.005   # agrees with the file
ps = pulley_section()
assert ps.is_valid()
arcs = [e for e in ps.outer_wire().edges() if e.geom_type == GeomType.CIRCLE]
assert sum(abs(e.radius - PULLEY_GROOVE_TIP_R) < 1e-6 for e in arcs) == 80
assert sum(abs(e.radius - PULLEY_GROOVE_FLANK_R) < 1e-6 for e in arcs) == 80
```

If `FLANK_CENTRE_Y == BELT_PLD` ever fails, investigate. Do not relax it to a
tolerance; they are one physical quantity. The same applies to the junction
test: if it fails, the construction is wrong, not the tolerance.

---

## 5. `parts/shaft_set.py` — two pulleys and a guide wheel, one part

### 5.1 Why one part

The baseline has four identical pulleys. This replaces each shaft's pair with a
single printed part that also carries the guide wheel. It answers three of the
open questions at once:

- **Phase** (Q6). The two pulleys on a shaft are printed together, so their
  teeth are in phase to the accuracy of the printer, with nothing to align.
- **Axial spacing.** Belt centres are 54.0 apart by construction rather than by
  two separately positioned hubs.
- **Tail** (Q5). The tail shaft carries an identical part, fixed to a shaft that
  turns in its pillow blocks. Both belts are then synchronised through steel at
  both ends, not only through the slats.

Two off, identical.

### 5.2 Local frame

- **Local z** along the shaft axis, which is machine z. The part is symmetric
  about z = 0.
- **Local x, y** radial.
- **Origin** on the axis, at the centre plane of the guide groove.

Placement is `at(0, 0)` for the tail and `at(CENTRE_DIST, 0)` for the head,
since offset 0 is the shaft axis.

### 5.3 Body: a revolved profile

Build the body as one revolve of an (r, z) profile, then cut teeth and groove.
For z ≥ 0, mirrored:

| Zone | z from | z to | Radius | What passes beside it |
|---|---|---|---|---|
| Guide wheel | 0 | 8.0 | 19.447 (rim) | slat underside at 19.947, lug in the groove |
| Wheel chamfer | 8.0 | 14.447 | 45° cone, 19.447 → 13.0 | nothing |
| Drum | 14.447 | 20.7 | 13.0 | inner tab 17.1–19.6 and lip 19.6–20.4, tips at r = 16.347 |
| Flare | 20.7 | 24.5 | 45° cone, 13.0 → 16.8 | overhanging belt teeth at r ≥ 17.547 |
| Pulley | 24.5 | 29.5 | 18.718 − `PULLEY_OD_COMP`/2 | the belt |

Every zone boundary is derived:

- Wheel rim = `belt_back_radius() − GUIDE_RIM_GAP`.
- Wheel and drum edges from `GUIDE_WIDTH` and the 45° chamfer.
- Flare ends at the pulley face, `BELT_SPACING/2 − PULLEY_FACE_WIDTH/2`.
- Pulley outer end = `SHAFTSET_LENGTH/2`.

`END_CHAMFER` on both end faces, outer edge.

**Why the 45° cones are on both sides.** Printed axis-vertical, the lower half
steps outward twice going up — drum to wheel, and drum to pulley. Those steps
need 45° cones to print without support. The upper half steps inward and would
not need them, but the part is kept symmetric so it goes on the shaft either way
round and prints either end down.

**Why the flare stops at 16.8.** The belt overhangs the 5 mm pulley face by 5.0
each side, and its teeth hang inward to r = 17.547 with nothing under them. The
flare must stay `BELT_TOOTH_CLEAR` below that, giving 17.047 as the limit and
16.8 in practice. The step from 16.8 up to the pulley OD is a 1.9 overhang at
the lands, which prints unsupported.

### 5.4 Teeth

Each pulley zone is `pulley_section()` (§4.3) extruded across
`PULLEY_FACE_WIDTH` and unioned into the revolved body in place of the plain
OD cylinder. Grooves are centred at `PULLEY_GROOVE_PHASE + k·9.0` degrees from
local +y, identical on both pulleys, so the two belts' teeth are in phase.

Do not cut grooves any other way — not from `tooth_face()`, and not by
importing the STEP file. One function makes teeth, and it is the one tested
against the manufacturer's geometry.

No flanges. The space beside each pulley face is where the saddle tabs run.

### 5.5 Guide groove

A V-groove running round the guide wheel's rim, centred on z = 0. Its
cross-section is the lug's cross-section (§6.1) offset outward by
`GROOVE_FLANK_CLEAR` on each flank and deepened by `GROOVE_TIP_CLEAR` at the
tip, revolved about the axis.

With the numbers above: groove bottom at r = 14.447, groove width at the rim
about 11.4, leaving a 2.3 land either side on the 16.0 wheel. Lateral play
before a flank engages is ±0.71.

**Why 90° and not the 40° industrial standard.** Printed axis-vertical, the
groove's upper flank is a downward-facing surface. At 40° included it would sit
20° off horizontal and cannot print. At 90° both flanks are at 45°, and so are
the lug's, which prints tabs-up on the slat. The centring force per unit of
lateral load is lower at 90°, which does not matter at these loads.

**While a slat is wrapped on the pulley, the lug has no motion relative to the
groove.** Slat, belt and shaft set rotate together as one body. Contact happens
only during entry and exit. This is why the guide wheel is fixed rather than
idling on its own bearings.

### 5.6 Fixing

- Bore: `PULLEY_BORE + PULLEY_BORE_CLEARANCE` = 8.15, through, 0.4 chamfer
  each end.
- Two M4 grub screws, at z = ±`GRUB_Z`, **same angular position**, radial
  along local +x.
- Each into an M4 heat-set insert, pocket `PULLEY_INSERT_DIA` ×
  `PULLEY_INSERT_DEPTH`, then M4 clearance through to the bore.
- The shaft gets a flat filed `SHAFT_FLAT_DEPTH` deep and `SHAFT_FLAT_LENGTH`
  long; both grubs bear on it.

**Why the insert depth changes.** The baseline's 8.0 insert in a 22 mm hub
would have broken into the bore: 11.0 − 4.075 = 6.9 of wall. In the 26 mm drum
there is 8.925, and a 6.0 insert leaves 2.9. Assert it (§12.3).

Axial position on the shaft is set by the grubs. Both shaft sets must sit at the
same z, since the guide grooves define where every slat runs. §13 gives the
procedure.

### 5.7 Leaving the project

Printed. Exported as STL, axis vertical, either end down. PETG. Teeth are
vertical walls; nothing needs support.

```
out/shaft_set.stl
```

---

## 6. Changes to `parts/slat.py`

This modifies finished geometry. **Do not batch-print slats until this lands.**
Any slats already printed are for test-fitting the saddle only.

### 6.1 Guide lug

A trapezoidal ridge on the belt-contact face, centred at slat-local z = 0,
hanging in −y:

- Cross-section across the machine: `LUG_TOP_WIDTH` = 11.0 at y = 0, tapering
  at `LUG_ANGLE`/2 to `LUG_TIP_WIDTH` = 3.0 at y = −`LUG_DEPTH` = −4.0.
- Length along the run: `LUG_LENGTH` = 8.0, centred on x = 0.
- `LUG_END_CHAMFER` on its leading and trailing ends, so it enters the groove
  cleanly.

On every slat, plain and cleated. With 46 slats, about three lugs are seated in
each groove at any moment.

It prints pointing up, alongside the tabs, flanks at 45°.

**Why the lug's straight length does not bind on the curved groove.** Wrapped
on the pulley, the lug is a chord and the groove is an arc. The lug's ends sit
further from the axis than its middle, where the V-groove is wider. Clearance
grows toward the ends; nothing gets tighter.

### 6.2 Tab depth

`SADDLE_TAB_DEPTH` 6.0 → 3.6. The lip's upper face moves from 5.0 to 2.6 below
the contact face, 0.2 under a 2.4 belt. The lips now hold the belt. It also
moves the tab tips from r = 13.947 to 16.347 on the pulley, which is what makes
the 26 mm drum fit.

If the measured belt comes in at the 2.44 some sheets quote, the gap closes to
0.16. Still positive. Re-evaluate after measuring.

### 6.3 What changes in the slat's checks

- Bounding box, plain: 16 × 9 × 80 → **16 × 7 × 80**. The lug at 4.0 now sets
  the depth.
- Bounding box, cleated: 16 × 21 × 80 → **16 × 19 × 80**.
- Volume: lug adds about 0.22 cm³, shallower tabs remove about 0.17. Net
  +0.06 cm³; recompute the bands from the model rather than widening them.
- Add probes: lug present at (0, −2, 0) and (0, −3.8, 0); absent at
  (0, −2, 5.0), (0, −4.5, 0), (6.0, −2, 0).
- Re-export both slat STLs.

---

## 7. `parts/shaft.py`

Bought, reference solid only.

```python
def shaft() -> Part:
    """8.0 dia x 145.0, axis along local z, origin at its centre.
    Flat of SHAFT_FLAT_DEPTH x SHAFT_FLAT_LENGTH centred at z = 0,
    facing local +x."""
```

Same part at both ends. The head shaft's drive end is simply whichever end the
motor goes on.

---

## 8. `parts/belt.py`

Bought, reference solid only, never exported.

```python
def belt_segment(teeth: int) -> Part:
    """Straight, toothed. Land on y = 0, teeth in -y to -TOOTH_HEIGHT,
    back at +BELT_BACK_THICKNESS. BELT_WIDTH across. For mesh checks."""

def belt_wrapped(teeth: int) -> Part:
    """The same teeth wrapped on the pitch circle as meshed on a pulley,
    centred on local +y. For mesh checks only."""

def belt_band() -> Part:
    """The full loop as backing only, no teeth: land to back, following the
    loop path. For the assembly and for clash checks against slats."""
```

Decision 10. The assembly needs the belt's position, not its teeth; 276 teeth
× 2 belts would make the viewer unusable. `belt_band()` is what goes in the
`belts` group. The toothed loop exists only behind `detail=True`.

---

## 9. `geometry.py` additions

### 9.1 Radial stations

```python
def belt_back_radius() -> float:       # corrected, 19.947
def belt_tooth_tip_radius() -> float:  # 17.547
def tab_tip_radius() -> float:         # belt_back - SADDLE_TAB_DEPTH = 16.347
def cleat_tip_radius() -> float:       # 34.947
def guide_rim_radius() -> float:       # 19.447
def guide_groove_bottom_radius() -> float:  # 14.447
```

Everything that asserts a clearance uses these, never literals.

### 9.2 `loop_at(s)` — placement anywhere on the belt

`at(t, offset)` only covers the straight runs. Slats also sit on the arcs, so
the slat group needs a placement that follows the whole loop.

```python
def loop_at(s: float) -> Location:
    """Frame on the belt back at distance s around the loop, measured
    along the pitch line, 0 <= s < BELT_LOOP_LENGTH.

    s = 0 is the tail tangent point at the start of the carrying run.
      0     .. C        carrying run
      C     .. C + 60   head arc
      C+60  .. 2C + 60  return run, travelling tailward
      2C+60 .. 828      tail arc

    Local +x is the direction of belt travel, +y points out of the belt
    back away from the loop, +z is machine z. On the carrying run this
    agrees exactly with at(s, belt_back_radius())."""
```

Distance is measured on the **pitch line**, because that is where tooth pitch —
and so the 18.0 slat pitch — is defined. Each arc is exactly 60.0 of pitch line,
20 teeth, which is a useful check. Position is then reported at the belt-back
radius, where the slat sits.

Slat i is placed with `loop_at(i * SLAT_PITCH)`. `at_return()` is superseded;
keep it only if something already depends on it.

### 9.3 Take-up

```python
def tail_shaft_t(takeup: float = 0.0) -> float:
    """Run position of the tail shaft with the tail plate slid by takeup,
    TAIL_TAKEUP_MIN <= takeup <= TAIL_TAKEUP_MAX."""
```

The assembly is built at takeup 0, which is the nominal 354.0 centre distance.
The range exists only for the clearance checks in §12.6. The mechanism that
pushes the plate — a jacking screw in a block bolted to the frame — is a later
part.

---

## 10. `parts/coupons.py`

Two coupons, both printed, both exported. Each is made by the **same
functions** as the real part, so it calibrates the real part.

```python
def ring_coupon() -> Part:
    """pulley_section() extruded 3.0 thick, with a plain bore of
    PULLEY_BORE + PULLEY_BORE_CLEARANCE. Tests the real groove and the
    real pitch together, and sets PULLEY_GROOVE_COMP and PULLEY_OD_COMP."""

def guide_coupon() -> Part:
    """The guide wheel zone of shaft_set() alone, with its groove and bore.
    Paired with one printed slat to check lug entry and centring."""
```

The rev A flat groove coupon is gone. It existed to discover the tooth shape,
and the shape is no longer unknown. What is left to learn is how the printer
distorts a known shape, and the ring coupon measures that on the real
curvature, including pitch, which a flat bar cannot.

Three millimetres is enough: it is a few minutes of printing, and a 15 mm belt
laid round it seats on the full groove profile across the ring's width.

---

## 11. Assembly groups

```python
def drivetrain_group() -> Compound:
    """Two shafts and two shaft sets at at(0, 0) and at(CENTRE_DIST, 0)."""

def belts_group(detail: bool = False) -> Compound:
    """Two belt_band() at z = +/- BELT_SPACING/2. Toothed loops if detail."""

def slats_group(detail: bool = False) -> Compound:
    """46 slats at loop_at(i * SLAT_PITCH), cleated where is_cleated(i).
    Plain boxes of the slat bounding box unless detail."""

GROUPS["drivetrain"] = drivetrain_group
GROUPS["belts"] = belts_group
GROUPS["slats"] = slats_group
```

Each is a few lines. If any needs more, the framework is the problem.

---

## 12. Acceptance criteria

### 12.1 The correction

```
assert belt_back_radius() == approx(PULLEY_OD/2 + BELT_BACK_THICKNESS, abs=1e-9)
assert belt_back_radius() == approx(19.947, abs=1e-3)
assert belt_back_radius() - belt_tooth_tip_radius() == approx(BELT_THICKNESS)
assert belt_tooth_tip_radius() < PULLEY_OD/2          # teeth sit in grooves
assert PULLEY_OD/2 < PULLEY_PD/2 < belt_back_radius() # pitch line inside backing
assert PULLEY_GROOVE_BOTTOM_R < belt_tooth_tip_radius()  # teeth don't bottom out
```

The last three are the ones that would have caught the error: belt teeth
inside the OD, pitch line inside the backing, and tooth tips above the
standard groove's bottom.

### 12.2 Radial envelope, all from §9.1

```
assert tab_tip_radius() >= DRUM_DIA/2 + DRUM_TAB_CLEAR          # 16.347 vs 14.0
assert belt_tooth_tip_radius() >= PULLEY_SKIRT_R + BELT_TOOTH_CLEAR  # 17.547 vs 17.3
assert guide_groove_bottom_radius() > DRUM_DIA/2                # 14.447 vs 13.0
assert SHAFT_HEIGHT_ABOVE_PLATE - cleat_tip_radius() > 5.0      # 13.05
```

### 12.3 Shaft set

```
ss = shaft_set()
assert ss.is_valid()
assert bbox_size(ss) == approx((38.894, 38.894, 59.0), abs=0.05)
assert 38.0 <= volume_cm3(ss) <= 52.0
assert PULLEY_INSERT_DEPTH <= DRUM_DIA/2 - (PULLEY_BORE + PULLEY_BORE_CLEARANCE)/2 - 2.0

# probes, local frame
assert contains(ss, (0, 14.0, 0))        # wheel, below the groove
assert not contains(ss, (0, 17.0, 0))    # inside the guide groove
assert contains(ss, (0, 19.0, 7.0))      # wheel rim land beside the groove
assert not contains(ss, (0, 14.0, 17.5)) # tab running zone, outside drum
assert contains(ss, (0, 18.5, 27.0))     # pulley land, on +y by phase
assert not contains(ss, (1.3966, 17.7451, 27.0))  # pulley groove, r 17.8 at 4.5°
assert contains(ss, (1.3573, 17.2467, 27.0))      # below groove bottom, r 17.3
assert not contains(ss, (0, 3.9, 0))     # bore
```

Angles are measured from local +y toward local +x.

The guide-groove probe at (0, 17.0, 0), the pulley land probe at
(0, 18.5, 27.0) and the pulley groove probe at r 17.8 are the ones that catch
a groove or a tooth cut that silently missed.

### 12.4 Mesh: belt in pulley

The direction of this test has reversed since rev A. The groove is the
standard and is not in question; this checks that the **belt model** is a
fair representation of a belt sitting in it.

```
w = belt_wrapped(8)
assert not clash(w, shaft_set())
# the belt model must not be shrunken to pass: its teeth reach nearly
# to the groove bottom
assert belt_tooth_tip_radius() - PULLEY_GROOVE_BOTTOM_R < 0.1    # 0.046
```

With the current radii the belt tooth clears the groove by 0.046 at the tip
and at least 0.145 on the flanks. If the clash fails, adjust `FLANK_RADIUS`
and `ROOT_RADIUS` until the belt model fits. **Never** change a
`PULLEY_GROOVE_` value to make this pass.

### 12.5 Guide: lug in groove

```
s = slat(False).moved(loop_at(C + 30))   # mid head arc
h = shaft_set().moved(at(C, 0))
assert not clash(s, h)
assert clash(s, shaft_set_with(groove_flank_clear=0.0,
                               groove_tip_clear=0.0).moved(at(C, 0)))
```

Same idea: the zero-clearance groove must collide with the lug, or the lug is
not in the groove at all.

### 12.6 Whole-loop clearances

```
for i in range(SLAT_COUNT):
    s = slat(is_cleated(i)).moved(loop_at(i * SLAT_PITCH))
    for part in drivetrain_group():
        assert not clash(s, part)
    for plate in plates_group():
        assert not clash(s, plate)
```

Run it at takeup `TAIL_TAKEUP_MIN`, 0 and `TAIL_TAKEUP_MAX`, moving the tail
plate, pillow-block station and tail shaft set together.

This is the expensive test. It uses real slat geometry; the detail flag is for
viewing, not for checks.

### 12.7 Loop geometry

```
assert loop_at(0).position == approx(at(0, belt_back_radius()).position)
assert loop_at(C/2).position == approx(at(C/2, belt_back_radius()).position)
assert (loop_at(BELT_LOOP_LENGTH - 1e-9).position
        - loop_at(0).position).length < 1e-6
assert 2*CENTRE_DIST + pi*PULLEY_PD == approx(BELT_LOOP_LENGTH, abs=1e-9)
```

---

## 13. Physical calibration and tests, in order

Nothing in §12 can tell you the model matches the belt. These can. Each gates
the next.

1. **Measure the belt.** Thickness at several points, and width. If thickness
   is 2.44 rather than 2.4, update `BELT_THICKNESS` and rerun everything.
2. **Ring coupon.** This replaces rev A's two coupons. Fix pitch first, then
   fit:
   - Measure the OD across two opposite lands with calipers; with 40 teeth a
     land always faces a land. Set `PULLEY_OD_COMP` = measured − 37.435 and
     reprint.
   - Wrap a length of real belt 180° round it. If teeth ride progressively
     higher toward the ends of the wrap, pitch is still wrong: revisit
     `PULLEY_OD_COMP`.
   - If the belt needs force to seat everywhere, the printed grooves are
     narrow: raise `PULLEY_GROOVE_COMP` by 0.05 and reprint. If it rocks, lower
     it. Stop when it seats by hand with no rocking.

   Do **not** tune `FLANK_RADIUS` or `ROOT_RADIUS` here. They no longer shape
   anything printed, and the groove shape is the standard. If you find yourself
   wanting to change the groove's shape to make a print fit, the printer is the
   problem, not the geometry.
3. **Saddle fit.** One plain slat on real belt: snaps on, holds, lips sit just
   under the belt.
4. **Guide coupon.** With that slat, the lug enters the groove from a 1 mm
   offset without catching, and the slat returns to centre.
5. **First shaft set.** Only now.
6. **Assembly and axial set-up.** Set both shaft sets with a caliper from the
   inner face of each pillow block, equal on both sides and equal head to
   tail. Tension by sliding the tail plate until a finger press at mid-span
   deflects the belt about 5 mm.
7. **Creep test.** Mark each slat's position against the belt teeth with a
   paint pen. Run 1000 revolutions, about 35 minutes at 30 rpm. Check drift.

On creep (decision 9): wrapped on the pulley, the belt back falls away from the
slat's flat underside by 1.6 at the slat ends, so the slat never loads the
belt. Within each 7.0 tab the belt curves 0.31 relative to flat, flexed on
every pass. The grip is friction only. If slats walk along the belt, the
fallback is a positive key — a small printed pin through a hole punched in the
belt's land between two teeth, one per slat end. Do not build it unless the test
fails.

---

## 14. Definition of done

1. §0 applied; all 15 existing checks and 58 existing tests still pass, with
   updated expected values where the correction moves them.
2. Every assertion in §12 passes, in both `checks.py` and pytest.
3. `python parts/shaft_set.py` shows the part with visible teeth and groove.
4. `python assembly.py frame plates drivetrain belts slats` shows the machine
   with slats running round both ends.
5. `export.py` writes `shaft_set.stl`, both slat STLs, and the two coupons.
   `reference/htd3m_40t_40015040.stp` is committed unmodified and is never
   written by the project.
6. README: the belt-radius correction and its date; the groove's source file
   and licence; which parameters are awaiting §13; and the §13 order.
7. No remaining reference to `GROOVE_CLEARANCE`, `COUPON_LENGTH`,
   `COUPON_GROOVE_COUNT` or `groove_coupon` anywhere in the project.

---

## 15. Out of scope, recorded so it isn't lost

- The side skirts no longer guide anything. When they're specified, their gap
  can open to 2.0, with ±0.71 of slat play from the V-guide to allow for.
- Pillow blocks and their standoffs, once measured.
- The tail take-up jacking screw.
- Motor mount and coupler.
