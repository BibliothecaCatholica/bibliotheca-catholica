"""Full-year saints calendar (facts only): shared helpers for tools/import_saints.py, tools/build_saints.py, and
tools/build_static.py. See docs/SAINTS-CALENDAR.md.

Two files:
- the raw import (`.local/saints-calendar.json`, git-ignored, never deployed): every fact field, slugs, and the
  source URLs, written by tools/import_saints.py for the record and for re-matching;
- `data/saints-days.json` (committed): per day, the calendar's entries in site style, with no source URLs and no
  slugs: `n` name, `t` type, `f` short facts, `o` other days the same person is kept on, `g` the guide saint id
  when matched. Optional: with no file, nothing here adds a page, a link, or a byte to data/saints.js.

At build time each day's list merges the guide's own saints (Vatican News "Saint of the day" dates in
data/saints.json) with the calendar entries into ONE list, deduplicated by person (guide id, or the normalized
name with Saint/St./Blessed/Pope dropped for matching only), grouped by type, with a short neutral note where the
sources disagree. No per-entry source links: the calendar's source is credited once, on the Resources page
(References, "Saints & hagiography"). Owner's decision, 2026-11-09.
"""
import html,json,re,unicodedata
from pathlib import Path
from urllib.parse import urlparse
E=html.escape
MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December']
DAYS_IN={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
ALL_DAYS=['%02d-%02d'%(m,d) for m in range(1,13) for d in range(1,DAYS_IN[m]+1)]
TYPES=[('feast','Feasts'),('marian-title','Marian titles'),('saint','Saints'),('pope','Popes'),('blessed','Blessed'),('martyr-group','Martyr groups'),('unknown','Other')]
TYPE_IDS=dict(TYPES)
TITLE={'saint':'Saint','pope':'Saint','blessed':'Blessed','martyr-group':'Saint'}
ENTRY_KEYS={'n','t','f','o','g'}
MAX_FACTS=400
HOSTS=('catholicsaints.info','catholicsaints.mobi')
HON={'saint','st','sts','saints','blessed','bl','bd','pope','the','venerable','ven'}
def key(s):  # tools/build_saints.py key(), plus 'venerable': for matching only, never shown
    s=unicodedata.normalize('NFKD',str(s));s=''.join(c for c in s if not unicodedata.combining(c)).lower()
    s=re.sub(r"[’'`]",'',s);s=re.sub(r'[^a-z0-9]+',' ',s).strip();w=s.split()
    while len(w)>1 and w[0] in HON:w=w[1:]
    return ' '.join(w)
def site_name(name,status=None):
    """Site style: 'Saint Thomas Aquinas' -> 'St. Thomas Aquinas', 'Saints X and Y' -> 'Sts. X and Y',
    'Pope Saint John Paul II' -> 'Pope St. John Paul II', 'Bl. X' -> 'Blessed X'. A bare guide name gets its
    title from `status` (saint, archangel -> St., blessed -> Blessed, venerable -> Venerable)."""
    n=re.sub(r'\s+',' ',str(name)).strip()
    n=re.sub(r'^(Pope\s+)?Saints\s+',lambda m:(m.group(1) or '')+'Sts. ',n)
    n=re.sub(r'^(Pope\s+)?(Saint|St\.?)\s+',lambda m:(m.group(1) or '')+'St. ',n)
    n=re.sub(r'^(Blessed|Bl\.|Bd\.)\s+','Blessed ',n)
    if status and not re.match(r'^(Pope |St\. |Sts\. |Blessed |Venerable |Our Lady|Holy |The )',n):
        n={'saint':'St. ','archangel':'St. ','blessed':'Blessed ','venerable':'Venerable '}.get(status,'')+n
    return n
def fmt_day(md):return str(int(md[3:]))+' '+MONTHS[int(md[:2])-1]
def fmt_when(v):
    m=re.fullmatch(r'(\d{4})-(\d\d)-(\d\d)(.*)',v or '')
    if m and 1<=int(m.group(2))<=12:return str(int(m.group(3)))+' '+MONTHS[int(m.group(2))-1]+' '+str(int(m.group(1)))+m.group(4)
    return v
def oxford(xs):
    xs=list(xs);return xs[0] if len(xs)==1 else ' and '.join(xs) if len(xs)==2 else ', '.join(xs[:-1])+', and '+xs[-1]
FACTS_MAX=300
def facts_line(s):
    """Short facts in a fixed order; a part that would push the line past FACTS_MAX characters is left out."""
    parts=[]
    for lab,dk,pk in(('Born','born_date','born_place'),('Died','died_date','died_place')):
        v=', '.join(fmt_when(s[k]) if k.endswith('date') else s[k] for k in(dk,pk) if s.get(k))
        if v:parts.append(lab+': '+v+'.')
    if s.get('beatified'):parts.append('Beatified: '+fmt_when(s['beatified'])+'.')
    if s.get('canonized'):parts.append('Canonized: '+fmt_when(s['canonized'])+'.')
    if s.get('patronage'):parts.append('Patronage: '+oxford(s['patronage'])+'.')
    if s.get('aliases'):parts.append('Also called '+oxford(s['aliases'])+'.')
    out=''
    for x in parts:
        if len(out)+1+len(x)<=FACTS_MAX:out=(out+' '+x).strip()
    return out
# ---------- import time: raw calendar -> data/saints-days.json ----------
def url_path(u):
    p=urlparse(u or '');return '/'+'/'.join(x for x in p.path.split('/') if x).lower() if p.hostname in HOSTS else None
def guide_keys(guide_saints,alias_table):
    """normalized multi-word name -> guide id (the guide's own alias table, plus each name)."""
    ids={s['id'] for s in guide_saints};K={}
    for k,i in alias_table.items():
        if ' ' in k and i in ids:K[k]=i
    for s in guide_saints:K.setdefault(key(s['name']),s['id'])
    return K
def match_guide(raw,guide_saints,alias_table):
    """slug -> guide id: the same CatholicSaints.Info page as a guide saint's hand-checked tier 1 link (path compared,
    so .mobi and .info agree), else an exact multi-word normalized name or alias. No one-word or fuzzy matches."""
    by_path={url_path(s['catholicsaints']['url']):s['id'] for s in guide_saints if s.get('catholicsaints')}
    K=guide_keys(guide_saints,alias_table);M={};how={'url':0,'name':0}
    for slug,s in raw['saints'].items():
        p=url_path(s.get('url'))
        if p and p in by_path:M[slug]=by_path[p];how['url']+=1;continue
        if s['type'] not in('saint','pope','blessed'):continue
        for nm in [s['name']]+s.get('aliases',[]):
            k=key(nm)
            if ' ' in k and k in K:M[slug]=K[k];how['name']+=1;break
    return M,how
def make_days(raw,guide_saints,alias_table):
    """The committed per-day file: names in site style, types, short facts, other days, guide ids. No URLs, no slugs."""
    M,how=match_guide(raw,guide_saints,alias_table);S=raw['saints'];days={}
    for md in ALL_DAYS:
        d=raw['days'].get(md);L=[]
        if d:
            seen=set()
            for sl in d['slugs']:
                s=S[sl];e={'n':site_name(s['name']),'t':s['type']}
                f=facts_line(s)
                if f:e['f']=f
                o=[x for x in s['dates'] if x!=md]
                if o:e['o']=o
                if sl in M:e['g']=M[sl]
                if (e['n'],e.get('f'),e['t']) in seen:continue  # two source pages, same name and facts: show once
                seen.add((e['n'],e.get('f'),e['t']));L.append(e)
            have={key(x['n']) for x in L}
            for n in d.get('names',[]):
                e={'n':site_name(n['name']),'t':n['type']}
                if key(e['n']) in have:continue  # a bare name repeating a full entry on the same day
                have.add(key(e['n']));L.append(e)
        if L:days[md]=L
    return {'note':'Facts only, per day, in site style. Built by tools/import_saints.py; no source URLs or slugs. The calendar facts source is credited on the Resources page. See docs/SAINTS-CALENDAR.md.',
            'matched':how,'days':days}
# ---------- build time ----------
class CalendarError(ValueError):pass
def load(root):
    p=Path(root)/'data/saints-days.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
def validate(doc,guide_ids):
    def text(v,w,mx):
        if not isinstance(v,str) or not v.strip():raise CalendarError(w+': expected text')
        if '\u2014' in v:raise CalendarError(w+': em-dash')
        if re.search(r'https?:|www\.|amazon|amzn\.|catholicsaints',v,re.I):raise CalendarError(w+': links and source names do not belong in entries')
        if len(v)>mx:raise CalendarError(w+': longer than %d characters (prose?)'%mx)
    if set(doc)-{'note','matched','days'}:raise CalendarError('unexpected top-level keys')
    for md,L in doc['days'].items():
        if md not in ALL_DAYS:raise CalendarError('bad day '+md)
        for i,e in enumerate(L):
            w='%s[%d]'%(md,i)
            if set(e)-ENTRY_KEYS:raise CalendarError(w+': unexpected fields '+', '.join(sorted(set(e)-ENTRY_KEYS)))
            text(e['n'],w+'.n',160)
            if e['t'] not in TYPE_IDS:raise CalendarError(w+': bad type')
            if 'f' in e:text(e['f'],w+'.f',MAX_FACTS)
            if any(x not in ALL_DAYS or x==md for x in e.get('o',[])):raise CalendarError(w+': bad other days')
            if 'g' in e and e['g'] not in guide_ids:raise CalendarError(w+': unknown guide saint '+e['g'])
    return True
def guide_type(s):
    v=(s.get('status') or {}).get('value')
    return {'saint':'saint','archangel':'saint','blessed':'blessed'}.get(v,'unknown')
_CD={}
def _cal_days(doc):
    if not doc:return {}
    c=_CD.get(id(doc))
    if c is None or c[0] is not doc:
        m={}
        for d,L in doc['days'].items():
            for e in L:
                if e.get('g'):m.setdefault(e['g'],set()).add(d)
        c=_CD[id(doc)]=(doc,m)
    return c[1]
def merged_day(md,doc,guide_saints,guide_href):
    """ONE list for the day: [{'name','type','href','facts','notes'}] grouped later by type.
    Guide saints listed by Vatican News on `md` and calendar entries are merged by guide id or normalized name."""
    days=doc['days'] if doc else {};cal=days.get(md,[])
    gid={s['id']:s for s in guide_saints}
    vn=lambda s:[v['date'] for v in (s['feasts'].get('vatican_news') or [])]
    cal_days_of=_cal_days(doc)  # guide id -> days the calendar keeps that saint on
    out=[];by_key={};by_gid={}
    def add(entry,keys,g):
        out.append(entry)
        for k in keys:by_key.setdefault(k,entry)
        if g:by_gid[g]=entry
    for s in sorted((s for s in guide_saints if md in vn(s)),key=lambda s:key(s['name'])):
        # on its own day a guide saint also answers to its other names, one-word ones included ("St. Monica")
        add({'name':site_name(s['name'],(s.get('status') or {}).get('value')),'type':guide_type(s),'href':guide_href(s),'facts':'','notes':[],'g':s['id'],'src':{'guide'}},[key(x) for x in [s['name']]+s.get('aliases',[])],s['id'])
    for e in cal:
        k=key(e['n']);g=e.get('g')
        hit=by_gid.get(g) if g else None
        if hit is None and k in by_key and (not by_key[k].get('facts') or by_key[k]['facts']==e.get('f','')):hit=by_key[k]
        if hit is not None:
            hit['src'].add('cal')
            if e.get('f') and not hit['facts']:hit['facts']=e['f']
            if hit['type']!=e['t']:
                if {hit['type'],e['t']}=={'saint','blessed'}:hit['notes'].append('Listed as Saint in some sources and Blessed in others.')
                elif hit['type'] in('saint','unknown') and e['t'] in('pope','martyr-group','feast','marian-title'):hit['type']=e['t']
            hit.setdefault('cal_o',set()).update(e.get('o',[]))
            if g and not hit.get('g'):hit['g']=g
            continue
        add({'name':e['n'],'type':e['t'],'href':guide_href(gid[g]) if g in gid else None,'facts':e.get('f',''),'notes':[],'g':g,'src':{'cal'},'cal_o':set(e.get('o',[]))},[k],g)
    for x in out:
        s=gid.get(x.get('g'))
        other=set(x.get('cal_o',()))
        if s:other|=set(vn(s))|cal_days_of.get(s['id'],set())
        other.discard(md)
        if s and x['src']!={'guide','cal'}:
            # on this day in one source only, while the other places the same person elsewhere
            elsewhere=(cal_days_of.get(s['id'],set()) if 'guide' in x['src'] else set(vn(s)))-{md}
            if elsewhere:x['notes'].insert(0,'Date differs between sources; also kept on '+days_list(elsewhere)+'.')
            other-=elsewhere
        if other:x['notes'].append('Also kept on '+days_list(other)+' in some calendars.')
    return out
def counts(doc,guide_saints):
    href=lambda s:''
    return {md:len(merged_day(md,doc,guide_saints,href)) for md in ALL_DAYS}
def browser_summary(doc,guide_saints):
    n=counts(doc,guide_saints);return {'n':{k:v for k,v in n.items() if v},'total':sum(n.values())}
def guide_days(doc,s):
    """Days the merged calendar lists a guide saint on (its Vatican News days and the calendar's)."""
    D={v['date'] for v in (s['feasts'].get('vatican_news') or [])}
    for md,L in (doc or {}).get('days',{}).items():
        if any(e.get('g')==s['id'] for e in L):D.add(md)
    return sorted(D)
def days_list(days,cap=4):
    d=sorted(days);shown=[fmt_day(x) for x in d[:cap]]
    if len(d)>cap:shown.append(str(len(d)-cap)+' other days')
    return oxford(shown)
def neighbours(md):
    i=ALL_DAYS.index(md);return ALL_DAYS[i-1],ALL_DAYS[(i+1)%len(ALL_DAYS)]
PAGE_NOTE=('This list combines the Vatican News “Saint of the day” pages with a long-form calendar of saints, blessed, and feasts '
           '(credited on our Resources page). Calendars differ, so a note marks each place the sources disagree. '
           'This is not the General Roman Calendar.')
def day_page(md,entries,a):
    """(title, description core, body, count) for /saints/calendar/<md>/ from merged_day() entries."""
    total=len(entries);day=fmt_day(md)
    lede=(str(total)+(' saint, blessed, or feast' if total==1 else ' saints, blessed, and feasts')+' kept on '+day+', with short facts.') if total else 'No saints are listed for '+day+' yet.'
    h='<div class="page-head"><div class="eyebrow">Sancti · '+E(MONTHS[int(md[:2])-1])+'</div><h1>'+E('Saints of '+day)+'</h1><p class="lede">'+E(lede)+'</p></div>'
    for t,label in TYPES:
        L=sorted((x for x in entries if x['type']==t),key=lambda x:(0 if x.get('href') else 1,key(x['name'])))
        if not L:continue
        h+='<section><h2>'+E(label)+' ('+str(len(L))+')</h2><ul class="saint-list cal-facts">'
        for x in L:
            nm=a(x['href'],x['name']) if x.get('href') else E(x['name'])
            h+='<li class="saint-row"><b>'+nm+'</b>'+(' <span class="saint-meta">'+E(x['facts'])+'</span>' if x['facts'] else '')+(' <span class="saint-note small muted">'+E(' '.join(x['notes']))+'</span>' if x['notes'] else '')+'</li>'
        h+='</ul></section>'
    prev,nxt=neighbours(md)
    h+='<p class="small muted">'+E(PAGE_NOTE)+' '+a('/references/','Resources')+' · '+a('/saints/about/','Sources & method')+'</p>'
    h+='<p class="cal-nav">'+a('/saints/calendar/'+prev+'/','← '+fmt_day(prev))+' '+a('/saints/calendar/'+nxt+'/',fmt_day(nxt)+' →')+'</p>'
    h+='<p>'+a('/#/saints/calendar','The whole year')+' · '+a('/saints/','Saints & Hagiography')+'</p>'
    order={t:i for i,(t,_) in enumerate(TYPES)}
    top=[x['name'] for x in sorted(entries,key=lambda x:(0 if x.get('href') else 1,order[x['type']],key(x['name'])))][:2]
    desc_core='Saints, blessed, and feasts for '+day+(': '+oxford(top)+(', and more' if total>2 else '') if top else '')+'.'
    return 'Saints of '+day+' — Saints — Bibliotheca Catholica',desc_core,h,total
def months_html(n,a):
    """The whole year as month lists of day links (static /saints/ page); `n` is counts()."""
    out='<h2>The full-year calendar</h2><p>Every day of the year, with the saints, blessed, and feasts kept on it ('+format(sum(n.values()),',')+' entries in all), short facts, and a note wherever calendars disagree.</p>'
    for m in range(1,13):
        days=[x for x in ALL_DAYS if int(x[:2])==m]
        out+='<h3>'+E(MONTHS[m-1])+'</h3><p class="cal-month">'+' '.join(a('/saints/calendar/'+x+'/',str(int(x[3:]))) for x in days)+'</p>'
    return out
