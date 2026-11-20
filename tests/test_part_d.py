"""Part D, beautiful editions (Orthodoxy pilot): title-page work page, chapter openers and endings, book paragraphs.
On chapter pages the chapter opener replaces what was above the text. Covers: design C (tests/test_covers.py)."""
import json, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_static as BS  # noqa: E402
import build_text_pages as BTP  # noqa: E402

TP = json.loads((ROOT / 'data/text-pages.json').read_text())['works']


def main(p):
    s = (ROOT / p).read_text()
    return s[s.index('<main'):s.index('</main>')]


class PartD(unittest.TestCase):
    def test_designed_editions(self):
        # Orthodoxy pilot, batch 1 (Story of a Soul, the four Father Brown collections), and batch 2 (ten editions), November 15, 2026
        self.assertEqual(set(BTP.PART_D), {'orthodoxy', 'story-of-a-soul', 'innocence-father-brown', 'wisdom-father-brown',
                                           'secret-father-brown', 'incredulity-father-brown', 'heretics', 'ball-and-cross',
                                           'man-thursday', 'chesterton-francis', 'grammar-assent', 'development-doctrine',
                                           'paradoxes-catholicism', 'life-of-teresa', 'apologia', 'virgin-saints-and-martyrs',
                                           # Chesterton editions, November 15, 2026
                                           'catholic-church-conversion', 'ballad-white-horse',
                                           'whats-wrong-world', 'short-history-england', 'man-who-knew-too-much', 'flying-inn',
                                           'trees-of-pride', 'manalive', 'club-queer-trades',
                                           # Orthodoxy flow batch 1, November 19, 2026
                                           'confessions', 'betrothed', 'revelations-divine-love',
                                           # Orthodoxy flow batch 2, November 19, 2026
                                           'bede-ecclesiastical-history', 'consolation-philosophy', 'abandonment',
                                           # Orthodoxy flow batch 3, November 20, 2026
                                           'catherine-letters', 'apostolic-fathers', 'europe-faith'})
        for wid, d in TP.items():
            self.assertIn('partD', d, wid)
            self.assertEqual(d['partD']['words'], sum(x['words'] for x in d['items']))
            self.assertEqual(d['partD']['minutes'], round(d['partD']['words'] / 230))
            x = d['items'][0]
            m = main('work/%s/%s/%s/index.html' % (wid, d['kind'], x['slug']))
            self.assertIn('<header class="ch-opener"><p class="ch-label">', m)
            self.assertIn('<p>End of %s</p>' % BS.part_label(d, x).replace('&', '&amp;'), m)
            self.assertNotIn('<div class="page-head">', m[:m.index('<article')])

    def test_chapter_pages_open_and_end_like_a_book(self):
        items = TP['orthodoxy']['items']
        for k, x in enumerate(items):
            m = main('work/orthodoxy/ch/%s/index.html' % x['slug'])
            before = m[:m.index('<article')]
            self.assertIn('<header class="ch-opener"><p class="ch-label">Chapter</p><p class="ch-num">%s</p><h1>' % x['num'], before)
            self.assertNotIn('page-head', before)
            self.assertNotIn('dl-row', before)
            self.assertIn('<article class="reading-text edition-designed"', m)
            end = m[m.index('</article>'):]
            self.assertIn('<p>End of Chapter %s</p>' % x['num'], end)
            self.assertIn('Continue in the reading room', end)
            if k + 1 < len(items):
                self.assertIn('Next: %s. ' % items[k + 1]['num'], end)

    def test_reading_pages_contents_continue_and_colophon(self):
        # design refresh (owner's pick, November 17, 2026): contents at the start only, Continue reading, Finis and a colophon
        import html as H, re
        for wid, d in TP.items():
            items = d['items']
            for k, x in enumerate(items):
                m = main('work/%s/%s/%s/index.html' % (wid, d['kind'], x['slug']))
                toc = m[m.index('<nav class="ch-toc"'):m.index('</nav>', m.index('<nav class="ch-toc"'))]
                self.assertLess(m.index('<nav class="ch-toc"'), m.index('<article'))
                self.assertEqual(toc.count('aria-current="page"'), 1)
                self.assertIn('href="/work/%s/%s/%s/" aria-current="page"' % (wid, d['kind'], x['slug']), toc)
                self.assertEqual(m.count('<ol class="text-parts">'), 0)  # the contents list is not repeated after the pager
                end = m[m.index('</article>'):]
                if k + 1 < len(items):
                    self.assertIn('class="ch-next" rel="next"', end)
                    f = re.search(r'class="ch-next-f">([^<]*)</span>', end)
                    if f:
                        nm = main('work/%s/%s/%s/index.html' % (wid, d['kind'], items[k + 1]['slug']))
                        art = nm[nm.index('<article'):nm.index('</article>')]
                        plain = re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]*>', '', art))).replace('_', '')
                        self.assertIn(H.unescape(f.group(1)).rstrip(' …'), plain, (wid, x['slug']))
                    self.assertNotIn('class="end-colophon"', m)
                else:
                    self.assertIn('<p class="ch-fin">Finis</p>', end)
                    self.assertIn('<section class="end-colophon"', end)
                    self.assertNotIn('rights-badge', end)
                    self.assertLess(end.index('class="end-colophon"'), end.index('pg-notice'))

    def test_work_page_title_page_facts_agree(self):
        m = main('work/orthodoxy/index.html')
        d = TP['orthodoxy']['partD']
        self.assertIn('<p class="work-facts">%s · %s</p>' % (BS.facts_words(d['words']), BS.facts_time(d['minutes'])), m)
        self.assertIn('<h2>About this edition</h2>', m)
        js = (ROOT / 'scripts/library.js').read_text()
        a, b = js.index('function factsWords('), js.index('\n', js.index('function factsTime('))
        out = subprocess.run(['node', '-e', js[a:b] + ';process.stdout.write(JSON.stringify([factsWords(%d),factsTime(%d),factsTime(60),factsTime(25)]))' % (d['words'], d['minutes'])],
                             capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(out.stdout), [BS.facts_words(d['words']), BS.facts_time(d['minutes']), BS.facts_time(60), BS.facts_time(25)])
        self.assertIn("'<a class=\"btn\" href=\"#/read/'+w.id+'/'+hosted.id+'\">Read</a>'", js)

    def test_reader_endings_and_print(self):
        js = (ROOT / 'scripts/library.js').read_text()
        self.assertIn('End of Chapter', js)
        self.assertIn("if(ENDS[i])body+=ENDS[i]", js)
        self.assertIn("d.className='edition-designed'", (ROOT / 'scripts/reader.js').read_text())
        css = (ROOT / 'styles/library.css').read_text()
        for rule in ('.edition-designed p.reading-chapter::before{content:"Chapter"', '::first-letter', 'text-indent:1.5em', 'break-before:page'):
            self.assertIn(rule, css)

    def test_cover_design_chosen(self):
        import covers
        self.assertEqual(set(covers.DESIGNS), {'A', 'B', 'C'})
        self.assertEqual(covers.CHOSEN, 'C')  # tests/test_covers.py checks the files

if __name__ == '__main__':
    unittest.main()
