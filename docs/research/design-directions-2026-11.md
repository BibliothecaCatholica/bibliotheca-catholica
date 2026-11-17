# Design directions, November 2026

Part 1 of the in-house design refresh: an audit of five areas, four working variations for each, and a recommendation per area. Nothing here changes the live pages. Micah picks a variation for each area (or a mix); Part 2 then builds the picks, one area per pull request, presentation only.

**Previews** (unlisted, `noindex,nofollow`, disallowed in `robots.txt`, out of the sitemap and nav): <https://bibliothecacatholica.com/design-preview/>. Each page has a bar at the top to switch between v1 to v4 and to try the dark theme. They are written by `tools/build_design_preview.py` (called at the end of `tools/build_static.py`) from the real data: `data/library.json`, `data/catholic-hub.json`, `data/portraits.json`, `data/covers.json`, `data/hero.json`, the home copy in `tools/site_copy.py`, the generated Orthodoxy chapter pages, and `LICENSING.md` through `tools/rights_pages.py`. `tests/test_design_preview.py` checks them. Delete the script, its call, the test, and `/design-preview/` together when the refresh is done.

Method: the live site and the templates were checked on November 17, 2026 at 1366 by 900 and 390 by 844 (Playwright, both themes), with contrast computed from the `:root` tokens. The patterns named below are described in our own words from public sites; no code or assets were copied.

## Ground rules every variation keeps

- The DESIGN.md tokens exactly as in `styles.css`: the parchment, burgundy (`--rubric`), and gold palette in both themes, the 14 to 48 px type scale, the 4 to 64 px spacing scale, Cormorant Garamond for display, EB Garamond for reading, Inter only for small controls. No new fonts or hosts.
- One filled button per screen at most; outlined and text links for the rest; 6 px corners; no shadows; a border or a tint, never both.
- Visible focus: the previews use a 2 px `--rubric` outline (7.96:1 on the light background; gold in dark), which fixes the audit's focus-contrast finding below.
- Motion only behind `prefers-reduced-motion: no-preference` (smooth scrolling); nothing animates otherwise.
- No new analytics, events, scripts, embeds, affiliate links, or Amazon links. Each page carries the one GA4 tag only, and with no `app.js` on these pages no page view is sent.
- Wording is the site's own. Where a variation adds a label (for example "The End", "Begin with", "Cite this edition"), it is noted below; anything that would state rights or credits in new words needs the owner's review before it ships (PROJECT-RULES rule 14).

## Audit summary

Contrast measured on the light background `#f6f0e2`: ink 13.9:1, muted 5.36:1, rubric 7.96:1, gold-ink 5.13:1, **gold 2.78:1**, line 1.3:1. Dark theme: all text pairs pass (rubric 6.6:1, muted 6.58:1).

Sitewide findings:

- **Focus ring below 3:1.** `:focus-visible` uses a 3 px `--gold` outline in `styles/library.css` and `styles/home.css`; gold on the light background is 2.78:1, under WCAG 1.4.11's 3:1 for focus indicators. Using `--rubric` (or `--gold-ink`, 5.13:1) fixes it.
- **Field borders are faint.** Inputs and selects use `--line` (1.3:1). A darker hairline (the previews' `--rule`, `#cdbb97`) makes fields findable without adding weight.
- **Off-scale sizes remain** in `styles/refresh.css` (9, 11, 12, 13, 19, 22, and 29 px) and in some controls (the brand subtitle is 9 px tracked capitals).
- Pages have no horizontal overflow at 390 px; images carry `alt`; landmarks and the skip link are present. The hidden "Interactive features could not start" H2 sits first in every page's heading outline (it is `hidden`, so screen readers skip it; harmless).

### a. Home page hero and Start here

- **Works:** the Doré engraving is a strong, appropriate image with a full credit; "Tolle Lege" with its translation is a good title; one filled button; the portrait row is the most inviting part of the page; the Start here list is short.
- **Generic or cluttered:** the left-text, right-image hero is the most common landing layout on the web; the "Bibliotheca Catholica" label above the title is set in tracked capitals (`.hero-c .eyebrow{letter-spacing:.32em}`), which DESIGN.md retires for labels; Start here gives title and author only, so a newcomer has no reason to choose one book over another; the Substack sign-up iframe renders as a large white box on the parchment page (and is blank until it loads).
- **Accessibility and mobile:** on phones the engraving pushes Start here below two full screens; the portrait row scrolls sideways with no visible cue.

### b. Library and author index

- **Works:** rows with small covers and hairline dividers; "Recently added" first; the subject filter and "Read on this site" checkbox are real controls; author rows with portraits and dates read well.
- **Generic or cluttered:** the reading room's filter bar mixes sizes (the Subject select is larger than Format); the author page shows 476 authors on one page (about 58,000 px tall on desktop, 59,000 on a phone) with no way to jump; the era and type filters are 33 pill chips in a tinted panel, which DESIGN.md's "pill buttons are retired" otherwise avoids; the breadcrumb says "Discover & Read" while the nav says "Reading Room".
- **Accessibility and mobile:** on phones the 33 chips wrap into a tall block before the first author; the active nav item is a filled burgundy pill, louder than anything else in the header.

### c. Reading pages

- **Works:** the designed-edition opener (Chapter label, burgundy numeral, title, ❦) and the drop cap; the measure is right (26em); the Gutenberg sentence sits once after the text; edition details stay behind a disclosure.
- **Generic or cluttered:** the whole site header (search, seven sections, Support) stays above the text, so the first screen is mostly chrome; there is no way to reach the contents or the next chapter until the end of the chapter; the end of chapter IX reads "End of Chapter IX" and "Continue in the reading room", the same as any chapter, so the book never says it has ended; the chapter list after the pager repeats the work page; line height is 1.8 (36 px at 20 px on a phone), so a phone screen holds few lines of text.
- **Accessibility and mobile:** prev/next is one outlined button row at the very end of the chapter, after the text, the ornament, and the Gutenberg sentence.

### d. Sources and credits (`/licensing/`)

- **Works:** every term is stated plainly with "not legal advice" in the first paragraph; the summary table is the right idea; Rights and Takedown are linked.
- **Generic or cluttered:** the H1 is "Licensing (draft)" while the nav, title, and footer say "Licensing & credits" and the label above says "Rights & Permissions" (three names for one page); the whole text sits in a bordered panel, and the table inside it adds more rules; inline `code` paths are louder than the prose around them.
- **Accessibility and mobile:** at 390 px the three-column table wraps into tall, narrow cells (the page is 6,100 px tall on a phone); the table already has `data-label` on each cell, so it can stack into labelled rows without markup changes.

### e. Navigation and footer

- **Works:** seven sections, everything else in the footer (the design budget); one search; the footer's two link columns and one credit line; "About this independent project" behind a disclosure.
- **Generic or cluttered:** sans-serif nav items with a filled pill for the current page read as an app, not a library; the phone menu is a grid of tinted tiles; the footer's "Read & explore" column is seventeen links in one list.
- **Accessibility and mobile:** the header is about 120 px tall on desktop before any content; the phone header packs three square icon buttons together.

## Patterns studied

Described in our own words, as ideas only:

- **Standard Ebooks:** a book's own colophon page (what the edition is, where it came from, how it was set); restrained covers in a grid; a plain, dense list view.
- **The Paris Review:** a centered masthead with serif section names; generous space between items; an issue's table of contents as a typographic list.
- **Folger Shakespeare digital texts:** a table of contents beside the text; line or paragraph numbers in the margin for citing.
- **Library of Congress and university digital libraries:** a facet column with counts beside results; an "On this page" list for long policy pages; rights statements given their own page.
- **Internet Archive book reader:** a strip or scrubber that shows where you are in the book and lets you jump.
- **Stripe Press:** facing-page compositions and a cover-led shelf.
- **Museum collection sites:** "highlights" galleries led by people or objects; a directory footer that lists every section with a line about it.
- **Printed books:** the title page, the running head, "The End" or "Finis", the printer's colophon, the back-of-book index, and the chronology with dates in a hanging column.

## a. Home page hero and Start here

| | Idea | Borrows | Fit with DESIGN.md |
|---|---|---|---|
| [v1 Title page](https://bibliothecacatholica.com/design-preview/home/v1/) | A centered title page (label, Tolle Lege, translation, ❦, one button), the engraving as a frontispiece below, Start here as a numbered contents list with leaders, small portraits, then About. | A printed title page and frontispiece; Standard Ebooks' quiet title pages. | Labels in serif small caps; one filled button; rows and a list, no cards; the engraving keeps its full credit. |
| [v2 Facing pages](https://bibliothecacatholica.com/design-preview/home/v2/) | An open-book spread: engraving on the left, title and the existing "About" sentence on the right; Start here as rows with covers and the catalogue descriptions; portraits and Explore side by side. | Stripe Press facing pages; museum object pages with image and text in balance. | Uses the design C covers already in `assets/covers/`; rows with hairlines; 20 links before the footer (budget 25; v1 has 20, v3 21, v4 23). |
| [v3 Editor's shelf](https://bibliothecacatholica.com/design-preview/home/v3/) | Type only above the fold with a facts line of counts (from the data); Start here as an annotated reading list; names as a two-column list; the engraving becomes a small vignette beside About. | The Paris Review's typographic contents; an editor's introduction to a reading list. | The fastest first screen (no image above the fold); counts come from `data/library.json`, `data/catholic-hub.json`, and the Isidore count already on the page. |
| [v4 Saints first](https://bibliothecacatholica.com/design-preview/home/v4/) | A tinted banner with the engraving cropped to the right; the eight portraits as the main gallery, each with "Begin with" and that person's first hosted book. | Museum "highlights" led by people. | Uses the portrait set as DESIGN.md intends ("portraits as the visual interest"); the crop shows only part of the engraving, which weakens the artwork. Adds the label "Begin with". |

**Recommendation: v2 (Facing pages)**, with v3's annotated Start here rows if Micah wants fewer images. v2 keeps the engraving whole and credited, gives Start here the descriptions a newcomer needs, and stays within the link budget. Separately, consider moving the Substack iframe off the home page or behind a text link (an embed placement change needs the owner's approval; it is not part of any variation).

## b. Library and author index

| | Idea | Borrows | Fit with DESIGN.md |
|---|---|---|---|
| [v1 Faceted catalogue](https://bibliothecacatholica.com/design-preview/library/v1/) | A sticky facet column (find, subject or era as radio buttons with counts, Read on this site) beside rows with small covers or portraits and a two-line description; a live result count. | Library of Congress and university catalogue facets. | Rows with hairlines; labels in small caps; radio buttons are native controls (keyboard by default); no pills. |
| [v2 Printed shelf list](https://bibliothecacatholica.com/design-preview/library/v2/) | Two-column lists grouped by subject or era, a jump line of groups with counts, one plain filter bar; title, author, and date only. | A printed catalogue; Standard Ebooks' compact list. | The lightest pages (no images); serif throughout; the author index shrinks from about 58,000 px to about 12,000 px for both lists together. |
| [v3 Cover shelf](https://bibliothecacatholica.com/design-preview/library/v3/) | The design C covers as a wall, link-only works as plain typographic spines; subject tabs as underlined serif text; authors as a portrait index. | Stripe Press and Standard Ebooks cover grids. | Breaks DESIGN.md's "rows rather than grids of cards" (the covers carry no card border, but it is a grid). Heaviest on phones (about 74,000 px). |
| [v4 Index and chronology](https://bibliothecacatholica.com/design-preview/library/v4/) | Works A to Z with a sticky letter bar; authors as a chronology with an era rail (ranges) and dates in a hanging column. | The back-of-book index; a printed chronology; museum timelines. | Rows; lining figures for dates (allowed in tables and counters); sticky elements are plain CSS. |

**Recommendation: v1 for the reading room and v4 for the author index.** The reading room's 186 works benefit from descriptions and covers (v1), while the 476 authors are best found by era and date (v4's rail and chronology), which also ends the 58,000 px page. Both keep the existing filter scopes and the "Read on this site" checkbox.

## c. Reading pages

All four use the same Orthodoxy text (the first six paragraphs of chapter II and the last two of chapter IX, from the generated chapter pages), the same opener, the Gutenberg 1.E.1 sentence once after the text, and the same "Edition details" disclosure. They differ in navigation, contents, and the end of the book.

| | Idea | Borrows | Fit with DESIGN.md |
|---|---|---|---|
| [v1 Running head](https://bibliothecacatholica.com/design-preview/reading/v1/) | A slim sticky running head (book · chapter, a Contents menu, ‹ ›); "Next: <chapter>" at each chapter end; a three-part pager; after chapter IX, "The End" and a centered colophon. | The printed running head; Standard Ebooks' colophon. | 26em measure kept; opener unchanged; the colophon gathers fields already on the work page (edition, release, rights string as recorded, checked date, SHA-256, EPUB). Adds "The End" and "Colophon". |
| [v2 Margin contents](https://bibliothecacatholica.com/design-preview/reading/v2/) | The contents in a sticky left margin with the current chapter marked and "Chapter II of 9"; on phones it folds into a disclosure above the text; the colophon is a ruled two-column list. | Folger's contents beside the text. | Uses the empty left margin on desktop; nothing added above the text on phones but one closed disclosure. |
| [v3 Chapter strip](https://bibliothecacatholica.com/design-preview/reading/v3/) | A row of chapter numerals under the opener (current underlined); a Continue reading block with the next chapter's number, title, and first sentence; "Finis" and a book-style colophon. | The Internet Archive reader's position strip; a magazine's "next in this issue". | The first sentence of the next chapter comes from its page; no new copy beyond "Continue reading" and "Finis". |
| [v4 Scholarly apparatus](https://bibliothecacatholica.com/design-preview/reading/v4/) | Paragraph numbers in the margin, each a link for citing; ← and → keys move between chapters; an edition record table and a "Cite this edition" line. | Folger line numbers; CCEL-style paragraph numbering; library citation tools. | The numbers are display only (the TXT and block ids are unchanged). The keyboard handler is a few lines and ignores form fields; the citation line is new wording built from the record. |

**Recommendation: v1 (Running head) with v3's Continue reading block at chapter ends.** It moves the contents and next chapter within one tap at all times, gives the book a real ending and colophon, and changes the least on phones. v2 is a strong alternative for desktop readers; v4's paragraph numbers could be added later as a reader option.

## d. Sources and credits

The page in question is `/licensing/` ("Licensing & credits"; no page is titled "Sources and credits"). Every variation shows the `LICENSING.md` text exactly as `/licensing/` renders it, including the "not legal advice" sentence and the Rights and Takedown links; only the layout changes.

| | Idea | Borrows | Fit with DESIGN.md |
|---|---|---|---|
| [v1 Copyright-page ledger](https://bibliothecacatholica.com/design-preview/sources/v1/) | One column at reading measure; the summary table becomes a ledger (material, terms, where); sections follow as plain prose; no panel. | A university press copyright page. | No border around prose; the ledger stacks cleanly on phones. |
| [v2 Contents rail](https://bibliothecacatholica.com/design-preview/sources/v2/) | A sticky "On this page" list (Summary, sections 1 to 5, Rights, Takedown) beside the text; the summary stays a table, without the panel border. | Library of Congress rights pages; long policy pages with a side contents. | Two columns on desktop, a two-column list of anchors on phones. |
| [v3 Credits by source](https://bibliothecacatholica.com/design-preview/sources/v3/) | The terms ledger, then the hosted editions counted by the source each record names (Project Gutenberg 110, Internet Archive 6, Project Gutenberg Australia 5, Faded Page 5, CCEL 1, Standard Ebooks 1), then images, then the full note in an open disclosure. | Film and museum image credits; Standard Ebooks colophons. | Adds new sentences about sources and portraits. Those are credit statements, so this one needs the owner's review of the wording before it ships. |
| [v4 Printed note](https://bibliothecacatholica.com/design-preview/sources/v4/) | A centered document with section numbers hung in the margin and a ❦ at the end; the table stacks into labelled rows on phones using its existing `data-label` attributes. | A printed note or preface. | Smallest change to the text and the cleanest phone table. |

**Recommendation: v1 (Copyright-page ledger)**, with v4's phone table and v2's rail if the page grows. It removes the panel, fixes the phone table, and adds no new wording. Separately, the H1 ("Licensing (draft)") and the label above it ("Rights & Permissions") could match the nav's "Licensing & credits"; that is a wording change in `LICENSING.md` and `tools/rights_pages.py`, outside a presentation-only PR.

## e. Navigation and footer

All four keep the seven sections, the one search, the Support link, both footer link groups (every link, including Affiliate disclosure, Rights, Takedown, and Licensing), the newsletter line, the credit line, and the "About this independent project" disclosure.

| | Idea | Borrows | Fit with DESIGN.md |
|---|---|---|---|
| [v1 Masthead](https://bibliothecacatholica.com/design-preview/nav/v1/) | A centered wordmark with the cross, the sections below in serif small capitals on a ruled line, the current one underlined; three-column footer. | The Paris Review masthead; newspaper section rules. | Serif labels in small caps (as DESIGN.md asks); search becomes a text link to `/search/` on this variation, so the header search field (and its "/" shortcut) would need a home. |
| [v2 Quiet bar](https://bibliothecacatholica.com/design-preview/nav/v2/) | One 64 px row: brand, sections, search field, Support; the current section underlined in burgundy instead of a filled pill; a centered colophon footer with ❦. | Standard Ebooks' header; Stripe Press's restraint. | Keeps the search field; cuts the header from about 120 px to 64 px; footer columns become two short multi-column lists. |
| [v3 Two tiers](https://bibliothecacatholica.com/design-preview/nav/v3/) | The seven sections plus a tinted second row of links within the current section (here, Reading Room); the footer groups its seventeen links into Read, Explore, and Elsewhere, then The project. | Folger and Library of Congress section navigation. | Adds a row per section, which needs a list of sub-links for each of the seven sections (new navigation decisions). |
| [v4 Library directory](https://bibliothecacatholica.com/design-preview/nav/v4/) | A quiet bar in serif type; on phones the menu lists each section with its one-line description from `SECTION_LINKS`; the footer becomes a directory of every section with its description. | Museum directory footers; a library floor guide. | Reuses existing descriptions from `tools/site_copy.py`; the footer is longer but answers "what is here" at the bottom of every page. |

**Recommendation: v2 (Quiet bar) for the header, with v3's grouped footer.** It keeps the search field and its shortcut, removes the filled pill, halves the header height, and turns the seventeen-link column into three short groups. v4's described phone menu is worth adopting with it.

## Instruction files and the code

Mismatches found during the audit (the code was followed; nothing was changed to resolve them in this PR):

1. DESIGN.md retires pill buttons, but the author page's era and type filters are `.chip` elements with `border-radius:999px` (`styles.css`).
2. DESIGN.md sets labels in serif small caps at `.06em`, but the home hero's label uses `letter-spacing:.32em` (`.hero-c .eyebrow`), and the brand subtitle is 9 px with `.16em` tracking (`styles/refresh.css`).
3. DESIGN.md allows only the 14 to 48 px type scale in new rules; `styles/refresh.css` still uses 9, 11, 12, 13, 19, 22, and 29 px.
4. DESIGN.md asks for visible focus and 4.5:1 text contrast; the gold focus outline is 2.78:1 against the light background (under the 3:1 non-text minimum).
5. The task's standing rules say "No Amazon links"; OPERATIONS.md keeps a documented exception, and `guides/epub-on-your-device/` links Amazon's Send to Kindle and Kindle help pages. The previews add none.
6. The task refers to a "Sources and credits" page and prompt; the site's page is `/licensing/` ("Licensing & credits", H1 "Licensing (draft)"), and no Sources and credits prompt is in the repository.
7. The no-em-dash rule for site copy is not yet met in generated resource rows (`tools/build_static.py` joins name and description with " — "); the cleanup is already parked in HOLDS.md ("Audit leftovers").
8. The task says the FTC disclosure "stays sitewide"; the code (PROJECT-RULES rule 7) shows the one-line disclosure once per page beside affiliate links and links "Affiliate disclosure" in every footer. The previews carry no affiliate links and keep the footer link.

## Next step

Micah picks one variation per area (or names a mix, for example "home v2 with v3's Start here"). Part 2 then builds one area per PR: CSS and templates only, DESIGN.md updated to match, before and after screenshots at desktop and phone width, Lighthouse performance and accessibility not lower than today, merged on green CI. A final small PR deletes `/design-preview/` and its script and test.
