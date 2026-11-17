# Design rules

The site should read as a calm reading library: few choices per screen, type doing the work, and portraits of the saints and authors as the visual interest. These rules apply to every page and to both themes. When a rule here and the existing code disagree, follow the code and record the mismatch (AGENTS.md rule 11). The owner approved this pass on November 12, 2026.

## Type

- **Serif for reading.** Everything a reader reads (titles, headings, descriptions, notes, rows, the hosted texts) is set in the existing serifs: `--display` (Cormorant Garamond) for headings and `--serif` (EB Garamond) for text. Sans-serif (`--sans`) is only for small controls: buttons, form fields, the toolbar, and the navigation.
- **Measure.** Running text sits at 60 to 70 characters a line (`max-width: 66ch` on prose). The reader's text column is `26em`, measured at a median of 67 characters a line in EB Garamond at every text size; because it is in em, it holds when the reader changes the size.
- **Labels** (section labels, footer headings, filter labels) are serif small caps (`font-variant-caps: all-small-caps; letter-spacing: .06em`), not tracked uppercase sans. Status badges and rights chips are indicators, not labels: they stay small sans.
- **Numerals** in running text are old-style (`font-variant-numeric: oldstyle-nums`); tables and counters may use lining figures.
- **One type scale:** 14, 16, 18, 21, 26, 34, 48 px (`--t-xs` to `--t-3xl`). **One spacing scale:** 4, 8, 12, 16, 24, 32, 48, 64 px (`--s-1` to `--s-8`). No other sizes in new rules.
- No new fonts.

## Controls

Exactly three styles:

1. **Filled primary** (`.btn`): rubric fill. **At most one per screen.** It is the single thing the page wants you to do (for example "Read here", "Enter the reading room").
2. **Outlined secondary** (`.btn.ghost`): a hairline rubric border, no fill.
3. **Text link**: underlined serif or small sans, rubric. Use this for everything else, including rows of actions.

Gold buttons (`.btn.gold`) and pill buttons are retired, and so is the filled pill for the current section (it is underlined). Buttons have 6 px corners, not pills. Icon buttons (theme, menu) keep their square shape.

## Portraits

List thumbnails (home row, author and saint rows) are the self-hosted public-domain set in `assets/portraits/` (160 px WebP, `data/portraits.json` with checksums and credits, from `tools/fetch_portraits.py`), drawn at a fixed size with lazy loading; anything else shows a quiet initial. Person pages show the larger Wikimedia image with its credit line beneath.

## Home

Design refresh, owner's pick of November 17, 2026 ("Saints first", [design directions](research/design-directions-2026-11.md)); `home_hero()` and `home_paths()` in `tools/site_copy.py`, `styles/home.css`.
- **Hero:** a tinted band (`--bg2`, no border) with the label, "Tolle Lege", the translation, one filled button, and one text link; the Doré engraving fills the band's right side (cropped from the bottom so Dante and Beatrice stay in view) and sits above the title on phones. Its credit line is directly under the band. The hero title is the one size outside the type scale (`clamp(52px, 7vw, 84px)`).
- **Saints and authors:** the eight portraits (`HOME_PEOPLE`) are the main gallery, four across on desktop and two on phones, each with name, dates, and "Begin with" one hosted book by that person (`HOME_BEGIN`; `tools/build_static.py` checks it). Flagged titles are never featured.
- Then the three Explore rows, the one-line Today, About, and the newsletter. The 25-link budget before the footer still holds.

## Catalogue pages

Design refresh, owner's pick of November 17, 2026 ([design directions](research/design-directions-2026-11.md)): the reading room is the "Faceted catalogue" (v1) and the author index the "Printed shelf list" (v2).
- **Reading room** (`library()` in `scripts/library.js`, `styles/library.css`): a facet column beside the shelves. Find a work, Subject as radio buttons with counts (one choice, as before), Format, and Read on this site; the column is sticky on wide screens and sits above the results on phones. The shelves of rows, the six-per-shelf preview, and "See all" links are unchanged. The same `filter_use` events as before.
- **Author index and Doctors** (`authors()` in `app.js`, `styles.css`): one filter bar (Find, Era, Type, Order) with the count, a jump line of eras with counts, and names with dates in two columns under a small-caps era heading. No portraits or descriptions in the index; they stay on each author page. No pill chips.
- **Form fields** use the `--field` border (`#94805c` light, `#6b6f7c` dark), at least 3:1 against every background, and are 44 px tall.

## Reading pages

Design refresh, owner's pick of November 17, 2026: the "Margin contents" (v2) shown only at the start of each part, with the "Chapter strip" (v3) endings ([design directions](research/design-directions-2026-11.md)). `part_pages()` in `tools/build_static.py`, `styles/library.css`.
- **Contents at the start:** the book's title, author, and contents sit in a left column beside the opener, with the current part marked (`aria-current`) and "Chapter N of M" under them. They scroll away with the opener; nothing stays pinned while reading. On phones they fold into a closed "Contents" disclosure above the opener.
- **Measure and leading:** the text column stays 26em; static chapter pages use a line height of 1.65.
- **Continue reading:** each part but the last ends with the ornament, "End of …", and a block with "Next: N. Title" and the next part's first sentence, quoted from the hosted text (display only; underscores dropped), then the reading-room link.
- **End of the book:** the last part ends with three ornaments, "Finis", and a centered colophon of facts already in the records: the work, the edition and its release, length, checked date, the TXT file and its SHA-256, other formats, and the typefaces. Rights and quality notes stay in the Edition details (once per page).
- New blocks use only faces the page already loads: the quoted sentence is roman with CSS quotation marks and "Finis" is in small capitals, so no italic font file is fetched for them (an extra face cost 2 Lighthouse points).
- The Gutenberg sentence, the prev/next pager, and the Edition details stay after the text. The contents list no longer repeats after the pager. Print hides the contents and the Continue block.

## Licensing and credits

Design refresh, owner's pick of November 17, 2026: "Contents rail" ([design directions](research/design-directions-2026-11.md)); `licensing_html()` in `tools/rights_pages.py`, `styles/rights.css`. The page shows `LICENSING.md` word for word; only the layout changes.
- No panel border around the text. A sticky "On this page" list sits beside it on wide screens (Summary, the five numbered sections, then Rights & Permissions and Takedown requests) and becomes a two-column list above the text on phones.
- The list uses buttons that scroll to a section and move focus to its heading (`.lic-j` in `app.js`), not `#anchors`: the hash router would read an anchor as a route and count a page view.
- The summary table keeps its stacked, labelled rows on phones; its header is small sans over a dark rule, the Material column in semibold.

## Navigation and footer

Design refresh, owner's pick of November 17, 2026: "Masthead" ([design directions](research/design-directions-2026-11.md)); the header and footer markup in `index.html` are unchanged, and the rules are the last block of `styles/refresh.css`.
- **Masthead (1000 px and wider):** the search field on the left, the cross and the wordmark centered with "a library of libraries" in small capitals under it, Support and the theme button on the right. The header stays sticky at about its former height, because the reader, the author tabs, and the editions page measure it.
- **Sections:** one row on a hairline, in serif small capitals (18 px, `.06em`), centered. The current section is burgundy with a 2 px underline; no filled pill. Phones keep the search, theme, and menu buttons; the open menu is a list of full-width rows (48 px), the current section in burgundy.
- **Footer:** three columns (the project's name, description, newsletter line, and "About this independent project"; Read & explore; The project), serif links in `--ink2`, small-caps headings in `--gold-ink`, and one sans credit line.
- **Focus:** outlines use `--focus` (`#1f3a5f` light, `#e9c46a` dark), not gold, which was 2.78:1 on the light background.

## Containers

- A container has **a border or a tint, never both**, and no shadow.
- **No bordered card inside a bordered panel.**
- Prefer **rows separated by hairline dividers** to grids of cards. A list of works, editions, or links is a list of rows.

## Notices

- Each notice appears **once** on a page, at the **smallest legible size** (14 px), **nearest the thing it concerns**.
- Longer evidence (rights notes, checked dates, method, licence text) sits behind a `<details>` disclosure on the same page, or at the end of the text in the reader. It is never removed from the page source.
- Caveats that apply to the whole site ("listing is not endorsement", "files are served by the original library", "dates are distinct") live once on the policy or about page, not on primary surfaces.
- Required notices (the FTC affiliate line beside affiliate links, Project Gutenberg notices, Wikipedia and portrait credits, rights badges, editorial context notes on flagged titles) are never removed; they are made small and placed beside what they concern.
- Placement since the owner rule change of November 14, 2026 ([PROJECT-RULES](PROJECT-RULES.md) rules 2, 7, 10, and 11): the Gutenberg notice is the licence's own 1.E.1 sentence, verbatim, once per page after the text; quality labels only in the edition details; the affiliate line "Affiliate links: we may earn a commission. Details." once per page; rights badges only on a record's or edition's own page; the Wikipedia credit on one line; public-domain portrait credits behind a "Credits" toggle; the footer in two link columns with one line of credits.

## Editions

Designed editions (Part D; the Orthodoxy pilot, November 15, 2026) read as books. The parts below come from `PART_D` in `tools/build_text_pages.py` and `.edition-designed` in `styles/library.css`.
- **Paragraphs:** first-line indents of 1.5em and no space between paragraphs. The first paragraph after a heading is not indented and carries a drop cap. Verse, headings, and the title page keep their own spacing.
- **Chapter opener:** a small-caps "Chapter" label, a large burgundy numeral, the title, and one gold ornament (❦). On static chapter pages it replaces the page head and buttons above the text. In the reader the label and ornament are CSS, so the text still comes only from the TXT.
- **Chapter ending:** the ornament, "End of Chapter N", and a link to the next chapter (and, on chapter pages, to the reading room). On static chapter pages the link is a Continue reading block (see Reading pages).
- **Work page as a title page:** a facts line computed from the TXT (words and reading time at 230 words a minute), three choices (Read, Listen, Download), and "About this edition". Full source and rights stay behind the edition row's toggle.
- **Print:** each chapter starts a new page.
- **Covers:** design C, "Banded": a burgundy upper panel with the title in cream capitals and the category with its ornament, a gold rule, and a cream band with the author and the cross. Volumes and same-titled works carry a gold volume line. Every hosted edition has one (`tools/covers.py --build`; SVG source, WebP 480 by 720, social JPEG 1200 by 630, checksums in `data/covers.json`). Used beside the title on work pages, small in library rows and author lists, as the social image of a work's pages, first in print, and as the EPUB cover. The site's own `assets/og-image.png` stays for every other page.

## Accessibility

Visible focus on every control, keyboard access, and contrast of at least 4.5:1 for text in both themes. Fixed image dimensions so nothing jumps while loading.
