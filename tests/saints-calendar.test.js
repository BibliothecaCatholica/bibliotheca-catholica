const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
// Full-year saints calendar (docs/SAINTS-CALENDAR.md): day pages are static; the app keeps them on their own URL,
// links to them by real path, and adds no analytics event.
const S=require('../scripts/saints.js');
const {calCount,dayHref,calLine}=S.core;
const app=fs.readFileSync('app.js','utf8');
const so=app.match(/^function staticOnly\(.*$/m);assert(so);
test('calendar helpers: counts, real-path day links, and a Hodie line only when the data has the day',()=>{
 const D={cal:{n:{'01-21':12,'02-29':1},total:13}};
 assert.equal(calCount(D,'01-21'),12);assert.equal(calCount(D,'03-03'),0);assert.equal(calCount({},'01-21'),0);
 assert.equal(dayHref(D,'01-21'),'/saints/calendar/01-21/');
 assert.equal(dayHref({},'01-21'),'#/saints/calendar/01-21','no calendar data: the old app view');
 assert.match(calLine(D,'01-21'),/href="\/saints\/calendar\/01-21\/">12 saints, blessed, and feasts in the full calendar for 21 January/);
 assert.match(calLine(D,'02-29'),/1 saint in the full calendar for 29 February/);
 assert.equal(calLine(D,'03-03'),'');
 assert.doesNotMatch(calLine(D,'01-21'),/data-|track|gtag/,'plain link, no analytics');
});
test('a day page stays static on its own URL; hash links fall through to the saints view, which redirects',()=>{
 const c={window:{BC_BOOT:'saints/calendar/01-21'},location:{hash:''}};vm.runInNewContext(so[0]+';this.staticOnly=staticOnly;',c);
 assert.equal(c.staticOnly('saints/calendar/01-21'),true);
 assert.equal(c.staticOnly('saints/calendar/01-22'),false,'not this page');
 c.location.hash='#/saints/calendar/01-21';assert.equal(c.staticOnly('saints/calendar/01-21'),false,'hash route: no loop');
 for(const r of ['saints/calendar','saints/calendar/13-01','saints/calendar/1-21','saints/agnes-of-rome'])assert.equal(c.staticOnly(r),false,r);
});
test('saints.js sends no new analytics event for the calendar',()=>{
 const src=fs.readFileSync('scripts/saints.js','utf8');
 assert.deepEqual([...src.matchAll(/track\('([a-z_]+)'/g)].map(m=>m[1]),['saint_open']);
});
test('when the calendar data is built, data/saints.js carries only per-day counts',()=>{
 const ctx={window:{}};vm.runInNewContext(fs.readFileSync('data/saints.js','utf8'),ctx);const cal=ctx.window.SAINTS_DATA.cal;
 if(!fs.existsSync('data/saints-calendar.json')){assert.equal(cal,undefined);return}
 assert.deepEqual(Object.keys(cal).sort(),['n','source','total']);
 for(const [k,v] of Object.entries(cal.n)){assert.match(k,/^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/);assert(Number.isInteger(v)&&v>0)}
});
