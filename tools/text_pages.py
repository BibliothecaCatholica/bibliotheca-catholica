"""Chapter and story pages for hosted reading-room texts (deep-link gaps, 2026-11-09).

Each entry below names a hosted edition in data/library.json and, for every chapter or story, the
heading block exactly as it stands in that file plus the opening and closing words that Research
mapped (research/deep-link-gaps-2026-11-09.json). tools/build_text_pages.py (part of `npm run build`)
finds each heading in the file's splitText() blocks (the same blocks as the reader), checks that the
text's SHA-256 still matches the edition, checks that the first and last paragraphs of each part
start and end with the mapped words, and writes data/text-pages.json (block ranges, for
tools/build_static.py) and data/text-pages.js (window.TEXT_PAGES, the short contents list the app's
work page shows). The static pages live at /work/<work>/<kind>/<NN-slug>/; the app keeps the
static page as the view (staticOnly() in app.js) and links into the reader for highlights and notes.

Only hosted, rights-checked Gutenberg editions may appear here (content rules 1 and 2). Never add a
flagged title.
"""
# kind: 'ch' (chapters) or 'story' (stories). Each part: (slug, number label, title, heading block,
# first words of the first paragraph, last words of the last paragraph). Matching ignores case and
# runs of whitespace; Gutenberg _italic_ underscores count as text.
WORKS = {
 'orthodoxy': dict(edition='pg-16769', kind='ch', noun='Chapter', nouns='Chapters',
  # Research mapped these boundaries on Gutenberg #130; they are remapped here onto the hosted #16769
  # (John Lane 1934 reprint of the 1908 text, which has no Preface). Opening and closing words are
  # Research's, checked against #16769 by the builder.
  start_after='_ORTHODOXY_',
  edition_line='Transcribed from a John Lane, The Bodley Head reprint: first published 1908, this printing 1934 (title page). It has no Preface.',
  parts=[
   ('01-introduction-in-defence-of-everything-else','I','Introduction in Defence of Everything Else','CHAPTER I.--_Introduction in Defence of Everything Else_','The only possible excuse for this book is that it is an answer','I will write him another book.'),
   ('02-the-maniac','II','The Maniac','CHAPTER II.--_The Maniac_','Thoroughly worldly people never understand even the world;','has given to them all her name.'),
   ('03-the-suicide-of-thought','III','The Suicide of Thought','CHAPTER III.--_The Suicide of Thought_','The phrases of the street are not only forcible but subtle:','throughout.'),
   ('04-the-ethics-of-elfland','IV','The Ethics of Elfland','CHAPTER IV--_The Ethics of Elfland_','When the business man rebukes the idealism of his office-boy, it','of Christian theology.'),
   ('05-the-flag-of-the-world','V','The Flag of the World','CHAPTER V.--_The Flag of the World_','When I was a boy there were two curious men running about','at home.'),
   ('06-the-paradoxes-of-christianity','VI','The Paradoxes of Christianity','CHAPTER VI.--_The Paradoxes of Christianity_','The real trouble with this world of ours is not that it is an','the wild truth reeling but erect.'),
   ('07-the-eternal-revolution','VII','The Eternal Revolution','CHAPTER VII.--_The Eternal Revolution_','The following propositions have been urged: First, that some','the steepest adventure is to get there."'),
   ('08-the-romance-of-orthodoxy','VIII','The Romance of Orthodoxy','CHAPTER VIII.--_The Romance of Orthodoxy_','It is customary to complain of the bustle and strenuousness','but they laid waste the world.'),
   ('09-authority-and-the-adventurer','IX','Authority and the Adventurer','CHAPTER IX.--_Authority and the Adventurer_','The last chapter has been concerned with the contention that','His mirth.'),
  ]),
}
