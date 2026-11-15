"""Automatic display-only layout (step 2a, PR #24): the rule, its safeguards, and renderer parity."""
import copy, hashlib, json, subprocess, sys, unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import auto_layout as A  # noqa: E402
from reader_formatting import reading_block, with_auto_layout, with_structure  # noqa: E402

LIB = json.loads((ROOT / 'data/library.json').read_text())
EDITIONS = {e['id']: (w, e) for w in LIB['works'] for e in w['editions'] if e.get('text')}
REPORT = json.loads((ROOT / 'data/auto-layout/report.json').read_text())


class Text(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(markup)

    def handle_data(self, data):
        self.parts.append(data)


def blocks(e):
    return [b for b, r in A.raw_blocks((ROOT / e['text']).read_text(encoding='utf-8-sig'))]


class AutoLayout(unittest.TestCase):
    def test_rule_reproduces_the_verified_chapter_iv_result(self):
        raw = (ROOT / 'data/texts/pg-130.txt').read_text(encoding='utf-8-sig')
        rb, width = A.raw_blocks(raw), A.wrap_width(raw)
        flow = [i for i in range(77, 111) if A.decide(rb[i][1], width) == 'reflow']
        self.assertEqual(len(flow), 33)
        self.assertEqual(set(range(77, 111)) - set(flow), {93})
        f = EDITIONS['pg-130'][1]['readerFormatting']
        self.assertEqual(f['proseRanges'], [[77, 110]])
        self.assertEqual([v['block'] for v in f['verse']], [93])

    def test_generated_files_are_current_and_bound_to_the_text(self):
        files, report = A.build(write=False)
        self.assertEqual(report, REPORT)
        self.assertEqual(sorted(p.stem for p in (ROOT / 'data/auto-layout').glob('*.json') if p.stem != 'report'), sorted(files))
        for k, v in files.items():
            stored = json.loads((ROOT / 'data/auto-layout' / (k + '.json')).read_text())
            self.assertEqual(stored, v, k)
            w, e = EDITIONS[k]
            self.assertEqual(stored['sha256'], e['sha256'], k)
            self.assertEqual(hashlib.sha256((ROOT / e['text']).read_bytes()).hexdigest(), e['sha256'], k)

    def test_exclusions_and_editions_left_off(self):
        names = {w['id'] for w, e in EDITIONS.values()}
        for wid in ('divine-comedy', 'ballad-white-horse', 'hopkins-poems', 'dream-gerontius', 'legends-of-saint-patrick'):
            self.assertIn(wid, names)
            for k, (w, e) in EDITIONS.items():
                if w['id'] == wid:
                    self.assertIn(k, REPORT['excluded'])
                    self.assertFalse((ROOT / 'data/auto-layout' / (k + '.json')).exists(), k)
        self.assertNotIn('underHalf', REPORT)  # the 50% cut-off was dropped (owner, November 14); coverage is listed
        on = set(REPORT['editions'])
        self.assertEqual(on | set(REPORT['excluded']), set(EDITIONS))
        for k in ('pg-38326', 'pg-45305'):  # Bede and City of God XIV-XXII switched on
            self.assertIn(k, on)
        for (ed, i) in A.KEEP:  # known verse keeps the file's own line breaks
            lay = json.loads((ROOT / 'data/auto-layout' / (ed + '.json')).read_text())
            self.assertFalse(any(lo <= i <= hi for lo, hi in lay['reflow']), (ed, i))
        self.assertEqual(set(A.KEEP), {('pg-130', 123), ('pg-1695', 22)})

    def test_scan_verified_blocks_and_pinned_html_constraints(self):
        lay = json.loads((ROOT / 'data/auto-layout/pg-130.json').read_text())
        flowed = {i for lo, hi in lay['reflow'] for i in range(lo, hi + 1)}
        self.assertFalse(flowed & set(range(77, 111)), 'Chapter IV is left to its scan-verified formatting')
        self.assertFalse(any(b in range(77, 111) for b, s, e in lay['em']))
        for ed in ('pg-130', 'pg-16772'):
            lay = json.loads((ROOT / 'data/auto-layout' / (ed + '.json')).read_text())
            ordinary = A.html_ordinary(A.html_records()[ed])
            B = blocks(EDITIONS[ed][1])
            for lo, hi in lay['reflow']:
                for i in range(lo, hi + 1):
                    self.assertIn(A.fold(B[i]), ordinary, (ed, i))

    def test_underscore_pairing_is_conservative(self):
        self.assertEqual(A.underscore_spans('a _word_ b'), [(2, 8)])
        self.assertEqual(A.underscore_spans('one _two'), [])
        self.assertEqual(A.underscore_spans('a ____ rule'), [])
        self.assertEqual(A.underscore_spans('snake_case_name'), [])
        self.assertEqual(A.underscore_spans('_ spaced _'), [])

    def test_browser_and_python_agree_and_keep_every_character(self):
        js = """
const fs=require('fs'),vm=require('vm');
const s=fs.readFileSync('scripts/library.js','utf8');
const start=s.indexOf('function renderReadingBlock('),end=s.indexOf('window.BCReadingBlock=',start);
const c={esc:s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')};
vm.runInNewContext(s.slice(start,end)+';this.render=renderReadingBlock;',c);
const jobs=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(jobs.map(j=>j.blocks.map((b,i)=>c.render(j.edition,b,i,true)))));
"""
        jobs = []
        for k in sorted(REPORT['editions']):
            w, e = EDITIONS[k]
            jobs.append({'edition': with_auto_layout(with_structure(e)), 'blocks': blocks(e)})
        out = subprocess.run(['node', '-e', js], cwd=ROOT, input=json.dumps(jobs), text=True, capture_output=True, check=True)
        browser = json.loads(out.stdout)
        flowed = ems = 0
        for job, rendered in zip(jobs, browser):
            e = job['edition']
            for i, block in enumerate(job['blocks']):
                static = reading_block(e, block, i, True)
                self.assertEqual(static.replace('&#x27;', '&#39;'), rendered[i], (e['id'], i))
                self.assertEqual(''.join(Text(static).parts), block, (e['id'], i))
                self.assertIn('id="reading-p-%d"' % i, static)
                flowed += 'reading-prose' in static
                ems += static.count('<em class="u">')
        self.assertGreater(flowed, 60000)
        self.assertGreater(ems, 20000)
        # a stale checksum turns the layout off
        e = copy.deepcopy(with_auto_layout(EDITIONS['pg-3296'][1]))
        e['autoLayout']['sha256'] = '0' * 64
        self.assertNotIn('class=', reading_block(e, blocks(e)[20], 20))

    def test_reader_switch_and_label(self):
        lib = (ROOT / 'scripts/library.js').read_text()
        self.assertIn('id="reader-breaks"> Original line breaks', lib)
        self.assertIn("localStorage.getItem('bc:reader-breaks')", lib)
        self.assertIn("var AUTO_LABEL='" + A.LABEL + "'", lib)
        css = (ROOT / 'styles/library.css').read_text()
        self.assertIn('.reading-text.orig-breaks p.reading-prose{white-space:pre-wrap}', css)
        self.assertIn('.reading-text .us,#print-all .us{display:none}', css)
        # the label sits in the edition details, never above the text
        self.assertNotIn('text-auto-layout', lib)
        pages = list((ROOT / 'work/innocence-father-brown/story').glob('*/index.html'))
        self.assertTrue(pages)
        html = pages[0].read_text()
        self.assertGreater(html.index('text-auto-layout'), html.index('</article>'))


if __name__ == '__main__':
    unittest.main()
