(async function(){
 'use strict';
 const q=selector=>document.querySelector(selector);
 const text=(el,value)=>{el.textContent=value};
 try{
  if(window.PagefindUI)new PagefindUI({element:'#passage-search',showSubResults:true,processResult:function(result){
    const path=result.url.split('/').pop().replace('.html','');
    result.url=result.meta.reader || result.url;
    return result;
  }});
  const lib=await fetch('/data/library.json').then(r=>r.json()),editions=[];
  for(const work of lib.works)for(const edition of work.editions)if(edition.text){
   editions.push({work,edition});q('#edition').add(new Option(work.title+' · '+edition.label,String(editions.length-1)));
  }
  const params=new URLSearchParams(location.search),chosen=editions.findIndex(x=>x.work.id===params.get('work')&&(!params.get('edition')||x.edition.id===params.get('edition')));
  if(chosen>=0)q('#edition').value=chosen;
  function citation(){
   const item=editions[Number(q('#edition').value)],cite=BCResearch.citations(item.work,item.edition),format=q('#format').value;
   try{text(q('#citation'),format==='bibliography'?cite.format('bibliography',{format:'text',template:'apa',lang:'en-US'}):cite.format(format));}
   catch(error){text(q('#citation'),'This citation could not be formatted. Please use the edition’s original source.');}
  }
  q('#edition').onchange=citation;q('#format').onchange=citation;citation();
  q('#copy-citation').onclick=async()=>{try{await navigator.clipboard.writeText(q('#citation').textContent);text(q('#copy-status'),'Citation copied.')}catch(e){text(q('#copy-status'),'Select the citation text to copy it.')}};
  q('#download-citation').onclick=()=>{const url=URL.createObjectURL(new Blob([q('#citation').textContent],{type:'text/plain;charset=utf-8'})),link=document.createElement('a');link.href=url;link.download='bibliotheca-citation.'+({bibliography:'txt',bibtex:'bib',ris:'ris'}[q('#format').value]);link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
  q('#bible-form').onsubmit=event=>{
   event.preventDefault();const hits=BCResearch.scripture(q('#reference').value);q('#bible-result').replaceChildren();
   if(!hits.length){text(q('#bible-result'),'No reference recognized. Try a full book name, chapter, and verse.');return}
   for(const hit of hits){const a=document.createElement('a');a.href='https://www.biblegateway.com/passage/?search='+encodeURIComponent(q('#reference').value.slice(hit.indices[0],hit.indices[1]))+'&version=NRSVCE';a.textContent=hit.osis+' · read in NRSV Catholic Edition';a.target='_blank';a.rel='noopener';q('#bible-result').append(a,document.createElement('br'))}
  };
  const flags=await fetch('/data/summa-supplement-ocr.json').then(r=>r.json()),raw=await fetch('/data/texts/ia-summa-supplement.txt').then(r=>r.text()),blocks=raw.replace(/\r/g,'').split(/\n\s*\n/).map(p=>p.trim()).filter(Boolean);
  flags.flags.forEach((flag,index)=>q('#scan').add(new Option('Question '+flag.q+', article '+flag.a+' · '+flag.words.join(', '),index)));
  const show=()=>{const flag=flags.flags[Number(q('#scan').value)];text(q('#transcription'),blocks[flag.block]);q('#mirador').replaceChildren();text(q('#scan-status'),'');const a=document.createElement('a');a.href=flag.scan.url;a.textContent='Open original scan at the Internet Archive';q('#scan-status').append(a)};
  q('#scan').onchange=show;show();
  q('#open-scan').onclick=async()=>{
   try{
    if(!window.Mirador)await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src='/assets/study/mirador.js';s.onload=resolve;s.onerror=reject;document.head.append(s)});
    const flag=flags.flags[Number(q('#scan').value)],manifest='https://iiif.archive.org/iiif/'+flag.scan.identifier+'/manifest.json';
    Mirador.viewer({id:'mirador',windows:[{manifestId:manifest,canvasId:'https://iiif.archive.org/iiif/'+flag.scan.identifier+'$'+flag.scan.pages[0]+'/canvas'}]});
   }catch(e){text(q('#scan-status'),'The scan viewer could not load. Use the original scan link or try again.')}
  };
 }catch(error){const p=document.createElement('p');p.textContent='Some study tools could not load. Reload or return to the reading room.';document.querySelector('main').prepend(p)}
})();
