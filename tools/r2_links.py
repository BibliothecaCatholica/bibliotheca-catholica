"""Site links to files in R2 (Round 8, Job B3; November 23, 2026). Used by tools/build_static.py.

A link appears only for a file that `data/r2-manifest.json` records as uploaded and verified (`upload.verified`), so with an
empty bucket the site is unchanged. Two places:
  * a work page's edition line: "Original scan (PDF, 22 MB)" for the scan an edition was transcribed from, "Dated scan"
    for the printing a hosted text was checked against, and "Source PDF" for an imported PDF print;
  * an "Original scan" page at /scan/<slug>/ for a book not yet transcribed (below the read gate) whose scan has a clean
    basis: clearly marked as not yet transcribed, linked from its work page only, never featured. A flagged (fringe) item's
    page is noindex and stays out of the sitemap.
Links are plain anchors to files.bibliothecacatholica.com, counted by the existing `outbound_click` handler (domain only).
No new analytics event.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = lambda s: html.escape(str(s), quote=True)


def mb(n):
    return f'{n / 1e6:.0f} MB' if n >= 10**6 else f'{max(1, round(n / 1e3))} KB'


class R2Links:
    def __init__(self, manifest):
        self.items = []
        for it in (manifest or {}).get('items', []):
            if it.get('ownerReview'):
                continue
            files = [f for f in it['files'] if (f.get('upload') or {}).get('verified')]
            if files:
                self.items.append({**it, 'files': files})

    @classmethod
    def load(cls, path=ROOT / 'data/r2-manifest.json'):
        return cls(json.loads(Path(path).read_text()) if Path(path).exists() else None)

    def scan_pages(self):
        """Items that get an "Original scan" page: a PDF scan of a book not hosted here yet."""
        return [it for it in self.items if it['readGate'] != 'hosted' and it['source']['kind'] == 'archive.org'
                and any(f['kind'] == 'pdf' for f in it['files'])]

    def edition_links(self, eid):
        """' · ' separated links for one catalogue edition's line on its work page ('' when nothing is uploaded)."""
        out = []
        for it in self.items:
            for f in it['files']:
                if f['kind'] != 'pdf':
                    continue  # EPUBs keep their in-site link until the migration plan's step 2
                size = ' (PDF, ' + mb(f['bytes']) + ')'
                if it['source']['kind'] == 'pdf-print' and it['editionId'] == eid:
                    out.append(f'<a href="{E(f["url"])}" download>Source PDF</a> ({mb(f["bytes"])})')
                elif it['source']['kind'] == 'archive.org' and it.get('editionId') == eid:
                    if it in self.scan_pages():
                        out.append(f'<a href="/scan/{E(it["slug"])}/">Original scan</a> (not yet transcribed)')
                    else:
                        out.append(f'<a href="{E(f["url"])}">Original scan</a>{size}')
                elif it['source']['kind'] == 'archive.org' and not it.get('editionId') and it.get('hostedEditionId') == eid:
                    out.append(f'<a href="{E(f["url"])}">Dated scan, {E(it["year"])}</a>{size}')
        return ''.join(' · ' + x for x in out)

    def scan_page(self, it, work_href=None):
        """(route, title, description, body, jsonld, noindex) for one "Original scan" page."""
        f = next(f for f in it['files'] if f['kind'] == 'pdf')
        title = it['title']
        basis = ('Public domain in the United States: first published ' + str(it['year']) + '.' if it['rightsBasis'] == 'pd-date' else
                 'Public domain in the United States: published ' + str(it['year']) + ' with no copyright renewal (renewal search recorded).')
        gate = ('Our transcription is in progress (read-gate score ' + str(it['readGateScore']) + '%; a book is hosted as text at 99.5%).'
                if it.get('readGateScore') else 'This book has not been transcribed here.')
        body = ('<div class="page-head"><div class="eyebrow">Original scan · not yet transcribed</div><h1>' + E(title) + '</h1>'
                '<p class="lede">By ' + E(it['author'].split(';')[0]) + (', ' + E(it['year']) if it['year'] else '') + '. '
                'A page-image scan of the printed book. ' + E(gate) + '</p></div>'
                '<p class="callout"><b>Not yet transcribed.</b> This is the scanned book as printed, not a checked reading text, so it is not '
                'searchable here and is not in the reader. Listing is not endorsement.</p>'
                '<div class="dl-row"><a class="btn" href="' + E(f['url']) + '">Open the scan (PDF, ' + mb(f['bytes']) + ')</a></div>'
                '<h2>Edition details</h2><ul><li>Scan: <a href="' + E(it['source']['url']) + '" target="_blank" rel="noopener">Internet Archive, '
                + E(it['source']['id']) + '</a></li><li>Rights: ' + E(basis) + ' Outside the U.S., check local copyright rules.</li>'
                '<li>File: SHA-256 <code>' + E(f['upload']['sha256']) + '</code></li>'
                + ('<li>Work page: <a href="' + E(work_href) + '">' + E(title) + '</a></li>' if work_href else '') + '</ul>')
        desc = (title + ' by ' + it['author'].split(';')[0] + ': the original scan of the printed book (PDF), not yet transcribed, '
                'with its source and rights basis.')
        return ('scan/' + it['slug'], title + ' (original scan) · Bibliotheca Catholica', desc, body, (), bool(it.get('fringe')))
