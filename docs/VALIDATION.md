# Validation: reading and discovery release

- `npm run build`: 49 work records validated; deterministic browser bundle generated.
- `npm test`: 11 passing checks, including actual imported-catalog search isolation, accent/multiple-token queries, bundle/source agreement, local-text checksums, duplicate rejection, missing-author rejection, path containment, and external-only copyrighted/Anglican entries.
- JavaScript syntax checks: app.js, scripts/search.js, scripts/library.js.
- Open-data exporter runs from this checkout; the corrected NABRE edition note is reflected in JSON and CSV.
- 42 of 42 catalog source URLs returned HTTP 200; titles checked against records. See source-link-check.json. Availability may change.
- Browser: selected-library filter gives 24 local reading editions; Confessions edition details show Pusey's translator credit; text loads; typography and section survive reload; source heading navigation reaches BOOK II; full-text search for “restless” finds 9 paragraphs; both light and dark themes work.
- Browser: “Lewis” returns 12 selected results, including 8 new work records and the Anglican profile; switching to Isidore returns 31 imported results with explicit unreviewed labels. Existing imported records are preserved.
- Tested desktop preview only. Mobile CSS retains the existing responsive layout and adds wrapping reader controls; physical-device testing remains a follow-up.

The screenshot in reading-preview.jpg shows the local reading room, not a claim of production deployment.
