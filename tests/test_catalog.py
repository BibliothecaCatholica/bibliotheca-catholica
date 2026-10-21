import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_library', ROOT/'tools/build_library.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog=json.loads((ROOT/'data/library.json').read_text())
    def test_all_hosted_editions_have_verified_files_and_rights(self):
        build.validate(self.catalog)
        self.assertEqual(24,sum(bool(e.get('text')) for w in self.catalog['works'] for e in w['editions']))
    def test_duplicate_work_is_rejected(self):
        self.catalog['works'].append(copy.deepcopy(self.catalog['works'][0]))
        with self.assertRaises(AssertionError):build.validate(self.catalog)
    def test_changed_text_checksum_is_rejected(self):
        self.catalog['works'][0]['editions'][0]['sha256']='incorrect'
        with self.assertRaises(AssertionError):build.validate(self.catalog)
    def test_missing_author_is_rejected(self):
        self.catalog['works'][0]['authorId']='unknown-person'
        with self.assertRaises(AssertionError):build.validate(self.catalog)
    def test_text_path_cannot_escape_text_directory(self):
        self.catalog['works'][0]['editions'][0]['text']='../../outside.txt'
        with self.assertRaises(AssertionError):build.validate(self.catalog)
    def test_copyrighted_source_and_lewis_are_external_only(self):
        for w in self.catalog['works']:
            if w['id']=='practice-presence' or w['tradition']=='Anglican':
                self.assertTrue(all(not e.get('text') for e in w['editions']))
    def test_existing_hub_snapshots_agree(self):
        js=(ROOT/'data/data.js').read_text().split('=',1)[1].strip().rstrip(';')
        self.assertEqual(json.loads(js),json.loads((ROOT/'data/catholic-hub.json').read_text()))
