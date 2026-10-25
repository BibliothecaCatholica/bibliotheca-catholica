#!/usr/bin/env python3
"""Pre-render crawlable static entry pages for the hash-routed SPA (no build step needed to serve the site).

For every author, reading-room work, edition guide, reading list, and top-level section this writes
<route>/index.html: a copy of index.html with the route's own <title>, description, canonical URL,
Open Graph and Twitter tags, and real content HTML inside <main>, plus `window.BC_BOOT='<route>'` so
app.js boots straight into the same view.  It also writes sitemap.xml, robots.txt, and 404.html
(which forwards /author/x style paths that have no static page to /#/author/x).

Isidore Index book pages are not pre-rendered, and nothing listed in data/editorial-flags.json is
pre-rendered or put in the sitemap.  Run after data changes and commit the output:
    python3 tools/build_static.py
"""
import html,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SITE='https://bibliothecacatholica.com/';E=html.escape
def jsvar(path,var):
    s=(ROOT/path).read_text();p='window.%s='%var;return json.loads(s[s.index(p)+len(p):].rstrip().rstrip(';'))
SECTIONS={
 'library':('Discover & Read','Selected free reading editions of Catholic classics, with source editions, credits, and rights notes, readable here or downloadable.'),
 'related':('Related Christian writers','Christian writers outside the Catholic communion who are often read alongside the Catholic tradition, such as C. S. Lewis.'),
 'authors':('Catholic Authors','Hundreds of Catholic authors from the Apostolic Fathers to today, with dates, eras, short biographies, and links to their works online.'),
 'doctors':('Doctors of the Church','The Doctors of the Church, with their principal works and where to read them free online.'),
 'timeline':('Timeline of Saints & Writers','Saints and Catholic writers through the centuries, linked to their writings, biographies, reading editions, and sources.'),
 'scripture':('Sacred Scripture','Bibles in English, Latin, and the original languages; commentaries ancient and modern; daily readings.'),
 'magisterium':('Church Documents','Catechisms, ecumenical councils, papal encyclicals, canon law, and doctrinal documents, straight from the source.'),
 'references':('Reference Works','Encyclopedias, dictionaries, the Summa, patristic collections, liturgy, chant, saints, and apologetics.'),
 'media':('Podcasts & Media','The major Catholic podcasts, YouTube channels, radio and TV networks, and news outlets.'),
 'libraries':('Digital Libraries','The great Catholic digital libraries, archives, learning institutes, publishers, and homeschool programs.'),
 'prayers':('Prayers & Devotions','The common prayers of the Church, the Rosary, daily readings, the saint of the day, prayer apps, and parish finders.'),
 'rare':('Rare & Obscure','Rare and lesser-known Catholic books and manuscripts that are freely available online.'),
 'projects':('Projects','Open Catholic software, data, and digitization projects: liturgical calendars, Bible APIs, breviaries, and more.'),
 'isidore':('Ebooks & PDFs: the Isidore Index','A searchable index of more than 6,600 books in the St. Isidore e-book library (isidore.co), with formats, rights badges, and links to isidore.co.'),
 'data':('Open Data','The open data behind Bibliotheca Catholica: authors, resources, editions, and the Isidore catalogue, free to reuse.'),
 'support':('Support the Library','How to support Bibliotheca Catholica, an independent, ad-free index of Catholic sources.'),
 'editions':('Editions & Translations','Read a free edition, compare translations, or choose a print copy of the Catholic classics, with EPUB options and recommended picks.'),
 'reading':('Reading Lists','Curated Catholic reading lists: start here, apologetics, spiritual classics, fiction, philosophy, Church history, and more.'),
 'substacks':('Catholic Substacks','Catholic writers and newsletters on Substack, with recent posts.'),
 'saints':('Saints & Hagiography','A sourced guide to 185 saints: feast days as Vatican News lists them, the writers in the library, saints of legend, and the old lives of the saints.'),
}
# --- Saints & Hagiography (v15): see docs/SAINTS.md ---------------------------------------------
MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December']
FLAGL={'tradition':'Tradition and legend','tradition-with-historical-core':'Historical core, later legend','angel':'Archangel'}
def s_date(md):m,d=md.split('-');return str(int(d))+' '+MONTHS[int(m)-1]
def s_status(s):return {'archangel':'Archangel','saint':'Saint','blessed':'Blessed','venerable':'Venerable'}.get(s['status']['value'],'Status not recorded')
def s_years(s):  # mirrors years() in scripts/saints.js
    f=lambda y:str(-y)+' BC' if y<0 else str(y)
    b=s['born']['year'] if s.get('born') else None;d=s['died']['year'] if s.get('died') else None
    c='c. ' if d is not None and d<1000 else ''
    if b is not None and d is not None:return c+f(b)+'–'+f(d)
    if d is not None:return 'd. '+c+f(d)
    return 'b. '+f(b) if b is not None else ''
def s_vn(s):return ', '.join(s_date(v['date']) for v in s['feasts']['vatican_news'])
def s_facts(s):
    """One factual line built only from the spec's sourced fields (no prose copied from anywhere)."""
    t=s_status(s)+(' ('+s_years(s)+', Wikidata)' if s_years(s) else '')
    if s['feasts']['vatican_news']:t+='. Vatican News “Saint of the day”: '+s_vn(s)
    if s.get('historicity'):t+='. '+FLAGL[s['historicity']['flag']]+': '+s['historicity']['note'].rstrip('.')
    return t+'.'
def load_flags():
    p=ROOT/'data/editorial-flags.json'
    if not p.exists():return {'books':{},'hubAuthors':[]}
    return json.loads(p.read_text())
def ga_tag(tpl):
    m=re.search(r'<!-- Google tag \(gtag\.js\) -->.*?</script>\n<script>.*?</script>\n',tpl,flags=re.S)
    assert m and tpl.count('googletagmanager.com/gtag/js')==1,'index.html must carry exactly one Google tag right after <head>'
    return m.group(0)
def page(tpl,route,title,desc,body,noindex=False):
    url=SITE+(route+'/' if route else '');t=E(title);d=E(desc)
    s=tpl
    s=s.replace('<meta charset="utf-8">','<meta charset="utf-8">\n<base href="/">',1)
    sub=lambda pat,rep,s:re.sub(pat,lambda m:rep,s,count=1,flags=re.S)
    s=sub(r'<title>.*?</title>','<title>'+t+'</title>',s)
    s=sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+d+'">',s)
    s=sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="'+url+'">',s)
    if noindex:s=s.replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,follow">',1)
    for prop,val in (('og:title',t),('og:description',d),('og:url',url)):
        s=sub(r'<meta property="%s" content="[^"]*">'%prop,'<meta property="%s" content="%s">'%(prop,val),s)
    for nm,val in (('twitter:title',t),('twitter:description',d)):
        s=sub(r'<meta name="%s" content="[^"]*">'%nm,'<meta name="%s" content="%s">'%(nm,val),s)
    s=sub(r'<main id="main" tabindex="-1">.*?</main>','<main id="main" tabindex="-1"><div class="static-prerender">'+body+'</div></main>',s)
    s=re.sub(r'<script src="data/data\.js(\?[^"]*)?"></script>',lambda m:'<script>window.BC_BOOT='+json.dumps(route)+'</script>\n'+m.group(0),s,count=1)
    assert 'window.BC_BOOT' in s,'data/data.js script tag not found in index.html'
    return s
def a(href,label,ext=False):
    return '<a href="'+E(href)+'"'+(' target="_blank" rel="noopener"' if ext else '')+'>'+E(label)+'</a>'
def years(au):
    b,d=au.get('born'),au.get('died')
    f=lambda y:(str(-y)+' BC' if y<0 else str(y)) if isinstance(y,int) else ''
    return ' ('+f(b)+'–'+f(d)+')' if (b or d) else ''
def main():
    tpl=(ROOT/'index.html').read_text();global GA_TAG;GA_TAG=ga_tag(tpl);hub=json.loads((ROOT/'data/catholic-hub.json').read_text())
    lib=json.loads((ROOT/'data/library.json').read_text());guide=jsvar('data/guide.js','GUIDE_DATA');flags=load_flags()
    skip_auth=set(flags.get('hubAuthors',[]))
    eras={e['id']:e['label'] for e in hub['eras']}
    out={}  # route -> html
    SD=json.loads((ROOT/'data/saints.json').read_text());saints=SD['saints']
    saints_by_author={x['author_id']:x for x in saints if x['tier']==1 and x.get('author_id')}
    libw={w['id']:w for w in lib['works']}
    head=lambda eyebrow,h1,lede:'<div class="page-head"><div class="eyebrow">'+E(eyebrow)+'</div><h1>'+E(h1)+'</h1><p class="lede">'+E(lede)+'</p></div>'
    authors=[x for x in hub['authors'] if x['id'] not in skip_auth]
    for au in authors:
        desc=au.get('desc') or au.get('wikiDesc') or ''
        lede=desc+(' '+au['extract'] if au.get('extract') and au['extract'] not in desc else '')
        works=''.join('<li>'+a(w['url'],w['title'],True)+'</li>' for w in au.get('works') or [] if w.get('url'))
        mine=[w for w in lib['works'] if w.get('authorId')==au['id']]
        body=head(eras.get(au.get('era'),'Catholic author'),au['name']+years(au),lede)+(('<h2>Read here</h2><ul>'+''.join('<li>'+a('/work/'+w['id']+'/',w['title'])+'</li>' for w in mine)+'</ul>') if mine else '')+(('<h2>Works online</h2><ul>'+works+'</ul>') if works else '')+'<p>'+a('/authors/','All authors')+'</p>'
        sa=saints_by_author.get(au['id'])
        if sa:body=body.replace('<p>'+a('/authors/','All authors')+'</p>','<h2>Saint</h2><p>'+E(s_facts(sa))+' '+a('/saints/','Saints & Hagiography')+'</p><p>'+a('/authors/','All authors')+'</p>')
        out['author/'+au['id']]=(au['name']+' — Bibliotheca Catholica',(desc or au['name']+', Catholic author: biography and works online.')[:300],body)
    for w in lib['works']:
        eds=''.join('<li>'+E(e['label'])+(' · '+a('/#/read/'+w['id']+'/'+e['id'],'Read here') if e.get('text') else '')+' · '+a(e['source'],'Source',True)+'</li>' for e in w['editions'])
        d=w.get('description') or (w['title']+' by '+w['author']+': free reading edition with source, credits, and rights notes.')
        body=head(w['category']+' · '+w['tradition'],w['title'],w['author']+'. '+d)+'<h2>Reading editions &amp; sources</h2><ul>'+eds+'</ul><p>'+a('/library/','Selected library')+'</p>'
        out['work/'+w['id']]=(w['title']+' — Bibliotheca Catholica',d[:300],body)
    for ed in guide['editions']:
        picks=''.join('<li><b>'+E(p.get('lbl',''))+':</b> '+E(p.get('tr',''))+(' ('+E(p['pub'])+')' if p.get('pub') else '')+'</li>' for p in ed.get('picks',[]))
        body=head('Editions & Translations · '+ed.get('cat',''),ed['t'],(ed.get('a')+'. ' if ed.get('a') else '')+ed.get('why',''))+'<ol>'+picks+'</ol>'+('<p>Also good: '+E(ed['alt'])+'</p>' if ed.get('alt') else '')+'<p>'+a('/editions/','All edition guides')+'</p>'
        out['editions/'+ed['id']]=(ed['t']+': Editions & Translations — Bibliotheca Catholica',('Which edition of '+ed['t']+' to read: '+ed.get('why',''))[:300],body)
    gid={e['id']:e for e in guide['editions']}
    for L in guide['lists']:
        items=''.join('<li>'+(a('/editions/'+i['e']+'/',gid[i['e']]['t']) if i.get('e') in gid else E(i.get('t','')+(' — '+i['a'] if i.get('a') else '')))+(': '+E(i['b']) if i.get('b') else '')+'</li>' for i in L['items'])
        body=head('Reading list',L['t'],L.get('sub',''))+'<ol>'+items+'</ol><p>'+a('/reading/','All reading lists')+'</p>'
        out['reading/'+L['id']]=(L['t']+' — Reading Lists — Bibliotheca Catholica',(L['t']+': '+L.get('sub',''))[:300],body)
    s_href=lambda x:'/author/'+x['author_id']+'/' if x['tier']==1 and x.get('author_id') else '/saints/'+x['id']+'/'
    for x in saints:
        if x['tier']==1:continue  # writers' pages are their author pages
        L=[]
        if x.get('catholic_encyclopedia'):L.append(a(x['catholic_encyclopedia']['url'],'Catholic Encyclopedia (New Advent)',True))
        if x['feasts']['vatican_news']:L.append(a(x['feasts']['vatican_news'][0]['source_url'],'Vatican News',True))
        if x.get('wikipedia'):L.append(a(x['wikipedia'],'Wikipedia',True))
        L.append(a(x['wikidata'],'Wikidata '+x['qid'],True))
        rw=''.join('<li>'+a('/work/'+w+'/',libw[w]['title'])+'</li>' for w in x.get('reading_room_works',[]) if w in libw)
        ws=''.join('<li>'+(a('/work/'+b['work_id']+'/',b['title']) if b.get('work_id') in libw else a(b['url'],b['title'],True))+'</li>' for b in SD['shelf'] if x['id'] in b.get('about',[]))
        body=head(s_status(x)+(' · '+s_years(x) if s_years(x) else ''),x['name'],s_facts(x))+'<p>'+' · '.join(L)+'</p>'+('<h2>Read here</h2><ul>'+rw+'</ul>' if rw else '')+('<h2>Lives</h2><ul>'+ws+'</ul>' if ws else '')+'<p>'+a('/saints/','Saints & Hagiography')+'</p>'
        d=x['name']+': '+s_facts(x)[0].lower()+s_facts(x)[1:]+' Sources, feast days, and where to read more.'
        out['saints/'+x['id']]=(x['name']+' — Saints — Bibliotheca Catholica',d[:300],body)
    sh=''.join('<li>'+a(b['url'],b['title'],True)+' — '+E(b['author'])+'; '+E(b['edition'] or b['imprint'])+(' (novel)' if b.get('fiction') else '')+'</li>' for b in SD['shelf'])
    out['saints/books']=('The hagiography shelf — Saints — Bibliotheca Catholica','Public-domain lives of the saints, with editions and rights checked: Butler, Baring-Gould, the Golden Legend, the Little Flowers of St. Francis, and more.',head('Saints & Hagiography','The hagiography shelf','Public-domain lives of the saints, each with its edition, imprint, and rights evidence.')+'<ul>'+sh+'</ul><p>'+a('/saints/','Saints & Hagiography')+'</p>')
    out['saints/about']=('Saints: sources and method — Bibliotheca Catholica','Where the saints guide gets its facts, how feast dates are labelled, and what CatholicSaints.Info links mean.',head('Saints & Hagiography','Sources & method','Every fact links its source. Feast dates are labelled by where they come from: Vatican News “Saint of the day”, the General Roman Calendar (not yet checked), and other calendars recorded in Wikidata.')+'<p>'+a('/saints/','Saints & Hagiography')+'</p>')
    for k,(t,d) in SECTIONS.items():
        extra=''
        if k in('scripture','magisterium','references','media','libraries','prayers'):
            extra='<ul>'+''.join('<li>'+a(r['url'],r['name'],True)+' — '+E(r.get('desc',''))+'</li>' for r in hub['resources'] if r['section']==k)+'</ul>'
        elif k=='timeline':
            extra='<p>Authors are placed by their principal-work century; additional saints use sourced life dates. Undated and legendary figures remain outside the dated sequence. Writings by a person and biographies about them are listed separately in the interactive timeline.</p><p>'+a('/saints/','Saints & Hagiography')+' · '+a('/library/','Reading room')+'</p>'
            for au in sorted(authors,key=lambda x:(x.get('century') or 999,x['name'])):
                mine=[w for w in lib['works'] if w.get('authorId')==au['id']]
                sa=saints_by_author.get(au['id'])
                extra+='<h2>'+a('/author/'+au['id']+'/',au['name'])+'</h2><p>'+E(str(au.get('century','Unplaced'))+' century · principal work')+(' · '+E(s_status(sa)) if sa else '')+'</p>'
                if mine:extra+='<ul>'+''.join('<li>'+a('/work/'+w['id']+'/',w['title'])+'</li>' for w in mine)+'</ul>'
            extra+='<h2>Additional saints and traditional figures</h2><ul>'+''.join('<li>'+a(s_href(x),x['name'])+' — '+E(s_status(x))+(' · '+E(FLAGL[x['historicity']['flag']]) if x.get('historicity') else '')+'</li>' for x in saints if not x.get('author_id') and x['id'] not in skip_auth)+'</ul>'
        elif k=='authors':extra='<ul>'+''.join('<li>'+a('/author/'+x['id']+'/',x['name']+years(x))+'</li>' for x in authors)+'</ul>'
        elif k=='library':extra='<ul>'+''.join('<li>'+a('/work/'+w['id']+'/',w['title']+' — '+w['author'])+'</li>' for w in lib['works'])+'</ul>'
        elif k=='editions':extra='<ul>'+''.join('<li>'+a('/editions/'+e['id']+'/',e['t'])+'</li>' for e in guide['editions'])+'</ul>'
        elif k=='saints':extra='<ul>'+''.join('<li>'+a(s_href(x),x['name'])+' — '+E(s_status(x))+(' · Vatican News: '+E(s_vn(x)) if x['feasts']['vatican_news'] else '')+(' · '+E(FLAGL[x['historicity']['flag']]) if x.get('historicity') else '')+'</li>' for x in sorted(saints,key=lambda x:x['name']))+'</ul><p>'+a('/saints/books/','The hagiography shelf')+' · '+a('/saints/about/','Sources & method')+'</p>'
        elif k=='reading':extra='<ul>'+''.join('<li>'+a('/reading/'+L['id']+'/',L['t'])+'</li>' for L in guide['lists'])+'</ul>'
        out[k]=(t+' — Bibliotheca Catholica',d,head('Bibliotheca Catholica',t,d)+extra)
    if flags.get('policy_html'):
        out['policy']=('Fidelity & Editorial Policy — Bibliotheca Catholica','Bibliotheca Catholica is faithful to the Magisterium. Listing a book in the Isidore Index is not endorsement; flagged records carry context notes. How to report a concern.',flags['policy_html'])
    # v16 rights pages: same HTML as the app (data/rights-pages.js, written by tools/build_rights.py from tools/rights_pages.py)
    rp=json.loads((ROOT/'data/rights-pages.js').read_text().strip()[len('window.RIGHTS_PAGES='):-1])
    out['rights']=('Rights & Permissions — Bibliotheca Catholica','What the five rights badges mean (public domain in the US, open license, permission granted, link only, and unknown), how each status is decided, and when downloads are shown. Not legal advice.',rp['rights'])
    out['takedown']=('Takedown requests — Bibliotheca Catholica','How a rights holder can ask Bibliotheca Catholica to remove a text, a link, or a record’s file links, and how to send a counter-notice. Not legal advice.',rp['takedown'])
    extra_pages=ROOT/'tools/static_extra.json'
    if extra_pages.exists():
        for k,v in json.loads(extra_pages.read_text()).items():out[k]=(v['title'],v['desc'],v['body'])
    # remove the previous run's output (listed in the manifest), then write this run's pages
    man=ROOT/'docs/static-pages.txt'
    if man.exists():
        for line in man.read_text().split():
            f=ROOT/line
            if f.name=='index.html' and f.exists():f.unlink()
            d=f.parent
            while d!=ROOT and d.exists() and not any(d.iterdir()):d.rmdir();d=d.parent
    for route,(t,d,body) in out.items():
        f=ROOT/route/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(page(tpl,route,t,d,body))
    man.write_text(''.join(r+'/index.html\n' for r in sorted(out)))
    urls=[SITE]+[SITE+r+'/' for r in sorted(out)]
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+E(u)+'</loc></url>\n' for u in urls)+'</urlset>\n')
    (ROOT/'robots.txt').write_text('# Bibliotheca Catholica\nUser-agent: *\nAllow: /\nDisallow: /data/texts/\n\nSitemap: '+SITE+'sitemap.xml\n')
    (ROOT/'404.html').write_text('''<!doctype html><html lang="en"><head>
'''+GA_TAG+'''<meta charset="utf-8"><title>Not found — Bibliotheca Catholica</title><meta name="robots" content="noindex">
<script>(function(){var p=location.pathname.replace(/^\\/+|\\/+$/g,'').replace(/\\/index\\.html$/,'');
if(p&&/^[A-Za-z0-9._~%\\/-]+$/.test(p)){location.replace('/#/'+p+location.search);return}location.replace('/#/404')})();</script></head>
<body><p>Page not found. <a href="/">Go to Bibliotheca Catholica</a>.</p></body></html>
''')
    print(len(out),'pages;',len(urls),'sitemap URLs')
if __name__=='__main__':main()
