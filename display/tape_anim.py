"""display/tape_anim.py — 128x64 1-bit cassette tape-winding animation for the tape-window OLED.

Renders the iconic two-reel winding loop at the SSD1306's NATIVE 128x64 mono resolution — the way
it will look glowing through the cassette's central tape window (21.2 x 12 mm) with a 0.96" OLED
mounted behind. Output: a looping GIF (scaled x4 with NEAREST so the pixels stay crisp) + one still.

This file is the *look* / source-of-truth for the motion. Firmware (ESP32 SSD1306, I2C) either ships
these frames as a bitmap loop or re-implements the same parametric math on-device.

    python3 display/tape_anim.py  ->  display/build/tape_winddown.gif + tape_still.png
"""
import math
import os

from PIL import Image, ImageDraw

W, H = 128, 64        # SSD1306 0.96" native resolution
N = 36                # frames per loop
SCALE = 4             # preview upscale (NEAREST -> keep the 1-bit pixels hard)
TURNS = 2             # hub revolutions per loop (integer + 6 spokes -> seamless)

CX = (34, 94)         # left (supply) / right (take-up) reel centers, x
CY = 30               # reel center, y
HUB_R = 6             # hub spline radius
R_MID, R_AMP = 20, 8  # tape pack radius oscillates 12..28 (transfer L<->R)
SPOKES = 6
HEAD = (64, 61)       # tape passes the head/capstan at bottom center


def _reel(d, cx, r, ang):
    d.ellipse([cx - r, CY - r, cx + r, CY + r], outline=255, width=1)        # tape pack edge
    ir = (r + HUB_R) // 2
    d.ellipse([cx - ir, CY - ir, cx + ir, CY + ir], outline=255, width=1)    # a wound ring
    d.ellipse([cx - HUB_R, CY - HUB_R, cx + HUB_R, CY + HUB_R], outline=255, width=1)  # hub
    for k in range(SPOKES):
        a = ang + k * 2 * math.pi / SPOKES
        d.line([cx, CY, cx + HUB_R * math.cos(a), CY + HUB_R * math.sin(a)], fill=255)   # spline
        d.line([cx + (r - 2) * math.cos(a), CY + (r - 2) * math.sin(a),
                cx + r * math.cos(a), CY + r * math.sin(a)], fill=255)                   # pack tick


def frame(t):
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    ang = 2 * math.pi * TURNS * t
    rL = R_MID + R_AMP * math.cos(2 * math.pi * t)   # left winds down then back (seamless)
    rR = R_MID - R_AMP * math.cos(2 * math.pi * t)
    d.line([(CX[0], CY + rL), HEAD, (CX[1], CY + rR)], fill=255)   # tape across the head
    d.line([HEAD[0], HEAD[1] - 3, HEAD[0], HEAD[1] + 2], fill=255)  # head/capstan tick
    _reel(d, CX[0], rL, ang)
    _reel(d, CX[1], rR, ang)
    return img.point(lambda p: 255 if p >= 128 else 0)   # hard 1-bit threshold (no AA)


if __name__ == "__main__":
    bdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build")
    os.makedirs(bdir, exist_ok=True)
    frames = [frame(i / N) for i in range(N)]
    big = [f.resize((W * SCALE, H * SCALE), Image.NEAREST) for f in frames]
    big[0].save(os.path.join(bdir, "tape_winddown.gif"), save_all=True,
                append_images=big[1:], duration=55, loop=0)
    big[9].save(os.path.join(bdir, "tape_still.png"))
    print(f"wrote tape_winddown.gif  ({W}x{H} native, {N} frames, {TURNS} turns/loop)")
