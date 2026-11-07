<div align="center">

# RecRoll Suite — Public Releases

**Rolling sampler, retrospective audio recorder & companion wavetable/granular synthesizer.**<br>
Never lose a take you did not know you were recording.

[![Latest Release](https://img.shields.io/github/v/release/AA-EION/RecRoll-CICD-RELEASE?label=Latest%20Release&color=0f172a)](../../releases/latest)
[![Platforms](https://img.shields.io/badge/Platforms-Windows%2010%2F11%20%7C%20macOS%2011%2B-16a34a)](#installers)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%7C%20AU%20%7C%20CLAP%20%7C%20AAX%20%7C%20Standalone-ea580c)](#supported-formats)
[![License](https://img.shields.io/badge/License-Proprietary-64748b)](https://eionstudios.com)

**A product of [EION STUDIOS](https://eionstudios.com) · Protected by [Kuroko](https://issen.kurokamicorp.com)**

</div>

---

## Download

👉 **[Download RecRoll Suite at plugins.eionstudios.com](https://plugins.eionstudios.com)**

That page always has the current version for your system. The same installers are also attached to this repository's **[GitHub Releases](../../releases/latest)**.

---

## Overview

**RecRoll Suite** captures audio passing through any DAW channel in a lock-free circular RAM buffer (up to 10 minutes of stereo history) with **0 samples of latency** and bit-exact passthrough. Select any moment, audition it in place, reshape it through a modular 16-device rack, or drag it straight onto your DAW timeline as a 24-bit WAV.

The suite installs two plug-ins (and two standalone applications):

- **RecRoll (Effect)**: Continuous retrospective recorder with `15s`–`10m` buffer views, adaptive silence trimming, and a modular sound-design rack featuring 16 devices (*Granular, Wavetable, Filter, Gate, Compressor, Drive, Bit Crush, Psychoacoustic Sub-Harmonics, Chorus, Delay, Reverb, Utility, Resonator, Freq Shifter, Tape,* and *Repeat*) plus parallel **Split** lanes.
- **RecRoll Instrument (Companion Synthesizer)**: Dual-engine wavetable and granular synthesizer that receives captures directly from any open RecRoll instance over real-time lock-free IPC, complete with *Source FX*, *Voice FX*, 16-slot visual **Link** modulation, and searchable factory presets.

---

## Installers

| Platform | Architecture | Installer | Contents |
|---|---|---|---|
| **Windows 10 / 11** | Universal (`x64` + `ARM64`) | `RecRoll-<version>-Windows-Universal-Installer.exe` | VST3, CLAP, AAX, Standalone |
| **macOS 11+** | Universal 2 (`arm64` + `x86_64`) | `RecRoll-<version>-macOS-Universal.dmg` | `RecRoll Installer.pkg` (VST3, AU v2, CLAP, AAX, Standalone) and `Uninstall RecRoll.command` |

AAX is x64 only.

Every release also carries `release-manifest.json`, which lists each installer with its size and SHA-256. The plug-ins' update check, the EION Studios plug-in store and the Launcher read only that file.

---

## Supported Formats

RecRoll Suite registers under the manufacturer **EION Studios** in your DAW plug-in browser.

| Format | Windows | macOS |
|---|---|---|
| **VST3** | `C:\Program Files\Common Files\VST3\RecRoll*.vst3` | `/Library/Audio/Plug-Ins/VST3/RecRoll*.vst3` |
| **AU v2** | — | `/Library/Audio/Plug-Ins/Components/RecRoll*.component` |
| **CLAP** | `C:\Program Files\Common Files\CLAP\RecRoll*.clap` | `/Library/Audio/Plug-Ins/CLAP/RecRoll*.clap` |
| **AAX** | `C:\Program Files\Common Files\Avid\Audio\Plug-Ins\RecRoll*.aaxplugin` | `/Library/Application Support/Avid/Audio/Plug-Ins/RecRoll*.aaxplugin` |
| **Standalone** | `C:\Program Files\RecRoll\RecRoll*.exe` | `/Applications/RecRoll*.app` |

---

## Updates

When a new version is published here, RecRoll Suite tells you inside the plug-in and opens **[plugins.eionstudios.com](https://plugins.eionstudios.com)**, where you download and run the new installer. It installs over the previous version and keeps your license, settings and presets.

---

## Code Signing, Notarization & Integrity

- **macOS**: signed with an **Apple Developer ID** certificate (Hardened Runtime), notarized by Apple and stapled to both the `.pkg` and the `.dmg`. AAX bundles are wrapped and signed with **PACE Eden**. Installs without Gatekeeper warnings.
- **Windows**: AAX bundles are wrapped and signed with **PACE Eden** for Avid Pro Tools. The other binaries carry no public Authenticode certificate, so Windows SmartScreen shows an unknown-publisher prompt: choose *More info → Run anyway*.

Check a download against the SHA-256 in the release notes:

```bash
# macOS
shasum -a 256 RecRoll-*-macOS-Universal.dmg
```

```powershell
# Windows PowerShell
Get-FileHash -Algorithm SHA256 .\RecRoll-*-Windows-Universal-Installer.exe
```

---

## Licensing & Trial

- **Free tier, forever**: the core rolling sampler (15-second capture buffer, auditioning and drag-to-DAW export) never expires.
- **7-day evaluation**: the paid tiers (**Basic**, **Details** and **Creative**) can be tried for 7 days. They unlock longer buffers (`30s`–`10m`), the modular sound-design rack, **RecRoll Instrument** and real-time capture sharing between plug-ins.
- **Single activation**: one *RecRoll Suite* license activates both plug-ins in every format on that computer.

---

## Support

For documentation, licensing and technical support, visit **[eionstudios.com](https://eionstudios.com)**.

<div align="center">
<sub>Copyright © 2026 <b>EION STUDIOS</b> (永音). All rights reserved.</sub>
</div>
