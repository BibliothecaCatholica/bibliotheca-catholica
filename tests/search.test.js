const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {search,imported}=require('../scripts/search.js');
const catalog=JSON.parse(fs.readFileSync('data/library.json','utf8'));
const selected=catalog.works.map(w=>({type:'Selected work',t:w.title,s:w.author,x:w.title+' '+w.author,w:4}));
const raw=JSON.parse(fs.readFileSync('data/books.json','utf8'));
const external=raw.books.map(b=>({type:'Book',t:b[1],x:b[1],w:1}));
test('the actual imported catalog cannot leak into selected results',()=>{
 const entries=selected.concat(external);
 assert(search(entries,'christ','curated',99999).every(e=>!imported(e)));
 assert(search(entries,'christ','isidore',99999).every(imported));
 assert(search(entries,'christ','isidore',99999).length>0);
 assert.equal(search(external,'christ','curated',99999).length,0);
});
test('accent insensitive and multi-token queries find selected works',()=>{
 assert(search(selected,'therese soul','curated').some(e=>e.t==='Story of a Soul'));
 assert(search(selected,'pensees','curated').some(e=>e.t==='Pensées'));
 assert.equal(search(selected,'   ','all').length,0);
});
test('all scope includes both sources without changing the source records',()=>{
 const entries=selected.concat(external),before=JSON.stringify(entries);
 const results=search(entries,'confessions','all',1000);
 assert(results.some(imported));assert(results.some(e=>!imported(e)));
 assert.equal(JSON.stringify(entries),before);
});
test('the shipped browser metadata exactly matches the JSON source',()=>{
 const context={window:{}};vm.runInNewContext(fs.readFileSync('data/library.js','utf8'),context);
 assert.equal(JSON.stringify(context.window.LIBRARY_DATA),JSON.stringify(catalog));
});
