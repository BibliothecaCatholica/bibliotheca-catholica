"""Phase B item 6: the header and the static prerender must not shift when fonts or the app arrive."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LayoutStability(unittest.TestCase):
    def setUp(self):
        self.css = (ROOT / 'styles.css').read_text(encoding='utf-8')
        self.html = (ROOT / 'index.html').read_text(encoding='utf-8')

    def test_header_is_font_independent(self):
        self.assertRegex(self.css, r'\.brand-name\{display:block;width:[\d.]+em;white-space:nowrap\}')
        self.assertIn('.searchwrap input{line-height:19px}', self.css)

    def test_prerender_reserves_a_screen_only_with_js(self):
        self.assertIn('html.js #main>.static-prerender{min-height:100vh}', self.css)
        self.assertIn('html.app-unavailable #main>.static-prerender{min-height:0}', self.css)
        self.assertIn("document.documentElement.classList.add('js')", self.html)
        self.assertIn("classList.add('app-unavailable')", (ROOT / 'scripts' / 'boot.js').read_text(encoding='utf-8'))

    def test_static_pages_carry_the_js_class_script(self):
        for p in ('work/heretics/index.html', 'support/index.html'):
            self.assertIn("document.documentElement.classList.add('js')", (ROOT / p).read_text(encoding='utf-8'), p)


if __name__ == '__main__':
    unittest.main()
