#!/usr/bin/env python3
"""Rebuild a public-domain plain text from a browser's PDF print of its source page (owner-supplied; November 20, 2026).

Project Gutenberg Australia serves a JavaScript bot check, so tools/import_plain_text.py cannot fetch its pages. The
owner printed three of them to PDF in Safari (data/sources/pdf-prints/). This tool turns such a print back into the
source's own text and changes no words:
  * reads each line's position with `pdftotext -bbox-layout` (poppler) and drops the browser's running head (the page
    title and the print date) and foot (the page URL and "Page N of M") on every page;
  * keeps the source's paragraphs: a paragraph ends where the vertical gap between two lines is wider than the line
    spacing, and across a page turn only where the last line on the page stops well short of the measure and ends a
    sentence (an HTML page in a browser print has no other page breaks);
  * keeps every hyphen as printed. A browser does not hyphenate an HTML page, so a hyphen at the end of a line is
    the source's own (a compound such as witch-burning): the next line is joined without a space and the hyphen
    stays. (`pdftotext` without `-bbox-layout` drops those hyphens; never use its plain output.)
  * keeps the source's header, notices, and every line of its text; the words themselves are taken exactly as the
    PDF's text layer gives them (no OCR, no repair).
It then scores the text against the read gate the scanned transcriptions use (tools/transcribe_scan.py: the share of
words that are known words of the library's hosted texts or that occur in this book at least twice, as names do;
99.5% to host) and lists the unknown words for review.

    python3 tools/import_pdf_print.py SPEC.json --stage DIR     # rebuild and score only; writes DIR/<edition>.txt
    python3 tools/import_pdf_print.py SPEC.json --host          # network: archive.org scan comparison, then the
                                                                # tools/import_plain_text.py record and hosted text
                                                                # (entries without `ia` are skipped, not hosted)

SPEC is a list of {edition, pdf, sourceUrl, sourcePage, sourceName, sourceTitle, title, author, year, firstPublished,
firstPublishedEvidence, ia?}. `--host` skips an entry without `ia` (a dated Internet Archive scan of a printing that is
public domain in the US by date), exactly as tools/import_plain_text.py does: the comparison is the gate that shows the
source is the book it claims to be (95% agreement, tests/test_imported_texts.py).
"""
import argparse, collections, hashlib, html, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from rights_rule import pd_by_date  # noqa: E402

READ_GATE = 0.995
AGREEMENT = 0.95  # the scan comparison's floor (tests/test_imported_texts.py)
WORD = re.compile(r"[A-Za-z][A-Za-z'’]*")


def lines_of(pdf):
    """[(page, xMin, yMin, xMax, text)] for every line of the print, in reading order."""
    xml = subprocess.run(['pdftotext', '-bbox-layout', str(pdf), '-'], capture_output=True, check=True).stdout.decode('utf-8')
    out = []
    for pn, page in enumerate(re.findall(r'<page [^>]*>(.*?)</page>', xml, re.S), 1):
        for m in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="[\d.]+">(.*?)</line>', page, re.S):
            words = [html.unescape(w) for w in re.findall(r'<word [^>]*>(.*?)</word>', m.group(4), re.S)]
            out.append((pn, float(m.group(1)), float(m.group(2)), float(m.group(3)), ' '.join(words)))
    return out


def body_lines(lines, title):
    """Drops the browser's running head and foot: the first two lines of each page when they are the page title and
    a print date, and the last two when they are the page URL and "Page N of M"."""
    pages = collections.defaultdict(list)
    for ln in lines:
        pages[ln[0]].append(ln)
    out = []
    for pn in sorted(pages):
        L = pages[pn]
        if len(L) >= 2 and L[0][4] == title and re.fullmatch(r'\d{1,2}/\d{1,2}/\d{2},? \d{1,2}:\d{2} [AP]M', L[1][4]):
            L = L[2:]
        if len(L) >= 2 and L[-1][4].startswith('Page ') and re.fullmatch(r'Page \d+ of \d+', L[-1][4]) and L[-2][4].startswith('https://'):
            L = L[:-2]
        out += L
    return out


def paragraphs(L):
    """Groups body lines into the source's paragraphs (see the module docstring); returns a list of lists of lines."""
    gaps = sorted(round(b[2] - a[2], 1) for a, b in zip(L, L[1:]) if a[0] == b[0] and 0 < b[2] - a[2] < 40)
    step = collections.Counter(gaps).most_common(1)[0][0] if gaps else 18.0
    measure = max(ln[3] for ln in L) if L else 0
    paras, cur = [], []
    for i, ln in enumerate(L):
        if cur:
            prev = cur[-1]
            if ln[0] == prev[0]:
                new = ln[2] - prev[2] > step * 1.45
            else:  # page turn: a new paragraph only after a short line that ends a sentence, before a line that
                # does not start in lower case ("... that C." / "underwent a change" is one sentence)
                new = (prev[3] < measure - 60 and re.search(r'[.!?:”"’)\]]$', prev[4]) is not None
                       and not ln[4][:1].islower())
            if new:
                paras.append(cur); cur = []
        cur.append(ln)
    if cur:
        paras.append(cur)
    return paras


def join_lines(par):
    """One paragraph's lines as the source has them: hyphens kept, and lines kept as printed (a hard line break
    for verse and set-out lines; wrapped prose reflows on the site through the automatic layout)."""
    texts = [ln[4] for ln in par]
    out = [texts[0]]
    for t in texts[1:]:
        if out[-1].endswith('-') and not out[-1].endswith(' -') and t[:1].isalpha():
            out[-1] = out[-1] + t  # the source's own hyphen; the browser does not hyphenate
        else:
            out.append(t)
    return '\n'.join(out)


def rebuild(pdf, title):
    L = body_lines(lines_of(pdf), title)
    return '\n\n'.join(join_lines(p) for p in paragraphs(L)) + '\n'


def read_rate(text):
    """The read gate of tools/transcribe_scan.py, applied to the text below the source's header."""
    import transcribe_scan
    V = transcribe_scan.vocabulary()
    words = [w.strip("'’") for w in WORD.findall(text)]
    counts = collections.Counter(w.lower() for w in words)
    unknown = [w for w in words if not transcribe_scan.known(w, V) and counts[w.lower()] < 2]
    return {'words': len(words), 'unknown': len(unknown), 'readRate': round(1 - len(unknown) / max(1, len(words)), 4),
            'unknownWords': sorted(set(unknown))[:200], 'gate': READ_GATE,
            'method': 'share of words that are known words of the hosted texts (tools/transcribe_scan.py) or occur at least twice in this text'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec'); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--stage'); g.add_argument('--host', action='store_true')
    a = ap.parse_args()
    for e in json.loads(Path(a.spec).read_text()):
        assert pd_by_date(e['year']), (e['edition'], 'public domain in the US by date only')
        pdf = ROOT / e['pdf']
        text = rebuild(pdf, e['pdfTitle'])
        sha_pdf = hashlib.sha256(pdf.read_bytes()).hexdigest()
        assert sha_pdf == e['pdfSha256'], (e['edition'], 'the PDF is not the pinned print')
        body = text[text.index(e['bodyStartsWith']):] if e.get('bodyStartsWith') else text
        r = read_rate(body)
        if a.stage:
            d = Path(a.stage); d.mkdir(parents=True, exist_ok=True)
            (d / f"{e['edition']}.txt").write_text(text)
            (d / f"{e['edition']}.read.json").write_text(json.dumps(r, ensure_ascii=False, indent=1) + '\n')
            print(e['edition'], f"{r['words']} words, read rate {r['readRate']:.2%} ({r['unknown']} unknown)",
                  'passes' if r['readRate'] >= READ_GATE else 'BELOW THE GATE', f"pdf {sha_pdf[:12]}")
        else:
            host(e, pdf, text, sha_pdf, r)


def host(e, pdf, text, sha_pdf, r):
    """Hosts one rebuilt text through tools/import_plain_text.py: the dated scan comparison, then the hosted text and
    its source record. Refuses (and writes nothing) without `ia`, below the read gate, or below 95% agreement."""
    import import_plain_text as I
    if (ROOT / f"data/texts/{e['edition']}.txt").exists():
        print(e['edition'], 'already hosted; a pinned text never changes'); return
    if not e.get('ia') and not e.get('scanException'):
        print(e['edition'], 'NOT HOSTED: no dated Internet Archive scan (`ia`) to compare with'); return
    if r['readRate'] < READ_GATE:
        print(e['edition'], f"NOT HOSTED: read rate {r['readRate']:.2%} is below the gate"); return
    out, basis = I.check_basis(e)
    body = text.strip('\n')
    if not e.get('ia'):  # the owner-approved exception: hosted without a comparison, the exception recorded
        assert basis == 'pd-date' and str(e['scanException']['yearInText']) in body, e['edition']
        witness, col = None, None
    else:
        witness, col = I.scan_witness(e, body, basis)
    if col and col['agreement'] < AGREEMENT:
        print(e['edition'], f"NOT HOSTED: {col['agreement']:.1%} agreement with {e['ia']} is below {AGREEMENT:.0%}"); return
    I.host(e, pdf.read_bytes(), body, basis, out, witness, col,
           converted="Rebuilt from a browser's PDF print of the source page (tools/import_pdf_print.py)",
           extra={'sourceFile': e['pdf'], 'sourceFileNote': "sourceFileSha256 is the SHA-256 of the pinned PDF print "
                  "of the source page; the source's own server serves a bot check", 'readGate': {k: r[k] for k in (
                      'words', 'unknown', 'readRate', 'gate')}})


if __name__ == '__main__':
    main()
