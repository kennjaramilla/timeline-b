"""Upbeat original music + sound effects + narration mix for the Timeline B sample. Output: mix.wav (48 kHz stereo)."""
import json, math
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly

SR = 48000
J = json.load(open("timeline.json")); L, TOTAL = J["lines"], J["total"]
N = int(TOTAL * SR)
rng = np.random.default_rng(7)
C = {x["key"]: x for x in L}
ST = {}
for x in L:
    ST.setdefault(x["scene"], 0.0 if not ST else x["t"] - 0.28)
ct = lambda k: C[k]["t"]
cd = lambda k: C[k]["d"]


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def add(buf, sig, t, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0:
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig), 0] += sig * g * (1 - max(0, pan))
    buf[i:i + len(sig), 1] += sig * g * (1 + min(0, pan))


# ---------------- music: 112 bpm, bright F-major loop (F  C  Dm  Bb), drums, bass, plucks
BPM = 100.0
BEAT = 60 / BPM
BAR = 4 * BEAT
CH = [[53, 57, 60, 65], [48, 55, 60, 64], [50, 57, 62, 65], [46, 53, 58, 62]]
mus = np.zeros((N, 2))


def kick():
    t = np.arange(int(0.26 * SR)) / SR
    return np.sin(2 * np.pi * (46 + 110 * np.exp(-t * 34)) * t) * np.exp(-t * 13)


def snare():
    t = np.arange(int(0.2 * SR)) / SR
    return hp(rng.standard_normal(len(t)), 1400) * np.exp(-t * 24) * 0.7 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5


def hat(d=0.05):
    t = np.arange(int(d * SR)) / SR
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / d * 5)


def clap():
    t = np.arange(int(0.18 * SR)) / SR
    e = sum(np.exp(-np.maximum(t - o, 0) * 40) * (t >= o) for o in (0, 0.011, 0.023))
    return sosfilt(butter(2, [900, 3200], "band", fs=SR, output="sos"), rng.standard_normal(len(t))) * e * 0.5


def pluck(m, d=0.34):
    t = np.arange(int(d * SR)) / SR
    f = midi(m)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.35 + np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t)
    return lp(x, 3200) * np.exp(-t * 9) * np.minimum(t / 0.003, 1)


def bass(m, d):
    t = np.arange(int(d * SR)) / SR
    f = midi(m)
    return lp(np.sin(2 * np.pi * f * t) + 0.5 * np.sign(np.sin(2 * np.pi * f * t)), 420) * np.minimum(t / 0.005, 1) * np.exp(-t * 3.5)


K, SN, HH, CL = kick(), snare(), hat(), clap()
nb = int(math.ceil(TOTAL / BAR))
calm0, calm1 = ST["real"], ST["real"] + (ct("p") - ST["real"])        # the "now breathe" stretch: drums drop out
for b in range(nb):
    t0 = b * BAR
    ch = CH[b % 4]
    calm = calm0 - 0.3 <= t0 < calm1 - BAR * 0.5
    intro = b < 2
    # pad
    n = int((BAR + 0.5) * SR); t = np.arange(n) / SR
    env = np.minimum(t / 0.25, 1) * np.minimum((BAR + 0.5 - t) / 0.5, 1)
    pad = sum(np.sin(2 * np.pi * midi(m + 12) * t * (1 + d)) for m in ch for d in (-0.002, 0.002))
    add(mus, lp(pad, 2000) * env, t0, 0.022)
    for q in range(8):                       # eighth notes
        te = t0 + q * BEAT / 2
        root = ch[0] - 12
        if not calm:
            add(mus, bass(root + (12 if q in (3, 6) else 0), BEAT * 0.48), te, 0.20)
        elif q == 0:
            add(mus, bass(root, BAR * 0.9), te, 0.18)
        arp = [ch[1], ch[2], ch[3], ch[2] + 12, ch[3], ch[2], ch[1] + 12, ch[2]][q] + 12
        add(mus, pluck(arp), te, 0.085 if not calm else 0.06, 0.45 if q % 2 else -0.45)
        if not calm and not intro:
            add(mus, HH, te, 0.05 if q % 2 == 0 else 0.09)
    if not calm:
        for q in range(4):
            if not intro or q == 0:
                add(mus, K, t0 + q * BEAT, 0.30 if q % 2 == 0 else 0.16)
            if q in (1, 3) and not intro:
                add(mus, SN, t0 + q * BEAT, 0.10)
        if not intro and b % 4 == 3:          # little fill
            for o in (3.5, 3.75):
                add(mus, SN, t0 + o * BEAT, 0.06)
    # melody hook every other bar
    if not calm and b % 2 == 0 and b >= 2:
        for o, m in ((0, ch[3] + 24), (0.75, ch[2] + 24), (1.5, ch[3] + 24), (2.5, ch[1] + 24)):
            tt = np.arange(int(0.5 * SR)) / SR
            bell = (np.sin(2 * np.pi * midi(m) * tt) + 0.3 * np.sin(2 * np.pi * midi(m) * 3 * tt)) * np.exp(-tt * 7) * np.minimum(tt / 0.003, 1)
            add(mus, bell, t0 + o * BEAT, 0.045)


# ---------------- sound effects
def whoosh(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n + 2048); out = np.zeros(n)
    for i in range(0, n, 2048):
        fc = 600 + 5200 * math.sin(math.pi * (i / n)) ** 2
        y = sosfilt(butter(2, [fc * 0.6, fc * 1.5], "band", fs=SR, output="sos"), x[i:i + 2560])[:2048]
        out[i:min(n, i + 2048)] = y[: min(2048, n - i)]
    return out * np.sin(math.pi * t / d) ** 2


def pop(f=880):
    t = np.arange(int(0.16 * SR)) / SR
    return np.sin(2 * np.pi * f * t * (1 + 0.5 * np.exp(-t * 60))) * np.exp(-t * 34)


def boing():
    t = np.arange(int(0.42 * SR)) / SR
    f = 260 + 240 * np.exp(-t * 7) * np.abs(np.sin(2 * np.pi * 7 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def sparkle():
    out = np.zeros(int(0.9 * SR))
    for i, m in enumerate((84, 88, 91, 96, 100)):
        t = np.arange(int(0.5 * SR)) / SR
        s = np.sin(2 * np.pi * midi(m) * t) * np.exp(-t * 9)
        j = int(i * 0.06 * SR); out[j:j + len(s)] += s[: len(out) - j]
    return out


def boom():
    t = np.arange(int(1.2 * SR)) / SR
    return np.sin(2 * np.pi * (40 + 80 * np.exp(-t * 14)) * t) * np.exp(-t * 3.6) + lp(rng.standard_normal(len(t)), 300) * np.exp(-t * 9) * 0.5


def rush(d):
    n = int(d * SR); t = np.arange(n) / SR
    x = hp(lp(rng.standard_normal(n), 1800), 180)
    return x * np.sin(math.pi * np.clip(t / d, 0, 1)) ** 1.2


def thud():
    t = np.arange(int(0.5 * SR)) / SR
    return np.sin(2 * np.pi * (60 + 90 * np.exp(-t * 40)) * t) * np.exp(-t * 11) + lp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 40) * 0.6


fx = np.zeros((N, 2))
for name, s0 in ST.items():
    if s0 > 0:
        add(fx, whoosh(), s0 - 0.24, 0.5)
add(fx, pop(660), ct("a") + 0.9, 0.35)
add(fx, whoosh(0.8), ct("b") - 0.1, 0.45)
add(fx, boom(), ct("c") + 0.75, 0.5); add(fx, sparkle(), ct("c") + 1.0, 0.16)
add(fx, rush(2.6), ct("e") + 0.5, 0.09); add(fx, pop(520), ct("e") + cd("e") - 1.4, 0.32)
add(fx, rush(2.2), ct("f") + 0.25, 0.13); add(fx, sparkle(), ct("f") + 1.6, 0.13)
add(fx, pop(700), ct("g") + 1.4, 0.3); add(fx, rush(1.3), ct("g") + 1.5, 0.08)
add(fx, pop(780), ct("h") + 0.15, 0.3); add(fx, rush(1.2), ct("h") + 0.25, 0.11)
add(fx, pop(880), ct("ij") + 0.4, 0.3)
add(fx, boom(), ct("ij") + cd("ij") - 1.25, 0.5); add(fx, sparkle(), ct("ij") + cd("ij") - 1.15, 0.2)
add(fx, rush(2.0), ST["city"] + 0.35, 0.2)
for k, m in enumerate(("m1", "m2", "m3", "m4")):
    add(fx, pop(620 + 110 * k), ct(m) - 0.04, 0.34, (-0.4, -0.15, 0.15, 0.4)[k])
add(fx, thud(), ct("n") + cd("n") - 1.15, 0.6)
add(fx, sparkle(), ct("o") + cd("o") - 0.6, 0.12)
add(fx, rush(2.0), ct("p") + 0.3, 0.10); add(fx, pop(700), ct("q") + 0.2, 0.3)
add(fx, whoosh(0.9), ST["outro"] + 0.3, 0.35); add(fx, sparkle(), ST["outro"] + 0.55, 0.18)
add(fx, pop(880), ct("s"), 0.3)

# ---------------- narration + mix (music ducks under the voice)
vo, sr = sf.read("vo.wav")
vo = resample_poly(vo, SR, sr)
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
vo = hp(vo, 70)
envv = lp(np.abs(vo), 6)
duck = 1 - 0.5 * np.clip(envv / 0.08, 0, 1)
t = np.arange(N) / SR
fade = np.clip(t / 0.4, 0, 1) * np.clip((TOTAL - t) / 2.0, 0, 1)
mus /= np.abs(mus).max() + 1e-9
mix = mus * 0.30 * (duck * fade)[:, None] + fx * 0.5 * np.clip((TOTAL - t) / 0.8, 0, 1)[:, None] + vo[:, None] * 1.0
pk = np.abs(mix).max()
mix = np.tanh(mix / pk * 1.3) / np.tanh(1.3) * 0.93
sf.write("mix.wav", mix, SR, subtype="PCM_16")
r = lambda x: float(np.sqrt((x ** 2).mean()))
print("mix ok", round(TOTAL, 2), "music-under-voice rms", round(r(mus * 0.36 * 0.5), 4), "voice rms", round(r(vo[np.abs(vo) > 0.02]), 4))
