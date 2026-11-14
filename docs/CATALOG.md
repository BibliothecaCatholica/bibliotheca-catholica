# Catalog and reading editions

## Catalog and delivery inputs

The 64 hosted TXT editions are also published at `https://texts.bibliothecacatholica.com/texts/` from `BibliothecaCatholica/bibliotheca-texts`. `textArchive` in `data/library.json` controls the reader's preferred host. Original local paths, hashes, and source records remain authoritative; the reader falls back to local files on archive failure. Export with `python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts`. The export preserves original bytes and includes provenance, a searchable directory, and a manifest. See `docs/archive/PROJECT-REVIEW-2026-10-22.md` for the full assessment.

`data/library.json` is the maintained source; `python3 tools/build_library.py` validates it and emits `data/library.js`. Both are committed so the site can still deploy as plain static files. There are no production API keys, application server, or database. The Study desk bundles pinned npm dependencies; see [OPERATIONS](OPERATIONS.md#validation) for setup.

Each **work** has an identity, author, subject, tradition, optional work date, and review status. Each **edition** has its own identity, language, credited contributor roles, source URL, access type, rights statement, and check date. A hosted **copy** additionally has a local text path and SHA-256 checksum. Unknown publication/translation dates and contributor roles are left unspecified. A Gutenberg digital-release date is not the work's composition date.

## Release history

Dated additions, skipped candidates, and source-check results are in [catalog release notes](archive/CATALOG-RELEASE-NOTES.md). They are historical observations, not the current ingestion procedure.

## Catalog snapshot (November 9, 2026)

64 Gutenberg editions in the catalog, 61 hosted. This count is checked against `data/library.json` by `tests/test_counts.py`. Use the catalog for edition details; source snapshots establish the scope of each individual check.

## Corrections and boundaries

- Gutenberg 8120 is Teresa's **Life**, not **Interior Castle**.
- Gutenberg 70790 is **Charles Coppens's adapted retreat edition** of Ignatian exercises, not an unqualified critical text of the original.
- Gutenberg 50040 credits **Leonard J. Doyle**, not Gasquet.
- Gutenberg 204 is **The Innocence of Father Brown**, not the complete Father Brown stories.
- Gutenberg 63084 contains **Saint Francis**, not Chesterton's combined Francis/Aquinas volume; 8442 contains **Europe and the Faith**, not *The Path to Rome*.
- Gutenberg 5657 carries a copyright notice and remains external. The source's U.S. public-domain designation was required before adding any hosted edition; it is not represented as worldwide clearance.
- Existing guide links to covered editions now show the actual work title and its local edition page, making differences from a recommended print edition visible.
- The claim that *The Everlasting Man* “baptised” Lewis's imagination was removed; that phrase concerns MacDonald's *Phantastes*. No substitute quotation was added.

The 6,633-book Isidore import is preserved separately and is **unreviewed**, including its automatic author associations. “Selected library” search includes the site's existing author/resource/guide selections plus the new catalog, but excludes imported books and folders. Older selections have not all received a fresh bibliographic audit. Search scopes are encoded in the URL.

## Adding a reading edition

1. Identify the exact work and edition at its source. Credit translators, editors, or adapters only with evidence. Keep abridgments, adaptations, and partial collections explicit.
2. Record the catalog metadata and rights evidence in `data/sources/`. Add an edition with `access: "full-text"` or `"reference"`; reference links must not imply a readable text.
3. Only host a text whose edition rights have been checked. Keep the complete original notices and credits; save the source bytes in `data/texts/` and record their SHA-256. Other files remain source links. The current validator supports the checked Gutenberg public-domain ingestion path; an OCR transcription of pre-1931 Internet Archive scans for the Summa Supplement (`kind: ocr-transcription`); and a public-domain text with its own provenance record (`kind: public-domain-text`): On Christian Doctrine from CCEL NPNF1-02, and The Incredulity of Father Brown from Standard Ebooks (CC0), corrected to the 1926 printings (`tools/import_standard_ebooks.py`). Any other new source needs its own rights validation before hosting.
4. Run `npm run build` and `npm test`. Optionally run `python3 tools/check_library_links.py --output /tmp/source-links.json` and inspect returned titles/redirects. That checker never changes catalog records.

The reading interface renders escaped plain text, not third-party HTML or iframes. It loads one edition on demand, offers full-text paragraph search, source heading links when recognizable, section navigation, local reading-position persistence, typography settings, and original-source/download fallbacks. Sections are navigation chunks, not scholarly chapter or paragraph numbers. Scans, footnote formatting, images, and modern scholarly apparatus are best consulted at source. No account or tracking service was added.

## Hosted-text quality

The [hosted inventory](HOSTED-TEXT-INVENTORY.md) distinguishes the actual local editions from external links and records their scope. The [editorial assessment and procedure](HOSTED-TEXT-QUALITY.md) separates demonstrated defects from review leads and documents the bounded Orthodoxy Chapter IV formatting pilot. Source and rights checks do not establish a manual proofread.

## Follow-up editorial work

This release establishes the model rather than claiming a complete scholarly catalog. Expand the reviewed collections by topic, give each edition a human editorial pass, add exact translation/publication dates when established, and audit the older guide's remaining outbound links and attributions. PDF/EPUB rendering and account-synchronized annotations are not part of this release.

## Reading room and Isidore downloads

The reading room is the primary way to read. EPUB and PDF files in the St. Isidore e-book library are the alternate path. `python3 tools/match_isidore.py` writes `data/isidore-matches.json` and `.js` from `library.json` and `books.json`, with no network access. A work and an Isidore book match only when:
- the title is the same (ignoring a leading article, "Saint"/"St.", and "Holy"), or the Isidore title adds only a tail naming the author, or extends a title of three or more words;
- an author name token also matches;
- the book has an EPUB or PDF file.

Commentaries, guides, selections, and numbered volumes are excluded, and Anglican (Lewis) reference records are never matched. Matched works show **Other formats** on their work page. Matched Isidore books whose work has a hosted reading edition show **Read online here**. Review the printout whenever the catalog changes; translations may differ between the two paths.

## Reading access audit

Every selected work now has an original description and a direct full-text or sample access path. Lewis's eight bibliography records remain as publication references, with two PBS excerpts and six Google Books/Play samples in a separate `readingLinks` field. Samples never count as hosted or complete texts. Library searches are labeled as searches, with no promise of holdings or borrowing eligibility. The validator rejects a reference-only work without a reading sample.

The collection-wide audit tool, `tools/audit_collection.py`, inventories the selected catalog, all guide/list entries, New Advent work links, supplemental collections, author reading links, and imported book metadata. Its report distinguishes HTTP reachability from a bibliographic review. Imported download files are not fetched in bulk. See `docs/COLLECTION-REVIEW.md` for findings and unresolved checks.
