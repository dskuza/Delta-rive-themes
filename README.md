# Delta Rive themes

Two controller themes for the `rive` branch of [dskuza/Delta](https://github.com/dskuza/Delta/tree/rive):

| Folder | Controller | Output | Identifier |
| --- | --- | --- | --- |
| `nes/` | Digital D-pad, red A/B, Select, Start and Menu | `Dist/nes.deltaskin` | `com.dskuza.delta.rive.nes` |
| `n64/` | Continuous analog stick, digital D-pad, A/B, four C-buttons, L/R, dual Z, Start and Menu | `Dist/n64.deltaskin` | `com.dskuza.delta.rive.n64` |

Both use clear vector materials, colored socket LEDs and animated circuit signals.
N64 uses the original blue/green/yellow/red palette; NES uses gray/black/red.
Quick taps can finish their visual signal after the native input releases.
Reduced Motion uses stationary feedback. Both phone orientations include native
fallback artwork, rendered picker previews, and safe-area-aware layouts.

DeltaCore handles native touch, multitouch, controller input and emulation.
RiveRuntime's Concurrency API receives state for visual feedback; gameplay does
not wait for animation. The N64 cap follows signed X/Y continuously, while a
separate contact light can react to a thumb resting at the center.

## Build

Requires macOS with Metal, Xcode command-line tools, Python 3 and Rive CLI 1.8.0+.
The current scenes contain no executable scripts and export without a Rive login.

```sh
python3 Tools/build_themes.py
# Or build one controller:
python3 Tools/build_themes.py nes
python3 Tools/build_themes.py n64
```

This creates `.riv` files and importable `.deltaskin` ZIPs under `Dist/`.
Exports, per-controller `build/` folders, caches, recordings and local settings
are ignored by Git. Editable sources, metadata, fonts and licenses stay tracked.
Hand-authored `.riv` files outside `Dist/` remain eligible for version control.

## Edit the controllers

The geometry and artwork are generated from these sources:

- `Tools/generate_nes.py`: NES layout and feedback.
- `Tools/generate_n64.py`: N64 layout and the shared clear-material/circuit helpers.
- `Tools/controller_scene.py`: shared RML primitives, typed view models,
  Boolean transition conditions and numeric binding helpers.
- `Tools/default_layout.py` and `Assets/DefaultLayouts.json`: optional placement
  references from Delta's bundled phone skins.

When changing a generator, regenerate that controller before building:

```sh
python3 Tools/generate_nes.py
python3 Tools/generate_n64.py
python3 Tools/build_themes.py
```

The generated `scene.rml`, `rive.yaml`, `info.json`, `rive.json` and
`circuit-layout.json` remain editable authoring assets. Avoid hand-editing generated
files and later overwriting those edits by rerunning their generator.

## Develop a new theme with an AI assistant

Start with [SKILLS.md](SKILLS.md). Its provider-neutral skill explains the native
input contract, required view-model/default-instance setup, Boolean and Number
bindings, trigger limitations, analog/contact values, custom layouts and validation.
The current controller positions and visual treatment are examples, not requirements.

See the skill's [theme contract](.agents/skills/create-delta-rive-theme/references/theme-contract.md)
for schema version 1. A package's `info.json` defines native hit targets and
fallback assets; `rive.json` maps native input names to the Rive model properties.

## Set up Delta and import

The repositories normally sit beside each other:

```text
workspace/
  Delta/                # rive
  Delta-rive-themes/    # main
```

```sh
./Tools/setup.sh
./Tools/import_simulator.sh --device booted --restart
# Rebuild first, or select a subset:
./Tools/import_simulator.sh nes n64 --build --device booted --restart
```

Delta must already be installed in the selected simulator. `--restart` ends its
running game and relaunches it to refresh a selected theme. Use a device UDID if
several simulators are booted, or `--dry-run` to inspect packages without changing
the simulator. Pass `--delta PATH` or `DELTA_DIR` for a different Delta checkout.

The workflow uses Bash 3.2+ and jq. It keeps the system's Xcode selection unchanged;
use `--xcode` or `DEVELOPER_DIR` to select an installation. The optional `--build`
flag invokes the Python authoring tool. Packages go through Delta's normal import
flow and their installed checksums are verified. Copying a package into Documents
alone does not register it.

Enable **Rive Controller Themes** in Delta's Experimental Features and select
**NES** or **N64** under Settings → Skins for the desired orientations. Physical
devices can import the same `.deltaskin` files through the skin picker or Open in Delta.

Delta's pinned submodule uses [dskuza/DeltaCore's `rive` branch](https://github.com/dskuza/DeltaCore/tree/rive).
Setup also recovers the exact N64 homebrew compatibility commits from Delta's
`Scripts/RiveDependencies`; its README includes provenance. The production preview
and native input tests live in Delta at `Extras/RiveControllerPreview`.

## Verify

```sh
python3 Tests/render_controllers.py nes
python3 Tests/render_controllers.py n64
python3 ../Delta/Extras/RiveControllerTests/run_tests.py --themes .
```

Pixel checks cover short-tap signal completion, idle recovery, stationary Reduced
Motion and transparent game openings; N64 also checks visible cap movement.
The companion preview tests cover native buttons, digital diagonals, fractional
analog movement, resting contact, both Z regions, fallback, lifecycle changes
and both landscape notch positions.

The diagnostic ROMs remain in Delta with their sources/licenses:
`Extras/NESInputTest/input-test.nes` and `Extras/N64InputTest/mimi-6126231.z64`.
Import them with `--rom nes --rom n64`. The NES Input Lab displays real emulator
press/release counts; mimi's live range view plots the actual N64 stick input.

## License

Sources and tools retain Delta's GPLv3 license in `COPYING`. Space Grotesk uses
the SIL Open Font License in `Assets/OFL.txt`. The saved default layout reference
contains placement metadata derived from Delta's bundled controller skins.
