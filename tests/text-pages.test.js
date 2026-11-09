const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
// Deep-link gaps (2026-11-09): chapter and story pages are static documents. staticOnly() in app.js keeps the
// pre-rendered page as the view on its own URL and sends a hash link to the static page; canonicalFor() gives
// each one its own static URL; page views use the same plain route (no new analytics event).
const app=fs.readFileSync('app.js','utf8');
const so=app.match(/^function staticOnly\(.*$/m);assert(so,'staticOnly() is defined on one line');
const ctx={};vm.runInNewContext(so[0]+';this.staticOnly=staticOnly;',ctx);
const TP=JSON.parse(fs.readFileSync('data/text-pages.json','utf8')).works;
const routes=[];for(const [w,d] of Object.entries(TP))for(const x of d.items)routes.push('work/'+w+'/'+d.kind+'/'+x.slug);
test('every chapter and story route is static-only, and nothing else is',()=>{
 assert(routes.length>=9);
 for(const r of routes){assert.equal(ctx.staticOnly(r),true,r);assert.equal(ctx.staticOnly(r+'/'),true,r)}
 for(const r of ['work/orthodoxy','author/g-k-chesterton','read/orthodoxy/pg-16769/1/47','work/orthodoxy/ch','work/orthodoxy/notes/01-x','work/Orthodoxy/ch/01-x','',undefined])assert.equal(ctx.staticOnly(r),false,String(r));
});
test('canonicalFor() gives each chapter and story page its own static URL',()=>{
 const m=app.match(/^function canonicalFor\(\)[\s\S]*?return SITE\+'#\/'\+raw\}$/m);assert(m);
 const c={location:{hash:''},window:{BC_BOOT:'',BCSaints:{get:()=>null}},STATIC_SECTIONS:[],SITE:'https://bibliothecacatholica.com/'};
 vm.runInNewContext(m[0]+';this.canonicalFor=canonicalFor;',c);
 const sitemap=fs.readFileSync('sitemap.xml','utf8');
 for(const r of routes){
  const own='https://bibliothecacatholica.com/'+r+'/';assert(sitemap.includes('<loc>'+own+'</loc>'),r);
  c.window.BC_BOOT=r;c.location.hash='';assert.equal(c.canonicalFor(),own,r);
  c.window.BC_BOOT='';c.location.hash='#/'+r;assert.equal(c.canonicalFor(),own,r);
 }
});
test('page views on chapter pages use the plain route and add no event',()=>{
 const A=require('../scripts/analytics.js');
 for(const r of routes)assert.equal(A.pagePath('',r),'/#/'+r,r);
 assert(!/chapter_|story_|text_page/.test(fs.readFileSync('scripts/analytics.js','utf8')));
});
test('the work page in the app lists the parts by real path',()=>{
 const lib=fs.readFileSync('scripts/library.js','utf8');const m=lib.match(/^function partsList\(w\).*$/m);assert(m);
 const c={window:{TEXT_PAGES:JSON.parse(fs.readFileSync('data/text-pages.js','utf8').replace(/^window\.TEXT_PAGES=/,'').replace(/;\s*$/,''))},esc:s=>String(s)};
 vm.runInNewContext(m[0]+';this.partsList=partsList;',c);
 for(const [w,d] of Object.entries(TP)){const h=c.partsList({id:w});for(const x of d.items)assert(h.includes('href="/work/'+w+'/'+d.kind+'/'+x.slug+'/"'),x.slug)}
 assert.equal(c.partsList({id:'confessions'}),'');
});
