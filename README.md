# Rive controller themes

An experimental animated rendering layer for Delta skins, using RiveRuntime's
Swift Concurrency API. Native DeltaCore input handling continues to deliver
buttons, multitouch, stick movement, haptics and input mapping to the emulator.
Rive receives control state independently; emulation never waits for animation.

## Try it

The `Dist` directory contains two importable NES skins and their standalone `.riv`
files:

- `Template.deltaskin`: a complete starting point for another theme.
- `NeonCircuit.deltaskin`: graphite panels, feathered LED glows, a native NES
  D-pad, independent directional lights and reduced-motion press states.

Import a `.deltaskin` through Delta's usual skin import flow, enable **Rive
Controller Themes** under Experimental Features, and select the skin for NES.
Both portrait and landscape are included. Turn the feature off to compare the
native vector fallback. Existing skins need no changes.

Import `../NESInputTest/input-test.nes` as the game. Its display shows the inputs
actually received by the NES emulator, press/release counts in hexadecimal
(wrapping after FF), and a dot moved by directional input. The NES themes use a proper digital
D-pad with cardinal and diagonal input. `AnalogStickLab.riv` is a separate
animation reference for future systems with analog sticks; it is not part of
the NES controller skins.

## Standalone preview

Open `Preview/RiveControllerPreview.xcodeproj` and run **RiveControllerPreview**
on an iOS 17.4+ simulator. It uses the production loader, renderer, DeltaCore and
NESDeltaCore, and bundles the diagnostic ROM and both skins. No Delta account,
Rive login, or commercial ROM is needed. The **Themes** menu selects the theme,
toggles animation, and runs a simultaneous-input demonstration.

The preview uses DeltaCore's existing Metal video option. This avoids a legacy
OpenGL framebuffer crash observed when rotating the simulator.

From the repository root:

```sh
xcodebuild -project Extras/RiveControllerThemes/Preview/RiveControllerPreview.xcodeproj \
  -scheme RiveControllerPreview -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  CODE_SIGNING_ALLOWED=NO test
```

The preview project can be regenerated with `ruby Preview/create_project.rb`
(requires the `xcodeproj` Ruby gem installed with CocoaPods).

## Authoring and rebuilding

Requirements: macOS, Xcode command-line tools, Python 3 and Rive CLI 1.8.0+.
The ROM additionally needs `cc65` (`brew install cc65`).

```sh
python3 Extras/NESInputTest/build.py
python3 Extras/RiveControllerThemes/Tools/build_themes.py
python3 Extras/RiveControllerThemes/Tests/run_tests.py
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

Examples of local visual checks:

```sh
rive Extras/RiveControllerThemes/NeonCircuit --verify
rive Extras/RiveControllerThemes/NeonCircuit --artboard=Portrait \
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

Verified locally:

- DeltaCore device build and standalone preview simulator build.
- Production parser/archive tests for both sample packages, old skins, invalid
  metadata/assets, unsupported traits and normalized stick values.
- Every NES button and D-pad direction, diagonal input and release, switching themes,
  static fallback, portrait/landscape geometry and background/resume.
- Simultaneous A/B and diagonal state through the controller receiver mechanism.
- Rive CLI compilation and rendered idle/pressed/D-pad states; release returns
  pixel-for-pixel to the idle image.

Full Delta builds were attempted with both installed toolchains. Xcode 26.5
failed in the existing app icon asset catalog; Xcode 27 compiled the new Rive
sources but failed on existing `UIHinge`/`UIHingeInteraction` API references absent
from its SDK. The standalone preview isolates this work from those app build
requirements. Physical-device latency, thermals and power consumption still need
device testing before graduating the feature.
