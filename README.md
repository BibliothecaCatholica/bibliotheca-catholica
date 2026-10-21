# Bibliotheca Catholica

A clean, searchable master index of Catholic authors, Scripture, the Magisterium, references, podcasts and the great digital libraries. Texts remain with their publishers; this site links to the sources.

## Editions, reading lists, Substacks and buy links (v3)

* **Which Edition?** `#/editions`, **Reading Lists** `#/reading`, **Top Catholic Substacks** `#/substacks`.
* Content lives in `tools/editions_data.py`, `tools/reading_lists.py` and `tools/substacks_src.py`. Run
  `python3 tools/build_v3_data.py` to rebuild `data/guide.js` (this also refreshes the Substack "latest posts" snapshot).
* **Affiliate IDs:** paste them into `data/affiliates.js` (`bookshopId`, and `wrap`/`param` per publisher). While they are
  empty, every Buy link works as a plain link.
