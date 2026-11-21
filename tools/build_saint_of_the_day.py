"""Build static saint-of-the-day JSON from the existing saints calendar data.

Reads data/saints-days.json (does not edit it) and data/lectionary-references-2026.json,
and writes data/saint-of-the-day.json, keyed by MM-DD.

Mass readings are scripture citations only, never lectionary text. The 2026 citations come
from the USCCB Liturgical Calendar for the Dioceses of the United States of America (2026),
https://www.usccb.org/resources/2026cal.pdf, checked 21 November 2026. Weekday readings
follow that year; solemnities and feasts with proper readings are the usual fixed citations.
"""
from __future__ import annotations
import json, re, calendar
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAINTS = ROOT / 'data' / 'saints-days.json'
REFS = ROOT / 'data' / 'lectionary-references-2026.json'
OUT = ROOT / 'data' / 'saint-of-the-day.json'

SOURCE = {
    'name': 'Liturgical Calendar for the Dioceses of the United States of America (2026)',
    'publisher': 'United States Conference of Catholic Bishops',
    'url': 'https://www.usccb.org/resources/2026cal.pdf',
    'checked': '2026-11-21',
    'note': 'Scripture citations only (book, chapter, and verse). No lectionary or biblical text is reproduced. Weekday readings follow the 2026 weekday cycle in that calendar. A current year may differ. Official daily pages: https://bible.usccb.org/daily-bible-reading',
}
USCCB_DAILY = 'https://bible.usccb.org/daily-bible-reading'

# The current General Roman Calendar principal observance, used only when the
# saints-days data still carries an older title (we do not edit that file).
PRINCIPAL_OVERRIDE = {
    '01-01': {
        'name': 'Solemnity of Mary, the Holy Mother of God',
        'rank': 'solemnity',
        'note': 'The current General Roman Calendar keeps 1 January as this solemnity, the Octave Day of Christmas. The saints calendar data on this date still lists the older Feast of the Circumcision and does not yet name Mary, Mother of God. That data file was left unchanged in this build.',
    },
}

COLORS = re.compile(
    r'\s+(?:white|green|red|violet|black|rose)'
    r'(?:(?:\s+or\s+|\s*/\s*)(?:white|green|red|violet|black|rose))*\s*$',
    re.I,
)
LECTIONARY = re.compile(r'\((\d{1,4}[A-Z]?(?:\s*,\s*see[^)]+)?)\)')
PSS = re.compile(r'\s*Pss\s+\S+\s*$')
WEEK_PAREN = re.compile(
    r'\s+\((?:[^)]*\b(?:Week|Time|Sunday of)\b[^)]*)\)\s*$',
    re.I,
)
PRIVILEGED = re.compile(
    r'\b(Sunday|Solemnity|Ash Wednesday|Holy Thursday|Good Friday|Holy Saturday|'
    r'Easter|Pentecost|Octave|Nativity of the Lord|Immaculate Conception|'
    r'Assumption|All Saints|All Souls|Epiphany|Ascension|Corpus Christi|'
    r'Christ the King|Holy Family|Holy Mother of God|Our Lady of Guadalupe|'
    r'Chair of Saint Peter|Conversion of Saint Paul)\b',
    re.I,
)


def all_days():
    days = []
    for month in range(1, 13):
        for day in range(1, calendar.monthrange(2024, month)[1] + 1):  # 2024: include 29 February
            days.append(f'{month:02d}-{day:02d}')
    return days


def clean_title(s):
    s = re.sub(r'\s+', ' ', (s or '').strip())
    s = COLORS.sub('', s).strip()
    s = re.sub(r'^USA:\s*', '', s)
    s = WEEK_PAREN.sub('', s)
    s = re.sub(r'(?<=[A-Za-z)])\d{1,2}$', '', s)  # footnote markers such as Holy Saturday9
    s = s.strip(' .')
    core = re.sub(r'\([^)]*\)', '', s).strip()
    if core and core.upper() == core:
        def _tc(chunk):
            chunk = chunk.title()
            chunk = re.sub(r'\b(Of|The|And|For|Or|In|On|To)\b', lambda m: m.group().lower(), chunk)
            return (chunk[0].upper() + chunk[1:]) if chunk else chunk
        s = re.sub(r'[^()]+', lambda m: _tc(m.group(0)) if m.group(0).strip() and m.group(0).upper() == m.group(0) else m.group(0), s)
    return s


def normalize_cites(cites):
    out = []
    lectionary = []
    buf = []
    for raw in cites:
        s = raw.replace('\u2014', '-').replace('\u2013', '-').replace('—', '-').replace('–', '-')
        s = PSS.sub('', s).strip()
        for n in LECTIONARY.findall(s):
            if not n.lower().startswith('see'):
                lectionary.append(re.sub(r'\s*,\s*see.*$', '', n).strip())
        s = LECTIONARY.sub('', s)
        s = re.sub(r'\(\s*see[^)]*\)', '', s, flags=re.I)
        s = re.sub(r'\s+', ' ', s).strip(' ')
        if not s:
            continue
        if buf and buf[-1].endswith('/'):
            buf[-1] = buf[-1] + s
        else:
            buf.append(s)
    for s in buf:
        s = s.strip(' /')
        if s:
            out.append(s)
    return out, lectionary


def observances(entries):
    rows = []
    for e in entries or []:
        row = {'name': e.get('n'), 'type': e.get('t')}
        if e.get('g'):
            row['guide'] = e['g']
        rows.append(row)
    return rows


def liturgical_from_ref(ref):
    if not ref or not ref.get('title'):
        return None
    parts = [clean_title(ref['title'])]
    note_bits = []
    for extra in ref.get('extra') or []:
        e = extra.strip()
        if not e:
            continue
        if e.startswith('(') and e.endswith(')'):
            note_bits.append(e.strip('()'))
        else:
            parts.append(clean_title(e))
    title = ' '.join(p for p in parts if p)
    rank = ref.get('rank')
    low = (title + ' ' + ' '.join(ref.get('extra') or [])).lower()
    if not rank:
        if 'solemnity' in low or title.startswith('Solemnity'):
            rank = 'solemnity'
        elif re.search(r'\bfeast\b', low) or title in ('The Nativity of the Lord (Christmas)', 'The Nativity of the Lord', 'The Holy Innocents, Martyrs', 'The Holy Innocents'):
            rank = 'feast'
        elif re.search(r'\bmemorial\b', low):
            rank = 'memorial'
    row = {'name': title, 'rank': rank}
    if note_bits:
        row['calendarNote'] = '; '.join(note_bits)
    return row


def is_weekdayish(name, rank):
    if rank in ('solemnity', 'feast', 'memorial'):
        return False
    if name and PRIVILEGED.search(name):
        return False
    if not name:
        return True
    return bool(re.search(r'Weekday|Ordinary Time|^Monday |^Tuesday |^Wednesday |^Thursday |^Friday |^Saturday ', name, re.I))


def pick_principal(md, entries, ref):
    if md in PRINCIPAL_OVERRIDE:
        return dict(PRINCIPAL_OVERRIDE[md])
    lit = liturgical_from_ref(ref)
    optional = [clean_title(x) for x in (ref or {}).get('optional') or [] if clean_title(x)]
    if lit and is_weekdayish(lit.get('name'), lit.get('rank')) and optional:
        return {
            'name': optional[0],
            'rank': 'optional-memorial',
            'liturgical': lit['name'],
        }
    if lit:
        return lit
    for typ in ('solemnity', 'feast', 'marian-title'):
        for e in entries or []:
            if e.get('t') == typ:
                return {'name': e.get('n'), 'rank': typ if typ in ('feast', 'solemnity') else None}
    if entries:
        return {'name': entries[0].get('n'), 'rank': None}
    return None


def usccb_url(md):
    month, day = md.split('-')
    return f'https://bible.usccb.org/bible/readings/{month}{day}26.cfm'


def build():
    saints = json.loads(SAINTS.read_text(encoding='utf-8'))
    raw = json.loads(REFS.read_text(encoding='utf-8')) if REFS.exists() else {}
    refs = raw.get('days', raw)
    calendar_days = saints.get('days') or {}
    out = {
        'note': 'Saint of the day, generated at build time from data/saints-days.json. Mass readings are scripture citations only.',
        'readingsSource': SOURCE,
        'usccbDaily': USCCB_DAILY,
        'days': {},
    }
    for md in all_days():
        entries = calendar_days.get(md) or []
        ref = refs.get(md)
        principal = pick_principal(md, entries, ref)
        day = {
            'date': md,
            'principal': principal,
            'observances': observances(entries),
        }
        optional = [clean_title(x) for x in (ref or {}).get('optional') or [] if clean_title(x)]
        if optional:
            day['optionalMemorials'] = optional
        if ref:
            cites, lect = normalize_cites(ref.get('cites') or [])
            day['readings'] = {
                'year': 2026,
                'citations': cites,
                'lectionary': lect,
                'weekday': ref.get('weekday'),
                'usccb': usccb_url(md),
            }
        else:
            day['readings'] = {
                'year': None,
                'citations': [],
                'lectionary': [],
                'note': 'No 2026 civil-year assignment (29 February is not in 2026). See the USCCB daily readings in a leap year.',
            }
        out['days'][md] = day
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out


if __name__ == '__main__':
    data = build()
    print('saint-of-the-day: %d days, readings for %d' % (
        len(data['days']),
        sum(1 for v in data['days'].values() if v['readings'].get('citations'))))
