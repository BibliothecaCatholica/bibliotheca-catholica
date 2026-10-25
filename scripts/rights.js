/* Bibliotheca Catholica: rights badges (v16). See AGENTS.md, "Rights badges", and #/rights.
 * Five statuses; download and reader buttons appear ONLY for the first three (hostable):
 *   public_domain_us · open_license · permission_granted · link_only · unknown
 * Isidore Index statuses come from data/rights.js (window.RIGHTS_DATA, built by tools/build_rights.py),
 * lazy-loaded together with data/books.js. Until it loads, or if it fails, every record counts as unknown,
 * so the safe default is "no file links". Reading-room editions get their status from data/library.json.
 * Not legal advice.
 */
(function(root){
'use strict';
var STATUSES={
  public_domain_us:{label:'Public domain (US)',hostable:true},
  open_license:{label:'Open license',hostable:true},
  permission_granted:{label:'Permission granted',hostable:true},
  link_only:{label:'Link only',hostable:false},
  unknown:{label:'Unknown',hostable:false}
};
var ORDER=['public_domain_us','open_license','permission_granted','link_only','unknown'];
function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function data(){return root.RIGHTS_DATA||null}
function hostable(status){return !!(STATUSES[status]&&STATUSES[status].hostable)}
/* resolve(R, id): pure lookup in a RIGHTS_DATA object. Unknown ids, a missing file, or a hostable status
   without written evidence all fall back to unknown. */
function resolve(R,id){
  var r=R&&R.records&&R.records[String(id)];
  if(!r)return {status:'unknown',evidence:'Not yet reviewed.',checked:''};
  var c=R.codes[r[0]]||{};var status=r[0]==='M'?r[3]:c.status;
  var ev=((c.text||'')+(r[1]?' '+r[1]:'')).trim();
  if(!STATUSES[status])status='unknown';
  if(hostable(status)&&!(r[1]&&r[1].length>20))status='unknown';
  return {status:status,evidence:ev,checked:r[0]==='M'?r[2]:(R.checked||'')}}
function record(id){return resolve(data(),id)}
/* edition(e): a reading-room edition in data/library.json. Hosted texts were checked under the
   pre-1931 rule before they were added; everything else on a work page is a link to its source. */
function edition(e){
  if(!e||e.access==='reference')return null;
  if(e.text&&/^Public domain in the USA/.test(e.rights||'')&&e.checked)return {status:'public_domain_us',evidence:(e.note?e.note+' ':'')+e.rights,checked:e.checked};
  return {status:'link_only',evidence:(e.rights||'')+' Read it at the source.',checked:e.checked||''}}
function title(x){return STATUSES[x.status].label+'. '+x.evidence+(x.checked?' Checked '+x.checked+'.':'')+' Not legal advice.'}
/* badge(x): calm, factual pill linking to #/rights, with the evidence and the checked date in its tooltip. */
function badge(x){if(!x)return '';return ' <a class="rights-badge rb-'+x.status.replace(/_/g,'-')+'" href="#/rights" data-rights="'+x.status+'" title="'+esc(title(x))+'"><span class="rb-k">Rights:</span> '+esc(STATUSES[x.status].label)+'</a>'}
/* line(x): the record-page line with evidence and checked date. */
function line(x){if(!x)return '';return '<div class="rights-line">'+badge(x).trim()+'<p class="small">'+esc(x.evidence)+(x.checked?' <span class="muted">Checked '+esc(x.checked)+'.</span>':'')+' <a href="#/rights">How rights are determined</a> · not legal advice.</p></div>'}
var LOADING=false,WAIT=[];
function load(cb){if(data()){cb&&setTimeout(cb,0);return}if(cb)WAIT.push(cb);if(LOADING)return;LOADING=true;
  if(typeof document==='undefined')return;
  var s=document.createElement('script');s.src='data/rights.js?v=20261025-v16';
  s.onload=s.onerror=function(){WAIT.splice(0).forEach(function(f){try{f()}catch(e){}})};document.head.appendChild(s)}
var API={STATUSES:STATUSES,ORDER:ORDER,hostable:hostable,resolve:resolve,record:record,edition:edition,badge:badge,line:line,title:title,load:load};
root.BCRights=API;
if(typeof module!=='undefined'&&module.exports)module.exports=API;
})(typeof window!=='undefined'?window:globalThis);
