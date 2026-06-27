"""insert.py — flexisette tape-head insert (the trapezoidal piece at the cassette bottom).

The vendor split this into two color-halves for multicolor first-layer printing
(side-1-insert + side-2-insert). They fit together with one FLIPPED OVER (180° about Z),
mating open-face-to-open-face into the hollow trapezoidal shell. We union them into one
watertight piece; it prints solid (slicer infill). The trapezoidal footprint clears the
PCB/frame cutouts and seats neatly into the frame's trapezoidal bottom section.

Source: Minecraft Soundtrack Cassette Shell remix, Printables #836410 (see assets/DOWNLOADS.md).

    python3 cad/insert.py -> build/insert.stl
"""
import os
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets", "cassette-shell-minecraft")
SRC1 = os.path.join(A, "side-1-insert.stl")
SRC2 = os.path.join(A, "side-2-insert.stl")


def solid():
    a = trimesh.load(SRC1); a.apply_translation(-a.bounding_box.centroid)
    b = trimesh.load(SRC2); b.apply_translation(-b.bounding_box.centroid)
    b.apply_transform(trimesh.transformations.rotation_matrix(np.radians(180), [0, 0, 1]))  # flip over
    b.apply_translation(-b.bounding_box.centroid)
    return trimesh.boolean.union([a, b], engine="manifold")     # closed trapezoidal shell


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    u = solid()
    out = os.path.join(HERE, "build", "insert.stl")
    u.export(out)
    print("insert:", np.round(u.extents, 2).tolist(),
          "watertight", u.is_watertight,
          "bodies", len(u.split(only_watertight=False)),
          "fill", round(u.volume / float(np.prod(u.extents)), 2),
          "(closed shell — prints solid with infill)")
