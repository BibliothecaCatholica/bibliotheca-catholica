import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'lexicon'))
import build_lexicon as L  # noqa: E402


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
        self.assertEqual(L.candidates('Aed', lex), [])

    def test_the_read_gate_tool_never_reads_the_lexicon(self):
        # A lexicon word counts as read in a book only once it is recorded in that book's spec after an image check.
        src = (ROOT / 'tools' / 'transcribe_scan.py').read_text(encoding='utf-8')
        self.assertNotIn('lexicon', src)


if __name__ == '__main__':
    unittest.main()
