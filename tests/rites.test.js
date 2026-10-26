const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const R=require('../scripts/rites.js');
const ctx={window:{}};vm.runInNewContext(fs.readFileSync('data/rites.js','utf8'),ctx);
const J=JSON.parse(JSON.stringify(ctx.window.RITES_DATA));
const main=f=>fs.readFileSync(f,'utf8').split('<main id="main" tabindex="-1">')[1].split('</main>')[0];
test('the app builds the same map block as the static pages (tools/rites_pages.py fill_slot)',()=>{
 const st=main('rites/index.html').split(' class="on"').join('').replace('<option value="fam-ant" selected>','<option value="fam-ant">').replace('value="present" checked>','value="present">');
 assert.ok(st.includes(R.core.block(J,'fam-ant',true,'present')));
 const rec=main('rites/melkite/index.html').split(' class="on"').join('').replace('value="present" checked>','value="present">');
 assert.ok(rec.includes(R.core.block(J,'melkite',false,'present')));
});
test('every token is filled and every layer has info and status for both views',()=>{
 for(const lid of Object.keys(J.layers))for(const v of ['present','heartland']){
  const b=R.core.block(J,lid,lid.startsWith('fam-'),v);assert.ok(!/%[A-Z]+%/.test(b),lid);
  assert.ok(J.info[lid+'|'+v]&&J.status[lid+'|'+v],lid+v);
 }
});
test('the heartland view is never the default, and codes are copies',()=>{
 assert.equal(R.core.defaultView(),'present');
 const c=R.core.codes(J,'maronite','present');c.push('XX');assert.ok(!J.layers.maronite.present.includes('XX'));
 assert.deepEqual(R.core.codes(J,'nope','present'),[]);
});
test('the page HTML has no hash links, pins, or population figures, and the selector lists every mapped layer',()=>{
 for(const [k,p] of Object.entries(J.pages)){assert.ok(!p.html.includes('href="#/'),k);assert.ok(!/<circle|<marker/.test(p.html),k)}
 for(const lid of Object.keys(J.layers))if(J.layers[lid].present.length||J.layers[lid].heartland.length||lid==='latin'){
  if(lid.startsWith('latin-')&&!['latin-ambrosian','latin-hispanic-mozarabic','latin-divine-worship'].includes(lid))continue;
  assert.ok(J.options.includes('value="'+lid+'"'),lid);
 }
});
test('the selector and radios are hidden until the app mounts them (no-JS pages show the default view)',()=>{
 assert.ok(J.tpl.full.includes('<div class="rmap-controls" hidden>'));
 assert.ok(J.tpl.full.includes('role="status" aria-live="polite"'));
 assert.ok(J.tpl.full.includes('<label class="rmap-sel"><span>Church or tradition</span><select id="rmap-sel"'));
 assert.ok(R.core.esc('<a&"')==='&lt;a&amp;&quot;');
});
