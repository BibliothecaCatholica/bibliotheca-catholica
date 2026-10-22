"""Inventory the whole catalog and check curated reading destinations.
Network checks establish reachability and page identity, not permission or a
human review of every text. Imported Isidore rows receive structural checks;
the tool does not request thousands of third-party download files.
"""
import argparse,collections,concurrent.futures,datetime,html,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def jsdata(name):
    return json.loads((ROOT/'data'/name).read_text().split('=',1)[1].strip().rstrip(';'))
def inventory():
    hub=json.loads((ROOT/'data/catholic-hub.json').read_text());lib=json.loads((ROOT/'data/library.json').read_text());books=json.loads((ROOT/'data/books.json').read_text());guide=jsdata('guide.js')
    urls=collections.defaultdict(list)
    def add(url,label):
        if url:urls[url].append(label)
    for w in lib['works']:
        for e in w['editions']:add(e['source'],'Selected: '+w['title'])
        for a in w.get('readingLinks',[]):add(a['url'],'Access: '+w['title'])
    for a in hub['authors']:
        for w in a.get('works',[]):add(w['url'],a['name']+': '+w['title'])
    for r in hub['resources']:add(r['url'],'Resource: '+r['name'])
    for w in guide['editions']:
        for label,url in w.get('free',[])+w.get('related',[]):add(url,'Guide '+w['t']+': '+label)
    for shelf in guide['lists']:
        for it in shelf['items']:
            for label,url in it.get('free',[]):add(url,'List '+shelf['t']+': '+label)
    # Include reading destinations from every supplemental collection. Source
    # citations and biography/search links remain inventoried separately.
    supplementary={}
    def collect(value,label):
        if isinstance(value,str) and value.startswith(('https://','http://')) and '{' not in value:
            add(value,label)
        elif isinstance(value,dict):
            for key,v in value.items():
                if key not in ['img','image','src','gh','m']:collect(v,label)
        elif isinstance(value,list):
            for v in value:collect(v,label)
    for name in ['doctors.js','rare.js','projects.js']:
        data=jsdata(name);before=len(urls);collect(data,name)
        supplementary[name]=len(urls)-before
    for author in hub['authors']:
        for entry in author.get('links',[]):
            if entry.get('kind')=='read':add(entry['url'],'Author reading: '+author['name'])
    problems=[];ids=set()
    for r in books['books']:
        if len(r)!=13:problems.append({'book':r[0],'issue':'Expected 13 fields'});continue
        if r[0] in ids:problems.append({'book':r[0],'issue':'Duplicate ID'})
        ids.add(r[0])
        for field,key in [(2,'authors'),(4,'tags')]:
            for idx in r[field]:
                if not isinstance(idx,int) or not 0<=idx<len(books[key]):problems.append({'book':r[0],'issue':'Invalid '+key+' index'})
        for field,key in [(5,'series'),(8,'folders'),(11,'publishers')]:
            idx=r[field]
            if idx!=-1 and (not isinstance(idx,int) or not 0<=idx<len(books[key])):problems.append({'book':r[0],'issue':'Invalid '+key+' index'})
    summary={'selectedWorks':len(lib['works']),'hostedWorks':sum(any(e.get('text') for e in w['editions']) for w in lib['works']),'referenceOnlyWorks':[w['id'] for w in lib['works'] if all(e['access']=='reference' for e in w['editions'])],'missingDescriptions':[w['id'] for w in lib['works'] if not w.get('description')],'editionGuides':len(guide['editions']),'readingPaths':len(guide['lists']),'readingListEntries':sum(len(s['items']) for s in guide['lists']),'authorWorkLinks':sum(len(a.get('works',[])) for a in hub['authors']),'curatedResources':len(hub['resources']),'importedBooks':len(books['books']),'importedFolders':len(hub['isidore']),'importedWithoutFiles':[r[0] for r in books['books'] if not r[7]],'importedStructureProblems':problems,'uniqueCuratedUrls':len(urls),'supplementalCollections':supplementary,'authorProfiles':len(hub['authors']),'importedAuthorLinksToMissingProfiles':[a[1] for a in books['authors'] if a[1] and a[1] not in {x['id'] for x in hub['authors']}],'authorReadingLinks':sum(sum(e.get('kind')=='read' for e in a.get('links',[])) for a in hub['authors'])}
    return summary,urls

def check(pair):
    url,labels=pair;out={'url':url,'usedBy':labels,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'BibliothecaCatholica-collection-audit/1.0'})
        with urllib.request.urlopen(req,timeout=15) as r:
            data=r.read(1000000);s=data.decode('utf-8',errors='replace')
            title=re.search(r'<title\b[^>]*>(.*?)</title>',s,re.S|re.I)
            h1=re.search(r'<h1\b[^>]*>(.*?)</h1>',s,re.S|re.I)
            clean=lambda x:html.unescape(re.sub('<[^>]*>','',x or '')).strip()
            out.update(status=r.status,finalUrl=r.url,title=clean(title.group(1)) if title else '',heading=clean(h1.group(1)) if h1 else '')
            if r.url.rstrip('/')!=url.rstrip('/'):out['redirected']=True
            if re.search(r'page not found|404 not found|access denied|just a moment|verify you are human|site unavailable',out['title'],re.I):out['needsReview']=True
    except Exception as e:out['error']=str(e)
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--network',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--output',default='docs/collection-audit.json');args=parser.parse_args()
    summary,urls=inventory();report={'checked':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All selected works, edition guides, reading-list entries, author work links, curated resources, and imported book metadata. Network checks cover curated destinations, not imported download files.','summary':summary}
    if args.network:
        cached={}
        previous=ROOT/args.output
        if args.resume and previous.exists():
            prior=json.loads(previous.read_text())
            cached={r['url']:dict(r,checkedAt=r.get('checkedAt',prior['checked'])) for r in prior.get('links',[])}
            for key in ['editorialFindings','retiredDestinationChecks','limits']:
                if key in prior:report[key]=prior[key]
        # Spread requests across hosts instead of sending the entire Fathers
        # collection to one server at once.
        buckets=collections.defaultdict(list)
        from urllib.parse import urlparse
        for item in sorted(urls.items()):
            if item[0] in cached:continue
            buckets[urlparse(item[0]).netloc].append(item)
        jobs=[]
        while any(buckets.values()):
            for values in buckets.values():
                if values:jobs.append(values.pop())
        print('Checking',len(jobs),'new destinations;',len(cached),'prior checks retained.',flush=True)
        results=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for row in pool.map(check,jobs):
                results.append(row)
                if len(results)%50==0:
                    print('Completed',len(results),'/',len(jobs),flush=True)
                    checkpoint=dict(report,complete=False,links=results+[dict(cached[u],usedBy=labels) for u,labels in urls.items() if u in cached])
                    (ROOT/args.output).write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n')
        results.extend(dict(cached[u],usedBy=labels) for u,labels in urls.items() if u in cached)
        report['complete']=True
        report['links']=results
        report['linkSummary']={'checked':len(report['links']),'reachable':sum('error' not in r for r in report['links']),'requestFailures':sum('error' in r for r in report['links']),'reviewFlags':sum(r.get('needsReview',False) for r in report['links'])}
    (ROOT/args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False));print(report.get('linkSummary',{}))
if __name__=='__main__':main()
