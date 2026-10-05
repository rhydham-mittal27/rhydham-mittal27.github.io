"""Assembles reel/voiceover.wav from the per-line TTS takes in reel/build/vo/
and writes each line's real start/end back into timeline.js (captions use them).

Each line is trimmed of silence and placed just after the start of its segment;
it fails loudly if a line overruns its segment (lengthen that segment's "real").

    python3 reel/voice.py
"""
import json
import os
import re
import wave

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
src = open(os.path.join(HERE, "timeline.js")).read()
TL = json.loads(re.sub(r"^window\.TL\s*=\s*|;\s*$", "", src.strip()))

seg_start, acc = [], 0.0
for s in TL["segments"]:
    seg_start.append(acc)
    acc += s["real"]
assert abs(acc - TL["duration"]) < 1e-6, f"segments sum to {acc}, duration is {TL['duration']}"

track = np.zeros(int(TL["duration"] * SR))
for i, line in enumerate(TL["narration"]):
    sr, x = wavfile.read(os.path.join(HERE, "build", "vo", f"line-{i}.wav"))
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(1)
    a = np.abs(x)
    idx = np.where(a > 0.02 * a.max())[0]
    pad = int(0.03 * sr)
    x = x[max(0, idx[0] - pad): idx[-1] + pad]
    x = resample_poly(x, SR, sr)
    x *= np.linspace(1, 0, len(x)) ** 0.05  # soften the tail
    k = line["seg"]
    lead = 0.05 if k == 0 else min(0.1, max(0.02, TL["segments"][k]["real"] - len(x) / SR - 0.02))
    if k == len(TL["segments"]) - 1:  # loop line: end right on the seam into "Six weeks."
        lead = TL["segments"][k]["real"] - len(x) / SR - 0.08
    start = seg_start[k] + lead
    end = start + len(x) / SR
    seg_end = seg_start[k] + TL["segments"][k]["real"]
    if end > seg_end + 1e-3:
        raise SystemExit(f"line {i} ends at {end:.2f}s, past its segment end {seg_end:.2f}s")
    j = int(start * SR)
    track[j: j + len(x)] += x
    line["start"], line["end"] = round(start, 2), round(end - 2 * pad / sr, 2)
    src = re.sub(r'(\{ "seg": %d,\s+"start": )[\d.]+(, "end": )[\d.]+' % k,
                 lambda m: f'{m.group(1)}{line["start"]}{m.group(2)}{line["end"]}', src)
    print(f"{i:2d}  {line['start']:6.2f} -> {line['end']:6.2f}  {line['text']}")

track = track / np.abs(track).max() * 0.9
with wave.open(os.path.join(HERE, "voiceover.wav"), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((track * 32767).astype(np.int16).tobytes())
open(os.path.join(HERE, "timeline.js"), "w").write(src)
print("wrote reel/voiceover.wav and narration timings in timeline.js")
