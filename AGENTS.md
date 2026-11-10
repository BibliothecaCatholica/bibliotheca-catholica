# Contributor instructions

Bibliotheca Catholica is a static Catholic reading room and curated resource index. Owner: Micah Watson. These instructions apply to every contributor and agent.

Read [CENTRAL.md](CENTRAL.md) next, then only the detailed documents relevant to your task. Do not treat a dated implementation note as a current task or fresh approval.

## Rules to retain

1. Host new texts only with owner authorization and edition-specific rights evidence under the project's pre-1931 selection rule. Rights badges permit eligible links, not automatic hosting. Unknown rights fail closed.
2. Retain source notices, original text bytes, checksums, provenance, and local fallback texts. Read the [detailed rules](docs/PROJECT-RULES.md) before content, rights, or analytics changes.
3. Reading here stays primary; downloads and affiliate purchases stay secondary. Flagged titles are never featured or indexed; listing is not endorsement.
4. Preserve the licensing boundaries, Wikipedia attribution, portrait credits, and editorial source requirements. Never invent rights evidence or source facts.
5. Keep the Oxford comma and neutral, sourced writing. No em-dashes in site/Advent fields. Advent wording starts in `data/advent-2026.json`, including material copied to Substack.
6. Edit maintained sources and regenerate their browser bundles and static output together. Never edit generated files alone. Preserve stable IDs and existing reader storage.
7. Preserve the one GA4 tag, production-host gate, sanitized real-path page views, and `BCAnalytics.track`. No personal data, notes, quotations, or full outbound URLs. The existing bounded `search_term` exception applies only to the search event.
8. Preserve `CNAME`, `.nojekyll`, `.well-known/atproto-did`, verification files, `_headers`, `robots.txt`, `sitemap.xml`, `404.html`, `assets/og-image.png`, `data/texts/`, and `data/sources/`. Generated files may be regenerated. Never add an unscoped noindex rule.
9. Preserve accessible keyboard controls, source-linked uncertainty labels, and contrast in both themes. Search defaults to Everything.
10. Respect the [owner decision boundaries](docs/OPERATIONS.md#owner-decisions), including hosting/DNS, expanded affiliate links, new analytics, and external outreach. Explicit authorization already given for the current task applies.

## Validate and hand off

Use the [current validation procedure](docs/OPERATIONS.md#validation), matching `.github/workflows/validate.yml`. Commit generated changes, rerun generators, and verify no new drift. Report failures honestly.

Update CENTRAL with the branch, changes, checks, blockers, and next action. Keep it under 150 lines; move old handoffs to `docs/HANDOFF-ARCHIVE.md`. Check live PR state before acting. Do not overwrite another contributor's work.

Details: [project rules](docs/PROJECT-RULES.md), [implementation reference](docs/IMPLEMENTATION-NOTES.md), [catalog](docs/CATALOG.md), [rights](docs/RIGHTS.md), [saints](docs/SAINTS.md), [calendar](docs/SAINTS-CALENDAR.md), [rites](docs/RITES.md), [SEO](docs/SEO.md), [reading plans](docs/READING-GUIDES.md).
