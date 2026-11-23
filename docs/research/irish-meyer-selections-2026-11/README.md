# Meyer, Selections from Ancient Irish Poetry: hand-pass status, November 23, 2026

Round 4, Job 2b. Not hosted: the raw score is below the 99.5% read gate, and the job's rule is to host only at 99.5% or above.

- **Scan and rights:** `selectancientiri00meye` is the New York, E. P. Dutton issue of 1911, checked on the title page image. The rights basis is pd-date (1911).
- **Measured** with `spec.json` (`layout: verse`, Tesseract `eng+lat` per line, leaves 4–145): **98.06%**, 344 of 17,725 unread. The gate allows 88, so 256 words are still to read, across 241 distinct forms. The method and every unread form are in `ia-selectancientiri00meye.json`. Without the verse layout it measured 97.48% (`../irish-editions-2026-11/`).
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
