"""The hosting rule is stated once, in tools/rights_rule.py (owner rule change, November 15, 2026)."""
import datetime, re, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import rights_rule as RR  # noqa: E402


class RightsRule(unittest.TestCase):
    def test_line_moves_each_january_first(self):
        self.assertEqual(RR.pd_last_year(datetime.date(2026, 1, 1)), 1930)
        self.assertEqual(RR.pd_last_year(datetime.date(2026, 12, 31)), 1930)
        self.assertEqual(RR.pd_last_year(datetime.date(2027, 1, 1)), 1931)
        self.assertTrue(RR.pd_by_date(1930, datetime.date(2026, 6, 1)))
        self.assertFalse(RR.pd_by_date(1931, datetime.date(2026, 6, 1)))
        self.assertFalse(RR.pd_by_date(None))
        self.assertEqual(RR.pd_enters(1935), datetime.date(2031, 1, 1))

    def test_sentence_names_the_year_and_fails_closed(self):
        s = RR.rule_sentence(datetime.date(2026, 11, 15))
        self.assertIn('in 2026, that means first published in 1930 or earlier', s)
        self.assertIn('moves forward one year each January 1', s)
        self.assertIn('Unknown rights fail closed', s)
        self.assertNotIn('—', s)

    def test_no_hard_coded_cutoff_in_rule_copy(self):
        # The rule's wording lives in rights_rule.py; these sources must not restate a fixed year as the rule.
        for path in ('AGENTS.md', 'README.md', 'docs/PROJECT-RULES.md', 'docs/RIGHTS.md', 'CONTRIBUTING.md',
                     'tools/rights_pages.py', 'tools/site_copy.py', 'tools/build_text_archive.py', 'scripts/rights.js'):
            text = (ROOT / path).read_text()
            self.assertIsNone(re.search(r'(?i)pre-1931 (selection )?rule|1931 rule|published before 1931 and', text), path)


if __name__ == '__main__':
    unittest.main()
