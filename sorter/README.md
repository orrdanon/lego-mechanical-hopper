# sorter

Parametric build123d model of the LEGO-sorter feed elevator, structured as
parts that assemble. Phase 1 built the conveyor slat (plain and cleated);
phase 4 added the assembly framework with the aluminium frame and the
plywood bridge plates as its first two groups. See the `phase*-cad-spec*.md`
files at the repo root: each phase depends on the earlier ones, and each
rev diffs against the previous one rather than replacing it.

## Setup

```bash
python3 -m venv .venv        # or reuse the repo's existing .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run everything below from this `sorter/` directory.

## Viewing a part

With the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer)
VS Code extension running (`ocp_vscode` connects to it over a websocket),
run any part module directly:

```bash
python3 parts/slat.py
```

This opens the viewer showing a plain slat. `parts/frame.py` and
`parts/bridge_plate.py` work the same way. Without a running viewer
server, `ocp_vscode` prints a connection warning but the geometry still
builds correctly (exit code 0) -- useful for a headless sanity check.

## Viewing the assembly

```bash
python3 assembly.py                 # every group
python3 assembly.py frame           # just the frame
python3 assembly.py frame plates    # both, in position
python3 assembly.py plates --detail
```

Each group is shown in its fixed colour from `assembly.COLOURS` and named
in the viewer tree, with its members labelled (`plate 0 (bearing)`, `rail
+z`, ...). `--detail` is accepted by every group; in this phase both
ignore it. Phase 5's slats group will honour it by drawing plain boxes by
default, because forty-odd real slats make the viewer crawl.

## Running checks

```bash
python3 checks.py
```

Prints one line per acceptance check from rev B §5 and phase 4 §8 and
exits non-zero if any fail. This is the same set of assertions as the
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

Writes `out/slat_plain.stl` and `out/slat_cleated.stl` (print-rotated per
`params.PRINT_ROT_PLAIN` / `PRINT_ROT_CLEATED`). `out/` is gitignored.

The frame is owned hardware and the bridge plates are cut from plywood, so
neither is exported as STL. `python3 cut_list.py` writes `out/cut_list.txt`
with the plate rectangle and hole positions instead.

## The assembly framework (phase 4)

### Four layers, reading downward only

| Layer | Answers | Returns | May import |
|---|---|---|---|
| `params.py` | what did we choose | floats | `math` |
| `geometry.py` | where, how far | floats, `Location` | `params` |
| `parts/*.py` | what shape | `Part` | `params`, `geometry` |
| `assembly.py` | what goes where | `Compound` | all three |

`geometry` never builds a solid. A part returns a solid in its own local
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

Local axes for anything placed by `at()`: +x along the run, +y out along
the run normal, +z across the machine. Each part's docstring states its
origin; when a future part sits 9 mm out of place, that is the first thing
to check.

### How to add a group

1. Write `<name>_group(detail: bool = False) -> Compound` in `assembly.py`,
   building parts and placing them with `at()` and the `geometry` datums.
   No new positions invented inside the part modules.
2. Add `"<name>": <name>_group` to `GROUPS` and a fixed colour to `COLOURS`.
3. Add its acceptance checks to `checks.py` and `tests/`.

If adding a group needs more than that, the framework is wrong and should
be fixed rather than worked around (phase 4 §10).

## Phase 4 resolutions

Four places where the phase 4 spec conflicts with the repo or with itself,
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

### Plate overlap and `CENTRE_DIST`

Phases 2-4 were written against the old 390 mm centre distance (phase 2's
`POST_SPACING = CENTRE_DIST/4 = 97.5`; phase 4's 552 mm frame). With the
real belt, `CENTRE_DIST = 135`, so five 45 mm plates at a 33.75 mm pitch
overlap their neighbours and phase 4 §8.5 cannot pass. This is the open
layout question of rev C §8 becoming physical, not a modelling error, so
the numbers were left as specified: the §8.5 check is a `strict=True`
xfail in `tests/test_bridge_plate.py` and an `_EXPECTED_FAILURES` entry in
`checks.py`, both citing the reason. Settle `CENTRE_DIST` (longer belt,
idler, or narrower plates / fewer stations) and the check goes green on its
own, at which point both entries must be removed.

## Missing parameters

None. Every dimension needed by phase 1 is present in `params.py`.

## Provisional parameters

One value in `params.py` is a best guess, not a measurement, per rev B §8:

- `SHAFT_HEIGHT_ABOVE_PLATE` (48mm) -- depends on the pillow blocks actually
  bought; measure before modelling the standoff that sets this height.

`BELT_LOOP_LENGTH` is no longer provisional (rev C): it's the real belt
bought, a 5mm HTD-pitch, 9mm wide, 390mm pitch length, 78-tooth timing belt.
See "Slat pitch and width, rev C" and "Open: centre distance" below for what
that value changes and what it leaves unresolved.

`SADDLE_INTERFERENCE` and `CLEAT_HEIGHT` are also unvalidated against real
hardware (rev B §8) -- the acceptance checks confirm internal consistency,
not a physical fit. That fit is still the gate before phase 2: print one
plain slat and one cleated, clip them to a scrap of 9mm HTD-5M, and run them
round a pulley before modelling anything further.

## Slat pitch and width, rev C

`BELT_LOOP_LENGTH = 390` (78 teeth) isn't divisible by 4, so rev B's
`SLAT_PITCH = 20` ("4 belt teeth") no longer divides it evenly -- rev B
§5.1's `BELT_LOOP_LENGTH % SLAT_PITCH == 0` would fail. Rev C moves to 3
teeth per slat, `SLAT_PITCH = 15`, which divides 390mm evenly (26 slats).

`SLAT_WIDTH` then has to shrink to stay under the new, smaller pitch.
Rev C keeps the same 2mm inter-slat gap rev B used (`20 - 18 = 2`), giving
`SLAT_WIDTH = 15 - 2 = 13`. This is a choice, not something forced by the
spec's other assertions -- any value in `(12, 15)` would satisfy
`SLAT_WIDTH < SLAT_PITCH` and `SLAT_PITCH - SLAT_WIDTH <= 3.0` -- but
preserving the existing gap rather than picking a new one keeps the
slat-to-slat spacing behaviour unchanged from rev B.

The bounding-box, volume, and cleated-count acceptance numbers in
`checks.py`/`tests/` all follow from this and were recomputed from the
actual built geometry (see `phase1-cad-spec-revC.md` §5), not scaled by
hand -- the saddle tabs and cleat don't shrink with `SLAT_WIDTH`, so volume
in particular doesn't scale linearly with it.

## Open: centre distance

`CENTRE_DIST` derives from `BELT_LOOP_LENGTH` (rev B changelog #10). With
the real 390mm belt, `CENTRE_DIST = 135.0mm` -- under half of rev A's old
fixed 390mm. This is arithmetically consistent and passes every check, but
**it has not been confirmed against the hopper/discharge layout**. Unlike
`SHAFT_HEIGHT_ABOVE_PLATE`, this isn't a missing measurement waiting on a
part purchase; it's an open layout decision (a longer belt, an idler
pulley, or repositioning within the frame could each resolve it
differently). Don't treat `CENTRE_DIST` as final, and don't build anything
downstream that assumes a 135mm span is enough, before that decision is
made.

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
