"""The "Sources and credits" page (/credits/) and the colophon at the end of each book (owner direction, November 15, 2026;
docs/PROJECT-RULES.md rules 2, 10, and 11; docs/DESIGN.md "Notices"). Credits leave the reading and author pages for one
page generated from data; every item keeps its full credit there, and each page links to it. Nothing is deleted."""
import json, re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import credits_page as CP  # noqa: E402
R = lambda p: (ROOT / p).read_text(encoding='utf-8')
def main(s): return s[s.index('<main'):s.index('</main>')]
PAGE = R('credits/index.html')
CREDITS = main(PAGE)
LIB = json.loads(R('data/library.json'))
HUB = json.loads(R('data/catholic-hub.json'))


class CreditsPage(unittest.TestCase):
    def test_page_is_built_listed_and_linked_from_the_footer(self):
        self.assertIn('<h1>Sources and credits</h1>', CREDITS)
        self.assertEqual(PAGE.count('G-HFG445Y1LT'), R('about/index.html').count('G-HFG445Y1LT'))  # one GA4 tag, as on every page
        self.assertIn('<loc>https://bibliothecacatholica.com/credits/</loc>', R('sitemap.xml'))
        for p in ('index.html', 'about/index.html', 'credits/index.html'):
            self.assertIn('<a href="/credits/">Sources &amp; credits</a>', R(p), p)
        self.assertIn("if(path==='credits')return true;", R('app.js'))  # the app keeps the static page as the view
        self.assertNotIn('—', ''.join(re.findall(r"'([^']*)'", R('tools/credits_page.py'))))  # our copy: no em-dashes

    def test_every_hosted_edition_has_a_full_record(self):
        for w in LIB['works']:
            for e in w['editions']:
                if not e.get('text'):
                    continue
                with self.subTest(e['id']):
                    m = re.search(r'<section class="credit-record" id="ed-' + re.escape(e['id']) + r'">(.*?)</section>', CREDITS, re.S)
                    self.assertTrue(m)
                    rec = m.group(1)
                    for k in ('Rights', 'Basis', 'Source', 'Source record', 'SHA-256', 'Checks', 'Checked'):
                        self.assertIn('<dt>' + k + '</dt>', rec)
                    self.assertIn('<code>' + e['sha256'] + '</code>', rec)
                    self.assertIn(CP.PROVENANCE + e['id'] + '.json', rec)
                    if e.get('rightsEvidence'):
                        self.assertIn('<dt>Evidence</dt>', rec)
                    if e.get('retired'):
                        self.assertIn('href="#ed-' + e['retired']['replacedBy'] + '"', rec)

    def test_every_book_ends_with_its_colophon(self):
        tp = json.loads(R('data/text-pages.json'))['works']
        for wid, d in tp.items():
            last = d['items'][-1]
            s = main(R('work/' + wid + '/' + d['kind'] + '/' + last['slug'] + '/index.html'))
            with self.subTest(wid):
                self.assertEqual(s.count('class="small colophon"'), 1)
                self.assertIn('href="/credits/#ed-' + d['edition'] + '"', s)
                self.assertLess(s.index('class="small pg-notice"'), s.index('class="small colophon"'))  # after the source's notice
            first = main(R('work/' + wid + '/' + d['kind'] + '/' + d['items'][0]['slug'] + '/index.html'))
            if len(d['items']) > 1:
                self.assertNotIn('class="small colophon"', first, wid)  # once, at the end of the book
        lj = R('scripts/library.js')  # the reading room: every hosted edition, after the last section's notice
        self.assertIn("'<div class=\"reader-notices\">'+sourceNotice(e,true)+colophon(e)+'</div>'", lj)
        self.assertIn("<a href=\"/credits/#ed-'+esc(e.id)+'\">Full record in Sources and credits</a>", lj)
        for k, v in CP.BASIS.items():
            self.assertIn("'" + k + "':'" + v + "'", lj)  # the same words in both builders

    def test_portraits_keep_their_full_credit_on_the_credits_page(self):
        app = R('app.js')
        self.assertIn('<a href="/credits/#portrait-\'+esc(a.id)+\'">Image credit</a>', app)
        self.assertNotIn("'Portrait: '", app)
        n = 0
        for a in HUB['authors']:
            if not (a.get('img') and a.get('imgCredit')):
                continue
            n += 1
            c = a['imgCredit']
            with self.subTest(a['id']):
                m = re.search(r'<li id="portrait-' + re.escape(a['id']) + r'">(.*?)</li>', CREDITS)
                self.assertTrue(m)
                self.assertIn('href="' + c['page'].replace('&', '&amp;') + '"', m.group(1))
                if c.get('licenseUrl'):
                    self.assertIn('href="' + c['licenseUrl'].replace('&', '&amp;') + '"', m.group(1))
        self.assertGreater(n, 300)

    def test_unchanged_notices_stay_where_they_are(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        from notices import PG_LINE
        tp = json.loads(R('data/text-pages.json'))['works']
        pg = next(wid for wid, d in tp.items() if 'gutenberg.org' in next(e for w in LIB['works'] if w['id'] == wid for e in w['editions'] if e['id'] == d['edition'])['source'])
        d = tp[pg]
        self.assertIn(PG_LINE, R('work/' + pg + '/' + d['kind'] + '/' + d['items'][-1]['slug'] + '/index.html'))  # the Gutenberg sentence
        works = [p for p in (ROOT / 'work').glob('*/index.html') if 'bookshop.org' in p.read_text()]
        self.assertTrue(works)
        self.assertTrue(all('Affiliate links' in main(p.read_text()) for p in works))  # the FTC line beside affiliate links
        self.assertIn('<a href="/takedown/">Takedown requests</a>', R('index.html'))  # the takedown link
        self.assertTrue(any('<div class="ef-h">Context note</div>' in p.read_text() for p in (ROOT / 'author').glob('*/index.html')))
        self.assertIn('<p class="hero-credit">', R('index.html'))  # the home engraving keeps its line; its entry is on /credits/ too
        self.assertIn('id="home-engraving"', CREDITS)


    def test_counts_agree_with_their_nouns(self):
        # QA, November 21, 2026: "1 OCR confusions" and "1 paragraphs" (Do We Agree?)
        self.assertEqual([CP.plural(n, 'paragraph') for n in (0, 1, 2, 1204)], ['0 paragraphs', '1 paragraph', '2 paragraphs', '1,204 paragraphs'])
        self.assertEqual(CP.plural(1, 'OCR confusion'), '1 OCR confusion')
        text = re.sub(r'<[^>]+>', ' ', main(PAGE))
        self.assertEqual(re.findall(r'(?<![\d,.])1 (?:OCR confusions|paragraphs|misreadings|words)\b', text), [])
        self.assertIn('1 OCR confusion repaired', text)

if __name__ == '__main__':
    unittest.main()
