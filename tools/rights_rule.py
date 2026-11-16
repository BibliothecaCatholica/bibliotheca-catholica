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
import re

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


# --- pd-nonrenewal (owner prompt, November 15, 2026; Part 1) -------------------------------------------------------
# A US work first published 1931 to 1963 whose copyright was never renewed. The structured evidence lives in the
# edition's source record (data/sources/<edition>.json) under `nonRenewal`; the edition keeps `rightsEvidence` as plain
# sentences. `nonrenewal_problems()` returns every way a record falls short; an empty list means it passes.
NONRENEWAL_YEARS = (1931, 1963)
NO_RENEWAL = 'no renewal found'
HATHI_CODES = {'pd', 'pdus', 'ic', 'icus', 'und', 'op', 'orph', 'nobody', 'pd-pvt', 'cc-zero', 'cc-by-4.0'}


def nonrenewal_problems(ev):
    """Problems with a `nonRenewal` evidence record (dict); [] when it passes."""
    if not isinstance(ev, dict) or not ev:
        return ['missing evidence']
    p = []
    year = ev.get('firstPublicationYear')
    if not isinstance(year, int) or not NONRENEWAL_YEARS[0] <= year <= NONRENEWAL_YEARS[1]:
        p.append('first publication year must be 1931 to 1963')
    if ev.get('firstPublicationCountry') != 'US':
        p.append('first publication must be in the United States (firstPublicationCountry "US")')
    for k in ('firstPublicationPlace', 'firstPublicationPublisher'):
        if not str(ev.get(k, '')).strip():
            p.append(f'{k} missing')
    searches = ['stanford', 'nypl'] + (['copyrightOffice'] if isinstance(year, int) and year >= 1950 else [])
    for k in searches:  # a renewal for a 1950 or later book fell due in 1978 or later: the Copyright Office's own records
        s = ev.get(k) or {}
        if s.get('result') != NO_RENEWAL or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(s.get('checked', ''))):
            p.append(f'{k} search missing, dated wrong, or not "{NO_RENEWAL}"')
    if ev.get('hathitrust') is not None and ev['hathitrust'] not in HATHI_CODES:
        p.append('hathitrust rights code not a HathiTrust code (quote it exactly, or leave it out)')
    if len(str(ev.get('uraa', '')).strip()) < 40:
        p.append('URAA line missing: say how first publication abroad was ruled out')
    if not str(ev.get('scan', '')).strip():
        p.append('scan missing: name the printing the hosted text follows')
    return p
