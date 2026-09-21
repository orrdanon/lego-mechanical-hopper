# Phase 4 — the assembly framework

Depends on phases 1–3. Coordinate conventions and hard rules from `phase1-cad-spec.md`
apply unchanged.

This phase is mostly architecture. The visible deliverable is small on purpose: the
aluminium frame and the five bridge plates, each viewable on its own and the two
together. If that works, every later part slots in without redesigning anything.

---

## 1. The initial achievement

Three commands must work:

```
python parts/frame.py          # the aluminium frame alone
python parts/bridge_plate.py   # one plate alone
python assembly.py frame plates  # both, in position
```

That is the whole target. Resist adding slats, belts or pulleys to the assembly in this
phase — they exist, and putting them in now hides whether the framework itself is sound.

---

## 2. Architecture rules

These are the point of the phase. Every later part depends on them being followed
exactly.

### 2.1 Four layers, reading upward only

| Layer | Answers | Returns | May import |
|---|---|---|---|
| `params.py` | what did we choose | floats | `math` |
| `geometry.py` | where, how far | floats, `Location` | `params` |
| `parts/*.py` | what shape | `Part` | `params`, `geometry` |
| `assembly.py` | what goes where | `Compound` | all three |

Nothing reaches downward. `params` never imports `geometry`; `geometry` never builds a
solid; `parts` never computes a machine position.

### 2.2 Parts hold no positions

A part function returns a solid in its own local frame, as though it were the only object
in the universe. It must not reference `INCLINE`, `t`, `plate_t()`, `at()` or any station.

A part **may** import a scalar from `geometry` when that scalar is one of its own
dimensions — `skirt_post()` legitimately asks for `SHAFT_HEIGHT_ABOVE_PLATE` to know how
tall it is. The line is: dimensions yes, positions no.

### 2.3 Local origin at the mating surface

Every part's local origin sits on the face that mates with something else, not at its
centroid and not at a corner. This is what makes placement a single call with no
corrective offsets.

- **Bridge plate** — centre of its **top** face, the surface the pillow blocks and posts
  bolt to.
- **Frame rail** — centre of its **top** face, the surface the plates sit on.
- **Skirt post** — centre of its **foot's bottom** face, the surface that meets the plate.
- **Slat** — centre of its **belt-contact** face. (Already so, from phase 1.)

Local axis convention for any part placed by `at()`: **+x along the run, +y out along the
run normal, +z across the machine.** A part modelled that way places correctly with no
extra rotation.

Document each part's origin in its docstring. When a future part sits 9 mm out of place,
this is the first thing you will check.

---

## 3. Parameter additions

| Name | Value | Unit | Note |
|---|---|---|---|
| `FRAME_T_START` | −60.0 | mm | run parameter at the frame's tail end |
| `FRAME_END_LENGTH` | derived | mm | `FRAME_INNER_WIDTH` = 234.0 |
| `RAIL_SLOT_WIDTH` | 6.0 | mm | already present as `FRAME_SLOT_WIDTH`; reuse it |
| `RAIL_SLOT_DEPTH` | 6.0 | mm | modelled cosmetically |
| `PLATE_STATIONS` | 5 | — | |

`FRAME_LENGTH` (552), `FRAME_WIDTH` (274), `FRAME_PROFILE` (20), `FRAME_INNER_WIDTH`
(234), `PLATE_THICKNESS` (9), `PLATE_WIDTH` (45) already exist from phases 2 and 3.

Assert `FRAME_T_START + FRAME_LENGTH > CENTRE_DIST + 60` — the frame must overhang the
head shaft far enough to carry the motor.

---

## 4. `geometry.py` additions

```python
def rail_top_offset() -> float:
    """Offset of the frame rails' top faces from the shaft axis, along
    run_normal. Negative. = plate_top_offset() - PLATE_THICKNESS = -57.0"""

def rail_lateral() -> float:
    """Z of a rail's centreline. = FRAME_WIDTH/2 - FRAME_PROFILE/2 = 127.0"""

def frame_t_centre() -> float:
    """Run parameter at the frame's midpoint."""

def frame_t_end() -> float:
    """Run parameter at the frame's head end."""

def plate_t(index: int) -> float:
    """Run parameter of bridge plate `index`, 0 at the tail shaft through
    4 at the head shaft. Raises IndexError outside 0..4."""

def plate_role(index: int) -> str:
    """'bearing' for plates 0 and 4, 'support' for 1, 2 and 3."""
```

`plate_t` was sketched in phase 2; this is its real definition. `plate_role` exists so
later phases ask the geometry layer which plate carries what, rather than hard-coding
indices in the assembly.

---

## 5. `parts/frame.py`

The frame is **owned hardware, not a printed part**. It is a reference solid: modelled so
other things can be positioned against it and clash-tested, never exported as STL.

```python
def rail(length: float) -> Part:
    """A length of 2020 extrusion. Local origin at the centre of the top
    face; length along local x, 20 mm along local z, extending 20 mm
    into negative local y."""

def frame() -> Compound:
    """The complete rectangle: two rails of FRAME_LENGTH at
    lateral = +/- rail_lateral(), and two end members of FRAME_END_LENGTH
    spanning between them at each end. All four top faces coplanar."""
```

Model the extrusion as a 20 × 20 prism with a `RAIL_SLOT_WIDTH` × `RAIL_SLOT_DEPTH`
rectangular groove centred on each of the four faces. The groove is cosmetic — it is
there so you can see at a glance which faces are available for T-nuts. Do not model the
internal T profile; it buys nothing and multiplies faces.

End members are the same `rail()` solid. Because `at()` gives +z across the machine, an
end member is just a rail whose length runs along local z — build it by rotating 90°
about local y inside `frame()`, not by making a second part function.

`frame()` returns a `Compound` already positioned in the machine frame. It is the one
exception to rule 2.2, because the frame *is* a fixed piece of the world rather than a
repeatable part, and there is exactly one of it. State that exception in its docstring.

---

## 6. `parts/bridge_plate.py`

Completes the stub from phase 2.

```python
def bridge_plate(role: str = "support") -> Part:
    """A plywood bridge plate. Local origin at the centre of the top face.
    Length PLATE_LENGTH along local z, PLATE_WIDTH along local x,
    PLATE_THICKNESS into negative local y.

    role='bearing' or 'support' — identical body, different hole pattern.
    Both patterns may be empty in this phase; add them in phase 5."""
```

Four M5 clearance holes, two at each end, positioned to land in the rail slots: at
local z = ±(`FRAME_INNER_WIDTH`/2 − 10) and local x = ±12.

The body is identical for both roles. Keep the `role` argument now even though it changes
nothing yet, so phase 5 adds holes rather than changing the signature.

---

## 7. `assembly.py` — the framework

This is the part worth getting right.

### 7.1 Groups

```python
def frame_group() -> Compound:
    """The aluminium frame, as owned."""

def plates_group() -> Compound:
    """Five bridge plates at plate_t(0..4), each placed with
    at(plate_t(i), plate_top_offset())."""

GROUPS: dict[str, Callable[[], Compound]] = {
    "frame": frame_group,
    "plates": plates_group,
}
```

Later phases add entries to `GROUPS` and nothing else. That is the extension point, and
the reason this phase exists.

### 7.2 Building and showing

```python
def assembly(*names: str, detail: bool = False) -> dict[str, Compound]:
    """Build the named groups, or every group if none are named.
    Returns a mapping so the viewer can name and colour them.
    Unknown names raise ValueError listing the valid ones."""

def show_assembly(*names: str, detail: bool = False) -> None:
    """Build and display, one colour per group, names shown in the tree."""
```

Assign a fixed colour per group in a `COLOURS` dict so a group keeps its colour between
runs. Being able to say "the amber thing is 4 mm out" is worth more than it sounds.

### 7.3 Command line

```
python assembly.py                 # everything
python assembly.py frame           # just the frame
python assembly.py frame plates    # both
python assembly.py plates --detail
```

Parse with `sys.argv` only. No `argparse`, no config file, no new dependency.

### 7.4 The detail flag

Nothing in this phase is heavy enough to need it, and it must be built anyway. `detail`
defaults to `False`; each group decides what that means for itself. For now both groups
ignore it. Phase 5 makes `slats_group()` honour it by drawing plain boxes.

Establishing the flag now costs one argument. Retrofitting it after forty-five slats are
already in the assembly costs an afternoon.

---

## 8. Acceptance criteria

### 8.1 Geometry

```
assert rail_top_offset() == approx(-57.0)
assert rail_lateral() == approx(127.0)
assert plate_t(0) == approx(0.0)
assert plate_t(4) == approx(CENTRE_DIST)
assert [plate_role(i) for i in range(5)] == \
       ["bearing", "support", "support", "support", "bearing"]
with pytest.raises(IndexError): plate_t(5)
```

### 8.2 The frame

```
f = frame()
assert f.is_valid()
bb = bbox_size(f)
assert sorted(bb)[-1] == approx(FRAME_LENGTH, abs=0.5)
assert len(f.solids()) == 4
```

The bounding box is checked loosely because the frame is inclined in the machine frame,
so its axis-aligned box is not 552 × 274 × 20. Check the longest extent and the solid
count; a stricter test belongs in the frame's own local frame if you want one.

### 8.3 Plates sit on the rails

```
for i in range(PLATE_STATIONS):
    p = bridge_plate(plate_role(i)).moved(at(plate_t(i), plate_top_offset()))
    assert not clash(p, frame(), tol=1.0)
```

They must **touch and not overlap**. A tolerance of 1 mm³ allows for coincident faces
without permitting a real intersection. If this fails by a large volume, `rail_top_offset`
and `PLATE_THICKNESS` disagree.

### 8.4 Plates span the rails

```
p = bridge_plate()
assert bbox_size(p)[2] == approx(FRAME_INNER_WIDTH, abs=0.02)
```

### 8.5 Plates don't collide with each other or the frame ends

```
placed = [bridge_plate().moved(at(plate_t(i), plate_top_offset()))
          for i in range(PLATE_STATIONS)]
for a, b in combinations(placed, 2):
    assert not clash(a, b)
```

### 8.6 The framework itself

```
assert set(assembly().keys()) == set(GROUPS)
assert set(assembly("frame").keys()) == {"frame"}
with pytest.raises(ValueError): assembly("drivetrain")
assert assembly("plates")["plates"].is_valid()
```

---

## 9. Definition of done

1. Everything from phases 1–3 still passes.
2. All §8 assertions pass.
3. `python parts/frame.py` shows the frame alone.
4. `python parts/bridge_plate.py` shows one plate alone.
5. `python assembly.py frame plates` shows five plates sitting on an inclined frame, in
   two distinct colours, each named in the viewer tree.
6. `export.py` is unchanged — neither the frame nor the plates produce an STL. The plate
   goes in `out/cut_list.txt` instead.
7. The README gains a short section: the four layers, the local-origin rule, and how to
   add a group.

---

## 10. How later phases extend this

Adding the drivetrain should be exactly this and nothing more:

```python
def drivetrain_group() -> Compound:
    shafts = [shaft().moved(at(t, 0)) for t in (0.0, CENTRE_DIST)]
    pulleys = [pulley().moved(at(t, 0, lateral=z))
               for t in (0.0, CENTRE_DIST) for z in (-BELT_SPACING/2, BELT_SPACING/2)]
    return Compound(children=shafts + pulleys)

GROUPS["drivetrain"] = drivetrain_group
```

Four lines, no new positions invented, nothing else in the project touched. If adding a
group ever needs more than that, the framework is wrong and should be fixed rather than
worked around.
