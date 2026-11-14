"""Site copy shared by the static build and the app (v17 SEO).

tools/build_static.py renders these into the pre-rendered home page (index.html, between the
static-home markers), into /about/, and into data/site-copy.js (window.SITE_COPY) so app.js shows the
same text on #/ and #/about.  Plain facts only: every count comes from the data files; no rankings,
reviews, or claims we cannot check.  Oxford commas; follow the money rules in AGENTS.md.
"""
import html
E=html.escape
# (path, label, one-line description) for the home page's "Sections of the library" list
SECTION_LINKS=[
 ('/library/','Reading Room: Discover & Read','classic texts to read here, with source editions and rights notes'),
 ('/authors/','Catholic Authors','biographies and works online, from the Apostolic Fathers to today'),
 ('/saints/','Saints & Hagiography','sourced feast days, the saints of legend, and the old lives of the saints'),
 ('/doctors/','Doctors of the Church','the saints honored for eminent teaching'),
 ('/timeline/','Timeline','saints and writers through the centuries'),
 ('/editions/','Editions & Translations','which translation of each classic to read or buy'),
 ('/reading/','Reading Lists','curated paths for beginners, apologetics, spiritual classics, and more'),
 ('/reading/advent-2026/','Advent with the Fathers','a daily reading plan for Advent 2026, November 29 to December 24'),
 ('/isidore/','The Isidore Index','e-books and PDFs in the St. Isidore library, each with a rights badge'),
 ('/scripture/','Sacred Scripture','Bibles, commentaries, and daily readings'),
 ('/magisterium/','Church Documents','catechisms, councils, encyclicals, and canon law'),
 ('/prayers/','Prayers & Devotions','the common prayers of the Church and the Rosary'),
 ('/references/','Reference Works','encyclopedias, dictionaries, liturgy, and chant'),
 ('/libraries/','Digital Libraries','the great Catholic archives and online libraries'),
 ('/media/','Podcasts & Media','podcasts, channels, radio, and news'),
 ('/rare/','Rare & Obscure','lesser-known books and manuscripts online'),
 ('/projects/','Projects','open Catholic software, data, and translations'),
 ('/substacks/','Catholic Substacks','writers and newsletters worth reading'),
 ('/data/','Open Data','the catalogue as JSON and CSV, free to reuse'),
]
INFO_LINKS=[('/about/','About the library'),('/policy/','Fidelity & Editorial Policy'),('/rights/','Rights & Permissions'),('/takedown/','Takedown requests'),('/support/','Support the Library')]
LICENSING_URL='/licensing/'
def a(href,label):return '<a href="'+E(href)+'">'+E(label)+'</a>'
def home_about(n):
    """The descriptive block on the home page (static HTML and the app). n: dict of counts."""
    sec=''.join('<li>'+a(h,l)+' <span>'+E(d)+'</span></li>' for h,l,d in SECTION_LINKS)
    info=' · '.join(a(h,l) for h,l in INFO_LINKS)
    return ('<section class="home-about" aria-labelledby="home-about-h"><div class="eyebrow">About the library</div>'
     '<h2 id="home-about-h">A Catholic reading room and resource index</h2>'
     '<div class="home-about-text">'
     '<p><b>Bibliotheca Catholica</b> (bibliothecacatholica.com) gathers Catholic books and the libraries that preserve them. '
     'The '+a('/library/','reading room')+' offers '+str(n['hosted'])+' editions to read here for free. Each keeps its source, original notices, and rights evidence. '
     'Other works open at their original libraries or publishers.</p>'
     '<p>Explore '+str(n['authors'])+' '+a('/authors/','authors')+', compare '+a('/editions/','translations')+', or browse the '
     +a('/isidore/','Isidore Index')+' of '+format(n['books'],',')+' e-books. Bibliotheca Catholica is independent, free for everyone, and has no ads.</p>'
     '</div><details class="home-directory"><summary>All sections of the library</summary><ul class="home-sections">'+sec+'</ul></details><p class="home-info">'+info+'</p></section>')

def home_hero():
    return ('<section class="hero hero-c"><h1 class="eyebrow hero-name">Bibliotheca Catholica</h1>'
     '<p class="hero-title">Tolle Lege</p><p class="hero-trans">Take up and read</p>'
     '<p class="hero-sub">Two thousand years of Catholic thought, in one place.</p>'
     '<p class="lede">Find a book, spend time with its author, and follow the ideas that lead you further into the Catholic tradition.</p>'
     '<form class="hero-search" action="/search/" onsubmit="location.hash=\'#/search/\'+encodeURIComponent(this.lookup.value);return false">'
     '<input type="search" name="lookup" placeholder="Search a title, author, or subject" aria-label="Search everything">'
     '<button class="btn">Search</button></form>'
     '<div class="hero-cta"><a class="btn gold" href="/library/">Enter the reading room →</a>'
     '<a class="btn ghost" href="/reading/">Help me choose a book</a></div></section>')

def home_paths(n):
    paths=[('/authors/','Follow an author','Meet the Fathers, Doctors, theologians, poets, and novelists through their lives and writings.'),
           ('/saints/','Explore the saints','Find sourced feast days, historical context, and the books that tell their stories.'),
           ('/libraries/','Search the wider tradition','Visit digital libraries and archives for Scripture, theology, manuscripts, and reference works.')]
    cards=''.join('<a class="home-path" href="'+u+'"><h3>'+E(t)+'</h3><p>'+E(d)+'</p><span aria-hidden="true">Explore →</span></a>' for u,t,d in paths)
    picks=[('confessions','Confessions','St. Augustine'),('imitation-of-christ','The Imitation of Christ','Thomas à Kempis'),('story-of-a-soul','Story of a Soul','St. Thérèse of Lisieux'),('orthodoxy','Orthodoxy','G. K. Chesterton')]
    return ('<section class="reading-home" aria-labelledby="home-reading-h"><div><div class="eyebrow">The reading room</div>'
     '<h2 id="home-reading-h">A place to begin</h2><p>'+str(n['hosted'])+' source-checked editions to read here, with adjustable text, search, highlights, notes, and your place saved in this browser.</p>'
     '<a href="/library/">Browse the reading room →</a></div><ul class="rh-list">'+''.join('<li><a href="/work/'+i+'/"><b>'+E(t)+'</b><span>'+E(au)+'</span></a></li>' for i,t,au in picks)+'</ul></section>'
     '<section aria-labelledby="home-explore-h"><div class="page-head"><h2 id="home-explore-h">Follow your curiosity</h2></div><div class="home-paths">'+cards+'</div></section>')

def acta_source():
    return ('<section class="panel"><h2>Read the Bollandist sources</h2><p>'
     '<a href="https://actasanctorum.org/index-saints.html" target="_blank" rel="noopener">Acta Sanctorum: index of saints ↗</a>'
     ' offers Wilson Pruitt’s AI-assisted English translation alongside source references. The publisher reports coverage of the published series through November 10, not a complete modern liturgical calendar. '
     'Historical feast dates and hagiographic narratives need their own context.</p><p>'
     '<a href="https://actasanctorum.org/about.html" target="_blank" rel="noopener">Translation method and known defects ↗</a> · '
     '<a href="https://actasanctorum.org/rights.html" target="_blank" rel="noopener">Translation license: CC BY-NC 4.0 ↗</a>'
     '</p><p class="small muted">Read at source. This modern translation is separate from the public-domain editions on this shelf; its fidelity has not been independently reviewed here.</p></section>')
def about_page(n):
    return ('<div class="page-head"><div class="eyebrow">De bibliotheca</div><h1>About the library</h1>'
     '<p class="lede">A free Catholic library of libraries: a selected reading room and a curated resource index, with links to original Church sources and digital libraries. Coverage is selective, not exhaustive.</p></div>'
     '<section class="panel policy"><h2>What is here</h2>'
     '<p>The library has four parts. The '+a('/library/','reading room')+' holds '+str(n['hosted'])+' classic texts you can read on this site. '
     'The '+a('/authors/','author pages')+' ('+str(n['authors'])+' authors), the '+a('/saints/','saints guide')+' ('+str(n['saints'])+' saints), the '+a('/editions/','edition guides')+', and the '+a('/reading/','reading lists')+' are our own curated shelves. '
     'The '+a('/isidore/','Isidore Index')+' catalogues '+format(n['books'],',')+' books in the St. Isidore e-book library (isidore.co). '
     'The section pages, such as '+a('/scripture/','Scripture')+', '+a('/magisterium/','Church Documents')+', and '+a('/libraries/','Digital Libraries')+', point to the Church’s own documents and the great Catholic digital libraries.</p>'
     '<h2>Where the texts come from</h2>'
     '<p>Every hosted text is a public-domain edition from a known source, usually Project Gutenberg. We keep the original file, a snapshot of its catalogue record, and its SHA-256 checksum, so anyone can check that the text has not been changed, and each reader page shows the source edition, its translator where known, and its license notice. '
     'Our rule is to host only texts first published before 1931, in an edition or translation its source lists as public domain in the United States. The rule applies to the text, not always to the printing that was transcribed: a file can come from a later reprint of an earlier text, for example a 1952 reprint of a 1920 book. For some hosted editions our records do not yet note the year of the specific translation; we are adding that evidence. Later works are linked at their publishers or libraries, never copied.</p>'
     '<h2>Dates, files, and sections</h2>'
     '<p>Dates for a work, its translation, and a digital release are distinct, and source editions retain their own notices and credits. '
     'Ebook files, Isidore Index files, and library-copy searches are served by the original libraries; their formatting and editorial details may differ from the online text, and holdings, borrowing, and digital availability depend on the library and edition. '
     'In the reader, sections divide a source into manageable reading lengths; they are navigation aids, not editorial chapters or scholarly paragraph numbers.</p>'
     '<h2>Licensing and credits</h2>'
     '<p>The site’s code is under the MIT License, the '+a('/data/','open data')+' is dedicated to the public domain under CC0, and the writing on these pages is under CC BY 4.0. Hosted texts carry no license from us: they are public domain in the United States, and each keeps its source’s notice. Author excerpts from Wikipedia are shortened and shared under CC BY-SA 4.0, and each portrait is credited on its author page. The details are in our <a href="'+LICENSING_URL+'">licensing note</a>, a summary rather than legal advice.</p>'
     '<h2>Our name</h2>'
     '<p>Bibliotheca Catholica (bibliothecacatholica.com) is an independent project. It is not affiliated with IntraText’s “Bibliotheca Catholica” collection (intratext.com) or with Minha Biblioteca Católica (bibliotecacatolica.com.br), and it does not speak for them.</p>'
     '<h2>Rights badges</h2>'
     '<p>Every record carries one of five '+a('/rights/','rights badges')+': public domain (US), open license, permission granted, link only, or unknown, with its evidence and the date it was checked. Download and reader buttons appear only for the first three. '
     'A rights holder who wants a text or link removed can follow the '+a('/takedown/','takedown process')+'.</p>'
     '<h2>Editorial policy</h2>'
     '<p>Bibliotheca Catholica intends to be faithful to the Magisterium of the Catholic Church. Listing a book is not endorsement: some records in the Isidore Index carry calm, factual context notes, and they are never featured. The '+a('/policy/','Fidelity & Editorial Policy')+' explains this and includes the privacy notice.</p>'
     '<h2>Goals</h2>'
     '<p>To make the Catholic tradition easy to find and pleasant to read: clean editions, honest sources, careful rights checks, and links that lead back to the libraries that did the work. The catalogue is also published as '+a('/data/','open data')+' for anyone to reuse.</p>'
     '<h2>Help the library</h2>'
     '<p>The library is independent and has no ads. You can '+a('/support/','support the library')+', suggest a correction, or offer commentary from the Support page. To follow the project, see '+'<a href="https://x.com/BiblioCatholica" target="_blank" rel="noopener">X</a>'+', '+'<a href="https://bsky.app/profile/bibliothecacatholica.com" target="_blank" rel="noopener">Bluesky</a>'+', and the '+'<a href="https://bibliothecacatholica.substack.com/subscribe" target="_blank" rel="noopener">Newsletter</a>'+' on Substack.</p></section>')

# --- Newsletter sign-up (owner-approved preview 2026-11-09). The Substack embed is third-party content, so it is
# used only on the home page and /reading/advent-2026/ (lazy-loaded, responsive, titled); every other page has the
# plain sign-up link in the footer (index.html). The pitch line (NEWSLETTER_LINE) appears once per page, in the footer. No analytics attributes: outbound_click classifies substack.com.
SUBSTACK='https://bibliothecacatholica.substack.com/'
SUBSCRIBE=SUBSTACK+'subscribe'
NEWSLETTER_LINE='Advent with the Fathers: a short reading from the Church Fathers each day, Nov 29 to Dec 24. Free.'
def newsletter_box():
    return ('<section class="newsletter-box" aria-label="Newsletter sign-up"><div class="eyebrow">The newsletter</div>'
     '<h2>Bibliotheca Catholica by email</h2>'
     '<iframe class="nl-embed" src="'+SUBSTACK+'embed" title="Sign up for the Bibliotheca Catholica newsletter on Substack" width="480" height="320" loading="lazy" style="border:1px solid #EEE; background:white;" frameborder="0" scrolling="no"></iframe>'
     '<p class="small nl-fine">The sign-up form is provided by Substack under its own <a href="https://substack.com/privacy" target="_blank" rel="noopener">privacy policy</a>.</p></section>')

# --- /disclosure/ (owner-approved preview 2026-11-09): the affiliate relationships, in plain words.
DISCLOSURE_TITLE='Affiliate disclosure'
DISCLOSURE_DESC='How Bibliotheca Catholica uses affiliate links to Bookshop.org and TAN Books, what they earn, and why free reading in the library always comes first here.'
def disclosure_page(ftc):
    return ('<div class="page-head"><div class="eyebrow">Support the library</div><h1>'+DISCLOSURE_TITLE+'</h1>'
     '<p class="lede">'+E(ftc)+'</p></div>'
     '<section class="panel policy">'
     '<h2>Reading here is always free</h2>'
     '<p>The '+a('/library/','reading room')+' comes first. Every hosted text is free to read on this site, and book pages always list the free reading editions before any place to buy a print copy. Purchase links appear in a separate, clearly labeled section, “Buy in print,” with this disclosure beside them.</p>'
     '<h2>Bookshop.org</h2>'
     '<p>Bibliotheca Catholica is a Bookshop.org affiliate. Links to Bookshop.org on book pages, '+a('/editions/','edition guides')+', and the '+a('/support/','Support page')+' carry our affiliate ID. When you buy through them, Bookshop.org pays us a small commission at no extra cost to you, and part of each sale supports independent bookstores. We link a specific book only where our edition guide records its ISBN.</p>'
     '<h2>TAN Books</h2>'
     '<p>Bibliotheca Catholica is a TAN Books affiliate. The “Browse TAN Books” link on classic Catholic works and their authors’ pages is a referral link (it passes through lddy.no, TAN Books’ referral service, and opens tanbooks.com). If you buy from TAN Books after following it, we may earn a small commission at no extra cost to you. The link opens TAN’s store, not a particular book, and does not mean TAN publishes that title.</p>'
     '<h2>Other links</h2>'
     '<p>Links to other publishers, libraries, and bookstores, including the publisher searches in the edition guides, are ordinary links, and we earn nothing from them unless a program is added to this page. We do not use Amazon affiliate links.</p>'
     '<h2>How we choose</h2>'
     '<p>Commissions never decide what we recommend. Editions and translations are chosen on their merits, and a book with no affiliate link is listed just the same. Listing is not endorsement; see the '+a('/policy/','Fidelity & Editorial Policy')+'.</p>'
     '<h2>Privacy</h2>'
     '<p>Affiliate links are plain links. Our analytics record only that an outside link was clicked, with its domain and a general kind (such as bookshop or affiliate), as the '+a('/policy/','Privacy section')+' explains. Bookshop.org and TAN Books handle your purchase under their own privacy policies.</p>'
     '<h2>Other ways to help</h2>'
     '<p>You can also '+a('/support/','support the library')+' directly, or get the free <a href="'+SUBSCRIBE+'" target="_blank" rel="noopener">newsletter</a> on Substack.</p>'
     '</section>')
