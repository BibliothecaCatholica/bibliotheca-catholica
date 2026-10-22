/* Shared catalog relationships for the edition guide and reading paths. */
(function(root,factory){var api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.BCGuides=api})(typeof window!=='undefined'?window:this,function(){
 'use strict';
 function norm(s){return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()}
 function works(record,catalog){return (record.workIds||[]).map(function(id){return catalog.find(function(w){return w.id===id})}).filter(Boolean)}
 function item(record,editions,catalog){var guide=editions.find(function(w){return w.id===record.e}),matched=works(guide||record,catalog),first=matched[0];return {guide:guide,works:matched,title:record.t||(guide?guide.t:first?first.title:''),author:record.a||(guide?guide.a:first?first.author:''),free:guide?guide.free||[]:record.free||[]}}
 function available(record,catalog,options){var matched=works(record,catalog);return {here:matched.some(function(w){return w.editions.some(function(e){return !!e.text})}),online:!!(record.free||[]).length||matched.some(function(w){return w.editions.some(function(e){return e.access==='full-text'})}),epub:matched.some(function(w){return (options[w.id]||[]).some(function(o){return o.format==='EPUB'})})}}
 function matches(record,q){var text=norm([record.t,record.a,record.title,record.author,record.b,record.why,record.cat,(record.picks||[]).map(function(p){return p.tr+' '+p.pub+' '+p.isbn}).join(' ')].join(' '));return norm(q).trim().split(/\s+/).filter(Boolean).every(function(t){return text.indexOf(t)>=0})}
 return {norm:norm,works:works,item:item,available:available,matches:matches};
});
