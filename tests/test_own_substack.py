"""Our own newsletter is the first, clearly labeled entry on /substacks/ (owner request 2026-11-09), in the static page and in
the app's data (GUIDE_DATA.own), with a subscribe button, no iframe, and site style."""
import json, pathlib, re, sys, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
URL = 'https://bibliothecacatholica.substack.com/'
SUB = URL + 'subscribe'


def guide():
    s = (ROOT / 'data/guide.js').read_text(encoding='utf-8')
    return json.loads(s.split('=', 1)[1].strip().rstrip(';'))


class OwnSubstackTests(unittest.TestCase):
    def test_source_and_data_agree(self):
        import substacks_src as S
        g = guide()
        self.assertEqual(g['own']['url'], URL)
        self.assertEqual(g['own']['subscribe'], SUB)
        self.assertEqual(g['own']['html'], S.own_html())
        d = S.OWN['desc']
        self.assertIn('Advent with the Fathers', d); self.assertIn('Nov 29 to Dec 24', d)
        self.assertNotIn('—', d); self.assertIn('texts, guides, and features', d)  # Oxford comma
        # not duplicated in the curated directory list
        self.assertFalse([s for s in g['substacks'] if 'bibliothecacatholica' in s['url']])

    def test_static_page_shows_it_first(self):
        html = (ROOT / 'substacks/index.html').read_text(encoding='utf-8')
        main = html[html.index('<main'):html.index('</main>')]
        self.assertIn('<div class="eyebrow">Our newsletter</div>', main)
        self.assertIn('<a class="btn" href="' + SUB + '" target="_blank" rel="noopener">Subscribe (free) ↗</a>', main)
        self.assertIn('href="' + URL + '"', main)
        self.assertNotIn('<iframe', html)
        self.assertLess(main.index('Our newsletter'), main.index('<h1>') + 2000)  # right under the heading and intro
        self.assertNotRegex(re.search(r'<section class="featured own-substack".*?</section>', main).group(0), r'data-(support|ga|track)')

    def test_app_renders_it_before_the_featured_column(self):
        app = (ROOT / 'app.js').read_text(encoding='utf-8')
        self.assertIn("var o=(GD.own&&GD.own.html||'')+'<section class=\"featured\"><div class=\"feat-l\"><div class=\"eyebrow\">Featured column", app)
        self.assertNotIn('data/guide.js?v=20261021-collection-access', app)  # cache token bumped with the new data


if __name__ == '__main__':
    unittest.main()
