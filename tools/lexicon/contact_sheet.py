#!/usr/bin/env python3
"""Faster hand pass: group a book's remaining unread forms, crop every occurrence from the scan's own page image, and
pre-fill a candidate reading from the verified lexicon, so a reviewer can confirm forms in batches.

  python3 tools/lexicon/contact_sheet.py SPEC --cache DIR --out DIR [--edition ID] [--per-sheet 30] [--sheet-scale 0.5]

Writes to --out (a scratch directory: the sheets are working files and are never committed):
  index.html        the contact sheet: one group per form, its crops, a pre-filled reading, and an export box
  sheets/NN.png     the same crops as numbered image sheets, for reviewing without a browser
  occurrences.json  every occurrence (leaf, printed page, line as chosen, crop) with its candidates
Nothing here counts a word as read. The reviewer looks at each crop, and only the decisions they record in the spec
(verifiedWords for a form printed that way, handFixes for a misreading) change the score; see --apply.

  python3 tools/lexicon/contact_sheet.py SPEC --edition ID --out DIR --apply DECISIONS.json
DECISIONS.json maps a form to {"printed": true} (verified as printed on every crop) or {"reading": "..."} (a misreading,
fixed on every listed line), each with "checked" (the date) and optionally "only": [occurrence ids] to limit it.
"""
import argparse, collections, html, json, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import transcribe_scan as T  # noqa: E402
import build_lexicon as L  # noqa: E402

CORE = re.compile(r"^[^\w]+|[^\w]+$")


def chosen_pages(e, cache, V):
    """The scan's lines per leaf exactly as build() sees them before layout: archive.org OCR, the per-line second OCR,
    and the hand fixes already recorded."""
    xml, _ = T.fetch(e['ia'], cache)
    objs = ET.fromstring(xml).findall('.//OBJECT')[e['firstLeaf']:e['lastLeaf'] + 1]
    raw = [(int(o.get('height') or 3000), T.page_lines(o)) for o in objs]
    foreign, _ = T.foreign_read(e)
    verified = set(e.get('verifiedWords', [])) | foreign
    if e.get('secondOcr'):
        T.second_ocr(e, objs, raw, cache, V, verified)
    T.apply_hand_fixes(raw, e)
    return objs, raw


def occurrences(e, objs, raw, forms):
    out = []
    for i, (_, lines) in enumerate(raw):
        leaf = e['firstLeaf'] + i
        for li, l in enumerate(lines):
            toks = l['text'].split(' ')
            for ti, t in enumerate(toks):
                c = CORE.sub('', t)
                if c in forms:
                    start = len(' '.join(toks[:ti])) + (1 if ti else 0)
                    out.append({'form': c, 'leaf': leaf, 'line': l['text'], 'lineIndex': li, 'box': [l['x'], l['top'], l['x2'], l['y']],
                                'span': [start / max(1, len(l['text'])), (start + len(t)) / max(1, len(l['text']))],
                                'engine': l.get('engine', 'archive.org'), 'obj': i})
    return out


def crop(e, objs, o, cache, dest):
    from PIL import Image, ImageDraw
    obj = objs[o['obj']]
    img = Image.open(T.page_image(e['ia'], obj, cache, 1)).convert('RGB')
    k = img.width / int(obj.get('width'))
    x, top, x2, y = (int(v * k) for v in o['box'])
    pad = max(12, (y - top) // 2)
    box = (max(0, x - pad), max(0, top - pad), min(img.width, x2 + pad), min(img.height, y + pad))
    c = img.crop(box)
    d = ImageDraw.Draw(c)
    wx, wx2 = x + (x2 - x) * o['span'][0] - box[0], x + (x2 - x) * o['span'][1] - box[0]
    d.rectangle([max(0, wx - 4), 1, min(c.width - 1, wx2 + 4), c.height - 2], outline=(220, 30, 30), width=2)
    c.save(dest, quality=88)
    return c


def groups_of(occ, forms, lex):
    by_form = collections.defaultdict(list)
    for o in occ:
        by_form[o['form']].append(o)
    out = []
    for f, n in forms.items():
        cands = L.candidates(f, lex)
        out.append({'form': f, 'count': n, 'located': by_form.get(f, []), 'candidates': cands,
                    'key': (cands[0]['reading'] if cands else f).lower()})
    # forms that share a candidate sit together; then by how many words the group clears
    tally = collections.Counter()
    for g in out:
        tally[g['key']] += g['count']
    out.sort(key=lambda g: (-tally[g['key']], g['key'], -g['count'], g['form']))
    return out


def write_html(e, groups, out):
    esc = html.escape
    rows = []
    for gi, g in enumerate(groups, 1):
        pre = g['candidates'][0]['reading'] if g['candidates'] else g['form']
        why = '; '.join(f"{esc(c['reading'])} ({esc(c['why'])})" for c in g['candidates'][:3]) or 'no lexicon candidate'
        crops = ''.join(f"<figure><img src='crops/{o['id']}.jpg' alt='Leaf {o['leaf']}: {esc(o['line'])}' loading='lazy'>"
                        f"<figcaption>{esc(o['id'])} · leaf {o['leaf']} · {esc(o['engine'])}</figcaption></figure>" for o in g['located'])
        missing = g['count'] - len(g['located'])
        rows.append(f"""<section class='g' data-form='{esc(g['form'], True)}'>
<h2>{gi}. <code>{esc(g['form'])}</code> × {g['count']}</h2>
<p class='why'>Candidates: {why}{f'; {missing} occurrence(s) not located line by line (joined across a line break)' if missing > 0 else ''}</p>
<p><label><input type='radio' name='v{gi}' value='printed'> printed as read</label>
<label><input type='radio' name='v{gi}' value='reading'> misread; reading <input type='text' value='{esc(pre, True)}' aria-label='Reading for {esc(g['form'], True)}'></label>
<label><input type='radio' name='v{gi}' value='' checked> not decided</label></p>
<div class='crops'>{crops}</div></section>""")
    page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Hand pass: {esc(e['edition'])}</title>
<meta name='robots' content='noindex'><style>
body{{font:15px/1.4 system-ui,sans-serif;margin:16px;background:#fff;color:#111}} .g{{border-top:1px solid #ccc;padding:8px 0}}
.crops{{display:flex;flex-wrap:wrap;gap:8px}} figure{{margin:0}} img{{max-width:100%;border:1px solid #ddd}}
figcaption{{font-size:12px;color:#555}} .why{{color:#444}} textarea{{width:100%;height:12em}}</style></head><body>
<h1>Hand pass: {esc(e['edition'])}</h1>
<p>{len(groups)} unread forms. Every reading is only a candidate until it is checked on the crop, which is cut from this scan's own page image.
Mark each group, then export the decisions and apply them with <code>contact_sheet.py --apply</code>.</p>
{''.join(rows)}
<h2>Decisions</h2><button type='button' id='x'>Export</button><textarea id='out' aria-label='Decisions JSON'></textarea>
<script>document.getElementById('x').onclick=()=>{{const d={{}},t=new Date().toISOString().slice(0,10);
document.querySelectorAll('.g').forEach(s=>{{const r=s.querySelector('input[type=radio]:checked');if(!r||!r.value)return;
d[s.dataset.form]=r.value==='printed'?{{printed:true,checked:t}}:{{reading:s.querySelector('input[type=text]').value,checked:t}};}});
document.getElementById('out').value=JSON.stringify(d,null,1);}};</script></body></html>
"""
    (out / 'index.html').write_text(page, encoding='utf-8')


def write_sheets(groups, out, per_sheet, scale=0.5):
    from PIL import Image, ImageDraw
    items = [(g, o) for g in groups for o in g['located']]
    (out / 'sheets').mkdir(exist_ok=True)
    for s in range(0, len(items), per_sheet):
        chunk = items[s:s + per_sheet]
        ims = [Image.open(out / 'crops' / f"{o['id']}.jpg") for _, o in chunk]
        ims = [i.resize((max(1, int(i.width * scale)), max(1, int(i.height * scale)))) for i in ims]
        w = min(900, max(i.width for i in ims))
        scaled = [i if i.width <= w else i.resize((w, int(i.height * w / i.width))) for i in ims]
        H = sum(i.height + 22 for i in scaled)
        sheet = Image.new('RGB', (w, H), 'white')
        d = ImageDraw.Draw(sheet)
        yy = 0
        for (g, o), i in zip(chunk, scaled):
            cand = g['candidates'][0]['reading'] if g['candidates'] else '-'
            d.text((4, yy + 4), f"{o['id']}  {g['form']}  ->  {cand}   (leaf {o['leaf']})", fill=(0, 0, 160))
            sheet.paste(i, (0, yy + 20))
            yy += i.height + 22
        sheet.save(out / 'sheets' / f'{s // per_sheet + 1:02d}.png')


def apply(spec, edition, out, decisions):
    data = json.loads(Path(spec).read_text(encoding='utf-8'))
    e = next(x for x in data if x['edition'] == edition)
    occ = {o['id']: o for o in json.loads((out / 'occurrences.json').read_text(encoding='utf-8'))}
    vw, fixes = list(e.get('verifiedWords', [])), list(e.get('handFixes', []))
    for form, d in json.loads(Path(decisions).read_text(encoding='utf-8')).items():
        assert d.get('checked'), (form, 'record the date the crops were checked')
        if d.get('printed'):
            if form not in vw:
                vw.append(form)
            continue
        assert d.get('reading') and d['reading'] != form, (form, d)
        lines = collections.OrderedDict()
        for o in occ.values():
            if o['form'] == form and (not d.get('only') or o['id'] in d['only']):
                lines[(o['leaf'], o['line'])] = o
        for (leaf, line), o in lines.items():
            new = ' '.join(t.replace(form, d['reading'], 1) if CORE.sub('', t) == form else t for t in line.split(' '))
            fixes.append({'leaf': leaf, 'page': o.get('page'), 'ocr': line, 'reading': new})
    e['verifiedWords'], e['handFixes'] = vw, fixes
    Path(spec).write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(edition, len(vw), 'verified words,', len(fixes), 'hand fixes')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--cache', default=None)
    ap.add_argument('--out', required=True)
    ap.add_argument('--edition')
    ap.add_argument('--per-sheet', type=int, default=30)
    ap.add_argument('--sheet-scale', type=float, default=0.5)
    ap.add_argument('--apply')
    a = ap.parse_args()
    out = Path(a.out)
    specs = json.loads(Path(a.spec).read_text(encoding='utf-8'))
    e = next(x for x in specs if not a.edition or x['edition'] == a.edition)
    if a.apply:
        return apply(a.spec, e['edition'], out, a.apply)
    assert a.cache, '--cache is required to build a sheet'
    assert not str(out.resolve()).startswith(str(HERE.parent.parent.resolve()) + '/'), 'write sheets outside the repository'
    (out / 'crops').mkdir(parents=True, exist_ok=True)
    V = T.vocabulary()
    _, _, _, words, unknown, _, _, info = T.build(e, a.cache, V)
    forms = dict(info['unread'].most_common())
    objs, raw = chosen_pages(e, a.cache, V)
    occ = occurrences(e, objs, raw, forms)
    for n, o in enumerate(occ, 1):
        o['id'] = f'o{n:04d}'
        crop(e, objs, o, a.cache, out / 'crops' / f"{o['id']}.jpg")
    lex = L.load_built()
    groups = groups_of(occ, forms, lex)
    for o in occ:
        o['candidates'] = [c['reading'] for c in L.candidates(o['form'], lex)]
    (out / 'occurrences.json').write_text(json.dumps(occ, ensure_ascii=False, indent=1), encoding='utf-8')
    write_html(e, groups, out)
    write_sheets(groups, out, a.per_sheet, a.sheet_scale)
    gate = int(words * (1 - 0.995))
    print(f"{e['edition']}: {unknown} unread of {words} ({1 - unknown / words:.2%}); gate allows {gate}; "
          f"{len(forms)} forms, {len(occ)} occurrences located; with candidates: {sum(1 for g in groups if g['candidates'])}")


if __name__ == '__main__':
    main()
