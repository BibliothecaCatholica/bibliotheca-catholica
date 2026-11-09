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
        self.assertEqual(62,sum(bool(e.get('text')) for w in self.catalog['works'] for e in w['editions']))
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
    def test_reference_only_work_requires_a_reading_sample(self):
        work=next(w for w in self.catalog['works'] if w['tradition']=='Anglican')
        work.pop('readingLinks', None)
        with self.assertRaises(AssertionError):build.validate(self.catalog)
    def test_samples_cannot_be_mislabeled_as_complete_text(self):
        work=next(w for w in self.catalog['works'] if w['tradition']=='Anglican')
        work['readingLinks'][0]['kind']='full-text'
        with self.assertRaises(AssertionError):build.validate(self.catalog)
    def test_existing_hub_snapshots_agree(self):
        # Phase B item 5: data.js (core) + authors-detail.js + isidore-authors.js rebuild the JSON exactly (tools/hubio.py)
        import sys;sys.path.insert(0,str(ROOT/'tools'));import hubio
        hub=json.loads((ROOT/'data/catholic-hub.json').read_text())
        self.assertEqual(hubio.merged(),hub)
        core,det,iso=hubio.split(hub)
        self.assertEqual((ROOT/'data/data.js').read_text(),'window.HUB_DATA='+hubio.dumps(core)+';\n')
        self.assertEqual((ROOT/'data/authors-detail.js').read_text(),'window.HUB_DETAIL='+det+';\n')
        self.assertEqual((ROOT/'data/isidore-authors.js').read_text(),'window.HUB_ISIDORE='+iso+';\n')
    def test_core_hub_is_slim(self):
        js=json.loads((ROOT/'data/data.js').read_text().split('=',1)[1].strip().rstrip(';'))
        self.assertLess((ROOT/'data/data.js').stat().st_size,400_000)
        self.assertNotIn('isidore',js);self.assertEqual(js['isidoreCount'],len(json.loads((ROOT/'data/catholic-hub.json').read_text())['isidore']))
        for a in js['authors']:
            for k in('extract','links','intro','books','media','qidWork','isidoreFolder'):self.assertNotIn(k,a)
            if 'imgCredit' in a:self.assertEqual(a['imgCredit'],{'pd':True});self.assertIn('img',a)
        idx=(ROOT/'index.html').read_text()
        import re
        tags=re.findall(r'<script[^>]* src="(?!https://www\.googletagmanager)[^"]+"[^>]*>',idx)
        self.assertTrue(tags);self.assertTrue(all(' defer ' in t or t.startswith('<script defer') for t in tags if 'boot.js' not in t),tags)
        self.assertEqual(idx.count('rel="preload" as="font"'),2)
        # fonts are self-hosted: no Google Fonts request, and every face in styles/fonts.css exists in fonts/
        self.assertNotIn('fonts.googleapis.com/css',idx);self.assertNotIn('fonts.gstatic.com',idx)
        for f in re.findall(r'href="/fonts/([^"]+)"',idx)+re.findall(r'url\(/fonts/([^)]+)\)',(ROOT/'styles/fonts.css').read_text()):self.assertTrue((ROOT/'fonts'/f).exists(),f)
        for f in('cormorantgaramond','ebgaramond','inter'):self.assertIn('SIL Open Font License',(ROOT/'fonts'/('OFL-'+f+'.txt')).read_text())
        # static author and timeline pages preload the lazy author detail with the token data.js carries
        pre='<link rel="preload" as="script" href="data/authors-detail.js?v='+js['detailV']+'">'
        self.assertIn(pre,(ROOT/'author/trent-horn/index.html').read_text());self.assertIn(pre,(ROOT/'timeline/index.html').read_text())
        self.assertNotIn('authors-detail',(ROOT/'work/confessions/index.html').read_text())

class IsidoreMatchTests(unittest.TestCase):
    def test_matches_point_to_real_books_and_works(self):
        m=json.loads((ROOT/'data/isidore-matches.json').read_text())
        js=json.loads((ROOT/'data/isidore-matches.js').read_text().split('=',1)[1].strip().rstrip(';'))
        self.assertEqual(m,js)
        books={b[0]:b for b in json.loads((ROOT/'data/books.json').read_text())['books']}
        works={w['id']:w for w in json.loads((ROOT/'data/library.json').read_text())['works']}
        for wid,L in m['matches'].items():
            self.assertIn(wid,works);self.assertNotEqual(works[wid]['tradition'],'Anglican')
            for b in L:
                self.assertIn(b['id'],books);self.assertTrue(b['f'] and set(b['f'])<= {'EPUB','PDF'})
                self.assertTrue(set(b['f'])<=set(books[b['id']][7].split('|')))
