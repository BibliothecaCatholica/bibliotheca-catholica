"""Assemble the deployable site into dist/ from tracked sources and generated outputs.

Only public site paths ship (`is_public()`, Phase 2 prep, docs/plans/build-on-deploy-plan.md section 5): the site shell
and root host files, every generated route directory, the assets the pages load, the app's data (less three build-only
folders), and docs/CATALOG.md, which the Open Data page links. Tools, tests, notes, and other repository-only files stay
in the repository and are not published."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
SKIP_DIRS = {
    '.git',
    'node_modules',
    'dist',
    '.validate',
    '.study-index',
    '.epub-build',
    '.local',
    '.openai',
    'epub-review',
    '__pycache__',
}
BUILT_ROOT_FILES = (
    'index.html',
    'study/index.html',
    '404.html',
    'sitemap.xml',
    'robots.txt',
    'build.json',
    'docs/static-pages.txt',
    'styles/rites.css',
)
BUILT_DIRS = (
    'drafts',
    'data',
    'assets/study',
    'assets/libraries',
    'pagefind',
    'downloads/epub',
)
REQUIRED_DIST_FILES = (
    'CNAME',
    '.nojekyll',
    '.well-known/atproto-did',
    'google3b007babfa8923a4.html',
    '_headers',
    'sitemap.xml',
    'robots.txt',
    '404.html',
    'build.json',
    'index.html',
    'study/index.html',
    'drafts/index.html',
)


# Never published: repository-only paths (assemble() fails if one reaches dist/).
REPO_ONLY = ('tools', 'tests', 'src', '.github', 'docs/static-pages.txt', 'docs/PROJECT-RULES.md', 'data/sources',
             'data/structured', 'data/rites-src', 'AGENTS.md', 'CENTRAL.md', 'HOLDS.md', 'README.md', 'CONTRIBUTING.md',
             'SECURITY.md', 'LICENSING.md', 'LICENSE', 'package.json', 'package-lock.json', '.gitattributes', '.gitignore')
# Root files that ship: the site shell, crawl files, and host and verification files.
PUBLIC_ROOT_FILES = frozenset({
    'index.html', '404.html', 'app.js', 'styles.css', 'sitemap.xml', 'robots.txt', 'build.json',
    'CNAME', '.nojekyll', '_headers', 'google3b007babfa8923a4.html',
})
# Directories whose whole contents ship: loaded by the pages (images, covers, fonts, scripts, styles, the Study
# bundles and search index, EPUBs), the app's data, the Bluesky handle, and the two routes not in the manifest.
PUBLIC_DIRS = ('.well-known', 'assets', 'fonts', 'scripts', 'styles', 'pagefind', 'downloads', 'data', 'study', 'drafts')
# Inside data/: build inputs no page links or fetches (source records live on texts.bibliothecacatholica.com).
BUILD_ONLY_DIRS = ('data/sources', 'data/structured', 'data/rites-src')
# Single files outside those directories that the site links.
PUBLIC_EXTRA_FILES = frozenset({
    'docs/CATALOG.md',  # "Sources & editorial notes" on the Open Data page (openData() in app.js)
})


def route_dirs() -> frozenset[str]:
    """Top-level route directories of the generated pages (docs/static-pages.txt, written by build_static.py)."""
    manifest = ROOT / 'docs/static-pages.txt'
    if not manifest.is_file():
        return frozenset()
    return frozenset(line.split('/', 1)[0] for line in manifest.read_text(encoding='utf-8').split() if '/' in line)


def is_public(rel: Path, routes: frozenset[str]) -> bool:
    """True when a repository-relative path belongs on the public site."""
    posix = rel.as_posix()
    if posix in PUBLIC_ROOT_FILES or posix in PUBLIC_EXTRA_FILES:
        return True
    if any(posix == d or posix.startswith(d + '/') for d in BUILD_ONLY_DIRS):
        return False
    top = rel.parts[0] if rel.parts else ''
    return len(rel.parts) > 1 and (top in PUBLIC_DIRS or top in routes)


def _should_skip(rel_parts: tuple[str, ...]) -> bool:
    return bool(SKIP_DIRS.intersection(rel_parts)) or (
        len(rel_parts) > 0 and rel_parts[-1].endswith('.pyc')
    )


def collect_paths() -> list[Path]:
    chosen: set[Path] = set()

    ls = subprocess.run(
        ['git', 'ls-files', '-z'],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    for raw in ls.stdout.split(b'\x00'):
        if not raw:
            continue
        rel = Path(raw.decode('utf-8'))
        if _should_skip(rel.parts):
            continue
        src = ROOT / rel
        if src.is_file():
            chosen.add(rel)

    for rel_str in BUILT_ROOT_FILES:
        rel = Path(rel_str)
        if (ROOT / rel).is_file():
            chosen.add(rel)

    manifest = ROOT / 'docs/static-pages.txt'
    if manifest.is_file():
        for line in manifest.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            rel = Path(line)
            if not _should_skip(rel.parts) and (ROOT / rel).is_file():
                chosen.add(rel)

    for d_str in BUILT_DIRS:
        base = ROOT / d_str
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_DIRS]
            for fn in sorted(filenames):
                if fn.endswith('.pyc'):
                    continue
                rel = (Path(dirpath) / fn).relative_to(ROOT)
                if not _should_skip(rel.parts):
                    chosen.add(rel)

    routes = route_dirs()
    return sorted(rel for rel in chosen if is_public(rel, routes))


def assemble() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    files = collect_paths()
    for rel in files:
        dst = DIST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)

    missing = [req for req in REQUIRED_DIST_FILES if not (DIST / req).is_file()]
    if missing:
        raise RuntimeError(f'dist/ is missing required files: {missing}')
    leaked = [p for p in REPO_ONLY if (DIST / p).exists()]
    if leaked:
        raise RuntimeError(f'dist/ holds repository-only paths: {leaked}')

    print(f'Assembled {len(files)} files into {DIST}')
    return len(files)


if __name__ == '__main__':
    assemble()
