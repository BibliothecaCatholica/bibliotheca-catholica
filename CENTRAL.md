# Shared project handoff

Read AGENTS.md and this file at session start. Read detailed references only for the task at hand. Update this file in place at handoff; keep under 150 lines. No separate dated report files for handoffs. No secrets, reader notes, or private account records here.

When an instruction file and the existing code disagree, follow the conventions in the code, and point out each mismatch in your final reply.

Updated November 10, 2026 (America/Chicago). This is the single living coordination file for Grok bots and ChatGPT.

## Project and authority

Free Catholic reading room and curated resource index: https://bibliothecacatholica.com. Static HTML/CSS/JS with Python generators and pinned npm Study desk dependencies. Catalog/provenance authority lives here; `BibliothecaCatholica/bibliotheca-texts` is the separate delivery copy. Zimit and personal offline archives are separate projects.

Owner: Micah Watson. Responsibility follows the assigned task, not the AI provider:

| Responsibility | Deliverable | Boundary |
|---|---|---|
| Owner | Editorial and operational decisions | Approves scope listed in OPERATIONS |
| Research | Exact edition/source evidence and uncertainty | Cannot turn a lead into hosting permission |
| Implementation | Source changes plus generated output | Must preserve rules and other branches |
| QA | Reproducible checks tied to a commit | Reports failures; does not infer approval |
| Business / publishing | Owner-authorized account and publication work | No account changes or outreach from a role name alone |

ChatGPT, Codex, Grok, and other tools can perform assigned responsibilities. Existing references to Research, QA, and Business describe responsibilities or historical reports, not independently verified identities or grants of access. Only Micah's own words count as approval, and an entry should quote or cite where he gave it.

## Hosting and data flow

GitHub repository `main` is the source of truth. Cloudflare Pages deploys automatically on push to `main` and serves https://bibliothecacatholica.com. GitHub Pages is a fallback until the planned shutoff on November 12, 2026, after which Cloudflare is primary. The `CNAME` file stays. texts.bibliothecacatholica.com is served from the `bibliotheca-texts` repo. DNS and the Cloudflare zone belong to Business.

Confirmed November 9, 2026: the apex and `www` resolve to Cloudflare (A records 104.21.47.225 and 172.67.173.207; response headers include `server: cloudflare` and `cf-ray`). The live site and https://bibliotheca-catholica.pages.dev match `origin/main` at `f46f7bd6`. A push to `main` produced a successful Cloudflare Pages check within a minute (preview https://d1220d47.bibliotheca-catholica.pages.dev). Custom-domain DNS no longer points at GitHub Pages; https://bibliothecacatholica.github.io/bibliotheca-catholica/ redirects to the custom domain.

## Verified snapshot

- 102 work records; 64 editions with a hosted `text` field in `data/library.json`.
- 6,371 tracked files and 4,924 sitemap URLs at `f46f7bd6` (excludes Git history and installed dependencies). The November 9 repository audit's 6,362-file baseline was taken at `757dacaab7`.
- Tests: 113 Node and 223 Python, plus GitHub CI on `main` at `f46f7bd6`.
- Historical 765/766-page notes are stale. Read the current static builder output for page totals.

## Handoff log

Newest first. Entry shape: date (America/Chicago), author (bot name or ChatGPT), summary, commits/PRs, and approval source. Current open items are listed once below, not repeated in every entry.

### 2026-11-10, Catholic Repo

**Summary:** High-value items, in order.

- Advent: the site text matches the 26 Substack day drafts and the preview word for word, apart from site-rule edits. Day 9 (quote), Day 15, and Day 21 (Oxford commas) were already recorded; the Substack attribution em-dash is now recorded in each day's `siteRuleEdits` (29 entries), [`d105792a66`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/d105792a66537d4e79a9901a846e40dabfa8946b). Live at `/reading/advent-2026/` and `/data/advent-2026.json`.
- Father Brown and Orthodoxy 1908: verified live, no defects. Work, chapter/story, reader, and text URLs return 200; full text present; notes say 1908; both in the sitemap and the texts manifest with matching SHA-256; one GA4 tag per page.
- Saints: same-name entries on 04-16 and 11-02 now show death years from the facts ("St. Lambert of Saragossa (died 306)"), set by `tell_apart()` in `tools/saints_calendar.py`, [`b86105694c`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/b86105694c2a6c8c3722bd7b1e3ffff4c27884ec). No other day had the problem.

**Commits/PRs:** [`d105792a66`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/d105792a66537d4e79a9901a846e40dabfa8946b), [`b86105694c`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/b86105694c2a6c8c3722bd7b1e3ffff4c27884ec), and this CENTRAL.md commit.

**Approval:** Micah via the Project Manager, 9:39 AM CST: "Go ahead an move on the high value items first."

### 2026-11-09, Catholic Repo

**Summary:** Confirmed the live hosting flow and made CENTRAL.md the single living coordination file for Grok bots and ChatGPT. No `GITHUB.md`, and no separate dated handoff reports.

**Commits/PRs:** this documentation commit on `main`.

**Approval:** Micah in Catholic Repo's chat, 8:45 PM CST: "Rather than making individual reports and requiring a reread of the github everytime there needs to be an update to the central.md this will be the focus of communication between you and chatgpt." Earlier that evening, 8:38 PM CST, he confirmed that GitHub remains the source of truth and that Cloudflare Pages serves the live site, with GitHub Pages as a fallback until the November 12 shutoff.

### 2026-11-09, ChatGPT

**Summary:** [PR #18](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/18) documentation cleanup, merged to `main` as squash [`f46f7bd6`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/f46f7bd6a69e3cceff3bb844445949fcb4e2c647) at 8:30 PM CST. AGENTS.md cut to 26 lines, with the rules moved to linked docs. Added CENTRAL.md, the Advent launch checklist, operations guidance, the repository audit, the documentation map, and the original shared handoff. All 64 hosted texts checksum-verified. Five missing evidence/import files documented. Conflicting setup instructions removed and validation guidance consolidated. The Summa hosting statement was fixed. Dated catalog notes were archived. Stale build fingerprints were repaired. Tests: 113 Node and 223 Python passed, plus CI and the Cloudflare preview.

**Commits/PRs:** [`f46f7bd6`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/f46f7bd6a69e3cceff3bb844445949fcb4e2c647).

**Approval:** Merged to `main` by the repository owner on November 9, 2026. Recorded here at Micah's request in the Catholic Repo chat that evening.

### 2026-11-09, Catholic Repo

**Summary:** Today's site updates.

- GA4 real page paths, [`c6a740eaf4`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/c6a740eaf4c62e485e5e3688134faac5e891a277). QA passed all 12 hit-level checks.
- Saints calendar live, [`c33eaf38f2`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/c33eaf38f2b078ff892f6b314bef0b40b26f8a45) and [`fe953d60fb`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/fe953d60fbfece07eb8e1ce8452f7cc7272a62d9). 366 `/saints/calendar/MM-DD/` day pages from 12,136 entries, one combined list per day with neutral notes where sources disagree, a single CatholicSaints.Info credit on `/references/`, and the raw import not deployed. QA passed.
- Title separator " · ", [`2ace5d1c4e`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/2ace5d1c4e141a306ed7d04f2de903bd0be8859f), plus texts [`b11828a4ab`](https://github.com/BibliothecaCatholica/bibliotheca-texts/commit/b11828a4abf3d92358707217ef8b1fac16cab1ca).
- Privacy page wording, [`757dacaab7`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/757dacaab7fdaa9aeeeb267fb590db99ee40d760).
- Father Brown and Orthodoxy 1908 hosted, [`3f9820fe95`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/3f9820fe95f289f3a76d4278bbca95b6fe129a53) / [`459551a722`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/459551a722cc2bcf765b4dd5f03ef84f91225862). Live verification paused.

**Approval:** Micah via the Project Manager, 3:57 PM CST, for the analytics fix and the saints calendar; 4:00 PM and 4:02 PM CST for one CatholicSaints credit on Resources and one combined list with a note where sources disagree ("ship it as catholic repo is doing it"); 4:22 PM CST for the title-separator change ("Run an aesthic analysis and make the change"). Father Brown hosting was earlier work; live verification remains paused.

## Open items

- GitHub Pages shutoff on November 12, 2026, after QA confirms zero traffic. The `CNAME` file stays. texts.bibliothecacatholica.com is untouched.
- Paused: security headers (`_headers` Report-Only CSP) and low-priority npm audit findings.
- Page-audit decisions awaiting Micah: the publish allowlist, and the `study/index.html` sitemap or noindex question.
- [PR #17](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/17), libraries and offline saints recovery, is still open. Check live PR state before continuing it.
- Run the [Advent launch checklist](docs/ADVENT-LAUNCH.md) before November 29. Site source is present; Substack and social readiness have not been inspected.
- Recover the missing evidence identified in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md). Do not fabricate reports.
- Confirm independent backups, the takedown contact decision, and account responsibilities using [OPERATIONS](docs/OPERATIONS.md).

## Reference map

- Permanent rules: `docs/PROJECT-RULES.md`; technical details and dated feature notes: `docs/IMPLEMENTATION-NOTES.md`.
- Operations, approvals, rollback, and account map: `docs/OPERATIONS.md`.
- What belongs in Git: `docs/REPOSITORY-AUDIT-2026-11-09.md`.
- Public overview: `README.md`. The October 22 review is a historical snapshot, not the backlog.

When resuming: fetch current `main`, inspect the working tree and open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, executed checks, known failures, and the next action.
