// Generates each narration line with Kokoro-82M (local, offline) into reel/build/vo/.
//   KOKORO_DIR=<dir with node_modules/kokoro-js and model/> node reel/tts.mjs
// <dir>/model must hold config.json, tokenizer.json, tokenizer_config.json and
// onnx/model_quantized.onnx (onnx-community/Kokoro-82M-v1.0-ONNX).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const K = process.env.KOKORO_DIR;
if (!K) throw new Error('set KOKORO_DIR');
const mod = p => import(pathToFileURL(path.join(K, 'node_modules', p)).href);
const { KokoroTTS } = await mod('kokoro-js/dist/kokoro.js');
const { env } = await mod('@huggingface/transformers/dist/transformers.node.mjs');
env.allowRemoteModels = false;
env.localModelPath = K + '/';

const TL = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.js'), 'utf8').replace(/^window\.TL\s*=\s*/, '').replace(/;\s*$/, ''));
const out = path.join(dir, 'build', 'vo');
fs.mkdirSync(out, { recursive: true });
const tts = await KokoroTTS.from_pretrained('model', { dtype: 'q8', device: 'cpu' });
for (const [i, l] of TL.narration.entries()) {
  const a = await tts.generate(l.say, { voice: TL.voice, speed: l.speed ?? 1 });
  a.save(path.join(out, `line-${i}.wav`));
  console.log(i, (a.audio.length / a.sampling_rate).toFixed(2) + 's', l.say);
}
