#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
npm ci
npm run build
python3 tools/build_static.py
npm run build:study
python3 tools/assemble_dist.py
