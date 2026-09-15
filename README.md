<div align="center">

# RecRoll — Release Runners

**Public build and release infrastructure for [RecRoll](https://eionstudios.com), a product of EION STUDIOS.**

[![Guard](https://github.com/AA-EION/RecRoll-CICD-RELEASE/actions/workflows/guard.yml/badge.svg)](https://github.com/AA-EION/RecRoll-CICD-RELEASE/actions/workflows/guard.yml)
[![Build and publish RecRoll](https://github.com/AA-EION/RecRoll-CICD-RELEASE/actions/workflows/release.yml/badge.svg)](https://github.com/AA-EION/RecRoll-CICD-RELEASE/actions/workflows/release.yml)

</div>

---

## ⚠️ This repository is for runners only

**No application code belongs here. Ever.**

This repository exists for one reason: so that GitHub's runners can build and
publish RecRoll without the application source being public. It contains
workflows, guard scripts and documentation — nothing else.

The plugin's source, its build system, its installers and its signing scripts
all live in the private **[AA-EION/RecRoll](https://github.com/AA-EION/RecRoll)**
repository. This repository clones that one at build time, runs *its* scripts,
publishes the allowlisted installers and signing reports, and deletes the clone.

A file committed here is public the moment it is pushed, and deleting it later
does not undo that — it stays in the git history and in every fork and clone
that already exists. So the rule is enforced by a check, not by memory:
[`scripts/guard_no_source.sh`](scripts/guard_no_source.sh) runs on every push
and pull request and fails the build if anything that looks like application or
packaging code appears in the tree.

If you are about to add a `.cpp`, a `CMakeLists.txt`, an `.iss`, a `.wxs`, a
certificate or a `Source/` directory — it belongs in the private repository.

---

## What this repository publishes

End-user installers, and nothing else:

| Platform | Asset | Contains |
|---|---|---|
| **Windows 10/11** | `RecRoll-Windows-Universal-Installer.exe` | VST3, CLAP, AAX, standalone — one file for Intel/AMD **and** Snapdragon |
| **macOS 11+** | `RecRoll-macOS-Universal.dmg` | A branded EION STUDIOS disk image with the installer package inside |
| Windows, scripted | `RecRoll-<version>-Windows-x64.msi`, `-arm64.msi` | The same payload for Group Policy, Intune, SCCM or `msiexec /qn` |

The `.exe` is the headline Windows download because it carries both
architectures and picks between them at install time. A Windows Installer
package cannot: its target architecture is fixed in the package, so the MSIs
come in a matched pair and the user has to know which machine they are on.
Installing the x64 package on a Snapdragon succeeds under emulation and then
leaves the plug-ins invisible to a native ARM64 host — a silent wrong answer,
which is why the MSIs are secondary rather than the front door.

…plus `SIGNING-windows.txt` and `SIGNING-macos.txt`, which state exactly what
was and was not signed in that build.

Everything else the build produces — the portable archives, the raw AAX
bundles, the component packages — stays private and is released from the
private repository instead.

The macOS DMG opens onto a branded window laid out for a first-time user:

```
        EION STUDIOS
          RecRoll
  ROLLING SAMPLER · RETROSPECTIVE RECORDER

  Double-click the installer, then follow the prompts.

    [pkg]        [read me]      [uninstall]     [legal]
   STEP 1     BEFORE YOU START   IF NEEDED       LEGAL
```

The Windows MSI carries the same artwork in its installer dialogs, so the two
platforms present one brand.

---

## Using it

Version **1.0.0**. Release-specific instructions: **[docs/RELEASE-1.0.0.md](docs/RELEASE-1.0.0.md)**

Full operations reference: **[docs/RUNBOOK.md](docs/RUNBOOK.md)**
Security model: **[docs/SECURITY-MODEL.md](docs/SECURITY-MODEL.md)**
For AI agents: **[AGENTS.md](AGENTS.md)**

The short version — from the **Actions** tab, run **Build and publish RecRoll**:

| Input | Meaning |
|---|---|
| `source_ref` | Branch, tag or SHA of `AA-EION/RecRoll` to build |
| `kuroko_ref` | Optional licensing revision override; otherwise use the source `KUROKO_REVISION` pin |
| `release_tag` | Publish under this tag. **Leave empty to build without releasing.** |
| `sign_pace` | `auto` / `on` / `off` — PACE Eden signing for AAX |
| `sign_binary` | `auto` / `on` / `off` — Developer ID and Authenticode signing, and notarisation |
| `platforms` | `both` / `windows` / `macos` |
| `prerelease` | Mark as a pre-release. Forced on when nothing was signed. |

`sign_pace` and `sign_binary` are independent, so all four signing shapes are
reachable: both signed, PACE only, binaries only, neither.

---

## Required secrets

| Secret | Purpose |
|---|---|
| `RECROLL_SOURCE_TOKEN` | **Required.** Fine-grained PAT with read-only *Contents* access to `AA-EION/RecRoll`. Nothing else. |
| `KUROKO_SOURCE_TOKEN` | **Required.** The same, for `AA-EION/Kuroko` — the licensing client the plugins are built against. |
| `RECROLL_GATE_SECRET` | **Required.** The per-product licensing gate secret, e.g. `0x5B27E1A3u`. |
| `AAX_SDK_TOKEN` | Read access to `AA-EION/AAX-SDK`, for the AAX format |
| `PACE_*`, `MACOS_*`, `WINDOWS_*` | Signing credentials — see the private repository's `installer/signing/README.md` |

## Required variables

| Variable | Purpose |
|---|---|
| `RECROLL_LICENSE_SERVER_URL` | The licensing server the plugins call, e.g. `https://lic.eionstudios.com`. Must be HTTPS; the build refuses anything else. |
| `RECROLL_LICENSE_PUBLIC_KEY` | The Ed25519 trust anchor, 64 hex characters, printed by the licensing server on boot. |

Variables, not secrets, and deliberately so: both are public by construction —
an endpoint clients connect to, and a key that only *verifies* — and masking
them in logs would make it impossible to tell which server and which key a
release was built against without opening the private log. The gate secret is
the one that is genuinely secret, and the log redactor withholds anything shaped
like it.

The licensing ones have no "optional" mode here. This repository publishes the
installers people download, so a build with licensing off would put unprotected
plugins on a public release page; the build fails instead. The private
repository has a per-run switch for deliberate unprotected builds, and those are
not the builds that get published.

Without the signing secrets the build still succeeds and produces unsigned
installers, which the manifest reports honestly.

---

<div align="center">
<sub>A product of <b>EION STUDIOS</b> · Engineered by ISSEN Software Group</sub>
</div>
