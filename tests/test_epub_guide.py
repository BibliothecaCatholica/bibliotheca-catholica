"""Steering C (2026-11-03): the EPUB guide at /guides/epub-on-your-device/ (tools/guide_pages.py)."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'));import guide_pages
PAGE=(ROOT/'guides/epub-on-your-device/index.html').read_text()
MAIN=re.search(r'<main.*?</main>',PAGE,re.S).group(0)
HTML=guide_pages.pages()['epub-on-your-device']['html']
class EpubGuide(unittest.TestCase):
    def test_prerendered_and_in_sitemap(self):
        self.assertIn('https://bibliothecacatholica.com/guides/epub-on-your-device/',(ROOT/'sitemap.xml').read_text())
        self.assertIn('guides/epub-on-your-device/index.html',(ROOT/'docs/static-pages.txt').read_text())
        self.assertIn('<h1>Read an EPUB on your device</h1>',MAIN)
        self.assertIn('window.BC_BOOT="guides/epub-on-your-device"',PAGE)
        self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/guides/epub-on-your-device/">',PAGE)
    def test_app_data_matches_static(self):
        g=json.loads((ROOT/'data/guides.js').read_text().strip()[len('window.GUIDES='):-1])
        self.assertEqual(g['epub-on-your-device']['html'],HTML);self.assertIn(HTML,MAIN)
    def test_linked_from_footer_and_download_areas(self):
        for f in('index.html','about/index.html','work/confessions/index.html','author/trent-horn/index.html'):
            self.assertIn('<a href="/guides/epub-on-your-device/">Read an EPUB on your device</a>',(ROOT/f).read_text(),f)
        lib=(ROOT/'scripts/library.js').read_text();self.assertEqual(lib.count('/guides/epub-on-your-device/'),1)  # the work page's Download row (design pass 2026-11-12)
        app=(ROOT/'app.js').read_text();self.assertIn("case 'guides':guidePage(",app);self.assertIn('|guides)$/',app)
        self.assertIn('/guides/epub-on-your-device/',app);self.assertIn("p[0]==='guides'",app)
    def test_reading_room_first_and_pdf(self):
        t=re.sub(r'<[^>]+>','',HTML)
        self.assertLess(t.find('Reading Room'),t.find('Send to Kindle'))
        self.assertIn('>EPUB help</a>',(ROOT/'scripts/library.js').read_text())
        self.assertIn('with nothing to install',t);self.assertIn('Prefer a PDF?',t)
        for dev in('Kindle','Kobo','Apple Books','iPhone','iPad','Android','Google Play Books','Moon+ Reader','Calibre','Send to Kindle','USB'):self.assertIn(dev,t,dev)
    def test_copy_rules(self):
        t=HTML.lower()
        self.assertNotIn('—',HTML);self.assertNotIn('tax-deductible',t);self.assertNotIn('tax deductible',t)
        self.assertNotRegex(t,r'amzn\.|tag=|ascsubtag|bookshop\.org|/dp/|/gp/product')
        self.assertNotRegex(HTML,r'data-support|data-ga|onclick|gtag')
        self.assertNotIn('href="#',HTML)
    def test_only_help_links(self):
        for u in re.findall(r'href="(https?://[^"]+)"',HTML):
            if 'amazon.' in u:self.assertRegex(u,r'^https://www\.amazon\.com/(gp/help/customer/display\.html\?nodeId=\w+|sendtokindle(/\w+)?)$',u)
            else:self.assertRegex(u,r'^https://(help\.kobo\.com|support\.apple\.com|support\.google\.com|play\.google\.com/store/apps/details\?id=com\.flyersoft\.moonreader|manual\.calibre-ebook\.com)(/|$)',u)
        for k,(name,url) in guide_pages.SOURCES.items():self.assertIn(url.replace('&','&amp;'),HTML,k)
    def test_one_ga_tag(self):
        self.assertEqual(PAGE.count('googletagmanager.com/gtag/js'),1)
if __name__=='__main__':unittest.main()
