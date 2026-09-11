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

Set RECROLL_LOG_MODE=verbose to pass everything through. That deliberately
publishes source excerpts on failure, so it is never the default and belongs
only in a debugging run the maintainer has decided to accept.
"""

import os
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

    if SOURCE_ECHO.match(stripped):
        return None

    match = NINJA_PROGRESS.match(stripped)
    if match:
        groups = match.groupdict()
        return "[%s/%s] %s %s" % (
            groups["done"], groups["total"], groups["verb"].strip(),
            basename(groups["rest"].split()[-1]),
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
    verbose = os.environ.get("RECROLL_LOG_MODE", "").lower() == "verbose"

    if len(sys.argv) > 1:
        stream = open(sys.argv[1], encoding="utf-8", errors="replace")
    else:
        stream = sys.stdin

    withheld = 0
    try:
        for line in stream:
            if verbose:
                sys.stdout.write(line)
                continue
            out = redact(line)
            if out is None:
                withheld += 1
            else:
                print(out, flush=True)
    finally:
        if stream is not sys.stdin:
            stream.close()

    if not verbose:
        print()
        print("--- %d line(s) withheld by scripts/redact_log.py ---" % withheld)
        print("This repository is public; raw build output can quote private source.")
        print("The full log is in the corresponding run in AA-EION/RecRoll.")


if __name__ == "__main__":
    main()
