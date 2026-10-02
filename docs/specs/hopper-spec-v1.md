# Hopper: specification, v1

Written against `design-baseline-v3.md` (commit `ca50e1a`). All dimensions are
millimetres and degrees. Status labels as in the baseline: **fixed**,
**catalogue**, **provisional**, **open**. Section references like "B§2.3" point
into the baseline.

Nothing in this spec changes a built part. It adds parts to the frame, adds a
group to `assembly.py`, extends the prop load check, and asks for two new
check helpers (§9).

---

## 0. Decisions this spec is built on

| # | Decision | Source |
|---|---|---|
| D1 | The hopper is **frame-mounted**: it tilts with the conveyor and is placed with `at(..., incline=incline)` | user |
| D2 | One fill holds **1–2 L** of loose LEGO | user |
| D3 | **Oversize parts are screened out before loading.** The hopper does not have to pass or reject anything that is wider than the 76 channel in both horizontal directions | user |
| D4 | Loading is **a bucket dumped all at once** | user |
| D5 | Throat: a **metering brush** limits the layer depth leaving the hopper; a **wiper brush** seals the back of the hopper against the slats | user |
| D6 | The hopper **does not wrap the tail pulley**. It sits entirely on the straight carrying run, headward of the point where slat gaps have closed. The tail arc, tail shaft set, tail plate and take-up stay open behind it | this spec, §1 |
| D7 | The hopper's lower walls **are the first section of side skirt**: same `SKIRT_INSET`, `SKIRT_GAP`, `SKIRT_HEIGHT`. The skirt spec starts where the hopper ends | this spec, §5.4 |
| D8 | A **carrying-run support rail** under the hopper zone takes the pile's weight and adds lateral guidance | this spec, §4.7 |

---

## 1. Concept

The pile sits in a V-trough formed by the rising carrying run and a back
wall. As the slats move up the run, cleats pull parts out from under the
pile. At the hopper's front, a brush set a little above the cleat tips lets
through one cleat-pocket's worth of parts and pushes the heap above that
back into the hopper.

**Why the hopper does not wrap the tail.** Round the tail pulley, slat top
gaps open to 5.7 and close again to 1.0 as slats come onto the straight
(B§4.1). A part resting on the slats there can drop into an open gap and be
pinched as it closes. The hopper therefore meets the slats only headward of
the point where every gap has closed, at every take-up. This also keeps the
tail arc, the tail grub screws and the take-up clear by construction: nothing
of the hopper is tailward of t = 10.

**Why frame-mounted.** Its geometry relative to the run is constant, so the
seal brush only has to accept the 6.0 of take-up (and not even that, since it
sits on the straight run where take-up changes nothing). The cost is that
every wall must still shed parts at 25° and at 55°, which sets the wall
angles (§3.3).

Section through the machine centre plane, run coordinates, not to scale.
`h` is height above the slat top (§2).

```
 h
 |                  rim, horizontal at 40°
189  ___-------------------____________
     |\                                ---___ 110
     | \ back wall (85° to run)                |
     |  \                                      | front wall
     |   \              pile                   | (normal to run)
     |    \                                    |
 22  |  [seal brush clamp]              [metering brush clamp]
     |      \\  bristles, tips headward        ||  tips 14 above slat top
  0  ======================================================  slat top  -> +t
         ^ seal line t = 28                    ^ front wall t = 130
     ~~~~~~~~ support rail t = 30 .. 140, under the slats ~~~~~~~~
```

Section across the run (looking headward), half shown:

```
      z=0          38 41               108 117
       |            |  |                 |  |
 h 110 -            |  |                 |  |  side panel (9 ply)
                    |  |                 |  |
  98 ---------------+--+-------------.---+  |  flare meets panel
                    |  |          .      |  |
                    |  |       .  liner  |  |
                    |  |    .   (45°)    |  |
  28 ---------------|  |.                |  |
                    |  | liner lower wall = skirt
 1.5 ---------------|__|
   0 ====slat top=======  (slat end at 40 ± 0.71)
```

---

## 2. Coordinates and frame

- **All hopper parts belong to the machine frame (tilting).** Placed with
  `at(t, offset, lateral, incline)`; never with `base_frame()`.
- In this spec, positions are given as `(t, h, z)` where
  **h = offset − slat-top station** (22.947, B§2.3). In code, `h` must be
  converted with the station function, never with the literal. A helper
  `hopper_offset(h)` in `geometry.py` is suggested.
- "Headward" is +t; "tailward" is −t.
- Every hopper part is fixed to the frame rails or to the fixed plate at
  t = 88.5. **None is fixed to the tail plate**, so take-up does not move the
  hopper. The group still accepts `takeup` (B§10 rule 6) because its checks
  run against the tail at every take-up.

---

## 3. Parameters

Everything below goes in `params.py`. "Derived" rows must be computed there,
with the assertion stated, not typed in.

### 3.1 Position along the run

| Name | Value | Status | Notes |
|---|---|---|---|
| `HOPPER_SEAL_T` | 28.0 | provisional | where the seal brush tips touch the slat tops |
| `HOPPER_SEAL_T_MIN` | 25.0 | derived | max over take-up of `tail_shaft_t(takeup)` (4.0, at take-up −4.0) + `SLAT_PITCH` (18.0) + 3.0. Assert `HOPPER_SEAL_T ≥ HOPPER_SEAL_T_MIN` |
| `HOPPER_FRONT_T` | 130.0 | provisional | front wall inner face |
| `HOPPER_TAIL_KEEPOUT_T` | 10.0 | derived | max tail_shaft_t + 6.0. No hopper part may have any point at t below this |

### 3.2 Channel (inherited from the skirts)

| Name | Value | Status | Notes |
|---|---|---|---|
| `SKIRT_INSET` | 38.0 | provisional (B§8.1) | liner lower-wall inner face, ±z |
| `SKIRT_GAP` | 1.5 | provisional (B§8.1) | liner bottom edge above slat top |
| `SKIRT_HEIGHT` | 28.0 | provisional (B§8.1) | height of the vertical lower wall; the flare starts here |
| `HOPPER_CHANNEL_W` | 76.0 | derived | 2 × `SKIRT_INSET` |

The hopper uses the skirt parameters by name, so whatever the skirt spec
decides about the 0.29 cleat-to-skirt clearance (B§8.1, B§11 Q1) applies here
too without editing this spec.

### 3.3 Walls and rim

| Name | Value | Status | Notes |
|---|---|---|---|
| `LINER_THICKNESS` | 3.0 | provisional | printed PETG |
| `FLARE_ANGLE` | 45.0 | provisional | liner flare, measured from the run normal, outward |
| `HOPPER_HALF_W` | 108.0 | provisional | side-panel inner face, ±z |
| `FLARE_TOP_H` | 98.0 | derived | `SKIRT_HEIGHT` + (`HOPPER_HALF_W` − `SKIRT_INSET`) / tan(`FLARE_ANGLE`) |
| `BACK_WALL_ANGLE` | 85.0 | provisional | included angle between the run (headward) and the back wall inner face; the wall leans 5° headward of the run normal |
| `RIM_FRONT_H` | 110.0 | provisional | rim height at the front wall. Assert ≥ `FLARE_TOP_H` + 5.0 |
| `RIM_LEVEL_INCLINE` | 40.0 | provisional | = `INCLINE`. The rim is horizontal at this incline: h_rim(t) = `RIM_FRONT_H` + (`HOPPER_FRONT_T` − t)·tan(`RIM_LEVEL_INCLINE`) |
| `PANEL_THICKNESS` | 9.0 | provisional | plywood, as the bridge plates |
| `WALL_THICKNESS` | 6.0 | provisional | plywood, back and front walls |
| `PANEL_BOTTOM_OFFSET` | −45.0 | provisional | panel bottom edge, as an offset (not h): 3.0 above the plate top face at −48.0 |
| `PANEL_REAR_T_MIN` | 34.0 | provisional | panel material stays headward of this below the flare top |

**Wall slopes that follow** (asserted in §8, A4, and printed every 2.5°):

- Liner flare, world slope = arccos(sin `FLARE_ANGLE` · cos θ): **50.1° at 25°**, 57.3° at 40°, 66.1° at 55°.
- Back wall inner face, world slope = 180 − `BACK_WALL_ANGLE` − θ: **70° at 25°**, 55° at 40°, **40° at 55°**.
- Front wall inner face faces tailward and overhangs the pile at every angle; parts do not rest on it.

LEGO on PETG or plywood starts sliding somewhere around 17°–25°, so all of
these shed parts. The back wall at 55° is the closest, with about 15° to
spare.

**Why the rim is not parallel to the run.** A rim parallel to the run puts
the back corner of the rim lowest at steep angles. That caps the level-fill
volume at 55° near 1.0 L for any reasonable size. Making the rim horizontal
at the nominal 40° leaves it only ±15° from level over the whole range.

### 3.4 Brushes

Both brushes are bought **strip brushes**. The expected source is a nylon
door-sweep strip, cut to length. Values are provisional until the actual strip
is measured.

| Name | Value | Status | Notes |
|---|---|---|---|
| `BRUSH_BACKING_W` | 6.0 | provisional, measure | backing strip thickness |
| `BRUSH_BACKING_H` | 8.0 | provisional, measure | backing height |
| `BRUSH_FREE_LEN` | 25.0 | provisional, measure | bristle length out of the backing |
| `BRUSH_LEN` | 75.0 | derived | `HOPPER_CHANNEL_W` − 1.0: 0.5 to each liner |
| `SEAL_BRUSH_INTERFERENCE` | 2.0 | provisional | undeflected tip below the slat top |
| `SEAL_BRUSH_RAKE` | 15.0 | provisional | bristles lean from the run normal; **tips headward** of the root, so slat motion and oncoming cleats bend them the way they already lean |
| `SEAL_ROOT_H` | 22.15 | derived | `BRUSH_FREE_LEN`·cos(rake) − interference. Assert ≥ `CLEAT_HEIGHT` (12.0) + 5.0 |
| `SEAL_ROOT_T` | 21.53 | derived | `HOPPER_SEAL_T` − `BRUSH_FREE_LEN`·sin(rake) |
| `METER_GAP` | 14.0 | provisional | metering brush tip above the slat top: cleats (12.0) pass 2.0 under it |
| `METER_GAP_MIN` / `_MAX` | 6.0 / 26.0 | provisional | adjustment range, slotted clamp (§4.5) |
| `METER_RAKE` | 0.0 | provisional | bristles along the run normal |

The back wall inner face is placed so that it **contains the seal brush root
line** (`SEAL_ROOT_T`, `SEAL_ROOT_H`) at `BACK_WALL_ANGLE`. At h = 0 it is at
t = 19.59, and at the rim t ≈ 36.1, h ≈ 188.8.

### 3.5 Support rail

| Name | Value | Status | Notes |
|---|---|---|---|
| `RAIL_T0` / `RAIL_T1` | 30.0 / 140.0 | provisional | rail extent; 10 beyond the front wall, so parts leaving under the metering brush are still supported |
| Rail section | guide wheel rim zone of B§5.1, extruded straight | derived | lands at the guide-wheel-rim station (19.447 offset), groove bottom at the groove-bottom station (14.447), 11.4 wide at the lands, `GUIDE_WIDTH` 16.0 overall. It must be built from the **same function** that makes the guide wheel section, so the groove matches by construction |
| `RAIL_BOTTOM_OFFSET` | 4.0 | provisional | rail body bottom face (offset, not h) |
| `RAIL_END_CHAMFER` | 45°, to the groove bottom | provisional | lead-in at both ends for lugs arriving from the tail wheel |
| `RAIL_ARM_OFFSET` | −12.0 .. +4.0 | provisional | cross-arm between the runs; 4.3 clear of the carrying and returning saddle-tab stations (±16.347) |
| `RAIL_ARM_T` | 76.5 .. 100.5 | provisional | centred on the plate at 88.5 |
| `RAIL_ARM_HALF_W` | 54.0 | provisional | the arm spans z ±54 |
| `RAIL_POST_Z` | ±44.0 .. ±54.0 | provisional | 3.29 outside the worst-case slat end (40.71) |

Slats run 0.5 above the lands: the belt back sits at 19.947, the lands at
19.447. At nominal tension they do not touch. Under the pile, the belt sags
onto the rail and the rail carries the load. The lug in the groove also gives
the carrying run under the hopper the same ±0.71 lateral constraint as the
pulleys. That answers B§11 Q2 and Q3 for the hopper zone only; the skirt spec
can extend the rail over the rest of the carrying run.

### 3.6 Mounting

| Name | Value | Status | Notes |
|---|---|---|---|
| `HOPPER_FOOT_T` | 46.0, 126.0 | provisional | foot centres along the run, on the rail top faces |
| `HOPPER_FOOT_LEN` | 24.0 | provisional | along the run |
| Foot spans | z 105 .. 137 | derived | sits on the rail top (117 .. 137), cantilevers 12 inboard to carry the panel |
| Clearances to plates | 7.5 to the tail plate at take-up −4.0; 8.0 and 3.0 to the plate at 88.5; 16.5 to the plate at 177 | derived | assert ≥ 3.0 |

### 3.7 Mass and load

| Name | Value | Status | Notes |
|---|---|---|---|
| `PLY_DENSITY` | 0.60 g/cm³ | provisional | weigh a plate offcut |
| `PETG_DENSITY` | 1.27 g/cm³ | catalogue | the infill fraction is ignored, which is conservative |
| `BRUSH_MASS` | 25 g each | provisional | weigh |
| `HOPPER_HARDWARE_MASS` | 60 g | provisional | from `--report` |
| `LOAD_BULK_DENSITY` | 0.50 kg/L | provisional | weigh a level litre of mixed LEGO |

The hopper mass and centre of gravity are **computed from the solids**, not
typed in (§7).

---

## 4. Parts

Every part is modelled in `parts/hopper.py` unless stated otherwise. Local
frame for all parts: +x along the run (headward), +y along the run normal,
+z across the machine, with the origin on the mating face named below.
Placing a part is then one `at()` transform.

### 4.1 Side panel, 2 off (identical), plywood 9, cut list

- **Outline, in (t, offset):**
  - bottom edge at `PANEL_BOTTOM_OFFSET` from t = `PANEL_REAR_T_MIN` to `HOPPER_FRONT_T` + `WALL_THICKNESS` (136.0);
  - front edge normal to the run at 136.0, up to the rim;
  - top edge on the rim line of §3.3;
  - rear edge along the back wall's outer face down to t = `PANEL_REAR_T_MIN`, then normal to the run down to the bottom edge.
- **Placement:** inner face at z = ±`HOPPER_HALF_W`, outer at ±117.0.
- **Holes:** two M4 per foot, and the corner-cleat holes of §4.6.
- **Local origin:** inner face, on the bottom edge, at t = `HOPPER_FRONT_T`.
- The panel passes over the plate at 88.5 with 3.0 to spare. It does not touch the plate, and it stays clear of the plate bolt heads at z = ±127.

### 4.2 Liner, mirror pair, printed PETG

- **Section** (constant along the run), 3.0 thick throughout:
  - a lower wall with its inner face at z = ±`SKIRT_INSET`, from h = `SKIRT_GAP` to `SKIRT_HEIGHT`;
  - a flare at `FLARE_ANGLE` out to the panel at `FLARE_TOP_H`;
  - a 12.0 vertical flange against the panel inner face, up to h = 110.
- **Extent along the run:** from the back wall inner face (cut at `BACK_WALL_ANGLE`, following it) to `HOPPER_FRONT_T`.
- **Fixing:** 3 × M3 wood screws through the flange into the panel. Two triangular ribs, 3.0 thick, run between the flare's underside and the flange at t ≈ 50 and 110.
- **Lower-wall edges:** the bottom edge has a 0.5 chamfer on the inner side. This matches the slat's own edge chamfer, so a part cannot catch on a sharp lip.
- **Local origin:** on the lower wall's inner face, at its bottom edge, at t = `HOPPER_FRONT_T`.
- **Print orientation:** on the flange's outer face, with the flare as a 45° overhang, which prints unsupported.
- **Bounding box, about:** 110 × 109 × 70. Volume 35–55 cm³.

### 4.3 Back wall, 1 off, plywood 6, cut list

- **Plane:** the inner face lies on the plane of §3.4, through the brush root line at 85° to the run.
- **Outline in its own plane:** it follows the cavity section (channel, flare and panels) grown by the liner thickness. It runs from its bottom edge up to the rim line where that crosses the wall.
- **Bottom edge over the channel:** at h = `SEAL_ROOT_H` + `BRUSH_BACKING_H` + 4.0, so the seal clamp (§4.4) closes the rest.
- **Bottom edge outside the channel:** at h = `SKIRT_GAP`, behind the liner ends.
- **Local origin:** the inner face, on the centre plane, at the brush root line.

### 4.4 Seal brush clamp, 1 off, printed PETG

- **Shape:** a bar 96 long (the channel plus 10 each side), screwed to the back wall's inner face with 3 × M4, with heat-set inserts in the clamp.
- **Brush retention:** a slot `BRUSH_BACKING_W` + 0.3 wide, `BRUSH_BACKING_H` deep, at `SEAL_BRUSH_RAKE`. Two M3 grub screws bear on the backing.
- **Lower face:** at h ≥ `SEAL_ROOT_H` − 1.0. This is still 9.15 above the cleat tips.
- **Local origin:** on the face that mates with the back wall, centre plane, bottom edge.
- **Print orientation:** mating face down.

### 4.5 Front wall and metering clamp

- **Front wall (1 off, plywood 6, cut list):**
  - inner face normal to the run at `HOPPER_FRONT_T`;
  - outline: the cavity section grown by the liner thickness, up to h = `RIM_FRONT_H`;
  - a notch the channel width (76) up to h = `METER_GAP_MAX` + `BRUSH_FREE_LEN` + `BRUSH_BACKING_H` + 4.0 (63.0);
  - 2 × M4 holes for the clamp.
- **Metering clamp (1 off, printed PETG):**
  - a plate 96 wide, lapping the notch by 10 each side, on the wall's inner face;
  - a brush slot at `METER_RAKE`, like §4.4;
  - two vertical slots, each 20.0 long (`METER_GAP_MAX` − `METER_GAP_MIN`), for the M4 bolts, with washers;
  - the plate closes the notch above the brush at every setting in the range.
- **Local origins:** the wall's inner face at the centre plane, h = 0; the clamp's mating face at the centre plane, at the brush tip line.
- **Clamp print orientation:** mating face down.

### 4.6 Feet and corner cleats, printed PETG

- **Hopper foot**, mirror pair × 2 (4 total):
  - 24 along the run × 32 across, rising from the rail top face (offset −57.0) to −27.0;
  - a slot 9.4 wide × 18 deep that takes the panel's bottom edge;
  - 1 × M5 × 12 + T-nut into the rail's top slot at z = ±127, and 2 × M4 through the slot cheeks and the panel;
  - local origin on its bottom face at the M5 axis; prints bottom face down.
- **Corner cleat**, 8 off, identical:
  - a 90° block, 15 × 15 × 30, with one M4 through each leg (bolt and nylock);
  - it joins the panels to the back and front walls, two per joint;
  - the back wall meets the panels at 90° in plan (its tilt is in the t–h plane), so one cleat type serves every joint.

### 4.7 Support rail and bridge, `parts/carry_rail.py`, printed PETG

- **Rail (1 off):** the section of §3.5 from `RAIL_T0` to `RAIL_T1`, with a flat bottom at `RAIL_BOTTOM_OFFSET`. Two M3 heat-set inserts in the bottom face over the arm.
  - Local origin: centre of the land plane (the guide-wheel-rim station) at t = `RAIL_T0`.
  - Print orientation: bottom face down, groove up; 45° flanks, no support.
  - Bounding box 110 × 15.447 × 16. Volume 18–28 cm³.
- **Bridge (1 off):**
  - a cross-arm at `RAIL_ARM_OFFSET` × `RAIL_ARM_T` × z ±`RAIL_ARM_HALF_W`;
  - two posts at `RAIL_POST_Z` from the arm down to the plate top face (offset −48.0), each with a pad and 2 × M4 through-bolts and nylocks through the 9 ply plate;
  - the rail bolts on top with 2 × M3.
  - Local origin: pad bottom face, centre plane, t = 88.5.
  - Print orientation: on its headward face (the section as drawn in §1 lies flat), no support. Volume 40–80 cm³.
- **Fitting sequence:** the arm passes between the carrying and returning runs from the side. The belts must be off, or a slat removed at the arm, to fit it. State this in the assembly notes.

### 4.8 Bought parts

| Item | Qty | Model as |
|---|---|---|
| Strip brush, cut to `BRUSH_LEN` | 2 | reference solids in `parts/brush.py`: backing box plus a bristle block, undeflected. Excluded from clash checks (§8, C4) |
| M5 × 12 + T-nut | 4 | `hardware` |
| M4 bolts, nylocks, washers; M4 heat-set inserts | about 30 / 5 | `hardware` |
| M3 × 8, M3 heat-set inserts; M3 grub screws | 2 + 2; 4 | `hardware` |
| M3 wood screws | 6 | `hardware` |

---

## 5. Interfaces and keep-outs

1. **Tail.** No hopper point at t < `HOPPER_TAIL_KEEPOUT_T` (10.0). This keeps clear:
   - the tail arc and tail shaft set, including the grub screws at z = ±17.5, reached from behind with the conveyor turned until a grub faces a slat gap;
   - the tail plate at every take-up;
   - whatever the take-up spec puts on the tail end rail.

   The tail-plate and take-up space is therefore not constrained by the hopper at all.
2. **Tail pillow blocks.** These are not yet modelled. Until they are, use a provisional envelope: t = tail_shaft_t ± 27.5, z = ±42 .. ±58, offset −48 .. +16. All hopper parts must stay ≥ 3.0 from it at every take-up. The nearest part is the liner's lower wall, about 8.4 above it.
3. **Plates.** The feet and panels keep ≥ 3.0 from the plates at 0 (sliding), 88.5 and 177. The rail bridge stands on the plate at 88.5, which is otherwise left free.
4. **Skirts.** The skirt spec starts at t = `HOPPER_FRONT_T` + `WALL_THICKNESS` (136.0) with the same inset, gap and height. The front wall's notch sides continue the channel for those 6.0, so the channel wall is continuous. The skirt spec no longer needs posts on the plate at 88.5.
5. **Hinge, prop, clevis, cross-member, base.**
   - Everything is above the rail top faces, and inboard of the hinge brackets, at t ≥ 34.
   - The checks confirm this at all nine tilt × take-up cases (C9) rather than assuming it.
6. **Returning run.** Only the rail bridge enters the loop. It must clear every returning slat, cleat and belt by ≥ 3.0 (C10).

---

## 6. Capacity

Capacity is the **level-fill volume**: the part of the hopper cavity (bounded
by the slat-top plane, the back wall, the liners, the panels and the front
wall, with the metering notch treated as closed) below the horizontal plane
through the cavity's lowest rim point, at the given incline. Loose LEGO
mounds above that, so this is conservative for a dumped bucket.

Estimated with a 0.5 grid model of the geometry above (the CAD value is
authoritative):

| Incline | Level-fill | Load centroid (t, offset) | Rim above base, front / back |
|---|---|---|---|
| 25° | 2.05 L | (74, 103) | 277 / 309 |
| 40° | 2.41 L | (73, 114) | 289 / 289 |
| 55° | 1.87 L | (66, 106) | 282 / 250 |

So a 2 L bucket fits at every angle, and the rim stays 250–310 above the
base top face. The mouth is about 216 across by 100 along the run.

---

## 7. Loads and the prop

The hopper sits near the hinge. At 25° its centre of gravity is ahead of the
hinge and adds to the prop force. At 55° the full load is **behind** the
hinge line and reduces it.

The check must compute:

1. **Hopper mass and CG** from every hopper solid's volume × density (plywood, PETG), plus the brushes and hardware. Expected 0.6–1.0 kg.
2. **Full load** = level-fill volume at each incline × `LOAD_BULK_DENSITY`, at that level-fill region's centroid.
3. **Prop force** from frame + hopper + full load, at every 2.5°, with and without the load. This replaces the single `TILT_WEIGHT_N` point mass with a list of (mass, t, offset). `TILT_WEIGHT_N` / `TILT_CG_*` stay as the frame's own entry until the frame is weighed.

Rough estimate from the numbers above:

- At 25°, the hopper and full load add about 12% to the prop force: about 98 → 110 N. Doubled, that is about 220 N against the 250 N ceiling.
- At 55°, the prop drops to about 29 N with the load, still in compression.

**Consequence for the motor spec.** Only about 30 N of doubled prop force
remains at 25°. At the head end, that is roughly **300 g of motor and mount**
before the ceiling is reached. This is an estimate; the check's exact margin
is what the motor spec must use. If that is too tight, the options are to
raise the tilt minimum above 25° (B§11 Q12), move pin A, or lift the ceiling
with a stronger printed eye.

---

## 8. Acceptance criteria

Each item goes in `checks.py` and as a pytest test. "Nine cases" means take-up
{−4.0, 0, +2.0} × incline `TILT_CHECK_ANGLES` {25, 40, 55}.

**A. Parameters and geometry**

- A1. `HOPPER_SEAL_T ≥ HOPPER_SEAL_T_MIN` (28.0 ≥ 25.0).
- A2. **Gap closure at the seal.** At all nine cases, for every adjacent slat pair whose shared top-face edge lies at t ≥ `HOPPER_SEAL_T`, the top-face gap is ≤ 1.05. Measure it between the positioned slat solids from `loop_at`.
  - Negative control: with the seal at t = 0, at take-up −4.0, some pair must show a gap > 1.5.
- A3. `SEAL_ROOT_H − CLEAT_HEIGHT ≥ 5.0` (10.15), and the seal clamp's lowest point is at h ≥ `CLEAT_HEIGHT` + 5.0.
- A4. Wall slopes at every 2.5° over `TILT_MIN .. TILT_MAX`:
  - flare ≥ 45.0 (minimum 50.1 at 25°);
  - back wall ≥ 35.0 (minimum 40.0 at 55°);
  - print the table.
- A5. The rim edge of each side panel is horizontal in the base frame at 40°, within 0.1°.
- A6. `RIM_FRONT_H ≥ FLARE_TOP_H + 5.0`.
- A7. Solid validity for every hopper and rail part.
- A8. Bounding boxes and volumes within the ranges of §4.

**B. Capacity**

- B1. Level-fill volume ≥ 1.50 L at 25°, 40° and 55°, and ≤ 2.60 L at 40°. Print it every 2.5° with the load centroid and the rim heights above the base.
- B2. Negative control: the same function run on a cavity built with `RIM_FRONT_H` = 60 (bypassing A6 for the control only) must give < 1.50 L at 55°. The grid estimate is 0.97.

**C. Clearances**

- C1. **Whole-loop sweep** (B§10): add every hopper part except the bristle solids to the fixed-part set. Require no clash, and a minimum distance ≥ 0.25 from any slat, at all nine cases.
  - The tight pair is expected to be the cleat end against the liner, 0.29 worst case, inherited from B§8.1. Report it by name.
- C2. **Rail.**
  - At every case, for every slat whose lug lies over the rail, the lug and rail do not clash.
  - At 40° and take-up 0, the distance from each slat's belt-contact face to the rail lands is 0.45 .. 0.55.
- C3. **Negative control for C2.** The rail raised by 1.0 must clash with at least one slat with a volume > 1 mm³. This is real interference, not a touch (B§10 rule 5).
- C4. **Brushes.**
  - The seal bristle solid's lowest point is 2.0 ± 0.1 below the slat-top plane.
  - The metering bristle tip is 14.0 ± 0.1 above it, and it can be set to 6.0 and 26.0 within the clamp slots.
  - The bristles are exempt from C1; their clamps are not.
- C5. The minimum distance from every hopper part to the tail shaft set, and to a cylinder of radius 35.0 (the cleat-tip swept radius) about the tail axis spanning z ±37.71, is ≥ 3.0 at all three take-ups.
- C6. The minimum t over all hopper solids, at every take-up, is ≥ `HOPPER_TAIL_KEEPOUT_T`.
- C7. The distance to the provisional pillow-block envelopes (§5.2) is ≥ 3.0 at every take-up.
- C8. Feet to plates at 0 (at each take-up), 88.5 and 177: ≥ 3.0 along the run. Panels to plate top faces: ≥ 3.0. Panels to the plate bolt-head envelopes (Ø10 × 5 at z = ±127): ≥ 3.0.
- C9. At all nine cases:
  - every hopper part is ≥ 4.0 from `base_ref`;
  - ≥ 3.0 from the hinge brackets, hinge blocks and their nuts;
  - ≥ 3.0 from the prop, the clevis and the cross-member.
- C10. The rail bridge is ≥ 3.0 from every returning slat, including the cleats, and from both belt reference solids, at all nine cases.
- C11. Every printed part's bounding box, in its stated print orientation, fits `PRINT_BED` (§10). Until then, check against 220 × 220 × 250.

**D. Loads**

- D1. Hopper mass is within 0.6 .. 1.0 kg.
- D2. At every 2.5°, doubled (frame + hopper + full load) gives a prop force ≤ `PROP_FORCE_MAX`. Print the margin at 25°; the motor spec needs it.
- D3. The prop force is ≥ 10 N (still in compression) at every 2.5°, with the hopper both empty and full.

---

## 9. What this adds to the project

This takes more than one group function (B§10 rule 10):

1. `params.py`: the parameters of §3 and their assertions.
2. `geometry.py`: `hopper_offset(h)`, the rim line, the back wall plane, and the wall-slope functions for A4. These return numbers only.
3. `parts/hopper.py`: the parts in §4.1–4.6, plus `hopper_cavity()`. The cavity is a reference solid, never exported, used by B1 and D.
4. `parts/carry_rail.py`: the rail and bridge. The rail section comes from the same function as the guide wheel section.
5. `parts/brush.py`: the brush reference solids.
6. `assembly.py`: a group `hopper(takeup, incline)` holding everything above, one entry in the group table, and one colour. The hopper parts are added to the whole-loop sweep's fixed-part list, with bristles excluded.
7. **New check helpers:**
   - `level_fill(cavity, incline)`: the cavity intersected with the half-space below the lowest rim point; returns the volume and centroid;
   - `mass_properties(parts, densities)`: returns the mass and CG.
8. **Prop force refactor:** `prop_force` takes a list of (mass, t, offset) instead of one weight.
9. Export:
   - STL for the liner pair, seal clamp, metering clamp, feet (mirror pair ×2), corner cleat, rail and bridge;
   - cut list for the two side panels, back wall and front wall, with outlines as DXF or dimensioned polygons;
   - bought items via `--report`.

---

## 10. Open inputs

| Input | Current assumption | Affects |
|---|---|---|
| `PRINT_BED` | 220 × 220 × 250 | C11. The liner (about 110 × 109 × 70) is the largest printed part. |
| Maximum rim height above the base or bench | 250–310 over the tilt range (§6) | Loading comfort. Lowering it means a shorter back wall or less capacity at 55° |
| Brush product | nylon door-sweep strip; backing 6 × 8, bristles 25 free | §3.4. Measure before modelling the clamps |
| `LOAD_BULK_DENSITY` | 0.50 kg/L | D2, D3. Weigh a level litre of mixed parts |
| Skirt decisions (B§11 Q1) | inset 38.0, gap 1.5, height 28.0 | Liner lower wall; inherited by name |

---

## 11. Physical tests to add to B§9

These run after B§9 test 7 (creep), in order.

| # | Test | Settles |
|---|---|---|
| H1 | Fit the liners: feeler-gauge the 1.5 gap over the slat tops along the channel, at 40° | `SKIRT_GAP` for the hopper |
| H2 | Rail: run at 40°, watch lugs enter the rail from the tail wheel and leave it at `RAIL_T1`; no catch or click. Press the pile zone and confirm the slats land on the rail | rail section, `RAIL_T0`, end chamfer |
| H3 | Seal: run 10 min with 1 L of mixed parts at 25°, 40° and 55°; count parts behind the back wall (target 0). Recheck the B§9 test 7 creep marks, since brush drag must not walk slats | `SEAL_BRUSH_INTERFERENCE`, `SEAL_BRUSH_RAKE` |
| H4 | Metering: at each angle, measure parts/min and check for jams with the largest pre-screened parts (a 1×16 beam, a 4×6 plate, a 2×8 plate) | `METER_GAP`, `METER_RAKE` |
| H5 | Fill: dump a 2 L bucket at 25°, 40° and 55° with the belt stopped; nothing spills | `RIM_FRONT_H`, capacity |
| H6 | Weigh the finished hopper, empty and with 2 L | `HOPPER` mass entry, `LOAD_BULK_DENSITY`; rerun D2/D3 |
| H7 | Thin parts: run a handful of the thinnest parts in the collection (flags, tiles, cloth) and look for anything under the liner edges or wedged at the seal brush | liner gap, brush interference |
