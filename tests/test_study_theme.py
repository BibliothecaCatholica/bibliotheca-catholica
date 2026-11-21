"""/study/ follows the reader's theme like every other page (QA review of #98 to #115, November 21, 2026).

study/index.html is maintained by hand, so it carries its own copy of the theme boot from index.html, and
assets/study/study.css restyles its hard-coded light colors under [data-theme=dark] with the site tokens."""
import re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BOOT = re.compile(r"<script>document\.documentElement\.classList\.add\('js'\);[^<]*</script>")


class StudyTheme(unittest.TestCase):
    def test_same_boot_as_the_home_page_before_the_stylesheets(self):
        home = BOOT.search((ROOT / 'index.html').read_text(encoding='utf-8')).group(0)
        study = (ROOT / 'study/index.html').read_text(encoding='utf-8')
        self.assertEqual(BOOT.findall(study), [home])
        self.assertLess(study.index(home), study.index('rel="stylesheet"'))
        self.assertLess((ROOT / 'index.html').read_text(encoding='utf-8').index(home), (ROOT / 'index.html').read_text(encoding='utf-8').index('rel="stylesheet"'))
        self.assertIn("localStorage.getItem('hub-theme')", home)
        for rel in ('support/index.html', 'prayers/index.html', 'doctors/index.html', 'reading/advent-2026/index.html'):
            page = (ROOT / rel).read_text(encoding='utf-8')
            with self.subTest(rel):
                self.assertEqual(BOOT.findall(page), [home], rel)
                self.assertLess(page.index(home), page.index('rel="stylesheet"'), rel)

    def test_dark_rules_use_site_tokens(self):
        css = (ROOT / 'assets/study/study.css').read_text(encoding='utf-8')
        for sel in ('[data-theme=dark] body{background:var(--bg);color:var(--ink)}', '[data-theme=dark] a{color:var(--rubric)}',
                    '[data-theme=dark] input,[data-theme=dark] select{background:var(--card)'):
            self.assertIn(sel, css)
        self.assertIn('/assets/study/study.css?v=', (ROOT / 'study/index.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
