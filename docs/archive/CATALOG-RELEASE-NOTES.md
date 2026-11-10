# Catalog release notes, October–November 2026

Historical change descriptions migrated from CATALOG.md. They include later corrections and are not a current work count, review guarantee, or to-do list. Paths in code spans are repository-root-relative. Current instructions: [CATALOG](../CATALOG.md); current work: [CENTRAL](../../CENTRAL.md). The Summa exclusion claim has been corrected to reflect the existing approved hosted editions.

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
- *The Catholic Encyclopedia* (1907–1913) saint entries: New Advent is already a listed library; per-saint links belong to the separate Saints & Hagiography section, which is now implemented; see [SAINTS](../SAINTS.md).
- The LibriVox recording of Butler's one-volume *Lives of the Saints with Reflections* (#5324) is an abridgment, so it is excluded (`audioExclude`) from the full Kenedy volumes.

## Reading-room expansion (2026-10-22, v10)

Nineteen works (20 Project Gutenberg editions) were added, each marked `"added": "2026-10-22"` so they appear under **Recently added** on Discover & Read. Each edition's `note` records the printed edition or translation year taken from the Gutenberg front matter; every one predates 1931.

- Chesterton: *Heretics* (1905; 1919 John Lane printing, PG #470), *What's Wrong with the World* (1910, #1717), *The Ball and the Cross* (1909, #5265), *The Wisdom of Father Brown* (1914, #223), *The Ballad of the White Horse* (1911, #1719), *The Catholic Church and Conversion* (Macmillan 1927 printing, ©1926, #76305).
- Belloc: *The Servile State* (Foulis 1912, #64882), *The Catholic Church and History* (Macmillan ©1926, #78085).
- Newman: *Loss and Gain* (8th ed., Burns & Oates 1881, #24574), *Callista* (Longmans 1904 impression, #30664), *The Dream of Gerontius* (Egan ed., Longmans 1910 printing, ©1903, #48927).
- Doctors and Fathers: Aquinas, *Summa Theologiae*, Parts I, I-II, II-II, and III (English Dominican translation, 1911 to 1925; #17611, #17897, #18755, #19950; added 2026-11-09; sample-collated against pre-1931 printings) with the Supplement (transcribed from Internet Archive scans of the 1917, 1921, and 1922 printings, `ia-summa-supplement`, OCR doubts flagged on the pages; see `docs/IMPLEMENTATION-NOTES.md`) and *On Prayer and the Contemplative Life* (tr. Hugh Pope, Washbourne 1914, #22295); Augustine, *The City of God* (tr. Dods, T&T Clark 1871, #45304 and #45305) and *On Christian Doctrine* (tr. Shaw, NPNF Series I Vol. II 1887/1890, `ccel-npnf102-doctrine`, added 2026-11-09); Bede, *Ecclesiastical History* (Sellar, Bell 1907, #38326); Catherine of Siena, *As Seen in Her Letters* (Scudder, 1905, #7403); Alphonsus Liguori, *The Glories of Mary* (2nd American ed., Dunigan 1852, #72411); *The Writings of the Apostolic Fathers* (Roberts, Donaldson, and Crombie, ANCL vol. I, T&T Clark 1870, #77576).
- Also: Boethius, *The Consolation of Philosophy* (tr. H. R. James, Elliot Stock 1897, #14328); R. H. Benson, *Paradoxes of Catholicism* (Longmans 1913, #16309).

Current correction: the four Gutenberg Summa volumes are hosted after the November 9 sample collation against pre-1931 witnesses; their catalog title does not establish that the hosted article text includes the 1947 apparatus. See [the implementation reference](../IMPLEMENTATION-NOTES.md) and `data/sources/`. Chesterton's *St. Thomas Aquinas* (1933), the excluded Sheen title, and E. Allison Peers's John of the Cross (1934–35) remain outside the project cutoff. No pre-1931 John of the Cross translation is on Gutenberg as text. Bernard's *On Loving God* (#21152) and Ambrose's *On the Duties of the Clergy* (#22789) have no plain-text file on Gutenberg (audio or HTML only). Catherine's *Dialogue* (Thorold) is not on Gutenberg, so the Scudder *Letters* were hosted instead.

LibriVox chapter lists for the in-reader Listen player are in `data/librivox/<recording id>.json`, generated by `python3 tools/fetch_librivox.py`. A work's `audioTitles` adds LibriVox title aliases.

## Sources checked for this release (2026-10-21)

- Project Gutenberg's catalog pages and complete UTF-8 texts: 64 Gutenberg editions in the catalog, 61 hosted (counted from `data/library.json`; `tests/test_counts.py` fails if these numbers drift). The 2026-10-21 release had 45 and 42. Of the three not hosted, #50040 (Doyle’s 1948 Rule) and #18269 (the 1958 Pensées with T. S. Eliot’s 1931 introduction) link out because they postdate the pre-1931 hosting rule, and #5657 (*The Practice of the Presence of God*) links to its source. Catalog metadata snapshots are in `data/sources/`. Original text files, including credits and the full Gutenberg license, are in `data/texts/`. No Gutenberg generated book summaries were imported.
- Eight individual patristic texts/collections at New Advent. Those editions remain external, with their translation and editorial credits at source.
- Eight individual Vatican documents: the four Vatican II constitutions, *Fides et Ratio*, *Veritatis Splendor*, *Deus Caritas Est*, and *Rerum Novarum*. These link to official English texts; they are not copied or framed.
- [C. S. Lewis College](https://www.cslewiscollege.org/c-s-lewis/) establishes Lewis's Anglican identity. [Dallas Baptist University's bibliography](https://www.dbu.edu/mitchell/c-s-lewis-resources/bibliography.html) identifies the eight works and original publication dates. These are explicitly bibliographic references, not free reading editions.
- [USCCB lectionary FAQ](https://www.usccb.org/faq/questions-about-lectionary) supports the correction distinguishing the NABRE study Bible from the U.S. Mass lectionary based on the NAB.

`docs/source-link-check.json` records GET results, returned titles, redirects, and response hashes for the 42 distinct catalog URLs. All returned HTTP 200 at this check. This is access evidence, not a guarantee of future availability or a theological review. The checked source titles were compared with the listed works.

