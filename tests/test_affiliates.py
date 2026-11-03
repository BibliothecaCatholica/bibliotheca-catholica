"""Affiliate config: Bookshop ID stays 130222, the shop URL is the owner-confirmed one, and the UI still hides the shop link if it is blank."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class AffiliateTests(unittest.TestCase):
    def setUp(self):
        self.aff = (ROOT / 'data/affiliates.js').read_text(encoding='utf-8')
        self.app = (ROOT / 'app.js').read_text(encoding='utf-8')

    def test_bookshop_id(self):
        self.assertRegex(self.aff, r"bookshopId:\s*'130222'")

    def test_shop_url_is_the_confirmed_shop(self):
        m = re.search(r"bookshopShop:\s*'([^']*)'", self.aff)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), 'https://bookshop.org/shop/bibliotheca-catholica', 'owner-confirmed shop URL (2026-11-03)')

    def test_shop_url_used_only_for_shop_button_and_support_line(self):
        # app.js reads it in exactly two places: the "Our Bookshop.org shop" button on the author Buy tab and the support line
        self.assertEqual(len(re.findall(r'AFF\.bookshopShop', self.app)), 3)  # the button's guard, its href, and support()'s var
        self.assertEqual(self.app.count('>Our Bookshop.org shop'), 1)
        self.assertEqual(self.app.count("esc(shop)"), 1)
        # the URL itself is written only in data/affiliates.js, never hard-coded in code, tools, or pages
        files = [ROOT / 'app.js', ROOT / 'index.html'] + list((ROOT / 'scripts').glob('*.js')) + list((ROOT / 'tools').glob('*.py'))
        for f in files:
            self.assertNotIn('bookshop.org/shop/', f.read_text(encoding='utf-8'), f.name)
        # the button sits next to the affiliate disclosure on the Buy tab
        i = self.app.index('>Our Bookshop.org shop')
        self.assertIn('discl()', self.app[i:i + 200])

    def test_shop_link_is_guarded(self):
        uses = [m.start() for m in re.finditer(r'AFF\.bookshopShop', self.app)]
        self.assertTrue(uses)
        self.assertIn("(AFF.bookshopShop?'<a class=\"btn ghost\" href=\"'+esc(AFF.bookshopShop)", self.app)
        self.assertIn("var shop=AFF.bookshopShop||''", self.app)
        self.assertIn("(shop?'<li><b>Buy books through our", self.app)

    def test_no_amazon(self):
        self.assertNotRegex(self.aff.lower(), r'amazon\.|amzn\.')


if __name__ == '__main__':
    unittest.main()
