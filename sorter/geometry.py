"""Geometric datums shared by every part.

Pure functions only -- no solids are built here. Every future part positions
itself against `at()`, so its correctness is the foundation the rest of the
project stands on.
"""

import math

from build123d import Location, Plane, Vector

import params


def run_direction() -> Vector:
    """Unit vector along the belt run, in machine coordinates."""
    theta = math.radians(params.INCLINE)
    return Vector(math.cos(theta), math.sin(theta), 0.0)


def run_normal() -> Vector:
    """Unit vector perpendicular to the run, out of the carrying face."""
    theta = math.radians(params.INCLINE)
    return Vector(-math.sin(theta), math.cos(theta), 0.0)


def belt_back_radius() -> float:
    """Distance from a shaft axis to the belt's smooth outer face, mm."""
    pulley_od_radius = params.PULLEY_PD / 2 - params.BELT_PLD
    return pulley_od_radius + params.BELT_THICKNESS


def shaft_axis(end: str) -> Vector:
    """Point on the tail ('tail') or head ('head') shaft axis at Z = 0.
    Raises ValueError for any other value."""
    if end == "tail":
        return Vector(0.0, 0.0, 0.0)
    if end == "head":
        return run_direction() * params.CENTRE_DIST
    raise ValueError(f"end must be 'tail' or 'head', got {end!r}")


def at(t: float, offset: float = 0.0, lateral: float = 0.0) -> Location:
    """A Location on the carrying run.

    t        distance along the run from the tail shaft axis, mm
    offset   distance outward from the belt back face along run_normal, mm
    lateral  distance along machine Z, mm

    The returned Location is oriented so that its local +x points along
    run_direction(), its local +y along run_normal(), and its local +z
    along machine +Z. Multiplying a part modelled in the slat local frame
    by this Location places it correctly on the belt.
    """
    radial = belt_back_radius() + offset
    position = (
        shaft_axis("tail")
        + run_direction() * t
        + run_normal() * radial
        + Vector(0.0, 0.0, 1.0) * lateral
    )
    plane = Plane(origin=position, x_dir=run_direction(), z_dir=Vector(0.0, 0.0, 1.0))
    return Location(plane)


def slat_t(index: int) -> float:
    """Run parameter of slat `index`, counting from 0 at the tail."""
    return index * params.SLAT_PITCH


def is_cleated(index: int) -> bool:
    """True if slat `index` carries a cleat."""
    return index % params.CLEAT_EVERY == 0
