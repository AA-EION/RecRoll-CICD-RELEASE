#!/usr/bin/env bash
# Copies the two public deliverables out of a private build, and nothing else.
#
#   collect_public_artifacts.sh <build-dist-dir> <out-dir> <windows|macos>
#
# The private build produces far more than the public release publishes:
# portable archives, raw AAX bundles, the .exe installer, component packages.
# Those are the private repository's business. This is an allowlist, not a
# filter - a new artefact type appearing in the build is excluded by default
# rather than published by accident.
#
# Public deliverables:
#   windows  RecRoll-Windows-Universal-Installer.exe  (the headline download:
#            one file, both architectures, picks at install time)
#            RecRoll-<version>-Windows-<arch>.msi     (for scripted/IT deploys)
#   macos    RecRoll-macOS-Universal.dmg   (the branded image, PKG inside)
# plus the signing manifest for that platform, so a user can tell what they got.
#
# The .exe pattern is deliberately narrow rather than "*.exe": this is the
# extension most easily confused with something unintended, and the build tree
# contains standalone application binaries that are not installers.

set -euo pipefail

SRC="${1:?source dist directory}"
OUT="${2:?output directory}"
PLATFORM="${3:?windows|macos}"

case "${PLATFORM}" in
    windows) PATTERNS=("RecRoll-*-Installer.exe" "*.msi") ;;
    macos)   PATTERNS=("*.dmg") ;;
    *) echo "Unknown platform: ${PLATFORM}" >&2; exit 2 ;;
esac

mkdir -p "${OUT}"

FOUND=0
for pattern in "${PATTERNS[@]}"; do
    while IFS= read -r file; do
        [ -n "${file}" ] || continue
        echo "  publishing $(basename "${file}")"
        cp "${file}" "${OUT}/"
        FOUND=$((FOUND + 1))
    done < <(find "${SRC}" -maxdepth 1 -type f -name "${pattern}" | sort)
done

if [ "${FOUND}" -eq 0 ]; then
    echo "No public deliverable found in ${SRC} for platform ${PLATFORM}." >&2
    echo "Expected one of: ${PATTERNS[*]}" >&2
    ls -la "${SRC}" >&2 || true
    exit 1
fi

# The manifest says what was actually signed; shipping the binary without it
# leaves a user guessing whether Gatekeeper will complain.
if [ -f "${SRC}/SIGNING-${PLATFORM}.txt" ]; then
    cp "${SRC}/SIGNING-${PLATFORM}.txt" "${OUT}/"
    echo "  publishing SIGNING-${PLATFORM}.txt"
fi

echo "Collected ${FOUND} deliverable(s) into ${OUT}."
