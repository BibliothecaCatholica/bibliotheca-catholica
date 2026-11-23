"""Client for Baidu's Unlimited-OCR-2 served by SGLang's OpenAI-compatible API (optional engine, off by default).

Nothing in validate, build, or CI calls this module. No model runs anywhere for this project yet. The client only talks to an
endpoint that someone has started and passed in explicitly (see tools/ocr/unlimited/README.md). Tests use a stub server.

Model facts this code follows were checked on November 23, 2026 against github.com/baidu/Unlimited-OCR (README, utils/) and
huggingface.co/baidu/Unlimited-OCR-2 (model card); see docs/research/unlimited-ocr-2026-11.md:
  * multi-page prompt: "<PAGE><image>" * n + "Multi page parsing.", images first, then the text part
  * output keeps special tokens (skip_special_tokens False): one <PAGE> per input page, in order
  * <PAGE> token id 128827, eos id 1; the server's DeepseekOCRNoRepeatNGramLogitProcessor takes ngram_size, window_size,
    page_token_id, eos_token_id, and max_page_tokens through custom_params
  * PDFs are rasterised at 300 DPI with PyMuPDF before sending
"""
from __future__ import annotations

import base64
import json
import os
import tempfile
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence

PAGE_TOKEN_ID = 128827  # <PAGE> marker id (sparse_attention_config.page_token_id in the model's config.json)
EOS_TOKEN_ID = 1
PROMPT_SUFFIX = 'Multi page parsing.'
# The no-repeat n-gram processor the official example sends; its serialized form comes from SGLang
# (DeepseekOCRNoRepeatNGramLogitProcessor.to_str()). TODO(server): fill from the running server's sglang install.
NGRAM_PROCESSOR_ENV = 'UNLIMITED_OCR_NGRAM_PROCESSOR'


@dataclass
class UnlimitedOCRConfig:
    """Request settings. Defaults follow the official SGLang example."""
    endpoint: str                      # e.g. "http://127.0.0.1:10000" (no trailing /v1)
    model: str = 'Unlimited-OCR-2'     # --served-model-name on the server
    page_window: int = 10              # pages per request; mirrors SGLANG_UOCR_DOC_*_PAGE_WINDOW (10 by default)
    tokens_per_page: int = 8000        # max_tokens = tokens_per_page * pages in the request
    max_page_tokens: int = 20000       # per-page output cap passed to the logit processor (<= 0 disables the guard)
    ngram_size: int = 35               # no-repeat n-gram size
    window_size: int | None = None     # n-gram window; None = 1024 for several pages, 128 for one (the official setup)
    crop_mode: bool = True             # True = "gundam" tiles, False = "base" one global view per page
    stream: bool = True
    timeout: float = 6000.0
    ngram_processor: str | None = field(default_factory=lambda: os.environ.get(NGRAM_PROCESSOR_ENV))


def build_prompt(n_pages: int) -> str:
    """The multi-page prompt: one "<PAGE><image>" per page, then the instruction."""
    if n_pages < 1:
        raise ValueError('at least one page')
    return '<PAGE><image>' * n_pages + PROMPT_SUFFIX


def pdf_to_images(pdf_path: str | os.PathLike, dpi: int = 300, out_dir: str | None = None) -> list[Path]:
    """Rasterise a PDF at `dpi` with PyMuPDF (imported lazily: an optional dependency, not in the required setup)."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover - depends on the optional package
        raise RuntimeError('PDF input needs PyMuPDF: pip install pymupdf') from exc
    out = Path(out_dir or tempfile.mkdtemp(prefix='uocr_pdf_'))
    doc = fitz.open(str(pdf_path))
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    paths = []
    for i, page in enumerate(doc):
        p = out / f'page_{i + 1:04d}.png'
        page.get_pixmap(matrix=mat).save(str(p))
        paths.append(p)
    doc.close()
    return paths


def _image_part(path: Path) -> dict:
    ext = path.suffix.lower()
    mime = 'image/jpeg' if ext in ('.jpg', '.jpeg') else f'image/{ext.lstrip(".")}'
    data = base64.b64encode(path.read_bytes()).decode('ascii')
    return {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{data}'}}


def build_payload(images: Sequence[Path], cfg: UnlimitedOCRConfig) -> dict:
    """The chat-completions request for one page window."""
    n = len(images)
    payload = {
        'model': cfg.model,
        'messages': [{'role': 'user', 'content': [_image_part(p) for p in images] + [{'type': 'text', 'text': build_prompt(n)}]}],
        'max_tokens': cfg.tokens_per_page * n,  # must be positive: the output budget for the whole request
        'temperature': 0,
        'skip_special_tokens': False,            # the post-processor needs <PAGE>, <BLOCK>, <LEVELn>, <FORK>
        'images_config': {'crop_mode': cfg.crop_mode},
        'custom_params': {
            'ngram_size': cfg.ngram_size,
            'window_size': cfg.window_size if cfg.window_size is not None else (1024 if n > 1 else 128),
            'page_token_id': PAGE_TOKEN_ID,
            'eos_token_id': EOS_TOKEN_ID,
            'max_page_tokens': cfg.max_page_tokens,
        },
        'stream': cfg.stream,
    }
    if cfg.ngram_processor:
        payload['custom_logit_processor'] = cfg.ngram_processor
    return payload


Transport = Callable[[str, bytes, float], Iterable[bytes]]


def _urllib_transport(url: str, body: bytes, timeout: float) -> Iterator[bytes]:
    """POST and yield the response line by line (works for streaming and plain JSON bodies)."""
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - endpoint is configured by the operator
        for line in resp:
            yield line


def parse_response(lines: Iterable[bytes]) -> str:
    """Join a response into raw text: server-sent events ("data: {...}" chunks with choices[0].delta.content, ending in
    "[DONE]") or one non-streaming JSON body (choices[0].message.content)."""
    raw = [l.decode('utf-8') if isinstance(l, bytes) else l for l in lines]
    if not any(l.lstrip().startswith('data:') for l in raw):
        body = json.loads(''.join(raw))
        return body['choices'][0]['message']['content']
    out = []
    for line in raw:
        line = line.strip()
        if not line.startswith('data:'):
            continue
        data = line[len('data:'):].strip()
        if data == '[DONE]':
            break
        choices = json.loads(data).get('choices') or []  # the final chunk may carry usage only
        if choices:
            out.append((choices[0].get('delta') or {}).get('content') or '')
    return ''.join(out)


class UnlimitedOCRClient:
    """Sends page images to the server in page windows and returns the raw layout output, one string per document.

    Windows are sent as separate requests and their raw outputs concatenated, so every input page still yields exactly one
    <PAGE>. (The server can also window internally with SGLANG_UOCR_EANABLE_DOC_LIMIT; a smaller window lowers memory but
    loses cross-page merging at the window edge.)"""

    def __init__(self, cfg: UnlimitedOCRConfig, transport: Transport | None = None):
        self.cfg = cfg
        self.transport = transport or _urllib_transport

    def raw_for_images(self, images: Sequence[str | os.PathLike]) -> str:
        paths = [Path(p) for p in images]
        if not paths:
            raise ValueError('no pages')
        w = max(1, self.cfg.page_window)
        parts = []
        for i in range(0, len(paths), w):
            body = json.dumps(build_payload(paths[i:i + w], self.cfg)).encode('utf-8')
            parts.append(parse_response(self.transport(self.cfg.endpoint.rstrip('/') + '/v1/chat/completions', body, self.cfg.timeout)))
        return ''.join(parts)

    def raw_for_pdf(self, pdf: str | os.PathLike, dpi: int = 300) -> str:
        return self.raw_for_images(pdf_to_images(pdf, dpi=dpi))
