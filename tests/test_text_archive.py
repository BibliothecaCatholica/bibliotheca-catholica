import importlib.util
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('build_text_archive', ROOT / 'tools/build_text_archive.py')
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class TextArchiveTests(unittest.TestCase):
    def test_export_preserves_every_verified_text_and_its_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = archive.export(directory)
            self.assertEqual(42, len(manifest['documents']))
            for entry in manifest['documents']:
                raw = (Path(directory) / entry['file']).read_bytes()
                self.assertEqual(entry['sha256'], hashlib.sha256(raw).hexdigest())
                self.assertEqual(entry['bytes'], len(raw))
                original = ROOT / 'data/texts' / Path(entry['file']).name
                self.assertEqual(original.read_bytes(), raw)
                record = json.loads((Path(directory) / entry['provenance']).read_text())
                self.assertEqual(['Public domain in the USA.'], record['metadata']['Copyright'])
            exported = {e['editionId'] for e in manifest['documents']}
            self.assertTrue({'pg-50040', 'pg-18269', 'pg-5657'}.isdisjoint(exported))
            self.assertEqual('texts.bibliothecacatholica.com\n', (Path(directory) / 'CNAME').read_text())

    def test_export_cannot_overwrite_the_main_website(self):
        with self.assertRaises(ValueError):
            archive.export(ROOT)
