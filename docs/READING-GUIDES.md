# Reading lists and edition guide

The reading-list landing page offers paths rather than rendering every recommendation. Each path has a suggested starting point, book search, and reading-access filters. Church Fathers, Church Documents, and Related Christian Voices reuse source-checked catalog records. Lewis is identified as Anglican, with references rather than hosted texts.

Edition cards put reading options before retailer links. Hosted copies name their translator where recorded; download links distinguish a file from a provider's options page. Print suggestions are expandable. Explicit `workIds` in `tools/editions_data.py` connect guides to catalog records. Multi-work collections identify their available component, and companion works/adaptations are kept in `related`. Interior Castle must not resolve to Teresa's Life; the original Spiritual Exercises must not resolve to Coppens's retreat adaptation.

Maintain recommendations in `tools/reading_lists.py` and `tools/editions_data.py`. Run `npm run build` to regenerate `data/library.js` and the guide. The guide's `--catalog-only` mode preserves existing featured/news snapshots and needs no network. The full feed-refresh command remains a separate editorial operation. CI checks both generated catalogs for drift.

Verification: catalog relationship and access-filter tests; existing library/search tests; browser checks for path selection, accent-insensitive search, original versus adapted works, external reading links, expandable print suggestions, direct reader links, and narrow-screen layout.

This revision does not change hash routing or provide an EPUB/PDF renderer. Indexable static work pages and a structured reader remain subsequent projects.
