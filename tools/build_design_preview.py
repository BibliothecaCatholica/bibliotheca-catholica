#!/usr/bin/env python3
"""Write the design-refresh preview pages at /design-preview/ (Part 1 of the November 2026 design refresh).

Five areas, four variations each, at /design-preview/<area>/v1/ to v4/, plus an index at /design-preview/.
Every page uses real site content read from the data files and the generated pages (no placeholder text),
carries the one GA4 tag and noindex,nofollow, and stays out of the sitemap, the nav, search, and feeds
(robots.txt disallows /design-preview/). The pages are self-contained: their CSS is inline here and uses the
DESIGN.md tokens, and the site's own styles are not touched. Called at the end of tools/build_static.py.
The directory is wiped and rebuilt on every run. Delete this script, its call, its test, and the
/design-preview/ directory together once every area has been built (docs/research/design-directions-2026-11.md).
"""
import html,json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
OUT=ROOT/'design-preview'
DOC='https://github.com/BibliothecaCatholica/bibliotheca-catholica/blob/main/docs/research/design-directions-2026-11.md'
E=lambda s:html.escape(str(s),quote=True)
ROMAN=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']

# ---------------------------------------------------------------- data (all real, read from the repository)
def ga_tag():
    import build_drafts
    return build_drafts.ga_tag()

def load():
    from site_copy import HOME_PEOPLE,HOME_SHELF,HOME_LINKS,SECTION_LINKS,home_hero
    from notices import PG_LINE
    from rights_pages import licensing_html
    lib=json.loads((ROOT/'data/library.json').read_text(encoding='utf-8'))
    hub=json.loads((ROOT/'data/catholic-hub.json').read_text(encoding='utf-8'))
    portraits=set(json.loads((ROOT/'data/portraits.json').read_text(encoding='utf-8'))['portraits'])
    covers=json.loads((ROOT/'data/covers.json').read_text(encoding='utf-8'))['covers']
    flags=json.loads((ROOT/'data/editorial-flags.json').read_text(encoding='utf-8'))
    tpl=(ROOT/'index.html').read_text(encoding='utf-8')
    d={'PG_LINE':PG_LINE,'SECTION_LINKS':SECTION_LINKS,'HOME_LINKS':HOME_LINKS,'flags':flags}
    authors={a['id']:a for a in hub['authors']}
    d['eras']=hub['eras']
    def dates(a):
        # the same form as years() in tools/build_static.py
        f=lambda y:(str(-y)+' BC' if y<0 else str(y)) if isinstance(y,int) else ''
        b,x=a.get('born'),a.get('died')
        return f(b)+'–'+f(x) if (b or x) else ''
    def cover(w):
        for e in w['editions']:
            if e.get('text') and e['id'] in covers:return '/assets/covers/'+e['id']+'.webp'
        return ''
    works=[]
    for w in lib['works']:
        hosted=any(e.get('text') for e in w['editions'])
        works.append({'id':w['id'],'title':w['title'],'author':w['author'],'authorId':w.get('authorId') or '','category':w['category'],
                      'desc':w.get('description') or '','date':w.get('date') or '','hosted':hosted,'cover':cover(w),'added':w.get('added') or ''})
    d['works']=works
    byid={w['id']:w for w in works}
    d['hosted']=sum(1 for w in lib['works'] for e in w['editions'] if e.get('text'))
    d['authors_n']=len(hub['authors'])
    m=re.search(r'window\.BOOKS_COUNT=(\d+)',tpl);d['books_n']=int(m.group(1)) if m else 0
    d['people']=[]
    for i in HOME_PEOPLE:
        a=authors[i];first=next((w for w in works if w['authorId']==i and w['hosted'] and w['id'] in HOME_SHELF),None) or next((w for w in works if w['authorId']==i and w['hosted']),None)
        d['people'].append({'id':i,'name':a['name'],'dates':dates(a),'work':first})
    d['shelf']=[byid[i] for i in HOME_SHELF]
    d['recent']=sorted([w for w in works if w['added'] and w['hosted']],key=lambda w:(w['added'],w['title']),reverse=True)[:6]
    d['authors']=[{'id':a['id'],'name':a['name'],'dates':dates(a),'era':a.get('era') or '','desc':a.get('desc') or '','portrait':a['id'] in portraits,
                   'hosted':sum(1 for w in works if w['authorId']==a['id'] and w['hosted'])} for a in hub['authors']]
    h=home_hero()
    d['hero_img']=re.search(r'<img [^>]+>',h).group(0)
    d['hero_cap']=re.search(r'<figcaption>(.*?)</figcaption>',h,re.S).group(1)
    # the generated home page holds the exact home copy (site_copy.py), so the preview reads it from there
    d['home_about']=re.search(r'<section class="home-about".*?<p>(.*?)</p>',tpl,re.S).group(1)
    d['mark']=re.search(r'<svg class="brand-mark".*?</svg>',tpl,re.S).group(0)
    d['nl_line']=re.search(r'<p class="nl-line">(.*?)</p>',tpl).group(1)
    d['footer_credit']=re.search(r'<p class="small footer-credit-line">(.*?)</p>',tpl,re.S).group(1)
    d['non_affiliation']=re.search(r'<p class="small non-affiliation">(.*?)</p>',tpl,re.S).group(1)
    d['social']=re.search(r'<p class="small social-links">(.*?)</p>',tpl,re.S).group(1)
    U=lambda pairs:[(h,html.unescape(t)) for h,t in pairs]
    d['footer_read']=U(re.findall(r'<a href="([^"]+)">([^<]+)</a>',re.search(r'aria-label="Read and explore"><h2>[^<]*</h2>(.*?)</nav>',tpl,re.S).group(1)))
    d['footer_project']=U(re.findall(r'<a (?:class="[^"]*" )?(?:data-support="footer" )?href="([^"]+)"[^>]*>([^<]+)</a>',re.search(r'aria-label="The project and policies"><h2>[^<]*</h2>(.*?)</nav>',tpl,re.S).group(1)))
    d['nav']=U(re.findall(r'<a href="([^"]+)" data-nav="[^"]+"(?: class="nav-m")?[^>]*>([^<]+)</a>',re.search(r'<nav class="mainnav".*?</nav>',tpl,re.S).group(0)))
    # reading: Orthodoxy (pg-130), the designed-edition pilot
    ow=next(w for w in lib['works'] if w['id']=='orthodoxy');oe=ow['editions'][0]
    wp=(ROOT/'work/orthodoxy/index.html').read_text(encoding='utf-8')
    d['ortho']={'work':ow,'ed':oe,'facts':re.search(r'<p class="work-facts">(.*?)</p>',wp).group(1),
                'about':re.search(r'<h2>About this edition</h2><p>(.*?)</p>',wp,re.S).group(1),
                'epub':re.search(r'href="(/downloads/epub/[^"]+\.epub)"',wp).group(1),
                'chapters':[(u,html.unescape(t)) for u,t in re.findall(r'<li><a href="(/work/orthodoxy/ch/[^"]+/)">([^<]+)</a></li>',re.search(r'<ol class="text-parts">(.*?)</ol>',wp,re.S).group(1))]}
    def paras(slug):
        s=(ROOT/'work/orthodoxy/ch'/slug/'index.html').read_text(encoding='utf-8')
        a=re.search(r'<article class="reading-text[^"]*"[^>]*>(.*?)</article>',s,re.S).group(1)
        return re.findall(r'<p class="reading-prose">(.*?)</p>',a,re.S)
    ch=[u.rstrip('/').split('/')[-1] for u,_ in d['ortho']['chapters']]
    d['ortho']['ch2']=paras(ch[1])[:6];d['ortho']['ch2_total']=len(paras(ch[1]))
    d['ortho']['ch3_first']=re.split(r'(?<=[.;?!])\s',re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',paras(ch[2])[0])),maxsplit=1)[0]
    d['ortho']['ch9_end']=paras(ch[8])[-2:]
    d['ortho']['author']=authors.get('g-k-chesterton',{}).get('name','G. K. Chesterton')
    # sources and credits: the licensing page exactly as /licensing/ renders it
    lic=licensing_html((ROOT/'LICENSING.md').read_text(encoding='utf-8'))
    d['lic_h1']=re.search(r'<h1>(.*?)</h1>',lic).group(1)
    d['lic_lede']=re.search(r'<p class="lede">(.*?)</p>',lic,re.S).group(1)
    d['lic_table']=re.search(r'<div class="table-wrap">.*?</div>',lic,re.S).group(0)
    d['lic_rows']=[[re.sub(r'^<td[^>]*>|</td>$','',c) for c in re.findall(r'<td[^>]*>.*?</td>',r,re.S)] for r in re.findall(r'<tr>(<td.*?)</tr>',lic,re.S)]
    body=re.search(r'</div>(<h2>.*)</section></div>$',lic,re.S).group(1)
    parts=re.split(r'(<h2>.*?</h2>)',body)
    secs=[];tail=''
    for i in range(1,len(parts),2):
        content=parts[i+1]
        m=re.search(r'<p class="small">This page shows.*$',content,re.S)
        if m:tail=m.group(0);content=content[:m.start()]
        secs.append((re.sub(r'</?h2>','',parts[i]),content))
    d['lic_secs']=secs;d['lic_tail']=tail
    from collections import Counter
    from urllib.parse import urlparse
    d['src_counts']=Counter(urlparse(e.get('source','')).netloc for w in lib['works'] for e in w['editions'] if e.get('text')).most_common()
    d['portraits_n']=len(portraits)
    return d

# ---------------------------------------------------------------- shared CSS (DESIGN.md tokens, copied from styles.css :root)
BASE_CSS='''
:root{--bg:#f6f0e2;--bg2:#efe6d2;--card:#fffaf0;--ink:#2a2118;--ink2:#5a4b3a;--muted:#6f604b;--rubric:#8b1e2d;--rubric2:#a8323f;--on-rubric:#fff8ea;--gold:#b8892d;--gold-ink:#80601a;--line:#e0d3b8;--rule:#cdbb97;--focus:#8b1e2d;
--serif:"EB Garamond","Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;--display:"Cormorant Garamond","EB Garamond",Georgia,serif;--sans:Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
--t-xs:14px;--t-sm:16px;--t-md:18px;--t-lg:21px;--t-xl:26px;--t-2xl:34px;--t-3xl:48px;--s-1:4px;--s-2:8px;--s-3:12px;--s-4:16px;--s-5:24px;--s-6:32px;--s-7:48px;--s-8:64px;color-scheme:light}
[data-theme=dark]{--bg:#14161c;--bg2:#1b1e26;--card:#1f232c;--ink:#ece4d4;--ink2:#c9bfae;--muted:#a49b8c;--rubric:#e37f89;--rubric2:#f08a94;--on-rubric:#14161c;--gold:#d9b45a;--gold-ink:#d9b45a;--line:#2f3440;--rule:#4a4f5c;--focus:#e9c46a;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:var(--t-md)/1.55 var(--serif);font-variant-numeric:oldstyle-nums;-webkit-text-size-adjust:100%}
a{color:var(--rubric);text-decoration-thickness:.06em;text-underline-offset:.18em}a:hover{color:var(--rubric2)}
:focus-visible{outline:2px solid var(--focus);outline-offset:3px;border-radius:2px}
img{max-width:100%;height:auto}
.skip{position:absolute;left:-999px}.skip:focus{left:var(--s-2);top:var(--s-2);z-index:99;background:var(--card);padding:var(--s-2) var(--s-3)}
.wrap{max-width:1160px;margin:0 auto;padding:0 var(--s-4)}
.label{font:500 var(--t-sm)/1.3 var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink);margin:0}
.muted{color:var(--muted)}.small{font-size:var(--t-xs)}
h1,h2,h3{font-family:var(--display);font-weight:600;line-height:1.15;margin:0}
.btn{display:inline-flex;align-items:center;min-height:44px;font:600 15px var(--sans);padding:0 var(--s-5);border-radius:6px;border:1px solid var(--rubric);background:var(--rubric);color:var(--on-rubric);text-decoration:none}
.btn:hover{background:var(--rubric2);border-color:var(--rubric2);color:var(--on-rubric)}.btn.ghost{background:transparent;color:var(--rubric)}
.rows{list-style:none;margin:0;padding:0}.rows>li{border-top:1px solid var(--line);padding:var(--s-3) 0}.rows>li:last-child{border-bottom:1px solid var(--line)}
.pv-bar{font:13px/1.4 var(--sans);background:var(--ink);color:var(--bg);}
.pv-bar .wrap{display:flex;flex-wrap:wrap;gap:var(--s-2) var(--s-4);align-items:center;padding-top:var(--s-2);padding-bottom:var(--s-2)}
.pv-bar a{color:var(--bg);display:inline-block;min-height:24px;padding:2px 4px}.pv-bar a[aria-current=page]{font-weight:700;text-decoration:none;border-bottom:2px solid var(--bg)}
.pv-bar b{font-weight:600}.pv-bar .pv-v{display:flex;gap:var(--s-1)}.pv-bar button{font:inherit;color:var(--bg);background:transparent;border:1px solid currentColor;border-radius:6px;min-height:28px;padding:0 var(--s-2);cursor:pointer;margin-left:auto}
.pv-bar :focus-visible{outline-color:var(--bg)}
.pv-note{font:var(--t-xs)/1.5 var(--sans);color:var(--muted);border-bottom:1px solid var(--line);padding:var(--s-2) 0}
/* the plain site header and footer used in areas a to d (area e shows the variations) */
.ph{border-bottom:1px solid var(--line)}.ph .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s-2) var(--s-5);padding-top:var(--s-3);padding-bottom:var(--s-3)}
.ph .brand{font:600 var(--t-lg)/1.1 var(--display);color:var(--ink);text-decoration:none}.ph nav{display:flex;flex-wrap:wrap;gap:0 var(--s-4);font:500 var(--t-xs)/1 var(--sans)}
.ph nav a{color:var(--ink2);text-decoration:none;display:inline-flex;align-items:center;min-height:32px}.ph nav a:hover{color:var(--rubric)}
.pf{margin-top:var(--s-8);border-top:1px solid var(--line);background:var(--bg2);font:var(--t-xs)/1.6 var(--sans);color:var(--ink2)}.pf .wrap{padding-top:var(--s-5);padding-bottom:var(--s-5)}
.pf a{color:var(--ink2);margin-right:var(--s-3);display:inline-block;min-height:24px}.pf summary{cursor:pointer;min-height:24px}.pf details a{margin-right:0;min-height:0}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
'''

THEME_INIT=("<script>(function(){var t;try{t=localStorage.getItem('hub-theme')}catch(e){}"
            "if(t!=='dark'&&t!=='light')t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';"
            "document.documentElement.dataset.theme=t})();</script>\n")
# the toggle only changes this page view; it reads the site's theme choice but never writes reader storage
THEME_TOGGLE=("<script>(function(){var b=document.getElementById('pv-theme');if(!b)return;function s(){var d=document.documentElement.dataset.theme==='dark';"
              "b.setAttribute('aria-pressed',d?'true':'false')}s();b.addEventListener('click',function(){var r=document.documentElement;"
              "r.dataset.theme=r.dataset.theme==='dark'?'light':'dark';s()})})();</script>\n")

AREAS=[
 ('home','Home page hero and Start here'),
 ('library','Library and author index'),
 ('reading','Reading pages'),
 ('sources','Sources and credits'),
 ('nav','Navigation and footer'),
]

def plain_header(d):
    return ('<header class="ph"><div class="wrap"><a class="brand" href="/">Bibliotheca Catholica</a><nav aria-label="Sections">'
            +''.join('<a href="'+E(h)+'">'+E(t)+'</a>' for h,t in d['nav'])+'<a href="/search/">Search</a></nav></div></header>\n')

def plain_footer(d):
    keep=[('/about/','About the library'),('/rights/','Rights & Permissions'),('/takedown/','Takedown requests'),('/licensing/','Licensing & credits'),('/disclosure/','Affiliate disclosure'),('/policy/','Fidelity & Editorial Policy')]
    return ('<footer class="footer"><div class="pf"><div class="wrap"><p>'+''.join('<a href="'+h+'">'+E(t)+'</a>' for h,t in keep)+'</p>'
            '<details><summary>About this independent project</summary><p>'+d['non_affiliation']+'</p><p>'+d['social']+'</p></details>'
            '<p>'+d['footer_credit']+'</p></div></div></footer>\n')

def page(d,area,v,name,idea,body,css,header=None,footer=None,script=''):
    vs=VARIANTS[area]
    title='Design preview: '+dict(AREAS)[area]+', '+v+' ('+name+') · Bibliotheca Catholica'
    bar=('<div class="pv-bar" role="region" aria-label="Design preview"><div class="wrap"><b>Design preview, not a live page</b>'
         '<span>'+E(dict(AREAS)[area])+'</span><span class="pv-v">'
         +''.join('<a href="/design-preview/'+area+'/'+k+'/"'+(' aria-current="page"' if k==v else '')+' title="'+E(n)+'">'+k+'</a>' for k,n,_ in vs)
         +'</span><a href="/design-preview/">All previews</a><button type="button" id="pv-theme" aria-pressed="false">Dark theme</button></div></div>\n')
    note='<div class="wrap"><p class="pv-note"><b>'+E(v)+': '+E(name)+'.</b> '+E(idea)+'</p></div>\n'
    return ('<!doctype html>\n<html lang="en" data-theme="light">\n<head>\n'+ga_tag()+
            '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>'+E(title)+'</title>\n<meta name="robots" content="noindex,nofollow">\n'
            '<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">\n<link rel="stylesheet" href="/styles/fonts.css">\n'
            '<style>'+BASE_CSS+css+'</style>\n'+THEME_INIT+'</head>\n<body>\n<a class="skip" href="#main">Skip to content</a>\n'
            +bar+(header if header is not None else plain_header(d))+note+'<main id="main" tabindex="-1">\n'+body+'\n</main>\n'
            +(footer if footer is not None else plain_footer(d))+THEME_TOGGLE+script+'</body>\n</html>\n')

def portrait(pid,size,has=True,name=''):
    if has:return '<img class="pt" src="/assets/portraits/'+E(pid)+'.webp" width="'+str(size)+'" height="'+str(size)+'" loading="lazy" decoding="async" alt="">'
    return '<span class="pt pt-i" style="width:'+str(size)+'px;height:'+str(size)+'px" aria-hidden="true">'+E(name[:1])+'</span>'

def coverimg(w,wd,ht,lazy=True):
    if w['cover']:return '<img class="cv" src="'+E(w['cover'])+'" width="'+str(wd)+'" height="'+str(ht)+'"'+(' loading="lazy"' if lazy else '')+' decoding="async" alt="">'
    return '<span class="cv cv-none" style="width:'+str(wd)+'px;height:'+str(ht)+'px" aria-hidden="true"></span>'

# ---------------------------------------------------------------- a. home
HOME_CTA='<a class="btn" href="/library/">Enter the reading room</a> <a class="tlink" href="/reading/">Help me choose a book</a>'
def home_links(d):
    return '<ul class="rows hl">'+''.join('<li><a href="'+E(h)+'">'+E(l)+'</a> <span class="muted">'+E(t)+'</span></li>' for h,l,t in d['HOME_LINKS'])+'</ul>'
def figure(d,cls='frontis'):
    return '<figure class="'+cls+'">'+d['hero_img']+'<figcaption>'+d['hero_cap']+'</figcaption></figure>'
HOME_CSS='''.tlink{font:500 15px var(--sans);display:inline-flex;align-items:center;min-height:44px;margin-left:var(--s-4)}
.hl li a{font-weight:600}
figure{margin:0}figcaption{font:var(--t-xs)/1.5 var(--sans);color:var(--muted);margin-top:var(--s-2)}
.pt{border-radius:50%;object-fit:cover;display:block;background:var(--bg2)}.pt-i{display:grid;place-items:center;font:600 var(--t-lg) var(--display);color:var(--muted)}
.cv{display:block;border:1px solid var(--line);background:var(--bg2)}
section{margin:var(--s-7) 0}h2{font-size:var(--t-xl);margin-bottom:var(--s-4)}
.about p{max-width:66ch}
'''
def home_v1(d):
    shelf=''.join('<li><span class="num">'+ROMAN[i]+'.</span><a href="/work/'+E(w['id'])+'/">'+E(w['title'])+'</a><span class="lead" aria-hidden="true"></span><span class="au">'+E(w['author'])+'</span></li>' for i,w in enumerate(d['shelf']))
    people=''.join('<li><a href="/author/'+E(p['id'])+'/">'+portrait(p['id'],64)+'<span>'+E(p['name'])+'</span></a></li>' for p in d['people'])
    body=('<div class="wrap">'
     '<section class="tp" aria-labelledby="tp-h"><h1 id="tp-h" class="label">Bibliotheca Catholica</h1><p class="tp-title">Tolle Lege</p>'
     '<p class="tp-trans">Take up and read: two thousand years of Catholic books, free to read here.</p><p class="orn" aria-hidden="true">❦</p>'
     '<p class="cta">'+HOME_CTA+'</p></section>'
     +figure(d)+
     '<section aria-labelledby="sh-h"><h2 id="sh-h">Start here</h2><ol class="contents">'+shelf+'</ol></section>'
     '<section aria-labelledby="pe-h"><h2 id="pe-h">Saints and authors</h2><ul class="people">'+people+'</ul></section>'
     '<nav aria-label="Explore">'+home_links(d)+'</nav>'
     '<section class="about" aria-labelledby="ab-h"><h2 id="ab-h">About the library</h2><p>'+d['home_about']+'</p><p><a href="/about/">How the library works</a></p></section>'
     '</div>')
    css=HOME_CSS+'''.tp{text-align:center;margin:var(--s-8) auto var(--s-6);max-width:40rem}
.tp-title{font:600 clamp(56px,10vw,96px)/1 var(--display);letter-spacing:-.02em;margin:var(--s-3) 0}
.tp-trans{font-style:italic;font-size:var(--t-lg);color:var(--ink2);margin:0}
.orn{color:var(--gold);font-size:var(--t-xl);margin:var(--s-5) 0}.cta{margin:0}.cta .tlink{margin-left:var(--s-4)}
.frontis{max-width:360px;margin:0 auto var(--s-7);text-align:center}.frontis img{border:1px solid var(--line)}
section:not(.tp){max-width:42rem;margin-left:auto;margin-right:auto}nav[aria-label=Explore]{max-width:42rem;margin:0 auto}
section h2{text-align:center}
.contents{list-style:none;padding:0;margin:0;font-size:var(--t-lg)}
.contents li{display:flex;align-items:baseline;gap:var(--s-2);padding:var(--s-2) 0}
.contents .num{min-width:2.4em;color:var(--gold-ink);font-family:var(--display)}
.contents .lead{flex:1;border-bottom:1px dotted var(--rule);transform:translateY(-.3em);min-width:var(--s-5)}
.contents .au{color:var(--muted);font-size:var(--t-md)}
.people{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;justify-content:center;gap:var(--s-4) var(--s-5)}
.people a{display:flex;flex-direction:column;align-items:center;gap:var(--s-2);width:96px;text-align:center;font-size:var(--t-xs);line-height:1.3;color:var(--ink);text-decoration:none}
.people a:hover span{color:var(--rubric);text-decoration:underline}
@media(max-width:560px){.contents li{flex-wrap:wrap}.contents .lead{display:none}.contents .au{flex-basis:100%;padding-left:2.9em}.cta .tlink{margin-left:0;display:flex;justify-content:center}}
'''
    return body,css
def home_v2(d):
    shelf=''.join('<li><a class="sw" href="/work/'+E(w['id'])+'/">'+coverimg(w,48,72)+'<span><b>'+E(w['title'])+'</b><span class="au">'+E(w['author'])+'</span><span class="ds">'+E(w['desc'])+'</span></span></a></li>' for w in d['shelf'])
    people=''.join('<li><a href="/author/'+E(p['id'])+'/">'+portrait(p['id'],56)+'<span><b>'+E(p['name'])+'</b><span class="muted">'+E(p['dates'])+'</span></span></a></li>' for p in d['people'])
    body=('<div class="wrap"><section class="spread">'+figure(d,'verso')+
     '<div class="recto"><h1 class="label">Bibliotheca Catholica</h1><p class="tp-title">Tolle Lege</p><p class="tp-trans">Take up and read: two thousand years of Catholic books, free to read here.</p>'
     '<hr><p class="intro">'+d['home_about']+'</p><p class="cta">'+HOME_CTA+'</p></div></section>'
     '<section aria-labelledby="sh-h"><h2 id="sh-h">Start here</h2><ul class="rows shelf">'+shelf+'</ul></section>'
     '<div class="two"><section aria-labelledby="pe-h"><h2 id="pe-h">Saints and authors</h2><ul class="rows ppl">'+people+'</ul></section>'
     '<section aria-labelledby="ex-h"><h2 id="ex-h">Explore</h2>'+home_links(d)+'<p><a href="/about/">How the library works</a></p></section></div></div>')
    css=HOME_CSS+'''.spread{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:var(--s-8);align-items:center;margin-top:var(--s-7);padding-bottom:var(--s-7);border-bottom:1px solid var(--line)}
.verso img{border:1px solid var(--line)}
.tp-title{font:600 clamp(52px,7vw,84px)/1 var(--display);letter-spacing:-.02em;margin:var(--s-2) 0 var(--s-3)}
.tp-trans{font-style:italic;font-size:var(--t-lg);color:var(--ink2);margin:0}
.recto hr{border:0;border-top:1px solid var(--gold);width:64px;margin:var(--s-5) 0}.intro{max-width:52ch;color:var(--ink2)}
.shelf .sw{display:flex;gap:var(--s-4);text-decoration:none;color:var(--ink)}.shelf b{display:block;font:600 var(--t-lg)/1.2 var(--display);color:var(--rubric)}
.shelf .sw:hover b{text-decoration:underline}.shelf .au{display:block;color:var(--muted);font-size:var(--t-sm)}.shelf .ds{display:block;font-size:var(--t-sm);max-width:66ch;margin-top:var(--s-1)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:var(--s-7)}
.ppl a{display:flex;gap:var(--s-3);align-items:center;text-decoration:none;color:var(--ink)}.ppl b{display:block;font-weight:500}.ppl a:hover b{color:var(--rubric);text-decoration:underline}
.ppl .muted{font-size:var(--t-xs)}
@media(max-width:760px){.spread,.two{grid-template-columns:1fr;gap:var(--s-5)}.verso{max-width:300px}.tlink{margin-left:0}}
'''
    return body,css
def home_v3(d):
    shelf=''.join('<li><p class="t"><a href="/work/'+E(w['id'])+'/">'+E(w['title'])+'</a></p><p class="au">'+E(w['author'])+(' · '+E(w['category']))+'</p><p class="ds">'+E(w['desc'])+'</p></li>' for w in d['shelf'])
    people=''.join('<li><a href="/author/'+E(p['id'])+'/">'+E(p['name'])+'</a></li>' for p in d['people'])
    facts=f"{d['hosted']} editions to read here · {d['authors_n']} authors · {d['books_n']:,} books in the Isidore Index"
    body=('<div class="wrap"><section class="mast"><h1 class="label">Bibliotheca Catholica</h1><p class="tp-title">Tolle Lege</p>'
     '<p class="tp-trans">Take up and read: two thousand years of Catholic books, free to read here.</p><p class="facts">'+E(facts)+'</p><p class="cta">'+HOME_CTA+'</p></section>'
     '<section class="shelf" aria-labelledby="sh-h"><h2 id="sh-h">Start here</h2><ol class="annot">'+shelf+'</ol></section>'
     '<section class="names" aria-labelledby="pe-h"><h2 id="pe-h">Saints and authors</h2><ul>'+people+'</ul><p><a href="/authors/">All authors</a></p></section>'
     '<section class="about-v" aria-labelledby="ab-h">'+figure(d,'vignette')+'<div><h2 id="ab-h">About the library</h2><p>'+d['home_about']+'</p><p><a href="/about/">How the library works</a></p>'+home_links(d)+'</div></section></div>')
    css=HOME_CSS+'''.mast{margin:var(--s-8) 0 var(--s-7);max-width:44rem}
.tp-title{font:600 clamp(48px,7vw,72px)/1 var(--display);letter-spacing:-.015em;margin:var(--s-2) 0}
.tp-trans{font-style:italic;font-size:var(--t-lg);color:var(--ink2);margin:0 0 var(--s-4)}
.facts{font-size:var(--t-sm);color:var(--muted);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:var(--s-2) 0;margin:0 0 var(--s-5)}
.annot{list-style:none;padding:0;margin:0;counter-reset:n;max-width:44rem}
.annot li{counter-increment:n;position:relative;padding:var(--s-4) 0 var(--s-4) 3em;border-top:1px solid var(--line)}
.annot li::before{content:counter(n);position:absolute;left:0;top:var(--s-4);font:600 var(--t-xl)/1 var(--display);color:var(--gold-ink)}
.annot p{margin:0}.annot .t{font:600 var(--t-xl)/1.2 var(--display)}.annot .au{color:var(--muted);font-size:var(--t-sm);margin:var(--s-1) 0}.annot .ds{max-width:60ch}
.names ul{list-style:none;padding:0;margin:0;columns:2 16rem;column-gap:var(--s-7)}.names li{padding:var(--s-1) 0;break-inside:avoid}
.about-v{display:grid;grid-template-columns:200px minmax(0,1fr);gap:var(--s-6);align-items:start;border-top:1px solid var(--line);padding-top:var(--s-6)}
.about-v p{max-width:60ch}
@media(max-width:640px){.about-v{grid-template-columns:1fr}.vignette{max-width:200px}.tlink{margin-left:0}}
'''
    return body,css
def home_v4(d):
    cards=''.join('<li>'+portrait(p['id'],112)+'<p class="nm"><a href="/author/'+E(p['id'])+'/">'+E(p['name'])+'</a></p><p class="dt">'+E(p['dates'])+'</p>'
                  +('<p class="bk">Begin with <a href="/work/'+E(p['work']['id'])+'/"><cite>'+E(p['work']['title'])+'</cite></a></p>' if p['work'] else '')+'</li>' for p in d['people'])
    body=('<section class="band"><img src="/assets/hero/dore-paradiso-31-640.webp" srcset="/assets/hero/dore-paradiso-31-360.webp 360w, /assets/hero/dore-paradiso-31-640.webp 640w" sizes="100vw" width="640" height="710" fetchpriority="high" decoding="async" alt="Engraving: Dante and Beatrice look up at the highest heaven, a vast rose of light ringed with angels.">'
     '<div class="wrap band-t"><h1 class="label">Bibliotheca Catholica</h1><p class="tp-title">Tolle Lege</p><p class="tp-trans">Take up and read: two thousand years of Catholic books, free to read here.</p><p class="cta">'+HOME_CTA+'</p></div></section>'
     '<div class="wrap"><p class="cap">'+d['hero_cap']+'</p>'
     '<section aria-labelledby="pe-h"><h2 id="pe-h">Saints and authors</h2><ul class="gallery">'+cards+'</ul></section>'
     '<nav aria-label="Explore">'+home_links(d)+'</nav>'
     '<section class="about" aria-labelledby="ab-h"><h2 id="ab-h">About the library</h2><p>'+d['home_about']+'</p><p><a href="/about/">How the library works</a></p></section></div>')
    css=HOME_CSS+'''.band{position:relative;border-bottom:1px solid var(--line);background:var(--bg2);overflow:hidden}
.band img{position:absolute;right:0;top:0;width:min(46%,520px);height:100%;object-fit:cover;object-position:50% 88%}
.band-t{position:relative;padding-top:var(--s-8);padding-bottom:var(--s-8)}.band-t>*{max-width:30rem}
.tp-title{font:600 clamp(52px,7vw,84px)/1 var(--display);letter-spacing:-.02em;margin:var(--s-2) 0}
.tp-trans{font-style:italic;font-size:var(--t-lg);color:var(--ink2);margin:0 0 var(--s-5)}
.cap{font:var(--t-xs)/1.5 var(--sans);color:var(--muted);text-align:right;margin:var(--s-2) 0 0}
.gallery{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:var(--s-6) var(--s-5)}
.gallery li{text-align:center}.gallery .pt{margin:0 auto var(--s-3)}.gallery p{margin:0}.gallery .nm{font:600 var(--t-lg)/1.2 var(--display)}.gallery .nm a{color:var(--ink);text-decoration:none}
.gallery .nm a:hover{color:var(--rubric);text-decoration:underline}.gallery .dt{font-size:var(--t-xs);color:var(--muted)}.gallery .bk{font-size:var(--t-sm);margin-top:var(--s-1)}
@media(max-width:720px){.band img{position:static;width:100%;height:220px}.band-t{padding-top:var(--s-5);padding-bottom:var(--s-6)}.cap{text-align:left}.tlink{margin-left:0}}
'''
    return body,css

# ---------------------------------------------------------------- b. library and author index
# One small filter for every variation: a form[data-for=<list id>] holds a text field (data-q), a subject or era
# control (name=c, select or radios, or buttons with aria-pressed), and a "Read on this site" checkbox (data-h).
FILTER_JS='''<script>(function(){function norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')}
document.querySelectorAll('form[data-for]').forEach(function(f){var list=document.getElementById(f.dataset.for);if(!list)return;
var out=f.querySelector('output'),items=[].slice.call(list.querySelectorAll('[data-s]')),groups=[].slice.call(list.querySelectorAll('[data-group]'));
function cat(){var r=f.querySelector('[name=c]:checked');if(r)return r.value;var s=f.querySelector('select[name=c]');if(s)return s.value;
var b=f.querySelector('button[name=c][aria-pressed=true]');return b?b.value:''}
function run(){var q=norm((f.querySelector('[data-q]')||{}).value),c=cat(),h=(f.querySelector('[data-h]')||{}).checked,n=0;
items.forEach(function(li){var ok=(!q||li.dataset.s.indexOf(q)>=0)&&(!c||li.dataset.c===c)&&(!h||li.dataset.h==='1');li.hidden=!ok;if(ok)n++});
groups.forEach(function(g){g.hidden=!g.querySelector('[data-s]:not([hidden])')});if(out)out.textContent=n+' of '+items.length}
f.addEventListener('input',run);f.addEventListener('change',run);f.addEventListener('submit',function(e){e.preventDefault()});
f.querySelectorAll('button[name=c]').forEach(function(b){b.addEventListener('click',function(){f.querySelectorAll('button[name=c]').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});run()})});run()})})();</script>
'''
def norm(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
def wattrs(w):return ' data-s="'+E(norm(w['title']+' '+w['author']+' '+w['category']))+'" data-c="'+E(w['category'])+'" data-h="'+('1' if w['hosted'] else '0')+'"'
def aattrs(a):return ' data-s="'+E(norm(a['name']+' '+a['desc']))+'" data-c="'+E(a['era'])+'" data-h="'+('1' if a['hosted'] else '0')+'"'
def subjects(d):
    from collections import Counter
    c=Counter(w['category'] for w in d['works'])
    order=[];[order.append(w['category']) for w in d['works'] if w['category'] not in order]
    return [(k,c[k]) for k in order]
def eras(d):
    from collections import Counter
    c=Counter(a['era'] for a in d['authors'])
    return [(e['id'],e['label'],e['range'],c[e['id']]) for e in d['eras'] if c[e['id']]]
LIB_CSS='''.pt{border-radius:50%;object-fit:cover;display:block;background:var(--bg2);flex:none}.pt-i{display:grid;place-items:center;font:600 var(--t-md) var(--display);color:var(--muted)}
.cv{display:block;flex:none;border:1px solid var(--line);background:var(--bg2)}.cv-none{background:repeating-linear-gradient(90deg,var(--bg2) 0 6px,transparent 6px 7px)}
.head{margin:var(--s-7) 0 var(--s-5);max-width:66ch}.head h1{font-size:var(--t-3xl)}.head p{color:var(--ink2);margin:var(--s-3) 0 0}
h2{font-size:var(--t-2xl);margin:var(--s-7) 0 var(--s-4)}
form label,form legend,.ctl{font:500 var(--t-xs)/1.3 var(--sans);color:var(--ink2)}
input[type=search],select{font:var(--t-sm) var(--sans);color:var(--ink);background:var(--card);border:1px solid var(--rule);border-radius:6px;min-height:44px;padding:0 var(--s-3)}
input[type=checkbox],input[type=radio]{accent-color:var(--rubric);width:18px;height:18px;margin:0}
output{font:var(--t-xs) var(--sans);color:var(--muted)}
[hidden]{display:none!important}
'''
def lib_head(t,p):return '<div class="head"><p class="label">Discover &amp; Read</p><h1>'+t+'</h1><p>'+p+'</p></div>'
LIB_INTRO='Classic Catholic books to read here, with their sources and every other way to read them.'
AU_INTRO='From the Apostolic Fathers to the present day.'
def library_v1(d):
    subj=''.join('<label class="fc"><input type="radio" name="c" value="'+E(k)+'"> <span>'+E(k)+'</span> <span class="n">'+str(n)+'</span></label>' for k,n in subjects(d))
    rows=''.join('<li'+wattrs(w)+'>'+coverimg(w,40,60)+'<div><p class="t"><a href="/work/'+E(w['id'])+'/">'+E(w['title'])+'</a>'+(' <span class="here">Read here</span>' if w['hosted'] else '')+'</p><p class="m">'+E(w['author'])+(' · '+E(w['date']) if w['date'] else '')+' · '+E(w['category'])+'</p><p class="ds">'+E(w['desc'])+'</p></div></li>' for w in d['works'])
    era=''.join('<label class="fc"><input type="radio" name="c" value="'+E(i)+'"> <span>'+E(l)+'</span> <span class="n">'+str(n)+'</span></label>' for i,l,r,n in eras(d))
    arows=''.join('<li'+aattrs(a)+'>'+portrait(a['id'],40,a['portrait'],a['name'])+'<div><p class="t"><a href="/author/'+E(a['id'])+'/">'+E(a['name'])+'</a></p><p class="m">'+E(a['dates'])+'</p><p class="ds">'+E(a['desc'])+'</p></div></li>' for a in d['authors'])
    def block(fid,lid,title,q,facets,legend,hosted,rows):
        return ('<section class="cat" aria-labelledby="'+lid+'-h"><h2 id="'+lid+'-h">'+title+'</h2><div class="grid"><form data-for="'+lid+'" class="facets" role="search" aria-label="Filter '+title.lower()+'">'
                '<label for="'+fid+'">Find</label><input id="'+fid+'" type="search" data-q placeholder="'+q+'">'
                '<fieldset><legend>'+legend+'</legend><label class="fc"><input type="radio" name="c" value="" checked> <span>All</span></label>'+facets+'</fieldset>'
                +(('<label class="fc hc"><input type="checkbox" data-h> <span>Read on this site</span></label>') if hosted else '')+'</form>'
                '<div><p class="count" aria-live="polite"><output form="x"></output></p><ul class="rows res" id="'+lid+'">'+rows+'</ul></div></div></section>')
    body=('<div class="wrap">'+lib_head('The reading room',LIB_INTRO)
          +block('q1','works','The shelves','Title, author, or subject',subj,'Subject',True,rows)
          +block('q2','authors','Authors','Name or keyword',era,'Era',True,arows)+'</div>')
    body=body.replace('<p class="count" aria-live="polite"><output form="x"></output></p>','<p class="count" aria-live="polite"></p>')
    css=LIB_CSS+'''.grid{display:grid;grid-template-columns:240px minmax(0,1fr);gap:var(--s-6);align-items:start}
.facets{position:sticky;top:var(--s-4);max-height:calc(100vh - 32px);overflow:auto;display:flex;flex-direction:column;gap:var(--s-2);padding-right:var(--s-2)}
.facets input[type=search]{width:100%}.facets fieldset{border:0;padding:0;margin:var(--s-3) 0 0;display:flex;flex-direction:column}
.facets legend{font:500 var(--t-sm)/1.3 var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink);margin-bottom:var(--s-1)}
.fc{display:flex;gap:var(--s-2);align-items:center;min-height:32px;font:var(--t-sm)/1.25 var(--serif);color:var(--ink);cursor:pointer}.fc .n{margin-left:auto;color:var(--muted);font-size:var(--t-xs);font-variant-numeric:lining-nums}
.hc{border-top:1px solid var(--line);padding-top:var(--s-2);margin-top:var(--s-2)}
.count{margin:0 0 var(--s-2);font:var(--t-xs) var(--sans);color:var(--muted)}
.res li{display:flex;gap:var(--s-4);align-items:flex-start}.res p{margin:0}.res .t{font:600 var(--t-lg)/1.2 var(--display)}
.res .here{font:500 12px var(--sans);color:var(--gold-ink);margin-left:var(--s-2);white-space:nowrap}
.res .m{font-size:var(--t-sm);color:var(--muted)}.res .ds{font-size:var(--t-sm);max-width:66ch;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
@media(max-width:760px){.grid{grid-template-columns:1fr}.facets{position:static;max-height:none;overflow:visible}.facets fieldset{flex-direction:row;flex-wrap:wrap;gap:0 var(--s-4)}.fc .n{margin-left:var(--s-1)}}
'''
    js=FILTER_JS.replace("var out=f.querySelector('output')","var out=f.parentNode.querySelector('.count')")
    return body,css,js
def library_v2(d):
    subj=subjects(d)
    jump=' · '.join('<a href="#s-'+str(i)+'">'+E(k)+'</a>&nbsp;<span class="n">'+str(n)+'</span>' for i,(k,n) in enumerate(subj))
    groups=''.join('<div class="grp" data-group id="s-'+str(i)+'"><h3>'+E(k)+' <span class="n">'+str(n)+'</span></h3><ul class="list">'+''.join('<li'+wattrs(w)+'><a href="/work/'+E(w['id'])+'/">'+E(w['title'])+'</a> <span class="au">'+E(w['author'])+'</span>'+(' <span class="dt">'+E(w['date'])+'</span>' if w['date'] else '')+'</li>' for w in d['works'] if w['category']==k)+'</ul></div>' for i,(k,n) in enumerate(subj))
    er=eras(d)
    ajump=' · '.join('<a href="#e-'+E(i)+'">'+E(l)+'</a>' for i,l,r,n in er)
    agroups=''.join('<div class="grp" data-group id="e-'+E(i)+'"><h3>'+E(l)+' <span class="n">'+E(r)+' · '+str(n)+'</span></h3><ul class="list">'+''.join('<li'+aattrs(a)+'><a href="/author/'+E(a['id'])+'/">'+E(a['name'])+'</a> <span class="dt">'+E(a['dates'])+'</span></li>' for a in d['authors'] if a['era']==i)+'</ul></div>' for i,l,r,n in er)
    def bar(fid,lid,ph,opts,hosted):
        return ('<form class="bar" data-for="'+lid+'" role="search" aria-label="Filter"><label for="'+fid+'">Find</label><input id="'+fid+'" type="search" data-q placeholder="'+ph+'">'
                '<label for="'+fid+'c">Show</label><select id="'+fid+'c" name="c"><option value="">All</option>'+opts+'</select>'
                +('<label class="ck"><input type="checkbox" data-h> Read on this site</label>' if hosted else '')+'<output aria-live="polite"></output></form>')
    body=('<div class="wrap">'+lib_head('The reading room',LIB_INTRO)
      +'<section aria-labelledby="w-h"><h2 id="w-h">The shelves</h2><p class="jump">'+jump+'</p>'+bar('q1','works','Title, author, or subject',''.join('<option>'+E(k)+'</option>' for k,n in subj),True)+'<div id="works">'+groups+'</div></section>'
      +'<section aria-labelledby="a-h"><h2 id="a-h">Authors</h2><p class="jump">'+ajump+'</p>'+bar('q2','authors','Name or keyword',''.join('<option value="'+E(i)+'">'+E(l)+'</option>' for i,l,r,n in er),False)+'<div id="authors">'+agroups+'</div></section></div>')
    css=LIB_CSS+'''.jump{font-size:var(--t-sm);line-height:2;max-width:none;color:var(--muted);margin:0 0 var(--s-4)}.n{color:var(--muted);font-size:var(--t-xs);font-variant-numeric:lining-nums}
.bar{display:flex;flex-wrap:wrap;gap:var(--s-2) var(--s-3);align-items:center;padding:var(--s-3) 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-bottom:var(--s-5)}
.bar input[type=search]{flex:1 1 220px}.ck{display:flex;gap:var(--s-2);align-items:center;min-height:44px}.bar output{margin-left:auto}
.grp h3{font:500 var(--t-md)/1.3 var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink);border-bottom:1px solid var(--line);padding-bottom:var(--s-1);margin:var(--s-5) 0 var(--s-2)}
.list{list-style:none;margin:0;padding:0;columns:2 22rem;column-gap:var(--s-7)}.list li{break-inside:avoid;padding:3px 0;font-size:var(--t-sm);line-height:1.4}
.list a{font-weight:500}.list .au{color:var(--ink2)}.list .dt{color:var(--muted);font-size:var(--t-xs)}
'''
    return body,css,FILTER_JS
def library_v3(d):
    subj=subjects(d)
    btns='<button type="button" name="c" value="" aria-pressed="true">All</button>'+''.join('<button type="button" name="c" value="'+E(k)+'" aria-pressed="false">'+E(k)+'</button>' for k,n in subj)
    tiles=''.join('<li'+wattrs(w)+'><a href="/work/'+E(w['id'])+'/">'+(coverimg(w,120,180) if w['cover'] else '<span class="cv spine" aria-hidden="true"><span>'+E(w['title'])+'</span></span>')+'<span class="t">'+E(w['title'])+'</span><span class="au">'+E(w['author'])+'</span></a></li>' for w in d['works'])
    er=eras(d)
    ebtns='<button type="button" name="c" value="" aria-pressed="true">All</button>'+''.join('<button type="button" name="c" value="'+E(i)+'" aria-pressed="false">'+E(l)+'</button>' for i,l,r,n in er)
    people=''.join('<li'+aattrs(a)+'><a href="/author/'+E(a['id'])+'/">'+portrait(a['id'],72,a['portrait'],a['name'])+'<span class="t">'+E(a['name'])+'</span><span class="au">'+E(a['dates'])+'</span></a></li>' for a in d['authors'])
    def bar(lid,b,hosted,ph):
        return ('<form class="bar" data-for="'+lid+'" role="search" aria-label="Filter"><div class="seg" role="group" aria-label="Show">'+b+'</div><div class="row2"><label class="vh" for="q-'+lid+'">Find</label><input id="q-'+lid+'" type="search" data-q placeholder="'+ph+'">'
                +('<label class="ck"><input type="checkbox" data-h> Read on this site</label>' if hosted else '')+'<output aria-live="polite"></output></div></form>')
    body=('<div class="wrap">'+lib_head('The reading room',LIB_INTRO)
      +'<section aria-labelledby="w-h"><h2 id="w-h">The shelves</h2>'+bar('works',btns,True,'Title, author, or subject')+'<ul class="wall" id="works">'+tiles+'</ul></section>'
      +'<section aria-labelledby="a-h"><h2 id="a-h">Authors</h2>'+bar('authors',ebtns,True,'Name or keyword')+'<ul class="wall ppl" id="authors">'+people+'</ul></section></div>')
    css=LIB_CSS+'''.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.bar{margin-bottom:var(--s-5)}.seg{display:flex;flex-wrap:wrap;gap:0 var(--s-4);border-bottom:1px solid var(--line);margin-bottom:var(--s-3)}
.seg button{font:var(--t-sm)/1 var(--serif);color:var(--ink2);background:none;border:0;border-bottom:2px solid transparent;padding:var(--s-2) 0;min-height:40px;cursor:pointer;margin-bottom:-1px}
.seg button:hover{color:var(--rubric)}.seg button[aria-pressed=true]{color:var(--ink);border-bottom-color:var(--rubric)}
.row2{display:flex;flex-wrap:wrap;gap:var(--s-3);align-items:center}.row2 input[type=search]{flex:0 1 320px}.ck{display:flex;gap:var(--s-2);align-items:center;min-height:44px}.row2 output{margin-left:auto}
.wall{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:var(--s-6) var(--s-5)}
.wall a{display:flex;flex-direction:column;gap:var(--s-1);text-decoration:none;color:var(--ink)}.wall .cv{width:120px;height:180px}
.wall a:hover .t{color:var(--rubric);text-decoration:underline}.wall .t{font:600 var(--t-sm)/1.25 var(--serif);margin-top:var(--s-2)}.wall .au{font-size:var(--t-xs);color:var(--muted)}
.spine{display:flex;align-items:flex-end;padding:var(--s-3);background:var(--bg2);border:1px solid var(--line)}.spine span{font:600 var(--t-md)/1.15 var(--display);color:var(--ink2)}
.ppl{grid-template-columns:repeat(auto-fill,minmax(120px,1fr))}.ppl a{align-items:center;text-align:center}
@media(max-width:480px){.wall{grid-template-columns:repeat(2,1fr)}.wall .cv{width:100%;height:auto;aspect-ratio:2/3}}
'''
    return body,css,FILTER_JS
def library_v4(d):
    import string
    ws=sorted(d['works'],key=lambda w:re.sub(r'^(the|a|an) ','',norm(w['title'])))
    key=lambda w:re.sub(r'^(the|a|an) ','',norm(w['title']))[:1].upper()
    letters=sorted({key(w) for w in ws})
    az=''.join(('<a href="#l-'+c+'">'+c+'</a>' if c in letters else '<span aria-hidden="true">'+c+'</span>') for c in string.ascii_uppercase)
    groups=''.join('<div class="grp" data-group id="l-'+c+'"><h3>'+c+'</h3><ul class="idx">'+''.join('<li'+wattrs(w)+'><a href="/work/'+E(w['id'])+'/">'+E(w['title'])+'</a><span class="au">'+E(w['author'])+'</span>'+('<span class="here" title="Read on this site">Read here</span>' if w['hosted'] else '')+'</li>' for w in ws if key(w)==c)+'</ul></div>' for c in letters)
    er=eras(d)
    rail=''.join('<li><a href="#e-'+E(i)+'"><span>'+E(l)+'</span><span class="r">'+E(r)+'</span></a></li>' for i,l,r,n in er)
    agroups=''.join('<div class="grp" data-group id="e-'+E(i)+'"><h3>'+E(l)+' <span class="r">'+E(r)+'</span></h3><ul class="chron">'+''.join('<li'+aattrs(a)+'><span class="dt">'+E(a['dates'])+'</span><a href="/author/'+E(a['id'])+'/">'+E(a['name'])+'</a></li>' for a in d['authors'] if a['era']==i)+'</ul></div>' for i,l,r,n in er)
    body=('<div class="wrap">'+lib_head('The reading room',LIB_INTRO)
      +'<section aria-labelledby="w-h"><h2 id="w-h">Works, A to Z</h2><form class="bar" data-for="works" role="search" aria-label="Filter works"><label for="q1">Find</label><input id="q1" type="search" data-q placeholder="Title, author, or subject">'
      +'<label class="ck"><input type="checkbox" data-h> Read on this site</label><output aria-live="polite"></output></form><nav class="az" aria-label="Titles by letter">'+az+'</nav><div id="works">'+groups+'</div></section>'
      +'<section aria-labelledby="a-h"><h2 id="a-h">Authors by era</h2><div class="split"><nav class="rail" aria-label="Eras"><ol>'+rail+'</ol></nav><div><form class="bar" data-for="authors" role="search" aria-label="Filter authors"><label for="q2">Find</label><input id="q2" type="search" data-q placeholder="Name or keyword"><output aria-live="polite"></output></form><div id="authors">'+agroups+'</div></div></div></section></div>')
    css=LIB_CSS+'''.bar{display:flex;flex-wrap:wrap;gap:var(--s-2) var(--s-3);align-items:center;margin-bottom:var(--s-3)}.bar input[type=search]{flex:0 1 320px}.ck{display:flex;gap:var(--s-2);align-items:center;min-height:44px}.bar output{margin-left:auto}
.az{display:flex;flex-wrap:wrap;gap:2px;font:600 var(--t-sm)/1 var(--display);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:var(--s-1) 0;position:sticky;top:0;background:var(--bg);z-index:2}
.az a,.az span{display:grid;place-items:center;min-width:28px;min-height:32px;text-decoration:none}.az span{color:var(--line)}.az a:hover{background:var(--bg2)}
.grp h3{font:600 var(--t-xl)/1 var(--display);color:var(--gold-ink);margin:var(--s-5) 0 var(--s-2)}
.idx{list-style:none;margin:0;padding:0;columns:2 24rem;column-gap:var(--s-7)}.idx li{break-inside:avoid;padding:var(--s-1) 0;font-size:var(--t-sm);line-height:1.4;display:flex;flex-wrap:wrap;gap:0 var(--s-2)}
.idx .au{color:var(--muted)}.idx .here{font:500 11px/1.8 var(--sans);color:var(--gold-ink)}
.split{display:grid;grid-template-columns:220px minmax(0,1fr);gap:var(--s-6);align-items:start}
.rail{position:sticky;top:var(--s-4)}.rail ol{list-style:none;margin:0;padding:0 0 0 var(--s-3);border-left:1px solid var(--rule)}
.rail a{display:flex;flex-direction:column;padding:var(--s-1) 0;text-decoration:none;font-size:var(--t-sm);line-height:1.25;color:var(--ink)}.rail a:hover span:first-child{color:var(--rubric);text-decoration:underline}
.rail .r,.grp h3 .r{font:var(--t-xs) var(--sans);color:var(--muted);font-variant-numeric:lining-nums}
.chron{list-style:none;margin:0;padding:0}.chron li{display:grid;grid-template-columns:8.5em minmax(0,1fr);gap:var(--s-3);padding:var(--s-1) 0;border-top:1px solid var(--line);font-size:var(--t-sm)}
.chron .dt{color:var(--muted);font-variant-numeric:lining-nums;font-size:var(--t-xs);padding-top:2px}
@media(max-width:760px){.split{grid-template-columns:1fr}.rail{position:static}.rail ol{columns:2;border-left:0;padding:0}}
'''
    return body,css,FILTER_JS

# ---------------------------------------------------------------- c. reading pages (Orthodoxy, PG #130)
from datetime import date as _date
def longdate(s):
    y,m,dd=map(int,s.split('-'));return _date(y,m,dd).strftime('%B ')+str(dd)+', '+str(y)
def reading_parts(d):
    o=d['ortho'];ch=o['chapters']
    text=''.join('<p'+(' class="dc"' if i==0 else '')+'>'+p+'</p>' for i,p in enumerate(o['ch2']))
    end9=''.join('<p>'+p+'</p>' for p in o['ch9_end'])
    excerpt='<p class="excerpt">Preview excerpt: the first '+str(len(o['ch2']))+' of the chapter’s '+str(o['ch2_total'])+' paragraphs. <a href="'+ch[1][0]+'">Read the whole chapter</a>.</p>'
    return o,ch,text,end9,excerpt
def roman_title(t):
    m=re.match(r'([IVXL]+)\. (.*)',t);return (m.group(1),m.group(2)) if m else ('',t)
def opener(num,title):
    return '<header class="op"><p class="op-l">Chapter</p><p class="op-n">'+num+'</p><h1>'+E(title)+'</h1><p class="orn" aria-hidden="true">❦</p></header>'
def colophon_facts(d):
    o=d['ortho'];e=o['ed'];w=o['work']
    return [('Work',E(w['title'])+', by '+E(o['author'])+(' ('+E(w['date'])+')' if w.get('date') else '')),
            ('Edition',E(e['label'])+', released '+E(e['digitalRelease'])+' · <a href="'+E(e['source'])+'" target="_blank" rel="noopener">Source record</a>'),
            ('About the text',o['about']),
            ('Length',o['facts']),
            ('Rights',E(e['rights'])+' <a href="/rights/">How rights are checked</a>'),
            ('Checked',E(longdate(e['checked']))),
            ('Text file','<code>'+E(e['text'].split('/')[-1])+'</code>, SHA-256 <code class="sha">'+E(e['sha256'])+'</code>'),
            ('Other formats','<a download href="'+E(o['epub'])+'">EPUB</a> · <a href="/'+E(e['text'])+'">Plain text</a>'),
            ('Type','Set in EB Garamond and Cormorant Garamond.')]
def edition_details(d):
    o=d['ortho'];e=o['ed']
    return ('<details class="ed"><summary>Edition details</summary><p>'+E(e['note'])+'</p><p>Source: '+E(o['author'])+'. '+E(o['work']['title'])+'. '+E(e['label'])+'. <a href="'+E(e['source'])+'" target="_blank" rel="noopener">Project Gutenberg record</a>. '+E(e['rights'])+'</p></details>')
READ_CSS='''.col{max-width:26em;margin:0 auto;font-size:21px;line-height:1.6}
.col p{margin:0;text-indent:1.5em}.col .op p,.col .end p{text-indent:0}.col .dc{text-indent:0}
.dc::first-letter{float:left;font:600 3.1em/.82 var(--display);color:var(--rubric);margin:.06em .08em 0 0}
.op{text-align:center;margin:var(--s-7) 0 var(--s-6)}.op p{margin:0}.op-l{font:500 var(--t-sm) var(--serif);font-variant-caps:all-small-caps;letter-spacing:.18em;color:var(--muted)}
.op-n{font:600 64px/1 var(--display);color:var(--rubric);margin:var(--s-2) 0!important}.op h1{font-size:var(--t-2xl);font-weight:500}
.orn{color:var(--gold);font-size:var(--t-lg);text-align:center;margin:var(--s-4) 0!important;text-indent:0!important}
.excerpt{font:var(--t-xs)/1.5 var(--sans)!important;color:var(--muted);text-indent:0!important;margin:var(--s-5) 0!important;padding:var(--s-2) 0;border-top:1px dashed var(--rule);border-bottom:1px dashed var(--rule)}
.divider{max-width:26em;margin:var(--s-8) auto var(--s-5);font:var(--t-xs)/1.4 var(--sans);color:var(--muted);text-align:center;border-top:1px solid var(--line);padding-top:var(--s-3)}
.end{text-align:center;margin:var(--s-6) 0}.end p{margin:0;text-indent:0}.end .e{font:500 var(--t-sm) var(--serif);font-variant-caps:all-small-caps;letter-spacing:.12em;color:var(--muted)}
.pgn{max-width:26em;margin:var(--s-6) auto 0;font:var(--t-xs)/1.6 var(--serif);color:var(--muted)}
details.ed{max-width:26em;margin:var(--s-4) auto;font:var(--t-xs)/1.6 var(--sans);color:var(--ink2)}details.ed summary{cursor:pointer;min-height:24px;color:var(--rubric)}
code{font-size:.85em;overflow-wrap:anywhere}.us{display:none}
@media(max-width:560px){.col{font-size:19px}.op-n{font-size:52px}}
@media(max-width:28em){.col,.pgn,details.ed,.divider,.colo,.cont,.next{padding-left:var(--s-4);padding-right:var(--s-4)}}
'''
def reading_v1(d):
    o,ch,text,end9,excerpt=reading_parts(d)
    toc=''.join('<li><a href="'+u+'"'+(' aria-current="page"' if i==1 else '')+'>'+E(t)+'</a></li>' for i,(u,t) in enumerate(ch))
    rh=('<div class="rh"><div class="rh-in"><a class="bk" href="/work/orthodoxy/">Orthodoxy</a><span class="sep" aria-hidden="true">·</span><span class="cur">II. The Maniac</span>'
        '<details class="toc"><summary>Contents</summary><ol>'+toc+'</ol></details>'
        '<nav class="arrows" aria-label="Chapter"><a href="'+ch[0][0]+'" rel="prev" aria-label="Previous chapter: '+E(ch[0][1])+'">‹</a><a href="'+ch[2][0]+'" rel="next" aria-label="Next chapter: '+E(ch[2][1])+'">›</a></nav></div></div>')
    facts=''.join('<p><span class="k">'+k+'</span> '+v+'</p>' for k,v in colophon_facts(d))
    body=(rh+'<article class="col">'+opener('II','The Maniac')+text+excerpt
     +'<div class="end"><p class="orn" aria-hidden="true">❦</p><p class="e">End of Chapter II</p><p><a href="'+ch[2][0]+'">Next: '+E(ch[2][1])+'</a></p></div></article>'
     +'<nav class="pager" aria-label="Chapters"><a rel="prev" href="'+ch[0][0]+'"><span>Previous</span>'+E(ch[0][1])+'</a><a href="/work/orthodoxy/"><span>Contents</span>Orthodoxy</a><a rel="next" href="'+ch[2][0]+'"><span>Next</span>'+E(ch[2][1])+'</a></nav>'
     +'<p class="divider">Below: how the last chapter ends, with the colophon</p>'
     +'<article class="col" aria-label="End of the book">'+end9+'<div class="end"><p class="orn" aria-hidden="true">❦</p><p class="e">End of Chapter IX</p><p class="fin">The End</p></div>'
     +'<section class="colo" aria-labelledby="co-h"><h2 id="co-h">Colophon</h2>'+facts+'</section></article>'
     +'<p class="pgn">'+d['PG_LINE']+'</p>'+edition_details(d))
    css=READ_CSS+'''.rh{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}
.rh-in{max-width:44rem;margin:0 auto;padding:0 var(--s-4);display:flex;align-items:center;gap:var(--s-2);min-height:48px;font:var(--t-xs)/1.2 var(--sans);color:var(--ink2)}
.rh .bk{font-weight:600;color:var(--ink);text-decoration:none}.rh .cur{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.toc{margin-left:auto;position:relative}.toc summary{cursor:pointer;list-style:none;min-height:36px;display:flex;align-items:center;padding:0 var(--s-2);color:var(--rubric)}
.toc summary::-webkit-details-marker{display:none}.toc ol{position:absolute;right:0;top:100%;width:min(22rem,90vw);background:var(--card);border:1px solid var(--line);margin:0;padding:var(--s-2) var(--s-3);list-style:none;font:var(--t-sm)/1.3 var(--serif)}
.toc li a{display:block;padding:var(--s-1) 0;text-decoration:none;color:var(--ink)}.toc a[aria-current]{color:var(--rubric);font-weight:600}
.arrows{display:flex}.arrows a{display:grid;place-items:center;width:36px;height:36px;font:var(--t-lg)/1 var(--serif);text-decoration:none}
.end .fin{font:600 var(--t-xl) var(--display);margin-top:var(--s-3)}
.pager{max-width:44rem;margin:var(--s-6) auto 0;padding:var(--s-3) var(--s-4);display:grid;grid-template-columns:1fr auto 1fr;gap:var(--s-4);border-top:1px solid var(--line);border-bottom:1px solid var(--line);font:var(--t-sm)/1.3 var(--serif)}
.pager a{text-decoration:none;display:flex;flex-direction:column;gap:2px;min-height:44px}.pager a:last-child{text-align:right}.pager a:nth-child(2){text-align:center}.pager span{font:500 12px var(--sans);color:var(--muted)}
.colo{margin-top:var(--s-7);text-align:center;font-size:var(--t-sm);line-height:1.55}.colo h2{font:500 var(--t-md) var(--serif);font-variant-caps:all-small-caps;letter-spacing:.12em;color:var(--gold-ink);margin-bottom:var(--s-3)}
.colo p{text-indent:0;margin:0 0 var(--s-2)}.colo .k{display:block;font:500 12px var(--sans);color:var(--muted)}
@media(max-width:560px){.pager{grid-template-columns:1fr 1fr}.pager a:nth-child(2){display:none}}
'''
    return body,css
def reading_v2(d):
    o,ch,text,end9,excerpt=reading_parts(d)
    def toc(cur):return '<ol>'+''.join('<li><a href="'+u+'"'+(' aria-current="page"' if i==cur else '')+'><span class="n">'+roman_title(t)[0]+'</span>'+E(roman_title(t)[1])+'</a></li>' for i,(u,t) in enumerate(ch))+'</ol>'
    dl=''.join('<div><dt>'+k+'</dt><dd>'+v+'</dd></div>' for k,v in colophon_facts(d))
    body=('<div class="lay"><nav class="side" aria-label="Contents"><p class="bk"><a href="/work/orthodoxy/">Orthodoxy</a></p><p class="by">'+E(o['author'])+'</p>'
     '<details class="mtoc" open><summary>Contents</summary>'+toc(1)+'</details><p class="prog">Chapter II of '+str(len(ch))+'</p></nav>'
     '<div class="main"><article class="col">'+opener('II','The Maniac')+text+excerpt
     +'<div class="end"><p class="orn" aria-hidden="true">❦</p><p class="e">End of Chapter II</p></div></article>'
     +'<nav class="next" aria-label="Chapters"><a rel="prev" href="'+ch[0][0]+'">← '+E(ch[0][1])+'</a><a rel="next" href="'+ch[2][0]+'">'+E(ch[2][1])+' →</a></nav>'
     +'<p class="divider">Below: how the last chapter ends, with the colophon</p>'
     +'<article class="col" aria-label="End of the book">'+end9+'<div class="end"><p class="orn" aria-hidden="true">❦</p><p class="e">End of Chapter IX · End of the book</p></div></article>'
     +'<section class="colo" aria-labelledby="co-h"><h2 id="co-h">About this edition</h2><dl>'+dl+'</dl></section>'
     +'<p class="pgn">'+d['PG_LINE']+'</p>'+edition_details(d)+'</div></div>')
    css=READ_CSS+'''.lay{display:grid;grid-template-columns:240px minmax(0,1fr);gap:var(--s-6);max-width:1160px;margin:0 auto;padding:0 var(--s-4)}
.side{position:sticky;top:0;align-self:start;max-height:100vh;overflow:auto;padding:var(--s-6) 0;font:var(--t-sm)/1.35 var(--serif)}
.side p{margin:0}.side .bk{font:600 var(--t-lg)/1.2 var(--display)}.side .bk a{color:var(--ink);text-decoration:none}.side .by{color:var(--muted);margin-bottom:var(--s-4)!important}
.mtoc summary{font:500 var(--t-sm) var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink);cursor:pointer;min-height:32px}
.mtoc ol{list-style:none;margin:0;padding:0;border-left:1px solid var(--line)}
.mtoc a{display:flex;gap:var(--s-2);padding:var(--s-1) var(--s-3);text-decoration:none;color:var(--ink2);margin-left:-1px;border-left:2px solid transparent}
.mtoc a:hover{color:var(--rubric)}.mtoc a[aria-current]{color:var(--ink);border-left-color:var(--rubric);font-weight:600}.mtoc .n{min-width:2.2em;color:var(--muted);font-family:var(--display)}
.prog{margin-top:var(--s-4)!important;font:var(--t-xs) var(--sans);color:var(--muted)}
.next{max-width:26em;margin:var(--s-5) auto 0;display:flex;justify-content:space-between;gap:var(--s-4);font-size:var(--t-sm)}.next a{min-height:44px;display:flex;align-items:center}
.colo{max-width:30em;margin:var(--s-7) auto 0}.colo h2{font-size:var(--t-xl);text-align:center;margin-bottom:var(--s-4)}
.colo dl{margin:0;font-size:var(--t-sm);line-height:1.5}.colo dl div{display:grid;grid-template-columns:8em minmax(0,1fr);gap:var(--s-3);padding:var(--s-2) 0;border-top:1px solid var(--line)}
.colo dt{font:500 12px/1.9 var(--sans);color:var(--muted)}.colo dd{margin:0}
@media(max-width:860px){.lay{grid-template-columns:1fr;gap:0}.side{position:static;max-height:none;padding:var(--s-4) 0 0;border-bottom:1px solid var(--line)}.mtoc:not([open]) summary{margin-bottom:var(--s-2)}.colo dl div{grid-template-columns:1fr;gap:0}}
'''
    js='<script>if(matchMedia("(max-width: 860px)").matches){var t=document.querySelector(".mtoc");if(t)t.open=false}</script>\n'
    return body,css,js
def reading_v3(d):
    o,ch,text,end9,excerpt=reading_parts(d)
    strip=''.join('<li><a href="'+u+'" title="'+E(t)+'"'+(' aria-current="page"' if i==1 else '')+'><span class="vh">Chapter </span>'+roman_title(t)[0]+'</a></li>' for i,(u,t) in enumerate(ch))
    n3,t3=roman_title(ch[2][1])
    facts=''.join('<p><b>'+k+'.</b> '+v+'</p>' for k,v in colophon_facts(d))
    body=('<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="/library/">Reading Room</a> › <a href="/work/orthodoxy/">Orthodoxy</a> › <span aria-current="page">The Maniac</span></nav></div>'
     '<article class="col">'+opener('II','The Maniac')+'<nav class="strip" aria-label="Chapters of Orthodoxy"><ol>'+strip+'</ol></nav>'+text+excerpt
     +'<div class="end"><p class="orn" aria-hidden="true">❦</p><p class="e">End of Chapter II</p></div></article>'
     +'<a class="cont" href="'+ch[2][0]+'"><span class="k">Continue reading</span><span class="cn">Chapter '+n3+'</span><span class="ct">'+E(t3)+'</span><span class="cf">'+E(o['ch3_first'])+'</span></a>'
     +'<p class="divider">Below: how the last chapter ends, with the colophon</p>'
     +'<article class="col" aria-label="End of the book">'+end9+'<div class="end"><p class="orn" aria-hidden="true">❦ ❦ ❦</p><p class="fin">Finis</p></div></article>'
     +'<section class="colo" aria-labelledby="co-h"><p class="orn" aria-hidden="true">❦</p><h2 id="co-h">Colophon</h2>'+facts+'<p class="back"><a href="/work/orthodoxy/">Back to the title page</a> · <a href="/library/">Reading Room</a></p></section>'
     +'<p class="pgn">'+d['PG_LINE']+'</p>'+edition_details(d))
    css=READ_CSS+'''.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.crumbs{font:var(--t-xs)/1.5 var(--sans);color:var(--muted);margin-top:var(--s-4)}
.strip ol{list-style:none;margin:0 0 var(--s-6);padding:0;display:flex;justify-content:center;flex-wrap:wrap;gap:var(--s-1);font:600 var(--t-sm)/1 var(--display)}
.strip a{display:grid;place-items:center;min-width:40px;min-height:40px;padding:0 var(--s-2);text-decoration:none;color:var(--muted);border-bottom:2px solid var(--line)}
.strip a:hover{color:var(--rubric);border-bottom-color:var(--rubric)}.strip a[aria-current]{color:var(--rubric);border-bottom-color:var(--rubric)}
.cont{display:block;max-width:26em;margin:var(--s-6) auto 0;padding:var(--s-5) 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);text-decoration:none;color:var(--ink);text-align:center}
.cont span{display:block}.cont .k{font:500 12px var(--sans);color:var(--muted)}.cont .cn{font:500 var(--t-sm) var(--serif);font-variant-caps:all-small-caps;letter-spacing:.12em;color:var(--rubric);margin-top:var(--s-2)}
.cont .ct{font:600 var(--t-xl)/1.2 var(--display)}.cont .cf{font-style:italic;color:var(--ink2);margin-top:var(--s-2);font-size:var(--t-md)}.cont:hover .ct{color:var(--rubric);text-decoration:underline}
.fin{font:italic 600 var(--t-2xl) var(--display)}
.colo{max-width:30em;margin:var(--s-7) auto 0;text-align:center;font-size:var(--t-sm);line-height:1.6}.colo h2{font:500 var(--t-lg) var(--serif);font-variant-caps:all-small-caps;letter-spacing:.14em;margin-bottom:var(--s-4)}
.colo p{margin:0 0 var(--s-3)}.colo b{font-weight:600}.colo .back{margin-top:var(--s-5)}
'''
    return body,css
def reading_v4(d):
    o,ch,text,end9,excerpt=reading_parts(d)
    nums=''.join('<div class="pp" id="p'+str(i+1)+'"><a class="pn" href="#p'+str(i+1)+'" aria-label="Paragraph '+str(i+1)+'">'+str(i+1)+'</a><p>'+p+'</p></div>' for i,p in enumerate(o['ch2']))
    n9=o['ch2_total']
    e=o['ed'];w=o['work']
    cite=E(o['author'].split()[-1])+', '+E(' '.join(o['author'].split()[:-1])).rstrip('.')+'. <cite>'+E(w['title'])+'</cite>. '+E(w.get('date',''))+'. '+E(e['label'])+'. Bibliotheca Catholica, https://bibliothecacatholica.com/work/orthodoxy/.'
    dl=''.join('<tr><th scope="row">'+k+'</th><td>'+v+'</td></tr>' for k,v in colophon_facts(d))
    body=('<div class="rh"><a href="/work/orthodoxy/">Orthodoxy</a><span>Chapter II · The Maniac</span><span class="kb">Keys: <kbd>←</kbd> <kbd>→</kbd> chapters</span></div>'
     '<article class="col app">'+opener('II','The Maniac')+nums+excerpt
     +'<div class="end"><p class="orn" aria-hidden="true">❦</p><p class="e">End of Chapter II</p></div></article>'
     +'<nav class="pager" aria-label="Chapters"><a rel="prev" href="'+ch[0][0]+'"><span>← Previous chapter</span>'+E(ch[0][1])+'</a><a rel="next" href="'+ch[2][0]+'"><span>Next chapter →</span>'+E(ch[2][1])+'</a></nav>'
     +'<p class="divider">Below: how the last chapter ends, with the colophon</p>'
     +'<article class="col" aria-label="End of the book">'+end9+'<div class="end"><p class="orn" aria-hidden="true">❦</p><p class="e">End of Chapter IX · End of the book</p></div></article>'
     +'<section class="colo" aria-labelledby="co-h"><h2 id="co-h">Edition record</h2><table>'+dl+'</table>'
     +'<h3>Cite this edition</h3><p class="cite">'+cite+'</p></section>'
     +'<p class="pgn">'+d['PG_LINE']+'</p>'+edition_details(d))
    js=('<script>document.addEventListener("keydown",function(e){if(e.altKey||e.ctrlKey||e.metaKey||/input|textarea|select/i.test(e.target.tagName))return;'
        'var r=e.key==="ArrowLeft"?"prev":e.key==="ArrowRight"?"next":"";if(!r)return;var a=document.querySelector(\'.pager a[rel="\'+r+\'"]\');if(a)location.href=a.href});</script>\n')
    css=READ_CSS+'''.rh{max-width:44rem;margin:var(--s-4) auto 0;padding:0 var(--s-4);display:flex;flex-wrap:wrap;gap:var(--s-2) var(--s-4);font:var(--t-xs)/1.4 var(--sans);color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:var(--s-2)}
.rh a{font-weight:600}.rh .kb{margin-left:auto}kbd{font:11px var(--sans);border:1px solid var(--rule);border-radius:3px;padding:0 4px}
.app .pp{position:relative}.app .pp p{text-indent:1.5em}.app .pp:first-of-type p{text-indent:0}
.app .pp:first-of-type p::first-letter{float:left;font:600 3.1em/.82 var(--display);color:var(--rubric);margin:.06em .08em 0 0}
.app .op+.pp p{text-indent:0}
.pn{position:absolute;left:-3.2em;top:.35em;width:2.4em;text-align:right;font:12px/1 var(--sans);color:var(--muted);text-decoration:none;font-variant-numeric:lining-nums}
.pn:hover,.pp:target .pn{color:var(--rubric)}.pp:target{background:color-mix(in srgb,var(--gold) 10%,transparent)}
.pager{max-width:26em;margin:var(--s-6) auto 0;display:grid;grid-template-columns:1fr 1fr;gap:var(--s-4);font:var(--t-sm)/1.3 var(--serif)}
.pager a{display:flex;flex-direction:column;gap:2px;text-decoration:none;padding:var(--s-3) 0;border-top:2px solid var(--line);min-height:44px}.pager a:hover{border-top-color:var(--rubric)}
.pager a:last-child{text-align:right}.pager span{font:500 12px var(--sans);color:var(--muted)}
.colo{max-width:34em;margin:var(--s-7) auto 0;font-size:var(--t-sm)}.colo h2{font-size:var(--t-xl);margin-bottom:var(--s-3)}.colo h3{font-size:var(--t-lg);margin:var(--s-5) 0 var(--s-2)}
.colo table{border-collapse:collapse;width:100%}.colo th{text-align:left;vertical-align:top;font:500 12px/2 var(--sans);color:var(--muted);padding:var(--s-2) var(--s-3) var(--s-2) 0;white-space:nowrap;width:1%}
.colo td{padding:var(--s-2) 0;border-top:1px solid var(--line);line-height:1.5}.colo th{border-top:1px solid var(--line)}
.cite{padding:var(--s-3) var(--s-4);background:var(--bg2);margin:0;line-height:1.5;overflow-wrap:anywhere}
@media(max-width:700px){.app{padding-left:calc(var(--s-4) + 1.6em)!important}.pn{left:-1.9em;width:1.5em}.rh .kb{display:none}.colo th{white-space:normal}}
'''
    return body,css,js

# ---------------------------------------------------------------- d. sources and credits (the /licensing/ text, unchanged)
SRC_CSS='''.head{margin:var(--s-7) 0 var(--s-5);max-width:66ch}.head h1{font-size:var(--t-3xl)}.lede{font-size:var(--t-md);color:var(--ink2);margin:var(--s-3) 0 0}
.prose{max-width:66ch}.prose p,.prose li{line-height:1.6}.prose h2{font-size:var(--t-xl);margin:var(--s-6) 0 var(--s-3)}
code{font:.82em/1 ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--bg2);padding:1px 4px;border-radius:3px;overflow-wrap:anywhere}
.tail{font:var(--t-xs)/1.5 var(--sans);color:var(--muted);margin-top:var(--s-6)}
'''
def src_head(d):return '<div class="head"><p class="label">Rights &amp; Permissions</p><h1>'+d['lic_h1']+'</h1><p class="lede">'+d['lic_lede']+'</p></div>'
def ledger(d):
    return '<dl class="ledger">'+''.join('<div><dt>'+r[0]+'</dt><dd class="terms">'+r[2]+'</dd><dd class="where">'+r[1]+'</dd></div>' for r in d['lic_rows'])+'</dl>'
LEDGER_CSS='''.ledger{margin:0;border-top:2px solid var(--ink)}.ledger div{display:grid;grid-template-columns:11em minmax(0,1fr);gap:0 var(--s-5);padding:var(--s-3) 0;border-bottom:1px solid var(--line)}
.ledger dt{font:600 var(--t-md)/1.3 var(--serif);grid-row:span 2}.ledger dd{margin:0}.ledger .terms{font-size:var(--t-md)}.ledger .where{font-size:var(--t-xs);color:var(--muted);margin-top:2px}
@media(max-width:600px){.ledger div{grid-template-columns:1fr}.ledger dt{grid-row:auto}}
'''
def sources_v1(d):
    secs=''.join('<section><h2>'+t+'</h2>'+c+'</section>' for t,c in d['lic_secs'])
    body='<div class="wrap"><div class="prose">'+src_head(d)+'<h2 class="sum">In brief</h2>'+ledger(d)+secs+'<p class="tail">'+re.sub(r'^<p class="small">|</p>$','',d['lic_tail'])+'</p></div></div>'
    return body,SRC_CSS+LEDGER_CSS+'.sum{font:500 var(--t-md) var(--serif)!important;font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink);margin-bottom:var(--s-2)!important}\n'
def sources_v2(d):
    ids=['s'+str(i+1) for i in range(len(d['lic_secs']))]
    rail='<li><a href="#sum">Summary</a></li>'+''.join('<li><a href="#'+i+'">'+t+'</a></li>' for i,(t,c) in zip(ids,d['lic_secs']))+'<li><a href="/rights/">Rights &amp; Permissions</a></li><li><a href="/takedown/">Takedown requests</a></li>'
    secs=''.join('<section id="'+i+'" aria-labelledby="'+i+'-h"><h2 id="'+i+'-h">'+t+'</h2>'+c+'</section>' for i,(t,c) in zip(ids,d['lic_secs']))
    body=('<div class="wrap">'+src_head(d)+'<div class="lay"><nav class="rail" aria-label="On this page"><p class="label">On this page</p><ol>'+rail+'</ol></nav>'
          '<div class="prose"><section id="sum" aria-labelledby="sum-h"><h2 id="sum-h">Summary</h2>'+d['lic_table']+'</section>'+secs+d['lic_tail']+'</div></div></div>')
    css=SRC_CSS+'''.lay{display:grid;grid-template-columns:220px minmax(0,1fr);gap:var(--s-7);align-items:start}.lay>*{min-width:0}
.rail{position:sticky;top:var(--s-4)}.rail ol{list-style:none;margin:var(--s-2) 0 0;padding:0;border-left:1px solid var(--line)}
.rail a{display:block;padding:var(--s-1) var(--s-3);font-size:var(--t-sm);line-height:1.3;text-decoration:none;color:var(--ink2);border-left:2px solid transparent;margin-left:-1px}
.rail a:hover{color:var(--rubric);border-left-color:var(--rubric)}
.prose{max-width:none}.prose>section{max-width:66ch}.prose>section#sum{max-width:none}section{scroll-margin-top:var(--s-4)}
.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:var(--t-sm)}th{text-align:left;font:500 var(--t-xs) var(--sans);color:var(--muted);border-bottom:2px solid var(--ink);padding:var(--s-2) var(--s-3) var(--s-2) 0}
td{vertical-align:top;border-bottom:1px solid var(--line);padding:var(--s-2) var(--s-3) var(--s-2) 0;line-height:1.45}td:first-child{font-weight:600;white-space:nowrap}
.tail,.prose>p.small{font:var(--t-xs)/1.5 var(--sans);color:var(--muted);margin-top:var(--s-6)}
@media(max-width:820px){.lay{grid-template-columns:1fr;gap:var(--s-4)}.rail{position:static}.rail ol{columns:2}}
'''
    return body,css
HOSTS={'www.gutenberg.org':'Project Gutenberg','archive.org':'Internet Archive','gutenberg.net.au':'Project Gutenberg Australia','www.fadedpage.com':'Faded Page','www.ccel.org':'Christian Classics Ethereal Library','standardebooks.org':'Standard Ebooks'}
def sources_v3(d):
    rows=''.join('<li><a href="https://'+E(h)+'/" target="_blank" rel="noopener">'+E(HOSTS.get(h,h))+'</a><span class="n">'+str(n)+' '+('edition' if n==1 else 'editions')+'</span></li>' for h,n in d['src_counts'])
    secs=''.join('<section><h3>'+t+'</h3>'+c+'</section>' for t,c in d['lic_secs'])
    body=('<div class="wrap"><div class="prose">'+src_head(d)+
     '<section aria-labelledby="t-h"><h2 id="t-h">Terms at a glance</h2>'+ledger(d)+'</section>'
     '<section aria-labelledby="h-h"><h2 id="h-h">Where the hosted texts come from</h2><p>Each hosted edition records its own source, rights basis, and checked date on its work page. Counts of hosted editions by the site each source record names:</p><ul class="srcs">'+rows+'</ul></section>'
     '<section aria-labelledby="i-h"><h2 id="i-h">Images</h2><ul class="srcs"><li><span>Home engraving: '+d['hero_cap']+'</span></li>'
     '<li><span>Author portraits: '+str(d['portraits_n'])+' self-hosted public-domain images, each with its file page, licence, and artist kept in <code>data/portraits.json</code>.</span></li></ul></section>'
     '<section aria-labelledby="f-h"><h2 id="f-h">The full licensing note</h2><details open><summary>Licensing (draft), sections 1 to 5</summary>'+secs+'</details></section>'
     '<p class="tail">'+re.sub(r'^<p class="small">|</p>$','',d['lic_tail'])+'</p></div></div>')
    css=SRC_CSS+LEDGER_CSS+'''.srcs{list-style:none;margin:0;padding:0}.srcs li{display:flex;justify-content:space-between;gap:var(--s-4);padding:var(--s-2) 0;border-bottom:1px solid var(--line)}
.srcs .n{color:var(--muted);font-size:var(--t-sm);white-space:nowrap;font-variant-numeric:lining-nums}
details summary{cursor:pointer;font:500 var(--t-sm) var(--sans);color:var(--rubric);min-height:32px}details h3{font-size:var(--t-lg);margin:var(--s-5) 0 var(--s-2)}
'''
    return body,css
def sources_v4(d):
    secs=''
    for t,c in d['lic_secs']:
        m=re.match(r'(\d+)\. (.*)',t)
        n,tt=(m.group(1),m.group(2)) if m else ('',t)
        secs+='<section class="ns"><h2><span class="hn" aria-hidden="true">'+n+'</span><span class="vh">'+n+'. </span>'+tt+'</h2>'+c+'</section>'
    body=('<div class="wrap"><article class="doc">'+src_head(d).replace('<p class="lede">','<p class="lede">')+'<div class="tbl">'+d['lic_table']+'</div>'+secs
          +'<footer class="docfoot"><p class="orn" aria-hidden="true">❦</p>'+d['lic_tail']+'</footer></article></div>')
    css=SRC_CSS+'''.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.doc{max-width:66ch;margin:0 auto}.doc .head{text-align:center;margin-left:auto;margin-right:auto}.doc .head .label{text-align:center}
.doc p,.doc li{line-height:1.65}.ns{position:relative}.ns h2{font-size:var(--t-xl);margin:var(--s-7) 0 var(--s-3)}
.hn{position:absolute;left:-2.4em;width:1.8em;text-align:right;color:var(--gold-ink);font-weight:500}
table{border-collapse:collapse;width:100%;font-size:var(--t-sm);margin:var(--s-5) 0}th{text-align:left;font:500 var(--t-sm) var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink);border-bottom:1px solid var(--ink);padding:var(--s-1) var(--s-3) var(--s-1) 0}
td{vertical-align:top;border-bottom:1px solid var(--line);padding:var(--s-2) var(--s-3) var(--s-2) 0;line-height:1.45}
.docfoot{text-align:center;margin-top:var(--s-7);font:var(--t-xs)/1.5 var(--sans);color:var(--muted)}.orn{color:var(--gold);font-size:var(--t-lg)}
@media(max-width:820px){.hn{position:static;width:auto;margin-right:.3em}.hn+.vh{display:none}}
@media(max-width:600px){thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}table,tbody,tr,td{display:block}tr{border-bottom:1px solid var(--line);padding:var(--s-2) 0}
td{border:0;padding:2px 0}td::before{content:attr(data-label);display:block;font:500 12px var(--sans);color:var(--muted)}}
'''
    return body,css

# ---------------------------------------------------------------- e. navigation and footer
def nav_sample(d):
    rows=''.join('<li><a href="/work/'+E(w['id'])+'/">'+E(w['title'])+'</a> <span class="muted">'+E(w['author'])+'</span></li>' for w in d['recent'])
    return ('<div class="wrap sample"><p class="label">Discover &amp; Read</p><h1>The reading room</h1><p class="lede">'+LIB_INTRO+'</p>'
            '<h2>Recently added</h2><ul class="rows">'+rows+'</ul></div>')
NAV_CSS='''.sample{padding-top:var(--s-6)}.sample h1{font-size:var(--t-3xl)}.sample h2{font-size:var(--t-xl);margin:var(--s-6) 0 var(--s-3)}.lede{color:var(--ink2);max-width:66ch}
.brand{display:inline-flex;align-items:center;gap:var(--s-2);color:var(--ink);text-decoration:none}.brand-mark{width:32px;height:32px;color:var(--rubric);flex:none}
.brand .nm{font:600 var(--t-xl)/1 var(--display)}.brand .sub{display:block;font:500 var(--t-xs)/1.2 var(--serif);font-variant-caps:all-small-caps;letter-spacing:.08em;color:var(--gold-ink);margin-top:2px}
.mmenu{display:none}.mmenu summary{cursor:pointer;list-style:none;font:500 var(--t-sm) var(--sans);min-height:44px;display:flex;align-items:center;gap:var(--s-2);color:var(--ink)}
.mmenu summary::-webkit-details-marker{display:none}.mmenu ul{list-style:none;margin:0;padding:0}.mmenu li a{display:flex;align-items:center;min-height:48px;border-top:1px solid var(--line);text-decoration:none;color:var(--ink);font-size:var(--t-md)}
.mmenu a[aria-current]{color:var(--rubric);font-weight:600}.mmenu li a{padding:var(--s-2) 0;line-height:1.3}.mmenu .small{font-weight:400}
.sf{display:flex}.sf input{font:var(--t-xs) var(--sans);color:var(--ink);background:var(--card);border:1px solid var(--rule);border-radius:6px 0 0 6px;min-height:36px;padding:0 var(--s-3);width:220px}
.sf button{font:500 var(--t-xs) var(--sans);border:1px solid var(--rubric);background:transparent;color:var(--rubric);border-radius:0 6px 6px 0;padding:0 var(--s-3);cursor:pointer}
.ft{margin-top:var(--s-8);background:var(--bg2);color:var(--ink2);font-size:var(--t-sm)}.ft a{color:var(--ink2)}.ft a:hover{color:var(--rubric)}
.ft h2{font:500 var(--t-sm)/1.3 var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink);margin:0 0 var(--s-2)}
.ft ul{list-style:none;margin:0;padding:0}.ft li a{display:inline-flex;align-items:center;min-height:28px;text-decoration:none}.ft li a:hover{text-decoration:underline}
.credit{font:var(--t-xs)/1.6 var(--sans);color:var(--muted);border-top:1px solid var(--line);padding-top:var(--s-4);margin-top:var(--s-6)}.credit a{color:var(--muted)}
.ft details summary{cursor:pointer;font:var(--t-xs) var(--sans);min-height:28px}.ft details p{font:var(--t-xs)/1.6 var(--sans)}
.nl{font-size:var(--t-sm)}
@media(max-width:820px){.dnav{display:none!important}.mmenu{display:block}}
'''
def navlinks(d,cls=''):  # Support has its own header link on wide screens, as on the live site (nav-m is phone-only)
    return ''.join('<li><a href="'+E(h)+'"'+(' aria-current="page"' if h=='/library/' else '')+'>'+E(t)+'</a></li>' for h,t in d['nav'] if h!='/support/')
def mobile_menu(d,desc=False):
    descs={h:t for h,_,t in d['SECTION_LINKS']}
    items=''.join('<li><a href="'+E(h)+'"'+(' aria-current="page"' if h=='/library/' else '')+'>'+(('<span><b>'+E(t)+'</b><br><span class="muted small">'+E(descs.get(h,''))+'</span></span>') if desc and descs.get(h) else E(t))+'</a></li>' for h,t in d['nav'])
    return '<details class="mmenu"><summary><span aria-hidden="true">☰</span> Menu</summary><ul>'+items+'<li><a href="/search/">Search</a></li></ul></details>'
def search_form(fid):return '<form class="sf" role="search" action="/search/" method="get"><label class="vh" for="'+fid+'">Search everything</label><input id="'+fid+'" name="lookup" type="search" placeholder="Search people, titles, and sources"><button type="submit">Search</button></form>'
VH='.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}\n'
def about_block(d):
    return ('<p class="nl">'+d['nl_line']+' <a href="https://bibliothecacatholica.substack.com/subscribe" target="_blank" rel="noopener">Subscribe to the newsletter ↗</a></p>'
            '<details><summary>About this independent project</summary><p>'+d['non_affiliation']+'</p><p>'+d['social']+'</p></details>')
def link_list(pairs):return '<ul>'+''.join('<li><a href="'+E(h)+'"'+(' target="_blank" rel="noopener"' if h.startswith('http') else '')+'>'+E(t)+'</a></li>' for h,t in pairs)+'</ul>'
def nav_v1(d):
    hdr=('<header class="mh"><div class="wrap top"><span></span><a class="brand mast" href="/">'+d['mark']+'<span><span class="nm">Bibliotheca Catholica</span><span class="sub">a library of libraries</span></span></a>'
         '<div class="tools"><a href="/search/">Search</a><a href="/support/">Support</a></div></div>'
         '<nav class="dnav" aria-label="Sections"><ul>'+navlinks(d)+'</ul></nav><div class="wrap">'+mobile_menu(d)+'</div></header>\n')
    ft=('<footer class="footer"><div class="ft"><div class="wrap fw"><div class="g"><div><p class="ftn">Bibliotheca Catholica</p><p>A free Catholic reading room and library of libraries.</p>'+about_block(d)+'</div>'
        '<nav aria-label="Read and explore"><h2>Read &amp; explore</h2>'+link_list(d['footer_read'])+'</nav><nav aria-label="The project and policies"><h2>The project</h2>'+link_list(d['footer_project'])+'</nav></div>'
        '<p class="credit">'+d['footer_credit']+'</p></div></div></footer>\n')
    css=NAV_CSS+VH+'''.mh{border-bottom:1px solid var(--line)}.top{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding-top:var(--s-5);padding-bottom:var(--s-3)}
.mast{flex-direction:column;text-align:center;gap:var(--s-1)}.mast .brand-mark{width:40px;height:40px}.mast .nm{font-size:var(--t-2xl)}
.tools{justify-self:end;display:flex;gap:var(--s-4);font:500 var(--t-xs) var(--sans)}.tools a{min-height:32px;display:inline-flex;align-items:center}
.dnav ul{list-style:none;margin:0;padding:var(--s-1) 0;display:flex;justify-content:center;flex-wrap:wrap;gap:0 var(--s-5);border-top:1px solid var(--line)}
.dnav a{display:inline-flex;align-items:center;min-height:40px;font:500 var(--t-md)/1 var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--ink2);text-decoration:none;border-bottom:2px solid transparent}
.dnav a:hover{color:var(--rubric)}.dnav a[aria-current]{color:var(--rubric);border-bottom-color:var(--rubric)}
.fw{padding-top:var(--s-7);padding-bottom:var(--s-5)}.g{display:grid;grid-template-columns:2fr 1fr 1fr;gap:var(--s-7)}.ftn{font:600 var(--t-xl) var(--display);color:var(--ink);margin:0 0 var(--s-2)}
@media(max-width:820px){.top{grid-template-columns:1fr auto;padding-top:var(--s-3)}.top>span:first-child{display:none}.mast{flex-direction:row;text-align:left}.mast .nm{font-size:var(--t-lg)}.mast .sub{display:none}.mast .brand-mark{width:28px;height:28px}.g{grid-template-columns:1fr 1fr}.g>div:first-child{grid-column:1/-1}}
'''
    return nav_sample(d),css,hdr,ft
def nav_v2(d):
    hdr=('<header class="qb"><div class="wrap row"><a class="brand" href="/">'+d['mark']+'<span class="nm">Bibliotheca Catholica</span></a>'
         '<nav class="dnav" aria-label="Sections"><ul>'+navlinks(d)+'</ul></nav><div class="dnav">'+search_form('hq')+'</div><a class="dnav sup" href="/support/">Support</a></div><div class="wrap">'+mobile_menu(d)+'</div></header>\n')
    ft=('<footer class="footer"><div class="ft colo"><div class="wrap"><p class="orn" aria-hidden="true">❦</p><p class="ftn">Bibliotheca Catholica</p><p>A free Catholic reading room and library of libraries.</p>'
        '<div class="cols"><nav aria-label="Read and explore"><h2>Read &amp; explore</h2>'+link_list(d['footer_read'])+'</nav><nav aria-label="The project and policies"><h2>The project</h2>'+link_list(d['footer_project'])+'</nav></div>'
        +about_block(d)+'<p class="credit">'+d['footer_credit']+'</p></div></div></footer>\n')
    css=NAV_CSS+VH+'''.qb{border-bottom:1px solid var(--line)}.row{display:flex;align-items:center;gap:var(--s-5);min-height:64px}.qb .nm{font-size:var(--t-lg)}
.qb .dnav ul{list-style:none;margin:0;padding:0;display:flex;gap:var(--s-4);font:500 var(--t-xs)/1 var(--sans)}
.qb .dnav ul a{display:inline-flex;align-items:center;min-height:64px;color:var(--ink2);text-decoration:none;border-bottom:2px solid transparent;margin-bottom:-1px}
.qb .dnav ul a:hover{color:var(--rubric)}.qb .dnav ul a[aria-current]{color:var(--ink);border-bottom-color:var(--rubric)}
.qb .sf{margin-left:auto}.qb .sf input{width:180px}.sup{font:500 var(--t-xs) var(--sans)}
@media(max-width:1180px){.qb .sf input{width:120px}.qb .dnav ul{gap:var(--s-3)}}
.colo{text-align:center}.colo .wrap{padding-top:var(--s-7);padding-bottom:var(--s-5);max-width:52rem}.orn{color:var(--gold);font-size:var(--t-xl);margin:0}.ftn{font:600 var(--t-xl) var(--display);color:var(--ink);margin:var(--s-2) 0}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:var(--s-6);text-align:left;margin:var(--s-6) 0;padding:var(--s-5) 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.cols ul{columns:2;column-gap:var(--s-5)}.colo details{text-align:left;max-width:40rem;margin:0 auto}
@media(max-width:820px){.cols{grid-template-columns:1fr}.cols ul{columns:2}}
'''
    return nav_sample(d),css,hdr,ft
def nav_v3(d):
    sub=[('/library/','The shelves'),('/reading/','Reading Lists'),('/editions/','Editions & Translations'),('/guides/epub-on-your-device/','Read an EPUB on your device'),('/isidore/','Isidore Index')]
    hdr=('<header class="tt"><div class="wrap row"><a class="brand" href="/">'+d['mark']+'<span><span class="nm">Bibliotheca Catholica</span><span class="sub">a library of libraries</span></span></a><div class="dnav">'+search_form('hq')+'</div><a class="dnav sup" href="/support/">Support</a></div>'
         '<nav class="dnav pri" aria-label="Sections"><div class="wrap"><ul>'+navlinks(d)+'</ul></div></nav>'
         '<nav class="sec" aria-label="In the Reading Room"><div class="wrap"><span class="here">Reading Room</span><ul>'+''.join('<li><a href="'+h+'"'+(' aria-current="page"' if i==0 else '')+'>'+E(t)+'</a></li>' for i,(h,t) in enumerate(sub))+'</ul></div></nav>'
         '<div class="wrap">'+mobile_menu(d)+'</div></header>\n')
    lab=dict(d['footer_read'])
    groups=[('Read',['/library/','/reading/','/reading/advent-2026/','/editions/','/guides/epub-on-your-device/','/study/']),
            ('Explore',['/timeline/','/scripture/','/doctors/','/rites/']),
            ('Elsewhere',['/isidore/','/references/','/libraries/','/media/','/rare/','/substacks/','/projects/'])]
    cols=''.join('<nav aria-label="'+g+'"><h2>'+g+'</h2>'+link_list([(h,lab[h]) for h in hs if h in lab])+'</nav>' for g,hs in groups)
    ft=('<footer class="footer"><div class="ft"><div class="wrap fw"><div class="g4">'+cols+'<nav aria-label="The project and policies"><h2>The project</h2>'+link_list(d['footer_project'])+'</nav></div>'
        '<div class="ab"><p class="ftn">Bibliotheca Catholica</p><p>A free Catholic reading room and library of libraries.</p>'+about_block(d)+'</div><p class="credit">'+d['footer_credit']+'</p></div></div></footer>\n')
    css=NAV_CSS+VH+'''.row{display:flex;align-items:center;gap:var(--s-5);padding-top:var(--s-4);padding-bottom:var(--s-3)}.row .dnav:first-of-type{margin-left:auto}.sup{font:500 var(--t-xs) var(--sans)}
.pri ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:0 var(--s-5);font:500 var(--t-sm)/1 var(--sans)}.pri a{display:inline-flex;align-items:center;min-height:44px;color:var(--ink2);text-decoration:none;border-bottom:2px solid transparent}
.pri a:hover{color:var(--rubric)}.pri a[aria-current]{color:var(--ink);border-bottom-color:var(--rubric)}.pri{border-bottom:1px solid var(--line)}
.sec{background:var(--bg2);border-bottom:1px solid var(--line)}.sec .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:0 var(--s-4)}
.sec .here{font:500 var(--t-sm)/1.3 var(--serif);font-variant-caps:all-small-caps;letter-spacing:.06em;color:var(--gold-ink)}
.sec ul{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:0 var(--s-4);font:var(--t-sm)/1 var(--serif)}.sec a{display:inline-flex;align-items:center;min-height:40px;color:var(--ink2)}.sec a[aria-current]{color:var(--rubric);font-weight:600}
.fw{padding-top:var(--s-7);padding-bottom:var(--s-5)}.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s-6)}
.ab{margin-top:var(--s-6);padding-top:var(--s-5);border-top:1px solid var(--line);max-width:44rem}.ftn{font:600 var(--t-lg) var(--display);color:var(--ink);margin:0}
@media(max-width:820px){.g4{grid-template-columns:1fr 1fr}.sec .wrap{overflow-x:auto;flex-wrap:nowrap}.sec ul{flex-wrap:nowrap;white-space:nowrap}}
'''
    return nav_sample(d),css,hdr,ft
def nav_v4(d):
    hdr=('<header class="qb"><div class="wrap row"><a class="brand" href="/">'+d['mark']+'<span class="nm">Bibliotheca Catholica</span></a>'
         '<nav class="dnav" aria-label="Sections"><ul>'+navlinks(d)+'</ul></nav><a class="dnav sup" href="/search/">Search</a><a class="dnav sup" href="/support/">Support</a></div><div class="wrap">'+mobile_menu(d,desc=True)+'</div></header>\n')
    dirlist=''.join('<li><a href="'+E(h)+'">'+E(l)+'</a><span>'+E(t)+'</span></li>' for h,l,t in d['SECTION_LINKS'])
    ft=('<footer class="footer"><div class="ft"><div class="wrap fw"><h2 class="dh">The library directory</h2><ul class="dir">'+dirlist+'</ul>'
        '<div class="proj"><nav aria-label="The project and policies"><h2>The project</h2><ul class="inl">'+''.join('<li><a href="'+E(h)+'"'+(' target="_blank" rel="noopener"' if h.startswith('http') else '')+'>'+E(t)+'</a></li>' for h,t in d['footer_project'])+'</ul></nav>'
        '<div>'+about_block(d)+'</div></div><p class="credit">'+d['footer_credit']+'</p></div></div></footer>\n')
    css=NAV_CSS+VH+'''.qb{border-bottom:1px solid var(--line)}.row{display:flex;align-items:center;gap:var(--s-5);min-height:64px}.qb .nm{font-size:var(--t-lg)}
.qb .dnav ul{list-style:none;margin:0 0 0 auto;padding:0;display:flex;gap:var(--s-4);font:var(--t-sm)/1 var(--serif)}
.qb .dnav ul a{display:inline-flex;align-items:center;min-height:44px;color:var(--ink2);text-decoration:none}.qb .dnav ul a:hover{color:var(--rubric);text-decoration:underline}
.qb .dnav ul a[aria-current]{color:var(--rubric);text-decoration:underline;text-decoration-thickness:2px}.sup{font:500 var(--t-xs) var(--sans)}nav.dnav{margin-left:auto}
.fw{padding-top:var(--s-7);padding-bottom:var(--s-5)}.dh{font:600 var(--t-xl) var(--display)!important;font-variant-caps:normal!important;letter-spacing:0!important;color:var(--ink)!important;margin-bottom:var(--s-4)!important}
.dir{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s-1) var(--s-6)}.dir li{padding:var(--s-2) 0;border-top:1px solid var(--line);line-height:1.35}.dir a{font-weight:600;min-height:0!important}.dir span{display:block;font-size:var(--t-xs);color:var(--muted)}
.proj{display:grid;grid-template-columns:1fr 1fr;gap:var(--s-6);margin-top:var(--s-6)}.inl{display:flex;flex-wrap:wrap;gap:0 var(--s-4)}
@media(max-width:820px){.dir{grid-template-columns:1fr 1fr}.proj{grid-template-columns:1fr}}@media(max-width:520px){.dir{grid-template-columns:1fr}}
'''
    return nav_sample(d),css,hdr,ft

# ---------------------------------------------------------------- variations and build
VARIANTS={
 'home':[('v1','Title page','A centered book title page: label, Tolle Lege, ornament, one button, then the engraving as a frontispiece and Start here as a numbered contents list.'),
         ('v2','Facing pages','An open-book spread: the engraving on the left, the title and a sentence about the library on the right, then Start here as rows with covers and descriptions.'),
         ('v3','Editor’s shelf','Type only above the fold, with a facts line of counts; Start here becomes an annotated reading list; the engraving moves beside About as a small vignette.'),
         ('v4','Saints first','A quiet banner with the engraving, then the eight portraits as the main gallery, each with the book to begin with.')],
 'library':[('v1','Faceted catalogue','A sticky facet column (subject or era, with counts) beside rows with small covers or portraits; the result count updates as you filter.'),
            ('v2','Printed shelf list','Dense two-column lists grouped by subject or era, with a jump line and one plain filter bar; no descriptions, no images.'),
            ('v3','Cover shelf','The design C covers as a wall of books, with subject tabs as underlined text; authors as a portrait index.'),
            ('v4','Index and chronology','Works A to Z with a sticky letter bar; authors in a chronology with an era rail and dates in a hanging column.')],
 'reading':[('v1','Running head','A slim sticky running head with the book, the chapter, a Contents menu, and arrows; a three-part pager; a centered colophon after “The End”.'),
            ('v2','Margin contents','The contents in a sticky left margin with the current chapter marked; it folds into a disclosure on phones; the colophon is a ruled list.'),
            ('v3','Chapter strip','A strip of chapter numerals under the opener; at the end, a Continue reading block with the next chapter’s first sentence; a book-style colophon.'),
            ('v4','Scholarly apparatus','Paragraph numbers in the margin for citing, arrow-key chapter paging, an edition record table, and a Cite this edition line.')],
 'sources':[('v1','Copyright-page ledger','One column at reading measure; the summary table becomes a ledger of material, terms, and where; sections follow as plain prose.'),
            ('v2','Contents rail','A sticky On this page list beside the text, including Rights and Takedown links; the summary stays a table, without the panel border.'),
            ('v3','Credits by source','The terms ledger, then where the hosted texts come from (counts by source), then images, with the full note in an open disclosure.'),
            ('v4','Printed note','A centered document with section numbers hung in the margin; the table stacks into labelled rows on phones.')],
 'nav':[('v1','Masthead','A centered wordmark with the sections in serif small capitals on a ruled line below; a three-column footer.'),
        ('v2','Quiet bar','One compact row: brand, sections, search, Support; the current section is underlined, not filled; a centered colophon footer.'),
        ('v3','Two tiers','The seven sections plus a tinted row of links within the current section; the footer groups its seventeen links into Read, Explore, and Elsewhere.'),
        ('v4','Library directory','A quiet bar in serif type; on phones the menu lists each section with its one-line description; the footer becomes a directory of every section.')],
}
FUNCS={'home':[home_v1,home_v2,home_v3,home_v4],'library':[library_v1,library_v2,library_v3,library_v4],'reading':[reading_v1,reading_v2,reading_v3,reading_v4],
       'sources':[sources_v1,sources_v2,sources_v3,sources_v4],'nav':[nav_v1,nav_v2,nav_v3,nav_v4]}

def index_page(d):
    secs=''.join('<section aria-labelledby="a-'+a+'"><h2 id="a-'+a+'">'+E(t)+'</h2><ol class="rows">'+''.join('<li><a href="/design-preview/'+a+'/'+k+'/">'+k+': '+E(n)+'</a><p>'+E(i)+'</p></li>' for k,n,i in VARIANTS[a])+'</ol></section>' for a,t in AREAS)
    body=('<div class="wrap ix"><p class="label">Design refresh, November 2026</p><h1>Design previews</h1>'
          '<p>Four variations for each of five areas, built from the site’s own content and tokens. These pages are unlisted and not indexed; nothing here changes the live pages. '
          'The reasoning for each variation and a recommendation per area are in <a href="'+DOC+'" target="_blank" rel="noopener">design-directions-2026-11.md</a>.</p>'+secs+'</div>')
    css='.ix{max-width:46rem;padding-top:var(--s-6)}.ix h1{font-size:var(--t-3xl);margin:var(--s-2) 0 var(--s-4)}.ix h2{font-size:var(--t-xl);margin:var(--s-6) 0 var(--s-2)}.ix li a{font-weight:600}.ix li p{margin:var(--s-1) 0 0;font-size:var(--t-sm);color:var(--ink2)}\n'
    bar='<div class="pv-bar" role="region" aria-label="Design preview"><div class="wrap"><b>Design preview, not a live page</b><button type="button" id="pv-theme" aria-pressed="false">Dark theme</button></div></div>\n'
    return ('<!doctype html>\n<html lang="en" data-theme="light">\n<head>\n'+ga_tag()+'<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>Design previews · Bibliotheca Catholica</title>\n<meta name="robots" content="noindex,nofollow">\n<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">\n<link rel="stylesheet" href="/styles/fonts.css">\n'
            '<style>'+BASE_CSS+css+'</style>\n'+THEME_INIT+'</head>\n<body>\n<a class="skip" href="#main">Skip to content</a>\n'+bar+plain_header(d)+'<main id="main" tabindex="-1">\n'+body+'\n</main>\n'+plain_footer(d)+THEME_TOGGLE+'</body>\n</html>\n')

def build():
    d=load()
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT/'index.html').write_text(index_page(d),encoding='utf-8')
    n=1
    for area,_ in AREAS:
        for (v,name,idea),fn in zip(VARIANTS[area],FUNCS[area]):
            r=fn(d)
            body,css=r[0],r[1]
            if area=='nav':html_=page(d,area,v,name,idea,body,css,header=r[2],footer=r[3])
            else:html_=page(d,area,v,name,idea,body,css,script=r[2] if len(r)>2 else '')
            f=OUT/area/v/'index.html';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(html_,encoding='utf-8');n+=1
    print(n,'design preview pages')

if __name__=='__main__':build()
