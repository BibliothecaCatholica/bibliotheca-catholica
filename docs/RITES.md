# Rites & Liturgy (v19)

Phases 1 (editorial review) and 2 (section and map) are built. Phase 3 (population layer) and phase 4
(regional outlines and a public-domain reader) are **not approved**; do not build them.

## Files

| File | What it is |
|---|---|
| `data/rites-src/rites-map.json` | Research copy of the 31 records (24 Churches sui iuris, 7 Latin rites and uses), unchanged. |
| `data/rites-src/rites-map-shading.json` | Research copy of the country layers, with `population_estimates` and `population_policy` removed. |
| `data/rites-src/geo.json` | Map geometry from Natural Earth, written by `tools/rites_geo.py`. |
| `tools/rites_geo.py` | Offline: `python3 tools/rites_geo.py <dir>` reads `ne_110m_admin_0_countries.geojson`, `ne_50m_admin_0_countries.geojson`, and `ne_50m_admin_1_states_provinces.geojson` (Natural Earth 5.x, from github.com/nvkelso/natural-earth-vector). Equirectangular, 1000 px wide, latitude 84 to -57; Douglas-Peucker simplification; relative paths in 0.1 px; insets clipped to their boxes; Guam (missing at 1:110m) drawn as a 3 px square from 1:50m. Rerun only to change the geometry. |
| `tools/build_rites.py` | Part of `npm run build`. Applies the editorial review (tables below), validates codes and cross-links, generates the palette, and writes `data/rites.json`, `data/rites.js`, and the palette block of `styles/rites.css`. |
| `tools/rites_pages.py` | Page HTML shared by the app and `tools/build_static.py` (like `tools/rights_pages.py`). |
| `scripts/rites.js` | `window.BCRites`: lazy-loads `data/rites.js`, renders `#/rites`, `#/rites/<id>`, `#/rites/sources`, mounts the map, and wires the selector. No analytics events (page views come from `app.js`). |
| `styles/rites.css` | Layout, table, map styles, and the generated palette. |
| `tests/test_rites.py`, `tests/rites.test.js` | The rules below. |

## Editorial rules (from the phase 1 review)

- Every displayed fact links its source. A low-confidence field is shown only if it is in `UNVERIFIED` (with an "Unverified" marker and its source); otherwise it is left out and shown as "Not yet verified". `DROP` lists fields left out on review, with the reason.
- Raw research notes are working notes and are never shown verbatim; `PUBLIC_NOTES` holds the public wording, each with a source (`NOTE_SRC`).
- Dates are ranges or centuries ("1653 to 1662", "4th century") unless a dated document is cited.
- Both classifications are shown: CCEO can. 28 §2 tradition and the Catechism (CCC 1203) wording.
- Heads: "as listed by GCatholic on <date>", without ages. Re-check every six months.
- The 1962 books are described in the words of Traditionis custodes (2021) arts. 1 to 3 and 8. Never "Ordinary Form" or "Extraordinary Form".
- Cross-links only to existing pages on the approved lists (`AUTHORS`, `WORKS`, `SAINTS`, `BYZ_LINKS`, `RELATED`); no Isidore links, no Orthodoxy or Sheen changes.
- Site text: Oxford commas, no em-dashes (`clean()` rewrites them), no population numbers.

## The map

- Inline SVG, no Leaflet, CDN, tiles, or pins. Whole countries are shaded, joined on `ISO_A2_EH`.
- One layer at a time: a Church, a family (union of its Churches, for families with more than one), or a Latin rite with its own jurisdiction (Ambrosian, Hispanic-Mozarabic, Divine Worship). The Latin Church is listed but not shaded.
- Present jurisdiction is the default view; the approximate historical heartland is a toggle and is never the default.
- Insets: A. Lebanon, B. The Holy Land, C. South India (Kerala outlined from Admin 1; shading is still by country).
- Colour: the Okabe and Ito hues, lightened or darkened per theme to reach 3:1 against land and sea, always with a hatch pattern (diagonal stripes for present, crosshatch for heartland) and a visible country list. Text uses the site tokens (4.5:1).
- Static pages inline the SVG shaded for the default layer, so the map, lists, and tables work without JavaScript; the selector is `hidden` until the app mounts it.
- Disclaimer (verbatim on every map): "Borders are illustrative (Natural Earth, de facto lines) and imply no position. Shading shows where a Church has its own jurisdiction, not where all its faithful live."
- Natural Earth is public domain (https://www.naturalearthdata.com/about/terms-of-use/); the note is on `/rites/sources/` and `/licensing/`.

## Needs research (as of 2026-10-26)

| Id | Field | Why |
|---|---|---|
| belarusian, bulgarian, croatia-serbia, greek, italo-albanian, macedonian, russian | head | Low confidence in the research (vacancies, administrators, or no current listing). |
| greek | canonical_status | Low confidence. |
| albanian | head | Shown as Unverified: an Apostolic Administrator, name not confirmed. |
| albanian | present_see, present country list | CNEWA places only a parish at Elbasan; GCatholic omits the Church. |
| belarusian | present_see | No eparchy; an Apostolic Visitator is not a see. |
| russian | mother_city, present_see | The 1917 exarchate seat needs a source; no functioning hierarchy. |
| coptic, ethiopian, eritrean, syriac, syro-malankara, armenian, chaldean, syro-malabar | liturgical_books_current | Shown as Unverified: current editions not confirmed. |
| latin-roman-1962 | status_reported_not_magisterial | Left out: press reports, not legislative acts. |
| latin-roman (laity Missal) | resource rights | Undated edition, badge Unknown until dated. |
| latin-religious-orders | everything per order | Not mapped; order-by-order sources needed. |

## Not built (deferred or not approved)

- Phase 3 population layer and phase 4 regional outlines and reader: not approved.
- An "Ordinariates for Eastern faithful" layer (not in the shading data), click-a-country side panels, and sub-national heartland shapes.
