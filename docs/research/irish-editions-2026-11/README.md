# Irish editions scoping, November 23, 2026

Round 3, Job 6: scoping only, no hosting. Plummer, Reeves, and Meyer (the HOLDS row of November 15) are each matched to a free Internet Archive scan, dated, given a rights basis, and measured raw.

## Method

- The scans were found with archive.org's advanced search. The metadata API confirmed each is public: no `access-restricted-item`, not dark.
- The rights basis is `pd-date` for all three, since each was first published before 1931 (PROJECT-RULES rule 1).
- The raw score comes from `tools/transcribe_scan.py --measure` with the specs in `measure.json`:
  - archive.org's djvu.xml OCR, with running heads and page numbers removed;
  - leaves 4 to the end, with nothing left out;
  - no hand fixes and no second OCR.
- Each `<edition>.json` here records the method (`readGate`) and every unread form with its count.
- The items' download servers were added to this environment's allowed hosts on November 23, at the owner's request.

| Edition | Scan | Leaves | Rights | Raw OCR | Words still to read for 99.5% | Distinct unread forms |
|---|---|---|---|---|---|---|
| Kuno Meyer, *Selections from Ancient Irish Poetry* (New York: E. P. Dutton, 1911) | `selectancientiri00meye` | 146 | pd-date (1911) | 97.48% (445 / 17,688) | 357 | 321 |
| Charles Plummer, *Bethada Náem nÉrenn*, vol. II, translations (Oxford: Clarendon Press, 1922) | `bethada02plumuoft` | 420 | pd-date (1922) | 94.19% (10,257 / 176,567) | 9,375 | 3,679 |
| Adamnan, *The Life of Saint Columba, Founder of Hy*, ed. William Reeves (Edinburgh: Edmonston and Douglas, 1874) | `bub_gb_8VULAAAAYAAJ` (Google scan) | 572 | pd-date (1874) | 88.91% (24,981 / 225,161) | 23,856 | 15,994 |

## Hand-pass size

- **Meyer:** the smallest. Its unread forms are mostly Irish names (Aed, Liadin, Carbery, Curithir, Guare, Marvan), which can be verified on the images. It is verse, so it needs `layout: verse`.
- **Plummer:** dominated by saints' and place names (Maedoc and "Maed" alone account for over 1,000 occurrences, plus Aed, Ruadan, Coem, Bairre, Moeog, Breifne, and Abban), so verifying names clears much of the gap. There are also "wiU" and "tiU" misreads that a second OCR may fix.
- **Reeves:** a Google scan with a "Digitized by Google" footer on every page, and long Latin and Irish notes. The Latin can be sample-verified under the read-gate process. Even so, this is the largest pass. A cleaner scan of the same printing would be worth looking for first.

Other scans of the same books exist but were not measured:
- a London Constable 1911 Meyer, `cu31924026825160`;
- Plummer vol. I with the Irish texts, `bethadanemnr01plumuoft`;
- the 1857 Reeves Latin edition, `MN5139ucmf_2`.
