#!/usr/bin/env python3
"""Give each Isidore Index author (hub.isidore {n, f}) the author name exactly as its books carry it (v18.2).

The A-Z names (`n`) come from isidore.co folder names, which drop letters a file system dislikes: "Wojtyła" became
"Wojtyla", "Søren" became "Soren", and "1248?-1309" became "1248_-1309" (shown as "1248.-1309"). An Index search for
such a name finds nothing. This tool looks at the books filed in each folder (data/books.json) and, where the books'
author string differs from `n`, stores it as `a`. Links to an author's Index search (the A-Z tab, author pages, the
open data) use `a` when present, so every link finds that author's books.  Run:  python3 tools/build_isidore_names.py
"""
import collections,json,re,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'));import hubio
LET=str.maketrans({'ł':'l','Ł':'L','ø':'o','Ø':'O','đ':'d','Đ':'D','ð':'d','Ð':'D','þ':'th','Þ':'Th','æ':'ae','Æ':'Ae','œ':'oe','Œ':'Oe','ß':'ss','ı':'i','ħ':'h','Ħ':'H'})
def fold(s):
    s=unicodedata.normalize('NFKD',str(s).translate(LET));s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',re.sub(r'[?_]','.',s)).strip().lower()
def main():
    d=json.loads((ROOT/'data/books.json').read_text());h=hubio.load()
    F=d['folders'];A=d['authors'];by=collections.defaultdict(list)
    for r in d['books']:by[F[r[8]]].append([A[i][0] for i in r[2]])
    changed=same=0
    for i in h['isidore']:
        i.pop('a',None);names=by.get(i['f']) or []
        cand=collections.Counter(x for L in names for x in L if fold(x)==fold(i['n']))
        if not cand:cand=collections.Counter(L[0] for L in names if L)
        best=cand.most_common(1)[0][0] if cand else i['n']
        if best!=i['n']:i['a']=best;changed+=1
        else:same+=1
    hubio.save(h);print(len(h['isidore']),'Isidore authors;',changed,'link by the books\' author name,',same,'unchanged')
if __name__=='__main__':main()
