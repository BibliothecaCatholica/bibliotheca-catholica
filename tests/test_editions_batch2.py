"""Editions batch 2 (November 15, 2026): chapter maps with two-block headings and division lines, and the label rule."""
import io, json, re, sys, unittest, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import structure_text as ST  # noqa: E402
from reader_formatting import reading_block, with_structure  # noqa: E402

LIB = {w['id']: w for w in json.loads((ROOT / 'data/library.json').read_text())['works']}
TP = json.loads((ROOT / 'data/text-pages.json').read_text())['works']
EP = json.loads((ROOT / 'data/epubs.json').read_text())['epubs']
BATCH2 = {'heretics': 20, 'ball-and-cross': 20, 'man-thursday': 15, 'chesterton-francis': 10, 'grammar-assent': 10,
          'development-doctrine': 12, 'paradoxes-catholicism': 11, 'life-of-teresa': 40, 'apologia': 7, 'virgin-saints-and-martyrs': 18}


def edition(wid):
    return with_structure(next(e for e in LIB[wid]['editions'] if e['id'] == TP[wid]['edition']))


def epub_doc(edition_id, name):
    z = zipfile.ZipFile(io.BytesIO((ROOT / EP[edition_id]['path']).read_bytes()))
    return z.read('OEBPS/' + name).decode()


class Batch2(unittest.TestCase):
    def test_ten_editions_mapped_structured_and_published(self):
        for wid, n in BATCH2.items():
            d = TP[wid]
            self.assertEqual(len(d['items']), n, wid)
            self.assertIn('partD', d, wid)
            self.assertIn((wid, d['edition']), ST.EDITIONS)
            self.assertIn(d['edition'], EP, wid)
            self.assertTrue(all(len(x['slug']) <= 60 for x in d['items']), wid)

    def test_two_block_headings(self):
        d = TP['paradoxes-catholicism']; x = d['items'][0]
        B = ST.txt_blocks(LIB['paradoxes-catholicism']['editions'][0]['text'])
        self.assertEqual((B[x['heading']], B[x['titleBlocks'][0]]), ('I', 'PEACE AND WAR'))
        self.assertEqual(x['start'], x['heading'] + 2)  # the title line is not repeated under the page's H1
        roles = dict(edition('paradoxes-catholicism')['structure']['roles'])
        self.assertEqual((roles[x['heading']], roles[x['titleBlocks'][0]]), ('chapter', 'heading'))

    def test_division_lines_stay_in_the_epub(self):
        x = TP['development-doctrine']['items'][4]
        B = ST.txt_blocks(LIB['development-doctrine']['editions'][0]['text'])
        self.assertEqual([B[i] for i in x['before']], ['PART II.', 'DOCTRINAL DEVELOPMENTS', 'VIEWED RELATIVELY TO DOCTRINAL', 'CORRUPTIONS.'])
        self.assertNotIn('PART II.', [B[i] for i in range(TP['development-doctrine']['items'][3]['start'], TP['development-doctrine']['items'][3]['end'] + 1)])
        doc = epub_doc('pg-35110', 'ch05.xhtml')
        self.assertLess(doc.index('DOCTRINAL DEVELOPMENTS'), doc.index('CORRUPTIONS.'))
        plate = epub_doc('pg-53841', 'ch02.xhtml')
        self.assertIn('[Illustration: S. CÆCILIA.]', plate)

    def test_named_headings_get_no_second_label(self):
        e = edition('man-thursday'); x = TP['man-thursday']['items'][0]
        B = ST.txt_blocks(e['text'])
        self.assertIn('class="reading-chapter ch-named"', reading_block(e, B[x['heading']], x['heading']))
        p = edition('paradoxes-catholicism'); y = TP['paradoxes-catholicism']['items'][0]
        self.assertNotIn('ch-named', reading_block(p, 'I', y['heading']))
        css = (ROOT / 'styles/library.css').read_text()
        self.assertIn('.edition-designed p.reading-chapter.ch-named::before{content:none}', css)
        js = (ROOT / 'scripts/library.js').read_text()
        self.assertIn("/^_?(chapter|book|part|discourse|lecture)\\b/i.test(p)?'ch-named'", js)


if __name__ == '__main__':
    unittest.main()
