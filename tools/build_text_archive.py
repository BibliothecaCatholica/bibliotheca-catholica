#!/usr/bin/env python3
"""Export verified reading copies into the separate bibliotheca-texts checkout."""
import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path

from build_library import ROOT, validate

ARCHIVE = 'https://texts.bibliothecacatholica.com'
SITE = 'https://bibliothecacatholica.com'


def export(output):
    output = Path(output).resolve()
    if output == ROOT or output.is_relative_to(ROOT):
        raise ValueError('Export into the separate document repository, outside the website checkout.')
    catalog = validate(json.loads((ROOT / 'data/library.json').read_text()))
    output.mkdir(parents=True, exist_ok=True)
    entries = []
    for work in catalog['works']:
        for edition in work['editions']:
            if not edition.get('text'):
                continue
            raw = (ROOT / edition['text']).read_bytes()
            filename = Path(edition['text']).name
            for relative, content in [
                ('texts/' + filename, raw),
                ('provenance/' + edition['id'] + '.json',
                 (ROOT / 'data/sources' / (edition['id'] + '.json')).read_bytes()),
            ]:
                destination = output / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
            entries.append({
                'workId': work['id'], 'editionId': edition['id'],
                'title': work['title'], 'author': work['author'],
                'language': edition.get('language', 'English'),
                'edition': edition['label'], 'contributors': edition.get('contributors', []),
                'rights': edition['rights'], 'source': edition['source'],
                'checked': edition['checked'], 'bytes': len(raw),
                'sha256': hashlib.sha256(raw).hexdigest(),
                'file': 'texts/' + filename,
                'provenance': 'provenance/' + edition['id'] + '.json',
                'read': SITE + '/#/read/' + work['id'] + '/' + edition['id'],
                'details': SITE + '/work/' + work['id'] + '/',
            })
    manifest = {'schemaVersion': 1, 'origin': ARCHIVE,
                'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'totalBytes': sum(e['bytes'] for e in entries), 'documents': entries}
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    escape = lambda value: html.escape(str(value), quote=True)
    rows = []
    for e in entries:
        credits = ', '.join(c['role'] + ': ' + c['name'] for c in e['contributors'])
        rows.append('<article><h2>' + escape(e['title']) + '</h2><p>' + escape(e['author']) +
                    '</p><p class="meta">' + escape(e['edition'] + ' · ' + e['language']) +
                    ('<br>' + escape(credits) if credits else '') + '</p><nav>' +
                    '<a class="primary" href="' + escape(e['read']) + '">Read in the library</a>' +
                    '<a href="' + escape(e['file']) + '" download>Download TXT</a>' +
                    '<a href="' + escape(e['details']) + '">Edition details</a></nav>' +
                    '<details><summary>Source, rights, and file verification</summary><p>' + escape(e['rights']) +
                    '</p><p><a href="' + escape(e['source']) + '">Original source</a> · <a href="' +
                    escape(e['provenance']) + '">Source record</a> · ' + escape(e['bytes']) +
                    ' bytes</p><p class="hash">SHA-256: ' + e['sha256'] + '</p></details></article>')
    template = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Text collection — Bibliotheca Catholica</title><meta name="description" content="Verified reading copies, original source credits, and downloadable Catholic classics.">
<link rel="canonical" href="https://texts.bibliothecacatholica.com/">
<style>
:root{color-scheme:light dark;--bg:#f6f0e2;--card:#fffaf0;--ink:#2a2118;--accent:#8b1e2d;--line:#d8c9ad}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.65 Georgia,serif}
main{max-width:1000px;margin:auto;padding:40px 24px}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2.2rem,6vw,3.6rem);line-height:1.15;margin:24px 0 12px}h2{font-size:1.5rem;line-height:1.3;margin:0}
.eyebrow,.meta,label,nav,summary,footer{font:15px/1.6 system-ui,sans-serif}.eyebrow{letter-spacing:.12em;text-transform:uppercase}
header{border-bottom:1px solid var(--line);padding-bottom:28px}header p{max-width:720px}.toolbar{margin:26px 0}
input{display:block;width:100%;padding:14px;margin-top:6px;font:18px system-ui;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
article{background:var(--card);padding:24px;border:1px solid var(--line);border-radius:8px;margin:18px 0}article p{margin:8px 0 16px}
nav{display:flex;gap:12px;flex-wrap:wrap;align-items:center}nav a{padding:8px 12px;border:1px solid var(--line);border-radius:5px}
nav .primary{background:var(--accent);color:var(--card);border-color:var(--accent);text-decoration:none}details{margin-top:20px}summary{cursor:pointer}.hash{overflow-wrap:anywhere;font:12px/1.7 monospace}
footer{border-top:1px solid var(--line);padding:24px 0;margin-top:32px}[hidden]{display:none}
@media(prefers-color-scheme:dark){:root{--bg:#14161c;--card:#1f232c;--ink:#ece4d4;--accent:#e0707b;--line:#44414a}}
</style></head><body><main><header><a href="https://bibliothecacatholica.com/">← Bibliotheca Catholica</a>
<p class="eyebrow">The text collection</p><h1>Keep a classic close.</h1>
<p>Complete reading copies from the library’s selected collection. Read with the library’s display controls, or download an original text with its source credits and notices intact.</p>
<p class="meta">__COUNT__ editions · __SIZE__ MB of text · <a href="manifest.json">Collection manifest</a></p></header>
<div class="toolbar"><label for="find">Find a title, author, or translator<input id="find" type="search" placeholder="Augustine, Newman, Chesterton…"></label><p id="count" role="status">__COUNT__ editions</p></div>
<section aria-label="Available documents">__ROWS__</section><footer>
<p>These editions are public domain in the United States. Edition-specific rights notes and original Project Gutenberg notices are retained. Check the applicable rules where you live. Source records establish edition identity and access; they are not endorsements of every statement.</p>
<a href="https://bibliothecacatholica.com/policy/">Fidelity &amp; Editorial Policy</a> · <a href="https://bibliothecacatholica.com/library/">Explore the reading collection</a>
</footer></main><script>
const input=document.getElementById('find'),cards=Array.from(document.querySelectorAll('article'));
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
input.addEventListener('input',()=>{const terms=norm(input.value).trim().split(/\\s+/);let n=0;cards.forEach(card=>{card.hidden=!terms.every(t=>norm(card.textContent).includes(t));if(!card.hidden)n++});document.getElementById('count').textContent=n+(n===1?' edition':' editions')});
</script></body></html>
'''
    (output / 'index.html').write_text(template.replace('__COUNT__', str(len(entries))).replace('__SIZE__', f"{manifest['totalBytes']/1_000_000:.2f}").replace('__ROWS__', '\n'.join(rows)))
    (output / 'CNAME').write_text('texts.bibliothecacatholica.com\n')
    (output / '.nojekyll').touch()
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /texts/\nDisallow: /provenance/\n')
    (output / 'README.md').write_text('''# Bibliotheca Catholica text collection

Served at https://texts.bibliothecacatholica.com by GitHub Pages from `main`.

Read these texts in the reader at [Bibliotheca Catholica](https://bibliothecacatholica.com) (https://bibliothecacatholica.com), the free library of Catholic authors and classics this collection serves.

This repository contains verified copies of the main library’s hosted texts. Original bytes, credits, and Project Gutenberg notices are preserved. Individual edition rights and SHA-256 hashes are recorded in `manifest.json`; source metadata snapshots are in `provenance/`. These are United States public-domain designations, not worldwide clearance. No blanket license overrides the individual source notices.

The authoritative catalog, reader, and export tool remain in https://github.com/BibliothecaCatholica/bibliotheca-catholica. To refresh this checkout, run `python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts` from that repository, review the diff and manifest, and publish it here. The export is offline and does not download additional works. Check for stale or retired files before publishing a later export; the exporter never deletes files.

Do not replace this repository with unreviewed Isidore downloads. New hosted editions require edition-specific rights review under the main repository’s contributor guide. Keep GitHub Pages below its published size and traffic limits. Keep an independent backup.
''')
    print(f"Exported {len(entries)} texts, {manifest['totalBytes']:,} bytes, to {output}")
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    export(parser.parse_args().output)
