# Documentation map

Start with [AGENTS](../AGENTS.md) and [CENTRAL](../CENTRAL.md). CENTRAL is the handoff; parked work and its next steps are in [HOLDS](../HOLDS.md).

| Document | Use |
|---|---|
| [PROJECT-RULES](PROJECT-RULES.md) | Detailed mandatory content, rights, and preservation rules |
| [ANALYTICS](ANALYTICS.md) | Mandatory GA4 and event rules; read before any analytics change |
| [OPERATIONS](OPERATIONS.md) | Current validation procedure, owner decisions, recovery, and account verification |
| [CATALOG](CATALOG.md) | Maintained catalog and edition workflow |
| [DESIGN](DESIGN.md) | Design rules for every page and both themes; read before visual or layout changes |
| [IMPLEMENTATION-NOTES](IMPLEMENTATION-NOTES.md) | Current technical reference, split by area; read only the part you need |
| [ADVENT-LAUNCH](ADVENT-LAUNCH.md) | Launch checklist; external publication state must be checked |
| [Repository audit](REPOSITORY-AUDIT-2026-11-09.md) | Dated inventory, missing evidence, and retention decisions |
| SAINTS, SAINTS-CALENDAR, RITES, RIGHTS, SEO, TIMELINE, READING-GUIDES | Topic-specific implementation and rules; check dates before trusting counts |
| [HOSTED-EDITIONS](HOSTED-EDITIONS.md) | Required before any hosted-book task: the structure, gate, rendering, and EPUB pipeline, the presentation standard, and each edition's status |
| [COLLECTION-REVIEW](COLLECTION-REVIEW.md) | Dated collection assessment; not the current backlog |
| HOSTED-TEXT-INVENTORY, HOSTED-TEXT-QUALITY, LIBRARIES-AND-ARCHIVES, AUTHOR-PAGES, PALETTE-NAVIGATION, READING-DESIGN-REFRESH | Topic references; search the inventory with grep rather than reading it whole |
| [claude-code-chesterton-prompt](claude-code-chesterton-prompt.md) | Prompt for the full Orthodoxy flow on the unstructured editions (see HOLDS) |
| [research/](research/) | Dated research: Chesterton and councils source tables, renewal checks, design directions, and the [design refresh screenshots](research/design-refresh-2026-11/README.md) |
| `static-pages.txt` | Generated list of static pages; search with grep, never edit by hand |
| [archive/](archive/) | Historical records: [implementation history](archive/IMPLEMENTATION-HISTORY.md), [October 22 project review](archive/PROJECT-REVIEW-2026-10-22.md), [October 26 quality audit](archive/QUALITY-AUDIT-2026-10-26.md), [October 21 validation snapshot](archive/VALIDATION.md); not the backlog or release verification |
| [Catalog release notes](archive/CATALOG-RELEASE-NOTES.md) | Archived additions and source checks, including the corrected Summa history |
| `link-health.*`, `source-link-check.json`, `collection-audit.json` | Dated observations; not guarantees of present availability or rights |
| `collection-reading-access.jpg`, `design-refresh.jpg`, `reading-guides-polish.jpg`, `reading-preview.jpg`, `restored-palette.jpg` | October screenshots; visual history, not evidence of the current deployed interface |

Keep a procedure in one authoritative document and link to it. Retain evidence and useful release history with a date/scope; do not keep contradictory current instructions. A generated file is not redundant merely because its source is tracked: static entry pages, browser bundles, search indexes, text-delivery fallbacks, and dependency license notices are required by the existing deployment.
