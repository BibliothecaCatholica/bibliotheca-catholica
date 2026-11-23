# Meyer, Selections from Ancient Irish Poetry: hand-pass status, November 23, 2026

Round 4, Job 2b. Not hosted: the raw score is below the 99.5% read gate, and the job's rule is to host only at 99.5% or above.

- **Scan and rights:** `selectancientiri00meye` is the New York, E. P. Dutton issue of 1911, checked on the title page image. The rights basis is pd-date (1911).
- **Measured** with `spec.json` (`layout: verse`, Tesseract `eng+lat` per line, the Round 4 range of leaves 4–145; Round 5 below narrowed `spec.json` to 4–135): **98.06%**, 344 of 17,725 unread. The gate allows 88, so 256 words are still to read, across 241 distinct forms. The method and every unread form are in `ia-selectancientiri00meye.json`. Without the verse layout it measured 97.48% (`../irish-editions-2026-11/`).
- **What blocks a fair pass:**
  1. **Verse layout covers the whole book.** `layout: verse` keeps every printed line break, which the poems need, but the prose introduction and the notes then keep their line-end hyphens unjoined ("velopment", "autho-" / "rity"). That costs about 20 unread words and breaks the prose. `tools/transcribe_scan.py` needs a per-leaf layout range (verse only for the poems) before the hand pass.
  2. **Some automatic repairs are wrong for Irish.** For example, "Caill" (Irish *caill*, "wood") becomes "Call". All 17 repairs need checking on the images, and Irish forms must be verified, not repaired. The brief says not to normalize spellings.
  3. **Most of the 241 forms are Irish names and place names** (Aed, Carbery, Liadin, Curithir, Ériu, Guare, Aidne, Fothad, Marvan, Pangur), each to be checked on the page image.

## Round 5 (November 23, 2026): per-leaf verse ranges

- **Tool:** `tools/transcribe_scan.py` now takes `verseLeaves: [[first, last], ...]`. Verse layout (printed lines and stanza breaks kept, no rejoins) applies only to those leaves, and every other leaf is prose. A book without the field builds exactly as before: Grant, Furfey, and Cassidy re-transcribe byte for byte. Walsh's pinned text was already not reproducible with the #143/#149 tool before this change, and this change doesn't affect it.
- **Spec:** `verseLeaves: [[20, 131]]` for the contents and the poems. The title page, dedication, introduction (leaves 4–19), and notes (132–135) are prose. `lastLeaf` is now 135, which leaves out four blank leaves and the library card pocket.
- **Score:** **98.16%** (325 of 17,670 unread; the gate allows 88). The verse-only run read 98.06%. 237 words are still to read, across 222 distinct forms, mostly Irish names (Aed, Carbery, Liadin, Curithir, Guare, Aidne, Fothad, Marvan, Pangur).
- **Automatic repairs, all checked on the page images:**
  - 14 are right: literature, cliff, that, flowers, flame, Carroll, blight, polished, Plentiful, would, dwelling, solicited, published, lived.
  - 2 were wrong and are now fixed: "Caill Cuan !" is Irish (*caill*, wood), so it is now verified and no longer repaired to "Call"; and German "für" is restored by hand on leaves 132 and 134 (it had become "fur").
- **Not hosted:** below 99.5%. Next is a hand pass of the 222 forms against the page images, without normalizing Irish spellings.

## Round 6 (November 23, 2026): hand pass with the contact sheet

- **Tool:** `tools/lexicon/contact_sheet.py` grouped the 227 unread forms (325 occurrences) and cropped every occurrence from the scan's own page image. All 325 were located line by line. Every crop was checked by eye; the sheets themselves are working files and were not committed.
- **Printed as read (`verifiedWords`, 208 forms):** mostly Irish names and places (Aed, Liadin, Curithir, Carbery, Guare, Aidne, Fothad, Marvan, Pangur, Ériu). The rest are Irish words (*fidchell*, *mBó*, *Ochone*, *Mairg*), Latin, German, French, and Spanish quoted in the introduction and notes, and rare English or Scots words (shieling, blaeberries, bragget, chiels, heathpoults). Two line-end fragments are also kept, because this verse layout doesn't rejoin them: "chal-" / "lenged" and "privi-" / "osity". Irish spellings are kept as printed, not normalized.
- **Misreadings fixed against the image:**
  - Xoisi → Noisi (3);
  - Mohng → Moling (2);
  - Movlurg → Moylurg;
  - vearnful → yearnful;
  - Finnhath → Finnliath;
  - Rilgarrow → Kilgarrow;
  - Yerily → Verily;
  - Praver → Prayer;
  - Uke → like;
  - Jouvnal → Journal;
  - tCraeb → Craeb;
  - Carberj^ → Carbery;
  - Moinmo^ → Moinmoy;
  - the contents' small capitals "deirdre's LAMENT" and "to crinog" → "DEIRDRE'S LAMENT" and "TO CRINOG";
  - a handwritten library date on leaf 9, dropped.
  The five corrected names and words (Noisi's, Moylurg, yearnful, Finnliath, Kilgarrow) were also verified as printed. With them verified, Tesseract's reading of five lines now matches the image exactly, so those lines need no hand fix.
- **Line-choice check:** verifying words changes which engine wins some lines, so every changed line was compared before and after. Three small-capital headings (MARVAN, GUARE, LIADIN) are kept in capitals by hand, matching the image. Two Tesseract superscripts ("Lugh,?" and "Bethech.!") and an opening quote ("*O Cormac") are corrected to the printed "Lugh,³", "Bethech.¹", and "‘O Cormac".
- **Score:** **99.98%** (3 of 17,668 unread), up from 98.16%. The three words left are footnote numbers printed against a word (Lugh,³ Bethech.¹ Moinmoy.¹), kept as printed. The method and remaining forms are in `ia-selectancientiri00meye.json`.
- **Not hosted** in this round. The book now passes the read gate, so hosting it is a separate PR for the owner to approve.
