"""pd-nonrenewal: a US work first published 1931 to 1963 with no renewal, evidence recorded (Part 1, November 2026)."""
import copy, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import rights_rule as RR  # noqa: E402
import build_library as BL  # noqa: E402

OK = {
    'firstPublicationYear': 1945, 'firstPublicationCountry': 'US', 'firstPublicationPlace': 'Milwaukee',
    'firstPublicationPublisher': 'The Bruce Publishing Company',
    'stanford': {'result': 'no renewal found', 'checked': '2026-11-16'},
    'nypl': {'result': 'no renewal found', 'checked': '2026-11-16'},
    'hathitrust': 'pdus',
    'uraa': 'US imprint and copyright page; no earlier edition abroad found, so URAA restoration does not apply.',
    'scan': 'mysteryofiniquit00furf',
}


class NonRenewal(unittest.TestCase):
    def test_passing_record(self):
        self.assertEqual(RR.nonrenewal_problems(OK), [])
        self.assertIn('pd-nonrenewal', RR.BASES)

    def fails(self, **change):
        ev = copy.deepcopy(OK)
        for k, v in change.items():
            if v is None:
                ev.pop(k, None)
            else:
                ev[k] = v
        return RR.nonrenewal_problems(ev)

    def test_missing_evidence(self):
        self.assertEqual(RR.nonrenewal_problems(None), ['missing evidence'])
        self.assertEqual(RR.nonrenewal_problems({}), ['missing evidence'])

    def test_year_outside_1931_to_1963(self):
        for y in (1930, 1964, '1945', None):
            self.assertTrue(any('1931 to 1963' in p for p in self.fails(firstPublicationYear=y)), y)

    def test_foreign_or_blank_first_publication(self):
        for c in ('GB', 'IE', '', None):
            self.assertTrue(any('United States' in p for p in self.fails(firstPublicationCountry=c)), c)
        self.assertTrue(self.fails(firstPublicationPlace=''))
        self.assertTrue(self.fails(firstPublicationPublisher=None))

    def test_missing_or_positive_renewal_search(self):
        self.assertTrue(any('stanford' in p for p in self.fails(stanford=None)))
        self.assertTrue(any('nypl' in p for p in self.fails(nypl={'result': 'R532959', 'checked': '2026-11-16'})))
        self.assertTrue(any('nypl' in p for p in self.fails(nypl={'result': 'no renewal found', 'checked': 'today'})))

    def test_copyright_office_needed_from_1950(self):
        self.assertTrue(any('copyrightOffice' in p for p in self.fails(firstPublicationYear=1952)))
        self.assertEqual(self.fails(firstPublicationYear=1952, copyrightOffice={'result': 'no renewal found', 'checked': '2026-11-20'}), [])

    def test_missing_uraa_line_and_scan(self):
        self.assertTrue(any('URAA' in p for p in self.fails(uraa=None)))
        self.assertTrue(any('URAA' in p for p in self.fails(uraa='n/a')))
        self.assertTrue(any('scan' in p for p in self.fails(scan='')))

    def test_hathitrust_code_quoted_exactly(self):
        self.assertTrue(self.fails(hathitrust='public domain'))
        self.assertEqual(self.fails(hathitrust=None), [])

    def test_scan_must_be_the_named_printing(self):
        ed = {'rightsBasis': 'pd-nonrenewal'}
        src = {'nonRenewal': OK}
        self.assertTrue(BL.scan_ok(ed, src, {'identifier': 'mysteryofiniquit00furf', 'year': 1945}))
        self.assertFalse(BL.scan_ok(ed, src, {'identifier': 'mysteryofiniquit00furf', 'year': 1950}))
        self.assertFalse(BL.scan_ok(ed, src, {'identifier': 'some-other-scan', 'year': 1945}))
        self.assertTrue(BL.scan_ok({'rightsBasis': 'pd-date'}, {}, {'year': 1920}))  # the date rule is unchanged
        self.assertFalse(BL.scan_ok({}, {}, {'year': RR.pd_last_year() + 1}))

    def test_validator_rejects_a_bad_hosted_edition(self):
        cat = json.loads((ROOT / 'data/library.json').read_text())
        w = next(w for w in cat['works'] if any(e.get('text') for e in w['editions']))
        e = next(e for e in w['editions'] if e.get('text'))
        e['rightsBasis'] = 'pd-nonrenewal'
        e['rightsEvidence'] = 'A long enough plain sentence, but the source record carries no nonRenewal evidence.'
        with self.assertRaises(AssertionError):
            BL.validate(cat)


if __name__ == '__main__':
    unittest.main()
