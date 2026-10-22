"""Find verified LibriVox recordings for reading-room works and edition guides.
Network: librivox.org public API (no key). Writes data/librivox.json and data/librivox.js.
A match needs the same core title (ignoring a leading article, a trailing parenthetical such as
"(Pusey translation)", and Saint/St.) AND an author-name token in common. Volumes/partial
recordings are skipped. Re-run and review the printout when the catalog changes.
For reading-room works (a hosted text), it also writes data/librivox/<recording id>.json with the
recording's chapter MP3s (archive.org, forced to https) so the reader's Listen dock can play them
in the page. A work may list extra LibriVox titles in "audioTitles" (exact recording titles only)."""
import json,re,time,unicodedata,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STOP={'the','a','an','of','on','saint','st','and','de','la','le','von','van','pope','blessed','anonymous','et','al','ed'}
def norm(s):
    s=unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
    s=re.sub(r"[’'`]",'',s);return ' '.join('st' if w=='saint' else w for w in re.sub(r'[^a-z0-9]+',' ',s).split())
def core(t):
    t=re.sub(r'\([^)]*\)','',t);t=re.split(r'[:;]',t)[0];t=norm(t);return re.sub(r'^(the|a|an) ','',t).strip()
BAD=re.compile(r'\b(vol|volume|volumes|book [ivx\d]+|part [ivx\d]+|selections?|abridged|excerpts?)\b',re.I)
def api(title):
    u='https://librivox.org/api/feed/audiobooks/?'+urllib.parse.urlencode({'title':'^'+title,'format':'json','extended':'1','limit':'50'})
    req=urllib.request.Request(u,headers={'User-Agent':'BibliothecaCatholica-linkcheck/1.0 (+https://bibliothecacatholica.com)'})
    try:
        with urllib.request.urlopen(req,timeout=40) as r:return json.load(r).get('books',[])
    except Exception:return []
def tracks(book_id):
    u='https://librivox.org/api/feed/audiobooks/?'+urllib.parse.urlencode({'id':book_id,'format':'json','extended':'1'})
    req=urllib.request.Request(u,headers={'User-Agent':'BibliothecaCatholica-linkcheck/1.0 (+https://bibliothecacatholica.com)'})
    with urllib.request.urlopen(req,timeout=60) as r:b=json.load(r)['books'][0]
    out=[]
    for x in sorted(b.get('sections',[]),key=lambda x:int(x.get('section_number') or 0)):
        mp3=(x.get('listen_url') or '').replace('http://','https://').replace('://www.archive.org/','://archive.org/')
        if not mp3.startswith('https://archive.org/download/'):continue
        out.append({'n':int(x.get('section_number') or 0),'t':(x.get('title') or '').strip(),'mp3':mp3,'s':int(x.get('playtime') or 0),
                    'r':', '.join(r.get('display_name','') for r in x.get('readers',[]))})
    return {'id':int(b['id']),'title':b['title'],'url':(b.get('url_librivox') or '').replace('://www.librivox.org','://librivox.org'),
            'zip':b.get('url_zip_file',''),'sections':out}
def targets():
    lib=json.loads((ROOT/'data/library.json').read_text())
    g=(ROOT/'data/guide.js').read_text();G=json.loads(g[g.index('=')+1:].strip().rstrip(';'))
    out=[]
    for w in lib['works']:
        if w.get('tradition')=='Anglican':continue
        out.append(('work',w['id'],[w['title']]+w.get('audioTitles',[]),w['author']))
    for e in G['editions']:
        if not e['a']:continue
        titles=[x.strip() for x in re.split(r' & |, ',re.sub(r'^More \w+: ','',e['t'])) if x.strip()]
        out.append(('edition',e['id'],titles,e['a']))
    return out
def main():
    res={'work':{},'edition':{}};cache={}
    for kind,key,titles,author in targets():
        at={t for t in norm(author).split() if t not in STOP and len(t)>=4}
        hits=[]
        for t in titles:
            ct=core(t)
            if len(ct)<3:continue
            q=re.sub(r'\([^)]*\)','',t).split(':')[0].strip()
            q=re.sub(r'^(The|A|An) ','',q)
            if q not in cache:cache[q]=api(q);time.sleep(0.4)
            for b in cache[q]:
                if core(b['title'])!=ct or BAD.search(b['title']):continue
                names=norm(' '.join((a.get('first_name','')+' '+a.get('last_name','')) for a in b.get('authors',[]))).split()
                if not at or not (at & set(names)):continue
                url=(b.get('url_librivox') or '').replace('://www.librivox.org','://librivox.org')
                if not url.startswith('https://librivox.org/'):continue
                h={'id':int(b['id']),'title':b['title'],'url':url,'lang':b.get('language',''),'time':b.get('totaltime','')}
                if h not in hits:hits.append(h)
        hits.sort(key=lambda h:(h['lang']!='English',h['id']))
        if hits:res[kind][key]=hits
        print(kind,key,'->',[(h['title'],h['lang']) for h in hits])
    lib=json.loads((ROOT/'data/library.json').read_text())
    hosted={w['id'] for w in lib['works'] if any(e.get('text') for e in w['editions'])}
    (ROOT/'data/librivox').mkdir(exist_ok=True)
    for key,hits in res['work'].items():
        if key not in hosted:continue
        for h in hits:
            if h['lang']!='English':continue
            try:t=tracks(h['id']);time.sleep(0.4)
            except Exception as err:print('tracks failed',h['id'],err);continue
            if t['sections']:
                (ROOT/'data/librivox'/f"{h['id']}.json").write_text(json.dumps(t,ensure_ascii=False,indent=1)+'\n');h['tracks']=len(t['sections'])
    data={'generated':time.strftime('%Y-%m-%d'),'note':'Generated by tools/fetch_librivox.py (title + author match against the LibriVox API).',**res}
    (ROOT/'data/librivox.json').write_text(json.dumps(data,ensure_ascii=False,indent=1)+'\n')
    (ROOT/'data/librivox.js').write_text('window.LIBRIVOX='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
    print(len(res['work']),'works,',len(res['edition']),'edition guides matched')
if __name__=='__main__':main()
