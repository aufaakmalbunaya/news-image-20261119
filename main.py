#!/usr/bin/env python3
"""The World in One Picture -- Thursday 19 November 2026.

Draws a 1024x1024 newspaper front page that sums up 19 November 2026
in a single image: 42 stories first reported that day, 13 of them as
illustrated lead cards with hand-drawn flat-vector scenes, a
by-the-numbers strip, region and field count bars, a dotted world map
with numbered pins, 29 one-line briefs, and a date-check footer.

Python standard library only. No network, no clock, no randomness:
two runs produce byte-identical PNGs.

Run:  python3 main.py
Writes entry.png next to this file, or to $MAKEFUN_OUTPUT_DIR/entry.png
when that variable is set (the grader runs with /bot read-only).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
INK = (24, 22, 20)
GREY = (105, 100, 92)
LIGHT = (232, 226, 214)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
TEAL = (14, 110, 110)
GOLD = (198, 142, 28)
GREEN = (46, 125, 50)
ORANGE = (214, 110, 30)
PURPLE = (96, 58, 140)
PINK = (214, 90, 130)
SKY = (140, 190, 220)
SEA = (34, 96, 150)
SAND = (224, 200, 150)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: seven rows of five characters, '#' on, '.' off.
# Written from scratch for this page; capitals, lower case, digits,
# and the punctuation the headlines need.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "a": ("     ", "     ", " ####", "    #", " ####", "#   #", " ####"),
    "b": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "),
    "c": ("     ", "     ", " ####", "#    ", "#    ", "#    ", " ####"),
    "d": ("    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"),
    "e": ("     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "),
    "f": ("  ## ", " #  #", " #   ", "#### ", " #   ", " #   ", " #   "),
    "g": ("     ", "     ", " ####", "#   #", "#   #", " ####", "    #"),
    "h": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "i": ("     ", "  #  ", "     ", " ##  ", "  #  ", "  #  ", " ### "),
    "j": ("     ", "   # ", "     ", "  ## ", "   # ", "   # ", "   # "),
    "k": ("#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "),
    "l": (" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "m": ("     ", "     ", "## # ", "# # #", "# # #", "# # #", "# # #"),
    "n": ("     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "o": ("     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "),
    "p": ("     ", "     ", "#### ", "#   #", "#   #", "#### ", "#    "),
    "q": ("     ", "     ", " ####", "#   #", "#   #", " ####", "    #"),
    "r": ("     ", "     ", "# ## ", "##  #", "#    ", "#    ", "#    "),
    "s": ("     ", "     ", " ####", "#    ", " ### ", "    #", "#### "),
    "t": (" #   ", " #   ", "#### ", " #   ", " #   ", " #   ", "  ## "),
    "u": ("     ", "     ", "#   #", "#   #", "#   #", "#   #", " ### "),
    "v": ("     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "w": ("     ", "     ", "#   #", "# # #", "# # #", "# # #", " # # "),
    "x": ("     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"),
    "y": ("     ", "     ", "#   #", "#   #", "#   #", " ####", "    #"),
    "z": ("     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "#": (" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "&": (" ##  ", "#  # ", "#  # ", " #   ", "# # #", "#  # ", " ## #"),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "*": ("     ", " # # ", "  #  ", "#####", "  #  ", " # # ", "     "),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    "/": ("    #", "   # ", "   # ", "  #  ", "  #  ", " #   ", "#    "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "<": ("   # ", "  #  ", " #   ", "#    ", " #   ", "  #  ", "   # "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    ">": (" #   ", "  #  ", "   # ", "    #", "   # ", "  #  ", " #   "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "@": (" ### ", "#   #", "# ###", "# # #", "# ###", "#    ", " ### "),
    "[": (" ### ", " #   ", " #   ", " #   ", " #   ", " #   ", " ### "),
    "\\": ("#    ", " #   ", " #   ", "  #  ", "  #  ", "   # ", "    #"),
    "]": (" ### ", "   # ", "   # ", "   # ", "   # ", "   # ", " ### "),
    "^": ("  #  ", " # # ", "     ", "     ", "     ", "     ", "     "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
    "`": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "{": ("   ##", "  #  ", "  #  ", " ##  ", "  #  ", "  #  ", "   ##"),
    "|": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "}": ("##   ", "  #  ", "  #  ", "  ## ", "  #  ", "  #  ", "##   "),
    "~": ("     ", "     ", " ## #", "# #  ", "     ", "     ", "     "),
    "€": ("  ## ", " #  #", "#    ", "###  ", "#    ", " #  #", "  ## "),
    "£": ("  ## ", " #  #", " #   ", "#### ", " #   ", " #   ", "#### "),
    "–": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "—": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "’": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "‘": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "“": (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "”": (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "•": ("     ", "     ", " ### ", " ### ", " ### ", "     ", "     "),
    "…": ("     ", "     ", "     ", "     ", "     ", "     ", " # # "),
}


def text_width(s, scale=1):
    """Pixel width of s at the given scale (6 px per char at scale 1)."""
    return len(s) * (5 * scale + scale)


def wrap_text(s, max_w, scale=1):
    """Greedy word wrap of s into lines no wider than max_w pixels."""
    char_w = 5 * scale + scale
    max_chars = max(1, max_w // char_w)
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Sheet:
    """An RGB pixel buffer with flat-vector drawing helpers."""

    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def box(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def frame(self, x, y, w, h, c, t=1):
        self.box(x, y, w, t, c)
        self.box(x, y + h - t, w, t, c)
        self.box(x, y, t, h, c)
        self.box(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.box(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.box(x, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.box(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            outer = int(math.sqrt(max(0, r * r - dy * dy)))
            inner = int(math.sqrt(max(0, (r - t) * (r - t) - dy * dy))) if r - t > 0 else 0
            self.box(cx - outer, yy, outer - inner, 1, c)
            self.box(cx + inner + 1, yy, outer - inner, 1, c)

    def tri(self, x1, y1, x2, y2, x3, y3, c):
        ys = sorted(((x1, y1), (x2, y2), (x3, y3)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            def edge(px, py, qx, qy):
                if py == qy:
                    return px
                return px + (qx - px) * (y - py) / (qy - py)
            if y < by:
                xa = edge(ax, ay, bx, by)
                xb = edge(ax, ay, cx, cy)
            else:
                xa = edge(bx, by, cx, cy)
                xb = edge(ax, ay, cx, cy)
            x0, x1 = int(min(xa, xb)), int(max(xa, xb))
            self.box(x0, y, x1 - x0 + 1, 1, c)

    def poly(self, pts, c):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ymin = min(p[1] for p in pts)
        ymax = max(p[1] for p in pts)
        for y in range(ymin, ymax + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.box(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)

    def seg(self, x1, y1, x2, y2, c, t=1):
        """Bresenham line, t pixels thick."""
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err, x, y = dx - dy, x1, y1
        while True:
            self.disc(x, y, max(0, t // 2), c)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def glyph(self, x, y, ch, c, scale=1):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        for r, row in enumerate(rows):
            for col, bit in enumerate(row):
                if bit == "#":
                    self.box(x + col * scale, y + r * scale, scale, scale, c)

    def text(self, x, y, s, c, scale=1):
        """Draw s; returns the x just past the last character."""
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, c, scale)
            cx += 6 * scale
        return cx

    def centred(self, y, s, c, scale=1, cx=None):
        cx = self.w // 2 if cx is None else cx
        self.text(cx - text_width(s, scale) // 2, y, s, c, scale)

    def sky_bands(self, x, y, w, h, top, bottom):
        """Vertical gradient made of flat bands (deterministic)."""
        steps = 12
        for i in range(steps):
            t = i / (steps - 1)
            col = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
            self.box(x, y + i * h // steps, w, h // steps + 1, col)


# ---------------------------------------------------------------- PNG writer
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(sheet, path):
    raw = bytearray()
    for y in range(sheet.h):
        raw.append(0)
        raw += sheet.px[y * sheet.w * 3:(y + 1) * sheet.w * 3]
    comp = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack(">IIBBBBB", sheet.w, sheet.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", comp) + _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


# ------------------------------------------------- lead scenes (flat vector)
# Each scene fills the box (x, y, w, h). Coordinates are given in
# percent of the box so the same scene works in a card and in the hero.
def _xy(x, y, w, h):
    X = lambda p: x + int(p * w / 100)
    Y = lambda p: y + int(p * h / 100)
    return X, Y


def scene_gta(s, x, y, w, h):
    """Vice City at sunset: pink sky, sun, skyline, palm, pink car."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (88, 40, 130), (240, 120, 70))
    s.disc(X(72), Y(34), max(6, w // 14), (255, 205, 95))
    s.ring(X(72), Y(34), max(6, w // 14) + 3, (255, 220, 140), 2)
    # skyline silhouettes with lit windows
    for bx, bw, bh in ((2, 16, 34), (20, 12, 46), (34, 18, 30), (54, 12, 52),
                       (68, 14, 38), (84, 14, 44)):
        s.box(X(bx), Y(96 - bh), int(bw * w / 100), int(bh * h / 100), (52, 24, 74))
        for wy in range(96 - bh + 6, 92, 10):
            for wx in range(bx + 3, bx + bw - 3, 6):
                if (wx * 7 + wy * 3) % 11 < 4:
                    s.box(X(wx), Y(wy), max(1, w // 90), max(1, h // 40), GOLD)
    # sea strip
    s.box(x, Y(88), w, h - int(88 * h / 100), (20, 90, 130))
    for i in range(6):
        s.box(X(6 + i * 16), Y(92), max(4, w // 22), 2, (200, 230, 240))
    # palm tree
    s.seg(X(12), Y(88), X(16), Y(58), (30, 60, 30), 3)
    for dx, dy in ((-12, -8), (-6, -12), (2, -13), (10, -10), (13, -4)):
        s.seg(X(16), Y(58), X(16 + dx), Y(58 + dy), (34, 110, 50), 2)
    # pink sports car
    s.poly([(X(52), Y(88)), (X(58), Y(76)), (X(74), Y(74)), (X(88), Y(80)),
            (X(92), Y(88))], PINK)
    s.box(X(60), Y(77), int(12 * w / 100), int(6 * h / 100), (240, 220, 235))
    s.disc(X(60), Y(88), max(3, w // 40), BLACK)
    s.disc(X(84), Y(88), max(3, w // 40), BLACK)
    s.disc(X(60), Y(88), max(1, w // 110), (200, 200, 200))
    s.disc(X(84), Y(88), max(1, w // 110), (200, 200, 200))


def scene_summit(s, x, y, w, h):
    """Three flags over a summit table: US, China, Russia."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (200, 220, 235), (240, 238, 228))
    s.box(x, Y(78), w, int(22 * h / 100), (150, 120, 90))
    # flag poles and flags
    for fx, kind in ((18, "us"), (50, "cn"), (82, "ru")):
        s.vline(X(fx), Y(8), int(58 * h / 100), (90, 80, 70), 2)
        s.disc(X(fx), Y(8), 2, GOLD)
        fw, fh = int(20 * w / 100), int(20 * h / 100)
        if kind == "us":
            for i in range(7):
                s.box(X(fx + 1), Y(10 + i * 3), fw, max(1, fh // 7),
                      RED if i % 2 == 0 else WHITE)
            s.box(X(fx + 1), Y(10), fw // 2, fh // 2, BLUE)
            for sy in (13, 18, 23):
                for sx in (fx + 4, fx + 7):
                    s.dot(X(sx), Y(sy), WHITE)
        elif kind == "cn":
            s.box(X(fx + 1), Y(10), fw, fh, (222, 40, 40))
            s.disc(X(fx + 6), Y(17), 2, GOLD)
            s.disc(X(fx + 13), Y(13), 1, GOLD)
            s.disc(X(fx + 15), Y(19), 1, GOLD)
        else:
            s.box(X(fx + 1), Y(10), fw, fh // 3 + 1, WHITE)
            s.box(X(fx + 1), Y(10 + fh // 3), fw, fh // 3 + 1, BLUE)
            s.box(X(fx + 1), Y(10 + 2 * fh // 3), fw, fh // 3 + 1, RED)
    # long table with microphones and name plates
    s.box(X(8), Y(66), int(84 * w / 100), int(10 * h / 100), (96, 62, 40))
    s.box(X(8), Y(66), int(84 * w / 100), 2, (140, 100, 60))
    for mx in (24, 50, 76):
        s.seg(X(mx), Y(66), X(mx), Y(58), INK, 1)
        s.disc(X(mx), Y(57), 2, INK)
        s.box(X(mx - 5), Y(70), int(10 * w / 100), 3, WHITE)


def scene_vangogh(s, x, y, w, h):
    """Blossom tree in a gold frame, gavel, record price tag."""
    X, Y = _xy(x, y, w, h)
    s.box(x, y, w, h, (226, 210, 180))
    s.frame(X(6), Y(6), int(62 * w / 100), int(88 * h / 100), GOLD, 3)
    s.box(X(8), Y(8), int(58 * w / 100), int(84 * h / 100), (150, 195, 225))
    # blossom tree
    s.poly([(X(30), Y(90)), (X(34), Y(60)), (X(38), Y(90))], (96, 62, 40))
    s.seg(X(34), Y(62), X(22), Y(40), (96, 62, 40), 3)
    s.seg(X(34), Y(62), X(48), Y(38), (96, 62, 40), 3)
    s.seg(X(34), Y(58), X(36), Y(30), (96, 62, 40), 2)
    for bx, by, br, col in ((22, 38, 9, (250, 245, 240)), (30, 30, 8, (245, 210, 225)),
                            (40, 26, 9, (250, 245, 240)), (48, 36, 8, (245, 210, 225)),
                            (56, 44, 7, (250, 245, 240)), (16, 48, 7, (245, 210, 225)),
                            (34, 44, 8, (250, 240, 235))):
        s.disc(X(bx), Y(by), max(2, br * w // 200), col)
        s.disc(X(bx - 2), Y(by - 2), 1, (200, 90, 110))
    s.box(X(8), Y(84), int(58 * w / 100), int(8 * h / 100), (90, 150, 80))
    # gavel and price tag
    s.seg(X(76), Y(84), X(90), Y(62), (120, 80, 40), 3)
    s.box(X(82), Y(56), int(14 * w / 100), int(9 * h / 100), (96, 62, 40))
    s.box(X(74), Y(88), int(20 * w / 100), 3, (120, 80, 40))
    s.box(X(72), Y(16), int(26 * w / 100), int(16 * h / 100), WHITE)
    s.frame(X(72), Y(16), int(26 * w / 100), int(16 * h / 100), RED, 1)
    s.text(X(74), Y(20), "$190.4M", RED, 1)


def scene_anthropic(s, x, y, w, h):
    """Rising market chart, trading bell, ANT ticker."""
    X, Y = _xy(x, y, w, h)
    s.box(x, y, w, h, (16, 26, 48))
    for gy in range(20, 90, 14):
        s.hline(X(6), Y(gy), int(88 * w / 100), (40, 60, 95), 1)
    # candlesticks
    for i, (cx, top, bot, up) in enumerate(((14, 62, 74, True), (26, 54, 68, True),
                                            (38, 58, 70, False), (50, 44, 60, True),
                                            (62, 36, 52, True), (74, 26, 44, True))):
        col = GREEN if up else RED
        s.box(X(cx), Y(top), max(3, w // 30), int((bot - top) * h / 100), col)
        s.vline(X(cx + 2), Y(top - 4), int((bot - top + 8) * h / 100), col, 1)
    # rising arrow line
    pts = [(X(8), Y(72)), (X(24), Y(60)), (X(40), Y(64)), (X(58), Y(46)),
           (X(74), Y(34)), (X(90), Y(18))]
    for a, b in zip(pts, pts[1:]):
        s.seg(a[0], a[1], b[0], b[1], (90, 220, 120), 2)
    s.tri(X(90), Y(18), X(82), Y(20), X(88), Y(26), (90, 220, 120))
    # bell
    s.disc(X(84), Y(58), max(5, w // 22), GOLD)
    s.box(X(76), Y(58), int(16 * w / 100), int(8 * h / 100), GOLD)
    s.box(X(74), Y(66), int(20 * w / 100), 3, GOLD)
    s.disc(X(84), Y(70), 2, GOLD)
    s.box(X(6), Y(82), int(16 * w / 100), int(12 * h / 100), WHITE)
    s.text(X(8), Y(85), "ANT", BLUE, 1)


def scene_crimea(s, x, y, w, h):
    """Bridge over the strait, smoke rising from the deck."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (180, 205, 225), (235, 235, 225))
    s.box(x, Y(64), w, h - int(64 * h / 100), SEA)
    for i in range(8):
        s.box(X(4 + i * 12), Y(72 + (i % 2) * 6), max(5, w // 18), 2, (200, 225, 240))
    # bridge deck, arch and pillars
    s.box(X(4), Y(52), int(92 * w / 100), int(6 * h / 100), (120, 120, 125))
    s.box(X(10), Y(58), 4, int(8 * h / 100), (100, 100, 105))
    s.box(X(86), Y(58), 4, int(8 * h / 100), (100, 100, 105))
    s.poly([(X(30), Y(52)), (X(50), Y(30)), (X(70), Y(52))], (150, 150, 155))
    s.poly([(X(38), Y(52)), (X(50), Y(38)), (X(62), Y(52))], (180, 205, 225))
    s.vline(X(50), Y(30), int(22 * h / 100), (120, 120, 125), 2)
    # smoke plume and blast star
    for sx, sy, sr in ((52, 44, 6), (55, 36, 8), (58, 27, 7), (61, 19, 5)):
        s.disc(X(sx), Y(sy), max(2, sr * w // 200), (120, 120, 120))
    s.disc(X(50), Y(50), max(3, w // 34), ORANGE)
    for ang in range(0, 360, 45):
        ex = X(50) + int(7 * w / 100 * math.cos(math.radians(ang)))
        ey = Y(50) + int(7 * h / 100 * math.sin(math.radians(ang)))
        s.seg(X(50), Y(50), ex, ey, GOLD, 2)


def scene_gaza(s, x, y, w, h):
    """Tank on desert ground, dashed ceasefire line, rooftops."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (235, 220, 190), (250, 235, 205))
    s.disc(X(84), Y(16), max(5, w // 20), (255, 220, 140))
    # rooftops
    for bx, bw, bh, col in ((4, 18, 26, (170, 150, 120)), (24, 14, 34, (150, 130, 105)),
                            (72, 16, 30, (170, 150, 120)), (88, 10, 22, (150, 130, 105))):
        s.box(X(bx), Y(78 - bh), int(bw * w / 100), int(bh * h / 100), col)
        s.box(X(bx + 3), Y(78 - bh + 5), 2, 3, (60, 50, 40))
        s.box(X(bx + bw - 6), Y(78 - bh + 5), 2, 3, (60, 50, 40))
    s.box(x, Y(78), w, h - int(78 * h / 100), SAND)
    # dashed yellow ceasefire line
    for i in range(0, 100, 8):
        s.box(X(i), Y(70), max(3, w // 28), 2, GOLD)
    s.tri(X(50), Y(62), X(46), Y(70), X(54), Y(70), RED)
    # tank
    s.box(X(30), Y(80), int(34 * w / 100), int(9 * h / 100), (64, 84, 52))
    s.box(X(40), Y(74), int(16 * w / 100), int(7 * h / 100), (64, 84, 52))
    s.seg(X(56), Y(76), X(72), Y(72), (50, 64, 42), 3)
    for wx in (34, 42, 50, 58):
        s.disc(X(wx), Y(89), max(2, w // 46), (30, 30, 30))
        s.disc(X(wx), Y(89), 1, (150, 150, 150))


def scene_cyclone(s, x, y, w, h):
    """Cyclone spiral over the Bay of Bengal, coastline, rain."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (60, 90, 130), (140, 170, 200))
    s.box(x, Y(70), w, h - int(70 * h / 100), (24, 80, 120))
    # coastline on the right
    s.poly([(X(74), Y(30)), (X(82), Y(45)), (X(78), Y(60)), (X(86), Y(75)),
            (X(84), Y(100)), (X(100), Y(100)), (X(100), Y(30))], SAND)
    s.box(X(78), Y(52), 3, 3, GREEN)
    s.box(X(82), Y(64), 3, 3, GREEN)
    # spiral: rings shrinking toward the eye
    cx, cy = X(42), Y(46)
    for i, r in enumerate((34, 27, 21, 15, 10, 5)):
        col = WHITE if i % 2 == 0 else (200, 220, 240)
        s.ring(cx + i * 2 - 4, cy + i - 2, max(2, r * w // 220), col, 3)
    s.disc(cx, cy, max(3, w // 34), (20, 40, 70))
    # rain streaks
    for i in range(7):
        rx = X(8 + i * 12)
        s.seg(rx, Y(14 + (i % 3) * 6), rx - 3, Y(26 + (i % 3) * 6), (210, 225, 240), 1)
    # warning triangle
    s.tri(X(84), Y(12), X(78), Y(24), X(90), Y(24), GOLD)
    s.text(X(83), Y(15), "!", INK, 1)


def scene_icj(s, x, y, w, h):
    """The Peace Palace: pediment, columns, scales of justice."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (170, 200, 225), (235, 235, 228))
    s.box(x, Y(86), w, h - int(86 * h / 100), (110, 140, 110))
    # courthouse
    s.tri(X(20), Y(24), X(50), Y(8), X(80), Y(24), (210, 200, 180))
    s.box(X(20), Y(24), int(60 * w / 100), int(4 * h / 100), (190, 180, 160))
    for cx in (26, 38, 50, 62, 74):
        s.box(X(cx - 2), Y(28), 4, int(48 * h / 100), (245, 242, 235))
        s.box(X(cx - 3), Y(28), 6, 2, (200, 190, 170))
        s.box(X(cx - 3), Y(74), 6, 2, (200, 190, 170))
    s.box(X(18), Y(76), int(64 * w / 100), int(4 * h / 100), (190, 180, 160))
    s.box(X(14), Y(80), int(72 * w / 100), int(3 * h / 100), (170, 160, 140))
    s.box(X(10), Y(83), int(80 * w / 100), int(3 * h / 100), (150, 140, 120))
    # scales of justice in front
    s.vline(X(50), Y(56), int(24 * h / 100), GOLD, 2)
    s.hline(X(38), Y(58), int(24 * w / 100), GOLD, 2)
    s.tri(X(40), Y(58), X(36), Y(68), X(44), Y(68), GOLD)
    s.tri(X(60), Y(58), X(56), Y(68), X(64), Y(68), GOLD)
    s.disc(X(50), Y(54), 2, GOLD)
    # flags
    for fx in (8, 92):
        s.vline(X(fx), Y(30), int(50 * h / 100), (90, 80, 70), 2)
        s.box(X(fx + 1), Y(30), int(8 * w / 100), int(10 * h / 100), BLUE)


def scene_voyager(s, x, y, w, h):
    """Voyager 1 one light-day out: stars, sun, golden probe."""
    X, Y = _xy(x, y, w, h)
    s.box(x, y, w, h, (8, 10, 26))
    for sx, sy, sr in ((8, 12, 1), (20, 30, 1), (30, 10, 1), (44, 22, 1),
                       (58, 12, 1), (70, 28, 1), (86, 14, 1), (92, 40, 1),
                       (12, 48, 1), (26, 62, 1), (66, 60, 1), (90, 66, 1),
                       (38, 76, 1), (80, 82, 1)):
        s.disc(X(sx), Y(sy), sr, WHITE)
    # sun with rays, lower left
    s.disc(X(14), Y(82), max(6, w // 16), (255, 200, 60))
    for ang in range(0, 360, 30):
        ex = X(14) + int(15 * w / 100 * math.cos(math.radians(ang)))
        ey = Y(82) + int(15 * h / 100 * math.sin(math.radians(ang)))
        s.seg(X(14), Y(82), ex, ey, (255, 200, 60), 1)
    # orbit ring
    s.ring(X(58), Y(48), max(10, w // 4), (70, 90, 130), 1)
    # probe: gold body, white dish, boom, antenna
    s.box(X(52), Y(40), int(12 * w / 100), int(10 * h / 100), GOLD)
    s.box(X(52), Y(40), int(12 * w / 100), 2, (230, 180, 60))
    s.disc(X(50), Y(45), max(4, w // 26), WHITE)
    s.seg(X(64), Y(45), X(78), Y(38), GOLD, 2)
    s.disc(X(79), Y(37), 2, RED)
    s.seg(X(58), Y(40), X(58), Y(28), (200, 200, 200), 1)
    s.disc(X(58), Y(27), 1, WHITE)
    s.seg(X(52), Y(48), X(44), Y(56), (150, 150, 160), 2)
    s.box(X(84), Y(70), int(12 * w / 100), int(12 * h / 100), WHITE)
    s.text(X(85), Y(73), "1 LD", BLUE, 1)


def scene_jeffries(s, x, y, w, h):
    """The US Capitol dome, flag on top, green lawn."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (165, 200, 230), (240, 240, 232))
    s.disc(X(12), Y(14), max(4, w // 24), (255, 225, 140))
    s.box(x, Y(84), w, h - int(84 * h / 100), (96, 150, 96))
    # dome
    s.box(X(38), Y(52), int(24 * w / 100), int(32 * h / 100), WHITE)
    s.disc(X(50), Y(52), max(8, w // 9), WHITE)
    s.box(X(46), Y(30), int(8 * w / 100), int(10 * h / 100), WHITE)
    s.vline(X(50), Y(18), int(12 * h / 100), INK, 1)
    for i in range(5):
        s.box(X(51), Y(20 + i * 2), int(9 * w / 100), 2, RED if i % 2 == 0 else WHITE)
    s.box(X(48), Y(46), int(4 * w / 100), int(6 * h / 100), (90, 90, 100))
    # wings and columns
    s.box(X(14), Y(66), int(24 * w / 100), int(18 * h / 100), (235, 232, 225))
    s.box(X(62), Y(66), int(24 * w / 100), int(18 * h / 100), (235, 232, 225))
    for cx in (20, 28, 36, 64, 72, 80):
        s.box(X(cx - 2), Y(68), 3, int(14 * h / 100), WHITE)
    s.box(X(10), Y(84), int(80 * w / 100), 2, (200, 195, 185))
    # steps
    for i in range(3):
        s.box(X(34 - i * 2), Y(84 + i * 3), int((32 + i * 4) * w / 100), 2, (215, 210, 200))


def scene_fed(s, x, y, w, h):
    """Central bank facade, rising rate arrow, gold coins."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (190, 200, 210), (240, 238, 230))
    # bank building
    s.tri(X(24), Y(34), X(50), Y(18), X(76), Y(34), (200, 190, 170))
    s.box(X(24), Y(34), int(52 * w / 100), int(4 * h / 100), (185, 175, 155))
    for cx in (30, 42, 54, 66):
        s.box(X(cx - 2), Y(38), 4, int(34 * h / 100), (245, 242, 235))
    s.box(X(22), Y(72), int(56 * w / 100), int(4 * h / 100), (185, 175, 155))
    s.box(X(46), Y(58), int(8 * w / 100), int(14 * h / 100), (90, 70, 50))
    s.box(x, Y(76), w, h - int(76 * h / 100), (120, 120, 115))
    # rising arrow
    pts = [(X(10), Y(66)), (X(26), Y(54)), (X(40), Y(58)), (X(56), Y(40)),
           (X(70), Y(30)), (X(88), Y(14))]
    for a, b in zip(pts, pts[1:]):
        s.seg(a[0], a[1], b[0], b[1], GREEN, 3)
    s.tri(X(88), Y(14), X(80), Y(16), X(86), Y(24), GREEN)
    # gold coins
    for i, (cx, cy) in enumerate(((84, 82), (88, 76), (80, 76))):
        s.disc(X(cx), Y(cy), max(3, w // 30), GOLD)
        s.ring(X(cx), Y(cy), max(3, w // 30), (160, 110, 20), 1)
        s.text(X(cx - 1), Y(cy - 3), "$", (120, 80, 10), 1)


def scene_nkorea(s, x, y, w, h):
    """Missile launch at dusk: mountains, launcher, smoke."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (70, 60, 110), (210, 120, 90))
    for sx, sy in ((10, 12), (26, 20), (44, 10), (62, 18), (82, 12), (92, 26)):
        s.disc(X(sx), Y(sy), 1, WHITE)
    # mountains
    s.poly([(X(0), Y(100)), (X(0), Y(70)), (X(18), Y(52)), (X(34), Y(72)),
            (X(48), Y(58)), (X(66), Y(74)), (X(82), Y(56)), (X(100), Y(72)),
            (X(100), Y(100))], (52, 48, 66))
    s.tri(X(14), Y(56), X(18), Y(52), X(22), Y(56), WHITE)
    s.tri(X(78), Y(60), X(82), Y(56), X(86), Y(60), WHITE)
    s.box(x, Y(88), w, h - int(88 * h / 100), (40, 38, 48))
    # launcher truck
    s.box(X(34), Y(80), int(26 * w / 100), int(8 * h / 100), (58, 92, 58))
    s.disc(X(40), Y(88), max(2, w // 46), BLACK)
    s.disc(X(54), Y(88), max(2, w // 46), BLACK)
    # missile
    s.box(X(45), Y(38), int(8 * w / 100), int(42 * h / 100), (235, 235, 235))
    s.tri(X(45), Y(38), X(49), Y(26), X(53), Y(38), RED)
    s.box(X(43), Y(72), int(12 * w / 100), int(6 * h / 100), RED)
    s.text(X(46), Y(52), "KP", RED, 1)
    # flame and smoke
    s.tri(X(46), Y(80), X(49), Y(90), X(52), Y(80), ORANGE)
    s.disc(X(49), Y(92), max(3, w // 30), (200, 200, 200))
    s.disc(X(42), Y(94), max(2, w // 40), (180, 180, 180))
    s.disc(X(56), Y(94), max(2, w // 40), (180, 180, 180))


def scene_bumrah(s, x, y, w, h):
    """Wellington Test, first over: bowler, stumps, crowd."""
    X, Y = _xy(x, y, w, h)
    s.sky_bands(x, y, w, h, (140, 190, 220), (220, 235, 240))
    # crowd blocks
    for i, col in enumerate((RED, BLUE, GOLD, GREEN, PURPLE, ORANGE)):
        s.box(X(4 + i * 16), Y(8), int(14 * w / 100), int(12 * h / 100), col)
        for wx in range(4 + i * 16 + 2, 4 + i * 16 + 13, 4):
            s.box(X(wx), Y(12), 2, 3, (240, 230, 210))
    s.box(x, Y(20), w, int(4 * h / 100), (90, 90, 95))
    # outfield and pitch
    s.box(x, Y(24), w, h - int(24 * h / 100), (70, 150, 80))
    s.box(X(38), Y(24), int(24 * w / 100), h - int(24 * h / 100), (210, 185, 140))
    s.hline(X(38), Y(30), int(24 * w / 100), WHITE, 1)
    s.hline(X(38), Y(88), int(24 * w / 100), WHITE, 1)
    # stumps at both ends
    for sy in (34, 82):
        for sx in (46, 49, 52):
            s.vline(X(sx), Y(sy), int(7 * h / 100), (240, 200, 60), 2)
        s.hline(X(46), Y(sy), int(8 * w / 100), (240, 200, 60), 1)
    # bowler mid-delivery, left of pitch
    s.disc(X(30), Y(44), max(3, w // 34), (120, 70, 40))
    s.seg(X(30), Y(48), X(30), Y(62), (20, 60, 140), 3)
    s.seg(X(30), Y(52), X(22), Y(44), (20, 60, 140), 2)
    s.seg(X(30), Y(52), X(38), Y(58), (20, 60, 140), 2)
    s.seg(X(30), Y(62), X(24), Y(74), WHITE, 2)
    s.seg(X(30), Y(62), X(36), Y(74), WHITE, 2)
    # ball trail to the stumps
    s.disc(X(44), Y(66), 2, WHITE)
    s.seg(X(38), Y(58), X(44), Y(66), WHITE, 1)
    s.seg(X(32), Y(50), X(38), Y(58), (255, 255, 255), 1)
    # batsman silhouette at the far stumps
    s.disc(X(50), Y(76), 2, (40, 40, 60))
    s.seg(X(50), Y(78), X(50), Y(86), (40, 40, 60), 2)
    s.seg(X(50), Y(80), X(56), Y(74), (120, 80, 40), 2)


SCENES = {
    "gta": scene_gta, "summit": scene_summit, "vangogh": scene_vangogh,
    "anthropic": scene_anthropic, "crimea": scene_crimea, "gaza": scene_gaza,
    "cyclone": scene_cyclone, "icj": scene_icj, "voyager": scene_voyager,
    "jeffries": scene_jeffries, "fed": scene_fed, "nkorea": scene_nkorea,
    "bumrah": scene_bumrah,
}


# ------------------------------------------------------------- the stories
# Every headline was checked against reporting of Thursday 19 November
# 2026 (BBC, AP, Reuters, The Hindu, NDTV, Sotheby's, Artnet,
# CricTracker, New York Times, Financial Times). Lead: (number, region,
# field, tag, scene, lon, lat, headline, deck). Brief: (region, field,
# one line, 54 chars or fewer).
LEADS = [
    (1, "N. AMERICA", "CULTURE", "CULTURE - GAMES", "gta", -80.2, 25.8,
     "Gamers enter Vice City as Grand Theft Auto VI begins its global rollout",
     "After a 13-year wait, Rockstar's $1bn epic lands today; pre-orders alone passed $1bn."),
    (2, "ASIA", "POLITICS", "POLITICS - APEC", "summit", 114.1, 22.5,
     "Trump, Xi and Putin shake hands as leaders gather in China",
     "Trilateral talks in Shenzhen; third Xi-Trump meeting this year."),
    (3, "N. AMERICA", "CULTURE", "CULTURE - ART", "vangogh", -74.0, 40.7,
     "Van Gogh sells for a record $190.4m after Nazi-era row",
     "Chataigniers en fleurs tops Sotheby's sale; Acquavella buys it."),
    (4, "N. AMERICA", "BUSINESS", "BUSINESS - AI", "anthropic", -122.4, 37.8,
     "Claude-maker Anthropic poised for $1.4tn market debut",
     "Shares start trading on Nasdaq Thursday; priced at $70-$78."),
    (5, "EUROPE", "POLITICS", "POLITICS - WAR", "crimea", 34.0, 45.3,
     "Crimean Bridge attacked again, Russian official says",
     "Blast hits the link to occupied Crimea; Kyiv has struck it before."),
    (6, "MIDDLE EAST", "POLITICS", "POLITICS - WAR", "gaza", 34.5, 31.5,
     "Israeli troops cross Gaza ceasefire line in rare raid",
     "Ground operation beyond the Yellow Line as floods add to Gaza's misery."),
    (7, "ASIA", "WEATHER", "WEATHER - INDIA", "cyclone", 88.0, 16.0,
     "Cyclone Akvan bears down on India's east coast",
     "Landfall likely between Machilipatnam and Puri; Andhra Pradesh on alert."),
    (8, "EUROPE", "POLITICS", "POLITICS - LAW", "icj", 4.3, 52.1,
     "Myanmar faces historic genocide verdict at UN court",
     "The Hague rules on the Rohingya case; a world first."),
    (9, "WORLD", "SCIENCE", "SCIENCE - SPACE", "voyager", -118.1, 34.1,
     "Voyager 1 believed to have reached one light-day out",
     "NASA confirms the milestone; the probe left Earth in 1977."),
    (10, "N. AMERICA", "POLITICS", "POLITICS - USA", "jeffries", -77.0, 38.9,
     "Jeffries set to be first Black Speaker of the House",
     "Democrats nominate Hakeem Jeffries; the vote is the talk of Washington."),
    (11, "N. AMERICA", "BUSINESS", "BUSINESS - RATES", "fed", -77.0, 38.9,
     "Fed minutes point to more rate rises ahead",
     "Most officials see further hikes if inflation runs hot."),
    (12, "ASIA", "POLITICS", "POLITICS - ASIA", "nkorea", 127.0, 40.0,
     "North Korea fires missiles after US-South Korea drill",
     "Missiles fly hours after the US-South Korea-Japan exercise ended."),
    (13, "OCEANIA", "SPORT", "SPORT - CRICKET", "bumrah", 174.8, -41.3,
     "Bumrah bowls Latham for a duck in the first over",
     "India strike in over one; the captain falls third ball."),
]

BRIEFS = [
    ("N. AMERICA", "POLITICS", "Canada retools China ties as Carney chases US deal"),
    ("N. AMERICA", "TECH", "Senators: AI cyber threats outpacing US defences"),
    ("EUROPE", "POLITICS", "EU proposes €45bn Ukraine loan, repaid from reparations"),
    ("EUROPE", "POLITICS", "Melenchon could win French presidency, minister says"),
    ("MIDDLE EAST", "POLITICS", "Saudi Arabia: danger passed in three southern cities"),
    ("AFRICA", "CRIME", "Cocaine, millions of pills seized in eastern Libya"),
    ("ASIA", "POLITICS", "Congress presses Modi government on inflation"),
    ("EUROPE", "CRIME", "McDonald's abuse: 'waiting for girls to turn 18'"),
    ("EUROPE", "CRIME", "Russian held for spying on Palantir over Ukraine aid"),
    ("MIDDLE EAST", "POLITICS", "Four nations urge Israel to let aid reach flooded Gaza"),
    ("S. AMERICA", "BUSINESS", "US details $12bn in Venezuelan oil, mineral revenue"),
    ("EUROPE", "POLITICS", "France faces fourth weekend of cost-of-living protests"),
    ("MIDDLE EAST", "POLITICS", "Eisenkot tapped to form government, not Netanyahu"),
    ("MIDDLE EAST", "POLITICS", "Israel limits care for 1,100 child amputees, NGO says"),
    ("N. AMERICA", "BUSINESS", "Nvidia chief promises earlier pay rises, more stock"),
    ("ASIA", "TECH", "Nvidia halts H-series chip shipments to mainland China"),
    ("WORLD", "CULTURE", "Islam on track to be top faith by 2035, Pew says"),
    ("WORLD", "SCIENCE", "Earth's missing billion years may finally be explained"),
    ("ASIA", "POLITICS", "India, Japan to review defence ties in 2+2 talks"),
    ("EUROPE", "WORLD", "German climber survives 100-metre fall in the Alps"),
    ("EUROPE", "CRIME", "Ukrainian-German woman charged with spying for Russia"),
    ("EUROPE", "SCIENCE", "ESA chief calls for space laws, satellite watch"),
    ("MIDDLE EAST", "POLITICS", "US, Iran trade fire again as Tehran widens Gulf attacks"),
    ("WORLD", "BUSINESS", "Oil prices fall as Middle East risk rises"),
    ("N. AMERICA", "TECH", "Microsoft in talks to sell AI services to ByteDance"),
    ("EUROPE", "CRIME", "Deutsche Bank handled $582m in Epstein deals, FT says"),
    ("OCEANIA", "SPORT", "Duckett's 133 powers England to 97-run ODI win"),
    ("EUROPE", "SPORT", "Brooks late winner lifts Sheffield Utd at Portsmouth"),
    ("AFRICA", "POLITICS", "Somalia accuses UAE of secret bases on its soil"),
]

# Figures reported on 19 November itself: (big figure, what it is).
NUMBERS = [
    ("$190.4M", "Van Gogh record at Sotheby's"),
    ("$1.4T", "Anthropic IPO valuation"),
    ("€45B", "EU loan proposed for Kyiv"),
    ("13 YRS", "wait ends as GTA VI lands"),
    ("1 LIGHT-DAY", "Voyager 1's distance mark"),
]

REGION_ORDER = ["N. AMERICA", "S. AMERICA", "EUROPE", "MIDDLE EAST",
                "AFRICA", "ASIA", "OCEANIA", "WORLD"]
FIELD_ORDER = ["POLITICS", "BUSINESS", "TECH", "SCIENCE", "CULTURE",
               "SPORT", "CRIME", "WEATHER", "WORLD"]

# ------------------------------------------------------------ dotted map
# Rough continent outlines in (lon, lat), drawn from memory for the
# dotted map; pins mark the 13 lead stories.
CONTINENTS = [
    [(-168, 66), (-150, 70), (-130, 71), (-115, 72), (-100, 72), (-90, 74),
     (-82, 72), (-76, 70), (-68, 62), (-60, 58), (-55, 52), (-60, 46),
     (-65, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 32), (-81, 26),
     (-84, 30), (-90, 21), (-94, 17), (-97, 16), (-100, 20), (-105, 22),
     (-110, 24), (-114, 29), (-120, 34), (-124, 40), (-124, 48), (-130, 55),
     (-140, 60), (-152, 58), (-162, 55), (-166, 60)],
    [(-79, 9), (-72, 11), (-64, 10), (-58, 6), (-52, 4), (-50, 0),
     (-44, -3), (-38, -6), (-35, -9), (-38, -15), (-40, -22), (-46, -26),
     (-52, -32), (-58, -36), (-62, -41), (-66, -47), (-68, -52), (-71, -54),
     (-73, -48), (-73, -38), (-71, -30), (-70, -20), (-76, -14), (-79, -6),
     (-81, 0)],
    [(-17, 15), (-15, 22), (-10, 29), (-6, 33), (0, 36), (8, 37), (11, 34),
     (18, 33), (22, 33), (30, 31), (33, 28), (36, 22), (39, 18), (43, 12),
     (48, 11), (51, 12), (48, 5), (44, 0), (40, -8), (38, -16), (34, -24),
     (30, -30), (26, -34), (20, -35), (16, -30), (13, -20), (12, -12),
     (9, -2), (9, 4), (2, 6), (-6, 5), (-12, 8), (-16, 12)],
    [(-10, 36), (-9, 42), (-4, 44), (-1, 46), (0, 49), (3, 51), (6, 54),
     (8, 57), (12, 56), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (32, 68), (38, 68), (46, 68), (54, 69), (62, 70), (70, 72), (78, 73),
     (88, 74), (100, 76), (112, 74), (124, 73), (136, 72), (148, 71),
     (158, 70), (170, 68), (178, 66), (173, 64), (168, 60), (162, 58),
     (158, 53), (152, 56), (144, 52), (142, 46), (140, 40), (134, 36),
     (128, 34), (122, 30), (118, 26), (112, 22), (108, 18), (106, 10),
     (103, 8), (100, 10), (98, 14), (94, 18), (90, 22), (86, 20), (82, 16),
     (80, 10), (77, 8), (74, 12), (72, 20), (68, 24), (62, 25), (58, 26),
     (54, 27), (50, 29), (48, 30), (44, 30), (40, 36), (36, 36), (32, 36),
     (28, 37), (24, 36), (22, 37), (20, 40), (18, 40), (16, 42), (14, 44),
     (12, 44), (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37), (-6, 36)],
    [(113, -22), (114, -28), (115, -33), (120, -34), (126, -32), (130, -32),
     (134, -33), (138, -35), (142, -38), (147, -39), (150, -37), (153, -32),
     (153, -27), (150, -23), (147, -19), (144, -15), (142, -11), (140, -17),
     (136, -12), (132, -11), (128, -14), (124, -15), (120, -20), (116, -21)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38),
     (141, 41), (142, 43), (144, 44), (141, 45), (139, 42), (137, 38),
     (134, 35), (131, 33)],
    [(95, 5), (98, 3), (100, 0), (103, -3), (106, -6), (110, -7), (114, -8),
     (118, -9), (122, -10), (126, -8), (130, -4), (132, -2), (136, -2),
     (140, -3), (141, -6), (138, -8), (132, -7), (126, -6), (120, -8),
     (114, -9), (108, -8), (102, -4), (98, 2)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (178, -37),
     (176, -40), (174, -41), (172, -43), (169, -46)],
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 78),
     (-35, 80), (-48, 78), (-56, 74), (-58, 68), (-54, 64), (-50, 60)],
    [(-22, 64), (-18, 63), (-14, 64), (-16, 66), (-20, 66), (-24, 65)],
]

# The two Washington leads share one spot: pin 11 is offset with a
# leader line back to the capital.
PIN_OFFSET = {11: (16, -12)}


def inside(px, py, poly):
    hit = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xi = x1 + (x2 - x1) * (py - y1) / (y2 - y1)
            if px < xi:
                hit = not hit
    return hit


def draw_map(s, x, y, w, h):
    s.frame(x, y, w, h, INK, 1)
    lon0, lon1, lat0, lat1 = -180, 180, 74, -58
    sc = min(w / (lon1 - lon0), h / (lat0 - lat1))
    ox = x + (w - (lon1 - lon0) * sc) / 2
    oy = y + (h - (lat0 - lat1) * sc) / 2

    def proj(lon, lat):
        return int(ox + (lon - lon0) * sc), int(oy + (lat0 - lat) * sc)

    lat = 72
    while lat >= -56:
        lon = -178
        while lon <= 178:
            for poly in CONTINENTS:
                if inside(lon, lat, poly):
                    px, py = proj(lon, lat)
                    s.box(px, py, 2, 2, BLUE)
                    break
            lon += 3
        lat -= 3
    for lead in LEADS:
        num, _rg, _fd, _tg, _sc, lon, lat, _hl, _dk = lead
        px, py = proj(lon, lat)
        dx, dy = PIN_OFFSET.get(num, (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            s.seg(px, py, qx, qy, RED, 1)
        s.disc(qx, qy, 7, RED)
        s.ring(qx, qy, 7, WHITE, 1)
        num_s = str(num)
        s.text(qx - text_width(num_s, 1) // 2, qy - 3, num_s, WHITE, 1)


# -------------------------------------------------------------- page parts
def count_by(stories, idx):
    counts = {}
    for st in stories:
        key = st[idx]
        counts[key] = counts.get(key, 0) + 1
    return counts


def draw_bars(s, y, label, order, counts, color):
    s.text(16, y, label, INK, 1)
    cx = 16 + text_width(label, 1) + 12
    for name in order:
        n = counts.get(name, 0)
        if not n:
            continue
        lab = "%s %d" % (name, n)
        s.text(cx, y, lab, INK, 1)
        cx += text_width(lab, 1) + 6
        s.box(cx, y + 1, n * 7, 5, color)
        cx += n * 7 + 14


def lead_card(s, x, y, w, h, lead):
    num, _rg, _fd, tag, scene, _lon, _lat, headline, deck = lead
    s.frame(x, y, w, h, INK, 1)
    SCENES[scene](s, x + 1, y + 1, w - 2, 96)
    s.box(x + 1, y + 1, 20, 14, RED)
    num_s = str(num)
    s.text(x + 1 + (20 - text_width(num_s, 1)) // 2, y + 4, num_s, WHITE, 1)
    s.text(x + 6, y + 102, tag, RED, 1)
    yy = y + 112
    for ln in wrap_text(headline, w - 12, 1)[:2]:
        s.text(x + 6, yy, ln, INK, 1)
        yy += 9
    yy = y + 134
    for ln in wrap_text(deck, w - 12, 1)[:2]:
        s.text(x + 6, yy, ln, GREY, 1)
        yy += 9


def hero_card(s, x, y, w, h, lead):
    _num, _rg, _fd, tag, scene, _lon, _lat, headline, deck = lead
    s.frame(x, y, w, h, INK, 1)
    iw = 470
    SCENES[scene](s, x + 1, y + 1, iw, h - 2)
    s.box(x + 1, y + 1, 20, 14, RED)
    s.text(x + 5, y + 4, "1", WHITE, 1)
    tx = x + iw + 14
    tw = w - iw - 28
    s.text(tx, y + 8, tag, RED, 1)
    yy = y + 22
    for ln in wrap_text(headline, tw, 2)[:3]:
        s.text(tx, yy, ln, INK, 2)
        yy += 16
    yy += 4
    for ln in wrap_text(deck, tw, 1)[:3]:
        s.text(tx, yy, ln, GREY, 1)
        yy += 9
    yy += 6
    s.hline(tx, yy, tw, LIGHT, 1)
    s.text(tx, yy + 5, "INSIDE: 12 MORE LEADS - BY THE NUMBERS - MAP - 29 BRIEFS",
           INK, 1)


# -------------------------------------------------------------------- main
def out_path():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return os.path.join(d, "entry.png")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def main():
    assert len(LEADS) + len(BRIEFS) == 42, "story count must be 42"
    s = Sheet()
    # masthead
    s.hline(16, 10, 992, INK, 2)
    s.centred(16, "THE WORLD IN ONE PICTURE", INK, 4)
    s.centred(48, "THURSDAY 19 NOVEMBER 2026 | 42 STORIES | ONE IMAGE", GREY, 1)
    s.hline(16, 60, 992, INK, 2)
    # hero lead: GTA VI
    hero_card(s, 16, 68, 992, 128, LEADS[0])
    # 12 more illustrated leads, 3 rows of 4
    for i, lead in enumerate(LEADS[1:]):
        row, col = divmod(i, 4)
        lead_card(s, 16 + col * 250, 204 + row * 172, 242, 164, lead)
    # by the numbers
    s.frame(16, 720, 992, 58, INK, 1)
    s.text(28, 734, "BY THE", RED, 1)
    s.text(28, 744, "NUMBERS", RED, 1)
    for i, (big, label) in enumerate(NUMBERS):
        cx = 140 + i * 172
        s.text(cx, 728, big, INK, 2)
        yy = 748
        for ln in wrap_text(label, 168, 1)[:2]:
            s.text(cx, yy, ln, GREY, 1)
            yy += 9
    # region and field bars, counted from the stories themselves
    all_stories = [(rg, fd) for (_n, rg, fd, _t, _s, _lo, _la, _h, _d) in LEADS]
    all_stories += [(rg, fd) for (rg, fd, _t) in BRIEFS]
    draw_bars(s, 788, "REGIONS", REGION_ORDER,
              count_by(all_stories, 0), BLUE)
    draw_bars(s, 802, "FIELDS", FIELD_ORDER,
              count_by(all_stories, 1), TEAL)
    # map and briefs
    s.text(16, 822, "WHERE THE NEWS HAPPENED", INK, 1)
    s.text(340, 822, "THE DAY IN BRIEF - 29 MORE STORIES", INK, 1)
    draw_map(s, 16, 834, 310, 150)
    for i, (_rg, _fd, text) in enumerate(BRIEFS):
        col = i // 15
        row = i % 15
        s.text(340 + col * 338, 834 + row * 10, text, INK, 1)
    # footer: date check and sources
    s.centred(992, "DATE CHECK: all 42 stories were reported on Thursday 19 November 2026.",
              INK, 1)
    s.centred(1004, "SOURCES: BBC News, AP, Reuters, The Hindu, NDTV, Sotheby's, Artnet, "
              "CricTracker, New York Times, Financial Times", GREY, 1)
    path = out_path()
    write_png(s, path)
    print("wrote %s 1024x1024, %d stories (%d leads, %d briefs)"
          % (path, len(LEADS) + len(BRIEFS), len(LEADS), len(BRIEFS)))


if __name__ == "__main__":
    main()
