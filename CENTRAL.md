# Shared project handoff

Read AGENTS.md and this file at session start. Read detailed references only for the task at hand. Update this file in place at handoff. Cap (owner rule change, November 14, 2026): handoff entries of at most 5 lines, the 3 newest only, and under 80 lines in all (`tests/test_central.py`). No separate dated report files for handoffs. No secrets, reader notes, or private account records here.

When an instruction file and the existing code disagree, follow the conventions in the code, and point out each mismatch in your final reply. Updated November 21, 2026 (America/Chicago). This is the single living coordination file for every contributor: the Grok bots, ChatGPT (and Codex), Claude (and Claude Code), and anyone else.

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

As of November 21, 2026, `main` after PR #114:

- 204 work records; 144 hosted editions of 139 works in `data/library.json` (222 editions in all, 4 retired); 52 structured editions with openers and EPUBs (`python3 tools/hosted_counts.py`).
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

### 2026-11-21, Claude (Claude Code): open run 2

- Chesterton polish (full Orthodoxy treatment, owner-approved): #108, #111, #112, #113, and #114 structure 14 more editions (Everlasting Man, Tremendous Trifles, New Jerusalem, Dickens, Poet and the Lunatics, Return of Don Quixote, Cobbett, Stevenson 1927, Irish Impressions, Napoleon of Notting Hill, Victorian Age, Four Faultless Felons, Eugenics, Tales of the Long Bow); about 45 Chesterton editions remain, several needing hand-built maps (`What I Saw in America` prints no headings). Hosted: Samuel Johnson (#109, 99.61%; `transcribe_scan.py` rejoins lost line-end hyphens) and the Stevenson booklet as its 1906 New York printing (#110). Essays and Addresses was already hosted with its evidence. Gloria in Profundis: no dated scan found.
- Still refused: every server in the December-texts, councils, and Schroeder rows, the Faustula scans (ia601004, ia801004, ia601606, ia903203), ia601403 (Trent images, so "Aposotlic" and "excomnunication" stay), la.wikisource.org, books.google.com, www.mirrorservice.org; gutenberg.org 503; HathiTrust bot check. The non-renewal batch was probed (Cassidy 98.87% with the new tool; about 270 cited names to check per book). Next: more Chesterton maps, then the non-renewal review batch.

### 2026-11-21, Claude (Claude Code): open run

- Merged #98 (Catholic Encyclopedia "Advent"; `transcribe_scan.py` learns article bounds, two columns, `verifiedWords`), #99 and #106 (Doré heads on ten sections; #95 closed), #100 (The Sword of Wood and C under an owner-approved `scanException`), #101 (Benham 1874), #102 (Trent r2: 34 confirmed typos; Session VII drop cap), #103 to #105 (G.K.C. as M.C., Do We Agree?, The Superstitions of the Sceptic). Bug sweep clean: no broken internal links or missing alt text in 5,726 pages, no console errors, plan check 26/26.
- Refused or down: la.wikisource.org; ia600703, ia800703 (PL 24); every free Catholic Encyclopedia vol. 11 server; babel.hathitrust.org (bot check); books.google.com; ia600805, ia800805 (Butler XII); gutenberg.org (503, maintenance, November 20 and 21). Wikimedia rate-limits uploads at times. Owner: the session could not delete branches; the 29 merged ones are listed in the run's final reply with a ready command. Next: Douay-Rheims once Gutenberg is back, Samuel Johnson, the non-renewal review batch, Candles' Beams, Robert Louis Stevenson, then the Orthodoxy flow.

### 2026-11-20, Claude (Claude Code): network pass

- Merged #90: Walsh's The World's Debt to the Catholic Church hosted (97.5% scan agreement); The Sword of Wood and C held (no dated scan). #96: Trent (Waterworth, 1848) hosted and structured by session via the new `tools/import_html_pages.py` (read gate 99.81%, 96.6% agreement), linked from /councils/. #95 (do not merge): Doré header options for five pages; the owner picks.
- Refused archive.org file servers (HOLDS rows name them): ia600707, ia800707, ia600406, ia800406 (Schroeder); ia600806, ia800806 (Percival); ia600803, ia800803 (Manning); ia601608, ia801608, ia600704, ia800704 (second printings).
- Stopped here: the transcription backlog (its scans are on allowed servers; G.K.C. as M.C., at 99.49%, is nearest the gate). #83 waits for the owner after the Nov 22 preview.

## Open items

- Parked items, owners, and next steps: [HOLDS.md](HOLDS.md).
- Owner: the takedown agent's name and postal address, and DMCA agent registration (the page shows only the contact email).
- Hosted texts: further editions batches; manual proofread of Orthodoxy Chapter IV; Supplement Q1 scan review.
- Advent launches November 29: data and local UI verified (#72); live-site checks and the publishing steps remain ([checklist](docs/ADVENT-LAUNCH.md), HOLDS row). Social readiness for Advent is owned by the Grok bot, not tracked here.
- Libraries research candidates need rights and provenance review before import. No Report-Only CSP exists in `_headers`; the enforced CSP is #83, which the owner merges after the November 22 preview. Low-priority npm audit findings are paused. Page-audit decisions: the publish allowlist. `/study/` is indexed, canonical, and in the sitemap (November 20). CI's Study drift check names the missing `study/passages` (harmless).
- Recover the evidence listed in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md); confirm backups and account responsibilities ([OPERATIONS](docs/OPERATIONS.md)).

## Reference map

- Repos: this one (source of truth); `BibliothecaCatholica/bibliotheca-texts` (exported delivery copy, see PROJECT-RULES "Document archive"); `BibliothecaCatholica/aquinas` (separate tool; read its own README and AGENTS.md).
- Rules: `docs/PROJECT-RULES.md` and `docs/ANALYTICS.md`. Technical reference: `docs/IMPLEMENTATION-NOTES.md`; history in `docs/archive/`; map in `docs/README.md`. Operations and approvals: `docs/OPERATIONS.md`.

When resuming: fetch `main`, inspect open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, checks run, known failures, and the next action.
