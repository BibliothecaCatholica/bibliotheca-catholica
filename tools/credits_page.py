"""The "Sources and credits" page (/credits/) and the short colophon at the end of each hosted book.

Owner direction (November 15, 2026; docs/PROJECT-RULES.md rules 10 and 11, docs/DESIGN.md "Notices"): credits and
rights detail move off the reading and author pages into this one page, generated from the same data the pages use.
Nothing is deleted from data/ or from the build output: what left a page is here in full, and the page links to it.

  * Books: one record per hosted edition (anchor `ed-<edition id>`): rights statement and basis, evidence, edition
    note, source, source record, SHA-256, the collation or read-rate result, and the checked date. The end of each book
    shows `colophon()`, one short line that links to its record. scripts/library.js `colophon()` writes the same line
    in the reading room (tests/test_credits_page.py checks both).
  * Portraits (anchor `portrait-<author id>`): artist, license and its link, and the file page, for every credited
    portrait the author pages show. Author pages show only an "Image credit" link.
  * Wikipedia excerpts (anchor `wiki-<author id>`): article link, "shortened", and CC BY-SA 4.0 with its link, for
    every author page that shows an excerpt. Those pages show only a "Text credit" link.
  * The home page engraving (anchor `home-engraving`); its credit line also stays on the home page.
"""
import html
import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CC_BY_SA = 'https://creativecommons.org/licenses/by-sa/4.0/'
PROVENANCE = 'https://texts.bibliothecacatholica.com/provenance/'
URL = '/credits/'
E = lambda s: html.escape(str(s), quote=True)
BASIS = {  # one plain line per rights basis; the same words as BASIS in scripts/library.js
    'pd-date': 'Public domain in the USA by date of publication.',
    'pd-nonrenewal': 'Public domain in the USA: first published in the United States, and its copyright was not renewed.',
}


def ext(href, label):
    return '<a href="' + E(href) + '" target="_blank" rel="noopener">' + label + '</a>'


def basis_line(e):
    """The colophon's rights sentence: from the recorded basis, else the first sentence of the edition's rights."""
    return BASIS.get(e.get('rightsBasis')) or (e.get('rights') or 'Rights not recorded.').split('. ')[0].rstrip('.') + '.'


def colophon(e):
    """The short colophon at the end of a hosted book: rights in one line, the source, the checked date, and the record link."""
    return ('<p class="small colophon">' + E(basis_line(e)) + ' Source: ' + ext(e['source'], E(e['label'])) + '. Checked '
            + E(e['checked']) + '. <a href="' + URL + '#ed-' + E(e['id']) + '">Full record in Sources and credits</a>.</p>')


def source_record(eid):
    p = ROOT / 'data/sources' / (eid + '.json')
    return json.loads(p.read_text()) if p.exists() else {}


def checks(r):
    """The collation or transcription result, from the edition's source record, in plain words."""
    if isinstance(r.get('collation'), str):  # a collation written up in words (the Standard Ebooks edition)
        return E(r['collation'])
    if r.get('collation'):
        c = r['collation']
        w = r.get('iaWitness') or {}
        return ('Compared word by word with the Internet Archive scan ' + ext(w.get('url', ''), E(w.get('identifier', ''))) + ' ('
                + E(w.get('year', '')) + '): ' + format(c['agreement'], '.1%') + ' of ' + format(c['sourceWords'], ',')
                + ' words confirmed by its OCR; the differing passages are listed in the source record.')
    if r.get('readRate') is not None:
        fixes = len(r.get('handFixes') or [])
        return ('Transcribed from the scan: ' + format(r['readRate'], '.2%') + ' of ' + format(r['words'], ',') + ' words read, '
                + str(r.get('corrections', 0)) + ' OCR confusions repaired, ' + (str(fixes) + ' misreadings corrected by hand against the page images, ' if fixes else '')
                + str(r.get('flaggedBlocks', 0)) + ' paragraphs flagged for an unread word. Not a manual proofread.')
    return 'The file is kept byte for byte as its source published it, with its own notices; no collation is recorded.'


def book_record(w, e, libw):
    r = source_record(e['id'])
    rows = [('Rights', E(e.get('rights', ''))),
            ('Basis', E(BASIS.get(e.get('rightsBasis'), 'Not recorded separately; see the rights statement.'))),
            ('Evidence', E(e['rightsEvidence']) if e.get('rightsEvidence') else ''),
            ('Edition note', E(e['note']) if e.get('note') else ''),
            ('Source', ext(e['source'], E(e['label']))),
            ('Source record', ext(PROVENANCE + e['id'] + '.json', 'provenance/' + E(e['id']) + '.json')),
            ('SHA-256', '<code>' + E(e['sha256']) + '</code>'),
            ('Checks', checks(r)),
            ('Checked', E(e['checked']))]
    if e.get('retired'):
        rt = e['retired']
        rows.insert(0, ('Retired', 'On ' + E(rt['date']) + ', replaced by <a href="#ed-' + E(rt['replacedBy']) + '">the corrected edition</a>: '
                        + E(rt['reason'])))
    return ('<section class="credit-record" id="ed-' + E(e['id']) + '"><h3><a href="/work/' + E(w['id']) + '/">' + E(w['title']) + '</a>, '
            + E(w['author']) + '</h3><p class="small muted">' + E(e['label']) + ' (' + E(e['id']) + ')</p><dl class="credit-fields">'
            + ''.join('<dt>' + k + '</dt><dd>' + v + '</dd>' for k, v in rows if v) + '</dl></section>')


def portrait_entries(hub):
    """Every credited portrait an author page shows (app.js portraitOk(a,1): an image and a credit)."""
    return [a for a in hub['authors'] if a.get('img') and a.get('imgCredit')]


def portrait_entry(a):
    c = a['imgCredit']
    lic = ext(c['licenseUrl'], E(c['license'])) if c.get('licenseUrl') else E(c['license'])
    src = 'Wikimedia Commons' if 'commons.wikimedia.org' in c['page'] else 'Wikipedia'
    return ('<li id="portrait-' + E(a['id']) + '"><a href="/author/' + E(a['id']) + '/">' + E(a['name']) + '</a>: portrait'
            + (' by ' + E(c['artist']) if c.get('artist') else '') + ', ' + lic + ', via ' + ext(c['page'], src) + '.</li>')


def wiki_url(a):
    return next((l['url'] for l in a.get('links') or [] if 'wikipedia.org/wiki/' in l.get('url', '')), None)


def wiki_entries(hub, hosted_authors):
    """Every author page that shows a Wikipedia excerpt (authors with a hosted work; tools/build_static.py and app.js)."""
    return [a for a in hub['authors'] if a['id'] in hosted_authors and a.get('extract')
            and a['extract'] not in (a.get('desc') or a.get('wikiDesc') or '')]


def wiki_entry(a):
    wk = wiki_url(a)
    wt = urllib.parse.unquote(wk.split('/wiki/')[1]).replace('_', ' ') if wk else a['name']
    return ('<li id="wiki-' + E(a['id']) + '"><a href="/author/' + E(a['id']) + '/">' + E(a['name']) + '</a>: the excerpt is from Wikipedia, '
            + (ext(wk, '“' + E(wt) + '”') if wk else '“' + E(wt) + '”') + ' (shortened), ' + ext(CC_BY_SA, 'CC BY-SA 4.0') + '.</li>')


def hosted_authors(lib):
    return {w['authorId'] for w in lib['works'] if w.get('authorId') and any(e.get('text') for e in w['editions'])}


ART_LABELS = (('library', 'Reading room'), ('magisterium', 'Church Documents'), ('councils', 'Councils'), ('saints', 'Saints'),
              ('summa', 'Summa'))  # section-header engravings (tools/site_copy.py PAGE_ART)


def page_html(lib, hub, hero_credit):
    import site_copy
    libw = {w['id']: w for w in lib['works']}
    books = [(w, e) for w in sorted(lib['works'], key=lambda w: (w['title'].lower(), w['id'])) for e in w['editions'] if e.get('text')]
    P = portrait_entries(hub)
    W = wiki_entries(hub, hosted_authors(lib))
    return ('<div class="page-head"><div class="eyebrow">Bibliotheca Catholica</div><h1>Sources and credits</h1>'
            '<p class="lede">Where every hosted book, portrait, and excerpt comes from, and why each may be shown here.</p></div>'
            '<p>Each reading page ends with a short colophon and each author page with small credit links. They point to the full '
            'record on this page. How rights are decided is on ' + '<a href="/rights/">Rights &amp; Permissions</a>' + '; the site’s own '
            'licences are on <a href="/licensing/">Licensing &amp; credits</a>. To report a problem with a credit or a text, use '
            '<a href="/takedown/">Takedown requests</a>.</p>'
            '<nav class="credits-toc" aria-label="On this page"><a href="#books">Books (' + str(len(books)) + ')</a> · <a href="#portraits">Portraits ('
            + str(len(P)) + ')</a> · <a href="#wikipedia">Wikipedia excerpts (' + str(len(W)) + ')</a> · <a href="#images">Other images</a></nav>'
            '<h2 id="books">Books</h2><p>Every hosted edition, including retired editions kept for earlier links. A SHA-256 identifies the exact file served.</p>'
            + ''.join(book_record(w, e, libw) for w, e in books)
            + '<h2 id="portraits">Portraits</h2><ul class="credit-list">' + ''.join(portrait_entry(a) for a in P) + '</ul>'
            + '<h2 id="wikipedia">Wikipedia excerpts</h2><p>These excerpts are shortened from Wikipedia and shared under CC BY-SA 4.0; they are '
            'not covered by the site’s own licences.</p><ul class="credit-list">' + ''.join(wiki_entry(a) for a in W) + '</ul>'
            + '<h2 id="images">Other images</h2><ul class="credit-list"><li id="home-engraving">Home page engraving: ' + hero_credit + '</li>'
            + ''.join('<li id="art-' + k + '">' + label + ' engraving: ' + site_copy.art_credit(k) + '</li>' for k, label in ART_LABELS)
            + '<li>Book covers are Bibliotheca Catholica’s own typographic designs, with no third-party art.</li></ul>')
