"""The hopper's two strip brushes (hopper-spec §3.4, §4.8): a bought nylon
door-sweep strip cut to BRUSH_LEN. Reference solids only, never exported,
modelled undeflected; the sizes are provisional until the strip is measured.

Backing and bristles are separate solids because they are treated
differently: the backing sits in its clamp's slot and is clash-checked like
any part, while the bristles are meant to touch the slats and are exempt
from the slat clearance sweep.

Local frame for both: origin on the root line, where the bristles leave the
backing, at mid-length; the bristles hang into -y, the backing stands in +y,
+z along the strip. A clamp's rake is a rotation about local z.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build123d import Align, Box, Part

import params as p


def brush_backing() -> Part:
    """BRUSH_BACKING_W thick, BRUSH_BACKING_H high, BRUSH_LEN long."""
    backing = Box(p.BRUSH_BACKING_W, p.BRUSH_BACKING_H, p.BRUSH_LEN, align=(Align.CENTER, Align.MIN, Align.CENTER))
    backing.label = "brush backing"
    return backing


def brush_bristles() -> Part:
    """The bristle tuft as a block, BRUSH_BRISTLE_T thick and BRUSH_FREE_LEN
    long, straight, as if nothing pressed on it."""
    bristles = Box(p.BRUSH_BRISTLE_T, p.BRUSH_FREE_LEN, p.BRUSH_LEN, align=(Align.CENTER, Align.MAX, Align.CENTER))
    bristles.label = "brush bristles"
    return bristles


if __name__ == "__main__":
    from ocp_vscode import show

    show(brush_backing(), brush_bristles())
