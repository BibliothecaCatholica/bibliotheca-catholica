"""Section-header engravings: full-width band, one-line credit, sepia tone (Micah's brief, 21 November 2026)."""
import re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PageArt(unittest.TestCase):
    def test_section_heads_span_full_content_width_like_the_home_hero(self):
        css = (ROOT / 'styles/home.css').read_text()
        # has-art must cancel the 900px .page-head cap so the band matches the home hero
        self.assertIn('.page-head.has-art{position:relative;max-width:none;', css)
        self.assertIn('width:min(44%,520px)', css)  # the same art width as .hero-art
        self.assertIn('filter:sepia(', css)

    def test_visible_section_credit_is_one_short_line_to_credits(self):
        # Full Doré lines stay on /credits/; the heading keeps only "Image credits".
        credits = (ROOT / 'credits/index.html').read_text()
        self.assertIn('id="art-councils"', credits)
        self.assertIn('Göttliche Komödie', credits)
        for rel, key in (('councils/index.html', 'councils'), ('magisterium/index.html', 'magisterium'),
                         ('library/index.html', 'library')):
            html = (ROOT / rel).read_text()
            caps = re.findall(r'<figcaption class="art-credit">(.*?)</figcaption>', html)
            self.assertEqual(len(caps), 1, rel)
            self.assertEqual(caps[0], '<a href="/credits/#art-' + key + '">Image credits</a>', rel)
            self.assertNotIn('Göttliche Komödie', caps[0])

    def test_home_engraving_keeps_its_full_credit_line(self):
        home = (ROOT / 'index.html').read_text()
        self.assertIn('<p class="hero-credit">', home)
        self.assertIn('Gustave Doré, <cite>The Empyrean</cite>', home)


if __name__ == '__main__':
    unittest.main()
