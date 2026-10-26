#!/usr/bin/env python3
"""Fetch the author and license of every author portrait from its file page (v18).

Author portraits are hotlinked from Wikimedia (Commons, and a few English Wikipedia local files).
Each file carries its own license, so this tool asks the MediaWiki API (`prop=imageinfo`,
`iiprop=extmetadata`) of the wiki that hosts the file for its Artist, LicenseShortName, and LicenseUrl,
and writes:

  data/portrait-credits.json   snapshot: {checked, source, files:{author_id:{...}}}
  data/catholic-hub.json + data/data.js   `imgCredit` on each author (through tools/hubio.py)

Nothing is invented: a portrait whose file page gives no author, no license, or a non-free license
(fair use) gets no `imgCredit`, and app.js then shows the author's initial instead of the image.
Author pages show each credited portrait with its credit line; list thumbnails (cards, mini panels)
show only portraits that need no attribution (`pd`: public domain, CC0, or no restrictions).
Credit names are tidied by `artist_name()` (v18.1): Commons often repeats a phrase ("Unknown author Unknown author")
or says "not specified"; those become "Author unknown", doubled phrases are collapsed, and "[réf. nécessaire]"-style
citation markers are dropped. The snapshot keeps the file page's raw `artist` and the shown `credit` name.
Network required.  Run:  python3 tools/fetch_portrait_credits.py
Offline (re-apply the snapshot, for example after changing artist_name()):  python3 tools/fetch_portrait_credits.py --apply
"""
import datetime,html,json,re,sys,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'));import hubio
UA='BibliothecaCatholica/1.0 (https://bibliothecacatholica.com; portrait credits)'
API={'commons':'https://commons.wikimedia.org/w/api.php','en':'https://en.wikipedia.org/w/api.php'}
PAGE={'commons':'https://commons.wikimedia.org/wiki/File:','en':'https://en.wikipedia.org/wiki/File:'}
def parse(u):
    """(wiki, file name) from a thumb.wikimedia.org or upload.wikimedia.org URL."""
    p=urllib.parse.urlparse(u).path.split('/')
    wiki='commons' if p[2]=='commons' else 'en' if p[2]=='en' else None
    name=p[p.index('thumb')+3] if 'thumb' in p else p[-1]
    return wiki,urllib.parse.unquote(name)
def text(v):
    v=re.sub(r'<[^>]+>',' ',v or '');v=html.unescape(v);return re.sub(r'\s+',' ',v).strip()
def query(wiki,names):
    q=urllib.parse.urlencode({'action':'query','format':'json','formatversion':2,'prop':'imageinfo','iiprop':'extmetadata',
        'iiextmetadatafilter':'Artist|LicenseShortName|LicenseUrl|NonFree|Copyrighted|UsageTerms|AttributionRequired','titles':'|'.join('File:'+n for n in names)})
    req=urllib.request.Request(API[wiki]+'?'+q,headers={'User-Agent':UA})
    for i in range(4):
        try:
            with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
        except Exception as e:
            if i==3:raise
            time.sleep(3*(i+1))
NOATTR=re.compile(r'^(public domain|pd\b|pd-|cc0|no restrictions)',re.I)
FREE=re.compile(r'^(public domain|pd\b|pd-|cc0|cc[- ]by|cc by|attribution|gfdl|no restrictions|copyrighted free use|fal\b|free art)',re.I)
UNKNOWN=re.compile(r'^(?:(?:unknown|anonymous|anon\.?|not specified|unknown (?:author|artist|photographer|autor|painter|engraver))[\s,;.]*)+(?:no author disclosure)?\W*$',re.I)
def artist_name(raw):
    """The credit name shown on the site, from the file page's Artist text. Never invents a name."""
    a=re.sub(r'\s*\[[^\]]{0,40}\]','',raw or '').strip()
    a=re.sub(r'\b(\w[\w.\'’-]*(?: \w[\w.\'’-]*){0,4})(?: \1\b)+',r'\1',a,flags=re.I)  # "Unknown author Unknown author"
    if re.search(r'not specified',a,re.I):a=re.sub(r'(?:^|(?<=[.;,]))\s*[^.;,]*\bnot specified\b[^.;,]*[.;,]?','',a,flags=re.I).strip(' .;,')  # drop "Photographer not specified."
    a=re.sub(r'\s+\.$','',a)  # Commons' stray " ." after a linked name
    a=re.sub(r'\s*\((?:re-?edited|cropped|retouched)[^)]*\)','',a,flags=re.I).strip()
    if not a or UNKNOWN.match(a):return 'Author unknown'
    if re.match(r'unknown\b',a):a='U'+a[1:]
    return a if len(a)<=200 else a[:199].rsplit(' ',1)[0]+'…'
def apply(h,files):
    """Set imgCredit on hub authors from the snapshot's file records."""
    credited=0
    for a in h['authors']:
        a.pop('imgCredit',None);rec=files.get(a['id'])
        if not a.get('img') or not rec:continue
        ok=not rec['missing'] and not rec['nonFree'] and rec['license'] and FREE.search(rec['license']) and (rec['artist'] or NOATTR.search(rec['license']))
        rec['shown']=bool(ok);rec.pop('credit',None)
        if not ok:continue
        credited+=1
        a['imgCredit']={'page':rec['page'],'license':rec['license']}
        if rec['artist']:a['imgCredit']['artist']=rec['credit']=artist_name(rec['artist'])
        if rec['licenseUrl']:a['imgCredit']['licenseUrl']=rec['licenseUrl']
        if NOATTR.search(rec['license']):a['imgCredit']['pd']=1  # no attribution required: may also appear as a small list thumbnail
    return credited
def main():
    if '--apply' in sys.argv:
        h=hubio.load();snap=json.loads((ROOT/'data/portrait-credits.json').read_text());credited=apply(h,snap['files'])
        (ROOT/'data/portrait-credits.json').write_text(json.dumps(snap,ensure_ascii=False,indent=1)+'\n');hubio.save(h)
        print(len(snap['files']),'portraits;',credited,'credited and shown;',len(snap['files'])-credited,'hidden');return
    h=hubio.load();want={}
    for a in h['authors']:
        if a.get('img'):
            w,n=parse(a['img']);want.setdefault((w,n),[]).append(a['id'])
    meta={}
    for wiki in ('commons','en'):
        names=sorted(n for w,n in want if w==wiki)
        for i in range(0,len(names),40):
            d=query(wiki,names[i:i+40])
            norm={x['to']:x['from'] for x in d['query'].get('normalized',[])}
            for p in d['query']['pages']:
                title=p['title'];orig=norm.get(title,title)[5:]
                ii=(p.get('imageinfo') or [{}])[0].get('extmetadata') or {}
                g=lambda k:(ii.get(k) or {}).get('value','')
                meta[(wiki,orig)]={'title':title,'artist':text(g('Artist')),'license':text(g('LicenseShortName')),'licenseUrl':g('LicenseUrl'),
                                    'nonFree':str(g('NonFree')).lower() in ('true','1'),'missing':'missing' in p or not ii}
            time.sleep(1)
    files={}
    for a in h['authors']:
        if not a.get('img'):continue
        w,n=parse(a['img']);m=meta.get((w,n)) or {'missing':True}
        files[a['id']]={'wiki':w,'file':n,'page':PAGE[w]+urllib.parse.quote(n.replace(' ','_')),'artist':m.get('artist',''),'license':m.get('license',''),'licenseUrl':m.get('licenseUrl',''),'nonFree':m.get('nonFree',False),'missing':m.get('missing',False)}
    # free license required; an author name is required too unless the file is public domain or CC0
    credited=apply(h,files)
    out={'checked':str(datetime.date.today()),'source':'MediaWiki API imageinfo extmetadata of each file page (commons.wikimedia.org or en.wikipedia.org)',
         'rule':'shown only when the file page gives a free license and, unless public domain or CC0, names an author; otherwise the portrait is hidden','files':files}
    (ROOT/'data/portrait-credits.json').write_text(json.dumps(out,ensure_ascii=False,indent=1)+'\n')
    hubio.save(h)
    print(len(files),'portraits;',credited,'credited and shown;',len(files)-credited,'hidden')
if __name__=='__main__':main()
