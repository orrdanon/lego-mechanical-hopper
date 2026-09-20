# lego-mechanical-hopper

Parametric build123d CAD model for a LEGO-sorting machine's feed elevator
(a cleated incline conveyor belt). Phase 1 scope is the conveyor slat only
(plain and cleated variants) plus the shared parameter/geometry modules —
not the frame, hopper, motor, or skirts.

## Spec authority

- **`phase1-cad-spec-revC.md`** (repo root) is the current spec. Read it first.
- `phase1-cad-spec-revB.md` (rev B) is superseded but still needed — rev C
  is a diff against it (see its §2 changelog), not a standalone rewrite.
  `phase1-cad-spec.md` (rev A) is superseded further back, kept as the base
  document rev B diffed against. Where any two conflict, the latest rev wins.
- If a future rev D (or later) spec file appears, treat it the same way:
  check its own header for what it supersedes and diffs against.

## Current implementation status

`sorter/params.py` matches rev C §3 (migrated from rev B — rev C §7's
"Definition of done" checklist is satisfied: every assertion in rev B §5 is
checked by both `checks.py` and `tests/` with rev C's substituted numbers,
`pytest` and `python checks.py` are green, `export.py` produces STLs at the
new dimensions, and `sorter/README.md` records why `SLAT_PITCH`/`SLAT_WIDTH`
changed and flags `CENTRE_DIST` as an open machine-layout question per rev C
§8 — not a provisional-parameter guess like `SHAFT_HEIGHT_ABOVE_PLATE`).
If a later revision changes the spec again, this paragraph is the thing to
update once the migration is done.

## Repo layout

```
phase1-cad-spec.md        rev A spec (superseded, kept as base document)
phase1-cad-spec-revB.md   rev B spec (superseded, diff against rev A)
phase1-cad-spec-revC.md   rev C spec (current, diff against rev B)
sorter/                   the build123d project (run all commands from here)
  params.py               single source of truth for every dimension
  geometry.py              pure functions: belt run direction, shaft axes, per-slat placement
  parts/slat.py            the slat part (plain + cleated), pulley_envelope()
  utils.py                 bbox/volume/contains/clash helpers used by checks & tests
  checks.py                human-facing runner of every acceptance assertion from the spec
  tests/                   the same assertions as pytest tests
  export.py                writes out/slat_plain.stl and out/slat_cleated.stl
```

## Conventions

- **No hard-coded dimensions outside `params.py`.** Every numeric
  dimension used anywhere in `sorter/` must be imported from `params.py`.
  If a part or check needs a new value, add it to `params.py` rather than
  inlining it.
- `geometry.py` builds no solids — it only supplies datums (directions,
  axes, per-slat placement) that parts position themselves against.
- Acceptance criteria in the spec (rev A §9 / rev B §5, substituted per rev C §5) are the contract:
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
python3 parts/slat.py          # opens in OCP CAD Viewer if running
```

## Out of scope for phase 1

Per rev B §6: bridge plates, pillow block standoffs, the real HTD-5M
pulley part, side skirts, motor mount, coupler, hopper, brush mounts.
Their parameters may exist in `params.py` for later phases to reference,
but don't build the parts themselves yet.
