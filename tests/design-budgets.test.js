// Design budgets (docs/DESIGN.md, owner-approved pass 2026-11-12). The work page is rendered by
// scripts/library.js, so it runs here against the real data with a minimal DOM stand-in.
const test=require('node:test');const assert=require('node:assert');const fs=require('fs');const vm=require('vm');

function load(){
 const win={};
 const ctx={window:win,document:{getElementById:()=>null,addEventListener(){},querySelector:()=>null,body:{classList:{add(){},remove(){}}}},location:{hash:''},localStorage:{getItem:()=>null,setItem(){}},console};
 win.document=ctx.document;win.location=ctx.location;
 for(const f of ['data/library.js','data/reading-options.js','data/isidore-matches.js','data/librivox.js','data/print-editions.js','data/text-pages.js','data/editorial-flags.js','scripts/rights.js','scripts/library.js'])
  vm.runInNewContext(fs.readFileSync(f,'utf8'),ctx,{filename:f});
 return win;
}
const W=load();
function workHtml(id){let out='';W.BCLibrary.work(h=>{out=h},id);return out}
const count=(h,re)=>(h.match(re)||[]).length;
const filled=h=>count(h,/class="btn(?: [^"]*)?"/g)-count(h,/class="btn [^"]*\bghost\b[^"]*"/g);
const buttons=h=>count(h,/<(?:a|button)\b[^>]*class="(?:btn|rb-btn)\b[^"]*"/g)+count(h,/<button\b(?![^>]*class=)/g);

test('every work page has at most one filled button and at most six buttons',()=>{
 const ids=W.LIBRARY_DATA.works.map(w=>w.id);assert.ok(ids.length>100);
 for(const id of ids){const h=workHtml(id);assert.ok(h.length>0,id);assert.ok(filled(h)<=1,id+': '+filled(h)+' filled buttons');assert.ok(buttons(h)<=6,id+': '+buttons(h)+' buttons')}
});
test('a hosted work leads with one "Read here" and keeps its rights evidence behind a disclosure',()=>{
 const h=workHtml('divine-comedy');  // an unmapped hosted work (verse, kept out of chapter maps); mapped works get the title-page work page
 assert.match(h,/<a class="btn" href="#\/read\/divine-comedy\/pg-1004">Read here<\/a>/);
 assert.ok(h.indexOf('Read here')<h.indexOf('Other ways to read'));
 assert.match(h,/<details class="ed-details"><summary>Source and rights details<\/summary>/);
 const e=W.LIBRARY_DATA.works.find(w=>w.id==='divine-comedy').editions[0];
 assert.ok(h.includes(e.checked)&&h.includes('Source checked'),'checked date stays on the page');
 for(const way of ['Listen','Download','Buy in print','Find in a library'])assert.ok(h.includes('<h3>'+way+'</h3>'),way);
 // rule 7 (owner, November 14, 2026): the one-line disclosure appears once, beside the affiliate links, with Details
 assert.equal(count(h,/Affiliate links: we may earn a commission\. <a href="\/disclosure\/">Details<\/a>\./g),1);
});
test('no bordered card inside a bordered panel on work pages',()=>{
 // rows use hairline dividers; the only bordered boxes left are context notes (.ef-box) and the
 // "not available here" callout, and neither ever holds another bordered element.
 for(const w of W.LIBRARY_DATA.works){const h=workHtml(w.id);
  assert.equal(count(h,/class="(?:panel|library-card|download-panel)\b/g),0,w.id);
  for(const box of h.match(/<div class="ef-box">[^]*?<\/div>/g)||[])assert.ok(!/class="(?:panel|ef-box|callout|btn)/.test(box.slice(20)),w.id)}
});
test('the reader keeps its storage keys and anchors',()=>{
 const lib=fs.readFileSync('scripts/library.js','utf8'),rd=fs.readFileSync('scripts/reader.js','utf8');
 for(const k of ["'bc-reading:'","'bc:'+setting[0]",'id="reader-size"','id="reader-spacing"','id="reader-part"',"' id=\"reading-p-'+i+'\"'"])assert.ok(lib.includes(k),k);
 for(const k of ["NOTES_PREFIX='bc-notes:'","RECENT_KEY='bc-recent'",'rb-aa-menu'])assert.ok(rd.includes(k),k);
});
// Design part 2 budgets (home, navigation, portraits).
test('home page: one search (the header), one filled button, and a short link budget before the footer',()=>{
 // 25 was the 12 November 2026 budget. The 21 November 2026 Ask Magisterium AI block adds three links:
 // the referral, Why we use Magisterium AI, and the disclosure Details link.
 const html=fs.readFileSync('index.html','utf8'),main=html.slice(html.indexOf('<main'),html.indexOf('</main>'));
 assert.ok(count(main,/<a\s/g)<=28,'links: '+count(main,/<a\s/g));
 assert.equal(count(html,/type="search"/g),1);assert.ok(!main.includes('hero-search'));
 assert.equal(filled(main),1);
});
test('navigation: six or seven visible sections and no drawer; everything else is in the footer',()=>{
 const html=fs.readFileSync('index.html','utf8'),nav=html.slice(html.indexOf('<nav class="mainnav"'),html.indexOf('</nav>',html.indexOf('<nav class="mainnav"')));
 const items=(nav.match(/<a [^>]*data-nav="[^"]+"[^>]*>/g)||[]).filter(a=>!a.includes('nav-m'));
 assert.ok(items.length>=6&&items.length<=7,String(items.length));assert.ok(!html.includes('nav-more'));
 const foot=html.slice(html.indexOf('<footer'));
 for(const p of ['/timeline/','/editions/','/isidore/','/scripture/','/doctors/','/rites/','/references/','/media/','/rare/','/substacks/','/projects/'])assert.ok(foot.includes('href="'+p+'"'),p);
});
test('portraits: every self-hosted file matches its manifest checksum and is a public-domain credited portrait',()=>{
 const crypto=require('crypto'),m=JSON.parse(fs.readFileSync('data/portraits.json','utf8')),hub=JSON.parse(fs.readFileSync('data/catholic-hub.json','utf8'));
 const byId=Object.fromEntries(hub.authors.map(a=>[a.id,a]));assert.ok(Object.keys(m.portraits).length>=280);
 for(const [id,r] of Object.entries(m.portraits)){const a=byId[id];assert.ok(a&&a.imgCredit&&a.imgCredit.pd,id);
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(r.file)).digest('hex'),r.sha256,id);assert.ok(r.page&&r.license,id)}
 assert.deepEqual(fs.readdirSync('assets/portraits').sort(),Object.values(m.portraits).map(r=>r.file.split('/').pop()).sort());
});
// Design part 2 fix (owner review, November 14, 2026): author pages on phones.
test('author pages: works are rows without format chips, and list links and controls are at least 24 px tall',()=>{
 const app=fs.readFileSync('app.js','utf8'),css=fs.readFileSync('styles.css','utf8');
 const fn=name=>{const i=app.indexOf('function '+name+'(');assert.ok(i>=0,name);return app.slice(i,app.indexOf('\nfunction ',i+1))};
 const works=fn('auWorks'),book=fn('auBook');
 assert.ok(works.includes('auBook')&&!works.includes('brow(')&&!works.includes('au-fmt'),'author works use book rows, no format filter');
 assert.ok(!/fmt fmt-|b-fmts|b-tag/.test(book),'no format or tag chips in author book rows');
 // the CSS guarantee measured in the browser (0 targets under 24 px on emulated iPhone 13 author pages)
 const rule=css.match(/\.au-panel li a,[^{]*\{[^}]*\}/);assert.ok(rule,'tap-target rule');
 for(const sel of ['.au-panel li a','.saint-panel li a','.au-panel button','.au-tabs a','.au-panel .linklist a'])assert.ok(rule[0].includes(sel),sel);
 assert.match(rule[0],/min-height:24px/);assert.match(css,/\.backlink\{[^}]*min-height:24px/);
});
test('phone header: search collapses behind a search button below 600 px; the form and its "/" shortcut are unchanged',()=>{
 const html=fs.readFileSync('index.html','utf8'),css=fs.readFileSync('styles.css','utf8'),app=fs.readFileSync('app.js','utf8');
 assert.match(html,/<button id="searchBtn" class="iconbtn search-btn" type="button" aria-label="Search" aria-controls="site-search" aria-expanded="false">/);
 assert.match(html,/<form class="searchwrap" id="site-search" role="search" action="\/search\/" method="get">/);
 assert.match(css,/\.iconbtn\.search-btn\{display:none\}/);
 assert.match(css,/@media\(max-width:600px\)\{html\.js \.iconbtn\.search-btn\{display:grid\}[^@]*html\.js \.topbar:not\(\.search-open\) \.searchwrap\{display:none\}/);
 assert.ok(app.includes("if(e.key==='/'&&")&&app.includes('if(searchCollapsed())searchOpen(true);else qi.focus()'));
 assert.ok(!/scope=(library|isidore)/.test(html.slice(html.indexOf('<form class="searchwrap"'),html.indexOf('</form>'))),'header search keeps the Everything default');
});

// Design refresh (owner's pick, November 17, 2026): catalogue pages.
test('reading room: subject facets with counts; author index: one filter bar, no chips or portraits',()=>{
 const lib=fs.readFileSync('scripts/library.js','utf8'),app=fs.readFileSync('app.js','utf8'),css=fs.readFileSync('styles.css','utf8');
 assert.match(lib,/<fieldset id="library-topic" class="lf-set"><legend>Subject<\/legend>/);
 assert.match(lib,/type="radio" name="library-topic"/);assert.match(lib,/class="lf-n">'\+n\+'/);
 for(const id of ['library-query','library-format','library-readable','library-count','library-results'])assert.ok(lib.includes('id="'+id+'"'),id);
 for(const ev of ["filter_name:'Subject'","filter_name:'Format'","filter_name:'Read on this site'"])assert.ok(lib.includes(ev),ev);
 const i=app.indexOf('function authors('),au=app.slice(i,app.indexOf('\nfunction ',i+1));
 assert.ok(au.includes('class="au-bar"')&&au.includes('id="af-era"')&&au.includes('class="au-list"'));
 assert.ok(!au.includes('class="chip')&&!au.includes('thumb('),'no chips or portraits in the author index');
 assert.match(css,/--field:#94805c/);assert.match(css,/\[data-theme=dark\]\{[^}]*--field:#6b6f7c/);
});

// Design refresh (owner's pick, November 17, 2026): masthead navigation and footer.
test('masthead: small-caps sections with an underlined current section, list menu on phones, focus not gold',()=>{
 const css=fs.readFileSync('styles/refresh.css','utf8'),blk=css.slice(css.indexOf('/* Navigation and footer (design refresh'));
 assert.ok(blk.length>100,'masthead block');
 assert.match(blk,/\.mainnav a\{font:500 18px\/1 var\(--serif\);font-variant-caps:all-small-caps/);
 assert.match(blk,/\.mainnav a\[aria-current=page\],\.mainnav a\.on,\[data-theme=dark\] \.mainnav a\.on\{color:var\(--rubric\);border-bottom-color:var\(--rubric\)\}/);
 assert.match(blk,/\.mainnav\.open \.nav-row\{display:block\}/);
 for(const f of ['styles/library.css','styles/home.css','styles/saints.css'])assert.ok(!/outline:[^;}]*var\(--gold\)/.test(fs.readFileSync(f,'utf8')),f);
});
