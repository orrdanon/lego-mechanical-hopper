# lego-mechanical-hopper

Parametric build123d model of the LEGO-sorter feed elevator, structured as
parts that assemble. Phase 1 built the conveyor slat (plain and cleated);
phase 4 added the assembly framework with the aluminium frame and the
plywood bridge plates as its first two groups; the drivetrain spec added
the tooth profile, the printed shaft sets, shafts, belts and the slats
running round both ends; the tilt spec made the incline adjustable by hand
over 25..55 degrees, with a hinge, a cross-member and a screw prop; the
hopper spec added the hopper, its brushes and a carry rail under it; the
skirts spec the side skirts, the carry rail on to the head and the split
support stations. See the `phase*-cad-spec*.md` files, `drivetrain-spec.md`,
`spec-tilt.md`, `hopper-spec-v1.md` and `spec-skirts.md` in `docs/specs/`: each phase depends on the earlier
ones, and each rev diffs against the previous one rather than replacing it.

For a single self-contained summary of what is built and decided, written
for readers outside the project and as the input to new specifications, see
`docs/design-baseline-v6.md`. Its numbers are taken from `params.py`:
regenerate them when parameters change. The earlier versions are frozen
snapshots kept as the reference of the spec written against each:
`docs/design-baseline-v5.md` (commit `8192562`, the input to spec-skirts,
before the skirts, rail B and the split stations),
`docs/design-baseline-v4.md` (commit `9461b13`, with the pillow blocks,
before the drive, the hopper and pin B at 140),
`docs/design-baseline-v3.md` (commit `ca50e1a`, before the pillow blocks) for
`spec-pillow-blocks.md`, `spec-drive.md`, `hopper-spec-v1.md` and anything
else written before it,
`docs/design-baseline-v2.md` (commit `ad71c0e`, before the tilt) for
`spec-tilt.md`, and `docs/design-baseline-v1.md` (commit `98f4fb1`, with the
uncorrected belt-back radius) for `drivetrain-spec.md`.

## Setup

```bash
python3 -m venv .venv        # or reuse the repo's existing .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run everything below from the repo root.

## Viewing a part

With the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer)
VS Code extension running (`ocp_vscode` connects to it over a websocket),
run any part module directly:

```bash
python3 parts/slat.py
```

This opens the viewer showing a plain slat. `parts/shaft_set.py` (teeth
and guide groove visible), `parts/shaft.py`, `parts/belt.py`,
`parts/coupons.py`, `parts/frame.py`, `parts/bridge_plate.py`,
`parts/hopper.py` (liners and walls) and `parts/carry_rail.py` (the rail on
its bridge) work the same way. Without a running viewer
server, `ocp_vscode` prints a connection warning but the geometry still
builds correctly (exit code 0) -- useful for a headless sanity check.

## Viewing the assembly

```bash
python3 assembly.py                 # every group
python3 assembly.py frame           # just the frame
python3 assembly.py frame plates    # both, in position
python3 assembly.py plates --detail
python3 assembly.py frame plates drivetrain belts slats   # the machine
python3 assembly.py plates pillow_blocks bearings spacers drivetrain   # the shaft mounts
python3 assembly.py plates pillow_blocks drivetrain drive              # the motor on the head shaft
python3 assembly.py "drivetrain:tail shaft" "drivetrain:tail shaft set"   # single members
python3 assembly.py drivetrain belts "slats:slat ?" --detail               # real slats 0-9 only
python3 assembly.py frame plates slats hopper   # the hopper over the carrying run
python3 assembly.py plates slats hopper skirts   # and the skirts, rail B and stations on to the head
python3 assembly.py --incline=55    # the whole machine tilted; INCLINE (40) if not given
python3 assembly.py --report        # no viewer: each group's members, and the bought hardware
```

A name is a group, or `group:pattern` for just the members whose label
matches the glob pattern; a pattern matching nothing lists the group's
member labels. So the drivetrain can be built up one part per run, and
`slats` on its own is the shortcut for all 46.

Each group is shown in its fixed colour from `assembly.COLOURS` and named
in the viewer tree, with its members labelled (`plate 0 (bearing)`, `rail
+z`, `head shaft set`, `slat 12`, ...). `--detail` is accepted by every
group. `slats` draws a few plain boxes per slat (body, cleat, tabs) without it and real slats with
it; `belts` draws the smooth backing band without it and both 276-tooth
loops with it. The rest ignore it.

`--incline` tilts the conveyor about the machine origin (the tail shaft
axis); the base is what moves in machine coordinates. The `tilt` group's
`base_ref` slab is a **placeholder** for the undecided base: it is shown in
its own muted colour (`assembly.PLACEHOLDERS`), flagged in `--report`, and
never exported.

## Running checks

```bash
python3 checks.py
```

Prints one line per acceptance check from rev B §5, phase 4 §8,
drivetrain-spec §4.4 and §12, spec-tilt §8.2, spec-pillow-blocks §5,
spec-drive §8, hopper-spec §8 and spec-skirts §8, and exits non-zero if any
fail. It takes about four minutes, most of it the whole-loop clearance sweep,
which runs at three take-ups and three inclines. It ends with the
**setting-up table** (spec-tilt §8.3): prop length and exposed rod against
incline, which is how the angle gets set by hand -- see "Tilt" below --
then the hopper's table of wall slopes, level fill, rim heights and prop
force every 2.5 degrees, and the skirts' mass and tight pairs. This is the same set of assertions as the
pytest suite, just human-facing. A check listed in `_EXPECTED_FAILURES`
prints `XFAIL` with its recorded reason instead of failing the run, and
prints `XPASS` and fails the run if it unexpectedly passes -- that is the
cue to delete the entry (and the matching `strict=True` xfail in `tests/`).

## Running tests

```bash
python -m pytest
```

## Exporting STLs

```bash
python3 export.py
```

Writes `out/slat_plain.stl`, `out/slat_cleated.stl`, `out/shaft_set.stl`
(print two, axis vertical, either end down, PETG, no support),
`out/ring_coupon.stl` and `out/guide_coupon.stl`, each print-rotated per
its `params.PRINT_ROT_*`. `out/` is gitignored. **Print in the order of
"Physical calibration" below** -- the coupons gate the shaft set, and no
slats should be batch-printed before the saddle and guide fits pass.

The tilt mechanism adds `hinge_bracket_R/L`, `hinge_block_R/L`,
`frame_clevis`, `prop_body`, `prop_foot`, `knob` and `base_pin_block`
(spec-tilt §8.4). R is the machine's +z side, the right-hand one looking
from tail to head. `prop_body` has a closed nut pocket: pause the print at
its ceiling and drop the M8 nut in.

The pillow blocks add `pillow_block` (print four, lip face down, no
support), `spacer` (print four, axis vertical) and `bearing_coupon` (print
first, lip face down like the block; see "Pillow blocks" below). The
608ZZ bearings are bought and not exported.

The drive adds `motor_bracket` (print one, foot down, no support; see
"Drive resolutions" for why not face plate down). The motor and coupler are
bought and not exported.

The hopper adds `hopper_liner_R/L`, `seal_clamp`, `metering_clamp`,
`hopper_foot_R/L` (print two of each), `corner_cleat` (print eight) and
`carry_rail` (rail A; hopper-spec §9.9). The seal clamp prints on its end;
see "Brush clamps" below.

The skirts add `carry_rail_b`, `station_post` (print six), `station_arm`
(print three) and `skirt_upright` (print four); one set of posts and an arm
is the hopper's station at 88.5, which replaced its `rail_bridge`
(spec-skirts §4).

Every printed part fits the printer, a **Bambu Lab P1S** (`PRINT_BED` = 256
x 256 x 256), in its print orientation, and `checks.py` holds all of them to
it (hopper-spec C11 asked it of every printed part). The largest are
rail B, 152.75 long, the bearing coupon, 150, and rail A, 146.75.

The frame and shafts are owned or bought hardware, the belt and brushes are
bought, and the bridge plates, the hopper's panels and walls and the skirts
are cut from plywood, so none is exported as STL. `python3 cut_list.py` writes
`out/cut_list.txt` with the plate rectangle and hole positions, the tilt's
cross-member (2020, 234), its prop rod (M8, 128), the two shafts (tail 145,
head 140), the hopper's four boards as corner and hole coordinates, and the
two skirt strips instead.

## The assembly framework (phase 4)

### Four layers, reading downward only

| Layer | Answers | Returns | May import |
|---|---|---|---|
| `params.py` | what did we choose | floats | `math` |
| `geometry.py` | where, how far | floats, `Location` | `params` |
| `profile.py` | what tooth form | `Edge`, `Face` | `params` |
| `parts/*.py` | what shape | `Part` | `params`, `geometry` |
| `assembly.py` | what goes where | `Compound` | all three |

`geometry` never builds a solid, and `profile` stops at 2D edges and faces. A part returns a solid in its own local
frame and never computes a machine position; it may import a scalar from
`geometry` when that scalar is one of its own dimensions. `frame()` is the
one exception -- it returns a Compound already positioned in the machine,
because there is exactly one frame and it is a fixed piece of the world.

### Local origin at the mating surface

Every part's origin sits on the face that mates with something else, so
placing it is a single `at()` call with no corrective offset:

- bridge plate: centre of its top face (pillow blocks and posts bolt here)
- frame rail: centre of its top face (plates sit here)
- slat: centre of its belt-contact face
- shaft set and shaft: on the axis, at the centre plane of the guide groove
- belt loop: the tail shaft axis, +x along the run

Local axes for anything placed by `at()`: +x along the run, +y out along
the run normal, +z across the machine. Each part's docstring states its
origin; when a future part sits 9 mm out of place, that is the first thing
to check.

### How to add a group

1. Write `<name>_group(detail: bool = False, takeup: float = 0.0) -> Compound`
   in `assembly.py`, building parts and placing them with `at()`,
   `loop_at()` and the `geometry` datums. No new positions invented inside
   the part modules. `takeup` slides whatever rides on the tail bridge
   plate; a group that doesn't, ignores it.
2. Add `"<name>": <name>_group` to `GROUPS` and a fixed colour to `COLOURS`.
3. Add its acceptance checks to `checks.py` and `tests/`.

If adding a group needs more than that, the framework is wrong and should
be fixed rather than worked around (phase 4 §10).

## Phase 4 resolutions

Four places where the phase 4 spec conflicted with the repo or with itself,
resolved from the spec's named-parameter definitions rather than its
worked examples, per the convention in `CLAUDE.md`.

### Offset origin

Phase 1's `at(t, offset)` measured `offset` outward from the belt's back
face. Phases 2-4 measure every offset from the shaft axis: phase 4 §10
places a shaft with `at(t, 0)`, and `rail_top_offset() = -57` and
`plate_top_offset() = -48` only make sense from the axis. `at()` now
measures from the shaft axis. A slat on the carrying run is placed at
`at(t, belt_back_radius())`, and the one phase-1 test that pinned `at(0)`
to the belt back was updated. Keeping the belt-relative convention would
have left every later spec number 22.3 mm off.

### Bridge plate length

Phase 2 §4 tabulates `PLATE_LENGTH = FRAME_INNER_WIDTH` (234). A plate of
that length fits *between* the rails and rests on nothing, while phase 4
defines `rail_top_offset()` as "the surface the plates sit on" and puts
the plate holes "in the rail slots". Those definitions win:
`PLATE_LENGTH = FRAME_WIDTH` (274), the plate rests on both rail tops, and
its holes sit at `PLATE_BOLT_Z = FRAME_WIDTH/2 - FRAME_PROFILE/2 = 127`,
on the top-slot centrelines (phase 4 §6's `FRAME_INNER_WIDTH/2 - 10 = 107`
would miss the slots by 20 mm). Phase 4 §8.4 is checked against
`PLATE_LENGTH`, and an extra check probes that each hole sits over an open
slot. If the plates are meant to be held between the rails by angle
brackets instead, change `PLATE_LENGTH` and `PLATE_BOLT_Z` back and drop
the "sit on the rails" checks.

### Frame bounding box

Phase 4 §8.2 asserts the longest axis-aligned extent of the placed frame is
`FRAME_LENGTH`, while noting the frame is inclined. Inclined at 40°, the
longest extent is `FRAME_LENGTH*cos(40°) + FRAME_PROFILE*sin(40°)` = 435.7,
not 552. The check asserts that projection, and the exact
`FRAME_LENGTH x FRAME_PROFILE x FRAME_WIDTH` box is checked in the frame's
own local frame, as §8.2 invites, by undoing `at(frame_t_centre(),
rail_top_offset())`.

### Plate overlap and `CENTRE_DIST` (resolved by rev D)

Phases 2-4 were written against a 390mm centre distance; rev C's belt gave
135mm, so five 45mm plates at a 33.75mm pitch overlapped and phase 4 §8.5
could not pass. It was carried as a strict expected failure until rev D
changed the belt (see "Belt, slat pitch and width, rev D"). With
`CENTRE_DIST = 354` the pitch is 88.5mm and §8.5 passes; the xfail and the
`_EXPECTED_FAILURES` entry have been removed. The mechanism stays in
`checks.py` for the next such case.

## Drivetrain

`docs/specs/drivetrain-spec.md` rev B. One printed **shaft set** per shaft
carries both toothed pulleys and a central V-grooved guide wheel, so the two
belts are in phase by construction; a **lug** under every slat runs in the
groove and is the machine's only lateral constraint. The tail bridge plate
slides in its T-slots as the take-up.

### Belt-back radius correction (2026-09-21)

Phase 1 defined `belt_back_radius()` as `PULLEY_PD/2 - BELT_PLD +
BELT_THICKNESS` = 21.118, which puts the belt's tooth *tips* on the pulley
OD. It is the belt's *land* that rests on the OD, with the teeth down in
the grooves, so the radius is `PULLEY_OD/2 + BELT_BACK_THICKNESS` =
**19.947** -- one tooth height (1.171) less. The error was in the phase 1
spec, not its implementation (drivetrain-spec §0). Every radial station
moved with it: slat top 22.947, cleat tip 34.947, returning-run clearance
to the plates 13.05 (was 11.9). `checks.py` and `tests/test_drivetrain.py`
now assert the three facts that would have caught it: tooth tips inside
the OD, pitch line inside the backing, tooth tips above the groove bottom.

### Pulley groove: source and licence

The groove is the standard HTD-3M groove **for 40 teeth**, rebuilt in closed
form by `profile.py` from five `PULLEY_GROOVE_*` values read out of CADENAS
PARTsolutions model 40015040, a 40-tooth HTD-3M pulley for 15 mm belt. The
model belongs at `reference/htd3m_40t_40015040.stp`, stored unmodified and
never written or imported by the project; its header gives the licence as
**CC BY-ND 4.0, credit CADENAS**. The rebuild is tested against four
junction points read from that file's B-rep and meets them to 0.0025, the
residual being the file's rounded OD. `pulley_section()` is the only thing
that makes teeth -- the shaft set and the ring coupon both use it -- and it
refuses any tooth count but 40. Never change a `PULLEY_GROOVE_*` value to
make a print or a check fit; `FLANK_RADIUS` and `ROOT_RADIUS` now shape the
belt *model* only, and are what to tune if the mesh check (§12.4) fails.

**The STEP file is not yet in the repo.** It was not available when the
drivetrain was implemented; see `reference/README.md`. Nothing at run time
or in the tests needs it.

### Parameters awaiting physical calibration

Set by drivetrain-spec §13, all provisional until then:

| Parameter | Now | Settled by |
|---|---|---|
| `BELT_THICKNESS` | 2.4 | step 1, caliper the belt (2.44 on some sheets) |
| `PULLEY_OD_COMP`, `PULLEY_GROOVE_COMP` | 0.0, 0.0 | step 2, ring coupon |
| `SADDLE_TAB_DEPTH`, `SADDLE_INTERFERENCE`, `SLAT_WIDTH` | 3.6, 0.2, 17.0 | step 3, saddle fit and printed width |
| `LUG_DEPTH`, `LUG_TIP_WIDTH`, `LUG_LENGTH`, `GROOVE_FLANK_CLEAR`, `GUIDE_WIDTH` | 4.0, 3.0, 8.0, 0.5, 16.0 | step 4, guide coupon |
| `DRUM_DIA`, `PULLEY_SKIRT_R`, `GRUB_Z`, `PULLEY_INSERT_DEPTH` | 26.0, 16.8, 17.5, 6.0 | step 5, first shaft set |
| `TAIL_TAKEUP_MIN`, `TAIL_TAKEUP_MAX` | -4.0, 2.0 | step 6, assembly |
| `PB_RIB_TIP_DIA` | 21.8 | pillow-block test B1, bearing coupon (below) |
| `PB_LIP_HOLE_DIA` | 16.0 | pillow-block test B2 |
| `PB_FOOT_*`, `PB_BOSS_RADIUS` | 44.0 x 7.0, 15.0 | pillow-block test B3, first block |
| `SHAFT_END_PLAY`, `SPACER_BORE` | 0.4, 8.3 | step 6, assembly |
| `PB_OUTBOARD_FACE_Z` as measured, `MOTOR_SHAFT_LEN` and its datum, `MOTOR_PILOT_*`, `COUPLER_ENGAGE`, bore depths and clamping | 5.0, 23.5, 22.0 x 2.0, 10.0 | drive test D1, measure the parts |
| `BRACKET_PILOT_BORE`, alignment | 22.4 | drive test D2, first bracket |
| `DRIVE_CURRENT_A` | 1.2 | drive tests D3 (case < 60 °C), D4 (skips before a slat slips) |
| `DRIVE_PULL_EST_N` | 8.0 | drive test D5, full hopper |

### Physical calibration, in order

Nothing in the checks can tell you the model matches the belt. These can,
and each gates the next (drivetrain-spec §13 has the full procedure):

1. **Measure the belt** -- thickness at several points, and width.
2. **Ring coupon** -- OD across two opposite lands sets `PULLEY_OD_COMP`;
   then wrap real belt 180° round it: teeth riding up toward the ends means
   pitch is still wrong, needing force to seat means raise
   `PULLEY_GROOVE_COMP` by 0.05. Do not tune `FLANK_RADIUS`/`ROOT_RADIUS`.
3. **Saddle fit** -- one plain slat on real belt: snaps on, holds, lips just
   under the belt.
4. **Guide coupon** -- with that slat, the lug enters from a 1 mm offset
   without catching and the slat returns to centre.
5. **First shaft set.** Only now.
6. **Assembly and axial set-up** -- slide each shaft set until both spacers
   are snug, back it off by about half `SHAFT_END_PLAY`, tighten the grubs;
   **no shaft collars** (spec-pillow-blocks §1.1, §8); tension by sliding the tail plate until a finger
   press at mid-span deflects the belt about 5 mm.
7. **Creep test** -- paint-mark slats against belt teeth, 1000 revolutions,
   check drift. The fallback if slats walk is a keyed pin through the belt
   land; do not build it unless the test fails.

Then the hopper's, hopper-spec §11 H1-H7: feeler-gauge the liners' 1.5 over
the slats (`SKIRT_GAP`); watch lugs enter and leave the carry rail and the
slats land on it under load (rail section, `RAIL_T0`); run 1 L of parts for
10 minutes at 25, 40 and 55 and count what gets past the seal
(`SEAL_BRUSH_INTERFERENCE`, `SEAL_BRUSH_RAKE`), rechecking the creep marks;
measure parts per minute and jams through the metering brush (`METER_GAP`);
dump a 2 L bucket at each angle (`RIM_FRONT_H`); weigh the hopper empty and
with 2 L (`LOAD_BULK_DENSITY`, then rerun D2/D3); and run the thinnest parts
looking under the liner edges and at the seal. **Measure the strip brush
before printing either clamp** -- `BRUSH_BACKING_W/H` and `BRUSH_FREE_LEN`
are guesses at a door sweep.

Then the skirts', spec-skirts §11 S1-S6, after H2: see "Skirts" below.

### Inter-slat gap (2026-09-21)

`SLAT_WIDTH` is 17.0, not rev D's 16.0, so neighbouring slats are 1 mm
apart instead of 2. This is a design decision, not a spec resolution. The
specs' only rule is that the gap stay under 3.0 so a 1x1 plate cannot drop
through; that says nothing about thin elements (flag panels, blades, ~1.6
mm features) wedging edge-on, which a 2 mm slot accepts and a 1 mm slot
does not. The gap is not needed for the wrap: slats sit on the belt back,
outside the pitch line, so they fan apart round a pulley, and the gap is
never smaller than on the straight runs (checked round the whole loop).
Round the head pulley the slat tops open to 5.7 mm either way.

What the narrower gap costs is margin. Slats have no positive location
along the belt -- the tabs grip its edges, not its teeth -- so:

- **Place each slat against the teeth**, centred on every sixth land, never
  with a shim against its neighbour: gauging from slat widths lets a 0.1
  print error accumulate to 4.6 mm at the 46th slat.
- The value is provisional until calibration step 3. Caliper the first
  printed slat and set `SLAT_WIDTH` so the *printed* gap is about 1.0.
- If the creep test (step 7) shows slats walking, this margin is the first
  thing they use up.

## Drivetrain resolutions

Places where drivetrain-spec rev B could not be followed to the letter,
resolved from its own definitions per the convention in `CLAUDE.md`.

### Lug-in-groove control

§12.5 asserts that a shaft set cut with `groove_flank_clear=0,
groove_tip_clear=0` must clash with the slat's lug. It cannot: the lug is
straight and the groove is revolved, so -- for exactly the reason §6.1 gives
for why the lug does not bind -- every point of the lug off its mid-plane is
further from the axis than the matching groove section, where the V is
wider. A zero-clearance groove touches the lug along lines at x = 0 and
shares no volume with it (`test_zero_clearance_groove_only_touches_the_lug`
pins this). The control's purpose is to prove the lug is really in the
groove, so it is kept in two forms that can fail: a groove tighter than the
lug by the nominal clearances (`-GROOVE_FLANK_CLEAR`, `-GROOVE_TIP_CLEAR`)
must clash; and the slat slid sideways by 0.9 of its ±0.707 play must run
clear while 1.1 of it must strike a flank, on both sides.

### Take-up and the loop

§12.6 runs the whole-loop clearance sweep at three take-ups, "moving the
tail plate, pillow-block station and tail shaft set together". If the slats
stayed on the nominal loop, the guide wheel pushed 2.0 tailward would run
into the slats wrapped on the tail arc (0.5 rim gap), which is not what a
take-up does: the belt goes with the shaft. So `loop_at(s, takeup)` builds
the loop round `tail_shaft_t(takeup)`, `loop_length(takeup)` is 828 +
2·takeup, and the slats are spread evenly round that loop. Every assembly
group takes `takeup`; only the checks pass anything but 0. `belts` ignores
it and stays at nominal length.

### Groove compensation

§4.2 says `PULLEY_GROOVE_COMP` makes "the bottom and flank arcs grow, the
tip arc shrinks, about unchanged centres". Two details need care to keep
every junction tangent. Offsetting the groove *outward* means into the
material, so the bottom arc -- concentric with the pulley -- gets a
*smaller* radius (deeper groove) while the concave flank arc's grows; their
centre distance `BOTTOM_R + FLANK_R` is then unchanged, as the spec intends.
And a tip arc shrunk about an unchanged centre no longer reaches the OD,
which has its own, independent `PULLEY_OD_COMP`; so the tip arc keeps its
tangential offset `PULLEY_GROOVE_TIP_U` and its centre moves radially to
stay tangent to the compensated OD. At the default 0.0 none of this applies
and the groove is exactly the standard.

### End chamfer on the toothed faces

`END_CHAMFER` is cut by intersecting each pulley zone with a coned envelope,
so it breaks the outer edge of the lands ("outer edge", §5.3) and leaves
the groove walls vertical. A true edge chamfer of 0.3 round a 0.191 tip
radius is not constructible.

### `tooth_face()` closure

§4.3 describes the tooth face as "spanning one pitch, closed along the
land". Between the root fillets and ±pitch/2 the land and the closing line
coincide and enclose no area, so the face spans fillet to fillet;
`tooth_half()` still runs the full half pitch.

## Tilt

`docs/specs/spec-tilt.md`. The incline is an argument, `incline=INCLINE`,
threaded through `geometry.py`, `parts/frame.py` and every assembly group
the way `takeup` was. The machine frame does not move: the conveyor rotates
about the tail shaft axis, and `geometry.base_frame(incline)` is where
everything standing on the base is placed. At 40 degrees every part lands
exactly where it did.

To set an angle on the real machine: slacken the lock nut, turn the knob
until the bare rod between the knob's jam nut and the lock nut measures the
"exposed rod" figure from the table `checks.py` prints, then run the lock nut
back up against the prop body. About 52 turns cover the range.

The base is **open**; so are the fasteners of the hinge blocks and the pin
block. `TILT_WEIGHT_N` is an estimate until the frame is weighed. The
take-up mechanism, when designed, must stay off the rails' outer faces from
t = -60 to -20 and out of the space outboard of them (spec-tilt §3.2).

## Tilt resolutions

Places where spec-tilt could not be followed to the letter, resolved per
the convention in `CLAUDE.md`. The first three are real conflicts in the
spec and worth a look before anything is printed.

### Frame clevis

Pin A is 10.0 below the cross-member (`PROP_PIN_A_OFFSET = -87.0`), and
three things the spec puts there do not fit in 10.0:

- the prop's eye is 9.0 in radius, so a clevis base of any useful thickness
  between the cheeks would be hit by it;
- pin A's hex head (15.0 across corners) and washer (16.0) stand 7.5 and 8.0
  above the pin on the cheeks' outer faces, leaving 2.0 for a flange there;
- the fixing bolts at z = +/-15.0 would put their heads inside that same
  hardware: the cheeks end at +/-12.3 and the M8 x 45 runs out to -32.7.

Pin A's position sets the whole length table, so it stays. Instead the
flange is open tailward of `CLEVIS_WINDOW_X` (10.0), between the cheeks and
outboard of them to `CLEVIS_WINDOW_Z` (35.0); the cheeks hang from a wall on
the head side, where the prop never goes (it always leaves pin A tailward,
13..23 degrees below the run); and the two M5 move out to
**`CLEVIS_BOLT_Z` = 42.0**, still in the cross-member's bottom slot.
`params.py` asserts that the pin's bolt stays inside its window and the
fixing bolts outside it. "Material below pin A >= 7.0" is read as wall below
the pin hole, so the cheek nose is 11.1 in radius; being more than 10.0, it
is a half-disc so nothing stands proud of the contact face.

The prop load is compression, carried by the cheeks' top faces straight into
the cross-member; the M5 only locate the part.

### Prop foot

The foot pocket (16.0) is wider than the foot's eye (12.0), so the foot has
to widen between the eye and the pocket -- inside the pin block's cheeks, if
they were round about pin B like the frame clevis's. The prop only ever
pushes pin B down, so the pin block's cheeks are solid below the pin and
have just a `PIN_BLOCK_CHEEK_R` = 7.0 nose above it, and the foot widens to
`FOOT_DIA` = 24.0 at the pocket floor, 8.0 from pin B; `params.py` asserts
the order. The spec's round pocket also has no way in for the two nuts, so
the foot has a window `FOOT_WINDOW_W` = 14.0 wide in its -y side, which
faces up and tailward, toward the hand. It doubles as spanner access for
jamming them.

### Prop force at doubled weight

Spec-tilt §5.4 asserts the prop force under `PROP_FORCE_MAX` = 150 N and
that "a doubled weight must still pass", but its own table has 98 N at 25
degrees, which doubles to 196 N; at 150 the doubled case only passes above
about 33 degrees. Resolved (2026-09-26) by raising **`PROP_FORCE_MAX` to
250 N** rather than narrowing the tilt range or moving pin B: the limit is
a ceiling for the printed pivots, not a spec datum, and the worst doubled
case, 195.5 N at 25 degrees, is an M8 pin bearing on 12 mm of printed eye,
about 2 MPa. The nominal and doubled assertions both pass now, and both
are ordinary checks. If the frame weighs in well over the 34 N estimate,
revisit `TILT_MIN` before raising this again. The drive (spec-drive §7)
adds 3.6 N at the head shaft: 112.8 N at 25 degrees, and 225.7 N doubled,
still under 250. The hopper then used up the rest, and pin B moved to 140:
see "Pin B at 140".

### Pin B at 140

With the drive and the hopper (see "Hopper and drive together") the doubled
prop force at 25 degrees reached 249.96 N of the 250 N ceiling. The force is
the loads' moment about the hinge over the prop's arm about it, and at 25
degrees, with pin B at 125, the prop leaned 52 degrees from vertical and its
arm was 81. **`PROP_PIN_B_X` moved to 140** (2026-09-27): the prop stands
more upright, the arm grows to 97, and the doubled force with a full hopper
drops to 209.7 N (frame and drive alone: 189.3, was 225.7).

It costs stroke and budget. The prop now runs 152.6 .. 217.9 pin to pin, a
65.2 stroke (was 56.4), about 52 knob turns (was 45). The screw prop's stroke
can be at most its body less 22 (captured nut, engagement, bore stop), and
its shortest length must leave the foot and stack (57.6) under the body, so
the rod's window shrinks: with the old 90 body it would be 2.8 wide.
**`PROP_BODY_LEN` went 90 -> 92** to widen it, and **`ROD_LEN` 136 -> 128**,
mid-window of 125.9 .. 130.6: cut the rod to +/-2. The stack on the foot now
has 3.0 spare at 25 degrees (was 16.5). Past about 145 the two conditions
cannot both hold with this prop; a bigger move would need a new prop design.

What was checked, not assumed: the prop still leaves pin A on the clevis's
open side, now 17 .. 27 degrees below the run (was 13 .. 23), and T7 and T8
pass; the body clears the rail underside plane by 3.9 / 5.1 / 5.5 (was 3.4 /
4.4 / 4.9); the pin block, 15 further headward, still clears the base and
everything that tilts; the T7 control at 300 is unchanged. The setting-up
table and every pinned prop number in the checks moved with it.
`docs/design-baseline-v5.md` has the moved pin; the frozen v4 shows 125.

### Negative controls

- **T7, pin B at 300.** Confirmed, as the spec asks, but not by the mechanism
  it expects. The prop is then 111.3 long at 25 degrees and stands square to
  the frame at z = 0, where there is no rail for the body to hit; what hits
  is the 136 rod, which comes up through pin A into the cross-member
  (488 mm^3). That is a real frame-underside clash, so the control stands.
- **T5, cross-member at 190.** The overlap with the plate at 177 is 19.5,
  not the 10 the spec quotes: the plates are 45 along the run.

### Smaller readings

- **T8** is checked as the whole body against the whole clevis, and the foot
  against the whole pin block: no overlap, and nothing nearer than the
  `CLEVIS_SIDE_CLEAR` = 0.3 the eyes run at. That covers the base, the
  cheeks and the head wall at once. The body clears the cheek noses by 0.9.
- **T7's plane distance** is measured on the prop body with everything
  inside the clevis's extent along the run cut away: 3.9 / 5.1 / 5.5 at
  25 / 40 / 55 degrees.
- **Hinge bracket.** "Its lowest point is 8.0 above the base" is the boss.
  The plate's tail bottom corner is the rail's own corner and rides with it,
  about 6 above the base.
- **Length budget.** The spec wants it asserted in `params.py`, which
  imports only `math`, and `prop_length` in `geometry.py`. So
  `params.prop_length_at()` is a closed form of the same distance and
  `tests/test_tilt.py` holds the two together.
- **T1.** Two existing tests did change, because the spec changes what they
  list: the export test's file names, and the whole-loop sweep, now 3 x 3.
  The project has no BOM, so §7's hardware is `params.TILT_HARDWARE`,
  printed by `python3 assembly.py --report`.
- The prop body's nut pocket leaves 1.3 of wall at the hex's corners
  (`PROP_BODY_DIA` 18.0 against 15.4 across corners). It is the spec's
  figure and is in compression; thicken the body if it splits.

## Pillow blocks

`docs/specs/spec-pillow-blocks.md`. Each shaft runs in two 608ZZ pressed
into printed PETG pillow blocks bolted to the end plates, which are their
own standoffs: bearing centre at `SHAFT_HEIGHT_ABOVE_PLATE` = 48.0, now
fixed. The two blocks on a shaft are the same part turned end for end, lips
outboard, and a printed spacer tube between each bearing's inner ring and
the shaft set captures the shaft axially between the two lips. Three groups:
`pillow_blocks`, `bearings`, `spacers`; the tail members slide with the
take-up. The end plates gain four Ø5.0 holes each (cut list).

The press fit is six crush ribs on a 21.8 tip circle. `bearing_pocket()`
cuts the pocket, ribs and lip hole for both the block and the bearing
coupon, so **print the coupon first** (tests B1-B2 in spec §7): press a
bearing into each pocket, loosest first, and set `PB_RIB_TIP_DIA` to the
tightest pocket where it seats flat, stays in inverted and still spins
freely. `python3 assembly.py --report` lists the bought hardware.

## Pillow block resolutions

The spec was written against baseline v2, before the tilt.

- **Existing names reused**, as the spec asks: its `SHAFT_HEIGHT` is
  `SHAFT_HEIGHT_ABOVE_PLATE`; its `BEARING_Z` is derived as
  `BEARING_SPACING / 2`, not a second copy of 100 / 2; its bridge-plate
  "45.0" in the foot assertion is `PLATE_WIDTH`.
- **Incline.** The three groups take `incline` like every other group, and
  join T2's "everything that tilts clears the base" and the 3 x 3 whole-loop
  clash sweep; the blocks and spacers are fixed parts in that sweep, as §4
  asks. The distance criteria (14, 16) run at the three take-ups only: the
  blocks move with the conveyor, so the incline cannot change them.
- **Worst-case play (14).** The spec's 5.79 is the tower's inboard face to
  the slat ends with the slat slid across by its lug play,
  `geometry.slat_lateral_play()` = 0.707 (6.5 - 0.707). The model's slats
  are centred, so the sweep is run with the blocks shifted by -/+ the play,
  the same relative motion, and pinned at 5.79. Unshifted, the minimum is
  the foot top to the returning cleat tips, 6.05, and that is pinned too.
- **17 vs 18.** "Minimum distance >= 1.0 except the designed contacts" also
  has to except the spacer facing its own shaft set's end, which 18 puts at
  0.2 by design. That pair is held to 18's 0.2 +/- 0.01 instead.
- **21** is checked from each placed block's location, at two points on its
  local axis, against the shaft's; §5.1's probes are what tie the pocket to
  that local axis.
- **Pinned bands.** First build: block 16.65 cm^3 (spec estimate 16.4),
  press-fit clash 3.34 mm^3 at 21.8 (estimate about 3). Both are pinned at
  +/-3 % inside the spec's wider ranges.
- **Ribs.** Each rib's flanks run on past the pocket wall by the mouth
  chamfer so the rib joins the wall across its whole base rather than
  along a chord just inside it; the lead-in is a cone from the wall at the
  mouth to the tip circle at `PB_RIB_LEAD_IN`, so every rib ramps the same.
- **Not asserted.** §2.2 says head clearance is "asserted in geometry
  terms; see §5", but §5 has no such criterion. The M4 heads are under the
  end plates at z = +/-40.25, between the rails, where nothing else is
  modelled.

## Drive

`docs/specs/spec-drive.md`. The head shaft is driven directly, no
reduction, by a NEMA 17 stepper through a 5 x 8 flexible coupler. The motor
bolts to a printed **motor bracket** standing on the head bridge plate,
which shares the plate's two drive-side M5 (now M5 x 20). The head shaft is
cut **140** with its long end to the motor; the tail shaft stays 145. One
group, `drive` (motor bracket, coupler, motor), frame-fixed, so it ignores
the take-up.

`DRIVE_SIDE` (+1 = +z) is **open** (spec §10.1). `drive_group` and
`drivetrain_group` take `drive_side`, and the checks build both sides every
run, so choosing it later is a one-line change in `params.py`. The stepper
skips at about 13.3 N of belt pull, against an 8 N estimate, and that is
meant to protect the slats: tests D3-D5 set the driver current between
running a full hopper and slipping a slat (spec §9). `python3 assembly.py
--report` lists the bought parts.

Physical tests, in order: **D1** measure the pillow block, motor and
coupler; **D2** print the bracket, fit motor and coupler, turn by hand; **D3**
60 min at 30 rpm, case < 60 °C; **D4** the motor must skip before a held
cleat moves on the belt; **D5** find the current that runs a full hopper.

## Drive resolutions

The spec was written against baseline v3, before the printed pillow blocks.
The first three are worth a look before the bracket is printed.

### Stack from the printed pillow block

Spec §4 takes `PILLOW_BLOCK_HALF_W` = 14.0, a bought insert block, and §5
says a narrower block moves the stack, shaft length included, inboard. The
printed block's outboard (lip) face is 5.0 past the bearing centre, so
`PILLOW_BLOCK_HALF_W = PB_OUTBOARD_FACE_Z` and everything moves 9.0 inboard
(decided 2026-09-26):

| | spec | built |
|---|---|---|
| block outer face | 64.0 | 55.0 |
| coupler, 8-bore end | 66.0 | 57.0 |
| head shaft end (engagement) | 76.5 (10.5) | 67.5 (10.5) |
| motor shaft tip (gap) | 81.0 (4.5) | 72.0 (4.5) |
| face plate, inboard face | 99.5 | 90.5 |
| motor mounting face | 104.5 | 95.5 |
| motor back | 144.5, 7.5 past the frame | 135.5, inside the frame's 137 |

The head shaft comes out **140, 5 shorter than the tail's 145**, though §4
says it "gains length": the old symmetric 145 already reached 72.5, past
the coupler. The spec's formula gives 139.5 and whole-mm rounding gives
140, drive end 17.5 past the bearing. The alternative was to keep 145 and
leave a 7.0 gap to the block. The 140 keeps the spec's 2.0 gap and the
motor inside the frame.

### Bracket foot

§6 runs the foot from local z = -19.5 to +37.5, "the plate edge". With the
face plate 9.0 further inboard, both can't hold. The plate edge is the
reason given for the outboard end, so the foot now runs to the plate edge
(`BRACKET_FOOT_OUTBOARD` = 46.5), and the 19.5 inboard of the face plate is
kept. The bounding box is **45 x 72 x 66**, not §8.7's 57 across. Volume
30.5 cm³, about 39 g, pinned ±3 %.

### Print orientation

§6 fixes "face plate down, foot vertical, all holes vertical", but the foot
crosses under the face plate: it runs 19.5 inboard of the plate and 41.5
outboard of it to the M5. So there is material on both sides of the face
plate's outboard face, and that face can't sit on the bed. No orientation
has every hole vertical. The bracket prints **foot down**
(`PRINT_ROT_MOTOR_BRACKET`), with no support. The M5 slots print vertical,
and the pilot bore and M3 holes print horizontal. The pilot bore is tuned
on the first print anyway (D2). If it comes out too oval, the alternative is
to drop the inboard 19.5 of foot and print the face plate's inboard face
down. The foot would then be an L, and the motor seat would be the top
surface instead of the bed face.

### Smaller readings

- **Coupler.** Modelled with a blind bore from each end,
  `COUPLER_BORE_DEPTH` = `COUPLER_ENGAGE_MAX`, so both shafts sit in it
  without clashing, and the checks assert that they do. The helical cut,
  the clamping and the motor shaft's D-flat are not modelled. Check 11's
  "swept cylinder" is the coupler itself: it is a Ø20.0 cylinder and the
  bores are inside it. Its gap to the pillow block is exactly
  `COUPLER_BLOCK_GAP`.
- **Check 13.** The spec's "about 225" at 25 degrees is the motor, 223.4.
  The bracket's foot, lower on the plate, is nearer, at 198.4. Both are
  pinned, and T2 holds everything to 4.0.
- **Check 14.** The drive is a separate weight at the head shaft
  (`DRIVE_MASS_KG`, `DRIVE_CG_T`), as §7 asks: `drive_load()`, one entry of
  `prop_force()`'s default `machine_loads()` beside the frame's since the
  hopper made it a list, and `doubled()` doubles both: 225.7 N ≤ 250 with
  pin B at 125, 189.3 N since it moved to 140.
- **Check 15.** Rather than flipping `DRIVE_SIDE` and re-running, every
  drive check, the whole-loop sweep and T2 build both sides in one run.
  The head shaft is turned about x, not y, for -z, so its flat still faces
  the shaft set's grubs.
- **M5 x 20.** Foot 6 + plate 9 + T-nut 5 = 20, asserted in `params.py`.
  The spec says to check this against "the length now used there". The
  project records no length for the plates' M5, so that comparison is
  left for assembly.

## Hopper

`docs/specs/hopper-spec-v1.md`. A frame-mounted V-trough on the straight
carrying run, t = 12 .. 136: the rising slats and a back wall at 85° to the
run form the V, a seal brush in the back wall's notch wipes the slats at
t = 28, and a metering brush 14 above the slat tops at the front wall lets
out one cleat pocket of parts. Its lower walls are the first section of side
skirt (`SKIRT_INSET`, `SKIRT_GAP`, `SKIRT_HEIGHT` by name), and a carry rail
under the slats, cut with the guide wheel's own groove, takes the pile's
weight off the belts. Nothing of it is tailward of t = 10, so the tail arc,
tail plate and take-up are untouched, and none of it rides the tail plate.

`parts/hopper.py` builds everything in hopper coordinates (t, h, z), h above
the slat top face, and `geometry.hopper_offset(h)` turns an h into an
`at()` offset. `parts/carry_rail.py` has the rail (rail A since
spec-skirts, now ending at 177), `parts/station.py` the station at 88.5
that holds it up, `parts/brush.py` the two strip brushes as reference
solids. `assembly.py`'s `hopper` group places all 28 members; `hopper_parts()`
takes `meter_gap` and `rail_raise` for the checks, and
`hopper_cavity_placed()` is the capacity reference solid, never in a group.

Level fill (litres, at 0.50 kg/L of LEGO) and the prop force with the
hopper, from `checks.py`'s table:

| Incline | Level fill | Rim over base, front / back | Prop, empty / full / doubled |
|---|---|---|---|
| 25° | 2.04 L | 277 / 309 | 108 / 112 / 224 N |
| 40° | 2.40 L | 289 / 289 | 63 / 61 / 122 N |
| 55° | 1.87 L | 282 / 250 | 37 / 32 / 65 N |

The prop forces include the frame estimate, the drive and, since
spec-skirts, the skirts. The hopper weighs 0.956 kg (solid PETG, 0.60 g/cm³
plywood, two brushes and 60 g of hardware), close to the spec's 1.0 kg
ceiling. Doubled, the prop force at 25° was 209.7 N with the hopper, 40.3 N
under `PROP_FORCE_MAX`, with pin B moved to 140 for it (see "Hopper and
drive together" below and "Pin B at 140"); **with the skirts it is
224.2 N, 25.8 N under**.

`--report` lists the hopper's bought hardware (`params.HOPPER_HARDWARE`);
the brushes are the only bought parts modelled as solids. The physical tests
H1-H7 of hopper-spec §11 follow calibration step 7 ("Physical calibration,
in order").

## Hopper resolutions

Where hopper-spec v1 could not be followed to the letter, resolved per the
convention in `CLAUDE.md`. The first three change what gets made.

### Brush clamps

§4.4 and §4.5 make both clamps 96 long, "the channel plus 10 each side",
lapping the notch sideways on the wall's inner face. But the liners run
from wall to wall along the channel's edge: their lower walls are at
z = ±38 .. ±41 from h = 1.5 to 28 and the flare starts there, so a clamp
reaching z = ±48 on the wall's face overlaps them. Both clamps are
`HOPPER_CLAMP_LEN` = 75 instead, the brush's own length, 0.5 from each liner
like the brush, and lap the wall **above** the notch rather than beside it.

The seal brush's root line lies on the back wall's inner face and the
backing leans back from it at 15°, so the backing reaches 5.7 behind the
face. The seal clamp therefore fills the notch, from 8.0 in front of the
face to 3.0 behind the wall's outer face (`SEAL_CLAMP_FRONT`,
`SEAL_CLAMP_BACK`), with its lower face at `SEAL_ROOT_H - 1.0` as §4.4 says.
Because it reaches behind the face it mates with, it cannot print "mating
face down"; it prints on an end, section flat, which leaves the raked slot a
plain vertical channel with no support. Its grub screws come in from behind,
the metering clamp's from the hopper side.

The metering clamp is 12 thick, not the 10 first drafted, so the walls
either side of its 6.3 brush slot are 2.85. Its wall bolts are at h = 72,
9 above the notch, and its slots give the full 6..26 range; `params.py`
asserts the plate still laps the wall by 10 at the lowest setting.

### Front wall

§4.5 gives the front wall "the cavity section grown by the liner thickness",
the liner's outer boundary, like the back wall. Then the only place the
front wall meets a panel is h = 93.8 .. 110, and the liner's flange fills
that corner, so the front pair of corner cleats (§4.6) have nothing to
bolt to. The front wall spans the full ±108 from `SKIRT_GAP` up, with the
channel notch, and its cleats sit in the corner under the flare, at
`CORNER_CLEAT_FRONT_H` = 10 and 45, clear of the flare's underside. The back
wall is as the spec draws it; its cleats sit in the cavity above the liner's
flange (`CORNER_CLEAT_BACK_H`), because below the flare top the panels start
at t = 34, well headward of it.

### Corner cleats

§4.6 wants eight identical cleats and §4.1 two identical panels. An angle
with a bolt through each leg is chiral once the two bolts are at different
heights, which they must be or the bolts meet inside the angle; turning the
cleat 180° about its diagonal is a symmetry of the part, so it has one
placement per corner. On the -z side, then, the panel's bolt is the upper
one where on the +z side it is the lower. The cleats stay identical and the
**two panels differ in their four cleat holes**; `cut_list.py` gives both.

### Hopper and drive together

The hopper spec was written against baseline v3, before the drive, and
worked out that its doubled load at 25° left about 30 N under the ceiling:
"roughly 300 g of motor and mount before the ceiling is reached". The drive
spec, written against the same baseline, spent it: its 0.37 kg at the head
shaft adds 30.2 N doubled at 25°. Built together with pin B at 125, D2
passed by 0.04 N (249.96 N). Of the spec's options -- raise `TILT_MIN`,
move a pin, or lift `PROP_FORCE_MAX` with a stronger printed eye -- pin B
moved (2026-09-27, "Pin B at 140"): D2 is now 209.7 N, 40.3 N under the
ceiling. Moving pin A headward, the spec's suggestion, makes it worse: the
prop leans further from the frame's normal and its arm about the hinge
shrinks. Weighing the frame and a litre of parts (`TILT_WEIGHT_N`,
`LOAD_BULK_DENSITY`) is still the real test of that margin.

### Smaller readings

- **C7, the pillow blocks.** §5.2 gives a provisional envelope for the tail
  pillow blocks "until they are modelled". They are now, so C7 checks every
  hopper part against the real blocks, bearings and spacers, 3.0 clear at
  every take-up, and the envelope is gone.
- **Liner flange.** "A 12.0 flange against the panel inner face, up to
  h = 110" puts the flange's inner face 3.0 in from the panel, so the flare's
  inner face meets it at h = 95, not at `FLARE_TOP_H` = 98 (which is where it
  would meet the panel), and its top would be a 3.0 ledge facing up. The top
  inner edge is chamfered 45° (`LINER_FLANGE_CHAMFER` = 2.0).
- **Panel rear edge.** "Along the back wall's outer face down to t = 34"
  cannot happen: that face is at t = 13.6 .. 30.5 over its whole height. Read
  with "panel material stays headward of 34 below the flare top": the rear
  edge follows the wall's outer face down to `FLARE_TOP_H`, then steps
  headward to t = 34.
- **A2, gaps under the seal.** The limit of 1.05 is the nominal 1.0 gap plus
  0.05. The model spreads the slats evenly round the longer loop at a
  positive take-up (see "Take-up and the loop"), so at +2.0 every
  straight-run gap is 1.087; the check allows the straight-run gap at each
  take-up plus 0.05. The gap is measured between the slats' top bands, just
  below the edge chamfers, at four belt positions within a pitch, for pairs
  on the carrying side from the tail arc to the front wall's outer face (the
  head arc opens its gaps too, which is open question 9, not the hopper's).
- **Distances measured with the run along x.** The slats and every hopper
  part turn with the frame, so a distance between them cannot depend on the
  incline. C1, C2's clash, C5-C8 are measured at incline 0, where bounding
  boxes are tight and the sweeps quick; the no-clash whole-loop sweep with
  the hopper in it, C9 (base, hinge, prop) and C10 run at all nine cases,
  and a test confirms a slat-to-liner distance is the same at 0, 25 and 55.
- **C1's tight pair.** The sweep places slats on the centreline, where the
  nearest part is the carry rail at 0.5. The 0.29 cleat-to-liner figure is
  measured with every slat pushed its full ±0.71 lug play (`slat_lateral_play()`), with the rail
  left out then, since its groove is what stops them.
- **C4, the seal brush tip.** The bristles are a 3.0 tuft raked 15°, so the
  corner of the block is 0.39 below its tip line. "Lowest point 2.0 below the
  slat top" is checked on the tip line, the middle of the tuft's end.
- **C5, the cleat sweep.** A solid r = 35 cylinder about the tail axis
  contains the carry rail, which runs 0.5 under the slats from t = 30: no
  cleat goes there, since on the straight they ride above the slat top. The
  cylinder is applied to material above the slat-top plane; the rail and
  bridge are checked against the real slats by C1 and C10. The bristles are
  exempt from C5 as from C1: the seal brush meets the cleats coming off the
  tail wheel by design.
- **`level_fill(cavity)`** takes the cavity already placed at its incline:
  the machine frame never tilts, so horizontal is always machine +Y. The rim
  is the cavity's most upward-facing face, which a test checks at all three
  angles. The cavity leaves out the clamps and cleats and keeps the liner
  flange's 3.0 step.
- **`prop_force(incline, loads)`** takes (mass kg, t, offset) as §7.3 asks.
  `machine_loads()` is its default: `frame_load()`, which turns
  `TILT_WEIGHT_N` into the frame's entry, and `drive_load()`. They sum to
  spec-drive's `TILT_TOTAL_WEIGHT_N` at its combined centre of gravity, and
  a test holds the two forms equal. `doubled()` doubles a list. The hopper's hardware mass sits at the
  solids' centre of gravity, each brush at its backing.
- **Bolt holes and hardware.** Holes are modelled where the spec names them
  (feet, cleats, clamps, rail and bridge); the fasteners themselves are only
  listed. The foot's two M4 are at ±8.5 along the run to clear the M5
  counterbore. (The bridge's M3 up through its arm went with the bridge:
  spec-skirts fixes the rails through the arm's cheeks into side inserts.)

## Skirts

`docs/specs/spec-skirts.md`. The skirts continue the hopper's channel from
the front wall's outer face (t = 136) to t = 350: 6 ply strips, inner face
at `SKIRT_INSET` (38) over the slat ends, bottom edge `SKIRT_GAP` (1.5) over
the slat top, top at `SKIRT_HEIGHT` (28). The carry rail now runs the whole
carrying run as two rails, A (the hopper's, 30 .. 176.75) and B
(177.25 .. 330), meeting on the station at 177, so the lugs are in a groove
everywhere but on and next to the wheels and the slats land on the rail
instead of sagging away from the skirts. `CLEAT_LENGTH` went 74 -> 73, so
the cleat ends clear the skirts and the liners by 1.5, and **0.79** at
worst-case lug play (was 0.29).

The rails stand on **split support stations** on the three middle plates:
two posts outboard of the returning run (`parts/station.py`), and an arm
across them between the runs, its two cheeks holding the rail ends, with
M3s through one cheek into the rails' side inserts. At 177 and 265.5 a skirt
upright stands on each end of the arm, and one M3 x 60 clamps upright, arm
and post together. The skirt's outer face lands on the uprights at z = 44,
so its countersunk M4 heads lie flush in the channel face.

**Fitting** (spec-skirts §5.2): posts on the plates; belt on and tensioned;
each arm slid in sideways between the runs onto its posts (at 88.5 with the
hopper's +z side panel, its liner and feet off); rail A lowered between the
belts 3.0 headward of its place with the metering clamp off and its slats
unclipped, then slid back under the seal clamp, then rail B straight down;
slats back against the teeth; uprights; skirts. A one-piece bridge, which
the hopper first had, is a ring the belt loop passes through and could
only go in with the belt off.

`assembly.py`'s `skirts` group holds rail B, the two stations with their
uprights and both skirts (13 members); the `hopper` group keeps rail A and
the station at 88.5. Together they weigh 0.315 kg at t = 229, which is in
the prop force: **doubled at 25°, 224.2 N, 25.8 N under `PROP_FORCE_MAX`**.
`--report` lists the bought hardware (`params.SKIRTS_HARDWARE`), and the
cut list the two strips.

Physical tests, spec-skirts §11, after H2: S1 fitting with the belt on;
S2 lugs across the joint at 177, no click; S3 slats land on rail B at
mid-span; S4 feeler-gauge the skirt gap and the cleat-end gap; S5 a litre
of parts at three angles, nothing over, under or wedged; S6 weigh the parts.

## Skirt resolutions

Where spec-skirts could not be followed to the letter, or left a choice,
resolved per the convention in `CLAUDE.md`.

### The station at 88.5 (D5)

The spec retrofits the hopper's one-piece rail bridge to the split station,
recording that the user approved split stations without ruling on the
retrofit. It is built that way: one part family at all three stations, and
none that needs the belt off. To keep the bridge instead, restore
`rail_bridge()` at 88.5 and give rail A's 88.5 inserts back to its bottom.

### Derived values that need geometry

`UPRIGHT_CBORE_DEPTH` (§3.3) depends on the skirt top's offset, which is the
slat-top station plus `SKIRT_HEIGHT`; `params.py` cannot import `geometry`.
It is `parts/station.upright_cbore_depth()` (7.947), with `upright_height()`
and `post_height()` beside it, and a test holds the screw stack to
`UPRIGHT_SCREW_LEN`. S1 and S2 use `slat_lateral_play()` and are checks,
as the spec says.

### Smaller readings

- **Labels.** Rail A keeps the label `carry rail`, so the hopper's C1-C3
  read it unchanged; rail B is `carry rail B`. Station members are labelled
  by station: `station arm at 177`, `skirt upright -z at 265.5`.
- **K2 at the skirt ends.** The spec's 0.31 at t = 350 is a sharp top
  corner swept at radius 24.47. The real slat's edge chamfers keep it 0.53
  from the skirts, measured at twelve belt positions per pitch round the
  head (`head_arc_skirt_clearance()`).
- **K3.** With the slats pushed their play, a cleat end is 0.79 from a liner
  and from a skirt alike, the same channel face; the check accepts either.
- **T3, the arm's path**, is checked against every hopper part except the
  ones §5.2 takes off at 88.5 (the +z panel, liner and feet), not only the
  frame, plates and loop: stronger than the spec asks. The control leaves
  the panel on and must clash.
- **T4, rail A's path**, includes every hopper part except the metering
  clamp and brush; the slide back along the cheeks is checked as a box from
  the arm tops to the lands over the whole slid length.
- **Controls with numbers of their own:** R5 runs rail B to
  `RAIL_B_T1_CONTROL` (345), and T4 lowers the rails from
  `RAIL_FIT_TOP_OFFSET` (60, above every slat and cleat).
- **The joint relief** is a 45° chamfer of `RAIL_JOINT_RELIEF` on every top
  edge of the joint end face: the lands, the flanks and the groove floor.
- **M2, M3** are the hopper's D2 and D3: `prop_loads()` carries the skirts'
  mass now, so those checks are the skirts' too. The hopper's own mass rose
  to 0.956 kg with rail A to 177, still within D1.

## Missing parameters

None. Every dimension needed so far is present in `params.py`. The
drivetrain added a few the spec used but did not name:
`PULLEY_BORE_CHAMFER`, `PULLEY_GRUB_CLEARANCE_DIA`,
`PULLEY_INSERT_MIN_WALL`, `SHAFTSET_CONE_ANGLE`, `RING_COUPON_THICKNESS`
and `PULLEY_GROOVE_TEETH`. The tilt added the M8 and M5 catalogue sizes and
the dimensions spec-tilt gave only in its tables' value columns (the hinge
block's flange, both clevises' cheeks, the foot's pocket and wall, the base
reference slab, the check criteria), plus those its resolutions needed:
`CLEVIS_WINDOW_X/Z`, `CLEVIS_HEAD_X`, `CLEVIS_BOLT_Z`, `PROP_EYE_LEN`,
`FOOT_DIA`, `FOOT_WINDOW_W`, `PIN_BLOCK_CHEEK_R` and the knob's scallops.
The pillow blocks added `BC_POCKET_EDGE` (the spec's "15.0 from one long
edge"), `PB_SLAT_CLEAR_MIN` (its 5.0 criteria) and the bought-hardware
table `PILLOW_BLOCK_HARDWARE`. The drive added the values spec-drive gives
without names: the motor's rated current and step count, the running-torque
factor, the coupler's bores, torque and mass, the stack's derived z
positions (`COUPLER_Z`, `MOTOR_FACE_Z`, ...), the bracket's face-plate
height, M3 hole, fillet and tie slot, the M5 head and T-nut, the check
clearances, `GRAVITY`, the `TILT_TOTAL_*` combination and `DRIVE_HARDWARE`.
The hopper added the M4 and M3 sizes, the check limits of its §8, the
corner cleat's and the clamps' own dimensions (`CORNER_CLEAT_*`,
`SEAL_CLAMP_*`, `METER_CLAMP_*`, `METER_BOLT_*`), the bridge's pads and bolt
positions, and `BRUSH_BRISTLE_T` for the reference solid. The skirts added
`STATION_T`, `SKIRT_STATIONS`, the R5 and T4 controls' `RAIL_B_T1_CONTROL`
and `RAIL_FIT_TOP_OFFSET`, `PRINT_ROT_STATION`/`_UPRIGHT` and
`SKIRTS_HARDWARE`.

## Provisional parameters

`SHAFT_HEIGHT_ABOVE_PLATE` (48mm) is no longer provisional: the printed
pillow block is its own standoff and is designed to it (spec-pillow-blocks
§2.2). The drivetrain's and the pillow blocks' provisional values are
tabulated under "Parameters awaiting physical calibration".

The belt is the HTD-3M, 15mm wide, 828mm pitch length, 276-tooth loop chosen
in rev D. Its thickness (2.4) and pitch line differential (0.381) are
catalogue figures for the profile, not measurements of this belt -- caliper
it. See "Belt, slat pitch and width, rev D" below for what the belt drives.

`SADDLE_INTERFERENCE`, `SADDLE_TAB_DEPTH` and `CLEAT_HEIGHT` are also
unvalidated against real hardware (rev B §8) -- the acceptance checks
confirm internal consistency, not a physical fit. The drivetrain spec cut
the tab depth from 6.0 to 3.6 (belt 2.4 + 0.2 gap + lip 1.0) so the lips
sit just under the 2.4mm belt instead of 2.6 below it, and added the guide
lug; **any slat printed before that is for saddle test-fitting only, and
none should be batch-printed until calibration step 4 passes.**

## Belt, slat pitch and width, rev D

Rev C's 390mm HTD-5M loop forced a 135mm centre distance that could not
carry five 45mm bridge plates (phase 4 made this physical). Rev D changes
the belt to an HTD-3M x 15mm x 828mm loop, 276 teeth, and follows every
parameter that depends on it. `docs/specs/phase1-cad-spec-revD.md` §2 has the full
changelog and reasoning; the short version:

- `PULLEY_TEETH = 40`, because 40 x 3mm is the same 120mm circumference as
  24 x 5mm, so the pitch diameter and every clearance built on it are
  unchanged. `CENTRE_DIST` becomes 354mm.
- `SLAT_PITCH = 18` (6 teeth) is the smallest whole-tooth pitch dividing
  828mm that leaves room for the 10mm cleat root; `SLAT_WIDTH = 16` kept
  rev C's 2mm gap (since narrowed, see "Inter-slat gap"); 46 slats.
- `CLEAT_EVERY = 2`: 46 isn't divisible by 3, and "every third" would put
  two cleats 18mm apart at the belt seam. A new `params.py` assertion,
  `SLAT_COUNT % CLEAT_EVERY == 0`, guards that.
- `BELT_SPACING = 54` (was 60): a 15mm belt's outer tab would otherwise end
  0.1mm from the slat end against the 2mm rule. Moving the belts inward was
  chosen over lengthening the slat so the slat, cleat and phase 2 skirt
  numbers stay put.
- `SADDLE_TAB_LENGTH = 7` (was 12): rev B's "grips at most 2.5 teeth" is
  7.5mm at a 3mm pitch.
- Phase 3 profile radii renumbered so `TOOTH_HEIGHT` is the published 1.17mm
  for HTD-3M; still approximate, and since the drivetrain spec they shape
  the belt model only.

The bounding-box, volume, probe-point and cleated-count numbers in
`checks.py`/`tests/` were recomputed from the built geometry (rev D §5),
as rev C did, not scaled.

## Centre distance

Closed by rev D. `CENTRE_DIST` derives from `BELT_LOOP_LENGTH` (rev B
changelog #10) and is 354.0mm with the 828mm belt, which fits the 552mm
frame with 138mm to spare past the head shaft and spaces the five bridge
plates 88.5mm apart. Rev C §8's open layout question no longer applies.

## Saddle tab z-positions

`parts/slat.py`'s `_saddle_pair()` derives each tab's position directly from
`BELT_WIDTH` and `SADDLE_INTERFERENCE`: the facing surfaces of a tab pair
sit `BELT_WIDTH - SADDLE_INTERFERENCE` apart, centred on the belt centre.
This is what rev B §3 specifies directly (its note on the saddle table:
"tab positions now derive from `BELT_WIDTH` and `SADDLE_INTERFERENCE`
alone"), and rev B deletes the old `SADDLE_TAB_CLEARANCE` parameter this
implementation never actually used, removing a redundant value that could
contradict the others.

## Chamfer edge selection (S8.1)

"The four edges parallel to z on the top face" is only geometrically
possible to read as two edges (a face has two edges parallel to any given
in-plane axis) plus the caveat that follows it ("do not chamfer the y=0
face") reads as excluding the bottom pair from a naively-selected set of
four. Implemented as: the top face's two z-parallel edges, plus the four
vertical (y-parallel) edges of the two end faces. None of these touch the
y = 0 belt-contact face.
