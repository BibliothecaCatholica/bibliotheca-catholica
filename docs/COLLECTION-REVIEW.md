# Collection review and reading access

> Historical review from October 21, 2026. The 49-work totals below describe that snapshot and have since changed; use the current [README](../README.md) and live catalog for present counts. Lewis preview availability can vary by provider, location, and account.

## Translation collections and discovery

Checked November 10, 2026. The maintained evidence is [translation-collections.json](../data/sources/translation-collections.json). This is a bibliographic and access review, not independent certification of translation fidelity.

| Source | Verified access and scope | Implemented decision |
|---|---|---|
| Mind of the Church | Online English works, with PDF and EPUB formats on the inspected Sixtus and Contzen pages | Added library resource and link-only catalog records for *The Holy Library* (1566 Latin source) and *Ten Books of Politics* (1629 Latin source). Translation method and independent review are unverified. |
| Morals of the Church | Existing resource; linked from its companion site | Retained its single resource record and clarified historical manuals versus modern translations. |
| Acta Sanctorum | Current homepage and About report January through November 10, the endpoint of the published Bollandist series. Older cached pages are stale. Per-entry HTML/TXT/JSON and bulk JSONL/TXT exports are advertised. | Added the reference resource and a contextual link on the hagiography shelf, including method, known defects, and CC BY-NC 4.0 links. No automatic saint-name matching. |
| The Faith Received | Protestant-hosted library; PL, PG, and Roman Catholic collection entry points verified. Its transparency policy describes AI labels, original-language comparison, issue histories, and Reviewed / Needs Review statuses. | Added the library and both patristic collection resources, with AI and independent-coverage qualifications. No full-text ingestion or claim of complete PL/PG coverage. |

All seven new resource URLs were checked against the existing resource records before adding them. The two new work identities do not duplicate selected works already in `data/library.json`; different modern translations must remain distinct from their ancient or early modern originals. Collection size and free access do not establish item-level quality or redistribution permission.

**Hosting assessment:** Current project rules limit hosted editions to the pre-1931 selection policy. These modern translations remain at source. Acta's translator and structured edition have an express noncommercial license; compatibility with this affiliate-supported project has not been established. No blanket redistribution grant was verified for The Faith Received or Mind of the Church. An intermediary's recommendation does not establish permission from another project's rights holder. No source text was copied or bulk-downloaded.

**Prioritized additional catalog research:** Bellarmine, Suárez, Cajetan, and Báñez are advertised in The Faith Received's Catholic collection and have no selected work records here. Inspect actual titles, original editions, extent, and each translation's review status before making records. Dynamic collection inventories were not fully available to the research client, so individual holdings and completeness remain unverified. Existing Augustine, Aquinas, and other patristic works should gain a separately credited edition only after a precise match, rather than another duplicate work. Riccioli's *Almagestum Novum*, Book IX is a verified additional source lead, distinct from the whole work.

The homepage now gives reading and choosing a book priority, keeps four starter works and three discovery paths, and puts the full section directory behind a native disclosure. The global navigation keeps five primary routes and exposes the other collections under More sections. The former duplicate section-card wall, stats row, second Index search, author strip, promotional banner, and repeated library links have been removed from the homepage. Shared Python copy generates both the plain HTML and interactive home, retaining crawlable links and the existing reader continuation and daily panel.

## Why Lewis previously led to a dead end

The initial eight Lewis entries cited the same academic bibliography to establish titles and publication dates. Those were reference records, and the later reading path reused them without adding a reading destination. An author biography or bibliography does not satisfy a reading action.

All eight now have distinct, title-specific excerpts or edition previews. PBS supplies selected passages from Mere Christianity and The Four Loves; Google Books and Google Play Books supply limited samples for the other six. No complete Lewis text was copied. The records identify his Anglican tradition. Preview availability can vary by location and account. WorldCat and Open Library title searches provide a path toward complete copies, with availability left to the provider.

## Changes across the collection

- All 49 selected works have meaningful descriptions. Direct card actions distinguish the hosted reader, full texts at source, and excerpts/previews. Bibliographic references are expandable support material.
- Reading-list and collection filters distinguish complete reading links from samples. Searches handle accents and initials such as “CS Lewis”; library filters persist when returning from a work.
- Every edition guide and reading-list recommendation without a complete free reading link offers library searches alongside its edition suggestions. Such searches do not guarantee a digital loan.
- True Devotion to Mary now links to the Montfort Missionaries' own complete PDF. The Spiritual Combat links to its identified Isidore ebook record; it is not confused with the adapted Unseen Warfare.
- New Advent's parallel Bible is labeled as Knox English, not Douay-Rheims. Bible Gateway's RSV-CE is distinguished from RSV-2CE.
- The Catholic Primer resource was removed after its URL redirected to an unrelated school's events page. The obsolete Vulgate directory link was replaced with the project's working search page. Aquinas links use the publisher-advertised project root after the previous deep URL returned 404 to the audit client.
- Four writings traditionally placed under Clement of Rome are labeled as spurious attributions, following New Advent's own index.
- All 6,633 imported book rows were checked for duplicate IDs and valid table references. All 476 author profile IDs are unique, and imported author links point to existing profiles. Seventy-five imported books list no files; their cards and detail pages say so and do not offer an empty Calibre reader.

## Evidence and limits

`collection-audit.json` records the scope, counts, endpoint responses, redirects, and editorial dispositions. The network sweep includes the curated source destinations, Doctors, Rare & Obscure, Projects, and author reading links. Reachability does not prove that a linked edition is complete, correctly attributed, or authorized for redistribution. An automated 403, timeout, or 503 is treated as inconclusive; it is not a reason to delete an otherwise useful collection. The imported ebook files were not individually downloaded or read.

This is a catalog and access review, not a claim that every imported book received a textual, theological, or copyright review. The imported Isidore collection retains its unreviewed status. The selected reader's existing source files and their notices are unchanged.

## Maintaining the review

Run `npm run build` and `npm test` after catalog edits. Use `python tools/audit_collection.py --network --resume` for a broader check; `--resume` reuses prior endpoint results and checks newly added destinations. Remove `--resume` for an intentional fresh sweep. Failures and unexpected redirects need manual review before changing a source. Network checking is separate from CI.

Final sweep: 1,629 distinct destinations; 1,607 returned a response without a request error and 22 checks were inconclusive. All 49 selected works have complete-text access (41) or a labeled sample (8); 22 have hosted reader copies. The 69 edition guides and 115 reading-list entries were inventoried. Thirty-one edition guides still have no complete free copy listed and offer library searches.
