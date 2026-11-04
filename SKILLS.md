# Developing Delta Rive themes with an AI assistant

Use [create-delta-rive-theme](.agents/skills/create-delta-rive-theme/SKILL.md)
to create or modify a controller theme in this repository. It covers the native
input contract, typed view-model bindings, custom layouts, Rive authoring,
packaging, previews, and emulator verification.

The skill uses the provider-neutral [Agent Skills format](https://agentskills.io/specification):
plain Markdown with `name` and `description` frontmatter, plus local references.
It does not require a particular model, editor, tool API, or account integration.
Automatic discovery and installation locations vary between assistants.
`AGENTS.md` points repository-aware assistants to the skill; for other tools,
attach the skill folder or explicitly ask the assistant to read it and its references.
Keep the references with `SKILL.md` when copying the skill into another tool.

A starting prompt:

> Read SKILLS.md and use the create-delta-rive-theme skill in this repository.
> Create an original N64 controller theme with a continuous analog stick,
> independent button feedback, Reduced Motion states, both phone orientations,
> native fallback artwork, and real picker previews. Choose a new visual style
> and ergonomic layout; the existing controllers are references, not a required
> design. Build the package, inspect its rendered states, and report which
> emulator input checks you could actually run.

For a smaller change, specify the theme, system, visual goal and desired layouts.
A purely digital system such as NES needs a D-pad, not an emulated analog stick.
If the assistant cannot run macOS/Metal tools, it can still author and inspect
sources; it should report the remaining rendering and emulator checks explicitly.

The skill's two focused references are:

- [Theme contract](.agents/skills/create-delta-rive-theme/references/theme-contract.md):
  view models, native inputs, Boolean/Number types, manifest examples, triggers,
  coordinate systems and package constraints.
- [Authoring workflow](.agents/skills/create-delta-rive-theme/references/authoring-workflow.md):
  source ownership, tool integration, useful Rive features and verification.
