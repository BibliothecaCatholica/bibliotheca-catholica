# Catalog and reading editions

## Document archive (October 22, 2026)

The 56 hosted TXT editions are also published at `https://texts.bibliothecacatholica.com/texts/` from `BibliothecaCatholica/bibliotheca-texts`. `textArchive` in `data/library.json` controls the reader's preferred host. Original local paths, hashes, and source records remain authoritative; the reader falls back to local files on archive failure. Export with `python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts`. The export preserves original bytes and includes provenance, a searchable directory, and a manifest. See `docs/PROJECT-REVIEW-2026-10-22.md` for the full assessment.

`data/library.json` is the maintained source; `python3 tools/build_library.py` validates it and emits `data/library.js`. Both are committed so the site can still deploy as plain static files. There are no API keys, production server, database, or runtime package dependencies.

Each **work** has an identity, author, subject, tradition, optional work date, and review status. Each **edition** has its own identity, language, credited contributor roles, source URL, access type, rights statement, and check date. A hosted **copy** additionally has a local text path and SHA-256 checksum. Unknown publication/translation dates and contributor roles are left unspecified. A Gutenberg digital-release date is not the work's composition date.

## Saints and hagiography books (2026-10-25, v14)

Source: Bibliotheca Research's verified list (35 records, `saints-books-verified.json`, checked 2026-10-25). Each Gutenberg imprint below was re-read from the downloaded PG file; every Internet Archive item was re-checked through its `/metadata` record (publisher, date, and no lending restriction).

**Hosted (14 Project Gutenberg editions, `"added": "2026-10-25"`):**
- Alban Butler, *The Lives of the Saints*: January–March (Kenedy, imprimatur 1895, #20450) and July (Kenedy 1908, #49604).
- Sabine Baring-Gould (Anglican), *The Lives of the Saints*: January, February, and March (Nimmo, MDCCCXCVII, #46947, #45604, and #48395), and *Virgin Saints and Martyrs* (Crowell 1901, #53841).
- Anna Jameson, *Sacred and Legendary Art*, vol. 1 (6th ed., Longmans 1870, #69581; vol. 2 links to an Internet Archive scan) and *Legends of the Madonna* (Houghton, Mifflin 1881, #12047).
- William Canton, *A Child's Book of Saints* (Dent 1906, first published 1898, #22112).
- Paul Sabatier (Protestant), *Life of St. Francis of Assisi* (tr. Houghton, Hodder & Stoughton 1919, ©1894, #18787).
- Candide Chalippe, *The Life and Legends of Saint Francis of Assisi* (Duerk's Jubilee Edition, imprimatur 1917, #6367).
- Aubrey de Vere, *The Legends of Saint Patrick* (Cassell 1892, #7165).
- James O'Leary (ed.), *The Most Ancient Lives of Saint Patrick* (5th ed., Kenedy 1880, #18482).
- Nicholas Wiseman, *Fabiola* (Benziger 1886, ©1885, #62254), labeled as fiction (a historical novel) in its description.

**Link-only (16 works; scans or texts at their source, not hosted):** Butler's 1812 London edition (8 volumes on the Internet Archive), further volumes of Baring-Gould's 1897 edition (5 volumes), Jameson's *Legends of the Monastic Orders* (1863), *The Golden Legend* (Ellis's Temple Classics edition, 1900, at Fordham plus 6 IA volumes), *The Roman Martyrology* (Baltimore 1897), the Ramsgate *Book of Saints* (1st ed., 1921 only), Dunbar's *Dictionary of Saintly Women* (1904–1905), Shea's *Pictorial Lives of the Saints* (1887), Delehaye's *Legends of the Saints* (tr. Crawford, 1907), Alger's *Little Flowers of Saint Francis* (1887), Thorold's *Dialogue* of Catherine of Siena (1896 complete and 1907 abridged), O'Kennedy's *The Holy Angels* (1887), Goodier's *The Crown of Sorrow* (1918; 1927 impression), Nepveu's *Meditations for Every Day in the Month* (1911), Yorke's *The Mass* (1921), and *The New Catholic Dictionary* (1929).

**Resource link fixes:** "Butler's Lives of the Saints (CCEL)" pointed to CCEL's page for Joseph Butler (the Anglican bishop), and `/ccel/butler/lives` returns 404. It is now two resources, Gutenberg #20450 (January–March) and #49604 (July). "Roman Martyrology (Internet Archive)" was a search; it now opens the 1897 Baltimore edition (`romanmartyrology00cath`).

**Skipped:**
- Fulton J. Sheen, *The Seven Last Words* (Appleton-Century 1934): after the pre-1931 cutoff, and the Internet Archive copy is lending-only.
- Richard F. Clarke, *Charity*: neither Internet Archive upload shows a publisher, date, or imprimatur, and one adds modern captions.
- Joseph Simler, *Catechism of Mental Prayer*: only an 1888 approbation line in a user upload, with no scanned title page.
- *The Catholic Encyclopedia* (1907–1913) saint entries: New Advent is already a listed library; per-saint links belong to the separate Saints & Hagiography section, which awaits the owner's go-ahead.
- The LibriVox recording of Butler's one-volume *Lives of the Saints with Reflections* (#5324) is an abridgment, so it is excluded (`audioExclude`) from the full Kenedy volumes.

## Reading-room expansion (2026-10-22, v10)

Nineteen works (20 Project Gutenberg editions) were added, each marked `"added": "2026-10-22"` so they appear under **Recently added** on Discover & Read. Each edition's `note` records the printed edition or translation year taken from the Gutenberg front matter; every one predates 1931.

- Chesterton: *Heretics* (1905; 1919 John Lane printing, PG #470), *What's Wrong with the World* (1910, #1717), *The Ball and the Cross* (1909, #5265), *The Wisdom of Father Brown* (1914, #223), *The Ballad of the White Horse* (1911, #1719), *The Catholic Church and Conversion* (Macmillan 1927 printing, ©1926, #76305).
- Belloc: *The Servile State* (Foulis 1912, #64882), *The Catholic Church and History* (Macmillan ©1926, #78085).
- Newman: *Loss and Gain* (8th ed., Burns & Oates 1881, #24574), *Callista* (Longmans 1904 impression, #30664), *The Dream of Gerontius* (Egan ed., Longmans 1910 printing, ©1903, #48927).
- Doctors and Fathers: Aquinas, *On Prayer and the Contemplative Life* (tr. Hugh Pope, Washbourne 1914, #22295); Augustine, *The City of God* (tr. Dods, T&T Clark 1871, #45304 and #45305); Bede, *Ecclesiastical History* (Sellar, Bell 1907, #38326); Catherine of Siena, *As Seen in Her Letters* (Scudder, 1905, #7403); Alphonsus Liguori, *The Glories of Mary* (2nd American ed., Dunigan 1852, #72411); *The Writings of the Apostolic Fathers* (Roberts, Donaldson, and Crombie, ANCL vol. I, T&T Clark 1870, #77576).
- Also: Boethius, *The Consolation of Philosophy* (tr. H. R. James, Elliot Stock 1897, #14328); R. H. Benson, *Paradoxes of Catholicism* (Longmans 1913, #16309).

Not hosted: the Gutenberg *Summa Theologica* (#17611, #17897, #19950, #18755) is the 1947 Benziger "Complete American Edition"; Chesterton's *St. Thomas Aquinas* (1933); Fulton Sheen; and E. Allison Peers's John of the Cross (1934–35) are all post-1931. No pre-1931 John of the Cross translation is on Gutenberg as text. Bernard's *On Loving God* (#21152) and Ambrose's *On the Duties of the Clergy* (#22789) have no plain-text file on Gutenberg (audio or HTML only). Catherine's *Dialogue* (Thorold) is not on Gutenberg, so the Scudder *Letters* were hosted instead.

LibriVox chapter lists for the in-reader Listen player are in `data/librivox/<recording id>.json`, generated by `python3 tools/fetch_librivox.py`. A work's `audioTitles` adds LibriVox title aliases.

## Sources checked for this release (2026-10-21)

- Project Gutenberg's catalog pages and complete UTF-8 texts: 45 identified editions, 42 hosted. Two (#50040, Doyle’s 1948 Rule; #18269, the 1958 Pensées with T. S. Eliot’s 1931 introduction) link out because they postdate the pre-1931 hosting rule. Catalog metadata snapshots are in `data/sources/`. Original text files, including credits and the full Gutenberg license, are in `data/texts/`. No Gutenberg generated book summaries were imported.
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

## Reading access audit

Every selected work now has an original description and a direct full-text or sample access path. Lewis's eight bibliography records remain as publication references, with two PBS excerpts and six Google Books/Play samples in a separate `readingLinks` field. Samples never count as hosted or complete texts. Library searches are labeled as searches, with no promise of holdings or borrowing eligibility. The validator rejects a reference-only work without a reading sample.

The collection-wide audit tool, `tools/audit_collection.py`, inventories the selected catalog, all guide/list entries, New Advent work links, supplemental collections, author reading links, and imported book metadata. Its report distinguishes HTTP reachability from a bibliographic review. Imported download files are not fetched in bulk. See `docs/COLLECTION-REVIEW.md` for findings and unresolved checks.
