# Hosted-text quality

This is the living editorial assessment and work procedure, not a claim that the collection has been proofread. The [generated inventory](HOSTED-TEXT-INVENTORY.md) enumerates every hosted edition, its file, source record, checksum, existing bibliographic note, and mechanical review indicators. Rebuild it with `python3 tools/audit_hosted_texts.py`. Snapshot inspected: main `25e6276`, November 12, 2026. The separate illuminated Orthodoxy Site is outside this project and was not modified.

## Actual scope

The selected catalogue has 104 works and 131 edition records. Only 64 editions, belonging to 59 works, have a `text` field. All 64 local files match their catalogue SHA-256 values; there are no extra files in `data/texts/`. There are 61 Gutenberg files, two public-domain extractions (CCEL and Standard Ebooks), and one OCR transcription. The other 45 selected works have no hosted reading edition. The 6,633-record imported Isidore index, source libraries, external edition links, and sample links are not hosted books.

“Complete” must name its unit. We hold the entire current source file for each of the 64 editions, including its notices. That does not establish completeness against a printed book. Important explicit limits:

| Hosted unit | Scope and limits |
|---|---|
| Summa Theologiae | Four Gutenberg Parts plus the Supplement; Part III ends at Q90. The Supplement has 99 questions and 446 articles; its two printed appendices are omitted. |
| The City of God | Two files: Books I–XIII and XIV–XXII. |
| Catherine's letters | Scudder's selection, not the complete correspondence. |
| Spiritual Exercises | Coppens's adapted retreat edition, not an unabridged Ignatian critical text. |
| On Prayer and the Contemplative Life | Selected Summa questions, not a separate Aquinas treatise. |
| Lives of the Saints | Butler: January–March and July; Baring-Gould: January, February, and March. No complete annual series. |
| Sacred and Legendary Art | Volume I of II only. |
| Hopkins | Early collected edition, not all poems in a modern scholarly edition. |
| Father Brown | Four separately hosted pre-1931 collections. Each is its named collection, not the complete Father Brown corpus. |
| On Christian Doctrine | Preface and Books I–IV; Schaff's introductory note and index omitted by the extraction. |
| The Incredulity of Father Brown | Dedication, Note, and eight stories. SE title page, imprint, colophon, Uncopyright, and cover art omitted; source credits are preserved in our file and record. |
| Saint Francis of Assisi | Chesterton's Francis book alone, not a Francis/Aquinas combined volume. |

The other titles and their recorded edition scopes are listed individually in the inventory. Their missing paragraphs, apparatus, or edition differences require an edition-by-edition check; none is certified complete by this audit.

Additional local reading material exists outside the 64 book files: `data/prayers.js` holds 18 traditional prayers in three groups (some with Latin) and Rosary instructions/mysteries; `data/advent-2026.json` holds 26 curated excerpts with reflections and source references, compiled into `data/reading-plans.json/.js`. They need their own variant/quotation review. The prayer file gives a general public-domain/traditional note without individual print-edition witnesses. Scripture pages direct readers to sources; the Study desk's Bible parser is citation software, not a hosted Bible text. These adjuncts are not silently counted as complete books or altered by this pilot.

## Maintained sources and rendering

| Layer | Authority and behavior |
|---|---|
| Source bytes | `data/texts/*.txt`. Retain unchanged, including licenses, credits, and original spelling. Catalogue hashes protect these files. |
| Bibliography and access | `data/library.json`, compiled to `data/library.js` by `tools/build_library.py`. `access: full-text` alone can describe an external link; `text` is required for hosting. `checked` and `reviewStatus: source-checked` are source/bibliographic checks, not proofreading grades. |
| Provenance | `data/sources/<edition>.json`: source URLs/catalogue snapshots, rights evidence, some named print witnesses and OCR hashes. Several older edition notes are blank; most Gutenberg snapshots do not identify a particular printing. |
| Generic reader | `scripts/library.js`: split on blank lines, trim blocks, escape plain text, 35 blocks per reading section. `styles/library.css` normally preserves every single newline with `pre-wrap`, including hard prose wraps. `scripts/reader.js` adds stored anchors/highlights, settings, and printing. |
| Chapters and stories | `tools/text_pages.py` supplies explicit heading/boundary maps; `tools/build_text_pages.py` validates hashes/order and generates `data/text-pages.json/.js`. `tools/build_static.py` renders Orthodoxy and Father Brown parts from those same blocks. Maps identify boundaries, not a proofread text. |
| Summa pages | `tools/build_summa.py` builds `data/summa.json`; `summa_para()` in `tools/build_static.py` joins wrapped lines, renders underscore emphasis, and marks flagged Supplement blocks. This specialized renderer differs from the generic reader. |
| Existing embedded formatting | TXT line breaks, indentation, underscores, capitalized headings/emphasis, inline bracket notes, and separators vary by source. They are source characters, not consistently tagged semantics. The SE importer explicitly drops XHTML italics; a general regex cannot recover them. |
| Delivery | `textArchive` prefers `texts.bibliothecacatholica.com/texts/` with local fallback. `tools/build_text_archive.py` exports original files/provenance. No delivery TXT changed, so this pilot needs no new text mirror. |
| New presentation support | `readerFormatting` is opt-in, bound to the edition's checksum, with explicit prose block ranges, verse line starts, and exact emphasis spans. `tools/reader_formatting.py` and the browser renderer share the contract. Static chapters, the generic reader, and whole-book print use it. No block or character is removed; existing anchors retain their text and offsets. Other editions retain their layout. |

## Demonstrated findings versus open questions

| Category | Demonstrated in files/code | Still needs checking |
|---|---|---|
| OCR errors | `data/summa-supplement-ocr.json` has 328 flagged blocks. Examples include `remenibrance` (block 19) and `willll` (block 29). These remain flagged; no new guesses applied. | Scan-by-scan adjudication, including apparently plausible words the flagger misses. The prior 1,516 automatic corrections are not 1,516 scan-verified corrections. |
| Broken words | Hopkins has 82 word-hyphen-newline-lowercase patterns. | Some may be ordinary compounds or editorial apparatus; inspect every candidate against a named printing before joining. Inventory counts are not error counts. |
| Page numbers | Bede has a numeric-only block `1907` at index 17. It is a publication year, not evidence of a stray page number. | Running heads and genuine page artifacts need contextual inspection. Do not delete numbers using a global regex. |
| Paragraphs | Every renderer derives blocks from blank lines. Source file/block counts and mapped chapter boundaries are checkable. | Lost paragraph boundaries within a block cannot be detected by that split. No collection-wide paragraph collation has been performed. |
| Verse | Orthodoxy block 93 merges Yeats's first/second line and breaks `And dance / upon` at a TXT wrap. Block 123 and block 227 also visibly flatten quotations. | Blocks 123/227 and poetry-heavy Hopkins, Dante, White Horse, Gerontius, and Patrick require exact line/stanza witnesses before layout changes. No blanket prose reflow. |
| Emphasis | Generic reader escapes `_italic_` literally, including Hopkins and Summa; Summa static pages already render many of these as emphasis. Orthodoxy #130 has no underscore markers. Page 99 shows two italic `if` words missing from its TXT representation. | Full emphasis recovery needs the printing/source markup, not inferred importance or blanket conversion of capitals. SE extraction intentionally discarded emphasis. |
| Footnotes | Source files contain inline/bracket notes; generic reader does not link note calls to note bodies. Summa renders translator notes inline. | Calls/bodies, numbering, note ownership, and any absent notes require manual/source comparisons. No automatic renumbering or unverified missing-note claims. |
| Typography | Straight/curly quotation marks, dash conventions, underscores, and prose wraps differ between TXT editions. Shared `pre-wrap` makes a fixed-width prose file ragged on wide screens and doubly wrapped on narrow screens. | Typographic differences can belong to an edition. Do not silently standardize historical spelling, hyphenation, quotation punctuation, or capitalization. |

## Existing correction records and limits

- Gutenberg snapshots preserve source metadata/credits and upstream corrections or transcriber notes inside the TXT. They do not provide a uniform local per-change ledger.
- Orthodoxy's source record already names the 1909 John Lane witness, records an automated OCR word comparison, keeps `ecstasy` against print `ecstacy`, and records a Chapter IX `at last` / `at least` discrepancy. Those are inherited findings, not a new manual proofread. The latter remains queued for visual verification and a separately recorded correction.
- Incredulity's record and `tools/import_standard_ebooks.py` contain 46 old/new correction pairs against two 1926 OCR witnesses, a pinned SE commit, input-file hashes, and retained SE spelling/hyphenation modernizations. The catalogue's former “checked word by word against scans” description is narrowed to the recorded OCR comparison. The individual corrections were not visually reverified in this audit.
- Supplement: `tools/transcribe_supplement.py` records the extraction/correction method, and `data/summa-supplement-ocr.json` links remaining uncertainty to scan leaves. The source record reports counts, not a complete per-change scan-proofreading ledger. Dictionary-based substitutions require editorial review.
- CCEL Doctrine: source URL/hash, translation/print witness, and extraction inclusions/omissions exist, but no local correction list or whole-book print collation is established.

## First batch and completed pilot

1. **Completed: ordinary hosted Orthodoxy, Chapter IV.** Its 34 body blocks (77–110) are a bounded prose/verse pilot with an existing edition witness. Thirty-three prose blocks now reflow; the Yeats quote uses two displayed lines. Two conditional `if` words in block 92 have italic emphasis. The exact placement of these features was visually checked on printed page 99 of the 1909 John Lane Company printing, [scan leaf n106](https://archive.org/details/orthodoxy1909ches/page/n106/mode/1up). `formattingReview` in `data/sources/pg-130.json` records the page, image hash, scope, and zero textual corrections. No wording, spelling, punctuation, whitespace characters, block boundaries, or order changes. A visible note says this is a formatting pilot, not a full manual proofread. Other chapters keep their existing layout.
2. **Next: remaining Orthodoxy chapters, one chapter at a time.** Verify the other verse quotations and emphasis; visually confirm Chapter IX's recorded discrepancy. Any wording correction needs an exact before/after ledger and an identified print page. Retain the original TXT and derive a separate reviewed reading representation if wording must change; design anchor migration before shipping it.
3. **Then: Supplement Q1 only (three articles).** Review each flagged passage and earlier automatic substitutions against its linked scan pages; record before/after, page/leaf, reason, confidence, and verifier. Broaden only after this bounded sample. This is more urgent textually than typography but needs sustained human/scan adjudication.
4. **Separate later batch: one Hopkins poem and its notes.** Establish line/stanza and emphasis semantics before touching a poetry collection. Avoid applying prose rules across all files.

No substantive correction was made in this pilot, so its textual correction list is empty. No title is newly called “proofread,” and the existing `checked` date is not advanced for layout work. Human proofreading is still needed for all other emphasis, paragraph divisions, footnotes, ambiguous words, and edition differences, including the pilot chapter beyond the specific page-99 features.

## Fidelity checks and editorial procedure

The new regression tests compare browser and Python output for every block of Orthodoxy. Parsed text must match every source character, including newlines and spaces; paragraph IDs remain stable. The generated chapter must contain all 34 original body blocks in order. The validator rejects stale source checksums, out-of-range formatting, or emphasis spans that do not match their quoted source characters. Unreviewed editions cannot acquire automatic prose/verse guesses.

For future substantive corrections, preserve the original source and checksum; identify the exact edition and scan page; retain before/after readings and the reason; distinguish OCR evidence from visual print verification; and leave ambiguity unresolved with a source-linked note. A word-level automated comparison verifies an alignment, not punctuation, emphasis, layout, or a manual line-by-line proofread. A successful build verifies software behavior, not authorial wording.

Validation and browser QA results for the current change belong in CENTRAL.md and its PR, so this document remains an editorial reference rather than a dated deployment handoff.
