const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
// The reader runs in its own VM realm; plain() copies results into this realm for deepEqual.
const plain=v=>JSON.parse(JSON.stringify(v));
function core(){const window={};vm.runInNewContext(fs.readFileSync('scripts/reader.js','utf8'),{window});const c=window.BCReader.core,out={};for(const k of Object.keys(c))out[k]=typeof c[k]==='function'?(...a)=>{const r=c[k](...a);return r&&typeof r==='object'?plain(r):r}:c[k];return out}
const C=core();
const paras=['In the beginning was the Word.','And the Word was with God, and the Word was God.','The same was in the beginning with God.'];
const text=C.sectionText(paras);
test('anchors record the quote, its context, and offsets',()=>{
 const s=text.indexOf('the Word was God'),a=C.makeAnchor(text,s,s+16);
 assert.equal(a.exact,'the Word was God');assert.equal(a.start,s);assert.ok(a.prefix.endsWith('and '));assert.ok(a.suffix.startsWith('.'));
 assert.deepEqual(C.resolveAnchor(text,a),{start:s,end:s+16});
 assert.equal(C.makeAnchor(text,5,5),null);
});
test('anchors survive shifted offsets by matching the quote and context',()=>{
 const s=text.indexOf('the Word was God'),a=C.makeAnchor(text,s,s+16);
 const shifted='A new preface paragraph.\n\n'+text;
 assert.deepEqual(C.resolveAnchor(shifted,a),{start:s+26,end:s+42});
});
test('repeated phrases resolve to the occurrence with matching context',()=>{
 const i=text.indexOf('the Word',text.indexOf('was God')-20),a=C.makeAnchor(text,i,i+8);
 const r=C.resolveAnchor('Preface. '+text,a);assert.equal(r.start,i+9);
 const first=text.indexOf('the Word'),b=C.makeAnchor(text,first,first+8);
 assert.equal(C.resolveAnchor('XX'+text,b).start,first+2);
});
test('a quote that is gone resolves to null (shown as unplaced in My notes)',()=>{
 const a=C.makeAnchor(text,0,6);assert.equal(C.resolveAnchor('Completely different text.',a),null);
});
test('paragraph starts account for the blank-line separators',()=>{
 assert.deepEqual(C.paraStarts(paras),[0,paras[0].length+2,paras[0].length+paras[1].length+4]);
});
test('shortcut guard ignores typing, modifiers, and media controls',()=>{
 const ev=(key,target,extra)=>Object.assign({key,target:target||{tagName:'BODY'}},extra||{});
 assert.equal(C.shortcutAction(ev('j')),'next');assert.equal(C.shortcutAction(ev('ArrowRight')),'next');
 assert.equal(C.shortcutAction(ev('k')),'prev');assert.equal(C.shortcutAction(ev('ArrowLeft')),'prev');
 assert.equal(C.shortcutAction(ev('/')),'find');assert.equal(C.shortcutAction(ev('t')),'toc');assert.equal(C.shortcutAction(ev('n')),'notes');
 assert.equal(C.shortcutAction(ev('?')),'help');assert.equal(C.shortcutAction(ev('Escape')),'close');
 for(const tag of ['INPUT','TEXTAREA','SELECT','AUDIO','input'])assert.equal(C.shortcutAction(ev('j',{tagName:tag})),null,tag);
 assert.equal(C.shortcutAction(ev('n',{tagName:'DIV',isContentEditable:true})),null);
 assert.equal(C.shortcutAction(ev('Escape',{tagName:'TEXTAREA'})),'close');
 assert.equal(C.shortcutAction(ev('j',null,{ctrlKey:true})),null);assert.equal(C.shortcutAction(ev('/',null,{metaKey:true})),null);
 assert.equal(C.shortcutAction(ev('x')),null);
});
test('progress, recent list, and edition line',()=>{
 assert.deepEqual(C.progress(2,40),{section:3,total:40,percent:8});assert.deepEqual(C.progress(99,4),{section:4,total:4,percent:100});
 let L=C.recentUpsert([],{w:'a',e:'1',t:1});L=C.recentUpsert(L,{w:'b',e:'2',t:2});L=C.recentUpsert(L,{w:'a',e:'1',t:3});
 assert.deepEqual(L.map(x=>x.w),['a','b']);assert.equal(C.recentUpsert(Array.from({length:20},(_,i)=>({w:'w'+i,e:'e'})),{w:'z',e:'e'},8).length,8);
 assert.equal(C.shortName('Pusey, E. B. (Edward Bouverie), 1800-1882'),'E. B. Pusey');assert.equal(C.shortName('Hugh Pope, O.P.'),'Hugh Pope, O.P.');assert.equal(C.shortName('McMahon, Ella'),'Ella McMahon');
 const lib=JSON.parse(fs.readFileSync('data/library.json','utf8')),w=lib.works.find(x=>x.id==='confessions');
 assert.equal(C.editionLine(w,w.editions[0]),'Confessions, tr. E. B. Pusey, Project Gutenberg #3296');
 for(const work of lib.works)for(const e of work.editions.filter(e=>e.text))assert.ok(C.editionLine(work,e).startsWith(work.title),work.id);
});
test('notes export as Markdown and plain text in reading order',()=>{
 const lib=JSON.parse(fs.readFileSync('data/library.json','utf8')),w=lib.works.find(x=>x.id==='confessions'),e=w.editions[0];
 const items=[{id:'b',s:1,a:{exact:'second',p:40,po:0},c:'blue',n:''},{id:'a',s:0,a:{exact:'Great art Thou',p:3,po:0},c:'yellow',n:'Opening praise'}];
 const md=C.notesToMarkdown(w,e,items,'https://bibliothecacatholica.com/#/read/confessions/pg-3296');
 assert.ok(md.startsWith('# My notes: Confessions'));assert.ok(md.indexOf('## Section 1')<md.indexOf('## Section 2'));assert.match(md,/> Great art Thou\n\nNote: Opening praise/);
 const txt=C.notesToText(w,e,items);assert.match(txt,/Section 1:\n"Great art Thou"\nNote: Opening praise/);assert.ok(!txt.includes('## ')&&!txt.includes('> '));
});
test('backup import merges by id, keeps newer edits, and rejects other files',()=>{
 const cur={notes:{'w/e':[{id:'x',a:{exact:'a',p:0},ut:5,n:'old'}]},recent:[{w:'w',e:'e',t:5}],progress:{e:3}};
 const bk={format:'bibliotheca-catholica-reader-backup',notes:{'w/e':[{id:'x',a:{exact:'a',p:0},ut:9,n:'new'},{id:'y',a:{exact:'b',p:1},ut:1}],'v/f':[{id:'z',a:{exact:'c',p:2}},{bad:true}]},recent:[{w:'v',e:'f',t:7}],progress:{e:9,f:2}};
 const m=C.mergeBackup(cur,bk);
 assert.equal(m.added,2);assert.equal(m.updated,1);assert.equal(m.notes['w/e'].find(x=>x.id==='x').n,'new');assert.equal(m.notes['v/f'].length,1);
 assert.deepEqual(m.recent.map(r=>r.w),['v','w']);assert.deepEqual(m.progress,{e:3,f:2});
 assert.throws(()=>C.mergeBackup(cur,{notes:{}}),/not a Bibliotheca Catholica reader backup/);
});
test('index.html loads the reader after the library and before app.js',()=>{
 const html=fs.readFileSync('index.html','utf8'),lib=html.indexOf('scripts/library.js'),rd=html.indexOf('scripts/reader.js'),app=html.indexOf('app.js?');
 assert.ok(lib>0&&rd>lib&&app>rd);assert.match(html,/styles\/reader\.css\?v=/);assert.match(html,/viewport-fit=cover/);
});
test('print stylesheet keeps the edition line and the Gutenberg notice',()=>{
 const css=fs.readFileSync('styles/reader.css','utf8'),print=css.slice(css.indexOf('@media print'));
 assert.match(print,/\.print-edition\{display:block!important/);assert.match(print,/\.pg-notice\{display:block!important/);
 assert.ok(!/(^|[,}\s])\.pg-notice[^{]*\{display:none/.test(print.replace(/:not\(\.pg-notice\)/g,'')));
 const js=fs.readFileSync('scripts/reader.js','utf8');assert.match(js,/PG_NOTICE='This eBook is for the use of anyone anywhere/);
});
