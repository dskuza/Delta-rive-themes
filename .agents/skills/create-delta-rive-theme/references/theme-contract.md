# Delta Rive theme contract, schema version 1

This contract describes the `rive` branches of `dskuza/Delta` and
`dskuza/DeltaCore`, with RiveRuntime pinned at 6.29.0. When changing the contract,
check the current implementation rather than assuming a sample's behavior is an
API guarantee:

- `Delta/Controller Themes/RiveControllerSkinManifest.swift`: manifest validation.
- `Delta/Controller Themes/RiveControllerSkinRenderer.swift`: values and types.
- `Delta/Controller Themes/RiveControllerSkinArchive.swift`: archive loading.
- `Delta/Database/Model/Human/ControllerSkin.swift`: picker preview decoding.
- DeltaCore's `Model/ControllerSkin.swift` and `UI/Controller`: native geometry/input.

These are paths inside the companion Delta checkout, normally `../Delta`.

## Two files, two responsibilities

A `.deltaskin` is a ZIP. `info.json` identifies the theme/system and supplies the
native controller representations, control hit targets, screen frames and fallback
assets. `rive.json` maps those input names to Rive artwork and view-model properties.

The native controls own touches, multitouch, input values, haptics and emulator
mapping. The Rive view is a visual overlay with gameplay pointer handling disabled.
Animations must not gate, delay or replace native input. Visual signals traveling
to the display are decorative input feedback, not emulator acknowledgements.

## Rive objects and default state

The samples use these names, but other names work when the manifest matches:

| Object | Sample name | Requirement |
| --- | --- | --- |
| Artboards | `Portrait`, `Landscape` | One named artboard for each animated representation; dimensions match native `mappingSize` |
| State machine | `Controller` | Exists on the chosen artboard and consumes view-model bindings |
| View model | `Controller` | Exists in the file with the exact mapped property names and types |
| Default instance | `Default` | Authored default instance of that view model, initialized with false Booleans and zero Numbers |

The host loads the file through the Concurrency API, creates the selected
artboard and named view model's **default instance**, checks every configured
property using its expected type, and explicitly binds the instance when creating
the state machine. Merely declaring traditional state-machine inputs named
`aPressed` or `stickX` is insufficient.

In the RML examples, `Scene.finish()` authors `ViewModel`,
`ViewModelPropertyBoolean`/`ViewModelPropertyNumber`, a default
`ViewModelInstance`, and the corresponding instance values. Its
`defaultInstanceId` points to that instance. Artboards declare `viewModelId` and
`viewModelInstanceId`. Reuse that pattern rather than inventing a different
initialization mechanism.

## Values provided by Delta

Property paths are chosen by the theme. The following names are conventions,
not compulsory spellings. Paths may traverse nested view models with `/`.

| Manifest field | Rive type / conventional property | Host value |
| --- | --- | --- |
| `buttons.a` | Boolean `aPressed` | True while native input `a` has value greater than zero; false otherwise |
| `buttons.<input>` | Boolean `<input>Pressed` | Same rule for any mapped native input name |
| `sticks[].x` | Number `stickX` | `right - left`, each side clamped to 0…1; result −1…1 |
| `sticks[].y` | Number `stickY` | `up - down`, each side clamped to 0…1; result −1…1, positive upward |
| `sticks[].active` | Boolean `stickActive` | Optional: X or Y is nonzero; this means displacement, not contact |
| `sticks[].magnitude` | Number `stickMagnitude` | Optional: `min(hypot(x, y), 1)`, range 0…1 |
| `sticks[].contact` | Boolean `stickContact` | Optional: a matching native thumbstick reports physical contact, even at center |
| `reduceMotion` | Boolean `reduceMotion` | Optional: the system Reduce Motion preference |

Missing native inputs produce false/zero values. Nonfinite stick components are
handled as zero. Opposing directions cancel. A full diagonal can have both
axes at ±1; only the reported magnitude is clamped to 1. Do not normalize the
axes to a unit circle in the artwork unless the visual design specifically needs it.
Map positive host Y to negative artwork Y when moving a cap in top-left coordinates.

Contact is not pressure, hover or displacement. It clears on touch end or
cancellation. `contact` works with the native thumbstick's directional input
names; adding that property to an unrelated button does not create touch sensing.

Every configured output path must be unique across all buttons, all sticks and
Reduce Motion in one representation. To draw two Z buttons, declare two native
regions with `inputs: ["z"]`, map `z` once to `zPressed`, then bind both visual
assemblies to that property. Do not duplicate output paths to simulate OR logic.

### Native input names

Use the target core's actual raw input names, with their exact case. A label on
the artwork does not define a new emulator input.

- NES: `up`, `down`, `left`, `right`, `a`, `b`, `select`, `start`.
- N64: `up`, `down`, `left`, `right`, `a`, `b`, `l`, `r`, `z`, `start`,
  `cUp`, `cDown`, `cLeft`, `cRight`, and `analogStickUp`, `analogStickDown`,
  `analogStickLeft`, `analogStickRight`.
- `menu` is a Delta app action, not a ROM button. Keep an accessible route to it.
- For other systems, inspect their core input definitions or bundled standard
  `info.json` in Delta before choosing names. A new theme alone cannot add a new
  system, input source or emulator feature.

D-pad directions may be true together. N64's digital D-pad and analog stick are
separate input groups. Boolean analog-direction bindings can drive sector lights,
but use numeric X/Y for the cap so small movements remain continuous.

### Triggers and events

**The current loader does not call Rive Trigger properties or legacy trigger
inputs.** It supplies Boolean and Number view-model values, plus the named
accessibility preference. An arbitrary `trigger` or `events` field is not a
supported extension to `rive.json`.

For a press animation, use a state transition conditioned on `aPressed == true`,
and return/re-arm when false. For an effect that must finish after a quick tap,
let a visual animation reach its exit time before returning to idle. Native
release still reaches the emulator immediately. Use separate layers for each
button and direction instead of one mutually exclusive pressed state.

The current samples have no executable Rive scripts. Schema v1 supplies no
pressure, velocity, ROM state, rumble, scoring, display-pixel or audio telemetry,
and does not promise mirroring of external hardware controllers. Such behavior
needs a deliberate host/runtime extension, not invented view-model properties.

## Example `rive.json` representation

This is a complete manifest with **one** N64 representation. Add entries for all
other native representations that should animate; adjust names to your own file.
The named model needs every Boolean and Number referenced below.

```json
{
  "schemaVersion": 1,
  "representations": {
    "iphone-edgeToEdge-portrait": {
      "file": "MyController.riv",
      "artboard": "Portrait",
      "stateMachine": "Controller",
      "viewModel": "Controller",
      "buttons": {
        "up": "upPressed",
        "down": "downPressed",
        "left": "leftPressed",
        "right": "rightPressed",
        "a": "aPressed",
        "b": "bPressed",
        "l": "lPressed",
        "r": "rPressed",
        "z": "zPressed",
        "start": "startPressed",
        "menu": "menuPressed",
        "cUp": "cUpPressed",
        "cDown": "cDownPressed",
        "cLeft": "cLeftPressed",
        "cRight": "cRightPressed"
      },
      "sticks": [{
        "up": "analogStickUp",
        "down": "analogStickDown",
        "left": "analogStickLeft",
        "right": "analogStickRight",
        "x": "stickX",
        "y": "stickY",
        "active": "stickActive",
        "magnitude": "stickMagnitude",
        "contact": "stickContact"
      }],
      "reduceMotion": "reduceMotion",
      "preview": "portrait-preview.png"
    }
  }
}
```

For NES, omit `sticks` and its model properties, omit N64-only buttons, and add
`select: selectPressed`. The digital examples already provide complete manifests.
Names such as `analogStickUpPressed` are optional visual-sector Booleans; add
explicit `buttons` mappings if you use them, as Orbit does.

Representation keys are the resolved native traits' `description`, including
case: for example `iphone-standard-portrait`, `iphone-standard-landscape`,
`iphone-edgeToEdge-portrait`, `iphone-edgeToEdge-landscape`. Native fallback
resolves first; provide an exact matching animated entry for each resolved
representation you intend to animate. Split-view currently uses static artwork.

## Native layout, coordinates and fallback assets

Use a unique reverse-domain `info.json.identifier` for a new theme, and the target
`gameTypeIdentifier` (`com.rileytestut.delta.game.nes` or
`com.rileytestut.delta.game.n64`). Preserve identifiers for intentional updates.
Custom positions, artboard dimensions and visual treatments are allowed.

Each native representation contains `mappingSize`, `assets`, and `items`:

- Geometry uses artwork units in top-left coordinates: X rightward, Y downward.
  Artboard dimensions must equal `mappingSize`. Rive uses fill fitting; mismatches
  distort artwork relative to native hit targets.
- A button item has an `inputs` array such as `["a"]`, plus `frame` with
  `x`, `y`, `width`, `height`. Optional `extendedEdges` enlarge its hit region;
  `mask` can be `circle` or `rectangle`. Avoid overlapping controls accidentally.
- A digital D-pad has `inputs: {"up":"up","down":"down","left":"left","right":"right"}`
  and a frame. It does not have a `thumbstick` declaration.
- An analog item uses the same directional dictionary shape, with the system's
  analog names, **and** `thumbstick: {"name":"stick.pdf","width":53,"height":53}`
  (example dimensions). Without that explicit asset name and size, the native
  control becomes a digital D-pad. The normal cap asset is still required even
  when Rive draws the visible moving cap.
- `assets.resizable` names the representation's fallback PDF in the ZIP.
  Match its dimensions and controls to the Rive representation. Fallback must
  remain usable when animation is disabled, unsupported or fails to load.
- For a screen inside the controller, provide `screens[].outputFrame` and leave
  that aperture transparent in **both** Rive and fallback artwork. Do not draw
  shell fills, trace paths, hidden shapes or feather tails over the game opening.
- `respectsSafeArea: true` opts a representation into UIKit safe-area layout.
  Artwork, controls and embedded screens share the transform. Keep the notch and
  home indicator out of baked-in offsets; inspect portrait and both landscape
  rotations. Existing examples opt `edgeToEdge` in and retain standard behavior.

Keep visual cap travel distinct from native input normalization. Changing its
pixel travel must not change the signed host input values. Use generous reachable
controls, readable labels and a clear distinction between digital and analog input.

## Package and validation limits

Use root-level archive filenames for `.riv` assets and PNG previews. `.riv`
filenames are validated as basenames with a `.riv` extension; previews likewise
use `.png`. Keep referenced fallback/cap assets in the package too.

Current limits: schema version 1, 1…64 representations, at most 64 button mappings
and 4 sticks per representation. Property paths are nonempty, at most 256 characters,
and cannot contain empty `/` segments. The archive reader caps `rive.json` at
256 KiB, each Rive asset at 8 MiB, and unique Rive assets together at 32 MiB.
It checks the `RIVE` file header. Preview extraction is limited to 2 MiB per PNG;
the app accepts positive dimensions up to 4096 per side and 4,194,304 total pixels.

Archive/manifest errors reject import. A later animation-loading or binding error
leaves native fallback usable; inspect Delta's `RiveControllerSkins` log category.
Missing/unreadable picker previews fall back to native preview rendering. A
successful compile alone does not prove that property types, hit targets, game
transparency or emulator input are correct.
