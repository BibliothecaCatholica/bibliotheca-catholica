#!/usr/bin/env python3
"""Validate the dated reading plans and write data/reading-plans.json/.js.

Two inputs per plan: tools/reading_plans.py anchors each day to a passage in a hosted edition, and the plan's
`text` file (data/advent-2026.json for Advent 2026) holds every word readers see: the liturgical day, title,
theme, excerpt, attribution, reflection, and intro. That JSON file is the one source of truth the site page
and the Substack posts both read from (public at https://bibliothecacatholica.com/data/advent-2026.json).

Every day must point at a hosted reading-room edition (data/library.json, with its SHA-256), at a passage
that exists in that file and sits in one reader section, in an edition whose year evidence in EDITION_YEARS
is before 1931. Orthodoxy (pg-16769) is never used, and no editorially flagged author is used. Each excerpt
must be the hosted text word for word: every piece between … cuts is matched against the passage with only
whitespace collapsed, Gutenberg's _italic_ underscores and [n] or (n) footnote markers dropped, and a verse
line number at the end of a line dropped (see display() and excerpt_ok()). Site text has no em-dashes.
Part of `npm run build`.

    python3 tools/build_reading_plans.py
    python3 tools/build_reading_plans.py --selection out.md [--brand brand.md]   # also write selection notes
"""
import datetime,hashlib,json,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import reading_plans as RP
SITE='https://bibliothecacatholica.com/'
SIZE=35;WPM=200;CUTOFF=1931;BANNED_EDITIONS={'pg-16769'};EM='\u2014'
def split_text(raw):
    """Same as splitText() in scripts/library.js: blank-line blocks, trimmed, empties dropped."""
    return [p.strip() for p in re.split(r'\n\s*\n',raw.replace('\r','')) if p.strip()]
def display(s):
    """Reading form of a source paragraph: collapse whitespace, drop _italic_ markers and [n] or attached (n) footnote refs."""
    s=re.sub(r'\[\d+\]|(?<=\S)\(\d+\)','',s).replace('_','')
    return re.sub(r'\s+',' ',s).strip()
def flat(s):return re.sub(r'\s+',' ',s).strip()
def excerpt_ok(excerpt,paras):
    """True when each piece of the excerpt (split at … cuts) appears in the passage, in order, word for word.
    paras: the passage's raw blocks. A verse line number padded at the end of a line (for example 810) is dropped."""
    text=flat(' '.join(display(re.sub(r'[ \t]{2,}\d{1,4}[ \t]*(?=\n|$)','',b)) for b in paras));pos=0
    for piece in re.split(r'\s*…\s*',excerpt):
        piece=flat(piece)
        if not piece:continue
        k=text.find(piece,pos)
        if k<0:return False
        pos=k+len(piece)
    return True
def load_text(P):
    T=json.loads((ROOT/P['text']).read_text(encoding='utf-8'))
    assert T['id']==P['id'] and T['schema']==1,P['text']
    return T
_cache={}
def blocks(path):
    if path not in _cache:_cache[path]=split_text((ROOT/path).read_text(encoding='utf-8'))
    return _cache[path]
def build():
    lib=json.loads((ROOT/'data/library.json').read_text())
    works={w['id']:w for w in lib['works']}
    flags=json.loads((ROOT/'data/editorial-flags.json').read_text())
    flagged=set(flags.get('hubAuthors',[]))
    hub={a['id']:a for a in json.loads((ROOT/'data/catholic-hub.json').read_text())['authors']}
    out=[];ids=set()
    for P in RP.PLANS:
        assert P['id'] not in ids and re.fullmatch(r'[a-z0-9-]+',P['id']);ids.add(P['id'])
        T=load_text(P)
        start=datetime.date.fromisoformat(T['start']);end=datetime.date.fromisoformat(T['end'])
        n=(end-start).days+1
        assert len(P['days'])==n==len(T['days']),(P['id'],len(P['days']),len(T['days']),n)
        for s_ in (T['intro'],T['sub']):assert EM not in s_,'no em-dashes in site text'
        days=[]
        for i,(d,t) in enumerate(zip(P['days'],T['days'])):
            date=datetime.date.fromisoformat(d['d'])
            assert date==start+datetime.timedelta(days=i) and t['date']==d['d'] and t['day']==i+1,(P['id'],d['d'],t['date'])
            m=t['liturgicalDay']
            if 'Sunday' in m:assert date.weekday()==6,(d['d'],m)
            w=works[d['w']];e=next(x for x in w['editions'] if x['id']==d['e'])
            assert e.get('text') and e['access']=='full-text',d['e']
            assert e['id'] not in BANNED_EDITIONS,e['id']
            assert hashlib.sha256((ROOT/e['text']).read_bytes()).hexdigest()==e['sha256'],e['id']
            assert e['rights'].startswith('Public domain in the USA'),e['id']
            yr,kind,ev=RP.EDITION_YEARS[e['id']]
            assert isinstance(yr,int) and yr<CUTOFF and kind in('edition','translator'),e['id']
            assert not w.get('authorId') or (w['authorId'] in hub and w['authorId'] not in flagged),w['id']
            B=blocks(e['text']);a,b=d['p'];at=d['at']
            assert 0<=at<=a<=b<len(B),(d['d'],at,a,b,len(B))
            assert at//SIZE==a//SIZE==b//SIZE,('passage crosses a reader section',d['d'])
            start_pg=next((k for k,p in enumerate(B) if re.search(r'\*\*\* ?START OF (THE |THIS )?PROJECT GUTENBERG',p,re.I)),-1)
            assert a>start_pg,('passage is in the Gutenberg front matter',d['d'])
            words=sum(len(display(B[k]).split()) for k in range(a,b+1))
            assert excerpt_ok(t['excerpt'],B[a:b+1]),('excerpt is not word for word from the hosted passage',d['d'])
            sec=at//SIZE;href='#/read/'+w['id']+'/'+e['id']+'/'+str(sec)+'/'+str(at)
            assert t['links']['reader']==SITE+href,(d['d'],t['links']['reader'],href)
            assert t['links']['work']==SITE+'work/'+w['id']+'/',(d['d'],t['links']['work'])
            assert t['title']=='Day %d: %s'%(i+1,t['theme']),t['title']
            assert t['attribution']=='%s, %s, %s. %s.'%(t['author'],t['work'],t['location'],t['translation']),d['d']
            for k in ('liturgicalDay','title','subtitle','theme','attribution','reflection'):
                assert EM not in t[k],('no em-dashes in site text',d['d'],k)
                assert 'amazon.' not in t[k].lower(),d['d']
            days.append(dict(day=i+1,date=d['d'],marker=m,theme=t['theme'],work=w['id'],title=w['title'],author=d.get('a') or w['author'],authorId=w.get('authorId') or '',
                edition=e['id'],editionLabel=e['label'],contributors=[c['name'] for c in e.get('contributors',[]) if 'translat' in c['role'] or 'editor' in c['role']],
                year=yr,yearKind=kind,yearEvidence=ev,section=sec,anchor=at,start=a,end=b,href=href,
                words=words,minutes=max(1,math.ceil(words/WPM)),excerpt=t['excerpt'],
                location=t['location'],attrAuthor=t['author'],attrWork=t['work'],attrRest=', '+t['location']+'. '+t['translation']+'.',reflection=t['reflection']))
        out.append(dict(id=P['id'],t=T['title'],year=T['year'],start=T['start'],end=T['end'],sub=T['sub'],intro=T['intro'],text=P['text'],days=days))
    return out
def passage_text(day):
    e=next(x for w in json.loads((ROOT/'data/library.json').read_text())['works'] if w['id']==day['work'] for x in w['editions'] if x['id']==day['edition'])
    B=blocks(e['text']);return '\n\n'.join(display(B[k]) for k in range(day['start'],day['end']+1))
def md_cell(s):return s.replace('|','\\|').replace('\n',' ')
def selection_md(plan,brand=False):
    L=['# '+plan['t']+' '+str(plan['year'])+(': selection for the Substack series' if brand else ': proposed 26-day selection'),'',
       'Built from `tools/reading_plans.py` by `python3 tools/build_reading_plans.py`. Every passage is in a hosted reading-room edition; each excerpt was checked word for word by string match against the hosted TXT file (whitespace collapsed, Gutenberg _underscores_ and [n] or (n) footnote markers dropped). Live page (planned): '+SITE+'reading/'+plan['id']+'/','']
    if not brand:
        L+=['| Day | Date | Marker | Author | Work | Edition id | Anchor (section/paragraph) | Where | Excerpt opening |','|---|---|---|---|---|---|---|---|---|']
        for d in plan['days']:L.append('| '+' | '.join(md_cell(str(x)) for x in [d['day'],d['date'],d['marker'] or '',d['author'],d['title'],d['edition'],'%d / %d (passage %d to %d)'%(d['section'],d['anchor'],d['start'],d['end']),d['location'],' '.join(d['excerpt'].split()[:20])+'…'])+' |')
    else:
        L+=['| Day | Date | Marker | Author | Work | Hosted page URL | Edition and translation year | Reading time |','|---|---|---|---|---|---|---|---|']
        for d in plan['days']:L.append('| '+' | '.join(md_cell(str(x)) for x in [d['day'],d['date'],d['marker'] or '',d['author'],d['title']+' ('+d['location']+')',SITE+d['href'],str(d['year'])+(' (translator’s death year; no edition year in the file)' if d['yearKind']=='translator' else '')+': '+d['yearEvidence'],str(d['minutes'])+' min'])+' |')
        L+=['','## Exact passage text','','Each passage is the hosted text, paragraph for paragraph, with whitespace collapsed and Gutenberg italics underscores and footnote numbers removed. Quote from here, not from memory.','']
        for d in plan['days']:
            L+=['### Day %d, %s%s: %s, %s'%(d['day'],d['date'],(' ('+d['marker']+')') if d['marker'] else '',d['author'],d['title']),'',d['location']+'. '+d['editionLabel']+'. '+SITE+d['href'],'',passage_text(d),'']
    return '\n'.join(L)+'\n'
def main():
    plans=build()
    (ROOT/'data/reading-plans.json').write_text(json.dumps({'plans':plans},ensure_ascii=False,indent=1)+'\n')
    (ROOT/'data/reading-plans.js').write_text('window.READING_PLANS='+json.dumps({'plans':plans},ensure_ascii=False,separators=(',',':'))+';\n')
    a=sys.argv[1:]
    if '--selection' in a:Path(a[a.index('--selection')+1]).write_text(selection_md(plans[0]))
    if '--brand' in a:Path(a[a.index('--brand')+1]).write_text(selection_md(plans[0],True))
    print('Built %d reading plan(s): %s'%(len(plans),', '.join('%s (%d days)'%(p['id'],len(p['days'])) for p in plans)))
if __name__=='__main__':main()
