---
name: create-delta-rive-theme
description: Create or modify Delta controller themes using Rive, including native input layouts, typed view-model bindings, animations, fallback artwork, packaging, previews and emulator checks.
---

# Create a Delta Rive controller theme

Create a playable `.deltaskin` package with editable authoring sources. Work from
the user's system, visual direction and layout requirements. Original layouts
are supported: default Delta positions and the current clear circuit-board
appearance are useful examples, not requirements.

## Read the relevant contract

Read [theme-contract.md](references/theme-contract.md) before changing native
inputs, view models, manifests or layout metadata. It specifies which values
Delta supplies, their types, and what the runtime cannot currently drive.
Read [authoring-workflow.md](references/authoring-workflow.md) for source ownership,
RML helpers, build registration and verification commands. Commands there run
from the theme repository root, unless stated otherwise.

## Working approach

- Inspect a working digital or analog example and choose the source of truth
  before editing. Existing generated RML and JSON can be overwritten by their
  generators; update the owning generator when working on those examples.
- Make a new identity for a new theme; retain identity for an intentional update.
  Establish its native control inventory and both orientation layouts before
  adding effects. Use one geometry definition for artwork, hit targets, screens
  and fallback images so interaction matches appearance.
- Create the named Rive view model and its authored default instance. Bind a
  state machine explicitly to its Boolean/Number properties. Property names are
  chosen by the theme and mapped in `rive.json`; they are not Swift constants.
- Keep gameplay in native DeltaCore controls. Rive receives state for visual
  feedback; its pointer listeners, animation completion and scripts do not
  deliver emulator input. Prefer independent layers or bindings so chords and
  diagonals can appear simultaneously.
- Add continuous numeric stick movement for analog systems, and distinguish
  displacement from physical contact. Implement useful stationary Reduced
  Motion feedback. Preserve input correctness regardless of visual effects.
- Register a new theme in the actual build/fallback/import/preview tools as
  needed. Their current sample lists and classifications are not automatic
  discovery. Build real picker images and usable native fallback artwork.
- Verify compilation, visible states and package integrity. When a compatible
  Delta simulator is available, verify actual native input with a diagnostic
  ROM, including release/cancellation and safe areas in both landscape directions.
  State any checks the environment cannot run instead of claiming success.

## Completion

Deliver the editable sources and a reproducible route to the local package.
Summarize the system and inputs, the important bindings and effects, build/import
commands, verification performed and any limitations. Follow the user's existing
branch and commit conventions. The skill itself does not authorize publishing,
installing software or interrupting an unrelated running game.
