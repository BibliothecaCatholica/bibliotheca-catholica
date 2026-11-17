"""The /councils/ section (2026-11-17): all twenty-one councils in order, linked from the top of Church Documents
and the footer, never from the main nav; plain own-words summaries without em-dashes; one GA4 tag; no new events."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import councils_page
D=json.loads((ROOT/'data/councils.json').read_text())
PAGE=(ROOT/'councils/index.html').read_text()
class Councils(unittest.TestCase):
    def test_twenty_one_in_order(self):
        C=D['councils'];self.assertEqual([c['n'] for c in C],list(range(1,22)))
        self.assertEqual(len({c['id'] for c in C}),21)
        self.assertEqual(C[0]['name'],'First Council of Nicaea');self.assertEqual(C[-1]['name'],'Second Vatican Council')
        eras={e['id'] for e in D['eras']};self.assertTrue(all(c['era'] in eras for c in C))
        firsts=[int(re.match(r'\d+',c['years']).group(0)) for c in C];self.assertEqual(firsts,sorted(firsts))
    def test_summaries_plain(self):
        for c in D['councils']:
            for f in ('name','years','summary'):self.assertNotIn('—',c[f],c['id'])
            self.assertTrue(20<len(c['summary'])<220,c['id']);self.assertTrue(c['summary'].endswith('.'),c['id'])
        self.assertNotIn('—',PAGE[PAGE.index('<main'):PAGE.index('</main>')])
    def test_every_row_links_somewhere(self):
        lib=json.loads((ROOT/'data/library.json').read_text());hosted=councils_page.hosted_works(lib)
        for c in D['councils']:
            self.assertTrue((c.get('work') in hosted) or c.get('links'),c['id'])
            for L in c.get('links',[]):self.assertTrue(L['url'].startswith('https://'),L)
        # the Church Documents links already on the site are kept
        for u in ('https://www.papalencyclicals.net/councils','https://www.papalencyclicals.net/councils/trent.htm','https://www.papalencyclicals.net/councils/ecum20.htm','https://www.vatican.va/archive/hist_councils/ii_vatican_council/index.htm'):
            self.assertIn(u,PAGE)
    def test_read_here_only_when_hosted(self):
        lib=json.loads((ROOT/'data/library.json').read_text())
        c=dict(D['councils'][0],work='orthodoxy',links=[])
        self.assertIn('Read on this site',councils_page.row(c,lib,{'orthodoxy'},{}))
        self.assertNotIn('Read on this site',councils_page.row(dict(c,links=[{'label':'x','url':'https://example.org/'}]),lib,set(),{}))
        n_hosted=sum(1 for c in D['councils'] if c.get('work') in councils_page.hosted_works(lib))
        self.assertEqual(PAGE.count('Read on this site'),n_hosted)
    def test_page_shape(self):
        self.assertEqual(PAGE.count('googletagmanager.com/gtag/js'),1)
        self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/councils/">',PAGE)
        self.assertIn('window.BC_BOOT="councils"',PAGE)
        self.assertEqual(PAGE.count('class="council"'),21)
        body=PAGE[PAGE.index('<main'):PAGE.index('</main>')]
        self.assertNotRegex(body,r'href="#(?!/)')  # app.js reads location.hash as the route: no in-page anchors
        self.assertNotIn('btn"',body)  # no filled primary here; rows use text links
        self.assertIn('https://bibliothecacatholica.com/councils/',(ROOT/'sitemap.xml').read_text())
    def test_linked_from_church_documents_and_footer_not_nav(self):
        mag=(ROOT/'magisterium/index.html').read_text();main=mag[mag.index('<main'):]
        self.assertIn(councils_page.MAGISTERIUM_LINK,main)
        self.assertLess(main.index('href="/councils/"'),main.index('<ul>'))  # before the resource list
        app=(ROOT/'app.js').read_text()
        self.assertIn("if(k==='magisterium')h+='"+councils_page.MAGISTERIUM_LINK+"'",app)
        self.assertRegex(app,r"return path==='councils'\|\|")
        self.assertRegex(app,r"STATIC_SECTIONS=\[[^\]]*'councils'")
        tpl=(ROOT/'index.html').read_text()
        nav=tpl[tpl.index('<nav'):tpl.index('</nav>')]
        self.assertNotIn('/councils/',nav)
        self.assertEqual(len(re.findall(r'data-nav="',nav)),8)  # seven sections plus the phone-only Support link
        foot=tpl[tpl.index('<footer'):tpl.index('</footer>')];self.assertIn('<a href="/councils/">Ecumenical Councils</a>',foot)
    def test_no_new_analytics(self):
        for f in ('tools/councils_page.py','data/councils.json'):
            s=(ROOT/f).read_text();self.assertNotIn('gtag(',s);self.assertNotIn('track(',s);self.assertNotIn('<script',s)
if __name__=='__main__':unittest.main()
