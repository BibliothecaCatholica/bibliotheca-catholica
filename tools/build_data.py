import json,re,urllib.parse,unicodedata,datetime
exec(open('resources.py').read()); exec(open('extras.py').read())
A=json.load(open('authors_raw.json'))
ERAS=[('apostolic','Apostolic Fathers','c. 50–160'),('ante-nicene','Ante-Nicene Fathers','160–325'),('post-nicene','Nicene & Post-Nicene Fathers','325–500'),('desert','Desert Fathers & Mothers','250–650'),('early-medieval','Early Middle Ages','500–1050'),('scholastic','High Middle Ages & Scholastics','1050–1300'),('late-medieval','Late Medieval Mystics','1300–1500'),('counter-reformation','Reformation & Counter-Reformation','1500–1650'),('early-modern','Early Modern','1650–1800'),('19th-century','Nineteenth Century','1800–1900'),('20th-century','Twentieth Century','1900–2000'),('contemporary','Contemporary','2000–today')]
STOP={'of','the','de','von','st','saint','pope','la','le','du','van','der','da','y','fr','dr','bl','bishop','cardinal','i','ii','a','great','author','mother','dom','ignatius','press','founder'}
def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c)).lower()
def slug(s): return re.sub(r'[^a-z0-9]+','-',norm(s)).strip('-')
out=[]
for a in A:
    nm=re.sub(r'\(.*?\)','',a['name']).strip()
    links=[]
    na=a.get('newadvent')
    if na:
        links.append(dict(label='Works at New Advent (Fathers)',url='https://www.newadvent.org/fathers/',kind='read'))
        links.append(dict(label='Catholic Encyclopedia article',url=na['cathen'],kind='about'))
    if a.get('isidore'): links.append(dict(label='Books in the isidore.co library',url=a['isidore'],kind='read'))
    if a.get('ccel'): links.append(dict(label='Works at CCEL',url=a['ccel'],kind='read'))
    if a.get('gutenberg'): links.append(dict(label='Free e-books at Project Gutenberg',url=a['gutenberg'],kind='read'))
    for l,u in EX.get(a['name'],[]): links.append(dict(label=l,url=u,kind='read' if 'vatican' in u or 'Works' in l or 'works' in l else 'site'))
    q=nm.replace('Bishop ','').replace('Fr. ','').replace('Dr. ','')
    links.append(dict(label='Search the Internet Archive',url='https://archive.org/search?query='+urllib.parse.quote('"'+q+'"'),kind='search'))
    toks=[t for t in re.split(r'[\s\.]+',q) if t and norm(t) not in STOP]
    key=(toks[-1] if toks else q) if ' of ' not in q else q.split(' of ')[0]
    links.append(dict(label='Search the isidore.co catalog',url='https://isidore.co/calibre/mobile?search='+urllib.parse.quote(key)+'&num=25',kind='search'))
    if a.get('wikiUrl'): links.append(dict(label='Wikipedia',url=a['wikiUrl'],kind='about'))
    try: b=int(a['born'])
    except: b=None
    try: d=int(a['died'])
    except: d=None
    fl=(d-15) if d else ((b+40) if b else None)
    if d and b and d-b<40: fl=b+(d-b)//2+5
    out.append(dict(id=slug(nm),name=a['name'],born=b,died=d,century=(fl//100+1) if fl else None,era=a['era'],tags=a['tags'],desc=a['desc'],wikiDesc=a.get('wikiDesc',''),extract=a.get('extract',''),img=a.get('img'),dshow=a.get('dshow'),qid=a.get('qid'),qidWork=a.get('qidWork'),works=[dict(title=t,url=u) for t,u in (na['works'] if na else [])][:40],links=links,doctor='doctor' in a['tags']))
# isidore index
F=[l.strip().rstrip('/') for l in open('isidore_authors.txt',encoding='utf-8') if l.strip().endswith('/') and not l.startswith('/')]
JUNK=[f for f in F if re.match(r'(?i)(https?[:%]|www\.)',f)]
F=[f for f in F if f not in JUNK]
print('isidore junk folders removed:',JUNK)
iso=[dict(n=re.sub(r'_$','.',f).replace('_','.'),u='https://isidore.co/CalibreLibrary/'+urllib.parse.quote(f)+'/') for f in F]
data=dict(generated=str(datetime.date.today()),eras=[dict(id=i,label=l,range=r) for i,l,r in ERAS],authors=out,resources=R,isidore=iso)
json.dump(data,open('../site/data/catholic-hub.json','w'),ensure_ascii=False)
open('../site/data/data.js','w').write('window.HUB_DATA='+json.dumps(data,ensure_ascii=False)+';')
from collections import Counter
print('authors',len(out),'resources',Counter(r['section'] for r in R),'isidore',len(iso))
print('doctors',sum(o['doctor'] for o in out)); print(Counter(o['era'] for o in out))
