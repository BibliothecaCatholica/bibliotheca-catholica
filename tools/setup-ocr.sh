#!/usr/bin/env bash
# Install Tesseract and the language packs tools/transcribe_scan.py's second OCR uses (secondOcr, PROJECT-RULES rule 1,
# "Read gate"), then check that each pack is present. Containers do not keep it between sessions, so run this once per
# session, or paste the line below into the cloud environment's setup script:
#
#   bash tools/setup-ocr.sh
#
# Needs root (apt). Exits non-zero if tesseract or any language pack is missing afterwards.
set -euo pipefail
LANGS=(eng lat ita fra deu)
if ! command -v tesseract >/dev/null 2>&1 || [ "${1:-}" = "--force" ]; then
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  $SUDO apt-get update -qq
  $SUDO apt-get install -y tesseract-ocr tesseract-ocr-lat tesseract-ocr-ita tesseract-ocr-fra tesseract-ocr-deu
fi
have=$(tesseract --list-langs 2>/dev/null | tail -n +2)
missing=()
for l in "${LANGS[@]}"; do grep -qx "$l" <<<"$have" || missing+=("$l"); done
if [ ${#missing[@]} -gt 0 ]; then
  echo "setup-ocr: missing Tesseract language packs: ${missing[*]}" >&2
  exit 1
fi
echo "setup-ocr: $(tesseract --version 2>&1 | head -1); languages: ${LANGS[*]}"
