"""Fetch a Project Gutenberg edition for rights review before hosting it in the reading room.

Network: gutenberg.org (catalog page + plain-text file). Usage:
    python3 tools/fetch_gutenberg_edition.py 470 1717 ...
Writes data/sources/pg-<n>.json (catalog metadata snapshot, same shape as the existing records)
and data/texts/pg-<n>.txt (the original UTF-8 bytes, credits and full Gutenberg license kept),
then prints the SHA-256 and the first lines of front matter so a reviewer can confirm the
translation/edition publication date is before 1931. It never edits data/library.json: add the
work there by hand (with the year evidence in the edition note) and run `npm run build`.
"""
import hashlib, html, json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {'User-Agent': 'BibliothecaCatholica-catalog/1.0 (+https://bibliothecacatholica.com)'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def metadata(n):
    page = get(f'https://www.gutenberg.org/ebooks/{n}').decode('utf-8')
    table = page[page.find('<table class="bibrec"'):]
    table = table[:table.find('</table>')]
    meta = {}
    for m in re.finditer(r'<tr[^>]*>\s*<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>', table, re.S):
        key = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
        val = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2)))).strip()
        if key in ('Summary', 'EBook-No.'):
            continue  # do not import Gutenberg's generated summaries
        meta.setdefault(key, []).append(val)
    return meta


def main(ids):
    for n in ids:
        url = f'https://www.gutenberg.org/cache/epub/{n}/pg{n}.txt'
        try:
            meta = metadata(n)
            raw = get(url)
        except Exception as err:  # audio-only or HTML-only releases have no plain text
            print(f'pg-{n}: skipped ({err})')
            continue
        assert b'END OF THE PROJECT GUTENBERG' in raw.upper(), f'{n}: license/end marker missing'
        (ROOT / f'data/texts/pg-{n}.txt').write_bytes(raw)
        rec = {'id': int(n), 'metadata': meta, 'textUrl': url, 'checked': time.strftime('%Y-%m-%d')}
        (ROOT / f'data/sources/pg-{n}.json').write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
        print(f'pg-{n}', meta.get('Title'), meta.get('Copyright'), hashlib.sha256(raw).hexdigest(), len(raw))
        time.sleep(1)


if __name__ == '__main__':
    main(sys.argv[1:])
