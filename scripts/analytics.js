/* Bibliotheca Catholica: GA4 event helper (v14).
 * Uses only the existing Google tag (G-HFG445Y1LT) in <head>. No other tracking IDs, no Google Tag Manager,
 * no personal data. Every call is guarded with typeof gtag==='function' and wrapped in try/catch, so analytics
 * can never break the reader. Notes, highlights, quotes, and other free text are never sent; the only free text
 * is the search term, trimmed, lowercased, and cut to 100 characters. See AGENTS.md, "Google Analytics (GA4)".
 */
(function(root){
'use strict';
var EVENTS=['page_view','search','open_text','reader_section','listen_play','listen_complete','outbound_click','filter_use','support_click','theme_toggle'];
var MAX=100;
function str(v){return String(v==null?'':v)}
function cleanTerm(s){return str(s).replace(/\s+/g,' ').trim().toLowerCase().slice(0,MAX)}
function clean(params){var out={};if(!params||typeof params!=='object')return out;Object.keys(params).forEach(function(k){var v=params[k];
  if(v==null||v==='')return;if(typeof v==='number'){if(isFinite(v))out[k]=v;return}if(typeof v==='boolean'){out[k]=v;return}
  if(k==='page_location'||k==='page_path'){out[k]=str(v).slice(0,500);return}out[k]=str(v).slice(0,MAX)});return out}
/* track(name, params): the only way the site sends a GA4 event. Returns true when an event was handed to gtag. */
function track(name,params){try{if(typeof gtag!=='function')return false;if(EVENTS.indexOf(name)<0)return false;gtag('event',name,clean(params));return true}catch(e){return false}}
function domain(url){try{return new URL(url,'https://bibliothecacatholica.com/').hostname.replace(/^www\./,'').toLowerCase()}catch(e){return ''}}
var PUB_HOSTS=null;
function pubHosts(){if(PUB_HOSTS)return PUB_HOSTS;PUB_HOSTS={};try{var P=(root.AFFILIATES&&root.AFFILIATES.publishers)||{};Object.keys(P).forEach(function(k){var d=domain(P[k].search||'');if(d)PUB_HOSTS[d]=k})}catch(e){}return PUB_HOSTS}
/* linkKind(domain, hints): 'bookshop', 'publisher', 'substack', or 'other'. hints: {publisher:key, substack:bool} */
function linkKind(d,hints){hints=hints||{};d=str(d).toLowerCase();
  if(d==='bookshop.org'||/\.bookshop\.org$/.test(d))return 'bookshop';
  if(hints.publisher||pubHosts()[d])return 'publisher';
  if(hints.substack||d==='substack.com'||/\.substack\.com$/.test(d))return 'substack';
  return 'other'}
function publisherKey(d){return pubHosts()[str(d).toLowerCase()]||''}
/* work id from the current route (#/work/<id> or #/read/<id>/...) */
function routeWork(hash){var m=/^#\/(?:work|read)\/([a-z0-9-]+)/i.exec(str(hash));return m?m[1]:''}
/* once(key): true the first time a key is seen in a scope; reset(scope) forgets it */
var SEEN={};
function once(scope,key){var s=SEEN[scope]||(SEEN[scope]={});if(s[key])return false;s[key]=1;return true}
function reset(scope){delete SEEN[scope]}
function onClick(e){try{var t=e.target&&e.target.closest?e.target.closest('a[href]'):null;if(!t)return;
  var sup=t.closest('[data-support]');if(sup)track('support_click',{target:sup.getAttribute('data-support')});
  var href=t.getAttribute('href')||'';if(!/^https?:\/\//i.test(href))return;var d=domain(href);if(!d||d==='bibliothecacatholica.com')return;
  var dw=t.closest('[data-work]'),wk=(dw&&dw.getAttribute('data-work'))||routeWork(root.location&&root.location.hash);
  var ot=t.getAttribute('data-open-text');if(ot)track('open_text',{work_id:ot,text_source:'external',link_domain:d});
  var pk=t.getAttribute('data-pub')||publisherKey(d);
  var kind=linkKind(d,{publisher:t.getAttribute('data-pub'),substack:!!t.closest('#ss-out')});
  track('outbound_click',{link_domain:d,link_kind:kind,work_id:wk,publisher:kind==='publisher'?pk:''})}catch(err){}}
var api={EVENTS:EVENTS,MAX_TERM:MAX,track:track,cleanTerm:cleanTerm,clean:clean,domain:domain,linkKind:linkKind,publisherKey:publisherKey,routeWork:routeWork,once:once,reset:reset,onClick:onClick};
root.BCAnalytics=api;
if(root.document&&root.document.addEventListener)root.document.addEventListener('click',onClick,true);
if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
