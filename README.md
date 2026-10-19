<div align="center">

# RecRoll — Public Releases

**Rolling sampler, retrospective audio recorder & companion wavetable/granular synthesizer.**<br>
Never lose a take you did not know you were recording.

[![Latest Release](https://img.shields.io/github/v/release/AA-EION/RecRoll-CICD-RELEASE?label=Latest%20Release&color=0f172a)](../../releases/latest)
[![Platforms](https://img.shields.io/badge/Platforms-Windows%2010%2F11%20%7C%20macOS%2011%2B-16a34a)](#deliverables)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%7C%20AU%20%7C%20CLAP%20%7C%20AAX%20%7C%20Standalone-ea580c)](#supported-formats)
[![License](https://img.shields.io/badge/License-Proprietary-64748b)](https://eionstudios.com)

**A product of [EION STUDIOS](https://eionstudios.com) · Engineered by ISSEN Software Group · Protected by [Kuroko](https://issen.kurokamicorp.com)**

</div>

---

## Overview

**RecRoll Suite** captures audio passing through any DAW channel in a lock-free circular RAM buffer (up to 10 minutes of stereo history) with **0 samples of latency** and bit-exact passthrough. Select any moment, audition it in place, reshape it through a modular 16-device rack, or drag it straight onto your DAW timeline as a 24-bit WAV.

The suite installs two plug-ins (and two standalone applications):

- **RecRoll (Effect)**: Continuous retrospective recorder with `15s`–`10m` buffer views, adaptive silence trimming, and a modular sound-design rack featuring 16 devices (*Granular, Wavetable, Filter, Gate, Compressor, Drive, Bit Crush, Psychoacoustic Sub-Harmonics, Chorus, Delay, Reverb, Utility, Resonator, Freq Shifter, Tape,* and *Repeat*) plus parallel **Split** lanes.
- **RecRoll Instrument (Companion Synthesizer)**: Dual-engine wavetable and granular synthesizer that receives captures directly from any open RecRoll instance over real-time lock-free IPC, complete with *Source FX*, *Voice FX*, 16-slot visual **Link** modulation, and searchable factory presets.

---

## Deliverables

👉 **[Download the latest release from GitHub Releases](../../releases/latest)**

| Platform | Architecture | Installer Package | Description |
|---|---|---|---|
| **Windows 10 / 11** | Universal (`x64` & `ARM64`) | `RecRoll-Windows-Universal-Installer.exe` | Universal setup installer for Intel/AMD (`x64`) and Snapdragon X (`ARM64`) |
| **Windows 10 / 11 (MSI)** | `x64` / `ARM64` | `RecRoll-<version>-Windows-x64.msi`<br>`RecRoll-<version>-Windows-arm64.msi` | Enterprise & managed Windows Installer packages |
| **macOS 11+** | Universal 2 (`arm64` + `x86_64`) | `RecRoll-macOS-Universal.dmg` | Signed & notarized disk image containing `RecRoll Installer.pkg` & Uninstaller |

Each release includes SHA-256 checksums and `SIGNING-windows.txt` / `SIGNING-macos.txt` verification manifests.

---

## Supported Formats

Both **RecRoll** and **RecRoll Instrument** register under the manufacturer **EION Studios** in your DAW plug-in browser.

| Format | Windows 10/11 (`x64` / `ARM64`) | macOS 11+ (`Universal 2: Apple Silicon + Intel`) |
|---|---|---|
| **VST3** | `C:\Program Files\Common Files\VST3\RecRoll*.vst3` | `/Library/Audio/Plug-Ins/VST3/RecRoll*.vst3` |
| **AU v2** | — | `/Library/Audio/Plug-Ins/Components/RecRoll*.component` |
| **CLAP** | `C:\Program Files\Common Files\CLAP\RecRoll*.clap` | `/Library/Audio/Plug-Ins/CLAP/RecRoll*.clap` |
| **AAX** | `C:\Program Files\Common Files\Avid\Audio\Plug-Ins\RecRoll*.aaxplugin` (`x64`) | `/Library/Application Support/Avid/Audio/Plug-Ins/RecRoll*.aaxplugin` |
| **Standalone** | `C:\Program Files\RecRoll\RecRoll*.exe` | `/Applications/RecRoll*.app` |

---

## Code Signing, Notarization & Integrity Verification

- **macOS**: Signed with an official **Apple Developer ID** certificate (Hardened Runtime), notarized by Apple, and stapled to both the installer `.pkg` and `.dmg`. Both AAX bundles carry authorized **PACE Eden** digital signatures. Installs cleanly without Gatekeeper prompts.
- **Windows**: Both AAX bundles are digitally wrapped and signed with **PACE Eden** for Avid Pro Tools. Verify all installer downloads against the SHA-256 hashes published in each release's notes:

```bash
# macOS
shasum -a 256 RecRoll-macOS-Universal.dmg
```

```powershell
# Windows PowerShell
Get-FileHash -Algorithm SHA256 .\RecRoll-Windows-Universal-Installer.exe
Get-FileHash -Algorithm SHA256 .\RecRoll-*-Windows-*.msi
```

---

## Licensing & Tiers

The core rolling sampler (**Free tier**: 15-second capture buffer, auditioning, and drag-to-DAW export) is **free forever** with no trial expiry. Paid tiers (**Basic**, **Details**, and **Creative**) unlock extended buffer durations (`30s`–`10m`), the modular sound-design rack, **RecRoll Instrument**, and real-time cross-plugin capture sharing with a single license activation (*RecRoll Suite*).

---

## Support

For product documentation, tier upgrades, and technical support, visit **[eionstudios.com](https://eionstudios.com)**.

<div align="center">
<sub>Copyright © 2026 <b>EION STUDIOS</b> (永音). All rights reserved.</sub>
</div>
