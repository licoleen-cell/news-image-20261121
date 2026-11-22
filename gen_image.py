#!/usr/bin/env python3
"""Render image.png: 10-story pictogram grid front page (candidate D).

Deterministic: fixed fonts, fixed geometry, no randomness, no clock reads.
Layout per cell: pictogram left, headline right, sub-headline full width below.
"""
import itertools
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
SS = 4

PAPER = "#FFFFFF"
INK = "#12151A"
SUBINK = "#2E3540"
BORDER = "#D8D3C9"
RED = "#B3122B"

FONT_SUB = "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf"
FONT_HEAD = "/usr/share/fonts/truetype/noto/NotoSansDisplay-ExtraCondensedBold.ttf"
FONT_DATE = "/usr/share/fonts/truetype/noto/NotoSansCondensed-Bold.ttf"

DATE = "SATURDAY 21 NOVEMBER 2026"

MARGIN = 10
GAP = 8
CELL_W = 498
CELL_H = 179
GRID_TOP = 88

PAD_L = 14
ICON = 52
HEAD_X = PAD_L + ICON + 14
HEAD_W = CELL_W - HEAD_X - 8
HEAD_TOP = 8
HEAD_H = 112
SUB_TOP = 126
SUB_W = CELL_W - 2 * PAD_L - 8
LH = 1.04
HEAD_STROKE = 0
SUB_STROKE = 0

STORIES = [
    dict(words="IRAN CLAIMS STRIKES IN BAHRAIN".split(),
         sub="Radar claim; no one hurt", accent="#B3122B", icon="strike"),
    dict(words="BOY, 7, KILLED IN KRYVYI RIH".split(),
         sub="Friday: 2 dead, dozens hurt", accent="#1D4ED8", icon="teddy"),
    dict(words="RUSSIAN SHIP ABLAZE".split(),
         sub="Sparta II hit; 16 crew saved", accent="#C2410C", icon="ship"),
    dict(words="MEXICO CAPTURES EL CHAPO ISIDRO".split(),
         sub="Friday raid: 11 dead", accent="#5B21B6", icon="cuffs"),
    dict(words="CLIMATE TALKS DEADLOCKED".split(),
         sub="Past deadline; fossil text cut", accent="#0F766E", icon="climate"),
    dict(words="NASDAQ ERASES 2026 GAINS".split(),
         sub="S&P -3.7%; Nasdaq -5.3%", accent="#111827", icon="chart"),
    dict(words="TRUMP, XI, PUTIN AT APEC".split(),
         sub="Nov 19 summit; 'my friend'", accent="#0C4A6E", icon="leaders"),
    dict(words="MOSQUITOES BEAT DENGUE".split(),
         sub="Wolbachia cuts dengue 69%", accent="#4D7C0F", icon="mosquito"),
    dict(words="QUAKE SHAKES PERU ANDES".split(),
         sub="Magnitude 6.7; Friday, Junin", accent="#B45309", icon="quake"),
    dict(words="BITCOIN CRASHES, REBOUNDS".split(),
         sub="$55.3K low; back above $60K", accent="#B7791F", icon="bitcoin"),
]


def rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return tuple(int(round(ca[i] * (1 - t) + cb[i] * t)) for i in range(3))


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def text_w(text, font):
    return _MEASURE.textlength(text, font=font)


def best_split(words, font, nlines):
    best = None
    for cuts in itertools.combinations(range(1, len(words)), nlines - 1):
        idx = (0,) + cuts + (len(words),)
        lines = [" ".join(words[idx[i]:idx[i + 1]]) for i in range(nlines)]
        width = max(text_w(line, font) for line in lines)
        if best is None or width < best[0] - 1e-9:
            best = (width, lines)
    return best


def fits(words, font, width, height):
    lh = round(font.size * LH)
    for nlines in (2, 3):
        if nlines > len(words):
            continue
        w, _ = best_split(words, font, nlines)
        if w <= width and lh * nlines <= height:
            return True
    return False


def layout_headline(words, size, width, height):
    font = ImageFont.truetype(FONT_HEAD, size)
    lh = round(size * LH)
    for nlines in (2, 3):
        if nlines > len(words):
            continue
        w, lines = best_split(words, font, nlines)
        if w <= width and lh * nlines <= height:
            return font, lines, lh
    raise RuntimeError("headline does not fit at %dpx: %r" % (size, words))


def fit_headline_size(width, height):
    size = 36
    for candidate in range(36, 96):
        font = ImageFont.truetype(FONT_HEAD, candidate)
        if all(fits(st["words"], font, width, height) for st in STORIES):
            size = candidate
    return size


def fit_sub_size(sub, width):
    for size in (40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24):
        if text_w(sub, ImageFont.truetype(FONT_SUB, size)) <= width:
            return size
    raise RuntimeError("sub does not fit: %r" % (sub,))


class Unit:
    """Draw helper using 0..1 coordinates inside a square."""

    def __init__(self, draw, x, y, s):
        self.d = draw
        self.x, self.y, self.s = x, y, s

    def p(self, ux, uy):
        return (self.x + ux * self.s, self.y + uy * self.s)

    def box(self, x0, y0, x1, y1):
        return [self.x + x0 * self.s, self.y + y0 * self.s,
                self.x + x1 * self.s, self.y + y1 * self.s]

    def w(self, v):
        return max(1, int(round(v * self.s)))

    def poly(self, pts, fill):
        self.d.polygon([self.p(*q) for q in pts], fill=fill)

    def ell(self, x0, y0, x1, y1, fill=None, outline=None, width=0):
        self.d.ellipse(self.box(x0, y0, x1, y1), fill=fill,
                       outline=outline, width=width)


def ic_strike(u, ac):
    """Missile on a descending path into a red impact burst."""
    d = u.d
    u.poly([(0.04, 0.14), (0.50, 0.42), (0.44, 0.55), (0.00, 0.27)], "#333B45")
    u.poly([(0.44, 0.55), (0.50, 0.42), (0.58, 0.48), (0.52, 0.60)], ac)
    u.poly([(0.02, 0.12), (0.14, 0.19), (0.06, 0.28)], "#5A6470")
    u.poly([(0.05, 0.31), (0.16, 0.37), (0.09, 0.46)], "#5A6470")
    star = []
    for i in range(16):
        ang = math.pi * 2 * i / 16 - math.pi / 2
        r = 0.32 if i % 2 == 0 else 0.15
        star.append((0.70 + r * math.cos(ang), 0.60 + r * math.sin(ang)))
    u.poly(star, ac)
    u.ell(0.62, 0.52, 0.78, 0.68, fill="#FFE7A8")


def ic_teddy(u, ac):
    """Teddy bear: the standard symbol for a child victim."""
    d = u.d
    u.ell(0.20, 0.02, 0.40, 0.22, fill="#7A4B22")
    u.ell(0.60, 0.02, 0.80, 0.22, fill="#7A4B22")
    u.ell(0.28, 0.06, 0.72, 0.50, fill="#A9743F")
    u.ell(0.40, 0.27, 0.60, 0.47, fill="#EAD6B8")
    u.ell(0.455, 0.29, 0.545, 0.38, fill="#2A1C10")
    u.ell(0.375, 0.19, 0.445, 0.26, fill="#2A1C10")
    u.ell(0.555, 0.19, 0.625, 0.26, fill="#2A1C10")
    u.ell(0.14, 0.48, 0.32, 0.72, fill="#7A4B22")
    u.ell(0.68, 0.48, 0.86, 0.72, fill="#7A4B22")
    u.ell(0.30, 0.44, 0.70, 0.94, fill="#A9743F")
    u.ell(0.40, 0.57, 0.60, 0.82, fill="#EAD6B8")
    u.ell(0.24, 0.80, 0.46, 0.99, fill="#7A4B22")
    u.ell(0.54, 0.80, 0.76, 0.99, fill="#7A4B22")


def ic_ship(u, ac):
    """Cargo ship with flames and smoke: Russian vessel ablaze."""
    d = u.d
    d.rectangle(u.box(0.0, 0.86, 1.0, 0.97), fill="#2C6FA8")
    u.poly([(0.03, 0.60), (0.97, 0.60), (0.85, 0.87), (0.15, 0.87)], "#25313F")
    d.rectangle(u.box(0.30, 0.44, 0.70, 0.60), fill="#EDE7DA")
    for wx in (0.34, 0.45, 0.56):
        d.rectangle(u.box(wx, 0.48, wx + 0.06, 0.56), fill="#4A5560")
    u.poly([(0.34, 0.44), (0.40, 0.16), (0.45, 0.32), (0.50, 0.04),
            (0.56, 0.30), (0.62, 0.18), (0.66, 0.44)], "#EE7A1E")
    u.poly([(0.40, 0.44), (0.44, 0.28), (0.48, 0.36), (0.51, 0.18),
            (0.55, 0.34), (0.59, 0.28), (0.61, 0.44)], "#F7B733")
    u.ell(0.68, 0.12, 0.86, 0.30, fill="#8C959F")
    u.ell(0.76, 0.02, 0.94, 0.20, fill="#A8B1B9")


def ic_cuffs(u, ac):
    """Two linked handcuffs: arrest of a cartel boss."""
    d = u.d
    d.ellipse(u.box(0.02, 0.24, 0.48, 0.80), outline="#39404A", width=u.w(0.10))
    d.ellipse(u.box(0.52, 0.24, 0.98, 0.80), outline=ac, width=u.w(0.10))
    for cx in (0.44, 0.50, 0.56):
        d.ellipse(u.box(cx - 0.042, 0.44, cx + 0.042, 0.58), fill="#39404A")
    d.rectangle(u.box(0.34, 0.10, 0.42, 0.24), fill="#39404A")
    d.rectangle(u.box(0.58, 0.10, 0.66, 0.24), fill="#39404A")


def ic_climate(u, ac):
    """Globe with landmasses plus a red thermometer: climate deadlock."""
    d = u.d
    u.ell(0.00, 0.10, 0.68, 0.82, fill="#8EC5E8")
    u.poly([(0.08, 0.32), (0.26, 0.22), (0.40, 0.30), (0.34, 0.46),
            (0.14, 0.48), (0.04, 0.40)], "#2F6B37")
    u.poly([(0.30, 0.56), (0.48, 0.48), (0.60, 0.58), (0.52, 0.72),
            (0.32, 0.72), (0.24, 0.64)], "#2F6B37")
    d.arc(u.box(0.04, 0.16, 0.64, 0.76), 100, 260, fill="#FFFFFF", width=u.w(0.016))
    d.rounded_rectangle(u.box(0.74, 0.06, 0.92, 0.66), radius=u.w(0.09),
                        fill="#FFFFFF", outline="#39404A", width=u.w(0.024))
    d.rounded_rectangle(u.box(0.795, 0.30, 0.865, 0.60), radius=u.w(0.035), fill=ac)
    d.ellipse(u.box(0.70, 0.56, 0.96, 0.84), fill=ac, outline="#39404A", width=u.w(0.024))


def ic_chart(u, ac):
    """Falling line on a light panel: market erase."""
    d = u.d
    d.rounded_rectangle(u.box(0.00, 0.06, 1.00, 0.94), radius=u.w(0.07),
                        fill="#F2F4F7", outline="#39404A", width=u.w(0.028))
    for gy in (0.30, 0.50, 0.70):
        d.line([u.p(0.10, gy), u.p(0.90, gy)], fill="#B9C1CB", width=u.w(0.014))
    pts = [(0.12, 0.24), (0.28, 0.34), (0.40, 0.28), (0.54, 0.50),
           (0.66, 0.58), (0.76, 0.54), (0.88, 0.80)]
    d.line([u.p(*q) for q in pts], fill=ac, width=u.w(0.075), joint="curve")
    u.poly([(0.97, 0.90), (0.74, 0.78), (0.92, 0.66)], ac)


def ic_leaders(u, ac):
    """Three separated figures above a thin podium: Trump, Xi, Putin at APEC."""
    d = u.d
    for col, cx, top in (("#4C5A6B", 0.145, 0.20), ("#8A3B3B", 0.50, 0.08),
                         ("#2F5C46", 0.855, 0.20)):
        u.ell(cx - 0.085, top, cx + 0.085, top + 0.175, fill=col)
        d.rectangle(u.box(cx - 0.125, top + 0.185, cx + 0.125, 0.80), fill=col)
    d.rectangle(u.box(0.00, 0.80, 1.00, 0.87), fill="#B99A6B")
    d.rectangle(u.box(0.00, 0.87, 1.00, 0.94), fill="#7E5F35")


def ic_mosquito(u, ac):
    """Mosquito: Wolbachia trial cuts dengue."""
    d = u.d
    u.ell(0.26, 0.10, 0.62, 0.34, fill="#9CC3E2", outline="#4E7FA8", width=u.w(0.016))
    u.ell(0.38, 0.05, 0.74, 0.29, fill="#BFD9EE", outline="#4E7FA8", width=u.w(0.016))
    u.poly([(0.18, 0.44), (0.58, 0.53), (0.72, 0.46), (0.58, 0.36), (0.24, 0.33)], "#1F242B")
    u.ell(0.64, 0.36, 0.82, 0.54, fill="#1F242B")
    d.line([u.p(0.81, 0.44), u.p(0.99, 0.30)], fill="#1F242B", width=u.w(0.035))
    for a, b in (((0.27, 0.46), (0.14, 0.76)), ((0.39, 0.50), (0.30, 0.82)),
                 ((0.50, 0.52), (0.50, 0.84)), ((0.61, 0.51), (0.72, 0.80))):
        d.line([u.p(*a), u.p(*b)], fill="#1F242B", width=u.w(0.028))
    d.ellipse(u.box(0.93, 0.24, 1.0, 0.33), fill=ac)


def ic_quake(u, ac):
    """Seismograph trace with an epicentre: Peru earthquake."""
    d = u.d
    d.rounded_rectangle(u.box(0.00, 0.10, 1.00, 0.90), radius=u.w(0.05),
                        fill="#FFFFFF", outline="#39404A", width=u.w(0.026))
    for gy in (0.33, 0.67):
        d.line([u.p(0.06, gy), u.p(0.94, gy)], fill="#C6CCD4", width=u.w(0.012))
    pts = [(0.06, 0.50), (0.20, 0.50), (0.26, 0.22), (0.35, 0.78),
           (0.43, 0.32), (0.52, 0.68), (0.60, 0.46), (0.68, 0.50), (0.94, 0.50)]
    d.line([u.p(*q) for q in pts], fill="#1B2430", width=u.w(0.042), joint="curve")
    d.ellipse(u.box(0.63, 0.41, 0.75, 0.53), fill=ac)
    for r in (0.10, 0.17):
        d.arc(u.box(0.69 - r, 0.47 - r, 0.69 + r, 0.47 + r), 200, 340,
              fill=ac, width=u.w(0.018))


def ic_bitcoin(u, ac):
    """Gold coin with a dark B and a rebound arrow."""
    d = u.d
    u.ell(0.02, 0.00, 0.94, 0.92, fill="#E8B33A", outline="#8A5F12", width=u.w(0.04))
    d.rectangle(u.box(0.32, 0.20, 0.41, 0.72), fill="#3A2A08")
    d.rounded_rectangle(u.box(0.38, 0.22, 0.63, 0.45), radius=u.w(0.12), fill="#3A2A08")
    d.rounded_rectangle(u.box(0.38, 0.47, 0.66, 0.70), radius=u.w(0.12), fill="#3A2A08")
    d.rectangle(u.box(0.42, 0.28, 0.56, 0.39), fill="#E8B33A")
    d.rectangle(u.box(0.42, 0.53, 0.59, 0.64), fill="#E8B33A")
    d.rectangle(u.box(0.28, 0.11, 0.35, 0.21), fill="#3A2A08")
    d.rectangle(u.box(0.28, 0.71, 0.35, 0.81), fill="#3A2A08")
    pts = [(0.06, 0.99), (0.30, 0.86), (0.48, 0.94), (0.74, 0.74)]
    d.line([u.p(*q) for q in pts], fill="#1F6B33", width=u.w(0.06), joint="curve")
    u.poly([(0.85, 0.65), (0.66, 0.68), (0.78, 0.82)], "#1F6B33")


ICONS = {
    "strike": ic_strike,
    "teddy": ic_teddy,
    "ship": ic_ship,
    "cuffs": ic_cuffs,
    "climate": ic_climate,
    "chart": ic_chart,
    "leaders": ic_leaders,
    "mosquito": ic_mosquito,
    "quake": ic_quake,
    "bitcoin": ic_bitcoin,
}


def build():
    head_size = fit_headline_size(HEAD_W, HEAD_H)

    layouts = []
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = MARGIN + col * (CELL_W + GAP)
        y0 = GRID_TOP + row * (CELL_H + GAP)
        font, lines, lh = layout_headline(story["words"], head_size, HEAD_W, HEAD_H)
        layouts.append(dict(story=story, x=x0, y=y0, font=font, lines=lines, lh=lh,
                            sub_size=fit_sub_size(story["sub"], SUB_W)))

    img = Image.new("RGB", (W * SS, H * SS), PAPER)
    d = ImageDraw.Draw(img)

    d.rectangle([10 * SS, 6 * SS, (W - 10) * SS, 8 * SS], fill=INK)
    d.rectangle([10 * SS, 80 * SS, (W - 10) * SS, 85 * SS], fill=RED)

    for lay in layouts:
        x0, y0 = lay["x"], lay["y"]
        accent = lay["story"]["accent"]
        tint = mix(accent, PAPER, 0.90)
        d.rounded_rectangle([x0 * SS, y0 * SS, (x0 + CELL_W) * SS, (y0 + CELL_H) * SS],
                            radius=8 * SS, fill=PAPER, outline=BORDER, width=2 * SS)
        d.rectangle([(x0 + 6) * SS, (y0 + 10) * SS, (x0 + 12) * SS, (y0 + CELL_H - 10) * SS],
                    fill=accent)
        icon_y = y0 + (SUB_TOP - 6 - ICON) // 2
        d.rounded_rectangle([(x0 + PAD_L) * SS, icon_y * SS,
                             (x0 + PAD_L + ICON) * SS, (icon_y + ICON) * SS],
                            radius=min(18, ICON // 3) * SS, fill=tint)
        ICONS[lay["story"]["icon"]](Unit(d, (x0 + PAD_L) * SS, icon_y * SS, ICON * SS), accent)

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(img)

    date_font = ImageFont.truetype(FONT_SUB, 62)
    while text_w(DATE, date_font) > W - 44 and date_font.size > 40:
        date_font = ImageFont.truetype(FONT_SUB, date_font.size - 1)
    d.text((W // 2, 44), DATE, font=date_font, fill=INK, anchor="mm")

    for lay in layouts:
        x0, y0 = lay["x"], lay["y"]
        block_h = lay["lh"] * len(lay["lines"])
        top = y0 + HEAD_TOP + (HEAD_H - block_h) // 2
        for i, line in enumerate(lay["lines"]):
            d.text((x0 + HEAD_X, top + i * lay["lh"]), line,
                   font=lay["font"], fill=INK, stroke_width=HEAD_STROKE,
                   stroke_fill=INK)
        sub_font = ImageFont.truetype(FONT_SUB, lay["sub_size"])
        d.text((x0 + PAD_L, y0 + SUB_TOP), lay["story"]["sub"], font=sub_font,
               fill=SUBINK, stroke_width=SUB_STROKE, stroke_fill=SUBINK)

    words = len(DATE.split())
    for st in STORIES:
        words += len(st["words"]) + len(st["sub"].split())
    if words > 110:
        raise RuntimeError("too many words: %d" % words)

    img.save("image.png", format="PNG", optimize=False, compress_level=9)
    print("headline %dpx, icon %dpx, head width %d, sub width %d" %
          (head_size, ICON, HEAD_W, SUB_W))
    for lay in layouts:
        print("  %-40s sub %dpx" % (" / ".join(lay["lines"]), lay["sub_size"]))
    print("words:", words)
    print("image.png:", img.size, os.path.getsize("image.png"), "bytes")


if __name__ == "__main__":
    build()
