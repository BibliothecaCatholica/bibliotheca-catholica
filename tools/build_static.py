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
import hashlib,html,json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SITE='https://bibliothecacatholica.com/';E=html.escape
sys.path.insert(0,str(ROOT/'tools'));import site_copy
# --- v17 SEO: see docs/SEO.md ---------------------------------------------------------------------
NAME='Bibliotheca Catholica';OG_IMAGE=SITE+'assets/og-image.png'
# Profiles we can verify belong to the project: the GitHub organization (this repo) and the Bluesky
# handle bibliothecacatholica.com, which resolves to the DID in .well-known/atproto-did.
SAME_AS=['https://github.com/BibliothecaCatholica','https://bsky.app/profile/bibliothecacatholica.com']
HOME_TITLE='Bibliotheca Catholica: a free library of Catholic authors and classics'
HOME_DESC='Bibliotheca Catholica is a free, curated, searchable library of Catholic authors, Scripture, Church documents, prayers, saints, and classics to read online.'
DESC_MIN,DESC_MAX=120,160
def fit(parts,extra=(),hi=DESC_MAX,lo=150):
    """Join sentences into a meta description of at most `hi` characters: the core `parts` first, then
    optional `extra` sentences while they fit (aiming for 150-160). Over-long text is cut at a word."""
    d=' '.join(x.strip() for x in parts if x and x.strip())
    d=re.sub(r'\s+',' ',d)
    if len(d)>hi:d=d[:hi-1].rsplit(' ',1)[0].rstrip(' ,;:—–-')+'…'
    for x in extra:  # each item is a sentence or a tuple of variants, longest first
        if len(d)>=lo:break
        for v in ((x,) if isinstance(x,str) else x):
            if v and len(d)+1+len(v)<=hi:d=d+' '+v;break
    return d
def ld(obj):return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+'</script>'
def crumbs(*items):
    """BreadcrumbList JSON-LD from (name, path) pairs; the home page is always first."""
    L=[(NAME,'')]+list(items)
    return {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':SITE+u} for i,(n,u) in enumerate(L)]}
def crumb_html(*items):
    L=[(NAME,'/')]+[(n,'/'+u) for n,u in items[:-1]]
    return '<nav class="crumbs small" aria-label="Breadcrumb">'+' › '.join('<a href="'+E(u)+'">'+E(n)+'</a>' for n,u in L)+' › <span aria-current="page">'+E(items[-1][0])+'</span></nav>'
def iso_year(y):return '%04d'%y if isinstance(y,int) and 0<y<10000 else None
ORDINAL=lambda n:str(n)+({1:'st',2:'nd',3:'rd'}.get(n%10 if n%100 not in(11,12,13) else 0,'th'))
def oxford(xs):
    xs=list(xs)
    return xs[0] if len(xs)==1 else ' and '.join(xs) if len(xs)==2 else ', '.join(xs[:-1])+', and '+xs[-1]
# Short "how to use this page" paragraphs for index and list pages (shown under the page heading).
INTRO={
 'library':'This is the reading room of Bibliotheca Catholica. Each work below opens a page with its source editions, translators, and rights notes; works marked “Read here” can be read on this site, with contents, search, highlights, and notes saved in your browser.',
 'authors':'Browse Catholic authors in chronological order, from the Apostolic Fathers to contemporary writers. Each name opens an author page with dates, a short biography, the author’s works online, and any editions in the reading room. Use the search box at the top to find an author or a title quickly.',
 'doctors':'The Church has named these saints Doctors of the Church for the eminence of their teaching and the holiness of their lives. Each name opens the author page, with dates, a short biography, and links to read their works free online.',
 'timeline':'The timeline places saints and Catholic writers by century, so you can see who wrote when and follow each name to its author page and reading editions.',
 'editions':'Each guide below answers one question: which edition or translation of a Catholic classic to read. Guides list the recommended translations, free editions, and print copies, with a short note on why each pick is recommended.',
 'reading':'Reading lists are curated paths through the library. Pick a list, start with its first book, and follow the links to edition guides and free texts.',
 'saints':'This guide lists every saint in the pilot collection, with feast days labelled by their source. Writers who are saints open their author pages; other saints have their own profiles with sources and the lives written about them.',
 'isidore':'The Isidore Index catalogues the St. Isidore e-book library (isidore.co). Search or filter by title, author, language, era, or format; each record shows a rights badge that decides whether it links to isidore.co’s book page or offers a download.',
 'scripture':'Free Bibles, commentaries, and daily readings, each linking to the original site.',
 'magisterium':'The documents of the Church’s teaching office, from catechisms and councils to encyclicals and canon law, linked at vatican.va and other official sources.',
 'references':'Standard Catholic reference works, linked at their original sites.',
 'media':'Catholic podcasts, channels, networks, and news outlets, each linked at its own site.',
 'libraries':'The digital libraries and archives that hold the texts this site points to.',
 'prayers':'The common prayers and devotions of the Church, with links to daily readings and prayer resources.',
 'rare':'Lesser-known Catholic books, tracts, and manuscripts held in digital archives.',
 'projects':'Open Catholic software, datasets, and digitization projects.',
 'substacks':'Catholic writers and newsletters published on Substack.',
 'related':'Writers outside the Catholic communion who are widely read alongside the Catholic tradition.',
 'data':'The open data behind Bibliotheca Catholica, published under CC0 for anyone to reuse.',
 'support':'Bibliotheca Catholica is free for everyone and has no ads. Here is how you can help keep it that way.',
}
DESC_EXTRA=(('Part of Bibliotheca Catholica, a free Catholic library.','From Bibliotheca Catholica, a free Catholic library.','At Bibliotheca Catholica, a free Catholic library.','Free at Bibliotheca Catholica.','At Bibliotheca Catholica.'),)
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
HOME_RE=re.compile(r'<!-- static-home:start -->.*?<!-- static-home:end -->',re.S)
LD_RE=re.compile(r'<!-- jsonld:start -->.*?<!-- jsonld:end -->\n',re.S)
def page(tpl,route,title,desc,body,noindex=False,jsonld=()):
    url=SITE+(route+'/' if route else '');t=E(title);d=E(desc)
    s=LD_RE.sub('',tpl)
    if jsonld:s=s.replace('</head>','<!-- jsonld:start -->'+''.join(ld(x) for x in jsonld)+'<!-- jsonld:end -->\n</head>',1)
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
TAGL={'saint':'saint','theologian':'theologian','philosopher':'philosopher','convert':'convert','bishop':'bishop','mystic':'mystic','monastic':'monastic','spiritual':'spiritual writer','father':'Church Father','historian':'historian','poet':'poet','apologist':'apologist','founder':'founder','cardinal':'cardinal','novelist':'novelist','preacher':'preacher','martyr':'martyr','pope':'pope','scripture':'Scripture scholar','liturgist':'liturgist','scholar':'scholar','journalist':'journalist','scientist':'scientist','catechist':'catechist','biographer':'biographer','hagiographer':'hagiographer','canonist':'canonist','statesman':'statesman','publisher':'publisher'}
def write_home(tpl,counts):
    """v17: the home page IS index.html.  Rewrite only its marked regions (the crawlable landing content
    inside <main> and the WebSite/Organization JSON-LD) and data/site-copy.js, so hand edits elsewhere in
    index.html survive.  Idempotent: CI reruns this and checks git diff."""
    about=site_copy.home_about(counts)
    hero=('<section class="hero hero-c"><h1 class="eyebrow hero-name">Bibliotheca Catholica</h1><p class="hero-title">Tolle Lege</p><p class="hero-trans">Take up and read</p>'
      '<p class="hero-sub">Two thousand years of Catholic thought, in one place.</p>'
      '<p class="lede">Discover the writers, ideas, and spiritual classics of the Catholic tradition. Read here, download an ebook, or find the edition that belongs on your shelf.</p>'
      '<div class="hero-cta"><a class="btn gold" href="/library/">Discover &amp; Read →</a><a class="btn ghost" href="/isidore/">Explore the Isidore Index</a><a class="btn ghost" href="/timeline/">Browse the timeline</a></div></section>')
    home='<!-- static-home:start --><div class="static-prerender">'+hero+about+'</div><!-- static-home:end -->'
    s=(ROOT/'index.html').read_text()
    assert '<!-- static-home:start -->' in s,'index.html <main> must contain the static-home markers'
    s=HOME_RE.sub(lambda m:home,s,count=1)
    s=re.sub(r'<title>.*?</title>',lambda m:'<title>'+E(HOME_TITLE)+'</title>',s,count=1,flags=re.S)
    s=re.sub(r'<meta name="description" content="[^"]*">',lambda m:'<meta name="description" content="'+E(HOME_DESC)+'">',s,count=1)
    org={'@context':'https://schema.org','@type':'Organization','@id':SITE+'#organization','name':NAME,'url':SITE,'logo':OG_IMAGE,'sameAs':SAME_AS}
    web={'@context':'https://schema.org','@type':'WebSite','@id':SITE+'#website','name':NAME,'url':SITE,'description':HOME_DESC,'inLanguage':'en','publisher':{'@id':SITE+'#organization'}}
    s=LD_RE.sub('',s).replace('</head>','<!-- jsonld:start -->'+ld(web)+ld(org)+'<!-- jsonld:end -->\n</head>',1)
    js='window.SITE_COPY='+json.dumps({'homeTitle':HOME_TITLE,'homeDesc':HOME_DESC,'home':about,'about':site_copy.about_page(counts)},ensure_ascii=False,separators=(',',':'))+';\n'
    (ROOT/'data/site-copy.js').write_text(js)
    s=re.sub(r'data/site-copy\.js\?v=[0-9a-f]*','data/site-copy.js?v='+hashlib.sha256(js.encode()).hexdigest()[:10],s)
    (ROOT/'index.html').write_text(s)
def main():
    tpl=(ROOT/'index.html').read_text();global GA_TAG;GA_TAG=ga_tag(tpl);hub=json.loads((ROOT/'data/catholic-hub.json').read_text())
    lib=json.loads((ROOT/'data/library.json').read_text());guide=jsvar('data/guide.js','GUIDE_DATA');flags=load_flags()
    skip_auth=set(flags.get('hubAuthors',[]))
    eras={e['id']:e['label'] for e in hub['eras']}
    out={}  # route -> html
    SD=json.loads((ROOT/'data/saints.json').read_text());saints=SD['saints']
    saints_by_author={x['author_id']:x for x in saints if x['tier']==1 and x.get('author_id')}
    libw={w['id']:w for w in lib['works']}
    auth_ids={x['id'] for x in hub['authors'] if x['id'] not in skip_auth}
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
        # v17: facts already in the data (era, century, vocations from tags, Doctor of the Church) and the curated links
        era=eras.get(au.get('era'));tags=[TAGL[t] for t in au.get('tags',[]) if t in TAGL]
        facts=[]
        if era:facts.append('Era: '+era+(' ('+ORDINAL(au['century'])+' century)' if isinstance(au.get('century'),int) and au['century']>0 else '')+'.')
        if tags:facts.append(oxford(tags)[0].upper()+oxford(tags)[1:]+'.')
        if au.get('doctor'):facts.append('Doctor of the Church.')
        # never isidore.co folder listings or raw files (rights rule 10): book pages and outside sites only
        more=[a(l['url'],l['label'],True) for l in au.get('links') or [] if l.get('url') and not re.search(r'isidore\.co/(CalibreLibrary/|get/|calibre/get)',l['url'])]
        if au.get('qid'):more.append(a('https://www.wikidata.org/wiki/'+au['qid'],'Wikidata '+au['qid'],True))
        extra=('<h2>At a glance</h2><p>'+E(' '.join(facts))+'</p>' if facts else '')+(('<h2>More sources</h2><ul>'+''.join('<li>'+x+'</li>' for x in more)+'</ul>') if more else '')
        body=body.replace('<p>'+a('/authors/','All authors')+'</p>',extra+'<p>'+a('/authors/','All authors')+' · '+a('/timeline/','Timeline')+(' · '+a('/doctors/','Doctors of the Church') if au.get('doctor') else '')+'</p>')
        body=crumb_html(('Authors','authors/'),(au['name'],''))+body
        role=desc or au.get('wikiDesc') or ''
        d=fit([au['name']+years(au)+(', '+era if era else '')+':',(role.rstrip('.')+'.') if role else 'Catholic author.'],
              ((('Biography, works online, and '+str(len(mine))+' books to read here.','Biography and '+str(len(mine))+' books to read here.') if len(mine)>1 else ('Biography, works online, and a book to read here.','Biography and a book to read here.')) if mine else ('Dates, a short biography, and links to read their works online.','Biography and links to read their works online.','Biography and works online.'),
               (oxford(tags)[0].upper()+oxford(tags)[1:]+'.',) if tags else (),)+DESC_EXTRA)
        person={'@context':'https://schema.org','@type':'Person','name':au['name'],'url':SITE+'author/'+au['id']+'/'}
        if role:person['description']=role
        if iso_year(au.get('born')):person['birthDate']=iso_year(au['born'])
        if iso_year(au.get('died')):person['deathDate']=iso_year(au['died'])
        if au.get('qid'):person['sameAs']=['https://www.wikidata.org/wiki/'+au['qid']]
        out['author/'+au['id']]=(au['name']+' — Bibliotheca Catholica',d,body,[person,crumbs(('Authors','authors/'),(au['name'],'author/'+au['id']+'/'))])
    for w in lib['works']:
        eds=''.join('<li>'+E(e['label'])+(' · '+a('/#/read/'+w['id']+'/'+e['id'],'Read here') if e.get('text') else '')+' · '+a(e['source'],'Source',True)+'</li>' for e in w['editions'])
        d=w.get('description') or (w['title']+' by '+w['author']+': free reading edition with source, credits, and rights notes.')
        hosted=any(e.get('text') for e in w['editions'])
        by=a('/author/'+w['authorId']+'/',w['author']) if w.get('authorId') in auth_ids else E(w['author'])
        body=crumb_html(('Discover & Read','library/'),(w['title'],''))+head(w['category']+' · '+w['tradition'],w['title'],w['author']+'. '+d)+'<p>By '+by+'. '+E(str(len(w['editions']))+(' edition' if len(w['editions'])==1 else ' editions')+(', with a text you can read on this site.' if hosted else ', each linked at its source.'))+'</p><h2>Reading editions &amp; sources</h2><ul>'+eds+'</ul><p>'+a('/library/','Selected library')+' · '+a('/rights/','Rights badges')+'</p>'
        book={'@context':'https://schema.org','@type':'Book','name':w['title'],'url':SITE+'work/'+w['id']+'/','author':{'@type':'Person','name':w['author']},'description':d,'genre':w['category']}
        if w.get('authorId') in auth_ids:book['author']['url']=SITE+'author/'+w['authorId']+'/'
        langs=sorted({e['language'] for e in w['editions'] if e.get('language')})
        if langs:book['inLanguage']=langs[0] if len(langs)==1 else langs
        if hosted:book['isAccessibleForFree']=True
        md=fit([w['title']+' by '+w['author']+':',d.rstrip('.')+'.'],(('Read it free online, with source and rights notes.','Read it free online.') if hosted else ('Editions and sources, with rights notes.','Editions and sources.'),)+DESC_EXTRA)
        out['work/'+w['id']]=(w['title']+' — Bibliotheca Catholica',md,body,[book,crumbs(('Discover & Read','library/'),(w['title'],'work/'+w['id']+'/'))])
    for ed in guide['editions']:
        picks=''.join('<li><b>'+E(p.get('lbl',''))+':</b> '+E(p.get('tr',''))+(' ('+E(p['pub'])+')' if p.get('pub') else '')+'</li>' for p in ed.get('picks',[]))
        body=head('Editions & Translations · '+ed.get('cat',''),ed['t'],(ed.get('a')+'. ' if ed.get('a') else '')+ed.get('why',''))+'<ol>'+picks+'</ol>'+('<p>Also good: '+E(ed['alt'])+'</p>' if ed.get('alt') else '')+'<p>'+a('/editions/','All edition guides')+'</p>'
        body=crumb_html(('Editions & Translations','editions/'),(ed['t'],''))+body
        md=fit(['Which edition of '+ed['t']+(' by '+ed['a'] if ed.get('a') else '')+' to read:',ed.get('why','').rstrip('.')+'.'],(('Recommended translations, free texts, and print copies.','Translations, free texts, and print copies.','Translations compared.'),('Compare translations at Bibliotheca Catholica.','At Bibliotheca Catholica.')))
        out['editions/'+ed['id']]=(ed['t']+': Editions & Translations — Bibliotheca Catholica',md,body,[crumbs(('Editions & Translations','editions/'),(ed['t'],'editions/'+ed['id']+'/'))])
    gid={e['id']:e for e in guide['editions']}
    for L in guide['lists']:
        items=''.join('<li>'+(a('/editions/'+i['e']+'/',gid[i['e']]['t']) if i.get('e') in gid else E(i.get('t','')+(' — '+i['a'] if i.get('a') else '')))+(': '+E(i['b']) if i.get('b') else '')+'</li>' for i in L['items'])
        body=head('Reading list',L['t'],L.get('sub',''))+'<ol>'+items+'</ol><p>'+a('/reading/','All reading lists')+'</p>'
        md=fit([L['t']+', a Catholic reading list:',L.get('sub','').rstrip('.')+'.'],((str(len(L['items']))+' books, with edition guides and free texts.',str(len(L['items']))+' books.'),)+DESC_EXTRA)
        out['reading/'+L['id']]=(L['t']+' — Reading Lists — Bibliotheca Catholica',md,crumb_html(('Reading Lists','reading/'),(L['t'],''))+body,[crumbs(('Reading Lists','reading/'),(L['t'],'reading/'+L['id']+'/'))])
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
        d=fit([d],DESC_EXTRA)
        out['saints/'+x['id']]=(x['name']+' — Saints — Bibliotheca Catholica',d,crumb_html(('Saints & Hagiography','saints/'),(x['name'],''))+body,[crumbs(('Saints & Hagiography','saints/'),(x['name'],'saints/'+x['id']+'/'))])
    sh=''.join('<li>'+a(b['url'],b['title'],True)+' — '+E(b['author'])+'; '+E(b['edition'] or b['imprint'])+(' (novel)' if b.get('fiction') else '')+'</li>' for b in SD['shelf'])
    out['saints/books']=('The hagiography shelf — Saints — Bibliotheca Catholica','Public-domain lives of the saints, with editions and rights checked: Butler, Baring-Gould, the Golden Legend, the Little Flowers of St. Francis, and more.',head('Saints & Hagiography','The hagiography shelf','Public-domain lives of the saints, each with its edition, imprint, and rights evidence.')+'<ul>'+sh+'</ul><p>'+a('/saints/','Saints & Hagiography')+'</p>',[crumbs(('Saints & Hagiography','saints/'),('The hagiography shelf','saints/books/'))])
    out['saints/about']=('Saints: sources and method — Bibliotheca Catholica','Where the Bibliotheca Catholica saints guide gets its facts, how feast dates are labelled by source, and what the CatholicSaints.Info links mean.',head('Saints & Hagiography','Sources & method','Every fact links its source. Feast dates are labelled by where they come from: Vatican News “Saint of the day”, the General Roman Calendar (not yet checked), and other calendars recorded in Wikidata.')+'<p>'+a('/saints/','Saints & Hagiography')+'</p>',[crumbs(('Saints & Hagiography','saints/'),('Sources & method','saints/about/'))])
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
        elif k=='doctors':extra='<ul>'+''.join('<li>'+a('/author/'+x['id']+'/',x['name']+years(x))+'</li>' for x in authors if x.get('doctor'))+'</ul>'
        intro='<p class="section-intro">'+E(INTRO[k])+'</p>' if k in INTRO else ''
        out[k]=(t+' — Bibliotheca Catholica',fit([d],DESC_EXTRA),head('Bibliotheca Catholica',t,d)+intro+extra,[crumbs((t,k+'/'))])
    if flags.get('policy_html'):
        out['policy']=('Fidelity & Editorial Policy — Bibliotheca Catholica','Bibliotheca Catholica is faithful to the Magisterium. Listing is not endorsement; flagged records carry calm context notes. Privacy and how to report a concern.',flags['policy_html'],[crumbs(('Fidelity & Editorial Policy','policy/'))])
    # v16 rights pages: same HTML as the app (data/rights-pages.js, written by tools/build_rights.py from tools/rights_pages.py)
    rp=json.loads((ROOT/'data/rights-pages.js').read_text().strip()[len('window.RIGHTS_PAGES='):-1])
    out['rights']=('Rights & Permissions — Bibliotheca Catholica','What the five Bibliotheca Catholica rights badges mean, how each status is decided, and when downloads are shown. Not legal advice.',rp['rights'],[crumbs(('Rights & Permissions','rights/'))])
    out['takedown']=('Takedown requests — Bibliotheca Catholica','How a rights holder can ask Bibliotheca Catholica to remove a text, a link, or a record’s file links, and how to send a counter-notice. Not legal advice.',rp['takedown'],[crumbs(('Takedown requests','takedown/'))])
    counts={'authors':len(authors),'saints':len(saints),'books':6633,'hosted':sum(1 for w in lib['works'] if any(e.get('text') for e in w['editions']))}
    m=re.search(r'window\.BOOKS_COUNT=(\d+)',tpl)
    if m:counts['books']=int(m.group(1))
    out['about']=('About the library — Bibliotheca Catholica','About Bibliotheca Catholica: what the free Catholic library holds, where its texts come from, the 1931 rule, rights badges, editorial policy, and goals.',site_copy.about_page(counts),[crumbs(('About the library','about/'))])
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
    for route,v in out.items():
        t,d,body=v[:3];f=ROOT/route/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(page(tpl,route,t,d,body,jsonld=v[3] if len(v)>3 else ()))
    write_home(tpl,counts)
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
