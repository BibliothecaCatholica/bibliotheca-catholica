// Design budgets (docs/DESIGN.md, owner-approved pass 2026-11-12). The work page is rendered by
// scripts/library.js, so it runs here against the real data with a minimal DOM stand-in.
const test=require('node:test');const assert=require('node:assert');const fs=require('fs');const vm=require('vm');

function load(){
 const win={};
 const ctx={window:win,document:{getElementById:()=>null,addEventListener(){},querySelector:()=>null,body:{classList:{add(){},remove(){}}}},location:{hash:''},localStorage:{getItem:()=>null,setItem(){}},console};
 win.document=ctx.document;win.location=ctx.location;
 for(const f of ['data/library.js','data/reading-options.js','data/isidore-matches.js','data/librivox.js','data/print-editions.js','data/text-pages.js','data/editorial-flags.js','scripts/rights.js','scripts/library.js'])
  vm.runInNewContext(fs.readFileSync(f,'utf8'),ctx,{filename:f});
 return win;
}
const W=load();
function workHtml(id){let out='';W.BCLibrary.work(h=>{out=h},id);return out}
const count=(h,re)=>(h.match(re)||[]).length;
const filled=h=>count(h,/class="btn(?: [^"]*)?"/g)-count(h,/class="btn [^"]*\bghost\b[^"]*"/g);
const buttons=h=>count(h,/<(?:a|button)\b[^>]*class="(?:btn|rb-btn)\b[^"]*"/g)+count(h,/<button\b(?![^>]*class=)/g);

test('every work page has at most one filled button and at most six buttons',()=>{
 const ids=W.LIBRARY_DATA.works.map(w=>w.id);assert.ok(ids.length>100);
 for(const id of ids){const h=workHtml(id);assert.ok(h.length>0,id);assert.ok(filled(h)<=1,id+': '+filled(h)+' filled buttons');assert.ok(buttons(h)<=6,id+': '+buttons(h)+' buttons')}
});
test('a hosted work leads with one "Read here" and keeps its rights evidence behind a disclosure',()=>{
 const h=workHtml('confessions');
 assert.match(h,/<a class="btn" href="#\/read\/confessions\/pg-3296">Read here<\/a>/);
 assert.ok(h.indexOf('Read here')<h.indexOf('Other ways to read'));
 assert.match(h,/<details class="ed-details"><summary>Source and rights details<\/summary>/);
 const e=W.LIBRARY_DATA.works.find(w=>w.id==='confessions').editions[0];
 assert.ok(h.includes(e.checked)&&h.includes('Source checked'),'checked date stays on the page');
 for(const way of ['Listen','Download','Buy in print','Find in a library'])assert.ok(h.includes('<h3>'+way+'</h3>'),way);
 // the FTC line appears once, inside the purchase block, beside the affiliate links
 assert.equal(count(h,/Some links are affiliate links/g),1);
});
test('no bordered card inside a bordered panel on work pages',()=>{
 // rows use hairline dividers; the only bordered boxes left are context notes (.ef-box) and the
 // "not available here" callout, and neither ever holds another bordered element.
 for(const w of W.LIBRARY_DATA.works){const h=workHtml(w.id);
  assert.equal(count(h,/class="(?:panel|library-card|download-panel)\b/g),0,w.id);
  for(const box of h.match(/<div class="ef-box">[^]*?<\/div>/g)||[])assert.ok(!/class="(?:panel|ef-box|callout|btn)/.test(box.slice(20)),w.id)}
});
test('the reader keeps its storage keys and anchors',()=>{
 const lib=fs.readFileSync('scripts/library.js','utf8'),rd=fs.readFileSync('scripts/reader.js','utf8');
 for(const k of ["'bc-reading:'","'bc:'+setting[0]",'id="reader-size"','id="reader-spacing"','id="reader-part"',"' id=\"reading-p-'+i+'\"'"])assert.ok(lib.includes(k),k);
 for(const k of ["NOTES_PREFIX='bc-notes:'","RECENT_KEY='bc-recent'",'rb-aa-menu'])assert.ok(rd.includes(k),k);
});
