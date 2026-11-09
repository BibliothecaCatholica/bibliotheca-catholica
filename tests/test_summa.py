"""Deep-link gaps 4 (2026-11-09): the Summa Theologiae by question and article from the four hosted Project
Gutenberg volumes (#17611, #17897, #18755, #19950) and the Supplement transcription (tests/test_summa_supplement.py). data/summa.json comes from tools/build_summa.py; the static
pages are /summa/, /summa/<part>/, /summa/<part>/q<n>/, and /summa/<part>/q<n>/a<m>/."""
import hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SITE='https://bibliothecacatholica.com/'
R=lambda p:(ROOT/p).read_text()
S=json.loads(R('data/summa.json'));LIB=json.loads(R('data/library.json'));W=next(w for w in LIB['works'] if w['id']=='summa-theologiae')
def main(p):s=R(p);return s[s.find('<main'):s.find('</main>')]
def blocks(path):return [p.strip() for p in re.split(r'\n\s*\n',R(path).replace('\r','')) if p.strip()]
class Summa(unittest.TestCase):
    def test_editions_are_the_four_gutenberg_volumes_and_the_supplement(self):
        self.assertEqual([e['id'] for e in W['editions']],['pg-17611','pg-17897','pg-18755','pg-19950','ia-summa-supplement'])
        for e in W['editions'][:4]:
            self.assertEqual(e['source'],'https://www.gutenberg.org/ebooks/'+e['id'][3:])
            self.assertEqual(hashlib.sha256((ROOT/e['text']).read_bytes()).hexdigest(),e['sha256'])
            self.assertIn('sample check',e['note']);self.assertIn('no 1947 introduction, synopsis, or index',e['note'])
            self.assertEqual('provenance note only' in e['note'],'Complete American Edition' in e['sourceTitle'],e['id'])
            raw=R(e['text']);self.assertNotIn('1947',raw);self.assertNotIn('Complete American Edition',raw)
        self.assertNotIn('newadvent',json.dumps(W['editions'][:4]));self.assertNotIn('newadvent.org',json.dumps(W));self.assertNotIn('corpusthomisticum',json.dumps(W))
    def test_standard_totals(self):
        got={P['slug']:(len(P['questions']),sum(len(q['articles']) for q in P['questions'])) for P in S['parts']}
        self.assertEqual(got,{'1':(119,584),'1-2':(114,619),'2-2':(189,917),'3':(90,549),'supp':(99,446)})
        for P in S['parts']:
            self.assertEqual([q['n'] for q in P['questions']],list(range(1,len(P['questions'])+1)))
            for q in P['questions']:self.assertEqual([x['n'] for x in q['articles']],list(range(1,len(q['articles'])+1)))
    def test_block_ranges_match_the_reader_split(self):
        P=S['parts'][0];B=blocks('data/texts/pg-17611.txt')
        q2=P['questions'][1];self.assertEqual(B[q2['heading']],'QUESTION 2');a3=q2['articles'][2]
        self.assertEqual(B[a3['heading']],'THIRD ARTICLE [I, Q. 2, Art. 3]');self.assertEqual(a3['title'],'Whether God Exists?')
        self.assertTrue(B[a3['start']].startswith('Objection 1: It seems that God does not exist'))
        self.assertTrue(B[a3['end']].startswith('Reply Obj. 2:'))
    def test_pages_and_sitemap(self):
        sm=R('sitemap.xml');pages=set(R('docs/static-pages.txt').split())
        routes=['summa']+['summa/'+P['slug'] for P in S['parts']]+['summa/%s/q%d'%(P['slug'],q['n']) for P in S['parts'] for q in P['questions']]+['summa/%s/q%d/a%d'%(P['slug'],q['n'],x['n']) for P in S['parts'] for q in P['questions'] for x in q['articles']]
        self.assertEqual(len(routes),1+5+611+3115)
        for r in routes:
            self.assertIn(r+'/index.html',pages,r);self.assertIn('<loc>'+SITE+r+'/</loc>',sm,r)
        for r in ('summa','summa/1','summa/1/q2','summa/1/q2/a3','summa/3/q90/a4','summa/2-2/q83/a17','summa/1/q71/a1','summa/supp','summa/supp/q1','summa/supp/q1/a1','summa/supp/q99/a5'):
            s=R(r+'/index.html');m=main(r+'/index.html')
            self.assertEqual(s.count('googletagmanager.com/gtag/js'),1,r)
            self.assertIn('<link rel="canonical" href="%s%s/">'%(SITE,r),s)
            self.assertIn('class="small ocr-notice"' if r.startswith('summa/supp') else 'class="small pg-notice"',m,r);self.assertIn('rb-public-domain-us',m,r)
            if r.startswith('summa/supp'):self.assertNotIn('pg-notice',m,r)  # the Gutenberg notice only where the source is Gutenberg
            self.assertNotIn('—',m,r);self.assertNotIn('amazon.',m);self.assertNotIn('data-ga',m);self.assertNotIn('href="#',m,r)
            d=re.search(r'<meta name="description" content="([^"]*)">',s).group(1);self.assertTrue(100<=len(d)<=160,(r,len(d)))
    def test_article_page(self):
        m=main('summa/1/q2/a3/index.html')
        self.assertIn('<h1>Whether God Exists?</h1>',m)
        self.assertIn('href="/#/read/summa-theologiae/pg-17611/%d/%d"'%(S['parts'][0]['questions'][1]['articles'][2]['heading']//35,S['parts'][0]['questions'][1]['articles'][2]['heading']),m)
        self.assertIn('href="https://www.newadvent.org/summa/1002.htm#article3"',m)
        self.assertIn('rel="prev" href="/summa/1/q2/a2/"',m);self.assertIn('rel="next" href="/summa/1/q3/a1/"',m)
        self.assertIn('<em>I answer that,</em> The existence of God can be proved in five ways.',m)
        self.assertIn('href="/summa/1/q2/"',m);self.assertIn('href="/author/thomas-aquinas/"',m)
        self.assertNotIn('newadvent.org/summa/1002.htm"',main('summa/1/q2/a3/index.html').replace('1002.htm#','x'))
        last=main('summa/1/q119/a2/index.html');self.assertIn('rel="next" href="/summa/1-2/q1/a1/"',last)  # across parts
        self.assertIn('rel="next" href="/summa/supp/q1/a1/"',main('summa/3/q90/a4/index.html'))  # on into the Supplement
        self.assertNotIn('rel="next"',main('summa/supp/q99/a5/index.html'))
    def test_question_part_and_index(self):
        m=main('summa/1/q2/index.html')
        self.assertIn('<h1>Question 2. The Existence of God</h1>',m)
        for k in (1,2,3):self.assertIn('href="/summa/1/q2/a%d/"'%k,m)
        self.assertIn('https://www.newadvent.org/summa/1002.htm"',m)
        p=main('summa/1-2/index.html');self.assertIn('<h2>Prologue</h2>',p);self.assertIn('<h3>Treatise on Law</h3>',p);self.assertIn('href="/summa/1-2/q90/"',p)
        i=main('summa/index.html')
        for P in S['parts']:self.assertIn('href="/summa/%s/"'%P['slug'],i)
        self.assertIn('Supplement',i);self.assertIn('question 90',i);self.assertIn('sample check',i);self.assertIn('href="/summa/supp/"',main('summa/3/index.html'));self.assertIn('the Supplement is a separate edition here',W['editions'][3]['note']);self.assertIn('corpusthomisticum.org',i);self.assertIn('newadvent.org/summa/',i)
        self.assertIn('href="/summa/"',main('work/summa-theologiae/index.html'))
    def test_app_keeps_summa_static(self):
        app=R('app.js');self.assertRegex(app,r'function staticOnly\(path\)\{.*summa')
        self.assertIn("python3 tools/build_summa.py",R('package.json'));self.assertIn('data/summa.json',R('.github/workflows/validate.yml'))
if __name__=='__main__':unittest.main()
