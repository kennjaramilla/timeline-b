"""Timeline B brand kit (cinematic space): profile picture, Facebook cover, YouTube banner.
Two versions of one world: Timeline A (ice caps) on the left, Timeline B (no ice, higher seas) on the right."""
import os
import cv2
import numpy as np
import tl, space
from tl import CY, WH, GR, AM, INK

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def glowline(fr, pts, w, cols):
    tl.glow(fr, lambda lay, k: tl.gline(lay, np.asarray(pts) * k, max(1, int(w * k * 2.6)), 1.0, cols), 1.0, sigma=w * 2.6)
    tl.gline(fr, pts, w, 1.0, cols)


def link(fr, xa, xb, y, node_x, rise, dx, w):
    """Grey Timeline A line from the left world to a node, cyan Timeline B branch on to the right world."""
    cv2.line(fr, (int(xa), int(y)), (int(node_x), int(y)), GR, int(w * 0.8), cv2.LINE_AA)
    tl.dashed(fr, node_x, node_x + dx * 1.5, y, tl.DIM, max(2, int(w * 0.5)), w * 3, w * 2.4)
    glowline(fr, tl.fork_pts(node_x, y, dx, rise, xb), w, (CY, (150, 235, 255), WH))
    cv2.circle(fr, (int(node_x), int(y)), int(w * 1.9), WH, -1, cv2.LINE_AA)
    cv2.circle(fr, (int(node_x), int(y)), int(w * 1.0), INK, -1, cv2.LINE_AA)


def title(fr, cx, cy, h, tag_size, gap):
    tl.glow(fr, lambda lay, k: cv2.ellipse(lay, (int(cx * k), int(cy * k)), (int(h * 4.2 * k), int(h * 0.9 * k)), 0, 0, 360, (0, 0, 0), -1), 0, 1)
    tl.wordmark(fr, cx, cy, h, eyes=False, tilt=0)
    tl.put(fr, tl.text("What if things went differently?", "semi", tag_size, INK), cx + 2, cy + gap + 3, 0.8)
    tl.put(fr, tl.text("What if things went differently?", "semi", tag_size, WH), cx, cy + gap)


def profile(S=1080):
    k = S / 1080
    fr = space.space_bg(S, S, 6).copy()
    p = space.planet(int(560 * k), "B", 5, 0.6)
    tl.put(fr, p, 840 * k, 1150 * k)                               # big world rising from the lower right
    node = (190 * k, 610 * k)
    cv2.line(fr, (0, int(node[1])), (int(node[0]), int(node[1])), GR, int(22 * k), cv2.LINE_AA)
    tl.dashed(fr, node[0], 560 * k, node[1], tl.DIM, int(12 * k), 62 * k, 50 * k)
    glowline(fr, tl.fork_pts(node[0], node[1], 300 * k, 215 * k, 640 * k), int(26 * k), (CY, (150, 235, 255), WH))
    cv2.circle(fr, (int(node[0]), int(node[1])), int(48 * k), WH, -1, cv2.LINE_AA)
    cv2.circle(fr, (int(node[0]), int(node[1])), int(26 * k), INK, -1, cv2.LINE_AA)
    tl.put(fr, tl.badge(int(360 * k)), 650 * k, 390 * k)
    tl.put(fr, tl.text("TIMELINE", "head", int(120 * k), INK, track=int(8 * k)), 546 * k, 818 * k, 0.8)
    tl.put(fr, tl.text("TIMELINE", "head", int(120 * k), WH, track=int(8 * k)), 540 * k, 810 * k)
    return fr


def cover(W=1640, H=624):
    fr = space.space_bg(W, H, 4).copy()
    y = 455
    tl.put(fr, space.planet(210, "A", 5, 0.6, glow=0.8), 330, y)
    tl.put(fr, space.planet(225, "B", 5, 0.6), 1345, y)
    link(fr, 330 + 214, 1345 - 231, y + 40, 700, 80, 190, 9)
    tl.put(fr, tl.text("TIMELINE A", "mono", 22, GR, track=4), 330, y - 242)
    tl.put(fr, tl.text("TIMELINE B", "mono", 22, CY, track=4), 1380, y - 252)
    title(fr, W / 2, 150, 118, 44, 128)
    return fr


def banner(W=2560, H=1440):
    fr = space.space_bg(W, H, 8).copy()
    # TV-only area: a ringed giant and a moon
    half = space.rings(fr, 2130, 300, 150)
    half(False); tl.put(fr, space.planet(150, "gas", 12, 1.0, glow=0.6), 2130, 300); half(True)
    tl.put(fr, space.planet(90, "moon", 3, 2.0, glow=0.3), 420, 1150)
    tl.put(fr, space.planet(520, "B", 5, 2.2, glow=0.8), 2300, 1560)
    y = 800
    tl.put(fr, space.planet(145, "A", 5, 0.6, glow=0.8), 680, y + 10)
    tl.put(fr, space.planet(150, "B", 5, 0.6), 1870, y + 6)
    link(fr, 680 + 148, 1870 - 154, y + 62, 1010, 54, 170, 8)
    title(fr, W / 2, 628, 122, 44, 118)
    tl.put(fr, tl.text("NEW ANIMATED WHAT-IF EVERY WEEK", "mono", 28, AM, track=4), W / 2, 1060)
    return fr


if __name__ == "__main__":
    p, c, b = profile(), cover(), banner()
    tl.save(p, f"{OUT}/TimelineB_Profile_1080.png")
    tl.save(c, f"{OUT}/TimelineB_Facebook_Cover_1640x624.png")
    tl.save(b, f"{OUT}/TimelineB_YouTube_Banner_2560x1440.png")
    m = np.zeros(p.shape[:2], np.uint8); cv2.circle(m, (540, 540), 540, 255, -1)
    p = p.copy(); p[m == 0] = 255
    chk = np.full((624 + 624 + 423 + 20, 1640, 3), 60, np.uint8)
    chk[:624, :624] = cv2.resize(p, (624, 624), interpolation=cv2.INTER_AREA)
    chk[:140, 700:840] = cv2.resize(p, (140, 140), interpolation=cv2.INTER_AREA)
    chk[:562, 880:1640] = cv2.resize(b, (1000, 562), interpolation=cv2.INTER_AREA)[:, 120:880]
    chk[634:1258] = c
    cv2.rectangle(chk, (265, 634), (1375, 1257), (255, 0, 0), 2)
    chk[1268:1268 + 423, :1546] = b[508:931, 507:2053]
    tl.save(chk, os.path.join(OUT, "brand_check.jpg"))
