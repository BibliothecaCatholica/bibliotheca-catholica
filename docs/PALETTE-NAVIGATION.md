# Original palette and visible navigation

Restores the original shared colors from styles.css by removing the green-tinted replacement variables in refresh.css. Light mode again uses parchment, burgundy, and gold; dark mode uses the original charcoal/navy backgrounds and warm text. Background decoration and gold buttons inherit their original colors as well.

Navigation is organized into two visible groups instead of hiding core collections under a dropdown:

- Reading and discovery: Discover & Read, Isidore Index (v18; was "Ebooks & PDFs"), Authors, Timeline, Reading Lists, Editions & Translations, Podcasts & Media.
- Faith and reference: Scripture, Church Documents, Prayer, Doctors, Reference Works, Digital Libraries, Rare & Obscure, Substacks, Projects.

Open Data stays in the footer. On phones, the menu displays all collections in a wrapping two-column layout. It announces its expanded state, closes when a section is chosen, supports Escape, and marks the current section with aria-current. Updated asset query strings prevent an older cached override from retaining the green palette after the new HTML loads.

Validation: 14 existing checks pass and app.js passes syntax checking. Browser checks confirm the media and timeline links are visible on desktop and available directly in the phone menu, Timeline navigation closes the menu, and the document has no horizontal overflow in 390px and 768px iframe viewport checks. Both restored color themes were inspected. These are responsive browser checks, not physical-device testing. No catalog records or reading files were changed.
