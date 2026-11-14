# Shared project handoff

Read AGENTS.md and this file at session start. Read detailed references only for the task at hand. Update this file in place at handoff; keep under 150 lines. No separate dated report files for handoffs. No secrets, reader notes, or private account records here.

When an instruction file and the existing code disagree, follow the conventions in the code, and point out each mismatch in your final reply. Updated November 13, 2026 (America/Chicago), notes cleanup. This is the single living coordination file for every contributor (Grok bots, ChatGPT, Codex, Claude, and others).

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

GitHub repository `main` is the source of truth. Cloudflare Pages deploys automatically on push to `main` and serves https://bibliothecacatholica.com; every PR also gets a Cloudflare Pages preview check. The `CNAME` file stays. texts.bibliothecacatholica.com is served from the `bibliotheca-texts` repo. DNS and the Cloudflare zone belong to Business. Last confirmed November 9, 2026: the apex and `www` resolve to Cloudflare, and https://bibliothecacatholica.github.io/bibliotheca-catholica/ redirects to the custom domain. GitHub Pages was a fallback until the planned November 12 shutoff. November 13: whether the shutoff happened is still unverified; this session's proxy refused connections to both `bibliothecacatholica.github.io` and `bibliothecacatholica.com`, so neither host could be checked. Hosting was not changed.

## Verified snapshot

As of November 13, 2026, `main` at `80f3072284` (PR #23) plus this cleanup branch:

- 104 work records; 64 hosted editions of 59 works in `data/library.json`.
- 4,925 static pages and 4,926 sitemap URLs from `tools/build_static.py`; 6,389 tracked files, 5,923 of them generated and marked `linguist-generated` in `.gitattributes`.
- Tests: 115 Node and 231 Python.
- Landed: PRs #17 (as #23), #20, #21, and #22. Open: [PR #24](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/24), Orthodoxy structured-text and EPUB pilot, awaiting a decision.

## Handoff log

Newest first. Entry shape: date (America/Chicago), author, summary, commits/PRs, validation, and approval source. Open items are listed once below, not repeated in every entry. Older entries are in Git history: `git log -p -- CENTRAL.md`.

### 2026-11-13, Claude (Claude Code): notes cleanup and generated-output diff hygiene

- **Summary:** Cut session reading. CENTRAL.md keeps the three newest entries, this one included. The GA4 section of `docs/PROJECT-RULES.md` moved verbatim to `docs/ANALYTICS.md`; AGENTS.md rules 2 and 7 point to each. `docs/IMPLEMENTATION-NOTES.md` now states current behaviour in subsections by area; its previous full text is in `docs/archive/IMPLEMENTATION-HISTORY.md`. PROJECT-REVIEW, QUALITY-AUDIT, and VALIDATION moved to `docs/archive/`; `docs/STATUS.md` deleted; links and the docs map fixed. `.gitattributes` marks every builder output `linguist-generated=true` (static pages, data bundles, `pagefind/`, Study and Libraries bundles). `-diff` was tested and not added: the drift checks still fail correctly, but `git diff --check` stops checking generated files. AGENTS.md gives the source-only diff command. Sizes (lines/bytes, before to after): AGENTS 27/3,307 to 29/3,778; CENTRAL 129/16,809 to 77/11,590; PROJECT-RULES 76/32,329 to 51/20,351; ANALYTICS new, 30/12,322; IMPLEMENTATION-NOTES 126/46,784 to 136/48,493 (slightly larger, because it gained subsection headings and checked current facts, but a session now reads one subsection). Code and doc mismatches are listed in the PR.
- **Commits/PRs:** branch `claude/peaceful-keller-pp04tg`; see its PR.
- **Validation/status:** See the PR for the full procedure and results. No site output changed: docs are outside the `build.json` fingerprint, and README.md was left unedited so the build ID stays the same.
- **Approval:** Micah, November 12, 2026, pasted the cleanup brief as the instruction.

### 2026-11-13, Claude (Claude Code): PRs #20 and #17 landed

- **Summary:** Merged PR #20 (hosted-text inventory and Orthodoxy Chapter IV formatting pilot) after mobile QA. Rebuilt PR #17 (Great Libraries research desk and offline saints recovery tool) on current `main` as PR #23. Ported its sources unchanged: `tools/library_desk.py`, `src/libraries/`, `styles/library-desk.css`, `tools/recover_saints_archive.py`, the pinned `fuse.js` 7.1.0, the two Libraries resources (Open Library, plus Corpus Thomisticum under Libraries), and the CI drift check for `assets/libraries`. Resolved the `tools/build_static.py` conflict by keeping the TAN referral disclosure in the resource list and adding the desk above it. #17's AGENTS.md note moved to `docs/IMPLEMENTATION-NOTES.md`, since AGENTS.md now holds rules only. Corrected the Fuse.js license in `docs/LIBRARIES-AND-ARCHIVES.md` from MIT to Apache-2.0. Cache tokens `data/data.js?v=` and `app.js?v=` are `20261113-libraries`.
- **Commits/PRs:** [PR #20](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/20), squash-merged as [`56b71d0e8c`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/56b71d0e8cab26169de82cf7dfa0a59d243d65b9). [PR #23](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/23) replaces [PR #17](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/17), which is closed.
- **Validation/status:** #20: all GitHub checks passed. Chapter IV checked at iPhone 13 width in both themes: no overflow, Yeats lines set apart, both italic “if” words present, no script errors or missing files. #23: all three builds pass with no post-commit drift; 115 Node and 231 Python tests pass; the generated `assets/libraries/desk.js`, its license file, and `data/library-desk.js` are byte-identical to #17's. In a browser, `/libraries/` at desktop and phone, both themes: six research paths, the Fuse bundle loads, "intrnet archve" finds Internet Archive, the TAN referral link is intact, no overflow, no script errors. The desk sends no analytics events.
- **Approval:** Micah, November 13: "Main concern is the features and additions of each being #20 and #17 being on the website." The saints recovery tool keeps #17's November 9 owner authorization; recovered outputs stay outside the repository.

### 2026-11-13, Claude (Claude Code): cross logo

- **Summary:** Merged the Spanish Victory cross (PR #21) and followed up on small sizes. The cross with trefoil terminals replaces the plain cross in the shared header, the browser icon (`assets/favicon.svg`, replacing the inline data-URI icon), and the social preview (`tools/make_og_image.py` regenerates `assets/og-image.png`), in the existing burgundy, gold, and cream palette. The Alpha and Omega stay in the social preview image only: at the 32 px header and the 16 px tab icon they rendered as specks, so the follow-up removes them there. Also brought PR #20 up to date with this `main`.
- **Commits/PRs:** [PR #21](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/21), squash-merged as [`ef634a1c0b`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/ef634a1c0b35200d7fc3ecd971b906114a752c45). Follow-up on branch `claude/epic-franklin-hbdr1c`, which also carries this CENTRAL.md consolidation.
- **Validation/status:** PR #21 before merge: two `validate` runs and the Cloudflare Pages preview passed; local tests, library build, and static regeneration showed no drift; desktop and phone, both themes, no script errors. Follow-up: library, static, and Study builds pass; 113 Node and 228 Python tests pass; header and icon checked in a browser at 16, 32, and 64 px with no script errors. Live-site checks could not be run from this session (outbound proxy blocked); confirm the live build ID after merge.
- **Approval:** Micah in the current chat, November 13: "Merge #21," and "the Alpha and Omega at small sizes can be removed that is fine." The cross itself: Micah's November 12 request, recorded in PR #21's handoff, to use the cross throughout the website while retaining its existing colors.

## Open items

- Hosted-text quality: a manual proofread of Orthodoxy Chapter IV. Next editorial batches: the remaining Orthodoxy chapters one at a time; scan review of Supplement Q1 (three articles), including earlier automatic substitutions; then one Hopkins poem and its notes. PR #24 (Orthodoxy structured text and EPUB) awaits Micah's decision.
- Libraries research candidates in `docs/LIBRARIES-AND-ARCHIVES.md` (CRMEDR, Torch data, an opt-in Open Library edition finder) need rights and provenance review before any import.
- Advent launches November 29. Still to do from the [Advent launch checklist](docs/ADVENT-LAUNCH.md): excerpt-to-source comparison, and Substack and social readiness.
- The takedown page still shows "PLACEHOLDER: designated takedown agent." Micah to decide the name, postal address, and email.
- Confirm whether the November 12 GitHub Pages shutoff happened (unverifiable from cloud sessions; needs a check from an unrestricted network or the GitHub settings page). The `CNAME` file stays.
- CI's Study drift check names `study/passages`, which no longer exists; harmless, but the workflow could drop it.
- Paused: security headers (`_headers` Report-Only CSP) and low-priority npm audit findings.
- Page-audit decisions awaiting Micah: the publish allowlist, and the `study/index.html` sitemap or noindex question.
- Recover the missing evidence identified in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md). Do not fabricate reports.
- Confirm independent backups and account responsibilities using [OPERATIONS](docs/OPERATIONS.md).

## Reference map

- Rules: `docs/PROJECT-RULES.md` (content, rights, preservation) and `docs/ANALYTICS.md` (GA4). Technical reference by area: `docs/IMPLEMENTATION-NOTES.md`; history in `docs/archive/`. Map of all docs: `docs/README.md`.
- Operations, approvals, rollback, and accounts: `docs/OPERATIONS.md`. What belongs in Git: `docs/REPOSITORY-AUDIT-2026-11-09.md`. Public overview: `README.md`.

When resuming: fetch current `main`, inspect the working tree and open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, executed checks, known failures, and the next action.
