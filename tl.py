"""Timeline B shared drawing kit: colours, fonts, text sprites, fork lines, backdrop.
Frames are numpy uint8 RGB arrays. Shapes use OpenCV (anti-aliased), text uses PIL sprites."""
import math
from functools import lru_cache
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BG = (15, 13, 58)        # deep indigo
BG2 = (34, 52, 150)      # blue
EYES = False             # mascot eyes on the B badge
CONFETTI = False
TILT = False
CY = (64, 240, 236)      # Timeline B
AM = (255, 214, 10)      # sunny yellow
PINK = (255, 77, 166)
WH = (255, 255, 255)
GR = (186, 178, 232)     # Timeline A (lavender grey)
DIM = (120, 110, 190)
RED = (255, 92, 92)
SEA = (22, 150, 230)
SEA2 = (20, 62, 170)
ICE = (232, 248, 255)
INK = (26, 10, 66)
PANEL = (14, 12, 50)
PANEL2 = (26, 24, 84)
EDGE = (88, 96, 210)

GF = "/usr/share/fonts/truetype/google-fonts/"
FONTS = {
    "head": GF + "ofl/archivoblack/ArchivoBlack-Regular.ttf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "med": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "mono": GF + "ofl/anonymouspro/AnonymousPro-Bold.ttf",
}


@lru_cache(None)
def font(kind, size):
    return ImageFont.truetype(FONTS[kind], int(size))


@lru_cache(4096)
def text(txt, kind="bold", size=48, color=WH, track=0, pad=8):
    """RGBA sprite (numpy) of one line of text; track = extra px between letters."""
    f = font(kind, size)
    asc, desc = f.getmetrics()
    if track:
        ws = [f.getlength(c) for c in txt]
        w = int(sum(ws) + track * (len(txt) - 1))
    else:
        w = int(f.getlength(txt))
    im = Image.new("RGBA", (w + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track:
        x = pad
        for c, cw in zip(txt, ws):
            d.text((x, pad), c, font=f, fill=color)
            x += cw + track
    else:
        d.text((pad, pad), txt, font=f, fill=color)
    return np.asarray(im)


def put(fr, spr, cx, cy, a=1.0, s=1.0, anchor="c"):
    """Alpha-composite RGBA sprite onto RGB frame. anchor: c, l (left-middle), r (right-middle)."""
    if a <= 0.003 or s <= 0.01:
        return
    if abs(s - 1) > 1e-3:
        spr = cv2.resize(spr, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
    h, w = spr.shape[:2]
    x0 = int(round(cx - w / 2)) if anchor == "c" else int(round(cx)) if anchor == "l" else int(round(cx - w))
    y0 = int(round(cy - h / 2))
    H, W = fr.shape[:2]
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    sp = spr[ya - y0:yb - y0, xa - x0:xb - x0]
    al = sp[..., 3:4].astype(np.float32) * (a / 255.0)
    reg = fr[ya:yb, xa:xb]
    reg[:] = (reg * (1 - al) + sp[..., :3] * al).astype(np.uint8)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def seg(t, t0, d):
    """0..1 progress of t through [t0, t0+d]."""
    return clamp((t - t0) / d) if d > 0 else float(t >= t0)


def eo(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x); return x * x * (3 - 2 * x)


def back(x, k=1.7):
    x = clamp(x) - 1; return 1 + x * x * ((k + 1) * x + k)


def lerp(a, b, k):
    return a + (b - a) * k


def mix(c1, c2, k):
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


@lru_cache(8)
def backdrop(W, H, grid=96, seed=3):
    """Deep indigo gradient with a faint grid, soft glow and sparse dots."""
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    g = np.clip(1.15 - np.hypot((x - 0.5) * 1.25, (y - 0.42) * 1.5), 0, 1) ** 1.6
    im = np.zeros((H, W, 3), np.float32)
    for i in range(3):
        im[..., i] = BG[i] + (BG2[i] - BG[i]) * g
    gs = max(2, int(grid))
    ln = max(1, W // 1900)
    for gx in range(gs // 2, W, gs):
        im[:, gx:gx + ln] += 7
    for gy in range(gs // 2, H, gs):
        im[gy:gy + ln, :] += 7
    rng = np.random.default_rng(seed)
    out = np.clip(im, 0, 255).astype(np.uint8)
    for _ in range(int(W * H / 26000)):
        px, py = int(rng.integers(0, W)), int(rng.integers(0, H))
        cv2.circle(out, (px, py), max(1, W // 1300), mix(BG2, WH, float(rng.uniform(.15, .5))), -1, cv2.LINE_AA)
    return out


def fork_pts(x0, y0, dx, rise, x_end, n=48):
    """Timeline B path: leaves the node, S-curves up by `rise` over `dx`, then runs flat to x_end."""
    pts = [(x0 + dx * i / n, y0 - rise * eio(i / n)) for i in range(n + 1)]
    if x_end > x0 + dx:
        pts.append((x_end, y0 - rise))
    return np.array(pts, np.float32)


def partial(pts, k):
    """First fraction k (0..1) of a polyline by length."""
    if k >= 1:
        return pts
    d = np.hypot(*np.diff(pts, axis=0).T)
    c = np.concatenate([[0], np.cumsum(d)])
    L = c[-1] * clamp(k)
    i = int(np.searchsorted(c, L, side="right") - 1)
    i = min(i, len(pts) - 2)
    r = (L - c[i]) / (d[i] + 1e-9)
    return np.vstack([pts[:i + 1], pts[i] + (pts[i + 1] - pts[i]) * r])


def line(fr, pts, color, w):
    cv2.polylines(fr, [np.round(np.asarray(pts) * 8).astype(np.int32)], False, color, int(w), cv2.LINE_AA, shift=3)


def dashed(fr, x0, x1, y, color, w, dash=26, gap=20, phase=0.0):
    x = x0 - (phase % (dash + gap))
    while x < x1:
        a, b = max(x, x0), min(x + dash, x1)
        if b > a:
            cv2.line(fr, (int(a), int(y)), (int(b), int(y)), color, int(w), cv2.LINE_AA)
        x += dash + gap


def glow(fr, draw, strength=0.9, sigma=14, ds=4):
    """Run draw(layer) on a black layer, blur it and add it to the frame (cheap bloom)."""
    H, W = fr.shape[:2]
    lay = np.zeros((H // ds, W // ds, 3), np.uint8)
    draw(lay, 1.0 / ds)
    lay = cv2.GaussianBlur(lay, (0, 0), sigma / ds)
    lay = cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR)
    cv2.addWeighted(fr, 1.0, lay, strength, 0, dst=fr)


def rrect(fr, x0, y0, x1, y1, r, color, a=1.0):
    """Filled rounded rectangle (anti-aliased), optional opacity."""
    x0, y0, x1, y1, r = int(x0), int(y0), int(x1), int(y1), int(r)
    r = max(0, min(r, (x1 - x0) // 2, (y1 - y0) // 2))
    tgt = fr if a >= 0.999 else fr.copy()
    cv2.rectangle(tgt, (x0 + r, y0), (x1 - r, y1), color, -1, cv2.LINE_AA)
    cv2.rectangle(tgt, (x0, y0 + r), (x1, y1 - r), color, -1, cv2.LINE_AA)
    for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
        cv2.circle(tgt, (cx, cy), r, color, -1, cv2.LINE_AA)
    if tgt is not fr:
        cv2.addWeighted(tgt, a, fr, 1 - a, 0, dst=fr)


@lru_cache(64)
def badge(size, color=CY, ink=BG):
    """The 'B' badge: rounded square with the letter B."""
    S = int(size)
    im = Image.new("RGBA", (S * 2, S * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S * 2 - 1, S * 2 - 1], radius=int(S * 0.44), fill=color)
    f = font("head", S * 1.5)
    d.text((S, S * 0.98), "B", font=f, fill=ink, anchor="mm")
    return np.asarray(im.resize((S, S), Image.LANCZOS))


def wordmark(fr, cx, cy, h, a=1.0, s=1.0):
    """TIMELINE + B badge, centred on (cx, cy); h = letter size in px."""
    t = text("TIMELINE", "head", h, WH, track=int(h * 0.04))
    b = badge(int(h * 1.12))
    gap = h * 0.22
    tot = (t.shape[1] + gap + b.shape[1]) * s
    x = cx - tot / 2
    put(fr, t, x, cy, a, s, "l")
    put(fr, b, x + (t.shape[1] + gap) * s, cy - h * 0.02 * s, a, s, "l")
    return tot


def fork(fr, node, x_left, x_right, rise, dx, w, kA=1.0, kB=1.0, phase=0.0, dot=True, glow_s=0.9):
    """Draw the brand fork: grey Timeline A through `node`, cyan Timeline B branching up."""
    x0, y0 = node
    if kA > 0:
        cv2.line(fr, (int(x_left), int(y0)), (int(lerp(x_left, x0, clamp(kA * 2))), int(y0)), GR, int(w), cv2.LINE_AA)
        if kA > 0.5:
            dashed(fr, x0, lerp(x0, x_right, (kA - 0.5) * 2), y0, DIM, max(2, int(w * 0.6)), w * 3.2, w * 2.4, phase)
    if kB > 0:
        pts = partial(fork_pts(x0, y0, dx, rise, x_right), kB)
        if glow_s:
            glow(fr, lambda lay, k: line(lay, pts * k, CY, max(1, int(w * k * 2.2))), glow_s, sigma=w * 2.4)
        line(fr, pts, CY, w)
        if dot:
            cv2.circle(fr, (int(pts[-1][0]), int(pts[-1][1])), int(w * 1.25), WH, -1, cv2.LINE_AA)
    if kA > 0.5:
        cv2.circle(fr, (int(x0), int(y0)), int(w * 1.9), BG, -1, cv2.LINE_AA)
        cv2.circle(fr, (int(x0), int(y0)), int(w * 1.9), WH, max(2, int(w * 0.7)), cv2.LINE_AA)


# ====================================================================== lively kit (v2)
def _blob(r, col):
    y, x = np.mgrid[-r:r, -r:r].astype(np.float32)
    g = np.clip(1 - np.hypot(x, y) / r, 0, 1) ** 2
    return (g[..., None] * np.array(col, np.float32)).astype(np.uint8)


@lru_cache(8)
def _base(W, H):
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    g = np.clip(0.15 + 0.75 * (0.55 * x + 0.45 * (1 - y)), 0, 1)
    im = np.zeros((H, W, 3), np.float32)
    for i in range(3):
        im[..., i] = BG[i] + (BG2[i] - BG[i]) * g
    out = np.clip(im, 0, 255).astype(np.uint8)
    step = max(28, W // 44)
    for gy in range(step // 2, H, step):          # dot pattern
        for gx in range(step // 2 + (gy // step % 2) * step // 2, W, step):
            cv2.circle(out, (gx, gy), max(1, W // 900), mix(BG2, WH, 0.10), -1, cv2.LINE_AA)
    return out


@lru_cache(16)
def _blobspr(r, col):
    return _blob(r, col)


def _addblob(fr, cx, cy, r, col):
    H, W = fr.shape[:2]
    b = _blobspr(int(r), col)
    x0, y0 = int(cx - r), int(cy - r)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + 2 * int(r), W), min(y0 + 2 * int(r), H)
    if xa < xb and ya < yb:
        reg = fr[ya:yb, xa:xb]
        reg[:] = cv2.add(reg, b[ya - y0:yb - y0, xa - x0:xb - x0])


def star(fr, cx, cy, r, col=WH, rot=0.0):
    pts = []
    for i in range(8):
        a = rot + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.3
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    cv2.fillPoly(fr, [np.round(np.array(pts) * 8).astype(np.int32)], col, cv2.LINE_AA, shift=3)


_PRNG = np.random.default_rng(21)
_PART = _PRNG.random((46, 5))


def bg_frame(W, H, T=0.0, k=1.0):
    """Vivid animated background: gradient, drifting colour glows, rising sparkles."""
    fr = _base(W, H).copy()
    u = W / 1920
    for i, (col, r, fx, fy, ph) in enumerate(((mix((0, 0, 0), PINK, 0.16), 620, .82, .18, 0.0),
                                              (mix((0, 0, 0), CY, 0.14), 560, .12, .86, 2.0),
                                              (mix((0, 0, 0), (120, 90, 255), 0.22), 520, .5, .55, 4.0))):
        _addblob(fr, (fx + 0.07 * math.sin(T * 0.35 + ph)) * W, (fy + 0.08 * math.cos(T * 0.28 + ph)) * H, r * u, col)
    for px, py, sp, sz, tw in _PART:
        y = ((py - T * (0.012 + 0.03 * sp)) % 1.0) * H
        x = (px + 0.012 * math.sin(T * (0.6 + sp) + tw * 6)) * W
        a = 0.35 + 0.65 * abs(math.sin(T * (1 + 2 * tw) + px * 9))
        if sz > 0.93:
            star(fr, x, y, (7 + 9 * sz) * u * a, mix(BG2, WH, 0.9), T * 0.6 + px * 5)
        else:
            cv2.circle(fr, (int(x), int(y)), int((2 + 4 * sz) * u), mix(BG2, WH, 0.25 + 0.5 * a), -1, cv2.LINE_AA)
    return fr


def backdrop(W, H, grid=96, seed=3):
    return bg_frame(W, H, 1.7)


def gline(fr, pts, w, k=1.0, cols=None):
    """Poly-line with a colour gradient along its full length; k draws only the first fraction."""
    cols = cols or (CY, (120, 150, 255), PINK)
    pts = np.asarray(pts, np.float32)
    d = np.hypot(*np.diff(pts, axis=0).T); c = np.concatenate([[0], np.cumsum(d)]); L = c[-1]
    n = max(2, int(L / max(6, w * 0.8)))
    last = None
    for i in range(n + 1):
        q = i / n
        if q > k:
            break
        l = q * L
        j = min(int(np.searchsorted(c, l, side="right") - 1), len(pts) - 2)
        p = pts[j] + (pts[j + 1] - pts[j]) * ((l - c[j]) / (d[j] + 1e-9))
        seg_ = q * (len(cols) - 1); a = min(int(seg_), len(cols) - 2)
        col = mix(cols[a], cols[a + 1], seg_ - a)
        if last is not None:
            cv2.line(fr, (int(last[0] * 8), int(last[1] * 8)), (int(p[0] * 8), int(p[1] * 8)), col, int(w), cv2.LINE_AA, shift=3)
        last = p
    return last


@lru_cache(64)
def badge(size, color=AM, ink=INK):
    """Sticker-style B badge: yellow tile, white rim, soft shadow."""
    S = int(size); P = int(S * 0.14); Q = 3
    im = Image.new("RGBA", ((S + 2 * P) * Q, (S + 2 * P) * Q), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([P * Q, (P + S * 0.07) * Q, (P + S) * Q, (P + S * 1.07) * Q], radius=int(S * 0.26 * Q), fill=(10, 0, 40, 130))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S * 0.035 * Q)))
    d = ImageDraw.Draw(im)
    rim = S * 0.055
    d.rounded_rectangle([(P - rim) * Q, (P - rim) * Q, (P + S + rim) * Q, (P + S + rim) * Q], radius=int((S * 0.24 + rim) * Q), fill=WH)
    d.rounded_rectangle([P * Q, P * Q, (P + S) * Q, (P + S) * Q], radius=int(S * 0.24 * Q), fill=color)
    d.rounded_rectangle([(P + S * .08) * Q, (P + S * .07) * Q, (P + S * .92) * Q, (P + S * .36) * Q], radius=int(S * 0.16 * Q), fill=mix(color, WH, 0.35))
    d.text(((P + S / 2) * Q, (P + S * 0.5) * Q), "B", font=font("head", S * 0.78 * Q), fill=ink, anchor="mm")
    return np.asarray(im.resize((S + 2 * P, S + 2 * P), Image.LANCZOS))


@lru_cache(8)
def _b_holes(S):
    """Centres of the two holes in the letter B (as fractions of the badge sprite)."""
    P = int(S * 0.14); N = S + 2 * P
    im = Image.new("L", (N, N), 0)
    ImageDraw.Draw(im).text((P + S / 2, P + S * 0.5), "B", font=font("head", S * 0.78), fill=255, anchor="mm")
    a = (np.asarray(im) < 128).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(a, connectivity=4)
    holes = [(cen[i][0] / N, cen[i][1] / N, st[i][4]) for i in range(1, n) if st[i][0] > 0 and st[i][1] > 0 and i != lab[0, 0]]
    holes = sorted(holes, key=lambda h: -h[2])[:2]
    return sorted([(h[0], h[1]) for h in holes], key=lambda h: h[1])


def mascot(size, look=(0.0, 0.0), blink=0.0, wow=0.0):
    """The B badge with eyes in the holes of the letter. look in -1..1, blink 0..1, wow 0..1 (wide eyes)."""
    S = int(size)
    if not EYES:
        return badge(S)
    spr = badge(S).copy()
    N = spr.shape[0]
    hs = _b_holes(S)
    if len(hs) < 2:
        return spr
    rgb = np.ascontiguousarray(spr[..., :3])
    r = S * (0.105 + 0.008 * wow)
    for hx, hy in hs:
        cx, cy = hx * N + S * 0.015, hy * N
        ry = max(1.0, r * (1 - 0.9 * blink))
        cv2.ellipse(rgb, (int(cx * 8), int(cy * 8)), (int(r * 8), int(r * 8)), 0, 0, 360, INK, -1, cv2.LINE_AA, shift=3)
        cv2.ellipse(rgb, (int(cx * 8), int(cy * 8)), (int(r * 0.84 * 8), int(max(1, ry - r * 0.16) * 8)), 0, 0, 360, WH, -1, cv2.LINE_AA, shift=3)
        if blink < 0.6:
            px, py = cx + look[0] * r * 0.38, cy + look[1] * r * 0.34
            cv2.circle(rgb, (int(px * 8), int(py * 8)), int(r * (0.5 - 0.1 * wow) * 8), INK, -1, cv2.LINE_AA, shift=3)
            cv2.circle(rgb, (int((px - r * .16) * 8), int((py - r * .18) * 8)), int(r * 0.15 * 8), WH, -1, cv2.LINE_AA, shift=3)
    return np.dstack([rgb, spr[..., 3]])


def rot(spr, deg):
    if not TILT or not deg:
        return spr
    return np.asarray(Image.fromarray(spr).rotate(deg, expand=True, resample=Image.BICUBIC))


def wordmark(fr, cx, cy, h, a=1.0, s=1.0, eyes=True, tilt=-6, T=None):
    """TIMELINE + B sticker, centred on (cx, cy); h = letter size in px."""
    t = text("TIMELINE", "head", h, WH, track=int(h * 0.04))
    sh = text("TIMELINE", "head", h, INK, track=int(h * 0.04))
    bs = int(h * 1.2)
    if T is None:
        b = mascot(bs, (0.3, 0.1)) if eyes and h >= 60 else badge(bs)
    else:
        b = mascot(bs, (0.6 * math.sin(T * 1.3), 0.3 * math.cos(T * 0.9)), blink=1.0 if (T % 3.1) < 0.12 else 0.0)
    b = rot(b, tilt)
    gap = h * 0.02
    tot = (t.shape[1] + gap + b.shape[1]) * s
    x = cx - tot / 2
    put(fr, sh, x + h * 0.05 * s, cy + h * 0.07 * s, a * 0.55, s, "l")
    put(fr, t, x, cy, a, s, "l")
    put(fr, b, x + (t.shape[1] + gap) * s, cy - h * 0.02 * s, a, s, "l")
    return tot


def fork(fr, node, x_left, x_right, rise, dx, w, kA=1.0, kB=1.0, phase=0.0, dot=True, glow_s=0.9):
    """Brand fork: lavender Timeline A through `node`, rainbow Timeline B branching up."""
    x0, y0 = node
    if kA > 0:
        cv2.line(fr, (int(x_left), int(y0)), (int(lerp(x_left, x0, clamp(kA * 2))), int(y0)), GR, int(w), cv2.LINE_AA)
        if kA > 0.5:
            dashed(fr, x0, lerp(x0, x_right, (kA - 0.5) * 2), y0, DIM, max(2, int(w * 0.6)), w * 3.2, w * 2.4, phase)
    if kB > 0:
        pts = fork_pts(x0, y0, dx, rise, x_right)
        if glow_s:
            glow(fr, lambda lay, k: gline(lay, pts * k, max(1, int(w * k * 2.4)), kB), glow_s, sigma=w * 2.2)
        end = gline(fr, pts, w, kB)
        if dot and end is not None:
            cv2.circle(fr, (int(end[0]), int(end[1])), int(w * 1.5), WH, -1, cv2.LINE_AA)
    if kA > 0.5:
        cv2.circle(fr, (int(x0), int(y0)), int(w * 2.0), WH, -1, cv2.LINE_AA)
        cv2.circle(fr, (int(x0), int(y0)), int(w * 1.05), PINK, -1, cv2.LINE_AA)


def burst(fr, cx, cy, t, n=26, seed=0, R=420):
    """Confetti burst: t = seconds since it fired."""
    if not CONFETTI or t < 0 or t > 1.6:
        return
    rng = np.random.default_rng(seed)
    cols = (AM, PINK, CY, WH)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); v = rng.uniform(0.4, 1.0)
        d = R * v * (1 - math.exp(-t * 3.2))
        x = cx + d * math.cos(a); y = cy + d * math.sin(a) + 260 * t * t
        s = (9 + 9 * rng.random()) * clamp(1.5 - t)
        if s < 1:
            continue
        if i % 3 == 0:
            star(fr, x, y, s * 1.5, cols[i % 4], t * 5 + i)
        else:
            cv2.circle(fr, (int(x), int(y)), int(s * 0.7), cols[i % 4], -1, cv2.LINE_AA)


@lru_cache(256)
def pill(txt, bg=AM, fg=INK, size=28, deg=0.0, kind="head"):
    """Sticker pill with text, optional tilt."""
    t = text(txt, kind, size, fg)
    h, w = t.shape[:2]
    px, py, rim = int(size * 0.55), int(size * 0.18), max(3, int(size * 0.12))
    W_, H_ = w + 2 * px + 2 * rim, h + 2 * py + 2 * rim
    im = Image.new("RGBA", (W_ * 2, H_ * 2 + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 10, W_ * 2 - 1, H_ * 2 + 9], radius=H_, fill=(10, 0, 40, 110))
    d.rounded_rectangle([0, 0, W_ * 2 - 1, H_ * 2 - 1], radius=H_, fill=WH)
    d.rounded_rectangle([rim * 2, rim * 2, (W_ - rim) * 2 - 1, (H_ - rim) * 2 - 1], radius=H_ - rim * 2, fill=bg)
    im = im.resize((W_, H_ + 6), Image.LANCZOS)
    im.alpha_composite(Image.fromarray(t), (px + rim, py + rim))
    if deg and TILT:
        im = im.rotate(deg, expand=True, resample=Image.BICUBIC)
    return np.asarray(im)


def save(fr, path):
    Image.fromarray(fr).save(path)
