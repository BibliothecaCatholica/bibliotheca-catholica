const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
// robotsFor() in app.js decides the runtime meta robots value (QA 2026-11-02: /search/ is in sitemap.xml and must stay indexable).
const app=fs.readFileSync('app.js','utf8');
const src=app.match(/^function robotsFor\(.*$/m);
assert(src,'robotsFor() is defined on one line in app.js');
const ctx={URLSearchParams};vm.runInNewContext(src[0]+';this.robotsFor=robotsFor;',ctx);
const R=ctx.robotsFor,I='index,follow',N='noindex,follow';
const sitemap=fs.readFileSync('sitemap.xml','utf8');
test('the empty search entry page stays indexable, matching its static HTML and the sitemap',()=>{
 assert(sitemap.includes('<loc>https://bibliothecacatholica.com/search/</loc>'));
 assert(fs.readFileSync('search/index.html','utf8').includes('<meta name="robots" content="index,follow">'));
 assert.equal(R('','search',''),I);
 assert.equal(R('','search','?lookup='),I);
 assert.equal(R('','search','?lookup=%20%20'),I);
 assert.equal(R('#/search','',''),I);
 assert.equal(R('#/search/','',''),I);
 assert.equal(R('#/search?scope=all','',''),I);
});
test('a real search query is noindex',()=>{
 assert.equal(R('#/search/augustine','',''),N);
 assert.equal(R('#/search/augustine?scope=all','',''),N);
 assert.equal(R('#/search/augustine','search',''),N);
 assert.equal(R('','search','?lookup=augustine'),N);
 assert.equal(R('#/search/x','search','?lookup=augustine'),N);
});
test('Isidore Index: base and A to Z pages indexable, filters and queries noindex, flagged books noindex',()=>{
 assert(sitemap.includes('<loc>https://bibliothecacatholica.com/isidore/</loc>'));
 assert.equal(R('#/isidore','',''),I);
 assert.equal(R('','isidore',''),I);
 assert.equal(R('#/isidore/folders','',''),I);
 assert.equal(R('#/isidore/book/12','',''),I);
 assert.equal(R('#/isidore/book/3895','','',true),N);
 for(const h of ['#/isidore/q=newman','#/isidore/author=Newman, John Henry','#/isidore/newman','#/isidore/lang=eng','#/isidore/era=medieval','#/books/newman'])assert.equal(R(h,'',''),N,h);
});
test('other routes stay indexable',()=>{
 for(const h of ['','#/','#/authors','#/author/thomas-aquinas','#/work/confessions','#/rites/latin-ambrosian','#/reading/advent-2026'])assert.equal(R(h,'',''),I,h);
 assert.equal(R('','author/thomas-aquinas',''),I);
});
test('updateMeta uses robotsFor and the empty search page keeps the static title',()=>{
 assert(app.includes("setMeta('meta[name=robots]','content',robotsFor(location.hash,window.BC_BOOT,location.search,bk))"));
 assert(!app.includes("raw[0]==='search'?'noindex,follow'"));
 const title=fs.readFileSync('search/index.html','utf8').match(/<title>([^<]*)<\/title>/)[1];
 assert(app.includes("document.title='"+title+"'"),title);
});
test('canonicalFor(): edition slugs with an underscore keep their own static URL (QA 2026-11-02 re-check)',()=>{
 const m=app.match(/^function canonicalFor\(\)[\s\S]*?return SITE\+'#\/'\+raw\}$/m);
 assert(m,'canonicalFor() found in app.js');
 const c={location:{hash:''},window:{BC_BOOT:'',BCSaints:{get:()=>null}},STATIC_SECTIONS:['editions','reading','rites','saints','search'],SITE:'https://bibliothecacatholica.com/'};
 vm.runInNewContext(m[0]+';this.canonicalFor=canonicalFor;',c);
 const at=(hash,boot)=>{c.location.hash=hash;c.window.BC_BOOT=boot||'';return c.canonicalFor()};
 for(const s of ['campion_ck','intro_xty','jesus_naz','spirit_lit']){
  const own='https://bibliothecacatholica.com/editions/'+s+'/';
  assert(sitemap.includes('<loc>'+own+'</loc>'),s);
  assert.equal(at('#/editions/'+s),own,s);
  assert.equal(at('','editions/'+s),own,s);
 }
 assert.equal(at('#/editions/confessions'),'https://bibliothecacatholica.com/editions/confessions/');
 // other routes are not loosened: an underscore there still falls back to the hash URL
 assert.equal(at('#/author/a_b'),'https://bibliothecacatholica.com/#/author/a_b');
 assert.equal(at('#/work/a_b'),'https://bibliothecacatholica.com/#/work/a_b');
 assert.equal(at('#/editions/Bad_Slug'),'https://bibliothecacatholica.com/#/editions/Bad_Slug');
});
test('route(): the "Search and browse" title is set only on the empty search page',()=>{
 const i=app.indexOf("case 'search':"),j=app.indexOf('break;',app.indexOf("document.title='Search and browse",i));
 assert(i>0&&j>i);
 const seg=app.slice(i,j);
 assert.match(seg,/results\(p\.slice\(1\)\.join\('\/'\)\);else\{render\(/,'else branch has braces');
 assert(seg.endsWith("document.title='Search and browse · Bibliotheca Catholica'}"),'title line sits inside the else block');
});
