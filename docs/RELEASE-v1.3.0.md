# RecRoll Suite 1.3.0

Release pública 1.3.0 de **RecRoll Suite** (**RecRoll** y **RecRoll Instrument**).

## Descargas

### macOS (Universal: Apple Silicon & Intel)

- **Instalador DMG**: `RecRoll-macOS-Universal.dmg`
  - **SHA-256**: `<SHA256_MACOS_DMG>`
  - Compatible con macOS 11.0 (Big Sur) hasta macOS 26 (Tahoe+).
  - Paquete Universal 2 nativo (`arm64` + `x86_64`).
  - Totalmente firmado con Apple Developer ID, notarizado y grapado (stapled) por Apple.

### Windows (x64 / ARM64)

- **Instalador Universal (.exe)**: `RecRoll-Windows-Universal-Installer.exe`
  - **SHA-256**: `<SHA256_WINDOWS_EXE>`
  - Instalador universal para Windows 10/11 (`x64` y `ARM64`).
  - Incluye plugins VST3, CLAP, AAX (PACE Eden wrapped y firmado) y aplicaciones Standalone.
- **Paquetes Windows Installer (.msi)**:
  - `RecRoll-1.3.0-Windows-x64.msi` — **SHA-256**: `<SHA256_WINDOWS_X64_MSI>`
  - `RecRoll-1.3.0-Windows-arm64.msi` — **SHA-256**: `<SHA256_WINDOWS_ARM64_MSI>`

---

## Formatos incluidos

Incluye **RecRoll** y **RecRoll Instrument** en:
- **VST3** (`RecRoll.vst3`, `RecRoll Instrument.vst3`)
- **AU / Audio Unit (.component)** (`RecRoll.component`, `RecRoll Instrument.component` — macOS)
- **CLAP** (`RecRoll.clap`, `RecRoll Instrument.clap`)
- **AAX** (`RecRoll.aaxplugin`, `RecRoll Instrument.aaxplugin` — Avid Pro Tools, firmados y wrapped con PACE Eden)
- **Aplicación Standalone** (`RecRoll`, `RecRoll Instrument`)

---

## Firma y notarización

- **macOS**: Todos los binarios y el instalador cuentan con firma oficial **Apple Developer ID** (`Juan Gallego - D7V3TP96W4`), **Hardened Runtime** y están **completamente notarizados y grapados (stapled)** por Apple. Los plugins AAX cuentan con la firma digital autorizada de **PACE Eden**. Instalación limpia y directa sin bloqueos de Gatekeeper.
- **Windows**: Los bundles AAX llevan la firma digital de **PACE Eden** y cargan en Pro Tools. El resto de binarios no llevan un certificado Authenticode de confianza pública: Windows SmartScreen mostrará un aviso de editor desconocido al ejecutar el instalador. Es esperado en esta versión. Para continuar: *"Más información" → "Ejecutar de todas formas"*.

---

## Changelog — 1.3.0

### Cadena modular de 16 dispositivos y procesamiento en paralelo (Split)
- **Rack de dispositivos en lugar de páginas**: Tanto el efecto como el instrumento construyen su sonido mediante una cadena modular de dispositivos arrastrables, duplicables y automatizables: *Granular, Wavetable, Filter, Gate, Compressor, Drive, Bit Crush, Sub-Harmonics, Chorus, Delay, Reverb, Utility, Resonator, Freq Shifter, Tape* y *Repeat*.
- **4 nuevos dispositivos de diseño sonoro**: *Resonator* (banco de 4 resonadores de cuerda afinados por acordes), *Freq Shifter* (desplazamiento lineal en Hz y modo Ring), *Tape* (saturación, wow/flutter, envejecimiento y hiss determinista) y *Repeat* (beat-repeat sincronizado al tempo del host).
- **Sub-armónicos psicoacústicos (*Sub-Harmonics*)**: Añade cuerpo y octava grave siguiendo la línea de bajo mientras mantiene el pico de salida dentro de ~1 dB.
- **Líneas en paralelo (*Split*)**: Cada cadena puede dividir la señal en 2 o 3 líneas paralelas con sus propios dispositivos y nivel de salida independiente (*OUT*), editables desde un panel dedicado sin alterar la altura del rack.

### RecRoll Instrument rediseñado en una sola vista
- **Ambos motores a la vez**: Los generadores *Wavetable* y *Granular* cuentan con interruptor de encendido y nivel propio más control *Balance* para combinarlos simultáneamente.
- **Flujo de señal ordenado de arriba abajo**: *1 Source* (captura + *Source FX* pre-síntesis), *2 Generate* (Wavetable, Granular, Mix), *3 Voice* (filtro + etapa *Amp* con envolvente de altura completa) y *4 Effects* (*FX* en tiempo real).
- **Tira unificada de moduladores y modo LINK**: Todas las fuentes (*Envelopes, LFOs, Macros, Note, Controllers* y *Links*) viven bajo la cabecera; el modo **LINK** muestra hasta 16 conexiones como cables de patch y permite usar cualquier potenciómetro como fuente de modulación.

### Presets con buscador, acabados y flujo de trabajo
- **Navegador de presets con búsqueda**: 14 nuevos presets de diseño sonoro en el efecto (`.recrollmod`) y 19 presets de fábrica en el instrumento, filtrables por categoría o texto.
- **Temas y tamaño de interfaz**: Acabados de hardware oscuro y claro (*About → Theme*) y escalado de ventana del **75% al 200%**.
- **Recorte de silencio adaptativo**: Eliminación automática de DC y seguimiento suave de ataques y colas al enviar audio a Mod o al Instrumento.
- **Capturas persistentes**: Las tomas arrastradas al DAW se guardan en `Music/RecRoll Captures` para que los proyectos guardados nunca pierdan sus referencias de audio.
- **Desinstalador configurable**: Permite elegir si conservar o eliminar presets, ajustes y activación de licencia (igual que en Boundless).
