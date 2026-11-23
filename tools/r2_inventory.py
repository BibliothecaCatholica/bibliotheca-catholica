"""R2 inventory: every scan, PDF, and EPUB the library holds or can source, ranked for upload to R2.

Writes `data/r2-manifest.json` (the upload manifest that `tools/r2_upload.py` reads and writes back to) and
`docs/R2-INVENTORY.md` (the same inventory as a readable table). Round 8, Job B1 (November 23, 2026).

Inputs, all in this repository:
  * `data/library.json`: editions whose source is an Internet Archive scan (hosted transcriptions and link-only scans);
  * `data/sources/*.json`: `iaWitness` scans, the dated printings that hosted texts were checked against;
  * `data/epubs.json` and `downloads/epub/`: the EPUBs we build; `data/sources/pdf-prints/`: source PDFs we hold;
  * `data/r2-sources.json`: a snapshot of each scan's Internet Archive file list (PDF name, size, checksums, file
    server), plus the read-gate notes and research candidates below the catalogue. `--refresh` rebuilds the
    snapshot from archive.org/metadata (network); every other run is offline and deterministic.

Rules (docs/PROJECT-RULES.md rule 1, stated once in tools/rights_rule.py): an item is listed for upload only with a
clean, edition-specific basis: public domain in the US by date (`pd_by_date`), or a recorded non-renewal check.
Anything else is listed under `excluded` with the reason. Nothing here uploads; listing is not approval: every
batch goes to the owner before `r2_upload.py --apply`, and non-renewal scans not yet approved for hosting carry
`ownerReview`. Upload records already written into the manifest are kept on every rebuild.
"""
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from rights_rule import pd_by_date, pd_last_year  # noqa: E402

MANIFEST = ROOT / 'data/r2-manifest.json'
SOURCES = ROOT / 'data/r2-sources.json'
DOC = ROOT / 'docs/R2-INVENTORY.md'
BUCKET = 'bibliotheca-files'
ACCOUNT_ID = '0bb2840dc3b530bc23ed51b05170ade1'  # Cloudflare account that owns the bucket (an identifier, not a secret)
PUBLIC_BASE = 'https://files.bibliothecacatholica.com'
FREE_TIER_BYTES = 10 * 10**9  # R2 free tier: 10 GB-month of Standard storage
BATCH_TARGET = 3 * 10**9  # a few GB per batch
CONTENT_TYPES = {'pdf': 'application/pdf', 'epub': 'application/epub+zip', 'jpg': 'image/jpeg', 'webp': 'image/webp',
                 'png': 'image/png', 'json': 'application/json'}
IMMUTABLE = 'public, max-age=31536000, immutable'
LARGE = 100 * 10**6  # a single file over 100 MB waits for a later batch

# Ranking tiers, lowest first. Within a tier, smaller files first (more books per GB).
TIERS = {
    'pairs': (1, 'pairs with a hosted text: readers can check the transcription against the original scan'),
    'epub': (2, 'already built from a hosted text; moves the file out of git'),
    'source-pdf': (2, 'the source PDF a hosted text was imported from; kept in git as provenance, mirrored here'),
    'witness': (3, 'the dated printing a hosted text was checked against'),
    'near': (4, 'near the read gate: an original-scan page while the transcription is finished'),
    'series': (5, 'completes a series the library already lists'),
    'candidate': (6, 'a research candidate (HOLDS or a sourced list): original scan before any transcription'),
}


def slug_for(identifier):
    """The R2 slug of an Internet Archive scan: the catalogue's own edition-id form ('ia-' + identifier)."""
    return 'ia-' + re.sub(r'[^a-z0-9]+', '-', identifier.lower()).strip('-')


def year_of(*values):
    """The latest four-digit year in the values (a range such as '1904-05' counts as its last year), or None."""
    years = []
    for v in values:
        v = re.sub(r'\b(?:before|after|until|since) (?:January 1, )?\d{4}', '', str(v or ''))  # a cutoff, not a date
        for m in re.finditer(r'(1[5-9]\d\d|20\d\d)(?:-(\d\d))?', v):
            years.append(int(m.group(1)[:2] + m.group(2)) if m.group(2) else int(m.group(1)))
    return max(years) if years else None


def first_published(edition):
    """The first-publication year recorded for a catalogue edition: its source record's `firstPublished`, `year`, or
    `iaWitness.year`, else the year in its rights evidence ("First published ... 1944"), else None."""
    p = ROOT / 'data/sources' / (edition['id'] + '.json')
    rec = json.loads(p.read_text()) if p.exists() else {}
    rec = rec if isinstance(rec, dict) else {}
    for v in (rec.get('firstPublished'), rec.get('year'), (rec.get('iaWitness') or {}).get('year') if isinstance(rec.get('iaWitness'), dict) else None):
        if year_of(v):
            return year_of(v)
    m = re.search(r'First published[^.]*?\b(1[5-9]\d\d)\b', str(edition.get('rightsEvidence') or '') + ' ' + edition.get('note', ''))
    return int(m.group(1)) if m else None


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def refresh(identifiers):
    """Rebuild the archive.org file snapshot (network: archive.org only)."""
    snap = json.loads(SOURCES.read_text()) if SOURCES.exists() else {}
    ia = {}
    for ident in sorted(identifiers):
        with urllib.request.urlopen(f'https://archive.org/metadata/{ident}', timeout=60) as r:
            d = json.load(r)
        m, files = d.get('metadata', {}), d.get('files', [])
        public = [f for f in files if f.get('private') not in ('true', True)]
        pdfs = [f for f in public if f['name'].lower().endswith('.pdf')]
        pdf = max(pdfs, key=lambda f: int(f.get('size', 0))) if pdfs else None
        jp2 = [f for f in public if f['name'].endswith(('_jp2.zip', '_jp2.tar'))]
        ia[ident] = {
            'title': m.get('title') if isinstance(m.get('title'), str) else '; '.join(m.get('title') or []),
            'creator': m.get('creator') if isinstance(m.get('creator'), str) else '; '.join(m.get('creator') or []),
            'date': str(m.get('date') or ''), 'restricted': m.get('access-restricted-item') in ('true', True),
            'servers': sorted({d.get('d1'), d.get('d2')} - {None}),
            'pdf': {'name': pdf['name'], 'size': int(pdf['size']), 'md5': pdf.get('md5'), 'sha1': pdf.get('sha1')} if pdf else None,
            'pageImagesBytes': sum(int(f.get('size', 0)) for f in jp2),
        }
        time.sleep(0.5)  # polite to archive.org
    snap['archiveOrg'] = ia
    snap['refreshed'] = time.strftime('%Y-%m-%d')
    SOURCES.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + '\n')
    return snap


def catalogue_scans(library):
    """{identifier: [(work, edition)]} for every edition whose source is an Internet Archive scan."""
    out = {}
    for w in library['works']:
        for e in w['editions']:
            m = re.search(r'archive\.org/details/([^/?#\s]+)', e.get('source', ''))
            if m:
                out.setdefault(m.group(1), []).append((w, e))
    return out


def witness_scans(library):
    """{identifier: (work, edition)} for the dated scans that hosted texts were checked against (`iaWitness`)."""
    editions = {e['id']: (w, e) for w in library['works'] for e in w['editions']}
    out = {}
    for p in sorted((ROOT / 'data/sources').glob('*.json')):
        rec = json.loads(p.read_text())
        wit = rec.get('iaWitness') if isinstance(rec, dict) else None
        if isinstance(wit, dict) and wit.get('identifier') and p.stem in editions:
            out.setdefault(wit['identifier'], editions[p.stem])
    return out


def build(snap, library, old):
    ia = snap['archiveOrg']
    notes = snap.get('readGate', {})
    candidates = snap.get('candidates', {})
    cat, wit = catalogue_scans(library), witness_scans(library)
    uploads = {f['key']: f.get('upload') for it in old.get('items', []) for f in it.get('files', []) if f.get('upload')}
    items, excluded = [], []

    def add(item, kind_tier):
        tier, reason = TIERS[kind_tier]
        item['tier'], item['priorityReason'] = tier, reason
        for f in item['files']:
            f['contentType'] = CONTENT_TYPES[f['key'].rsplit('.', 1)[1]]
            f['cacheControl'] = IMMUTABLE
            f['url'] = PUBLIC_BASE + '/' + f['key']
            f['upload'] = uploads.get(f['key'])
        items.append(item)

    for ident, meta in sorted(ia.items()):
        base = {'source': {'kind': 'archive.org', 'id': ident, 'url': f'https://archive.org/details/{ident}'},
                'fringe': False}
        refs = cat.get(ident, [])
        current = [(w, e) for w, e in refs if not e.get('retired')]
        w, e = (current or refs or [(None, None)])[0]
        if ident in candidates and candidates[ident].get('exclude'):
            excluded.append({**base, 'title': meta['title'], 'author': meta['creator'], 'year': year_of(meta['date']),
                             'reason': candidates[ident]['exclude']})
            continue
        if not meta.get('pdf') or meta.get('restricted'):
            excluded.append({**base, 'title': meta['title'], 'author': meta['creator'], 'year': year_of(meta['date']),
                             'reason': 'no public PDF on the Internet Archive item' if not meta.get('pdf') else 'lending-restricted item'})
            continue
        hosted_by = None
        if e is not None:
            work, edition = w, e
            year = first_published(e) or year_of(meta['date'], e.get('rights'), e.get('label'))
            if any(ed.get('text') for _, ed in current):
                kind, gate = 'pairs', 'hosted'
            elif ident in notes:
                kind, gate = 'near', 'near gate' if notes[ident]['score'] >= 98.5 else 'below'
            elif len({ed['id'] for ed in work['editions']}) > 1 and all(not ed.get('text') for ed in work['editions']):
                kind, gate = 'series', 'below'
            else:
                kind, gate = 'series', 'below'
        elif ident in wit:
            work, edition = wit[ident]
            hosted_by = edition['id']
            year, kind, gate = year_of(meta['date']), 'witness', 'hosted'
        else:
            work = edition = None
            year = year_of(meta['date'])
            kind = 'near' if ident in notes else 'candidate'
            gate = ('near gate' if notes[ident]['score'] >= 98.5 else 'below') if ident in notes else 'below'
        basis, evidence, review = None, None, False
        rights_basis = (edition or {}).get('rightsBasis')
        evidence_note = (edition or {}).get('note', '') + ' ' + str((edition or {}).get('rightsEvidence') or '')
        cand = candidates.get(ident, {})
        if year is not None and pd_by_date(year) and rights_basis in (None, 'pd-date'):
            basis = 'pd-date'
            evidence = f'first published {year}, before {pd_last_year() + 1}'
        elif rights_basis == 'pd-nonrenewal' or 'renewal check found no renewal' in evidence_note or cand.get('nonrenewal'):
            basis = 'pd-nonrenewal'
            evidence = cand.get('nonrenewal') or ('data/library.json ' + edition['id'] + ' rightsEvidence' if rights_basis == 'pd-nonrenewal'
                                                  else 'docs/research/us-pd-renewal-checks-2026-11.csv (' + edition['id'] + ')')
            review = rights_basis != 'pd-nonrenewal' or not any(ed.get('text') for _, ed in current)
        if basis is None:
            excluded.append({**base, 'title': (work or {}).get('title') or meta['title'], 'author': (work or {}).get('author') or meta['creator'],
                             'year': year, 'reason': f'no recorded basis: first published {year}, after {pd_last_year()}, and no non-renewal check is recorded'})
            continue
        slug = slug_for(ident)
        item = {**base, 'slug': slug, 'title': (work or {}).get('title') or meta['title'], 'author': (work or {}).get('author') or meta['creator'],
                'year': year, 'rightsBasis': basis, 'rightsEvidence': evidence, 'readGate': gate,
                'workId': (work or {}).get('id'), 'editionId': (edition or {}).get('id') if kind != 'witness' else None,
                'hostedEditionId': hosted_by or ((edition or {}).get('id') if gate == 'hosted' else None),
                'files': [{'kind': 'pdf', 'key': f'pdf/{slug}.pdf', 'bytes': meta['pdf']['size'], 'sha256': None,
                           'sourceUrl': f"https://archive.org/download/{ident}/{urllib.request.quote(meta['pdf']['name'])}",
                           'sourceSha1': meta['pdf'].get('sha1'), 'localPath': None}],
                'pageImagesBytes': meta.get('pageImagesBytes', 0), 'servers': meta.get('servers', [])}
        if ident in notes:
            item['readGateScore'] = notes[ident]['score']
            item['readGateNote'] = notes[ident]['note']
        if review:
            item['ownerReview'] = 'pd-nonrenewal scan not yet approved for hosting; the owner reviews it before upload'
        if meta['pdf']['size'] > LARGE:
            kind = 'candidate' if kind in ('series', 'candidate', 'near') else kind
            item['large'] = True
        add(item, kind)

    # EPUBs we build (downloads/epub/) and source PDFs we hold (data/sources/pdf-prints/): sha256 computed here
    epubs = json.loads((ROOT / 'data/epubs.json').read_text())['epubs']
    works = {w['id']: w for w in library['works']}
    editions = {e['id']: e for w in library['works'] for e in w['editions']}
    for eid, rec in sorted(epubs.items()):
        path = ROOT / rec['path']
        if rec['work'] not in works or eid not in editions:
            continue  # an EPUB of an edition outside this catalogue (only in tests with a small catalogue)
        w = works[rec['work']]
        e = editions[eid]
        add({'source': {'kind': 'epub', 'id': eid, 'url': 'https://bibliothecacatholica.com/' + rec['path']}, 'fringe': False,
             'slug': path.stem, 'title': w['title'], 'author': w['author'], 'year': first_published(e),
             'rightsBasis': e.get('rightsBasis', 'pd-date'), 'rightsEvidence': 'the hosted edition ' + eid + ' (data/library.json)',
             'readGate': 'hosted', 'workId': w['id'], 'editionId': eid, 'hostedEditionId': eid,
             'files': [{'kind': 'epub', 'key': f'epub/{path.name}', 'bytes': path.stat().st_size, 'sha256': sha256(path),
                        'sourceUrl': None, 'localPath': rec['path']}]}, 'epub')
    for path in sorted((ROOT / 'data/sources/pdf-prints').glob('*.pdf')):
        eid = path.stem
        e = editions.get(eid)
        w = next((w for w in library['works'] for ed in w['editions'] if ed['id'] == eid), None)
        if not (e and w):
            continue
        add({'source': {'kind': 'pdf-print', 'id': eid, 'url': e.get('source')}, 'fringe': False, 'slug': eid,
             'title': w['title'], 'author': w['author'], 'year': first_published(e),
             'rightsBasis': e.get('rightsBasis', 'pd-date'), 'rightsEvidence': 'the hosted edition ' + eid + ' (data/library.json)',
             'readGate': 'hosted', 'workId': w['id'], 'editionId': eid, 'hostedEditionId': eid,
             'files': [{'kind': 'pdf', 'key': f'pdf/{eid}.pdf', 'bytes': path.stat().st_size, 'sha256': sha256(path),
                        'sourceUrl': None, 'localPath': str(path.relative_to(ROOT))}]}, 'source-pdf')

    items.sort(key=lambda it: (it['tier'], bool(it.get('ownerReview')), sum(f['bytes'] for f in it['files']), it['slug']))
    for n, it in enumerate(items, 1):
        it['priority'] = n
    sizes = {it['slug']: sum(f['bytes'] for f in it['files']) for it in items}
    # Batches follow the ranking: 1, what pairs with or was built from hosted texts (tiers 1 to 3); 2, near-gate books and
    # series completions (tiers 4 and 5); 3, research candidates (tier 6). A batch over BATCH_TARGET spills into the next.
    # Non-renewal scans not yet approved for hosting join no batch until the owner reviews them.
    groups = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3}
    batches = {}
    for it in items:
        if it.get('ownerReview'):
            continue
        n = groups[it['tier']]
        while sum(sizes[s] for s in batches.get(f'batch-{n}', [])) + sizes[it['slug']] > BATCH_TARGET:
            n += 1
        batches.setdefault(f'batch-{n}', []).append(it['slug'])
        it['batch'] = f'batch-{n}'
    batches = dict(sorted(batches.items(), key=lambda kv: int(kv[0].split('-')[1])))
    excluded.sort(key=lambda x: x['source']['id'])
    return {
        'note': 'Generated by tools/r2_inventory.py; upload records are written back by tools/r2_upload.py. Listing is not approval: '
                'each batch is uploaded only after the owner approves it.',
        'accountId': ACCOUNT_ID, 'bucket': BUCKET, 'publicBase': PUBLIC_BASE, 'freeTierBytes': FREE_TIER_BYTES, 'batchTargetBytes': BATCH_TARGET,
        'keyScheme': {'pdf': 'pdf/<slug>.pdf', 'epub': 'epub/<slug>.epub', 'scans': 'scans/<slug>/<leaf>.<ext>'},
        'snapshot': snap.get('refreshed'), 'items': items, 'excluded': excluded,
        'batches': {k: {'items': v, 'bytes': sum(f['bytes'] for it in items if it['slug'] in v for f in it['files'])} for k, v in batches.items()},
    }


def gb(n):
    return f'{n / 1e9:.2f} GB'


def mb(n):
    return f'{n / 1e6:.1f} MB'


def write_doc(m):
    items = m['items']
    total = sum(f['bytes'] for it in items for f in it['files'])
    held = sum(f['bytes'] for it in items for f in it['files'] if f['localPath'])
    review = [it for it in items if it.get('ownerReview')]
    images = sum(it.get('pageImagesBytes', 0) for it in items)
    lines = ['# R2 inventory', '',
             'Generated by `tools/r2_inventory.py` from `data/r2-manifest.json`; do not edit by hand. Every scan, PDF, and EPUB the',
             'library holds or can source, with its rights basis and a priority rank for upload to the `bibliotheca-files` bucket',
             f'(served at {PUBLIC_BASE}). Nothing is uploaded until the owner approves a batch; see [R2-RUNBOOK](R2-RUNBOOK.md).', '',
             '## Totals', '',
             f'- **{len(items)} items, {gb(total)}** in all, against the **10 GB** free tier ({total / m["freeTierBytes"]:.0%}). Held in git now: {mb(held)}.',
             f'- Waiting on the owner\'s review of a non-renewal scan: {len(review)} items, {gb(sum(f["bytes"] for it in review for f in it["files"]))}.',
             f'- Excluded (no clean basis or no public file): {len(m["excluded"])}.',
             f'- The page images behind these scans (JP2) come to {gb(images)}: too large for the free tier, so the site serves the scan PDF and',
             '  `scans/<slug>/` stays reserved for web-sized page images made later for a scan viewer.', '',
             '## Batches', '', '| Batch | Items | Size | Running total | Of free tier |', '|---|---|---|---|---|']
    run = 0
    for name, b in m['batches'].items():
        run += b['bytes']
        lines.append(f'| {name} | {len(b["items"])} | {gb(b["bytes"])} | {gb(run)} | {run / m["freeTierBytes"]:.0%} |')
    lines += ['', 'Batch 1 is what pairs with or was built from hosted texts; batch 2, near-gate books and series; batch 3, research candidates. Each stays under 3 GB; items under owner review join a batch once approved.', '',
              '## Items', '', '| # | Item | Year | Basis | Read gate | File | Size | Batch | Reason |', '|---|---|---|---|---|---|---|---|---|']
    for it in items:
        f = it['files'][0]
        flag = ' (owner review)' if it.get('ownerReview') else ''
        gate = it['readGate'] + (f' {it["readGateScore"]}%' if it.get('readGateScore') else '')
        title = it['title'].replace('|', '/')[:70]
        src = f'[{it["source"]["id"]}]({it["source"]["url"]})' if it['source']['kind'] == 'archive.org' else f'`{it["source"]["id"]}`'
        lines.append(f'| {it["priority"]} | {title}, {it["author"].split(";")[0][:40]} ({src}) | {it["year"] or "pre-" + str(pd_last_year() + 1)} | {it["rightsBasis"]}{flag} | {gate} | '
                     f'`{f["key"]}` | {mb(sum(x["bytes"] for x in it["files"]))} | {it.get("batch", "held")} | {it["priorityReason"]} |')
    lines += ['', '## Excluded', '', '| Source | Title | Year | Reason |', '|---|---|---|---|']
    for x in m['excluded']:
        lines.append(f'| [{x["source"]["id"]}]({x["source"]["url"]}) | {str(x["title"]).replace("|", "/")[:70]} | {x["year"] or "?"} | {x["reason"]} |')
    lines += ['', 'Fringe flags: no work in `data/library.json` is flagged in `data/editorial-flags.json` (its flags cover Isidore index',
              'records, which are never featured or pre-rendered), so every item here carries `fringe: false`. A flagged item would get',
              'an original-scan page with no featured placement.', '']
    DOC.write_text('\n'.join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--refresh', action='store_true', help='rebuild data/r2-sources.json from archive.org (network)')
    ap.add_argument('--check', action='store_true', help='fail if the manifest or inventory would change')
    a = ap.parse_args(argv)
    library = json.loads((ROOT / 'data/library.json').read_text())
    snap = json.loads(SOURCES.read_text())
    if a.refresh:
        ids = set(snap.get('archiveOrg', {})) | set(catalogue_scans(library)) | set(witness_scans(library)) | set(snap.get('candidates', {}))
        snap = refresh(ids)
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    m = build(snap, library, old)
    text = json.dumps(m, indent=1, ensure_ascii=False) + '\n'
    if a.check:
        before = (MANIFEST.read_text() if MANIFEST.exists() else '', DOC.read_text() if DOC.exists() else '')
        write_doc(m)
        MANIFEST.write_text(text)
        after = (MANIFEST.read_text(), DOC.read_text())
        if before != after:
            print('r2 inventory is out of date: run python3 tools/r2_inventory.py')
            return 1
        return 0
    MANIFEST.write_text(text)
    write_doc(m)
    total = sum(f['bytes'] for it in m['items'] for f in it['files'])
    print(f"R2 inventory: {len(m['items'])} items, {gb(total)}; {len(m['excluded'])} excluded; batches: "
          + ', '.join(f"{k} {gb(v['bytes'])}" for k, v in m['batches'].items()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
