/* Shared, dependency-free search rules. Imported records never enter selected search. */
(function(root){
  'use strict';
  function norm(s){return String(s||'').replace(/\b([a-z])\.\s*([a-z])\./gi,'$1$2').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
  function imported(e){return e.type==='Book'||e.type==='Isidore Index author'}
  function search(entries,q,scope,limit){
    var query=norm(q),tokens=query.split(/\s+/).filter(Boolean);
    if(!tokens.length)return [];
    return entries.filter(function(e){return scope==='all'||(scope==='isidore'?imported(e):!imported(e))})
      .map(function(e){var title=norm(e.t),haystack=norm(e.x||e.t+' '+e.s),score=e.w||1;
        if(!tokens.every(function(t){return haystack.indexOf(t)>=0}))return null;
        tokens.forEach(function(t){if(title.indexOf(t)===0)score+=4;else if(title.indexOf(t)>=0)score+=2.5});
        return {e:e,score:score+(title===query?10:0)};
      }).filter(Boolean).sort(function(a,b){return b.score-a.score||a.e.t.localeCompare(b.e.t)})
      .slice(0,limit||400).map(function(x){return x.e});
  }
  var api={search:search,imported:imported};
  if(typeof module!=='undefined')module.exports=api;else root.BCSearch=api;
})(typeof window!=='undefined'?window:globalThis);
