const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const T=require('../scripts/timeline.js').core,R=require('../scripts/rights.js');
const hub=JSON.parse(fs.readFileSync('data/catholic-hub.json')),saints=JSON.parse(fs.readFileSync('data/saints.json')),lib=JSON.parse(fs.readFileSync('data/library.json'));
const rows=T.build(hub.authors,saints.saints,lib.works,saints.shelf,{},R);
test('one entry per person merges author saints without duplicating them',()=>{
 assert.equal(rows.length,hub.authors.length+saints.saints.filter(s=>!s.author_id).length);
 assert.equal(new Set(rows.map(r=>r.id)).size,rows.length);
 const a=rows.find(r=>r.id==='thomas-aquinas');assert(a.author&&a.saint&&a.doctor);assert(a.own.length);
 assert.equal(a.century,a.author.century);
});
test('biographies about Francis are not writings attributed to Francis',()=>{
 const f=rows.find(r=>r.id==='francis-of-assisi');assert(f.about.length);assert(!f.own.some(w=>w.id==='chesterton-francis'));
 assert(T.filter(rows,'Little Flower','saints','',false).some(r=>r.id==='therese-of-lisieux'));
 assert(T.filter(rows,'Confessions','all','',false).some(r=>r.id==='augustine-of-hippo'));
});
test('papal documents connect to the existing author profiles',()=>{
 for(const [id,work] of [['john-paul-ii','veritatis-splendor'],['joseph-ratzinger','deus-caritas-est'],['pope-leo-xiii','rerum-novarum']])assert(rows.find(r=>r.id===id).own.some(w=>w.id===work));
});
test('chronology has no year zero and does not invent dates for tradition or angels',()=>{
 for(const [y,c] of [[1,1],[100,1],[101,2],[-1,-1],[-100,-1],[-101,-2],[0,null]])assert.equal(T.centuryOf(y),c);
 assert.equal(T.chronological({kind:'person',died:{year:304}}),4);
 assert.equal(T.chronological({kind:'person',born:{year:1501}}),16);
 assert.equal(T.chronological({kind:'person',historicity:{flag:'tradition'},died:{year:304}}),null);
 assert.equal(T.chronological({kind:'angel',died:{year:304}}),null);
 assert.equal(T.groups(rows).at(-1).key,'undated');
});
test('editorial exclusions and rights gates fail closed',()=>{
 assert(!T.build(hub.authors,saints.saints,lib.works,saints.shelf,{hubAuthors:['thomas-aquinas']},R).some(r=>r.id==='thomas-aquinas'));
 assert.equal(T.filter(T.build(hub.authors,saints.saints,lib.works,saints.shelf,{},null),'','all','',true).length,0);
 for(const r of rows){for(const w of r.own){const e=r.canRead(w);if(e)assert(R.hostable(R.edition(e).status));}assert(r.external.every(w=>!w.url.includes('isidore.co/')));}
 assert(T.filter(rows,'','saints','',false).every(r=>r.saint));
 assert(T.filter(rows,'','doctors','',false).every(r=>r.doctor));
});
