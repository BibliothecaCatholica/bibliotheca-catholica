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
        # Orthodoxy pilot, then batch 1 (November 15, 2026): Story of a Soul and the four Father Brown collections
        self.assertEqual(set(BTP.PART_D), {'orthodoxy', 'story-of-a-soul', 'innocence-father-brown', 'wisdom-father-brown',
                                           'secret-father-brown', 'incredulity-father-brown'})
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
