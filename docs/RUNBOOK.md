# Runbook — publishing a RecRoll release from this repository

Everything here happens from the GitHub web UI or the `gh` CLI. You never need
to clone this repository to use it.

---

## One-time setup

### 1. Create the source token

The runners need to clone the private repository. Give them the narrowest
credential that allows it.

1. GitHub → **Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token**
2. **Resource owner:** `AA-EION`
3. **Repository access:** *Only select repositories* → `AA-EION/RecRoll`
   (and `AA-EION/AAX-SDK` if you want AAX built)
4. **Permissions:** *Repository permissions → Contents → **Read-only***.
   Nothing else. Not Actions, not Workflows, not Metadata write.
5. **Expiration:** 90 days. Put a reminder in your calendar — an expired token
   shows up as a checkout failure in the build job, which is easy to misread as
   a broken workflow.

Add it here as the secret **`RECROLL_SOURCE_TOKEN`**
(*Settings → Secrets and variables → Actions → New repository secret*).

A token scoped this way can read the source. It cannot push, cannot open pull
requests, cannot read other repositories, and cannot touch Actions. If it ever
leaks, the damage is bounded to "someone read code they could have read by
compromising a runner anyway" — and you revoke it in one click.

### 2. Add the licensing inputs (required)

The plugins this repository publishes are licensed products, and the licensing
client lives in a second private repository. Create a second fine-grained PAT
exactly like the first — *Contents: read-only*, on `AA-EION/Kuroko`, nothing
else — and add it as the secret **`KUROKO_SOURCE_TOKEN`**.

Then add:

| Kind | Name | Value |
|---|---|---|
| Secret | `RECROLL_GATE_SECRET` | The per-product gate secret, e.g. `0x5B27E1A3u`. Must match the value the private repository builds with. |
| Variable | `RECROLL_LICENSE_SERVER_URL` | `https://lic.eionstudios.com` — the server the plugins call. HTTPS only; the build refuses anything else. |
| Variable | `RECROLL_LICENSE_PUBLIC_KEY` | The 64-hex-character Ed25519 public key the licensing server prints on boot. |

The last two are *variables* on purpose. An endpoint and a verify-only public
key are public by construction, and hiding them in logs would only make it
impossible to tell which server and which key a release was built against.
`RECROLL_GATE_SECRET` is the real secret — it is what somebody patching the
binary would need to forge the license gate's check field — so it is never
printed, and `scripts/redact_log.py` withholds any line shaped like it.

None of these are optional. A build here produces the installers people
download; one with licensing off would publish unprotected plugins. If any are
missing the run fails in its first minute with a message naming exactly what to
create, rather than 40 minutes later in a CMake error.

### 3. Add the AAX SDK token (optional)

`AAX_SDK_TOKEN` — read access to `AA-EION/AAX-SDK`. Without it the build still
succeeds; it simply produces no AAX format, and the installers offer no AAX
component.

### 4. Add the signing secrets (optional)

Copy them from the private repository, or set them up fresh following
`installer/signing/README.md` there. The full list:

```
PACE_ACCOUNT  PACE_PASSWORD  PACE_WC_GUID  PACE_SIGN_ID

MACOS_CERT_P12_BASE64  MACOS_CERT_PASSWORD
MACOS_DEV_ID_APP       MACOS_DEV_ID_INSTALLER   MACOS_KEYCHAIN_PASSWORD
MACOS_NOTARY_API_KEY_BASE64  MACOS_NOTARY_KEY_ID  MACOS_NOTARY_ISSUER_ID
   (or) MACOS_NOTARY_APPLE_ID  MACOS_NOTARY_PASSWORD  MACOS_NOTARY_TEAM_ID

WINDOWS_CERT_PFX_BASE64  WINDOWS_CERT_PASSWORD  WINDOWS_TIMESTAMP_URL
```

Skip the ones you do not have. A build with no signing secrets at all still
produces complete installers.

### 4. Self-hosted runners (optional)

Set repository *variables* (not secrets) to move a job off the hosted runners:

```
WINDOWS_RUNNER_LABELS = ["self-hosted","windows","x64"]
MACOS_RUNNER_LABELS   = ["self-hosted","macOS","ARM64"]
```

Unset, the jobs use `windows-latest` and `macos-14`.

---

## Publishing a release

**Actions → Build and publish RecRoll → Run workflow.**

| Input | Set it to |
|---|---|
| `source_ref` | The tag you are releasing, e.g. `v1.1.0`. A branch or SHA also works. |
| `release_tag` | The same tag. **Empty means build but do not publish** — that is the dry run. |
| `sign_pace` | `on` for a real release. |
| `sign_binary` | `on` for a real release. |
| `platforms` | `both` |
| `replace_existing` | `true` if you are re-cutting a tag you already published. |
| `prerelease` | `true` for a release candidate. It is forced on anyway when nothing was signed. |

Setting both signing switches to `on` rather than leaving them at `auto` is the
point of the distinction: `auto` skips signing when a secret is missing and
ships anyway, `on` fails the build. For a release you want the failure.

When the run finishes, the release appears on the **Releases** page with the
MSIs, the DMG and the signing manifests attached.

An unsigned build is always published as a pre-release, whatever you set
`prerelease` to. Gatekeeper and SmartScreen both warn on an unsigned installer,
and someone who has to click through those warnings should have been told by
the label on the release rather than finding out at the download. The publish
job decides this from the signing manifest, not from the inputs.

### Dry run first

Leave `release_tag` empty. The build runs end to end and uploads the same files
as **workflow artefacts** instead of publishing them. Download them from the run
summary, install them on a real machine, then run again with the tag.

This is worth doing for anything that touches packaging. The DMG's window
layout in particular depends on Finder scripting being available on the runner;
the build logs whether the layout was applied, but the only way to be sure it
looks right is to mount it.

### From the CLI

```bash
gh workflow run release.yml \
  --repo AA-EION/RecRoll-CICD-RELEASE \
  -f source_ref=v1.1.0 \
  -f release_tag=v1.1.0 \
  -f sign_pace=on \
  -f sign_binary=on \
  -f platforms=both

gh run watch --repo AA-EION/RecRoll-CICD-RELEASE
```

---

## The four signing shapes

`sign_pace` and `sign_binary` are independent, and every combination is a
supported release:

| `sign_pace` | `sign_binary` | Result |
|---|---|---|
| `on` | `on` | The real public release. AAX loads in Pro Tools; Gatekeeper and SmartScreen stay quiet. |
| `on` | `off` | AAX loads in Pro Tools, but macOS and Windows warn on first launch. Useful for testing AAX without burning a notarisation round trip. |
| `off` | `on` | Everything signed and notarised, no AAX. Useful when the PACE account is unavailable. |
| `off` | `off` | Nothing signed. Fast. For testing packaging only — do not hand this to a user expecting a clean install. |

`auto` means "sign if the secrets are there". It is the default so that a run
by someone without the credentials still works, but it is not what a release
wants.

Whatever you choose, the published `SIGNING-*.txt` reports what actually
happened rather than what was requested — a run that asked for signing and
skipped it says so.

---

## Reading a failed build

Build logs here are **redacted**. This repository is public, and a failing
compile quotes the source line it choked on. `scripts/redact_log.py` reduces
diagnostics to file name, line number and error code, and withholds the rest.

So a failure looks like:

```
RingBuffer.cpp(214): error C2065  [message withheld]
--- 37 line(s) withheld by scripts/redact_log.py ---
```

That is enough to locate the problem. For the full text, run the same commit
through the private repository's own workflow — its logs are private and
unredacted:

```bash
gh workflow run build-and-release.yml --repo AA-EION/RecRoll -r <branch>
```

There is no switch here to turn redaction off. There was one, briefly, and it
had no use the private workflow does not cover better — so it was only ever a
way to publish source into a public log by accident.

### Failures that are not build failures

| Symptom | Cause |
|---|---|
| The "Clone the private source" step fails with 404 | `RECROLL_SOURCE_TOKEN` expired, was revoked, or lacks access to `AA-EION/RecRoll`. The 404 is deliberate on GitHub's side — a private repository you cannot see is indistinguishable from one that does not exist. |
| The "Clone the Kuroko licensing client" step fails with 404 | The same, for `KUROKO_SOURCE_TOKEN` and `AA-EION/Kuroko`. |
| "Licensing inputs are missing" in the first minute | One of `KUROKO_SOURCE_TOKEN`, `RECROLL_GATE_SECRET`, `RECROLL_LICENSE_SERVER_URL` or `RECROLL_LICENSE_PUBLIC_KEY` is unset. The message names which. This check exists so the run fails here instead of at CMake configure time. |
| `RECROLL_LICENSE_PUBLIC_KEY must be exactly 64 hex characters` | The variable was pasted with a stray space, a `0x` prefix, or truncated. It is the plain hex the server prints, nothing around it. |
| CMake: `SERVER_URL must be https://` | `RECROLL_LICENSE_SERVER_URL` is plaintext. Licensing traffic carries serial keys; the build will not produce a release that sends them in the clear. |
| `No public deliverable found in src/dist` | The build succeeded but produced no MSI or DMG. Look further up for the packaging step. |
| `wix build failed` | Usually a payload missing from staging. The MSI script prints which payloads it found before it compiles. |
| No `.exe` on the release | Inno Setup was not installed on the runner. The build logs a warning and carries on, so the job stays green and the MSIs still ship. |
| The DMG builds but looks unstyled | Finder scripting was unavailable on the runner. The image is valid, just not laid out. The build logs `styled: no`. |
| Notarisation times out | Apple's service, not you. Re-run the job. |

---

## Cutting a release end to end

1. Tag the private repository: `git tag v1.1.0 && git push origin v1.1.0`
2. Dry run here with `source_ref=v1.1.0` and `release_tag` empty.
3. Download the artefacts; run the `.exe` on Windows and mount the DMG on macOS.
   Check the MSIs too if you publish them — they install the same payload, but
   through a different installer engine.
4. Run again with `release_tag=v1.1.0`, `sign_pace=on`, `sign_binary=on`.
5. Check the release page: the Windows `.exe`, the macOS `.dmg`, both MSIs and
   the two manifests.
6. Read the manifests. If either says `unsigned` where you expected otherwise,
   the release is wrong regardless of what the run's green tick says.
