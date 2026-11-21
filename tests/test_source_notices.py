"""Hosted part-page notices follow the source host, not a Gutenberg-or-Standard-Ebooks split (QA, 21 November 2026)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import notices as N  # noqa: E402

JS = (ROOT / 'scripts/library.js').read_text(encoding='utf-8')
LIB = json.loads((ROOT / 'data/library.json').read_text())
EM = '\u2014'


class SourceNotices(unittest.TestCase):
    def test_gutenberg_australia_is_not_gutenberg_org(self):
        src = 'https://gutenberg.net.au/ebooks09/0900711h.html'
        self.assertEqual(N.source_kind(src), 'pga')
        self.assertNotEqual(N.source_kind(src), 'pg')
        self.assertIn('Project Gutenberg Australia', N.notice_for(src))
        self.assertNotIn('Project Gutenberg™ License', N.notice_for(src))
        self.assertEqual(N.record_label(src), 'Project Gutenberg Australia record')

    def test_each_known_host_has_its_own_notice_and_label(self):
        cases = {
            'https://www.gutenberg.org/ebooks/130': ('pg', 'Project Gutenberg record', 'Project Gutenberg™ License'),
            'https://standardebooks.org/ebooks/g-k-chesterton/the-incredulity-of-father-brown': ('se', 'Standard Ebooks record', 'Standard Ebooks edition'),
            'https://ebible.org/engDRA/': ('ebible', 'eBible.org record', 'eBible.org'),
            'https://www.papalencyclicals.net/councils/trent.htm': ('peo', 'Papal Encyclicals Online record', 'Papal Encyclicals Online'),
            'https://gutenberg.net.au/ebooks03/0300781h.html': ('pga', 'Project Gutenberg Australia record', 'Project Gutenberg Australia'),
            'https://mlat.uzh.ch/?text=7170': ('mlat', 'Corpus Corporum record', 'Corpus Corporum'),
        }
        for src, (kind, label, needle) in cases.items():
            with self.subTest(src=src):
                self.assertEqual(N.source_kind(src), kind)
                self.assertEqual(N.record_label(src), label)
                self.assertIn(needle, N.notice_for(src))
                if kind != 'se':
                    self.assertNotIn('Standard Ebooks edition', N.notice_for(src))
                if kind != 'pg':
                    self.assertNotIn('Project Gutenberg™ License', N.notice_for(src))
                self.assertNotIn(EM, N.notice_for(src))
                self.assertNotIn(EM, label)

    def test_unknown_hosts_get_a_generic_notice_without_false_attribution(self):
        src = 'https://example.org/some-edition'
        self.assertEqual(N.source_kind(src), 'other')
        self.assertEqual(N.record_label(src), 'Source record')
        n = N.notice_for(src)
        self.assertIn('linked source', n)
        self.assertNotIn('This text comes from the Standard Ebooks edition', n)
        self.assertNotIn('Project Gutenberg™ License', n)
        self.assertNotIn('eBible.org notices', n)
        self.assertNotIn(EM, n)

    def test_library_js_keeps_the_same_words_and_checks_australia_first(self):
        for name, val in (
            ('EBIBLE_NOTICE', N.EBIBLE_NOTICE),
            ('PEO_NOTICE', N.PEO_NOTICE),
            ('PGA_NOTICE', N.PGA_NOTICE),
            ('GENERIC_NOTICE', N.GENERIC_NOTICE),
            ('MLAT_NOTICE', N.MLAT_NOTICE),
            ('SE_NOTICE', N.SE_NOTICE),
        ):
            compact = ' '.join(val.split())
            self.assertIn("var " + name + "='" + compact + "';", JS, name)
        start = JS.index('function sourceNotice')
        fn = JS[start:JS.index('\n', start)]
        plain = fn.replace('\\', '')
        self.assertIn('gutenberg.net.au', plain)
        # Australia is tested before gutenberg.org, so a .net.au URL never gets the .org licence.
        self.assertLess(plain.index('gutenberg.net.au'), plain.index('gutenberg.org'))

    def test_hosted_editions_are_classified_without_false_standard_ebooks_labels(self):
        seen = set()
        for w in LIB['works']:
            for e in w['editions']:
                if not e.get('text') or not e.get('source'):
                    continue
                kind = N.source_kind(e['source'])
                seen.add(kind)
                if kind != 'se':
                    self.assertNotIn('This text comes from the Standard Ebooks edition', N.notice_for(e['source']), e['id'])
                    self.assertNotEqual(N.record_label(e['source']), 'Standard Ebooks record', e['id'])
        for needed in ('pg', 'se', 'ebible', 'peo', 'pga'):
            self.assertIn(needed, seen)


if __name__ == '__main__':
    unittest.main()
