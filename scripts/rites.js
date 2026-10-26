/* Rites & Liturgy (v19, phase 2). Data and page HTML: data/rites.js (window.RITES_DATA), built by
   tools/build_rites.py from data/rites-src/ and lazy-loaded on first use (books.js is untouched). The
   pages are the same HTML as the static /rites/ pages (tools/rites_pages.py); this file only mounts the
   map and wires the selector. One Church or family at a time, present vs approximate historical
   heartland; no pins, no dioceses, no population numbers, no tracking beyond the page_view that app.js
   already sends. Pure helpers live in BCRites.core (tested in tests/rites.test.js). See docs/RITES.md. */
(function(root){
  'use strict';
  var VER='20261026-v19';
  var D=null,WAIT=[],LOADING=false;
  function load(cb){if(D){cb&&cb(D);return}if(cb)WAIT.push(cb);if(LOADING)return;LOADING=true;
    function done(){D=root.RITES_DATA||null;WAIT.splice(0).forEach(function(f){try{f(D)}catch(e){console.warn(e)}})}
    if(root.RITES_DATA){setTimeout(done,0);return}var sc=document.createElement('script');sc.src='data/rites.js?v='+VER;sc.onload=done;sc.onerror=done;document.head.appendChild(sc)}
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  /* Same steps as fill_slot() in tools/rites_pages.py. */
  function block(J,lid,select,view){var L=J.layers[lid],t=J.tpl[select?'full':'record'],k=lid+'|'+view;
    var rep={'%LAYER%':lid,'%VIEW%':view,'%FAM%':L.family,'%SVG%':J.svg,'%INSETS%':J.insets,'%INFO%':J.info[k],'%STATUS%':esc(J.status[k]),'%OPTIONS%':J.options};
    Object.keys(rep).forEach(function(x){t=t.split(x).join(rep[x])});return t}
  function codes(J,lid,view){var L=J.layers[lid];return L?(L[view]||[]).slice():[]}
  function defaultView(){return 'present'}  /* the heartland layer is approximate and never the default */
  var core={block:block,codes:codes,defaultView:defaultView,esc:esc};
  function apply(sec,lid,view){if(!D.layers[lid])return;var L=D.layers[lid];if(view==='heartland'&&!L.heartland.length)view='present';
    sec.setAttribute('data-layer',lid);sec.setAttribute('data-view',view);sec.setAttribute('data-fam',L.family);
    var on={};L[view].forEach(function(c){on[c]=1});
    sec.querySelectorAll('path[data-c]').forEach(function(p){p.classList.toggle('on',!!on[p.getAttribute('data-c')])});
    var k=lid+'|'+view;sec.querySelector('.rmap-info').innerHTML=D.info[k];sec.querySelector('.rmap-status').textContent=D.status[k];
    var sel=sec.querySelector('#rmap-sel');if(sel&&sel.value!==lid)sel.value=lid;
    sec.querySelectorAll('input[name=rmap-view]').forEach(function(r){r.checked=r.value===view;if(r.value==='heartland')r.disabled=!L.heartland.length})}
  function mount(scope){scope.querySelectorAll('.rmap-slot').forEach(function(slot){var lid=slot.getAttribute('data-layer'),select=slot.getAttribute('data-select')==='1';
      if(!D.layers[lid])return;var w=document.createElement('div');w.innerHTML=block(D,lid,select,defaultView());var sec=w.firstChild;slot.parentNode.replaceChild(sec,slot);
      apply(sec,lid,defaultView());var ctl=sec.querySelector('.rmap-controls');if(ctl)ctl.hidden=false;
      var sel=sec.querySelector('#rmap-sel');if(sel)sel.addEventListener('change',function(){apply(sec,sel.value,'present')});
      sec.querySelectorAll('input[name=rmap-view]').forEach(function(r){r.addEventListener('change',function(){if(r.checked)apply(sec,sec.getAttribute('data-layer'),r.value)})});
      if(select)scope.querySelectorAll('.rites-show').forEach(function(b){b.hidden=false;b.addEventListener('click',function(){var id=b.getAttribute('data-layer'),L=D.layers[id];
        apply(sec,id,L&&!L.present.length&&L.heartland.length?'heartland':'present');if(sec.scrollIntoView)sec.scrollIntoView({block:'nearest',behavior:'smooth'})})})})}
  function view(render,p){load(function(){
    if(!D){render('<div class="empty"><h2>Rites &amp; Liturgy could not load</h2><p><a href="/rites/">Open the plain version</a></p></div>','rites');return}
    var k=p[0]||'',pg=D.pages[k];
    if(!pg||p.length>1){render('<div class="page-head"><h1>Page not found</h1><p class="lede">There is no Rites &amp; Liturgy page at this address. <a href="/rites/">See all Churches and rites</a>.</p></div>','rites');return}
    render(pg.html,'rites');mount(document.getElementById('main')||document)})}
  var api={core:core,load:load,view:view,mount:mount};
  if(typeof module!=='undefined')module.exports=api;else root.BCRites=api;
})(typeof window!=='undefined'?window:globalThis);
