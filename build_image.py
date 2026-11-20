#!/usr/bin/env python3
"""Build the news-image-20261120 front page (1024x1024, Pillow).

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


def main():
    with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    stories = {s["n"]: s for s in man["stories"]}
    leads = [stories[n] for n in (1, 2, 3)]
    cards = [stories[n] for n in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13)]
    briefs = [stories[n] for n in range(14, 38)]
    numbers = man["by_the_numbers"]
    date_check = man["date_check_excluded"]

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- MASTHEAD ----------
    y = 14
    d.text((MARGIN, y), "THE WORLD TODAY", font=F_TITLE(50), fill=INK)
    tw = d.textlength("20 NOV 2026", font=F_TITLE(28))
    d.text((W - MARGIN - tw, y + 12), "20 NOV 2026", font=F_TITLE(28), fill=RED)
    y = 68
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=3)
    y += 6
    draw_centered(d, y, "FRIDAY 20 NOVEMBER 2026", F_TITLE(40), fill=INK)
    y += 48
    draw_centered(
        d, y, "One day. One picture. Every story that mattered.",
        F_REG(16), fill=GREY,
    )
    y += 24
    d.rectangle([MARGIN, y, W - MARGIN, y + 22], fill=INK)
    regions = "ASIA  ·  EUROPE  ·  MIDDLE EAST  ·  AFRICA  ·  AMERICAS  ·  OCEANIA"
    draw_centered(d, y + 3, regions, F_BOLD(14), fill=PAPER)
    y += 28

    # ---------- HEROES (3 columns) ----------
    hero_y = y
    hero_art_h = 84
    col_w = (CW - 2 * 12) // 3  # 317
    # compute hero section height from content (headline 2 lines max, subhead 1 line)
    hero_h = hero_art_h + 8 + 2 * 34 + 18 + 6 + 14
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
        # headline (max 2 lines)
        hy = hero_y + hero_art_h + 8
        lines = wrap(d, s["headline"], F_TITLE(30), col_w)[:2]
        for ln in lines:
            d.text((x0, hy), ln, font=F_TITLE(30), fill=INK)
            hy += 34
        if len(lines) == 1:
            hy += 34
        # subhead (1 line, truncated to fit)
        sub = s["summary"]
        while d.textlength(sub, font=F_REG(14)) > col_w and len(sub) > 10:
            sub = sub.rsplit(" ", 1)[0] + "…"
        d.text((x0, hy), sub, font=F_REG(14), fill=(60, 60, 60))
        hy += 18
        # region tag (placed after subhead, no overlap)
        d.text((x0, hy + 6), s["region"].upper() + "  ·  " + s["category"].upper(),
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
            d.text((x0 + 6, cy + 33), s["region"].upper(), font=F_BOLD(10), fill=RED)
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
    map_h = 82
    d.text((MARGIN, map_y), "WHERE IT HAPPENED — 20 NOVEMBER 2026", font=F_BOLD(12), fill=INK)
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
            txt = f"{s['n']}. {s['headline']}"
            lines = wrap(d, txt, F_REG(11), col_w2 - 14)
            for ln in lines[:1]:
                d.text((x0, by), ln, font=F_REG(11), fill=INK)
                by += 12
    y += per_col * 12 + 3

    # ---------- FOOTER: DATE CHECK + SOURCES ----------
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 3
    d.text((MARGIN, y), "DATE CHECK — THESE HAPPENED ON 18–19 NOVEMBER, NOT 20 NOVEMBER",
           font=F_BOLD(11), fill=RED)
    y += 14
    dc = [it["event"] for it in date_check]
    per = math.ceil(len(dc) / 3)
    for col in range(3):
        x0 = MARGIN + col * (CW // 3)
        chunk = dc[col * per:(col + 1) * per]
        by = y
        for item in chunk:
            lines = wrap(d, "· " + item, F_REG(10), CW // 3 - 12)
            for ln in lines[:1]:
                d.text((x0, by), ln, font=F_REG(10), fill=(80, 80, 80))
                by += 11
    y += per * 11 + 1
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=LIGHT_GREY, width=1)
    y += 2
    src = ("Sources: Reuters · AP · AFP · BBC · Al Jazeera · Bloomberg · IMD · USGS · "
           "UN News · RSMC Nadi · JTWC · Le Monde · ANSA · CGIL · CSIS · EMSC. "
           "Full source list in SOURCES.md. All figures verified 20 Nov 2026.")
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
    if idx == 0:  # cyclone: spiral arcs + rain
        for r in (46, 35, 24, 14):
            d.arc([cx - r, cy - r + 4, cx + r, cy + r + 4], 20, 300, fill=BLUE, width=5)
        d.ellipse([cx - 7, cy - 3, cx + 7, cy + 11], fill=BLUE)
        for rx in (-70, -40, 40, 70):
            d.line([(cx + rx, y0 + h - 18), (cx + rx - 5, y0 + h - 7)], fill=TEAL, width=3)
    elif idx == 1:  # Kyiv: skyline + one missile streak + flame
        base = y0 + h - 10
        for bx, bw, bh in ((-140, 40, 40), (-95, 30, 54), (-60, 44, 32), (-10, 34, 48), (30, 42, 36), (78, 30, 58), (112, 38, 42)):
            d.rectangle([cx + bx, base - bh, cx + bx + bw, base], fill=(90, 90, 96))
        d.line([(cx - 110, y0 + 14), (cx - 30, y0 + 46)], fill=RED, width=4)
        d.polygon([(cx - 78, base - 54), (cx - 66, base - 74), (cx - 54, base - 54)], fill=RED)
        d.polygon([(cx - 72, base - 54), (cx - 66, base - 66), (cx - 60, base - 54)], fill=AMBER)
    else:  # Taiex: falling chart + red arrow; label bottom-left (clear of badge/chip)
        pts = [(x0 + 20, y0 + 16), (x0 + 70, y0 + 26), (x0 + 110, y0 + 22),
               (x0 + 160, y0 + 42), (x0 + 210, y0 + 38), (x0 + 260, y0 + 64)]
        d.line(pts, fill=RED, width=5, joint="curve")
        d.polygon([(x0 + 260, y0 + 64), (x0 + 238, y0 + 54), (x0 + 246, y0 + 72)], fill=RED)
        d.text((x0 + 12, y0 + h - 28), "-6%", font=F_TITLE(22), fill=RED)


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
    elif n == 12:  # chip
        d.rectangle([cx - 9, cy - 9, cx + 9, cy + 9], outline=INK, width=2)
        d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=INK)
        for dx in (-12, 0, 12):
            d.line([(cx + dx, cy - 9), (cx + dx, cy - 13)], fill=INK, width=2)
            d.line([(cx + dx, cy + 9), (cx + dx, cy + 13)], fill=INK, width=2)
    elif n == 13:  # star / sparkle
        d.polygon([(cx, cy - 11), (cx + 3, cy - 3), (cx + 11, cy), (cx + 3, cy + 3),
                   (cx, cy + 11), (cx - 3, cy + 3), (cx - 11, cy), (cx - 3, cy - 3)],
                  fill=AMBER)
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
        12: (0.13, 0.36),  # US
        13: (0.20, 0.24),  # US (Gemini)
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
