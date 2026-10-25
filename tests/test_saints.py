"""Saints & Hagiography (v15) schema and rights checks. See docs/SAINTS.md."""
import json,re,subprocess,sys,unittest
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
def js_obj(path,var):
    s=(ROOT/path).read_text();p='window.%s='%var;assert s.startswith(p);return json.loads(s[len(p):].rstrip().rstrip(';'))
D=json.loads((ROOT/'data/saints.json').read_text());S=D['saints']
REQ=['id','qid','name','tier','kind','aliases','status','feasts','wikidata','reading_room_works','lives_about','catholicsaints']
HARD={'barbara','catherine-of-alexandria','christopher','dymphna','expeditus','george','margaret-of-antioch','michael-the-archangel','philomena','ursula','valentine','veronica'}
sys.path.insert(0,str(ROOT/'tools'))
import build_saints
class SaintSchemaTests(unittest.TestCase):
    def test_counts_and_required_fields(self):
        self.assertEqual(len(S),185)
        self.assertEqual(sorted(__import__('collections').Counter(s['tier'] for s in S).items()),[(1,139),(2,34),(3,12)])
        self.assertEqual(len({s['id'] for s in S}),185)
        for s in S:
            for f in REQ:self.assertIn(f,s,s['id']+' '+f)
            self.assertRegex(s['id'],r'^[a-z0-9-]+$');self.assertRegex(s['qid'],r'^Q\d+$')
            self.assertTrue(s['status']['source_url'].startswith('https://'),s['id'])
            for v in s['feasts']['vatican_news']:
                self.assertRegex(v['date'],r'^\d\d-\d\d$');self.assertEqual(urlparse(v['source_url']).hostname,'www.vaticannews.va')
            self.assertIsNone(s['feasts']['general_roman_calendar'],'GRC dates are deferred until checked against the Missal')
            for d in s['feasts']['other_wikidata']['dates']:self.assertRegex(d,r'^\d\d-\d\d$')
            if s.get('born') and s.get('died'):self.assertLess(s['born']['year'],s['died']['year'],s['id'])
    def test_tier1_saints_are_hub_authors_and_not_flagged(self):
        hub={a['id'] for a in json.loads((ROOT/'data/catholic-hub.json').read_text())['authors']}
        flagged=set(json.loads((ROOT/'data/editorial-flags.json').read_text()).get('hubAuthors',[]))
        for s in S:
            if s['tier']==1:self.assertEqual(s['author_id'],s['id']);self.assertIn(s['author_id'],hub)
            if s.get('author_id'):self.assertNotIn(s['author_id'],flagged)
    def test_catholicsaints_link_only_tier1(self):
        linked=[s for s in S if s['catholicsaints']]
        self.assertEqual(len(linked),139)
        for s in linked:
            self.assertEqual(s['tier'],1,s['id']+': no CatholicSaints.Info links for tiers 2 and 3')
            c=s['catholicsaints'];self.assertEqual(urlparse(c['url']).hostname,'catholicsaints.info')
            self.assertTrue(c['link_only']);self.assertIn(c['confidence'],('high','medium'))
            self.assertLessEqual(set(c),{'url','wayback_url','confidence','source','link_only'})
        for s in S:
            if s['tier']>1:self.assertIsNone(s['catholicsaints'],s['id'])
        # nothing copied: no other field may cite or quote CatholicSaints.Info
        for s in S:
            rest={k:v for k,v in s.items() if k!='catholicsaints'}
            self.assertNotIn('catholicsaints.info',json.dumps(rest).lower(),s['id'])
    def test_hard_cases_carry_tradition_flags(self):
        flagged={s['id']:s['historicity'] for s in S if s.get('historicity')}
        self.assertEqual(set(flagged),HARD)
        for i,h in flagged.items():
            self.assertIn(h['flag'],('tradition','tradition-with-historical-core','angel'),i)
            self.assertTrue(h['note'] and h['source_url'].startswith('https://'),i)
        self.assertTrue(all(s['tier']==3 for s in S if s['id'] in HARD))
    def test_works_and_books_resolve(self):
        works={w['id'] for w in json.loads((ROOT/'data/library.json').read_text())['works']}
        ids={s['id'] for s in S}
        for s in S:
            for w in s['reading_room_works']:self.assertIn(w,works,s['id'])
        for b in D['shelf']:
            self.assertTrue(b['url'].startswith('https://'));self.assertNotIn('amazon.',b['url'])
            self.assertTrue(b['public_domain'] and b['evidence'] and b['imprint'],b['id'])
            self.assertLessEqual(set(b['about'])|set(b['by']),ids)
            m=re.search(r'\d{4}',b['imprint_date']);self.assertTrue(m and int(m.group())<=1931,b['id'])
class SaintAliasTests(unittest.TestCase):
    def test_alias_table_matches_generated_js(self):
        al=json.loads((ROOT/'data/saints-aliases.json').read_text());js=js_obj('data/saints.js','SAINTS_DATA')
        self.assertEqual(al['aliases'],js['aliases']);self.assertEqual(al['collisions'],js['collisions'])
        self.assertEqual(len(js['saints']),185)
    def test_aliases_unique_and_resolve(self):
        al=json.loads((ROOT/'data/saints-aliases.json').read_text());ids={s['id'] for s in S}
        self.assertFalse(set(al['aliases'])&set(al['collisions']),'a key is either unique or a collision')
        for k,v in al['aliases'].items():self.assertIn(v,ids);self.assertEqual(build_saints.key(k),k)
        for k,v in al['collisions'].items():self.assertGreaterEqual(len(v),1);self.assertLessEqual(set(v),ids)
        for q,i in (('Little Flower','therese-of-lisieux'),('Thérèse of Lisieux','therese-of-lisieux'),('Therese','therese-of-lisieux'),
                    ('St. Thomas Aquinas','thomas-aquinas'),('Angelic Doctor','thomas-aquinas'),('John Damascene','john-of-damascus'),('Laurence','lawrence-of-rome')):
            self.assertEqual(al['aliases'].get(build_saints.key(q)),i,q)
        self.assertIn('john',al['collisions'])
    def test_build_is_current(self):
        before=(ROOT/'data/saints.js').read_bytes()
        subprocess.run([sys.executable,str(ROOT/'tools/build_saints.py')],check=True,capture_output=True)
        self.assertEqual(before,(ROOT/'data/saints.js').read_bytes(),'run python3 tools/build_saints.py and commit')
class SaintStaticTests(unittest.TestCase):
    def test_static_pages(self):
        for s in S:
            f=ROOT/('author/'+s['author_id'] if s['tier']==1 else 'saints/'+s['id'])/'index.html'
            self.assertTrue(f.exists(),s['id']);h=f.read_text()
            self.assertEqual(h.count('googletagmanager.com/gtag/js'),1)
            if s['tier']>1:
                self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/saints/%s/">'%s['id'],h)
                self.assertIn('<title>%s — Saints — Bibliotheca Catholica</title>'%s['name'].replace('&','&amp;'),h)
                self.assertNotIn('catholicsaints.info',h)
                if s.get('historicity'):self.assertIn('Tradition and legend' if s['historicity']['flag']=='tradition' else 'legend' if s['historicity']['flag']!='angel' else 'Archangel',h)
        sm=(ROOT/'sitemap.xml').read_text()
        for u in ('saints/','saints/books/','saints/about/','saints/christopher/'):self.assertIn('https://bibliothecacatholica.com/'+u,sm)
if __name__=='__main__':unittest.main()
