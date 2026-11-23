"""Turn Unlimited-OCR-2's raw layout output into page-bounded Markdown, and into lines for per-line engine choice.

Raw format (documented in github.com/baidu/Unlimited-OCR utils/README.md, checked November 23, 2026). The model emits no
Markdown. Each document is one string of layout blocks, one <PAGE> per input page, in order:

    <PAGE><BLOCK>title<LEVEL1>[x1,y1,x2,y2]<FORK>Chapter One
    <BLOCK>text[x1,y1,x2,y2]<FORK>body text ...
    <BLOCK>cross_table[x1,y1,x2,y2]<FORK><table>...</table><PAGE><BLOCK>append_table[...]<FORK>...

* labels: title (with <LEVELn>), text, image/figure/chart/seal, table, and cross_<t>/append_<t> for blocks continued across
  pages; <MERGE> joins same-page columns
* bounding boxes are on a 0-1000 grid of the page, (x1, y1) top left
* blank pages still carry their <PAGE> marker

This module keeps page boundaries (unlike the official converter, utils/process_unlimitedOCR2.py, which merges continued blocks
across pages for benchmark scoring): Bibliotheca Catholica checks every page against its own image, so a page's words must
stay on that page. Continued blocks are marked, not merged.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass

PAGE_RE = re.compile(r'<\s*/?\s*PAGE\s*\d*\s*>', re.I)
BLOCK_RE = re.compile(
    r'<\s*BLOCK\s*>\s*(?P<label>[A-Za-z_]+)\s*'
    r'(?:<\s*/?\s*LEVEL\s*(?P<lv1>\d*)\s*[>}]?)?\s*'
    r'(?:\[\s*(?P<x1>-?\d+)\s*[,，]\s*(?P<y1>-?\d+)\s*[,，]\s*(?P<x2>-?\d+)\s*[,，]\s*(?P<y2>-?\d+)\s*\])?\s*'
    r'(?:<\s*/?\s*LEVEL\s*(?P<lv2>\d*)\s*[>}]?)?\s*'
    r'(?:<\s*FORK\s*>)?', re.I)
STRAY_RE = re.compile(r'<[|｜]/?[a-zA-Z_]+[|｜]>|<image>|<\s*/?\s*(?:BLOCK|FORK|MERGE)\s*>|<\s*/?\s*LEVEL\s*\d*\s*[>}]?', re.I)
FIGURES = {'image', 'figure', 'chart', 'seal'}


@dataclass
class Block:
    page: int                 # 1-based page number in the request order
    label: str                # base label, e.g. "text", "title", "table"
    continued: str            # "", "cross" (continues on the next page), or "append" (continues the previous page)
    level: int | None         # heading level for titles
    bbox: tuple[int, int, int, int] | None  # 0-1000 grid
    content: str


def _clamp(v: int) -> int:
    return max(0, min(1000, v))


def parse(raw: str) -> list[list[Block]]:
    """Split raw output into pages of blocks. The text before the first <PAGE> is ignored (it is empty in the model's output)."""
    pages = PAGE_RE.split(raw)[1:] if PAGE_RE.search(raw) else [raw]
    out = []
    for n, seg in enumerate(pages, 1):
        blocks = []
        ms = list(BLOCK_RE.finditer(seg))
        for i, m in enumerate(ms):
            end = ms[i + 1].start() if i + 1 < len(ms) else len(seg)
            label = m.group('label').lower()
            cont = ''
            for pre in ('cross_', 'append_'):
                if label.startswith(pre):
                    cont, label = pre[:-1], label[len(pre):]
            lv = m.group('lv1') or m.group('lv2')
            box = None
            if m.group('x1') is not None:
                box = tuple(_clamp(int(m.group(k))) for k in ('x1', 'y1', 'x2', 'y2'))
            content = STRAY_RE.sub('', seg[m.end():end]).strip()
            blocks.append(Block(n, label, cont, int(lv) if lv else (1 if label == 'title' else None), box, content))
        out.append(blocks)
    return out


def to_markdown(raw: str) -> str:
    """Page-bounded Markdown: a "<!-- page N -->" comment opens each page; titles become headings; figures become image
    references named by page and box; tables stay HTML; a block continued across a page break is marked, never merged."""
    lines = []
    for n, blocks in enumerate(parse(raw), 1):
        lines.append(f'<!-- page {n} -->')
        for b in blocks:
            mark = ' <!-- continued on next page -->' if b.continued == 'cross' else ''
            if b.continued == 'append':
                lines.append('<!-- continued from previous page -->')
            if b.label == 'title':
                lines.append('#' * min(6, b.level or 1) + ' ' + ' '.join(b.content.split()) + mark)
            elif b.label in FIGURES:
                box = '_'.join(map(str, b.bbox)) if b.bbox else 'nobox'
                lines.append(f'![](page{n}_{box}.jpg){mark}')
            else:
                lines.append(b.content + mark)
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def page_lines(blocks: list[Block], obj_width: int, obj_height: int) -> list[dict]:
    """Lines for tools/transcribe_scan.py's per-line engine choice, in djvu coordinates (the same keys Tesseract lines carry:
    x, x2, top, y, h, text). The model gives boxes per block, not per line, so a block's text lines (split on newlines) are
    spread evenly down its box. Tables and figures are left out: per-line choice compares running text."""
    out = []
    for b in blocks:
        if b.bbox is None or b.label in FIGURES or b.label == 'table':
            continue
        texts = [t for t in (html.unescape(re.sub(r'<[^>]+>', ' ', l)).strip() for l in b.content.split('\n')) if t]
        if not texts:
            continue
        x1, y1, x2, y2 = b.bbox
        top, bot = y1 * obj_height / 1000, y2 * obj_height / 1000
        h = (bot - top) / len(texts)
        for i, t in enumerate(texts):
            t0 = top + i * h
            out.append({'x': int(x1 * obj_width / 1000), 'x2': int(x2 * obj_width / 1000), 'top': int(t0), 'y': int(t0 + h),
                        'h': max(1, int(h)), 'text': ' '.join(t.split())})
    return out
