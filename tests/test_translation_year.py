"""Optional edition field translationYear (2026-11-15): an integer year, filled only where the record states it."""
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_library import validate  # noqa: E402

CATALOG = json.loads((ROOT / 'data/library.json').read_text())
EDS = {e['id']: e for w in CATALOG['works'] for e in w['editions']}


class TranslationYear(unittest.TestCase):
    def test_filled_only_where_stated(self):
        self.assertEqual(EDS['pg-45304']['translationYear'], 1871)
        self.assertEqual(EDS['ccel-npnf102-doctrine']['translationYear'], 1873)
        self.assertEqual(EDS['pg-7403']['translationYear'], 1905)
        # Benham's Imitation: the hosted file names no edition year, so it stays unset
        self.assertNotIn('translationYear', EDS['pg-1653'])
        for e in EDS.values():
            if 'translationYear' in e:
                rest = {k: v for k, v in e.items() if k != 'translationYear'}
                self.assertIn(str(e['translationYear']), json.dumps(rest, ensure_ascii=False), e['id'])

    def test_validator_rejects_bad_values(self):
        for bad in ('1874', True, 1200, 3000):
            cat = copy.deepcopy(CATALOG)
            cat['works'][0]['editions'][0]['translationYear'] = bad
            with self.assertRaises(AssertionError, msg=repr(bad)):
                validate(cat)


if __name__ == '__main__':
    unittest.main()
