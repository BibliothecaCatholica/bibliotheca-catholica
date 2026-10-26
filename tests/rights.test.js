/* v16 rights badges: no download, files, or reader links for link_only or unknown records; no hostable status without evidence. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const RT=require('../scripts/rights.js');
const RD=JSON.parse(fs.readFileSync('data/rights.json','utf8'));globalThis.RIGHTS_DATA=RD;
const lib=JSON.parse(fs.readFileSync('data/library.json','utf8'));
// pull one top-level function's source out of a file (skips string literals when matching braces)
function fn(src,name){const i=src.indexOf('function '+name+'(');assert(i>=0,name);let d=0,q=null;
 for(let j=src.indexOf('{',i);j<src.length;j++){const c=src[j];
  if(q){if(c==='\\')j++;else if(c===q)q=null;continue}
  if(c==="'"||c==='"')q=c;else if(c==='{')d++;else if(c==='}'&&--d===0)return src.slice(i,j+1)}}
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const APP=fs.readFileSync('app.js','utf8'),LIB=fs.readFileSync('scripts/library.js','utf8');
const idsBy=st=>Object.keys(RD.records).filter(i=>RT.resolve(RD,i).status===st);
const RAW=/calibre\/get\/|isidore\.co\/CalibreLibrary\/|#book_id=/;
function appCtx(){const ctx={ISO_NOTE:'Bibliotheca Catholica does not host, and does not vouch for, any file at isidore.co.',RT,esc,hl:esc,efBadge:()=>'',efOf:()=>null,efBox:()=>'',bookAuthors:()=>'',eraLabel:x=>x,LANGN:{},AID:{},avatar:()=>'',dates:()=>'',notfound:()=>{throw new Error('nf')},
  B:{server:'https://isidore.co/calibre/',base:'https://isidore.co/CalibreLibrary/',ids:{}},document:{},out:'',window:{BCLibrary:{readHere:()=>''}}};
 ctx.render=h=>{ctx.out=h};ctx.loadBooks=cb=>cb();
 ctx.encPath=encodeURIComponent;vm.runInNewContext(['bookUrl','bookFiles','bookAppUrl','rightsOf','canHost','brow','dlUrl','bookDetail'].map(n=>fn(APP,n)).join('\n'),ctx);return ctx}
function book(id){return {id:+id,t:'T'+id,a:[['A',null]],y:1900,tg:[],se:'',si:0,f:['PDF','EPUB'],fo:'A',sub:'T ('+id+')',lg:['eng'],pub:'',er:''}}
test('global RIGHTS_DATA lookups match the shipped data file',()=>{
 const c={window:{}};vm.runInNewContext(fs.readFileSync("data/rights.js","utf8"),c);assert.equal(JSON.stringify(c.window.RIGHTS_DATA),JSON.stringify(RD))});
test('only the first three statuses are hostable',()=>{
 assert.deepEqual(RT.ORDER.filter(RT.hostable),['public_domain_us','open_license','permission_granted']);
 assert.equal(RT.hostable('link_only'),false);assert.equal(RT.hostable('unknown'),false);assert.equal(RT.hostable('nonsense'),false)});
test('missing data, missing ids, and hostable codes without evidence fall back to unknown',()=>{
 assert.equal(RT.resolve(null,1).status,'unknown');assert.equal(RT.resolve(RD,99999999).status,'unknown');
 const fake={checked:'2026-10-25',codes:{P1:{status:'public_domain_us',text:'x'}},records:{1:['P1'],2:['P1','short'],3:['M','','2026-10-25','public_domain_us']}};
 ['1','2','3'].forEach(i=>assert.equal(RT.resolve(fake,i).status,'unknown'))});
test('every hostable record carries written evidence and a checked date',()=>{
 for(const i of RT.ORDER.filter(RT.hostable).flatMap(idsBy)){const x=RT.resolve(RD,i);assert(x.evidence.length>40,i);assert.match(x.checked,/^\d{4}-\d{2}-\d{2}$/);assert(!/^Lead, not confirmed/.test(x.evidence),i)}});
test('list rows: link only and unknown records get the book page and no file links; hostable rows keep them',()=>{
 const c=appCtx();
 for(const st of ['link_only','unknown']){const i=idsBy(st)[0];const h=c.brow(book(i));
  assert(h.includes('rb-'+st.replace('_','-')),st);assert(!RAW.test(h),st+': '+h);assert(h.includes('legacy/book/'+i+'/CalibreLibrary'));assert(!/download/i.test(h))}
 const p=idsBy('public_domain_us')[0];const h=c.brow(book(p));assert(h.includes('rb-public-domain-us'));assert(RAW.test(h))});
test('record pages: download buttons only for hostable records, with evidence and checked date shown',()=>{
 for(const st of ['link_only','unknown','public_domain_us']){const c=appCtx();const i=idsBy(st)[0];c.B.ids[i]=book(i);c.B.list=[c.B.ids[i]];c.bookDetail(+i);
  const x=RT.resolve(RD,i);assert(c.out.includes(esc(x.evidence)),st);assert(c.out.includes('Checked '+x.checked));
  if(RT.hostable(st)){assert(c.out.includes('calibre/get/PDF/'+i))}else{assert(!RAW.test(c.out),st);assert(!c.out.includes(' ↓</a>'));assert(c.out.includes('legacy/book/'+i+'/CalibreLibrary'))}}});
test('work pages: the Other formats panel links files only for hostable matches',()=>{
 const ctx={esc,window:{BCRights:RT,EDITORIAL_FLAGS:{books:{}}},IM:{server:'https://isidore.co/calibre/',rightsChecked:'2026-10-25',matches:{w:[{id:1,t:'a',a:[],f:['EPUB'],r:'link_only'},{id:2,t:'b',a:[],f:['EPUB'],r:'unknown'},{id:3,t:'c',a:[],f:['EPUB']}]}},unflagged:()=>true};
 vm.runInNewContext(['isidoreDl','otherFormats','rightsFor','canHostB'].map(n=>fn(LIB,n)).join('\n'),ctx);
 let h=ctx.otherFormats({id:'w'});assert(!RAW.test(h));assert.equal((h.match(/Book page on isidore\.co/g)||[]).length,3);
 ctx.IM.matches.w=[{id:4,t:'d',a:[],f:['EPUB'],r:'public_domain_us'}];h=ctx.otherFormats({id:'w'});assert(h.includes('calibre/get/EPUB/4'))});
test('every match in isidore-matches carries the status from rights.json',()=>{
 const im=JSON.parse(fs.readFileSync('data/isidore-matches.json','utf8'));
 for(const L of Object.values(im.matches))for(const b of L)assert.equal(b.r,RT.resolve(RD,b.id).status,b.id)});
test('every hosted reading-room edition maps to public domain (US); external editions are link only',()=>{
 let n=0;for(const w of lib.works)for(const e of w.editions){const x=RT.edition(e);
  if(e.text){n++;assert.equal(x.status,'public_domain_us',e.id)}else if(e.access==='reference')assert.equal(x,null);else assert.equal(x.status,'link_only',e.id)}
 assert(n>=50)});
test('badges are calm and accessible: a link to #/rights with evidence and checked date in the title',()=>{
 const h=RT.badge(RT.resolve(RD,idsBy('link_only')[0]));assert.match(h,/href="#\/rights"/);assert.match(h,/title="Link only\. .+ Checked 2026-10-25\. Not legal advice\."/);assert(!/!|warning|illegal|pirat/i.test(h))});
test('v18: the Authors A-Z tab, search entries, and hub data never link raw isidore.co folder listings',()=>{
 const els={};const $=sel=>els[sel]||(els[sel]={innerHTML:'',textContent:'',addEventListener(){}});
 const hub=JSON.parse(fs.readFileSync('data/catholic-hub.json','utf8'));
 const ctx={esc,hl:esc,norm:s=>String(s).toLowerCase(),$,D:{isidore:hub.isidore.slice(0,400)},window:{scrollTo(){}},document:{getElementById:()=>null},out:''};
 ctx.render=h=>{ctx.out=h};
 vm.runInNewContext(fn(APP,'isoName')+'\n'+fn(APP,'isoAuthorHref')+'\nvar ISO_NOTE="note";\n'+fn(APP,'isidore'),ctx);ctx.isidore();
 const all=ctx.out+els['#iso-out'].innerHTML;
 assert(!/isidore\.co\/CalibreLibrary\//.test(all),'raw folder link in the A-Z page');
 assert(/href="#\/isidore\/author=[^"]+"/.test(els['#iso-out'].innerHTML),'names open Isidore Index searches');
 assert.match(ctx.out,/Authors A–Z/);assert.doesNotMatch(ctx.out,/Author folders/);
 assert.match(APP,/IDX\.push\(\{type:'Isidore Index author',t:isoName\(i\),[^}]*h:isoAuthorHref\(i\)/);
 assert.doesNotMatch(APP,/'isidore\.co folder'/);
 const raw=JSON.stringify(hub);assert(!/isidore\.co\/CalibreLibrary\//.test(raw),'hub data still links a folder listing');
 assert(hub.isidore.every(i=>i.n&&typeof i.f==='string'&&!('u' in i)));
 for(const ds of ['isidore-folders','authors']){assert(!/isidore\.co\/CalibreLibrary\//.test(fs.readFileSync('data/open/'+ds+'.json','utf8')),ds)}
});
