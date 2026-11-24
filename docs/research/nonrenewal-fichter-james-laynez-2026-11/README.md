# Fichter, James Laynez, Jesuit: hand pass and hosting, November 23, 2026

Round 7, Job F. The spec is `spec.json`, the method record with every remaining unread form is `ia-jameslaynezjesui00fich.json`, and the provenance record is `data/sources/ia-jameslaynezjesui00fich.json`.

- **Scan and rights:** `jameslaynezjesui00fich`, St. Louis: B. Herder Book Co., 1944. The basis is pd-nonrenewal, with the evidence recorded in `nonRenewal` (Stanford and NYPL show no renewal; HathiTrust pdus; US publication at least simultaneous with London).
- **Leaves 5–304.** The index (pages 287–299, leaves 306–318) is left out, with a pointer to the scan.
- **Score:** 99.02% raw → **99.57%** (473 of 110,708 words unread; the gate allows 553).

## Method
1. **Contact sheet** (`tools/lexicon/contact_sheet.py`, #159). Word-level crops of the 62 commonest unread forms (559 occurrences) were checked against this scan's page images.
   - 57 forms are printed as read and recorded in `verifiedWords`, mostly names: Polanco, Lainii, Grisar, Broet, Salmeronis, Seripando, Cogordan, and others.
   - Misread forms: "Lainit" for Lainii, "Compania" for Compañia / Compañía, and "pany" for family.
2. **Blank leaves.** Leaves 9, 13, and 182 were checked on the images and carry no print; their OCR was show-through noise. They are now listed in the new spec field `blankLeaves` and read as empty.
3. **Front matter**, from the images:
   - the title page ("Beeb Re DE RY BOO. KR GO." → B. HERDER BOOK CO.);
   - the imprimatur ("✠ Joannes J. Glennon, S.T.D.", Sti. Ludovici) and the dedication (Sociis Meis);
   - the contents, rebuilt line by line with their page numbers;
   - `verseLeaves [[6, 8], [12, 12]]` keeps the printed lines of those pages.
4. **Chapter openings.** All twenty chapter openings and the seven appendix openings were checked on the images.
   - The CHAPTER numbers were restored from OCR debris such as "Gori A Eon Ree iil".
   - The titles are marked `heading` (a new hand-fix flag), so a mixed-case title stands alone instead of running into the first paragraph.
   - The small-capital first words are restored (THE fame, IT WAS, TO THE, MY DEAR, and so on).
   - Two-line titles were joined.
   - "CHAPTER I" and the title-page lines that the running-head rule took for page furniture are kept by keep marks.
5. **Debris pass.** Every line with OCR debris the scorer doesn't count was checked on its crop:
   - digits for letters: "1s" → is, "1n" → in, "U1" → III, "Hol1-" → Holi-;
   - stray bars, underscores, braces, and tildes;
   - running heads with garbled page numbers, which were dropped.
6. **Totals:** 217 hand fixes and 57 verified words. The two automatic repairs left were checked against the images.

## Tool changes (in this PR, with tests)
Neither field changes a book that doesn't use it.
- **`blankLeaves`:** leaves checked on the image to carry no print are read as empty and listed in the record.
- **`"heading": true` on a hand fix:** in prose, that line is its own paragraph.
