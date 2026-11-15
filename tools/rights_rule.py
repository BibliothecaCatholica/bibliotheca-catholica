"""The hosting rule, stated once (owner rule change, November 15, 2026; docs/PROJECT-RULES.md rule 1).

There is no fixed publication-date cutoff. A full text is hosted only when that edition's basis for
hosting is recorded with evidence. Public domain in the United States by date is the usual basis:
a work first published in the year `pd_last_year()` or earlier is out of US copyright (95 years from
publication), and the line moves forward one year every January 1. A later edition needs one of the
other recorded bases. Unknown rights fail closed.

Import `pd_last_year`, `pd_by_date`, and `RULE_SENTENCE` instead of writing a year into copy, asserts,
or tests. Stable rights-code IDs that name 1931 (for example `U1a_1931_63_...`) are historical
classification labels and stay as they are.
"""
import datetime

TERM = 95  # 17 U.S.C. 304(b): 95 years from publication, running to the end of the calendar year

# The recorded bases a hosted edition may carry (provenance `rightsBasis`; README of bibliotheca-texts).
BASES = {
    'pd-date': 'Public domain in the United States by date of first publication',
    'pd-nonrenewal': 'Public domain in the United States: no renewal (US work, 1931 to 1963; renewal search and URAA check recorded)',
    'pd-defect': 'Public domain in the United States: published without notice or with a defective notice (evidence recorded)',
    'open-license': 'Open license (the license is named and its text retained)',
    'permission': 'Permission granted (the grant is quoted and dated)',
}


def pd_last_year(today=None):
    """The last first-publication year that is public domain in the US by date (1930 during 2026)."""
    return (today or datetime.date.today()).year - TERM - 1


def pd_by_date(year, today=None):
    return year is not None and int(year) <= pd_last_year(today)


def pd_enters(year):
    """January 1 on which a work first published in `year` enters the US public domain by date."""
    return datetime.date(int(year) + TERM + 1, 1, 1)


def rule_sentence(today=None):
    y = pd_last_year(today)
    return (f'We host a full text only when that edition’s basis is recorded with evidence. Public domain in the '
            f'United States by date is the usual basis: in {y + 1 + TERM}, that means first published in {y} or earlier, '
            f'and the line moves forward one year each January 1. A later edition is hosted only with written '
            f'evidence of another basis (no renewal, a defective notice, an open license, or the holder’s '
            f'permission). Unknown rights fail closed.')


RULE_SENTENCE = rule_sentence()
