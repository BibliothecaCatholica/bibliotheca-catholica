#!/usr/bin/env python3
"""Build the verified lexicon, and propose candidate readings for unread OCR forms.

The lexicon is made only of readings already checked against a page image:
  - every verifiedWords entry in docs/research/*/spec*.json (a word confirmed as printed in that scan);
  - word-level OCR -> reading pairs taken from those specs' handFixes (each fix was made against the page image);
  - the automatic repairs listed in sources/confirmed-repairs.json, each checked on the page image afterwards.
Optional seed lists (sources/seeds.json) must record their source and licence.

The lexicon only proposes. A proposed reading counts as read in a book only after a reviewer checks it against that
book's page image and records it in the book's spec (verifiedWords or handFixes). Nothing here changes a score:
tools/transcribe_scan.py never reads the lexicon.

  python3 tools/lexicon/build_lexicon.py            rebuild words/*.json and repairs.json
  python3 tools/lexicon/build_lexicon.py --check    exit 1 if the committed files differ from a fresh build
  python3 tools/lexicon/build_lexicon.py --propose FORM [FORM ...]
"""
import difflib, glob, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from transcribe_scan import CONFUSIONS  # noqa: E402  the tool's own list of OCR confusions
LANGUAGES = ('latin', 'irish', 'german', 'french', 'spanish', 'greek', 'names', 'english')
TOKEN = re.compile(r"^[^\w]*(.*?)[^\w']*$", re.UNICODE)
STATUS = 'candidate: check on this book\'s page image before recording it'


def spec_editions():
    for f in sorted(glob.glob(str(ROOT / 'docs/research/*/spec*.json'))):
        d = json.loads(Path(f).read_text(encoding='utf-8'))
        for e in (d if isinstance(d, list) else d.get('editions', [d])):
            if isinstance(e, dict) and e.get('edition'):
                yield Path(f).relative_to(ROOT).as_posix(), e


def core(tok):
    return TOKEN.match(tok).group(1)


def word_pairs(ocr, reading):
    """Word-level (ocr, reading) pairs from one hand fix: aligned one-for-one replacements of similar words only."""
    a, b = ocr.split(), reading.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != 'replace' or i2 - i1 != j2 - j1:
            continue
        for x, y in zip(a[i1:i2], b[j1:j2]):
            x, y = core(x), core(y)
            if (len(x) >= 3 and x.lower() != y.lower() and re.fullmatch(r"[^\W\d_]+(?:'[^\W\d_]+)?", y)
                    and difflib.SequenceMatcher(None, x.lower(), y.lower()).ratio() >= 0.5):
                out.append((x, y))
    return out


def load(name):
    return json.loads((HERE / 'sources' / name).read_text(encoding='utf-8'))


def build():
    langs = load('languages.json')
    lang_of = {}
    for lang in LANGUAGES:
        for w in langs[lang]:
            assert w not in lang_of, f'{w}: listed under {lang_of[w]} and {lang}'
            lang_of[w] = lang
    words = {lang: {} for lang in LANGUAGES}
    repairs = {}
    seen = set()
    for path, e in spec_editions():
        for w in e.get('verifiedWords', []):
            assert w in lang_of, f'{w} ({e["edition"]}): add it to tools/lexicon/sources/languages.json'
            words[lang_of[w]].setdefault(w, set()).add((e['edition'], path))
            seen.add(w)
        for f in e.get('handFixes', []):
            for x, y in word_pairs(f['ocr'], f['reading']):
                repairs.setdefault((x, y), set()).add((e['edition'], path, 'hand fix'))
    unused = sorted(set(lang_of) - seen)
    assert not unused, f'languages.json lists words no spec verifies: {unused}'
    for r in load('confirmed-repairs.json')['repairs']:
        repairs.setdefault((r['ocr'], r['reading']), set()).add((r['edition'], r['evidence'], 'automatic repair checked on the image'))
    for s in load('seeds.json')['seeds']:
        assert s.get('source') and s.get('url') and s.get('licence') and s.get('language') in LANGUAGES, s
        for w in s['words']:
            words[s['language']].setdefault(w, set()).add((s['source'], s['licence']))
    files = {}
    for lang in LANGUAGES:
        files[f'words/{lang}.json'] = {
            'language': lang,
            'count': len(words[lang]),
            'words': {w: [{'edition': a, 'record': b} for a, b in sorted(words[lang][w])]
                      for w in sorted(words[lang], key=lambda w: (w.lower(), w))}}
    files['repairs.json'] = {
        'count': len(repairs),
        'repairs': [{'ocr': x, 'reading': y, 'from': [{'edition': a, 'record': b, 'kind': k} for a, b, k in sorted(src)]}
                    for (x, y), src in sorted(repairs.items(), key=lambda kv: (kv[0][0].lower(), kv[0]))]}
    return {k: json.dumps(v, ensure_ascii=False, indent=1) + '\n' for k, v in files.items()}


def load_built():
    words = {lang: json.loads((HERE / f'words/{lang}.json').read_text(encoding='utf-8'))['words'] for lang in LANGUAGES}
    repairs = json.loads((HERE / 'repairs.json').read_text(encoding='utf-8'))['repairs']
    return words, repairs


def edits1(w):
    letters = 'abcdefghijklmnopqrstuvwxyzæœéèêëáíóúüöäàâîôûçñ'
    splits = [(w[:i], w[i:]) for i in range(len(w) + 1)]
    return ({a + b[1:] for a, b in splits if b} | {a + c + b[1:] for a, b in splits if b for c in letters}
            | {a + c + b for a, b in splits for c in letters} | {a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1})


def candidates(form, lexicon=None):
    """Proposed readings for one unread form, best first. Each is only a candidate (see STATUS)."""
    words, repairs = lexicon or load_built()
    index = {}
    for lang, ws in words.items():
        for w in ws:
            index.setdefault(w.lower(), []).append((w, lang))
    out = []

    def add(reading, lang, why):
        if all(c['reading'] != reading for c in out):
            out.append({'form': form, 'reading': reading, 'language': lang, 'why': why, 'status': STATUS})

    for r in repairs:
        if r['ocr'] == form:
            add(r['reading'], None, 'the same OCR form was read as this on a page image in ' + r['from'][0]['edition'])
    for w, lang in index.get(form.lower(), []):
        add(w, lang, 'verified as printed in ' + words[lang][w][0]['edition'])
    for a, b in CONFUSIONS:
        i = form.find(a)
        while i >= 0:
            c = form[:i] + b + form[i + len(a):]
            for w, lang in index.get(c.lower(), []):
                add(w, lang, f'OCR confusion {a!r} for {b!r}; verified in ' + words[lang][w][0]['edition'])
            i = form.find(a, i + 1)
    if len(form) >= 5:
        for c in sorted(edits1(form.lower())):
            for w, lang in index.get(c, []):
                add(w, lang, 'one letter from a word verified in ' + words[lang][w][0]['edition'])
    return out


def main(argv):
    if argv[:1] == ['--propose']:
        lex = load_built()
        for f in argv[1:]:
            print(json.dumps({'form': f, 'candidates': candidates(f, lex)}, ensure_ascii=False))
        return 0
    files = build()
    if argv[:1] == ['--check']:
        stale = [k for k, v in files.items() if not (HERE / k).exists() or (HERE / k).read_text(encoding='utf-8') != v]
        if stale:
            print('tools/lexicon is out of date; run python3 tools/lexicon/build_lexicon.py:', ', '.join(stale))
            return 1
        return 0
    for k, v in files.items():
        (HERE / k).parent.mkdir(parents=True, exist_ok=True)
        (HERE / k).write_text(v, encoding='utf-8')
    print({k: json.loads(v)['count'] for k, v in files.items()})
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
