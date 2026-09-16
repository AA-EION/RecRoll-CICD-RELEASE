#!/usr/bin/env bash
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
    echo "No deliverable found in ${SRC} for platform ${PLATFORM}." >&2
    exit 1
fi

if [ -f "${SRC}/SIGNING-${PLATFORM}.txt" ]; then
    cp "${SRC}/SIGNING-${PLATFORM}.txt" "${OUT}/"
    echo "  publishing SIGNING-${PLATFORM}.txt"
fi

echo "Collected ${FOUND} deliverable(s)."
