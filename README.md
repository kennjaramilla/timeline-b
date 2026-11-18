# Timeline B

Video engine for **Timeline B**, an animated what-if channel. Tagline: *What if things went differently?*

Every video opens in Timeline A (what is real), forks to Timeline B (one thing changed), and ends back in Timeline A with what is actually true today.

## What is here

| Path | What it is |
|---|---|
| `tl.py` | Drawing kit: colours, fonts, text sprites, pills, the forking line, the B badge, wordmark |
| `space.py` | Procedural planets, star field and nebula for the cinematic look |
| `brand.py` | Profile picture, Facebook cover and YouTube banner (`assets/brand/` has the exports) |
| `audio_short.py` | Music + effects + voice mix for short pieces such as Reels |
| `ep01_edsa/` | Episode 1, *What if EDSA was redesigned from scratch?* (full video and two Reels) |
| `sample_ice/` | The first test video, *What if all the ice on Earth melted?* |

Inside an episode folder:

- `script.py`: the narration, split into pieces. Each piece has a cue key, so visuals are timed to the voice exactly. Also holds the sources list.
- `base.py`: shared frame assembly (captions with word highlight, top bar, scene wipes, outro).
- `render.py` / `render2.py`: the scenes. `render2.py` is the extended cut and imports `render.py`.
- `reels.py`: vertical 1080x1920 cuts with their own short narration.
- `audio.py`: original music, sound effects and the final mix.

## Set up

```
pip install -r requirements.txt
./setup_tts.sh          # voice model, about 350 MB, kept out of git
```

Fonts used: Archivo Black, Inter, Anonymous Pro (paths are at the top of `tl.py`). `ffmpeg` must be installed.

## Make an episode

1. Copy `ep01_edsa/` to a new folder, for example `ep02_moon/`.
2. Research first. Every number needs a source; put the sources in `SOURCES` in `script.py`.
3. Rewrite `S` in `script.py`. Keep one idea per piece and give each piece a cue key.
4. `python3 script.py` records the voice and writes `timeline.json` with the cue times.
5. Write the scenes in `render2.py`. Time everything with `cl("key", "scene")`, never with fixed seconds.
6. Check frames before rendering: `python3 render2.py stills check.jpg 4.5 30 60`.
7. Render in two halves (two CPU cores), then join:
   ```
   python3 render2.py part 0 N/2 parts/a.mp4 &  python3 render2.py part N/2 N parts/b.mp4
   python3 audio.py
   ffmpeg -f concat -safe 0 -i list.txt -c copy silent.mp4
   ffmpeg -i silent.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac out.mp4
   ```
8. Reels: edit `REELS` in `reels.py`, then `python3 reels.py voice A`, `python3 reels.py render A reelA/v.mp4`, and mix with `audio_short.py` from inside the reel folder.

## Channel rules

- Facts come from named sources and are shown on screen with the source. Contested or estimated figures are attributed ("according to...").
- Anything we calculate ourselves is labelled as our arithmetic.
- Scenarios are framed as scenarios. Each video says once, clearly, that it is not a forecast or an official plan.
- Illustrations are labelled as illustrations. No real logos, photos or other channels' artwork.
- The voice is an AI voice and the video says so.
- Tone: curious and clear. A hook in the first five seconds, a person to follow where possible, and at least two different views so it is never one picture for the whole video.

## Look and voice

- Night sky and dark indigo, white type, cyan for Timeline B, yellow for the B badge and key numbers, lavender grey for Timeline A.
- Narrator: Kokoro voices `am_puck` and `am_michael` blended 2:1, speed 1.08.
- Music: original, 100 bpm, soft drums, ducked under the voice.

## Episode list

1. Philippines: What if EDSA was redesigned from scratch? (done)
2. World: What if the Moon disappeared?
3. Philippines: What if all the ice melted, and what happens to the Philippines?
4. World: What if the internet went down for a year?
5. Philippines: What if the Big One hit Metro Manila?
6. World: What if the dinosaurs never went extinct?
