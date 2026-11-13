const {test}=require('node:test');
const assert=require('node:assert/strict');
test('collection searches encode literal queries and reject unknown providers',async()=>{
 const {sourceUrl}=await import('../src/libraries/logic.mjs');
 for(const id of ['openlibrary','archive','gutenberg','worldcat']){
  const url=new URL(sourceUrl(id,'Bede & Joseph? <script> # /'));
  assert.equal([...url.searchParams.values()][0],'Bede & Joseph? <script> # /');
  assert.equal(url.hash,'');assert.equal(url.protocol,'https:');
 }
 assert.throws(()=>sourceUrl('__proto__','x'));assert.throws(()=>sourceUrl('https://evil.test','x'));
});
test('library discovery tolerates typos and matches all tokens across fields',async()=>{
 const {rankResources}=await import('../src/libraries/logic.mjs');const {default:Fuse}=await import('fuse.js');
 const rows=[{name:'Corpus Thomisticum',desc:'Latin works of Aquinas',tags:['scholarly']},{name:'Open Library',desc:'Works and editions',tags:['catalog']}];
 assert.equal(rankResources(Fuse,rows,'Thomisticm Latin')[0],rows[0]);
 assert.deepEqual(rankResources(Fuse,rows,'unfindable zzzzz'),[]);
 assert.equal(rankResources(Fuse,rows,'')[0],rows[0]);
});
