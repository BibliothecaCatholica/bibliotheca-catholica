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

# Notices for other hosted sources (November 21, 2026). Only the Project Gutenberg
# 1.E.1 sentence is used for gutenberg.org. Every other host gets its own wording,
# so a Douay-Rheims chapter from eBible.org is never labelled a Standard Ebooks edition.
# gutenberg.net.au is checked before gutenberg.org so the Australia site is not mistaken
# for Project Gutenberg.
EBIBLE_NOTICE=('This text comes from eBible.org. It is in the public domain in the United States. '
  'eBible.org notices are retained. It is not a Project Gutenberg eBook.')
PEO_NOTICE=('This text comes from Papal Encyclicals Online. It is in the public domain in the United States. '
  'Papal Encyclicals Online notices are retained. It is not a Project Gutenberg eBook.')
PGA_NOTICE=('This text comes from Project Gutenberg Australia, not from Project Gutenberg at gutenberg.org. '
  'It is in the public domain in the United States. Project Gutenberg Australia notices are retained.')
IA_NOTICE=('This text is Bibliotheca Catholica’s transcription of public-domain scans at the Internet Archive, not a Project Gutenberg eBook.')
CCEL_NOTICE=('This text is the public-domain Shaw translation from the Nicene and Post-Nicene Fathers (Series I, Volume II), taken from the CCEL Public Domain plain-text edition, not a Project Gutenberg eBook.')
GENERIC_NOTICE=('This text is taken from the linked source. See the edition rights for what may be done with it. '
  'It is not a Project Gutenberg eBook and not a Standard Ebooks edition.')
RECORD_LABEL = {
    'pg': 'Project Gutenberg record',
    'pga': 'Project Gutenberg Australia record',
    'se': 'Standard Ebooks record',
    'ebible': 'eBible.org record',
    'peo': 'Papal Encyclicals Online record',
    'ia': 'Internet Archive record',
    'ccel': 'CCEL record',
    'other': 'Source record',
}

def source_kind(source):
    """Classify a hosted edition by the host of its source URL."""
    s = source or ''
    if 'gutenberg.net.au' in s:
        return 'pga'
    if 'gutenberg.org' in s:
        return 'pg'
    if 'standardebooks.org' in s:
        return 'se'
    if 'ebible.org' in s:
        return 'ebible'
    if 'papalencyclicals.net' in s:
        return 'peo'
    if 'archive.org' in s:
        return 'ia'
    if 'ccel.org' in s:
        return 'ccel'
    return 'other'

def notice_for(source):
    """The licence or source notice shown on a hosted part page (plain HTML, no wrapping <p>)."""
    k = source_kind(source)
    return {
        'pg': PG_LINE,
        'se': SE_NOTICE,
        'ebible': EBIBLE_NOTICE,
        'peo': PEO_NOTICE,
        'pga': PGA_NOTICE,
        'ia': IA_NOTICE,
        'ccel': CCEL_NOTICE,
        'other': GENERIC_NOTICE,
    }[k]

def record_label(source):
    return RECORD_LABEL[source_kind(source)]
