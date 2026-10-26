"""v16 rights badges: data, open datasets, and the /rights and /takedown pages. Not legal advice."""
import csv,json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_rights as BR
RD=json.loads((ROOT/'data/rights.json').read_text())
HOST={k for k,v in BR.STATUSES.items() if v['hostable']}
def js(path,var):
    s=(ROOT/path).read_text();return json.loads(s[len('window.%s='%var):].rstrip().rstrip(';'))
def lum(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)];c=[x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4 for x in c];return .2126*c[0]+.7152*c[1]+.0722*c[2]
def ratio(a,b):
    a,b=lum(a),lum(b);return (max(a,b)+.05)/(min(a,b)+.05)
class RightsData(unittest.TestCase):
    def test_five_statuses_and_hostable_set(self):
        self.assertEqual(list(BR.STATUSES),['public_domain_us','open_license','permission_granted','link_only','unknown'])
        self.assertEqual(HOST,{'public_domain_us','open_license','permission_granted'})
    def test_validates_and_covers_every_record(self):
        ids=BR.validate(RD);self.assertEqual(len(ids),6633)
        self.assertEqual(js('data/rights.js','RIGHTS_DATA'),RD)
    def test_leads_are_never_public_domain(self):
        for code in ('H1','H2','H3','U1a','U1b','U1c','U2','U2a','U3','U4'):
            self.assertEqual(RD['codes'][code]['status'],'unknown',code)
        for code in ('H1','H2','H3','U1a'):self.assertTrue(RD['codes'][code]['text'].startswith('Lead, not confirmed'),code)
        for code in ('L1','L2','L3','L4','L5','L6'):self.assertEqual(RD['codes'][code]['status'],'link_only',code)
    def test_no_hostable_status_without_evidence(self):
        for i,r in RD['records'].items():
            s=BR.status_of(RD,r)
            if s in HOST:
                self.assertIn(r[0],('P1','M'),i);self.assertGreater(len(r[1]),20,i)
                self.assertRegex(BR.checked_of(RD,r),r'^\d{4}-\d{2}-\d{2}$')
    def test_conservative_counts(self):
        from collections import Counter
        c=Counter(BR.status_of(RD,r) for r in RD['records'].values())
        self.assertLessEqual(c['public_domain_us'],20);self.assertEqual(c['open_license']+c['permission_granted'],len([1 for r in RD['records'].values() if r[0]=='M' and r[3] in('open_license','permission_granted')]))
        self.assertEqual(sum(c.values()),6633)
        self.assertEqual(BR.status_of(RD,RD['records']['6248']),'unknown')  # TAN ISBN edition of Lord of the World: needs a person
    def test_matches_carry_status(self):
        im=json.loads((ROOT/'data/isidore-matches.json').read_text())
        self.assertEqual(im,js('data/isidore-matches.js','ISIDORE_MATCHES'))
        for L in im['matches'].values():
            for b in L:self.assertEqual(b['r'],BR.status_of(RD,RD['records'][str(b['id'])]))
class OpenData(unittest.TestCase):
    def test_index_dataset_has_rights_fields_and_gates_files(self):
        rec=json.loads((ROOT/'data/open/isidore-index.json').read_text())['records']
        for r in rec:
            st=BR.status_of(RD,RD['records'][str(r['id'])])
            self.assertEqual(r['rights_status'],st);self.assertTrue(r['rights_evidence']);self.assertRegex(r['rights_checked'],r'^\d{4}-\d{2}-\d{2}$')
            self.assertTrue(r['isidore_book_url'].endswith('/legacy/book/%d/CalibreLibrary'%r['id']))
            if st not in HOST:self.assertEqual(r['download_urls'],[]);self.assertIsNone(r['isidore_files_url'])
        head=(ROOT/'data/open/isidore-index.csv').read_text(encoding='utf-8').split('\n',1)[0].split(',')
        for k in ('rights_status','rights_evidence','rights_checked'):self.assertIn(k,head)
        man=(ROOT/'data/open/manifest.json').read_text()+(ROOT/'data/open/README.md').read_text()
        for k in ('rights_status','rights_evidence','rights_checked'):self.assertIn(k,man)
class Pages(unittest.TestCase):
    def test_static_pages(self):
        for k in ('rights','takedown'):
            s=(ROOT/k/'index.html').read_text()
            self.assertIn('This is not legal advice.',s,k)
            self.assertEqual(s.count('googletagmanager.com/gtag/js'),1,k);self.assertIn("'send_page_view': false",s)
            self.assertIn("window.BC_BOOT=\"%s\""%k,s)
            self.assertNotRegex(s.lower(),r'tax[- ]deductible|amazon\.|amzn\.')
            self.assertIn('<loc>https://bibliothecacatholica.com/%s/</loc>'%k,(ROOT/'sitemap.xml').read_text())
            self.assertIn('%s/index.html'%k,(ROOT/'docs/static-pages.txt').read_text())
    def test_takedown_placeholder_not_invented(self):
        s=(ROOT/'takedown/index.html').read_text();body=s[s.index('<main'):s.index('</main>')]
        self.assertIn('PLACEHOLDER: designated takedown agent',body)
        self.assertNotIn('mailto:',body)  # the owner adds the agent contact
        for k in ('512(c)(3)','512(g)(3)','penalty of perjury','good faith'):self.assertIn(k,body)
    def test_rights_page_explains(self):
        s=(ROOT/'rights/index.html').read_text()
        for k in ('Public domain (US)','Open license','Permission granted','Link only','Unknown','1931','#/policy','checked','may not be in the public domain in your country'):self.assertIn(k,s)
    def test_app_routes_and_footer(self):
        app=(ROOT/'app.js').read_text();html=(ROOT/'index.html').read_text()
        self.assertIn("case 'rights':case 'takedown':case 'licensing':rightsPage(p[0])",app)
        self.assertRegex(app,r"STATIC_SECTIONS=\[[^\]]*'rights','takedown'")
        # v17: footer links are real paths (app.js routes them as hashes on the home page)
        self.assertIn('href="/rights/">Rights &amp; Permissions</a>',html);self.assertIn('href="/takedown/">Takedown requests</a>',html)
        self.assertLess(html.index('scripts/rights.js'),html.index('scripts/library.js'))
        P=js('data/rights-pages.js','RIGHTS_PAGES')
        for k in ('rights','takedown'):self.assertIn(P[k],(ROOT/k/'index.html').read_text())
    def test_badge_contrast_aa_light_and_dark(self):
        css=(ROOT/'styles/rights.css').read_text()
        pairs=re.findall(r'(\[data-theme=dark\] )?\.rb-([a-z-]+)\{color:(#[0-9a-f]{6});background:(#[0-9a-f]{6})',css)
        self.assertEqual(len(pairs),10)
        for dark,k,fg,bg in pairs:self.assertGreaterEqual(ratio(fg,bg),4.5,(k,dark))
        for _,k,fg,_ in [p for p in pairs if not p[0]]:self.assertGreaterEqual(ratio(fg,'#fffaf0'),4.5,k)
        for _,k,fg,_ in [p for p in pairs if p[0]]:self.assertGreaterEqual(ratio(fg,'#1f232c'),4.5,k)
    def test_books_js_not_bloated(self):
        self.assertNotIn('rights',(ROOT/'data/books.js').read_text()[:2000])
        self.assertLess((ROOT/'data/rights.js').stat().st_size,300_000)
if __name__=='__main__':unittest.main()
