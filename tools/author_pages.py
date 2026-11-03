"""Phase A item 2 (2026-11-03): static pages for the authors with no hosted work in the reading room.

Each such page gets, from data already in the repo (nothing invented, nothing hosted):
  - a short intro: the hand-written `intro` on the hub record (Trent Horn, Thomas E. Woods, Warren H. Carroll,
    Scott Hahn; sources in docs/AUTHOR-PAGES.md), else `intro()` below, a neutral sentence built from fields.
    app.js `auIntro()` builds the same text in the browser (tests/author_pages.test.js compares them);
  - their reading-room works (link only) and their Isidore Index books, each with its rights badge and a link to
    the record page only (rights rule 10: never files, folder listings, or the viewer);
  - their edition guides, with Bookshop.org buttons only for ISBNs already in data/guide.js (bookshop.org/a/<id>/<isbn>);
  - their official site, talks, and podcasts: hub `links` of kind `site` and AUTHORX `own`, shown only when the URL
    is in CHECKED (it answered 200 on that date; rerun tools/check_author_links.py to refresh).
The Wikipedia excerpt is not shown on these pages (the Wikipedia link stays in "More sources").
"""
import html,json,re
E=lambda s:html.escape(str(s),quote=True)
# Role words for intro(); keep in step with AU_ROLE in app.js.
ROLE={'saint':'saint','father':'Church Father','pope':'pope','martyr':'martyr','bishop':'bishop','cardinal':'cardinal',
      'theologian':'theologian','philosopher':'philosopher','mystic':'mystic','apologist':'apologist','novelist':'novelist',
      'poet':'poet','historian':'historian','spiritual':'spiritual writer','monastic':'monastic','scripture':'Scripture scholar',
      'convert':'convert','founder':'founder','preacher':'preacher','liturgist':'liturgist','scientist':'scientist',
      'journalist':'journalist','canonist':'canonist','catechist':'catechist'}
def oxford(xs):
    xs=list(xs)
    return xs[0] if len(xs)==1 else ' and '.join(xs) if len(xs)==2 else ', '.join(xs[:-1])+', and '+xs[-1]
def plural(n,one,many):return str(n)+' '+(one if n==1 else many)
def intro(au,era_label,n_books,n_guides,n_online):
    """Two neutral sentences from fields: name, years, era, roles, and what the page lists."""
    if au.get('intro'):return au['intro']
    f=lambda y:str(-y)+' BC' if y<0 else str(y)
    b,d=au.get('born'),au.get('died')
    yrs=' ('+f(b)+'–'+f(d)+')' if isinstance(b,int) and isinstance(d,int) else ' (born '+f(b)+')' if isinstance(b,int) else ' (died '+f(d)+')' if isinstance(d,int) else ''
    roles=[ROLE[t] for t in au.get('tags') or [] if t in ROLE][:3]
    s=au['name']+yrs+' appears in our authors list'+(' under '+era_label if era_label else '')+(', as '+('an' if roles[0][0] in 'aeiouAEIOU' else 'a')+' '+oxford(roles) if roles else '')+'.'
    parts=[]
    if n_guides:parts.append(plural(n_guides,'edition guide','edition guides'))
    if n_online:parts.append(plural(n_online,'work','works')+' to read at outside sources')
    if n_books:parts.append(plural(n_books,'book','books')+' in the Isidore Index, each linked to its catalog record with a rights badge')
    return s+' '+('This page lists '+oxford(parts)+'.' if parts else 'This page links outside sources about '+au['name']+'.')
# --- rights badges (a port of scripts/rights.js resolve(), edition(), title(), and badge()) ---
STATUSES={'public_domain_us':('Public domain (US)',True),'open_license':('Open license',True),'permission_granted':('Permission granted',True),
          'link_only':('Link only',False),'unknown':('Unknown',False)}
def resolve(R,id):
    r=(R.get('records') or {}).get(str(id))
    if not r:return {'status':'unknown','evidence':'Not yet reviewed.','checked':''}
    c=R['codes'].get(r[0]) or {};st=r[3] if r[0]=='M' else c.get('status')
    extra=r[1] if len(r)>1 and r[1] else ''
    ev=((c.get('text') or '')+(' '+extra if extra else '')).strip()
    if st not in STATUSES:st='unknown'
    if STATUSES[st][1] and not len(extra)>20:st='unknown'
    return {'status':st,'evidence':ev,'checked':r[2] if r[0]=='M' else R.get('checked','')}
def edition(e):
    if not e or e.get('access')=='reference':return None
    if e.get('text') and re.match(r'Public domain in the USA',e.get('rights') or '') and e.get('checked'):
        return {'status':'public_domain_us','evidence':((e['note']+' ') if e.get('note') else '')+e['rights'],'checked':e['checked']}
    return {'status':'link_only','evidence':(e.get('rights') or '')+' Read it at the source.','checked':e.get('checked') or ''}
def badge(x):
    if not x:return ''
    lab=STATUSES[x['status']][0]
    t=lab+'. '+x['evidence']+(' Checked '+x['checked']+'.' if x['checked'] else '')+' Not legal advice.'
    return ' <a class="rights-badge rb-'+x['status'].replace('_','-')+'" href="/rights/" data-rights="'+x['status']+'" title="'+E(t)+'"><span class="rb-k">Rights:</span> '+E(lab)+'</a>'
# --- outside links, each answered 200 on the date given (tools/check_author_links.py) ---
CHECKED={
 'https://bibleinayear.fireside.fm/':'2026-11-03','https://catechisminayear.fireside.fm/':'2026-11-03','https://catholicproductions.com/':'2026-11-03',
 'https://chastity.com/':'2026-11-03','https://chnetwork.org/':'2026-11-03','https://edwardfeser.blogspot.com/':'2026-11-03',
 'https://jimmyakin.com/':'2026-11-03','https://maritain.nd.edu/':'2026-11-03','https://mattfradd.substack.com':'2026-11-03',
 'https://merton.org/':'2026-11-03','https://patrickmadrid.com/':'2026-11-03','https://press.christendom.edu/':'2026-11-03',
 'https://stpaulcenter.com/':'2026-11-03','https://tobinstitute.org/':'2026-11-03','https://www.catholic.com/':'2026-11-03',
 'https://www.catholic.com/audio/cot':'2026-11-03','https://www.catholicworker.org/':'2026-11-03','https://www.catholicworker.org/dorothyday/':'2026-11-03',
 'https://www.celebratesheen.com/':'2026-11-03','https://www.dailywire.com/show/pints-with-aquinas':'2026-11-03','https://www.ewtn.com/':'2026-11-03',
 'https://www.jpearce.co/':'2026-11-03','https://www.peterkreeft.com/':'2026-11-03','https://www.peterkwasniewski.com/':'2026-11-03',
 'https://www.studiobrien.com/':'2026-11-03','https://www.tolkiensociety.org/':'2026-11-03','https://www.traditionsanity.com':'2026-11-03',
 'https://www.trenthorn.com/':'2026-11-03','https://www.trenthorn.com/books/':'2026-11-03','https://www.wordonfire.org/':'2026-11-03',
 'https://www.wordonfire.org/videos/wordonfire-show/':'2026-11-03','https://www.youtube.com/@AscensionPresents':'2026-11-03',
 'https://www.youtube.com/@BishopBarron':'2026-11-03','https://www.youtube.com/@CatholicProductions':'2026-11-03',
 'https://www.youtube.com/@DrTaylorMarshall':'2026-11-03','https://www.youtube.com/@StPaulCenter':'2026-11-03',
 'https://www.youtube.com/@TheCounselofTrent':'2026-11-03','https://www.youtube.com/@pintswithaquinas':'2026-11-03',
}
# Not shown: isidore.co (rule 10; the Calibre app root offers files), searches, and URLs that did not answer 200
# on 2026-11-03 (coramfratribus.com 403, mysteriousworld.com no response).
def official(au,X):
    """[(label, url, kind)] of the author's own sites and media, CHECKED only, in data order, no duplicates."""
    out,seen=[],set()
    for l in au.get('links') or []:
        if l.get('kind')=='site':out.append((l['label'],l['url'],'site'))
    for o in (X.get('own') or []):out.append((o['t'],o['u'],o.get('k') or 'site'))
    res=[]
    for t,u,k in out:
        if u in CHECKED and u not in seen and 'isidore.co' not in u and '/search' not in u:seen.add(u);res.append((t,u,k))
    return res
def bookshop_id(root):
    m=re.search(r"bookshopId:\s*'(\d+)'",(root/'data/affiliates.js').read_text());assert m and m.group(1)=='130222','Bookshop id must be 130222'
    return m.group(1)
def disclosure(root):
    m=re.search(r"disclosure:\s*'([^']*)'",(root/'data/affiliates.js').read_text());t=m.group(1)
    return '<p class="disclosure small"><b>Affiliate disclosure:</b> '+E(re.sub(r'^Affiliate disclosure:\s*','',t))+'</p>'
