#!/usr/bin/env python3
"""Spinning ASCII art with perspective projection, depth shading and flicker-free redraw.

Examples:
  python3 spin.py                       # default: cyan gradient, original art
  python3 spin.py -c magenta            # pick a color preset
  python3 spin.py -c 208                # any 256-color code (single color)
  python3 spin.py -c 27,51,231          # custom gradient: back -> front
  python3 spin.py -s '#*+'              # build the figure from these characters
  python3 spin.py -c green -s '@'       # combine both
  python3 spin.py -d up                 # spin bottom -> top (also: down, left, right, all)

Color presets: cyan, blue, green, red, magenta, yellow, white
"""

import argparse
import math
import shutil
import sys
import time

ART = [
    r"         /\ ",
    r"        /  \ ",
    r"       /    \ ",
    r"______/______\______",
    r"\    /        \    /",
    r" \  /          \  /",
    r"  \/            \/",
    r"  /\            /\ ",
    r" /  \          /  \ ",
    r"/____\________/____\ ",
    r"      \      / ",
    r"       \    / ",
    r"        \  / ",
    r"         \/ ",
]

COLOR_PRESETS = {
    "cyan":    [27, 33, 39, 45, 51, 81, 87, 123, 159, 195, 231],
    "blue":    [18, 19, 20, 21, 27, 33, 69, 75, 111, 147, 189],
    "green":   [22, 28, 34, 40, 46, 82, 118, 154, 190, 194, 231],
    "red":     [88, 124, 160, 196, 203, 209, 216, 217, 224, 231],
    "magenta": [54, 91, 127, 163, 199, 205, 213, 219, 225, 231],
    "yellow":  [94, 136, 178, 184, 220, 226, 227, 228, 229, 231],
    "white":   [240, 244, 248, 252, 255, 231],
}
DEFAULT_COLOR = "cyan"

THICKNESS = (0, 1)      # each point is also drawn one cell to the right -> thicker strokes
MIRROR_CHARS = {"/": "\\", "\\": "/"}  # glyphs to swap when the figure is seen from behind

CAMERA_DIST = 60.0      # distance from the eye to the pivot (larger = weaker perspective)
SPIN_SPEED = 1.1        # radians per second around the vertical axis
TILT_AMPLITUDE = 0.35   # radians of slow wobble around the horizontal axis
TARGET_FPS = 60
RESET = "\033[0m"


def parse_color(value):
    """Accept a preset name or a comma-separated list of 256-color codes."""
    if value in COLOR_PRESETS:
        return COLOR_PRESETS[value]
    try:
        codes = [int(part) for part in value.split(",")]
    except ValueError:
        codes = []
    if not codes or not all(0 <= c <= 255 for c in codes):
        names = ", ".join(COLOR_PRESETS)
        raise argparse.ArgumentTypeError(
            f"unknown color {value!r}: use a preset ({names}) or codes like 27,51,231"
        )
    return codes


def parse_chars(value):
    """Characters to build the figure from (spaces are ignored)."""
    chars = value.replace(" ", "")
    if not chars:
        raise argparse.ArgumentTypeError("--chars must contain at least one character")
    return chars


def load_points(art, chars=None):
    """Turn every visible character into a 3D point centred on the art's bounding box."""
    cells = [(col, row, ch)
             for row, line in enumerate(art)
             for col, ch in enumerate(line) if ch != " "]
    min_c = min(c for c, _, _ in cells)
    max_c = max(c for c, _, _ in cells)
    min_r = min(r for _, r, _ in cells)
    max_r = max(r for _, r, _ in cells)
    cx = (min_c + max_c) / 2
    cy = (min_r + max_r) / 2

    # Terminal cells are roughly twice as tall as they are wide, so the vertical
    # axis is doubled to keep the figure's proportions correct.
    points = []
    for i, (col, row, ch) in enumerate(cells):
        if chars:
            ch = chars[i % len(chars)]  # user-chosen symbols, cycled across the figure
        points.append((col - cx, (row - cy) * 2.0, ch))

    radius = max(math.hypot(x, y) for x, y, _ in points)
    art_w = max_c - min_c + 1
    art_h = max_r - min_r + 1
    return points, radius, art_w, art_h


def fit_scale(term_w, term_h, art_w, art_h):

    by_width = 0.95 * term_w / (1.2 * art_w)
    by_height = 0.95 * term_h / art_h
    return max(0.5, min(by_width, by_height, 4.0))


def spin_angles(direction, t):
    """Return (angle_y, angle_x): rotation around the vertical and horizontal axes."""
    spin = SPIN_SPEED * t
    wobble = TILT_AMPLITUDE * math.sin(t * 0.7)
    if direction == "right":   # left -> right
        return spin, wobble
    if direction == "left":    # right -> left
        return -spin, wobble
    if direction == "up":      # bottom -> top
        return wobble, spin
    if direction == "down":    # top -> bottom
        return wobble, -spin
  
    return spin, spin * 0.7


def project(points, angle, tilt, scale, w, h):
    """Rotate each point in 3D and project it onto the screen."""
    ca, sa = math.cos(angle), math.sin(angle)
    ct, st = math.cos(tilt), math.sin(tilt)
   
    mirrored = (ca < 0) != (ct < 0)
    projected = []
    for x, y, ch in points:
        glyph = MIRROR_CHARS.get(ch, ch) if mirrored else ch
        # Spin around the vertical axis.
        x1 = x * ca
        z1 = x * sa
        # Tilt around the horizontal axis.
        y2 = y * ct - z1 * st
        z2 = y * st + z1 * ct
        # Perspective: nearer points (z > 0) are magnified.
        k = CAMERA_DIST / (CAMERA_DIST - z2)
        sx = int(round(w / 2 + x1 * k * scale))
        sy = int(round(h / 2 + y2 * k * scale * 0.5))
        projected.append((z2, sx, sy, glyph))
    return projected


def draw(projected, w, h, radius, palette):
    """Paint the points into a grid, far to near, and return an ANSI string."""
    chars = [[" "] * w for _ in range(h)]
    colors = [[0] * w for _ in range(h)]
    n = len(palette)

    projected.sort(key=lambda p: p[0])  # far first, so near points overwrite
    for z, sx, sy, ch in projected:
        depth = min(1.0, max(0.0, (z / radius + 1) / 2))
        color = palette[int(depth * (n - 1))]
        for dx in THICKNESS:
            x = sx + dx
            if 0 <= x < w and 0 <= sy < h:
                chars[sy][x] = ch
                colors[sy][x] = color

    lines = []
    for y in range(h):
        parts = []
        current = None
        for x in range(w):
            c = colors[y][x]
            if c and c != current:
                parts.append(f"\033[1;38;5;{c}m")  # bold makes the strokes stand out
                current = c
            parts.append(chars[y][x])
        parts.append(RESET)
        lines.append("".join(parts))
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Spinning ASCII art in the terminal.")
    parser.add_argument(
        "-c", "--color", type=parse_color, default=COLOR_PRESETS[DEFAULT_COLOR],
        help="color preset (cyan, blue, green, red, magenta, yellow, white) "
             "or 256-color codes separated by commas, e.g. 27,51,231",
    )
    parser.add_argument(
        "-s", "--chars", type=parse_chars, default=None,
        help="characters to build the figure from, e.g. '#*+'. Default: the original art.",
    )
    parser.add_argument(
        "-d", "--direction", choices=["right", "left", "up", "down", "all"], default="right",
        help="spin direction: right (left->right, default), left, up (bottom->top), "
             "down (top->bottom), or all (tumble in every direction)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    points, radius, art_w, art_h = load_points(ART, args.chars)
    palette = args.color

    out = sys.stdout
    out.write("\033[?25l\033[2J")  # hide cursor, clear screen once
    out.flush()

    start = time.perf_counter()
    frame_time = 1.0 / TARGET_FPS
    last_size = None

    try:
        while True:
            t0 = time.perf_counter()
            t = t0 - start

            size = shutil.get_terminal_size((80, 24))
            w = size.columns
            h = max(1, size.lines - 1)  # keep the last line free so the screen never scrolls
            if (w, h) != last_size:
                out.write("\033[2J")  # terminal was resized: wipe leftovers
                last_size = (w, h)

            scale = fit_scale(w, h, art_w, art_h)
            angle, tilt = spin_angles(args.direction, t)

            frame = draw(project(points, angle, tilt, scale, w, h), w, h, radius, palette)
            out.write("\033[H" + frame)
            out.flush()

            elapsed = time.perf_counter() - t0
            time.sleep(max(0.0, frame_time - elapsed))
    except KeyboardInterrupt:
        pass
    finally:
        out.write(RESET + "\033[?25h\033[2J\033[H")  # restore cursor and clean up
        out.flush()


if __name__ == "__main__":
    main()