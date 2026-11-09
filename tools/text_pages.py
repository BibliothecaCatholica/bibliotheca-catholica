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

Only hosted, rights-checked editions (Gutenberg, or a public-domain text with a provenance record) may appear here (content rules 1 and 2). Never add a
flagged title.
"""
# kind: 'ch' (chapters) or 'story' (stories). Each part: (slug, number label, title, heading block,
# first words of the first paragraph, last words of the last paragraph). Matching ignores case and
# runs of whitespace; Gutenberg _italic_ underscores count as text.
WORKS = {
 'orthodoxy': dict(edition='pg-130', kind='ch', noun='Chapter', nouns='Chapters',
  # Research mapped these boundaries on Gutenberg #130, the hosted edition since 2026-11-09 (the 1908 text as printed by
  # the John Lane Company, New York, with the Preface). Opening and closing words are Research's, checked by the builder.
  start_after='ORTHODOXY',
  edition_line='The 1908 first edition text (New York: John Lane Company; London: John Lane, The Bodley Head), with the Preface. Checked against the 1909 John Lane Company printing at the Internet Archive.',
  parts=[
   ('01-introduction-in-defence-of-everything-else','I','Introduction in Defence of Everything Else','I INTRODUCTION IN DEFENCE OF EVERYTHING ELSE','The only possible excuse for this book is that it is an answer','I will write him another book.'),
   ('02-the-maniac','II','The Maniac','II THE MANIAC','Thoroughly worldly people never understand even the world;','has given to them all her name.'),
   ('03-the-suicide-of-thought','III','The Suicide of Thought','III THE SUICIDE OF THOUGHT','The phrases of the street are not only forcible but subtle:','throughout.'),
   ('04-the-ethics-of-elfland','IV','The Ethics of Elfland','IV THE ETHICS OF ELFLAND','When the business man rebukes the idealism of his office-boy, it','of Christian theology.'),
   ('05-the-flag-of-the-world','V','The Flag of the World','V THE FLAG OF THE WORLD','When I was a boy there were two curious men running about','at home.'),
   ('06-the-paradoxes-of-christianity','VI','The Paradoxes of Christianity','VI THE PARADOXES OF CHRISTIANITY','The real trouble with this world of ours is not that it is an','the wild truth reeling but erect.'),
   ('07-the-eternal-revolution','VII','The Eternal Revolution','VII THE ETERNAL REVOLUTION','The following propositions have been urged: First, that some','the steepest adventure is to get there."'),
   ('08-the-romance-of-orthodoxy','VIII','The Romance of Orthodoxy','VIII THE ROMANCE OF ORTHODOXY','It is customary to complain of the bustle and strenuousness','but they laid waste the world.'),
   ('09-authority-and-the-adventurer','IX','Authority and the Adventurer','IX AUTHORITY AND THE ADVENTURER','The last chapter has been concerned with the contention that','His mirth.'),
  ]),
# Father Brown: the collections published before 1931 and hosted here (Research 2026-11-09; The Incredulity, 1926,
 # added 2026-11-09 from Standard Ebooks, corrected to the 1926 printings). The Scandal (1935) is after the cutoff: see
 # `series` in data/library.json.
 'innocence-father-brown': dict(edition='pg-204', kind='story', noun='Story', nouns='Stories',
  start_after='Contents',
  parts=[
   ('01-the-blue-cross', '1', 'The Blue Cross', 'The Blue Cross', 'Between the silver ribbon of morning and the green', 'priest blinked about for his umbrella.'),
   ('02-the-secret-garden', '2', 'The Secret Garden', 'The Secret Garden', 'Aristide Valentin, Chief of the Paris Police, was late', 'more than the pride of Cato.'),
   ('03-the-queer-feet', '3', 'The Queer Feet', 'The Queer Feet', 'If you meet a member of that select club,', 'in search of a penny omnibus.'),
   ('04-the-flying-stars', '4', 'The Flying Stars', 'The Flying Stars', '“The most beautiful crime I ever committed,” Flambeau would', 'cloistered and ignorant of this world.'),
   ('05-the-invisible-man', '5', 'The Invisible Man', 'The Invisible Man', 'In the cool blue twilight of two steep streets', 'each other will never be known.'),
   ('06-the-honour-of-israel-gow', '6', 'The Honour of Israel Gow', 'The Honour of Israel Gow', 'A stormy evening of olive and silver was closing', 'sober top hat on his head.'),
   ('07-the-wrong-shape', '7', 'The Wrong Shape', 'The Wrong Shape', 'Certain of the great roads going north out of', 'policemen gleamed in the road outside.'),
   ('08-the-sins-of-prince-saradine', '8', 'The Sins of Prince Saradine', 'The Sins of Prince Saradine', 'When Flambeau took his month’s holiday from his office', 'and the homes of harmless men.'),
   ('09-the-hammer-of-god', '9', 'The Hammer of God', 'The Hammer of God', 'The little village of Bohun Beacon was perched on', 'up; I have killed my brother.”'),
   ('10-the-eye-of-apollo', '10', 'The Eye of Apollo', 'The Eye of Apollo', 'That singular smoky sparkle, at once a confusion and', 'knew that he was expecting it.”'),
   ('11-the-sign-of-the-broken-sword', '11', 'The Sign of the Broken Sword', 'The Sign of the Broken Sword', 'The thousand arms of the forest were grey, and', '“Or brandy,” said Flambeau.'),
   ('12-the-three-tools-of-death', '12', 'The Three Tools of Death', 'The Three Tools of Death', 'Both by calling and conviction Father Brown knew better', 'I can’t stop for the inquiry.”'),
  ]),
 'wisdom-father-brown': dict(edition='pg-223', kind='story', noun='Story', nouns='Stories',
  start_after='CONTENTS',
  parts=[
   ('01-the-absence-of-mr-glass', '1', 'The Absence of Mr Glass', 'ONE -- The Absence of Mr Glass', 'THE consulting-rooms of Dr Orion Hood, the eminent criminologist', 'Monday next at eight o’clock precisely.'),
   ('02-the-paradise-of-thieves', '2', 'The Paradise of Thieves', 'TWO. -- The Paradise of Thieves', 'THE great Muscari, most original of the young Tuscan', '“to the real Paradise of Thieves.”'),
   ('03-the-duel-of-dr-hirsch', '3', 'The Duel of Dr Hirsch', 'THREE -- The Duel of Dr Hirsch', 'M. MAURICE BRUN and M. Armand Armagnac were crossing', 'once more appeared upon the balcony.'),
   ('04-the-man-in-the-passage', '4', 'The Man in the Passage', 'FOUR -- The Man in the Passage', 'TWO men appeared simultaneously at the two ends of', 'don’t look at it so often.”'),
   ('05-the-mistake-of-the-machine', '5', 'The Mistake of the Machine', 'FIVE -- The Mistake of the Machine', 'FLAMBEAU and his friend the priest were sitting in', 'eyes, but Father Brown was gone.'),
   ('06-the-head-of-caesar', '6', 'The Head of Caesar', 'SIX -- The Head of Caesar', 'THERE is somewhere in Brompton or Kensington an interminable', 'are probably getting on very well.”'),
   ('07-the-purple-wig', '7', 'The Purple Wig', 'SEVEN -- The Purple Wig', 'MR EDWARD NUTT, the industrious editor of the Daily', 'word “God” to the word “circumstances.”'),
   ('08-the-perishing-of-the-pendragons', '8', 'The Perishing of the Pendragons', 'EIGHT -- The Perishing of the Pendragons', 'FATHER BROWN was in no mood for adventures. He', 'no answer: Father Brown was asleep.'),
   ('09-the-god-of-the-gongs', '9', 'The God of the Gongs', 'NINE -- The God of the Gongs', 'IT was one of those chilly and empty afternoons', 'singing on the sands.'),
   ('10-the-salad-of-colonel-cray', '10', 'The Salad of Colonel Cray', 'TEN -- The Salad of Colonel Cray', 'FATHER BROWN was walking home from Mass on a', 'Major?” said the priest. “Well, good-bye.”'),
   ('11-the-strange-crime-of-john-boulnois', '11', 'The Strange Crime of John Boulnois', 'ELEVEN -- The Strange Crime of John Boulnois', 'MR CALHOUN KIDD was a very young gentleman with', '“Being hanged,” said Father Brown.'),
   ('12-the-fairy-tale-of-father-brown', '12', 'The Fairy Tale of Father Brown', 'TWELVE -- The Fairy Tale of Father Brown', 'THE picturesque city and state of Heiligwaldenstein was one', 'the black warning in his eyes.'),
  ]),
 'incredulity-father-brown': dict(edition='se-incredulity-father-brown', kind='story', noun='Story', nouns='Stories',
  start_after='*** START OF THE HOSTED TEXT: THE INCREDULITY OF FATHER BROWN ***',
  edition_line='First published 1926 (London: Cassell and Company; New York: Dodd, Mead and Company). Standard Ebooks text, corrected to the wording of the 1926 printings.',
  parts=[
   ('01-the-resurrection-of-father-brown', '1', 'The Resurrection of Father Brown', 'I. THE RESURRECTION OF FATHER BROWN', 'There was a brief period during which Father Brown', 'about a bottle of real wine?”'),
   ('02-the-arrow-of-heaven', '2', 'The Arrow of Heaven', 'II. THE ARROW OF HEAVEN', 'It is to be feared that about a hundred', 'into a blue abyss of sky.'),
   ('03-the-oracle-of-the-dog', '3', 'The Oracle of the Dog', 'III. THE ORACLE OF THE DOG', '“Yes,” said Father Brown, “I always like a dog,', 'the wolf looked at St. Francis.'),
   ('04-the-miracle-of-moon-crescent', '4', 'The Miracle of Moon Crescent', 'IV. THE MIRACLE OF MOON CRESCENT', 'Moon Crescent was meant in a sense to be', 'for a man like Warren Wynd.”'),
   ('05-the-curse-of-the-golden-cross', '5', 'The Curse of the Golden Cross', 'V. THE CURSE OF THE GOLDEN CROSS', 'Six people sat round a small table, seeming almost', 'only fishes who survive the Deluge.”'),
   ('06-the-dagger-with-wings', '6', 'The Dagger with Wings', 'VI. THE DAGGER WITH WINGS', 'Father Brown, at one period of his life, found', 'knows where to look for it.”'),
   ('07-the-doom-of-the-darnaways', '7', 'The Doom of the Darnaways', 'VII. THE DOOM OF THE DARNAWAYS', 'Two landscape-painters stood looking at one landscape, which was', 'deserve to be put in it.”'),
   ('08-the-ghost-of-gideon-wise', '8', 'The Ghost of Gideon Wise', 'VIII. THE GHOST OF GIDEON WISE', 'Father Brown always regarded the case as the queerest', 'history, he is also a poet.”'),
  ]),
 'secret-father-brown': dict(edition='pg-70175', kind='story', noun='Story', nouns='Stories',
  start_after='THE SECRET OF FLAMBEAU',
  parts=[
   ('00-the-secret-of-father-brown', 'Opening frame story', 'The Secret of Father Brown', 'THE\nSECRET OF FATHER BROWN', 'FLAMBEAU, once the most famous criminal in France and', 'lips, "I can remember pretty well----"'),
   ('01-the-mirror-of-the-magistrate', '1', 'The Mirror of the Magistrate', 'THE MIRROR OF THE MAGISTRATE', 'JAMES BAGSHAW and Wilfred Underhill were old friends, and', 'again, but not in a mirror."'),
   ('02-the-man-with-two-beards', '2', 'The Man with Two Beards', 'THE MAN WITH TWO BEARDS', 'THIS tale was told by Father Brown to Professor', 'alike in this world, doesn\'t it?"'),
   ('03-the-song-of-the-flying-fish', '3', 'The Song of the Flying Fish', 'THE SONG OF THE FLYING FISH', 'THE soul of Mr. Peregrine Smart hovered like a', 'that she will suddenly do it."'),
   ('04-the-actor-and-the-alibi', '4', 'The Actor and the Alibi', 'THE ACTOR AND THE ALIBI', 'MR. MUNDON MANDEVILLE, the theatrical manager, walked briskly through', 'and went out into the night.'),
   ('05-the-vanishing-of-vaudrey', '5', 'The Vanishing of Vaudrey', 'THE VANISHING OF VAUDREY', 'SIR ARTHUR VAUDREY, in his light-grey summer suit, and', 'me," said Father Brown. "How strange!"'),
   ('06-the-worst-crime-in-the-world', '6', 'The Worst Crime in the World', 'THE WORST CRIME IN THE WORLD', 'FATHER BROWN was wandering through a picture gallery with', 'in favour of a prudent marriage."'),
   ('07-the-red-moon-of-meru', '7', 'The Red Moon of Meru', 'THE RED MOON OF MERU', 'EVERYONE agreed that the bazaar at Mallowood Abbey (by', 'said, "and that was also stolen."'),
   ('08-the-chief-mourner-of-marne', '8', 'The Chief Mourner of Marne', 'THE CHIEF MOURNER OF MARNE', 'A BLAZE of lightning blanched the grey woods tracing', 'to the melancholy castle of Marne.'),
   ('09-the-secret-of-flambeau', 'Closing frame story', 'The Secret of Flambeau', 'THE SECRET OF FLAMBEAU', '"----the sort of murders in which I played the', '"I could try," said Father Brown.'),
  ]),
}
