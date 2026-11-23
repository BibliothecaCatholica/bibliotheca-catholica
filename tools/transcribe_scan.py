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
  * flags (never rewrites) any paragraph that still has a word it could not read; it never supplies a missing word;
  * counts a word in the spec's `verifiedWords` as read: a name or foreign word a person checked against the page image
    of the same scan (listed in the provenance record; November 20, 2026);
  * applies the spec's `handFixes`, if any, before all of the above: each is {leaf, page, ocr, reading}, a misread checked
    by a person against the page image of the same scan (never another edition). `ocr` must be one whole OCR line of
    that leaf or occur exactly once in its lines and is replaced by `reading` (an empty reading drops a whole line of OCR noise). Every fix is
    copied to the provenance record (owner decision, November 17, 2026).
Known words are those of the library's own hosted texts (data/texts/), so the vocabulary is period English.

Read-gate process (owner approval, November 22, 2026; docs/PROJECT-RULES.md rule 1, "Read gate"):
  * `secondOcr` {engine: "tesseract", langs: "eng+lat+ita", scale: 1}: each leaf's page image is re-read with Tesseract
    and, line by line, its reading replaces the archive.org line only when it has strictly fewer unread words and about
    the same number of words (choose_lines()); archive.org's OCR stays the default and the fallback;
  * `foreignWords` {lat|ita|fra|deu|grc-translit: {forms, checked | allChecked + wrong}}: a language's unread forms count
    as read when the reproducible random sample (foreign_sample(): at least 10% of the forms and at least 30) was
    checked against the page images and every sampled form was right; otherwise every form is checked by hand;
  * `omitted` [{what, leaves, pages}]: an index, bibliography, or long appendix after the body may be left out, with a
    sentence in the text's header pointing to the full scan; body text, footnotes, and front matter never are;
  * every score is saved with its method (readGate in the source record: engine, leaves scored, omissions, line
    choices, hand fixes, verified words, foreign samples), and `--measure DIR` scores a book without hosting it and
    writes DIR/<edition>.json with the method and every unread form; `--sample` prints the samples to check.

    python3 tools/transcribe_scan.py SPEC.json [--cache DIR] [--measure DIR | --sample]

SPEC is a list of {edition, ia, title, sourceTitle, author, year, firstPublished, firstLeaf, lastLeaf, note?, startsWith?,
endsWith?, layout?, publisher?} (startsWith/endsWith cut one article from shared pages: see bounded(); layout 'verse'
keeps printed line and stanza breaks and does not rejoin words across line ends; publisher and year override a
mislabeled Internet Archive catalog entry when the printed title page is recorded in note); leaves
are 0-based page indexes of the djvu.xml, chosen by looking at the scan (front matter in, library stamps and
publisher's advertisements out). Output per entry: data/texts/<edition>.txt and data/sources/<edition>.json
(kind `ocr-transcription`, validated by tools/build_library.py and tests/test_transcribed_scans.py).
"""
import argparse, collections, difflib, glob, hashlib, html, json, math, random, re, statistics, subprocess, sys, time, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from rights_rule import nonrenewal_problems, pd_by_date  # noqa: E402

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
        (Path(cache) / f'{ia}.where.json').write_text(json.dumps({'server': meta['server'], 'dir': meta['dir']}))
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


def tesseract_version():
    try:
        return subprocess.run(['tesseract', '--version'], capture_output=True, text=True).stdout.split('\n')[0].strip()
    except FileNotFoundError:
        return None


def page_image(ia, obj, cache, scale=1):
    """The scan's own page image for one leaf (BookReader, the same JPEG 2000 the djvu.xml was made from), cached."""
    where = json.loads((Path(cache) / f'{ia}.where.json').read_text())
    n = re.search(r'_(\d{4})\.djvu', obj.get('usemap')).group(1)
    out = Path(cache) / 'img' / ia / f'{n}-s{scale}.jpg'
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(get(f"https://{where['server']}/BookReader/BookReaderImages.php?zip={where['dir']}/{ia}_jp2.zip"
                            f"&file={ia}_jp2/{ia}_{n}.jp2&id={ia}&scale={scale}&rotate=0"))
    return out


def tesseract_lines(img, langs, obj_width):
    """Lines from Tesseract (TSV), in the djvu.xml's coordinate space: [{x, x2, top, y, h, text}]."""
    tsv = img.with_suffix(f'.{langs.replace("+", "-")}.tsv')
    if not tsv.exists():
        r = subprocess.run(['tesseract', str(img), '-', '-l', langs, '--psm', '3', 'tsv'], capture_output=True, text=True)
        tsv.write_text(r.stdout)
    rows = [l.split('\t') for l in tsv.read_text().splitlines()[1:]]
    page_w = next((int(r[8]) for r in rows if len(r) >= 12 and r[0] == '1'), 0) or 1
    k = obj_width / page_w
    lines = collections.OrderedDict()
    for r in rows:
        if len(r) < 12 or r[0] != '5' or not r[11].strip():
            continue
        x, y, w, h = (int(v) for v in r[6:10])
        lines.setdefault((r[2], r[3], r[4]), []).append((x, y, w, h, r[11].strip()))
    out = []
    for ws in lines.values():
        out.append({'x': int(min(a[0] for a in ws) * k), 'x2': int(max(a[0] + a[2] for a in ws) * k),
                    'top': int(min(a[1] for a in ws) * k), 'y': int(max(a[1] + a[3] for a in ws) * k),
                    'h': int(statistics.median(a[3] for a in ws) * k), 'text': ' '.join(a[4] for a in ws)})
    return out


def unread(text, V, verified=frozenset()):
    """Tokens of a line the scorer would flag: not a known word, not verified, and with no unique repair."""
    n = 0
    for t in text.split(' '):
        if re.sub(r"^[^\w]+|[^\w]+$", '', t) in verified:
            continue
        if repair(t, V)[1] == 'unknown':
            n += 1
    return n


def choose_lines(arch, tess, V, verified=frozenset()):
    """For each line of the Internet Archive OCR, take the Tesseract reading of the same printed line instead when it has
    strictly fewer unread words and about the same number of words (so no words are dropped or invented); otherwise keep
    the archive.org line, which stays the default and the fallback (November 22, 2026). Lines are matched by their boxes:
    most of the shorter line's height and some of its width must overlap. Returns (lines, counts)."""
    counts = collections.Counter()
    out = []
    for a in arch:
        best, best_ov = None, 0.0
        for t in tess:
            vy = min(a['y'], t['y']) - max(a['top'], t['top'])
            vx = min(a['x2'], t['x2']) - max(a['x'], t['x'])
            if vy <= 0 or vx <= 0:
                continue
            ov = vy / max(1, min(a['y'] - a['top'], t['y'] - t['top']))
            if ov > best_ov:
                best, best_ov = t, ov
        na = len(a['text'].split())
        if best is not None and best_ov >= 0.5 and abs(len(best['text'].split()) - na) <= max(1, na // 5) \
                and unread(best['text'], V, verified) < unread(a['text'], V, verified):
            out.append(dict(a, text=re.sub(r'\s+', ' ', best['text']), engine='tesseract'))
            counts['tesseract'] += 1
        else:
            out.append(a)
            counts['archive.org'] += 1
    return out, counts


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
                out.append({'x': min(b[0] for b in boxes), 'x2': max(b[2] for b in boxes), 'top': min(b[3] for b in boxes),
                            'y': max(b[1] for b in boxes), 'h': statistics.median(b[1] - b[3] for b in boxes),
                            'text': re.sub(r'\s+', ' ', text), 'paraStart': l_i == 0, 'para': p_i})
    return out


ROMAN_LINE = re.compile(r'^[IVXLC]+\.?$', re.I)  # verse stanza numbers: I., V., X. (one letter would look like noise)


def body(lines, height, heads, V=None, keep_roman=False):
    """Drop the running head and the page number: by their text, and by layout (a top or bottom line set apart from
    the body by a wider gap than the page's line spacing, which catches heads the OCR misread)."""
    num = r'[\[(|]?\s*[\dIVXLCivxlc]{1,6}\s*[\])|]?\.?'
    keep = [l for l in lines if re.search(r'[A-Za-z]{2}|\d', l['text'])
            or (keep_roman and ROMAN_LINE.match(l['text'].strip()))]  # scanning noise: no word of two letters
    # a running head set as several short items on one line (an encyclopedia's "ADVENT  166  ADVENTISTS", November 20,
    # 2026): drop the whole band when it sits at the top, apart from the text below it
    if len(keep) > 3 and keep[0]['y'] < 0.15 * height:
        band = [l for l in keep if abs(l['y'] - keep[0]['y']) < keep[0]['h']]
        below = [l['y'] for l in keep if l not in band]
        if len(band) > 1 and all(len(l['text'].split()) <= 4 for l in band) and below and min(below) - keep[0]['y'] > 2 * keep[0]['h']:
            keep = [l for l in keep if l not in band]
    if keep and re.fullmatch(num, keep[0]['text']) and not (keep_roman and ROMAN_LINE.match(keep[0]['text'].strip())):
        keep = keep[1:]
    ys = [l['y'] for l in keep]
    gaps = [b - a for a, b in zip(ys, ys[1:]) if b > a]
    if len(gaps) >= 4:
        step = statistics.median(gaps)
        if keep[0]['y'] < 0.2 * height and ys[1] - ys[0] > 1.3 * step:
            keep = keep[1:]
        if len(keep) > 1 and keep[-1]['y'] > 0.75 * height and keep[-1]['y'] - keep[-2]['y'] > 1.3 * step and len(keep[-1]['text'].split()) <= 4:
            keep = keep[:-1]
    if keep and keep[0]['y'] < 0.2 * height and (norm_head(keep[0]['text']) in heads or re.fullmatch(r'[\divxlcIVXLC.\s]{1,8}', keep[0]['text'])) \
            and not (keep_roman and ROMAN_LINE.match(keep[0]['text'].strip())):
        keep = keep[1:]
    if keep and re.fullmatch(num, keep[-1]['text']) and not (keep_roman and ROMAN_LINE.match(keep[-1]['text'].strip())):
        keep = keep[:-1]
    if keep and re.fullmatch(num, keep[0]['text']) and not (keep_roman and ROMAN_LINE.match(keep[0]['text'].strip())):
        keep = keep[1:]
    # a printed rule under the running head, read by the OCR as nonsense: a top line with no real word in it
    if V is not None and keep and keep[0]['y'] < 0.25 * height and len(keep[0]['text'].split()) <= 6 \
            and not any(len(w) > 2 and known(w, V) for w in WORD.findall(keep[0]['text'])):
        keep = keep[1:]
    return keep


def norm_head(t):
    return re.sub(r'[^a-z]', '', t.lower())


NOTE_MARK = re.compile(r'^[*°†‡§]|^\d{1,2}\.?\s+\S')  # "5 Moral." or "10. Cf."


def split_notes(lines, height):
    """Footnotes: a block at the foot of the page, or a long note that starts above mid-page, set off by a wider gap
    than the line spacing and set in smaller type than the lines before the break (not the whole-page median, which
    hides the break when notes fill most of the page). The first line of the remainder must itself be smaller, so a
    still-body line is not pulled into the notes. A note mark is not required (a continued note often has none).
    Heading lines (more than 1.25 times the page's median height, or with no lowercase letter: a chapter numeral or
    title) are left out of that comparison.
    Returns (body lines, [note lines per note])."""
    if len(lines) < 4:
        return lines, []
    ys = [l['y'] for l in lines]
    gaps = [b - a for a, b in zip(ys, ys[1:])]
    step = statistics.median(g for g in gaps if g > 0) if any(g > 0 for g in gaps) else 0
    starts = []
    page_h = statistics.median(l['h'] for l in lines)
    for k in range(1, len(lines)):
        rest = lines[k:]
        if len(rest) < 2:
            continue
        # a chapter's opening page: its numeral and title are set larger than the text, so measure the type before
        # the break without heading-size lines, and never start notes right after headings alone (November 22, 2026)
        before = [l['h'] for l in lines[:k] if l['h'] <= 1.25 * page_h and any(c.islower() for c in l['text'])]
        if not before:
            continue
        med_before = statistics.median(before)
        if not (lines[k]['h'] < 0.90 * med_before and statistics.median(l['h'] for l in rest) < 0.88 * med_before):
            continue
        if gaps[k - 1] > 1.4 * step or NOTE_MARK.match(lines[k]['text']):
            starts.append(k)
    if starts:
        k = min(starts)  # the first note of the block; the notes below it are part of the same block
        notes = []
        for l in lines[k:]:
            if NOTE_MARK.match(l['text']) or not notes:
                notes.append([l['text']])
            else:
                notes[-1].append(l['text'])
        return lines[:k], notes
    return lines, []


def note_text(lines):
    t = re.sub(r'([a-z])- ([a-z])', r'\1\2', ' '.join(lines))  # rejoin a word hyphenated across the note's lines
    return '[Note: ' + t + ']'


def library_stamps(raw_pages, heads):
    """Short capital lines (a library's stamp) repeated on three or more pages below the top band of the page, where
    running heads sit, and that are not running heads."""
    c = collections.Counter()
    for height, ls in raw_pages:
        for l in ls:
            t = l['text']
            if l['y'] > 0.2 * height and len(t.split()) <= 6 and all_caps(t):
                c[norm_head(t)] += 1
    return {h for h, n in c.items() if n >= 3 and h and h not in heads and len(h) >= 8}


def all_caps(t):
    return sum(ch.isupper() for ch in t) > 0.7 * max(1, sum(ch.isalpha() for ch in t))


def is_stamp(text, stamps):
    n = norm_head(text)
    return all_caps(text) and len(n) >= 8 and any(difflib.SequenceMatcher(None, n, s).ratio() >= 0.85 for s in stamps)


def apply_hand_fixes(raw_pages, e):
    for f in e.get('handFixes', []):
        lines = raw_pages[f['leaf'] - e['firstLeaf']][1]
        hits = [l for l in lines if l['text'] == f['ocr']] or [l for l in lines if f['ocr'] in l['text']]
        assert len(hits) == 1 and hits[0]['text'].count(f['ocr']) == 1, (e['edition'], f, len(hits))
        if f['reading'] == '':
            assert hits[0]['text'] == f['ocr'], ('only a whole line may be dropped', f)
            lines.remove(hits[0])
        else:
            hits[0]['text'] = hits[0]['text'].replace(f['ocr'], f['reading'])



def explode_newlines(lines):
    """A handFix may insert printed lines (an omission row of asterisks) by putting newlines in `reading`."""
    out = []
    for l in lines:
        if '\n' not in l['text']:
            out.append(l)
            continue
        for i, part in enumerate(l['text'].split('\n')):
            nl = dict(l)
            nl['text'] = part
            nl['y'] = l['y'] + i
            out.append(nl)
    return out


def verse_paras(raw_pages, e, heads, stamps, V):
    """Keep each printed verse line, and open a new stanza where the scan leaves a wider gap than about one and a half times the line spacing
    (or where a handFix inserted a blank line). Hyphenated run-overs and ordinary line-end hyphens are left as printed."""
    paras = []
    for height, ls in raw_pages:
        ls = [l for l in ls if not is_stamp(l['text'], stamps)]
        ls = body(ls, height, heads, keep_roman=True)  # no vocabulary: a Latin heading would look unread and be dropped as a rule
        ls = explode_newlines(ls)
        if not ls:
            continue
        solid = [l for l in ls if l['text'].strip()]
        gaps = [b['y'] - a['y'] for a, b in zip(solid, solid[1:]) if b['y'] > a['y']]
        step = statistics.median(gaps) if gaps else 20
        cur, prev = [], None
        for l in ls:
            if not l['text'].strip():
                if cur:
                    paras.append(cur)
                    cur = []
                prev = l
                continue
            if prev is not None and l['y'] - prev['y'] > 1.45 * step and cur:
                paras.append(cur)
                cur = []
            cur.append(l['text'])
            prev = l
        if cur:
            paras.append(cur)
    return bounded(paras, e)


def bounded(paras, e):
    """One article cut from shared pages (an encyclopedia entry, November 20, 2026): with `startsWith` and `endsWith` in
    the spec, keep the paragraphs from the first one that starts with the one through the first later one that ends
    with the other. Matching ignores runs of spaces; both must be found, or nothing is kept."""
    if not (e.get('startsWith') or e.get('endsWith')):
        return paras
    n = lambda t: re.sub(r'\s+', ' ', t).strip()
    a = next(i for i, p in enumerate(paras) if n(' '.join(p)).startswith(n(e['startsWith'])))
    b = next(i for i, p in enumerate(paras) if i >= a and n(' '.join(p)).endswith(n(e['endsWith'])))
    return paras[a:b + 1]


def join_lines(p, V):
    """One paragraph's OCR lines as one string: line-end hyphens and lost hyphens resolved by the vocabulary."""
    text = ''
    for line in p:
        head = text.rsplit(' ', 1)[-1] if text else ''
        tail = line.split(' ', 1)[0]
        if text.endswith(HYPHENS) and line[:1].islower():
            joined = re.sub(r'[^A-Za-zæœ]', '', head + tail)
            text = text[:-1] + line if known(joined, V) else text[:-1] + '-' + line
        elif (head.isalpha() and (tc := re.sub(r"[^A-Za-z]+$", '', tail)).isalpha() and tc[:1].islower()
              and (not known(head, V) and not known(tc, V) and known(head + tc, V)
                   or V.get((head + tc).lower(), 0) >= 3 and (not known(head, V) or not known(tc, V)))):
            # OCR lost the line-end hyphen: neither half is a word and the whole is; or one half is not a word and the
            # whole is a common one ("imagina" / "tion", "per" / "formances"; November 21, 2026)
            text = text + line
        else:
            text = (text + ' ' + line).strip()
    return text


LANGS = ('lat', 'ita', 'fra', 'deu', 'grc-translit')


def foreign_sample(edition, lang, forms):
    """The random sample of distinct word forms to check against the page images: at least 10% of the forms and at least
    30 (or every form, if there are fewer), drawn with a seed made of the edition id and the language so anyone can
    draw the same sample again."""
    forms = sorted(set(forms))
    n = min(len(forms), max(30, math.ceil(0.1 * len(forms))))
    return sorted(random.Random(f'{edition}:{lang}').sample(forms, n))


def foreign_read(e):
    """Sample-verified foreign words (owner approval, November 22, 2026): a language's unread forms count as read when every
    form in the drawn sample was checked against the page images and found correct; if any sampled form was wrong,
    every form of that language must be checked by hand (`allChecked`) and only the correct ones count. Returns
    (set of forms read, record for the source record)."""
    read, rec = set(), {}
    for lang, d in (e.get('foreignWords') or {}).items():
        assert lang in LANGS, (e['edition'], lang, 'language must be one of', LANGS)
        forms = sorted(set(d['forms']))
        wrong = sorted(set(d.get('wrong', [])))
        sample = foreign_sample(e['edition'], lang, forms)
        if wrong or d.get('allChecked'):
            assert d.get('allChecked'), (e['edition'], lang, 'a wrong sampled form means every form must be checked by hand')
            assert set(wrong) <= set(forms), (e['edition'], lang)
            ok, result = [f for f in forms if f not in wrong], 'a sampled form was wrong, so every form was checked by hand'
        else:
            assert sorted(set(d.get('checked', []))) == sample, (e['edition'], lang, 'checked must be exactly the drawn sample')
            ok, result = forms, 'every sampled form correct'
        read |= set(ok)
        rec[lang] = {'forms': forms, 'sampleSize': len(sample), 'sample': sample, 'wrong': wrong, 'result': result,
                     'seed': f"{e['edition']}:{lang}"}
    return read, rec


def second_ocr(e, objs, raw_pages, cache, V, verified):
    """Re-OCR each leaf's page image with Tesseract and let choose_lines() pick per line (spec `secondOcr`:
    {"engine": "tesseract", "langs": "eng+lat+ita", "scale": 1}). Images and Tesseract output are cached."""
    cfg = e['secondOcr']
    assert cfg.get('engine', 'tesseract') == 'tesseract', cfg
    langs, scale = cfg.get('langs', 'eng'), cfg.get('scale', 1)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as pool:
        tess = list(pool.map(lambda o: tesseract_lines(page_image(e['ia'], o, cache, scale), langs, int(o.get('width'))), objs))
    counts = collections.Counter()
    for i, (height, ls) in enumerate(raw_pages):
        chosen, c = choose_lines(ls, tess[i], V, verified)
        raw_pages[i] = (height, chosen)
        counts += c
    return {'engine': tesseract_version(), 'langs': langs, 'scale': scale, 'lineChoices': dict(counts)}


def build(e, cache, V):
    xml, meta = fetch(e['ia'], cache)
    root = ET.fromstring(xml)
    objs = root.findall('.//OBJECT')[e['firstLeaf']:e['lastLeaf'] + 1]
    raw_pages = [(int(o.get('height') or 3000), page_lines(o)) for o in objs]
    foreign, foreign_rec = foreign_read(e)
    verified = set(e.get('verifiedWords', [])) | foreign
    info = {'foreignWords': foreign_rec, 'secondOcr': second_ocr(e, objs, raw_pages, cache, V, verified) if e.get('secondOcr') else None,
            'unread': collections.Counter()}
    apply_hand_fixes(raw_pages, e)
    firsts = collections.Counter(norm_head(ls[0]['text']) for _, ls in raw_pages if ls and len(ls[0]['text']) < 70)
    heads = {h for h, n in firsts.items() if n >= 3 and h}
    stamps = library_stamps(raw_pages, heads)
    paras, corrections, flagged, pending = [], [], [], []
    cur, prev_end = [], ''
    if e.get('layout') == 'verse':
        paras = verse_paras(raw_pages, e, heads, stamps, V)
    else:

        def close(par):
            paras.append(par)
            while pending:  # a page's footnotes follow the paragraph that was running on that page
                paras.append([note_text(pending.pop(0))])
        for height, ls in raw_pages:
            ls = [l for l in ls if not is_stamp(l['text'], stamps)]
            ls = body(ls, height, heads, V)
            ls, notes = split_notes(ls, height)
            if not ls:
                pending.extend(notes)
                continue
            margin = statistics.median(l['x'] for l in ls)
            # Two-column pages (an encyclopedia, November 20, 2026): a line set higher than the one before it starts the
            # next column. The OCR opens a new paragraph there, but the text runs on unless the line is indented.
            wide = [l['x'] for l in ls if len(l['text']) > 30]
            two_col = bool(wide) and max(wide) - min(wide) > 300
            prev_y = None
            for k, l in enumerate(ls):
                col_top = two_col and prev_y is not None and l['y'] < prev_y - 3 * l['h']
                prev_y = l['y']
                if col_top:
                    left = min(x['x'] for x in ls if abs(x['x'] - l['x']) < 120)
                    indent = l['x'] > left + 25 and not prev_end.endswith('-')
                    sentence_end = bool(re.search(r'[.!?:;"”’)]\s*[\d*°†‡§]{0,2}$', prev_end))
                    heading = l['text'].isupper() and len(l['text'].split()) <= 10 and not prev_end.endswith('-')
                    if cur and (heading or (indent and sentence_end)):
                        close(cur); cur = []
                    cur.append(l['text']); prev_end = l['text']
                    continue
                # on a two-column page the indent is measured from the line's own column
                left = min(x['x'] for x in ls if abs(x['x'] - l['x']) < 120) if two_col else margin
                indent = l['x'] > left + 25 and not prev_end.endswith('-')
                sentence_end = bool(re.search(r'[.!?:;"”’)]\s*[\d*°†‡§]{0,2}$', prev_end))  # a note mark may follow
                heading = l['text'].isupper() and len(l['text'].split()) <= 10 and not prev_end.endswith('-')
                new = cur and (heading or (l['paraStart'] and sentence_end) or (indent and sentence_end)
                               or (cur and cur[-1].isupper() and len(cur[-1].split()) <= 10))
                if new:
                    close(cur); cur = []
                cur.append(l['text']); prev_end = l['text']
            pending.extend(notes)
        if cur:
            close(cur)
        while pending:  # notes on the last pages
            paras.append([note_text(pending.pop(0))])
        paras = bounded(paras, e)
    out = []
    verse = e.get('layout') == 'verse'

    def score_line(line, bad):
        toks = []
        for t in line.split(' '):
            stem = re.sub(r"^[^\w]+|[^\w]+$", '', t)
            if stem in verified:
                toks.append(t)
                continue  # checked against the page image: do not auto-repair (vilia must not become villa)
            f, ch = repair(t, V)
            if isinstance(ch, tuple):
                corrections.append({'ocr': ch[0], 'reading': ch[1]})
            elif ch == 'unknown':
                bad.append(t)
                info['unread'][re.sub(r"^[^\w]+|[^\w]+$", '', t)] += 1
            toks.append(f)
        return ' '.join(toks)

    for p in paras:
        bad = []
        if verse:
            out.append('\n'.join(score_line(line, bad) for line in p))
        else:
            text = join_lines(p, V)
            text = re.sub(r'\s+([,;:.!?])', r'\1', re.sub(r'\s+', ' ', text))
            text, nj = re.subn(r'(?<=[A-Za-z]) j(?= [a-z])', ';', text)  # a semicolon the OCR read as a lone "j"
            corrections.extend({'ocr': 'j', 'reading': ';'} for _ in range(nj))
            text = score_line(text, bad)
            out.append(text)
        if bad:  # the first 8 unread words are listed; n counts them all (a cap here once hid unread words)
            flagged.append({'block': len(out) - 1, 'words': bad[:8], **({'n': len(bad)} if len(bad) > 8 else {})})
    words = sum(len(WORD.findall(p)) for p in out)
    unknown = sum(f.get('n', len(f['words'])) for f in flagged)
    return out, corrections, flagged, words, unknown, meta, xml, info


def read_gate_record(e, words, unknown, info):
    """How the score was made, printed and saved with it so it can be reproduced (owner, November 22, 2026)."""
    so = info.get('secondOcr')
    return {'gate': 0.995, 'words': words, 'unknown': unknown, 'readRate': round(1 - unknown / max(1, words), 4),
            'scorer': 'tools/transcribe_scan.py; vocabulary of the proofread hosted texts in data/texts (ia-* excluded)',
            'engine': ('archive.org djvu.xml OCR' + (f", with {so['engine']} ({so['langs']}, image scale {so['scale']}) chosen per "
                       f"line where it reads more words" if so else '')),
            **({'lineChoices': so['lineChoices']} if so else {}),
            'leavesScored': [e['firstLeaf'], e['lastLeaf']],
            'omitted': e.get('omitted', []),
            'handFixes': len(e.get('handFixes', [])), 'verifiedWords': len(e.get('verifiedWords', [])),
            'foreignWords': {k: {x: v[x] for x in ('sampleSize', 'wrong', 'result')} | {'forms': len(v['forms'])}
                             for k, v in info.get('foreignWords', {}).items()},
            'measured': time.strftime('%Y-%m-%d')}


def check_omitted(e):
    """Back matter only (owner, November 22, 2026): an index, bibliography, or long appendix after the body may be left out,
    with a note on the text page and a link to the scan. Body text, footnotes, and front matter are never dropped."""
    for o in e.get('omitted', []):
        assert o['leaves'][0] > e['lastLeaf'] and o['leaves'][0] <= o['leaves'][1], (e['edition'], 'only back matter after the body', o)
        assert o.get('what') and o.get('pages'), (e['edition'], o)


def omitted_sentence(e):
    om = e.get('omitted', [])
    if not om:
        return ''
    parts = [f"{o['what']} (pages {o['pages']})" for o in om]
    listed = parts[0] if len(parts) == 1 else ', '.join(parts[:-1]) + ', and ' + parts[-1]
    return f" Left out of this text: {listed}; read them in the full scan at https://archive.org/details/{e['ia']}."


def main(spec, cache, measure=None):
    V = vocabulary()
    for e in json.loads(Path(spec).read_text()):
        check_omitted(e)
        out_path = ROOT / f"data/texts/{e['edition']}.txt"
        if measure:  # score only: nothing is hosted, and the method and every unread form are saved for review
            paras, corrections, flagged, words, unknown, meta, xml, info = build(e, cache, V)
            rg = read_gate_record(e, words, unknown, info)
            out = Path(measure) / f"{e['edition']}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({'edition': e['edition'], 'ia': e['ia'], 'readGate': rg,
                                       'unreadForms': dict(info['unread'].most_common())}, ensure_ascii=False, indent=1) + '\n')
            print(e['edition'], json.dumps(rg, ensure_ascii=False))
            continue
        assert not out_path.exists(), f"{e['edition']}: already hosted; a pinned text never changes"
        basis = e.get('rightsBasis', 'pd-date')
        if basis == 'pd-date':
            assert pd_by_date(e['year']), e['edition']
        else:  # pd-nonrenewal: the evidence must pass, and the scan must be the printing it names
            assert basis == 'pd-nonrenewal', basis
            assert not nonrenewal_problems(e.get('nonRenewal')), (e['edition'], nonrenewal_problems(e.get('nonRenewal')))
            assert e['nonRenewal']['scan'] == e['ia'], e['edition']
        paras, corrections, flagged, words, unknown, meta, xml, info = build(e, cache, V)
        meta_year = int(re.search(r'\d{4}', str(meta.get('date') or e['year'])).group())
        year = int(e['year'])
        publisher = e.get('publisher') or meta.get('publisher')
        if basis == 'pd-date':
            assert pd_by_date(year), (e['ia'], year)
            if meta_year != year:
                assert e.get('note'), (e['edition'], 'IA catalog date differs from the printed year; record it in note')
        else:
            assert year == e['nonRenewal']['firstPublicationYear'], (e['ia'], year)
        T = e['title']
        if e.get('layout') == 'verse':
            cleaned = ("running heads and page numbers removed, verse lines and stanza breaks kept as printed, "
                       "words not rejoined across line breaks, and ")
        else:
            cleaned = "running heads and page numbers removed, words rejoined across line breaks, and "
        head = [T, '', f"By {e['author']}", '', f"First published {e['firstPublished']}. Public domain in the USA.", '',
                f"Transcribed for Bibliotheca Catholica from the Internet Archive scan {e['ia']} "
                f"({publisher or 'publisher not recorded'}, {year}; https://archive.org/details/{e['ia']}). "
                f"The OCR was cleaned by tools/transcribe_scan.py: {cleaned}"
                f"{len(corrections)} common OCR confusions repaired where only one reading is a "
                f"known word. {len(flagged)} paragraphs keep a word the tool could not read; they are listed in the "
                f"provenance record. No missing words were supplied. Not a manual proofread."
                + (f" {len(e['handFixes'])} misreadings were corrected by hand against the page images of the same scan; "
                   f"each is listed in the provenance record." if e.get('handFixes') else '')
                + (f" {e['correction']}" if e.get('correction') else '') + omitted_sentence(e), '',
                '*** START OF THE TRANSCRIPTION ***', '']
        data = ('\n'.join(head) + '\n\n'.join(paras) + '\n\n' + END + '\n').encode('utf-8')
        out_path.write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        rec = {'id': e['edition'], 'kind': 'ocr-transcription', 'title': e['sourceTitle'], 'author': e['author'],
               'rights': (f"Public domain in the USA. First published {e['firstPublished']}; the scanned printing is of {year}."
                          if basis == 'pd-date' else f"Public domain in the USA. First published in the United States in "
                          f"{year} and not renewed; the evidence is in nonRenewal."),
               'rightsBasis': basis, **({'nonRenewal': e['nonRenewal']} if basis == 'pd-nonrenewal' else {}),
               'volumes': [{'identifier': e['ia'], 'url': f"https://archive.org/details/{e['ia']}", 'year': year,
                            'publisher': publisher, 'ocr': f"{e['ia']}_djvu.xml",
                            'ocrSha256': hashlib.sha256(xml).hexdigest(), 'leaves': [e['firstLeaf'], e['lastLeaf']]}],
               'method': ('tools/transcribe_scan.py: Internet Archive djvu.xml OCR, running heads and page numbers removed, '
                         'verse lines and stanza breaks kept as printed, words not rejoined across line breaks, unique '
                         'known-word OCR repairs recorded, unread words flagged and kept as printed.'
                         if e.get('layout') == 'verse' else
                         'tools/transcribe_scan.py: Internet Archive djvu.xml OCR, running heads and page numbers removed, '
                         'paragraphs from the scan, words rejoined across line breaks, the space the printer set before '
                         'punctuation closed, unique known-word OCR repairs recorded, unread words flagged and kept as printed.'),
               'words': words, 'unknownWords': unknown, 'readRate': round(1 - unknown / max(1, words), 4),
               'flaggedBlocks': len(flagged), 'flagged': flagged, 'corrections': len(corrections),
               'correctionList': corrections, 'text': f"data/texts/{e['edition']}.txt", 'sha256': sha,
               'checked': time.strftime('%Y-%m-%d')}
        if e.get('handFixes'):
            rec['handFixes'] = [{k: f[k] for k in ('leaf', 'page', 'ocr', 'reading')} for f in e['handFixes']]
            rec['method'] += (f" {len(e['handFixes'])} misreadings corrected by hand against the page images of this "
                              f"scan, each listed in handFixes; no wording was taken from another edition.")
        if e.get('verifiedWords'):
            rec['verifiedWords'] = e['verifiedWords']
            rec['method'] += (f" {len(e['verifiedWords'])} words the vocabulary does not know (names, Latin, and foreign "
                              f"titles) were checked by hand against the page images and are listed in verifiedWords.")
        rg = read_gate_record(e, words, unknown, info)
        rec['readGate'] = rg
        if info.get('secondOcr'):
            rec['volumes'][0]['secondOcr'] = info['secondOcr']
            rec['method'] += (f" A second OCR ({info['secondOcr']['engine']}, {info['secondOcr']['langs']}) was run on the scan's page "
                              f"images and its reading taken for a line only where it read more words "
                              f"({info['secondOcr']['lineChoices'].get('tesseract', 0)} of "
                              f"{sum(info['secondOcr']['lineChoices'].values())} lines).")
        if info.get('foreignWords'):
            rec['foreignWords'] = info['foreignWords']
            rec['method'] += (" Foreign words were counted as read by language after a random sample of their forms was checked "
                              "against the page images (foreignWords).")
        if e.get('omitted'):
            rec['omitted'] = e['omitted']
        if e.get('layout'):
            rec['layout'] = e['layout']
        if e.get('note'):
            rec['note'] = e['note']
        (ROOT / f"data/sources/{e['edition']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
        print(e['edition'], sha[:12], f"{words} words, read rate {rec['readRate']:.2%}, {len(corrections)} repairs, {len(flagged)} flagged")
        print(json.dumps(rg, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec')
    ap.add_argument('--cache', default='/tmp/transcribe-scan-cache')
    ap.add_argument('--measure', metavar='DIR', help='score only: write DIR/<edition>.json (method and unread forms); host nothing')
    ap.add_argument('--sample', action='store_true', help="print each foreignWords language's sample to check on the images")
    a = ap.parse_args()
    Path(a.cache).mkdir(parents=True, exist_ok=True)
    if a.sample:
        for e in json.loads(Path(a.spec).read_text()):
            for lang, d in (e.get('foreignWords') or {}).items():
                print(e['edition'], lang, json.dumps(foreign_sample(e['edition'], lang, d['forms']), ensure_ascii=False))
    else:
        main(a.spec, a.cache, a.measure)
