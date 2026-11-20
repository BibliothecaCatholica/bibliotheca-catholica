#!/usr/bin/env python3
"""Structured-text pilot (Orthodoxy, PR #24): an intermediate structure file from Project Gutenberg's own HTML.

Orthodoxy uses the hosted edition's own HTML (#130), structure only. Nothing is
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
        # Step 2b, per-edition presentation overrides. No characters change: a role override
        # only changes a block's class, and 'front' blocks move into the reader's collapsed front matter (and the
        # EPUB's notice appendix). Each override names the block by index and checks its exact text.
        'presentation': {
            'decision': 'Step 2b: centre the "by" line as a byline and move the '
                        'proofreader\'s credit line into the collapsed front matter; no characters change; the same in the EPUB.',
            'roles': {11: ('by', 'byline')},
            'front': {9: 'This etext was proofread by Martin Ward'},
        },
    },
    ('story-of-a-soul', 'pg-16772'): {
        'html': 'data/sources/gutenberg-html/pg16772-images.json',
        'out': 'data/structured/story-of-a-soul-pg-16772.json',
        'allowed_txt_only': {},
        'decision': 'Story of a Soul is built with accent-insensitive matching in the fidelity '
                    'check (the displayed text still comes from the hosted TXT) and with the italics from its own '
                    'Gutenberg HTML; verse stays as the source\'s line breaks; bracketed notes stay as plain text. '
                    'A line break next to "--" in the TXT is ignored '
                    'for comparison only, in the two places where the HTML has none).',
        'fold': True,       # accent- and ligature-insensitive block matching (fold_accents)
        'italics': True,    # the HTML's <i> spans, mapped to TXT character offsets
        'classify': 'headings',  # h1 title; h4/h5 "CHAPTER N TITLE" chapters; other h4/h5 headings; no contents guess
    },
}
# Map mode (editions batch 1, November 15, 2026): structure from the edition's existing chapter or story map
# (tools/text_pages.py, checked against the TXT by tools/build_text_pages.py), with no HTML. Only the mapped heading
# blocks get a role; nothing else is inferred.
for _wid, _ed in (('innocence-father-brown', 'pg-204'), ('wisdom-father-brown', 'pg-223'), ('secret-father-brown', 'pg-70175'),
                  ('incredulity-father-brown', 'se-incredulity-father-brown'),
                  # editions batch 2 (November 15, 2026)
                  ('heretics', 'pg-470'), ('ball-and-cross', 'pg-5265'), ('man-thursday', 'pg-1695'),
                  ('chesterton-francis', 'pg-63084'), ('grammar-assent', 'pg-34022'), ('development-doctrine', 'pg-35110'),
                  ('paradoxes-catholicism', 'pg-16309'), ('life-of-teresa', 'pg-8120'), ('apologia', 'pg-19690'),
                  ('virgin-saints-and-martyrs', 'pg-53841'),
                  # Chesterton editions (November 15, 2026)
                  ('catholic-church-conversion', 'pg-76305'), ('ballad-white-horse', 'pg-1719'), ('whats-wrong-world', 'pg-1717'),
                  ('manalive', 'pg-1718'), ('club-queer-trades', 'pg-1696'), ('short-history-england', 'pg-20897'),
                  ('man-who-knew-too-much', 'pg-1720'), ('flying-inn', 'pg-59239'), ('trees-of-pride', 'pg-1721'),
                  # Orthodoxy flow batch 1 (November 19, 2026)
                  ('confessions', 'pg-3296'), ('betrothed', 'pg-35155'), ('revelations-divine-love', 'pg-52958'),
                  # Orthodoxy flow batch 2 (November 19, 2026)
                  ('bede-ecclesiastical-history', 'pg-38326'), ('consolation-philosophy', 'pg-14328'), ('abandonment', 'pg-52057'),
                  # Orthodoxy flow batch 3 (November 20, 2026)
                  ('catherine-letters', 'pg-7403'), ('apostolic-fathers', 'pg-77576'), ('europe-faith', 'pg-8442'),
                  # Orthodoxy flow batch 4 (November 20, 2026)
                  ('idea-university', 'pg-24526'), ('aquinas-prayer-contemplative', 'pg-22295'), ('glories-of-mary', 'pg-72411'),
                  # Councils Part 3 (November 20, 2026)
                  ('council-of-trent', 'peo-trent-1848')):
    EDITIONS[(_wid, _ed)] = {'mode': 'map', 'out': 'data/structured/%s-%s.json' % (_wid, _ed)}


def norm(s):
    s = unicodedata.normalize('NFC', html.unescape(s))
    return re.sub(r'\s+', ' ', s).strip()


# The only typographic difference the gate accepts between Gutenberg's HTML and its TXT: the HTML sets an em dash
# where the plain-text file has two hyphens. Each one is counted in the gate report; nothing else is folded.
TYPOGRAPHIC = (('\u2014', '--'),)


LIGATURES = {'æ': 'ae', 'Æ': 'AE', 'œ': 'oe', 'Œ': 'OE'}


def fold_accents(s):
    """Accent-insensitive form (owner decision for Story of a Soul, November 14, 2026): the pinned HTML drops accents
    and ligatures that the TXT keeps (Therese for Thérèse, anaemia for anæmia). Used only to match blocks; the
    displayed text always comes from the TXT."""
    s = ''.join(LIGATURES.get(c, c) for c in s)
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def match_key(s, fold=False):
    s = norm(s)
    for a, b in TYPOGRAPHIC:
        s = s.replace(a, b)
    # Story of a Soul: the TXT marks italics with _underscores_ where the HTML uses <i>; both are dropped for matching.
    # Spaces next to "--" are ignored too: the TXT's hard wraps can put a line break before "--" where the HTML has
    # none (two places in Story of a Soul; counted in the gate report).
    return re.sub(r'\s*--\s*', '--', re.sub(r'\s+', ' ', fold_accents(s).replace('_', ''))).strip() if fold else s


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
            self.cur = {'tag': tag, 'id': dict(attrs).get('id'), 'text': '', 'br': 0, 'it': [], 'open': []}
        elif tag == 'br' and self.cur is not None:
            self.cur['br'] += 1
            self.cur['text'] += '\n'
        if tag in self.marks:
            self.marks[tag] += 1
        if tag in ('i', 'em') and self.cur is not None:
            self.cur['open'].append(len(self.cur['text']))

    def handle_endtag(self, tag):
        if tag in ('i', 'em') and self.cur is not None and self.cur['open']:
            a = self.cur['open'].pop()
            if not self.cur['open']:
                self.cur['it'].append([a, len(self.cur['text'])])
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


CHAPTER = re.compile(r'^CHAPTER (?P<num>[IVXL]+)\.? (?P<title>.+)$')


def classify(h, k, blocks, mode=None):
    """Role of one HTML block, from its own tag and position only (no inference about verse or emphasis)."""
    t, txt = h['tag'], norm(h['text'])
    if mode == 'headings':  # Story of a Soul: heading levels are inconsistent (h4 and h5), so only the tag family counts
        if t == 'h1':
            return {'role': 'title'}
        if t in ('h2', 'h3', 'h4', 'h5', 'h6'):
            m = CHAPTER.match(txt)
            if m:
                return {'role': 'chapter', 'num': m.group('num'), 'title': m.group('title').title()}
            return {'role': 'heading', 'level': 2}
        return {'role': 'paragraph'}
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


def _skeleton(text, skip):
    """(comparable characters, index of each in text): whitespace and characters in skip dropped, accents folded."""
    chars, idx = [], []
    for n, c in enumerate(text):
        if c.isspace() or c in skip:
            continue
        for f in fold_accents(c).replace('\u2014', '--'):
            chars.append(f)
            idx.append(n)
    return ''.join(chars), idx


def italic_spans(rows, H, B):
    """Map each HTML <i> span to [block, start, end] in the TXT block, character by character on a skeleton that
    ignores whitespace, underscores, accents, and the em-dash spelling. Spans the TXT already marks with paired
    underscores (auto_layout.underscore_spans) are left to that marking."""
    from auto_layout import underscore_spans
    out, report = [], {'htmlSpans': 0, 'mapped': 0, 'alreadyUnderscored': 0, 'unmapped': 0}
    for r in rows:
        if r.get('part') == 2:
            continue
        parts, it, at = H[r['k']:r['k'] + r['span']], [], 0
        for x in parts:
            it += [[a + at, b + at] for a, b in x['it']]
            at += len(x['text']) + 1
        if not it:
            continue
        htxt = ' '.join(x['text'] for x in parts)
        bl = [r['block']] + ([r['also']] if r.get('also') else [])
        hs, hidx = _skeleton(htxt, '_')  # underscores in the HTML are rules, not markers
        ts, tidx, tblk = '', [], []
        for b in bl:
            c, i = _skeleton(B[b], '_')
            ts, tidx, tblk = ts + c, tidx + i, tblk + [b] * len(i)
        under = {b: underscore_spans(B[b]) for b in bl}
        for a, b in it:
            report['htmlSpans'] += 1
            sa = next((n for n, i in enumerate(hidx) if i >= a), None)
            sb = next((n for n in range(len(hidx) - 1, -1, -1) if hidx[n] < b), None)
            if hs != ts or sa is None or sb is None or sb < sa:
                report['unmapped'] += 1
                continue
            if tblk[sa] != tblk[sb]:
                report['unmapped'] += 1
                continue
            blk, ta, tb = tblk[sa], tidx[sa], tidx[sb] + 1
            if any(ua <= ta and tb <= ub for ua, ub in under[blk]):
                report['alreadyUnderscored'] += 1
                continue
            if '_' in B[blk][ta:tb]:
                report['unmapped'] += 1
                continue
            if ta and tb < len(B[blk]) and B[blk][ta - 1] == '_' and B[blk][tb] == '_':
                out.append([blk, ta - 1, tb + 1, 1])  # the TXT's own underscores, which auto layout could not pair: kept, hidden on screen
            else:
                out.append([blk, ta, tb])
            report['mapped'] += 1
    return out, report


def build_map(work, edition, spec, write=True):
    import build_text_pages as BTP, text_pages as TP
    lib = json.loads((ROOT / 'data/library.json').read_text())
    w = next(x for x in lib['works'] if x['id'] == work)
    e = next(x for x in w['editions'] if x['id'] == edition)
    problems = []
    tb = (ROOT / e['text']).read_bytes()
    if hashlib.sha256(tb).hexdigest() != e['sha256']:
        problems.append('TXT checksum differs from data/library.json')
    B = txt_blocks(e['text'])
    tp = TP.WORKS[work]
    assert tp['edition'] == edition
    items = BTP.items_for(work, tp, BTP.split_text(tb.decode('utf-8')))
    start = next(i for i, b in enumerate(B) if re.search(r'\*\*\* ?START OF', b))
    end = next(i for i, b in enumerate(B) if re.search(r'\*\*\* ?END OF', b))
    for x in items:
        if not (start < x['heading'] < end):
            problems.append('heading %d is outside the text body' % x['heading'])
    out = {
        'note': 'Generated by tools/structure_text.py (map mode). Structure only, keyed to block indexes of the hosted TXT: '
                'the mapped heading blocks of tools/text_pages.py. No body text is stored here and renderers take every character from the TXT.',
        'work': work, 'edition': edition,
        'decision': 'Structure from the edition\'s chapter or story map; only the mapped headings get a role.',
        'txt': {'file': e['text'], 'sha256': e['sha256'], 'blocks': len(B), 'bodyStart': start + 1, 'bodyEnd': end - 1},
        'source': 'chapter map (tools/text_pages.py), %d %s' % (len(items), tp['nouns'].lower()),
        # the heading block is the chapter; a separate title line under it and a division heading between parts
        # ("PART II.") are headings; plate captions and rules between parts get no role
        'blocks': sorted([{'block': x['heading'], 'role': 'chapter'} for x in items]
                         + [{'block': i, 'role': 'heading'} for x in items for i in x.get('titleBlocks', [])]
                         + [{'block': i, 'role': 'heading'} for x in items for i in x.get('before', [])
                            if re.search(r'[A-Za-z]', B[i]) and not B[i].startswith('[')], key=lambda r: r['block']),
        'chapters': [dict({'num': x['num'], 'title': x['title'], 'heading': x['heading'], 'start': x['start'], 'end': x['end'], 'words': x['words']},
                          **({'before': x['before']} if x.get('before') else {})) for x in items],
        'presentation': None, 'formatting': None,
        'gate': {'mode': 'map', 'headings': len(items), 'wordChanges': 0, 'passed': not problems},
    }
    if write and not problems:
        (ROOT / spec['out']).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    return out, problems


def build(work, edition, spec, write=True):
    if spec.get('mode') == 'map':
        return build_map(work, edition, spec, write)
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
    rows, cur, k, dashes, joined, split = [], start + 1, 0, 0, [], []
    fold = bool(spec.get('fold'))
    keys = {i: match_key(B[i], fold) for i in range(start + 1, end)}
    while k < len(H):
        h, hit = H[k], None
        # one HTML block, or up to three consecutive ones that the HTML splits where the TXT keeps one paragraph
        for span in (1, 2, 3):
            want = match_key(' '.join(x['text'] for x in H[k:k + span]), fold)
            j = next((i for i in range(cur, end) if keys[i] == want), None)
            if j is not None:
                hit = (j, span, want)
                break
        if hit is None and fold:
            # the TXT splits one HTML paragraph into two consecutive blocks (Story of a Soul has one such place)
            want = match_key(h['text'], fold)
            j = next((i for i in range(cur, end - 1) if keys[i] + ' ' + keys[i + 1] == want), None)
            if j is not None:
                split.append({'blocks': [j, j + 1], 'html': h['id'] or h['tag']})
                rows.append(dict(classify(h, k, H, spec.get('classify')), block=j, html=h['id'] or h['tag'], words=len(B[j].split()), k=k, span=1, also=j + 1))
                rows.append(dict(role='paragraph', block=j + 1, html=h['id'] or h['tag'], words=len(B[j + 1].split()), k=k, span=1, part=2))
                cur, k = j + 2, k + 1
                continue
        if hit is None:
            problems.append('HTML block %d (%s %s) has no TXT block with the same words after %d: %r' % (k, h['tag'], h['id'], cur, norm(h['text'])[:70]))
            k += 1
            continue
        j, span, want = hit
        dashes += sum(norm(x['text']).count('\u2014') for x in H[k:k + span])
        if span > 1:
            joined.append({'block': j, 'html': [x['id'] or x['tag'] for x in H[k:k + span]]})
        rows.append(dict(classify(h, k, H, spec.get('classify')), block=j, html=h['id'] or h['tag'], words=len(want.split()), k=k, span=span))
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

    folded = sum(1 for r in rows if fold and match_key(B[r['block']]) != match_key(' '.join(x['text'] for x in H[r['k']:r['k'] + r['span']])))
    underscored = sum(1 for r in rows if fold and '_' in B[r['block']])
    dash_space = sum(1 for r in rows if fold and re.search(r'\s--|--\s', match_key(B[r['block']]).replace('_', '')) and not re.search(r'\s--|--\s', match_key(' '.join(x['text'] for x in H[r['k']:r['k'] + r['span']]))))
    em, em_report = (italic_spans(rows, H, B) if spec.get('italics') else ([], None))
    if em_report and em_report['unmapped']:
        problems.append('%d HTML italic spans could not be mapped to the TXT' % em_report['unmapped'])
    # Step 2b: presentation overrides, each checked against the exact TXT block.
    pres = spec.get('presentation') or {}
    overrides = []
    for b, (text, role) in sorted(pres.get('roles', {}).items()):
        r = next((x for x in rows if x['block'] == b), None)
        if r is None or B[b] != text:
            problems.append('presentation override for block %d does not match the TXT: %r' % (b, B[b][:40]))
            continue
        overrides.append({'block': b, 'role': role, 'was': r['role']})
        r['role'] = role
    front = []
    for b, prefix in sorted(pres.get('front', {}).items()):
        if not B[b].startswith(prefix) or not (start < b < end):
            problems.append('front-matter override for block %d does not match the TXT: %r' % (b, B[b][:40]))
            continue
        front.append(b)
    if front and front != list(range(start + 1, start + 1 + len(front))):
        problems.append('front-matter blocks must follow the START marker directly: %r' % front)
    chapters, ch = [], [r for r in rows if r['role'] == 'chapter']
    if spec.get('classify') == 'headings':
        # a chapter ends at the next chapter or heading (Story of a Soul: "END OF THE AUTOBIOGRAPHY" closes Chapter XI);
        # its label is taken from the TXT block, which keeps the accents the HTML drops
        small = {'a', 'an', 'and', 'of', 'the', 'to', 'in', 'on', 'for'}
        for r in ch:
            m = CHAPTER.match(norm(B[r['block']]))
            r['title'] = ' '.join(w.capitalize() if n == 0 or w.lower() not in small else w.lower() for n, w in enumerate(m.group('title').split()))
    stops = sorted(x['block'] for x in rows if x['role'] in ('chapter', 'heading')) if spec.get('classify') == 'headings' else None
    for n, r in enumerate(ch):
        last = (ch[n + 1]['block'] - 1) if n + 1 < len(ch) else max(x['block'] for x in rows)
        if stops:
            last = min([b - 1 for b in stops if b > r['block']] + [last])
        body = [x for x in rows if r['block'] < x['block'] <= last and x['role'] == 'paragraph']
        chapters.append({'num': r['num'], 'title': r['title'], 'heading': r['block'], 'start': body[0]['block'] if body else r['block'],
                         'end': last, 'paragraphs': len(body), 'words': sum(x['words'] for x in body)})
    out = {
        'note': 'Generated by tools/structure_text.py. Structure only, keyed to block indexes of the hosted TXT; '
                'no body text is stored here (only chapter labels) and renderers take every character from the TXT. Do not edit by hand.',
        'work': work, 'edition': edition,
        'decision': spec.get('decision', 'The hosted edition\'s own HTML (#130), structure only; nothing from #16769.'),
        'txt': {'file': e['text'], 'sha256': e['sha256'], 'blocks': len(B), 'bodyStart': start + 1, 'bodyEnd': end - 1},
        'html': {'file': rec['file'], 'sha256': rec['sha256'], 'url': rec['url'], 'retrieved': rec['retrieved'],
                 'markup': {'italics': marks['i'] + marks['em'], 'bold': marks['b'], 'lineBreaks': marks['br']}},
        'blocks': [{k: r[k] for k in ('block', 'role', 'num', 'title', 'level') if k in r} for r in rows],
        'emphasis': ({'source': 'the pinned HTML\'s <i> spans, as [block, start, end] offsets into the TXT block ([block, start, end, 1] when the span includes the TXT\'s own underscores, which stay in the text and are hidden on screen); spans auto layout already shows from paired underscores are left to it',
                      'spans': em, 'report': em_report} if spec.get('italics') else None),
        'chapters': chapters,
        'presentation': ({'decision': pres['decision'], 'roles': overrides, 'front': front} if pres else None),
        'formatting': ({'source': 'data/library.json readerFormatting (scan-verified Chapter IV pilot, unchanged)',
                        'evidence': f['evidence'], 'verse': f['verse'], 'emphasis': f.get('emphasis', [])} if f else None),
        'gate': {'htmlBlocks': len(H), 'matched': len(rows), 'txtBodyBlocks': end - start - 1, 'uncovered': [],
                 'wordChanges': 0, 'typographic': dict({'em dash in HTML = two hyphens in TXT': dashes}, **({'accents, ligatures, or TXT underscores folded (blocks)': folded, 'TXT blocks with underscores for the HTML italics': underscored, 'line break next to two hyphens in TXT (blocks)': dash_space} if fold else {})),
                 'joinedHtmlBlocks': joined, **({'splitTxtBlocks': split} if split else {}), 'passed': not problems},
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
        if g.get('mode') == 'map':
            print('%s/%s: map mode, %d headings from the chapter map' % (work, edition, g['headings']))
        else:
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
