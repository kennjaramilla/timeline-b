"""Timeline B, episode 1 (extended cut): What if EDSA was redesigned from scratch?
Adds a hook, a route map, a commuter to follow and two real-world examples on top of render.py.
Usage: render2.py stills out.jpg T1 T2 ... | render2.py part A B out.mp4"""
from render import *          # noqa: brings tl, space, R (base), xsec, head, pop, rangebar, stamp, vehicles ...
import render as E
from tl import PINK

# ------------------------------------------------------------------ route map (schematic)
MC, MR = (480, 540), 320
STN = [("Monumento", 0.0), ("North Avenue", 0.2), ("Cubao", 0.42), ("Ortigas", 0.55), ("Guadalupe", 0.7), ("Ayala", 0.8),
       ("Taft Avenue", 0.93)]


def mpt(f, off=0.0):
    th = math.radians(-125 + 245 * f); r = MR + off
    return (MC[0] + r * math.cos(th), MC[1] + r * 0.94 * math.sin(th))


def emap(fr, T, tb=0.0, draw=1.0, ana=None, a=1.0):
    pts = np.array([mpt(i / 90) for i in range(91)], np.float32)
    put(fr, text("MANILA", "mono", 30, DIM, track=8), MC[0] - 40, MC[1], a)
    tl.line(fr, tl.partial(pts, draw), (64, 66, 108), 34)
    if draw >= 1:
        m = np.array([mpt(0.2 + 0.73 * i / 60, 30) for i in range(61)], np.float32)
        tl.line(fr, m, mix(CY, (0, 0, 0), 0.25), 6)
        tl.line(fr, pts, mix(AM, (0, 0, 0), 0.2), 4 + int(5 * tb))
        n = int(64 - 30 * tb)
        for i in range(n):
            f = (i / n + T * (0.004 + 0.008 * tb) + 0.012 * math.sin(i * 3 + T * 0.5)) % 1
            x, y = mpt(f, (-11, 11)[i % 2])
            cv2.circle(fr, (int(x), int(y)), 5, CARS[i % 8], -1, cv2.LINE_AA)
        nb = int(7 + 7 * tb)
        for i in range(nb):
            f = (i / nb + T * (0.022 + 0.012 * tb) * (1.4 if tb > 0.5 and i % 2 else 1.0)) % 1
            x, y = mpt(f, 3 if i % 2 else -3)
            cv2.circle(fr, (int(x), int(y)), 9, WH, -1, cv2.LINE_AA); cv2.circle(fr, (int(x), int(y)), 6, AM, -1, cv2.LINE_AA)
        x, y = mpt(0.2 + 0.73 * (0.5 - 0.5 * math.cos(T * 0.45)), 30)
        cv2.circle(fr, (int(x), int(y)), 10, CY, -1, cv2.LINE_AA)
        for nm, f in STN:
            x, y = mpt(f)
            cv2.circle(fr, (int(x), int(y)), 9, INK, -1, cv2.LINE_AA); cv2.circle(fr, (int(x), int(y)), 9, WH, 3, cv2.LINE_AA)
            th = math.radians(-125 + 245 * f)
            lx, ly = mpt(f, 58)
            if math.cos(th) > 0.25:
                put(fr, text(nm, "bold", 24, WH), lx - 6, ly, a, anchor="l")
            else:
                put(fr, text(nm, "bold", 24, WH), lx + 20, ly + (-14 if math.sin(th) < 0 else 14), a)
        ex, ey = mpt(1.0)
        cv2.arrowedLine(fr, (int(ex), int(ey)), (int(ex - 70), int(ey + 34)), GR, 5, cv2.LINE_AA, tipLength=0.4)
        put(fr, text("to PITX", "mono", 24, GR), ex - 120, ey + 62, a)
        put(fr, text("MRT-3", "mono", 22, CY), mpt(0.36, 96)[0], mpt(0.36, 96)[1], a)
    if ana is not None:
        x, y = mpt(ana)
        cv2.circle(fr, (int(x), int(y)), 22, WH, -1, cv2.LINE_AA); cv2.circle(fr, (int(x), int(y)), 16, PINK, -1, cv2.LINE_AA)
        put(fr, tl.pill("ANA", PINK, WH, 22, 0), x, y - 46)


RX = 1400   # centre of the right-hand text column


def capacity_block(fr, t, tb, tc, y0=0):
    k = seg(t, tb + 0.2, 0.4)
    if k <= 0:
        return
    x0, x1, y, vmax = 1010, 1800, 420 + y0, 460000
    px = lambda v: x0 + (x1 - x0) * v / vmax
    p = eio(seg(t, tb + 0.5, 1.7))
    n = int(round(400000 * p / 1000) * 1000)
    head(fr, f"{n:,}" + ("+" if p >= 1 else ""), 232 + y0, 124, AM, eo(k), x=RX)
    put(fr, text("vehicles on EDSA every day", "semi", 40, WH), RX, 326 + y0, eo(k))
    tl.rrect(fr, x0, y - 22, x1, y + 22, 12, PANEL2, eo(k))
    v = 430000 * p
    tl.rrect(fr, x0, y - 22, px(min(v, 300000)) + 1, y + 22, 12, mix(AM, WH, 0.1))
    if v > 300000:
        tl.rrect(fr, px(300000), y - 22, px(v), y + 22, 12, RED)
    kc = eo(seg(t, tc + 0.3, 0.5))
    if kc > 0:
        tl.rrect(fr, px(250000), y - 34, px(300000), y + 34, 6, CY, 0.55 * kc)
        cv2.rectangle(fr, (int(px(250000)), y - 34), (int(px(300000)), y + 34), CY, 3, cv2.LINE_AA)
        put(fr, text("BUILT FOR 250,000–300,000", "bold", 26, CY), px(300000) + 6, y + 62, kc, anchor="r")
        put(fr, text("OVER CAPACITY", "bold", 26, RED), px(312000), y + 62, kc, anchor="l")
        put(fr, text("capacity per MMDA", "mono", 22, GR), RX, y + 104, kc)


def busway_inset(fr, T, x0, y0, x1, y1, a=1.0):
    """Top-down: a stopped bus at a station, an express bus overtaking in the second lane."""
    if a <= 0:
        return
    base = fr.copy()
    tl.rrect(fr, x0 - 6, y0 - 6, x1 + 6, y1 + 6, 22, EDGE)
    tl.rrect(fr, x0, y0, x1, y1, 18, PANEL)
    h = y1 - y0; ym = (y0 + y1) / 2
    tl.rrect(fr, x0 + 14, y0 + h * 0.26, x1 - 14, y1 - 16, 8, (60, 52, 44))
    tl.dashed(fr, x0 + 20, x1 - 20, y0 + h * 0.62, AM, 4, 30, 22, -T * 60)
    cx = (x0 + x1) / 2
    tl.rrect(fr, cx - 190, y0 + 12, cx + 190, y0 + h * 0.24, 8, (120, 124, 160))
    put(fr, text("STATION", "mono", 20, INK, track=3), cx, y0 + h * 0.13)
    bw, bh = 170, h * 0.24

    def tbus(x, y, col):
        tl.rrect(fr, x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2, 10, col)
        tl.rrect(fr, x + bw / 2 - 26, y - bh / 2 + 5, x + bw / 2 - 8, y + bh / 2 - 5, 4, (28, 40, 78))
        tl.rrect(fr, x - bw / 2 + 8, y - 3, x + bw / 2 - 34, y + 3, 2, BUSC)
    tbus(cx - 30, y0 + h * 0.44, (236, 240, 252))
    q = (T * 0.36) % 1
    tbus(lerp(x0 - bw, x1 + bw, q), y0 + h * 0.8, (255, 226, 150))
    m = np.zeros(fr.shape[:2], np.uint8)
    tl.rrect(m, x0 - 6, y0 - 6, x1 + 6, y1 + 6, 22, 255)
    mm = (m[..., None].astype(np.float32) / 255.0) * a
    fr[:] = (fr * mm + base * (1 - mm)).astype(np.uint8)


# ------------------------------------------------------------------ scenes
def sc_hook(fr, t, T):
    t1, t2, t3 = cl("h1", "hook"), cl("h2", "hook"), cl("h3", "hook")
    hb = eo(seg(t, t1 + 0.3, 0.5)) * (1 - seg(t, t3 + 0.3, 0.4))
    hc = eo(seg(t, t2 + 0.9, 0.5)) * (1 - seg(t, t3 + 0.3, 0.4))
    xsec(fr, T, hi_bus=hb, hi_car=hc, a=eo(seg(t, 0.2, 0.4)))
    a1 = 1 - seg(t, t2 - 0.2, 0.3)
    if a1 > 0:
        e, s = pop(t, t1 + 0.2)
        put(fr, tl.pill("ONE BUS LANE EACH WAY", AM, INK, 36, 0), CX, 170, e * a1, s)
        e, s = pop(t, t1 + 2.2)
        head(fr, "180,000 PEOPLE A DAY", 290, 96, WH, e * a1, s)
    a2 = eo(seg(t, t2 + 0.1, 0.3)) * (1 - seg(t, t3 + 0.3, 0.4))
    if a2 > 0:
        head(fr, "SO WHY ONLY ONE LANE?", 230, 100, AM, a2, 0.85 + 0.15 * back(seg(t, t2 + 0.1, 0.45)))
        put(fr, text("buses: 1 lane · everything else: about 4", "semi", 42, WH), CX, 330, a2 * eo(seg(t, t2 + 1.6, 0.4)))
    k = seg(t, t3 + 0.9, 0.5)
    if k > 0:
        cv2.addWeighted(fr, 1 - 0.82 * eo(k), np.zeros_like(fr), 0, 0, dst=fr)
        tl.fork(fr, (360, 800), 0, W, 110, 250, 9, kA=1.0, kB=eio(seg(t, t3 + 1.0, 1.0)), phase=-T * 40)
        tl.wordmark(fr, CX, 250, 96, eo(k), 0.8 + 0.2 * back(k), eyes=False, tilt=0)
        for i, ln in enumerate(("WHAT IF EDSA WAS", "REDESIGNED FROM SCRATCH?")):
            kk = seg(t, t3 + 1.2 + i * 0.2, 0.45)
            head(fr, ln, 440 + i * 116, 92, AM if i else WH, eo(kk), 0.85 + 0.15 * back(kk))


def sc_road(fr, t, T):
    ta, ta2, tb, tc = cl("a", "road"), cl("a2", "road"), cl("b", "road"), cl("c", "road")
    emap(fr, T, draw=eio(seg(t, 0.1, 1.6)))
    a1 = 1 - seg(t, tb - 0.25, 0.3)
    if a1 > 0:
        put(fr, tl.pill("TIMELINE A", GR, INK, 30, 0), RX, 150, eo(seg(t, 0.2, 0.4)) * a1)
        e, s = pop(t, ta + 0.6)
        head(fr, "EDSA", 262, 130, WH, e * a1, s, x=RX)
        put(fr, text("23.8 km · Caloocan to Pasay", "semi", 42, WH), RX, 362, eo(seg(t, ta + 2.2, 0.4)) * a1)
        d = cdur("a2")
        for i, (fr_, lab, c) in enumerate(((0.06, "1940 · Circumferential Road", GR), (0.46, "1950s · Highway 54", GR),
                                           (0.62, "1959 · Epifanio de los Santos Avenue", AM))):
            e, s = pop(t, ta2 + d * fr_)
            put(fr, tl.pill(lab, c, INK, 30, 0, "bold"), RX, 470 + i * 78, e * a1, s)
    capacity_block(fr, t, tb, tc)


def sc_ana(fr, t, T):
    td, td2, td3 = cl("d", "ana"), cl("d2", "ana"), cl("d3", "ana")
    f = 0.3 * eio(seg(t, td2 + 0.3, cdur("d2") + 2.0)) + 0.7 * eio(seg(t, td3 + 3.2, 3.6))
    emap(fr, T, ana=f, tb=0.0)
    e, s = pop(t, td + 0.2)
    put(fr, tl.pill("MEET ANA", PINK, WH, 34, 0), RX, 150, e, s)
    head(fr, "MONUMENTO TO PITX", 240, 58, WH, eo(seg(t, td + 2.6, 0.4)), x=RX)
    put(fr, text("an illustrative commuter, every morning", "mono", 24, GR), RX, 296, eo(seg(t, td + 2.9, 0.4)))
    x0, full = 1010, 780
    k = seg(t, td2 + 2.6, 0.4)
    if k > 0:
        put(fr, text("BEFORE 2020", "bold", 28, WH), x0, 384, eo(k), anchor="l")
        tl.rrect(fr, x0, 410, x0 + full * eio(seg(t, td2 + 2.8, 1.6)), 462, 14, RED, eo(k))
        put(fr, text("up to 3 hours", "head", 44, WH), x0, 506, eo(seg(t, td2 + 4.2, 0.4)), anchor="l")
    k = seg(t, td3 + 5.0, 0.4)
    if k > 0:
        put(fr, text("WITH THE BUSWAY", "bold", 28, WH), x0, 592, eo(k), anchor="l")
        w = full * eio(seg(t, td3 + 5.2, 0.9))
        tl.rrect(fr, x0, 618, x0 + w * (60 / 180), 670, 14, mix(AM, (0, 0, 0), 0.35), eo(k))
        tl.rrect(fr, x0, 618, x0 + w * (45 / 180), 670, 14, AM, eo(k))
        put(fr, text("45 minutes to 1 hour", "head", 44, AM), x0, 714, eo(seg(t, td3 + 6.0, 0.4)), anchor="l")
        put(fr, text("per DOTr, 2020", "mono", 24, GR), x0, 762, eo(seg(t, td3 + 6.3, 0.4)), anchor="l")


def sc_today(fr, t, T):
    te, tf = cl("e", "today"), cl("f", "today")
    hm = eo(seg(t, te + 0.9, 0.5)); hb = eo(seg(t, tf + 0.2, 0.5))
    xsec(fr, T, hi_mrt=hm * (1 - 0.5 * hb), hi_bus=hb)
    e, s = pop(t, 0.15)
    head(fr, "WHAT MOVES THE MOST PEOPLE?", 150, 60, WH, e, s)
    k = seg(t, te + 1.0, 0.45)
    put(fr, tl.pill("MRT-3 · about 388,000 passengers a day (2025)", CY, INK, 34, 0, "bold"), CX, 250, eo(k), 0.8 + 0.2 * back(k))
    k = seg(t, te + cdur("e") * 0.62, 0.45)
    put(fr, tl.pill("Record: 506,904 in one day · Oct 21, 2026", WH, INK, 28, 0, "bold"), CX, 322, eo(k), 0.8 + 0.2 * back(k))
    k = seg(t, tf + 0.3, 0.45)
    if k > 0:
        for sx in (-1, 1):
            cv2.line(fr, (CX + sx * 330, 420), (CX + sx * 150, int(lerp(420, G - 200, eo(k)))), AM, 4, cv2.LINE_AA)
        put(fr, tl.pill("EDSA Busway · about 180,000 a day · one lane each way", AM, INK, 34, 0, "bold"), CX, 398, eo(k), 0.8 + 0.2 * back(k))


def sc_ride(fr, t, T):
    t1, t2 = cl("r1", "ride"), cl("r2", "ride")
    xsec(fr, T, 1, 1, 1, hi_bus=0.0)
    put(fr, tl.pill("TIMELINE B · ANA'S RIDE", CY, INK, 32, 0), CX, 136, eo(seg(t, 0.2, 0.4)))
    busway_inset(fr, T, 380, 190, 1540, 380, eo(seg(t, t1 + 1.6, 0.5)))
    e, s = pop(t, t1 + 4.2)
    put(fr, tl.pill("EXPRESS BUSES PASS", AM, INK, 30, 0), CX, 420, e, s)
    e, s = pop(t, t2 + 1.0)
    put(fr, tl.pill("A BIKE LANE WITH A BARRIER", BIKEC, INK, 28, 0), 380, 470, e, s)
    e, s = pop(t, t2 + 2.6)
    put(fr, tl.pill("SHADE FOR WALKING", (214, 208, 236), INK, 28, 0), 1540, 470, e, s)


def seoul(fr, T, k, x0=360, x1=1560, g=800):
    """Before: elevated highway over a road. After: an open stream with trees. k = 0..1."""
    tl.rrect(fr, x0, g, x1, g + 22, 4, (58, 60, 92))
    if k < 1:
        a = 1 - k
        yd = g - 190 - 260 * k * k
        for px_ in range(x0 + 120, x1 - 60, 240):
            tl.rrect(fr, px_ - 22, yd + 24, px_ + 22, g, 4, (92, 96, 128), a)
        tl.rrect(fr, x0 + 30, yd, x1 - 30, yd + 28, 6, (120, 124, 158), a)
        if a > 0.4:
            for i, px_ in enumerate(range(x0 + 150, x1 - 100, 150)):
                car(fr, px_, yd, 0.85 * a, CARS[i % 8])
            for i, px_ in enumerate(range(x0 + 90, x1 - 60, 240)):
                car(fr, px_, g, 0.8 * a, CARS[(i + 3) % 8])
    if k > 0:
        e = back(k)
        R.water(fr, x0 + 330, x1 - 330, g - 4 + 30 * (1 - k), g + 22, T, 0.9 * k, 4, crest=True, wl=120)
        tl.rrect(fr, x0 + 330, g + 2, x1 - 330, g + 22, 4, (22, 150, 230), k)
        for px_, sc_ in ((x0 + 90, 1.0), (x0 + 230, 0.85), (x1 - 240, 0.9), (x1 - 90, 1.05)):
            tree(fr, px_, g, sc_ * e, T)
        for px_, c in ((x0 + 160, (240, 150, 90)), (x0 + 290, (120, 170, 250)), (x1 - 300, (220, 120, 150)), (x1 - 160, (90, 220, 150))):
            ped(fr, px_, g, 0.95 * e, c)


def sc_world(fr, t, T):
    t1, t2 = cl("w1", "world"), cl("w2", "world")
    a1 = 1 - seg(t, t2 - 0.25, 0.3)
    if a1 > 0:
        put(fr, tl.pill("HAS ANY CITY DONE THIS?", WH, INK, 30, 0), CX, 140, eo(seg(t, 0.2, 0.4)) * a1)
        e, s = pop(t, t1 + 1.7)
        head(fr, "BOGOTÁ", 240, 96, AM, e * a1, s)
        put(fr, text("TransMilenio busway · two lanes at stations", "semi", 40, WH), CX, 326, eo(seg(t, t1 + 2.6, 0.4)) * a1)
        busway_inset(fr, T, 330, 400, 1590, 640, eo(seg(t, t1 + 3.0, 0.5)) * a1)
        e, s = pop(t, t1 + cdur("w1") * 0.66)
        head(fr, "ABOUT 43,000 PASSENGERS AN HOUR", 730, 60, WH, e * a1, s)
        put(fr, text("measured, one direction · Hidalgo et al., 2013", "mono", 24, GR), CX, 790, e * a1)
    a2 = eo(seg(t, t2 + 0.05, 0.4))
    if a2 > 0:
        d = cdur("w2")
        k = eio(seg(t, t2 + d * 0.66, 1.8))
        put(fr, tl.pill("AND ONE STEP FURTHER", WH, INK, 30, 0), CX, 140, a2)
        head(fr, "SEOUL", 240, 96, AM, a2, 0.85 + 0.15 * back(seg(t, t2 + 0.05, 0.45)))
        put(fr, text("Cheonggyecheon · 2003 to 2005", "semi", 40, WH), CX, 326, a2)
        seoul(fr, T, k)
        al = eo(seg(t, t2 + d * 0.36, 0.4)) * (1 - k)
        put(fr, tl.pill("Elevated highway · about 168,000 vehicles a day", RED, WH, 30, 0, "bold"), CX, 420, al)
        put(fr, tl.pill("5.8 km of stream restored", CY, INK, 30, 0, "bold"), CX, 420, eo(k) * a2 if k > 0.5 else 0)


def sc_real(fr, t, T):
    tq, tq2, tr, tw = cl("q", "real"), cl("q2", "real"), cl("r", "real"), cl("w", "real")
    kb = 1 - eio(seg(t, tw + 0.3, 1.0))
    xsec(fr, T, kb, kb, kb)
    aA = 1 - seg(t, tw - 0.2, 0.3)
    if aA > 0:
        a1 = aA * (1 - seg(t, tq2 - 0.2, 0.3))
        e, s = pop(t, tq + 0.2)
        put(fr, tl.pill("THE REAL COST", RED, WH, 32, 0), CX, 150, e * aA, s)
        e, s = pop(t, tq + 1.5)
        head(fr, "DRIVERS LOSE HALF THEIR LANES", 240, 60, WH, e * a1, s)
        e, s = pop(t, tq + 3.6)
        head(fr, "IT ONLY WORKS IF ENOUGH PEOPLE SWITCH", 318, 48, AM, e * a1, s)
        a2 = aA * eo(seg(t, tq2 + 0.1, 0.3)) * (1 - seg(t, tr - 0.2, 0.3))
        if a2 > 0:
            head(fr, "170,000 MOTORCYCLES A DAY", 240, 70, AM, a2, 0.85 + 0.15 * back(seg(t, tq2 + 3.4, 0.45)))
            put(fr, text("DOTr estimate, 2024 · this design leaves that question open", "semi", 36, WH), CX, 318, a2)
        if tr <= t < tw:
            stamp(fr, "ONE POSSIBLE DESIGN", CX, 300, t, tr + 0.4, 0.6)
    aB = eo(seg(t, tw + 0.1, 0.4))
    if aB > 0:
        put(fr, tl.pill("BACK IN TIMELINE A", GR, INK, 32, 0), CX, 150, aB)
        head(fr, "EDSA IS BEING RESURFACED NOW", 248, 60, WH, aB, 0.85 + 0.15 * back(seg(t, tw + 0.1, 0.45)))
        put(fr, text("DPWH rehabilitation, phase 2 · remaining work targeted for 2027", "semi", 38, WH), CX, 330, eo(seg(t, tw + 2.6, 0.4)))


SCN = {"hook": sc_hook, "road": sc_road, "ana": sc_ana, "today": sc_today, "cap": E.sc_cap, "fork": E.sc_fork, "ride": sc_ride,
       "world": sc_world, "math": E.sc_math, "real": sc_real, "outro": E.sc_outro}
SRC = {"hook": "Simplified typical section; lane count varies · AI voice · Source: DoTr busway ridership, 2025",
       "road": "Schematic map, not to scale · Sources: Manila Bulletin (2020), RA 2140, MMDA (2026)",
       "ana": "Schematic map · Ana is an illustration · Source: DOTr via Inquirer and CarGuide, 2020",
       "today": "Sources: DOTr / MRT-3 and DoTr busway ridership, 2025–2026",
       "cap": "Source: NACTO Transit Street Design Guide (planning-level capacities)",
       "fork": "Illustration of one possible design. Not an official plan.",
       "ride": "Illustration of one possible design. Not an official plan.",
       "world": "Illustrations · Sources: Hidalgo et al. (2013); Landscape Performance Series; Seoul Metropolitan Government",
       "math": "Source: NACTO per-lane capacities; totals are our own arithmetic",
       "real": "Sources: DOTr (2024), DPWH (November 2026)", "outro": None}


def scene_frame(i, T):
    name, s0 = R.STARTS[i]
    fr = (space.space_bg(W, H, 11) if name == "outro" else city_bg()).copy()
    if name in ("road", "ana", "world"):
        fr[G - 340:G + 2] = (space.space_bg(W, H, 11)[G - 340:G + 2] * 0.8).astype(np.uint8)   # no skyline behind maps/cards
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
