"""Link-health check for every outbound URL in the site's data (no build step; network only).

    python3 tools/check_links.py [--isidore-sample 60] [--workers 24] [--out docs/link-health.json]

* Extracts http(s) URLs from data/*.js, data/*.json, app.js, scripts/, and index.html.
* isidore.co per-book/per-folder URLs (thousands) are sampled, not exhaustively crawled.
* GET with a desktop UA, 20 s timeout, one retry at 45 s. Classifies:
  ok | redirect-offsite (different registrable domain: possible hijack/parking) | soft-404/parked
  (title or body markers) | client-error | server-error | blocked (401/403/429, usually bot protection) | timeout/error.
Writes a JSON report plus a Markdown summary next to it. Nothing on the site is changed."""
import argparse,concurrent.futures as cf,json,random,re,ssl,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 BibliothecaCatholica-linkcheck'
PARKED=re.compile(r'domain (is )?for sale|buy this domain|parked (free|domain)|site not found|this domain may be for sale|hugedomains|sedo\.com|dan\.com|casino|slot gacor|togel',re.I)
URL=re.compile(r'https?://[^\s"\'<>\\)\]]+')
URLJ=re.compile(r'https?://[^\s"<>\\\]]+')  # JSON / generated data: apostrophes and parentheses are legal in URLs
def sources():
    files=[p for p in (ROOT/'data').glob('*.js')]+[p for p in (ROOT/'data').glob('*.json')]+[ROOT/'app.js',ROOT/'index.html']+list((ROOT/'scripts').glob('*.js'))
    files=[p for p in files if p.name not in('books.json','catholic-hub.json')]  # books.js / data.js already cover these
    seen={}
    for p in files:
        txt=p.read_text(errors='ignore');rx=URLJ if (p.suffix=='.json' or txt.lstrip().startswith('window.')) else URL
        for u in rx.findall(txt):
            u=u.rstrip('.,;')
            while u.endswith(')') and u.count(')')>u.count('('):u=u[:-1]
            if '{' in u:continue  # URL templates
            if 'localhost' in u or 'bibliothecacatholica.com' in u or u.endswith(("'+","+'")):continue
            seen.setdefault(u,set()).add(p.name)
    return seen
def reg(host):
    parts=(host or '').lower().split('.');return '.'.join(parts[-3:] if len(parts)>2 and parts[-2] in('co','com','org','ac','gov','edu') and len(parts[-1])==2 else parts[-2:])
def fetch(u,timeout):
    u=urllib.parse.quote(u,safe=":/?#[]@!$&'()*+,;=%~")
    req=urllib.request.Request(u,headers={'User-Agent':UA,'Accept':'text/html,*/*;q=0.8','Range':'bytes=0-65535'})
    ctx=ssl.create_default_context()
    with urllib.request.urlopen(req,timeout=timeout,context=ctx) as r:
        body=r.read(65536).decode('utf-8','ignore');return r.status,r.geturl(),body
def check(u):
    last=None
    for t in (20,45):
        try:
            st,final,body=fetch(u,t);title=(re.search(r'<title[^>]*>([^<]{0,200})',body,re.I) or [None,''])[1].strip()
            off=reg(urllib.parse.urlparse(final).hostname)!=reg(urllib.parse.urlparse(u).hostname)
            cls='ok'
            if PARKED.search(title) or (len(body)<4000 and PARKED.search(body)):cls='soft-404/parked'
            elif off:cls='redirect-offsite'
            return dict(url=u,status=st,final=final,title=title[:120],cls=cls)
        except urllib.error.HTTPError as e:
            c=e.code;cls='blocked' if c in(401,403,429) else 'client-error' if c<500 else 'server-error'
            last=dict(url=u,status=c,final=u,title='',cls=cls)
            if c in(404,410):return last
        except Exception as e:
            last=dict(url=u,status=0,final=u,title=str(e)[:120],cls='timeout/error')
    return last
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--isidore-sample',type=int,default=60);ap.add_argument('--workers',type=int,default=24)
    ap.add_argument('--out',default=str(ROOT/'docs/link-health.json'));a=ap.parse_args()
    S=sources();isi=[u for u in S if 'isidore.co/' in u and ('/CalibreLibrary/' in u or '/calibre/' in u)]
    rest=[u for u in S if u not in isi];random.seed(1);sample=random.sample(isi,min(a.isidore_sample,len(isi)))
    todo=sorted(rest)+sample;t0=time.time();res=[]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for r in ex.map(check,todo):r['files']=sorted(S[r['url']]);res.append(r)
    from collections import Counter;C=Counter(r['cls'] for r in res)
    rep=dict(checked=time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime()),seconds=round(time.time()-t0),total_urls=len(S),checked_urls=len(todo),isidore_urls=len(isi),isidore_sampled=len(sample),summary=dict(C),results=sorted(res,key=lambda r:(r['cls']=='ok',r['url'])))
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(rep,ensure_ascii=False,indent=1)+'\n')
    md=[f"# Link health ({rep['checked']})",'',f"Checked {len(todo)} of {len(S)} outbound URLs ({len(sample)} sampled from {len(isi)} isidore.co book/folder URLs) in {rep['seconds']} s.",'','| Class | Count |','|---|---|']+[f'| {k} | {v} |' for k,v in C.most_common()]+['','## Needs review (not ok)','','| Class | Status | URL | Final URL / note | Files |','|---|---|---|---|---|']
    md+=[f"| {r['cls']} | {r['status']} | {r['url']} | {(r['final'] if r['final']!=r['url'] else r['title'])[:90]} | {', '.join(r['files'])} |" for r in rep['results'] if r['cls']!='ok']
    Path(a.out).with_suffix('.md').write_text('\n'.join(md)+'\n');print(json.dumps(rep['summary']),'->',a.out)
if __name__=='__main__':main()
