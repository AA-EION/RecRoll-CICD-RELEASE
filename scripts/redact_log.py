#!/usr/bin/env python3
"""
Filters build output so a public runner can report on a private build without
republishing it.

This repository is public. Its job logs are public. The source it compiles is
not, and a compiler is happy to quote the line it choked on straight into the
log - so raw build output cannot be echoed here.

Reads the build's combined output on stdin (or from a file argument) and writes
a redacted version to stdout, line by line, so failures are still diagnosable:

  * progress and status lines from our own scripts pass through untouched
  * a compiler or linker diagnostic is reduced to file name, line number,
    severity and error code - never the message, which quotes identifiers, and
    never the source excerpt the compiler prints under it
  * everything else is withheld and counted

There is deliberately no switch to turn this off. When the full text is needed,
the same commit is run through AA-EION/RecRoll's own workflow, whose logs are
private and complete.
"""

import re
import sys

# Lines our own scripts emit. They are written to be safe to publish.
SAFE_PREFIXES = (
    "[sign]", "[aax]", "[*]", "[!]", "[x]", "[OK]", "===", "---",
    "##[", "::notice", "::warning", "::error", "::group", "::endgroup",
    "Staged ", "Found AAX", "AAX ", "Using ", "Running ", "Installing ",
    "wrote ", "  wrote ", "RecRoll ", "  ", "Note: ",
)

SAFE_PATTERNS = (
    re.compile(r"^\s*$"),
    re.compile(r"^\s*\d+>?\s*$"),
    re.compile(r"^--\s"),                            # cmake status
    re.compile(r"^\s*Build (succeeded|FAILED)\.?\s*$"),
    re.compile(r"^\s*Time Elapsed\b"),
    re.compile(r"^\s*\d+ (Warning|Error)\(s\)\s*$"),
    re.compile(r"^\s*(Copyright|Microsoft \(R\)|Apple clang|clang version|cmake version)"),
    re.compile(r"^Total time:"),
    re.compile(r"^\s*(PASSED|FAILED|OK|All tests passed)\b", re.IGNORECASE),
)

# MSVC:  C:\path\file.cpp(123,4): error C2065: 'x': undeclared identifier [p.vcxproj]
MSVC_DIAG = re.compile(
    r"^(?P<path>[^()]+?\.(?:c|cc|cpp|cxx|h|hpp|hxx|inl|m|mm))"
    r"\((?P<line>\d+)(?:,\d+)?\)\s*:\s*"
    r"(?P<sev>fatal error|error|warning)\s+(?P<code>[A-Z]+\d+)",
    re.IGNORECASE,
)

# Clang/GCC:  /path/file.cpp:12:3: error: use of undeclared identifier 'x'
CLANG_DIAG = re.compile(
    r"^(?P<path>[^:]+?\.(?:c|cc|cpp|cxx|h|hpp|hxx|inl|m|mm)):"
    r"(?P<line>\d+):(?:(?P<col>\d+):)?\s*"
    r"(?P<sev>fatal error|error|warning|note)\s*:",
    re.IGNORECASE,
)

# Linker errors name symbols, which are mangled source identifiers.
LINK_DIAG = re.compile(
    r"^(?P<path>[^()]+?\.(?:obj|o|lib|a|dll|exe))\s*:\s*"
    r"(?P<sev>fatal error|error|warning)\s+(?P<code>[A-Z]+\d+)",
    re.IGNORECASE,
)

# Credential-shaped material, checked before any rule that would let a line
# through. GitHub masks exact secret values in logs by itself, but masking only
# matches the value as stored: a secret that has been decoded, re-encoded, or
# split across lines is no longer an exact match and reaches the log intact.
# Nothing in this pipeline prints a credential on purpose; this is for the tool
# that does it by accident.
CREDENTIAL_SHAPED = (
    re.compile(r"-----BEGIN [A-Z ]*(PRIVATE KEY|CERTIFICATE)"),
    re.compile(r"(x-access-token|oauth2|[A-Za-z0-9_-]+):[^@/\s]{8,}@"),  # credentials in a URL
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(r"[A-Za-z0-9+/]{120,}={0,2}"),   # a long base64 run: a decoded cert or key
    re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key|keypassword)\b\s*[:=]\s*\S"),
    # Password-carrying command-line flags. signtool and wraptool both take the
    # password as an argument, so any tool that echoes its own command line -
    # or a shell that traces it - puts one in the log.
    re.compile(r"(?i)(^|\s)(-p|/p|-P|--password|--keypassword|--pass|--keyfile-password)\s+\S"),
    # Secret-carrying CMake definitions. The build scripts never print these,
    # but CMake echoes the whole command line when a configure step fails, and
    # a failing configure is exactly when somebody reads these logs closely.
    # RECROLL_GATE_SECRET is the one that matters: it is what a patcher would
    # need to forge the license gate's keyed check field.
    re.compile(r"(?i)-D[A-Za-z0-9_]*(SECRET|PRIVATE_KEY|TOKEN|PASSWORD|PASSWD)[A-Za-z0-9_]*="),
    re.compile(r"(?i)\b(GATE_SECRET|KUROKO_PRIVATE_KEY|KUROKO_SOURCE_TOKEN|RECROLL_SOURCE_TOKEN)\b"),
    # A 64-character hex run. The Ed25519 *public* key is this shape and is
    # harmless, but so is a 32-byte private seed and so is any raw key material
    # rendered as hex - and nothing in this pipeline needs to print any of them
    # for a log to be useful. Withholding costs nothing here.
    re.compile(r"\b[0-9a-fA-F]{64}\b"),
)

# Source excerpts clang prints beneath a diagnostic, and their caret line.
SOURCE_ECHO = re.compile(r"^\s*(\d+\s*\|)|^\s*[\^~]+\s*$|^\s*\|\s*[\^~]")

# Ninja progress. Worth keeping - it is how you tell a hang from a slow link -
# but the object path it carries maps out the private source tree, so only the
# counter and the file name survive.
NINJA_PROGRESS = re.compile(r"^\s*\[\s*(?P<done>\d+)/(?P<total>\d+)\s*\]\s*(?P<verb>[A-Za-z ]+?)\s+(?P<rest>\S.*)$")


def basename(path):
    return re.split(r"[\\/]", path.strip())[-1]


def redact(line):
    """Returns the line to print, or None to withhold it."""
    stripped = line.rstrip("\r\n")

    # First, and ahead of every pass-through rule: nothing credential-shaped
    # leaves this function, whatever else the line looks like.
    for pattern in CREDENTIAL_SHAPED:
        if pattern.search(stripped):
            return "[line withheld: looked like credential material]"

    if SOURCE_ECHO.match(stripped):
        return None

    match = NINJA_PROGRESS.match(stripped)
    if match:
        groups = match.groupdict()
        # The path starts at the first token carrying a separator, and may
        # contain spaces from here on - "RecRoll Instrument.vst3" does. Taking
        # the last whitespace-delimited token instead reported it as
        # `Linking Instrument"`.
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
        # readline, not `for line in stream`: iterating a pipe fills an
        # internal read-ahead buffer, and a long build would then show nothing
        # for minutes at a time.
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
    print("This repository is public; raw build output can quote private source.")
    print("The full log is in the corresponding run in AA-EION/RecRoll.")


if __name__ == "__main__":
    main()
