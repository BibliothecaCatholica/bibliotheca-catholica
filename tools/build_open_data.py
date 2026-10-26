"""Build the CC0 open-data release in site/data/open/ (JSON + CSV + README + manifest)."""
import json,csv,os,re,subprocess,datetime,urllib.parse,hashlib
from pathlib import Path
S=str(Path(__file__).resolve().parents[1]/'data')+'/';O=S+'open/';os.makedirs(O,exist_ok=True)
EFL=json.load(open(S+'editorial-flags.json',encoding='utf-8'))['books'] if os.path.exists(S+'editorial-flags.json') else {}
def loadjs(p,var):
    s=open(p,encoding='utf-8').read();i=s.index('=')+1;return json.loads(s[i:].strip().rstrip(';'))
hub=json.load(open(S+'catholic-hub.json'));bk=json.load(open(S+'books.json'))
# v16 rights status (tools/build_rights.py): file links only for public_domain_us, open_license, permission_granted
RT=json.load(open(S+'rights.json',encoding='utf-8'))
def rights(i):
    r=RT['records'][str(i)];c=RT['codes'][r[0]];st=r[3] if r[0]=='M' else c['status']
    return st,(c['text']+' '+r[1]).strip() if len(r)>1 and r[1] else c['text'],(r[2] if r[0]=='M' else RT['checked']),RT['statuses'][st]['hostable']
guide=loadjs(S+'guide.js','GUIDE_DATA');doc=loadjs(S+'doctors.js','DOCTORS_DATA');rare=loadjs(S+'rare.js','RARE_DATA');proj=loadjs(S+'projects.js','PROJECTS_DATA')
SITE='https://bibliothecacatholica.com/'
ERAL={e['id']:e['label'] for e in hub['eras']}
LANGN={'eng':'English','lat':'Latin','fra':'French','ita':'Italian','spa':'Spanish','deu':'German','grc':'Ancient Greek','por':'Portuguese','hbo':'Hebrew (Ancient)','rus':'Russian','syc':'Syriac','pol':'Polish','ile':'Interlingua (Peano)','zho':'Chinese','fro':'Old & Middle French','fas':'Persian','chu':'Church Slavonic','enm':'Middle English','nor':'Norwegian','gle':'Irish','swe':'Swedish','fin':'Finnish'}
MAN=[]
def write(name,rows,cols,desc,fields):
    json.dump(dict(name=name,description=desc,license='CC0-1.0',generated=str(datetime.date.today()),count=len(rows),fields=fields,records=rows),open(O+name+'.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
    with open(O+name+'.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(cols)
        for r in rows: w.writerow(['; '.join(map(str,r[c])) if isinstance(r.get(c),list) else ('' if r.get(c) is None else r.get(c)) for c in cols])
    MAN.append(dict(name=name,description=desc,count=len(rows),json='data/open/'+name+'.json',csv='data/open/'+name+'.csv',fields=fields))
# 1. Isidore Index
def predSub(t,i):
    import unicodedata
    t=re.sub(r'[\u0300-\u036f]','',unicodedata.normalize('NFD',t));t=re.sub(r'[\\/:*?"<>|]','_',t);return t[:95].strip()+f' ({i})'
rows=[]
for r in bk['books']:
    au=[bk['authors'][i] for i in r[2]];fo=bk['folders'][r[8]];sub=r[9] or predSub(r[1],r[0])
    e=r[12] if len(r)>12 else -1
    fm=r[7].split('|') if r[7] else []
    rs,rev,rch,ok=rights(r[0])
    rows.append(dict(id=r[0],title=r[1],authors=[a[0] for a in au],curated_author_ids=[a[1] for a in au if a[1]],catalog_year=r[3] or None,
      era=bk['eras'][e%100] if e>=0 else None,era_source=('catalog life dates' if e>=100 else 'curated author page') if e>=0 else None,
      languages=[LANGN.get(l,l) for l in (r[10].split(',') if r[10] else [])],language_codes=r[10].split(',') if r[10] else [],
      formats=fm,subjects=[bk['tags'][i] for i in r[4]],series=bk['series'][r[5]] if r[5]>=0 else None,series_index=r[6] if r[5]>=0 else None,
      publisher=bk['publishers'][r[11]] if r[11]>=0 else None,
      isidore_book_url=bk['server']+f'legacy/book/{r[0]}/CalibreLibrary',isidore_files_url=bk['base']+urllib.parse.quote(fo)+'/'+urllib.parse.quote(sub)+'/' if ok else None,
      download_urls=[bk['server']+f'get/{f}/{r[0]}/CalibreLibrary' for f in fm] if ok else [],rights_status=rs,rights_evidence=rev,rights_checked=rch,page_url=SITE+f'#/isidore/book/{r[0]}',editorial_flag=(EFL.get(str(r[0])) or {}).get('flag'),context_note=(EFL.get(str(r[0])) or {}).get('note')))
F1={'id':'isidore.co Calibre book id','title':'title as catalogued','authors':'author names as catalogued (Calibre "Surname, Forename")','curated_author_ids':'ids of matching pages in authors.json','catalog_year':'Calibre pubdate year; often a scan or reprint date, NOT evidence of copyright status','era':'era id (see authors.json eras)','era_source':'"curated author page" or "catalog life dates" (inferred)','languages':'canonical language names','language_codes':'ISO 639-2/3 codes after normalization','formats':'file formats on isidore.co','subjects':'Calibre tags (up to 6, most common first)','series':'series','series_index':'number in series','publisher':'publisher','isidore_book_url':'book page on isidore.co','isidore_files_url':'folder of files on isidore.co; empty unless rights_status is public_domain_us, open_license, or permission_granted','download_urls':'per-format download URLs on isidore.co; empty unless rights_status is public_domain_us, open_license, or permission_granted','rights_status':'public_domain_us, open_license, permission_granted, link_only, or unknown (see /rights; not legal advice). Only the first three may be downloaded or read here','rights_evidence':'why the record has that status: a lead to check, a presumption, or written evidence','rights_checked':'date the status was last checked (YYYY-MM-DD)','page_url':'detail page on Bibliotheca Catholica','editorial_flag':'editorial category if the record carries a context note (see #/policy); listing is not endorsement','context_note':'short factual context note shown on the record page'}
write('isidore-index',rows,list(F1),'Every book record in the St. Isidore (isidore.co) Calibre library, normalized: canonical languages, author era, rights status, and deep links. Files stay on isidore.co; file links are given only for public-domain, openly licensed, or permitted records.',F1)
# 2. Isidore author names (v18: no raw isidore.co folder URLs, rights rule 10; each name links to its Isidore Index search)
def iso_url(i):return SITE+'#/isidore/author='+urllib.parse.quote(i.get('a') or i['n'],safe='')  # v18.2: name as the books carry it
fold2={}
for a in hub['authors']:
    if a.get('isidoreFolder'):fold2[a['isidoreFolder']]=a['id']
for r in bk['books']:
    if r[2] and bk['authors'][r[2][0]][1]:
        fold2.setdefault(bk['folders'][r[8]],bk['authors'][r[2][0]][1])
rows=[dict(name=i['n'],folder=i['f'],index_url=iso_url(i),curated_author_id=fold2.get(i['f'])) for i in hub['isidore']]
print('folders mapped to curated authors',sum(1 for x in rows if x['curated_author_id']),'distinct authors',len(set(x['curated_author_id'] for x in rows if x['curated_author_id'])))
F2={'name':'author name as catalogued on isidore.co','folder':'the catalog folder name (text only; folder listings are not linked)','index_url':'this author in the Isidore Index on bibliothecacatholica.com, where rights badges decide which links each book gets','curated_author_id':'matching page in authors.json, if any'}
write('isidore-folders',rows,list(F2),'Every author name in the isidore.co catalog, with a link to its Isidore Index search and to curated author pages where confident. Raw folder listings are not linked.',F2)
# 3. Authors (no Wikipedia text: that is CC BY-SA and excluded)
rows=[]
for a in hub['authors']:
    L=a['links'];g=lambda k:next((l['url'] for l in L if k in l['url']),None)
    rows.append(dict(id=a['id'],name=a['name'],born=a['born'],died=a['died'],dates_display=a.get('dshow'),era=a['era'],era_label=ERAL[a['era']],century=a['century'],tags=a['tags'],doctor=a['doctor'],summary=a['desc'],
      wikidata_qid=a.get('qid'),wikidata_work_qid=a.get('qidWork'),wikipedia_url=g('wikipedia.org'),isidore_index_url=iso_url(next(i for i in hub['isidore'] if i['f']==a['isidoreFolder'])) if a.get('isidoreFolder') else None,
      catholic_encyclopedia_url=next((l['url'] for l in L if '/cathen/' in l['url']),None),gutenberg_url=g('gutenberg.org'),ccel_url=g('ccel.org'),page_url=SITE+'#/author/'+a['id']))
F3={'id':'stable slug','name':'display name','born':'birth year (number; approximate for early figures)','died':'death year','dates_display':'precise display form where sources differ','era':'era id','era_label':'era name','century':'floruit century','tags':'roles (doctor, saint, pope, …)','doctor':'Doctor of the Church','summary':'our one-line summary (CC0)','wikidata_qid':'Wikidata item for the person, verified via the enwiki sitelink','wikidata_work_qid':'for anonymous authors: Wikidata item of the work','wikipedia_url':'English Wikipedia article','isidore_index_url':'this author in the Isidore Index (v18; replaces isidore_folder_url)','catholic_encyclopedia_url':'New Advent Catholic Encyclopedia article','gutenberg_url':'Project Gutenberg author page','ccel_url':'CCEL author page','page_url':'author page on Bibliotheca Catholica'}
write('authors',rows,list(F3),'Curated Catholic authors (476) in 12 eras, with Wikidata QIDs and cross-links.',F3)
# 4. Editions
rows=[]
for w in guide['editions']:
    for i,p in enumerate(w['picks']):
        rows.append(dict(work_id=w['id'],work=w['t'],author=w['a'],author_id=w.get('aid') or None,category=w['cat'],rank=i+1,label=p.get('lbl'),edition=p.get('tr'),publisher=p.get('pub'),isbn13=p.get('isbn') or None,note=p.get('note'),page_url=SITE+'#/editions/'+w['id']))
F4={'work_id':'work slug','work':'work title','author':'author','author_id':'authors.json id','category':'category','rank':'order of recommendation','label':'why this pick','edition':'translation / edition','publisher':'publisher','isbn13':'ISBN-13 verified against Open Library','note':'our note','page_url':'guide page'}
write('editions',rows,list(F4),'“Which edition?” guide: recommended translations and editions of Catholic classics, with verified ISBNs.',F4)
# 5. Doctors free texts
rows=[]
for did,d in doc['doctors'].items():
    for w in d['works']:
        if not w['links']: rows.append(dict(doctor_id=did,doctor=d['name'],work=w['t'],url=None,source=None,translator=None,edition_year=None,rights=None,flag=None,gap=w.get('gap')))
        for l in w['links']: rows.append(dict(doctor_id=did,doctor=d['name'],work=w['t'],url=l['u'],source=l['s'],translator=l['tr'],edition_year=l['y'],rights=l['pds'],flag=l['fl'],gap=w.get('gap')))
F5={'doctor_id':'authors.json id','doctor':'name','work':'work','url':'free full-text link (outbound)','source':'host site','translator':'translator of the linked edition','edition_year':'year of the linked edition','rights':'rights status of the linked edition (US PD = before 1931)','flag':'access caveat','gap':'note when no free PD English text was found'}
write('doctors-free-texts',rows,list(F5),'Key works of the 38 Doctors of the Church with free full-text links and per-edition rights status.',F5)
# 6. Rare
rows=[dict(id=r['id'],theme=r['th'],title_english=r['t'],title_original=r['o'],author=r['a'],date=r['d'],language=r['lang'],genre=r['g'],why_notable=r['w'],catholic_status=r['cs'],public_domain_status=r['pds'],ai_assisted_translation=r['ai'],links=[l[0]+': '+l[1] for l in r['links']],page_url=SITE+'#/rare/'+urllib.parse.quote(r['id'])) for r in rare['items']]
F6={'id':'Internet Archive identifier','theme':'theme','title_english':'English gloss','title_original':'original title','author':'author (archive metadata)','date':'edition date','language':'language','genre':'genre / subject','why_notable':'note','catholic_status':'Catholic, or flagged','public_domain_status':'US PD or NOT PD','ai_assisted_translation':'self-described AI translation','links':'labelled links (files are linked only for PD items)','page_url':'entry on Bibliotheca Catholica'}
write('rare-works',rows,list(F6),'Rare & Obscure: 122 forgotten Catholic works in digital archives, grouped by theme.',F6)
# 7. Projects
rows=[dict(name=p['n'],category=p['cat'],url=p['u'],github=p['gh'] or None,license=p['lic'],languages=p['lang'],description=p['d'],texts=p['tx'],ai=p['ai'],ai_detail=p['ais'],note=p['note'] or None,x_handles=p['h']) for p in proj['items']]
F7={'name':'project','category':'category','url':'homepage','github':'repository','license':'license as stated','languages':'languages','description':'summary','texts':'texts covered','ai':'human / ai / unclear','ai_detail':'stated AI use','note':'neutral note','x_handles':'X accounts'}
write('projects',rows,list(F7),'Projects & Translations: 73 Catholic digital projects with AI-assisted work labelled (flagged entries excluded).',F7)
json.dump(dict(title='Bibliotheca Catholica open data',license='CC0-1.0',generated=str(datetime.date.today()),homepage=SITE+'#/data',datasets=MAN),open(O+'manifest.json','w'),indent=1)
print([(m['name'],m['count']) for m in MAN])
open(S+'open.js','w').write('window.OPEN_MANIFEST='+json.dumps(dict(generated=str(datetime.date.today()),datasets=[{k:m[k] for k in ('name','description','count','json','csv','fields')} for m in MAN]),ensure_ascii=False,separators=(',',':'))+';\n')
