const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const S=require('../scripts/saints.js');
const ctx={window:{}};vm.runInNewContext(fs.readFileSync('data/saints.js','utf8'),ctx);
const raw=JSON.parse(JSON.stringify(ctx.window.SAINTS_DATA));
const D=Object.assign({},raw,{byId:Object.fromEntries(raw.saints.map(s=>[s.id,s]))});
const {key,lookup,fmtDate,onDay,href}=S.core;
test('alias keys normalize like tools/build_saints.py',()=>{
 assert.equal(key('Saint Thérèse of Lisieux'),'therese of lisieux');
 assert.equal(key('St. Thomas Aquinas'),'thomas aquinas');
 assert.equal(key("St Patrick's"),'patricks');
 assert.equal(key('The Little Flower'),'little flower');
 assert.equal(key('Saint'),'saint');
});
test('alias lookup finds Therese, Little Flower, and Thomas Aquinas; bare names are collisions',()=>{
 for(const q of ['Little Flower','Therese','Thérèse','St. Thérèse of Lisieux'])assert.equal(lookup(D,q).id,'therese-of-lisieux',q);
 assert.equal(lookup(D,'Thomas Aquinas').id,'thomas-aquinas');
 const j=lookup(D,'John');assert(j.collision&&j.collision.length>=2);
 assert.equal(lookup(D,'zzzz'),null);
});
test('tier 1 saints open their author page; others their own page',()=>{
 assert.equal(href(D.byId['thomas-aquinas']),'#/author/thomas-aquinas');
 assert.equal(href(D.byId['christopher']),'#/saints/christopher');
});
test('day lists separate Vatican News from other calendars',()=>{
 assert.equal(fmtDate('07-25'),'25 July');
 const d=onDay(D,'07-25');assert(d.vn.some(s=>s.id==='christopher'));
 for(const s of d.other)assert(!s.feasts.vatican_news.some(v=>v.date==='07-25'));
});
test('no CatholicSaints.Info link outside tier 1',()=>{
 for(const s of raw.saints)if(s.tier>1)assert.equal(s.catholicsaints,null,s.id);
});
