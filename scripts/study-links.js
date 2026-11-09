(function(){
 const enhance=()=>{
  const main=document.getElementById('main');if(!main)return;
  const match=location.hash.match(/^#\/(?:work|read)\/([^/]+)(?:\/([^/]+))?/);
  if(match&&!main.querySelector('.study-link')){
   const a=document.createElement('a');a.className='study-link btn ghost';a.href='/study/?work='+encodeURIComponent(match[1])+(match[2]?'&edition='+encodeURIComponent(match[2]):'')+'#cite';a.textContent='Cite this edition · Study tools';main.append(a);
  }
  const daily=main.querySelector('.daily-head');
  if(daily&&!daily.querySelector('.calendar-source')){
   const box=document.createElement('div');box.className='calendar-source';daily.append(box);
   fetch('/data/study/calendar.json').then(r=>r.json()).then(data=>{
    const d=new Date(),key=[d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-'),events=data.days[key];
    box.textContent=events?events.sort((a,b)=>b.rank-a.rank).map(e=>e.name).join(' · '):'Calendar coverage: 2026–2027';
    const source=document.createElement('a');source.href='https://litcal.johnromanodorazio.com/';source.textContent=' · Roman rite, US · LitCal';box.append(source);
   }).catch(()=>{box.textContent='Liturgical calendar unavailable.'});
  }
 };
 document.addEventListener('DOMContentLoaded',()=>{const main=document.getElementById('main');if(main)new MutationObserver(enhance).observe(main,{childList:true});enhance()});
 window.addEventListener('hashchange',enhance);
})();
