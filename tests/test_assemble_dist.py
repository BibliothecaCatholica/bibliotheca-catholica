"""tools/assemble_dist.py ships only public site paths (build-on-deploy Phase 2 prep, November 22, 2026;
docs/plans/build-on-deploy-plan.md section 5)."""
import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import assemble_dist as A  # noqa: E402

ROUTES = A.route_dirs()
TRACKED = [Path(p) for p in subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True).stdout.split()]


class AssembleDist(unittest.TestCase):
    def test_required_root_files_ship(self):
        for f in ('CNAME', '.nojekyll', '.well-known/atproto-did', 'google3b007babfa8923a4.html', '_headers', 'sitemap.xml',
                  'robots.txt', '404.html', 'build.json', 'index.html', 'study/index.html', 'drafts/index.html'):
            self.assertTrue(A.is_public(Path(f), ROUTES), f)
            self.assertIn(f, A.REQUIRED_DIST_FILES)

    def test_every_generated_page_ships(self):
        pages = (ROOT / 'docs/static-pages.txt').read_text(encoding='utf-8').split()
        self.assertGreater(len(pages), 5000)
        self.assertEqual([p for p in pages if not A.is_public(Path(p), ROUTES)], [])

    def test_site_assets_and_linked_files_ship(self):
        for f in ('app.js', 'styles.css', 'scripts/analytics.js', 'data/library.json', 'data/texts/pg-130.txt',
                  'data/open/README.md', 'data/study/calendar.json', 'docs/CATALOG.md', 'assets/og-image.png'):
            self.assertTrue(A.is_public(Path(f), ROUTES), f)

    def test_repository_only_paths_do_not_ship(self):
        for f in ('tools/build_static.py', 'tests/test_assemble_dist.py', 'src/study/tools.js', '.github/workflows/validate.yml',
                  'docs/PROJECT-RULES.md', 'docs/static-pages.txt', 'data/sources/pg-130.json', 'data/structured/pg-130.json',
                  'AGENTS.md', 'CENTRAL.md', 'HOLDS.md', 'README.md', 'LICENSE', 'package.json', 'tools/templates/index.html'):
            self.assertFalse(A.is_public(Path(f), ROUTES), f)
        shipped_repo_only = [p for p in TRACKED if A.is_public(p, ROUTES) and any(
            p.as_posix() == r or p.as_posix().startswith(r + '/') for r in A.REPO_ONLY)]
        self.assertEqual(shipped_repo_only, [])

    def test_every_tracked_file_is_classified(self):
        # a new top-level tracked path must be added to one list or the other on purpose
        tops = {p.parts[0] for p in TRACKED}
        known = (set(A.PUBLIC_DIRS) | set(ROUTES) | set(A.PUBLIC_ROOT_FILES) | {r.split('/')[0] for r in A.REPO_ONLY}
                 | {'docs'})
        self.assertEqual(sorted(tops - known), [])


if __name__ == '__main__':
    unittest.main()
