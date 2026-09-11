#!/usr/bin/env bash
# Last gate before anything is attached to a public release.
#
#   verify_public_payload.sh <dir>
#
# collect_public_artifacts.sh already allowlists what gets copied, but it runs
# on the build runners, one per platform. This runs once, in the publish job,
# over the exact set of files about to be uploaded - so a mistake in a build
# job, a stray download, or a future edit to the workflow still cannot put an
# unintended file on a public release.

set -euo pipefail

DIR="${1:?directory to verify}"

ALLOWED='\.(msi|dmg)$|^SIGNING-(windows|macos)\.txt$'

echo "Verifying the public release payload in ${DIR}..."
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
    echo "Nothing to publish - the build produced no public deliverable." >&2
    exit 1
fi

if [ "${FAILED}" -ne 0 ]; then
    echo >&2
    echo "Refusing to publish: the payload contains files that are not a public" >&2
    echo "deliverable. Only .msi, .dmg and the signing manifests may be released" >&2
    echo "from this repository." >&2
    exit 1
fi

echo "PASS: ${COUNT} file(s), all permitted."
