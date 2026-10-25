# Bibliotheca Catholica open data

Version: v6 (2026-10-25). License: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), public domain dedication. You do not have to give credit, but a link to https://bibliothecacatholica.com is appreciated.

Each dataset ships as both `.json` and `.csv`.

**The JSON files** are objects with these keys:
- `name`
- `description`
- `license`
- `generated`
- `count`
- `fields`, which documents every column
- `records`

**The CSV files** have one row per record. List values are joined with `; `.

`manifest.json` lists every dataset with its record count and field descriptions.

| Dataset | Records | What it is |
|---|---|---|
| `isidore-index` | 6,633 | Every book in the St. Isidore (isidore.co) Calibre library: authors, catalog year, normalized language, author era, formats, subjects, series, publisher, a **rights status** (`rights_status`, `rights_evidence`, `rights_checked`), and deep links (book page always; files folder and per-format downloads only for records whose rights status allows it), plus `editorial_flag` and `context_note` for the 54 records that carry an editorial context note (see the Fidelity & Editorial Policy, https://bibliothecacatholica.com/policy/). Listing is not endorsement. |
| `isidore-folders` | 3,352 | Every author folder in isidore.co's CalibreLibrary, linked to a curated author where the match is confident. |
| `authors` | 476 | Curated Catholic authors in 12 eras: dates, roles, our one-line summary, **Wikidata QIDs** (450 people, plus 5 work items for anonymous authors), and cross-links. |
| `editions` | 111 | The "Which edition?" guide: recommended translations and editions of 69 classics, with ISBNs checked against Open Library. |
| `doctors-free-texts` | 270 | The 38 Doctors of the Church and their key works. There are 248 free full-text links, each with a per-edition rights status, plus rows for works with no free text. |
| `rare-works` | 122 | Rare & Obscure: forgotten Catholic works in digital archives, grouped by theme. Modern unlicensed translations are linked to their item pages only. |
| `projects` | 73 | Catholic digital projects and translations, labeled human, AI-assisted, or unclear. Flagged entries are excluded. |

## How it was made, and the caveats

**isidore-index**
- **Source.** The data comes from the public Calibre metadata of isidore.co, snapshot 2026-10-21. Bibliotheca Catholica hosts **no book files**. Every download URL points to isidore.co.
- **Rights status (v6).** `rights_status` is one of `public_domain_us`, `open_license`, `permission_granted`, `link_only`, or `unknown` (explained at https://bibliothecacatholica.com/rights/). `rights_evidence` says why, and `rights_checked` gives the date (YYYY-MM-DD). `isidore_files_url` and `download_urls` are filled in **only** for the first three statuses; for `link_only` and `unknown` records use `isidore_book_url`, the record's book page. The statuses come from a 2026-10-25 research classification by publication year, ISBN, publisher, and an automated copyright-renewal match. "Likely hostable" leads (a pre-1931 catalog year, a Project Gutenberg source, or no renewal found) are recorded as `unknown` until a person checks the title page and the evidence: catalog years are often scan or reprint dates. The only records marked `public_domain_us` automatically are the same Project Gutenberg texts our reading room hosts after a rights check. This is a research aid, **not legal advice**, and public domain in the US may not be public domain in your country.
- **Catalog year.** `catalog_year` is Calibre's pubdate. It is often a scan or reprint date, so **do not use it to judge copyright**.
- **Languages.** The 87 raw language strings, over 26 codes, were normalized to 22 canonical languages, de-duplicated per book. Two merges and one fix were made:
  - Mis-tagged `enq` became English.
  - `nob` was merged into `nor`, and `och` into `zho`.
  - `frm` and `fro` were combined as "Old & Middle French".
- **Era.** `era` comes from the author's curated page. If there is none, it is inferred from life dates in the catalog author name; `era_source` tells you which. It is blank when neither is known.

**Author matching** between the catalog and the curated authors uses only confident rules:
- the site's own isidore folder links;
- an exact name match;
- an exact match on surname plus forename, with no conflicting life dates and only one candidate;
- an exact match on birth and death years plus a shared name token;
- one hand-verified alias, Billuart = "Carolus Renatus".

**Wikidata QIDs** come from each author's English Wikipedia article (`pageprops.wikibase_item`). Each was confirmed on Wikidata by checking that the item's enwiki sitelink is that same article. Authors without an article have no QID, and no QIDs were guessed.

**What CC0 covers.** CC0 applies to our compilation, normalization, and curation: summaries, notes, rights labels, matches, and QID links. We include **no Wikipedia text**, which is CC BY-SA. Titles, names, and links are facts. Texts reached through the links keep their own rights.

**Rights labels** in `doctors-free-texts` and `rare-works` follow a simple US rule: public domain if published before 1931, judged by the specific edition linked. They are research aids, not legal advice.

## Changelog

- **v6 (2026-10-25):** `isidore-index` gains `rights_status`, `rights_evidence`, and `rights_checked`; file links are given only for public-domain, openly licensed, or permitted records.
- **v5 (2026-10-21):** first documented release.
