# Contributor instructions

Bibliotheca Catholica is a static Catholic reading room and curated resource index. Owner: Micah Watson. These instructions apply to every contributor and agent.

Read [CENTRAL.md](CENTRAL.md) next (the shared handoff for the Grok bots, ChatGPT, and Claude), then only the detailed documents relevant to your task. Do not treat a dated implementation note as a current task or fresh approval.

## Rules to retain

1. Host new texts only with owner authorization and a recorded, edition-specific basis ([hosting rule](docs/PROJECT-RULES.md), stated once in `tools/rights_rule.py`): public domain in the US by date (in 2026, first published 1930 or earlier; the line moves each January 1), or written evidence of no renewal, a defective notice, an open license, or permission. Texts may come from any source; the edition, not the website, carries the rights. Rights badges permit eligible links, not automatic hosting. Unknown rights fail closed.
2. Retain source notices, original text bytes, checksums, provenance, and local fallback texts. Read the [detailed rules](docs/PROJECT-RULES.md) before content or rights changes.
3. Reading here stays primary; downloads and affiliate purchases stay secondary. No Amazon links, except Amazon's generic Kindle help pages in the EPUB guide (`tools/guide_pages.py`); never an Amazon product or affiliate link. Flagged titles are never featured or indexed; listing is not endorsement.
4. Preserve the licensing boundaries, Wikipedia attribution, portrait credits, and editorial source requirements. Never invent rights evidence or source facts.
5. Keep the Oxford comma and neutral, sourced writing. No em-dashes in site/Advent fields. Advent wording starts in `data/advent-2026.json`, including material copied to Substack.
6. Edit maintained sources and regenerate their browser bundles and static output together. Never edit generated files alone. Preserve stable IDs and existing reader storage.
7. Preserve the one GA4 tag, production-host gate, sanitized real-path page views, and `BCAnalytics.track`. No personal data, notes, quotations, or full outbound URLs. The existing bounded `search_term` exception applies only to the search event. Read the [analytics rules](docs/ANALYTICS.md) before analytics changes.
8. Preserve `CNAME`, `.nojekyll`, `.well-known/atproto-did`, verification files, `_headers`, `assets/og-image.png`, `data/texts/`, and `data/sources/`. `robots.txt`, `sitemap.xml`, and `404.html` are written by `tools/build_static.py`: keep them, change them only through it, and never edit them by hand. Generated files may be regenerated. Never add an unscoped noindex rule.
9. Preserve accessible keyboard controls, source-linked uncertainty labels, and contrast in both themes. Search defaults to Everything.
10. Respect the [owner decision boundaries](docs/OPERATIONS.md#owner-decisions), including hosting/DNS, expanded affiliate links, new analytics, and external outreach. Explicit authorization already given for the current task applies. Changes limited to presentation, docs, tests, and tooling may merge on green CI under the standing approval described there.
11. When an instruction file and the existing code disagree, follow the conventions in the code, and point out each mismatch in your final reply.

## Validate and hand off

Use the [current validation procedure](docs/OPERATIONS.md#validation), matching `.github/workflows/validate.yml`: `npm run validate` runs it with a one-line result per step, and `npm run validate -- --drift` after committing checks for drift. After adding or removing a hosted book, `python3 tools/hosted_counts.py --write` refreshes every stated count. Report failures honestly.

Review source changes only: `git diff origin/main -- . ':(exclude,attr:linguist-generated=true)'` (generated paths are marked in `.gitattributes`). Confirm generated output with the drift check in [OPERATIONS](docs/OPERATIONS.md#validation), never by reading generated pages. Search `docs/static-pages.txt` and `docs/HOSTED-TEXT-INVENTORY.md` with grep; do not open them whole.

Update [CENTRAL.md](CENTRAL.md) in place with significant updates, handoffs, decisions, and status notes, newest first. Handoff entries are at most 5 lines, only the 3 newest are kept, and the file stays under 80 lines (`tests/test_central.py`). No separate dated report files for handoffs. Check live PR state before acting. Do not overwrite another contributor's work.

Visual and layout changes follow the [design rules](docs/DESIGN.md).

Before any task that touches a hosted book (its text, reader, chapter pages, EPUB, cover, or work page), read [hosted editions](docs/HOSTED-EDITIONS.md): how books are prepared and presented, and what must never change.

Details: [project rules](docs/PROJECT-RULES.md), [analytics](docs/ANALYTICS.md), [implementation reference](docs/IMPLEMENTATION-NOTES.md), [catalog](docs/CATALOG.md), [rights](docs/RIGHTS.md), [saints](docs/SAINTS.md), [calendar](docs/SAINTS-CALENDAR.md), [rites](docs/RITES.md), [SEO](docs/SEO.md), [reading plans](docs/READING-GUIDES.md).
