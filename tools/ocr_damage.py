"""OCR damage the read gate misses (Round 8, Job C3 proposal, November 23, 2026). Analysis only: changes no score.

    python3 tools/ocr_damage.py [EDITION ...]     # default: the five hosted transcriptions measured below

`transcribe_scan.repair()` reads a token as prefix + word + suffix with ASCII letters only, so four kinds of damage pass the
gate unflagged: (1) a token with a non-ASCII letter inside it fails that pattern and counts as read ("Cloriviére",
"rémischen", "Schóningh", a Greek word read as Latin letters with accents); (2) a backslash or other symbol inside a token does
the same ("IIX\\ovcuos"); (3) a note digit fused to a word is read as the word ("1bid" as "bid", "1Shahan"); (4) note marks read
as symbols (°, ®, ©, ¢, |) stand alone or cling to a word. This tool counts each kind in a hosted text, leaving out words the
edition's record already verified and accented forms the proofread texts use, and prints the read-gate score each book would
have if they counted as unread. The proposal (docs/research/gate-damage-2026-11/README.md) is to make `unread()` count them.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import transcribe_scan as T  # noqa: E402

BOOKS = ['ia-johnenglandameri00gran', 'ia-mysteryofiniquit00furf', 'ia-moldersofmedieva00cass', 'ia-highpointsofmedi00wals',
         'ia-rightswrongsinin00haas']
NOTE_MARKS = '°®©¢|¦§'
ORDINAL = re.compile(r'^\d+(st|nd|rd|th|d|s|mo|vo|to|o)$', re.I)


def accented_vocabulary():
    """Accented word forms used in the proofread texts (data/texts, ia-* left out), lowercased."""
    out = set()
    for f in (ROOT / 'data/texts').glob('*.txt'):
        if not f.name.startswith('ia-'):
            out.update(w.lower() for w in re.findall(r"[^\W\d_]+", f.read_text(errors='replace')) if any(ord(c) > 127 for c in w))
    return out


def kind(tok, accented, verified):
    """The damage kind of one whitespace token, or None."""
    core = tok.strip('.,;:!?()[]"“”‘’\'*')
    if not core or core in verified:
        return None
    if '\\' in core:
        return 'symbol-in-word'
    letters = [c for c in core if c.isalpha()]
    if any(c in NOTE_MARKS for c in core):
        return 'note-mark'
    if letters and any(ord(c) > 127 and c not in 'æœÆŒ' for c in letters):
        word = re.sub(r'[^\w]', '', core).lower()
        if word not in accented and unicodedata.normalize('NFC', word) not in accented:
            return 'accent-in-word'
    m = re.match(r'^(\d+)([A-Za-z]{2,})$', core)
    if m and not ORDINAL.match(core):
        return 'digit-glued'
    return None


def scan(edition, accented):
    rec = json.loads((ROOT / 'data/sources' / (edition + '.json')).read_text())
    rg = rec.get('readGate') or {'words': rec.get('words', 0), 'unknown': rec.get('unknownWords', 0)}  # older records keep the counts at the top
    verified = set(rec.get('verifiedWords', []))
    text = (ROOT / 'data/texts' / (edition + '.txt')).read_text()
    found = {}
    for tok in text.split():
        k = kind(tok, accented, verified)
        if k:
            found.setdefault(k, []).append(tok)
    return rg, found


def main(argv=None):
    eds = (argv if argv is not None else sys.argv[1:]) or BOOKS
    accented = accented_vocabulary()
    rows = []
    for ed in eds:
        rg, found = scan(ed, accented)
        words, unknown = rg.get('words', 0), rg.get('unknown', 0)
        extra = sum(len(v) for v in found.values())
        before = 1 - unknown / max(1, words)
        after = 1 - (unknown + extra) / max(1, words)
        rows.append({'edition': ed, 'words': words, 'unknown': unknown, 'before': round(before * 100, 2), 'damage': {k: len(v) for k, v in found.items()},
                     'after': round(after * 100, 2), 'passesAfter': after >= 0.995,
                     'examples': {k: sorted(set(v))[:12] for k, v in found.items()}})
    print(json.dumps(rows, indent=1, ensure_ascii=False))
    return rows


if __name__ == '__main__':
    main()
