#!/usr/bin/env python3
"""Check a deployed text archive against the maintained catalog's hashes."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def verify(base):
    catalog = json.loads((ROOT / 'data/library.json').read_text())
    editions = [e for w in catalog['works'] for e in w['editions'] if e.get('text')]
    def check(edition):
        url = base.rstrip('/') + '/texts/' + Path(edition['text']).name
        try:
            request = Request(url, headers={'Origin': 'https://bibliothecacatholica.com'})
            with urlopen(request, timeout=25) as response:
                raw = response.read()
                cors = response.headers.get('Access-Control-Allow-Origin')
                status = response.status
                final = response.url
            digest = hashlib.sha256(raw).hexdigest()
            return {'edition': edition['id'], 'url': final, 'status': status,
                    'bytes': len(raw), 'sha256': digest,
                    'matchesOriginal': digest == edition['sha256'],
                    'readerCors': cors in ('*', 'https://bibliothecacatholica.com')}
        except Exception as error:
            return {'edition': edition['id'], 'url': url, 'error': str(error),
                    'matchesOriginal': False, 'readerCors': False}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, editions))
    success = all(r['matchesOriginal'] and r['readerCors'] for r in results)
    print(json.dumps({'baseUrl': base, 'success': success, 'checked': len(results), 'results': results}, indent=2))
    return success


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='https://texts.bibliothecacatholica.com')
    raise SystemExit(0 if verify(parser.parse_args().base_url) else 1)
