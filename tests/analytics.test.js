const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const SRC=fs.readFileSync('scripts/analytics.js','utf8');
// Load the helper in its own realm, optionally with a gtag stub that records calls.
function load(withGtag,throwing,hostname){const calls=[];const ctx={URL,location:{hash:'',hostname:hostname||'bibliothecacatholica.com',pathname:'/',search:''},AFFILIATES:{publishers:{ignatius:{search:'https://ignatius.com/search.php?search_query={q}'},tan:{search:'https://tanbooks.com/search?q={q}'}}}};
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
 assert.equal(A.pagePath('#/search/augustine%20confessions?scope=all'),'/search/');
 assert.equal(A.pagePath('#/search/my private query'),'/search/');
 assert.equal(A.pagePath('#/isidore/q=summa'),'/isidore/');
 assert.equal(A.pagePath('#/isidore/Chesterton%2C%20G.%20K.'),'/isidore/');
 assert.equal(A.pagePath('#/isidore/lang=eng'),'/isidore/');
 assert.equal(A.pagePath('#/books/garrigou'),'/isidore/');
 assert.equal(A.pagePath('#/isidore/book/6229'),'/isidore/book/6229/');
 assert.equal(A.pagePath('#/isidore/folders'),'/isidore/folders/');
 assert.equal(A.pagePath('#/author/g-k-chesterton'),'/author/g-k-chesterton/');
 assert.equal(A.pagePath('#/author/g-k-chesterton','work/orthodoxy'),'/author/g-k-chesterton/');
 assert.equal(A.pagePath('','work/orthodoxy'),'/work/orthodoxy/');
 assert.equal(A.pagePath('',''),'/');assert.equal(A.pagePath('#/'),'/');
 assert.equal(A.pagePath('#/nothing here/x'),'/');
 assert.equal(A.pageLocation(A.pagePath('#/search/secret')),'https://bibliothecacatholica.com/search/');
 for(const h of ['#/search/secret','#/isidore/secret','#/isidore/q=secret','#/books/secret']){assert.doesNotMatch(A.pagePath(h),/secret/);assert.doesNotMatch(A.pageLocation(A.pagePath(h)),/secret/)}
});
test('v18: gaPageView sends the normalized path and location, never location.href',()=>{
 const app=fs.readFileSync('app.js','utf8');const m=/function gaPageView\(\)\{[\s\S]*?\},400\)\}/.exec(app);assert.ok(m);
 assert.match(m[0],/pagePath\(location\.hash,window\.BC_BOOT\)/);assert.match(m[0],/A\.pageLocation\(path,landing\?A\.landingSearch\(location\.search,location\.hash\):''\)/);assert.match(m[0],/page_location:loc/);
 assert.doesNotMatch(m[0],/location\.href/);
});
test('v18: outbound_click carries only link_domain and link_kind',()=>{
 const {A,calls,ctx}=load(true);ctx.location.hash='#/work/orthodoxy';
 const a={getAttribute:k=>k==='href'?'https://ignatius.com/x':null,closest:sel=>sel==='a[href]'?a:null};
 A.onClick({target:a});
 const ev=calls.filter(c=>c[0]==='event');assert.deepEqual(ev.map(c=>c[1]),['outbound_click']);assert.deepEqual(ev[0][2],{link_domain:'ignatius.com',link_kind:'publisher'});
 assert.deepEqual(calls[0],['set',{page_title:'Bibliotheca Catholica',page_location:'https://bibliothecacatholica.com/work/orthodoxy/'}]);
});

test('v18.1: no search or Index term reaches page_title or page_location on any event; only search_term carries it, capped',()=>{
 const term='zqx'+'b'.repeat(150);assert.equal(term.length,153);
 const routes=['#/search/'+term,'#/search/'+encodeURIComponent(term)+'?scope=isidore','#/isidore/q='+term,'#/isidore/'+term,'#/isidore/lang=eng&q='+term,'#/books/'+term];
 for(const h of routes){const {A,calls,ctx}=load(true);ctx.location.hash=h;ctx.document={title:'Search: '+term+' · Bibliotheca Catholica'};
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
 assert.doesNotMatch(APP,/document\.title='Search: '\+/);assert.match(APP,/document\.title='Search · Bibliotheca Catholica'/);
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
 A.track('page_view',{page_path:'/work/imitation/'});A.onClick({target:lv});
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
 assert.equal(A.pageLocation(A.pagePath('','search'),'?lookup=foo'),O+'/search/');
 assert.equal(A.pageLocation(A.pagePath('#/search/foo'),''),O+'/search/');
 assert.equal(A.pageLocation(A.pagePath('#/search/foo'),'?lookup=foo&q=foo&utm_source=x'),O+'/search/?utm_source=x');
 // (b) kept on the landing view
 assert.equal(A.pageLocation('/','?utm_source=substack&utm_medium=email&utm_campaign=x'),O+'/?utm_source=substack&utm_medium=email&utm_campaign=x');
 assert.equal(A.pageLocation('/work/x/','?utm_content=footer+link&utm_source=bsky'),O+'/work/x/?utm_source=bsky&utm_content=footer%20link');
 // a path that still holds a '#' gets the tags before it
 assert.equal(A.pageLocation('/#/work/x','?utm_content=footer+link&utm_source=bsky'),O+'/?utm_source=bsky&utm_content=footer%20link#/work/x');
 // (c) utm_term and unknown parameters dropped
 assert.equal(A.pageLocation('/','?utm_term=secret&gclid=abc&fbclid=1&ref=x&utm_id=9'),O+'/');
 assert.doesNotMatch(A.pageLocation('/','?utm_source=a&utm_term=secret'),/secret|utm_term/);
 // (d) each value cut to 100 characters
 const long='a'.repeat(150),u=A.pageLocation('/','?utm_campaign='+long+'&utm_source=%20%20s%20');
 assert.equal(u,O+'/?utm_source=s&utm_campaign='+'a'.repeat(100));
 assert.equal(A.pageLocation('/','?utm_source='),O+'/');assert.equal(A.pageLocation('/','?utm_source=%E0%A4%A'),O+'/');
 // app.js passes location.search only on the first page view
 const APP=fs.readFileSync('app.js','utf8');assert.match(APP,/var landing=!gaLanded,loc=A\.pageLocation\(path,landing\?A\.landingSearch\(location\.search,location\.hash\):''\);gaLanded=true;/);
 assert.doesNotMatch(SRC,/utm_term'/);
});

/* ---------- UTM tags before the '#' (QA 2026-11-03 medium; owner-approved fix 2026-11-09) ---------- */
test('2026-11-09: landing page_location puts the tags in the query string, where GA4 reads them',()=>{
 const {A}=load(false);
 for(const path of ['/','/library/','/work/orthodoxy/','/search/']){
  const u=new URL(A.pageLocation(path,'?utm_source=x&utm_medium=social&utm_campaign=advent'));
  assert.equal(u.origin+u.pathname,'https://bibliothecacatholica.com'+path,path);assert.equal(u.hash,'',path);
  assert.equal(u.searchParams.get('utm_source'),'x');assert.equal(u.searchParams.get('utm_medium'),'social');assert.equal(u.searchParams.get('utm_campaign'),'advent');
  assert.doesNotMatch(u.hash,/utm_/)}
 assert.equal(A.pageLocation('/library/',''),'https://bibliothecacatholica.com/library/');
});
test('2026-11-09: campaignUrl builds links with the tags before the fragment',()=>{
 const {A}=load(false);
 const a=new URL(A.campaignUrl('#/library',{utm_source:'x',utm_medium:'social'}));
 assert.equal(a.href,'https://bibliothecacatholica.com/?utm_source=x&utm_medium=social#/library');
 assert.equal(a.searchParams.get('utm_source'),'x');assert.equal(a.searchParams.get('utm_medium'),'social');assert.equal(a.hash,'#/library');
 const b=new URL(A.campaignUrl('/work/orthodoxy/',{utm_source:'substack',utm_medium:'email',utm_campaign:'c'.repeat(150),utm_term:'secret',utm_content:' '}));
 assert.equal(b.pathname,'/work/orthodoxy/');assert.equal(b.hash,'');assert.equal(b.searchParams.get('utm_campaign').length,100);
 assert.equal(b.searchParams.has('utm_term'),false);assert.equal(b.searchParams.has('utm_content'),false);
 // a link that already has tags after the '#' is repaired
 const c=new URL(A.campaignUrl('https://bibliothecacatholica.com/#/author/g-k-chesterton?utm_source=old',{utm_source:'bsky',utm_medium:'social'}));
 assert.equal(c.hash,'#/author/g-k-chesterton');assert.equal(c.searchParams.get('utm_source'),'bsky');
 assert.equal(new URL(A.campaignUrl('/',{utm_source:'x'})).href,'https://bibliothecacatholica.com/?utm_source=x');
});
test('2026-11-09: utm_ tags after the # are read for the landing view, cut to 100, and location.search wins',()=>{
 const {A}=load(false),O='https://bibliothecacatholica.com';
 assert.deepEqual({...A.hashUtm('#/library?utm_source=x&utm_medium=social')},{query:'?utm_source=x&utm_medium=social',hash:'#/library',changed:true});
 assert.deepEqual({...A.hashUtm('#/search/foo?scope=isidore&utm_source=x&utm_term=t')},{query:'?utm_source=x&utm_term=t',hash:'#/search/foo?scope=isidore',changed:true});
 assert.deepEqual({...A.hashUtm('#?utm_source=x')},{query:'?utm_source=x',hash:'',changed:true});
 assert.deepEqual({...A.hashUtm('#/work/x?scope=all')},{query:'',hash:'#/work/x?scope=all',changed:false});
 assert.deepEqual({...A.hashUtm('')},{query:'',hash:'',changed:false});
 const h='#/library?utm_source=x&utm_medium=social&utm_campaign='+'a'.repeat(150)+'&utm_term=secret&gclid=1';
 const loc=A.pageLocation(A.pagePath(h),A.landingSearch('',h)),u=new URL(loc);
 assert.equal(u.pathname,'/library/');assert.equal(u.hash,'');assert.equal(u.searchParams.get('utm_source'),'x');assert.equal(u.searchParams.get('utm_medium'),'social');
 assert.equal(u.searchParams.get('utm_campaign').length,100);assert.equal(u.searchParams.has('utm_term'),false);assert.doesNotMatch(loc,/secret|gclid/);
 // a tag in location.search beats the same tag in the hash; others are filled from the hash
 const v=new URL(A.pageLocation('/library/',A.landingSearch('?utm_source=real','#/library?utm_source=hash&utm_medium=social')));
 assert.equal(v.searchParams.get('utm_source'),'real');assert.equal(v.searchParams.get('utm_medium'),'social');
 assert.equal(A.landingSearch('',''),'');assert.equal(A.pageLocation('/library/',A.landingSearch('','#/library')),O+'/library/');
});
test('2026-11-09: stripHashUtm removes the tags from the hash with replaceState and keeps everything else',()=>{
 const {A,ctx}=load(false),seen=[];
 ctx.history={state:null,replaceState:(s,t,u)=>seen.push(u)};
 ctx.location={pathname:'/',search:'?utm_source=real',hash:'#/library?utm_source=x&utm_medium=social',hostname:'bibliothecacatholica.com'};
 assert.equal(A.stripHashUtm(),true);assert.deepEqual([...seen],['/?utm_source=real#/library']);
 ctx.location={pathname:'/work/orthodoxy/',search:'',hash:'#/search/foo?scope=all&utm_campaign=c',hostname:'bibliothecacatholica.com'};
 assert.equal(A.stripHashUtm(),true);assert.equal(seen[1],'/work/orthodoxy/#/search/foo?scope=all');
 ctx.location={pathname:'/',search:'',hash:'#/library',hostname:'bibliothecacatholica.com'};assert.equal(A.stripHashUtm(),false);assert.equal(seen.length,2);
 ctx.history={replaceState:()=>{throw new Error('boom')}};ctx.location={pathname:'/',search:'',hash:'#/x?utm_source=1',hostname:'bibliothecacatholica.com'};assert.equal(A.stripHashUtm(),false);
 delete ctx.history;assert.equal(A.stripHashUtm(),false);
});
test('2026-11-09: the hash fallback is the existing landing page_view, not a new event',()=>{
 const {A,calls,ctx}=load(true);ctx.location={pathname:'/',search:'',hash:'#/library?utm_source=x&utm_medium=social',hostname:'bibliothecacatholica.com'};
 const seen=[];ctx.history={state:null,replaceState:(s,t,u)=>{seen.push(u);ctx.location.hash=u.slice(u.indexOf('#'))}};
 const path=A.pagePath(ctx.location.hash);A.track('page_view',{page_title:'t',page_location:A.pageLocation(path,A.landingSearch(ctx.location.search,ctx.location.hash)),page_path:path});A.stripHashUtm();
 const ev=calls.filter(c=>c[0]==='event');assert.deepEqual(ev.map(c=>c[1]),['page_view']);
 assert.equal(ev[0][2].page_location,'https://bibliothecacatholica.com/library/?utm_source=x&utm_medium=social');assert.equal(ev[0][2].page_path,'/library/');
 assert.deepEqual([...seen],['/#/library']);assert.equal(ctx.location.hash,'#/library');
 assert.deepEqual(calls[0],['set',{page_title:'Bibliotheca Catholica',page_location:'https://bibliothecacatholica.com/library/'}]);
 assert.equal(A.EVENTS.length,12);
 const APP=fs.readFileSync('app.js','utf8');assert.match(APP,/if\(landing&&A\.stripHashUtm&&A\.stripHashUtm\(\)\)gaLast=location\.pathname\+location\.hash/);
});

test('affiliate preview 2026-11-09: lddy.no (TAN Books referral) is link_kind affiliate, checked right after bookshop',()=>{
 const {A}=load(false);
 assert.deepEqual(Array.from(A.AFFILIATE_HOSTS),['lddy.no']);
 assert.equal(A.linkKind('lddy.no'),'affiliate');assert.equal(A.linkKind('go.lddy.no'),'affiliate');assert.equal(A.linkKind('notlddy.no'),'other');
 assert.equal(A.linkKind('lddy.no',{publisher:'tan'}),'affiliate');assert.equal(A.linkKind('lddy.no',{source:true}),'affiliate');
 assert.equal(A.linkKind('bookshop.org'),'bookshop');assert.equal(A.linkKind('bookshop.org',{publisher:'tan'}),'bookshop');
 assert.equal(A.linkKind('bibliothecacatholica.substack.com'),'substack');assert.equal(A.linkKind('tanbooks.com'),'publisher');
 const kinds=['bookshop','affiliate','publisher','substack','audio','official','source','other'];
 for(const [href,d,k] of [['https://lddy.no/1qbrw','lddy.no','affiliate'],['https://bookshop.org/a/130222/9780898705522','bookshop.org','bookshop'],['https://bibliothecacatholica.substack.com/subscribe','bibliothecacatholica.substack.com','substack']]){
  const {A,calls,ctx}=load(true);ctx.location.hash='#/work/orthodoxy';
  const a={getAttribute:x=>x==='href'?href:null,closest:sel=>sel==='a[href]'?a:null};
  A.onClick({target:a});
  const ev=calls.filter(c=>c[0]==='event');assert.deepEqual(ev.map(c=>c[1]),['outbound_click']);assert.deepEqual(ev[0][2],{link_domain:d,link_kind:k});assert.ok(kinds.includes(k));
 }
 // no new event names
 assert.deepEqual(Array.from(A.EVENTS).sort(),['filter_use','listen_complete','listen_play','open_text','outbound_click','page_view','reader_section','listen_open','saint_open','search','support_click','theme_toggle'].sort());
});

test('2026-11-09: pages.dev hostname makes track() a no-op (no page_view, no outbound_click)',()=>{
 const {A,calls,ctx}=load(true,false,'bibliotheca-catholica.pages.dev');
 assert.equal(A.allowedHost(),false);
 assert.equal(A.track('page_view',{page_title:'t',page_location:'https://bibliothecacatholica.com/',page_path:'/'}),false);
 const a={getAttribute:x=>x==='href'?'https://bookshop.org/a/130222/9780141441146':null,closest:sel=>sel==='a[href]'?a:null};
 A.onClick({target:a});
 assert.deepEqual(calls,[]);
});
test('2026-11-09: production hostname still sends page_view and outbound_click',()=>{
 const {A,calls}=load(true,false,'bibliothecacatholica.com');
 assert.equal(A.allowedHost(),true);
 assert.equal(A.track('page_view',{page_title:'t',page_location:'https://bibliothecacatholica.com/',page_path:'/'}),true);
 const a={getAttribute:x=>x==='href'?'https://bookshop.org/a/130222/9780141441146':null,closest:sel=>sel==='a[href]'?a:null};
 A.onClick({target:a});
 const ev=calls.filter(c=>c[0]==='event').map(c=>c[1]);
 assert.deepEqual(ev,['page_view','outbound_click']);
 const {A:A2}=load(true,false,'www.bibliothecacatholica.com');
 assert.equal(A2.allowedHost(),true);
 assert.equal(A2.track('page_view',{page_title:'t',page_location:'https://bibliothecacatholica.com/',page_path:'/'}),true);
});

/* ---------- real-path page views (QA hit-level test 2026-11-09; owner-approved fix 2026-11-09) ---------- */
test('2026-11-09: page_path is the real path GA4 can store, never a #/ route',()=>{
 const {A}=load(false),O='https://bibliothecacatholica.com';
 const cases=[['#/author/karl-adam','','/author/karl-adam/'],['','author/karl-adam','/author/karl-adam/'],['','work/confessions','/work/confessions/'],
  ['','reading/spiritual','/reading/spiritual/'],['','library','/library/'],['','policy','/policy/'],['#/library','','/library/'],
  ['','work/orthodoxy/ch/01-introduction-in-defence-of-everything-else','/work/orthodoxy/ch/01-introduction-in-defence-of-everything-else/'],
  ['#/work/confessions','author/karl-adam','/work/confessions/'],['','summa/1-2/q12/a3','/summa/1-2/q12/a3/'],['','search','/search/'],
  ['#/read/confessions/pg-3296/3','','/read/confessions/pg-3296/3/'],['#/saints/calendar/11-09','','/saints/calendar/11-09/']];
 for(const [h,b,want] of cases){const p=A.pagePath(h,b);assert.equal(p,want,h+' '+b);assert.doesNotMatch(p,/#/);
  const u=new URL(A.pageLocation(p));assert.equal(u.pathname,want);assert.equal(u.hash,'');assert.equal(u.href,O+want)}
 assert.equal(A.pageLocation(A.pagePath('','author/karl-adam')),'https://bibliothecacatholica.com/author/karl-adam/');
 assert.equal(A.pageTitle('/search/','Search — x'),'Search · Bibliotheca Catholica');assert.equal(A.pageTitle('/isidore/','x'),'The Isidore Index · Bibliotheca Catholica');
});
test('2026-11-09: on every static page, page_path equals the path of its <link rel=canonical>',()=>{
 const {A}=load(false),{execSync}=require('child_process');
 const files=execSync('git ls-files "*index.html"',{encoding:'utf8'}).split('\n').filter(f=>f&&f!=='index.html');let n=0;
 for(const f of files){const html=fs.readFileSync(f,'utf8'),b=/window\.BC_BOOT="([^"]*)"/.exec(html),c=/<link rel="canonical" href="https:\/\/bibliothecacatholica\.com([^"]*)"/.exec(html);
  if(!b||!c)continue;n++;assert.equal(A.pagePath('',b[1]),c[1],f);assert.equal(A.pagePath('#/'+b[1]),c[1],f)}
 assert.ok(n>4000,'checked '+n+' static pages');
});
