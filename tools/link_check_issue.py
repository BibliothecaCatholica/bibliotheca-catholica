"""The body of the single weekly link-check issue (Round 8, Job F, November 23, 2026).

    python3 tools/link_check_issue.py REPORT_DIR    # reads internal.json and outbound.json, writes REPORT_DIR/issue.md

Prints `failures=N` (and appends it to $GITHUB_OUTPUT when set). Broken internal links, and outbound links that are gone
(4xx other than bot blocks), parked, moved to another site, server errors, or timeouts count as failures. Bot-protection
answers (401, 403, 429) are listed for reference but are not failures: those sites usually block automated checks.
Never exits non-zero: the workflow reports, it does not fail.
"""
import json
import os
import sys
from pathlib import Path

FAIL = ('client-error', 'soft-404/parked', 'redirect-offsite', 'server-error', 'timeout/error')
MAX_ROWS = 150  # keeps the issue body well under GitHub's 65,536-character limit


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def body(internal, outbound, run_url=''):
    lines = ['Weekly link check. This issue is opened and updated by `.github/workflows/link-check.yml`; it closes itself when a run '
             'finds no failures. Fix the source data (never a generated page), then let the next run confirm.', '']
    if run_url:
        lines += [f'Run: {run_url}', '']
    failures = 0
    if internal is None:
        lines += ['**Internal links:** the check did not finish (see the run log).', '']
    else:
        broken = internal.get('broken', [])
        failures += len(broken)
        lines += [f'**Internal links:** {internal["links"]:,} links in {internal["pages"]:,} pages; {len(broken)} broken targets.', '']
        if broken:
            lines += ['| Missing path | Pages | Example page |', '|---|---|---|']
            lines += [f'| `/{b["path"]}` | {b["pageCount"]} | `/{b["pages"][0]}` |' for b in broken[:MAX_ROWS]]
            lines += ['']
    if outbound is None:
        lines += ['**Outbound links:** the check did not finish (see the run log).', '']
    else:
        bad = [r for r in outbound.get('results', []) if r['cls'] in FAIL]
        blocked = [r for r in outbound.get('results', []) if r['cls'] == 'blocked']
        failures += len(bad)
        cap = ' (partial run: time cap reached)' if outbound.get('capped') else ''
        lines += [f'**Outbound links:** {outbound["checked_urls"]:,} of {outbound["total_urls"]:,} URLs checked{cap}; {len(bad)} failures; '
                  f'{len(blocked)} blocked by bot protection (not counted).', '']
        if bad:
            lines += ['| Class | Status | URL | Final URL or note | Found in |', '|---|---|---|---|---|']
            for r in sorted(bad, key=lambda r: (r['cls'], r['url']))[:MAX_ROWS]:
                note = r['final'] if r['final'] != r['url'] else r['title']
                lines.append(f'| {r["cls"]} | {r["status"]} | {r["url"]} | {str(note)[:90]} | {", ".join(r.get("files", []))} |')
            if len(bad) > MAX_ROWS:
                lines.append(f'| … | | {len(bad) - MAX_ROWS} more in the run artifact | | |')
            lines += ['']
    return '\n'.join(lines), failures


def main(argv=None):
    d = Path((argv or sys.argv[1:] or ['link-report'])[0])
    run_url = ''
    if os.environ.get('GITHUB_RUN_ID'):
        run_url = f'{os.environ.get("GITHUB_SERVER_URL", "https://github.com")}/{os.environ.get("GITHUB_REPOSITORY")}/actions/runs/{os.environ["GITHUB_RUN_ID"]}'
    text, failures = body(load(d / 'internal.json'), load(d / 'outbound.json'), run_url)
    d.mkdir(parents=True, exist_ok=True)
    (d / 'issue.md').write_text(text + '\n')
    print(f'failures={failures}')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f'failures={failures}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
