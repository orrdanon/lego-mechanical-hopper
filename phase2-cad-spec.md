# Phase 2 — side skirts and their supports

Depends on `phase1-cad-spec.md` and `phase1-cad-spec-revB.md`. Read those first; the
coordinate conventions, module structure and hard rules there all apply unchanged.

Supersedes the provisional skirt block in rev B §3. Those numbers were placeholders and
two of them were wrong.

---

## 1. Purpose

Model the side skirts that stop bricks falling off the edges of the belt, together with
everything that holds them up. Two parts are printed; two are plywood and appear in the
model only as reference solids for clearance checking.

### In scope

- `parts/skirt_post.py` — printed support post
- `parts/skirt.py` — plywood strip, reference solid only
- `parts/bridge_plate.py` — plywood plate, reference solid only
- Parameter additions to `params.py`
- Geometry additions: plate and skirt datum functions
- Acceptance criteria, including two new clash tests

### Out of scope

Pillow block standoffs, the printed pulley, motor mount, coupler, hopper, brush. The
standoff in particular waits until real pillow blocks have been measured.

---

## 2. Why the skirt is plywood

A 3 mm wall, 35 mm tall, 420 mm long is a flat strip. Printing it would take hours, warp,
and need splicing across the bed. Cut it from 3 mm plywood or acrylic with a saw and it's
straighter than a printed part and costs nothing.

So the printed part is the bracket, not the wall. This is the same division as everywhere
else in the machine: buy or cut the long straight things, print the awkward connecting
shapes.

---

## 3. Arrangement

Five bridge plates span the frame's inner width, all identical rectangles of 9 mm
plywood, all bolted into the frame's T-slots and therefore positionable anywhere along
the run.

- **2 bearing plates**, at the tail and head, carrying the pillow blocks
- **3 support plates**, evenly spaced between them, each carrying two skirt posts

Six posts in total, three per side, dividing the skirt's span into four sections of
97.5 mm. The skirt cannot be supported at the two bearing plates because the pillow
blocks already occupy that lateral position.

The skirt itself runs longer than the centre distance so that it continues into the
hopper. If it stopped at the hopper's front wall, bricks would escape at the pickup
point, which is where the belt is most crowded.

---

## 4. Parameter additions

Append to `params.py` under new section headers. The skirt block from rev B §3 is
**replaced** by this one.

### Bridge plates

| Name | Value | Unit | Note |
|---|---|---|---|
| `PLATE_THICKNESS` | 9.0 | mm | plywood |
| `PLATE_WIDTH` | 45.0 | mm | along the run |
| `PLATE_LENGTH` | derived | mm | `FRAME_INNER_WIDTH` = 234.0 |
| `PLATE_COUNT_BEARING` | 2 | — | |
| `PLATE_COUNT_SUPPORT` | 3 | — | |

### Skirts

| Name | Value | Unit | Note |
|---|---|---|---|
| `SKIRT_INSET` | 41.0 | mm | inner face, from centreline |
| `SKIRT_THICKNESS` | 3.0 | mm | plywood |
| `SKIRT_RISE` | 28.0 | mm | above the slat top face |
| `SKIRT_DROP` | 4.0 | mm | below the slat underside |
| `SKIRT_HEIGHT` | derived | mm | `SKIRT_RISE + SLAT_THICKNESS + SKIRT_DROP` = 35.0 |
| `SKIRT_LENGTH` | 420.0 | mm | overruns the centre distance into the hopper |
| `SKIRT_GAP` | derived | mm | `SKIRT_INSET - SLAT_LENGTH/2` = 1.0 |

Two corrections against rev B: `SKIRT_INSET` was 38.0 and is now 41.0, and the total
height is 35 mm, not the 38 mm quoted earlier — that figure double-counted the slat
thickness.

### Skirt post

| Name | Value | Unit | Note |
|---|---|---|---|
| `POST_COUNT` | 6 | — | 3 per side |
| `POST_SPACING` | derived | mm | `CENTRE_DIST / 4` = 97.5 |
| `POST_HEIGHT` | 100.0 | mm | plate top to post top |
| `POST_COLUMN_WIDTH` | 18.0 | mm | along the run |
| `POST_COLUMN_THICKNESS` | 12.0 | mm | across the machine |
| `POST_FOOT_LENGTH` | 44.0 | mm | along the run |
| `POST_FOOT_DEPTH` | 34.0 | mm | across the machine, outboard |
| `POST_FOOT_THICKNESS` | 10.0 | mm | |
| `POST_BOLT_M` | 4.0 | mm | M4 throughout |

---

## 5. Geometry module additions

```python
def plate_top_offset() -> float:
    """Offset of the bridge plate's top face from the shaft axis, along
    run_normal. Negative, since the plate is below the shafts.
    Returns -SHAFT_HEIGHT_ABOVE_PLATE."""

def skirt_bottom_offset() -> float:
    """belt_back_radius() - SKIRT_DROP  ->  18.327"""

def skirt_top_offset() -> float:
    """belt_back_radius() + SLAT_THICKNESS + SKIRT_RISE  ->  53.327"""

def plate_t(index: int) -> float:
    """Run parameter of bridge plate `index`, 0 at the tail bearing plate
    through 4 at the head bearing plate, spaced CENTRE_DIST/4 apart."""

def post_stations() -> list[float]:
    """Run parameters of the three support plates: plate_t(1..3)."""
```

`plate_t` is the function future phases will use to place the motor mount and the brush,
so get its indexing right: plates 0 and 4 carry bearings, plates 1, 2 and 3 carry posts.

---

## 6. Part geometry

### 6.1 `skirt_post(side: str = "right") -> Part`

Printed, PETG. Local frame:

- **Local origin** at the centre of the foot's bottom face, which is the surface that
  sits on the plate's top face.
- **+x** along the run
- **+y** away from the plate, parallel to `run_normal`
- **+z** outboard, away from the machine centreline

The post's **inner face lies at local z = 0**, and that face is where the plywood skirt
bolts. Positioning the post is therefore just placing local z = 0 at machine
Z = `SKIRT_INSET + SKIRT_THICKNESS` = 44.0.

**Foot**: x ∈ [−22, 22], y ∈ [0, 10], z ∈ [0, 34]. Two M4 clearance holes through y, at
x = ±14, z = 17.

**Column**: x ∈ [−9, 9], y ∈ [10, 100], z ∈ [0, 12].

**Gusset**: a triangular web on the outboard side, from the column's z = 12 face down and
out to the foot's z = 34 edge, spanning y ∈ [10, 60]. Without it a 90 mm cantilever in
PETG will flex enough to matter.

**Skirt bolt holes**: two M4 clearance holes through the column along z, at y = 72 and
y = 92, x = 0. Those land at run_normal offsets of +24 and +44, both comfortably inside
the skirt's span of 18.327 to 53.327.

**Fillets**: 3 mm where the column meets the foot, on both sides.

`side="left"` returns the part mirrored about local z.

Print orientation: foot flat on the bed, column vertical. The gusset makes every
overhang self-supporting.

### 6.2 `skirt(side: str = "right") -> Part`

Reference solid, not printed. A plain rectangular strip:
`SKIRT_LENGTH` × `SKIRT_HEIGHT` × `SKIRT_THICKNESS`, with six M4 clearance holes matching
the post bolt pattern.

Model it in the machine frame directly rather than a local frame, since it has no
orientation ambiguity: inner face at machine Z = ±`SKIRT_INSET`, spanning run_normal
`skirt_bottom_offset()` to `skirt_top_offset()`, running from t = −15 to t = 405.

### 6.3 `bridge_plate() -> Part`

Reference solid. `PLATE_LENGTH` × `PLATE_WIDTH` × `PLATE_THICKNESS`, with four M5
clearance holes at its ends for the frame T-nuts. Both plate types share this body; the
bearing and post hole patterns are added by later phases.

---

## 7. Acceptance criteria

Additional to rev B §5, which still applies in full.

### 7.1 Parameter consistency

```
assert SKIRT_INSET - SLAT_LENGTH/2 == approx(SKIRT_GAP)
assert 0.5 <= SKIRT_GAP <= 1.5
assert SKIRT_HEIGHT == approx(SKIRT_RISE + SLAT_THICKNESS + SKIRT_DROP)
assert SKIRT_LENGTH > CENTRE_DIST                    # overruns into the hopper
assert POST_SPACING * 4 == approx(CENTRE_DIST)
assert POST_COLUMN_THICKNESS <= PLATE_WIDTH
```

### 7.2 The skirt overlaps the slat edge

```
assert skirt_bottom_offset() < belt_back_radius()
assert skirt_top_offset() - (belt_back_radius() + SLAT_THICKNESS) >= 25.0
```

The first is the one that matters. If the skirt's bottom edge sits level with the slat
top instead of below it, the only contact when the belt walks sideways is the slat's top
edge, and it will ride up and over.

### 7.3 Bolt holes land on the skirt

```
for y in (72.0, 92.0):
    offset = plate_top_offset() + y
    assert skirt_bottom_offset() + 5 < offset < skirt_top_offset() - 5
```

### 7.4 Clash tests

Two new ones, both real risks.

```
# the carrying run's slats must not touch the skirt
assert not clash(slat(True).moved(at(195, 0)), skirt("right"))
assert not clash(slat(True).moved(at(195, 0)), skirt("left"))

# the RETURNING run's slats pass between the posts
assert not clash(slat(True).moved(at_return(195)), skirt_post("right").moved(...))
```

The return-run check is the important one. The posts stand at machine Z = ±44 and rise
from the plate all the way past the returning belt, whose slats reach ±40. Four
millimetres of clearance, on both sides, on every one of the six posts. Verify it rather
than assuming it.

You will need a `geometry.at_return(t)` companion to `at()` for this — same run
parameter, opposite normal, and the part flipped. Add it.

### 7.5 Volume and validity

```
assert 38.0 <= volume_cm3(skirt_post()) <= 52.0
assert skirt_post().is_valid()
assert skirt_post("left").is_valid()
assert bbox_size(skirt_post()) == approx((44.0, 100.0, 34.0), abs=0.02)
```

---

## 8. Definition of done

1. All rev B assertions still pass — nothing here may break phase 1.
2. All §7 assertions pass.
3. `python parts/skirt_post.py` shows a post in the viewer.
4. A new `python assembly.py` shows: one bridge plate, two posts, both skirts, and three
   slats on the carrying run plus one on the return. That is the minimum needed to see
   by eye that the clearances are real.
5. `export.py` writes `out/skirt_post_left.stl` and `out/skirt_post_right.stl`.
6. The plywood parts are **not** exported as STL. Instead, write `out/cut_list.txt`
   giving the rectangle sizes and hole positions for the skirts and plates, which is what
   you actually need at the saw.

---

## 9. Note on assembly.py

This is the first phase with an assembly, so keep it honest from the start: a `detail`
flag that draws slats as plain boxes by default. Forty-five real slats with saddle
geometry will make the viewer crawl and turn every edit into a twenty-second wait. What
you are checking in the assembly is where things are, not what a fillet looks like.
