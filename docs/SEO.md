# SEO and discoverability (v17, 2026-10-26)

Bibliotheca Catholica (https://bibliothecacatholica.com) is a static site. Google sees the pre-rendered HTML that `tools/build_static.py` writes, so every rule below is applied there; `tests/test_seo.py` checks it.

## What each page carries

| Page type | Title | Description | H1 | JSON-LD | Visible extras |
|---|---|---|---|---|---|
| Home (`index.html`) | `HOME_TITLE` | `HOME_DESC` (150–160 chars) | "Bibliotheca Catholica" | WebSite, Organization | about text (about 300 words) and links to every section |
| Section index (`/authors/`, `/saints/`, …) | section name + site name | fitted, 120–160 chars | section name | BreadcrumbList | intro paragraph (`INTRO`) and breadcrumb |
| Author (`/author/<id>/`) | name + site name | fitted from the bio, era, and tags | author name | Person, BreadcrumbList | At a glance, More sources, breadcrumb |
| Work (`/work/<id>/`) | title + site name | fitted | work title | Book, BreadcrumbList | "By <author>", editions count, Rights link |
| Edition guide, reading list, saint | name + site name | fitted | name | BreadcrumbList | breadcrumb |
| About (`/about/`) | "About the library" + site name | fitted | "About the library" | BreadcrumbList | what is here, sources, rights, policy |

`fit(parts, extra)` builds a description from real data and adds only true, generic sentences (variants in `DESC_EXTRA`) until it is 150–160 characters; it never invents facts. Long text is cut at a word boundary.

## Rules

- One GA4 tag per page with `send_page_view: false` (unchanged).
- Nav and footer links are real paths. `app.js` intercepts them on the root page only.
- `sameAs`: GitHub and Bluesky only (verified). Add X, Substack, or others only after confirming the profile belongs to the project.
- No `SearchAction` (search is a hash route and Google retired the sitelinks search box), no FAQ, review, or rating schema, no hidden text, no keyword stuffing.
- Flagged titles never appear on the home page or in the sitemap; flagged book pages stay `noindex`.
- No `lastmod` until accurate dates are available.
- `google3b007babfa8923a4.html`, `.well-known/atproto-did`, `404.html`'s redirect, `robots.txt` rules, `/rights/`, and `/takedown/` are not part of SEO edits.

## Owner steps outside the repo

Search Console: URL inspection, then Request indexing for `/`, `/authors/`, `/author/thomas-aquinas/`, and `/work/confessions/`; confirm the sitemap shows about 729 discovered URLs. Bing Webmaster Tools: import from Search Console. Link the site from the project's own profiles. Branded results usually take several weeks to settle.
