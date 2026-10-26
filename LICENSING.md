# Licensing (draft)

Bibliotheca Catholica (bibliothecacatholica.com) contains several kinds of material, each under its own terms. This note is a draft summary, **not legal advice**. If anything here conflicts with a notice in a file or on a source page, that notice governs for that material.

| Material | Where | Terms |
|---|---|---|
| Code | HTML templates, `app.js`, `scripts/`, `styles*`, `tools/`, `tests/` | MIT License (`LICENSE`) |
| Open data | `data/open/`, and the reading catalog metadata in `data/library.json` | CC0 1.0 public domain dedication |
| Site writing | text written for this site | CC BY 4.0 |
| Hosted texts | `data/texts/` and texts.bibliothecacatholica.com | public domain in the US; no license from us; source notices apply |
| Wikipedia excerpts | the `extract` field in `data/catholic-hub.json` and `data/data.js` | CC BY-SA 4.0, not MIT and not CC0 |
| Portraits | images shown on author pages | the license on each image's file page |

## 1. Code

The HTML templates, JavaScript, CSS, Python tools, and tests in this repository are released under the [MIT License](LICENSE). Copyright (c) 2026 Bibliotheca Catholica contributors.

The MIT License covers code only. It does not cover the data files the code reads, the writing it displays, the hosted texts, or any third-party material described below, even where those files sit in the same folders.

## 2. Open data (CC0)

The datasets in `data/open/` are dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (`data/open/LICENSE.txt`). CC0 covers our compilation, normalization, and curation: our one-line summaries, notes, rights labels, matches, and Wikidata links.

The reading catalog metadata in `data/library.json` (work and edition records, contributor roles, rights labels, checked dates, notes, and checksums) is also dedicated to the public domain under CC0 1.0. It was checked on 2026-10-26 and contains no Wikipedia text. CC0 does not extend to the texts those records point to.

CC0 does not cover any third-party material described in section 5. In particular, the Wikipedia excerpts in `data/catholic-hub.json` and `data/data.js` are **not** CC0, and they are not included in `data/open/`.

## 3. Site writing (CC BY 4.0)

Text written for this site, such as the About page, section introductions, edition guides, reading-list notes, editorial context notes, and the rights and policy pages, is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please credit "Bibliotheca Catholica" with a link to https://bibliothecacatholica.com.

## 4. Hosted texts

The texts in `data/texts/` and at https://texts.bibliothecacatholica.com are editions checked as public domain in the United States. We claim no rights in them and add no license; there is no blanket license over them. Each Project Gutenberg file keeps its full Project Gutenberg License and credits, and those terms apply to the file as distributed. "Project Gutenberg" is a registered trademark of the Project Gutenberg Literary Archive Foundation. Outside the United States, check your local law.

## 5. Third-party material

- **Wikipedia.** Author excerpts are shortened from the English Wikipedia article named and linked on each author page, and are available under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). They are stored in the `extract` field of `data/catholic-hub.json` and `data/data.js`. They are carved out of the MIT License and of CC0, and are not part of the open data.
- **Wikimedia Commons and Wikipedia images.** Author portraits are shown only with a credit taken from the image's file page (author where named, license, and a link to the file page), recorded in `data/portrait-credits.json`. Each image stays under the license on its file page. Images marked non-free (fair use) are not shown.
- **Project Gutenberg.** Texts and catalog snapshots from Project Gutenberg follow the [Project Gutenberg License](https://www.gutenberg.org/policy/license.html) and terms of use.
- **Isidore Index.** The Index reproduces catalog information from the St. Isidore e-book library (isidore.co). Files listed there are held by isidore.co, not by this site; Bibliotheca Catholica does not host, and does not vouch for, any file at isidore.co.
- **Facts and links.** Names, titles, dates, ISBNs, and links are facts.

Questions or rights concerns: see https://bibliothecacatholica.com/rights/ and https://bibliothecacatholica.com/takedown/.
