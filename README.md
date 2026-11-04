# Rive controller themes

An experimental animated rendering layer for Delta skins, using RiveRuntime's
Swift Concurrency API. Native DeltaCore input handling continues to deliver
buttons, multitouch, stick movement, haptics and input mapping to the emulator.
Rive receives control state independently; emulation never waits for animation.

## Try it

The `Dist` directory contains three importable NES skins, two N64 skins, and their standalone `.riv`
files:

- `Template.deltaskin`: a complete starting point for another theme.
- `NeonCircuit.deltaskin`: graphite panels, feathered LED glows, a native NES
  D-pad, independent directional lights and reduced-motion press states.
- `CrystalNES.deltaskin`: the clear circuit-board style adapted to NES, with
  lightly red-tinted A/B caps and placement derived from Delta’s bundled NES skin.
  Portrait keeps Menu at the upper right; landscape uses diagonal A/B, bottom
  Select/Start and top-center Menu. Independent red LED and signal-path effects support diagonal and
  simultaneous input, with steady routes for Reduced Motion. Artwork stays
  unbranded, with safe-area layout and native vector fallback in both orientations.
- `Orbit.deltaskin`: a continuous N64 analog stick with a moving cap and feathered
  halo, magnitude-driven lighting, independent axis sectors, a separate D-pad,
  all four C-buttons, A/B/Z/L/R/Start, and native vector fallback artwork.
  Uses the original controller's button order and colors: green B above-left of
  blue A, yellow vector arrows in the C-button diamond, red Start in the middle,
  D-pad above the stick, L/R along the top and an accessible Z below the stick.
  Edge-to-edge representations opt into UIKit safe-area layout, keeping artwork,
  native touch targets and the game screen clear of the notch and home indicator
  in portrait and both landscape directions, including static fallback.
- `OrbitCrystal.deltaskin`: **Orbit: Crystal**, a smoked-clear N64 controller with
  visible circuit routes and chips, transparent button caps, colored socket LEDs,
  and moving signal packets from each control toward the game display. The analog
  module exposes independently moving X/Y sensor rails and a contact LED that
  lights even when a thumb rests at center. A quick tap's packet finishes traveling
  after input releases; held controls repeat independently. Reduced Motion uses
  steady illuminated routes. Both phone orientations respect device safe areas.
  Original N64 hues tint the clear caps: blue A, green B, yellow C buttons,
  red Start and neutral gray controls. Low-opacity fills retain the see-through
  material, with brighter colors supplied by the socket LEDs and signal pulses.
  Theme names appear in the skin picker only; the controller artwork is unbranded.
  Placement follows Delta’s bundled N64 skin: stick above the D-pad, C-buttons
  below A/B, center Start and top Menu. Matching Z buttons remain above L and R.
  Both Z regions send the same N64 input and illuminate together. Native touch
  handling unions held inputs, so lifting one Z leaves it held by the other.
  Landscape places Menu above the game screen and Start below it.
  `Tools/default_layout.py` reads `Assets/DefaultLayouts.json`, a saved reference
  from Delta’s bundled default phone skins, so the reference
  positions are explicit; UIKit supplies the notch and home indicator insets.

Import a `.deltaskin` through Delta's usual skin import flow, enable **Rive
Controller Themes** under Experimental Features, and select the skin for its system.
Both portrait and landscape are included. The skin picker uses actual Rive
artboard renders with lit A and D-pad LEDs, including the analog cap.
Turn the feature off to compare the
native vector fallback. Existing skins need no changes.

Import `../Delta/Extras/NESInputTest/input-test.nes` as the game. Its display shows the inputs
actually received by the NES emulator, press/release counts in hexadecimal
(wrapping after FF), and a dot moved by directional input. The NES themes use a proper digital
D-pad with cardinal and diagonal input. `AnalogStickLab.riv` is a separate
animation reference for future systems with analog sticks; it is not part of
the NES controller skins. Orbit is the complete N64 example built from that idea.

For N64, import `../Delta/Extras/N64InputTest/mimi-6126231.z64`, select **Orbit N64** for
portrait and landscape (or select **Orbit: Crystal**), and open mimi's **live range** view using the D-pad and A.
Drag Orbit's stick to compare actual emulated X/Y movement with its vector cap
and glow. Small movements retain fractional values; releasing returns to center.
mimi's provenance, checksum and credits are in `../Delta/Extras/N64InputTest/README.md`.

## App integration and preview

The app and integration harness live in [dskuza/Delta](https://github.com/dskuza/Delta/tree/rive)
on its `rive` branch. Its DeltaCore submodule uses [dskuza/DeltaCore](https://github.com/dskuza/DeltaCore/tree/rive).
Keep the repositories as siblings, or pass explicit paths to their tools:

```text
workspace/
  Delta/                # rive
  Delta-rive-themes/    # main
```

Run `./Tools/setup.sh` to connect the checkouts and resolve dependencies.
The production renderer, native-input UI tests and emulator preview remain in
Delta at `Extras/RiveControllerPreview`. See Delta's `Docs/RiveDevelopment.md`.
Theme compilation and pixel tests here do not need the Delta checkout.

## Authoring and rebuilding

Requirements: macOS with Metal, Xcode command-line tools, Python 3 and Rive CLI 1.8.0+.
The ROM additionally needs `cc65` (`brew install cc65`).

```sh
python3 ../Delta/Extras/NESInputTest/build.py
python3 Tools/build_themes.py
python3 ../Delta/Extras/RiveControllerTests/run_tests.py --themes .
```

`scene.rml` and `rive.yaml` are editable Rive authoring sources. The scenes contain
no scripts, raster images, or external runtime assets. Text uses the bundled OFL
Space Grotesk font. `--once` exports these script-free files without account
signing. The font license is in `Assets/OFL.txt`.

`Tools/generate_themes.py` regenerates RML, `info.json` and `rive.json` from one
coordinate definition. Run it only when changing the generator; it overwrites
hand edits to those generated files. `build_themes.py` compiles the current RML,
creates vector PDF fallback artwork, and packages the exports into `Dist`.
The fallback PDFs preserve a transparent landscape game aperture.

Orbit's coordinate source is `Tools/generate_orbit.py`. To rebuild only Orbit:

```sh
python3 Tools/generate_orbit.py
python3 Tools/build_themes.py Orbit
```

Crystal's source is `Tools/generate_crystal.py`. Its generated `circuit-layout.json`
also supplies the native fallback's traces. To rebuild and check its actual rendered effects:

```sh
python3 Tools/generate_crystal.py
python3 Tools/build_themes.py OrbitCrystal
python3 Tests/render_crystal.py
```

Crystal uses Rive Joysticks to scrub two bone-position pose timelines, a translation
constraint to attach its cap, and independent state-machine layers for LEDs and
Trim Path signal packets. These are authored Rive features, without executable
scripts or account signing. Its effects visualize controller inputs, not emulator
acknowledgements or game-specific events. The game always receives input immediately.

The NES counterpart reuses Crystal's material, button and signal authoring helpers,
with its own digital controls and layout. It has no analog bindings:

```sh
python3 Tools/generate_crystal_nes.py
python3 Tools/build_themes.py CrystalNES
python3 Tests/render_crystal.py CrystalNES
```

Examples of local visual checks:

```sh
rive NeonCircuit --verify
rive NeonCircuit --artboard=Portrait \
  --data=aPressed=true --data=bPressed=true \
  --data=upPressed=true --data=rightPressed=true \
  --advance=20 --screenshot=/tmp/neon-active.png
```

A Metal-capable session is required to render screenshots. Plain verification
and `.riv` export do not require a graphics session.

## Theme contract (version 1)

A theme remains a normal `.deltaskin` ZIP. `info.json` supplies identity, system,
representations, screen placement, native hit targets and fallback assets.
An optional `rive.json` supplies the animation configuration:

```json
{
  "schemaVersion": 1,
  "representations": {
    "iphone-standard-portrait": {
      "file": "MyController.riv",
      "artboard": "Portrait",
      "stateMachine": "Controller",
      "viewModel": "Controller",
      "buttons": { "a": "aPressed", "b": "bPressed" },
      "sticks": [{
        "up": "up", "down": "down", "left": "left", "right": "right",
        "x": "stickX", "y": "stickY", "active": "stickActive"
      }],
      "reduceMotion": "reduceMotion"
    }
  }
}
```

- Representation keys use DeltaCore's resolved `Traits.description`:
  `device-displayType-orientation`. Native trait fallback happens first.
- Artboard dimensions and artwork coordinates must match that representation's
  `mappingSize`. The view uses `.fill` so artwork and normalized native hit
  regions receive the same transform. Keep game apertures transparent.
- `buttons` maps original **skin input names** to Boolean view model paths. Paths
  may refer to nested view models, using `/`. Names are not hard-coded in Swift.
- `sticks` is optional. Its directional names identify native inputs; numeric
  property paths receive signed X/Y in −1…1, with positive Y pointing up. The
  optional Boolean `active` means nonzero displacement, including diagonal input.
  An optional numeric `magnitude` path receives the vector length clamped to 0…1,
  for effects such as glow intensity that increases with stick displacement.
- A stick's optional `contact` Boolean path receives physical thumb contact,
  independently of displacement. It can light the cap while input remains zero.
  Contact is not pressure, is cleared on touch end/cancellation and removal of the
  native control, and is initialized when an animated renderer attaches.
- `reduceMotion` is an optional Boolean path receiving the system accessibility
  preference. The samples remove button travel in reduced-motion states.
- The named view model needs an authored default instance. All configured property
  paths and types are checked against that instance before artwork is replaced.
- `.riv` assets must be root-level archive members. The loader bounds manifest
  and asset sizes and extracts in memory. Malformed imports are rejected; runtime
  loading/binding failures leave the native fallback usable and are logged under
  `RiveControllerSkins`.
- Static fallback images remain required for sizing, selection previews and
  disabled/unsupported animation. A native thumbstick still needs its ordinary
  `thumbstick` asset declaration, even though its artwork is hidden while Rive
  draws the cap.
- An `info.json` representation can set `"respectsSafeArea": true` to fit the
  complete controller inside the current UIKit safe-area frame. All native hit
  targets, fallback artwork, Rive artwork and embedded game screens share that
  transform; notch padding is not baked into the Rive scene. Omitted/false keeps
  the existing full-bounds layout. Orbit enables it for `edgeToEdge` only.

The first version covers controller placement on ordinary phone layouts and
compatible tablet fallbacks. Split-view keyboard controllers use static artwork.
It does not forward Rive pointer events to gameplay or mirror hardware controllers.

## Implementation and verification

DeltaCore exposes `ControllerSkinRendering`; it owns the optional view and sends
raw controller-state snapshots through the existing receiver mechanism, including
sustained inputs. Delta owns the Rive dependency, worker, loaded file, explicit
view model binding and lifecycle coordinator. The coordinator cancels obsolete
loads, caches a worker per scene, checks the selected skin/traits before attaching,
pauses on inactivity, and retains static artwork until initialization succeeds.

Changes to the Rive runtime are pinned at **6.29.0**. The companion DeltaCore
changes are on branch `codex/rive-controller-rendering`; publish that branch and
make its commits available before sharing the parent repository's submodule
reference with another checkout.
N64 homebrew compatibility is on N64DeltaCore's `codex/orbit-homebrew-support`
branch and its nested Mupen64Plus core's `codex/mimi-homebrew-compatibility`
branch. Publish those companion branches as well before sharing their references.

Verified locally:

- Full Delta Debug device build with Xcode 27.2 (27B52), iOS 27.2 SDK,
  and code signing disabled.
- Full Delta simulator build and launch on an iPhone 18 Pro running iOS 27.0,
  with the NES diagnostic ROM and Neon Circuit selected for both orientations.
- DeltaCore device build and standalone preview simulator build.
- Production parser/archive tests for both sample packages, old skins, invalid
  metadata/assets, unsupported traits and normalized stick values.
- Every NES button and D-pad direction, diagonal input and release, switching themes,
  static fallback, portrait/landscape geometry and background/resume.
- Orbit N64 native touch gestures: fractional analog values, full left/down
  diagonal, release to center, every digital control, static fallback, rotation
  and background/resume, with mimi running in the standalone preview.
- Crystal's complete N64 controls, resting contact without movement, simultaneous
  buttons and analog input, static fallback, and both landscape safe areas.
- Crystal's rendered pixels: visible XY cap travel, a short tap's complete packet,
  return to idle, stationary Reduced Motion effects and a transparent game aperture.
- Crystal NES: all nine controls, native digital diagonals, simultaneous A/B and
  directional input, static fallback, background/resume, and both landscape safe
  areas. The same rendered-effect checks cover its signal packets and game opening.
- mimi boot and display after the focused PI DMA, cached-code alias and VI
  framebuffer address fixes; host-side PI/VI register regression checks pass.
- Simultaneous A/B and diagonal state through the controller receiver mechanism.
- Rive CLI compilation and rendered idle/pressed/D-pad states; release returns
  pixel-for-pixel to the idle image.

Use Xcode 27.1 or later for the full Delta app: its existing
`UIHinge`/`UIHingeInteraction` references require the iOS 27.1 SDK. The full
build passes with Xcode 27.2. Xcode 26.5 failed in the app icon asset catalog,
and Xcode 27.0 lacks the required UIKit APIs. The standalone preview also
builds with Xcode 26.5. Physical-device latency, thermals and power consumption
still need device testing before graduating the feature.

To select Xcode for a command without changing the system-wide default, prefix
`xcodebuild` and `xcrun simctl` commands with
`DEVELOPER_DIR=/Applications/Xcode-27.2.0.app/Contents/Developer`.

Picker artwork is optional: each `rive.json` representation can name a PNG in
`preview`. The builder renders `portrait-preview.png` and `landscape-preview.png`
from the same artboards it packages. Delta uses these images in both skin pickers,
independently of whether animation is enabled. Older skins, missing images and
unreadable previews retain the native fallback. Preview extraction stays in memory
and checks the filename, PNG header, file size and decoded dimensions.

## Generated files

`Dist/`, per-theme `build/` folders, caches, recordings and local settings are
ignored by Git. Run `python3 Tools/build_themes.py` to recreate all importable
skins and their previews. Built files remain available locally for testing and
release distribution; source `.riv` files outside `Dist/` remain eligible for Git.

Use `./Tools/import_simulator.sh --device booted --restart` to import built
packages into an installed Delta simulator app. Add `--build` to rebuild first.
The command uses Delta's normal skin importer; it does not edit the database.

## License and history

Theme sources and tools retain Delta's GPLv3 license; see `COPYING`. Space
Grotesk retains its SIL Open Font License in `Assets/OFL.txt`. The layout
reference contains placement metadata derived from Delta's bundled skins.
The repository history was extracted from Delta's `Extras/RiveControllerThemes`
with `git subtree split`, retaining the original theme authors and commit messages.
App-only preview and archive tests moved back to Delta; their history remains
available here before the repository split.
