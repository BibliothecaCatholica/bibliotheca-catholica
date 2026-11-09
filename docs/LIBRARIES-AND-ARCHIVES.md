# Libraries, integrations, and saints recovery

Checked November 9, 2026 against the current repository, upstream documentation, and the supplied archive.

## Delivered

The Libraries page now opens with six research paths, source-specific search, and a directory with typo-tolerant matching. Search stays in the browser until a visitor submits a query to a chosen collection. Open Library and Corpus Thomisticum are included in the library directory. Catalog matches and scanned editions are not promises of free access or permission to host.

`tools/library_desk.py` produces the shared static/app markup (`data/library-desk.js`). `src/libraries/desk.js` bundles Fuse.js at a pinned version, with its MIT license in `assets/libraries/`. It loads only on the Libraries route. Rebuild with `npm run build`, `python3 tools/build_static.py`, and `npm run build:study`. The latter now builds the library bundle too.

## Existing integrations and next candidates

| Project | Current use or decision | Next useful work |
| --- | --- | --- |
| [Pagefind](https://github.com/Pagefind/pagefind) | Existing hosted-passage search; retained | Keep the index limited to checked editions; do not index borrowed or restricted outside texts. |
| [Mirador](https://github.com/ProjectMirador/mirador) | Existing IIIF scan comparison; retained | Add individually checked IIIF manifests from manuscript institutions; identifiers and rights must come from each item record. |
| [Citation.js](https://github.com/citation-js/citation-js) | Existing APA, BibTeX, and RIS exports; retained | Reuse edition metadata rather than infer missing dates. |
| [Bible Passage Reference Parser](https://github.com/openbibleinfo/Bible-Passage-Reference-Parser) | Existing Scripture lookup; retained | Preserve deuterocanonical coverage and Psalm-numbering cautions. |
| [Fuse.js](https://github.com/krisk/Fuse) | Added: local library directory discovery | Weights library names and matches every query token across name, description, category, and tags. |
| [python-libzim](https://github.com/openzim/python-libzim) | Added: offline recovery tool, separate from the public build | Reads the supplied ZIM and writes a fresh indexed ZIM and browser ZIP. No crawler or Zimit integration. |
| [CatholicOS/CRMEDR](https://github.com/CatholicOS/crmedr) | Research candidate | Eulogy identifiers could improve saint identity matching. A martyrology entry is not proof of a universal-calendar celebration. Review exact data license, version, schema, and person mappings before import. |
| [Torch data](https://github.com/joshx2415/torch-data) | Research candidate | Structured saint relationships could support by/about reading paths. Review dataset provenance and individual source rights before any import; API availability alone is insufficient. |
| [Open Library search](https://openlibrary.org/dev/docs/api/search) | Added outbound catalog search; no live API dependency | An opt-in edition finder could use bounded field selections later. Source results must not inherit our public-domain badges. |

These candidates were examined as upstream projects, not installed wholesale. Existing project-directory entries remain intact. No credentials, visitor accounts, or third-party API polling are introduced.

## CatholicSaints recovery: actual scope

Live CatholicSaints.info and CatholicSaints.mobi requests failed through this environment on November 9. This does not establish a worldwide outage. The owner's supplied `catholicsaints_2026-10.zim`, captured October 25, is the recovery source. Its original bytes are not committed or redistributed on the public site.

The archive contains 422 entries and 186 HTML entries. Recovery found 164 article bodies, including many short definitions and topic lists, not 164 saint biographies. Twenty-two HTML entries contain no article body. The output manifest records those exclusions, every recovered source URL, text hashes, and missing targets. It is a partial snapshot, not a complete website mirror or an updated scrape.

The recovery tool removes active content, embedded resources, forms, styling, and images. It preserves article text and inline source credits, repairs links only when their exact target was captured, marks missing internal targets, and leaves external citations as online links. The ZIP opens from `index.html` without a server; the fresh ZIM includes a native full-text index for Kiwix. Original capture date and recovery date are kept separate.

```sh
python3 -m pip install -r tools/saints-archive-requirements.txt
python3 tools/recover_saints_archive.py /absolute/path/to/catholicsaints_2026-10.zim --output /absolute/path/to/new-output-directory
```

The output directory must not already exist. This optional tool does not run during site builds or fetch the source site.

## Applying the useful structure to the public site

The saved material emphasizes saint names, memorials, patronage, saints' writings, historical feast terminology, and old reference texts. The Libraries research paths now connect those interests to our sourced saints guide, existing hagiography shelf, edition comparisons, and a checked New Advent patron-saints reference. Butler's January–March and July volumes, Bede, and other checked lives are already readable in this site's catalog; no duplicate works were created.

The private recovered collection is not a public download. Its mixture of older sources, modern editorial prose, translations, and images has no established blanket republication license. Public saints records and their hand-checked CatholicSaints links remain unchanged. A future public import needs item-level source evidence; historical feast rules must not become present-day liturgical instructions. User authorization to recover the saved archive does not classify its contents as public domain.
