"""Find structure in parsed Unlimited-OCR-2 output: title candidates, headings, author and imprint signals, page ranges.

The result is a JSON-ready dict in the style of data/sources/ records (keys a person then confirms and copies). These are
suggestions only: a metadata guess, from this module or from any frontier model, never supplies transcription text, and every
value is checked against the page images before it goes into a record (PROJECT-RULES rule 1, "Read gate")."""
from __future__ import annotations

import re
from typing import Any

from .postprocess import Block, parse

IMPRINT_RE = re.compile(r'\b(?:PUBLISHING|PRESS|COMPANY|CO\.|BOOK CO|SONS|LTD|& CO|VERLAG|LIBRAIRIE)\b', re.I)
PLACE_RE = re.compile(r'\b(?:LONDON|NEW YORK|MILWAUKEE|ST\. LOUIS|DUBLIN|EDINBURGH|BOSTON|BALTIMORE|PHILADELPHIA|OXFORD|PARIS)\b', re.I)
YEAR_RE = re.compile(r'\b(1[5-9]\d\d|20[0-2]\d)\b|\bM{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})\b')
BY_RE = re.compile(r'^\s*(?:by|BY)\s+(.+)$')
COPYRIGHT_RE = re.compile(r'copyright[,\s]+(?:©\s*)?(\d{4})', re.I)


def _roman(s: str) -> int | None:
    vals = {'M': 1000, 'D': 500, 'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1}
    if not s or any(c not in vals for c in s):
        return None
    n = 0
    for a, b in zip(s, s[1:] + ' '):
        n += -vals[a] if b != ' ' and vals[a] < vals[b] else vals[a]
    return n if 1500 <= n <= 2029 else None


def structure(raw: str, front_pages: int = 8) -> dict[str, Any]:
    """Signals from the first `front_pages` pages (title, author, imprint, years) and headings from every page."""
    pages = parse(raw)
    titles, authors, imprints, years, copyright_years = [], [], [], [], []
    for blocks in pages[:front_pages]:
        lines = [(b, l.strip()) for b in blocks for l in b.content.split('\n') if l.strip()]
        for i, (b, l) in enumerate(lines):
            if b.label == 'title' and (b.level or 1) == 1 and len(l) < 120:
                titles.append({'text': l, 'page': b.page})
            m = BY_RE.match(l)
            if m:
                authors.append({'text': m.group(1).strip(), 'page': b.page})
            elif l.upper() in ('BY', 'BY:') and i + 1 < len(lines):
                authors.append({'text': lines[i + 1][1], 'page': b.page})
            if IMPRINT_RE.search(l) or PLACE_RE.search(l):
                imprints.append({'text': l, 'page': b.page})
            m = COPYRIGHT_RE.search(l)
            if m:
                copyright_years.append({'year': int(m.group(1)), 'page': b.page})
            for y in YEAR_RE.finditer(l):
                v = int(y.group(1)) if y.group(1) else _roman(y.group(0))
                if v:
                    years.append({'year': v, 'page': b.page})
    headings = [{'text': ' '.join(b.content.split()), 'level': b.level or 1, 'page': b.page}
                for blocks in pages for b in blocks if b.label == 'title' and b.content.strip()]
    # page ranges: each heading opens a range that runs to the page before the next heading
    ranges = []
    for i, h in enumerate(headings):
        end = (headings[i + 1]['page'] - 1) if i + 1 < len(headings) else len(pages)
        ranges.append({'heading': h['text'], 'pages': [h['page'], max(h['page'], end)]})
    return {
        'kind': 'ocr-structure-suggestion',
        'engine': 'unlimited-ocr-2',
        'pages': len(pages),
        'titleCandidates': titles,
        'authorCandidates': authors,
        'imprintLines': imprints,
        'copyrightYears': copyright_years,
        'yearsSeen': years,
        'headings': headings,
        'pageRanges': ranges,
        'note': 'Suggestions from layout output only; confirm every value against the page images before use.',
    }


__all__ = ['structure', 'Block']
