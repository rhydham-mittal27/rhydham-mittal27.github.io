// Renders reel.html frame-by-frame with headless Chromium and encodes an
// Instagram/TikTok/Shorts-ready MP4 (1080x1920, 30fps, H.264 + AAC).
//
//   node reel/render.mjs                 -> reel/rhydham-reel.mp4 (+ cover.jpg)
//   node reel/render.mjs --stills 0,2.5  -> reel/build/still-<t>.jpg previews
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(path.join(process.execPath, '../../lib/node_modules/playwright'))); }

const dir = path.dirname(fileURLToPath(import.meta.url));
const build = path.join(dir, 'build');
mkdirSync(build, { recursive: true });
const TL = JSON.parse(readFileSync(path.join(dir, 'timeline.js'), 'utf8').replace(/^window\.TL\s*=\s*/, '').replace(/;\s*$/, ''));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(path.join(dir, 'reel.html')).href + '?render=1');
await page.evaluate(() => document.fonts.ready);
await page.waitForFunction(() => [...document.images].every(i => i.complete));

const shot = async t => { await page.evaluate(t => window.render(t), t); return page.screenshot({ type: 'jpeg', quality: 94 }); };

const stillsArg = process.argv.indexOf('--stills');
if (stillsArg > -1) {
  for (const t of process.argv[stillsArg + 1].split(',').map(Number)) {
    await page.evaluate(t => window.render(t), t);
    await page.screenshot({ path: path.join(build, `still-${t}.jpg`), type: 'jpeg', quality: 85 });
  }
  await browser.close();
  process.exit(0);
}

const audio = path.join(build, 'soundtrack.wav');
const out = path.join(dir, 'rhydham-reel.mp4');
const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(TL.fps), '-c:v', 'mjpeg', '-i', '-'];
if (existsSync(audio)) args.push('-i', audio);
args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(TL.fps));
if (existsSync(audio)) args.push('-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest');
args.push('-movflags', '+faststart', out);
const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });

const frames = Math.round(TL.duration * TL.fps);
for (let f = 0; f < frames; f++) {
  const buf = await shot(f / TL.fps);
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (f % 60 === 0) process.stdout.write(`frame ${f}/${frames}\n`);
}
ff.stdin.end();
await new Promise((res, rej) => ff.on('close', c => c ? rej(new Error('ffmpeg exit ' + c)) : res()));

// Cover image: the "6 WEEKS. SOLO." hook frame — pick it as the Reel cover.
await page.evaluate(() => window.render(1.5));
await page.screenshot({ path: path.join(dir, 'cover.jpg'), type: 'jpeg', quality: 92 });
await browser.close();
console.log('wrote', out);
