#!/usr/bin/env python3
"""Editorial flags for Isidore Index records (Fidelity & Editorial Policy, #/policy).

Records are NOT removed: a flagged record keeps its page, catalogue data, and isidore.co links, but it
gets a factual context note and the Dignitatis Humanae disclaimer, a `noindex` robots tag, and it is
never featured (home page, reading lists, reading room, "Read here" matches, static pages, sitemap).

Writes data/editorial-flags.json and data/editorial-flags.js. Re-run tools/build_open_data.py and
tools/build_static.py afterwards. Sources: research/site-improvements.md §9.3 and social-listening.json.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DH_URL='https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651207_dignitatis-humanae_en.html'
# Checked word for word against DH_URL on 2026-10-21 (§1 and §3 of the English text on vatican.va).
DISCLAIMER=[
 {'text':'The truth cannot impose itself except by virtue of its own truth, as it makes its entrance into the mind at once quietly and with power.','cite':'Vatican II, Dignitatis Humanae 1'},
 {'text':'The inquiry is to be free, carried on with the aid of teaching or instruction, communication and dialogue, in the course of which men explain to one another the truth they have discovered, or think they have discovered, in order thus to assist one another in the quest for truth.','cite':'Dignitatis Humanae 3'},
]
CATEGORIES={
 'antisemitic-content':'Antisemitic content',
 'polemical-historical':'Polemical history (conspiracy theory)',
 'sedevacantist-position':'Sedevacantist position',
 'author-context':'Author context',
}
FAHEY=('Fr. Denis Fahey, C.S.Sp. (1883–1954), an Irish priest, wrote on the Social Kingship of Christ. '
       'For scholarly context on his writing about Jews and Freemasonry, see Mary Christine Athans, '
       '“The Coughlin–Fahey Connection” (1991).')
JONES='E. Michael Jones (born 1948), editor of Culture Wars magazine, is widely criticized for antisemitic writing.'
DELASSUS=('Mgr Henri Delassus (1836–1921), a French priest and editor, wrote polemical histories that present modern '
          'history as an anti-Christian conspiracy of Freemasons and Jews. Read them as period documents, not as reliable history.')
SEDE=('Sedevacantism is the claim that the popes since the Second Vatican Council have not been true popes. '
      'The Catholic Church does not accept this position.')
BOOKS={}
def flag(ids,cat,note):
    for i in ids:BOOKS[str(i)]={'flag':cat,'note':note}
flag([3895],'antisemitic-content','The Protocols of the Learned Elders of Zion is a fabricated text, first published in Russia in 1903, that purports to record a Jewish plan for world domination. It was exposed as a forgery in 1921 and has been used to justify the persecution of Jews. It is catalogued here only as a historical document.')
flag([2967],'antisemitic-content','The Plot Against the Church, published in 1962 under the pseudonym “Maurice Pinay” and circulated to bishops during the Second Vatican Council, presents an antisemitic conspiracy theory of Church history. It is catalogued here only as a historical document.')
flag([9089,4588,9438,4228,9434,9088,9085],'antisemitic-content',FAHEY+' This work presents Jewish and Masonic conspiracy claims.')
flag([9726,9087,9433,4241,9086],'author-context',FAHEY)
flag([6062,9728,5001,7439,5004,4686,4853,7012,5003,5011],'antisemitic-content',JONES+' This title concerns Jews or Judaism in that context.')
flag([5006,5016,7459,5021,5015,5020,8465,6332,5010,6725,5013,8774,5000,5009,5018,5007,9562,5002],'author-context',JONES)
flag([10258,10616,5475,5477,5478,10257],'polemical-historical',DELASSUS)
flag([5476],'author-context',DELASSUS)
flag([9057],'sedevacantist-position','Patrick Henry Omlor wrote from a sedevacantist position. '+SEDE)
flag([9297,8929],'sedevacantist-position','Fr. Anthony Cekada (1951–2020) wrote from a sedevacantist position. '+SEDE)
flag([7783],'sedevacantist-position','Donald J. Sanborn writes from a sedevacantist position. '+SEDE)
flag([6354],'sedevacantist-position','John Lane writes from a sedevacantist position. '+SEDE)
MAIL='micahwatson@bibliothecacatholica.com'
def policy_html(counts,total):
    q=''.join('<blockquote class="dh-quote"><p>“'+x['text']+'”</p><footer>('+x['cite']+')</footer></blockquote>' for x in DISCLAIMER)
    cats=''.join('<li><b>'+CATEGORIES[k]+'</b> ('+str(counts.get(k,0))+' records)</li>' for k in CATEGORIES)
    return ('<div class="page-head"><div class="eyebrow">Fides et ratio</div><h1>Fidelity &amp; Editorial Policy</h1>'
     '<p class="lede">Bibliotheca Catholica is an independent index that intends to be faithful to the Magisterium of the Catholic Church. '
     'It points readers to the Church’s own documents, to the Fathers and Doctors, and to the great Catholic digital libraries.</p></div>'
     '<section class="panel policy"><h2>Listing is not endorsement</h2>'
     '<p>The Isidore Index mirrors the catalogue of a third-party library, <a href="https://isidore.co/calibre" target="_blank" rel="noopener">isidore.co</a>, with its records imported as supplied. '
     'A book’s presence in the Index, in search results, or in the open data is not a recommendation, an endorsement, or a judgment that it is free of error. '
     'Our own recommendations are the hand-picked shelves: <a href="#/library">Discover &amp; Read</a>, <a href="#/editions">Editions &amp; Translations</a>, and the <a href="#/reading">Reading Lists</a>.</p>'
     '<h2>Context notes on flagged records</h2>'
     '<p>Some records in the Index contain antisemitic conspiracy claims, conspiracy-theory history, or positions the Church does not accept, such as sedevacantism. '
     'We do not remove them: they remain available for historical study and research, and files stay on isidore.co. Instead, each flagged record carries a short, factual context note, this policy’s disclaimer, and a link back to this page. '
     'Flagged records are never featured on the home page, in reading lists, edition guides, or recommendations, or in the reading room, and their pages ask search engines not to index them.</p>'
     '<p>Categories currently in use ('+str(total)+' records):</p><ul>'+cats+'</ul>'
     '<p>“Author context” marks other works by an author whose writing is flagged elsewhere; it is not a judgment that every such work contains the same claims.</p>'
     '<h2>Why we keep them, with this disclaimer</h2>'+q+
     '<p class="small">Source: <a href="'+DH_URL+'" target="_blank" rel="noopener">Second Vatican Council, Declaration on Religious Freedom, Dignitatis Humanae (7 December 1965), vatican.va</a>.</p>'
     '<h2>Report a concern</h2>'
     '<p>If you think a record needs a context note, has the wrong one, or should not be listed, or if you hold the rights to a work and want a listing changed, write to '
     '<a href="mailto:'+MAIL+'?subject=Editorial%20concern">'+MAIL+'</a>. Please include the book’s Index number or page link.</p>'
     '<h2 id="privacy">Privacy</h2>'
     '<p>This site uses Google Analytics to count visits and understand which pages are used. Google may set cookies in your browser to do this. '
     'The site itself has no accounts and does not collect your name, email address, or other personal information. '
     'See <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">how Google uses information from sites that use its services</a>.</p>'
     '</section>')
def main():
    books=json.loads((ROOT/'data/books.json').read_text());have={str(b[0]):b for b in books['books']}
    missing=[i for i in BOOKS if i not in have];assert not missing,missing
    out=dict(generated='2026-10-21',policy='#/policy',policy_url='https://bibliothecacatholica.com/policy/',
             note='Listing is not endorsement. Flagged records stay in the Index with a context note; they are never featured and carry noindex.',
             disclaimer=dict(quotes=DISCLAIMER,source=DH_URL),categories=CATEGORIES,
             policy_html=policy_html(__import__('collections').Counter(v['flag'] for v in BOOKS.values()),len(BOOKS)),
             books={k:dict(v,title=have[k][1]) for k,v in sorted(BOOKS.items(),key=lambda x:int(x[0]))},hubAuthors=[])
    s=json.dumps(out,ensure_ascii=False,indent=1)
    (ROOT/'data/editorial-flags.json').write_text(s+'\n');(ROOT/'data/editorial-flags.js').write_text('window.EDITORIAL_FLAGS='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
    from collections import Counter;c=Counter(v['flag'] for v in BOOKS.values());print(len(BOOKS),'flagged',dict(c))
if __name__=='__main__':main()
