"""Example: OCR a PDF or page images with a running Unlimited-OCR-2 server, then write raw output, Markdown, and structure JSON.

    python3 tools/ocr/unlimited/example.py --endpoint http://127.0.0.1:10000 --out out/ book.pdf
    python3 tools/ocr/unlimited/example.py --endpoint http://127.0.0.1:10000 --out out/ page_0001.jpg page_0002.jpg

It needs a server someone has started (see tools/ocr/unlimited/README.md); without --endpoint it refuses to run.
PDF input needs PyMuPDF (optional). Nothing here touches data/ or any hosted text."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/
from ocr.unlimited.client import UnlimitedOCRClient, UnlimitedOCRConfig  # noqa: E402
from ocr.unlimited.postprocess import to_markdown  # noqa: E402
from ocr.unlimited.structure import structure  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('inputs', nargs='+', help='one PDF, or page images in page order')
    ap.add_argument('--endpoint', required=True, help='SGLang server, e.g. http://127.0.0.1:10000')
    ap.add_argument('--out', default='unlimited-ocr-out')
    ap.add_argument('--page-window', type=int, default=10)
    ap.add_argument('--tokens-per-page', type=int, default=8000)
    ap.add_argument('--ngram-size', type=int, default=35)
    a = ap.parse_args(argv)
    client = UnlimitedOCRClient(UnlimitedOCRConfig(endpoint=a.endpoint, page_window=a.page_window,
                                                   tokens_per_page=a.tokens_per_page, ngram_size=a.ngram_size))
    raw = client.raw_for_pdf(a.inputs[0]) if a.inputs[0].lower().endswith('.pdf') else client.raw_for_images(a.inputs)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'raw.txt').write_text(raw, encoding='utf-8')
    (out / 'document.md').write_text(to_markdown(raw), encoding='utf-8')
    (out / 'structure.json').write_text(json.dumps(structure(raw), ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'wrote {out}/raw.txt, document.md, structure.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
