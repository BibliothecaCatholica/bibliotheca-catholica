#!/usr/bin/env python3
"""Validate the chapter and story maps in tools/text_pages.py and write data/text-pages.json/.js.

For each hosted edition: the file's SHA-256 must equal the edition's `sha256` in data/library.json,
every heading must occur exactly once after `start_after`, in order, and each part's first and last
paragraphs must start and end with the words Research mapped. A part runs from its heading block to
the block before the next heading (a bare Roman numeral printed above a heading is left out); the
last part ends before the Project Gutenberg (or hosted-text) END marker. Part of `npm run build`.

    python3 tools/build_text_pages.py
"""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import text_pages as TP
from reader_formatting import structure_for
SIZE=35  # reader section size (read() in scripts/library.js)
SLUG=re.compile(r'^\d\d-[a-z0-9]+(?:-[a-z0-9]+)*$')
def split_text(raw):
    """Same as splitText() in scripts/library.js: blank-line blocks, trimmed, empties dropped."""
    return [p.strip() for p in re.split(r'\n\s*\n',raw.replace('\r','')) if p.strip()]
def norm(s):return re.sub(r'\s+',' ',s).strip().casefold()
def words(s):return len(re.sub(r'[_\[\]]',' ',s).split())
# Part D, "Beautiful editions" (owner brief; Orthodoxy pilot, November 14-15, 2026): editions presented as designed
# books: a title-page work page (facts line, three choices, About this edition), chapter openers and endings.
PART_D={
    'orthodoxy':{'about':'Project Gutenberg #130: the 1908 first edition text, with Chesterton’s Preface. The nine chapters and the title page follow Gutenberg’s own HTML for the same eBook, matched word for word with the hosted text; no words were changed.'},
    # Batch 1 (November 15, 2026). Each sentence restates the edition's own record in data/library.json and its map.
    'story-of-a-soul':{'about':'Project Gutenberg #16772: the Thomas N. Taylor translation, with the additional writings and sayings of his edition. The eleven chapters of the autobiography follow Gutenberg’s own HTML for the same eBook, matched with the hosted text; no words were changed.'},
    'innocence-father-brown':{'about':'Project Gutenberg #204: the first Father Brown collection, twelve stories. Story divisions follow the site’s map of the hosted text; no words were changed.'},
    'wisdom-father-brown':{'about':'Project Gutenberg #223: the second collection, first published in 1914 (London: Cassell), twelve stories. Story divisions follow the site’s map of the hosted text; no words were changed.'},
    'secret-father-brown':{'about':'Project Gutenberg #70175: first published in 1927 (London: Cassell and Company), eight stories between an opening and a closing frame story. Story divisions follow the site’s map of the hosted text; no words were changed.'},
    'incredulity-father-brown':{'about':'The Standard Ebooks text (CC0), corrected to the wording of the 1926 Cassell printings, eight stories. Each correction is listed in the edition’s provenance record. Story divisions follow the site’s map of the hosted text.'},
}
def part_d(wid,d):
    """Facts for the title page: total words of the parts (rounded to the thousand) and reading time at 230 words a minute."""
    wc=sum(x['words'] for x in d['items'])
    return dict(PART_D[wid],words=wc,minutes=round(wc/230))
def items_for(wid,spec,B):
    """The parts of one mapped work: heading, body range, and words (also used by tools/structure_text.py map mode)."""
    end=next(i for i,b in enumerate(B) if re.search(r'\*\*\* ?END OF (THE |THIS )?(PROJECT GUTENBERG|HOSTED TEXT)',b,re.I))
    if spec.get('end_before'):end=next(i for i in range(len(B)) if norm(B[i])==norm(spec['end_before']))  # back matter after the last part
    at=next(i for i,b in enumerate(B) if norm(b)==norm(spec['start_after']))
    heads=[]
    for slug,num,title,head,first,last in spec['parts']:
        assert SLUG.match(slug),slug
        hits=[i for i in range(at+1,end) if norm(B[i])==norm(head)]
        assert len(hits)==1,(wid,slug,'heading must occur once',hits)
        assert not heads or hits[0]>heads[-1],(wid,slug,'out of order')
        heads.append(hits[0])
    items=[]
    for k,(slug,num,title,head,first,last) in enumerate(spec['parts']):
        h=heads[k];stop=(heads[k+1] if k+1<len(heads) else end)-1
        while stop>h and re.fullmatch(r'[IVXLC]+\.?',B[stop]):stop-=1  # a numeral printed above the next heading
        body=list(range(h+1,stop+1))
        assert body,(wid,slug,'empty part')
        assert norm(B[body[0]]).startswith(norm(first)),(wid,slug,'first words do not match',B[body[0]][:80])
        assert norm(B[body[-1]]).endswith(norm(last)),(wid,slug,'last words do not match',B[body[-1]][-80:])
        items.append(dict(slug=slug,num=num,title=title,heading=h,start=body[0],end=body[-1],section=h//SIZE,
                          words=sum(words(B[i]) for i in body),firstWords=' '.join(re.sub(r'[_]','',B[body[0]]).split()[:12])))
    return items
def build():
    lib=json.loads((ROOT/'data/library.json').read_text());works={w['id']:w for w in lib['works']}
    flags=json.loads((ROOT/'data/editorial-flags.json').read_text())
    out={}
    for wid,spec in TP.WORKS.items():
        w=works[wid];e=next(x for x in w['editions'] if x['id']==spec['edition'])
        assert e.get('text') and e.get('sha256'),(wid,'not a hosted edition')
        src=json.loads((ROOT/('data/sources/'+e['id']+'.json')).read_text())
        # Gutenberg editions, or (2026-11-09, The Incredulity of Father Brown) a public-domain text with a provenance record
        assert 'gutenberg.org' in e['source'] or src.get('kind')=='public-domain-text',(wid,'chapter pages need a Gutenberg or provenance-checked edition')
        assert not w.get('authorId') or w['authorId'] not in flags.get('hubAuthors',[]),wid
        raw=(ROOT/e['text']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'],(wid,'text changed')
        B=split_text(raw.decode('utf-8'))
        items=items_for(wid,spec,B)
        assert len({i['slug'] for i in items})==len(items),wid
        st=structure_for(e)  # structured-text pilot (tools/structure_text.py): roles, only for this exact TXT
        if st:
            S=json.loads((ROOT/st['source']).read_text())
            assert [(c['heading'],c['start'],c['end']) for c in S['chapters']]==[(x['heading'],x['start'],x['end']) for x in items],(wid,'structure and chapter map disagree')
        out[wid]=dict(**({'partD':part_d(wid,{'items':items})} if wid in PART_D else {}),edition=e['id'],kind=spec['kind'],editionLine=spec.get('edition_line',''),noun=spec['noun'],nouns=spec['nouns'],sha256=e['sha256'],blocks=len(B),items=items,**({'structure':st} if st else {}))
    return out
def main():
    data=build()
    (ROOT/'data/text-pages.json').write_text(json.dumps({'note':'Generated by tools/build_text_pages.py from tools/text_pages.py; block indexes are splitText() blocks of the hosted file.','works':data},ensure_ascii=False,indent=1)+'\n')
    slim={wid:dict({'edition':d['edition'],'k':d['kind'],'n':d['nouns'],'i':[[x['slug'],x['num'],x['title'],x['heading']]+([x['end']] if d.get('partD') else []) for x in d['items']]},**({'d':d['partD']} if d.get('partD') else {}),**({'s':dict({'sha256':d['structure']['sha256'],'r':d['structure']['roles']},**({'f':d['structure']['front']} if d['structure'].get('front') else {}))} if d.get('structure') else {})) for wid,d in data.items()}
    (ROOT/'data/text-pages.js').write_text('window.TEXT_PAGES='+json.dumps(slim,ensure_ascii=False,separators=(',',':'))+';\n')
    print('text pages:',', '.join('%s %d'%(k,len(v['items'])) for k,v in data.items()))
if __name__=='__main__':main()
