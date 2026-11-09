"""Build the browser catalog from versioned metadata; no network or credentials."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate(catalog):
    assert catalog['schemaVersion'] == 1
    archive = catalog.get('textArchive')
    if archive:
        assert archive['baseUrl'] == 'https://texts.bibliothecacatholica.com/texts/'
        assert isinstance(archive['enabled'], bool)
    ids, editions = set(), set()
    by_id = {work['id']: work for work in catalog['works']}
    authors = {a['id'] for a in json.loads((ROOT / 'data/catholic-hub.json').read_text())['authors']}
    for work in catalog['works']:
        assert work['id'] not in ids, f"Duplicate work: {work['id']}"
        ids.add(work['id'])
        assert work['title'] and work['author'] and work['category'] and work['tradition']
        assert not work.get('authorId') or work['authorId'] in authors
        assert work['description'].strip(), f"Missing description: {work['id']}"
        if all(e['access']=='reference' for e in work['editions']):
            assert work.get('readingLinks'), f"Reference-only work needs a reading sample: {work['id']}"
        for item in work.get('readingLinks', []):
            assert item['kind'] in ['excerpt', 'preview'], work['id']
            assert item['url'].startswith('https://')
            assert item['label'] and item['note'] and item['checked']
        assert work['editions'], work['id']
        for edition in work['editions']:
            assert edition['id'] not in editions, edition['id']
            editions.add(edition['id'])
            assert edition['source'].startswith('https://')
            assert edition['rights'] and edition['checked'] and edition['access'] in ['full-text', 'reference']
            for contributor in edition.get('contributors', []):
                assert contributor['role'] and contributor['name']
            if edition.get('text'):
                path = (ROOT / edition['text']).resolve()
                assert path.is_relative_to(ROOT / 'data/texts')
                raw = path.read_bytes()
                assert hashlib.sha256(raw).hexdigest() == edition['sha256'], edition['id']
                source = json.loads((ROOT / ('data/sources/' + edition['id'] + '.json')).read_text())
                if source.get('kind') == 'ocr-transcription':
                    # Supplement to the Summa (2026-11-09): our transcription of Internet Archive scans of printings
                    # before 1931; the source record names every scan, its imprint year, and its OCR file's SHA-256
                    assert edition['source'].startswith('https://archive.org/details/'), edition['id']
                    assert b'*** END OF THE TRANSCRIPTION ***' in raw and source['sha256'] == edition['sha256'], edition['id']
                    assert source['title'] == edition['sourceTitle'] and edition['rights'].startswith('Public domain in the USA.')
                    scans = source['volumes'] + [source['substitutePages']]
                    assert edition['source'] in [v['url'] for v in scans], edition['id']
                    for v in scans:
                        assert v['url'] == 'https://archive.org/details/' + v['identifier'] and v['year'] < 1931, v['identifier']
                        assert re.fullmatch(r'[0-9a-f]{64}', v['ocrSha256']), v['identifier']
                    continue
                assert b'END OF THE PROJECT GUTENBERG' in raw.upper()
                assert source['metadata']['Copyright'] == ['Public domain in the USA.']
                assert source['metadata']['Title'][0] == edition['sourceTitle']
    # Deep-link gaps (2026-11-09): a series lists its books in order; a book from 1931 or later is never a work here
    for series in catalog.get('series', []):
        assert series['id'] and series['title'] and series['items'], series
        years = [item['year'] for item in series['items']]
        assert years == sorted(years), series['id']
        for item in series['items']:
            assert item['title'] and isinstance(item['year'], int)
            if item['workId']:
                assert item['workId'] in ids, item
                assert item['year'] < 1931, item
            else:
                assert item.get('note'), item
    # Deep-link gaps (2026-11-09): author pages for writers outside the Catholic communion whose books are in the
    # reading room (Research: deep-link-gaps-2026-11-09.json). They are not hub authors and never Catholic Authors.
    seen = set()
    for author in catalog.get('relatedAuthors', []):
        assert re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', author['id']) and author['id'] not in authors and author['id'] not in seen, author['id']
        seen.add(author['id'])
        assert author['name'] and isinstance(author['born'], int) and isinstance(author['died'], int)
        assert author['badge'] == 'Non-Catholic Christian' and author['tradition'] and author['evidence'] and author['bio'] and 120 <= len(author['desc']) <= 160
        assert author['workIds'] and all(w in ids for w in author['workIds']), author['id']
        surname = author['name'].split()[-1]
        assert all(surname in by_id[w]['author'] and not by_id[w].get('authorId') for w in author['workIds']), author['id']
        assert set(author.get('noteWorks', [])) <= set(author['workIds']) and (not author.get('noteWorks') or author.get('note'))
        assert all(w in ids for w in author.get('readAlso', [])), author['id']
        assert all(x['url'].startswith('https://') for x in author.get('otherWorks', []) + author['sources'])
        assert '\u2014' not in json.dumps(author, ensure_ascii=False), author['id']  # no em-dashes in site text
    return catalog

def main():
    data = validate(json.loads((ROOT / 'data/library.json').read_text()))
    (ROOT / 'data/library.js').write_text('window.LIBRARY_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f"Validated and built {len(data['works'])} works.")

if __name__ == '__main__':
    main()
