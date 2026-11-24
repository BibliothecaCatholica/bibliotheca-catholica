# Cloudflare build-on-deploy switch runbook

Round 8 and 9, Job E (November 23, 2026). The steps to switch the production Pages project `bibliotheca-catholica` from serving the
committed repository to building on deploy (`bash tools/deploy_build.sh` into `dist/`, from #135 and #138). **Not before December 27,
2026, and only on Micah's go.** Business makes every Cloudflare setting change; the repository side is two PRs. Plan and parity proof:
`docs/plans/build-on-deploy-plan.md` (on #135 and #138; not yet on `main`).

## Before the switch (repository)

1. #135 and #138 are restacked on current `main`, green in CI, and QA PASS for their head SHAs.
2. **Parity proof on that head** (plan section 4): in a fresh clone, record the SHA-256 of every committed public file, delete the
   generated files, run `bash tools/deploy_build.sh`, and run `python3 tools/compare_tree.py committed.sha dist/`. It must report
   0 missing, 0 extra, 0 changed. Record the result and the commit in the PR.
3. Check in `dist/`: `CNAME`, `.nojekyll`, `.well-known/atproto-did`, `google3b007babfa8923a4.html`, `_headers` (CSP, security headers,
   `*.pages.dev` noindex), `robots.txt`, `sitemap.xml`, `404.html`, `build.json`, and `drafts/` (noindex, not in the sitemap).
4. One GA4 tag per page in `dist/` (`tests/test_analytics.py` logic run against `dist/`), and the build ID in `dist/build.json` equals the
   committed `build.json` of the same commit.
5. Merge #135 and #138 **without** removing generated files from git. Production keeps serving the committed tree until step 6.

## The switch (Cloudflare, Business)

6. Pages project `bibliotheca-catholica`, Settings, Builds: build command `bash tools/deploy_build.sh`, output directory `dist`, root
   directory empty. Environment variables (production and preview): `NODE_VERSION=22`, `PYTHON_VERSION=3.12`. Record the old values
   (empty build command, empty output directory) in the change note.
7. Trigger a production deployment of `main` (Deployments, Retry deployment on the latest `main` commit, or push an empty-content
   docs commit through a normal PR).
8. No DNS, custom-domain, or R2 change is part of the switch.

## Checks after the switch (within 30 minutes)

- The deployment log shows `deploy_build.sh` finishing in about 2 minutes, with no npm or Python errors.
- `https://bibliothecacatholica.com/build.json` `id` equals `git show origin/main:build.json` `id`.
- Spot pages: `/`, `/library/`, `/work/orthodoxy/`, a chapter page, `/summa/1-1/q1/a1/`, `/saints/`, `/reading/advent-2026/`, `/study/`,
  `/credits/`, `/drafts/` (noindex), and a 404 path. Each returns 200 (the 404 path redirects as today) with one GA4 tag.
- Headers on `/`: the CSP and `Permissions-Policy` from `_headers`; on a `*.pages.dev` deployment URL: `X-Robots-Tag: noindex`.
- `https://bibliothecacatholica.com/sitemap.xml` has the same URL count as the committed one; `robots.txt` matches.
- The reader opens a hosted text (texts.bibliothecacatholica.com first, local fallback).
- No `tools/`, `tests/`, `docs/` (except `docs/CATALOG.md`), `data/sources/`, or `node_modules/` paths are served (404).

## Rollback (one step)

**Pages, Deployments: open the last deployment from before the switch and choose "Rollback to this deployment".** It serves the
previous committed-tree deployment at once, with no rebuild. Then set the build command and output directory back to empty (the
recorded old values) so the next push deploys the committed tree again. No repository change is needed to roll back, because the
generated files stay committed until the later removal PR (plan section 6), which runs only after two clean weeks on build-on-deploy.

## After two clean weeks

The removal PR (plan section 6) stops committing generated pages, updates AGENTS.md rules 6 and 8, CI, and the docs. It needs QA
and Micah's go like any hosting change.
