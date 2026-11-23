#!/usr/bin/env python3
"""THE WORLD TODAY — classic broadsheet front page, Sunday 22 November 2026.
Draws entry.png (1024x1024) with PIL only. Every story first reported
22 Nov 2026, cross-checked against dailysummaryof final edition (updated
23:45 UTC) and AP/Reuters/BBC/CNN via One Turn."""
import os
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (163, 18, 18)
NAVY = (28, 42, 74)
GREY = (110, 104, 90)
BLUE = (214, 228, 238)
TAN = (222, 200, 150)
RULEC = (170, 162, 145)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


BADGE_COL = {"R": (34, 110, 60), "C": (176, 124, 22), "O": (38, 74, 150)}
BADGE_LBL = {"R": "REPORTED", "C": "CLAIM", "O": "ONGOING"}


def badge(draw, x, y, kind, size=9):
    label = BADGE_LBL[kind]
    col = BADGE_COL[kind]
    f = F(SANS_B, size)
    tw = draw.textlength(label, font=f)
    h = size + 4
    draw.rounded_rectangle([x, y, x + tw + 10, y + h], radius=2, fill=col)
    draw.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return tw + 10


def story(draw, x, y, w, head, body, src, kind, hsize=13, bsize=10, hlead=16, blead=13):
    """One column story; returns y after it (gap included)."""
    hf = F(SERIF_B, hsize)
    bf = F(SERIF, bsize)
    sf = F(SANS, 9)
    for ln in wrap(draw, head, hf, w):
        draw.text((x, y), ln, font=hf, fill=INK)
        y += hlead
    for ln in wrap(draw, body, bf, w):
        draw.text((x, y), ln, font=bf, fill=INK)
        y += blead
    bw = badge(draw, x, y + 1, kind)
    draw.text((x + bw + 5, y + 2), src, font=sf, fill=GREY)
    y += 16 + 7
    return y


def rule(draw, x0, x1, y, wdt=1, col=INK):
    draw.line([(x0, y), (x1, y)], fill=col, width=wdt)


def draw_map(draw, x0, y0, x1, y1, pins):
    draw.rectangle([x0, y0, x1, y1], fill=BLUE, outline=INK, width=1)

    def poly(pts):
        draw.polygon([(x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)) for fx, fy in pts],
                     fill=TAN, outline=(150, 130, 95))
    poly([(0.03, 0.30), (0.10, 0.18), (0.20, 0.16), (0.26, 0.28), (0.22, 0.42),
          (0.14, 0.55), (0.08, 0.48), (0.03, 0.40)])          # N America
    poly([(0.20, 0.62), (0.26, 0.58), (0.30, 0.66), (0.27, 0.78), (0.21, 0.74)])  # S America
    poly([(0.44, 0.16), (0.52, 0.10), (0.62, 0.12), (0.66, 0.20), (0.58, 0.26),
          (0.50, 0.30), (0.44, 0.24)])                          # Europe
    poly([(0.44, 0.34), (0.52, 0.32), (0.56, 0.42), (0.52, 0.62), (0.46, 0.66),
          (0.43, 0.48)])                                        # Africa
    poly([(0.62, 0.14), (0.78, 0.08), (0.92, 0.16), (0.95, 0.34), (0.86, 0.48),
          (0.74, 0.44), (0.66, 0.30), (0.60, 0.22)])            # Asia
    poly([(0.86, 0.68), (0.92, 0.66), (0.94, 0.74), (0.88, 0.78)])  # Oceania
    for tx, ty, lx, ly, n in pins:
        # leader line from true location to fanned-out pin
        tpx, tpy = x0 + tx * (x1 - x0), y0 + ty * (y1 - y0)
        px, py = x0 + lx * (x1 - x0), y0 + ly * (y1 - y0)
        draw.line([(tpx, tpy), (px, py)], fill=(120, 110, 95), width=1)
        draw.ellipse([tpx - 2, tpy - 2, tpx + 2, tpy + 2], fill=RED)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        f = F(SANS_B, 9)
        tw = draw.textlength(str(n), font=f)
        draw.text((px - tw / 2, py - 5), str(n), font=f, fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 26

    # ---- top rule + masthead ----
    d.rectangle([0, 0, W, 7], fill=INK)
    f_name = F(SERIF_B, 62)
    name = "THE WORLD TODAY"
    tw = d.textlength(name, font=f_name)
    d.text(((W - tw) / 2, 12), name, font=f_name, fill=INK)
    rule(d, M, W - M, 82, 2)
    # dateline strip
    f_dl = F(SANS_B, 12)
    d.text((M, 89), "SUNDAY, 22 NOVEMBER 2026", font=f_dl, fill=RED)
    f_mid = F(SANS, 11)
    mid = "30 STORIES  ·  EVERY ITEM FIRST REPORTED 22 NOV"
    tw = d.textlength(mid, font=f_mid)
    d.text(((W - tw) / 2, 90), mid, font=f_mid, fill=INK)
    lx = W - M
    for kind in ("O", "C", "R"):
        label = BADGE_LBL[kind]
        f = F(SANS_B, 8)
        twl = d.textlength(label, font=f)
        lx -= twl + 10
        d.rounded_rectangle([lx, 89, lx + twl + 10, 102], radius=2, fill=BADGE_COL[kind])
        d.text((lx + 5, 91), label, font=f, fill=(255, 255, 255))
        lx -= 5
    rule(d, M, W - M, 108, 1)

    # ---- numbers strip ----
    d.rectangle([M, 114, W - M, 142], fill=NAVY)
    nums = [("258", "House seats"), ("2", "tankers hit"), ("194", "COP31 parties"),
            ("330", "votes in NC"), ("36", "missing in Banten"), ("1,661", "Gaza toll")]
    f_n = F(SERIF_B, 20)
    f_nl = F(SANS, 10)
    x = M + 14
    for val, lab in nums:
        d.text((x, 117), val, font=f_n, fill=(232, 190, 60))
        vw = d.textlength(val, font=f_n)
        d.text((x + vw + 6, 124), lab, font=f_nl, fill=(235, 235, 235))
        x += vw + 6 + d.textlength(lab, font=f_nl) + 26

    # ---- LEAD: Hormuz ----
    y = 150
    f_kick = F(SANS_B, 12)
    d.text((M, y), "CONFLICT  ·  STRAIT OF HORMUZ", font=f_kick, fill=RED)
    d.text((W - M - d.textlength("17:13 UTC", font=f_kick), y), "17:13 UTC", font=f_kick, fill=INK)
    y += 18
    f_h1 = F(SERIF_B, 34)
    d.text((M, y), "TWO TANKERS HIT BY MINES OFF HORMUZ", font=f_h1, fill=INK)
    y += 42
    f_deck = F(SERIF_I, 15)
    deck = ("Two supertankers struck naval mines and caught fire east of the strait, "
            "north of Ghanam Island — the sharpest turn yet in the Gulf standoff.")
    for ln in wrap(d, deck, f_deck, 660):
        d.text((M, y), ln, font=f_deck, fill=INK)
        y += 19
    y += 3
    f_body = F(SERIF, 11)
    body = ("Iran's navy said the ships had switched off detection and navigation systems. "
            "It warned that reliance on US Central Command would bring heavy losses, as "
            "Washington's blockade passed 130 days.")
    for ln in wrap(d, body, f_body, 660):
        d.text((M, y), ln, font=f_body, fill=INK)
        y += 15
    bw = badge(d, M, y + 2, "R")
    d.text((M + bw + 5, y + 3), "Iran navy · AP", font=F(SANS, 10), fill=GREY)
    # tanker sketch, right of lead
    sx, sy = 760, 156
    d.rectangle([sx, sy + 52, sx + 210, sy + 78], fill=(40, 70, 110))        # hull
    d.rectangle([sx, sy + 48, sx + 210, sy + 52], fill=(235, 235, 235))      # deck line
    d.rectangle([sx + 150, sy + 28, sx + 195, sy + 48], fill=(250, 250, 250), outline=INK)  # bridge
    d.rectangle([sx + 165, sy + 18, sx + 180, sy + 28], fill=RED)            # funnel
    d.rectangle([sx + 55, sy + 38, sx + 110, sy + 48], fill=(200, 210, 220), outline=INK)  # tank
    for wx in range(sx, sx + 210, 18):
        d.arc([wx, sy + 78, wx + 18, sy + 92], 0, 180, fill=NAVY, width=2)
    mx, my = sx + 15, sy + 6
    for a in range(0, 360, 45):
        x2 = mx + 10 * math.cos(math.radians(a))
        y2 = my + 10 * math.sin(math.radians(a))
        d.line([(mx, my), (x2, y2)], fill=INK, width=2)
    d.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=INK)
    d.text((sx, sy + 96), "A supertanker east of the strait. Sketch: The World Today",
           font=F(SERIF_I, 9), fill=GREY)
    rule(d, M, W - M, 302, 2)

    # ---- three ruled columns ----
    col_w = 306
    xs = [M, M + col_w + 16, M + 2 * (col_w + 16)]
    for cx in xs[1:]:
        d.line([(cx - 8, 312), (cx - 8, 700)], fill=RULEC, width=1)
    y0 = 312

    # Column A: 2 big + 3 small
    y = y0
    y = story(d, xs[0], y, col_w,
              "NO DEAL AT COP31",
              "The Antalya summit ended with no agreement after the EU and about 130 parties "
              "rejected a text that never named fossil fuels. The longest climate conference "
              "ever, and the first to fail since 2009.", "CNN · Reuters", "R",
              hsize=21, bsize=11, hlead=24, blead=14)
    rule(d, xs[0], xs[0] + col_w, y - 4, 1, RULEC)
    y = story(d, xs[0], y, col_w,
              "258 — DEMOCRATS WIN THE HOUSE",
              "Hubbard beat Foxx by 330 votes in a North Carolina recount, giving Democrats "
              "their largest House majority since 1992. Republicans hold 173; four races "
              "are uncalled.", "AP · Reuters", "R",
              hsize=19, bsize=11, hlead=22, blead=14)
    rule(d, xs[0], xs[0] + col_w, y - 4, 1, RULEC)
    y = story(d, xs[0], y, col_w,
              "Russian ship hit at Benghazi",
              "A suspected sea-drone strike hit the corvette Merkury at the Libyan naval base, "
              "causing an explosion and fire. No group claimed it.", "France 24", "C")
    y = story(d, xs[0], y, col_w,
              "Drones kill four near Khartoum",
              "Strikes blamed on the Rapid Support Forces killed four around the capital and "
              "damaged a UN building while staff were inside.", "AP", "C")
    y = story(d, xs[0], y, col_w,
              "Zelenskyy pleads for Patriots",
              "Kyiv urged Washington to release missiles partners have paid for, as Russia "
              "fired about 2,700 drones in a week.", "BBC", "R")

    # Column B: 6 small
    y = y0
    y = story(d, xs[1], y, col_w,
              "Iran shows off missile city",
              "State media showed a dual-missile launcher and tunnels of a new underground "
              "missile city as the blockade bites.", "IRGC media", "R")
    y = story(d, xs[1], y, col_w,
              "Saudis stop Houthi attack",
              "The coalition intercepted a Houthi drone and missile; the Houthis claimed a "
              "strike on the Rabigh refinery.", "Reuters", "C")
    y = story(d, xs[1], y, col_w,
              "Bahrain blames Iran; UAE condemns",
              "Bahrain said Iran hit a civilian industrial site; the UAE called the strikes a "
              "violation of sovereignty.", "France 24", "R")
    y = story(d, xs[1], y, col_w,
              "Europe protests, day three",
              "Marches over living costs and housing entered a third day, from Portugal to "
              "France, where protests ran a sixth straight weekend.", "AP", "R")
    y = story(d, xs[1], y, col_w,
              "Settlers burn 12 cars in West Bank",
              "Settlers attacked villages near Ramallah, burning cars and spraying slogans on "
              "homes. Police opened an arson inquiry.", "Guardian", "R")
    y = story(d, xs[1], y, col_w,
              "Blast at Benghazi ammo depot",
              "An explosion inside a naval base ammunition depot set off a fire; emergency "
              "crews were sent in. No toll was given.", "Local auth.", "R")

    # Column C: 6 small
    y = y0
    y = story(d, xs[2], y, col_w,
              "Unity talks stall in Israel",
              "Eisenkot's Yashar met Likud on a unity government, but a wide gap remains "
              "between rhetoric and action.", "Israeli media", "R")
    y = story(d, xs[2], y, col_w,
              "Finland: war spills over",
              "Helsinki said the war is spilling over after a drone hit a Russian cargo ship "
              "in the Baltic Sea.", "Finnish govt", "R")
    y = story(d, xs[2], y, col_w,
              "WCK: three killed were not our team",
              "World Central Kitchen said the three killed in a strike on a food aid vehicle "
              "in Gaza City were not its staff.", "WCK", "R")
    y = story(d, xs[2], y, col_w,
              "“War was perfectly avoidable”",
              "Former UN envoy Álvaro de Soto said the Iran war need not have happened, at the "
              "MED Dialogues in Naples.", "MED Dialogues", "R")
    y = story(d, xs[2], y, col_w,
              "Candy factory fire: 3 dead, 36 missing",
              "A blaze swept the PT Fonusa Agung Mulia factory in Serang, Banten; 15 people "
              "were rescued alive.", "BBC", "R")
    y = story(d, xs[2], y, col_w,
              "Fidan: Israel may use Druze",
              "Turkey's foreign minister said Israel is arming a Druze tribe in Syria and may "
              "use it to provoke Damascus.", "Anadolu", "C")

    # ---- THE DAY IN BRIEF: stories 19-30, two columns ----
    rule(d, M, W - M, 708, 2)
    f_sec = F(SANS_B, 11)
    d.text((M, 716), "THE DAY IN BRIEF — STORIES 19–30", font=f_sec, fill=INK)
    d.text((W - M - d.textlength("ALL TIMES UTC", font=f_sec), 716), "ALL TIMES UTC", font=f_sec, fill=GREY)
    brief = [
        ("19", "Fidan: war fallout hits markets", "Anadolu", "R"),
        ("20", "Aoun: Israel must leave every inch", "Al Jazeera", "R"),
        ("21", "Gaza: 350,000 families homeless", "Al Jazeera", "R"),
        ("22", "“Silent economic war” — Pezeshkian", "IRNA", "R"),
        ("23", "Settlers attack homes in Hebron", "WAFA", "R"),
        ("24", "Turkey: Gaza homes blocked", "Anadolu", "C"),
        ("25", "Germany urged to arrest soldier", "HRF", "R"),
        ("26", "Fred Nile dies, aged 92", "Guardian", "R"),
        ("27", "Gamer, 16, helps FBI rescue girl", "FBI", "R"),
        ("28", "Gaza toll since Oct 2025: 1,661", "Gaza health min.", "R"),
        ("29", "Ex-police chief found dead", "ANSA", "R"),
        ("30", "IRGC claims hits on US bases in Bahrain", "IRGC media", "C"),
    ]
    f_bn = F(SERIF_B, 11)
    f_bb = F(SERIF, 11)
    f_bs = F(SANS, 9)
    bx = [M, M + 500]
    for i, (num, head, src, kind) in enumerate(brief):
        cx = bx[i // 6]
        cy = 736 + (i % 6) * 15
        d.text((cx, cy), num, font=F(SERIF_B, 11), fill=RED)
        d.text((cx + 26, cy), head, font=f_bb, fill=INK)
        hw = d.textlength(head, font=f_bb)
        d.text((cx + 26 + hw + 6, cy + 1), src, font=f_bs, fill=GREY)

    # ---- map strip ----
    rule(d, M, W - M, 830, 2)
    d.text((M, 838), "WHERE IT HAPPENED — EVERY HERO PINNED", font=f_sec, fill=INK)
    # pins: (true fx, true fy, label fx, label fy, number) — fanned out with leaders
    pins = [(0.66, 0.42, 0.72, 0.55, 1), (0.55, 0.22, 0.50, 0.08, 2),
            (0.10, 0.30, 0.10, 0.30, 3), (0.50, 0.34, 0.38, 0.18, 4),
            (0.50, 0.48, 0.42, 0.72, 5), (0.58, 0.18, 0.68, 0.10, 6),
            (0.86, 0.52, 0.88, 0.62, 7), (0.56, 0.30, 0.62, 0.34, 8)]
    draw_map(d, M, 856, 430, 940, pins)
    d.text((446, 856), "PIN KEY", font=F(SANS_B, 11), fill=INK)
    key_l = ["1 Hormuz — tankers hit", "2 Antalya — no deal",
             "3 Washington — Dems 258", "4 Benghazi — ship hit"]
    key_r = ["5 Khartoum — 4 killed", "6 Kyiv — Patriots plea",
             "7 Banten — factory fire", "8 Gaza — toll 1,661"]
    ky = 874
    for a, b in zip(key_l, key_r):
        d.text((446, ky), a, font=F(SANS, 10), fill=INK)
        d.text((580, ky), b, font=F(SANS, 10), fill=INK)
        ky += 15
    d.rectangle([700, 856, W - M, 940], outline=RED, width=1, fill=(253, 238, 226))
    d.text((712, 862), "NOT YET — DO NOT READ AS DONE", font=F(SANS_B, 10), fill=RED)
    ny = ["4 House races uncalled", "COP32 venue not set",
          "Gaza ceasefire talks: no deal announced",
          "Iran tanker convoy: no test of the blockade yet"]
    yy = 880
    for it in ny:
        d.text((712, yy), "·  " + it, font=F(SANS, 10), fill=INK)
        yy += 14

    # ---- footer ----
    rule(d, M, W - M, 950, 1)
    f_f = F(SANS, 10)
    fl1 = "DATE CHECK — Every story above was first reported on 22 Nov, unless its kicker says otherwise."
    fl2 = "EXCLUDED:  El Chapo Isidro captured 20 Nov  ·  BepiColombo Mercury orbit 21 Nov  ·  ICJ Myanmar ruling 19 Nov  ·  Wall St rout 20 Nov  ·  FBI NCIC hack first reported 21 Nov."
    d.text((M, 955), fl1, font=f_f, fill=INK)
    d.text((M, 968), fl2, font=f_f, fill=INK)
    d.text((M, 981), "LEGEND:  REPORTED = confirmed by 2+ sources  ·  CLAIM = one side alleges, unverified  ·  ONGOING = still developing.",
           font=f_f, fill=INK)
    d.text((M, 994), "SOURCES:  AP · Reuters · BBC · CNN · France 24 · Al Jazeera · Guardian · IRNA · Anadolu · WAFA · HRF · WCK · FBI · Euronews · dailysummaryof, 22 Nov 2026.",
           font=f_f, fill=INK)
    f_end = F(SERIF_B, 10)
    end = "— THE WORLD TODAY · 22 NOV 2026 —"
    d.text(((W - d.textlength(end, font=f_end)) / 2, 1007), end, font=f_end, fill=INK)

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, "entry.png")
    img.save(p, optimize=True)
    print("wrote", p, os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
