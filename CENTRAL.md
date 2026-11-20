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

As of November 19, 2026, `main` after PR #74 (`0384057ebf`):

- 195 work records; 130 hosted editions of 125 works in `data/library.json` (215 editions in all, 3 retired); 37 structured editions with openers and EPUBs (`python3 tools/hosted_counts.py`).
- 5,327 sitemap URLs; 8,132 tracked files, most generated (`linguist-generated` in `.gitattributes`).
- Tests: 127 Node and 337 Python.

## Standing decisions

- **Notice rules (November 14, 2026):** the Gutenberg notice is the licence's own 1.E.1 sentence, verbatim, once per page after the text; quality labels in edition details only; one-line affiliate disclosure; rights badges only on a record's own page; one-line Wikipedia credit and a Credits toggle for public-domain portraits; this file's cap. Details: `docs/PROJECT-RULES.md` rules 2, 7, 10, 11, 14, and 15.
- **Hosting rule (November 15, 2026):** no fixed date cutoff. Host a full text only with a recorded, edition-specific basis: US public domain by date (stated once in `tools/rights_rule.py`; in 2026, 1930 or earlier, moving each January 1), or written evidence of no renewal, a defective notice, an open license, or permission. Texts may come from any source. Unknown or in-copyright without permission is link only, never hosted in part. Details: PROJECT-RULES rule 1.
- **Non-renewal basis (November 17, 2026):** `pd-nonrenewal` approved as built in PR #53, with the B. Herder "Printed in U.S.A." reading (US publication at least simultaneous with London; no URAA restoration). Each `pd-nonrenewal` batch still waits for the owner's review. Schroeder's Disciplinary Decrees (B. Herder, 1937; councils 8 to 18) approved as pd-nonrenewal on November 20, 2026 (#87); its hosting batch still goes to the owner's review.
- **Standing approval:** presentation, docs, tests, and tooling may merge on green CI, and so do hosted texts public domain by date (November 15, 2026); the owner's review is still required for new hosted texts on any other basis (each `pd-nonrenewal` batch), rights-rule changes, hosted-text wording, rights or licence statements, affiliate placements, analytics, hosting or DNS, takedown identity, and outreach ([OPERATIONS](docs/OPERATIONS.md#owner-decisions)).
- **Settled (November 15, 2026):** Story of a Soul matching rule; EPUBs published for structured editions; hero engraving; takedown contact email; covers design C; Summa Design A.
- **Donations (November 19, 2026):** Buy Me a Coffee was removed. PayPal is the only donation option.
- **Magisterium AI (November 19, 2026):** the placements as built in #73 (PROJECT-RULES rule 7, `PAGES` in `tools/study_partner.py`), and counting its /study/ clicks as the existing affiliate kind (#75).

## Handoff log

Newest first, 3 entries of at most 5 lines. Older entries: `git log -p -- CENTRAL.md`.

### 2026-11-19, Claude (Claude Code): follow-up pass

- Merged #72 (Advent readiness) and #73 (Magisterium AI panels on /magisterium/, /councils/, /summa/, /study/), after validating #73 on the new main.
- #74 (merged): /study/ loads the site fonts; the disclosure line is 14 px on every page (one `.disclosure` rule); /libraries/ has one line, under its Magisterium link; tests keep one line per page.
- #75 (merged, analytics): /study/ loads `scripts/analytics.js` with `BC_CLICK_KINDS=['affiliate']`, so only the Magisterium click counts there. The 60 merged branches were deleted on November 19. Day 4's J. M. Dent publisher not added: the hosted Scudder file names no publisher.

### 2026-11-19, Claude (Claude Code): cleanup pass, Advent readiness, Magisterium AI support

- Hygiene (#71): snapshot, lean HOLDS with an Advent publishing row, dead /design-preview/ links fixed, docs/README.md matches docs/. Advent (#72): all 26 entries checked against the hosted texts (no data errors); `tools/check_plan_ui.js`; live-site and Publishing items stay open. Magisterium AI (#73): rule 7 allowlist test.

### 2026-11-19, Claude (Claude Code): third pass (in progress)

- Housekeeping (#77): the branch cleanup HOLDS row is removed (all 60 deleted on November 19). "Licensing & credits" everywhere (#78); the home page has a Subscribe button instead of the Substack embed (#79). Dependabot (#80): weekly grouped npm and Actions PRs. Site copy has no em-dashes (#84, `tests/test_site_copy_dashes.py`). Orthodoxy flow batch 1: Confessions, The Betrothed, and Revelations of Divine Love get chapter pages, openers, structure, and EPUBs (#88); batch 2 adds Bede, Boethius, and Abandonment (#89); batch 3 Catherine, the Apostolic Fathers, and Belloc (#91); batch 4 Newman's Idea, Aquinas On Prayer, and the Glories of Mary (37 structured).
- Schroeder (councils 8 to 18): no renewal in the NYPL data; basis approved (#87). Blocked here: archive.org, Wikimedia, and HathiTrust are outside this session's network, so Councils 1a to 1c, the hand passes, and the Doré headers wait for a session on the repo's own environment.

## Open items

- Parked items, owners, and next steps: [HOLDS.md](HOLDS.md).
- Owner: the takedown agent's name and postal address, and DMCA agent registration (the page shows only the contact email).
- Hosted texts: further editions batches; manual proofread of Orthodoxy Chapter IV; Supplement Q1 scan review.
- Advent launches November 29: data and local UI verified (#72); live-site checks and the publishing steps remain ([checklist](docs/ADVENT-LAUNCH.md), HOLDS row). Social readiness for Advent is owned by the Grok bot, not tracked here.
- Libraries research candidates need rights and provenance review before import. No Report-Only CSP exists in `_headers`; the enforced CSP is #83, which the owner merges after the November 22 preview. Low-priority npm audit findings are paused.
- Page-audit decisions: the publish allowlist. `/study/` is indexed, canonical, and in the sitemap (November 20). CI's Study drift check names the missing `study/passages` (harmless).
- Recover the evidence listed in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md); confirm backups and account responsibilities ([OPERATIONS](docs/OPERATIONS.md)).

## Reference map

- Repos: this one (source of truth); `BibliothecaCatholica/bibliotheca-texts` (exported delivery copy, see PROJECT-RULES "Document archive"); `BibliothecaCatholica/aquinas` (separate tool; read its own README and AGENTS.md).
- Rules: `docs/PROJECT-RULES.md` and `docs/ANALYTICS.md`. Technical reference: `docs/IMPLEMENTATION-NOTES.md`; history in `docs/archive/`; map in `docs/README.md`. Operations and approvals: `docs/OPERATIONS.md`.

When resuming: fetch `main`, inspect open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, checks run, known failures, and the next action.
