# Shared project handoff

Read AGENTS.md and this file at session start. Read detailed references only for the task at hand. Update this file in place at handoff. Cap (owner rule change, November 14, 2026): handoff entries of at most 5 lines, the 3 newest only, and under 80 lines in all (`tests/test_central.py`). No separate dated report files for handoffs. No secrets, reader notes, or private account records here.

When an instruction file and the existing code disagree, follow the conventions in the code, and point out each mismatch in your final reply. Updated November 14, 2026 (America/Chicago). This is the single living coordination file for every contributor (Grok bots, ChatGPT, Codex, Claude, and others).

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

## Verified snapshot

As of November 15, 2026, `main` at `54c17291c1` (PR #37):

- 157 work records; 117 hosted editions of 112 works in `data/library.json`.
- 4,936 static pages and 4,937 sitemap URLs; about 6,800 tracked files, most generated (`linguist-generated` in `.gitattributes`).
- Tests: 124 Node and 270 Python.

## Standing decisions

- **Notice rules (November 14, 2026):** the Gutenberg notice is the licence's own 1.E.1 sentence, verbatim, once per page after the text; quality labels in edition details only; one-line affiliate disclosure; rights badges only on a record's own page; one-line Wikipedia credit and a Credits toggle for public-domain portraits; this file's cap. Details: `docs/PROJECT-RULES.md` rules 2, 7, 10, 11, 14, and 15.
- **Hosting rule (November 15, 2026):** no fixed date cutoff. Host a full text only with a recorded, edition-specific basis: US public domain by date (stated once in `tools/rights_rule.py`; in 2026, 1930 or earlier, moving each January 1), or written evidence of no renewal, a defective notice, an open license, or permission. Texts may come from any source. Unknown or in-copyright without permission is link only, never hosted in part. Details: PROJECT-RULES rule 1.
- **Standing approval:** presentation, docs, tests, and tooling may merge on green CI; the owner's review is still required for new hosted texts, hosted-text wording, rights or licence statements, affiliate placements, analytics, hosting or DNS, takedown identity, and outreach ([OPERATIONS](docs/OPERATIONS.md#owner-decisions)).
- **Settled (November 15, 2026):** Story of a Soul matching rule; EPUBs published for structured editions; hero engraving; takedown contact email; covers design C; Summa Design A.

## Handoff log

Newest first, 3 entries of at most 5 lines. Older entries: `git log -p -- CENTRAL.md`.

### 2026-11-15, Catholic Repo (Grok): GitHub Pages turned off

- GitHub Pages disabled for `bibliotheca-catholica` (Micah, Nov 15). `CNAME` kept; texts.bibliothecacatholica.com untouched. Live site checked afterward: 200 from Cloudflare. Pages can be re-enabled in repo settings if ever needed.

### 2026-11-15, Claude (Claude Code): editions batch 2

- Ten more editions with chapter pages, openers, structure files, and EPUBs: Heretics, The Ball and the Cross, The Man Who Was Thursday, Chesterton's Saint Francis, Grammar of Assent, Development of Christian Doctrine, Paradoxes of Catholicism, Life of St. Teresa, Apologia, Virgin Saints and Martyrs.
- Map tooling: two-block headings, division lines carried into the EPUB, slugs capped at 60 characters, no second "Chapter" label on headings that name themselves.

### 2026-11-15, Claude (Claude Code): approval statements removed; Summa Design A

- Approval statements removed from the repository (PR #38); Summa Design A on all 3,726 question and article pages (PR #37).

## Open items

- Owner: the takedown agent's name and postal address, and DMCA agent registration (the page shows only the contact email).
- Hosted texts: further editions batches; manual proofread of Orthodoxy Chapter IV; Supplement Q1 scan review.
- Advent launches November 29: excerpt-to-source comparison ([checklist](docs/ADVENT-LAUNCH.md)). Social readiness for Advent is owned by the Grok bot, not tracked here.
- Libraries research candidates need rights and provenance review before import. Paused: `_headers` Report-Only CSP, low-priority npm audit findings.
- Page-audit decisions: the publish allowlist and the `study/index.html` sitemap or noindex question. CI's Study drift check names the missing `study/passages` (harmless).
- Recover the evidence listed in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md); confirm backups and account responsibilities ([OPERATIONS](docs/OPERATIONS.md)).

## Reference map

- Rules: `docs/PROJECT-RULES.md` and `docs/ANALYTICS.md`. Technical reference: `docs/IMPLEMENTATION-NOTES.md`; history in `docs/archive/`; map in `docs/README.md`. Operations and approvals: `docs/OPERATIONS.md`.

When resuming: fetch `main`, inspect open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, checks run, known failures, and the next action.
