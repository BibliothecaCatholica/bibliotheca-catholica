# Repository material audit, November 9, 2026

Baseline: `757dacaab7fdaa9aeeeb267fb590db99ee40d760`, main checkout. Scope: tracked-file inventory and sizes, catalog/file integrity, contributor documentation, generators and CI, source evidence availability, and open PR metadata. This is not a line-by-line theological, legal, security, or textual collation of the corpus; no account dashboard or external research drive was inspected.

## Findings and disposition

| Priority | Observed finding | Action / material needed |
|---|---|---|
| High | AGENTS combined 80 KB of rules, architecture, dated changes, and old counts | Implemented short AGENTS plus CENTRAL; retained all original sections in PROJECT-RULES and IMPLEMENTATION-NOTES |
| High | README claimed no npm installation while CI installs dependencies and builds Study assets | Added correct setup and Study generation command to CONTRIBUTING and OPERATIONS; README wording remains a documented correction to avoid fingerprint-only regeneration of thousands of pages |
| High | Five cited external files are absent (table below) | Obtain actual artifacts or safe, durable source pointers; never reconstruct evidence from a narrative summary |
| High | Repository hosting notes call Cloudflare a mirror; owner reports production transition | Documented discrepancy; verify actual binding and DNS in owner-controlled systems before changing config |
| High | No independent backup or tested recovery evidence found in reviewed docs | Added backup/restore procedure; destination, schedule, and restore test remain owner work |
| High | Takedown template has a designated-agent PLACEHOLDER | Keep existing contact fallback; owner must supply actual decision and details, not an invented identity |
| Medium | LICENSING remains explicitly a draft | Preserve boundaries; owner resolves final wording separately, with all dependent surfaces updated together |
| Medium | Historical reviews and AGENTS page counts could mislead a new contributor | Marked October 22 review historical; moved current work to CENTRAL; use actual build/test output |
| Medium | No consolidated Advent publication-readiness checklist found | Added ADVENT-LAUNCH; external draft and schedule state remains unchecked |
| Medium | Live open PR #17 overlaps site integrations | Link it as dated observed work; do not merge or imply its features are on main |

## Measured inventory

At baseline: 6,362 tracked files, 243,244,030 bytes (about 232 MiB), excluding Git object history and dependencies. Largest tracked file is `data/open/isidore-index.json`, 6,319,819 bytes. File count is not a deployed-file count; deployment exclusions and host configuration need separate inspection. Historical ~9k-file claims and provider-cap estimates are not measurements of this checkout.

| Area | Tracked files | Decision |
|---|---:|---|
| `summa/` | 3,732 | Keep generated article/question pages: intentional deep links and static delivery |
| `pagefind/` | 969 | Keep generated pinned search output while current deploy serves committed assets |
| `author/` | 480 | Keep generated public entry pages |
| `saints/` | 415 | Keep calendar/profile pages built from approved sources |
| `data/` | 245 | Keep maintained inputs, generated bundles, approved texts, and source evidence |
| `work/` | 153 | Keep work, chapter, and story entry points |

Catalog inspection: 102 work records, 64 editions with `text`; all 64 files exist and match catalog SHA-256. There are 68 files directly under `data/sources/`. These checks establish file integrity against the catalog, not copyright clearance or transcription accuracy. Old Orthodoxy `pg-16769` artifacts are intentionally retained under the existing preservation rule; do not remove them as apparent orphans.

## Missing evidence and external inputs

These exact filenames were searched recursively and are absent. Their storage locations are not established by this audit.

| Missing input | What should be committed or documented |
|---|---|
| `summa-1947-collation-2026-11-09.md` | Recover the original sample report, witness IDs/pages, sample scope, findings, and reviewer/date; distinguish sample checking from a complete comparison |
| `qa/pageview-path-test-2026-11-09.md` | Sanitized hit-level QA procedure/results tied to tested commit; exclude identifiers and private traffic exports |
| `research/saints-pilot.json` | Approved, redistributable source snapshot or documented private location/schema/hash; current `data/saints.json` remains the committed build input |
| `metadata.db` | Prefer documented acquisition, schema, hash, and import procedure; do not upload a database or its files without review. Current books snapshots support normal builds |
| `hosting-classification.csv` | Recover classification evidence with provenance/date/hash, or record controlled location; existing rights snapshot supports ordinary regeneration without reclassification |

For every externally maintained input, record custodian, durable location, access method without credentials, checked date, checksum, license/reuse boundary, schema, generating command, and outputs. A missing-file marker is not a claim that the file never existed. Do not expand hosting permissions to make an import reproducible.

## What belongs here

Keep source code, generators, lockfiles, CI, regression tests, maintained catalog data, approved source snapshots/notices, exact text bytes/checksums, public editorial documentation, and generated assets required by the existing static deployment. Keep a small current handoff and dated reports with scope/commit evidence. Existing design screenshots document prior work; no evidence justifies removing them in this pass.

Add genuine missing research/QA evidence after privacy and redistribution review. Record asset origin/license, pinned upstream revision, and regeneration instructions for new integrations. Strengthen incremental content review with edition-specific completeness, translation, OCR uncertainty, source dates, and verified external access; do not interpret every imported Isidore row as reviewed.

Keep outside the public repository: personal offline ZIM/ZIP archives and video collections, unapproved scraped corpora, copyrighted source caches without permission, account credentials/recovery codes, private reader notes, billing/account exports, raw traffic logs, installed `node_modules`, temporary OCR/download caches, and independent backup bundles. Zimit is expressly a separate personal project. PR #17's recovery-tool description does not authorize publishing its recovered content.

No corpus files were deleted or reclassified by this documentation pass. The inventory supports targeted evidence recovery and operational verification, not indiscriminate cleanup of intentional generated output.

## Verification

Run the procedure in OPERATIONS and use this change's GitHub PR for executed command outcomes. Reproduce inventory with `git ls-files -z` (sum working-file sizes, excluding Git metadata), hosted editions with `data/library.json`, and page totals with `python3 tools/build_static.py`. Recheck open PRs live; the November 9 observation preceded this documentation PR.

## Validation handoff

PR #18: https://github.com/BibliothecaCatholica/bibliotheca-catholica/pull/18. Local validation passed 113 Node and 223 Python tests, all maintained browser-script syntax checks, catalog/static/Study builds, and whitespace checks. Static build reports 4,923 pages and 4,924 sitemap URLs. GitHub validation failed at the post-static-build drift check; the baseline build.json contains stale source hashes (including editorial-flags data and its generator). This documentation branch does not modify those sources. Resolve the baseline fingerprint/generated-page drift and rerun CI before merge. Cloudflare preview succeeded; production deployment is not claimed. Missing external evidence and dashboard settings remain unverified.
