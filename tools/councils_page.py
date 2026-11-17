"""The /councils/ page: the twenty-one ecumenical councils in order (data/councils.json).

Each row gives the council's name, years, a one-line summary written for this site, and where to read it:
"Read on this site" when the council's `work` has a hosted edition in data/library.json, otherwise the
outbound links recorded in the data. tools/build_static.py writes the page; app.js keeps it static
(staticOnly), so there is no second renderer. Also used for the Church Documents link (MAGISTERIUM_LINK).
"""
import html,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=html.escape
TITLE='The Ecumenical Councils'
DESC='The twenty-one ecumenical councils of the Catholic Church, from Nicaea in 325 to Vatican II, with what each one settled and where to read its texts.'
LEDE='All twenty-one ecumenical councils of the Catholic Church, from Nicaea to the Second Vatican Council, in order, with what each settled and where to read it.'
# The link at the top of /magisterium/ (static page and app.js section(); tests/test_councils.py keeps them in step)
MAGISTERIUM_LINK='<p class="councils-link"><a class="btn ghost" href="/councils/">The 21 Ecumenical Councils</a> <span class="small">From Nicaea to Vatican II, in order, with what each one settled.</span></p>'
def load():return json.loads((ROOT/'data/councils.json').read_text())
def hosted_works(lib):
    """Work ids with at least one edition readable here."""
    return {w['id'] for w in lib['works'] if any(e.get('text') for e in w['editions'])}
def ext(url,label):return '<a href="'+E(url)+'" target="_blank" rel="noopener">'+E(label)+' ↗</a>'
def row(c,lib,hosted,libw):
    acts=[]
    if c.get('work') and c['work'] in hosted:
        acts.append('<a class="council-read" href="/work/'+E(c['work'])+'/">Read on this site</a>')
    else:
        acts+=[ext(L['url'],L['label']) for L in c.get('links',[])]
    sw=[w for w in c.get('siteWorks',[]) if w in libw]
    more=('<p class="council-more">In the reading room: '+', '.join('<a href="/work/'+E(w)+'/">'+E(libw[w]['title'])+'</a>' for w in sw)+'</p>') if sw else ''
    return ('<li class="council" id="'+E(c['id'])+'"><span class="council-n" aria-hidden="true">'+str(c['n'])+'</span><div class="council-body">'
            '<h3><span class="sr-only">'+str(c['n'])+'. </span>'+E(c['name'])+' <span class="council-years">'+E(c['years'])+'</span></h3>'
            '<p class="council-sum">'+E(c['summary'])+'</p><p class="council-acts">'+' · '.join(acts)+'</p>'+more+'</div></li>')
def body(lib=None):
    lib=lib or json.loads((ROOT/'data/library.json').read_text())
    D=load();hosted=hosted_works(lib);libw={w['id']:w for w in lib['works']}
    h='<div class="page-head"><div class="eyebrow">Church Documents</div><h1>'+E(TITLE)+'</h1><p class="lede">'+E(LEDE)+'</p></div>'
    # no in-page #anchor links: app.js reads location.hash as the route
    for e in D['eras']:
        rows=[c for c in D['councils'] if c['era']==e['id']]
        h+='<section class="council-era" aria-labelledby="era-'+E(e['id'])+'"><h2 id="era-'+E(e['id'])+'">'+E(e['t'])+' <span class="council-years">'+E(e['span'])+'</span></h2><ol class="rows council-list" start="'+str(rows[0]['n'])+'">'+''.join(row(c,lib,hosted,libw) for c in rows)+'</ol></section>'
    h+=('<p class="council-note small">Summaries are our own, in brief. For the authoritative text of any council, '
        '<a href="https://www.vatican.va/content/vatican/en.html" target="_blank" rel="noopener">vatican.va</a> and the scholarly editions are the sources; '
        'links marked ↗ open other sites. More Church documents: <a href="/magisterium/">Church Documents</a>.</p>')
    return h
