# Bibliotheca Catholica

A clean, searchable master index of Catholic authors, Scripture, the Magisterium, prayers, references, podcasts, and the great digital libraries. Texts remain with their publishers; this site links to the sources.

## Editions, reading lists, Substacks, and buy links (v3)

* **Which Edition?** `#/editions`, **Reading Lists** `#/reading`, **Top Catholic Substacks** `#/substacks`.
* Content lives in `tools/editions_data.py`, `tools/reading_lists.py`, and `tools/substacks_src.py`. Run
  `python3 tools/build_v3_data.py` to rebuild `data/guide.js` (this also refreshes the Substack "latest posts" snapshot).
* **Affiliate IDs:** paste them into `data/affiliates.js` (`bookshopId`, and `wrap`/`param` per publisher). While they are
  empty, every Buy link works as a plain link.

## Prayers, Doctors' free texts, Rare & Obscure, and Projects (v4)

* **Prayers & Devotions** `#/prayers`: public-domain prayer texts live in `data/prayers.js`; the links come from the resources data.
* **Read free** panels on every Doctor's page come from `data/doctors.js`. **Rare & Obscure** `#/rare` uses `data/rare.js`, and **Projects & Translations** `#/projects` uses `data/projects.js`.
  All three are built from the research files by `tools/build_v4_data.py`. Every one of these texts is an outbound link; none is hosted here.
