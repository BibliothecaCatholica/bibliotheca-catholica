"""Affiliate config: Bookshop ID stays 130222, the unconfirmed shop URL stays blank, and the UI hides the shop link when it is blank."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


class AffiliateTests(unittest.TestCase):
    def setUp(self):
        self.aff = (ROOT / 'data/affiliates.js').read_text(encoding='utf-8')
        self.app = (ROOT / 'app.js').read_text(encoding='utf-8')

    def test_bookshop_id(self):
        self.assertRegex(self.aff, r"bookshopId:\s*'130222'")

    def test_shop_url_blank_until_owner_confirms(self):
        m = re.search(r"bookshopShop:\s*'([^']*)'", self.aff)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), '', 'bookshopShop stays blank until the owner confirms the real shop URL')
        self.assertNotIn('bookshop.org/shop/bibliotheca-catholica', self.app)

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
