# AGENTS.md: continuity guide for Bibliotheca Catholica

Read this before changing the site. It applies to every contributor and coding agent (Codex, ChatGPT, Grok Bot, and others). Owner: Micah Watson, micahwatson@bibliothecacatholica.com. Live site: https://bibliothecacatholica.com (GitHub Pages from `main`).

## Architecture

- **Static single-page app.** Vanilla HTML, CSS, and JavaScript: `index.html`, `app.js` (router and most views), `scripts/library.js` (reading room, work pages, LibriVox buttons), `scripts/guides.js` (edition guides and reading paths), `scripts/search.js`, `scripts/analytics.js` (GA4 event helper), `styles.css` plus `styles/`. Routes are hashes (`#/author/<id>`, `#/work/<id>`, `#/read/<work>/<edition>`, `#/editions/<id>`, `#/reading/<id>`, `#/isidore/book/<n>`, `#/policy`).
- **Reader (v11):** `scripts/reader.js` (loaded after `scripts/library.js`, before `app.js`) and `styles/reader.css` add highlights and notes, the sticky edition banner with progress, the contents sidebar (sticky at ≥1100px, a drawer below), keyboard shortcuts, the mobile bottom bar, Print / save as PDF, and Continue reading. `scripts/library.js` `read()` calls `BCReader.enhance(...)` after rendering a section; the home page and Discover & Read call `BCReader.continueRow()`. Pure logic lives in `BCReader.core` and is tested in `tests/reader.test.js`. See "Reader storage and features" below.
- **Data lives in files, not a server.** `data/catholic-hub.json` = `data/data.js` (authors, resources, eras), `data/library.json` → `data/library.js` (selected works and editions), `data/guide.js` (edition guides and reading lists, built from `tools/editions_data.py` and `tools/reading_lists.py`), `data/reading-options.json/.js` (EPUB options), `data/isidore-matches.*`, `data/librivox.*`, `data/editorial-flags.*`, and `data/books.js` (the 6,633-record Isidore Index, lazy-loaded, about 1.2 MB). Each `.js` file is a generated copy of its `.json`; never edit only one of them.
- **No build step to serve.** The one generator that must be rerun is `python3 tools/build_static.py`. It pre-renders about 728 static entry pages (`author/`, `work/`, `editions/`, `reading/`, `saints/`, sections, `about/`, `policy/`) from `index.html`, and it writes `sitemap.xml` (729 URLs with the home page), `robots.txt`, and `404.html`. Since v17 it also rewrites the marked regions of `index.html` itself (see "SEO" below). **Rerun it whenever you change `index.html` (header, footer, script tags, meta), routes, authors, works, edition guides, reading lists, or editorial flags, and commit the output.** CI fails if the output is stale.
- **Saints & Hagiography (v15):** `scripts/saints.js` (`window.BCSaints`, loaded before `app.js`) and `styles/saints.css` render `#/saints` (landing with the Hodie block), `#/saints/az[/<letter>]`, `#/saints/calendar[/<MM-DD>]`, `#/saints/writers`, `#/saints/legend`, `#/saints/books` (the hagiography shelf), `#/saints/about`, and `#/saints/<id>` (tier 2 and 3 profiles; tier 1 writers redirect to `#/author/<id>`, which gains a Saint panel). Data: `data/saints.json` → `data/saints.js` (`window.SAINTS_DATA`, about 310 KB, lazy-loaded by `BCSaints.load()`) and `data/saints-aliases.json`, all built by `python3 tools/build_saints.py` (part of `npm run build`). See "Saints" under Content rules and `docs/SAINTS.md`.
- **Rights badges (v16):** `scripts/rights.js` (`window.BCRights`, loaded before `scripts/library.js` and `app.js`) and `styles/rights.css`. Index statuses live in `data/rights.json` → `data/rights.js` (`window.RIGHTS_DATA`, about 190 KB, keyed by Index id, lazy-loaded with `data/books.js`; `books.js` itself is unchanged). `tools/build_rights.py` (part of `npm run build`) validates them, writes `data/rights.js`, adds each match's status `r` to `data/isidore-matches.*`, and writes `data/rights-pages.js` (the `#/rights` and `#/takedown` HTML from `tools/rights_pages.py`, also used by `build_static.py` for `/rights/` and `/takedown/`). See "Rights" under Content rules and `docs/RIGHTS.md`.
- When you bump the `?v=` cache-busting query on script tags in `index.html`, keep `data/data.js` as a script tag: `build_static.py` inserts `window.BC_BOOT` right before it.

## Google Analytics (GA4)

- Measurement ID **`G-HFG445Y1LT`**. Every HTML content page must carry **exactly one** copy of the standard Google tag (gtag.js) snippet, placed immediately after `<head>`. The owner-supplied Search Console verification file `google3b007babfa8923a4.html` is a verification response, not a content page: retain its exact original bytes, add no analytics or HTML wrapper, and keep it published at the site root.
- The single source is `index.html`. `tools/build_static.py` copies it into every static page and into `404.html` (it fails if `index.html` has zero or two tags). Never paste the tag into generated pages by hand, never remove it, and never add a second tag, Google Tag Manager container, or another analytics script without the owner's approval.
- **Page views (v14).** The config line is `gtag('config', 'G-HFG445Y1LT', {'send_page_view': false});`, so the tag sends no automatic page view. `app.js` `gaPageView()` sends exactly one `page_view` (`page_title`, `page_location`, `page_path` = path plus hash) for the first load (after the first `route()`, which also covers static entry pages through `window.BC_BOOT`) and one per later `hashchange`, debounced 400 ms and deduped by path. `404.html` carries the same config and no `app.js`, so it sends nothing; the `/#/...` page it redirects to counts the visit once. Do not remove `send_page_view: false`, and do not add a second page-view listener. The owner turns off GA4 enhanced measurement "page changes based on browser history events" in GA4 admin so hash changes are not counted twice.
- **Events (v14).** Every event goes through the helper `window.BCAnalytics.track(name, params)` in `scripts/analytics.js` (loaded once, after `data/affiliates.js` and before `scripts/library.js` and `app.js`). It checks `typeof gtag==='function'`, wraps everything in `try/catch`, accepts only the event names below, drops empty values, and caps string params at 100 characters. `app.js` and `scripts/library.js` call it through a local `track()` wrapper; nothing else may call `gtag(` or touch `dataLayer`.

| Event | Params | Fired from |
|---|---|---|
| `page_view` | `page_title`, `page_location`, `page_path` | `app.js` `gaPageView()` |
| `search` | `search_term` (trimmed, lowercased, max 100 characters), `search_scope` (`Everything`, `Selected library`, or `Isidore Index`), `results_count` | `app.js` `results()`: once per visit to a results URL, after the catalogs that scope needs load (or after 8 s); Isidore Index page: a query in the URL, or typing that pauses for 1.5 s (deduped) |
| `open_text` | `work_id`, `text_source` (`hosted` or `external`), `edition_id` (hosted) or `link_domain` (external) | `scripts/library.js` `read()` once per reader opening; external "Read at source" / "Read full text at source" links carry `data-open-text` |
| `reader_section` | `work_id`, `edition_id`, `section_index` | `read()`, once per section per reader session |
| `listen_play`, `listen_complete` | `work_id`, `section_index` (audio chapter), `recording_id` | Listen dock `<audio>` `play` (once per chapter per dock) and `ended` |
| `outbound_click` | `link_domain`, `link_kind` (`bookshop`, `publisher`, `substack`, or `other`), `work_id` (from `#/work/` or `#/read/` routes, or a `data-work` ancestor), `publisher` (key from `data/affiliates.js`; publisher buttons carry `data-pub`) | delegated document click handler in `scripts/analytics.js`, http(s) links to other domains only |
| `filter_use` | `filter_name` (`Format`, `Language`, `Era`, `Tag`, `Subject`, `Linked`, `On-topic`; Discover & Read adds `Read on this site`), `filter_value`, `filter_scope` (`isidore` or `library`) | Isidore Index filters and tag chips, Discover & Read filters |
| `support_click` | `target` (`header`, `menu`, `footer`, `footer_disclosure`, `buymeacoffee`, `paypal`, `bookshop_shop`, `commentary_email`, `correction_email`) | any link with a `data-support` attribute |
| `theme_toggle` | `theme` (`light` or `dark`) | the moon/sun button |
| `saint_open` | `saint_id`, `saint_tier` (1, 2, or 3) | `scripts/saints.js` `profile()`, once per saint profile render (tier 2 and 3 pages; tier 1 saints open their author page) (v15) |

- **Rules.** No new measurement IDs, Google Tag Manager, pixels, or other analytics scripts without the owner's approval. Events go only through the helper. Never send personal data or free text: no notes, highlights, quotes, find-in-work terms, email addresses, or full URLs of outside links (domain only). The search term is the only free text, and it stays trimmed, lowercased, and capped at 100 characters. Adding an event name means adding it to `EVENTS` in `scripts/analytics.js`, to this table, to `tests/analytics.test.js`, and, if it measures something new, to the Privacy section.
- The privacy disclosure is the "Privacy" section at the end of the Fidelity & Editorial Policy (`tools/build_editorial_flags.py`, `#/policy`, `/policy/`), linked from the footer as "Privacy & Analytics". Keep it accurate if analytics change. `tests/test_analytics.py` and `tests/analytics.test.js` check all of this.
- Google Search Console verifies the domain by DNS TXT record (owner-managed DNS) or by this GA tag; do not add or remove `google*.html` verification files or verification meta tags without the owner's approval.

## SEO and discoverability (v17)

Full notes: `docs/SEO.md`. `tests/test_seo.py` enforces these rules.

- **The home page is static.** `index.html` holds generated regions: `<!-- static-home:start -->…<!-- static-home:end -->` inside `<main>` (the about text and section links from `tools/site_copy.py`) and `<!-- jsonld:start -->…<!-- jsonld:end -->` before `</head>`, plus the `<title>` and meta description (`HOME_TITLE` and `HOME_DESC` in `tools/build_static.py`). Edit `tools/site_copy.py` or `build_static.py`, never the regions by hand. It also writes `data/site-copy.js` (`window.SITE_COPY`, used by `app.js` for the home text and `#/about`) with a content-hash `?v=`. Do not bring back a "Loading…" or noscript-only main.
- **Every indexable page** needs a unique `<title>` that contains "Bibliotheca Catholica", a unique meta description of 120 to 160 characters (aim for 150 to 160 with `fit()`), exactly one `<h1>`, a canonical, `og:*` and `twitter:*` tags, `robots` `index,follow` (flagged books stay `noindex`), and JSON-LD that parses. Index and section pages get a visible intro (`INTRO` in `build_static.py`).
- **Header and footer links are real paths** (`/authors/`, `/about/`, and so on) so crawlers can follow them. `app.js` turns them into hash routes only on the root page; on static pages they load the static page. Keep new nav links as paths.
- **Structured data must be true.** The home page has `WebSite` and `Organization` only. `sameAs` lists only verified profiles (GitHub, and Bluesky because `.well-known/atproto-did` matches the handle); add X or others only once the profile is verified. Author pages have `Person` (dates only from data), work pages have `Book`, and pages have `BreadcrumbList`. No `SearchAction` (search is a hash route), and never FAQ, review, or rating schema. No invented facts in bios or descriptions.
- **No ranking tricks:** no keyword stuffing, hidden text, doorway pages, or claims about rankings or traffic. `lastmod` stays out of the sitemap until dates are accurate (CI uses a shallow checkout).
- **About page:** `/about/` and `#/about`, linked in the footer and the home page, and listed in the sitemap.

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

**Document archive:** `BibliothecaCatholica/bibliotheca-texts` serves the 56 verified TXT copies at `https://texts.bibliothecacatholica.com/texts/`. The main reader prefers that host and falls back to local `data/texts/`. Keep local originals and provenance. `textArchive` in `data/library.json` controls this behavior. Export offline with `python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts`; review the manifest and checksums before publishing the separate repository. Do not bulk mirror unreviewed imported books. See `docs/PROJECT-REVIEW-2026-10-22.md`.

**Link-only editions (v14 pattern):** a public-domain scan or text that is not on the validated Gutenberg path (Internet Archive, Fordham, and similar) is an edition with `access: "full-text"` and a `source` URL but no `text`, like the New Advent and Vatican editions. Its card says "Full text at source" and it is never downloaded or mirrored. Leave out `added` on link-only works so **Recently added** ("New in the reading room") lists only texts readable here.

**Adding a hosted Gutenberg text (v10 pattern):**
1. Check the specific edition or translation year in the Gutenberg front matter (pre-1931 only; record the evidence in the edition `note`).
2. `python3 tools/fetch_gutenberg_edition.py <PG number> ...` downloads the original `pgN.txt` bytes to `data/texts/pg-N.txt`, snapshots the catalog record to `data/sources/pg-N.json`, and prints the SHA-256. It never edits `data/library.json` and skips releases with no plain-text file.
3. Add the work and edition to `data/library.json` by hand (`label`, `rights`, `checked`, `note`, `sourceTitle`, `text`, `sha256`), with `"added": "YYYY-MM-DD"`. The `added` date drives the **Recently added** section on Discover & Read and a "New" card badge for 90 days.
4. `python3 tools/fetch_librivox.py` rebuilds `data/librivox.json/.js` and the per-recording chapter lists in `data/librivox/<id>.json` that power the reader's persistent **Listen** dock. Use the work's `audioTitles` array for LibriVox title aliases; leave out a recording that is clearly a different work or an abridgment by listing its LibriVox id in the work's `audioExclude` array (for example, Butler's one-volume *Lives of the Saints with Reflections*, #5324, is excluded from the full Kenedy volumes).
5. `npm run build`, update test counts, then re-export and push `bibliotheca-texts` (step above) so the text is served from the texts subdomain.

`CNAME`, `.nojekyll`, `.well-known/atproto-did` (the Bluesky handle; leave it unchanged), `robots.txt`, `sitemap.xml`, `404.html`, `assets/og-image.png`, `data/texts/`, and `data/sources/`.

## Content rules (non-negotiable)

1. **Public domain cutoff.** Host full texts only if they were published before 1931 (US public domain) and the edition's rights have been checked. Anything later is a link out.
2. **Gutenberg notice.** Every reader section of a Project Gutenberg text shows the Gutenberg license notice; downloaded texts keep the full original license.
3. **Reading room first.** "Read here" is the primary way to read. Isidore EPUB and PDF downloads are an alternate format ("Other formats"), not the headline, and appear only where the rights badge allows (rule 10).
4. **Editorial flags.** Fringe, conspiracy, and sedevacantist titles in the Isidore Index stay listed (removing them feeds the conspiracy), but each gets a calm, factual context note, the Dignitatis Humanae 1 and 3 disclaimer quoted verbatim from vatican.va, and a link to the Fidelity & Editorial Policy (`#/policy`, `/policy/`). Listing is not endorsement. Sedevacantist works are labeled as sedevacantist. Do not add Nostra Aetate quotes without the owner's approval.
5. **Flagged titles are never featured.** They must not appear on the home page, in reading lists, edition guides, reading options, reading-room matches, recommendations, the sitemap, or static pages. Flagged book pages carry `noindex`.
6. **Search defaults to "Everything"** (selected works rank first; the scopes are Everything, Selected library only, and Isidore Index only).
7. **Money.** Bookshop.org affiliate ID `130222` only (`data/affiliates.js`). `bookshopShop` in `data/affiliates.js` is intentionally blank (`''`) until the owner creates or confirms the real Bookshop.org shop URL (the old `https://bookshop.org/shop/bibliotheca-catholica` returned 404 on 2026-10-25). While it is blank, the "Our Bookshop.org shop" button on author pages and the shop line on `#/support` stay hidden; do not fill it in with a guessed URL. `tests/test_affiliates.py` checks this. No Amazon links. Donations are never described as tax-deductible (the library is a sole proprietorship, not a 501(c)(3)).
8. **Saints (v15).** CatholicSaints.Info is **link-only**: its robots.txt bars crawling and its terms forbid copying. Never copy its text, never fetch it at build or run time, and link it only where `data/saints.json` has a `catholicsaints` object, which `tools/import_saints_pilot.py` takes from the hand-checked tier 1 matches in `catholicsaints-mapping.json` (139 links). The link always comes after New Advent and Vatican News. No CatholicSaints.Info links for tier 2 or 3 saints (the 30 name-match-only candidates stay unpublished), and no outreach to its author. Vatican News “Saint of the day” dates are always labelled as such, never as the General Roman Calendar (GRC dates stay `null` until checked against the Roman Missal). The tradition and legend saints (`historicity` flag) always show their flag. No biographies are written yet; profiles show only sourced fields. `tools/build_saints.py` and `tests/test_saints.py` enforce these rules.
9. **Style.** Use the Oxford comma. Keep notes neutral and sourced. Do not contact outside sites (isidore.co, CCEL, and others) on the owner's behalf; draft only.
10. **Rights (v16).** Every Isidore Index record and every reading-room edition shows one of five badges: **Public domain (US)** (`public_domain_us`), **Open license** (`open_license`), **Permission granted** (`permission_granted`), **Link only** (`link_only`), or **Unknown** (`unknown`), with its evidence and checked date (tooltip and record-page line), linking to `#/rights`.
   - **Download, Files, Calibre-viewer, and reader buttons appear ONLY for the first three.** Link-only and unknown records link only to the record's isidore.co **book page** (`legacy/book/<id>/CalibreLibrary`), never to raw files (`get/…`, `CalibreLibrary/<folder>/`, or the viewer). If `data/rights.js` fails to load, every record counts as unknown. The open data follows the same rule (`download_urls` is `[]` and `isidore_files_url` is `null` unless hostable).
   - **Be conservative.** The research classification (`hosting-classification.csv`, 2026-10-25) is the starting point: L* codes are link only; H*/U* codes, including every "likely hostable" lead, are **unknown**. A lead is never public domain on its own. The only automatic `public_domain_us` records (code `P1`) are the same Project Gutenberg ebook as a hosted, rights-checked reading-room edition, without a modern publisher's ISBN. Anything else becomes hostable only through a `MANUAL` entry in `tools/build_rights.py` with written evidence (URL, quotation, or CCE volume and page), a checked date, and who checked it. When in doubt, unknown. The 1931 rule and the editorial-flag rules still apply on top of the badge.
   - **Host nothing new** because of a badge. The badge permits links; hosting a file is a separate, owner-approved step (rule 1 and the Gutenberg pattern above). Never bulk-download isidore.co files.
   - `/rights` and `/takedown` both say "This is not legal advice." The takedown agent contact is a visible **PLACEHOLDER** until the owner decides on DMCA agent registration (US Copyright Office directory, $6 per 3 years); never fill in a guessed name or email. `tests/test_rights.py` and `tests/rights.test.js` enforce these rules.

## How to add things

- **Connected timeline:** `scripts/timeline.js` joins authors and the existing saints guide, with by/about reading links and rights-gated read-here buttons. Keep historical flags and the undated group. See `docs/TIMELINE.md` and `tests/timeline.test.js`.

- **A reading-room work or edition:** follow `docs/CATALOG.md`. Edit `data/library.json` (with rights evidence in `data/sources/`, plus `data/texts/` and SHA-256 if hosted), then run `npm run build`.
- **An author or resource:** load, edit, and save with `tools/hubio.py` (`load()` and `save()`) so `catholic-hub.json` and `data.js` stay identical. Author ids are kebab-case slugs used in URLs.
- **An edition guide or reading list:** edit `tools/editions_data.py` or `tools/reading_lists.py`, then run `npm run build`. Never add a flagged title.
- **An editorial flag:** add the Isidore book id to `tools/build_editorial_flags.py` with a category (`antisemitic-content`, `polemical-historical`, `sedevacantist-position`, or `author-context`) and a factual note. Then run `python3 tools/build_editorial_flags.py`, `python3 tools/build_open_data.py`, and `python3 tools/build_static.py`.
- **A saint:** add the saint to `research/saints-pilot.json` (outside this repo) and rerun `python3 tools/import_saints_pilot.py --research <dir>`, or edit `data/saints.json` directly: every claim needs a `source_url`; tier 1 ids must equal a hub author id; tier 3 saints need a `historicity` flag. Then run `python3 tools/build_saints.py` (it validates, rebuilds the alias table, and fails on an ambiguous multi-word alias) and `python3 tools/build_static.py`. Search aliases: exact keys after NFKD, diacritic stripping, lowercasing, and dropping leading honorifics (Saint, St., Blessed, Pope); bare first names such as "John" are collisions shown as "Did you mean". Add a nickname (for example "Little Flower") to `HAND_ALIASES` in `tools/import_saints_pilot.py`.
- **A rights status:** add a hand-checked entry to `MANUAL` in `tools/build_rights.py`, rerun `python3 tools/build_rights.py --research <research dir>` (or without `--research` to keep the current classification), then `python3 tools/build_open_data.py` and `python3 tools/build_static.py`.
- **LibriVox audio:** run `python3 tools/fetch_librivox.py` (network) and review the matches.
- After any of these, run `python3 tools/build_static.py`.

## Before opening a PR

```sh
npm run build                         # library.js, guide.js, and saints.js must not change afterward
python3 tools/build_static.py         # static pages, sitemap, and robots must not change afterward
git diff --exit-code                  # nothing stale
npm test                              # node tests (incl. reader anchoring and shortcut guard) plus tests/test_*.py (editorial flags, v9 crawlability, catalog, analytics, saints)
node --check app.js && node --check scripts/saints.js && node --check scripts/analytics.js && node --check scripts/reader.js && node --check scripts/library.js && node --check scripts/guides.js && node --check scripts/search.js && node --check scripts/rights.js && node --check data/site-copy.js
```

Optional network checks: `python3 tools/check_links.py` (writes `docs/link-health.*`) and `python3 tools/check_library_links.py --output /tmp/source-links.json`. Then preview with `npm run dev` and check the home page (with JavaScript off too), an author page, `/policy/`, a flagged book (for example `#/isidore/book/3895`), and a reading-room work with a Listen button (highlight a passage, reload, and check My notes, Continue reading on the home page, and the print preview).

## Hosting limits (free GitHub only; checked 2026-10-25)

The site is served free by GitHub Pages from `main`; the reading-room texts also live in the separate `bibliotheca-texts` repo. Published site size on 2026-10-25: about 44 MB.

- **GitHub Pages:** published site at most 1 GB; source repo recommended at most 1 GB; soft bandwidth limit 100 GB per month; deployments time out after 10 minutes; soft limit of 10 builds per hour (https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).
- **Repository files:** warning above 50 MiB, blocked above 100 MiB (25 MiB through the browser); repos ideally under 1 GB, strongly recommended under 5 GB (https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
- **Releases:** up to 1,000 assets per release, each under 2 GiB; no limit on total release size or bandwidth (https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
- So the ~32 GB of isidore.co files cannot go on Pages or in a repo; Releases could hold permitted files one by one, but nothing is hosted until each file is rights-checked and the owner approves.
