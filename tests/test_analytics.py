"""Google Analytics: every HTML page carries exactly one GA4 tag right after <head>."""
import pathlib, re, unittest
ROOT = pathlib.Path(__file__).resolve().parent.parent
GA = 'G-HFG445Y1LT'

class TestAnalytics(unittest.TestCase):
    def pages(self):
        return [f for f in ROOT.rglob('*.html') if not ({'.git', 'node_modules'} & set(f.relative_to(ROOT).parts))]

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

    def test_spa_page_views(self):
        js = (ROOT / 'app.js').read_text()
        self.assertIn("typeof gtag!=='function'", js)
        self.assertIn("gtag('event','page_view'", js)

    def test_privacy_note(self):
        s = (ROOT / 'policy/index.html').read_text()
        self.assertIn('id="privacy"', s)
        self.assertIn('Google Analytics', s)
        self.assertIn('https://policies.google.com/technologies/partner-sites', s)

if __name__ == '__main__':
    unittest.main()
