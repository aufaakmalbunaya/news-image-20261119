#!/usr/bin/env python3
"""THE WORLD IN ONE PICTURE - Thursday 19 November 2026.

Draws a 1024x1024 newspaper front page (48 stories) as a PNG.
Standard library only. Deterministic: no time, no randomness.
Writes entry.png beside this script, or to $MAKEFUN_OUTPUT_DIR.
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (179, 35, 27)
NAVY = (20, 38, 77)
TEAL = (14, 110, 110)
GOLD = (201, 141, 32)
SKY = (168, 208, 232)
GREY = (110, 108, 100)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits, written as strings. Lowercase maps to
# uppercase, so M and W keep their full shapes and never read as rn.
_G = {}


def _g(ch, rows):
    _G[ch] = tuple(int(r.replace("#", "1").replace(".", "0"), 2) for r in rows)


_g("A", ["01110", "10001", "10001", "11111", "10001", "10001", "10001"])
_g("B", ["11110", "10001", "10001", "11110", "10001", "10001", "11110"])
_g("C", ["01110", "10001", "10000", "10000", "10000", "10001", "01110"])
_g("D", ["11110", "10001", "10001", "10001", "10001", "10001", "11110"])
_g("E", ["11111", "10000", "10000", "11110", "10000", "10000", "11111"])
_g("F", ["11111", "10000", "10000", "11110", "10000", "10000", "10000"])
_g("G", ["01110", "10001", "10000", "10111", "10001", "10001", "01111"])
_g("H", ["10001", "10001", "10001", "11111", "10001", "10001", "10001"])
_g("I", ["01110", "00100", "00100", "00100", "00100", "00100", "01110"])
_g("J", ["00111", "00010", "00010", "00010", "00010", "10010", "01100"])
_g("K", ["10001", "10010", "10100", "11000", "10100", "10010", "10001"])
_g("L", ["10000", "10000", "10000", "10000", "10000", "10000", "11111"])
_g("M", ["10001", "11011", "10101", "10101", "10001", "10001", "10001"])
_g("N", ["10001", "11001", "10101", "10011", "10001", "10001", "10001"])
_g("O", ["01110", "10001", "10001", "10001", "10001", "10001", "01110"])
_g("P", ["11110", "10001", "10001", "11110", "10000", "10000", "10000"])
_g("Q", ["01110", "10001", "10001", "10001", "10101", "10010", "01101"])
_g("R", ["11110", "10001", "10001", "11110", "10100", "10010", "10001"])
_g("S", ["01111", "10000", "10000", "01110", "00001", "00001", "11110"])
_g("T", ["11111", "00100", "00100", "00100", "00100", "00100", "00100"])
_g("U", ["10001", "10001", "10001", "10001", "10001", "10001", "01110"])
_g("V", ["10001", "10001", "10001", "10001", "10001", "01010", "00100"])
_g("W", ["10001", "10001", "10001", "10101", "10101", "10101", "01010"])
_g("X", ["10001", "10001", "01010", "00100", "01010", "10001", "10001"])
_g("Y", ["10001", "10001", "01010", "00100", "00100", "00100", "00100"])
_g("Z", ["11111", "00001", "00010", "00100", "01000", "10000", "11111"])
_g("0", ["01110", "10001", "10011", "10101", "11001", "10001", "01110"])
_g("1", ["00100", "01100", "00100", "00100", "00100", "00100", "01110"])
_g("2", ["01110", "10001", "00001", "00110", "01000", "10000", "11111"])
_g("3", ["11110", "00001", "00001", "01110", "00001", "00001", "11110"])
_g("4", ["00010", "00110", "01010", "10010", "11111", "00010", "00010"])
_g("5", ["11111", "10000", "11110", "00001", "00001", "10001", "01110"])
_g("6", ["01110", "10000", "10000", "11110", "10001", "10001", "01110"])
_g("7", ["11111", "00001", "00010", "00100", "01000", "01000", "01000"])
_g("8", ["01110", "10001", "10001", "01110", "10001", "10001", "01110"])
_g("9", ["01110", "10001", "10001", "01111", "00001", "00001", "01110"])
_g(".", ["00000", "00000", "00000", "00000", "00000", "01100", "01100"])
_g(",", ["00000", "00000", "00000", "00000", "01100", "00100", "01000"])
_g(":", ["00000", "01100", "01100", "00000", "01100", "01100", "00000"])
_g(";", ["00000", "01100", "01100", "00000", "01100", "00100", "01000"])
_g("!", ["00100", "00100", "00100", "00100", "00100", "00000", "00100"])
_g("?", ["01110", "10001", "00001", "00110", "00100", "00000", "00100"])
_g("'", ["00100", "00100", "01000", "00000", "00000", "00000", "00000"])
_g('"', ["01010", "01010", "00000", "00000", "00000", "00000", "00000"])
_g("-", ["00000", "00000", "00000", "01110", "00000", "00000", "00000"])
_g("/", ["00001", "00010", "00010", "00100", "01000", "01000", "10000"])
_g("(", ["00010", "00100", "01000", "01000", "01000", "00100", "00010"])
_g(")", ["01000", "00100", "00010", "00010", "00010", "00100", "01000"])
_g("$", ["00100", "01111", "10100", "01110", "00101", "11110", "00100"])
_g("%", ["11001", "11010", "00010", "00100", "01000", "01011", "10011"])
_g("&", ["01100", "10010", "10100", "01000", "10101", "10010", "01101"])
_g("+", ["00000", "00100", "00100", "11111", "00100", "00100", "00000"])
_g("=", ["00000", "00000", "11111", "00000", "11111", "00000", "00000"])
_g("*", ["00000", "10101", "01110", "10101", "00000", "00000", "00000"])
_g("#", ["01010", "01010", "11111", "01010", "11111", "01010", "01010"])
_g("@", ["01110", "10001", "10111", "10101", "10110", "10000", "01110"])
_g("_", ["00000", "00000", "00000", "00000", "00000", "00000", "11111"])
_g("<", ["00010", "00100", "01000", "10000", "01000", "00100", "00010"])
_g(">", ["01000", "00100", "00010", "00001", "00010", "00100", "01000"])
_g("[", ["01110", "01000", "01000", "01000", "01000", "01000", "01110"])
_g("]", ["01110", "00010", "00010", "00010", "00010", "00010", "01110"])
_g(" ", ["00000", "00000", "00000", "00000", "00000", "00000", "00000"])

SPACE_W = 6


def glyph(ch):
    ch = ch.upper()
    if ch in ("’", "‘"):
        ch = "'"
    if ch in ("–", "—"):
        ch = "-"
    return _G.get(ch, _G[" "])


def text_w(s, sc):
    return len(s) * SPACE_W * sc


def wrap(s, maxw, sc):
    words = s.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, sc) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c)

    def tri(self, ax, ay, bx, by, cx, cy, c):
        ys = sorted([ay, by, cy])
        for y in range(ys[0], ys[2] + 1):
            xs = []
            for (x0, y0, x1, y1) in ((ax, ay, bx, by), (bx, by, cx, cy), (cx, cy, ax, ay)):
                if y0 == y1:
                    continue
                if min(y0, y1) <= y <= max(y0, y1):
                    xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
            if len(xs) >= 2:
                for x in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(x, y, c)

    def text(self, x, y, s, sc, c, bold=False):
        cx = x
        for ch in s:
            g = glyph(ch)
            for r in range(7):
                bits = g[r]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.rect(cx + col * sc, y + r * sc, sc, sc, c)
                        if bold:
                            self.rect(cx + col * sc + 1, y + r * sc, sc, sc, c)
            cx += SPACE_W * sc
        return cx

    def text_lines(self, x, y, lines, sc, c, bold=False, lh=None):
        lh = lh or (7 * sc + 2)
        for ln in lines:
            self.text(x, y, ln, sc, c, bold)
            y += lh
        return y


def png_bytes(w, h, px):
    raw = b"".join(b"\x00" + bytes(px[y * w * 3:(y + 1) * w * 3]) for y in range(h))

    def chunk(t, data):
        c = t + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- data
# region buckets: NAMERICA SAMERICA EUROPE MIDEAST AFRICA ASIA OCEANIA WORLD
# fields: POLITICS BUSINESS TECH SCIENCE CULTURE SPORT CRIME WEATHER HEALTH
LEADS = [
    dict(n=1, kicker="VICE CITY - GAMES", head="GAMERS ENTER VICE CITY AS GTA VI LANDS",
         deck="After a 13-year wait, Rockstar's epic lands at midnight. Pre-orders passed $1.5bn. Metacritic 99.",
         region="WORLD", field="CULTURE", scene="gta", pin=(-74, 40),
         src="Sensor Tower; Metacritic"),
    dict(n=2, kicker="APEC - SHENZHEN", head="TRUMP, XI AND PUTIN MEET IN FIRST THREE-WAY SUMMIT",
         deck="Nuclear arms and Iran top the agenda.",
         region="ASIA", field="POLITICS", scene="apec", pin=(114, 22), src="Reuters"),
    dict(n=3, kicker="BUSINESS - AI", head="ANTHROPIC DEBUTS AFTER RECORD $81.3BN IPO",
         deck="Priced $83, ANT lists on Nasdaq.",
         region="NAMERICA", field="BUSINESS", scene="ipo", pin=(-122, 37), src="Reuters"),
    dict(n=4, kicker="POLITICS - WAR", head="CRIMEAN BRIDGE HIT A THIRD TIME IN A WEEK",
         deck="Railway section struck. Traffic halted.",
         region="EUROPE", field="POLITICS", scene="bridge", pin=(36, 45), src="Reuters"),
    dict(n=5, kicker="POLITICS - LAW", head="WORLD COURT RULES ON MYANMAR GENOCIDE CASE",
         deck="The Hague rules today. Filed in 2019.",
         region="EUROPE", field="POLITICS", scene="court", pin=(4, 52), src="Reuters"),
    dict(n=6, kicker="WEATHER - INDIA", head="CYCLONE AKVAN NEARS INDIA'S EAST COAST",
         deck="Landfall due Friday. 200,000 evacuated.",
         region="ASIA", field="WEATHER", scene="cyclone", pin=(86, 20), src="Reuters"),
    dict(n=7, kicker="POLITICS - GAZA", head="ISRAELI TANKS CROSS GAZA CEASEFIRE LINE",
         deck="First ground push since the truce.",
         region="MIDEAST", field="POLITICS", scene="gaza", pin=(34, 31), src="World Attention"),
    dict(n=8, kicker="BUSINESS - MARKETS", head="S AND P 500 FALLS FOR A FIFTH STRAIGHT DAY",
         deck="Longest slide since June. Dow falls 561.",
         region="NAMERICA", field="BUSINESS", scene="stocks", pin=(-87, 41), src="Traders Union"),
    dict(n=9, kicker="SPORT - CRICKET", head="BUMRAH BOWLS LATHAM FOR A DUCK AT WELLINGTON",
         deck="First-over strike. NZ 60 for 4.",
         region="OCEANIA", field="SPORT", scene="cricket", pin=(174, -41), src="Reuters"),
    dict(n=10, kicker="WEATHER - USA", head="FLOODED FLORIDA BRACES FOR STILL MORE RAIN",
         deck="A foot of rain. Schools shut Thursday.",
         region="NAMERICA", field="WEATHER", scene="flood", pin=(-80, 26), src="Florida Today"),
    dict(n=11, kicker="POLITICS - SAUDI ARABIA", head="SAUDI DEFENCES DOWN A MISSILE AIMED SOUTH",
         deck="Thursday intercept after Wed alerts.",
         region="MIDEAST", field="POLITICS", scene="saudi", pin=(46, 24), src="The Chronicle"),
    dict(n=12, kicker="BUSINESS - MEXICO", head="BANXICO MINUTES LAND AFTER ITS SPLIT RATE CUT",
         deck="Minutes of the 3-2 cut to 6.25% out.",
         region="NAMERICA", field="BUSINESS", scene="bank", pin=(-99, 19), src="Banxico"),
    dict(n=13, kicker="POLITICS - INDIA", head="MODI MEETS WILLIAM AND KATE AS ROYAL TOUR ENDS",
         deck="Earthshot week ends in Delhi today.",
         region="ASIA", field="POLITICS", scene="royal", pin=(77, 28), src="BBC News"),
]

BRIEFS = [
    ("NAMERICA", "POLITICS", "CANADA - Carney retools China ties, chases US deal"),
    ("NAMERICA", "TECH", "USA - Senators: AI cyber threats outpace defences"),
    ("ASIA", "POLITICS", "INDIA - Congress presses Modi govt on inflation"),
    ("NAMERICA", "CRIME", "USA - McDonald's abuse: girls told to wait till 18"),
    ("EUROPE", "CRIME", "EUROPE - Russian held for spying on Palantir"),
    ("ASIA", "POLITICS", "ASIA - India, Japan review defence ties in 2+2"),
    ("AFRICA", "POLITICS", "AFRICA - Somalia accuses UAE of secret bases"),
    ("WORLD", "CULTURE", "WORLD - Islam on track as top faith by 2035: Pew"),
    ("WORLD", "BUSINESS", "WORLD - Oil prices fall as Middle East risk rises"),
    ("EUROPE", "POLITICS", "EUROPE - Prague crowds demand media freedom"),
    ("EUROPE", "POLITICS", "EUROPE - Russia, Ukraine trade drone strikes"),
    ("EUROPE", "TECH", "GERMANY - Police warn of hybrid cyber threats"),
    ("EUROPE", "SPORT", "UK - Man Utd chase Como star Paz, gossip says"),
    ("MIDEAST", "POLITICS", "GAZA - Peace Council: Gaza rebuild has stalled"),
    ("NAMERICA", "HEALTH", "USA - Merck launches new rabies vaccine for pets"),
    ("MIDEAST", "HEALTH", "GAZA - NGO: Israel limits care for 1,100 child amputees"),
    ("EUROPE", "POLITICS", "FRANCE - 146,000 march over cost of living"),
    ("EUROPE", "POLITICS", "GERMANY - Soder urges deal on power tax, brackets"),
    ("EUROPE", "HEALTH", "GERMANY - Older Germans take twice the sick days"),
    ("EUROPE", "POLITICS", "GERMANY - Die Linke seeks windfall tax on defence"),
    ("EUROPE", "POLITICS", "GERMANY - Most Germans see Russia as a threat"),
    ("EUROPE", "CRIME", "FRANCE - Navy seizes boat with 146kg drug haul"),
    ("EUROPE", "POLITICS", "GERMANY - Debate on phone cameras for drivers"),
    ("EUROPE", "TECH", "GERMANY - AI in focus at engineering summit"),
    ("NAMERICA", "POLITICS", "USA - Senator: arms stockpile spent on Iran war"),
    ("ASIA", "TECH", "CHINA - Tiny electric cars crowd city streets"),
    ("NAMERICA", "SCIENCE", "USA - NASA hosts live Voyager talk today"),
    ("WORLD", "BUSINESS", "WORLD - Gold holds above $4,100 as yields cool"),
    ("OCEANIA", "SPORT", "NZ - Latham duck ties Sehwag opener record"),
    ("NAMERICA", "BUSINESS", "USA - Amazon, Google hold big Anthropic stakes"),
    ("NAMERICA", "BUSINESS", "USA - Anthropic revenue hits $33bn in nine months"),
    ("ASIA", "POLITICS", "INDIA - Air India crash probe near done, Centre tells SC"),
    ("NAMERICA", "BUSINESS", "USA - Nasdaq ends slide as Dow falls 561"),
    ("NAMERICA", "BUSINESS", "USA - UnitedHealth sinks 10% on Medicare clawback"),
    ("NAMERICA", "BUSINESS", "USA - Anthropic lines up $26bn private placement"),
]

NUMBERS = [
    ("$81.3B", "Anthropic IPO, largest ever"),
    ("13 YRS", "wait ends as GTA VI lands"),
    ("$1.5BN", "GTA VI pre-orders"),
    ("980M", "Anthropic shares sold"),
    ("60/4", "NZ at lunch in Wellington"),
    ("200,000", "evacuated ahead of Akvan"),
]

REGION_ORDER = ["NAMERICA", "SAMERICA", "EUROPE", "MIDEAST", "AFRICA", "ASIA", "OCEANIA", "WORLD"]
REGION_LABEL = {"NAMERICA": "N. AMERICA", "SAMERICA": "S. AMERICA", "EUROPE": "EUROPE",
                "MIDEAST": "MIDDLE EAST", "AFRICA": "AFRICA", "ASIA": "ASIA",
                "OCEANIA": "OCEANIA", "WORLD": "WORLD"}
FIELD_ORDER = ["POLITICS", "BUSINESS", "TECH", "SCIENCE", "CULTURE", "SPORT", "CRIME", "WEATHER", "HEALTH", "WORLD"]
FIELD_COLOR = {"POLITICS": RED, "BUSINESS": NAVY, "TECH": TEAL, "SCIENCE": (90, 60, 140),
               "CULTURE": GOLD, "SPORT": (30, 130, 60), "CRIME": (120, 40, 90),
               "WEATHER": (40, 120, 170), "HEALTH": (200, 90, 40), "WORLD": GREY}

FOOTER_LEFT_OUT = ("LEFT OUT ON PURPOSE: VENEZUELA $12BN KPMG REPORT (12 NOV); "
                   "EISENKOT MANDATE (8 NOV); ESTONIA BORDER CLOSURE (15 NOV); "
                   "STACY KEACH DIES (10 NOV); JEFFRIES NOMINATION 251-11 (18 NOV); "
                   "VOYAGER 1 ONE LIGHT-DAY (18 NOV); EU 45BN EURO UKRAINE LOAN (18 NOV); "
                   "NVIDIA $115.8BN QUARTER (17 NOV); SPAIN GENERAL STRIKE (11 NOV); "
                   "GAZA TENTS STATEMENT (15 NOV); MELENCHON WARNING (18 NOV); "
                   "LIBYA DRUG HAUL (18 NOV).")
SOURCES = ("SOURCES: REUTERS, AP, BBC NEWS, NPR, SENSOR TOWER, NATIONAL WEATHER SERVICE, "
           "FLORIDA TODAY, THE HINDU BUSINESS LINE, TRADERS UNION, BANXICO, THE CHRONICLE.")


# ---------------------------------------------------------------- scenes
def _sky(cv, x, y, w, h, top, bot):
    cv.rect(x, y, w, h // 2, top)
    cv.rect(x, y + h // 2, w, h - h // 2, bot)


def _building(cv, x, y, w, h, c, lit):
    cv.rect(x, y, w, h, c)
    for wy in range(y + 4, y + h - 3, 7):
        for wx in range(x + 3, x + w - 3, 6):
            if (wx * 7 + wy * 13) % 5 < 2:
                cv.rect(wx, wy, 2, 3, lit)


def _flag(cv, x, y, w, h, kind):
    cv.line(x, y, x, y + h + 14, INK)
    if kind == "us":
        cv.rect(x, y, w, h, (200, 40, 40))
        for i in range(4):
            cv.rect(x, y + i * (h // 4), w, h // 8, (255, 255, 255))
        cv.rect(x, y, w // 2, h // 2, NAVY)
    elif kind == "cn":
        cv.rect(x, y, w, h, (220, 30, 30))
        cv.disc(x + 5, y + 4, 2, GOLD)
    elif kind == "ru":
        cv.rect(x, y, w, h // 3, (255, 255, 255))
        cv.rect(x, y + h // 3, w, h // 3, (40, 80, 200))
        cv.rect(x, y + 2 * h // 3, w, h // 3 + 1, (200, 40, 40))
    elif kind == "uk":
        cv.rect(x, y, w, h, NAVY)
        cv.rect(x + w // 2 - 1, y, 3, h, (255, 255, 255))
        cv.rect(x, y + h // 2 - 1, w, 3, (255, 255, 255))
        cv.rect(x + w // 2 - 1, y, 1, h, RED)
        cv.rect(x, y + h // 2 - 1, w, 1, RED)
    elif kind == "in":
        cv.rect(x, y, w, h // 3, (230, 120, 30))
        cv.rect(x, y + h // 3, w, h // 3, (255, 255, 255))
        cv.rect(x, y + 2 * h // 3, w, h // 3 + 1, (30, 130, 60))
        cv.disc(x + w // 2, y + h // 2, 2, NAVY)


def _person(cv, x, y, s, shirt, skin=(220, 180, 140)):
    cv.disc(x, y, 3 * s // 2, skin)
    cv.rect(x - 3 * s // 2, y + 3 * s // 2, 3 * s, 5 * s, shirt)
    cv.rect(x - 3 * s // 2, y + 8 * s // 2, s, 5 * s, INK)
    cv.rect(x + s // 2, y + 8 * s // 2, s, 5 * s, INK)


def draw_scene(cv, key, x, y, w, h):
    if key == "gta":
        _sky(cv, x, y, w, h, (120, 60, 140), (240, 120, 60))
        cv.disc(x + w - w // 5, y + h // 4, h // 5, (255, 210, 90))
        for i, bh in enumerate((h // 2, h // 3, h * 3 // 5, h // 4, h // 2)):
            _building(cv, x + 4 + i * (w // 6), y + h - 14 - bh, w // 8, bh, (30, 20, 40), (255, 220, 100))
        cv.rect(x, y + h - 14, w, 14, (40, 40, 50))
        for dx in range(4, w - 4, 16):
            cv.rect(x + dx, y + h - 8, 8, 2, (255, 255, 255))
        cv.rect(x + w // 4, y + h - 26, w // 3, 8, (230, 60, 140))
        cv.rect(x + w // 4 + 4, y + h - 32, w // 5, 6, (230, 60, 140))
        cv.disc(x + w // 4 + 6, y + h - 16, 3, INK)
        cv.disc(x + w // 4 + w // 3 - 6, y + h - 16, 3, INK)
        cv.line(x + w - 14, y + h - 14, x + w - 8, y + h - 30, (30, 130, 60))
        cv.line(x + w - 14, y + h - 30, x + w - 22, y + h - 26, (30, 130, 60))
        cv.line(x + w - 14, y + h - 30, x + w - 6, y + h - 26, (30, 130, 60))
    elif key == "apec":
        _sky(cv, x, y, w, h, SKY, (210, 225, 235))
        _flag(cv, x + w // 6, y + 4, 18, 12, "us")
        _flag(cv, x + w // 2 - 9, y + 4, 18, 12, "cn")
        _flag(cv, x + 5 * w // 6 - 18, y + 4, 18, 12, "ru")
        cv.rect(x + 6, y + h - 18, w - 12, 8, (120, 80, 40))
        cv.rect(x + 6, y + h - 26, w - 12, 8, (150, 105, 55))
        _person(cv, x + w // 5, y + h - 40, 1, NAVY)
        _person(cv, x + w // 2, y + h - 40, 1, RED)
        _person(cv, x + 4 * w // 5, y + h - 40, 1, (60, 60, 60))
    elif key == "ipo":
        cv.rect(x, y, w, h, NAVY)
        cv.disc(x + w - 18, y + 12, 8, GOLD)
        cv.text(x + w - 21, y + 9, "$", 1, NAVY, True)
        pts = [(x + 4, y + h - 10), (x + w // 4, y + h - 18), (x + w // 2, y + h - 26),
               (x + 3 * w // 4, y + h - 34), (x + w - 6, y + h - 42)]
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], (60, 200, 90))
            cv.line(a[0], a[1] + 1, b[0], b[1] + 1, (60, 200, 90))
        cv.rect(x + w // 3, y + h - 20, 6, 12, RED)
        cv.rect(x + w // 2, y + h - 26, 6, 18, (60, 200, 90))
        cv.text(x + 4, y + 4, "ANT $83", 1, (255, 255, 255), True)
    elif key == "bridge":
        _sky(cv, x, y, w, h, SKY, (190, 215, 230))
        cv.rect(x, y + h // 2, w, h // 2, (40, 110, 170))
        cv.rect(x, y + h // 2 - 6, w, 6, (120, 120, 125))
        cv.rect(x + w // 4, y + 8, 4, h // 2, (90, 90, 95))
        cv.rect(x + 3 * w // 4, y + 8, 4, h // 2, (90, 90, 95))
        cv.line(x + w // 4 + 2, y + 8, x + w // 2, y + h // 2 - 6, (90, 90, 95))
        cv.line(x + 3 * w // 4 + 2, y + 8, x + w // 2, y + h // 2 - 6, (90, 90, 95))
        ex, ey = x + w // 2, y + h // 2 - 10
        for dx, dy in ((0, -12), (10, -6), (12, 4), (4, 12), (-6, 10), (-12, 2), (-9, -8), (6, -11)):
            cv.tri(ex, ey, ex + dx, ey + dy, ex + dx // 2 + 3, ey + dy // 2 - 3, (255, 140, 0))
        cv.disc(ex, ey, 5, (255, 220, 60))
        cv.disc(ex - 14, ey - 8, 5, (120, 120, 120))
        cv.disc(ex + 16, ey - 6, 4, (120, 120, 120))
    elif key == "court":
        _sky(cv, x, y, w, h, SKY, (215, 225, 235))
        cv.rect(x + 6, y + h - 10, w - 12, 10, (160, 150, 130))
        cv.tri(x + 4, y + 8, x + w - 4, y + 8, x + w // 2, y + 2, (230, 220, 200))
        for i in range(4):
            cx0 = x + 12 + i * (w - 24) // 4
            cv.rect(cx0, y + 10, 6, h - 22, (240, 235, 220))
            cv.rect(cx0 - 2, y + 8, 10, 3, (240, 235, 220))
        cv.rect(x + w // 2 - 8, y + h - 24, 16, 14, (90, 60, 40))
    elif key == "cyclone":
        _sky(cv, x, y, w, h, (150, 180, 210), (190, 205, 225))
        cx0, cy0 = x + w // 3, y + h // 2
        for r in range(4, h // 2, 5):
            cv.circle(cx0, cy0, r, (255, 255, 255))
        cv.disc(cx0, cy0, 3, NAVY)
        cv.tri(x + 2 * w // 3, y + h - 16, x + w - 2, y + h - 16, x + 5 * w // 6, y + h // 2, (220, 170, 90))
        cv.rect(x + 2 * w // 3, y + h - 16, w // 3, 4, (200, 150, 70))
        for i in range(6):
            cv.line(x + 8 + i * 12, y + 4, x + 4 + i * 12, y + 12, (200, 220, 240))
    elif key == "gaza":
        _sky(cv, x, y, w, h, (220, 200, 150), (200, 175, 120))
        for i in range(3):
            tx = x + 8 + i * (w // 3)
            cv.tri(tx, y + h - 14, tx + 20, y + h - 14, tx + 10, y + h - 28, (240, 235, 220))
        for dx in range(0, w, 10):
            cv.rect(x + dx, y + h // 2, 5, 2, GOLD)
        cv.rect(x + w // 2 - 18, y + h - 26, 30, 10, (60, 90, 50))
        cv.rect(x + w // 2 - 10, y + h - 32, 12, 7, (60, 90, 50))
        cv.line(x + w // 2 + 2, y + h - 29, x + w // 2 + 20, y + h - 29, INK)
        cv.disc(x + w // 2 - 12, y + h - 15, 3, INK)
        cv.disc(x + w // 2 + 6, y + h - 15, 3, INK)
    elif key == "stocks":
        cv.rect(x, y, w, h, (255, 255, 255))
        cv.rect(x, y + h - 14, w, 2, GREY)
        for i, hh in enumerate((14, 10, 16, 8, 12)):
            bx = x + 10 + i * (w // 6)
            cv.rect(bx, y + 10 + i * 3, 8, hh, RED)
            cv.line(bx + 4, y + 6 + i * 3, bx + 4, y + 12 + i * 3 + hh, RED)
        pts = [(x + 4, y + 8), (x + w // 4, y + 16), (x + w // 2, y + 22),
               (x + 3 * w // 4, y + 30), (x + w - 6, y + h - 18)]
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], RED)
            cv.line(a[0], a[1] + 1, b[0], b[1] + 1, RED)
        cv.text(x + 4, y + h - 12, "-0.23%", 1, RED, True)
    elif key == "cricket":
        _sky(cv, x, y, w, h, SKY, (200, 225, 235))
        cv.rect(x, y + h - 20, w, 20, (70, 160, 80))
        cv.rect(x + w // 3, y + h - 20, w // 3, 20, (190, 160, 110))
        for i in range(3):
            cv.rect(x + w // 2 - 6 + i * 5, y + h - 34, 2, 14, (255, 255, 255))
        cv.rect(x + w // 2 - 6, y + h - 36, 14, 2, (255, 255, 255))
        _person(cv, x + w // 5, y + h - 40, 1, (30, 130, 60))
        cv.disc(x + w // 2 + 14, y + h - 30, 3, RED)
        cv.rect(x + w - 22, y + h - 34, 14, 12, (255, 255, 255))
        cv.text(x + w - 20, y + h - 32, "60", 1, INK, True)
    elif key == "flood":
        _sky(cv, x, y, w, h, (120, 140, 165), (150, 170, 190))
        for i in range(8):
            cv.line(x + 6 + i * 14, y + 2, x + 2 + i * 14, y + 10, (200, 220, 240))
        cv.rect(x, y + h // 2, w, h // 2, (50, 110, 170))
        cv.rect(x + 8, y + h // 2 - 14, 30, 14, (240, 220, 180))
        cv.tri(x + 4, y + h // 2 - 14, x + 42, y + h // 2 - 14, x + 23, y + h // 2 - 26, (180, 60, 50))
        cv.rect(x + w // 2, y + h - 12, 34, 8, (200, 60, 60))
        cv.rect(x + w // 2 + 4, y + h - 18, 24, 6, (200, 60, 60))
        cv.line(x + w - 16, y + h // 2 - 4, x + w - 10, y + h // 2 - 20, (30, 130, 60))
        cv.line(x + w - 10, y + h // 2 - 20, x + w - 20, y + h // 2 - 16, (30, 130, 60))
    elif key == "saudi":
        _sky(cv, x, y, w, h, (240, 200, 130), (230, 180, 110))
        for i, bh in enumerate((h // 3, h // 2, h // 4)):
            _building(cv, x + 6 + i * (w // 4), y + h - 12 - bh, w // 6, bh, (180, 160, 120), (255, 240, 180))
        cv.line(x + w // 2, y + 6, x + w // 2 + 16, y + h // 2, (255, 255, 255))
        cv.line(x + w // 2 + 16, y + h // 2, x + w // 2 + 22, y + h // 2 + 8, (255, 140, 0))
        cv.disc(x + w // 2 + 24, y + h // 2 + 10, 4, (255, 140, 0))
        cv.disc(x + w // 2 + 26, y + h // 2 + 12, 2, (255, 220, 60))
        cv.line(x + w // 3, y + h - 12, x + w // 3 + 10, y + h // 2 + 6, (255, 255, 255))
    elif key == "bank":
        _sky(cv, x, y, w, h, SKY, (215, 225, 235))
        cv.tri(x + 8, y + 10, x + w - 8, y + 10, x + w // 2, y + 2, (200, 190, 160))
        for i in range(4):
            cx0 = x + 14 + i * (w - 28) // 4
            cv.rect(cx0, y + 12, 6, h - 24, (240, 235, 220))
        cv.rect(x + 6, y + h - 12, w - 12, 12, (160, 150, 130))
        cv.disc(x + w - 16, y + 12, 7, GOLD)
        cv.text(x + w - 19, y + 9, "$", 1, INK, True)
        cv.text(x + 6, y + h - 11, "6.25%", 1, NAVY, True)
    elif key == "royal":
        _sky(cv, x, y, w, h, SKY, (215, 225, 235))
        _flag(cv, x + w // 5, y + 4, 18, 12, "uk")
        _flag(cv, x + 3 * w // 5, y + 4, 18, 12, "in")
        cv.rect(x, y + h - 12, w, 12, (150, 40, 40))
        _person(cv, x + w // 3, y + h - 38, 1, NAVY)
        _person(cv, x + 2 * w // 3, y + h - 38, 1, (90, 60, 140))
        cv.line(x + w // 3 + 5, y + h - 30, x + 2 * w // 3 - 5, y + h - 30, (220, 180, 140))
    else:
        cv.rect(x, y, w, h, SKY)


def _badge(cv, x, y, n):
    cv.rect(x, y, 16, 14, RED)
    s = str(n)
    cv.text(x + (16 - text_w(s, 1)) // 2, y + 3, s, 1, (255, 255, 255), True)


def _counts(items):
    rc, fc = {}, {}
    for r, f, _t in items:
        rc[r] = rc.get(r, 0) + 1
        fc[f] = fc.get(f, 0) + 1
    return rc, fc


def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.text(8, 4, "THE WORLD IN ONE PICTURE", 4, INK, True)
    cv.text(8, 38, "THURSDAY 19 NOVEMBER 2026  |  48 STORIES  |  ONE IMAGE", 1, RED, True)
    cv.rect(8, 54, 1008, 2, INK)
    # hero lead 1
    hero = LEADS[0]
    cv.frame(8, 60, 1008, 130, INK)
    draw_scene(cv, "gta", 9, 61, 500, 128)
    _badge(cv, 9, 61, 1)
    tx = 520
    cv.text(tx, 68, hero["kicker"], 1, RED, True)
    y = cv.text_lines(tx, 82, wrap(hero["head"], 480, 3), 3, INK, True, lh=26)
    y = cv.text_lines(tx, y + 4, wrap(hero["deck"], 480, 1), 1, INK, False, lh=9)
    cv.text(tx, y + 6, "INSIDE: 12 MORE LEADS - BY THE NUMBERS - MAP - 35 BRIEFS", 1, GREY, True)
    # lead grid: 12 cards, 3 rows x 4
    cw, ch, gx, gy = 246, 124, 8, 6
    for idx, lead in enumerate(LEADS[1:]):
        r, c = divmod(idx, 4)
        x = 8 + c * (cw + gx)
        yy = 196 + r * (ch + gy)
        cv.frame(x, yy, cw, ch, INK)
        draw_scene(cv, lead["scene"], x + 1, yy + 1, cw - 2, 44)
        _badge(cv, x + 1, yy + 1, lead["n"])
        cv.text(x + 5, yy + 49, lead["kicker"], 1, RED, True)
        hy = cv.text_lines(x + 5, yy + 60, wrap(lead["head"], cw - 10, 2), 2, INK, True, lh=15)
        cv.text_lines(x + 5, hy + 1, wrap(lead["deck"], cw - 10, 1)[:1], 1, INK, False, lh=9)
    # numbers strip
    ny = 584
    bw = 166
    for i, (val, lab) in enumerate(NUMBERS):
        x = 8 + i * (bw + 4)
        cv.frame(x, ny, bw, 46, INK)
        cv.text(x + 6, ny + 5, val, 2, RED, True)
        cv.text_lines(x + 6, ny + 24, wrap(lab, bw - 12, 1), 1, INK, False, lh=9)
    # region + field counts
    items = [(ld["region"], ld["field"], "") for ld in LEADS]
    items += [(r, f, t) for r, f, t in BRIEFS]
    rc, fc = _counts(items)
    ry = 636
    cv.text(8, ry, "REGIONS", 1, RED, True)
    rx = 70
    for reg in REGION_ORDER:
        s = "%s %d" % (REGION_LABEL[reg], rc.get(reg, 0))
        rx = cv.text(rx, ry, s, 1, INK, True) + 12
    fy = 650
    cv.text(8, fy, "FIELDS", 1, RED, True)
    fx = 70
    for fld in FIELD_ORDER:
        if fc.get(fld, 0) == 0:
            continue
        s = "%s %d" % (fld, fc.get(fld, 0))
        cv.rect(fx, fy + 1, 6, 6, FIELD_COLOR[fld])
        fx = cv.text(fx + 9, fy, s, 1, INK, True) + 12
    # bottom: map + briefs
    by = 666
    cv.text(8, by, "WHERE THE NEWS HAPPENED", 1, RED, True)
    cv.text(316, by, "THE DAY IN BRIEF - 35 MORE STORIES", 1, RED, True)
    cv.rect(8, by + 12, 1008, 1, INK)
    mx, my, mw, mh = 8, 682, 298, 266
    cv.frame(mx, my, mw, mh, INK)
    blobs = [(-100, 48, 38, 18), (-60, -12, 13, 20), (12, 52, 20, 12),
             (18, 4, 20, 26), (95, 45, 48, 22), (134, -25, 16, 10)]
    for gy2 in range(my + 4, my + mh - 4, 5):
        for gx2 in range(mx + 4, mx + mw - 4, 5):
            lon = (gx2 - mx) / mw * 360 - 180
            lat = 90 - (gy2 - my) / mh * 180
            for (lc, tc, lr, tr) in blobs:
                if ((lon - lc) / lr) ** 2 + ((lat - tc) / tr) ** 2 <= 1:
                    cv.rect(gx2, gy2, 2, 2, NAVY)
                    break
    for lead in LEADS:
        lon, lat = lead["pin"]
        px = mx + int((lon + 180) / 360 * mw)
        py = my + int((90 - lat) / 180 * mh)
        cv.disc(px, py, 8, RED)
        cv.frame(px - 8, py - 8, 16, 16, (255, 255, 255))
        s = str(lead["n"])
        cv.text(px - text_w(s, 1) // 2, py - 3, s, 1, (255, 255, 255), True)
    cols = [BRIEFS[:18], BRIEFS[18:]]
    for ci, col in enumerate(cols):
        bx = 316 + ci * 354
        yy = by + 18
        for _r, _f, t in col:
            cv.text(bx, yy, t, 1, INK, False)
            yy += 14
    # footer
    fy2 = 954
    cv.rect(8, fy2, 1008, 2, INK)
    y = cv.text_lines(8, fy2 + 6, wrap(
        "DATE CHECK: EVERY STORY ON THIS PAGE HAPPENED, OR WAS FIRST REPORTED, "
        "ON THURSDAY 19 NOVEMBER 2026.", 1008, 1), 1, RED, True, lh=9)
    y = cv.text_lines(8, y + 2, wrap(FOOTER_LEFT_OUT, 1008, 1), 1, INK, False, lh=9)
    cv.text_lines(8, y + 2, wrap(SOURCES, 1008, 1), 1, GREY, False, lh=9)
    return cv


def main():
    cv = build()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    base = outdir if outdir else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png_bytes(W, H, cv.px))
    print("wrote", path)


if __name__ == "__main__":
    main()
