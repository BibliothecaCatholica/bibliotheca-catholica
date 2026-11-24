"""Internal link check for the built site (offline; Round 8, Job F, November 23, 2026).

    python3 tools/check_internal_links.py [--out docs/link-health-internal.json]

Reads every tracked HTML page and checks each same-site link (`href` and `src`): root-relative paths ("/work/x/"), paths
relative to the pages' `<base href="/">`, and absolute links to bibliothecacatholica.com. A link is good when the path is a
tracked file, or a folder whose index.html is tracked. App hash routes (`/#/read/...`), fragments, `mailto:`, `tel:`,
`javascript:`, `data:`, and other sites are skipped (tools/check_links.py checks other sites). Writes a JSON report and a
Markdown summary; exits 0 either way (the weekly workflow reports, it never fails a build).
"""
import argparse
import html
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTR = re.compile(r'\s(?:href|src)="([^"]*)"')
SKIP = ('mailto:', 'tel:', 'javascript:', 'data:', 'blob:', '#')
SITE_HOSTS = ('bibliothecacatholica.com', 'www.bibliothecacatholica.com')
IGNORE_DIRS = ('node_modules/', '.validate/', 'epub-review/', 'dist/')


def tracked():
    out = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True).stdout.decode().split('\0')
    return {p for p in out if p and not p.startswith(IGNORE_DIRS)}


def target(link):
    """The repository path a same-site link points to, or None when it is not a same-site file link."""
    link = html.unescape(link.strip())
    if not link or link.startswith(SKIP) or link.startswith('/#') or link.startswith('#'):
        return None
    u = urllib.parse.urlsplit(link)
    if u.scheme in ('http', 'https'):
        if (u.hostname or '').lower() not in SITE_HOSTS:
            return None
    elif u.scheme or link.startswith('//'):
        return None
    path = urllib.parse.unquote(u.path)
    if not path or path == '/':
        return 'index.html'
    return path.lstrip('/')


def resolves(path, files):
    if path in files:
        return True
    folder = path.rstrip('/')
    return (folder + '/index.html') in files


def check(files):
    broken, links, pages = {}, 0, 0
    for page in sorted(p for p in files if p.endswith('.html')):
        try:
            text = (ROOT / page).read_text(errors='ignore')
        except FileNotFoundError:
            continue
        pages += 1
        for raw in ATTR.findall(text):
            t = target(raw)
            if t is None:
                continue
            links += 1
            if not resolves(t, files):
                broken.setdefault(t, set()).add(page)
    return pages, links, broken


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', default=str(ROOT / 'docs/link-health-internal.json'))
    a = ap.parse_args(argv)
    t0 = time.time()
    pages, links, broken = check(tracked())
    rep = {'checked': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), 'seconds': round(time.time() - t0, 2), 'pages': pages,
           'links': links, 'broken': [{'path': k, 'pages': sorted(v)[:10], 'pageCount': len(v)} for k, v in sorted(broken.items())]}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    md = [f'# Internal links ({rep["checked"]})', '', f'{links:,} same-site links in {pages:,} pages; {len(broken)} broken targets.', '']
    if broken:
        md += ['| Missing path | Pages | Example page |', '|---|---|---|']
        md += [f'| /{b["path"]} | {b["pageCount"]} | /{b["pages"][0]} |' for b in rep['broken']]
    out.with_suffix('.md').write_text('\n'.join(md) + '\n')
    print(f'{links} links in {pages} pages; {len(broken)} broken -> {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
