#!/usr/bin/env python3
"""Build the Saints & Hagiography data: data/saints.json -> data/saints.js and data/saints-aliases.json.

    python3 tools/build_saints.py

data/saints.json is the hand-edited source. This script validates it (every claim has a source_url,
CatholicSaints.Info links only on tier-1 writers from the mapping, tradition flags on tier 3, author
ids exist), builds the alias table with the spec's normalization (NFKD, strip diacritics, lowercase,
collapse punctuation, drop leading honorifics), and FAILS if a multi-word alias key maps to two
saints. Bare one-word names shared by several saints (john, gregory, catherine, ...) never map to one
saint; they go to `collisions` and the UI shows "Did you mean...". No fuzzy matching anywhere.
"""
import json,re,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HONORIFICS={'saint','st','sts','saints','blessed','bl','bd','pope','the'}
# Bare names that must never resolve to one saint (spec section 5), whatever the data says.
BARE={'alexander','richard','maximus','julian','leonard','henry','edmund','raymond','charles','philip','titus','columba','claude','germanus','macarius','methodius','theodore','jean','robert','andrew','dionysius','margaret','anthony','antony','john','gregory','francis','catherine','thomas','james','peter','paul','mary','teresa','theresa','joseph','michael','george','anne','benedict','leo','pius','ignatius','cyril','clement','basil','vincent','dominic','bernard','anthony','antony','augustine','john paul','louis','margaret','elizabeth','bridget','clare','agnes','lucy','martin','nicholas','patrick','stephen','andrew','jude','jerome','ambrose','bede','isidore','lawrence','laurence'}
# One-word keys that are each a single, well-known saint in the pilot and may map directly.
BARE_OK={'joseph':'joseph','michael':'michael-the-archangel','george':'george','jerome':'jerome','ambrose':'ambrose-of-milan','bede':'bede-the-venerable','patrick':'patrick','nicholas':'nicholas-of-myra','lucy':'lucy-of-syracuse','agnes':'agnes-of-rome','jude':'jude-the-apostle','clare':'clare-of-assisi','laurence':'lawrence-of-rome','lawrence':'lawrence-of-rome','stephen':'stephen-protomartyr'}
# Reviewed one-word forms (Latin, Greek, or vernacular names) that point to one pilot saint only.
SINGLE_OK={'adamnan','agathe','aikaterine','ekaterine','hecaterina','ambrosius','aquinas','athanasias','augoustinos','barbe','bernardin','bernardine','bernardinus','bernhardin','blasius','bonaventura','caecilia','cephas','chrysostomus','chryssorhoas','columban','cothirthiacus','magonus','succetus','patricius','davnet','didymos','didymus','heronimos','hieronymus','hildefuns','ildefonso','ildefonsus','hildegardis','hrabanus','rhabanus','josef','jpii','kipa','laurentius','magdalene','rochus','roche','saul','saulus','valentinus','winfrid','wynfrith','wynfryth','therese'}
def key(s):
    s=unicodedata.normalize('NFKD',str(s));s=''.join(c for c in s if not unicodedata.combining(c)).lower()
    s=re.sub(r"[’'`]",'',s);s=re.sub(r'[^a-z0-9]+',' ',s).strip()
    w=s.split()
    while len(w)>1 and w[0] in HONORIFICS:w=w[1:]
    return ' '.join(w)
def fail(msg):sys.exit('build_saints: '+msg)
def claims(o,path):
    """Yield (path,dict) for every dict that looks like a claim (has a value-ish field)."""
    if isinstance(o,dict):
        yield path,o
        for k,v in o.items():yield from claims(v,path+'.'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o):yield from claims(v,path+'[%d]'%i)
def validate(D,hub,lib):
    ids=set();S=D['saints']
    for s in S:
        i=s['id']
        if i in ids:fail('duplicate id '+i)
        ids.add(i)
        for f in('id','qid','name','tier','kind','aliases','status','feasts','wikidata'):
            if f not in s:fail(i+': missing '+f)
        if not re.match(r'^[a-z0-9-]+$',i):fail(i+': id must be kebab-case')
        if s.get('born') and s.get('died') and s['born']['year']>=s['died']['year']:fail(i+': born year is not before died year')
        if s['tier'] not in(1,2,3):fail(i+': tier')
        if s['tier']==1 and s.get('author_id')!=i:fail(i+': tier-1 id must equal its author id')
        if s.get('author_id') and s['author_id'] not in hub:fail(i+': unknown author '+s['author_id'])
        if s['tier']==3 and not (s.get('historicity') or {}).get('flag'):fail(i+': tier 3 needs a historicity flag')
        if s.get('historicity') and not s['historicity'].get('source_url'):fail(i+': historicity needs a source_url')
        for p,o in claims({k:v for k,v in s.items() if k not in('catholicsaints',)},i):
            if any(k in o for k in('value','year','date','flag','title_on_source')) and not o.get('source_url'):fail(p+': claim without source_url')
        if s['feasts'].get('other_wikidata',{}).get('dates') and not s['feasts']['other_wikidata'].get('source_url'):fail(i+': other calendars need a source')
        for d in [v['date'] for v in s['feasts']['vatican_news']]+s['feasts'].get('other_wikidata',{}).get('dates',[]):
            if not re.match(r'^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$',d):fail(i+': bad date '+d)
        for v in s['feasts']['vatican_news']:
            if not v['source_url'].startswith('https://www.vaticannews.va/'):fail(i+': Vatican News source must be vaticannews.va')
        cs=s.get('catholicsaints')
        if cs:
            if s['tier']!=1:fail(i+': CatholicSaints.Info links are allowed only on tier-1 writers from the mapping')
            if cs.get('confidence') not in('high','medium') or cs.get('source')!='catholicsaints-mapping.json' or not cs.get('link_only'):fail(i+': CatholicSaints.Info link must come from the mapping and be link-only')
            if set(cs)-{'url','wayback_url','confidence','source','link_only'}:fail(i+': CatholicSaints.Info entry may hold links only, no copied text')
        for w in s.get('reading_room_works',[]):
            if w not in lib:fail(i+': unknown reading-room work '+w)
    return ids
NAME={}
def aliases(S):
    NAME.update({s['id']:s['name'] for s in S})
    owners={}
    for s in S:
        for a in [s['name']]+s['aliases']:
            k=key(a)
            if k:owners.setdefault(k,set()).add(s['id'])
    first={}
    for s in S:first.setdefault(key(s['name']).split(' ')[0],set()).add(s['id'])
    table={};coll={}
    for k,ids in sorted(owners.items()):
        if ' ' not in k:
            if k in BARE_OK:
                if BARE_OK[k] not in ids and BARE_OK[k] not in first.get(k,set()):fail('BARE_OK %s -> %s is not an alias of that saint'%(k,BARE_OK[k]))
                table[k]=BARE_OK[k];continue
            cand=ids|first.get(k,set())
            if k in BARE or len(cand)>1:coll[k]=sorted(cand);continue
            only=next(iter(ids))
            if k in SINGLE_OK or k==key(NAME[only]).split(' ')[0]:table[k]=only
            # other one-word aliases are not keys (they stay findable by ordinary search)
        else:
            if len(ids)>1:fail('alias key "%s" maps to %s; make it unique or remove it'%(k,sorted(ids)))
            table[k]=next(iter(ids))
    for k,ids in first.items():
        if len(ids)>1 and k not in table and k not in coll:coll[k]=sorted(ids)
    for k in list(coll):
        if k in table:del coll[k]
    return table,coll
def main():
    D=json.loads((ROOT/'data/saints.json').read_text())
    hub={a['id'] for a in json.loads((ROOT/'data/catholic-hub.json').read_text())['authors']}
    lib={w['id'] for w in json.loads((ROOT/'data/library.json').read_text())['works']}
    flagged=set(json.loads((ROOT/'data/editorial-flags.json').read_text()).get('hubAuthors',[]))
    validate(D,hub,lib)
    bad=[s['id'] for s in D['saints'] if s.get('author_id') in flagged]
    if bad:fail('flagged authors may not be featured as saints: '+', '.join(bad))
    table,coll=aliases(D['saints'])
    A={'note':'Normalized alias -> saint id. Built by tools/build_saints.py; exact keys only, no fuzzy matching. Keys in collisions map to several saints and are shown as "Did you mean...".','aliases':table,'collisions':coll}
    (ROOT/'data/saints-aliases.json').write_text(json.dumps(A,ensure_ascii=False,indent=1,sort_keys=True)+'\n')
    # compact browser copy: drop fields the UI does not need (sources stay)
    rt={'generated':D['generated'],'shelf_groups':D['shelf_groups'],'saints':D['saints'],'shelf':D['shelf'],'aliases':table,'collisions':coll}
    (ROOT/'data/saints.js').write_text('window.SAINTS_DATA='+json.dumps(rt,ensure_ascii=False,separators=(',',':'))+';\n')
    print(len(D['saints']),'saints;',len(table),'alias keys;',len(coll),'collisions;',len(D['shelf']),'shelf books')
if __name__=='__main__':main()
