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
     '<p><b>Bibliotheca Catholica</b> (bibliothecacatholica.com) is a free Catholic library of libraries: a selected reading room and a curated resource index. '
     'It gathers Catholic authors from the Apostolic Fathers to today, Sacred Scripture, the documents of the Magisterium, prayers and devotions, reference works, podcasts and media, and a reading room of classic texts. '
     'Each entry links to its original source, such as vatican.va, New Advent, the Christian Classics Ethereal Library, Project Gutenberg, and the St. Isidore e-book library.</p>'
     '<p>The '+a('/library/','reading room')+' comes first. Its '+str(n['hosted'])+' hosted texts are older editions listed by their sources as public domain in the United States, chosen under our pre-1931 rule and checked against those sources, and readable right here, with contents, search, highlights, notes, and your place saved in your own browser. '
     'Every hosted text keeps its source record, its SHA-256 checksum, and its rights evidence. Everything else stays with its publisher, and Bibliotheca Catholica links to it.</p>'
     '<p>Beyond the reading room, the library indexes '+str(n['authors'])+' '+a('/authors/','Catholic authors')+' with short biographies and works online, '
     +str(n['saints'])+' '+a('/saints/','saints')+' with sourced feast days, '+a('/editions/','edition guides')+' that compare translations, curated '+a('/reading/','reading lists')+', and the '
     +a('/isidore/','Isidore Index')+' of '+format(n['books'],',')+' e-books, each with a '+a('/rights/','rights badge')+'. '
     'Listing a book is not endorsement; the '+a('/policy/','Fidelity & Editorial Policy')+' explains how context notes work.</p>'
     '<p>Bibliotheca Catholica is independent, free for everyone, and has no ads. Start with a section below, or search everything from the box at the top of any page.</p>'
     '</div><h3>Sections of the library</h3><ul class="home-sections">'+sec+'</ul><p class="home-info">'+info+'</p></section>')
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
     'Our rule is to host only texts first published before 1931, in an edition or translation its source lists as public domain in the United States. The rule applies to the text, not always to the printing that was transcribed: a file can come from a later reprint of an earlier text, for example a 1934 reprint of a 1908 book. For some hosted editions our records do not yet note the year of the specific translation; we are adding that evidence. Later works are linked at their publishers or libraries, never copied.</p>'
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
     '<p>The library is independent and has no ads. You can '+a('/support/','support the library')+', suggest a correction, or offer commentary from the Support page.</p></section>')
