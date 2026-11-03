"""Phase A item 3 (2026-11): the pre-rendered HTML crawlers read.  Reading-list entries always carry a title;
work, edition-guide, and author pages link one another by real paths; a hash route with a static page is written as its path,
and the hash routes with no static page (#/read/..., #/isidore/author=...) sit beside a real fallback link."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGES=[l.strip() for l in (ROOT/'docs/static-pages.txt').read_text().splitlines() if l.strip()]
ROUTES={p[:-len('/index.html')] for p in PAGES}
def main(p):
    s=(ROOT/p).read_text();return s[s.find('<main'):s.find('</main>')]
def jsvar(f):
    s=(ROOT/f).read_text();return json.loads(s[s.index('=')+1:].rstrip().rstrip(';'))
GUIDE=jsvar('data/guide.js');LIB=json.loads((ROOT/'data/library.json').read_text())
ONWARD=re.compile(r'href="(/(?:work|author|editions|saints|reading)/[^"#]+)"')
class StaticCrosslinks(unittest.TestCase):
    def test_reading_list_entries_have_titles(self):
        for L in GUIDE['lists']:
            m=main('reading/%s/index.html'%L['id'])
            items=re.findall(r'<li>(.*?)</li>',m[m.find('<ol>'):m.find('</ol>')])
            self.assertEqual(len(items),len(L['items']),L['id'])
            for li in items:
                title=re.sub(r'<[^>]+>','',li).split(':')[0].strip()
                self.assertTrue(title,'empty reading-list title in %s: %r'%(L['id'],li))
    def test_every_work_page_links_onward(self):
        for w in LIB['works']:
            hs={h for h in ONWARD.findall(main('work/%s/index.html'%w['id'])) if h!='/work/%s/'%w['id']}
            self.assertTrue(hs,'work/%s has no onward link'%w['id'])
    def test_works_link_their_edition_guides_and_back(self):
        self.assertIn('href="/editions/rule/"',main('work/rule-of-benedict/index.html'))
        for ed in GUIDE['editions']:
            m=main('editions/%s/index.html'%ed['id'])
            for wid in ed.get('workIds') or []:
                self.assertIn('href="/editions/%s/"'%ed['id'],main('work/%s/index.html'%wid))
                self.assertIn('href="/work/%s/"'%wid,m)
            if ed.get('aid') and 'author/'+ed['aid'] in ROUTES:
                self.assertIn('href="/author/%s/"'%ed['aid'],m)
                self.assertIn('href="/editions/%s/"'%ed['id'],main('author/%s/index.html'%ed['aid']))
    def test_no_hash_link_where_a_static_page_exists(self):
        for p in PAGES:
            for h in re.findall(r'href="/?#/([a-z0-9/-]+?)/?"',main(p)):
                self.assertNotIn(h,ROUTES,'%s links #/%s; use /%s/'%(p,h,h))
    def test_hash_only_routes_have_a_fallback(self):
        for p in PAGES:
            m=main(p)
            if '/#/isidore/' in m:self.assertIn('href="/isidore/"',m,p)
            if '/#/read/' in m:self.assertRegex(m,r'href="(/work/[^"]+|https?://[^"]+)"',p)
if __name__=='__main__':unittest.main()
