"""Full-year saints calendar (facts only): shared helpers for tools/build_saints.py and tools/build_static.py.

Source: data/saints-calendar.json, written by tools/import_saints.py (see docs/SAINTS-CALENDAR.md). The file is
optional: with no file, nothing here adds a page, a link, or a byte to data/saints.js.

What it adds to the existing saints guide (no new page types, no per-saint pages):
- one static page per calendar day, /saints/calendar/<MM-DD>/ (366), which the app's #/saints/calendar/<MM-DD>
  view opens; it lists the guide's own saints for the day (Vatican News, labelled as before) and then every
  name the calendar lists, grouped by type, with facts and an outbound "CatholicSaints.Info" link;
- per-day counts in data/saints.js (`cal`), for the month grid, the Hodie line, and the saints landing;
- day links on the author pages and saint profiles of guide saints matched to a calendar entry.
CatholicSaints.Info stays link-only: nothing is fetched at build or run time and no text is copied.
"""
import datetime,html,json,re,unicodedata
from pathlib import Path
from urllib.parse import urlparse
E=html.escape
MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December']
DAYS_IN={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
ALL_DAYS=['%02d-%02d'%(m,d) for m in range(1,13) for d in range(1,DAYS_IN[m]+1)]
TYPES=[('feast','Feasts'),('marian-title','Marian titles'),('saint','Saints'),('pope','Popes'),('blessed','Blessed'),('martyr-group','Martyr groups'),('unknown','Other names')]
FACT_KEYS={'slug','name','type','born_date','born_place','died_date','died_place','beatified','canonized','url','dates','aliases','patronage','pd_life'}
HOSTS=('catholicsaints.info','catholicsaints.mobi')
MAX_FACT=160
HON={'saint','st','sts','saints','blessed','bl','bd','pope','the'}
def key(s):  # same as tools/build_saints.py key()
    s=unicodedata.normalize('NFKD',str(s));s=''.join(c for c in s if not unicodedata.combining(c)).lower()
    s=re.sub(r"[’'`]",'',s);s=re.sub(r'[^a-z0-9]+',' ',s).strip();w=s.split()
    while len(w)>1 and w[0] in HON:w=w[1:]
    return ' '.join(w)
def load(root):
    p=Path(root)/'data/saints-calendar.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
class CalendarError(ValueError):pass
def validate(cal):
    """Fail on anything that is not a short fact: unknown keys, em-dashes, Amazon, outside URLs, long text,
    and a public-domain life without a pre-1931 source."""
    def text(v,where):
        if not isinstance(v,str):raise CalendarError(where+': expected text')
        if '\u2014' in v:raise CalendarError(where+': em-dash')
        if re.search(r'amazon\.|amzn\.',v,re.I):raise CalendarError(where+': Amazon link')
        if len(v)>MAX_FACT:raise CalendarError(where+': longer than %d characters (prose?)'%MAX_FACT)
    for slug,s in cal['saints'].items():
        w='saint '+slug
        if set(s)-FACT_KEYS:raise CalendarError(w+': unexpected fields '+', '.join(sorted(set(s)-FACT_KEYS)))
        if s.get('slug')!=slug or not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*',slug):raise CalendarError(w+': bad slug')
        if s['type'] not in dict(TYPES):raise CalendarError(w+': bad type '+str(s['type']))
        if not s.get('dates') or any(d not in ALL_DAYS for d in s['dates']):raise CalendarError(w+': bad dates')
        for k in('name','born_date','born_place','died_date','died_place','beatified','canonized'):
            if k in s:text(s[k],w+'.'+k)
        for k in('aliases','patronage'):
            for v in s.get(k,[]):text(v,w+'.'+k)
        if s.get('url'):
            u=urlparse(s['url'])
            if u.scheme!='https' or u.hostname not in HOSTS:raise CalendarError(w+': outbound URL must be https on '+' or '.join(HOSTS))
        L=s.get('pd_life')
        if L is not None:
            if not(isinstance(L,dict) and L.get('text') and L.get('source_title') and L.get('source_url','').startswith('https://') and isinstance(L.get('source_year'),int) and L['source_year']<1931):
                raise CalendarError(w+': pd_life needs text, source_title, https source_url, and a source_year before 1931')
            if '\u2014' in L['text']:raise CalendarError(w+': pd_life em-dash')
    for md,d in cal['days'].items():
        if md not in ALL_DAYS:raise CalendarError('bad day '+md)
        for sl in d['slugs']:
            if sl not in cal['saints'] or md not in cal['saints'][sl]['dates']:raise CalendarError(md+': slug '+sl+' does not list this day')
        for n in d.get('names',[]):
            text(n['name'],md+' name')
            if n.get('url') and urlparse(n['url']).hostname not in HOSTS:raise CalendarError(md+': outside URL')
    return True
def counts(cal):
    return {md:len(d['slugs'])+len(d.get('names',[])) for md,d in sorted(cal['days'].items())}
def browser_summary(cal):
    """Small block for data/saints.js: per-day counts only (about 4 KB for 366 days)."""
    n=counts(cal)
    return {'n':{k:v for k,v in n.items() if v},'total':sum(n.values()),'source':'CatholicSaints.Info calendar'}
def url_path(u):
    p=urlparse(u or '');return '/'+'/'.join(x for x in p.path.split('/') if x).lower() if p.hostname in HOSTS else None
def match_guide(cal,guide_saints,alias_table):
    """slug -> guide saint id. 1) the same CatholicSaints.Info page as the guide's hand-checked tier 1 link
    (path compared, so .mobi and .info agree); 2) an exact multi-word alias key from data/saints-aliases.json
    (no one-word keys, no fuzzy matching). Returns (matches, method counts)."""
    by_path={url_path(s['catholicsaints']['url']):s['id'] for s in guide_saints if s.get('catholicsaints')}
    ids={s['id'] for s in guide_saints}
    M={};how={'url':0,'alias':0}
    for slug,s in cal['saints'].items():
        p=url_path(s.get('url'))
        if p and p in by_path:M[slug]=by_path[p];how['url']+=1;continue
        if s['type'] not in('saint','pope','blessed'):continue
        for nm in [s['name']]+s.get('aliases',[]):
            k=key(nm)
            if ' ' in k and alias_table.get(k) in ids:M[slug]=alias_table[k];how['alias']+=1;break
    return M,how
def fmt_day(md):return str(int(md[3:]))+' '+MONTHS[int(md[:2])-1]
def fmt_when(v):
    m=re.fullmatch(r'(\d{4})-(\d\d)-(\d\d)(.*)',v or '')
    if m and 1<=int(m.group(2))<=12:return str(int(m.group(3)))+' '+MONTHS[int(m.group(2))-1]+' '+str(int(m.group(1)))+m.group(4)
    return v
def oxford(xs):
    xs=list(xs);return xs[0] if len(xs)==1 else ' and '.join(xs) if len(xs)==2 else ', '.join(xs[:-1])+', and '+xs[-1]
def facts_line(s):
    out=[]
    for lab,dk,pk in(('Born','born_date','born_place'),('Died','died_date','died_place')):
        v=', '.join(fmt_when(s[k]) if k.endswith('date') else s[k] for k in(dk,pk) if s.get(k))
        if v:out.append(lab+' '+v+'.')
    if s.get('patronage'):out.append('Patron of '+oxford(s['patronage'])+'.')
    if s.get('beatified'):out.append('Beatified '+fmt_when(s['beatified'])+'.')
    if s.get('canonized'):out.append('Canonized '+fmt_when(s['canonized'])+'.')
    return ' '.join(out)
def neighbours(md):
    i=ALL_DAYS.index(md);return ALL_DAYS[i-1],ALL_DAYS[(i+1)%len(ALL_DAYS)]
CS_NOTE=('Names and facts are from the CatholicSaints.Info calendar, which keeps a long list of saints, blessed, and feasts for each day. '
         'Calendars differ, and this is not the General Roman Calendar. We copy no text from CatholicSaints.Info; read each life there.')
def day_page(md,cal,guide_today,matches,guide_href,a):
    """(title, description, body, h1) for /saints/calendar/<md>/. `guide_today` is [(saint, vatican news title)],
    `matches` slug -> guide id, `guide_href` id -> (href, label), `a` is build_static.a."""
    d=cal['days'].get(md,{'slugs':[]});S=cal['saints']
    rows={t:[] for t,_ in TYPES}
    for sl in d['slugs']:rows[S[sl]['type']].append(S[sl])
    total=len(d['slugs'])+len(d.get('names',[]))
    day=fmt_day(md)
    lede=(str(total)+(' name' if total==1 else ' names')+' the CatholicSaints.Info calendar lists for '+day+', with short facts and a link to read each life.') if total else 'No names are listed for '+day+' in the CatholicSaints.Info calendar.'
    h='<div class="page-head"><div class="eyebrow">Sancti · '+E(MONTHS[int(md[:2])-1])+'</div><h1>'+E('Saints of '+day)+'</h1><p class="lede">'+E(lede)+'</p></div>'
    if guide_today:
        h+='<section><h2>In our saints guide</h2><ul class="saint-list">'+''.join('<li class="saint-row">'+a(guide_href[s['id']][0],s['name'])+' <span class="saint-meta">'+E(guide_href[s['id']][1])+' · as listed by Vatican News: “'+E(t)+'”</span></li>' for s,t in guide_today)+'</ul><p class="small muted">Vatican News “Saint of the day” lists are shown as that page lists them, not as the official calendar.</p></section>'
    for t,label in TYPES:
        L=sorted(rows[t],key=lambda s:key(s['name']))
        names=sorted((n for n in d.get('names',[]) if n['type']==t),key=lambda n:key(n['name']))  # names with no slug: listed, no facts
        if not L and not names:continue
        h+='<section><h2>'+E(label)+' ('+str(len(L)+len(names))+')</h2><ul class="saint-list cal-facts">'
        for s in L:
            bits=[]
            if s['slug'] in matches:gh=guide_href[matches[s['slug']]];bits.append(a(gh[0],gh[1]))
            if s.get('url'):bits.append(a(s['url'],'CatholicSaints.Info ↗',True))
            other=[x for x in s['dates'] if x!=md]
            if other:bits.append('Also listed on '+', '.join(a('/saints/calendar/'+x+'/',fmt_day(x)) for x in other))
            fl=facts_line(s)
            if s.get('aliases'):fl=(fl+' ' if fl else '')+'Also called '+oxford(s['aliases'])+'.'
            life=''
            if s.get('pd_life'):
                L2=s['pd_life'];life='<blockquote class="pd-life">'+E(L2['text'])+'<footer class="small muted">From '+a(L2['source_url'],L2['source_title'],True)+' ('+str(L2['source_year'])+'), public domain.</footer></blockquote>'
            h+='<li class="saint-row"><b>'+E(s['name'])+'</b>'+(' <span class="saint-meta">'+E(fl)+'</span>' if fl else '')+(' <span class="saint-src">'+' · '.join(bits)+'</span>' if bits else '')+life+'</li>'
        for n in names:
            h+='<li class="saint-row">'+E(n['name'])+(' <span class="saint-src">'+a(n['url'],'CatholicSaints.Info ↗',True)+'</span>' if n.get('url') else '')+'</li>'
        h+='</ul></section>'
    prev,nxt=neighbours(md)
    h+='<p class="small muted">'+E(CS_NOTE)+' '+a('/saints/about/','Sources & method')+'</p>'
    h+='<p class="cal-nav">'+a('/saints/calendar/'+prev+'/','← '+fmt_day(prev))+' '+a('/saints/calendar/'+nxt+'/',fmt_day(nxt)+' →')+'</p>'
    h+='<p>'+a('/#/saints/calendar','The whole year')+' · '+a('/saints/','Saints & Hagiography')+'</p>'
    top=[s['name'] for s in sorted([S[x] for x in d['slugs']],key=lambda s:(dict((t,i) for i,(t,_) in enumerate(TYPES))[s['type']],key(s['name'])))][:2]
    desc_core='Saints, blessed, and feasts for '+day+(': '+oxford(top)+(', and more' if total>2 else '') if top else '')+'.'
    return 'Saints of '+day+' — Saints — Bibliotheca Catholica',desc_core,h,total
def months_html(cal,a):
    """The whole year as month lists of day links (for the static /saints/ page)."""
    n=counts(cal);out='<h2>The full-year calendar</h2><p>Every day of the year, with the saints, blessed, and feasts the CatholicSaints.Info calendar lists ('+format(sum(n.values()),',')+' names in all). Facts only, with a link to read each life.</p>'
    for m in range(1,13):
        days=[x for x in ALL_DAYS if int(x[:2])==m]
        out+='<h3>'+E(MONTHS[m-1])+'</h3><p class="cal-month">'+' '.join(a('/saints/calendar/'+x+'/',str(int(x[3:]))) for x in days)+'</p>'
    return out
def day_links(cal,slugs):
    """Sorted distinct days on which any of `slugs` is listed."""
    return sorted({d for sl in slugs for d in cal['saints'].get(sl,{}).get('dates',[])})
