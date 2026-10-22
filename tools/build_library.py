"""Build the browser catalog from versioned metadata; no network or credentials."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate(catalog):
    assert catalog['schemaVersion'] == 1
    ids, editions = set(), set()
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
                assert b'END OF THE PROJECT GUTENBERG' in raw.upper()
                source = json.loads((ROOT / ('data/sources/' + edition['id'] + '.json')).read_text())
                assert source['metadata']['Copyright'] == ['Public domain in the USA.']
                assert source['metadata']['Title'][0] == edition['sourceTitle']
    return catalog

def main():
    data = validate(json.loads((ROOT / 'data/library.json').read_text()))
    (ROOT / 'data/library.js').write_text('window.LIBRARY_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f"Validated and built {len(data['works'])} works.")

if __name__ == '__main__':
    main()
