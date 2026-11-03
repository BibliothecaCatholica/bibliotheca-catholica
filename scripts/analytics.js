/* Bibliotheca Catholica: GA4 event helper (v14; v18 page paths).
 * Uses only the existing Google tag (G-HFG445Y1LT) in <head>. No other tracking IDs, no Google Tag Manager,
 * no personal data. Every call is guarded with typeof gtag==='function' and wrapped in try/catch, so analytics
 * can never break the reader. Notes, highlights, quotes, and other free text are never sent; the only free text
 * is the search term, trimmed, lowercased, and cut to 100 characters, sent only on the search event. Page views carry a
 * normalized route (pagePath) that never includes a search term or filter, and every event is preceded by
 * gtag('set') with the term-free page_title and page_location for the route (v18.1). See AGENTS.md, "Google Analytics (GA4)".
 */
(function(root){
'use strict';
var EVENTS=['page_view','search','open_text','reader_section','listen_play','listen_complete','outbound_click','filter_use','support_click','theme_toggle','saint_open','listen_open'];
var MAX=100;
function str(v){return String(v==null?'':v)}
function cleanTerm(s){return str(s).replace(/\s+/g,' ').trim().toLowerCase().slice(0,MAX)}
function clean(params){var out={};if(!params||typeof params!=='object')return out;Object.keys(params).forEach(function(k){var v=params[k];
  if(v==null||v==='')return;if(typeof v==='number'){if(isFinite(v))out[k]=v;return}if(typeof v==='boolean'){out[k]=v;return}
  if(k==='page_location'||k==='page_path'){out[k]=str(v).slice(0,500);return}out[k]=str(v).slice(0,MAX)});return out}
/* track(name, params): the only way the site sends a GA4 event. Returns true when an event was handed to gtag. */
function track(name,params){try{if(typeof gtag!=='function')return false;if(EVENTS.indexOf(name)<0)return false;if(name==='page_view')reset('listen_open');
  var c=context();if(c)gtag('set',{page_title:c.title,page_location:c.location});gtag('event',name,clean(params));return true}catch(e){return false}}
/* context(): the term-free page title and location for the current route. Set before every event (v18.1), so the
   search, outbound_click, and GA's own enhanced-measurement events never fall back to a document title or URL that
   holds free text. */
function context(){try{var L=root.location;if(!L)return null;var d=root.document,path=pagePath(L.hash,root.BC_BOOT);
  return {path:path,title:pageTitle(path,d&&d.title),location:pageLocation(path)}}catch(e){return null}}
function domain(url){try{return new URL(url,'https://bibliothecacatholica.com/').hostname.replace(/^www\./,'').toLowerCase()}catch(e){return ''}}
var PUB_HOSTS=null;
function pubHosts(){if(PUB_HOSTS)return PUB_HOSTS;PUB_HOSTS={};try{var P=(root.AFFILIATES&&root.AFFILIATES.publishers)||{};Object.keys(P).forEach(function(k){var d=domain(P[k].search||'');if(d)PUB_HOSTS[d]=k})}catch(e){}return PUB_HOSTS}
/* linkKind(domain, hints): 'bookshop', 'publisher', 'substack', 'audio', 'official', 'source', or 'other', in that order
   of precedence (analytics spec 2026-11-03). hints: {publisher:key, substack:bool, source:bool (the link has data-open-text)}.
   Each host matches itself and its subdomains. */
var AUDIO_HOSTS=['librivox.org'],OFFICIAL_HOSTS=['vatican.va','usccb.org','vaticannews.va'],
  SOURCE_HOSTS=['isidore.co','gutenberg.org','newadvent.org','ccel.org','archive.org','documentacatholicaomnia.eu','tertullian.org','dbu.edu','sourcebooks.fordham.edu'];
function hostIn(d,list){for(var i=0;i<list.length;i++){var h=list[i];if(d===h||d.slice(-h.length-1)==='.'+h)return true}return false}
function linkKind(d,hints){hints=hints||{};d=str(d).toLowerCase();
  if(d==='bookshop.org'||/\.bookshop\.org$/.test(d))return 'bookshop';
  if(hints.publisher||pubHosts()[d])return 'publisher';
  if(hints.substack||d==='substack.com'||/\.substack\.com$/.test(d))return 'substack';
  if(hostIn(d,AUDIO_HOSTS))return 'audio';
  if(hostIn(d,OFFICIAL_HOSTS))return 'official';
  if(hints.source||hostIn(d,SOURCE_HOSTS))return 'source';
  return 'other'}
function publisherKey(d){return pubHosts()[str(d).toLowerCase()]||''}
/* work id from the current route (#/work/<id> or #/read/<id>/...) */
function routeWork(hash){var m=/^#\/(?:work|read)\/([a-z0-9-]+)/i.exec(str(hash));return m?m[1]:''}
/* pagePath(hash, boot): the route a page_view reports. One form per view whatever URL served it (/#/author/x and
   /work/y/#/author/x both give /#/author/x; a static page with no hash uses its BC_BOOT route). Search and Isidore Index
   filters are free text, so they collapse to /#/search and /#/isidore; a segment that is not a plain slug ends the path. */
var ORIGIN='https://bibliothecacatholica.com';
function pagePath(hash,boot){var raw=str(hash).replace(/^#\/?/,'');if(!raw)raw=str(boot);raw=raw.split('?')[0];
  var p=raw.split('/').filter(Boolean),out=[];
  if(!p.length)return '/';
  if(p[0]==='search')return '/#/search';
  if(p[0]==='isidore'||p[0]==='books'){if(p[1]==='book'&&/^\d+$/.test(p[2]||''))return '/#/isidore/book/'+p[2];if(p[1]==='folders')return '/#/isidore/folders';return '/#/isidore'}
  for(var i=0;i<p.length&&i<6;i++){if(!/^[a-z0-9_.-]{1,80}$/i.test(p[i]))break;out.push(p[i])}
  return out.length?'/#/'+out.join('/'):'/'}
/* pageLocation(path, search): ORIGIN + path. Only the landing page_view passes location.search (app.js gaPageView()); from
   it only utm_source, utm_medium, utm_campaign, and utm_content are kept, each trimmed and cut to 100 characters. utm_term,
   gclid, lookup, q, and every other parameter are dropped, so no search term can reach page_location (spec 2026-11-03). */
var UTM_KEEP=['utm_source','utm_medium','utm_campaign','utm_content'];
function utmQuery(search){var q=str(search).replace(/^\?/,''),got={},out=[];if(!q)return '';
  q.split('&').forEach(function(kv){var i=kv.indexOf('='),k,v;if(i<1)return;try{k=decodeURIComponent(kv.slice(0,i).replace(/\+/g,' '));v=decodeURIComponent(kv.slice(i+1).replace(/\+/g,' '))}catch(e){return}
    if(UTM_KEEP.indexOf(k)<0||got.hasOwnProperty(k))return;v=v.replace(/\s+/g,' ').trim().slice(0,MAX);if(v)got[k]=v});
  UTM_KEEP.forEach(function(k){if(got.hasOwnProperty(k))out.push(k+'='+encodeURIComponent(got[k]))});return out.length?'?'+out.join('&'):''}
function pageLocation(path,search){return ORIGIN+(path||'/')+(search?utmQuery(search):'')}
/* pageTitle(path, docTitle): search and Index routes get a fixed title; elsewhere the document title, which on
   those routes is built from catalog data only. */
var SITE_NAME='Bibliotheca Catholica';
function pageTitle(path,docTitle){if(path==='/#/search')return 'Search — '+SITE_NAME;if(path==='/#/isidore')return 'The Isidore Index — '+SITE_NAME;
  return str(docTitle||SITE_NAME).slice(0,MAX)}
/* once(key): true the first time a key is seen in a scope; reset(scope) forgets it */
var SEEN={};
function once(scope,key){var s=SEEN[scope]||(SEEN[scope]={});if(s[key])return false;s[key]=1;return true}
function reset(scope){delete SEEN[scope]}
function onClick(e){try{var t=e.target&&e.target.closest?e.target.closest('a[href]'):null;if(!t)return;
  var sup=t.closest('[data-support]');if(sup)track('support_click',{target:sup.getAttribute('data-support')});
  var href=t.getAttribute('href')||'';if(!/^https?:\/\//i.test(href))return;var d=domain(href);if(!d||d==='bibliothecacatholica.com')return;
  var ot=t.getAttribute('data-open-text');if(ot)track('open_text',{work_id:ot,text_source:'external',link_domain:d});
  var kind=linkKind(d,{publisher:t.getAttribute('data-pub'),substack:!!t.closest('#ss-out'),source:!!ot});
  /* listen_open (librivox): a work-page Listen link (class listen-btn) to LibriVox, once per work per page view */
  if(kind==='audio'&&t.classList&&t.classList.contains('listen-btn')){var L=root.location||{},wid=routeWork(L.hash)||routeWork('#/'+str(root.BC_BOOT));
    if(wid&&once('listen_open',wid))track('listen_open',{work_id:wid,listen_source:'librivox'})}
  track('outbound_click',{link_domain:d,link_kind:kind})}catch(err){}}
var api={utmQuery:utmQuery,hostIn:hostIn,EVENTS:EVENTS,MAX_TERM:MAX,track:track,cleanTerm:cleanTerm,clean:clean,domain:domain,linkKind:linkKind,publisherKey:publisherKey,routeWork:routeWork,pagePath:pagePath,pageLocation:pageLocation,pageTitle:pageTitle,context:context,once:once,reset:reset,onClick:onClick};
root.BCAnalytics=api;
if(root.document&&root.document.addEventListener)root.document.addEventListener('click',onClick,true);
if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
