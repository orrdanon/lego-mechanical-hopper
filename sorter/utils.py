"""Small, part-agnostic helpers for inspecting and comparing solids."""

from build123d import Box, Part, Pos


def _overlap_volume(a: Part, b: Part) -> float:
    result = a.intersect(b)
    if result is None:
        return 0.0
    return sum(shape.volume for shape in result)


def contains(part: Part, point: tuple[float, float, float], eps: float = 0.05) -> bool:
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


def clash(a: Part, b: Part, tol: float = 1e-6) -> bool:
    """True if the two solids overlap by more than `tol` mm^3."""
    return _overlap_volume(a, b) > tol
