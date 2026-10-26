"""Build compact book index from isidore.co Calibre metadata.db -> site/data/books.js + books.json"""
import sqlite3,json,re,unicodedata,urllib.parse
from collections import Counter,defaultdict
c=sqlite3.connect('metadata.db')
hub=json.load(open('../site/data/catholic-hub.json'))
def norm(s): return ''.join(ch for ch in unicodedata.normalize('NFKD',s) if not unicodedata.combining(ch)).lower()
# --- site author <-> isidore folder map
fold2site={}
for a in hub['authors']:
    if a.get('isidoreFolder'):fold2site[a['isidoreFolder']]=a['id']  # v18: folder name kept as data, no longer a link
    for l in a['links']:
        if 'isidore.co/CalibreLibrary/' in l['url']:
            f=urllib.parse.unquote(l['url'].split('/CalibreLibrary/')[1].rstrip('/'))
            fold2site[f]=a['id']
books=c.execute('select id,title,path,pubdate,series_index,timestamp from books').fetchall()
BA=defaultdict(list)
for b,a in c.execute('select book,author from books_authors_link order by id'): BA[b].append(a)
AN=dict(c.execute('select id,name from authors'))
BT=defaultdict(list)
for b,t in c.execute('select book,tag from books_tags_link'): BT[b].append(t)
TN=dict(c.execute('select id,name from tags'))
tagfreq=Counter(t for L in BT.values() for t in L)
BS=dict(c.execute('select book,series from books_series_link'))
SN=dict(c.execute('select id,name from series'))
BL=defaultdict(list)
for b,l in c.execute('select book,lang_code from books_languages_link order by item_order'): BL[b].append(l)
LN=dict(c.execute('select id,lang_code from languages'))
BP=dict(c.execute('select book,publisher from books_publishers_link'))
PN=dict(c.execute('select id,name from publishers'))
FM=defaultdict(list)
for b,f,n in c.execute('select book,format,name from data'): FM[b].append((f,n))
ORDER=['PDF','EPUB','PDF_OCR','DJVU','MOBI','AZW3','TXT','DOCX','DOC','MP3','ZIP','PDF_ORIGINAL']
# folder -> site author: the first path segment is the folder of the book's first author
auth_site={}  # calibre author id -> site id
for bid,title,path,*_ in books:
    f=path.split('/')[0]
    if f in fold2site and BA[bid]: auth_site.setdefault(BA[bid][0],fold2site[f])
# second pass: name match (Surname| Forename -> Forename Surname, honorifics stripped) + aliases
HON=r'\b(st|saint|pope|bl|blessed|cdl|card|cardinal|abp|bp|fr|rev|msgr|dr|sr|mother|dom|ven|o\.?p|s\.?j|o\.?s\.?b|o\.?f\.?m|cap|c\.?ss\.?r|d\.?d|ph\.?d)\b\.?'
def nkey(n):
    n=norm(re.sub(r'\(.*?\)','',n)); n=re.sub(r'\d{3,4}\s*-\s*\d{0,4}','',n); n=re.sub(HON,' ',n); return ' '.join(re.findall(r'[a-z]+',n))
SK={}
for a in hub['authors']: SK.setdefault(nkey(a['name']),a['id'])
ALIAS={'Benedict XVI':'joseph-ratzinger'}
SITE_IDS={a['id'] for a in hub['authors']}
for aid,name in AN.items():
    if aid in auth_site: continue
    if name in ALIAS and ALIAS[name] in SITE_IDS: auth_site[aid]=ALIAS[name]; continue
    p=[x.strip() for x in name.split('|')]
    for k in [nkey(name)]+([nkey(p[1]+' '+p[0])] if len(p)>=2 else []):
        if len(k)>3 and k in SK: auth_site[aid]=SK[k]; break
# v5: confident date matching. A catalog name with life dates (b-d) maps to a curated author with the same birth AND death
# years who also shares a name token of 4+ letters. Ambiguous hits (two curated authors) are skipped.
def yrs(n):
    m=re.search(r'(\d{3,4})\s*-\s*(?:approximately\s*|ca\.\s*|c\.\s*)?(\d{3,4})',n)
    return (int(m.group(1)),int(m.group(2))) if m else None
CUR=[]
for a in hub['authors']:
    if a.get('born') and a.get('died'): CUR.append((a['born'],a['died'],set(t for t in re.findall(r'[a-z]{4,}',norm(a['name'])) if t not in ('saint','pope','bishop','blessed','father','mother','abbot')),a['id']))
DATE_MATCH=[]
for aid,name in AN.items():
    if aid in auth_site: continue
    y=yrs(name)
    if not y: continue
    toks=set(re.findall(r'[a-z]{4,}',norm(name)))
    hits=[c for c in CUR if c[0]==y[0] and c[1]==y[1] and (c[2]&toks)]
    if len(hits)==1: auth_site[aid]=hits[0][3]; DATE_MATCH.append((name,hits[0][3]))
print('date matches',len(DATE_MATCH)); open('date_matches.txt','w').write('\n'.join(f'{n}\t{i}' for n,i in DATE_MATCH))
# v5: surname + forename matching. "Surname| Forename ..." must equal the curated author's last and first name tokens,
# with no conflicting life dates and exactly one curated candidate. Plus hand-verified aliases.
HONW={'st','saint','pope','bl','blessed','cardinal','fr','rev','msgr','dr','sr','mother','dom','ven','bishop','abp','bp','father','brother','sister','jr'}
def ntoks(s): return [t for t in re.findall(r"[a-z]+",norm(re.sub(r'\(.*?\)','',s))) if t not in HONW and len(t)>1]
CK={}
for a in hub['authors']:
    t=ntoks(a['name'])
    if len(t)>=2: CK.setdefault((t[-1],t[0]),[]).append(a)
ALIAS2={'Billuart| Carolus Renatus| O.P.':'charles-billuart'}
NAME_MATCH=[]
for aid,name in AN.items():
    if aid in auth_site: continue
    if name in ALIAS2 and ALIAS2[name] in SITE_IDS: auth_site[aid]=ALIAS2[name]; NAME_MATCH.append((name,ALIAS2[name])); continue
    p=[x.strip() for x in name.split('|')]
    if len(p)<2: continue
    sur=ntoks(p[0]); giv=ntoks(p[1])
    if len(sur)!=1 or not giv: continue
    c=CK.get((sur[0],giv[0]),[])
    if len(c)!=1: continue
    y=yrs(name); a=c[0]
    if y and (a.get('born') and abs(a['born']-y[0])>2 or a.get('died') and abs(a['died']-y[1])>2): continue
    bo=re.search(r'\b(\d{4})\s*-\s*$',name)
    if bo and a.get('born') and abs(a['born']-int(bo.group(1)))>2: continue
    full=lambda x:[t for t in re.findall(r"[a-z]+",norm(re.sub(r'\(.*?\)','',x))) if t not in HONW]
    if not set(full(a['name']))<=set(full(name)): continue
    if re.search(r'\b(a\.m|m\.a|ph\.d)\b',norm(name)) and re.search(r'\b[a-z]\.',norm(a['name'])): continue
    auth_site[aid]=a['id']; NAME_MATCH.append((name,a['id']))
print('name matches',len(NAME_MATCH)); open('name_matches.txt','w').write('\n'.join(f'{n}\t{i}' for n,i in NAME_MATCH))
# v5: canonical languages (raw multi-code strings -> deduped canonical codes)
LCANON={'enq':'eng','nob':'nor','frm':'fro','och':'zho'}
# v5: author era (curated page era, else from life dates in the catalog name)
ERA_OF={a['id']:a['era'] for a in hub['authors']}
EORD=[e['id'] for e in hub['eras']]
def era_from_year(fl):
    for lim,e in [(160,'apostolic'),(325,'ante-nicene'),(500,'post-nicene'),(1050,'early-medieval'),(1300,'scholastic'),(1500,'late-medieval'),(1650,'counter-reformation'),(1800,'early-modern'),(1900,'19th-century'),(2000,'20th-century')]:
        if fl<lim: return e
    return 'contemporary'
def name_fl(n):
    y=yrs(n)
    if y: return y[1]-15 if y[1]-y[0]>=40 else y[0]+(y[1]-y[0])//2+5
    m=re.search(r'(?:-|✝\s*(?:c\.\s*)?)(\d{3,4})\b',n)
    if m: return int(m.group(1))-15
    m=re.search(r'\bfl\.?\s*(\d{3,4})',n)
    if m: return int(m.group(1))
    m=re.search(r'\b(\d{4})\s*-\s*$',n.strip())
    if m: return int(m.group(1))+40
    return None
# tables
alist=[];aidx={}
def ai(a):
    if a not in aidx: aidx[a]=len(alist); alist.append([AN[a].replace('|',','),auth_site.get(a,'')])
    return aidx[a]
tlist=[];tidx={}
def ti(t):
    if t not in tidx: tidx[t]=len(tlist); tlist.append(TN[t])
    return tidx[t]
slist=[];sidx={}
def si(s):
    if s not in sidx: sidx[s]=len(slist); slist.append(SN[s])
    return sidx[s]
plist=[];pidx={}
def pi(p):
    if p not in pidx: pidx[p]=len(plist); plist.append(PN[p])
    return pidx[p]
flist=[];fidx={}
def fi(f):
    if f not in fidx: fidx[f]=len(flist); flist.append(f)
    return fidx[f]
def pred_sub(t,bid):
    t=re.sub(r'[\u0300-\u036f]','',unicodedata.normalize('NFD',t))
    t=re.sub(r'[\\/:*?"<>|]','_',t)
    return t[:95].strip()+f' ({bid})'
def book_era(bid):
    es=[ERA_OF[auth_site[a]] for a in BA[bid] if a in auth_site]
    if es: return min(EORD.index(e) for e in es)
    fls=[f for f in (name_fl(AN[a]) for a in BA[bid]) if f]
    if fls: return EORD.index(era_from_year(min(fls)))+100   # +100 = inferred from catalog life dates
    return -1
out=[];stats=Counter()
for bid,title,path,pub,sidx_,ts in sorted(books,key=lambda r:norm(re.sub(r'^(the|a|an|le|la|les|il|de|der|die|das)\s+','',re.sub(r'^[^0-9A-Za-zÀ-ÿ]+','',r[1]),flags=re.I))):
    y=None
    try:
        y=int(pub[:4])
        if y<=101: y=None
    except: pass
    tags=sorted(BT[bid],key=lambda t:-tagfreq[t])[:6]
    fm=sorted(FM[bid],key=lambda x:ORDER.index(x[0]) if x[0] in ORDER else 99)
    folder,sub=path.split('/',1)
    sub_d = '' if sub==pred_sub(title,bid) else sub   # store only when not predictable (JS mirrors pred_sub)
    names=set(n for _,n in fm)
    fname = fm[0][1] if fm else ''
    rec=[bid,title,[ai(a) for a in BA[bid]],y or 0,[ti(t) for t in tags],si(BS[bid]) if bid in BS else -1,
         (sidx_ if bid in BS else 0),'|'.join(f for f,_ in fm),fi(folder),sub_d,
         ','.join(dict.fromkeys(LCANON.get(LN[l],LN[l]) for l in BL[bid])),pi(BP[bid]) if bid in BP else -1,book_era(bid)]
    stats['sub_pred']+= sub_d==''
    out.append(rec)
# compress: drop float series index .0
for r in out:
    if isinstance(r[6],float) and r[6].is_integer(): r[6]=int(r[6])
data=dict(v=2,count=len(out),fields=['id','title','authors','year','tags','series','seriesIndex','formats','folder','sub','lang','publisher','era (index into eras; +100 = inferred from catalog life dates; -1 unknown)'],eras=EORD,
          authors=alist,tags=tlist,series=slist,publishers=plist,folders=flist,books=out,
          base='https://isidore.co/CalibreLibrary/',server='https://isidore.co/calibre/')
js=json.dumps(data,ensure_ascii=False,separators=(',',':'))
open('../site/data/books.json','w').write(js)
open('../site/data/books.js','w').write('window.BOOKS_DATA='+js+';')
print('books',len(out),'authors',len(alist),'linked to site authors',sum(1 for a in alist if a[1]),'books w/ site author',sum(1 for r in out if any(alist[i][1] for i in r[2])),
      'tags',len(tlist),'series',len(slist),'folders',len(flist),'bytes',len(js.encode()),stats)
