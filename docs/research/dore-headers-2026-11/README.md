# Doré engravings for the section headers (proposal, November 20, 2026)

Proposal only: nothing here changes the site. The owner picks one option per page, or none, before anything is built.

The idea is to carry the home page's engraving (Doré's Empyrean, Paradiso Canto XXXI) into five section headers: the reading room (`/library/`), Church Documents (`/magisterium/`), the Councils (`/councils/`), the Saints (`/saints/`), and the Summa (`/summa/`). Each sheet shows two or three options in four views: desktop light, desktop dark, phone light, and phone dark (an emulated iPhone 13).

| Page | Sheet | Option A | Option B | Option C |
|---|---|---|---|---|
| Reading room | [library.jpg](library.jpg) | Paradiso XIV | Paradiso III | Paradiso XXI |
| Church Documents | [magisterium.jpg](magisterium.jpg) | Paradiso XVIII | Paradiso XXVIII | |
| Councils | [councils.jpg](councils.jpg) | Paradiso III | Paradiso XII | |
| Saints | [saints.jpg](saints.jpg) | Paradiso XXXI (second plate) | Paradiso XXI | |
| Summa | [summa.jpg](summa.jpg) | Paradiso XII | Paradiso XXVIII | |

Plates are named here only by canto, as their Commons files name them. Any wording about what a plate shows will be checked against the poem before it goes into alt text or a caption.

## How the mock-ups were made

The pages are the current built site, served locally. A script added the engraving to each page's existing `.page-head` in the browser. It used the home hero's layout: a tinted band (`--bg2`) with the engraving filling the right side on desktop and sitting above the title on phones, and a one-line credit under the band. No site file was changed. If an option is chosen, the build would add a `page_art()` helper beside `home_hero()` in `tools/site_copy.py`, one shared rule in `styles/home.css`, self-hosted WebP files in `assets/hero/` (360 and 640 wide, like the Empyrean), and a credit for each chosen image on `/credits/` ("Other images", `tools/credits_page.py`). Contrast in both themes and the phone layout would be checked again on the real build.

## Sources and credits (all public domain)

All plates come from one scanned book on Wikimedia Commons: Dante Alighieri, *Göttliche Komödie*, T. 3, *Das Paradies*, illustrated by Gustave Doré (Berlin: W. Moeser, 1871). Commons tags each scan public domain (PD-old-100-expired; Doré died in 1883). The crops below are cut from the plate area of each page scan and given an automatic levels adjustment, with no other retouching.

| Plate | Commons file | Full size |
|---|---|---|
| Paradiso III | [Gottliche Komodie. T. 3, Das Paradies 1871 (148199779).jpg](https://commons.wikimedia.org/wiki/File:Gottliche_Komodie._T._3%2C_Das_Paradies_1871_%28148199779%29.jpg) | 4,648 × 6,305 |
| Paradiso XII | [Gottliche Komodie. T. 3, Das Paradies 1871 (148199891).jpg](https://commons.wikimedia.org/wiki/File:Gottliche_Komodie._T._3%2C_Das_Paradies_1871_%28148199891%29.jpg) | 4,607 × 6,346 |
| Paradiso XIV | [Gottliche Komodie. T. 3, Das Paradies 1871 (148199950).jpg](https://commons.wikimedia.org/wiki/File:Gottliche_Komodie._T._3%2C_Das_Paradies_1871_%28148199950%29.jpg) | 4,706 × 6,352 |
| Paradiso XVIII | [Gottliche Komodie. T. 3, Das Paradies 1871 (148200062).jpg](https://commons.wikimedia.org/wiki/File:Gottliche_Komodie._T._3%2C_Das_Paradies_1871_%28148200062%29.jpg) | 4,636 × 6,334 |
| Paradiso XXI | [Gottliche Komodie. T. 3, Das Paradies 1871 (148200170).jpg](https://commons.wikimedia.org/wiki/File:Gottliche_Komodie._T._3%2C_Das_Paradies_1871_%28148200170%29.jpg) | 4,670 × 6,334 |
| Paradiso XXVIII | [Gottliche Komodie. T. 3, Das Paradies 1871 (148200346).jpg](https://commons.wikimedia.org/wiki/File:Gottliche_Komodie._T._3%2C_Das_Paradies_1871_%28148200346%29.jpg) | 4,648 × 6,334 |
| Paradiso XXXI (second plate) | [Paradiso Canto 31 - Madonna (148200440).jpg](https://commons.wikimedia.org/wiki/File:Paradiso_Canto_31_-_Madonna_%28148200440%29.jpg) | 3,070 × 3,801 |

Proposed credit line (the home page's pattern): "Gustave Doré, *Paradiso, Canto N*, from the 1871 Berlin *Göttliche Komödie*. Public domain, via Wikimedia Commons." The link points to the file's own Commons page.
