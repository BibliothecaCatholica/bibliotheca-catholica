#!/usr/bin/env python3
"""Hosted-edition counts, computed once, and the docs that state them (agent efficiency, November 15, 2026).

    python3 tools/hosted_counts.py            print the counts
    python3 tools/hosted_counts.py --check    exit 1 if any doc below states a stale count
    python3 tools/hosted_counts.py --write    rewrite those counts in place (run after adding or removing a book)

The counts come from data/library.json, data/structured/, tools/text_pages.py (PART_D, the chapter openers),
and downloads/epub/. Tests compare against `count()`, so adding a book needs no test edits; `tests/test_hosted_counts.py`
runs --check, so a stale count in a doc fails CI instead of being found by the next reader.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def count():
    lib = json.loads((ROOT / 'data/library.json').read_text())
    eds = [e for w in lib['works'] for e in w['editions']]
    import text_pages
    pg = [e for e in eds if 'gutenberg.org' in json.dumps(e['source'])]
    return {
        'pg': len(pg),
        'pg_hosted': sum(1 for e in pg if e.get('text')),
        'works': len(lib['works']),
        'editions': len(eds),
        'hosted': sum(1 for e in eds if e.get('text') and not e.get('retired')),  # public count: retired files are served, not counted
        'retired': sum(1 for e in eds if e.get('text') and e.get('retired')),
        'hosted_works': sum(1 for w in lib['works'] if any(e.get('text') for e in w['editions'])),
        'structured': len(list((ROOT / 'data/structured').glob('*.json'))),
        'openers': len(__import__('build_text_pages').PART_D),
        'epubs': len(list((ROOT / 'downloads/epub').glob('*.epub'))),
        'mapped': len(text_pages.WORKS),
    }


# (file, regex with named groups, which count each group holds). Each pattern must match exactly once.
STATED = [
    ('README.md', r'(?P<works>\d+) individual work records, including (?P<hosted>\d+) hosted reading editions', None),
    ('README.md', r'The (?P<hosted>\d+) hosted text editions', None),
    ('CENTRAL.md', r'(?P<works>\d+) work records; (?P<hosted>\d+) hosted editions of (?P<hosted_works>\d+) works', None),
    ('docs/CATALOG.md', r'The (?P<hosted>\d+) hosted TXT editions', None),
    ('docs/CATALOG.md', r'(?P<pg>\d+) Gutenberg editions in the catalog, (?P<pg_hosted>\d+) hosted', None),
    ('docs/HOSTED-TEXT-QUALITY.md', r'has (?P<works>\d+) works and (?P<editions>\d+) edition records\. Only (?P<hosted>\d+) editions, belonging to (?P<hosted_works>\d+) works', None),
    ('docs/HOSTED-TEXT-QUALITY.md', r'for each of the (?P<hosted>\d+) editions', None),
    ('docs/HOSTED-EDITIONS.md', r'(?P<hosted>\d+) hosted editions: (?P<structured>\d+) with a structure file, (?P<openers>\d+) with chapter openers, (?P<hosted__cover>\d+) with a cover, (?P<epubs>\d+) with a published EPUB', None),
]


def stale(c=None):
    c = c or count()
    out = []
    for path, pat, _ in STATED:
        text = (ROOT / path).read_text()
        hits = list(re.finditer(pat, text))
        if len(hits) != 1:
            out.append((path, pat, f'pattern matched {len(hits)} times'))
            continue
        for name, val in hits[0].groupdict().items():
            want = c[name.split('__')[0]]
            if int(val) != want:
                out.append((path, name, f'states {val}, actual {want}'))
    return out


def write(c=None):
    c = c or count()
    for path, pat, _ in STATED:
        p = ROOT / path
        text = p.read_text()

        def fix(m):
            s, base, parts = m.group(0), m.start(), []
            last = 0
            for name in m.re.groupindex:
                a, b = m.span(name)
                parts.append(s[last:a - base] + str(c[name.split('__')[0]]))
                last = b - base
            return ''.join(parts) + s[last:]
        p.write_text(re.sub(pat, fix, text, count=1))


if __name__ == '__main__':
    c = count()
    if '--write' in sys.argv:
        write(c)
    problems = stale(c)
    if '--check' in sys.argv or '--write' in sys.argv:
        for p in problems:
            print('stale:', *p)
        sys.exit(1 if problems else 0)
    print(json.dumps(c, indent=1))
