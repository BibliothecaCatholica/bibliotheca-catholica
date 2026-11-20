"""tools/import_pdf_print.py: rebuilding a source text from a browser's PDF print (owner-supplied PDFs, November 20, 2026).

The rules are tested on synthetic lines, so CI needs no PDF reader; the pinned prints and their spec are checked too."""
import hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import import_pdf_print as P  # noqa: E402
from rights_rule import pd_by_date  # noqa: E402

SPEC = json.loads((ROOT / 'docs/research/pga-pdf-prints-2026-11/spec.json').read_text())


def L(page, y, text, x2=500.0, x1=100.0):
    return (page, x1, y, x2, text)


class ImportPdfPrint(unittest.TestCase):
    def test_running_head_and_foot_are_dropped_and_nothing_else(self):
        lines = [L(1, 17, 'The Sword of Wood'), L(1, 17, '11/20/26, 9:32 AM'), L(1, 100, 'DOWN in the little village'),
                 L(1, 742, 'https://gutenberg.net.au/ebooks09/0900731h.html'), L(1, 742, 'Page 1 of 17'),
                 L(2, 17, 'The Sword of Wood'), L(2, 17, '11/20/26, 9:32 AM'), L(2, 100, 'army was disbanded;')]
        self.assertEqual([x[4] for x in P.body_lines(lines, 'The Sword of Wood')], ['DOWN in the little village', 'army was disbanded;'])
        # a body line that merely looks like a title is kept when no print date follows it
        self.assertEqual(len(P.body_lines([L(1, 17, 'The Sword of Wood'), L(1, 40, 'by')], 'The Sword of Wood')), 2)

    def test_paragraphs_follow_gaps_and_page_turns(self):
        lines = [L(1, 100, 'eyes, may have had a glimmer of it.', x2=300), L(1, 133, 'On the contrary, by the theory', x2=500),
                 L(1, 151, 'had returned; the terrible', x2=500),            # full measure at the foot of the page
                 L(2, 50, 'army was disbanded.', x2=200),                   # continues across the turn
                 L(2, 68, 'It was in the half of his year that C.', x2=250),  # short, ends with a full stop...
                 L(3, 50, 'underwent a startling change.', x2=500),           # ...but the next page goes on in lower case
                 L(3, 68, 'He said nothing more.', x2=200),
                 L(4, 50, 'The next morning came.', x2=500)]                  # a new paragraph after a short, ended line
        got = [[x[4] for x in p] for p in P.paragraphs(lines)]
        self.assertEqual(got, [['eyes, may have had a glimmer of it.'],
                               ['On the contrary, by the theory', 'had returned; the terrible', 'army was disbanded.',
                                'It was in the half of his year that C.', 'underwent a startling change.', 'He said nothing more.'],
                               ['The next morning came.']])

    def test_hyphens_are_kept(self):
        par = [L(1, 10, 'occasional panics of witch-'), L(1, 28, 'burning. And these'), L(1, 46, 'every one else\'s -'), L(1, 64, 'and so on')]
        self.assertEqual(P.join_lines(par), "occasional panics of witch-burning. And these\nevery one else's -\nand so on")

    def test_spec_names_pinned_prints_public_domain_by_date(self):
        self.assertEqual(len(SPEC), 3)
        for e in SPEC:
            pdf = ROOT / e['pdf']
            self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(), e['pdfSha256'], e['edition'])
            self.assertTrue(pd_by_date(e['year']), e['edition'])
            self.assertTrue(e['sourceUrl'].startswith('https://gutenberg.net.au/'), e['edition'])
            self.assertIn(str(e['year']), e['firstPublishedEvidence'], e['edition'])
            r = json.loads((ROOT / 'docs/research/pga-pdf-prints-2026-11' / (e['edition'] + '.read.json')).read_text())
            self.assertGreaterEqual(r['readRate'], P.READ_GATE, e['edition'])
            hosted = ROOT / 'data/texts' / (e['edition'] + '.txt')
            if not e.get('ia'):
                self.assertFalse(hosted.exists(), 'hosted only through --host, after the scan comparison')
                continue
            src = json.loads((ROOT / 'data/sources' / (e['edition'] + '.json')).read_text())
            self.assertEqual(src['iaWitness']['identifier'], e['ia'], e['edition'])
            self.assertGreaterEqual(src['collation']['agreement'], P.AGREEMENT, e['edition'])
            self.assertEqual(src['sourceFileSha256'], e['pdfSha256'], e['edition'])  # the pinned print, not a refetch
            self.assertGreaterEqual(src['readGate']['readRate'], P.READ_GATE, e['edition'])
            self.assertEqual(hashlib.sha256(hosted.read_bytes()).hexdigest(), src['sha256'], e['edition'])


if __name__ == '__main__':
    unittest.main()
