/* Saints & Hagiography (phase 1). Data: data/saints.js (window.SAINTS_DATA), built by tools/build_saints.py
   from data/saints.json and lazy-loaded on first use. Pure helpers live in BCSaints.core (tested in
   tests/saints.test.js). Rights: CatholicSaints.Info is link-only and appears only where the data has a
   mapped tier-1 link, after New Advent and Vatican News. Vatican News day lists are labelled as such,
   never as the General Roman Calendar. See AGENTS.md and docs/SAINTS.md. */
(function(root){
  'use strict';
  var VER='20261025-v15';
  var MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December'];
  var HON={saint:1,st:1,sts:1,saints:1,blessed:1,bl:1,bd:1,pope:1,the:1};
  /* Same normalization as tools/build_saints.py key(): NFKD, strip diacritics, lowercase, drop apostrophes,
     collapse other punctuation and spaces, drop leading honorifics. Exact keys only: no fuzzy matching. */
  function key(s){s=String(s==null?'':s).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[’'`]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
    var w=s?s.split(' '):[];while(w.length>1&&HON[w[0]])w.shift();return w.join(' ')}
  function lookup(D,q){var k=key(q);if(!k||!D)return null;if(D.aliases[k])return {id:D.aliases[k],key:k};if(D.collisions[k])return {collision:D.collisions[k].slice(),key:k};return null}
  function fmtDate(md){var m=/^(\d\d)-(\d\d)$/.exec(md||'');return m?(+m[2])+' '+MONTHS[+m[1]-1]:''}
  function mdOf(d){d=d||new Date();return ('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}
  function onDay(D,md){var vn=[],other=[];D.saints.forEach(function(s){var f=s.feasts||{};
      if((f.vatican_news||[]).some(function(v){return v.date===md}))vn.push(s);
      else if(((f.other_wikidata||{}).dates||[]).indexOf(md)>=0)other.push(s)});
    var by=function(a,b){return a.name.localeCompare(b.name)};return {vn:vn.sort(by),other:other.sort(by)}}
  function href(s){return s.tier===1&&s.author_id?'#/author/'+s.author_id:'#/saints/'+s.id}
  function statusLabel(s){var v=(s.status||{}).value;return v==='archangel'?'Archangel':v==='saint'?'Saint':v==='blessed'?'Blessed':v==='venerable'?'Venerable':'Status not recorded'}
  function years(s){var f=function(y){return y<0?(-y)+' BC':String(y)};var b=s.born&&s.born.year,d=s.died&&s.died.year;
    if(b!=null&&d!=null)return (d<1000?'c. ':'')+f(b)+' – '+f(d);if(d!=null)return 'd. '+(d<1000?'c. ':'')+f(d);if(b!=null)return 'b. '+f(b);return ''}
  var FLAGL={'tradition':'Tradition and legend','tradition-with-historical-core':'Historical core, later legend','angel':'Archangel'};
  var core={key:key,lookup:lookup,fmtDate:fmtDate,mdOf:mdOf,onDay:onDay,href:href,statusLabel:statusLabel,years:years,FLAGL:FLAGL};

  /* ---------- browser ---------- */
  var D=null,WAIT=[],LOADING=false;
  function load(cb){if(D){cb&&cb(D);return}if(cb)WAIT.push(cb);if(LOADING)return;LOADING=true;
    function done(){D=root.SAINTS_DATA||null;if(D){D.byId={};D.saints.forEach(function(s){D.byId[s.id]=s})}WAIT.splice(0).forEach(function(f){try{f(D)}catch(e){console.warn(e)}})}
    if(root.SAINTS_DATA){setTimeout(done,0);return}var sc=document.createElement('script');sc.src='data/saints.js?v='+VER;sc.onload=done;sc.onerror=done;document.head.appendChild(sc)}
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function ext(u,l,cls){return '<a class="'+(cls||'chip')+'" href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(l)+' ↗</a>'}
  function lib(){return (root.LIBRARY_DATA||{works:[]}).works}
  function work(id){return lib().find(function(w){return w.id===id})||null}
  function hosted(w){return w&&w.editions.find(function(e){return e.text})}
  function lv(id){return ((root.LIBRIVOX||{}).work||{})[id]||[]}
  function track(name,params){try{if(root.BCAnalytics&&typeof root.BCAnalytics.track==='function')root.BCAnalytics.track(name,params)}catch(e){}}
  function flagBadge(s){var h=s.historicity;return h&&h.flag?'<span class="saint-flag f-'+esc(h.flag)+'">'+esc(FLAGL[h.flag]||h.flag)+'</span>':''}
  function statusChip(s){var v=(s.status||{}).value;return '<span class="saint-status s-'+esc(v||'unknown')+'">'+esc(statusLabel(s))+'</span>'}
  function head(eyebrow,h1,lede){return '<div class="page-head"><div class="eyebrow">'+esc(eyebrow)+'</div><h1>'+esc(h1)+'</h1>'+(lede?'<p class="lede">'+lede+'</p>':'')+'</div>'}
  function crumbs(extra){return '<a class="backlink" href="#/saints">← Saints &amp; Hagiography</a>'+(extra||'')}
  function srow(s){var f=(s.feasts||{}).vatican_news||[];return '<li class="saint-row"><a href="'+href(s)+'"><b>'+esc(s.name)+'</b></a> '+statusChip(s)+flagBadge(s)+
    '<span class="saint-meta">'+esc(years(s))+(f.length?(years(s)?' · ':'')+'Vatican News: '+esc(f.map(function(v){return fmtDate(v.date)}).join(', ')):'')+(s.tier===1?' · Writer in the library':'')+'</span></li>'}
  function searchBox(){return '<form class="hero-search saint-search" role="search" data-saint-search><input name="q" placeholder="Find a saint: “Little Flower”, “Aquinas”, “Laurence”…" aria-label="Find a saint by name"><button class="btn">Find</button></form><div class="saint-search-out" aria-live="polite"></div>'}
  function wireSearch(){var f=document.querySelector('[data-saint-search]');if(!f)return;f.addEventListener('submit',function(e){e.preventDefault();var q=f.q.value.trim(),out=document.querySelector('.saint-search-out');if(!q)return;var r=lookup(D,q);
      if(r&&r.id){location.hash=href(D.byId[r.id]);return}
      if(r&&r.collision){out.innerHTML='<p class="callout">Several saints are called “'+esc(q)+'”. Did you mean: '+r.collision.map(function(i){var s=D.byId[i];return '<a href="'+href(s)+'">'+esc(s.name)+'</a>'}).join(', ')+'?</p>';return}
      location.hash='#/search/'+encodeURIComponent(q)})}
  var VN_NOTE='Vatican News “Saint of the day” lists also include saints of the Roman Martyrology who are not in the General Roman Calendar, so these dates are shown as Vatican News lists them, not as the official calendar.';

  function landing(render){var md=mdOf(),t=onDay(D,md),n={1:0,2:0,3:0};D.saints.forEach(function(s){n[s.tier]++});
    var h=head('Sancti · the saints','Saints & Hagiography','A small, sourced guide to '+D.saints.length+' saints: the writers already in the library, the saints people look up most, and a few famous figures of legend. Every fact links to its source, and the old lives of the saints are on the hagiography shelf.')+searchBox();
    h+='<section class="saint-today"><div class="eyebrow">Hodie · '+esc(fmtDate(md))+'</div>'+(t.vn.length?'<h2>On this day, as listed by Vatican News</h2><ul class="saint-list">'+t.vn.map(srow).join('')+'</ul>':'<h2>No saint in our guide is listed for today by Vatican News</h2>')+
      (t.other.length?'<h3 class="small-h">Also on this day in other calendars (Wikidata)</h3><ul class="saint-list">'+t.other.map(srow).join('')+'</ul>':'')+
      '<p class="small muted">'+esc(VN_NOTE)+' <a href="#/saints/calendar/'+md+'">This day in the calendar →</a></p></section>';
    var tiles=[['#/saints/calendar','◷','Calendar','The year day by day, with the date each saint is listed by Vatican News, and other calendars labelled.',''],
      ['#/saints/az','A','A–Z','Every saint in the guide by name, with other names and spellings.',D.saints.length],
      ['#/saints/writers','✎','Writers who are saints','Saints, blesseds, and venerables whose own books are in the library.',n[1]],
      ['#/saints/books','❦','The hagiography shelf','Butler, Baring-Gould, the Golden Legend, the Roman Martyrology (1897), and more, all public domain.',D.shelf.length],
      ['#/saints/legend','?','Saints of legend','Saints whose stories come mostly from tradition, and what that does and does not mean.',n[3]],
      ['#/saints/about','i','Sources & method','Where every date and status comes from, calendars explained, and our rights rules.','']];
    h+='<div class="grid g-sections saint-tiles">'+tiles.map(function(x){return '<a class="sec-card" href="'+x[0]+'">'+(x[4]!==''?'<span class="count">'+x[4]+'</span>':'')+'<div class="glyph">'+x[1]+'</div><h3>'+esc(x[2])+'</h3><p>'+esc(x[3])+'</p></a>'}).join('')+'</div>';
    render(h,'saints');wireSearch()}
  function az(render,letter){var L={};D.saints.forEach(function(s){var c=key(s.name).charAt(0).toUpperCase();(L[c]=L[c]||[]).push(s)});var ks=Object.keys(L).sort();letter=(letter||'').toUpperCase();
    var list=(letter&&L[letter]?L[letter]:D.saints).slice().sort(function(a,b){return a.name.localeCompare(b.name)});
    var h=crumbs()+head('Sancti · A–Z','Saints A–Z',D.saints.length+' saints, blesseds, venerables, and one archangel. Writers link to their author pages.')+
      '<nav class="az-bar" aria-label="Letters"><a href="#/saints/az"'+(!letter?' aria-current="true"':'')+'>All</a>'+ks.map(function(k){return '<a href="#/saints/az/'+k+'"'+(k===letter?' aria-current="true"':'')+'>'+k+'</a>'}).join('')+'</nav>'+
      '<ul class="saint-list">'+list.map(function(s){var al=s.aliases.filter(function(a){return key(a)!==key(s.name)}).slice(0,4);return srow(s).replace('</li>',al.length?'<span class="saint-aka">Also: '+esc(al.join(' · '))+'</span></li>':'</li>')}).join('')+'</ul>';
    render(h,'saints');document.title='Saints A–Z — Bibliotheca Catholica'}
  function calendar(render){var c={};D.saints.forEach(function(s){(s.feasts.vatican_news||[]).forEach(function(v){c[v.date]=(c[v.date]||0)+1})});var today=mdOf();
    var h=crumbs()+head('Sancti · the calendar','Saints’ calendar','Days on which Vatican News lists a saint from our guide. '+esc(VN_NOTE));
    h+='<div class="cal-grid">'+MONTHS.map(function(m,i){var mm=('0'+(i+1)).slice(-2),n=new Date(2024,i+1,0).getDate(),cells='';for(var d=1;d<=n;d++){var md=mm+'-'+('0'+d).slice(-2);cells+='<a class="cal-d'+(c[md]?' has':'')+(md===today?' today':'')+'" href="#/saints/calendar/'+md+'" aria-label="'+d+' '+m+(c[md]?': '+c[md]+' saint'+(c[md]>1?'s':''):'')+'">'+d+'</a>'}
      return '<section class="cal-m"><h2>'+m+'</h2><div class="cal-days">'+cells+'</div></section>'}).join('')+'</div>';
    render(h,'saints');document.title='Saints’ calendar — Bibliotheca Catholica'}
  function day(render,md){if(!/^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(md)){location.replace('#/saints/calendar');return}var t=onDay(D,md),m=+md.slice(0,2),dd=+md.slice(3);
    var h=crumbs(' · <a class="backlink" href="#/saints/calendar">Calendar</a>')+head('Sancti · '+MONTHS[m-1],fmtDate(md),'');
    h+='<section><h2>Listed by Vatican News</h2>'+(t.vn.length?'<ul class="saint-list">'+t.vn.map(function(s){var v=s.feasts.vatican_news.filter(function(x){return x.date===md})[0];return srow(s).replace('</li>','<span class="saint-src">“'+esc(v.title_on_source)+'” · <a href="'+esc(v.source_url)+'" target="_blank" rel="noopener">Vatican News ↗</a></span></li>')}).join('')+'</ul>':'<p class="muted">No saint in our guide is listed by Vatican News for this day. <a href="https://www.vaticannews.va/en/saints/'+md.replace('-','/')+'.html" target="_blank" rel="noopener">See Vatican News for '+esc(fmtDate(md))+' ↗</a></p>')+'<p class="small muted">'+esc(VN_NOTE)+'</p></section>';
    h+='<section><h2>General Roman Calendar</h2><p class="muted">Not yet checked against the Roman Missal (2002) for this guide, so no rank or official date is shown here.</p></section>';
    if(t.other.length)h+='<section><h2>Other calendars (Wikidata)</h2><p class="small muted">Eastern, local, and older dates recorded in Wikidata. Calendars differ, and these are unverified.</p><ul class="saint-list">'+t.other.map(srow).join('')+'</ul></section>';
    var prev=new Date(2024,m-1,dd-1),next=new Date(2024,m-1,dd+1);h+='<p class="cal-nav"><a href="#/saints/calendar/'+mdOf(prev)+'">← '+esc(fmtDate(mdOf(prev)))+'</a><a href="#/saints/calendar/'+mdOf(next)+'">'+esc(fmtDate(mdOf(next)))+' →</a></p>';
    render(h,'saints');document.title=fmtDate(md)+': saints of the day — Bibliotheca Catholica'}
  function writers(render){var L=D.saints.filter(function(s){return s.tier===1}).sort(function(a,b){return a.name.localeCompare(b.name)});
    render(crumbs()+head('Sancti · scriptores','Writers who are saints',L.length+' writers in the library who are saints, blesseds, or venerables, or who have a cult without formal status. Each links to the author page, which has a Saint panel with sources.')+'<ul class="saint-list">'+L.map(srow).join('')+'</ul>','saints');document.title='Writers who are saints — Bibliotheca Catholica'}
  function legend(render){var L=D.saints.filter(function(s){return s.historicity}).sort(function(a,b){return a.name.localeCompare(b.name)});
    render(crumbs()+head('Sancti · legenda','Saints of legend','Some much-loved saints are known almost entirely from later legend. Being removed from the General Roman Calendar in the 1969 reform (in force from 1970), as Christopher, Barbara, and Valentine were, is not the same as being declared “not a saint”: Christopher and Barbara, for example, remain in the Roman Martyrology. Philomena is the exception here: in 1961 the Holy See removed her from all liturgical calendars.')+
      '<ul class="saint-list">'+L.map(function(s){return srow(s).replace('</li>','<span class="saint-src">'+esc(s.historicity.note)+' <a href="'+esc(s.historicity.source_url)+'" target="_blank" rel="noopener">Source ↗</a></span></li>')}).join('')+'</ul>','saints');document.title='Saints of legend — Bibliotheca Catholica'}
  function bookLink(b){var w=b.work_id&&work(b.work_id),e=hosted(w);return w?(e?'<a class="btn" href="#/read/'+w.id+'/'+e.id+'">Read here</a> <a class="chip" href="#/work/'+w.id+'">About this edition</a>':'<a class="chip" href="#/work/'+w.id+'">In the reading room</a>'):''}
  function shelfItem(b){return '<li class="shelf-item"><div class="shelf-t"><b>'+esc(b.title)+'</b>'+(b.fiction?' <span class="saint-flag f-fiction">Novel</span>':'')+'<span class="saint-meta">'+esc(b.author)+'</span></div>'+
      '<dl class="shelf-dl">'+(b.edition?'<dt>Edition</dt><dd>'+esc(b.edition)+'</dd>':'')+'<dt>Imprint</dt><dd>'+esc(b.imprint)+'</dd><dt>Translator or editor</dt><dd>'+esc(b.translator_editor)+'</dd><dt>Rights</dt><dd>'+esc(b.public_domain)+': '+esc(b.evidence)+' (checked '+esc(b.checked)+')</dd></dl>'+
      '<div class="shelf-a">'+bookLink(b)+ext(b.url,b.source)+'</div></li>'}
  function books(render){var h=crumbs()+head('Sancti · bibliotheca','The hagiography shelf','Public-domain lives of the saints, with the edition, imprint, translator, and rights evidence for each. Books hosted in the reading room open here; the rest link to their scans. Baring-Gould was an Anglican priest, and the Golden Legend is a medieval collection of legends: read both with that in mind.');
    D.shelf_groups.forEach(function(g){var L=D.shelf.filter(function(b){return b.group===g[0]});if(!L.length)return;h+='<section class="shelf-g"><h2>'+esc(g[1])+'</h2><ul class="shelf">'+L.map(shelfItem).join('')+'</ul></section>'});
    render(h,'saints');document.title='The hagiography shelf — Bibliotheca Catholica'}
  function about(render){render(crumbs()+head('Sancti · de fontibus','Sources & method','How this guide is built, and what each date and label means.')+
    '<div class="prose saint-about"><h2>Where the facts come from</h2><ul><li><b>Names, other names, and dates of birth and death</b> come from Wikidata (CC0) and are marked “(Wikidata)”.</li><li><b>Status</b> (saint, blessed, or venerable) comes from the title on the Vatican News “Saint of the day” page where there is one, otherwise from Wikidata. Wikidata’s status data is noisy, so each status links its source, and some are marked for review. They have not yet been checked against the Dicastery for the Causes of Saints.</li><li><b>Catholic Encyclopedia</b> links go to New Advent’s copy of the 1907–1914 encyclopedia.</li><li><b>CatholicSaints.Info</b> is linked, never copied, and only for writers whose profile was checked by hand. Its own terms forbid copying, and its robots.txt bars crawling, so nothing here is taken from it.</li></ul>'+
    '<h2>Three kinds of date</h2><ol><li><b>General Roman Calendar.</b> The Church’s current universal calendar, from the <i>Calendarium Romanum</i> (1969) as revised for the Roman Missal (2002) and later decrees. This guide has not yet checked its dates against the Missal, so no official rank or date is shown.</li><li><b>Vatican News “Saint of the day”.</b> A Holy See news outlet’s daily list. It is good evidence for a saint’s day, but it also lists saints who are only in the Roman Martyrology, so it is labelled separately.</li><li><b>Other calendars (Wikidata).</b> Eastern, local, and older dates. Calendars differ, and these are unverified.</li></ol>'+
    '<p>The <a href="https://archive.org/details/romanmartyrology00cath" target="_blank" rel="noopener">Roman Martyrology (1897 English edition) ↗</a> is a historical witness, not today’s calendar.</p>'+
    '<h2>Legend and history</h2><p>Some saints are known mainly from later legend. We flag them, cite the source of the flag, and explain it. Removal from the General Roman Calendar is not the same as being declared “not a saint”.</p>'+
    '<h2>What comes next</h2><p>Later phases add patronages and emblems in art (each with its own source), a check of feast dates against the Missal, and more saints. Corrections are welcome: <a href="mailto:micahwatson@bibliothecacatholica.com?subject=Saints%20correction">tell us ✉</a>.</p></div>','saints');document.title='Saints: sources and method — Bibliotheca Catholica'}
  var MONTH_VOLS=[['butler-lives-january-march',[1,2,3]],['butler-lives-july',[7]],['baring-gould-lives-january',[1]],['baring-gould-lives-february',[2]],['baring-gould-lives-march',[3]]];
  function livesBlock(s){var out=[];(s.lives_about||[]).forEach(function(bid){var b=D.shelf.find(function(x){return x.id===bid});if(!b)return;var w=b.work_id&&work(b.work_id),e=hosted(w);
      out.push('<li>'+(e?'<a href="#/read/'+w.id+'/'+e.id+'">'+esc(b.title)+'</a> <span class="k read">Read here</span>':'<a href="'+esc(b.url)+'" target="_blank" rel="noopener">'+esc(b.title)+' ↗</a>')+' <span class="muted">'+esc(b.author)+', '+esc(b.imprint_date)+'</span></li>')});
    var months={};((s.feasts||{}).vatican_news||[]).forEach(function(v){months[+v.date.slice(0,2)]=v.date});
    MONTH_VOLS.forEach(function(x){var w=work(x[0]),e=hosted(w);if(!e)return;var md=x[1].map(function(m){return months[m]}).filter(Boolean)[0];if(!md)return;
      out.push('<li><a href="#/read/'+w.id+'/'+e.id+'">'+esc(w.title)+'</a> <span class="muted">look near '+esc(fmtDate(md))+'; these volumes follow the older calendar, so the day may differ</span></li>')});
    return out.length?'<h3>Lives of this saint</h3><ul class="linklist saint-lives">'+out.join('')+'</ul>':''}
  function feastBlock(s){var f=s.feasts||{},vn=f.vatican_news||[],ow=(f.other_wikidata||{}).dates||[];
    return '<dl class="saint-feasts"><dt>Vatican News “Saint of the day”</dt><dd>'+(vn.length?vn.map(function(v){return esc(fmtDate(v.date))+': “'+esc(v.title_on_source)+'” <a href="'+esc(v.source_url)+'" target="_blank" rel="noopener">Vatican News ↗</a>'}).join('<br>'):'<span class="muted">Not found on Vatican News for the candidate dates.</span>')+'</dd>'+
      '<dt>General Roman Calendar</dt><dd class="muted">Not yet checked against the Roman Missal.</dd>'+
      (ow.length?'<dt>Other calendars (Wikidata)</dt><dd>'+esc(ow.map(fmtDate).join(' · '))+' <a href="'+esc(f.other_wikidata.source_url)+'" target="_blank" rel="noopener">Wikidata ↗</a> <span class="small muted">calendars differ; unverified</span></dd>':'')+'</dl>'}
  function statusLine(s){var st=s.status||{},vn=/vaticannews/.test(st.source_url||'');
    return '<p class="saint-statusline">'+statusChip(s)+' <span class="small muted">'+(st.value==='archangel'?'An archangel, not a human saint. ':'')+(vn?'From the title on <a href="'+esc(st.source_url)+'" target="_blank" rel="noopener">Vatican News ↗</a>':'From <a href="'+esc(st.source_url)+'" target="_blank" rel="noopener">Wikidata ↗</a>; not yet checked against the Dicastery for the Causes of Saints')+'.'+(st.review?' Under review: '+esc(st.review):'')+'</span></p>'}
  function histBox(s){var h=s.historicity;if(!h)return '';var gen=h.flag==='angel'?'':' Being removed from the General Roman Calendar is not the same as being declared “not a saint”.';
    return '<aside class="saint-hist" role="note"><b>'+esc(FLAGL[h.flag]||h.flag)+'.</b> '+esc(h.note)+gen+' <a href="'+esc(h.source_url)+'" target="_blank" rel="noopener">Source ↗</a> · <a href="#/saints/legend">About saints of legend</a></aside>'}
  function linkChips(s){var L=[];if(s.catholic_encyclopedia)L.push(ext(s.catholic_encyclopedia.url,'Catholic Encyclopedia (New Advent)'));
    var vn=((s.feasts||{}).vatican_news||[])[0];if(vn)L.push(ext(vn.source_url,'Vatican News'));
    if(s.catholicsaints&&s.catholicsaints.url){L.push(ext(s.catholicsaints.url,'CatholicSaints.Info'));if(s.catholicsaints.wayback_url)L.push(ext(s.catholicsaints.wayback_url,'CatholicSaints.Info (archived copy)'))}
    if(s.wikipedia)L.push(ext(s.wikipedia,'Wikipedia'));L.push(ext(s.wikidata,'Wikidata '+s.qid));return '<div class="au-key saint-links">'+L.join('')+'</div>'}
  function worksBlock(s){var W=(s.reading_room_works||[]).map(work).filter(Boolean);if(!W.length)return '';
    return '<h3>Read and listen</h3><ul class="linklist">'+W.map(function(w){var e=hosted(w),a=lv(w.id);return '<li><a href="'+(e?'#/read/'+w.id+'/'+e.id:'#/work/'+w.id)+'">'+esc(w.title)+'</a> <span class="k read">Read here</span>'+(a.length?' <a class="k listen" href="'+esc(a[0].url)+'" target="_blank" rel="noopener">Listen on LibriVox ↗</a>':'')+'</li>'}).join('')+'</ul>'}
  function profile(render,id){var s=D.byId[id];if(!s){render('<div class="empty"><h2>Saint not found</h2><p><a href="#/saints/az">Browse saints A–Z</a></p></div>','saints');return}
    if(s.tier===1&&s.author_id){location.replace('#/author/'+s.author_id);return}
    var h=crumbs()+'<article class="saint-page"><header class="au-head"><div class="eyebrow">'+esc(statusLabel(s))+(years(s)?' · '+esc(years(s))+' <span class="small">(Wikidata)</span>':'')+'</div><h1>'+esc(s.name)+'</h1>'+flagBadge(s)+statusLine(s)+histBox(s)+linkChips(s)+'</header>'+
      '<section class="panel"><h2>Feast days</h2>'+feastBlock(s)+'<p class="small muted">'+esc(VN_NOTE)+' <a href="#/saints/about">How dates are labelled</a></p></section>'+
      (worksBlock(s)||livesBlock(s)?'<section class="panel">'+worksBlock(s)+livesBlock(s)+'</section>':'')+
      (s.aliases.length?'<p class="small muted saint-aka">Also known as: '+esc(s.aliases.join(' · '))+' (<a href="'+esc(s.aliases_source||s.wikidata)+'" target="_blank" rel="noopener">Wikidata ↗</a>)</p>':'')+'</article>';
    render(h,'saints');document.title=s.name+' — Saints — Bibliotheca Catholica';track('saint_open',{saint_id:s.id,saint_tier:s.tier})}
  /* Saint panel on a writer's author page (tier 1). Returns HTML or ''. */
  function authorPanel(aid){if(!D)return '';var s=D.byId[aid];if(!s||s.tier!==1)return '';
    return '<section class="saint-panel" aria-label="Saint"><div class="eyebrow">Saint · <a href="#/saints">Saints &amp; Hagiography</a></div>'+statusLine(s)+histBox(s)+feastBlock(s)+
      '<div class="au-key saint-links">'+(s.catholic_encyclopedia?ext(s.catholic_encyclopedia.url,'Catholic Encyclopedia (New Advent)'):'')+(((s.feasts||{}).vatican_news||[])[0]?ext(s.feasts.vatican_news[0].source_url,'Vatican News'):'')+(s.catholicsaints&&s.catholicsaints.url?ext(s.catholicsaints.url,'CatholicSaints.Info')+(s.catholicsaints.wayback_url?ext(s.catholicsaints.wayback_url,'CatholicSaints.Info (archived copy)'):''):'')+'</div>'+livesBlock(s)+'</section>'}
  function todayLine(){if(!D)return '';var t=onDay(D,mdOf());if(!t.vn.length)return '';
    return '<p class="hodie-saints"><span class="k">On this feast day</span> '+t.vn.map(function(s){return '<a href="'+href(s)+'">'+esc(s.name)+'</a>'}).join(', ')+' <span class="small muted">(as listed by Vatican News)</span> · <a href="#/saints/calendar/'+mdOf()+'">Saints’ calendar →</a></p>'}
  function searchRows(norm){if(!D)return [];return D.saints.map(function(s){var f=(s.feasts.vatican_news||[]).map(function(v){return fmtDate(v.date)}).join(', ');
    return {type:'Saint',t:s.name,s:statusLabel(s)+(years(s)?' · '+years(s):'')+(f?' · Vatican News: '+f:'')+(s.historicity?' · '+(FLAGL[s.historicity.flag]||''):''),h:href(s),x:norm(s.name+' '+s.aliases.join(' ')+' saint saints'),w:3.2}})}
  function view(render,p){load(function(){if(!D){render('<div class="empty"><h2>The saints guide could not load</h2><p><a href="#/">Return home</a></p></div>','saints');return}
    var a=p[0]||'';if(!a)landing(render);else if(a==='az')az(render,p[1]);else if(a==='calendar'){if(p[1])day(render,p[1]);else calendar(render)}else if(a==='writers')writers(render);else if(a==='legend')legend(render);else if(a==='books')books(render);else if(a==='about')about(render);else profile(render,a)})}
  var api={core:core,load:load,view:view,authorPanel:authorPanel,todayLine:todayLine,searchRows:searchRows,lookup:function(q){return lookup(D,q)},get:function(id){return D&&D.byId[id]},href:href};
  if(typeof module!=='undefined')module.exports=api;else root.BCSaints=api;
})(typeof window!=='undefined'?window:globalThis);
