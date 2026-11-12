"""Opt-in presentation only. Never alter source characters or paragraph indexes.

Mirror renderReadingBlock() in scripts/library.js. No inferred prose/verse rules.
"""
import html


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


def reading_block(edition, text, index, anchor=False):
    f = edition.get('readerFormatting')
    active = f and f['sha256'] == edition['sha256']
    verse = next((v for v in f['verse'] if v['block'] == index), None) if active else None
    prose = active and any(lo <= index <= hi for lo, hi in f['proseRanges'])
    cls = 'reading-verse' if verse else 'reading-prose' if prose else ''
    content = html.escape(text)
    if active and not verse:
        at, parts = 0, []
        for item in f.get('emphasis', []):
            if item['block'] == index:
                a, b = item['start'], item['end']
                parts += [html.escape(text[at:a]), '<em>'+html.escape(text[a:b])+'</em>']
                at = b
        content = ''.join(parts)+html.escape(text[at:])
    if verse:
        starts = verse['lineStarts'] + [len(text)]
        content = ''.join('<span class="verse-line">'+html.escape(text[a:b])+'</span>'
                          for a, b in zip(starts, starts[1:]))
    return '<p'+(' id="reading-p-'+str(index)+'"' if anchor else '')+(' class="'+cls+'"' if cls else '')+'>'+content+'</p>'


def formatting_note(edition):
    f = edition.get('readerFormatting')
    if not f:
        return ''
    return '<p class="small text-formatting">'+html.escape(f['note'])+' <a href="'+html.escape(f['evidence'])+'" target="_blank" rel="noopener">Formatting witness ↗</a></p>'
