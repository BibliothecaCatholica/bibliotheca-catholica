const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const guides=require('../scripts/guides.js');
const context={window:{}};
vm.runInNewContext(fs.readFileSync('data/guide.js','utf8'),context);
const data=JSON.parse(JSON.stringify(context.window.GUIDE_DATA));
const catalog=JSON.parse(fs.readFileSync('data/library.json','utf8')).works;
const options=JSON.parse(fs.readFileSync('data/reading-options.json','utf8')).options;
test('every reading recommendation resolves to a named work and valid catalog references',()=>{
 const ids=new Set();
 for(const l of data.lists){
  assert(!ids.has(l.id),l.id);ids.add(l.id);assert(l.start&&l.audience,l.id);
  for(const it of l.items){
   if(it.e)assert(data.editions.some(w=>w.id===it.e),it.e);
   const item=guides.item(it,data.editions,catalog);assert(item.title,l.id);
   for(const id of it.workIds||[])assert(catalog.some(w=>w.id===id),id);
  }
 }
 for(const w of data.editions)for(const id of w.workIds||[])assert(catalog.some(c=>c.id===id),id);
});
test('a companion work or adaptation cannot become the primary reading edition',()=>{
 const teresa=data.editions.find(w=>w.id==='teresa');
 const exercises=data.editions.find(w=>w.id==='exercises');
 const lord=data.editions.find(w=>w.id==='lordworld');
 assert(!teresa.free.some(f=>f[1].endsWith('/8120')));
 assert(teresa.related.some(f=>f[1].endsWith('/8120')));
 assert(!exercises.free.some(f=>f[1].endsWith('/70790')));
 assert(!guides.available(exercises,catalog,options).here);
 assert(!lord.free.some(f=>f[1].endsWith('/15992')));
 assert.equal(guides.works(data.editions.find(w=>w.id==='fatherbrown'),catalog)[0].id,'innocence-father-brown');
});
test('reading filters distinguish hosted texts, external reading, EPUBs, and references',()=>{
 assert.deepEqual(guides.available(data.editions.find(w=>w.id==='confessions'),catalog,options),{here:true,online:true,epub:true});
 assert.deepEqual(guides.available({workIds:['dei-verbum']},catalog,options),{here:false,online:true,epub:false});
 assert.deepEqual(guides.available({workIds:['lewis-mere-christianity']},catalog,options),{here:false,online:false,epub:false});
 assert(guides.matches({t:'Story of a Soul',a:'Thérèse of Lisieux'},'therese soul'));
 assert(!guides.matches({t:'Confessions',a:'Augustine'},'therese'));
});
