# Reading options and visual refresh

Built on main after PR #1 and its review fixes were merged. Existing source notices, the pre-1931 local hosting rule, Isidore matches, donation links, and affiliate settings are preserved.

- “Which Edition?” is now “Editions & Translations”; reading links precede print recommendations.
- The reading collection can be filtered by online, EPUB, or PDF availability. Format badges include the existing Isidore matches.
- 25 Project Gutenberg EPUB URLs were discovered from their catalog pages, followed to their final URLs, and checked for a ZIP signature. Files remain with Gutenberg; nothing new is mirrored.
- Four Chesterton editions link to Standard Ebooks' EPUB selection pages. These are labeled “Choose EPUB at source,” rather than represented as verified direct file downloads. A candidate Francis of Assisi URL returned 404 and was excluded.
- Reading source metadata is in data/reading-options.json; its browser snapshot is data/reading-options.js. tools/refresh_reading_options.py is an optional network refresh, separate from the deterministic build. Review updates before committing.
- Navigation has seven primary sections and an accessible native “Explore more” disclosure. Open Data is moved to the footer, alongside the source directory and other site information. Repeated external footer shortcuts and the header/hero Vatican shortcut are removed; Church sources remain available in the relevant collections.
- Visual changes: ivory and burgundy palette, left-aligned editorial homepage, quieter cards, reduced decoration, clearer reading/download buttons, and responsive wrapping.

Validation: 14 automated checks pass; application and reading module syntax checks pass. Browser-tested EPUB filtering (26 work records including Isidore matches), edition-guide reading actions, Orthodoxy's Gutenberg/Standard Ebooks/Isidore choices, and disclosure navigation. Desktop light/dark appearance inspected. Physical mobile device testing has not been performed. Preview screenshot: design-refresh.jpg.
