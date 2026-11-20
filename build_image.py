#!/usr/bin/env python3
"""Build the news-image-20261120 front page (1024x1024, Pillow). v2.

Draws a newspaper front page summarising Friday 20 November 2026 world news.
All text is rendered in code with DejaVu (OFL) fonts committed to this repo.
No network, no image model. Run: python3 build_image.py  -> entry.png
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976

# Colours
INK = (18, 18, 18)
PAPER = (252, 250, 244)
RED = (178, 34, 34)
GREY = (110, 110, 110)
LIGHT_GREY = (200, 198, 190)
BLUE = (30, 80, 140)
TEAL = (20, 120, 110)
AMBER = (200, 140, 20)
CARD_BG = (255, 255, 255)
SEA = (198, 220, 236)
LAND = (224, 212, 186)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = lambda s: font("DejaVuSans-Bold.ttf", s)
F_REG = lambda s: font("DejaVuSans.ttf", s)
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, y, text, fnt, fill=INK, x0=MARGIN, x1=W - MARGIN):
    tw = draw.textlength(text, font=fnt)
    draw.text(((x0 + x1 - tw) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


REGION_LABEL = {
    "Asia": "ASIA-PACIFIC",
    "Europe": "EUROPE",
    "Americas": "THE AMERICAS",
    "Oceania": "OCEANIA",
    "World": "WORLD",
    "Middle East": "MIDDLE EAST",
}
REGION_ORDER = ["ASIA-PACIFIC", "EUROPE", "THE AMERICAS", "OCEANIA", "WORLD", "MIDDLE EAST"]
CONFIRMED = {1: "IMD", 2: "REUTERS", 3: "REUTERS"}


def main():
    with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    stories = {s["n"]: s for s in man["stories"]}
    leads = [stories[n] for n in (1, 2, 3)]
    cards = [stories[n] for n in range(4, 14)]
    briefs = [stories[n] for n in range(14, 23)]
    numbers = man["by_the_numbers"]
    date_check = man["date_check_excluded"]

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- MASTHEAD: the date is the single biggest text ----------
    y = 10
    draw_centered(d, y, "THE WORLD IN ONE DAY", F_BOLD(14), fill=RED)
    y += 18
    draw_centered(d, y, "Friday 20 November 2026", F_TITLE(54), fill=INK)
    y += 62
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=3)
    y += 6
    draw_centered(
        d, y,
        "A cyclone comes ashore in India · Missiles rain on Kyiv · Taiwan stocks crash 6%",
        F_REG(15), fill=(60, 60, 60),
    )
    y += 22
    # region bar with counts, computed from the story list
    counts = {}
    for s in man["stories"]:
        lab = REGION_LABEL.get(s["region"], s["region"].upper())
        counts[lab] = counts.get(lab, 0) + 1
    regions = "  ·  ".join(f"{lab} {counts[lab]}" for lab in REGION_ORDER if lab in counts)
    d.rectangle([MARGIN, y, W - MARGIN, y + 22], fill=INK)
    draw_centered(d, y + 3, regions, F_BOLD(13), fill=PAPER)
    y += 26

    # ---------- HEROES (3 columns) ----------
    hero_y = y
    hero_art_h = 84
    col_w = (CW - 2 * 12) // 3  # 317
    hero_h = 232
    for i, s in enumerate(leads):
        x0 = MARGIN + i * (col_w + 12)
        x1 = x0 + col_w
        # illustration box
        d.rectangle([x0, hero_y, x1, hero_y + hero_art_h], fill=(235, 232, 222))
        draw_hero_art(d, i, x0, hero_y, col_w, hero_art_h)
        # number badge
        badge = str(s["n"])
        d.ellipse([x0 + 6, hero_y + 6, x0 + 30, hero_y + 30], fill=RED)
        tb = d.textlength(badge, font=F_BOLD(14))
        d.text((x0 + 18 - tb / 2, hero_y + 9), badge, font=F_BOLD(14), fill=PAPER)
        # time chip
        chip = s["event_time_utc"][11:16] + " UTC"
        cw_ = d.textlength(chip, font=F_BOLD(12)) + 12
        d.rounded_rectangle(
            [x1 - cw_ - 6, hero_y + 8, x1 - 6, hero_y + 28], radius=9, fill=INK
        )
        d.text((x1 - cw_ - 6 + 6, hero_y + 11), chip, font=F_BOLD(12), fill=PAPER)
        # CONFIRMED badge (pill under the art)
        hy = hero_y + hero_art_h + 6
        conf = "CONFIRMED · " + CONFIRMED[s["n"]]
        cw2 = d.textlength(conf, font=F_BOLD(11)) + 16
        d.rounded_rectangle([x0, hy, x0 + cw2, hy + 18], radius=9, fill=RED)
        d.text((x0 + 8, hy + 3), conf, font=F_BOLD(11), fill=PAPER)
        hy += 24
        # headline (max 2 lines)
        lines = wrap(d, s["headline"], F_TITLE(30), col_w)[:2]
        for ln in lines:
            d.text((x0, hy), ln, font=F_TITLE(30), fill=INK)
            hy += 34
        if len(lines) == 1:
            hy += 34
        # summary (1 line, truncated to fit)
        sub = s["summary"]
        while d.textlength(sub, font=F_REG(14)) > col_w and len(sub) > 10:
            sub = sub.rsplit(" ", 1)[0] + "…"
        d.text((x0, hy), sub, font=F_REG(14), fill=(60, 60, 60))
        hy += 18
        # source tag
        d.text((x0, hy), s["source_tag"], font=F_REG(11), fill=(90, 90, 90))
        hy += 14
        # region tag
        d.text((x0, hy + 2), s["region"].upper() + "  ·  " + s["category"].upper(),
               font=F_BOLD(11), fill=RED)
    y = hero_y + hero_h + 4

    # ---------- BY THE NUMBERS ----------
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 3
    d.text((MARGIN, y), "BY THE NUMBERS", font=F_BOLD(13), fill=RED)
    y += 16
    seg_w = CW // 6
    for i, nb in enumerate(numbers):
        x0 = MARGIN + i * seg_w
        d.text((x0, y), nb["label"], font=F_TITLE(18), fill=INK)
        clines = wrap(d, nb["context"], F_REG(10), seg_w - 10)[:2]
        cy = y + 21
        for ln in clines:
            d.text((x0, cy), ln, font=F_REG(10), fill=GREY)
            cy += 12
        if i:
            d.line([(x0 - 6, y), (x0 - 6, y + 34)], fill=LIGHT_GREY, width=1)
    y += 42
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 6

    # ---------- ILLUSTRATED CARDS (2 rows x 5) ----------
    card_w = (CW - 4 * 10) // 5  # 187
    card_h = 106
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            if idx >= len(cards):
                break
            s = cards[idx]
            x0 = MARGIN + col * (card_w + 10)
            cy = y + row * (card_h + 6)
            d.rectangle([x0, cy, x0 + card_w, cy + card_h], outline=LIGHT_GREY, width=1, fill=CARD_BG)
            d.rectangle([x0 + 1, cy + 1, x0 + card_w - 1, cy + 30], fill=(238, 236, 228))
            draw_card_art(d, s["n"], x0, cy, card_w, 30)
            # region + source outlet on one line
            d.text((x0 + 6, cy + 33),
                   s["region"].upper() + " " + s["source_tag"].upper(),
                   font=F_BOLD(10), fill=RED)
            hy = cy + 46
            lines = wrap(d, s["headline"], F_BOLD(15), card_w - 12)[:2]
            for ln in lines:
                d.text((x0 + 6, hy), ln, font=F_BOLD(15), fill=INK)
                hy += 17
            slines = wrap(d, s["summary"], F_REG(11), card_w - 12)[:2]
            for ln in slines:
                d.text((x0 + 6, hy), ln, font=F_REG(11), fill=(70, 70, 70))
                hy += 13
    y += 2 * card_h + 6 + 4

    # ---------- DOTTED WORLD MAP + PINS ----------
    map_y = y
    map_h = 76
    d.text((MARGIN, map_y), "WHERE IT HAPPENED — 20 NOVEMBER 2026  (positions approximate)",
           font=F_BOLD(12), fill=INK)
    map_y += 15
    draw_world_map(d, MARGIN, map_y, CW, map_h - 15, stories)
    y = map_y + map_h - 15 + 4

    # ---------- UTC TIMELINE (staggered lead markers) ----------
    d.text((MARGIN, y), "WHEN — UTC TIMELINE  (1 Akvan 02:00 · 2 Kyiv 01:22 · 3 Taiex 01:00)",
           font=F_BOLD(12), fill=INK)
    y += 14
    tl_y = y
    d.line([(MARGIN, tl_y + 8), (W - MARGIN, tl_y + 8)], fill=LIGHT_GREY, width=2)
    for h in range(0, 25, 4):
        x = MARGIN + (CW * h) // 24
        d.line([(x, tl_y + 4), (x, tl_y + 12)], fill=GREY, width=1)
        lab = f"{h:02d}:00"
        d.text((x - 12, tl_y + 14), lab, font=F_REG(9), fill=GREY)
    # lead markers: small red dots on the line (they cluster 01:00-02:00,
    # so no numbered circles — the legend in the heading names them)
    for s in leads:
        hh = int(s["event_time_utc"][11:13])
        mm = int(s["event_time_utc"][14:16])
        frac = (hh * 60 + mm) / 1440
        x = MARGIN + int(CW * frac)
        d.ellipse([x - 5, tl_y + 3, x + 5, tl_y + 13], fill=RED)
    y = tl_y + 28

    # ---------- ALSO ON 20 NOVEMBER ----------
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 3
    d.text((MARGIN, y), "ALSO ON 20 NOVEMBER", font=F_BOLD(13), fill=INK)
    y += 17
    col_w2 = CW // 3
    per_col = math.ceil(len(briefs) / 3)
    for col in range(3):
        x0 = MARGIN + col * col_w2
        chunk = briefs[col * per_col:(col + 1) * per_col]
        by = y
        for s in chunk:
            txt = f"{s['n']}. {s['headline']} {s['source_tag']}"
            while d.textlength(txt, font=F_REG(11)) > col_w2 - 14 and len(txt) > 10:
                txt = txt.rsplit(" ", 1)[0] + "…"
            d.text((x0, by), txt, font=F_REG(11), fill=INK)
            by += 12
    y += per_col * 12 + 3

    # ---------- FOOTER: DATE CHECK (red box) + SOURCES ----------
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 3
    dc = [it["event"] for it in date_check]
    per = math.ceil(len(dc) / 3)
    dc_block = 16 + per * 10 + 6
    d.rectangle([MARGIN - 4, y - 2, W - MARGIN + 4, y - 2 + dc_block], outline=RED, width=2)
    d.text((MARGIN, y + 2),
           "DATE CHECK — First reported Thursday 19 Nov, so NOT on this page as Friday's news:",
           font=F_BOLD(11), fill=RED)
    y += 16
    for col in range(3):
        x0 = MARGIN + col * (CW // 3)
        chunk = dc[col * per:(col + 1) * per]
        by = y
        for item in chunk:
            lines = wrap(d, "· " + item, F_REG(10), CW // 3 - 12)
            for ln in lines[:1]:
                d.text((x0, by), ln, font=F_REG(10), fill=(80, 80, 80))
                by += 10
    y += per * 10 + 6
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=LIGHT_GREY, width=1)
    y += 4
    draw_centered(
        d, y,
        "Every story here happened, or was first reported, on Friday 20 November 2026.",
        F_BOLD(12), fill=INK,
    )
    y += 17
    src = ("Sources: Reuters · AP · AFP · IMD · USGS · UN News · RSMC Nadi · JTWC · Le Monde · "
           "ANSA · CGIL · ESA · UNICEF · ATP · Deadline · CoinGecko · CNN · RealGM. "
           "Full source list in SOURCES.md. Original drawings.")
    lines = wrap(d, src, F_REG(10), CW)
    for ln in lines:
        d.text((MARGIN, y), ln, font=F_REG(10), fill=GREY)
        y += 12

    print(f"final y = {y} (canvas {H})")
    img.save(OUT, optimize=True)
    print(f"Saved {OUT}  {img.size}  {os.path.getsize(OUT)} bytes")


# ---------------- illustrations ----------------

def draw_hero_art(d, idx, x0, y0, w, h):
    """Flat-shape illustration for each hero story."""
    cx, cy = x0 + w // 2, y0 + h // 2
    if idx == 0:
        # Akvan: Bay of Bengal schematic — sea, India coast, cyclone track, landfall
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA)
        # India east-coast landmass (left)
        d.polygon([(x0 + 8, y0 + h), (x0 + 52, y0 + 8), (x0 + 108, y0 + 2),
                   (x0 + 132, y0 + 30), (x0 + 118, y0 + h)], fill=LAND)
        d.line([(x0 + 52, y0 + 8), (x0 + 108, y0 + 2), (x0 + 132, y0 + 30)],
               fill=(150, 130, 100), width=2)
        # cyclone spiral over the bay
        scx, scy = x0 + 210, y0 + 46
        for r in (26, 18, 11):
            d.arc([scx - r, scy - r, scx + r, scy + r], 20, 300, fill=BLUE, width=4)
        d.ellipse([scx - 5, scy - 5, scx + 5, scy + 5], fill=BLUE)
        # dashed track from the cyclone to the coast (landfall near Gopalpur)
        lx, ly = x0 + 128, y0 + 34
        segs = 8
        for k in range(segs):
            t0, t1 = k / segs, (k + 0.55) / segs
            x_a = scx + (lx - scx) * t0
            y_a = scy + (ly - scy) * t0 - 6 * (1 - t0) * t0 * 4
            x_b = scx + (lx - scx) * t1
            y_b = scy + (ly - scy) * t1 - 6 * (1 - t1) * t1 * 4
            d.line([(x_a, y_a), (x_b, y_b)], fill=RED, width=3)
        d.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=RED, outline=PAPER, width=1)
        d.text((lx - 62, ly - 5), "Gopalpur", font=F_BOLD(10), fill=RED)
    elif idx == 1:
        # Kyiv: skyline silhouette with missile trails
        base = y0 + h - 10
        for bx, bw, bh in ((-140, 40, 40), (-95, 30, 54), (-60, 44, 32), (-10, 34, 48), (30, 42, 36), (78, 30, 58), (112, 38, 42)):
            d.rectangle([cx + bx, base - bh, cx + bx + bw, base], fill=(90, 90, 96))
        # lit windows
        for wx, wy in ((-128, base - 30), (-88, base - 44), (-48, base - 22),
                       (2, base - 38), (42, base - 26), (86, base - 48), (122, base - 32)):
            d.rectangle([cx + wx, wy, cx + wx + 5, wy + 6], fill=AMBER)
        # two missile trails
        d.line([(cx - 110, y0 + 12), (cx - 30, y0 + 46)], fill=RED, width=4)
        d.line([(cx + 120, y0 + 8), (cx + 55, y0 + 40)], fill=RED, width=4)
        # impact flame on the middle tower
        d.polygon([(cx - 78, base - 54), (cx - 66, base - 74), (cx - 54, base - 54)], fill=RED)
        d.polygon([(cx - 72, base - 54), (cx - 66, base - 66), (cx - 60, base - 54)], fill=AMBER)
    else:
        # Taiex: falling candlestick chart
        candles = [  # (open_y, close_y) — falling trend
            (y0 + 18, y0 + 26), (y0 + 24, y0 + 34), (y0 + 30, y0 + 40),
            (y0 + 38, y0 + 50), (y0 + 46, y0 + 58), (y0 + 56, y0 + 68),
        ]
        for k, (oy, cy_) in enumerate(candles):
            bx = x0 + 28 + k * 42
            top, bot = min(oy, cy_), max(oy, cy_)
            d.line([(bx + 7, top - 6), (bx + 7, bot + 6)], fill=RED, width=2)
            d.rectangle([bx, top, bx + 14, bot], fill=RED)
        d.text((x0 + 12, y0 + h - 26), "-6%", font=F_TITLE(22), fill=RED)
        d.text((x0 + 168, y0 + h - 22), "36,096", font=F_BOLD(12), fill=RED)


def draw_card_art(d, n, x0, y0, w, h):
    """Small flat motif per card, drawn in the top strip of the card."""
    cx = x0 + w // 2
    cy = y0 + h // 2
    if n == 4:  # COP31 globe
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=TEAL, width=3)
        d.line([(cx - 11, cy), (cx + 11, cy)], fill=TEAL, width=2)
        d.line([(cx, cy - 11), (cx, cy + 11)], fill=TEAL, width=2)
    elif n == 5:  # markets down
        d.line([(x0 + 16, y0 + 8), (x0 + 60, y0 + 13), (x0 + 100, y0 + 10),
                (x0 + 140, y0 + 20), (x0 + 168, y0 + 18)], fill=RED, width=3)
        d.polygon([(x0 + 168, y0 + 18), (x0 + 157, y0 + 13), (x0 + 159, y0 + 23)], fill=RED)
    elif n == 6:  # cyclone
        for r in (11, 7):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=BLUE, width=3)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=BLUE)
    elif n == 7:  # inflation arrow up
        d.line([(cx, cy + 9), (cx, cy - 8)], fill=AMBER, width=3)
        d.polygon([(cx, cy - 12), (cx - 5, cy - 3), (cx + 5, cy - 3)], fill=AMBER)
        d.text((cx + 12, cy - 7), "%", font=F_BOLD(13), fill=AMBER)
    elif n == 8:  # oil barrel
        d.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], outline=INK, width=2)
        d.line([(cx - 10, cy - 3), (cx + 10, cy - 3)], fill=INK, width=1)
        d.line([(cx - 10, cy + 3), (cx + 10, cy + 3)], fill=INK, width=1)
        d.polygon([(cx + 14, cy - 10), (cx + 17, cy - 17), (cx + 20, cy - 10)], fill=RED)
    elif n == 9:  # two flags
        d.line([(cx - 14, cy - 10), (cx - 14, cy + 10)], fill=INK, width=2)
        d.line([(cx + 6, cy - 10), (cx + 6, cy + 10)], fill=INK, width=2)
        d.polygon([(cx - 14, cy - 10), (cx + 2, cy - 6), (cx - 14, cy - 2)], fill=BLUE)
        d.polygon([(cx + 6, cy - 10), (cx + 22, cy - 6), (cx + 6, cy - 2)], fill=RED)
    elif n == 10:  # megaphone
        d.polygon([(cx - 12, cy - 2), (cx + 4, cy - 10), (cx + 4, cy + 10), (cx - 12, cy + 5)], fill=AMBER)
        d.line([(cx - 12, cy - 2), (cx - 18, cy - 2)], fill=INK, width=3)
        d.line([(cx - 12, cy + 5), (cx - 18, cy + 5)], fill=INK, width=3)
    elif n == 11:  # seismograph
        d.line([(x0 + 10, cy), (x0 + 36, cy), (x0 + 43, cy - 9), (x0 + 50, cy + 9),
                (x0 + 57, cy - 5), (x0 + 64, cy + 3), (x0 + 71, cy),
                (x0 + 108, cy), (x0 + 115, cy - 7), (x0 + 122, cy + 7),
                (x0 + 129, cy), (x0 + 172, cy)], fill=RED, width=2)
    elif n == 12:  # BepiColombo: Mercury + probe
        d.ellipse([cx - 20, cy - 9, cx - 2, cy + 9], fill=(176, 148, 120))
        d.ellipse([cx - 16, cy - 4, cx - 13, cy - 1], fill=(140, 112, 86))
        d.ellipse([cx - 10, cy + 3, cx - 7, cy + 6], fill=(140, 112, 86))
        d.rectangle([cx + 6, cy - 4, cx + 14, cy + 4], fill=INK)
        d.rectangle([cx - 2, cy - 2, cx + 6, cy + 2], fill=BLUE)
        d.rectangle([cx + 14, cy - 2, cx + 22, cy + 2], fill=BLUE)
    elif n == 13:  # Phillips: cricket bat + ball
        d.polygon([(cx - 14, cy + 10), (cx - 2, cy + 10), (cx - 2, cy - 2),
                   (cx - 6, cy - 12), (cx - 10, cy - 12), (cx - 10, cy - 2)], fill=(206, 172, 118), outline=INK)
        d.ellipse([cx + 8, cy - 10, cx + 18, cy], fill=RED)
    else:
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=GREY, width=2)


# Simplified world map: rows of dots approximating continents.
WORLD = [
    "                                                ",
    "      ######  #########  ##################      ",
    "   ##########  ########   ##################     ",
    "    #########   ######     ########  ########    ",
    "     #######     ####       ######    ######      ",
    "      #####      ###         ####      ####       ",
    "       ###       ##          ###       ##         ",
    "        #        #           ##       #          ",
    "                  ##        ###                  ",
    "                 ####      #####      ##         ",
    "                ######    #######    ####        ",
    "                 ####      #####      ##         ",
    "                  ##        ###                  ",
    "                                                ",
]


def draw_world_map(d, x0, y0, w, h, stories):
    rows = len(WORLD)
    cols = len(WORLD[0])
    dx = w / cols
    dy = h / rows
    for r, row in enumerate(WORLD):
        for c, ch in enumerate(row):
            if ch == "#":
                cx = x0 + (c + 0.5) * dx
                cy = y0 + (r + 0.5) * dy
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=(150, 148, 138))
    # pins: story number -> (fraction x, fraction y); spread to avoid collisions
    pins = {
        1: (0.70, 0.48),   # Akvan, India
        2: (0.53, 0.16),   # Kyiv
        3: (0.80, 0.42),   # Taiwan
        4: (0.56, 0.36),   # COP31 Antalya
        5: (0.84, 0.30),   # Asia markets (Tokyo/Seoul)
        6: (0.94, 0.60),   # Xavier, Cook Islands
        7: (0.90, 0.22),   # Japan
        8: (0.58, 0.52),   # Gulf oil
        9: (0.46, 0.20),   # Paris
        10: (0.49, 0.32),  # Italy
        11: (0.88, 0.76),  # Loyalty Islands
        12: (0.44, 0.12),  # BepiColombo (ESA mission control, Darmstadt)
        13: (0.96, 0.82),  # Phillips, Wellington NZ
    }
    for n, (fx, fy) in pins.items():
        px = x0 + fx * w
        py = y0 + fy * h
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=PAPER, width=1)
        lab = str(n)
        tw = d.textlength(lab, font=F_BOLD(9))
        d.text((px - tw / 2, py - 5), lab, font=F_BOLD(9), fill=PAPER)


if __name__ == "__main__":
    main()
