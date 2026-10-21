# Catalog and reading editions

`data/library.json` is the maintained source; `python3 tools/build_library.py` validates it and emits `data/library.js`. Both are committed so the site can still deploy as plain static files. There are no API keys, production server, database, or runtime package dependencies.

Each **work** has an identity, author, subject, tradition, optional work date, and review status. Each **edition** has its own identity, language, credited contributor roles, source URL, access type, rights statement, and check date. A hosted **copy** additionally has a local text path and SHA-256 checksum. Unknown publication/translation dates and contributor roles are left unspecified. A Gutenberg digital-release date is not the work's composition date.

## Sources checked for this release (2026-10-21)

- Project Gutenberg's catalog pages and complete UTF-8 texts: 25 identified editions, 22 hosted. Two (#50040, Doyle’s 1948 Rule; #18269, the 1958 Pensées with T. S. Eliot’s 1931 introduction) link out because they postdate the pre-1931 hosting rule. Catalog metadata snapshots are in `data/sources/`. Original text files, including credits and the full Gutenberg license, are in `data/texts/`. No Gutenberg generated book summaries were imported.
- Eight individual patristic texts/collections at New Advent. Those editions remain external, with their translation and editorial credits at source.
- Eight individual Vatican documents: the four Vatican II constitutions, *Fides et Ratio*, *Veritatis Splendor*, *Deus Caritas Est*, and *Rerum Novarum*. These link to official English texts; they are not copied or framed.
- [C. S. Lewis College](https://www.cslewiscollege.org/c-s-lewis/) establishes Lewis's Anglican identity. [Dallas Baptist University's bibliography](https://www.dbu.edu/mitchell/c-s-lewis-resources/bibliography.html) identifies the eight works and original publication dates. These are explicitly bibliographic references, not free reading editions.
- [USCCB lectionary FAQ](https://www.usccb.org/faq/questions-about-lectionary) supports the correction distinguishing the NABRE study Bible from the U.S. Mass lectionary based on the NAB.

`docs/source-link-check.json` records GET results, returned titles, redirects, and response hashes for the 42 distinct catalog URLs. All returned HTTP 200 at this check. This is access evidence, not a guarantee of future availability or a theological review. The checked source titles were compared with the listed works.

## Corrections and boundaries

- Gutenberg 8120 is Teresa's **Life**, not **Interior Castle**.
- Gutenberg 70790 is **Charles Coppens's adapted retreat edition** of Ignatian exercises, not an unqualified critical text of the original.
- Gutenberg 50040 credits **Leonard J. Doyle**, not Gasquet.
- Gutenberg 204 is **The Innocence of Father Brown**, not the complete Father Brown stories.
- Gutenberg 63084 contains **Saint Francis**, not Chesterton's combined Francis/Aquinas volume; 8442 contains **Europe and the Faith**, not *The Path to Rome*.
- Gutenberg 5657 carries a copyright notice and remains external. The source's U.S. public-domain designation was required before adding any hosted edition; it is not represented as worldwide clearance.
- Existing guide links to covered editions now show the actual work title and its local edition page, making differences from a recommended print edition visible.
- The claim that *The Everlasting Man* “baptised” Lewis's imagination was removed; that phrase concerns MacDonald's *Phantastes*. No substitute quotation was added.

The 6,633-book Isidore import is preserved separately and is **unreviewed**, including its automatic author associations. “Selected library” search includes the site's existing author/resource/guide selections plus the new catalog, but excludes imported books and folders. Older selections have not all received a fresh bibliographic audit. Search scopes are encoded in the URL.

## Adding a reading edition

1. Identify the exact work and edition at its source. Credit translators, editors, or adapters only with evidence. Keep abridgments, adaptations, and partial collections explicit.
2. Record the catalog metadata and rights evidence in `data/sources/`. Add an edition with `access: "full-text"` or `"reference"`; reference links must not imply a readable text.
3. Only host a text whose edition rights have been checked. Keep the complete original notices and credits; save the source bytes in `data/texts/` and record their SHA-256. Other files remain source links. The current validator supports only the checked Gutenberg public-domain ingestion path; a new source needs its own rights validation before hosting.
4. Run `npm run build` and `npm test`. Optionally run `python3 tools/check_library_links.py --output /tmp/source-links.json` and inspect returned titles/redirects. That checker never changes catalog records.

The reading interface renders escaped plain text, not third-party HTML or iframes. It loads one edition on demand, offers full-text paragraph search, source heading links when recognizable, section navigation, local reading-position persistence, typography settings, and original-source/download fallbacks. Sections are navigation chunks, not scholarly chapter or paragraph numbers. Scans, footnote formatting, images, and modern scholarly apparatus are best consulted at source. No account or tracking service was added.

## Follow-up editorial work

This release establishes the model rather than claiming a complete scholarly catalog. Expand the reviewed collections by topic, give each edition a human editorial pass, add exact translation/publication dates when established, and audit the older guide's remaining outbound links and attributions. PDF/EPUB rendering and account-synchronized annotations are not part of this release.

## Reading room and Isidore downloads

The reading room is the primary way to read. EPUB and PDF files in the St. Isidore e-book library are the alternate path. `python3 tools/match_isidore.py` writes `data/isidore-matches.json` and `.js` from `library.json` and `books.json`, with no network access. A work and an Isidore book match only when:
- the title is the same (ignoring a leading article, "Saint"/"St.", and "Holy"), or the Isidore title adds only a tail naming the author, or extends a title of three or more words;
- an author name token also matches;
- the book has an EPUB or PDF file.

Commentaries, guides, selections, and numbered volumes are excluded, and Anglican (Lewis) reference records are never matched. Matched works show **Other formats** on their work page. Matched Isidore books whose work has a hosted reading edition show **Read online here**. Review the printout whenever the catalog changes; translations may differ between the two paths.
