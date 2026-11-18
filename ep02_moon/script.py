"""Timeline B, episode 2: What if the Moon disappeared?
Voice is recorded piece by piece so every cue has an exact time. Writes vo.wav + timeline.json."""
import json, sys
import numpy as np, soundfile as sf

VOICE, SPEED = ("am_puck", "am_puck", "am_michael"), 1.08   # two parts lively to one part calm
# (scene, cue key, caption group, caption text, pause after, spoken text if different)
S = [
 ("hook", "h1", 1, "Look up tonight. The Moon is about 384,000 kilometres away, where it has been for billions of years.", 0.3,
  "Look up tonight. The Moon is about three hundred eighty-four thousand kilometres away, where it has been for billions of years."),
 ("hook", "h2", 2, "Now delete it. No explosion, no debris. It's just gone.", 0.35, None),
 ("hook", "h3", 3, "Welcome to Timeline B.", 1.5, None),
 ("moon", "a", 4, "First, Timeline A. The Moon is about 3,475 kilometres wide, roughly a quarter the width of Earth.", 0.3,
  "First, Timeline A. The Moon is about three thousand four hundred seventy-five kilometres wide, roughly a quarter the width of Earth."),
 ("moon", "a2", 5, "The leading theory is that it formed about four and a half billion years ago, when something the size of Mars hit the young Earth.", 0.3, None),
 ("moon", "a2b", 6, "Back then it hung far closer, about 22,000 kilometres away by one estimate. It has been drifting outward ever since.", 0.3,
  "Back then it hung far closer, about twenty-two thousand kilometres away by one estimate. It has been drifting outward ever since."),
 ("moon", "a3", 7, "Ever since, it has been quietly running things down here.", 0.6, None),
 ("night", "b", 8, "In Timeline B, the first thing you notice is the dark. Ana steps outside on what should be a full-Moon night. The glow is gone.", 0.3, None),
 ("night", "b2", 9, "A full Moon is more than 1,600 times brighter than Venus, the next brightest thing in the night sky. Now Venus is the best we've got.", 0.3,
  "A full Moon is more than sixteen hundred times brighter than Venus, the next brightest thing in the night sky. Now Venus is the best we've got."),
 ("night", "b3", 10, "For scale, the Sun is about 400,000 times brighter than the full Moon. But at night, the Moon was all we had.", 0.6,
  "For scale, the Sun is about four hundred thousand times brighter than the full Moon. But at night, the Moon was all we had."),
 ("tide", "c", 11, "Morning comes, and the sea feels wrong. The Moon was the main engine of the tides.", 0.3, None),
 ("tide", "c1b", 12, "Why the Moon and not the Sun? The Sun is 27 million times more massive, but it is 390 times farther away, and for tides, distance matters most.", 0.3,
  "Why the Moon and not the Sun? The Sun is twenty-seven million times more massive, but it is three hundred ninety times farther away, and for tides, distance matters most."),
 ("tide", "c2", 13, "They don't stop, because the Sun pulls on the oceans too. But NOAA puts the Sun's tidal pull at about half the Moon's. So the tides shrink to roughly a third of what they were.", 0.3,
  "They don't stop, because the Sun pulls on the oceans too. But Noah puts the Sun's tidal pull at about half the Moon's. So the tides shrink to roughly a third of what they were."),
 ("tide", "c3", 14, "No more spring tides. Just a small, steady rise and fall.", 0.6, None),
 ("life", "d", 15, "Under the water, it gets stranger. On Australia's Great Barrier Reef, corals release their eggs together, just a few days after a full Moon.", 0.3, None),
 ("life", "d1b", 16, "Researchers have called it the largest reproduction event on Earth.", 0.3, None),
 ("life", "d2", 17, "Scientists have shown that moonlight is one of the signals they use. In Timeline B, that signal never comes. Nobody knows how well they would adapt.", 0.6, None),
 ("day", "e", 18, "Then there's the clock. The Moon's pull on the tides acts like a brake on Earth's spin, adding about two milliseconds to the day every century.", 0.3, None),
 ("day", "e2", 19, "It adds up. One study of ancient rocks found that 1.4 billion years ago, a day lasted about 18 hours.", 0.3,
  "It adds up. One study of ancient rocks found that one point four billion years ago, a day lasted about eighteen hours."),
 ("day", "e3", 20, "Take the Moon away, and most of that braking stops.", 0.6, None),
 ("tilt", "f", 21, "The biggest question is the tilt. Earth leans at about 23 degrees, and that lean gives us seasons. With the Moon, it only wobbles between about 22 and 24 and a half degrees.", 0.3,
  "The biggest question is the tilt. Earth leans at about twenty-three degrees, and that lean gives us seasons. With the Moon, it only wobbles between about twenty-two and twenty-four and a half degrees."),
 ("tilt", "f2", 22, "In 1993, a famous study calculated that without the Moon, the tilt could swing anywhere from zero to 85 degrees.", 0.3,
  "In nineteen ninety-three, a famous study calculated that without the Moon, the tilt could swing anywhere from zero to eighty-five degrees."),
 ("tilt", "f2b", 23, "Mars is the warning. It has only two tiny moons, and its tilt is thought to swing between zero and 60 degrees.", 0.3,
  "Mars is the warning. It has only two tiny moons, and its tilt is thought to swing between zero and sixty degrees."),
 ("tilt", "f3", 24, "But in 2012, new simulations found the swings might be much smaller, about ten degrees more than today. So the science isn't settled.", 0.6,
  "But in twenty twelve, new simulations found the swings might be much smaller, about ten degrees more than today. So the science isn't settled."),
 ("gone", "g", 25, "And some things simply vanish. No more eclipses. No more moonrise. No more phases to count the months by.", 0.6, None),
 ("real", "r", 26, "Back in Timeline A, breathe. Nothing we know of can make the Moon disappear.", 0.3, None),
 ("real", "r2", 27, "It is leaving, though: about 3.8 centimetres a year. At that pace, it will be up there for a very long time.", 0.6,
  "It is leaving, though: about three point eight centimetres a year. At that pace, it will be up there for a very long time."),
 ("outro", "t", 28, "That was Timeline B.", 0.2, None),
 ("outro", "s", 29, "What should we change next?", 2.6, None),
]
SOURCES = [
 "NASA, Royal Museums Greenwich, Space.com: Moon size, distance, origin, drift · EarthSky: brightness",
 "NOAA Ocean Service: tide-generating forces · Kaniewska et al. (2015), eLife: coral spawning and moonlight",
 "Meyers & Malinverno (2018), PNAS: 18-hour day · day lengthening about 2 ms per century",
 "Laskar et al. (1993) and Laskar & Robutel (1993), Nature · Lissauer et al. (2012), Icarus: axial tilt",
]

if __name__ == "__main__":
    from kokoro_onnx import Kokoro
    import os
    TTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tts")
    k = Kokoro(os.path.join(TTS, "kokoro-v1.0.onnx"), os.path.join(TTS, "voices-v1.0.bin"))
    VS = sum(k.get_voice_style(v) for v in VOICE) / len(VOICE)
    SR, LEAD = 24000, 0.6
    out, t, tl = [np.zeros(int(LEAD * SR), np.float32)], LEAD, []
    for sc, key, grp, txt, pause, say in S:
        a, sr = k.create(say or txt, voice=VS, speed=SPEED, lang="en-us")
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
