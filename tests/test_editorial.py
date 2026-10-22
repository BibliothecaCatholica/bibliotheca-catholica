"""Part B: editorial flags are present, never featured, and quote Dignitatis Humanae verbatim."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DH='https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651207_dignitatis-humanae_en.html'
Q1='The truth cannot impose itself except by virtue of its own truth, as it makes its entrance into the mind at once quietly and with power.'
Q3='The inquiry is to be free, carried on with the aid of teaching or instruction, communication and dialogue, in the course of which men explain to one another the truth they have discovered, or think they have discovered, in order thus to assist one another in the quest for truth.'
F=json.loads((ROOT/'data/editorial-flags.json').read_text())
def js(path,var):
    s=(ROOT/path).read_text();return json.loads(s[len('window.%s='%var):].rstrip().rstrip(';'))
class EditorialTests(unittest.TestCase):
    def test_js_matches_json_and_quotes_verbatim(self):
        self.assertEqual(F,js('data/editorial-flags.js','EDITORIAL_FLAGS'))
        self.assertEqual([q['text'] for q in F['disclaimer']['quotes']],[Q1,Q3])
        self.assertEqual([q['cite'] for q in F['disclaimer']['quotes']],['Vatican II, Dignitatis Humanae 1','Dignitatis Humanae 3'])
        self.assertEqual(F['disclaimer']['source'],DH)
        self.assertIn(Q1,F['policy_html']);self.assertIn(Q3,F['policy_html']);self.assertIn('mailto:micahwatson@bibliothecacatholica.com',F['policy_html'])
        self.assertIn('Listing is not endorsement',F['policy_html'])
    def test_required_records_flagged_and_kept(self):
        B=F['books'];books={str(b[0]) for b in json.loads((ROOT/'data/books.json').read_text())['books']}
        for i,c in (('3895','antisemitic-content'),('2967','antisemitic-content'),('9057','sedevacantist-position'),('8929','sedevacantist-position'),('9297','sedevacantist-position'),('7783','sedevacantist-position')):
            self.assertEqual(B[i]['flag'],c)
        self.assertTrue(set(B)<=books)  # records are kept in the Index
        self.assertNotIn('7046',B)      # William Edmund Fahey is a different author
        for v in B.values():self.assertTrue(v['note'].strip())
        rec=json.loads((ROOT/'data/open/isidore-index.json').read_text())['records']
        self.assertEqual(len(rec),len(books));self.assertEqual({str(r['id']) for r in rec if r['editorial_flag']},set(B))
    def test_flagged_never_featured(self):
        ids=set(F['books']);titles={v['title'].lower() for v in F['books'].values()}
        m=json.loads((ROOT/'data/isidore-matches.json').read_text())
        self.assertFalse({str(b['id']) for L in m['matches'].values() for b in L}&ids)
        names=re.compile(r'Denis Fahey|Fahey, Denis|E\. Michael Jones|Jones, Eugene Michael|Delassus|Cekada|Sanborn|Omlor|Maurice Pinay|Protocols of the Learned',re.I)
        hub=json.loads((ROOT/'data/catholic-hub.json').read_text());hub.pop('isidore',None)  # the neutral A-Z list of every isidore.co folder is an index, not a feature
        texts={f:(ROOT/f).read_text() for f in ('data/library.json','data/guide.js','data/rare.js','data/projects.js','data/doctors.js','data/reading-options.json','data/librivox.json','index.html','sitemap.xml')}
        texts['data/catholic-hub.json (minus the isidore folder index)']=json.dumps(hub,ensure_ascii=False)
        for f,s in texts.items():
            self.assertIsNone(names.search(s),f)
            for t in titles:self.assertNotIn(t,s.lower(),(f,t)) if len(t)>12 else None
        for line in (ROOT/'docs/static-pages.txt').read_text().split():
            self.assertNotIn('isidore/book',line)
    def test_no_nostra_aetate(self):
        for p in list(ROOT.glob('*.html'))+list((ROOT/'data').glob('*.js'))+list((ROOT/'data').glob('*.json'))+[ROOT/'app.js']+list((ROOT/'scripts').glob('*.js'))+list((ROOT/'policy').glob('*.html')):
            self.assertNotIn('nostra aetate',p.read_text().lower(),p.name)
if __name__=='__main__':unittest.main()
