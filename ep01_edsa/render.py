"""Timeline B, episode 1: What if EDSA was redesigned from scratch?
Usage: render.py stills out.jpg T1 T2 ... | render.py part A B out.mp4"""
import math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import tl, space
import base as R
from tl import CY, AM, WH, GR, DIM, INK, RED, PANEL, PANEL2, EDGE, put, text, seg, eo, eio, back, lerp, mix, clamp

W, H, FPS = R.W, R.H, R.FPS
cl, cdur = R.cl, R.cdur
R.QUESTION = "WHAT IF EDSA WAS REDESIGNED FROM SCRATCH?"
G, CX, MED = 880, 960, 75            # ground line, centre, half median
BUSC, BIKEC, WALKC, ROAD = (255, 190, 40), (70, 200, 120), (176, 170, 196), (58, 60, 92)
CARS = [(226, 86, 86), (240, 240, 248), (90, 150, 240), (150, 156, 176), (250, 170, 60), (60, 190, 170), (200, 120, 220), (120, 130, 150)]


# ------------------------------------------------------------------ background
_BG = {}


def city_bg():
    if "c" not in _BG:
        im = (space.space_bg(W, H, 11).astype(np.float32) * 0.8).astype(np.uint8)
        rng = np.random.default_rng(8)
        x = -20
        while x < W:
            w, h = int(rng.integers(60, 150)), int(rng.integers(70, 330))
            cv2.rectangle(im, (x, G - h), (x + w, G), (15, 17, 46), -1)
            for yy in range(G - h + 14, G - 12, 22):
                for xx in range(x + 10, x + w - 12, 20):
                    if rng.random() < 0.28:
                        cv2.rectangle(im, (xx, yy), (xx + 8, yy + 9), (92, 88, 120), -1)
            x += w + int(rng.integers(4, 22))
        cv2.rectangle(im, (0, G), (W, H), (9, 9, 28), -1)
        _BG["c"] = im
    return _BG["c"]


# ------------------------------------------------------------------ vehicles (front views)
def rr(fr, x0, y0, x1, y1, r, col):
    tl.rrect(fr, x0, y0, x1, y1, r, col)


def car(fr, x, g, s, col):
    if s < 0.05:
        return
    w, h = 104 * s, 44 * s
    rr(fr, x - w * .46, g - 12 * s, x - w * .28, g, 3, (14, 14, 24)); rr(fr, x + w * .28, g - 12 * s, x + w * .46, g, 3, (14, 14, 24))
    rr(fr, x - w * .37, g - h - 34 * s, x + w * .37, g - h + 8 * s, 14 * s, mix(col, (0, 0, 0), 0.12))
    rr(fr, x - w * .31, g - h - 28 * s, x + w * .31, g - h + 2 * s, 9 * s, (28, 40, 78))
    rr(fr, x - w / 2, g - h - 4 * s, x + w / 2, g - 6 * s, 12 * s, col)
    for sx in (-1, 1):
        cv2.circle(fr, (int(x + sx * w * .34), int(g - h * .58)), max(2, int(8 * s)), (255, 240, 170), -1, cv2.LINE_AA)
    rr(fr, x - w * .2, g - h * .46, x + w * .2, g - h * .3, 3, mix(col, (0, 0, 0), 0.45))


def bus(fr, x, g, s, col=(240, 244, 255)):
    if s < 0.05:
        return
    w, h = 116 * s, 150 * s
    rr(fr, x - w * .44, g - 12 * s, x - w * .26, g, 3, (14, 14, 24)); rr(fr, x + w * .26, g - 12 * s, x + w * .44, g, 3, (14, 14, 24))
    rr(fr, x - w / 2, g - h, x + w / 2, g - 6 * s, 14 * s, col)
    rr(fr, x - w * .42, g - h + 10 * s, x + w * .42, g - h + 30 * s, 5 * s, (30, 26, 60))
    put(fr, text("BUSWAY", "bold", max(8, int(15 * s)), AM), x, g - h + 20 * s)
    rr(fr, x - w * .42, g - h + 36 * s, x + w * .42, g - h * .42, 6 * s, (28, 40, 78))
    rr(fr, x - w / 2, g - h * .36, x + w / 2, g - h * .27, 1, BUSC)
    for sx in (-1, 1):
        cv2.circle(fr, (int(x + sx * w * .36), int(g - h * .16)), max(2, int(8 * s)), (255, 240, 170), -1, cv2.LINE_AA)


def biker(fr, x, g, s, col=(90, 220, 150)):
    if s < 0.05:
        return
    cv2.ellipse(fr, (int(x), int(g - 26 * s)), (max(2, int(5 * s)), int(26 * s)), 0, 0, 360, (20, 20, 34), -1, cv2.LINE_AA)
    cv2.line(fr, (int(x - 16 * s), int(g - 56 * s)), (int(x + 16 * s), int(g - 56 * s)), (200, 204, 220), max(2, int(4 * s)), cv2.LINE_AA)
    rr(fr, x - 13 * s, g - 100 * s, x + 13 * s, g - 54 * s, 9 * s, col)
    cv2.circle(fr, (int(x), int(g - 114 * s)), int(13 * s), (238, 196, 160), -1, cv2.LINE_AA)
    cv2.ellipse(fr, (int(x), int(g - 118 * s)), (int(15 * s), int(11 * s)), 0, 180, 360, AM, -1, cv2.LINE_AA)


def ped(fr, x, g, s, col):
    if s < 0.05:
        return
    rr(fr, x - 8 * s, g - 34 * s, x - 1 * s, g, 3, (36, 40, 70)); rr(fr, x + 1 * s, g - 34 * s, x + 8 * s, g, 3, (36, 40, 70))
    rr(fr, x - 12 * s, g - 78 * s, x + 12 * s, g - 30 * s, 9 * s, col)
    cv2.circle(fr, (int(x), int(g - 91 * s)), int(11 * s), (238, 196, 160), -1, cv2.LINE_AA)


def tree(fr, x, g, s, T=0.0):
    if s < 0.05:
        return
    rr(fr, x - 6 * s, g - 96 * s, x + 6 * s, g, 3, (120, 84, 60))
    sw = 3 * math.sin(T * 1.4 + x)
    for dx, dy, r, c in ((-24, -120, 34, (48, 150, 86)), (22, -126, 36, (58, 170, 96)), (0, -156, 40, (70, 190, 108))):
        cv2.circle(fr, (int(x + dx * s + sw), int(g + dy * s)), int(r * s), c, -1, cv2.LINE_AA)


def queue(fr, fn, x, g, s, col=None, depth=3, T=0.0, ph=0.0):
    """A lane seen head-on: a few vehicles fading back for depth."""
    if s < 0.05:
        return
    for r in range(depth - 1, -1, -1):
        k = (1.0, 0.8, 0.64)[r]
        y = g - (0, 40, 70)[r] * s + (1.6 * math.sin(T * 7 + ph + r) if fn is car else 0)
        c = mix(col, (14, 15, 40), (0, 0.4, 0.62)[r]) if col is not None else None
        fn(fr, x, y, s * k, c) if c is not None else fn(fr, x, y, s * k)


def mrt(fr, T, hi=0.0):
    rr(fr, CX - 30, G - 250, CX + 30, G + 4, 6, (86, 90, 122))
    rr(fr, CX - 215, G - 276, CX + 215, G - 246, 8, (110, 114, 148))
    for sx in (-1, 1):
        x = CX + sx * 104
        if hi > 0:
            tl.glow(fr, lambda lay, q, x=x: tl.rrect(lay, (x - 78) * q, (G - 390) * q, (x + 78) * q, (G - 270) * q, 10 * q, CY), 0.9 * hi, 26)
        rr(fr, x - 66, G - 378, x + 66, G - 276, 16, (236, 240, 252))
        rr(fr, x - 54, G - 366, x + 54, G - 322, 8, (28, 40, 78))
        rr(fr, x - 66, G - 312, x + 66, G - 302, 1, (60, 120, 230))
        for s2 in (-1, 1):
            cv2.circle(fr, (int(x + s2 * 44), G - 290), 6, (255, 240, 170), -1, cv2.LINE_AA)


def surface(fr, x0, x1, col, a=1.0):
    tl.rrect(fr, min(x0, x1), G, max(x0, x1), G + 26, 2, col, a)


def xsec(fr, T, kj=0.0, kk=0.0, kl=0.0, hi_bus=0.0, hi_mrt=0.0, hi_car=0.0, labels=True, a=1.0):
    """EDSA cross-section, one typical stretch (simplified). k* = 0 today, 1 redesigned."""
    cv2.rectangle(fr, (CX - MED, G), (CX + MED, G + 26), (40, 42, 70), -1)
    for sg in (-1, 1):
        X = lambda off: CX + sg * (MED + off * 0.95)
        mid = lambda a_, b_: (X(a_) + X(b_)) / 2
        # surfaces
        surface(fr, X(0), X(150), BUSC)
        surface(fr, X(150), X(300), mix(ROAD, BUSC, kj))
        surface(fr, X(300), X(600), ROAD)
        surface(fr, X(600), X(730), mix(ROAD, BIKEC, kk))
        surface(fr, X(730), X(750), mix(ROAD, WALKC, kl))
        surface(fr, X(750), X(820), mix(BIKEC, WALKC, kl))
        surface(fr, X(820), X(880), WALKC)
        for off in (150, 300, 450, 600, 730 if kk > 0.5 else 750):
            cv2.line(fr, (int(X(off)), G), (int(X(off)), G + 26), (16, 16, 40), 3)
        if hi_bus > 0:
            tl.glow(fr, lambda lay, q: tl.rrect(lay, min(X(4), X(146)) * q, (G - 170) * q, max(X(4), X(146)) * q, (G + 26) * q, 8 * q, AM), 0.8 * hi_bus, 30)
        # kerb-side: sidewalk, trees, bikes
        if kl < 1:
            ped(fr, mid(826, 876), G, 0.8 * (1 - kl), (220, 120, 150))
            biker(fr, mid(752, 818), G, 0.72 * (1 - kl))
        if kl > 0:
            e = back(kl)
            tree(fr, X(760), G, 1.0 * e, T); tree(fr, X(858), G, 0.85 * e, T)
            ped(fr, X(800), G, 0.95 * e, (240, 150, 90)); ped(fr, X(832), G, 0.9 * e, (120, 170, 250))
        if kk > 0:
            e = back(kk)
            biker(fr, X(640), G, 0.95 * e); biker(fr, X(692), G - 0, 0.9 * e, (250, 150, 110))
            for off in (604, 726):                       # bollards
                rr(fr, X(off) - 4, G - 30 * e, X(off) + 4, G, 3, WH)
        # traffic lanes
        if kk < 1:
            queue(fr, car, mid(600, 750), G, 1 - kk, CARS[(3 + (sg > 0) * 4) % 8], T=T, ph=4)
        for n, (a_, b_) in enumerate(((300, 450), (450, 600))):
            if hi_car > 0:
                tl.glow(fr, lambda lay, q, a_=a_, b_=b_: tl.rrect(lay, min(X(a_ + 6), X(b_ - 6)) * q, (G - 120) * q, max(X(a_ + 6), X(b_ - 6)) * q, (G + 26) * q, 8 * q, CY), 0.6 * hi_car, 26)
            queue(fr, car, mid(a_, b_), G, 1.0, CARS[(n + 1 + (sg > 0) * 3) % 8], depth=3 if kj < 0.5 else 2, T=T, ph=n * 2 + sg)
        if kj < 1:
            queue(fr, car, mid(150, 300), G, 1 - kj, CARS[(0 + (sg > 0) * 5) % 8], T=T, ph=1)
        if kj > 0:
            queue(fr, bus, mid(150, 300), G, back(kj), (236, 240, 252), depth=1)
        queue(fr, bus, mid(0, 150), G, 1.0, (236, 240, 252), depth=2 if kj < 0.5 else 1)
        if labels:
            lab = [("BUS", mid(0, 150) if kj < 0.5 else mid(0, 300), AM), ("CARS", mid(150, 750) if kj < 0.5 else mid(300, 600), GR)]
            if kk > 0.5:
                lab.append(("BIKE", mid(600, 730), BIKEC))
            if kl > 0.5:
                lab.append(("WALK", mid(730, 880), WALKC))
            else:
                lab.append(("BIKE · WALK", mid(750, 880), WALKC))
            for t_, x_, c_ in lab:
                put(fr, text(t_, "mono", 22, c_, track=2), x_, G + 48, a)
    mrt(fr, T, hi_mrt)
    if labels:
        put(fr, text("MRT-3", "mono", 22, WH, track=2), CX, G - 408, a * 0.9)


# ------------------------------------------------------------------ small helpers
def head(fr, s, y, size, col=WH, a=1.0, sc=1.0, x=CX):
    put(fr, text(s, "head", size, INK), x + 4, y + 5, a * 0.7, sc)
    put(fr, text(s, "head", size, col), x, y, a, sc)


def pop(t, t0, d=0.45):
    k = seg(t, t0, d)
    return eo(k), 0.8 + 0.2 * back(k)


def rangebar(fr, x0, x1, y, lo, hi, vmax, col, k, label, val, a=1.0):
    px = lambda v: x0 + (x1 - x0) * v / vmax
    tl.rrect(fr, x0, y - 6, x1, y + 6, 6, PANEL2, a)
    if k > 0:
        tl.rrect(fr, px(lo), y - 26, px(lo + (hi - lo) * eio(k)), y + 26, 14, col, a)
        put(fr, text(val, "head", 40, col), px(hi) + 22, y - 2, a * eo(k), anchor="l")
    put(fr, text(label, "bold", 28, WH), x0 - 26, y, a, anchor="r")


STAMPS = {}


def stamp(fr, txt, x, y, t, t0, sc=0.6, col=AM):
    if txt not in STAMPS:
        STAMPS[txt] = R.stamp_sprite(txt, col)
    k = seg(t, t0, 0.4)
    if k > 0:
        put(fr, STAMPS[txt], x, y, min(1, k * 2), sc * (1.5 - 0.5 * back(k, 2.4)))


# ------------------------------------------------------------------ scenes
def sc_open(fr, t, T):
    tb, tc = cl("b", "open"), cl("c", "open")
    xsec(fr, T, a=eo(seg(t, 0.3, 0.5)))
    a1 = 1 - seg(t, tb - 0.25, 0.3)
    if a1 > 0:
        e, s = pop(t, 0.25)
        head(fr, "EDSA", 200, 170, WH, e * a1, s)
        put(fr, text("23.8 km · the busiest road in Metro Manila", "semi", 42, WH), CX, 322, eo(seg(t, 1.0, 0.4)) * a1)
        put(fr, text("TIMELINE A", "mono", 28, GR, track=5), CX, 392, eo(seg(t, 1.4, 0.4)) * a1)
    k = seg(t, tb + 0.2, 0.4)
    if k > 0:
        x0, x1, y, vmax = 330, 1590, 386, 460000
        px = lambda v: x0 + (x1 - x0) * v / vmax
        p = eio(seg(t, tb + 0.5, 1.7))
        n = int(round(400000 * p / 1000) * 1000)
        head(fr, f"{n:,}" + ("+" if p >= 1 else ""), 196, 150, AM, eo(k))
        put(fr, text("vehicles on EDSA every day", "semi", 42, WH), CX, 300, eo(k))
        tl.rrect(fr, x0, y - 22, x1, y + 22, 12, PANEL2, eo(k))
        v = 430000 * p
        tl.rrect(fr, x0, y - 22, px(min(v, 300000)) + 1, y + 22, 12, mix(AM, WH, 0.1))
        if v > 300000:
            tl.rrect(fr, px(300000), y - 22, px(v), y + 22, 12, RED)
        kc = eo(seg(t, tc + 0.3, 0.5))
        if kc > 0:
            tl.rrect(fr, px(250000), y - 34, px(300000), y + 34, 6, CY, 0.55 * kc)
            cv2.rectangle(fr, (int(px(250000)), y - 34), (int(px(300000)), y + 34), CY, 3, cv2.LINE_AA)
            put(fr, text("BUILT FOR 250,000–300,000", "bold", 28, CY), px(300000) + 6, y + 62, kc, anchor="r")
            put(fr, text("OVER CAPACITY", "bold", 28, RED), px(312000), y + 62, kc, anchor="l")


def sc_today(fr, t, T):
    te, tf = cl("e", "today"), cl("f", "today")
    hm = eo(seg(t, te + 0.4, 0.5)); hb = eo(seg(t, tf + 0.2, 0.5))
    xsec(fr, T, hi_mrt=hm * (1 - 0.5 * hb), hi_bus=hb)
    e, s = pop(t, cl("d", "today") + 0.1)
    head(fr, "WHAT MOVES THE MOST PEOPLE?", 150, 60, WH, e, s)
    k = seg(t, te + 0.5, 0.45)
    if k > 0:
        cv2.line(fr, (CX, 300), (CX, int(lerp(300, 440, eo(k)))), CY, 4, cv2.LINE_AA)
        put(fr, tl.pill("MRT-3 · about 388,000 passengers a day (2025)", CY, INK, 34, 0, "bold"), CX, 262, eo(k), 0.8 + 0.2 * back(k))
    k = seg(t, tf + 0.3, 0.45)
    if k > 0:
        for sx in (-1, 1):
            cv2.line(fr, (CX + sx * 330, 400), (CX + sx * 150, int(lerp(400, G - 200, eo(k)))), AM, 4, cv2.LINE_AA)
        put(fr, tl.pill("EDSA Busway · about 180,000 a day · one lane each way", AM, INK, 34, 0, "bold"), CX, 372, eo(k), 0.8 + 0.2 * back(k))


def sc_cap(fr, t, T):
    xsec(fr, T, labels=False)
    fr[440:] = (fr[440:] * 0.55).astype(np.uint8)
    tg, th = cl("g", "cap"), cl("h", "cap")
    e, s = pop(t, 0.15)
    head(fr, "PEOPLE ONE LANE CAN MOVE IN AN HOUR", 150, 52, WH, e, s)
    x0, x1 = 640, 1500
    rangebar(fr, x0, x1, 250, 600, 1600, 8000, mix(GR, WH, 0.4), seg(t, tg + 4.2, 0.8), "ONE LANE OF CARS", "600–1,600", e)
    rangebar(fr, x0, x1, 350, 4000, 8000, 8000, AM, seg(t, th + 0.9, 0.8), "ONE DEDICATED BUS LANE", "4,000–8,000", e)
    for v in range(0, 8001, 2000):
        x = x0 + (x1 - x0) * v / 8000
        cv2.line(fr, (int(x), 396), (int(x), 408), GR, 3)
        put(fr, text(f"{v:,}", "mono", 22, GR), x, 428, e)


def sc_fork(fr, t, T):
    tj, tk_, tl_, tm = (cl(k, "fork") for k in "jklm")
    kj, kk, kl = eio(seg(t, tj + 0.5, 0.9)), eio(seg(t, tk_ + 0.3, 0.9)), eio(seg(t, tl_ + 0.3, 0.9))
    xsec(fr, T, kj, kk, kl, hi_car=eo(seg(t, tm + 0.8, 0.5)))
    e, s = pop(t, 0.2)
    put(fr, tl.pill("TIMELINE B · ONE POSSIBLE DESIGN", CY, INK, 34, 0), CX, 150, e, s)
    steps = [(cl("i", "fork") + 0.9, tj, "EDSA, REDESIGNED", WH), (tj, tk_, "2 BUS LANES EACH WAY", AM), (tk_, tl_, "PROTECTED BIKEWAY", BIKEC),
             (tl_, tm, "WIDER SIDEWALK + TREES", (214, 208, 236)), (tm, 1e9, "CARS: FROM 4 LANES TO 2", WH)]
    for a_, b_, s_, c_ in steps:
        al = eo(seg(t, a_, 0.3)) * (1 - seg(t, b_ - 0.2, 0.2))
        if al > 0:
            head(fr, s_, 280, 76, c_, al, 0.85 + 0.15 * back(seg(t, a_, 0.4)))
    for n, (a_, _, _, c_) in enumerate(steps[1:]):
        on = t >= a_
        cv2.circle(fr, (CX - 60 + n * 40, 380), 9, c_ if on else PANEL2, -1, cv2.LINE_AA)


def sc_math(fr, t, T):
    xsec(fr, T, 1, 1, 1, labels=False)
    fr[440:] = (fr[440:] * 0.55).astype(np.uint8)
    tn, to, tp = cl("n", "math"), cl("o", "math"), cl("p", "math")
    e, s = pop(t, 0.15)
    head(fr, "PEOPLE PER HOUR, ONE DIRECTION", 150, 52, WH, e, s)
    x0, x1 = 600, 1420
    rangebar(fr, x0, x1, 250, 9200, 19200, 20000, CY, seg(t, tn + 4.3, 0.9), "TIMELINE B LAYOUT", "9,200–19,200", e)
    rangebar(fr, x0, x1, 350, 6400, 14400, 20000, mix(GR, WH, 0.4), seg(t, to + 0.9, 0.9), "TODAY'S LAYOUT", "6,400–14,400", e)
    for v in range(0, 20001, 5000):
        x = x0 + (x1 - x0) * v / 20000
        cv2.line(fr, (int(x), 396), (int(x), 408), GR, 3)
        put(fr, text(f"{v:,}", "mono", 22, GR), x, 428, e)
    put(fr, text("Road lanes only. Per-lane planning capacities × number of lanes; our arithmetic.", "mono", 22, WH), CX, 474, 0.85 * e)
    stamp(fr, "CAPACITY, NOT A FORECAST", CX, 560, t, tp + 0.5, 0.5)


def sc_real(fr, t, T):
    tq, tr, tw = cl("q", "real"), cl("r", "real"), cl("w", "real")
    kb = 1 - eio(seg(t, tw + 0.3, 1.0))
    xsec(fr, T, kb, kb, kb)
    aA = 1 - seg(t, tw - 0.2, 0.3)
    if aA > 0:
        e, s = pop(t, tq + 0.2)
        put(fr, tl.pill("THE REAL COST", RED, WH, 32, 0), CX, 150, e * aA, s)
        e, s = pop(t, tq + 1.5)
        head(fr, "DRIVERS LOSE HALF THEIR LANES", 226, 60, WH, e * aA, s)
        e, s = pop(t, tq + 3.6)
        head(fr, "IT ONLY WORKS IF ENOUGH PEOPLE SWITCH", 296, 48, AM, e * aA, s)
        if t < tw:
            stamp(fr, "ONE POSSIBLE DESIGN", CX, 400, t, tr + 0.4, 0.42)
    aB = eo(seg(t, tw + 0.1, 0.4))
    if aB > 0:
        put(fr, tl.pill("BACK IN TIMELINE A", GR, INK, 32, 0), CX, 150, aB)
        head(fr, "EDSA IS BEING RESURFACED NOW", 248, 60, WH, aB, 0.85 + 0.15 * back(seg(t, tw + 0.1, 0.45)))
        put(fr, text("DPWH rehabilitation, phase 2 · remaining work targeted for 2027", "semi", 38, WH), CX, 330, eo(seg(t, tw + 2.6, 0.4)))


def sc_outro(fr, t, T):
    R.sc_outro(fr, t, T)


SCN = {"open": sc_open, "today": sc_today, "cap": sc_cap, "fork": sc_fork, "math": sc_math, "real": sc_real, "outro": sc_outro}
SRC = {"open": "Simplified typical section; lane count varies · AI voice · Source: MMDA (2026)",
       "today": "Sources: DOTr / MRT-3 and DoTr busway ridership, 2025",
       "cap": "Source: NACTO Transit Street Design Guide (planning-level capacities)",
       "fork": "Illustration of one possible design. Not an official plan.",
       "math": "Source: NACTO per-lane capacities; totals are our own arithmetic",
       "real": "Source: DPWH, November 2026", "outro": None}


def scene_frame(i, T):
    name, s0 = R.STARTS[i]
    fr = (space.space_bg(W, H, 11) if name == "outro" else city_bg()).copy()
    SCN[name](fr, T - s0, T)
    z = 1.004 + 0.003 * math.sin(T * 0.7)
    M = cv2.getRotationMatrix2D((W / 2 + 8 * math.sin(T * 0.5), H / 2), 0.15 * math.sin(T * 0.6), z)
    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    R.hud(fr, 0.0 if name == "outro" else eo(seg(T, 1.2, 0.5)), SRC[name])
    return fr


R.scene_frame = scene_frame

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ims = [cv2.resize(R.frame(float(x)), (960, 540), interpolation=cv2.INTER_AREA) for x in sys.argv[3:]]
        Image.fromarray(np.vstack([np.hstack(ims[i:i + 2]) for i in range(0, len(ims), 2)])).save(sys.argv[2], quality=88)
    else:
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        tmp = out + ".tmp.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "60", tmp],
                             stdin=subprocess.PIPE)
        for f in range(a, b):
            p.stdin.write(R.frame(f / FPS).tobytes())
        p.stdin.close()
        if p.wait() == 0:
            os.replace(tmp, out); print("done", out)
