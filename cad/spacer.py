"""flexisette spacer frame — sets the inter-PCB gap (= SPACER_GAP). Two variants:

  variant="dummy" : beefier closed frame, no openings. The plain structural body;
                    prints mostly-solid with infill. Use when you don't need deck playback.
  variant="head"  : the original — front slot for the head-holes insert PLUS a head-bay
                    shelf with a pocket so the actual magnetic transmit head can mount
                    behind the head window (for playing in a real deck).
"""
from build123d import *
import machine_params as M

W, H, R = M.SHELL_W, M.SHELL_H, M.CORNER_R
GAP, IN_W = M.SPACER_GAP, M.INSERT_W


def part(variant: str = "head"):
    wall = M.DUMMY_WALL if variant == "dummy" else M.WALL
    with BuildPart() as p:
        with BuildSketch():
            RectangleRounded(W, H, R)
            RectangleRounded(W - 2 * wall, H - 2 * wall, max(R - wall, 0.6), mode=Mode.SUBTRACT)
        extrude(amount=GAP)

        if variant == "head":
            # front slot to receive the head-holes insert (front = -Y edge)
            with Locations((0, M.FRONT_Y, GAP / 2)):
                Box(IN_W, M.WALL * 2.5, GAP + 0.2, mode=Mode.SUBTRACT)
            # head-bay shelf: a cross-bar spanning the inner width (fuses to both side walls),
            # set just behind the front window
            bay_y = M.FRONT_Y + M.WALL + M.HEAD_BAY_D / 2
            with Locations((0, bay_y, GAP / 2)):
                Box(W - 2 * M.WALL, M.HEAD_BAY_D, GAP)                       # ADD (fuses)
            # pocket in the bar to seat the magnetic head, opening toward the window
            with Locations((0, bay_y, GAP / 2)):
                Box(M.HEAD_POCKET_W, M.HEAD_BAY_D + 0.4, M.HEAD_POCKET_H, mode=Mode.SUBTRACT)
    return p.part


def MATES(variant: str = "head"):
    m = {
        "pcb_bottom": Pos(0, 0, 0),
        "pcb_top": Pos(0, 0, GAP),
    }
    if variant == "head":
        m["insert_seat"] = Pos(0, M.FRONT_Y, GAP / 2)
        m["head_seat"] = Pos(0, M.FRONT_Y + M.WALL + M.HEAD_BAY_D / 2, GAP / 2)
    return m


if __name__ == "__main__":
    for v in ("dummy", "head"):
        s = part(v)
        print(f"spacer[{v}] valid:", s.is_valid(), "bbox:", tuple(round(x, 2) for x in s.bounding_box().size))
