# Bibliotheca Catholica

A clean, searchable master index of Catholic authors, Scripture, the Magisterium, prayers, references, podcasts, and the great digital libraries. A selected collection can be read on the site; the wider index links to its original sources.

## Reading and discovery

- **Discover & Read** `#/library`: 49 individual work records, including 22 hosted reading editions, eight Lewis titles, eight patristic writings/collections, and eight official Church documents.
- **Reader** `#/read/<work>/<edition>`: text size, spacing, dark mode, source-heading navigation, full-text search, saved section, citation, and download/source links.
- **Related Christian writers** `#/related`: C. S. Lewis, explicitly identified as Anglican.
- Search defaults to the selected library. The full imported Isidore catalog remains available through its own scope and the Everything scope.
- Read [catalog provenance and editorial boundaries](docs/CATALOG.md) before adding new editions.

### Develop and validate

Python 3.10+ and Node 18+ are sufficient; no npm install is required.

```sh
npm run dev      # http://127.0.0.1:4173
npm run build    # deterministic catalog validation and browser bundle
npm test        # search isolation, metadata integrity, rights, and checksums
python3 tools/build_open_data.py
```

Optional external availability check: `python3 tools/check_library_links.py --output /tmp/source-links.json`. Network checks are separate from deterministic CI tests.

Deploy the repository's static files as before. Preserve `data/texts/`, `data/sources/`, the new `scripts/` and `styles/` directories. No hosting migration or server-side secret is needed.

### Legacy generator inputs

The committed data snapshots remain usable. Some older ingestion scripts expect the original `metadata.db`, `research/`, author research files, or a historical `site/data/` layout that is not present in this checkout. They are not a reproducible full rebuild and should not be run over current data without restoring their inputs. The new library build and the open-data exporter resolve paths from this repository and work independently of those missing sources.

## Editions, reading lists, Substacks, and buy links (v3)

* **Which Edition?** `#/editions`, **Reading Lists** `#/reading`, **Top Catholic Substacks** `#/substacks`.
* Content lives in `tools/editions_data.py`, `tools/reading_lists.py`, and `tools/substacks_src.py`. Run
  `python3 tools/build_v3_data.py` to rebuild `data/guide.js` (this also refreshes the Substack "latest posts" snapshot).
* **Affiliate IDs:** paste them into `data/affiliates.js` (`bookshopId`, and `wrap`/`param` per publisher). While they are
  empty, every Buy link works as a plain link.

## Prayers, Doctors' free texts, Rare & Obscure, and Projects (v4)

* **Prayers & Devotions** `#/prayers`: public-domain prayer texts live in `data/prayers.js`; the links come from the resources data.
* **Read free** panels on every Doctor's page come from `data/doctors.js`. **Rare & Obscure** `#/rare` uses `data/rare.js`, and **Projects & Translations** `#/projects` uses `data/projects.js`.
  All three are built from the research files by `tools/build_v4_data.py`. Every one of these texts is an outbound link; none is hosted here.

## The Isidore Index and Open Data (v5)

- The Isidore Index (`#/isidore`) is now the flagship. All 6,633 isidore.co books can be filtered by era, language (22 canonical), format, and subject, and each book has its own page with direct downloads from isidore.co.
- Open Data (`#/data`, `/data/open/`) offers the index, curated authors (with verified Wikidata QIDs), editions, Doctors' free texts, rare works, and projects as JSON and CSV under CC0.
- Hygiene: a junk folder was removed, language codes were normalized, the aquinas.cc link was confirmed, and LibriVox was added.

## Tabbed author profiles (v6)

- Each author page keeps the name, dates, portrait, blurb, feast day, and key links on top, with tabs for **Works**, **Commentaries**, **Buy the Books**, and **Related**. Every tab has its own link (e.g. `#/author/chesterton/works`), shows a count, and the site remembers the last tab you opened.
- Commentaries include the featured Chesterton column, curated Substacks and podcasts, studies by other authors in the library, and encyclopedia articles. Want to contribute one? Write to micahwatson@bibliothecacatholica.com.

## Reading options and design refresh

The navigation guide is now **Editions & Translations** (`#/editions`, existing links preserved). Additional EPUB options live in `data/reading-options.json` and its browser snapshot. See [the refresh notes](docs/READING-DESIGN-REFRESH.md) for source checks, UI changes, and validation.
