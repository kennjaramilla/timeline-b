"""Thumbnail for the Moon episode. Usage: thumb.py out_dir"""
from render import *          # noqa
import render as E


def make():
    fr = E.SKY.copy()
    put(fr, space.planet(330, "A", 5, 0.6, E.LIGHT), 430, 760)
    mx, my = 1430, 700
    tl.glow(fr, lambda lay, q: cv2.circle(lay, (int(mx * q), int(my * q)), int(230 * q), (60, 70, 110), -1), 0.9, 80)
    put(fr, fullmoon(200), mx, my, 0.22)
    for i in range(30):
        a0 = i * 12
        cv2.ellipse(fr, (mx, my), (206, 206), 0, a0, a0 + 7, WH, 8, cv2.LINE_AA)
    head(fr, "?", my + 6, 260, AM, x=mx)
    head(fr, "WHAT IF THE MOON", 170, 138, WH)
    head(fr, "DISAPPEARED?", 350, 176, AM)
    put(fr, tl.badge(104), W - 96, 96)
    return fr


if __name__ == "__main__":
    out = sys.argv[1]
    fr = make()
    Image.fromarray(fr).save(os.path.join(out, "TimelineB_EP02_Thumbnail_1920x1080.png"))
    Image.fromarray(cv2.resize(fr, (1280, 720), interpolation=cv2.INTER_AREA)).save(os.path.join(out, "TimelineB_EP02_Thumbnail_1280x720.jpg"), quality=92)
