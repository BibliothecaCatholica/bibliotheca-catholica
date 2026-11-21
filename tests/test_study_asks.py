"""Ask Magisterium AI blocks, Ask-about-this-book questions, the Why page, and vatican.va Ask buttons
(owner-approved draft, 21 November 2026)."""
import pathlib, re, sys, unittest
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import study_partner as SP

MAG = 'https://www.magisterium.com/pro/micah'
DLINE = '<p class="disclosure small">Affiliate links: we may earn a commission. <a href="/disclosure/">Details</a>.</p>'


def main_of(html):
    return html[html.index('<main'):html.index('</main>')]


def read_page(path):
    return (ROOT / path).read_text(encoding='utf-8')


class StudyAskTests(unittest.TestCase):
    def test_questions_are_our_own_words_and_not_prefilled(self):
        for route, qs in SP.QUESTIONS.items():
            self.assertGreaterEqual(len(qs), 3, route)
            self.assertLessEqual(len(qs), 4, route)
            for q in qs:
                self.assertTrue(q.endswith('?'), q)
                self.assertNotIn('\u2014', q)
                self.assertNotIn('?q=', q)
        for wid, qs in SP.BOOK_QUESTIONS.items():
            self.assertGreaterEqual(len(qs), 3, wid)
            self.assertLessEqual(len(qs), 4, wid)
            for q in qs:
                self.assertTrue(q.endswith('?'), q)
                self.assertNotIn('\u2014', q)

    def test_section_ask_blocks_on_static_pages(self):
        mapping = {
            'index.html': ('home', 'What does the Church teach about the relationship between Scripture and Tradition?'),
            'scripture/index.html': ('scripture', 'What is the Catholic sense of this passage, and which Church documents discuss it?'),
            'saints/index.html': ('saints', 'Who was St. Francis de Sales, and what did he write?'),
            'doctors/index.html': ('doctors', 'What does it mean for the Church to name someone a Doctor of the Church?'),
            'prayers/index.html': ('prayers', 'How does the Church teach us to pray the Rosary, and what are the mysteries?'),
        }
        for path, (route, sample) in mapping.items():
            m = main_of(read_page(path))
            self.assertIn(SP.ask_block(route), m, path)
            self.assertIn(sample, m, path)
            self.assertIn('Questions to ask Magisterium AI', m, path)
            self.assertIn('the question is not filled in for you', m, path)
            self.assertIn(SP.INDEPENDENT, m, path)
            self.assertIn('href="/about/magisterium-ai/"', m, path)
            self.assertIn(MAG, m, path)
            self.assertNotIn('?q=', m, path)
            self.assertEqual(m.count(DLINE), 1, path)
            self.assertNotIn('/reading/advent-2026/', SP.ask_block(route))

    def test_advent_freeze_is_untouched(self):
        self.assertNotIn('advent', ' '.join(SP.ASK_ROUTES))
        adv = ROOT / 'reading/advent-2026/index.html'
        if adv.exists():
            self.assertNotIn(MAG, adv.read_text(encoding='utf-8'))

    def test_existing_panels_gain_questions_but_keep_one_link(self):
        for r in ('magisterium', 'councils', 'summa', 'study'):
            path = r + '/index.html'
            m = main_of(read_page(path))
            panel = re.search(r'<aside class="study-partner".*?</aside>', m, re.S).group(0)
            self.assertEqual(panel, SP.panel(r), r)
            self.assertIn('Questions to ask Magisterium AI', panel, r)
            for q in SP.QUESTIONS[r]:
                self.assertIn(q, unescape(panel), r)
            self.assertEqual(panel.count(MAG), 1, r)
            self.assertIn(SP.INDEPENDENT, panel, r)

    def test_book_questions_on_major_works(self):
        for wid, sample in (
            ('confessions', 'What does Augustine mean when he says our heart is restless until it rests in God?'),
            ('orthodoxy', 'What does Chesterton mean by the romance of orthodoxy?'),
            ('dei-verbum', 'What does Dei Verbum teach about divine revelation?'),
            ('lumen-gentium', "What does Lumen Gentium teach about the mystery of the Church?"),
            ('sacrosanctum-concilium', 'What does Sacrosanctum Concilium teach about the liturgy as the work of Christ and the Church?'),
            ('gaudium-spes', "What does Gaudium et Spes say about the Church's relationship to the modern world?"),
            ('council-of-trent', 'How did the Council of Trent describe justification?'),
        ):
            m = main_of(read_page('work/%s/index.html' % wid))
            self.assertIn('Ask about this book', m, wid)
            self.assertIn(sample, unescape(m), wid)
            self.assertIn(MAG, m, wid)
            self.assertNotIn('?q=', m, wid)
            self.assertEqual(m.count(DLINE), 1, wid)
            self.assertEqual(m.count('class="disclosure'), 1, wid)
            # questions belong on the work page, not on a chapter page
            ch = list((ROOT / 'work' / wid / 'ch').glob('*/index.html')) if (ROOT / 'work' / wid / 'ch').exists() else []
            if ch:
                self.assertNotIn(MAG, ch[0].read_text(encoding='utf-8'), ch[0])

    def test_why_page(self):
        html = read_page('about/magisterium-ai/index.html')
        m = main_of(html)
        self.assertIn(SP.why_page(), m)
        self.assertIn('Why we use Magisterium AI', m)
        self.assertIn(SP.INDEPENDENT, m)
        self.assertIn('not endorsed', m.lower())
        self.assertIn('Longbeard Inc.', m)
        self.assertIn('checked against the sources they cite', m)
        self.assertIn('not official Church teaching', m)
        self.assertIn('may receive a commission', m)
        self.assertIn('no extra cost to you', m)
        self.assertIn('href="/disclosure/"', m)
        self.assertIn(MAG, m)
        self.assertNotIn('\u2014', m)
        self.assertNotIn('tax-deductible', m.lower())
        # the referral is in the page body, never the header or footer
        self.assertNotIn(MAG, html[:html.index('<main')])
        self.assertNotIn(MAG, html[html.index('<footer'):])

    def test_ask_buttons_beside_vatican_links_on_church_documents(self):
        m = main_of(read_page('magisterium/index.html'))
        self.assertIn(SP.ask_button(), m)
        # every vatican.va resource on this page has an Ask button in the same list item
        # only the Church Documents resource list, not the suggested questions
        res = re.search(r'<ul>(.*?)</ul>\s*(?:<aside class="study-partner"|<p class="disclosure)', m, re.S)
        self.assertTrue(res)
        items = re.findall(r'<li>.*?</li>', res.group(1), re.S)
        vat = [li for li in items if 'href="https://www.vatican.va' in li or 'href="https://vatican.va' in li]
        self.assertGreaterEqual(len(vat), 8)
        for li in vat:
            self.assertIn('class="study-ask-btn"', li)
            self.assertIn(MAG, li)
            self.assertIn('rel="noopener sponsored"', li)
        # other section resource lists do not get the buttons
        scripture = main_of(read_page('scripture/index.html'))
        self.assertNotIn('class="study-ask-btn"', scripture)

    def test_site_copy_exports_and_no_hardcoded_url_in_sources(self):
        sc = (ROOT / 'data' / 'site-copy.js').read_text(encoding='utf-8')
        self.assertIn('whyMagisterium', sc)
        self.assertIn('studyAsks', sc)
        self.assertIn('bookAsks', sc)
        self.assertIn('askButton', sc)
        self.assertIn(MAG, sc)
        for path in list((ROOT / 'tools').glob('*.py')) + [ROOT / 'app.js'] + list((ROOT / 'scripts').glob('*.js')):
            self.assertNotIn(MAG, path.read_text(encoding='utf-8'), path.name)

    def test_copy_avoids_em_dashes_and_donation_language(self):
        blob = ' '.join(SP.ASK_COPY.values()) + ' '.join(q for qs in list(SP.QUESTIONS.values()) + list(SP.BOOK_QUESTIONS.values()) for q in qs)
        blob += SP.INDEPENDENT + SP.QS_INTRO + SP.why_page()
        self.assertNotIn('\u2014', blob)
        self.assertNotIn('donat', blob.lower())
        self.assertNotIn('tax-deductible', blob.lower())


if __name__ == '__main__':
    unittest.main()
