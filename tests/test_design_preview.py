"""Unlisted design-refresh previews at /design-preview/ (tools/build_design_preview.py, November 2026).

Delete this test with the script and the directory once the refresh is built (docs/research/design-directions-2026-11.md)."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_design_preview as bdp
from notices import PG_LINE
OUT=ROOT/'design-preview'
ROBOTS='<meta name="robots" content="noindex,nofollow">'
GA='G-HFG445Y1LT'
AREAS=[a for a,_ in bdp.AREAS]

def pages():
    return [OUT/'index.html']+[OUT/a/v/'index.html' for a in AREAS for v in ('v1','v2','v3','v4')]

class DesignPreview(unittest.TestCase):
    def test_every_page_exists_and_nothing_else(self):
        have=sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file())
        self.assertEqual(have,sorted(p.relative_to(OUT).as_posix() for p in pages()))
        self.assertEqual(len(AREAS),5)
        for a in AREAS:self.assertEqual([k for k,_,_ in bdp.VARIANTS[a]],['v1','v2','v3','v4'])

    def test_noindex_one_ga_tag_and_no_app(self):
        for p in pages():
            s=p.read_text(encoding='utf-8');rel=str(p.relative_to(ROOT))
            with self.subTest(page=rel):
                self.assertEqual(s.count(ROBOTS),1)
                self.assertTrue(re.search(r'<head>\s*<!-- Google tag \(gtag\.js\) -->',s))
                self.assertEqual(s.count('googletagmanager.com/gtag/js'),1)
                self.assertIn("gtag('config', '"+GA+"', {'send_page_view': false});",s)
                self.assertNotRegex(s,r'src="[^"]*(app|analytics)\.js');self.assertNotIn('BCAnalytics',s)
                self.assertEqual(re.findall(r'<script[^>]+src="([^"]+)"',s),['https://www.googletagmanager.com/gtag/js?id='+GA])
                self.assertNotRegex(s,r'fonts\.googleapis|fonts\.gstatic|<iframe')
                self.assertEqual(len(re.findall(r'<h1[ >]',s)),1)
                self.assertNotIn('<link rel="canonical"',s)

    def test_out_of_sitemap_nav_search_and_robots_disallowed(self):
        self.assertNotIn('design-preview',(ROOT/'sitemap.xml').read_text(encoding='utf-8'))
        self.assertNotIn('design-preview',(ROOT/'docs/static-pages.txt').read_text(encoding='utf-8'))
        self.assertIn('Disallow: /design-preview/',(ROOT/'robots.txt').read_text(encoding='utf-8'))
        for f in ('index.html','app.js','data/site-copy.js','404.html'):
            self.assertNotIn('design-preview',(ROOT/f).read_text(encoding='utf-8'),f)

    def test_standing_rules(self):
        flags=json.loads((ROOT/'data/editorial-flags.json').read_text(encoding='utf-8'))
        flagged=[f.get('title') for f in flags['books'].values() if f.get('title')]
        for p in pages():
            s=p.read_text(encoding='utf-8');low=s.lower();rel=str(p.relative_to(ROOT))
            with self.subTest(page=rel):
                self.assertNotRegex(low,r'amazon\.|amzn\.')
                self.assertNotIn('tax-deductible',low);self.assertNotIn('tax deductible',low)
                self.assertNotIn('bookshop.org',low)  # no affiliate links in the previews, so no disclosure line is needed beside them
                self.assertNotIn('isidore/book/',s)
                if '/home/' in rel:
                    for t in flagged:self.assertNotIn('>'+t+'<',s)
        # our own copy carries no em-dashes (hosted book text may)
        self.assertNotIn('—',(ROOT/'tools/build_design_preview.py').read_text(encoding='utf-8'))

    def test_reading_pages_keep_the_gutenberg_sentence_once_after_the_text(self):
        for v in ('v1','v2','v3','v4'):
            s=(OUT/'reading'/v/'index.html').read_text(encoding='utf-8')
            self.assertEqual(s.count(PG_LINE),1,v)
            self.assertGreater(s.index(PG_LINE),s.rindex('</article>'),v)
            self.assertIn('<summary>Edition details</summary>',s)

    def test_sources_pages_keep_licensing_text_and_takedown_link(self):
        from rights_pages import licensing_html
        lic=licensing_html((ROOT/'LICENSING.md').read_text(encoding='utf-8'))
        lede=re.search(r'<p class="lede">(.*?)</p>',lic,re.S).group(1)
        for v in ('v1','v2','v3','v4'):
            s=(OUT/'sources'/v/'index.html').read_text(encoding='utf-8')
            self.assertIn(lede,s,v);self.assertIn('not legal advice',s)
            self.assertIn('https://bibliothecacatholica.com/takedown/',s.replace('href="/takedown/"','https://bibliothecacatholica.com/takedown/'),v)
            for h in re.findall(r'<h2>(.*?)</h2>',lic):self.assertIn(re.sub(r'^\d+\. ','',h),s,v)

    def test_rebuild_drops_stale_output(self):
        stale=OUT/'stale'/'v9';stale.mkdir(parents=True,exist_ok=True);(stale/'index.html').write_text('stale',encoding='utf-8')
        bdp.build()
        self.assertFalse((OUT/'stale').exists())

if __name__=='__main__':unittest.main()
