# Bibliotheca Catholica

[Open the library](https://bibliothecacatholica.com) · [Report a problem or correction](https://github.com/BibliothecaCatholica/bibliotheca-catholica/issues/new?template=site_problem.yml) · [Browse the source code](https://github.com/BibliothecaCatholica/bibliotheca-catholica)

Bibliotheca Catholica is a free Catholic **reading room and curated resource index**—a library of libraries. It helps readers find classic texts, compare editions, follow sourced links to original documents, and discover authors, saints, reference works, and media. Coverage is selective, not exhaustive; inclusion is not endorsement.

## What readers will find

- **Discover & Read** is the selected reading room: 102 individual work records, including 63 hosted reading editions. A *work* is the title; an *edition* is a particular translation, printing, or source copy. Some works have a text to read here; others point to an external text, scan, or bibliographic reference. The reader provides contents navigation, text search, display controls, saved place, notes, and source/download links.
- **Saints & Hagiography** has sourced profiles, a calendar, and the hagiography shelf at [/saints/](https://bibliothecacatholica.com/saints/).
- **Authors, Saints, Timeline, Editions & Translations, and Reading Lists** connect people, writings, editions, and paths through the collection. An author or saint page can point to a work without claiming that the work is hosted here.
- **Rites & Liturgy** ([/rites/](https://bibliothecacatholica.com/rites/)) offers sourced pages for 24 Churches sui iuris and seven Latin rites and uses, with an interactive map and visible source and uncertainty notes.
- **Seasonal reading plans** connect day-by-day readings to the hosted texts. [Advent with the Fathers 2026](https://bibliothecacatholica.com/reading/advent-2026/) has 26 daily readings, November 29 to December 24, all from hosted pre-1931 editions; reading progress is saved in the reader's browser.
- **The Isidore Index** is a separate discovery layer for the St. Isidore e-book library. It contains 6,633 imported catalog records. Those records have not each been reviewed; a listing is not a recommendation, a full-text copy, or confirmation that an outside file is available. Every record and every reading-room edition shows one of five rights badges (Public domain (US), Open license, Permission granted, Link only, or Unknown), explained at [/rights/](https://bibliothecacatholica.com/rights/). The site links to files only for the first three; otherwise it sends readers to the book's page at isidore.co. Rights holders can use [/takedown/](https://bibliothecacatholica.com/takedown/).
- **Related Christian Writers** includes C. S. Lewis, identified as Anglican. His eight title records link to external excerpts or previews; they are not hosted complete books. More generally, a title record does not promise a free online edition.
- **Digital Libraries, Scripture, Church Documents, Prayer, Reference Works, Podcasts & Media, Rare & Obscure, and Projects** are curated directories that help readers continue to original publishers and source libraries.

Search defaults to **Everything**. Readers can narrow it to the **Selected library** or the **Isidore Index**; the selected scope excludes the imported Isidore book records. Search and the on-site reader need JavaScript. The static pages and `/search/` directory still provide useful links if JavaScript does not run.

## What this repository contains

This repository is the source for the main website: its static app, catalog, reading texts, generators, tests, and documentation. It deploys as static files; there is no production database, login, or server-side search service.

The 63 hosted text editions are also published at [texts.bibliothecacatholica.com](https://texts.bibliothecacatholica.com) from the separate [bibliotheca-texts repository](https://github.com/BibliothecaCatholica/bibliotheca-texts). The main repository remains authoritative for the catalog, source evidence, reader, and export tool. The text repository is a checked copy for delivery, not a place to add unreviewed downloads.

| Path | Purpose |
|---|---|
| `index.html`, `app.js`, `scripts/`, `styles/` | Site shell, browser application, and presentation |
| `data/library.json` | Maintained reading-room work and edition records |
| `data/texts/`, `data/sources/` | Hosted text copies and source/provenance snapshots |
| `data/books.json`, `data/books.js`, `data/isidore-matches.json` | Imported Isidore catalog snapshots and curated matches; see the catalog and rights notes before changing them |
| `data/open/` | Generated JSON/CSV exports and their reuse terms |
| `tools/`, `tests/` | Data builders, static-page generation, validation, and regression checks |
| `docs/` | Catalog rules, editorial and rights details (`RIGHTS.md`), Rites & Liturgy (`RITES.md`), saints (`SAINTS.md`), SEO (`SEO.md`), reading guides and plans (`READING-GUIDES.md`), source reviews, and maintenance notes |
| `AGENTS.md` | Continuity guide: architecture, must-keep files, analytics privacy, and content rules for every contributor |

## Develop and validate

Python 3.10+ and Node 18+ are sufficient for the current site build; no npm package installation is required.

```sh
npm run dev      # serve at http://127.0.0.1:4173
npm run build    # validate and generate the browser data bundles
python3 tools/build_static.py  # refresh crawlable pages, sitemap, and build fingerprint
npm test         # run JavaScript and Python tests
git diff --check
```

Commit generated output after changing a template, route, application code, or source data. Re-run the builds and tests, then confirm `git diff --exit-code` is clean. CI (the "Validate library" workflow) runs the offline validation on every push and pull request, and GitHub Pages deploys `main`. Optional network checks are separate: they can be blocked or redirected and do not establish that a text is accurate, licensed, or the edition described.

## Updating the catalog

Start with [the catalog rules](docs/CATALOG.md) and [contributing guide](CONTRIBUTING.md). For an existing reading-room work, edit `data/library.json`; preserve stable IDs, cite the exact source edition, record translator/editor evidence and rights checks, and include the original file and checksum only when hosting is approved. Run `npm run build` and `python3 tools/build_static.py` so generated data and pages stay aligned.

Edition guides, reading lists, and Substack metadata are maintained in `tools/editions_data.py`, `tools/reading_lists.py`, and `tools/substacks_src.py`. `python3 tools/build_v3_data.py --catalog-only` regenerates the guides while preserving the existing feed snapshot. The full generator refreshes external feeds and is a separate editorial/network operation.

The open-data exporter is `python3 tools/build_open_data.py`. The text archive export is `python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts`; review its manifest and diff before publishing to the separate text repository.

Some older import scripts expect source material such as `metadata.db` or a historical `research/` directory that is not included in this checkout. Their presence does not make those inputs reproducible. Do not run legacy ingestion scripts over current data without first confirming their inputs and output paths.

## Editorial, rights, and licensing boundaries

- The site is an independent index and reading room, not the publisher or host of every linked work. Prefer primary sources and identify the edition readers will reach.
- Catalog records distinguish hosted reading editions, external full-text sources, and references. Never describe a reference or a scan link as a text hosted by this site.
- Hosted editions require edition-specific rights evidence and retain their original source notices. The pre-1931 rule is a project selection rule, not worldwide legal clearance. Unknown rights fail closed.
- Isidore catalog rows are imported and unreviewed as a whole; automated author associations can be imperfect. CatholicSaints.Info remains link-only; do not copy or crawl it.
- Current terms differ by material: code is MIT; open data and reading-catalog metadata are CC0; site writing is CC BY 4.0; hosted texts carry their source terms and no blanket license from this project. See [LICENSING.md](LICENSING.md) and the live [licensing note](https://bibliothecacatholica.com/licensing/).

For broken links, metadata corrections, search/reader problems, or accessibility reports, use the [site problem form](https://github.com/BibliothecaCatholica/bibliotheca-catholica/issues/new?template=site_problem.yml). Do not include private reader notes or credentials in public issues. See [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## License

This repository contains material under different terms; the root [MIT License](LICENSE) applies to code only. The full [licensing summary](LICENSING.md) explains the scope and exceptions. Do not infer a license for a text, image, dataset, or excerpt from its location in this repository.

### Reading and citation updates (November 9, 2026)

Search accepts Summa references such as `ST I q 2 a 3`. It checks the article page before showing its title. The initial Catechism lookup, `CCC 1324`, opens the Vatican section containing that paragraph. Verify an official destination before adding a Catechism mapping. The first explicit article cross-reference connects I, q. 2, a. 1 to I, q. 3, a. 4.

Hosted edition panels offer Search this book. Search results link to individual paragraphs. For mapped chapters and stories the reader uses the edition and block offsets from the generated text-pages bundle. Update the maintained mapping in tools/text_pages.py, regenerate the catalog and static pages, run both test suites, and commit generated output together. After Pages deploys, compare the live build.json ID with the repository and open a citation, a chapter, and a paragraph search result.

### Passage search and specialist references

The reader uses its existing paragraph and heading offsets to show a chapter, matched phrase, surrounding text, and a link to the paragraph. Search stays on the device. The desktop contents sidebar replaces the duplicate inline contents disclosure. Check a mapped chapter and an unmapped book, punctuation in a query, keyboard focus, and both color themes after reader changes.

Design references: [Noxidsoft’s historical dossier](https://github.com/noxidsoft/all-historical-evidence-of-jesus-christ) pairs source labels with excerpts. [Morals of the Church](https://moralsofthechurch.com/) combines full-text lookup with editorial topic indexes. [Readest](https://github.com/readest/readest) distinguishes book and shelf search. Bibliotheca uses original interface code and links the first two collections as independent resources. Maintain their directory records through tools/hubio.py and regenerate the browser data and static pages.

### Study desk integrations

The Study desk at /study/ provides Pagefind search across all hosted edition sections, Scripture reference parsing (including deuterocanonical books), Citation.js citation exports, and Mirador scan comparison for the Supplement's OCR flags. Every dependency version is pinned in package-lock.json. Run npm ci, npm run build, python3 tools/build_static.py, then npm run build:study and npm test. Commit the generated pagefind/ and assets/study/ together. The Pagefind index covers each edition once, avoiding duplicate chapter and Summa question/article results. Its reader metadata sends each result to its edition section.

The Roman-calendar snapshot at data/study/calendar.json comes from LiturgicalCalendarAPI, United States, English, civil years 2026 and 2027. Refresh it from the recorded source with year_type=CIVIL and review the returned jurisdiction and date coverage before replacing it. The homepage labels this jurisdiction. Other rites retain their separate existing data.

Mirador fetches IIIF images from iiif.archive.org only when the visitor opens the scan viewer. The original scan remains linked. Bible lookup opens BibleGateway's NRSV Catholic Edition. Citation.js emits the catalog's edition data and does not infer a publication date. Source dependency licenses are retained in assets/study/licenses. The index includes catalog-approved hosted texts only.

The shared footer is maintained in index.html. build_static.py also synchronizes it to the standalone Study desk. Reading links, project links, and policies have separate groups; credits and build information live in the expandable lower row.
