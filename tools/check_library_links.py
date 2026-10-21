"""Check curated source URLs; report redirects and failures without changing catalog data.
Usage: python tools/check_library_links.py [--output /path/report.json]
Uses GET because many archives reject HEAD. A reachable URL is not a bibliographic review.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from html import unescape
ROOT = Path(__file__).resolve().parents[1]
def check(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'BibliothecaCatholica-link-check/1.0'})
        with urllib.request.urlopen(req, timeout=35) as response:
            raw = response.read(4000000)
            html = raw.decode('utf-8', errors='replace')
            title = re.search(r'<title[^>]*>(.*?)</title>', html, re.S|re.I)
            return dict(url=url, status=response.status, finalUrl=response.url, title=unescape(re.sub('<[^>]+>','',title.group(1))).strip() if title else '', sha256=hashlib.sha256(raw).hexdigest())
    except Exception as error:
        return dict(url=url, error=str(error))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
    catalog=json.loads((ROOT/'data/library.json').read_text())
    urls=sorted({e['source'] for w in catalog['works'] for e in w['editions']})
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(check,urls))
    report=dict(checked=datetime.datetime.now(datetime.timezone.utc).isoformat(),results=results)
    if args.output:Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for row in results:print(row.get('status','FAIL'),row['url'],row.get('title',row.get('error','')))
    print(f"{sum('error' not in r for r in results)}/{len(results)} sources reachable. Review titles and redirects manually.")
if __name__=='__main__':main()
