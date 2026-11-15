#!/usr/bin/env python3
"""EPUB pilot (Orthodoxy, PR #24): an EPUB 3 built from the hosted TXT and the structured-text intermediate file.

Not published and not linked from the site: CI uploads it as a pull-request artifact for review only. Output
defaults to .epub-build/ (git-ignored), never to a served path.

Fidelity:
  * Every character of the book comes from the hosted TXT (data/texts/), rendered by the same block renderer as the
    reader and chapter pages (tools/reader_formatting.py reading_block), so the scan-verified Chapter IV verse and
    emphasis are carried over and nothing else is inferred. Hard line wraps inside a paragraph render as ordinary
    XHTML whitespace; the TXT is unchanged.
  * The Project Gutenberg header and the full license (the TXT blocks before START and after END) are included
    verbatim, as the content rules require for downloaded texts.
  * Before writing, the text of each chapter document is extracted again and compared with the TXT blocks
    (whitespace-normalized): any difference fails the build. Every XHTML document must parse as XML.
  * Deterministic: fixed timestamps and order, so the same inputs give the same SHA-256.

  python3 tools/build_epub.py [--out DIR]
"""
import argparse, hashlib, html, io, json, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from reader_formatting import reading_block, with_structure  # noqa: E402
import structure_text as ST  # noqa: E402
from notices import PG_LINE  # noqa: E402

E = html.escape
STAMP = (2026, 11, 14, 0, 0, 0)
CSS = """body{font-family:serif;line-height:1.55;margin:0 1em}
h1,h2{font-weight:normal;text-align:center;line-height:1.25}
h1{font-size:1.8em;margin:2em 0 .4em}h2{font-size:1.25em;margin:2.5em 0 1.2em;font-variant:small-caps;letter-spacing:.04em}
p{margin:0 0 .9em;text-indent:0}
.reading-title{text-align:center;font-size:1.6em;margin:2em 0 .3em}
.reading-byline,.reading-heading{text-align:center;font-variant:small-caps;letter-spacing:.06em;margin:1.4em 0 .6em}
.reading-chapter{display:none}
.reading-contents{white-space:pre-line}
.reading-verse{margin-left:1.5em}.verse-line{display:block}
.notice p,.notice pre{font-size:.85em}.notice pre{white-space:pre-wrap;font-family:serif}
.colophon{font-size:.85em}
.pg-line{font-size:.8em;margin-top:2em}
"""


def xhtml(title, body, lang='en'):
    return ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="%s" xml:lang="%s">'
            '<head><meta charset="utf-8"/><title>%s</title><link rel="stylesheet" type="text/css" href="style.css"/></head>'
            '<body>%s</body></html>\n' % (lang, lang, E(title), body))


def to_xml(fragment):
    """reading_block() writes HTML; make the two HTML-only spellings XML-safe (no text changes)."""
    return fragment.replace('&#x27;', '&#39;')


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def build(work='orthodoxy', edition='pg-130', out_dir=ROOT / '.epub-build'):
    lib = json.loads((ROOT / 'data/library.json').read_text())
    w = next(x for x in lib['works'] if x['id'] == work)
    e = with_structure(next(x for x in w['editions'] if x['id'] == edition))
    S = json.loads((ROOT / ST.EDITIONS[(work, edition)]['out']).read_text())
    raw = (ROOT / e['text']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == e['sha256'] == S['txt']['sha256'], 'TXT changed since the structure was built'
    assert S['gate']['passed'], 'structure gate did not pass'
    B = ST.txt_blocks(e['text'])
    lo, hi = S['txt']['bodyStart'], S['txt']['bodyEnd']
    TITLES = {x['heading']: x['title'] for x in json.loads((ROOT / 'data/text-pages.json').read_text())['works'][work]['items']}

    docs = []  # (id, file, title, xhtml, blocks it carries)
    first_ch = S['chapters'][0]['heading']
    moved = (S.get('presentation') or {}).get('front', [])  # step 2b: e.g. the proofreader's credit, with the notices
    front = [i for i in range(lo, first_ch) if i not in moved]
    docs.append(('front', 'front.xhtml', w['title'],
                 xhtml(w['title'], '<section epub:type="frontmatter">' + ''.join(to_xml(reading_block(e, B[i], i)) for i in front) + '</section>'), front))
    for n, c in enumerate(S['chapters']):
        ids = list(range(c['start'], c['end'] + 1))
        title = c['num'] + '. ' + TITLES[c['heading']]  # the site's chapter titles (data/text-pages.json)
        body = ('<section epub:type="chapter" aria-labelledby="h"><h2 id="h">' + E(title) + '</h2>'
                + ''.join(to_xml(reading_block(e, B[i], i)) for i in ids) + '</section>')
        if n == len(S['chapters']) - 1:  # rule 2: the licence's own 1.E.1 sentence once, at the end of the text
            body = body[:-len('</section>')] + '<div class="pg-line">' + PG_LINE.replace(' target="_blank" rel="noopener"', '') + '</div></section>'
        docs.append(('ch%02d' % (n + 1), 'ch%02d.xhtml' % (n + 1), title, xhtml(title, body), ids))

    # Gutenberg header and license, verbatim (content rule 2)
    head = B[:lo]
    tail = B[hi + 1:]
    notice = ('<section class="notice" epub:type="appendix"><h1>Project Gutenberg notice and license</h1>'
              '<p>This edition reproduces Project Gutenberg eBook #130. Its header, the transcriber\'s credit, and the full license follow exactly as in the source file.</p>'
              + ''.join('<pre>' + E(b) + '</pre>' for b in head + [B[i] for i in moved] + tail) + '</section>')
    docs.append(('notice', 'notice.xhtml', 'Project Gutenberg notice and license', xhtml('Project Gutenberg notice and license', notice), []))
    colophon = ('<section class="colophon"><h1>About this edition</h1>'
                '<p>' + E(w['author']) + ', <i>' + E(w['title']) + '</i>. ' + E(e['label']) + '. Source: ' + E(e['source']) + '.</p>'
                '<p>' + E(e['rights']) + '</p>'
                '<p>Prepared by Bibliotheca Catholica from the hosted text (SHA-256 ' + e['sha256'] + '), with chapter structure from '
                'Project Gutenberg\'s HTML for the same eBook. No words were changed. Chapter IV\'s two italicized words and two-line '
                'quotation follow page 99 of the 1909 John Lane Company printing: ' + E(e['readerFormatting']['evidence']) + '.</p>'
                '<p>Review copy for the structured-text pilot; not published.</p></section>')
    docs.append(('colophon', 'colophon.xhtml', 'About this edition', xhtml('About this edition', colophon), []))

    # Fidelity: every carried block's text, extracted from the XHTML, equals the TXT block.
    for did, fn, title, doc, ids in docs:
        root = ET.fromstring(doc.encode('utf-8'))  # well-formed XML or fail
        if ids:
            got = [norm(''.join(p.itertext())) for p in root.iter('{http://www.w3.org/1999/xhtml}p')]
            assert got == [norm(B[i]) for i in ids], 'text differs in ' + fn

    nav = ('<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>'
           + ''.join('<li><a href="%s">%s</a></li>' % (fn, E(t)) for did, fn, t, doc, ids in docs) + '</ol></nav>')
    navdoc = xhtml('Contents', nav)
    ET.fromstring(navdoc.encode('utf-8'))
    uid = 'urn:bibliotheca-catholica:%s:%s:%s' % (work, edition, e['sha256'][:12])
    opf = ('<?xml version="1.0" encoding="utf-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="en">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           '<dc:identifier id="uid">' + uid + '</dc:identifier><dc:title>' + E(w['title']) + '</dc:title>'
           '<dc:creator>' + E(w['author']) + '</dc:creator><dc:language>en</dc:language>'
           '<dc:source>' + E(e['source']) + '</dc:source><dc:rights>' + E(e['rights']) + '</dc:rights>'
           '<dc:publisher>Bibliotheca Catholica (review copy, not published)</dc:publisher>'
           '<meta property="dcterms:modified">2026-11-14T00:00:00Z</meta></metadata><manifest>'
           '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
           '<item id="css" href="style.css" media-type="text/css"/>'
           + ''.join('<item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (did, fn) for did, fn, t, d, i in docs)
           + '</manifest><spine>' + ''.join('<itemref idref="%s"/>' % did for did, fn, t, d, i in docs) + '</spine></package>\n')
    ET.fromstring(opf.encode('utf-8'))
    container = ('<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>\n')

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        def put(name, data, store=False):
            zi = zipfile.ZipInfo(name, STAMP)
            zi.compress_type = zipfile.ZIP_STORED if store else zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data)
        put('mimetype', 'application/epub+zip', store=True)  # first and uncompressed (OCF)
        put('META-INF/container.xml', container)
        put('OEBPS/content.opf', opf)
        put('OEBPS/nav.xhtml', navdoc)
        put('OEBPS/style.css', CSS)
        for did, fn, t, doc, ids in docs:
            put('OEBPS/' + fn, doc)
    data = buf.getvalue()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / ('%s-%s.epub' % (work, edition))
    path.write_bytes(data)
    report = {'file': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), 'bytes': len(data),
              'sha256': hashlib.sha256(data).hexdigest(), 'documents': [fn for d, fn, t, x, i in docs],
              'chapters': len(S['chapters']), 'bookBlocks': sum(len(i) for d, f, t, x, i in docs)}
    (out_dir / ('%s-%s.json' % (work, edition))).write_text(json.dumps(report, indent=1) + '\n')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT / '.epub-build'))
    r = build(out_dir=Path(ap.parse_args().out))
    print('%s: %d bytes, sha256 %s, %d chapters, %d book blocks' % (r['file'], r['bytes'], r['sha256'], r['chapters'], r['bookBlocks']))
