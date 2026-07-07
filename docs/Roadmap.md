# PPT Master SUSTech Enhancement Roadmap

> Last updated: 2026-07-07
> Current release line: `r3.1.0-v0.4.0`
> Upstream baseline: `hugohe3/ppt-master@v3.1.0`
> Tracked upstream range: `v3.1.0..c2cb78ad997b41d16cefe083831d62571ab9f741`

## Purpose

This file is the long-lived inventory for the SUSTech-enhanced `ppt-master` line.

It has two jobs:

1. Record the functional changes that distinguish the SUSTech-enhanced source from the upstream skill.
2. Serve as the guard checklist for future upstream fusions and version updates so local enhancements are not lost.

Whenever version metadata changes, observable behavior changes, or upstream code is fused again, update this file in the same change set.

## Current Layering Model

| Layer | Meaning | Current State |
|---|---|---|
| Baseline | Official upstream release tag used as the release base | `v3.1.0` / `b8808a3a17377ea4e7fd79bdad096bab613f86b9` |
| Tracking | Upstream main commits after the baseline that have also been absorbed | `c2cb78ad997b41d16cefe083831d62571ab9f741` / fixed cutoff for this fusion |
| Overlay | SUSTech local behavior, release identity, templates, and workflow extensions | Preserved on top of the baseline and tracking patchset |

Rule of thumb:

- `RELEASE_META.json.upstream.commit` records the baseline tag commit.
- `RELEASE_META.json.upstream.tracked_commit` records the extra upstream main cutoff.
- SUSTech-only capabilities are treated as overlay and must be checked explicitly during each upstream fusion.

## SUSTech Enhancement Inventory

### 1. Release Identity and Distribution

SUSTech maintains a versioned release identity independent from the upstream repository layout.

Key files:

- `VERSION`
- `RELEASE_META.json`
- `README.md`
- `docs/README.md`

Current rules:

- Version format is `r<upstream-version>-v<local-version>`.
- Current version is `r3.1.0-v0.4.0`.

Fusion guard:

- Keep `.env.example` and `requirements.txt` aligned with the recorded release identity.
- Keep `VERSION`, `RELEASE_META.json`, README files, release notes, and this roadmap aligned.

### 2. Support Files

The release keeps support files in the skill root:

- `.env.example`
- `requirements.txt`

Current rules:

- Their basis is recorded in `RELEASE_META.json.support_files`.

Fusion guard:

- After upstream dependency changes, compare upstream support files against local copies.
- Preserve the SUSTech headers and documented support-file basis.
- If support-file behavior changes, update this roadmap.

### 3. Live Preview Editing Boundary

SUSTech keeps compatible layout diagnostics while upstream v3.1 direct editing remains the source of truth.

Key files:

- `workflows/live-preview.md`
- `scripts/svg_editor/server.py`
- `scripts/svg_editor/static/app.js`
- `scripts/svg_editor/static/index.html`
- `scripts/svg_editor/static/style.css`

Preserved local capabilities:

- static `layout_quality` diagnostics through `scripts/svg_quality_checker.py`
- optional browser geometry probe through `scripts/svg_layout_probe.py`
- annotation remains available for changes requiring AI judgment

Upstream v3.1 capabilities that must also stay present:

- project-level `.live_preview.lock`
- slide/cache mechanism
- slide polling
- reload banner
- warning banner
- trilingual UI including Japanese strings
- slide navigation toolbar
- staged direct SVG edits (`/api/slide/<name>/edit`, undo, save-all)
- drag-to-move and arrow-key nudge through staged direct edit
- geometry resize through direct-edit controls
- overlap picker
- free-port handling via `server_common.py`

Fusion guard:

- Do not let local aids override upstream direct-edit behavior.
- Keep deterministic drag / resize / nudge on upstream staged direct-edit semantics.
- Keep annotation available for changes that need AI judgment, rewriting, layout reasoning, or broad design context.
- Do not make the old `ppt_text_normalize` review workspace a release blocker.
- Verify both API smoke and browser interaction when this area changes.

### 4. Template Creation Audit Lock and Validation

SUSTech adds a stricter `/create-template` audit flow.

Key files:

- `workflows/create-template.md`
- `references/template-brief-confirmation.md`
- `scripts/template_brief_lock.py`
- `scripts/template_quality_checker.py`
- `scripts/template_preview.py`
- `scripts/template_import/`
- `scripts/pptx_template_import.py`
- `scripts/pptx_to_svg.py`
- `scripts/pptx_to_svg/`

Current rules:

- `brief_lock.json` is a SUSTech create-template audit lock.
- New `/create-template` outputs must write `brief_lock.json`.
- `template_quality_checker.py --require-brief-lock` is the strict gate for new SUSTech-created templates.
- Default template quality checking allows missing `brief_lock.json` for upstream or legacy templates.
- `design_spec.md` YAML frontmatter is the primary metadata source for template discovery and registration.

Fusion guard:

- Do not make `brief_lock.json` a universal hard dependency for all upstream templates.
- Do not remove strict mode for new SUSTech templates.
- Preserve template preview feedback before registration.

### 5. Brand / Layout / Deck Template Model

The current template model follows the upstream `brand / layout / deck` structure while preserving SUSTech assets.

Key directories:

- `templates/brands/`
- `templates/layouts/`
- `templates/decks/`
- `templates/icons/`

Current state:

- `templates/layouts/` keeps only upstream layout presets:
  - `academic_defense`
  - `ai_ops`
  - `government_blue`
  - `government_red`
  - `medical_university`
  - `pixel_retro`
  - `psychology_attachment`
- `sustech_academic_official` is maintained as a deck under `templates/decks/`.
- Brand-like historical layouts have been cleaned up.
- SUSTech and organization templates should use deck mode unless a real structural layout preset is intended.

Fusion guard:

- Do not reintroduce cleaned legacy brand layouts into `templates/layouts/`.
- Keep `sustech_academic_official` as a deck.
- Rebuild and validate `templates/brands/brands_index.json`, `templates/layouts/layouts_index.json`, and `templates/decks/decks_index.json` after template changes.

### 6. Local Template and Icon Assets

SUSTech keeps reusable visual assets in addition to upstream assets.

Important preserved assets:

- `templates/icons/chunk/`
- `templates/icons/chunk-filled/`
- SUSTech deck assets
- organization deck assets

Upstream assets retained:

- `templates/icons/phosphor-duotone/`
- `templates/icons/simple-icons/`
- `templates/icons/tabler-filled/`
- `templates/icons/tabler-outline/`
- chart templates and indexes

Fusion guard:

- Take the asset union unless a user explicitly confirms cleanup.
- Do not overwrite SUSTech-specific decks or icon sets with upstream-only copies.
- Keep JSON indexes valid.

### 7. Post-v3.1.0 Tracked Additions

The SUSTech line currently includes selected upstream `main` changes after the `v3.1.0` tag.

Tracked cutoff:

- `c2cb78ad997b41d16cefe083831d62571ab9f741`
- fixed cutoff for the `r3.1.0-v0.4.0` fusion

Absorbed skill-root changes:

- v3.1 prompt, workflow, source-intake, Confirm UI, and live-preview architecture
- native PPTX object/export improvements including opt-in tables/charts
- chart workbook generation dependency recorded through `XlsxWriter>=3.0.0`
- native chart negative-value point-color fix
- Confirm UI custom prompt notes for image strategy
- URL-encoded visual-review slide fetch for non-ASCII names
- update-path docs and `update_repo.py` hardening

Fusion guard:

- Treat tracked post-tag commits as upstream tracking, not as part of the formal baseline tag.
- Keep `RELEASE_META.json.upstream.tracked_*` fields current when the tracked cutoff changes.

### 8. Built-in PPT Text Normalize Safe MVP

SUSTech now treats `scripts/ppt_text_normalize/` as a built-in repo capability with a conservative Safe MVP source command surface.

Key files:

- `scripts/ppt_text_normalize/scan.py`
- `scripts/ppt_text_normalize/apply.py`
- `scripts/docs/ppt-text-normalize.md`
- `scripts/ppt_text_normalize/README.md`
- `scripts/ppt_text_normalize/CONTEXT.md`
- `scripts/ppt_text_normalize/tests/`

Current rules:

- The public command surface for `r3.1.0-v0.4.0` is `scan` / `apply`.
- Safe MVP semantics include Object Slot matching, hero freeze, weak-canonical restraint, safe field gating, report output, and OOXML namespace-preserving PPTX writes.
- Review workspace / browser panel / reviewed-rules assets remain in source but are not advertised as active release capabilities until separately revalidated.

Fusion guard:

- Do not describe review-gate expansion as shipped until the commands and browser flow are reverified against the current upstream editor.
- Keep `scan` / `apply` semantics aligned with `scripts/docs/ppt-text-normalize.md`, `scripts/ppt_text_normalize/README.md`, and release notes.
- Preserve the OOXML namespace-preservation rule and regression coverage when this module changes.

## Maintenance Rules

Update this roadmap when any of the following happens:

1. A release version is bumped.
2. `RELEASE_META.json` upstream baseline or tracked cutoff changes.
3. Distribution content rules change.
4. `SKILL.md`, `workflows/`, `references/`, `scripts/`, or `templates/` behavior changes in a way users or agents can observe.
5. Upstream code is fused, even if the visible SUSTech version is not bumped yet.
6. A SUSTech-only feature is added, removed, renamed, or intentionally handed back to upstream behavior.
7. A template, deck, brand, or icon cleanup changes compatibility expectations.

When version information changes, keep these files aligned:

- `VERSION`
- `RELEASE_META.json`
- `README.md`
- `docs/README.md`
- `docs/Roadmap.md`

## Future Upstream Fusion Checklist

Before accepting a future upstream update, verify:

- [ ] The upstream skill subtree is mapped from `skills/ppt-master/`, not merged as a full repository root by accident.
- [ ] `VERSION` and `RELEASE_META.json` preserve baseline vs tracked-cutoff semantics.
- [ ] `.env.example` and `requirements.txt` stay aligned with `RELEASE_META.json.support_files`.
- [ ] Live preview keeps upstream lifecycle features and only compatible SUSTech layout diagnostics.
- [ ] `/create-template` keeps `brief_lock.json` strict mode for new SUSTech templates.
- [ ] Upstream templates do not fail only because they lack `brief_lock.json`.
- [ ] `sustech_academic_official` remains a deck.
- [ ] Cleaned legacy layouts are not reintroduced without explicit decision.
- [ ] Local icon and deck assets remain present.
- [ ] Native object export, chart workbook generation, and source-intake changes remain present.

## Release Line Status

As of 2026-07-07:

- Current source release line: `r3.1.0-v0.4.0`
- `ppt_text_normalize` Safe MVP first enters the formal capability release line at `r2.8.0-v0.2.0`
- `r3.1.0-v0.4.0` is the first SUSTech line on the upstream v3.1 architecture.
- For this release, `ppt_text_normalize` public wording is conservative: `scan` / `apply` only.

Release pages:

- <https://github.com/lengmh/ppt-master-sustech-skill/releases>
