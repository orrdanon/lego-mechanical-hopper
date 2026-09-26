"""Small, part-agnostic helpers for inspecting and comparing solids."""

from build123d import BoundBox, Box, Part, Pos, Shape, ShapeList


def _volume(result) -> float:
    if result is None:
        return 0.0
    if isinstance(result, ShapeList):
        return sum(shape.volume for shape in result)
    return result.volume


def _overlap_volume(a: Shape, b: Shape) -> float:
    """Total volume shared by `a` and `b`, summed solid by solid.

    `Compound.intersect()` returns None for a multi-solid Compound such as
    the frame, so the intersection is taken pairwise over the solids of
    each shape. That double-counts only where a shape's own solids overlap
    each other, which no assembly group here does.

    Solids whose bounding boxes are disjoint share nothing, and are skipped
    without a boolean -- which is what keeps a whole-loop clash sweep cheap."""
    total = 0.0
    for solid_a in a.solids():
        box_a = solid_a.bounding_box()
        for solid_b in b.solids():
            if _boxes_overlap(box_a, solid_b.bounding_box()):
                total += _volume(solid_a.intersect(solid_b))
    return total


def _boxes_overlap(a: BoundBox, b: BoundBox) -> bool:
    return all(
        lo_a <= hi_b and lo_b <= hi_a
        for lo_a, hi_a, lo_b, hi_b in zip(a.min, a.max, b.min, b.max)
    )


def contains(part: Shape, point: tuple[float, float, float], eps: float = 0.05) -> bool:
    """True if `point` lies inside the solid. Implemented by intersecting a small
    box of side 2*eps centred on the point and testing for non-zero volume."""
    probe = Pos(*point) * Box(2 * eps, 2 * eps, 2 * eps)
    return _overlap_volume(part, probe) > 0.0


def volume_cm3(part: Part) -> float:
    """Volume in cubic centimetres, for readable assertions."""
    return part.volume / 1000.0


def bbox_size(part: Part) -> tuple[float, float, float]:
    """Bounding box extents as (x, y, z)."""
    box = part.bounding_box()
    size = box.size
    return (size.X, size.Y, size.Z)


def clash(a: Shape, b: Shape, tol: float = 1e-6) -> bool:
    """True if the two solids overlap by more than `tol` mm^3."""
    return _overlap_volume(a, b) > tol


def _box_gap(a: BoundBox, b: BoundBox) -> float:
    """Euclidean distance between two bounding boxes, 0 if they overlap."""
    return sum(
        max(lo_b - hi_a, lo_a - hi_b, 0.0) ** 2
        for lo_a, hi_a, lo_b, hi_b in zip(a.min, a.max, b.min, b.max)
    ) ** 0.5


def distance_within(a: Shape, b: Shape, limit: float) -> float:
    """The distance between `a` and `b` if it could be under `limit`;
    otherwise the gap between their bounding boxes, a lower bound that is
    already >= limit."""
    return min_distance(a, [b], limit)


def min_distance(a: Shape, others, limit: float) -> float:
    """The least distance_within(a, b, limit) over `others`, taking `a`'s
    bounding box once -- on a real slat that box costs more than most of
    the distances, which is what keeps a whole-loop sweep cheap."""
    box = a.bounding_box()
    least = float("inf")
    for b in others:
        gap = _box_gap(box, b.bounding_box())
        least = min(least, gap if gap >= limit else a.distance_to(b))
    return least
