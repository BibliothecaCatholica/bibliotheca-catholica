"""Edition covers: design C ("Banded") for every hosted edition (tools/covers.py). The SVG is the source; the WebP and social JPEG are
rendered from it with the site's fonts and pinned by SHA-256 in data/covers.json."""
import hashlib, json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import covers as C  # noqa: E402

M = json.loads((ROOT / 'data/covers.json').read_text())
LIB = json.loads((ROOT / 'data/library.json').read_text())


class Covers(unittest.TestCase):
    def test_every_hosted_edition_has_its_design_c_cover(self):
        self.assertEqual(M['design'], 'C')
        self.assertEqual(C.CHOSEN, 'C')
        hosted = {e['id']: w for w in LIB['works'] for e in w['editions'] if e.get('text')}
        c = __import__('hosted_counts').count()
        self.assertEqual(len(hosted), c['hosted'] + c['retired'])  # retired editions keep their files and covers
        self.assertEqual(set(M['covers']), set(hosted))
        shared = C.shared_titles()
        for ed, row in M['covers'].items():
            w = hosted[ed]
            e = next(x for x in w['editions'] if x['id'] == ed)
            svg = (ROOT / 'assets/covers' / (ed + '.svg')).read_text()
            self.assertEqual(svg, C.edition_cover(w, e, shared) + '\n', ed)  # the source is current
            self.assertEqual(hashlib.sha256(svg.encode()).hexdigest(), row['svg'], ed)
            for kind, f in (('webp', ed + '.webp'), ('og', ed + '-og.jpg')):
                self.assertEqual(hashlib.sha256((ROOT / 'assets/covers' / f).read_bytes()).hexdigest(), row[kind], ed + ' ' + kind)
            self.assertEqual(row['work'], w['id'])
        self.assertEqual(sorted(p.name for p in (ROOT / 'assets/covers').iterdir()),
                         sorted(n for ed in M['covers'] for n in (ed + '.svg', ed + '.webp', ed + '-og.jpg')))

    def test_covers_are_typographic_and_tell_volumes_apart(self):
        for ed in M['covers']:
            svg = (ROOT / 'assets/covers' / (ed + '.svg')).read_text()
            self.assertNotIn('<image', svg)  # no photographs or third-party art
            self.assertIn('#8b1e2d', svg)
        txt = lambda ed: ' '.join(re.findall(r'>([^<]+)</text>', (ROOT / 'assets/covers' / (ed + '.svg')).read_text()))
        self.assertIn('VOLUME II', txt('pg-45305'))
        self.assertIn('SUPPLEMENT', txt('ia-summa-supplement'))
        self.assertIn('FEBRUARY', txt('pg-45604'))
        self.assertIn('THÉRÈSE OF LISIEUX', txt('pg-16772'))

    def test_covers_are_used(self):
        work = (ROOT / 'work/orthodoxy/index.html').read_text()
        self.assertIn('<img class="work-cover" src="/assets/covers/pg-130.webp"', work)
        self.assertIn('<meta property="og:image" content="https://bibliothecacatholica.com/assets/covers/pg-130-og.jpg">', work)
        ch = (ROOT / 'work/orthodoxy/ch/04-the-ethics-of-elfland/index.html').read_text()
        self.assertIn('assets/covers/pg-130-og.jpg', ch)
        home = (ROOT / 'index.html').read_text()
        self.assertIn('assets/og-image.png', home)  # the site image stays for every other page
        self.assertIn('list-cover', (ROOT / 'author/g-k-chesterton/index.html').read_text())
        lib = (ROOT / 'scripts/library.js').read_text()
        self.assertIn("coverImg(local,'wrow-cover',48)", lib)
        self.assertIn("coverImg(hosted,'work-cover',220)", lib)
        self.assertIn('pa-cover', (ROOT / 'scripts/reader.js').read_text())
        self.assertIn('properties="cover-image"', (ROOT / 'tools/build_epub.py').read_text())


if __name__ == '__main__':
    unittest.main()
