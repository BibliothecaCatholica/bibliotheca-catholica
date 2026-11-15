"""Source notices shared by the static pages and the EPUB builder.

PG_LINE is the Project Gutenberg License's own sentence (clause 1.E.1), verbatim and never paraphrased
(docs/PROJECT-RULES.md rule 2), with "Project Gutenberg™ License" linked to the full licence.
It appears once per page, at the end of the text, in small type. scripts/library.js PG_LINE has the same words, and
tests/test_text_pages.py checks both against the licence text in data/texts/pg-130.txt.
"""
PG_LINE=('This eBook is for the use of anyone anywhere in the United States and most other parts of the world at no cost and with almost no restrictions whatsoever. You may copy it, give it away or re-use it under the terms of the <a href="https://www.gutenberg.org/policy/license.html" target="_blank" rel="noopener">Project Gutenberg™ License</a> included with this eBook or online at www.gutenberg.org. If you are not located in the United States, you will have to check the laws of the country where you are located before using this eBook.')
# The Standard Ebooks notice (The Incredulity of Father Brown); same words as SE_NOTICE in scripts/library.js.
SE_NOTICE=('This text comes from the Standard Ebooks edition, which its producers dedicate to the public domain (CC0 1.0); it is not a Project Gutenberg eBook. '
  'Bibliotheca Catholica corrected it to the wording of the first printings where they differ; each correction is listed in the edition’s provenance record.')
