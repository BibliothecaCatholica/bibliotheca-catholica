"""Opt-in presentation only. Never alter source characters or paragraph indexes.

Mirror renderReadingBlock() in scripts/library.js. No inferred prose/verse rules.
"""
import html
import re


def validate_formatting(edition, blocks):
    f = edition.get('readerFormatting')
    if not f:
        return
    assert f['sha256'] == edition['sha256'], 'Stale reader formatting'
    assert f['note'] and f['evidence'].startswith('https://')
    previous = -1
    for lo, hi in f['proseRanges']:
        assert 0 <= lo <= hi < len(blocks) and lo > previous
        previous = hi
    seen = set()
    for verse in f['verse']:
        i, starts = verse['block'], verse['lineStarts']
        assert i not in seen and any(lo <= i <= hi for lo, hi in f['proseRanges'])
        seen.add(i)
        assert starts[0] == 0 and starts == sorted(set(starts))
        assert all(isinstance(x, int) and 0 <= x < len(blocks[i]) for x in starts)
        # Break at a word boundary, without removing the original whitespace.
        assert all(blocks[i][x-1].isspace() and not blocks[i][x].isspace() for x in starts[1:])

    previous = {}
    for item in f.get('emphasis', []):
        i, a, b = item['block'], item['start'], item['end']
        assert any(lo <= i <= hi for lo, hi in f['proseRanges'])
        assert 0 <= a < b <= len(blocks[i]) and a >= previous.get(i, 0)
        assert blocks[i][a:b] == item['text']
        previous[i] = b
        assert not any(v['block'] == i for v in f['verse']), 'Separate verse/emphasis in this pilot'


def structure_for(edition):
    """The structured-text pilot's roles for this edition (data/structured/*.json from tools/structure_text.py),
    only when built from this exact TXT. Roles are presentation only: the text still comes from the TXT."""
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for p in sorted((root / 'data/structured').glob('*.json')):
        d = json.loads(p.read_text())
        if d.get('edition') == edition.get('id') and d['txt']['sha256'] == edition.get('sha256') and d['gate']['passed']:
            return {'sha256': d['txt']['sha256'], 'source': 'data/structured/' + p.name,
                    'roles': [[b['block'], b['role']] for b in d['blocks'] if b['role'] != 'paragraph'],
                    'front': (d.get('presentation') or {}).get('front', []),
                    'em': (d.get('emphasis') or {}).get('spans', [])}
    return None


def with_structure(edition):
    """A copy of the edition with its structure roles attached (for data/library.js and the static pages)."""
    s = structure_for(edition)
    return dict(edition, structure=s) if s else edition


def auto_layout_for(edition):
    """Automatic display-only layout (tools/auto_layout.py) for this edition, only when built from this exact TXT."""
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / 'data/auto-layout' / (str(edition.get('id')) + '.json')
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    return d if d.get('sha256') == edition.get('sha256') else None


def with_auto_layout(edition):
    a = auto_layout_for(edition)
    return dict(edition, autoLayout=a) if a else edition


def structure_em(edition, index):
    """Italics from the structure file (Story of a Soul: its own HTML's <i> spans), as (start, end, marked)."""
    s = edition.get('structure')
    if not s or s['sha256'] != edition.get('sha256'):
        return []
    return [(x[1], x[2], len(x) > 3) for x in s.get('em', []) if x[0] == index]


def _no_overlap(spans):
    out, at = [], 0
    for x in sorted(spans):
        if x[0] >= at:
            out.append(x)
            at = x[1]
    return out


def _emphasis_html(text, spans, marked):
    """Escape text with <em> spans. marked=True keeps the source's underscores inside the span, hidden on screen;
    marked=None takes it from each (start, end, marked) span."""
    at, parts = 0, []
    for sp in spans:
        a, b = sp[0], sp[1]
        if marked is None:
            m = sp[2]
        else:
            m = marked
        parts.append(html.escape(text[at:a]))
        if m:
            parts.append('<em class="u"><span class="us">_</span>' + html.escape(text[a + 1:b - 1]) + '<span class="us">_</span></em>')
        else:
            parts.append('<em>' + html.escape(text[a:b]) + '</em>')
        at = b
    return ''.join(parts) + html.escape(text[at:])


def block_role(edition, index):
    s = edition.get('structure')
    if not s or s['sha256'] != edition.get('sha256'):
        return ''
    return next((r for b, r in s['roles'] if b == index), '')


def reading_block(edition, text, index, anchor=False):
    """Mirror of renderReadingBlock() in scripts/library.js. Precedence: scan-verified readerFormatting for the blocks
    it covers, then automatic layout (autoLayout); every character of the block is kept, in order."""
    f = edition.get('readerFormatting')
    active = bool(f) and f['sha256'] == edition['sha256']
    verse = next((v for v in f['verse'] if v['block'] == index), None) if active else None
    prose = active and any(lo <= index <= hi for lo, hi in f['proseRanges'])
    vem = [(x['start'], x['end']) for x in (f.get('emphasis', []) if active else []) if x['block'] == index]
    verified = bool(verse or prose or vem)
    a = edition.get('autoLayout')
    auto = bool(a) and not verified and a['sha256'] == edition['sha256']
    if auto:
        prose = any(lo <= index <= hi for lo, hi in a['reflow'])
    sem = [] if verified else structure_em(edition, index)
    role = block_role(edition, index)
    cls = ' '.join(x for x in (('reading-' + role) if role else '', 'reading-verse' if verse else 'reading-prose' if prose else '') if x)
    if verse:
        starts = verse['lineStarts'] + [len(text)]
        content = ''.join('<span class="verse-line">'+html.escape(text[a:b])+'</span>' for a, b in zip(starts, starts[1:]))
    elif role == 'chapter' and re.match(r'^[IVXLC]+ \S', text):
        # Part D chapter opener: the numeral and the title in their own spans; every character is kept, in order
        n = text.index(' ')
        content = '<span class="ch-n">' + html.escape(text[:n]) + '</span> <span class="ch-t">' + html.escape(text[n + 1:]) + '</span>'
    elif vem:
        content = _emphasis_html(text, vem, False)
    elif auto or sem:
        spans = ([(s, e, True) for b, s, e in a['em'] if b == index] if auto else []) + sem
        content = _emphasis_html(text, _no_overlap(spans), None)
    else:
        content = html.escape(text)
    return '<p'+(' id="reading-p-'+str(index)+'"' if anchor else '')+(' class="'+cls+'"' if cls else '')+'>'+content+'</p>'


def formatting_note(edition):
    f = edition.get('readerFormatting')
    if not f:
        return ''
    return '<p class="small text-formatting">'+html.escape(f['note'])+' <a href="'+html.escape(f['evidence'])+'" target="_blank" rel="noopener">Formatting witness ↗</a></p>'
