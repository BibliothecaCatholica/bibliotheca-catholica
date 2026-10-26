# Bibliotheca Catholica

[Open the library](https://bibliothecacatholica.com) · [Report a problem or correction](https://github.com/BibliothecaCatholica/bibliotheca-catholica/issues/new?template=site_problem.yml) · [Browse the source code](https://github.com/BibliothecaCatholica/bibliotheca-catholica)

Bibliotheca Catholica is a free Catholic **reading room and curated resource index**—a library of libraries. It helps readers find classic texts, compare editions, follow sourced links to original documents, and discover authors, saints, reference works, and media. Coverage is selective, not exhaustive; inclusion is not endorsement.

## What readers will find

- **Discover & Read** is the selected reading room: 98 individual work records, including 56 hosted reading editions. A *work* is the title; an *edition* is a particular translation, printing, or source copy. Some works have a text to read here; others point to an external text, scan, or bibliographic reference. The reader provides contents navigation, text search, display controls, saved place, notes, and source/download links.
- **Authors, Saints, Timeline, Editions & Translations, and Reading Lists** connect people, writings, editions, and paths through the collection. An author or saint page can point to a work without claiming that the work is hosted here.
- **The Isidore Index** is a separate discovery layer for the St. Isidore e-book library. It contains 6,633 imported catalog records. Those records have not each been reviewed; a listing is not a recommendation, a full-text copy, or confirmation that an outside file is available. The site links to files only when its record meets the displayed rights rule; otherwise it sends readers to the book's page at isidore.co.
- **Related Christian Writers** includes C. S. Lewis as an Anglican voice. The eight Lewis records are bibliographic references, not eight hosted free books. More generally, a title record does not promise a free online edition.
- **Digital Libraries, Scripture, Church Documents, Prayer, Reference Works, Podcasts & Media, Rare & Obscure, and Projects** are curated directories that help readers continue to original publishers and source libraries.

Search defaults to **Everything**. Readers can narrow it to the **Selected library** or the **Isidore Index**; the selected scope excludes the imported Isidore book records. Search and the on-site reader need JavaScript. The static pages and `/search/` directory still provide useful links if JavaScript does not run.

## What this repository contains

This repository is the source for the main website: its static app, catalog, reading texts, generators, tests, and documentation. It deploys as static files; there is no production database, login, or server-side search service.

The 56 hosted text editions are also published at [texts.bibliothecacatholica.com](https://texts.bibliothecacatholica.com) from the separate [bibliotheca-texts repository](https://github.com/BibliothecaCatholica/bibliotheca-texts). The main repository remains authoritative for the catalog, source evidence, reader, and export tool. The text repository is a checked copy for delivery, not a place to add unreviewed downloads.

| Path | Purpose |
|---|---|
| `index.html`, `app.js`, `scripts/`, `styles/` | Site shell, browser application, and presentation |
| `data/library.json` | Maintained reading-room work and edition records |
| `data/texts/`, `data/sources/` | Hosted text copies and source/provenance snapshots |
| `data/books.json`, `data/books.js`, `data/isidore-matches.json` | Imported Isidore catalog snapshots and curated matches; see the catalog and rights notes before changing them |
| `data/open/` | Generated JSON/CSV exports and their reuse terms |
| `tools/`, `tests/` | Data builders, static-page generation, validation, and regression checks |
| `docs/` | Catalog rules, editorial and rights details, source reviews, and maintenance notes |

## Develop and validate

Python 3.10+ and Node 18+ are sufficient for the current site build; no npm package installation is required.

```sh
npm run dev      # serve at http://127.0.0.1:4173
npm run build    # validate and generate the browser data bundles
python3 tools/build_static.py  # refresh crawlable pages, sitemap, and build fingerprint
npm test         # run JavaScript and Python tests
git diff --check
```

Commit generated output after changing a template, route, application code, or source data. Re-run the builds and tests, then confirm `git diff --exit-code` is clean. CI runs the offline validation on pull requests. Optional network checks are separate: they can be blocked or redirected and do not establish that a text is accurate, licensed, or the edition described.

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
