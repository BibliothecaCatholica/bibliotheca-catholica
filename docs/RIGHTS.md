# Rights badges (v16)

Not legal advice. This explains how the site labels and links books.

| Status | Badge | Downloads / reader | Source of the status |
|---|---|---|---|
| `public_domain_us` | Public domain (US) | yes | hosted reading-room editions checked under the pre-1931 rule; Index records only via `P1` (same PG ebook as a hosted edition, no modern ISBN edition) or a hand-checked `MANUAL` entry |
| `open_license` | Open license | yes | `MANUAL` entry naming the license (none yet) |
| `permission_granted` | Permission granted | yes | `MANUAL` entry citing written permission (none yet) |
| `link_only` | Link only | no; link to the isidore.co book page | research codes L1–L6 (1978+, ISBN, renewed, post-1930 Church texts, and similar) |
| `unknown` | Unknown | no; link to the isidore.co book page | research codes H1–H3 and U1a–U4, including every "likely hostable" lead |

Counts on 2026-10-25: public domain (US) 6, open license 0, permission granted 0, link only 4,149, unknown 2,478 (6,633 records).

## Files

- `data/rights.json` → `data/rights.js`: `{v, checked, note, statuses, codes, records:{id:[code, detail?]}}`; `MANUAL` records are `["M", evidence, checked, status, checked_by]`.
- `tools/build_rights.py --research <dir>` derives `rights.json` from `<dir>/hosting-classification.csv`; without `--research` it validates and regenerates `rights.js`, the `r` field in `data/isidore-matches.*`, and `data/rights-pages.js`.
- `tools/rights_pages.py`: the `/rights` and `/takedown` HTML (one source for the app and the static pages).
- Open data: `isidore-index` has `rights_status`, `rights_evidence`, and `rights_checked`; file links only when hostable.

## Open decisions for the owner

- DMCA designated agent: register (US Copyright Office, $6 per 3 years) and replace the PLACEHOLDER on `/takedown`.
- Whether to promise a specific removal time (the research guide suggested 48 hours; the page says "promptly").
- Raw isidore.co author-folder links (the Index's "Author folders A–Z" tab and a few hub resources) still link to directory listings; they are not per-record files and were left as they are.
