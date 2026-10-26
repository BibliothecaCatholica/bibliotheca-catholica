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
 assert.deepEqual(Array.from(A.EVENTS).sort(),['filter_use','listen_complete','listen_play','open_text','outbound_click','page_view','reader_section','saint_open','search','support_click','theme_toggle']);
});
test('track is a no-op without gtag and never throws',()=>{
 const {A}=load(false);assert.equal(A.track('search',{search_term:'x'}),false);
 const t=load(true,true);assert.equal(t.A.track('search',{search_term:'x'}),false);
});
test('track sends gtag event with cleaned params and rejects unknown names',()=>{
 const {A,calls}=load(true);
 assert.equal(A.track('search',{search_term:'confessions',search_scope:'Everything',results_count:12,empty:'',nothing:null}),true);
 assert.deepEqual(calls[0],['event','search',{search_term:'confessions',search_scope:'Everything',results_count:12}]);
 assert.equal(A.track('made_up_event',{}),false);assert.equal(calls.length,1);
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
 assert.equal(A.linkKind('www.gutenberg.org'),'other');
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
 assert.match(m[0],/pagePath\(location\.hash,window\.BC_BOOT\)/);assert.match(m[0],/page_location:A\.pageLocation\(path\)/);
 assert.doesNotMatch(m[0],/location\.href/);
});
test('v18: outbound_click carries only link_domain and link_kind',()=>{
 const {A,calls,ctx}=load(true);ctx.location.hash='#/work/orthodoxy';
 const a={getAttribute:k=>k==='href'?'https://ignatius.com/x':null,closest:sel=>sel==='a[href]'?a:null};
 A.onClick({target:a});
 assert.deepEqual(calls.map(c=>c[1]),['outbound_click']);assert.deepEqual(calls[0][2],{link_domain:'ignatius.com',link_kind:'publisher'});
});
