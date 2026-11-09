"""Generate searchable hosted passages and the study desk. Run after build_static.py."""
import json,re,html,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=html.escape
out=ROOT/'.study-index'
if out.exists():shutil.rmtree(out)
out.mkdir(parents=True)
lib=json.loads((ROOT/'data/library.json').read_text())
for w in sorted(lib['works'], key=lambda w: w['id']):
 for e in sorted(w['editions'], key=lambda e: e['id']):
  if not e.get('text'):continue
  blocks=[p.strip() for p in re.split(r'\n\s*\n',(ROOT/e['text']).read_text().replace('\r','')) if p.strip()]
  for start in range(0,len(blocks),35):
   text='\n\n'.join(blocks[start:start+35])
   # Search each hosted edition once, without duplicate question/chapter pages.
   url='/#/read/'+w['id']+'/'+e['id']+'/'+str(start//35)
   title=w['title']+' · '+e['label']+' · section '+str(start//35+1)
   (out/(w['id']+'-'+e['id']+'-'+str(start)+'.html')).write_text('<html lang="en"><head><title>'+E(title)+'</title></head><body><main data-pagefind-body><a data-pagefind-meta="reader[href]" href="'+url+'"></a><h1>'+E(title)+'</h1><p>'+E(w['author'])+'</p><article>'+E(text)+'</article><a href="'+url+'">Open in the reader</a></main></body></html>')
# A search URL points to its reader section rather than the indexing document.
print('Study search:',len(list(out.glob('*.html'))),'edition sections')
