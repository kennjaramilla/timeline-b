"""Thumbnail for the EDSA episode: Timeline A on the left, Timeline B on the right. Usage: thumb.py out_dir"""
from render import *          # noqa
import render as E

def make():
    A = city_bg().copy(); xsec(A, 2.0, labels=False)
    B = city_bg().copy(); xsec(B, 2.0, 1, 1, 1, labels=False)
    fr = space.space_bg(W, H, 11).copy()
    y0 = 400
    a = A[y0:940, :CX].astype(np.float32); g = a.mean(2, keepdims=True)
    a = (a * 0.55 + g * 0.45) * np.array([1.08, 0.9, 0.9], np.float32)          # duller, slightly red
    b = np.clip(B[y0:940, CX:].astype(np.float32) * 1.12 + np.array([0, 6, 10], np.float32), 0, 255)
    fr[H - (940 - y0):, :CX] = np.clip(a, 0, 255).astype(np.uint8)
    fr[H - (940 - y0):, CX:] = b.astype(np.uint8)
    top = H - (940 - y0)
    # fade the strip into the sky
    for i in range(90):
        k = i / 90
        fr[top + i] = (fr[top + i] * k + space.space_bg(W, H, 11)[top + i] * (1 - k)).astype(np.uint8)
    tl.glow(fr, lambda lay, q: cv2.line(lay, (int(CX * q), int((top + 40) * q)), (int(CX * q), int(H * q)), CY, 4), 1.0, 22)
    cv2.line(fr, (CX, top + 40), (CX, H), WH, 6, cv2.LINE_AA)
    head(fr, "WHAT IF EDSA", 190, 176, WH)
    head(fr, "WAS REDESIGNED?", 372, 150, AM)
    put(fr, tl.pill("TIMELINE A · TODAY", GR, INK, 44, 0), CX / 2, 560)
    put(fr, tl.pill("TIMELINE B", CY, INK, 44, 0), CX * 1.5, 560)
    put(fr, tl.badge(104), W - 96, 96)
    return fr

if __name__ == "__main__":
    out = sys.argv[1]
    fr = make()
    Image.fromarray(fr).save(os.path.join(out, "TimelineB_EP01_Thumbnail_1920x1080.png"))
    Image.fromarray(cv2.resize(fr, (1280, 720), interpolation=cv2.INTER_AREA)).save(os.path.join(out, "TimelineB_EP01_Thumbnail_1280x720.jpg"), quality=92)
