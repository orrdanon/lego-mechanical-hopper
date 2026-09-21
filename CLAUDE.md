# lego-mechanical-hopper

Parametric build123d CAD model for a LEGO-sorting machine's feed elevator
(a cleated incline conveyor belt). The project is structured as parts that
assemble: `params` -> `geometry` -> `parts/` -> `assembly.py`, each layer
reading only downward (phase 4 §2). Phase 1 built the conveyor slat, phase
4 the assembly framework with the aluminium frame and bridge plates as its
first two groups. Phases 2 (skirts, posts) and 3 (tooth profile, belt,
pulley) are specified but not yet built beyond their parameters.

## Spec authority

- Specs are numbered by phase, each depending on the earlier ones.
  Phase 1: `phase1-cad-spec.md` (rev A) -> `-revB.md` -> `-revC.md` ->
  `-revD.md` (current for the slat and the belt; each rev is a diff against
  the previous, not a standalone rewrite, so all four are still needed.
  Rev D also renumbers the belt-dependent tables of phases 2-4). Phase 2:
  `phase2-cad-spec.md`. Phase 3: `phase3-cad-spec.md` -> `-revB.md`.
  Phase 4: `phase4-cad-spec.md`. Where any two conflict, the latest rev of
  the latest phase wins.
- If a new rev or phase spec file appears, check its own header for what it
  supersedes and diffs against, and treat it the same way.

## Current implementation status

- **Phase 1 (slat): done.** `params.py` matches rev D §3 (HTD-3M x 15mm x
  828mm belt, 40-tooth pulley, 18mm slat pitch, 46 slats); every rev B §5
  assertion is checked with rev D's numbers by both `checks.py` and
  `tests/`, and `export.py` writes the two slat STLs.
- **Phase 2 (skirts, posts): not built.** Only the bridge-plate subset of
  its parameters and `plate_top_offset()`/`plate_t()` exist, because phase
  4 needs them. Skirt and post parameters are still rev B's provisional
  block.
- **Phase 3 (profile, belt, pulley): parameters only**, renumbered for
  HTD-3M by rev D. No `profile.py`, `parts/pulley.py` or `parts/belt.py`
  yet.
- **Phase 4 (assembly framework): done**, with three live spec deviations
  recorded in `sorter/README.md` ("Phase 4 resolutions"): `at()` offsets
  are measured from the shaft axis; `PLATE_LENGTH` is `FRAME_WIDTH`, not
  `FRAME_INNER_WIDTH`; the frame bounding-box check is done in the frame's
  local frame. The fourth (plates overlapping at rev C's 135mm centre
  distance) was resolved by rev D's belt.
- Open: `SHAFT_HEIGHT_ABOVE_PLATE` (measurement, rev B §8), and the
  physical saddle fit on the new 2.4mm-thick belt (rev D §7).

If a later phase or revision changes the picture, this list is the thing to
update once the migration is done.

## Repo layout

```
phase1-cad-spec.md        rev A spec (superseded, kept as base document)
phase1-cad-spec-revB.md   rev B spec (superseded, diff against rev A)
phase1-cad-spec-revC.md   rev C spec (current for phase 1, diff against rev B)
phase2-cad-spec.md        skirts and posts (not yet built)
phase3-cad-spec.md        tooth profile, belt, pulley (rev A)
phase3-cad-spec-revB.md   phase 3 rev B (current for phase 3, diff against rev A)
phase4-cad-spec.md        assembly framework, frame, bridge plates (current)
sorter/                   the build123d project (run all commands from here)
  params.py               single source of truth for every dimension
  geometry.py              pure functions: run direction, shaft axes, at(), plate/frame datums
  parts/slat.py            the slat part (plain + cleated), pulley_envelope()
  parts/bridge_plate.py    plywood bridge plate (reference solid, cut list not STL)
  parts/frame.py           2020 aluminium frame (owned hardware, reference solid)
  assembly.py              GROUPS dict of positioned Compounds; `python assembly.py [group ...] [--detail]`
  cut_list.py              writes out/cut_list.txt for the plywood parts
  utils.py                 bbox/volume/contains/clash helpers used by checks & tests
  checks.py                human-facing runner of every acceptance assertion from the specs
  tests/                   the same assertions as pytest tests
  export.py                writes out/slat_plain.stl and out/slat_cleated.stl
```

## Conventions

- **No hard-coded dimensions outside `params.py`.** Every numeric
  dimension used anywhere in `sorter/` must be imported from `params.py`.
  If a part or check needs a new value, add it to `params.py` rather than
  inlining it.
- **Four layers, reading downward only** (phase 4 §2.1): `params` imports
  only `math`; `geometry.py` builds no solids and imports only `params`;
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
- **Adding a part to the machine** means one `<name>_group(detail)`
  function in `assembly.py` returning a positioned Compound, one `GROUPS`
  entry and one `COLOURS` entry. Nothing else should need touching.
- Acceptance criteria in the specs (rev B §5 substituted per rev C §5; phase 4 §8) are the contract:
  they're expressed both as `checks.py` (human-facing pass/fail output)
  and as the `tests/` pytest suite. Keep both in sync with whichever spec
  revision is current.
- Where the spec's prose is ambiguous or internally inconsistent, resolve
  it from the spec's own named-parameter definitions rather than its
  worked examples, and record the resolution and reasoning in
  `sorter/README.md` (see its "Saddle tab z-positions" and "Chamfer edge
  selection" sections for the existing pattern).
- Physical test fit is still the real gate: rev B §8 is explicit that
  `SADDLE_INTERFERENCE` and `CLEAT_HEIGHT` are unvalidated guesses until a
  printed plain + cleated slat pair is run on actual belt stock. Don't
  treat passing checks as physical validation.

## Workflow

```bash
cd sorter
source ../.venv/bin/activate   # or create one per sorter/README.md
python3 checks.py              # pass/fail per acceptance check
python -m pytest                # same assertions, pytest form
python3 export.py              # writes out/*.stl (gitignored)
python3 cut_list.py            # writes out/cut_list.txt for the plywood parts
python3 parts/slat.py          # opens one part in OCP CAD Viewer if running
python3 assembly.py frame plates   # the assembly, one colour per group; no args = every group
```

`checks.py` reports `XFAIL` for checks listed in its `_EXPECTED_FAILURES`
table and fails the run with `XPASS` if one of them starts passing; the
pytest twin is a `strict=True` xfail. Remove both when the cause is fixed.

## Out of scope so far

Per rev B §6 and phase 4 §1: pillow block standoffs, the real HTD-5M pulley
part, side skirts and posts, motor mount, coupler, hopper, brush mounts.
Their parameters may exist in `params.py` for later phases to reference,
but don't build the parts themselves until their phase. Don't add slats,
belts or pulleys to the assembly before phase 5.
