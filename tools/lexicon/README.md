# Verified lexicon

A reusable list of readings that a reviewer has already checked against a page image in one of the library's scans. Its only use is to **propose** a reading for an unread OCR form in another book. A proposed reading counts as read in that book only after a reviewer checks it against that book's own page image and records it in the book's spec (`verifiedWords`, or a `handFixes` entry). The read gate (99.5%) and `tools/transcribe_scan.py` are unchanged: the transcription tool never reads this lexicon.

## Inputs (edited by hand)

- `docs/research/*/spec*.json`: each spec's `verifiedWords` and `handFixes`, all of them checked on the page images of that scan.
- `sources/languages.json`: the language of every verified word, reviewed in context in the hosted text. The lists are Latin, Irish, German, French, Spanish, Greek (transliterated, plus one word in Greek script), proper names, and English. Spanish (three words quoted in Meyer's notes) and English are extra lists; English is for English words the scorer's vocabulary lacks ("baseball", "totalitarianism", "niblicks"). The build fails if a spec verifies a word this file doesn't classify.
- `sources/confirmed-repairs.json`: automatic repairs by the transcription tool that were then checked one by one on the page images. So far these are the 14 Meyer repairs from November 23, 2026. The tool's other automatic repairs aren't listed, because they weren't checked individually.
- `sources/seeds.json`: optional seed lists from openly licensed sources. Each entry must record its source, URL, and licence. None is used yet.

## Outputs (generated; never edit by hand)

- `words/<language>.json`: each word, with every edition and spec that verified it.
- `repairs.json`: word-level OCR-to-reading pairs. They come from the hand fixes (aligned one for one, similar words only, no case-only changes) and from the confirmed repairs.

Rebuild with `python3 tools/lexicon/build_lexicon.py`. `tests/test_lexicon.py` fails if the committed files differ from a fresh build.

## Proposing candidates

```
python3 tools/lexicon/build_lexicon.py --propose Calahoira hved
```

For each form, the tool offers these candidates, in this order:
1. an exact earlier OCR-to-reading pair;
2. the same word already verified in another book;
3. a verified word reached through one of the transcription tool's own OCR confusions (`CONFUSIONS`);
4. a verified word one letter away, for forms of five letters or more.

Every candidate carries the status "candidate: check on this book's page image before recording it".

## Contact sheet (faster hand pass)

```
python3 tools/lexicon/contact_sheet.py SPEC --cache DIR --out SCRATCH_DIR
python3 tools/lexicon/contact_sheet.py SPEC --out SCRATCH_DIR --apply DECISIONS.json
```

The first command builds a review sheet in a scratch directory. It refuses to write inside the repository, and the sheets are never committed. The sheet:
- groups the book's remaining unread forms, with forms that share a lexicon candidate kept together;
- crops each occurrence from the scan's own page image, using the line the transcription tool chose, with the word boxed;
- pre-fills the lexicon's best candidate.

The output is `index.html`, numbered PNG sheets for review without a browser, and `occurrences.json`.

The reviewer marks each form "printed as read" or "misread; reading …" and exports the decisions. `--apply` writes them into the spec: printed forms go into `verifiedWords`, and each misread line becomes a `handFixes` entry. Each decision must carry the date it was checked.

Verifying words can change which OCR engine wins a line, so after applying:
1. re-run the sheet;
2. drop any hand fix whose line the tool now reads correctly;
3. compare every changed line against the image.
