"""Texts imported from sources other than Project Gutenberg (tools/import_plain_text.py; hosting rule, Nov 15, 2026)."""
import hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from rights_rule import nonrenewal_problems, pd_by_date  # noqa: E402

LIB = json.loads((ROOT / 'data/library.json').read_text())
IMPORTED = [(w, e, json.loads((ROOT / 'data/sources' / (e['id'] + '.json')).read_text()))
            for w in LIB['works'] for e in w['editions'] if e.get('text')
            if json.loads((ROOT / 'data/sources' / (e['id'] + '.json')).read_text()).get('sourceName')]


class ImportedTexts(unittest.TestCase):
    def test_each_import_keeps_its_source_notice_and_names_a_dated_scan(self):
        for w, e, r in IMPORTED:
            raw = (ROOT / e['text']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), r['sha256'], e['id'])
            text = raw.decode('utf-8')
            self.assertIn(r['sourceNotice'].strip()[:400], text, e['id'])  # the source's own header, unchanged
            self.assertIn('*** START OF THE HOSTED TEXT', text, e['id'])
            self.assertTrue(text.rstrip().endswith('***'), e['id'])
            self.assertIn(r['rightsBasis'], ('pd-date', 'pd-nonrenewal'), e['id'])
            if r['rightsBasis'] == 'pd-date':
                self.assertTrue(pd_by_date(r['iaWitness']['year']), e['id'])
            else:
                self.assertEqual(nonrenewal_problems(r.get('nonRenewal')), [], e['id'])
                self.assertEqual(r['iaWitness']['identifier'], r['nonRenewal']['scan'], e['id'])
            self.assertEqual(r['iaWitness']['url'], 'https://archive.org/details/' + r['iaWitness']['identifier'])
            col = r['collation']
            if 'accepted' in col:  # per-edition owner acceptance below 95%, recorded with its score and reason
                self.assertEqual(col['accepted']['agreement'], col['agreement'], e['id'])
                self.assertGreaterEqual(col['agreement'], 0.9, e['id'])
                self.assertTrue(col['accepted']['date'] and len(col['accepted']['reason']) > 40, e['id'])
                self.assertIn('Accepted by owner ' + col['accepted']['date'] + ' at ' + f"{col['agreement']:.1%}", e['note'], e['id'])
            else:
                self.assertGreaterEqual(col['agreement'], 0.95, e['id'])  # OCR noise allowed; a wrong book is not
            self.assertTrue(e['rights'].startswith('Public domain in the USA.'), e['id'])
            self.assertIn(r['sourceName'], e['rights'], e['id'])


if __name__ == '__main__':
    unittest.main()
