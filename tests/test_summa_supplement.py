"""Summa Supplement (2026-11-09): edition ia-summa-supplement, transcribed by tools/transcribe_supplement.py from
Internet Archive scans of the 1917, 1921, and 1922 English Dominican printings, at /summa/supp/q<n>/a<m>/."""
import hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=lambda p:(ROOT/p).read_text(encoding='utf-8')
LIB=json.loads(R('data/library.json'));W=next(w for w in LIB['works'] if w['id']=='summa-theologiae')
E=next(e for e in W['editions'] if e['id']=='ia-summa-supplement');SRC=json.loads(R('data/sources/ia-summa-supplement.json'))
OCR=json.loads(R('data/summa-supplement-ocr.json'));S=json.loads(R('data/summa.json'));P=next(p for p in S['parts'] if p['slug']=='supp')
def main(p):s=R(p);return s[s.find('<main'):s.find('</main>')]
def blocks(path):return [p.strip() for p in re.split(r'\n\s*\n',R(path).replace('\r','')) if p.strip()]
ABOUT=('About the Supplement: Aquinas died in 1274 before finishing Part III. The Supplement completing it was compiled after his death from his earlier Commentary on the Sentences, traditionally attributed to his companion Reginald of Piperno. '
       'Parts I to III here come from the Project Gutenberg e-text of the English Dominican translation, and the Supplement is transcribed from the 1917, 1921, and 1922 printings of the same translation, so formatting may differ slightly.')
class Supplement(unittest.TestCase):
    def test_provenance_rights_and_checksums(self):
        raw=(ROOT/E['text']).read_bytes();sha=hashlib.sha256(raw).hexdigest()
        self.assertEqual(sha,E['sha256']);self.assertEqual(SRC['sha256'],sha);self.assertEqual(OCR['sha256'],sha)
        self.assertTrue(E['source'].startswith('https://archive.org/details/'));self.assertTrue(E['rights'].startswith('Public domain in the USA.'))
        self.assertEqual([v['identifier'] for v in SRC['volumes']],['summatheologi18thom','summatheologi19thom','summatheologi20thom','summatheologicao0000unse_f4n0'])
        self.assertEqual([v['year'] for v in SRC['volumes']],[1917,1922,1921,1922])
        self.assertEqual([tuple(v['questions']) for v in SRC['volumes']],[(1,33),(34,68),(69,86),(87,99)])
        for v in SRC['volumes']+[SRC['substitutePages']]:
            self.assertLess(v['year'],1931);self.assertRegex(v['ocrSha256'],r'^[0-9a-f]{64}$');self.assertEqual(v['url'],'https://archive.org/details/'+v['identifier'])
        t=raw.decode('utf-8');self.assertIn('*** END OF THE TRANSCRIPTION ***',t);self.assertNotIn('1947',t);self.assertNotIn('Project Gutenberg License',t)
        self.assertNotIn('\u2014',json.dumps(E,ensure_ascii=False)+R('data/sources/ia-summa-supplement.json'))
    def test_standard_structure(self):
        self.assertEqual(len(P['questions']),99);self.assertEqual(sum(len(q['articles']) for q in P['questions']),446)
        off=[(q['n'],q['stated'],len(q['articles'])) for q in P['questions'] if q['stated']!=len(q['articles'])]
        self.assertEqual(off,[(64,7,10)])  # the 1922 printing's heading says seven; its inquiry list and text have ten
        self.assertTrue(all(a['title'].startswith('Whether') for q in P['questions'] for a in q['articles']))
        self.assertGreaterEqual(sum(1 for q in P['questions'] for a in q['articles'] if 'o' in a['has'] and 'r' in a['has']),430)
    def test_spot_checks_against_the_scan(self):
        B=blocks(E['text']);q={x['n']:x for x in P['questions']}
        a=q[1]['articles'][0];self.assertEqual(a['title'],'Whether contrition is an assumed sorrow for sins, together with the purpose of confessing them and of making satisfaction for them?')
        self.assertTrue(B[a['start']].startswith('Objection 1: It seems that contrition is not an assumed sorrow for sins'))
        a=q[34]['articles'][4];body=' '.join(B[a['start']:a['end']+1])
        self.assertIn('_I answer that,_ The matter employed outwardly in the sacraments signifies that the power which works in the sacraments comes entirely from without.',body)
        a=q[72]['articles'][2];body=' '.join(B[a['start']:a['end']+1])  # scan page 83 of the 1921 volume is read from the second scan
        self.assertIn('_On the contrary,_ It is written (2 Machab. xv. 14): This is he that prayeth much for the people',body)
        self.assertEqual(q[99]['articles'][4]['title'],'Whether all those who perform works of mercy will be punished eternally?')
        self.assertEqual(B[q[50]['heading']],'QUESTION 50');self.assertEqual(len(q[50]['articles']),1)
    def test_flags_are_on_the_pages(self):
        B=blocks(E['text']);self.assertEqual(len(P['ocrFlags']),len(OCR['flags']));self.assertGreater(len(OCR['flags']),0)
        for f in OCR['flags']:
            self.assertTrue(B[f['block']].startswith(f['starts']));self.assertTrue(f['scan']['url'].startswith('https://archive.org/details/'+f['scan']['identifier']+'/page/n'))
        f=next(f for f in OCR['flags'] if f['a']);m=main('summa/supp/q%d/a%d/index.html'%(f['q'],f['a']))
        self.assertIn('class="ocr-flag"',m);self.assertIn('OCR uncertain',m);self.assertIn(f['scan']['url'],m)
        self.assertIn(str(len(OCR['flags']))+' passages in the Supplement are marked',main('summa/supp/index.html'))
    def test_note_wording_and_pages(self):
        m=main('summa/supp/index.html');self.assertIn(ABOUT,re.sub(r'<[^>]+>','',m))
        self.assertLess(m.find('About the Supplement:'),m.find('<h2>Questions</h2>'))
        for r in ('summa/supp','summa/supp/q1','summa/supp/q1/a1','summa/supp/q64/a10'):
            s=R(r+'/index.html');mm=main(r+'/index.html')
            self.assertEqual(s.count('googletagmanager.com/gtag/js'),1,r);self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/%s/">'%r,s)
            self.assertNotIn('\u2014',mm);self.assertNotIn('data-ga',mm);self.assertIn('ocr-notice',mm);self.assertNotIn('pg-notice',mm)
            self.assertIn('/#/read/summa-theologiae/ia-summa-supplement/',mm)
        self.assertIn('href="/summa/supp/"',main('summa/index.html'));self.assertIn('href="/summa/supp/"',main('work/summa-theologiae/index.html'))
        self.assertIn('rel="prev" href="/summa/3/q90/a4/"',main('summa/supp/q1/a1/index.html'))
    def test_stale_wording_is_gone(self):
        stale=re.compile(r'Supplement is not (in the Gutenberg files|included)|the Supplement is not included|ends at (III|Part III|the Third Part), q(uestion|\.) ?90|No Supplement|Don.t add the Supplement',re.I)
        for p in ('data/library.json','AGENTS.md','docs/CATALOG.md','tools/build_static.py','summa/index.html','summa/3/index.html','work/summa-theologiae/index.html'):
            self.assertIsNone(stale.search(R(p)),p)
    def test_app_reader_and_archive(self):
        self.assertIn('3|supp)',R('app.js'));self.assertIn("archive\\.org\\//.test(e.source)",R('scripts/library.js'))
        self.assertIn('ia-summa-supplement.txt',R('tools/build_text_archive.py'))
        self.assertNotIn('transcribe_supplement',R('package.json'))  # network tool, never part of the build
if __name__=='__main__':unittest.main()
