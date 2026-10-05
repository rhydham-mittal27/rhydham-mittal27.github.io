"""Synthesizes the reel soundtrack (original, royalty-free) from timeline.js.

Music: 120 BPM A-minor beat (kick, clap, hats, bass, pad, arp) with a
breakdown + riser before the CTA drop. SFX are placed on the cues in
timeline.js so every cut, slam and pop is on-beat with the visuals.

If reel/voiceover.wav exists (your own recording of the script in README.md),
it is mixed on top and the music is side-chain ducked under the voice.

    python3 reel/audio.py   ->  reel/build/soundtrack.wav
"""
import json
import os
import re
import wave

import numpy as np
from scipy.signal import butter, sosfilt, resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
TL = json.loads(re.sub(r"^window\.TL\s*=\s*|;\s*$", "", open(os.path.join(HERE, "timeline.js")).read().strip()))
DUR = TL["duration"]
N = int(DUR * SR)
BEAT = 60 / TL["bpm"]
BAR = BEAT * 4
rng = np.random.default_rng(7)


def t_arr(sec):
    return np.arange(int(sec * SR)) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def place(buf, sig, at, gain=1.0):
    """Add sig into buf (stereo or mono-broadcast) at time `at`, wrapping past the end so the loop seam is clean."""
    i = int(at * SR) % N
    sig = sig * gain
    if sig.ndim == 1:
        sig = np.stack([sig, sig], 1)
    end = i + len(sig)
    if end <= N:
        buf[i:end] += sig
    else:
        buf[i:] += sig[: N - i]
        buf[: end - N] += sig[N - i:]


def noise(sec):
    return rng.standard_normal(int(sec * SR))


# ---------------- instruments ----------------
def kick():
    t = t_arr(0.45)
    f = 48 + 110 * np.exp(-t * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    click = hp(noise(0.45), 2000) * np.exp(-t * 300) * 0.4
    return np.tanh((body + click) * 1.6)


def clap():
    t = t_arr(0.35)
    env = np.exp(-t * 22) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    return bp(noise(0.35), 900, 4500) * env * 0.55


def hat(open_=False):
    t = t_arr(0.3 if open_ else 0.06)
    return hp(noise(len(t) / SR), 7500) * np.exp(-t * (14 if open_ else 70)) * 0.22


def saw(freq, sec, detune=0.0):
    t = t_arr(sec)
    out = np.zeros_like(t)
    for d in (-detune, 0, detune) if detune else (0,):
        ph = (t * freq * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / (3 if detune else 1)


def note(midi):
    return 440 * 2 ** ((midi - 69) / 12)


# A minor: Am F C G  (roots / triads in MIDI)
CHORDS = [(45, [57, 60, 64]), (41, [57, 60, 65]), (36, [55, 60, 64]), (43, [55, 59, 62])]


def build_music():
    mus = np.zeros((N, 2))
    drums = np.zeros((N, 2))
    k, c = kick(), clap()
    b0, b1 = TL["breakdown"]
    nbeats = int(round(DUR / BEAT))
    kick_times = []
    for b in range(nbeats):
        tb = b * BEAT
        if b0 <= tb < b1:
            continue
        place(drums, k, tb, 0.95)
        kick_times.append(tb)
        if b % 2 == 1:
            place(drums, c, tb, 0.8)
        # hats: offbeat 8ths, plus 16ths in the high-energy sections
        place(drums, hat(open_=(b % 4 == 3)), tb + BEAT / 2, 1.0)
        if 13 <= tb < 19 or tb >= 22:
            place(drums, hat(), tb + BEAT / 4, 0.55)
            place(drums, hat(), tb + 3 * BEAT / 4, 0.55)

    nbars = int(np.ceil(DUR / BAR))
    for bar in range(nbars):
        root, triad = CHORDS[bar % 4]
        tb = bar * BAR
        # pad (whole bar, stereo detune)
        pad_l = sum(saw(note(m), BAR, 0.004) for m in triad)
        pad_r = sum(saw(note(m) * 1.003, BAR, 0.005) for m in triad)
        env = np.minimum(1, t_arr(BAR) / 0.05) * np.minimum(1, (BAR - t_arr(BAR)) / 0.1)
        pad = np.stack([lp(pad_l, 1400), lp(pad_r, 1400)], 1) * env[:, None] * 0.07
        place(mus, pad, tb)
        # bass: 8th-note pluck
        for e in range(8):
            ts = tb + e * BEAT / 2
            if b0 <= ts < b1:
                continue
            tt = t_arr(BEAT / 2)
            s = lp(saw(note(root + 12), BEAT / 2), 900) + 0.5 * np.sin(2 * np.pi * note(root) * tt)
            place(mus, s * np.exp(-tt * 6) * 0.32, ts)
        # arp: 16ths in build / stack / CTA sections
        for s16 in range(16):
            ts = tb + s16 * BEAT / 4
            if not (4 <= ts < 7 or 17 <= ts < 19 or 22 <= ts < 25.5):
                continue
            m = (triad + [triad[0] + 12])[s16 % 4] + 12
            tt = t_arr(BEAT / 4)
            sig = np.sin(2 * np.pi * note(m) * tt) + 0.3 * np.sin(4 * np.pi * note(m) * tt)
            pan = 0.5 + 0.35 * np.sin(s16)
            place(mus, np.stack([sig * (1 - pan), sig * pan], 1) * np.exp(-tt * 18)[:, None] * 0.16, ts)

    # side-chain pump on music from the kick
    duck = np.ones(N)
    for tk in kick_times:
        i = int(tk * SR)
        L = int(0.22 * SR)
        seg = 1 - 0.55 * np.exp(-np.arange(L) / SR * 14)
        j = min(N, i + L)
        duck[i:j] = np.minimum(duck[i:j], seg[: j - i])
    mus *= duck[:, None]
    # breakdown: filter the music down to a muffled pad
    i0, i1 = int(b0 * SR), int(b1 * SR)
    mus[i0:i1] = np.stack([lp(mus[i0:i1, 0], 500), lp(mus[i0:i1, 1], 500)], 1) * 0.7
    return mus + drums


# ---------------- sfx ----------------
def whoosh(sec=0.4):
    t = t_arr(sec)
    n = noise(sec)
    out = np.zeros_like(n)
    blocks = 24
    L = len(n) // blocks
    for b in range(blocks):
        f = 400 * (12 ** (b / blocks))
        seg = n[b * L:(b + 1) * L]
        out[b * L:(b + 1) * L] = bp(seg, f * 0.7, min(f * 1.6, 20000))
    env = np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2
    return out * env * 0.5


def impact():
    t = t_arr(1.2)
    boom = np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t * 18)) / SR) * np.exp(-t * 3.2)
    crack = lp(noise(1.2), 3000) * np.exp(-t * 25) * 0.6
    return np.tanh((boom + crack) * 1.4) * 0.8


def stamp():
    t = t_arr(0.35)
    return (np.sin(2 * np.pi * np.cumsum(90 + 200 * np.exp(-t * 40)) / SR) * np.exp(-t * 12)
            + bp(noise(0.35), 800, 3000) * np.exp(-t * 35) * 0.6) * 0.7


def pop():
    t = t_arr(0.09)
    return np.sin(2 * np.pi * np.cumsum(1100 * np.exp(-t * 18) + 380) / SR) * np.exp(-t * 45) * 0.45


def tick():
    t = t_arr(0.05)
    return (np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 120) + hp(noise(0.05), 4000) * np.exp(-t * 200) * 0.3) * 0.35


def key_click():
    t = t_arr(0.03)
    return (bp(noise(0.03), 1500, 6000) * np.exp(-t * 260) + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 200) * 0.4) * 0.5


def chime():
    t = t_arr(1.0)
    return sum(np.sin(2 * np.pi * f * t) * a for f, a in ((1318.5, 1), (1975.5, .6), (2637, .3))) * np.exp(-t * 4.5) * 0.18


def slam_sfx():
    return 0.55 * stamp() + 0.3 * np.pad(pop(), (0, len(stamp()) - len(pop())))


def riser(sec):
    t = t_arr(sec)
    n = noise(sec)
    out = np.zeros_like(n)
    blocks = 40
    L = len(n) // blocks
    for b in range(blocks):
        f = 300 * (25 ** (b / blocks))
        out[b * L:(b + 1) * L] = bp(n[b * L:(b + 1) * L], f * .8, min(f * 1.3, 20000))
    tone = np.sin(2 * np.pi * np.cumsum(200 * (8 ** (t / sec))) / SR) * 0.25
    return (out + tone) * (t / sec) ** 2 * 0.55


def build_sfx():
    fx = np.zeros((N, 2))
    for c in TL["cuts"]:
        w = whoosh(0.4)
        place(fx, np.stack([w * .8, w], 1), c - 0.3, 0.9)
    for cue in TL["sfx"]:
        ty, at = cue["type"], cue["t"]
        if ty == "impact":
            place(fx, impact(), at)
        elif ty == "stamp":
            place(fx, stamp(), at)
        elif ty == "pop":
            place(fx, pop(), at)
        elif ty == "tick":
            place(fx, tick(), at)
        elif ty == "chime":
            place(fx, chime(), at)
        elif ty == "slam":
            place(fx, slam_sfx(), at, 0.8)
        elif ty == "riser":
            place(fx, riser(cue["dur"]), at)
        elif ty == "typing":
            for i in range(cue["chars"]):
                place(fx, key_click(), at + cue["dur"] * i / cue["chars"] + rng.uniform(-.008, .008), rng.uniform(.6, 1))
        elif ty == "ticks":
            for i in range(14):
                place(fx, tick(), at + cue["dur"] * i / 14, 0.6)
    return fx


def read_wav(path):
    with wave.open(path) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2:
        raise SystemExit("voiceover.wav must be 16-bit PCM (export as WAV 16-bit)")
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    x = x.reshape(-1, ch).mean(1)
    if sr != SR:
        x = resample_poly(x, SR, sr)
    return x


def main():
    music = build_music()
    fx = build_sfx()
    mix = music * 0.8 + fx * 0.9
    vo_path = os.path.join(HERE, "voiceover.wav")
    if os.path.exists(vo_path):
        vo = read_wav(vo_path)[:N]
        vo = np.pad(vo, (0, N - len(vo)))
        vo = vo / (np.abs(vo).max() + 1e-9) * 0.9
        # envelope follower -> duck music ~9 dB while speaking
        env = np.convolve(np.abs(vo), np.ones(int(0.05 * SR)) / int(0.05 * SR), "same")
        duck = 1 - 0.65 * np.clip(env / 0.05, 0, 1)
        mix = mix * duck[:, None] + np.stack([vo, vo], 1)
        print("mixed voiceover.wav")
    mix = np.tanh(mix * 1.1)
    mix = mix / np.abs(mix).max() * 0.93
    out = os.path.join(HERE, "build", "soundtrack.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main()
