"""Fidelity contract for opt-in layout and the two independent reading renderers."""
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from build_text_pages import split_text
from reader_formatting import reading_block, validate_formatting


class Text(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(markup)

    def handle_data(self, text):
        self.parts.append(text)


class Formatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lib = json.loads((ROOT/'data/library.json').read_text())
        cls.edition = next(w for w in lib['works'] if w['id']=='orthodoxy')['editions'][0]
        cls.blocks = split_text((ROOT/cls.edition['text']).read_text())

    def test_every_character_and_block_in_both_renderers(self):
        # Exercise the actual browser renderer, including script/markup escaping.
        js = """
const fs=require('fs'),vm=require('vm');
const s=fs.readFileSync('scripts/library.js','utf8');
const start=s.indexOf('function renderReadingBlock('),end=s.indexOf('window.BCReadingBlock=',start);
const c={esc:s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')};
vm.runInNewContext(s.slice(start,end)+';this.render=renderReadingBlock;',c);
const {edition,blocks}=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(blocks.map((b,i)=>c.render(edition,b,i,true))));
"""
        blocks = self.blocks + ['<script>alert("x")</script> & literal _markers_']
        result = subprocess.run(['node','-e',js],cwd=ROOT,input=json.dumps(dict(edition=self.edition,blocks=blocks)),
                                text=True,capture_output=True,check=True)
        browser = json.loads(result.stdout)
        self.assertEqual(len(browser), len(blocks))
        for i, block in enumerate(blocks):
            static = reading_block(self.edition,block,i,True)
            for markup in (static,browser[i]):
                self.assertEqual(''.join(Text(markup).parts),block, i)
                self.assertIn(f'id="reading-p-{i}"',markup)
            # Equivalent output, allowing the two escape spellings for apostrophes.
            self.assertEqual(static.replace('&#x27;','&#39;'),browser[i])
        self.assertNotIn('<script>',browser[-1])

    def test_reviewed_scope_and_drift_guards(self):
        validate_formatting(self.edition,self.blocks)
        e = copy.deepcopy(self.edition)
        e['readerFormatting']['sha256'] = '0'*64
        with self.assertRaises(AssertionError):
            validate_formatting(e,self.blocks)
        self.assertNotIn('class=',reading_block(e,self.blocks[93],93))
        e = copy.deepcopy(self.edition)
        e['readerFormatting']['emphasis'][0]['text'] = 'IF'
        with self.assertRaises(AssertionError):
            validate_formatting(e,self.blocks)
        for i,b in enumerate(self.blocks):
            h=reading_block(self.edition,b,i)
            if not 77 <= i <= 110:
                self.assertNotIn('class=',h)
        verse=reading_block(self.edition,self.blocks[93],93)
        self.assertEqual(verse.count('class="verse-line"'),2)
        self.assertIn('<span class="verse-line">And dance\nupon',verse)
        self.assertEqual(reading_block(self.edition,self.blocks[92],92).count('<em>if</em>'),2)

    def test_generated_chapter_keeps_complete_original_order(self):
        page=(ROOT/'work/orthodoxy/ch/04-the-ethics-of-elfland/index.html').read_text()
        article=page.split('<article class="reading-text"',1)[1].split('>',1)[1].split('</article>',1)[0]
        parser=Text(article)
        self.assertEqual(''.join(parser.parts),''.join(self.blocks[77:111]))
        self.assertEqual(article.count('<p'),34)
        self.assertIn('not a full manual proofread',page)


if __name__ == '__main__':
    unittest.main()
