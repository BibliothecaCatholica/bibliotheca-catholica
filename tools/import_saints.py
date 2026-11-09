#!/usr/bin/env python3
"""Import the facts-only saints calendar (JSONL): a private raw copy (.local/, git-ignored) and data/saints-days.json.

    python3 tools/import_saints.py --input /path/to/saints-calendar-facts-full-year.jsonl
    python3 tools/import_saints.py --input tests/fixtures/saints-sample.jsonl --raw /tmp/raw.json --output /tmp/days.json --report /tmp/r.json

Facts only (see docs/SAINTS-CALENDAR.md). Every input key is checked against a WHITELIST of fact fields;
anything else (profile, biography, summary, text, notes, and any unknown key) is dropped and counted, so
no prose can reach the site. Records are deduplicated on slug, merging the days a slug is listed on.
A name with no slug (and no CatholicSaints URL to take one from) is kept only as a name on its day.
The site never fetches CatholicSaints.Info. Its URLs stay in the private raw copy (used only to match the guide's
hand-checked links); the committed per-day file has no URLs, no slugs, and no source names.

Checks: dates are MM-DD (02-29 allowed); slugs are [a-z0-9-]; no em-dashes in any kept text (replaced and
counted); no Amazon links (value dropped); URLs only on catholicsaints.info or catholicsaints.mobi;
a kept text value longer than MAX_FACT characters is treated as prose that slipped through and dropped.
Exit status 1 if any record was rejected and --strict is given. The report lists every problem.
"""
import argparse,json,re,sys
from collections import Counter,OrderedDict
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
MAX_FACT=160
DATE=re.compile(r'^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$')
DAYS_IN={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
MONTHS=['january','february','march','april','may','june','july','august','september','october','november','december']
SLUG=re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
HOSTS=('catholicsaints.info','catholicsaints.mobi')
# canonical field -> accepted input keys (first non-empty wins). Nothing outside this table is kept.
FIELDS=OrderedDict([
 ('date',('date','feast_date','feast','day','mmdd','calendar_date')),
 ('name',('name','display_name','title_name','saint')),
 ('slug',('slug','id','saint_slug')),
 ('aliases',('aliases','also_known_as','aka','alias','other_names')),
 ('type',('type','kind','category','record_type')),
 ('born_date',('born_date','birth_date','born_on')),
 ('born_place',('born_place','birth_place','born_in')),
 ('died_date',('died_date','death_date','died_on')),
 ('died_place',('died_place','death_place','died_in')),
 ('patronage',('patronage','patron_of','patronages','patron')),
 ('beatified',('beatified','beatification','beatification_date')),
 ('canonized',('canonized','canonised','canonization','canonisation','canonization_date')),
 ('url',('url','canonical_url','catholicsaints_url','source_url','link')),
])
NESTED={'born':('born_date','born_place'),'died':('died_date','died_place'),'birth':('born_date','born_place'),'death':('died_date','died_place')}
TYPES=OrderedDict([('saint','Saints'),('blessed','Blessed'),('pope','Popes'),('martyr-group','Martyr groups'),('marian-title','Marian titles'),('feast','Feasts'),('unknown','Other names')])
TYPE_MAP={'saint':'saint','saints':'saint','st':'saint','st.':'saint','blessed':'blessed','bl':'blessed','bl.':'blessed','beatus':'blessed',
 'pope':'pope','popes':'pope','martyr group':'martyr-group','martyr-group':'martyr-group','martyr_group':'martyr-group','martyrs':'martyr-group','group':'martyr-group','group of martyrs':'martyr-group',
 'marian title':'marian-title','marian-title':'marian-title','marian_title':'marian-title','marian':'marian-title','our lady':'marian-title',
 'feast':'feast','feasts':'feast','solemnity':'feast','memorial':'feast','unknown':'unknown','unlinked':'unknown','other':'unknown','':'unknown'}
PROSE_KEYS=re.compile(r'(profile|bio|biography|life|summary|description|text|body|content|notes?|excerpt|html|story|prayer|quote|reflection)',re.I)
AMAZON=re.compile(r'(amazon\.|amzn\.)',re.I)
def norm_date(v):
    """MM-DD from '01-21', '1-21', '01/21', 'January 21', or '2026-01-21'."""
    s=str(v or '').strip().lower()
    m=re.fullmatch(r'(?:\d{4}-)?(\d{1,2})[-/](\d{1,2})',s)
    if not m:
        m2=re.fullmatch(r'([a-z]+)\.?\s+(\d{1,2})',s)
        if m2 and m2.group(1)[:3] in [x[:3] for x in MONTHS]:m=(None,[x[:3] for x in MONTHS].index(m2.group(1)[:3])+1,int(m2.group(2)))
        else:return None
        mo,d=m[1],m[2]
    else:mo,d=int(m.group(1)),int(m.group(2))
    if not(1<=mo<=12 and 1<=d<=DAYS_IN[mo]):return None
    return '%02d-%02d'%(mo,d)
def clean_text(s,P,field,dateish=False):
    """Trim, collapse spaces, replace em-dashes (counted). Returns None for empty or rejected values."""
    if s is None:return None
    s=re.sub(r'\s+',' ',str(s)).strip()
    if not s:return None
    if AMAZON.search(s):P['amazon'].append({'field':field,'value':s[:120]});return None
    if '\u2014' in s:
        P['emdash_fixed'][field]+=1
        s=re.sub(r'\s*\u2014\s*','\u2013' if dateish else ', ',s)
    if len(s)>MAX_FACT:P['prose_dropped'].append({'field':field,'chars':len(s),'start':s[:60]});return None
    return s
def as_list(v):
    if v is None:return []
    if isinstance(v,list):return v
    return [x for x in re.split(r'\s*[;|\n]\s*',str(v)) if x.strip()]
def ok_url(u,P):
    if not u:return None
    u=str(u).strip()
    p=urlparse(u)
    host=(p.hostname or '').lower()
    if host.startswith('www.'):host=host[4:]
    if p.scheme not in('http','https') or host not in HOSTS:P['bad_url'].append(u[:120]);return None
    return 'https://'+host+(p.path or '/')
def slug_from_url(u):
    seg=[x for x in urlparse(u).path.split('/') if x]
    return seg[-1].lower() if seg and SLUG.match(seg[-1].lower()) else None
def read_records(path):
    for n,line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(),1):
        if line.strip():
            try:yield n,json.loads(line)
            except json.JSONDecodeError as e:yield n,{'__error__':str(e)}
def pick(rec,keys):
    for k in keys:
        if k in rec and rec[k] not in(None,'',[]):return rec[k]
    return None
def import_records(records):
    P={'bad_json':[],'bad_date':[],'missing_name':[],'missing_slug':[],'slug_from_url':0,'bad_slug':[],'bad_url':[],'amazon':[],
       'prose_dropped':[],'emdash_fixed':Counter(),'dropped_keys':Counter(),'type_unmapped':Counter(),'conflicts':[],'duplicate_rows':0}
    used={k for ks in FIELDS.values() for k in ks}|set(NESTED)
    saints=OrderedDict();days={}
    rows=0
    for n,rec in records:
        rows+=1
        if '__error__' in rec:P['bad_json'].append(n);continue
        for k in rec:
            if k not in used:P['dropped_keys'][k]+=1
        for k,(fd,fp) in NESTED.items():
            o=rec.get(k)
            if isinstance(o,dict):
                rec.setdefault(fd,o.get('date') or o.get('year'));rec.setdefault(fp,o.get('place'))
        r={f:pick(rec,ks) for f,ks in FIELDS.items()}
        md=norm_date(r['date'])
        name=clean_text(r['name'],P,'name')
        if not md:P['bad_date'].append({'line':n,'date':str(r['date'])[:20],'name':(name or '')[:60]});continue
        if not name:P['missing_name'].append(n);continue
        t=str(r['type'] or '').strip().lower()
        typ=TYPE_MAP.get(t)
        if typ is None:P['type_unmapped'][t]+=1;typ='unknown'
        url=ok_url(r['url'],P)
        slug=str(r['slug']).strip().lower() if r['slug'] else None
        if slug and not SLUG.match(slug):P['bad_slug'].append({'line':n,'slug':slug[:80]});slug=None
        if not slug and url:
            slug=slug_from_url(url)
            if slug:P['slug_from_url']+=1
        day=days.setdefault(md,{'slugs':[],'names':[]})
        if not slug:
            P['missing_slug'].append({'line':n,'date':md,'name':name[:80]})
            entry={'name':name,'type':typ}
            if url:entry['url']=url
            if entry not in day['names']:day['names'].append(entry)
            continue
        facts={'name':name,'type':typ}
        for f,dateish in(('born_date',1),('born_place',0),('died_date',1),('died_place',0),('beatified',1),('canonized',1)):
            v=clean_text(r[f],P,f,bool(dateish))
            if v:facts[f]=v
        if url:facts['url']=url
        al=[x for x in (clean_text(a,P,'aliases') for a in as_list(r['aliases'])) if x and x!=name]
        pa=[x for x in (clean_text(a,P,'patronage') for a in as_list(r['patronage'])) if x]
        if slug not in saints:
            s=OrderedDict(slug=slug,**facts);s['dates']=[];s['aliases']=[];s['patronage']=[]
            saints[slug]=s
        else:
            P['duplicate_rows']+=1
            s=saints[slug]
            for f,v in facts.items():
                if f not in s:s[f]=v
                elif s[f]!=v:P['conflicts'].append({'slug':slug,'field':f,'kept':s[f],'other':v})
        if md not in s['dates']:s['dates'].append(md)
        for a in al:
            if a not in s['aliases']:s['aliases'].append(a)
        for a in pa:
            if a not in s['patronage']:s['patronage'].append(a)
        if slug not in day['slugs']:day['slugs'].append(slug)
    out_saints=OrderedDict()
    for slug in sorted(saints):
        s=saints[slug];s['dates'].sort()
        for f in('aliases','patronage'):
            if not s[f]:del s[f]
        s['pd_life']=None  # slot for a public-domain life (pre-1931 source), filled later by hand; see docs
        out_saints[slug]=s
    out_days=OrderedDict((d,days[d]) for d in sorted(days))
    for d in out_days.values():
        if not d['names']:del d['names']
    counts=Counter(s['type'] for s in out_saints.values())
    stats={'rows':rows,'slugs':len(out_saints),'days':len(out_days),'by_type':dict(sorted(counts.items())),
           'unlinked_names':sum(len(d.get('names',[])) for d in out_days.values()),
           'multi_day_slugs':sum(1 for s in out_saints.values() if len(s['dates'])>1),
           'with_url':sum(1 for s in out_saints.values() if s.get('url')),
           'mobi_urls':sum(1 for s in out_saints.values() if 'catholicsaints.mobi' in s.get('url',''))}
    missing_days=[d for m in range(1,13) for d in ('%02d-%02d'%(m,x) for x in range(1,DAYS_IN[m]+1)) if d not in out_days]
    stats['missing_days']=missing_days
    return out_saints,out_days,stats,P
def report_json(stats,P):
    R=dict(stats)
    for k,v in P.items():
        if isinstance(v,Counter):R[k]=dict(v.most_common())
        elif isinstance(v,list):R[k+'_count']=len(v);R[k]=v[:200]
        else:R[k]=v
    return R
def dump(data):
    """Stable JSON with one saint and one day per line, so diffs stay readable."""
    head=OrderedDict((k,v) for k,v in data.items() if k not in('saints','days'))
    L=['{']
    for k,v in head.items():L.append(json.dumps(k)+':'+json.dumps(v,ensure_ascii=False)+',')
    L.append('"saints":{')
    items=list(data['saints'].items())
    L+=[json.dumps(k)+':'+json.dumps(v,ensure_ascii=False,separators=(',',':'))+(',' if i<len(items)-1 else '') for i,(k,v) in enumerate(items)]
    L.append('},"days":{')
    items=list(data['days'].items())
    L+=[json.dumps(k)+':'+json.dumps(v,ensure_ascii=False,separators=(',',':'))+(',' if i<len(items)-1 else '') for i,(k,v) in enumerate(items)]
    L.append('}}')
    return '\n'.join(L)+'\n'
def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input',required=True)
    ap.add_argument('--raw',default=str(ROOT/'.local/saints-calendar.json'),help='full import with slugs and source URLs (git-ignored; never deployed)')
    ap.add_argument('--output',default=str(ROOT/'data/saints-days.json'),help='the committed per-day file the site builds from')
    ap.add_argument('--report');ap.add_argument('--source',default='CatholicSaints.Info calendar (catholicsaints.mobi portable calendar), facts only')
    ap.add_argument('--strict',action='store_true',help='exit 1 if any record was rejected')
    a=ap.parse_args(argv)
    sys.path.insert(0,str(ROOT/'tools'));import saints_calendar as SC
    saints,days,stats,P=import_records(read_records(a.input))
    raw=OrderedDict(note='Raw facts-only import (private; never deployed). Built by tools/import_saints.py. See docs/SAINTS-CALENDAR.md.',
                    source=a.source,types=TYPES,stats={k:v for k,v in stats.items() if k!='missing_days'},saints=saints,days=days)
    Path(a.raw).parent.mkdir(parents=True,exist_ok=True);Path(a.raw).write_text(dump(raw),encoding='utf-8')
    guide=json.loads((ROOT/'data/saints.json').read_text())['saints']
    alias=json.loads((ROOT/'data/saints-aliases.json').read_text())['aliases']
    doc=SC.make_days(raw,guide,alias)
    SC.validate(doc,{g['id'] for g in guide})
    Path(a.output).write_text(dump_days(doc),encoding='utf-8')
    stats['matched_to_guide']=doc['matched']
    R=report_json(stats,P)
    if a.report:Path(a.report).write_text(json.dumps(R,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
    print('import_saints: %d rows -> %d slugs on %d days (%s); %d unlinked names; %d multi-day slugs; matched to the guide: %s'%(stats['rows'],stats['slugs'],stats['days'],', '.join('%s %d'%kv for kv in stats['by_type'].items()),stats['unlinked_names'],stats['multi_day_slugs'],json.dumps(doc['matched'])))
    probs={k:(len(v) if isinstance(v,list) else sum(v.values()) if isinstance(v,Counter) else v) for k,v in P.items()}
    print('problems:',json.dumps(probs))
    if stats['missing_days']:print('days with no record:',len(stats['missing_days']),stats['missing_days'][:12])
    print('wrote',a.raw,'(private) and',a.output)
    rejected=len(P['bad_json'])+len(P['bad_date'])+len(P['missing_name'])
    return 1 if a.strict and rejected else 0
def dump_days(doc):
    L=['{"note":'+json.dumps(doc['note'],ensure_ascii=False)+',','"matched":'+json.dumps(doc['matched'])+',','"days":{']
    items=list(doc['days'].items())
    L+=[json.dumps(k)+':'+json.dumps(v,ensure_ascii=False,separators=(',',':'))+(',' if i<len(items)-1 else '') for i,(k,v) in enumerate(items)]
    L.append('}}');return '\n'.join(L)+'\n'
if __name__=='__main__':sys.exit(main())
