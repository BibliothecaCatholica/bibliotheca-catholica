import {execFileSync} from 'node:child_process';
import {copyFileSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {build} from 'esbuild';
import {createIndex, close} from 'pagefind';

mkdirSync('assets/study', {recursive: true});
mkdirSync('assets/libraries', {recursive: true});
await build({entryPoints: ['src/libraries/desk.js'], bundle: true, format: 'iife', outfile: 'assets/libraries/desk.js', minify: true});
copyFileSync('node_modules/fuse.js/LICENSE', 'assets/libraries/Fuse-LICENSE');
await build({entryPoints: ['src/study/tools.js'], bundle: true, format: 'iife', outfile: 'assets/study/tools.js', minify: true});
copyFileSync('node_modules/mirador/dist/mirador.min.js', 'assets/study/mirador.js');
execFileSync('python3', ['tools/build_study.py'], {stdio: 'inherit'});

// Pagefind's CLI directory walk does not sort files, so page numbers (and thus
// index hashes) follow filesystem readdir order and differ between machines
// (Pagefind #1395). Index through the JS API in sorted sourcePath order so a
// rebuild is byte-identical on CI and locally. maxFragments: 500 bundles the
// ~3.8k Study sections into ≤500 .pf_fragment files (Pagefind 1.6.0) so Cloudflare
// Pages Free stays under the 20k-file deploy cap.
rmSync('pagefind', {recursive: true, force: true});
const {index, errors: createErrors} = await createIndex({forceLanguage: 'en', maxFragments: 500});
if (createErrors?.length) {
  throw new Error(createErrors.join('\n'));
}
const files = readdirSync('.study-index').filter((f) => f.endsWith('.html')).sort();
for (const file of files) {
  const content = readFileSync(join('.study-index', file), 'utf8');
  const {errors} = await index.addHTMLFile({sourcePath: file, content});
  if (errors?.length) {
    throw new Error(file + ': ' + errors.join('\n'));
  }
}
const {errors: writeErrors} = await index.writeFiles({outputPath: 'pagefind'});
if (writeErrors?.length) {
  throw new Error(writeErrors.join('\n'));
}
await close();

const entry = JSON.parse(readFileSync('pagefind/pagefind-entry.json', 'utf8'));
const lang = entry.languages.en;
if (!lang || lang.page_count !== files.length) {
  throw new Error('Pagefind indexed ' + (lang && lang.page_count) + ' pages, expected ' + files.length);
}
// Pagefind 1.6.0 with maxFragments writes .pf_fragment under pagefind/fragment/.
function countExt(dir, ext) {
  let n = 0;
  for (const name of readdirSync(dir, {withFileTypes: true})) {
    const p = join(dir, name.name);
    if (name.isDirectory()) n += countExt(p, ext);
    else if (name.name.endsWith(ext)) n += 1;
  }
  return n;
}
const fragmentCount = countExt('pagefind', '.pf_fragment');
if (fragmentCount > 500 || fragmentCount < 1) {
  throw new Error('Expected 1–500 .pf_fragment files after maxFragments, got ' + fragmentCount);
}
// Stable trailing newline for the JSON entry (Pagefind omits it).
writeFileSync('pagefind/pagefind-entry.json', JSON.stringify(entry) + '\n');
console.log('Pagefind deterministic index:', lang.hash, '(' + lang.page_count + ' pages, ' + fragmentCount + ' fragments)');

rmSync('.study-index', {recursive: true, force: true});
rmSync('pagefind-api-test', {recursive: true, force: true});
