"""Corrected editions (owner decision, November 17, 2026): a faulty hosted text is replaced by a new edition, never
overwritten; the old edition keeps its file and record and is marked retired (docs/PROJECT-RULES.md rule 1)."""
import copy, hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_library as BL  # noqa: E402

LIB = json.loads((ROOT / 'data/library.json').read_text())


class CorrectedEditions(unittest.TestCase):
    def test_retired_editions_keep_their_files_and_point_forward(self):
        retired = [(w, e) for w in LIB['works'] for e in w['editions'] if e.get('retired')]
        self.assertTrue(retired)
        for w, e in retired:
            raw = (ROOT / e['text']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), e['sha256'], e['id'])  # the old file, unchanged
            new = next(x for x in w['editions'] if x['id'] == e['retired']['replacedBy'])
            self.assertEqual(w['editions'][0]['id'], new['id'])  # the reading pages use the correction
            self.assertIn('retired', e['label'])
            self.assertIn('Corrected edition', new['note'])
            self.assertIn('Corrected edition', (ROOT / new['text']).read_text(encoding='utf-8')[:3000])

    def test_retired_editions_are_left_out_of_the_public_count(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import hosted_counts as HC
        c = HC.count()
        live = sum(1 for w in LIB['works'] for e in w['editions'] if e.get('text') and not e.get('retired'))
        self.assertEqual(c['hosted'], live)
        self.assertEqual(c['retired'], sum(1 for w in LIB['works'] for e in w['editions'] if e.get('retired')))
        self.assertIn("(e.text&&!e.retired)", (ROOT / 'app.js').read_text())
        self.assertIn("e.get('text') and not e.get('retired')", (ROOT / 'tools/build_static.py').read_text())

    def test_validator_rejects_a_bad_retirement(self):
        cat = copy.deepcopy(LIB)
        w, e = next((w, e) for w in cat['works'] for e in w['editions'] if e.get('retired'))
        e['retired']['replacedBy'] = 'no-such-edition'
        with self.assertRaises(AssertionError):
            BL.validate(cat)
        cat = copy.deepcopy(LIB)
        w = next(w for w in cat['works'] if any(e.get('retired') for e in w['editions']))
        w['editions'].reverse()  # the retired edition listed first
        with self.assertRaises(AssertionError):
            BL.validate(cat)


if __name__ == '__main__':
    unittest.main()
