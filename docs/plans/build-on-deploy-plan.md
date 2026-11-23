# Build on deploy: stop committing generated pages (plan, revised November 22, 2026)

Status: Phase 1 is draft PR #135 (`tools/deploy_build.sh`, `tools/assemble_dist.py`, `tools/compare_tree.py`, templates moved to `tools/templates/`, disk-based tests). Phase 2 prep (dist/ ships only public paths) is a draft PR stacked on #135. Nothing has changed in Cloudflare, and no generated page has been removed. Target switch: about December 26, 2026, after the Advent freeze.

**Why.** `main` tracks 9,132 files (`bff50fcb6e`, after #130), most of them generated (`linguist-generated` in `.gitattributes`), including about 6,000 `index.html` pages. Every source change rewrites the build ID in every page footer, so open PRs conflict and need rebuilding ("Merge main … and rebuild" commits before #131, #132, and #133).

## 1. What Cloudflare must run

- **Build command:** `bash tools/deploy_build.sh` (Phase 1): `npm ci`, `npm run build`, `python3 tools/build_static.py`, `npm run build:study`, then `python3 tools/assemble_dist.py`.
- **Output directory:** `dist/` (ignored by git). Serving the repository root after `npm ci` would also upload `node_modules`.
- **Versions:** CI runs Node 22 and Python 3.12 (`.github/workflows/validate.yml`). QA's fresh-clone check on Node 24 and Python 3.13 produced the same hashes. Pin `NODE_VERSION=22` and `PYTHON_VERSION=3.12` in the Pages settings, or in `.node-version` and `.python-version`, and confirm both in the first build log.
- **Dependencies:**
  - Python: the standard library only. The 38 modules the build reaches import nothing third-party.
  - Node: `package-lock.json` (esbuild 0.28.2, pagefind 1.6.0, mirador 4.3.0, fuse.js 7.5.0, citation-js 0.9.0, bible-passage-reference-parser 4.0.0).
- **Network:** the build is *not* network-free. `npm ci` downloads the packages, including Pagefind's platform binary, from the npm registry. After install, the build itself fetches nothing. The one network path in the Python build, `build_v3_data.py`'s feed fetch, is skipped by `--catalog-only`.
- **Local-only inputs (none block the build):**
  - Covers need Playwright, but `assets/covers/` is committed.
  - `.local/saints-calendar.json` is only the raw import; day pages come from the committed `data/saints-days.json`.
  - EPUBCheck (Java) runs only in the `epub-pilot` workflow.
- **Time:** about 2 minutes (build about 50 s, static 10 s, study 50 s).
- **Build ID:** `tools/build_info.py` hashes the inputs, with no git SHA or clock, so a deploy build of a commit gives the same `build.json` `id` as a local build.

## 2. Files that must ship unchanged

| File | After the switch |
|---|---|
| `CNAME`, `.nojekyll`, `.well-known/atproto-did`, `google3b007babfa8923a4.html`, `_headers` (the #83 CSP and security headers, and `*.pages.dev` noindex) | Committed; copied as-is into `dist/` |
| `sitemap.xml` (5,968 URLs on `main`), `robots.txt`, `404.html`, `build.json` | Written by `build_static.py` at deploy |
| `/drafts/` (`noindex,nofollow`, `Disallow: /drafts/`, not in the sitemap) | Written by `build_drafts.py`; `tests/test_drafts.py` guards it |
| `index.html`, `study/index.html` | Built from `tools/templates/index.html` and `tools/templates/study/index.html` (moved in Phase 1) |
| `data/texts/`, `assets/`, `fonts/`, `downloads/epub/`, the data bundles | Stay committed in this phase |

`/design-preview/` no longer exists: it was removed in #69, so `/drafts/` is the only noindexed area.

## 3. Analytics

There is no change. The single GA4 tag (`G-HFG445Y1LT`) and the `scripts/analytics.js?v=20261121-hash-route` token live in `tools/templates/index.html`, and every page is cut from it. `ga_tag()` in `build_static.py` asserts exactly one tag, and `tests/test_analytics.py` checks every built `*.html`. No events are added.

Phase 1 had to exclude `dist/` (and `tools/templates/`) from the scans in `tests/test_analytics.py` and `tests/test_social_links.py`. Otherwise the assembled copy and the template sources would be counted as extra pages.

## 4. Proving the deploy output matches today

1. In a fresh clone of the commit, record SHA-256s of the committed files that ship (the public paths in section 5).
2. Delete every generated file (`linguist-generated`, plus `index.html` and `study/index.html`), run `tools/deploy_build.sh`, and hash `dist/`.
3. `python3 tools/compare_tree.py committed.sha dist/` must report zero missing, extra, or changed files.
4. Repeat against the Cloudflare preview: fetch every sitemap URL and the root files, compare body hashes, and check the CSP header and the `pages.dev` noindex header.

## 5. Which paths ship (Phase 2 prep)

`tools/assemble_dist.py` copies only public site paths, chosen by `is_public()`:

| Ships | Why |
|---|---|
| Root: `index.html`, `404.html`, `app.js`, `styles.css`, `sitemap.xml`, `robots.txt`, `build.json`, `CNAME`, `.nojekyll`, `_headers`, `google3b007babfa8923a4.html`, `.well-known/` | The site shell, crawl files, host and verification files |
| Every route directory in `docs/static-pages.txt`, plus `study/` and `drafts/` | The generated pages |
| `assets/`, `fonts/`, `scripts/`, `styles/`, `pagefind/`, `downloads/` | Loaded by the pages (images, covers, Study bundles, search index, EPUBs) |
| `data/`, except `data/sources/`, `data/structured/`, and `data/rites-src/` | Bundles and JSON loaded by the app; `data/texts/` (reader fallback), `data/auto-layout/`, `data/librivox/`, `data/study/`, `data/open/` (downloads), and `data/library.json` (Download catalog JSON) |
| `docs/CATALOG.md` | The Open Data page links it as "Sources & editorial notes" (`openData()` in `app.js`) |

**No longer published:** `tools/`, `tests/`, `src/`, `.github/`, `docs/` (except `CATALOG.md`), `data/sources/`, `data/structured/`, `data/rites-src/`, and the repo files (`AGENTS.md`, `CENTRAL.md`, `HOLDS.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSING.md`, `LICENSE`, `package.json`, `package-lock.json`, `.gitattributes`, `.gitignore`). No page or script links or fetches them. The site links `LICENSE` and `LICENSING.md` on GitHub, and the credits page links source records on texts.bibliothecacatholica.com. They stay in the repository.

**Proof result (November 22, #138 at `4e482dfd97`):** a fresh clone with the 6,016 generated pages and root outputs deleted, rebuilt by `tools/deploy_build.sh`, gave `MATCH: 8442 files identical by sha256` against the committed public files.

## 6. The removal PR (after parity is proven)

- **Delete from git** the generated pages and root outputs only: the `linguist-generated` page trees, `404.html`, `sitemap.xml`, `robots.txt`, `build.json`, `docs/static-pages.txt`, `index.html`, and `study/index.html`. Not every `linguist-generated` file can be rebuilt: `data/guide.js` is also an input (`build_v3_data.py --catalog-only` keeps its feed snapshot, which needs the network to refresh), so the data bundles stay committed (November 22 proof).
- **`.gitignore`:** add the same paths.
- **CI:** keep build, static, study, and tests. Replace the page-tree `git diff --exit-code` with a guard that no generated page is tracked, plus a sitemap count floor. Keep the drift checks on the still-committed data bundles.
- **Docs:**
  - AGENTS.md rules 6 and 8 and "Validate and hand off" (commit sources only; robots, sitemap, and 404 are build outputs);
  - OPERATIONS "Validation";
  - PROJECT-RULES line 63;
  - CENTRAL (hosting, snapshot, handoff);
  - README's hosting sentence.

Phase 1 already moved the git-based tests (`tests/analytics.test.js`, `tests/test_isidore_raw_links.py`) to the tree on disk. `tests/test_hosted_counts.py` needs no change.

## 7. Switch, step by step

1. Merge #135 and this Phase 2 prep after QA (pages are still committed, so production is untouched).
2. Run the local parity proof (section 4, steps 1 to 3) at the merge commit, requiring zero differences.
3. **Owner:** create a temporary second Pages project on the same repository with the build command and `dist/` output. It deploys only to `*.pages.dev`, which is noindexed.
4. **QA on that preview:**
   - section 4, step 4;
   - `tests/test_analytics.py` logic run on the fetched pages;
   - `/drafts/` noindex;
   - a 404 test;
   - `node tools/check_plan_ui.js https://<preview>.pages.dev` reads 26/26;
   - the preview's `/build.json` `id` equals `main`'s.
5. **Owner, about December 26:** set the production project's build command and output. The next deploy of `main` must keep the same `build.json` `id`.
6. Merge the removal PR. Then confirm that the live `/build.json` matches a local build of `main`, and rerun step 4 against production.
7. Delete the preview project, and record the change in CENTRAL and HOLDS.

**Rollback:**
- A failed Pages build keeps the last good deployment live.
- After a bad live deploy, use "Rollback" in the Pages deployments list, revert the removal PR (which restores the committed pages), and clear the build command.

## 8. Risks and open questions for Micah

1. **Cloudflare settings** (build command, output, versions, the preview project) are hosting changes, so they are yours.
2. **Phase 2 scope:** the data bundles, `pagefind/` (1,121 files), `assets/study/`, and `downloads/epub/` are also generated. Leave them committed for now (lower risk; EPUBCheck CI reads the committed EPUBs), or include them?
3. **Dropped paths:** `data/sources/` and `docs/` are no longer served from the site. Is anything outside the site linking to them? The site itself does not.
4. **Reviewers lose the generated diff;** the per-PR Cloudflare preview becomes the way to inspect output.
5. **Other contributors** must stop committing generated pages. The CI guard will catch it until AGENTS.md is updated.
6. **Build image drift:** versions are pinned, and the build ID check in step 5 catches any difference.

## Summary

Cloudflare can build the site from source with Node 22, Python 3.12, and the pinned npm packages; its only network need is the npm install. The output is proven identical by hashing every shipped file both ways, first locally and then on a throwaway preview. Only the public site ships; tools, tests, and notes stay in the repository. After Christmas, Micah turns on the build and the generated pages leave git. Rollback is Cloudflare's button plus a revert.
