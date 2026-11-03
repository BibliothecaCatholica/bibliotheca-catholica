const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const SRC=fs.readFileSync('scripts/analytics.js','utf8');
// Load the helper in its own realm, optionally with a gtag stub that records calls.
function load(withGtag,throwing){const calls=[];const ctx={URL,location:{hash:''},AFFILIATES:{publishers:{ignatius:{search:'https://ignatius.com/search.php?search_query={q}'},tan:{search:'https://tanbooks.com/search?q={q}'}}}};
 ctx.window=ctx;ctx.globalThis=ctx;if(withGtag)ctx.gtag=function(){if(throwing)throw new Error('boom');calls.push(JSON.parse(JSON.stringify(Array.from(arguments))))};
 vm.runInNewContext(SRC,ctx);return {A:ctx.BCAnalytics,calls,ctx}}
test('event names are the agreed GA4 set',()=>{
 const {A}=load(false);
 assert.deepEqual(Array.from(A.EVENTS).sort(),['filter_use','listen_complete','listen_play','open_text','outbound_click','page_view','reader_section','listen_open','saint_open','search','support_click','theme_toggle'].sort());
});
test('track is a no-op without gtag and never throws',()=>{
 const {A}=load(false);assert.equal(A.track('search',{search_term:'x'}),false);
 const t=load(true,true);assert.equal(t.A.track('search',{search_term:'x'}),false);
});
test('track sends gtag event with cleaned params and rejects unknown names',()=>{
 const {A,calls}=load(true);
 assert.equal(A.track('search',{search_term:'confessions',search_scope:'Everything',results_count:12,empty:'',nothing:null}),true);
 const ev=calls.filter(c=>c[0]==='event');
 assert.deepEqual(ev[0],['event','search',{search_term:'confessions',search_scope:'Everything',results_count:12}]);
 assert.equal(A.track('made_up_event',{}),false);assert.equal(calls.filter(c=>c[0]==='event').length,1);
});
test('search terms are trimmed, lowercased, and cut to 100 characters',()=>{
 const {A}=load(false);
 assert.equal(A.cleanTerm('  The   CITY of God  '),'the city of god');
 assert.equal(A.cleanTerm('x'.repeat(250)).length,100);
 assert.equal(A.cleanTerm(null),'');
});
test('string params are capped at 100 characters',()=>{
 const {A}=load(false);assert.equal(A.clean({v:'y'.repeat(300)}).v.length,100);
});
test('outbound links are classified by kind',()=>{
 const {A}=load(false);
 assert.equal(A.domain('https://www.bookshop.org/a/130222/9780141441146'),'bookshop.org');
 assert.equal(A.linkKind('bookshop.org'),'bookshop');
 assert.equal(A.linkKind('ignatius.com'),'publisher');assert.equal(A.publisherKey('tanbooks.com'),'tan');
 assert.equal(A.linkKind('example.org',{publisher:'cluny'}),'publisher');
 assert.equal(A.linkKind('chesterton.substack.com'),'substack');
 assert.equal(A.linkKind('www.gutenberg.org'),'source');assert.equal(A.linkKind('example.org'),'other');
});
test('work id comes from work and reader routes only',()=>{
 const {A}=load(false);
 assert.equal(A.routeWork('#/read/confessions/pusey/3'),'confessions');
 assert.equal(A.routeWork('#/work/orthodoxy'),'orthodoxy');
 assert.equal(A.routeWork('#/author/g-k-chesterton'),'');
});
test('once() dedupes within a scope until reset',()=>{
 const {A}=load(false);
 assert.equal(A.once('reader_section','a/b/1'),true);assert.equal(A.once('reader_section','a/b/1'),false);
 assert.equal(A.once('reader_section','a/b/2'),true);A.reset('reader_section');assert.equal(A.once('reader_section','a/b/1'),true);
});
test('v18: page_path never carries a search term or Index filter, and one view has one path',()=>{
 const {A}=load(false);
 assert.equal(A.pagePath('#/search/augustine%20confessions?scope=all'),'/#/search');
 assert.equal(A.pagePath('#/search/my private query'),'/#/search');
 assert.equal(A.pagePath('#/isidore/q=summa'),'/#/isidore');
 assert.equal(A.pagePath('#/isidore/Chesterton%2C%20G.%20K.'),'/#/isidore');
 assert.equal(A.pagePath('#/isidore/lang=eng'),'/#/isidore');
 assert.equal(A.pagePath('#/books/garrigou'),'/#/isidore');
 assert.equal(A.pagePath('#/isidore/book/6229'),'/#/isidore/book/6229');
 assert.equal(A.pagePath('#/isidore/folders'),'/#/isidore/folders');
 assert.equal(A.pagePath('#/author/g-k-chesterton'),'/#/author/g-k-chesterton');
 assert.equal(A.pagePath('#/author/g-k-chesterton','work/orthodoxy'),'/#/author/g-k-chesterton');
 assert.equal(A.pagePath('','work/orthodoxy'),'/#/work/orthodoxy');
 assert.equal(A.pagePath('',''),'/');assert.equal(A.pagePath('#/'),'/');
 assert.equal(A.pagePath('#/nothing here/x'),'/');
 assert.equal(A.pageLocation(A.pagePath('#/search/secret')),'https://bibliothecacatholica.com/#/search');
 for(const h of ['#/search/secret','#/isidore/secret','#/isidore/q=secret','#/books/secret']){assert.doesNotMatch(A.pagePath(h),/secret/);assert.doesNotMatch(A.pageLocation(A.pagePath(h)),/secret/)}
});
test('v18: gaPageView sends the normalized path and location, never location.href',()=>{
 const app=fs.readFileSync('app.js','utf8');const m=/function gaPageView\(\)\{[\s\S]*?\},400\)\}/.exec(app);assert.ok(m);
 assert.match(m[0],/pagePath\(location\.hash,window\.BC_BOOT\)/);assert.match(m[0],/A\.pageLocation\(path,gaLanded\?'':location\.search\)/);assert.match(m[0],/page_location:loc/);
 assert.doesNotMatch(m[0],/location\.href/);
});
test('v18: outbound_click carries only link_domain and link_kind',()=>{
 const {A,calls,ctx}=load(true);ctx.location.hash='#/work/orthodoxy';
 const a={getAttribute:k=>k==='href'?'https://ignatius.com/x':null,closest:sel=>sel==='a[href]'?a:null};
 A.onClick({target:a});
 const ev=calls.filter(c=>c[0]==='event');assert.deepEqual(ev.map(c=>c[1]),['outbound_click']);assert.deepEqual(ev[0][2],{link_domain:'ignatius.com',link_kind:'publisher'});
 assert.deepEqual(calls[0],['set',{page_title:'Bibliotheca Catholica',page_location:'https://bibliothecacatholica.com/#/work/orthodoxy'}]);
});

test('v18.1: no search or Index term reaches page_title or page_location on any event; only search_term carries it, capped',()=>{
 const term='zqx'+'b'.repeat(150);assert.equal(term.length,153);
 const routes=['#/search/'+term,'#/search/'+encodeURIComponent(term)+'?scope=isidore','#/isidore/q='+term,'#/isidore/'+term,'#/isidore/lang=eng&q='+term,'#/books/'+term];
 for(const h of routes){const {A,calls,ctx}=load(true);ctx.location.hash=h;ctx.document={title:'Search: '+term+' — Bibliotheca Catholica'};
  A.track('search',{search_term:A.cleanTerm(term),search_scope:'Everything',results_count:0});
  A.track('outbound_click',{link_domain:'isidore.co',link_kind:'other'});
  A.track('page_view',{page_title:A.pageTitle(A.pagePath(h),ctx.document.title),page_location:A.pageLocation(A.pagePath(h)),page_path:A.pagePath(h)});
  const sets=calls.filter(c=>c[0]==='set');assert.equal(sets.length,3,h);
  for(const c of calls){const p=c[c.length-1];for(const k of ['page_title','page_location','page_path'])if(p[k]!==undefined){assert.doesNotMatch(p[k],/zqx|bbbb/,h+' '+k)}}
  // the term appears only in the search event's search_term, at 100 characters
  const withTerm=calls.filter(c=>/zqx/.test(JSON.stringify(c)));assert.equal(withTerm.length,1,h);
  assert.equal(withTerm[0][1],'search');assert.equal(withTerm[0][2].search_term.length,100);
 }
});
test('v18.1: app.js keeps search terms out of document.title and uses pageTitle for page views',()=>{
 const APP=fs.readFileSync('app.js','utf8');
 assert.doesNotMatch(APP,/document\.title='Search: '\+/);assert.match(APP,/document\.title='Search — Bibliotheca Catholica'/);
 assert.match(APP,/title=A\.pageTitle\(path,document\.title\)/);
});

/* ---------- analytics spec 2026-11-03 (approved by the owner) ---------- */
test('spec 2026-11-03: link_kind adds audio, official, and source, in order of precedence',()=>{
 const {A}=load(false);
 for(const d of ['librivox.org','archive.librivox.org'])assert.equal(A.linkKind(d),'audio',d);
 for(const d of ['vatican.va','press.vatican.va','usccb.org','bible.usccb.org','vaticannews.va'])assert.equal(A.linkKind(d),'official',d);
 for(const d of ['isidore.co','gutenberg.org','newadvent.org','ccel.org','archive.org','ia800.archive.org','documentacatholicaomnia.eu','tertullian.org','dbu.edu','sourcebooks.fordham.edu'])assert.equal(A.linkKind(d),'source',d);
 assert.equal(A.linkKind('example.org',{source:true}),'source');assert.equal(A.linkKind('vatican.va',{source:true}),'official');
 assert.equal(A.linkKind('bookshop.org',{source:true}),'bookshop');assert.equal(A.linkKind('notvatican.va'),'other');assert.equal(A.linkKind('fordham.edu'),'other');
});
function link(href,cls,attrs){const a={getAttribute:k=>k==='href'?href:(attrs||{})[k]||null,classList:{contains:c=>c===cls},closest:sel=>sel==='a[href]'?a:null};return a}
test('spec 2026-11-03: listen_open fires once per work per page view, for a work-page LibriVox Listen link and the dock',()=>{
 const {A,calls,ctx}=load(true);ctx.location.hash='#/work/imitation';
 const lv=link('https://librivox.org/imitation-of-christ/','listen-btn');
 A.onClick({target:lv});A.onClick({target:lv});
 let ev=calls.filter(c=>c[0]==='event');
 assert.deepEqual(ev.map(c=>c[1]),['listen_open','outbound_click','outbound_click']);
 assert.deepEqual(ev[0][2],{work_id:'imitation',listen_source:'librivox'});assert.deepEqual(ev[1][2],{link_domain:'librivox.org',link_kind:'audio'});
 A.track('page_view',{page_path:'/#/work/imitation'});A.onClick({target:lv});
 ev=calls.filter(c=>c[0]==='event');assert.equal(ev.filter(c=>c[1]==='listen_open').length,2);
 // a LibriVox link that is not a Listen button sends only outbound_click
 const c2=load(true);c2.ctx.location.hash='#/work/imitation';c2.A.onClick({target:link('https://librivox.org/x/','other')});
 assert.deepEqual(c2.calls.filter(c=>c[0]==='event').map(c=>c[1]),['outbound_click']);
 // static work page: work id from BC_BOOT
 const c3=load(true);c3.ctx.BC_BOOT='work/confessions';c3.A.onClick({target:lv});
 assert.deepEqual(c3.calls.filter(c=>c[0]==='event')[0][2],{work_id:'confessions',listen_source:'librivox'});
 const LIB=fs.readFileSync('scripts/library.js','utf8');
 assert.match(LIB,/if\(o\)\{load\(\);if\(gaOnce\('listen_open',w\.id\)\)track\('listen_open',\{work_id:w\.id,listen_source:'dock'\}\)\}/);
});
test('spec 2026-11-03: reader_section carries sections_total',()=>{
 const LIB=fs.readFileSync('scripts/library.js','utf8');
 assert.match(LIB,/track\('reader_section',\{work_id:w\.id,edition_id:e\.id,section_index:page,sections_total:total\}\)/);
});
test('spec 2026-11-03: UTM tags on the landing page_view only; never utm_term, lookup, or other parameters',()=>{
 const {A}=load(false),O='https://bibliothecacatholica.com';
 // (a) search terms never reach page_location
 assert.equal(A.pageLocation(A.pagePath('','search'),'?lookup=foo'),O+'/#/search');
 assert.equal(A.pageLocation(A.pagePath('#/search/foo'),''),O+'/#/search');
 assert.equal(A.pageLocation(A.pagePath('#/search/foo'),'?lookup=foo&q=foo&utm_source=x'),O+'/#/search?utm_source=x');
 // (b) kept on the landing view
 assert.equal(A.pageLocation('/','?utm_source=substack&utm_medium=email&utm_campaign=x'),O+'/?utm_source=substack&utm_medium=email&utm_campaign=x');
 assert.equal(A.pageLocation('/#/work/x','?utm_content=footer+link&utm_source=bsky'),O+'/#/work/x?utm_source=bsky&utm_content=footer%20link');
 // (c) utm_term and unknown parameters dropped
 assert.equal(A.pageLocation('/','?utm_term=secret&gclid=abc&fbclid=1&ref=x&utm_id=9'),O+'/');
 assert.doesNotMatch(A.pageLocation('/','?utm_source=a&utm_term=secret'),/secret|utm_term/);
 // (d) each value cut to 100 characters
 const long='a'.repeat(150),u=A.pageLocation('/','?utm_campaign='+long+'&utm_source=%20%20s%20');
 assert.equal(u,O+'/?utm_source=s&utm_campaign='+'a'.repeat(100));
 assert.equal(A.pageLocation('/','?utm_source='),O+'/');assert.equal(A.pageLocation('/','?utm_source=%E0%A4%A'),O+'/');
 // app.js passes location.search only on the first page view
 const APP=fs.readFileSync('app.js','utf8');assert.match(APP,/var loc=A\.pageLocation\(path,gaLanded\?'':location\.search\);gaLanded=true;/);
 assert.doesNotMatch(SRC,/utm_term'/);
});
