"""flexisette PCB half — a cassette-outline plate. Used as both top and bottom of the sandwich."""
from build123d import *
import machine_params as M

# named constants drive BOTH geometry and mates
W, H, R, T = M.SHELL_W, M.SHELL_H, M.CORNER_R, M.PCB_T


def part():
    with BuildPart() as p:
        with BuildSketch():
            RectangleRounded(W, H, R)
        extrude(amount=T)
    return p.part


# Mate convention: +Z points OUT along the joining (stack) direction; origin on the contact face.
MATES = {
    "outer": Pos(0, 0, 0),       # outward face (cassette exterior)
    "inner": Pos(0, 0, T),       # inward face (touches the spacer)
}

if __name__ == "__main__":
    s = part()
    print("pcb_half valid:", s.is_valid(), "bbox:", s.bounding_box().size)
