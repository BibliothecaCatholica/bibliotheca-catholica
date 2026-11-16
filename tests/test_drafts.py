"""Unlisted Substack draft preview pages at /drafts/ (data/substack-drafts.json, tools/build_drafts.py)."""
import json,re,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_drafts
SITE='https://bibliothecacatholica.com/'
DATA=json.loads((ROOT/'data/substack-drafts.json').read_text(encoding='utf-8'))
DRAFTS=DATA['drafts']
ROBOTS='<meta name="robots" content="noindex,nofollow">'
GA='G-HFG445Y1LT'

class DraftPages(unittest.TestCase):
    def test_data_entries(self):
        slugs=[]
        for d in DRAFTS:
            self.assertEqual(d['status'],'draft',d['slug'])
            self.assertRegex(d['slug'],r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
            self.assertTrue(d['title']);self.assertTrue(d['body'])
            slugs.append(d['slug'])
        self.assertEqual(len(slugs),len(set(slugs)))
        self.assertGreaterEqual(len(slugs),1)

    def test_pages_exist_and_are_plain(self):
        index=ROOT/'drafts'/'index.html'
        self.assertTrue(index.is_file())
        idx=index.read_text(encoding='utf-8')
        self.assertIn(ROBOTS,idx)
        self.assertTrue(re.search(r'<head>\s*<!-- Google tag \(gtag\.js\) -->',idx))
        self.assertEqual(idx.count('googletagmanager.com/gtag/js'),1)
        self.assertIn("gtag('config', '"+GA+"', {'send_page_view': false});",idx)
        self.assertNotIn('class="footer"',idx)
        self.assertNotIn('class="mainnav"',idx)
        for d in DRAFTS:
            p=ROOT/'drafts'/d['slug']/'index.html'
            s=p.read_text(encoding='utf-8')
            self.assertIn(ROBOTS,s,d['slug'])
            self.assertIn('<h1>'+d['title']+'</h1>',s)
            self.assertIn('<article>',s)
            self.assertNotIn('class="footer"',s)
            self.assertNotIn('class="mainnav"',s)
            self.assertNotIn('window.BC_BOOT',s)
            self.assertIn('href="/drafts/'+d['slug']+'/"',idx)

    def test_absent_from_sitemap_nav_search_and_feeds(self):
        sm=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
        self.assertNotIn('/drafts',sm)
        pages=(ROOT/'docs'/'static-pages.txt').read_text(encoding='utf-8')
        self.assertNotIn('drafts/',pages)
        home=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertNotIn('href="/drafts/',home)
        robots=(ROOT/'robots.txt').read_text(encoding='utf-8')
        self.assertIn('Disallow: /drafts/',robots)
        # client search and section lists do not include the drafts path
        app=(ROOT/'app.js').read_text(encoding='utf-8')
        self.assertNotIn("'/drafts'",app)
        self.assertNotIn('"/drafts/"',app)
        m=re.search(r"var STATIC_SECTIONS=\[([^\]]*)\]",app)
        self.assertIsNotNone(m)
        self.assertNotIn("'drafts'",m.group(1))

    def test_no_amazon(self):
        for d in DRAFTS:
            self.assertNotRegex(d['body'].lower(),r'href="[^"]*(amazon\.|amzn\.)',d['slug'])

    def test_rebuild_drops_removed_entries(self):
        """Deleting an entry and rebuilding must drop that page and leave no stale directory."""
        stale=ROOT/'drafts'/'stale-removed-slug'
        stale.mkdir(exist_ok=True)
        (stale/'index.html').write_text('stale',encoding='utf-8')
        build_drafts.build()
        self.assertFalse(stale.exists())
        have={p.name for p in (ROOT/'drafts').iterdir()}
        self.assertEqual(have,{'index.html'}|{d['slug'] for d in DRAFTS})

if __name__=='__main__':unittest.main()
