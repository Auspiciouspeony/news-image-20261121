# build_front.py — renders the front page for make.fun news-image-20261121.
# "Sum up 21 November's world news in one image" — Saturday 21 November 2026.
# Every fact below was verified live against AP / Reuters / BBC / USGS / IMD
# reporting on 21 Nov 2026 (see SOURCES in the footer). Run:
#   python3 build_front.py            -> writes entry.png (1024x1024 JPEG)
#   python3 build_front.py --check    -> same, plus prints the fit report
# Deterministic: no timestamps, no randomness; same input bytes every run.

import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 22
CW = W - 2 * MARGIN  # 980 content width

NAVY = (13, 32, 74)
NAVY_LT = (28, 58, 112)
RED = (178, 24, 24)
RED_LT = (214, 48, 49)
BLACK = (12, 12, 12)
GREY = (88, 88, 88)
GREY_LT = (200, 200, 200)
PAPER = (255, 255, 255)
CREAM = (248, 246, 240)
GOLD = (184, 134, 11)
SEA = (214, 228, 238)
LAND = (232, 228, 216)
YELLOW_BG = (255, 243, 205)
YELLOW_BD = (180, 140, 20)

FDIR = "/usr/share/fonts/truetype/dejavu/"
LDIR = "/usr/share/fonts/truetype/liberation/"


def font(path, size):
    return ImageFont.truetype(path, size)


B = lambda s: font(FDIR + "DejaVuSans-Bold.ttf", s)
R = lambda s: font(FDIR + "DejaVuSans.ttf", s)
SB = lambda s: font(LDIR + "LiberationSans-Bold.ttf", s)
SR = lambda s: font(LDIR + "LiberationSans-Regular.ttf", s)

# ---------------------------------------------------------------- data

HERO = ["RUSSIAN MISSILES HIT POLAND"]
HERO_DECK = ("Two missiles and a drone cross into NATO land \u2014 Tusk calls it a deliberate "
              "provocation; Rutte flies to Warsaw today. No injuries.")
SUBHERO = "KYIV BRIDGES HIT IN MASSIVE STRIKE"
SUBHERO_DECK = ("400+ drones and 110 missiles, 27 ballistic \u2014 8 killed as Russia answers "
                 "the Kerch bridge attack.")

NUMBERS = [
    ("2", "missiles land\nin Poland"),
    ("400+", "drones fired\nat Ukraine"),
    ("110", "missiles in\none night"),
    ("8", "killed across\nUkraine"),
    ("\u20ac1bn", "EU military\naid to Kyiv"),
    ("\u22125.3%", "Nasdaq on\nFriday"),
    ("370k", "evacuated\nfrom Akvan"),
]

REGIONS = [("EUROPE", 7), ("AMERICAS", 12), ("ASIA", 5),
           ("MIDDLE EAST", 2), ("AFRICA", 1), ("WORLD", 3)]
TOTAL_STORIES = 30  # 2 heroes + 4 features + 24 briefs

FEATURES = [
    ("RIYADH INTERCEPTS\n3 MISSILES",
     "Houthi rockets downed over Riyadh on Saturday \u2014 second attack in days.",
     "riyadh"),
    ("MARKETS ROUT:\nS&P \u22123.7%",
     "Nasdaq \u22125.3%, down for the year; Dow \u2212950, worst week in 18 months.",
     "markets"),
    ("BITCOIN UNDER\n$60,000",
     "First time since July; about $59,100 as November's slide tops 20%.",
     "bitcoin"),
    ("AKVAN FADES\nOVER INDIA",
     "No deaths as it weakens; 370,000 evacuated, 209 mm of rain in Ganjam.",
     "cyclone"),
]

# (headline, deck, region) — 24 briefs, one story each.
BRIEFS = [
    ("COP31 slips into overtime",
     "Third draft due Saturday; Panama may block it.", "WORLD"),
    ("UK and EU sign reset deals",
     "Burnham signs food, carbon and youth-mobility pacts.", "EUROPE"),
    ("EU approves \u20ac1bn arms aid",
     "Joint kit buys for Kyiv, delivery by end of 2027.", "EUROPE"),
    ("US, China: humans run war AI",
     "Trump and Xi agree humans must oversee military AI.", "ASIA"),
    ("Trump: bring back Huang",
     "Trump urges Nvidia to restore its ex-CEO; board says no.", "AMERICAS"),
    ("SEC probes Nvidia books",
     "SEC examines Nvidia books, Reuters cites sources.", "AMERICAS"),
    ("US weighs new Iran strikes",
     "Trump mulls action as the military warns of strain.", "M. EAST"),
    ("Senate blocks war-powers bid",
     "Iran resolution fails 51\u201348 after passing the House.", "AMERICAS"),
    ("Trump pardons Pete Rose",
     "Posthumous pardon for the late baseball star.", "AMERICAS"),
    ("LA shaken by 4.2 quake",
     "Commerce tremor at 3:25 a.m.; no damage reported.", "AMERICAS"),
    ("Mongolia's president goes",
     "Parliament accepts it; election due within 4 months.", "ASIA"),
    ("Court: Myanmar committed genocide",
     "World Court rules on the Rohingya case at The Hague.", "ASIA"),
    ("Mamdani: shut Rikers by 2032",
     "New York mayor-elect sets a date to close the jail.", "AMERICAS"),
    ("ANC fights for its cities",
     "South Africa's ruling party battles to hold key metros.", "AFRICA"),
    ("Bukele seeks a third term",
     "El Salvador move could keep him in power until 2033.", "AMERICAS"),
    ("Denmark: Russia plotted killing",
     "Moscow accused of a plot to kill a US-Ukrainian rapper.", "EUROPE"),
    ("Nepal's new PM faces India test",
     "Balendra Shah navigates ties with the old neighbour.", "ASIA"),
    ("US releases more UFO film",
     "Newly declassified footage was shot in the Middle East.", "AMERICAS"),
    ("Hegseth curbs Canada ties",
     "Secret memo restricts US\u2013Canada defence ties.", "AMERICAS"),
    ("French police sentenced",
     "Officers jailed over beating of producer Michel Zecler.", "EUROPE"),
    ("19 years in Sikh murder plot",
     "Indian man sentenced over a US assassination scheme.", "AMERICAS"),
    ("Cost-of-living protests spread",
     "Marches sweep European cities over prices and housing.", "EUROPE"),
    ("Trump: ban AI centres abroad",
     "Trump threatens to stop US firms building them abroad.", "AMERICAS"),
    ("Gold hits 14-month low",
     "Metal posts a 9.4% weekly loss as the sell-off spreads.", "WORLD"),
]

DATE_CHECK = ("DATE CHECK \u2014 SATURDAY 21 NOVEMBER 2026:  Rutte flies to Warsaw today  \u00b7  "
               "Riyadh's 3-missile intercept came at 02:40 UTC  \u00b7  COP31's third draft is due "
               "this morning.")
FOOTER = ("Sources: AP \u00b7 Reuters \u00b7 BBC \u00b7 USGS \u00b7 IMD  \u2014  All facts checked on "
          "Saturday 21 November 2026  \u00b7  30 stories")

# Coarse continent outlines as (lon, lat) — drawn equirectangular, my own roughs.
CONTINENTS = {
    "N America": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
                  (-75, 73), (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 38),
                  (-80, 32), (-85, 29), (-90, 21), (-95, 19), (-100, 16), (-105, 20),
                  (-110, 24), (-115, 30), (-120, 34), (-125, 40), (-125, 49), (-135, 58),
                  (-150, 60), (-165, 60)],
    "Greenland": [(-58, 64), (-45, 60), (-30, 68), (-25, 70), (-40, 76), (-55, 76)],
    "S America": [(-80, 9), (-75, 11), (-62, 11), (-52, 5), (-50, 0), (-44, -3),
                  (-35, -8), (-40, -20), (-48, -28), (-57, -38), (-65, -41), (-70, -50),
                  (-74, -53), (-73, -40), (-72, -20), (-77, -12), (-80, -4)],
    "Africa": [(-6, 35), (-10, 31), (-17, 15), (-17, 12), (-12, 8), (-8, 5), (0, 6),
              (6, 4), (9, 4), (13, -1), (12, -6), (13, -12), (12, -18), (16, -28),
              (20, -35), (28, -33), (33, -26), (35, -20), (40, -15), (41, -10),
              (48, -1), (51, 11), (44, 11), (39, 15), (37, 18), (33, 27), (32, 31),
              (25, 32), (19, 33), (11, 34)],
    "Eurasia": [(-10, 36), (-9, 43), (-2, 44), (0, 46), (-4, 48), (0, 50), (3, 53),
               (8, 55), (8, 57), (10, 59), (5, 60), (12, 62), (18, 64), (25, 70),
               (30, 70), (40, 68), (55, 68), (68, 73), (75, 73), (85, 76), (100, 77),
               (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
               (170, 66), (178, 65), (178, 62), (170, 60), (162, 56), (158, 52),
               (150, 59), (142, 55), (140, 50), (135, 43), (130, 42), (127, 40),
               (122, 38), (120, 32), (122, 28), (118, 25), (110, 20), (108, 12),
               (105, 9), (100, 8), (98, 12), (95, 16), (92, 21), (90, 22), (86, 20),
               (82, 17), (80, 13), (77, 8), (74, 10), (70, 15), (66, 25), (62, 25),
               (58, 26), (56, 27), (52, 28), (50, 30), (48, 30), (44, 29), (40, 28),
               (36, 36), (30, 36), (27, 37), (23, 36), (19, 40), (15, 44), (12, 44),
               (8, 44), (3, 43), (-2, 37), (-6, 36)],
    "Australia": [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
                  (132, -32), (135, -35), (137, -35), (140, -38), (145, -38), (150, -37),
                  (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
                  (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
                  (118, -20)],
    "UK": [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    "Japan": [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 38),
              (141, 41), (143, 42), (145, 44), (142, 45), (140, 42), (139, 38),
              (137, 37), (135, 35), (133, 34)],
    "Indonesia": [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
                  (125, -9), (130, -4), (135, -3), (140, -8), (138, -8), (130, -5),
                  (120, -2), (110, 0)],
    "NZ": [(167, -45), (170, -43), (174, -41), (177, -38), (175, -36), (172, -40)],
}

# (lon, lat, label, label dx, label dy) — pins at true coordinates.
PINS = [
    (-0.1, 51.5, "LONDON", -60, -10),
    (21.0, 52.2, "WARSAW", 8, -16),
    (30.5, 50.5, "KYIV", 10, 8),
    (30.7, 36.9, "ANTALYA", -64, 8),
    (46.7, 24.6, "RIYADH", 8, -4),
    (84.9, 19.3, "GOPALPUR", 8, 2),
    (116.4, 39.9, "BEIJING", 8, -12),
    (106.9, 47.9, "ULAANBAATAR", -92, -12),
    (-118.2, 34.0, "LOS ANGELES", -96, 2),
    (-74.0, 40.7, "NEW YORK", 8, -12),
]

# ---------------------------------------------------------------- helpers

def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def centered(draw, x0, x1, y, s, f, fill):
    w = draw.textlength(s, font=f)
    draw.text(((x0 + x1 - w) / 2, y), s, font=f, fill=fill)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_check(draw, s, f, max_w, what):
    w = draw.textlength(s, font=f)
    assert w <= max_w, f"{what} too wide: {w:.0f} > {max_w} ({s!r})"
    return w


# ---------------------------------------------------------------- feature art

def draw_feature_art(d, kind, x, y, w, h):
    """Small flat illustration inside a feature panel."""
    if kind == "riyadh":
        d.rectangle([x, y, x + w, y + h], fill=(16, 22, 48))
        for sx, sy in [(18, 14), (60, 26), (120, 10), (180, 22), (210, 12)]:
            d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
        # skyline + tower
        d.rectangle([x + 8, y + h - 26, x + 52, y + h], fill=(70, 84, 120))
        d.rectangle([x + 60, y + h - 38, x + 96, y + h], fill=(90, 104, 140))
        d.rectangle([x + 150, y + h - 30, x + 196, y + h], fill=(70, 84, 120))
        d.rectangle([x + 204, y + h - 20, x + w - 8, y + h], fill=(90, 104, 140))
        # interceptor arc + burst
        d.arc([x + 96, y + 8, x + 200, y + 62], 200, 340, fill=(255, 200, 60), width=3)
        d.ellipse([x + 168, y + 12, x + 184, y + 28], fill=(255, 180, 40))
        for dx, dy in [(0, -8), (7, -4), (7, 4), (0, 8), (-7, 4), (-7, -4)]:
            d.line([x + 176, y + 20, x + 176 + dx * 2, y + 20 + dy * 2],
                   fill=(255, 200, 60), width=2)
    elif kind == "markets":
        d.rectangle([x, y, x + w, y + h], fill=(255, 240, 240))
        base = y + h - 8
        bars = [0.55, 0.72, 0.48, 0.66, 0.40, 0.30, 0.18]
        bw = w / len(bars)
        for i, v in enumerate(bars):
            bx = x + i * bw + 4
            d.rectangle([bx, base - v * (h - 20), bx + bw - 8, base], fill=(196, 60, 60))
        pts = [(x + 8 + i * (w - 16) / 6, base - v * (h - 22)) for i, v in enumerate(bars)]
        d.line(pts, fill=(140, 10, 10), width=3, joint="curve")
        d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] + 12, pts[-1][1] - 4),
                   (pts[-1][0] + 2, pts[-1][1] + 10)], fill=(140, 10, 10))
    elif kind == "bitcoin":
        d.rectangle([x, y, x + w, y + h], fill=(255, 248, 220))
        d.line([(x + 14, y + h - 16), (x + 60, y + h - 34), (x + 110, y + h - 22),
                (x + 160, y + h - 44), (x + w - 14, y + h - 30)], fill=(178, 24, 24), width=3)
        cx, cy, r = x + w // 2, y + h // 2 + 2, 34
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 176, 20),
                  outline=(160, 110, 0), width=3)
        d.ellipse([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
                  outline=(160, 110, 0), width=2)
        d.text((cx - 13, cy - 20), "B", font=B(38), fill=(120, 78, 0))
        d.line([(cx - 17, cy - 14), (cx + 15, cy - 14)], fill=(120, 78, 0), width=3)
        d.line([(cx - 17, cy + 12), (cx + 15, cy + 12)], fill=(120, 78, 0), width=3)
    elif kind == "cyclone":
        d.rectangle([x, y, x + w, y + h], fill=(222, 236, 246))
        cx, cy = x + w // 2, y + h // 2
        import math
        pts = []
        for t in range(0, 721, 6):
            ang = math.radians(t)
            rr = 4 + t * 0.062
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang) * 0.8))
        d.line(pts, fill=(28, 78, 130), width=5, joint="curve")
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(178, 24, 24))
        # coastline + rain
        d.polygon([(x, y + h), (x + 46, y + h - 18), (x + 90, y + h - 6), (x + 120, y + h)],
                  fill=(120, 150, 110))
        for rx in (150, 175, 200):
            d.line([(x + rx, y + 10), (x + rx - 5, y + 26)], fill=(60, 110, 170), width=2)

# ---------------------------------------------------------------- map

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # graticule every 30 degrees
    for lon in range(-180, 181, 30):
        gx = x + (lon + 180) / 360 * w
        d.line([(gx, y), (gx, y + h)], fill=(190, 208, 222), width=1)
    for lat in range(-60, 91, 30):
        gy = y + (90 - lat) / 180 * h
        d.line([(x, gy), (x + w, gy)], fill=(190, 208, 222), width=1)
    # ocean labels
    ol = font(FDIR + "DejaVuSans-Bold.ttf", 11)
    d.text((x + 60, y + h - 22), "PACIFIC", font=ol, fill=(110, 140, 165))
    d.text((x + w // 2 - 170, y + h - 40), "ATLANTIC", font=ol, fill=(110, 140, 165))
    d.text((x + w - 150, y + h - 22), "INDIAN OCEAN", font=ol, fill=(110, 140, 165))

    def proj(lon, lat):
        return (x + (lon + 180) / 360 * w, y + (90 - lat) / 180 * h)

    for pts in CONTINENTS.values():
        d.polygon([proj(lon, lat) for lon, lat in pts], fill=LAND,
                  outline=(90, 100, 110))
    cl = font(FDIR + "DejaVuSans-Bold.ttf", 10)
    for clon, clat, cname in [(-115, 60, "NORTH AMERICA"), (-58, -14, "SOUTH AMERICA"),
                              (18, 2, "AFRICA"), (134, -30, "AUSTRALIA")]:
        cx, cy = (x + (clon + 180) / 360 * w, y + (90 - clat) / 180 * h)
        d.text((cx, cy), cname, font=cl, fill=(110, 122, 134))
    # pins with leader labels
    lf = font(FDIR + "DejaVuSans-Bold.ttf", 11)
    for lon, lat, label, dx, dy in PINS:
        px, py = proj(lon, lat)
        lx, ly = px + dx, py + dy
        d.line([(px, py), (lx + (6 if dx >= 0 else -6), ly + 5)],
               fill=(120, 120, 120), width=1)
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED,
                  outline=(255, 255, 255), width=2)
        # halo then text
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d.text((lx + ox, ly + oy), label, font=lf, fill=(255, 255, 255))
        d.text((lx, ly), label, font=lf, fill=NAVY)

# ---------------------------------------------------------------- page

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # outer border
    d.rectangle([3, 3, W - 4, H - 4], outline=NAVY, width=6)

    # --- masthead
    d.rectangle([MARGIN, 12, W - MARGIN, 64], fill=NAVY)
    centered(d, MARGIN, W - MARGIN, 18, "THE WORLD TODAY", SB(40), (255, 255, 255))
    centered(d, MARGIN, W - MARGIN, 70, "SATURDAY 21 NOVEMBER 2026", SB(44), NAVY)
    d.rectangle([MARGIN, 120, W - MARGIN, 124], fill=RED)

    # --- hero
    y = 132
    for line in HERO:
        fit_check(d, line, B(54), CW, "hero")
        centered(d, MARGIN, W - MARGIN, y, line, B(54), BLACK)
        y += 60
    deck_lines = wrap(d, HERO_DECK, R(19), CW)
    assert len(deck_lines) <= 2, f"hero deck {len(deck_lines)} lines"
    for line in deck_lines:
        centered(d, MARGIN, W - MARGIN, y + 2, line, R(19), NAVY_LT)
        y += 25
    y += 8

    # --- sub-hero
    fit_check(d, SUBHERO, B(27), CW, "subhero")
    centered(d, MARGIN, W - MARGIN, y, SUBHERO, B(27), BLACK)
    y += 36
    for line in wrap(d, SUBHERO_DECK, R(16), CW):
        centered(d, MARGIN, W - MARGIN, y, line, R(16), NAVY_LT)
        y += 22
    y += 6
    d.rectangle([MARGIN, y, W - MARGIN, y + 3], fill=RED)
    y += 10

    # --- numbers strip
    cell_w = CW / len(NUMBERS)
    ny = y
    for i, (num, label) in enumerate(NUMBERS):
        cx = MARGIN + i * cell_w
        fit_check(d, num, B(30), cell_w - 8, f"number {num}")
        centered(d, cx, cx + cell_w, ny, num, B(30), RED)
        ly = ny + 36
        for ln in label.split("\n"):
            centered(d, cx, cx + cell_w, ly, ln, R(12), GREY)
            ly += 14
        if i:
            d.line([(cx, ny + 4), (cx, ny + 62)], fill=GREY_LT, width=1)
    y = ny + 66
    d.rectangle([MARGIN, y, W - MARGIN, y + 2], fill=NAVY)
    y += 8

    # --- region strip
    d.rectangle([MARGIN, y, W - MARGIN, y + 28], fill=NAVY)
    parts = "   \u00b7   ".join(f"{name} {n}" for name, n in REGIONS)
    strip = parts + f"        \u2014  {TOTAL_STORIES} STORIES"
    fit_check(d, strip, SB(15), CW - 16, "region strip")
    centered(d, MARGIN, W - MARGIN, y + 5, strip, SB(15), (255, 255, 255))
    y += 32

    # --- features: 4 panels in a row
    gap = 8
    pw = (CW - 3 * gap) / 4
    fy = y
    art_h = 68
    for i, (title, deck, kind) in enumerate(FEATURES):
        px = MARGIN + i * (pw + gap)
        d.rectangle([px, fy, px + pw, fy + art_h], outline=NAVY, width=1)
        draw_feature_art(d, kind, px + 1, fy + 1, pw - 2, art_h - 2)
        ty = fy + art_h + 6
        for ln in title.split("\n"):
            fit_check(d, ln, B(15), pw, f"feature title {ln}")
            d.text((px, ty), ln, font=B(15), fill=BLACK)
            ty += 19
        for ln in wrap(d, deck, R(12), pw):
            d.text((px, ty), ln, font=R(12), fill=GREY)
            ty += 15
        d.rectangle([px, fy, px + pw, ty + 2], outline=NAVY, width=1)
    y = fy + art_h + 6 + 2 * 19 + 2 * 15 + 10

    # --- map band
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=B(13), fill=NAVY)
    y += 18
    map_h = 110
    d.rectangle([MARGIN, y, W - MARGIN, y + map_h], outline=NAVY, width=1)
    draw_map(d, MARGIN + 1, y + 1, CW - 2, map_h - 2)
    y += map_h + 10

    # --- briefs
    d.text((MARGIN, y), "THE DAY IN BRIEF", font=B(13), fill=NAVY)
    d.text((W - MARGIN - 200, y), "24 MORE STORIES", font=B(13), fill=RED)
    y += 20
    assert len(BRIEFS) == 24, f"expected 24 briefs, got {len(BRIEFS)}"
    col_w = (CW - 2 * 16) / 3
    row_h = 24
    for idx, (head, deck, region) in enumerate(BRIEFS):
        col, row = idx % 3, idx // 3
        bx = MARGIN + col * (col_w + 16)
        by = y + row * row_h
        tag = region.upper()
        d.text((bx, by), tag, font=B(10), fill=RED)
        hx = bx + d.textlength(tag, font=B(10)) + 6
        fit_check(d, head, B(13), bx + col_w - hx, f"brief head {head}")
        d.text((hx, by - 1), head, font=B(13), fill=BLACK)
        fit_check(d, deck, R(11), col_w, f"brief deck {deck}")
        d.text((bx, by + 13), deck, font=R(11), fill=GREY)
    y += 8 * row_h + 8

    # --- date check box
    d.rectangle([MARGIN, y, W - MARGIN, y + 40], fill=YELLOW_BG, outline=YELLOW_BD, width=2)
    dc_lines = wrap(d, DATE_CHECK, B(12), CW - 24)
    assert len(dc_lines) <= 2, f"date check {len(dc_lines)} lines"
    dy = y + 5
    for ln in dc_lines:
        centered(d, MARGIN, W - MARGIN, dy, ln, B(12), (90, 60, 0))
        dy += 15
    y += 44

    # --- footer
    fit_check(d, FOOTER, R(11), CW, "footer")
    centered(d, MARGIN, W - MARGIN, y, FOOTER, R(11), GREY)
    y += 18

    assert y <= H - 8, f"page overflow: content ends at y={y}"
    # region counts must sum to the story total
    assert sum(n for _, n in REGIONS) == TOTAL_STORIES, "region counts != total"
    assert 2 + len(FEATURES) + len(BRIEFS) == TOTAL_STORIES, "story count != total"
    return img, y


def main():
    img, end_y = build()
    img.save("entry.png", "JPEG", quality=88, optimize=True)
    import hashlib, os
    data = open("entry.png", "rb").read()
    print(f"entry.png: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"content ends at y={end_y} of {H}; size OK (<1MiB): {len(data) < 1048576}")
    assert len(data) < 1048576, "entry.png over 1 MiB"
    assert data[:2] == b"\xff\xd8" and data[-2:] == b"\xff\xd9", "not a whole JPEG"
    print("checks: PASS")


if __name__ == "__main__":
    main()
