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
import hashlib,html,json,re,shutil,sys,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SITE='https://bibliothecacatholica.com/';E=html.escape
sys.path.insert(0,str(ROOT/'tools'));import site_copy,build_info
# --- v17 SEO: see docs/SEO.md ---------------------------------------------------------------------
NAME='Bibliotheca Catholica';OG_IMAGE=SITE+'assets/og-image.png'
# Profiles we can verify belong to the project: the GitHub organization (this repo) and the Bluesky
# handle bibliothecacatholica.com, which resolves to the DID in .well-known/atproto-did.
SAME_AS=['https://github.com/BibliothecaCatholica','https://x.com/BiblioCatholica','https://bsky.app/profile/bibliothecacatholica.com']
HOME_TITLE='Bibliotheca Catholica — a library of libraries'
HOME_DESC='A free Catholic reading room and curated resource index. Read classic texts online, compare editions, and explore saints, Church documents, and source texts.'
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
 'isidore':'The Isidore Index catalogues the St. Isidore e-book library (isidore.co). Search or filter by title, author, language, era, or format; each record shows a rights badge that decides whether it links to isidore.co’s book page or offers a download. Bibliotheca Catholica does not host, and does not vouch for, any file at isidore.co.',
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
 'data':'The open data behind Bibliotheca Catholica, dedicated to the public domain under CC0 for anyone to reuse. CC0 covers this data only, not the texts, Wikipedia excerpts, or portraits it points to.',
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
 'isidore':('The Isidore Index: e-book catalog','A searchable index of more than 6,600 books in the St. Isidore e-book library (isidore.co), with formats, rights badges, and links to isidore.co.'),
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
import hubio as _hubio
DETAIL_V=_hubio.split(_hubio.load())[0]['detailV']
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
    s=re.sub(r'<script (?:defer )?src="data/data\.js(\?[^"]*)?"></script>',lambda m:'<script>window.BC_BOOT='+json.dumps(route)+'</script>\n'+m.group(0),s,count=1)
    assert 'window.BC_BOOT' in s,'data/data.js script tag not found in index.html'
    if route.startswith('author/') or route=='timeline':  # Phase B item 5: these routes wait for the lazy author detail; fetch it with the core
        s=s.replace('</head>','<link rel="preload" as="script" href="data/authors-detail.js?v='+DETAIL_V+'">\n</head>',1)
    return s
CC_BY_SA='https://creativecommons.org/licenses/by-sa/4.0/'
def a(href,label,ext=False):
    return '<a href="'+E(href)+'"'+(' target="_blank" rel="noopener"' if ext else '')+'>'+E(label)+'</a>'
def years(au):
    b,d=au.get('born'),au.get('died')
    f=lambda y:(str(-y)+' BC' if y<0 else str(y)) if isinstance(y,int) else ''
    return ' ('+f(b)+'–'+f(d)+')' if (b or d) else ''
TAGL={'saint':'saint','theologian':'theologian','philosopher':'philosopher','convert':'convert','bishop':'bishop','mystic':'mystic','monastic':'monastic','spiritual':'spiritual writer','father':'Church Father','historian':'historian','poet':'poet','apologist':'apologist','founder':'founder','cardinal':'cardinal','novelist':'novelist','preacher':'preacher','martyr':'martyr','pope':'pope','scripture':'Scripture scholar','liturgist':'liturgist','scholar':'scholar','journalist':'journalist','scientist':'scientist','catechist':'catechist','biographer':'biographer','hagiographer':'hagiographer','canonist':'canonist','statesman':'statesman','publisher':'publisher'}
def write_home(tpl,counts,snapshot):
    """v17: the home page IS index.html.  Rewrite only its marked regions (the crawlable landing content
    inside <main> and the WebSite/Organization JSON-LD) and data/site-copy.js, so hand edits elsewhere in
    index.html survive.  Idempotent: CI reruns this and checks git diff."""
    about=site_copy.home_about(counts)
    hero=('<section class="hero hero-c"><h1 class="eyebrow hero-name">Bibliotheca Catholica</h1><p class="hero-title">Tolle Lege</p><p class="hero-trans">Take up and read</p>'
      '<p class="hero-sub">Two thousand years of Catholic thought, in one place.</p>'
      '<p class="lede">Discover the writers, ideas, and spiritual classics of the Catholic tradition. Read here, download an ebook, or find the edition that belongs on your shelf.</p>'
      '<div class="hero-cta"><a class="btn gold" href="/library/">Discover &amp; Read →</a><a class="btn ghost" href="/isidore/">Explore the Isidore Index</a><a class="btn ghost" href="/timeline/">Browse the timeline</a></div></section>')
    home='<!-- static-home:start --><div class="static-prerender">'+hero+about+'</div><!-- static-home:end -->'
    s=tpl
    assert '<!-- static-home:start -->' in s,'index.html <main> must contain the static-home markers'
    s=HOME_RE.sub(lambda m:home,s,count=1)
    s=re.sub(r'<title>.*?</title>',lambda m:'<title>'+E(HOME_TITLE)+'</title>',s,count=1,flags=re.S)
    s=re.sub(r'<meta name="description" content="[^"]*">',lambda m:'<meta name="description" content="'+E(HOME_DESC)+'">',s,count=1)
    for key,value in (('og:title',HOME_TITLE),('og:description',HOME_DESC),('twitter:title',HOME_TITLE),('twitter:description',HOME_DESC)):
        attr='property' if key.startswith('og:') else 'name'
        s=re.sub(r'<meta '+attr+'="'+key+'" content="[^"]*">',lambda m:'<meta '+attr+'="'+key+'" content="'+E(value)+'">',s,count=1)
    org={'@context':'https://schema.org','@type':'Organization','@id':SITE+'#organization','name':NAME,'url':SITE,'logo':OG_IMAGE,'sameAs':SAME_AS}
    web={'@context':'https://schema.org','@type':'WebSite','@id':SITE+'#website','name':NAME,'url':SITE,'description':HOME_DESC,'inLanguage':'en','publisher':{'@id':SITE+'#organization'}}
    s=LD_RE.sub('',s).replace('</head>','<!-- jsonld:start -->'+ld(web)+ld(org)+'<!-- jsonld:end -->\n</head>',1)
    js='window.SITE_COPY='+json.dumps({'homeTitle':HOME_TITLE,'homeDesc':HOME_DESC,'home':about,'about':site_copy.about_page(counts)},ensure_ascii=False,separators=(',',':'))+';\n'
    (ROOT/'data/site-copy.js').write_text(js)
    s=re.sub(r'data/site-copy\.js\?v=[0-9a-f]*','data/site-copy.js?v='+hashlib.sha256(js.encode()).hexdigest()[:10],s)
    s=re.sub(r'data/text-pages\.js\?v=[0-9a-f]*','data/text-pages.js?v='+hashlib.sha256((ROOT/'data/text-pages.js').read_bytes()).hexdigest()[:10],s)  # deep-link gaps: content token
    (ROOT/'index.html').write_text(build_info.stamp(s,snapshot))
# --- v20 dated reading plans: the static page lists every day; scripts/plans.js adds the today highlight and marks.
PLAN_DESC={'advent-2026':'Advent with the Fathers: 26 daily readings for Advent 2026, November 29 to December 24, from Augustine, Clement, Ignatius, Bede, Aquinas, Julian, and more.'}
WEEKDAYS=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
def plan_date(iso,weekday=True):
    import datetime;d=datetime.date.fromisoformat(iso);return (WEEKDAYS[d.weekday()]+', ' if weekday else '')+MONTHS[d.month-1]+' '+str(d.day)
PLAN_SPAN=lambda P:plan_date(P['start'],False)+' to '+plan_date(P['end'],False)+', '+str(P['year'])
def plan_day_html(d):
    """Mirrors dayHtml() in scripts/plans.js, without the today highlight and the mark-as-read box."""
    au=a('/author/'+d['authorId']+'/',d['author']) if d['authorId'] else E(d['author'])
    ed=E(d['editionLabel'])+(', tr. '+E(', '.join(d['contributors'])) if d['contributors'] else '')+'. '+('Edition: ' if d['yearKind']=='edition' else 'Translation by ')+str(d['year'])+'.'
    return ('<li class="plan-day'+(' has-marker' if d['marker'] else '')+'" id="day-'+str(d['day'])+'" data-date="'+d['date']+'">'
      '<div class="pd-head"><span class="pd-num">Day '+str(d['day'])+'</span><time datetime="'+d['date']+'">'+E(plan_date(d['date']))+'</time></div>'
      +('<p class="pd-marker">'+E(d['marker'])+'</p>' if d['marker'] else '')+
      '<h2 class="pd-title">'+au+', <cite>'+a('/work/'+d['work']+'/',d['title'])+'</cite></h2>'
      '<p class="pd-ref">'+E(d['ref'])+' · about '+str(d['minutes'])+' min</p>'
      '<blockquote class="pd-quote"><p>“'+E(d['quote'])+('…' if d['cut'] else '')+'”</p></blockquote><p class="pd-note">'+E(d['note'])+'</p>'
      '<div class="pd-foot"><a class="btn" href="/'+E(d['href'])+'">Read day '+str(d['day'])+' →</a><span class="pd-print-link">bibliothecacatholica.com/'+E(d['href'])+'</span></div>'
      '<p class="small pd-ed">'+ed+' <a class="rights-badge rb-public-domain-us" href="/rights/" data-rights="public_domain_us" title="'+E(d['yearEvidence'])+'"><span class="rb-k">Rights:</span> Public domain (US)</a></p></li>')
def plan_html(P):
    return (crumb_html(('Reading Lists','reading/'),(P['t'],''))+'<div class="page-head plan-head"><div class="eyebrow">Reading plan · '+E(PLAN_SPAN(P))+'</div><h1>'+E(P['t'])+'</h1><p class="lede">'+E(P['intro'])+'</p></div>'
      '<ol class="plan-days">'+''.join(plan_day_html(d) for d in P['days'])+'</ol>'
      '<p class="small plan-foot">Every reading opens in the on-site reader at the start of the passage. The editions are public domain in the United States; each badge links to '+a('/rights/','how rights are determined')+'. '+a('/reading/','All reading lists')+'.</p>')
def list_item_title(i,gid,libw):
    """A reading-list entry's title: its edition guide, else its reading-room works (Phase A: the 14 entries
    that carry only `workIds` rendered as ": description"), else its own title and author. Never empty."""
    if i.get('e') in gid:return a('/editions/'+i['e']+'/',gid[i['e']]['t'])
    ws=[libw[x] for x in i.get('workIds') or [] if x in libw]
    if ws:return ', '.join(a('/work/'+w['id']+'/',w['title'])+' by '+E(w['author']) for w in ws)
    t=E(i.get('t','')+(' — '+i['a'] if i.get('a') else ''))
    assert t.strip(),'reading-list entry with no title, guide, or work: %r'%i
    return t
# --- Deep-link gaps (2026-11-09): chapter and story pages for hosted texts (tools/text_pages.py, data/text-pages.json) ---
PG_NOTICE=('This eBook is for the use of anyone anywhere in the United States and most other parts of the world at no cost and with almost no restrictions whatsoever. '
  'You may copy it, give it away or re-use it under the terms of the <a href="https://www.gutenberg.org/policy/license.html" target="_blank" rel="noopener">Project Gutenberg License</a> '
  'included with this eBook or online at <a href="https://www.gutenberg.org" target="_blank" rel="noopener">www.gutenberg.org</a>. If you are not located in the United States, '
  'you will have to check the laws of the country where you are located before using this eBook.')  # same words as read() in scripts/library.js
def pd_badge(evidence):
    return ' <a class="rights-badge rb-public-domain-us" href="/rights/" data-rights="public_domain_us" title="'+E(evidence)+'"><span class="rb-k">Rights:</span> Public domain (US)</a>'
def text_split(path):
    return [p.strip() for p in re.split(r'\n\s*\n',(ROOT/path).read_text(encoding='utf-8').replace('\r','')) if p.strip()]
def part_label(d,x,low=False):
    t=(d['noun']+' '+x['num']) if x['num'][:1].isdigit() or d['kind']=='ch' else x['num']
    return t[0].lower()+t[1:] if low else t
def part_path(wid,d,x):return 'work/'+wid+'/'+d['kind']+'/'+x['slug']
def parts_list(wid,d):
    """The contents list a work page shows (static work page; the app mirrors it from data/text-pages.js)."""
    return ('<h2>'+E(d['nouns'])+'</h2><ol class="text-parts">'+''.join('<li>'+a('/'+part_path(wid,d,x)+'/',(x['num']+'. ' if d['kind']=='ch' else '')+x['title'])+'</li>' for x in d['items'])+'</ol>')
def ra_note_html(ra,libw,listing):
    """The calm context note Research wrote for a related author (Sabatier), in the editorial-note box style, with onward reading."""
    if not ra.get('note'):return ''
    also=('<p>Read also: '+oxford([a('/work/'+x+'/',libw[x]['title'])+('' if libw[x]['author'].startswith('Anonymous') else ' by '+E(libw[x]['author'])) for x in ra['readAlso']])+'.</p>') if ra.get('readAlso') else ''
    return '<div class="ef-box"><div class="ef-h">Context note</div><p>'+E(ra['note'])+'</p>'+also+('<p class="small">Listing is not endorsement. See the '+a('/policy/','Fidelity & Editorial Policy')+'.</p>' if listing else '')+'</div>'
def related_authors(out,lib,ra_badge):
    """Deep-link gaps (2026-11-09): /author/<id>/ for writers outside the Catholic communion whose books are in the reading
    room (data/library.json `relatedAuthors`, from Research). Badge, sourced bio, the works here, and a calm context note
    in the editorial-note style where Research gave one. The app keeps these static pages as the view (staticOnly())."""
    libw={w['id']:w for w in lib['works']}
    for ra in lib.get('relatedAuthors',[]):
        yrs=' ('+str(ra['born'])+'–'+str(ra['died'])+')'
        mine=[libw[x] for x in ra['workIds']]
        li=''.join('<li>'+a('/work/'+w['id']+'/',w['title'])+(' · '+a('/#/read/'+w['id']+'/'+next(e['id'] for e in w['editions'] if e.get('text')),'Read here') if any(e.get('text') for e in w['editions']) else ' (full text at the source)')+'</li>' for w in mine)
        note=ra_note_html(ra,libw,False)
        other=''.join('<li>'+a(x['url'],x['title'],True)+(' ('+str(x['year'])+')' if x.get('year') else '')+'</li>' for x in ra.get('otherWorks',[]))
        body=(crumb_html(('Related Christian writers','related/'),(ra['name'],''))
          +'<div class="page-head"><div class="eyebrow">Related Christian writer</div><h1>'+E(ra['name']+yrs)+'</h1><p class="lede">'+E(ra['bio'])+'</p></div>'
          +'<p>'+ra_badge(ra)+'</p>'+note
          +'<p class="small">Bibliotheca Catholica lists some writers outside the Catholic communion whose books are read alongside the Catholic tradition. Listing is not endorsement; see the '+a('/policy/','Fidelity & Editorial Policy')+'.</p>'
          +'<h2>In our library</h2><ul>'+li+'</ul>'+(('<h2>Other works online</h2><ul>'+other+'</ul>') if other else '')
          +'<h2>More sources</h2><ul>'+''.join('<li>'+a(x['url'],x['label'],True)+'</li>' for x in ra['sources'])+'</ul>'
          +'<h2>At a glance</h2><p>'+E('Born '+str(ra['born'])+', died '+str(ra['died'])+'. '+ra['badge']+': '+ra['tradition']+'. Sources checked '+ra['checked']+'.')+'</p>'
          +'<p>'+a('/related/','Related Christian writers')+' · '+a('/library/','Selected library')+'</p>')
        n=len(mine)
        d=fit([ra['desc']])
        assert 120<=len(d)<=160,(ra['id'],len(d))
        person={'@context':'https://schema.org','@type':'Person','name':ra['name'],'url':SITE+'author/'+ra['id']+'/','birthDate':iso_year(ra['born']),'deathDate':iso_year(ra['died'])}
        out['author/'+ra['id']]=(ra['name']+' — Bibliotheca Catholica',d,body,[person,crumbs(('Related Christian writers','related/'),(ra['name'],'author/'+ra['id']+'/'))])
def series_html(w,lib,TPD):
    """Deep-link gaps: the books of a series in order (data/library.json `series`), mirrored by seriesList() in scripts/library.js."""
    libw={v['id']:v for v in lib['works']};h=''
    for S in lib.get('series',[]):
        if not any(i['workId']==w['id'] for i in S['items']):continue
        li=[]
        for i in S['items']:
            v=libw.get(i['workId']);t=E(i['title'])+' ('+str(i['year'])+')'
            if v and v['id']==w['id']:t='<b>'+t+'</b>, this book'
            elif v:t=a('/work/'+v['id']+'/',i['title'])+' ('+str(i['year'])+')'
            if v and v['id'] in TPD:t+=': read here, '+str(len(TPD[v['id']]['items']))+' '+E(TPD[v['id']]['nouns'].lower())+' on their own pages'
            elif v and any(e.get('text') for e in v['editions']):t+=': read here'
            if i.get('note'):t+='. '+E(i['note'])
            if i.get('contents'):t+=' Stories: '+E(oxford(i['contents']))+'.'
            if not v:t+=' '+a('https://search.worldcat.org/search?q='+urllib.parse.quote(i['title']+' '+w['author']),'WorldCat',True)+' · '+a('https://openlibrary.org/search?q='+urllib.parse.quote(i['title']+' '+w['author']),'Open Library',True)
            li.append('<li>'+t+'</li>')
        h+='<h2>'+E(S['title'])+'</h2><ol class="series-list">'+''.join(li)+'</ol>'
    return h
def part_pages(out,lib,by_html,author_ld):
    TPD=json.loads((ROOT/'data/text-pages.json').read_text())['works'];libw={w['id']:w for w in lib['works']}
    for wid,d in TPD.items():
        w=libw[wid];e=next(x for x in w['editions'] if x['id']==d['edition']);B=text_split(e['text']);n=len(d['items'])
        for k,x in enumerate(d['items']):
            route=part_path(wid,d,x);prev=d['items'][k-1] if k else None;nxt=d['items'][k+1] if k+1<n else None
            nav=('<nav class="reader-pagination" aria-label="'+E(d['nouns'])+'">'+(a('/'+part_path(wid,d,prev)+'/','← '+prev['title']).replace('<a ','<a class="btn ghost" rel="prev" ',1) if prev else '')
                 +'<span>'+E(part_label(d,x))+(' of '+str(n) if d['kind']=='ch' else ' · '+str(k+1)+' of '+str(n))+'</span>'+(a('/'+part_path(wid,d,nxt)+'/',nxt['title']+' →').replace('<a ','<a class="btn" rel="next" ',1) if nxt else '')+'</nav>')
            reader='/#/read/'+wid+'/'+e['id']+'/'+str(x['section'])+'/'+str(x['heading'])
            body=(crumb_html(('Discover & Read','library/'),(w['title'],'work/'+wid+'/'),(x['title'],''))
              +'<div class="page-head"><div class="eyebrow">'+E(w['title'])+' · '+E(part_label(d,x))+'</div><h1>'+E(x['title'])+'</h1>'
              +'<p class="lede">'+by_html(w)+', <cite>'+a('/work/'+wid+'/',w['title'])+'</cite>, '+E(part_label(d,x,True))+(' of '+str(sum(1 for y in d['items'] if y['num'][:1].isdigit() or d['kind']=='ch')) if x['num'][:1].isdigit() or d['kind']=='ch' else '')+'. About '+str(max(1,round(x['words']/200)))+' min.</p></div>'
              +'<p class="dl-row"><a class="btn" href="'+E(reader)+'">Read in the reading room →</a> '+a('/work/'+wid+'/','Work page and editions')+'</p>'
              +'<p class="small">The reading room adds highlights, notes, find in work, and saved places. This page shows the same hosted text in one piece.</p>'
              +'<p class="small text-edition">Text: '+E(w['title'])+', '+E(e['label'])+'. '+E(d.get('editionLine') or e.get('note',''))+pd_badge(e['rights'])+'</p>'
              +nav+'<p class="small pg-notice">'+PG_NOTICE+'</p>'
              +'<article class="reading-text" aria-label="'+E(x['title'])+'">'+''.join('<p>'+E(B[i])+'</p>' for i in range(x['start'],x['end']+1))+'</article>'
              +nav+parts_list(wid,d)
              +'<p class="small">Source: '+E(w['author']+'. '+w['title']+'. '+e['label']+'.')+' '+a(e['source'],'Project Gutenberg record',True)+'. '+E(e['rights'])+' The full Project Gutenberg license is kept in the hosted text.</p>'
              +'<p>'+a('/work/'+wid+'/',w['title'])+' · '+a('/library/','Selected library')+' · '+a('/rights/','Rights badges')+'</p>')
            what='“'+x['title']+',” '+part_label(d,x,True)+' '+('of '+str(n)+' ' if d['kind']=='ch' else '')+'in '+w['title']+' by '+w['author']+'.'
            md=fit([what],(('The full text on one page, free, with a link into the reading room for notes and highlights.','The full text on one page, with a link into the reading room.','The full text, free to read.'),)+DESC_EXTRA)
            ld_part={'@context':'https://schema.org','@type':'Chapter' if d['kind']=='ch' else 'ShortStory','name':x['title'],'url':SITE+route+'/','position':k+1,
                     'isPartOf':{'@type':'Book','name':w['title'],'url':SITE+'work/'+wid+'/','author':author_ld(w)},'isAccessibleForFree':True,'inLanguage':e.get('language') or 'English'}
            out[route]=(x['title']+' ('+w['title']+', '+part_label(d,x,True)+') — Bibliotheca Catholica',md,body,[ld_part,crumbs(('Discover & Read','library/'),(w['title'],'work/'+wid+'/'),(x['title'],route+'/'))])
    return TPD

# Deep-link gaps 4 (2026-11-09): the Summa Theologiae by question and article (data/summa.json from tools/build_summa.py)
def summa_para(p,flag=None):
    """One paragraph: line breaks joined, _italics_ as <em>, a trailing ____ rule dropped. No fragment ids: a bare #id
    would reach the app's hash router (route(), canonical, and page_view all read location.hash). A Supplement
    paragraph the OCR clean-up could not settle (flag) is marked, with the doubtful words and a link to its scan page."""
    p=re.sub(r'(\n_{5,})+$','',p).strip()
    h=re.sub(r'_([^_\n]+?)_',r'<em>\1</em>',E(' '.join(p.split())))
    if not flag:return '<p>'+h+'</p>'
    pages=', '.join(str(n) for n in flag['pages'])
    return ('<p class="ocr-flag">'+h+' <span class="small ocr-note">[OCR uncertain: '+E(', '.join(w for w in flag['words'] if w!='article title') or 'heading')
            +'. '+a(flag['scan'],'Check the scan',True)+', image '+E(pages)+'.]</span></p>')
def summa_pages(out,lib):
    S=json.loads((ROOT/'data/summa.json').read_text());w=next(x for x in lib['works'] if x['id']==S['work']);eds={e['id']:e for e in w['editions']}
    by=a('/author/thomas-aquinas/','Thomas Aquinas')
    NA='https://www.newadvent.org/summa/';CT='https://www.corpusthomisticum.org/sth0000.html'
    ld_by={'@type':'Person','name':'Thomas Aquinas','url':SITE+'author/thomas-aquinas/'}
    TEXT={}
    def blocks(ed):
        if ed not in TEXT:TEXT[ed]=text_split(eds[ed]['text'])
        return TEXT[ed]
    def para(P,B,i):return summa_para(B[i],P.get('ocrFlags',{}).get(str(i)))
    def flagged(P,lo,hi):return sum(1 for i in range(lo,hi+1) if str(i) in P.get('ocrFlags',{}))
    SUPP=next((P for P in S['parts'] if P['slug']=='supp'),None)
    ABOUT_SUPP=('<p class="supp-note"><b>About the Supplement:</b> Aquinas died in 1274 before finishing Part III. The Supplement completing it was compiled after his death from his earlier Commentary on the Sentences, traditionally attributed to his companion Reginald of Piperno. '
                'Parts I to III here come from the Project Gutenberg e-text of the English Dominican translation, and the Supplement is transcribed from the 1917, 1921, and 1922 printings of the same translation, so formatting may differ slightly.</p>')
    def qref(P,q):return P['token']+', q. '+str(q['n'])
    def aref(P,q,x):return qref(P,q)+', a. '+str(x['n'])
    def qpath(P,q):return 'summa/'+P['slug']+'/q'+str(q['n'])
    def apath(P,q,x):return qpath(P,q)+'/a'+str(x['n'])
    def na(P,q,x=None):return NA+'%d%03d.htm'%(P['newAdvent'],q['n'])+('#article'+str(x['n']) if x else '')
    def reader(P,i):return '/#/read/'+w['id']+'/'+P['edition']+'/'+str(i//35)+'/'+str(i)
    def edline(P):
        e=eds[P['edition']]
        if P['slug']=='supp':
            return ('<p class="small text-edition">Text: '+E(w['title'])+', '+E(e['label'])+', translated by the Fathers of the English Dominican Province. '+E(e['note'])+pd_badge(e['rights'])+'</p>')
        return ('<p class="small text-edition">Text: '+E(w['title'])+', '+E(e['label'])+', translated by the Fathers of the English Dominican Province. '+E(e['note'])+pd_badge(e['rights'])+'</p>')
    def source(P):
        e=eds[P['edition']]
        if P['slug']=='supp':
            src=json.loads((ROOT/'data/sources'/(e['id']+'.json')).read_text())
            vols=[a(v['url'],v['titlePage']+', '+str(v['year']),True) for v in src['volumes']]
            return ('<p class="small">Source: Thomas Aquinas. Summa Theologica, Supplement to the Third Part. Internet Archive scans: '+', '.join(vols[:-1])+', and '+vols[-1]
                    +'; two curled pages of the 1921 volume are read from '+a(src['substitutePages']['url'],'another scan of the same printing',True)+'. '+E(e['rights'])
                    +' Transcription, OCR file checksums, and method: '+a('https://texts.bibliothecacatholica.com/provenance/'+e['id']+'.json','source record',True)+'.</p>')
        return ('<p class="small">Source: '+E('Thomas Aquinas. Summa Theologica, '+P['name']+'. '+e['label'].split(',')[0]+'.')+' '+a(e['source'],'Project Gutenberg record',True)+'. '+E(e['rights'])+' The full Project Gutenberg license is kept in the hosted text.</p>')
    other=('<p class="small">Also online, linked only: the same translation at '+a(NA,'New Advent',True)+' and the Latin text at '+a(CT,'Corpus Thomisticum',True)+'. Neither is copied here.</p>')
    pg_notice='<p class="small pg-notice">'+PG_NOTICE+'</p>'
    tr_notice=('<p class="small ocr-notice">The Supplement is not a Project Gutenberg text. It is Bibliotheca Catholica’s transcription of public-domain scans at the Internet Archive; '
               'obvious OCR errors were corrected, and passages marked “OCR uncertain” could not be confidently corrected, so check them against the linked scan page.</p>')
    SUPP_LINE=('<p class="small supp-line">From the Supplement, compiled after Aquinas’s death from his Commentary on the Sentences and transcribed here from the 1917 to 1922 printings. '+a('/summa/supp/','About the Supplement')+'.</p>')
    def NOTICE(P):return tr_notice if P['slug']=='supp' else pg_notice
    C=[('Discover & Read','library/'),(w['title'],'work/'+w['id']+'/')]
    flat=[(P,q,x) for P in S['parts'] for q in P['questions'] for x in q['articles']]
    qflat=[(P,q) for P in S['parts'] for q in P['questions']]
    total_a=len(flat);total_q=len(qflat)
    # /summa/
    parts_ul='<ul class="text-parts">'+''.join('<li>'+a('/summa/'+P['slug']+'/',P['name']+' ('+P['latin']+')')+': '+str(len(P['questions']))+' questions, '+str(sum(len(q['articles']) for q in P['questions']))+' articles</li>' for P in S['parts'])+'</ul>'
    body=(crumb_html(*C,('By question and article',''))+'<div class="page-head"><div class="eyebrow">Thomas Aquinas · Theology</div><h1>Summa Theologiae</h1>'
          +'<p class="lede">The whole Summa in English, one page for each of its '+str(total_q)+' questions and '+str(total_a)+' articles, from the four Project Gutenberg volumes in the reading room and a transcription of the Supplement.</p></div>'
          +'<p>Each article page has the objections, the reply “On the contrary,” the answer “I answer that,” and the replies to the objections, with a link into the reading room for notes and highlights. Article pages are at <code>/summa/&lt;part&gt;/q&lt;question&gt;/a&lt;article&gt;/</code>; for example '+a('/summa/1/q2/a3/','First Part, question 2, article 3')+', “Whether God Exists?”</p>'
          +'<h2>The four parts and the Supplement</h2>'+parts_ul
          +'<p class="small">Aquinas left the Third Part unfinished at question 90, where the Gutenberg files end. The '+a('/summa/supp/','Supplement')+', compiled from his earlier writings after his death, completes it here in '+str(len(SUPP['questions']))+' questions, transcribed from the 1917, 1921, and 1922 printings of the same translation.</p>'
          +'<p class="small">About this text: the English Dominican translation, first printed 1911 to 1925. A sample check on 2026-11-09 against pre-1931 printings at the Internet Archive found that the article text matches, with no 1947 introduction, synopsis, or index; “From the Complete American Edition” in Gutenberg’s catalog titles is a provenance note only.</p>'
          +'<p class="dl-row"><a class="btn" href="/work/'+w['id']+'/">Work page and editions</a> '+a('/editions/summa/','Edition guide')+'</p>'
          +''.join(edline(P) for P in S['parts'][:1])+other+pg_notice+tr_notice+'<p>'+a('/author/thomas-aquinas/','Thomas Aquinas')+' · '+a('/library/','Selected library')+' · '+a('/rights/','Rights badges')+'</p>')
    out['summa']=('Summa Theologiae by Question and Article — Bibliotheca Catholica',
        fit(['The Summa Theologiae of Thomas Aquinas in English, one free page for each of its %d questions and %d articles.'%(total_q,total_a)],(('Read in the reading room too.',''),)+DESC_EXTRA),
        body,[{'@context':'https://schema.org','@type':'Book','name':'Summa Theologiae','url':SITE+'summa/','author':ld_by,'isAccessibleForFree':True,'inLanguage':'English','hasPart':[{'@type':'Book','name':'Summa Theologiae, '+P['name'],'url':SITE+'summa/'+P['slug']+'/'} for P in S['parts']]},crumbs(*C,('By question and article','summa/'))])
    for pi,P in enumerate(S['parts']):
        B=blocks(P['edition']);CP=C+[('Summa',  'summa/'),(P['name'],'summa/'+P['slug']+'/')]
        tq={}
        for t in P['treatises']:
            for n in t['questions']:tq[n]=t
        li=[];last=None
        for q in P['questions']:
            t=tq.get(q['n'])
            if t is not last and t:li.append('</ol><h3>'+E(t['title'])+'</h3><ol class="text-parts" start="'+str(q['n'])+'">')
            last=t or last
            li.append('<li>'+a('/'+qpath(P,q)+'/',q['title'])+' <span class="small">('+str(len(q['articles']))+(' article' if len(q['articles'])==1 else ' articles')+')</span></li>')
        pro=''
        if P.get('prologue'):
            pro='<h2>Prologue</h2>'+''.join(para(P,B,i) for i in range(P['prologue'][0],P['prologue'][1]+1))
        nav='<nav class="reader-pagination" aria-label="Parts">'+(a('/summa/'+S['parts'][pi-1]['slug']+'/','← '+S['parts'][pi-1]['name']).replace('<a ','<a class="btn ghost" rel="prev" ',1) if pi else '')+'<span>'+('Part '+str(pi+1)+' of 4' if P['slug']!='supp' else 'Supplement to the Third Part')+'</span>'+(a('/summa/'+S['parts'][pi+1]['slug']+'/',S['parts'][pi+1]['name']+' →').replace('<a ','<a class="btn" rel="next" ',1) if pi<len(S['parts'])-1 else '')+'</nav>'
        na_=sum(len(q['articles']) for q in P['questions'])
        body=(crumb_html(*C,('Summa','summa/'),(P['name'],''))+'<div class="page-head"><div class="eyebrow">Summa Theologiae · '+E(P['token'])+'</div><h1>'+E(P['name'])+' <span class="small">('+E(P['latin'])+')</span></h1>'
              +'<p class="lede">'+by+', <cite>'+a('/summa/','Summa Theologiae')+'</cite>. '+str(len(P['questions']))+' questions, '+str(na_)+' articles.</p></div>'
              +'<p class="dl-row"><a class="btn" href="'+E(reader(P,P['start']))+'">Read in the reading room →</a> '+a('/work/'+w['id']+'/','Work page and editions')+'</p>'
              +(ABOUT_SUPP+'<p class="small">'+str(len(P['ocrFlags']))+' passages in the Supplement are marked “OCR uncertain” where the scan could not be read with confidence; each links to its scan page.</p>' if P['slug']=='supp' else '')
              +edline(P)+nav+NOTICE(P)+pro+'<h2>Questions</h2><ol class="text-parts">'+''.join(li)+'</ol>'+('<p class="small">Aquinas left the Third Part unfinished here, at question 90, where the Gutenberg files end. The '+a('/summa/supp/','Supplement')+' completes it.</p>' if P['slug']=='3' else '')+nav+other+source(P))
        body=body.replace('<ol class="text-parts"></ol>','')
        out['summa/'+P['slug']]=('Summa Theologiae, '+P['name']+' ('+P['latin']+') — Bibliotheca Catholica',
            fit(['The %s of the Summa Theologiae (%s) by Thomas Aquinas in English: %d questions and %d articles, each on its own free page.'%(P['name'],P['latin'],len(P['questions']),na_)],DESC_EXTRA),
            body,[{'@context':'https://schema.org','@type':'Book','name':'Summa Theologiae, '+P['name'],'url':SITE+'summa/'+P['slug']+'/','author':ld_by,'isPartOf':{'@type':'Book','name':'Summa Theologiae','url':SITE+'summa/'},'isAccessibleForFree':True,'inLanguage':'English'},crumbs(*CP)])
    for k,(P,q) in enumerate(qflat):
        B=blocks(P['edition']);CQ=C+[('Summa','summa/'),(P['name'],'summa/'+P['slug']+'/'),('Question '+str(q['n']),qpath(P,q)+'/')]
        pv=qflat[k-1] if k else None;nx=qflat[k+1] if k+1<len(qflat) else None
        lab=lambda PQ:PQ[0]['token']+', q. '+str(PQ[1]['n'])
        nav=('<nav class="reader-pagination" aria-label="Questions">'+(a('/'+qpath(*pv)+'/','← '+lab(pv)).replace('<a ','<a class="btn ghost" rel="prev" ',1) if pv else '')
             +'<span>'+E(P['token'])+', question '+str(q['n'])+' of '+str(len(P['questions']))+'</span>'+(a('/'+qpath(*nx)+'/',lab(nx)+' →').replace('<a ','<a class="btn" rel="next" ',1) if nx else '')+'</nav>')
        pro=''.join(para(P,B,i) for i in range(q['prologue'][0],q['prologue'][1]+1))
        arts='<ol class="text-parts">'+''.join('<li>'+a('/'+apath(P,q,x)+'/',x['title'])+'</li>' for x in q['articles'])+'</ol>'
        body=(crumb_html(*C,('Summa','summa/'),(P['name'],'summa/'+P['slug']+'/'),('Question '+str(q['n']),''))
              +'<div class="page-head"><div class="eyebrow">Summa Theologiae · '+E(qref(P,q))+'</div><h1>Question '+str(q['n'])+'. '+E(q['title'])+'</h1>'
              +'<p class="lede">'+by+', <cite>'+a('/summa/','Summa Theologiae')+'</cite>, '+a('/summa/'+P['slug']+'/',P['name'])+'. '+str(len(q['articles']))+(' article.' if len(q['articles'])==1 else ' articles.')+'</p></div>'
              +'<p class="dl-row"><a class="btn" href="'+E(reader(P,q['heading']))+'">Read in the reading room →</a> '+a(na(P,q),'This question at New Advent',True)+'</p>'
              +(SUPP_LINE if P['slug']=='supp' else '')+edline(P)+nav+NOTICE(P)+'<article class="reading-text" aria-label="'+E('Question '+str(q['n']))+'">'+pro+'</article>'
              +'<h2>Articles</h2>'+arts+nav+other+source(P))
        out[qpath(P,q)]=('Summa Theologiae '+qref(P,q)+': '+q['title']+' — Bibliotheca Catholica',
            fit(['Summa Theologiae, %s, question %d: %s.'%(P['name'],q['n'],q['title'].rstrip('?.')),'The question’s opening and its %d article%s, by Thomas Aquinas, free in English.'%(len(q['articles']),'' if len(q['articles'])==1 else 's')],DESC_EXTRA),
            body,[{'@context':'https://schema.org','@type':'Chapter','name':'Question '+str(q['n'])+'. '+q['title'],'url':SITE+qpath(P,q)+'/','position':q['n'],'isPartOf':{'@type':'Book','name':'Summa Theologiae, '+P['name'],'url':SITE+'summa/'+P['slug']+'/','author':ld_by},'isAccessibleForFree':True,'inLanguage':'English'},crumbs(*CQ)])
    for k,(P,q,x) in enumerate(flat):
        B=blocks(P['edition'])
        pv=flat[k-1] if k else None;nx=flat[k+1] if k+1<len(flat) else None
        lab=lambda T:T[0]['token']+', q. '+str(T[1]['n'])+', a. '+str(T[2]['n'])
        nav=('<nav class="reader-pagination" aria-label="Articles">'+(a('/'+apath(*pv)+'/','← '+lab(pv)).replace('<a ','<a class="btn ghost" rel="prev" ',1) if pv else '')
             +'<span>Article '+str(x['n'])+' of '+str(len(q['articles']))+'</span>'+(a('/'+apath(*nx)+'/',lab(nx)+' →').replace('<a ','<a class="btn" rel="next" ',1) if nx else '')+'</nav>')
        text=''.join(para(P,B,i) for i in range(x['start'],x['end']+1));nf=flagged(P,x['heading'],x['end'])
        fl=('<p class="small ocr-count">'+('One passage' if nf==1 else str(nf)+' passages')+' on this page '+('is' if nf==1 else 'are')+' marked “OCR uncertain”; check '+('it' if nf==1 else 'them')+' against the scan.</p>') if nf else ''
        body=(crumb_html(*C,('Summa','summa/'),(P['name'],'summa/'+P['slug']+'/'),('Question '+str(q['n']),qpath(P,q)+'/'),('Article '+str(x['n']),''))
              +'<div class="page-head"><div class="eyebrow">Summa Theologiae · '+E(aref(P,q,x))+'</div><h1>'+E(x['title'])+'</h1>'
              +'<p class="lede">'+by+', <cite>'+a('/summa/','Summa Theologiae')+'</cite>, '+a('/summa/'+P['slug']+'/',P['name'])+', '+a('/'+qpath(P,q)+'/','question '+str(q['n'])+', '+q['title'])+', article '+str(x['n'])+'. About '+str(max(1,round(x['words']/200)))+' min.</p></div>'
              +'<p class="dl-row"><a class="btn" href="'+E(reader(P,x['heading']))+'">Read in the reading room →</a> '+a(na(P,q,x),'This article at New Advent',True)+'</p>'
              +(SUPP_LINE if P['slug']=='supp' else '')+edline(P)+nav+NOTICE(P)+fl+'<article class="reading-text" aria-label="'+E(aref(P,q,x))+'">'+text+'</article>'+nav+other+source(P))
        if (P['slug'],q['n'],x['n'])==('1',2,1):
            assert re.search(r'Q\. 3, Art\. 4',text)
            body+='<aside><h2>References in this article</h2>'+a('/summa/1/q3/a4/','I, q. 3, a. 4 · Whether essence and existence are the same in God?')+'</aside>'
        out[apath(P,q,x)]=('Summa Theologiae '+aref(P,q,x)+': '+x['title']+' — Bibliotheca Catholica',
            fit(['Summa Theologiae, %s, question %d, article %d: %s'%(P['name'],q['n'],x['n'],x['title'] if x['title'].endswith(('?','.')) else x['title']+'.'),'The objections, the answer, and the replies by Thomas Aquinas, free in English.'],DESC_EXTRA),
            body,[{'@context':'https://schema.org','@type':'Article','headline':x['title'][:110],'name':aref(P,q,x)+': '+x['title'],'url':SITE+apath(P,q,x)+'/','author':ld_by,'isPartOf':{'@type':'Chapter','name':'Question '+str(q['n'])+'. '+q['title'],'url':SITE+qpath(P,q)+'/'},'isAccessibleForFree':True,'inLanguage':'English'},
                  crumbs(*C,('Summa','summa/'),(P['name'],'summa/'+P['slug']+'/'),('Question '+str(q['n']),qpath(P,q)+'/'),('Article '+str(x['n']),apath(P,q,x)+'/'))])
    return S
def summa_work_html(S):
    return ('<h2>By question and article</h2><p>'+a('/summa/','The whole Summa, one page per question and article')+': '+', '.join(a('/summa/'+P['slug']+'/',P['name']) for P in S['parts'][:-1])+', and '+a('/summa/'+S['parts'][-1]['slug']+'/',S['parts'][-1]['name'])+'.</p>')
def main():
    tpl=(ROOT/'index.html').read_text();global GA_TAG;GA_TAG=ga_tag(tpl);hub=json.loads((ROOT/'data/catholic-hub.json').read_text())
    lib=json.loads((ROOT/'data/library.json').read_text());guide=jsvar('data/guide.js','GUIDE_DATA');flags=load_flags();plans=json.loads((ROOT/'data/reading-plans.json').read_text())['plans']
    skip_auth=set(flags.get('hubAuthors',[]))
    eras={e['id']:e['label'] for e in hub['eras']}
    out={}  # route -> html
    SD=json.loads((ROOT/'data/saints.json').read_text());saints=SD['saints']
    saints_by_author={x['author_id']:x for x in saints if x['tier']==1 and x.get('author_id')}
    libw={w['id']:w for w in lib['works']}
    auth_ids={x['id'] for x in hub['authors'] if x['id'] not in skip_auth}
    # Phase A item 3: onward links between work, author, edition-guide, reading-list, and saint pages (all from existing data)
    gid={e['id']:e for e in guide['editions']}
    guides_for,lists_for,saints_for={}, {}, {}
    for ed in guide['editions']:
        for wid in ed.get('workIds') or []:guides_for.setdefault(wid,[]).append(ed)
    list_guides={}
    for L in guide['lists']:
        for i in L['items']:
            for wid in (i.get('workIds') or [])+(gid[i['e']].get('workIds') or [] if i.get('e') in gid else []):
                if L not in lists_for.setdefault(wid,[]):lists_for[wid].append(L)
            if i.get('e') in gid and L not in list_guides.setdefault(i['e'],[]):list_guides[i['e']].append(L)
    for x in saints:
        if x['id'] in skip_auth:continue
        for wid in x.get('reading_room_works') or []:
            if x not in saints_for.setdefault(wid,[]):saints_for[wid].append(x)
    for b in SD['shelf']:
        for sid in b.get('about') or []:
            x=next((y for y in saints if y['id']==sid and y['id'] not in skip_auth),None)
            if x and b.get('work_id') and x not in saints_for.setdefault(b['work_id'],[]):saints_for[b['work_id']].append(x)
    s_href=lambda x:'/author/'+x['author_id']+'/' if x['tier']==1 and x.get('author_id') else '/saints/'+x['id']+'/'
    shelf_works={b['work_id'] for b in SD['shelf'] if b.get('work_id') in libw}
    def same_author(w):
        k=w.get('authorId') or w['author']
        return [v for v in lib['works'] if v['id']!=w['id'] and (v.get('authorId') or v['author'])==k]
    BK=json.loads((ROOT/'data/books.json').read_text())
    iso_names={}  # hub author id -> the name its Isidore books carry most often
    for bk in BK['books']:
        for ai in bk[2]:
            nm,hid=BK['authors'][ai][0],BK['authors'][ai][1]
            if hid:iso_names.setdefault(hid,{});iso_names[hid][nm]=iso_names[hid].get(nm,0)+1
    head=lambda eyebrow,h1,lede:'<div class="page-head"><div class="eyebrow">'+E(eyebrow)+'</div><h1>'+E(h1)+'</h1><p class="lede">'+E(lede)+'</p></div>'
    authors=[x for x in hub['authors'] if x['id'] not in skip_auth]
    # Phase A item 2: authors with no hosted work get tools/author_pages.py sections instead of the Wikipedia excerpt
    import author_pages as AP
    hosted_auth={w['authorId'] for w in lib['works'] if w.get('authorId') and any(e.get('text') for e in w['editions'])}
    RJ=json.loads((ROOT/'data/rights.json').read_text());AX=jsvar('data/authorx.js','AUTHORX')['by'];BSID=AP.bookshop_id(ROOT);DISCL=AP.disclosure(ROOT)
    fbooks=set((flags.get('books') or {}).keys());books_by={}
    for bk in BK['books']:
        for ai in bk[2]:
            hid=BK['authors'][ai][1]
            if hid and str(bk[0]) not in fbooks:books_by.setdefault(hid,[]).append(bk)  # as app.js B.by, flagged books left out
    for au in authors:
        desc=au.get('desc') or au.get('wikiDesc') or ''
        lede=desc
        # v18: the Wikipedia excerpt is its own block with the credit CC BY-SA 4.0 asks for (article link, license link, "shortened")
        wk=next((l['url'] for l in au.get('links') or [] if 'wikipedia.org/wiki/' in l.get('url','')),None)
        wiki_block=''
        if au.get('extract') and au['extract'] not in desc:
            wt=urllib.parse.unquote(wk.split('/wiki/')[1]).replace('_',' ') if wk else au['name']
            wiki_block=('<blockquote class="extract"><p>'+E(au['extract']+('…' if len(au['extract'])>=595 else ''))+'</p></blockquote>'
              '<p class="small wiki-credit">Shortened excerpt from the Wikipedia article '+(a(wk,'“'+wt+'”',True) if wk else '“'+E(wt)+'”')+', available under '+a(CC_BY_SA,'CC BY-SA 4.0',True)+'.</p>')
        works=''.join('<li>'+a(w['url'],w['title'],True)+'</li>' for w in au.get('works') or [] if w.get('url'))
        mine=[w for w in lib['works'] if w.get('authorId')==au['id']]
        # v18.1: the 211 former isidore.co folder links became internal Isidore Index searches (#/isidore/<catalog name>)
        # v18.2: the search uses the author name as the books carry it (hub.isidore `a`, else `n`) and shows all subjects
        iso_n=next((i.get('a') or i['n'] for i in hub['isidore'] if i['f']==au.get('isidoreFolder')),None) if au.get('isidoreFolder') else None
        if not iso_n and iso_names.get(au['id']):iso_n=max(iso_names[au['id']].items(),key=lambda kv:(kv[1],kv[0]))[0]  # Phase A: mapped books, no folder
        # Phase A item 3: the hash search has no static page, so /isidore/ (pre-rendered) is the crawlable fallback beside it
        iso_link=('<p>'+a('/#/isidore/author='+urllib.parse.quote(iso_n,safe=''),'All their books in the Isidore Index')+' · '+a('/isidore/','Browse the Isidore Index')+'</p>') if iso_n else ''
        au_guides=[e for e in guide['editions'] if e.get('aid')==au['id']]
        if au_guides:iso_link=('<h2>Edition guides</h2><ul>'+''.join('<li>'+a('/editions/'+e['id']+'/',e['t'])+'</li>' for e in au_guides)+'</ul>')+iso_link
        official=[]
        if au['id'] not in hosted_auth:
            wiki_block=''  # no Wikipedia excerpt; the Wikipedia link stays in More sources
            bks=sorted(books_by.get(au['id'],[]),key=lambda b:(re.sub(r'^(the|a|an) ','',b[1].casefold()),b[0]))
            n_online=sum(1 for w in au.get('works') or [] if w.get('url'))
            intro='<p class="au-intro">'+E(AP.intro(au,eras.get(au.get('era'),''),len(bks),len(au_guides),n_online))+'</p>'
            def ed_badge(w):
                return AP.badge(next((x for x in (AP.edition(e) for e in w['editions']) if x),None))
            lib_html=('<h2>In our library (read at the source)</h2><ul>'+''.join('<li>'+a('/work/'+w['id']+'/',w['title'])+ed_badge(w)+'</li>' for w in mine)+'</ul>') if mine else ''
            bk_html=('<h2>Books in the Isidore Index</h2><p class="small">Each title opens its catalog record on isidore.co. We do not host these books; the badge says what the record allows.</p><ul class="au-books">'+''.join('<li>'+a(BK['server']+'legacy/book/'+str(b[0])+'/CalibreLibrary',b[1],True)+(' ('+str(b[3])+')' if b[3] else '')+AP.badge(AP.resolve(RJ,b[0]))+'</li>' for b in bks)+'</ul>') if bks else ''
            gd_html=''
            if au_guides:
                buys=0;li=[]
                for e in au_guides:
                    btn=[]
                    for pk in (e.get('picks') or []) if AP.AUTHOR_GUIDE_BOOKSHOP_BUTTONS else []:
                        if re.fullmatch(r'97[89]\d{10}',pk.get('isbn') or ''):
                            btn.append('<a class="buy-b bs" href="https://bookshop.org/a/'+BSID+'/'+pk['isbn']+'" target="_blank" rel="noopener sponsored">Bookshop.org: '+E(pk.get('lbl') or pk.get('tr') or e['t'])+(' ('+E(pk['pub'])+')' if pk.get('pub') else '')+'</a>')
                    buys+=len(btn)
                    li.append('<li>'+a('/editions/'+e['id']+'/',e['t'])+(': '+E(e['why']) if e.get('why') else '')+('<div class="buy">'+''.join(btn)+'</div>' if btn else '')+'</li>')
                gd_html='<h2>Edition guides</h2><ul>'+''.join(li)+'</ul>'+(DISCL if buys else '')
            official=AP.official(au,AX.get(au['id'],{}))
            of_html=('<h2>Official site, talks, and podcasts</h2><ul>'+''.join('<li>'+a(u,t,True)+'</li>' for t,u,k in official)+'</ul>') if official else ''
            iso_only=('<p>'+a('/#/isidore/author='+urllib.parse.quote(iso_n,safe=''),'All their books in the Isidore Index')+' · '+a('/isidore/','Browse the Isidore Index')+'</p>') if iso_n else ''
            body=head(eras.get(au.get('era'),'Catholic author'),au['name']+years(au),lede)+intro+AP.books_html(au,E,a)+lib_html+bk_html+(('<h2>Works online</h2><ul>'+works+'</ul>') if works else '')+gd_html+of_html+iso_only+'<p>'+a('/authors/','All authors')+'</p>'
        else:
          body=head(eras.get(au.get('era'),'Catholic author'),au['name']+years(au),lede)+wiki_block+(('<h2>Read here</h2><ul>'+''.join('<li>'+a('/work/'+w['id']+'/',w['title'])+'</li>' for w in mine)+'</ul>') if mine else '')+(('<h2>Works online</h2><ul>'+works+'</ul>') if works else '')+iso_link+'<p>'+a('/authors/','All authors')+'</p>'
        sa=saints_by_author.get(au['id'])
        if sa:body=body.replace('<p>'+a('/authors/','All authors')+'</p>','<h2>Saint</h2><p>'+E(s_facts(sa))+' '+a('/saints/','Saints & Hagiography')+'</p><p>'+a('/authors/','All authors')+'</p>')
        # v17: facts already in the data (era, century, vocations from tags, Doctor of the Church) and the curated links
        era=eras.get(au.get('era'));tags=[TAGL[t] for t in au.get('tags',[]) if t in TAGL]
        facts=[]
        if era:facts.append('Era: '+era+(' ('+ORDINAL(au['century'])+' century)' if isinstance(au.get('century'),int) and au['century']>0 and au.get('era')!=ORDINAL(au['century'])+'-century' else '')+'.')  # v18.2: the century once
        if tags:facts.append(oxford(tags)[0].upper()+oxford(tags)[1:]+'.')
        if au.get('doctor'):facts.append('Doctor of the Church.')
        # never isidore.co folder listings or raw files (rights rule 10): book pages and outside sites only
        shown={u for t,u,k in official}
        more=[a(l['url'],l['label'],True) for l in au.get('links') or [] if l.get('url') and l['url'] not in shown and not re.search(r'isidore\.co/(CalibreLibrary/|get/|calibre/get)',l['url'])]
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
    def work_related(w):
        r=[]
        for ed in guides_for.get(w['id'],[]):r.append('Edition guide: '+a('/editions/'+ed['id']+'/',ed['t']))
        for L in lists_for.get(w['id'],[]):r.append('Reading list: '+a('/reading/'+L['id']+'/',L['t']))
        for x in saints_for.get(w['id'],[]):
            h=s_href(x)
            if h!='/author/'+str(w.get('authorId'))+'/':r.append(('Author page: ' if h.startswith('/author/') else 'Saint: ')+a(h,x['name']))
        sa=same_author(w)
        if sa:r.append('More by '+E(w['author'])+': '+', '.join(a('/work/'+v['id']+'/',v['title']) for v in sa[:8]))
        if w['id'] in shelf_works:r.append(a('/saints/books/','The hagiography shelf'))
        if len(r)<2:  # few onward links: up to six other works of the same category, in library order
            cat=[v for v in lib['works'] if v['category']==w['category'] and v['id']!=w['id'] and v not in sa][:6]
            if cat:r.append('More in '+E(w['category'])+': '+', '.join(a('/work/'+v['id']+'/',v['title']) for v in cat))
        return ('<h2>Related</h2><ul>'+''.join('<li>'+x+'</li>' for x in r)+'</ul>') if r else ''
    RA={x:ra for ra in lib.get('relatedAuthors',[]) for x in ra['workIds']}  # work id -> related author (deep-link gaps)
    ra_badge=lambda ra:'<span class="ef-badge tradition-badge" title="'+E(ra['evidence'])+'">'+E(ra['badge']+' · '+ra['tradition'])+'</span>'
    related_authors(out,lib,ra_badge)
    def byline(w):
        if w.get('authorId') in auth_ids:return a('/author/'+w['authorId']+'/',w['author'])
        if w['id'] in RA:return a('/author/'+RA[w['id']]['id']+'/',w['author'])+' '+ra_badge(RA[w['id']])
        return E(w['author'])
    TPD=part_pages(out,lib,lambda w:(a('/author/'+w['authorId']+'/',w['author']) if w.get('authorId') in auth_ids else E(w['author'])),
                   lambda w:dict({'@type':'Person','name':w['author']},**({'url':SITE+'author/'+w['authorId']+'/'} if w.get('authorId') in auth_ids else {})))
    SUMMA=summa_pages(out,lib) if (ROOT/'data/summa.json').exists() else None
    for w in lib['works']:
        eds=''.join('<li>'+E(e['label'])+''.join(' · '+E(c['role'])+': '+E(c['name']) for c in e.get('contributors',[]) if 'translat' in c['role'].lower())+(' · '+a('/#/read/'+w['id']+'/'+e['id'],'Read here') if e.get('text') else '')+' · '+a(e['source'],'Source',True)+'</li>' for e in w['editions'])
        d=w.get('description') or (w['title']+' by '+w['author']+': free reading edition with source, credits, and rights notes.')
        hosted=any(e.get('text') for e in w['editions'])
        by=byline(w)
        ra=RA.get(w['id']);ra_note=ra_note_html(ra,libw,True) if ra and w['id'] in ra.get('noteWorks',[]) else ''
        body=crumb_html(('Discover & Read','library/'),(w['title'],''))+head(w['category']+' · '+w['tradition'],w['title'],w['author']+'. '+d)+'<p>By '+by+'. '+E(str(len(w['editions']))+(' edition' if len(w['editions'])==1 else ' editions')+(', with a text you can read on this site.' if hosted else ', each linked at its source.'))+'</p>'+ra_note+'<h2>Reading editions &amp; sources</h2><ul>'+eds+'</ul>'+(parts_list(w['id'],TPD[w['id']]) if w['id'] in TPD else '')+(summa_work_html(SUMMA) if SUMMA and w['id']==SUMMA['work'] else '')+series_html(w,lib,TPD)+work_related(w)+'<p>'+a('/library/','Selected library')+' · '+a('/rights/','Rights badges')+'</p>'
        book={'@context':'https://schema.org','@type':'Book','name':w['title'],'url':SITE+'work/'+w['id']+'/','author':{'@type':'Person','name':w['author']},'description':d,'genre':w['category']}
        if w.get('authorId') in auth_ids:book['author']['url']=SITE+'author/'+w['authorId']+'/'
        elif w['id'] in RA:book['author']['url']=SITE+'author/'+RA[w['id']]['id']+'/'
        langs=sorted({e['language'] for e in w['editions'] if e.get('language')})
        if langs:book['inLanguage']=langs[0] if len(langs)==1 else langs
        if hosted:book['isAccessibleForFree']=True
        md=fit([w['title']+' by '+w['author']+':',d.rstrip('.')+'.'],(('Read it free online, with source and rights notes.','Read it free online.') if hosted else ('Editions and sources, with rights notes.','Editions and sources.'),)+DESC_EXTRA)
        out['work/'+w['id']]=(w['title']+' — Bibliotheca Catholica',md,body,[book,crumbs(('Discover & Read','library/'),(w['title'],'work/'+w['id']+'/'))])
    def ed_related(ed):
        r=[]
        if ed.get('aid') in auth_ids:r.append('Author: '+a('/author/'+ed['aid']+'/',ed.get('a') or ed['aid']))
        for wid in ed.get('workIds') or []:
            if wid in libw:r.append('In the reading room: '+a('/work/'+wid+'/',libw[wid]['title']))
        for L in list_guides.get(ed['id'],[]):r.append('Reading list: '+a('/reading/'+L['id']+'/',L['t']))
        return ('<h2>Related</h2><ul>'+''.join('<li>'+x+'</li>' for x in r)+'</ul>') if r else ''
    for ed in guide['editions']:
        picks=''.join('<li><b>'+E(p.get('lbl',''))+':</b> '+E(p.get('tr',''))+(' ('+E(p['pub'])+')' if p.get('pub') else '')+'</li>' for p in ed.get('picks',[]))
        body=head('Editions & Translations · '+ed.get('cat',''),ed['t'],(ed.get('a')+'. ' if ed.get('a') else '')+ed.get('why',''))+'<ol>'+picks+'</ol>'+('<p>Also good: '+E(ed['alt'])+'</p>' if ed.get('alt') else '')+ed_related(ed)+'<p>'+a('/editions/','All edition guides')+'</p>'
        body=crumb_html(('Editions & Translations','editions/'),(ed['t'],''))+body
        md=fit(['Which edition of '+ed['t']+(' by '+ed['a'] if ed.get('a') else '')+' to read:',ed.get('why','').rstrip('.')+'.'],(('Recommended translations, free texts, and print copies.','Translations, free texts, and print copies.','Translations compared.'),('Compare translations at Bibliotheca Catholica.','At Bibliotheca Catholica.')))
        out['editions/'+ed['id']]=(ed['t']+': Editions & Translations — Bibliotheca Catholica',md,body,[crumbs(('Editions & Translations','editions/'),(ed['t'],'editions/'+ed['id']+'/'))])
    for L in guide['lists']:
        items=''.join('<li>'+list_item_title(i,gid,libw)+(': '+E(i['b']) if i.get('b') else '')+'</li>' for i in L['items'])
        body=head('Reading list',L['t'],L.get('sub',''))+'<ol>'+items+'</ol><p>'+a('/reading/','All reading lists')+'</p>'
        md=fit([L['t']+', a Catholic reading list:',L.get('sub','').rstrip('.')+'.'],((str(len(L['items']))+' books, with edition guides and free texts.',str(len(L['items']))+' books.'),)+DESC_EXTRA)
        out['reading/'+L['id']]=(L['t']+' — Reading Lists — Bibliotheca Catholica',md,crumb_html(('Reading Lists','reading/'),(L['t'],''))+body,[crumbs(('Reading Lists','reading/'),(L['t'],'reading/'+L['id']+'/'))])
    # v20 dated reading plans (data/reading-plans.json from tools/build_reading_plans.py); see docs/READING-GUIDES.md
    for P in plans:
        out['reading/'+P['id']]=(P['t']+' '+str(P['year'])+': a daily reading plan — Bibliotheca Catholica',PLAN_DESC[P['id']],plan_html(P),[crumbs(('Reading Lists','reading/'),(P['t'],'reading/'+P['id']+'/'))])
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
        elif k=='related':extra='<h2>Writers with their own pages</h2><ul>'+''.join('<li>'+a('/author/'+ra['id']+'/',ra['name']+' ('+str(ra['born'])+'–'+str(ra['died'])+')')+' · '+E(ra['badge']+' · '+ra['tradition'])+'</li>' for ra in lib.get('relatedAuthors',[]))+'</ul>'
        elif k=='authors':extra='<ul>'+''.join('<li>'+a('/author/'+x['id']+'/',x['name']+years(x))+'</li>' for x in authors)+'</ul>'
        elif k=='library':extra='<ul>'+''.join('<li>'+a('/work/'+w['id']+'/',w['title']+' — '+w['author'])+'</li>' for w in lib['works'])+'</ul>'
        elif k=='editions':extra='<ul>'+''.join('<li>'+a('/editions/'+e['id']+'/',e['t'])+'</li>' for e in guide['editions'])+'</ul>'
        elif k=='saints':extra='<ul>'+''.join('<li>'+a(s_href(x),x['name'])+' — '+E(s_status(x))+(' · Vatican News: '+E(s_vn(x)) if x['feasts']['vatican_news'] else '')+(' · '+E(FLAGL[x['historicity']['flag']]) if x.get('historicity') else '')+'</li>' for x in sorted(saints,key=lambda x:x['name']))+'</ul><p>'+a('/saints/books/','The hagiography shelf')+' · '+a('/saints/about/','Sources & method')+'</p>'
        elif k=='reading':extra='<h2>Reading plans</h2><ul>'+''.join('<li>'+a('/reading/'+P['id']+'/',P['t']+' ('+str(len(P['days']))+' days, '+PLAN_SPAN(P)+')')+'</li>' for P in plans)+'</ul><h2>Reading lists</h2><ul>'+''.join('<li>'+a('/reading/'+L['id']+'/',L['t'])+'</li>' for L in guide['lists'])+'</ul>'
        elif k=='doctors':extra='<ul>'+''.join('<li>'+a('/author/'+x['id']+'/',x['name']+years(x))+'</li>' for x in authors if x.get('doctor'))+'</ul>'
        intro='<p class="section-intro">'+E(INTRO[k])+'</p>' if k in INTRO else ''
        out[k]=(t+' — Bibliotheca Catholica',fit([d],DESC_EXTRA),head('Bibliotheca Catholica',t,d)+intro+extra,[crumbs((t,k+'/'))])
    if flags.get('policy_html'):
        out['policy']=('Fidelity & Editorial Policy — Bibliotheca Catholica','Bibliotheca Catholica is faithful to the Magisterium. Listing is not endorsement; flagged records carry calm context notes. Privacy and how to report a concern.',flags['policy_html'],[crumbs(('Fidelity & Editorial Policy','policy/'))])
    # v16 rights pages: same HTML as the app (data/rights-pages.js, written by tools/build_rights.py from tools/rights_pages.py)
    rp=json.loads((ROOT/'data/rights-pages.js').read_text().strip()[len('window.RIGHTS_PAGES='):-1])
    out['rights']=('Rights & Permissions — Bibliotheca Catholica','What the five Bibliotheca Catholica rights badges mean, how each status is decided, and when downloads are shown. Not legal advice.',rp['rights'],[crumbs(('Rights & Permissions','rights/'))])
    out['takedown']=('Takedown requests — Bibliotheca Catholica','How a rights holder can ask Bibliotheca Catholica to remove a text, a link, or a record’s file links, and how to send a counter-notice. Not legal advice.',rp['takedown'],[crumbs(('Takedown requests','takedown/'))])
    out['licensing']=('Licensing & credits — Bibliotheca Catholica','How Bibliotheca Catholica is licensed: code MIT, open data CC0, site writing CC BY 4.0, texts public domain in the US, plus Wikipedia and portrait credits.',rp['licensing'],[crumbs(('Licensing & credits','licensing/'))])
    # Steering C (2026-11-03) help guides: same HTML as the app (data/guides.js, written by tools/build_guides.py from tools/guide_pages.py)
    gj=json.loads((ROOT/'data/guides.js').read_text().strip()[len('window.GUIDES='):-1]);sys.path.insert(0,str(ROOT/'tools'));import guide_pages
    for k,g in gj.items():
        out['guides/'+k]=(g['title']+' — Bibliotheca Catholica',guide_pages.PAGES[k]['desc'],g['html'],[crumbs((g['title'],'guides/'+k+'/'))])
    # v19 Rites & Liturgy: same HTML as the app (data/rites.js, written by tools/build_rites.py from tools/rites_pages.py),
    # with the map inlined and shaded for the default layer so the pages work without JavaScript
    sys.path.insert(0,str(ROOT/'tools'));import rites_pages
    rj=json.loads((ROOT/'data/rites.js').read_text().strip()[len('window.RITES_DATA='):-1])
    for k,pg in rj['pages'].items():
        route='rites/'+k if k else 'rites'
        cr=[('Rites & Liturgy','rites/')]+([(pg['h1'] if k!='sources' else 'Sources and method',route+'/')] if k else [])
        out[route]=(pg['title']+' — Bibliotheca Catholica',pg['desc'],rites_pages.expand(pg['html'],rj),[crumbs(*cr)])
    counts={'authors':len(authors),'saints':len(saints),'books':6633,'hosted':sum(1 for w in lib['works'] if any(e.get('text') for e in w['editions']))}
    m=re.search(r'window\.BOOKS_COUNT=(\d+)',tpl)
    if m:counts['books']=int(m.group(1))
    out['about']=('About the library — Bibliotheca Catholica','About Bibliotheca Catholica: what the free Catholic library holds, where its texts come from, the 1931 rule, rights badges, editorial policy, and goals.',site_copy.about_page(counts),[crumbs(('About the library','about/'))])
    directory=head('Find a text','Search and browse the library','Use the search box for interactive results. Without JavaScript, browse the titles and authors below, or use your browser’s Find command.')
    directory+='<h2>Selected reading editions</h2><ul class="search-browse">'+''.join('<li>'+a('/work/'+w['id']+'/',w['title'])+' — '+E(w['author'])+'</li>' for w in sorted(lib['works'],key=lambda w:w['title'].casefold()))+'</ul>'
    directory+='<h2>Authors</h2><ul class="search-browse">'+''.join('<li>'+a('/author/'+au['id']+'/',au['name'])+'</li>' for au in sorted(authors,key=lambda au:au['name'].casefold()))+'</ul>'
    directory+='<p>'+a('/saints/','Saints & Hagiography')+' · '+a('/editions/','Editions & Translations')+' · '+a('/reading/','Reading Lists')+'</p>'
    out['search']=('Search and browse — Bibliotheca Catholica','Search Bibliotheca Catholica for people and titles, or browse the plain directory of selected reading editions and Catholic authors without JavaScript.',directory,[crumbs(('Search and browse','search/'))])
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
    # Build the shared template first, so every entry page gets the same copy token, date, and build ID.
    write_home(tpl,counts,hub['generated'])
    tpl=(ROOT/'index.html').read_text()
    # Phase A item 3: a hash route that has a pre-rendered page becomes its real path (#/policy -> /policy/), so crawlers follow it.
    # Hash routes with no static page (#/read/..., #/isidore/author=...) stay, each beside a real fallback link.
    unhash=lambda body:re.sub(r'href="/?#/([a-z0-9/-]+?)/?"',lambda m:'href="/'+m.group(1)+'/"' if m.group(1) in out else m.group(0),body)
    for route,v in out.items():
        t,d,body=v[:3];body=unhash(body);f=ROOT/route/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(page(tpl,route,t,d,body,jsonld=v[3] if len(v)>3 else ()))
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
