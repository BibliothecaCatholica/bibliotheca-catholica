#!/usr/bin/env python3
"""Structured-text pilot (Orthodoxy, PR #24): an intermediate structure file from Project Gutenberg's own HTML.

Owner decision (Micah, November 14, 2026): use the hosted edition's own HTML (#130), structure only. Nothing is
borrowed from #16769; its pinned file stays as reference evidence only.

The intermediate file (data/structured/<work>-<edition>.json) holds STRUCTURE ONLY, keyed to the block indexes of the
hosted TXT (the same indexes the reader's anchors, saved notes, and chapter pages use: blank-line split, as
splitText() in scripts/library.js and text_split() in tools/build_static.py). It never holds the book's words.
Renderers keep taking every character from data/texts/<file>.txt, so this pipeline cannot change wording.

Fidelity gate (run here and in tests/test_structured_text.py):
  1. The TXT and the pinned HTML match their recorded SHA-256 checksums.
  2. Every HTML block in the book body matches exactly one TXT block, in order, word for word (whitespace and the
     HTML's line wrapping are the only differences allowed).
  3. Every TXT block between Gutenberg's START and END markers is covered by an HTML block, except the ones listed
     in ALLOWED_TXT_ONLY with a reason.
  4. The Chapter IV formatting pilot (readerFormatting in data/library.json) is carried over unchanged, with its
     evidence, and still validates against the TXT.

  python3 tools/structure_text.py           build data/structured/*.json and print the gate report
  python3 tools/structure_text.py --check   gate only; exit 1 on any failure (no writes)
"""
import argparse, gzip, hashlib, html, json, re, sys, unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from reader_formatting import validate_formatting  # noqa: E402

# One entry per pilot edition. Only Orthodoxy is built; the registry shape is for later editions.
EDITIONS = {
    ('orthodoxy', 'pg-130'): {
        'html': 'data/sources/gutenberg-html/pg130-images.json',
        'out': 'data/structured/orthodoxy-pg-130.json',
        # TXT blocks inside the markers that the HTML body does not carry, with the reason.
        'allowed_txt_only': {},
    },
}


def norm(s):
    s = unicodedata.normalize('NFC', html.unescape(s))
    return re.sub(r'\s+', ' ', s).strip()


# The only typographic difference the gate accepts between Gutenberg's HTML and its TXT: the HTML sets an em dash
# where the plain-text file has two hyphens. Each one is counted in the gate report; nothing else is folded.
TYPOGRAPHIC = (('\u2014', '--'),)


def match_key(s):
    s = norm(s)
    for a, b in TYPOGRAPHIC:
        s = s.replace(a, b)
    return s


def txt_blocks(path):
    raw = (ROOT / path).read_text(encoding='utf-8-sig').replace('\r', '')
    return [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip()]


class Body(HTMLParser):
    """Collect block-level elements (headings and paragraphs) in document order, with their text and line breaks."""
    BLOCK = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.cur, self.marks = [], None, {'i': 0, 'em': 0, 'b': 0, 'br': 0}

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK and self.cur is None:
            self.cur = {'tag': tag, 'id': dict(attrs).get('id'), 'text': '', 'br': 0}
        elif tag == 'br' and self.cur is not None:
            self.cur['br'] += 1
            self.cur['text'] += '\n'
        if tag in self.marks:
            self.marks[tag] += 1

    def handle_endtag(self, tag):
        if self.cur is not None and tag == self.cur['tag']:
            self.blocks.append(self.cur)
            self.cur = None

    def handle_data(self, data):
        if self.cur is not None:
            self.cur['text'] += data


def html_body(rec):
    data = gzip.decompress((ROOT / rec['file']).read_bytes())
    assert hashlib.sha256(data).hexdigest() == rec['sha256'], 'pinned HTML does not match its recorded checksum'
    doc = data.decode('utf-8')
    a, b = doc.find('*** START OF'), doc.find('*** END OF')
    assert a > 0 and b > a, 'Gutenberg markers not found in the HTML'
    doc = doc[doc.find('</', a):b]  # from the element closing the START marker line
    p = Body()
    p.feed(doc)
    return [x for x in p.blocks if norm(x['text'])], p.marks


ROMAN = re.compile(r'^(?P<num>[IVXLC]+)\.?\s+(?P<title>.+)$')


def classify(h, k, blocks):
    """Role of one HTML block, from its own tag and position only (no inference about verse or emphasis)."""
    t, txt = h['tag'], norm(h['text'])
    if t == 'p' and h['br'] >= 3:
        return {'role': 'contents'}
    if t in ('h1', 'h2'):
        return {'role': 'heading', 'level': 1}
    if t == 'h3':
        m = ROMAN.match(txt)
        if m:
            return {'role': 'chapter', 'num': m.group('num'), 'title': m.group('title')}
        return {'role': 'title'}
    if t in ('h4', 'h5', 'h6'):
        return {'role': 'byline'}
    return {'role': 'paragraph'}


def build(work, edition, spec, write=True):
    lib = json.loads((ROOT / 'data/library.json').read_text())
    w = next(x for x in lib['works'] if x['id'] == work)
    e = next(x for x in w['editions'] if x['id'] == edition)
    tb = (ROOT / e['text']).read_bytes()
    problems = []
    if hashlib.sha256(tb).hexdigest() != e['sha256']:
        problems.append('TXT checksum differs from data/library.json')
    B = txt_blocks(e['text'])
    start = next(i for i, b in enumerate(B) if re.search(r'\*\*\* ?START OF', b))
    end = next(i for i, b in enumerate(B) if re.search(r'\*\*\* ?END OF', b))
    rec = json.loads((ROOT / spec['html']).read_text())
    H, marks = html_body(rec)

    # Gate 2: in-order, word-for-word alignment of every HTML block to one TXT block.
    rows, cur, k, dashes, joined = [], start + 1, 0, 0, []
    keys = {i: match_key(B[i]) for i in range(start + 1, end)}
    while k < len(H):
        h, hit = H[k], None
        # one HTML block, or up to three consecutive ones that the HTML splits where the TXT keeps one paragraph
        for span in (1, 2, 3):
            want = match_key(' '.join(x['text'] for x in H[k:k + span]))
            j = next((i for i in range(cur, end) if keys[i] == want), None)
            if j is not None:
                hit = (j, span, want)
                break
        if hit is None:
            problems.append('HTML block %d (%s %s) has no TXT block with the same words after %d: %r' % (k, h['tag'], h['id'], cur, norm(h['text'])[:70]))
            k += 1
            continue
        j, span, want = hit
        dashes += sum(norm(x['text']).count('\u2014') for x in H[k:k + span])
        if span > 1:
            joined.append({'block': j, 'html': [x['id'] or x['tag'] for x in H[k:k + span]]})
        rows.append(dict(classify(h, k, H), block=j, html=h['id'] or h['tag'], words=len(want.split())))
        cur, k = j + 1, k + span
    # Gate 3: coverage of the TXT body.
    covered = {r['block'] for r in rows}
    for i in range(start + 1, end):
        if i not in covered and str(i) not in spec['allowed_txt_only']:
            problems.append('TXT block %d is not in the HTML body: %r' % (i, B[i][:70]))
    # Gate 4: the Chapter IV pilot carried over unchanged and still valid.
    f = e.get('readerFormatting')
    try:
        validate_formatting(e, B)
    except AssertionError as err:
        problems.append('readerFormatting no longer validates: %s' % err)

    chapters, ch = [], [r for r in rows if r['role'] == 'chapter']
    for n, r in enumerate(ch):
        last = (ch[n + 1]['block'] - 1) if n + 1 < len(ch) else max(x['block'] for x in rows)
        body = [x for x in rows if r['block'] < x['block'] <= last and x['role'] == 'paragraph']
        chapters.append({'num': r['num'], 'title': r['title'], 'heading': r['block'], 'start': body[0]['block'] if body else r['block'],
                         'end': last, 'paragraphs': len(body), 'words': sum(x['words'] for x in body)})
    out = {
        'note': 'Generated by tools/structure_text.py. Structure only, keyed to block indexes of the hosted TXT; '
                'no body text is stored here (only chapter labels) and renderers take every character from the TXT. Do not edit by hand.',
        'work': work, 'edition': edition,
        'decision': 'Micah, November 14, 2026: use the hosted edition\'s own HTML (#130), structure only; nothing from #16769.',
        'txt': {'file': e['text'], 'sha256': e['sha256'], 'blocks': len(B), 'bodyStart': start + 1, 'bodyEnd': end - 1},
        'html': {'file': rec['file'], 'sha256': rec['sha256'], 'url': rec['url'], 'retrieved': rec['retrieved'],
                 'markup': {'italics': marks['i'] + marks['em'], 'bold': marks['b'], 'lineBreaks': marks['br']}},
        'blocks': [{k: r[k] for k in ('block', 'role', 'num', 'title', 'level') if k in r} for r in rows],
        'chapters': chapters,
        'formatting': ({'source': 'data/library.json readerFormatting (scan-verified Chapter IV pilot, unchanged)',
                        'evidence': f['evidence'], 'verse': f['verse'], 'emphasis': f.get('emphasis', [])} if f else None),
        'gate': {'htmlBlocks': len(H), 'matched': len(rows), 'txtBodyBlocks': end - start - 1, 'uncovered': [],
                 'wordChanges': 0, 'typographic': {'em dash in HTML = two hyphens in TXT': dashes},
                 'joinedHtmlBlocks': joined, 'passed': not problems},
    }
    if write and not problems:
        p = ROOT / spec['out']
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    return out, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    bad = 0
    for (work, edition), spec in EDITIONS.items():
        out, problems = build(work, edition, spec, write=not a.check)
        g = out['gate']
        print('%s/%s: %d HTML blocks, %d matched to TXT blocks, %d TXT body blocks, %d chapters, italics in source HTML: %d'
              % (work, edition, g['htmlBlocks'], g['matched'], g['txtBodyBlocks'], len(out['chapters']), out['html']['markup']['italics']))
        for p in problems:
            print('  GATE FAIL:', p)
        if a.check and not problems:
            stored = json.loads((ROOT / spec['out']).read_text())
            if stored != out:
                print('  GATE FAIL: %s is out of date; run tools/structure_text.py' % spec['out'])
                problems.append('stale')
        bad += bool(problems)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
