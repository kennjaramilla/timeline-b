"""Timeline B, episode 2: What if the Moon disappeared?
Visuals are split in two: vis_*() draws a picture inside the centre box (x 420-1500, y 330-900) with no text, so the
vertical Reels can reuse it; sc_*() adds the landscape text on top.
Usage: render.py stills out.jpg T1 T2 ... | render.py part A B out.mp4"""
import math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import tl, space
import base as R
from tl import CY, AM, WH, GR, DIM, INK, RED, PINK, PANEL, PANEL2, EDGE, put, text, seg, eo, eio, back, lerp, mix, clamp

W, H, FPS = R.W, R.H, R.FPS
cl, cdur = R.cl, R.cdur
CX = W // 2
R.QUESTION = "WHAT IF THE MOON DISAPPEARED?"
SKY = space.space_bg(W, H, 21)
LIGHT = (-0.6, -0.4, 0.7)


def earth(r, rot=0.6):
    return space.planet(int(r), "A", 5, rot, LIGHT)


def moon(r):
    return space.planet(int(r), "moon", 3, 2.0, LIGHT, 0.5)


_FM = {}


def fullmoon(r):
    """A bright, front-lit full Moon."""
    if r not in _FM:
        m = space.planet(int(r), "moon", 3, 2.0, (0.05, -0.1, 1.0), 0.9).astype(np.float32)
        m[..., :3] = np.clip(m[..., :3] * 1.75 + 18, 0, 255)
        _FM[r] = m.astype(np.uint8)
    return _FM[r]


# ------------------------------------------------------------------ helpers
def head(fr, s, y, size, col=WH, a=1.0, sc=1.0, x=CX):
    if a <= 0:
        return
    put(fr, text(s, "head", size, INK), x + 4, y + 5, a * 0.7, sc)
    put(fr, text(s, "head", size, col), x, y, a, sc)


def pop(t, t0, d=0.45):
    k = seg(t, t0, d)
    return eo(k), 0.8 + 0.2 * back(k)


def title(fr, t, pill, pcol, lines):
    """Top text block: a pill, then headline/sub lines that swap on cue. lines = [(t_in, t_out, headline, colour, sub)]."""
    e, s = pop(t, 0.2)
    put(fr, tl.pill(pill, pcol, INK, 30, 0), CX, 140, e, s)
    for t0, t1, hl, col, sub in lines:
        a = eo(seg(t, t0, 0.3)) * (1 - seg(t, t1 - 0.25, 0.25))
        if a > 0:
            size = 66 if len(hl) <= 26 else 56 if len(hl) <= 32 else 48
            head(fr, hl, 222, size, col, a, 0.85 + 0.15 * back(seg(t, t0, 0.4)))
            if sub:
                put(fr, text(sub, "semi", 34, WH), CX, 290, a * eo(seg(t, t0 + 0.5, 0.4)))


STAMPS = {}


def stamp(fr, txt, x, y, t, t0, sc=0.6, col=AM):
    if txt not in STAMPS:
        STAMPS[txt] = R.stamp_sprite(txt, col)
    k = seg(t, t0, 0.4)
    if k > 0:
        put(fr, STAMPS[txt], x, y, min(1, k * 2), sc * (1.5 - 0.5 * back(k, 2.4)))


def person(fr, x, g, s, col=PINK, dark=0.0):
    c = lambda c_: mix(c_, (8, 8, 20), dark)
    tl.rrect(fr, x - 8 * s, g - 34 * s, x - 1 * s, g, 3, c((36, 40, 70))); tl.rrect(fr, x + 1 * s, g - 34 * s, x + 8 * s, g, 3, c((36, 40, 70)))
    tl.rrect(fr, x - 12 * s, g - 78 * s, x + 12 * s, g - 30 * s, int(9 * s), c(col))
    cv2.circle(fr, (int(x), int(g - 91 * s)), int(11 * s), c((238, 196, 160)), -1, cv2.LINE_AA)


def rot_sprite(spr, deg):
    h, w = spr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    return cv2.warpAffine(spr, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))


def dotted(fr, p0, p1, col, n=22, r=4):
    for i in range(n + 1):
        cv2.circle(fr, (int(lerp(p0[0], p1[0], i / n)), int(lerp(p0[1], p1[1], i / n))), r, col, -1, cv2.LINE_AA)


# ------------------------------------------------------------------ visuals (no headline text)
def vis_pair(fr, T, gone=0.0, arrow=0.0, label=True):
    ex, ey, mx, my = 700, 640, 1300, 560
    put(fr, earth(170), ex, ey + 4 * math.sin(T * 0.8))
    if label and gone < 0.5:
        dotted(fr, (ex + 190, ey - 26), (mx - 70, my + 10), mix(GR, (0, 0, 0), 0.2 + 0.6 * gone))
        put(fr, text("384,400 km on average · not to scale", "mono", 22, GR), (ex + mx) / 2 + 30, (ey + my) / 2 - 44, 1 - gone * 2)
    if gone < 1:
        put(fr, moon(50), mx, my, 1 - gone)
    if 0 < gone < 1:
        cv2.circle(fr, (mx, my), int(50 + 170 * eo(gone)), mix(WH, (0, 0, 0), gone), max(1, int(6 * (1 - gone))), cv2.LINE_AA)
    if gone >= 0.5:
        for i in range(24):
            a0 = i * 15
            cv2.ellipse(fr, (mx, my), (50, 50), 0, a0, a0 + 8, DIM, 3, cv2.LINE_AA)
    if arrow > 0:
        cv2.arrowedLine(fr, (mx + 66, my - 20), (int(mx + 66 + 120 * eo(arrow)), int(my - 20 - 44 * eo(arrow))), AM, 6, cv2.LINE_AA, tipLength=0.3)


def vis_size(fr, T, k=1.0):
    ex, mx, y = 760, 1230, 610
    put(fr, earth(180), ex, y)
    put(fr, moon(49), mx, y, eo(k), 0.6 + 0.4 * back(k))
    for x, r, lab in ((ex, 180, "Earth · 12,742 km"), (mx, 49, "Moon · 3,475 km")):
        cv2.line(fr, (x - r, y + 215), (x + r, y + 215), WH, 4, cv2.LINE_AA)
        for sx in (-1, 1):
            cv2.line(fr, (x + sx * r, y + 203), (x + sx * r, y + 227), WH, 4, cv2.LINE_AA)
        put(fr, text(lab, "bold", 28, WH), x, y + 258)


_rng = np.random.default_rng(4)
HILLS = np.array([(0, 900)] + [(x, 800 + 26 * math.sin(x / 190) + 14 * math.sin(x / 71 + 1)) for x in range(0, W + 40, 40)] + [(W, 900)], np.int32)


def vis_night(fr, T, k=0.0):
    """k = 0 full-Moon night, 1 = no Moon."""
    lit = 1 - k
    if lit > 0:
        tl.glow(fr, lambda lay, q: cv2.circle(lay, (int(1180 * q), int(470 * q)), int(170 * q), (110, 120, 160), -1), 1.0 * lit, 70)
        put(fr, fullmoon(72), 1180, 470, lit)
    cv2.fillPoly(fr, [HILLS], mix((14, 15, 34), (58, 70, 112), lit), cv2.LINE_AA)
    for x, h_ in ((520, 120), (600, 90), (1380, 130), (1450, 100)):
        gy = 800 + 26 * math.sin(x / 190) + 14 * math.sin(x / 71 + 1)
        tl.rrect(fr, x - 5, gy - h_ * 0.5, x + 5, gy + 4, 2, mix((10, 10, 24), (34, 40, 70), lit))
        cv2.circle(fr, (x, int(gy - h_ * 0.62)), int(h_ * 0.36), mix((10, 11, 26), (36, 52, 78), lit), -1, cv2.LINE_AA)
    gx = 800; gy = 800 + 26 * math.sin(gx / 190) + 14 * math.sin(gx / 71 + 1)
    if lit > 0.05:
        cv2.ellipse(fr, (gx + 46, int(gy + 6)), (60, 9), 0, 0, 360, mix((58, 70, 112), (20, 24, 50), 0.7), -1, cv2.LINE_AA)
    person(fr, gx, gy + 2, 1.5, PINK, dark=0.72 * k)
    if k > 0.6:
        a = eo((k - 0.6) / 0.4)
        tl.glow(fr, lambda lay, q: cv2.circle(lay, (int(1010 * q), int(600 * q)), int(16 * q), (160, 170, 210), -1), a, 14)
        cv2.circle(fr, (1010, 600), 6, WH, -1, cv2.LINE_AA)
        put(fr, text("Venus", "mono", 24, WH), 1010, 640, a)


SAND = np.array([(0, 900), (0, 872), (700, 846), (1500, 650), (W, 560), (W, 900)], np.int32)


def vis_tide(fr, T, k=0.0):
    """k = 0 tides with the Moon, 1 = Sun-only tides (about a third)."""
    y0 = 760
    A = lerp(84, 28, k)
    lvl = y0 - A * math.sin(T * 0.85)
    cv2.fillPoly(fr, [SAND], (196, 170, 120), cv2.LINE_AA)
    tl.rrect(fr, 1140, 560, 1158, 870, 4, (90, 70, 56)); tl.rrect(fr, 1126, 556, 1172, 572, 4, (110, 86, 66))
    R.water(fr, 0, W, lvl, 900, T, 0.72, 7)
    bx, by = 640, lvl + 4 * math.sin(T * 2.1)
    cv2.fillPoly(fr, [np.array([(bx - 70, by - 22), (bx + 70, by - 22), (bx + 48, by + 10), (bx - 48, by + 10)], np.int32)], (236, 240, 252), cv2.LINE_AA)
    cv2.line(fr, (int(bx), int(by - 22)), (int(bx), int(by - 110)), (236, 240, 252), 5, cv2.LINE_AA)
    cv2.fillPoly(fr, [np.array([(bx + 6, by - 106), (bx + 60, by - 40), (bx + 6, by - 40)], np.int32)], AM, cv2.LINE_AA)
    for yy, lab in ((y0 - A, "high tide"), (y0 + A, "low tide")):
        tl.dashed(fr, 430, 1490, yy, WH, 3, 18, 14)
        put(fr, text(lab, "mono", 22, WH), 1484, yy - 20, 0.9, anchor="r")


CORALS = [(520, 60, (236, 110, 150)), (640, 84, (250, 150, 90)), (790, 70, (180, 120, 230)), (930, 96, (236, 110, 150)),
          (1080, 66, (250, 190, 90)), (1220, 88, (120, 200, 190)), (1370, 74, (236, 130, 170))]


def vis_reef(fr, T, k=0.0, spawn=0.0):
    """Underwater reef. k = 0 moonlit, 1 = no Moon; spawn 0..1 = eggs rising."""
    y = np.linspace(0, 1, 600, dtype=np.float32)[:, None, None]
    grad = (np.array([24, 96, 168], np.float32) * (1 - y) + np.array([6, 22, 70], np.float32) * y) * (1 - 0.35 * k)
    fr[320:920] = np.clip(grad, 0, 255).astype(np.uint8).repeat(W, 1)
    if k < 1:
        lay = fr.copy()
        cv2.fillPoly(lay, [np.array([(1040, 320), (1260, 320), (1080, 900), (620, 900)], np.int32)], (150, 190, 230), cv2.LINE_AA)
        cv2.addWeighted(lay, 0.16 * (1 - k), fr, 1 - 0.16 * (1 - k), 0, dst=fr)
        tl.glow(fr, lambda lay_, q: cv2.circle(lay_, (int(1150 * q), int(330 * q)), int(60 * q), (150, 170, 210), -1), 0.9 * (1 - k), 40)
    cv2.fillPoly(fr, [np.array([(0, 920), (0, 860)] + [(x, 850 + 14 * math.sin(x / 120)) for x in range(0, W + 60, 60)] + [(W, 920)], np.int32)],
                 (30, 44, 84), cv2.LINE_AA)
    for i, (x, h_, col) in enumerate(CORALS):
        col = mix(col, (20, 30, 70), 0.25 * k)
        sw = 5 * math.sin(T * 1.2 + i)
        for j, (dx, dh) in enumerate(((-26, 0.62), (0, 1.0), (26, 0.72))):
            tl.rrect(fr, x + dx - 9 + sw * dh, 860 - h_ * dh, x + dx + 9 + sw * dh, 866, 9, col)
            cv2.circle(fr, (int(x + dx + sw * dh), int(860 - h_ * dh)), 13, mix(col, WH, 0.2), -1, cv2.LINE_AA)
        if spawn > 0:
            for j in range(9):
                q = ((T * 0.22 + j / 9 + i * 0.13) % 1)
                if q < spawn:
                    cv2.circle(fr, (int(x + 30 * math.sin(j * 2.1 + T + i)), int(850 - h_ - q * 420)), 5, (255, 190, 210), -1, cv2.LINE_AA)
    cv2.line(fr, (0, 320), (W, 320), (120, 170, 220), 3)


_SPIN = {}


def vis_spin(fr, T, k=0.0, speed=1.0):
    """Rotating Earth; k = 0 with the Moon tugging on it, 1 = Moon gone."""
    n = 48
    i = int((T * 5 * speed) % n)
    if i not in _SPIN:
        _SPIN[i] = earth(185, 0.6 + 2 * math.pi * i / n)
    put(fr, _SPIN[i], CX, 620)
    cv2.ellipse(fr, (CX, 620), (250, 70), 0, 200, 340, AM, 6, cv2.LINE_AA)
    cv2.arrowedLine(fr, (CX + 228, 592), (CX + 238, 604), AM, 6, cv2.LINE_AA, tipLength=1.0)
    if k < 1:
        put(fr, moon(42), 1390, 500, 1 - k)
        for j in range(3):
            q = (T * 0.6 + j / 3) % 1
            x = lerp(1330, 1180, q); yy = lerp(520, 580, q)
            cv2.circle(fr, (int(x), int(yy)), int(7 * (1 - q) + 2), mix(GR, (0, 0, 0), k), -1, cv2.LINE_AA)


def tilted(fr, x, y, r, deg, col=WH):
    put(fr, rot_sprite(earth(r), -deg + 0.0), x, y)
    a = math.radians(deg)
    dx, dy = math.sin(a) * r * 1.5, -math.cos(a) * r * 1.5
    cv2.line(fr, (int(x - dx), int(y - dy)), (int(x + dx), int(y + dy)), col, 5, cv2.LINE_AA)
    cv2.line(fr, (int(x), int(y - r * 1.5)), (int(x), int(y + r * 1.5)), DIM, 2, cv2.LINE_AA)


def vis_tilt(fr, T, mode=0, k2=1.0):
    """mode 0: today's steady 23.4 deg lean. mode 1: two studies side by side (wide swing vs small swing)."""
    if mode == 0:
        d = 23.4 + 1.2 * math.sin(T * 0.9)
        tilted(fr, CX, 620, 160, d)
        put(fr, moon(36), 1330, 520 + 6 * math.sin(T))
        put(fr, text(f"{d:4.1f}°", "head", 54, AM), CX + 250, 440)
    else:
        d1 = 42.5 + 42.5 * math.sin(T * 0.7)
        tilted(fr, 690, 630, 130, d1, AM)
        put(fr, text(f"{d1:2.0f}°", "head", 50, AM), 690, 850)
        if k2 > 0:
            d2 = 23.4 + 10 * math.sin(T * 0.55)
            put(fr, np.dstack([np.zeros((2, 2, 3), np.uint8), np.zeros((2, 2), np.uint8)]), 0, 0, 0)
            base = fr.copy() if k2 < 1 else None
            tilted(fr, 1230, 630, 130, d2, CY)
            put(fr, text(f"{d2:2.0f}°", "head", 50, CY), 1230, 850)
            if base is not None:
                cv2.addWeighted(fr, k2, base, 1 - k2, 0, dst=fr)


def vis_gone(fr, T):
    put(fr, moon(120), CX, 600, 0.12)
    for i in range(36):
        a0 = i * 10 + T * 6
        cv2.ellipse(fr, (CX, 600), (124, 124), 0, a0, a0 + 5, GR, 4, cv2.LINE_AA)


# ------------------------------------------------------------------ scenes
def sc_hook(fr, t, T):
    t1, t2, t3 = cl("h1", "hook"), cl("h2", "hook"), cl("h3", "hook")
    g = eio(seg(t, t2 + 0.9, 0.7))
    vis_pair(fr, T, gone=g)
    a1 = 1 - seg(t, t2 - 0.2, 0.3)
    e, s = pop(t, t1 + 0.2)
    put(fr, tl.pill("TONIGHT", WH, INK, 34, 0), CX, 150, e * a1, s)
    e, s = pop(t, t1 + 1.8)
    head(fr, "384,400 KM AWAY", 250, 92, WH, e * a1, s)
    a2 = eo(seg(t, t2 + 0.1, 0.3)) * (1 - seg(t, t3 + 0.4, 0.4))
    head(fr, "NOW DELETE IT.", 220, 100, AM, a2, 0.85 + 0.15 * back(seg(t, t2 + 0.1, 0.45)))
    put(fr, text("no explosion · no debris · just gone", "semi", 40, WH), CX, 310, a2 * eo(seg(t, t2 + 1.6, 0.4)))
    k = seg(t, t3 + 0.7, 0.5)
    if k > 0:
        cv2.addWeighted(fr, 1 - 0.8 * eo(k), np.zeros_like(fr), 0, 0, dst=fr)
        tl.fork(fr, (360, 820), 0, W, 110, 250, 9, kA=1.0, kB=eio(seg(t, t3 + 0.8, 1.0)), phase=-T * 40)
        tl.wordmark(fr, CX, 250, 96, eo(k), 0.8 + 0.2 * back(k), eyes=False, tilt=0)
        for i, ln in enumerate(("WHAT IF THE MOON", "DISAPPEARED?")):
            kk = seg(t, t3 + 1.0 + i * 0.2, 0.45)
            head(fr, ln, 450 + i * 124, 104, AM if i else WH, eo(kk), 0.85 + 0.15 * back(kk))


def sc_moon(fr, t, T):
    ta, ta2, ta2b, ta3 = cl("a", "moon"), cl("a2", "moon"), cl("a2b", "moon"), cl("a3", "moon")
    vis_size(fr, T, seg(t, ta + 1.4, 0.5))
    title(fr, t, "TIMELINE A", GR, [
        (ta + 1.6, ta2, "A QUARTER OF EARTH'S WIDTH", WH, "the Moon is about 3,475 km across"),
        (ta2 + 0.4, ta2b, "ABOUT 4.5 BILLION YEARS OLD", WH, "leading theory: a Mars-sized object hit the young Earth"),
        (ta2b + 0.3, ta3, "IT USED TO BE MUCH CLOSER", WH, "about 22,500 km by one estimate · today about 384,400 km"),
        (ta3 + 0.2, 1e9, "IT'S BEEN RUNNING THINGS", AM, "tides, nights, the length of the day, even the seasons")])


def sc_night(fr, t, T):
    tb, tb2, tb3 = cl("b", "night"), cl("b2", "night"), cl("b3", "night")
    k = eio(seg(t, tb + cdur("b") * 0.52, 1.4))
    vis_night(fr, T, k)
    title(fr, t, "TIMELINE B · NIGHT ONE", CY, [
        (tb + 0.4, tb + cdur("b") * 0.52, "A FULL-MOON NIGHT", WH, "this is what Ana expects to see"),
        (tb + cdur("b") * 0.56, tb2, "THE GLOW IS GONE", AM, None),
        (tb2 + 0.3, tb3, "1,600× BRIGHTER THAN VENUS", WH, "a full Moon vs the next brightest thing in the night sky"),
        (tb3 + 0.3, 1e9, "THE SUN: 400,000× THE MOON", WH, "but at night, the Moon was all we had")])


def sc_tide(fr, t, T):
    tc, tc1b, tc2, tc3 = cl("c", "tide"), cl("c1b", "tide"), cl("c2", "tide"), cl("c3", "tide")
    d = cdur("c2")
    k = eio(seg(t, tc2 + d * 0.66, 2.0))
    vis_tide(fr, T, k)
    title(fr, t, "MORNING · THE TIDES", CY, [
        (tc + 2.4, tc1b, "THE MOON DROVE THE TIDES", WH, None),
        (tc1b + 0.3, tc2, "WHY THE MOON, NOT THE SUN?", WH, "the Sun: 27 million times the mass, but 390 times farther (NOAA)"),
        (tc2 + 0.3, tc2 + d * 0.62, "THE SUN PULLS TOO", WH, "its tidal pull is about half the Moon's (NOAA)"),
        (tc2 + d * 0.66, tc3, "TIDES: ABOUT A THIRD", AM, "our arithmetic from NOAA's figure"),
        (tc3 + 0.2, 1e9, "NO MORE SPRING TIDES", WH, "just a small, steady rise and fall")])


def sc_life(fr, t, T):
    td, td1b, td2 = cl("d", "life"), cl("d1b", "life"), cl("d2", "life")
    d = cdur("d2")
    k = eio(seg(t, td2 + d * 0.42, 1.4))
    vis_reef(fr, T, k, spawn=seg(t, td + 3.0, 2.5) * (1 - k))
    title(fr, t, "UNDER THE WATER", CY, [
        (td + 2.2, td1b, "CORALS SPAWN BY THE MOON", WH, "Great Barrier Reef: a few days after a full Moon"),
        (td1b + 0.2, td2, "EARTH'S LARGEST REPRODUCTION EVENT", WH, "as researchers have described it"),
        (td2 + 0.3, td2 + d * 0.4, "MOONLIGHT IS A SIGNAL", WH, "Kaniewska et al., 2015"),
        (td2 + d * 0.44, 1e9, "THE SIGNAL NEVER COMES", AM, "nobody knows how well they would adapt")])


def sc_day(fr, t, T):
    te, te2, te3 = cl("e", "day"), cl("e2", "day"), cl("e3", "day")
    k = eio(seg(t, te3 + 0.6, 1.0))
    vis_spin(fr, T, k, speed=lerp(1.0, 1.35, k))
    title(fr, t, "THE CLOCK", CY, [
        (te + 1.6, te2, "+2 MILLISECONDS A CENTURY", WH, "the Moon's tidal brake on Earth's spin"),
        (te2 + 0.9, te3, "1.4 BILLION YEARS AGO: 18 HOURS", WH, "the length of a day · Meyers & Malinverno, 2018"),
        (te3 + 0.3, 1e9, "THE BRAKE COMES OFF", AM, "most of that slowing stops")])


def sc_tilt(fr, t, T):
    tf, tf2, tf2b, tf3 = cl("f", "tilt"), cl("f2", "tilt"), cl("f2b", "tilt"), cl("f3", "tilt")
    d = cdur("f")
    if t < tf2 - 0.15:
        vis_tilt(fr, T, 0)
    else:
        vis_tilt(fr, T, 1, k2=eo(seg(t, tf3 + 0.3, 0.6)))
        put(fr, tl.pill("1993 study: 0° to 85°", AM, INK, 28, 0, "bold"), 690, 400, eo(seg(t, tf2 + 0.5, 0.4)))
        put(fr, tl.pill("2012 study: about 10° more", CY, INK, 28, 0, "bold"), 1230, 400, eo(seg(t, tf3 + 0.6, 0.4)))
    title(fr, t, "THE BIGGEST QUESTION", CY, [
        (tf + 1.6, tf + d * 0.55, "EARTH LEANS ABOUT 23°", WH, "that lean gives us seasons"),
        (tf + d * 0.58, tf2, "WITH THE MOON: 22.1° TO 24.5°", WH, "a small, steady wobble"),
        (tf2 + 0.3, tf2b, "WITHOUT IT: A WILD SWING?", AM, "Laskar et al., 1993"),
        (tf2b + 0.3, tf3, "MARS: 0° TO 60°", RED, "two tiny moons · Laskar & Robutel, 1993"),
        (tf3 + 0.3, 1e9, "OR MAYBE NOT SO WILD", CY, "Lissauer et al., 2012 · the science isn't settled")])


def sc_gone(fr, t, T):
    tg = cl("g", "gone"); d = cdur("g")
    vis_gone(fr, T)
    title(fr, t, "ALSO GONE", CY, [(tg + 0.3, 1e9, "SOME THINGS SIMPLY VANISH", WH, None)])
    for i, (f_, lab, x) in enumerate(((0.3, "ECLIPSES", 500), (0.5, "MOONRISE", 880), (0.68, "PHASES OF THE MONTH", 1340))):
        e, s = pop(t, tg + d * f_)
        spr = tl.pill(lab, PANEL2, WH, 34, 0)
        put(fr, spr, x, 840, e, s)
        if e > 0.9:
            w = spr.shape[1] / 2 - 16
            cv2.line(fr, (int(x - w), 838), (int(x - w + 2 * w * eo(seg(t, tg + d * f_ + 0.4, 0.3))), 838), RED, 5, cv2.LINE_AA)


def sc_real(fr, t, T):
    tr, tr2 = cl("r", "real"), cl("r2", "real")
    vis_pair(fr, T, gone=0.0, arrow=seg(t, tr2 + 0.8, 0.8), label=False)
    title(fr, t, "BACK IN TIMELINE A", GR, [
        (tr + 1.2, tr2, "THE MOON IS STAYING PUT", WH, "nothing we know of can make it disappear"),
        (tr2 + 0.4, 1e9, "IT DRIFTS 3.8 CM A YEAR", AM, "so it will be up there for a very long time")])
    stamp(fr, "A THOUGHT EXPERIMENT", CX, 876, t, tr + 3.0, 0.36)


SCN = {"hook": sc_hook, "moon": sc_moon, "night": sc_night, "tide": sc_tide, "life": sc_life, "day": sc_day, "tilt": sc_tilt,
       "gone": sc_gone, "real": sc_real, "outro": R.sc_outro}
SRC = {"hook": "Illustration, not to scale · AI voice · Source: NASA",
       "moon": "Sizes to scale, distance not · Sources: NASA, Royal Museums Greenwich",
       "night": "Illustration · Ana is made up · Source: EarthSky (Moon and Venus brightness)",
       "tide": "Illustration · Source: NOAA Ocean Service; the one-third figure is our arithmetic",
       "life": "Illustration · Source: Kaniewska et al. (2015), eLife",
       "day": "Illustration · Sources: Meyers & Malinverno (2018), PNAS; day-length estimates",
       "tilt": "Illustration, swings sped up · Sources: Laskar et al. (1993); Lissauer et al. (2012)",
       "gone": "Illustration", "real": "Illustration, not to scale · Source: NASA lunar laser ranging", "outro": None}


def scene_frame(i, T):
    name, s0 = R.STARTS[i]
    fr = SKY.copy()
    SCN[name](fr, T - s0, T)
    z = 1.004 + 0.003 * math.sin(T * 0.7)
    M = cv2.getRotationMatrix2D((W / 2 + 8 * math.sin(T * 0.5), H / 2), 0.15 * math.sin(T * 0.6), z)
    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    R.hud(fr, 0.0 if name in ("outro", "hook") else 1.0, SRC[name])
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
                              "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-g", "60", tmp],
                             stdin=subprocess.PIPE)
        for f in range(a, b):
            p.stdin.write(R.frame(f / FPS).tobytes())
        p.stdin.close()
        if p.wait() == 0:
            os.replace(tmp, out); print("done", out)
