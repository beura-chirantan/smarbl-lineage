#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANTLR_VERSION="4.13.2"
ANTLR_SHA256="eae2dfa119a64327444672aff63e9ec35a20180dc5b8090b7a6ab85125df4d76"
JAR_DIR="${ROOT_DIR}/.antlr"
JAR_PATH="${JAR_DIR}/antlr-${ANTLR_VERSION}-complete.jar"

mkdir -p "${JAR_DIR}" "${ROOT_DIR}/src/lineage/generated"

if [[ ! -f "${JAR_PATH}" ]]; then
  curl --fail --location --silent --show-error \
    --output "${JAR_PATH}" \
    "https://www.antlr.org/download/antlr-${ANTLR_VERSION}-complete.jar"
fi

if command -v shasum >/dev/null 2>&1; then
  ACTUAL_SHA256="$(shasum -a 256 "${JAR_PATH}" | awk '{print $1}')"
elif command -v sha256sum >/dev/null 2>&1; then
  ACTUAL_SHA256="$(sha256sum "${JAR_PATH}" | awk '{print $1}')"
else
  echo "A SHA-256 tool (shasum or sha256sum) is required" >&2
  exit 1
fi
if [[ "${ACTUAL_SHA256}" != "${ANTLR_SHA256}" ]]; then
  echo "ANTLR jar checksum mismatch" >&2
  exit 1
fi

(
  cd "${ROOT_DIR}/grammar"
  java -jar "${JAR_PATH}" \
    -Dlanguage=Python3 \
    -visitor \
    -no-listener \
    -o "${ROOT_DIR}/src/lineage/generated" \
    Lineage.g4
)

echo "Generated Python parser with ANTLR ${ANTLR_VERSION}."
