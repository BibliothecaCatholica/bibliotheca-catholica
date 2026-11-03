# Author pages without a hosted work (Phase A item 2, 2026-11-03)

454 of the 476 hub authors (editorially flagged hub authors excluded) have no work with a hosted text. Their pages no
longer show the Wikipedia excerpt. They show our own intro, then link-only lists with rights badges. See AGENTS.md,
"Author pages without a hosted work", for the template and rules.

## Hand-written intros (hub `intro`)

Each sentence is a plain fact taken from the sources below (all checked on 2026-11-03).

- **Trent Horn** (`trent-horn`): https://www.trenthorn.com/about (convert, three master's degrees, Catholic Answers,
  The Counsel of Trent), https://www.trenthorn.com/books/ (titles).
- **Thomas E. Woods Jr.** (`thomas-e-woods`): https://www.thomasewoods.com/abouttom1.htm, https://tomwoods.com/about,
  and the encyclopedia.com biography (Columbia PhD in history, book titles).
- **Warren H. Carroll** (`warren-h-carroll`): https://www.christendom.edu/about/warren-h-carroll/ (conversion in 1968,
  founding in 1977, president until 1985, History chair until 2002), Wikipedia and Open Library (dates, A History of Christendom).
- **Scott Hahn** (`scott-hahn`): https://stpaulcenter.com/scott-hahn/bio/ and https://stpaulcenter.com/history/
  (former Presbyterian minister, entered the Church in 1986, Franciscan University since 1990, St. Paul Center founder, books).

## Official links added to the hub (all returned 200 on 2026-11-03)

- Trent Horn: https://www.trenthorn.com/ and https://www.trenthorn.com/books/ (curl needs a browser User-Agent; plain curl gets 406).
- Warren H. Carroll: https://press.christendom.edu/ (publisher of A History of Christendom).
- Not added: tomwoods.com for Thomas Woods (not in the data or a Research file; a candidate for the owner).
- Excluded from "Official site, talks, and podcasts" because they failed the check: coramfratribus.com (403), mysteriousworld.com (no response).

## Templated intro

"<Name> (<dates>) appears in our authors list under <era>, as a <up to three roles from tags>. This page lists <edition
guides>, <works to read at outside sources>, and <books in the Isidore Index, each linked to its catalog record with a
rights badge>." Pages with none of those end with "This page links outside sources about <Name>." The roles come from
`ROLE` in `tools/author_pages.py` and `AU_ROLE` in `app.js` (keep them identical).
