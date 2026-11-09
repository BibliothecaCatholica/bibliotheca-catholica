#!/usr/bin/env python3
"""Affiliate purchase blocks for book pages (owner-approved preview, Business 2026-11-09). Part of `npm run build`.

Reads data/affiliates.js (the Bookshop.org affiliate ID, the TAN Books referral link, and the disclosure),
data/guide.js (edition-guide picks with verified ISBN-13s), and data/library.json, and writes
data/print-editions.json and data/print-editions.js (window.PRINT_EDITIONS). Both the static pages
(tools/build_static.py) and the app (scripts/library.js, app.js) insert the same pre-rendered HTML.

Rules (AGENTS.md, "Affiliate links"):
- Reading here stays primary: the block is a second, modest section below the reading editions.
- A Bookshop.org link appears only for an edition-guide pick with a valid ISBN-13 (never invented),
  as https://bookshop.org/a/<bookshopId>/<isbn13>. Ebook-only picks are left out.
- TAN Books gets one general "Browse TAN Books" link (the LeadDyno referral link); no claim that TAN
  sells a particular title. It is shown on classic Catholic works (tradition "Catholic tradition", not
  Reference or Magisterium, not a related writer's book) and on their authors' pages.
- Every block carries the affiliate disclosure and a link to /disclosure/. No Amazon. No analytics
  attributes: the existing outbound_click handler classifies the links (bookshop, affiliate).
"""
import html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=html.escape
ISBN=re.compile(r'97[89]\d{10}')
TAN_SKIP_CATEGORIES={'Reference','Magisterium'}

def affiliates():
    s=(ROOT/'data/affiliates.js').read_text(encoding='utf-8')
    bid=re.search(r"bookshopId:\s*'(\d+)'",s).group(1);assert bid=='130222','Bookshop id must be 130222'
    tan=re.search(r"tan:\s*\{\s*name:\s*'([^']+)',\s*url:\s*'([^']+)'",s[s.index('partners'):])
    assert tan and tan.group(2)=='https://lddy.no/1qbrw','TAN Books referral link must be https://lddy.no/1qbrw'
    d=re.search(r"disclosure:\s*'([^']*)'",s).group(1)
    assert not re.search(r'amazon\.|amzn\.',s.lower()),'no Amazon links'
    return bid,tan.group(1),tan.group(2),re.sub(r'^Affiliate disclosure:\s*','',d)

def jsvar(path,var):
    s=(ROOT/path).read_text(encoding='utf-8');p='window.%s='%var;return json.loads(s[s.index(p)+len(p):].rstrip().rstrip(';'))

def disclosure_html(text):
    return '<p class="disclosure small"><b>Affiliate disclosure:</b> '+E(text)+' <a href="/disclosure/">How our affiliate links work</a>.</p>'

def tan_html(name,url):
    return ('<p class="buy-tan"><a class="buy-b" href="'+E(url)+'" target="_blank" rel="noopener sponsored">Browse '+E(name)+' ↗</a> '
            '<span class="small">'+E(name)+' publishes Catholic classics in print. Search its catalog for this author or title.</span></p>')

def build():
    bid,tan_name,tan_url,disc=affiliates()
    lib=json.loads((ROOT/'data/library.json').read_text(encoding='utf-8'))
    guide=jsvar('data/guide.js','GUIDE_DATA')
    related={w for ra in lib.get('relatedAuthors',[]) for w in ra['workIds']}
    D=disclosure_html(disc)
    works,authors={},{}
    tan_works=[w['id'] for w in lib['works'] if w.get('tradition')=='Catholic tradition' and w['category'] not in TAN_SKIP_CATEGORIES and w['id'] not in related]
    for w in lib['works']:
        picks,seen,gids=[],set(),[]
        for ed in guide['editions']:
            if w['id'] not in (ed.get('workIds') or []):continue
            for p in ed.get('picks') or []:
                isbn=p.get('isbn') or ''
                if p.get('access')=='ebook' or not ISBN.fullmatch(isbn) or isbn in seen:continue
                seen.add(isbn);picks.append((ed,p))
                if ed['id'] not in gids:gids.append(ed['id'])
        tan=w['id'] in tan_works
        if not picks and not tan:continue
        h='<section class="buy-print"><h2>Where to buy print editions</h2><p class="small">Reading here is free. If you would like a printed copy, '
        if picks:
            g=[ed for ed in guide['editions'] if ed['id'] in gids]
            h+=('these editions come from our edition guide'+('s' if len(g)>1 else '')+' for '+', '.join('<a href="/editions/'+E(x['id'])+'/">'+E(x['t'])+'</a>' for x in g)+'. Check the translator and ISBN before you buy.</p><ul class="buy-list">')
            for ed,p in picks:
                h+=('<li><span class="buy-what">'+(E(p['lbl'])+': ' if p.get('lbl') else '')+E(p.get('tr') or ed['t'])+(' ('+E(p['pub'])+')' if p.get('pub') and p['pub'] not in (p.get('tr') or '') else '')+'. ISBN '+p['isbn']+'.</span> '
                    '<a class="buy-b bs" href="https://bookshop.org/a/'+bid+'/'+p['isbn']+'" target="_blank" rel="noopener sponsored">Bookshop.org ↗</a></li>')
            h+='</ul>'
        else:
            h+='you can find one from a Catholic publisher.</p>'
        if tan:h+=tan_html(tan_name,tan_url)
        h+=D+'</section>'
        works[w['id']]={'html':h,'bookshop':len(picks),'tan':tan}
    tan_authors=sorted({w['authorId'] for w in lib['works'] if w['id'] in tan_works and w.get('authorId')})
    for aid in tan_authors:
        authors[aid]={'html':'<section class="buy-print"><h2>Where to buy print editions</h2>'+tan_html(tan_name,tan_url)+D+'</section>'}
    return {'note':'Generated by tools/build_print_editions.py from data/affiliates.js, data/guide.js, and data/library.json. Do not edit.',
            'bookshopId':bid,'tanUrl':tan_url,'disclosure':D,'works':works,'authors':authors}

def main():
    out=build()
    j=json.dumps(out,ensure_ascii=False,indent=1,sort_keys=True)
    (ROOT/'data/print-editions.json').write_text(j+'\n',encoding='utf-8')
    (ROOT/'data/print-editions.js').write_text('window.PRINT_EDITIONS='+json.dumps(out,ensure_ascii=False,separators=(',',':'),sort_keys=True)+';\n',encoding='utf-8')
    print('print editions:',len(out['works']),'work pages,',sum(1 for v in out['works'].values() if v['bookshop']),'with Bookshop links ('+str(sum(v['bookshop'] for v in out['works'].values()))+' links),',
          sum(1 for v in out['works'].values() if v['tan']),'with TAN Books;',len(out['authors']),'author pages with TAN Books')
if __name__=='__main__':main()
