# lego-mechanical-hopper

Parametric build123d CAD model for a LEGO-sorting machine's feed elevator
(a cleated incline conveyor belt). The project is structured as parts that
assemble: `params` -> `geometry`/`profile` -> `parts/` -> `assembly.py`,
each layer reading only downward (phase 4 §2). Phase 1 built the conveyor
slat, phase 4 the assembly framework with the aluminium frame and bridge
plates as its first two groups, and the drivetrain spec the tooth profile,
shaft sets, shafts, belts and the slats placed round the whole loop. Phase
2 (skirts, posts) is specified but not yet built beyond its parameters.

## Spec authority

- Specs live in `docs/specs/`, numbered by phase, each depending on the earlier ones.
  Phase 1: `phase1-cad-spec.md` (rev A) -> `-revB.md` -> `-revC.md` ->
  `-revD.md` (current for the slat and the belt; each rev is a diff against
  the previous, not a standalone rewrite, so all four are still needed.
  Rev D also renumbers the belt-dependent tables of phases 2-4). Phase 2:
  `phase2-cad-spec.md`. Phase 3: `phase3-cad-spec.md` -> `-revB.md`.
  Phase 4: `phase4-cad-spec.md`. Drivetrain: `drivetrain-spec.md` (rev B,
  written against `docs/design-baseline-v1.md`; it supersedes phase 3's
  pulley, groove clearance and coupon, corrects phase 1's
  `belt_back_radius()`, and changes the slat). Where any two conflict, the
  latest rev of the latest phase wins, and the drivetrain spec is latest.
- If a new rev or phase spec file appears, check its own header for what it
  supersedes and diffs against, and treat it the same way.

## Current implementation status

- **Phase 1 (slat): done, then changed by the drivetrain spec.** `params.py`
  matches rev D §3 (HTD-3M x 15mm x 828mm belt, 40-tooth pulley, 18mm slat
  pitch, 46 slats) except `SLAT_WIDTH`, widened 16 -> 17 for a 1mm
  inter-slat gap (README "Inter-slat gap"); every rev B §5 assertion is checked by both `checks.py`
  and `tests/`, with drivetrain-spec §6.3's numbers where the guide lug and
  the 3.6mm tab depth moved them.
- **Phase 2 (skirts, posts): not built.** Only the bridge-plate subset of
  its parameters and `plate_top_offset()`/`plate_t()` exist, because phase
  4 needs them. Skirt and post parameters are still rev B's provisional
  block.
- **Phase 3 (profile, belt, pulley): superseded by the drivetrain spec.**
  There is no `parts/pulley.py` and never will be; the pulleys are part of
  the shaft set.
- **Drivetrain: done in CAD, nothing printed.** `profile.py` (belt tooth,
  and the standard 40-tooth HTD-3M groove rebuilt from catalogue values and
  tested against the manufacturer's junction points), `parts/shaft_set.py`,
  `shaft.py`, `belt.py`, `coupons.py`, the slat's guide lug, `loop_at()`
  and the take-up in `geometry.py`, and the `drivetrain`, `belts` and
  `slats` groups. Five deviations are recorded in `README.md` ("Drivetrain
  resolutions"): the lug-in-groove negative control, slats following the
  take-up, groove compensation geometry, the end chamfer, and
  `tooth_face()`'s closure. `reference/htd3m_40t_40015040.stp` is still
  missing from the repo (see `reference/README.md`).
- **Phase 4 (assembly framework): done**, with three live spec deviations
  recorded in `README.md` ("Phase 4 resolutions"): `at()` offsets
  are measured from the shaft axis; `PLATE_LENGTH` is `FRAME_WIDTH`, not
  `FRAME_INNER_WIDTH`; the frame bounding-box check is done in the frame's
  local frame. The fourth (plates overlapping at rev C's 135mm centre
  distance) was resolved by rev D's belt.
- Open: `SHAFT_HEIGHT_ABOVE_PLATE` (measurement, rev B §8), and the whole
  of drivetrain-spec §13 -- belt measurement, ring coupon, saddle fit,
  guide coupon, first shaft set, set-up, creep test, in that order. README
  "Parameters awaiting physical calibration" lists what each step settles.

If a later phase or revision changes the picture, this list is the thing to
update once the migration is done.

## Repo layout

```
docs/design-baseline-v2.md  self-contained as-built summary for external spec writers (current);
                          derived from params.py -- regenerate its numbers when params change
docs/design-baseline-v1.md  the same at commit 98f4fb1, the input to the drivetrain spec; frozen, superseded by v2
docs/specs/               the phase specs
  phase1-cad-spec.md        rev A spec (superseded, kept as base document)
  phase1-cad-spec-revB.md   rev B spec (superseded, diff against rev A)
  phase1-cad-spec-revC.md   rev C spec (superseded, diff against rev B)
  phase1-cad-spec-revD.md   rev D spec (current for phase 1 and the belt, diff against rev C)
  phase2-cad-spec.md        skirts and posts (not yet built)
  phase3-cad-spec.md        tooth profile, belt, pulley (rev A)
  phase3-cad-spec-revB.md   phase 3 rev B (current for phase 3, diff against rev A)
  phase4-cad-spec.md        assembly framework, frame, bridge plates (current)
  drivetrain-spec.md        profile, shaft sets, shafts, belt, guide lug, loop placement (rev B, current)
reference/                third-party source models, unmodified, never written or imported (CC BY-ND)
README.md                 setup, usage, and the recorded spec resolutions
params.py                 single source of truth for every dimension
geometry.py               pure functions: run direction, shaft axes, at(), loop_at(), radial stations, take-up, plate/frame datums
profile.py                2D only: belt tooth (belt model) and the standard pulley groove; pulley_section() is the one source of teeth
parts/slat.py             the slat part (plain + cleated) with saddle tabs and guide lug, pulley_envelope()
parts/shaft_set.py        printed: both pulleys + V-grooved guide wheel of one shaft; shaft_set_with() for the groove control
parts/shaft.py            bought 8mm shaft with its filed flat (reference solid)
parts/belt.py             bought belt: belt_segment/belt_wrapped for mesh checks, belt_band for the assembly, belt_loop behind --detail
parts/coupons.py          printed: ring_coupon and guide_coupon, made by the shaft set's own functions
parts/bridge_plate.py     plywood bridge plate (reference solid, cut list not STL)
parts/frame.py            2020 aluminium frame (owned hardware, reference solid)
assembly.py               GROUPS dict of positioned Compounds; `python assembly.py [group ...] [--detail]`
cut_list.py               writes out/cut_list.txt for the plywood parts
utils.py                  bbox/volume/contains/clash helpers used by checks & tests
checks.py                 human-facing runner of every acceptance assertion from the specs
tests/                    the same assertions as pytest tests
export.py                 writes out/*.stl: both slats, shaft_set, ring_coupon, guide_coupon
```

## Conventions

- **No hard-coded dimensions outside `params.py`.** Every numeric
  dimension used anywhere in the code must be imported from `params.py`.
  If a part or check needs a new value, add it to `params.py` rather than
  inlining it.
- **Four layers, reading downward only** (phase 4 §2.1): `params` imports
  only `math`; `geometry.py` builds no solids and imports only `params`;
  `profile.py` sits beside it, imports only `params` and stops at 2D edges
  and faces;
  `parts/*.py` return a solid in its own local frame and never compute a
  machine position (they may import a scalar from `geometry` that is one of
  their own dimensions); `assembly.py` is the only module that combines
  parts with positions. `parts/frame.py`'s `frame()` is the one documented
  exception: it returns a positioned Compound because there is exactly one
  frame.
- **Local origin at the mating surface** (phase 4 §2.3): a part's origin is
  the face it mates with, so placement is one `at()` call with no
  corrective offset. Local +x along the run, +y out along the run normal,
  +z across the machine. Document the origin in every part's docstring.
- **`at(t, offset, lateral)` measures `offset` from the shaft axis**, so
  `at(t, 0)` is on the shaft and a slat on the carrying run goes at
  `at(t, belt_back_radius())`. Every `*_offset()` datum shares that origin.
  Anything riding the belt goes at `loop_at(s)`, s along the pitch line.
- **Radial clearances use the `geometry` stations** (`belt_back_radius()`,
  `tab_tip_radius()`, `guide_rim_radius()`, ...), never literals.
- **One function makes teeth**: `profile.pulley_section()`. Don't cut pulley
  grooves from `tooth_face()` or the STEP file, and never change a
  `PULLEY_GROOVE_*` catalogue value to make a check or a print fit -- tune
  `FLANK_RADIUS`/`ROOT_RADIUS` (belt model) or the `_COMP` values (printer).
- **Adding a part to the machine** means one `<name>_group(detail, takeup)`
  function in `assembly.py` returning a positioned Compound, one `GROUPS`
  entry and one `COLOURS` entry. Nothing else should need touching.
- Acceptance criteria in the specs (rev B §5 substituted per rev C §5; phase 4 §8; drivetrain §4.4, §6.3, §12) are the contract:
  they're expressed both as `checks.py` (human-facing pass/fail output)
  and as the `tests/` pytest suite. Keep both in sync with whichever spec
  revision is current.
- Where the spec's prose is ambiguous or internally inconsistent, resolve
  it from the spec's own named-parameter definitions rather than its
  worked examples, and record the resolution and reasoning in
  `README.md` (see its "Saddle tab z-positions" and "Chamfer edge
  selection" sections for the existing pattern).
- Physical test fit is still the real gate: rev B §8 is explicit that
  `SADDLE_INTERFERENCE` and `CLEAT_HEIGHT` are unvalidated guesses until a
  printed plain + cleated slat pair is run on actual belt stock. Don't
  treat passing checks as physical validation.

## Workflow

```bash
source .venv/bin/activate   # or create one per README.md
python3 checks.py              # pass/fail per acceptance check, ~35s (the whole-loop clash sweep)
python -m pytest                # same assertions, pytest form, ~70s
python3 export.py              # writes out/*.stl (gitignored)
python3 cut_list.py            # writes out/cut_list.txt for the plywood parts
python3 parts/slat.py          # opens one part in OCP CAD Viewer if running
python3 assembly.py frame plates   # the assembly, one colour per group; no args = every group
python3 assembly.py frame plates drivetrain belts slats --detail   # real slats and toothed belts
```

`checks.py` reports `XFAIL` for checks listed in its `_EXPECTED_FAILURES`
table and fails the run with `XPASS` if one of them starts passing; the
pytest twin is a `strict=True` xfail. Remove both when the cause is fixed.

## Out of scope so far

Per rev B §6, phase 4 §1 and drivetrain-spec §1, §15: pillow blocks and their
standoffs (unmodelled until the real ones are measured), the tail take-up
jacking screw, side skirts and posts, motor mount, coupler, hopper, brush
mounts. Their parameters may exist in `params.py` for later phases to
reference, but don't build the parts themselves until their phase. The
skirts no longer guide anything; when specified, their gap can open to 2.0.
Don't build the creep-test fallback (keyed pin through the belt land)
unless the physical test fails.
