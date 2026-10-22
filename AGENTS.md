# AGENTS.md: continuity guide for Bibliotheca Catholica

Read this before changing the site. It applies to every contributor and coding agent (Codex, ChatGPT, Grok Bot, and others). Owner: Micah Watson, micahwatson@bibliothecacatholica.com. Live site: https://bibliothecacatholica.com (GitHub Pages from `main`).

## Architecture

- **Static single-page app.** Vanilla HTML, CSS, and JavaScript: `index.html`, `app.js` (router and most views), `scripts/library.js` (reading room, work pages, LibriVox buttons), `scripts/guides.js` (edition guides and reading paths), `scripts/search.js`, `styles.css` plus `styles/`. Routes are hashes (`#/author/<id>`, `#/work/<id>`, `#/read/<work>/<edition>`, `#/editions/<id>`, `#/reading/<id>`, `#/isidore/book/<n>`, `#/policy`).
- **Data lives in files, not a server.** `data/catholic-hub.json` = `data/data.js` (authors, resources, eras), `data/library.json` → `data/library.js` (selected works and editions), `data/guide.js` (edition guides and reading lists, built from `tools/editions_data.py` and `tools/reading_lists.py`), `data/reading-options.json/.js` (EPUB options), `data/isidore-matches.*`, `data/librivox.*`, `data/editorial-flags.*`, and `data/books.js` (the 6,633-record Isidore Index, lazy-loaded, about 1.2 MB). Each `.js` file is a generated copy of its `.json`; never edit only one of them.
- **No build step to serve.** The one generator that must be rerun is `python3 tools/build_static.py`. It pre-renders about 630 static entry pages (`author/`, `work/`, `editions/`, `reading/`, sections, `policy/`) from `index.html`, and it writes `sitemap.xml`, `robots.txt`, and `404.html`. **Rerun it whenever you change `index.html` (header, footer, script tags, meta), routes, authors, works, edition guides, reading lists, or editorial flags, and commit the output.** CI fails if the output is stale.
- When you bump the `?v=` cache-busting query on script tags in `index.html`, keep `data/data.js` as a script tag: `build_static.py` inserts `window.BC_BOOT` right before it.

## Files that must never be deleted or moved

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
npm test                              # node tests plus tests/test_*.py (editorial flags, v9 crawlability, catalog)
node --check app.js && node --check scripts/library.js && node --check scripts/guides.js && node --check scripts/search.js
```

Optional network checks: `python3 tools/check_links.py` (writes `docs/link-health.*`) and `python3 tools/check_library_links.py --output /tmp/source-links.json`. Then preview with `npm run dev` and check the home page, an author page, `/policy/`, a flagged book (for example `#/isidore/book/3895`), and a reading-room work with a Listen button.
