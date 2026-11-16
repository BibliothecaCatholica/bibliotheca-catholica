"""Work status "not-yet-available" (2026-11-15): listed works with no online copy found yet."""
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_library import validate  # noqa: E402

CATALOG = json.loads((ROOT / 'data/library.json').read_text())
NYA = [w for w in CATALOG['works'] if w.get('status') == 'not-yet-available']


class NotYetAvailable(unittest.TestCase):
    def test_chesterton_list(self):
        self.assertEqual(len(NYA), 11)
        for w in NYA:
            self.assertEqual(w['authorId'], 'g-k-chesterton')
            self.assertEqual(w['editions'], [])
            self.assertNotIn('added', w)
            self.assertNotIn('\u2014', w['description'])

    def test_exemption_is_for_this_status_only(self):
        cat = copy.deepcopy(CATALOG)
        w = next(x for x in cat['works'] if x['id'] == NYA[0]['id'])
        del w['status']
        with self.assertRaises(AssertionError):
            validate(cat)
        cat = copy.deepcopy(CATALOG)
        next(x for x in cat['works'] if x['id'] == NYA[0]['id'])['status'] = 'hidden'
        with self.assertRaises(AssertionError):
            validate(cat)
        cat = copy.deepcopy(CATALOG)
        next(x for x in cat['works'] if x['id'] == NYA[0]['id'])['editions'] = copy.deepcopy(CATALOG['works'][0]['editions'])
        with self.assertRaises(AssertionError):
            validate(cat)

    def test_pages_say_not_yet_available(self):
        page = (ROOT / 'work' / NYA[0]['id'] / 'index.html').read_text()
        self.assertIn('Not yet available online.', page)
        self.assertIn("cta='<p class=\"small\">Not yet available online.</p>'", (ROOT / 'scripts/library.js').read_text())


if __name__ == '__main__':
    unittest.main()
