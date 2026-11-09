"""Shared, progressively enhanced research paths for /libraries/."""
import html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=html.escape
PATHS=[
 ('Read the Fathers','Compare a readable text with a scanned edition and follow its Scripture references.','/study/','Open the study desk'),
 ('Find a saint','Browse sourced names and calendar dates, then follow writings and biographies.','/saints/','Explore the saints'),
 ('Lives of the saints','Read Butler here, or compare historical collections and their editions.','/saints/books/','Browse the hagiography shelf'),
 ('Understand patron saints','A historical reference article from the Catholic Encyclopedia. Historical liturgical rules may differ from current practice.','https://www.newadvent.org/cathen/11562a.htm','Read at New Advent'),
 ('Compare translations','Choose an edition with its translator, date, and reading options in view.','/editions/','Compare editions'),
 ('Explore Latin sources','Find Aquinas in Latin, with bibliographies and research tools at Corpus Thomisticum.','https://www.corpusthomisticum.org/','Visit Corpus Thomisticum')]
def desk_html():
 h='<section class="library-desk" aria-labelledby="library-desk-title"><p class="eyebrow">The great libraries</p><h2 id="library-desk-title">One question, several collections</h2><p>Start with a research path, or carry a title, author, or subject into another collection. Each source keeps its own catalog and access rules.</p><div class="library-paths">'
 for t,d,u,label in PATHS:
  h+='<article><h3>'+E(t)+'</h3><p>'+E(d)+'</p><a href="'+E(u)+'"'+(' target="_blank" rel="noopener"' if u.startswith('https:') else '')+'>'+E(label)+' →</a></article>'
 h+='</div><div class="library-source-search"><h3>Search another collection</h3><form id="library-source-form" action="https://openlibrary.org/search" method="get" target="_blank" rel="noopener"><label for="library-source-q">Title, author, or subject</label><input id="library-source-q" name="q" type="search" maxlength="200" placeholder="For example, Bede or Lives of the Saints" required><label for="library-source">Collection</label><select id="library-source" disabled><option>Open Library</option></select><button class="btn" type="submit">Search at source ↗</button></form><p id="library-source-note" class="small" role="status">Search opens Open Library in a new tab. Your query goes to the collection you choose only when you submit.</p></div><p><a href="/study/">Search passages in our hosted editions</a> · <a href="/saints/books/">Read lives of the saints here</a></p></section>'
 return h
if __name__=='__main__':
 (ROOT/'data/library-desk.js').write_text('window.LIBRARY_DESK='+json.dumps({'html':desk_html()},ensure_ascii=False)+';\n')
