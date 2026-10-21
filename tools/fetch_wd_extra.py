"""v6: For each curated author with a verified QID, read from Wikidata (no guessing):
P3241 Catholic Encyclopedia ID, P3123 Stanford Encyclopedia of Philosophy ID, P5088 Internet Encyclopedia of Philosophy ID,
P841 feast day (labels), P611 religious order, P1066/P802 student of/student, P737 influenced by (kept only when the target is another curated author), enwikisource / enwikiquote sitelinks."""
import json,urllib.parse,urllib.request,time
UA={'User-Agent':'BibliothecaCatholica/1.0 (https://bibliothecacatholica.com)'}
def get(url):
    for i in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60))
        except Exception as e: time.sleep(2+i*3)
    raise SystemExit('fetch failed '+url)
A=json.load(open('authors_raw.json'))
byq={a['qid']:a for a in A if a.get('qid')}
Q=list(byq);out={};feastq=set()
def vals(e,p):
    r=[]
    for c in e.get('claims',{}).get(p,[]):
        if c.get('rank')=='deprecated':continue
        v=c['mainsnak'].get('datavalue',{}).get('value')
        if v is None:continue
        r.append(v['id'] if isinstance(v,dict) and 'id' in v else v)
    return r
for i in range(0,len(Q),50):
    d=get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks|claims&sitefilter=enwikisource|enwikiquote&ids='+'|'.join(Q[i:i+50]))
    for q,e in d['entities'].items():
        sl=e.get('sitelinks',{})
        o=dict(ce=vals(e,'P3241'),sep=vals(e,'P3123'),iep=vals(e,'P5088'),feast=vals(e,'P841'),infl=[x for x in vals(e,'P737') if x in byq],order=vals(e,'P611'),stof=[x for x in vals(e,'P1066') if x in byq],stu=[x for x in vals(e,'P802') if x in byq],
               ws=sl.get('enwikisource',{}).get('title'),wq=sl.get('enwikiquote',{}).get('title'))
        feastq.update(o['feast']);feastq.update(o['order']);out[byq[q]['id'] if 'id' in byq[q] else q]=o;out[q]=o
FL={}
F=list(feastq)
for i in range(0,len(F),50):
    d=get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&languages=en&ids='+'|'.join(F[i:i+50]))
    for q,e in d['entities'].items(): FL[q]=e.get('labels',{}).get('en',{}).get('value')
res={q:dict(o,feast=[FL.get(x) for x in o['feast'] if FL.get(x)],order=[[x,FL.get(x)] for x in o['order'] if FL.get(x)]) for q,o in out.items() if q.startswith('Q')}
json.dump(res,open('wd_extra.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
print(len(res),{k:sum(1 for o in res.values() if o[k]) for k in ['ce','sep','iep','feast','infl','order','stof','stu','ws','wq']})
print(Counter(f for o in res.values() for f in o['feast']).most_common(15))
