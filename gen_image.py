#!/usr/bin/env python3
"""Front page as a pictogram grid: eight stories, one bold icon each.

Renders a deterministic 1024x1024 PNG (image.png) with Pillow.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

PAPER = (245, 242, 234)
CARD = (255, 255, 255)
CARD_EDGE = (196, 187, 171)
INK = (14, 14, 14)
INK_SOFT = (52, 49, 45)
GOLD = (255, 196, 56)
LEAD_RED = (176, 42, 31)

SS = 4  # supersampling factor for icon shapes
WORD_GAP = 1.0  # extra px between words, keeps words distinct when scaled

FONTS = {
    "head": "/usr/share/fonts/truetype/noto/NotoSans-CondensedExtraBold.ttf",
    "deck": "/usr/share/fonts/truetype/noto/NotoSans-CondensedSemiBold.ttf",
    "deck_b": "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf",
    "sym": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
}

STORIES = [
    {
        "head": "IRAN CLAIMS STRIKES IN BAHRAIN",
        "deck": "IRGC claims US radars hit; Bahrain: site ablaze, no one hurt.",
        "icon": "missile",
        "color": (166, 38, 28),
        "lead": True,
    },
    {
        "head": "RUSSIAN SHIP ABLAZE",
        "deck": "Drones hit Sparta II; 16 crew saved.",
        "icon": "ship",
        "color": (24, 56, 84),
        "lead": False,
    },
    {
        "head": "CLIMATE TALKS DEADLOCKED",
        "deck": "Past deadline; fossil-fuel text dropped.",
        "icon": "globe",
        "color": (12, 92, 84),
        "lead": False,
    },
    {
        "head": "BITCOIN CRASHES, REBOUNDS",
        "deck": "$55,300 low; back above $60,000.",
        "icon": "bitcoin",
        "color": (140, 82, 14),
        "lead": False,
    },
    {
        "head": "MOSQUITOES BEAT DENGUE",
        "deck": "Wolbachia cuts dengue 69% in Brazil trial.",
        "icon": "mosquito",
        "color": (36, 88, 44),
        "lead": False,
    },
    {
        "head": "BOY, 7, KILLED IN KRYVYI RIH",
        "deck": "Friday: 2 dead, dozens hurt.",
        "icon": "building",
        "color": (54, 58, 68),
        "lead": False,
    },
    {
        "head": "MEXICO CAPTURES EL CHAPO ISIDRO",
        "deck": "Friday raid: 11 dead.",
        "icon": "cuffs",
        "color": (42, 50, 94),
        "lead": False,
    },
    {
        "head": "QUAKE SHAKES PERU ANDES",
        "deck": "Magnitude 6.7; Friday in Jun\u00edn.",
        "icon": "quake",
        "color": (114, 66, 26),
        "lead": False,
    },
]

EMPHASIS = ("IRGC", "Friday")

CFG = {
    "margin": 8,
    "gutter": 6,
    "pad": 6,
    "masthead": 60,
    "icon": 88,
    "head_ladder": (62, 56, 50, 44),
    "deck_size": 28,
    "radius": 8,
    "gap": 12,
}


def font(kind, size):
    return ImageFont.truetype(FONTS[kind], size)


# --------------------------------------------------------------------------
# icons: drawn in a 100x100 unit box, white on the story colour


class Pen:
    def __init__(self, img, bg):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.k = img.width / 100.0
        self.bg = bg

    def _p(self, pts):
        return [(x * self.k, y * self.k) for x, y in pts]

    def poly(self, pts, fill):
        self.d.polygon(self._p(pts), fill=fill)

    def rrect(self, box, r, fill):
        x0, y0, x1, y1 = box
        self.d.rounded_rectangle(
            [x0 * self.k, y0 * self.k, x1 * self.k, y1 * self.k],
            radius=max(1, r * self.k), fill=fill)

    def disc(self, c, r, fill):
        cx, cy = c
        self.d.ellipse([(cx - r) * self.k, (cy - r) * self.k,
                        (cx + r) * self.k, (cy + r) * self.k], fill=fill)

    def ring(self, c, r, w, fill):
        cx, cy = c
        self.d.ellipse([(cx - r) * self.k, (cy - r) * self.k,
                        (cx + r) * self.k, (cy + r) * self.k],
                       outline=fill, width=max(1, int(round(w * self.k))))

    def oval(self, box, w, fill):
        x0, y0, x1, y1 = box
        self.d.ellipse([x0 * self.k, y0 * self.k, x1 * self.k, y1 * self.k],
                       outline=fill, width=max(1, int(round(w * self.k))))

    def line(self, pts, w, fill):
        self.d.line(self._p(pts), fill=fill,
                    width=max(1, int(round(w * self.k))), joint="curve")

    def star(self, c, r_out, r_in, n, fill, rot=0.0):
        pts = []
        for i in range(n * 2):
            ang = rot + i * math.pi / n
            r = r_out if i % 2 == 0 else r_in
            pts.append((c[0] + r * math.cos(ang), c[1] + r * math.sin(ang)))
        self.poly(pts, fill)


def icon_missile(p):
    p.star((80, 18), 17, 7.5, 8, GOLD, rot=0.25)
    # body: nose cone, shaft, tail fins, exhaust
    p.poly([(50, 4), (60, 24), (60, 58), (40, 58), (40, 24)], CARD)
    p.poly([(40, 34), (24, 56), (40, 50)], CARD)
    p.poly([(60, 34), (76, 56), (60, 50)], CARD)
    p.poly([(42, 58), (58, 58), (50, 86)], GOLD)
    p.poly([(47, 58), (53, 58), (50, 74)], CARD)


def icon_ship(p):
    # flames along the deck, hull, cabin, mast, waves beneath
    for x in (22, 36, 64, 78):
        p.poly([(x - 9, 58), (x + 9, 58), (x + 3, 34), (x - 3, 34)], GOLD)
        p.poly([(x - 4, 58), (x + 4, 58), (x, 44)], p.bg)
    p.poly([(8, 58), (92, 58), (81, 78), (19, 78)], CARD)
    p.poly([(19, 78), (81, 78), (75, 68), (25, 68)], p.bg)
    p.rrect((36, 38, 64, 58), 3, CARD)
    p.rrect((42, 44, 58, 52), 1, p.bg)
    p.line([(50, 24), (50, 38)], 4, CARD)
    p.disc((50, 21), 4, CARD)
    p.line([(2, 88), (14, 93), (26, 88), (38, 93), (50, 88), (62, 93),
            (74, 88), (86, 93), (98, 88)], 5, CARD)
    p.disc((22, 24), 7, GOLD)
    p.disc((35, 13), 5, GOLD)


def icon_globe(p):
    p.ring((36, 56), 27, 7, CARD)
    p.line([(9, 56), (63, 56)], 5.5, CARD)
    p.oval((21, 29, 51, 83), 5, CARD)
    p.oval((9, 41, 63, 71), 4.5, CARD)
    p.rrect((76, 8, 90, 56), 7, GOLD)
    p.disc((83, 70), 7, GOLD)


def icon_bitcoin(p):
    f = font("sym", int(56 * p.k))
    p.d.text((46 * p.k, 40 * p.k), "\u20bf", font=f, fill=CARD, anchor="mm")
    p.line([(14, 30), (34, 50), (50, 64), (66, 44), (86, 20)], 7, GOLD)
    p.poly([(86, 20), (70, 22), (85, 36)], GOLD)


def icon_mosquito(p):
    p.oval((24, 16, 48, 38), 3.5, GOLD)
    p.oval((52, 16, 76, 38), 3.5, GOLD)
    p.disc((50, 27), 8, CARD)
    p.line([(50, 19), (50, 3)], 3.5, CARD)
    p.line([(44, 22), (35, 8)], 3, CARD)
    p.line([(56, 22), (65, 8)], 3, CARD)
    p.d.ellipse([42 * p.k, 34 * p.k, 58 * p.k, 78 * p.k], fill=CARD)
    for y in (45, 54, 63):
        p.line([(42.5, y), (57.5, y)], 3, p.bg)
    for dy in (-2, 9):
        p.line([(43, 40 + dy), (26, 32 + dy), (16, 45 + dy)], 3.5, CARD)
        p.line([(57, 40 + dy), (74, 32 + dy), (84, 45 + dy)], 3.5, CARD)
    p.line([(45, 66), (28, 72), (21, 90)], 3.5, CARD)
    p.line([(55, 66), (72, 72), (79, 90)], 3.5, CARD)
    p.line([(50, 78), (50, 95)], 3, CARD)


def icon_building(p):
    p.poly([(26, 88), (26, 38), (36, 24), (46, 38), (56, 22), (64, 34),
            (74, 30), (74, 88)], CARD)
    for row in range(3):
        for col in range(4):
            x = 31 + col * 11
            y = 44 + row * 13
            p.rrect((x, y, x + 7, y + 7), 1, p.bg)
    p.line([(47, 28), (44, 46), (51, 60), (46, 76)], 3.5, p.bg)
    p.poly([(4, 88), (24, 88), (14, 70)], GOLD)
    p.poly([(76, 88), (96, 88), (85, 72)], GOLD)
    p.poly([(10, 70), (25, 70), (17, 60)], GOLD)
    p.disc((16, 55), 5, GOLD)
    p.disc((86, 64), 4.5, GOLD)


def icon_cuffs(p):
    p.ring((30, 56), 19, 9, CARD)
    p.ring((70, 56), 19, 9, CARD)
    p.rrect((43, 49, 57, 63), 6, GOLD)
    p.ring((50, 56), 4, 3, p.bg)
    p.rrect((24, 42, 34, 60), 2, GOLD)
    p.rrect((66, 42, 76, 60), 2, GOLD)
    p.line([(30, 37), (30, 24)], 5, CARD)
    p.line([(70, 37), (70, 24)], 5, CARD)


def icon_quake(p):
    p.line([(2, 12), (17, 12), (25, 0), (33, 24), (41, 6), (49, 19),
            (57, 2), (65, 21), (74, 12), (98, 12)], 5, GOLD)
    p.poly([(2, 84), (26, 42), (41, 66), (57, 30), (75, 62), (98, 84)], CARD)
    p.line([(45, 84), (40, 69), (49, 59), (42, 49), (51, 38)], 5.5, p.bg)
    p.line([(2, 89), (98, 89)], 5, CARD)


ICONS = {
    "missile": icon_missile,
    "ship": icon_ship,
    "globe": icon_globe,
    "bitcoin": icon_bitcoin,
    "mosquito": icon_mosquito,
    "building": icon_building,
    "cuffs": icon_cuffs,
    "quake": icon_quake,
}


def icon_tile(name, size, bg):
    big = Image.new("RGBA", (size * SS, size * SS), bg + (255,))
    ICONS[name](Pen(big, bg))
    return big.resize((size, size), Image.LANCZOS)


# --------------------------------------------------------------------------
# text


def wrap(words, fonts, width):
    space = fonts[0].getlength(" ") + WORD_GAP
    lines, cur, cur_w = [], [], 0.0
    for word, f in zip(words, fonts):
        ww = f.getlength(word)
        add = ww if not cur else space + ww
        if cur and cur_w + add > width:
            lines.append((cur, cur_w))
            cur, cur_w = [(word, f)], ww
        else:
            cur.append((word, f))
            cur_w += add
    if cur:
        lines.append((cur, cur_w))
    return lines


def faces(story, hs, ds):
    h = font("head", hs)
    d = font("deck", ds)
    db = font("deck_b", ds)
    heads = [h] * len(story["head"].split())
    decks = [db if w.strip(",.;:") in EMPHASIS else d
             for w in story["deck"].split()]
    return heads, decks


def measure(story, hs, ds, text_w):
    heads, decks = faces(story, hs, ds)
    hl = wrap(story["head"].split(), heads, text_w)
    dl = wrap(story["deck"].split(), decks, text_w)
    head_lh = int(round(hs * 1.03))
    deck_lh = int(round(ds * 1.16))
    gap = int(round(hs * 0.16))
    return {
        "head_lines": hl, "deck_lines": dl, "head_lh": head_lh,
        "deck_lh": deck_lh, "gap": gap,
        "height": len(hl) * head_lh + gap + len(dl) * deck_lh,
    }


def draw_lines(d, lines, x, y, lh, fill):
    """Draw wrapped lines; integer positions keep glyphs crisp when scaled."""
    x = int(round(x))
    y = int(round(y))
    for i, (words, _w) in enumerate(lines):
        cx = x
        for j, (word, f) in enumerate(words):
            d.text((cx, y + i * lh), word, font=f, fill=fill)
            gap = f.getlength(" ") + (WORD_GAP if j < len(words) - 1 else 0)
            cx += int(round(f.getlength(word) + gap))
    return y + len(lines) * lh


# --------------------------------------------------------------------------
# page


def text_box(cfg, card_w):
    tx = cfg["pad"] + cfg["icon"] + cfg["gap"]
    return tx, card_w - tx - cfg["pad"]


def masthead(d, cfg):
    d.rectangle([0, 0, W, 6], fill=LEAD_RED)
    date = "SATURDAY 21 NOVEMBER 2026"
    limit = W - 2 * cfg["margin"] - 16
    size = int(cfg["masthead"] * 1.05)
    while size > 24:
        f = font("head", size)
        if f.getlength(date) <= limit:
            break
        size -= 1
    f = font("head", size)
    top = 6 + (cfg["masthead"] - 6 - size) // 2 - 4
    d.text((W // 2, top), date, font=f, fill=INK, anchor="ma")
    base = top + f.getbbox(date)[3]
    d.rectangle([cfg["margin"], base + 3, W - cfg["margin"], base + 6],
                fill=INK)
    d.rectangle([cfg["margin"], base + 9, W - cfg["margin"], base + 10],
                fill=CARD_EDGE)
    return base + 10 + cfg["gutter"]


def rows(cfg, avail, text_w):
    """Row heights sized so every story fits the same headline size.

    Try the ladder from largest to smallest; the first size whose four row
    heights fit the page wins. Each row then gets its own need plus an equal
    share of the slack, so a three-line card never shrinks its neighbours.
    """
    groups = [STORIES[0:2], STORIES[2:4], STORIES[4:6], STORIES[6:8]]
    chosen = None
    for size in cfg["head_ladder"]:
        needs = [max(measure(s, size, cfg["deck_size"], text_w)["height"]
                     for s in group) + 2 * cfg["pad"]
                 for group in groups]
        if sum(needs) <= avail:
            chosen = needs
            break
    if chosen is None:
        chosen = [max(measure(s, cfg["head_ladder"][-1], cfg["deck_size"],
                              text_w)["height"] for s in group) + 2 * cfg["pad"]
                  for group in groups]
    slack = max(0.0, avail - sum(chosen)) / len(chosen)
    return [(g, n + slack) for g, n in zip(groups, chosen)]


def fit_story(story, cfg, text_w, avail_h):
    """Largest ladder size whose block fits, so neighbours stay related."""
    for hs in cfg["head_ladder"]:
        lay = measure(story, hs, cfg["deck_size"], text_w)
        if lay["height"] <= avail_h:
            return lay
    lo = cfg["head_ladder"][-1]
    return measure(story, lo, cfg["deck_size"], text_w)


def build(cfg=CFG):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    top = masthead(d, cfg)
    card_w = (W - 2 * cfg["margin"] - cfg["gutter"]) // 2
    tx, text_w = text_box(cfg, card_w)
    avail = H - 6 - top - 3 * cfg["gutter"]

    y = top
    for pair, row_h in rows(cfg, avail, text_w):
        avail_h = row_h - 2 * cfg["pad"]
        for c, story in enumerate(pair):
            x0 = cfg["margin"] + c * (card_w + cfg["gutter"])
            d.rounded_rectangle(
                [x0, y, x0 + card_w - 1, y + row_h - 1],
                radius=cfg["radius"], fill=CARD, outline=CARD_EDGE, width=1)
            if story["lead"]:
                d.rounded_rectangle(
                    [x0 + 1, y + 1, x0 + card_w - 2, y + 5],
                    radius=2, fill=LEAD_RED)

            icon = min(cfg["icon"], int(row_h - 2 * cfg["pad"]))
            tile = icon_tile(story["icon"], icon, story["color"])
            mask = Image.new("L", (icon, icon), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                [0, 0, icon - 1, icon - 1],
                radius=max(4, cfg["radius"] + 3), fill=255)

            lay = fit_story(story, cfg, text_w, avail_h)
            ty = y + cfg["pad"]
            img.paste(tile.convert("RGB"),
                      (int(x0 + cfg["pad"]),
                       int(y + (row_h - icon) / 2)), mask)
            d = ImageDraw.Draw(img)

            ty = draw_lines(d, lay["head_lines"], x0 + tx, ty,
                            lay["head_lh"], INK)
            draw_lines(d, lay["deck_lines"], x0 + tx, ty + lay["gap"],
                       lay["deck_lh"], INK_SOFT)
        y += row_h + cfg["gutter"]

    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
    img.save(out, format="PNG", optimize=True)
    print("%s %dx%d %d bytes"
          % (os.path.basename(out), img.width, img.height,
             os.path.getsize(out)))


if __name__ == "__main__":
    main()
