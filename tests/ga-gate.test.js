// The Google tag loads only on the production host; elsewhere (*.pages.dev previews) the page gets robots noindex
// and no Google script at all (Round 8, Job D, November 23, 2026). Runs the tag from index.html in a sandbox.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('index.html','utf8');
const tag=html.match(/<!-- Google tag \(gtag\.js\) -->\n<script>([\s\S]*?)<\/script>\n<script>([\s\S]*?)<\/script>\n/);
function run(hostname){
  const added=[];const document={head:{appendChild:el=>added.push(el)},createElement:t=>({tagName:t})};
  const window={};const ctx={window,document,location:{hostname},Date};ctx.dataLayer=window.dataLayer=[];
  vm.createContext(ctx);vm.runInContext('var window=this;'+tag[1]+'\n'+tag[2],ctx);
  return {added,calls:ctx.dataLayer.map(a=>Array.from(a))};
}
test('the tag is two inline scripts with one gtag.js URL and one config call',()=>{
  assert.ok(tag,'tag right after <head>');
  assert.equal(html.split('googletagmanager.com/gtag/js?id=G-HFG445Y1LT').length-1,1);
  assert.doesNotMatch(html,/<script async src="https:\/\/www\.googletagmanager\.com/);
});
for(const host of ['bibliothecacatholica.com','www.bibliothecacatholica.com'])
  test('production ('+host+') loads gtag.js and configures without an automatic page view',()=>{
    const r=run(host);
    assert.deepEqual(r.added.map(e=>[e.tagName,e.src,e.async]),[['script','https://www.googletagmanager.com/gtag/js?id=G-HFG445Y1LT',true]]);
    assert.equal(JSON.stringify(r.calls.filter(c=>c[0]==='config')),JSON.stringify([['config','G-HFG445Y1LT',{send_page_view:false}]]));
  });
for(const host of ['bibliotheca-catholica.pages.dev','abc123.bibliotheca-catholica-preview.pages.dev','localhost',''])
  test('elsewhere ('+(host||'no host')+') adds robots noindex and loads no Google script',()=>{
    const r=run(host);
    assert.deepEqual(r.added.map(e=>[e.tagName,e.name,e.content]),[['meta','robots','noindex']]);
    assert.equal(r.calls.filter(c=>c[0]==='config').length,0);
  });
