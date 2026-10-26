"""v18 licensing, attribution, credits, Isidore folder links, non-affiliation, and 1931 wording."""
import json,re,unittest,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
R=lambda p:(ROOT/p).read_text(encoding='utf-8')
def main(s):return s[s.index('<main'):s.index('</main>')]
def footer(s):return s[s.index('<footer'):s.index('</footer>')]
class Licensing(unittest.TestCase):
    def test_license_files_and_package_field(self):
        self.assertTrue(R('LICENSE').startswith('MIT License'))
        lic=R('LICENSING.md')
        for k in('not legal advice','draft','MIT','CC0','CC BY 4.0','CC BY-SA 4.0','data/library.json','data/catholic-hub.json','data/data.js','Project Gutenberg','Wikimedia Commons','no license'):self.assertIn(k,lic)
        self.assertEqual(json.loads(R('package.json')).get('license'),'MIT')
        self.assertIn('## License',R('README.md'))
        self.assertIn('NOTICE.md',R('tools/build_text_archive.py'))
        t=R('tools/build_text_archive.py');self.assertNotIn('catalog metadata in the main repository is CC0',t)  # v18.2: CC0 scope as in LICENSING.md
        self.assertIn('only the open data in `data/open/` and the reading catalog metadata in `data/library.json` are CC0',t)
    def test_library_json_cc0_only_while_free_of_wikipedia_text(self):
        lib=R('data/library.json');hub=json.loads(R('data/catholic-hub.json'))
        self.assertNotIn('wikipedia',lib.lower())
        for a in hub['authors']:
            if a.get('extract'):self.assertNotIn(a['extract'][:80],lib)
        for p in('data/open/authors.json',):self.assertNotIn('"extract"',R(p))
    def test_footer_links_on_every_page(self):
        for p in('index.html','about/index.html','author/augustine-of-hippo/index.html','isidore/index.html'):
            f=footer(R(p))
            with self.subTest(p):
                self.assertIn('<a href="/licensing/">Licensing &amp; credits</a>',f);self.assertNotIn('LICENSING.md',f);self.assertIn('https://creativecommons.org/licenses/by-sa/4.0/',f)
                self.assertIn('code MIT, open data CC0, site writing CC BY 4.0, hosted texts public domain in the US',f)
                self.assertIn('href="https://en.wikipedia.org/"',f)
                self.assertIn('is an independent project and is not affiliated with other projects of a similar name',f)
                self.assertNotIn('—',f[f.index('non-affiliation'):])
    def test_about_names_both_unaffiliated_projects_and_softens_1931(self):
        m=main(R('about/index.html'))
        for k in('IntraText','Bibliotheca Catholica” collection','Minha Biblioteca Católica','bibliotecacatolica.com.br','intratext.com','not affiliated','later reprint','not legal advice'.replace('not legal advice','summary rather than legal advice')):self.assertIn(k,m)
        self.assertNotIn('We host only works published before 1931',m)
        self.assertNotIn('public-domain editions published before 1931',main(R('index.html')))
    def test_wikipedia_credit_on_author_pages(self):
        app=R('app.js');self.assertIn('Shortened excerpt from the Wikipedia article',app);self.assertIn("CC_BY_SA='https://creativecommons.org/licenses/by-sa/4.0/'",app)
        hub=json.loads(R('data/catholic-hub.json'))
        ids=[a['id'] for a in hub['authors'] if a.get('extract')]
        n=0
        for i in ids:
            f=ROOT/'author'/i/'index.html'
            if not f.exists():continue
            s=main(f.read_text());n+=1
            with self.subTest(i):
                self.assertIn('Shortened excerpt from the Wikipedia article',s)
                self.assertIn('href="https://creativecommons.org/licenses/by-sa/4.0/"',s)
                self.assertRegex(s,r'<a href="https://en\.wikipedia\.org/wiki/[^"]+" target="_blank" rel="noopener">“')
                lede=re.search(r'<p class="lede">(.*?)</p>',s).group(1)
                a=next(x for x in hub['authors'] if x['id']==i)
                self.assertNotIn(a['extract'][:60].replace('&','&amp;'),lede)
        self.assertGreater(n,400)
    def test_portraits_need_credits(self):
        hub=json.loads(R('data/catholic-hub.json'));pc=json.loads(R('data/portrait-credits.json'))
        for a in hub['authors']:
            c=a.get('imgCredit')
            if not c:continue
            with self.subTest(a['id']):
                self.assertTrue(a.get('img'));self.assertTrue(c['page'].startswith('https://'));self.assertTrue(c['license'])
                self.assertNotRegex(c['license'],r'(?i)fair use|non-free')
                self.assertTrue(c.get('artist') or c.get('pd'))
                self.assertTrue(pc['files'][a['id']]['shown'])
        app=R('app.js');self.assertIn('function portraitOk(a,full){return !!(a.img&&a.imgCredit&&(full||a.imgCredit.pd))}',app)
        self.assertIn("avatar(a,null,1)",app);self.assertIn('portraitCredit(a)',app)
    def test_no_raw_isidore_folder_links(self):
        for p in('data/catholic-hub.json','data/data.js','tools/resources.py','data/open/isidore-folders.json','data/open/authors.json','app.js'):
            self.assertNotRegex(R(p),r'isidore\.co/CalibreLibrary/[^"\s]',p)
        self.assertIn('does not vouch for',R('app.js'));self.assertIn('does not vouch for',main(R('rights/index.html')));self.assertIn('does not vouch for',main(R('isidore/index.html')))
        self.assertIn('>Isidore Index</a>',R('index.html'));self.assertNotIn('Ebooks &amp; PDFs',R('index.html'))

class V181(unittest.TestCase):
    def test_licensing_page_renders_licensing_md_and_is_in_sitemap(self):
        m=main(R('licensing/index.html'))
        self.assertEqual(m.count('<h1'),1);self.assertIn('Licensing (draft)',m);self.assertIn('not legal advice',m)
        for k in('MIT','CC0 1.0','CC BY 4.0','CC BY-SA 4.0','Project Gutenberg License','data/library.json','does not vouch for'):self.assertIn(k,m)
        self.assertIn('<loc>https://bibliothecacatholica.com/licensing/</loc>',R('sitemap.xml'))
        self.assertIn("case 'licensing':rightsPage(p[0])",R('app.js'))
    def test_cc0_scope_matches_in_license_txt_and_licensing_md(self):
        t=R('data/open/LICENSE.txt');self.assertIn('data/open/',t);self.assertIn('data/library.json',t)
        self.assertIn('`data/open/LICENSE.txt` names it',R('LICENSING.md'))
    def test_portrait_credit_names_are_tidy(self):
        import re
        hub=json.loads(R('data/catholic-hub.json'));n=0
        for a in hub['authors']:
            c=a.get('imgCredit')
            if not c or 'artist' not in c:continue
            n+=1;t=c['artist']
            with self.subTest(a['id']):
                self.assertNotRegex(t,r'(?i)not specified')
                self.assertNotRegex(t,r'(?i)\b(\w[\w.]*(?: \w[\w.]*){0,4}) \1\b')
                self.assertNotRegex(t,r'(?i)^(unknown|anonymous)( (author|artist|photographer))?$')
        self.assertGreater(n,80)
        files=json.loads(R('data/portrait-credits.json'))['files']
        self.assertEqual(files['roger-bacon']['license'],'CC BY-SA 3.0');self.assertFalse(files['roger-bacon']['shown'])
        self.assertNotIn('imgCredit',next(a for a in hub['authors'] if a['id']=='roger-bacon'))
    def test_former_folder_authors_link_to_their_index_search(self):
        hub=json.loads(R('data/catholic-hub.json'));names={i['f']:i.get('a') or i['n'] for i in hub['isidore']}  # v18.2: the books' author name
        A=[a for a in hub['authors'] if a.get('isidoreFolder')];self.assertEqual(len(A),211)
        import urllib.parse
        for a in A[:400]:
            with self.subTest(a['id']):
                self.assertIn('href="/#/isidore/author='+urllib.parse.quote(names[a['isidoreFolder']],safe='')+'"',main(R('author/'+a['id']+'/index.html')))
        self.assertIn("All their books in the Isidore Index",R('app.js'))

class V182(unittest.TestCase):
    """v18.2 QA fixes: Isidore names from the books, /licensing/ table and self-link, portrait-credits fields, era shown once."""
    def test_isidore_names_from_books(self):
        hub=json.loads(R('data/catholic-hub.json'));I={i['f']:i for i in hub['isidore']}
        self.assertEqual(I['Wojtyla, Karol']['a'],'Wojtyła, Karol')
        self.assertEqual(I['Angela of Foligno, Bl., 1248_-1309']['a'],'Angela of Foligno, Bl., 1248?-1309')
        self.assertEqual(I['Llull, Ramon, 1232_-1316']['a'],'Llull, Ramon, 1232?-1316')
        self.assertEqual(I['Kierkegaard, Soren']['a'],'Kierkegaard, Søren')
        import csv,io
        rows=list(csv.DictReader(io.StringIO(R('data/open/isidore-folders.csv'))))
        w=next(r for r in rows if r['folder']=='Wojtyla, Karol');self.assertTrue(w['index_url'].endswith('#/isidore/author=Wojty%C5%82a%2C%20Karol'))
    def test_licensing_page_stacks_and_has_no_self_link(self):
        s=R('licensing/index.html');page=s[s.index('<main'):]
        self.assertNotIn('also shown on the site at',page)
        self.assertIn('also shown on the site at',R('LICENSING.md'))
        self.assertIn('<td data-label="Terms">',page);self.assertIn('<td data-label="Material">',page)
        css=R('styles/rights.css');self.assertIn('.licensing-table td::before{content:attr(data-label)',css)
        self.assertRegex(css,r'@media \(max-width:640px\)\{\s*\.licensing-table thead')
    def test_portrait_credits_fields(self):
        import re
        pc=json.loads(R('data/portrait-credits.json'));self.assertIn('fields',pc)
        for k,r in pc['files'].items():
            with self.subTest(k):
                self.assertIn('artistRaw',r);self.assertNotIn('credit',r)
                self.assertNotRegex(r['artist'],r'(?i)not specified')
                self.assertNotRegex(r['artist'],r'(?i)\b(\w[\w.]*(?: \w[\w.]*){0,4}) \1\b')
        self.assertEqual(sum(1 for r in pc['files'].values() if r['shown'] and r['artist']=='Author unknown'),87)
        self.assertEqual(pc['files']['mary-ann-glendon']['artist'],'United States Department of State')
        self.assertIn('`artistRaw`',R('LICENSING.md'));self.assertIn('87',R('AGENTS.md'))
    def test_era_shown_once(self):
        self.assertIn("a.era!==ord(a.century)+'-century'",R('app.js'))
        s=R('author/john-paul-ii/index.html')
        self.assertNotIn('Twentieth Century (20th century)',s)

if __name__=='__main__':unittest.main()
