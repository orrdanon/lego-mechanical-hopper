"""Small, part-agnostic helpers for inspecting and comparing solids."""

from build123d import Box, Part, Pos, Shape, ShapeList


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
    each other, which no assembly group here does."""
    total = 0.0
    for solid_a in a.solids():
        for solid_b in b.solids():
            total += _volume(solid_a.intersect(solid_b))
    return total


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
