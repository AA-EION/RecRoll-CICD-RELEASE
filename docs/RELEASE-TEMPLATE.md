# Plantilla de release — RecRoll Suite (ES / EN)

Usa esta plantilla al publicar a mano una versión nueva en **[GitHub Releases](../../releases/new)** o con `gh release create`. El tag es la versión (`1.2.3`).

> **Obligatorio / Required — `release-manifest.json`.** Cada release sube, junto a los instaladores, el `release-manifest.json` generado en el repositorio privado (`tools/make_release_manifest.py`). La comprobación de actualizaciones de los plugins, la tienda y el EION Studios Launcher solo leen ese archivo. Verifica antes de publicar: `./scripts/verify_public_payload.sh <carpeta>`.
>
> Every release uploads, beside the installers, the `release-manifest.json` generated in the private repository. The plug-ins' update check, the store and the Launcher read only that file. See [AGENTS.md](../AGENTS.md).

Archivos que se suben / Files to upload:

- `RecRoll-<VERSION>-Windows-Universal-Installer.exe`
- `RecRoll-<VERSION>-macOS-Universal.dmg`
- `release-manifest.json`

---

## Opción A — Español

````markdown
# RecRoll Suite <VERSION>

Versión pública <VERSION> de **RecRoll Suite**, sampler retrospectivo y sintetizador compañero (**RecRoll** y **RecRoll Instrument**) de **EION STUDIOS**.

**Descarga desde [plugins.eionstudios.com](https://plugins.eionstudios.com).** Los mismos instaladores están adjuntos abajo.

## Descargas

### macOS (Universal 2: Apple Silicon e Intel)

- **`RecRoll-<VERSION>-macOS-Universal.dmg`**
  - **SHA-256**: `<SHA256_MACOS_DMG>`
  - Compatible con macOS 11 (Big Sur) y posteriores.
  - Incluye `RecRoll Installer.pkg` y `Uninstall RecRoll.command`.
  - Firmado con Apple Developer ID, notarizado y grapado por Apple.

### Windows 10 / 11 (x64 y ARM64)

- **`RecRoll-<VERSION>-Windows-Universal-Installer.exe`**
  - **SHA-256**: `<SHA256_WINDOWS_EXE>`
  - Incluye VST3, CLAP, AAX (AAX firmado con PACE Eden) y la aplicación Standalone.
  - AAX es solo x64.

## Firma

- **macOS**: firma Apple Developer ID (`Juan Gallego - D7V3TP96W4`), Hardened Runtime, notarizado y grapado. AAX firmado con PACE Eden.
- **Windows**: AAX firmado con PACE Eden. El resto no lleva certificado Authenticode público, así que SmartScreen avisa de editor desconocido: *"Más información" → "Ejecutar de todas formas"*.

Comprueba la descarga con el SHA-256 indicado arriba.

## Cambios

### Novedades
- <Novedad 1>

### Correcciones
- <Corrección 1>
````

---

## Option B — English

````markdown
# RecRoll Suite <VERSION>

Public release <VERSION> of **RecRoll Suite** by **EION STUDIOS**.

**Download from [plugins.eionstudios.com](https://plugins.eionstudios.com).** The same installers are attached below.

## Downloads

### macOS (Universal 2: Apple Silicon and Intel)

- **`RecRoll-<VERSION>-macOS-Universal.dmg`**
  - **SHA-256**: `<SHA256_MACOS_DMG>`
  - Supports macOS 11 (Big Sur) and later.
  - Contains `RecRoll Installer.pkg` and `Uninstall RecRoll.command`.
  - Signed with Apple Developer ID, notarized and stapled by Apple.

### Windows 10 / 11 (x64 and ARM64)

- **`RecRoll-<VERSION>-Windows-Universal-Installer.exe`**
  - **SHA-256**: `<SHA256_WINDOWS_EXE>`
  - Includes VST3, CLAP, AAX (AAX signed with PACE Eden) and the Standalone application.
  - AAX is x64 only.

## Code signing

- **macOS**: Apple Developer ID (`Juan Gallego - D7V3TP96W4`), Hardened Runtime, notarized and stapled. AAX signed with PACE Eden.
- **Windows**: AAX signed with PACE Eden. Other binaries carry no public Authenticode certificate, so SmartScreen shows an unknown-publisher prompt: *More info → Run anyway*.

Check your download against the SHA-256 above.

## Changes

### New
- <Highlight 1>

### Fixes
- <Fix 1>
````
