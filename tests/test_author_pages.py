"""Phase A item 2 (2026-11-03): static pages for the 454 authors with no hosted work (tools/author_pages.py).
Intro instead of the Wikipedia excerpt; reading-room works and Isidore Index books listed link-only with rights badges;
edition guides with Bookshop.org buttons only for ISBNs in data/guide.js; official links only when checked."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import author_pages as AP
def jsvar(f):
    s=(ROOT/f).read_text();return json.loads(s[s.index('=')+1:].rstrip().rstrip(';'))
HUB=json.loads((ROOT/'data/catholic-hub.json').read_text());LIB=json.loads((ROOT/'data/library.json').read_text())
FL=json.loads((ROOT/'data/editorial-flags.json').read_text());GUIDE=jsvar('data/guide.js')
HOSTED={w['authorId'] for w in LIB['works'] if w.get('authorId') and any(e.get('text') for e in w['editions'])}
AUTH=[a for a in HUB['authors'] if a['id'] not in set(FL.get('hubAuthors',[]))]
NOH=[a for a in AUTH if a['id'] not in HOSTED]
ISBNS={p['isbn'] for e in GUIDE['editions'] for p in e.get('picks') or [] if p.get('isbn')}
def page(id):return (ROOT/'author'/id/'index.html').read_text()
def main(s):return s[s.find('<main'):s.find('</main>')]
class AuthorPages(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(NOH),454);self.assertEqual(len(AUTH)-len(NOH),22)
    def test_intro_not_wikipedia_excerpt(self):
        for a in NOH:
            m=main(page(a['id']))
            self.assertEqual(m.count('<p class="au-intro">'),1,a['id'])
            self.assertNotIn('class="extract"',m,a['id']);self.assertNotIn('wiki-credit',m,a['id']);self.assertNotIn('CC BY-SA',m,a['id'])
            if any('wikipedia.org/wiki/' in l['url'] for l in a.get('links') or []):self.assertRegex(m,r'href="https://en\.wikipedia\.org/wiki/[^"]+"',a['id'])
    def test_hosted_authors_keep_the_credited_excerpt(self):
        for a in AUTH:
            if a['id'] in HOSTED and a.get('extract') and a['extract'] not in (a.get('desc') or a.get('wikiDesc') or ''):
                m=main(page(a['id']));self.assertIn('class="extract"',m);self.assertIn('CC BY-SA 4.0',m)
    def test_works_lists_are_link_only_with_badges(self):
        n=0
        for a in NOH:
            m=main(page(a['id']))
            for sec in re.findall(r'<h2>(?:Books in the Isidore Index|In our library \(read at the source\))</h2>.*?</ul>',m):
                for li in re.findall(r'<li>(.*?)</li>',sec):
                    n+=1;self.assertIn('class="rights-badge rb-',li,a['id']);self.assertIn('href="/rights/"',li)
                    for h in re.findall(r'href="([^"]+)"',li):
                        self.assertRegex(h,r'^(https://isidore\.co/calibre/legacy/book/\d+/CalibreLibrary|/work/[a-z0-9-]+/|/rights/)$',a['id'])
            self.assertNotRegex(m,r'/get/|calibre/mobile|CalibreLibrary/[^"]|#book_id=|>Download|>Read here<',a['id'])
        self.assertGreater(n,1000)
    def test_flagged_books_never_listed(self):
        ids={k for k in FL['books']};allm=''.join(main(page(a['id'])) for a in NOH)
        for k in ids:self.assertNotIn('legacy/book/%s/CalibreLibrary'%k,allm)
    def test_bookshop_links_use_our_id_and_known_isbns(self):
        n=0
        for a in NOH:
            m=main(page(a['id']))
            self.assertNotRegex(m.lower(),r'amazon\.|amzn\.')
            for h in re.findall(r'href="(https://bookshop\.org[^"]*)"',m):
                n+=1;mm=re.fullmatch(r'https://bookshop\.org/a/130222/(97[89]\d{10})',h);self.assertTrue(mm,h);self.assertIn(mm.group(1),ISBNS)
            if 'bookshop.org' in m:self.assertIn('Affiliate disclosure',m)
        self.assertGreater(n,0)
    def test_official_links_checked(self):
        for a in NOH:
            m=main(page(a['id']))
            sec=re.search(r'<h2>Official site, talks, and podcasts</h2><ul>(.*?)</ul>',m)
            if sec:
                for h in re.findall(r'href="([^"]+)"',sec.group(1)):self.assertIn(h.replace('&amp;','&'),AP.CHECKED,a['id'])
    def test_the_four_named_pages(self):
        want={'warren-h-carroll':['/editions/carroll/','https://press.christendom.edu/'],'scott-hahn':['/editions/romesweethome/','/editions/lambssupper/','https://stpaulcenter.com/'],
              'trent-horn':['https://www.trenthorn.com/','https://www.catholic.com/audio/cot'],'thomas-e-woods':['https://isidore.co/calibre/legacy/book/4949/CalibreLibrary']}
        for id,hs in want.items():
            s=page(id);m=main(s)
            for h in hs:self.assertIn('href="%s"'%h,m,id)
            self.assertEqual(s.count('<h1'),1);self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/author/%s/">'%id,s)
            self.assertNotIn('—',re.sub(r'<[^>]+>','',m.split('<p class="au-intro">')[1].split('</p>')[0]))
    def test_unique_titles_one_h1(self):
        seen={}
        for a in AUTH:
            s=page(a['id']);t=re.search(r'<title>([^<]*)</title>',s).group(1)
            self.assertNotIn(t,seen,a['id']);seen[t]=a['id'];self.assertEqual(s.count('<h1'),1,a['id'])
    def test_role_words_match_app(self):
        js=re.search(r'var AU_ROLE=(\{[^\n]*\});',(ROOT/'app.js').read_text()).group(1)
        self.assertEqual(dict(re.findall(r"(\w+):'([^']*)'",js)),AP.ROLE)
if __name__=='__main__':unittest.main()
