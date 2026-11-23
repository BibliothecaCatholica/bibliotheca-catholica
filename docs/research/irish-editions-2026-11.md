# Irish editions scoping, November 23, 2026

Round 3, Job 6: scoping only, no hosting. Plummer, Reeves, and Meyer (the HOLDS row of November 15) are each matched to a free Internet Archive scan, dated, given a rights basis, and scored raw.

## Method

- The scans were found with archive.org's advanced search. The metadata API confirmed each is public: no `access-restricted-item`, not dark.
- The rights basis is `pd-date` for all three, since each was first published before 1931 (PROJECT-RULES rule 1).
- **The raw score is an estimate.** It comes from archive.org's plain-text OCR (`/stream/<id>/<id>_djvu.txt`), with line-end hyphens rejoined and the whole book counted, including front and back matter. Words are checked against the vocabulary of `tools/transcribe_scan.py`.
- The positional `djvu.xml` and the page images come from each item's own download server, which this environment's network does not allow. So this is not a `--measure` run: no running heads were removed and no second OCR was tried. A scored run will read higher.
- The hand-pass size is the number of distinct unread forms, most frequent first, that would need verifying or fixing to reach 99.5%.

| Edition | Scan | Leaves | Rights | Raw OCR | Words still to read for 99.5% | Distinct forms |
|---|---|---|---|---|---|---|
| Kuno Meyer, *Selections from Ancient Irish Poetry* (New York: E. P. Dutton, 1911) | `selectancientiri00meye` | 146 | pd-date (1911) | 96.98% (542 / 17,956) | 453 | about 311 of 400 |
| Charles Plummer, *Bethada Náem nÉrenn*, vol. II, translations (Oxford: Clarendon Press, 1922) | `bethada02plumuoft` | 420 | pd-date (1922) | 93.38% (11,838 / 178,918) | 10,944 | about 3,800 of 4,701 |
| Adamnan, *The Life of Saint Columba, Founder of Hy*, ed. William Reeves (Edinburgh: Edmonston and Douglas, 1874) | `bub_gb_8VULAAAAYAAJ` (Google scan) | 572 | pd-date (1874) | 87.45% (28,799 / 229,490) | 27,652 | about 16,700 of 17,845 |

Most frequent unread forms:
- **Meyer:** Aed, Liadin, Carbery, Curithir, Guare, Marvan. These are mostly names. The book is verse, so it needs `layout: verse`.
- **Plummer:** Maedoc (over 1,200 counting "Maed"), Aed, Ruadan, Coem, Bairre, Moeog, Breifne, Abban. These are saints' and place names that verification would clear in bulk, plus "wiU" and "tiU" misreads.
- **Reeves:** the scan's "Digitized by Google" footer (486), Colg, Tiree, Baithene, Hinba. Much of the rest is Latin and Irish in the notes (sample-verifiable).

Other scans of the same books exist (a London Constable 1911 Meyer `cu31924026825160`, Plummer vol. I with the Irish texts `bethadanemnr01plumuoft`, the 1857 Reeves Latin edition `MN5139ucmf_2`). They were not scored.

## Unblocker

A scored run (`tools/transcribe_scan.py --measure`) needs the items' download servers allowed in this environment:
- ia903207 and ia803207 (Plummer);
- ia600609 and ia800609 (Reeves);
- ia600602 and ia800602 (Meyer).

All are `.us.archive.org`. After that, hand-pass Meyer first: it is the smallest, with about 311 forms, mostly names.
