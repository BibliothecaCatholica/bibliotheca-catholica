/* One chronology for authors and the existing saints guide. No new biographical claims or sources. */
(function(root){
'use strict';
function norm(s){return String(s||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/\b([a-z])\.\s*([a-z])\./gi,'$1$2').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function safeSource(url){return /^https?:\/\//i.test(url||'')&&!/isidore\.co\//i.test(url)}
function centuryOf(y){return Number.isInteger(y)&&y!==0?(y>0?Math.ceil(y/100):-Math.ceil(-y/100)):null}
function year(s,k){var value=s&&s[k]&&s[k].year;return Number.isInteger(value)&&value!==0?value:null}
function status(s){var value=s&&s.status&&s.status.value;return {saint:'Saint',blessed:'Blessed',venerable:'Venerable',archangel:'Archangel'}[value]||'Status not recorded'}
function chronological(s){if(s&&(s.kind!=='person'||s.historicity&&['angel','tradition'].indexOf(s.historicity.flag)>=0))return null;return centuryOf(year(s,'died')||year(s,'born'))}
function uniq(list,key){var seen={};return list.filter(function(x){var k=key(x);if(seen[k])return false;seen[k]=true;return true})}
function build(authors,saints,works,shelf,flags,rights){
 var excluded=new Set((flags||{}).hubAuthors||[]),byAuthor={},rows=[],workMap={};
 works.forEach(function(w){workMap[w.id]=w});
 saints.forEach(function(s){if(s.author_id)byAuthor[s.author_id]=s});
 function canRead(e){return !!(e.text&&rights&&rights.hostable((rights.edition(e)||{}).status))}
 function make(a,s){
  var id=a?a.id:s.id;if(excluded.has(id)||s&&excluded.has(s.id))return;
  var authored=works.filter(function(w){return a&&w.authorId===a.id});
  (s&&s.reading_room_works||[]).forEach(function(id){var w=workMap[id];if(w&&(!a||!w.authorId||w.authorId===a.id))authored.push(w)});
  authored=uniq(authored,function(w){return w.id});
  var titles=authored.map(function(w){return norm(w.title)});
  var external=uniq((a&&a.works||[]).filter(function(w){return safeSource(w.url)&&titles.indexOf(norm(w.title))<0}),function(w){return w.url});
  var about=(s&&s.lives_about||[]).map(function(id){return shelf.find(function(b){return b.id===id})}).filter(Boolean);
  var collections=(a&&a.links||[]).filter(function(l){return l.kind==='read'&&safeSource(l.url)});
  var c=a&&Number.isInteger(a.century)&&a.century>0?a.century:chronological(s);
  var dateSource=a&&c===a.century?'Author’s principal work':s&&(year(s,'died')||year(s,'born'))&&c?'Life dates in the saints guide':'No chronological placement';
  var row={id:id,name:a?a.name:s.name,author:a||null,saint:s||null,century:c,dateBasis:dateSource,
   profile:a?'#/author/'+a.id:'#/saints/'+s.id,doctor:!!(a&&a.doctor),own:authored,external:external,about:about,collections:collections};
  row.canRead=function(w){return (w.editions||[]).find(canRead)||null};
  row.readable=authored.some(function(w){return row.canRead(w)})||about.some(function(b){return workMap[b.work_id]&&row.canRead(workMap[b.work_id])});
  row.search=norm(row.name+' '+(s&&s.aliases||[]).join(' ')+' '+(a&&a.desc||'')+' '+(s?status(s):'')+' '+authored.map(function(w){return w.title}).join(' ')+' '+external.map(function(w){return w.title}).join(' ')+' '+about.map(function(b){return b.title}).join(' '));
  rows.push(row);
 }
 authors.forEach(function(a){make(a,byAuthor[a.id])});
 saints.filter(function(s){return !s.author_id||!authors.some(function(a){return a.id===s.author_id})}).forEach(function(s){make(null,s)});
 return rows;
}
function filter(rows,query,scope,century,readable){var terms=norm(query).split(/\s+/).filter(Boolean);return rows.filter(function(r){return (!scope||scope==='all'||scope==='saints'&&r.saint||scope==='authors'&&r.author||scope==='doctors'&&r.doctor)&&(!century||String(r.century)===century||century==='undated'&&r.century===null)&&(!readable||r.readable)&&terms.every(function(t){return r.search.indexOf(t)>=0})})}
function groups(rows){var map={};rows.forEach(function(r){var key=r.century===null?'undated':String(r.century);(map[key]=map[key]||[]).push(r)});return Object.keys(map).sort(function(a,b){return a==='undated'?1:b==='undated'?-1:Number(a)-Number(b)}).map(function(k){return {key:k,people:map[k].slice().sort(function(a,b){return a.name.localeCompare(b.name)})}})}
function centuryLabel(c){if(c===null||c==='undated')return 'Outside the dated timeline';c=Number(c);return Math.abs(c)+(Math.abs(c)%100>=11&&Math.abs(c)%100<=13?'th':({1:'st',2:'nd',3:'rd'}[Math.abs(c)%10]||'th'))+' century'+(c<0?' BC':'')}
function range(c){return c>0?((c-1)*100+1)+'–'+(c*100):(-c*100)+'–'+((-c-1)*100+1)+' BC'}
function peopleCount(n){return n+' '+(n===1?'person':'people')}
var STATE={query:'',century:'',readable:false,scope:'all'},serial=0;
function flag(s){var h=s&&s.historicity;if(!h)return '';var labels={'tradition':'Tradition and legend','tradition-with-historical-core':'Historical core, later legend','angel':'Archangel'};return '<span class="saint-flag f-'+esc(h.flag)+'">'+esc(labels[h.flag]||h.flag)+'</span>'}
function workItem(w,row){var e=row.canRead(w),full=w.editions.some(function(e){return e.access==='full-text'});
 return '<li><a href="#/work/'+esc(w.id)+'">'+esc(w.title)+'</a> '+(e?'<a class="tl-action" href="#/read/'+esc(w.id)+'/'+esc(e.id)+'">Read here →</a>':'<span class="small muted">'+(full?'Full text at source':'Excerpt / preview')+'</span>')+'</li>'}
function person(row,workMap,focus){var s=row.saint,a=row.author,born=a&&a.born||year(s,'born'),died=a&&a.died||year(s,'died');
 function yr(v){return v<0?-v+' BC':String(v)}
 var dates=born&&died?yr(born)+' – '+yr(died):born?'born '+yr(born):died?'died '+yr(died):'',labels=(s?'<span class="tl-status">'+esc(status(s))+'</span>':'')+(row.doctor?'<span class="tl-status tl-doctor">Doctor of the Church</span>':'');
 var writingCount=row.own.length+row.external.length;
 var h='<details class="tl-person'+(row.doctor?' tl-is-doctor':'')+'" id="tl-person-'+esc(row.id)+'"'+(focus===row.id?' open':'')+'><summary><span class="tl-person-name">'+esc(row.name)+'</span><span class="tl-person-meta">'+labels+flag(s)+(row.readable?'<span class="tl-status">Read here</span>':'')+'<span class="tl-connection">'+(writingCount?writingCount+' writing'+(writingCount===1?'':'s'):row.about.length?row.about.length+' biograph'+(row.about.length===1?'y':'ies'):'Profile &amp; sources')+'</span></span></summary><div class="tl-person-body">';
 h+='<p class="small muted">'+(dates?'Life dates: '+esc(dates)+'. ':'')+'Placement: '+esc(row.dateBasis)+'.'+(s&&row.dateBasis==='Life dates in the saints guide'?' Dates from Wikidata; see the linked profile for sources.':'')+'</p>';
 if(s&&s.historicity)h+='<p class="small">'+esc(s.historicity.note)+' <a href="'+esc(s.historicity.source_url)+'" target="_blank" rel="noopener">Historical context ↗</a></p>';
 if(s&&s.status&&s.status.review)h+='<p class="small">Status under review: '+esc(s.status.review)+'</p>';
 h+='<p class="tl-profile"><a href="'+esc(row.profile)+'">'+(a?'All writings &amp; sources':'Saint profile &amp; sources')+' →</a>'+(s?' · <a href="#/saints">Saints &amp; Hagiography</a>':'')+'</p>';
 if(row.own.length)h+='<h4>Writings by '+esc(row.name)+'</h4><ul class="tl-works">'+row.own.map(function(w){return workItem(w,row)}).join('')+'</ul>';
 if(row.external.length)h+='<h4>'+(row.own.length?'More writings at source':'Writings at source')+'</h4><ul class="tl-works">'+row.external.slice(0,3).map(function(w){return '<li><a href="'+esc(w.url)+'" target="_blank" rel="noopener">'+esc(w.title)+' ↗</a></li>'}).join('')+'</ul>'+(row.external.length>3?'<p class="small"><a href="'+esc(row.profile)+'">'+(row.external.length-3)+' more source links →</a></p>':'');
 if(row.collections.length)h+='<h4>Source collections</h4><ul class="tl-works">'+row.collections.map(function(l){return '<li><a href="'+esc(l.url)+'" target="_blank" rel="noopener">'+esc(l.label)+' ↗</a></li>'}).join('')+'</ul>';
 if(row.about.length)h+='<h4>Lives and biographies about '+esc(row.name)+'</h4><ul class="tl-works">'+row.about.map(function(b){var w=workMap[b.work_id];return w?workItem(w,row):'<li><a href="'+esc(b.url)+'" target="_blank" rel="noopener">'+esc(b.title)+' ↗</a></li>'}).join('')+'</ul>';
 if(!writingCount&&row.about.length)h+='<p class="small muted">These are works about this person, not writings attributed to them.</p>';
 return h+'</div></details>';
}
function view(render,opts){opts=opts||{};var ticket=++serial,requested=root.location.hash;
 var scope=['all','saints','authors','doctors'].indexOf(opts.scope)>=0?opts.scope:'all';STATE.scope=scope;
 render('<div class="page-head"><h1>Timeline of Saints &amp; Writers</h1><p role="status">Connecting people and reading sources…</p></div>','timeline');
 root.BCSaints.load(function(data){if(ticket!==serial||root.location.hash!==requested)return;
  var hub=root.HUB_DATA,works=(root.LIBRARY_DATA||{works:[]}).works,workMap={};works.forEach(function(w){workMap[w.id]=w});
  var rows=build(hub.authors,data?data.saints:[],works,data?data.shelf:[],root.EDITORIAL_FLAGS,root.BCRights);
  if(opts.focus){var found=rows.find(function(r){return r.id===opts.focus});if(found){STATE.query='';STATE.century=found.century===null?'undated':String(found.century);STATE.readable=false}}
  var allGroups=groups(rows),h='<div class="page-head"><div class="eyebrow">Per saecula · connected reading</div><h1>Timeline of Saints &amp; Writers</h1><p class="lede">Follow people through the centuries, then open their writings, biographies, and source collections. Open a name to explore its reading links.</p></div>';
  h+='<div class="tl-overview"><a class="chip" href="#/saints">Saints &amp; Hagiography →</a><a class="chip" href="#/library">Reading room →</a><a class="chip" href="#/reading">Reading paths →</a><a class="chip" href="#/editions">Editions &amp; Translations →</a></div>';
  h+='<div class="toolbar tl-toolbar"><label>Find a person or work<input id="tl-query" type="search" placeholder="Augustine, Little Flower, Confessions…"></label><label>People<select id="tl-scope"><option value="all">All authors &amp; saints</option><option value="saints">Saints guide</option><option value="authors">Authors</option><option value="doctors">Doctors of the Church</option></select></label><label>Century<select id="tl-century"><option value="">All centuries</option>'+allGroups.map(function(g){return '<option value="'+g.key+'">'+esc(centuryLabel(g.key))+'</option>'}).join('')+'</select></label><label class="tl-readable"><input id="tl-readable" type="checkbox"> Readable here</label><button class="btn ghost" id="tl-reset" type="button">Reset</button></div>';
  h+='<details class="tl-method"><summary>How people and dates are connected</summary><p>Authors retain their existing principal-work century. Additional saints use a recorded death year, or birth year if no death year is recorded. Undated figures, archangels, and figures marked as known mainly through legend stay outside the dated sequence. These are historical placements, not feast days or canonization dates.</p><p>The Saints guide filter includes saints, blesseds, venerables, and traditional figures already in the guide; each status is labeled. Writings and biographies are separate. “Readable here” means a linked writing or biography has a checked edition in our reader. This is a selected guide, not a complete list of Catholic saints. <a href="#/saints/about">Sources &amp; method →</a></p></details>';
  if(!data)h+='<p class="callout" role="status">The saints guide could not load. Authors and their reading links are still available; reload to include the saints.</p>';
  render(h+'<p id="tl-count" role="status"></p><div id="tl-results"></div>','timeline');
  var q=document.getElementById('tl-query'),sc=document.getElementById('tl-scope'),ce=document.getElementById('tl-century'),rd=document.getElementById('tl-readable');
  q.value=STATE.query;sc.value=STATE.scope;ce.value=STATE.century;rd.checked=STATE.readable;
  function draw(){STATE.query=q.value;STATE.scope=sc.value;STATE.century=ce.value;STATE.readable=rd.checked;var shown=filter(rows,STATE.query,STATE.scope,STATE.century,STATE.readable);
   document.getElementById('tl-count').textContent=shown.length+' of '+rows.length+' people · '+shown.filter(function(r){return r.saint}).length+' in the saints guide';
   document.getElementById('tl-results').innerHTML=shown.length?'<div class="connected-timeline">'+groups(shown).map(function(g){return '<section class="tl-century"><header><h2>'+esc(centuryLabel(g.key))+'</h2><span class="small muted">'+(g.key==='undated'?'No invented dates':esc(range(Number(g.key))))+' · '+peopleCount(g.people.length)+'</span></header><div class="tl-people">'+g.people.map(function(r){return person(r,workMap,opts.focus)}).join('')+'</div></section>'}).join('')+'</div>':'<div class="empty"><h2>No people match these filters</h2><p>Try another name or title, choose all centuries, or clear “Readable here”.</p></div>';
  }
  [q,sc,ce,rd].forEach(function(el){el.addEventListener('input',draw)});
  document.getElementById('tl-reset').onclick=function(){q.value='';sc.value='all';ce.value='';rd.checked=false;draw();q.focus()};
  draw();if(opts.focus){var target=document.getElementById('tl-person-'+opts.focus);if(target){target.scrollIntoView({block:'center'});target.querySelector('summary').focus()}}
 });
}
var api={core:{norm:norm,build:build,filter:filter,groups:groups,centuryOf:centuryOf,centuryLabel:centuryLabel,chronological:chronological},view:view};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.BCTimeline=api;
})(typeof window!=='undefined'?window:globalThis);
