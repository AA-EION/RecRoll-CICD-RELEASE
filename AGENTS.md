# Notes for AI agents working in this repository

## What this repository is

The **public release repository** of one EION Studios plug-in. It holds the
README, the release-notes template, the `release-manifest.json` check and the
installers uploaded by hand to GitHub Releases. **It contains no application
code, no packaging code and no build pipeline.**

`Boundless-CICD-RELEASE`, `RecRoll-CICD-RELEASE` and `FlyVerb-CICD-RELEASE` have
the same layout and the same scripts and workflow, byte for byte. The only
files that differ between them are:

| File | What changes |
|---|---|
| `scripts/product.env` | product id (`PRODUCT_ID`) and installer file prefix (`FILE_PREFIX`) |
| `README.md` | product description, formats, paths, trial |
| `docs/RELEASE-TEMPLATE.md` | release-notes text |

Change a shared file in all three repositories at once. Work directly on
`main`; these repositories use no branches.

```
.github/CODEOWNERS
.github/workflows/release-manifest.yml   the only workflow
docs/RELEASE-TEMPLATE.md
scripts/product.env
scripts/guard_no_source.sh
scripts/verify_public_payload.sh
scripts/verify_release_manifest.py
AGENTS.md  README.md  .gitignore  .gitattributes
```

## The layout rule

**Never add application or packaging code here**, nor any build or release
automation that reaches the private repositories, nor any secret, encrypted
or not. That includes `.cpp`, `.h`, `.mm`, `CMakeLists.txt`, `.cmake`, `.iss`,
`.wxs`, project files, `src/`, `Source/`, `resources/`, `packaging/`,
`installer/`, `libs/`, and any certificate, key or `.enc` file.

`scripts/guard_no_source.sh` enforces this. Run it before you commit.

## Release model

Releases are built, signed and notarized locally on dedicated Windows and
macOS machines from the private product repository, then uploaded by hand.

1. **Installer names** are the same in every product:

   | Platform | File |
   |---|---|
   | Windows, x64 + ARM64 | `<Product>-<version>-Windows-Universal-Installer.exe` |
   | Windows, x64 only | `<Product>-<version>-Windows-x64-Installer.exe` |
   | macOS, Universal 2 | `<Product>-<version>-macOS-Universal.dmg` |

   `<Product>` is `FILE_PREFIX` in `scripts/product.env`.

2. **Every release has `release-manifest.json` next to the installers**,
   generated in the private product repository with
   `tools/make_release_manifest.py --dist <folder>`. Never write or edit it by
   hand.

3. **Verify the folder before uploading**:

   ```bash
   ./scripts/verify_public_payload.sh <release-files-dir>
   ```

4. The tag is the version (`1.2.3`, or `v1.2.3`) and must equal the
   manifest's `version`. Use `docs/RELEASE-TEMPLATE.md` for the notes.

5. **When the installers of a published release change** (a platform added
   later, an installer replaced), regenerate the manifest in the product
   repository (`--merge` with the attached copy keeps the other platforms) and
   upload it with the installer:

   ```bash
   source scripts/product.env
   ./scripts/verify_public_payload.sh <folder-with-new-installer-and-manifest> --adding
   gh release upload <tag> <new installer> <folder>/release-manifest.json --clobber
   python3 scripts/verify_release_manifest.py --github <tag> --repo <owner>/<this-repository> --product "$PRODUCT_ID"
   ```

## Who reads `release-manifest.json`

- **The plug-ins' update check** reads
  `https://github.com/AA-EION/<this-repository>/releases/latest/download/release-manifest.json`,
  compares `version` with its own and, when it is newer, sends the user to
  **https://plugins.eionstudios.com** to download it. The plug-ins never
  download installers from GitHub themselves. A release marked *latest* must
  therefore always carry a valid manifest.
- **The plug-in store and the EION Studios Launcher** read the platforms and
  each installer's size and SHA-256 from it. A platform it does not list is
  shown as not available; a release whose manifest does not match its files is
  rejected.

The fields are those of schema 2 (`schemaVersion`, `product`, `name`,
`version`, `releasedAt`, `channel`, `sourceCommit`, `changelog.en`,
`changelog.es`, `artifacts[]` with `file`, `platform`, `arch`, `kind`, `size`,
`sha256`, `minimumSystem`, `formats`, and `install`). The contract is
`shared/schema/release-manifest.schema.json` in
`AA-EION/EION-STUDIOS-PLUGIN-LAUNCHER`.

`.github/workflows/release-manifest.yml` re-checks every release when it is
published or edited, and fails when the manifest is missing or out of date.

## Testing a change

```bash
./scripts/guard_no_source.sh
python3 -m py_compile scripts/*.py
for f in scripts/*.sh; do bash -n "$f"; done
```
