/* Bibliotheca Catholica: dated reading plans (v20), e.g. #/reading/advent-2026.
 * Data: data/reading-plans.js (window.READING_PLANS), built by tools/build_reading_plans.py from
 * tools/reading_plans.py and lazy-loaded on first use. The static page reading/<id>/ lists every day;
 * this view adds two things in the browser only: today's day is highlighted (local date), and each day
 * can be marked as read, saved in localStorage under bc-plan:<id> as {v:1,read:[day numbers]}.
 * Nothing is sent anywhere, and no analytics event is fired.
 */
(function(root){
'use strict';
var IDS=['advent-2026'];   // must match data/reading-plans.json (tests/test_reading_plans.py checks)
var DAYS=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
var MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December'];
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function has(id){return IDS.indexOf(id)>=0}
/* ISO yyyy-mm-dd -> "Sunday, November 29" (computed in UTC so the weekday never shifts). */
function longDate(iso){var p=iso.split('-').map(Number),d=new Date(Date.UTC(p[0],p[1]-1,p[2]));return DAYS[d.getUTCDay()]+', '+MONTHS[p[1]-1]+' '+p[2]}
function todayIso(now){now=now||new Date();var m=now.getMonth()+1,d=now.getDate();return now.getFullYear()+'-'+(m<10?'0':'')+m+'-'+(d<10?'0':'')+d}
function key(id){return 'bc-plan:'+id}
function getRead(id,store){store=store||root.localStorage;try{var v=JSON.parse(store.getItem(key(id))||'null');if(v&&v.v===1&&Array.isArray(v.read))return v.read.filter(function(n){return typeof n==='number'&&n>0&&n<400})}catch(e){}return []}
function setRead(id,list,store){store=store||root.localStorage;try{if(list.length)store.setItem(key(id),JSON.stringify({v:1,read:list.slice().sort(function(a,b){return a-b})}));else store.removeItem(key(id))}catch(e){}}
function find(id){var P=root.READING_PLANS;return P&&P.plans.filter(function(p){return p.id===id})[0]}
var LOADING=false,WAIT=[];
function load(cb){if(root.READING_PLANS){setTimeout(cb,0);return}WAIT.push(cb);if(LOADING)return;LOADING=true;
  var s=document.createElement('script');s.src='data/reading-plans.js?v=20261026-v20';
  s.onload=s.onerror=function(){LOADING=false;WAIT.splice(0).forEach(function(f){try{f()}catch(e){}})};document.head.appendChild(s)}
function edition(d){var L=root.LIBRARY_DATA,w=L&&L.works.filter(function(x){return x.id===d.work})[0];return w&&w.editions.filter(function(e){return e.id===d.edition})[0]}
function badge(d){var R=root.BCRights,e=edition(d);return R&&e?R.badge(R.edition(e)):''}
/* dayHtml(d, state): one day of the plan. state = {today:'yyyy-mm-dd', read:{n:true}} */
function dayHtml(d,state){var isToday=state.today===d.date,done=!!state.read[d.day];
  return '<li class="plan-day'+(d.marker?' has-marker':'')+(isToday?' is-today':'')+(done?' is-read':'')+'" id="day-'+d.day+'"'+(isToday?' aria-current="date"':'')+' data-date="'+d.date+'">'+
   '<div class="pd-head"><span class="pd-num">Day '+d.day+'</span><time datetime="'+d.date+'">'+esc(longDate(d.date))+'</time>'+(isToday?'<span class="pd-today">Today</span>':'')+'</div>'+
   (d.marker?'<p class="pd-marker">'+esc(d.marker)+'</p>':'')+
   '<h2 class="pd-title">'+(d.authorId?'<a href="#/author/'+esc(d.authorId)+'">'+esc(d.author)+'</a>':esc(d.author))+', <cite><a href="#/work/'+esc(d.work)+'">'+esc(d.title)+'</a></cite></h2>'+
   '<p class="pd-ref">'+esc(d.ref)+' · about '+d.minutes+' min</p>'+
   '<blockquote class="pd-quote"><p>“'+esc(d.quote)+(d.cut?'…':'')+'”</p></blockquote>'+
   '<p class="pd-note">'+esc(d.note)+'</p>'+
   '<div class="pd-foot"><a class="btn" href="'+esc(d.href)+'">Read day '+d.day+' →</a>'+
   '<span class="pd-print-link">bibliothecacatholica.com/'+esc(d.href)+'</span><label class="pd-check"><input type="checkbox" data-day="'+d.day+'" aria-label="Mark day '+d.day+' as read"'+(done?' checked':'')+'> Mark as read</label></div>'+
   '<p class="small pd-ed">'+esc(d.editionLabel)+(d.contributors.length?', tr. '+esc(d.contributors.join(', ')):'')+'. '+(d.yearKind==='edition'?'Edition: ':'Translation by ')+d.year+'.'+badge(d)+'</p></li>'}
function progress(plan,read){var n=plan.days.filter(function(d){return read[d.day]}).length;return n+' of '+plan.days.length+' days marked as read'}
function view(render,id){
  render('<div class="page-head"><div class="eyebrow">Reading plan</div><h1>Advent with the Fathers</h1><p class="lede">Loading the plan…</p></div>','reading');
  load(function(){var plan=find(id),main=document.getElementById('main');if(!main)return;
    if(!plan){main.innerHTML='<div class="empty"><p>This reading plan could not be loaded. <a href="/reading/'+esc(id)+'/">Open the plain version</a>.</p></div>';return}
    var list=getRead(id),read={};list.forEach(function(n){read[n]=true});var today=todayIso(),cur=plan.days.filter(function(d){return d.date===today})[0];
    var state={today:today,read:read};
    var h='<nav class="crumbs small" aria-label="Breadcrumb"><a href="#/">Bibliotheca Catholica</a> › <a href="#/reading">Reading Lists</a> › <span aria-current="page">'+esc(plan.t)+'</span></nav>'+
      '<div class="page-head plan-head"><div class="eyebrow">Reading plan · '+esc(longDate(plan.start).replace(/^\w+, /,''))+' to '+esc(longDate(plan.end).replace(/^\w+, /,''))+', '+plan.year+'</div><h1>'+esc(plan.t)+'</h1><p class="lede">'+esc(plan.intro)+'</p>'+
      '<div class="plan-tools"><span id="plan-progress" role="status">'+esc(progress(plan,read))+'</span>'+(cur?'<a class="btn gold" href="#day-'+cur.day+'" id="plan-jump">Go to today, day '+cur.day+'</a>':'')+'<button type="button" class="btn ghost" id="plan-print">Print the plan</button><button type="button" class="btn ghost" id="plan-reset"'+(list.length?'':' hidden')+'>Clear marks</button></div>'+
      '<p class="small plan-privacy">Your marks are saved only in this browser.</p></div>'+
      '<ol class="plan-days">'+plan.days.map(function(d){return dayHtml(d,state)}).join('')+'</ol>'+
      '<p class="small plan-foot">Every reading opens in the on-site reader at the start of the passage. The editions are public domain in the United States; each badge links to <a href="#/rights">how rights are determined</a>. <a href="#/reading">All reading lists</a>.</p>';
    main.innerHTML=h;document.title=plan.t+' '+plan.year+': a daily reading plan — Bibliotheca Catholica';
    function sync(){var L=Object.keys(read).filter(function(k){return read[k]}).map(Number);setRead(id,L);document.getElementById('plan-progress').textContent=progress(plan,read);document.getElementById('plan-reset').hidden=!L.length}
    main.querySelector('.plan-days').addEventListener('change',function(e){var t=e.target;if(!t.matches||!t.matches('input[data-day]'))return;var n=Number(t.dataset.day);read[n]=t.checked;if(!t.checked)delete read[n];t.closest('.plan-day').classList.toggle('is-read',t.checked);sync()});
    document.getElementById('plan-reset').onclick=function(){read={};main.querySelectorAll('input[data-day]').forEach(function(x){x.checked=false;x.closest('.plan-day').classList.remove('is-read')});sync()};
    document.getElementById('plan-print').onclick=function(){root.print()};
    var j=document.getElementById('plan-jump');if(j)j.onclick=function(e){e.preventDefault();var el=document.getElementById('day-'+cur.day);if(el){el.scrollIntoView({block:'start'});el.setAttribute('tabindex','-1');el.focus({preventScroll:true})}};
    if(root.BCRights&&root.BCRights.load)root.BCRights.load()})}
root.BCPlans={IDS:IDS,has:has,view:view,dayHtml:dayHtml,longDate:longDate,todayIso:todayIso,getRead:getRead,setRead:setRead,key:key};
if(typeof module!=='undefined')module.exports=root.BCPlans;
})(typeof window!=='undefined'?window:globalThis);
