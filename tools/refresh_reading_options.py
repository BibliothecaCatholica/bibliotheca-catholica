"""Refresh external EPUB links from source pages; no files are mirrored.
Run manually with network access. Review the JSON diff before committing.
"""
import concurrent.futures
import datetime
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.parse
import urllib.request
ROOT = Path(__file__).resolve().parents[1]
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self, tag, attrs):
        if tag=='a':
            a=dict(attrs)
            if a.get('href'):self.links.append(a)
def discover(source, provider):
    with urllib.request.urlopen(source, timeout=30) as response:
        parser=Links();parser.feed(response.read().decode('utf-8'))
    candidates=[a for a in parser.links if (a.get('type')=='application/epub+zip' or '.epub' in a['href']) and 'advanced' not in a['href'] and '.kepub' not in a['href']]
    candidates.sort(key=lambda a: (0 if 'epub3' in a['href'] else 1, 0 if a['href'].endswith('.epub') else 1))
    if not candidates:raise ValueError('No EPUB found: '+source)
    url=urllib.parse.urljoin(source,candidates[0]['href'])
    # Check the selected file, following redirects; only a small prefix is read.
    with urllib.request.urlopen(url,timeout=30) as response:
        if response.read(2)!=b'PK':
            if provider=='Standard Ebooks':return dict(provider=provider,source=source,url=source,format='EPUB',access='source-page',checked=str(datetime.date.today()))
            raise ValueError('Not an EPUB ZIP: '+url)
        url=response.url
    return dict(provider=provider,source=source,url=url,format='EPUB',checked=str(datetime.date.today()))
def main():
    catalog=json.loads((ROOT/'data/library.json').read_text());jobs=[]
    for w in catalog['works']:
        for e in w['editions']:
            if 'gutenberg.org/ebooks/' in e['source']:jobs.append((w['id'],e['source'],'Project Gutenberg'))
    for wid,slug in [('orthodoxy','orthodoxy'),('everlasting-man','the-everlasting-man'),('innocence-father-brown','the-innocence-of-father-brown'),('man-thursday','the-man-who-was-thursday')]:
        jobs.append((wid,'https://standardebooks.org/ebooks/g-k-chesterton/'+slug,'Standard Ebooks'))
    def fetch(job):
        wid,source,provider=job
        try:return wid,discover(source,provider)
        except Exception as error:print('Skipped',wid,str(error),flush=True);return wid,None
    options={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for wid,item in pool.map(fetch,jobs):
            if item:options.setdefault(wid,[]).append(item)
    data=dict(checked=str(datetime.date.today()),options=options)
    (ROOT/'data/reading-options.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'data/reading-options.js').write_text('window.READING_OPTIONS='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
    print(sum(map(len,options.values())),'verified EPUB options for',len(options),'works')
if __name__=='__main__':main()
