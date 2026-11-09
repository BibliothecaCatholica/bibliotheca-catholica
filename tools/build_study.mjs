import {execFileSync} from 'node:child_process';
import {copyFileSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {build} from 'esbuild';
mkdirSync('assets/study',{recursive:true});
await build({entryPoints:['src/study/tools.js'],bundle:true,format:'iife',outfile:'assets/study/tools.js',minify:true});
copyFileSync('node_modules/mirador/dist/mirador.min.js','assets/study/mirador.js');
execFileSync('python3',['tools/build_study.py'],{stdio:'inherit'});
rmSync('pagefind',{recursive:true,force:true});
execFileSync('node_modules/.bin/pagefind',['--site','.study-index','--output-path','pagefind'],{stdio:'inherit'});

rmSync('.study-index',{recursive:true,force:true});
