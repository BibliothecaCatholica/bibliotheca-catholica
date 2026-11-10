"""On Christian Doctrine (2026-11-09): hosted Shaw translation from CCEL NPNF1-02 Public Domain plain text."""
import hashlib, json, re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = lambda p: (ROOT / p).read_text(encoding='utf-8')
LIB = json.loads(R('data/library.json'))
W = next(w for w in LIB['works'] if w['id'] == 'on-christian-doctrine')
E = next(e for e in W['editions'] if e['id'] == 'ccel-npnf102-doctrine')
NA = next(e for e in W['editions'] if e['id'] == 'on-christian-doctrine-newadvent')
SRC = json.loads(R('data/sources/ccel-npnf102-doctrine.json'))


def main(p):
    s = R(p)
    return s[s.find('<main'):s.find('</main>')]


def blocks(path):
    return [p.strip() for p in re.split(r'\n\s*\n', R(path).replace('\r', '')) if p.strip()]


class OnChristianDoctrine(unittest.TestCase):
    def test_provenance_rights_and_checksum(self):
        raw = (ROOT / E['text']).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(sha, E['sha256'])
        self.assertEqual(SRC['sha256'], sha)
        self.assertEqual(SRC['kind'], 'public-domain-text')
        self.assertEqual(SRC['title'], E['sourceTitle'])
        self.assertTrue(E['rights'].startswith('Public domain in the USA.'))
        self.assertTrue(E['source'].startswith('https://www.ccel.org/'))
        self.assertRegex(SRC['sourceFileSha256'], r'^[0-9a-f]{64}$')
        self.assertEqual(SRC['iaWitness']['identifier'], 'selectlibraryofn0002unse')
        self.assertLess(SRC['iaWitness']['year'], 1931)
        self.assertIn('*** END OF THE HOSTED TEXT: ON CHRISTIAN DOCTRINE ***', raw.decode('utf-8'))
        self.assertNotIn('Project Gutenberg License', raw.decode('utf-8'))
        self.assertNotIn('\u2014', json.dumps(W, ensure_ascii=False) + R('data/sources/ccel-npnf102-doctrine.json'))
        self.assertNotIn('newadvent.org', E['text'])

    def test_structure_preface_and_four_books(self):
        B = blocks(E['text'])
        self.assertIn('PREFACE.', B)
        for book in ('BOOK I.', 'BOOK II.', 'BOOK III.', 'BOOK IV.'):
            self.assertIn(book, B)
        # Chapters present for each book; heading detector finds BOOK/CHAPTER lines under 140 chars
        heads = [p for p in B if len(p) < 140 and re.match(r'^(BOOK|CHAPTER)\s+([IVXLCDM]+|\d+)([. :\n]|$)', p, re.I)]
        self.assertGreaterEqual(len(heads), 140)
        self.assertTrue(any(p.startswith('CHAPTER 1.') for p in B))
        self.assertTrue(any('CHAPTER 40.' in p for p in B))  # Book I has 40 chapters
        self.assertLess(B.index('PREFACE.'), B.index('BOOK I.'))
        self.assertLess(B.index('BOOK I.'), B.index('BOOK II.'))
        self.assertLess(B.index('BOOK II.'), B.index('BOOK III.'))
        self.assertLess(B.index('BOOK III.'), B.index('BOOK IV.'))
        # Opening of the Preface
        i = B.index('PREFACE.')
        self.assertTrue(any('rules for the interpretation of Scripture' in B[j] for j in range(i, i + 5)))

    def test_new_advent_is_link_only(self):
        self.assertIsNone(NA.get('text'))
        self.assertEqual(NA['source'], 'https://www.newadvent.org/fathers/1202.htm')
        self.assertIn('Not hosted here', NA['rights'])

    def test_author_and_work_pages(self):
        aw = main('author/augustine-of-hippo/index.html')
        self.assertIn('href="/work/on-christian-doctrine/"', aw)
        self.assertIn('Confessions', aw)
        ww = main('work/on-christian-doctrine/index.html')
        self.assertIn('On Christian Doctrine', ww)
        self.assertIn('Shaw', ww)
        self.assertIn('/#/read/on-christian-doctrine/ccel-npnf102-doctrine', ww)
        self.assertIn('newadvent.org/fathers/1202.htm', ww)
        self.assertNotIn('\u2014', ww)
        page = R('work/on-christian-doctrine/index.html')
        self.assertEqual(page.count('googletagmanager.com/gtag/js'), 1)
        self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/work/on-christian-doctrine/">', page)
        self.assertIn('/work/on-christian-doctrine/', R('sitemap.xml'))

    def test_reader_notice_and_archive_docs(self):
        self.assertIn('ccel\\.org\\//.test(e.source)', R('scripts/library.js'))
        self.assertIn('public-domain-text', R('tools/build_library.py'))
        self.assertIn('ccel-npnf102-doctrine', R('docs/IMPLEMENTATION-NOTES.md'))
        self.assertIn('ccel-npnf102-doctrine.txt', R('tools/build_text_archive.py'))


if __name__ == '__main__':
    unittest.main()
