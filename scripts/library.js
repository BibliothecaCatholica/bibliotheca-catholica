(function(){
'use strict';
var C=window.LIBRARY_DATA,main=document.getElementById('main');
/* GA4 events only through window.BCAnalytics (scripts/analytics.js): guarded and wrapped, never notes, quotes, or other free text */
function track(n,p){try{if(window.BCAnalytics)window.BCAnalytics.track(n,p)}catch(err){}}
function gaOnce(sc,k){try{return window.BCAnalytics?window.BCAnalytics.once(sc,k):false}catch(err){return false}}
function gaReset(sc){try{if(window.BCAnalytics)window.BCAnalytics.reset(sc)}catch(err){}}
function extLink(url,label,wid){return '<a target="_blank" rel="noopener" data-open-text="'+esc(wid)+'" href="'+esc(url)+'">'+esc(label)+' ↗</a>'}
function textUrl(e){return C.textArchive&&C.textArchive.enabled?C.textArchive.baseUrl+encodeURIComponent(e.text.split('/').pop()):e.text}
function fetchReadingText(e){
 var primary=textUrl(e),controller=new AbortController(),timer=setTimeout(function(){controller.abort()},8000);
 return fetch(primary,{signal:controller.signal}).then(function(r){if(!r.ok)throw Error('Text unavailable');return r.text()}).catch(function(err){if(primary===e.text)throw err;return fetch(e.text).then(function(r){if(!r.ok)throw Error('Text unavailable');return r.text()})}).finally(function(){clearTimeout(timer)});
}
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function link(url,label){return '<a target="_blank" rel="noopener" href="'+esc(url)+'">'+esc(label)+' ↗</a>'}
function norm(v){return String(v||'').replace(/\b([a-z])\.\s*([a-z])\./gi,'$1$2').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
function sampleLinks(w){return (w.readingLinks||[]).map(function(item){return '<a class="reading-action" target="_blank" rel="noopener" href="'+esc(item.url)+'">'+esc(item.label)+' ↗</a>'}).join('')}
function libraryLinks(title,author){var query=encodeURIComponent(title+' '+(author||''));return '<div class="reading-actions library-finders"><a href="https://search.worldcat.org/search?q='+query+'" target="_blank" rel="noopener">Find in a library · WorldCat ↗</a><a href="https://openlibrary.org/search?q='+query+'" target="_blank" rel="noopener">Check editions &amp; borrowing · Open Library ↗</a></div>'}
// Design part 2 (Step 7): works as rows (title, author and date, one-line description, text actions); no format chips
// or "New" badges in rows: formats are shown on the work page.
// Edition covers (design C; tools/covers.py): one for every hosted edition.
function coverImg(e,cls,wd){return e&&e.text?'<img class="'+cls+'" src="/assets/covers/'+esc(e.id)+'.webp" width="'+wd+'" height="'+Math.round(wd*1.5)+'" loading="lazy" decoding="async" alt="">':''}
function wrow(w){var local=w.editions.find(function(e){return e.text}),external=w.editions.find(function(e){return e.access==='full-text'});
 return '<li class="wrow'+(local?' has-cover':'')+'">'+coverImg(local,'wrow-cover',48)+'<div class="wrow-main"><a class="wrow-t" href="#/work/'+w.id+'">'+esc(w.title)+'</a><span class="wrow-by">'+esc(w.author)+(w.date?' · '+esc(w.date):'')+'</span><span class="wrow-d">'+esc(firstSentence(w.description))+'</span></div><p class="wrow-acts">'+(local?'<a href="#/read/'+w.id+'/'+local.id+'">Read here</a> · ':external?extLink(external.source,'Read at source',w.id)+' · ':'')+'<a href="#/work/'+w.id+'">'+(local||external?'Details':'Find a copy')+'</a></p></li>'}
function cards(works){return works.length?'<ul class="rows wrows">'+works.map(wrow).join('')+'</ul>':''}
// Unfiltered, each shelf shows six works and a link that opens that subject; any filter shows every match.
function shelves(works,brief){var cats=[];works.forEach(function(w){if(cats.indexOf(w.category)<0)cats.push(w.category)});return cats.map(function(c){var L=works.filter(function(w){return w.category===c}),more=brief&&L.length>6;return '<section class="shelf"><h2>'+esc(c)+' <span class="shelf-n">'+L.length+'</span></h2>'+cards(more?L.slice(0,6):L)+(more?'<p class="see-all"><a href="#/library/'+encodeURIComponent(c)+'">See all '+L.length+' in '+esc(c)+' →</a></p>':'')+'</section>'}).join('')}
var IM=window.ISIDORE_MATCHES||{matches:{}};

var RO=window.READING_OPTIONS||{options:{}};
function formats(w){var list=[];if(w.editions.some(function(e){return e.text}))list.push('Online');if(w.editions.some(function(e){return e.access==='full-text'}))list.push('Source');if((w.readingLinks||[]).length)list.push('Sample');(RO.options[w.id]||[]).forEach(function(o){if(!list.includes(o.format))list.push(o.format)});(IM.matches[w.id]||[]).forEach(function(b){b.f.forEach(function(f){if(!list.includes(f))list.push(f)})});return list}
function formatLinks(w){var local=w.editions.find(function(e){return e.text}),external=w.editions.find(function(e){return e.access==='full-text'}),option=(RO.options[w.id]||[]).find(function(o){return o.format==='EPUB'});return '<span class="reading-actions">'+(local?'<a class="reading-action" href="#/read/'+w.id+'/'+local.id+'">Read here</a>':external?extLink(external.source,'Read at source',w.id):sampleLinks(w))+(option?'<a class="reading-action" href="'+esc(option.url)+'" target="_blank" rel="noopener">'+(option.access==='source-page'?'View EPUB options':'Download EPUB')+' · '+esc(option.provider)+' ↗</a>':'')+'<a href="#/work/'+w.id+'">'+esc(w.title)+' · all reading options →</a></span>'}
function sourceShelf(){return '<section class="source-shelf"><h2>More places to read</h2><ul class="rows">'+[['Project Gutenberg','https://www.gutenberg.org/','EPUB and online classics'],['Standard Ebooks','https://standardebooks.org/','carefully produced ebooks'],['CCEL','https://ccel.org/index/format','Christian texts, EPUB and PDF'],['Internet Archive','https://archive.org/','scans and available downloads']].map(function(x){return '<li><a href="'+x[1]+'" target="_blank" rel="noopener">'+x[0]+' ↗</a> <span class="muted">'+x[2]+'</span></li>'}).join('')+'<li><a href="#/libraries">All digital libraries →</a> <span class="muted">sources, archives, and collections</span></li></ul></section>'}
var LV=window.LIBRIVOX||{work:{},edition:{}};
// Recently added: works carry `added` (YYYY-MM-DD) in data/library.json; cards show "New" for 90 days.
function isNew(w){if(!w.added)return false;var t=Date.parse(w.added+'T00:00:00Z');return !isNaN(t)&&(Date.now()-t)<90*864e5}
function fmtDate(d){var t=new Date(d+'T12:00:00Z');return isNaN(t)?d:t.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'})}
function recentList(){return C.works.map(function(w,i){return {w:w,i:i}}).filter(function(x){return x.w.added}).sort(function(a,b){return a.w.added<b.w.added?1:a.w.added>b.w.added?-1:a.i-b.i}).map(function(x){return x.w}).slice(0,24)}
function recentlyAdded(all){var R=recentList();if(!R.length)return '';var shown=all?R:R.slice(0,6);
 return '<section class="recent-added" aria-labelledby="recent-h"><h2 id="recent-h">Recently added</h2><ul class="rows ra-rows">'+shown.map(function(w){var e=w.editions.find(function(x){return x.text});return '<li><a href="'+(e?'#/read/'+w.id+'/'+e.id:'#/work/'+w.id)+'">'+esc(w.title)+'</a> <span class="muted">'+esc(w.author)+' · added '+esc(fmtDate(w.added))+'</span></li>'}).join('')+'</ul>'+(all?'<p><a href="#/library">← The whole reading room</a></p>':(R.length>6?'<p class="see-all"><a href="#/library/recent">See all '+R.length+' recent additions →</a></p>':''))+'</section>'}
// Listen dock: a LibriVox player fixed to the reader that persists across sections of one work.
// Chapter lists come from data/librivox/<recording id>.json (tools/fetch_librivox.py).
var DOCK={work:null,el:null,data:{}};
function fmtTime(s){s=Math.max(0,Math.round(s||0));var h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;return (h?h+':'+(m<10?'0':''):'')+m+':'+(x<10?'0':'')+x}
function closeDock(){if(DOCK.el){var a=DOCK.el.querySelector('audio');if(a)a.pause();DOCK.el.remove()}DOCK.el=null;DOCK.work=null;document.body.classList.remove('has-listen-dock')}
function listenDock(w){var recs=LV.work[w.id]||[];if(!recs.length){closeDock();return}
 if(DOCK.work===w.id&&DOCK.el&&document.body.contains(DOCK.el))return;closeDock();DOCK.work=w.id;
 var key='bc-listen:'+w.id,st={};try{st=JSON.parse(localStorage.getItem(key)||'{}')||{}}catch(err){}
 var playable=recs.filter(function(r){return r.tracks}),el=document.createElement('aside');el.className='listen-dock'+(st.open?' open':'');el.setAttribute('aria-label','Listen to this work');
 el.innerHTML='<button type="button" class="ld-toggle" aria-expanded="'+(st.open?'true':'false')+'" aria-controls="ld-panel">🎧 <span>Listen</span></button><div class="ld-panel" id="ld-panel"'+(st.open?'':' hidden')+'><div class="ld-top"><b>Listen while you read</b><button type="button" class="ld-close" aria-label="Hide the player">×</button></div>'+(playable.length?'<label>Recording <select class="ld-rec">'+playable.map(function(r){return '<option value="'+esc(r.id)+'">'+esc(r.title)+(r.time?' · '+esc(r.time):'')+'</option>'}).join('')+'</select></label><label>Chapter <select class="ld-sec"><option>Loading…</option></select></label><audio class="ld-audio" controls preload="none"></audio><div class="ld-nav"><button type="button" class="ld-prev">‹ Previous</button><span class="ld-read small" aria-live="polite"></span><button type="button" class="ld-next">Next ›</button></div>':'')+'<p class="small ld-note">Free public-domain audio from <a class="ld-lv" target="_blank" rel="noopener" href="'+esc((playable[0]||recs[0]).url)+'">LibriVox ↗</a>, read by volunteers and streamed from the Internet Archive. A recording may follow a different translation or edition than this text.'+(playable.length?'':' '+recs.map(function(r){return '<a target="_blank" rel="noopener" href="'+esc(r.url)+'">'+esc(r.title)+' ↗</a>'}).join(' · '))+'</p></div>';
 document.body.appendChild(el);document.body.classList.add('has-listen-dock');DOCK.el=el;
 function save(){try{localStorage.setItem(key,JSON.stringify(st))}catch(err){}}
 var panel=el.querySelector('.ld-panel'),tog=el.querySelector('.ld-toggle'),loaded=false;
 function setOpen(o){st.open=o;panel.hidden=!o;el.classList.toggle('open',o);tog.setAttribute('aria-expanded',o?'true':'false');save();if(o){load();if(gaOnce('listen_open',w.id))track('listen_open',{work_id:w.id,listen_source:'dock'})}}
 tog.onclick=function(){setOpen(!st.open)};el.querySelector('.ld-close').onclick=function(){setOpen(false);tog.focus()};
 var rec=el.querySelector('.ld-rec'),sec=el.querySelector('.ld-sec'),au=el.querySelector('.ld-audio'),cur=null;
 function load(){if(loaded||!rec)return;loaded=true;useRec(rec.value,String(st.rec)===rec.value)}
 if(!playable.length)return;
 if(st.rec&&playable.some(function(r){return String(r.id)===String(st.rec)}))rec.value=String(st.rec);
 function pick(i,play,at){if(!cur)return;i=Math.max(0,Math.min(cur.sections.length-1,i));var x=cur.sections[i];sec.value=String(i);st.rec=cur.id;st.sec=i;st.t=at||0;save();au.src=x.mp3;au.preload='metadata';
  el.querySelector('.ld-read').textContent=[x.r?'Read by '+x.r:'',x.s?fmtTime(x.s):''].filter(Boolean).join(' · ');el.querySelector('.ld-prev').disabled=i===0;el.querySelector('.ld-next').disabled=i===cur.sections.length-1;
  if(at)au.addEventListener('loadedmetadata',function f(){au.removeEventListener('loadedmetadata',f);try{au.currentTime=at}catch(err){}});if(play)au.play().catch(function(){})}
 function useRec(id,keep){var done=function(d){cur=d;el.querySelector('.ld-lv').href=d.url;sec.innerHTML=d.sections.map(function(x,i){return '<option value="'+i+'">'+esc((x.n?x.n+'. ':'')+x.t)+'</option>'}).join('');pick(keep&&st.sec!=null?Number(st.sec):0,false,keep?Number(st.t)||0:0)};
  if(DOCK.data[id]){done(DOCK.data[id]);return}fetch('data/librivox/'+encodeURIComponent(id)+'.json').then(function(r){if(!r.ok)throw Error('audio list');return r.json()}).then(function(d){DOCK.data[id]=d;if(DOCK.el===el)done(d)}).catch(function(){sec.innerHTML='<option>Chapter list unavailable</option>'})}
 rec.onchange=function(){useRec(rec.value,false)};sec.onchange=function(){pick(Number(sec.value),true)};
 el.querySelector('.ld-prev').onclick=function(){pick(Number(sec.value)-1,true)};el.querySelector('.ld-next').onclick=function(){pick(Number(sec.value)+1,true)};
 var last=0;au.ontimeupdate=function(){if(Date.now()-last>4000){last=Date.now();st.t=au.currentTime;save()}};
 au.onended=function(){if(cur&&Number(sec.value)<cur.sections.length-1)pick(Number(sec.value)+1,true)};
 /* analytics: the chapter is captured at play time, because onended above advances the chapter select before 'ended' listeners run */
 gaReset('listen');var gaPlaying=null;function lp(){return {work_id:w.id,section_index:Number(sec.value)||0,recording_id:cur?String(cur.id):''}}
 au.addEventListener('play',function(){var x=lp();gaPlaying=x;if(gaOnce('listen',x.recording_id+'/'+x.section_index))track('listen_play',x)});
 au.addEventListener('ended',function(){if(gaPlaying)track('listen_complete',gaPlaying);gaPlaying=null});
 if(st.open)load();
}
if(window.addEventListener)window.addEventListener('hashchange',function(){if(DOCK.work&&location.hash.indexOf('#/read/'+DOCK.work+'/')!==0)closeDock();if(location.hash.indexOf('#/read/')!==0){gaReset('open_text');gaReset('reader_section')}});
function listen(list,compact){if(!list||!list.length)return '';
 return '<p class="listen'+(compact?' compact':'')+'"><span class="listen-lbl">Listen free on LibriVox:</span> '+list.map(function(r){return '<a class="listen-btn" target="_blank" rel="noopener" href="'+esc(r.url)+'" title="'+esc(r.title)+(r.time?' · '+esc(r.time):'')+'">'+esc(list.length>1||compact?r.title:'Listen')+(r.lang&&r.lang!=='English'?' ('+esc(r.lang)+')':'')+' ↗</a>'}).join(' · ')+'</p>'}
var EFB=(window.EDITORIAL_FLAGS||{books:{}}).books;function unflagged(b){return !EFB[String(b.id)]}
// Design part 2 review fix: one text link to the Isidore Index record (several records: one link to the Index search
// for this title). The record page carries the rights badge and gates every file link (rights rule 10).
function otherFormats(w){var L=(IM.matches[w.id]||[]).filter(unflagged);if(!L||!L.length)return '';
 return L.length===1?'<a href="#/isidore/book/'+Number(L[0].id)+'">Isidore Index record</a>':'<a href="#/isidore/q='+encodeURIComponent(w.title)+'">'+L.length+' records in the Isidore Index</a>'}
function readHere(bookId){var hit=null;if(EFB[String(bookId)])return '';Object.keys(IM.matches).some(function(wid){if(IM.matches[wid].some(function(b){return b.id===bookId})){var w=C.works.find(function(x){return x.id===wid});var e=w&&w.editions.find(function(x){return x.text});if(e){hit={w:w,e:e};return true}}return false});
 if(!hit)return '';return '<div class="callout read-here"><span><b>'+esc(hit.w.title)+'</b> is in our reading room, free to read in your browser.</span><a class="btn" href="#/read/'+hit.w.id+'/'+hit.e.id+'">Read online here →</a><a href="#/work/'+hit.w.id+'">Edition details</a><span class="small muted">The reading edition may be a different translation from this file.</span></div>'}
function authorWorks(id){var works=C.works.filter(function(w){return w.authorId===id});return works.length?'<h3>Selected works &amp; reading editions</h3>'+cards(works):''}
var LF={q:'',topic:'',format:'',readable:false};
function library(render,topic){try{topic=decodeURIComponent(topic||'')}catch(err){}
 var topics=Array.from(new Set(C.works.map(function(w){return w.category}))).sort();
 if(topic==='recent'){render('<a class="backlink" href="#/library">← Reading room</a><div class="page-head"><h1>Recently added</h1></div>'+recentlyAdded(true),'library');document.title='Recently added · Bibliotheca Catholica';return}
 render('<div class="page-head"><div class="eyebrow">Discover &amp; read</div><h1>The reading room</h1><p class="lede">Classic Catholic books to read here, with their sources and every other way to read them. <a href="#/reading">Choose a reading path →</a></p></div>'+(window.BCReader?window.BCReader.continueRow():'')+recentlyAdded()+'<h2 class="lib-all-h">The shelves</h2><div class="lib-cat"><form class="lib-facets" role="search" aria-label="Filter the shelves"><label class="lf-l" for="library-query">Find a work</label><input id="library-query" type="search" placeholder="Title, author, or subject">'
  +'<fieldset id="library-topic" class="lf-set"><legend>Subject</legend>'+[''].concat(topics).map(function(t){var n=t?C.works.filter(function(w){return w.category===t}).length:C.works.length;return '<label class="lf-c"><input type="radio" name="library-topic" value="'+esc(t)+'"'+(t?'':' checked')+'> <span>'+(t?esc(t):'All subjects')+'</span> <span class="lf-n">'+n+'</span></label>'}).join('')+'</fieldset>'
  +'<label class="lf-l" for="library-format">Format</label><select id="library-format"><option value="">Any format</option><option value="Online">Read here</option><option value="Source">Full text at source</option><option value="Sample">Excerpts &amp; previews</option><option value="EPUB">EPUB</option><option value="PDF">PDF</option></select>'
  +'<label class="lf-c lf-h"><input id="library-readable" type="checkbox"> <span>Read on this site</span></label></form>'
  +'<div class="lib-res"><p id="library-count" class="lf-count" role="status"></p><div id="library-results"></div></div></div>'+sourceShelf(),'library');
 var q=document.getElementById('library-query'),ts=document.getElementById('library-topic'),r=document.getElementById('library-readable'),f=document.getElementById('library-format');
 // Design refresh (owner's pick, November 17, 2026: faceted catalogue): Subject is a radio set with counts; t mirrors a select's value
 var t={get value(){var c=ts.querySelector('input:checked');return c?c.value:''},set value(v){Array.prototype.forEach.call(ts.querySelectorAll('input'),function(i){i.checked=i.value===(v||'')})},addEventListener:function(n,fn){ts.addEventListener(n,fn)}};
 document.querySelector('.lib-facets').addEventListener('submit',function(e){e.preventDefault()});
 if(topics.includes(topic))LF.topic=topic;q.value=LF.q;t.value=LF.topic;f.value=LF.format;r.checked=LF.readable;
 function draw(){LF={q:q.value,topic:t.value,format:f.value,readable:r.checked};var query=norm(q.value).trim(),works=C.works.filter(function(w){return (!f.value||formats(w).includes(f.value))&&(!t.value||w.category===t.value)&&(!r.checked||w.editions.some(function(e){return e.text}))&&query.split(/\s+/).every(function(token){return norm(w.title+' '+w.author+' '+w.category+' '+w.description).includes(token)})});document.getElementById('library-results').innerHTML=shelves(works,!q.value.trim()&&!t.value&&!f.value&&!r.checked)||'<p>No works match these filters.</p>';document.getElementById('library-count').textContent=works.length+(works.length===1?' work':' works')}
 [q,t,r,f].forEach(function(el){el.addEventListener('input',draw)});draw();
 t.addEventListener('change',function(){track('filter_use',{filter_name:'Subject',filter_value:t.value||'All',filter_scope:'library'})});
 f.addEventListener('change',function(){track('filter_use',{filter_name:'Format',filter_value:f.value||'Any',filter_scope:'library'})});
 r.addEventListener('change',function(){track('filter_use',{filter_name:'Read on this site',filter_value:r.checked?'on':'off',filter_scope:'library'})});
}
/* Deep-link gaps (2026-11-09): chapter and story pages, data/text-pages.js from tools/build_text_pages.py; real paths to the static pages */
function partsList(w){var T=window.TEXT_PAGES&&window.TEXT_PAGES[w.id];if(!T)return '';return '<h2>'+esc(T.n)+'</h2><ol class="text-parts">'+T.i.map(function(x){return '<li><a href="/work/'+w.id+'/'+T.k+'/'+x[0]+'/">'+(T.k==='ch'?esc(x[1])+'. ':'')+esc(x[2])+'</a></li>'}).join('')+'</ol>'}
/* Deep-link gaps (2026-11-09): writers outside the Catholic communion with their own static author page (LIBRARY_DATA.relatedAuthors) */
function relatedAuthor(w){return (C.relatedAuthors||[]).find(function(r){return r.workIds.indexOf(w.id)>=0})}
function raBadge(r){return '<span class="ef-badge tradition-badge" title="'+esc(r.evidence)+'">'+esc(r.badge+' · '+r.tradition)+'</span>'}
function relatedBy(w){var r=relatedAuthor(w);return r?'<a href="/author/'+r.id+'/">'+esc(w.author)+'</a> '+raBadge(r):esc(w.author)}
function relatedNote(w){var r=relatedAuthor(w);if(!r||!r.note||(r.noteWorks||[]).indexOf(w.id)<0)return '';var also=(r.readAlso||[]).map(function(id){var v=C.works.find(function(x){return x.id===id});return v?'<a href="/work/'+v.id+'/">'+esc(v.title)+'</a>'+(/^Anonymous/.test(v.author)?'':' by '+esc(v.author)):''}).filter(Boolean);return '<div class="ef-box"><div class="ef-h">Context note</div><p>'+esc(r.note)+'</p>'+(also.length?'<p>Read also: '+(also.length>2?also.slice(0,-1).join(', ')+', and '+also[also.length-1]:also.join(' and '))+'.</p>':'')+'<p class="small">Listing is not endorsement. See the <a href="/policy/">Fidelity &amp; Editorial Policy</a>.</p></div>'}
function seriesList(w){return (C.series||[]).filter(function(S){return S.items.some(function(i){return i.workId===w.id})}).map(function(S){return '<h2>'+esc(S.title)+'</h2><ol class="series-list">'+S.items.map(function(i){var v=i.workId&&C.works.find(function(x){return x.id===i.workId}),T=v&&window.TEXT_PAGES&&window.TEXT_PAGES[v.id],t=esc(i.title)+' ('+i.year+')';if(v&&v.id===w.id)t='<b>'+t+'</b>, this book';else if(v)t='<a href="/work/'+v.id+'/">'+esc(i.title)+'</a> ('+i.year+')';if(T)t+=': read here, '+T.i.length+' '+esc(T.n.toLowerCase())+' on their own pages';else if(v&&v.editions.some(function(e){return e.text}))t+=': read here';if(i.note)t+='. '+esc(i.note);if(i.contents)t+=' Stories: '+esc(i.contents.slice(0,-1).join(', ')+', and '+i.contents[i.contents.length-1])+'.';if(!v){var q=encodeURIComponent(i.title+' '+w.author);t+=' <a href="https://search.worldcat.org/search?q='+q+'" target="_blank" rel="noopener">WorldCat</a> · <a href="https://openlibrary.org/search?q='+q+'" target="_blank" rel="noopener">Open Library</a>'}return '<li>'+t+'</li>'}).join('')+'</ol>'}).join('')}
/* Affiliate preview (2026-11-09): "Buy in print" (renamed in the 2026-11-12 design pass) (Bookshop.org links for edition-guide picks with a verified ISBN,
   "Browse TAN Books", and the disclosure), the same HTML as the static page (data/print-editions.js from tools/build_print_editions.py).
   It comes after every free reading option; plain links, no analytics attributes. */
function printEditions(w){var P=window.PRINT_EDITIONS,x=P&&P.works&&P.works[w.id];return x?x.html:''}
function editionReadLabel(edition){
 var names=(edition.contributors||[]).filter(function(c){return /translator/i.test(c.role)}).map(function(c){return c.name.split(/, (?=[0-9])/)[0]});
 return names.length ? 'Read translation by '+names.join(' and ') : 'Read here';
}
function firstSentence(t){t=String(t||'');var re=/([.!?])[”"’)]?\s+(?=[A-Z“"(])/g,m;while((m=re.exec(t))){var before=t.slice(0,m.index),word=(/(\S+)$/.exec(before)||['',''])[1];if(m[1]==='.'&&(/^(St|Sts|Bl|Ven|Fr|Dr|Mr|Mrs|Msgr|Card|Abp|Bp|Rev|Vol|vol|ch|cf|ca|c|e\.g|i\.e|Jr|Sr|Ss|No|pp|p)$/.test(word)||/^[A-Z]$/.test(word)||/\.[A-Z]$/.test(word)))continue;return t.slice(0,re.lastIndex).trim()}return t}
// Design pass (owner-approved 2026-11-12, docs/DESIGN.md): one summary line per edition (edition, source, rights);
// the full note, checked date, and rights evidence sit behind "Source and rights details" on the same page.
function editionRow(w,e,primary){
 var who=(e.contributors||[]).map(function(c){return esc(c.role)+': '+esc(c.name)}).join(' · ');
 var acts=[];
 if(e.text){if(!primary)acts.push('<a href="#/read/'+w.id+'/'+e.id+'">'+esc(editionReadLabel(e))+'</a>');acts.push('<a href="#/read/'+w.id+'/'+e.id+'/find">Search this book</a>');acts.push(link(e.source,'Source edition'))}
 else acts.push(extLink(e.source,'Read full text at source',w.id));
 return '<li class="ed-row"><p class="ed-sum"><b>'+esc(e.label)+'</b> · '+esc(e.language||'English')+(who?' · '+who:'')+(window.BCRights?window.BCRights.badge(window.BCRights.edition(e)):'')+'</p><p class="ed-acts">'+acts.join(' · ')+'</p><details class="ed-details"><summary>Source and rights details</summary>'+(e.note?'<p>'+esc(e.note)+'</p>':'')+'<p>'+esc(e.rights)+' · Source checked '+esc(e.checked)+'</p></details></li>';
}
function way(label,body,id){return body?'<li class="way"'+(id?' id="'+id+'"':'')+'><h3>'+label+'</h3><div class="way-body">'+body+'</div></li>':''}
function work(render,id){var w=C.works.find(function(x){return x.id===id});if(!w){render('<h1>Work not found</h1><a href="#/library">Browse the library</a>','library');return}
 var full=w.editions.filter(function(e){return e.access==='full-text'}),refs=w.editions.filter(function(e){return e.access==='reference'});
 var hosted=full.find(function(e){return e.text}),ext=!hosted&&full[0];
 var cta=hosted?'<a class="btn" href="#/read/'+w.id+'/'+hosted.id+'">Read here</a>'+(editionReadLabel(hosted)!=='Read here'?' <span class="small muted">'+esc(editionReadLabel(hosted).replace(/^Read translation by/,'Translated by'))+'</span>':''):ext?'<a class="btn" href="'+esc(ext.source)+'" target="_blank" rel="noopener" data-open-text="'+esc(w.id)+'">Read at source ↗</a>':'';
 if(w.status==='not-yet-available')cta='<p class="small">Not yet available online.</p>';
 var recs=LV.work[w.id]||[];
 var listenRow=recs.length?listen(recs)+(recs.some(function(r){return r.tracks})&&hosted?'<p class="small muted">Or press Listen in the reader to hear the chapters as you read.</p>':''):'';
 var opts=RO.options[w.id]||[];
 var dl=[];if(hosted)dl.push('<a download href="'+esc(hosted.text)+'">Plain text (TXT) ↓</a>');
 // Published EPUB of this edition (tools/build_epub.py --publish, data/epubs.js), ahead of the external EPUB links.
 var ep=hosted&&(window.EPUBS||{})[hosted.id];if(ep)dl.push('<a download href="/'+esc(ep.path)+'">EPUB (this edition) ↓</a>');
 opts.forEach(function(o){dl.push('<a href="'+esc(o.url)+'" target="_blank" rel="noopener">'+(o.access==='source-page'?'EPUB at ':'EPUB · ')+esc(o.provider)+' ↗</a>')});
 var iso=otherFormats(w);
 if(iso)dl.push(iso);
 var dlRow=dl.length?'<p>'+dl.join(' · ')+(opts.length?' · <a href="/guides/epub-on-your-device/">EPUB help</a>':'')+'</p>':'';
 var buy=printEditions(w).replace('<h2>Buy in print</h2>','');
 var q=encodeURIComponent(w.title+' '+(w.author||''));
 var libRow='<p><a href="https://search.worldcat.org/search?q='+q+'" target="_blank" rel="noopener">WorldCat ↗</a> · <a href="https://openlibrary.org/search?q='+q+'" target="_blank" rel="noopener">Open Library ↗</a></p>';
 var excerpt=(w.readingLinks||[]).length?w.readingLinks.map(function(item){return '<p>'+link(item.url,item.label)+(item.note?' <span class="small muted">'+esc(item.note)+'</span>':'')+'</p>'}).join(''):'';
 var others=full.filter(function(e){return e!==hosted&&e!==ext});
 // Part D title page (Orthodoxy pilot): a facts line computed from the hosted text, three choices, and About this edition.
 var PD=hosted&&(window.TEXT_PAGES||{})[w.id]&&window.TEXT_PAGES[w.id].d,titlePage='';
 if(PD){cta='<a class="btn" href="#/read/'+w.id+'/'+hosted.id+'">Read</a>'+(recs.length?'<button type="button" class="choice" data-jump="way-listen">Listen</button>':'')+'<a class="choice" download href="'+esc(hosted.text)+'">Download</a>';
  titlePage='<p class="work-facts">'+[factsWords(PD.words),factsTime(PD.minutes)].filter(Boolean).map(esc).join(' · ')+'</p>'}
 render('<a class="backlink" href="#/library">← Reading room</a><div class="page-head work-head'+(hosted?' has-cover':'')+'">'+coverImg(hosted,'work-cover',220).replace(' loading="lazy"','')+'<div class="eyebrow">'+esc(w.category)+'</div><h1>'+esc(w.title)+'</h1><p class="lede">'+(w.authorId?'<a href="#/author/'+w.authorId+'">'+esc(w.author)+'</a>':relatedBy(w))+(w.date?' <span class="muted">· '+esc(w.date)+'</span>':'')+'</p><p class="work-desc">'+esc(firstSentence(w.description))+'</p>'+relatedNote(w)+titlePage+(cta?'<p class="work-cta'+(PD?' work-choices':'')+'">'+cta+'</p>':'')+'</div>'+(PD?'<section class="about-edition"><h2>About this edition</h2><p>'+esc(PD.about)+'</p></section>':'')
  +(full.length?'':'<p class="callout">The complete book is not available in this site’s reader. Excerpts and previews show only part of a book.</p>')
  +partsList(w)+seriesList(w)
  +(full.length?'<section class="work-editions"><h2>'+(full.length>1?'Editions':'Edition')+'</h2><ul class="rows">'+(hosted?editionRow(w,hosted,true):'')+(ext?editionRow(w,ext,false):'')+others.map(function(e){return editionRow(w,e,false)}).join('')+'</ul></section>':'')
  +'<section class="other-ways"><h2>Other ways to read</h2><ul class="rows ways">'+way('Excerpt',excerpt)+way('Listen',listenRow,'way-listen')+way('Download',dlRow)+way('Buy in print',buy)+way('Find in a library',libRow)+'</ul></section>'
  +(refs.length?'<details class="work-refs"><summary>Bibliography &amp; publication references</summary>'+refs.map(function(e){return '<p>'+link(e.source,e.label)+'</p><p class="small">'+esc(e.note)+' '+esc(e.rights)+'</p>'}).join('')+'</details>':''),'library');document.title=w.title+' · Bibliotheca Catholica';
 var jb=document.querySelector('[data-jump]');if(jb)jb.onclick=function(){var t=document.getElementById(jb.getAttribute('data-jump'));if(t){t.scrollIntoView({block:'start'});var f=t.querySelector('a,button');if(f)f.focus()}};
}
function factsWords(n){return 'about '+(Math.round(n/1000)*1000).toLocaleString('en-US')+' words'}
function factsTime(m){m=Math.round(m/10)*10;var h=Math.floor(m/60),r=m%60;return 'about '+(h?h+(h===1?' hour':' hours'):'')+(h&&r?' ':'')+(r?r+' minutes':'')+' of reading'}
function related(render){render('<div class="page-head"><div class="eyebrow">Explore Christian literature</div><h1>Related Christian Writers</h1><p class="lede">C. S. Lewis · Anglican · apologist and novelist</p><p>Start with an excerpt or a limited edition preview, then find a complete library copy. Each book below has its own reading link. These writings are identified by their tradition alongside the Catholic collection.</p><p><a href="#/reading/related-christian">Follow the reading path →</a></p></div>'+cards(C.works.filter(function(w){return w.tradition==='Anglican'}))+((C.relatedAuthors||[]).length?'<h2>Writers with their own pages</h2><ul>'+C.relatedAuthors.map(function(r){return '<li><a href="/author/'+r.id+'/">'+esc(r.name)+' ('+r.born+'–'+r.died+')</a> '+raBadge(r)+'</li>'}).join('')+'</ul>':''),'library')}
// Standard Ebooks texts (The Incredulity of Father Brown, 2026-11-09): same words as SE_NOTICE in tools/build_static.py
var AUTO_LABEL='Automatic layout: wrapped lines are joined and _underscored_ words shown in italics for easier reading. The text is unchanged; turn on Original line breaks in the Aa menu to see the file as it is.';
var SE_NOTICE='This text comes from the Standard Ebooks edition, which its producers dedicate to the public domain (CC0 1.0); it is not a Project Gutenberg eBook. Bibliotheca Catholica corrected it to the wording of the first printings where they differ; each correction is listed in the edition’s provenance record.';
// Opt-in source-bound presentation. Keep textContent and block indexes exact for saved notes.
function renderReadingBlock(e,p,i,anchor){
 // Structured-text pilot (PR #24): a role class (title, byline, heading, chapter, contents) from data/structured/*.json,
 // shipped in data/text-pages.js (or attached as e.structure by the static builder); only for this exact TXT.
 var S=e.structure||(e.autoLayout&&e.autoLayout.structure)||(function(){var T=typeof window!=='undefined'&&window.TEXT_PAGES||{};for(var k in T)if(T[k].edition===e.id&&T[k].s)return {sha256:T[k].s.sha256,roles:T[k].s.r};return null})();
 var st=S&&S.sha256===e.sha256?S.roles.find(function(x){return x[0]===i}):null;
 // Precedence: scan-verified readerFormatting for the blocks it covers, then automatic display-only layout (e.autoLayout,
 // data/auto-layout/<edition>.json from tools/auto_layout.py, fetched with the text). Every character is kept, in order;
 // automatic emphasis keeps the source's underscores inside the span, hidden on screen. Mirror: tools/reader_formatting.py.
 var f=e.readerFormatting,active=!!f&&f.sha256===e.sha256,v=active?f.verse.find(function(x){return x.block===i}):null,prose=active&&f.proseRanges.some(function(r){return i>=r[0]&&i<=r[1]});
 var vem=active?(f.emphasis||[]).filter(function(x){return x.block===i}).map(function(x){return [x.start,x.end]}):[],verified=!!(v||prose||vem.length);
 var a=e.autoLayout,auto=!!a&&!verified&&a.sha256===e.sha256;if(auto)prose=a.reflow.some(function(r){return i>=r[0]&&i<=r[1]});
 // Italics from the structure file (Story of a Soul: its HTML's <i> spans), as [start,end,marked]; mirror: structure_em().
 var sem=S&&S.sha256===e.sha256&&!verified?(S.em||[]).filter(function(x){return x[0]===i}).map(function(x){return [x[1],x[2],x.length>3]}):[];
 var cls=[st?'reading-'+st[1]:'',v?'reading-verse':prose?'reading-prose':'',st&&st[1]==='chapter'&&/^_?(chapter|book|part|discourse|lecture)\b/i.test(p)?'ch-named':''].filter(Boolean).join(' '),content;
 function ems(spans,marked){var at=0,out='';spans.forEach(function(x){var m=marked==null?x[2]:marked;out+=esc(p.slice(at,x[0]))+(m?'<em class="u"><span class="us">_</span>'+esc(p.slice(x[0]+1,x[1]-1))+'<span class="us">_</span></em>':'<em>'+esc(p.slice(x[0],x[1]))+'</em>');at=x[1]});return out+esc(p.slice(at))}
 if(v){var starts=v.lineStarts.concat([p.length]);content=v.lineStarts.map(function(x,k){return '<span class="verse-line">'+esc(p.slice(x,starts[k+1]))+'</span>'}).join('')}
 else if(st&&st[1]==='chapter'&&/^[IVXLC]+\.? \S/.test(p)){var sp1=p.indexOf(' ');content='<span class="ch-n">'+esc(p.slice(0,sp1))+'</span> <span class="ch-t">'+esc(p.slice(sp1+1))+'</span>'}
 else if(vem.length)content=ems(vem,false);
 else if(auto||sem.length){var sp=(auto?a.em.filter(function(x){return x[0]===i}).map(function(x){return [x[1],x[2],true]}):[]).concat(sem).sort(function(x,y){return x[0]-y[0]||x[1]-y[1]}),at2=0;content=ems(sp.filter(function(x){if(x[0]<at2)return false;at2=x[1];return true}),null)}
 else content=esc(p);
 return '<p'+(anchor?' id="reading-p-'+i+'"':'')+(cls?' class="'+cls+'"':'')+'>'+content+'</p>';
}
window.BCReadingBlock=renderReadingBlock;
// Notice rule 2 (owner, November 14, 2026): the Project Gutenberg License's own sentence (clause 1.E.1), verbatim, once per page:
// at the end of the last section. Same words as PG_LINE in tools/build_static.py.
var PG_LINE='This eBook is for the use of anyone anywhere in the United States and most other parts of the world at no cost and with almost no restrictions whatsoever. You may copy it, give it away or re-use it under the terms of the <a href=\"https://www.gutenberg.org/policy/license.html\" target=\"_blank\" rel=\"noopener\">Project Gutenberg™ License</a> included with this eBook or online at www.gutenberg.org. If you are not located in the United States, you will have to check the laws of the country where you are located before using this eBook.';
function sourceNotice(e,end){var t=/gutenberg\.org/.test(e.source)?PG_LINE:/archive\.org\//.test(e.source)?'This text is Bibliotheca Catholica’s transcription of public-domain scans at the Internet Archive, not a Project Gutenberg eBook.'+(end?'':' Obvious OCR errors were corrected; doubtful passages are marked on the <a href="/summa/supp/">Supplement pages</a>.'):/ccel\.org\//.test(e.source)?'This text is the public-domain Shaw translation from the Nicene and Post-Nicene Fathers (Series I, Volume II), taken from the CCEL Public Domain plain-text edition, not a Project Gutenberg eBook.':/standardebooks\.org\//.test(e.source)?SE_NOTICE:'';return t?'<p class="small pg-notice">'+t+'</p>':''}
// The short colophon at the end of a hosted book (owner direction, November 15, 2026): rights in one line, the source, the
// checked date, and a link to the full record on /credits/. Same words as colophon() in tools/credits_page.py.
var BASIS={'pd-date':'Public domain in the USA by date of publication.','pd-nonrenewal':'Public domain in the USA: first published in the United States, and its copyright was not renewed.'};
function colophon(e){var b=BASIS[e.rightsBasis]||(String(e.rights||'Rights not recorded.').split('. ')[0].replace(/\.$/,'')+'.');
 return '<p class="small colophon">'+esc(b)+' Source: <a href="'+esc(e.source)+'" target="_blank" rel="noopener">'+esc(e.label)+'</a>. Checked '+esc(e.checked)+'. <a href="/credits/#ed-'+esc(e.id)+'">Full record in Sources and credits</a>.</p>'}
function formattingNote(e){var f=e.readerFormatting;return f?'<p class="small text-formatting">'+esc(f.note)+' <a href="'+esc(f.evidence)+'" target="_blank" rel="noopener">Formatting witness ↗</a></p>':''}
function splitText(raw){return raw.replace(/\r/g,'').split(/\n\s*\n/).map(function(p){return p.trim()}).filter(Boolean)}
function read(render,id,editionId,part,anchor){
 var w=C.works.find(function(x){return x.id===id}),e=w&&w.editions.find(function(x){return x.id===editionId});
 if(!e||!e.text){work(render,id);return}
 var requestedHash=location.hash,key='bc-reading:'+e.id;
 render('<div class="page-head"><h1>'+esc(w.title)+'</h1><p role="status">Loading the reading edition…</p></div>','library');
 // Automatic layout (display only) travels in its own small file, bound to the TXT checksum; without it the text shows as before.
 var layout=fetch('/data/auto-layout/'+encodeURIComponent(e.id)+'.json').then(function(r){return r.ok?r.json():null}).catch(function(){return null});
 Promise.all([fetchReadingText(e),layout]).then(function(got){var raw=got[0],lay=got[1];if(lay&&lay.sha256===e.sha256)e=Object.assign({},e,{autoLayout:lay});
  if(location.hash!==requestedHash)return;
  var blocks=splitText(raw),size=35,total=Math.ceil(blocks.length/size),saved=null;
  var startAt=blocks.findIndex(function(p){return /\*\*\* ?START OF (THE |THIS )?PROJECT GUTENBERG/i.test(p)});
  // Step 2b (owner, November 14, 2026): blocks the structure file moves into the collapsed front matter (Orthodoxy: the proofreader's credit).
  var FRONT=(function(){var T=window.TEXT_PAGES||{};for(var k in T){var x=T[k];if(x.edition===e.id&&x.s&&x.s.sha256===e.sha256&&x.s.f)return x.s.f}return []})();
  // Part D (Orthodoxy pilot): a chapter ending after each chapter's last block: an ornament, "End of Chapter N", and the next chapter.
  var ENDS={};(function(){var T=(window.TEXT_PAGES||{})[w.id];if(!T||!T.d||T.edition!==e.id)return;T.i.forEach(function(x,k){var nx=T.i[k+1];
   ENDS[x[4]]='<div class="ch-end"><span class="ch-orn" aria-hidden="true">❦</span><p>End of '+esc(/^([0-9]+|[IVXLC]+)$/.test(x[1])?(T.k==='story'?'Story ':'Chapter ')+x[1]:x[1])+'</p>'+(nx?'<a href="#/read/'+w.id+'/'+e.id+'/'+Math.floor(nx[3]/size)+'/'+nx[3]+'">Next: '+esc(nx[1])+'. '+esc(nx[2])+' →</a>':'')+'</div>'})})();
  try{var sv=localStorage.getItem(key);if(sv!==null)saved=Number(sv)}catch(err){}
  var page=part!=null&&part!=='find'?Number(part):saved!=null?saved:0;page=Number.isInteger(page)?Math.max(0,Math.min(total-1,page)):0;
  var base='#/read/'+w.id+'/'+e.id;
  var headings=[];blocks.forEach(function(p,i){if(p.length<140&&/^(BOOK|CHAPTER|CANTO|PART)\s+([IVXLCDM]+|\d+)([. :\n]|$)/i.test(p))headings.push({title:p.replace(/\s+/g,' '),index:i})});
  var mapped=window.TEXT_PAGES && window.TEXT_PAGES[w.id];
  if(mapped && mapped.edition===e.id) headings=mapped.i.map(function(item){
    return {title:item[1]+'. '+item[2],index:item[3]};
  });
  render('<a class="backlink" href="#/work/'+w.id+'">← '+esc(w.title)+': edition details</a><div class="page-head reader-head"><h1>'+esc(w.title)+'</h1><p class="reader-by">'+esc(w.author)+' · '+esc(e.label)+'</p>'+((LV.work[w.id]||[]).length?'<button type="button" class="rb-btn rb-listen" id="reader-listen" title="Free LibriVox audio keeps playing as you turn sections">Listen</button>':'')+'</div><div class="reader-tools"><label>Text size <select id="reader-size"><option value="19">Small</option><option value="22" selected>Medium</option><option value="26">Large</option><option value="30">Extra large</option></select></label><label>Line spacing <select id="reader-spacing"><option value="1.5">Compact</option><option value="1.8" selected>Comfortable</option><option value="2.1">Wide</option></select></label><label>Reading section <select id="reader-part">'+Array.from({length:total},function(_,i){return '<option value="'+i+'"'+(i===page?' selected':'')+'>'+(i+1)+' of '+total+'</option>'}).join('')+'</select></label><label class="rt-breaks"><input type="checkbox" id="reader-breaks"> Original line breaks</label><p class="small muted rt-note">Your section and display preferences are saved on this device when storage is available.</p></div>'+(headings.length?'<details class="panel source-headings"><summary>Contents: source headings</summary><ul>'+headings.map(function(h){return '<li><a href="'+base+'/'+Math.floor(h.index/size)+'/'+h.index+'">'+esc(h.title)+'</a></li>'}).join('')+'</ul></details>':'')+'<details class="panel passage-search"><summary>Find a passage</summary><form id="reader-find" role="search" aria-label="Search this edition"><label for="reader-term" class="sr-only">Word or phrase in this edition</label><input type="search" id="reader-term" placeholder="Enter a word or phrase…" required minlength="2"><button type="submit">Find passages</button></form><div id="reader-hits" role="status"></div></details>'+'<article id="reading-text" class="reading-text'+(((window.TEXT_PAGES||{})[w.id]||{}).d?' edition-designed'+(window.TEXT_PAGES[w.id].k==='story'?' noun-story':''):'')+'" aria-label="Reading text">'+(function(){var para=function(p,i){return renderReadingBlock(e,p,i,true)},lo=page*size,hi=Math.min(blocks.length,(page+1)*size),fm='',body='';for(var i=lo;i<hi;i++){if(page===0&&startAt>=0&&(i<=startAt||FRONT.indexOf(i)>=0))fm+=para(blocks[i],i);else body+=para(blocks[i],i);if(ENDS[i])body+=ENDS[i]}return (fm?'<details class="pg-front"><summary>Source front matter and Project Gutenberg notice</summary>'+fm+'</details>':'')+body})()+'</article>'+(page===total-1?'<div class="reader-notices">'+sourceNotice(e,true)+colophon(e)+'</div>':'')+'<nav class="reader-pagination" aria-label="Reading sections">'+(page?'<a class="btn ghost" href="'+base+'/'+(page-1)+'">← Previous</a>':'')+'<span>Section '+(page+1)+' / '+total+'</span>'+(page<total-1?'<a class="btn" href="'+base+'/'+(page+1)+'">Next →</a>':'')+'</nav><details class="panel reader-source"><summary>Source, rights, and downloads</summary><p>'+esc(w.author+'. '+w.title+'. '+e.label+'. '+e.source)+'.</p><p>'+esc(e.rights)+'</p>'+formattingNote(e)+(e.autoLayout?'<p class="small">'+esc(e.autoLayout.label||AUTO_LABEL)+'</p>':'')+'<p><a download href="'+esc(e.text)+'">Download TXT</a> · '+link(e.source,'Original edition')+'</p><p>Full source credits and the Project Gutenberg license are preserved in the downloadable text and the source front matter. Section numbers here are navigation aids, not scholarly paragraph numbers.</p></details>','library');
  document.title=w.title+' · Reading · Bibliotheca Catholica';
  listenDock(w);var lb=document.getElementById('reader-listen');if(lb)lb.onclick=function(){if(!DOCK.el)return;var t=DOCK.el.querySelector('.ld-toggle');if(!DOCK.el.classList.contains('open'))t.click();var a=DOCK.el.querySelector('.ld-rec')||t;a.focus()};
  if(anchor!=null){var target=document.getElementById('reading-p-'+Number(anchor));if(target)target.scrollIntoView({block:'start'})}
  try{localStorage.setItem(key,String(page))}catch(err){}
  document.getElementById('reader-part').onchange=function(ev){location.hash=base+'/'+ev.target.value};
  (function(){var box=document.getElementById('reader-breaks'),art=document.getElementById('reading-text');if(!box||!art)return;try{box.checked=localStorage.getItem('bc:reader-breaks')==='1'}catch(err){}function apply(){art.classList.toggle('orig-breaks',box.checked);try{localStorage.setItem('bc:reader-breaks',box.checked?'1':'0')}catch(err){}}box.onchange=apply;apply()})();
  [['reader-size','fontSize','px'],['reader-spacing','lineHeight','']].forEach(function(setting){var input=document.getElementById(setting[0]);try{var pref=localStorage.getItem('bc:'+setting[0]);if(Array.from(input.options).some(function(o){return o.value===pref}))input.value=pref}catch(err){}function apply(){document.getElementById('reading-text').style[setting[1]]=input.value+setting[2];try{localStorage.setItem('bc:'+setting[0],input.value)}catch(err){}}input.onchange=apply;apply()});
  document.getElementById('reader-find').onsubmit=function(event){
    event.preventDefault();
    var term=document.getElementById('reader-term').value.trim();
    var results=document.getElementById('reader-hits');
    if(term.length<2){results.textContent='Enter at least two characters.';return}
    var pattern=new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'iu');
    var cards=[],count=0,headingIndex=-1;
    blocks.forEach(function(block,index){
      while(headingIndex+1<headings.length && headings[headingIndex+1].index<=index)headingIndex++;
      var match=pattern.exec(block);
      if(!match)return;
      count++;
      if(cards.length>=50)return;
      var start=Math.max(0,match.index-65),end=Math.min(block.length,match.index+match[0].length+100);
      var section=Math.floor(index/size);
      var label=headingIndex>=0?headings[headingIndex].title:'Section '+(section+1);
      cards.push('<li><a href="'+base+'/'+section+'/'+index+'"><strong>'+esc(label)+'</strong><span>'+
        (start?'…':'')+esc(block.slice(start,match.index))+'<mark>'+esc(match[0])+'</mark>'+
        esc(block.slice(match.index+match[0].length,end))+(end<block.length?'…':'')+'</span></a></li>');
    });
    results.innerHTML=count?'<p>'+count+' matching paragraph'+(count===1?'':'s')+(count>50?' · first 50 shown':'')+'</p><ol>'+cards.join('')+'</ol>':'<p>No matching passages. Try a shorter phrase or a different spelling.</p>';
  };
  if(gaOnce('open_text',w.id+'/'+e.id)){gaReset('open_text');gaOnce('open_text',w.id+'/'+e.id);gaReset('reader_section');track('open_text',{work_id:w.id,edition_id:e.id,text_source:'hosted'})}
  if(gaOnce('reader_section',w.id+'/'+e.id+'/'+page))track('reader_section',{work_id:w.id,edition_id:e.id,section_index:page,sections_total:total});
  if(window.BCReader)window.BCReader.enhance({w:w,e:e,blocks:blocks,size:size,total:total,page:page,base:base,headings:headings,anchor:anchor});
  if(part==='find'){
    var input=document.getElementById('reader-term');
    input.closest('details').open=true;
    input.focus();
  }
 }).catch(function(){if(location.hash===requestedHash)render('<h1>The reading edition could not load</h1><p>Please try again, or '+link(e.source,'read at the source')+'.</p><a href="#/work/'+w.id+'">Edition details</a>','library')});
}
window.BCLibrary={recentlyAdded:recentlyAdded,isNew:isNew,listenDock:listenDock,closeDock:closeDock,textUrl:textUrl,fetchReadingText:fetchReadingText,listen:listen,listenEdition:function(id){return listen(LV.edition[id])},sampleLinks:sampleLinks,libraryLinks:libraryLinks,formatLinks:formatLinks,readHere:readHere,library:library,work:work,read:read,related:related,authorWorks:authorWorks,entries:C.works.map(function(w){return {type:'Selected work',t:w.title,s:w.author+' · '+w.category+' · '+w.tradition,h:'#/work/'+w.id,x:w.title+' '+w.author+' '+w.category+' '+(w.description||''),w:4}}).concat([{type:'Author',t:'C. S. Lewis',s:'Anglican · related Christian writer',h:'#/related',x:'C. S. Lewis cs lewis clive staples anglican apologetics',w:4}])};
})();
