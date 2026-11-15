"""Home hero engraving (Micah, November 15, 2026: "move on the hero engraving"): Doré's Empyrean, public domain, with
its source recorded in data/hero.json and a visible credit line."""
import hashlib, json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H = json.loads((ROOT / 'data/hero.json').read_text())


class Hero(unittest.TestCase):
    def test_record_and_files(self):
        self.assertIn('PD-old-100-1923', H['license'])
        self.assertEqual(H['commons'], 'https://commons.wikimedia.org/wiki/File:Paradiso_Canto_31.jpg')
        self.assertIn('Gutenberg #8789', H['source'])
        for f in H['files'].values():
            data = (ROOT / f['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), f['sha256'])
            self.assertEqual(len(data), f['bytes'])

    def test_on_the_home_page_with_credit(self):
        home = (ROOT / 'index.html').read_text()
        main = home[home.index('<main'):home.index('</main>')]
        self.assertIn('src="/assets/hero/dore-paradiso-31-640.webp"', main)
        self.assertIn('alt="Engraving: Dante and Beatrice', main)
        self.assertIn('Gustave Doré, <cite>The Empyrean</cite>', main)
        self.assertIn('href="https://commons.wikimedia.org/wiki/File:Paradiso_Canto_31.jpg"', main)


if __name__ == '__main__':
    unittest.main()
