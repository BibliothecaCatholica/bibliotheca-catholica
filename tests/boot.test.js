const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function boot(){
 const events={},notice={hidden:true},classes=new Set(),timers=new Map();let next=0;
 const document={body:{},documentElement:{classList:{add:c=>classes.add(c)}},getElementById:id=>id==='app-status'?notice:null,querySelectorAll:()=>[]};
 const window={addEventListener:(n,fn)=>events[n]=fn};
 const ctx={window,document,setTimeout:fn=>{timers.set(++next,fn);return next},clearTimeout:id=>timers.delete(id)};
 vm.runInNewContext(fs.readFileSync('scripts/boot.js','utf8'),ctx);
 return {window,events,notice,classes,timers};
}
test('a missing core script reveals recovery without removing plain content',()=>{
 const x=boot();x.events.error({target:{tagName:'SCRIPT',src:'https://bibliothecacatholica.com/data/library.js?v=1'}});
 assert.equal(x.notice.hidden,false);assert(x.classes.has('app-unavailable'));
});
test('blocked analytics and successful startup do not produce a false site failure',()=>{
 const x=boot();x.events.error({target:{tagName:'SCRIPT',src:'https://www.googletagmanager.com/gtag/js?id=G-HFG445Y1LT'}});
 x.window.BCBoot.ready();x.events.DOMContentLoaded();assert.equal(x.notice.hidden,true);assert.equal(x.timers.size,0);
});
test('startup timeout displays recovery and ready cancels the timeout',()=>{
 const x=boot();x.events.DOMContentLoaded();assert.equal(x.timers.size,1);[...x.timers.values()][0]();assert.equal(x.notice.hidden,false);
 const y=boot();y.events.DOMContentLoaded();y.window.BCBoot.ready();assert.equal(y.timers.size,0);assert.equal(y.notice.hidden,true);
});
test('partial search failures attempt each missing collection once and announce incomplete results',()=>{
 const source=fs.readFileSync('app.js','utf8'),code=source.slice(source.indexOf('function results(q){'),source.indexOf('var srchT=null'));
 const tries={},rendered=[];const attempt=(name,cb,value)=>{tries[name]=(tries[name]||0)+1;if(tries[name]>1)throw Error('unbounded retry: '+name);cb(value)};
 const ctx={location:{hash:'#/search/test'},SAINTS_IN:false,SEARCH_ERRORS:{},GD:null,B:null,LZ:{},searchScope:'all',
  saintsIdx:cb=>attempt('saints',cb,null),loadGuide:cb=>attempt('guides',cb,true),loadBooks:cb=>attempt('books',cb,true),lazy:(file,name,cb)=>attempt(name,cb,null),
  search:()=>[],saintHit:()=>'',esc:String,encodeURIComponent,render:h=>rendered.push(h),document:{title:''},$:()=>({}),
  setTimeout:()=>1,clearTimeout:()=>{},srchT:null,window:{BCSearch:{imported:()=>false}}};
 vm.runInNewContext(code+"\nresults('test');results('test');",ctx);
 assert.equal(Object.keys(tries).length,5);assert(Object.values(tries).every(n=>n===1));
 assert(rendered.at(-1).includes('These results are incomplete'));assert(!rendered.at(-1).includes('(loading books…)'));
});
