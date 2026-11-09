"""Deep-link gaps (2026-11-09): chapter and story pages for hosted texts (tools/text_pages.py).

Orthodoxy's nine chapters are mapped onto the hosted Project Gutenberg #130 file (the 1908 text; it replaced the
1934-reprint #16769 on 2026-11-09). Each page is a real static page: in the sitemap, one H1, its own canonical, the
Gutenberg notice (the Standard Ebooks notice for The Incredulity of Father Brown), the hosted text of exactly
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
    def test_orthodoxy_nine_chapters_on_the_hosted_130(self):
        d=TP['orthodoxy'];self.assertEqual(d['edition'],'pg-130');self.assertEqual(d['kind'],'ch')
        self.assertEqual([x['slug'] for x in d['items']],['01-introduction-in-defence-of-everything-else','02-the-maniac','03-the-suicide-of-thought','04-the-ethics-of-elfland','05-the-flag-of-the-world','06-the-paradoxes-of-christianity','07-the-eternal-revolution','08-the-romance-of-orthodoxy','09-authority-and-the-adventurer'])
        self.assertEqual([x['num'] for x in d['items']],['I','II','III','IV','V','VI','VII','VIII','IX'])
        self.assertEqual([x['id'] for x in LIB['orthodoxy']['editions']],['pg-130'])  # no 1934 reprint is hosted or listed
        e=next(x for x in LIB['orthodoxy']['editions'] if x['id']=='pg-130')
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
                if 'gutenberg.org' in e['source']:self.assertIn('class="small pg-notice">This eBook is for the use of anyone anywhere in the United States',m,f)
                else:self.assertIn('class="small pg-notice">This text comes from the Standard Ebooks edition',m,f);self.assertNotIn('Project Gutenberg License',m,f)
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
    def test_father_brown_story_pages(self):
        self.assertEqual({k:(TP[k]['edition'],len(TP[k]['items'])) for k in TP if 'father-brown' in k},
                         {'innocence-father-brown':('pg-204',12),'wisdom-father-brown':('pg-223',12),'incredulity-father-brown':('se-incredulity-father-brown',8),'secret-father-brown':('pg-70175',10)})
        self.assertEqual(TP['innocence-father-brown']['items'][0]['slug'],'01-the-blue-cross')
        self.assertEqual(TP['wisdom-father-brown']['items'][-1]['slug'],'12-the-fairy-tale-of-father-brown')
        sec=TP['secret-father-brown']['items'];self.assertEqual((sec[0]['slug'],sec[-1]['slug']),('00-the-secret-of-father-brown','09-the-secret-of-flambeau'))
        self.assertEqual([x['num'] for x in sec],['Opening frame story']+[str(i) for i in range(1,9)]+['Closing frame story'])
        self.assertEqual([x['slug'] for x in TP['incredulity-father-brown']['items']],['01-the-resurrection-of-father-brown','02-the-arrow-of-heaven','03-the-oracle-of-the-dog','04-the-miracle-of-moon-crescent','05-the-curse-of-the-golden-cross','06-the-dagger-with-wings','07-the-doom-of-the-darnaways','08-the-ghost-of-gideon-wise'])
        for wid in ('innocence-father-brown','wisdom-father-brown','incredulity-father-brown','secret-father-brown'):
            d=TP[wid];self.assertEqual(d['kind'],'story')
            for a,b in zip(d['items'],d['items'][1:]):self.assertLessEqual(b['heading']-a['end'],2)  # at most a bare numeral between stories
    def test_secret_is_hosted_with_pre_1931_evidence(self):
        w=LIB['secret-father-brown'];e=w['editions'][0];self.assertEqual(e['id'],'pg-70175')
        raw=(ROOT/e['text']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),e['sha256'])
        self.assertIn(b'First Published in 1927',raw);self.assertIn('1927',e['note']);self.assertEqual(w['date'],'1927')
        src=json.loads(R('data/sources/pg-70175.json'));self.assertEqual(src['metadata']['Copyright'],['Public domain in the USA.'])
        self.assertEqual(src['metadata']['Original Publication'],['United Kingdom: Cassell and Company, 1927.'])
    def test_incredulity_is_hosted_and_scandal_is_never_a_work(self):
        w=LIB['incredulity-father-brown'];self.assertEqual(w['added'],'2026-11-09')
        self.assertEqual([(e['id'],bool(e.get('text'))) for e in w['editions']],[('se-incredulity-father-brown',True),('ia-incredulityoffat0000ches',False)])
        self.assertIn('incredulity-father-brown',TP);self.assertTrue((ROOT/'work/incredulity-father-brown/story').exists())
        wm=main('work/incredulity-father-brown/index.html')
        self.assertNotIn('full text here is coming',wm);self.assertNotIn('text here is coming',R('data/library.json'))
        self.assertIn('/#/read/incredulity-father-brown/se-incredulity-father-brown',wm)
        self.assertFalse(any('scandal' in k for k in LIB))
        S=json.loads(R('data/library.json'))['series'][0]
        self.assertEqual([(i['title'].split(' of ')[0],i['year'],bool(i['workId'])) for i in S['items']],
                         [('The Innocence',1911,True),('The Wisdom',1914,True),('The Incredulity',1926,True),('The Secret',1927,True),('The Scandal',1935,False)])
        for wid in ('innocence-father-brown','wisdom-father-brown','incredulity-father-brown','secret-father-brown'):
            m=main('work/%s/index.html'%wid);self.assertIn('<h2>The Father Brown collections</h2>',m)
            self.assertIn('The Scandal of Father Brown (1935)',m);self.assertIn('after this library’s 1931 cutoff',m)
        for p in PAGES:self.assertNotIn('gutenberg.net.au',R(p),p)
if __name__=='__main__':unittest.main()
