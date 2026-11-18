"""Vertical Reels (1080x1920) for the Moon episode. They reuse the vis_*() pictures from render.py.
Usage: reels.py voice A|B · reels.py stills A out.jpg T1 T2 ... · reels.py render A out.mp4"""
import json
from render import *          # noqa
import render as E

VW, VH = 1080, 1920
VOICE, SPEED = ("am_puck", "am_puck", "am_michael"), 1.08
REELS = {
 "A": dict(title="DAY ONE WITHOUT THE MOON", src="Sources: EarthSky (brightness) · NOAA (tides); one-third is our arithmetic", S=[
  ("a1", "Delete the Moon. No explosion. It's just gone.", 0.3, None),
  ("a2", "The first thing you notice is the dark.", 0.25, None),
  ("a3", "A full Moon is more than 1,600 times brighter than Venus, the next brightest thing in the night sky.", 0.3,
   "A full Moon is more than sixteen hundred times brighter than Venus, the next brightest thing in the night sky."),
  ("a4", "Then the sea changes. With only the Sun pulling, tides shrink to roughly a third.", 0.35, None),
  ("a5", "And that's just day one.", 0.2, None),
  ("a6", "Full video on our page.", 1.6, None)]),
 "B": dict(title="THE MOON AND OUR SEASONS", src="Sources: Laskar et al. (1993) · Lissauer et al. (2012) · swings sped up", S=[
  ("b1", "Earth leans at about 23 degrees. That lean gives us seasons.", 0.3, "Earth leans at about twenty-three degrees. That lean gives us seasons."),
  ("b2", "The Moon keeps it steady, between about 22 and 24 and a half degrees.", 0.3,
   "The Moon keeps it steady, between about twenty-two and twenty-four and a half degrees."),
  ("b3", "Without it? A 1993 study said the tilt could swing from zero to 85 degrees.", 0.3,
   "Without it? A nineteen ninety-three study said the tilt could swing from zero to eighty-five degrees."),
  ("b4", "A 2012 study said maybe only about ten degrees more.", 0.35, "A twenty twelve study said maybe only about ten degrees more."),
  ("b5", "So what really happens if the Moon disappears?", 0.2, None),
  ("b6", "Full video on our page.", 1.6, None)]),
}


def rdir(r):
    d = os.path.join(E.HERE, "reel" + r); os.makedirs(d, exist_ok=True); return d


def voice(r):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    tts = os.path.join(E.HERE, "..", "tts")
    k = Kokoro(os.path.join(tts, "kokoro-v1.0.onnx"), os.path.join(tts, "voices-v1.0.bin"))
    VS = sum(k.get_voice_style(v) for v in VOICE) / len(VOICE)
    SR, t = 24000, 0.35
    out, tlj = [np.zeros(int(t * SR), np.float32)], []
    for n, (key, txt, pause, say) in enumerate(REELS[r]["S"]):
        a, _ = k.create(say or txt, voice=VS, speed=SPEED, lang="en-us")
        a = np.asarray(a, np.float32); nz = np.where(np.abs(a) > 0.012)[0]
        a = a[max(0, nz[0] - 500): nz[-1] + 1300]
        a[:240] *= np.linspace(0, 1, 240); a[-600:] *= np.linspace(1, 0, 600)
        a = a / (np.abs(a).max() + 1e-9) * 0.85
        d = len(a) / SR
        tlj.append(dict(scene="reel", key=key, grp=n, text=txt, t=round(t, 3), d=round(d, 3)))
        out += [a, np.zeros(int(pause * SR), np.float32)]; t += d + pause
    sf.write(os.path.join(rdir(r), "vo.wav"), np.concatenate(out), SR)
    json.dump(dict(lines=tlj, total=round(t, 3)), open(os.path.join(rdir(r), "timeline.json"), "w"), indent=1)
    print(r, "total", round(t, 2), [(x["key"], x["t"]) for x in tlj])


class Reel:
    def __init__(s, r):
        s.r = r
        J = json.load(open(os.path.join(rdir(r), "timeline.json")))
        s.L, s.total = J["lines"], J["total"]
        s.C = {x["key"]: x for x in s.L}
        s.nf = int(round(s.total * FPS))
        s.caps = []
        for x in s.L:
            words = x["text"].split(" "); lines, cur = [], []
            kq = math.ceil(len(x["text"]) / 27); tgt = len(x["text"]) / kq
            for w in words:
                if cur and len(" ".join(cur + [w])) > tgt + 3 and kq > 1:
                    lines.append(cur); cur = [w]; kq -= 1
                else:
                    cur.append(w)
            lines.append(cur)
            tot = sum(len(w) + 1 for w in words); t = x["t"]
            for ln in lines:
                ws = []
                for w in ln:
                    dw = x["d"] * (len(w) + 1) / tot; ws.append((w, t, t + dw)); t += dw
                s.caps.append((ws[0][1], ws[-1][2], ws))
        s.bg = space.space_bg(VW, VH, 5)

    def c(s, k):
        return s.C[k]["t"]

    def cd(s, k):
        return s.C[k]["d"]

    def caption(s, V, T):
        for a, b, words in s.caps:
            if a - 0.04 <= T < b + 0.12:
                sz = 60
                while True:
                    sprs = [text(w, "bold", sz, WH) for w, _, _ in words]
                    gap = int(sz / 3)
                    tw = sum(sp.shape[1] - 16 for sp in sprs) + gap * (len(sprs) - 1)
                    if tw <= 940 or sz <= 40:
                        break
                    sz -= 4
                tl.rrect(V, VW / 2 - tw / 2 - 36, 1476, VW / 2 + tw / 2 + 36, 1586, 34, INK, 0.88)
                x = VW / 2 - tw / 2
                for (w, w0, w1), sp in zip(words, sprs):
                    ww = sp.shape[1] - 16
                    put(V, text(w, "bold", sz, AM) if w0 <= T < w1 else sp, x + ww / 2, 1529, 1.0 if T >= w0 else 0.72)
                    x += ww + gap
                return

    def panel(s, V, draw, y=820):
        """draw(L) paints a landscape picture; its centre box is cropped into the Reel."""
        Lf = E.SKY.copy()
        draw(Lf)
        V[y:y + 600] = Lf[310:910, 420:1500]
        cv2.line(V, (0, y), (VW, y), EDGE, 4); cv2.line(V, (0, y + 600), (VW, y + 600), EDGE, 4)

    def frame(s, T):
        V = s.bg.copy()
        (fa if s.r == "A" else fb)(s, V, T)
        tl.wordmark(V, VW / 2, 150, 62, eyes=False, tilt=0)
        put(V, tl.pill(REELS[s.r]["title"], CY, INK, 34, 0), VW / 2, 262)
        s.caption(V, T)
        put(V, text(REELS[s.r]["src"], "mono", 20, GR), VW / 2, 1640, 0.9)
        put(V, text("AI voice · illustration, not to scale", "mono", 20, GR), VW / 2, 1674, 0.9)
        if T > s.total - 0.5:
            V = (V * clamp((s.total - T) / 0.5)).astype(np.uint8)
        return V


def hd(V, s_, y, size, col, t, t0, t1=1e9):
    a = eo(seg(t, t0, 0.3)) * (1 - seg(t, t1 - 0.2, 0.2))
    if a > 0:
        head(V, s_, y, size, col, a, 0.85 + 0.15 * back(seg(t, t0, 0.4)), x=VW / 2)


def cta(V, T, t0, y=700):
    e = seg(T, t0, 0.4)
    put(V, tl.pill("FULL VIDEO ON OUR PAGE", AM, INK, 40, 0), VW / 2, y, eo(e), 0.8 + 0.2 * back(e))


def fa(s, V, T):
    c = s.c
    if T < c("a2"):
        s.panel(V, lambda L: vis_pair(L, T, gone=eio(seg(T, c("a1") + 0.9, 0.7))))
    elif T < c("a4"):
        s.panel(V, lambda L: vis_night(L, T, eio(seg(T, c("a2") + 0.2, 1.4))))
    else:
        s.panel(V, lambda L: vis_tide(L, T, eio(seg(T, c("a4") + 2.0, 2.0))))
    hd(V, "DELETE", 450, 120, WH, T, c("a1") + 0.1, c("a2")); hd(V, "THE MOON", 590, 120, AM, T, c("a1") + 0.3, c("a2"))
    hd(V, "FIRST:", 420, 76, WH, T, c("a2") + 0.1, c("a3")); hd(V, "THE DARK", 540, 124, AM, T, c("a2") + 0.5, c("a3"))
    hd(V, "A FULL MOON IS", 410, 70, WH, T, c("a3") + 0.1, c("a4")); hd(V, "1,600×", 540, 150, AM, T, c("a3") + 1.6, c("a4"))
    hd(V, "BRIGHTER THAN VENUS", 670, 66, WH, T, c("a3") + 2.6, c("a4"))
    hd(V, "THEN THE TIDES", 420, 80, WH, T, c("a4") + 0.1, c("a5")); hd(V, "SHRINK TO", 530, 80, WH, T, c("a4") + 2.2, c("a5"))
    hd(V, "ABOUT A THIRD", 646, 104, AM, T, c("a4") + 2.6, c("a5"))
    hd(V, "AND THAT'S", 440, 90, WH, T, c("a5") + 0.1); hd(V, "JUST DAY ONE", 560, 104, AM, T, c("a5") + 0.3)
    cta(V, T, c("a6"))


def fb(s, V, T):
    c = s.c
    if T < c("b3") - 0.1:
        s.panel(V, lambda L: vis_tilt(L, T, 0))
    else:
        s.panel(V, lambda L: vis_tilt(L, T, 1, k2=eo(seg(T, c("b4") + 0.3, 0.6))))
    hd(V, "EARTH LEANS", 430, 96, WH, T, c("b1") + 0.1, c("b2")); hd(V, "ABOUT 23°", 560, 130, AM, T, c("b1") + 0.9, c("b2"))
    hd(V, "THAT GIVES US SEASONS", 690, 58, WH, T, c("b1") + 2.6, c("b2"))
    hd(V, "THE MOON KEEPS", 430, 82, WH, T, c("b2") + 0.1, c("b3")); hd(V, "IT STEADY", 540, 110, CY, T, c("b2") + 0.4, c("b3"))
    hd(V, "22.1° TO 24.5°", 670, 76, WH, T, c("b2") + 1.8, c("b3"))
    hd(V, "WITHOUT IT?", 420, 96, WH, T, c("b3") + 0.1, c("b5")); hd(V, "1993: 0° TO 85°", 550, 92, AM, T, c("b3") + 1.4, c("b5"))
    hd(V, "2012: ABOUT 10° MORE", 676, 70, CY, T, c("b4") + 0.5, c("b5"))
    hd(V, "SO WHAT REALLY", 440, 86, WH, T, c("b5") + 0.1); hd(V, "HAPPENS?", 566, 120, AM, T, c("b5") + 0.3)
    cta(V, T, c("b6"))


if __name__ == "__main__":
    mode, r = sys.argv[1], sys.argv[2]
    if mode == "voice":
        voice(r)
    elif mode == "stills":
        R_ = Reel(r)
        ims = [cv2.resize(R_.frame(float(x)), (432, 768), interpolation=cv2.INTER_AREA) for x in sys.argv[4:]]
        Image.fromarray(np.hstack(ims)).save(sys.argv[3], quality=88)
    else:
        R_ = Reel(r); out = sys.argv[3]; tmp = out + ".tmp.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-g", "60", tmp],
                             stdin=subprocess.PIPE)
        for f in range(R_.nf):
            p.stdin.write(R_.frame(f / FPS).tobytes())
        p.stdin.close()
        if p.wait() == 0:
            os.replace(tmp, out); print("done", out, R_.total)
