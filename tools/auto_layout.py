#!/usr/bin/env python3
"""Automatic, display-only layout for hosted editions (step 2a, PR #24).

Automatic, display-only prose reflow and underscore italics are allowed on hosted editions under fixed safeguards.
This tool applies those safeguards and writes, per
hosted edition, which blocks may reflow and which _underscored_ spans render as emphasis. No character of any hosted
text changes: renderers still take every character from data/texts/, and the underscores stay in the TXT, the
download, and the page text (hidden on screen only).

The rule, for each blank-line block of the TXT body (between the START and END markers when present):
  * Single-line blocks are untouched.
  * A block is left exactly as today if any non-first line is indented, any line is all capitals, or it contains a
    run of three or more spaces between words.
  * Otherwise it reflows only if every line break is a wrap: the line (as it stands in the file, first-line indent
    included) plus one space plus the next line's first word reaches the file's wrap width (98th percentile of its
    non-blank line lengths) minus 14 characters.
  * Where a pinned Gutenberg HTML exists for the edition (data/sources/gutenberg-html/), a block reflows only if the
    HTML also marks it as an ordinary paragraph (a <p> without line breaks).
  * Paired _underscores_ inside one block render as emphasis (a block whose underscores do not pair cleanly gets none).
  * Scan-verified formatting (readerFormatting in data/library.json, Orthodoxy Chapter IV) takes precedence: those
    blocks are left to it.
  * Excluded by name: Divine Comedy, The Ballad of the White Horse, Poems of Gerard Manley Hopkins, The Dream of
    Gerontius, The Legends of Saint Patrick. Every other edition is on; its coverage (share of multi-line blocks
    reflowed) is listed in the report. Known verse the rule misreads is kept by block (KEEP).

Output: data/auto-layout/<edition>.json (bound to the TXT's SHA-256) for each edition that is on, and
data/auto-layout/report.json (counts per edition, exclusions, the spot-check sample). Part of `npm run build`.

  python3 tools/auto_layout.py
"""
import gzip, hashlib, html, json, random, re, sys, unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/auto-layout'
EXCLUDE = {
    'divine-comedy': 'Divine Comedy (verse)',
    'ballad-white-horse': 'The Ballad of the White Horse (verse)',
    'hopkins-poems': 'Poems of Gerard Manley Hopkins (verse)',
    'dream-gerontius': 'The Dream of Gerontius (verse)',
    'legends-of-saint-patrick': 'The Legends of Saint Patrick (verse)',
    'prudentius-eulalia': 'Prudentius, Peristephanon III (verse)',
}
# Known verse the rule cannot tell from prose: keep the file's own line breaks.
KEEP = {('pg-130', 123): 'known verse (quoted stanza)', ('pg-1695', 22): 'known verse (last stanza of the dedication)'}
MARGIN = 14
START = re.compile(r'\*\*\* ?START OF (THE |THIS )?(PROJECT GUTENBERG|HOSTED TEXT)', re.I)
END = re.compile(r'\*\*\* ?END OF (THE |THIS )?(PROJECT GUTENBERG|HOSTED TEXT)', re.I)
LABEL = 'Automatic layout: wrapped lines are joined and _underscored_ words shown in italics for easier reading. The text is unchanged; turn on Original line breaks in the Aa menu to see the file as it is.'


def raw_blocks(raw):
    """The reader's blocks (splitText in scripts/library.js) with the raw form kept, so a first-line indent counts."""
    out = []
    for p in re.split(r'\n\s*\n', raw.replace('\r', '')):
        if p.strip():
            out.append((p.strip(), p.strip('\n')))
    return out


def wrap_width(raw):
    L = sorted(len(l.rstrip()) for l in raw.replace('\r', '').split('\n') if l.strip())
    return L[int(0.98 * (len(L) - 1))] if L else 0


def all_caps(line):
    letters = [c for c in line if c.isalpha()]
    return len(letters) >= 2 and all(c.isupper() for c in letters)


def decide(raw_block, width):
    """'reflow', or the reason the block stays as it is."""
    lines = raw_block.split('\n')
    if len(lines) < 2:
        return 'single line'
    if any(l[:1].isspace() for l in lines[1:]):
        return 'indented line'
    if any(all_caps(l) for l in lines):
        return 'all-capitals line'
    if re.search(r'\S {3,}\S', raw_block):
        return 'run of spaces'
    for a, b in zip(lines, lines[1:]):
        first = b.split()[0] if b.split() else ''
        if len(a.rstrip()) + 1 + len(first) < width - MARGIN:
            return 'short line'
    return 'reflow'


def underscore_spans(text):
    """Paired _underscores_ in one block: [(start, end)] with both underscores inside the span, or [] if they do not
    pair cleanly. Runs of two or more underscores (rules, blanks) are not markers and leave the block alone."""
    if re.search(r'__', text):
        return []
    marks = [m.start() for m in re.finditer(r'_', text)]
    if not marks or len(marks) % 2:
        return []
    spans = []
    for a, b in zip(marks[::2], marks[1::2]):
        before = text[a - 1] if a else ' '
        after = text[b + 1] if b + 1 < len(text) else ' '
        inner = text[a + 1:b]
        if before.isalnum() or after.isalnum() or not inner.strip() or inner[0].isspace() or inner[-1].isspace():
            return []
        spans.append((a, b + 1))
    return spans


def fold(s):
    s = unicodedata.normalize('NFKD', html.unescape(s))
    s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace('æ', 'ae').replace('œ', 'oe').replace('—', ' ').replace('--', ' ')
    return ' '.join(re.findall(r"[a-z0-9]+", s))


class Paras(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.cur = [], None

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'blockquote') and self.cur is None:
            self.cur = [tag, '', 0]
        elif tag == 'br' and self.cur is not None:
            self.cur[2] += 1
            self.cur[1] += ' '

    def handle_endtag(self, tag):
        if self.cur is not None and tag == self.cur[0]:
            self.out.append(tuple(self.cur))
            self.cur = None

    def handle_data(self, d):
        if self.cur is not None:
            self.cur[1] += d


def html_records():
    recs = {}
    for p in sorted((ROOT / 'data/sources/gutenberg-html').glob('*.json')):
        r = json.loads(p.read_text())
        recs['pg-%d' % r['id']] = r
    return recs


def html_ordinary(rec):
    """Folded-text keys of the blocks the pinned HTML marks as ordinary paragraphs (and of everything it marks)."""
    data = gzip.decompress((ROOT / rec['file']).read_bytes())
    assert hashlib.sha256(data).hexdigest() == rec['sha256'], rec['file'] + ' does not match its record'
    doc = data.decode('utf-8')
    a, b = doc.find('*** START OF'), doc.find('*** END OF')
    p = Paras()
    p.feed(doc[a:b] if a > 0 and b > a else doc)
    ordinary = {fold(t) for tag, t, br in p.out if tag == 'p' and br == 0 and fold(t)}
    return ordinary


def edition_layout(w, e, recs):
    raw = (ROOT / e['text']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == e['sha256'], e['id'] + ': TXT changed'
    text = raw.decode('utf-8-sig')
    RB = raw_blocks(text)
    B = [b for b, r in RB]
    s = next((i + 1 for i, b in enumerate(B) if START.search(b)), 0)
    t = next((i for i, b in enumerate(B) if END.search(b)), len(B))
    width = wrap_width(text)
    f = e.get('readerFormatting')
    verified = set()
    if f and f.get('sha256') == e['sha256']:
        for lo, hi in f['proseRanges']:
            verified.update(range(lo, hi + 1))
        verified.update(v['block'] for v in f['verse'])
        verified.update(x['block'] for x in f.get('emphasis', []))
    ordinary = html_ordinary(recs[e['id']]) if e['id'] in recs else None
    reflow, kept, reasons, multi = [], [], {}, 0
    for i in range(s, t):
        d = decide(RB[i][1], width)
        if d == 'single line':
            continue
        multi += 1
        if i in verified:
            d = 'scan-verified formatting'
        elif (e['id'], i) in KEEP:
            d = KEEP[(e['id'], i)]
        elif d == 'reflow' and ordinary is not None and fold(B[i]) not in ordinary:
            d = 'not an ordinary paragraph in the pinned HTML'
        if d == 'reflow':
            reflow.append(i)
        else:
            kept.append(i)
            reasons[d] = reasons.get(d, 0) + 1
    em = [[i, a, b] for i in range(s, t) if i not in verified for a, b in underscore_spans(B[i])]
    ranges = []
    for i in reflow:
        if ranges and ranges[-1][1] == i - 1:
            ranges[-1][1] = i
        else:
            ranges.append([i, i])
    share = len(reflow) / multi if multi else 0.0
    from reader_formatting import structure_for
    st = structure_for(e)
    return {
        **({'structure': st} if st else {}),  # roles and italics from data/structured/ for editions without chapter pages
        'edition': e['id'], 'work': w['id'], 'sha256': e['sha256'], 'wrapWidth': width, 'threshold': width - MARGIN,
        'body': [s, t - 1], 'reflow': ranges, 'em': em,
        'stats': {'multiLineBlocks': multi, 'reflowed': len(reflow), 'kept': len(kept), 'share': round(share, 3),
                  'keptBecause': dict(sorted(reasons.items())), 'emphasisSpans': len(em),
                  'pinnedHtml': e['id'] in recs},
    }, reflow


def build(write=True):
    lib = json.loads((ROOT / 'data/library.json').read_text())
    recs = html_records()
    report = {'note': 'Generated by tools/auto_layout.py. Display-only layout; no hosted text changes.',
              'rule': {'wrapWidth': '98th percentile of the file\'s non-blank line lengths', 'margin': MARGIN,
                       'keep': ['%s block %d: %s' % (k[0], k[1], v) for k, v in sorted(KEEP.items())]},
              'label': LABEL, 'editions': {}, 'excluded': {}, 'spotCheck': []}
    files, pool = {}, []
    for w in lib['works']:
        for e in w['editions']:
            if not e.get('text'):
                continue
            if w['id'] in EXCLUDE:
                report['excluded'][e['id']] = EXCLUDE[w['id']]
                continue
            lay, reflow = edition_layout(w, e, recs)
            st = lay['stats']
            row = dict(work=w['title'], **{k: st[k] for k in ('multiLineBlocks', 'reflowed', 'kept', 'share', 'emphasisSpans', 'pinnedHtml', 'keptBecause')})
            report['editions'][e['id']] = row
            files[e['id']] = lay
            pool += [(e['id'], i) for i in reflow]
    rnd = random.Random(20261114)
    report['spotCheck'] = [{'edition': ed, 'block': i} for ed, i in sorted(rnd.sample(pool, min(20, len(pool))))]
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        keep = set(files) | {'report'}
        for p in OUT.glob('*.json'):
            if p.stem not in keep:
                p.unlink()
        for k, v in files.items():
            (OUT / (k + '.json')).write_text(json.dumps(v, ensure_ascii=False, separators=(',', ':')) + '\n')
        (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    return files, report


if __name__ == '__main__':
    files, rep = build()
    on = rep['editions']
    print('auto layout: %d editions on (%d blocks reflowed, %d kept, %d emphasis spans); %d excluded by name'
          % (len(on), sum(r['reflowed'] for r in on.values()), sum(r['kept'] for r in on.values()),
             sum(r['emphasisSpans'] for r in on.values()), len(rep['excluded'])))
