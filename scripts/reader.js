// Reader enhancements (v11): highlights and notes, progress and Continue reading, the sticky
// edition banner, the contents sidebar, keyboard shortcuts, mobile controls, print, and a11y.
// Everything here is stored in this browser's localStorage only; nothing is sent anywhere.
// localStorage keys (documented in AGENTS.md):
//   bc-notes:<workId>/<editionId>  {v:1,items:[highlight]}   highlights and notes
//   bc-recent                      [{w,e,p,n,t,title,author}] Continue reading (newest first)
//   bc-reading:<editionId>         section index (saved place; written by scripts/library.js)
//   bc:reader-size, bc:reader-spacing, bc-listen:<workId>, hub-theme (existing preferences)
(function(){
'use strict';
var W=typeof window!=='undefined'?window:this;
var NOTES_PREFIX='bc-notes:',RECENT_KEY='bc-recent',RECENT_MAX=8,CTX=40;
var COLORS=[['yellow','Yellow'],['green','Green'],['blue','Blue'],['pink','Pink']];

// ---------- pure core (unit-tested in tests/reader.test.js) ----------
function sectionText(paras){return paras.join('\n\n')}
function paraStarts(paras){var s=[],o=0;paras.forEach(function(p){s.push(o);o+=p.length+2});return s}
function makeAnchor(text,start,end){
 if(!(end>start))return null;
 return {start:start,end:end,exact:text.slice(start,end),prefix:text.slice(Math.max(0,start-CTX),start),suffix:text.slice(end,end+CTX)};
}
function commonTail(a,b){var n=0;while(n<a.length&&n<b.length&&a[a.length-1-n]===b[b.length-1-n])n++;return n}
function commonHead(a,b){var n=0;while(n<a.length&&n<b.length&&a[n]===b[n])n++;return n}
// Returns {start,end} in text, or null if the quoted passage cannot be found.
function resolveAnchor(text,a,hint){
 if(!a||!a.exact)return null;var L=a.exact.length;
 var at=typeof hint==='number'&&hint>=0?hint:a.start;
 if(typeof at==='number'&&text.substr(at,L)===a.exact)return {start:at,end:at+L};
 var best=null,bestScore=-Infinity,i=text.indexOf(a.exact);
 while(i>=0){
  var score=commonTail(a.prefix||'',text.slice(Math.max(0,i-CTX),i))+commonHead(a.suffix||'',text.slice(i+L,i+L+CTX))-(typeof at==='number'?Math.abs(i-at)/1e6:0);
  if(score>bestScore){bestScore=score;best=i}
  i=text.indexOf(a.exact,i+1);
 }
 return best==null?null:{start:best,end:best+L};
}
// Keyboard shortcuts must never fire while the reader is typing or using a media control.
function isTypingTarget(el){
 if(!el)return false;var tag=String(el.tagName||'').toUpperCase();
 if(tag==='INPUT'||tag==='TEXTAREA'||tag==='SELECT'||tag==='AUDIO'||tag==='VIDEO')return true;
 if(el.isContentEditable)return true;
 return false;
}
function shortcutAction(ev){
 if(!ev||ev.defaultPrevented||ev.ctrlKey||ev.metaKey||ev.altKey||ev.isComposing)return null;
 if(isTypingTarget(ev.target))return ev.key==='Escape'?'close':null;
 switch(ev.key){
  case 'ArrowLeft':case 'k':return 'prev';
  case 'ArrowRight':case 'j':return 'next';
  case '/':return 'find';
  case 't':return 'toc';
  case 'n':return 'notes';
  case 'Escape':return 'close';
  case '?':return 'help';
 }
 return null;
}
function progress(page,total){total=Math.max(1,total|0);page=Math.max(0,Math.min(total-1,page|0));return {section:page+1,total:total,percent:Math.round((page+1)/total*100)}}
function recentUpsert(list,item,max){
 list=(Array.isArray(list)?list:[]).filter(function(x){return x&&!(x.w===item.w&&x.e===item.e)});
 list.unshift(item);return list.slice(0,max||RECENT_MAX);
}
function shortName(name){
 var n=String(name||'').replace(/,\s*(\d{3,4}\??-?(\d{3,4})?|fl\.[^,]*|active[^,]*)$/,'').replace(/\s*\([^)]*\)/g,'').trim();
 var m=n.match(/^([^,]+),\s*(.+)$/);
 if(m&&!/^(O\.?P\.?|S\.?J\.?|O\.?S\.?B\.?|O\.?F\.?M\.?|C\.?Ss\.?R\.?|Jr\.?|Sr\.?)$/.test(m[2]))n=m[2]+' '+m[1];
 return n;
}
function editionLine(w,e){
 var cs=(e&&e.contributors)||[],tr=cs.filter(function(c){return /translator/i.test(c.role)}),ed=cs.filter(function(c){return /^editor|^translator and editor/i.test(c.role)}),ad=cs.filter(function(c){return /adapter/i.test(c.role)});
 var who='';
 if(tr.length)who='tr. '+shortName(tr[0].name)+(tr.length>1?' and others':'');
 else if(ad.length)who='adapted by '+shortName(ad[0].name);
 else if(ed.length)who='ed. '+shortName(ed[0].name);
 var src=/gutenberg\.org/.test((e&&e.source)||'')?(e.label||'Project Gutenberg'):(e&&e.label)||'';
 return [w.title+(who?', '+who:''),src].filter(Boolean).join(', ');
}
function sortedItems(items){return items.slice().sort(function(a,b){return (a.a.p-b.a.p)||(a.a.po-b.a.po)})}
function notesToMarkdown(w,e,items,url){
 var out=['# My notes: '+w.title,'',w.author+'. Reading: '+editionLine(w,e)+'.','Exported from Bibliotheca Catholica'+(url?' ('+url+')':'')+'.',''];
 var last=null;
 sortedItems(items).forEach(function(it){
  if(it.s!==last){out.push('## Section '+(it.s+1),'');last=it.s}
  out.push(it.a.exact.split(/\n/).map(function(l){return '> '+l}).join('\n'),'');
  if(it.n)out.push('Note: '+it.n,'');
 });
 if(!items.length)out.push('_No highlights or notes yet._','');
 return out.join('\n');
}
function notesToText(w,e,items,url){
 var out=['My notes: '+w.title,w.author+'. Reading: '+editionLine(w,e)+'.','Exported from Bibliotheca Catholica'+(url?' ('+url+')':'')+'.',''];
 sortedItems(items).forEach(function(it){out.push('Section '+(it.s+1)+':','"'+it.a.exact+'"');if(it.n)out.push('Note: '+it.n);out.push('')});
 if(!items.length)out.push('No highlights or notes yet.');
 return out.join('\n');
}
function validItem(it){return it&&typeof it.id==='string'&&it.a&&typeof it.a.exact==='string'&&typeof it.a.p==='number'}
// Merge a backup into existing data: newer `ut` wins per highlight id; existing saved places win.
function mergeBackup(cur,bk){
 if(!bk||bk.format!=='bibliotheca-catholica-reader-backup')throw Error('This file is not a Bibliotheca Catholica reader backup.');
 var res={notes:{},recent:(cur.recent||[]).slice(),progress:Object.assign({},cur.progress||{}),added:0,updated:0};
 Object.keys(cur.notes||{}).forEach(function(k){res.notes[k]=(cur.notes[k]||[]).slice()});
 Object.keys(bk.notes||{}).forEach(function(k){
  var list=res.notes[k]||(res.notes[k]=[]);
  (bk.notes[k]||[]).filter(validItem).forEach(function(it){
   var i=list.findIndex(function(x){return x.id===it.id});
   if(i<0){list.push(it);res.added++}else if((it.ut||0)>(list[i].ut||0)){list[i]=it;res.updated++}
  });
 });
 (bk.recent||[]).forEach(function(r){if(!r||!r.w||!r.e)return;var i=res.recent.findIndex(function(x){return x.w===r.w&&x.e===r.e});if(i<0)res.recent.push(r);else if((r.t||0)>(res.recent[i].t||0))res.recent[i]=r});
 res.recent.sort(function(a,b){return (b.t||0)-(a.t||0)});res.recent=res.recent.slice(0,RECENT_MAX);
 Object.keys(bk.progress||{}).forEach(function(k){if(!(k in res.progress)&&Number.isInteger(bk.progress[k]))res.progress[k]=bk.progress[k]});
 return res;
}
var core={sectionText:sectionText,paraStarts:paraStarts,makeAnchor:makeAnchor,resolveAnchor:resolveAnchor,isTypingTarget:isTypingTarget,shortcutAction:shortcutAction,progress:progress,recentUpsert:recentUpsert,shortName:shortName,editionLine:editionLine,notesToMarkdown:notesToMarkdown,notesToText:notesToText,mergeBackup:mergeBackup,NOTES_PREFIX:NOTES_PREFIX,RECENT_KEY:RECENT_KEY};
W.BCReader={core:core,enhance:function(){},continueRow:function(){return ''}};
if(typeof document==='undefined'||!document.addEventListener)return;

// ---------- storage ----------
function lsGet(k,d){try{var v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(err){return d}}
function lsSet(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(err){return false}}
function notesKey(w,e){return NOTES_PREFIX+w+'/'+e}
function loadItems(wid,eid){var d=lsGet(notesKey(wid,eid),null);return d&&Array.isArray(d.items)?d.items.filter(validItem):[]}
function saveItems(wid,eid,items){return lsSet(notesKey(wid,eid),{v:1,items:items})}
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function lib(){return W.LIBRARY_DATA||{works:[]}}
function findWE(wid,eid){var w=lib().works.find(function(x){return x.id===wid}),e=w&&w.editions.find(function(x){return x.id===eid&&x.text});return e?{w:w,e:e}:null}
function uid(){return 'h'+Date.now().toString(36)+Math.random().toString(36).slice(2,7)}
function announce(msg){var s=document.getElementById('bc-live');if(!s){s=document.createElement('div');s.id='bc-live';s.className='sr-only';s.setAttribute('role','status');s.setAttribute('aria-live','polite');document.body.appendChild(s)}s.textContent='';setTimeout(function(){s.textContent=msg},30)}
function download(name,text,type){var b=new Blob([text],{type:type||'text/plain'}),u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download=name;document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(u);a.remove()},500)}

// ---------- Continue reading ----------
function recentList(){return (lsGet(RECENT_KEY,[])||[]).filter(function(r){return r&&findWE(r.w,r.e)})}
function continueRow(){
 var L=recentList().slice(0,6);if(!L.length)return '';
 return '<section class="continue-reading" aria-labelledby="cr-h"><div class="cr-head"><div><div class="eyebrow">Your reading</div><h2 id="cr-h">Continue reading</h2></div><button type="button" class="btn ghost cr-clear" data-bc-clear-recent>Clear list</button></div><ul class="cr-list">'+L.map(function(r){var x=findWE(r.w,r.e),pr=progress(r.p,r.n);
  return '<li><a href="#/read/'+esc(r.w)+'/'+esc(r.e)+'/'+(pr.section-1)+'"><b>'+esc(x.w.title)+'</b><span>'+esc(x.w.author)+'</span><span class="cr-pos">Section '+pr.section+' of '+pr.total+' · '+pr.percent+'%</span><span class="bc-bar" role="progressbar" aria-label="Progress in '+esc(x.w.title)+'" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'+pr.percent+'"><i style="width:'+pr.percent+'%"></i></span></a><button type="button" class="cr-x" data-bc-remove-recent="'+esc(r.w+'|'+r.e)+'" aria-label="Remove '+esc(x.w.title)+' from Continue reading">×</button></li>'}).join('')+'</ul><p class="small cr-note">Saved only in this browser. Nothing leaves this device.</p></section>';
}
document.addEventListener('click',function(ev){
 var c=ev.target.closest&&ev.target.closest('[data-bc-clear-recent]');
 if(c){lsSet(RECENT_KEY,[]);var s=c.closest('.continue-reading');if(s)s.remove();announce('Continue reading list cleared.');return}
 var r=ev.target.closest&&ev.target.closest('[data-bc-remove-recent]');
 if(r){var p=r.getAttribute('data-bc-remove-recent').split('|'),L=(lsGet(RECENT_KEY,[])||[]).filter(function(x){return !(x.w===p[0]&&x.e===p[1])});lsSet(RECENT_KEY,L);var li=r.closest('li'),sec=r.closest('.continue-reading'),next=li&&(li.nextElementSibling||li.previousElementSibling);if(li)li.remove();if(sec&&!sec.querySelector('li')){sec.remove()}else if(next){(next.querySelector('a')||next).focus()}announce('Removed from Continue reading.')}
});

// ---------- reader state ----------
var R=null; // current reader context
var UI={panel:null,opener:null,panelOpen:false,panelFor:null,bar:null,help:null,tool:null,sel:null,lastY:0};
function inReader(){return R&&document.body.contains(R.root)&&location.hash.indexOf('#/read/')===0}
function paraEls(){return Array.prototype.slice.call(R.article.querySelectorAll('p[id^="reading-p-"]'))}

function enhance(ctx){
 var main=document.getElementById('main'),article=document.getElementById('reading-text');if(!main||!article)return;
 var w=ctx.w,e=ctx.e,pr=progress(ctx.page,ctx.total);
 R={w:w,e:e,blocks:ctx.blocks,size:ctx.size,total:ctx.total,page:ctx.page,base:ctx.base,headings:ctx.headings||[],article:article,root:null,items:loadItems(w.id,e.id)};
 // Recent list (Continue reading)
 var rec=lsGet(RECENT_KEY,[]);lsSet(RECENT_KEY,recentUpsert(rec,{w:w.id,e:e.id,p:ctx.page,n:ctx.total,t:Date.now(),title:w.title,author:w.author},RECENT_MAX));
 // Layout: sidebar + main column
 var shell=document.createElement('div');shell.className='reader-shell';
 var side=document.createElement('aside');side.className='reader-side';side.id='reader-side';side.setAttribute('aria-labelledby','rs-h');side.tabIndex=-1;
 side.innerHTML=tocHTML(pr);
 var col=document.createElement('div');col.className='reader-col';
 while(main.firstChild)col.appendChild(main.firstChild);
 shell.appendChild(side);shell.appendChild(col);main.appendChild(shell);R.root=shell;
 // Banner
 var line=editionLine(w,e),banner=document.createElement('div');banner.className='reader-banner';banner.setAttribute('role','region');banner.setAttribute('aria-label','Edition and progress');banner.style.setProperty('--rb-pct',pr.percent+'%');
 banner.innerHTML='<button type="button" class="rb-chip" aria-expanded="false" aria-controls="rb-full" title="Show the full edition line"><span class="rb-chip-t">'+esc(w.title)+'</span><span class="rb-chip-p">§'+pr.section+'/'+pr.total+'</span></button>'+
  '<div class="rb-full" id="rb-full"><span class="rb-ed"><span class="rb-lbl">Reading:</span> '+esc(line)+'</span>'+
  '<span class="rb-prog"><span class="rb-sec">Section '+pr.section+' of '+pr.total+' · '+pr.percent+'%</span><span class="bc-bar" role="progressbar" aria-label="Progress through this work" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'+pr.percent+'" aria-valuetext="Section '+pr.section+' of '+pr.total+', '+pr.percent+' percent"><i style="width:'+pr.percent+'%"></i></span></span></div>'+
  '<div class="rb-actions" role="toolbar" aria-label="Reader tools"><button type="button" class="rb-btn rb-toc" data-act="toc" aria-controls="reader-side" aria-keyshortcuts="t">Contents</button><button type="button" class="rb-btn" data-act="notes" aria-controls="bc-notes" aria-keyshortcuts="n">My notes <span class="rb-count">'+R.items.length+'</span></button><button type="button" class="rb-btn" data-act="find" aria-keyshortcuts="/">Find</button>'+
  '<details class="rb-print"><summary class="rb-btn">Print / save as PDF</summary><div class="rb-menu"><button type="button" data-act="print-section">This section</button><button type="button" data-act="print-work">Whole work</button></div></details><button type="button" class="rb-btn rb-help" data-act="help" aria-label="Keyboard shortcuts" aria-keyshortcuts="?">?</button></div>'+
  '<div class="print-edition">'+esc(w.author)+'. Reading: '+esc(line)+'. Section '+pr.section+' of '+pr.total+'. bibliothecacatholica.com/'+esc(ctx.base)+'</div>';
 var head=col.querySelector('.page-head');col.insertBefore(banner,head?head.nextSibling:col.firstChild);
 banner.querySelector('.rb-chip').onclick=function(){var o=banner.classList.toggle('expanded');this.setAttribute('aria-expanded',o?'true':'false')};
 banner.addEventListener('click',function(ev){var b=ev.target.closest('[data-act]');if(!b)return;var d=b.closest('details');if(d)d.open=false;act(b.getAttribute('data-act'),b)});
 // Pagination a11y
 Array.prototype.forEach.call(col.querySelectorAll('.reader-pagination a'),function(a){a.setAttribute('aria-label',/Previous/.test(a.textContent)?'Previous section':'Next section');a.setAttribute('rel',/Previous/.test(a.textContent)?'prev':'next')});
 var find=col.querySelector('#reader-find');if(find){var fd=find.closest('details');if(fd)fd.id='reader-find-panel'}
 var tools=col.querySelector('.reader-tools');if(tools)tools.setAttribute('aria-label','Display settings');
 article.setAttribute('aria-label','Reading text, section '+pr.section+' of '+pr.total);
 // Highlights
 paintAll();
 article.addEventListener('click',function(ev){var m=ev.target.closest('mark.bc-hl');if(m&&!String(getSelection()).length)openPanel(m,m.getAttribute('data-id'))});
 // Mobile bar, panel, sidebar
 ensureBar();refreshPanel();measure();
 side.addEventListener('click',function(ev){var a=ev.target.closest('a');if(a&&document.body.classList.contains('toc-open'))closeToc(false)});
 // Focus requests (Go to from the notes panel) and anchors
 var want=null;try{want=sessionStorage.getItem('bc-hl-focus');sessionStorage.removeItem('bc-hl-focus')}catch(err){}
 if(want){var m=article.querySelector('mark[data-id="'+want+'"]');if(m)setTimeout(function(){flash(m)},60)}
 else if(ctx.anchor!=null){var t=document.getElementById('reading-p-'+Number(ctx.anchor));if(t)setTimeout(function(){t.scrollIntoView({block:'start'})},30)}
 if(UI.panelOpen&&UI.panelFor===e.id)showPanel(false);else hidePanel(false);
}
function tocHTML(pr){
 var cur=R.page,hs=R.headings,base=R.base,size=R.size;
 var sec=Array.from({length:R.total},function(_,i){return '<li><a href="'+base+'/'+i+'"'+(i===cur?' aria-current="page"':'')+' aria-label="Section '+(i+1)+' of '+R.total+'">'+(i+1)+'</a></li>'}).join('');
 return '<div class="rs-head"><h2 id="rs-h">Contents</h2><button type="button" class="rs-close" aria-label="Close contents">×</button></div>'+
  (hs.length?'<nav aria-label="Headings in this work"><ul class="rs-heads">'+hs.map(function(h){var s=Math.floor(h.index/size);return '<li'+(s===cur?' class="here"':'')+'><a href="'+base+'/'+s+'/'+h.index+'"'+(s===cur?' aria-current="location"':'')+'>'+esc(h.title)+'</a></li>'}).join('')+'</ul></nav>':'<p class="small">This source has no chapter headings to list; jump by section instead.</p>')+
  '<nav aria-label="Reading sections"><h3 class="rs-sub">Sections</h3><ol class="rs-secs">'+sec+'</ol></nav>';
}
// ---------- highlight painting ----------
function sectionModel(){var ps=paraEls(),texts=ps.map(function(p){return p.textContent}),starts=paraStarts(texts);return {ps:ps,texts:texts,starts:starts,text:sectionText(texts),idx:ps.map(function(p){return Number(p.id.slice(10))})}}
function unpaint(){Array.prototype.forEach.call(R.article.querySelectorAll('mark.bc-hl'),function(m){var p=m.parentNode;while(m.firstChild)p.insertBefore(m.firstChild,m);p.removeChild(m);p.normalize()})}
function wrapLocal(p,s,e,it){
 var tw=document.createTreeWalker(p,NodeFilter.SHOW_TEXT,null),pos=0,n,todo=[];
 while((n=tw.nextNode())){var a=pos,b=pos+n.length;pos=b;if(b<=s||a>=e)continue;todo.push([n,Math.max(s,a)-a,Math.min(e,b)-a])}
 todo.forEach(function(t,k){var node=t[0];if(t[2]<node.length)node.splitText(t[2]);if(t[1]>0)node=node.splitText(t[1]);var m=document.createElement('mark');m.className='bc-hl hl-'+(it.c||'yellow')+(it.n?' has-note':'');m.setAttribute('data-id',it.id);if(it.n)m.title='Note: '+it.n.slice(0,200);node.parentNode.insertBefore(m,node);m.appendChild(node)});
}
function paintAll(){
 unpaint();var M=sectionModel();R.model=M;R.orphans={};
 var lo=R.page*R.size,hi=lo+R.size;
 R.items.forEach(function(it){
  if(it.a.p<lo||it.a.p>=hi)return;
  var k=M.idx.indexOf(it.a.p),hint=k>=0?M.starts[k]+(it.a.po||0):undefined,r=resolveAnchor(M.text,it.a,hint);
  if(!r){R.orphans[it.id]=true;return}
  M.ps.forEach(function(p,i){var ps=M.starts[i],pe=ps+M.texts[i].length;if(r.end<=ps||r.start>=pe)return;wrapLocal(p,Math.max(r.start,ps)-ps,Math.min(r.end,pe)-ps,it)});
 });
}
function pointOffset(node,off){
 var p=node.nodeType===1?node:node.parentNode;p=p&&p.closest?p.closest('p[id^="reading-p-"]'):null;
 if(!p){ // boundary between paragraphs
  if(node.nodeType===1){var c=node.childNodes[off];if(c&&c.matches&&c.matches('p[id^="reading-p-"]'))return {p:c,o:0};var b=node.childNodes[off-1];if(b&&b.matches&&b.matches('p[id^="reading-p-"]'))return {p:b,o:b.textContent.length}}
  return null;
 }
 if(!R.article.contains(p))return null;
 var r=document.createRange();r.setStart(p,0);r.setEnd(node,off);return {p:p,o:r.toString().length};
}
function selectionAnchor(){
 var s=getSelection();if(!s||s.isCollapsed||!s.rangeCount)return null;var rg=s.getRangeAt(0);
 if(!R.article.contains(rg.commonAncestorContainer)&&rg.commonAncestorContainer!==R.article)return null;
 var a=pointOffset(rg.startContainer,rg.startOffset),b=pointOffset(rg.endContainer,rg.endOffset);if(!a||!b)return null;
 var M=sectionModel(),ia=M.ps.indexOf(a.p),ib=M.ps.indexOf(b.p);if(ia<0||ib<0)return null;
 var start=M.starts[ia]+a.o,end=M.starts[ib]+b.o;
 while(start<end&&/\s/.test(M.text[start]))start++;while(end>start&&/\s/.test(M.text[end-1]))end--;
 if(end-start<1)return null;if(end-start>6000)end=start+6000;
 var an=makeAnchor(M.text,start,end);
 for(var k=M.starts.length-1;k>=0;k--){if(M.starts[k]<=start){an.p=M.idx[k];an.po=start-M.starts[k];break}}
 return {anchor:an,rect:rg.getBoundingClientRect()};
}
// ---------- selection toolbar ----------
function toolbar(){
 if(UI.tool)return UI.tool;
 var t=document.createElement('div');t.className='hl-toolbar';t.setAttribute('role','toolbar');t.setAttribute('aria-label','Highlight the selected text');t.hidden=true;
 t.innerHTML=COLORS.map(function(c){return '<button type="button" class="hl-sw hl-'+c[0]+'" data-c="'+c[0]+'" aria-label="Highlight '+c[1].toLowerCase()+'"></button>'}).join('')+'<button type="button" class="hl-addnote" data-note>Add note</button>';
 t.addEventListener('mousedown',function(ev){ev.preventDefault()});
 t.addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b||!UI.sel||!inReader())return;var withNote=b.hasAttribute('data-note');addHighlight(UI.sel,withNote?'yellow':b.getAttribute('data-c'),withNote)});
 document.body.appendChild(t);UI.tool=t;return t;
}
function hideTool(){if(UI.tool)UI.tool.hidden=true;UI.sel=null}
var selT=null;
document.addEventListener('selectionchange',function(){clearTimeout(selT);selT=setTimeout(function(){
 if(!inReader()){hideTool();return}var s=selectionAnchor();if(!s){if(UI.tool&&!UI.tool.contains(document.activeElement))hideTool();return}
 UI.sel=s.anchor;var t=toolbar();t.hidden=false;var r=s.rect,coarse=matchMedia('(pointer:coarse)').matches,tw=t.offsetWidth||220,th=t.offsetHeight||44;
 var top=coarse||r.top<130?r.bottom+10:r.top-th-8;top=Math.min(Math.max(top,8),innerHeight-th-80);
 var left=Math.min(Math.max(8,r.left+r.width/2-tw/2),innerWidth-tw-8);t.style.top=(top+scrollY)+'px';t.style.left=left+'px';
},180)});
function addHighlight(anchor,color,withNote){
 var it={id:uid(),s:Math.floor(anchor.p/R.size),a:anchor,c:color,n:'',ct:Date.now(),ut:Date.now()};
 R.items.push(it);persist();hideTool();try{getSelection().removeAllRanges()}catch(err){}
 paintAll();refreshPanel();announce('Highlight saved'+(withNote?'. Add your note.':'.'));
 if(withNote){showPanel(true);editItem(it.id)}
}
function persist(){if(!saveItems(R.w.id,R.e.id,R.items))announce('Could not save: this browser is blocking local storage.');var c=R.root&&R.root.parentNode&&document.querySelector('.rb-count');if(c)c.textContent=R.items.length;var bc=document.querySelector('.rbar-count');if(bc)bc.textContent=R.items.length}
function flash(m){m.scrollIntoView({block:'center'});m.classList.add('hl-flash');setTimeout(function(){m.classList.remove('hl-flash')},1600)}
// ---------- notes panel ----------
function panel(){
 if(UI.panel)return UI.panel;
 var p=document.createElement('aside');p.id='bc-notes';p.className='notes-panel';p.setAttribute('role','dialog');p.setAttribute('aria-modal','false');p.setAttribute('aria-labelledby','np-h');p.hidden=true;
 p.innerHTML='<div class="np-head"><h2 id="np-h" tabindex="-1">My notes</h2><button type="button" class="np-close" aria-label="Close my notes">×</button></div><p class="small np-privacy">Your highlights and notes are saved only in this browser’s local storage. Nothing leaves this device.</p><p class="small np-how">Select text in the reading to highlight it in a color or add a note.</p><ol class="np-list"></ol>'+
  '<div class="np-tools"><h3>Export &amp; backup</h3><div class="np-row"><button type="button" class="btn ghost" data-np="md">Notes as Markdown</button><button type="button" class="btn ghost" data-np="txt">Notes as plain text</button></div><div class="np-row"><button type="button" class="btn ghost" data-np="backup">Back up everything (JSON)</button><label class="btn ghost np-import">Restore a backup<input type="file" accept="application/json,.json" data-np="import"></label></div><p class="small np-status" role="status"></p></div>';
 p.querySelector('.np-close').onclick=function(){hidePanel(true)};
 p.addEventListener('click',onPanelClick);
 p.querySelector('input[data-np="import"]').onchange=function(ev){var f=ev.target.files[0];if(!f)return;f.text().then(function(t){importBackup(JSON.parse(t))}).catch(function(err){status(err&&err.message&&/backup/.test(err.message)?err.message:'That file could not be read as a backup.')});ev.target.value=''};
 document.body.appendChild(p);UI.panel=p;return p;
}
function status(m){var s=UI.panel&&UI.panel.querySelector('.np-status');if(s)s.textContent=m}
function refreshPanel(){
 var p=panel();if(!R)return;
 var items=sortedItems(R.items);
 p.querySelector('#np-h').textContent='My notes: '+R.w.title;
 p.querySelector('.np-list').innerHTML=items.length?items.map(function(it){var here=it.s===R.page,orph=here&&R.orphans&&R.orphans[it.id];
  return '<li class="np-item" data-id="'+it.id+'"><blockquote class="np-q hl-'+esc(it.c)+'">'+esc(it.a.exact.length>320?it.a.exact.slice(0,320)+'…':it.a.exact)+'</blockquote><div class="small np-meta">Section '+(it.s+1)+(here?' · this section':'')+(orph?' · <em>this passage could not be found in the current text</em>':'')+'</div>'+(it.n?'<p class="np-note">'+esc(it.n)+'</p>':'')+
  '<div class="np-acts"><button type="button" data-np="go">Go to</button><button type="button" data-np="edit">'+(it.n?'Edit note':'Add note')+'</button><button type="button" data-np="del" aria-label="Delete this highlight">Delete</button></div></li>'}).join(''):'<li class="np-empty">No highlights yet in this work.</li>';
}
function onPanelClick(ev){
 var b=ev.target.closest('button[data-np]');if(!b)return;var k=b.getAttribute('data-np'),li=b.closest('.np-item'),id=li&&li.getAttribute('data-id');
 if(k==='md')return download(R.w.id+'-notes.md',notesToMarkdown(R.w,R.e,R.items,location.origin+'/'+R.base),'text/markdown');
 if(k==='txt')return download(R.w.id+'-notes.txt',notesToText(R.w,R.e,R.items,location.origin+'/'+R.base),'text/plain');
 if(k==='backup')return download('bibliotheca-catholica-reader-backup-'+new Date().toISOString().slice(0,10)+'.json',JSON.stringify(collectBackup(),null,1),'application/json');
 var it=R.items.find(function(x){return x.id===id});if(!it)return;
 if(k==='go'){if(it.s===R.page){var m=R.article.querySelector('mark[data-id="'+id+'"]');if(m){if(matchMedia('(max-width:760px)').matches)hidePanel(false);flash(m)}}else{try{sessionStorage.setItem('bc-hl-focus',id)}catch(err){}if(matchMedia('(max-width:760px)').matches)UI.panelOpen=false;location.hash=R.base+'/'+it.s}}
 else if(k==='edit')editItem(id);
 else if(k==='del'){R.items=R.items.filter(function(x){return x.id!==id});persist();paintAll();refreshPanel();announce('Highlight deleted.');var f=UI.panel.querySelector('.np-item button')||UI.panel.querySelector('#np-h');f.focus()}
 else if(k==='save'||k==='cancel'){if(k==='save'){it.n=li.querySelector('textarea').value.trim();var c=li.querySelector('input[name="np-c"]:checked');if(c)it.c=c.value;it.ut=Date.now();persist();paintAll();announce('Note saved.')}refreshPanel();var again=UI.panel.querySelector('.np-item[data-id="'+id+'"] button[data-np="edit"]');if(again)again.focus()}
}
function editItem(id){
 var it=R.items.find(function(x){return x.id===id}),li=UI.panel.querySelector('.np-item[data-id="'+id+'"]');if(!it||!li)return;
 var acts=li.querySelector('.np-acts'),old=li.querySelector('.np-note');if(old)old.remove();
 acts.outerHTML='<div class="np-edit"><label class="np-lbl" for="np-t-'+id+'">Note</label><textarea id="np-t-'+id+'" rows="4">'+esc(it.n)+'</textarea><fieldset class="np-colors"><legend>Color</legend>'+COLORS.map(function(c){return '<label><input type="radio" name="np-c" value="'+c[0]+'"'+(it.c===c[0]?' checked':'')+'><span class="hl-sw hl-'+c[0]+'" aria-hidden="true"></span>'+c[1]+'</label>'}).join('')+'</fieldset><div class="np-acts"><button type="button" class="btn" data-np="save">Save</button><button type="button" data-np="cancel">Cancel</button></div></div>';
 var ta=li.querySelector('textarea');li.scrollIntoView({block:'nearest'});ta.focus();
 ta.addEventListener('keydown',function(ev){if(ev.key==='Enter'&&(ev.metaKey||ev.ctrlKey)){ev.preventDefault();li.querySelector('[data-np="save"]').click()}});
}
function openPanel(opener,focusId){UI.opener=opener||document.activeElement;showPanel(true);if(focusId){var li=UI.panel.querySelector('.np-item[data-id="'+focusId+'"]');if(li){li.scrollIntoView({block:'nearest'});li.classList.add('np-hot');setTimeout(function(){li.classList.remove('np-hot')},1500);var b=li.querySelector('button');if(b)b.focus()}}}
function showPanel(focus){var p=panel();refreshPanel();p.hidden=false;document.body.classList.add('notes-open');UI.panelOpen=true;UI.panelFor=R.e.id;setExpanded('notes',true);if(focus)p.querySelector('#np-h').focus()}
function hidePanel(restore){if(!UI.panel)return;var was=!UI.panel.hidden;UI.panel.hidden=true;document.body.classList.remove('notes-open');UI.panelOpen=false;setExpanded('notes',false);if(restore&&was){var o=UI.opener;UI.opener=null;(o&&document.body.contains(o)?o:document.querySelector('.rb-btn[data-act="notes"]')||R.article).focus()}}
function setExpanded(act,on){Array.prototype.forEach.call(document.querySelectorAll('[data-act="'+act+'"]'),function(b){b.setAttribute('aria-expanded',on?'true':'false')})}
// ---------- backup ----------
function collectBackup(){
 var notes={},progressMap={},prefs={};
 for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);
  if(k.indexOf(NOTES_PREFIX)===0){var d=lsGet(k,null);if(d&&Array.isArray(d.items))notes[k.slice(NOTES_PREFIX.length)]=d.items}
  else if(k.indexOf('bc-reading:')===0){var v=Number(localStorage.getItem(k));if(Number.isInteger(v))progressMap[k.slice(11)]=v}
  else if(k==='bc:reader-size'||k==='bc:reader-spacing'||k==='hub-theme')prefs[k]=localStorage.getItem(k)}
 return {format:'bibliotheca-catholica-reader-backup',version:1,exported:new Date().toISOString(),site:'https://bibliothecacatholica.com',note:'Highlights, notes, reading progress, and reader preferences from this browser. Restore it on the reader’s My notes panel.',notes:notes,recent:lsGet(RECENT_KEY,[]),progress:progressMap,prefs:prefs};
}
function importBackup(bk){
 var cur=collectBackup(),m;try{m=mergeBackup(cur,bk)}catch(err){status(err.message);return}
 Object.keys(m.notes).forEach(function(k){lsSet(NOTES_PREFIX+k,{v:1,items:m.notes[k]})});lsSet(RECENT_KEY,m.recent);
 Object.keys(m.progress).forEach(function(k){try{localStorage.setItem('bc-reading:'+k,String(m.progress[k]))}catch(err){}});
 Object.keys(bk.prefs||{}).forEach(function(k){if(/^(bc:reader-size|bc:reader-spacing|hub-theme)$/.test(k)&&localStorage.getItem(k)==null)try{localStorage.setItem(k,String(bk.prefs[k]))}catch(err){}});
 if(R){R.items=loadItems(R.w.id,R.e.id);persist();paintAll();refreshPanel()}
 status('Backup restored: '+m.added+' highlights added and '+m.updated+' updated.');
}
// ---------- contents sidebar / drawer ----------
function wide(){return matchMedia('(min-width:1100px)').matches}
function openToc(){var s=document.getElementById('reader-side');if(!s)return;if(wide()){var a=s.querySelector('[aria-current]')||s.querySelector('a');(a||s).focus();return}UI.tocOpener=document.activeElement;document.body.classList.add('toc-open');setExpanded('toc',true);s.setAttribute('role','dialog');s.setAttribute('aria-modal','true');var c=s.querySelector('.rs-close');c.onclick=function(){closeToc(true)};var cur=s.querySelector('[aria-current]');if(cur)cur.scrollIntoView({block:'center'});c.focus()}
function closeToc(restore){var s=document.getElementById('reader-side');document.body.classList.remove('toc-open');setExpanded('toc',false);if(s){s.removeAttribute('role');s.removeAttribute('aria-modal')}if(restore&&UI.tocOpener&&document.body.contains(UI.tocOpener))UI.tocOpener.focus();UI.tocOpener=null}
// ---------- help overlay ----------
function openHelp(){
 if(!UI.help){var h=document.createElement('div');h.className='kb-help';h.id='kb-help';h.setAttribute('role','dialog');h.setAttribute('aria-modal','true');h.setAttribute('aria-labelledby','kb-h');h.hidden=true;
  h.innerHTML='<div class="kb-box"><div class="np-head"><h2 id="kb-h" tabindex="-1">Keyboard shortcuts</h2><button type="button" class="kb-close" aria-label="Close keyboard shortcuts">×</button></div><dl class="kb-list">'+[['← or k','Previous section'],['→ or j','Next section'],['/','Find in this work'],['t','Contents'],['n','My notes'],['Esc','Close a panel'],['?','Show this help']].map(function(x){return '<div><dt><kbd>'+x[0].split(' or ').join('</kbd> or <kbd>')+'</kbd></dt><dd>'+x[1]+'</dd></div>'}).join('')+'</dl><p class="small">Shortcuts are off while you type in a field. Select text to highlight it or add a note.</p></div>';
  h.addEventListener('click',function(ev){if(ev.target===h||ev.target.closest('.kb-close'))closeHelp()});
  h.addEventListener('keydown',function(ev){if(ev.key==='Tab'){ev.preventDefault();h.querySelector('.kb-close').focus()}});
  document.body.appendChild(h);UI.help=h}
 UI.helpOpener=document.activeElement;UI.help.hidden=false;UI.help.querySelector('.kb-close').focus();
}
function closeHelp(){if(!UI.help||UI.help.hidden)return false;UI.help.hidden=true;if(UI.helpOpener&&document.body.contains(UI.helpOpener))UI.helpOpener.focus();return true}
// ---------- actions ----------
function go(delta){var n=R.page+delta;if(n<0||n>=R.total)return;location.hash=R.base+'/'+n}
function openFind(){var d=document.getElementById('reader-find-panel'),i=document.getElementById('reader-term');if(d)d.open=true;if(i){i.focus();i.scrollIntoView({block:'center'})}}
function act(a,opener){
 if(!inReader())return;
 if(a==='prev')go(-1);else if(a==='next')go(1);
 else if(a==='find')openFind();
 else if(a==='toc'){if(document.body.classList.contains('toc-open'))closeToc(true);else openToc()}
 else if(a==='notes'){if(UI.panel&&!UI.panel.hidden)hidePanel(true);else openPanel(opener)}
 else if(a==='help')openHelp();
 else if(a==='print-section')printNow(false);
 else if(a==='print-work')printNow(true);
 else if(a==='close')closeAll();
}
function closeAll(){if(closeHelp())return true;if(document.body.classList.contains('toc-open')){closeToc(true);return true}if(UI.panel&&!UI.panel.hidden){hidePanel(true);return true}if(UI.tool&&!UI.tool.hidden){hideTool();return true}var d=document.getElementById('reader-find-panel');if(d&&d.open&&d.contains(document.activeElement)){d.open=false;d.querySelector('summary').focus();return true}return false}
document.addEventListener('keydown',function(ev){
 if(!inReader())return;
 if(UI.help&&!UI.help.hidden){if(ev.key==='Escape'||ev.key==='?'){ev.preventDefault();closeHelp()}return}
 var a=shortcutAction(ev);if(!a)return;
 if(a==='close'){if(closeAll())ev.preventDefault();return}
 ev.preventDefault();ev.stopImmediatePropagation();act(a,document.activeElement);
});
// ---------- print ----------
var PG_NOTICE='This eBook is for the use of anyone anywhere in the United States and most other parts of the world at no cost and with almost no restrictions whatsoever. You may copy it, give it away or re-use it under the terms of the Project Gutenberg License included with this eBook or online at www.gutenberg.org. If you are not located in the United States, you will have to check the laws of the country where you are located before using this eBook.';
function printNow(all){
 var old=document.getElementById('print-all');if(old)old.remove();
 if(all){
  var pg=/gutenberg\.org/.test(R.e.source),d=document.createElement('div');d.id='print-all';
  var notice=pg?'<p class="pa-notice">'+esc(PG_NOTICE)+' Project Gutenberg License: https://www.gutenberg.org/policy/license.html</p>':'';
  d.innerHTML='<h1>'+esc(R.w.title)+'</h1><p class="pa-ed">'+esc(R.w.author)+'. Reading: '+esc(editionLine(R.w,R.e))+'. Printed from bibliothecacatholica.com/'+esc(R.base)+'</p>'+notice+R.blocks.map(function(p){return '<p>'+esc(p)+'</p>'}).join('')+notice;
  document.body.appendChild(d);document.body.classList.add('print-all');
 }
 var done=function(){document.body.classList.remove('print-all');var x=document.getElementById('print-all');if(x)x.remove();removeEventListener('afterprint',done)};
 if(all)addEventListener('afterprint',done);
 setTimeout(function(){window.print();if(all&&!('onafterprint' in window))setTimeout(done,1000)},50);
}
// ---------- mobile bottom bar ----------
function ensureBar(){
 var b=UI.bar;
 if(!b){b=document.createElement('nav');b.className='reader-bar';b.setAttribute('aria-label','Reader controls');
  b.innerHTML='<button type="button" data-act="prev" aria-label="Previous section">‹<span class="rbar-l">Prev</span></button><button type="button" data-act="toc" aria-controls="reader-side" aria-label="Contents">☰<span class="rbar-l">Contents</span></button><button type="button" data-act="notes" aria-controls="bc-notes" aria-label="My notes">✎<span class="rbar-l">Notes <span class="rbar-count"></span></span></button><button type="button" data-act="find" aria-label="Find in this work">⌕<span class="rbar-l">Find</span></button><button type="button" data-act="next" aria-label="Next section">›<span class="rbar-l">Next</span></button>';
  b.addEventListener('click',function(ev){var x=ev.target.closest('[data-act]');if(x)act(x.getAttribute('data-act'),x)});
  document.body.appendChild(b);UI.bar=b}
 b.querySelector('[data-act="prev"]').disabled=R.page===0;b.querySelector('[data-act="next"]').disabled=R.page>=R.total-1;b.querySelector('.rbar-count').textContent=R.items.length;
 document.body.classList.add('in-reader');document.body.classList.remove('rbar-hidden');UI.lastY=scrollY;
}
addEventListener('scroll',function(){
 if(!document.body.classList.contains('in-reader'))return;var y=scrollY,dy=y-UI.lastY;if(Math.abs(dy)<8)return;
 var hide=dy>0&&y>140&&!document.body.classList.contains('toc-open')&&!document.body.classList.contains('notes-open');
 document.body.classList.toggle('rbar-hidden',hide);UI.lastY=y;
},{passive:true});
function measure(){var t=document.querySelector('.topbar');if(t)document.documentElement.style.setProperty('--tb-h',t.offsetHeight+'px')}
addEventListener('resize',function(){measure();if(wide()&&document.body.classList.contains('toc-open'))closeToc(false)});
addEventListener('hashchange',function(){
 hideTool();if(document.body.classList.contains('toc-open'))closeToc(false);closeHelp();
 if(location.hash.indexOf('#/read/')!==0){document.body.classList.remove('in-reader','rbar-hidden','notes-open');if(UI.panel){UI.panel.hidden=true;UI.panelOpen=false}R=null}
});
W.BCReader.enhance=enhance;W.BCReader.continueRow=continueRow;W.BCReader.openPanel=openPanel;
})();
