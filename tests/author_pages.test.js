/* Phase A item 2: app.js auIntro() gives the same intro as the static author pages (tools/author_pages.py intro()),
   for every author with no hosted work, and those authors never show the Wikipedia excerpt in the app. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function fn(src,name){const i=src.indexOf('function '+name+'(');assert(i>=0,name);let d=0,q=null;
 for(let j=src.indexOf('{',i);j<src.length;j++){const c=src[j];
  if(q){if(c==='\\')j++;else if(c===q)q=null;continue}
  if(c==="'"||c==='"')q=c;else if(c==='{')d++;else if(c==='}'&&--d===0)return src.slice(i,j+1)}}
const APP=fs.readFileSync('app.js','utf8');
const jsvar=(f)=>{const s=fs.readFileSync(f,'utf8');return JSON.parse(s.slice(s.indexOf('=')+1).trim().replace(/;$/,''))};
const hub=JSON.parse(fs.readFileSync('data/catholic-hub.json','utf8'));
const lib=JSON.parse(fs.readFileSync('data/library.json','utf8'));
const R=JSON.parse(fs.readFileSync('data/books.json','utf8'));
const flags=JSON.parse(fs.readFileSync('data/editorial-flags.json','utf8'));
const GD=jsvar('data/guide.js');
const ctx={window:{LIBRARY_DATA:lib}};vm.createContext(ctx);
vm.runInContext([/var AU_ROLE=\{[^\n]*\};/.exec(APP)[0],...['auHosted','auOxford','auIntro'].map(n=>fn(APP,n))].join('\n'),ctx);
const unesc=s=>s.replace(/&#x27;/g,"'").replace(/&quot;/g,'"').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');
const ERA={};hub.eras.forEach(e=>{ERA[e.id]=e.label});
const BY={};R.books.forEach(b=>{if(flags.books[String(b[0])])return;b[2].forEach(i=>{const h=R.authors[i][1];if(h)BY[h]=(BY[h]||0)+1})});
const skip=new Set(flags.hubAuthors||[]);
const noHosted=hub.authors.filter(a=>!skip.has(a.id)&&!ctx.auHosted(a.id));
test('454 authors have no hosted work; 22 do',()=>{assert.equal(noHosted.length,454)});
test('auIntro() matches the static intro on every page without a hosted work',()=>{
 for(const a of noHosted){
  const html=fs.readFileSync('author/'+a.id+'/index.html','utf8');
  const m=/<p class="au-intro">([^<]*)<\/p>/.exec(html);assert(m,a.id);
  const js=ctx.auIntro(a,ERA[a.era]||'',BY[a.id]||0,GD.editions.filter(e=>e.aid===a.id).length,a.works.filter(w=>w.url).length);
  assert.equal(js,unesc(m[1]),a.id)}});
test('the four rebuilt pages carry hand-written intros',()=>{
 for(const id of ['trent-horn','thomas-e-woods','warren-h-carroll','scott-hahn']){
  const a=hub.authors.find(x=>x.id===id);assert(a.intro&&a.intro.length>120,id);assert(!/—/.test(a.intro),id)}});
test('the app shows the intro, not the Wikipedia excerpt, for authors with no hosted work',()=>{
 assert.match(APP,/\(!auHosted\(a\.id\)\?'<p class="au-intro" id="au-intro">'\+esc\(a\.intro\|\|''\)\+'<\/p>':a\.extract\?/)});
