# Authoring and verifying a theme

Run commands from the themes repository root unless a different working directory
is given. Runtime bindings are specified in `theme-contract.md`; these instructions
explain how to author and deliver artwork using this repository's current tools.

## Choose the source and system

Inspect the user's requested controls, visual direction and layouts. Choose a
compatible diagnostic ROM and input inventory. New visual layouts do not need
to reuse default controller positions or the samples' panel geometry.

| Example | Editable source of truth | Useful reference |
| --- | --- | --- |
| `nes/` | `Tools/generate_nes.py` | Digital NES controls and red circuit feedback |
| `n64/` | `Tools/generate_n64.py` | Continuous N64 stick, contact LEDs, pose timelines, constraints and routed signal packets |
| Shared authoring | `Tools/controller_scene.py` | RML primitives, typed model/default instance, Boolean conditions and numeric range helpers |
| Default geometry reference | `Assets/DefaultLayouts.json` and `Tools/default_layout.py` | Optional placement reference; independent of a Delta checkout |

Generated `scene.rml`, `info.json`, `rive.json` and, where used,
`circuit-layout.json` are checked-in authoring assets. For those examples, edit
the owning generator and regenerate the affected project. A new project may use
a different generator or maintain its RML directly; explicitly choose which
source owns geometry so later generation does not overwrite intentional edits.
Changes to shared helpers can affect several themes; inspect their generated diffs.

A new theme folder normally contains `scene.rml`, `rive.yaml`, `info.json` and
`rive.json`. The YAML name/export filename, manifest filename and packaging name
must agree. Copy only needed source files, choose a new identifier and update
names rather than accidentally shipping a renamed duplicate of an existing theme.
Fonts and other assets may live in `Assets/`; retain their licenses.

## Author the model and artwork together

1. Define each orientation's dimensions, native input regions and game opening.
   Use the same coordinates for the artboard, metadata and fallback. Test ergonomic
   reach and spacing; avoid relying on tiny labels or a hard-coded notch offset.
2. Declare the Boolean/Number properties the manifest will map. Author the named
   model's default instance. `Scene.finish()` is the existing pattern for this.
   `Scene.bind()`, `Scene.condition()` and `AnalogScene.numeric()` show numeric bindings,
   typed Boolean transition conditions and range conversion.
3. Bind each control to independent feedback. A press can change its rim,
   illumination, texture or pose; release must restore a clear idle state. Preserve
   chords and diagonals. A held Boolean is a state, not a repeated event; the host
   deduplicates unchanged values, so do not depend on per-frame press notifications.
4. For analog controls, bind X/Y continuously and invert the artwork's Y movement.
   Map −1…1 into a deliberate visual travel range. Add magnitude/contact effects
   only when their properties exist and the manifest maps them. If an entire
   analog module is scaled, scale its native frame and fallback cap consistently.
5. Implement Reduced Motion as a usable stationary state. Keep a held button
   identifiable; remove looping packets or oscillation. Handle the preference
   changing while a control remains held, as well as changing before a press.

Prefer Rive-native features when they serve the requested style:

| Feature | Practical use |
| --- | --- |
| Vector fills, gradients, strokes and feathering | Clear shells, colored rims, soft socket LEDs without bitmap glows |
| Independent state-machine layers | Simultaneous A/B, digital diagonals, multiple illuminated controls |
| Numeric data bindings / range converters | Continuous cap travel, axis rails, magnitude-based intensity |
| Joysticks with X/Y pose timelines | Two-axis authored motion; the N64 stick is a working example |
| Bones and translation constraints | Related parts following a cap or gimbal without manual duplication |
| Trim Paths and animation exit times | Traveling signal packets, with a complete short-tap pulse after native release |
| Native Rive clipping and groups | Isolating effects while keeping an embedded game aperture clear |

Choose effects for readability and interaction, not a checklist of features.
Keep object IDs unique in generated RML and references stable where practical.
RML property keys and type names are runtime-specific; inspect the installed
CLI's schema rather than guessing numeric keys for a new feature:

```sh
rive --version
rive schema DataBindContext
rive schema Node --bindable
rive docs --search "data binding"
```

Current samples are vector artwork without executable scripts. They export
with `--once` without a Rive account. If a task adds scripts, referenced assets
or other runtime requirements, check their export/loading support separately;
do not assume the current script-free build path handles them.

## Register a new theme with the tools

Existing sample names are hard-coded in several places. A new folder alone does
not make these tools discover it automatically:

- `Tools/build_themes.py`: add the new theme to accepted/default selections as
  appropriate. It compiles projects, generates fallback, renders picker PNGs and
  packages the ZIP. It currently assumes `Portrait`/`Landscape` artboard names,
  orientation-named PDFs/previews, `<ThemeName>.riv`, and `aPressed`/`upPressed`
  preview properties. Adapt those assumptions if your manifest uses other names;
  adding a new allowed name is not enough in that case.
- `Tools/FallbackArtwork.swift`: add the intended fallback treatment. It currently
  draws the two clear controllers, classifies N64 by `gameTypeIdentifier`, and
  reads `circuit-layout.json` for routes, headers and chips. Extend it for another
  style or system; custom layouts must update its fallback panel and aperture
  geometry as well as Rive artwork.
- The packager includes thumbstick cap assets declared in native `info.json`
  metadata. Generate every referenced cap PDF; the current N64 fallback emits
  `stick.pdf`. A new filename needs corresponding fallback generation.
- Delta's `Scripts/import-rive-themes.sh` defaults to `nes` and `n64`. Pass a
  new theme name explicitly; extend default selections only if intended.
  `Tools/import_simulator.sh` forwards explicit names to that command.
- For production integration checks, extend the companion Delta preview's theme
  choices/resources and its relevant tests. Its resources live in the themes repo
  through `RIVE_THEMES_ROOT`; app/renderer code stays in Delta.

Keep new registration changes focused and reviewable. Schema/binding extensions
that require host support belong in the Delta fork as well as the authoring tools.

## Compile, render and package

Examples below use existing themes; substitute your registered project and actual
property names for a new one. The builder consumes current sources; it does not
run generators automatically.

```sh
# Regenerate only when changing this example's owning generator.
python3 Tools/generate_nes.py
rive nes --verify
rive nes --once
python3 Tools/build_themes.py nes
```

Plain verification/export can run without a graphics session. The current PDF
fallback and packaging workflow requires macOS/Xcode; PNG renders and pixel
checks require a Metal-capable session. Python remains the authoring-tool language;
setup and simulator import entry points are executable Bash scripts. Select Xcode
with `DEVELOPER_DIR` or the workflow's `--xcode`, leaving the system default alone.

Inspect actual idle, pressed, held, released, diagonal and analog frames rather
than relying only on compilation:

```sh
rive nes --artboard=Portrait --advance=1 \
  --screenshot=/tmp/controller-idle.png
rive nes --data=aPressed=true --data=bPressed=true \
  --data=upPressed=true --data=rightPressed=true --advance=20 \
  --screenshot=/tmp/controller-chord.png
rive nes --data=aPressed=true --advance=6 \
  --data=aPressed=false --advance=100 --screenshot=/tmp/controller-released.png
rive n64 --data=stickX=0.35 --data=stickY=-0.6 \
  --data=stickContact=true --advance=10 --screenshot=/tmp/controller-stick.png
rive n64 --data=stickContact=true --advance=10 \
  --screenshot=/tmp/controller-center-contact.png
rive n64 --data=aPressed=true --data=reduceMotion=true \
  --advance=35 --screenshot=/tmp/controller-reduced.png
rive n64 --artboard=Landscape --advance=1 \
  --screenshot=/tmp/controller-landscape.png
```

The shipped pixel checks cover `nes` and `n64`:

```sh
python3 Tests/render_controllers.py nes
python3 Tests/render_controllers.py n64
```

Do not treat those checks as coverage for a new theme automatically. Adapt the
relevant visual invariants and test geometry when adding coverage: cap movement,
short-tap completion, eventual idle recovery, stationary Reduced Motion, and an
unpainted game aperture. Transparent material should also be inspected against
real emulated content; the CLI preview composites onto its own backdrop.

## Import and verify native gameplay

Use the companion Delta `rive` branch with its pinned forked DeltaCore. The
runtime package contract is independent of the CLI preview; both need to work.

```sh
./Tools/setup.sh
./Tools/import_simulator.sh nes n64 --device booted --restart
# Optional diagnostic ROMs, bundled with their provenance in Delta:
./Tools/import_simulator.sh nes --device booted --rom nes --restart
./Tools/import_simulator.sh n64 --device booted --rom n64 --restart
```

`--restart` ends the running Delta game. Use it when that interruption is within
the task's authorization. Select a UDID when several simulators are booted;
`--dry-run` validates and lists built packages without simulator changes.
Pass `--delta PATH` or `DELTA_DIR` for a non-sibling Delta checkout. Import uses
the normal app importer and verifies the installed package checksum. Copying a
file to Documents alone does not register a theme.

Enable Rive Controller Themes in Delta's Experimental Features and select the
skin for the target system and orientations. The NES Input Lab shows emulator
press/release counters and a directional dot. mimi's live range display shows
N64 analog movement; use the D-pad and A to select it. Keep diagnostic source,
licenses and compatibility details in Delta's `Extras/NESInputTest` and
`Extras/N64InputTest` rather than modifying ROM bytes to hide input problems.

For native parser/archive coverage:

```sh
python3 ../Delta/Extras/RiveControllerTests/run_tests.py --themes .
```

That runner currently enumerates the two controller projects; extend it to exercise a new
package. Add an actual input test or manual emulator check for new layouts:

- Every digital control, diagonal input, A/B chords and sustained holds.
- Fractional analog X/Y, both signs, full travel and return to zero; center
  contact must not introduce analog movement.
- Release on drag-off/cancel, background/resume, orientation and theme changes.
- Portrait plus landscape with the notch on either side, including fallback.
- Actual fallback usability when animation is disabled, and real picker images
  containing the new artwork rather than generic placeholders.

## Deliver and preserve work

The package contains `info.json`, `rive.json`, its `.riv`, fallback PDFs,
optional stick cap assets and rendered picker PNGs, with names matching metadata.
Keep generated `Dist/`, per-theme `build/`, caches and local captures ignored.
Commit editable sources, relevant tool updates, reference tests and asset licenses.
Do not force-add generated exports just to demonstrate a successful build.

Report the package's local path, build/import commands and the checks actually
performed. If the environment lacks Rive CLI, macOS, Metal or a compatible
simulator, distinguish source/metadata checks from pending visual or gameplay
verification. Use the user's requested branch/commit/publishing workflow; the
skill supplies technical guidance, not extra authorization for external actions.
