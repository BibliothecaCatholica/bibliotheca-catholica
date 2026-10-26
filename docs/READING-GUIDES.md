# Reading lists and edition guide

The reading-list landing page offers paths rather than rendering every recommendation. Each path has a suggested starting point, book search, and reading-access filters. Church Fathers, Church Documents, and Related Christian Voices reuse source-checked catalog records. Lewis is identified as Anglican, with references rather than hosted texts.

Edition cards put reading options before retailer links. Hosted copies name their translator where recorded; download links distinguish a file from a provider's options page. Print suggestions are expandable. Explicit `workIds` in `tools/editions_data.py` connect guides to catalog records. Multi-work collections identify their available component, and companion works/adaptations are kept in `related`. Interior Castle must not resolve to Teresa's Life; the original Spiritual Exercises must not resolve to Coppens's retreat adaptation.

Maintain recommendations in `tools/reading_lists.py` and `tools/editions_data.py`. Run `npm run build` to regenerate `data/library.js` and the guide. The guide's `--catalog-only` mode preserves existing featured/news snapshots and needs no network. The full feed-refresh command remains a separate editorial operation. CI checks both generated catalogs for drift.

Verification: catalog relationship and access-filter tests; existing library/search tests; browser checks for path selection, accent-insensitive search, original versus adapted works, external reading links, expandable print suggestions, direct reader links, and narrow-screen layout.

The current site still uses hash routes for interactive navigation, and the build also pre-renders clean, crawlable work and section pages. The on-site reader displays hosted plain-text editions; it does not render EPUB or PDF files. Those formats remain links to the source or publisher, subject to the record's rights status.
## Dated reading plans (v20)

A reading plan is a dated sequence of short readings, unlike a reading list, which is a path through whole books. The first is **Advent with the Fathers 2026** at `/reading/advent-2026/` (`#/reading/advent-2026`): 26 days, from the First Sunday of Advent (November 29, 2026) to Christmas Eve. It is linked from the Reading Lists page (a card in the app, a "Reading plans" list on the static page) and from the home page's "Sections of the library" list.

- **Source:** `tools/reading_plans.py` lists each day (date, marker, work, edition, link paragraph, passage paragraphs, location, note) and `EDITION_YEARS` with the evidence that each edition is before 1931.
- **Build:** `python3 tools/build_reading_plans.py` (in `npm run build`) checks the dates, Sunday markers, editions, SHA-256, anchors, and sections, computes reading time at 200 words a minute, takes the quote, and writes `data/reading-plans.json` and `data/reading-plans.js`. `--selection <file>` and `--brand <file>` also write the editorial selection notes (the brand file includes the full passage text for writers).
- **Page:** `tools/build_static.py` pre-renders every day with its quote, note, edition, and rights badge. `scripts/plans.js` renders the same list in the app, highlights today, and adds mark-as-read boxes saved in `localStorage` (`bc-plan:<id>`). `styles/plans.css` uses theme colors only and has print styles that drop the buttons and print each reading's address.
- **Tests:** `tests/test_reading_plans.py` (26 days, dates and markers, links, pre-1931 editions, flags, quotes against the raw text, title and description uniqueness, sitemap and links, contrast) and `tests/plans.test.js` (today highlight, storage, links).

The 2026 selection draws on the hosted texts only, so several Advent preachers are absent (Leo the Great, Gregory the Great, Ambrose's own works, Bernard's sermons, Cyril of Jerusalem, and Newman's sermons are not in the reading room). Bernard appears through Dante's Paradiso XXXIII and Ambrose through Augustine's Confessions.
