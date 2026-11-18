"""Timeline B sample episode: What if all the ice on Earth melted?
Usage: render.py stills out.jpg | render.py part A B out.mp4   (frame range [A, B))"""
import json, math, os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import tl
from tl import (CY, AM, WH, GR, DIM, BG, BG2, SEA, SEA2, ICE, RED, PINK, INK, PANEL, PANEL2, EDGE, put, text, seg, eo, eio, back, lerp, mix, clamp)

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 30
J = json.load(open(os.path.join(HERE, "timeline.json")))
L, TOTAL = J["lines"], J["total"]
NF = int(round(TOTAL * FPS))
QUESTION = "WHAT IF ALL THE ICE ON EARTH MELTED?"
STARTS, _seen = [], set()
for x in L:
    if x["scene"] not in _seen:
        _seen.add(x["scene"]); STARTS.append((x["scene"], 0.0 if not STARTS else x["t"] - 0.28))
ST = dict(STARTS)


C = {x["key"]: x for x in L}


def cl(key, scene):
    """Start of narration piece `key`, in the scene's local time."""
    return C[key]["t"] - ST[scene]


def cdur(key):
    return C[key]["d"]


def buddy(fr, x, y, size, T, look=(0.0, 0.0), wow=0.0, hop=14, a=1.0, tilt=0.0):
    """The B mascot: bobs, blinks, looks around."""
    if a <= 0 or not tl.EYES:
        return
    spr = tl.mascot(size, (round(look[0] + 0.25 * math.sin(T * 1.7), 1), round(look[1] + 0.2 * math.cos(T * 1.1), 1)),
                    1.0 if (T % 2.7) < 0.11 else 0.0, round(wow, 1))
    deg = tilt + 5 * math.sin(T * 2.3)
    spr = tl.rot(spr, round(deg))
    put(fr, spr, x, y - hop * abs(math.sin(T * 3.4)), min(1.0, a), 0.6 + 0.4 * back(a) if a < 1 else 1.0)


# ------------------------------------------------------------------ captions
def chunks(s, n=56):
    """Caption pieces: break at sentences, keep short sentences together, split long ones evenly."""
    import re
    sents = re.split(r"(?<=[.:?!]) (?=[A-Z])", s.replace("U.S. ", "U.S.\u00a0"))
    merged = []
    for x in sents:
        if merged and len(merged[-1]) + 1 + len(x) <= 34:
            merged[-1] += " " + x
        else:
            merged.append(x)
    out = []
    for x in merged:
        k = math.ceil(len(x) / n)
        words, tgt, cur = x.split(" "), len(x) / k, ""
        for w in words:
            if cur and len(out_k := cur) + 1 + len(w) > tgt + 4 and k > 1:
                out.append(cur); cur = w; k -= 1
            else:
                cur = (cur + " " + w).strip()
        out.append(cur)
    return [c.replace("\u00a0", " ") for c in out]


CAPS = []
_groups = {}
for x in L:
    _groups.setdefault(x["grp"], []).append(x)
for g, xs in _groups.items():
    full = " ".join(x["text"] for x in xs)
    t0, t1 = xs[0]["t"], xs[-1]["t"] + xs[-1]["d"]
    cs = chunks(full); tot = sum(len(c) for c in cs); t = t0
    for c in cs:
        d = (t1 - t0) * len(c) / tot
        ws = c.split(" "); wt = sum(len(w) + 1 for w in ws); tw = t; words = []
        for w in ws:
            dw = d * (len(w) + 1) / wt
            words.append((w, tw, tw + dw)); tw += dw
        CAPS.append((t, t + d, words)); t += d


def caption(fr, T):
    for a, b, words in CAPS:
        if a - 0.05 <= T < b + 0.15:
            sprs = [text(w, "bold", 44, WH) for w, _, _ in words]
            gap = 17
            tw = sum(sp.shape[1] - 16 for sp in sprs) + gap * (len(sprs) - 1)
            k = eo(seg(T, a - 0.05, 0.14))
            tl.rrect(fr, W / 2 - tw / 2 - 34, 950, W / 2 + tw / 2 + 34, 1034, 30, INK, 0.86 * k)
            x = W / 2 - tw / 2
            for (w, w0, w1), sp in zip(words, sprs):
                ww = sp.shape[1] - 16
                if w0 <= T < w1:
                    q = seg(T, w0, 0.09)
                    put(fr, text(w, "bold", 44, AM), x + ww / 2, 991, k)
                else:
                    put(fr, sp, x + ww / 2, 991, k * (1.0 if T >= w1 else 0.72))
                x += ww + gap
            return


def hud(fr, a=1.0, src=None):
    if a > 0:
        tl.wordmark(fr, 176, 62, 30, a)
        put(fr, tl.pill(QUESTION, INK, WH, 22, 0, "bold"), 1876, 64, a, anchor="r")
    if src:
        put(fr, text(src, "mono", 21, WH), 56, 1056, 0.8, anchor="l")


# ------------------------------------------------------------------ helpers
def water(fr, x0, x1, ylev, ybot, T, alpha=0.62, amp=7, col=SEA, crest=True, wl=150):
    """Semi-transparent sea with a moving wave top between x0..x1, from ylev down to ybot."""
    x0, x1, ybot = int(x0), int(x1), int(ybot)
    top = int(ylev - amp - 3)
    if ybot <= top:
        return
    top = max(top, 0)
    xs = np.arange(0, x1 - x0 + 12, 12, dtype=np.float32)
    ys = ylev + amp * np.sin(xs / wl * 2 * math.pi + T * 2.2) * 0.6 + amp * 0.4 * np.sin(xs / (wl * 0.37) - T * 3.1) - top
    roi = fr[top:ybot, x0:x1].copy()
    lay = roi.copy()
    poly = np.vstack([np.stack([xs, ys], 1), [[x1 - x0 + 12, ybot - top], [0, ybot - top]]]).astype(np.int32)
    cv2.fillPoly(lay, [poly], col, cv2.LINE_AA)
    g = np.linspace(1.0, 0.55, lay.shape[0], dtype=np.float32)[:, None, None]
    m = (lay != roi).any(2, keepdims=True)
    lay = np.where(m, (lay * g + np.array(SEA2, np.float32) * (1 - g)).astype(np.uint8), lay)
    cv2.addWeighted(lay, alpha, roi, 1 - alpha, 0, dst=roi)
    if crest:
        cv2.polylines(roi, [np.stack([xs, ys], 1).astype(np.int32)], False, mix(col, WH, 0.65), 3, cv2.LINE_AA)
    fr[top:ybot, x0:x1] = roi


def earth(ice=True, R=250):
    """Stylised globe (illustration, not a map)."""
    S = R * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, S - 1, S - 1], fill=(24, 96, 178))
    rng = np.random.default_rng(11)
    land, soil = (64, 158, 112), (150, 128, 96)
    blobs = [(.30, .40, .17, .12), (.36, .52, .10, .15), (.62, .36, .22, .13), (.70, .50, .12, .12), (.57, .62, .08, .11),
             (.80, .66, .08, .05), (.25, .30, .10, .07)]
    for bx, by, bw, bh in blobs:
        for _ in range(7):
            ox, oy = rng.normal(0, bw * .35), rng.normal(0, bh * .35)
            rw, rh = bw * rng.uniform(.5, .9), bh * rng.uniform(.5, .9)
            d.ellipse([(bx + ox - rw) * S, (by + oy - rh) * S, (bx + ox + rw) * S, (by + oy + rh) * S], fill=land)
    cap = (232, 246, 255) if ice else soil
    if ice:
        d.ellipse([.22 * S, -.20 * S, .78 * S, .115 * S], fill=cap)                       # Arctic sea ice
    for gx, gy, gw, gh in ((.42, .17, .075, .06), (.45, .215, .05, .055), (.40, .13, .05, .03)):   # Greenland
        d.ellipse([(gx - gw) * S, (gy - gh) * S, (gx + gw) * S, (gy + gh) * S], fill=cap if ice else land)
    if ice:
        d.ellipse([.10 * S, .85 * S, .90 * S, 1.25 * S], fill=cap)                       # Antarctica
    else:
        for ax, aw in ((.38, .14), (.56, .10), (.66, .05)):
            d.ellipse([(ax - aw) * S, .90 * S, (ax + aw) * S, 1.12 * S], fill=soil)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([2, 2, S - 3, S - 3], fill=255)
    sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh).ellipse([-.25 * S, -.3 * S, .85 * S, .8 * S], fill=255)
    sh = sh.filter(ImageFilter.GaussianBlur(S * .12))
    dark = Image.new("RGBA", (S, S), (4, 8, 40, 255))
    im = Image.composite(im, Image.blend(im, dark, 0.34), sh)
    im.putalpha(mask)
    return np.asarray(im.resize((R * 2, R * 2), Image.LANCZOS))


EARTH = {True: earth(True), False: earth(False)}


def halo(fr, cx, cy, r, col, s=0.5):
    tl.glow(fr, lambda lay, k: cv2.circle(lay, (int(cx * k), int(cy * k)), int(r * k), col, -1, cv2.LINE_AA), s, sigma=46)


def stamp_sprite(txt="NOT A FORECAST", col=AM):
    t = text(txt, "head", 104, col, track=4)
    h, w = t.shape[:2]
    im = Image.new("RGBA", (w + 110, h + 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, w + 103, h + 63], radius=26, outline=col, width=10)
    im.alpha_composite(Image.fromarray(t), (55, 35))
    return np.asarray(im.rotate(5, expand=True, resample=Image.BICUBIC))


STAMP = stamp_sprite()


def value(fr, pre, val, x, y, col, size, a=1.0):
    """Right-aligned big value with a small prefix word (ABOUT / UNDER)."""
    v = text(val, "head", size, col)
    put(fr, v, x, y, a, anchor="r")
    put(fr, text(pre, "mono", int(size * 0.34), GR, track=2), x - v.shape[1] - 6, y + size * 0.16, a, anchor="r")


# ------------------------------------------------------------------ scenes
def sc_open(fr, t, T):
    yA, node = 838, (430, 838)
    tf, tm = cl("b", "open") - 0.05, cl("c", "open") + 0.75
    kf = seg(t, tf, 0.9)
    if kf <= 0:
        cv2.line(fr, (0, yA), (int(W * eo(seg(t, 0.1, 0.9))), yA), GR, 9, cv2.LINE_AA)
    else:
        tl.fork(fr, node, 0, W, 118, 250, 9, kA=1.0, kB=eio(kf), phase=-T * 40)
        kb = seg(t, tf + 0.55, 0.4)
        put(fr, tl.pill("TIMELINE B", CY, INK, 28, 0), 800, 780, eo(kb), 0.6 + 0.4 * back(kb))
        buddy(fr, 1640, 838 - 118 - 78, 150, T, (-0.6, 0.0), wow=seg(t, tm, 0.3), a=seg(t, tf + 0.8, 0.35))
        tl.burst(fr, 1250, 470, t - tm - 0.25, 34, 3)
    put(fr, text("TIMELINE A", "mono", 30, GR, track=5), 70, 798, eo(seg(t, 0.5, 0.4)), anchor="l")
    # globe
    ex, ey = 500, 420 + 6 * math.sin(T * 1.3)
    s = back(seg(t, 0.25, 0.7))
    km = eio(seg(t, tm, 1.3))
    halo(fr, ex, ey, 262 * s, mix((90, 160, 255), CY, km), 0.42)
    put(fr, EARTH[True], ex, ey, 1.0, s)
    if km > 0:
        put(fr, EARTH[False], ex, ey, km, s)
    # stat (Timeline A) then title (Timeline B)
    a1 = eo(seg(t, 1.5, 0.4)) * (1 - seg(t, tm - 0.1, 0.3))
    if a1 > 0:
        x = 900
        put(fr, text("ABOUT", "mono", 34, GR, track=6), x + 6, 262, a1, anchor="l")
        put(fr, text("10%", "head", 210, AM), x, 400 + 40 * (1 - back(seg(t, 1.5, 0.5))), a1, anchor="l")
        put(fr, text("of Earth's land is covered", "semi", 50, WH), x + 6, 548, a1, anchor="l")
        put(fr, text("by glacier ice", "semi", 50, WH), x + 6, 612, a1, anchor="l")
    a2 = seg(t, tm + 0.15, 0.35)
    if a2 > 0:
        x = 880
        put(fr, tl.pill("WHAT IF...", CY, INK, 38, 0), x + 4, 262, eo(a2), 0.6 + 0.4 * back(a2), anchor="l")
        for i, ln in enumerate(("ALL THE ICE", "ON EARTH", "MELTED?")):
            k = seg(t, tm + 0.3 + i * 0.16, 0.4)
            put(fr, text(ln, "head", 112, INK), x + 7, 380 + i * 118, eo(k) * 0.5, anchor="l")
            put(fr, text(ln, "head", 112, AM if i == 2 else WH), x + 90 * (1 - back(k)), 372 + i * 118, eo(k), anchor="l")


def panel(fr, x0, y0, x1, y1, draw, dim=0.0):
    tl.rrect(fr, x0 - 6, y0 - 6, x1 + 6, y1 + 6, 30, EDGE)
    roi = np.ascontiguousarray(fr[y0:y1, x0:x1])
    roi[:] = PANEL
    draw(roi)
    if dim > 0:
        roi[:] = (roi * (1 - dim) + np.array(BG, np.float32) * dim).astype(np.uint8)
    fr[y0:y1, x0:x1] = roi


def sc_float(fr, t, T):
    tR = cl("f", "float") - 0.1
    kin = back(seg(t, 0.0, 0.55), 1.2)
    TBC = cl("e", "float") + cdur("e") - 1.4
    mL = eio(seg(t, cl("e", "float") + 0.5, 2.6))            # left melt
    mR = eio(seg(t, tR + 0.35, 2.2))      # right melt
    act = seg(t, tR - 0.2, 0.4)

    def left(p):
        w, h = p.shape[1], p.shape[0]
        yw = 250
        s = 1 - mL
        if s > 0.02:
            bw, bh = 330 * (0.35 + 0.65 * s), 230 * s
            cx = w / 2 + 6 * math.sin(T * 0.9)
            top = yw - bh * 0.11 + 4 * math.sin(T * 1.7)
            pts = np.array([[cx - bw / 2, top + bh * .12], [cx - bw * .3, top], [cx + bw * .34, top + bh * .03],
                            [cx + bw / 2, top + bh * .16], [cx + bw * .42, top + bh * .8], [cx + bw * .1, top + bh],
                            [cx - bw * .36, top + bh * .86]], np.int32)
            cv2.fillPoly(p, [pts], ICE, cv2.LINE_AA)
            cv2.polylines(p, [pts[:4]], False, WH, 4, cv2.LINE_AA)
        water(p, 0, w, yw, h, T, 0.66, 6)
        tl.dashed(p, 0, w, yw, WH, 3, 18, 14)
        put(p, text("sea level", "mono", 24, WH), w - 24, yw - 26, 0.9, anchor="r")
        put(p, text("BARELY CHANGES", "head", 50, AM), w / 2, h - 74, back(seg(t, TBC, 0.45)), 0.6 + 0.4 * back(seg(t, TBC, 0.45)))

    def right(p):
        w, h = p.shape[1], p.shape[0]
        y0w, rise = 430, 96
        rock = np.array([[0, h], [0, 470], [210, 410], [400, 250], [w, 215], [w, h]], np.int32)
        if mR < 0.98:
            dome = [(420 + (w - 420) * i / 30, 244 - 29 * i / 30 - (1 - mR) * 170 * math.sin(min(1, i / 9) * math.pi / 2))
                    for i in range(31)]
            pts = np.array(dome + [(w, 215), (400, 250)], np.int32)
            cv2.fillPoly(p, [pts], ICE, cv2.LINE_AA)
            cv2.polylines(p, [np.array(dome, np.int32)], False, WH, 4, cv2.LINE_AA)
        cv2.fillPoly(p, [rock], (86, 80, 108), cv2.LINE_AA)
        cv2.polylines(p, [rock[1:5]], False, (126, 120, 150), 4, cv2.LINE_AA)
        if 0.02 < mR < 0.97:   # meltwater running down the slope
            for j in range(9):
                q = ((T * 0.9 + j / 9) % 1)
                x = lerp(400, 215, q); y = lerp(250, 408, q)
                cv2.circle(p, (int(x), int(y - 8)), 7, CY, -1, cv2.LINE_AA)
        lev = y0w - rise * mR
        water(p, 0, w, lev, h, T, 0.66, 6)
        tl.dashed(p, 0, 330, y0w, WH, 3, 18, 14)
        put(p, text("before", "mono", 24, WH), 20, y0w + 26, 0.9, anchor="l")
        if mR > 0.15:
            ax = 110
            cv2.arrowedLine(p, (ax, y0w - 6), (ax, int(lev + 14)), AM, 6, cv2.LINE_AA, tipLength=0.3)
        k = back(seg(t, tR + 1.7, 0.45))
        put(p, text("SEA LEVEL RISES", "head", 50, CY), w / 2 + 110, h - 74, k, 0.6 + 0.4 * k)

    yo = int(40 * (1 - kin))
    panel(fr, 110, 250 + yo, 930, 810 + yo, left, dim=0.45 * act)
    panel(fr, 990, 250 + yo, 1810, 810 + yo, right, dim=0.5 * (1 - act))
    put(fr, text("FLOATING SEA ICE", "head", 42, mix(WH, GR, act)), 112, 200 + yo, kin, anchor="l")
    put(fr, text("ICE ON LAND", "head", 42, mix(GR, WH, act)), 992, 200 + yo, kin, anchor="l")
    put(fr, text("already in the water", "mono", 26, GR), 928, 204 + yo, kin, anchor="r")
    put(fr, text("ice sheets + glaciers", "mono", 26, GR), 1808, 204 + yo, kin, anchor="r")
    buddy(fr, 960, 128, 108, T, (-0.8 + 1.6 * act, 0.7), wow=seg(t, tR + 0.4, 0.3) * (1 - seg(t, tR + 2.6, 0.4)), a=seg(t, 0.4, 0.35))


def sc_count(fr, t, T):
    gx0, gx1, y0, y70 = 250, 450, 870, 190
    ppm = (y0 - y70) / 70.0
    parts = [("GREENLAND ICE SHEET", "ABOUT", "7 m", 7.4, mix(CY, WH, 0.55), cl("g", "count") + 1.5, 1.3, "NSIDC"),
             ("ANTARCTIC ICE SHEET", "ABOUT", "58 m", 58.0, CY, cl("h", "count") + 0.25, 1.2, "NSIDC"),
             ("MOUNTAIN GLACIERS", "UNDER", "0.5 m", 0.4, AM, cl("ij", "count") + 0.5, 0.6, "USGS")]
    kin = eo(seg(t, 0, 0.5))
    tt = cl("ij", "count") + cdur("ij") - 1.25
    tl.rrect(fr, gx0 - 10, y70 - 10, gx1 + 10, y0 + 10, 22, EDGE, kin)
    tl.rrect(fr, gx0, y70, gx1, y0, 14, PANEL, kin)
    lvl = 0.0
    for name, pre, val, m, col, ts, dur, src in parts:
        k = eio(seg(t, ts, dur))
        if k > 0:
            ya, yb = y0 - lvl * ppm, y0 - (lvl + m * k) * ppm
            cv2.rectangle(fr, (gx0, int(yb)), (gx1, int(ya)), col, -1)
            if m * k * ppm > 3:
                cv2.line(fr, (gx0, int(ya)), (gx1, int(ya)), BG, 2)
        lvl += m * k
    if lvl > 0.3:
        water(fr, gx0, gx1, y0 - lvl * ppm, y0 - lvl * ppm + 16, T, 0.9, 4, col=mix(CY, WH, 0.5), crest=False, wl=90)
    for m in range(0, 71, 10):
        y = int(y0 - m * ppm)
        cv2.line(fr, (gx0 - 34, y), (gx0 - 12, y), GR, 3, cv2.LINE_AA)
        put(fr, text(f"{m} m", "mono", 26, GR), gx0 - 46, y, kin, anchor="r")
    put(fr, text("SEA LEVEL RISE", "mono", 24, GR, track=3), (gx0 + gx1) / 2, y0 + 38, kin)
    buddy(fr, gx1 + 78, y0 - lvl * ppm - 40, 104, T, (-0.3, 0.4), wow=seg(t, tt, 0.3), a=seg(t, 0.3, 0.35))
    tl.burst(fr, 1200, 770, t - tt - 0.1, 36, 5)
    # rows
    for i, (name, pre, val, m, col, ts, dur, src) in enumerate(parts):
        k = eo(seg(t, ts - 0.1, 0.45)); y = 246 + i * 138; xo = 90 * (1 - back(seg(t, ts - 0.1, 0.5)))
        if k <= 0:
            continue
        tl.rrect(fr, 600 + xo, y - 52, 1800 + xo, y + 52, 22, PANEL2, 0.92 * k)
        cv2.circle(fr, (int(652 + xo), y), 15, col, -1, cv2.LINE_AA)
        put(fr, text(name, "bold", 40, WH), 690 + xo, y - 12, k, anchor="l")
        put(fr, text(f"if it all melted · {src}", "mono", 22, GR), 692 + xo, y + 26, k, anchor="l")
        value(fr, pre, val, 1770 + xo, y, col, 74, k)
    k = seg(t, tt, 0.5)
    if k > 0:
        y = y70
        tl.dashed(fr, gx0 - 60, gx1 + 90, y, WH, 4, 16, 10)
        e = back(k)
        tl.glow(fr, lambda lay, q: tl.rrect(lay, 600 * q, 668 * q, 1800 * q, 880 * q, 20 * q, CY), 0.25 * eo(k), sigma=30)
        tl.rrect(fr, 596, 664, 1804, 884, 30, CY, eo(k))
        tl.rrect(fr, 602, 670, 1798, 878, 25, PANEL, eo(k))
        put(fr, text("TOTAL", "head", 54, WH), 650, 740, eo(k), anchor="l")
        put(fr, text("U.S. Geological Survey estimate", "bold", 30, WH), 652, 800, eo(k), anchor="l")
        put(fr, text("totals vary by study, about 65–70 m", "mono", 23, GR), 652, 842, eo(k), anchor="l")
        v = text("70 m", "head", 150, CY)
        put(fr, v, 1766, 770, eo(k), 0.7 + 0.3 * e, anchor="r")
        put(fr, text("ABOUT", "mono", 34, GR, track=3), 1766 - v.shape[1] * (0.7 + 0.3 * e) - 4, 796, eo(k), anchor="r")


_rng = np.random.default_rng(5)
SKY = []
_x = 560
while _x < W + 40:
    _w = int(_rng.integers(70, 150)); _h = int(_rng.integers(110, 430))
    SKY.append((_x, _w, _h, int(_rng.integers(0, 3)))); _x += _w + int(_rng.integers(6, 26))
BACK = [(int(x), int(_rng.integers(80, 170)), int(_rng.integers(160, 520))) for x in range(-40, W, 150)]
CITIES = [("MANILA", 930), ("TOKYO", 1160), ("NEW YORK", 1420), ("LONDON", 1700)]


def building(fr, x, w, h, g, body, win, lit, floors=None):
    cv2.rectangle(fr, (x, g - h), (x + w, g), body, -1)
    cv2.rectangle(fr, (x, g - h), (x + w, g - h + 6), mix(body, WH, 0.25), -1)
    fh = h / floors if floors else 30
    n = floors or int(h // 30)
    cols = max(2, w // 34)
    cw = (w - 20) / cols
    for r in range(n):
        y = int(g - (r + 1) * fh + fh * 0.28)
        for c in range(cols):
            on = ((r * 7 + c * 13 + x) % 5) < 3
            cv2.rectangle(fr, (int(x + 10 + c * cw + 4), y), (int(x + 10 + (c + 1) * cw - 4), int(y + fh * 0.44)),
                          lit if on else win, -1)


def sc_city(fr, t, T):
    g, bx, bw, bh = 880, 300, 220, 600
    ppm = bh / 70.0
    kin = eo(seg(t, 0, 0.5))
    for x, w, h in BACK:
        cv2.rectangle(fr, (x, g - h), (x + w, g), (22, 28, 72), -1)
    for x, w, h, _ in SKY:
        building(fr, x, w, h, g, (38, 46, 104), (30, 37, 86), (104, 112, 168))
    building(fr, bx, bw, bh, g, (64, 74, 150), (44, 52, 112), (255, 214, 120), floors=20)
    cv2.rectangle(fr, (0, g), (W, g + 30), (20, 25, 62), -1)
    # ruler
    rx = bx - 50
    cv2.line(fr, (rx, g), (rx, g - bh), GR, 3, cv2.LINE_AA)
    for m in range(0, 71, 10):
        y = int(g - m * ppm)
        cv2.line(fr, (rx - 18, y), (rx, y), GR, 3, cv2.LINE_AA)
        put(fr, text(f"{m} m", "mono", 24, GR), rx - 28, y, kin, anchor="r")
    put(fr, text("20 STOREYS", "mono", 26, WH, track=3), bx + bw / 2, g - bh - 34, eo(seg(t, 0.5, 0.4)))
    k = eio(seg(t, 0.35, 1.9))
    lev = g - bh * k
    if k > 0:
        water(fr, 0, W, lev, g + 30, T, 0.6, 9)
        n = int(round(70 * k))
        tl.rrect(fr, bx + bw + 30, lev - 104, bx + bw + 290, lev - 22, 22, INK, 0.8)
        put(fr, text(f"+{n} m", "head", 62, WH), bx + bw + 160, lev - 64)
    t2 = cl("l", "city")
    kh = seg(t, t2 + 0.05, 0.4)
    put(fr, tl.pill("EVERY COASTAL CITY ON THE PLANET WOULD FLOOD", INK, WH, 34, 0), 1260, 136, eo(kh), 0.7 + 0.3 * back(kh))
    buddy(fr, 112, min(g - 58, lev - 40), 108, T, (0.7, -0.3), wow=k * (1 - seg(t, 3.2, 0.5)), hop=8, a=seg(t, 0.2, 0.3))
    names_t = [cl(m, "city") - 0.04 for m in ("m1", "m2", "m3", "m4")]
    for (nm, x), tn in zip(CITIES, names_t):
        kk = seg(t, tn, 0.4)
        if kk <= 0:
            continue
        e = back(kk); y = lev - 70 + 5 * math.sin(T * 2 + x)
        spr = text(nm, "head", 36, INK)
        w2 = spr.shape[1] / 2 + 18
        cv2.line(fr, (x, int(y + 26)), (x, int(lev + 150)), AM, 4, cv2.LINE_AA)
        cv2.circle(fr, (x, int(lev + 150)), 9, AM, -1, cv2.LINE_AA)
        tl.burst(fr, x, y, t - tn, 9, x, 150)
        tl.rrect(fr, x - w2 * e - 5, y - 30 * e - 5, x + w2 * e + 5, y + 30 * e + 5, 20, WH)
        tl.rrect(fr, x - w2 * e, y - 30 * e, x + w2 * e, y + 30 * e, 16, AM)
        put(fr, spr, x, y, eo(kk), 0.5 + 0.5 * e)


def sc_real(fr, t, T):
    tb = cl("p", "real") - 0.2
    aA = 1 - seg(t, tb - 0.3, 0.3)
    aB = seg(t, tb, 0.35)
    if aA > 0:
        base = fr.copy() if aA < 1 else None
        cv2.line(fr, (0, 838), (int(W * eo(seg(t, 0.0, 0.8))), 838), GR, 9, cv2.LINE_AA)
        put(fr, text("BACK IN TIMELINE A", "mono", 30, GR, track=5), 70, 798, eo(seg(t, 0.2, 0.4)), anchor="l")
        buddy(fr, 1720, 838 - 66, 120, T, (-0.7, -0.2), hop=22, a=seg(t, 0.3, 0.3))
        ks = seg(t, cl("n", "real") + cdur("n") - 1.15, 0.4)
        if ks > 0:
            put(fr, STAMP, 960, 290, min(1, ks * 2), 1.5 - 0.5 * back(ks, 2.4))
        ty = cl("o", "real") + 0.9
        ky = seg(t, ty, 0.4)
        if ky > 0:
            x0, x1, y = 300, 1620, 640
            cv2.line(fr, (x0, y), (x1, y), DIM, 8, cv2.LINE_AA)
            p = eio(seg(t, ty + 0.3, cdur("o") - 1.7))
            xe = int(lerp(x0, x1, p))
            tl.glow(fr, lambda lay, q: cv2.line(lay, (int(x0 * q), int(y * q)), (int(xe * q), int(y * q)), AM, 6), 0.8, 16)
            cv2.line(fr, (x0, y), (xe, y), AM, 8, cv2.LINE_AA)
            for i in range(11):
                xx = int(lerp(x0, x1, i / 10))
                cv2.line(fr, (xx, y - 14), (xx, y + 14), WH if xx <= xe else DIM, 3, cv2.LINE_AA)
            cv2.circle(fr, (xe, y), 15, WH, -1, cv2.LINE_AA)
            put(fr, text("TODAY", "mono", 26, WH, track=3), x0, y + 46, ky)
            n = int(round(5000 * p / 100) * 100)
            lab = f"{n:,}" + ("+ YEARS" if p >= 1 else " YEARS")
            put(fr, text(lab, "head", 104, WH), 960, 520, eo(ky))
            put(fr, text("to melt all of Earth's ice, some scientists say", "semi", 40, WH), 960, 722, eo(seg(t, ty + 0.5, 0.4)))
        if base is not None:
            cv2.addWeighted(fr, aA, base, 1 - aA, 0, dst=fr)
    if aB > 0:
        base = fr.copy() if aB < 1 else None
        px, y1880, rise = 520, 740, 140
        k = eio(seg(t, tb + 0.5, 2.0))
        lev = y1880 - rise * k
        cv2.rectangle(fr, (0, 880), (W, 910), (20, 25, 62), -1)
        tl.rrect(fr, px - 36, 210, px + 36, 884, 12, (226, 230, 244))
        for i in range(34):
            yy = 236 + i * 19
            cv2.line(fr, (px - 36, yy), (px - (8 if i % 5 else -8), yy), (60, 66, 110), 3)
        cv2.rectangle(fr, (px - 36, 210), (px + 36, 236), RED, -1)
        water(fr, 0, W, lev, 884, T, 0.62, 7)
        tl.dashed(fr, 60, 1000, y1880, WH, 4, 20, 14)
        put(fr, text("1880 level", "mono", 28, WH), 70, y1880 + 30, 1, anchor="l")
        if k > 0.1:
            bx = 660
            cv2.line(fr, (bx, int(lev)), (bx, y1880), AM, 6, cv2.LINE_AA)
            cv2.line(fr, (bx - 18, int(lev)), (bx + 18, int(lev)), AM, 6, cv2.LINE_AA)
            cv2.line(fr, (bx - 18, y1880), (bx + 18, y1880), AM, 6, cv2.LINE_AA)
            put(fr, text("today", "mono", 28, WH), 70, lev - 30, 1, anchor="l")
        kt = eo(seg(t, cl("q", "real") + 0.2, 0.5))
        put(fr, tl.pill("THE SEA REALLY IS RISING", CY, INK, 30, -2), 1010, 258, eo(seg(t, tb + 0.3, 0.4)), anchor="l")
        put(fr, text("21–24 cm", "head", 150, AM), 1000 + 80 * (1 - back(seg(t, cl("q", "real") + 0.2, 0.5))), 388, kt, anchor="l")
        buddy(fr, 345, lev - 44, 110, T, (0.7, -0.4), hop=8)
        put(fr, text("higher than in 1880, global average", "semi", 44, WH), 1010, 504, kt, anchor="l")
        put(fr, text("gauge not to scale", "mono", 24, WH), 70, 850, 0.8, anchor="l")
        if base is not None:
            cv2.addWeighted(fr, aB, base, 1 - aB, 0, dst=fr)


def sc_outro(fr, t, T):
    import script as SCR
    k = seg(t, 0.1, 1.6)
    tl.fork(fr, (500, 668), 0, W, 0, 10, 9, kA=min(1, k * 1.6), kB=0, phase=-T * 40) if False else None
    tl.fork(fr, (430, 690), 0, W, 110, 250, 9, kA=min(1.0, k * 2), kB=eio(seg(t, 0.5, 1.1)), phase=-T * 40)
    e = seg(t, 0.35, 0.6)
    if e > 0:
        tl.wordmark(fr, 960, 250, 136, eo(e), 0.7 + 0.3 * back(e), T=T)
        tl.burst(fr, 960, 250, t - 0.55, 44, 9, 620)
    put(fr, text("What if things went differently?", "semi", 52, WH), 960, 384, eo(seg(t, 0.9, 0.4)), 0.7 + 0.3 * back(seg(t, 0.9, 0.45)))
    kq = seg(t, cl("s", "outro"), 0.45)
    put(fr, text("WHAT SHOULD WE CHANGE NEXT?", "head", 54, AM), 960, 500, eo(kq), 0.85 + 0.15 * back(kq))
    ks = eo(seg(t, 2.6, 0.5))
    if ks > 0:
        tl.rrect(fr, 380, 740, 1540, 935, 22, INK, 0.86 * ks)
        put(fr, text("SOURCES", "mono", 22, CY, track=4), 410, 768, ks, anchor="l")
        for i, s in enumerate(SCR.SOURCES):
            put(fr, text(s, "mono", 23, WH), 410, 804 + i * 31, ks, anchor="l")
        put(fr, text("AI voice · illustrations are schematic, not to scale", "mono", 20, GR), 1510, 768, ks, anchor="r")


PUNCH = [] if not tl.CONFETTI else [C["a"]["t"] + 0.95, C["c"]["t"] + 1.0, C["e"]["t"] + cdur("e") - 1.4, C["f"]["t"] + 1.6, C["g"]["t"] + 1.5, C["h"]["t"] + 0.25,
         C["ij"]["t"] + cdur("ij") - 1.25, C["m1"]["t"], C["m2"]["t"], C["m3"]["t"], C["m4"]["t"],
         C["n"]["t"] + cdur("n") - 1.15, C["q"]["t"] + 0.2, ST["outro"] + 0.55, C["s"]["t"]]
SCN = {"open": sc_open, "float": sc_float, "count": sc_count, "city": sc_city, "real": sc_real, "outro": sc_outro}
SRC = {"open": "Illustration, not a map · AI voice · Source: NSIDC", "float": "Illustration · Source: NSIDC, USGS",
       "count": "Sources: NSIDC, USGS", "city": "Illustration, no real skyline · Source: USGS",
       "real": "Sources: National Geographic (2013), NOAA Climate.gov", "outro": None}


def scene_frame(i, T):
    name, s0 = STARTS[i]
    fr = tl.bg_frame(W, H, T)
    SCN[name](fr, T - s0, T)
    t = T - s0
    z = 1.008 + 0.005 * math.sin(T * 0.7) + sum(0.035 * math.exp(-(T - pc) * 7) for pc in PUNCH if 0 <= T - pc < 0.8)
    M = cv2.getRotationMatrix2D((W / 2 + 10 * math.sin(T * 0.5), H / 2), 0.25 * math.sin(T * 0.6), z)
    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    hud(fr, 0.0 if name == "outro" else eo(seg(t, cl("c", "open") + 1.9, 0.5)) if name == "open" else 1.0, SRC[name])
    return fr


def frame(T):
    i = max(k for k, (_, s) in enumerate(STARTS) if s <= T)
    fr = scene_frame(i, T)
    # wipe transitions: the last 0.2 s of a scene and first 0.2 s of the next share a sweeping bar
    D = 0.2
    for j, other in ((i + 1, False), (i, True)):
        if 0 < j < len(STARTS):
            b = STARTS[j][1]
            p = (T - (b - D)) / (2 * D)
            if 0 <= p < 1:
                x = int(lerp(-160, W + 160, eio(p)))
                if not other:          # still in old scene: new scene shows left of the bar
                    nw = scene_frame(j, b + 0.001)
                    fr[:, :max(0, x)] = nw[:, :max(0, x)]
                else:                  # in new scene: old scene remains right of the bar
                    old = scene_frame(j - 1, b - 0.001)
                    fr[:, max(0, x):] = old[:, max(0, x):]
                cv2.rectangle(fr, (x - 70, 0), (x, H), CY, -1)
                cv2.rectangle(fr, (x - 110, 0), (x - 86, H), WH, -1)
                break
    caption(fr, T)
    if T > TOTAL - 0.6:
        fr = (fr * clamp((TOTAL - T) / 0.6)).astype(np.uint8)
    return fr


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ts = [float(x) for x in sys.argv[3:]]
        ims = [cv2.resize(frame(T), (960, 540), interpolation=cv2.INTER_AREA) for T in ts]
        rows = [np.hstack(ims[i:i + 2]) for i in range(0, len(ims), 2)]
        Image.fromarray(np.vstack(rows)).save(sys.argv[2], quality=88)
    elif sys.argv[1] == "one":
        Image.fromarray(frame(float(sys.argv[3]))).save(sys.argv[2], quality=92)
    else:
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        tmp = out + ".tmp.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                              "-pix_fmt", "yuv420p", "-g", "60", tmp], stdin=subprocess.PIPE)
        for f in range(a, b):
            p.stdin.write(frame(f / FPS).tobytes())
        p.stdin.close()
        if p.wait() == 0:
            os.replace(tmp, out)
            print("done", out)
