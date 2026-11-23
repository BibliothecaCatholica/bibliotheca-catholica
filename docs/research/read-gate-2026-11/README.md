# Read-gate re-measurement, November 23, 2026

Every book that HOLDS lists below the 99.5% read gate, measured again with `tools/transcribe_scan.py --measure` under the owner-approved process (PROJECT-RULES rule 1, "Read gate", November 22, 2026). No hand fixes or verified words are applied, so these are raw OCR scores. Unread words are counted in full: the earlier scorer counted at most 8 per flagged paragraph, so it overstated every figure recorded before this date.

- `measure-archive.json`: the six specs, archive.org's djvu.xml OCR only. Results are in `archive-only/`.
- `measure-tesseract.json`: the same specs with `secondOcr` (Tesseract 5.3.4, `eng+lat+ita`, page images at scale 1). Each line uses whichever engine leaves fewer unread words. Results are in `tesseract/`.
- Each result file records the method (`readGate`: engine, line choices by engine, leaves scored, omitted back matter, date) and every unread form with its count (`unreadForms`).

| Book (edition) | Leaves scored | Back matter left out | archive.org only | with Tesseract per line | Lines taken from Tesseract | Earlier recorded |
|---|---|---|---|---|---|---|
| Grant, *John England* (`ia-johnenglandameri00gran`) | 4–186 | none | 99.17% (441 / 53,130) | **99.21%** (420 / 53,132) | 32 of 5,855 | 99.13% |
| Cassidy, *Molders of the Medieval Mind* (`ia-moldersofmedieva00cass`) | 4–191 | bibliography pp. 181–188, index pp. 189–194 | 99.00% (417 / 41,663) | **99.19%** (339 / 41,660) | 76 of 5,656 | 98.87% |
| Furfey, *The Mystery of Iniquity* (`ia-mysteryofiniquit00furf`) | 4–193 (endnotes kept) | index pp. 191–192 | 99.14% (506 / 58,909) | **99.18%** (483 / 58,913) | 21 of 7,014 | 99.12% |
| Fichter, *James Laynez, Jesuit* (`ia-jameslaynezjesui00fich`) | 5–304 | index pp. 287–299 | 98.96% (1,151 / 111,004) | **99.02%** (1,088 / 111,008) | 72 of 10,705 | 98.87% |
| Walsh, *Saint Teresa of Avila* (`ia-saintteresaofavi00wals`) | 10–609 | index pp. 585–592 | 98.66% (3,414 / 254,194) | **98.82%** (3,001 / 254,432) | 408 of 24,343 | 98.64% |
| Huber, *St. Anthony of Padua* (`ia-stanthonyofpadua00hube`) | 6–180 | bibliography pp. 164–199, Latin sermon appendix pp. 200–204, index pp. 205–209 | 95.49% (2,632 / 58,328) | **95.69%** (2,513 / 58,326) | 119 of 6,541 | 99.24% (not reproducible; see HOLDS) |

None of the six reaches 99.5% on OCR alone. The gap to the gate is the hand-pass size: about 155 more words read for Grant (420 unread, at most 265 allowed), 131 for Cassidy, 189 for Furfey, 533 for Fichter, 1,729 for *Teresa*, and 2,222 for Huber. Many unread forms are proper names or Latin, Spanish, Italian, or French words. Under the new process those can be counted as read by sampling at least 10% of each language's distinct forms (minimum 30) against the page images, so the real hand-pass size is smaller than these gaps.

Tesseract helps most where archive.org's OCR broke whole lines (Cassidy gains 0.19 points). On the cleaner scans it adds 0.04 to 0.06 points (Grant, Furfey, Fichter); *Teresa* and Huber gain 0.16 and 0.20. Both engines are kept: archive.org stays the default and Tesseract replaces a line only when it reads strictly more words with about the same word count.
