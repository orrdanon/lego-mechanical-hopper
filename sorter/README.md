# sorter -- Phase 1

Parametric build123d model of the LEGO-sorter feed elevator: the shared
parameter and geometry modules, and the conveyor slat (plain and cleated
variants). See `phase1-cad-spec-revC.md` at the repo root for the current
spec this implements -- it diffs against `phase1-cad-spec-revB.md`, which
in turn diffs against `phase1-cad-spec.md` (rev A), the base document.

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

This opens the viewer showing a cleated slat. Without a running viewer
server, `ocp_vscode` prints a connection warning but the geometry still
builds correctly (exit code 0) -- useful for a headless sanity check.

## Running checks

```bash
python3 checks.py
```

Prints one pass/fail line per acceptance check from rev B §5 and exits
non-zero if any fail. This is the same set of assertions as the pytest
suite, just human-facing.

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
