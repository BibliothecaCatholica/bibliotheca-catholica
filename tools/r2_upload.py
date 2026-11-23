"""Upload one approved batch of `data/r2-manifest.json` to the R2 bucket `bibliotheca-files`. Dry run by default.

    python3 tools/r2_upload.py --batch batch-1             # dry run: what would be uploaded, and the projected size
    python3 tools/r2_upload.py --batch batch-1 --apply     # upload, verify each object's SHA-256, record it
    python3 tools/r2_upload.py --delete pdf/ia-x.pdf --apply   # roll back one object and clear its record
    python3 tools/r2_upload.py --usage                     # the bucket's current size and object count

Round 8, Job B2 (November 23, 2026). Steps for one file:
  1. read it from `localPath` (files we hold), or download `sourceUrl` into `.r2-cache/` and check the source's SHA-1;
  2. PUT it to `pdf/<slug>.pdf`, `epub/<slug>.epub`, or `scans/<slug>/...` with its Content-Type and
     `Cache-Control: public, max-age=31536000, immutable` (keys never change content: a correction is a new edition);
  3. GET it back and compare SHA-256, Content-Type, and Cache-Control;
  4. write `upload` (date, batch, bytes, sha256, verified) and `sha256` into the manifest.
An object already recorded with the same SHA-256 is skipped. Items under `ownerReview` are never in a batch.

Auth: the Cloudflare API at api.cloudflare.com with an API token that has R2 Storage Edit. Set CLOUDFLARE_API_TOKEN
(in the cloud environment the network proxy injects the real token, so any placeholder value works there) and
CLOUDFLARE_ACCOUNT_ID, or rely on the manifest's `accountId`. The token is never printed. Docs: docs/R2-RUNBOOK.md.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/r2-manifest.json'
CACHE = ROOT / '.r2-cache'
API = 'https://api.cloudflare.com/client/v4'
KEY_PREFIXES = ('pdf/', 'epub/', 'scans/')


class Failed(Exception):
    pass


def check_key(key):
    """Keys follow the scheme in the manifest; nothing outside pdf/, epub/, and scans/ is ever written."""
    if not key.startswith(KEY_PREFIXES) or '..' in key or key.startswith('/') or '//' in key:
        raise Failed(f'key outside the scheme: {key}')
    if key.startswith('pdf/') and not key.endswith('.pdf') or key.startswith('epub/') and not key.endswith('.epub'):
        raise Failed(f'key extension does not match its folder: {key}')
    return key


class Client:
    """The few R2 calls this tool makes, through the Cloudflare API (urllib only; tests replace this class)."""

    def __init__(self, account, bucket, token):
        self.base = f'{API}/accounts/{account}/r2/buckets/{bucket}'
        self.token = token

    def _req(self, method, path, data=None, headers=None):
        h = {'Authorization': 'Bearer ' + self.token, **(headers or {})}
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=h)
        try:
            return urllib.request.urlopen(req, timeout=600)
        except urllib.error.HTTPError as e:  # never echo request headers (the token)
            raise Failed(f'{method} {path}: HTTP {e.code} {e.read()[:300].decode("utf-8", "replace")}') from None

    def put(self, key, body, content_type, cache_control):
        with self._req('PUT', '/objects/' + urllib.parse.quote(key), body,
                       {'Content-Type': content_type, 'Cache-Control': cache_control}) as r:
            return json.load(r)

    def get(self, key):
        """(sha256 of the body, bytes, Content-Type, Cache-Control) of the stored object."""
        with self._req('GET', '/objects/' + urllib.parse.quote(key)) as r:
            h, n = hashlib.sha256(), 0
            for chunk in iter(lambda: r.read(1 << 20), b''):
                h.update(chunk)
                n += len(chunk)
            return h.hexdigest(), n, r.headers.get('Content-Type'), r.headers.get('Cache-Control')

    def delete(self, key):
        with self._req('DELETE', '/objects/' + urllib.parse.quote(key)) as r:
            return json.load(r)

    def usage(self):
        with self._req('GET', '/usage') as r:
            return json.load(r)['result']


def fetch(f, download=None):
    """The file's bytes: from `localPath`, or from `sourceUrl` via the cache, checked against `sourceSha1`."""
    if f.get('localPath'):
        return (ROOT / f['localPath']).read_bytes()
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f['key'].replace('/', '__')
    if not path.exists():
        (download or _download)(f['sourceUrl'], path)
    body = path.read_bytes()
    if f.get('sourceSha1') and hashlib.sha1(body).hexdigest() != f['sourceSha1']:
        path.unlink()
        raise Failed(f'{f["key"]}: the download does not match the source SHA-1; nothing uploaded')
    if f.get('bytes') and len(body) != f['bytes']:
        path.unlink()
        raise Failed(f'{f["key"]}: the download is {len(body)} bytes, the manifest says {f["bytes"]}; nothing uploaded')
    return body


def _download(url, path):
    tmp = path.with_suffix('.part')
    with urllib.request.urlopen(url, timeout=600) as r, open(tmp, 'wb') as out:
        for chunk in iter(lambda: r.read(1 << 20), b''):
            out.write(chunk)
    tmp.rename(path)


def batch_files(manifest, batch):
    if batch not in manifest.get('batches', {}):
        raise Failed(f'no batch named {batch!r} in the manifest (batches: {", ".join(manifest.get("batches", {})) or "none"})')
    slugs = set(manifest['batches'][batch]['items'])
    items = [it for it in manifest['items'] if it['slug'] in slugs]
    for it in items:
        if it.get('ownerReview'):
            raise Failed(f'{it["slug"]} is waiting on the owner\'s review and cannot be uploaded')
    return [(it, f) for it in items for f in it['files']]


def plan(manifest, batch):
    """[(item, file, action)] where action is 'upload' or 'skip' (already recorded)."""
    out = []
    for it, f in batch_files(manifest, batch):
        check_key(f['key'])
        done = f.get('upload') and f['upload'].get('verified') and (not f.get('sha256') or f['upload']['sha256'] == f['sha256'])
        out.append((it, f, 'skip' if done else 'upload'))
    return out


def apply(manifest, batch, client, download=None, today=None, log=print):
    uploaded = 0
    for it, f, action in plan(manifest, batch):
        if action == 'skip':
            log(f'skip    {f["key"]} (recorded {f["upload"]["at"]})')
            continue
        body = fetch(f, download)
        digest = hashlib.sha256(body).hexdigest()
        if f.get('sha256') and f['sha256'] != digest:
            raise Failed(f'{f["key"]}: the file\'s SHA-256 differs from the manifest; nothing uploaded')
        client.put(f['key'], body, f['contentType'], f['cacheControl'])
        got, n, ctype, cache = client.get(f['key'])
        if (got, n) != (digest, len(body)) or (ctype or '').split(';')[0] != f['contentType'] or cache != f['cacheControl']:
            raise Failed(f'{f["key"]}: verification failed after upload (sha256 {got[:12]} vs {digest[:12]}, {n} vs {len(body)} bytes, '
                         f'{ctype!r}, {cache!r}); roll back with --delete {f["key"]} --apply')
        f['sha256'] = digest
        f['upload'] = {'at': (today or datetime.date.today()).isoformat(), 'batch': batch, 'bytes': len(body), 'sha256': digest, 'verified': True}
        write(manifest)  # record each object as soon as it is verified, so a later failure leaves an accurate manifest
        uploaded += len(body)
        log(f'upload  {f["key"]} {len(body):,} bytes, sha256 {digest[:12]}, verified')
    return uploaded


def delete(manifest, key, client):
    check_key(key)
    client.delete(key)
    for it in manifest['items']:
        for f in it['files']:
            if f['key'] == key:
                f['upload'] = None
    write(manifest)


def write(manifest):
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n')


def client_from_env(manifest):
    token = os.environ.get('CLOUDFLARE_API_TOKEN')
    if not token:
        raise Failed('set CLOUDFLARE_API_TOKEN (any placeholder where the network proxy injects the token)')
    account = os.environ.get('CLOUDFLARE_ACCOUNT_ID') or manifest.get('accountId')
    return Client(account, manifest['bucket'], token)


def main(argv=None, client=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--batch', help='the manifest batch to upload (required for an upload)')
    ap.add_argument('--apply', action='store_true', help='really upload (or delete); without it, a dry run')
    ap.add_argument('--delete', metavar='KEY', help='delete one object (roll back) and clear its upload record')
    ap.add_argument('--usage', action='store_true', help='print the bucket size and object count (read only)')
    a = ap.parse_args(argv)
    manifest = json.loads(MANIFEST.read_text())
    try:
        if a.usage:
            u = (client or client_from_env(manifest)).usage()
            size = int(u.get('payloadSize', 0)) + int(u.get('metadataSize', 0))
            print(f"{manifest['bucket']}: {int(u.get('objectCount', 0))} objects, {size / 1e9:.2f} GB of the {manifest['freeTierBytes'] / 1e9:.0f} GB free tier")
            return 0
        if a.delete:
            if not a.apply:
                print(f'dry run: would delete {check_key(a.delete)} and clear its upload record (add --apply)')
                return 0
            delete(manifest, a.delete, client or client_from_env(manifest))
            print(f'deleted {a.delete}; its upload record is cleared. Revert any site change that linked to it.')
            return 0
        if not a.batch:
            ap.error('--batch is required (an upload is always one named, owner-approved batch)')
        steps = plan(manifest, a.batch)
        todo = [(it, f) for it, f, act in steps if act == 'upload']
        stored = sum(f['upload']['bytes'] for it in manifest['items'] for f in it['files'] if f.get('upload'))
        add = sum(f['bytes'] or 0 for _, f in todo)
        if not a.apply:
            for it, f, act in steps:
                src = f['localPath'] or f['sourceUrl']
                print(f'{"would upload" if act == "upload" else "skip (recorded)":16} {f["key"]}  {(f["bytes"] or 0) / 1e6:.1f} MB  {f["contentType"]}  from {src}')
            print(f'dry run: {len(todo)} of {len(steps)} files, {add / 1e9:.2f} GB; recorded in R2 afterwards {(stored + add) / 1e9:.2f} GB '
                  f'of {manifest["freeTierBytes"] / 1e9:.0f} GB. Nothing was uploaded; add --apply once the owner approves {a.batch}.')
            return 0
        if stored + add > manifest['freeTierBytes']:
            raise Failed(f'{a.batch} would take R2 past the free tier ({(stored + add) / 1e9:.2f} GB); stop and ask the owner')
        n = apply(manifest, a.batch, client or client_from_env(manifest))
        print(f'{a.batch}: {n / 1e9:.2f} GB uploaded and verified; data/r2-manifest.json records each object. Commit it.')
        return 0
    except Failed as e:
        print('r2_upload: ' + str(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
