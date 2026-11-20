#!/usr/bin/env python3
"""Import a public-domain plain text from a source other than Project Gutenberg (network; not part of `npm run build`).

First use (2026-11-15): Chesterton books of 1924 to 1930 that Project Gutenberg lacks, from Project Gutenberg
Australia and Faded Page (owner decision, November 15, 2026: texts may come from any source; the edition, not
the website, carries the rights; docs/PROJECT-RULES.md rule 1).

    python3 tools/import_plain_text.py SPEC.json

SPEC is a list of {edition, sourceUrl, sourcePage, sourceName, sourceTitle, title, author, year, firstPublished,
ia} where `ia` is an Internet Archive identifier for a scan of a printing that is public domain in the US by date.
For each entry the tool:
  1. downloads the source file and records its SHA-256 (sourceFileSha256); decodes it (UTF-8, else Windows-1252)
     and normalises line endings, changing no words; the source's own header, licence, and notices stay in place;
  2. downloads the scan's metadata and OCR (`<ia>_djvu.txt`), records the printing and the OCR's SHA-256, and
     compares the two texts word by word (case and punctuation ignored), recording the share of the source's words
     that the scan confirms and up to 40 differing passages for a reader to review. Nothing is corrected
     automatically: an OCR reading is a lead, not a fact (docs/HOSTED-EDITIONS.md rule 3);
  3. writes data/texts/<edition>.txt (a short header naming the source, its rights statement, and the comparison,
     then the source text between START and END markers) and data/sources/<edition>.json (kind
     `public-domain-text`, the shape tools/build_library.py validates).
It never edits data/library.json and never overwrites an existing hosted text.
"""
import difflib, hashlib, html, json, re, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from rights_rule import nonrenewal_problems, pd_by_date  # noqa: E402

UA = {'User-Agent': 'BibliothecaCatholica-catalog/1.0 (+https://bibliothecacatholica.com)'}
RIGHTS = 'Public domain in the USA. Outside the U.S., check local copyright rules. {name} notices retained.'


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def decode(raw):
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('cp1252')


def words(s):
    # accents are folded (é to e) so a French title is one word, not two fragments, on both sides (2026-11-15)
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", s.lower().replace('’', "'").replace("'", ''))


def collate(src, ocr):
    a, b = words(src), words(ocr)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    matched = sum(bl.size for bl in sm.get_matching_blocks())
    diffs = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'equal' and (i2 - i1) <= 6 and (j2 - j1) <= 6 and len(diffs) < 40 and i2 > i1:
            diffs.append({'source': ' '.join(a[max(0, i1 - 3):i2 + 3]), 'scan': ' '.join(b[max(0, j1 - 3):j2 + 3])})
    return {'sourceWords': len(a), 'scanWords': len(b), 'matchedWords': matched,
            'agreement': round(matched / max(1, len(a)), 4), 'sampleDifferences': diffs,
            'method': 'difflib word alignment, lower case, letters and digits only; OCR noise counts as disagreement'}


def check_basis(e):
    out = ROOT / f"data/texts/{e['edition']}.txt"
    assert not out.exists(), f"{e['edition']}: already hosted; a pinned text never changes"
    basis = e.get('rightsBasis', 'pd-date')
    if basis == 'pd-date':
        assert pd_by_date(e['year']), e['edition']
    else:  # pd-nonrenewal: the evidence must pass, and the witness scan must be the printing it names
        assert basis == 'pd-nonrenewal', basis
        assert not nonrenewal_problems(e.get('nonRenewal')), (e['edition'], nonrenewal_problems(e.get('nonRenewal')))
        assert e['nonRenewal']['scan'] == e['ia'], e['edition']
    return out, basis


def scan_witness(e, text, basis):
    """Downloads the dated scan's metadata and OCR and collates the source text with it (step 2)."""
    meta = json.loads(get(f"https://archive.org/metadata/{e['ia']}"))
    m = meta['metadata']
    ocr_name = next(f['name'] for f in meta['files'] if f['name'].endswith('_djvu.txt'))
    # archive.org/download redirects to numbered storage hosts; the /stream/ page serves the same OCR inline.
    page = decode(get(f"https://archive.org/stream/{e['ia']}/{urllib.parse.quote(ocr_name)}"))
    ocr = html.unescape(re.search(r'<pre[^>]*>(.*?)</pre>', page, re.S).group(1)).encode('utf-8')
    year = int(re.search(r'\d{4}', str(m.get('date') or m.get('year'))).group())
    assert pd_by_date(year) if basis == 'pd-date' else year == e['nonRenewal']['firstPublicationYear'], (e['ia'], year)
    col = collate(text, decode(ocr))
    witness = {'identifier': e['ia'], 'url': f"https://archive.org/details/{e['ia']}", 'year': year,
               'publisher': m.get('publisher'), 'ocr': ocr_name, 'ocrSha256': hashlib.sha256(ocr).hexdigest(),
               'ocrNote': 'SHA-256 of the OCR text as served inline by archive.org/stream/ (UTF-8)'}
    return witness, col


def host(e, raw, text, basis, out, witness, col, converted='Converted to UTF-8 plain text', extra=None):
    """Writes the hosted text and its source record (step 3). `raw` is the source file as received."""
    year, m_pub = witness['year'], witness['publisher']
    T = e['title'].upper()
    head = [T, '', f"By {e['author']}", '',
            f"First published {e['firstPublished']}. Public domain in the USA.", '',
            f"Source: {e['sourceName']} ({e['sourcePage']}), reproduced unchanged below with its own notices. "
            f"{converted} by Bibliotheca Catholica; no words were changed. Compared word by word "
            f"with the Internet Archive scan {e['ia']} ({m_pub or 'publisher not recorded'}, {year}): "
            f"{col['agreement']:.1%} of the source's words are confirmed by the scan's OCR, and the differences "
            f"are listed for review in the provenance record.", '',
            f"*** START OF THE HOSTED TEXT: {T} ***", '']
    body = '\n'.join(head) + text + f"\n\n*** END OF THE HOSTED TEXT: {T} ***\n"
    data = body.encode('utf-8')
    out.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    notice = text[:1500]
    rec = {'id': e['edition'], 'kind': 'public-domain-text', 'title': e['sourceTitle'], 'author': e['author'],
           'firstPublished': e['firstPublished'], 'rights': RIGHTS.format(name=e['sourceName']),
           'rightsBasis': basis, **({'nonRenewal': e['nonRenewal']} if basis == 'pd-nonrenewal' else {}), 'sourceName': e['sourceName'], 'sourceUrl': e['sourceUrl'],
           'sourcePage': e['sourcePage'], 'sourceNotice': notice, 'sourceFileSha256': hashlib.sha256(raw).hexdigest(),
           **(extra or {}), 'iaWitness': witness, 'collation': col, 'sha256': sha, 'bytes': len(data),
           'checked': time.strftime('%Y-%m-%d')}
    (ROOT / f"data/sources/{e['edition']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
    print(e['edition'], sha, f"agreement {col['agreement']:.1%}", f"scan {e['ia']} {year}")
    return sha


def main(spec_path):
    for e in json.loads(Path(spec_path).read_text()):
        out, basis = check_basis(e)
        raw = get(e['sourceUrl'])
        text = decode(raw).replace('\r\n', '\n').replace('\r', '\n').strip('\n')
        witness, col = scan_witness(e, text, basis)
        host(e, raw, text, basis, out, witness, col)
        time.sleep(1)


if __name__ == '__main__':
    main(sys.argv[1])
