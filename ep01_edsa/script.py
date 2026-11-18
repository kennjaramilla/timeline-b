"""Timeline B, episode 1: What if EDSA was redesigned from scratch?
Voice is recorded piece by piece so every cue has an exact time. Writes vo.wav + timeline.json."""
import json, sys
import numpy as np, soundfile as sf

VOICE, SPEED = ("am_puck", "am_puck", "am_michael"), 1.08   # two parts lively to one part calm
# (scene, cue key, caption group, caption text, pause after, spoken text if different)
S = [
 ("hook", "h1", 1, "On EDSA, one lane of buses carries about 180,000 people a day.", 0.3,
  "On Edsa, one lane of buses carries about a hundred eighty thousand people a day."),
 ("hook", "h2", 2, "So why do the buses get one lane, and everything else gets about four?", 0.35, None),
 ("hook", "h3", 3, "Let's change that. Welcome to Timeline B.", 1.3, None),
 ("road", "a", 4, "First, Timeline A. EDSA is 23.8 kilometres long, a half circle around Manila, from Caloocan to Pasay.", 0.3,
  "First, Timeline A. Edsa is twenty-three point eight kilometres long, a half circle around Manila, from Caloocan to Pasay."),
 ("road", "a2", 5, "It was completed in 1940 as the Circumferential Road. Later it became Highway 54, and in 1959 a law renamed it after the historian Epifanio de los Santos.", 0.35,
  "It was completed in nineteen forty as the Circumferential Road. Later it became Highway fifty-four, and in nineteen fifty-nine a law renamed it after the historian Epifanio de los Santos."),
 ("road", "b", 6, "Today, more than 400,000 vehicles squeeze onto it every day.", 0.3,
  "Today, more than four hundred thousand vehicles squeeze onto it every day."),
 ("road", "c", 7, "According to the MMDA, it was built for about 250,000 to 300,000.", 0.6,
  "According to the M M D A, it was built for about two hundred fifty to three hundred thousand."),
 ("ana", "d", 8, "Meet Ana. She's made up, but her commute is real: Monumento to the far end of the line, every morning.", 0.3, None),
 ("ana", "d2", 9, "Before 2020, buses fought for space with everyone else, and that ride could take up to three hours.", 0.3,
  "Before twenty twenty, buses fought for space with everyone else, and that ride could take up to three hours."),
 ("ana", "d3", 10, "Then the busway opened: one lane in the middle, for buses only. The Department of Transportation said the same trip fell to 45 minutes to an hour.", 0.6,
  "Then the busway opened: one lane in the middle, for buses only. The Department of Transportation said the same trip fell to forty-five minutes to an hour."),
 ("today", "e", 11, "Above her, the train, MRT-3, carried about 388,000 passengers a day last year. This October it set a record: more than half a million in one day.", 0.3,
  "Above her, the train, M R T three, carried about three hundred eighty-eight thousand passengers a day last year. This October it set a record: more than half a million in one day."),
 ("today", "f", 12, "And that single bus lane each way? About 180,000 a day.", 0.6,
  "And that single bus lane each way? About a hundred eighty thousand a day."),
 ("cap", "g", 13, "Here's why it works. By street-planning guidelines, a lane of private cars moves 600 to 1,600 people an hour.", 0.3,
  "Here's why it works. By street-planning guidelines, a lane of private cars moves six hundred to sixteen hundred people an hour."),
 ("cap", "h", 14, "A dedicated bus lane? 4,000 to 8,000.", 0.6, "A dedicated bus lane? Four thousand to eight thousand."),
 ("fork", "i", 15, "So in Timeline B, EDSA is redesigned around people, not vehicles.", 0.4,
  "So in Timeline B, Edsa is redesigned around people, not vehicles."),
 ("fork", "j", 16, "Each direction gets two bus lanes instead of one.", 0.3, None),
 ("fork", "k", 17, "The curb lane becomes a protected bikeway.", 0.3, None),
 ("fork", "l", 18, "The sidewalk gets wider, with trees.", 0.3, None),
 ("fork", "m", 19, "And general traffic goes from about four lanes to two.", 0.6, None),
 ("ride", "r1", 20, "Now ride with Ana again. Her bus doesn't wait behind the one in front. Express buses pass the ones that stop.", 0.3, None),
 ("ride", "r2", 21, "If she'd rather cycle, there's a lane with a barrier. And if she walks, there's shade.", 0.6, None),
 ("world", "w1", 22, "Has any city done this? Bogotá built its busway with two lanes at stations so buses can overtake. Researchers measured about 43,000 passengers an hour in one direction.", 0.35,
  "Has any city done this? Bogota built its busway with two lanes at stations so buses can overtake. Researchers measured about forty-three thousand passengers an hour in one direction."),
 ("world", "w2", 23, "Seoul went further. In 2003 it began tearing down an elevated highway that carried about 168,000 vehicles a day, and brought back the stream underneath.", 0.6,
  "Seoul went further. In two thousand three it began tearing down an elevated highway that carried about a hundred sixty-eight thousand vehicles a day, and brought back the stream underneath."),
 ("math", "n", 24, "Back to EDSA. Run the same guideline numbers, and one direction could carry about 9,000 to 19,000 people an hour.", 0.3,
  "Back to Edsa. Run the same guideline numbers, and one direction could carry about nine thousand to nineteen thousand people an hour."),
 ("math", "o", 25, "Today's layout: about 6,000 to 14,000.", 0.3, "Today's layout: about six thousand to fourteen thousand."),
 ("math", "p", 26, "That's capacity on paper, not a forecast.", 0.6, None),
 ("real", "q", 27, "And there's a real cost. Drivers would lose half their lanes, and it only works if enough of them switch to the bus, the train or a bike.", 0.3, None),
 ("real", "q2", 28, "It also leaves a big question open: by a 2024 government estimate, about 170,000 motorcycles use EDSA every day.", 0.3,
  "It also leaves a big question open: by a twenty twenty-four government estimate, about a hundred seventy thousand motorcycles use Edsa every day."),
 ("real", "r", 29, "So this is one possible design, not an official plan.", 0.35, None),
 ("real", "w", 30, "Back in Timeline A, the government is resurfacing EDSA right now, with the remaining work targeted for 2027.", 0.6,
  "Back in Timeline A, the government is resurfacing Edsa right now, with the remaining work targeted for twenty twenty-seven."),
 ("outro", "t", 31, "That was Timeline B.", 0.2, None),
 ("outro", "s", 32, "What should we redesign next?", 2.6, None),
]
SOURCES = [
 "MMDA (2026): EDSA volume and capacity · DOTr / MRT-3 and EDSA Busway ridership · DOTr (2020, 2024)",
 "Manila Bulletin (2020) and Republic Act 2140: EDSA history · DPWH (Nov 2026): rehabilitation",
 "NACTO Transit Street Design Guide · Hidalgo et al. (2013), TransMilenio capacity",
 "Landscape Performance Series and Seoul Metropolitan Government: Cheonggyecheon",
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
