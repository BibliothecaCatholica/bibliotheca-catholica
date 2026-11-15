#!/usr/bin/env bash
# The validation procedure in docs/OPERATIONS.md#validation as one command (agent efficiency, November 15, 2026).
#
#   npm run validate            build, static, study, tests, and syntax checks (before committing)
#   npm run validate -- --drift after committing: rebuild, then fail on any tracked change or untracked file
#
# Each step's full output goes to .validate/<step>.log; only a one-line result per step is printed, plus the
# log's last lines when a step fails. CI (.github/workflows/validate.yml) stays authoritative.
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=.validate; mkdir -p "$LOG"; FAIL=0
step() {  # step <name> <command...>
  local name=$1; shift
  local t0=$SECONDS
  if "$@" >"$LOG/$name.log" 2>&1; then
    printf 'ok    %-12s %3ss  %s\n' "$name" $((SECONDS-t0)) "$(grep -v '^\s*$' "$LOG/$name.log" | tail -1 | cut -c1-90)"
  else
    printf 'FAIL  %-12s %3ss  (%s)\n' "$name" $((SECONDS-t0)) "$LOG/$name.log"
    grep -E '^(FAIL|ERROR|not ok|AssertionError|Traceback)|Error:' "$LOG/$name.log" | head -15
    tail -5 "$LOG/$name.log"; FAIL=1
  fi
}
step build    npm run build
step static   python3 tools/build_static.py
step study    npm run build:study
if [ "${1:-}" = "--drift" ]; then
  step drift  bash -c 'git diff --exit-code --stat && test -z "$(git status --short)"'
  exit $FAIL
fi
step test     npm test
step whitespace git diff --check
step syntax   bash -c 'node --check app.js && find scripts -name "*.js" -exec node --check {} \; && node --check data/site-copy.js'
step counts   python3 tools/hosted_counts.py --check
exit $FAIL
