"""Site links to verified R2 uploads (Round 8, Job B3). An empty or unverified manifest changes nothing."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from r2_links import R2Links  # noqa: E402

UP = {'at': '2026-12-01', 'batch': 'batch-1', 'bytes': 22039320, 'sha256': 'a' * 64, 'verified': True}


def item(slug, kind='archive.org', gate='hosted', edition=None, hosted=None, upload=UP, **extra):
    return {'slug': slug, 'source': {'kind': kind, 'id': slug, 'url': 'https://archive.org/details/' + slug}, 'title': 'T ' + slug,
            'author': 'A', 'year': 1937, 'rightsBasis': 'pd-date', 'readGate': gate, 'editionId': edition, 'hostedEditionId': hosted,
            'fringe': False, 'workId': 'w',
            'files': [{'kind': 'pdf', 'key': f'pdf/{slug}.pdf', 'bytes': 22039320, 'url': f'https://files.bibliothecacatholica.com/pdf/{slug}.pdf',
                       'upload': upload}], **extra}


class Links(unittest.TestCase):
    def test_the_committed_manifest_links_only_verified_uploads(self):
        links = R2Links.load()
        for it in links.items:
            self.assertTrue(all(f['upload']['verified'] for f in it['files']))
            self.assertNotIn('ownerReview', it)

    def test_empty_or_unverified_manifest_changes_nothing(self):
        for m in (None, {}, {'items': [item('ia-x', edition='ia-x', upload=None)]},
                  {'items': [item('ia-x', edition='ia-x', upload={**UP, 'verified': False})]},
                  {'items': [item('ia-x', edition='ia-x', ownerReview='waiting')]}):
            links = R2Links(m)
            self.assertEqual(links.edition_links('ia-x'), '')
            self.assertEqual(links.scan_pages(), [])

    def test_hosted_scan_witness_and_source_pdf(self):
        links = R2Links({'items': [item('ia-high', edition='ia-high', hosted='ia-high'),
                                   item('ia-wit', hosted='pg-130'),
                                   item('pga-1', kind='pdf-print', edition='pga-1', hosted='pga-1')]})
        self.assertEqual(links.edition_links('ia-high'),
                         ' · <a href="https://files.bibliothecacatholica.com/pdf/ia-high.pdf">Original scan</a> (PDF, 22 MB)')
        self.assertIn('Dated scan, 1937</a> (PDF, 22 MB)', links.edition_links('pg-130'))
        self.assertIn('download>Source PDF</a>', links.edition_links('pga-1'))
        self.assertEqual(links.scan_pages(), [])  # hosted books get links, not scan pages

    def test_original_scan_page_for_a_book_not_yet_transcribed(self):
        it = item('ia-meyer', gate='near gate', edition='ia-meyer', readGateScore=99.13)
        links = R2Links({'items': [it]})
        self.assertEqual(links.edition_links('ia-meyer'), ' · <a href="/scan/ia-meyer/">Original scan</a> (not yet transcribed)')
        route, title, desc, body, ld, noindex = links.scan_page(links.scan_pages()[0], '/work/w/')
        self.assertEqual(route, 'scan/ia-meyer')
        self.assertIn('Not yet transcribed', body)
        self.assertIn('99.13%', body)
        self.assertIn('https://files.bibliothecacatholica.com/pdf/ia-meyer.pdf', body)
        self.assertNotIn('—', body + desc + title)  # no em-dashes in site copy
        self.assertFalse(noindex)
        fringe = R2Links({'items': [item('ia-f', gate='below', edition='ia-f', fringe=True)]})
        self.assertTrue(fringe.scan_page(fringe.scan_pages()[0])[5])  # a flagged book's page is noindex and out of the sitemap

    def test_no_new_analytics(self):
        src = (ROOT / 'tools/r2_links.py').read_text()
        self.assertNotIn('gtag', src)
        self.assertNotIn('BCAnalytics', src)
        self.assertNotIn('data-track', src)


if __name__ == '__main__':
    unittest.main()
