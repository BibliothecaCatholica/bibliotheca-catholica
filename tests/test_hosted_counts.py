"""Every doc that states a hosted-edition count agrees with the catalog (tools/hosted_counts.py --write fixes them)."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import hosted_counts as HC  # noqa: E402


class HostedCounts(unittest.TestCase):
    def test_docs_state_current_counts(self):
        self.assertEqual(HC.stale(), [], 'run: python3 tools/hosted_counts.py --write')

    def test_counts_are_consistent(self):
        c = HC.count()
        self.assertLessEqual(c['hosted_works'], c['hosted'])
        self.assertLessEqual(c['hosted'], c['editions'])
        self.assertEqual(c['structured'], c['epubs'])  # EPUBs are published for every structured edition


if __name__ == '__main__':
    unittest.main()
