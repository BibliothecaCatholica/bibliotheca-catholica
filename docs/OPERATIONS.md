# Operations and owner decisions

## Validation

Use Node 22 and Python 3.12 as in CI. Install pinned dependencies with `npm ci`.

```sh
npm ci
npm run build
python3 tools/build_static.py
npm run build:study
npm test
git diff --check
node --check app.js
# Check every maintained browser script changed by the task:
find scripts -name '*.js' -exec node --check {} \;
node --check data/site-copy.js
```

Review and commit intended source and generated changes. Rerun the three build commands after committing, then `git diff --exit-code` and `git status --short` to detect tracked drift and untracked output. A clean diff before committing is not expected. CI is authoritative for required checks; do not skip a failure because a change is documentation-only. Network link checks are optional and do not prove textual fidelity or rights.

## Owner decisions

Existing explicit authorization for a task applies; do not ask twice. Otherwise obtain owner direction before:

- New hosting or mirroring of files; new text eligibility cannot be inferred from a rights badge.
- Hosting settings, DNS, verification files, production cutover, or retirement of a host.
- New analytics IDs, scripts, measurements/events; expansion of data collection requires accurate privacy disclosure and tests.
- Affiliate expansion beyond existing configured placements; author Bookshop hooks remain disabled. Preserve the documented EPUB vendor-help exception to the general no-Amazon rule.
- Licensing changes (update all linked terms together), takedown agent identity, or a promised removal deadline.
- Nostra Aetate quotations, expanded CatholicSaints.Info linking/copying, unapproved Rites phases/population layers, additional newsletter embed placements, or new verified social `sameAs` profiles.
- Publishing or contacting others on the owner's behalf, unless explicitly authorized in the task. A role label does not authorize sending.

Read PROJECT-RULES for exact existing restrictions and exceptions. Nothing in this document authorizes new ingestion or expands rights.

## Failed CI or broken deployment

Stop treating the branch as ready. Record the failing command, commit, and relevant output; reproduce with the pinned dependencies. Fix maintained sources, rebuild, and rerun affected and required checks. Do not hand-edit generated pages, disable CI, or silently refresh external input to hide a failure.

For a production incident, identify the last known-good deployed commit and compare its `build.json` with the failing deployment. Prepare a revert of the smallest responsible commit on a branch; preserve unrelated work and validate it. Deploy through the established authorized path. Use a host's previous deployment only with owner authorization and recorded deployment ID; dashboard access is not implied. Check home, affected routes, reader, canonical/robots, assets, and live build identifier after recovery. Record incident and recovery evidence in CENTRAL. No destructive Git reset or force-push to main.

## Backup and restore

Independent backup is not verified by this audit. Git history and a second delivery repository do not establish an independent recoverable backup.

Owner must select a separate storage destination and schedule. A proposed minimum is a Git bundle of all refs for each repository, current source/provenance/text files, and an export of required host settings without secrets. Record commit IDs, SHA-256 manifests, destination, retention, and backup date privately. Restore to a fresh directory, verify hashes, run the build/test procedure, and compare the exported text archive manifest. Record the restore-test outcome here with a safe evidence pointer. No backup service or schedule has been provisioned by this documentation change.

## Accounts and service map

This is a responsibility checklist, not proof of dashboard access. Never commit passwords, API tokens, billing exports, or recovery codes.

| Service | Repository evidence | Responsibility / verification still needed |
|---|---|---|
| GitHub | Main site, texts repo, validation workflow | Owner confirms administrators and deploy permissions |
| Cloudflare Pages / DNS | `_headers`; documented mirror; owner-reported cutover | Owner confirms production domains, project binding, DNS, deploy root, and rollback |
| Squarespace registrar | Owner-reported registrar | Owner confirms renewal and nameserver control privately |
| GA4 / Search Console | Existing tag and root verification file | Owner confirms admin access and enhanced-measurement settings |
| Substack | Newsletter links and limited embeds | Owner/publishing role confirms draft and schedule state |
| Bookshop / TAN LeadDyno | `data/affiliates.js` | Owner confirms account and existing approved placements |
| Text delivery | `data/library.json` textArchive config | Owner confirms delivery deployment and independent backup |

Hosting descriptions in retained historical notes must not be treated as DNS verification. Confirm bindings before changing CNAME, headers, or hosting settings. Provider limits also require current provider verification before capacity decisions.
