# Shared project handoff

Read AGENTS.md and this file at session start. Read detailed references only for the task at hand. Update this file in place at handoff; keep under 150 lines. No separate dated report files for handoffs. No secrets, reader notes, or private account records here.

When an instruction file and the existing code disagree, follow the conventions in the code, and point out each mismatch in your final reply.

Updated November 13, 2026 (America/Chicago), design pass part 1. This is the single living coordination file for every contributor (Grok bots, ChatGPT, Codex, Claude, and others).

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

Any tool can perform an assigned responsibility. References to Research, QA, and Business describe responsibilities or historical reports, not verified identities or grants of access. Only Micah's own words count as approval, and an entry should quote or cite where he gave it.

## Hosting and data flow

GitHub repository `main` is the source of truth. Cloudflare Pages deploys automatically on push to `main` and serves https://bibliothecacatholica.com; every PR also gets a Cloudflare Pages preview check. The `CNAME` file stays. texts.bibliothecacatholica.com is served from the `bibliotheca-texts` repo. DNS and the Cloudflare zone belong to Business.

Last confirmed November 9, 2026: the apex and `www` resolve to Cloudflare, and https://bibliothecacatholica.github.io/bibliotheca-catholica/ redirects to the custom domain. GitHub Pages was a fallback until the planned November 12 shutoff; completion of that shutoff has not been recorded here.

## Verified snapshot

As of November 13, 2026, with PRs #20 and #23:

- 104 work records; 64 hosted editions of 59 works in `data/library.json`.
- 4,925 static pages and 4,926 sitemap URLs from `tools/build_static.py`; about 6,370 tracked files.
- Tests: 119 Node and 231 Python (4 Node design-budget tests added in the design pass).
- Historical 765/766-page notes are stale. Read the current static builder output for page totals.

## Handoff log

Newest first. Entry shape: date (America/Chicago), author, summary, commits/PRs, validation, and approval source. Open items are listed once below, not repeated in every entry.

### 2026-11-13, Claude (Claude Code): design pass, part 1 (Steps 0, 1, 5, 6)

**Summary:** First of two PRs for the owner's "calm, high-class library" brief. Added `docs/DESIGN.md` (type, three control styles, containers, notices) and a pointer in AGENTS.md. Trimmed notices: the footer FTC paragraph is gone (the FTC line stays beside every affiliate block, plus `/disclosure/` and its footer link); the newsletter pitch appears once per page (footer only; the home and Advent sign-up boxes keep the embed and the Substack privacy line); site-wide caveats ("dates are distinct", "files are served by the original library", library-copy holdings, reader sections) moved to `/about/` ("Dates, files, and sections"); the home and library "not endorsement" caveats removed from primary surfaces (kept on `/policy/`, `/about/`, `/disclosure/`, and in context notes). Work page (app): title, author, one sentence, one filled "Read here", chapters, one summary row per edition with "Source and rights details" behind a disclosure, then "Other ways to read" rows (Listen, Download, Buy in print, Find in a library) as text links. Purchase block heading is now "Buy in print", with text links. Reader: compact head, one quiet toolbar (Contents, Aa, Notes, Find, Print, Listen, ?), settings in the "Aa" menu with the same control IDs and storage keys, and Gutenberg, source, and formatting notices at the end of every section. The header Support pill is now a text link. Cache tokens `20261113-design`. Home, navigation, portraits, catalogue shelves, and the CSS consolidation are part 2.

**Validation/status:** Three builds pass; 119 Node and 231 Python tests pass; post-commit rebuild shows no drift. Budgets (tests/design-budgets.test.js): every one of 104 work pages has at most one filled button and at most six buttons, and no bordered card inside a bordered panel. Reader first paragraph at 361 px of an 800 px viewport (1280 wide) and 374 px of 787 px visible (390 wide, above the mobile bar), both themes. CSS 136,183 bytes before, 136,184 after.

**Approval:** Micah, November 12, 2026, approved the hero art, the one-line Today panel, portraits of the saints, and trimming the disclosures, and pasted the design-pass brief as the instruction.

### 2026-11-13, Claude (Claude Code): PRs #20 and #17 landed

**Summary:** Merged PR #20 (hosted-text inventory and Orthodoxy Chapter IV formatting pilot) after mobile QA. Rebuilt PR #17 (Great Libraries research desk and offline saints recovery tool) on current `main` as PR #23. Ported its sources unchanged: `tools/library_desk.py`, `src/libraries/`, `styles/library-desk.css`, `tools/recover_saints_archive.py`, the pinned `fuse.js` 7.1.0, the two Libraries resources (Open Library, plus Corpus Thomisticum under Libraries), and the CI drift check for `assets/libraries`. Resolved the `tools/build_static.py` conflict by keeping the TAN referral disclosure in the resource list and adding the desk above it. #17's AGENTS.md note moved to `docs/IMPLEMENTATION-NOTES.md`, since AGENTS.md now holds rules only. Corrected the Fuse.js license in `docs/LIBRARIES-AND-ARCHIVES.md` from MIT to Apache-2.0. Cache tokens `data/data.js?v=` and `app.js?v=` are `20261113-libraries`.

**Commits/PRs:** [PR #20](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/20), squash-merged as [`56b71d0e8c`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/56b71d0e8cab26169de82cf7dfa0a59d243d65b9). [PR #23](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/23) replaces [PR #17](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/17), which is closed.

**Validation/status:** #20: all GitHub checks passed. Chapter IV checked at iPhone 13 width in both themes: no overflow, Yeats lines set apart, both italic “if” words present, no script errors or missing files. #23: all three builds pass with no post-commit drift; 115 Node and 231 Python tests pass; the generated `assets/libraries/desk.js`, its license file, and `data/library-desk.js` are byte-identical to #17's. In a browser, `/libraries/` at desktop and phone, both themes: six research paths, the Fuse bundle loads, "intrnet archve" finds Internet Archive, the TAN referral link is intact, no overflow, no script errors. The desk sends no analytics events.

**Approval:** Micah, November 13: "Main concern is the features and additions of each being #20 and #17 being on the website." The saints recovery tool keeps #17's November 9 owner authorization; recovered outputs stay outside the repository.

### 2026-11-13, Claude (Claude Code): cross logo

**Summary:** Merged the Spanish Victory cross (PR #21) and followed up on small sizes. The cross with trefoil terminals replaces the plain cross in the shared header, the browser icon (`assets/favicon.svg`, replacing the inline data-URI icon), and the social preview (`tools/make_og_image.py` regenerates `assets/og-image.png`), in the existing burgundy, gold, and cream palette. The Alpha and Omega stay in the social preview image only: at the 32 px header and the 16 px tab icon they rendered as specks, so the follow-up removes them there. Also brought PR #20 up to date with this `main`.

**Commits/PRs:** [PR #21](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/21), squash-merged as [`ef634a1c0b`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/ef634a1c0b35200d7fc3ecd971b906114a752c45). Follow-up on branch `claude/epic-franklin-hbdr1c`, which also carries this CENTRAL.md consolidation.

**Validation/status:** PR #21 before merge: two `validate` runs and the Cloudflare Pages preview passed; local tests, library build, and static regeneration showed no drift; desktop and phone, both themes, no script errors. Follow-up: library, static, and Study builds pass; 113 Node and 228 Python tests pass; header and icon checked in a browser at 16, 32, and 64 px with no script errors. Live-site checks could not be run from this session (outbound proxy blocked); confirm the live build ID after merge.

**Approval:** Micah in the current chat, November 13: "Merge #21," and "the Alpha and Omega at small sizes can be removed that is fine." The cross itself: Micah's November 12 request, recorded in PR #21's handoff, to use the cross throughout the website while retaining its existing colors.

### 2026-11-12, ChatGPT

**Summary:** Hosted-text quality inventory and a first faithful-formatting pilot. The hosted scope is 59 works in 64 local editions, distinct from the 104 selected work records and the external Isidore index; see the [inventory](docs/HOSTED-TEXT-INVENTORY.md) and [editorial assessment](docs/HOSTED-TEXT-QUALITY.md). Added opt-in, checksum-bound layout support. Ordinary hosted Orthodoxy Chapter IV now reflows its prose, shows the Yeats quotation in two lines, and restores two italic “if” words, each verified against the 1909 John Lane printing, p. 99 (Internet Archive `orthodoxy1909ches`, leaf n106). The provenance record lists the pilot scope and zero wording corrections. Orthodoxy and Incredulity verification notes now distinguish automated OCR comparison from manual proofreading. All 64 original TXT files and hashes are unchanged; no imports, no text-mirror changes, and the separate illuminated Orthodoxy prototype is untouched.

**Commits/PRs:** [PR #20](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/20), source commit `624db3ee16`. Brought up to date with `main` (PR #21 and the small-logo follow-up) on November 13 by Claude.

**Validation/status:** Python and browser renderers match the full Orthodoxy text character by character; all 34 chapter body blocks retained in order, anchors unchanged. 113 Node and 231 Python tests pass; library, static, and Study builds pass with no post-commit drift; all 64 originals checksum-match. Browser checks: the chapter in light mode and the section reader in dark mode. Mobile QA and manual whole-chapter proofreading are outstanding.

**Approval:** Micah's November 12 request to inventory hosted works and carry out an initial faithful cleanup. No permission inferred for external imports, mirroring, or the separate illustrated site.

### 2026-11-11, Catholic Repo

**Summary:** Replaced the plain TAN Books link on `/libraries/` with the existing LeadDyno referral link `https://lddy.no/1qbrw`, link text "Browse TAN Books ↗", with `rel="noopener sponsored"` and the FTC disclosure in `<main>`, on both the static page and in the app. Cache tokens: `data/data.js?v=` and `app.js?v=` are `20261111-tan-libraries`. Added one libraries-page test.

**Commits/PRs:** [`4165841b42`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/4165841b42341dd1271cd485bd78b1d33b607d85).

**Validation/status:** All five GitHub check runs passed. Verified live at 8:22 AM CST.

**Approval:** Micah in Catholic Repo's chat, 8:13 AM CST November 11: "Yes, add the TAN affiliate link today."

### 2026-11-10, ChatGPT

**Summary:** Owner-requested feedback: reduced homepage and navigation clutter; shared plain/interactive landing copy; added seven source resources, two link-only Mind of the Church work records, and an Acta source panel on the hagiography shelf. Collection evidence and rights/translation limits are in `data/sources/translation-collections.json` and `docs/COLLECTION-REVIEW.md`. Fixed the Isidore test helper's function parsing. Modern translations remain at source under the existing selection policy.

**Commits/PRs:** [PR #19](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/19), merged as [`67ca66a2cc`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/67ca66a2cc).

**Backlink prepared, not sent:** Name: Bibliotheca Catholica. URL: https://bibliothecacatholica.com/. Description: “A free Catholic reading room and curated guide to authors, saints, Church documents, and digital libraries, with source editions and rights notes.” Intended listing: https://mindofthechurch.com/fellows/. No outreach sent; no backlink claimed.

**Validation/status:** Tests and all three builds passed; home checked in both themes. Physical-device testing was not performed.

**Approval:** Micah in ChatGPT's chat: “Run through everything on the github and make the stated corrections as you just pointed out,” with everything except sending an email authorized.

### 2026-11-10, Catholic Repo

**Summary:** Reworded the /about/ reprint example to a generic "1952 reprint of a 1920 book," removed the unlinked old Orthodoxy file `data/texts/pg-16769.txt`, and bumped `scripts/analytics.js?v=` to `20261110-title-separator`. A cached copy of the removed file may answer the bare production URL until its `s-maxage=604800` expires or the cache is purged. Advent: site text matches the 26 Substack day drafts apart from recorded site-rule edits (29 `siteRuleEdits` entries). Father Brown and Orthodoxy 1908 verified live. Same-name saints on 04-16 and 11-02 now show death years, set by `tell_apart()` in `tools/saints_calendar.py`.

**Commits/PRs:** [`187d73f7e3`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/187d73f7e391011df58f45d8906d8b1407d4ef21), [`d105792a66`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/d105792a66537d4e79a9901a846e40dabfa8946b), [`b86105694c`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/b86105694c2a6c8c3722bd7b1e3ffff4c27884ec).

**Approval:** Micah via the Project Manager, 9:39 AM CST ("Go ahead an move on the high value items first") and 10:23 AM CST, November 10.

### 2026-11-09, ChatGPT and Catholic Repo

**Summary:** [PR #18](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/18) documentation cleanup, squash-merged as [`f46f7bd6`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/f46f7bd6a69e3cceff3bb844445949fcb4e2c647): AGENTS.md cut to its rules with details in linked docs; added this file, the Advent launch checklist, operations guidance, and the repository audit; all 64 hosted texts checksum-verified; five missing evidence/import files documented. CENTRAL.md became the single coordination file, with no `GITHUB.md` and no dated handoff reports. Same day, live: GA4 real page paths ([`c6a740eaf4`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/c6a740eaf4c62e485e5e3688134faac5e891a277)); the saints calendar, 366 day pages from 12,136 entries with one CatholicSaints.Info credit on `/references/` ([`c33eaf38f2`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/c33eaf38f2b078ff892f6b314bef0b40b26f8a45), [`fe953d60fb`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/fe953d60fbfece07eb8e1ce8452f7cc7272a62d9)); the " · " title separator ([`2ace5d1c4e`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/2ace5d1c4e141a306ed7d04f2de903bd0be8859f)); privacy wording ([`757dacaab7`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/757dacaab7fdaa9aeeeb267fb590db99ee40d760)); and Father Brown and Orthodoxy 1908 hosted ([`3f9820fe95`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/3f9820fe95f289f3a76d4278bbca95b6fe129a53), [`459551a722`](https://github.com/BibliothecaCatholica/bibliotheca-catholica/commit/459551a722cc2bcf765b4dd5f03ef84f91225862)).

**Approval:** PR #18 merged by the repository owner, November 9. Micah in Catholic Repo's chat, 8:45 PM CST: CENTRAL.md "will be the focus of communication between you and chatgpt"; 8:38 PM CST: GitHub stays the source of truth with Cloudflare Pages serving the site. Via the Project Manager: 3:57 PM CST (analytics, saints calendar), 4:00 and 4:02 PM CST (one credit, one combined list), 4:22 PM CST (title separator).

## Open items

- Design pass part 2 (Steps 2, 3, 4, 7, 8 of the November 12 brief): portraits, home, navigation, catalogue shelves, CSS consolidation; the owner chooses one of three proposed hero engravings and decides on portrait self-hosting.
- Hosted-text quality: a manual proofread of Orthodoxy Chapter IV. Next editorial batches: the remaining Orthodoxy chapters one at a time; scan review of Supplement Q1 (three articles), including earlier automatic substitutions; then one Hopkins poem and its notes.
- Libraries research candidates in `docs/LIBRARIES-AND-ARCHIVES.md` (CRMEDR, Torch data, an opt-in Open Library edition finder) need rights and provenance review before any import.
- Advent launches November 29. `data/advent-2026.json` checked November 13: 26 days, November 29 to December 24, weekdays and 2026 liturgical labels correct, no em-dashes or empty fields, all links resolve to catalog works. Still to do from the [Advent launch checklist](docs/ADVENT-LAUNCH.md): excerpt-to-source comparison, and Substack and social readiness.
- The takedown page still shows "PLACEHOLDER: designated takedown agent." Micah to decide the name, postal address, and email.
- Record whether the November 12 GitHub Pages shutoff happened. The `CNAME` file stays; texts.bibliothecacatholica.com is untouched.
- Paused: security headers (`_headers` Report-Only CSP) and low-priority npm audit findings.
- Page-audit decisions awaiting Micah: the publish allowlist, and the `study/index.html` sitemap or noindex question.
- Recover the missing evidence identified in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md). Do not fabricate reports.
- Confirm independent backups and account responsibilities using [OPERATIONS](docs/OPERATIONS.md).

## Reference map

- Permanent rules: `docs/PROJECT-RULES.md`; technical details and dated feature notes: `docs/IMPLEMENTATION-NOTES.md`.
- Operations, approvals, rollback, and account map: `docs/OPERATIONS.md`.
- What belongs in Git: `docs/REPOSITORY-AUDIT-2026-11-09.md`.
- Public overview: `README.md`. The October 22 review is a historical snapshot, not the backlog.

When resuming: fetch current `main`, inspect the working tree and open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, executed checks, known failures, and the next action.
