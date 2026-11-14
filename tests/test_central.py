"""CENTRAL.md size cap (owner rule change, November 14, 2026; docs/PROJECT-RULES.md rule 15): handoff entries of at
most 5 lines, the 3 newest only, and under 80 lines in all."""
import re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / 'CENTRAL.md').read_text(encoding='utf-8')


class CentralCap(unittest.TestCase):
    def test_under_80_lines(self):
        self.assertLess(len(TEXT.splitlines()), 80)

    def test_three_newest_entries_of_at_most_five_lines(self):
        log = TEXT[TEXT.index('## Handoff log'):]
        log = log[:log.index('\n## ', 1)]
        entries = re.split(r'\n### ', log)[1:]
        self.assertGreaterEqual(len(entries), 1)
        self.assertLessEqual(len(entries), 3)
        dates = []
        for e in entries:
            title, _, body = e.partition('\n')
            lines = [l for l in body.splitlines() if l.strip()]
            self.assertLessEqual(len(lines), 5, title)
            dates.append(re.match(r'(\d{4}-\d{2}-\d{2})', title).group(1))
        self.assertEqual(dates, sorted(dates, reverse=True), 'newest first')


if __name__ == '__main__':
    unittest.main()
