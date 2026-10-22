"""Build site/data/guide.js (editions guide, reading lists, Substack directory + latest-posts snapshot)."""
import json,re,html,datetime,urllib.request,os,sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,os.path.dirname(__file__))
from editions_data import W
from reading_lists import L
from substacks_src import FEATURED,S
if '--catalog-only' in sys.argv:
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / 'data' / 'guide.js'
    old = json.loads(path.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))
    old.update(editions=W, lists=L)
    path.write_text('window.GUIDE_DATA='+json.dumps(old,ensure_ascii=False,separators=(',',':'))+';\n', encoding='utf-8')
    print('Updated reading guides; preserved the existing feed snapshot.')
    sys.exit(0)
UA={'User-Agent':'Mozilla/5.0 (BibliothecaCatholica feed snapshot)'}
def feed(url,n=3):
    try:
        x=urllib.request.urlopen(urllib.request.Request(url.rstrip('/')+'/feed',headers=UA),timeout=40).read().decode('utf-8','ignore')
    except Exception as e:
        return None,[]
    def g(p,s):
        m=re.search(p,s,re.S);return html.unescape(m.group(1)).strip() if m else ''
    out=[]
    for it in re.findall(r'<item>(.*?)</item>',x,re.S)[:n]:
        t=g(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>',it)
        u=g(r'<link>(.*?)</link>',it)
        d=g(r'<pubDate>(.*?)</pubDate>',it)
        try: d=datetime.datetime.strptime(d[:16],'%a, %d %b %Y').strftime('%Y-%m-%d')
        except Exception: d=d[:16]
        sub=g(r'<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>',it)
        sub=re.sub('<[^>]+>','',html.unescape(sub))[:160]
        out.append({'t':t,'u':u,'d':d,'s':sub})
    return True,out
subs=[dict(name=a,author=b,url=c,cat=d,desc=e) for a,b,c,d,e in S]
with ThreadPoolExecutor(8) as ex:
    res=list(ex.map(lambda s:feed(s['url']),subs+[FEATURED]))
for s,(ok,posts) in zip(subs+[FEATURED],res):
    s['posts']=posts; s['ok']=bool(ok)
bad=[s['name'] for s in subs if not s['ok']]
if bad: print('WARNING feeds failed:',bad)
F=dict(FEATURED); F['posts']=res[-1][1]
# featured pick: use the requested post (title from feed if present)
pk=[p for p in F['posts'] if p['u'].rstrip('/')==F['pick']]
F['pickPost']=pk[0] if pk else {'t':'A Defense of Man’s Place in Nature','u':F['pick'],'d':'2026-09-10','s':''}
if not F['posts']:
    # keep last good snapshot if feed temporarily fails
    pass
G={'generated':datetime.date.today().isoformat(),'editions':W,'lists':L,'featured':F,'substacks':[{k:v for k,v in s.items() if k!='ok'} for s in subs]}
js='window.GUIDE_DATA='+json.dumps(G,ensure_ascii=False,separators=(',',':'))+';\n'
p=(os.path.join(os.path.dirname(__file__),'..','site','data','guide.js') if os.path.isdir(os.path.join(os.path.dirname(__file__),'..','site')) else os.path.join(os.path.dirname(__file__),'..','data','guide.js'))
open(p,'w').write(js)
print('wrote',p,len(js),'bytes;',len(W),'works,',sum(len(w['picks']) for w in W),'editions,',len(L),'lists,',sum(len(l['items']) for l in L),'list items,',len(subs),'substacks')
