# Rhydham — lead-gen reel

**Video:** [`rhydham-reel.mp4`](rhydham-reel.mp4) — 26 s, 1080×1920 (9:16), 30 fps, H.264 + AAC, loudness-normalised to −14 LUFS.
**Cover:** [`cover.jpg`](cover.jpg) (the "6 WEEKS. SOLO." frame). Upload it as the Reel cover.

Everything here is original: the motion graphics, the music and the sound effects are generated from code, so there are no copyright or music-licensing issues on Instagram, YouTube Shorts, TikTok or LinkedIn.

## Why it's built this way (research-backed)

| Rule | How the reel does it |
|---|---|
| The first 3 s decide distribution; ~45% of viewers leave in that window | Frame 0 already shows the payoff, **"6 WEEKS."**, which slams in at 0.3 s with an impact and a camera shake. No logo intro and no throat-clearing. |
| A face within the first 3 s gives about 35% more retention | Your photo rises in at 2.1 s. |
| Most people watch muted, and about 80% are more likely to finish with captions | Word-by-word **dictation captions** follow the narration script, and every claim is also shown as on-screen text. |
| Pattern interrupts and cuts every 1.5–2.5 s | 11 cuts in 26 s. Wipes, flash-cuts, a background colour change on the proof cards, and a beat drop before the CTA. |
| Edits synced to the beat | 120 BPM track. Every slam, pop and cut lands on a cue from `timeline.js`. |
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

## Add your own voice (recommended)

A real voice, your own, builds more trust than any AI voice. Read this script at an energetic pace, about 3.5 words per second. Each line has to fit its time window, and the captions already follow these timings:

| Time | Say |
|---|---|
| 0.0 – 1.9 | Six weeks. Idea to live product. |
| 2.1 – 3.9 | Hi, I'm Rhydham. Full-stack engineer and founder. |
| 4.1 – 6.9 | I build the whole thing: frontend, backend, database, SEO. Shipped. |
| 7.1 – 10.4 | My startup MentalSaathi hit fifteen hundred visitors in month one. Zero ad spend. |
| 10.6 – 12.9 | CollabFluenz: built for a founder. Live in production. |
| 13.1 – 14.3 | Zero-downtime database migration. |
| 14.4 – 15.6 | Ninety-one percent accurate sign-language AI. |
| 15.75 – 16.9 | My own open-source framework. |
| 17.1 – 18.9 | Next.js, FastAPI, Postgres. One dev, full stack. |
| 19.1 – 21.4 | Weekly builds you can click. Not status updates. |
| 22.1 – 25.3 | Got something that needs building? Comment BUILD and I'll DM you. |
| 25.5 – 26.0 | Your idea, live in… |

Then **either**:
- **Quick:** record it in Instagram's Reels editor (*Voiceover*) over the uploaded video, or use Instagram's or CapCut's text-to-speech on the script; **or**
- **Best:** save the recording as `reel/voiceover.wav` (16-bit WAV, starting at 0:00) and rebuild. The music automatically ducks under your voice.

## Rebuild / edit

Requires Python 3 with `numpy` and `scipy`, Node with `playwright` (Chromium), and `ffmpeg`.

```bash
python3 reel/audio.py      # music + SFX (+ voiceover.wav if present) -> reel/build/soundtrack.wav
node reel/render.mjs       # frames -> reel/rhydham-reel.mp4 + reel/cover.jpg   (~2.5 min)
node reel/render.mjs --stills 0,3.5,9.6   # quick still previews in reel/build/
```

- **Text, timings, SFX cues and captions:** edit `timeline.js`. The visuals and audio both read from it.
- **Visuals:** edit `reel.html`. Open it in a browser and click to preview live with sound, after running `audio.py`.
