#!/usr/bin/env bash
set -euo pipefail

DIR="${1:?directory to verify}"
# --adding: the folder holds only installers being added to a published
# release, plus the regenerated release-manifest.json.
ADDING="${2:-}"

ALLOWED='^RecRoll-.*-Installer\.exe$|\.dmg$|^release-manifest\.json$'

FAILED=0
COUNT=0

while IFS= read -r file; do
    [ -n "${file}" ] || continue
    name="$(basename "${file}")"
    COUNT=$((COUNT + 1))
    if printf '%s' "${name}" | grep -qE "${ALLOWED}"; then
        printf '  OK       %-52s %s\n' "${name}" "$(du -h "${file}" | cut -f1)"
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
    echo "Refusing to publish unpermitted files." >&2
    exit 1
fi

# Every release carries release-manifest.json, and it must describe exactly
# these installers: the store and the Launcher read only that file.
if [ ! -f "${DIR}/release-manifest.json" ]; then
    echo "release-manifest.json is missing. Generate it in the product repository:" >&2
    echo "  python3 tools/make_release_manifest.py --dist <this folder>" >&2
    exit 1
fi
python3 "$(dirname "${BASH_SOURCE[0]}")/verify_release_manifest.py" --dir "${DIR}" --product recroll ${ADDING:+--adding}

echo "PASS: ${COUNT} file(s) verified."
