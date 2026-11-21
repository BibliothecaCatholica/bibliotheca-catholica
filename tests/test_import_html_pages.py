"""tools/import_html_pages.py: texts a source serves as a series of HTML pages (first use: Waterworth's Trent, November 20, 2026).

The pinned pages must still be the bytes the record names, and extracting them again must give the hosted body exactly,
so the hosted file holds the source's words and nothing else. The scan comparison and its 95% floor are checked by
tests/test_imported_texts.py for every imported text."""
import hashlib, json, re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import import_html_pages as H  # noqa: E402

RECORDS = [json.loads(p.read_text()) for p in sorted((ROOT / 'data/sources').glob('*.json'))]
RECORDS = [r for r in RECORDS if isinstance(r, dict) and r.get('sourcePages')]


class ImportHtmlPages(unittest.TestCase):
    def test_there_is_at_least_one(self):
        self.assertTrue(RECORDS)

    def test_corrected_edition_differs_only_by_its_logged_corrections(self):
        # Trent r2 (November 20, 2026): same characters as the edition it corrects except the listed words, in order
        body = lambda i: (lambda t: t[t.index('*** START'):])((ROOT / 'data/texts' / (i + '.txt')).read_text(encoding='utf-8'))
        for r in RECORDS:
            if not r.get('correctedFrom'):
                continue
            a, b = body(r['correctedFrom']), body(r['id'])
            self.assertEqual(re.split(r'[A-Za-z]+', a), re.split(r'[A-Za-z]+', b), r['id'])  # nothing else moved
            diffs = [(x, y) for x, y in zip(re.findall(r'[A-Za-z]+', a), re.findall(r'[A-Za-z]+', b)) if x != y]
            self.assertEqual(diffs, [(c['old'], c['new']) for c in r['typoCorrections']], r['id'])
            self.assertEqual(hashlib.sha256((ROOT / r['text'] if 'text' in r else ROOT / 'data/texts' / (r['id'] + '.txt')).read_bytes()).hexdigest(), r['sha256'])

    def test_pinned_pages_rebuild_the_hosted_body(self):
        for r in RECORDS:
            if r.get('correctedFrom'):
                continue  # checked above against the edition it corrects
            pages = H.pinned(r['id'])
            self.assertEqual([str(p.relative_to(ROOT)) for p, _ in pages], [x['file'] for x in r['sourcePages']], r['id'])
            for (p, raw), x in zip(pages, r['sourcePages']):
                self.assertEqual(hashlib.sha256(raw).hexdigest(), x['sha256'], x['url'])
            self.assertEqual(hashlib.sha256(b''.join(raw for _, raw in pages)).hexdigest(), r['sourceFileSha256'], r['id'])
            text = (ROOT / 'data/texts' / (r['id'] + '.txt')).read_text(encoding='utf-8')
            start = text.index('***\n', text.index('*** START OF THE HOSTED TEXT')) + 4
            end = text.rindex('\n\n*** END OF THE HOSTED TEXT')
            self.assertEqual(text[start:end], H.joined([raw for _, raw in pages], r.get('sourceFormat', 'entry-content')), r['id'])

    def test_read_gate_and_witnesses(self):
        for r in RECORDS:
            self.assertGreaterEqual(r['readGate']['readRate'], H.READ_GATE, r['id'])
            self.assertGreaterEqual(r['collation']['agreement'], H.AGREEMENT, r['id'])
            for w in r.get('secondWitnesses', []):
                self.assertTrue(w['url'].startswith('https://archive.org/details/') and len(w['note']) > 40, r['id'])

    def test_extract_keeps_words_and_drops_only_tags_and_menus(self):
        raw = ('<h1 class="post-title">Session &#8217;Two</h1><div class="entry-content x"><p>'
               '<!-- UberMenu [x] --><nav>First Session</nav></p><p>A  <strong>[Page 5]</strong> word,<br />next'
               '</p><p>&nbsp;</p><h3>CANON I.</h3></div><!-- .entry-content -->').encode('utf-8')
        self.assertEqual(H.extract(raw), 'Session ’Two\n\nA [Page 5] word,\nnext\n\nCANON I.')


    def test_extract_ebible_keeps_titles_heading_and_numbered_verses(self):
        # eBible.org chapter pages (Douay-Rheims Wisdom and Ecclesiasticus, November 21, 2026)
        raw = ("\ufeff<html><body><ul class='tnav'>\n<li><a href='index.htm'>Sirach</a></li>\n<li><a href='SIR02.htm'>&gt;</a></li>\n</ul>"
               '<div class="main">\n <div class=\'mt\'>THE WISDOM OF JESUS THE SON OF SIRACH,  </div><div class=\'mt2\'>OR  </div>'
               "<div class='chapterlabel' id=\"V0\"> 1</div><div class='p'> <span class=\"verse\" id=\"V1\">1&#160;</span>All wisdom"
               ' is from the Lord God.   <span class="verse" id="V2">2&#160;</span>Who hath numbered the sand?   </div>'
               "<ul class='tnav'>\n<li><a href='index.htm'>Sirach</a></li></ul><div class=\"copyright\"><p>Public Domain</p></div></body></html>").encode('utf-8')
        self.assertEqual(H.extract_ebible(raw), 'THE WISDOM OF JESUS THE SON OF SIRACH,\nOR\n\nSirach 1\n\n'
                         '1 All wisdom is from the Lord God.\n\n2 Who hath numbered the sand?')
        self.assertEqual(H.joined([raw, raw], 'ebible').count('Sirach 1'), 2)
        for r in RECORDS:  # every eBible record compares with one book of its scan, named in the witness
            if r.get('sourceFormat') == 'ebible':
                self.assertTrue(r['sourceUrl'].startswith('https://ebible.org/'), r['id'])
                self.assertIn('excerpt', r['iaWitness'], r['id'])

    def test_scan_excerpt_is_whitespace_insensitive_and_bounded(self):
        import import_plain_text as I
        ocr = 'TOBIAS ends.\n\nTHE \n\nBOOK  OF  WISDOM. \n\nLove justice.\n\nECCLESIASTICUS. \n\nThis  Book is so called'
        self.assertEqual(I.excerpt(ocr, 'BOOK OF WISDOM.', 'ECCLESIASTICUS. This Book'), 'BOOK  OF  WISDOM. \n\nLove justice.\n\n')
        with self.assertRaises(AttributeError):
            I.excerpt(ocr, 'BOOK OF JOB', 'ECCLESIASTICUS')

if __name__ == '__main__':
    unittest.main()
