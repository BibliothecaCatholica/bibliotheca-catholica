/* Keep plain pages useful when the interactive application cannot start. No telemetry or storage. */
(function(root){
'use strict';
var ready=false,failed=false,timer=null;
var critical=/\/(?:app\.js|data\/(?:data|library)\.js|scripts\/(?:library|search|saints|timeline|rights)\.js)(?:\?|$)/;
function show(){
 if(!document.body)return;
 var notice=document.getElementById('app-status');if(!notice)return;
 notice.hidden=false;
 document.documentElement.classList.add('app-unavailable');
 document.querySelectorAll('a[href]').forEach(function(a){
  var href=a.getAttribute('href'),m=/^#\/(author|work|editions|reading|saints)\/([a-z0-9-]+)$/.exec(href||'');
  if(m)a.href='/'+m[1]+'/'+m[2]+'/';
 });
}
function fail(){failed=true;clearTimeout(timer);show()}
root.BCBoot={ready:function(){ready=true;clearTimeout(timer);if(!failed){var n=document.getElementById('app-status');if(n)n.hidden=true}},fail:fail};
root.addEventListener('error',function(e){var src=e.target&&e.target.tagName==='SCRIPT'?e.target.src:e.filename;
 if(!ready&&src&&critical.test(src))fail();
},true);
root.addEventListener('DOMContentLoaded',function(){
 if(failed)show();else if(!ready)timer=setTimeout(fail,10000);
 var reload=document.getElementById('app-reload');if(reload)reload.addEventListener('click',function(){root.location.reload()});
});
})(window);
