"""Story of a Soul (pg-16772) structured edition.

Built with accent-insensitive matching in the fidelity check (the displayed
text still comes from the hosted TXT) and with the italics from its own Gutenberg HTML; verse stays as the source's line
breaks; bracketed notes stay as plain text."""
import hashlib, json, re, subprocess, sys, unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import structure_text as ST  # noqa: E402
import auto_layout as A  # noqa: E402
from reader_formatting import reading_block, with_auto_layout, with_structure  # noqa: E402

KEY = ('story-of-a-soul', 'pg-16772')
SPEC = ST.EDITIONS[KEY]
STORED = json.loads((ROOT / SPEC['out']).read_text())
LIB = json.loads((ROOT / 'data/library.json').read_text())
EDITION = next(e for w in LIB['works'] for e in w['editions'] if e['id'] == 'pg-16772')


class Text(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(markup)

    def handle_data(self, data):
        self.parts.append(data)


class StoryOfASoul(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocks = ST.txt_blocks(EDITION['text'])

    def test_gate_passes_and_the_stored_file_is_current(self):
        fresh, problems = ST.build(*KEY, SPEC, write=False)
        self.assertEqual(problems, [])
        self.assertEqual(fresh, STORED)
        g = STORED['gate']
        self.assertTrue(g['passed'])
        self.assertEqual(g['matched'], g['txtBodyBlocks'])
        self.assertEqual(g['wordChanges'], 0)
        self.assertEqual(g['splitTxtBlocks'], [{'blocks': [249, 250], 'html': 'id00239'}])
        self.assertEqual(set(g['typographic']), {'em dash in HTML = two hyphens in TXT',
                                                 'accents, ligatures, or TXT underscores folded (blocks)',
                                                 'TXT blocks with underscores for the HTML italics',
                                                 'line break next to two hyphens in TXT (blocks)'})
        self.assertEqual(g['typographic']['line break next to two hyphens in TXT (blocks)'], 2)
        self.assertIn('accent-insensitive', STORED['decision'])

    def test_folding_is_for_matching_only(self):
        self.assertEqual(ST.fold_accents('Thérèse, anæmia, Âme'), 'Therese, anaemia, Ame')
        self.assertEqual(ST.match_key('Thérèse _x_', True), ST.match_key('Therese x', True))
        self.assertNotEqual(ST.match_key('Thérèse'), ST.match_key('Therese'))  # Orthodoxy's gate does not fold
        raw = (ROOT / EDITION['text']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EDITION['sha256'])
        self.assertEqual(STORED['txt']['sha256'], EDITION['sha256'])
        self.assertIn('Thérèse', raw.decode('utf-8-sig'))

    def test_intermediate_holds_structure_not_text(self):
        s = json.dumps({k: v for k, v in STORED.items() if k != 'chapters'}, ensure_ascii=False)
        for i in range(STORED['txt']['bodyStart'], STORED['txt']['bodyEnd'] + 1):
            if len(self.blocks[i]) > 60:
                self.assertNotIn(self.blocks[i][:60], s, i)

    def test_chapters_come_from_the_html_and_labels_from_the_txt(self):
        ch = STORED['chapters']
        self.assertEqual([c['num'] for c in ch], ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI'])
        self.assertEqual(ch[4]['title'], 'Vocation of Thérèse')
        for c in ch:
            self.assertTrue(re.sub(r'\s+', ' ', self.blocks[c['heading']]).startswith('CHAPTER ' + c['num']), c)
        self.assertIn('END OF THE AUTOBIOGRAPHY', self.blocks[ch[-1]['end'] + 1])

    def test_italics_from_the_html(self):
        em = STORED['emphasis']
        self.assertEqual(em['report'], {'htmlSpans': 145, 'mapped': 1, 'alreadyUnderscored': 144, 'unmapped': 0})
        for s in em['spans']:
            b, a, z = s[:3]
            if len(s) > 3:
                self.assertEqual((self.blocks[b][a], self.blocks[b][z - 1]), ('_', '_'))
        html = reading_block(with_auto_layout(with_structure(EDITION)), self.blocks[1566], 1566, True)
        self.assertIn('<em class="u"><span class="us">_</span>sister.<span class="us">_</span></em>', html)

    def test_verse_keeps_its_line_breaks_and_notes_stay_plain(self):
        lay = json.loads((ROOT / 'data/auto-layout/pg-16772.json').read_text())
        flowed = {i for lo, hi in lay['reflow'] for i in range(lo, hi + 1)}
        rec = json.loads((ROOT / SPEC['html']).read_text())
        H, _ = ST.html_body(rec)
        with_br = {ST.match_key(h['text'], True) for h in H if h['br']}
        verse = [i for i in range(STORED['txt']['bodyStart'], STORED['txt']['bodyEnd'] + 1)
                 if ST.match_key(self.blocks[i], True) in with_br]
        self.assertGreater(len(verse), 40)
        self.assertFalse(flowed & set(verse))
        self.assertNotIn('note', {b['role'] for b in STORED['blocks']})
        self.assertEqual(lay['structure']['sha256'], EDITION['sha256'])

    def test_browser_and_python_agree_and_keep_every_character(self):
        js = """
const fs=require('fs'),vm=require('vm');
const s=fs.readFileSync('scripts/library.js','utf8');
const start=s.indexOf('function renderReadingBlock('),end=s.indexOf('window.BCReadingBlock=',start);
const c={esc:s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')};
vm.runInNewContext(s.slice(start,end)+';this.render=renderReadingBlock;',c);
const {edition,blocks}=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(blocks.map((b,i)=>c.render(edition,b,i,true))));
"""
        e = with_auto_layout(EDITION)  # the browser gets the structure inside the auto-layout file
        self.assertIn('structure', e['autoLayout'])
        out = subprocess.run(['node', '-e', js], cwd=ROOT, input=json.dumps(dict(edition=e, blocks=self.blocks)),
                             text=True, capture_output=True, check=True)
        browser = json.loads(out.stdout)
        py = with_auto_layout(with_structure(EDITION))
        roles = dict(py['structure']['roles'])
        for i, block in enumerate(self.blocks):
            static = reading_block(py, block, i, True)
            self.assertEqual(static.replace('&#x27;', '&#39;'), browser[i], i)
            self.assertEqual(''.join(Text(static).parts), block, i)
            if i in roles:
                self.assertIn('reading-' + roles[i], static)


if __name__ == '__main__':
    unittest.main()
