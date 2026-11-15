#!/usr/bin/env python3
"""EPUBs of the hosted editions that have a structure file (tools/structure_text.py): an EPUB 3 built from the hosted
TXT and the structured-text intermediate file.

Published (Micah, November 15, 2026: "Publish our EPUB file"): `--publish` (part of `npm run build`) writes each one to
downloads/epub/<work>-<edition>.<sha256[:12]>.epub, a content-hashed name, with data/epubs.json and data/epubs.js
(path, sha256, size). The work page links it as "EPUB (this edition)". CI also builds a review copy into epub-review/
and runs EPUBCheck on both. Entries are stored uncompressed, so the bytes do not depend on the zlib version.

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
from notices import PG_LINE, SE_NOTICE  # noqa: E402

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
.cover{text-align:center;margin:0}.cover img{max-width:100%;max-height:100%}
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
    tp = json.loads((ROOT / 'data/text-pages.json').read_text())['works'].get(work)
    TITLES = {x['heading']: x['title'] for x in tp['items']} if tp else {}  # the site's chapter titles where it has chapter pages
    pg = re.search(r'gutenberg\.org/ebooks/(\d+)', e['source'])

    docs = []  # (id, file, title, xhtml, blocks it carries)
    # The edition cover (design C, chosen by Micah on November 15, 2026; tools/covers.py), first in the book.
    cover = (ROOT / 'assets/covers' / (edition + '.webp')).read_bytes()
    docs.append(('cover', 'cover.xhtml', 'Cover', xhtml('Cover', '<section epub:type="cover" class="cover"><img src="cover.webp" alt="Cover of '
                 + E(w['title']) + ' by ' + E(w['author']) + '"/></section>'), []))
    first_ch = S['chapters'][0]['heading']
    moved = (S.get('presentation') or {}).get('front', [])  # step 2b: e.g. the proofreader's credit, with the notices
    front = [i for i in range(lo, first_ch) if i not in moved]
    docs.append(('front', 'front.xhtml', w['title'],
                 xhtml(w['title'], '<section epub:type="frontmatter">' + ''.join(to_xml(reading_block(e, B[i], i)) for i in front) + '</section>'), front))
    for n, c in enumerate(S['chapters']):
        ids = list(range(c['start'], c['end'] + 1))
        title = c['num'] + '. ' + TITLES.get(c['heading'], c['title'])
        body = ('<section epub:type="chapter" aria-labelledby="h"><h2 id="h">' + E(title) + '</h2>'
                + ''.join(to_xml(reading_block(e, B[i], i)) for i in ids) + '</section>')
        docs.append(('ch%02d' % (n + 1), 'ch%02d.xhtml' % (n + 1), title, xhtml(title, body), ids))
    back = list(range(S['chapters'][-1]['end'] + 1, hi + 1))
    if back:  # what follows the last chapter (Story of a Soul: the epilogue, counsels, letters, prayers, and poems)
        docs.append(('back', 'back.xhtml', 'After the last chapter', xhtml(w['title'], '<section epub:type="backmatter">'
                     + ''.join(to_xml(reading_block(e, B[i], i)) for i in back) + '</section>'), back))
    end_notice = (PG_LINE.replace(' target="_blank" rel="noopener"', '') if pg
                  else E(SE_NOTICE) if 'standardebooks.org' in e['source'] else '')
    if end_notice:  # rule 2: the source's own notice once, at the end of the text (Gutenberg: the 1.E.1 sentence verbatim)
        did, fn, t, doc, ids = docs[-1]
        doc = doc.replace('</section></body>', '<div class="pg-line">' + end_notice + '</div></section></body>')
        docs[-1] = (did, fn, t, doc, ids)

    # The source's header and license, verbatim (content rule 2)
    head = B[:lo]
    tail = B[hi + 1:]
    label = 'Project Gutenberg eBook #' + pg.group(1) if pg else e['label']
    notice = ('<section class="notice" epub:type="appendix"><h1>Source notice and license</h1>'
              '<p>This edition reproduces ' + E(label) + '. Its header' + (', the transcriber\'s credit,' if moved else '') + ' and the full license follow exactly as in the source file.</p>'
              + ''.join('<pre>' + E(b) + '</pre>' for b in head + [B[i] for i in moved] + tail) + '</section>')
    docs.append(('notice', 'notice.xhtml', 'Source notice and license', xhtml('Source notice and license', notice), []))
    f = e.get('readerFormatting')
    colophon = ('<section class="colophon"><h1>About this edition</h1>'
                '<p>' + E(w['author']) + ', <i>' + E(w['title']) + '</i>. ' + E(e['label']) + '. Source: ' + E(e['source']) + '.</p>'
                '<p>' + E(e['rights']) + '</p>'
                '<p>Prepared by Bibliotheca Catholica from the hosted text (SHA-256 ' + e['sha256'] + '), with '
                + ('divisions from the site\'s map of the hosted text' if S['gate'].get('mode') == 'map'
                   else 'chapter structure from Project Gutenberg\'s HTML for the same eBook, matched word for word with the hosted text')
                + '. No words were changed.</p>'
                + ('<p>' + E(f['note']) + ' Witness: ' + E(f['evidence']) + '.</p>' if f and f.get('sha256') == e['sha256'] else '')
                + '<p>Published by Bibliotheca Catholica, bibliothecacatholica.com.</p></section>')
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
           '<dc:publisher>Bibliotheca Catholica</dc:publisher>'
           '<meta property="dcterms:modified">2026-11-14T00:00:00Z</meta></metadata><manifest>'
           '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
           '<item id="css" href="style.css" media-type="text/css"/>'
           '<item id="cover-image" href="cover.webp" media-type="image/webp" properties="cover-image"/>'
           + ''.join('<item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (did, fn) for did, fn, t, d, i in docs)
           + '</manifest><spine>' + ''.join('<itemref idref="%s"/>' % did for did, fn, t, d, i in docs) + '</spine></package>\n')
    ET.fromstring(opf.encode('utf-8'))
    container = ('<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>\n')

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        def put(name, data, store=False):
            zi = zipfile.ZipInfo(name, STAMP)
            zi.compress_type = zipfile.ZIP_STORED  # stored: identical bytes whatever the zlib version (local and CI)
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data)
        put('mimetype', 'application/epub+zip', store=True)  # first and uncompressed (OCF)
        put('META-INF/container.xml', container)
        put('OEBPS/content.opf', opf)
        put('OEBPS/nav.xhtml', navdoc)
        put('OEBPS/style.css', CSS)
        put('OEBPS/cover.webp', cover, store=True)
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


def publish():
    """Build every structured edition's EPUB into downloads/epub/ under a content-hashed name, with a manifest."""
    import shutil, tempfile
    out = ROOT / 'downloads/epub'
    out.mkdir(parents=True, exist_ok=True)
    rows, keep = {}, set()
    with tempfile.TemporaryDirectory() as tmp:
        for (work, edition) in sorted(ST.EDITIONS):
            r = build(work, edition, Path(tmp))
            name = '%s-%s.%s.epub' % (work, edition, r['sha256'][:12])
            shutil.copyfile(Path(tmp) / ('%s-%s.epub' % (work, edition)), out / name)
            keep.add(name)
            rows[edition] = {'work': work, 'path': 'downloads/epub/' + name, 'sha256': r['sha256'], 'size': r['bytes']}
    for p in out.glob('*.epub'):
        if p.name not in keep:
            p.unlink()
    m = {'note': 'Generated by tools/build_epub.py --publish. EPUB 3 files of the hosted editions with a structure file; '
                 'every character of the text comes from the hosted TXT. Published by decision of Micah, November 15, 2026.',
         'epubs': rows}
    (ROOT / 'data/epubs.json').write_text(json.dumps(m, indent=1) + '\n')
    (ROOT / 'data/epubs.js').write_text('window.EPUBS=' + json.dumps({k: {'path': v['path'], 'size': v['size']} for k, v in rows.items()}, separators=(',', ':')) + ';\n')
    return m


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT / '.epub-build'))
    ap.add_argument('--publish', action='store_true')
    a = ap.parse_args()
    if a.publish:
        m = publish()
        print('published EPUBs: ' + ', '.join('%s %d bytes' % (k, v['size']) for k, v in m['epubs'].items()))
        raise SystemExit(0)
    r = build(out_dir=Path(a.out))
    print('%s: %d bytes, sha256 %s, %d chapters, %d book blocks' % (r['file'], r['bytes'], r['sha256'], r['chapters'], r['bookBlocks']))
