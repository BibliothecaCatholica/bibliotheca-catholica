#!/usr/bin/env python3
"""Typographic covers for hosted editions (Part D, "Beautiful editions"): title, author, and the site's cross mark,
in burgundy, cream, and gold, one series design with a small variation by category. No photographs or third-party art.

Three candidate designs were drawn; design C, "Banded", is the one in use. `--build` writes the C cover of every
hosted edition: assets/covers/<edition>.svg (deterministic, checked by tests/test_covers.py), and, rendered in a
browser with the site's own fonts (tools/render_covers.js, Playwright), <edition>.webp (480 by 720) and
<edition>-og.jpg (1200 by 630, the social image), with SHA-256 checksums in data/covers.json.

  python3 tools/covers.py --sheet OUT.html   # contact sheet: every design for a sample of editions
  python3 tools/covers.py --build            # the chosen design for every hosted edition (needs Node and Playwright)
"""
import argparse, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W, H = 600, 900
BURGUNDY, DEEP, CREAM, PAPER, GOLD, INK = '#8b1e2d', '#5e1420', '#fff8ea', '#f6f0e2', '#c9a24a', '#2a2118'
DISPLAY = "'Cormorant Garamond','EB Garamond',Georgia,serif"
SERIF = "'EB Garamond',Georgia,serif"
# The small variation by category: an ornament glyph from the site's existing typographic set.
ORNAMENT = {'Theology': '✠', 'Spiritual life': '❦', 'Biography': '❧', 'Literature': '✦', 'Apologetics': '✥',
            'History': '⁂', 'Poetry': '❀', 'Philosophy': '◆', 'Church Fathers': '✙', 'Art': '✿', 'Education': '✧'}
DESIGNS = {'A': 'Rubric: a burgundy field, a gold double frame, the cross above a centred title in cream capitals.',
           'B': 'Library: a cream field, a thin burgundy frame, a burgundy title and a gold rule, the cross below.',
           'C': 'Banded: a burgundy upper panel with the title, a cream lower band with the author and the cross.'}


def cross(cx, cy, size, fill):
    """The site's cross mark (assets/favicon.svg, trefoil terminals), scaled to size and centred on (cx, cy)."""
    s = size / 64.0
    parts = ['<rect x="28" y="11" width="8" height="43" rx="4"/>', '<rect x="11" y="26" width="42" height="8" rx="4"/>']
    for x, y, r in ((32, 8, 4), (27.5, 12, 3.2), (36.5, 12, 3.2), (32, 56, 4), (27.5, 52, 3.2), (36.5, 52, 3.2),
                    (8, 30, 4), (12, 25.5, 3.2), (12, 34.5, 3.2), (56, 30, 4), (52, 25.5, 3.2), (52, 34.5, 3.2)):
        parts.append('<circle cx="%s" cy="%s" r="%s"/>' % (x, y, r))
    return '<g fill="%s" transform="translate(%.1f %.1f) scale(%.4f)">%s</g>' % (fill, cx - 32 * s, cy - 32 * s, s, ''.join(parts))


def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    return lines + ([cur] if cur else [])


def title_lines(title, caps=True):
    t = title.upper() if caps else title
    n = len(t)
    size = (66 if n <= 12 else 60 if n <= 20 else 52 if n <= 32 else 46) if caps else (84 if n <= 12 else 72 if n <= 20 else 62 if n <= 32 else 54)
    per = max(8, int(W * 0.74 / (size * (0.6 if caps else 0.47))))
    lines = wrap(t, per)[:5]
    return lines, size, size * 1.1


def title_svg(lines, size, lh, cx, first_baseline, color, caps=True):
    return ''.join('<text x="%d" y="%.1f" text-anchor="middle" font-family="%s" font-size="%d" font-weight="500" letter-spacing="%s" fill="%s">%s</text>'
                   % (cx, first_baseline + i * lh, DISPLAY, size, '3' if caps else '0', color, html.escape(l)) for i, l in enumerate(lines))


def short_title(t):
    return re.sub(r':.*$', '', t).strip()


def cover_svg(design, title, author, category, volume=''):
    t, a, orn = short_title(title), author, ORNAMENT.get(category, '✦')
    cat = html.escape(category.upper())
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s">' % (W, H, W, H, html.escape(t + ' by ' + a))
    txt = lambda x, y, size, fill, s, **k: '<text x="%d" y="%.1f" text-anchor="middle" font-family="%s" font-size="%d"%s fill="%s">%s</text>' % (
        x, y, k.get('family', SERIF), size, ''.join(' %s="%s"' % (n.replace('_', '-'), v) for n, v in k.items() if n != 'family'), fill, html.escape(s))
    if design == 'A':
        lines, size, lh = title_lines(t)
        block = size + (len(lines) - 1) * lh + 40 + 60  # title, ornament gap, author line
        top = 250 + (520 - block) / 2
        body = ['<rect width="600" height="900" fill="%s"/>' % BURGUNDY,
                '<rect x="28" y="28" width="544" height="844" fill="none" stroke="%s" stroke-width="3"/>' % GOLD,
                '<rect x="40" y="40" width="520" height="820" fill="none" stroke="%s" stroke-width="1"/>' % GOLD,
                cross(300, 160, 84, GOLD),
                title_svg(lines, size, lh, 300, top + size, CREAM)]
        y = top + size + (len(lines) - 1) * lh
        body += [txt(300, y + 56, 30, GOLD, orn), txt(300, y + 112, 27, CREAM, a.upper(), letter_spacing=3),
                 txt(300, 822, 17, GOLD, category.upper(), letter_spacing=5)]
    elif design == 'B':
        lines, size, lh = title_lines(t, caps=False)
        block = size + (len(lines) - 1) * lh + 50 + 70
        top = 150 + (560 - block) / 2
        body = ['<rect width="600" height="900" fill="%s"/>' % CREAM,
                '<rect x="34" y="34" width="532" height="832" fill="none" stroke="%s" stroke-width="2"/>' % BURGUNDY,
                '<rect x="44" y="44" width="512" height="812" fill="none" stroke="%s" stroke-width="0.8"/>' % BURGUNDY,
                txt(300, 108, 17, BURGUNDY, category.upper(), letter_spacing=5),
                title_svg(lines, size, lh, 300, top + size, BURGUNDY, caps=False)]
        y = top + size + (len(lines) - 1) * lh
        body += ['<line x1="240" x2="360" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (y + 42, y + 42, GOLD),
                 txt(300, y + 100, 32, INK, a, font_style='italic'),
                 txt(300, 735, 28, GOLD, orn), cross(300, 800, 56, BURGUNDY)]
    else:  # 'C'
        lines, size, lh = title_lines(t)
        block = size + (len(lines) - 1) * lh
        top = 120 + (470 - block) / 2
        body = ['<rect width="600" height="900" fill="%s"/>' % PAPER, '<rect width="600" height="610" fill="%s"/>' % BURGUNDY,
                '<rect y="610" width="600" height="8" fill="%s"/>' % GOLD,
                txt(300, 92, 17, GOLD, orn + '  ' + category.upper(), letter_spacing=5),
                title_svg(lines, size, lh, 300, top + size, CREAM),
                cross(300, 795, 64, BURGUNDY)]
        al = wrap(a.upper(), 30)  # a long author line (The Writings of the Apostolic Fathers) wraps to two smaller lines
        if len(al) == 1:
            body.append(txt(300, 702, 28, INK, al[0], letter_spacing=3))
        else:
            body += [txt(300, 684 + 32 * n, 22, INK, l, letter_spacing=2) for n, l in enumerate(al[:2])]
        if volume:  # multi-volume works: the part or volume in gold small capitals under the title
            y = top + size + (len(lines) - 1) * lh
            body.append(txt(300, min(y + 58, 588), 22, GOLD, volume.upper(), letter_spacing=4))
    return head + ''.join(body) + '</svg>'


def hosted():
    lib = json.loads((ROOT / 'data/library.json').read_text())
    return [(w, e) for w in lib['works'] for e in w['editions'] if e.get('text')]


SAMPLE = ['orthodoxy', 'confessions', 'story-of-a-soul', 'summa-theologiae', 'imitation-of-christ', 'innocence-father-brown',
          'divine-comedy', 'apologia', 'city-of-god', 'hopkins-poems', 'life-of-teresa', 'ballad-white-horse']


def sheet():
    eds = hosted()
    by = {}
    for w, e in eds:
        by.setdefault(w['id'], (w, e))
    picks = [by[k] for k in SAMPLE if k in by]
    picks += [v for k, v in by.items() if k not in SAMPLE][:max(0, 12 - len(picks))]
    rows = []
    for d, desc in DESIGNS.items():
        cells = ''.join('<figure><div class="c">%s</div><figcaption>%s<br><span>%s</span></figcaption></figure>'
                        % (cover_svg(d, w['title'], w['author'], w['category']), html.escape(short_title(w['title'])), html.escape(w['category'])) for w, e in picks)
        rows.append('<section><h2>Design %s</h2><p>%s</p><div class="grid">%s</div></section>' % (d, html.escape(desc), cells))
    return picks, rows


CHOSEN = 'C'
# Editions of one work that need telling apart on the cover (from each edition's label in data/library.json).
VOLUMES = {'pg-17611': 'First Part', 'pg-17897': 'First Part of the Second Part', 'pg-18755': 'Second Part of the Second Part',
           'pg-19950': 'Third Part', 'ia-summa-supplement': 'Supplement', 'pg-45304': 'Volume I', 'pg-45305': 'Volume II'}
OUT = ROOT / 'assets/covers'


def edition_cover(w, e, shared=()):
    """Where several hosted works share a short title (The Lives of the Saints), the subtitle becomes the volume line."""
    vol = VOLUMES.get(e['id'], '')
    if not vol and short_title(w['title']) in shared and ':' in w['title']:
        vol = w['title'].split(':', 1)[1].strip()
    return cover_svg(CHOSEN, w['title'], w['author'], w['category'], vol)


def shared_titles():
    from collections import Counter
    c = Counter(short_title(w['title']) for w in {w['id']: w for w, e in hosted()}.values())
    return {t for t, n in c.items() if n > 1}


def build_svgs():
    import hashlib
    OUT.mkdir(parents=True, exist_ok=True)
    rows, shared = {}, shared_titles()
    for w, e in hosted():
        svg = edition_cover(w, e, shared) + '\n'
        (OUT / (e['id'] + '.svg')).write_text(svg)
        rows[e['id']] = {'work': w['id'], 'svg': hashlib.sha256(svg.encode()).hexdigest()}
    return rows


def build():
    import hashlib, subprocess
    rows = build_svgs()
    subprocess.run(['node', str(ROOT / 'tools/render_covers.js'), str(OUT)] + sorted(rows), check=True, cwd=ROOT)
    from PIL import Image
    for k, r in rows.items():
        png = OUT / (k + '.png')
        im = Image.open(png).convert('RGB')
        im.resize((480, 720), Image.LANCZOS).save(OUT / (k + '.webp'), 'WEBP', quality=86, method=6)
        png.unlink()
        for kind, f in (('webp', k + '.webp'), ('og', k + '-og.jpg')):
            r[kind] = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
    manifest = {'note': 'Generated by tools/covers.py --build. Design C ("Banded"). '
                        'The SVG is the source; the WebP (480x720) and the social JPEG (1200x630) are rendered from it with the site fonts.',
                'design': CHOSEN, 'covers': dict(sorted(rows.items()))}
    (ROOT / 'data/covers.json').write_text(json.dumps(manifest, indent=1) + '\n')
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheet')
    ap.add_argument('--build', action='store_true')
    a = ap.parse_args()
    if a.build:
        m = build()
        print('%d covers (design %s) -> assets/covers/' % (len(m['covers']), m['design']))
        raise SystemExit(0)
    picks, rows = sheet()
    if a.sheet:
        Path(a.sheet).write_text('\n'.join(rows))
        print('%d editions x %d designs -> %s' % (len(picks), len(DESIGNS), a.sheet))
