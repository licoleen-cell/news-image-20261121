#!/usr/bin/env python3
"""Draw the front page for Saturday 21 November 2026 and save it as image.png.

Every block is measured before it is drawn; the script raises if any block
would overflow, so a successful run means the page is geometrically sound.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 22
CW = W - 2 * M

PAPER = (246, 242, 231)
PANEL = (252, 249, 241)
INK = (16, 19, 24)
MUTED = (74, 79, 88)
HAIR = (201, 194, 178)
NAVY = (20, 36, 61)
RED = (168, 18, 28)

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerif-CondensedBlack.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-CondensedBold.ttf"
SERIF_ITAL = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def text_w(d, text, f, tracking=0.0):
    if not text:
        return 0.0
    return sum(d.textlength(c, font=f) for c in text) + tracking * (len(text) - 1)


def draw_tracked(d, x, y, text, f, fill, tracking=0.0, center=None):
    if center is not None:
        x = center - text_w(d, text, f, tracking) / 2
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tracking


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=f) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def wrap_balanced(d, text, f, maxw, max_lines):
    """Greedy wrap, then re-break to even out line lengths within max_lines.

    Short last lines and very long first lines look like accidents on a printed
    page, so pick the break points that minimise raggedness instead.
    """
    words = text.split()
    if not words:
        return []
    widths = [d.textlength(w, font=f) for w in words]
    space = d.textlength(" ", font=f)

    def cost(start, end):
        w = sum(widths[start:end]) + space * (end - start - 1)
        if w > maxw:
            return None
        return (maxw - w) ** 2

    n = len(words)
    best = {0: (0, [])}
    for end in range(1, n + 1):
        cand = None
        for start in range(end):
            if start not in best:
                continue
            nlines = len(best[start][1]) + 1
            if nlines > max_lines:
                continue
            c = cost(start, end)
            if c is None:
                continue
            total = best[start][0] + c
            if cand is None or total < cand[0]:
                cand = (total, best[start][1] + [(start, end)])
        if cand is not None:
            best[end] = cand
    if n not in best:
        return wrap(d, text, f, maxw)
    return [" ".join(words[s:e]) for s, e in best[n][1]]


def pick_size(d, text, path, maxw, max_lines, sizes, tag):
    """Largest font size whose text fits maxw in at most max_lines lines."""
    for size in sizes:
        f = font(path, size)
        lines = wrap(d, text, f, maxw)
        if len(lines) <= max_lines and all(d.textlength(l, font=f) <= maxw for l in lines):
            return f
    raise SystemExit(f"text does not fit: {tag!r}")


def rule(d, x0, y, x1, colour=INK, weight=1):
    d.rectangle([x0, y, x1, y + weight - 1], fill=colour)


def _star(a, cx, cy, r, fill, core=None, points=8):
    pts = []
    for i in range(points * 2):
        ang = math.radians(i * 180 / points)
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    a.polygon(pts, fill=fill)
    if core:
        a.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28], fill=core)


def _ship(a, x, y, s, hull=(26, 34, 48), fire=True):
    """Small tanker seen from above-ish, with fire on deck."""
    a.polygon([(x, y), (x + s, y), (x + s * 0.9, y + s * 0.30), (x + s * 0.1, y + s * 0.30)], fill=hull)
    a.rectangle([x + s * 0.62, y - s * 0.16, x + s * 0.88, y], fill=(40, 50, 68))
    if fire:
        a.polygon([(x + s * 0.30, y + s * 0.02), (x + s * 0.40, y - s * 0.34),
                   (x + s * 0.50, y + s * 0.02)], fill=(255, 150, 50))
        a.polygon([(x + s * 0.44, y + s * 0.02), (x + s * 0.53, y - s * 0.22),
                   (x + s * 0.60, y + s * 0.02)], fill=(255, 205, 110))


def lead_art(img, d, x0, y0, w, h):
    """Stylised map of the Gulf: Iran to the north, Bahrain hit, tankers at Hormuz."""
    S = 3
    art = Image.new("RGB", (w * S, h * S), (10, 22, 40))
    a = ImageDraw.Draw(art)

    def P(*pairs):
        return [(x * w * S, y * h * S) for x, y in pairs]

    # water: deeper to the south
    for i in range(h * S):
        t = i / max(1, h * S - 1)
        a.line([(0, i), (w * S, i)], fill=(int(18 - 9 * t), int(46 - 24 * t), int(70 - 34 * t)))

    land = (186, 173, 140)
    coast = (124, 110, 82)

    # Iran, across the north
    iran = P((0, 0), (1, 0), (1, 0.245), (0.90, 0.290), (0.80, 0.250), (0.70, 0.310),
             (0.58, 0.262), (0.47, 0.325), (0.35, 0.275), (0.22, 0.335), (0.10, 0.300),
             (0, 0.355))
    a.polygon(iran, fill=land)
    a.line(iran[2:] + [iran[0]], fill=coast, width=2 * S)

    # Musandam (Oman), bottom right, leaving the strait between
    mus = P((1, 0.560), (1, 1), (0.760, 1), (0.800, 0.845), (0.875, 0.740), (0.950, 0.645))
    a.polygon(mus, fill=land)
    a.line(mus, fill=coast, width=2 * S)

    # Qatar peninsula, bottom centre
    qat = P((0.520, 1), (0.545, 0.880), (0.592, 0.828), (0.638, 0.880), (0.662, 1))
    a.polygon(qat, fill=land)
    a.line(qat, fill=coast, width=2 * S)

    # Bahrain: a small island with two US positions struck
    bx, by = 0.395 * w * S, 0.560 * h * S
    a.ellipse([bx - 0.056 * w * S, by - 0.040 * h * S, bx + 0.056 * w * S, by + 0.040 * h * S], fill=land)
    a.ellipse([bx + 0.050 * w * S, by - 0.010 * h * S, bx + 0.080 * w * S, by + 0.020 * h * S], fill=land)

    # tankers struck near the strait
    _ship(a, 0.800 * w * S, 0.690 * h * S, 0.070 * w * S)
    _ship(a, 0.870 * w * S, 0.790 * h * S, 0.056 * w * S)

    # strike markers over the two US positions in Bahrain
    _star(a, bx - 0.022 * w * S, by - 0.008 * h * S, 0.034 * w * S, (214, 40, 32), (255, 240, 214))
    _star(a, bx + 0.024 * w * S, by + 0.016 * h * S, 0.027 * w * S, (214, 40, 32), (255, 240, 214))

    # shipping lane through the strait
    lane = P((0.985, 0.520), (0.880, 0.575), (0.760, 0.610), (0.640, 0.560),
             (0.520, 0.500), (0.400, 0.455), (0.280, 0.430), (0.140, 0.425))
    dash, gap = 9 * S, 6 * S
    carry = 0.0
    for i in range(len(lane) - 1):
        x1, y1 = lane[i]
        x2, y2 = lane[i + 1]
        seg = math.hypot(x2 - x1, y2 - y1)
        pos = -carry
        while pos < seg:
            s0 = max(pos, 0.0)
            s1 = min(pos + dash, seg)
            if s1 > s0:
                t0, t1 = s0 / seg, s1 / seg
                a.line([(x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0),
                        (x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1)],
                       fill=(120, 162, 200), width=3 * S)
            pos += dash + gap
        carry = max(0.0, seg - (pos - dash - gap)) if pos > seg else 0.0

    # labels
    fl = font(SANS_BOLD, 11 * S)
    fs = font(SANS, 10 * S)
    a.text((0.075 * w * S, 0.085 * h * S), "IRAN", font=fl, fill=(52, 44, 28))
    a.text((0.150 * w * S, 0.690 * h * S), "BAHRAIN", font=fl, fill=(226, 236, 248))
    a.line([(0.258 * w * S, 0.700 * h * S), (0.360 * w * S, 0.600 * h * S)],
           fill=(226, 236, 248), width=S)
    a.text((0.620 * w * S, 0.400 * h * S), "STRAIT OF", font=fs, fill=(176, 198, 224))
    a.text((0.620 * w * S, 0.452 * h * S), "HORMUZ", font=fs, fill=(176, 198, 224))

    img.paste(art.resize((w, h), Image.LANCZOS), (x0, y0))
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=(10, 16, 26), width=2)


def check_glyphs(texts):
    """Every character must be present in the cmap of the font that draws it."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return
    missing = set()
    for path in (SERIF_BLACK, SERIF_BOLD, SERIF_ITAL, SANS, SANS_BOLD):
        cmap = TTFont(path).getBestCmap()
        for t in texts:
            for ch in set(t):
                if ch != " " and ord(ch) not in cmap:
                    missing.add((path.rsplit("/", 1)[-1], ch))
    if missing:
        raise SystemExit(f"missing glyphs: {sorted(missing)}")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    check_glyphs([
        "THE WORLD", "SATURDAY 21 NOVEMBER 2026", "WORLD EDITION", "PAGE ONE", "LATE EDITION",
        "TEN STORIES  ·  ONE PAGE", "LEAD STORY  ·  MIDDLE EAST", "THE DAY IN BRIEF",
        "NINE MORE STORIES", "IRAN STRIKES TWO US SITES IN BAHRAIN", "IRAN", "BAHRAIN",
        "STRAIT OF HORMUZ",
        "BOY, 7, AND PARAMEDIC KILLED IN KRYVYI RIH",
        "RUSSIAN CARGO SHIP ABLAZE IN GULF OF FINLAND",
        "MEXICO CAPTURES 'EL CHAPO ISIDRO'",
        "COP31 TALKS RUN PAST DEADLINE IN ANTALYA",
        "NASDAQ ERASES ALL OF ITS 2026 GAINS",
        "TRUMP, XI AND PUTIN MEET AT APEC IN SHENZHEN",
        "MOSQUITOES CUT CHILD DENGUE CASES BY 69%",
        "MAGNITUDE 6.8 EARTHQUAKE SHAKES THE ANDES",
        "BITCOIN SLIDES TO $55,300, THEN REBOUNDS",
    ])

    # ---- top strip -------------------------------------------------------
    f_top = font(SANS_BOLD, 9)
    draw_tracked(d, M, 20, "WORLD EDITION", f_top, MUTED, 1.6)
    right = "TEN STORIES  ·  ONE PAGE"
    draw_tracked(d, W - M - text_w(d, right, f_top, 1.6), 20, right, f_top, MUTED, 1.6)
    rule(d, M, 36, W - M, INK, 2)

    # ---- masthead --------------------------------------------------------
    mast_text = "THE WORLD"
    track = 6.0
    f_mast = font(SERIF_BLACK, 140)
    while text_w(d, mast_text, f_mast, track) > CW - 14 and f_mast.size > 40:
        f_mast = font(SERIF_BLACK, f_mast.size - 2)
    bb = d.textbbox((0, 0), mast_text, font=f_mast)
    mast_y = 42 - bb[1]
    draw_tracked(d, 0, mast_y, mast_text, f_mast, INK, track, center=W / 2)
    mast_bottom = mast_y + bb[3] + 8
    rule(d, M, mast_bottom, W - M, INK, 3)
    rule(d, M, mast_bottom + 5, W - M, INK, 1)

    # ---- date bar --------------------------------------------------------
    bar_y = mast_bottom + 10
    bar_h = 34
    d.rectangle([M, bar_y, W - M, bar_y + bar_h], fill=NAVY)
    f_no = font(SANS_BOLD, 10)
    d.text((M + 12, bar_y + 11), "PAGE ONE", font=f_no, fill=(196, 208, 226))
    ed = "LATE EDITION"
    d.text((W - M - 12 - d.textlength(ed, font=f_no), bar_y + 11), ed, font=f_no, fill=(196, 208, 226))
    f_date = font(SERIF_BOLD, 21)
    draw_tracked(d, 0, bar_y + 5, "SATURDAY 21 NOVEMBER 2026", f_date, (255, 255, 255), 2.2, center=W / 2)

    # ---- lead story ------------------------------------------------------
    lead_y = bar_y + bar_h + 16
    art_w = 322
    tw = CW - art_w - 22

    f_kick = font(SANS_BOLD, 12)
    f_head = pick_size(d, "IRAN STRIKES TWO US SITES IN BAHRAIN", SERIF_BLACK,
                       tw, 2, [58, 56, 54, 52, 50, 48, 46], "lead")
    hsize = f_head.size
    head_lines = wrap_balanced(d, "IRAN STRIKES TWO US SITES IN BAHRAIN", f_head, tw, 2)
    f_deck = font(SERIF_ITAL, 16)
    deck = ("Guards say two US positions were hit; a civilian industrial site burned and "
            "tankers were struck near Hormuz.")
    deck_lines = wrap_balanced(d, deck, f_deck, tw, 3)
    if len(deck_lines) > 3:
        raise SystemExit(f"deck overflows: {deck_lines}")

    f_body = font(SANS, 12)
    col_w = (tw - 20) // 2
    body = [
        "The Revolutionary Guards said they hit two US military positions in Bahrain. "
        "Bahrain said no one was injured.",
        "Two tankers were struck near the Strait of Hormuz, the chokepoint for a fifth of "
        "the world's oil.",
    ]
    body_lines = [wrap(d, t, f_body, col_w) for t in body]
    for i, lines in enumerate(body_lines):
        if len(lines) > 3:
            raise SystemExit(f"body col {i} overflows: {lines}")

    # ---- grid metrics (computed first; the lead panel takes the slack) ----
    stories = [
        (["#0057B7", "#FFD700"], "UKRAINE",
         "BOY, 7, AND PARAMEDIC KILLED IN KRYVYI RIH",
         "A Russian missile hit Zelensky's hometown, wounding dozens; missiles also hit Poland."),
        (["#FFFFFF", "#0039A6", "#D52B1E"], "BALTIC",
         "RUSSIAN CARGO SHIP ABLAZE IN GULF OF FINLAND",
         "A drone strike set the Sparta II on fire; the crew abandoned ship."),
        (["#006847", "#FFFFFF", "#CE1126"], "MEXICO",
         "MEXICO CAPTURES 'EL CHAPO ISIDRO'",
         "FBI most-wanted Fausto Isidro Meza Flores was seized; at least 11 died in the violence."),
        (["#E30A17", "#FFFFFF", "#1E7A46"], "CLIMATE",
         "COP31 TALKS RUN PAST DEADLINE IN ANTALYA",
         "Negotiators closed in on a final deal as a fossil-fuel dispute dragged on."),
        (["#8C1018", "#B3202A", "#5A0A10"], "MARKETS",
         "NASDAQ ERASES ALL OF ITS 2026 GAINS",
         "The S&P 500 fell into correction; Nvidia dropped 14% on a reported SEC probe."),
        (["#DE2910", "#FFDE00", "#DE2910"], "DIPLOMACY",
         "TRUMP, XI AND PUTIN MEET AT APEC IN SHENZHEN",
         "Trump called Putin 'my friend' at the summit, drawing a backlash."),
        (["#009C3B", "#FFDF00", "#009C3B"], "HOPE",
         "MOSQUITOES CUT CHILD DENGUE CASES BY 69%",
         "A trial in Brazil found infections in children fell by about 69%."),
        (["#D91023", "#FFFFFF", "#D91023"], "PERU",
         "MAGNITUDE 6.8 EARTHQUAKE SHAKES THE ANDES",
         "A strong quake struck Peru, shaking the Andean region."),
        (["#F7931A", "#FFB84D", "#C26A05"], "CRYPTO",
         "BITCOIN SLIDES TO $55,300, THEN REBOUNDS",
         "Lowest since September 2024; it climbed back above $60,000."),
    ]

    gap = 8
    cols = 3
    pw = (CW - gap * (cols - 1)) // cols
    pad = 12
    inner = pw - 2 * pad

    # one headline size for every panel, so the grid reads as a single page
    f_h = None
    for size in (30, 29, 28, 27, 26, 25, 24, 23):
        cand = font(SERIF_BLACK, size)
        ok = True
        for _, _, headline, _ in stories:
            lines = wrap(d, headline, cand, inner)
            if len(lines) > 3 or any(d.textlength(l, font=cand) > inner for l in lines):
                ok = False
                break
        if ok:
            f_h = cand
            break
    if f_h is None:
        raise SystemExit("no uniform headline size fits the grid")
    line_h = round(f_h.size * 0.96)

    # panel metrics
    head_top = 29
    sum_gap = 5
    sum_line = 16
    bot_pad = 8

    f_s = font(SANS, 13)
    need_h = 0
    for _, _, headline, summary in stories:
        slines = wrap_balanced(d, summary, f_s, inner, 3)
        if len(slines) > 3:
            raise SystemExit(f"summary overflows: {slines}")
        nhead = len(wrap_balanced(d, headline, f_h, inner, 3))
        need_h = max(need_h, head_top + nhead * line_h + sum_gap + len(slines) * sum_line + bot_pad)

    rows = 3
    ph = need_h
    grid_h = rows * ph + gap * (rows - 1)
    grid_bottom = H - M
    grid_top = grid_bottom - grid_h
    brief_y = grid_top - 32
    lead_h = brief_y - 14 - lead_y
    if lead_h < 200:
        raise SystemExit(f"lead panel only {lead_h}px tall")

    body_h = max(len(b) for b in body_lines) * 15
    text_h = 34 + len(head_lines) * int(hsize * 1.0) + 6 + len(deck_lines) * 20 + 8 + body_h
    if text_h + 8 > lead_h:
        raise SystemExit(f"lead text needs {text_h}px, panel is {lead_h}px")

    d.rectangle([M, lead_y, M + 62, lead_y + 5], fill=RED)
    draw_tracked(d, M, lead_y + 8, "LEAD STORY  ·  MIDDLE EAST", f_kick, RED, 1.4)

    hy = lead_y + 34
    for line in head_lines:
        d.text((M, hy), line, font=f_head, fill=INK)
        hy += int(hsize * 1.0)

    dy = hy + 6
    for line in deck_lines:
        d.text((M, dy), line, font=f_deck, fill=(52, 56, 64))
        dy += 20

    by = dy + 8
    for i, lines in enumerate(body_lines):
        bx = M + i * (col_w + 20)
        yy = by
        for line in lines:
            d.text((bx, yy), line, font=f_body, fill=(62, 66, 74))
            yy += 15
        if i == 0:
            d.line([(M + col_w + 10, by), (M + col_w + 10, yy - 4)], fill=HAIR, width=1)

    lead_art(img, d, W - M - art_w, lead_y, art_w, lead_h)

    # ---- section header --------------------------------------------------
    rule(d, M, brief_y, W - M, INK, 2)
    f_sec = font(SANS_BOLD, 11)
    draw_tracked(d, M, brief_y + 8, "THE DAY IN BRIEF", f_sec, INK, 2.0)
    tail = "NINE MORE STORIES"
    draw_tracked(d, W - M - text_w(d, tail, f_sec, 2.0), brief_y + 8, tail, f_sec, MUTED, 2.0)
    rule(d, M, brief_y + 25, W - M, HAIR, 1)

    # ---- grid ------------------------------------------------------------
    for idx, (strip, kicker, headline, summary) in enumerate(stories):
        r, c = divmod(idx, cols)
        x = M + c * (pw + gap)
        y = grid_top + r * (ph + gap)

        d.rectangle([x, y, x + pw - 1, y + ph - 1], fill=PANEL, outline=HAIR, width=1)

        sw = (pw - 2) / len(strip)
        for i, col in enumerate(strip):
            d.rectangle([x + 1 + i * sw, y + 1, x + 1 + (i + 1) * sw - 1, y + 7], fill=col)

        draw_tracked(d, x + pad, y + 14, kicker, font(SANS_BOLD, 10), MUTED, 1.4)

        yy = y + head_top
        for line in wrap_balanced(d, headline, f_h, inner, 3):
            d.text((x + pad, yy), line, font=f_h, fill=INK)
            yy += line_h

        sy = yy + sum_gap
        for line in wrap_balanced(d, summary, f_s, inner, 3):
            d.text((x + pad, sy), line, font=f_s, fill=(64, 68, 76))
            sy += sum_line

    return img


if __name__ == "__main__":
    build().save("image.png", "PNG", optimize=True)
    print("wrote image.png")
