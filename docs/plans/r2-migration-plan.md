# R2 migration plan

Round 8, Job B4 (November 23, 2026). A plan, not a change: nothing is uploaded and no file leaves git this round. Which repository
files could later be served from R2 instead, in what order, and how much that saves. Inventory: [R2-INVENTORY](../R2-INVENTORY.md);
procedures: [R2-RUNBOOK](../R2-RUNBOOK.md).

## Where the size is

The `main` working tree is about 396 MB in 9,185 tracked files, mostly generated HTML and text. Binary files (PDF, EPUB, and
images) come to 56 MB in 801 files. The git history is about 1.9 GB packed; removing a file from the tree does not shrink history,
so R2 mostly helps future growth (scans, PDFs, and more EPUBs never enter git), not today's clone size.

| Path | Size | Files | Could move to R2? |
|---|---|---|---|
| `downloads/epub/` | 27.8 MB | 57 | **Yes, later (step 2).** Built by `tools/build_epub.py`; content-hashed names already suit immutable keys (`epub/<name>`). |
| `data/sources/pdf-prints/` | 4.1 MB | 3 | **Mirror only.** Preserved provenance (AGENTS rule 8: `data/sources/` stays); R2 gets a copy for reader downloads. |
| `docs/research/` images | 15.9 MB | 119 | **Possible (step 3).** Review screenshots and contact sheets, not served to readers; could move to R2 under a non-public prefix or an archive, with checksums kept in the notes. Owner's call. |
| `assets/covers/`, `assets/portraits/`, `assets/hero/` | 8.2 MB | 770 | **No.** Small, needed by every page build and the OG images; keeping them in git keeps the site self-contained. |
| `data/texts/` | 77.2 MB | 154 | **No.** Original text bytes are preserved in git (AGENTS rules 2 and 8); the texts site is the delivery copy. |
| `pagefind/` | 56.8 MB | 1,141 | **No (build-on-deploy instead).** Generated search index; after the Cloudflare build-on-deploy switch it stops being committed. |

## Steps

1. **Batch 1 (pending approval).** Upload the scans that pair with hosted texts, the existing EPUBs, the three source PDFs, and the
   witness scans: 96 files, 1.09 GB. Git keeps every file; the site links to R2 copies only where the manifest records a verified
   upload (draft PR for B3). Nothing is removed.
2. **EPUBs served from R2.** Once batch 1 has been live for two weeks with no broken downloads: `tools/build_epub.py --publish`
   writes the EPUB, uploads it with `r2_upload.py` (new `epub/` key per content hash), and records it; work pages link
   `files.bibliothecacatholica.com/epub/...`; `downloads/epub/` leaves the tree, with a new Cloudflare Pages `_redirects` file
   (there is none today; it would be written by a build tool, never by hand) so old links keep working. Saves 27.8 MB of tree now and about 0.5 MB per new
   EPUB. EPUB generation stays in CI, with epubcheck, before upload. Needs the owner's go (hosting change).
3. **Research images (optional).** Move `docs/research/**/*.png|jpg` to R2 under `research/` (not linked from the site), keep a
   checksum list in each research folder. Saves 15.9 MB of tree. Owner's call: these are review evidence.
4. **New scans and PDFs never enter git.** From batch 2 on, new scans live only in R2 (with their manifest record and source
   checksum), so hosting many more books with their originals costs no repository size.

Total tree saving from steps 2 and 3: about **44 MB** (11% of the tree, 78% of its binaries). The larger gain is that the 73.8 GB of
page images and the scan PDFs for future books stay out of git entirely.

## What does not change

`CNAME`, `.nojekyll`, `.well-known/atproto-did`, verification files, `_headers`, `assets/og-image.png`, `data/texts/`, and
`data/sources/` stay in git. The reader keeps reading the hosted TXT first; downloads and scans stay secondary links. No new
analytics events: R2 links use the existing outbound and download tracking.
