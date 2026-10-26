/* v18.2: every Isidore Index author link (the 211 author pages and the 3,352 Authors A-Z entries) finds at least one book.
   Runs the app's own norm, isoNorm, prepBooks, offTopic, and isoAuthorHref, and the books() route parsing rules. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function fn(src,name){const i=src.indexOf('function '+name+'(');assert(i>=0,name);let d=0,q=null;
 for(let j=src.indexOf('{',i);j<src.length;j++){const c=src[j];
  if(q){if(c==='\\')j++;else if(c===q)q=null;continue}
  if(c==="'"||c==='"')q=c;else if(c==='{')d++;else if(c==='}'&&--d===0)return src.slice(i,j+1)}}
const APP=fs.readFileSync('app.js','utf8');
const line=re=>{const m=re.exec(APP);assert(m,String(re));return m[0]};
const hub=JSON.parse(fs.readFileSync('data/catholic-hub.json','utf8'));
const R=JSON.parse(fs.readFileSync('data/books.json','utf8'));
const ctx={AID:{},window:{}};vm.createContext(ctx);
vm.runInContext([line(/var FOLD=\{[^\n]*\};/),line(/var OFFT=[^\n]*;/),line(/var RELT=[^\n]*;/),
 ...['norm','isoNorm','predSub','prepBooks','offTopic','isoName','isoAuthorHref'].map(n=>fn(APP,n)),
 'var B=prepBooks(R);'].join('\n'),Object.assign(ctx,{R}));
// the books() route: "author=<name>" searches <name> with the off-topic filter off; any other arg keeps it on
function hits(href){const arg=decodeURIComponent(href.replace(/^#\/isidore\//,''));const m=/^author=(.*)$/.exec(arg);
 const q=m?m[1]:arg,ontopic=!m,toks=ctx.isoNorm(q).split(/\s+/).filter(Boolean);
 return ctx.B.list.filter(b=>!(ontopic&&ctx.offTopic(b))&&toks.every(t=>b.x.indexOf(t)>=0)).length}
test('books() reads author= links as a search with the off-topic filter off',()=>{
 assert.match(APP,/if\(m&&m\[1\]==='author'\)\{BF\.q=m\[2\];BF\.ontopic=false;authorArg=true\}/)});
test('v18.3: an author= link sends no GA search event; a q= or typed search still does',()=>{
 const b=fn(APP,'books');
 assert.match(b,/var qArg=false,authorArg=false;/);
 // only q= (or a bare term) sets qArg, which is what sends the search event on load
 assert.doesNotMatch(b.match(/if\(m&&m\[1\]==='author'\)\{[^}]*\}/)[0],/qArg/);
 assert.match(b,/if\(qArg\)trackQ\(\);/);
 assert.match(b,/else if\(m\)\{BF\[m\[1\]==='q'\?'q':m\[1\]\]=m\[2\];qArg=m\[1\]==='q'\}else\{BF\.q=arg;qArg=true\}/);
 // the author name counts as already seen, so it is not sent later unless the reader changes the query
 assert.match(b,/var lastTerm=authorArg\?cleanTerm\(BF\.q\):'';function trackQ\(\)\{var t=cleanTerm\(BF\.q\);if\(t\.length<2\|\|t===lastTerm/);
 assert.equal((b.match(/track\('search'/g)||[]).length,1)});
test('the Isidore search folds ł, ø, đ, æ, œ, ß and treats ?/_ in dates like .',()=>{
 assert.equal(ctx.norm('Wojtyła Søren Đorđe Ælfric Œuvres Straße'),'wojtyla soren dorde aelfric oeuvres strasse');
 assert.equal(ctx.isoNorm('1248?-1309'),ctx.isoNorm('1248.-1309'));assert.equal(ctx.isoNorm('1232_-1316'),'1232.-1316')});
test('the three named author links QA found empty now find books',()=>{
 for(const id of ['john-paul-ii','angela-of-foligno','ramon-llull']){const a=hub.authors.find(x=>x.id===id);
  const i=hub.isidore.find(x=>x.f===a.isidoreFolder);assert(i,id);assert(hits(ctx.isoAuthorHref(i))>0,id)}});
test('all 211 author-page links and all A-Z entries return at least one book',()=>{
 const folders=hub.authors.filter(a=>a.isidoreFolder);assert.equal(folders.length,211);
 const empty=[];for(const a of folders){const i=hub.isidore.find(x=>x.f===a.isidoreFolder);if(!i||!hits(ctx.isoAuthorHref(i)))empty.push(a.id)}
 assert.deepEqual(empty,[]);
 const emptyAZ=hub.isidore.filter(i=>!hits(ctx.isoAuthorHref(i))).map(i=>i.n);
 assert.equal(hub.isidore.length,3352);assert.deepEqual(emptyAZ,[])});
test('static author pages and open data use the same author= link',()=>{
 const S=fs.readFileSync('tools/build_static.py','utf8'),O=fs.readFileSync('tools/build_open_data.py','utf8');
 assert.match(S,/'\/#\/isidore\/author='\+urllib\.parse\.quote\(iso_n,safe=''\)/);assert.match(S,/i\.get\('a'\) or i\['n'\]/);
 assert.match(O,/#\/isidore\/author='\+urllib\.parse\.quote\(i\.get\('a'\) or i\['n'\],safe=''\)/)});
