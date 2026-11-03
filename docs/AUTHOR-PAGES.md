# Author pages without a hosted work (Phase A item 2, 2026-11-03)

454 of the 476 hub authors (editorially flagged hub authors excluded) have no work with a hosted text. Their pages no
longer show the Wikipedia excerpt. They show our own intro, then link-only lists with rights badges. See AGENTS.md,
"Author pages without a hosted work", for the template and rules.

## The four Research pages (Horn, Woods, Hahn, Carroll)

Data: `data/modern-authors.json`, a copy of Research's `research/modern-authors-pages.json` (2026-11-03; sources, credentials,
and the verified-vs-unverified ledger are in it). `python3 tools/import_modern_authors.py` writes into the hub, through hubio:

- `intro`: Research's original 60 to 90 word intro, as written (each fact has a source in the file).
- `born`: cleared for Trent Horn (1985 is only on Wikipedia and Wikidata, unsourced).
- `books`: every book with a verified ISBN-13, link-only with a rights badge. The title links its publisher page or Open
  Library record (never Amazon, never scotthahn.com book pages, which sell through Amazon). No year where Research marks it
  unverified or in conflict (What the Saints Never Said, Sacred Then and Sacred Now). Christendom Press ISBNs that are 2004
  reprint records say "ISBN is the 2004 Christendom Press reprint". Thomas Woods: all four books in the file (owner, 2026-11-03).
- `media`: official site, podcasts, YouTube, X, and organization pages, only URLs in `author_pages.CHECKED` (200 to curl,
  ours or Research's check; christendom.edu blocks curl with a WAF 202, so its founder page was read with a fetch tool).
  Left out: Facebook (400 login wall), Rumble (403), mises.org (403), and trenthorn.com's dead YouTube link
  (`youtube.com/user/defense4thefaith`, 404); Horn's channel is `@TheCounselofTrent`.

**No Bookshop.org buttons.** Business asked on 2026-11-03 for no new Bookshop links until the owner approves, and no Bookshop
product page could be verified (Cloudflare 403). The ISBN stays in the data and in `data-isbn` as a disabled hook:
`RESEARCH_BOOKSHOP_BUTTONS` and `AUTHOR_GUIDE_BOOKSHOP_BUTTONS` in `tools/author_pages.py` are False. The edition-guide pages
and the app's Buy tab keep the Bookshop links they already had.

## Templated intro

"<Name> (<dates>) appears in our authors list under <era>, as a <up to three roles from tags>. This page lists <edition
guides>, <works to read at outside sources>, and <books in the Isidore Index, each linked to its catalog record with a
rights badge>." Pages with none of those end with "This page links outside sources about <Name>." The roles come from
`ROLE` in `tools/author_pages.py` and `AU_ROLE` in `app.js` (keep them identical).
