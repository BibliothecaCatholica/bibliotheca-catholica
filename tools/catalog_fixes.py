"""Hand-checked corrections to isidore.co catalog author names (v18.3).

The Isidore Index shows catalog names as isidore.co supplies them. A name here is corrected only when it carries a
clear factual error, checked against a reliable source. The isidore.co folder name (`isidoreFolder`, `hub.isidore` `f`,
and the open data `folder` column) is left as it is, because it is the folder's actual name on isidore.co.

Used by tools/build_books.py (book author strings in data/books.json) and tools/build_isidore_names.py (`hub.isidore` `n`).
"""
CATALOG_NAME_FIXES={
    # isidore.co gives St Benedict's dates (480-547). Gregory the Great was born c. 540 and died 12 March 604
    # (Catholic Encyclopedia, "Pope St. Gregory I ('the Great')", https://www.newadvent.org/cathen/06780a.htm).
    'Gregory the Great, Pope St., O.S.B. (480-547)':'Gregory the Great, Pope St., O.S.B. (c. 540-604)',
}
def fix(name):return CATALOG_NAME_FIXES.get(name,name)
