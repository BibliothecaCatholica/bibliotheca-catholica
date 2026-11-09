"""Deep-link gaps (2026-11-09): chapter and story pages for hosted texts (tools/text_pages.py).

Orthodoxy's nine chapters are mapped onto the hosted Project Gutenberg #16769 file. Each page is a real
static page: in the sitemap, one H1, its own canonical, the Gutenberg notice, the hosted text of exactly
that part, a link into the reader at the part's heading, and links back to the work and to the
previous and next parts. The work page lists every part."""
import hashlib,json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SITE='https://bibliothecacatholica.com/'
sys.path.insert(0,str(ROOT/'tools'))
import build_text_pages as BTP
R=lambda p:(ROOT/p).read_text()
TP=json.loads(R('data/text-pages.json'))['works'];LIB={w['id']:w for w in json.loads(R('data/library.json'))['works']}
SITEMAP=R('sitemap.xml');PAGES=set(R('docs/static-pages.txt').split())
def main(p):s=R(p);return s[s.find('<main'):s.find('</main>')]
def path(wid,d,x):return 'work/%s/%s/%s/'%(wid,d['kind'],x['slug'])
class TextPages(unittest.TestCase):
    def test_data_is_current(self):
        self.assertEqual(BTP.build(),TP)
        js=R('data/text-pages.js');self.assertTrue(js.startswith('window.TEXT_PAGES='))
        slim=json.loads(js[len('window.TEXT_PAGES='):].rstrip().rstrip(';'))
        for wid,d in TP.items():self.assertEqual([i[0] for i in slim[wid]['i']],[x['slug'] for x in d['items']])
    def test_orthodoxy_nine_chapters_on_the_hosted_16769(self):
        d=TP['orthodoxy'];self.assertEqual(d['edition'],'pg-16769');self.assertEqual(d['kind'],'ch')
        self.assertEqual([x['slug'] for x in d['items']],['01-introduction-in-defence-of-everything-else','02-the-maniac','03-the-suicide-of-thought','04-the-ethics-of-elfland','05-the-flag-of-the-world','06-the-paradoxes-of-christianity','07-the-eternal-revolution','08-the-romance-of-orthodoxy','09-authority-and-the-adventurer'])
        self.assertEqual([x['num'] for x in d['items']],['I','II','III','IV','V','VI','VII','VIII','IX'])
        e=next(x for x in LIB['orthodoxy']['editions'] if x['id']=='pg-16769')
        self.assertEqual(hashlib.sha256((ROOT/e['text']).read_bytes()).hexdigest(),d['sha256'])
        B=BTP.split_text((ROOT/e['text']).read_text(encoding='utf-8'))
        for x,(_,_,title,head,first,last) in zip(d['items'],BTP.TP.WORKS['orthodoxy']['parts']):
            self.assertEqual(BTP.norm(B[x['heading']]),BTP.norm(head))
            self.assertTrue(BTP.norm(B[x['start']]).startswith(BTP.norm(first)),title)
            self.assertTrue(BTP.norm(B[x['end']]).endswith(BTP.norm(last)),title)
        # chapters tile the body: each ends right before the next heading, the last right before the END marker
        for a,b in zip(d['items'],d['items'][1:]):self.assertEqual(a['end']+1,b['heading'])
        self.assertRegex(B[d['items'][-1]['end']+1],r'\*\*\* END OF THE PROJECT GUTENBERG')
    def test_pages_are_real_static_pages(self):
        for wid,d in TP.items():
            w=LIB[wid];e=next(x for x in w['editions'] if x['id']==d['edition'])
            B=BTP.split_text((ROOT/e['text']).read_text(encoding='utf-8'));n=len(d['items'])
            wm=main('work/%s/index.html'%wid)
            for k,x in enumerate(d['items']):
                p=path(wid,d,x);f=p+'index.html';self.assertIn(f,PAGES);self.assertIn('<loc>'+SITE+p+'</loc>',SITEMAP)
                s=R(f);m=main(f)
                self.assertEqual(s.count('googletagmanager.com/gtag/js'),1,f)
                self.assertIn('<link rel="canonical" href="'+SITE+p+'">',s);self.assertIn('<meta name="robots" content="index,follow">',s)
                self.assertIn('window.BC_BOOT='+json.dumps(p.rstrip('/')),s)
                self.assertEqual(m.count('<h1>'),1);self.assertIn('<h1>'+x['title'].replace('&','&amp;')+'</h1>',m)
                self.assertIn('class="small pg-notice">This eBook is for the use of anyone anywhere in the United States',m,f)
                self.assertIn('href="/#/read/%s/%s/%d/%d"'%(wid,e['id'],x['heading']//35,x['heading']),m)
                self.assertIn('href="/work/%s/"'%wid,m);self.assertIn('href="/rights/"',m)
                if k:self.assertIn('rel="prev" href="/'+path(wid,d,d['items'][k-1])+'"',m)
                else:self.assertNotIn('rel="prev"',m)
                if k+1<n:self.assertIn('rel="next" href="/'+path(wid,d,d['items'][k+1])+'"',m)
                else:self.assertNotIn('rel="next"',m)
                art=m[m.index('<article class="reading-text"'):m.index('</article>')]
                self.assertEqual(art.count('<p>'),x['end']-x['start']+1,f)
                import html as H
                self.assertIn('<p>'+H.escape(B[x['start']])+'</p>',art);self.assertIn('<p>'+H.escape(B[x['end']])+'</p>',art)
                self.assertNotIn('<p>'+H.escape(B[x['end']+1])+'</p>',art)
                self.assertNotIn('data-ga',m);self.assertNotIn('amazon.',m)
                self.assertIn('href="/'+p+'"',wm,'work page lists '+p)
                ld=[json.loads(j) for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s)]
                part=[j for j in ld if j['@type'] in('Chapter','ShortStory')][0]
                self.assertEqual(part['url'],SITE+p);self.assertEqual(part['isPartOf']['url'],SITE+'work/%s/'%wid)
    def test_no_em_dashes_in_our_page_copy(self):
        for wid,d in TP.items():
            for x in d['items']:
                m=main(path(wid,d,x)+'index.html');m=m[:m.find('<article')]+m[m.find('</article>'):]
                self.assertNotIn('—',m.replace('— Bibliotheca Catholica',''),path(wid,d,x))
    def test_app_keeps_the_static_page_and_mirrors_the_contents(self):
        app=R('app.js');lib=R('scripts/library.js')
        self.assertIn("if(staticOnly(h)){keepStatic(h);return}",app)
        self.assertIn('function partsList(w)',lib);self.assertIn('+partsList(w)+',lib)
        self.assertRegex(R('index.html'),r'<script defer src="data/text-pages\.js\?v=[0-9a-f]{10}"></script>')
if __name__=='__main__':unittest.main()
