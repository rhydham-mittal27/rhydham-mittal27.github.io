// Generates each narration line with Kokoro-82M (local, offline) into reel/build/vo/.
//   KOKORO_DIR=<dir with node_modules/kokoro-js and model/> node reel/tts.mjs [voice] [outDir] [lineIdx,...]
// <dir>/model must hold config.json, tokenizer.json, tokenizer_config.json and
// onnx/model_quantized.onnx (onnx-community/Kokoro-82M-v1.0-ONNX).
//
// "say" text supports inline pronunciations: [Rhydham](/ɹˈiːdəm/) speaks the
// IPA between the slashes. English is phonemized as en-us for every voice, so
// the Hindi voices (hm_omega, hm_psi, hf_alpha, hf_beta) speak English with an
// Indian accent.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const K = process.env.KOKORO_DIR;
if (!K) throw new Error('set KOKORO_DIR');
const mod = p => import(pathToFileURL(path.join(K, 'node_modules', p)).href);
const { KokoroTTS } = await mod('kokoro-js/dist/kokoro.js');
const { env } = await mod('@huggingface/transformers/dist/transformers.node.mjs');
const { phonemize } = await mod('phonemizer/dist/phonemizer.js');
env.allowRemoteModels = false;
env.localModelPath = K + '/';

const TL = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.js'), 'utf8').replace(/^window\.TL\s*=\s*/, '').replace(/;\s*$/, ''));
const voice = process.argv[2] || TL.voice;
const out = process.argv[3] || path.join(dir, 'build', 'vo');
const only = process.argv[4] ? process.argv[4].split(',').map(Number) : null;
fs.mkdirSync(out, { recursive: true });

// Same post-processing kokoro-js applies to espeak output; punctuation is kept for prosody.
const PUNCT = /(\s*[;:,.!?¡¿—…"«»“”(){}[\]]+\s*)+/g;
async function toPhonemes(text) {
  const parts = [];
  let last = 0;
  for (const m of text.matchAll(/\[([^\]]+)\]\(\/([^/]+)\/\)/g)) {
    parts.push({ text: text.slice(last, m.index) }, { ipa: m[2] });
    last = m.index + m[0].length;
  }
  parts.push({ text: text.slice(last) });
  // espeak trims whitespace, so carry the original word boundaries across.
  const words = async s => (/^\s/.test(s) ? ' ' : '') + (await phonemize(s, 'en-us')).join(' ') + (/\s$/.test(s) ? ' ' : '');
  let ps = '';
  for (const p of parts) {
    if (p.ipa) { ps += p.ipa; continue; }
    let i = 0;
    for (const m of p.text.matchAll(PUNCT)) {
      if (m.index > i) ps += await words(p.text.slice(i, m.index));
      ps += m[0];
      i = m.index + m[0].length;
    }
    if (i < p.text.length) ps += await words(p.text.slice(i));
  }
  return ps.replace(/ʲ/g, 'j').replace(/r/g, 'ɹ').replace(/x/g, 'k').replace(/ɬ/g, 'l').replace(/\s+/g, ' ').trim();
}

const tts = await KokoroTTS.from_pretrained('model', { dtype: 'q8', device: 'cpu' });
for (const [i, l] of TL.narration.entries()) {
  if (only && !only.includes(i)) continue;
  const ps = await toPhonemes(l.say);
  const { input_ids } = tts.tokenizer(ps, { truncation: true });
  const a = await tts.generate_from_ids(input_ids, { voice, speed: l.speed ?? 1 });
  a.save(path.join(out, `line-${i}.wav`));
  console.log(i, (a.audio.length / a.sampling_rate).toFixed(2) + 's', ps);
}
