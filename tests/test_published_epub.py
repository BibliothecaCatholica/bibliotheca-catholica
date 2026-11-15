"""Published EPUBs: built in the site build by
tools/build_epub.py --publish, content-hashed names, a manifest (path, sha256, size), linked as "EPUB (this edition)"
ahead of the external EPUB links, with the verbatim Gutenberg 1.E.1 sentence and the full licence inside."""
import hashlib, html, io, json, re, sys, unittest, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import structure_text as ST  # noqa: E402
from notices import PG_LINE  # noqa: E402

M = json.loads((ROOT / 'data/epubs.json').read_text())['epubs']


class PublishedEpub(unittest.TestCase):
    def test_one_per_structured_edition_with_a_hashed_name_and_manifest(self):
        self.assertEqual(set(M), {ed for (w, ed) in ST.EDITIONS})
        self.assertEqual(sorted(p.name for p in (ROOT / 'downloads/epub').glob('*')), sorted(Path(v['path']).name for v in M.values()))
        for ed, v in M.items():
            data = (ROOT / v['path']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), v['sha256'], ed)
            self.assertEqual(len(data), v['size'], ed)
            self.assertEqual(v['path'], 'downloads/epub/%s-%s.%s.epub' % (v['work'], ed, v['sha256'][:12]))
        js = (ROOT / 'data/epubs.js').read_text()
        self.assertEqual(json.loads(js[len('window.EPUBS='):].rstrip().rstrip(';')), {k: {'path': v['path'], 'size': v['size']} for k, v in M.items()})
        self.assertIn('python3 tools/build_epub.py --publish', (ROOT / 'package.json').read_text())

    def test_notice_and_full_licence_inside(self):
        sentence = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', PG_LINE)).split())
        for ed, v in M.items():
            z = zipfile.ZipFile(io.BytesIO((ROOT / v['path']).read_bytes()))
            self.assertEqual(z.namelist()[0], 'mimetype')
            self.assertTrue(all(i.compress_type == zipfile.ZIP_STORED for i in z.infolist()), ed)
            text = ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', b''.join(z.read(n) for n in z.namelist() if n.endswith('.xhtml')).decode())).split())
            if ed.startswith('pg-'):
                self.assertIn(sentence, text, ed)  # the 1.E.1 sentence, verbatim, at the end of the text
                self.assertIn('START: FULL LICENSE', text, ed)
                self.assertIn('1.E.1. The following sentence', text, ed)
            else:  # Standard Ebooks: its own notice at the end and its CC0 dedication from the source file
                from notices import SE_NOTICE
                self.assertIn(' '.join(SE_NOTICE.split()), text, ed)
                self.assertIn('CC0', text, ed)
            self.assertNotIn('review copy', text.lower(), ed)  # the pilot's review-copy marker (the phrase "not published" occurs in Newman's text)

    def test_linked_ahead_of_external_epubs(self):
        lib = (ROOT / 'scripts/library.js').read_text()
        a = lib.index("EPUB (this edition) ↓"); b = lib.index("opts.forEach(function(o){dl.push(")
        self.assertLess(a, b)
        for ed, v in M.items():
            page = (ROOT / ('work/%s/index.html' % v['work'])).read_text()
            self.assertIn('<a download href="/%s">EPUB (this edition)</a>' % v['path'], page)
        idx = (ROOT / 'index.html').read_text()
        tok = hashlib.sha256((ROOT / 'data/epubs.js').read_bytes()).hexdigest()[:10]
        self.assertIn('data/epubs.js?v=' + tok, idx)



class EditionStatus(unittest.TestCase):
    def test_status_table_is_current(self):
        import subprocess
        self.assertEqual(subprocess.run([sys.executable, str(ROOT / 'tools/edition_status.py'), '--check']).returncode, 0)


if __name__ == '__main__':
    unittest.main()
