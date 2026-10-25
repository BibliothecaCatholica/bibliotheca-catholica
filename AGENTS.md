# AGENTS.md: continuity guide for Bibliotheca Catholica

Read this before changing the site. It applies to every contributor and coding agent (Codex, ChatGPT, Grok Bot, and others). Owner: Micah Watson, micahwatson@bibliothecacatholica.com. Live site: https://bibliothecacatholica.com (GitHub Pages from `main`).

## Architecture

- **Static single-page app.** Vanilla HTML, CSS, and JavaScript: `index.html`, `app.js` (router and most views), `scripts/library.js` (reading room, work pages, LibriVox buttons), `scripts/guides.js` (edition guides and reading paths), `scripts/search.js`, `styles.css` plus `styles/`. Routes are hashes (`#/author/<id>`, `#/work/<id>`, `#/read/<work>/<edition>`, `#/editions/<id>`, `#/reading/<id>`, `#/isidore/book/<n>`, `#/policy`).
- **Reader (v11):** `scripts/reader.js` (loaded after `scripts/library.js`, before `app.js`) and `styles/reader.css` add highlights and notes, the sticky edition banner with progress, the contents sidebar (sticky at ≥1100px, a drawer below), keyboard shortcuts, the mobile bottom bar, Print / save as PDF, and Continue reading. `scripts/library.js` `read()` calls `BCReader.enhance(...)` after rendering a section; the home page and Discover & Read call `BCReader.continueRow()`. Pure logic lives in `BCReader.core` and is tested in `tests/reader.test.js`. See "Reader storage and features" below.
- **Data lives in files, not a server.** `data/catholic-hub.json` = `data/data.js` (authors, resources, eras), `data/library.json` → `data/library.js` (selected works and editions), `data/guide.js` (edition guides and reading lists, built from `tools/editions_data.py` and `tools/reading_lists.py`), `data/reading-options.json/.js` (EPUB options), `data/isidore-matches.*`, `data/librivox.*`, `data/editorial-flags.*`, and `data/books.js` (the 6,633-record Isidore Index, lazy-loaded, about 1.2 MB). Each `.js` file is a generated copy of its `.json`; never edit only one of them.
- **No build step to serve.** The one generator that must be rerun is `python3 tools/build_static.py`. It pre-renders about 630 static entry pages (`author/`, `work/`, `editions/`, `reading/`, sections, `policy/`) from `index.html`, and it writes `sitemap.xml`, `robots.txt`, and `404.html`. **Rerun it whenever you change `index.html` (header, footer, script tags, meta), routes, authors, works, edition guides, reading lists, or editorial flags, and commit the output.** CI fails if the output is stale.
- When you bump the `?v=` cache-busting query on script tags in `index.html`, keep `data/data.js` as a script tag: `build_static.py` inserts `window.BC_BOOT` right before it.

## Google Analytics (GA4)

- Measurement ID **`G-HFG445Y1LT`**. Every HTML content page must carry **exactly one** copy of the standard Google tag (gtag.js) snippet, placed immediately after `<head>`. The owner-supplied Search Console verification file `google3b007babfa8923a4.html` is a verification response, not a content page: retain its exact original bytes, add no analytics or HTML wrapper, and keep it published at the site root.
- The single source is `index.html`. `tools/build_static.py` copies it into every static page and into `404.html` (it fails if `index.html` has zero or two tags). Never paste the tag into generated pages by hand, never remove it, and never add a second tag, Google Tag Manager container, or another analytics script without the owner's approval.
- The site is a hash-route SPA. The `gtag('config', ...)` call sends the first page view; `app.js` sends `gtag('event','page_view',...)` (title, full URL, and path with hash) only on later `hashchange` events, guarded by `typeof gtag==='function'`. Do not add `send_page_view` changes or a second page-view listener, or visits will be double-counted.
- The privacy disclosure is the "Privacy" section at the end of the Fidelity & Editorial Policy (`tools/build_editorial_flags.py`, `#/policy`, `/policy/`), linked from the footer as "Privacy & Analytics". Keep it accurate if analytics change. `tests/test_analytics.py` checks all of this.
- Google Search Console verifies the domain by DNS TXT record (owner-managed DNS) or by this GA tag; do not add or remove `google*.html` verification files or verification meta tags without the owner's approval.

## Reader storage and features (v11)

Everything a reader saves stays in that browser's `localStorage`; nothing is sent to this site, Google, or anyone else. Keep it that way (no sync, no accounts, no analytics events containing notes or quotes), and keep the Privacy section sentence in `tools/build_editorial_flags.py` accurate.

| Key | Value | Written by |
|---|---|---|
| `bc-notes:<workId>/<editionId>` | `{v:1,items:[{id,s,a:{start,end,exact,prefix,suffix,p,po},c,n,ct,ut}]}`: highlights and notes. `a` is a text-quote anchor: `exact` plus 40 characters of `prefix`/`suffix`, offsets within the section text (paragraphs joined by a blank line), `p` = global paragraph index of the start, and `po` = offset in that paragraph. `c` is `yellow`, `green`, `blue`, or `pink`; `n` is the note. | `scripts/reader.js` |
| `bc-recent` | Continue reading list, newest first, at most 8: `[{w,e,p,n,t,title,author}]` (`p` section index, `n` section count). | `scripts/reader.js` |
| `bc-reading:<editionId>` | Saved section index. | `scripts/library.js` |
| `bc:reader-size`, `bc:reader-spacing` | Display preferences. | `scripts/library.js` |
| `bc-listen:<workId>` | Listen dock state (recording, chapter, time, open). | `scripts/library.js` |
| `hub-theme` | `light` or `dark`. | `app.js` |

- **Anchoring:** highlights resolve by offset first, then by searching the section for the exact quote and choosing the occurrence whose prefix and suffix match best. Sections are 35 paragraphs (`size` in `read()`); `p` lets highlights find their section even if that size changes. If a passage can no longer be found, My notes still lists it as unplaced. Do not change `splitText()` or the `reading-p-<index>` paragraph ids without a migration.
- **My notes panel:** lists a work's highlights, jumps to them, and edits or deletes them. It exports notes as Markdown or plain text, and backs up or restores everything (notes, Continue reading, saved places, and preferences) as JSON (`format: "bibliotheca-catholica-reader-backup"`, merged by highlight id, newer edit wins).
- **Shortcuts:** ← or k (previous section), → or j (next), / (find in work, overrides the site search only in the reader), t (contents), n (notes), Esc (close a panel), ? (help). `BCReader.core.shortcutAction()` ignores keys while typing in inputs, textareas, selects, contenteditable, or media controls, and with Ctrl, Cmd, or Alt.
- **Edition banner:** "Reading: <title>, tr. <translator>, Project Gutenberg #N" (from `editionLine()`), with "Section X of Y" and a percentage bar. On screens ≤760px it collapses to a one-line chip pinned at the top, the site header scrolls away, and a bottom bar (Prev, Contents, Notes, Find, Next; 44px targets; safe-area insets) hides on scroll down. The Listen dock sits above that bar and moves with it.
- **Print:** `styles/reader.css` has the print stylesheet. "Print / save as PDF" prints the current section or the whole work, and the printout must keep the edition line and the Project Gutenberg license notice (the whole-work printout repeats the notice at the start and end). Never hide `.pg-notice` or `.print-edition` in print.
- **Accessibility:** reader controls have labels, panels move focus in and restore it on close, `:focus-visible` rings are on, and reader text meets 4.5:1 contrast in light and dark (site-wide since v12; see "Palette and text contrast").

## Palette and text contrast (v12)

Colors come from the tokens at the top of `styles.css` (`:root` for light, `[data-theme=dark]` for dark). Any text color, in **both** modes, must keep a contrast ratio of at least **4.5:1** against the background it sits on (3:1 only for large text, 24px+ or 18.66px+ bold). Check both themes before changing a token or adding a text color.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--muted` | `#6f604b` (was `#867660`) | `#a49b8c` (was `#9a907f`) | secondary and fine-print text |
| `--gold-ink` (new) | `#80601a` | `#d9b45a` | gold **text** (eyebrows, dates, counts, brand subtitle, DJVU badge). `--gold` (`#b8892d`) is for borders, rules, and fills only, never small text in light mode |
| `--on-rubric` (new) | `#fff8ea` | `#14161c` | text on `--rubric`/`--rubric2` fills (`.btn`, `.chip.on`, `.mainnav a.on`, Bookshop button, reader controls). Never hard-code `#fff`/`#fff8ea` on a rubric fill: dark-mode rubric is light pink |
| `--rubric` | `#8b1e2d` (unchanged) | `#e37f89` (was `#e0707b`) | links, accents, and filled buttons |

Text on gradients (`.btn.gold`, `.sec-card .glyph`, `.avatar`) must also pass against every part of the gradient behind the text.

## Files that must never be deleted or moved

**Document archive:** `BibliothecaCatholica/bibliotheca-texts` serves the 42 verified TXT copies at `https://texts.bibliothecacatholica.com/texts/`. The main reader prefers that host and falls back to local `data/texts/`. Keep local originals and provenance. `textArchive` in `data/library.json` controls this behavior. Export offline with `python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts`; review the manifest and checksums before publishing the separate repository. Do not bulk mirror unreviewed imported books. See `docs/PROJECT-REVIEW-2026-10-22.md`.

**Adding a hosted Gutenberg text (v10 pattern):**
1. Check the specific edition or translation year in the Gutenberg front matter (pre-1931 only; record the evidence in the edition `note`).
2. `python3 tools/fetch_gutenberg_edition.py <PG number> ...` downloads the original `pgN.txt` bytes to `data/texts/pg-N.txt`, snapshots the catalog record to `data/sources/pg-N.json`, and prints the SHA-256. It never edits `data/library.json` and skips releases with no plain-text file.
3. Add the work and edition to `data/library.json` by hand (`label`, `rights`, `checked`, `note`, `sourceTitle`, `text`, `sha256`), with `"added": "YYYY-MM-DD"`. The `added` date drives the **Recently added** section on Discover & Read and a "New" card badge for 90 days.
4. `python3 tools/fetch_librivox.py` rebuilds `data/librivox.json/.js` and the per-recording chapter lists in `data/librivox/<id>.json` that power the reader's persistent **Listen** dock. Use the work's `audioTitles` array for LibriVox title aliases; leave out a recording that is clearly a different work.
5. `npm run build`, update test counts, then re-export and push `bibliotheca-texts` (step above) so the text is served from the texts subdomain.

`CNAME`, `.nojekyll`, `.well-known/atproto-did` (the Bluesky handle; leave it unchanged), `robots.txt`, `sitemap.xml`, `404.html`, `assets/og-image.png`, `data/texts/`, and `data/sources/`.

## Content rules (non-negotiable)

1. **Public domain cutoff.** Host full texts only if they were published before 1931 (US public domain) and the edition's rights have been checked. Anything later is a link out.
2. **Gutenberg notice.** Every reader section of a Project Gutenberg text shows the Gutenberg license notice; downloaded texts keep the full original license.
3. **Reading room first.** "Read here" is the primary way to read. Isidore EPUB and PDF downloads are an alternate format ("Other formats"), not the headline.
4. **Editorial flags.** Fringe, conspiracy, and sedevacantist titles in the Isidore Index stay listed (removing them feeds the conspiracy), but each gets a calm, factual context note, the Dignitatis Humanae 1 and 3 disclaimer quoted verbatim from vatican.va, and a link to the Fidelity & Editorial Policy (`#/policy`, `/policy/`). Listing is not endorsement. Sedevacantist works are labeled as sedevacantist. Do not add Nostra Aetate quotes without the owner's approval.
5. **Flagged titles are never featured.** They must not appear on the home page, in reading lists, edition guides, reading options, reading-room matches, recommendations, the sitemap, or static pages. Flagged book pages carry `noindex`.
6. **Search defaults to "Everything"** (selected works rank first; the scopes are Everything, Selected library only, and Isidore Index only).
7. **Money.** Bookshop.org affiliate ID `130222` only (`data/affiliates.js`). No Amazon links. Donations are never described as tax-deductible (the library is a sole proprietorship, not a 501(c)(3)).
8. **Style.** Use the Oxford comma. Keep notes neutral and sourced. Do not contact outside sites (isidore.co, CCEL, and others) on the owner's behalf; draft only.

## How to add things

- **A reading-room work or edition:** follow `docs/CATALOG.md`. Edit `data/library.json` (with rights evidence in `data/sources/`, plus `data/texts/` and SHA-256 if hosted), then run `npm run build`.
- **An author or resource:** load, edit, and save with `tools/hubio.py` (`load()` and `save()`) so `catholic-hub.json` and `data.js` stay identical. Author ids are kebab-case slugs used in URLs.
- **An edition guide or reading list:** edit `tools/editions_data.py` or `tools/reading_lists.py`, then run `npm run build`. Never add a flagged title.
- **An editorial flag:** add the Isidore book id to `tools/build_editorial_flags.py` with a category (`antisemitic-content`, `polemical-historical`, `sedevacantist-position`, or `author-context`) and a factual note. Then run `python3 tools/build_editorial_flags.py`, `python3 tools/build_open_data.py`, and `python3 tools/build_static.py`.
- **LibriVox audio:** run `python3 tools/fetch_librivox.py` (network) and review the matches.
- After any of these, run `python3 tools/build_static.py`.

## Before opening a PR

```sh
npm run build                         # library.js and guide.js must not change afterward
python3 tools/build_static.py         # static pages, sitemap, and robots must not change afterward
git diff --exit-code                  # nothing stale
npm test                              # node tests (incl. reader anchoring and shortcut guard) plus tests/test_*.py (editorial flags, v9 crawlability, catalog, analytics)
node --check app.js && node --check scripts/reader.js && node --check scripts/library.js && node --check scripts/guides.js && node --check scripts/search.js
```

Optional network checks: `python3 tools/check_links.py` (writes `docs/link-health.*`) and `python3 tools/check_library_links.py --output /tmp/source-links.json`. Then preview with `npm run dev` and check the home page, an author page, `/policy/`, a flagged book (for example `#/isidore/book/3895`), and a reading-room work with a Listen button (highlight a passage, reload, and check My notes, Continue reading on the home page, and the print preview).
