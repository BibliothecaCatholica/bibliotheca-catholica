"""v9 checks: LibriVox data, crawlability files (added as they land)."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def js_obj(path,var):
    s=(ROOT/path).read_text();p='window.%s='%var;assert s.startswith(p);return json.loads(s[len(p):].rstrip().rstrip(';'))
class LibriVoxTests(unittest.TestCase):
    def test_librivox_matches_known_works(self):
        lv=json.loads((ROOT/'data/librivox.json').read_text());self.assertEqual(lv,js_obj('data/librivox.js','LIBRIVOX'))
        works={w['id'] for w in json.loads((ROOT/'data/library.json').read_text())['works']}
        guide={e['id'] for e in js_obj('data/guide.js','GUIDE_DATA')['editions']}
        self.assertTrue(set(lv['work'])<=works);self.assertTrue(set(lv['edition'])<=guide)
        for L in list(lv['work'].values())+list(lv['edition'].values()):
            for r in L:self.assertRegex(r['url'],r'^https://librivox\.org/[A-Za-z0-9_.-]+/$')
class CrawlTests(unittest.TestCase):
    def test_sitemap_lists_existing_static_pages(self):
        locs=re.findall(r'<loc>([^<]+)</loc>',(ROOT/'sitemap.xml').read_text());self.assertGreater(len(locs),500)
        for u in locs:
            self.assertTrue(u.startswith('https://bibliothecacatholica.com/'))
            rel=u[len('https://bibliothecacatholica.com/'):]
            f=ROOT/rel/'index.html' if rel else ROOT/'index.html';self.assertTrue(f.exists(),rel)
            s=f.read_text();self.assertIn('<link rel="canonical" href="%s">'%u,s)
            if rel:self.assertIn('window.BC_BOOT="%s"'%rel.rstrip('/'),s);self.assertIn('<base href="/">',s)
        self.assertIn('Sitemap: https://bibliothecacatholica.com/sitemap.xml',(ROOT/'robots.txt').read_text())
    def test_share_image(self):
        b=(ROOT/'assets/og-image.png').read_bytes();self.assertEqual(b[:8],b'\x89PNG\r\n\x1a\n')
        import struct;self.assertEqual(struct.unpack('>II',b[16:24]),(1200,630))
if __name__=='__main__':unittest.main()
