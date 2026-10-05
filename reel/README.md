# Rhydham — lead-gen reel

**Video:** [`rhydham-reel.mp4`](rhydham-reel.mp4) — 36 s, 1080×1920 (9:16), 30 fps, H.264 + AAC, loudness-normalised to −14 LUFS. Includes an AI **voiceover**, music, SFX and word-by-word captions.
**Cover:** [`cover.jpg`](cover.jpg) (the "6 WEEKS. SOLO." frame). Upload it as the Reel cover.

Everything here is original: the motion graphics, the music and the sound effects are generated from code, and the narration comes from the open Kokoro-82M voice model (Apache-2.0). There are no copyright or music-licensing issues on Instagram, YouTube Shorts, TikTok or LinkedIn.

## Why it's built this way (research-backed)

| Rule | How the reel does it |
|---|---|
| The first 3 s decide distribution; ~45% of viewers leave in that window | Frame 0 already shows the payoff, **"6 WEEKS."**, which slams in at 0.3 s with an impact and a camera shake. No logo intro and no throat-clearing. |
| A face within the first 3 s gives about 35% more retention | Your photo rises in at 2.1 s. |
| Most people watch muted, and about 80% are more likely to finish with captions | A voiceover for sound-on viewers, plus word-by-word **captions** timed to it for muted ones. Every claim is also shown as on-screen text. |
| Pattern interrupts and cuts every 1.5–2.5 s | 11 cuts in 36 s, each landing on a beat. Wipes, flash-cuts, a background colour change on the proof cards, and a beat drop before the CTA. |
| Edits synced to the beat | 120 BPM track. Scene lengths are whole beats, so every cut is on the beat. The music ducks under the voice. |
| Watch time and replays are the top ranking signals | A seamless loop: the last frame types "IDEA → LIVE PRODUCT IN…" and the first frame answers "6 WEEKS." |
| Comment-keyword CTAs convert 4–6× better than "link in bio" | The CTA is **Comment "BUILD"**, plus WhatsApp as a backup. |
| 9:16 safe zones (avoid the top ~14%, the bottom ~35% and ~6% at the sides) | All key text sits between y≈290 and y≈1260 px, clear of Instagram's buttons and caption. |

## Post it

**Caption** (keyword-first, because Instagram now ranks on caption search):

```
Full-stack developer for startups & founders 🚀
I took MentalSaathi from blank repo → live product in 6 weeks, solo. 1,500+ visitors in month one on ₹0 ads.

What I build: SaaS apps · startup MVPs · AI tools · landing pages that actually rank
Stack: Next.js · FastAPI · PostgreSQL · Supabase

💬 Comment "BUILD" and I'll DM you to scope your project.
📲 Or WhatsApp: +91 76579 71009

#fullstackdeveloper #freelancedeveloper #mvpdevelopment #startupindia #webdevelopment #nextjs #saas #indiedev
```

**Checklist**
1. Upload `rhydham-reel.mp4` and set `cover.jpg` as the cover.
2. Answer **every** "BUILD" comment with a DM within the hour. Better still, automate it with ManyChat or Instagram's built-in auto-reply, because the CTA promises a DM.
3. Optional: under *Add audio*, layer a trending track at about 10–15% volume on top of the original audio for extra reach. Keep the original sound on so the SFX still land.
4. Cross-post the same file to YouTube Shorts, LinkedIn (strong for B2B clients) and TikTok.
5. Pin the reel to the top of your profile.

## Voiceover

The narration uses Kokoro's `am_fenrir` voice. Names are spelled phonetically in `timeline.js` → `say` ("Ridham", "Mental Saathee", "Collab Fluence"), while the captions show the real spelling (`text`). Each scene stretches to fit its spoken line, with segments in `timeline.js` → `segments`.

**Want to use your own voice instead?** A founder's real voice builds the most trust. Record the `text` lines, each at the time shown in `timeline.js` → `narration` (start/end). Save the result as `reel/voiceover.wav` (16-bit WAV, starting at 0:00), then run `audio.py` and `render.mjs`. The music ducks under your voice automatically.

## Rebuild / edit

Requires Python 3 with `numpy` and `scipy`, Node with `playwright` (Chromium), and `ffmpeg`.

```bash
KOKORO_DIR=<dir> node reel/tts.mjs   # speak each narration line -> reel/build/vo/  (see tts.mjs header)
python3 reel/voice.py                # trim + place lines -> reel/voiceover.wav, caption timings -> timeline.js
python3 reel/audio.py      # music + SFX (+ voiceover.wav if present) -> reel/build/soundtrack.wav
node reel/render.mjs       # frames -> reel/rhydham-reel.mp4 + reel/cover.jpg   (~3.5 min)
node reel/render.mjs --stills 0,3.5,9.6   # quick still previews in reel/build/
```

- **Text, timings, SFX cues and captions:** edit `timeline.js`. The visuals and audio both read from it.
- **Visuals:** edit `reel.html`. Open it in a browser and click to preview live with sound, after running `audio.py`.
