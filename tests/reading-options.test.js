const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const data=JSON.parse(fs.readFileSync('data/reading-options.json','utf8'));
const catalog=JSON.parse(fs.readFileSync('data/library.json','utf8'));
test('reading options point to known works and identify direct files versus edition pages',()=>{
 for(const [id,options] of Object.entries(data.options)){
  assert(catalog.works.some(w=>w.id===id),id);
  for(const option of options){
   assert.equal(option.format,'EPUB');
   const source=new URL(option.source),download=new URL(option.url);
   assert.equal(source.protocol,'https:');assert.equal(download.protocol,'https:');
   assert(['www.gutenberg.org','standardebooks.org'].includes(source.hostname));
   if(option.access==='source-page')assert.equal(option.url,option.source);
   else assert.equal(download.hostname,'www.gutenberg.org');
   assert.match(option.checked,/^\d{4}-\d{2}-\d{2}$/);
  }
 }
});
test('browser reading options match the maintained metadata',()=>{
 const context={window:{}};vm.runInNewContext(fs.readFileSync('data/reading-options.js','utf8'),context);
 assert.equal(JSON.stringify(context.window.READING_OPTIONS),JSON.stringify(data));
});
