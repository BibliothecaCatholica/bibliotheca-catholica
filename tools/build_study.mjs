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
// rebuild is byte-identical on CI and locally.
rmSync('pagefind', {recursive: true, force: true});
const {index, errors: createErrors} = await createIndex({forceLanguage: 'en'});
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
// Stable trailing newline for the JSON entry (Pagefind omits it).
writeFileSync('pagefind/pagefind-entry.json', JSON.stringify(entry) + '\n');
console.log('Pagefind deterministic index:', lang.hash, '(' + lang.page_count + ' pages)');

rmSync('.study-index', {recursive: true, force: true});
rmSync('pagefind-api-test', {recursive: true, force: true});
