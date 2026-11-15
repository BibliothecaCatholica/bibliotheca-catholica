"""Structured-text pilot (Orthodoxy, PR #24): the intermediate structure file, its fidelity gate, and rendering from it.

Owner decision, November 14, 2026: the hosted edition's own HTML (#130), structure only; nothing from #16769."""
import copy, hashlib, json, re, subprocess, sys, unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import structure_text as ST  # noqa: E402
from reader_formatting import reading_block, with_structure  # noqa: E402

SPEC = ST.EDITIONS[('orthodoxy', 'pg-130')]
STORED = json.loads((ROOT / SPEC['out']).read_text())


class Text(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(markup)

    def handle_data(self, data):
        self.parts.append(data)


class StructuredText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lib = json.loads((ROOT / 'data/library.json').read_text())
        cls.edition = next(w for w in lib['works'] if w['id'] == 'orthodoxy')['editions'][0]
        cls.blocks = ST.txt_blocks(cls.edition['text'])

    def test_gate_passes_and_the_stored_file_is_current(self):
        fresh, problems = ST.build('orthodoxy', 'pg-130', SPEC, write=False)
        self.assertEqual(problems, [])
        self.assertEqual(fresh, STORED)
        g = STORED['gate']
        self.assertTrue(g['passed'])
        self.assertEqual(g['wordChanges'], 0)
        self.assertEqual(g['matched'], g['txtBodyBlocks'])
        self.assertEqual(g['uncovered'], [])
        self.assertEqual(list(g['typographic']), ['em dash in HTML = two hyphens in TXT'])

    def test_sources_are_unchanged(self):
        raw = (ROOT / self.edition['text']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.edition['sha256'])
        self.assertEqual(STORED['txt']['sha256'], self.edition['sha256'])
        rec = json.loads((ROOT / SPEC['html']).read_text())
        self.assertEqual(STORED['html']['sha256'], rec['sha256'])
        self.assertIn('130', STORED['html']['url'])
        self.assertFalse('16769' in json.dumps({k: v for k, v in STORED.items() if k != 'decision'}), 'nothing borrowed from #16769')

    def test_intermediate_holds_structure_not_text(self):
        s = json.dumps(STORED, ensure_ascii=False)
        for i in range(STORED['txt']['bodyStart'], STORED['txt']['bodyEnd'] + 1):
            b = self.blocks[i]
            if len(b) > 60:
                self.assertNotIn(b[:60], s, i)
        self.assertFalse('"text"' in json.dumps({k: v for k, v in STORED.items() if k != 'formatting'}), 'no text fields outside the Chapter IV emphasis spans')

    def test_chapters_agree_with_the_chapter_pages(self):
        items = json.loads((ROOT / 'data/text-pages.json').read_text())['works']['orthodoxy']['items']
        self.assertEqual([(c['heading'], c['start'], c['end']) for c in STORED['chapters']],
                         [(x['heading'], x['start'], x['end']) for x in items])
        for c in STORED['chapters']:
            self.assertEqual(re.sub(r'\s+', ' ', self.blocks[c['heading']]), c['num'] + ' ' + c['title'])

    def test_chapter_iv_pilot_is_carried_over_unchanged(self):
        f = self.edition['readerFormatting']
        self.assertEqual(STORED['formatting']['verse'], f['verse'])
        self.assertEqual(STORED['formatting']['emphasis'], f['emphasis'])
        self.assertEqual(STORED['formatting']['evidence'], f['evidence'])
        page = (ROOT / 'work/orthodoxy/ch/04-the-ethics-of-elfland/index.html').read_text()
        self.assertEqual(page.count('<em>if</em>'), 2)
        self.assertEqual(page.count('class="verse-line"'), 2)

    def test_roles_reach_the_browser_through_text_pages_not_the_catalog(self):
        js = (ROOT / 'data/text-pages.js').read_text()
        tp = json.loads(js[len('window.TEXT_PAGES='):].rstrip().rstrip(';'))['orthodoxy']
        self.assertEqual(tp['s']['sha256'], self.edition['sha256'])
        self.assertEqual(tp['s']['r'], with_structure(self.edition)['structure']['roles'])
        self.assertEqual(len([r for r in tp['s']['r'] if r[1] == 'chapter']), 9)
        self.assertNotIn('structure', (ROOT / 'data/library.json').read_text())
        self.assertNotIn('"structure"', (ROOT / 'data/library.js').read_text())

    def test_both_renderers_agree_with_structure_and_keep_every_character(self):
        e = with_structure(self.edition)
        js = """
const fs=require('fs'),vm=require('vm');
const s=fs.readFileSync('scripts/library.js','utf8');
const start=s.indexOf('function renderReadingBlock('),end=s.indexOf('window.BCReadingBlock=',start);
const c={esc:s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')};
vm.runInNewContext(s.slice(start,end)+';this.render=renderReadingBlock;',c);
const {edition,blocks}=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(blocks.map((b,i)=>c.render(edition,b,i,true))));
"""
        out = subprocess.run(['node', '-e', js], cwd=ROOT, input=json.dumps(dict(edition=e, blocks=self.blocks)),
                             text=True, capture_output=True, check=True)
        browser = json.loads(out.stdout)
        roles = dict((b, r) for b, r in e['structure']['roles'])
        for i, block in enumerate(self.blocks):
            static = reading_block(e, block, i, True)
            self.assertEqual(static.replace('&#x27;', '&#39;'), browser[i], i)
            self.assertEqual(''.join(Text(static).parts), block, i)
            self.assertIn('id="reading-p-%d"' % i, static)
            if i in roles:
                self.assertIn('reading-' + roles[i], static)
        stale = copy.deepcopy(e)
        stale['structure']['sha256'] = '0' * 64
        self.assertNotIn('reading-chapter', reading_block(stale, self.blocks[19], 19))

    def test_presentation_overrides_step_2b(self):
        """Micah, November 14, 2026 (step 2b): "by" is a byline; the proofreader's credit goes to the front matter."""
        p = STORED['presentation']
        self.assertIn('step 2b', p['decision'])
        self.assertEqual(p['roles'], [{'block': 11, 'role': 'byline', 'was': 'paragraph'}])
        self.assertEqual(self.blocks[11], 'by')
        self.assertEqual(p['front'], [9])
        self.assertTrue(self.blocks[9].startswith('This etext was proofread by Martin Ward'))
        self.assertIn([11, 'byline'], with_structure(self.edition)['structure']['roles'])
        js = (ROOT / 'data/text-pages.js').read_text()
        tp = json.loads(js[len('window.TEXT_PAGES='):].rstrip().rstrip(';'))['orthodoxy']
        self.assertEqual(tp['s']['f'], [9])
        self.assertIn('FRONT.indexOf(i)>=0', (ROOT / 'scripts/library.js').read_text())
        # the EPUB: credit moved to the notice appendix, verbatim; the byline is centred by its role class
        import tempfile, zipfile, build_epub
        with tempfile.TemporaryDirectory() as d:
            r = build_epub.build(out_dir=Path(d))
            z = zipfile.ZipFile(Path(d) / 'orthodoxy-pg-130.epub')
            front = z.read('OEBPS/front.xhtml').decode()
            notice = z.read('OEBPS/notice.xhtml').decode()
        self.assertNotIn('proofread by Martin Ward', front)
        self.assertIn('class="reading-byline">by</p>', front)
        self.assertIn(self.blocks[9].split('\n')[0], notice)


if __name__ == '__main__':
    unittest.main()
