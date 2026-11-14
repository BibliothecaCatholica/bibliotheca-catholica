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

Any tool can perform an assigned responsibility. References to Research, QA, and Business describe responsibilities or historical reports, not verified identities or grants of access. Only Micah's own words count as approval, and an entry should quote or cite where he gave it.

## Hosting and data flow

GitHub `main` is the source of truth. Cloudflare Pages deploys it automatically to https://bibliothecacatholica.com (every PR gets a preview check); confirm a deploy by comparing the live `/build.json` `id` with `git show origin/main:build.json`. The `CNAME` file stays. texts.bibliothecacatholica.com is served from `bibliotheca-texts`. DNS and the Cloudflare zone belong to Business. GitHub Pages only redirects (301 to the apex, checked November 14).

## Verified snapshot

As of November 14, 2026, `main` at `6acc7bae4f` (PR #24) plus branch `claude/notice-rules`:

- 104 work records; 64 hosted editions of 59 works in `data/library.json`.
- 4,925 static pages and 4,926 sitemap URLs; about 6,750 tracked files, about 5,980 generated (`linguist-generated` in `.gitattributes`).
- Tests: 124 Node and 246 Python.

## Standing owner decisions

- **Rule changes of November 14, 2026** (Micah's message pasted as the instruction "including every rule change below", items 1 to 5): one-sentence Gutenberg notice, quality labels in edition details only, one-line affiliate disclosure, badges only on a record's own page, one-line Wikipedia credit and a Credits toggle for public-domain portraits, the standing approval below, and this file's cap. Recorded here once; the rules cite it as "owner rule change, November 14, 2026". Details: `docs/PROJECT-RULES.md` rules 2, 7, 10, 11, 14, and 15.
- **Standing approval:** presentation, docs, tests, and tooling may merge on green CI without Micah's review; his review is still required for new hosted texts, hosted-text wording, rights or licence statements, affiliate placements, analytics, hosting or DNS, takedown identity, and outreach ([OPERATIONS](docs/OPERATIONS.md#owner-decisions)).

## Handoff log

Newest first, 3 entries of at most 5 lines. Older entries: `git log -p -- CENTRAL.md`.

### 2026-11-14, Claude (Claude Code): notice rules applied site-wide

- Chapter and Summa pages: text first, then the one-line notice, then an "Edition details" toggle (edition, source, quality labels, OCR notes); no badges. Reader: notice at the end of the last section and in "Source, rights, and downloads". Affiliate line once per page; badges off lists, author pages, the Advent plan, and rites resource lists (status kept as `data-rights`); one-line Wikipedia credit; Credits toggle for public-domain portraits; footer of two columns and one credits line.
- [PR #28](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/28), branch `claude/notice-rules`: open for Micah's review, since it changes licence wording (outside the standing approval). Builds pass, 124 Node and 247 Python tests pass, no drift.

### 2026-11-14, Claude (Claude Code): PR #24 merged and deployed

- Orthodoxy structured text, review EPUB (CI artifact, unpublished), and automatic display-only layout (59 editions on, five verse works excluded, coverage per edition in `data/auto-layout/report.json`, `KEEP` for Orthodoxy 123 and Thursday 22). Process: [docs/HOSTED-EDITIONS.md](docs/HOSTED-EDITIONS.md).
- Squash-merged as `6acc7bae4f`; live `/build.json` served `bc-29cc90930dce`, the build ID of `main` at that commit.
- Approval: Micah, November 14 (item 1 of the rule-change message; step 2a rule change quoted in PROJECT-RULES rule 13).

### 2026-11-14, Claude (Claude Code): design pass parts 1 and 2 merged and deployed

- PR #26 as `8cb4f466` (deploy `bc-3ac4a7750581`) and PR #27 as `d7943291` (deploy `bc-bab55b05a928`): design rules, calmer work page and reader, self-hosted portraits, seven-item navigation, catalogue shelves.
- Approval: Micah, November 12 and 14 (design brief, "Start on Plan B", and merge without a phone check).

## Open items

- Micah: a hero engraving (three proposals in PR #27); the takedown agent's name, address, and email (page shows a PLACEHOLDER).
- Hosted texts: Story of a Soul structure (no HTML italics without a decision); Part D (beautiful editions) under the standing approval for presentation; manual proofread of Orthodoxy Chapter IV; Supplement Q1 scan review.
- Advent launches November 29: excerpt-to-source comparison, Substack and social readiness ([checklist](docs/ADVENT-LAUNCH.md)).
- Libraries research candidates need rights and provenance review before import. Paused: `_headers` Report-Only CSP, low-priority npm audit findings.
- Page-audit decisions: the publish allowlist and the `study/index.html` sitemap or noindex question. CI's Study drift check names the missing `study/passages` (harmless).
- Recover the evidence listed in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md); confirm backups and account responsibilities ([OPERATIONS](docs/OPERATIONS.md)).

## Reference map

- Rules: `docs/PROJECT-RULES.md` and `docs/ANALYTICS.md`. Technical reference: `docs/IMPLEMENTATION-NOTES.md`; history in `docs/archive/`; map in `docs/README.md`. Operations and approvals: `docs/OPERATIONS.md`.

When resuming: fetch `main`, inspect open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, checks run, known failures, and the next action.
