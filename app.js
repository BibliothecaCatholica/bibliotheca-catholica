(function(){
'use strict';
var D=window.HUB_DATA; var $=function(s,r){return (r||document).querySelector(s)}; var main=$('#main');
if(!D){main.innerHTML='<div class="empty">Data failed to load (data/data.js).</div>';return}
$('#gen').textContent=D.generated;
var ERA={};D.eras.forEach(function(e,i){e.i=i;ERA[e.id]=e});
var A=D.authors.slice().sort(function(a,b){return (ERA[a.era].i-ERA[b.era].i)||((a.born||a.died||0)-(b.born||b.died||0))});
var AID={};A.forEach(function(a){AID[a.id]=a});
var SECTIONS={scripture:{t:'Sacred Scripture',e:'Verbum Dei',d:'Bibles in English, Latin, and the original languages; commentaries ancient and modern; daily readings.',g:'✠'},
 magisterium:{t:'Magisterium',e:'Documents of the Church',d:'Catechisms, ecumenical councils, papal encyclicals, canon law, and doctrinal documents — straight from the source.',g:'☩'},
 references:{t:'References',e:'Instrumenta',d:'Encyclopedias, dictionaries, the Summa, patristic collections, liturgy, chant, saints, and apologetics.',g:'R'},
 media:{t:'Podcasts & Media',e:'Fides ex auditu',d:'The major Catholic podcasts, YouTube channels, radio and TV networks, and news outlets.',g:'♪'},
 libraries:{t:'Libraries & Institutions',e:'Bibliothecae',d:'The great Catholic digital libraries, archives, learning institutes, publishers, and homeschool programs.',g:'L'},
 prayers:{t:'Prayers & Devotions',e:'Ora et labora',d:'The common prayers of the Church, the Rosary, daily readings, the saint of the day, prayer apps, and parish finders.',g:'✝'}};
var PR=window.PRAYERS||null;
var TAGL={father:'Church Father',doctor:'Doctor of the Church',saint:'Saint',pope:'Pope',martyr:'Martyr',bishop:'Bishop',cardinal:'Cardinal',theologian:'Theologian',philosopher:'Philosopher',mystic:'Mystic',apologist:'Apologist',novelist:'Novelist',poet:'Poet',historian:'Historian',spiritual:'Spiritual writer',monastic:'Monastic',scripture:'Scripture scholar',convert:'Convert',founder:'Founder',preacher:'Preacher',liturgist:'Liturgist',scientist:'Scientist',journalist:'Journalist',canonist:'Canonist',catechist:'Catechist'};
var TAGF=['doctor','father','saint','pope','martyr','theologian','philosopher','mystic','spiritual','apologist','scripture','historian','novelist','poet','monastic','convert','founder','liturgist','scientist'];
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function norm(s){return String(s||'').replace(/\b([a-z])\.\s*([a-z])\./gi,'$1$2').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
function roman(n){var r='',m=[[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']];m.forEach(function(p){while(n>=p[0]){r+=p[1];n-=p[0]}});return r}
function ord(n){var s=['th','st','nd','rd'],v=n%100;return n+(s[(v-20)%10]||s[v]||s[0])}
function dates(a){if(a.dshow)return a.dshow;if(a.born&&a.died){var c=a.died<1000?'c. ':'';return c+a.born+' – '+a.died}if(a.born&&!a.died)return 'b. '+a.born;if(a.died)return 'd. '+a.died;return ''}
function initial(n){var s=n.replace(/^(St\.|Pope|Bishop|Fr\.|Dr\.|Mother|Dom|Bl\.)\s+/,'');return s.charAt(0)}
function avatar(a,cls){return '<span class="'+(cls||'avatar')+'">'+(a.img?'<img loading="lazy" alt="" src="'+esc(a.img)+'" onerror="this.remove()">':'')+(a.img?'':esc(initial(a.name)))+'</span>'}
function host(u){try{return new URL(u).hostname.replace(/^www\./,'')}catch(e){return ''}}
function fav(u){var h=host(u);return h?'<img class="fav" loading="lazy" alt="" src="https://www.google.com/s2/favicons?domain='+encodeURIComponent(h)+'&sz=64" onerror="this.style.visibility=\'hidden\'">':''}
function badges(a,max){var t=a.tags.filter(function(x){return TAGL[x]});t.sort(function(x,y){return TAGF.indexOf(x)-TAGF.indexOf(y)});return '<div class="badges">'+t.slice(0,max||4).map(function(x){return '<span class="badge '+x+'">'+esc(x==='doctor'?'Doctor':TAGL[x])+'</span>'}).join('')+'</div>'}
function acard(a){return '<a class="acard" href="#/author/'+a.id+'">'+avatar(a)+'<div><h3>'+esc(a.name)+'</h3><div class="dates">'+esc(dates(a))+' · '+esc(ERA[a.era].label)+'</div><p>'+esc(a.desc)+'</p>'+badges(a)+'</div></a>'}
function rcard(r){return '<a class="rcard" href="'+esc(r.url)+'" target="_blank" rel="noopener"><div class="rc-top">'+fav(r.url)+'<h3>'+esc(r.name)+'</h3></div><p>'+esc(r.desc)+'</p><div class="host">'+esc(host(r.url))+' ↗</div></a>'}
function setNav(k){document.querySelectorAll('.mainnav a').forEach(function(a){var active=a.dataset.nav===k;a.classList.toggle('on',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});$('#mainnav').classList.remove('open');$('#menuBtn').setAttribute('aria-expanded','false');$('#menuBtn').setAttribute('aria-label','Open menu')}

function render(html,k){main.innerHTML=html;setNav(k);window.scrollTo(0,0);document.title=(k?($('.page-head h1')||{}).textContent||'':'')+(k?' — ':'')+'Bibliotheca Catholica'}

/* ---------- search index ---------- */
var IDX=[];
A.forEach(function(a){IDX.push({type:'Author',t:a.name,s:dates(a)+' · '+a.desc,h:'#/author/'+a.id,x:norm(a.name+' '+a.tags.join(' ')+' '+a.desc+' '+a.wikiDesc+' '+ERA[a.era].label),w:3});
  a.works.forEach(function(w){IDX.push({type:'Work',t:w.title,s:a.name+' · New Advent',h:w.url,ext:1,x:norm(w.title+' '+a.name),w:2})})});
D.resources.forEach(function(r){IDX.push({type:SECTIONS[r.section].t,t:r.name,s:r.category+' · '+r.desc,h:r.url,ext:1,x:norm(r.name+' '+r.category+' '+r.desc+' '+r.tags.join(' ')+' '+r.section),w:2.5})});
if(PR)PR.groups.forEach(function(g){g.items.forEach(function(p){IDX.push({type:'Prayer',t:p.t,s:g.t+' · '+p.en.slice(0,110)+'…',h:'#/prayers/'+p.id,x:norm(p.t+' prayer '+g.t+' '+p.en+' '+(p.la||'')),w:3})})});
D.isidore.forEach(function(i){IDX.push({type:'isidore.co folder',t:i.n,s:'Author folder in the St. Isidore e-book library',h:i.u,ext:1,x:norm(i.n),w:1})});
var searchScope='all';
IDX=IDX.concat(window.BCLibrary.entries);
function search(q,lim){return window.BCSearch.search(IDX,q,searchScope,lim)}
function searchHref(q){return '#/search/'+encodeURIComponent(q)+'?scope='+searchScope}
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
var LANGN={eng:'English',lat:'Latin',fra:'French',ita:'Italian',spa:'Spanish',deu:'German',por:'Portuguese',grc:'Ancient Greek',ell:'Greek',nld:'Dutch',pol:'Polish',heb:'Hebrew',rus:'Russian',hun:'Hungarian',cat:'Catalan',ara:'Arabic',syr:'Syriac',cop:'Coptic',lit:'Lithuanian',ces:'Czech',slk:'Slovak',hrv:'Croatian',slv:'Slovenian',gle:'Irish',ina:'Interlingua',epo:'Esperanto',swe:'Swedish',dan:'Danish',nor:'Norwegian',fin:'Finnish',jpn:'Japanese',zho:'Chinese',kor:'Korean',ukr:'Ukrainian',arm:'Armenian',hye:'Armenian',chu:'Church Slavonic',und:'Undetermined',hbo:'Hebrew (Ancient)',syc:'Syriac',ile:'Interlingua (Peano)',fas:'Persian',fro:'Old & Middle French',enm:'Middle English'};
function prepBooks(R){var L=R.books.map(function(r){var o={id:r[0],t:r[1],a:r[2].map(function(i){return R.authors[i]}),y:r[3]||0,tg:r[4].map(function(i){return R.tags[i]}),se:r[5]>=0?R.series[r[5]]:'',si:r[6],f:r[7]?r[7].split('|'):[],fo:R.folders[r[8]],sub:r[9]||predSub(r[1],r[0]),lg:r[10]?r[10].split(','):[],pub:r[11]>=0?R.publishers[r[11]]:'',er:(r[12]!=null&&r[12]>=0&&R.eras)?R.eras[r[12]%100]:'',eri:r[12]>=100};
   o.an=o.a.map(function(x){return x[0]}).join(' & ');o.x=norm(o.t+' '+o.an+' '+o.se+' '+o.tg.join(' ')+' '+o.pub+' '+o.y);o.tn=norm(o.t);o.ts=o.tn.replace(/^[^a-z0-9]+/,'').replace(/^(the|a|an) /,'');return o});
  var BY={};L.forEach(function(b){b.a.forEach(function(x){if(x[1]&&AID[x[1]]){(BY[x[1]]=BY[x[1]]||[]).push(b)}})});
  var langs={},fmts={};L.forEach(function(b){b.lg.forEach(function(l){langs[l]=(langs[l]||0)+1});b.f.forEach(function(f){fmts[f]=(fmts[f]||0)+1})});
  var ids={};L.forEach(function(b){ids[b.id]=b});return {list:L,ids:ids,by:BY,langs:langs,fmts:fmts,server:R.server,base:R.base,count:R.count}}
function bookUrl(b){return B.server+'legacy/book/'+b.id+'/CalibreLibrary'}
function bookAppUrl(b){return B.server+'#book_id='+b.id+'&library_id=CalibreLibrary&panel=book_details'}
function bookFiles(b){return B.base+encPath(b.fo)+'/'+encPath(b.sub)+'/'}
function addBooksToIdx(){B.list.forEach(function(b){var ef=efOf(b.id);IDX.push({type:'Book',t:b.t,s:(ef?'Context note: '+(EFL.categories[ef.flag]||ef.flag)+' · ':'')+(b.an||'Unknown')+(b.y?' · '+b.y:'')+(b.se?' · '+b.se+(b.si?' #'+b.si:''):'')+' · '+b.f.join(', '),h:'#/isidore/book/'+b.id,x:b.x,w:ef?0.75:1.5})})}
function bookAuthors(b){if(!b.a.length)return '<span class="muted">Unknown</span>';return b.a.map(function(x){return x[1]&&AID[x[1]]?'<a class="b-au linked" href="#/author/'+x[1]+'" title="Author page on this site">'+esc(x[0])+'</a>':'<a class="b-au" href="#/books/'+encodeURIComponent(x[0])+'" data-author="'+esc(x[0])+'">'+esc(x[0])+'</a>'}).join(' <span class="amp">&amp;</span> ')}
var EFL=window.EDITORIAL_FLAGS||{books:{},categories:{}};
function efOf(id){return EFL.books[String(id)]||null}
function efBadge(id){var f=efOf(id);return f?' <a class="ef-badge" href="#/policy" title="This record carries an editorial context note">Context note: '+esc(EFL.categories[f.flag]||f.flag)+'</a>':''}
function efBox(id){var f=efOf(id);if(!f)return '';
  return '<aside class="ef-box" role="note" aria-label="Editorial context note"><div class="ef-h"><span class="ef-cat">'+esc(EFL.categories[f.flag]||f.flag)+'</span> Editorial context note</div><p>'+esc(f.note)+'</p>'+
   EFL.disclaimer.quotes.map(function(x){return '<blockquote class="dh-quote"><p>“'+esc(x.text)+'”</p><footer>('+esc(x.cite)+')</footer></blockquote>'}).join('')+
   '<p class="small">Source: <a href="'+esc(EFL.disclaimer.source)+'" target="_blank" rel="noopener">Dignitatis Humanae, vatican.va ↗</a> · Listing is not endorsement: see our <a href="#/policy">Fidelity &amp; Editorial Policy</a>. This record is kept for historical study and is never featured.</p></aside>'}
function policy(){render(EFL.policy_html||'<h1>Fidelity &amp; Editorial Policy</h1>','policy')}
function brow(b,q){return '<div class="brow"><div class="b-main"><a class="b-title" href="#/isidore/book/'+b.id+'">'+(q?hl(b.t,q):esc(b.t))+'</a>'+efBadge(b.id)+
  '<div class="b-meta">'+bookAuthors(b)+(b.y?' <span class="dot">·</span> '+b.y:'')+(b.se?' <span class="dot">·</span> <i>'+esc(b.se)+(b.si?' #'+b.si:'')+'</i>':'')+(b.pub?' <span class="dot">·</span> <span class="muted">'+esc(b.pub)+'</span>':'')+(b.er?' <span class="dot">·</span> <span class="era-tag">'+esc(eraLabel(b.er))+'</span>':'')+'</div>'+
  (b.tg.length?'<div class="b-tags">'+b.tg.slice(0,5).map(function(t){return '<button class="b-tag" data-tag="'+esc(t)+'">'+esc(t)+'</button>'}).join('')+'</div>':'')+'</div>'+
  '<div class="b-side"><div class="b-fmts">'+b.f.slice(0,5).map(function(f){return '<span class="fmt fmt-'+esc(f.toLowerCase())+'">'+esc(f.replace('_',' '))+'</span>'}).join('')+(!b.f.length?'<span class="small muted">No files listed</span>':'')+(b.lg.length?'<span class="lang">'+esc(b.lg.map(function(l){return LANGN[l]||l}).join(', '))+'</span>':'')+'</div>'+
  '<div class="b-links"><a href="#/isidore/book/'+b.id+'">'+(b.f.length?'Details &amp; downloads':'Catalog details — no files listed')+'</a><a href="'+esc(bookUrl(b))+'" target="_blank" rel="noopener">isidore.co ↗</a><a href="'+esc(bookFiles(b))+'" target="_blank" rel="noopener">Files ↗</a><a href="'+esc(bookAppUrl(b))+'" target="_blank" rel="noopener">Calibre ↗</a></div></div></div>'}
var OFFT=/mathemat|physics|physique|computer|programming|\blie (theory|group|algebra)|^lie|differential|calculus|algebra|mechanics|electro|electric|magnetism|quantum|astronom|astrophys|cosmolog|chemistry|relativity|thermodynam|gravity|plasma|linux|unix|networking|^security$|cryptograph|artificial intelligence|machine learning|data science|data processing|bitcoin|cooking|vegan|nutrition|health & fitness|diet|amateur radio|prepper|e-commerce|software|operating systems|open source|algorithms|combinatoric|geometry|symmetry|perturbation|celestial|satisfiab|^sat$|^c$|^web$|information technology|system administration|discrete math|group theory|mathematical|analysis$|acoustics|electronics|engineering|business|leadership|self-help|personal growth|gardening|^google$|sample book|amazon\.com|intellectual property|creative commons|biology|life sciences|embryology|medical|musical instruments|vocal technique/i;
var RELT=/relig|theolog|cathol|christ|church|saint|\bst\.|bible|biblic|liturg|spiritu|prayer|pope|papa|papal|thom|aquin|dominic|mary|virgin|scholast|apolog|catech|\bmass\b|chant|canon|monast|mystic|sacrament|god|jesus|devot|council|vatican|trent|ecclesi|moral|natural law|virtue|marriage|celibacy|sermon|patrist|fathers|creed|missal|divine office|rosary|grace|faith|jesuit|franciscan|benedictine|carmelit|duhem|jaki/i;
function offTopic(b){if(b._off!=null)return b._off;b._off=b.tg.some(function(t){return OFFT.test(t)})&&!b.tg.some(function(t){return RELT.test(t)})&&!b.a.some(function(x){return x[1]})&&!RELT.test(b.t);return b._off}
var BF={q:'',fmt:'',lang:'',era:'',tag:'',sort:'title',linked:false,ontopic:true};
function bfReset(){BF.q='';BF.fmt='';BF.lang='';BF.era='';BF.tag='';BF.linked=false;BF.ontopic=true;BF.sort='title'}
function eraLabel(id){return ERA[id]?ERA[id].label:id}
function books(arg){
  if(arg!=null&&arg!==''){var m=/^(lang|era|fmt|tag|q)=(.*)$/.exec(arg);bfReset();if(m){BF[m[1]==='q'?'q':m[1]]=m[2]}else BF.q=arg}
  var h='<div class="page-head isx-head"><div class="eyebrow">Index Isidorianus · EPUB &amp; PDF downloads</div><h1>The Isidore Index</h1><p class="lede">All '+(window.BOOKS_COUNT||6633).toLocaleString()+' books in the <a href="https://isidore.co/calibre" target="_blank" rel="noopener">St. Isidore e-book library</a>, catalogued and searchable by title, author, series, subject, language, format, and era. Every book has a detail page with download links back to isidore.co.</p>'+
   '<p class="callout">Catalog records are imported from isidore.co as supplied and have not each been reviewed; inclusion is not a recommendation. For a hand-picked starting point with texts you can read here, see <a href="#/library">Discover &amp; Read</a>. Some records carry editorial context notes: see the <a href="#/policy">Fidelity &amp; Editorial Policy</a>.</p><div class="isx-tabs"><a class="on" href="#/isidore">Books</a><a href="#/isidore/folders">Author folders A–Z ('+D.isidore.length.toLocaleString()+')</a></div></div>'+
   '<div class="toolbar isx-tools"><input type="search" id="bk-q" placeholder="Search titles, authors, series, subjects…" value="'+esc(BF.q)+'">'+
   '<div class="isx-sel"><label>Sort<select id="bk-sort"><option value="title">English first, A → Z</option><option value="az">Title A → Z (all languages)</option><option value="author">Author A → Z</option><option value="old">Oldest catalog date</option><option value="new">Newest catalog date</option></select></label>'+
   '<label>Era<select id="bk-era"><option value="">All eras</option></select></label>'+
   '<label>Language<select id="bk-lang"><option value="">All languages</option></select></label>'+
   '<label>Subject<select id="bk-tag"><option value="">All subjects</option></select></label></div>'+
   '<div class="filter-row"><label>Format</label><div class="chips" id="bk-fmt"></div></div>'+
   '<div class="filter-row"><label>Show</label><div class="chips"><button class="chip gold'+(BF.ontopic?' on':'')+'" id="bk-ontopic" title="Hide maths, computing, cooking, and other off-topic books that share the isidore.co shelves">Catholic &amp; related subjects only</button><button class="chip gold'+(BF.linked?' on':'')+'" id="bk-linked" title="Only books by authors who have a page on this site">Authors with a page here</button><button class="chip" id="bk-clear">Clear filters</button></div></div></div>'+
   '<div class="result-meta" id="bk-meta">Loading the catalog…</div><div class="blist" id="bk-out"></div><div class="bk-more-wrap"><button class="btn ghost" id="bk-more" hidden>Show more</button></div>'+
   '<p class="small muted isx-note">Era comes from the author’s page on this site, or else from life dates in the catalog’s author name (marked “inferred”); it is blank when neither is known. Catalog dates are often scan or reprint dates, so they say nothing about copyright. Data: <a href="#/data">Open Data</a>.</p>';
  render(h,'isidore');
  loadBooks(function(err){if(err){$('#bk-meta').textContent='The book catalog could not be loaded.';return}if(!$('#bk-out'))return;
    var shown=60,cur=[];
    function base(skip){var toks=norm(BF.q).split(/\s+/).filter(Boolean);return B.list.filter(function(b){
        if(skip!=='fmt'&&BF.fmt&&b.f.indexOf(BF.fmt)<0)return false;if(skip!=='lang'&&BF.lang&&b.lg.indexOf(BF.lang)<0)return false;if(skip!=='tag'&&BF.tag&&b.tg.indexOf(BF.tag)<0)return false;
        if(skip!=='era'&&BF.era&&b.er!==BF.era)return false;
        if(BF.linked&&!b.a.some(function(x){return x[1]}))return false;if(BF.ontopic&&offTopic(b))return false;
        for(var j=0;j<toks.length;j++)if(b.x.indexOf(toks[j])<0)return false;return true})}
    function counts(L,fn){var c={};L.forEach(function(b){fn(b).forEach(function(v){if(v)c[v]=(c[v]||0)+1})});return c}
    function facets(){
      var ce=counts(base('era'),function(b){return [b.er]});$('#bk-era').innerHTML='<option value="">All eras</option>'+D.eras.filter(function(e){return ce[e.id]||BF.era===e.id}).map(function(e){return '<option value="'+e.id+'">'+esc(e.label)+' ('+(ce[e.id]||0).toLocaleString()+')</option>'}).join('');$('#bk-era').value=BF.era;
      var cl=counts(base('lang'),function(b){return b.lg});var ll=Object.keys(cl).sort(function(a,b){return cl[b]-cl[a]});if(BF.lang&&ll.indexOf(BF.lang)<0)ll.unshift(BF.lang);
      $('#bk-lang').innerHTML='<option value="">All languages ('+ll.length+')</option>'+ll.map(function(l){return '<option value="'+esc(l)+'">'+esc(LANGN[l]||l)+' ('+(cl[l]||0).toLocaleString()+')</option>'}).join('');$('#bk-lang').value=BF.lang;
      var ct=counts(base('tag'),function(b){return b.tg});var tl=Object.keys(ct).sort(function(a,b){return ct[b]-ct[a]}).slice(0,120);if(BF.tag&&tl.indexOf(BF.tag)<0)tl.unshift(BF.tag);
      $('#bk-tag').innerHTML='<option value="">All subjects</option>'+tl.map(function(t){return '<option value="'+esc(t)+'">'+esc(t)+' ('+(ct[t]||0).toLocaleString()+')</option>'}).join('');$('#bk-tag').value=BF.tag;
      var cf=counts(base('fmt'),function(b){return b.f});var fl=Object.keys(B.fmts).sort(function(a,b){return B.fmts[b]-B.fmts[a]}).slice(0,9);
      $('#bk-fmt').innerHTML='<button class="chip'+(BF.fmt?'':' on')+'" data-f="">Any</button>'+fl.map(function(f){return '<button class="chip'+(BF.fmt===f?' on':'')+'" data-f="'+esc(f)+'">'+esc(f.replace('_',' '))+' <span class="small">'+(cf[f]||0).toLocaleString()+'</span></button>'}).join('')}
    function sortL(L){var toks=norm(BF.q).split(/\s+/).filter(Boolean);
      if(BF.sort==='new')return L.sort(function(a,b){return (b.y||0)-(a.y||0)});
      if(BF.sort==='old')return L.sort(function(a,b){return (a.y||9999)-(b.y||9999)});
      if(BF.sort==='author')return L.sort(function(a,b){return norm(a.an||'~').localeCompare(norm(b.an||'~'))});
      if(BF.sort==='az')return L.sort(function(a,b){return a.ts.localeCompare(b.ts)});
      if(toks.length){var nq=norm(BF.q);return L.map(function(b){var s=0;if(b.tn===nq)s+=20;else if(b.tn.indexOf(nq)===0)s+=10;else if(b.tn.indexOf(nq)>=0)s+=6;toks.forEach(function(t){if(b.tn.indexOf(t)>=0)s+=2});if(b.lg.indexOf('eng')>=0)s+=0.5;return [s,b]}).sort(function(a,b){return b[0]-a[0]}).map(function(x){return x[1]})}
      return L.sort(function(a,b){var ea=a.lg.indexOf('eng')>=0?0:1,eb=b.lg.indexOf('eng')>=0?0:1;return (ea-eb)||a.ts.localeCompare(b.ts)})}
    function draw(reset){if(reset){shown=60;cur=sortL(base(''));facets()}
      var f=[];if(BF.era)f.push(eraLabel(BF.era));if(BF.lang)f.push(LANGN[BF.lang]||BF.lang);if(BF.tag)f.push('“'+BF.tag+'”');if(BF.fmt)f.push(BF.fmt.replace('_',' '));
      $('#bk-meta').innerHTML='<b>'+cur.length.toLocaleString()+'</b> of '+B.list.length.toLocaleString()+' books'+(f.length?' · '+esc(f.join(' · ')):'')+(BF.ontopic?' <span class="muted">(off-topic subjects hidden)</span>':'')+(BF.q?' matching “'+esc(BF.q)+'” · <a href="https://isidore.co/calibre/mobile?search='+encodeURIComponent(BF.q)+'&num=25" target="_blank" rel="noopener">same search on isidore.co ↗</a>':'');
      $('#bk-out').innerHTML=cur.length?cur.slice(0,shown).map(function(b){return brow(b,BF.q)}).join(''):'<div class="empty">No books match. Try clearing a filter.</div>';
      $('#bk-more').hidden=shown>=cur.length;$('#bk-more').textContent='Show more ('+(cur.length-shown).toLocaleString()+' remaining)'}
    $('#bk-sort').value=BF.sort;draw(true);
    var tm;$('#bk-q').addEventListener('input',function(e){BF.q=e.target.value;clearTimeout(tm);tm=setTimeout(function(){draw(true)},140)});
    [['#bk-sort','sort'],['#bk-lang','lang'],['#bk-era','era'],['#bk-tag','tag']].forEach(function(x){$(x[0]).addEventListener('change',function(e){BF[x[1]]=e.target.value;draw(true)})});
    $('#bk-fmt').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;BF.fmt=b.dataset.f;draw(true)});
    $('#bk-linked').addEventListener('click',function(e){BF.linked=!BF.linked;e.currentTarget.classList.toggle('on',BF.linked);draw(true)});
    $('#bk-ontopic').addEventListener('click',function(e){BF.ontopic=!BF.ontopic;e.currentTarget.classList.toggle('on',BF.ontopic);draw(true)});
    $('#bk-clear').addEventListener('click',function(){bfReset();$('#bk-q').value='';$('#bk-sort').value='title';$('#bk-linked').classList.remove('on');$('#bk-ontopic').classList.add('on');draw(true)});
    $('#bk-more').addEventListener('click',function(){shown+=120;draw(false)});
    $('#bk-out').addEventListener('click',function(e){var t=e.target.closest('.b-tag');if(t){BF.tag=t.dataset.tag;draw(true);window.scrollTo({top:0,behavior:'smooth'});return}
      var a=e.target.closest('.b-au[data-author]');if(a){e.preventDefault();BF.q=a.dataset.author;$('#bk-q').value=BF.q;draw(true);window.scrollTo({top:0,behavior:'smooth'})}});
  });
}
function dlUrl(b,f){return B.server+'get/'+encodeURIComponent(f)+'/'+b.id+'/CalibreLibrary'}
function bookDetail(id){
  render('<div class="loading">Loading book…</div>','isidore');
  loadBooks(function(err){if(err){main.innerHTML='<div class="empty">The book catalog could not be loaded.</div>';return}
    var b=B.ids[id];if(!b)return notfound();
    var same=[];b.a.forEach(function(x){B.list.forEach(function(o){if(o!==b&&same.indexOf(o)<0&&o.a.some(function(y){return y[0]===x[0]}))same.push(o)})});
    var h='<a class="backlink" href="#/isidore">← The Isidore Index</a><div class="detail"><article class="detail-main bookd"><div class="eyebrow">Isidore Index · book '+b.id+'</div><h1>'+esc(b.t)+'</h1><div class="b-meta big">'+bookAuthors(b)+'</div>'+(efOf(b.id)?efBox(b.id):window.BCLibrary.readHere(b.id))+
     '<dl class="bk-dl">'+(b.y?'<dt>Catalog date</dt><dd>'+b.y+' <span class="muted small">(often a scan or reprint date)</span></dd>':'')+(b.er?'<dt>Era</dt><dd><a href="#/isidore/era='+b.er+'">'+esc(eraLabel(b.er))+'</a>'+(b.eri?' <span class="muted small">(inferred from the author’s life dates)</span>':'')+'</dd>':'')+
     (b.lg.length?'<dt>Language</dt><dd>'+b.lg.map(function(l){return '<a href="#/isidore/lang='+l+'">'+esc(LANGN[l]||l)+'</a>'}).join(', ')+'</dd>':'')+(b.se?'<dt>Series</dt><dd>'+esc(b.se)+(b.si?' #'+b.si:'')+'</dd>':'')+(b.pub?'<dt>Publisher</dt><dd>'+esc(b.pub)+'</dd>':'')+
     (b.tg.length?'<dt>Subjects</dt><dd class="b-tags">'+b.tg.map(function(t){return '<a class="b-tag" href="#/isidore/tag='+encodeURIComponent(t)+'">'+esc(t)+'</a>'}).join('')+'</dd>':'')+'</dl>'+
     '<p class="callout"><b>External catalog · unreviewed.</b> Contributor names and dates are imported as supplied. Names may include editors or translators; author links are automated associations. Inclusion does not imply a recommendation (<a href="#/policy">editorial policy</a>).</p><h3>'+(b.f.length?'Download from isidore.co':'Check the source catalog')+'</h3><div class="dl-row">'+(b.f.length?b.f.map(function(f){return '<a class="btn'+(f==='PDF'||f==='EPUB'?' gold':' ghost')+'" href="'+esc(dlUrl(b,f))+'" target="_blank" rel="noopener">'+esc(f.replace('_',' '))+' ↓</a>'}).join(''):'<span class="muted">No files listed.</span>')+'</div>'+
     '<ul class="linklist">'+[['Book page on isidore.co',bookUrl(b),'read'],['Folder of files on isidore.co',bookFiles(b),'site'],['Open in the Calibre viewer',bookAppUrl(b),'site'],['Search isidore.co for this title','https://isidore.co/calibre/mobile?search='+encodeURIComponent(b.t)+'&num=25','search']].filter(function(x){return b.f.length||x[0]!=='Open in the Calibre viewer'}).map(function(x){return '<li><a href="'+esc(x[1])+'" target="_blank" rel="noopener"><span class="k '+x[2]+'">'+x[2]+'</span>'+x[0]+' ↗</a></li>'}).join('')+'</ul>'+
     '<p class="small muted">Files are served by isidore.co; Bibliotheca Catholica hosts none of them. Check the rights status of an edition before reusing it.</p></article>'+
     '<aside class="side">'+(same.length?'<div class="panel"><h3>More by '+esc(b.a[0][0])+'</h3><ul class="linklist">'+same.slice(0,12).map(function(o){return '<li><a href="#/isidore/book/'+o.id+'">'+esc(o.t)+'</a></li>'}).join('')+'</ul></div>':'')+
     b.a.filter(function(x){return x[1]&&AID[x[1]]}).map(function(x){var a=AID[x[1]];return '<div class="panel"><h3>About the author</h3><a class="mini-au" href="#/author/'+a.id+'">'+avatar(a)+'<b>'+esc(a.name)+'</b><span>'+esc(dates(a))+'</span></a><p class="small">'+esc(a.desc)+'</p></div>'}).join('')+'</aside></div>';
    render(h,'isidore');document.title=b.t+' — Isidore Index — Bibliotheca Catholica'})}
function authorBooks(a){var box=$('#au-books');if(!box)return;loadBooks(function(err){box=$('#au-books');if(!box)return;if(err){box.innerHTML='';return}
  var L=(B.by[a.id]||[]).slice().sort(function(x,y){return x.tn.localeCompare(y.tn)});
  if(!L.length){box.innerHTML='';return}
  box.innerHTML='<div class="rule"></div><h3>Books in the isidore.co library <span class="small">('+L.length+')</span></h3><div class="blist compact">'+L.slice(0,40).map(function(b){return brow(b)}).join('')+'</div>'+(L.length>40?'<p><a href="#/isidore/'+encodeURIComponent(L[0].a.filter(function(x){return x[1]===a.id})[0][0])+'">See all '+L.length+' books →</a></p>':'');
  box.addEventListener('click',function(e){var t=e.target.closest('.b-tag');if(t){bfReset();BF.tag=t.dataset.tag;location.hash='#/isidore'}})})}


/* ---------- guide data: editions, reading lists, substacks (lazy) ---------- */
var GD=null,GWAIT=[],GLOADING=false,ED={};
function loadGuide(cb){if(GD){cb&&cb();return}if(cb)GWAIT.push(cb);if(GLOADING)return;GLOADING=true;
  function done(){var R=window.GUIDE_DATA;if(!R){GLOADING=false;GWAIT.splice(0).forEach(function(f){try{f(true)}catch(e){}});return}
    GD=R;GD.editions.forEach(function(w){ED[w.id]=w});addGuideToIdx();GWAIT.splice(0).forEach(function(f){f()})}
  if(window.GUIDE_DATA){setTimeout(done,0);return}
  var s=document.createElement('script');s.src='data/guide.js?v=20261021-collection-access';s.onload=done;s.onerror=function(){done()};document.head.appendChild(s)}
function addGuideToIdx(){GD.editions.forEach(function(w){IDX.push({type:'Edition guide',t:w.t,s:(w.a?w.a+' · ':'')+'Compare editions and translations '+w.picks.map(function(p){return p.tr}).slice(0,2).join(' · '),h:'#/editions/'+w.id,x:norm(w.t+' '+w.a+' '+w.cat+' '+w.picks.map(function(p){return p.tr+' '+p.pub}).join(' ')),w:2.6})});
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
function discl(){var t=AFF.disclosure||'';var m=/^Affiliate disclosure:\s*/.exec(t);return '<p class="disclosure">'+(m?'<b>Affiliate disclosure:</b> '+esc(t.slice(m[0].length)):esc(t))+'</p>'}
function guideWorks(w){return BCGuides.works(w,window.LIBRARY_DATA.works)}
function guideAvailability(w){return BCGuides.available(w,window.LIBRARY_DATA.works,window.READING_OPTIONS.options)}
function freeLinks(f){if(!f||!f.length)return '';return '<div class="free"><span class="free-l">Read at source</span>'+f.map(function(x){return '<a href="'+esc(x[1])+'" target="_blank" rel="noopener">'+esc(x[0])+' ↗</a>'}).join('')+'</div>'}
function guideCopies(w){return guideWorks(w).map(function(work){var edition=work.editions.find(function(e){return e.text}),option=(window.READING_OPTIONS.options[work.id]||[]).find(function(o){return o.format==='EPUB'}),con=edition?(edition.contributors||[]).map(function(c){return c.role+': '+c.name}).join(' · '):'';
 return '<div class="guide-copy"><b>'+esc(work.title)+'</b>'+(edition?'<span class="small">'+esc(edition.language+(con?' · '+con:''))+'</span>':'')+'<div class="reading-actions">'+(edition?'<a class="btn" href="#/read/'+work.id+'/'+edition.id+'">Read here</a>':'')+(!edition&&work.editions.some(function(e){return e.access==='full-text'})?'<a class="btn ghost" href="'+esc(work.editions.find(function(e){return e.access==='full-text'}).source)+'" target="_blank" rel="noopener">Read at source ↗</a>':'')+(option?'<a class="reading-action" href="'+esc(option.url)+'" target="_blank" rel="noopener">'+(option.access==='source-page'?'View EPUB options':'Download EPUB')+' · '+esc(option.provider)+' ↗</a>':'')+window.BCLibrary.sampleLinks(work)+'<a href="#/work/'+work.id+'">'+(edition?'Edition details & all formats':'Reading options & source details')+' →</a></div></div>'}).join('')}
function readingChoices(w){var copies=guideCopies(w),free=freeLinks(w.free);return (copies||free?'<div class="guide-reading">'+copies+free+'</div>':'<p class="small availability-note">No complete free reading copy is listed here yet. Check library holdings or the edition suggestions below.</p>'+window.BCLibrary.libraryLinks(w.t,w.a))+(w.readingNote?'<p class="edition-note">'+esc(w.readingNote)+'</p>':'')+(w.related&&w.related.length?'<details class="related-reading"><summary>Companion works &amp; adaptations</summary>'+freeLinks(w.related)+'</details>':'')}
function printPick(p,w,i){var ebook=p.access==='ebook';return '<li class="pick'+(i===0?' top':'')+'"><div class="pick-lbl">'+esc(p.lbl)+'</div><div class="pick-tr">'+esc(p.tr)+'</div><div class="pick-meta">'+esc(p.pub)+(isbnOk(p.isbn)?' · ISBN '+p.isbn:'')+'</div>'+(p.note?'<p>'+esc(p.note)+'</p>':'')+(ebook?'<a href="'+esc(w.free[0][1])+'" target="_blank" rel="noopener">View ebook edition ↗</a>':buyBtns(p.isbn,p.bq||(w.multi?p.lbl:w.t),w.a,p.pk))+'</li>'}
function edCard(w){var au=w.aid&&AID[w.aid]?'<a href="#/author/'+w.aid+'">'+esc(w.a)+'</a>':esc(w.a),a=guideAvailability(w),lists=GD.lists.filter(function(l){return l.items.some(function(it){return it.e===w.id})});
 return '<article class="ed-card" id="ed-'+w.id+'"><div class="ed-head"><div><div class="eyebrow">'+esc(w.cat)+(w.orig?' · '+esc(w.orig):'')+'</div><h2>'+esc(w.t)+'</h2>'+(w.a?'<div class="ed-au">'+au+'</div>':'')+'</div><span class="pd-badge">'+(a.here?'Read here':a.online?'Read at source':'Edition guide')+'</span></div><p class="ed-why">'+esc(w.why)+'</p>'+readingChoices(w)+'<details class="print-editions"><summary>Compare '+w.picks.length+' '+(w.picks.every(function(p){return p.access==='ebook'})?'ebook':'edition')+' suggestion'+(w.picks.length===1?'':'s')+'</summary><ol class="picks">'+w.picks.map(function(p,i){return printPick(p,w,i)}).join('')+'</ol>'+(w.alt?'<p class="ed-alt"><b>Other options:</b> '+esc(w.alt)+'</p>':'')+'</details>'+(lists.length?'<p class="small guide-paths">Reading paths: '+lists.map(function(l){return '<a href="#/reading/'+l.id+'">'+esc(l.t)+'</a>'}).join(' · ')+'</p>':'')+window.BCLibrary.listenEdition(w.id)+'<a class="small" href="#/editions/'+w.id+'">Link to this guide →</a></article>'}
var EF={q:'',cat:'',access:''};
function editions(arg){
 var h='<div class="page-head"><div class="eyebrow">Choose a reading copy</div><h1>Editions &amp; Translations</h1><p class="lede">Read a free edition, compare translations, or choose a print copy. The translator and the particular work matter as much as the format.</p></div><details class="panel edition-help"><summary>How to choose an edition</summary><p><b>For a first reading:</b> look for clear language and a complete text. <b>For study:</b> check the translator, notes, and references. <b>For an e-reader:</b> EPUB adapts to your screen; a scanned PDF preserves the printed page.</p><p>Online texts can use a different translation from the print suggestions. Companion works and adaptations are labeled separately. Suggestions reflect editorial judgment; retailer links may be searches, so confirm the title, translator, and ISBN before buying.</p></details><div class="toolbar guide-toolbar"><label>Find a work or edition<input type="search" id="ed-q" placeholder="Title, author, translator, publisher or ISBN…" value="'+esc(EF.q)+'"></label><label>Reading access<select id="ed-access"><option value="">All options</option><option value="here">Read here</option><option value="online">Full-text reading link</option><option value="sample">Excerpts &amp; previews</option><option value="epub">EPUB options</option></select></label><div class="chips" id="ed-c" role="group" aria-label="Edition subjects"></div></div><div class="result-meta" id="ed-m" role="status">Loading…</div><div id="ed-out" class="ed-list"></div>'+discl();
 render(h,'editions');
 loadGuide(function(err){if(err||!$('#ed-out')){if($('#ed-m'))$('#ed-m').textContent='The guide could not be loaded. Please reload to try again.';return}
  var cats=[];GD.editions.forEach(function(w){if(cats.indexOf(w.cat)<0)cats.push(w.cat)});
  function chips(){$('#ed-c').innerHTML='<button class="chip'+(EF.cat?'':' on')+'" aria-pressed="'+(!EF.cat)+'" data-c="">All subjects</button>'+cats.map(function(c){return '<button class="chip'+(EF.cat===c?' on':'')+'" aria-pressed="'+(EF.cat===c)+'" data-c="'+esc(c)+'">'+esc(c)+'</button>'}).join('')}
  function draw(){var L=GD.editions.filter(function(w){return (!EF.cat||w.cat===EF.cat)&&(!EF.access||guideAvailability(w)[EF.access])&&BCGuides.matches(w,EF.q)});$('#ed-m').textContent=L.length+' of '+GD.editions.length+' guides · reading copies and edition suggestions';$('#ed-out').innerHTML=L.map(edCard).join('')||'<div class="empty"><p>No editions match these filters.</p><button id="ed-reset">Clear filters</button></div>';var reset=$('#ed-reset');if(reset)reset.onclick=function(){EF={q:'',cat:'',access:''};$('#ed-q').value='';$('#ed-access').value='';chips();draw()}}
  // A linked title always wins over filters from a previous visit.
  if(arg){EF={q:'',cat:'',access:''};$('#ed-q').value=''}
  $('#ed-access').value=EF.access;chips();draw();
  $('#ed-q').addEventListener('input',function(e){EF.q=e.target.value;draw()});
  $('#ed-access').addEventListener('change',function(e){EF.access=e.target.value;draw()});
  $('#ed-c').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;EF.cat=b.dataset.c;chips();draw()});
  if(arg){var el=document.getElementById('ed-'+arg);if(el){el.classList.add('flash');window.scrollTo(0,Math.max(0,el.getBoundingClientRect().top+window.scrollY-document.querySelector('.topbar').getBoundingClientRect().height-20));var w=ED[arg];if(w)document.title=w.t+' — Editions & Translations — Bibliotheca Catholica'}else $('#ed-m').textContent='That edition guide was not found. Browse the guides below.'}
 })}
function recItem(it){var info=BCGuides.item(it,GD.editions,window.LIBRARY_DATA.works),w=info.guide,t=info.title,a=info.author,p=w?w.picks.find(function(x){return x.access!=='ebook'}):null,record=w||{workIds:it.workIds||[],free:it.free||[]},titleLink=w?'#/editions/'+w.id:info.works.length?'#/work/'+info.works[0].id:'',buy=p?buyBtns(p.isbn,p.bq||(w.multi?p.lbl:w.t),a,p.pk):it.t?buyBtns(it.isbn,it.t,a,it.pk):'';
 return '<li class="rec"><div class="rec-main"><h3>'+(titleLink?'<a href="'+titleLink+'">'+esc(t)+'</a>':esc(t))+'</h3><div class="ed-au">'+esc(a)+'</div><p>'+esc(it.b)+'</p>'+guideCopies(record)+freeLinks(info.free)+(!guideAvailability(record).here&&!guideAvailability(record).online?window.BCLibrary.libraryLinks(t,a):'')+(w&&w.readingNote?'<p class="edition-note">'+esc(w.readingNote)+'</p>':'')+(w?'<a class="guide-compare" href="#/editions/'+w.id+'">Compare editions &amp; translations →</a>':'')+(buy?'<details class="rec-buy"><summary>Find a print copy</summary>'+buy+'</details>':'')+'</div></li>'}
var RF={q:'',access:''};
function reading(arg){
 var h='<div class="page-head"><div class="eyebrow">Tolle, lege</div><h1>Reading Lists</h1><p class="lede">Choose a path, start with one book, and follow its reading links. Each shelf explains where to begin; you can read at your own pace.</p></div><div class="toolbar guide-toolbar"><label>Find a book or reading path<input type="search" id="rl-q" placeholder="Search titles, authors or topics…" value="'+esc(RF.q)+'"></label><label>Reading access<select id="rl-access"><option value="">All options</option><option value="here">Read here</option><option value="online">Full-text reading link</option><option value="sample">Excerpts &amp; previews</option><option value="epub">EPUB options</option></select></label></div><div class="chips rl-tabs" id="rl-t" role="group" aria-label="Reading paths"></div><div id="rl-meta" class="result-meta" role="status"></div><div id="rl-out"><div class="loading">Loading…</div></div>'+discl();
 render(h,'reading');
 loadGuide(function(err){if(!$('#rl-out'))return;if(err){$('#rl-out').innerHTML='<p>The reading lists could not be loaded. Please reload to try again.</p>';return}var cur=arg&&GD.lists.some(function(l){return l.id===arg})?arg:'';
  function draw(){var filtering=!!(RF.q.trim()||RF.access);$('#rl-t').innerHTML='<a class="chip'+(cur?'':' on')+'"'+(!cur?' aria-current="page"':'')+' href="#/reading">All paths</a>'+GD.lists.map(function(l){return '<a class="chip'+(cur===l.id?' on':'')+'"'+(cur===l.id?' aria-current="page"':'')+' href="#/reading/'+l.id+'">'+esc(l.t)+'</a>'}).join('');
   var L=(cur?GD.lists.filter(function(l){return l.id===cur}):GD.lists).map(function(l){return {list:l,items:l.items.filter(function(it){var info=BCGuides.item(it,GD.editions,window.LIBRARY_DATA.works),record=info.guide||{workIds:it.workIds||[],free:it.free||[]};return (!RF.access||guideAvailability(record)[RF.access])&&(BCGuides.matches({t:info.title,a:info.author,b:it.b},RF.q)||BCGuides.matches({t:l.t,b:l.sub},RF.q))})}}).filter(function(x){return x.items.length});
   if(!cur&&!filtering){$('#rl-meta').textContent=GD.lists.length+' reading paths · choose a shelf to see its books';$('#rl-out').innerHTML='<div class="grid g-lists">'+GD.lists.map(function(l){return '<a class="sec-card" href="#/reading/'+l.id+'"><span class="count">'+l.items.length+' reads</span><div class="glyph" aria-hidden="true">'+esc(l.ic)+'</div><h2>'+esc(l.t)+'</h2><p>'+esc(l.sub)+'</p><span class="small">'+esc(l.audience)+' →</span></a>'}).join('')+'</div>';return}
   var count=L.reduce(function(n,x){return n+x.items.length},0);$('#rl-meta').textContent=count+' reading-list entries'+(filtering?' match your filters':' · suggested starting points below')+(arg&&!cur?' · Unknown path; showing available lists':'');
   $('#rl-out').innerHTML=L.map(function(x){var l=x.list;return '<section class="rl" id="rl-'+l.id+'"><div class="cat-title"><h2>'+esc(l.t)+'</h2></div><p class="lede small">'+esc(l.sub)+'</p><div class="callout"><b>Where to begin</b><p>'+esc(l.start)+'</p></div><ol class="recs">'+x.items.map(recItem).join('')+'</ol></section>'}).join('')||'<div class="empty"><p>No reading-list entries match these filters.</p><button id="rl-reset">Clear filters</button></div>';var reset=$('#rl-reset');if(reset)reset.onclick=function(){RF={q:'',access:''};$('#rl-q').value='';$('#rl-access').value='';draw()}
  }
  // Opening a different named path should show that complete path.
  if(cur){RF={q:'',access:''};$('#rl-q').value=''}$('#rl-access').value=RF.access;draw();if(cur)document.title=GD.lists.find(function(l){return l.id===cur}).t+' — Reading Lists — Bibliotheca Catholica';
  $('#rl-q').addEventListener('input',function(e){RF.q=e.target.value;draw()});$('#rl-access').addEventListener('change',function(e){RF.access=e.target.value;draw()});
 })}
function featuredMini(){var F=GD.featured;return '<a class="feat-mini" href="#/substacks"><span class="k read">column</span> Read <b>'+esc(F.author)+'</b>’s Chesterton commentary column, coming soon, and his essays on Substack →</a>'}
function postsList(p){if(!p||!p.length)return '';return '<ul class="posts">'+p.map(function(x){return '<li><a href="'+esc(x.u)+'" target="_blank" rel="noopener">'+esc(x.t)+'</a><span>'+esc(x.d)+'</span></li>'}).join('')+'</ul>'}
function substacks(){
  var h='<div class="page-head"><div class="eyebrow">Scriptores hodierni</div><h1>Top Catholic Substacks</h1><p class="lede">Writers, columnists, and newsletters worth subscribing to, from literature and liturgy to news and the spiritual life. Latest posts are a snapshot taken when the site was last built.</p></div><div id="ss-out"><div class="loading">Loading…</div></div>';
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
  box.innerHTML='<div class="panel"><h3>Editions &amp; Translations</h3><ul class="linklist">'+L.map(function(w){return '<li><a href="#/editions/'+w.id+'"><span class="k read">guide</span>'+esc(w.t)+'</a></li>'}).join('')+'</ul></div>'})}

/* ---------- views ---------- */
function home(){
  var docs=A.filter(function(a){return a.doctor});
  var picks=['thomas-aquinas','augustine-of-hippo','g-k-chesterton','john-henry-newman','fulton-j-sheen','teresa-of-avila','flannery-o-connor','j-r-r-tolkien','joseph-ratzinger','therese-of-lisieux','hilaire-belloc','evelyn-waugh','francis-de-sales','ignatius-of-antioch'].map(function(i){return AID[i]}).filter(Boolean);
  var cnt={};D.resources.forEach(function(r){cnt[r.section]=(cnt[r.section]||0)+1});
  var h='<section class="hero hero-c"><div class="eyebrow">Bibliotheca Catholica</div><h1 class="hero-title">Tolle Lege</h1><p class="hero-trans">Take up and read</p><div class="hero-orn" aria-hidden="true"><span>✠</span></div>'+
  '<p class="hero-sub">Two thousand years of Catholic thought, in one place.</p>'+
  '<p class="lede">Discover the writers, ideas, and spiritual classics of the Catholic tradition. Read here, download an ebook, or find the edition that belongs on your shelf.</p>'+
  '<form class="hero-search" onsubmit="location.hash=\'#/search/\'+encodeURIComponent(this.q.value);return false"><input name="q" placeholder="Try “Confessions”, “Chesterton”, “encyclical”, “Latin dictionary”…" aria-label="Search"><button class="btn">Search</button></form>'+
  '<div class="hero-cta"><a class="btn gold" href="#/library">Discover &amp; Read →</a><a class="btn ghost" href="#/isidore">Explore the Isidore Index</a><a class="btn ghost" href="#/timeline">Browse the timeline</a></div>'+
  '<div class="stats"><div class="stat"><b>'+A.length+'</b><span>Catholic authors</span></div><div class="stat"><b>'+docs.length+'</b><span>Doctors of the Church</span></div><div class="stat"><b>'+D.resources.length+'</b><span>curated resources</span></div><div class="stat"><b>'+(window.BOOKS_COUNT||6633).toLocaleString()+'</b><span>isidore.co books searchable</span></div><div class="stat"><b>'+D.isidore.length.toLocaleString()+'</b><span>isidore.co author folders indexed</span></div></div></section>';
  h+=(function(){var L=window.LIBRARY_DATA,W=L?L.works.filter(function(w){return w.editions.some(function(e){return e.text})}):[];if(!W.length)return '';var pick=['confessions','imitation-of-christ','story-of-a-soul','orthodoxy','apologia','divine-comedy','life-of-teresa','lord-world'].map(function(id){return W.find(function(w){return w.id===id})}).filter(Boolean);
  return '<section class="reading-home"><div><div class="eyebrow">Tolle, lege · the reading room</div><h2>A place to begin</h2><p>'+W.length+' classics in clean, source-checked editions you can read right in your browser, with adjustable text, dark mode, contents, search, and your place saved.</p><a class="btn" href="#/library">Find your next read →</a></div><ul class="rh-list">'+pick.map(function(w){var e=w.editions.find(function(x){return x.text});return '<li><a href="#/read/'+w.id+'/'+e.id+'"><b>'+esc(w.title)+'</b><span>'+esc(w.author)+'</span></a></li>'}).join('')+'</ul></section>'})();
  h+='<section class="flagship fs-secondary"><div class="fs-main"><div class="eyebrow">Other formats · EPUB &amp; PDF</div><h2>The Isidore Index</h2><p>'+(window.BOOKS_COUNT||6633).toLocaleString()+' books from the St. Isidore e-book library, catalogued in '+(window.BOOKS_LANGS||22)+' languages, with filters for era, format, and subject, and a detail page for every book with downloads from isidore.co.</p>'+
   '<form class="hero-search fs-search" onsubmit="location.hash=\'#/isidore/\'+encodeURIComponent(this.q.value);return false"><input name="q" placeholder="Search the Index: “Garrigou-Lagrange”, “De Trinitate”, “catechism”…" aria-label="Search the Isidore Index"><button class="btn">Search</button></form></div>'+
   '<div class="fs-links"><span class="fs-l">Browse</span>'+[['English','lang=eng'],['Latin','lang=lat'],['French','lang=fra'],['Ancient Greek','lang=grc'],['Church Fathers (325–500)','era=post-nicene'],['High Middle Ages','era=scholastic'],['Nineteenth Century','era=19th-century'],['Twentieth Century','era=20th-century'],['EPUB','fmt=EPUB'],['DJVU','fmt=DJVU']].map(function(x){return '<a class="chip" href="#/isidore/'+x[1]+'">'+x[0]+'</a>'}).join('')+'<a class="chip gold" href="#/isidore/folders">Author folders A–Z</a></div></section>';
  h+=dailyPanel();
  h+='<div class="rule"></div><div class="page-head"><div class="eyebrow">Explore</div><h2>The sections of the library</h2></div><div class="grid g-sections">'+
  '<a class="sec-card" href="#/authors"><span class="count">'+A.length+'</span><div class="glyph">A</div><h3>Authors</h3><p>Fathers, Doctors, scholastics, mystics, saints, popes, theologians, apologists, novelists, and poets.</p></a>'+
  '<a class="sec-card" href="#/timeline"><span class="count">I–XXI</span><div class="glyph">T</div><h3>Timeline</h3><p>Every author placed by century, from Clement of Rome to Pope Leo XIV.</p></a>'+
  '<a class="sec-card" href="#/doctors"><span class="count">'+docs.length+'</span><div class="glyph">D</div><h3>Doctors of the Church</h3><p>The '+docs.length+' saints whose teaching the Church holds up as eminent.</p></a>';
  Object.keys(SECTIONS).forEach(function(k){var s=SECTIONS[k];h+='<a class="sec-card" href="#/'+k+'"><span class="count">'+cnt[k]+'</span><div class="glyph">'+s.g+'</div><h3>'+esc(s.t)+'</h3><p>'+esc(s.d)+'</p></a>'});
  h+='<a class="sec-card" href="#/isidore"><span class="count">'+(window.BOOKS_COUNT||6633).toLocaleString()+'</span><div class="glyph">B</div><h3>The Isidore Index</h3><p>Every title in the isidore.co Calibre library, searchable by title, author, series, and subject.</p></a>';
  h+='<a class="sec-card" href="#/editions"><span class="count">60+</span><div class="glyph">E</div><h3>Editions &amp; Translations</h3><p>The best translation and edition of each Catholic classic, with free texts and where to buy.</p></a>';
  h+='<a class="sec-card" href="#/reading"><span class="count">10</span><div class="glyph">❦</div><h3>Reading Lists</h3><p>Start Here, Apologetics, Spiritual Classics, a Waugh starter, the Chesterton shelf, and more.</p></a>';
  h+='<a class="sec-card" href="#/substacks"><span class="count">30+</span><div class="glyph">S</div><h3>Catholic Substacks</h3><p>The best Catholic writers and newsletters, with our featured Chesterton column.</p></a>';
  h+='<a class="sec-card" href="#/rare"><span class="count">122</span><div class="glyph">❧</div><h3>Rare &amp; Obscure</h3><p>Forgotten recusant tracts, Baroque scholastics, incunabula, and old periodicals in the digital archives.</p></a>';
  h+='<a class="sec-card" href="#/projects"><span class="count">70+</span><div class="glyph">P</div><h3>Projects &amp; Translations</h3><p>New Catholic translations, datasets, apps, and open libraries, with AI-assisted work clearly labeled.</p></a>';
  h+='<a class="sec-card" href="#/isidore/folders"><span class="count">'+D.isidore.length.toLocaleString()+'</span><div class="glyph">I</div><h3>Isidore author folders</h3><p>A readable A–Z of every author folder in the isidore.co Calibre library.</p></a>'+
  '<a class="sec-card sec-support" href="#/support"><span class="count">♥</span><div class="glyph">✠</div><h3>Support the Library</h3><p>Free for everyone. Donations by Buy Me a Coffee or PayPal cover hosting and curation.</p></a>'+
  '</div>';
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
/* ---------- v6: tabbed author profile ---------- */
var AUTABS=[['works','Works'],['commentaries','Commentaries'],['buy','Buy the Books'],['related','Related']];
var CUR_AU=null;
function auResolve(id){if(AID[id])return AID[id];var c=A.filter(function(a){return a.id.slice(-id.length-1)==='-'+id||a.id.split('-').indexOf(id)>=0&&a.id.split('-').pop()===id});return c.length===1?c[0]:null}
function auTabGet(){try{return localStorage.getItem('bc-au-tab')||''}catch(e){return ''}}
function auTabSet(t){try{localStorage.setItem('bc-au-tab',t)}catch(e){}}
function auLinkList(L){return '<ul class="linklist">'+L.map(function(l){return '<li><a href="'+esc(l.u)+'"'+(l.int?'':' target="_blank" rel="noopener"')+'><span class="k '+(l.k||'read')+'">'+esc(l.kl||l.k||'read')+'</span>'+esc(l.t)+(l.int?'':' ↗')+(l.n?'<span class="ll-n">'+esc(l.n)+'</span>':'')+'</a></li>'}).join('')+'</ul>'}
function auNames(ids){return ids.filter(function(i){return AID[i]}).map(function(i){return '<a href="#/author/'+i+'">'+esc(AID[i].name)+'</a>'}).join('')}
function author(id,tab){
  var a=auResolve(id);if(!a)return notfound();
  if(a.id!==id){location.replace('#/author/'+a.id+(tab?'/'+tab:''));return}
  if(CUR_AU&&CUR_AU.id===a.id&&$('#au-tabs')){auShow(tab||CUR_AU.tab);return}
  var X={};var site=a.links.filter(function(l){return l.kind==='site'}),wiki=a.links.filter(function(l){return /wikipedia\.org/.test(l.url)})[0];
  var key=[];if(wiki)key.push(['Wikipedia',wiki.url]);if(a.qid)key.push(['Wikidata '+a.qid,'https://www.wikidata.org/wiki/'+a.qid]);else if(a.qidWork)key.push(['Wikidata '+a.qidWork,'https://www.wikidata.org/wiki/'+a.qidWork]);
  site.slice(0,2).forEach(function(l){key.push([l.label,l.url])});
  var h='<a class="backlink" href="#/authors">← All authors</a><article class="au-page"><header class="au-head"><div class="detail-head">'+avatar(a)+'<div><div class="eyebrow">'+esc(ERA[a.era].label)+(a.century?' · '+ord(a.century)+' century':'')+'</div><h1>'+esc(a.name)+'</h1><div class="dates">'+esc(dates(a))+'</div><div id="au-feast" class="au-feast"></div>'+badges(a,8)+'</div></div>'+
   '<p class="summary dropcap">'+esc(a.desc)+'</p>'+(a.extract?'<div class="extract"><p>'+esc(a.extract)+(a.extract.length>=595?'…':'')+'</p><p class="small">Summary from Wikipedia'+(a.wikiDesc?': “'+esc(a.wikiDesc)+'”':'')+'.</p></div>':'')+
   '<div class="au-key" id="au-key">'+key.map(function(k){return '<a class="chip" href="'+esc(k[1])+'" target="_blank" rel="noopener">'+esc(k[0])+' ↗</a>'}).join('')+'</div></header>'+
   '<nav class="au-tabs" id="au-tabs" role="tablist" aria-label="Sections">'+AUTABS.map(function(t){return '<a role="tab" href="#/author/'+a.id+'/'+t[0]+'" data-t="'+t[0]+'" id="tab-'+t[0]+'">'+t[1]+' <span class="tc">…</span></a>'}).join('')+'</nav>'+
   AUTABS.map(function(t){return '<section class="au-panel" role="tabpanel" id="tp-'+t[0]+'" aria-labelledby="tab-'+t[0]+'" hidden></section>'}).join('')+'</article>';
  render(h,'authors');document.title=a.name+' — Bibliotheca Catholica';
  CUR_AU={id:a.id,a:a,tab:'',n:{},ready:{}};
  var T=$('#au-tabs');T.addEventListener('click',function(e){var l=e.target.closest('a[data-t]');if(!l)return;e.preventDefault();var t=l.dataset.t;history.pushState(null,'','#/author/'+a.id+'/'+t);auShow(t,true)});
  auSticky();
  var want=tab||auTabGet()||'works';CUR_AU.want=want;auShow(want);
  // data
  var pend=4;function step(){if(--pend===0)auBuild()}
  loadBooks(function(){step()});loadGuide(function(){step()});lazy('authorx.js','AUTHORX',function(){step()});
  if(a.doctor)lazy('doctors.js','DOCTORS_DATA',function(){step()});else step();
}
function auSticky(){var tb=document.querySelector('.topbar');var T=$('#au-tabs');if(!tb||!T)return;T.style.top=(tb.getBoundingClientRect().height-1)+'px'}
window.addEventListener('resize',function(){if($('#au-tabs'))auSticky()});
function auShow(t,user){var C=CUR_AU;if(!C)return;var ok=AUTABS.map(function(x){return x[0]});if(ok.indexOf(t)<0)t='works';
  var el=$('#tab-'+t);if(el&&el.hidden&&C.built){t='works';if($('#tab-works').hidden)t='commentaries'}
  C.tab=t;if(user||C.built)auTabSet(t);
  if(C.built){var hh='#/author/'+C.id+'/'+t;var cur=location.hash;if(/^#\/author\/[^/]+\/./.test(cur)&&cur!==hh)history.replaceState(null,'',hh)}
  document.querySelectorAll('#au-tabs a').forEach(function(x){var on=x.dataset.t===t;x.classList.toggle('on',on);x.setAttribute('aria-selected',on?'true':'false')});
  document.querySelectorAll('.au-panel').forEach(function(p){p.hidden=p.id!=='tp-'+t});
  if(user){var T=$('#au-tabs');var y=T.getBoundingClientRect().top;var top=parseFloat(T.style.top)||0;if(y<top+2)window.scrollTo(0,T.offsetTop-top+1)
    var on=document.querySelector('#au-tabs a.on');if(on&&on.scrollIntoView)on.scrollIntoView({block:'nearest',inline:'nearest'})}
  document.title=C.a.name+(t!=='works'?' · '+AUTABS.filter(function(x){return x[0]===t})[0][1]:'')+' — Bibliotheca Catholica'}
function auCount(t,n,keep){var C=CUR_AU;C.n[t]=n;var el=$('#tab-'+t);if(!el)return;el.querySelector('.tc').textContent=n?n.toLocaleString():'0';el.hidden=!n&&!keep;el.classList.toggle('empty',!n)}
function auBuild(){var C=CUR_AU;if(!C||!$('#au-tabs'))return;var a=C.a;var X=((window.AUTHORX||{}).by||{})[a.id]||{};C.X=X;
  var DR=a.doctor&&window.DOCTORS_DATA?window.DOCTORS_DATA.doctors[a.id]:null;
  // feast
  var fe=DR?[DR.feast]:(X.feast||[]);if(fe.length)$('#au-feast').innerHTML='<span class="k">Feast</span> '+esc(fe.join(' · '))+(DR?'':' <span class="small muted" title="From Wikidata; calendars differ">(Wikidata'+(fe.length>1?'; calendars differ':'')+')</span>');
  if(X.ce){var k=$('#au-key');if(k&&!/cathen/.test(k.innerHTML))k.insertAdjacentHTML('beforeend','<a class="chip" href="'+esc(X.ce)+'" target="_blank" rel="noopener">Catholic Encyclopedia ↗</a>')}
  auWorks(a,X,DR);auComm(a,X,DR);auBuy(a);auRel(a,X);
  C.built=true;var want=C.want;var el=$('#tab-'+want);if(!el||el.hidden){want=['works','commentaries'].filter(function(t){return !$('#tab-'+t).hidden})[0]}auShow(want)}
function auWorks(a,X,DR){var p=$('#tp-works'),n=window.LIBRARY_DATA.works.filter(function(w){return w.authorId===a.id}).length,h=window.BCLibrary.authorWorks(a.id);
  if(DR){h+='<div id="au-free"></div>';n+=DR.works.length}
  if(a.works.length){n+=a.works.length;h+='<h3>Works to read online (New Advent)</h3><ul class="works">'+a.works.map(function(w){return '<li><a href="'+esc(w.url)+'" target="_blank" rel="noopener">'+esc(w.title)+'</a></li>'}).join('')+'</ul>'}
  var rd=a.links.filter(function(l){return l.kind==='read'}).map(function(l){return {k:'read',t:l.label,u:l.url}});
  if(X.ws)rd.push({k:'read',t:'Author page on Wikisource',u:X.ws});
  var more=a.links.filter(function(l){return l.kind==='search'}).map(function(l){return {k:'search',t:l.label,u:l.url}});
  if(X.wq)more.push({k:'about',kl:'quotes',t:'Quotations on Wikiquote',u:X.wq});
  if(a.qid)more.push({k:'about',kl:'data',t:'Wikidata item '+a.qid,u:'https://www.wikidata.org/wiki/'+a.qid});
  n+=rd.length;
  if(rd.length)h+='<h3>Read free online</h3>'+auLinkList(rd);
  if(X.own){n+=X.own.length;h+='<h3>Writing &amp; media by '+esc(a.name)+'</h3>'+auLinkList(X.own.map(function(o){return {k:o.k==='substack'?'read':'site',kl:o.k,t:o.t,u:o.u,n:o.n}}))}
  var L=(B&&B.by[a.id]||[]).slice().sort(function(x,y){return x.tn.localeCompare(y.tn)});n+=L.length;
  if(L.length){var fm={};L.forEach(function(b){b.f.forEach(function(f){fm[f]=(fm[f]||0)+1})});var fk=Object.keys(fm).sort(function(x,y){return fm[y]-fm[x]});
    h+='<div class="rule"></div><h3>Books in the Isidore Index <span class="small">('+L.length+')</span></h3><div class="chips au-fmt" id="au-fmt"><button class="chip on" data-f="">All '+L.length+'</button>'+fk.map(function(f){return '<button class="chip" data-f="'+esc(f)+'">'+esc(f)+' '+fm[f]+'</button>'}).join('')+'</div><div class="blist compact" id="au-bl"></div><div id="au-blm"></div>'}
  if(more.length)h+='<h3>Search &amp; data</h3>'+auLinkList(more);
  p.innerHTML=h||'<div class="empty">No free texts are linked yet.</div>';auCount('works',n);
  if(DR)readFree(a);
  if(L.length){var cur='',lim=40;function draw(){var M=cur?L.filter(function(b){return b.f.indexOf(cur)>=0}):L;$('#au-bl').innerHTML=M.slice(0,lim).map(function(b){return brow(b)}).join('');
      $('#au-blm').innerHTML=M.length>lim?'<button class="btn ghost" id="au-more">Show all '+M.length+'</button>':''}
    draw();$('#au-fmt').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;cur=b.dataset.f;lim=40;$('#au-fmt').querySelectorAll('.chip').forEach(function(x){x.classList.toggle('on',x===b)});draw()});
    p.addEventListener('click',function(e){if(e.target.id==='au-more'){lim=1e9;draw()}var t=e.target.closest('.b-tag');if(t){bfReset();BF.tag=t.dataset.tag;location.hash='#/isidore'}})}}
var WOF={k:'podcast',t:'Way of the Fathers (Catholic Culture podcast)',u:'https://www.catholicculture.org/commentary/category/way-fathers/',n:'A podcast on the Fathers and Doctors of the Church.'};
function auComm(a,X,DR){var p=$('#tp-commentaries'),n=0,h='';var cm=(X.comm||[]).slice();
  var feat=cm.filter(function(c){return c.feat});cm=cm.filter(function(c){return !c.feat});
  if(feat.length){n+=feat.length;h+=feat.map(function(c){return '<a class="au-feat" href="'+esc(c.u)+'" target="_blank" rel="noopener"><span class="eyebrow">Featured column</span><b>'+esc(c.t)+' ↗</b><span>'+esc(c.n)+'</span></a>'}).join('')}
  if(a.doctor||/apostolic|ante-nicene|post-nicene|desert/.test(a.era))cm.push(WOF);
  if(cm.length){n+=cm.length;h+='<h3>Commentary, podcasts &amp; Substacks</h3>'+auLinkList(cm.map(function(c){return {k:c.k==='substack'?'read':(c.k==='society'?'site':'about'),kl:c.k,t:c.t,u:c.u,n:c.n}}))}
  if(X.studies){n+=X.studies.length;h+='<h3>Studies &amp; biographies by authors in our library</h3>'+auLinkList(X.studies.filter(function(s){return AID[s[0]]}).map(function(s){return {k:'read',kl:'study',t:AID[s[0]].name+', '+s[1],u:'#/author/'+s[0],int:1}}))}
  var ref=[];if(X.ce)ref.push({k:'about',kl:'1913',t:'Catholic Encyclopedia article',u:X.ce,n:'The 1913 Catholic Encyclopedia at New Advent.'});
  if(X.sep)ref.push({k:'about',kl:'SEP',t:'Stanford Encyclopedia of Philosophy',u:X.sep});if(X.iep)ref.push({k:'about',kl:'IEP',t:'Internet Encyclopedia of Philosophy',u:X.iep});
  var wiki=a.links.filter(function(l){return /wikipedia\.org/.test(l.url)})[0];if(wiki)ref.push({k:'about',kl:'bio',t:'Biography on Wikipedia',u:wiki.url});
  a.links.filter(function(l){return l.kind==='about'&&!/wikipedia|cathen/.test(l.url)}).forEach(function(l){ref.push({k:'about',t:l.label,u:l.url})});
  if(ref.length){n+=ref.length;h+='<h3>Reference articles</h3>'+auLinkList(ref)}
  var ab=(X.about||[]).map(function(i){return B&&B.ids[i]}).filter(Boolean);
  if(ab.length){n+=ab.length;h+='<div class="rule"></div><h3>Books about '+esc(a.name)+' in the Isidore Index <span class="small">('+ab.length+')</span></h3><div class="blist compact">'+ab.slice(0,30).map(function(b){return brow(b)}).join('')+'</div>'}
  var mail='mailto:micahwatson@bibliothecacatholica.com?subject='+encodeURIComponent('Commentary on '+a.name);
  h+=(n?'<div class="au-cta small-cta">':'<div class="au-cta"><h3>Commentaries coming soon.</h3>')+'<p>'+(n?'Want to write about '+esc(a.name)+'? ':'Want to write one? ')+'We are looking for writers to contribute original commentary on '+esc(a.name)+(n?'.':', from short introductions to close readings.')+'</p><a class="btn'+(n?' ghost':'')+'" href="'+mail+'">Write a commentary ✉</a></div>';
  p.innerHTML=h;auCount('commentaries',n,true)}
function auBuy(a){var p=$('#tp-buy');var L=GD?GD.editions.filter(function(w){return w.aid===a.id}):[];
  if(!L.length){p.innerHTML='';auCount('buy',0);return}
  p.innerHTML='<p class="lede small">Our recommended translations and editions of '+esc(a.name)+', with verified ISBNs where we could confirm them. See the full <a href="#/editions">Editions &amp; Translations</a> guide.</p><div class="ed-list">'+L.map(edCard).join('')+'</div><p class="au-buy-more"><a class="btn ghost" href="'+esc(bookshopUrl('',a.name))+'" target="_blank" rel="noopener sponsored">More by '+esc(a.name)+' on Bookshop.org ↗</a>'+(AFF.bookshopShop?'<a class="btn ghost" href="'+esc(AFF.bookshopShop)+'" target="_blank" rel="noopener sponsored">Our Bookshop.org shop ↗</a>':'')+'</p>'+discl();
  auCount('buy',L.reduce(function(n,w){return n+w.picks.length},0))}
function auRel(a,X){var p=$('#tp-related'),n=0,h='';
  function grp(t,ids){ids=(ids||[]).filter(function(i){return AID[i]&&i!==a.id});if(!ids.length)return;n+=ids.length;h+='<h3>'+t+'</h3><div class="related">'+auNames(ids)+'</div>'}
  grp('Influenced by',X.infl);grp('Influenced',X.inflOn);grp('Teachers',X.stof);grp('Students',X.stu);
  if(X.wroteOn){n+=X.wroteOn.length;h+='<h3>Wrote about</h3>'+auLinkList(X.wroteOn.filter(function(s){return AID[s[0]]}).map(function(s){return {k:'read',kl:'study',t:AID[s[0]].name+': '+s[1],u:'#/author/'+s[0],int:1}}))}
  var XB=(window.AUTHORX||{}).by||{};
  (X.order||[]).forEach(function(o){var ids=A.filter(function(b){return b.id!==a.id&&((XB[b.id]||{}).order||[]).indexOf(o)>=0}).map(function(b){return b.id});grp('Also '+o+' <span class="small">('+ids.length+')</span>',ids.slice(0,24))});
  var same=A.filter(function(b){return b.era===a.era&&b.id!==a.id}).slice(0,16).map(function(b){return b.id});grp('Also in this era: '+esc(ERA[a.era].label),same);
  if(X.lists){n+=X.lists.length;h+='<h3>On our reading lists</h3>'+auLinkList(X.lists.map(function(l){return {k:'read',kl:'list',t:l[1],u:'#/reading/'+l[0],int:1}}))}
  var lv=$('#au-ed-l');h+='<div id="au-rp"></div>';
  p.innerHTML=h;auCount('related',n+(X.rare||[]).length+(X.proj||[]).length);
  if(X.rare)lazy('rare.js','RARE_DATA',function(R){var box=$('#au-rp');if(!box||!R)return;var M={};R.items.forEach(function(r){M[r.id]=r});var L=X.rare.map(function(i){return M[i]}).filter(Boolean);
    box.insertAdjacentHTML('afterbegin','<h3>Rare &amp; Obscure</h3>'+auLinkList(L.map(function(r){return {k:'read',kl:'rare',t:r.t,u:'#/rare/'+encodeURIComponent(r.id),int:1,n:[r.a,r.lang].filter(Boolean).join(' · ')}})))});
  if(X.proj)lazy('projects.js','PROJECTS_DATA',function(R){var box=$('#au-rp');if(!box||!R)return;var M={};R.items.forEach(function(r){M[r.id]=r});var L=X.proj.map(function(i){return M[i]}).filter(Boolean);
    box.insertAdjacentHTML('beforeend','<h3>Projects &amp; translations</h3>'+auLinkList(L.map(function(r){return {k:'site',kl:'project',t:r.n,u:r.u,n:r.d}})))})}

function timeline(){
  var by={};A.forEach(function(a){if(!a.century)return;(by[a.century]=by[a.century]||[]).push(a)});
  var cs=Object.keys(by).map(Number).sort(function(a,b){return a-b});
  var h='<div class="page-head"><div class="eyebrow">Per saecula</div><h1>Timeline of Catholic Authors</h1><p class="lede">Each author placed in the century of their principal work. Gold-bordered names are Doctors of the Church.</p></div><div class="timeline">';
  cs.forEach(function(c){var L=by[c].sort(function(a,b){return (a.died||a.born+60)-(b.died||b.born+60)});h+='<div class="century"><div class="c-label">'+roman(c)+'<small>'+((c-1)*100)+'–'+(c*100)+'</small></div><div class="c-people">'+L.map(function(a){return '<a class="'+(a.doctor?'doc':'')+'" href="#/author/'+a.id+'" title="'+esc(dates(a)+' — '+a.desc)+'">'+avatar(a,'mini')+esc(a.name)+'</a>'}).join('')+'</div></div>'});
  render(h+'</div>','timeline');
}

/* ---------- v4 lazy data: doctors' free texts, rare works, projects ---------- */
var LZ={};
function lazy(file,gv,cb){var st=LZ[gv]||(LZ[gv]={w:[],l:false,d:null});if(st.d){cb&&cb(st.d);return}if(cb)st.w.push(cb);if(st.l)return;st.l=true;
  function done(){st.d=window[gv]||null;if(st.d&&LZIDX[gv])LZIDX[gv](st.d);st.w.splice(0).forEach(function(f){try{f(st.d)}catch(e){console.warn(e)}})}
  if(window[gv]){setTimeout(done,0);return}var sc=document.createElement('script');sc.src='data/'+file+'?v=20261021-collection-access';sc.onload=done;sc.onerror=done;document.head.appendChild(sc)}
var LZIDX={RARE_DATA:function(R){R.items.forEach(function(r){IDX.push({type:'Rare & Obscure',t:r.t,s:(r.a||'')+(r.d?' · '+r.d:'')+' · '+r.th,h:'#/rare/'+encodeURIComponent(r.id),x:norm(r.t+' '+r.o+' '+r.a+' '+r.th+' '+r.g+' '+r.w+' '+r.lang),w:1.8})})},
  PROJECTS_DATA:function(R){R.items.forEach(function(p){IDX.push({type:'Projects & Translations',t:p.n,s:p.cat+' · '+p.d,h:p.u,ext:1,x:norm(p.n+' '+p.cat+' '+p.d+' '+p.tx+' '+p.lang),w:2})})}};
var PDL={pd:['pd','Public domain'],orig:['pd','PD · original language'],free:['free','Free to read · not PD'],cr:['cr','Copyrighted'],unc:['unc','Rights uncertain']};
function readFree(a){var box=$('#au-free');if(!box)return;lazy('doctors.js','DOCTORS_DATA',function(R){box=$('#au-free');if(!box||!R)return;var d=R.doctors[a.id];if(!d){box.innerHTML='';return}
  var meta='<p class="dr-meta"><b>Feast:</b> '+esc(d.feast)+' · <b>Declared a Doctor:</b> '+esc(d.decl)+' by '+esc(d.by)+'</p>'+(d.feastNote?'<p class="dr-meta">'+esc(d.feastNote)+' <a href="'+esc(d.feastSrc)+'" target="_blank" rel="noopener">Decree ↗</a></p>':'');
  var h='<div class="rule"></div><h3>Read free: key works</h3>'+meta+'<p class="small muted">Every link goes out to the library that holds the text; Bibliotheca Catholica hosts none of them. Rights are judged by the specific edition linked (US public domain = published before 1931).</p><div class="rf">';
  d.works.forEach(function(w){h+='<div class="rf-w"><h4>'+esc(w.t)+'</h4>';if(!w.links.length){h+='<p class="rf-gap">'+esc(w.gap||'No free full text found yet.')+'</p></div>';return}
    if(w.gap)h+='<p class="rf-gap">'+esc(w.gap)+'</p>';
    h+='<ul>'+w.links.map(function(l){var p=PDL[l.pd]||PDL.unc;return '<li><a href="'+esc(l.u)+'" target="_blank" rel="noopener">'+esc(l.s)+' ↗</a><span class="rf-d">'+esc([l.tr,l.y].filter(Boolean).join(', '))+'</span><span class="pdb pdb-'+p[0]+'" title="'+esc(l.pds)+'">'+p[1]+'</span>'+(l.fl?'<span class="rf-fl">'+esc(l.fl)+'</span>':'')+'</li>'}).join('')+'</ul></div>'});
  box.innerHTML=h+'</div>'})}
function rare(focus){
  var h='<div class="page-head"><div class="eyebrow">Thesauri absconditi</div><h1>Rare &amp; Obscure</h1><p class="lede">Forgotten Catholic books in the digital archives: recusant tracts, Baroque scholastics, Counter-Reformation polemic, incunabula, and old periodicals, with new English translations, grouped by theme.</p></div>'+
   '<div class="callout">Almost every item is a pre-1931 scan and in the US public domain; it opens on the Internet Archive. The ten <b>modern community translations</b> carry no license, so we link only to their archive pages. Two items are <b>non-Catholic replies</b>, labeled and kept only for context.</div>'+
   '<div class="toolbar"><input type="search" id="rr-q" placeholder="Filter by title, author, language…"><div class="chips" id="rr-c"></div></div><div id="rr-out"><div class="loading">Loading the collection…</div></div>';
  render(h,'rare');
  lazy('rare.js','RARE_DATA',function(R){if(!$('#rr-out'))return;if(!R){$('#rr-out').innerHTML='<div class="empty">The collection failed to load.</div>';return}
    var cur='',q='';var th=R.themes.filter(function(t){return R.items.some(function(r){return r.th===t})});
    function short(t){return t.replace(' (seed cluster)','').replace('Cornaeus & the Würzburg/Bamberg Jesuit controversialists','Cornaeus & Würzburg Jesuits').replace('19th-c. neo-scholastic revival & critical editions','19th-c. neo-scholastics').replace('Flagged: non-Catholic responses (context only)','Non-Catholic (context)')}
    $('#rr-c').innerHTML='<button class="chip on" data-c="">All '+R.items.length+'</button>'+th.map(function(t){return '<button class="chip" data-c="'+esc(t)+'">'+esc(short(t))+'</button>'}).join('');
    function card(r){var b=r.nonc?'<span class="pdb pdb-cr">Non-Catholic · context only</span>':'';b+=r.notpd?'<span class="pdb pdb-free">Modern translation · not PD · link only</span>':'<span class="pdb pdb-pd">Public domain</span>';if(r.ai)b+='<span class="pdb pdb-unc">AI-assisted translation</span>';
      return '<div class="rare'+(r.nonc?' nonc':'')+'" id="rr-'+esc(r.id)+'"><h3>'+esc(r.t)+'</h3><div class="rare-o">'+esc(r.o.length>140?r.o.slice(0,140)+'…':r.o)+'</div><div class="rare-m">'+esc([r.a,r.d,r.lang].filter(Boolean).join(' · '))+'</div><p>'+esc(r.w)+'</p>'+(r.nonc?'<p class="small muted">'+esc(r.cs)+'</p>':'')+'<div class="rare-b">'+b+'</div><div class="rare-l">'+r.links.map(function(l){return '<a href="'+esc(l[1])+'" target="_blank" rel="noopener">'+esc(l[0])+' ↗</a>'}).join('')+'</div></div>'}
    function draw(){var t=norm(q),out='';th.forEach(function(c){if(cur&&c!==cur)return;var L=R.items.filter(function(r){return r.th===c&&(!t||norm(r.t+' '+r.o+' '+r.a+' '+r.lang+' '+r.w).indexOf(t)>=0)});if(!L.length)return;out+='<div class="cat-title"><h2>'+esc(c)+' <span class="small">('+L.length+')</span></h2></div><div class="rare-grid">'+L.map(card).join('')+'</div>'});$('#rr-out').innerHTML=out||'<div class="empty">Nothing matches.</div>'}
    draw();$('#rr-q').addEventListener('input',function(e){q=e.target.value;draw()});
    $('#rr-c').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;cur=b.dataset.c;document.querySelectorAll('#rr-c .chip').forEach(function(x){x.classList.toggle('on',x===b)});draw()});
    if(focus){var el=document.getElementById('rr-'+focus);if(el){el.classList.add('hl');el.scrollIntoView({block:'center'})}}})}
function projects(){
  var h='<div class="page-head"><div class="eyebrow">Opera in fieri</div><h1>Projects &amp; Translations</h1><p class="lede">The new wave of Catholic digital projects: open translations, datasets and APIs, liturgy apps, Bible tools, and digital libraries.</p></div>'+
   '<div class="callout">Many 2026 translations are <b>AI-assisted</b>, and are labeled so. Scholars urge caution in citing them; for study, prefer the human translations, which are listed first.</div>'+
   '<div class="toolbar"><input type="search" id="pj-q" placeholder="Filter projects…"><div class="chips" id="pj-c"></div></div><div id="pj-out"><div class="loading">Loading projects…</div></div>';
  render(h,'projects');
  lazy('projects.js','PROJECTS_DATA',function(R){if(!$('#pj-out'))return;if(!R){$('#pj-out').innerHTML='<div class="empty">Failed to load.</div>';return}
    var order=['translation','digital library','Bible','liturgy app','dataset/API','tool','other'];var CL={translation:'Translations','digital library':'Digital libraries',Bible:'Bible','liturgy app':'Liturgy apps','dataset/API':'Datasets & APIs',tool:'Tools',other:'Other'};
    var cats=order.filter(function(c){return R.items.some(function(p){return p.cat===c})});var cur='',q='',hum=false;
    $('#pj-c').innerHTML='<button class="chip on" data-c="">All '+R.items.length+'</button>'+cats.map(function(c){return '<button class="chip" data-c="'+esc(c)+'">'+esc(CL[c]||c)+'</button>'}).join('')+'<button class="chip" id="pj-h" type="button">Human translations only</button>';
    function card(p){var b=p.ai==='ai'?'<span class="pdb pdb-unc" title="'+esc(p.ais)+'">AI-assisted</span>':p.ai==='human'?(p.cat==='translation'?'<span class="pdb pdb-pd">Human translation</span>':''):'<span class="pdb pdb-free" title="'+esc(p.ais)+'">AI use unclear</span>';
      return '<div class="proj"><h3><a href="'+esc(p.u)+'" target="_blank" rel="noopener">'+esc(p.n)+' ↗</a></h3><div class="rare-b">'+b+(p.lang?'<span class="pdb">'+esc(p.lang)+'</span>':'')+'</div><p>'+esc(p.d)+'</p>'+
       '<div class="proj-m">'+(p.lic?'<div><b>License:</b> '+esc(p.lic)+'</div>':'')+(p.m&&!/^not (named|stated)/i.test(p.m)?'<div><b>Maintainer:</b> '+esc(p.m)+'</div>':'')+(p.note?'<div><b>Note:</b> '+esc(p.note)+'</div>':'')+(p.st!=='200'?'<div class="muted">Homepage did not answer our automated check ('+esc(p.st)+'); it may still open in a browser.</div>':'')+'</div>'+
       '<div class="rare-l">'+(p.gh?'<a href="'+esc(p.gh)+'" target="_blank" rel="noopener">GitHub'+(p.stars?' ★'+esc(p.stars):'')+' ↗</a>':'')+p.h.map(function(x){return '<a href="https://x.com/'+esc(x.replace('@',''))+'" target="_blank" rel="noopener">'+esc(x)+' ↗</a>'}).join('')+'</div></div>'}
    function ok(p){var t=norm(q);if(hum&&!(p.cat==='translation'&&p.ai==='human'))return false;return !t||norm(p.n+' '+p.d+' '+p.tx+' '+p.lang+' '+p.why).indexOf(t)>=0}
    function draw(){var out='';if(!cur&&!q&&!hum){var S=R.items.filter(function(p){return p.std});out+='<div class="cat-title"><h2>Standouts</h2></div><div class="rare-grid">'+S.map(card).join('')+'</div>'}
      cats.forEach(function(c){if(cur&&c!==cur)return;var L=R.items.filter(function(p){return p.cat===c&&ok(p)&&(cur||q||hum||!p.std)});if(!L.length)return;out+='<div class="cat-title"><h2>'+esc(CL[c]||c)+' <span class="small">('+L.length+')</span></h2></div><div class="rare-grid">'+L.map(card).join('')+'</div>'});$('#pj-out').innerHTML=out||'<div class="empty">Nothing matches.</div>'}
    draw();$('#pj-q').addEventListener('input',function(e){q=e.target.value;draw()});
    $('#pj-c').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;if(b.id==='pj-h'){hum=!hum;b.classList.toggle('on',hum);draw();return}cur=b.dataset.c;document.querySelectorAll('#pj-c .chip').forEach(function(x){if(x.id!=='pj-h')x.classList.toggle('on',x===b)});draw()})})}
function openData(){
  var h='<div class="page-head"><div class="eyebrow">Data aperta</div><h1>Open Data</h1><p class="lede">The Isidore Index, curated authors, editions, Doctors’ free texts, rare works, and projects, as documented JSON and CSV under <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" rel="noopener">CC0</a>. Use them for anything; a link back is appreciated.</p></div>'+
   '<div class="callout">Read the <a href="'+odUrl('data/open/README.md')+'" target="_blank" rel="noopener">README</a> for how each dataset was made and its caveats. CC0 covers our compilation and curation; it does not cover third-party texts reached through the links, and no Wikipedia text is included. The <a href="'+odUrl('data/open/manifest.json')+'" target="_blank" rel="noopener">manifest</a> lists every field.</div><div id="od-out"><div class="loading">Loading…</div></div>';
  h+='<section class="panel"><h2>Selected reading catalog</h2><p>49 work records with edition sources, contributor roles, access labels, and hosted-copy checksums. Rights notices for texts remain separate from catalog metadata.</p><a class="btn ghost" href="data/library.json" download>Download catalog JSON</a> · <a href="docs/CATALOG.md" target="_blank" rel="noopener">Sources &amp; editorial notes</a></section>';
  render(h,'data');
  lazy('open.js','OPEN_MANIFEST',function(M){if(!$('#od-out'))return;if(!M){$('#od-out').innerHTML='<div class="empty">Manifest failed to load.</div>';return}
    $('#od-out').innerHTML='<div class="od-grid">'+M.datasets.map(function(d){var f=Object.keys(d.fields);return '<div class="od"><h3>'+esc(d.name)+' <span class="small muted">'+d.count.toLocaleString()+' records</span></h3><p>'+esc(d.description)+'</p><div class="dl-row"><a class="btn gold" href="'+odUrl(d.json)+'" download>JSON ↓</a><a class="btn ghost" href="'+odUrl(d.csv)+'" download>CSV ↓</a></div><details><summary>'+f.length+' fields</summary><dl class="od-f">'+f.map(function(k){return '<dt>'+esc(k)+'</dt><dd>'+esc(d.fields[k])+'</dd>'}).join('')+'</dl></details></div>'}).join('')+'</div><p class="small muted">Generated '+esc(M.generated)+'.</p>'})}
function odUrl(p){return (location.protocol==='file:'?'https://bibliothecacatholica.com/':'')+p}
function season(d){d=d||new Date();var y=d.getFullYear();function easter(Y){var a=Y%19,b=Math.floor(Y/100),c=Y%100,dd=Math.floor(b/4),e=b%4,f=Math.floor((b+8)/25),g=Math.floor((b-f+1)/3),h=(19*a+b-dd-g+15)%30,i=Math.floor(c/4),k=c%4,l=(32+2*e+2*i-h-k)%7,m=Math.floor((a+11*h+22*l)/451),mo=Math.floor((h+l-7*m+114)/31),da=((h+l-7*m+114)%31)+1;return new Date(Y,mo-1,da)}
  function add(x,n){var r=new Date(x);r.setDate(r.getDate()+n);return r}var t=new Date(y,d.getMonth(),d.getDate());
  var E=easter(y),ash=add(E,-46),holyThu=add(E,-3),pent=add(E,49);var xmas=new Date(y,11,25),adv=add(xmas,-((xmas.getDay()||7)+21));
  var ep=new Date(y,0,6),bapt=add(ep,7-ep.getDay());
  if(t>=adv&&t<xmas)return {n:'Advent',c:'violet'};if(t>=xmas||t<=bapt)return {n:'Christmas',c:'white'};
  if(t>=ash&&t<holyThu)return {n:'Lent',c:'violet'};if(t>=holyThu&&t<E)return {n:'the Sacred Triduum',c:'red'};
  if(t>=E&&t<=pent)return {n:'Eastertide',c:'white'};return {n:'Ordinary Time',c:'green'}}
function dailyPanel(){var d=new Date(),s=season(d);var ds=d.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',year:'numeric'});
  var L=[['Today’s Mass readings','USCCB','https://bible.usccb.org/daily-bible-reading'],['Readings & Liturgy of the Hours','Universalis','https://universalis.com/'],['The Divine Office, with audio','divineoffice.org','https://divineoffice.org/'],['Saint of the day','Franciscan Media','https://www.franciscanmedia.org/saint-of-the-day/'],['Word of the day','Vatican News','https://www.vaticannews.va/en/word-of-the-day.html'],['Liturgical calendar','GCatholic','https://gcatholic.org/calendar/'],['This day in the liturgical year','Catholic Culture','https://www.catholicculture.org/culture/liturgicalyear/calendar/day.cfm?date='+d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)]];
  return '<section class="daily"><div class="daily-head"><div><div class="eyebrow">Hodie · today</div><h2>'+esc(ds)+'</h2><p class="season"><span class="sw sw-'+s.c+'"></span>'+esc(s.n)+'</p></div><a class="btn ghost" href="#/prayers">Prayers &amp; devotions →</a></div><div class="daily-grid">'+L.map(function(x){return '<a href="'+x[2]+'" target="_blank" rel="noopener"><b>'+esc(x[0])+' ↗</b><span>'+esc(x[1])+'</span></a>'}).join('')+'</div></section>'}
function prayerText(t){return esc(t).split('\n').map(function(l){return '<p>'+l.replace(/^(V\.|R\.)/,'<b class="vr">$1</b>')+'</p>'}).join('')}
function prayersBlock(){if(!PR)return '';var dow=new Date().getDay();var today={1:0,6:0,4:1,2:2,5:2,3:3,0:3}[dow];
  var h='<div class="callout">'+esc(PR.note)+' Tap a prayer to open it; tap <b>Latin</b> to see the Latin text.</div><div class="pr-wrap">';
  PR.groups.forEach(function(g){h+='<div class="cat-title"><h2>'+esc(g.t)+'</h2></div><div class="pr-list">'+g.items.map(function(p){return '<details class="prayer" id="pr-'+p.id+'"><summary>'+esc(p.t)+'</summary><div class="pr-body"><div class="pr-en">'+prayerText(p.en)+'</div>'+(p.la?'<div class="pr-la" hidden lang="la">'+prayerText(p.la)+'</div>':'')+(p.note?'<p class="pr-note">'+esc(p.note)+'</p>':'')+'<div class="pr-tools">'+(p.la?'<button class="chip pr-lat" type="button">Latin</button>':'')+'<a class="chip" href="#/prayers/'+p.id+'">Link</a></div></div></details>'}).join('')+'</div>'});
  var R=PR.rosary;h+='<div class="cat-title"><h2>The Holy Rosary</h2></div><div class="rosary"><ol class="ro-how">'+R.how.map(function(x){return '<li>'+esc(x)+'</li>'}).join('')+'</ol><div class="ro-sets">'+R.sets.map(function(s,i){return '<div class="ro-set'+(i===today?' today':'')+'"><h3>'+esc(s.t)+'</h3><div class="ro-d">'+esc(s.d)+(i===today?' · <b>today</b>':'')+'</div><ol>'+s.m.map(function(m){return '<li>'+esc(m)+'</li>'}).join('')+'</ol></div>'}).join('')+'</div></div></div>';
  return h}
function prayersWire(focus){document.querySelectorAll('.pr-lat').forEach(function(b){b.addEventListener('click',function(){var d=b.closest('.pr-body');var la=$('.pr-la',d),en=$('.pr-en',d);var on=la.hidden;la.hidden=!on;en.hidden=on;b.classList.toggle('on',on);b.textContent=on?'English':'Latin'})});
  if(focus){var el=document.getElementById('pr-'+focus);if(el){el.open=true;setTimeout(function(){el.scrollIntoView({block:'center'})},30)}}}
function section(k,focus){
  var s=SECTIONS[k];var R=D.resources.filter(function(r){return r.section===k});var cats=[];R.forEach(function(r){if(cats.indexOf(r.category)<0)cats.push(r.category)});
  var h='<div class="page-head"><div class="eyebrow">'+esc(s.e)+'</div><h1>'+esc(s.t)+'</h1><p class="lede">'+esc(s.d)+'</p></div>';
  if(k==='magisterium')h+='<p><a class="btn" href="#/library/Magisterium">Read individual Church documents →</a></p>';
  if(k==='magisterium')h+='<div class="callout">For the authoritative text of any papal or curial document, <a href="https://www.vatican.va/content/vatican/en.html" target="_blank" rel="noopener">vatican.va</a> is always the primary source; the other links here are convenient mirrors and finding aids.</div>';
  if(k==='prayers')h+=prayersBlock();
  if(k==='libraries')h+='<div class="callout">This hub is built to complement the <a href="https://isidore.co/calibre" target="_blank" rel="noopener">St. Isidore e-book library</a>. Browse its authors in a readable A–Z on the <a href="#/isidore">Isidore Index</a> page. For forgotten scans, see <a href="#/rare">Rare &amp; Obscure</a>; for new translation efforts, see <a href="#/projects">Projects &amp; Translations</a>.</div>';
  h+='<div class="toolbar"><input type="search" id="rs-q" placeholder="Filter '+esc(s.t)+'…"><div class="chips" id="rs-c"><button class="chip on" data-c="">All</button>'+cats.map(function(c){return '<button class="chip" data-c="'+esc(c)+'">'+esc(c)+'</button>'}).join('')+'</div></div><div id="rs-out"></div>';
  render(h,k);var cur='',q='';
  function draw(){var out='';cats.forEach(function(c){if(cur&&c!==cur)return;var L=R.filter(function(r){return r.category===c&&(!q||norm(r.name+' '+r.desc+' '+r.tags.join(' ')).indexOf(norm(q))>=0)});if(!L.length)return;out+='<div class="cat-title"><h2>'+esc(c)+'</h2></div><div class="grid g-res">'+L.map(rcard).join('')+'</div>'});$('#rs-out').innerHTML=out||'<div class="empty">Nothing matches.</div>'}
  draw();$('#rs-q').addEventListener('input',function(e){q=e.target.value;draw()});
  if(k==='prayers')prayersWire(focus);
  $('#rs-c').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;cur=b.dataset.c;document.querySelectorAll('#rs-c .chip').forEach(function(x){x.classList.toggle('on',x===b)});draw()});
}
function isidore(){
  var h='<div class="page-head"><div class="eyebrow">Index Isidorianus</div><h1>The Isidore Index: author folders</h1><p class="lede">Every author folder in the <a href="https://isidore.co/CalibreLibrary/" target="_blank" rel="noopener">St. Isidore Calibre library</a> ('+D.isidore.length.toLocaleString()+' entries), presented as a readable index. Each name opens that author’s folder of e-books on isidore.co.</p><div class="isx-tabs"><a href="#/isidore">Books</a><a class="on" href="#/isidore/folders">Author folders A–Z ('+D.isidore.length.toLocaleString()+')</a></div></div>'+
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
  var requestedHash=location.hash;
  if(!GD){loadGuide(function(){if(location.hash===requestedHash)results(q)})}
  if(searchScope!=='curated'&&!B){loadBooks(function(){if(location.hash===requestedHash)results(q)})}
  [['rare.js','RARE_DATA'],['projects.js','PROJECTS_DATA']].forEach(function(x){if(!(LZ[x[1]]&&LZ[x[1]].d))lazy(x[0],x[1],function(){if(location.hash===requestedHash)results(q)})});
  var R=search(q,1200);var groups={};R.forEach(function(e){(groups[e.type]=groups[e.type]||[]).push(e)});
  var order=['Selected work','Author','Prayer','Edition guide','Reading list','Work','Substack','Sacred Scripture','Magisterium','Prayers & Devotions','References','Podcasts & Media','Libraries & Institutions','Rare & Obscure','Projects & Translations','Book','isidore.co folder'];
  var h='<div class="page-head"><div class="eyebrow">Quaerite et invenietis</div><h1>Results for “'+esc(q)+'”</h1><p class="result-meta">'+R.length+(R.length>=1200?'+':'')+' matches in '+(searchScope==='curated'?'the selected library':searchScope==='isidore'?'the imported Isidore index':'all collections')+(searchScope!=='curated'&&!B?' (loading books…)':'')+' · <a href="https://isidore.co/calibre/mobile?search='+encodeURIComponent(q)+'&num=25" target="_blank" rel="noopener">Search isidore.co’s full catalog for “'+esc(q)+'” ↗</a> · <a href="https://www.vatican.va/content/vatican/en/search.html?q='+encodeURIComponent(q)+'" target="_blank" rel="noopener">Search vatican.va ↗</a></p></div>';
  h+='<p class="callout">Search in: <a href="#/search/'+encodeURIComponent(q)+'?scope=all"'+(searchScope==='all'?' aria-current="true"':'')+'>Everything</a> · <a href="#/search/'+encodeURIComponent(q)+'?scope=curated"'+(searchScope==='curated'?' aria-current="true"':'')+'>Selected library only</a> · <a href="#/search/'+encodeURIComponent(q)+'?scope=isidore"'+(searchScope==='isidore'?' aria-current="true"':'')+'>Isidore Index only</a>. Imported records are unreviewed external listings, not recommendations.</p>';
  if(!R.length)h+='<div class="empty">Nothing found here. Try the external searches above.</div>';
  order.forEach(function(g){var L=groups[g];if(!L)return;h+='<section class="sr-group"><div class="cat-title"><h2>'+esc(g==='Author'?'Authors':g==='Work'?'Works':g==='isidore.co folder'?'isidore.co library folders':g==='Book'?'Books in the isidore.co catalog':g)+' <span class="small">('+L.length+')</span></h2>'+(g==='Book'?'<a class="cat-more" href="#/isidore/'+encodeURIComponent(q)+'">Browse all in the Isidore Index →</a>':'')+'</div>'+L.slice(0,g==='isidore.co folder'?40:g==='Book'?30:60).map(function(e){return '<a class="sr-item" href="'+esc(e.h)+'"'+(e.ext?' target="_blank" rel="noopener"':'')+'><small>'+esc(e.type)+(window.BCSearch.imported(e)?' · External catalog · unreviewed':'')+(e.ext?' · '+esc(host(e.h))+' ↗':'')+'</small><br><b>'+hl(e.t,q)+'</b><span>'+hl(e.s.slice(0,220),q)+'</span></a>'}).join('')+'</section>'});
  render(h,'');document.title='Search: '+q+' — Bibliotheca Catholica';$('#q').value=q;
}
function notfound(){render('<div class="empty"><h2>Not found</h2><p><a href="#/">Return home</a></p></div>','')}
/* ---------- v7: Support the Library ---------- */
var SUPPORT={bmc:'https://buymeacoffee.com/bibliothecacatholica',paypal:'https://www.paypal.com/donate/?hosted_button_id=D48R9YU7SH43A'};
function support(){var shop=AFF.bookshopShop||'';
  var h='<div class="page-head"><div class="eyebrow">Adiuva bibliothecam</div><h1>Support the Library</h1><p class="lede">Bibliotheca Catholica is free for everyone, with no ads and no paywall. Donations cover hosting and the hours of curation behind every author page, edition, and link.</p></div>'+
   '<div class="sup-grid">'+
   '<div class="sup-card"><div class="sup-ico" aria-hidden="true">☕</div><h2>Buy Me a Coffee</h2><p>A quick, small gift in a few taps.</p><a class="btn sup-btn" href="'+SUPPORT.bmc+'" target="_blank" rel="noopener">Buy us a coffee ↗</a></div>'+
   '<div class="sup-card"><div class="sup-ico" aria-hidden="true">✠</div><h2>Donate with PayPal</h2><p>Give once, or set up a monthly gift that keeps the library growing.</p><a class="btn sup-btn sup-pp" href="'+SUPPORT.paypal+'" target="_blank" rel="noopener">Donate with PayPal ↗</a><p class="small muted">Choose one-time or monthly on the PayPal page.</p></div>'+
   '</div>'+
   '<h2 class="sup-h">Other ways to help</h2><ul class="sup-list">'+
   (shop?'<li><b>Buy books through our <a href="'+esc(shop)+'" target="_blank" rel="noopener sponsored">Bookshop.org shop ↗</a>.</b> It supports independent bookstores, and the library earns a small commission at no extra cost to you.</li>':'')+
   '<li><b>Write a commentary.</b> We welcome original, human-written commentary on the authors in the library. <a href="mailto:micahwatson@bibliothecacatholica.com?subject=Commentary">Get in touch ✉</a></li>'+
   '<li><b>Report a broken link or an error.</b> <a href="mailto:micahwatson@bibliothecacatholica.com?subject=Correction">Tell us ✉</a>, and we will fix it.</li>'+
   '<li><b>Share the library</b> with a friend, a parish, or a homeschool group.</li></ul>'+
   '<p class="small muted sup-fine">Bibliotheca Catholica is an independent project. Payments are handled by Buy Me a Coffee and PayPal; we never see your card details.</p>'+discl();
  render(h,'support')}
function route(){var raw=location.hash.replace(/^#\/?/,'');if(!raw&&window.BC_BOOT)raw=window.BC_BOOT;var queryAt=raw.indexOf('?');var query=new URLSearchParams(queryAt<0?'':raw.slice(queryAt+1));var path=queryAt<0?raw:raw.slice(0,queryAt);var h;try{h=decodeURIComponent(path)}catch(e){notfound();return}var p=h.split('/');if(p[0]==='search'){searchScope=['curated','isidore','all'].indexOf(query.get('scope'))>=0?query.get('scope'):'all';}
  hideSug();
  switch(p[0]){case 'library':window.BCLibrary.library(render,p[1]);break;case 'work':window.BCLibrary.work(render,p[1]);break;case 'read':window.BCLibrary.read(render,p[1],p[2],p[3],p[4]);break;case 'related':window.BCLibrary.related(render);break;case '':home();break;case 'authors':authors();break;case 'doctors':authors({doctors:true});break;case 'author':author(p[1],p[2]||'');break;case 'timeline':timeline();break;
   case 'scripture':case 'magisterium':case 'references':case 'media':case 'libraries':section(p[0]);break;case 'prayers':section('prayers',p[1]||'');break;case 'rare':rare(p[1]||'');break;case 'projects':projects();break;case 'isidore':if(p[1]==='folders')isidore();else if(p[1]==='book')bookDetail(+p[2]);else books(p.slice(1).join('/'));break;case 'books':location.replace('#/isidore'+(p[1]?'/'+p.slice(1).join('/'):''));break;case 'data':openData();break;case 'support':support();break;case 'policy':policy();break;case 'editions':editions(p[1]||'');break;case 'reading':reading(p[1]||'');break;case 'substacks':substacks();break;case 'search':results(p.slice(1).join('/'));break;default:notfound()}}
window.addEventListener('hashchange',route);
/* ---------- per-route meta (description, canonical, Open Graph, Twitter) ---------- */
var SITE='https://bibliothecacatholica.com/',DEF_DESC=(document.querySelector('meta[name=description]')||{}).content||'';
var STATIC_SECTIONS=['library','related','authors','doctors','timeline','scripture','magisterium','references','media','libraries','prayers','rare','projects','isidore','data','support','editions','reading','substacks','policy'];
function canonicalFor(){var raw=(location.hash.replace(/^#\/?/,'')||window.BC_BOOT||'').split('?')[0],p=raw.split('/').filter(Boolean);
  if(!p.length)return SITE;if(p.length===1&&STATIC_SECTIONS.indexOf(p[0])>=0)return SITE+p[0]+'/';
  if(p.length===2&&/^(author|work|editions)$/.test(p[0])&&/^[a-z0-9-]+$/.test(p[1]))return SITE+p[0]+'/'+p[1]+'/';
  if(p.length===2&&p[0]==='reading'&&/^[a-z0-9-]+$/.test(p[1]))return SITE+'reading/'+p[1]+'/';
  return SITE+'#/'+raw}
function setMeta(sel,attr,val){var m=document.head.querySelector(sel);if(!m){m=document.createElement(sel.indexOf('link')===0?'link':'meta');var k=sel.match(/\[(\w+)=["']?([^"'\]]+)/);m.setAttribute(k[1],k[2]);document.head.appendChild(m)}m.setAttribute(attr,val)}
function updateMeta(){var t=document.title,raw=(location.hash.replace(/^#\/?/,'')||window.BC_BOOT||'').split('?')[0].split('/'),d='';
  var focus=raw[0]==='editions'&&raw[1]?main.querySelector('#ed-'+CSS.escape(raw[1])+' .ed-why'):null;if(focus)d=t.replace(/ — .*$/,'')+': '+focus.textContent.trim();
  if(!d)[].slice.call(main.querySelectorAll('.page-head .lede, .page-head p:not(.small), .detail-main p, main p')).some(function(el){var x=el.textContent.replace(/\s+/g,' ').trim();if(x)d+=(d?' ':'')+x;return d.length>=60});
  if(d.length<40)d=DEF_DESC;if(d.length>200)d=d.slice(0,197).replace(/\s+\S*$/,'')+'…';var u=canonicalFor();
  var bk=raw[0]==='isidore'&&raw[1]==='book'&&efOf(raw[2]);setMeta('meta[name=robots]','content',bk?'noindex,follow':'index,follow');
  setMeta('meta[name=description]','content',d);setMeta('link[rel=canonical]','href',u);setMeta('meta[property="og:title"]','content',t);setMeta('meta[property="og:description"]','content',d);setMeta('meta[property="og:url"]','content',u);setMeta('meta[name="twitter:title"]','content',t);setMeta('meta[name="twitter:description"]','content',d)}
var metaT=null;function queueMeta(){clearTimeout(metaT);metaT=setTimeout(updateMeta,30)}
new MutationObserver(queueMeta).observe(document.querySelector('title'),{childList:true,characterData:true,subtree:true});window.addEventListener('hashchange',queueMeta);

/* ---------- header search with suggestions ---------- */
var qi=$('#q'),sg=$('#suggest'),act=-1;
function hideSug(){sg.hidden=true;act=-1}
function showSug(){var q=qi.value.trim();if(q.length<2){hideSug();return}if(searchScope!=='curated'&&!B)loadBooks(function(e){if(!e&&document.activeElement===qi)showSug()});if(!GD)loadGuide(function(e){if(!e&&document.activeElement===qi)showSug()});var R=search(q,60);var by={},order=[];R.forEach(function(e){if(!by[e.type]){by[e.type]=[];order.push(e.type)}if(by[e.type].length<(e.type==='Author'?6:e.type==='Book'?5:3))by[e.type].push(e)});
  var rk=function(t){return t==='Selected work'?0:(t==='Book'||t==='isidore.co folder')?2:1};order.sort(function(x,y){return rk(x)-rk(y)});var html='';order.slice(0,7).forEach(function(t){html+='<div class="sg-h">'+esc(t)+'</div>'+by[t].map(function(e){return '<a role="option" href="'+esc(e.h)+'"'+(e.ext?' target="_blank" rel="noopener"':'')+'><span>'+hl(e.t,q)+(e.ext?' ↗':'')+'</span><small>'+esc(e.s)+'</small></a>'}).join('')});
  html+='<a class="sg-all" href="'+searchHref(q)+'">See all results for “'+esc(q)+'” →</a>';sg.innerHTML=html;sg.hidden=false;act=-1}
qi.addEventListener('input',showSug);qi.addEventListener('focus',showSug);
qi.addEventListener('keydown',function(e){var items=sg.querySelectorAll('a');
  if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(!items.length)return;act=(act+(e.key==='ArrowDown'?1:-1)+items.length)%items.length;items.forEach(function(x,i){x.classList.toggle('active',i===act)});items[act].scrollIntoView({block:'nearest'})}
  else if(e.key==='Enter'){e.preventDefault();if(act>=0&&items[act]){items[act].click()}else if(qi.value.trim()){location.hash=searchHref(qi.value.trim())}hideSug();qi.blur()}
  else if(e.key==='Escape'){hideSug();qi.blur()}});
document.addEventListener('click',function(e){if(!e.target.closest('.searchwrap'))hideSug()});
sg.addEventListener('click',function(e){if(e.target.closest('a'))setTimeout(hideSug,0)});
document.addEventListener('keydown',function(e){if(e.key==='/'&&!/input|textarea|select/i.test(document.activeElement.tagName)){e.preventDefault();qi.focus()}});
$('#themeBtn').addEventListener('click',function(){var t=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=t;try{localStorage.setItem('hub-theme',t)}catch(e){}});
$('#menuBtn').addEventListener('click',function(){var open=$('#mainnav').classList.toggle('open');this.setAttribute('aria-expanded',String(open));this.setAttribute('aria-label',open?'Close menu':'Open menu')});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&$('#mainnav').classList.contains('open')){$('#mainnav').classList.remove('open');$('#menuBtn').setAttribute('aria-expanded','false');$('#menuBtn').setAttribute('aria-label','Open menu');$('#menuBtn').focus()}});
route();
})();
