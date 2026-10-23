# Plantilla de Release — RecRoll Suite (ES / EN)

Usa esta plantilla al publicar manualmente una nueva versión en **[GitHub Releases](../../releases/new)** o mediante `gh release create`. Se suben los instaladores (el instalador `.exe` de Windows y el `.dmg` de macOS) y `release-manifest.json`.

> **Obligatorio / Required — `release-manifest.json`.** Cada release sube, junto a los instaladores, el `release-manifest.json` generado en el repositorio privado (`tools/make_release_manifest.py`). La tienda y el EION Studios Launcher solo leen ese archivo: una plataforma que no aparece en él se muestra como *no disponible*. Si se añade o reemplaza un instalador después, se regenera y se vuelve a subir en el mismo paso. Verifica antes de publicar: `./scripts/verify_public_payload.sh <carpeta>`.
>
> Every release uploads, beside the installers, the `release-manifest.json` generated in the private repository. The store and the Launcher read only that file; a platform it does not list is shown as *not available*. When an installer is added or replaced later, regenerate and re-upload it in the same step. See [AGENTS.md](../AGENTS.md#every-release-carries-release-manifestjson-required).

---

## Opción A — Español (Formato oficial EION Studios)

````markdown
# RecRoll Suite <VERSION>

Release pública <VERSION> de **RecRoll Suite** (**RecRoll** y **RecRoll Instrument**).

## Descargas

### macOS (Universal: Apple Silicon & Intel)

- **Instalador DMG**: `RecRoll-macOS-Universal.dmg`
  - **SHA-256**: `<SHA256_MACOS_DMG>`
  - Compatible con macOS 11.0 (Big Sur) hasta macOS 26 (Tahoe+).
  - Paquete universal nativo (`arm64` + `x86_64`).
  - Totalmente firmado con Apple Developer ID y notarizado por Apple.

### Windows (x64 / ARM64)

- **Instalador Universal**: `RecRoll-Windows-Universal-Installer.exe`
  - **SHA-256**: `<SHA256_WINDOWS_EXE>`
  - Instalador universal para Windows 10/11 (x64 y ARM64).
  - Incluye plugins VST3, CLAP, AAX (PACE Eden wrapped y firmado) y aplicación Standalone.

---

## Formatos incluidos

Incluye **RecRoll** y **RecRoll Instrument** en:
- **VST3**
- **AU / Audio Unit (.component)** (macOS)
- **CLAP**
- **AAX** (Avid Pro Tools — firmado y wrapped con PACE Eden)
- **Aplicación Standalone**

---

## Firma y notarización

- **macOS**: Todos los binarios y el instalador cuentan con firma oficial **Apple Developer ID** (`Juan Gallego - D7V3TP96W4`), **Hardened Runtime** y están **completamente notarizados y grapados (stapled)** por Apple. Los plugins AAX cuentan con la firma digital autorizada de **PACE Eden**. Instalación limpia y directa sin bloqueos de Gatekeeper.
- **Windows**: Los bundles AAX llevan la firma digital de **PACE Eden** y cargan en Pro Tools. El resto de binarios no llevan un certificado Authenticode de confianza pública: Windows SmartScreen mostrará un aviso de editor desconocido al ejecutar el instalador. Es esperado en esta versión. Para continuar: *"Más información" → "Ejecutar de todas formas"*.

---

## Changelog

### <Categoría 1>
- <Cambio 1>
- <Cambio 2>

### Correcciones
- <Corrección 1>
````

---

## Opción B — English

````markdown
# RecRoll Suite <VERSION>

Public release <VERSION> of **RecRoll Suite** (**RecRoll** and **RecRoll Instrument**).

## Downloads

### macOS (Universal: Apple Silicon & Intel)

- **DMG Installer**: `RecRoll-macOS-Universal.dmg`
  - **SHA-256**: `<SHA256_MACOS_DMG>`
  - Supports macOS 11.0 (Big Sur) through macOS 26 (Tahoe+).
  - Native Universal 2 package (`arm64` + `x86_64`).
  - Signed with Apple Developer ID, notarized, and stapled by Apple.

### Windows (x64 / ARM64)

- **Universal Installer**: `RecRoll-Windows-Universal-Installer.exe`
  - **SHA-256**: `<SHA256_WINDOWS_EXE>`
  - Universal installer for Windows 10/11 (x64 and ARM64).
  - Includes VST3, CLAP, AAX (PACE Eden wrapped and signed), and Standalone applications.

---

## Included Formats

Includes both **RecRoll** and **RecRoll Instrument** in:
- **VST3**
- **AU / Audio Unit (.component)** (macOS)
- **CLAP**
- **AAX** (Avid Pro Tools — PACE Eden wrapped & signed)
- **Standalone Application**

---

## Code Signing & Notarization

- **macOS**: All binaries and the installer are signed with **Apple Developer ID** (`Juan Gallego - D7V3TP96W4`) with **Hardened Runtime**, and are **notarized and stapled** by Apple. Both AAX bundles carry authorized **PACE Eden** digital signatures. Installs without Gatekeeper prompts.
- **Windows**: Both AAX bundles carry **PACE Eden** digital signatures and load in Pro Tools. Other Windows binaries do not carry a public CA Authenticode certificate: Windows SmartScreen will display an unknown publisher prompt when launching the installer. Click *"More info" → "Run anyway"* to proceed.

---

## Changelog

### <Section 1>
- <Change 1>
- <Change 2>

### Fixes
- <Fix 1>
````
