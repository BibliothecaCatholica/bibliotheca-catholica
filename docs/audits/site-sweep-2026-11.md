# Site sweep, November 2026

Live-site link and accessibility sweep (Claude Code round 3, Job 4), run November 23, 2026 against https://bibliothecacatholica.com. The live `build.json` reported `bc-4357287ed2f9`, the same build as `main` at `e441e4e608`, so the built tree on `main` and the live site are the same pages.

## Summary

The site is in good shape. No broken internal links, every sitemap URL answers 200, and every page carries exactly one GA4 tag. Accessibility checks found two minor issues on 24 page types. No presentation fix was low-risk enough to make in this PR. The two findings and their proposed fixes are below.

| Check | Scope | Result |
|---|---|---|
| Internal links and assets (`href`/`src` starting with `/`) | 6,045 HTML files in the built tree | 0 broken targets |
| Images without `alt` | the same 6,045 files | 0 |
| Live status of every sitemap URL | 6,000 URLs, GET | 6,000 × 200, no redirects |
| GA4 tag on every live sitemap page | 6,000 pages | exactly one `gtag/js?id=G-HFG445Y1LT` on each |
| GA4 tag in the built tree | 6,002 pages | one on each, except `google3b007babfa8923a4.html` (the Search Console file, which must stay as it is) |
| Disclosure link (`/disclosure/`) | 6,002 pages | on every page except `404.html` (a redirect stub into the app, which shows the footer) and the Search Console file |
| "tax-deductible" anywhere in pages, data, or scripts | whole tree | absent; it appears only in the docs that forbid it |
| Bookshop affiliate ID `130222` on author pages | 480 author pages | absent |
| Amazon links | whole tree | 7, all generic Kindle help links on `/guides/epub-on-your-device/` (allowed) |
| `noindex` | whole tree | only `404.html`; `/drafts/` pages are kept out of the sitemap |
| Internet Archive items linked from pages | 90 distinct items | all public: none dark, lending-only, or missing (metadata API) |
| axe-core 4.10.2 (WCAG 2.0/2.1 A and AA, best practice) | 24 page types × desktop light, desktop dark, phone | 2 findings, below |
| Horizontal scroll on phone (iPhone 13) | the same 24 pages | none |

The 24 page types were the home page, Authors, an author page (G. K. Chesterton), a work page and a chapter page (Orthodoxy), Library, Reading, Study, Search, Support, Prayers, Doctors, Councils, Scripture, the EPUB guide, Credits, Disclosure, About, Timeline, Rights, a Summa article (`/summa/1-2/q111/a5/`), a saints calendar day (`/saints/calendar/02-06/`), a rite (`/rites/bulgarian/`), and an editions page (`/editions/bernanos/`). The dark theme was set through the site's own `hub-theme` setting and confirmed on each page (`data-theme="dark"`).

## Findings

1. **Author pages: heading order (axe `heading-order`, moderate).** The tab panels that `scripts/library.js` draws (`authorWorks()` and its neighbours) open with `<h3>` headings such as "Selected works & reading editions", directly under the page's `<h1>`. Screen-reader users who move by heading meet a skipped level on all 480 author pages.
   *Proposed fix:* make the panel headings `<h2>` in `scripts/library.js`, and change `styles.css` lines 450 and 451 (`.au-panel h3`, `.au-panel>h3:first-child`) to match, so the look stays the same. Not made here: it changes the app script and every author page's layout rules, so it needs a visual check on desktop and phone in both themes, which is more than a low-risk presentation fix.
2. **Study page: search box labelled only by `title` (axe `label-title-only`, serious, best practice).** Pagefind's default UI on `/study/` gives its input `title="Search"` and a placeholder but no `<label>` or `aria-label`. `/search/` passed, so the site's own search page is fine.
   *Proposed fix:* after `PagefindUI` mounts on `/study/`, set `aria-label="Search the library"` on `.pagefind-ui__search-input`, or pass Pagefind's own option for this if the pinned 1.6.0 has one. Not made here: `study/index.html` is maintained by hand and has its own theme test, so this belongs in a small PR of its own.

## Not checked

- **External links beyond 18 hosts.** This session's network policy blocks most outside hosts, so 190 of the 208 external hostnames could not be reached. That includes www.newadvent.org (4,156 links), www.wikidata.org, www.vatican.va, bookshop.org, and cnewa.org. These are not findings. A per-domain sample of up to 40 links per host returned 200 on archive.org, ccel.org, commons.wikimedia.org, en.wikipedia.org, isidore.co, texts.bibliothecacatholica.com, www.papalencyclicals.net, en.wikisource.org, gutenberg.net.au, and www.fadedpage.com. www.gutenberg.org answered 503 to all 40 sampled links, which was a Gutenberg outage or rate limit at the time (the same thing `tools/fetch_gutenberg_edition.py` reports as "gutenberg.org is down"). openlibrary.org answered with its "verify human" page. github.com refused the logged-out issue-form link (`issues/new?template=site_problem.yml`, in every footer); the template file exists in `.github/ISSUE_TEMPLATE/`. vulsearch.sourceforge.net (on `/scripture/`) answered 403 from its Cloudflare bot check.
- **Client-side links** that the app draws only after a search or click (for example, search results) were not crawled.

Unblocker for a full external check: repeat the external-link step from a machine or cloud environment whose network allows those hosts. Allowing them here is an environment settings change for Micah.
