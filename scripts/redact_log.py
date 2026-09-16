#!/usr/bin/env python3
import re
import sys

SAFE_PREFIXES = (
    "[sign]", "[aax]", "[*]", "[!]", "[x]", "[OK]", "===", "---",
    "##[", "::notice", "::warning", "::error", "::group", "::endgroup",
    "Staged ", "Found AAX", "AAX ", "Using ", "Running ", "Installing ",
    "wrote ", "  wrote ", "RecRoll ", "  ", "Note: ",
)

SAFE_PATTERNS = (
    re.compile(r"^\s*$"),
    re.compile(r"^\s*\d+>?\s*$"),
    re.compile(r"^--\s"),
    re.compile(r"^\s*Build (succeeded|FAILED)\.?\s*$"),
    re.compile(r"^\s*Time Elapsed\b"),
    re.compile(r"^\s*\d+ (Warning|Error)\(s\)\s*$"),
    re.compile(r"^\s*(Copyright|Microsoft \(R\)|Apple clang|clang version|cmake version)"),
    re.compile(r"^Total time:"),
    re.compile(r"^\s*(PASSED|FAILED|OK|All tests passed)\b", re.IGNORECASE),
)

MSVC_DIAG = re.compile(
    r"^(?P<path>[^()]+?\.(?:c|cc|cpp|cxx|h|hpp|hxx|inl|m|mm))"
    r"\((?P<line>\d+)(?:,\d+)?\)\s*:\s*"
    r"(?P<sev>fatal error|error|warning)\s+(?P<code>[A-Z]+\d+)",
    re.IGNORECASE,
)

CLANG_DIAG = re.compile(
    r"^(?P<path>[^:]+?\.(?:c|cc|cpp|cxx|h|hpp|hxx|inl|m|mm)):"
    r"(?P<line>\d+):(?:(?P<col>\d+):)?\s*"
    r"(?P<sev>fatal error|error|warning|note)\s*:",
    re.IGNORECASE,
)

LINK_DIAG = re.compile(
    r"^(?P<path>[^()]+?\.(?:obj|o|lib|a|dll|exe))\s*:\s*"
    r"(?P<sev>fatal error|error|warning)\s+(?P<code>[A-Z]+\d+)",
    re.IGNORECASE,
)

CREDENTIAL_SHAPED = (
    re.compile(r"-----BEGIN [A-Z ]*(PRIVATE KEY|CERTIFICATE)"),
    re.compile(r"(x-access-token|oauth2|[A-Za-z0-9_-]+):[^@/\s]{8,}@"),
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(r"[A-Za-z0-9+/]{120,}={0,2}"),
    re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key|keypassword)\b\s*[:=]\s*\S"),
    re.compile(r"(?i)(^|\s)(-p|/p|-P|--password|--keypassword|--pass|--keyfile-password)\s+\S"),
    re.compile(r"(?i)-D[A-Za-z0-9_]*(SECRET|PRIVATE_KEY|TOKEN|PASSWORD|PASSWD)[A-Za-z0-9_]*="),
    re.compile(r"(?i)\b([A-Za-z0-9_]+_(SECRET|PRIVATE_KEY|TOKEN|PASSWORD|PASSWD))\b"),
    re.compile(r"\b[0-9a-fA-F]{64}\b"),
)

SOURCE_ECHO = re.compile(r"^\s*(\d+\s*\|)|^\s*[\^~]+\s*$|^\s*\|\s*[\^~]")

NINJA_PROGRESS = re.compile(r"^\s*\[\s*(?P<done>\d+)/(?P<total>\d+)\s*\]\s*(?P<verb>[A-Za-z ]+?)\s+(?P<rest>\S.*)$")

def basename(path):
    return re.split(r"[\\/]", path.strip())[-1]

def redact(line):
    stripped = line.rstrip("\r\n")

    for pattern in CREDENTIAL_SHAPED:
        if pattern.search(stripped):
            return "[line withheld: looked like credential material]"

    if SOURCE_ECHO.match(stripped):
        return None

    match = NINJA_PROGRESS.match(stripped)
    if match:
        groups = match.groupdict()
        tokens = groups["rest"].split()
        path = tokens[-1] if tokens else ""
        for index, token in enumerate(tokens):
            if "/" in token or "\\" in token:
                path = " ".join(tokens[index:])
                break
        return "[%s/%s] %s %s" % (
            groups["done"], groups["total"], groups["verb"].strip(),
            basename(path.strip('"')),
        )

    match = MSVC_DIAG.match(stripped) or LINK_DIAG.match(stripped)
    if match:
        groups = match.groupdict()
        return "%s(%s): %s %s  [message withheld]" % (
            basename(groups["path"]), groups.get("line", "?"),
            groups["sev"].lower(), groups.get("code", ""),
        )

    match = CLANG_DIAG.match(stripped)
    if match:
        groups = match.groupdict()
        return "%s:%s: %s  [message withheld]" % (
            basename(groups["path"]), groups["line"], groups["sev"].lower(),
        )

    if stripped.startswith(SAFE_PREFIXES):
        return stripped
    for pattern in SAFE_PATTERNS:
        if pattern.match(stripped):
            return stripped

    return None

def main():
    if len(sys.argv) > 1:
        stream = open(sys.argv[1], encoding="utf-8", errors="replace")
    else:
        stream = sys.stdin

    withheld = 0
    try:
        for line in iter(stream.readline, ""):
            out = redact(line)
            if out is None:
                withheld += 1
            else:
                print(out, flush=True)
    finally:
        if stream is not sys.stdin:
            stream.close()

    print()
    print("--- %d line(s) withheld by scripts/redact_log.py ---" % withheld)
    print("Log filtered for public release.")

if __name__ == "__main__":
    main()
