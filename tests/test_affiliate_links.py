"""Affiliate preview (owner-approved for a preview, Business 2026-11-09): Bookshop.org ID 130222 links only for real
edition-guide ISBNs, "Browse TAN Books" through the referral link, the FTC disclosure beside every affiliate link,
the /disclosure/ page, no Amazon, the Substack sign-up on every page (the embed only on the home page and the Advent
plan), and no new analytics."""
import json, pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FTC = 'Some links are affiliate links. If you buy through them, Bibliotheca Catholica may earn a small commission at no extra cost to you. It helps keep the library free.'
SUBSCRIBE = 'https://bibliothecacatholica.substack.com/subscribe'
TAN = 'https://lddy.no/1qbrw'
LINE = 'Advent with the Fathers: a short reading from the Church Fathers each day, Nov 29 to Dec 24. Free.'


def pages():
    for line in (ROOT / 'docs/static-pages.txt').read_text().split():
        yield line, (ROOT / line).read_text(encoding='utf-8')
    yield 'index.html', (ROOT / 'index.html').read_text(encoding='utf-8')


def main_of(html):
    return html[html.index('<main'):html.index('</main>')]


def jsvar(path, var):
    s = (ROOT / path).read_text(encoding='utf-8'); p = 'window.%s=' % var
    return json.loads(s[s.index(p) + len(p):].rstrip().rstrip(';'))


class AffiliateLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = dict(pages())
        cls.aff = (ROOT / 'data/affiliates.js').read_text(encoding='utf-8')
        cls.pe = json.loads((ROOT / 'data/print-editions.json').read_text(encoding='utf-8'))
        guide = jsvar('data/guide.js', 'GUIDE_DATA')
        cls.isbns = {p['isbn'] for e in guide['editions'] for p in e.get('picks') or [] if p.get('isbn') and p.get('access') != 'ebook'}

    def test_config(self):
        self.assertRegex(self.aff, r"bookshopId:\s*'130222'")
        self.assertIn("tan: { name: 'TAN Books', url: '" + TAN + "'", self.aff)
        self.assertIn("disclosure: 'Affiliate disclosure: " + FTC + "'", self.aff)
        self.assertEqual(self.pe['bookshopId'], '130222')

    def test_bookshop_links_carry_the_id_and_a_real_isbn(self):
        n = 0
        for name, html in self.pages.items():
            for m in re.finditer(r'href="https?://(?:www\.)?bookshop\.org/a/([^/"]+)/([^/"]*)"', html):
                n += 1
                self.assertEqual(m.group(1), '130222', name)
                self.assertRegex(m.group(2), r'^97[89]\d{10}$', name)
                self.assertIn(m.group(2), self.isbns, name + ': ISBN not in an edition guide')
        self.assertGreater(n, 50)

    def test_work_pages_get_purchase_blocks_after_free_reading(self):
        works = self.pe['works']
        self.assertIn('orthodoxy', works); self.assertTrue(works['orthodoxy']['bookshop']); self.assertTrue(works['orthodoxy']['tan'])
        self.assertGreaterEqual(sum(1 for v in works.values() if v['bookshop']), 15)
        for wid, v in works.items():
            html = main_of(self.pages['work/%s/index.html' % wid])
            self.assertIn(v['html'], html, wid)
            self.assertLess(html.index('Reading editions &amp; sources'), html.index('Where to buy print editions'), wid)
        # never on related (non-Catholic) writers' books, Magisterium documents, or reference works
        lib = json.loads((ROOT / 'data/library.json').read_text())
        rel = {w for ra in lib['relatedAuthors'] for w in ra['workIds']}
        for w in lib['works']:
            if w['id'] in rel or w['category'] in ('Magisterium', 'Reference'):
                self.assertFalse(works.get(w['id'], {}).get('tan'), w['id'])
        self.assertIn('g-k-chesterton', self.pe['authors'])
        self.assertIn(TAN, main_of(self.pages['author/g-k-chesterton/index.html']))

    def test_disclosure_beside_every_affiliate_link(self):
        for name, html in self.pages.items():
            m = main_of(html)
            for sec in re.findall(r'<section class="buy-print">.*?</section>', m):
                self.assertIn(FTC, sec, name); self.assertIn('href="/disclosure/"', sec, name)
            if re.search(r'bookshop\.org/a/|lddy\.no', m):
                self.assertIn(FTC, m, name)
            # the TAN link is only the general store link, never a claim about a title
            for t in re.findall(r'<a [^>]*href="https://lddy\.no/1qbrw"[^>]*>([^<]*)</a>', m):
                self.assertEqual(t, 'Browse TAN Books ↗', name)

    def test_affiliate_links_are_plain_and_sponsored(self):
        for name, html in self.pages.items():
            for a in re.findall(r'<a [^>]*href="(?:https://bookshop\.org/a/|https://lddy\.no/)[^>]*>', main_of(html)):
                self.assertIn('rel="noopener sponsored"', a, name)
                self.assertNotRegex(a, r'data-(support|ga|track|event)', name)

    def test_libraries_page_uses_tan_referral_link(self):
        m = main_of(self.pages['libraries/index.html'])
        self.assertIn('TAN Books', m)
        texts = re.findall(r'<a [^>]*href="https://lddy\.no/1qbrw"[^>]*>([^<]*)</a>', m)
        self.assertEqual(texts, ['Browse TAN Books ↗'])
        self.assertIn('rel="noopener sponsored"', re.search(r'<a [^>]*href="https://lddy\.no/1qbrw"[^>]*>', m).group(0))
        self.assertIn(FTC, m)
        self.assertIn('href="/disclosure/"', m)
        self.assertNotIn('https://tanbooks.com/', m)
        hub = json.loads((ROOT / 'data/catholic-hub.json').read_text())
        tan = [r for r in hub['resources'] if r['name'] == 'TAN Books' and r['category'] == 'Publishers']
        self.assertEqual(len(tan), 1)
        self.assertEqual(tan[0]['url'], TAN)

    def test_disclosure_page(self):
        html = self.pages['disclosure/index.html']
        self.assertIn('<h1>Affiliate disclosure</h1>', html)
        self.assertIn('<meta name="robots" content="index,follow">', html)
        self.assertIn('https://bibliothecacatholica.com/disclosure/', (ROOT / 'sitemap.xml').read_text())
        for s in ('Bookshop.org', 'TAN Books', 'lddy.no', FTC, 'Commissions never decide'):
            self.assertIn(s, html)
        self.assertEqual(html.count('googletagmanager.com/gtag/js'), 1)
        self.assertIn("'disclosure'", (ROOT / 'app.js').read_text())

    def test_footer_on_every_page(self):
        for name, html in self.pages.items():
            foot = html[html.index('<footer'):]
            self.assertIn('<a href="/disclosure/">Affiliate disclosure</a>', foot, name)
            self.assertIn(FTC, foot, name)
            self.assertIn('<a class="btn nl-btn" href="' + SUBSCRIBE + '"', foot, name)
            self.assertIn(LINE, foot, name)
            self.assertIn('data-support="footer"', foot, name)  # donation link
            self.assertIn('href="/support/"', foot, name)

    def test_substack_embed_only_on_home_and_advent(self):
        with_embed = {n for n, h in self.pages.items() if '<iframe' in h}
        self.assertEqual(with_embed, {'index.html', 'reading/advent-2026/index.html'})
        for n in with_embed:
            f = re.search(r'<iframe [^>]*>', self.pages[n]).group(0)
            self.assertIn('src="https://bibliothecacatholica.substack.com/embed"', f)
            for attr in ('loading="lazy"', 'title="', 'class="nl-embed"'):
                self.assertIn(attr, f)
        css = (ROOT / 'styles.css').read_text()
        self.assertRegex(css, r'\.newsletter-box \.nl-embed\{[^}]*max-width:480px[^}]*\}')
        self.assertIn('width:100%', re.search(r'\.newsletter-box \.nl-embed\{[^}]*\}', css).group(0))

    def test_no_amazon(self):
        files = [ROOT / 'app.js', ROOT / 'index.html', ROOT / 'data/affiliates.js', ROOT / 'data/print-editions.js'] + list((ROOT / 'scripts').glob('*.js'))
        for f in files:
            self.assertNotRegex(f.read_text(encoding='utf-8').lower(), r'amazon\.|amzn\.', f.name)
        for name, html in self.pages.items():
            if name.startswith('guides/'):
                continue  # the EPUB guide may link Amazon help pages only (tests/test_epub_guide.py)
            self.assertNotRegex(html.lower(), r'href="[^"]*(amazon\.|amzn\.)', name)

    def test_copy_style(self):
        import sys; sys.path.insert(0, str(ROOT / 'tools')); import site_copy
        for s in (site_copy.disclosure_page(FTC), site_copy.newsletter_box(), LINE, json.dumps(self.pe, ensure_ascii=False)):
            self.assertNotIn('—', s)
            self.assertNotRegex(s.lower(), r'tax[- ]deductible')

    def test_privacy_mentions_substack_and_affiliate(self):
        pol = self.pages['policy/index.html']
        self.assertIn('The newsletter sign-up form on the home page and the Advent reading plan is provided by Substack under its own', pol)
        self.assertIn('affiliate (a referral link', pol)

    def test_agents_md_rules(self):
        t = (ROOT / 'docs/IMPLEMENTATION-NOTES.md').read_text() + (ROOT / 'docs/PROJECT-RULES.md').read_text()
        self.assertIn('docs/PROJECT-RULES.md', (ROOT / 'AGENTS.md').read_text())
        self.assertIn('Affiliate links (2026-11-09', t)
        self.assertIn('`affiliate` (lddy.no', t)


if __name__ == '__main__':
    unittest.main()
