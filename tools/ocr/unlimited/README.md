# Unlimited-OCR-2 (optional engine)

A client, post-processor, and structurer for Baidu's [Unlimited-OCR-2](https://huggingface.co/baidu/Unlimited-OCR-2), plus a third per-line engine in `tools/transcribe_scan.py`. **It is off by default and runs nowhere yet.** Nothing in `npm run validate`, the build, or CI calls it, and no model is served for this project. The design note is [docs/research/unlimited-ocr-2026-11.md](../../../docs/research/unlimited-ocr-2026-11.md).

## What works today
- `client.py` builds the official request: page images as data URLs, then `"<PAGE><image>" * n + "Multi page parsing."`, with `skip_special_tokens: false` and the n-gram logit processor's parameters. It reads streaming (server-sent events) and plain JSON responses and sends long documents in page windows. A PDF is rasterised at 300 DPI with PyMuPDF, which is imported only when needed and is not in the required setup.
- `postprocess.py` parses the raw layout blocks (`<PAGE>`, `<BLOCK>label<LEVELn>[x1,y1,x2,y2]<FORK>…`, boxes on a 0–1000 grid) into page-bounded Markdown. It also gives lines in djvu coordinates for per-line engine choice.
- `structure.py` suggests title, author, imprint, and copyright-year candidates, headings, and page ranges as JSON in the `data/sources/` style. These are suggestions to confirm on the images, never values to copy blindly.
- `tools/transcribe_scan.py --unlimited-ocr --unlimited-endpoint URL` adds the model as a third engine. It is chosen line by line with the same rule as Tesseract: strictly fewer unread words and about the same number of words. Without both options, behavior and every score are unchanged; `tests/test_unlimited_ocr.py` proves it.
- Tests use a stub server and stored sample output (`tests/fixtures/unlimited_ocr/`).

## Using it once a server exists
1. Start SGLang on a GPU machine as the official README shows: the customized SGLang wheel from the model repository, `--chat-template unlimited-ocr`, `--enable-custom-logit-processor`, and the page-window environment variables.
2. Optional: export `UNLIMITED_OCR_NGRAM_PROCESSOR` with the string from `DeepseekOCRNoRepeatNGramLogitProcessor.to_str()` in that SGLang install, so requests carry the no-repeat n-gram processor (TODO in `client.py`).
3. Try a document:
   ```
   python3 tools/ocr/unlimited/example.py --endpoint http://GPU-HOST:10000 --out /tmp/uocr book.pdf
   ```
4. Score a scan with the third engine (writes only the measurement):
   ```
   python3 tools/transcribe_scan.py SPEC.json --measure /tmp/m --unlimited-ocr --unlimited-endpoint http://GPU-HOST:10000
   ```
   Raw output is cached per page under `<cache>/uocr/<ia>/`.

## Hardware notes (from the official docs, November 23, 2026)
- **Transformers** (native, for quick tests): tested with Python 3.10, torch 2.13.0, and transformers 4.52.1 on an NVIDIA A800-80GB, in bfloat16.
- **SGLang** (recommended for serving) needs Baidu's customized wheel. The memory settings that matter: `--mem-fraction-static 0.7` (0.75 is unstable at 32 or more concurrent requests), `--max-prefill-tokens 2048` (memory grows linearly with it), and a smaller page window, which lowers peak memory but loses cross-page merging at the window edge.
- About 3.34 billion parameters (safetensors total from the model API). No figure for the smallest workable GPU is published; plan on a data-center GPU until one is tested.

## Limitations
- **The read gate is unchanged.** Output from this engine, like Tesseract's or archive.org's, is OCR: every hosted text is still verified against the same scan's page images and must reach 99.5%. A frontier model may suggest metadata (title, author, imprint), but it never supplies transcription text.
- **Line placement is approximate.** The model gives boxes per block, not per line, so `page_lines()` spreads a block's lines evenly down its box. Per-line matching against archive.org lines can miss when a block's lines are unevenly spaced.
- **One page per request in `transcribe_scan.py`.** That keeps each page's words on its own page image. It also gives up the model's cross-page context, which is the point of the "unlimited-horizon" design.
- **Long documents.** The claim that v1 parsed "100 pages in one shot" was overstated (per the owner's brief; I couldn't find it in the v1 README to quote). The v2 docs describe page-window scheduling with 10 pages per window by default.
