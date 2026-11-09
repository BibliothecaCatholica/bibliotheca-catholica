# Full-year saints calendar (facts only): REVIEW BRANCH, not approved for publication

Status (2026-11-09): built on the local branch `saints-calendar` for the owner's review. Nothing here is public
until Micah approves it, and the AGENTS.md rule 8 change below needs his approval too.

## What it does (no new page types; expands the existing saints guide)

The v15 saints guide already has a calendar (`#/saints/calendar`, a month grid, and `#/saints/calendar/<MM-DD>`
day views, app-only), a Hodie line on the home page, a Hodie block on `#/saints`, author-page Saint panels, and
static profiles. With `data/saints-calendar.json` present, the build adds:

- **Day pages** `/saints/calendar/<MM-DD>/`, one per day (366, including 29 February). Each lists the guide's
  own saints for the day (Vatican News, labelled as before), then every name the calendar lists, grouped as
  Feasts, Marian titles, Saints, Popes, Blessed, Martyr groups, and Other names, with short facts (born, died,
  patronage, beatified, canonized, other names), an outbound "CatholicSaints.Info ↗" link, the other days the
  same saint is listed on, and a link to the guide's profile or author page when the saint is matched.
  These are the app's day view: `#/saints/calendar/<MM-DD>` redirects to them, and `staticOnly()` keeps them.
  No per-saint pages are generated (owner's direction, 2026-11-09).
- **Month grid** (`#/saints/calendar`): each day links to its day page and its label carries the day's count.
- **Saints today**: the home Hodie line and the `#/saints` Hodie block add "N saints, blessed, and feasts in the
  full calendar for <day> →". Plain links, client-side date, no analytics event.
- **Author pages and profiles** of guide saints matched to the calendar: "In the CatholicSaints.Info calendar:
  <day links>".
- **/saints/**: a "The full-year calendar" block with every day linked by month.

Matching to the guide (`saints_calendar.match_guide`) is conservative: the same CatholicSaints.Info page as a
guide saint's hand-checked tier 1 link (path compared, so .mobi and .info agree), or an exact multi-word alias
key from `data/saints-aliases.json`. One-word names never match. Rites pages have no saint key to match on, so
no Rites links are added.

## Data

`data/saints-calendar.json`, written only by `tools/import_saints.py`:

```
{"note":…, "source":…, "types":{type: label}, "stats":{…},
 "saints":{"<slug>":{"slug","name","type","dates":["MM-DD",…],"aliases"?,"born_date"?,"born_place"?,
                    "died_date"?,"died_place"?,"patronage"?,"beatified"?,"canonized"?,"url"?,"pd_life":null}},
 "days":{"MM-DD":{"slugs":[…],"names"?:[{"name","type","url"?}]}}}
```

- `type` is one of `saint`, `blessed`, `pope`, `martyr-group`, `marian-title`, `feast`, `unknown`.
- `names` are calendar names with no slug (unlinked): listed on their day, no facts.
- `pd_life` is the slot for a public-domain life: `{text, source_title, source_url, source_year}` with
  `source_year` before 1931 (for example the 1921 *Book of Saints* or pre-1931 Butler). Empty until filled by hand.
- `tools/build_saints.py` validates the file and puts per-day counts only (`cal`, about 4 KB) in `data/saints.js`;
  `tools/build_static.py` writes the day pages. With no file, neither adds anything.

## Importing

```sh
python3 tools/import_saints.py --input /path/to/saints-calendar-facts-full-year.jsonl --report /tmp/saints-import-report.json
python3 tools/build_saints.py
python3 tools/build_static.py
npm test
```

The importer accepts several spellings of each field (see `FIELDS`: for example `born_place`/`birth_place`, or
nested `born: {date, place}`). Every other key is dropped and counted (`dropped_keys`), so profiles and other prose
never reach the site. It dedupes on slug (merging days, aliases, and patronages; differing scalar values are
reported as `conflicts`, first value kept), takes a missing slug from the CatholicSaints URL path when there is one,
replaces em-dashes (counted), drops Amazon links and URLs outside catholicsaints.info/.mobi, treats any kept value
over 160 characters as prose and drops it, and rejects bad dates. `--strict` exits 1 if a record was rejected.

Do not commit the raw scrape; commit only `data/saints-calendar.json` and the build output.

## Size and hosting

Measured with a synthetic 12,337-row file of the same shape (not committed): 10,430 slugs; `data/saints-calendar.json`
about 4 MB; `data/saints.js` +4 KB; 366 day pages, about 28 KB each on average (36 KB max), 13 MB in all;
`build_static.py` about 0.5 s slower. File count: +367 (366 pages and the data file), so about 6,355 of the
20,000-file Cloudflare Pages limit. Pagefind (the Study desk) indexes only hosted texts and is unchanged.

## Rights (open questions for the owner)

- AGENTS.md rule 8 allowed CatholicSaints.Info links only on 139 hand-checked tier 1 writers. Day pages add one
  outbound link per calendar entry. That change needs the owner's approval.
- The dataset was scraped from catholicsaints.mobi. CatholicSaints.Info's robots.txt bars crawling and its terms
  forbid copying (AGENTS.md rule 8). Facts are not copyrightable in the US, but publishing the whole calendar as
  `data/saints-calendar.json` (served at /data/) republishes the compilation. Consider keeping the raw data file
  out of the deployed tree, or confirming the owner accepts the risk.
- No prose is hosted. Lives come only from public-domain sources through `pd_life`.

Tests: `tests/test_saints_calendar.py`, `tests/saints-calendar.test.js` (fixture: `tests/fixtures/saints-sample.jsonl`).
