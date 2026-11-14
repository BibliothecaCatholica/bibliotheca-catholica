# Hosted editions: how we prepare and present the books

Read this before any task that touches a hosted book: its text, reader, chapter pages, EPUB, cover, or work page. It describes the process proved on Orthodoxy (PR #24, November 2026) and the presentation the owner wants for every hosted edition. The editorial assessment of the 64 hosted editions, and the procedure for substantive corrections, are in [HOSTED-TEXT-QUALITY.md](HOSTED-TEXT-QUALITY.md). Visual rules are in [DESIGN.md](DESIGN.md). Hosting and rights rules are in [PROJECT-RULES.md](PROJECT-RULES.md). Status and approvals are in [CENTRAL.md](../CENTRAL.md).

## The goal

Each hosted book should read as a designed edition, not a text file in a web page: a calm title page, real chapters, a comfortable measure, verse and emphasis where the source marks them, and an EPUB of the same quality. Presentation improves; **the words never change**. Orthodoxy is the reference: compare any new work with it.

## Non-negotiables

1. **The TXT is the text.** Every character a reader sees, prints, or downloads comes from `data/texts/<file>.txt`, whose SHA-256 is pinned in `data/library.json`. Never edit those files. Do not change their wording, spelling, punctuation, or block order.
2. **Structure, not text, is added.** Structure lives in separate files keyed to the TXT's block numbers (blank-line blocks, the same as `splitText()` in `scripts/library.js`). Those files hold no body text.
3. **Never infer.** Verse, emphasis, notes, and headings come only from what a source marks: the edition's own HTML, or a page of a named printing that was checked visually. Do not guess them from capitals, indentation, line length, or importance. If the source does not mark something, leave it plain. On Orthodoxy's title page, "by" stays an ordinary paragraph because the HTML marks it as one.
4. **Anchors and reader data survive.** Every block keeps its `<p id="reading-p-N">` element and its exact text, so saved notes, highlights, reading positions, and links keep working. Add classes; do not re-split, merge, or re-wrap blocks.
5. **Notices stay.** The Project Gutenberg (or other source) notice, rights line, and source credit stay reachable from every edition, and EPUBs carry the full original license verbatim.
6. **Every claim is checked.** A gate compares the structure with the TXT word for word, and tests compare the Python (static) and browser renderers character for character. "Builds" does not mean "proofread."
7. **Owner decisions are recorded.** The choice of markup source, any typographic equivalence the gate accepts, and every new hosted work need Micah's own words, quoted in CENTRAL.md.

## The pipeline (as run for Orthodoxy)

| Step | What happens | Where |
|---|---|---|
| 1. Survey | Fetch the source's own HTML, pin the original bytes (gzip, deterministic) with a record: URL, retrieval time, SHA-256, and counts of headings, italics, verse, notes, and line breaks. Compare its words with the TXT. Note any other edition's file only as reference evidence. **Stop and report**; the owner chooses the markup source. | `data/sources/gutenberg-html/*.html.gz` and `*.json` |
| 2. Convert | Parse the chosen HTML's book body into roles (title, byline, heading, contents, chapter, paragraph), aligned to TXT block numbers. Write the intermediate file with structure only. | `tools/structure_text.py` → `data/structured/<work>-<edition>.json` |
| 3. Gate | Check that both checksums match. Check that every TXT body block is matched, in order, with the same words. Check that the chapter map equals the existing chapter pages, and that any scan-verified formatting is carried over unchanged. List each accepted typographic difference by name and count it. Orthodoxy has one: the HTML's em dash for the TXT's "--", 103 times. The gate runs at the start of `npm run build`. | `tools/structure_text.py --check`, `tests/test_structured_text.py` |
| 4. Render | Roles travel in `data/text-pages.js` (`s.r`) and are applied only when the structure was built from this exact TXT. The reader and static pages add a `reading-<role>` class; the text is unchanged. `data/library.json` and `data/library.js` stay identical (an existing test requires this). | `tools/build_text_pages.py`, `renderReadingBlock()` in `scripts/library.js`, `tools/reader_formatting.py`, `styles/library.css` |
| 5. EPUB | Build an EPUB 3 from the TXT and the structure with the same block renderer: front matter, chapters, the full source notice and license, and a colophon. It re-checks its own text against the TXT and is deterministic (same inputs, same SHA-256). CI attaches it to the PR as a review artifact; it is **not published or linked** until the owner says so. | `tools/build_epub.py`, `.github/workflows/epub-pilot.yml` |
| 6. Review | Screenshots (reader title page, a chapter, phone and desktop), gate and test counts, drift check, and CENTRAL.md entry. Stop for the owner's review; do not merge a book's PR without it. | the PR |

Scan-verified features (verse lines and exact emphasis spans checked on a named printing's page) are a separate layer: `readerFormatting` in `data/library.json`, bound to the TXT checksum and validated by `tools/reader_formatting.py`. Orthodoxy Chapter IV is the only one so far (page 99 of the 1909 John Lane printing). The structure pipeline carries this layer over unchanged and never invents more.

## How the books should look

These follow [DESIGN.md](DESIGN.md). The first group is built for Orthodoxy. The second is the owner's approved direction for the "Beautiful editions" brief (Part D), which starts only when Micah says so.

**Now (Orthodoxy):**
- Reading measure of 60 to 70 characters (the reader's text column is `26em`), serif text, and generous leading.
- Title centred; byline and section headings in small caps; each chapter heading set apart with a hairline above.
- Chapter IV's two italic words and two-line Yeats quotation, from the scan-verified layer.
- One quiet toolbar (Contents, Aa, Notes, Find, Print, Listen); the source and licence notices at the end of each section.
- Chapter pages (`/work/<id>/ch/<slug>/`) and a work page with one filled "Read here".

**Next (Part D, pilot on Orthodoxy, then all 64 editions where noted):**
- **Covers:** a typographic cover for every hosted edition (title, author, the site's cross mark, in burgundy, cream, and gold), one series design with a small variation by category. It is used on the work page, the shelves, author pages, the EPUB, and as a PNG social image. No photographs or third-party art.
- **Work page as a title page:** cover beside the title; a facts line computed from the TXT (year, word count, reading time); three choices: Read, Listen, Download; and a short "About this edition" block. Full source and rights details stay behind the existing toggle.
- **Chapter openers and endings** for editions with chapter structure: a large numeral, a small-caps "Chapter" label, the title, a drop cap, one ornament or rule, then a centred ornament, "End of Chapter N", and a link to the next chapter. Reading position is still saved.
- **Text:** one paragraph style (first-line indents or spaced paragraphs, recorded in DESIGN.md), with verse, block quotations, and notes styled distinctly **only where the structure marks them**.
- **Print and save-as-PDF** with the same design, the cover as the first page.

## Status of the hosted editions

| Edition | Structure | Notes |
|---|---|---|
| Orthodoxy (pg-130) | **Full pipeline**: structure from #130 HTML, gate, rendering, review EPUB | Chapter IV scan-verified verse and emphasis. #16769 (1934 reprint) is reference evidence only. |
| Father Brown: Innocence (pg-204), Wisdom (pg-223), Secret (pg-70175), Incredulity (se-incredulity-father-brown) | Story maps in `tools/text_pages.py` | Would need steps 1 to 5 for roles and EPUBs. Incredulity comes from Standard Ebooks (CC0), not Gutenberg HTML. |
| Summa Theologiae (four parts and the Supplement) | Question and article map (`tools/build_summa.py`) | Its own renderer, `summa_para()`; the Supplement has OCR flags to adjudicate first. |
| Story of a Soul (pg-16772) | **Surveyed, not built** (HTML pinned November 14) | 145 italic spans; verse only as line breaks; notes as plain bracketed text (611); inconsistent heading levels; the HTML drops accents the TXT keeps. Building it needs owner decisions: an accent-folding rule for the gate, and whether to use the HTML's italics. |
| The other 56 hosted editions | None | Survey first (step 1); do not build without a decision. |

## When you are tasked with a hosted book

1. Read this file, then the edition's rows in [HOSTED-TEXT-INVENTORY.md](HOSTED-TEXT-INVENTORY.md) and [HOSTED-TEXT-QUALITY.md](HOSTED-TEXT-QUALITY.md), and its provenance record in `data/sources/`.
2. Check CENTRAL.md and the open PRs for decisions already made about that book.
3. Start at the earliest step not yet done, and stop where the table says to stop.
4. Prove fidelity: run `python3 tools/structure_text.py --check`, confirm `sha256sum data/texts/<file>.txt` against `data/library.json`, and run the full validation in [OPERATIONS.md](OPERATIONS.md#validation).
5. Compare the result with Orthodoxy on desktop and phone, in both themes. Include screenshots in the PR.
6. Never publish an EPUB or new presentation layer, and never mark a text "proofread", without the owner's approval.
