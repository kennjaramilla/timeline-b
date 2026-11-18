"""Cinematic space kit for Timeline B: procedural planets, star field, nebula. All original artwork."""
import math
from functools import lru_cache
import cv2
import numpy as np


def _noise(w, h, seed, octaves=6, base=4):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32); amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        a = rng.random((max(2, n // 2), n), dtype=np.float32)
        a = np.concatenate([a, a[:, :1]], 1)                      # wrap in longitude
        out += cv2.resize(a, (w, h), interpolation=cv2.INTER_CUBIC) * amp
        tot += amp; amp *= 0.55
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)


@lru_cache(32)
def planet(R, kind="A", seed=1, rot=0.0, light=(-0.55, -0.45, 0.7), glow=1.0):
    """RGBA planet sprite of radius R px (sprite is larger, for the atmosphere glow).
    kind: A = Earth-like with ice caps, B = same world with no ice and higher seas, moon, gas."""
    S = 2; r = R * S; pad = int(r * 0.32); N = 2 * (r + pad)
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    x = (x - N / 2) / r; y = (y - N / 2) / r
    rr = np.hypot(x, y)
    inside = rr < 1
    z = np.sqrt(np.clip(1 - rr * rr, 0, 1))
    lon = (np.arctan2(x, z) + rot) % (2 * math.pi)
    lat = np.arcsin(np.clip(y, -1, 1))
    TW, TH = 1024, 512
    u = (lon / (2 * math.pi) * (TW - 1)).astype(np.float32)
    v = ((lat / math.pi + 0.5) * (TH - 1)).astype(np.float32)
    samp = lambda t: cv2.remap(t, u, v, cv2.INTER_LINEAR)
    h = samp(_noise(TW, TH, seed))
    fine = samp(_noise(TW, TH, seed + 7, 7, 16))
    col = np.zeros((N, N, 3), np.float32)
    if kind in ("A", "B"):
        sea = 0.52 if kind == "A" else 0.60                       # higher seas in Timeline B
        d = np.clip((sea - h) / 0.25, 0, 1)[..., None]
        ocean = np.array([26, 96, 178], np.float32) * (1 - d) + np.array([6, 26, 88], np.float32) * d
        e = np.clip((h - sea) / 0.22, 0, 1)[..., None]
        land = np.array([46, 118, 64], np.float32) * (1 - e) + np.array([158, 136, 92], np.float32) * e
        land = land * (0.8 + 0.4 * fine[..., None])
        col = np.where((h > sea)[..., None], land, ocean)
        if kind == "A":
            ice = (np.abs(lat) + (fine - 0.5) * 0.3) > math.radians(52)
            col = np.where(ice[..., None], np.array([236, 244, 252], np.float32), col)
        cl = samp(_noise(TW, TH, seed + 31, 5, 14))
        ca = np.clip((cl - 0.58) / 0.16, 0, 1)[..., None] * 0.6
        col = col * (1 - ca) + 250 * ca
        rim, halo = np.array([90, 170, 255], np.float32), (np.array([70, 150, 255]) if kind == "A" else np.array([64, 240, 236]))
    elif kind == "moon":
        g = 105 + 80 * (h - 0.5) + 50 * (fine - 0.5)
        col = np.stack([g, g, g * 1.03], -1)
        rim, halo = np.array([0, 0, 0], np.float32), np.array([150, 160, 190])
    else:                                                          # banded gas giant
        b = samp(_noise(TW, TH, seed, 5, 2).mean(1, keepdims=True).repeat(TW, 1) * 0.6 + _noise(TW, TH, seed + 3, 6, 8) * 0.12)
        b = (b - b.min()) / (b.max() - b.min() + 1e-9)
        c1, c2 = np.array([214, 176, 132], np.float32), np.array([120, 84, 70], np.float32)
        col = c1 * b[..., None] + c2 * (1 - b[..., None])
        rim, halo = np.array([255, 200, 150], np.float32), np.array([255, 190, 140])
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    lam = np.clip(x * L[0] + y * L[1] + z * L[2], 0, 1)
    lit = 0.035 + 0.965 * lam ** 0.8
    col = col * lit[..., None]
    col += rim * ((1 - z) ** 2.6 * lam)[..., None] * 0.9          # atmosphere on the lit limb
    img = np.zeros((N, N, 4), np.float32)
    img[..., :3] = np.clip(col, 0, 255)
    edge = np.clip((1 - rr) * r / 1.5, 0, 1)
    img[..., 3] = edge * 255
    # outer glow, stronger on the lit side
    side = np.clip((x * L[0] + y * L[1]) / np.maximum(rr, 1e-6) * 0.6 + 0.55, 0, 1)
    g = np.clip(1 - (rr - 1) / 0.26, 0, 1) ** 3 * (rr >= 1) * side * 0.75 * glow
    out = img.copy()
    out[..., :3] = np.where(inside[..., None], img[..., :3], halo.astype(np.float32))
    out[..., 3] = np.where(inside, img[..., 3], g * 255)
    out = cv2.resize(out, (N // S, N // S), interpolation=cv2.INTER_AREA)
    return np.clip(out, 0, 255).astype(np.uint8)


def rings(fr, cx, cy, R, tilt=0.32, deg=-18, col=(220, 190, 150)):
    """Planet rings: call back half before the planet, front half after."""
    def half(front):
        lay = fr.copy()
        for k, a in ((1.55, 0.55), (1.75, 0.8), (1.98, 0.5), (2.18, 0.3)):
            cv2.ellipse(lay, (int(cx), int(cy)), (int(R * k), int(R * k * tilt)), deg, 0 if front else 180, 180 if front else 360,
                        tuple(int(c * a) for c in col), max(2, int(R * 0.07)), cv2.LINE_AA)
        cv2.addWeighted(lay, 0.8, fr, 0.2, 0, dst=fr)
    return half


@lru_cache(8)
def space_bg(W, H, seed=4):
    """Near-black space: soft blue/violet nebula, dense star field, vignette."""
    rng = np.random.default_rng(seed)
    n1 = cv2.resize(_noise(256, 128, seed, 5, 2), (W, H), interpolation=cv2.INTER_CUBIC)
    n2 = cv2.resize(_noise(256, 128, seed + 9, 5, 2), (W, H), interpolation=cv2.INTER_CUBIC)
    im = np.zeros((H, W, 3), np.float32)
    im += np.array([3, 4, 12], np.float32)
    im += np.clip(n1 - 0.48, 0, 1)[..., None] ** 1.5 * np.array([40, 60, 190], np.float32) * 1.3
    im += np.clip(n2 - 0.52, 0, 1)[..., None] ** 1.5 * np.array([120, 40, 170], np.float32) * 1.2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = np.clip(1.15 - np.hypot((xx / W - 0.5) * 1.1, (yy / H - 0.5) * 1.3), 0.25, 1)
    im *= vig[..., None]
    out = np.clip(im, 0, 255).astype(np.uint8)
    u = max(1.0, W / 1640)
    glow = np.zeros_like(out)
    for _ in range(int(W * H / 1500)):
        px, py = int(rng.integers(0, W)), int(rng.integers(0, H))
        b = rng.random() ** 3.2
        c = int(70 + 185 * b)
        tint = (c, c, min(255, int(c * 1.08))) if rng.random() < 0.7 else (min(255, int(c * 1.05)), int(c * 0.92), int(c * 0.85))
        if b > 0.55:
            cv2.circle(out, (px, py), max(1, int(1.5 * u)), tint, -1, cv2.LINE_AA)
            if b > 0.8:
                cv2.circle(glow, (px, py), int(5 * u), (70, 80, 130), -1, cv2.LINE_AA)
        else:
            out[py, px] = np.maximum(out[py, px], tint)
    out = cv2.add(out, cv2.GaussianBlur(glow, (0, 0), 4 * u))
    return out
