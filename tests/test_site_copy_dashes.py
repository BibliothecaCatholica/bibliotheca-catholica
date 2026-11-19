"""No em-dashes in our own site copy (AGENTS.md rule 5; audit leftovers, owner go-ahead November 19, 2026).

Covered: resource names and descriptions, author link labels, project names, edition labels, and every static page's
<main> outside book texts. Left alone on purpose: hosted book texts and chapter, story, and Summa article pages;
quotations (blockquotes, plan excerpts); Wikipedia extracts; Wikimedia credit strings, quoted as given on /credits/;
Substack post titles; and the Isidore catalogue's third-party records and subject headings."""
import json, re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
D = '—'


def jsvar(path, var):
    s = (ROOT / path).read_text(encoding='utf-8'); p = 'window.%s=' % var
    return json.loads(s[s.index(p) + len(p):].rstrip().rstrip(';'))


class SiteCopyDashes(unittest.TestCase):
    def test_data_copy(self):
        hub = json.loads((ROOT / 'data/catholic-hub.json').read_text(encoding='utf-8'))
        for r in hub['resources']:
            self.assertNotIn(D, r['name'] + r.get('desc', ''), r['name'])
        for a in hub['authors']:
            for l in a.get('links', []):
                self.assertNotIn(D, l.get('label', ''), a['id'])
        for p in jsvar('data/projects.js', 'PROJECTS_DATA')['items']:
            self.assertNotIn(D, p['n'] + p.get('m', '') + p.get('d', '') + p.get('why', ''), p['id'])
        lib = json.loads((ROOT / 'data/library.json').read_text(encoding='utf-8'))
        for w in lib['works']:
            for e in w['editions']:
                self.assertNotIn(D, e.get('label', ''), e['id'])

    def test_rendered_pages(self):
        skip = re.compile(r'(work/[^/]+/(ch|story)/|summa/[^/]+/q|drafts/|credits/)')
        pages = (ROOT / 'docs/static-pages.txt').read_text().split() + ['index.html', 'study/index.html']
        for p in pages:
            if skip.match(p):
                continue
            h = (ROOT / p).read_text(encoding='utf-8')
            if '<main' not in h:
                continue
            m = h[h.index('<main'):h.index('</main>')]
            m = re.sub(r'<blockquote.*?</blockquote>|<p class="plan-excerpt.*?</p>|<div class="reading-text.*?</div>', '', m, flags=re.S)
            self.assertNotIn(D, re.sub(r'<[^>]+>', ' ', m), p)

    def test_credits_page_dashes_are_quoted_credits_only(self):
        h = (ROOT / 'credits/index.html').read_text(encoding='utf-8')
        m = re.sub(r'<[^>]+>', ' ', h[h.index('<main'):h.index('</main>')])
        hub = json.loads((ROOT / 'data/catholic-hub.json').read_text(encoding='utf-8'))
        credits = ' '.join(str((a.get('imgCredit') or {}).get('artist', '')) for a in hub['authors'])
        for x in re.finditer(D, m):
            self.assertIn(re.sub(r'\s+', ' ', m[max(0, x.start() - 12):x.start() + 1]).strip()[-6:], credits)


if __name__ == '__main__':
    unittest.main()
