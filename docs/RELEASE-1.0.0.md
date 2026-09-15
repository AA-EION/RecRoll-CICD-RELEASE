# Build and verify version 1.0.0

The runner repository's VERSION is 1.0.0. The plugin and installer version comes
from the private source revision selected for the build. Build both platforms
before publishing, and read the signing reports rather than inferring signing
from the workflow inputs.

## First build: artifacts only

1. Open **Actions → Build and publish RecRoll → Run workflow**.
2. Select the reviewed runner branch. During review use `codex/release-1.0.0`;
   after merging the runner PR, use `main`.
3. Set `source_ref` to the full commit SHA of the reviewed plugin source.
4. Leave `kuroko_ref` empty to use that source's `KUROKO_REVISION`, or enter an
   exact reviewed Kuroko SHA to test an override.
5. Leave `release_tag` **empty**, set `platforms=both`, `sign_pace=off`, and
   `sign_binary=off`. Keep `replace_existing=false`.
6. Start the workflow. Wait for **guard, Windows and macOS** to pass. The publish
   job is expected to be skipped because no release tag was supplied.
7. Open the completed run. Download `RecRoll-Windows-Installers` and
   `RecRoll-macOS-DMG` from **Artifacts**. Extract each ZIP before opening an
   installer. Workflow artifacts expire according to retention settings; they
   are not a permanent release download page.

Equivalent GitHub CLI command (replace the placeholder SHA):

```sh
gh workflow run release.yml --repo AA-EION/RecRoll-CICD-RELEASE \
  --ref codex/release-1.0.0 \
  -f source_ref=FULL_REVIEWED_SOURCE_SHA \
  -f kuroko_ref= -f release_tag= -f platforms=both \
  -f sign_pace=off -f sign_binary=off \
  -f replace_existing=false -f prerelease=true
gh run list --repo AA-EION/RecRoll-CICD-RELEASE --workflow release.yml --limit 5
gh run view RUN_ID --repo AA-EION/RecRoll-CICD-RELEASE
gh run download RUN_ID --repo AA-EION/RecRoll-CICD-RELEASE --dir ./recroll-artifacts
```

The workflow must exist on the default branch for manual dispatch to be
available; `--ref` selects which branch's workflow to execute. See
[GitHub's manual-run instructions](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
and the [workflow command reference](https://cli.github.com/manual/gh_workflow_run).

## Expected files

| Artifact | Files |
|---|---|
| Windows | `RecRoll-Windows-Universal-Installer.exe`, `RecRoll-1.0.0-Windows-x64.msi`, `RecRoll-1.0.0-Windows-arm64.msi`, `SIGNING-windows.txt` |
| macOS | `RecRoll-macOS-Universal.dmg`, `SIGNING-macos.txt` |

The DMG contains the PKG. Windows includes x64 and ARM64 builds; AAX is x64
only. macOS uses universal binaries containing arm64 and x86_64. Both plugin
products are included. AAX requires a successfully acquired SDK and PACE
signing before it can be used in regular release Pro Tools. An unsigned build
is a packaging/test result, not proof of PACE or operating-system trust.

The reports name the source commit, licensing commit, product version and
observed signing results. Confirm these match the revisions you selected.

## Configuration and signing

The required token names and licensing variables are in the root README. The
SDK token is needed if AAX must be included. Never paste tokens or signing
passwords into workflow inputs or public logs.

Default hosted runners can build unsigned installers. This workflow does not
install proprietary PACE tools. For actual PACE signing, provision an isolated,
trusted runner with the vendor-supported wraptool and licensing hardware or
service, then select its labels through `WINDOWS_RUNNER_LABELS` or
`MACOS_RUNNER_LABELS` (JSON arrays). Set `sign_pace=on` and `sign_binary=on`
only once the PACE, Windows certificate, Developer ID and Apple notarization
credentials are configured. Required signing fails if prerequisites are absent.

The complete local Windows/macOS build, PACE setup, certificate import and
verification guide is `docs/BUILD-SIGN-RELEASE-1.0.0.md` in the private source
repository. It documents the current implementation; the PACE/Avid developer
portal supplies the licensed tool and account-specific signing instructions.

## Publishing later

Use a **new, unused** tag, for example `v1.0.0-rc.1` only after checking that it
does not already exist. The source repository already has historical GPL
`v1.0.0` and `v1.1.0` tags. The current proprietary product's version reset
must not replace or relabel them. Keep `replace_existing=false`.

For a candidate build, set `prerelease=true`, both signing modes to `on`, and
the new tag. Verify every requested platform succeeds: the publisher can create
an explicitly incomplete prerelease when only one platform succeeds. A green
publish job alone does not prove both installers were built.

If an existing 1.2.0 installation is present, this intentional 1.0.0 reset can
be treated as a downgrade by the installer. Test a clean installation and the
documented uninstall/reinstall path before distributing it to those users.

Keep source, raw binaries, SDKs, certificates, logs and caches out of this
repository. Troubleshoot compiler failures in the private workflow at the same
source and licensing revisions; never disable public log redaction.
