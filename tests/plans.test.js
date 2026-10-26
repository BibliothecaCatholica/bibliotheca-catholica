'use strict';
const test=require('node:test');const assert=require('node:assert');
global.window=global;const P=require('../scripts/plans.js');
const data=JSON.parse(require('fs').readFileSync(__dirname+'/../data/reading-plans.json','utf8')).plans[0];
function store(){const m={};return {getItem:k=>k in m?m[k]:null,setItem:(k,v)=>{m[k]=String(v)},removeItem:k=>{delete m[k]},m}}
test('plan ids and weekday labels',()=>{assert.ok(P.has('advent-2026'));assert.ok(!P.has('nope'));
  assert.strictEqual(P.longDate('2026-11-29'),'Sunday, November 29');assert.strictEqual(P.longDate('2026-12-24'),'Thursday, December 24');
  data.days.filter(d=>/Sunday of Advent/.test(d.marker)).forEach(d=>assert.match(P.longDate(d.date),/^Sunday/))});
test('today is highlighted by script only, on the matching date',()=>{const d=data.days[7];
  const on=P.dayHtml(d,{today:d.date,read:{}}),off=P.dayHtml(d,{today:'2026-01-01',read:{}});
  assert.match(on,/is-today/);assert.match(on,/aria-current="date"/);assert.doesNotMatch(off,/is-today/);
  assert.strictEqual(P.todayIso(new Date(2026,11,8,23,30)),'2026-12-08')});
test('mark as read is stored locally under bc-plan:<id>',()=>{const s=store();assert.deepStrictEqual(P.getRead('advent-2026',s),[]);
  P.setRead('advent-2026',[3,1],s);assert.strictEqual(s.m['bc-plan:advent-2026'],'{"v":1,"read":[1,3]}');assert.deepStrictEqual(P.getRead('advent-2026',s),[1,3]);
  assert.match(P.dayHtml(data.days[0],{today:'',read:{1:true}}),/is-read[^>]*>[\s\S]*checked/);
  P.setRead('advent-2026',[],s);assert.ok(!('bc-plan:advent-2026' in s.m));s.setItem('bc-plan:advent-2026','not json');assert.deepStrictEqual(P.getRead('advent-2026',s),[])});
test('every day links into the reader',()=>{assert.strictEqual(data.days.length,26);data.days.forEach(d=>{const h=P.dayHtml(d,{today:'',read:{}});assert.ok(h.includes('href="'+d.href+'"'));assert.match(d.href,/^#\/read\/[a-z0-9-]+\/pg-\d+\/\d+\/\d+$/)})});
