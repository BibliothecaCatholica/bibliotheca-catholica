# Full-year saints calendar (facts only): REVIEW BRANCH, not approved for publication

Status (2026-11-09): built on the local branch `saints-calendar` for the owner's review. Nothing here is public
until Micah approves it.

## Owner's decisions (2026-11-09)

- 3:40 PM CST: no per-saint pages. Use the data to expand the existing saints and calendar features.
- 4:00 PM CST: "Have a single instance of linking the information to CatholicSaints (that can be pushed to the
  resources) … having the saint on a date is not exclusive to CatholicSaints, which is the point of this project …
  it should be combined into 1 list; we can have a note for disagreements." So:
  - no per-entry CatholicSaints.Info links (day pages, today lines, author and profile lines). One Resources entry
    (References, "Saints & hagiography": "CatholicSaints.Info") credits it as a source of the calendar facts. AGENTS.md
    rule 8 is otherwise unchanged, and the 139 hand-checked tier 1 author-page links stay as they were;
  - one merged list per day, with a short neutral note where sources disagree, and no source label per entry;
  - the raw import stays out of the deployed site.

## What it adds to the existing saints guide

The v15 guide already had a calendar (`#/saints/calendar`, a month grid, and `#/saints/calendar/<MM-DD>` day views,
app-only), a Hodie line on the home page, a Hodie block on `#/saints`, author-page Saint panels, and static profiles.
With `data/saints-days.json` present, the build adds:

- **Day pages** `/saints/calendar/<MM-DD>/` (366, including 29 February). Each is ONE list that merges the guide's
  own saints for the day (Vatican News "Saint of the day" dates) with the calendar entries, deduplicated by person,
  grouped as Feasts, Marian titles, Saints, Popes, Blessed, Martyr groups, and Other. Each entry: the name in site
  style ("St. Thomas Aquinas", "Pope St. John Paul II", "Blessed …"), linked to the guide's author page or profile when
  there is one; short facts (born, died, patronage, beatified, canonized, other names); and a note when needed:
  - "Date differs between sources; also kept on <days>." when one source has the person on this day and the other
    places them elsewhere;
  - "Also kept on <days> in some calendars." for other days the same person is kept on;
  - "Listed as Saint in some sources and Blessed in others." for a title conflict.
  One page-level note says the list combines the Vatican News pages with a long-form calendar credited on the
  Resources page, and that this is not the General Roman Calendar. These pages are the app's day view:
  `#/saints/calendar/<MM-DD>` redirects to them and `staticOnly()` keeps them.
- **Month grid** (`#/saints/calendar`): each day links to its page; its label carries the day's merged count.
- **Saints today**: the home Hodie line and the `#/saints` Hodie block add "N saints, blessed, and feasts kept on
  <day> →". Plain links, client-side date, no analytics event.
- **Author pages and profiles** of guide saints: "Saints calendar: <day links>".
- **/saints/**: a "The full-year calendar" block with every day linked by month.

Merging (`saints_calendar.merged_day`): a calendar entry joins a guide saint when its guide id matches (set at import
from the same CatholicSaints page as the guide's hand-checked link, or an exact multi-word name or alias), or, on the
guide saint's own day, when its normalized name equals any of the guide saint's names (so "St. Monica" joins
"Monica of Hippo" on 27 August). Normalizing drops Saint, St., Sts., Blessed, Bl., Pope, Venerable, and The, for
matching only. Two calendar entries on one day merge only if their normalized names and facts agree. Rites pages
have no saint key to match on, so no Rites links are added.

## Data

- **Raw import** `.local/saints-calendar.json` (git-ignored; never committed or deployed): every fact field, slugs,
  and the source URLs, keyed by slug, with a date index. Kept for the record and for re-matching.
- **`data/saints-days.json`** (committed): `{"note", "matched", "days": {"MM-DD": [entry, …]}}`, each entry
  `{"n": name in site style, "t": type, "f"?: short facts, "o"?: [other MM-DD], "g"?: guide saint id}`. No URLs,
  no slugs, no source names (`validate()` fails on any of them, on em-dashes, and on text over 400 characters).
  Types: `feast`, `marian-title`, `saint`, `pope`, `blessed`, `martyr-group`, `unknown`.
- `data/saints.js` gets merged per-day counts only (`cal`, about 4 KB).
- A slot for a public-domain life (pre-1931 source, for example the 1921 *Book of Saints*) is reserved for later; it
  is not in the per-day file yet.

## Importing

```sh
python3 tools/import_saints.py --input /path/to/saints-calendar-facts-full-year.jsonl --report /tmp/saints-import-report.json
python3 tools/build_saints.py
python3 tools/build_static.py
npm test
```

The importer keeps only whitelisted fact fields (`FIELDS`; several spellings and nested `born`/`died` accepted) and
counts every dropped key, so profiles and other prose never reach the site. It dedupes on slug (merging days,
aliases, and patronages; differing values are reported as `conflicts`), takes a missing slug from the URL path,
replaces em-dashes, drops Amazon links and URLs outside catholicsaints.info/.mobi, treats any value over 160
characters as prose, and rejects bad dates. `--strict` exits 1 if a record was rejected. The report lists bad dates,
missing slugs (unlinked names), conflicts, dropped keys, prose dropped, and days with no record.

## Size and hosting

Measured with a synthetic 12,337-row file of the same shape (not committed): 366 day pages of about 28 KB on
average (36 KB max), 13 MB in all; `build_static.py` about 0.5 s slower. File count: +367 (366 pages and
`data/saints-days.json`), about 6,360 of the 20,000-file Cloudflare Pages limit. Pagefind (the Study desk) indexes
only hosted texts and is unchanged.

Tests: `tests/test_saints_calendar.py`, `tests/saints-calendar.test.js` (fixture: `tests/fixtures/saints-sample.jsonl`).
