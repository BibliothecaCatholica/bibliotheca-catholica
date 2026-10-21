"""Fetch Wikidata QIDs for curated authors via each author's own English Wikipedia article (pageprops.wikibase_item),
then confirm on Wikidata that the item's enwiki sitelink is that same article. No guessing: no article -> no QID."""
import json,urllib.parse,urllib.request,time
UA={'User-Agent':'BibliothecaCatholica/1.0 (https://bibliothecacatholica.com)'}
def get(url):
    for i in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40))
        except Exception as e: time.sleep(2+i*3)
    raise SystemExit('fetch failed '+url)
A=json.load(open('authors_raw.json'))
titles={}
for a in A:
    u=a.get('wikiUrl') or ''
    if '/wiki/' in u and 'en.wikipedia.org' in u: titles[a['name']]=urllib.parse.unquote(u.split('/wiki/',1)[1]).replace('_',' ')
T=list(set(titles.values()));res={}
for i in range(0,len(T),50):
    ch=T[i:i+50]
    d=get('https://en.wikipedia.org/w/api.php?action=query&format=json&redirects=1&prop=pageprops&ppprop=wikibase_item&titles='+urllib.parse.quote('|'.join(ch)))
    q=d['query'];norm={x['from']:x['to'] for x in q.get('normalized',[])};red={x['from']:x['to'] for x in q.get('redirects',[])}
    byt={p['title']:p.get('pageprops',{}).get('wikibase_item') for p in q['pages'].values() if 'missing' not in p}
    for t in ch:
        t2=norm.get(t,t);t3=red.get(t2,t2);res[t]=(byt.get(t3),t3)
# confirm on Wikidata
Q=[v[0] for v in res.values() if v[0]];conf={}
for i in range(0,len(Q),50):
    d=get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks|claims&sitefilter=enwiki&ids='+'|'.join(Q[i:i+50]))
    for qid,e in d['entities'].items():
        sl=e.get('sitelinks',{}).get('enwiki',{}).get('title')
        p31=[c['mainsnak'].get('datavalue',{}).get('value',{}).get('id') for c in e.get('claims',{}).get('P31',[])]
        conf[qid]=(sl,p31)
n=0;out={}
for a in A:
    a.pop('qid',None)
    t=titles.get(a['name'])
    if not t: continue
    qid,final=res.get(t,(None,None))
    if qid and conf.get(qid,(None,))[0]==final:
        a['qid']=qid;n+=1;out[a['name']]=dict(qid=qid,enwiki=final,human='Q5' in conf[qid][1])
json.dump(A,open('authors_raw.json','w'),ensure_ascii=False,indent=1)
json.dump(out,open('qids.json','w'),ensure_ascii=False,indent=1)
print('authors',len(A),'with enwiki',len(titles),'qids verified',n,'non-human items',[k for k,v in out.items() if not v['human']])
