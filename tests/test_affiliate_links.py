"""Affiliate preview (owner-approved for a preview, Business 2026-11-09): Bookshop.org ID 130222 links only for real
edition-guide ISBNs, "Browse TAN Books" through the referral link, the one-line FTC disclosure once per page beside the links,
the /disclosure/ page, no Amazon, the Substack sign-up on every page (the embed only on the Advent plan; a Subscribe button on the home page), and no new analytics."""
import json, pathlib, re, unittest
from html import escape as html_escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
FTC = 'Some links are affiliate links. If you buy through them, Bibliotheca Catholica may earn a small commission at no extra cost to you. It helps keep the library free.'
SUBSCRIBE = 'https://bibliothecacatholica.substack.com/subscribe'
TAN = 'https://lddy.no/1qbrw'
MAG = 'https://www.magisterium.com/pro/micah'
MAG_LINE = 'We earn a commission if you subscribe through this link.'
DLINE = '<p class="disclosure small">Affiliate links: we may earn a commission. <a href="/disclosure/">Details</a>.</p>'  # rule 7, November 14, 2026
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
        self.assertIn("magisterium: { name: 'Magisterium AI', url: '" + MAG + "'", self.aff)
        self.assertIn("disclosure: 'Affiliate disclosure: " + FTC + "'", self.aff)  # the fuller statement on /disclosure/
        self.assertIn("line: 'Affiliate links: we may earn a commission.'", self.aff)
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
            self.assertLess(html.index('Reading editions &amp; sources'), html.index('<h2>Buy in print</h2>'), wid)
        # never on related (non-Catholic) writers' books, Magisterium documents, or reference works
        lib = json.loads((ROOT / 'data/library.json').read_text())
        rel = {w for ra in lib['relatedAuthors'] for w in ra['workIds']}
        for w in lib['works']:
            if w['id'] in rel or w['category'] in ('Magisterium', 'Reference'):
                self.assertFalse(works.get(w['id'], {}).get('tan'), w['id'])
        self.assertIn('g-k-chesterton', self.pe['authors'])
        self.assertIn(TAN, main_of(self.pages['author/g-k-chesterton/index.html']))

    def test_disclosure_beside_every_affiliate_link(self):
        # rule 7 (owner, November 14, 2026): one line beside the links, "Details" to /disclosure/, once per page
        for name, html in self.pages.items():
            m = main_of(html)
            if name != 'disclosure/index.html' and re.search(r'href="https://(?:bookshop\.org/a/|lddy\.no)', m):
                self.assertEqual(m.count(DLINE), 1, name)
                first = re.search(r'href="https://(?:bookshop\.org/a/|lddy\.no)', m).start()
                self.assertLess(abs(m.index(DLINE) - first), 6000, name + ': the line sits beside the links')
            self.assertLessEqual(m.count('class="disclosure'), 1, name)
            self.assertNotIn(FTC, m if name != 'disclosure/index.html' else '', name)
            # the TAN link is only the general store link, never a claim about a title
            for t in re.findall(r'<a [^>]*href="https://lddy\.no/1qbrw"[^>]*>([^<]*)</a>', m):
                self.assertEqual(t, 'Browse TAN Books ↗', name)

    def test_exactly_one_disclosure_line_per_page(self):
        # rule 7: every page with an affiliate link has the one-line disclosure exactly once; pages without one have none
        study = (ROOT / 'study/index.html').read_text(encoding='utf-8')
        aff = r'href="https://(?:bookshop\.org/a/|lddy\.no/|www\.magisterium\.com/)'
        n = 0
        for name, html in dict(self.pages, **{'study/index.html': study}).items():
            m = main_of(html)
            if name == 'disclosure/index.html':
                continue
            has = bool(re.search(aff, m)); n += has
            self.assertEqual(m.count(DLINE), 1 if has else 0, name)
            self.assertEqual(m.count('class="disclosure'), 1 if has else 0, name)
        self.assertGreater(n, 200)

    def test_one_disclosure_size(self):
        # DESIGN.md "Notices": the smallest legible size, 14 px (--t-xs), the same on every page
        css = (ROOT / 'styles.css').read_text(encoding='utf-8')
        self.assertIn('.disclosure{font:400 var(--t-xs)/1.45 var(--sans);', css)
        self.assertIn('--t-xs:14px', css)
        # container paragraph rules must not restyle the line: the panels exclude it explicitly
        self.assertIn('.study-partner p:not(.disclosure){', css)
        self.assertNotRegex(css, r'\.study-partner p\{')
        sheets = [ROOT / 'styles.css'] + list((ROOT / 'styles').glob('*.css')) + list((ROOT / 'assets').glob('*/*.css'))
        for f in sheets:
            for sel, body in re.findall(r'([^{}]*\.disclosure[^{}]*)\{([^}]*)\}', f.read_text(encoding='utf-8')):
                if sel.strip() == '.disclosure' or ':not(.disclosure)' in sel:
                    continue  # the one rule that sets the size, and rules that exclude the line
                self.assertNotRegex(body, r'font(-size)?\s*:', f.name + ' ' + sel.strip())

    def test_affiliate_links_are_plain_and_sponsored(self):
        for name, html in self.pages.items():
            for a in re.findall(r'<a [^>]*href="(?:https://bookshop\.org/a/|https://lddy\.no/|https://www\.magisterium\.com/)[^>]*>', main_of(html)):
                self.assertIn('rel="noopener sponsored"', a, name)
                self.assertNotRegex(a, r'data-(support|ga|track|event)', name)

    def test_libraries_page_uses_tan_referral_link(self):
        m = main_of(self.pages['libraries/index.html'])
        self.assertIn('TAN Books', m)
        texts = re.findall(r'<a [^>]*href="https://lddy\.no/1qbrw"[^>]*>([^<]*)</a>', m)
        self.assertEqual(texts, ['Browse TAN Books ↗'])
        self.assertIn('rel="noopener sponsored"', re.search(r'<a [^>]*href="https://lddy\.no/1qbrw"[^>]*>', m).group(0))
        self.assertIn(DLINE, m)
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
        for s in ('Bookshop.org', 'TAN Books', 'lddy.no', 'Magisterium AI', MAG, FTC, 'Commissions never decide', 'not a donation to the library'):
            self.assertIn(s, html)
        self.assertEqual(html.count('googletagmanager.com/gtag/js'), 1)
        self.assertIn("'disclosure'", (ROOT / 'app.js').read_text())

    def test_footer_on_every_page(self):
        for name, html in self.pages.items():
            foot = html[html.index('<footer'):]
            self.assertIn('<a href="/disclosure/">Affiliate disclosure</a>', foot, name)
            # design pass (owner-approved 2026-11-12): the FTC line sits only beside affiliate links, not in the footer
            self.assertNotIn(FTC, foot, name)
            self.assertIn('<a class="nl-btn" href="' + SUBSCRIBE + '"', foot, name)
            self.assertEqual(html.count(LINE), 1, name)  # the newsletter pitch appears once per page
            self.assertIn(LINE, foot, name)
            self.assertIn('data-support="footer"', foot, name)  # donation link
            self.assertIn('href="/support/"', foot, name)

    def test_substack_embed_only_on_home_and_advent(self):
        with_embed = {n for n, h in self.pages.items() if '<iframe' in h}
        self.assertEqual(with_embed, {'reading/advent-2026/index.html'})  # the home page has a button instead (2026-11-19)
        home = main_of(self.pages['index.html'])
        btn = re.search(r'<section class="newsletter-box nl-home".*?</section>', home, re.S).group(0)
        self.assertIn('<a class="btn ghost" href="' + SUBSCRIBE + '" target="_blank" rel="noopener">Subscribe ↗</a>', btn)  # the hero keeps the one filled button
        self.assertNotRegex(btn, r'data-(support|ga|track|event)|onclick')
        self.assertIn("(SC.homeNewsletter||'')", (ROOT / 'app.js').read_text(encoding='utf-8'))
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
        self.assertIn('The newsletter sign-up form on the Advent reading plan is provided by Substack under its own', pol)
        self.assertIn('affiliate (a referral link', pol)
        self.assertIn('Some links to Bookshop.org, TAN Books, and Magisterium AI are affiliate links', pol)
        self.assertIn('The “Search another collection” form on the <a href="/libraries/">Libraries</a> page sends what you type to Open Library', pol)

    def test_magisterium_on_libraries(self):
        # #70: /libraries/ keeps its own wording, with sponsored rel and the commission line beside the link; not a donation
        m = main_of(self.pages['libraries/index.html'])
        a = re.search(r'<a [^>]*href="' + re.escape(MAG) + r'"[^>]*>', m).group(0)
        self.assertIn('rel="noopener sponsored"', a)
        self.assertIn('target="_blank"', a)
        self.assertIn('Try Magisterium AI Pro ↗', m)
        self.assertNotIn(MAG_LINE, m)  # one disclosure line per page (rule 7); the fuller statement is on /disclosure/
        self.assertIn('Readers who subscribe to Pro through this link get 25% off', m)
        sec = re.search(r'<section class="library-affiliate".*?</section>', m, re.S).group(0)
        self.assertEqual(sec.count(DLINE), 1)  # the page's one line sits beside its first affiliate link
        self.assertEqual(m.count('class="disclosure'), 1)
        app = (ROOT / 'app.js').read_text(encoding='utf-8')
        self.assertIn("$('#rs-q').closest('.toolbar').before(box);oneDiscl();", app)  # the lazy desk keeps one line in the app too
        self.assertNotIn('donation', m.lower())
        self.assertNotIn('support the library', m.lower())

    def test_magisterium_allowlist(self):
        # rule 7 (owner-approved placements, November 19, 2026, extended 21 November 2026): the referral is on the
        # pages in study_partner.placement_files() only. Advent plan pages stay off the list for the freeze.
        import sys; sys.path.insert(0, str(ROOT / 'tools')); import study_partner as SP
        self.assertEqual(SP.partner(), ('Magisterium AI', MAG))  # read from partners.magisterium in data/affiliates.js
        study = (ROOT / 'study/index.html').read_text(encoding='utf-8')
        allp = dict(self.pages, **{'study/index.html': study})
        hits = {n for n, h in allp.items() if MAG in h}
        self.assertEqual(hits, SP.placement_files())
        self.assertIn('index.html', hits)  # home Ask block, 21 November 2026
        self.assertTrue(hits >= {'work/confessions/index.html', 'work/orthodoxy/index.html', 'work/dei-verbum/index.html'})
        for name, html in allp.items():
            head = html[:html.index('<main')] if '<main' in html else html
            self.assertNotIn(MAG, head, name + ': header')
            self.assertNotIn(MAG, html[html.index('<footer'):], name + ': footer')
            if name.startswith('author/') or '/ch/' in name or '/story/' in name or re.match(r'summa/[^/]+/', name) or name.startswith('reading/advent'):
                self.assertNotIn(MAG, html, name)
        after = {'magisterium': '</ul>', 'councils': 'class="council-note', 'summa': 'class="dl-row"', 'study': 'id="scans"'}
        for r in SP.PANEL_ROUTES:
            m = main_of(allp[r + '/index.html'])
            self.assertEqual(m.count('class="study-partner"'), 1, r)  # one panel, no repeats
            if r == 'magisterium':
                self.assertGreater(m.count(MAG), 1, r)  # the panel link plus Ask buttons beside vatican.va links
            else:
                self.assertEqual(m.count(MAG), 1, r)
            panel = re.search(r'<aside class="study-partner".*?</aside>', m, re.S).group(0)
            self.assertEqual(panel.count(MAG), 1, r)  # the panel itself still has one referral link
            self.assertIn('<h2 id="study-partner-h">Study with Magisterium AI</h2>', panel)
            self.assertEqual(re.findall(r'<a [^>]*href="' + re.escape(MAG) + r'"[^>]*>([^<]*)</a>', panel), ['Try Magisterium AI Pro ↗'], r)
            a = re.search(r'<a [^>]*href="' + re.escape(MAG) + r'"[^>]*>', panel).group(0)
            self.assertIn('rel="noopener sponsored"', a); self.assertIn('target="_blank"', a)
            self.assertNotRegex(a, r'data-(support|ga|track|event)', r)
            self.assertEqual(panel.count(DLINE), 1, r); self.assertEqual(m.count('class="disclosure'), 1, r)  # once per page
            self.assertLess(m.index(after[r]), m.index(panel), r + ': below the free reading options')
            copy = re.findall(r'<p>([^<]*)</p>', panel)[0]
            self.assertEqual(copy, html_escape(SP.COPY[r]))
            self.assertIn(len(re.findall(r'(?<!\bSt)[.!?](?:\s|$)', copy)), (1, 2), r)  # 'St.' does not end a sentence
            for bad in ('—', 'donat', '<iframe', 'onclick', 'position:fixed', 'banner'):
                self.assertNotIn(bad, panel.lower(), r)
        # the app renders /magisterium/ itself: the same panel from SITE_COPY, after the resource rows
        sc = jsvar('data/site-copy.js', 'SITE_COPY')
        self.assertEqual(sc['studyPartner'], SP.panel('magisterium'))
        app = (ROOT / 'app.js').read_text(encoding='utf-8')
        self.assertIn("(k==='magisterium'?(SC.studyPartner||''):'')+((SC.studyAsks&&SC.studyAsks[k])||'')", app)
        # never hard-coded: the URL lives only in data/affiliates.js (and the pages built from it)
        for f in list((ROOT / 'tools').glob('*.py')) + [ROOT / 'app.js'] + list((ROOT / 'scripts').glob('*.js')):
            self.assertNotIn(MAG, f.read_text(encoding='utf-8'), f.name)
        # no affiliate link in the open data; entry 70 keeps its neutral catalogue description
        proj = jsvar('data/projects.js', 'PROJECTS_DATA')
        e70 = next(x for x in proj['items'] if x['id'] == 70)
        self.assertEqual(e70['d'], 'A Catholic AI assistant that answers from Church documents with citations.')
        for f in [ROOT / 'data/projects.js', ROOT / 'data/library.json'] + list((ROOT / 'data/open').glob('*')):
            if f.is_file():
                s = f.read_text(encoding='utf-8', errors='ignore')
                self.assertNotIn('magisterium.com/pro', s, f.name); self.assertNotIn('via=micah', s, f.name)

    def test_support_names_the_tool_apart_from_donations(self):
        sc = jsvar('data/site-copy.js', 'SITE_COPY')
        note = sc['supportTools']
        self.assertIn('<h2 class="sup-h">Tools we support</h2>', note)
        self.assertIn('Magisterium AI', note)
        self.assertNotIn(MAG, note); self.assertNotIn('sponsored', note)  # no referral link on /support/
        self.assertIn('not a donation to the library', note)
        self.assertIn('The only way to donate is PayPal', note)
        app = (ROOT / 'app.js').read_text(encoding='utf-8')
        sup = app[app.index('function support()'):app.index("render(h,'support')}")]
        self.assertLess(sup.index('Donate with PayPal'), sup.index('SC.supportTools'))
        self.assertLess(sup.index('Other ways to help'), sup.index('SC.supportTools'))
        self.assertEqual(re.findall(r"var SUPPORT=\{([a-z]+):", app), ['paypal'])  # PayPal stays the only donation option
        self.assertNotIn('buymeacoffee', app.lower())

    def test_disclosure_lists_every_magisterium_page(self):
        html = main_of(self.pages['disclosure/index.html'])
        para = html[html.index('<h2>Magisterium AI</h2>'):]
        para = para[:para.index('</p>')]
        for href in ('/', '/scripture/', '/libraries/', '/magisterium/', '/councils/', '/summa/', '/study/',
                     '/saints/', '/doctors/', '/prayers/', '/about/magisterium-ai/', '/work/confessions/', '/work/orthodoxy/'):
            self.assertIn('href="' + href + '"', para, href)
        self.assertIn(MAG, para)

    def test_agents_md_rules(self):
        t = ''.join((ROOT / f).read_text() for f in ('docs/IMPLEMENTATION-NOTES.md', 'docs/PROJECT-RULES.md', 'docs/ANALYTICS.md'))
        self.assertIn('docs/PROJECT-RULES.md', (ROOT / 'AGENTS.md').read_text())
        self.assertIn('**Affiliate links (owner-approved).**', t)
        self.assertIn('`affiliate` (lddy.no', t)


if __name__ == '__main__':
    unittest.main()
