#!/usr/bin/env python3
"""Import a public-domain text that a source serves as a series of HTML pages (network; not part of `npm run build`).

First use (November 20, 2026): Waterworth's Council of Trent (London: Dolman, 1848) as Papal Encyclicals Online serves
the Hanover Historical Texts Project transcription, one page per session (owner-approved councils sources table,
docs/research/councils-sources-2026-11.csv; texts may come from any source, docs/PROJECT-RULES.md rule 1).

    python3 tools/import_html_pages.py SPEC.json

SPEC is a list of {edition, pages: [url, ...], sourcePage, sourceName, sourceTitle, title, author, year, firstPublished,
ia, siteNotice, format?, scanFrom?, scanTo?}, the fields of tools/import_plain_text.py plus the page list. `format` names
the page layout (FORMATS): `entry-content` (the default, Papal Encyclicals Online) or `ebible` (eBible.org's chapter
pages, first used November 21, 2026 for the Douay-Rheims books of Wisdom and Ecclesiasticus). For each entry the tool:
  1. downloads every page in order and pins its exact bytes, gzipped deterministically, in
     data/sources/html-pages/<edition>/<NN>.html.gz, with each page's URL and SHA-256 in the source record;
  2. takes from each page only its own title (the `<h1>`) and the article body (`entry-content`), drops the site's
     menus, and turns block tags into line breaks (`extract()`, re-run by tests/test_import_html_pages.py against the
     pinned pages). No word is changed, added, or dropped: the source's page markers, notes, and spellings stay;
  3. hands the joined text to tools/import_plain_text.py for the dated scan comparison (95% agreement) and the hosted
     text and source record, and scores it with the read gate of tools/transcribe_scan.py (99.5%). It writes nothing
     below either floor.
"""
import gzip, hashlib, html, io, json, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import import_plain_text as I  # noqa: E402

READ_GATE, AGREEMENT = 0.995, 0.95
BLOCK = re.compile(r'</?(?:p|h\d|center|address|div|li|ul|ol|blockquote|table|tr)\b[^>]*>|<(?:br|hr)\b[^>]*>')


def extract(raw):
    """One page's title and article body as plain text: block tags become line breaks, runs of spaces one space,
    and blank lines one blank line (a paragraph break). Nothing else changes."""
    s = raw.decode('utf-8')
    title = html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1)).strip()
    body = re.search(r'<div class="entry-content[^"]*"[^>]*>(.*?)</div><!-- .entry-content -->', s, re.S).group(1)
    body = re.sub(r'<!-- UberMenu.*?</nav>|<nav\b.*?</nav>', '', body, flags=re.S)  # the site's session menu
    t = html.unescape(re.sub(r'<[^>]+>', '', BLOCK.sub('\n', body))).replace('\r', '')
    out = [title, '']
    for line in (re.sub(r'[ \t\xa0]+', ' ', x).strip() for x in t.split('\n')):
        if line:
            out.append(line)
        elif out[-1] != '':
            out.append('')
    return '\n'.join(out).strip('\n')


def extract_ebible(raw):
    """One eBible.org chapter page (for example https://ebible.org/engDRA/WIS08.htm) as plain text: the book's own title
    lines where the page prints them (first chapter only), then a heading of the book name from the page's navigation and
    the chapter number, then one paragraph per verse, each starting with its number. Words are kept as served; the site's
    navigation, the empty footnote block, and the "Public Domain" footer link are dropped."""
    s = raw.decode('utf-8-sig')
    book = html.unescape(re.search(r"<li><a href='index\.htm'>(.*?)</a></li>", s).group(1)).strip()
    main = re.search(r'<div class="main">(.*?)</div><ul class=\'tnav\'>', s, re.S).group(1)
    clean = lambda x: re.sub(r'[ \t\xa0\n]+', ' ', html.unescape(re.sub(r'<[^>]+>', '', x))).strip()
    title = [clean(t) for t in re.findall(r"<div class='mt2?'>(.*?)</div>", main, re.S)]
    out = ['\n'.join(title)] if title else []
    out.append(book + ' ' + clean(re.search(r"<div class='chapterlabel'[^>]*>(.*?)</div>", main, re.S).group(1)))
    body = main[main.index("<div class='p'>"):]
    for n, verse in re.findall(r'<span class="verse" id="V\d+">(\d+)&#160;</span>(.*?)(?=<span class="verse"|$)', body, re.S):
        out.append(n + ' ' + clean(verse))
    return '\n\n'.join(out)  # one paragraph per verse, so each verse has its own place in the reader


FORMATS = {'entry-content': extract, 'ebible': extract_ebible}


def pinned(edition):
    """The pinned pages of an edition, in order: [(path, raw bytes)]."""
    d = ROOT / 'data/sources/html-pages' / edition
    return [(p, gzip.decompress(p.read_bytes())) for p in sorted(d.glob('*.html.gz'))]


def joined(raws, fmt='entry-content'):
    return '\n\n'.join(FORMATS[fmt](r) for r in raws)


def gz(raw):
    b = io.BytesIO()
    with gzip.GzipFile(fileobj=b, mode='wb', mtime=0, filename='') as f:
        f.write(raw)
    return b.getvalue()


def main(spec_path):
    import import_pdf_print as P
    for e in json.loads(Path(spec_path).read_text()):
        out, basis = I.check_basis(e)
        raws, pages = [], []
        d = ROOT / 'data/sources/html-pages' / e['edition']
        d.mkdir(parents=True, exist_ok=True)
        for n, url in enumerate(e['pages'], 1):
            raw = I.get(url); raws.append(raw)
            f = d / f'{n:02d}.html.gz'
            f.write_bytes(gz(raw))
            pages.append({'url': url, 'sha256': hashlib.sha256(raw).hexdigest(), 'file': str(f.relative_to(ROOT))})
            time.sleep(1)
        fmt = e.get('format', 'entry-content')
        text = joined(raws, fmt)
        r = P.read_rate(text)
        if r['readRate'] < READ_GATE:
            sys.exit(f"{e['edition']}: read rate {r['readRate']:.2%} is below the gate; nothing hosted")
        witness, col = I.scan_witness(e, text, basis)
        if col['agreement'] < AGREEMENT:
            sys.exit(f"{e['edition']}: {col['agreement']:.1%} agreement with {e['ia']} is below 95%; nothing hosted")
        I.host(e, b''.join(raws), text, basis, out, witness, col,
               converted='Extracted from the pages\' HTML as plain text (tools/import_html_pages.py)',
               extra={'sourcePages': pages, 'sourceFileNote': 'sourceFileSha256 is the SHA-256 of the pages\' bytes '
                      'joined in order; each page is pinned in sourcePages', 'siteNotice': e['siteNotice'],
                      'readGate': {k: r[k] for k in ('words', 'unknown', 'readRate', 'gate')},
                      'readGateUnknownWords': r['unknownWords'],
                      **({'sourceFormat': fmt} if fmt != 'entry-content' else {}),
                      **({'secondWitnesses': e['secondWitnesses']} if e.get('secondWitnesses') else {})})


if __name__ == '__main__':
    main(sys.argv[1])
