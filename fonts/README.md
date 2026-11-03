# Fonts

Self-hosted copies of the Google Fonts files the site used to load from fonts.googleapis.com (Phase B item 5): Cormorant Garamond, EB Garamond, and Inter, every subset Google serves for the css2 request in `styles/fonts.css`. Each family is under the SIL Open Font License 1.1; the license texts are `OFL-cormorantgaramond.txt`, `OFL-ebgaramond.txt`, and `OFL-inter.txt` (from github.com/google/fonts). `styles/fonts.css` gives each file its unicode-range, so a browser downloads only the subsets a page uses. `index.html` preloads the two latin faces that paint the first screen.
