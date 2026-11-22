"""Assemble the complete deployable site into dist/ from tracked sources and generated outputs."""
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

    return sorted(chosen)


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

    print(f'Assembled {len(files)} files into {DIST}')
    return len(files)


if __name__ == '__main__':
    assemble()
