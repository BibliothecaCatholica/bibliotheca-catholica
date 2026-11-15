#!/usr/bin/env python3
"""Export verified reading copies into the separate bibliotheca-texts checkout."""
import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path

from build_library import ROOT, validate
from rights_rule import TERM, pd_last_year

ARCHIVE = 'https://texts.bibliothecacatholica.com'
SITE = 'https://bibliothecacatholica.com'


def export(output):
    output = Path(output).resolve()
    if output == ROOT or output.is_relative_to(ROOT):
        raise ValueError('Export into the separate document repository, outside the website checkout.')
    catalog = validate(json.loads((ROOT / 'data/library.json').read_text()))
    output.mkdir(parents=True, exist_ok=True)
    entries, converted = [], []
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
            record = json.loads((ROOT / 'data/sources' / (edition['id'] + '.json')).read_text())
            if record.get('sourceName'):  # imported by tools/import_plain_text.py: converted, header added
                converted.append(f"`{filename}` ({record['sourceName']}; see `provenance/{edition['id']}.json`)")
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
<title>Text collection · Bibliotheca Catholica</title><meta name="description" content="Verified reading copies, original source credits, and downloadable Catholic classics.">
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
<p>Each edition’s basis for hosting, usually public domain in the United States, is recorded in the manifest. Edition-specific rights notes and original Project Gutenberg notices are retained; the Summa Supplement is our transcription of Internet Archive scans, On Christian Doctrine is the Shaw / NPNF text from the CCEL Public Domain plain-text edition, and The Incredulity of Father Brown is the Standard Ebooks (CC0) text corrected to the 1926 printings. Check the applicable rules where you live. Source records establish edition identity and access; they are not endorsements of every statement.</p>
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
    (output / 'README.md').write_text(readme())
    (output / 'NOTICE.md').write_text('''# Notice

This repository holds copies of texts whose basis for hosting Bibliotheca Catholica (https://bibliothecacatholica.com) checked and recorded, edition by edition: usually public domain in the United States, otherwise an open license or the holder's written permission. This notice is a summary, not legal advice.

- **No license from us.** Bibliotheca Catholica claims no rights in these texts and adds no license. There is no blanket license over this repository; it is not MIT and not CC0.
- **Source notices apply.** Each file is kept byte for byte as its source published it, except `ia-summa-supplement.txt` (Bibliotheca Catholica's own transcription of public-domain Internet Archive scans; see `provenance/ia-summa-supplement.json`) `ccel-npnf102-doctrine.txt` (Shaw translation extracted from the CCEL NPNF1-02 Public Domain plain text; see `provenance/ccel-npnf102-doctrine.json`), and `se-incredulity-father-brown.txt` (converted from the Standard Ebooks source files, which Standard Ebooks dedicates to the public domain under CC0 1.0, with word-level corrections to the 1926 printings; see `provenance/se-incredulity-father-brown.json`).__CONVERTED__ Project Gutenberg files keep their full Project Gutenberg License and credits, and those terms apply to them as distributed (https://www.gutenberg.org/policy/license.html). "Project Gutenberg" is a registered trademark of the Project Gutenberg Literary Archive Foundation.
- **United States only.** Public-domain status is a United States designation for each edition. An edition with unresolved rights is not hosted. Outside the United States, check your local law before reusing a text.
- **Records.** `manifest.json` lists each file's rights statement and SHA-256 checksum, and `provenance/` holds the source catalog snapshots. In the main repository, only the open data in `data/open/` and the reading catalog metadata in `data/library.json` are CC0; its code is MIT, and its other files carry the terms set out in https://github.com/BibliothecaCatholica/bibliotheca-catholica/blob/main/LICENSING.md.
- **Concerns.** A rights holder can follow https://bibliothecacatholica.com/takedown/.
'''.replace('__CONVERTED__', (' Texts imported from other sources are converted to UTF-8 plain text with no words '
                               'changed; each keeps its source\'s own header, licence, and notices unchanged below a short '
                               'header of ours, and its provenance record gives the source file\'s SHA-256 and a word-by-word '
                               'comparison with a dated scan: ' + ', '.join(converted) + '.') if converted else ''))
    print(f"Exported {len(entries)} texts, {manifest['totalBytes']:,} bytes, to {output}")
    return manifest


def readme():
    """README for bibliotheca-texts. The hosting rule is stated once in tools/rights_rule.py; its year is computed."""
    y = pd_last_year()
    return f'''# Bibliotheca Catholica text collection

Served at https://texts.bibliothecacatholica.com by GitHub Pages from `main`.

Read these texts in the reader at [Bibliotheca Catholica](https://bibliothecacatholica.com), the free library of Catholic authors and classics this collection serves.

This repository contains verified copies of the main library’s hosted texts. Original bytes, credits, and source notices are preserved. Individual edition rights and SHA-256 hashes are recorded in `manifest.json`; source metadata snapshots are in `provenance/`. See `NOTICE.md`.

## Hosting scope

There is **no fixed publication-date cutoff**. Public domain in the United States by date is the usual basis for hosting: in {y + 1 + TERM}, that means first published in {y} or earlier, and the line moves forward one year each January 1. Past that line, United States public-domain reasoning stops being automatic, so a later edition is hosted only when its basis is recorded explicitly instead of assumed. Every hosted edition, of any date, needs a named source, a provenance record, and a rights entry before it lands. Texts may come from any source; the rights belong to the edition, not the website it came from.

Hosting here is a **United States** designation, not worldwide clearance. No blanket license overrides the individual source notices. An edition with unresolved rights stays out until the question is answered; unknown fails closed.

### How editions past the date line are handled

- Record the basis for hosting in the edition’s provenance record: public domain by non-renewal (renewal search cited, and URAA restoration checked for a work first published abroad), public domain by a missing or defective notice, an open license (with the license named), or permission granted (with the grant quoted and dated).
- Keep the copyright page, publisher line, translator credit, and any front-matter notice with the text. Do not strip a notice because the file looks like an older scan.
- Name the translation and the printing, not just the work. A 1910 translation and a 1975 revision of the same title are different rights objects and get separate records.
- Where a source already asserts a status, quote it. Do not upgrade, launder, or paraphrase a source’s claim into your own.
- An edition still in copyright with no documented permission is link only. It is not hosted, in whole or in part.
- Where a source’s own terms conflict with this repository’s habits, the source wins.

### Rights badges

Every edition carries one badge, using the same five values as the main library and explained at [/rights/](https://bibliothecacatholica.com/rights/):

| Badge | Meaning here |
|---|---|
| Public domain (US) | No live US copyright on the edition; date, non-renewal, or defect recorded |
| Open license | A named license permits redistribution; license text retained |
| Permission granted | Written grant from the holder, quoted and dated in `provenance/` |
| Link only | Catalogued but not hosted; readers go to the holder |
| Unknown | Not hosted; the open question is written down |

Only the first three are hosted. A takedown request is honored first; the record is corrected afterward, not defended.

## Layout

- `texts/`: the hosted text files, with stable names
- `manifest.json`: edition IDs, rights statement, source URL, SHA-256
- `provenance/`: source metadata snapshots and, where applicable, grant text
- `NOTICE.md`: the standing rights and takedown statement

Do not rename a published file; readers and citations point at those paths. Retire a file by leaving it and marking the record, not by deleting it.

## Publishing an export

The authoritative catalog, reader, and export tool remain in https://github.com/BibliothecaCatholica/bibliotheca-catholica. To refresh this checkout, run

```sh
python3 tools/build_text_archive.py --output /absolute/path/to/bibliotheca-texts
```

from that repository, then review the diff and `manifest.json` before committing. The export is offline and downloads no additional works. The exporter never deletes files, so check for stale or retired paths by hand on each later export.

Before publishing, confirm for every new edition:

1. A provenance record exists and names the actual source copy.
2. A rights statement is set and its basis is written down.
3. Source notices survive in the text.
4. The SHA-256 matches the file actually being committed.
5. The file name does not collide with an existing edition.

New hosted editions also require edition-specific rights review under the main repository’s contributor guide. Do not replace this repository with unreviewed Isidore downloads.

## Limits and housekeeping

Keep GitHub Pages below its published size and traffic limits; prefer text over page images, and split oversized files by book or chapter rather than by page. Keep an independent backup: this repository is a delivery copy, not the archive of record.

## Corrections and takedown

Open an issue at https://github.com/BibliothecaCatholica/bibliotheca-catholica/issues/new/choose for a wrong file, wrong credit, or wrong rights record. Rights holders can use https://bibliothecacatholica.com/takedown/; include the edition ID and the basis for the claim.
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    export(parser.parse_args().output)
