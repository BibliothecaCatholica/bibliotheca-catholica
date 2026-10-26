"""v20 dated reading plans: Advent with the Fathers 2026 (tools/reading_plans.py)."""
import datetime,html,json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import build_reading_plans as B,reading_plans as RP
PLAN=json.loads((ROOT/'data/reading-plans.json').read_text())['plans'][0]
LIB={w['id']:w for w in json.loads((ROOT/'data/library.json').read_text())['works']}
PAGE=(ROOT/'reading/advent-2026/index.html').read_text()
def raw_blocks(path):  # independent re-implementation of splitText() in scripts/library.js
    return [p.strip() for p in re.split(r'\n\s*\n',(ROOT/path).read_text(encoding='utf-8').replace('\r','')) if p.strip()]
def hex_rgb(h):h=h.lstrip('#');return [int(h[i:i+2],16)/255 for i in (0,2,4)]
def lum(h):return sum(w*((c/12.92) if c<=0.03928 else ((c+0.055)/1.055)**2.4) for w,c in zip((0.2126,0.7152,0.0722),hex_rgb(h)))
def ratio(a,b):x,y=sorted((lum(a),lum(b)),reverse=True);return (x+0.05)/(y+0.05)
class ReadingPlans(unittest.TestCase):
    def test_generated_files_are_current(self):
        self.assertEqual(json.loads((ROOT/'data/reading-plans.json').read_text())['plans'],B.build())
        js=(ROOT/'data/reading-plans.js').read_text()
        self.assertEqual(json.loads(js[len('window.READING_PLANS='):-2])['plans'],B.build())
        ids=re.search(r"var IDS=\[([^\]]*)\]",(ROOT/'scripts/plans.js').read_text()).group(1)
        self.assertEqual(re.findall(r"'([a-z0-9-]+)'",ids),[p['id'] for p in B.build()])
    def test_26_days_on_the_right_dates(self):
        days=PLAN['days'];self.assertEqual(len(days),26)
        self.assertEqual((PLAN['start'],PLAN['end']),('2026-11-29','2026-12-24'))
        for i,d in enumerate(days):
            self.assertEqual(d['day'],i+1);self.assertEqual(d['date'],(datetime.date(2026,11,29)+datetime.timedelta(days=i)).isoformat())
        by={d['date']:d['marker'] for d in days}
        for iso,word in (('2026-11-29','First Sunday of Advent'),('2026-12-06','Second Sunday of Advent'),('2026-12-13','Gaudete'),('2026-12-20','Fourth Sunday of Advent'),('2026-12-08','Immaculate Conception'),('2026-12-24','Christmas Eve')):
            self.assertIn(word,by[iso])
        for iso in ('2026-11-29','2026-12-06','2026-12-13','2026-12-20'):self.assertEqual(datetime.date.fromisoformat(iso).weekday(),6)
        self.assertEqual(sum('Sunday' in d['marker'] for d in days),4)
        ant=['Sapientia','Adonai','Radix Jesse','Clavis David','Oriens','Rex Gentium','Emmanuel']
        for k,name in enumerate(ant):self.assertIn('O '+name,by['2026-12-%d'%(17+k)])
    def test_links_resolve_to_hosted_passages(self):
        for d in PLAN['days']:
            w=LIB[d['work']];e=next(x for x in w['editions'] if x['id']==d['edition'])
            self.assertTrue(e.get('text'));self.assertEqual(e['access'],'full-text')
            bl=raw_blocks(e['text'])
            self.assertTrue(d['anchor']<=d['start']<=d['end']<len(bl),d['day'])
            self.assertEqual(d['section'],d['anchor']//35)
            self.assertEqual(d['start']//35,d['section']);self.assertEqual(d['end']//35,d['section'])
            self.assertEqual(d['href'],'#/read/%s/%s/%d/%d'%(d['work'],d['edition'],d['section'],d['anchor']))
            self.assertIn('href="/'+d['href']+'"',PAGE)
            self.assertTrue((ROOT/'work'/d['work']/'index.html').exists(),d['work'])
            if d['authorId']:self.assertTrue((ROOT/'author'/d['authorId']/'index.html').exists())
    def test_editions_are_pre_1931_and_nothing_flagged(self):
        flags=json.loads((ROOT/'data/editorial-flags.json').read_text())
        flagged_books={str(k) for k in flags.get('books',{})};flagged_authors=set(flags.get('hubAuthors',[]))
        for d in PLAN['days']:
            self.assertNotEqual(d['edition'],'pg-16769')
            self.assertLess(d['year'],1931);self.assertIn(d['yearKind'],('edition','translator'))
            self.assertEqual(RP.EDITION_YEARS[d['edition']][0],d['year'])
            self.assertTrue(re.search(r'\b1[5-9]\d\d\b',d['yearEvidence']))
            self.assertNotIn(d['authorId'],flagged_authors)
            self.assertNotIn(d['edition'].replace('pg-',''),flagged_books)
            e=next(x for x in LIB[d['work']]['editions'] if x['id']==d['edition'])
            self.assertTrue(e['rights'].startswith('Public domain in the USA'))
    def test_quotes_match_the_source(self):
        """Each quote is the passage's own first words. Checked against the raw block with a pattern that
        allows only whitespace, Gutenberg underscores, and footnote markers between the quoted words."""
        for d in PLAN['days']:
            e=next(x for x in LIB[d['work']]['editions'] if x['id']==d['edition'])
            bl=raw_blocks(e['text']);words=d['quote'].split(' ')
            self.assertTrue(12<=len(words)<=20,d['day'])
            mark=r'(?:_|\[\d+\]|\(\d+\))*'
            pat=''.join(r'\s+'+mark if c==' ' else re.escape(c)+mark for c in d['quote'])
            hit=[k for k in range(d['start'],d['end']+1) if re.match(r'(?:_|\s)*'+pat,bl[k])]
            self.assertTrue(hit,(d['day'],d['quote']))
            if len(words)<20:self.assertEqual(B.display(bl[hit[0]]),d['quote']);self.assertFalse(d['cut'])  # a short opening paragraph is quoted whole
            self.assertIn(html.escape('“'+d['quote']+('…' if d['cut'] else '')+'”'),PAGE)
            self.assertEqual(d['cut'],B.display(bl[hit[0]])!=d['quote'])
    def test_static_page_seo(self):
        t=re.search(r'<title>(.*?)</title>',PAGE).group(1);desc=re.search(r'<meta name="description" content="([^"]*)">',PAGE).group(1)
        self.assertTrue(150<=len(html.unescape(desc))<=160,len(desc))
        self.assertIn('<link rel="canonical" href="https://bibliothecacatholica.com/reading/advent-2026/">',PAGE)
        h1=re.findall(r'<h1[^>]*>(.*?)</h1>',re.search(r'<main.*?</main>',PAGE,re.S).group(0))
        self.assertEqual(len(h1),1);self.assertIn('Advent',h1[0])
        self.assertIn('"@type":"BreadcrumbList"',PAGE);self.assertIn('https://bibliothecacatholica.com/reading/advent-2026/',PAGE)
        self.assertEqual(PAGE.count('googletagmanager.com/gtag/js'),1);self.assertRegex(PAGE,r"send_page_view'?\s*:\s*false")
        titles,descs={},{}
        for f in (ROOT/'docs/static-pages.txt').read_text().split():
            s=(ROOT/f).read_text();titles.setdefault(re.search(r'<title>(.*?)</title>',s).group(1),[]).append(f);descs.setdefault(re.search(r'<meta name="description" content="([^"]*)">',s).group(1),[]).append(f)
        self.assertEqual(titles[t],['reading/advent-2026/index.html']);self.assertEqual(descs[desc],['reading/advent-2026/index.html'])
        for s in (t,desc,PLAN['intro'],PLAN['sub'])+tuple(x for d in PLAN['days'] for x in (d['note'],d['ref'],d['marker'])):
            self.assertNotIn('\u2014',s.replace(' — Bibliotheca Catholica',''));self.assertNotIn('tax-deductible',s.lower())
        self.assertNotIn('amazon.',PAGE.lower())
    def test_listed_and_linked(self):
        self.assertIn('<loc>https://bibliothecacatholica.com/reading/advent-2026/</loc>',(ROOT/'sitemap.xml').read_text())
        self.assertIn('href="/reading/advent-2026/"',(ROOT/'reading/index.html').read_text())
        self.assertIn('href="/reading/advent-2026/"',(ROOT/'index.html').read_text())
        self.assertIn("#/reading/advent-2026",(ROOT/'app.js').read_text())
        self.assertIn('scripts/plans.js',(ROOT/'index.html').read_text())
    def test_static_page_lists_every_day_without_a_today_highlight(self):
        self.assertEqual(PAGE.count('<li class="plan-day'),26)
        self.assertNotIn('is-today',PAGE);self.assertNotIn('aria-current="date"',PAGE)
        self.assertEqual(PAGE.count('data-rights="public_domain_us"'),26)
    def test_contrast_light_and_dark(self):
        css=(ROOT/'styles.css').read_text()
        themes=[dict(re.findall(r'--([a-z0-9-]+):(#[0-9a-fA-F]{6})',blk)) for blk in re.findall(r'\{([^}]*--card:[^}]*)\}',css)[:2]]
        self.assertEqual(len(themes),2)
        for v in themes:
            for fg in ('ink','ink2','muted','gold-ink','rubric'):
                for bg in ('card','bg'):self.assertGreaterEqual(ratio(v[fg],v[bg]),4.5,(fg,bg,v[fg],v[bg]))
            self.assertGreaterEqual(ratio(v['on-rubric'],v['rubric']),4.5)
        pc=(ROOT/'styles/plans.css').read_text()
        self.assertIn('@media print',pc);self.assertNotRegex(pc,r'opacity:\s*\.[0-8]')
        used=set(re.findall(r'color:var\(--([a-z0-9-]+)\)',pc))
        self.assertTrue(used<= {'ink','ink2','muted','gold-ink','rubric','on-rubric'},used)
    def test_no_analytics_events_added(self):
        js=(ROOT/'scripts/plans.js').read_text()
        self.assertNotIn('track(',js);self.assertNotIn('gtag',js);self.assertNotIn('BCAnalytics',js)
if __name__=='__main__':unittest.main()
