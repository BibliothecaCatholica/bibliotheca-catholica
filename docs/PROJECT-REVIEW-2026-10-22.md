# Bibliotheca Catholica: project review, October 22, 2026

## Where the project stands

The project has developed from a directory into a reading environment: find a work, understand its edition, read an eligible copy, choose another format, listen where an audio match exists, and continue through a reading path. The selected library and imported Isidore catalog remain distinct. Breadth belongs to the index; stronger edition checks belong to the hosted collection.

Source baseline: main commit `5af56d9`, including PRs #1–#5 and the subsequent v9 changes present when this review began. Counts describe maintained records, not a textual or theological review of every imported book.

| Area | Scope | What changed and why it matters |
| --- | ---: | --- |
| Selected works | 49 | Work identities, descriptions, edition contributors, access labels, source links, and rights notes replace loosely related destinations. |
| Complete-text access | 41 works | 22 have our hosted reading copies; 19 rely on external complete texts. |
| Related Christian writers | 8 Lewis works | Individual excerpts or limited previews replace a bibliography dead end. Anglican identity and partial access are explicit; these are not hosted complete books. |
| Hosted files | 22; 13,039,652 bytes | Original Gutenberg bytes and notices remain intact. The document repository adds file checksums and source metadata. |
| Edition guides | 69 | Reading links precede optional print recommendations; recommended translations remain distinct from available free editions. |
| Reading paths | 13; 115 entries | Searchable paths identify an audience and starting point, with reading and edition actions. |
| Imported Isidore records | 6,633 | Search and downloads remain available; 75 records without files say so. Imported files have not been bulk copied. |
| Author profiles | 476 | Biographies connect to works, reading copies, and source collections. |
| Curated resources | 225 | Scripture, Church documents, references, prayer, media, and external libraries broaden the environment. |
| LibriVox matches | 22 work keys; 26 edition keys | Audio supplements reading. These are matching keys, not necessarily unique recordings or identical translations. |
| Editorial flags | 54 imported records | Context notes and a policy link distinguish listing from endorsement; flagged records stay out of featured recommendations. |
| Crawlable pages | 627; 628 sitemap URLs including home | Static author, work, edition, reading-list, and section pages provide content beyond hash navigation. |

## Changes across the work so far

1. **A reading room.** Text size, spacing, saved section progress, source-heading navigation, and searching across a work support actual reading. Original credits and Gutenberg notices remain available. Sections are navigation chunks rather than scholarly chapters or citations.
2. **Edition identity.** Corrections distinguish Teresa's autobiography from Interior Castle, Coppens's adapted Ignatian retreat from the original Spiritual Exercises, individual Chesterton books from collected works, New Advent's Knox English from Douay-Rheims, and RSV-CE from RSV-2CE. Doyle's 1948 Rule and the 1958 Pensées remain external under the pre-1931 hosting rule.
3. **Clear access.** Cards distinguish reading here, complete text at source, and excerpts/previews. WorldCat and Open Library title searches provide a next step without promising holdings or a digital loan. The eight Lewis recommendations now lead to title-specific reading samples.
4. **Reading paths and editions.** “Which Edition?” became Editions & Translations. Companion works and adaptations are separate from primary copies. Thirty-one guides still lack a listed complete free copy: a real remaining access gap.
5. **Navigation and appearance.** Original parchment, burgundy, and gold light colors and charcoal/navy dark colors were restored. Podcasts & Media and Timeline are visible in primary navigation. Open Data sits in the footer; Vatican links belong in content. Mobile navigation gained accessibility and keyboard improvements.
6. **Broader sources and collection review.** Gutenberg, Standard Ebooks, CCEL, New Advent, Vatican documents, archives, and other Catholic collections supplement Isidore. Unrelated redirects and inaccurate edition labels were corrected. The broader audit covered 1,629 destinations, with 22 inconclusive checks; it did not inspect every downloaded book.
7. **Subsequent v9 work preserved.** The newer main branch adds crawlable entry pages, canonical URLs, social metadata, a sitemap, LibriVox links, library references, editorial flags, a Fidelity & Editorial Policy page, and AGENTS.md. These changes were already on main when this storage pass began.

## Hosting introduced in this pass

`BibliothecaCatholica/bibliotheca-texts` is the dedicated document repository, published through GitHub Pages at `texts.bibliothecacatholica.com`. This replaces the initial Squarespace 302 forwarding rule. Squarespace manages DNS and supplies no document storage here.

The first batch is the 22 already-hosted TXT editions. The archive provides a searchable title/author/translator directory, direct downloads, links to the main reader, source records, and `manifest.json` with file sizes and SHA-256 hashes. No edition was copied merely because it appears in the imported catalog. EPUBs, PDFs, official Vatican texts, New Advent texts, and Lewis samples remain at their existing providers unless reviewed and exported later.

The main reader requests the archive copy first and falls back to the existing local copy on failure or timeout. Local `data/texts/` and `data/sources/` stay in place. This is a first hosting separation, **not yet a reduction in the main repository's stored bytes**. Removing duplication later requires a stable archive, independent backups, and corresponding contributor-rule changes.

Export offline with `python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts`. The tool validates the maintained catalog and original hashes, refuses to export inside the main checkout, and never deletes older archive files. Review stale files explicitly during subsequent exports.

## Assessment and remaining priorities

The strongest niche is a trusted route from Catholic discovery to actual reading: broad sources, clear editions, readable copies, and useful next steps. The site cannot yet claim to be an exhaustive Catholic repository or a fully reviewed digital critical library.

| Priority | Improvement | Value |
| --- | --- | --- |
| 1 | Expand checked complete works and exact editions | Closes reading gaps without turning the imported index into an unreviewed mirror. |
| 2 | Add verified EPUBs and selected searchable PDFs | Supports portable and print-friendly reading. Scans require OCR and image-quality review. |
| 3 | Improve chapter structure, bookmarks, and citations | Supports sustained reading and references beyond 35-paragraph sections. |
| 4 | Add corpus full-text search | Finds passages as well as titles. Global search currently searches catalog metadata, not every hosted text. |
| 5 | Add alternate translations, original languages, and completeness metadata | Makes translation comparison more useful and keeps adaptations distinct. |
| 6 | Maintain backups, integrity checks, link checks, and storage budgets | Separates preservation from deployment; Git history alone is not an independent backup. |

This batch uses about 13 MB. GitHub Pages' 1 GB published-site limit and soft 100 GB monthly bandwidth limit still matter. Separate repositories organize the application and collection; they do not provide unlimited archival hosting. Track published bytes and traffic before adding large scans or audio. Additional paid storage is not required for this first batch.

## Validation and evidence

The current suite passes 12 Node tests and 19 Python tests, including new export integrity and reader fallback checks. The static generator produces 627 entry pages. Deployment checks must also verify live file hashes, browser cross-origin loading, DNS, and HTTPS; offline tests alone establish none of those.

Supporting records: `docs/CATALOG.md`, `docs/COLLECTION-REVIEW.md`, `docs/collection-audit.json`, `docs/READING-GUIDES.md`, `docs/PALETTE-NAVIGATION.md`, and `AGENTS.md`.

GitHub's current limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
