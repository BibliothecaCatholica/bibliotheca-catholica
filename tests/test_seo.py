"""v17 SEO checks on the pre-rendered pages (what a crawler sees without JavaScript). See docs/SEO.md."""
import json,re,unittest,collections
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SITE='https://bibliothecacatholica.com/'
class P(HTMLParser):
    def __init__(s):
        super().__init__();s.stack=[];s.title='';s.h1=0;s.h1t='';s.meta={};s.canon=[];s.ld=[];s.cur=None;s.text=[];s.inmain=0;s.imgs=[]
    def handle_starttag(s,t,a):
        a=dict(a);s.stack.append(t)
        if t=='main':s.inmain+=1
        if t=='h1':s.h1+=1
        if t=='meta' and (a.get('name') or a.get('property')):s.meta.setdefault(a.get('name') or a.get('property'),[]).append(a.get('content') or '')
        if t=='link' and a.get('rel')=='canonical':s.canon.append(a.get('href'))
        if t=='script' and a.get('type')=='application/ld+json':s.cur=''
        if t=='img':s.imgs.append(a)
    def handle_endtag(s,t):
        if t=='script' and s.cur is not None:s.ld.append(s.cur);s.cur=None
        if t=='main':s.inmain-=1
        while s.stack and s.stack.pop()!=t:pass
    def handle_data(s,d):
        if s.cur is not None:s.cur+=d;return
        if 'title' in s.stack:s.title+=d
        if 'h1' in s.stack:s.h1t+=d
        if s.inmain and not any(x in s.stack for x in('script','style','noscript')):s.text.append(d)
def parse(rel):
    p=P();p.feed((ROOT/rel).read_text());return p
PAGES=['index.html']+(ROOT/'docs/static-pages.txt').read_text().split()
PARSED={r:parse(r) for r in PAGES}
class SEO(unittest.TestCase):
    def test_unique_titles_and_descriptions(self):
        t=collections.Counter(p.title.strip() for p in PARSED.values());d=collections.Counter(p.meta['description'][0] for p in PARSED.values())
        self.assertEqual([k for k,v in t.items() if v>1],[]);self.assertEqual([k for k,v in d.items() if v>1],[])
    def test_titles_name_the_site(self):
        for r,p in PARSED.items():self.assertIn('Bibliotheca Catholica',p.title,r)
    def test_description_length(self):
        for r,p in PARSED.items():
            self.assertEqual(len(p.meta['description']),1,r);self.assertTrue(120<=len(p.meta['description'][0])<=160,(r,len(p.meta['description'][0])))
        self.assertTrue(150<=len(PARSED['index.html'].meta['description'][0])<=160)
    def test_one_h1_canonical_og_twitter(self):
        for r,p in PARSED.items():
            self.assertEqual(p.h1,1,r);self.assertEqual(len(p.canon),1,r)
            route=r[:-len('index.html')]
            self.assertEqual(p.canon[0],SITE+route,r);self.assertEqual(p.meta['og:url'],[SITE+route],r)
            for k in('og:title','og:description','og:image','twitter:card','twitter:title','twitter:description','twitter:image'):self.assertEqual(len(p.meta.get(k,[])),1,(r,k))
            self.assertEqual(p.meta['og:image'],[SITE+'assets/og-image.png'])
            self.assertEqual(p.meta['robots'],['index,follow'],r)
    def test_home_is_a_real_landing_page(self):
        p=PARSED['index.html'];self.assertIn('Bibliotheca Catholica',p.h1t)
        words=len(' '.join(p.text).split());self.assertGreaterEqual(words,200)
        s=(ROOT/'index.html').read_text();main=s[s.index('<main'):s.index('</main>')]
        self.assertNotIn('class="loading"',main)
        for href in('/library/','/authors/','/saints/','/editions/','/reading/','/isidore/','/about/','/policy/','/rights/','/takedown/','/support/','/timeline/','/doctors/','/data/'):self.assertIn('href="'+href+'"',main,href)
        self.assertIn('bibliothecacatholica.com',main)
    def test_home_never_features_flagged_titles(self):
        flags=json.loads((ROOT/'data/editorial-flags.json').read_text())
        s=(ROOT/'index.html').read_text()+(ROOT/'data/site-copy.js').read_text()
        for k in flags['books']:self.assertNotIn('isidore/book/'+k+'"',s)
    def test_jsonld_parses_and_is_accurate(self):
        hub={a['id']:a for a in json.loads((ROOT/'data/catholic-hub.json').read_text())['authors']}
        for r,p in PARSED.items():
            self.assertTrue(p.ld,r)
            for x in p.ld:
                j=json.loads(x);self.assertEqual(j['@context'],'https://schema.org',r)
                if j['@type']=='BreadcrumbList':
                    self.assertEqual(j['itemListElement'][0]['item'],SITE);self.assertEqual(j['itemListElement'][-1]['item'],p.canon[0],r)
                if j['@type']=='Person':
                    a=hub[r.split('/')[1]];self.assertEqual(j['name'],a['name'])
                    if 'birthDate' in j:self.assertEqual(int(j['birthDate']),a['born'])
                    if 'deathDate' in j:self.assertEqual(int(j['deathDate']),a['died'])
        home=[json.loads(x) for x in PARSED['index.html'].ld];types=[j['@type'] for j in home]
        self.assertEqual(sorted(types),['Organization','WebSite'])
        self.assertFalse(any('potentialAction' in j for j in home))  # no SearchAction: the site search is a hash route
        org=[j for j in home if j['@type']=='Organization'][0]
        self.assertEqual(org['sameAs'],['https://github.com/BibliothecaCatholica','https://bsky.app/profile/bibliothecacatholica.com'])
        self.assertEqual((ROOT/'.well-known/atproto-did').read_text().strip(),'did:plc:phhtp6omv2vh4nua6bkmzaww')
    def test_no_review_or_faq_schema(self):
        for r,p in PARSED.items():
            for x in p.ld:self.assertNotRegex(x,r'"(Review|AggregateRating|FAQPage)"',r)
    def test_index_pages_have_intro_text(self):
        for k in('authors','library','editions','reading','saints','doctors','timeline','isidore'):
            s=(ROOT/k/'index.html').read_text();self.assertIn('class="section-intro"',s,k)
    def test_about_page(self):
        s=(ROOT/'about/index.html').read_text();main=s[s.index('<main'):s.index('</main>')]
        for k in('href="/rights/"','href="/takedown/"','href="/policy/"','href="/support/"','1931','SHA-256','rights badges'):self.assertIn(k,main)
        self.assertIn(SITE+'about/',(ROOT/'sitemap.xml').read_text());self.assertIn('href="/about/"',(ROOT/'index.html').read_text())
        app=(ROOT/'app.js').read_text();self.assertIn("case 'about':",app);self.assertRegex(app,r"STATIC_SECTIONS=\[[^\]]*'about'")
    def test_nav_links_are_crawlable_paths(self):
        s=(ROOT/'index.html').read_text();nav=s[s.index('<header'):s.index('</header>')]+s[s.index('<footer'):s.index('</footer>')]
        self.assertNotRegex(nav,r'href="#/');self.assertIn('href="/authors/"',nav)
    def test_site_copy_matches_static_home(self):
        js=(ROOT/'data/site-copy.js').read_text();c=json.loads(js[len('window.SITE_COPY='):].rstrip().rstrip(';'))
        s=(ROOT/'index.html').read_text();self.assertIn(c['home'],s);self.assertIn('<title>'+c['homeTitle']+'</title>',s)
        self.assertIn(c['about'],(ROOT/'about/index.html').read_text())
    def test_copy_rules(self):
        for f in('index.html','about/index.html','data/site-copy.js','tools/site_copy.py'):
            t=(ROOT/f).read_text().lower();self.assertNotIn('tax-deductible',t);self.assertNotIn('tax deductible',t);self.assertNotIn('amazon.',t)
    def test_images_have_alt(self):
        for r,p in PARSED.items():
            for i in p.imgs:self.assertIn('alt',i,r)
    def test_static_author_pages_skip_raw_isidore_folders(self):
        for r in PAGES:
            if r.startswith('author/'):
                s=(ROOT/r).read_text();self.assertNotRegex(s[s.index('<main'):s.index('</main>')],r'isidore\.co/CalibreLibrary/')
if __name__=='__main__':unittest.main()
