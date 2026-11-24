"""No tracked file carries Git conflict markers (November 23, 2026: a squash merge once put them into every page
footer). CI runs this; the local whitespace step alone did not catch it."""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = re.compile(rb'^(<<<<<<<|>>>>>>>)( |$)', re.M)


class NoConflictMarkers(unittest.TestCase):
    def test_tracked_files(self):
        files = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True).stdout.decode().split('\0')
        bad = []
        for f in files:
            p = ROOT / f
            if f and p.is_file() and p.suffix in ('.html', '.md', '.json', '.js', '.py', '.css', '.txt', '.xml', '.yml', '.sh', '.mjs'):
                if MARK.search(p.read_bytes()):
                    bad.append(f)
        self.assertEqual(bad[:20], [], f'{len(bad)} tracked files carry conflict markers')


if __name__ == '__main__':
    unittest.main()
