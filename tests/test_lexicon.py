import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'lexicon'))
import build_lexicon as L  # noqa: E402
import contact_sheet as C  # noqa: E402


class LexiconTests(unittest.TestCase):
    def test_committed_lexicon_matches_a_fresh_build(self):
        for name, text in L.build().items():
            self.assertEqual((L.HERE / name).read_text(encoding='utf-8'), text, name)

    def test_every_word_has_a_language_and_a_checked_source(self):
        words, repairs = L.load_built()
        self.assertEqual(set(words), set(L.LANGUAGES))
        specs = {e['edition']: e for _, e in L.spec_editions()}
        for lang, ws in words.items():
            for w, srcs in ws.items():
                self.assertTrue(srcs, w)
                for s in srcs:  # a verified word comes from that edition's own spec, checked on its page images
                    self.assertIn(w, specs[s['edition']].get('verifiedWords', []), (lang, w))
                    self.assertTrue((ROOT / s['record']).exists(), s)
        for r in repairs:
            self.assertTrue(r['from'], r)
            for s in r['from']:
                self.assertIn(s['kind'], ('hand fix', 'automatic repair checked on the image'))
                self.assertTrue((ROOT / s['record']).exists(), s)

    def test_seeds_must_record_source_and_licence(self):
        for s in L.load('seeds.json')['seeds']:
            self.assertTrue(s.get('source') and s.get('url') and s.get('licence'), s)

    def test_hand_fix_pairs_are_word_level_and_similar(self):
        self.assertEqual(L.word_pairs('Festschrift fiir Whitley', 'Festschrift für Whitley'), [('fiir', 'für')])
        self.assertEqual(L.word_pairs('Pee RDER BOOK CoO.', 'B. HERDER BOOK CO.'), [('RDER', 'HERDER'), ('CoO', 'CO')])
        self.assertEqual(L.word_pairs('JUN 2 1949', ''), [])
        self.assertEqual(L.word_pairs('No more', 'NO more'), [])  # case-only changes are not repairs

    def test_candidates_are_only_proposals(self):
        lex = L.load_built()
        cs = L.candidates('Calahoira', lex)
        self.assertEqual(cs[0]['reading'], 'Calahorra')
        self.assertEqual(cs[0]['language'], 'names')
        for c in L.candidates('hved', lex) + cs:
            self.assertEqual(c['status'], L.STATUS)
            self.assertIn('page image', c['status'])
        self.assertEqual(L.candidates('Qzxvk', lex), [])

    def test_the_read_gate_tool_never_reads_the_lexicon(self):
        # A lexicon word counts as read in a book only once it is recorded in that book's spec after an image check.
        src = (ROOT / 'tools' / 'transcribe_scan.py').read_text(encoding='utf-8')
        self.assertNotIn('lexicon', src)


class ContactSheetTests(unittest.TestCase):
    def test_apply_records_only_the_reviewers_decisions(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            spec = d / 'spec.json'
            spec.write_text(json.dumps([{'edition': 'x', 'verifiedWords': ['Aed'], 'handFixes': []}]))
            (d / 'occurrences.json').write_text(json.dumps([
                {'id': 'o1', 'form': 'Liadin', 'leaf': 5, 'line': 'Since I parted from Liadin,'},
                {'id': 'o2', 'form': 'Mohng', 'leaf': 6, 'line': "says Mohng. ' Why"},
                {'id': 'o3', 'form': 'Mohng', 'leaf': 7, 'line': 'Mohng and Mohng'},
                {'id': 'o4', 'form': 'Guare', 'leaf': 8, 'line': 'King Guare'}]))
            dec = d / 'decisions.json'
            dec.write_text(json.dumps({'Liadin': {'printed': True, 'checked': '2026-11-23'},
                                       'Mohng': {'reading': 'Moling', 'checked': '2026-11-23', 'only': ['o2']}}))
            C.apply(spec, 'x', d, dec)
            e = json.loads(spec.read_text())[0]
            self.assertEqual(e['verifiedWords'], ['Aed', 'Liadin'])  # Guare was not decided, so it stays unread
            self.assertEqual(e['handFixes'], [{'leaf': 6, 'page': None, 'ocr': "says Mohng. ' Why", 'reading': "says Moling. ' Why"}])
            dec.write_text(json.dumps({'Guare': {'printed': True}}))
            with self.assertRaises(AssertionError):  # every decision records when the crops were checked
                C.apply(spec, 'x', d, dec)

    def test_sheets_are_never_written_inside_the_repository(self):
        src = (ROOT / 'tools' / 'lexicon' / 'contact_sheet.py').read_text(encoding='utf-8')
        self.assertIn("'write sheets outside the repository'", src)


if __name__ == '__main__':
    unittest.main()
