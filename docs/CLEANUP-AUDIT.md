# Cleanup audit (read only)

Round 9, Job 7 (November 24, 2026). **Audit only: nothing is deleted, closed, or rewritten.** Micah approves items by table and number; deletion happens in a later round, only for approved items.

Never proposed for removal: branches of open PRs, `feat/build-on-deploy-phase1`, `claude/dist-public-paths`, `main`, `CNAME`, `.well-known/atproto-did`, `google3b007babfa8923a4.html`, `data/advent-2026.json`, anything under `qa/`, HOLDS, and rights evidence.

How branches were checked: `git for-each-ref` on the remote (last commit date), the PR list (open and closed), and, for merged PRs, the squash commit on `main`. A squash-merged branch is never an ancestor of `main`, so "merged" here means its PR was merged.

## Table 1: branches

### bibliotheca-catholica

| # | Branch | Last commit | PR | Status | Proposal |
|---|---|---|---|---|---|
| 1.1 | `claude/host-fichter-james-laynez` | 2026-11-24 | #164 | merged | delete |
| 1.2 | `main` | 2026-11-23 | | default | keep |
| 1.3 | `claude/switch-runbook` | 2026-11-24 | #176 | open | keep (still needed) |
| 1.4 | `claude/host-meyer-selections` | 2026-11-24 | #163 | merged | delete |
| 1.5 | `claude/hotfix-conflict-markers` | 2026-11-23 | #175 | merged | delete |
| 1.6 | `claude/texts-hsts` | 2026-11-23 | #174 | open | keep (still needed (Micah decides HSTS)) |
| 1.7 | `claude/hand-pass-sheets` | 2026-11-23 | #159 | merged | delete |
| 1.8 | `claude/qa-lows-housekeeping` | 2026-11-23 | #171 | open | keep (still needed) |
| 1.9 | `claude/holds-rescore` | 2026-11-23 | #160 | open | keep (still needed) |
| 1.10 | `claude/verified-lexicon` | 2026-11-23 | #158 | merged | delete |
| 1.11 | `claude/walsh-teresa-hand-pass` | 2026-11-23 | #165 | open | keep (still needed) |
| 1.12 | `claude/host-meyer-irish-poetry` | 2026-11-23 | #154 | merged | delete |
| 1.13 | `claude/r2-inventory` | 2026-11-23 | #167 | open | keep (still needed; **delete after merge** (its earlier commits hold the Cloudflare account ID; squash-merge keeps them off main)) |
| 1.14 | `claude/texts-no-cname` | 2026-11-23 | #166 | merged | delete |
| 1.15 | `claude/gate-damage-proposal` | 2026-11-23 | #172 | open | keep (still needed) |
| 1.16 | `claude/furfey-1944-labels` | 2026-11-23 | #173 | open | keep (still needed) |
| 1.17 | `claude/ga-preview-gate` | 2026-11-23 | #170 | open | keep (still needed (held to Dec 27)) |
| 1.18 | `claude/weekly-link-check` | 2026-11-23 | #169 | open | keep (still needed) |
| 1.19 | `claude/r2-site-links` | 2026-11-23 | #168 | open | keep (still needed) |
| 1.20 | `claude/walsh-r2` | 2026-11-23 | #157 | open | keep (still needed) |
| 1.21 | `claude/verse-leaves-tool` | 2026-11-23 | #162 | merged | delete |
| 1.22 | `claude/host-cassidy-molders` | 2026-11-23 | #153 | merged | delete |
| 1.23 | `claude/host-furfey-mystery-of-iniquity` | 2026-11-23 | #152 | merged | delete |
| 1.24 | `claude/teaching-data` | 2026-11-23 | #161 | open | keep (still needed) |
| 1.25 | `claude/meyer-verse-ranges` | 2026-11-23 | #156 | merged | delete |
| 1.26 | `claude/irish-editions-scoping` | 2026-11-23 | #150 | open | keep (still needed) |
| 1.27 | `claude/unlimited-ocr-scaffold` | 2026-11-23 | #155 | open | keep (still needed) |
| 1.28 | `claude/docs-leftovers` | 2026-11-23 | #141 | open | keep (still needed) |
| 1.29 | `claude/host-grant-john-england` | 2026-11-23 | #149 | merged | delete |
| 1.30 | `claude/holds-read-gate-scores` | 2026-11-23 | #148 | merged | delete |
| 1.31 | `claude/chesterton-what-i-saw` | 2026-11-23 | #146 | open | keep (still needed) |
| 1.32 | `claude/chesterton-polish-9` | 2026-11-23 | #145 | open | keep (still needed) |
| 1.33 | `claude/chesterton-polish-8` | 2026-11-23 | #144 | open | keep (still needed) |
| 1.34 | `claude/read-gate-process` | 2026-11-23 | #143 | merged | delete |
| 1.35 | `claude/ocr-setup-script` | 2026-11-23 | #151 | open | keep (still needed) |
| 1.36 | `claude/site-sweep-2026-11` | 2026-11-23 | #147 | open | keep (still needed) |
| 1.37 | `claude/chesterton-polish-7` | 2026-11-23 | #142 | open | keep (still needed) |
| 1.38 | `claude/dist-public-paths` | 2026-11-23 | #138 | open | keep (still needed (protected: build-on-deploy)) |
| 1.39 | `feat/build-on-deploy-phase1` | 2026-11-23 | #135 | open | keep (still needed (protected: build-on-deploy)) |
| 1.40 | `claude/chesterton-polish-6` | 2026-11-23 | #140 | merged | delete |
| 1.41 | `claude/walsh-high-points` | 2026-11-23 | #139 | merged | delete |
| 1.42 | `claude/docs-cleanup-nov22` | 2026-11-23 | #136 | merged | delete |
| 1.43 | `claude/faustula-holds` | 2026-11-22 | #137 | merged | delete |
| 1.44 | `draft-saints-calendar-2026-11-21` | 2026-11-21 | #130 | merged | delete |
| 1.45 | `claude/bibliotheca-catholica-network-pass-q5unrj` | 2026-11-21 | #107 | merged | delete |
| 1.46 | `feat/magisterium-disclosure-saint-of-the-day` | 2026-11-21 | #129 | merged | delete |
| 1.47 | `host-jerome-isaiah-prologue` | 2026-11-21 | #132 | merged | delete |
| 1.48 | `host-thackeray-eulalia` | 2026-11-21 | #131 | merged | delete |

### bibliotheca-texts

| # | Branch | Last commit | PR | Status | Proposal |
|---|---|---|---|---|---|
| 1.T1 | `claude/export-cassidy-2026-11` | 2026-11-23 | texts #7 | merged | delete |
| 1.T2 | `claude/export-furfey-2026-11` | 2026-11-23 | texts #6 | merged | delete |
| 1.T3 | `claude/export-grant-2026-11` | 2026-11-23 | texts #5 | merged | delete |
| 1.T4 | `claude/re-export-2026-11-23` | 2026-11-23 | texts #4 | merged | delete |
| 1.T5 | `claude/export-meyer-fichter-2026-11` | 2026-11-24 | texts #8 | merged | delete |
| 1.T6 | `claude/sweet-goldberg-yrlrud` | 2026-11-15 | texts #1 (closed, not merged) | superseded by the later full re-exports (#2 to #8) | delete |
| 1.T7 | `deep-link-gaps` | 2026-11-09 | none | not merged by PR; superseded: every later export rewrites manifest.json (verify against texts history before deleting) | delete after check |
| 1.T8 | `deep-link-gaps-summa` | 2026-11-09 | none | not merged by PR; superseded as above (Summa rights notes now come from the catalogue) | delete after check |
| 1.T9 | `main` | 2026-11-24 |  | default | keep |

## Table 2: open PRs

| # | PR | Head (Nov 24) | Proposal | Reason |
|---|---|---|---|---|
| 2.1 | #176 switch runbook | `2ef0b92c76` | merge after QA | docs only (Job E) |
| 2.2 | #174 texts HSTS (max-age=300) | `3049cbf2f5` | keep | Micah decides HSTS; stacked on #171 |
| 2.3 | #173 Furfey 1944 labels | `2b9a1b19b3` | merge | QA PASS; work date fix rides with the restack |
| 2.4 | #172 gate-damage proposal | `008686d719` | merge | QA PASS; proposal doc and analysis tool only, no rule change |
| 2.5 | #171 QA lows (minus HSTS) | restacked | merge | QA PASS; restacked on #166 |
| 2.6 | #170 GA loader gate | `083961d803` | keep until Dec 27, then merge | QA PASS; touches the Advent page head |
| 2.7 | #169 weekly link check | `b87371d11d` | merge | QA PASS |
| 2.8 | #168 R2 site links | `3330d30d5d` | merge after #167 | waits for #167 |
| 2.9 | #167 R2 inventory and tools | `9b21f1c2ed` | merge after a fresh QA PASS | security fix pushed; then delete its branch |
| 2.10 | #165 Teresa partial hand pass | `083ddb3413` | merge as a record, or keep for the rest of the hand pass | QA PASS (not hosted, below gate) |
| 2.11 | #161 Related Church teaching data | `152345efdb` | merge | QA PASS (round 6); affiliate placement approved |
| 2.12 | #160 HOLDS scores | `8ab50f670d` | merge after QA | Plummer 95.10% recorded; Reeves unconfirmed |
| 2.13 | #157 Walsh `-r2` | `ea232c96c7` | merge | QA PASS ("Micah-only") |
| 2.14 | #155 Unlimited-OCR scaffold | `ec015297a0` | keep | off by default; not reviewed |
| 2.15 | #151 `tools/setup-ocr.sh` | `8e95342132` | merge after QA, or close | the environment's setup script now installs Tesseract; the script still helps local runs |
| 2.16 | #150 Irish editions scoping | `6b5142ed8b` | close as superseded | Meyer is hosted (#163) and #160 carries the Plummer and Reeves scores |
| 2.17 | #147 site sweep | `3c5fb36bdd` | re-review | findings from Nov 22; several fixed since (#171) |
| 2.18 | #146, #145, #144, #142 Chesterton polish | various | keep, restack, QA | still needed (HOLDS: unstructured editions) |
| 2.19 | #141 docs leftovers | `74f7be6360` | keep, restack | parts overlap #166 and #171 (README and SECURITY hosting lines) |
| 2.20 | #138, #135 build-on-deploy | `8ae7b798d0`, `48230bb779` | keep | protected; the switch waits for Dec 27 and Micah's go |

## Table 3: files

Checked with `git grep` across tracked sources (generated pages, `pagefind/`, and `build.json` fingerprints left out), `package.json` scripts, the CI workflows, and the build chain in `tools/validate.sh`.

| # | Path | Size | Reason | How checked | Proposal |
|---|---|---|---|---|---|
| 3.1 | `tools/build_v4_data.py` | 5.9 KB | old data builder, not in `npm run build` | referenced only by `build.json`'s fingerprint list | delete after confirming its outputs are no longer regenerated by anyone |
| 3.2 | `tools/build_v6_data.py` | 12.1 KB | same | same | same |
| 3.3 | `tools/fetch_qids.py` | 2.4 KB | one-time Wikidata fetch | `build.json` only | delete |
| 3.4 | `tools/verify_text_archive.py` | 2.0 KB | superseded by `tests/test_text_archive.py` | `build.json` and one archived review only | delete |
| 3.5 | `tools/make_og_image.py` | 2.6 KB | makes `assets/og-image.png` (a preserved file) | `build.json` only | **keep** (needed to regenerate the OG image) |
| 3.6 | `docs/link-health.json`, `docs/link-health.md` | 1.18 MB | Nov 20 one-off report; #169's weekly run reports in an issue and an artifact | `docs/README.md` lists it; `tools/check_links.py` default path | delete after #169 merges, and point the default at a temp path |
| 3.7 | `docs/collection-audit.json` | 741 KB | Nov 9 audit snapshot | `docs/COLLECTION-REVIEW.md` and `docs/README.md` cite it | move to R2 `research/` (or delete) and update the two docs |
| 3.8 | `docs/research/magisterium-placements-2026-11/*.png` | 3.2 MB | review screenshots | no references outside the folder | move to R2 `research/` with a checksum list (migration plan step 3) |
| 3.9 | `docs/research/presentation-consistency-2026-11/*.png` | 1.6 MB | review screenshots | no references | same |
| 3.10 | `docs/research/orthodoxy-flow-batch-{1..4}-2026-11/*.png` | about 2 MB | review screenshots | no references | same |
| 3.11 | `docs/research/dore-headers-2026-11/built/*` | 0.4 MB | review renders | no references | same |
| 3.12 | `docs/research/design-refresh-2026-11/**/*.png` | 7.6 MB | design review screenshots | cited by 2 docs | move to R2 `research/` and keep the doc links working |
| 3.13 | `downloads/epub/*.epub` | 27.8 MB | R2 copies after batch 1 | built by `tools/build_epub.py`; linked by work pages | only after R2 batch 1 and migration plan step 2 (redirects), not before |

Not proposed: `data/texts/`, `data/sources/` (including `pdf-prints/`), site assets, `docs/archive/` (75 KB of history), HOLDS, and rights evidence. No duplicate scans are tracked in git; the duplicate Schroeder upload is excluded in the R2 manifest.
