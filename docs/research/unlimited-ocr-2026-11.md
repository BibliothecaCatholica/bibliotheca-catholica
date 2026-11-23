# Unlimited-OCR-2 as an optional OCR engine: design note, November 23, 2026

Owner's brief (round 4, Job 4): fit Baidu's Unlimited-OCR-2 into this repository as an optional engine, off by default, with no model running anywhere yet. The code is in `tools/ocr/unlimited/` and its README; tests are in `tests/test_unlimited_ocr.py`.

## Pipeline

1. **Input:** a PDF (rasterised at 300 DPI with PyMuPDF) or page images in page order. In `tools/transcribe_scan.py` the input is always the scan's own page images, the same JPEG 2000 files the archive.org OCR was made from (`page_image()`).
2. **OCR:** `client.py` sends windows of pages to an SGLang server's OpenAI-compatible `/v1/chat/completions`. The prompt is `"<PAGE><image>" * n + "Multi page parsing."`, with special tokens kept. It returns raw layout output, one `<PAGE>` per input page.
3. **Cleanup:** `postprocess.py` turns the layout blocks into page-bounded Markdown. Unlike the official converter, it never merges a block across a page break: a hosted text is checked page by page against its images, so each page's words stay on that page.
4. **Structure:** `structure.py` suggests title, author, imprint, copyright year, headings, and page ranges as JSON in the `data/sources/` style. A person confirms each value on the page images before it goes into a record.
5. **Storage:** nothing new. Raw output is cached beside the page images (`<cache>/uocr/<ia>/`). A transcription that passes the read gate is stored as every hosted text is: `data/texts/<edition>.txt` plus its provenance record in `data/sources/`, with the engine and per-line choices in `readGate`.

### Inside transcribe_scan.py
The model is a third engine in the existing per-line choice, behind the same interface as the Tesseract path from #143:
- archive.org's line stays the default;
- Tesseract's reading replaces it only with strictly fewer unread words and about the same word count;
- Unlimited-OCR-2 is then compared against the result, under the same rule.

It runs only when the command line gives both `--unlimited-ocr` and `--unlimited-endpoint URL`. Otherwise `build()` never calls it, and every text and score is unchanged; `TranscribeScanEngine.test_off_by_default_scores_and_text_unchanged` proves it. The read gate is unchanged: OCR from any engine, and any frontier-model metadata step, still needs page-image verification before hosting. Frontier models may suggest metadata, but they never supply transcription text.

### Once compute exists
The design doesn't change:
- Start SGLang on a GPU host and pass its URL. Step 2 is the only network call, and it is behind one configurable endpoint.
- The `transport` in `UnlimitedOCRClient` is injectable, so a queue, batch job, or hosted API can replace HTTP without touching post-processing or structuring.
- Page windows (`page_window`) let long books run in chunks within memory limits.
- Raw output is cached, so re-scoring after hand fixes doesn't re-run the model.

## Model facts, verified against the sources on November 23, 2026

Sources: github.com/baidu/Unlimited-OCR (README.md, utils/README.md, utils/process_unlimitedOCR2.py, LICENSE, fetched as raw files) and huggingface.co/baidu/Unlimited-OCR-2 (model card and model API).

| Fact in the brief | Status | What the sources say |
|---|---|---|
| Multi-page prompt `"<PAGE><image>" * n + "Multi page parsing."` | **verified** | Both READMEs give this format for `infer_multi` and for the SGLang example. |
| Special tokens | **verified** | Output keeps `<PAGE>`, `<BLOCK>`, `<LEVELn>`, `<FORK>`, and `<MERGE>`. The SGLang example sets `skip_special_tokens: false`, `page_token_id: 128827`, and `eos_token_id: 1`. |
| `utils/process_unlimitedOCR2.py` | **verified** | Exists. Standard library only. Converts raw output to Markdown: splits on `<PAGE>` (keeping blank pages), turns `title<LEVELn>` into headings, writes figures as `![](page<N>_x1_y1_x2_y2.jpg)` with coordinates clamped to 0–1000, keeps tables as HTML, and merges cross- and append-chains across pages. |
| License | **verified** | MIT (LICENSE file, "Copyright (c) 2026 Baidu"; model card `license: mit`). |
| Hardware | **verified (partly)** | Transformers path tested on an NVIDIA A800-80GB (torch 2.13.0, transformers 4.52.1). SGLang recommended for serving, with memory notes. About 3.34 billion parameters per the model API. No minimum GPU is stated. |
| PyMuPDF at 300 DPI | **verified** | The SGLang example's `pdf_to_images(pdf_path, dpi=300)` uses `fitz`; the README installs `pymupdf==1.27.2.2`. |
| Page windowing, max tokens per page, no-repeat n-gram size | **verified** | Server environment variables `SGLANG_UOCR_DOC_*_PAGE_WINDOW=10` and `SGLANG_UOCR_MAX_PAGE_TOKENS=20000`. Request `max_tokens = tokens_per_page × pages` (8000 per page in the example). `custom_params.ngram_size: 35` with `window_size` 1024 for several pages or 128 for one. |
| "100 pages in one shot" (v1) was overstated | **unverified** | Not found in the v1 README fetched from the `UnlimitedOCR1.0` branch. The v2 docs describe page-window scheduling instead. |

## Not done here (needs a server)
- A real run on a library scan, and a comparison of its per-line choices with Tesseract's on Grant, Furfey, or Cassidy.
- The serialized n-gram processor string, which comes from the server's SGLang install. Until then the client sends the processor's parameters and omits the processor reference.
