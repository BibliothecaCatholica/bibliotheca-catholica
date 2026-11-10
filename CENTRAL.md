# Shared project handoff

Read AGENTS.md and this file at session start. Read detailed references only for the task at hand. Update this file at handoff; keep under 150 lines. No secrets, reader notes, or private account records here.

Updated November 9, 2026. Repository audit baseline: `757dacaab7fdaa9aeeeb267fb590db99ee40d760`. Counts are dated observations, not live counters.

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

ChatGPT, Codex, Grok, and other tools can perform assigned responsibilities. Existing references to Research, QA, and Business describe responsibilities or historical reports, not independently verified identities or grants of access.

## Verified snapshot

- 102 work records; 64 editions with a hosted `text` field in `data/library.json`.
- 6,362 tracked files, 243,244,030 tracked working-tree bytes at baseline (excludes Git history and installed dependencies).
- Read the current static builder output for page/sitemap totals and test output for test counts. Historical 765/766-page notes are stale.
- The repository still describes GitHub Pages production and a Cloudflare mirror. Owner reports a Cloudflare hosting transition; actual custom-domain bindings, DNS, and retirement schedule need dashboard verification. Preserve both configurations pending that verification.

## Active work and next actions

1. Review the cleaned documentation and refreshed output in PR #18; continue only from its latest validated commit.
2. Review existing [PR #17](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/17), libraries and offline saints recovery. Observed open November 9; not merged by this documentation task. Check live PR state before continuing it.
3. Run the [Advent launch checklist](docs/ADVENT-LAUNCH.md) before November 29. Site source is present; Substack/social readiness has not been inspected.
4. Recover the missing evidence identified in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md), with source locations, hashes, and review scope. Do not fabricate reports.
5. Confirm independent backups, takedown contact decision, account responsibilities, and production hosting using [OPERATIONS](docs/OPERATIONS.md).

## Handoff log

| Date | Contributor | Change and checks | Next / blockers |
|---|---|---|---|
| 2026-11-09 | Codex | Removed contradictory Summa/setup guidance; consolidated validation and archived catalog release notes | Required generated assets and package license notices retained |
| 2026-11-09 | Codex | Reconciled supplied draft with source, CI, tracked inventory, and open PR; separated entry instructions from retained detailed rules | See documentation PR for final validation; external evidence and dashboard state remain unverified |

## Reference map

- Permanent rules: `docs/PROJECT-RULES.md`; technical details and dated feature notes: `docs/IMPLEMENTATION-NOTES.md`.
- Operations, approvals, rollback, and account map: `docs/OPERATIONS.md`.
- What belongs in Git: `docs/REPOSITORY-AUDIT-2026-11-09.md`.
- Public overview: `README.md`. October 22 review is a historical snapshot, not the backlog.

When resuming: fetch current main, inspect working tree and open PRs, record task scope/branch here, and reconcile conflicts before editing. End with changed paths, commit/PR, executed checks, known failures, and next action. Archive older log rows when approaching the line limit.

## Validation handoff

[PR #18](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/18) contains the documentation cleanup and refreshed generated pages. The one-time refresh workflow passed catalog/static/Study builds, all 113 Node and 223 Python tests, and whitespace checks, then committed generated output and removed itself. The previous fingerprint drift is repaired. Required CI on the final commit must pass before merge. External evidence, dashboard settings, and publication schedules remain unverified.
