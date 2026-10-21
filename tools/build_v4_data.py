"""Build site/data/doctors.js and site/data/rare.js from the research drops (links only; nothing hosted)."""
import json,re,os
R='research'
def pdk(s):
    s=s or ''
    if s.startswith('PD in US (original'): return 'orig'
    if s.startswith('PD in US'): return 'pd'
    if s.startswith('free to read'): return 'free'
    if s.startswith('copyrighted'): return 'cr'
    return 'unc'
D=json.load(open(f'{R}/doctors-fulltext-sources.json'))
docs={};nl=0;nw=0
for d in D['doctors']:
    works=[]
    for w in d['works']:
        nw+=1
        L=[]
        for l in w['links']:
            nl+=1
            L.append(dict(u=l['url'],s=l['source_site'],tr=l['translator'],y=l['edition_year'],pd=pdk(l['pd_status']),pds=l['pd_status'],fl=l['flag']))
        works.append(dict(t=w['title'],gap=w.get('gap'),links=L))
    o=dict(name=d['name'],born=d['born'],died=d['died'],feast=d['feast_day'],decl=d['declared_doctor'],by=d['declared_by'],src=d['bio_sources'],works=works)
    if d['id']=='john-henry-newman':
        o['feastNote']='Optional memorial on 9 October, inscribed in the General Roman Calendar by the decree published 3 February 2026.'
        o['feastSrc']='https://press.vatican.va/content/salastampa/en/bollettino/pubblico/2026/02/03/260203a.html'
    docs[d['id']]=o
O=json.load(open(f'{R}/obscure-archive-writings.json'))
order=['Modern community translations (seed cluster)','Cornaeus & the Würzburg/Bamberg Jesuit controversialists','German Counter-Reformation polemic','English & Scottish recusant literature','French, Polish & Hungarian controversy','Early Dominican Thomists & incunabula','Forgotten Baroque scholastics','Jesuitica, devotion, missions & curiosa','19th-c. neo-scholastic revival & critical editions','19th-c. Catholic periodicals','Flagged: non-Catholic responses (context only)']
rare=[];cnt={'pd':0,'notpd':0,'noncath':0}
for e in O['entries']:
    notpd=e['public_domain_status'].startswith('NOT PD')
    nonc='NON-CATHOLIC' in e['catholic_status'].upper()
    lk=e['links'];links=[]
    links.append(('Archive.org',lk['item_url']))
    if not notpd:  # modern unlicensed translations: link to the item page only, never the file
        if lk.get('file_url'): links.append(('PDF',lk['file_url']))
        if lk.get('google_books_url'): links.append(('Google Books',lk['google_books_url']))
        if lk.get('bsb'): links.append(('MDZ (BSB)',lk['bsb']))
        if lk.get('translation_url'): links.append(('English translation',lk['translation_url']))
    if lk.get('prdl'): links.append(('PRDL',lk['prdl']))
    if lk.get('wiki'): links.append(('About',lk['wiki']))
    ai='AI translation' in e['why_notable'] or 'AI translation' in e['english_translation']
    why=re.sub(r'\s*FLAG: self-described AI translation\.?','',re.sub(r'\s*FLAG: the uploader describes it as an AI translation\.?','',e['why_notable'])).strip()
    cnt['notpd' if notpd else 'pd']+=1; cnt['noncath']+=nonc
    rare.append(dict(id=e['id'],th=e['theme'],t=e['title_english_gloss'],o=e['title_original'],a=e['author'],d=e['date_edition'],lang=e['language'],g=e['genre_subject'],w=why,cs=e['catholic_status'],nonc=nonc,notpd=notpd,ai=ai,pds=e['public_domain_status'],links=links))
rare.sort(key=lambda r:(order.index(r['th']) if r['th'] in order else 99))
os.makedirs('site/data',exist_ok=True)
open('site/data/doctors.js','w').write('window.DOCTORS_DATA='+json.dumps(dict(generated=D['meta']['generated'],doctors=docs),ensure_ascii=False,separators=(',',':'))+';\n')
open('site/data/rare.js','w').write('window.RARE_DATA='+json.dumps(dict(generated=O['generated'],themes=order,items=rare),ensure_ascii=False,separators=(',',':'))+';\n')
print('doctors',len(docs),'works',nw,'links',nl,'| rare',len(rare),cnt)

# ---------- Projects & Translations ----------
P=json.load(open(f'{R}/catholic-projects.json'))['projects']
BAD_H={'@complutenses','@ofsaintthomas','@thomisticae'}
def isexcluded(p):
    n=(p.get('orthodoxy_note') or '')
    return n.startswith('FLAG') or n.strip()=='Not a Catholic project' or 'sedevacant' in n.lower()
def fixh(s): return re.sub(r'@[Tt]homisticae','@ViaEximii',s or '')
def aik(s):
    s=(s or '').lower()
    if s.startswith('no'): return 'human'
    if s.startswith(('yes','partly','likely')): return 'ai'
    return 'unclear'
projects=[];excl=[]
for p in P:
    if isexcluded(p): excl.append((p['id'],p['name'],p['orthodoxy_note'][:90])); continue
    hs=[h.strip() for h in (p['x_handle'] or '').split(';') if h.strip() and h.strip().lower() not in BAD_H]
    o=dict(id=p['id'],n=fixh(p['name']),cat=p['category'],u=p['url'],st=p['url_status'],gh=p['github_url'],stars=p['github_stars'],lic=p['license'],lang=p['languages'],tx=fixh(p['texts']),m=fixh(p['maintainer']),d=fixh(p['description']),why=fixh(p['why']),ai=aik(p['ai_assisted']),ais=p['ai_assisted'],note=p['orthodoxy_note'],unc=fixh(p['uncertainty']),std=p['tier']=='standout',h=hs)
    if p['id']==8:
        o['n']='@ViaEximii: Baroque Thomist and controversialist translations (Internet Archive)'
        o['m']='Astro, @ViaEximii on X (Substack: benescripsisti.substack.com)'
        o['unc']='Attribution is per item, and several volumes are self-described AI translations. Read them alongside the Latin.'
        o['tx']=o['tx'].replace("that credit '@ViaEximii'","by the same translator")
    projects.append(o)
# human translations first within each category, then AI-assisted
rank={'human':0,'unclear':1,'ai':2}
projects.sort(key=lambda o:(rank[o['ai']] if o['cat']=='translation' else 0))
open('site/data/projects.js','w').write('window.PROJECTS_DATA='+json.dumps(dict(generated='2026-10-21',items=projects),ensure_ascii=False,separators=(',',':'))+';\n')
import collections
print('projects shown',len(projects),'excluded',len(excl),excl)
print(' ai',collections.Counter(o['ai'] for o in projects),'standouts',sum(o['std'] for o in projects),collections.Counter(o['cat'] for o in projects))
