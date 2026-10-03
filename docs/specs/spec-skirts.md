# Side skirts, carry rail and support stations: specification

Written against `design-baseline-v5.md` (commit `8192562`). All dimensions are
millimetres and degrees. Status labels as in the baseline: **fixed**,
**catalogue**, **provisional**, **open**. "B§" points into the baseline,
"H§" into `hopper-spec-v1.md`.

**Supersedes** `phase2-cad-spec.md` for the skirts and posts. Its bridge-plate
subset is already built (phase 4) and stays. Phase 2's skirt geometry (3 ply
outboard of the slat ends, posts on all three middle plates) is replaced
wholesale; its intent, plywood walls on printed supports, carries over.

**Changes built parts** (unlike the hopper spec):

- the cleated slat: `CLEAT_LENGTH` 74 → 73 (§3.1);
- the hopper's carry rail: it now ends at the joint at t = 177, and is fixed
  through side inserts instead of bottom inserts (§4.1);
- the hopper's rail bridge: replaced by a split support station (§4.2–4.3).

It answers B§12 Q1 (skirts), Q2 (lateral support) and Q3 (belt support) for
the whole carrying run.

---

## 0. Decisions this spec is built on

| # | Decision | Source |
|---|---|---|
| D1 | The skirts **continue the hopper's channel unchanged**: inner face at `SKIRT_INSET` (38.0), bottom edge `SKIRT_GAP` (1.5) above the slat top, top at `SKIRT_HEIGHT` (28.0). Not phase 2's outboard skirt, which would put a step in the channel at the front wall | user, this spec §1 |
| D2 | **`CLEAT_LENGTH` = 73.0**, so the cleat end clears the skirt by 1.5 nominal and **0.79** at worst-case play (was 0.29), in the hopper's liners too | user |
| D3 | **The carry rail runs on to the head**, t ≈ 330, as a second rail. The joint between the two is **on a support station at t = 177**, so the hopper's rail is cut back from 140 to 177 | user |
| D4 | **Support stations are split**: two posts on the plate, and an arm bolted across them. The arm slides in sideways between the runs, so a station can be fitted with the belt on and tensioned | user |
| D5 | The station at 88.5 is **retrofitted** to the same split parts, replacing the one-piece rail bridge, so every station is the same and none needs the belt off | this spec; the user approved D4 without ruling on the retrofit. Reverse it by keeping `rail_bridge()` at 88.5 |
| D6 | Skirts are **6 ply**, not phase 2's 3 | this spec, §1 |

---

## 1. Concept

Along the run, carrying side, not to scale:

```
 t:  0   30          88.5     130 136   177           265.5        330   350 354
     |   [== rail A ===|========|===|===][== rail B ======|=========]      |   |
     |       hopper    S        |front  S  skirt =========S=================]  |
     tail            station    wall   station          station          head
                                            ^ joint                    shaft
```

- **Rails.** Rail A (the hopper's, t = 30 .. 176.75) and rail B
  (177.25 .. 330) are one section, the guide wheel's rim zone run straight
  (H§3.5). The lugs run in the groove over the whole carrying run except
  where they are on or near the wheels, so the ±0.71 lateral play holds
  everywhere. The lands sit 0.5 under the slats: at nominal tension nothing
  touches, and under load the slats land on the rail instead of sagging. That
  keeps the skirt gap at 1.5 .. 2.0 instead of opening as the belt sags.
- **Stations** on the three middle plates. The posts stand outboard of the
  returning run. The arm crosses between the runs and carries the rail ends.
  At 177 and 265.5 a skirt upright stands on each end of the arm.
- **Skirts**, one strip a side from the front wall's outer face (t = 136) to
  t = 350, bolted to the uprights.

Section across the run at a skirt station, z ≥ 0, offsets from the shaft
axis, not to scale:

```
       z = 0      8 10.7      36.5 38   40   44        54   64
 offset  |        |  |         |   |    |    |          |    |
  50.9   |        |  |         |   +---------+==========+          skirt top (h 28), upright top
         |        |  |         |   | skirt   | upright  |
  34.9   |   cleat tip (h 12) -+   | 6 ply   |  M4 csk  |
         |        |  |         |   |         |  x 2     |
  24.4   |        |  |         |   +---------+          |          skirt bottom (h 1.5)
  22.9   ===== slat top ===================]  |          |          slat end 40 +/- 0.71
  19.9   ----- slat contact face ----------]  |          |
  19.4   [lands]  |  |                        |          |
  12.0   [ rail ] [cheek]                     |          |
   4.0   [______]_[__]________________________+==========+          arm top, upright foot
 -12.0   ================== arm ==============+==========+          arm underside, post top
 -19.9   ----- returning slats ------------]  |   post   |
 -34.9   ----- returning cleat tips           |          |
 -48.0   ===================== plate top ====+----------+----+     pad, 2 x M4 through the plate
```

**Why the hopper's geometry and not phase 2's.** The liners are built with
their inner face at 38 over the slat ends. An outboard skirt from t = 136 on
would step the channel wall outward by 3.5 exactly where parts leave the
metering brush, and any part riding the wall would catch on the front wall's
edge coming back.

**Why 6 ply.** It matches the front wall, so the skirt's tail end butts the
front wall across its full thickness and the channel wall is continuous. Its
outer face then lands at z = 44, which is where the post's inner face is
already (`RAIL_POST_Z`), so the uprights stand straight up from the arm ends
with no inboard head reaching over the slat ends. Countersunk M4 heads sink
flush into 6 ply but not into 3. A 3 ply strip 214 long cantilevered 85 past
its last support would also be floppy.

**Why the arm slides in.** A one-piece bridge bolted to its plate is a
closed ring (arm, post, plate, post), and the belt loop passes through it.
Two closed loops cannot be linked without opening one, so a one-piece bridge
can only go in round a slack belt with the shafts out. A split station is
closed last, by sliding its arm in between the runs onto posts already
bolted down.

---

## 2. Coordinates and frame

- **Every part in this spec belongs to the machine frame (tilting)** and is
  placed with `at(t, offset, lateral, incline)`. Heights h above the slat
  top go through `hopper_offset(h)`, as in the hopper.
- **None is on the tail plate.** The groups still take `takeup` (B§11 rule 6)
  because rail A's tail end is checked against the tail at every take-up.
- Stations are at `STATION_T` = plate_t(1 .. 3) = 88.5, 177.0, 265.5.

---

## 3. Parameters

Everything below goes in `params.py`. "Derived" rows are computed there, not
typed in, with the assertion stated.

### 3.1 Slat

| Name | Value | Status | Notes |
|---|---|---|---|
| `CLEAT_LENGTH` | **73.0** (was 74.0) | provisional | cleat ends at z = ±36.5 |
| `SKIRT_CLEAT_CLEAR_MIN` | 0.75 | provisional | assert `SKIRT_INSET − CLEAT_LENGTH/2 − slat_lateral_play()` ≥ this (0.79) |
| `SKIRT_SLAT_LAP_MIN` | 1.0 | provisional | assert `SLAT_LENGTH/2 − slat_lateral_play() − SKIRT_INSET` ≥ this (1.29): the slat end always runs under the skirt |

The second assertion uses `geometry.slat_lateral_play()`, so it goes in a
check, not in `params.py`. The first can be written in `params.py` only by
repeating the play's formula, so put it in the check too.

### 3.2 Rails

| Name | Value | Status | Notes |
|---|---|---|---|
| `STATION_T` | (88.5, 177.0, 265.5) | derived | `CENTRE_DIST · i / (PLATE_STATIONS − 1)`, i = 1 .. 3. `RAIL_ARM_T_CENTRE` becomes `STATION_T[0]` |
| `RAIL_JOINT_GAP` | 0.5 | provisional | between rail A's head end and rail B's tail end |
| `RAIL_T0` | 30.0 | provisional, unchanged | rail A tail end |
| `RAIL_T1` | 176.75 (was 140.0) | derived | `STATION_T[1] − RAIL_JOINT_GAP/2` |
| `RAIL_B_T0` | 177.25 | derived | `STATION_T[1] + RAIL_JOINT_GAP/2` |
| `RAIL_B_T1` | 330.0 | provisional | rail B head end; bottom corner 4.9 from the head guide wheel rim |
| `RAIL_WHEEL_CLEAR` | 3.0 | provisional | least distance, either rail to either shaft set, every take-up |
| `RAIL_END_CHAMFER` | 45°, unchanged | | on the two **free** ends only (t = 30, 330) |
| `RAIL_JOINT_RELIEF` | 0.5 | provisional | 45° on every top edge (lands and groove flanks) at the two **joint** ends, instead of the lead-in |
| `RAIL_SIDE_INSERT_OFFSET` | 8.0 | provisional | offset of the side screws' axis; a Ø4.0 insert leaves 2.0 of rail below it and 4.4 under the groove bottom |
| `RAIL_FIT_SHIFT` | 3.0 | provisional | rail A goes in this far headward of its place and slides back under the seal clamp (which reaches t = 32.3), §5.2 |
| `RAIL_INSERT_X` | 6.0, unchanged | | ±, from each station centre along the run |
| `RAIL_INSERT_EDGE` | 4.0 | provisional | least distance from an insert centre to a rail end |

**Insert positions** follow from the stations: a rail has an insert at every
`STATION_T ± RAIL_INSERT_X` that lies on it at least `RAIL_INSERT_EDGE` from
its ends. Rail A: 82.5, 94.5, 171.0. Rail B: 183.0, 259.5, 271.5. At the
joint each rail end has one, 5.75 from its end.

Lengths: rail A 146.75, rail B 152.75. Both fit `PRINT_BED`.

### 3.3 Stations

The post and arm envelopes are the built rail bridge's (`RAIL_ARM_*`,
`RAIL_POST_Z`, `RAIL_PAD_*`, unchanged), so the hopper's clearances to it
still hold.

| Name | Value | Status | Notes |
|---|---|---|---|
| `RAIL_CHEEK_T` | 2.5 | provisional | two cheeks on the arm's top, either side of the rail |
| `RAIL_CHEEK_CLEAR` | 0.2 | provisional | each side, rail to cheek: cheeks at z = ±8.2 .. ±10.7 |
| `RAIL_CHEEK_TOP_OFFSET` | 12.0 | provisional | 7.9 under the slat contact face; the lug (≤ 5.5) and tabs (≥ 17.1) are clear of it in z |
| `STATION_POST_INSERT_X` | 7.0 | provisional | ±, along the run |
| `STATION_POST_INSERT_Z` | 49.0 | derived | mid-post, (`RAIL_POST_Z[0]` + `RAIL_POST_Z[1]`)/2; 2 × M3 heat-set inserts per post top |
| `STATION_ARM_CBORE_DEPTH` | 3.5 | provisional | M3 heads sunk in the arm top at the post bolts (only used at 88.5) |
| `UPRIGHT_SCREW_LEN` | 60.0 | provisional | M3 socket head, through upright and arm into the post's insert |
| `UPRIGHT_CBORE_DEPTH` | 7.95 | derived | upright height + arm thickness + `M3_INSERT_DEPTH` − `UPRIGHT_SCREW_LEN`, so the screw engages the whole insert |

The upright is `RAIL_ARM_LEN` (24) along the run and z = 44 .. 54 across,
from the arm top (offset 4.0) to the skirt top, `hopper_offset(SKIRT_HEIGHT)`
(50.947): 46.947 tall.

### 3.4 Skirts

| Name | Value | Status | Notes |
|---|---|---|---|
| `SKIRT_INSET`, `SKIRT_GAP`, `SKIRT_HEIGHT` | 38.0, 1.5, 28.0 | provisional, unchanged | the hopper's, by name |
| `SKIRT_THICKNESS` | 6.0 | provisional | plywood; assert `SKIRT_INSET + SKIRT_THICKNESS == RAIL_POST_Z[0]` |
| `SKIRT_T0` | 136.0 | derived | `HOPPER_FRONT_T + WALL_THICKNESS`, the front wall's outer face |
| `SKIRT_T1` | 350.0 | provisional | a slat rounding the head lifts its trailing top corner (swept radius 24.47) to within 0.31 of the skirt's bottom edge at t = 350; 350.34 is where that reaches 0.25. Asserted by the sweep (K2) |
| `SKIRT_EDGE_CHAMFER` | 0.5 | provisional | on the inner bottom edge, like the liner (H§4.2) |
| `SKIRT_BOLT_H` | (7.0, 21.0) | provisional | h of the two M4 per upright; along the run at the station centre |
| `M4_CSK_DIA` | 9.0 | catalogue | ISO 10642 head, 90°, sunk from the channel face |

Strip size: 214.0 × 26.5 × 6, two off, mirror images: the countersinks are
on the inner face and the holes are not symmetric along the strip (41.0 and
129.5 from the tail end).

### 3.5 Mass

| Name | Value | Status | Notes |
|---|---|---|---|
| `SKIRTS_HARDWARE_MASS` | 0.030 kg | provisional | from `--report` |
| `SKIRTS_MASS_RANGE` | (0.25, 0.40) kg | provisional | expected about 0.32: rail B 41 g, two stations 152 g, four uprights 54 g, skirts 41 g, hardware 30 g |

As for the hopper, the mass and centre of gravity are computed from the
solids (`PETG_DENSITY`, `PLY_DENSITY`), not typed in.

---

## 4. Parts

Local frames: +x along the run (headward), +y along the run normal, +z
across, with the origin on the mating face named. Placing a part is one
`at()`. Mirror sides by a 180° turn about local y wherever the part is
symmetric in x (posts, uprights), so one part serves both sides.

### 4.1 Carry rail, `parts/carry_rail.py`, printed PETG, 2 off

`carry_rail(t0, t1, free_ends, raise_by)`: generalises the built rail.

- **Section:** unchanged, from `guide_groove_section()`.
- **Ends:** a free end gets the `RAIL_END_CHAMFER` lead-in; a joint end gets
  `RAIL_JOINT_RELIEF` on its top edges and is otherwise square. `free_ends`
  says which. Rail A = (30, 176.75, tail end free); rail B =
  (177.25, 330, head end free).
- **Fixing:** M3 heat-set inserts in the **+z side face** at
  `RAIL_SIDE_INSERT_OFFSET`, at the positions of §3.2. The bottom inserts go.
- **Local origin:** unchanged: the land plane, centre plane, at t0.
- **Print orientation:** unchanged: bottom down, groove up.
- **Bounding boxes:** rail A 146.75 × 15.447 × 16, rail B 152.75 × 15.447 × 16.
  Volumes 27–35 and 28–37 cm³.

### 4.2 Station post, printed PETG, 6 off, identical

- **Shape:** the built bridge's post and pad as one part: a column at
  z = 44 .. 54, `RAIL_ARM_LEN` along the run, from the plate top (−48) up to
  the arm's underside (−12), and a pad `RAIL_PAD_THK` thick outboard to
  z = 64.
- **Holes:** the pad's 2 × M4 through the plate (`RAIL_PAD_BOLT_X`,
  `RAIL_PAD_BOLT_Z`, unchanged); 2 × M3 heat-set insert pockets down from the
  column top (`STATION_POST_INSERT_X`, `_Z`).
- **Local origin:** the pad's bottom face, at the column's inner face
  (z = 44), centred on the station. Placed with
  `at(T, plate_top_offset(), ±RAIL_POST_Z[0])`, the −z one turned 180° about y.
- **Print orientation:** on its headward face (section flat), no support.
- **Bounding box** 24 × 36 × 20. Volume 8–12 cm³.

### 4.3 Station arm, printed PETG, 3 off, identical

- **Shape:** the built bridge's arm, `RAIL_ARM_LEN` × `RAIL_ARM_OFFSET` ×
  z ±`RAIL_ARM_HALF_W`, plus two **cheeks** on its top face, `RAIL_CHEEK_T`
  thick at z = ±(8.2 .. 10.7), from the arm top (4.0) to
  `RAIL_CHEEK_TOP_OFFSET`, the full arm length.
- **Holes:**
  - 4 × M3 clearance down through the arm ends onto the post inserts, with a
    `STATION_ARM_CBORE_DEPTH` counterbore from the top;
  - 2 × M3 clearance through the +z cheek along z, at `RAIL_INSERT_X`, on
    the side-insert axis.
  - The built bridge's two counterbored M3 from below go: nothing now hangs
    under the arm toward the returning lugs.
- **Local origin:** the arm's bottom face, centre plane, centred on the
  station. Placed with `at(T, RAIL_ARM_OFFSET[0])`.
- **Print orientation:** on its headward face, no support (the cheeks are in
  the section).
- **Bounding box** 24 × 24.0 (16 + the 8.0 cheeks) × 108. Volume 36–46 cm³.

The two rails at 177 sit between the same pair of cheeks, so the cheeks line
the two grooves up to each other by construction; the M3 hole clearance
does not enter into it.

### 4.4 Skirt upright, printed PETG, 4 off, identical

- **Shape:** a block `RAIL_ARM_LEN` along the run, z = 44 .. 54, from the arm
  top to the skirt top, 46.947 tall.
- **Holes:**
  - 2 × M3 clearance top to bottom at (`STATION_POST_INSERT_X`, z = 49),
    counterbored `UPRIGHT_CBORE_DEPTH` from the top. One M3 × 60 each
    clamps upright, arm and post together.
  - 2 × M4 clearance along z at `SKIRT_BOLT_H`, x = 0, for the skirt; a
    nylock and washer on the outboard face.
- **Local origin:** its bottom face, at its inner face (z = 44), centred on
  the station. Placed with `at(T, RAIL_ARM_OFFSET[1], ±RAIL_POST_Z[0])`, the
  −z one turned 180° about y.
- **Print orientation:** bottom face down, so the long M3 holes are vertical.
- **Bounding box** 24 × 46.947 × 10. Volume 9–12.5 cm³.

### 4.5 Skirt, plywood 6, cut list, 2 off (mirror pair)

- **Shape:** a strip from `SKIRT_T0` to `SKIRT_T1`, h = `SKIRT_GAP` to
  `SKIRT_HEIGHT`, inner face at z = ±`SKIRT_INSET`, 6 thick outboard.
  `SKIRT_EDGE_CHAMFER` on the inner bottom edge.
- **Holes:** 4 × Ø4.5, countersunk `M4_CSK_DIA` from the inner face, at
  t = 177 and 265.5, h = `SKIRT_BOLT_H`.
- **Local origin:** the inner face, at the bottom edge, at `SKIRT_T0`. Placed
  with `at(SKIRT_T0, hopper_offset(SKIRT_GAP), ±SKIRT_INSET)`, the −z one
  mirrored (it is a different strip, not a turned copy).
- **Leaves the project** as a cut-list entry, both strips, with hole
  positions from the tail end and bottom edge, the countersink face, and
  the edge chamfer.

### 4.6 Removed

`rail_bridge()` goes, with its STL, its group member and its two bottom M3
screws. Its checks move to the stations (§8).

### 4.7 Bought parts

| Item | Qty | Use |
|---|---|---|
| M4 × 25 + nylock + 2 washers | 12 | station pads through the plates (4 already listed for 88.5) |
| M3 heat-set insert | 12 + 6 | post tops; rail side faces (replacing the hopper's 2 bottom inserts) |
| M3 × 16 socket head | 4 | arm to posts at 88.5 |
| M3 × 60 socket head | 8 | uprights, arms and posts at 177 and 265.5 |
| M3 × 8 socket head | 6 | through the cheeks into the rails (replacing the hopper's 2) |
| M4 × 20 countersunk + nylock + washer | 8 | skirts to uprights (grip 16) |

Exact lengths are the implementation's to settle against the stack and list
in `--report`; the rule is that every M3 engages at least 3.5 of its insert.

---

## 5. Groups and fitting

### 5.1 What goes where

- **`hopper`** keeps what is under the hopper: **rail A** and the **station
  at 88.5** (two posts and an arm, no uprights), in place of the rail and
  bridge. Its labels change; its checks follow (§8).
- **`skirts`**, new: **rail B**, the stations at 177 and 265.5 (posts, arms),
  the four uprights and both skirts. One `skirts_group(detail, takeup,
  incline)`, one `GROUPS` entry, one `COLOURS` entry.

### 5.2 Fitting sequence

This replaces H§4.7's "the belts must be off, or a slat removed at the arm".

1. Posts on the three plates, at any time.
2. Belt loop on and tensioned; slats on.
3. Each arm slid in sideways between the runs onto its posts and screwed
   down. At 177 and 265.5 the path is open. At 88.5 it is blocked by the
   hopper's side panel: take one panel off (its two feet's M5, the M4s
   through it, and the liner screwed to it come with it).
4. Rails lowered between the belts onto the arms, between the cheeks, with
   the slats over them unclipped (about 8 for rail A, 9 for rail B). Rail A
   first: with the metering clamp off (two wing nuts), it goes down
   `RAIL_FIT_SHIFT` headward of its place, clear of the seal clamp, and
   slides tailward along the cheeks under it. Then rail B, straight down.
   Side screws in through the +z cheek, a hex key reaching in between the
   runs from outboard. Slats back, each against the belt teeth (B§10).
5. Uprights on the arm ends at 177 and 265.5 with the M3 × 60s.
6. Skirts on the uprights.

A rail on the arm cannot be slid in with the arm: its lands stand above the
carrying slats' tab tips.

---

## 6. Interfaces and keep-outs

1. **Hopper.** The skirt's tail end touches the front wall's outer face at
   t = 136 (a butt joint; a touch, not a clash). Its inner face and bottom
   edge are coplanar with the liner lower wall's. No upright is within 3.0
   of any hopper part.
2. **Head.** Skirts stop at 350, rail B at 330. Both stay ≥ 3.0 from the head
   shaft set, pillow blocks, bearings, spacers, the motor bracket, motor and
   coupler, with `DRIVE_SIDE` both ways.
3. **Returning run.** Posts and arms are the built bridge's envelope: ≥ 3.0
   from every returning slat, cleat and belt. Uprights are above the arm,
   on the carrying side; ≥ 3.0 from the slat ends at full play (3.29).
4. **Under the frame.** Nothing here goes below the plate top faces.
5. **Discharge.** Out of scope (B§12 Q9, Q10). The skirts end at 350 and do
   not shape the discharge; a chute spec may extend or trim them.

---

## 7. Loads

The `skirts` group adds about 0.32 kg on the frame around t = 245, ahead of
the hinge. Treat it like the hopper: mass and centre of gravity from the
solids plus `SKIRTS_HARDWARE_MASS`, one more entry in the prop's load list.

On today's loads, a 0.3 kg point at (245, 10) raises the doubled prop force
at 25° from 209.7 to about **224 N**, leaving about **26 N** under
`PROP_FORCE_MAX`. The check's number is the authority; print it.

---

## 8. Acceptance criteria

Each in `checks.py` and as a pytest test. "Nine cases" as in H§8.

**S. Parameters**

- S1. `SKIRT_INSET − CLEAT_LENGTH/2 − slat_lateral_play()` ≥
  `SKIRT_CLEAT_CLEAR_MIN` (0.79 ≥ 0.75).
- S2. `SLAT_LENGTH/2 − slat_lateral_play() − SKIRT_INSET` ≥
  `SKIRT_SLAT_LAP_MIN` (1.29 ≥ 1.0).
- S3. `SKIRT_INSET + SKIRT_THICKNESS == RAIL_POST_Z[0]`;
  `SKIRT_T0 == HOPPER_FRONT_T + WALL_THICKNESS`.
- S4. `RAIL_B_T0 − RAIL_T1 == RAIL_JOINT_GAP`, centred on `STATION_T[1]`;
  every rail insert ≥ `RAIL_INSERT_EDGE` from its rail's ends; each rail
  has at least one insert per station it crosses.

**R. Rails**

- R1 (H C2, extended). For both rails, at every take-up: no lug clashes
  with either rail. At 40° and take-up 0, every slat over either rail has
  its contact face 0.45 .. 0.55 from the lands.
- R2 (H C3, extended). Either rail raised by 1.0 clashes with at least one
  slat, volume > 1 mm³.
- R3. **Joint.** The two rails' land planes coincide within 0.01, their
  groove centre planes within 0.01, and the gap is `RAIL_JOINT_GAP` ± 0.01.
  The joint ends carry no lead-in chamfer: at 1.0 from each joint end, the
  land is at the rim station within 0.01.
- R4. **Coverage.** Every carrying-run slat whose lug centre lies in
  [`RAIL_T0` + `LUG_LENGTH`, `RAIL_B_T1` − `LUG_LENGTH`] has its lug over a
  rail, except across the joint gap.
- R5. Both rails ≥ `RAIL_WHEEL_CLEAR` from both shaft sets, at every
  take-up. Negative control: rail B with `RAIL_B_T1` = 345 is < 3.0.
- R6. Each rail sits between the cheeks of every arm it crosses: no clash,
  and 0.2 ± 0.01 to each cheek.

**K. Skirts**

- K1. **Continuity.** At t = 136 the skirt's inner face is at
  z = ±`SKIRT_INSET` and its bottom edge at h = `SKIRT_GAP`, coplanar with
  the liner's lower wall within 0.01. Skirt and front wall do not clash
  (tolerance 0.01 mm³) and touch (distance < 0.01).
- K2. **Whole-loop sweep** (B§11): add the `skirts` group to the fixed
  parts. No clash, and ≥ `HOPPER_SLAT_CLEAR` (0.25) from every slat, at all
  nine cases, over the head arc included.
- K3. With slats pushed ±`slat_lateral_play()`, the tightest slat-to-fixed
  pair is a cleat end against a liner or skirt at 0.79 ± 0.01. Report it by
  name. This replaces H C1's expected 0.29.
- K4. Skirts ≥ 3.0 from the head shaft set, pillow blocks, bearings,
  spacers and the whole `drive` group, with `DRIVE_SIDE` = +1 and −1.

**T. Stations**

- T1 (H C10, extended). Every post and arm, at all three stations, ≥ 3.0
  from every returning slat (cleats included) and both belts, at all nine
  cases.
- T2. Every upright ≥ 3.0 from every carrying slat at full lateral play.
- T3. **Arm fitting path.** At each station, a box with the arm's section
  in t × offset, from the arm's +z end out to z = `FRAME_WIDTH`, clashes
  with nothing in `frame`, `plates`, `belts` or `slats` (all take-ups) or
  in the station's posts (tolerance 0.01 mm³: the arm slides on the post
  tops). At 88.5 the +z side panel, its liner and its feet are left out,
  as §5.2 step 3 removes them. Negative control: the same box at 88.5 with
  the panel in clashes.
- T4. **Rail fitting path.** Rail B's solid swept straight up along the run
  normal to offset 60 clashes with nothing in `belts`, `pillow_blocks` or
  `drivetrain`. Rail A's, moved `RAIL_FIT_SHIFT` headward, likewise, and
  also with the `hopper` parts except the metering clamp and brush; and
  rail A swept from there back to its place along the run clashes with no
  hopper part (the seal bristles stop at t = 29.45). Negative control:
  rail A swept up from its own place clashes with the seal clamp.
- T5. Uprights and posts ≥ 3.0 from every hopper part.

**V. Parts**

- V1. Validity for every new or changed solid: both rails, post, arm,
  upright, both skirts.
- V2. Bounding boxes ± 0.02 and volumes in the ranges of §4.
- V3. Every printed part fits `PRINT_BED` in its print orientation
  (H C11, unchanged).
- V4. The cleated slat's volume range is recomputed for the 73 cleat and
  still holds the plain slat below it.

**M. Loads**

- M1. `skirts` mass within `SKIRTS_MASS_RANGE`. Hopper mass still within
  `HOPPER_MASS_RANGE` with rail A's new length and the split station.
- M2 (H D2, extended). Doubled (frame + drive + hopper + full load +
  skirts) ≤ `PROP_FORCE_MAX` at every 2.5°. Print the 25° margin.
- M3 (H D3, extended). ≥ `PROP_FORCE_MIN` at every 2.5°, hopper empty and
  full, with the skirts.

---

## 9. What this adds to the project

1. `params.py`: §3; `CLEAT_LENGTH`, `RAIL_T1` and `RAIL_ARM_T_CENTRE`
   changed; the provisional skirt block replaced; hardware tuples updated.
2. `geometry.py`: `station_t(i)` if wanted (or `plate_t`), and nothing else.
   Skirt positions are `hopper_offset()` and `at()`.
3. `parts/carry_rail.py`: `carry_rail(t0, t1, free_ends, raise_by)`;
   `rail_bridge()` removed.
4. `parts/station.py`: `station_post()`, `station_arm()`, `skirt_upright()`.
5. `parts/skirt.py`: `skirt(side)`, the plywood reference solid.
6. `parts/slat.py`: nothing but the parameter.
7. `assembly.py`: the `hopper` group's rail and station; `skirts_group`,
   its `GROUPS` and `COLOURS` entries; the whole-loop sweep's fixed parts.
8. `checks.py`, `tests/`: §8; H C1's 0.29 expectation, C2, C3, C10 and D1–D3
   updated as listed there.
9. `export.py`: `carry_rail` (A), `carry_rail_b`, `station_post`,
   `station_arm`, `skirt_upright`; `rail_bridge` removed.
10. `cut_list.py`: both skirt strips.
11. `README.md` ("Skirt resolutions"), `CLAUDE.md` status, and a design
    baseline v6 once built.

---

## 10. Open inputs

| Input | Current assumption | Affects |
|---|---|---|
| 6 ply for the skirts | the same sheet as the hopper's walls | §3.4; 3 ply would need an inboard head on the upright |
| `SKIRT_T1` and the discharge | 350, square end | a chute spec may change it |
| `PLY_DENSITY` | 0.60 | M1, M2 |
| Retrofit at 88.5 (D5) | yes | §5.1; keeping the one-piece bridge leaves that station belts-off only |

---

## 11. Physical tests to add

After H2 (rail entry), in order.

| # | Test | Settles |
|---|---|---|
| S1 | Fitting: with the belt tensioned, slide each arm in, drop both rails in with their slats unclipped, refit the slats against the teeth | §5.2; `RAIL_CHEEK_CLEAR` |
| S2 | Joint: run at 40°, watch and listen at t = 177: no click as lugs cross; a fingernail finds no step across the lands | `RAIL_JOINT_GAP`, `RAIL_JOINT_RELIEF` |
| S3 | Rail B: press the run at mid-span, t ≈ 250, and confirm the slats land on the lands; release and they lift clear | `RAIL_B_T1`, the 0.5 land gap away from the hopper |
| S4 | Skirt gap: feeler-gauge the 1.5 over the slat tops from 136 to 350 at 40°, and the cleat end to skirt with slats pushed each way (1.5 nominal, 0.79 least) | `SKIRT_GAP`, `CLEAT_LENGTH` |
| S5 | Run 10 min with 1 L at 25°, 40°, 55°: nothing over the skirt tops, nothing under their edges, nothing wedged between a cleat end and a skirt; repeat H7's thin parts along the skirts | `SKIRT_HEIGHT`, `SKIRT_GAP` |
| S6 | Weigh the `skirts` parts; rerun M2 | `SKIRTS_MASS_RANGE`, the prop margin |
