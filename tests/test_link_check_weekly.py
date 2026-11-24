"""Weekly link check (Round 8, Job F): internal links, polite outbound spacing, and the issue body. No network."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_internal_links as IL  # noqa: E402
import check_links as CL  # noqa: E402
import link_check_issue as LI  # noqa: E402


class Internal(unittest.TestCase):
    def test_targets(self):
        self.assertEqual(IL.target('/work/orthodoxy/'), 'work/orthodoxy/')
        self.assertEqual(IL.target('styles.css?v=1'), 'styles.css')  # relative to <base href="/">
        self.assertEqual(IL.target('https://bibliothecacatholica.com/policy/#privacy'), 'policy/')
        self.assertEqual(IL.target('/'), 'index.html')
        for skip in ('/#/read/x/y', '#top', 'mailto:a@b.c', 'https://archive.org/details/x', '//cdn.example/x', 'data:image/png;base64,'):
            self.assertIsNone(IL.target(skip), skip)

    def test_resolution(self):
        files = {'index.html', 'work/x/index.html', 'styles.css'}
        self.assertTrue(IL.resolves('work/x/', files))
        self.assertTrue(IL.resolves('work/x', files))
        self.assertTrue(IL.resolves('styles.css', files))
        self.assertFalse(IL.resolves('work/y/', files))

    def test_the_workflow_never_runs_on_push(self):
        wf = (ROOT / '.github/workflows/link-check.yml').read_text()
        self.assertIn("cron: '23 10 * * 0'", wf)
        self.assertNotIn('pull_request', wf)
        self.assertNotIn('push:', wf)
        self.assertEqual(wf.count('continue-on-error: true'), 5)  # every step after setup tolerates failure
        self.assertIn('--per-host-interval 1', wf)


class Polite(unittest.TestCase):
    def test_one_host_is_spaced_and_others_are_not(self):
        old = CL.HOST_INTERVAL
        try:
            CL.HOST_INTERVAL, CL._HOST_NEXT = 1.0, {}
            clock, slept = [100.0], []
            waits = [CL.wait_turn('a.org', now=lambda: clock[0], sleep=slept.append) for _ in range(3)]
            self.assertEqual(waits, [0.0, 1.0, 2.0])
            self.assertEqual(CL.wait_turn('b.org', now=lambda: clock[0], sleep=slept.append), 0.0)
            CL.HOST_INTERVAL = 0.0
            self.assertEqual(CL.wait_turn('a.org', now=lambda: clock[0], sleep=slept.append), 0.0)
        finally:
            CL.HOST_INTERVAL, CL._HOST_NEXT = old, {}


class Issue(unittest.TestCase):
    def test_counts_failures_not_bot_blocks(self):
        internal = {'links': 10, 'pages': 2, 'broken': [{'path': 'work/gone/', 'pages': ['index.html'], 'pageCount': 1}]}
        outbound = {'checked_urls': 3, 'total_urls': 3, 'capped': False, 'results': [
            {'cls': 'ok', 'status': 200, 'url': 'https://a.org/', 'final': 'https://a.org/', 'title': '', 'files': ['x']},
            {'cls': 'blocked', 'status': 403, 'url': 'https://b.org/', 'final': 'https://b.org/', 'title': '', 'files': ['x']},
            {'cls': 'client-error', 'status': 404, 'url': 'https://c.org/gone', 'final': 'https://c.org/gone', 'title': '', 'files': ['data/library.json']}]}
        text, n = LI.body(internal, outbound)
        self.assertEqual(n, 2)
        self.assertIn('`/work/gone/`', text)
        self.assertIn('https://c.org/gone', text)
        self.assertIn('1 blocked by bot protection (not counted)', text)
        self.assertNotIn('https://b.org/', text)
        self.assertEqual(LI.body({'links': 1, 'pages': 1, 'broken': []}, {**outbound, 'results': outbound['results'][:2]})[1], 0)
        self.assertIn('did not finish', LI.body(None, None)[0])


if __name__ == '__main__':
    unittest.main()
