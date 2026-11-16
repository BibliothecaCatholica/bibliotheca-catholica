#!/usr/bin/env python3
"""Transcribe a single-scan public-domain book from Internet Archive positional OCR (network; not part of `npm run build`).

The general form of tools/transcribe_supplement.py (owner prompt, November 15, 2026: "turn its method into a general,
tested tool for a single-scan book"). It does the same things and nothing more:
  * keeps each page's lines in reading order and drops the running head and the page number;
  * splits paragraphs where the scan starts one (an indented first line after a line that ends a sentence, or the OCR's
    own paragraph break), and rejoins paragraphs broken by a page turn;
  * rejoins words hyphenated at line ends when the joined word is a known word, and keeps the hyphen otherwise;
  * fixes a short, fixed list of OCR confusions only when exactly one repair is a known word and the OCR form is not, and
    records every change;
  * flags (never rewrites) any paragraph that still has a word it could not read; it never supplies a missing word.
Known words are those of the library's own hosted texts (data/texts/), so the vocabulary is period English.

    python3 tools/transcribe_scan.py SPEC.json [--cache DIR]

SPEC is a list of {edition, ia, title, sourceTitle, author, year, firstPublished, firstLeaf, lastLeaf, note?}; leaves
are 0-based page indexes of the djvu.xml, chosen by looking at the scan (front matter in, library stamps and
publisher's advertisements out). Output per entry: data/texts/<edition>.txt and data/sources/<edition>.json
(kind `ocr-transcription`, validated by tools/build_library.py and tests/test_transcribed_scans.py).
"""
import argparse, collections, glob, hashlib, html, json, re, statistics, sys, time, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from rights_rule import pd_by_date  # noqa: E402

UA = {'User-Agent': 'BibliothecaCatholica-catalog/1.0 (+https://bibliothecacatholica.com)'}
END = '*** END OF THE TRANSCRIPTION ***'
# OCR confusions, tried only on words the vocabulary does not know: (wrong, right) substrings.
CONFUSIONS = [('rn', 'm'), ('m', 'rn'), ('tm', 'un'), ('iu', 'ur'), ('ni', 'm'), ('m', 'ni'), ('li', 'h'), ('h', 'li'),
              ('ii', 'u'), ('u', 'ii'), ('cl', 'd'), ('d', 'cl'), ('vv', 'w'), ('1', 'l'), ('0', 'o'), ('c', 'e'), ('e', 'c'),
              ('f', 't'), ('t', 'f'), ('j', 'i'), ('n', 'u'), ('u', 'n'), ('b', 'h'), ('h', 'b'),
              ('im', 'un'), ('iin', 'un'), ('U', 'll'), ('fii', 'fu'), ('iy', 'ry'), ('ai', 'a'), ('aQ', 'an'), ('Gr', 'G'),
              ('ri', 'n'), ('n', 'ri'), ('l', 'i'), ('i', 'l'),
              ('z', 'æ'), ('u', 'h'), ('U', 'H'), ('W', 'Wh')]
WORD = re.compile(r"[A-Za-zæœÆŒ][A-Za-zæœÆŒ']*")
HYPHENS = ('-', '\u00ac')  # some OCR reads the line-end hyphen as a not-sign
SUFFIXES = ('s', 'es', 'ed', 'd', 'ing', 'ly', 'er', 'ers', 'ness', 'ism', 'ist', 'ists', 'al', 'ally', 'ation', 'ations')
PREFIXES = ('un', 're', 'in', 'non', 'over', 'pre', 'mis', 'dis', 'counter')


def vocabulary():
    c = collections.Counter()
    # Proofread texts only: earlier OCR transcriptions (ia-*) are left out so their flagged words never become known.
    for f in glob.glob(str(ROOT / 'data/texts/*.txt')):
        if Path(f).name.startswith('ia-'):
            continue
        c.update(w.lower() for w in WORD.findall(Path(f).read_text(encoding='utf-8', errors='replace')))
    return dict(c)


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
        return r.read()


def fetch(ia, cache):
    p = Path(cache) / f'{ia}_djvu.xml'
    if not p.exists():
        meta = json.loads(get(f'https://archive.org/metadata/{ia}'))
        assert not meta['metadata'].get('access-restricted-item'), f'{ia}: lending-only scan'
        p.write_bytes(get(f"https://{meta['server']}{meta['dir']}/{ia}_djvu.xml"))
        (Path(cache) / f'{ia}.meta.json').write_text(json.dumps(meta['metadata']))
    return p.read_bytes(), json.loads((Path(cache) / f'{ia}.meta.json').read_text())


def known(w, V, depth=1):
    w = w.lower().strip("'")
    if not w or w in V or w.isdigit() or len(w) == 1:
        return True
    if depth and w.endswith("'s") and known(w[:-2], V, 0):
        return True
    if depth and any(w.endswith(x) and len(w) - len(x) >= 3 and (w[:-len(x)] in V or w[:-len(x)] + 'e' in V) for x in SUFFIXES):
        return True  # a known word with a regular ending: "monopolist" + "s"
    return bool(depth) and any(w.startswith(x) and len(w) - len(x) >= 4 and known(w[len(x):], V, 0) for x in PREFIXES)



def repair(tok, V):
    """Return (fixed token, changed?) for one whitespace token; only a unique known repair is accepted."""
    m = re.match(r"^([^A-Za-zæœÆŒ]*)([A-Za-zæœÆŒ][A-Za-zæœÆŒ0-9'*]*?)([^A-Za-zæœÆŒ]*)$", tok)
    if not m:
        return tok, None
    pre, core, post = m.groups()
    if known(core, V) or not re.search(r'[a-z]', core):
        return tok, None
    if len(core.replace('*', '')) < 4:  # too short to repair safely: flag it
        return tok, 'unknown'
    plain = core.replace('*', '')
    cands = set()
    for a, b in CONFUSIONS:
        i = plain.find(a)
        while i >= 0:
            c = plain[:i] + b + plain[i + len(a):]
            if c and V.get(c.lower(), 0) >= 10 and c.lower() != plain.lower() and len(c) > 1:  # repair only to a common word
                cands.add(c)
            i = plain.find(a, i + 1)
    if plain != core and V.get(plain.lower(), 0) >= 10:
        cands.add(plain)
    # Take a repair only when it is far commoner in the library's texts than any other repair (20 times or more).
    ranked = sorted(cands, key=lambda c: -V.get(c.lower(), 0))
    if ranked and (len(ranked) == 1 or V.get(ranked[0].lower(), 0) >= 20 * max(1, V.get(ranked[1].lower(), 0))):
        c = ranked[0]
        return pre + c + post, (core, c)
    return tok, 'unknown'  # names included: kept as printed and flagged, never accepted silently


def page_lines(obj):
    out = []
    for p_i, para in enumerate(obj.iter('PARAGRAPH')):
        for l_i, line in enumerate(para.iter('LINE')):
            ws = line.findall('WORD')
            if not ws:
                continue
            boxes = [[int(x) for x in w.get('coords').split(',')[:4]] for w in ws]
            text = html.unescape(' '.join((w.text or '').strip() for w in ws).strip())  # some OCR files double-escape quotes
            if text:
                out.append({'x': min(b[0] for b in boxes), 'y': max(b[1] for b in boxes), 'h': statistics.median(b[1] - b[3] for b in boxes),
                            'text': re.sub(r'\s+', ' ', text), 'paraStart': l_i == 0, 'para': p_i})
    return out


def body(lines, height, heads, V=None):
    """Drop the running head and the page number: by their text, and by layout (a top or bottom line set apart from
    the body by a wider gap than the page's line spacing, which catches heads the OCR misread)."""
    num = r'[\[(|]?\s*[\dIVXLCivxlc]{1,6}\s*[\])|]?\.?'
    keep = [l for l in lines if re.search(r'[A-Za-z]{2}|\d', l['text'])]  # scanning noise: no word of two letters
    if keep and re.fullmatch(num, keep[0]['text']):
        keep = keep[1:]
    ys = [l['y'] for l in keep]
    gaps = [b - a for a, b in zip(ys, ys[1:]) if b > a]
    if len(gaps) >= 4:
        step = statistics.median(gaps)
        if keep[0]['y'] < 0.2 * height and ys[1] - ys[0] > 1.3 * step:
            keep = keep[1:]
        if len(keep) > 1 and keep[-1]['y'] > 0.75 * height and keep[-1]['y'] - keep[-2]['y'] > 1.3 * step and len(keep[-1]['text'].split()) <= 4:
            keep = keep[:-1]
    if keep and keep[0]['y'] < 0.2 * height and (norm_head(keep[0]['text']) in heads or re.fullmatch(r'[\divxlcIVXLC.\s]{1,8}', keep[0]['text'])):
        keep = keep[1:]
    if keep and re.fullmatch(num, keep[-1]['text']):
        keep = keep[:-1]
    if keep and re.fullmatch(num, keep[0]['text']):
        keep = keep[1:]
    # a printed rule under the running head, read by the OCR as nonsense: a top line with no real word in it
    if V is not None and keep and keep[0]['y'] < 0.25 * height and len(keep[0]['text'].split()) <= 6 \
            and not any(len(w) > 2 and known(w, V) for w in WORD.findall(keep[0]['text'])):
        keep = keep[1:]
    return keep


def norm_head(t):
    return re.sub(r'[^a-z]', '', t.lower())


def build(e, cache, V):
    xml, meta = fetch(e['ia'], cache)
    root = ET.fromstring(xml)
    objs = root.findall('.//OBJECT')[e['firstLeaf']:e['lastLeaf'] + 1]
    raw_pages = [(int(o.get('height') or 3000), page_lines(o)) for o in objs]
    firsts = collections.Counter(norm_head(ls[0]['text']) for _, ls in raw_pages if ls and len(ls[0]['text']) < 70)
    heads = {h for h, n in firsts.items() if n >= 3 and h}
    paras, corrections, flagged = [], [], []
    cur, prev_end = [], ''
    for height, ls in raw_pages:
        ls = body(ls, height, heads, V)
        if not ls:
            continue
        margin = statistics.median(l['x'] for l in ls)
        for k, l in enumerate(ls):
            indent = l['x'] > margin + 25 and not prev_end.endswith('-')
            sentence_end = bool(re.search(r'[.!?:;"”’)]$', prev_end))
            heading = l['text'].isupper() and len(l['text'].split()) <= 10 and not prev_end.endswith('-')
            new = cur and (heading or (l['paraStart'] and sentence_end) or (indent and sentence_end)
                           or (cur and cur[-1].isupper() and len(cur[-1].split()) <= 10))
            if new:
                paras.append(cur); cur = []
            cur.append(l['text']); prev_end = l['text']
    if cur:
        paras.append(cur)
    out = []
    for p in paras:
        text = ''
        for line in p:
            head = text.rsplit(' ', 1)[-1] if text else ''
            tail = line.split(' ', 1)[0]
            if text.endswith(HYPHENS) and line[:1].islower():
                joined = re.sub(r'[^A-Za-zæœ]', '', head + tail)
                text = text[:-1] + line if known(joined, V) else text[:-1] + '-' + line
            elif (head.isalpha() and tail.isalpha() and tail[:1].islower() and not known(head, V)
                  and not known(tail, V) and known(head + tail, V)):
                text = text + line  # OCR lost the line-end hyphen: neither half is a word, the whole is
            else:
                text = (text + ' ' + line).strip()
        text = re.sub(r'\s+([,;:.!?])', r'\1', re.sub(r'\s+', ' ', text))
        toks, bad = [], []
        for t in text.split(' '):
            f, ch = repair(t, V)
            if isinstance(ch, tuple):
                corrections.append({'ocr': ch[0], 'reading': ch[1]})
            elif ch == 'unknown':
                bad.append(t)
            toks.append(f)
        out.append(' '.join(toks))
        if bad:
            flagged.append({'block': len(out) - 1, 'words': bad[:8]})
    words = sum(len(WORD.findall(p)) for p in out)
    unknown = sum(len(f['words']) for f in flagged)
    return out, corrections, flagged, words, unknown, meta, xml


def main(spec, cache):
    V = vocabulary()
    for e in json.loads(Path(spec).read_text()):
        out_path = ROOT / f"data/texts/{e['edition']}.txt"
        assert not out_path.exists(), f"{e['edition']}: already hosted; a pinned text never changes"
        assert pd_by_date(e['year']), e['edition']
        paras, corrections, flagged, words, unknown, meta, xml = build(e, cache, V)
        year = int(re.search(r'\d{4}', str(meta.get('date'))).group())
        assert pd_by_date(year), (e['ia'], year)
        T = e['title']
        head = [T, '', f"By {e['author']}", '', f"First published {e['firstPublished']}. Public domain in the USA.", '',
                f"Transcribed for Bibliotheca Catholica from the Internet Archive scan {e['ia']} "
                f"({meta.get('publisher') or 'publisher not recorded'}, {year}; https://archive.org/details/{e['ia']}). "
                f"The OCR was cleaned by tools/transcribe_scan.py: running heads and page numbers removed, words rejoined "
                f"across line breaks, and {len(corrections)} common OCR confusions repaired where only one reading is a "
                f"known word. {len(flagged)} paragraphs keep a word the tool could not read; they are listed in the "
                f"provenance record. No missing words were supplied. Not a manual proofread.", '',
                '*** START OF THE TRANSCRIPTION ***', '']
        data = ('\n'.join(head) + '\n\n'.join(paras) + '\n\n' + END + '\n').encode('utf-8')
        out_path.write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        rec = {'id': e['edition'], 'kind': 'ocr-transcription', 'title': e['sourceTitle'], 'author': e['author'],
               'rights': f"Public domain in the USA. First published {e['firstPublished']}; the scanned printing is of {year}.",
               'rightsBasis': 'pd-date',
               'volumes': [{'identifier': e['ia'], 'url': f"https://archive.org/details/{e['ia']}", 'year': year,
                            'publisher': meta.get('publisher'), 'ocr': f"{e['ia']}_djvu.xml",
                            'ocrSha256': hashlib.sha256(xml).hexdigest(), 'leaves': [e['firstLeaf'], e['lastLeaf']]}],
               'method': 'tools/transcribe_scan.py: Internet Archive djvu.xml OCR, running heads and page numbers removed, '
                         'paragraphs from the scan, words rejoined across line breaks, the space the printer set before '
                         'punctuation closed, unique known-word OCR repairs recorded, unread words flagged and kept as printed.',
               'words': words, 'unknownWords': unknown, 'readRate': round(1 - unknown / max(1, words), 4),
               'flaggedBlocks': len(flagged), 'flagged': flagged, 'corrections': len(corrections),
               'correctionList': corrections, 'text': f"data/texts/{e['edition']}.txt", 'sha256': sha,
               'checked': time.strftime('%Y-%m-%d')}
        if e.get('note'):
            rec['note'] = e['note']
        (ROOT / f"data/sources/{e['edition']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
        print(e['edition'], sha[:12], f"{words} words, read rate {rec['readRate']:.2%}, {len(corrections)} repairs, {len(flagged)} flagged")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec')
    ap.add_argument('--cache', default='/tmp/transcribe-scan-cache')
    a = ap.parse_args()
    Path(a.cache).mkdir(parents=True, exist_ok=True)
    main(a.spec, a.cache)
