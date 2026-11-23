"""R2 inventory and upload tooling (Round 8, Job B; November 23, 2026). No test touches the network."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import r2_inventory as I  # noqa: E402
import r2_upload as U  # noqa: E402
from rights_rule import pd_by_date  # noqa: E402

MANIFEST = json.loads((ROOT / 'data/r2-manifest.json').read_text())


class FakeClient:
    """Stores objects in memory; `corrupt` makes GET return different bytes."""

    def __init__(self, corrupt=False, cache=None):
        self.objects, self.calls, self.corrupt, self.cache = {}, [], corrupt, cache

    def put(self, key, body, content_type, cache_control):
        self.calls.append(('put', key))
        self.objects[key] = (body + (b'x' if self.corrupt else b''), content_type, self.cache or cache_control)
        return {'success': True}

    def get(self, key):
        self.calls.append(('get', key))
        body, ctype, cache = self.objects[key]
        return hashlib.sha256(body).hexdigest(), len(body), ctype, cache

    def delete(self, key):
        self.calls.append(('delete', key))
        self.objects.pop(key, None)
        return {'success': True}


def tiny_manifest(directory):
    """A one-batch manifest whose single file is a local file in `directory`."""
    path = Path(directory) / 'a.pdf'
    path.write_bytes(b'%PDF-1.4 test')
    return {'bucket': 'b', 'accountId': 'x', 'freeTierBytes': 10**10, 'batches': {'batch-1': {'items': ['ia-a'], 'bytes': 13}},
            'items': [{'slug': 'ia-a', 'files': [{'kind': 'pdf', 'key': 'pdf/ia-a.pdf', 'bytes': 13, 'sha256': None, 'localPath': str(path),
                                                   'sourceUrl': None, 'contentType': 'application/pdf', 'cacheControl': I.IMMUTABLE, 'upload': None}]}]}


class Inventory(unittest.TestCase):
    def test_manifest_and_inventory_are_current(self):
        snap = json.loads(I.SOURCES.read_text())
        library = json.loads((ROOT / 'data/library.json').read_text())
        built = I.build(snap, library, MANIFEST)
        self.assertEqual(json.loads(json.dumps(built)), MANIFEST, 'run python3 tools/r2_inventory.py')

    def test_every_listed_item_has_a_clean_basis(self):
        for it in MANIFEST['items']:
            self.assertIn(it['rightsBasis'], ('pd-date', 'pd-nonrenewal'), it['slug'])
            if it['rightsBasis'] == 'pd-date' and it['year']:
                self.assertTrue(pd_by_date(it['year']), it['slug'])
            if it['rightsBasis'] == 'pd-nonrenewal':
                self.assertTrue(it['rightsEvidence'], it['slug'])
            self.assertIn(it['readGate'], ('hosted', 'near gate', 'below'), it['slug'])
            self.assertIs(it['fringe'], False)
            self.assertTrue(it['priorityReason'])

    def test_keys_types_and_cache_headers(self):
        for it in MANIFEST['items']:
            for f in it['files']:
                U.check_key(f['key'])
                self.assertEqual(f['url'], MANIFEST['publicBase'] + '/' + f['key'])
                self.assertEqual(f['cacheControl'], 'public, max-age=31536000, immutable')
                self.assertEqual(f['contentType'], {'pdf': 'application/pdf', 'epub': 'application/epub+zip'}[f['key'].rsplit('.', 1)[1]])
                if f['localPath']:
                    self.assertEqual(f['sha256'], hashlib.sha256((ROOT / f['localPath']).read_bytes()).hexdigest())
        keys = [f['key'] for it in MANIFEST['items'] for f in it['files']]
        self.assertEqual(len(keys), len(set(keys)))

    def test_batches_respect_review_and_the_free_tier(self):
        in_batches = [s for b in MANIFEST['batches'].values() for s in b['items']]
        self.assertEqual(len(in_batches), len(set(in_batches)))
        review = {it['slug'] for it in MANIFEST['items'] if it.get('ownerReview')}
        self.assertTrue(review.isdisjoint(in_batches))
        self.assertIn('ia-jameslaynezjesui00fich', review)  # Fichter waits for the owner's written approval (#164)
        for b in MANIFEST['batches'].values():
            self.assertLessEqual(b['bytes'], MANIFEST['batchTargetBytes'])
        self.assertLess(sum(b['bytes'] for b in MANIFEST['batches'].values()), MANIFEST['freeTierBytes'])

    def test_years_ignore_cutoff_phrases(self):
        self.assertEqual(I.year_of('Published before 1931 (public domain in the USA)'), None)
        self.assertEqual(I.year_of('Published 1926, before 1931'), 1926)
        self.assertEqual(I.year_of('1904-05'), 1905)
        self.assertEqual(I.year_of('c1911'), 1911)
        self.assertEqual(I.slug_for('livesoffathersma12butl_0'), 'ia-livesoffathersma12butl-0')

    def test_after_the_cutoff_without_evidence_is_excluded(self):
        snap = {'archiveOrg': {'later00book': {'title': 'Later Book', 'creator': 'A', 'date': '1950', 'restricted': False, 'servers': [],
                                               'pdf': {'name': 'x.pdf', 'size': 10, 'sha1': 'a'}, 'pageImagesBytes': 0}}}
        lib = {'works': [{'id': 'w', 'title': 'W', 'author': 'A', 'editions': []}]}
        m = I.build(snap, lib, {})
        self.assertEqual([x['source']['id'] for x in m['excluded']], ['later00book'])
        self.assertNotIn('later00book', [it['source']['id'] for it in m['items']])

    def test_upload_records_survive_a_rebuild(self):
        old = copy.deepcopy(MANIFEST)
        key = old['items'][0]['files'][0]['key']
        old['items'][0]['files'][0]['upload'] = {'at': '2026-12-01', 'batch': 'batch-1', 'bytes': 1, 'sha256': 'a', 'verified': True}
        m = I.build(json.loads(I.SOURCES.read_text()), json.loads((ROOT / 'data/library.json').read_text()), old)
        self.assertEqual(next(f for it in m['items'] for f in it['files'] if f['key'] == key)['upload']['at'], '2026-12-01')


class Upload(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.written = []
        self._write = U.write
        U.write = lambda m: self.written.append(copy.deepcopy(m))

    def tearDown(self):
        U.write = self._write
        self.tmp.cleanup()

    def test_dry_run_is_the_default_and_calls_nothing(self):
        client = FakeClient()
        with unittest.mock.patch('builtins.print'):
            self.assertEqual(U.main(['--batch', 'batch-1'], client=client), 0)
        self.assertEqual(client.calls, [])
        self.assertEqual(self.written, [])

    def test_apply_needs_a_batch(self):
        with self.assertRaises(SystemExit), unittest.mock.patch('sys.stderr'):
            U.main(['--apply'], client=FakeClient())

    def test_apply_uploads_verifies_and_records(self):
        m = tiny_manifest(self.tmp.name)
        client = FakeClient()
        n = U.apply(m, 'batch-1', client, today=__import__('datetime').date(2026, 12, 1), log=lambda *a: None)
        self.assertEqual(n, 13)
        self.assertEqual(client.calls, [('put', 'pdf/ia-a.pdf'), ('get', 'pdf/ia-a.pdf')])
        f = m['items'][0]['files'][0]
        self.assertEqual(f['upload'], {'at': '2026-12-01', 'batch': 'batch-1', 'bytes': 13,
                                       'sha256': hashlib.sha256(b'%PDF-1.4 test').hexdigest(), 'verified': True})
        self.assertEqual(client.objects['pdf/ia-a.pdf'][1:], ('application/pdf', 'public, max-age=31536000, immutable'))
        client.calls.clear()
        U.apply(m, 'batch-1', client, log=lambda *a: None)  # a second run skips the recorded object
        self.assertEqual(client.calls, [])

    def test_verification_failure_writes_no_record(self):
        for client in (FakeClient(corrupt=True), FakeClient(cache='no-cache')):
            m = tiny_manifest(self.tmp.name)
            with self.assertRaises(U.Failed):
                U.apply(m, 'batch-1', client, log=lambda *a: None)
            self.assertIsNone(m['items'][0]['files'][0]['upload'])
        self.assertEqual(self.written, [])

    def test_source_checksum_mismatch_uploads_nothing(self):
        m = tiny_manifest(self.tmp.name)
        f = m['items'][0]['files'][0]
        f.update(localPath=None, sourceUrl='https://archive.org/download/x/x.pdf', sourceSha1='0' * 40, key='pdf/ia-zz-test.pdf')
        U.CACHE = Path(self.tmp.name) / 'cache'
        client = FakeClient()
        with self.assertRaises(U.Failed):
            U.apply(m, 'batch-1', client, download=lambda url, path: path.write_bytes(b'not the pdf'), log=lambda *a: None)
        self.assertEqual(client.calls, [])

    def test_delete_clears_the_record(self):
        m = tiny_manifest(self.tmp.name)
        client = FakeClient()
        U.apply(m, 'batch-1', client, log=lambda *a: None)
        U.delete(m, 'pdf/ia-a.pdf', client)
        self.assertIsNone(m['items'][0]['files'][0]['upload'])
        self.assertNotIn('pdf/ia-a.pdf', client.objects)

    def test_keys_outside_the_scheme_are_refused(self):
        for key in ('index.html', 'pdf/../CNAME', '/pdf/a.pdf', 'pdf/a.epub', 'epub/a.pdf'):
            with self.assertRaises(U.Failed):
                U.check_key(key)

    def test_review_items_cannot_be_uploaded(self):
        m = tiny_manifest(self.tmp.name)
        m['items'][0]['ownerReview'] = 'waiting'
        with self.assertRaises(U.Failed):
            U.plan(m, 'batch-1')


import unittest.mock  # noqa: E402

if __name__ == '__main__':
    unittest.main()
