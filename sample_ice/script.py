"""Timeline B sample: What if all the ice on Earth melted?  (lively cut)
Records the voice piece by piece so every cue has an exact time, and writes timeline.json."""
import json, sys
import numpy as np, soundfile as sf

VOICE, SPEED = ("am_puck", "am_michael"), 1.05      # 50/50 blend of a lively and a calm voice
# (scene, cue key, caption group, text, pause after)
S = [
 ("open", "a", 1, "In Timeline A, ice covers about a tenth of all the land on Earth.", 0.35),
 ("open", "b", 2, "But this is Timeline B.", 0.22),
 ("open", "c", 3, "Here, every bit of it has melted.", 0.8),
 ("float", "d", 4, "Start with the ice floating on the sea.", 0.22),
 ("float", "e", 5, "It's already in the water, so melting it barely moves sea level.", 0.32),
 ("float", "f", 6, "The ice that matters is sitting on land.", 0.5),
 ("count", "g", 7, "Greenland's ice sheet holds enough water to lift the oceans about seven metres.", 0.3),
 ("count", "h", 8, "Antarctica's? About fifty-eight.", 0.35),
 ("count", "ij", 9, "Add the mountain glaciers, and the U.S. Geological Survey puts the total at roughly seventy metres.", 0.5),
 ("city", "k", 10, "That's about as tall as a twenty-storey building.", 0.3),
 ("city", "l", 11, "Every coastal city on the planet would flood.", 0.2),
 ("city", "m1", 12, "Manila.", 0.1), ("city", "m2", 12, "Tokyo.", 0.1),
 ("city", "m3", 12, "New York.", 0.1), ("city", "m4", 12, "London.", 0.6),
 ("real", "n", 13, "But back in Timeline A, this is not a forecast.", 0.3),
 ("real", "o", 14, "Some scientists say melting all of it would probably take more than five thousand years.", 0.4),
 ("real", "p", 15, "Still, the sea really is rising:", 0.12),
 ("real", "q", 15, "about twenty-one to twenty-four centimetres since 1880.", 0.6),
 ("outro", "r", 16, "That was Timeline B.", 0.2),
 ("outro", "s", 17, "What should we change next?", 2.6),
]
SOURCES = [
 "USGS: How would sea level change if all glaciers melted?",
 "NSIDC: Glaciers quick facts · Ice Sheets quick facts",
 "NOAA Climate.gov: Climate Change: Global Sea Level",
 "National Geographic (Sept 2013): If All the Ice Melted",
]

if __name__ == "__main__":
    from kokoro_onnx import Kokoro
    import os
    TTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tts")
    k = Kokoro(os.path.join(TTS, "kokoro-v1.0.onnx"), os.path.join(TTS, "voices-v1.0.bin"))
    VS = sum(k.get_voice_style(v) for v in VOICE) / len(VOICE)
    SR, LEAD = 24000, 0.6
    out, t, tl = [np.zeros(int(LEAD * SR), np.float32)], LEAD, []
    for sc, key, grp, txt, pause in S:
        a, sr = k.create(txt, voice=VS, speed=SPEED, lang="en-us")
        a = np.asarray(a, np.float32)
        nz = np.where(np.abs(a) > 0.012)[0]
        a = a[max(0, nz[0] - 500): nz[-1] + 1300]
        a[:240] *= np.linspace(0, 1, 240); a[-600:] *= np.linspace(1, 0, 600)
        a = a / (np.abs(a).max() + 1e-9) * 0.85
        d = len(a) / SR
        tl.append(dict(scene=sc, key=key, grp=grp, text=txt, t=round(t, 3), d=round(d, 3)))
        out += [a, np.zeros(int(pause * SR), np.float32)]
        t += d + pause
    sf.write("vo.wav", np.concatenate(out), SR)
    json.dump(dict(lines=tl, total=round(t, 3)), open("timeline.json", "w"), indent=1)
    for x in tl:
        print(x["scene"], x["key"], x["t"], x["d"])
    print("total", round(t, 2))
    if len(sys.argv) > 1:      # voice comparison clip
        parts = []
        for v in ("am_puck", "af_bella", "am_fenrir"):
            a, sr = k.create("But this is Timeline B! And here? Every bit of it just melted!", voice=v, speed=SPEED, lang="en-us")
            parts += [np.asarray(a, np.float32), np.zeros(SR // 2, np.float32)]
        sf.write("voices.wav", np.concatenate(parts), SR)
