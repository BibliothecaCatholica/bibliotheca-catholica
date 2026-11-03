"""Phase A item 2: copy the Research file for the four modern author pages (data/modern-authors.json, a copy of
research/modern-authors-pages.json, 2026-11-03) into data/catholic-hub.json through hubio.
Sets: intro (Research's original intro, as written), born (null when Research marks it unverified), books (every book
in the file, link-only, verified ISBN-13 only), media (official site, podcasts, YouTube, X, organization pages; only URLs
in author_pages.CHECKED). Never scotthahn.com book links (they sell through Amazon), never Amazon, never Bookshop
(no Bookshop product page could be verified, so no button). Run: python3 tools/import_modern_authors.py"""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import hubio,author_pages as AP
NO_LINK=re.compile(r'amazon\.|amzn\.|scotthahn\.com/.*book|bookshop\.org',re.I)
def book_url(b):
    srcs=[u for u in b.get('isbn_sources') or [] if not NO_LINK.search(u) and u in AP.CHECKED]
    pub=[u for u in srcs if 'openlibrary.org' not in u]
    return (pub or srcs or [None])[0]
def book_note(b):
    n=b.get('edition_note') or ''
    if 'Christendom' in (b.get('publisher') or '') and '2004' in n:return 'ISBN is the 2004 Christendom Press reprint'
    if b.get('coauthor'):return 'with '+b['coauthor']
    return ''
def main():
    R=json.loads((ROOT/'data/modern-authors.json').read_text())
    hub=hubio.load();by={a['id']:a for a in hub['authors']}
    for r in R['authors']:
        a=by[r['id']]
        a['intro']=r['intro']
        if r.get('born_status')=='unverified':a['born']=None
        books=[]
        for b in r['books']:
            if b.get('isbn13_status')!='verified' or not re.fullmatch(r'97[89]\d{10}',b.get('isbn13') or ''):continue
            y=b.get('first_published') if b.get('first_published_status')=='verified' else None
            x={'t':b['title'],'pub':b.get('publisher') or '','isbn':b['isbn13']}
            if y:x['y']=y
            u=book_url(b)
            if u:x['url']=u
            n=book_note(b)
            if n:x['note']=n
            books.append(x)
        a['books']=books
        media=[]
        def add(label,url,kind):
            if url and url in AP.CHECKED and not NO_LINK.search(url) and all(m['url']!=url for m in media):media.append({'label':label,'url':url,'kind':kind})
        if r.get('official_site'):add(r['name']+' (official site)',r['official_site'],'official')
        for m in r.get('free_media') or []:add(m['label'],m['url'],m.get('kind') or 'media')
        for s in r.get('social') or []:add(r['name']+' on '+s['platform'],s['url'],'social')
        for o in r.get('organizations') or []:add(o['label'],o['url'],'organization')
        a['media']=media
        # the hub 'site' links these replace (official() would list them twice)
        mu={m['url'] for m in media}
        a['links']=[l for l in a.get('links') or [] if l.get('kind')!='site' or l['url'] not in mu]
    hubio.save(hub)
    for r in R['authors']:
        a=by[r['id']];print(r['id'],'born',a.get('born'),'books',len(a['books']),'media',len(a['media']),'links',[l['label'] for l in a['links']])
if __name__=='__main__':main()
