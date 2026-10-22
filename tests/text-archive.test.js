const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function reader(fetch){
 const window={LIBRARY_DATA:{textArchive:{enabled:true,baseUrl:'https://texts.bibliothecacatholica.com/texts/'},works:[]}};
 const context={window,document:{getElementById:()=>null},fetch,AbortController,setTimeout,clearTimeout};
 vm.runInNewContext(fs.readFileSync('scripts/library.js','utf8'),context);
 return window.BCLibrary;
}
test('reader requests the archive copy first',async()=>{
 const calls=[];
 const library=reader(async url=>{calls.push(url);return {ok:true,text:async()=>'original source bytes'};});
 assert.equal(await library.fetchReadingText({text:'data/texts/pg-3296.txt'}),'original source bytes');
 assert.deepEqual(calls,['https://texts.bibliothecacatholica.com/texts/pg-3296.txt']);
});
test('archive network and HTTP failures fall back to the preserved local copy',async()=>{
 for(const failure of ['network','http']){
  const calls=[];
  const library=reader(async url=>{calls.push(url);if(calls.length===1){if(failure==='network')throw Error('unavailable');return {ok:false};}return {ok:true,text:async()=>'local original'};});
  assert.equal(await library.fetchReadingText({text:'data/texts/pg-3296.txt'}),'local original');
  assert.equal(calls[1],'data/texts/pg-3296.txt');
 }
});
test('reader propagates failure if neither copy is available',async()=>{
 const library=reader(async()=>({ok:false}));
 await assert.rejects(library.fetchReadingText({text:'data/texts/pg-3296.txt'}),/Text unavailable/);
});
