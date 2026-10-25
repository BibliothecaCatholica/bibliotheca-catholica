#!/usr/bin/env python3
"""One-time (re)import of the Bibliotheca Research saints pilot into data/saints.json.

    python3 tools/import_saints_pilot.py --research /path/to/research
    python3 tools/build_saints.py

Reads saints-pilot.json, catholicsaints-mapping.json, and saints-books-verified.json from the
research folder and writes data/saints.json, the hand-editable source for the Saints section.
After the import, edit data/saints.json directly (see AGENTS.md, "Saints & Hagiography").

Rights rules enforced here (see docs/SAINTS.md):
- CatholicSaints.Info is link-only. A profile link is kept ONLY for the 139 tier-1 writers listed
  in catholicsaints-mapping.json `mapping`; the tier-2/3 exact-name sitemap matches ("unverified")
  are dropped until a person checks them. No CatholicSaints.Info text, dates, or calendar is kept.
- Emblems and patronages (phase 4) are not imported yet.
"""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MONTHS=['january','february','march','april','may','june','july','august','september','october','november','december']
def year(v):
    if not v:return None
    m=re.match(r'^([+-]?)(\d{1,4})-',v)
    if not m:return None
    y=int(m.group(2));return -y if m.group(1)=='-' else y
def p841(vals):
    out=[]
    for v in vals:
        m=re.match(r'^([A-Za-z]+)\s+(\d{1,2})$',v.strip())
        if m and m.group(1).lower() in MONTHS:out.append('%02d-%02d'%(MONTHS.index(m.group(1).lower())+1,int(m.group(2))))
    return sorted(set(out))
# Hand-added alias forms (spec section 5). Keys are display forms; build_saints.py normalizes them.
HAND_ALIASES={
 'john-of-damascus':['John Damascene'],
 'edith-stein':['Teresa Benedicta of the Cross'],
 'rita-of-cascia':['Margherita Lotti'],
 'lawrence-of-rome':['Laurence'],
 'therese-of-lisieux':['Little Flower','Thérèse of the Child Jesus','Saint Thérèse'],
 'thomas-aquinas':['Thomas Aquinas','Angelic Doctor'],
}
# Books on the hagiography shelf that are about specific pilot saints.
BOOK_ABOUT={
 'pg-7165-the-legends-of-saint-patrick':['patrick'],'pg-18482-the-most-ancient-lives-of-saint-patrick':['patrick'],
 'pg-18787-life-of-st-francis-of-assisi':['francis-of-assisi'],'pg-6367-the-life-and-legends-of-saint-francis-of':['francis-of-assisi'],
 'little-flowers-alger-1887':['francis-of-assisi'],
}
BOOK_BY={'catherine-dialogue-thorold':['catherine-of-siena']}
SKIP_BOOKS={'butler-ccel','sheen-seven-last-words','clarke-charity','catechism-of-mental-prayer'}
SHELF_GROUPS=[
 ('collections','Collected lives and dictionaries',['butler-lives-pg-20450','butler-lives-pg-49604','butler-lives-ia-1812','baring-gould-lives-pg-46947','baring-gould-lives-pg-45604','baring-gould-lives-pg-48395','baring-gould-lives-ia-1897','golden-legend-ellis-1900','roman-martyrology-1897','ramsgate-book-of-saints-1921','dunbar-saintly-women','catholic-encyclopedia-saints','pictorial-lives-of-the-saints','new-catholic-dictionary-1929']),
 ('single','Lives of single saints, and their own writings',['little-flowers-alger-1887','pg-18787-life-of-st-francis-of-assisi','pg-6367-the-life-and-legends-of-saint-francis-of','pg-7165-the-legends-of-saint-patrick','pg-18482-the-most-ancient-lives-of-saint-patrick','catherine-dialogue-thorold','baring-gould-virgin-saints-pg-53841','pg-22112-a-childs-book-of-saints']),
 ('art','Saints in art and the study of legend',['jameson-sacred-legendary-art','jameson-legends-madonna','jameson-monastic-orders','delehaye-legends-of-the-saints']),
 ('devotion','Devotional companions',['okennedy-holy-angels','goodier-crown-of-sorrow','nepveu-meditations','yorke-the-mass']),
 ('fiction','Fiction',['pg-62254-fabiola']),
]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--research',required=True);args=ap.parse_args();R=Path(args.research)
    pilot=json.loads((R/'saints-pilot.json').read_text());mapping=json.loads((R/'catholicsaints-mapping.json').read_text())
    books=json.loads((R/'saints-books-verified.json').read_text())['books']
    cs={m['author_id']:m for m in mapping['mapping']}
    hub={a['id']:a for a in json.loads((ROOT/'data/catholic-hub.json').read_text())['authors']}
    saints=[]
    for s in pilot['saints']:
        aid=s.get('author_id')
        st=s['status'];status={'value':st['value'],'evidence':st.get('evidence',''),'source_url':st['source_url']}
        if st.get('review'):status['review']=st['review']
        if s.get('historicity',{}).get('flag')=='angel':status['value']='archangel'
        f=s['feast'];wd=f.get('wikidata_p841') or {}
        # Wikidata sometimes holds century-precision birth years that fall after the death year
        # (e.g. Christopher born "300", died 251). Drop an impossible birth year rather than show it.
        by,dy=year(s.get('born')),year(s.get('died'))
        if by is not None and dy is not None and by>=dy:s=dict(s,born=None)
        rec={'id':s['id'],'qid':s['qid'],'name':s['name'],'tier':s['tier'],
             'kind':'angel' if (s.get('historicity') or {}).get('flag')=='angel' else 'person',
             'author_id':aid,'aliases':sorted(set(s['aliases']+([hub[aid]['name']] if aid else [])+HAND_ALIASES.get(s['id'],[]))),
             'aliases_source':s['aliases_source'],'status':status,
             'born':{'year':year(s.get('born')),'source_url':s['wikidata_url']+'#P569'} if year(s.get('born')) is not None else None,
             'died':{'year':year(s.get('died')),'source_url':s['wikidata_url']+'#P570'} if year(s.get('died')) is not None else None,
             'feasts':{'vatican_news':[{'date':v['date'],'title_on_source':v['title_on_source'],'source_url':v['source_url']} for v in f['vatican_news']],
                       'general_roman_calendar':None,
                       'other_wikidata':{'dates':p841(wd.get('values',[])),'source_url':wd.get('source_url',s['wikidata_url']+'#P841')}},
             'historicity':s.get('historicity'),
             'catholic_encyclopedia':{'url':s['catholic_encyclopedia']['url'],'source_url':s['catholic_encyclopedia']['source_url']} if s.get('catholic_encyclopedia') else None,
             'catholicsaints':None,'wikipedia':s.get('enwiki'),'wikidata':s['wikidata_url'],
             'reading_room_works':s['reading_room_works'],'lives_about':[]}
        if aid and aid in cs and s['tier']==1:
            m=cs[aid];assert m['catholicsaints_url']==(s.get('catholicsaints') or {}).get('url'),aid
            rec['catholicsaints']={'url':m['catholicsaints_url'],'wayback_url':m['wayback_url'],'confidence':m['confidence'],'source':'catholicsaints-mapping.json','link_only':True}
        for bid,ids in BOOK_ABOUT.items():
            if s['id'] in ids:rec['lives_about'].append(bid)
        saints.append({k:v for k,v in rec.items() if v is not None or k in('catholicsaints','historicity','author_id')})
    B={b['id']:b for b in books};shelf=[]
    # Link each shelf book to its reading-room work (v14b added most of them) by matching the source URL.
    LIBW=json.loads((Path(__file__).resolve().parents[1]/'data/library.json').read_text())['works']
    def lib_work(url):
        tail=url.rstrip('/').split('/')[-1]
        for w in LIBW:
            if any(e.get('source') and (e['source'].rstrip('/')==url.rstrip('/') or e['source'].rstrip('/').endswith('/'+tail)) for e in w['editions']):return w['id']
        return None
    for gid,glabel,ids in SHELF_GROUPS:
        for bid in ids:
            b=B[bid];assert bid not in SKIP_BOOKS and b['public_domain_verdict'].startswith('PD-US'),bid
            sre=b.get('suggested_reader_entry') or {}
            shelf.append({'id':bid,'group':gid,'title':b['title'],'author':b['author'],'url':b['url'],'source':b['source'],
              'edition':b['edition'],'imprint_date':b['imprint_date'],'imprint':b['imprint'],'translator_editor':b['translator_editor'],
              'public_domain':b['public_domain_verdict'],'evidence':b['evidence'],'checked':b['checked'],
              'work_id':lib_work(b['url']),'fiction':bid=='pg-62254-fabiola','about':BOOK_ABOUT.get(bid,[]),'by':BOOK_BY.get(bid,[])})
    out={'generated':pilot['generated'],
         'note':'Source for the Saints & Hagiography section. Edit this file, then run python3 tools/build_saints.py. Every claim carries a source_url. CatholicSaints.Info is link-only (tier-1 mapping only).',
         'shelf_groups':[[g,l] for g,l,_ in SHELF_GROUPS],'saints':sorted(saints,key=lambda x:x['id']),'shelf':shelf}
    (ROOT/'data/saints.json').write_text(json.dumps(out,ensure_ascii=False,indent=1)+'\n')
    print(len(saints),'saints;',sum(1 for x in saints if x['catholicsaints']),'CatholicSaints.Info links;',len(shelf),'shelf books')
if __name__=='__main__':main()
