const test=require('node:test'),assert=require('node:assert/strict');
global.window={};require('../assets/study/tools.js');
test('Scripture parser recognizes deuterocanonical passages and refuses ordinary prose',()=>{
 const p=window.BCResearch.scripture;
 assert.equal(p('Wisdom 2:12-20')[0].osis,'Wis.2.12-Wis.2.20');
 assert.equal(p('the heart of the matter').length,0);
});
test('Citations preserve translator and source without inventing a publication date',()=>{
 const cite=window.BCResearch.citations({id:'test',title:'Confessions',author:'Augustine'},{id:'edition',source:'https://www.gutenberg.org/ebooks/3296',contributors:[{role:'translator',name:'E. B. Pusey'}]});
 const ris=cite.format('ris');assert.match(ris,/Pusey/);assert.match(ris,/3296/);
 assert.match(cite.format('bibliography',{format:'text',template:'apa'}),/Confessions/);
});
test('/study/ loads the site fonts the same way the other static pages do',()=>{
 const fs=require('fs'),path=require('path'),R=p=>fs.readFileSync(path.join(__dirname,'..',p),'utf8');
 const idx=R('index.html'),study=R('study/index.html');
 const fontsCss=idx.match(/href="(?:\/)?(styles\/fonts\.css\?v=[^"]+)"/)[1];
 assert.ok(study.includes('href="/'+fontsCss+'"'),'same fonts.css version as index.html');
 for(const m of idx.matchAll(/<link rel="preload" as="font"[^>]*href="(\/fonts\/[^"]+)">/g))assert.ok(study.includes('href="'+m[1]+'"'),m[1]);
 assert.ok(study.indexOf('fonts.css')<study.indexOf('/styles.css'),'fonts.css before styles.css');
 assert.equal((study.match(/googletagmanager\.com\/gtag\/js/g)||[]).length,1);
});
test('housekeeping 2026-11-20: /study/ is indexed, canonical, described, and in the sitemap',()=>{
 const fs=require('fs'),path=require('path'),R=p=>fs.readFileSync(path.join(__dirname,'..',p),'utf8');
 const s=R('study/index.html');
 assert.match(s,/<link rel="canonical" href="https:\/\/bibliothecacatholica\.com\/study\/">/);
 assert.match(s,/<meta name="robots" content="index,follow">/);
 const d=s.match(/<meta name="description" content="([^"]+)">/)[1];assert.ok(d.length>=50&&d.length<=170&&!d.includes('—'),d);
 assert.ok(R('sitemap.xml').includes('<loc>https://bibliothecacatholica.com/study/</loc>'));
 assert.ok(!/Disallow: \/study/.test(R('robots.txt')));
});
