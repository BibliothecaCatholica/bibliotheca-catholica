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
 assert.deepEqual(Array.from(A.EVENTS).sort(),['filter_use','listen_complete','listen_play','open_text','outbound_click','page_view','reader_section','search','support_click','theme_toggle']);
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
