#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ALLOWED_PREFIXES=(
    ".github/"
    "docs/"
    "scripts/"
    ".gitignore"
    ".gitattributes"
    ".editorconfig"
    "README.md"
    "VERSION"
    "AGENTS.md"
)

DENIED_PATTERNS=(
    '\.(c|cc|cpp|cxx|C)$'
    '\.(h|hh|hpp|hxx|inl|ipp)$'
    '\.(m|mm|swift|rs|java|cs|kt)$'
    '(^|/)CMakeLists\.txt$'
    '\.cmake$'
    '\.(iss|wxs|wxi|wxl)$'
    '\.(vcxproj|sln|xcodeproj|jucer)$'
    '(^|/)(Source|Resources|installer|libs|Assets|modules)/'
    '\.(p12|pfx|pem|cer|key|jks)$'
)

FAILED=0
note() { printf '  %s\n' "$*"; }

echo "Verifying runner layout..."

FILES="$(git ls-files)"

UNEXPECTED=()
while IFS= read -r file; do
    [ -n "${file}" ] || continue
    ok=0
    for prefix in "${ALLOWED_PREFIXES[@]}"; do
        case "${file}" in
            "${prefix}"*) ok=1; break ;;
        esac
    done
    [ "${ok}" -eq 1 ] || UNEXPECTED+=("${file}")
done <<< "${FILES}"

if [ ${#UNEXPECTED[@]} -gt 0 ]; then
    FAILED=1
    echo "FAIL: Unexpected files outside runner layout:"
    for file in "${UNEXPECTED[@]}"; do note "${file}"; done
fi

for pattern in "${DENIED_PATTERNS[@]}"; do
    HITS="$(printf '%s\n' "${FILES}" | grep -E "${pattern}" || true)"
    if [ -n "${HITS}" ]; then
        FAILED=1
        echo "FAIL: Files matching restricted patterns:"
        printf '%s\n' "${HITS}" | while IFS= read -r hit; do note "${hit}"; done
    fi
done

for checkout in src RecRoll kuroko Kuroko; do
    if [ -e "${checkout}" ]; then
        FAILED=1
        echo "FAIL: Local checkout directory (${checkout}/) found."
    fi
done

if [ "${FAILED}" -eq 0 ]; then
    echo "PASS: $(printf '%s\n' "${FILES}" | grep -c .) tracked file(s)."
    exit 0
fi

exit 1
