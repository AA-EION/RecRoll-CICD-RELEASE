#!/usr/bin/env bash
set -euo pipefail

DIR="${1:?directory to verify}"

ALLOWED='^RecRoll-.*-Installer\.exe$|\.(msi|dmg)$|^SIGNING-(windows|macos)\.txt$'

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

echo "PASS: ${COUNT} file(s) verified."
