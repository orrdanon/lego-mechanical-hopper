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
    offset   distance from the shaft axis along run_normal, mm; positive is
             outward through the belt, negative is down towards the plates
    lateral  distance along machine Z, mm

    `offset` is measured from the shaft axis, not the belt back face, so
    `at(t, 0)` is on the shaft and a slat on the carrying run is placed at
    `at(t, belt_back_radius())`. Every *_offset() datum below shares this
    origin. See sorter/README.md "Offset origin".

    The returned Location is oriented so that its local +x points along
    run_direction(), its local +y along run_normal(), and its local +z
    along machine +Z. Multiplying a part modelled in the spec's local frame
    (+x along the run, +y out along the normal, +z across) by this Location
    places it correctly with no extra rotation.
    """
    position = (
        shaft_axis("tail")
        + run_direction() * t
        + run_normal() * offset
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


# --- Bridge plates and frame -- phase 2 §5, phase 4 §4 -----------------------


def plate_top_offset() -> float:
    """Offset of the bridge plates' top faces from the shaft axis, along
    run_normal. Negative, since the plates are below the shafts.
    = -SHAFT_HEIGHT_ABOVE_PLATE = -48.0"""
    return -params.SHAFT_HEIGHT_ABOVE_PLATE


def rail_top_offset() -> float:
    """Offset of the frame rails' top faces from the shaft axis, along
    run_normal. Negative. = plate_top_offset() - PLATE_THICKNESS = -57.0"""
    return plate_top_offset() - params.PLATE_THICKNESS


def rail_lateral() -> float:
    """Z of a rail's centreline. = FRAME_WIDTH/2 - FRAME_PROFILE/2 = 127.0"""
    return params.FRAME_WIDTH / 2 - params.FRAME_PROFILE / 2


def frame_t_centre() -> float:
    """Run parameter at the frame's midpoint."""
    return params.FRAME_T_START + params.FRAME_LENGTH / 2


def frame_t_end() -> float:
    """Run parameter at the frame's head end."""
    return params.FRAME_T_START + params.FRAME_LENGTH


def plate_t(index: int) -> float:
    """Run parameter of bridge plate `index`, 0 at the tail shaft through
    PLATE_STATIONS-1 (4) at the head shaft, evenly spaced.
    Raises IndexError outside that range."""
    if not 0 <= index < params.PLATE_STATIONS:
        raise IndexError(f"plate index must be in 0..{params.PLATE_STATIONS - 1}, got {index}")
    return index * params.CENTRE_DIST / (params.PLATE_STATIONS - 1)


def plate_role(index: int) -> str:
    """'bearing' for the end plates (0 and PLATE_STATIONS-1), 'support'
    for the ones between. Raises IndexError outside 0..PLATE_STATIONS-1."""
    plate_t(index)   # range check
    if index in (0, params.PLATE_STATIONS - 1):
        return "bearing"
    return "support"
