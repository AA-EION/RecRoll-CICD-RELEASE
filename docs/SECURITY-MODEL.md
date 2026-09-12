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

`KUROKO_SOURCE_TOKEN`, which clones the licensing client into `kuroko/`, is
scoped and handled identically. Both checkouts are deleted before any artefact
is uploaded, and the cleanup step *asserts* they are gone rather than assuming
it: the upload step takes a path, and a path is one typo away from sweeping the
workspace into an artefact on a public repository — which a later deletion does
not undo.

### 3b. Licensing material leaks into a public log

`RECROLL_GATE_SECRET` is the constant woven into the license gate's keyed check
field. Someone patching a binary cannot recompute that field without it, which
is the whole reason patching the gate does not pay off — so it is the one
licensing input that must never appear here.

Nothing prints it on purpose. The build scripts echo the licensing *endpoint*,
because a release built against the wrong server is worth catching by eye, and
nothing else. The exposure that remains is a tool echoing its own command line,
which CMake does when a configure step fails — precisely when these logs get
read closely. `scripts/redact_log.py` therefore withholds any line carrying a
`-D…SECRET…=`-shaped definition, the names of the licensing secrets, or a
64-character hex run (the shape of a public key, and equally of a private seed).
`guard.yml` asserts all of that on every push, and asserts that the endpoint
line still survives — a redactor that hides everything is safe, useless, and
switched off by the next person who needs it.

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

There is **no input that disables redaction**. An earlier revision had one. It
was removed on review: anyone who needs the full text can run the same commit
through `AA-EION/RecRoll`'s own workflow, whose logs are private and complete,
so the switch had no use its safe alternative did not cover — which left it as
nothing but a way to publish source into a public log in a hurry.

As a second line, the redactor also drops any line carrying credential-shaped
material — a PEM header, a long base64 run, a `token:`-style URL — regardless of
which rule would otherwise have passed it. GitHub masks exact secret values in
logs on its own, but masking only matches the value as stored: a secret that has
been decoded, re-encoded or split across lines is no longer an exact match, and
this catches that case.

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

---

## Residual risks

These are known, accepted, or need a decision that is not this repository's to
make. They are listed so nobody has to rediscover them.

### Signing secrets reach a job that compiles third-party code

Both repositories' build jobs hold the Developer ID certificate, the PACE
password and the Authenticode PFX while CMake fetches and compiles JUCE and
`clap-juce-extensions`. Anything that executes during that build can read the
job's environment.

`clap-juce-extensions` is fetched at **`GIT_TAG main`** in the private
repository's `CMakeLists.txt` — a moving branch, not a pinned commit. A
compromise of that repository, or of any commit pushed to its default branch,
runs in a job holding code-signing keys. **Pin it to a tag or commit SHA.**

The stronger fix for both: move the signing secrets into a GitHub
**Environment** with a required reviewer, and let ordinary branch and
pull-request builds run unsigned. Signing then only happens on a run a human
approved, and a malicious pull request cannot reach the keys.

### Passwords appear on command lines

`signtool /p`, `wraptool -p` and `wraptool --keypassword` all take the password
as an argument, and neither tool offers an environment-variable or stdin
alternative. Any process on the same machine can read it out of the process
list while signing runs.

On GitHub-hosted runners this is not a practical concern: the VM is
single-tenant and destroyed after the job. **On a self-hosted runner it is** —
do not run the signing jobs on a machine that is shared with anything else, and
do not give that machine other tenants.

The redactor withholds any line carrying such a flag, so this does not reach the
logs; the exposure is to the machine, not to the log.

### A fork's pull request runs its own copy of the guard

For `pull_request`, GitHub runs the workflow file from the pull request, not
from the base branch. A fork can therefore weaken `guard.yml` in its own PR and
watch it pass. That proves nothing about the change — the guard is a check on
*merged* content, and what actually protects the default branch is branch
protection plus a maintainer reading the diff.

**Enable branch protection on the default branch** with a required review and
required status checks. Without it, a maintainer in a hurry can push source
straight past every check in this repository.

### The redacted log still names files

`RingBuffer.cpp(214)` says a file by that name exists. That is structure, not
content. Removing it would make a failed public build undiagnosable, and an
undiagnosable check is one that gets turned off — see the note above about what
happened to the redaction override.

### Debug information is stripped, not merely unrequested

MSVC writes the linker's side outputs next to the module it produces, which for
a JUCE plug-in is *inside* the `.vst3` bundle — and that bundle is copied whole
into the MSI. A `.pdb` is not source, but it carries every symbol name and the
full source path of every file on the build machine.

`ci/stage_windows.ps1` deletes `.pdb`, `.ilk`, `.exp`, `.lib`, `.map`, `.obj`
and friends from the staging tree, then **asserts** that none survived and fails
the build if any did. `installer/macos/build_installer.sh` does the same for
`.dSYM` and object files. The assertion is the point: the deletion could be
right today and wrong after the next JUCE upgrade changes a bundle layout.

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
