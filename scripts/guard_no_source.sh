#!/usr/bin/env bash
# Fails if anything that is not runner plumbing has been committed here.
#
# This repository exists so that public GitHub runners can build and publish
# RecRoll without the application source being public. That only holds as long
# as the application source never lands in it. A file added here is public
# immediately and permanently - a later deletion does not un-publish it, since
# it stays in the git history and in every fork and clone.
#
# So the rule is enforced mechanically rather than by care: an allowlist of
# directories, plus a denylist of things that are unmistakably application or
# packaging code. Run it locally before you commit; CI runs it on every push
# and pull request.

set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Paths that may exist here. Everything else is a finding.
ALLOWED_PREFIXES=(
    ".github/"
    "docs/"
    "scripts/"
    ".gitignore"
    ".gitattributes"
    ".editorconfig"
    "README.md"
    "AGENTS.md"
)

# Extensions and names that are application or packaging code and must live in
# the private repository instead.
DENIED_PATTERNS=(
    '\.(c|cc|cpp|cxx|C)$'
    '\.(h|hh|hpp|hxx|inl|ipp)$'
    '\.(m|mm|swift|rs|java|cs|kt)$'
    '(^|/)CMakeLists\.txt$'
    '\.cmake$'
    '\.(iss|wxs|wxi|wxl)$'
    '\.(vcxproj|sln|xcodeproj|jucer)$'
    '(^|/)(Source|Resources|installer|libs|Assets)/'
    '\.(p12|pfx|pem|cer|key|jks)$'
)

FAILED=0
note() { printf '  %s\n' "$*"; }

echo "Checking that this repository contains only runner plumbing..."

FILES="$(git ls-files)"

# --- 1. Everything must sit under an allowed prefix -------------------------
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
    echo
    echo "FAIL: files outside the allowed layout:"
    for file in "${UNEXPECTED[@]}"; do note "${file}"; done
    echo
    echo "  Only .github/, docs/ and scripts/ (plus the top-level dotfiles and"
    echo "  README.md) belong here. Anything else belongs in AA-EION/RecRoll."
fi

# --- 2. Nothing may look like application or packaging code -----------------
for pattern in "${DENIED_PATTERNS[@]}"; do
    HITS="$(printf '%s\n' "${FILES}" | grep -E "${pattern}" || true)"
    if [ -n "${HITS}" ]; then
        FAILED=1
        echo
        echo "FAIL: files matching /${pattern}/ - this is application or packaging code:"
        printf '%s\n' "${HITS}" | while IFS= read -r hit; do note "${hit}"; done
    fi
done

# --- 3. No vendored checkout of the private repository ----------------------
if [ -e "src" ] || [ -e "RecRoll" ]; then
    FAILED=1
    echo
    echo "FAIL: a checkout directory (src/ or RecRoll/) is present in the tree."
    echo "  The private source is cloned at build time and deleted afterwards;"
    echo "  it must never be committed. Check .gitignore."
fi

echo
if [ "${FAILED}" -eq 0 ]; then
    echo "PASS: $(printf '%s\n' "${FILES}" | grep -c .) tracked file(s), all runner plumbing."
    exit 0
fi

echo "This repository is public. If application code was committed, deleting it"
echo "is not enough: rotate anything sensitive and rewrite the history."
exit 1
