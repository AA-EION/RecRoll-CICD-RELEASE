#!/usr/bin/env bash
# Check a folder before uploading it to a GitHub release: it may hold only
# this product's installers, named by the convention below, and the
# release-manifest.json that describes exactly them.
#
#   ./scripts/verify_public_payload.sh <folder>            # a new release
#   ./scripts/verify_public_payload.sh <folder> --adding   # adding installers to a published release
#
# Installer names (the same in every EION Studios release repository):
#   <Product>-<version>-Windows-<Universal|x64|arm64>-Installer.exe
#   <Product>-<version>-macOS-Universal.dmg
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/product.env"

DIR="${1:?folder to verify}"
ADDING="${2:-}"

VER='[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?'
ALLOWED="^${FILE_PREFIX}-${VER}-Windows-(Universal|x64|arm64)-Installer\.exe$|^${FILE_PREFIX}-${VER}-macOS-Universal\.dmg$|^release-manifest\.json$"

FAILED=0
COUNT=0

while IFS= read -r file; do
    [ -n "${file}" ] || continue
    name="$(basename "${file}")"
    COUNT=$((COUNT + 1))
    if printf '%s' "${name}" | grep -qE "${ALLOWED}"; then
        printf '  OK       %-56s %s\n' "${name}" "$(du -h "${file}" | cut -f1)"
    else
        printf '  REFUSED  %s\n' "${name}"
        FAILED=1
    fi
done < <(find "${DIR}" -type f | sort)

if [ "${COUNT}" -eq 0 ]; then
    echo "Nothing to publish." >&2
    exit 1
fi

if [ "${FAILED}" -ne 0 ]; then
    echo "Refusing to publish unpermitted files. Installers must be named" >&2
    echo "  ${FILE_PREFIX}-<version>-Windows-<Universal|x64|arm64>-Installer.exe" >&2
    echo "  ${FILE_PREFIX}-<version>-macOS-Universal.dmg" >&2
    exit 1
fi

if [ ! -f "${DIR}/release-manifest.json" ]; then
    echo "release-manifest.json is missing. Generate it in the product repository:" >&2
    echo "  python3 tools/make_release_manifest.py --dist <this folder>" >&2
    exit 1
fi
python3 "$(dirname "${BASH_SOURCE[0]}")/verify_release_manifest.py" --dir "${DIR}" --product "${PRODUCT_ID}" ${ADDING:+--adding}

echo "PASS: ${COUNT} file(s) verified."
