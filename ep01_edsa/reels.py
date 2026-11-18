"""Vertical Reels (1080x1920) for the EDSA episode. Each Reel has its own short narration.
Usage: reels.py voice A|B · reels.py stills A out.jpg T1 T2 ... · reels.py render A out.mp4"""
import json
from render import *          # noqa
import render as E

VW, VH = 1080, 1920
VOICE, SPEED = ("am_puck", "am_puck", "am_michael"), 1.08
REELS = {
 "A": dict(title="WHY ONLY ONE LANE?", src="Sources: DoTr and MRT-3 ridership (2025) · NACTO lane capacities", S=[
  ("a1", "On EDSA, one lane of buses carries about 180,000 people a day.", 0.25, "On Edsa, one lane of buses carries about a hundred eighty thousand people a day."),
  ("a2", "The train above it? About 388,000.", 0.3, "The train above it? About three hundred eighty-eight thousand."),
  ("a3", "By street-planning guidelines, a lane of cars moves 600 to 1,600 people an hour.", 0.2,
   "By street-planning guidelines, a lane of cars moves six hundred to sixteen hundred people an hour."),
  ("a4", "A bus lane: 4,000 to 8,000.", 0.35, "A bus lane: four thousand to eight thousand."),
  ("a5", "So why do buses get one lane, and everything else about four?", 0.4, None),
  ("a6", "In Timeline B, we redesigned it.", 0.2, None),
  ("a7", "Full video on our page.", 1.6, None)]),
 "B": dict(title="EDSA, REDESIGNED", src="One possible design, not an official plan · NACTO capacities, our arithmetic", S=[
  ("b1", "What if EDSA was redesigned from scratch?", 0.3, "What if Edsa was redesigned from scratch?"),
  ("b2", "Two bus lanes each way, so express buses can pass.", 0.25, None),
  ("b3", "A protected bikeway.", 0.25, None),
  ("b4", "A wider sidewalk, with trees.", 0.25, None),
  ("b5", "And cars go from about four lanes to two.", 0.35, None),
  ("b6", "By planning guidelines, one direction could carry 9,000 to 19,000 people an hour, up from 6,000 to 14,000 today.", 0.3,
   "By planning guidelines, one direction could carry nine thousand to nineteen thousand people an hour, up from six thousand to fourteen thousand today."),
  ("b7", "The catch? Drivers lose half their lanes. It's one possible design, not an official plan.", 0.35, None),
  ("b8", "Would you take that trade? Full video on our page.", 1.6, None)]),
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

    def panel(s, V, T, y=820, **kw):
        Lf = city_bg().copy()
        xsec(Lf, T, **kw)
        crop = Lf[396:940, 925:1895]
        p = cv2.resize(crop, (VW, int(crop.shape[0] * VW / crop.shape[1])), interpolation=cv2.INTER_AREA)
        V[y:y + p.shape[0]] = p
        cv2.line(V, (0, y), (VW, y), EDGE, 4); cv2.line(V, (0, y + p.shape[0]), (VW, y + p.shape[0]), EDGE, 4)
        return y + p.shape[0]

    def frame(s, T):
        V = s.bg.copy()
        (fa if s.r == "A" else fb)(s, V, T)
        tl.wordmark(V, VW / 2, 150, 62, eyes=False, tilt=0)
        put(V, tl.pill(REELS[s.r]["title"], CY, INK, 34, 0), VW / 2, 262)
        s.caption(V, T)
        put(V, text(REELS[s.r]["src"], "mono", 20, GR), VW / 2, 1640, 0.9)
        put(V, text("AI voice · simplified illustration · one direction shown", "mono", 20, GR), VW / 2, 1674, 0.9)
        if T > s.total - 0.5:
            V = (V * clamp((s.total - T) / 0.5)).astype(np.uint8)
        return V


def hd(V, s_, y, size, col, t, t0, t1=1e9):
    a = eo(seg(t, t0, 0.3)) * (1 - seg(t, t1 - 0.2, 0.2))
    if a > 0:
        head(V, s_, y, size, col, a, 0.85 + 0.15 * back(seg(t, t0, 0.4)), x=VW / 2)


def vbar(V, y, lo, hi, vmax, col, k, label, val, a=1.0):
    x0, x1 = 90, 990
    px = lambda v: x0 + (x1 - x0) * v / vmax
    put(V, text(label, "bold", 30, WH), x0, y - 44, a, anchor="l")
    put(V, text(val, "head", 40, col), x1, y - 46, a * eo(k), anchor="r")
    tl.rrect(V, x0, y - 6, x1, y + 6, 6, PANEL2, a)
    if k > 0:
        tl.rrect(V, px(lo), y - 20, px(lo + (hi - lo) * eio(k)), y + 20, 12, col, a)


def fa(s, V, T):
    c = s.c
    hb = eo(seg(T, c("a1") + 0.3, 0.4)) * (1 - seg(T, c("a3") - 0.2, 0.3))
    hm = eo(seg(T, c("a2") + 0.2, 0.4)) * (1 - seg(T, c("a3") - 0.2, 0.3))
    hc = eo(seg(T, c("a5") + 0.8, 0.4)) * (1 - seg(T, c("a6") - 0.1, 0.3))
    k = eio(seg(T, c("a6") + 0.3, 1.3))
    s.panel(V, T, kj=k, kk=k, kl=k, hi_bus=hb, hi_mrt=hm, hi_car=hc)
    hd(V, "ONE BUS LANE", 430, 92, AM, T, c("a1") + 0.1, c("a3"))
    hd(V, "180,000 A DAY", 550, 92, WH, T, c("a1") + 2.0, c("a3"))
    hd(V, "MRT-3: 388,000 A DAY", 680, 62, CY, T, c("a2") + 0.9, c("a3"))
    a = eo(seg(T, c("a3") + 0.1, 0.3)) * (1 - seg(T, c("a5") - 0.2, 0.2))
    if a > 0:
        head(V, "PEOPLE PER LANE,", 400, 64, WH, a, x=VW / 2); head(V, "PER HOUR", 478, 64, WH, a, x=VW / 2)
        vbar(V, 620, 600, 1600, 8000, mix(GR, WH, 0.4), seg(T, c("a3") + 3.0, 0.7), "ONE LANE OF CARS", "600–1,600", a)
        vbar(V, 750, 4000, 8000, 8000, AM, seg(T, c("a4") + 0.7, 0.7), "ONE BUS LANE", "4,000–8,000", a)
    hd(V, "SO WHY ONLY", 470, 100, AM, T, c("a5") + 0.1, c("a6")); hd(V, "ONE LANE?", 596, 100, AM, T, c("a5") + 0.3, c("a6"))
    hd(V, "IN TIMELINE B,", 440, 78, WH, T, c("a6") + 0.1); hd(V, "WE REDESIGNED IT", 548, 78, CY, T, c("a6") + 0.3)
    e = eo(seg(T, c("a7"), 0.4))
    put(V, tl.pill("FULL VIDEO ON OUR PAGE", AM, INK, 40, 0), VW / 2, 700, e, 0.8 + 0.2 * back(seg(T, c("a7"), 0.45)))


def fb(s, V, T):
    c = s.c
    kj, kk, kl = eio(seg(T, c("b2") + 0.3, 0.8)), eio(seg(T, c("b3") + 0.2, 0.8)), eio(seg(T, c("b4") + 0.2, 0.8))
    hc = eo(seg(T, c("b5") + 0.8, 0.4)) * (1 - seg(T, c("b6") - 0.1, 0.3))
    s.panel(V, T, kj=kj, kk=kk, kl=kl, hi_car=hc)
    hd(V, "WHAT IF EDSA WAS", 440, 78, WH, T, c("b1") + 0.1, c("b2")); hd(V, "REDESIGNED", 556, 110, AM, T, c("b1") + 0.3, c("b2"))
    hd(V, "FROM SCRATCH?", 676, 78, WH, T, c("b1") + 0.5, c("b2"))
    for a_, b_, t1, t2, col in (("b2", "b3", "2 BUS LANES", "EACH WAY", AM), ("b3", "b4", "PROTECTED", "BIKEWAY", BIKEC),
                                ("b4", "b5", "WIDER SIDEWALK", "+ TREES", (214, 208, 236)), ("b5", "b6", "CARS: FROM", "4 LANES TO 2", WH)):
        hd(V, t1, 470, 96, col, T, c(a_) + 0.1, c(b_)); hd(V, t2, 596, 96, col, T, c(a_) + 0.25, c(b_))
    a = eo(seg(T, c("b6") + 0.1, 0.3)) * (1 - seg(T, c("b7") - 0.2, 0.2))
    if a > 0:
        head(V, "PEOPLE PER HOUR,", 400, 64, WH, a, x=VW / 2); head(V, "ONE DIRECTION", 478, 64, WH, a, x=VW / 2)
        vbar(V, 620, 9200, 19200, 20000, CY, seg(T, c("b6") + 2.6, 0.8), "TIMELINE B LAYOUT", "9,200–19,200", a)
        vbar(V, 750, 6400, 14400, 20000, mix(GR, WH, 0.4), seg(T, c("b6") + s.cd("b6") * 0.72, 0.8), "TODAY", "6,400–14,400", a)
    hd(V, "THE CATCH:", 390, 70, RED, T, c("b7") + 0.1, c("b8")); hd(V, "DRIVERS LOSE", 490, 86, WH, T, c("b7") + 1.0, c("b8"))
    hd(V, "HALF THEIR LANES", 590, 86, WH, T, c("b7") + 1.2, c("b8"))
    if c("b7") + 3.0 <= T < c("b8"):
        stamp(V, "ONE POSSIBLE DESIGN", VW / 2, 730, T, c("b7") + s.cd("b7") * 0.6, 0.46)
    hd(V, "WOULD YOU TAKE", 450, 84, WH, T, c("b8") + 0.1); hd(V, "THAT TRADE?", 560, 100, AM, T, c("b8") + 0.3)
    e = seg(T, c("b8") + s.cd("b8") * 0.55, 0.4)
    put(V, tl.pill("FULL VIDEO ON OUR PAGE", AM, INK, 40, 0), VW / 2, 710, eo(e), 0.8 + 0.2 * back(e))


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
