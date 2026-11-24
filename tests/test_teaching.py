import json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'teaching'))
import teaching as T  # noqa: E402


class TeachingDataTests(unittest.TestCase):
    def test_validator_passes(self):
        self.assertEqual(T.check(), [])

    def test_catechism_index_covers_every_paragraph_once(self):
        idx = json.loads((T.DIR / 'catechism-index.json').read_text(encoding='utf-8'))
        nums = [n for r in idx['pages'] for n in r['paragraphs']]
        self.assertEqual(len(nums), len(set(nums)))
        self.assertEqual(sorted(nums), list(range(1, T.CCC_MAX + 1)))
        for r in idx['pages']:
            self.assertRegex(r['url'], r'^https://www\.vatican\.va/archive/ENG0015/__P\w+\.HTM$')

    def test_unverified_entries_are_never_published(self):
        data = json.loads((T.DIR / 'entries.json').read_text(encoding='utf-8'))
        for e in data['entries']:
            got = T.published(e['kind'], e['id'])
            if got is None:
                continue
            _, cs, ds = got
            self.assertTrue(all(c['status'] == 'verified' for c in cs + ds))

    def test_labels_are_headings_not_summaries(self):
        data = json.loads((T.DIR / 'entries.json').read_text(encoding='utf-8'))
        for e in data['entries']:
            for c in e['catechism']:
                self.assertLessEqual(len(c['label']), 90)
                self.assertNotRegex(c['label'], r'(?i)\b(teaches that|the church says|we must|must be)\b')

    def test_validator_catches_bad_numbers_and_hosts(self):
        data = json.loads((T.DIR / 'entries.json').read_text(encoding='utf-8'))
        bad = json.loads(json.dumps(data))
        e = next(x for x in bad['entries'] if x['catechism'])
        e['catechism'][0]['ccc'] = 9999
        e['documents'].append({'title': 'x', 'url': 'https://example.com/x', 'label': 'x', 'status': 'unverified'})
        problems = T.check(bad)
        self.assertTrue(any('out of range' in p for p in problems))
        self.assertTrue(any('not an official Holy See URL' in p for p in problems))

    def test_flagged_works_have_no_entries(self):
        works, _, _, flags = T.known_ids()
        data = json.loads((T.DIR / 'entries.json').read_text(encoding='utf-8'))
        for e in data['entries']:
            if e['kind'] == 'work':
                self.assertFalse(T.fringe_work(works[e['id']], flags), e['id'])


if __name__ == '__main__':
    unittest.main()
