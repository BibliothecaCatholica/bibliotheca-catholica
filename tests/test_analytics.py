"""Google Analytics: every HTML page carries exactly one GA4 tag right after <head>."""
import pathlib, re, unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
GA = 'G-HFG445Y1LT'
VERIFICATION_FILE = 'google3b007babfa8923a4.html'

class TestAnalytics(unittest.TestCase):
    def pages(self):
        return [f for f in ROOT.rglob('*.html') if not ({'.git', 'node_modules', '.openai'} & set(f.relative_to(ROOT).parts)) and f != ROOT / VERIFICATION_FILE]

    def test_google_verification_file_remains_exact(self):
        self.assertEqual((ROOT / VERIFICATION_FILE).read_bytes(),
                         ('google-site-verification: ' + VERIFICATION_FILE).encode('utf-8'))

    def test_exactly_one_tag_after_head(self):
        pages = self.pages()
        self.assertGreater(len(pages), 600)
        for f in pages:
            s = f.read_text(errors='ignore')
            with self.subTest(page=str(f.relative_to(ROOT))):
                self.assertEqual(s.count('googletagmanager.com/gtag/js'), 1)
                self.assertEqual(s.count('googletagmanager.com/gtag/js?id=' + GA), 1)
                self.assertEqual(s.count("gtag('config'"), 1)
                self.assertTrue(re.search(r'<head>\s*<!-- Google tag \(gtag\.js\) -->', s))

    def test_config_defers_first_page_view_to_app(self):
        # app.js sends the first page_view itself, so every config call turns off the automatic one (no double count)
        for f in self.pages():
            s = f.read_text(errors='ignore')
            with self.subTest(page=str(f.relative_to(ROOT))):
                self.assertIn("gtag('config', '" + GA + "', {'send_page_view': false});", s)
        nf = (ROOT / '404.html').read_text()
        self.assertNotIn('app.js', nf)  # 404.html only redirects; the page it redirects to counts the visit once

    def test_helper_is_loaded_once_before_library_and_app(self):
        s = (ROOT / 'index.html').read_text()
        self.assertEqual(s.count('scripts/analytics.js'), 1)
        self.assertLess(s.index('scripts/analytics.js'), s.index('scripts/library.js'))
        self.assertLess(s.index('scripts/analytics.js'), s.index('app.js?'))

    def test_helper_guard(self):
        js = (ROOT / 'scripts/analytics.js').read_text()
        self.assertIn("typeof gtag!=='function'", js)
        self.assertIn("gtag('event',name,", js)
        self.assertIn('try{', js)
        self.assertIn('G-HFG445Y1LT', js)  # named only in the comment; no other ID anywhere
        self.assertEqual(re.findall(r'G-[A-Z0-9]{6,}', js), ['G-HFG445Y1LT'])
        self.assertNotIn('googletagmanager', js)

    def test_events_only_via_helper(self):
        for name in ('app.js', 'scripts/library.js', 'scripts/reader.js', 'scripts/guides.js', 'scripts/search.js'):
            js = (ROOT / name).read_text()
            with self.subTest(file=name):
                self.assertNotIn("gtag(", js)
                self.assertNotIn('dataLayer', js)
        app = (ROOT / 'app.js').read_text()
        lib = (ROOT / 'scripts/library.js').read_text()
        for ev in ('page_view', 'search', 'filter_use', 'theme_toggle'):
            self.assertIn("track('" + ev + "'", app)
        for ev in ('open_text', 'reader_section', 'listen_play', 'listen_complete', 'filter_use'):
            self.assertIn("track('" + ev + "'", lib)
        helper = (ROOT / 'scripts/analytics.js').read_text()
        for ev in ('outbound_click', 'support_click', 'open_text'):
            self.assertIn("track('" + ev + "'", helper)

    def test_no_other_tracking_ids(self):
        for f in self.pages() + [ROOT / 'app.js'] + list((ROOT / 'scripts').glob('*.js')):
            s = f.read_text(errors='ignore')
            with self.subTest(file=str(f.relative_to(ROOT))):
                self.assertEqual(set(re.findall(r'\b(?:G|UA|AW|GTM)-[A-Z0-9-]{4,}', s)) - {GA}, set())

    def test_privacy_note(self):
        s = (ROOT / 'policy/index.html').read_text()
        self.assertIn('id="privacy"', s)
        self.assertIn('Google Analytics', s)
        self.assertIn('https://policies.google.com/technologies/partner-sites', s)
        self.assertIn('what people search for', s)
        self.assertIn('which outside links are clicked', s)
        self.assertIn('The site’s own events shorten search terms to 100 characters and send them only with the search itself.', s)
        self.assertNotIn('Search terms are shortened', s)  # v18.2: GA’s own outbound-click event is covered separately
        self.assertIn('built-in outside-link measurement', s)
        self.assertIn('collects no personal data', s)
        self.assertIn('runs no ads', s)
        self.assertIn('local storage on this device', s)

if __name__ == '__main__':
    unittest.main()
