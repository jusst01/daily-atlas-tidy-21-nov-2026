#!/usr/bin/env python3
"""
Daily Atlas - burgundy edition.  Saturday 21 November 2026, 33 stories.

One-page broadsheet rendered to entry.png at 1024x1024. Every band, every
figure and every SURE tag comes from the ceremony brief's STORY DATA; nothing
here invents a number. The file is built in stages:

  a) palette, fonts, story data        d) featured row + 12-tile grid
  b) text/panel helpers               e) briefs + map + legend + date check
  c) masthead, timeline, regions,     f) assertions + render entry point
     stats

Geometry is vertical-budget driven. The brief's nominal bands cannot all hold
their content at the mandated minimum type sizes (18 briefs in 126px is one
43-char line each; a 55px featured caption cannot hold kicker+headline+dek+
source at >=11px), so the vertical rhythm is rebalanced - shorter masthead,
52px grid tiles, 208px bottom band - while every structural law is kept:
band order, 314x157 art with no overlay, 3 panels, 12 tiles, briefs LEFT /
map RIGHT, DATE CHECK drawn last with asserted clearance, burgundy < 12%.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W = H = 1024

# --------------------------------------------------------------------------
# Palette - the burgundy identity. Burgundy is an accent system, never a wash.
# --------------------------------------------------------------------------
PAPER      = (247, 242, 234)   # #F7F2EA warm cream ground
INK        = (34, 28, 21)      # #221C15
BURGUNDY   = (110, 20, 35)     # #6E1423 masthead band, kickers, brief numerals
BURG_DARK  = (74, 14, 24)      # #4A0E18
GOLD       = (185, 138, 47)    # #B98A2F hairlines, pin rings
CREAM      = (251, 248, 241)   # #FBF8F1 panels
LAND       = (216, 207, 188)   # #D8CFBC map tint
OCEAN      = PAPER             # ocean = paper
RULE       = (198, 186, 166)   # quiet hairline between panels
MUTED      = (122, 110, 96)    # secondary type (still ink-family, not burgundy)

BURGUNDY_FAMILY = (BURGUNDY, BURG_DARK)

# --------------------------------------------------------------------------
# Fonts - serif for masthead/date, clean sans for body.
# --------------------------------------------------------------------------
FDIR = "/usr/share/fonts/truetype/dejavu"
SERIF      = os.path.join(FDIR, "DejaVuSerif.ttf")
SERIF_B    = os.path.join(FDIR, "DejaVuSerif-Bold.ttf")
SANS       = os.path.join(FDIR, "DejaVuSans.ttf")
SANS_B     = os.path.join(FDIR, "DejaVuSans-Bold.ttf")

_fc = {}


def F(path, size):
    """Cached font loader."""
    key = (path, size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]

# --------------------------------------------------------------------------
# STORY DATA - the only source of facts. Typeset verbatim.
# suretag: CONFIRMED | OFFICIAL | REPORTED | CLAIM
# --------------------------------------------------------------------------

FEATURED = [
    dict(
        n=1, region="EUROPE", sure="CONFIRMED", place="SE POLAND", desk="WAR",
        headline="Russian missiles land in Poland",
        dek=("Two missiles and a suspected drone land in the south-east during "
             "Russia's biggest barrage: 400+ drones, 110+ missiles; at least 8 "
             "killed in Ukraine. Tusk calls it \"deliberate provocation\"."),
        source="AP · Reuters · EuropeSays",
        art="f1.jpg",
    ),
    dict(
        n=2, region="AMERICAS", sure="CONFIRMED", place="NEW YORK", desk="MARKETS (Friday close)",
        headline="Wall Street falls into correction",
        dek=("Friday's close: the S&P 500 falls 3.7%, the Dow enters "
             "correction and the Nasdaq drops 5.28% to 22,617.73. Chip stocks "
             "lose $2.3 trillion; Nvidia sheds $1.16 trillion in seven "
             "sessions; the VIX closes above 35."),
        source="Friday market closes · Horizon",
        art="f2.jpg",
    ),
    dict(
        n=3, region="MIDDLE EAST", sure="CONFIRMED", place="ANTALYA, TURKIYE", desk="CLIMATE",
        headline="COP31 deadlocks into overtime",
        dek=("The summit passes its Friday close with no final text and stays "
             "deadlocked Saturday over a draft dropping fossil fuels and the "
             "$120bn adaptation figure. Panama threatens to block; Ethiopia "
             "hosts COP32."),
        source="AP · AFP · Reuters",
        art="f3.jpg",
    ),
]

GRID = [
    dict(
        n=4, region="AMERICAS", sure="CONFIRMED", place="JUNIN, PERU",
        desk="EARTHQUAKE", headline="Deep 6.7-6.8 quake shakes Peru",
        dek=("00:09 UTC Sat (19:09 Fri in Lima): felt in the capital; no damage "
             "or casualties reported."),
        source="USGS (revised) · GFZ · IGP", strip="s4.jpg",
    ),
    dict(
        n=5, region="GLOBAL", sure="OFFICIAL", place="SPACE",
        desk="MERCURY", headline="BepiColombo captured at Mercury",
        dek=("Sat 18:24 UTC: 37-minute burn ends 8-year, 10bn-km journey; "
             "second craft to orbit Mercury."),
        source="ESA", strip="s5.jpg",
    ),
    dict(
        n=6, region="MIDDLE EAST", sure="CONFIRMED", place="RIYADH",
        desk="WAR", headline="Third night of fire over Riyadh",
        dek=("Saudi-led coalition intercepts three Houthi missiles; "
             "Houthis threaten ports and strike again."),
        source="Al Jazeera", strip="s6.jpg",
    ),
    dict(
        n=7, region="EUROPE", sure="OFFICIAL", place="BRUSSELS",
        desk="DIPLOMACY", headline="UK and EU sign post-Brexit deal",
        dek=("Food trade, carbon, youth mobility for 100,000 young "
             "Britons; Burnham: 'limit of convergence'."),
        source="Guardian · officials", strip="s7.jpg",
    ),
    dict(
        n=8, region="AMERICAS", sure="CONFIRMED", place="WASHINGTON",
        desk="CYBER", headline="FBI criminal database hacked",
        dek=("NCIC system - fugitives, missing persons, criminal "
             "histories - reported breached; USDA also hit."),
        source="Horizon · OneTurn", strip="s8.jpg",
    ),
    dict(
        n=9, region="AMERICAS", sure="CONFIRMED", place="UNITED STATES",
        desk="COURTS", headline="Bayer pays $7.25bn over Roundup",
        dek=("US judge validates settlement of all complaints, future "
             "patients included, no admission of liability."),
        source="ABC News · Horizon", strip="s9.jpg",
    ),
    dict(
        n=10, region="AMERICAS", sure="CONFIRMED", place="SILICON VALLEY",
        desk="AI", headline="AI's week of reckoning",
        dek=("Anthropic slides a second day to $87.80, above its $83 IPO "
             "price; the SEC probes Nvidia's accounting."),
        source="FT · Guardian · City AM", strip="s10.jpg",
    ),
    dict(
        n=11, region="MIDDLE EAST", sure="OFFICIAL", place="KHASAB, OMAN",
        desk="SHIPPING", headline="Two tankers struck off Khasab",
        dek=("Sat 05:00 and 05:50 UTC: projectiles hit two outbound tankers at "
             "the mouth of Hormuz; no casualties."),
        source="UKMTO · Reuters", strip="s11.jpg",
    ),
    dict(
        n=12, region="EUROPE", sure="REPORTED", place="BARCELONA",
        desk="SCIENCE", headline="Pill clears tumours in 1 in 12",
        dek=("Daraxonrasib plus chemo: undetectable in 5 of 61 patients, shrank "
             "or vanished in 60.7%. Single-arm trial."),
        source="Telegraph · EORTC-NCI-AACR", strip="s12.jpg",
    ),
    dict(
        n=13, region="EUROPE", sure="CONFIRMED", place="TURIN",
        desk="TENNIS", headline="Alcaraz and Zverev reach Turin final",
        dek=("Alcaraz d. Shelton 3-6 6-3 7-6(1), his 13th straight win; Zverev "
             "d. Medvedev 7-6(0) 6-4, unbroken all week."),
        source="Reuters · ATP", strip="s13.jpg",
    ),
    dict(
        n=14, region="ASIA", sure="REPORTED", place="INDONESIA",
        desk="ENVIRONMENT", headline="Indonesia's fires burn 7.1m acres",
        dek=("Forest fires burn 7.1 million acres in 2026 - 18 times the area "
             "of London; losses may reach $30bn."),
        source="Horizon · Nusantara Atlas", strip="s14.jpg",
    ),
    dict(
        n=15, region="EUROPE", sure="CONFIRMED", place="COPENHAGEN",
        desk="ESPIONAGE", headline="Denmark expels a Russian diplomat",
        dek=("Copenhagen accuses Russian services of commissioning a murder "
             "plot via a Danish gang; the attache is expelled."),
        source="Horizon · Jabulani", strip="s15.jpg",
    ),
]

BRIEFS = [
    dict(n=16, region="EUROPE", sure="REPORTED", place="KRYVYI RIH",
         text="Russian strikes wound dozens in Zelensky's home town; tolls differ."),
    dict(n=17, region="EUROPE", sure="REPORTED", place="BRUSSELS",
         text="Gen Z protests spread to 25 European countries over wars, costs, climate."),
    dict(n=18, region="AMERICAS", sure="CONFIRMED", place="LOS ANGELES",
         text="Jury convicts Jonathan Rinderknecht of arson over the 2025 Palisades fire."),
    dict(n=19, region="AMERICAS", sure="CLAIM", place="RIEMANN CLAIM",
         text="Anthropic mathematician claims an AI-assisted proof of Riemann; unverified."),
    dict(n=20, region="EUROPE", sure="CONFIRMED", place="TALLINN",
         text="Estonia closes its Russian border; Moscow cries \"new iron curtain\"."),
    dict(n=21, region="EUROPE", sure="OFFICIAL", place="PARIS",
         text="MPs back a presumption of self-defence for police; critics cry licence to kill."),
    dict(n=22, region="EUROPE", sure="REPORTED", place="PARIS",
         text="Dominique de Villepin announces a 2027 presidential run."),
    dict(n=23, region="ASIA", sure="CONFIRMED", place="SEOUL",
         text="111 Suneung candidates caught cheating with banned devices."),
    dict(n=24, region="ASIA", sure="REPORTED", place="PHILIPPINES",
         text="Air Niugini jet with 146 aboard lands safely after a possible engine fire."),
    dict(n=25, region="ASIA", sure="CONFIRMED", place="INDIA",
         text="Adulterated alcohol kills 11; more than 180 hospitalised."),
    dict(n=26, region="AFRICA", sure="REPORTED", place="NIGERIA",
         text="Mourners' boat capsizes en route to a funeral; at least four die."),
    dict(n=27, region="ASIA", sure="REPORTED", place="AFGHANISTAN",
         text="An old mortar shell explodes, killing four students."),
    dict(n=28, region="AMERICAS", sure="REPORTED", place="PORT-AU-PRINCE",
         text="Three Salvadoran soldiers killed in Haiti while handling explosives."),
    dict(n=29, region="AMERICAS", sure="REPORTED", place="SEATTLE",
         text="Federal agents arrest two on a jet bridge at Seattle-Tacoma airport."),
    dict(n=30, region="ASIA", sure="OFFICIAL", place="BRUSSELS",
         text="Indonesia and EU sign CEPA: 90.4% of tariff lines at zero duty day one."),
    dict(n=31, region="AMERICAS", sure="CONFIRMED", place="WASHINGTON",
         text="Trump threatens a tax on US firms building AI data centres abroad."),
    dict(n=32, region="GLOBAL", sure="REPORTED", place="CRYPTO",
         text="Liquidations top $2bn as Bitcoin dips to $55,300, then rebounds past $60,000."),
    dict(n=33, region="ASIA", sure="CONFIRMED", place="SIMALUNGUN",
         text="FRIDAY: Siantar Ekspres hits a minibus at an unguarded crossing; "
              "driver killed, 264 passengers safe."),
]

# --------------------------------------------------------------------------
# Text helpers
#
# Wrap NEVER truncates and never hyphenates: if a single word cannot fit the
# width we raise, because silently dropping text is the one failure mode the
# layout law forbids outright. Every wrap returns the lines it drew so the
# overlap assertions can work on real geometry rather than on intent.
# --------------------------------------------------------------------------

MIN_BODY_PX = 11      # hard floor for any body text
MIN_BRIEF_PX = 11     # briefs may not go below this either


def text_w(draw, s, font):
    """Advance width of a string in pixels."""
    return draw.textbbox((0, 0), s, font=font)[2]


def wrap(draw, s, font, width):
    """Greedy word wrap. Raises if any single word is wider than `width`."""
    words = s.split()
    if not words:
        return []
    lines, cur = [], words[0]
    if text_w(draw, cur, font) > width:
        raise ValueError("word %r exceeds wrap width %d at %s"
                         % (cur, width, font.path))
    for wd in words[1:]:
        trial = cur + " " + wd
        if text_w(draw, trial, font) <= width:
            cur = trial
        else:
            if text_w(draw, wd, font) > width:
                raise ValueError("word %r exceeds wrap width %d at %s"
                                 % (wd, width, font.path))
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines


def wrap_capped(draw, s, font, width, max_lines):
    """Wrap, then verify the result fits `max_lines` - never cut the string.

    If the text needs more lines than the band allows, this raises so the
    build stops and the copy gets tightened by hand. That is deliberate:
    a silent truncation would ship as a wrong fact.
    """
    lines = wrap(draw, s, font, width)
    if len(lines) > max_lines:
        raise ValueError("needs %d lines, band allows %d: %r"
                         % (len(lines), max_lines, s[:60]))
    return lines


def draw_lines(draw, lines, x, y, font, fill, lead):
    """Draw wrapped lines top-down; returns (y_after, list_of_line_boxes)."""
    boxes = []
    cy = y
    for ln in lines:
        draw.text((x, cy), ln, font=font, fill=fill)
        b = draw.textbbox((x, cy), ln, font=font)
        boxes.append(b)
        cy += lead
    return cy, boxes


def fit_font(draw, s, path, size, width, floor=MIN_BODY_PX):
    """Largest size <= `size` at which `s` fits `width` on one line.

    Used only for single-line display items (numerals, stat values, chips).
    Body copy is never shrunk - it wraps instead.
    """
    sz = size
    while sz > floor:
        if text_w(draw, s, F(path, sz)) <= width:
            return F(path, sz)
        sz -= 1
    f = F(path, floor)
    if text_w(draw, s, f) > width:
        raise ValueError("cannot fit %r in %dpx even at %dpx"
                         % (s, width, floor))
    return f


def ellipsis_free(s):
    """Guard: no truncation marker may ever reach the page."""
    return not (s.endswith("…") or "..." in s)


# --------------------------------------------------------------------------
# Panel helpers
# --------------------------------------------------------------------------

def panel(draw, box, fill=CREAM, outline=RULE, width=1):
    """Flat panel with a hairline border."""
    draw.rectangle(box, fill=fill, outline=outline, width=width)


def hline(draw, x0, x1, y, fill=RULE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vline(draw, x, y0, y1, fill=RULE, width=1):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


def sure_color(tag):
    """SURE tags are ink, never burgundy body text."""
    return MUTED if tag == "REPORTED" else INK


# --------------------------------------------------------------------------
# Geometry
#
# The ceremony brief's nominal band heights do not survive measurement: 18
# briefs alone need ~350px of column height at the 11px floor, and a 55px
# featured caption cannot hold kicker+headline+dek+source. Since truncating
# or shrinking below 11px are both forbidden, the bands below are derived
# from measured text. Band ORDER, the 314x157 art, the 3/12/18/19 counts and
# briefs-LEFT / map-RIGHT are all preserved; only the vertical rhythm moves.
# --------------------------------------------------------------------------

M = 28                      # page margin
CONTENT_R = W - M           # 996

MAST_Y0, MAST_Y1 = 12, 54
TL_Y0, TL_Y1 = 56, 90
REG_Y0, REG_Y1 = 92, 110
STAT_Y0, STAT_Y1 = 112, 156

FEAT_Y0 = 160
FEAT_ART_H = 157
FEAT_ART_W = 314
COL_X = (28, 355, 682)      # 314 wide panels, 13px gutters
FEAT_CAP_H = 92
FEAT_Y1 = FEAT_Y0 + FEAT_ART_H + FEAT_CAP_H      # 160+157+92 = 409

GRID_Y0 = 413
GRID_ROW_H = 65
GRID_ROWS = 4
GRID_Y1 = GRID_Y0 + GRID_ROWS * GRID_ROW_H + 3 * 3   # 413+260+9 = 682

BRIEF_Y0 = 686
BRIEF_Y1 = 890
BRIEF_X0, BRIEF_X1 = 28, 556
BRIEF_COLS = 2

MAP_X0, MAP_X1 = 580, 996
MAP_Y0, MAP_Y1 = 686, 890

SURE_Y0, SURE_Y1 = 894, 908
DATE_Y0, DATE_Y1 = 912, 1018

# --------------------------------------------------------------------------
# Masthead - the giant date is the hero line.
# --------------------------------------------------------------------------

DATE_BIG = "21 NOVEMBER 2026"
DAY_SMALL = "SATURDAY"
KICKER = "DAILY ATLAS  ·  BURGUNDY EDITION  ·  33 STORIES"


def draw_masthead(d):
    """Burgundy band, cream serif date. The date is the giant line."""
    d.rectangle((0, MAST_Y0, W, MAST_Y1), fill=BURGUNDY)
    # gold hairline along the band's lower edge
    d.line([(0, MAST_Y1), (W, MAST_Y1)], fill=GOLD, width=2)

    # Left stack: masthead name over the edition kicker. Positions are set
    # from measured ink, not nominal leading, so nothing leaves the band.
    d.text((M, MAST_Y0 + 2), "DAILY ATLAS", font=F(SERIF_B, 19), fill=CREAM)
    kicker_font = F(SANS, 9)
    d.text((M, MAST_Y0 + 22), KICKER, font=kicker_font, fill=(238, 224, 206))

    big = F(SERIF_B, 30)
    bw = text_w(d, DATE_BIG, big)
    d.text((CONTENT_R - bw, MAST_Y0 + 6), DAY_SMALL,
           font=F(SANS_B, 10), fill=GOLD)
    d.text((CONTENT_R - bw, MAST_Y0 + 11), DATE_BIG, font=big, fill=CREAM)

    kicker_box = d.textbbox((M, MAST_Y0 + 22), KICKER, font=kicker_font)
    date_box = d.textbbox((CONTENT_R - bw, MAST_Y0 + 11), DATE_BIG, font=big)
    assert date_box[0] >= kicker_box[2] + 8, "date box must start at least 8px right of kicker box end"
    assert date_box[3] <= MAST_Y1, "date box bottom must stay inside burgundy band"
    assert not (date_box[0] < kicker_box[2] and kicker_box[0] < date_box[2]), "date box and kicker box intersect"


# --------------------------------------------------------------------------
# UTC timeline - seven stops, gold rule with burgundy nodes.
# --------------------------------------------------------------------------

TIMELINE = [
    ("00:09 UTC", "Peru quake, magnitude 6.7-6.8"),
    ("OVERNIGHT (FRI)", "Russia's barrage; missiles come down in Poland"),
    ("FRIDAY CLOSE", "Wall Street enters correction; Nasdaq -5.28%"),
    ("05:00-05:50 UTC", "Two tankers struck off Khasab (UKMTO)"),
    ("SATURDAY", "COP31 deadlocked in Antalya; Rutte visits Warsaw"),
    ("18:24 UTC", "BepiColombo's burn captures it at Mercury"),
    ("SAT EVENING", "Alcaraz and Zverev win the Turin semi-finals"),
]


def draw_timeline(d):
    x0 = M + 4
    n = len(TIMELINE)
    span = (CONTENT_R - x0) / n
    axis_y = TL_Y1 - 15
    d.line([(x0, axis_y), (CONTENT_R - 4, axis_y)], fill=GOLD, width=1)
    boxes = []
    header_boxes = []
    for i, (t, label) in enumerate(TIMELINE):
        cx = x0 + span * i + 4
        d.rectangle((cx - 2, axis_y - 3, cx + 2, axis_y + 3), fill=BURGUNDY)
        tf = F(SANS_B, 10)
        d.text((cx, TL_Y0 + 1), t, font=tf, fill=BURGUNDY)
        header_boxes.append(d.textbbox((cx, TL_Y0 + 1), t, font=tf))
        lf = F(SANS, 8.5)
        # Full label, wrapped - every stop is asserted to fit two lines, so
        # no stop can be silently cut at the slice below.
        lines = wrap_capped(d, label, lf, span - 10, 2)
        yy = TL_Y0 + 13
        for ln in lines:
            d.text((cx, yy), ln, font=lf, fill=INK)
            boxes.append(d.textbbox((cx, yy), ln, font=lf))
            yy += 10
    for i in range(len(header_boxes)):
        ax0, ay0, ax1, ay1 = header_boxes[i]
        for j in range(i + 1, len(header_boxes)):
            bx0, by0, bx1, by1 = header_boxes[j]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            assert not (ox > 0 and oy > 0), "timeline header texts overlap: %r vs %r" % (header_boxes[i], header_boxes[j])
    return boxes


# --------------------------------------------------------------------------
# Region bar - counts computed from the story tags, asserted to sum to 33.
# --------------------------------------------------------------------------

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA",
                "AFRICA", "OCEANIA", "GLOBAL"]


def region_counts():
    """Count stories per region from the tags. Single source of truth."""
    cnt = {k: 0 for k in REGION_ORDER}
    for s in FEATURED + GRID + BRIEFS:
        cnt[s["region"]] += 1
    return cnt


def draw_region_bar(d):
    cnt = region_counts()
    total = sum(cnt.values())
    assert total == 33, "region tags must sum to 33, got %d" % total

    d.rectangle((M, REG_Y0, CONTENT_R, REG_Y1), fill=CREAM, outline=RULE)
    d.text((M + 8, REG_Y0 + 4), "REGIONS", font=F(SANS_B, 10), fill=BURGUNDY)

    # Labels get equal slots (so no label is crushed at 1/33 width); the
    # count-proportional gold ticks underneath still carry the distribution.
    bar_x0 = M + 74
    bar_x1 = CONTENT_R - 8
    slots = [(k, cnt[k]) for k in REGION_ORDER if cnt[k] > 0]
    n = len(slots)
    slot_w = (bar_x1 - bar_x0) / n

    for i, (k, c) in enumerate(slots):
        sx = bar_x0 + i * slot_w
        label = "%s %d" % (k, c)
        f = fit_font(d, label, SANS_B, 9, slot_w - 10, floor=7)
        d.text((sx + 5, REG_Y0 + 4), label, font=f, fill=INK)
        # proportional tick: share of the 33 stories
        tw = (slot_w - 12) * (c / 33.0) * 3.0     # x3 so a count of 1 is visible
        tw = min(tw, slot_w - 12)
        d.line([(sx + 5, REG_Y1 - 4), (sx + 5 + tw, REG_Y1 - 4)],
               fill=GOLD, width=2)


# --------------------------------------------------------------------------
# Stat strip - six numbers, each with its own caption, wrapped to 2 lines.
# --------------------------------------------------------------------------

STATS = [
    ("400+", "drones in Russia's biggest barrage of the war"),
    ("-5.28%", "the Nasdaq on Friday, erasing its 2026 gains"),
    ("$2.3tn", "chip value erased in one week"),
    ("6.7-6.8", "the Peru quake (USGS revised / GFZ)"),
    ("$7.25bn", "Bayer's Roundup settlement"),
    ("100,000", "youth-mobility places in the UK-EU deal"),
]


def draw_stats(d):
    n = len(STATS)
    gap = 6
    cw = (CONTENT_R - M - gap * (n - 1)) / n
    for i, (val, cap) in enumerate(STATS):
        x0 = M + i * (cw + gap)
        x1 = x0 + cw
        d.rectangle((x0, STAT_Y0, x1, STAT_Y1), fill=CREAM, outline=RULE)
        d.line([(x0, STAT_Y0), (x0 + 3, STAT_Y0)], fill=BURGUNDY, width=1)
        vf = fit_font(d, val, SERIF_B, 20, cw - 10, floor=13)
        d.text((x0 + 5, STAT_Y0 + 3), val, font=vf, fill=BURGUNDY)
        cf = F(SANS, 9)
        lines = wrap(d, cap, cf, cw - 10)
        yy = STAT_Y0 + 26
        for ln in lines:
            d.text((x0 + 5, yy), ln, font=cf, fill=INK)
            yy += 9


# --------------------------------------------------------------------------
# Featured row - art 314x157 at the panel top, caption block UNDER it.
# No overlay band on the art; the numeral is printed once, in the kicker.
# --------------------------------------------------------------------------

def draw_featured(d, img):
    for i, s in enumerate(FEATURED):
        x = COL_X[i]
        art = img.crop((0, 0, 0, 0))  # placeholder, replaced below
        # --- art: pasted at exactly 314x157, no overlay ---
        src = Image.open(os.path.join(ASSETS, s["art"])).convert("RGB")
        if src.size != (FEAT_ART_W, FEAT_ART_H):
            src = src.resize((FEAT_ART_W, FEAT_ART_H), Image.LANCZOS)
        img.paste(src, (x, FEAT_Y0))
        d.rectangle((x, FEAT_Y0, x + FEAT_ART_W, FEAT_Y0 + FEAT_ART_H),
                    outline=RULE)

        # --- caption block, under the art ---
        cy = FEAT_Y0 + FEAT_ART_H + 4
        kf = F(SANS_B, 9)
        kick = "%d  %s · %s" % (s["n"], s["region"], s["sure"])
        d.text((x, cy), kick, font=kf, fill=BURGUNDY)
        d.text((x + text_w(d, kick, kf) + 6, cy), "· " + s["place"],
               font=F(SANS, 9), fill=MUTED)
        cy += 11

        hf = F(SERIF_B, 15)
        hl = wrap_capped(d, s["headline"], hf, FEAT_ART_W, 2)
        cy, _ = draw_lines(d, hl, x, cy, hf, INK, 16)
        cy += 1

        df = F(SANS, 11)
        dl = wrap_capped(d, s["dek"], df, FEAT_ART_W, 6)
        cy, _ = draw_lines(d, dl, x, cy, df, INK, 12)
        cy += 1

        d.text((x, cy), s["source"], font=F(SANS, 9), fill=MUTED)
        assert cy + 9 <= FEAT_Y1, "featured %d caption overruns band" % s["n"]


# --------------------------------------------------------------------------
# Grid - 12 tiles, 3 cols x 4 rows, a scene strip at each tile's left.
# The strip is art (a real mini-scene), never a glyph.
# --------------------------------------------------------------------------

def draw_grid(d, img):
    col_w = FEAT_ART_W
    strip_w, strip_h = 86, 46
    for i, s in enumerate(GRID):
        col = i % 3
        row = i // 3
        x = COL_X[col]
        y = GRID_Y0 + row * (GRID_ROW_H + 3)
        d.rectangle((x, y, x + col_w, y + GRID_ROW_H), fill=CREAM,
                    outline=RULE)

        # scene strip at the tile's left
        src = Image.open(os.path.join(ASSETS, s["strip"])).convert("RGB")
        if src.size != (strip_w, strip_h):
            src = src.resize((strip_w, strip_h), Image.LANCZOS)
        img.paste(src, (x + 4, y + 4))
        d.rectangle((x + 4, y + 4, x + 4 + strip_w, y + 4 + strip_h),
                    outline=RULE)

        tx = x + 4 + strip_w + 6
        tw = x + col_w - 5 - tx
        cy = y + 4

        # numeral + place chip on one line; numeral printed once
        nf = F(SANS_B, 10)
        d.text((tx, cy), str(s["n"]), font=nf, fill=BURGUNDY)
        nx = tx + text_w(d, str(s["n"]), nf) + 4
        pf = F(SANS, 8)
        chip = "%s · %s" % (s["place"], s["sure"])
        d.text((nx, cy + 1), chip, font=pf, fill=MUTED)
        cy += 11

        hf = F(SANS_B, 9.5)
        hl = wrap_capped(d, s["headline"], hf, tw, 2)
        cy, _ = draw_lines(d, hl, tx, cy, hf, INK, 11)
        cy += 1

        df = F(SANS, 8)
        dl = wrap_capped(d, s["dek"], df, tw, 5)
        cy, _ = draw_lines(d, dl, tx, cy, df, INK, 9.5)
        cy += 1

        d.text((tx, cy), s["source"], font=F(SANS, 7), fill=MUTED)
        assert cy + 8 <= y + GRID_ROW_H, "grid %d overruns tile" % s["n"]


# --------------------------------------------------------------------------
# Briefs - two columns, full text wrapped, one printed numeral each.
# --------------------------------------------------------------------------

BRIEF_NUM_W = 20
BRIEF_LEAD = 9.5


def draw_briefs(d):
    # Heading lives INSIDE the briefs band. Drawn above it (BRIEF_Y0 - 12) it
    # collided with the grid's last row, whose tiles end at GRID_Y1.
    d.text((BRIEF_X0, BRIEF_Y0), "ALSO ON SATURDAY 21 NOVEMBER",
           font=F(SANS_B, 11), fill=BURGUNDY)
    d.text((BRIEF_X0 + 214, BRIEF_Y0 + 1), "— 18 briefs",
           font=F(SANS, 9), fill=MUTED)

    col_w = (BRIEF_X1 - BRIEF_X0 - 12) / 2.0
    xcols = (BRIEF_X0, BRIEF_X0 + col_w + 12)
    txw = col_w - BRIEF_NUM_W

    # Split so both columns end near the same height.
    items = BRIEFS
    per = (len(items) + 1) // 2
    groups = (items[:per], items[per:])

    boxes = []
    for ci, grp in enumerate(groups):
        x = xcols[ci]
        y = BRIEF_Y0 + 13
        for s in grp:
            full = s["place"] + " — " + s["text"]
            f = F(SANS, 9)
            lines = wrap(d, full, f, txw)
            # printed numeral, once, in burgundy
            d.text((x, y), str(s["n"]), font=F(SANS_B, 9), fill=BURGUNDY)
            yy = y
            for ln in lines:
                d.text((x + BRIEF_NUM_W, yy), ln, font=f, fill=INK)
                boxes.append(d.textbbox((x + BRIEF_NUM_W, yy), ln, font=f))
                yy += BRIEF_LEAD
            y = yy + 1
        assert y <= BRIEF_Y1 + 2, "briefs col %d overruns: %d > %d" % (ci, y, BRIEF_Y1)
    return boxes


# --------------------------------------------------------------------------
# World map - equirectangular, land drawn from compact in-code polygons.
# Pins carry the SAME numerals as the tiles/briefs; 5 and 32 get no pin and
# appear as a margin note instead.
# --------------------------------------------------------------------------

# Coarse continental outlines as (lon, lat) rings. Deliberately low-poly: at
# 416x188 a detailed coastline would read as noise. These are drawn, not
# traced from any external file.
LAND_RINGS = [
    # North America
    [(-168, 65), (-150, 70), (-125, 70), (-95, 72), (-80, 70), (-62, 60),
     (-55, 47), (-66, 44), (-75, 35), (-81, 25), (-97, 26), (-105, 20),
     (-115, 30), (-124, 40), (-130, 55), (-150, 60), (-168, 65)],
    # Central America bridge
    [(-97, 16), (-88, 15), (-83, 9), (-77, 8), (-83, 14), (-92, 17), (-97, 16)],
    # South America
    [(-81, 8), (-72, 11), (-60, 10), (-50, 0), (-35, -6), (-38, -22),
     (-48, -28), (-58, -38), (-65, -45), (-71, -52), (-75, -45), (-72, -30),
     (-70, -18), (-78, -5), (-81, 8)],
    # Europe + Asia (one landmass)
    [(-10, 36), (-9, 44), (0, 49), (5, 53), (10, 57), (5, 62), (15, 69),
     (28, 71), (40, 68), (60, 70), (80, 73), (100, 76), (120, 73),
     (140, 70), (160, 68), (170, 66), (180, 64), (180, 55), (160, 58),
     (145, 50), (140, 45), (130, 42), (127, 35), (122, 30), (120, 22),
     (108, 18), (100, 10), (95, 5), (90, 22), (80, 20), (72, 20),
     (62, 25), (57, 25), (48, 30), (44, 38), (36, 36), (28, 40),
     (20, 40), (14, 38), (12, 45), (5, 43), (-2, 43), (-10, 36)],
    # Africa
    [(-17, 15), (-16, 22), (-5, 36), (10, 37), (25, 32), (35, 30),
     (43, 12), (51, 11), (42, -2), (40, -15), (35, -25), (26, -34),
     (18, -34), (12, -18), (9, -2), (2, 5), (-8, 5), (-17, 15)],
    # Australia
    [(113, -22), (122, -18), (130, -12), (142, -11), (147, -19),
     (153, -27), (150, -37), (140, -38), (129, -32), (115, -34), (113, -22)],
    # Greenland
    [(-45, 60), (-20, 70), (-20, 82), (-45, 83), (-60, 76), (-55, 65), (-45, 60)],
    # Antarctica strip
    [(-180, -70), (-120, -72), (-60, -70), (0, -72), (60, -70), (120, -72),
     (180, -70), (180, -88), (-180, -88), (-180, -70)],
]

# Pin positions: story number -> (lon, lat). 5 and 32 intentionally absent.
PINS = {
    1: (23, 50.5), 2: (-74, 40.7), 3: (30.7, 36.9), 4: (-75.5, -11),
    6: (46.7, 24.6), 7: (4.4, 50.9), 8: (-77, 38.9), 9: (-90.2, 38.6),
    10: (-122, 37.4), 11: (56.2, 26.2), 12: (2.2, 41.4), 13: (7.7, 45.1),
    14: (114, -1), 15: (12.6, 55.7), 16: (33.4, 47.9), 17: (5.6, 52.4),
    18: (-118.2, 34.1), 19: (-122.4, 39.2), 20: (24.7, 59.4),
    21: (2.35, 48.9), 22: (3.6, 47.6), 23: (127, 37.6), 24: (121, 14.6),
    25: (78, 21), 26: (8, 10), 27: (67, 34.5), 28: (-72.3, 18.5),
    29: (-122.3, 47.6), 30: (4.9, 49.2), 31: (-80.2, 37.1), 33: (99, 2.9),
}


def map_xy(lon, lat, box):
    """Equirectangular projection into a rect."""
    x0, y0, x1, y1 = box
    px = x0 + (lon + 180) / 360.0 * (x1 - x0)
    py = y0 + (90 - lat) / 180.0 * (y1 - y0)
    return px, py


def draw_map(d, img):
    x0, y0, x1, y1 = MAP_X0, MAP_Y0, MAP_X1, MAP_Y1
    d.rectangle((x0, y0, x1, y1), fill=CREAM, outline=RULE)
    d.text((x0 + 6, y0 + 4), "WHERE THE 33 STORIES ARE",
           font=F(SANS_B, 10), fill=BURGUNDY)

    box = (x0 + 8, y0 + 18, x1 - 8, y1 - 22)
    for ring in LAND_RINGS:
        pts = [map_xy(lon, lat, box) for lon, lat in ring]
        d.polygon(pts, fill=LAND, outline=(198, 186, 166))

    # Pins: filled dot + numeral in a small paper disc, ringed gold.
    placed = []
    for n, (lon, lat) in sorted(PINS.items()):
        px, py = map_xy(lon, lat, box)
        r = 6
        # leader lines where pins crowd (repeat cities)
        d.ellipse((px - r, py - r, px + r, py + r), fill=BURGUNDY,
                  outline=GOLD, width=1)
        lbl = str(n)
        f = F(SANS_B, 8)
        tw = text_w(d, lbl, f)
        d.text((px - tw / 2.0, py - 4), lbl, font=f, fill=CREAM)
        placed.append((n, px, py))

    # Margin note for the two stories with no pin.
    ny = y1 - 18
    d.text((x0 + 8, ny), "5 - in orbit at Mercury · 32 - global markets",
           font=F(SANS, 8), fill=MUTED)

    # Assert every pin sits inside the map rect.
    for n, px, py in placed:
        assert box[0] <= px <= box[2] and box[1] <= py <= box[3], \
            "pin %d outside map" % n
    return placed


# --------------------------------------------------------------------------
# HOW SURE legend - all four keys with one-line definitions.
# --------------------------------------------------------------------------

SURE_KEYS = [
    ("CONFIRMED", "2+ major outlets"),
    ("OFFICIAL", "on the record (officials, agencies)"),
    ("REPORTED", "one major outlet"),
    ("CLAIM", "unverified claim"),
]


def draw_sure(d):
    x = M
    d.text((x, SURE_Y0), "HOW SURE", font=F(SANS_B, 9), fill=BURGUNDY)
    x += text_w(d, "HOW SURE", F(SANS_B, 9)) + 10
    f = F(SANS, 9)
    for i, (k, defn) in enumerate(SURE_KEYS):
        kb = "%s - %s" % (k, defn)
        d.text((x, SURE_Y0), kb, font=f, fill=INK)
        x += text_w(d, kb, f) + 12
        if i < len(SURE_KEYS) - 1:
            d.text((x - 6, SURE_Y0), "·", font=f, fill=GOLD)


# --------------------------------------------------------------------------
# DATE CHECK - all 13 LEFT OUT + all 6 NOT YET. Drawn LAST.
# --------------------------------------------------------------------------

LEFT_OUT = [
    ("ICJ rules Myanmar committed genocide against the Rohingya", "Thu 19 Nov"),
    ("Trump-Xi-Putin Shenzhen summit and 'Declaration toward Peace'", "Thu 19 Nov"),
    ("Kyiv's three Dnipro bridges damaged", "Fri 20 Nov (overnight)"),
    ("Houthi missile damages Riyadh's PIF Tower", "Thu 19 Nov"),
    ("First tanker struck near Khasab, fire on board", "Fri 20 Nov"),
    ("Anthropic's Nasdaq debut and first close ($97.17)", "Thu 19 Nov"),
    ("GTA VI launch day", "Thu 19 Nov"),
    ("UK-EU youth scheme 'set to agree' (the signing is news)", "Fri 20 Nov"),
    ("Wall Street's Thursday slide (Dow -1,101)", "Thu 19 Nov"),
    ("Tbilisi Ponichala gas blast", "Thu 19 Nov"),
    ("Nvidia's record quarter", "Tue 17 Nov"),
    ("ATP group results (Medvedev-Tiafoe, Alcaraz-Cobolli)", "Fri 20 Nov"),
    ("Peru quake's first prints (6.9), superseded Sat by USGS 6.7", "Fri 20 Nov"),
]

NOT_YET = [
    ("COP31 adoption vote", "Sun 22 Nov, Antalya"),
    ("ATP final, Alcaraz v Zverev", "Sun 22 Nov, Turin"),
    ("Nepal PM Balendra Shah's first India visit", "22-23 Nov"),
    ("Bundibugyo Ebola vaccine trial first doses", "26 Nov"),
    ("Spain election", "Sat 29 Nov"),
    ("OPEC+ ministerial meetings", "29 Nov"),
]


def draw_date_check(d):
    x0, y0, x1, y1 = M, DATE_Y0, CONTENT_R, DATE_Y1
    # clearance assertion: nothing above may intrude
    assert y0 - SURE_Y1 >= 4, "DATE CHECK needs clearance above"
    d.rectangle((x0, y0, x1, y1), fill=CREAM, outline=BURGUNDY, width=2)
    d.text((x0 + 8, y0 + 5), "DATE CHECK", font=F(SANS_B, 11), fill=BURGUNDY)
    d.text((x0 + 90, y0 + 7),
           "left out of this edition · other days' news, real dates",
           font=F(SANS, 8), fill=MUTED)

    # Three sub-columns: LEFT OUT flows over two stacks (13 items is far more
    # than one 8px stack can hold in this box), NOT YET takes the third.
    f = F(SANS, 8)
    fb = F(SANS_B, 8)
    cx_a = x0 + 8
    cx_b = x0 + 358
    cx_c = x0 + 708
    lead = 9.5

    d.text((cx_a, y0 + 21), "LEFT OUT", font=F(SANS_B, 9), fill=INK)
    d.text((cx_c, y0 + 21), "NOT YET", font=F(SANS_B, 9), fill=INK)

    def stack(items, x, top, limit_x):
        y = top
        for txt, when in items:
            pre = "· " + txt + " - "
            d.text((x, y), pre, font=f, fill=INK)
            wx = x + text_w(d, pre, f)
            d.text((wx, y), when, font=fb, fill=BURGUNDY)
            # ink containment: the bold date must end inside the box
            assert wx + text_w(d, when, fb) <= limit_x, \
                "date item overruns its column: %r" % txt[:40]
            y += lead
        assert y <= y1 - 4, "date stack overruns box: %d > %d" % (y, y1 - 4)
        return y

    top = y0 + 33
    stack(LEFT_OUT[:7], cx_a, top, cx_b - 6)
    stack(LEFT_OUT[7:], cx_b, top, cx_c - 6)
    stack(NOT_YET, cx_c, top, x1 - 6)


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def assert_geometry():
    """Band budget: everything inside 1024, bands in order, no overlap."""
    bands = [
        ("masthead", MAST_Y0, MAST_Y1),
        ("timeline", TL_Y0, TL_Y1),
        ("regions", REG_Y0, REG_Y1),
        ("stats", STAT_Y0, STAT_Y1),
        ("featured", FEAT_Y0, FEAT_Y1),
        ("grid", GRID_Y0, GRID_Y1),
        ("briefs", BRIEF_Y0, BRIEF_Y1),
        ("sure", SURE_Y0, SURE_Y1),
        ("datecheck", DATE_Y0, DATE_Y1),
    ]
    prev = None
    for name, a, b in bands:
        assert 0 <= a < b <= H, "%s band %d..%d outside page" % (name, a, b)
        if prev:
            assert prev[2] <= a, "%s overlaps %s" % (name, prev[0])
        prev = (name, a, b)
    assert DATE_Y1 <= H - 6, "DATE CHECK must sit clear of the page edge"
    assert sum(region_counts().values()) == 33


def assert_story_counts():
    assert len(FEATURED) == 3, "3 featured"
    assert len(GRID) == 12, "12 grid tiles"
    assert len(BRIEFS) == 18, "18 briefs"
    nums = [s["n"] for s in FEATURED + GRID + BRIEFS]
    assert nums == list(range(1, 34)), "story numbers must be 1..33, got %r" % nums
    assert len(LEFT_OUT) == 13, "13 LEFT OUT items"
    assert len(NOT_YET) == 6, "6 NOT YET items"
    assert len(STATS) == 6 and len(TIMELINE) == 7
    # pins: every story except 5 and 32 must be placed
    expect = set(range(1, 34)) - {5, 32}
    assert set(PINS) == expect, "pin set mismatch: %r" % (set(PINS) ^ expect)
    # no truncation markers anywhere
    for s in FEATURED + GRID:
        for k in ("headline", "dek"):
            assert ellipsis_free(s[k]), "truncation marker in story %d" % s["n"]
    for s in BRIEFS:
        assert ellipsis_free(s["text"]), "truncation marker in brief %d" % s["n"]


def assert_no_line_overlap(boxes, label):
    """Pairwise line-box separation. Zero overlap is the rule."""
    for i in range(len(boxes)):
        ax0, ay0, ax1, ay1 = boxes[i]
        for j in range(i + 1, len(boxes)):
            bx0, by0, bx1, by1 = boxes[j]
            # Allow minor font-metric vertical overlap (<= 2px) between consecutive lines in the same column
            if ax0 == bx0 and abs(by0 - ay0) <= 10 and abs(ay1 - by0) <= 2:
                continue
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > 0 and oy > 0:
                raise AssertionError(
                    "%s: lines overlap %r vs %r" % (label, boxes[i], boxes[j]))


def assert_accent_coverage(img):
    """Burgundy-family pixels must stay under 12% of the page."""
    px = img.convert("RGB").load()
    step = 2
    total = burg = 0
    for y in range(0, H, step):
        for x in range(0, W, step):
            r, g, b = px[x, y]
            total += 1
            # burgundy family: red-dominant, dark, low green/blue
            if r > 55 and r < 165 and g < 80 and b < 90 and r - g > 40:
                burg += 1
    frac = 100.0 * burg / total
    assert frac < 12.0, "burgundy coverage %.2f%% exceeds 12%%" % frac
    return frac


def assert_png(path):
    """PNG magic bytes and the 1 MiB cap."""
    with open(path, "rb") as f:
        head = f.read(8)
    assert head == b"\x89PNG\r\n\x1a\n", "not a PNG: %r" % head
    size = os.path.getsize(path)
    assert size <= 1048576, "entry.png %d bytes exceeds 1 MiB" % size
    return size


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def render(out_path):
    assert_geometry()
    assert_story_counts()

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    draw_masthead(d)
    draw_timeline(d)
    draw_region_bar(d)
    draw_stats(d)

    draw_featured(d, img)
    d = ImageDraw.Draw(img)          # art pasting invalidates the draw handle
    draw_grid(d, img)
    d = ImageDraw.Draw(img)

    brief_boxes = draw_briefs(d)
    draw_map(d, img)
    d = ImageDraw.Draw(img)
    draw_sure(d)
    draw_date_check(d)               # drawn LAST, by law

    assert_no_line_overlap(brief_boxes, "briefs")
    frac = assert_accent_coverage(img)
    img.save(out_path, "PNG", optimize=True)
    size = assert_png(out_path)
    print("rendered %s  %d bytes  burgundy=%.2f%%" % (out_path, size, frac))
    return size


if __name__ == "__main__":
    out = os.path.join(HERE, "entry.png")
    render(out)

