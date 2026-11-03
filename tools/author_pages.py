"""Phase A item 2 (2026-11-03): static pages for the authors with no hosted work in the reading room.

Each such page gets, from data already in the repo (nothing invented, nothing hosted):
  - a short intro: the hand-written `intro` on the hub record (Trent Horn, Thomas E. Woods, Warren H. Carroll,
    Scott Hahn; sources in docs/AUTHOR-PAGES.md), else `intro()` below, a neutral sentence built from fields.
    app.js `auIntro()` builds the same text in the browser (tests/author_pages.test.js compares them);
  - their reading-room works (link only) and their Isidore Index books, each with its rights badge and a link to
    the record page only (rights rule 10: never files, folder listings, or the viewer);
  - their edition guides (Bookshop.org buttons switched off on author pages until the owner approves: AUTHOR_GUIDE_BOOKSHOP_BUTTONS);
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
# Phase A item 2 (Research file data/modern-authors.json): answered 200 to curl on 2026-11-03 (ours or Research's
# modern-authors-pages-urlchecks.tsv; Open Library often times out, so either check counts). christendom.edu answers curl
# with a WAF 202, so its founder page was read with a fetch tool instead.
CHECKED.update({
 'https://ignatius.com/rome-sweet-home-rshp/':'2026-11-03',
 'https://ignatius.com/the-case-for-catholicism-ccatp/':'2026-11-03',
 'https://open.spotify.com/show/4RziZyRebkVYcRuGJlkJHN':'2026-11-03',
 'https://open.spotify.com/show/5PGmCKE1KzIHMN9kvKOpC8':'2026-11-03',
 'https://openlibrary.org/books/OL11840237M':'2026-11-03',
 'https://openlibrary.org/books/OL1185320M':'2026-11-03',
 'https://openlibrary.org/books/OL1443841M':'2026-11-03',
 'https://openlibrary.org/books/OL24073218M':'2026-11-03',
 'https://openlibrary.org/books/OL25687142M':'2026-11-03',
 'https://openlibrary.org/books/OL26010787M':'2026-11-03',
 'https://openlibrary.org/books/OL27360486M':'2026-11-03',
 'https://openlibrary.org/books/OL27579221M':'2026-11-03',
 'https://openlibrary.org/books/OL29776930M':'2026-11-03',
 'https://openlibrary.org/books/OL3044488M':'2026-11-03',
 'https://openlibrary.org/books/OL31846749M':'2026-11-03',
 'https://openlibrary.org/books/OL32182826M':'2026-11-03',
 'https://openlibrary.org/books/OL32842693M':'2026-11-03',
 'https://openlibrary.org/books/OL3691914M':'2026-11-03',
 'https://openlibrary.org/books/OL37069606M':'2026-11-03',
 'https://openlibrary.org/books/OL37087M':'2026-11-03',
 'https://openlibrary.org/books/OL37739292M':'2026-11-03',
 'https://openlibrary.org/books/OL623217M':'2026-11-03',
 'https://openlibrary.org/books/OL6788677M':'2026-11-03',
 'https://openlibrary.org/books/OL698412M':'2026-11-03',
 'https://openlibrary.org/books/OL7440923M':'2026-11-03',
 'https://openlibrary.org/books/OL8250523M':'2026-11-03',
 'https://openlibrary.org/books/OL8385028M':'2026-11-03',
 'https://openlibrary.org/books/OL8385032M':'2026-11-03',
 'https://openlibrary.org/books/OL8385034M':'2026-11-03',
 'https://openlibrary.org/books/OL8385041M':'2026-11-03',
 'https://openlibrary.org/books/OL8385062M':'2026-11-03',
 'https://openlibrary.org/books/OL8385066M':'2026-11-03',
 'https://podcasts.apple.com/us/podcast/the-counsel-of-trent/id1354647807':'2026-11-03',
 'https://podcasts.apple.com/us/podcast/the-tom-woods-show/id716825890':'2026-11-03',
 'https://press.christendom.edu/product/1917/':'2026-11-03',
 'https://press.christendom.edu/product/history-of-christendom-collection/':'2026-11-03',
 'https://press.christendom.edu/product/isabel-of-spain/':'2026-11-03',
 'https://press.christendom.edu/product/our-lady-of-guadalupe-2/':'2026-11-03',
 'https://press.christendom.edu/product/the-building-of-christendom-324-1100/':'2026-11-03',
 'https://press.christendom.edu/product/the-cleaving-of-christendom-1517-1661/':'2026-11-03',
 'https://press.christendom.edu/product/the-crisis-of-christendom-1815-2005/':'2026-11-03',
 'https://press.christendom.edu/product/the-founding-of-christendom/':'2026-11-03',
 'https://press.christendom.edu/product/the-glory-of-christendom-1100-1517/':'2026-11-03',
 'https://press.christendom.edu/product/the-last-crusade-2/':'2026-11-03',
 'https://press.christendom.edu/product/the-revolution-against-christendom-1661-1815/':'2026-11-03',
 'https://shop.catholic.com/answering-atheism-how-to-make-the-case-for-god-with-logic-and-charity/':'2026-11-03',
 'https://shop.catholic.com/counterfeit-christs-finding-the-real-jesus-among-the-impostors/':'2026-11-03',
 'https://shop.catholic.com/made-this-way-how-to-prepare-kids-to-face-todays-tough-moral-issues/':'2026-11-03',
 'https://shop.catholic.com/what-the-saints-never-said-pious-misquotes-and-the-subtle-heresies-they-teach-you/':'2026-11-03',
 'https://shop.catholic.com/why-were-catholic-our-reasons-for-faith-hope-and-love/':'2026-11-03',
 'https://tomwoods.com/':'2026-11-03',
 'https://tomwoods.com/podcasts/':'2026-11-03',
 'https://www.catholic.com/profile/trent-horn':'2026-11-03',
 'https://www.christendom.edu/about/warren-h-carroll/':'2026-11-03',
 'https://www.franciscan.edu/':'2026-11-03',
 'https://www.instagram.com/scottwhahn':'2026-11-03',
 'https://www.ncregister.com/news/warren-carroll-1932-2011-83xz3xbw':'2026-11-03',
 'https://www.scotthahn.com/':'2026-11-03',
 'https://www.scotthahn.com/audio-video/2016/1/20/sunday-bible-reflections':'2026-11-03',
 'https://www.scotthahn.com/listen-online':'2026-11-03',
 'https://www.youtube.com/@TomWoodsTV':'2026-11-03',
 'https://x.com/Trent_Horn':'2026-11-03',
 'https://x.com/thomasewoods':'2026-11-03',
})
# Bookshop.org buttons for the Research books: DISABLED until the owner approves new Bookshop links (Business, 2026-11-03).
# No Bookshop product page could be verified (Cloudflare 403). The ISBN-13 stays in the data (hub `books[].isbn`) as the hook;
# nothing is rendered while this is False.
RESEARCH_BOOKSHOP_BUTTONS=False
# The edition-guide Bookshop buttons that commit 937ddf5a added to author pages are switched off the same way (they were
# new links on author pages; the edition-guide pages keep theirs). True restores them, with the affiliate disclosure.
AUTHOR_GUIDE_BOOKSHOP_BUTTONS=False
LINK_ONLY={'status':'link_only','evidence':'Published after 1931 and in copyright: we link to it and host nothing.','checked':'2026-11-03'}
def books_html(au,E,a):
    """'Selected books' from hub books[] (data/modern-authors.json via tools/import_modern_authors.py): link-only, rights badge,
    verified ISBN-13 as text. The ISBN is the disabled Bookshop hook (RESEARCH_BOOKSHOP_BUTTONS); nothing is linked to Bookshop."""
    bs=au.get('books') or []
    if not bs:return ''
    li=[]
    for b in bs:
        t=a(b['url'],b['t'],True) if b.get('url') else E(b['t'])
        meta=', '.join(x for x in [b.get('pub'),str(b['y']) if b.get('y') else ''] if x)
        li.append('<li data-isbn="'+b['isbn']+'">'+t+(' ('+E(meta)+')' if meta else '')+(', '+E(b['note']) if b.get('note') else '')+'. <span class="small">ISBN '+b['isbn']+'</span>'+badge(LINK_ONLY)+'</li>')
    return '<h2>Selected books</h2><p class="small">These books are in copyright. Each title links to its publisher or library record; we host none of them.</p><ul class="au-books">'+''.join(li)+'</ul>'
def official(au,X):
    """[(label, url, kind)] of the author's own sites and media, CHECKED only, in data order, no duplicates."""
    out,seen=[],set()
    for m in au.get('media') or []:out.append((m['label'],m['url'],m['kind']))
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
