"""Deep-link gaps (2026-11-09): author pages for four writers outside the Catholic communion whose books are in the
reading room (Baring-Gould, Jameson, Canton, Sabatier), from Research's deep-link-gaps-2026-11-09.json. Each page
carries the "Non-Catholic Christian" badge with its tradition, the sourced bio, links to the works here, and the
not-endorsement line; Sabatier's Life gets a calm context note in the editorial-note style. They are never listed
as Catholic Authors, Doctors, or on the timeline."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SITE='https://bibliothecacatholica.com/'
R=lambda p:(ROOT/p).read_text()
LIB=json.loads(R('data/library.json'));RA={a['id']:a for a in LIB['relatedAuthors']};W={w['id']:w for w in LIB['works']}
HUB={a['id'] for a in json.loads(R('data/catholic-hub.json'))['authors']}
def main(p):s=R(p);return s[s.find('<main'):s.find('</main>')]
class RelatedAuthors(unittest.TestCase):
    def test_the_four_authors_and_badges(self):
        self.assertEqual({k:a['tradition'] for k,a in RA.items()},{'sabine-baring-gould':'Anglican','anna-jameson':'Anglican','william-canton':'Protestant','paul-sabatier':'Protestant (French Reformed)'})
        for k,a in RA.items():
            self.assertEqual(a['badge'],'Non-Catholic Christian');self.assertNotIn(k,HUB)
            self.assertTrue(a['workIds']);self.assertEqual(a['checked'],'2026-11-09')
    def test_static_pages(self):
        sm=R('sitemap.xml');pages=R('docs/static-pages.txt').split()
        for k,a in RA.items():
            f='author/%s/index.html'%k;self.assertIn(f,pages);self.assertIn('<loc>%sauthor/%s/</loc>'%(SITE,k),sm)
            s=R(f);m=main(f)
            self.assertEqual(s.count('googletagmanager.com/gtag/js'),1)
            self.assertIn('<link rel="canonical" href="%sauthor/%s/">'%(SITE,k),s)
            self.assertIn('Non-Catholic Christian · '+a['tradition'].replace('&','&amp;'),m)
            self.assertIn('Listing is not endorsement',m);self.assertIn('href="/policy/"',m);self.assertIn('href="/related/"',m)
            for wid in a['workIds']:self.assertIn('href="/work/%s/"'%wid,m)
            self.assertNotIn('amazon.',m);self.assertNotIn('bookshop.org',m);self.assertNotIn('data-ga',m)
            self.assertNotIn('—',m)
            ld=[json.loads(j) for j in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s)]
            p=[j for j in ld if j['@type']=='Person'][0];self.assertEqual((p['name'],int(p['birthDate']),int(p['deathDate'])),(a['name'],a['born'],a['died']))
            for wid in a['workIds']:
                wm=main('work/%s/index.html'%wid);self.assertIn('href="/author/%s/"'%k,wm,wid);self.assertIn('Non-Catholic Christian',wm)
    def test_sabatier_context_note(self):
        a=RA['paul-sabatier'];self.assertEqual(a['noteWorks'],['sabatier-francis'])
        for f in ('author/paul-sabatier/index.html','work/sabatier-francis/index.html'):
            m=main(f);self.assertIn('<div class="ef-box"><div class="ef-h">Context note</div>',m,f)
            self.assertIn('not a Catholic hagiography',m);self.assertIn('href="/work/chesterton-francis/"',m)
        self.assertNotIn('Dignitatis',main('author/paul-sabatier/index.html'))  # a context note, not a fringe flag
        for k in ('sabine-baring-gould','anna-jameson','william-canton'):self.assertNotIn('ef-box',main('author/%s/index.html'%k))
    def test_never_catholic_authors(self):
        for f in ('authors/index.html','doctors/index.html','timeline/index.html'):
            for k in RA:self.assertNotIn('href="/author/%s/"'%k,main(f),f)
        rel=main('related/index.html')
        for k in RA:self.assertIn('href="/author/%s/"'%k,rel)
    def test_app_mirrors(self):
        lib=R('scripts/library.js');app=R('app.js')
        for fn in ('function relatedBy(w)','function relatedNote(w)','function raBadge(r)'):self.assertIn(fn,lib)
        self.assertIn(':relatedBy(w))',lib);self.assertIn('+relatedNote(w)',lib)
        self.assertRegex(app,r'function staticOnly\(path\)\{.*relatedAuthors')
    def test_jameson_reads_anglican_everywhere(self):
        a=RA['anna-jameson'];self.assertEqual(a['tradition'],'Anglican');self.assertNotIn('Protestant',a['desc']+a['bio'])
        for f in ['author/anna-jameson/index.html']+['work/%s/index.html'%w for w in a['workIds']]:
            m=main(f);self.assertIn('Non-Catholic Christian · Anglican',m,f);self.assertNotIn('Protestant',m,f)
        for w in a['workIds']:self.assertEqual(W[w]['tradition'],'Anglican writer')
    def test_secret_father_brown_librivox(self):
        LV=json.loads(R('data/librivox.json'));h=LV['work']['secret-father-brown']
        self.assertEqual([x['id'] for x in h],[19151]);self.assertEqual(h[0]['url'],'https://librivox.org/the-secret-of-father-brown-by-g-k-chesterton/')
        t=json.loads(R('data/librivox/19151.json'));self.assertEqual(len(t['sections']),h[0]['tracks'])
        self.assertTrue(all(x['mp3'].startswith('https://archive.org/download/') for x in t['sections']))
        self.assertIn('"secret-father-brown":[{"id":19151',R('data/librivox.js'))
if __name__=='__main__':unittest.main()
