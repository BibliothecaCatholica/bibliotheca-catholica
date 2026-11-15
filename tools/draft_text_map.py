#!/usr/bin/env python3
"""Draft a chapter map for tools/text_pages.py from a hosted text's own headings (agent efficiency, November 15, 2026).

    python3 tools/draft_text_map.py <work-id> [--edition ID] [--kind ch|story] [--start-after TEXT]
                                              [--end-before TEXT] [--heading REGEX]

Reads the hosted TXT (never writes it), finds heading blocks the file itself prints (CHAPTER I, BOOK II, "IV. Title",
or a bare numeral line followed by a title line), skips a contents list, and prints a WORKS entry in the same shape as
the hand-made ones: slug, number label, title, heading block exactly as in the file, and the first and last words of
each part. The draft is then run through build_text_pages.items_for(), the same check `npm run build` applies, and
each part's word count is shown so a reviewer can spot a missed or spurious heading. Paste the entry into WORKS only
after reading it; headings the file does not print are never invented (docs/HOSTED-EDITIONS.md, rule 3).
Exit 2 when no headings are found: the book then stays reader-only until its headings are mapped by hand.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_text_pages import items_for, norm, split_text  # noqa: E402

ROMAN = r'[IVXLC]+'
NUM = rf'(?:{ROMAN}|\d+)'
PATTERNS = [
    rf'(?i)^(?:chapter|book|part|story|lecture|sermon|essay)\s+(?P<num>{NUM}|[a-z]+)\b[.:]?\s*(?P<title>.*)$',
    rf'^(?P<num>{ROMAN})\.?\s+(?P<title>\S.*)$',
]
SMALL = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'from', 'in', 'into', 'nor', 'of', 'on', 'or', 'the', 'to', 'with'}
WORDNUM = {w: i + 1 for i, w in enumerate('one two three four five six seven eight nine ten eleven twelve thirteen fourteen '
                                         'fifteen sixteen seventeen eighteen nineteen twenty'.split())}


def title_case(s):
    s = re.sub(r'\s+', ' ', s).strip(' .:-—')
    if s != s.upper():
        return s
    out = []
    for i, w in enumerate(s.lower().split()):
        out.append(w if i and w in SMALL else w[:1].upper() + w[1:])
    return ' '.join(out)


def slug(n, title):
    base = re.sub(r'[^a-z0-9]+', '-', title.lower().replace('’', '').replace("'", '')).strip('-') or 'part'
    s = '%02d-%s' % (n, base)
    while len(s) > 60:
        s = s.rsplit('-', 1)[0]
    return s


def titleish(t):
    """A heading title, not a sentence: no closing colon or dash, and most words capitalised (small words aside)."""
    t = t.strip()
    if not t:
        return True
    if t.endswith((':', '--', ',', ';')) or re.search(r'\s\d+$', t):
        return False
    ws = [w for w in re.findall(r"[A-Za-z][\w'’]*", t) if w.lower() not in SMALL]
    if ws and sum(w[0].isupper() for w in ws) / len(ws) >= 0.6:
        return True
    return t[0].isupper() and len(t.split()) <= 8 and not t.endswith(('.', '!', '?'))  # "On the negative spirit"


def heading_at(B, i, rx):
    """(heading, num, title) if block i (or blocks i, i+1) is a heading, else None."""
    b = B[i]
    if '\n' in b.strip() and len(b) > 160:
        return None
    one = ' '.join(b.replace('_', ' ').split())  # Gutenberg _italic_ headings match on their words
    if len(one) > 120 or re.search(r'\s\d+$', one):  # a contents line ending in a page number
        return None
    for pat in ([rx] if rx else PATTERNS):
        m = re.match(pat, one)
        if m:
            num = m.groupdict().get('num') or ''
            title = (m.groupdict().get('title') or '').strip()
            if not rx and not titleish(title):
                continue
            nxt = ' '.join(B[i + 1].replace('_', ' ').split()) if i + 1 < len(B) else ''
            if not title and 0 < len(nxt) <= 100 and titleish(nxt) and not re.match(pat, nxt):
                return ((b, B[i + 1]), num, nxt)  # numeral line, then title line
            return (b, num, title or one)
    if re.fullmatch(ROMAN + r'\.?', one) and i + 1 < len(B):
        nxt = ' '.join(B[i + 1].replace('_', ' ').split())
        if 0 < len(nxt) <= 100 and titleish(nxt):
            return ((b, B[i + 1]), one.rstrip('.'), nxt)
    return None


def draft(work_id, edition=None, kind=None, start_after=None, end_before=None, rx=None):
    lib = json.loads((ROOT / 'data/library.json').read_text())
    work = next(w for w in lib['works'] if w['id'] == work_id)
    ed = next(e for e in work['editions'] if e.get('text') and (edition in (None, e['id'])))
    B = split_text((ROOT / ed['text']).read_text(encoding='utf-8'))
    end = next(i for i, b in enumerate(B) if re.search(r'\*\*\* ?END OF (THE |THIS )?(PROJECT GUTENBERG|HOSTED TEXT)', b, re.I))
    if end_before:
        end = next(i for i in range(len(B)) if norm(B[i]) == norm(end_before))
    begin = next((i for i, b in enumerate(B) if re.search(r'\*\*\* ?START OF', b, re.I)), -1)
    if start_after:
        begin = next(i for i, b in enumerate(B) if norm(b) == norm(start_after))
    found, i = [], begin + 1
    while i < end:
        h = heading_at(B, i, rx)
        if h:
            found.append((i,) + h)
            i += 2 if isinstance(h[0], tuple) else 1
        else:
            i += 1
    # A contents list repeats the headings with no text between them: keep only headings followed by a body
    # (the next block is not itself a heading) and drop earlier copies of a heading that recurs.
    body = [f for k, f in enumerate(found) if (k + 1 == len(found) or found[k + 1][0] > f[0] + (2 if isinstance(f[1], tuple) else 1) + 1)]
    seen, keep = {}, []
    for f in body:
        key = norm(' '.join(f[1]) if isinstance(f[1], tuple) else f[1])
        if key in seen:
            keep = [g for g in keep if g is not seen[key]]
        seen[key] = f
        keep.append(f)
    if not keep:
        return None
    first = keep[0][0]
    if not start_after:
        # start_after: the nearest block before the first heading whose first occurrence in the file is that block
        j = first - 1
        while j > begin and next(k for k, b in enumerate(B) if norm(b) == norm(B[j])) != j:
            j -= 1
        start_after = B[j]
    kind = kind or ('story' if re.search(r'father brown|stories|tales', work['title'], re.I) else 'ch')
    parts = []
    for n, (i, head, num, title) in enumerate(keep, 1):
        label = num.upper() if re.fullmatch(ROMAN, num.upper()) else str(WORDNUM.get(num.lower(), num or n))
        t = title_case(title)
        parts.append([slug(n, t), label, t, head, '', ''])
    spec = dict(edition=ed['id'], kind=kind, start_after=start_after, parts=[tuple(p) for p in parts])
    if end_before:
        spec['end_before'] = end_before
    items = items_for(work_id, spec, B)
    for p, it in zip(parts, items):
        p[4] = ' '.join(re.sub(r'\s+', ' ', B[it['start']]).split()[:9])
        p[5] = ' '.join(re.sub(r'\s+', ' ', B[it['end']]).split()[-6:])
    spec['parts'] = [tuple(p) for p in parts]
    items = items_for(work_id, spec, B)  # the filled draft passes the builder's own checks
    return spec, items


def render(work_id, spec):
    noun, nouns = ('Story', 'Stories') if spec['kind'] == 'story' else ('Chapter', 'Chapters')
    lines = [f" {work_id!r}: dict(edition={spec['edition']!r}, kind={spec['kind']!r}, noun={noun!r}, nouns={nouns!r},",
             f"  start_after={spec['start_after']!r},"]
    if spec.get('end_before'):
        lines.append(f"  end_before={spec['end_before']!r},")
    lines.append('  parts=[')
    lines += [f'   {p!r},' for p in spec['parts']]
    lines.append('  ]),')
    return '\n'.join(lines)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('work')
    ap.add_argument('--edition')
    ap.add_argument('--kind', choices=('ch', 'story'))
    ap.add_argument('--start-after')
    ap.add_argument('--end-before')
    ap.add_argument('--heading', help='custom regex with optional (?P<num>) and (?P<title>) groups')
    a = ap.parse_args()
    out = draft(a.work, a.edition, a.kind, a.start_after, a.end_before, a.heading)
    if not out:
        print(f'{a.work}: no headings found; leave it reader-only or map it by hand.', file=sys.stderr)
        sys.exit(2)
    spec, items = out
    print(render(a.work, spec))
    for p, it in zip(spec['parts'], items):
        flag = '  <- check' if it['words'] < 300 else ''
        print(f'# {p[0]}: blocks {it["start"]}-{it["end"]}, {it["words"]:,} words{flag}', file=sys.stderr)
