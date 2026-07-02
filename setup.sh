#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

"${PYTHON_BIN}" - <<'PY'
import sys

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required")
PY

"${PYTHON_BIN}" -m venv "${ROOT_DIR}/.venv"
"${ROOT_DIR}/.venv/bin/python" -m pip install \
  --disable-pip-version-check \
  --requirement "${ROOT_DIR}/requirements-dev.txt"
"${ROOT_DIR}/.venv/bin/python" -m pip install \
  --disable-pip-version-check \
  --no-build-isolation \
  --no-deps \
  --editable "${ROOT_DIR}"

echo "Setup complete. Run: bash \"${ROOT_DIR}/run.sh\" \"${ROOT_DIR}/examples/nodes.json\" summary"
