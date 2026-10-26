"""v18: counts shown to readers come from the data, and documents that quote counts match the data."""
import json,re,unittest,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def lib():
    L=json.loads((ROOT/'data/library.json').read_text())
    E=[(w,e) for w in L['works'] for e in w['editions']]
    pg=[e for w,e in E if 'gutenberg.org' in json.dumps(e['source'])]
    return dict(works=len(L['works']),editions=len(E),hosted=sum(1 for w,e in E if e.get('text')),pg=len(pg),pg_hosted=sum(1 for e in pg if e.get('text')))
class Counts(unittest.TestCase):
    def test_data_page_counts_are_computed(self):
        app=(ROOT/'app.js').read_text();m=re.search(r'function openData\(\)\{[\s\S]*?render\(h,\'data\'\)',app);self.assertTrue(m)
        body=m.group(0)
        self.assertIn("libCount('works')+' work records",body)
        self.assertNotRegex(body,r'\b\d+ work records')
        self.assertNotIn('Use them for anything',body)
    def test_docs_match_library_json(self):
        c=lib();cat=(ROOT/'docs/CATALOG.md').read_text();readme=(ROOT/'README.md').read_text()
        self.assertIn('The %d hosted TXT editions'%c['hosted'],cat)
        self.assertIn('%d Gutenberg editions in the catalog, %d hosted'%(c['pg'],c['pg_hosted']),cat)
        self.assertIn('%d individual work records, including %d hosted reading editions'%(c['works'],c['hosted']),readme)
    def test_static_counts_are_computed(self):
        bs=(ROOT/'tools/build_static.py').read_text()
        self.assertRegex(bs,r"counts=\{")
        self.assertNotRegex((ROOT/'tools/site_copy.py').read_text(),r'\b(56|55|98) (hosted|works|texts)\b')
if __name__=='__main__':unittest.main()
