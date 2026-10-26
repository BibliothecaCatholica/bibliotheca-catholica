# Verified quality review — October 26, 2026

This review reconciles the owner-supplied Copilot/Claude assessment (`bibliotheca_catholica_end_to_end_assessment_20261026_175410.pdf`) and its follow-up with actual repository files and current production responses. The assessment relied on an October 21 homepage capture and expressly could not inspect the repository. Its unknowns are questions to verify, not confirmed defects.

## Evidence and findings

Before changes, `main` was `5a80f1ba` (v18.2). Direct HTTPS GETs returned 200 for `/`, `/author/augustine-of-hippo/`, `/sitemap.xml`, `/robots.txt`, and `/app.js`; all five matched the checkout byte for byte. The raw homepage and sampled author page contained no “Tester.” A retrieval tool's inability to fetch these pages does not establish a production outage or indexing ban.

| Assessment area | Verified baseline | This pass |
|---|---|---|
| Meaningful HTML before scripts | Already present: real home content and hundreds of pre-rendered entry pages | Preserved; added a plain title-and-author directory |
| Clean URLs, sitemap, canonicals, structured data | Already implemented in v9/v17; header/footer used clean paths | Preserved; new directory is generated and listed in the sitemap |
| Search absent | Header input and interactive homepage search already existed | Header now has a submit button and form; suggestions expose expanded/selected state and active option |
| “Data compiled” blank | Confirmed in raw HTML; app filled it from the original catalog snapshot | Filled by the static generator too; explanatory wording distinguishes snapshot and per-source checks |
| Scope wording | Title, social metadata, body copy, README, and repository About wording varied | Unified homepage/browser/social copy, README, About page, and footer around “a library of libraries,” reading room, and curated index |
| Source-to-live comparison | Sampled deployed bytes matched `main`, but no visible build identity | Footer fingerprint and `/build.json` source hashes; build order fixed so all pages agree after one generation |
| Data loading failure | Core data failure replaced useful content; optional search collections could repeatedly retry after errors | Plain content retained, explicit recovery notice, and incomplete-results message; failed search loads are not automatically retried |
| Provenance and rights | Already substantial: edition sources, checked dates, source snapshots, checksums, rights gates, saints' fact sources, Wikipedia/portrait credits | Preserved; safe source schemes checked offline |
| CI and governance | Offline builds/tests and read-only workflow permissions existed; license/editorial/privacy pages existed | Pinned current action commits, added regression tests, issue form, contributing guide, and security scope/limitations |
| Security headers | Sampled production headers did not include CSP, framing, Permissions-Policy, or nosniff | Explicit referrer meta added; no unsupported claim that repository header files change GitHub Pages responses |

## Boundaries

The canonical brand remains Bibliotheca Catholica. “Library of libraries” describes a selected reading collection plus cross-library discovery. It does not claim exhaustive Catholic coverage, comprehensive full-text search across outside libraries, or new bibliographic verification merely because a page was rebuilt.

The footer's catalog date remains the actual original snapshot date. `bc-…` is a deterministic application/catalog content fingerprint, including source JavaScript, CSS, generators, metadata, README, and normalized template. It is independent of build time and shallow-checkout commit ancestry; `/build.json` is intentionally explicit that it is not a commit SHA. The official repository and source history are linked separately.

Interactive search and the reader need JavaScript. The static `/search/` directory supports normal links and browser Find; there is no server-side search service. Its form submits `lookup` to a real clean page, and the app reads it if scripts load. Search analytics retain their existing normalized, term-free page-view context; no new event types, tracking services, or storage are added.

No texts were imported, rights classifications broadened, licenses changed, or outside libraries contacted. No new crawler was run against CatholicSaints.Info. Existing colors remain in place.

## Validation

Offline coverage includes existing catalog, rights, analytics, saints, reader, search, licensing, SEO, static-output, and checksums tests, plus regressions for startup failure, blocked analytics, timeout recovery, partial-search failure/retry behavior, source URL schemes, shared dates/fingerprints, and metadata consistency. Build generation must be repeatable with no unstaged changes.

Browser preview checked the visible Search button, search results with selected works first, ArrowDown/Enter suggestion navigation, direct `/search/?lookup=Confessions`, and an intentionally missing core data script. The failure fixture retained the homepage and displayed working recovery links; it was removed before publication. Static tests inspect the content available without scripts. These checks do not establish screen-reader or full mobile/zoom conformance.

## Next priorities, with completion criteria

1. **Finish bibliographic evidence.** Record the specific translation/edition year wherever missing. Separate original work, translation, printing, digital release, and review dates; unknown stays unknown. Evaluate quality per work rather than adding volume without review.
2. **Make reader journeys measurable.** Test find → compare edition → read → resume, plus source-only and no-match cases, with real readers on mobile and keyboard. Establish baseline field Core Web Vitals and accessibility checks before setting budgets or claiming improvements.
3. **Persist remaining filters in URLs.** General search scope already persists; timeline, reading-room, and guide filters still have runtime state. Make copied links reproduce those views and verify Back/Forward behavior.
4. **Admin settings.** Confirm GA4 automatic outbound clicks/history-based page changes settings, retention, and opt-out behavior. Review GitHub private reporting, secret scanning, and push protection through account settings. These were not changed or asserted enabled here.
5. **Search visibility.** Verify sitemap processing and representative URLs in Search Console and Bing Webmaster Tools. A retrieval service's 403 or an absent branded result is not sufficient evidence of non-indexability. Repository About still has the old “master library” description; this connector exposes no repository-settings write action. Suggested replacement: “A free Catholic library of libraries: a selected reading room and curated resource index, with edition guides, saints, Church documents, and original sources.”
6. **Header controls and maintenance.** Evaluate a supported serving layer before promising CSP/frame/Permissions-Policy headers. First inventory/test all scripts, fonts, media, inline behavior, and source fetches. Add public-address and redirect validation before running link checks on untrusted contributions; then establish a maintenance cadence. External reachability alone is not source verification.

There is no evidence here that the project needs a new framework, database, or paid search backend. Revisit those choices when measured scale or reader needs justify them. The current dependency-free static architecture remains compatible with these improvements.
