# Read-gate proposal: count the OCR damage the gate misses

Round 8, Job C3 (November 23, 2026). **A proposal; nothing here changes a score or a text.** Measured with `tools/ocr_damage.py` (analysis only) on the five hosted `tools/transcribe_scan.py` transcriptions.

## What the gate misses

`transcribe_scan.repair()` reads a token as prefix + word + suffix with ASCII letters only, and `unread()` counts a token only when `repair()` calls it unknown. Four kinds of damage therefore pass as read:

1. **Accented letter inside a word** (`accent-in-word`): the token fails the pattern, so it is never checked. Misread accents ("Cloriviére", "rémischen", "Schóningh", "péres") and Greek read as accented Latin letters pass, and so do correct foreign words that were never verified ("Maréchal").
2. **Symbol inside a word** (`symbol-in-word`): a backslash or other symbol ("IIX\\ovcuos", mangled Greek) fails the pattern the same way.
3. **Note digit glued to a word** (`digit-glued`): the digit is taken as a prefix, so "1bid" scores as the known word "bid", and "1Shahan" as "Shahan".
4. **Note mark read as a symbol** (`note-mark`): superscript note numbers read as °, ®, ©, ¢, or | have no letters and are skipped.

## Before and after

"Words only" counts kinds 1 to 3 as unread; "all" also counts kind 4. Words the edition record already verifies, and accented forms used in the proofread (non-OCR) texts, are not counted.

| Book | Words | Unread now | Score now | + word damage | Words only | + note marks | All |
|---|---|---|---|---|---|---|---|
| Grant, *John England* (`ia-johnenglandameri00gran`) | 53,063 | 178 | 99.66% | 47 | 99.58% | 1 | 99.57% |
| Furfey, *The Mystery of Iniquity* (`ia-mysteryofiniquit00furf`) | 58,909 | 282 | 99.52% | 25 | **99.48%** | 135 | **99.25%** |
| Cassidy, *Molders of the Medieval Mind* (`ia-moldersofmedieva00cass`) | 41,563 | 170 | 99.59% | 16 | 99.55% | 211 | **99.04%** |
| Walsh, *High Points of Medieval Culture* (`ia-highpointsofmedi00wals`) | 94,629 | 338 | 99.64% | 20 | 99.62% | 50 | 99.57% |
| Haas, *Rights and Wrongs in Industry* (`ia-rightswrongsinin00haas`) | 10,663 | 40 | 99.62% | 1 | 99.62% | 8 | 99.54% |

Bold: below the 99.5% gate. With word damage counted, Furfey falls just under the gate (99.48%); with note marks too, Furfey (99.25%) and Cassidy (99.04%) fall under it. All five are hosted; none is withdrawn by this proposal. Each would get a `-r2` edition that fixes the damage against the page images (Job C2).

## Proposal

- `unread()` counts kinds 1 to 3 as unread unless the word is verified (`verifiedWords`) or is an accented form used in the proofread texts. Correct foreign words are then verified once on the image, as names already are.
- Kind 4 is reported beside the score, not in it: a misread note mark loses a footnote number, not a word. A hosted text should still have none left, so the hosting checklist adds "no note-mark symbols remain" (each restored to its number or `[Note: ...]` placement).
- The read-gate record gains `damage` counts by kind, so QA can see them without rerunning.
- Owner decision: this changes how the gate is measured (PROJECT-RULES rule 1, "Read gate"), so it waits for the owner. Nothing is rescored until then.

## What each book needs (Job C2 findings, for the `-r2` editions)

- **Grant, *John England***: accent-in-word 47: `Broénté`, `Bruté,`, `Brénté,`, `Cloriviére`, `Cloriviére:`, `Maréchal`, `Maréchal).`, `Maréchal,`, `Maréchal.`, `Maréchal’s`; note-mark 1: `|`.
- **Furfey, *The Mystery of Iniquity***: note-mark 135: `#®`, `$500.*°`, `*©`, `*°`, `*°The`, `Church.*°`, `Herodians.*°`, `Madianites.*®`, `Paul.*°`, `accident.*®`; accent-in-word 21: `(Gütersloh:`, `Casté`, `Desclée`, `Kraków`, `Ouvriére`, `Probléme`, `Razoén`, `Schóningh,`, `Supplément,`, `Téqui,`; digit-glued 1: `5On`; symbol-in-word 3: `\.2212050`, `“IIX\ovcuos`, `“TT\ovctos`.
- **Cassidy, *Molders of the Medieval Mind***: note-mark 211: `*®`, `*°`, `*°*`, `*°’`, `1°`, `240.”°`, `24107d.,°8:32.`, `250.*°`, `255.7°`, `258,?°`; digit-glued 8: `*1bid.,`, `1Cf.`, `1De`, `1Quoted`, `1Shahan,`, `2Taurie,`, `47De`, `5oo`; accent-in-word 8: `(München:`, `Flenri-Irénée`, `Péglise`, `d’archéologie`, `péres`, `rémischen`, `sidé`, `siécles`.
- **Walsh, *High Points of Medieval Culture***: note-mark 50: `Allegory®`, `Anselm.’®`, `Arts,’®`, `Century®`, `France,®`, `Freedom,®`, `History,®`, `Ireland,®>`, `XIIe®`, `accomplishment.|`; accent-in-word 19: `Averroés,`, `Aétius,`, `Bibliothéque`, `Brémond,`, `Com-payré’s`, `Compayré,`, `Compayré’s`, `Faérie`, `Héloise`, `Jörgensen’s`; symbol-in-word 1: `\`.
- **Haas, *Rights and Wrongs in Industry***: note-mark 8: `|`, `©`; accent-in-word 1: `reémployed`.

Every listed token is to be checked on the page image before it changes; some accented forms are correct as printed ("Maréchal", "Desclée", "Kraków") and become verified words, not corrections.
