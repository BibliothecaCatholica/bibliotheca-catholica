# Claude Code prompt: structure the remaining Chesterton editions

Rewritten November 23, 2026 to match current rules; the November 15 hosting prompt it replaces is in git history. Paste everything below the line into Claude Code, started in a clone of `BibliothecaCatholica/bibliotheca-catholica` on an up-to-date `main`.

---

You are working in the Bibliotheca Catholica site repository. Read `AGENTS.md`, `CENTRAL.md`, `HOLDS.md`, `docs/HOSTED-EDITIONS.md` (the Orthodoxy flow), and `docs/PROJECT-RULES.md` rule 1 first. Where a document and the code disagree, follow the code and list each mismatch in your final reply.

## The task

Give hosted Chesterton editions that have no chapter map the full Orthodoxy treatment, three editions per draft pull request, chosen by reader value:

- a chapter map in `tools/text_pages.py` (`WORKS`), built from the headings the file itself prints and checked by `items_for()`; start from `python3 tools/draft_text_map.py <work-id>`;
- registration in `tools/structure_text.py` (map mode), an "About this edition" sentence in `PART_D` in `tools/build_text_pages.py` (only facts the edition record or the file states), and the edition id in `tests/test_part_d.py`;
- the generated chapter pages and EPUB (`npm run build`, `python3 tools/build_static.py`), and `python3 tools/hosted_counts.py --write`;
- the HOLDS count updated in the same pull request.

List the candidates with the edition ids in `data/library.json` that have a `text` and no entry in `WORKS`. A file that prints no chapter headings (for example `What I Saw in America`) or whose transcription lost them (`The Thing`) needs a hand-built map from the printed contents page; leave it for its own pull request. Skip any edition an Advent day uses until after December 24 (City of God waits for a two-volume map).

## Hosting rules (when a task also adds a text)

- The hosting rule lives in `tools/rights_rule.py`: public domain in the US by date (in 2026, first published 1930 or earlier; the line moves each January 1), or a recorded non-renewal (`pd-nonrenewal`, `nonRenewal` evidence that passes `nonrenewal_problems()`). Unknown fails closed; a later book with no recorded basis stays link only.
- A transcription must reach the 99.5% read gate (`tools/transcribe_scan.py`), with every hand fix and verified word checked against the page image of the same scan and recorded in the source record.
- Imported plain texts (`tools/import_plain_text.py`, `tools/import_html_pages.py`) keep the source's words and notices and need at least 95% agreement with a dated Internet Archive scan.
- Never edit a hosted TXT; a correction is a new `-r2` edition.

## Process

- Open draft pull requests only, one job per pull request, branched from current `origin/main`. QA reviews each; Micah approves merges. Rebuild on current `main` right before a pull request is marked ready or merged.
- Before every push: `npm run validate`, commit, then `npm run validate -- --drift`.
- Site rules: Oxford comma; no em-dashes in our own copy; exactly one GA4 tag per page and no new analytics events; no Amazon product or affiliate links; Bookshop affiliate id 130222 never on author pages; never call donations tax-deductible; keep `CNAME`, `.well-known/atproto-did`, and `google3b007babfa8923a4.html`; no Cloudflare, DNS, analytics, or affiliate changes.
- If something fails twice, stop and report it.

## Report

Per pull request: link, head SHA, CI state, a one-line summary, any read-gate scores, and the documentation and code mismatches found; then what is blocked and exactly what would unblock it.
