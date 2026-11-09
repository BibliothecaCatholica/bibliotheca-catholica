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
