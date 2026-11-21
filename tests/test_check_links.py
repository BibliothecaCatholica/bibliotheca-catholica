"""Time cap and fast mode for tools/check_links.py (QA health-sweep, November 21, 2026)."""
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_links as CL  # noqa: E402


class CheckLinksModes(unittest.TestCase):
    def test_fast_uses_one_short_timeout_and_a_smaller_sample(self):
        self.assertEqual(CL.check_timeouts(False), (20, 45))
        self.assertEqual(CL.check_timeouts(True), (8,))
        ns_fast = CL.parse_args(['--fast'])
        ns_full = CL.parse_args([])
        self.assertEqual(ns_fast.isidore_sample, 10)
        self.assertEqual(ns_full.isidore_sample, 60)
        self.assertTrue(ns_fast.fast)
        self.assertFalse(ns_full.fast)

    def test_explicit_isidore_sample_wins_over_fast_default(self):
        ns = CL.parse_args(['--fast', '--isidore-sample', '3'])
        self.assertEqual(ns.isidore_sample, 3)

    def test_max_seconds_stops_and_writes_a_partial_report(self):
        def slow(u, timeouts=(20, 45)):
            time.sleep(0.4)
            return dict(url=u, status=200, final=u, title='ok', cls='ok')

        urls = [f'https://example.test/{i}' for i in range(8)]
        src = {u: {'app.js'} for u in urls}
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / 'link-health.json'
            with mock.patch.object(CL, 'sources', return_value=src), mock.patch.object(CL, 'check', side_effect=slow):
                t0 = time.time()
                CL.main(['--isidore-sample', '0', '--workers', '2', '--max-seconds', '0.5', '--out', str(out)])
                elapsed = time.time() - t0
            self.assertTrue(out.exists(), 'partial report should be written')
            import json
            rep = json.loads(out.read_text())
            self.assertTrue(rep['capped'])
            self.assertLess(rep['checked_urls'], rep['planned_urls'])
            self.assertLess(elapsed, 3.0)  # must not run every slow check to completion


if __name__ == '__main__':
    unittest.main()
