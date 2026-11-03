"""Check the official-site, talk, and podcast links that tools/author_pages.py may show (hub `links` of kind `site`
and data/authorx.js `own`).  Prints each URL's HTTP status after redirects; copy the 200s, with today's date, into
author_pages.CHECKED.  Needs the network and curl; not part of the build or CI."""
import json,subprocess,sys,concurrent.futures as cf
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import hubio
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def main():
    hub=hubio.load();s=(ROOT/'data/authorx.js').read_text();X=json.loads(s[s.index('=')+1:].rstrip().rstrip(';'))['by']
    urls=sorted({l['url'] for a in hub['authors'] for l in a.get('links') or [] if l.get('kind')=='site'}|{o['u'] for x in X.values() for o in x.get('own') or []})
    def chk(u):
        r=subprocess.run(['curl','-s','-o','/dev/null','-w','%{http_code}','-L','--max-time','25','-A',UA,'-H','Accept: text/html,application/xhtml+xml',u],capture_output=True,text=True)
        return u,r.stdout or 'ERR'
    with cf.ThreadPoolExecutor(12) as ex:
        for u,c in ex.map(chk,urls):print(c,u)
if __name__=='__main__':main()
