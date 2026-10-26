# Contributing

Read [AGENTS.md](AGENTS.md) and [the catalog rules](docs/CATALOG.md) before editing. The owner maintains the catalog and reviews inclusion, source evidence, and rights decisions. Listing an imported record is not endorsement.

Report broken links, search or reader problems, accessibility issues, and sourced corrections through [the issue form](https://github.com/BibliothecaCatholica/bibliotheca-catholica/issues/new?template=site_problem.yml). GitHub requires an account; the correction email on the site's Support page is the alternative. Include the affected URL, expected behavior, source evidence where applicable, and the footer's build ID. Never put private reader notes or credentials in a public issue. Report security concerns privately as described in [SECURITY.md](SECURITY.md).

Use Python 3.10+ and Node 18+. No runtime package installation is needed. Start with `npm run dev`. Before submitting a pull request, run:

```sh
npm run build
python3 tools/build_static.py
npm test
git diff --check
```

Commit generated output, stage the intended changes, then rerun the builds and require `git diff --exit-code` to pass. CI repeats the offline validation. Check changed flows by keyboard and in both themes. For reader changes, also check source notices, saved notes, and navigation. Do not claim WCAG conformance from automated checks alone.

Keep stable IDs and existing URLs. Edit source JSON and generators rather than generated copies. Dates must distinguish original publication, translation, digital release, original catalog snapshot, and source review. Never turn an inferred date into a reviewed fact.

Host no new text without the owner's approval and edition-specific rights evidence. Keep source records, checksums, and notices. CatholicSaints.Info remains link-only; never copy or crawl it. No unrequested outreach to outside libraries. Existing licensing terms in [LICENSING.md](LICENSING.md) remain unchanged.

Treat contributors and readers respectfully. Critique claims with sources and report editorial concerns calmly. Network link checks are optional maintenance tools, separate from offline CI; a blocked automated request alone does not prove a dead link.
