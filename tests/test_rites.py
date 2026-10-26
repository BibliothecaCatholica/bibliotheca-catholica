"""v19 Rites & Liturgy (phase 2): data validity and sources, low-confidence handling, the map (no pins,
every shaded code drawn), page SEO basics, rights badges, contrast, and wording rules. See docs/RITES.md."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
import build_rites as B, rites_pages as RP
def R(p):return (ROOT/p).read_text(encoding='utf-8')
D=json.loads(R('data/rites.json'))
J=json.loads(R('data/rites.js').strip()[len('window.RITES_DATA='):-1])
RAW=json.loads(R('data/rites-src/rites-map.json'))
RAWREC={r['id']:r for r in RAW['churches']+RAW['latin_rites_and_uses']}
ROUTES=['rites']+['rites/'+k for k in J['pages'] if k]
def page(route):return R(route+'/index.html')
def main_html(s):return s.split('<main id="main" tabindex="-1">',1)[1].split('</main>',1)[0]
def text(h):return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',re.sub(r'<(script|style|svg)\b.*?</\1>','',h,flags=re.S)))
FIELDS=['cceo','ccc','status','head','centre','see','geography','books','note']
class RitesData(unittest.TestCase):
    def test_counts_and_ids(self):
        recs=D['records'];self.assertEqual(len(recs),31)
        self.assertEqual(sum(r['kind']=='church' for r in recs),24);self.assertEqual(sum(r['kind']=='latin-rite' for r in recs),7)
        self.assertEqual(len({r['id'] for r in recs}),31)
        for r in recs:self.assertRegex(r['id'],r'^[a-z0-9-]+$');self.assertIn(r['family'],D['families'])
    def test_every_shown_field_and_milestone_has_a_source(self):
        for r in D['records']:
            self.assertTrue(r['name_src'] and r['sources'],r['id'])
            for k in FIELDS:
                f=r.get(k)
                if f:self.assertTrue(f['s'] and all(u.startswith('https://') for u in f['s']),(r['id'],k))
            for m in r['milestones']:self.assertTrue(m['s'] and m['s'][0].startswith('http'),(r['id'],m))
            for s in r.get('status_magisterial') or []:self.assertTrue(s['s'],r['id'])
            for x in r['resources']:self.assertIn(x['rights'],RP.RLABEL);self.assertTrue(x['url'].startswith('https://') and x['evidence'],x)
        for lid,L in D['layers'].items():
            if L['present'] and not lid.startswith('fam-'):self.assertTrue(L['psrc'].startswith('https://') and L['asof'],lid)
            if L['heartland'] and not lid.startswith('fam-'):self.assertTrue(L['hsrc'],lid)
    def test_low_confidence_is_never_plain_fact(self):
        out={r['id']:r for r in D['records']}
        keymap={'rite_tradition':'cceo','canonical_status':'status','head':'head','geography':'geography','liturgical_books_current':'books'}
        for rid,raw in RAWREC.items():
            o=out[rid]
            for rk,ok in keymap.items():
                f=raw.get(rk)
                if isinstance(f,dict) and f.get('confidence')=='low':
                    self.assertTrue(o.get(ok) is None or o[ok].get('unv'),(rid,rk))
            for rk,ok in(('mother_city','centre'),('present_see','see')):
                f=(raw.get('origin') or {}).get(rk)
                if isinstance(f,dict) and f.get('confidence')=='low':self.assertIsNone(o.get(ok),(rid,rk))
            lowms={m['when'] for m in raw.get('milestones',[]) if m.get('confidence')=='low'}
            self.assertEqual(len(o['milestones']),len(raw.get('milestones',[]))-len(lowms),rid)
        shade=json.loads(R('data/rites-src/rites-map-shading.json'))
        for L in shade['layers']:
            lid=L.get('church_id') or L.get('rite_id')
            if L['present_jurisdictions_countries'].get('confidence')=='low':self.assertEqual(D['layers'][lid]['present'],[],lid)
            if (L.get('heartland_historical') or {}).get('confidence')=='low':self.assertEqual(D['layers'][lid]['heartland'],[],lid)
        # every Unverified field is on the reviewed list and is marked on its page
        for r in D['records']:
            for k in FIELDS:
                if (r.get(k) or {}).get('unv'):
                    self.assertTrue(any(u.startswith(r['id']+':') for u in D['unverified']),(r['id'],k))
                    self.assertIn('class="rites-unv"',J['pages'][r['id']]['html'],r['id'])
    def test_no_population_numbers(self):
        sh=json.loads(R('data/rites-src/rites-map-shading.json'))
        self.assertNotIn('population_estimates',sh);self.assertNotIn('population_policy',sh);self.assertNotIn('population',json.dumps(sh['layers']))
        blob=json.dumps(J,ensure_ascii=False)+R('data/rites.json')
        self.assertNotIn('population_estimates',blob)
        for k,pg in J['pages'].items():
            t=text(pg['html']).lower()
            self.assertNotRegex(t,r'\b\d{1,3}(,\d{3})+\b',k)  # no head counts such as 4,500,000
            self.assertNotRegex(t,r'\d\s*(million|thousand)|\d[\d,.]*\s*(faithful|members|adherents|catholics)\b',k)
    def test_cross_links_resolve(self):
        hub={a['id'] for a in json.loads(R('data/catholic-hub.json'))['authors']};works={w['id'] for w in json.loads(R('data/library.json'))['works']}
        saints={s['id'] for s in json.loads(R('data/saints.json'))['saints']}
        for r in D['records']:
            for x in r['related']:self.assertIn(x['id'],{'author':hub,'work':works,'saint':saints}[x['kind']],x)
class RitesMap(unittest.TestCase):
    def test_every_shaded_code_is_drawn(self):
        drawn=set(re.findall(r'<path data-c="([A-Z]{2})"',J['svg']))
        self.assertGreater(len(drawn),170)
        for lid,L in J['layers'].items():
            for c in L['present']+L['heartland']:self.assertIn(c,drawn,(lid,c));self.assertIn(c,D['names'])
    def test_no_pins_markers_tiles_or_cdn(self):
        blob=J['svg']+J['insets']+R('scripts/rites.js')+R('styles/rites.css')
        for bad in('<circle','<marker','<image','<use','leaflet','tile.','unpkg','cdnjs','jsdelivr','googleapis','mapbox','openstreetmap'):self.assertNotIn(bad,blob.lower(),bad)
        for route in ROUTES:
            m=main_html(page(route))
            self.assertNotIn('<circle',m);self.assertNotIn('<script src=',m)
    def test_one_layer_shaded_on_static_pages_matches_data(self):
        m=main_html(page('rites'));on=re.findall(r'<path data-c="([A-Z]{2})" class="on"',m)
        self.assertEqual(set(on),set(J['layers']['fam-ant']['present']))
        self.assertIn('<option value="fam-ant" selected>',m);self.assertIn('value="present" checked',m)
        for k,pg in J['pages'].items():
            if k and 'rmap-slot' in pg['html']:
                on=set(re.findall(r'<path data-c="([A-Z]{2})" class="on"',main_html(page('rites/'+k))));self.assertEqual(on,set(J['layers'][k]['present']),k)
    def test_colour_is_paired_with_hatching_and_text(self):
        css=R('styles/rites.css')
        for f in B.FAM_ORDER:
            self.assertIn('<pattern id="rmp-'+f+'"',J['svg']);self.assertIn('<pattern id="rmh-'+f+'"',J['svg'])
            self.assertIn('path.on{fill:url(#rmp-'+f+')}',css);self.assertIn('path.on{fill:url(#rmh-'+f+')}',css)
        for k,v in J['info'].items():
            lid,view=k.split('|')
            if J['layers'][lid][view]:self.assertIn('class="rmap-countries"',v,k);self.assertEqual(v.count('<li>'),len(J['layers'][lid][view]),k)
    def test_contrast(self):
        P=D['palette']
        for mode in('light','dark'):
            for f in B.FAM_ORDER:
                for bg in('land','sea'):self.assertGreaterEqual(B.ratio(P[mode]['fill-'+f],P[mode][bg]),3.0,(mode,f,bg))
        css=R('styles/rites.css');self.assertIn(B.palette_css(P),css)
        site=R('styles.css');light=dict(re.findall(r'--(\w+):(#[0-9a-f]{6})',site.split('[data-theme=dark]')[0]));dark=dict(light);dark.update(re.findall(r'--(\w+):(#[0-9a-f]{6})',site.split('[data-theme=dark]{')[1].split('}')[0]))
        for T in(light,dark):
            for fg in('ink','ink2','muted','rubric'):
                for bg in('bg','bg2','card'):self.assertGreaterEqual(B.ratio(T[fg],T[bg]),4.5,(fg,bg))
        for mode,T in(('light',light),('dark',dark)):self.assertGreaterEqual(B.ratio(T['ink'],P[mode]['land']),4.5)  # map labels on their halo
    def test_natural_earth_note(self):
        self.assertEqual(D['geo_meta']['join_key'],'ISO_A2_EH');self.assertIn('public domain',D['geo_meta']['rights'].replace('_',' '))
        for route in('rites/sources','licensing'):self.assertIn('Natural Earth',page(route));self.assertIn('public domain',page(route))
        self.assertIn('Natural Earth',R('LICENSING.md'))
class RitesPages(unittest.TestCase):
    def test_static_pages_titles_descriptions_h1_canonical_sitemap(self):
        self.assertEqual(len(ROUTES),33);titles=set();descs=set();sm=R('sitemap.xml')
        for route in ROUTES:
            s=page(route);t=re.search(r'<title>(.*?)</title>',s).group(1);d=re.search(r'<meta name="description" content="([^"]*)">',s).group(1)
            self.assertTrue(150<=len(d.replace('&amp;','&').replace('&#x27;',"'"))<=160,(route,len(d)));titles.add(t);descs.add(d)
            self.assertEqual(len(re.findall(r'<h1[\s>]',main_html(s))),1,route)
            self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/'+route+'/">',s)
            self.assertIn('<loc>https://bibliothecacatholica.com/'+route+'/</loc>',sm)
            self.assertIn('"@type":"BreadcrumbList"',s)
        self.assertEqual(len(titles),33);self.assertEqual(len(descs),33)
    def test_app_description_is_the_lede(self):
        for k,pg in J['pages'].items():self.assertIn('<p class="lede">'+RP.E(pg['desc'])+'</p>',pg['html'],k)
    def test_resources_have_rights_badges(self):
        n=0
        for r in D['records']:
            h=J['pages'][r['id']]['html']
            for x in r['resources']:
                n+=1;self.assertIn('data-rights="'+x['rights']+'"',h);self.assertIn(RP.E(x['url']),h)
            self.assertEqual(h.count('class="rights-badge'),len(r['resources']),r['id'])
        self.assertGreater(n,20)
    def test_wording_rules(self):
        for k,pg in J['pages'].items():
            h=pg['html'];t=text(h)
            self.assertNotIn('—',t,k);self.assertNotIn('–',t,k)
            for bad in('ordinary form','extraordinary form','tax-deductible','amazon.','isidore.co','/isidore/','/author/adrian-fortescue','orthodoxy'):self.assertNotIn(bad,h.lower(),(k,bad))
            self.assertNotIn('href="#/',h,k)
        self.assertNotIn('—',text(J['tpl']['full']+J['options']+''.join(J['info'].values())))
    def test_nav_link_and_app_route(self):
        idx=R('index.html');sec=idx.split('nav-secondary',1)[1].split('</div>',1)[0]
        self.assertIn('<a href="/rites/" data-nav="rites">Rites<span class="nav-long"> &amp; Liturgy</span></a>',sec)
        self.assertEqual(idx.count('scripts/rites.js'),1);self.assertNotIn('data/rites.js',idx)  # lazy-loaded
        app=R('app.js');self.assertIn("case 'rites':if(window.BCRites)window.BCRites.view(render,p.slice(1));else notfound()",app)
        self.assertIn("saints|rites)$/.test(s[0])",app);self.assertIn("p[0]==='rites'",app)
        self.assertNotIn('RITES_DATA',R('data/books.js'));self.assertNotIn('rites',R('scripts/analytics.js').lower())
    def test_builds_are_current(self):
        before=R('data/rites.js');B.main();self.assertEqual(R('data/rites.js'),before)
if __name__=='__main__':unittest.main()
