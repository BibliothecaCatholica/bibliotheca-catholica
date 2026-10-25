"""v6: per-author extras for the tabbed author page -> site/data/authorx.js (window.AUTHORX).
Sources: data/wd_extra.json (Wikidata claims, fetched by data/fetch_wd_extra.py), the Isidore Index subject tags,
guide.js (reading lists, Substacks), rare.js, projects.js, and a small hand-curated, link-checked commentary list below."""
import json,re,unicodedata,os
R='/workspace/catholic-repo/'
def js(p):
    s=open(R+'site/data/'+p,encoding='utf-8').read();return json.loads(s[s.index('{'):s.rstrip().rstrip(';').rindex('}')+1])
def N(s): return re.sub(r'[^a-z0-9 ]',' ',unicodedata.normalize('NFD',(s or '').lower()).encode('ascii','ignore').decode()).split()
D=js('data.js');G=js('guide.js');RA=js('rare.js');PJ=js('projects.js');B=json.load(open(R+'site/data/books.json'))
W=json.load(open(R+'data/wd_extra.json'))
A=D['authors'];AID={a['id']:a for a in A};BYQ={a['qid']:a['id'] for a in A if a.get('qid')}
STOP={'saint','pope','the','of','von','de','del','della','van','and','st','der','la','le','du'}
X={}
def x(i): return X.setdefault(i,{})
# ---- Wikidata
FAM=[('Jesuits',r'Society of Jesus'),('Franciscans',r'Franciscan|Friars Minor|Saint Francis|Poor Clares|Capuchin'),('Dominicans',r'Dominic'),
     ('Carmelites',r'Carmel'),('Cistercians and Trappists',r'Cistercian'),('Benedictines',r'Benedictine'),('Augustinians',r'Order of St\. Augustine|^Augustinians'),
     ('Canons Regular',r'Canons? Regular|Canon regulars'),('Oratorians',r'Oratory of Saint Philip'),('Redemptorists',r'Redeemer'),('Carthusians',r'Carthusian'),('Sulpicians',r'Sulpice')]
for q,o in W.items():
    i=BYQ.get(q)
    if not i: continue
    e=x(i)
    if o['ce']: e['ce']='https://www.newadvent.org/cathen/'+o['ce'][0]+'.htm'
    if o['sep']: e['sep']='https://plato.stanford.edu/entries/'+o['sep'][0]+'/'
    if o['iep']: e['iep']='https://iep.utm.edu/'+o['iep'][0]+'/'
    # WS_FIX: Wikidata sitelinks that 404 on Wikisource (verified 2026-10-25)
    WS_FIX={'Portal:William of Ockham':'Author:William of Ockham'}
    if o['ws']: e['ws']='https://en.wikisource.org/wiki/'+WS_FIX.get(o['ws'],o['ws']).replace(' ','_')
    if o['wq']: e['wq']='https://en.wikiquote.org/wiki/'+o['wq'].replace(' ','_')
    f=list(dict.fromkeys(o['feast']))
    if f and ('saint' in AID[i]['tags'] or AID[i]['doctor']): e['feast']=f[:3]
    fam=[]
    for lab in [l for _,l in o['order']]:
        for n,rx in FAM:
            if re.search(rx,lab) and n not in fam: fam.append(n)
    if fam: e['order']=fam
    for k,src in (('infl','infl'),('stof','stof'),('stu','stu')):
        v=[BYQ[z] for z in o[src] if z in BYQ and BYQ[z]!=i]
        if v: e[k]=list(dict.fromkeys(v))
# reverse influence
for i,e in list(X.items()):
    for j in e.get('infl',[]): x(j).setdefault('inflOn',[]).append(i)
# existing CE links in the curated data
for a in A:
    for l in a['links']:
        if 'newadvent.org/cathen/' in l['url'] and 'ce' not in X.get(a['id'],{}): x(a['id'])['ce']=l['url']
# ---- curated commentary (link-checked 2026-10-21); k: column|substack|podcast|video|society|study
S={s['name']:s for s in G['substacks']}
def ss(n,why): s=S[n];return dict(k='substack',t=s['name']+' ('+s['author']+')',u=s['url'],n=why)
F=G['featured']
WOF=dict(k='podcast',t='Way of the Fathers (Catholic Culture podcast)',u='https://www.catholicculture.org/commentary/category/way-fathers/',n='A podcast on the Fathers and Doctors of the Church, hosted by Jim Papandrea (earlier seasons by Mike Aquilina).')
COMM={
 'g-k-chesterton':[dict(k='column',t=F['author']+': Chesterton commentary column',u=F['url'],n='Our featured Chesterton column, coming soon on Substack, with essays in a Chestertonian key in the meantime.',feat=1),
   dict(k='society',t='Society of G. K. Chesterton',u='https://www.chesterton.org/',n='Lectures, the Gilbert magazine, and study guides to Chesterton.')],
 'thomas-aquinas':[dict(k='podcast',t='The Thomistic Institute podcast',u='https://podcast.thomisticinstitute.org/',n='Lectures on Aquinas and Thomism by leading scholars.'),
   dict(k='video',t='The Thomistic Institute on YouTube',u='https://www.youtube.com/@ThomisticInstitute',n='Lectures in philosophy and theology.'),
   ss('Investigations','Essays from the Dominican Thomistic Institute.'),
   dict(k='podcast',t='Pints with Aquinas (Matt Fradd)',u='https://www.dailywire.com/show/pints-with-aquinas',n='Interviews and debates that began as a show about the Summa.')],
 'j-r-r-tolkien':[ss('The Tolkien Road','A long-running podcast and newsletter reading through the legendarium.'),ss('Holly Ordway’s Newsletter','From the author of Tolkien’s Faith: A Spiritual Biography.')],
 'dante-alighieri':[ss('Word & Song','From Anthony Esolen, translator of the Divine Comedy.')],
 'flannery-o-connor':[ss('The Scandal of Reading','From Jessica Hooten Wilson, a leading O’Connor scholar.')],
 'hans-urs-von-balthasar':[ss('Gaudium et Spes 22','Larry Chapp writes theology in the key of von Balthasar and Ratzinger.')],
 'joseph-ratzinger':[ss('Gaudium et Spes 22','Larry Chapp writes theology in the key of Ratzinger and von Balthasar.')],
 'dorothy-day':[ss('Gaudium et Spes 22','Larry Chapp writes often on the Catholic Worker.'),dict(k='society',t='The Catholic Worker Movement',u='https://catholicworker.org/',n='Dorothy Day’s writings and the movement she co-founded.')],
 'john-henry-newman':[dict(k='society',t='National Institute for Newman Studies',u='https://www.newmanstudies.org/',n='Research, the Newman Reader, and scholarship on Newman.'),
   dict(k='podcast',t='Catholic Culture Audiobooks',u='https://www.catholicculture.org/commentary/category/audiobooks',n='Readings of classic works, with a special emphasis on Newman and the Fathers.')],
 'thomas-merton':[dict(k='society',t='Thomas Merton Center (Bellarmine University)',u='https://merton.org/',n='The Merton archive, chronology, and research resources.')],
}
# studies: books by one curated author about another (internal links; facts checked against standard bibliographies)
STUDY=[('g-k-chesterton','thomas-aquinas','St. Thomas Aquinas: “The Dumb Ox” (1933)'),('g-k-chesterton','francis-of-assisi','St. Francis of Assisi (1923)'),
 ('josef-pieper','thomas-aquinas','Guide to Thomas Aquinas (1958)'),('etienne-gilson','thomas-aquinas','The Christian Philosophy of St. Thomas Aquinas (Le Thomisme)'),
 ('etienne-gilson','augustine-of-hippo','The Christian Philosophy of Saint Augustine (1929)'),('etienne-gilson','bonaventure','The Philosophy of St. Bonaventure (1924)'),
 ('etienne-gilson','dante-alighieri','Dante and Philosophy (1939)'),('edward-feser','thomas-aquinas','Aquinas: A Beginner’s Guide (2009)'),
 ('reginald-garrigou-lagrange','thomas-aquinas','Reality: A Synthesis of Thomistic Thought (1946)'),('joseph-ratzinger','bonaventure','The Theology of History in St. Bonaventure (1959)'),
 ('joseph-ratzinger','augustine-of-hippo','Volk und Haus Gottes in Augustins Lehre von der Kirche (1954)'),('hans-urs-von-balthasar','therese-of-lisieux','Thérèse of Lisieux: The Story of a Mission (1950)'),
 ('sigrid-undset','catherine-of-siena','Catherine of Siena (1951)'),('thomas-merton','john-of-the-cross','The Ascent to Truth (1951)'),
 ('maisie-ward','g-k-chesterton','Gilbert Keith Chesterton (1943)'),('joseph-pearce','g-k-chesterton','Wisdom and Innocence: A Life of G. K. Chesterton (1996)'),
 ('joseph-pearce','j-r-r-tolkien','Tolkien: Man and Myth (1998)'),('wilfrid-ward','john-henry-newman','The Life of John Henry, Cardinal Newman (1912)'),
 ('evelyn-waugh','edmund-campion','Edmund Campion (1935)'),('evelyn-waugh','ronald-knox','The Life of Ronald Knox (1959)'),
 ('jean-pierre-torrell','thomas-aquinas','Saint Thomas Aquinas, vol. 1: The Person and His Work (1993)')]
for by,on,t in STUDY:
    assert by in AID and on in AID,(by,on)
    x(on).setdefault('studies',[]).append([by,t]);x(by).setdefault('wroteOn',[]).append([on,t])
for i,L in COMM.items():
    assert i in AID,i;x(i)['comm']=L
# own Substack for curated authors who write one
for s in G['substacks']:
    for a in A:
        if N(a['name'])==N(s['author']): x(a['id'])['own']=[dict(k='substack',t=s['name'],u=s['url'],n=s['desc'])]
# media by the author (curated resources whose name carries the author's name)
OWN={'robert-barron':['Word on Fire Show (Bishop Barron)','Bishop Robert Barron'],'fr-mike-schmitz':['The Bible in a Year (Fr. Mike Schmitz)','The Catechism in a Year (Fr. Mike Schmitz)','Ascension Presents'],
 'brant-pitre':['Dr. Brant Pitre — Catholic Productions','Catholic Productions (Brant Pitre)'],'scott-hahn':['Scott Hahn — St. Paul Center'],'jimmy-akin':['The Jimmy Akin Podcast','Jimmy Akin\'s Mysterious World'],
 'matt-fradd':['Pints with Aquinas (Matt Fradd)','Pints With Aquinas'],'taylor-marshall':['Dr. Taylor Marshall'],'trent-horn':['Counsel of Trent (Trent Horn)','The Counsel of Trent']}
RS={r['name']:r for r in D['resources']}
for i,names in OWN.items():
    if i not in AID: continue
    for n in names:
        r=RS.get(n)
        if r: x(i).setdefault('own',[]).append(dict(k='video' if 'youtube' in r['url'] else 'podcast',t=r['name'],u=r['url'],n=r['desc']))
# ---- Isidore Index books about the author (subject tags)
TAGS={}
for ti,t in enumerate(B['tags']):
    tt=set(N(t));ys=set(int(z) for z in re.findall(r'\b(\d{3,4})\b',t))
    for a in A:
        nt=[z for z in N(a['name']) if len(z)>2 and z not in STOP]
        if not nt: continue
        r1=nt[-1] in tt and ((a.get('died') and a['died'] in ys) or (a.get('born') and a['born'] in ys)) and len(set(nt)&tt)>=min(2,len(nt))
        r2=len(nt)>=2 and set(nt)<=tt
        if r1 or r2: TAGS.setdefault(a['id'],set()).add(ti)
for i,ts in TAGS.items():
    ids=[b[0] for b in B['books'] if set(b[4])&ts and not any(B['authors'][k][1]==i for k in b[2] if isinstance(B['authors'][k],list))]
    if ids: x(i)['about']=ids[:60]
# ---- reading lists
for l in G['lists']:
    for it in l['items']:
        w=next((e for e in G['editions'] if e['id']==it.get('e')),None)
        aid=w['aid'] if w else next((a['id'] for a in A if it.get('a') and N(a['name'])==N(it['a'])),'')
        if aid:
            L=x(aid).setdefault('lists',[])
            if l['id'] not in [z[0] for z in L]: L.append([l['id'],l['t']])
# ---- rare works and projects that name the author
NOTR={('henry-edward-manning','a592135400mannuoft'),('james-gibbons','nevvtestamentofi00mart'),('robert-p-george','bub_gb_lY2XbxfPX4sC')}  # surname-only false positives, checked by hand
NOTP={('thomas-aquinas',13)}
lastc={}
for a in A:
    nt=[z for z in N(a['name']) if z not in STOP]
    if nt: lastc[nt[-1]]=lastc.get(nt[-1],0)+1
ALIAS={'augustine-of-hippo':['saint augustine','st augustine','augustine of hippo'],'thomas-aquinas':['thomas aquinas'],'bonaventure':['bonaventure'],'isidore-of-seville':['isidore of seville']}
def keys(a):
    nt=[z for z in N(a['name']) if z not in STOP];k=[' '.join(N(a['name']))]+ALIAS.get(a['id'],[])
    if ' of ' not in a['name'] and not a['name'].startswith('Pope') and nt and len(nt[-1])>=6 and lastc[nt[-1]]==1: k.append(nt[-1])
    return k
def hit(text,ks):
    t=' '+' '.join(N(text))+' ';return any(' '+k+' ' in t for k in ks)
for a in A:
    ks=keys(a)
    r=[it['id'] for it in RA['items'] if hit(it['a']+' '+it['t'],ks)]
    p=[it['id'] for it in PJ['items'] if hit(it['n']+' '+it['tx']+' '+it['d'],ks)]
    r=[z for z in r if (a['id'],z) not in NOTR]
    if r: x(a['id'])['rare']=r
    p=[z for z in p if (a['id'],z) not in NOTP]
    if p: x(a['id'])['proj']=p
out={'generated':'2026-10-21','note':'Per-author extras. Wikidata-derived fields (ce, sep, iep, ws, wq, feast, order, infl, inflOn, stof, stu) come only from each author\'s verified QID.','by':X}
open(R+'site/data/authorx.js','w',encoding='utf-8').write('window.AUTHORX='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
from collections import Counter
c=Counter(k for e in X.values() for k in e);print(len(X),dict(c),os.path.getsize(R+'site/data/authorx.js'))
for i in ['g-k-chesterton','thomas-aquinas','augustine-of-hippo','john-henry-newman']: print(i,json.dumps(X.get(i),ensure_ascii=False)[:900])
