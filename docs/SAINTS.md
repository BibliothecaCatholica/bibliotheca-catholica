# Saints & Hagiography (v15, phase 1)

The saints section is a small, sourced guide to 185 pilot saints, built from the research spec (`saints-hagiography-spec.md`) and its pilot files. It lives at `#/saints` and has static entry pages under `/saints/`.

## What shipped

- **185 saints** in `data/saints.json`: 139 tier 1 (writers already in the library), 34 tier 2 (saints people often look up), and 12 tier 3 (the hard cases of tradition and legend).
- **Pages:** the landing page (alias search, the Hodie block, and tiles), A–Z, a 12-month calendar with day pages, Writers who are saints, Saints of legend, the hagiography shelf (31 public-domain books with edition, imprint, translator, and rights evidence), Sources & method, and profiles.
- **Tier 1 saints** open their existing author page (`#/author/<id>`), which gains a Saint panel: status, tradition flag, labelled feast dates, New Advent, Vatican News, and CatholicSaints.Info links (in that order), and pointers into the hosted lives of the saints.
- **Tier 2 and 3 profiles** (`#/saints/<id>`, static `/saints/<id>/`): status with its source, tradition flag and note, link chips (New Advent, Vatican News, Wikipedia, Wikidata), labelled feast dates, works to read here and LibriVox audio, lives of the saints, and other names.
- **Search:** a `Saint` result group and an alias table (`data/saints-aliases.json`) that pins the exact saint ("Little Flower", "Therese", and "Thomas Aquinas"), or shows "Did you mean" for bare names such as "John".
- **Home page:** a Saints & Hagiography card next to Doctors of the Church, and an "On this feast day" line in the Hodie panel on days when Vatican News lists a saint in the guide.
- **Analytics:** `saint_open` (`saint_id`, `saint_tier`) through `BCAnalytics.track`.

## Data and build

```sh
python3 tools/import_saints_pilot.py --research /path/to/research   # research files -> data/saints.json
python3 tools/build_saints.py                                        # validate, alias table, data/saints.js
python3 tools/build_static.py                                        # /saints/ pages and sitemap
```

`data/saints.js` is about 310 KB, so it is lazy-loaded by `BCSaints.load()` rather than included as a script tag (a change from the spec's suggestion).

Every claim carries a `source_url`. Fields deliberately left out: emblems and patronages (phase 4), the CatholicSaints.Info cross-check dates, and the 30 tier 2 and 3 name-match-only CatholicSaints.Info links. Wikidata birth years that fall after the death year (century-precision values) are dropped.

## Dates

Three kinds of date, always labelled:

1. **Vatican News “Saint of the day”**: what that page lists. It includes saints of the Roman Martyrology who are not in the General Roman Calendar, so it is never presented as the official calendar.
2. **General Roman Calendar**: `null` for every saint, shown as "Not yet checked against the Roman Missal".
3. **Other calendars (Wikidata)**: P841 values, shown as unverified.

## Rights

- **CatholicSaints.Info is link-only.** Its robots.txt bars crawling and its terms forbid copying. Nothing is copied, nothing is fetched at build or run time, and links appear only for the 139 hand-checked tier 1 matches (138 high confidence, plus Hippolytus at medium), after New Advent and Vatican News, with an archived copy link. No outreach to its author.
- No biographies are written in phase 1. Profiles show only sourced fields (status, dates, and the historicity note from the spec).
- The shelf links out to public-domain editions (all imprints 1931 or earlier); nothing new is hosted.
- Flagged authors (`hubAuthors` in `data/editorial-flags.json`) can never be saints in the guide; `build_saints.py` fails if one is.

## Tests

`tests/test_saints.py` (schema, counts, no tier 2 or 3 CatholicSaints.Info links, the 12 tradition flags, unique aliases, the alias JSON equal to the JS, the build being current, and static pages with canonicals) and `tests/saints.test.js` (key normalization, alias lookup, collisions, and day lists).

## Deferred

- Phase 4: emblems and patronages.
- Phase 5: growth beyond the pilot and a saint-of-the-day feature.
- General Roman Calendar dates and ranks (Roman Missal check), and Dicastery for the Causes of Saints status checks.
- Roman Martyrology dates per saint, images, and short original biographies.
- CatholicSaints.Info links for tiers 2 and 3 (only after a hand check of each match).
