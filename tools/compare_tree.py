"""Compare two SHA-256 manifest files (or directories) and report missing, extra, or changed files."""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

SKIP_DIRS = {'.git', 'node_modules', 'dist', '.validate', '.study-index', '.epub-build', '.local', '.openai', 'epub-review', '__pycache__'}


def read_manifest(target: Path) -> dict[str, str]:
    if target.is_dir():
        out: dict[str, str] = {}
        for dirpath, dirnames, filenames in os.walk(target):
            dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_DIRS]
            for fn in sorted(filenames):
                p = Path(dirpath) / fn
                rel = p.relative_to(target).as_posix()
                out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
        return out

    out = {}
    for line in target.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(None, 1)
        rel = rel.lstrip('*')
        if rel.startswith('./'):
            rel = rel[2:]
        out[rel] = digest
    return out


def compare(left_path: Path, right_path: Path) -> int:
    left = read_manifest(left_path)
    right = read_manifest(right_path)

    only_left = sorted(set(left) - set(right))
    only_right = sorted(set(right) - set(left))
    changed = sorted(k for k in (set(left) & set(right)) if left[k] != right[k])

    print(f'Only in {left_path}: {len(only_left)}')
    for p in only_left:
        print(f'  - {p}')

    print(f'Only in {right_path}: {len(only_right)}')
    for p in only_right:
        print(f'  + {p}')

    print(f'Differing sha256: {len(changed)}')
    for p in changed:
        print(f'  ~ {p} ({left[p][:12]} != {right[p][:12]})')

    if not only_left and not only_right and not changed:
        print(f'MATCH: {len(left)} files identical by sha256.')
        return 0
    return 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 tools/compare_tree.py <committed.sha|dir> <built.sha|dir>', file=sys.stderr)
        sys.exit(2)
    sys.exit(compare(Path(sys.argv[1]), Path(sys.argv[2])))
