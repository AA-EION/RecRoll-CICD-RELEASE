# Security model

This repository is public. It builds private source. Those two facts are in
tension, and everything below is how the tension is resolved.

The goal is narrow and worth stating plainly: **the RecRoll source must not
become readable through this repository.** The compiled product becoming public
is the entire point — that is the release.

---

## The five leak paths, and what closes each

### 1. Someone commits source here

A file pushed to a public repository is public immediately, and deleting it does
not undo that: it remains in the git history, in every fork, in every clone, and
in GitHub's own event feed.

**Closed by** [`scripts/guard_no_source.sh`](../scripts/guard_no_source.sh),
which runs on every push and every pull request. It works two ways at once:

- an **allowlist** of paths — only `.github/`, `docs/`, `scripts/`, and a few
  top-level dotfiles may exist. Anything else fails, including file types nobody
  has thought of yet.
- a **denylist** of patterns — C/C++/Obj-C/Swift/Rust sources, `CMakeLists.txt`,
  `.cmake`, `.iss`, `.wxs`, project files, `Source/` `Resources/` `installer/`
  `libs/` directories, and private-key extensions.

The allowlist is the important half. A denylist alone only catches what was
anticipated.

### 2. A fork runs the workflow and captures the token

Forks are the classic way secrets escape a public repository: a pull request
from a fork runs workflow code the fork's author wrote, and if that workflow
gets secrets, the secrets are theirs.

**Closed by trigger selection.** `release.yml` has **no `pull_request` trigger
and no `push` trigger**. It starts only from `workflow_dispatch` or
`repository_dispatch`, both of which require write access to this repository.
The `guard` job additionally refuses to run when the owner is not `AA-EION`.

`guard.yml` does run on pull requests — deliberately. It holds no secrets and
clones nothing, so it is safe for anyone, and it is the check that keeps this
repository honest.

### 3. The source token leaks from the runner

**Bounded by scope.** `RECROLL_SOURCE_TOKEN` is a fine-grained PAT with
*Contents: read-only* on `AA-EION/RecRoll` and nothing else. It cannot push,
cannot open pull requests, cannot reach other repositories, cannot touch
Actions.

**Bounded by handling.** The checkout uses `persist-credentials: false`, so the
token is not written into `src/.git/config` where a later step or a stray
`git config --list` would expose it. It reaches the runner as a masked secret
and is not passed on the command line of anything.

### 4. Build logs quote the source

This is the one that is easy to miss. Compilers are *helpful*: clang prints the
offending source line under every diagnostic, with a caret. MSVC quotes the
identifier. A single failing build can put a dozen lines of private source into
a public log — and job logs are readable by anyone, indefinitely.

**Closed by** [`scripts/redact_log.py`](../scripts/redact_log.py), which every
build's output is piped through. It:

- passes through status lines our own scripts emit, which are written to be safe
- reduces a compiler or linker diagnostic to **file name, line number, severity
  and error code**, dropping the message — the message quotes identifiers
- drops the source excerpt and caret line clang prints beneath a diagnostic
- reduces ninja progress lines to the counter and the file name, dropping the
  object path that maps out the private source tree
- **withholds everything it does not recognise**, and reports the count

That last point is the design: the redactor is an allowlist, not a blocklist. An
unfamiliar tool printing something unexpected is withheld by default rather than
published by default.

The `guard` workflow self-tests this on every change, using a sample log that
contains invented identifiers, and fails if any of them survive. It also checks
that the file name and line number *do* survive — a redactor that hides
everything is safe and useless, and would quietly be replaced by someone
turning it off.

`verbose_logs` disables redaction. It exists because there are moments when the
maintainer decides the exposure is acceptable. It is off by default, it is
labelled as dangerous in the workflow input, and it should not become a habit.

### 5. Build products carry more than intended

The private build produces a lot: portable archives of every binary, raw AAX
bundles, component packages, the Inno Setup `.exe`, debug output. Only the MSI
and the DMG are meant to be public.

**Closed twice, on purpose:**

- [`scripts/collect_public_artifacts.sh`](../scripts/collect_public_artifacts.sh)
  runs on each build runner and copies **only** `*.msi` (Windows) or `*.dmg`
  (macOS), plus that platform's signing manifest. It is an allowlist: a new
  artefact type appearing in the build is excluded until someone decides
  otherwise.
- [`scripts/verify_public_payload.sh`](../scripts/verify_public_payload.sh) runs
  once in the publish job, over the exact set of files about to be attached to
  the release, and refuses anything that is not a permitted deliverable.

Two gates rather than one because they fail differently: the first depends on a
build job behaving, the second does not. A mistake in a build job, a stray
download, or a future edit to the workflow still cannot put an unintended file
on a public release.

The private checkout is also deleted (`rm -rf src`, with `if: always()`) before
the upload step, so even a mis-scoped upload path has nothing to find.

---

## What is deliberately *not* protected

**File and directory names appear in redacted logs.** `RingBuffer.cpp(214)`
tells you a file called `RingBuffer.cpp` exists. That is structure, not content,
and removing it would make a failed public build undiagnosable — at which point
people turn off the redactor entirely, which is much worse. This is a considered
trade, not an oversight.

**The binaries are public.** They are the product. Anyone can disassemble a
published plugin; that is true of every plugin ever shipped and is not a leak.

**No caching is configured in any workflow here.** A cache entry in a public
repository is reachable from a fork's workflow run, and a C++ build cache holds
object files and preprocessed headers — which contain source. If you are tempted
to add `actions/cache` to shorten a build: don't, unless you have first worked
out exactly what ends up in the cache key's payload.

---

## If something does leak

Assume the worst about timing: GitHub's event feed is scraped continuously, and
"it was only up for four minutes" is not a defence.

1. **Do not just delete the file and push.** That leaves it in the history.
2. Revoke `RECROLL_SOURCE_TOKEN` and every signing secret that was present in
   any run that could have been affected. Revocation first, investigation after.
3. Rewrite the history (`git filter-repo`), force-push, and ask GitHub Support
   to purge the cached views and any forks.
4. If signing material leaked, revoke the certificate with its issuer and with
   Apple or PACE. A leaked code-signing key is worse than leaked source: it lets
   someone else sign something as you.
5. Note what closed the gap, and add a check to `guard.yml` so the same shape of
   mistake fails the build next time.
