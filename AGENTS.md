# Notes for AI agents working in this repository

Read this before changing anything here.

## What this repository is

Public release runners for RecRoll. It contains workflows, guard scripts and
documentation. **It contains no application code and must never contain any.**

The plugin source, build system, installers and signing scripts live in the
private repository `AA-EION/RecRoll`. This repository clones that one at build
time, runs *its* scripts, publishes an MSI and a DMG, and deletes the clone.

## The one rule

**Never add application or packaging code here.**

That includes `.cpp`, `.h`, `.mm`, `CMakeLists.txt`, `.cmake`, `.iss`, `.wxs`,
project files, `Source/`, `Resources/`, `installer/`, `libs/`, and any
certificate or key.

This is not style guidance. This repository is public; a commit is public the
instant it is pushed, and deleting it afterwards does not un-publish it — it
stays in the history, in forks, in clones and in GitHub's event feed.

`scripts/guard_no_source.sh` enforces this on every push and pull request. Run
it before you commit:

```bash
./scripts/guard_no_source.sh
```

If a task seems to require adding source here, the task is misread. The change
belongs in `AA-EION/RecRoll`. Say so rather than working around the guard.

## Where a change actually belongs

| You want to change | Repository | Path |
|---|---|---|
| How the plugin builds | `AA-EION/RecRoll` | `ci/build_windows.ps1`, `ci/build_macos.sh` |
| What the installers contain | `AA-EION/RecRoll` | `installer/` |
| How things are signed | `AA-EION/RecRoll` | `installer/signing/` |
| Installer artwork | `AA-EION/RecRoll` | `tools/make_installer_art.py`, `Resources/installer/` |
| Which artefacts become public | **here** | `scripts/collect_public_artifacts.sh` |
| What may be attached to a release | **here** | `scripts/verify_public_payload.sh` |
| What build logs may say | **here** | `scripts/redact_log.py` |
| How a public release is triggered | **here** | `.github/workflows/release.yml` |

The build logic is intentionally in the private repository, called by both
repositories' workflows. Do not copy a build step into this repository to "make
it self-contained" — that is how the two releases start producing different
binaries, and it puts packaging code somewhere it must not be.

## Things that will bite you

**Do not add a `pull_request` or `push` trigger to `release.yml`.** That
workflow holds a token for a private repository. A fork's pull request runs the
fork's workflow code; giving it secrets hands them over. `release.yml` starts
only from `workflow_dispatch` and `repository_dispatch`, both of which require
write access here.

**Do not add caching to any workflow here.** Cache entries in a public
repository are reachable from forks' workflow runs, and a C++ build cache
contains object files and preprocessed headers — which contain source.

**Do not remove the redaction from the build steps.** Compilers quote the source
line they failed on. `guard.yml` self-tests the redactor with invented
identifiers and fails if any survive; if that test is in your way, it is telling
you something true.

**Do not widen the allowlists** in `collect_public_artifacts.sh` or
`verify_public_payload.sh` to make a build pass. If a deliverable is missing,
the packaging step failed — fix that in the private repository.

**Do not put the private repository's name or token anywhere but the workflow
env.** The checkout uses `persist-credentials: false` for a reason.

## Testing a change

Everything except an actual build can be checked locally:

```bash
./scripts/guard_no_source.sh              # the layout rule
python3 -m py_compile scripts/*.py        # the redactor parses
for f in scripts/*.sh; do bash -n "$f"; done

# The redactor, on a sample that looks like a real failure:
printf '%s\n' \
  '/src/Source/dsp/Ring.cpp:88:12: error: no member named '"'"'kSecret'"'"'' \
  '   88 |     const auto g = kSecret * shape(x);' \
  '      |                    ^~~~~~~' \
  | python3 scripts/redact_log.py
# kSecret must not appear in the output. Ring.cpp and 88 must.
```

For a real build, use a **dry run**: run the `Build and publish RecRoll`
workflow with `release_tag` empty. It builds end to end and uploads the
deliverables as workflow artefacts without publishing a release.

## Before you finish

- `./scripts/guard_no_source.sh` passes
- No new workflow trigger that a fork can reach
- No new path in an artefact allowlist that you cannot justify
- `docs/SECURITY-MODEL.md` still describes what the code does — if you changed a
  protection, the document is part of the change
