# Shared project handoff

Read AGENTS.md and this file at session start. Read detailed references only for the task at hand. Update this file in place at handoff. Cap (owner rule change, November 14, 2026): handoff entries of at most 5 lines, the 3 newest only, and under 80 lines in all (`tests/test_central.py`). No separate dated report files for handoffs. No secrets, reader notes, or private account records here.

When an instruction file and the existing code disagree, follow the conventions in the code, and point out each mismatch in your final reply. Updated November 14, 2026 (America/Chicago). This is the single living coordination file for every contributor: the Grok bots, ChatGPT (and Codex), Claude (and Claude Code), and anyone else.

## Project and authority

Free Catholic reading room and curated resource index: https://bibliothecacatholica.com. Static HTML/CSS/JS with Python generators and pinned npm Study desk dependencies. Catalog/provenance authority lives here; `BibliothecaCatholica/bibliotheca-texts` is the separate delivery copy. Zimit and personal offline archives are separate projects. Owner: Micah Watson. Responsibility follows the assigned task, not the AI provider:

| Responsibility | Deliverable | Boundary |
|---|---|---|
| Owner | Editorial and operational decisions | Approves scope listed in OPERATIONS |
| Research | Exact edition/source evidence and uncertainty | Cannot turn a lead into hosting permission |
| Implementation | Source changes plus generated output | Must preserve rules and other branches |
| QA | Reproducible checks tied to a commit | Reports failures; does not infer approval |
| Business / publishing | Owner-authorized account and publication work | No account changes or outreach from a role name alone |

Any tool can perform an assigned responsibility. References to Research, QA, and Business describe responsibilities or historical reports, not verified identities or grants of access. Approvals come only from the owner and are kept outside the repository: entries record what was done and decided, never quotes or names of approvers.

## Hosting and data flow

GitHub `main` is the source of truth. Cloudflare Pages deploys it automatically to https://bibliothecacatholica.com (every PR gets a preview check); confirm a deploy by comparing the live `/build.json` `id` with `git show origin/main:build.json`. The `CNAME` file stays. texts.bibliothecacatholica.com is served from `bibliotheca-texts`. DNS and the Cloudflare zone belong to Business. GitHub Pages for this repo was turned off on November 15, 2026, so Cloudflare is the only host; the texts repo keeps its own Pages site.

Three repositories: (1) `bibliotheca-catholica` (this one) holds the catalogue, provenance, and the original TXT files in `data/texts/`. (2) `bibliotheca-texts` is a delivery copy exported from here by `tools/build_text_archive.py` (texts, `manifest.json`, `provenance/`) and served by its own GitHub Pages at texts.bibliothecacatholica.com; the reader fetches `textArchive.baseUrl` first and falls back to the local copy. Never edit texts there by hand. (3) `aquinas` (new, November 14 and 15) is a separate local study tool: SQLite search over Summa I and I-II (Project Gutenberg 17611 and 17897) plus an experimental LFM3-1.7B model, the "Aquinas Neuron", released as GitHub prereleases for Ollama. It has no website or domain and does not feed this site; the site's `/summa/` pages are built here by `tools/build_summa.py`.

## Verified snapshot

As of November 15, 2026, `main` after PR #47 (`32e22d4d05`) and the QA fixes that followed it:

- 195 work records; 130 hosted editions of 125 works in `data/library.json` (203 editions in all); 16 structured editions with openers and EPUBs (`python3 tools/hosted_counts.py`).
- 5,169 sitemap URLs; 7699 tracked files, most generated (`linguist-generated` in `.gitattributes`).
- Tests: 124 Node and 284 Python.

## Standing decisions

- **Notice rules (November 14, 2026):** the Gutenberg notice is the licence's own 1.E.1 sentence, verbatim, once per page after the text; quality labels in edition details only; one-line affiliate disclosure; rights badges only on a record's own page; one-line Wikipedia credit and a Credits toggle for public-domain portraits; this file's cap. Details: `docs/PROJECT-RULES.md` rules 2, 7, 10, 11, 14, and 15.
- **Hosting rule (November 15, 2026):** no fixed date cutoff. Host a full text only with a recorded, edition-specific basis: US public domain by date (stated once in `tools/rights_rule.py`; in 2026, 1930 or earlier, moving each January 1), or written evidence of no renewal, a defective notice, an open license, or permission. Texts may come from any source. Unknown or in-copyright without permission is link only, never hosted in part. Details: PROJECT-RULES rule 1.
- **Non-renewal basis (November 17, 2026):** `pd-nonrenewal` approved as built in PR #53, with the B. Herder "Printed in U.S.A." reading (US publication at least simultaneous with London; no URAA restoration). Each `pd-nonrenewal` batch still waits for the owner's review.
- **Standing approval:** presentation, docs, tests, and tooling may merge on green CI, and so do hosted texts public domain by date (November 15, 2026); the owner's review is still required for new hosted texts on any other basis (each `pd-nonrenewal` batch), rights-rule changes, hosted-text wording, rights or licence statements, affiliate placements, analytics, hosting or DNS, takedown identity, and outreach ([OPERATIONS](docs/OPERATIONS.md#owner-decisions)).
- **Settled (November 15, 2026):** Story of a Soul matching rule; EPUBs published for structured editions; hero engraving; takedown contact email; covers design C; Summa Design A.

## Handoff log

Newest first, 3 entries of at most 5 lines. Older entries: `git log -p -- CENTRAL.md`.

### 2026-11-17, Claude (Claude Code): Sources and credits page (approved)

- /credits/ (tools/credits_page.py, from data): every hosted edition's full record, portraits, Wikipedia excerpts, and the home engraving, one anchor each; footer link; app.js keeps its #anchors out of routing and page views.
- A book ends with a one-line `.colophon` linking to its record (after the 2c `.end-colophon` section on static last pages); author pages show "Image credit" and "Text credit" links. Approved by Micah November 17 with the PR's defaults; merged after main's design refresh.

### 2026-11-17, Claude (Claude Code): design refresh

- Part 1 (#56): audit, 20 unlisted previews at /design-preview/ (tools/build_design_preview.py, tests/test_design_preview.py), and docs/research/design-directions-2026-11.md. Micah picked: home v4, reading room v1 with authors v2, reading v2 contents (not sticky) with v3 endings, licensing v2, nav v1.
- Part 2, one area per PR, screenshots in docs/research/design-refresh-2026-11/: home "Saints first" (#60; `HOME_BEGIN` in tools/site_copy.py); reading room facets and author shelf list (#64; `--field` token); chapter pages with contents at the start, Continue reading, Finis, colophon (#65); /licensing/ contents rail (#66); masthead navigation and footer (#67). /design-preview/ and its script and test removed; screenshots stay in docs/research/design-refresh-2026-11/. Open: HOLDS.md row on the licensing page names and the home Substack embed.

### 2026-11-17, Claude (Claude Code): Ecumenical Councils section

- /councils/: the 21 councils in order with own-words summaries and where to read each (data/councils.json, tools/councils_page.py, tests/test_councils.py); linked first on /magisterium/ and in the footer, not the main nav. Kept static by app.js (staticOnly), so it has no in-page #anchors.
- Sources (Part 2, docs only): docs/research/councils-sources-2026-11.csv. Hostable by date: 1 to 7 (Percival 1900), Trent (Waterworth 1848), Vatican I (Manning 1870). Link-only: 8 to 18 (Schroeder 1937 canons pending NYPL), Vatican II. No LibriVox recording of any council text. Hosting waits for Micah (HOLDS.md).

## Open items

- Parked items, owners, and next steps: [HOLDS.md](HOLDS.md).
- Owner: the takedown agent's name and postal address, and DMCA agent registration (the page shows only the contact email).
- Hosted texts: further editions batches; manual proofread of Orthodoxy Chapter IV; Supplement Q1 scan review.
- Advent launches November 29: excerpt-to-source comparison ([checklist](docs/ADVENT-LAUNCH.md)). Social readiness for Advent is owned by the Grok bot, not tracked here.
- Libraries research candidates need rights and provenance review before import. Paused: `_headers` Report-Only CSP, low-priority npm audit findings.
- Page-audit decisions: the publish allowlist and the `study/index.html` sitemap or noindex question. CI's Study drift check names the missing `study/passages` (harmless).
- Recover the evidence listed in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md); confirm backups and account responsibilities ([OPERATIONS](docs/OPERATIONS.md)).

## Reference map

- Repos: this one (source of truth); `BibliothecaCatholica/bibliotheca-texts` (exported delivery copy, see PROJECT-RULES "Document archive"); `BibliothecaCatholica/aquinas` (separate tool; read its own README and AGENTS.md).
- Rules: `docs/PROJECT-RULES.md` and `docs/ANALYTICS.md`. Technical reference: `docs/IMPLEMENTATION-NOTES.md`; history in `docs/archive/`; map in `docs/README.md`. Operations and approvals: `docs/OPERATIONS.md`.

When resuming: fetch `main`, inspect open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, checks run, known failures, and the next action.
