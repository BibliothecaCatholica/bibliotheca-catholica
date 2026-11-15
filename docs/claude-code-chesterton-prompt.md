# Claude Code prompt: host the remaining Chesterton works

Paste everything below the line into Claude Code, started in a clone of `BibliothecaCatholica/bibliotheca-catholica` on an up-to-date `main`. Written November 15, 2026 (America/Chicago).

---

You are working in the Bibliotheca Catholica site repository. Your task is to host the remaining G. K. Chesterton works that are public domain in the United States, in small batches, following the repository's own rules and tools. Read `AGENTS.md`, `CENTRAL.md`, `docs/PROJECT-RULES.md` (rule 1, the hosting rule), `docs/HOSTED-EDITIONS.md` (the Orthodoxy flow), and `docs/CATALOG.md` ("Adding a reading edition") before you change anything. When an instruction here and the code disagree, follow the code and say so in your reply (AGENTS.md rule 11).

## Input

`docs/research/chesterton-hostable-2026-11-15.csv` (Research, November 15, 2026). Columns: title, first_published, year_source, status, kind, best_source_type, source_url, source_url_check, pg_ebook_no, alternate_url, alternate_url_check, notes.

The `status` column is out of date: most rows marked `to_add` were hosted the same day. Before each batch, compare every row against `data/library.json` (match on `pg-<pg_ebook_no>` edition ids and on work titles) and work only on rows that are really missing.

## Already done (do not redo)

- Hosted with chapter structure and EPUB (Orthodoxy flow complete): Orthodoxy, Heretics, The Man Who Was Thursday, The Ball and the Cross, St. Francis of Assisi, and the four Father Brown collections that are hosted (Innocence, Wisdom, Incredulity from Standard Ebooks, Secret).
- Hosted as basic text editions (no structure file or EPUB yet): the 43 books of Chesterton batches 1 to 6 (PRs #42 to #47, for example Manalive, The Napoleon of Notting Hill, The Flying Inn, Tremendous Trifles, Twelve Types, Varied Types, The Poet and the Lunatics, The Return of Don Quixote, Four Faultless Felons), plus The Everlasting Man, What's Wrong with the World, The Ballad of the White Horse, and The Catholic Church and Conversion.
- Added November 15 by Catholic Repo (Grok): The Queen of Seven Swords (Faded Page text, `fp-20200364`) and The Trial of John Jasper (`pg-70690`) as hosted texts; link-only catalogue records (Internet Archive or Wikisource, no hosted text) for The Thing, The Resurrection of Rome, The Outline of Sanity, The Superstitions of the Sceptic, Generally Speaking, Do We Agree?, G.K.C. as M.C., Simplicity and Tolstoy, Samuel Johnson (with Alice Meynell), How to Help Annexation, Culture and the Coming Peril, and Gloria in Profundis.
- The Incredulity of Father Brown already uses the Standard Ebooks text (`se-incredulity-father-brown`); the scan is a link only. Keep it that way.

## What is left

1. **Turn the link-only records above into hosted texts** where a faithful plain text exists. Internet Archive OCR alone is not a faithful text: host from a scan only by producing a checked transcription, the way the Summa Supplement was done (`kind: ocr-transcription` in `tools/build_library.py`), or leave the record link-only and say so.
2. **Wikisource texts** (Samuel Johnson, How to Help Annexation, Culture and the Coming Peril, Gloria in Profundis): no import tool exists yet. If you add one, model it on `tools/import_plain_text.py` (pinned source bytes, SHA-256, a dated Internet Archive witness, word-by-word collation, at least 95% agreement) and add a test.
3. **The Sword of Wood** (Project Gutenberg Australia `0900731`): gutenberg.net.au serves a JavaScript bot check, so `tools/import_plain_text.py` cannot fetch it from a plain script. Fetch it some other legitimate way or leave it.
4. **The 11 works with no online copy** (`status = to_add_needs_source`). The validator rejects a work with no editions, and a work whose editions are all `reference` needs `readingLinks`. Do not invent links. Either propose a small, tested "not yet available" convention (for example a list on the Chesterton author page generated from data) and stop for Micah's review, or leave them listed in CENTRAL.md.
5. **Full Orthodoxy flow** for the basic text editions (structure file and site EPUB), one book at a time, after the above.

## Source rules

- Hosting basis (PROJECT-RULES rule 1, `tools/rights_rule.py`): first published in 1930 or earlier (the line moves each January 1), recorded per edition with `rightsBasis: pd-date` and a "First published YYYY" note with its evidence. Anything 1931 or later is link only, never hosted.
- Project Gutenberg: `python3 tools/fetch_gutenberg_edition.py <PG number>`, then add the work and edition to `data/library.json` by hand.
- Other plain texts (Faded Page, Project Gutenberg Australia): `python3 tools/import_plain_text.py SPEC.json`. It keeps the source's words, header, and notices unchanged below a short header of ours, pins the SHA-256, and collates against a dated Internet Archive scan. `tests/test_imported_texts.py` requires at least 95% agreement. If a text falls below 95% because the scan's OCR is poor, do not lower the gate on your own: list it for Micah with sample differences.
- Faded Page plain text is at `https://www.fadedpage.com/books/<pid>/<pid>.txt` (the `link.php` download link redirects to the book page).
- Project Gutenberg Australia: take only the public-domain text. That site also holds books still in US copyright; `tests/test_text_pages.py` allows its links only for editions hosted here.
- Standard Ebooks for Incredulity (already done).
- Internet Archive: before citing or using a scan, confirm it is freely viewable and not lending-only (`https://archive.org/metadata/<id>`; `access-restricted-item` must not be true).
- No overlapping duplicate volumes: Five Types overlaps Twelve Types and Varied Types; A Shilling for My Thoughts, The Wit and Wisdom of G. K. Chesterton, and the 1927 Collected Poems overlap books already hosted. Skip them unless Micah says otherwise. The Book of Job (1916) is only Chesterton's introduction; skip it.
- Never edit a hosted TXT. Em-dashes and spellings inside book texts stay exactly as the source has them.

## Orthodoxy flow (per book) and the light pass

Full flow (`docs/HOSTED-EDITIONS.md`): library.json entry; pinned TXT with SHA-256 and a source record in `data/sources/`; `rightsBasis`; a chapter map (start from `python3 tools/draft_text_map.py <work-id>`); a structure file in `data/structured/` that passes `python3 tools/structure_text.py --check`; the site EPUB from `tools/build_epub.py --publish` (part of `npm run build`); a cover from `tools/covers.py` (design C; rendering needs Node Playwright and its Chromium).

Light pass (allowed for a first pass): library.json entry, pinned TXT, source record, `rightsBasis`, and cover only. Structure and EPUB come later.

For each new hosted edition also run `python3 tools/hosted_counts.py --write` (it refreshes every stated count) and render its cover:

```sh
python3 tools/covers.py --build   # re-renders all covers; or render only the new editions with tools/render_covers.js
```

## Site rules (AGENTS.md)

- 1930-or-earlier basis as above; unknown rights fail closed.
- A work with a calm editorial context note is never featured: leave out `added` so it stays off "New in the reading room".
- No Amazon links. Bookshop affiliate id 130222 only, never on author pages.
- Exactly one GA4 tag (G-HFG445Y1LT) per page; no new analytics events.
- Our own copy (descriptions, notes, blurbs): plain, factual sentences, Oxford commas, no em-dashes, no promotional or AI-sounding phrasing, and never "tax-deductible". Describe only what the book or Research's notes support.
- Keep `CNAME`, `.well-known/atproto-did`, and `google3b007babfa8923a4.html`. Do not touch DNS, Cloudflare, or Pages settings.
- New hosted texts need Micah's review before merge (PROJECT-RULES rule 14). Open one pull request per batch; do not merge it yourself.

## Commands (run all before every push)

```sh
npm ci
npm run build
python3 tools/build_static.py
npm run build:study
python3 tools/hosted_counts.py --write
npm test
npm run validate
git diff --check
# after committing:
npm run validate -- --drift
```

After a batch merges, re-export the texts repository and push it (plain push to `main`, never force):

```sh
git clone https://github.com/BibliothecaCatholica/bibliotheca-texts.git /tmp/bibliotheca-texts
python3 tools/build_text_archive.py --output /tmp/bibliotheca-texts
cd /tmp/bibliotheca-texts && git add -A && git status   # review: new texts/, provenance/, manifest.json only
```

## Stop rules

- Batches of 5 to 10 works, one pull request each.
- Two failed attempts on any one book: stop on that book, record why, move on.
- Never force-push, never rewrite pushed history, never skip hooks.
- Stop and ask Micah before: lowering any test gate, adding a new source type without its own test, hosting anything without a recorded basis, or changing site copy outside the new records.
- At the end of each batch, add one CENTRAL.md handoff entry (at most 5 lines; the log keeps the 3 newest, the file stays under 80 lines; `tests/test_central.py`) listing what was hosted, what was skipped and why, and the PR link.
