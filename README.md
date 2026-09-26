# lego-mechanical-hopper

Parametric build123d model of the LEGO-sorter feed elevator, structured as
parts that assemble. Phase 1 built the conveyor slat (plain and cleated);
phase 4 added the assembly framework with the aluminium frame and the
plywood bridge plates as its first two groups; the drivetrain spec added
the tooth profile, the printed shaft sets, shafts, belts and the slats
running round both ends; the tilt spec made the incline adjustable by hand
over 25..55 degrees, with a hinge, a cross-member and a screw prop. See the
`phase*-cad-spec*.md` files, `drivetrain-spec.md` and `spec-tilt.md` in
`docs/specs/`: each phase depends on the earlier
ones, and each rev diffs against the previous one rather than replacing it.

For a single self-contained summary of what is built and decided, written
for readers outside the project and as the input to new specifications, see
`docs/design-baseline-v2.md`. Its numbers are taken from `params.py`:
regenerate them when parameters change. `docs/design-baseline-v1.md` is the
frozen snapshot at commit `98f4fb1` that the drivetrain specification was
written against; it carries the uncorrected belt-back radius and is kept
only as that spec's reference.

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
`parts/coupons.py`, `parts/frame.py` and `parts/bridge_plate.py` work the
same way. Without a running viewer
server, `ocp_vscode` prints a connection warning but the geometry still
builds correctly (exit code 0) -- useful for a headless sanity check.

## Viewing the assembly

```bash
python3 assembly.py                 # every group
python3 assembly.py frame           # just the frame
python3 assembly.py frame plates    # both, in position
python3 assembly.py plates --detail
python3 assembly.py frame plates drivetrain belts slats   # the machine
python3 assembly.py "drivetrain:tail shaft" "drivetrain:tail shaft set"   # single members
python3 assembly.py drivetrain belts "slats:slat ?" --detail               # real slats 0-9 only
python3 assembly.py --incline=55    # the whole machine tilted; INCLINE (40) if not given
python3 assembly.py --report        # no viewer: each group's members, and the tilt's bought hardware
```

A name is a group, or `group:pattern` for just the members whose label
matches the glob pattern; a pattern matching nothing lists the group's
member labels. So the drivetrain can be built up one part per run, and
`slats` on its own is the shortcut for all 46.

Each group is shown in its fixed colour from `assembly.COLOURS` and named
in the viewer tree, with its members labelled (`plate 0 (bearing)`, `rail
+z`, `head shaft set`, `slat 12`, ...). `--detail` is accepted by every
group. `slats` draws plain bounding boxes without it and real slats with
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
drivetrain-spec §4.4 and §12 and spec-tilt §8.2, and exits non-zero if any
fail. It takes about two minutes, most of it the whole-loop clearance sweep,
which runs at three take-ups and three inclines. It ends with the
**setting-up table** (spec-tilt §8.3): prop length and exposed rod against
incline, which is how the angle gets set by hand -- see "Tilt" below. This is the same set of assertions as the
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

The frame and shafts are owned or bought hardware, the belt is bought, and
the bridge plates are cut from plywood, so none is exported as STL. `python3 cut_list.py` writes `out/cut_list.txt`
with the plate rectangle and hole positions, the tilt's cross-member (2020,
234) and its prop rod (M8, 136) instead.

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
| `SHAFT_HEIGHT_ABOVE_PLATE` | 48.0 | measuring the pillow blocks (rev B §8) |

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
6. **Assembly and axial set-up** -- both shaft sets at the same z, by caliper
   from the pillow blocks; tension by sliding the tail plate until a finger
   press at mid-span deflects the belt about 5 mm.
7. **Creep test** -- paint-mark slats against belt teeth, 1000 revolutions,
   check drift. The fallback if slats walk is a keyed pin through the belt
   land; do not build it unless the test fails.

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
back up against the prop body. About 45 turns cover the range.

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
degrees, which doubles to 196 N. Doubled, the limit is only met above about
33 degrees. Both numbers are the spec's, so neither was changed: the nominal
assertion passes, and the doubled one is an `XFAIL` in `checks.py` and a
`strict=True` xfail in `tests/test_tilt.py`. It wants a decision -- raise
`PROP_FORCE_MAX` to 200 or more if the printed pivots are good for it, or
raise `TILT_MIN`, or move pin B -- and then the entry comes out.

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
  inside the clevis's extent along the run cut away: 3.4 / 4.4 / 4.9 at
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

## Provisional parameters

`SHAFT_HEIGHT_ABOVE_PLATE` (48mm) is a best guess, not a measurement, per
rev B §8 -- it depends on the pillow blocks actually bought; measure before
modelling the standoff that sets this height. The drivetrain's provisional
values are tabulated under "Parameters awaiting physical calibration".

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
