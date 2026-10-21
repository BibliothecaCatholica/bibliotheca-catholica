(function(){
'use strict';
var D=window.HUB_DATA; var $=function(s,r){return (r||document).querySelector(s)}; var main=$('#main');
if(!D){main.innerHTML='<div class="empty">Data failed to load (data/data.js).</div>';return}
$('#gen').textContent=D.generated;
var ERA={};D.eras.forEach(function(e,i){e.i=i;ERA[e.id]=e});
var A=D.authors.slice().sort(function(a,b){return (ERA[a.era].i-ERA[b.era].i)||((a.born||a.died||0)-(b.born||b.died||0))});
var AID={};A.forEach(function(a){AID[a.id]=a});
var SECTIONS={scripture:{t:'Sacred Scripture',e:'Verbum Dei',d:'Bibles in English, Latin and the original languages; commentaries ancient and modern; daily readings.',g:'✠'},
 magisterium:{t:'Magisterium',e:'Documents of the Church',d:'Catechisms, ecumenical councils, papal encyclicals, canon law and doctrinal documents — straight from the source.',g:'☩'},
 references:{t:'References',e:'Instrumenta',d:'Encyclopedias, dictionaries, the Summa, patristic collections, liturgy, chant, saints and apologetics.',g:'R'},
 media:{t:'Podcasts & Media',e:'Fides ex auditu',d:'The major Catholic podcasts, YouTube channels, radio and TV networks, and news outlets.',g:'♪'},
 libraries:{t:'Libraries & Institutions',e:'Bibliothecae',d:'The great Catholic digital libraries, archives, learning institutes and publishers.',g:'L'}};
var TAGL={father:'Church Father',doctor:'Doctor of the Church',saint:'Saint',pope:'Pope',martyr:'Martyr',bishop:'Bishop',cardinal:'Cardinal',theologian:'Theologian',philosopher:'Philosopher',mystic:'Mystic',apologist:'Apologist',novelist:'Novelist',poet:'Poet',historian:'Historian',spiritual:'Spiritual writer',monastic:'Monastic',scripture:'Scripture scholar',convert:'Convert',founder:'Founder',preacher:'Preacher',liturgist:'Liturgist',scientist:'Scientist',journalist:'Journalist',canonist:'Canonist',catechist:'Catechist'};
var TAGF=['doctor','father','saint','pope','martyr','theologian','philosopher','mystic','spiritual','apologist','scripture','historian','novelist','poet','monastic','convert','founder','liturgist','scientist'];
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function norm(s){return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
function roman(n){var r='',m=[[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']];m.forEach(function(p){while(n>=p[0]){r+=p[1];n-=p[0]}});return r}
function ord(n){var s=['th','st','nd','rd'],v=n%100;return n+(s[(v-20)%10]||s[v]||s[0])}
function dates(a){if(a.born&&a.died){var c=a.died<1000?'c. ':'';return c+a.born+' – '+a.died}if(a.born&&!a.died)return 'b. '+a.born;if(a.died)return 'd. '+a.died;return ''}
function initial(n){var s=n.replace(/^(St\.|Pope|Bishop|Fr\.|Dr\.|Mother|Dom|Bl\.)\s+/,'');return s.charAt(0)}
function avatar(a,cls){return '<span class="'+(cls||'avatar')+'">'+(a.img?'<img loading="lazy" alt="" src="'+esc(a.img)+'" onerror="this.remove()">':'')+(a.img?'':esc(initial(a.name)))+'</span>'}
function host(u){try{return new URL(u).hostname.replace(/^www\./,'')}catch(e){return ''}}
function fav(u){var h=host(u);return h?'<img class="fav" loading="lazy" alt="" src="https://www.google.com/s2/favicons?domain='+encodeURIComponent(h)+'&sz=64" onerror="this.style.visibility=\'hidden\'">':''}
function badges(a,max){var t=a.tags.filter(function(x){return TAGL[x]});t.sort(function(x,y){return TAGF.indexOf(x)-TAGF.indexOf(y)});return '<div class="badges">'+t.slice(0,max||4).map(function(x){return '<span class="badge '+x+'">'+esc(x==='doctor'?'Doctor':TAGL[x])+'</span>'}).join('')+'</div>'}
function acard(a){return '<a class="acard" href="#/author/'+a.id+'">'+avatar(a)+'<div><h3>'+esc(a.name)+'</h3><div class="dates">'+esc(dates(a))+' · '+esc(ERA[a.era].label)+'</div><p>'+esc(a.desc)+'</p>'+badges(a)+'</div></a>'}
function rcard(r){return '<a class="rcard" href="'+esc(r.url)+'" target="_blank" rel="noopener"><div class="rc-top">'+fav(r.url)+'<h3>'+esc(r.name)+'</h3></div><p>'+esc(r.desc)+'</p><div class="host">'+esc(host(r.url))+' ↗</div></a>'}
function setNav(k){document.querySelectorAll('.mainnav a').forEach(function(a){a.classList.toggle('on',a.dataset.nav===k)});$('#mainnav').classList.remove('open')}
function render(html,k){main.innerHTML=html;setNav(k);window.scrollTo(0,0);document.title=(k?($('.page-head h1')||{}).textContent||'':'')+(k?' — ':'')+'Bibliotheca Catholica'}

/* ---------- search index ---------- */
var IDX=[];
A.forEach(function(a){IDX.push({type:'Author',t:a.name,s:dates(a)+' · '+a.desc,h:'#/author/'+a.id,x:norm(a.name+' '+a.tags.join(' ')+' '+a.desc+' '+a.wikiDesc+' '+ERA[a.era].label),w:3});
  a.works.forEach(function(w){IDX.push({type:'Work',t:w.title,s:a.name+' · New Advent',h:w.url,ext:1,x:norm(w.title+' '+a.name),w:2})})});
D.resources.forEach(function(r){IDX.push({type:SECTIONS[r.section].t,t:r.name,s:r.category+' · '+r.desc,h:r.url,ext:1,x:norm(r.name+' '+r.category+' '+r.desc+' '+r.tags.join(' ')+' '+r.section),w:2.5})});
D.isidore.forEach(function(i){IDX.push({type:'isidore.co folder',t:i.n,s:'Author folder in the St. Isidore e-book library',h:i.u,ext:1,x:norm(i.n),w:1})});
function search(q,lim){var toks=norm(q).split(/\s+/).filter(Boolean);if(!toks.length)return [];var out=[];
  for(var i=0;i<IDX.length;i++){var e=IDX[i],ok=true,sc=e.w,tn=norm(e.t);for(var j=0;j<toks.length;j++){var t=toks[j];if(e.x.indexOf(t)<0){ok=false;break}if(tn.indexOf(t)===0)sc+=4;else if(tn.indexOf(' '+t)>=0||tn.indexOf(t)>=0)sc+=2.5}
   if(ok){if(tn===norm(q))sc+=10;out.push([sc,e])}}
  out.sort(function(a,b){return b[0]-a[0]});return out.slice(0,lim||400).map(function(x){return x[1]})}
function hl(s,q){var t=norm(q).split(/\s+/).filter(function(x){return x.length>1});if(!t.length)return esc(s);var src=esc(s),n=norm(src);var marks=[];t.forEach(function(k){var i=n.indexOf(k);while(i>=0){marks.push([i,i+k.length]);i=n.indexOf(k,i+k.length)}});if(!marks.length)return src;marks.sort(function(a,b){return a[0]-b[0]});var r='',p=0;marks.forEach(function(m){if(m[0]<p)return;r+=src.slice(p,m[0])+'<mark>'+src.slice(m[0],m[1])+'</mark>';p=m[1]});return r+src.slice(p)}

/* ---------- isidore.co book catalog (lazy) ---------- */
var B=null,BWAIT=[],BLOADING=false;
function loadBooks(cb){if(B){cb&&cb();return}if(cb)BWAIT.push(cb);if(BLOADING)return;BLOADING=true;
  function done(){var R=window.BOOKS_DATA;if(!R){var el=document.getElementById('books-json');if(el){try{R=JSON.parse(el.textContent)}catch(e){}}}
    if(!R){BLOADING=false;BWAIT.splice(0).forEach(function(f){try{f(true)}catch(e){}});return}
    B=prepBooks(R);addBooksToIdx();BWAIT.splice(0).forEach(function(f){f()})}
  if(window.BOOKS_DATA||document.getElementById('books-json')){setTimeout(done,0);return}
  var s=document.createElement('script');s.src='data/books.js';s.onload=done;s.onerror=function(){done()};document.head.appendChild(s)}
function predSub(t,id){t=String(t).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[\\\/:*?"<>|]/g,'_');return t.slice(0,95).trim()+' ('+id+')'}
function encPath(s){return encodeURIComponent(s).replace(/[!'()*]/g,function(c){return '%'+c.charCodeAt(0).toString(16).toUpperCase()})}
var LANGN={eng:'English',lat:'Latin',fra:'French',ita:'Italian',spa:'Spanish',deu:'German',por:'Portuguese',grc:'Ancient Greek',ell:'Greek',nld:'Dutch',pol:'Polish',heb:'Hebrew',rus:'Russian',hun:'Hungarian',cat:'Catalan',ara:'Arabic',syr:'Syriac',cop:'Coptic',lit:'Lithuanian',ces:'Czech',slk:'Slovak',hrv:'Croatian',slv:'Slovenian',gle:'Irish',ina:'Interlingua',epo:'Esperanto',swe:'Swedish',dan:'Danish',nor:'Norwegian',fin:'Finnish',jpn:'Japanese',zho:'Chinese',kor:'Korean',ukr:'Ukrainian',arm:'Armenian',hye:'Armenian',chu:'Church Slavonic',und:'Undetermined'};
function prepBooks(R){var L=R.books.map(function(r){var o={id:r[0],t:r[1],a:r[2].map(function(i){return R.authors[i]}),y:r[3]||0,tg:r[4].map(function(i){return R.tags[i]}),se:r[5]>=0?R.series[r[5]]:'',si:r[6],f:r[7]?r[7].split('|'):[],fo:R.folders[r[8]],sub:r[9]||predSub(r[1],r[0]),lg:r[10]?r[10].split(','):[],pub:r[11]>=0?R.publishers[r[11]]:''};
   o.an=o.a.map(function(x){return x[0]}).join(' & ');o.x=norm(o.t+' '+o.an+' '+o.se+' '+o.tg.join(' ')+' '+o.pub+' '+o.y);o.tn=norm(o.t);o.ts=o.tn.replace(/^[^a-z0-9]+/,'').replace(/^(the|a|an) /,'');return o});
  var BY={};L.forEach(function(b){b.a.forEach(function(x){if(x[1]&&AID[x[1]]){(BY[x[1]]=BY[x[1]]||[]).push(b)}})});
  var langs={},fmts={};L.forEach(function(b){b.lg.forEach(function(l){langs[l]=(langs[l]||0)+1});b.f.forEach(function(f){fmts[f]=(fmts[f]||0)+1})});
  return {list:L,by:BY,langs:langs,fmts:fmts,server:R.server,base:R.base,count:R.count}}
function bookUrl(b){return B.server+'legacy/book/'+b.id+'/CalibreLibrary'}
function bookAppUrl(b){return B.server+'#book_id='+b.id+'&library_id=CalibreLibrary&panel=book_details'}
function bookFiles(b){return B.base+encPath(b.fo)+'/'+encPath(b.sub)+'/'}
function addBooksToIdx(){B.list.forEach(function(b){IDX.push({type:'Book',t:b.t,s:(b.an||'Unknown')+(b.y?' · '+b.y:'')+(b.se?' · '+b.se+(b.si?' #'+b.si:''):'')+' · '+b.f.join(', '),h:bookUrl(b),ext:1,x:b.x,w:1.5})})}
function bookAuthors(b){if(!b.a.length)return '<span class="muted">Unknown</span>';return b.a.map(function(x){return x[1]&&AID[x[1]]?'<a class="b-au linked" href="#/author/'+x[1]+'" title="Author page on this site">'+esc(x[0])+'</a>':'<a class="b-au" href="#/books/'+encodeURIComponent(x[0])+'" data-author="'+esc(x[0])+'">'+esc(x[0])+'</a>'}).join(' <span class="amp">&amp;</span> ')}
function brow(b,q){return '<div class="brow"><div class="b-main"><a class="b-title" href="'+esc(bookUrl(b))+'" target="_blank" rel="noopener">'+(q?hl(b.t,q):esc(b.t))+'</a>'+
  '<div class="b-meta">'+bookAuthors(b)+(b.y?' <span class="dot">·</span> '+b.y:'')+(b.se?' <span class="dot">·</span> <i>'+esc(b.se)+(b.si?' #'+b.si:'')+'</i>':'')+(b.pub?' <span class="dot">·</span> <span class="muted">'+esc(b.pub)+'</span>':'')+'</div>'+
  (b.tg.length?'<div class="b-tags">'+b.tg.slice(0,5).map(function(t){return '<button class="b-tag" data-tag="'+esc(t)+'">'+esc(t)+'</button>'}).join('')+'</div>':'')+'</div>'+
  '<div class="b-side"><div class="b-fmts">'+b.f.slice(0,5).map(function(f){return '<span class="fmt fmt-'+esc(f.toLowerCase())+'">'+esc(f.replace('_',' '))+'</span>'}).join('')+(b.lg.length?'<span class="lang">'+esc(b.lg.map(function(l){return LANGN[l]||l}).join(', '))+'</span>':'')+'</div>'+
  '<div class="b-links"><a href="'+esc(bookUrl(b))+'" target="_blank" rel="noopener">Details ↗</a><a href="'+esc(bookFiles(b))+'" target="_blank" rel="noopener">Files ↗</a><a href="'+esc(bookAppUrl(b))+'" target="_blank" rel="noopener">Calibre ↗</a></div></div></div>'}
var BF={q:'',fmt:'',lang:'',sort:'title',linked:false,tag:'',ontopic:true};
var OFFT=/mathemat|physics|physique|computer|programming|\blie (theory|group|algebra)|^lie|differential|calculus|algebra|mechanics|electro|electric|magnetism|quantum|astronom|astrophys|cosmolog|chemistry|relativity|thermodynam|gravity|plasma|linux|unix|networking|^security$|cryptograph|artificial intelligence|machine learning|data science|data processing|bitcoin|cooking|vegan|nutrition|health & fitness|diet|amateur radio|prepper|e-commerce|software|operating systems|open source|algorithms|combinatoric|geometry|symmetry|perturbation|celestial|satisfiab|^sat$|^c$|^web$|information technology|system administration|discrete math|group theory|mathematical|analysis$|acoustics|electronics|engineering|business|leadership|self-help|personal growth|gardening|^google$|sample book|amazon\.com|intellectual property|creative commons|biology|life sciences|embryology|medical|musical instruments|vocal technique/i;
var RELT=/relig|theolog|cathol|christ|church|saint|\bst\.|bible|biblic|liturg|spiritu|prayer|pope|papa|papal|thom|aquin|dominic|mary|virgin|scholast|apolog|catech|\bmass\b|chant|canon|monast|mystic|sacrament|god|jesus|devot|council|vatican|trent|ecclesi|moral|natural law|virtue|marriage|celibacy|sermon|patrist|fathers|creed|missal|divine office|rosary|grace|faith|jesuit|franciscan|benedictine|carmelit|duhem|jaki/i;
function offTopic(b){if(b._off!=null)return b._off;b._off=b.tg.some(function(t){return OFFT.test(t)})&&!b.tg.some(function(t){return RELT.test(t)})&&!b.a.some(function(x){return x[1]})&&!RELT.test(b.t);return b._off}
function books(arg){
  if(arg!=null&&arg!==''){BF.q=arg;BF.tag=''}
  var h='<div class="page-head"><div class="eyebrow">Catalogus librorum</div><h1>Books in the isidore.co Library</h1><p class="lede">Every title in the <a href="https://isidore.co/calibre" target="_blank" rel="noopener">St. Isidore e-book library</a> — searchable by title, author, series, subject or year. Each book links to its isidore.co page, its folder of downloadable files, and the full Calibre viewer.</p></div>'+
   '<div class="toolbar"><input type="search" id="bk-q" placeholder="Search titles, authors, series, subjects…" value="'+esc(BF.q)+'">'+
   '<select id="bk-sort" aria-label="Sort"><option value="title">English first, A → Z</option><option value="az">Title A → Z (all languages)</option><option value="new">Newest first</option><option value="old">Oldest first</option><option value="author">Author A → Z</option></select>'+
   '<select id="bk-lang" aria-label="Language"><option value="">All languages</option></select>'+
   '<div class="filter-row"><label>Format</label><div class="chips" id="bk-fmt"></div></div>'+
   '<div class="filter-row"><label>Show</label><div class="chips"><button class="chip gold'+(BF.ontopic?' on':'')+'" id="bk-ontopic" title="Hide maths, computing, cooking and other off-topic books that share the isidore.co shelves">Catholic &amp; related subjects only</button><button class="chip gold'+(BF.linked?' on':'')+'" id="bk-linked" title="Only books by authors who have a page on this site">Authors with a page here</button><span id="bk-tagchip"></span></div></div></div>'+
   '<div class="result-meta" id="bk-meta">Loading the catalog…</div><div class="blist" id="bk-out"></div><div class="bk-more-wrap"><button class="btn ghost" id="bk-more" hidden>Show more</button></div>';
  render(h,'books');
  loadBooks(function(err){if(err){$('#bk-meta').textContent='The book catalog could not be loaded.';return}if(!$('#bk-out'))return;
    var fl=Object.keys(B.fmts).sort(function(a,b){return B.fmts[b]-B.fmts[a]}).slice(0,9);
    $('#bk-fmt').innerHTML='<button class="chip'+(BF.fmt?'':' on')+'" data-f="">Any</button>'+fl.map(function(f){return '<button class="chip'+(BF.fmt===f?' on':'')+'" data-f="'+esc(f)+'">'+esc(f.replace('_',' '))+' <span class="small">'+B.fmts[f]+'</span></button>'}).join('');
    var ll=Object.keys(B.langs).sort(function(a,b){return B.langs[b]-B.langs[a]});
    $('#bk-lang').innerHTML='<option value="">All languages</option>'+ll.map(function(l){return '<option value="'+esc(l)+'">'+esc(LANGN[l]||l)+' ('+B.langs[l]+')</option>'}).join('');
    $('#bk-lang').value=BF.lang;$('#bk-sort').value=BF.sort;
    var shown=60,cur=[];
    function filt(){var toks=norm(BF.q).split(/\s+/).filter(Boolean);var L=B.list.filter(function(b){
        if(BF.fmt&&b.f.indexOf(BF.fmt)<0)return false;if(BF.lang&&b.lg.indexOf(BF.lang)<0)return false;if(BF.tag&&b.tg.indexOf(BF.tag)<0)return false;
        if(BF.linked&&!b.a.some(function(x){return x[1]}))return false;if(BF.ontopic&&offTopic(b))return false;
        for(var j=0;j<toks.length;j++)if(b.x.indexOf(toks[j])<0)return false;return true});
      if(BF.sort==='new')L=L.slice().sort(function(a,b){return (b.y||0)-(a.y||0)});
      else if(BF.sort==='old')L=L.slice().sort(function(a,b){return (a.y||9999)-(b.y||9999)});
      else if(BF.sort==='author')L=L.slice().sort(function(a,b){return norm(a.an||'~').localeCompare(norm(b.an||'~'))});
      else if(BF.sort==='az')L=L.slice().sort(function(a,b){return a.ts.localeCompare(b.ts)});
      else if(!toks.length)L=L.slice().sort(function(a,b){var ea=a.lg.indexOf('eng')>=0?0:1,eb=b.lg.indexOf('eng')>=0?0:1;return (ea-eb)||a.ts.localeCompare(b.ts)});
      else if(toks.length){var nq=norm(BF.q);L=L.map(function(b){var s=0;if(b.tn===nq)s+=20;else if(b.tn.indexOf(nq)===0)s+=10;else if(b.tn.indexOf(nq)>=0)s+=6;toks.forEach(function(t){if(b.tn.indexOf(t)>=0)s+=2});return [s,b]}).sort(function(a,b){return b[0]-a[0]}).map(function(x){return x[1]})}
      return L}
    function draw(reset){if(reset){shown=60;cur=filt()}
      $('#bk-meta').innerHTML=cur.length.toLocaleString()+' of '+B.list.length.toLocaleString()+' books'+(BF.ontopic?' <span class="muted">(off-topic subjects hidden)</span>':'')+(BF.q?' matching “'+esc(BF.q)+'”':'')+(BF.q?' · <a href="https://isidore.co/calibre/mobile?search='+encodeURIComponent(BF.q)+'&num=25" target="_blank" rel="noopener">same search on isidore.co ↗</a>':'');
      $('#bk-out').innerHTML=cur.length?cur.slice(0,shown).map(function(b){return brow(b,BF.q)}).join(''):'<div class="empty">No books match. Try clearing a filter.</div>';
      $('#bk-more').hidden=shown>=cur.length;$('#bk-more').textContent='Show more ('+(cur.length-shown).toLocaleString()+' remaining)';
      $('#bk-tagchip').innerHTML=BF.tag?'<button class="chip on" id="bk-untag">Subject: '+esc(BF.tag)+' ✕</button>':''}
    draw(true);
    var tm;$('#bk-q').addEventListener('input',function(e){BF.q=e.target.value;clearTimeout(tm);tm=setTimeout(function(){draw(true)},120)});
    $('#bk-sort').addEventListener('change',function(e){BF.sort=e.target.value;draw(true)});
    $('#bk-lang').addEventListener('change',function(e){BF.lang=e.target.value;draw(true)});
    $('#bk-fmt').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;BF.fmt=b.dataset.f;$('#bk-fmt').querySelectorAll('.chip').forEach(function(x){x.classList.toggle('on',x===b)});draw(true)});
    $('#bk-linked').addEventListener('click',function(e){BF.linked=!BF.linked;e.currentTarget.classList.toggle('on',BF.linked);draw(true)});
    $('#bk-ontopic').addEventListener('click',function(e){BF.ontopic=!BF.ontopic;e.currentTarget.classList.toggle('on',BF.ontopic);draw(true)});
    $('#bk-more').addEventListener('click',function(){shown+=120;draw(false)});
    $('#bk-tagchip').addEventListener('click',function(){BF.tag='';draw(true)});
    $('#bk-out').addEventListener('click',function(e){var t=e.target.closest('.b-tag');if(t){BF.tag=t.dataset.tag;draw(true);window.scrollTo({top:0,behavior:'smooth'});return}
      var a=e.target.closest('.b-au[data-author]');if(a){e.preventDefault();BF.q=a.dataset.author;$('#bk-q').value=BF.q;draw(true);window.scrollTo({top:0,behavior:'smooth'})}});
  });
}
function authorBooks(a){var box=$('#au-books');if(!box)return;loadBooks(function(err){box=$('#au-books');if(!box)return;if(err){box.innerHTML='';return}
  var L=(B.by[a.id]||[]).slice().sort(function(x,y){return x.tn.localeCompare(y.tn)});
  if(!L.length){box.innerHTML='';return}
  box.innerHTML='<div class="rule"></div><h3>Books in the isidore.co library <span class="small">('+L.length+')</span></h3><div class="blist compact">'+L.slice(0,40).map(function(b){return brow(b)}).join('')+'</div>'+(L.length>40?'<p><a href="#/books/'+encodeURIComponent(L[0].a.filter(function(x){return x[1]===a.id})[0][0])+'">See all '+L.length+' books →</a></p>':'');
  box.addEventListener('click',function(e){var t=e.target.closest('.b-tag');if(t){BF.tag=t.dataset.tag;BF.q='';location.hash='#/books'}})})}


/* ---------- guide data: editions, reading lists, substacks (lazy) ---------- */
var GD=null,GWAIT=[],GLOADING=false,ED={};
function loadGuide(cb){if(GD){cb&&cb();return}if(cb)GWAIT.push(cb);if(GLOADING)return;GLOADING=true;
  function done(){var R=window.GUIDE_DATA;if(!R){GLOADING=false;GWAIT.splice(0).forEach(function(f){try{f(true)}catch(e){}});return}
    GD=R;GD.editions.forEach(function(w){ED[w.id]=w});addGuideToIdx();GWAIT.splice(0).forEach(function(f){f()})}
  if(window.GUIDE_DATA){setTimeout(done,0);return}
  var s=document.createElement('script');s.src='data/guide.js';s.onload=done;s.onerror=function(){done()};document.head.appendChild(s)}
function addGuideToIdx(){GD.editions.forEach(function(w){IDX.push({type:'Edition guide',t:w.t,s:(w.a?w.a+' · ':'')+'Which edition should I buy? '+w.picks.map(function(p){return p.tr}).slice(0,2).join(' · '),h:'#/editions/'+w.id,x:norm(w.t+' '+w.a+' '+w.cat+' '+w.picks.map(function(p){return p.tr+' '+p.pub}).join(' ')),w:2.6})});
  GD.lists.forEach(function(l){IDX.push({type:'Reading list',t:l.t,s:l.sub,h:'#/reading/'+l.id,x:norm(l.t+' '+l.sub+' reading list recommendations'),w:2.4})});
  GD.substacks.concat([GD.featured]).forEach(function(s){IDX.push({type:'Substack',t:s.name,s:s.author+' · '+s.desc,h:s.url,ext:1,x:norm(s.name+' '+s.author+' '+s.desc+' '+(s.cat||'')+' substack newsletter'),w:2.2})})}
var AFF=window.AFFILIATES||{bookshopId:'',publishers:{},disclosure:''};
function isbnOk(i){return /^97[89]\d{10}$/.test(i||'')}
function bookshopUrl(isbn,q){var id=(AFF.bookshopId||'').trim();
  if(isbnOk(isbn))return id?'https://bookshop.org/a/'+encodeURIComponent(id)+'/'+isbn:'https://bookshop.org/search?keywords='+isbn;
  return 'https://bookshop.org/search?keywords='+encodeURIComponent(q)}
function pubUrl(pk,q){var p=(AFF.publishers||{})[pk];if(!p||!p.search)return '';var u=p.search.replace('{q}',encodeURIComponent(q));
  if(p.wrap)return p.wrap.replace('{url}',encodeURIComponent(u));if(p.param)u+=(u.indexOf('?')>=0?'&':'?')+p.param;return u}
function buyBtns(isbn,title,author,pk){var q=title+(author?' '+author:'');var h='<div class="buy"><span class="buy-l">Buy</span><a class="buy-b bs" href="'+esc(bookshopUrl(isbn,q))+'" target="_blank" rel="noopener sponsored">Bookshop.org ↗</a>';
  var pu=pk&&pubUrl(pk,title);if(pu)h+='<a class="buy-b" href="'+esc(pu)+'" target="_blank" rel="noopener sponsored">'+esc(AFF.publishers[pk].name)+' ↗</a>';
  return h+'</div>'}
function discl(){return '<p class="disclosure">'+esc(AFF.disclosure||'')+'</p>'}
function freeLinks(f){if(!f||!f.length)return '';return '<div class="free"><span class="free-l">Free text</span>'+f.map(function(x){return '<a href="'+esc(x[1])+'" target="_blank" rel="noopener">'+esc(x[0])+' ↗</a>'}).join('')+'</div>'}
function edCard(w){var au=w.aid&&AID[w.aid]?'<a href="#/author/'+w.aid+'">'+esc(w.a)+'</a>':esc(w.a);
  return '<article class="ed-card" id="ed-'+w.id+'"><div class="ed-head"><div><div class="eyebrow">'+esc(w.cat)+(w.orig?' · '+esc(w.orig):'')+'</div><h3>'+esc(w.t)+'</h3>'+(w.a?'<div class="ed-au">'+au+'</div>':'')+'</div>'+(w.free&&w.free.length?'<span class="pd-badge" title="A public-domain text is free online">Free text online</span>':'')+'</div>'+
   '<p class="ed-why">'+esc(w.why)+'</p><ol class="picks">'+w.picks.map(function(p,i){return '<li class="pick'+(i===0?' top':'')+'"><div class="pick-lbl">'+esc(p.lbl)+'</div><div class="pick-tr">'+esc(p.tr)+'</div><div class="pick-meta">'+esc(p.pub)+(isbnOk(p.isbn)?' · ISBN '+p.isbn:'')+'</div>'+(p.note?'<p>'+esc(p.note)+'</p>':'')+buyBtns(p.isbn,p.bq||(w.multi?p.lbl:w.t),w.a,p.pk)+'</li>'}).join('')+'</ol>'+
   (w.alt?'<p class="ed-alt"><b>Also good:</b> '+esc(w.alt)+'</p>':'')+freeLinks(w.free)+'</article>'}
var EF={q:'',cat:''};
function editions(arg){
  var h='<div class="page-head"><div class="eyebrow">Quae editio?</div><h1>Which Edition Should I Buy?</h1><p class="lede">Recommended translations and editions of the Catholic classics, with why, the publisher, a verified ISBN where we could confirm one, and a link to a free public-domain text wherever one exists.</p></div>'+
   '<div class="callout">ISBNs were checked against Open Library records. Where an ISBN is blank, the buy button runs a search instead. Prices and printings change, so check the edition before you buy.</div>'+
   '<div class="toolbar"><input type="search" id="ed-q" placeholder="Filter by title, author, translator, publisher…" value="'+esc(EF.q)+'"><div class="chips" id="ed-c"></div></div><div class="result-meta" id="ed-m">Loading…</div><div id="ed-out" class="ed-list"></div>'+discl();
  render(h,'editions');
  loadGuide(function(err){if(err||!$('#ed-out')){if($('#ed-m'))$('#ed-m').textContent='The guide could not be loaded.';return}
    var cats=[];GD.editions.forEach(function(w){if(cats.indexOf(w.cat)<0)cats.push(w.cat)});
    $('#ed-c').innerHTML='<button class="chip'+(EF.cat?'':' on')+'" data-c="">All</button>'+cats.map(function(c){return '<button class="chip'+(EF.cat===c?' on':'')+'" data-c="'+esc(c)+'">'+esc(c)+'</button>'}).join('');
    function draw(){var t=norm(EF.q).split(/\s+/).filter(Boolean);var L=GD.editions.filter(function(w){if(EF.cat&&w.cat!==EF.cat)return false;var x=norm(w.t+' '+w.a+' '+w.cat+' '+w.picks.map(function(p){return p.tr+' '+p.pub+' '+p.isbn}).join(' '));return t.every(function(k){return x.indexOf(k)>=0})});
      $('#ed-m').textContent=L.length+' of '+GD.editions.length+' works · '+GD.editions.reduce(function(n,w){return n+w.picks.length},0)+' recommended editions';
      $('#ed-out').innerHTML=L.map(edCard).join('')||'<div class="empty">Nothing matches.</div>'}
    draw();
    $('#ed-q').addEventListener('input',function(e){EF.q=e.target.value;draw()});
    $('#ed-c').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;EF.cat=b.dataset.c;$('#ed-c').querySelectorAll('.chip').forEach(function(x){x.classList.toggle('on',x===b)});draw()});
    if(arg){var el=document.getElementById('ed-'+arg);if(!el&&(EF.q||EF.cat)){EF.q='';EF.cat='';$('#ed-q').value='';draw();el=document.getElementById('ed-'+arg)}
      if(el){el.classList.add('flash');setTimeout(function(){window.scrollTo({top:el.getBoundingClientRect().top+scrollY-130,behavior:'smooth'})},30);var w=ED[arg];if(w)document.title=w.t+' — editions — Bibliotheca Catholica'}}
  })}
function recItem(it){var w=it.e&&ED[it.e];var t=w?w.t:it.t,a=w?w.a:it.a;var p=w?w.picks[0]:null;
  var isbn=p?p.isbn:it.isbn,pk=p?p.pk:it.pk,fr=w?w.free:it.free;
  return '<li class="rec"><div class="rec-main"><h3>'+(w?'<a href="#/editions/'+w.id+'">'+esc(t)+'</a>':esc(t))+'</h3><div class="ed-au">'+(w&&w.aid&&AID[w.aid]?'<a href="#/author/'+w.aid+'">'+esc(a)+'</a>':esc(a))+'</div><p>'+esc(it.b)+'</p>'+
   (p?'<div class="pick-meta">Recommended: '+esc(p.tr)+' · '+esc(p.pub)+' · <a href="#/editions/'+w.id+'">all editions →</a></div>':'')+freeLinks(fr)+'</div>'+buyBtns(isbn,t,a,pk)+'</li>'}
function reading(arg){
  var h='<div class="page-head"><div class="eyebrow">Tolle, lege</div><h1>Reading Lists</h1><p class="lede">Curated shelves for every stage of the journey. Each book links to our edition guide, a free text where one exists, and a place to buy a good copy.</p></div><div class="chips rl-tabs" id="rl-t"></div><div id="rl-out"><div class="loading">Loading…</div></div>'+discl();
  render(h,'reading');
  loadGuide(function(err){if(err||!$('#rl-out'))return;var cur=arg&&GD.lists.some(function(l){return l.id===arg})?arg:'';
    function draw(){$('#rl-t').innerHTML='<button class="chip'+(cur?'':' on')+'" data-l="">All lists</button>'+GD.lists.map(function(l){return '<button class="chip'+(cur===l.id?' on':'')+'" data-l="'+l.id+'">'+esc(l.t)+'</button>'}).join('');
      var L=cur?GD.lists.filter(function(l){return l.id===cur}):GD.lists;
      $('#rl-out').innerHTML=(cur?'':'<div class="grid g-lists">'+GD.lists.map(function(l){return '<a class="sec-card" href="#/reading/'+l.id+'"><span class="count">'+l.items.length+'</span><div class="glyph">'+esc(l.ic)+'</div><h3>'+esc(l.t)+'</h3><p>'+esc(l.sub)+'</p></a>'}).join('')+'</div>')+
        L.map(function(l){return '<section class="rl" id="rl-'+l.id+'"><div class="cat-title"><h2>'+esc(l.t)+' <span class="small">('+l.items.length+')</span></h2></div><p class="lede small">'+esc(l.sub)+'</p>'+(l.id==='chesterton'?featuredMini():'')+'<ol class="recs">'+l.items.map(recItem).join('')+'</ol></section>'}).join('')}
    draw();if(cur)document.title=GD.lists.filter(function(l){return l.id===cur})[0].t+' — Reading Lists — Bibliotheca Catholica';
    $('#rl-t').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;location.hash='#/reading'+(b.dataset.l?'/'+b.dataset.l:'')})})}
function featuredMini(){var F=GD.featured;return '<a class="feat-mini" href="#/substacks"><span class="k read">column</span> Read <b>'+esc(F.author)+'</b>’s Chesterton commentary column, coming soon, and his essays on Substack →</a>'}
function postsList(p){if(!p||!p.length)return '';return '<ul class="posts">'+p.map(function(x){return '<li><a href="'+esc(x.u)+'" target="_blank" rel="noopener">'+esc(x.t)+'</a><span>'+esc(x.d)+'</span></li>'}).join('')+'</ul>'}
function substacks(){
  var h='<div class="page-head"><div class="eyebrow">Scriptores hodierni</div><h1>Top Catholic Substacks</h1><p class="lede">Writers, columnists and newsletters worth subscribing to, from literature and liturgy to news and the spiritual life. Latest posts are a snapshot taken when the site was last built.</p></div><div id="ss-out"><div class="loading">Loading…</div></div>';
  render(h,'substacks');
  loadGuide(function(err){if(err||!$('#ss-out'))return;var F=GD.featured,P=F.pickPost;var cats=[];GD.substacks.forEach(function(s){if(cats.indexOf(s.cat)<0)cats.push(s.cat)});
    var o='<section class="featured"><div class="feat-l"><div class="eyebrow">Featured column · Chesterton commentary coming soon</div><h2><a href="'+esc(F.url)+'" target="_blank" rel="noopener">'+esc(F.author)+'</a></h2><div class="host">'+esc(host(F.url))+' ↗</div><p>'+esc(F.desc)+'</p>'+
      '<div class="hero-cta"><a class="btn" href="'+esc(F.url)+'" target="_blank" rel="noopener">Read on Substack ↗</a><a class="btn ghost" href="'+esc(F.url)+'/subscribe" target="_blank" rel="noopener">Subscribe (free) ↗</a><a class="btn ghost" href="#/reading/chesterton">The Chesterton Shelf</a></div></div>'+
      '<div class="feat-r"><div class="small eyebrow">Featured read</div><a class="feat-post" href="'+esc(P.u)+'" target="_blank" rel="noopener"><b>'+esc(P.t)+'</b><span>'+esc(P.s)+'</span><small>'+esc(P.d)+' ↗</small></a><div class="small eyebrow" style="margin-top:12px">Latest</div>'+postsList(F.posts)+'</div></section>';
    o+='<div class="toolbar"><input type="search" id="ss-q" placeholder="Filter Substacks…"><div class="chips" id="ss-c"><button class="chip on" data-c="">All</button>'+cats.map(function(c){return '<button class="chip" data-c="'+esc(c)+'">'+esc(c)+'</button>'}).join('')+'</div></div><div id="ss-list"></div>'+
      '<p class="small muted">Snapshot of latest posts: '+esc(GD.generated)+'. Substack feeds can’t be read live from a static site (no CORS), so they refresh whenever the site is rebuilt. Know a great Catholic Substack? Tell us.</p>';
    $('#ss-out').innerHTML=o;var cur='',q='';
    function draw(){var out='';cats.forEach(function(c){if(cur&&c!==cur)return;var L=GD.substacks.filter(function(s){return s.cat===c&&(!q||norm(s.name+' '+s.author+' '+s.desc).indexOf(norm(q))>=0)});if(!L.length)return;
      out+='<div class="cat-title"><h2>'+esc(c)+'</h2></div><div class="grid g-subs">'+L.map(function(s){return '<div class="sscard"><a class="ss-top" href="'+esc(s.url)+'" target="_blank" rel="noopener">'+fav(s.url)+'<div><h3>'+esc(s.name)+'</h3><div class="ed-au">'+esc(s.author)+'</div></div></a><p>'+esc(s.desc)+'</p>'+postsList(s.posts.slice(0,2))+'<div class="host">'+esc(host(s.url))+' ↗</div></div>'}).join('')+'</div>'});
      $('#ss-list').innerHTML=out||'<div class="empty">Nothing matches.</div>'}
    draw();$('#ss-q').addEventListener('input',function(e){q=e.target.value;draw()});
    $('#ss-c').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;cur=b.dataset.c;$('#ss-c').querySelectorAll('.chip').forEach(function(x){x.classList.toggle('on',x===b)});draw()})})}
function authorEditions(a){loadGuide(function(err){if(err)return;var box=$('#au-ed');if(!box)return;var L=GD.editions.filter(function(w){return w.aid===a.id});if(!L.length)return;
  box.innerHTML='<div class="panel"><h3>Which edition?</h3><ul class="linklist">'+L.map(function(w){return '<li><a href="#/editions/'+w.id+'"><span class="k read">guide</span>'+esc(w.t)+'</a></li>'}).join('')+'</ul></div>'})}

/* ---------- views ---------- */
function home(){
  var docs=A.filter(function(a){return a.doctor});
  var picks=['thomas-aquinas','augustine-of-hippo','g-k-chesterton','john-henry-newman','fulton-j-sheen','teresa-of-avila','flannery-o-connor','j-r-r-tolkien','joseph-ratzinger','therese-of-lisieux','hilaire-belloc','evelyn-waugh','francis-de-sales','ignatius-of-antioch'].map(function(i){return AID[i]}).filter(Boolean);
  var cnt={};D.resources.forEach(function(r){cnt[r.section]=(cnt[r.section]||0)+1});
  var h='<section class="hero"><div class="eyebrow">Tolle, lege · take up and read</div><h1>Two thousand years of Catholic <span>thought</span>, in one place.</h1>'+
  '<p class="lede">A clean, searchable master index of Catholic authors — from the Apostolic Fathers to today — with the Scriptures, the Magisterium, essential references, podcasts and the great digital libraries. Everything links straight to the source.</p>'+
  '<form class="hero-search" onsubmit="location.hash=\'#/search/\'+encodeURIComponent(this.q.value);return false"><input name="q" placeholder="Try “Confessions”, “Chesterton”, “encyclical”, “Latin dictionary”…" aria-label="Search"><button class="btn">Search</button></form>'+
  '<div class="hero-cta"><a class="btn gold" href="https://www.vatican.va/content/vatican/en.html" target="_blank" rel="noopener">The Holy See · vatican.va ↗</a><a class="btn ghost" href="https://isidore.co/calibre" target="_blank" rel="noopener">St. Isidore e-book library ↗</a><a class="btn ghost" href="#/timeline">Browse the timeline</a></div>'+
  '<div class="stats"><div class="stat"><b>'+A.length+'</b><span>Catholic authors</span></div><div class="stat"><b>'+docs.length+'</b><span>Doctors of the Church</span></div><div class="stat"><b>'+D.resources.length+'</b><span>curated resources</span></div><div class="stat"><b>'+(window.BOOKS_COUNT||6633).toLocaleString()+'</b><span>isidore.co books searchable</span></div><div class="stat"><b>'+D.isidore.length.toLocaleString()+'</b><span>isidore.co author folders indexed</span></div></div></section>';
  h+='<div class="rule"></div><div class="page-head"><div class="eyebrow">Explore</div><h2>The sections of the library</h2></div><div class="grid g-sections">'+
  '<a class="sec-card" href="#/authors"><span class="count">'+A.length+'</span><div class="glyph">A</div><h3>Authors</h3><p>Fathers, Doctors, scholastics, mystics, saints, popes, theologians, apologists, novelists and poets.</p></a>'+
  '<a class="sec-card" href="#/timeline"><span class="count">I–XXI</span><div class="glyph">T</div><h3>Timeline</h3><p>Every author placed by century, from Clement of Rome to Pope Leo XIV.</p></a>'+
  '<a class="sec-card" href="#/doctors"><span class="count">'+docs.length+'</span><div class="glyph">D</div><h3>Doctors of the Church</h3><p>The '+docs.length+' saints whose teaching the Church holds up as eminent.</p></a>';
  Object.keys(SECTIONS).forEach(function(k){var s=SECTIONS[k];h+='<a class="sec-card" href="#/'+k+'"><span class="count">'+cnt[k]+'</span><div class="glyph">'+s.g+'</div><h3>'+esc(s.t)+'</h3><p>'+esc(s.d)+'</p></a>'});
  h+='<a class="sec-card" href="#/books"><span class="count">'+(window.BOOKS_COUNT||6633).toLocaleString()+'</span><div class="glyph">B</div><h3>Books</h3><p>Every title in the isidore.co Calibre library, searchable by title, author, series and subject.</p></a>';
  h+='<a class="sec-card" href="#/editions"><span class="count">60+</span><div class="glyph">E</div><h3>Which Edition?</h3><p>The best translation and edition of each Catholic classic, with free texts and where to buy.</p></a>';
  h+='<a class="sec-card" href="#/reading"><span class="count">10</span><div class="glyph">❦</div><h3>Reading Lists</h3><p>Start Here, Apologetics, Spiritual Classics, a Waugh starter, the Chesterton shelf and more.</p></a>';
  h+='<a class="sec-card" href="#/substacks"><span class="count">30+</span><div class="glyph">S</div><h3>Catholic Substacks</h3><p>The best Catholic writers and newsletters, with our featured Chesterton column.</p></a>';
  h+='<a class="sec-card" href="#/isidore"><span class="count">'+D.isidore.length.toLocaleString()+'</span><div class="glyph">I</div><h3>Isidore Index</h3><p>A readable A–Z of every author folder in the isidore.co Calibre library.</p></a></div>';
  h+='<div class="rule"></div><div class="page-head"><div class="eyebrow">Start here</div><h2>Beloved voices</h2></div><div class="feature-strip">'+picks.map(function(a){return '<a href="#/author/'+a.id+'">'+avatar(a)+esc(a.name)+'</a>'}).join('')+'</div>';
  h+='<a class="feat-banner" href="#/substacks"><span class="eyebrow">Featured column</span><b>Chris Wettig on Substack</b><span>Chesterton commentary, coming soon. Read his latest essays now →</span></a>';
  h+='<div class="two" style="margin-top:20px"><div class="panel"><h3>Read the Church in her own words</h3><ul class="linklist">'+[['Catechism of the Catholic Church','https://www.vatican.va/archive/ENG0015/_INDEX.HTM'],['Documents of Vatican II','https://www.vatican.va/archive/hist_councils/ii_vatican_council/index.htm'],['Code of Canon Law','https://www.vatican.va/archive/cod-iuris-canonici/cic_index_en.html'],['Pope Leo XIV','https://www.vatican.va/content/leo-xiv/en.html'],['Today’s Mass readings (USCCB)','https://bible.usccb.org/daily-bible-reading']].map(function(x){return '<li><a href="'+x[1]+'" target="_blank" rel="noopener"><span class="k read">read</span>'+x[0]+' ↗</a></li>'}).join('')+'</ul></div>'+
  '<div class="panel"><h3>The great libraries</h3><ul class="linklist">'+[['St. Isidore e-book library (Calibre)','https://isidore.co/calibre'],['New Advent — Encyclopedia, Fathers, Summa','https://www.newadvent.org/'],['Christian Classics Ethereal Library','https://ccel.org/'],['Documenta Catholica Omnia','https://www.documentacatholicaomnia.eu/'],['Corpus Thomisticum','https://www.corpusthomisticum.org/']].map(function(x){return '<li><a href="'+x[1]+'" target="_blank" rel="noopener"><span class="k site">site</span>'+x[0]+' ↗</a></li>'}).join('')+'</ul></div></div>';
  render(h,'');document.title='Bibliotheca Catholica — a library of libraries';
}
var AF={q:'',eras:{},tags:{},sort:'chron'};
function authors(opts){
  opts=opts||{};var doctorsOnly=opts.doctors;
  var h='<div class="page-head"><div class="eyebrow">'+(doctorsOnly?'Doctores Ecclesiae':'Auctores')+'</div><h1>'+(doctorsOnly?'Doctors of the Church':'Catholic Authors')+'</h1><p class="lede">'+(doctorsOnly?'The saints proclaimed Doctors of the Church for their eminent learning and holiness — from St. Athanasius to St. John Henry Newman (2025).':'From the Apostolic Fathers to the present day. Filter by era or vocation, or type to narrow instantly.')+'</p></div>';
  h+='<div class="toolbar"><input type="search" id="af-q" placeholder="Filter by name, work, keyword…" value="'+esc(AF.q)+'"><select id="af-sort" aria-label="Sort"><option value="chron">Chronological</option><option value="az">A → Z</option></select>'+
   '<div class="filter-row"><label>Era</label><div class="chips" id="af-eras">'+D.eras.map(function(e){return '<button class="chip gold'+(AF.eras[e.id]?' on':'')+'" data-era="'+e.id+'" title="'+esc(e.range)+'">'+esc(e.label)+'</button>'}).join('')+'</div></div>'+
   (doctorsOnly?'':'<div class="filter-row"><label>Type</label><div class="chips" id="af-tags">'+TAGF.map(function(t){return '<button class="chip'+(AF.tags[t]?' on':'')+'" data-tag="'+t+'">'+esc(TAGL[t])+'</button>'}).join('')+'</div></div>')+'</div><div class="result-meta" id="af-meta"></div><div id="af-out"></div>';
  render(h,doctorsOnly?'doctors':'authors');
  $('#af-sort').value=AF.sort;
  function draw(){var q=norm(AF.q),eras=Object.keys(AF.eras).filter(function(k){return AF.eras[k]}),tags=Object.keys(AF.tags).filter(function(k){return AF.tags[k]});
    var L=A.filter(function(a){if(doctorsOnly&&!a.doctor)return false;if(eras.length&&eras.indexOf(a.era)<0)return false;if(!doctorsOnly&&tags.length&&!tags.every(function(t){return a.tags.indexOf(t)>=0}))return false;
      if(q){var x=norm(a.name+' '+a.desc+' '+a.wikiDesc+' '+a.tags.join(' ')+' '+a.works.map(function(w){return w.title}).join(' '));return q.split(/\s+/).every(function(t){return x.indexOf(t)>=0})}return true});
    $('#af-meta').textContent=L.length+' of '+(doctorsOnly?A.filter(function(a){return a.doctor}).length:A.length)+' authors';
    var out='';
    if(AF.sort==='az'){L=L.slice().sort(function(a,b){return a.name.localeCompare(b.name)});out='<div class="grid g-authors">'+L.map(acard).join('')+'</div>'}
    else{var cur=null;D.eras.forEach(function(e){var g=L.filter(function(a){return a.era===e.id});if(!g.length)return;out+='<div class="era-block"><h2>'+esc(e.label)+'</h2><span>'+esc(e.range)+' · '+g.length+'</span></div><div class="grid g-authors">'+g.map(acard).join('')+'</div>'})}
    $('#af-out').innerHTML=out||'<div class="empty">No authors match. Try clearing a filter.</div>'}
  draw();
  $('#af-q').addEventListener('input',function(e){AF.q=e.target.value;draw()});
  $('#af-sort').addEventListener('change',function(e){AF.sort=e.target.value;draw()});
  main.addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;if(b.dataset.era){AF.eras[b.dataset.era]=!AF.eras[b.dataset.era]}else if(b.dataset.tag){AF.tags[b.dataset.tag]=!AF.tags[b.dataset.tag]}b.classList.toggle('on');draw()});
}
function author(id){
  var a=AID[id];if(!a)return notfound();
  var kinds={read:'read',site:'site',search:'search',about:'about'};
  var links=a.links.slice().sort(function(x,y){var o={read:0,site:1,about:2,search:3};return o[x.kind]-o[y.kind]});
  var same=A.filter(function(b){return b.era===a.era&&b.id!==a.id}).slice(0,14);
  var h='<a class="backlink" href="#/authors">← All authors</a><div class="detail"><article class="detail-main"><div class="detail-head">'+avatar(a)+'<div><div class="eyebrow">'+esc(ERA[a.era].label)+(a.century?' · '+ord(a.century)+' century':'')+'</div><h1>'+esc(a.name)+'</h1><div class="dates">'+esc(dates(a))+'</div>'+badges(a,8)+'</div></div>'+
   '<p class="summary dropcap">'+esc(a.desc)+'</p>'+(a.extract?'<div class="extract"><p>'+esc(a.extract)+(a.extract.length>=595?'…':'')+'</p><p class="small">Summary from Wikipedia'+(a.wikiDesc?' — “'+esc(a.wikiDesc)+'”':'')+'.</p></div>':'');
  var _w='';if(a.works.length)_w='<div class="rule"></div><h3>Works to read online (New Advent)</h3><ul class="works">'+a.works.map(function(w){return '<li><a href="'+esc(w.url)+'" target="_blank" rel="noopener">'+esc(w.title)+'</a></li>'}).join('')+'</ul>';
  h+=_w+'<div id="au-books"></div></article><aside class="side"><div class="panel"><h3>Read &amp; explore</h3><ul class="linklist">'+links.map(function(l){return '<li><a href="'+esc(l.url)+'" target="_blank" rel="noopener"><span class="k '+kinds[l.kind]+'">'+l.kind+'</span>'+esc(l.label)+' ↗</a></li>'}).join('')+'</ul></div>'+
   '<div id="au-ed"></div><div class="panel"><h3>Also in this era</h3><div class="related">'+same.map(function(b){return '<a href="#/author/'+b.id+'">'+esc(b.name)+'</a>'}).join('')+'</div></div></aside></div>';
  render(h,'authors');document.title=a.name+' — Bibliotheca Catholica';authorBooks(a);authorEditions(a);
}
function timeline(){
  var by={};A.forEach(function(a){if(!a.century)return;(by[a.century]=by[a.century]||[]).push(a)});
  var cs=Object.keys(by).map(Number).sort(function(a,b){return a-b});
  var h='<div class="page-head"><div class="eyebrow">Per saecula</div><h1>Timeline of Catholic Authors</h1><p class="lede">Each author placed in the century of their principal work. Gold-bordered names are Doctors of the Church.</p></div><div class="timeline">';
  cs.forEach(function(c){var L=by[c].sort(function(a,b){return (a.died||a.born+60)-(b.died||b.born+60)});h+='<div class="century"><div class="c-label">'+roman(c)+'<small>'+((c-1)*100)+'–'+(c*100)+'</small></div><div class="c-people">'+L.map(function(a){return '<a class="'+(a.doctor?'doc':'')+'" href="#/author/'+a.id+'" title="'+esc(dates(a)+' — '+a.desc)+'">'+avatar(a,'mini')+esc(a.name)+'</a>'}).join('')+'</div></div>'});
  render(h+'</div>','timeline');
}
function section(k){
  var s=SECTIONS[k];var R=D.resources.filter(function(r){return r.section===k});var cats=[];R.forEach(function(r){if(cats.indexOf(r.category)<0)cats.push(r.category)});
  var h='<div class="page-head"><div class="eyebrow">'+esc(s.e)+'</div><h1>'+esc(s.t)+'</h1><p class="lede">'+esc(s.d)+'</p></div>';
  if(k==='magisterium')h+='<div class="callout">For the authoritative text of any papal or curial document, <a href="https://www.vatican.va/content/vatican/en.html" target="_blank" rel="noopener">vatican.va</a> is always the primary source; the other links here are convenient mirrors and finding aids.</div>';
  if(k==='libraries')h+='<div class="callout">This hub is built to complement the <a href="https://isidore.co/calibre" target="_blank" rel="noopener">St. Isidore e-book library</a>. Browse its authors in a readable A–Z on the <a href="#/isidore">Isidore Index</a> page.</div>';
  h+='<div class="toolbar"><input type="search" id="rs-q" placeholder="Filter '+esc(s.t)+'…"><div class="chips" id="rs-c"><button class="chip on" data-c="">All</button>'+cats.map(function(c){return '<button class="chip" data-c="'+esc(c)+'">'+esc(c)+'</button>'}).join('')+'</div></div><div id="rs-out"></div>';
  render(h,k);var cur='',q='';
  function draw(){var out='';cats.forEach(function(c){if(cur&&c!==cur)return;var L=R.filter(function(r){return r.category===c&&(!q||norm(r.name+' '+r.desc+' '+r.tags.join(' ')).indexOf(norm(q))>=0)});if(!L.length)return;out+='<div class="cat-title"><h2>'+esc(c)+'</h2></div><div class="grid g-res">'+L.map(rcard).join('')+'</div>'});$('#rs-out').innerHTML=out||'<div class="empty">Nothing matches.</div>'}
  draw();$('#rs-q').addEventListener('input',function(e){q=e.target.value;draw()});
  $('#rs-c').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;cur=b.dataset.c;document.querySelectorAll('#rs-c .chip').forEach(function(x){x.classList.toggle('on',x===b)});draw()});
}
function isidore(){
  var h='<div class="page-head"><div class="eyebrow">Index Isidorianus</div><h1>The isidore.co Library, A to Z</h1><p class="lede">Every author folder in the <a href="https://isidore.co/CalibreLibrary/" target="_blank" rel="noopener">St. Isidore Calibre library</a> ('+D.isidore.length.toLocaleString()+' entries), presented as a readable index. Each name opens that author’s folder of e-books on isidore.co.</p></div>'+
   '<div class="callout">Prefer searching by title or subject? Use isidore.co’s own <a href="https://isidore.co/calibre" target="_blank" rel="noopener">Calibre interface</a> or its lightweight <a href="https://isidore.co/calibre/mobile" target="_blank" rel="noopener">list view</a>.</div>'+
   '<div class="toolbar"><input type="search" id="iso-q" placeholder="Filter '+D.isidore.length+' authors…"></div><div class="letters" id="iso-l"></div><div class="result-meta" id="iso-m"></div><div class="iso-list" id="iso-out"></div>';
  render(h,'isidore');
  var L=D.isidore.slice().sort(function(a,b){return norm(a.n).localeCompare(norm(b.n))});
  function key(n){var c=norm(n).replace(/^[^a-z]+/,'').charAt(0).toUpperCase();return c||'#'}
  function draw(q){var t=norm(q||''),out='',last='',letters=[],n=0;L.forEach(function(i){if(t&&norm(i.n).indexOf(t)<0)return;n++;var k=key(i.n);if(k!==last){out+='<h3 id="L-'+k+'">'+k+'</h3>';letters.push(k);last=k}out+='<a href="'+esc(i.u)+'" target="_blank" rel="noopener">'+(t?hl(i.n,q):esc(i.n))+'</a>'});
   $('#iso-out').innerHTML=out||'<div class="empty">No folders match.</div>';$('#iso-m').textContent=n+' folders';$('#iso-l').innerHTML=letters.map(function(k){return '<a href="javascript:void 0" data-l="'+k+'">'+k+'</a>'}).join('')}
  draw();$('#iso-q').addEventListener('input',function(e){draw(e.target.value)});
  $('#iso-l').addEventListener('click',function(e){var a=e.target.closest('a');if(!a)return;var el=document.getElementById('L-'+a.dataset.l);if(el)window.scrollTo({top:el.getBoundingClientRect().top+scrollY-140,behavior:'smooth'})});
}
function results(q){
  if(!GD){loadGuide(function(){if(decodeURIComponent(location.hash).indexOf('#/search/')===0)results(q)})}
  if(!B){loadBooks(function(){if(decodeURIComponent(location.hash).indexOf('#/search/')===0)results(q)})}
  var R=search(q,1200);var groups={};R.forEach(function(e){(groups[e.type]=groups[e.type]||[]).push(e)});
  var order=['Author','Edition guide','Reading list','Book','Work','Substack','Sacred Scripture','Magisterium','References','Podcasts & Media','Libraries & Institutions','isidore.co folder'];
  var h='<div class="page-head"><div class="eyebrow">Quaerite et invenietis</div><h1>Results for “'+esc(q)+'”</h1><p class="result-meta">'+R.length+(R.length>=600?'+':'')+' matches across authors, books, works, resources and the isidore.co index'+(B?'':' (loading books…)')+' · <a href="https://isidore.co/calibre/mobile?search='+encodeURIComponent(q)+'&num=25" target="_blank" rel="noopener">Search isidore.co’s full catalog for “'+esc(q)+'” ↗</a> · <a href="https://www.vatican.va/content/vatican/en/search.html?q='+encodeURIComponent(q)+'" target="_blank" rel="noopener">Search vatican.va ↗</a></p></div>';
  if(!R.length)h+='<div class="empty">Nothing found here. Try the external searches above.</div>';
  order.forEach(function(g){var L=groups[g];if(!L)return;h+='<section class="sr-group"><div class="cat-title"><h2>'+esc(g==='Author'?'Authors':g==='Work'?'Works':g==='isidore.co folder'?'isidore.co library folders':g==='Book'?'Books in the isidore.co catalog':g)+' <span class="small">('+L.length+')</span></h2>'+(g==='Book'?'<a class="cat-more" href="#/books/'+encodeURIComponent(q)+'">Browse all in Books →</a>':'')+'</div>'+L.slice(0,g==='isidore.co folder'?40:g==='Book'?30:60).map(function(e){return '<a class="sr-item" href="'+esc(e.h)+'"'+(e.ext?' target="_blank" rel="noopener"':'')+'><small>'+esc(e.type)+(e.ext?' · '+esc(host(e.h))+' ↗':'')+'</small><br><b>'+hl(e.t,q)+'</b><span>'+hl(e.s.slice(0,220),q)+'</span></a>'}).join('')+'</section>'});
  render(h,'');document.title='Search: '+q+' — Bibliotheca Catholica';$('#q').value=q;
}
function notfound(){render('<div class="empty"><h2>Not found</h2><p><a href="#/">Return home</a></p></div>','')}
function route(){var h=decodeURIComponent(location.hash.replace(/^#\/?/,''));var p=h.split('/');
  hideSug();
  switch(p[0]){case '':home();break;case 'authors':authors();break;case 'doctors':authors({doctors:true});break;case 'author':author(p[1]);break;case 'timeline':timeline();break;
   case 'scripture':case 'magisterium':case 'references':case 'media':case 'libraries':section(p[0]);break;case 'isidore':isidore();break;case 'books':books(p.slice(1).join('/'));break;case 'editions':editions(p[1]||'');break;case 'reading':reading(p[1]||'');break;case 'substacks':substacks();break;case 'search':results(p.slice(1).join('/'));break;default:notfound()}}
window.addEventListener('hashchange',route);

/* ---------- header search with suggestions ---------- */
var qi=$('#q'),sg=$('#suggest'),act=-1;
function hideSug(){sg.hidden=true;act=-1}
function showSug(){var q=qi.value.trim();if(q.length<2){hideSug();return}if(!B)loadBooks(function(e){if(!e&&document.activeElement===qi)showSug()});if(!GD)loadGuide(function(e){if(!e&&document.activeElement===qi)showSug()});var R=search(q,60);var by={},order=[];R.forEach(function(e){if(!by[e.type]){by[e.type]=[];order.push(e.type)}if(by[e.type].length<(e.type==='Author'?6:e.type==='Book'?5:3))by[e.type].push(e)});
  var html='';order.slice(0,7).forEach(function(t){html+='<div class="sg-h">'+esc(t)+'</div>'+by[t].map(function(e){return '<a role="option" href="'+esc(e.h)+'"'+(e.ext?' target="_blank" rel="noopener"':'')+'><span>'+hl(e.t,q)+(e.ext?' ↗':'')+'</span><small>'+esc(e.s)+'</small></a>'}).join('')});
  html+='<a class="sg-all" href="#/search/'+encodeURIComponent(q)+'">See all results for “'+esc(q)+'” →</a>';sg.innerHTML=html;sg.hidden=false;act=-1}
qi.addEventListener('input',showSug);qi.addEventListener('focus',showSug);
qi.addEventListener('keydown',function(e){var items=sg.querySelectorAll('a');
  if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(!items.length)return;act=(act+(e.key==='ArrowDown'?1:-1)+items.length)%items.length;items.forEach(function(x,i){x.classList.toggle('active',i===act)});items[act].scrollIntoView({block:'nearest'})}
  else if(e.key==='Enter'){e.preventDefault();if(act>=0&&items[act]){items[act].click()}else if(qi.value.trim()){location.hash='#/search/'+encodeURIComponent(qi.value.trim())}hideSug();qi.blur()}
  else if(e.key==='Escape'){hideSug();qi.blur()}});
document.addEventListener('click',function(e){if(!e.target.closest('.searchwrap'))hideSug()});
sg.addEventListener('click',function(e){if(e.target.closest('a'))setTimeout(hideSug,0)});
document.addEventListener('keydown',function(e){if(e.key==='/'&&!/input|textarea|select/i.test(document.activeElement.tagName)){e.preventDefault();qi.focus()}});
$('#themeBtn').addEventListener('click',function(){var t=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=t;try{localStorage.setItem('hub-theme',t)}catch(e){}});
$('#menuBtn').addEventListener('click',function(){$('#mainnav').classList.toggle('open')});
route();
})();
