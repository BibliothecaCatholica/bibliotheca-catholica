"""Full-year saints calendar (facts only): importer, validation, day pages. See docs/SAINTS-CALENDAR.md.
Uses tests/fixtures/saints-sample.jsonl (a FIXTURE, not site data)."""
import json,re,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import import_saints as IS,saints_calendar as SC
FIX=ROOT/'tests/fixtures/saints-sample.jsonl'
def run_fixture():
    return IS.import_records(IS.read_records(FIX))
class Importer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.S,cls.D,cls.st,cls.P=run_fixture()
    def test_counts_and_dedupe_on_slug(self):
        self.assertEqual(self.st['rows'],10);self.assertEqual(self.st['slugs'],7)
        self.assertEqual(self.S['saint-thomas-aquinas']['dates'],['01-28','03-07'])
        self.assertEqual(self.P['duplicate_rows'],1)
        self.assertEqual(self.S['saint-thomas-aquinas']['patronage'],['students','universities'],'merged from the second row')
        self.assertEqual(self.D['03-07']['slugs'],['saint-thomas-aquinas'])
    def test_whitelist_drops_prose_and_unknown_keys(self):
        self.assertEqual(self.P['dropped_keys'].get('profile'),1)
        blob=json.dumps(self.S)+json.dumps(self.D)
        self.assertNotIn('TEST PROSE',blob);self.assertNotIn('fixture"',blob)
        for s in self.S.values():self.assertLessEqual(set(s),SC.FACT_KEYS)
    def test_rejections_and_fixes(self):
        self.assertEqual([x['date'] for x in self.P['bad_date']],['13-40'])
        self.assertNotIn('fixture-bad-date',self.S)
        self.assertEqual(len(self.P['amazon']),1);self.assertNotIn('amazon',json.dumps(self.S).lower())
        self.assertEqual(self.S['fixture-test-blessed']['born_place'],'Testville, Fixture County')
        self.assertEqual(self.P['emdash_fixed']['born_place'],1)
        self.assertEqual(self.D['01-21']['names'],[{'name':'Fixture Unlinked Name (TEST DATA)','type':'unknown'}])
        self.assertEqual(self.S['holy-innocents']['type'],'martyr-group');self.assertEqual(self.S['pope-saint-john-paul-ii']['type'],'pope')
    def test_long_text_is_treated_as_prose(self):
        S,D,st,P=IS.import_records([(1,{'date':'January 5','name':'X Test','slug':'x-test','died_place':'word '*50,'url':'https://www.catholicsaints.info/x-test/'})])
        self.assertNotIn('died_place',S['x-test']);self.assertEqual(len(P['prose_dropped']),1)
        self.assertEqual(S['x-test']['dates'],['01-05']);self.assertEqual(S['x-test']['url'],'https://catholicsaints.info/x-test/')
    def test_outside_urls_dropped_and_slug_from_url(self):
        S,D,st,P=IS.import_records([(1,{'date':'02-01','name':'A Test','url':'https://catholicsaints.mobi/a-test/'}),(2,{'date':'02-01','name':'B Test','slug':'b-test','url':'https://example.com/b'})])
        self.assertIn('a-test',S);self.assertEqual(P['slug_from_url'],1)
        self.assertNotIn('url',S['b-test']);self.assertEqual(P['bad_url'],['https://example.com/b'])
    def test_output_validates_and_cli_writes_report(self):
        with tempfile.TemporaryDirectory() as t:
            out,rep=Path(t)/'c.json',Path(t)/'r.json'
            self.assertEqual(IS.main(['--input',str(FIX),'--output',str(out),'--report',str(rep)]),0)
            self.assertEqual(IS.main(['--input',str(FIX),'--output',str(out),'--strict']),1,'a rejected record fails --strict')
            cal=json.loads(out.read_text());self.assertTrue(SC.validate(cal))
            r=json.loads(rep.read_text());self.assertEqual(r['bad_date_count'],1);self.assertEqual(r['missing_slug_count'],1)
class Validate(unittest.TestCase):
    def cal(self):
        S,D,st,P=run_fixture();return json.loads(json.dumps({'saints':S,'days':D}))
    def test_rejects(self):
        for mut in (lambda c:c['saints']['saint-monica'].__setitem__('profile','x'),
                    lambda c:c['saints']['saint-monica'].__setitem__('died_place','Ostia \u2014 Rome'),
                    lambda c:c['saints']['saint-monica'].__setitem__('url','https://www.amazon.com/x'),
                    lambda c:c['saints']['saint-monica'].__setitem__('pd_life',{'text':'x','source_title':'Butler','source_url':'https://archive.org/x','source_year':1956}),
                    lambda c:c['days']['08-27']['slugs'].append('saint-agnes-of-rome')):
            c=self.cal();mut(c)
            with self.assertRaises(SC.CalendarError):SC.validate(c)
        c=self.cal();c['saints']['saint-monica']['pd_life']={'text':'A life.','source_title':'The Book of Saints','source_url':'https://archive.org/details/x','source_year':1921}
        self.assertTrue(SC.validate(c))
class Pages(unittest.TestCase):
    def test_day_page_from_fixture(self):
        S,D,st,P=run_fixture();cal={'saints':S,'days':D}
        a=lambda h,l,ext=False:'<a href="%s"%s>%s</a>'%(h,' target="_blank" rel="noopener"' if ext else '',l)
        guide=json.loads((ROOT/'data/saints.json').read_text())['saints'];al=json.loads((ROOT/'data/saints-aliases.json').read_text())['aliases']
        M,how=SC.match_guide(cal,guide,al)
        self.assertEqual(M.get('saint-thomas-aquinas'),'thomas-aquinas');self.assertEqual(M.get('pope-saint-john-paul-ii'),'john-paul-ii')
        self.assertEqual(M.get('saint-agnes-of-rome'),'agnes-of-rome');self.assertNotIn('saint-monica',M,'one-word names never match')
        gh={x['id']:('/x/'+x['id']+'/','In our saints guide') for x in guide}
        t,d,body,n=SC.day_page('01-28',cal,[],M,gh,a)
        self.assertEqual(t,'Saints of 28 January — Saints — Bibliotheca Catholica');self.assertEqual(n,1)
        self.assertIn('https://catholicsaints.info/saint-thomas-aquinas/',body);self.assertIn('/saints/calendar/03-07/',body)
        self.assertNotIn('\u2014',body);self.assertEqual(body.count('<h1>'),1)
        t,d,body,n=SC.day_page('07-04',cal,[],M,gh,a);self.assertEqual(n,0);self.assertIn('No names are listed',body)
class Built(unittest.TestCase):
    def test_static_pages_match_the_data(self):
        cal=SC.load(ROOT)
        pages=sorted(p.parent.name for p in (ROOT/'saints/calendar').glob('*/index.html')) if (ROOT/'saints/calendar').exists() else []
        if cal is None:self.assertEqual(pages,[],'no data file: no day pages');return
        self.assertEqual(pages,SC.ALL_DAYS)
        sm=(ROOT/'sitemap.xml').read_text()
        for md in ('01-01','02-29','12-31'):
            h=(ROOT/'saints/calendar'/md/'index.html').read_text()
            self.assertEqual(h.count("gtag('config'"),1);self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/saints/calendar/'+md+'/">',h)
            self.assertIn('https://bibliothecacatholica.com/saints/calendar/'+md+'/',sm)
            body=re.search(r'<div class="static-prerender">(.*)</div></main>',h,re.S).group(1)
            self.assertNotIn('\u2014',body);self.assertNotIn('amazon.',body.lower())
            for u in re.findall(r'href="(https?://[^"]+)"',body):self.assertRegex(u,r'^https://(catholicsaints\.(info|mobi)|www\.vaticannews\.va|archive\.org)/')
if __name__=='__main__':unittest.main()
