"""Full-year saints calendar (facts only): importer, validation, merged day lists, and the built pages.
See docs/SAINTS-CALENDAR.md. Uses tests/fixtures/saints-sample.jsonl (a FIXTURE, not site data).
Owner's decisions (2026-11-09): no per-entry CatholicSaints.Info links (one Resources entry credits it), one merged
list per day with neutral notes where sources disagree, and the raw import kept out of the deployed site."""
import json,re,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import import_saints as IS,saints_calendar as SC
FIX=ROOT/'tests/fixtures/saints-sample.jsonl'
GUIDE=json.loads((ROOT/'data/saints.json').read_text())['saints']
ALIAS=json.loads((ROOT/'data/saints-aliases.json').read_text())['aliases']
GIDS={s['id'] for s in GUIDE}
def run_fixture():return IS.import_records(IS.read_records(FIX))
def fixture_doc():
    S,D,st,P=run_fixture();return SC.make_days({'saints':S,'days':D},GUIDE,ALIAS)
href=lambda s:'/author/'+s['id']+'/' if s['tier']==1 else '/saints/'+s['id']+'/'
class Importer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.S,cls.D,cls.st,cls.P=run_fixture()
    def test_counts_and_dedupe_on_slug(self):
        self.assertEqual(self.st['rows'],10);self.assertEqual(self.st['slugs'],7)
        self.assertEqual(self.S['saint-thomas-aquinas']['dates'],['01-28','03-07']);self.assertEqual(self.P['duplicate_rows'],1)
        self.assertEqual(self.S['saint-thomas-aquinas']['patronage'],['students','universities'],'merged from the second row')
    def test_whitelist_drops_prose_and_unknown_keys(self):
        self.assertEqual(self.P['dropped_keys'].get('profile'),1)
        self.assertNotIn('TEST PROSE',json.dumps(self.S)+json.dumps(self.D))
    def test_rejections_and_fixes(self):
        self.assertEqual([x['date'] for x in self.P['bad_date']],['13-40']);self.assertNotIn('fixture-bad-date',self.S)
        self.assertEqual(len(self.P['amazon']),1);self.assertNotIn('amazon',json.dumps(self.S).lower())
        self.assertEqual(self.S['fixture-test-blessed']['born_place'],'Testville, Fixture County')
        self.assertEqual(self.D['01-21']['names'],[{'name':'Fixture Unlinked Name (TEST DATA)','type':'unknown'}])
    def test_long_text_is_treated_as_prose(self):
        S,D,st,P=IS.import_records([(1,{'date':'January 5','name':'X Test','slug':'x-test','died_place':'word '*50})])
        self.assertNotIn('died_place',S['x-test']);self.assertEqual(len(P['prose_dropped']),1);self.assertEqual(S['x-test']['dates'],['01-05'])
    def test_cli_writes_private_raw_and_committed_days(self):
        with tempfile.TemporaryDirectory() as t:
            raw,out,rep=Path(t)/'raw.json',Path(t)/'days.json',Path(t)/'r.json'
            self.assertEqual(IS.main(['--input',str(FIX),'--raw',str(raw),'--output',str(out),'--report',str(rep)]),0)
            self.assertEqual(IS.main(['--input',str(FIX),'--raw',str(raw),'--output',str(out),'--strict']),1,'a rejected record fails --strict')
            self.assertIn('catholicsaints.info',raw.read_text(),'the raw copy keeps source URLs for matching')
            days=out.read_text();self.assertNotRegex(days,r'(?i)https?:|catholicsaints|"slug"')
            self.assertTrue(SC.validate(json.loads(days),GIDS))
            self.assertEqual(json.loads(rep.read_text())['matched_to_guide'],{'url':3,'name':1})
    def test_raw_copy_is_git_ignored(self):
        self.assertIn('.local/',(ROOT/'.gitignore').read_text().split())
        self.assertEqual(subprocess.run(['git','check-ignore','-q','.local/saints-calendar.json'],cwd=ROOT).returncode,0)
class RealShape(unittest.TestCase):
    """Clean-up rules for the full-year export's shape (records with entry_type)."""
    def run_rows(self,rows):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'r.jsonl';f.write_text('\n'.join(json.dumps(r) for r in rows));return IS.import_records(IS.read_records(f))
    def row(self,**k):
        r={'date':'25-december','entry_type':'unknown','name':'','slug':'','canonical_url':'','born':'','died':'','beatified':'','canonized':'','patronage':[],'aliases':[]};r.update(k);return r
    def test_day_rows_and_junk(self):
        S,D,st,P=self.run_rows([self.row(name='Calendar of Saints - 25 December',slug='christmas'),
            self.row(name='Also celebrated but no entry yet',slug='also-celebrated-but-no-entry-yet'),
            self.row(date='21-april',name='Calendar of Saints - 21 April',slug='easter'),
            self.row(date='15-august',name='Assumption of the Blessed Virgin Mary',slug='assumption-of-the-blessed-virgin-mary')])
        names={s['name']:s['type'] for s in S.values()}
        self.assertEqual(names.get('Nativity of the Lord (Christmas)'),'feast')
        self.assertEqual(names.get('Assumption of the Blessed Virgin Mary'),'feast')
        self.assertEqual(len(names),2,names)
    def test_life_facts(self):
        self.assertEqual(IS.life_fact('7 March 1274 at Fossanuova monastery near Terracina, Italy of natural causes'),'7 March 1274 at Fossanuova monastery near Terracina, Italy')
        self.assertIsNone(IS.life_fact('relics taken to Mauzac Abbey in 761'))
        self.assertNotIn('relic',IS.life_fact('relics taken to Mauzac Abbey in 761 \u2022 5th century') or '')
class Names(unittest.TestCase):
    def test_site_style(self):
        for a,b in (('Saint Thomas Aquinas','St. Thomas Aquinas'),('Pope Saint John Paul II','Pope St. John Paul II'),('Saints Perpetua and Felicity','Sts. Perpetua and Felicity'),('St Agnes','St. Agnes'),('Bl. Fixture','Blessed Fixture'),('Holy Innocents','Holy Innocents')):
            self.assertEqual(SC.site_name(a),b)
        self.assertEqual(SC.site_name('Thomas Aquinas','saint'),'St. Thomas Aquinas');self.assertEqual(SC.site_name('Michael the Archangel','archangel'),'St. Michael the Archangel')
        self.assertEqual(SC.key('St. Thomas Aquinas'),SC.key('Saint Thomas Aquinas'))
class Validate(unittest.TestCase):
    def test_rejects(self):
        for mut in (lambda d:d['days']['08-27'][0].__setitem__('u','https://catholicsaints.info/x/'),
                    lambda d:d['days']['08-27'][0].__setitem__('f','See https://catholicsaints.info/x/'),
                    lambda d:d['days']['08-27'][0].__setitem__('f','From CatholicSaints.Info.'),
                    lambda d:d['days']['08-27'][0].__setitem__('n','St. A \u2014 B'),
                    lambda d:d['days']['08-27'][0].__setitem__('g','no-such-saint'),
                    lambda d:d['days']['08-27'][0].__setitem__('o',['08-27'])):
            d=fixture_doc();mut(d)
            with self.assertRaises(SC.CalendarError):SC.validate(d,GIDS)
        self.assertTrue(SC.validate(fixture_doc(),GIDS))
class Merged(unittest.TestCase):
    def day(self,md):
        L=SC.merged_day(md,fixture_doc(),GUIDE,href);return {x['name']:x for x in L},L
    def test_one_entry_per_person(self):
        M,L=self.day('01-28');self.assertEqual(len(L),1,'guide and calendar Aquinas are one entry')
        x=L[0];self.assertEqual(x['name'],'St. Thomas Aquinas');self.assertEqual(x['href'],'/author/thomas-aquinas/')
        self.assertIn('Canonized: 18 July 1323',x['facts']);self.assertEqual(x['notes'],['Also kept on 7 March in some calendars.'])
        M,L=self.day('08-27');self.assertEqual([x['name'] for x in L],['St. Monica of Hippo'],'one-word calendar name merges with the guide saint of the same day')
        M,L=self.day('01-21');self.assertEqual(sorted(M),['Fixture Unlinked Name (TEST DATA)','St. Agnes of Rome'])
    def test_disagreement_notes(self):
        M,L=self.day('03-07');x=M['St. Thomas Aquinas']
        self.assertEqual(x['href'],'/author/thomas-aquinas/');self.assertEqual(x['notes'],['Date differs between sources; also kept on 28 January.'])
        # a guide saint whose Vatican News day the calendar does not share
        g=[dict(s) for s in GUIDE];aq=next(s for s in g if s['id']=='thomas-aquinas');aq['feasts']=dict(aq['feasts'],vatican_news=[{'date':'01-29','title_on_source':'t','source_url':'https://www.vaticannews.va/x'}])
        L=SC.merged_day('01-29',fixture_doc(),g,href);x=[y for y in L if y.get('g')=='thomas-aquinas'][0]
        self.assertEqual(x['notes'][0],'Date differs between sources; also kept on 28 January and 7 March.')
    def test_types_and_pope(self):
        M,L=self.day('10-22');self.assertEqual(len(L),1);self.assertEqual(L[0]['type'],'pope');self.assertEqual(L[0]['href'],'/author/john-paul-ii/')
    def test_day_page_has_no_source_links(self):
        a=lambda h,l,ext=False:'<a href="%s">%s</a>'%(h,l)
        t,d,body,n=SC.day_page('01-28',SC.merged_day('01-28',fixture_doc(),GUIDE,href),a)
        self.assertEqual(t,'Saints of 28 January · Saints · Bibliotheca Catholica');self.assertEqual(n,1)
        self.assertNotRegex(body,r'(?i)catholicsaints|https?://');self.assertIn('/references/',body);self.assertNotIn('\u2014',body)
        t,d,body,n=SC.day_page('07-04',[],a);self.assertEqual(n,0);self.assertIn('No saints are listed',body)
class Built(unittest.TestCase):
    def test_resources_credit_once(self):
        R=[r for r in json.loads((ROOT/'data/catholic-hub.json').read_text())['resources'] if 'catholicsaints' in r['url']]
        self.assertEqual(len(R),1);self.assertEqual((R[0]['section'],R[0]['category'],R[0]['url']),('references','Saints & hagiography','https://catholicsaints.info/'))
    def test_no_raw_data_in_the_deployed_tree(self):
        tracked=subprocess.run(['git','ls-files'],cwd=ROOT,capture_output=True,text=True).stdout.split()
        self.assertNotIn('data/saints-calendar.json',tracked);self.assertFalse(any(p.startswith('.local/') for p in tracked))
    def test_static_pages_match_the_data(self):
        cal=SC.load(ROOT)
        pages=sorted(p.parent.name for p in (ROOT/'saints/calendar').glob('*/index.html')) if (ROOT/'saints/calendar').exists() else []
        if cal is None:self.assertEqual(pages,[],'no data file: no day pages');return
        self.assertEqual(pages,SC.ALL_DAYS);sm=(ROOT/'sitemap.xml').read_text()
        for md in SC.ALL_DAYS:
            h=(ROOT/'saints/calendar'/md/'index.html').read_text()
            body=re.search(r'<div class="static-prerender">(.*)</div></main>',h,re.S).group(1)
            self.assertNotRegex(body,r'(?i)catholicsaints|href="https?://');self.assertNotIn('\u2014',body)
            self.assertEqual(h.count("gtag('config'"),1);self.assertIn('https://bibliothecacatholica.com/saints/calendar/'+md+'/',sm)
if __name__=='__main__':unittest.main()
