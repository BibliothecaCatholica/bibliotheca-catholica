"""HTML for the Rites & Liturgy section (v19). One source for the app (data/rites.js, written by
tools/build_rites.py) and the static pages (tools/build_static.py). Links are crawlable paths.
Rules (docs/RITES.md): every fact carries its source link; a low-confidence field is never shown as
plain fact ("Unverified" marker or "Not yet verified"); no population numbers; no em-dashes."""
from html import escape
import re
def E(s):return escape(str(s),quote=True)
NYV='<span class="rites-nyv">Not yet verified</span>'
UNV='<span class="rites-unv" title="Low confidence in our sources. Shown with its source; check before relying on it.">Unverified</span>'
RLABEL={'public_domain_us':'Public domain (US)','open_license':'Open license','permission_granted':'Permission granted','link_only':'Link only','unknown':'Unknown'}
DISCLAIMER='Borders are illustrative (Natural Earth, de facto lines) and imply no position. Shading shows where a Church has its own jurisdiction, not where all its faithful live.'
LEGEND_P='Countries with the Church\'s own jurisdiction; faithful elsewhere are served by local ordinaries.'
LEGEND_H='Approximate historical heartland. Whole countries are shaded; the heartland itself is a smaller region.'
HOSTS=[('gcatholic.org','GCatholic'),('cnewa.org','CNEWA'),('wikidata.org','Wikidata'),('newadvent.org','Catholic Encyclopedia'),('archive.org','Internet Archive'),('press.vatican.va','Holy See Press Office'),
       ('cultodivino.va','Dicastery for Divine Worship'),('vatican.va','Holy See'),('chiesadimilano.it','Chiesa di Milano'),('diocese-braga.pt','Archdiocese of Braga'),('ctsbooks.org','CTS'),('mci.archpitt.org','Byzantine Catholic Metropolia of Pittsburgh'),
       ('cardenaldonmarcelo.es','Fundación Cardenal Don Marcelo'),('icelweb.org','ICEL'),('divinumofficium.com','Divinum Officium'),('naturalearthdata.com','Natural Earth'),('jfly.uni-koeln.de','Okabe and Ito'),('github.com/nvkelso','Natural Earth on GitHub')]
def host(u):
    for h,l in HOSTS:
        if h in u:
            if 'codex-can-eccl-orient' in u:return 'CCEO, vatican.va'
            if 'ENG0015' in u:return 'Catechism, vatican.va'
            return l
    return re.sub(r'^https?://(www\.)?','',u).split('/')[0]
def ext(u,label=None):return '<a href="'+E(u)+'" target="_blank" rel="noopener">'+E(label or host(u))+' ↗</a>'
def srcs(urls):
    urls=[u for u in (urls or []) if u]
    return ' <span class="rsrc">(Source: '+', '.join(ext(u) for u in urls)+')</span>' if urls else ''
def fact(f,extra=''):
    if not f:return NYV
    return (UNV+' ' if f.get('unv') else '')+E(f['v'])+extra+srcs(f['s'])
def badge(r):
    return '<a class="rights-badge rb-'+r['rights'].replace('_','-')+'" href="/rights/" data-rights="'+r['rights']+'" title="'+E(RLABEL[r['rights']]+'. '+r['evidence']+' Checked '+r['checked']+'. Not legal advice.')+'"><span class="rb-k">Rights:</span> '+E(RLABEL[r['rights']])+'</a>'
def crumbs(*items):
    L=[('Bibliotheca Catholica','/')]+list(items[:-1])
    return '<nav class="crumbs small" aria-label="Breadcrumb">'+' › '.join('<a href="'+E(u)+'">'+E(n)+'</a>' for n,u in L)+' › <span aria-current="page">'+E(items[-1][0])+'</span></nav>'
def head(eyebrow,h1,lede):return '<div class="page-head"><div class="eyebrow">'+E(eyebrow)+'</div><h1>'+E(h1)+'</h1><p class="lede">'+E(lede)+'</p></div>'
def fit(cands):
    for c in cands:
        c=re.sub(r'\s+',' ',c).strip()
        if 150<=len(c)<=160:return c
    raise ValueError('no description of 150-160 characters: '+' | '.join('%d %s'%(len(c),c) for c in cands))
def rec_desc(r,fam):
    short={'Constantinopolitan (Byzantine)':'Byzantine'}.get(fam['label'],fam['label'])
    cores=[r['name']+': a Church sui iuris of the '+fam['long']+'.',r['name']+': a Church sui iuris of the '+short+' tradition.',r['name']+', a '+short+' Church sui iuris.'] if r['kind']=='church' else [r['name']+': a rite or use within the Latin Church.',r['name']+', within the Latin Church.']
    tails=['Its status, head, countries, liturgical books, history, and sources, with public-domain texts to read.','Status, head, countries with its own jurisdiction, liturgical books, history, and sources.',
           'Status, head, countries, liturgical books, history, sources, and public-domain texts.','Status, head, countries, liturgical books, history, and sources.','Status, head, countries, books, history, and sources.',
           'Where it is found, its liturgical books, history, and sources, with public-domain texts to read.','Where it is found, its liturgical books, its history, and sources, with free texts.','Its books, history, and sources, with free texts.','Status, head, countries, books, and history.','Status, countries, books, history, and sources.','Its countries, books, and history.']
    sfx=['',' A map and sourced facts.',' With a map and sourced facts.',' At Bibliotheca Catholica.',' From Bibliotheca Catholica.',' Part of Bibliotheca Catholica, a free Catholic library.',' With a shaded map, at Bibliotheca Catholica.']
    return fit([c+' '+t+s for c in cores for s in sfx for t in tails])
def layer_name(D,lid):
    if lid.startswith('fam-'):
        f=D['families'][lid[4:]];n=len(D['layers'][lid]['members']);return 'the '+f['long']+' ('+str(n)+' Churches)'
    n=next(r['name'] for r in D['records'] if r['id']==lid);return n if n.startswith(('The ','Divine Worship')) else 'the '+n
def names(D,codes):return sorted((D['names'][c] for c in codes),key=lambda s:s.casefold())
def swatch(fam,view):
    return '<svg class="rm-sw" width="34" height="18" viewBox="0 0 34 18" aria-hidden="true" focusable="false"><rect width="34" height="18" rx="2" fill="url(#rm'+('p' if view=='present' else 'h')+'-'+fam+')" class="rm-swbox"/></svg>'
def info(D,lid,view):
    """Caption, legend, and visible country list for one layer and view (precomputed for the app)."""
    L=D['layers'][lid];codes=L[view];nm=layer_name(D,lid);fam=L['family']
    if view=='present':
        if codes:
            cap='Countries where '+nm+(' have' if lid.startswith('fam-') else ' has')+' its own jurisdiction: '+str(len(codes))+(' country.' if len(codes)==1 else ' countries.')
            if lid.startswith('fam-'):cap=cap.replace(' its own',' their own')
            leg=LEGEND_P
            src=('Source: '+ext(L['psrc'])+', as listed on '+E(L['asof'])+'.') if L.get('psrc') else 'Sources: each Church\'s list on GCatholic, linked from its page below.'
        else:cap=L.get('pmsg') or 'Present country list not verified.';leg='';src=''
    else:
        if codes:
            cap='Approximate historical heartland of '+nm+': '+(L['hdesc'] or '')+'.';leg=LEGEND_H
            src=('Source: '+ext(L['hsrc'])+' (medium confidence; approximate).') if L.get('hsrc') else 'Sources: each Church\'s page (medium confidence; approximate).'
        else:cap='No historical heartland layer for this '+('rite.' if lid.startswith('latin-') else 'Church.');leg='';src=''
    h='<p class="rmap-cap">'+E(cap)+'</p>'
    if leg:h+='<p class="rmap-legend">'+swatch(fam,view)+' <span>'+E(leg)+'</span></p>'
    if codes:h+='<details class="rmap-list" open><summary>Countries shaded ('+str(len(codes))+')</summary><ul class="rmap-countries">'+''.join('<li>'+E(n)+'</li>' for n in names(D,codes))+'</ul></details>'
    if lid.startswith('fam-'):
        h+='<p class="small">Churches: '+', '.join('<a href="/rites/'+m+'/">'+E(D['titles'][m])+'</a>' for m in L['members'])+'.</p>'
    if src:h+='<p class="small">'+src+'</p>'
    return h
def status_text(D,lid,view):
    L=D['layers'][lid];n=len(L[view]);v='present jurisdictions' if view=='present' else 'approximate historical heartland'
    return 'Showing '+layer_name(D,lid)+', '+v+': '+(str(n)+(' country' if n==1 else ' countries') if n else 'no countries shaded')+'.'
def options(D,sel):
    out='';R={r['id']:r for r in D['records']}
    for f in D['order_fam']:
        F=D['families'][f];grp=''
        if f=='lat':
            grp+='<option value="latin"'+(' selected' if sel=='latin' else '')+'>Latin Church (worldwide, not shaded)</option>'
            for rid in ('latin-ambrosian','latin-hispanic-mozarabic','latin-divine-worship'):grp+='<option value="'+rid+'"'+(' selected' if sel==rid else '')+'>'+E(R[rid]['name'])+'</option>'
        else:
            if 'fam-'+f in D['layers']:grp+='<option value="fam-'+f+'"'+(' selected' if sel=='fam-'+f else '')+'>All '+E(F['label'])+' Churches ('+str(len(D['layers']['fam-'+f]['members']))+')</option>'
            for r in D['records']:
                if r['kind']=='church' and r['family']==f:grp+='<option value="'+r['id']+'"'+(' selected' if sel==r['id'] else '')+'>'+E(r['name'])+'</option>'
        out+='<optgroup label="'+E(F['long'])+'">'+grp+'</optgroup>'
    return out
def map_tpl(D,select):
    """The map block with tokens %LAYER% %VIEW% %FAM% %SVG% %INSETS% %INFO% %STATUS% %OPTIONS%, filled by
    tools/build_static.py (static pages) and scripts/rites.js (the app) in the same way."""
    ctl='<div class="rmap-controls" hidden>'
    if select:ctl+='<label class="rmap-sel"><span>Church or tradition</span><select id="rmap-sel" aria-controls="rmap-fig">%OPTIONS%</select></label>'
    ctl+=('<fieldset class="rmap-view"><legend>Show</legend><label><input type="radio" name="rmap-view" value="present"> Present: own jurisdiction</label>'
          '<label><input type="radio" name="rmap-view" value="heartland"> Approximate historical heartland</label></fieldset></div>')
    return ('<section class="rmap" id="rmap" aria-labelledby="rmap-h" data-layer="%LAYER%" data-view="%VIEW%" data-fam="%FAM%"><h2 id="rmap-h">'+('Map' if select else 'Where it has its own jurisdiction')+'</h2>'+ctl+
            '<p class="rmap-status small" role="status" aria-live="polite">%STATUS%</p>'
            '<figure class="rmap-fig" id="rmap-fig"><div class="rmap-svg">%SVG%</div>%INSETS%<figcaption id="rmap-cap" class="rmap-info">%INFO%</figcaption></figure>'
            '<p class="rmap-disclaimer small">'+E(DISCLAIMER)+' Made with <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth ↗</a> (public domain). <a href="/rites/sources/">Sources and method</a>.</p>'
            '<noscript><p class="small">Without JavaScript the map shows the default view. Each Church\'s page has its own map, and the lists above and below give every country in text.</p></noscript></section>')
def slot(lid,select=False):return '<div class="rmap-slot" data-layer="'+E(lid)+'" data-select="'+('1' if select else '')+'"></div>'
CANON=('<section class="panel rites-terms"><h2>Church sui iuris and rite</h2>'
 '<p>A <b>Church sui iuris</b> is "a community of the faithful" joined together by a hierarchy according to law, which the supreme authority recognizes, expressly or tacitly, as sui iuris (CCEO can. 27). A <b>rite</b> is the "liturgical, theological, spiritual and disciplinary patrimony", distinguished by the culture and history of peoples, by which each Church sui iuris expresses its own way of living the faith (CCEO can. 28 §1).'+srcs(['https://www.vatican.va/content/john-paul-ii/la/apost_constitutions/documents/hf_jp-ii_apc_19901018_codex-can-eccl-orient-1.html'])+'</p>'
 '<p>So a Church is a community with its own hierarchy, and a rite is a patrimony. Several Churches share one tradition (fourteen are Byzantine), and one Church, the Latin Church, has several rites and uses. This section therefore has two kinds of entry: 24 Churches sui iuris, and 7 rites and uses within the Latin Church.</p>'
 '<h3>Two classifications, shown side by side</h3><ul>'
 '<li><b>CCEO can. 28 §2</b> groups the Eastern Churches by tradition of origin: Alexandrian, Antiochene, Armenian, Chaldean, and Constantinopolitan. It does not cover the Latin Church, which is governed by the 1983 Code of Canon Law.</li>'
 '<li><b>The Catechism (CCC 1203)</b> lists the rites in use: "the Latin (principally the Roman rite, but also the rites of certain local churches, such as the Ambrosian rite, or those of certain religious orders) and the Byzantine, Alexandrian or Coptic, Syriac, Armenian, Maronite and Chaldean rites".'+srcs(['https://www.vatican.va/archive/ENG0015/__P3C.HTM'])+'</li></ul>'
 '<p>The Catechism says "Byzantine" where the Code says Constantinopolitan, says "Syriac" for the West Syriac rites, and names the Maronite rite separately, while the Code places it within the Antiochene tradition. The table gives both for every Church; neither is forced onto the other.</p></section>')
VARIANTS=('<section class="panel"><h2>Where lists differ</h2><ul>'
 '<li><b>Albanian Greek Catholic Church.</b> Included in lists derived from the Annuario Pontificio, as here; GCatholic omits it. Its present country list is not verified.</li>'
 '<li><b>Kazakhstan and Central Asia.</b> GCatholic lists a "Byzantine Church in Kazakhstan and Central Asia", which is not one of the 24 here. It is mentioned only; it has no entry or shading.</li>'
 '<li><b>Ruthenian Greek Catholic Church.</b> CNEWA describes three jurisdictions whose relationship "has not been clarified"; see <a href="/rites/ruthenian/">its page</a>.</li></ul>'+srcs(['https://gcatholic.org/dioceses/rites.htm','https://cnewa.org/eastern-christian-churches/the-catholic-eastern-churches/'])+'</section>')
def landing(D):
    R=D['records'];ch=[r for r in R if r['kind']=='church'];lat=[r for r in R if r['kind']!='church']
    lede='The 24 Churches sui iuris of the Catholic Church and the rites and uses of the Latin Church, with a shaded map of where each Church has its own jurisdiction.';lede=fit([lede])
    rows=''
    for r in ch:
        L=D['layers'].get(r['id']) or {};n=len(L.get('present') or [])
        hd=r.get('head');hcell=((UNV+' ' if hd.get('unv') else '')+E(hd['v'])+(' <span class="small">('+E(hd.get('by',''))+(', '+E(hd['asof']) if hd.get('asof') else '')+')</span>' if hd.get('by') else '')) if hd else NYV
        if r['id']=='latin':cc='Worldwide (not shaded)'
        elif n:cc=str(n)+(' country' if n==1 else ' countries')+' <button type="button" class="rites-show" data-layer="'+r['id']+'" hidden>Show on map</button>'
        else:cc='Not verified'+(' <button type="button" class="rites-show" data-layer="'+r['id']+'" hidden>Show heartland</button>' if L.get('heartland') else '')
        rows+=('<tr><th scope="row"><a href="/rites/'+r['id']+'/">'+E(r['name'])+'</a></th><td data-label="Tradition (CCEO)">'+E(D['families'][r['family']]['label'] if r['family']!='lat' else 'Not covered by CCEO')+'</td>'
               '<td data-label="Catechism (CCC 1203)">'+E(r['ccc']['v'])+'</td><td data-label="Status">'+(((UNV+' ') if r['status'].get('unv') else '')+E(r['status']['v']) if r.get('status') else NYV)+'</td>'
               '<td data-label="Head">'+hcell+'</td><td data-label="Own jurisdiction in">'+cc+'</td></tr>')
    table=('<div class="table-wrap" role="region" aria-labelledby="rites-t1" tabindex="0"><table class="rites-table"><caption id="rites-t1">The 24 Churches sui iuris</caption><thead><tr><th scope="col">Church</th><th scope="col">Tradition (CCEO can. 28 §2)</th><th scope="col">Catechism (CCC 1203)</th><th scope="col">Canonical status</th><th scope="col">Head</th><th scope="col">Own jurisdiction in</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
           '<p class="small">Heads are as listed on the date shown and are re-checked every six months. Every entry\'s sources are on its page.</p>')
    lrows=''
    for r in lat:
        L=D['layers'].get(r['id']) or {};n=len(L.get('present') or [])
        where=(E(r['geography']['v']) if r.get('geography') else '')+((' ' if r.get('geography') else '')+'Own jurisdiction in '+', '.join(E(x) for x in names(D,L['present']))+'. <button type="button" class="rites-show" data-layer="'+r['id']+'" hidden>Show on map</button>' if n else '')
        lrows+=('<tr><th scope="row"><a href="/rites/'+r['id']+'/">'+E(r['name'])+'</a></th><td data-label="Where">'+(where or '<span class="small">Not mapped</span>')+'</td><td data-label="Current books">'+(((UNV+' ') if r['books'].get('unv') else '')+E(r['books']['v']) if r.get('books') else '<span class="small">Not listed</span>')+'</td></tr>')
    ltable=('<div class="table-wrap" role="region" aria-labelledby="rites-t2" tabindex="0"><table class="rites-table"><caption id="rites-t2">Rites and uses within the Latin Church</caption><thead><tr><th scope="col">Rite or use</th><th scope="col">Where</th><th scope="col">Current books</th></tr></thead><tbody>'+lrows+'</tbody></table></div>')
    body=(crumbs(('Rites & Liturgy','/rites/'))+head('Rites & Liturgy','Rites & Liturgy',lede)+
          '<p class="section-intro">The Catholic Church is a communion of Churches. Alongside the Latin Church are 23 Eastern Catholic Churches, each with its own hierarchy and liturgical tradition. This guide lists them in a table, with a map of the countries where each has its own jurisdiction, and links to public-domain liturgical texts.</p>'
          '<div class="rites-layout"><div class="rites-main">'+table+ltable+'</div><aside class="rites-aside" aria-label="Map">'+slot('fam-ant',True)+'</aside></div>'+CANON+VARIANTS+
          '<p class="rites-more"><a href="/rites/sources/">Sources and method</a> · <a href="/rights/">Rights badges</a> · <a href="/saints/">Saints &amp; Hagiography</a></p>')
    return {'title':'Rites & Liturgy','h1':'Rites & Liturgy','desc':lede,'html':'<div class="rites-page">'+body+'</div>'}
def record_page(D,r):
    F=D['families'][r['family']];d=rec_desc(r,F);L=D['layers'].get(r['id'])
    eb=('Church sui iuris · '+(F['label']+' tradition' if r['family']!='lat' else 'Latin Church')) if r['kind']=='church' else 'Rite or use · Latin Church'
    dl=''
    def row(k,v):return '<div><dt>'+E(k)+'</dt><dd>'+v+'</dd></div>'
    if r['kind']=='church':
        dl+=row('Tradition (CCEO can. 28 §2)',fact(r['cceo']))+row('Catechism (CCC 1203)',fact(r['ccc']))+row('Canonical status',fact(r.get('status')))
        hd=r.get('head');dl+=row('Head',fact(hd,(' (as listed by '+E(hd['by'])+(' on '+E(hd['asof']) if hd.get('asof') else '')+')') if hd and hd.get('by') else ''))
    else:
        dl+=row('Church','<a href="/rites/latin/">Latin Church</a>')
    if r.get('centre'):dl+=row('Historical centre' if r['kind']=='church' else 'Centre',fact(r['centre'],(' <span class="small">('+E(r['centre']['role'])+')</span>' if r['centre'].get('role') else '')))
    elif r['kind']=='church':dl+=row('Historical centre',NYV)
    if r['kind']=='church' and r['id']!='latin':dl+=row('Present see',fact(r.get('see'),(' <span class="small">('+E(r['see']['role'])+')</span>' if r.get('see') and r['see'].get('role') else '')))
    if r.get('geography'):dl+=row('Where it is used',fact(r['geography']))
    if r.get('books'):dl+=row('Liturgical books',fact(r['books'],(' <span class="small">'+E(r['books']['note'])+'</span>' if r['books'].get('note') else '')))
    if L:
        pc=L['present']
        dl+=row('Own jurisdiction in',(E(', '.join(names(D,pc)))+' ('+str(len(pc))+')'+srcs([L['psrc']])+(' <span class="small">As listed on '+E(L['asof'])+'.</span>' if L.get('asof') else '')) if pc else E(L.get('pmsg') or 'Not verified'))
        if L['heartland']:dl+=row('Approximate historical heartland',E(L['hdesc'])+' ('+E(', '.join(names(D,L['heartland'])))+')'+srcs([L['hsrc']]))
    elif r['id']=='latin':dl+=row('Own jurisdiction in','Worldwide. The Latin Church is not shaded on the map.')
    if r.get('note'):dl+=row('Note',fact(r['note']))
    h=crumbs(('Rites & Liturgy','/rites/'),(r['name'],'/rites/'+r['id']+'/'))+'<article class="rites-record">'+head(eb,r['name'],d)+'<dl class="rites-facts panel">'+dl+'</dl>'
    if r.get('status_magisterial'):
        h+='<section class="panel"><h2>Legislation in force</h2><p>The wording follows Traditionis custodes (2021): the liturgical books promulgated by Saint Paul VI and Saint John Paul II are "the unique expression of the lex orandi of the Roman Rite" (art. 1); the diocesan bishop authorizes "the use of the 1962 Roman Missal" (art. 2), "the Missal antecedent to the reform of 1970" (art. 3).</p><ul>'+''.join('<li>'+E(s['v'])+srcs(s['s'])+'</li>' for s in r['status_magisterial'])+'</ul></section>'
    if r.get('sub'):
        R={x['id']:x for x in D['records']}
        h+='<section class="panel"><h2>Rites and uses within the Latin Church</h2><ul>'+''.join('<li><a href="/rites/'+s+'/">'+E(R[s]['name'])+'</a></li>' for s in r['sub'])+'</ul></section>'
    if L and (L['present'] or L['heartland']):h+=slot(r['id'])
    if r['milestones']:
        h+='<section class="panel"><h2>History</h2><ol class="rites-ms">'+''.join('<li><span class="rites-when">'+E(m['when'])+'</span> '+E(m['event'])+srcs(m['s'])+'</li>' for m in r['milestones'])+'</ol><p class="small">Dates are given as ranges or centuries where the sources give no single date.</p></section>'
    if r['resources']:
        h+='<section class="panel"><h2>Texts and resources</h2><p class="small">Every resource is an outside link; nothing here is hosted by Bibliotheca Catholica. <a href="/rights/">What the badges mean</a>.</p><ul class="rites-res">'+''.join('<li>'+ext(x['url'],x['title'])+' '+badge(x)+'<br><span class="small">'+E(x['evidence'])+'</span></li>' for x in r['resources'])+'</ul></section>'
    if r['related']:
        pre={'author':'/author/','work':'/work/','saint':'/saints/'}
        h+='<section class="panel"><h2>In the library</h2><ul>'+''.join('<li><a href="'+pre[x['kind']]+x['id']+'/">'+E(x['label'])+'</a> <span class="small">'+E(x['why'])+'</span></li>' for x in r['related'])+'</ul></section>'
    if r['sources']:h+='<p class="small rites-srcs">Main sources: '+', '.join(ext(u) for u in r['sources'])+'. Checked '+E(D['checked'])+'. <a href="/rites/sources/">Sources and method</a>.</p>'
    h+='</article>'
    return {'title':r['name'],'h1':r['name'],'desc':d,'html':'<div class="rites-page">'+h+'</div>'}
def sources_page(D):
    lede='Where the Rites & Liturgy facts come from, how uncertain facts are marked, what is not yet verified, and the public-domain Natural Earth map boundaries.'
    nyv=[]
    for r in D['records']:
        for k,lab in (('status','canonical status'),('head','head')):
            if r['kind']=='church' and r['id']!='latin' and not r.get(k):nyv.append((r['name'],lab))
    g=D['geo_meta']
    h=(crumbs(('Rites & Liturgy','/rites/'),('Sources and method','/rites/sources/'))+head('Rites & Liturgy','Rites & Liturgy: sources and method',fit([lede]))+
       '<section class="panel prose"><h2>Sources</h2><ul>'
       '<li><b>Canon law and the Catechism</b>: the Code of Canons of the Eastern Churches (CCEO) and the Catechism, at vatican.va.</li>'
       '<li><b>Country lists and heads</b>: '+ext('https://gcatholic.org/dioceses/rites.htm','GCatholic')+', cited and linked, never copied. Heads are given as listed on the date shown and are re-checked every six months.</li>'
       '<li><b>History</b>: '+ext('https://cnewa.org/eastern-christian-churches/the-catholic-eastern-churches/','CNEWA')+' (Ronald Roberson\'s profiles) and the Catholic Encyclopedia (1907 to 1912) at New Advent.</li>'
       '<li><b>Historical centres and sees</b>: Wikidata (CC0). They are places, not territories, and are not drawn on the map.</li>'
       '<li><b>Texts</b>: public-domain scans at the Internet Archive, and official Church sites, linked only.</li></ul>'
       '<h2>How uncertain facts are shown</h2><ul><li>Every fact links its source.</li><li>A fact our sources give only at low confidence is never shown as plain fact. It is either marked '+UNV+' with its source, or left out and shown as '+NYV+'.</li>'
       '<li>Dates are ranges or centuries unless a document with a date is cited.</li><li>No population figures are shown.</li></ul>'
       '<h2>Not yet verified</h2><ul>'+''.join('<li>'+E(n)+': '+E(l)+'</li>' for n,l in nyv)+'<li>Albanian Greek Catholic Church: its present see and present country list</li><li>Russian Greek Catholic Church: its historical centre and present see</li><li>Belarusian Greek Catholic Church: its present see (there is no eparchy)</li>'
       '<li>Current editions of the liturgical books of the Alexandrian, Syriac, Armenian, and Chaldean Churches</li><li>The date of the undated Roman Missal for the laity (badge: Unknown)</li><li>The religious orders\' rites, order by order</li></ul>'
       '<h2>The map</h2><p>The map is drawn at build time as plain SVG from '+ext('https://www.naturalearthdata.com/','Natural Earth')+' Admin 0 country boundaries (1:110m for the world, 1:50m for the insets and for Guam) and, for the Kerala outline only, Admin 1 boundaries (1:50m). Countries are joined on Natural Earth\'s ISO_A2_EH code. '
       '<b>Natural Earth is in the public domain</b>: "All versions of Natural Earth raster + vector map data found on this website are in the public domain" ('+ext(g['terms'],'terms of use')+'). Made with Natural Earth.</p>'
       '<p>'+E(DISCLAIMER)+' Shading is by whole country, so a Church present in one region of a large country shades all of it. There are no pins, no diocesan boundaries, and no layer of a "main" rite per country.</p>'
       '<p>Colours are the Okabe and Ito colour-blind-safe set '+ext('https://jfly.uni-koeln.de/color/','(jfly.uni-koeln.de)')+', darkened or lightened to reach 3:1 against the map in each theme, and always paired with a hatch pattern and a text list.</p>'
       '<h2>Data</h2><p>The compiled records, with every source link, are in <a href="/data/rites.json">data/rites.json</a>. Our own wording and structure are CC0; the facts belong to no one, and GCatholic and CNEWA are cited and linked, not copied. See <a href="/licensing/">Licensing &amp; credits</a>.</p></section>')
    return {'title':'Rites & Liturgy: sources and method','h1':'Rites & Liturgy: sources and method','desc':fit([lede]),'html':'<div class="rites-page">'+h+'</div>'}
def build(D):
    D=dict(D);D['order_fam']=['lat','alex','ant','arm','chal','byz'];D['titles']={r['id']:r['name'] for r in D['records']}
    pages={'':landing(D),'sources':sources_page(D)}
    for r in D['records']:pages[r['id']]=record_page(D,r)
    info_map={lid+'|'+v:info(D,lid,v) for lid in D['layers'] for v in('present','heartland')}
    status={lid+'|'+v:status_text(D,lid,v) for lid in D['layers'] for v in('present','heartland')}
    names_={lid:layer_name(D,lid) for lid in D['layers']}
    return {'pages':pages,'info':info_map,'status':status,'tpl':{'full':map_tpl(D,True),'record':map_tpl(D,False)},'options':options(D,'%SEL%'),'layerNames':names_}
SLOT_RE=re.compile(r'<div class="rmap-slot" data-layer="([^"]+)" data-select="(1?)"></div>')
def shade(svg,codes):
    cs=set(codes);return re.sub(r'<path data-c="([A-Z]{2})"',lambda m:'<path data-c="'+m.group(1)+'"'+(' class="on"' if m.group(1) in cs else ''),svg)
def fill_slot(J,lid,select,view='present'):
    """Same steps as BCRites.core.block in scripts/rites.js; the app then shades by toggling classes."""
    L=J['layers'][lid];t=J['tpl']['full' if select else 'record']
    rep={'%LAYER%':lid,'%VIEW%':view,'%FAM%':L['family'],'%SVG%':J['svg'],'%INSETS%':J['insets'],'%INFO%':J['info'][lid+'|'+view],'%STATUS%':E(J['status'][lid+'|'+view]),'%OPTIONS%':J['options']}
    for k,v in rep.items():t=t.replace(k,v)
    return t
def static_slot(J,lid,select,view='present'):
    """No-JS version: shaded at build time, the default option and view preselected."""
    t=fill_slot(J,lid,select,view)
    t=shade(t,J['layers'][lid][view])
    t=t.replace('<option value="'+lid+'">','<option value="'+lid+'" selected>',1).replace('value="'+view+'">','value="'+view+'" checked>',1)
    if not J['layers'][lid]['heartland']:t=t.replace('value="heartland">','value="heartland" disabled>',1)
    return t
def expand(html,J):return SLOT_RE.sub(lambda m:static_slot(J,m.group(1),m.group(2)=='1'),html)
