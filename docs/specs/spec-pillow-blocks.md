# Specification: printed pillow blocks, bearings, spacer tubes and bearing coupon

Written against `design-baseline-v2.md` (commit `ad71c0e`). All dimensions are
millimetres and degrees. Status labels (fixed / catalogue / provisional / open)
mean what they mean in the baseline.

This specification closes baseline §7.2 and open questions 4 (pillow blocks and
standoffs) and 6 (axial location of the shaft sets). It does **not** change the
slat, the shaft set, the belt or the frame.

---

## 1. What is being added

Each 8 mm shaft runs in two **608ZZ ball bearings**, each pressed into a
**printed pillow block** that is its own standoff: one PETG part from the
bridge plate to the bearing, with the bearing centre at the baseline's shaft
height of 48.0. There is no separate standoff and no bought housing.

| Part | Module | Qty | How it leaves the project |
|---|---|---|---|
| Pillow block | `parts/pillow_block.py` | 4, identical | STL, printed, PETG |
| 608ZZ bearing | `parts/bearing.py` | 4 | reference solid only (bought) |
| Spacer tube | `parts/spacer.py` | 4, identical | STL, printed, PETG |
| Bearing coupon | `parts/coupons.py` (added beside the existing two) | 1 | STL, printed, PETG |

Bought hardware (not modelled beyond reference): 4 × 608ZZ (buy 6; see §7),
8 × M4 heat-set inserts (same type as the shaft set's), 8 × M4 × 16 socket-head
screws, 8 × M4 flat washers, 1 × M12 flat washer (a pressing tool, not a
machine part).

### 1.1 How the shaft is located

The two blocks on a shaft are mirror images of each other: each has a retaining
lip on its **outboard** side only. Between each bearing's inner race and the
shaft set sits a spacer tube. Any axial push on the shaft set therefore travels
through one spacer and one bearing into one lip. A push the other way ends at
the other lip. The shaft is captured between the two lips, and neither press
fit carries axial load.

Consequences that the implementation must respect:

- **No shaft collars.** A collar outboard of a bearing would push that bearing
  toward its open side, against the press fit only.
- The grub screws still carry torque. They no longer set the axial position by
  caliper; the shaft set is slid until both spacers are snug, then backed off
  to leave `SHAFT_END_PLAY`, then the grubs are tightened (§8).
- Both shaft sets end up at the same z because both are referenced to
  identical blocks at z = ±50, not because they were measured.

---

## 2. Parameters

Add to `params.py`. Names are proposals. Where the baseline already has a
parameter for a value, reuse it and do not duplicate it.

### 2.1 Bearing (608ZZ)

| Name | Value | | |
|---|---|---|---|
| `BEARING_BORE` | 8.0 | catalogue | |
| `BEARING_OD` | 22.0 | catalogue | |
| `BEARING_WIDTH` | 7.0 | catalogue | |
| `BEARING_INNER_RACE_OD` | 12.1 | catalogue | outside diameter of the inner ring's face; only used for clearance assertions |
| `BEARING_EDGE_CHAMFER` | 0.3 | catalogue | reference solid only |
| `BEARING_Z` | 50.0 | fixed | existing baseline value (centres at z = ±50); reuse |

### 2.2 Pillow block

Local frame and origin are defined in §3.1. `z` below is local: 0 is the
bearing centre plane, **+z is outboard**.

| Name | Value | | |
|---|---|---|---|
| `SHAFT_HEIGHT` | 48.0 | **fixed** (was provisional) | existing baseline value, bridge-plate top face to shaft axis; reuse the existing name |
| `PB_POCKET_DIA` | 22.4 | provisional | pocket wall between the ribs |
| `PB_POCKET_DEPTH` | 7.0 | derived = `BEARING_WIDTH` | bearing ends flush with the inboard face |
| `PB_RIB_COUNT` | 6 | fixed | |
| `PB_RIB_ANGLE_0` | 90° | fixed | first rib on local +y; the rest at 60° steps |
| `PB_RIB_TIP_DIA` | 21.8 | **provisional, set by the bearing coupon** | the one fit parameter |
| `PB_RIB_BASE_WIDTH` | 2.0 | provisional | rib width where it meets the pocket wall |
| `PB_RIB_TIP_WIDTH` | 0.8 | provisional | flat at the rib tip |
| `PB_RIB_LEAD_IN` | 1.0 | fixed | at the pocket mouth each rib ramps from the wall to full height over this depth |
| `PB_POCKET_MOUTH_CHAMFER` | 0.5 | fixed | 45°, on the pocket edge at the inboard face |
| `PB_LIP_THICKNESS` | 1.5 | provisional | |
| `PB_LIP_HOLE_DIA` | 16.0 | provisional | lip bears on the outer ring only |
| `PB_BOSS_RADIUS` | 15.0 | provisional | 3.8 of wall outside the pocket |
| `PB_TOWER_WIDTH` | 30.0 | derived = 2 × `PB_BOSS_RADIUS` | along the run |
| `PB_INBOARD_FACE_Z` | -3.5 | derived = -`BEARING_WIDTH` / 2 | machine z = ±46.5 |
| `PB_OUTBOARD_FACE_Z` | 5.0 | derived = `BEARING_WIDTH` / 2 + `PB_LIP_THICKNESS` | machine z = ±55.0 |
| `PB_FOOT_LENGTH` | 44.0 | provisional | along the run |
| `PB_FOOT_HEIGHT` | 7.0 | provisional | limited by the returning-run clearance, §5 |
| `PB_FOOT_INBOARD_Z` | -16.0 | provisional | machine z = ±34.0 |
| `PB_FILLET` | 3.0 | provisional | tower-to-foot, all concave edges |
| `PB_INSERT_DIA` | = `PULLEY_INSERT_DIA` (5.6) | derived | same insert as the shaft set |
| `PB_INSERT_POCKET_DEPTH` | 6.5 | provisional | blind, from the underside; leaves 0.5 skin |
| `PB_BOLT_X` | 14.0 | provisional | inserts at x = ±14 |
| `PB_BOLT_Z` | -9.75 | provisional | local z, inboard of the tower; machine z = ±40.25 |

Assertions in `params.py`:

- `PB_RIB_TIP_DIA < BEARING_OD < PB_POCKET_DIA` (ribs interfere; wall clears).
- `PB_LIP_HOLE_DIA / 2 - BEARING_INNER_RACE_OD / 2 >= 1.5` (lip clears the
  inner ring).
- `PB_LIP_HOLE_DIA < BEARING_OD - 2.0` (lip has at least 1.0 of ledge per side
  after the pocket-wall clearance).
- `PB_FOOT_LENGTH <= 45.0 - 1.0`, against the bridge-plate length parameter
  (foot stays on its plate with 0.5 per end).
- `PB_BOSS_RADIUS <= SHAFT_HEIGHT - PB_FOOT_HEIGHT` (the boss does not dip
  into the foot).
- Insert pocket inside the foot:
  `abs(PB_BOLT_Z) + PB_INSERT_DIA / 2 + 1.5 <= abs(PB_FOOT_INBOARD_Z)` and
  `PB_BOLT_X + PB_INSERT_DIA / 2 + 1.5 <= PB_FOOT_LENGTH / 2`.
- Head clearance is asserted in geometry terms; see §5.

### 2.3 Spacer tube

| Name | Value | | |
|---|---|---|---|
| `SPACER_BORE` | 8.3 | provisional | slides on the round part of the shaft |
| `SPACER_OD` | 11.0 | provisional | must land on the inner ring only |
| `SHAFT_END_PLAY` | 0.4 | provisional | total, per shaft |
| `SPACER_LENGTH` | 16.8 | derived = (`BEARING_Z` - `BEARING_WIDTH` / 2) - (shaft set half-length 29.5) - `SHAFT_END_PLAY` / 2 | |
| `SPACER_CHAMFER` | 0.3 | fixed | all four circular edges |

Assertions:

- `SPACER_OD <= BEARING_INNER_RACE_OD - 1.0` (never touches the shield or outer ring).
- `SPACER_OD / 2 >= (PULLEY_BORE + PULLEY_BORE_CLEARANCE) / 2 + 0.4 + 0.8`
  (at least 0.8 of contact on the shaft set end face beyond its 0.4 bore chamfer).
- The spacer stays clear of the shaft flat: the flat ends at z = 22.5, and the
  spacer starts at 29.7.

### 2.4 Bearing coupon

| Name | Value | | |
|---|---|---|---|
| `BC_RIB_TIP_DIAS` | (21.6, 21.7, 21.8, 21.9, 22.0) | provisional | one pocket each, tightest first |
| `BC_POCKET_PITCH` | 30.0 | provisional | |
| `BC_LENGTH` | 150.0 | derived = 5 × pitch | |
| `BC_WIDTH` | 40.0 | provisional | 30 for the pockets + 10 label strip |
| `BC_THICKNESS` | 8.5 | derived = `BEARING_WIDTH` + `PB_LIP_THICKNESS` | same section as the block |
| `BC_TEXT_SIZE` / `BC_TEXT_DEPTH` | 5.0 / 0.6 | provisional | engraved on the top face |

### 2.5 Bridge plate change

| Name | Value | | |
|---|---|---|---|
| `PLATE_PB_HOLE_DIA` | 5.0 | provisional | M4 clearance plus alignment float (±0.5) |

Four holes in each of the two **end** plates (t = 0 and t = 354) at plate-local
x = ±`PB_BOLT_X`, z = ±(`BEARING_Z` + `PB_BOLT_Z`) = ±40.25. They go on the cut
list. The three middle plates are unchanged.

---

## 3. Parts

### 3.1 Pillow block

**Local frame.** Origin on the underside of the foot (the face that mates with
the bridge plate), directly under the bearing axis, in the bearing centre
plane. +x along the run, +y up along the run normal, +z outboard. The bearing
axis is the line (0, `SHAFT_HEIGHT`, z).

**Placement.** For the +z side, translate to the plate top face under the shaft
axis with local z = 0 at machine z = +`BEARING_Z`. For the -z side, the same
part rotated 180° about local y (x → -x, z → -z). The part is symmetric in x,
so one design serves all four positions.

**Construction**, in this order:

1. **Foot**: box x ±`PB_FOOT_LENGTH`/2, y 0 .. `PB_FOOT_HEIGHT`,
   z `PB_FOOT_INBOARD_Z` .. `PB_OUTBOARD_FACE_Z`.
2. **Tower**: in the xy plane, a profile from y = `PB_FOOT_HEIGHT` up to the axis,
   `PB_TOWER_WIDTH` wide, capped by a semicircle of radius `PB_BOSS_RADIUS`
   about the axis. Extrude z `PB_INBOARD_FACE_Z` .. `PB_OUTBOARD_FACE_Z`.
   Union with the foot.
3. **Fillets** `PB_FILLET` on the concave edges where tower meets foot: both
   sides in x, and the inboard corner in z.
4. **Pocket**: cylinder `PB_POCKET_DIA` from the inboard face to depth
   `PB_POCKET_DEPTH`, i.e. local z -3.5 .. 3.5. Mouth chamfer
   `PB_POCKET_MOUTH_CHAMFER`.
5. **Ribs**: `PB_RIB_COUNT` trapezoidal ribs on the pocket wall, running the
   full pocket depth. Each is `PB_RIB_BASE_WIDTH` wide at the wall and
   `PB_RIB_TIP_WIDTH` at the tip, with tips on a circle of `PB_RIB_TIP_DIA`.
   The first rib is at `PB_RIB_ANGLE_0` in the local xy plane. Over the first
   `PB_RIB_LEAD_IN` from the mouth, each rib's tip ramps linearly from the
   pocket wall to full height.
6. **Lip hole**: through-cylinder `PB_LIP_HOLE_DIA` in the lip, local z 3.5 .. 5.0.
7. **Insert pockets**: two blind holes `PB_INSERT_DIA` × `PB_INSERT_POCKET_DEPTH`
   up from the underside at (±`PB_BOLT_X`, z = `PB_BOLT_Z`).

Build the pocket, ribs and lip hole (steps 4–6) as **one function returning the
cutting solid, taking the rib-tip diameter as an argument**, so the bearing
coupon is made by the same code. This follows the precedent of the ring and
guide coupons.

**Print orientation.** Outboard face (the lip face, local z = +5.0) down on the
bed, so the pocket is a vertical cylinder opening upward and the lip is the
first layers. No support. In this orientation the insert pockets are
horizontal holes; that is acceptable for heat-set inserts. Suggested slicer
settings, recorded in the part's docstring, not enforced: PETG, 4 perimeters,
40 % infill.

### 3.2 608ZZ bearing (reference)

An annulus, bore `BEARING_BORE`, OD `BEARING_OD`, width `BEARING_WIDTH`, with
`BEARING_EDGE_CHAMFER` on the four circular edges. It has no internal detail.
Local origin on the axis at the mid-width plane. It is placed at machine
z = ±`BEARING_Z`, coaxial with the shaft, and is never exported.

### 3.3 Spacer tube

A tube `SPACER_BORE` × `SPACER_OD` × `SPACER_LENGTH` with `SPACER_CHAMFER` on
all four circular edges. Local origin on the axis at the face that mates with
the bearing's inner ring; +z runs along the tube toward the shaft set.
Placement: bearing-end face at machine z = ±(`BEARING_Z` - `BEARING_WIDTH`/2)
= ±46.5, tube running inboard. This leaves a gap of `SHAFT_END_PLAY`/2 to the
shaft set end face at nominal. Print axis vertical, either end down.

### 3.4 Bearing coupon

A bar `BC_LENGTH` × `BC_WIDTH` × `BC_THICKNESS`. Five pockets, pitch
`BC_POCKET_PITCH`, on a line 15.0 from one long edge. Each pocket is cut with
the pillow block's pocket function at the matching value from
`BC_RIB_TIP_DIAS`, with the lip on the bed face and the pocket opening on the
top face exactly as in the block. The rib-tip value is engraved on the top face
in the label strip under each pocket (e.g. `21.8`).

Local origin at the centre of the bed (lip) face; +z up through the part. Print
orientation: that face down, the same orientation as the block, because hole
size depends on it.

---

## 4. Assembly

This needs three group functions, which is more than the baseline's one per
part:

| Group | Contents | Moves with take-up |
|---|---|---|
| `pillow_blocks` | 4 blocks | the tail two |
| `bearings` | 4 reference bearings | the tail two |
| `spacers` | 4 spacer tubes, placed per §3.3 | the tail two |

Each group takes the `takeup` argument like the existing groups. Add the
blocks and spacers to the whole-loop slat sweep as fixed parts. Each spacer
turns with its shaft, but it is axisymmetric, so a static placement is exact.

The bridge plate reference solid gains the holes of §2.5.

---

## 5. Acceptance criteria

Implement each criterion twice, as a `checks.py` entry and as a pytest test.
Tolerances are ±0.01 on lengths unless stated.

### 5.1 Pillow block, alone

1. Valid, single solid.
2. Bounding box 44.0 × 63.0 × 21.0 (x × y × z). The height 63.0 is
   `SHAFT_HEIGHT` + `PB_BOSS_RADIUS`.
3. Volume 15.0 .. 18.0 cm³. Estimated at about 16.4. Pin a ±3 % band on the
   first build.
4. Point (0, 48, 0), the pocket centre, is **outside**.
5. Point (0, 48 + 11.05, 0) is **inside** (on the +y rib). The same point rotated
   30° about the axis is **outside** (between ribs). Together these prove the
   rib count and phase.
6. Point (0, 48 + 10.3, 4.25) is **inside** (the lip ledge). Point
   (0, 48 + 7.0, 4.25) is **outside** (the lip hole).
7. Point (0, 48, -3.4) is **outside**: the pocket is open on the inboard face.
8. Point (14, 3.0, -9.75) is **outside** (in the insert pocket). Point
   (14, 6.8, -9.75) is **inside** (the skin above it).

### 5.2 Bearing in block (positive and negative controls)

9. **Positive control.** A reference bearing placed in the pocket (axis
   coincident, mid-plane at z = 0) clashes with the block, and the clash
   volume is 1.0 .. 10.0 mm³. That is rib interference only. Estimate about
   3 mm³ at `PB_RIB_TIP_DIA` 21.8; pin it on the first build.
10. **Negative control.** A block built with `PB_RIB_TIP_DIA` = 22.2 (ribs clear
    of the bearing) has **zero** clash volume with the same bearing, and a
    minimum distance between them of 0.0 (the lip contact) .. 0.01. This control
    must use a real clearance, not a touching surface, which is why it is 22.2
    and not 22.0 (baseline §9, rule 5).
11. Clash volume is monotonic: building at 21.6, 21.8 and 22.0 gives strictly
    decreasing clash volume.

### 5.3 Spacer and bearing, alone

12. Spacer: valid solid; bounding box 11.0 × 11.0 × 16.8; volume 0.64 .. 0.70 cm³.
13. Bearing: valid solid; bounding box 22.0 × 22.0 × 7.0; volume 2.25 .. 2.32 cm³.

### 5.4 In the machine, at take-up -4.0, 0 and +2.0

14. Blocks vs every slat, whole-loop sweep: minimum distance **≥ 5.0**. Expected
    minima are 5.79 from the tower inboard face to the slat ends at worst-case
    play, and 6.05 from the foot top to the returning cleat tips.
15. Returning-run clearance, asserted by name:
    `SHAFT_HEIGHT - cleat_tip_radius() - PB_FOOT_HEIGHT > 5.0` (6.05).
16. Spacers vs every slat, whole-loop sweep: minimum distance ≥ 5.0. Expected
    about 10.8 to the saddle tab tips (`saddle_tab_tip_radius()` - `SPACER_OD`/2).
17. Blocks, bearings and spacers vs belts and shaft sets: no clash; minimum
    distance ≥ 1.0 except the designed contacts (bearing bore on shaft,
    bearing on lip).
18. Spacer to shaft set end face, at nominal: gap = `SHAFT_END_PLAY`/2
    = 0.2 ± 0.01 on each side.
19. Blocks vs bridge plates: the block underside is coplanar with its plate top
    face (distance 0.0, no clash). Each block's footprint lies inside its own
    plate's outline in x and z.
20. Each insert-pocket axis passes through a `PLATE_PB_HOLE_DIA` hole in the
    plate. Check with a point-in-solid at the hole centre, mid-plate: the point
    is outside the plate.
21. The bearing axis of every block coincides with its shaft axis, within 0.01,
    at all three take-ups.
22. Both blocks on a shaft are mirror images: their outboard faces are at
    z = ±55.0 and their inboard faces at z = ±46.5.

---

## 6. Changes to record in the next baseline

- §6: the shaft height 48.0 becomes **fixed**, set by the pillow block. The
  word "standoff" is retired.
- §6: along each shaft, add *spacer 29.7 .. 46.5, bearing 46.5 .. 53.5, lip to
  55.0*. That leaves **17.5 of shaft beyond the outboard face** on each end for a
  coupler (the baseline's 22.5 was measured from the bearing centre).
- §5.3: the shaft set's axial position is set against the spacers with
  `SHAFT_END_PLAY`, not by caliper.
- §7.2 closed; §10 questions 4 and 6 closed.
- §7.4: the tail blocks occupy z = ±34 .. ±55 up to 63 above the tail plate, and
  move with the take-up. The hopper must clear them.
- Cut list: the end plates gain four Ø5.0 holes each.

---

## 7. Physical tests (insert into baseline §8)

These are independent of the belt tests and can run first.

| # | Test | Settles |
|---|---|---|
| B1 | Print the bearing coupon. Press a bearing into each pocket, loosest first (vise, M12 washer on the outer ring only). Pick the tightest pocket where the bearing seats flat on the lip, stays in when inverted and still spins as freely as out of the bag. Discard any bearing that went into a pocket that whitened, cracked or made it rough. | `PB_RIB_TIP_DIA` |
| B2 | Check that the lip bears on the outer ring only: the bearing, pressed into the chosen pocket, spins freely with the lip face flat on a table. | `PB_LIP_HOLE_DIA` |
| B3 | First block: an insert pressed in, bolted to a scrap of 9 plywood; push the shaft sideways and axially by hand. | `PB_FOOT_*`, `PB_BOSS_RADIUS` |
| B4 | After the first week of running (with baseline test 7): check that no outer ring turns in its pocket. If one does, a thin ring of epoxy at the pocket mouth. | whether the PETG press fit holds |

---

## 8. Assembly procedure (for the build notes, not the CAD)

1. Press heat-set inserts into both insert pockets of each block, from the
   underside.
2. Press a bearing into each block. Use a vise with the lip face on one jaw
   and an M12 flat washer between the other jaw and the bearing's outer ring.
   Stop when the bearing is flush with the inboard face.
3. Hang both belts, with slats as the baseline describes, around both shaft
   sets.
4. For each shaft: bolt one block to its plate finger-tight. Thread the shaft
   through that bearing, then through a spacer, the shaft set (inside the
   belts), the second spacer and the second block. Bolt the second block
   finger-tight.
5. Turn the shaft by hand while tightening the four M4 screws a little at a
   time, alternating blocks. If the shaft stiffens, loosen the block that
   caused it and repeat.
6. Slide the shaft set until both spacers are snug. Back it off by about half
   of `SHAFT_END_PLAY` so the shaft has a few tenths of end play, then tighten
   both grubs. **Fit no collars.**
