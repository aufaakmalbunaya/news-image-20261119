#!/usr/bin/env python3
"""The World in One Picture -- Thursday 19 November 2026. Round 2.

Draws a 1024x1024 newspaper front page that sums up 19 November 2026
in a single image: 48 stories first reported that day, 13 of them as
illustrated lead cards with detailed flat-vector scenes, a
by-the-numbers strip, region and field count bars, a dotted world map
with numbered pins, 35 one-line briefs, and a date-check footer that
names the big 18 November stories left out on purpose.

Round 2 fixes round 1: headlines are drawn bold (every glyph struck
twice, one pixel apart) so the letters read at small sizes; the
Anthropic lead now says priced at $83, $81.3bn raised, the largest IPO
on record; the Van Gogh sale, the Jeffries nomination, the Fed minutes,
the EU loan, the Gaza raid, the Voyager crossing and Duckett's 133 are
out, because each was first reported on 18 November; the cricket lead
keeps Jasprit Bumrah's name and adds the lunch score.

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
CREAM = (244, 230, 200)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
DARK = (32, 32, 48)
LEAF = (58, 140, 70)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: seven rows of five characters, '#' on, '.' off.
# Drawn from scratch for this page. Bold text strikes every glyph
# twice, one pixel to the right, so the strokes read at small sizes.
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
    "+": ("     ", "     ", "  #  ", "#####", "  #  ", "     ", "     "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", "  #  ", " #   "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    ":": ("     ", " ##  ", "     ", "     ", "     ", " ##  ", "     "),
    ";": ("     ", " ##  ", "     ", "     ", " ##  ", "  #  ", " #   "),
    "<": ("   # ", "  #  ", " #   ", "#    ", " #   ", "  #  ", "   # "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    ">": (" #   ", "  #  ", "   # ", "    #", "   # ", "  #  ", " #   "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "@": (" ### ", "#   #", "# ###", "# # #", "# ###", "#    ", " ### "),
    "[": (" ### ", " #   ", " #   ", " #   ", " #   ", " #   ", " ### "),
    "]": (" ### ", "   # ", "   # ", "   # ", "   # ", "   # ", " ### "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
    "`": ("  #  ", "  #  ", "   # ", "     ", "     ", "     ", "     "),
    "{": ("  ## ", "  #  ", "  #  ", "##   ", "  #  ", "  #  ", "  ## "),
    "|": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "}": ("##   ", "  #  ", "  #  ", "   ##", "  #  ", "  #  ", "##   "),
    "~": ("     ", "     ", " ## #", "# ## ", "     ", "     ", "     "),
    "\u20ac": (" ### ", "#   #", "#####", "#    ", "#####", "#   #", " ### "),
}


def text_width(s, scale=1, bold=False):
    """Pixel width of s at the given scale; bold adds one pixel a glyph."""
    return len(s) * (5 * scale + scale) + (len(s) if bold else 0)


def wrap_text(s, max_w, scale=1, bold=False):
    """Greedy word wrap of s into lines no wider than max_w pixels."""
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale, bold) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- sheet
class Sheet:
    """A 1024x1024 RGB canvas with flat-vector drawing helpers."""

    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def box(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            i = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                self.px[i:i + 3] = bytes(c)
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
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.dot(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = math.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
                if abs(d - r) <= t / 2 + 0.4:
                    self.dot(xx, yy, c)

    def tri(self, x1, y1, x2, y2, x3, y3, c):
        lo_x, hi_x = min(x1, x2, x3), max(x1, x2, x3)
        lo_y, hi_y = min(y1, y2, y3), max(y1, y2, y3)
        d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if d == 0:
            return
        for yy in range(lo_y, hi_y + 1):
            for xx in range(lo_x, hi_x + 1):
                a = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / d
                b = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / d
                cc = 1 - a - b
                if a >= 0 and b >= 0 and cc >= 0:
                    self.dot(xx, yy, c)

    def poly(self, pts, c):
        lo_y, hi_y = min(p[1] for p in pts), max(p[1] for p in pts)
        for yy in range(lo_y, hi_y + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= yy < y2) or (y2 <= yy < y1):
                    xs.append(x1 + (x2 - x1) * (yy - y1) / (y2 - y1))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.dot(xx, yy, c)

    def seg(self, x1, y1, x2, y2, c, t=1):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(steps + 1):
            x = int(x1 + (x2 - x1) * i / steps)
            y = int(y1 + (y2 - y1) * i / steps)
            for dy in range(t):
                for dx in range(t):
                    self.dot(x + dx, y + dy, c)

    def glyph(self, x, y, ch, c, scale=1, bold=False):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        for r, row in enumerate(rows):
            for col, mark in enumerate(row):
                if mark == "#":
                    for dy in range(scale):
                        for dx in range(scale):
                            self.dot(x + col * scale + dx, y + r * scale + dy, c)
                            if bold:
                                self.dot(x + col * scale + dx + 1,
                                         y + r * scale + dy, c)

    def text(self, x, y, s, c, scale=1, bold=False):
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, c, scale, bold)
            cx += 5 * scale + scale + (1 if bold else 0)
        return cx

    def centred(self, y, s, c, scale=1, cx=None, bold=False):
        if cx is None:
            cx = self.w // 2
        self.text(cx - text_width(s, scale, bold) // 2, y, s, c, scale, bold)

    def sky_bands(self, x, y, w, h, top, bottom):
        for i in range(h):
            t = i / max(1, h - 1)
            c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
            self.box(x, y + i, w, 1, c)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(sheet, path):
    raw = b"".join(
        b"\x00" + bytes(sheet.px[y * sheet.w * 3:(y + 1) * sheet.w * 3])
        for y in range(sheet.h))
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", struct.pack(">IIBBBBB", sheet.w, sheet.h,
                                         8, 2, 0, 0, 0))
           + _chunk(b"IDAT", zlib.compress(raw, 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------------ lead scenes
# Each scene draws a detailed flat-vector picture inside (x, y, w, h).
def scene_gta(s, x, y, w, h):
    s.sky_bands(x, y, w, h, (90, 40, 110), (235, 120, 60))
    s.disc(x + w - 52, y + 26, 20, (255, 210, 90))
    s.ring(x + w - 52, y + 26, 23, (255, 230, 150), 2)
    for i, bh in enumerate((34, 52, 28, 44, 60, 36, 48)):
        bx = x + 8 + i * 32
        s.box(bx, y + h - 34 - bh, 26, bh, DARK)
        for wy in range(0, bh - 6, 9):
            for wx in (5, 15):
                s.box(bx + wx, y + h - 30 - bh + wy, 4, 5, GOLD)
    s.box(x, y + h - 34, w, 4, (20, 20, 40))
    s.box(x, y + h - 30, w, 30, (30, 30, 60))
    for dx in range(0, w, 26):
        s.box(x + dx, y + h - 16, 14, 3, WHITE)
    cx, cy = x + w // 2 - 40, y + h - 52
    s.poly([(cx, cy + 12), (cx + 12, cy), (cx + 78, cy), (cx + 90, cy + 12)],
           (255, 90, 160))
    s.box(cx + 6, cy + 12, 78, 9, (200, 30, 110))
    s.disc(cx + 18, cy + 23, 7, BLACK)
    s.disc(cx + 72, cy + 23, 7, BLACK)
    s.disc(cx + 18, cy + 23, 3, (180, 180, 180))
    s.disc(cx + 72, cy + 23, 3, (180, 180, 180))
    for px in (x + 14, x + w - 24):
        s.seg(px, y + h - 34, px + 4, y + h - 58, LEAF, 2)
        s.seg(px + 4, y + h - 58, px - 8, y + h - 52, LEAF, 2)
        s.seg(px + 4, y + h - 58, px + 16, y + h - 52, LEAF, 2)
    s.text(x + 24, y + 6, "VICE CITY", WHITE, 1, bold=True)


def scene_summit(s, x, y, w, h):
    s.box(x, y, w, h, (200, 220, 235))
    for i, bh in enumerate((30, 46, 38, 54, 34)):
        bx = x + 10 + i * 44
        s.box(bx, y + h - 40 - bh, 34, bh, (120, 140, 170))
        for wy in range(0, bh - 6, 8):
            for wx in (6, 18):
                s.box(bx + wx, y + h - 36 - bh + wy, 5, 4, (230, 240, 250))
    s.box(x, y + h - 40, w, 40, (150, 160, 150))
    s.box(x + 20, y + h - 34, w - 40, 6, (90, 60, 40))
    for i, flag in enumerate(("us", "cn", "ru")):
        fx = x + 30 + i * 70
        s.vline(fx, y + 8, 40, INK, 2)
        if flag == "us":
            s.box(fx + 2, y + 10, 34, 20, RED)
            s.box(fx + 2, y + 14, 34, 3, WHITE)
            s.box(fx + 2, y + 21, 34, 3, WHITE)
            s.box(fx + 2, y + 10, 14, 9, BLUE)
        elif flag == "cn":
            s.box(fx + 2, y + 10, 34, 20, RED)
            s.disc(fx + 12, y + 18, 3, GOLD)
            s.disc(fx + 24, y + 15, 2, GOLD)
            s.disc(fx + 24, y + 23, 2, GOLD)
        else:
            s.box(fx + 2, y + 10, 34, 7, WHITE)
            s.box(fx + 2, y + 17, 34, 6, BLUE)
            s.box(fx + 2, y + 23, 34, 7, RED)
    for i in range(3):
        px = x + 44 + i * 70
        s.disc(px, y + h - 52, 7, (60, 40, 30))
        s.box(px - 8, y + h - 46, 16, 12, (40, 60, 120))
    s.box(x + w // 2 - 46, y + h - 26, 92, 5, (90, 60, 40))
    s.text(x + 8, y + h - 18, "APEC - SHENZHEN", INK, 1, bold=True)


def scene_anthropic(s, x, y, w, h):
    s.box(x, y, w, h, (12, 20, 44))
    for gy in range(14, h - 8, 14):
        s.hline(x + 8, y + gy, w - 16, (40, 55, 90), 1)
    pts = [(x + 14, y + h - 18), (x + 46, y + h - 34), (x + 78, y + h - 26),
           (x + 110, y + h - 48), (x + 142, y + h - 40), (x + 174, y + h - 62),
           (x + 206, y + h - 70)]
    for i in range(len(pts) - 1):
        s.seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GREEN, 3)
    s.tri(pts[-1][0] - 2, pts[-1][1] + 6, pts[-1][0] + 12, pts[-1][1] + 2,
          pts[-1][0] - 2, pts[-1][1] - 4, GREEN)
    for i, (bx, by, bh) in enumerate(((24, 0, 12), (56, 0, 18), (88, 0, 10),
                                      (120, 0, 22), (152, 0, 14), (184, 0, 26))):
        s.box(x + bx, y + h - 18 - bh, 10, bh, GREEN if i % 2 == 0 else RED)
    s.disc(x + w - 34, y + h - 22, 12, GOLD)
    s.box(x + w - 38, y + h - 26, 8, 4, GOLD)
    s.text(x + 24, y + 6, "ANT  $83", GREEN, 1, bold=True)
    s.text(x + 10, y + 18, "RECORD $81.3BN IPO", WHITE, 1, bold=True)


def scene_crimea(s, x, y, w, h):
    s.sky_bands(x, y, w, h, (150, 200, 230), (220, 235, 245))
    s.box(x, y + h - 34, w, 34, SEA)
    for wx in range(0, w, 30):
        s.box(x + wx, y + h - 22, 16, 2, WHITE)
    s.box(x, y + 44, w, 8, (120, 120, 125))
    for px in range(10, w - 10, 34):
        s.box(x + px, y + 52, 6, h - 86, (90, 90, 95))
    s.tri(x + w // 2 - 46, y + 44, x + w // 2, y + 16, x + w // 2 + 46, y + 44,
          (140, 140, 145))
    gap = x + w // 2 - 12
    s.box(gap, y + 44, 24, 8, SEA)
    s.seg(gap, y + 52, gap - 8, y + 60, (90, 90, 95), 2)
    s.seg(gap + 24, y + 52, gap + 32, y + 60, (90, 90, 95), 2)
    ex, ey = x + w // 2, y + 34
    for dx, dy in ((-16, -8), (14, -12), (-10, 10), (16, 8), (0, -16)):
        s.seg(ex, ey, ex + dx, ey + dy, ORANGE, 3)
    s.disc(ex, ey, 7, GOLD)
    s.disc(ex - 18, ey - 14, 9, (120, 120, 120))
    s.disc(ex + 20, ey - 10, 7, (120, 120, 120))
    s.disc(ex + 26, ey - 18, 5, (140, 140, 140))
    s.box(x + 24, y + 6, 74, 12, RED)
    s.text(x + 26, y + 8, "3RD STRIKE", WHITE, 1, bold=True)


def scene_icj(s, x, y, w, h):
    s.box(x, y, w, h, (205, 225, 240))
    s.disc(x + w // 2, y + 16, 12, (255, 220, 120))
    s.tri(x + 40, y + 34, x + w - 40, y + 34, x + w // 2, y + 18, CREAM)
    s.box(x + 40, y + 34, w - 80, 6, (170, 150, 120))
    for i in range(5):
        cx = x + 52 + i * 34
        s.box(cx, y + 40, 10, 26, CREAM)
        s.box(cx - 2, y + 38, 14, 3, (170, 150, 120))
    s.box(x + 40, y + 66, w - 80, 5, (170, 150, 120))
    s.box(x + 30, y + 71, w - 60, 4, (150, 130, 100))
    s.box(x + 22, y + 75, w - 44, 4, (130, 110, 85))
    s.box(x, y + h - 10, w, 10, LEAF)
    cx, cy = x + w // 2, y + 52
    s.vline(cx, cy - 8, 16, GOLD, 2)
    s.seg(cx, cy - 8, cx - 12, cy - 2, GOLD, 2)
    s.seg(cx, cy - 8, cx + 12, cy - 2, GOLD, 2)
    s.tri(cx - 16, cy, cx - 8, cy, cx - 12, cy + 6, GOLD)
    s.tri(cx + 8, cy, cx + 16, cy, cx + 12, cy + 6, GOLD)
    s.text(x + 8, y + h - 22, "THE HAGUE", INK, 1, bold=True)


def scene_cyclone(s, x, y, w, h):
    s.box(x, y, w, h, (170, 205, 230))
    cx, cy = x + w // 2 - 10, y + h // 2 + 4
    for r in (30, 24, 18, 12):
        s.ring(cx, cy, r, WHITE, 3)
    s.disc(cx, cy, 6, DARK)
    s.seg(cx + 30, cy - 6, cx + 44, cy - 14, WHITE, 2)
    s.seg(cx - 30, cy + 8, cx - 46, cy + 16, WHITE, 2)
    s.poly([(x + w - 52, y + h), (x + w - 30, y + 34), (x + w - 8, y + 52),
            (x + w, y + h)], SAND)
    s.box(x + w - 46, y + 40, 12, 10, ORANGE)
    s.tri(x + w - 40, y + 30, x + w - 34, y + 40, x + w - 46, y + 40, ORANGE)
    for i in range(6):
        rx = x + 8 + i * 12
        s.seg(rx, y + 10 + (i % 2) * 6, rx - 3, y + 22 + (i % 2) * 6, SKY, 1)
    s.box(x, y + h - 12, w, 12, SEA)
    s.text(x + 24, y + 6, "AKVAN - BAY OF BENGAL", INK, 1, bold=True)


def scene_venezuela(s, x, y, w, h):
    s.box(x, y, w, h, (240, 225, 190))
    s.disc(x + 26, y + 16, 12, (255, 210, 90))
    s.poly([(x + 90, y + h - 26), (x + 110, y + 18), (x + 130, y + 18),
            (x + 150, y + h - 26)], (60, 60, 60))
    s.seg(x + 120, y + 18, x + 150, y + h - 26, (60, 60, 60), 3)
    s.seg(x + 104, y + 40, x + 136, y + 40, (60, 60, 60), 2)
    s.seg(x + 98, y + 60, x + 142, y + 60, (60, 60, 60), 2)
    s.box(x, y + h - 26, w, 26, (120, 95, 60))
    for bx in (x + 12, x + 34, x + 56):
        s.box(bx, y + h - 46, 16, 20, (40, 40, 90))
        s.box(bx, y + h - 46, 16, 3, (25, 25, 60))
    for i, (px, py) in enumerate(((170, 52), (190, 44), (206, 56))):
        s.disc(x + px, y + py, 9, GOLD)
        s.text(x + px - 3, y + py - 3, "$", INK, 1)
    s.seg(x + 164, y + 66, x + 216, y + 30, GREEN, 3)
    s.tri(x + 204, y + 26, x + 216, y + 30, x + 204, y + 36, GREEN)
    s.text(x + 24, y + 6, "$12BN - CARACAS", INK, 1, bold=True)


def scene_eisenkot(s, x, y, w, h):
    s.box(x, y, w, h, (210, 225, 240))
    s.box(x + 30, y + 40, w - 60, 30, CREAM)
    s.tri(x + 30, y + 40, x + w - 30, y + 40, x + w // 2, y + 22, (170, 150, 120))
    s.disc(x + w // 2, y + 30, 8, GOLD)
    for i in range(4):
        cx = x + 48 + i * 36
        s.box(cx, y + 40, 10, 30, WHITE)
    s.box(x + 24, y + 70, w - 48, 4, (150, 130, 100))
    s.box(x + 18, y + 74, w - 36, 4, (130, 110, 85))
    s.box(x, y + h - 10, w, 10, LEAF)
    s.vline(x + 16, y + 8, 34, INK, 2)
    s.box(x + 18, y + 10, 26, 16, WHITE)
    s.box(x + 18, y + 15, 26, 6, BLUE)
    s.disc(x + 31, y + 13, 2, BLUE)
    px = x + w - 52
    s.disc(px, y + 52, 7, (60, 40, 30))
    s.box(px - 9, y + 58, 18, 14, (40, 60, 120))
    s.box(x + w - 76, y + 62, 20, 12, (120, 90, 60))
    s.box(x + w - 76, y + 58, 20, 4, (90, 65, 40))
    s.text(x + 8, y + h - 22, "KNESSET", INK, 1, bold=True)


def scene_gazaaid(s, x, y, w, h):
    s.box(x, y, w, h, (215, 230, 235))
    s.disc(x + 22, y + 14, 11, (255, 210, 90))
    for i in range(3):
        tx = x + 16 + i * 62
        s.tri(tx, y + 34, tx + 22, y + 34, tx + 11, y + 20, WHITE)
        s.box(tx, y + 34, 22, 12, (200, 195, 180))
        s.box(tx + 8, y + 38, 6, 8, RED)
    s.box(x, y + 52, w, 8, SAND)
    for i in range(2):
        tx = x + 30 + i * 96
        s.box(tx, y + 60, 44, 14, WHITE)
        s.box(tx + 44, y + 63, 14, 11, RED)
        s.disc(tx + 10, y + 76, 4, BLACK)
        s.disc(tx + 34, y + 76, 4, BLACK)
        s.disc(tx + 52, y + 76, 4, BLACK)
    s.box(x, y + h - 16, w, 16, (90, 140, 190))
    for wx in range(0, w, 26):
        s.box(x + wx, y + h - 10, 14, 2, WHITE)
    s.text(x + 24, y + 6, "150,000 TENTS WAITING", INK, 1, bold=True)


def scene_estonia(s, x, y, w, h):
    s.box(x, y, w, h, (185, 215, 200))
    for i, th in enumerate((30, 42, 34, 46, 28)):
        tx = x + 12 + i * 18
        s.tri(tx, y + h - 40 - th, tx + 12, y + h - 40 - th, tx + 6, y + h - 40,
              (30, 100, 50))
        s.box(tx + 5, y + h - 40, 2, 8, (90, 60, 40))
    s.box(x, y + h - 34, w, 34, (110, 140, 100))
    s.vline(x + w - 60, y + 8, 44, INK, 2)
    s.box(x + w - 58, y + 10, 34, 9, BLUE)
    s.box(x + w - 58, y + 19, 34, 9, BLACK)
    s.box(x + w - 58, y + 28, 34, 9, WHITE)
    for px in range(x + 110, x + w - 4, 22):
        s.vline(px, y + 40, 34, (70, 70, 70), 2)
    s.seg(x + 110, y + 44, x + w - 4, y + 40, (70, 70, 70), 1)
    s.seg(x + 110, y + 56, x + w - 4, y + 52, (70, 70, 70), 1)
    s.seg(x + 110, y + 68, x + w - 4, y + 64, (70, 70, 70), 1)
    s.box(x + 12, y + 46, 14, 18, (90, 90, 95))
    s.tri(x + 10, y + 46, x + 28, y + 46, x + 19, y + 36, RED)
    s.text(x + 24, y + 6, "TALLINN", INK, 1, bold=True)


def scene_spain(s, x, y, w, h):
    s.box(x, y, w, h, (225, 220, 205))
    s.disc(x + w - 26, y + 16, 11, (255, 210, 90))
    s.box(x + 10, y + 34, 60, 26, (150, 90, 70))
    s.box(x + 76, y + 26, 10, 34, (120, 70, 55))
    s.box(x + 92, y + 20, 10, 40, (120, 70, 55))
    for wx in (20, 38, 56):
        s.box(x + wx, y + 42, 8, 8, GOLD)
    s.box(x + 120, y + 40, 8, 20, (90, 90, 95))
    s.seg(x + 124, y + 40, x + 150, y + 28, (90, 90, 95), 2)
    s.seg(x + 124, y + 40, x + 98, y + 28, (90, 90, 95), 2)
    s.box(x + 150, y + 44, 34, 16, (40, 90, 130))
    s.box(x + 188, y + 44, 34, 16, (160, 60, 50))
    s.box(x, y + 60, w, 4, (80, 80, 80))
    for i in range(3):
        px = x + 30 + i * 62
        s.disc(px, y + 72, 6, (60, 40, 30))
        s.box(px - 7, y + 76, 14, 10, (40, 60, 120))
        s.vline(px + 10, y + 58, 16, (90, 60, 40), 2)
        s.box(px + 12, y + 56, 26, 10, WHITE)
    s.text(x + 24, y + 6, "HOUSING", INK, 1, bold=True)
    s.box(x, y + h - 8, w, 8, (110, 110, 110))


def scene_bumrah(s, x, y, w, h):
    s.box(x, y, w, h, (90, 170, 100))
    s.box(x + w // 2 - 16, y + 8, 32, h - 16, (200, 175, 130))
    s.box(x + w // 2 - 16, y + 8, 32, 3, WHITE)
    for sy in (y + 12, y + h - 24):
        for k in range(3):
            s.box(x + w // 2 - 9 + k * 7, sy, 3, 10, GOLD)
    s.disc(x + 44, y + 26, 6, (60, 40, 30))
    s.box(x + 38, y + 32, 12, 16, (20, 90, 160))
    s.seg(x + 44, y + 30, x + 62, y + 48, (60, 40, 30), 2)
    s.seg(x + 62, y + 48, x + 74, y + 56, (200, 170, 110), 3)
    s.disc(x + w - 46, y + 30, 6, (60, 40, 30))
    s.box(x + w - 52, y + 36, 12, 16, WHITE)
    s.seg(x + w - 46, y + 40, x + w - 30, y + 52, (60, 40, 30), 2)
    for i, (bx, by) in enumerate(((30, 60), (52, 66), (74, 62))):
        s.disc(x + bx, y + by, 3, RED)
    s.seg(x + 44, y + 30, x + w - 46, y + 30, WHITE, 1)
    s.box(x + 8, y + h - 18, 96, 12, INK)
    s.text(x + 10, y + h - 16, "NZ 60/4", WHITE, 1, bold=True)
    s.text(x + w - 66, y + 6, "1ST OVER", INK, 1, bold=True)


def scene_keach(s, x, y, w, h):
    s.box(x, y, w, h, (40, 20, 50))
    s.poly([(x + 30, y), (x + 70, y), (x + w // 2 + 26, y + h - 20),
            (x + w // 2 - 26, y + h - 20)], (255, 240, 180))
    s.box(x, y, 26, h, (160, 30, 40))
    s.box(x + w - 26, y, 26, h, (160, 30, 40))
    for i in range(4):
        s.box(x + 4 + i * 6, y + 8 + i * 4, 3, h - 16 - i * 8, (120, 20, 30))
        s.box(x + w - 7 - i * 6, y + 8 + i * 4, 3, h - 16 - i * 8, (120, 20, 30))
    s.disc(x + w // 2, y + h - 34, 8, (60, 40, 30))
    s.box(x + w // 2 - 10, y + h - 28, 20, 14, (30, 30, 60))
    s.box(x + w // 2 - 4, y + h - 40, 8, 8, (60, 40, 30))
    s.disc(x + 34, y + 22, 10, GOLD)
    s.disc(x + 34, y + 22, 4, DARK)
    s.box(x + w - 52, y + 14, 30, 20, (220, 220, 210))
    s.box(x + w - 52, y + 14, 30, 4, INK)
    s.seg(x + w - 52, y + 34, x + w - 22, y + 14, INK, 2)
    s.text(x + w // 2 - 30, y + h - 14, "1941-2026", GOLD, 1, bold=True)


SCENES = {
    "gta": scene_gta, "summit": scene_summit, "anthropic": scene_anthropic,
    "crimea": scene_crimea, "icj": scene_icj, "cyclone": scene_cyclone,
    "venezuela": scene_venezuela, "eisenkot": scene_eisenkot,
    "gazaaid": scene_gazaaid, "estonia": scene_estonia,
    "spain": scene_spain, "bumrah": scene_bumrah, "keach": scene_keach,
}


# ------------------------------------------------------------------ stories
LEADS = [
    (1, "N. AMERICA", "CULTURE", "CULTURE - GAMES", "gta", -80.2, 25.8,
     "Gamers enter Vice City as GTA VI begins its global rollout",
     "After a 13-year wait, Rockstar's epic lands at midnight; pre-orders passed $1.5bn."),
    (2, "ASIA", "POLITICS", "POLITICS - APEC", "summit", 114.1, 22.5,
     "Trump, Xi and Putin meet in first three-way summit",
     "Nuclear arms top the agenda in Shenzhen; no deal expected."),
    (3, "N. AMERICA", "BUSINESS", "BUSINESS - AI", "anthropic", -122.4, 37.8,
     "Anthropic debuts after record $81.3bn IPO",
     "Priced at $83 a share; ANT lists on Nasdaq at a $1.5tn value."),
    (4, "EUROPE", "POLITICS", "POLITICS - WAR", "crimea", 34.0, 45.3,
     "Crimean Bridge hit a third time in a week",
     "Railway section struck after midnight; traffic halted, damage unclear."),
    (5, "EUROPE", "POLITICS", "POLITICS - LAW", "icj", 4.3, 52.1,
     "World court rules on Myanmar genocide case",
     "The Hague delivers its verdict today; Gambia brought the case in 2019."),
    (6, "ASIA", "WEATHER", "WEATHER - INDIA", "cyclone", 85.3, 14.1,
     "Cyclone Akvan nears India's east coast",
     "Landfall due Friday; schools shut as rain begins in Odisha."),
    (7, "S. AMERICA", "BUSINESS", "BUSINESS - OIL", "venezuela", -66.9, 10.5,
     "US details $12bn in Venezuelan oil cash",
     "State Dept report tracks the money a year after Maduro's capture."),
    (8, "MIDDLE EAST", "POLITICS", "POLITICS - ISRAEL", "eisenkot", 35.2, 31.8,
     "Eisenkot asked to form Israel's government",
     "Herzog passes over Netanyahu; 67 in the Knesset back the ex-general."),
    (9, "MIDDLE EAST", "POLITICS", "POLITICS - GAZA", "gazaaid", 34.5, 31.5,
     "Four nations press Israel to open Gaza to aid",
     "Floods add to Gaza's misery; 150,000 tents are stuck at the border."),
    (10, "EUROPE", "POLITICS", "POLITICS - EUROPE", "estonia", 24.7, 59.4,
     "Estonia to shut its border with Russia",
     "Move follows a foiled attack on a drone maker; eight held."),
    (11, "EUROPE", "BUSINESS", "BUSINESS - STRIKE", "spain", -3.7, 40.4,
     "Spain's first general strike in 14 years",
     "Ports and car plants halt in a protest over housing costs."),
    (12, "OCEANIA", "SPORT", "SPORT - CRICKET", "bumrah", 174.8, -41.3,
     "Bumrah bowls Latham for a duck at Wellington",
     "India strike in the first over; NZ reach 60 for 4 at lunch."),
    (13, "N. AMERICA", "CULTURE", "CULTURE - OBITUARY", "keach", -118.2, 34.1,
     "Stacy Keach, TV's Mike Hammer, dies at 85",
     "Six-decade career on stage and screen; he died in Poland."),
]

BRIEFS = [
    ("N. AMERICA", "POLITICS", "Canada retools China ties as Carney chases US deal"),
    ("N. AMERICA", "TECH", "Senators: AI cyber threats outpacing US defences"),
    ("EUROPE", "POLITICS", "Melenchon could win French presidency, minister says"),
    ("MIDDLE EAST", "POLITICS", "Saudi Arabia: danger passed in three southern cities"),
    ("AFRICA", "CRIME", "Cocaine, millions of pills seized in eastern Libya"),
    ("ASIA", "POLITICS", "Congress presses Modi government on inflation"),
    ("EUROPE", "CRIME", "McDonald's abuse: 'waiting for girls to turn 18'"),
    ("EUROPE", "CRIME", "Russian held for spying on Palantir over Ukraine aid"),
    ("ASIA", "POLITICS", "India, Japan to review defence ties in 2+2 talks"),
    ("AFRICA", "POLITICS", "Somalia accuses UAE of secret bases on its soil"),
    ("WORLD", "CULTURE", "Islam on track to be top faith by 2035, Pew says"),
    ("WORLD", "BUSINESS", "Oil prices fall as Middle East risk rises"),
    ("EUROPE", "POLITICS", "Prague crowds demand media freedom"),
    ("EUROPE", "POLITICS", "Russia, Ukraine trade drone strikes as talks go on"),
    ("EUROPE", "CRIME", "German police warn of rising hybrid cyber threats"),
    ("EUROPE", "SPORT", "Man Utd chase Como star Paz, Thursday gossip says"),
    ("MIDDLE EAST", "POLITICS", "Peace Council warns Gaza rebuild has stalled"),
    ("N. AMERICA", "POLITICS", "Democrats gain most Senate seats in 70 years"),
    ("WORLD", "SCIENCE", "Merck launches new rabies vaccine for pets"),
    ("MIDDLE EAST", "POLITICS", "NGO: Israel limits care for 1,100 child amputees"),
    ("EUROPE", "POLITICS", "France counts 146,000 at cost-of-living marches"),
    ("EUROPE", "POLITICS", "Soder urges deal on power tax and bracket creep"),
    ("EUROPE", "WORLD", "Older Germans take twice the sick days, data show"),
    ("EUROPE", "POLITICS", "Die Linke seeks windfall tax on defence profits"),
    ("EUROPE", "POLITICS", "Most Germans see Russia as a threat, poll finds"),
    ("EUROPE", "CRIME", "French navy seizes boat with 146kg drug haul"),
    ("EUROPE", "TECH", "Germany debates phone cameras to catch drivers"),
    ("EUROPE", "TECH", "AI in focus at German engineering summit"),
    ("N. AMERICA", "POLITICS", "Senator reveals US arms stockpile spent on Iran war"),
    ("ASIA", "TECH", "Tiny electric cars crowd China's city streets"),
    ("WORLD", "SCIENCE", "NASA marks Voyager milestone with live talk"),
    ("WORLD", "BUSINESS", "Gold holds above $4,100 as yields cool"),
    ("OCEANIA", "SPORT", "Latham's duck ties Sehwag's opener record"),
    ("N. AMERICA", "BUSINESS", "Amazon, Google hold big Anthropic stakes"),
    ("N. AMERICA", "BUSINESS", "Anthropic revenue hits $33bn in nine months"),
]

# Figures reported on 19 November itself: (big figure, what it is).
NUMBERS = [
    ("$81.3B", "Anthropic IPO, largest ever"),
    ("13 YRS", "wait ends as GTA VI lands"),
    ("$1.5BN", "GTA VI pre-orders"),
    ("980M", "Anthropic shares sold"),
    ("60/4", "NZ at lunch in Wellington"),
    ("150,000", "tents stuck at Gaza border"),
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

# Leads 8 and 9 both sit on Israel and Gaza: pin 9 is offset with a
# leader line back to Gaza.
PIN_OFFSET = {9: (16, -12)}


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
    s.text(16, y, label, INK, 1, bold=True)
    cx = 16 + text_width(label, 1, True) + 12
    for name in order:
        n = counts.get(name, 0)
        if not n:
            continue
        lab = "%s %d" % (name, n)
        s.text(cx, y, lab, INK, 1)
        cx += text_width(lab, 1) + 6
        s.box(cx, y + 1, n * 6, 5, color)
        cx += n * 6 + 12


def lead_card(s, x, y, w, h, lead):
    num, _rg, _fd, tag, scene, _lon, _lat, headline, deck = lead
    s.frame(x, y, w, h, INK, 1)
    SCENES[scene](s, x + 1, y + 1, w - 2, 80)
    s.box(x + 1, y + 1, 20, 14, RED)
    num_s = str(num)
    s.text(x + 1 + (20 - text_width(num_s, 1)) // 2, y + 4, num_s, WHITE, 1)
    s.text(x + 6, y + 85, tag, RED, 1, bold=True)
    yy = y + 95
    for ln in wrap_text(headline, w - 12, 1, True)[:3]:
        s.text(x + 6, yy, ln, INK, 1, bold=True)
        yy += 10
    yy = y + 127
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
    s.text(tx, y + 8, tag, RED, 1, bold=True)
    yy = y + 22
    for ln in wrap_text(headline, tw, 2, True)[:3]:
        s.text(tx, yy, ln, INK, 2, bold=True)
        yy += 16
    yy = y + 74
    for ln in wrap_text(deck, tw, 1)[:2]:
        s.text(tx, yy, ln, GREY, 1)
        yy += 9
    s.hline(tx, y + 98, tw, LIGHT, 1)
    s.text(tx, y + 104, "INSIDE: 12 MORE LEADS - BY THE NUMBERS - MAP - 35 BRIEFS",
           INK, 1)


# -------------------------------------------------------------------- main
def out_path():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return os.path.join(d, "entry.png")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def main():
    assert len(LEADS) + len(BRIEFS) == 48, "story count must be 48"
    assert len(LEADS) == 13 and len(BRIEFS) == 35
    s = Sheet()
    # masthead
    s.hline(16, 10, 992, INK, 2)
    s.centred(16, "THE WORLD IN ONE PICTURE", INK, 4, bold=True)
    s.centred(48, "THURSDAY 19 NOVEMBER 2026 | 48 STORIES | ONE IMAGE",
              GREY, 1, bold=True)
    s.hline(16, 60, 992, INK, 2)
    # hero lead: GTA VI
    hero_card(s, 16, 68, 992, 122, LEADS[0])
    # 12 more illustrated leads, 3 rows of 4
    for i, lead in enumerate(LEADS[1:]):
        row, col = divmod(i, 4)
        lead_card(s, 16 + col * 250, 198 + row * 160, 242, 152, lead)
    # by the numbers
    s.frame(16, 678, 992, 50, INK, 1)
    s.text(28, 690, "BY THE", RED, 1, bold=True)
    s.text(28, 700, "NUMBERS", RED, 1, bold=True)
    for i, (big, label) in enumerate(NUMBERS):
        cx = 150 + i * 142
        s.text(cx, 686, big, INK, 2, bold=True)
        yy = 706
        for ln in wrap_text(label, 138, 1)[:2]:
            s.text(cx, yy, ln, GREY, 1)
            yy += 9
    # region and field bars, counted from the stories themselves
    all_stories = [(rg, fd) for (_n, rg, fd, _t, _s, _lo, _la, _h, _d) in LEADS]
    all_stories += [(rg, fd) for (rg, fd, _t) in BRIEFS]
    draw_bars(s, 736, "REGIONS", REGION_ORDER,
              count_by(all_stories, 0), BLUE)
    draw_bars(s, 750, "FIELDS", FIELD_ORDER,
              count_by(all_stories, 1), TEAL)
    # map and briefs
    s.text(16, 766, "WHERE THE NEWS HAPPENED", INK, 1, bold=True)
    s.text(340, 766, "THE DAY IN BRIEF - 35 MORE STORIES", INK, 1, bold=True)
    draw_map(s, 16, 778, 310, 180)
    for i, (_rg, _fd, text) in enumerate(BRIEFS):
        col = i // 18
        row = i % 18
        s.text(340 + col * 336, 778 + row * 10, text, INK, 1)
    # footer: date check, the 18 November stories left out, sources
    s.centred(966, "DATE CHECK: ALL 48 STORIES WERE REPORTED ON "
              "THURSDAY 19 NOVEMBER 2026.", INK, 1, bold=True)
    s.centred(978, "LEFT OUT, FIRST REPORTED 18 NOV: VAN GOGH $190.4M SALE - "
              "JEFFRIES NOMINATION - FED MINUTES -", INK, 1)
    s.centred(990, "EU \u20ac45BN LOAN - GAZA YELLOW LINE RAID - VOYAGER 1 "
              "CROSSING - DUCKETT 133.", INK, 1)
    s.centred(1002, "SOURCES: BBC NEWS, REUTERS, AP, CNN, THE HINDU, "
              "CRICTRACKER, LE MONDE, BUSINESSWORLD, NDTV", GREY, 1)
    path = out_path()
    write_png(s, path)
    print("wrote %s 1024x1024, %d stories (%d leads, %d briefs)"
          % (path, len(LEADS) + len(BRIEFS), len(LEADS), len(BRIEFS)))


if __name__ == "__main__":
    main()
