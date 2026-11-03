"""Load/save the hub snapshot. data/catholic-hub.json is the source of truth; save() also writes the three browser files:

  data/data.js            window.HUB_DATA     core, loaded on every page: eras, resources, and slim authors (no detail
                                              fields), plus isidoreCount, detailV, and isidoreV (content tokens)
  data/authors-detail.js  window.HUB_DETAIL   {by:{id:{detail fields, isoRec}}}: loaded on demand by the author page and timeline
                                              (isoRec = the author's Isidore Index name record, so the author page needs no name list)
  data/isidore-authors.js window.HUB_ISIDORE  the Isidore Index author names: loaded on demand by search and the A-Z list

merged() rebuilds the full snapshot from the three files (tests/test_catalog.py checks it equals the JSON)."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# author fields only the author page (and the timeline's source collections) read
DETAIL=('extract','links','intro','books','media','qidWork','isidoreFolder')
def load():return json.loads((ROOT/'data/catholic-hub.json').read_text())
def dumps(o):return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def split(h):
    core={k:v for k,v in h.items() if k not in('authors','isidore')};authors=[];by={};iso_by={i['f']:i for i in h.get('isidore',[])}
    for a in h['authors']:
        c={};d={}
        for k,v in a.items():(d if k in DETAIL else c)[k]=v
        cr=a.get('imgCredit')
        if cr is not None:  # list thumbnails need only img + pd; the full credit (and non-pd img) waits for the author page
            d['imgCredit']=cr;c.pop('imgCredit',None)
            if cr.get('pd'):c['imgCredit']={'pd':True}
            else:
                if 'img' in c:d['img']=c.pop('img')
        if a.get('isidoreFolder') in iso_by:d['isoRec']=iso_by[a['isidoreFolder']]  # the author page needs only this file, not the 190 KB name list
        if d:by[a['id']]=d
        authors.append(c)
    det=dumps({'by':by});iso=dumps(h.get('isidore',[]))
    tok=lambda s:hashlib.sha1(s.encode()).hexdigest()[:10]
    core['authors']=authors;core['isidoreCount']=len(h.get('isidore',[]));core['detailV']=tok(det);core['isidoreV']=tok(iso)
    return core,det,iso
def save(h):
    (ROOT/'data/catholic-hub.json').write_text(dumps(h)+'\n')
    core,det,iso=split(h)
    (ROOT/'data/data.js').write_text('window.HUB_DATA='+dumps(core)+';\n')
    (ROOT/'data/authors-detail.js').write_text('window.HUB_DETAIL='+det+';\n')
    (ROOT/'data/isidore-authors.js').write_text('window.HUB_ISIDORE='+iso+';\n')
def _js(p):s=(ROOT/p).read_text();return json.loads(s[s.index('=')+1:].strip().rstrip(';'))
def merged():
    """The full snapshot rebuilt from the three browser files, keys in the JSON's order."""
    core=_js('data/data.js');det=_js('data/authors-detail.js')['by'];iso=_js('data/isidore-authors.js')
    src=load();out={}
    for k in src:
        if k=='authors':
            L=[]
            for a,o in zip(core['authors'],src['authors']):
                m=dict(a);m.update(det.get(a['id'],{}));m.pop('isoRec',None);L.append({k2:m[k2] for k2 in o if k2 in m} if set(m)==set(o) else m)
            out[k]=L
        elif k=='isidore':out[k]=iso
        else:out[k]=core.get(k)
    return out
if __name__=='__main__':save(load());print('wrote data/data.js, data/authors-detail.js, data/isidore-authors.js')
