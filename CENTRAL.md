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

As of November 15, 2026, `main` at `ee33656ddd` (PR #32):

- 104 work records; 64 hosted editions of 59 works in `data/library.json`.
- 4,925 static pages and 4,926 sitemap URLs; about 6,750 tracked files, about 5,980 generated (`linguist-generated` in `.gitattributes`).
- Tests: 124 Node and 264 Python (with Story of a Soul).

## Standing owner decisions

- **Rule changes of November 14, 2026** (Micah's message pasted as the instruction "including every rule change below", items 1 to 5): the Gutenberg notice once per page after the text (wording decision, Micah's follow-up message the same day: the licence's own 1.E.1 sentence, verbatim), quality labels in edition details only, one-line affiliate disclosure, badges only on a record's own page, one-line Wikipedia credit and a Credits toggle for public-domain portraits, the standing approval below, and this file's cap. Recorded here once; the rules cite it as "owner rule change, November 14, 2026". Details: `docs/PROJECT-RULES.md` rules 2, 7, 10, 11, 14, and 15.
- **Standing approval:** presentation, docs, tests, and tooling may merge on green CI without Micah's review; his review is still required for new hosted texts, hosted-text wording, rights or licence statements, affiliate placements, analytics, hosting or DNS, takedown identity, and outreach ([OPERATIONS](docs/OPERATIONS.md#owner-decisions)).

## Handoff log

Newest first, 3 entries of at most 5 lines. Older entries: `git log -p -- CENTRAL.md`.

### 2026-11-15, Claude (Claude Code): Story of a Soul structured edition

- Structure from its own HTML (#16772) with accent-insensitive matching: 1,744 blocks, 11 chapters, headings; 144 of 145 HTML italics already underscored in the TXT, one added. Verse keeps its line breaks; notes stay plain. The gate also ignores line breaks next to "--" (2 blocks), comparison only; approved by Micah on November 15 ("Yes to the matching rule").
- [PR #30](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/30) squash-merged as `3d485831e7`; live `bc-1aa646a694a5` matches `main`. The EPUB CI job now runs on every pull request. Approval: Micah, November 14 and 15.

### 2026-11-15, Claude (Claude Code): Part D on Orthodoxy and covers

- Work page as a title page (facts line from the TXT, Read, Listen, Download, About this edition); on chapter pages the chapter opener replaces everything above the text, and it opens each chapter in the reader; chapter endings link the next chapter; book paragraphs with a drop cap; print starts each chapter on a new page. No characters change.
- Covers: Micah chose design C, "Banded" (November 15: "Banded (C) is the best looking cover page for the books"); applied to all 64 editions in [PR #32](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/32), squash-merged as `ee33656ddd`; live `/build.json` `bc-f707301463e0` matches `main`.
- [PR #31](https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/31) merged as `1f53e01cbf` (`bc-a962c8e3a225`), under the standing approval. Approval: Micah, November 14 (follow-up, item 4).

## Open items

- Micah: a hero engraving (three proposals in PR #27); the takedown agent's name, address, and email (page shows a PLACEHOLDER).
- Hosted texts: EPUBs are published for Orthodoxy and Story of a Soul (branch `claude/publish-epub`); manual proofread of Orthodoxy Chapter IV; Supplement Q1 scan review.
- Advent launches November 29: excerpt-to-source comparison, Substack and social readiness ([checklist](docs/ADVENT-LAUNCH.md)).
- Libraries research candidates need rights and provenance review before import. Paused: `_headers` Report-Only CSP, low-priority npm audit findings.
- Page-audit decisions: the publish allowlist and the `study/index.html` sitemap or noindex question. CI's Study drift check names the missing `study/passages` (harmless).
- Recover the evidence listed in the [repository audit](docs/REPOSITORY-AUDIT-2026-11-09.md); confirm backups and account responsibilities ([OPERATIONS](docs/OPERATIONS.md)).

## Reference map

- Rules: `docs/PROJECT-RULES.md` and `docs/ANALYTICS.md`. Technical reference: `docs/IMPLEMENTATION-NOTES.md`; history in `docs/archive/`; map in `docs/README.md`. Operations and approvals: `docs/OPERATIONS.md`.

When resuming: fetch `main`, inspect open PRs, record the task here, and reconcile conflicts before editing. End with changed paths, the commit or PR, checks run, known failures, and the next action.
