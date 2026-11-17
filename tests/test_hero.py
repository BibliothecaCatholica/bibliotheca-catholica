"""Home hero engraving: Doré's Empyrean, public domain, with
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

    def test_saints_first_gallery(self):
        # design refresh (owner's pick, November 17, 2026): each home portrait names a hosted book by that person to begin with
        import re, sys
        sys.path.insert(0, str(ROOT / 'tools'))
        import site_copy
        lib = {w['id']: w for w in json.loads((ROOT / 'data/library.json').read_text())['works']}
        home = (ROOT / 'index.html').read_text()
        main = home[home.index('<main'):home.index('</main>')]
        items = re.findall(r'<li><span class="pt"[^>]*><img src="/assets/portraits/([a-z-]+)\.webp".*?Begin with <a href="/work/([a-z0-9-]+)/">', main)
        self.assertEqual([i for i, _ in items], site_copy.HOME_PEOPLE)
        for person, work in items:
            w = lib[work]
            self.assertEqual(w['authorId'], person)
            self.assertTrue(any(e.get('text') for e in w['editions']), work)
        self.assertIn('class="hero-credit"', main)
        self.assertEqual(main.count('fetchpriority="high"'), 1)


if __name__ == '__main__':
    unittest.main()
