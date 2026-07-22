# PPT Master SUSTech Enhancement Roadmap

> Last updated: 2026-07-22
> Current release line: `r4.1.0-v0.4.0`
> Upstream baseline: `hugohe3/ppt-master@v4.1.0` (`cad57e4a45d8664bf4830d85711d355dc2600455`)
> Post-tag tracked range: `v4.1.0..cad57e4a45d8664bf4830d85711d355dc2600455` (zero commits)
> Absorbed release range: `c2cb78ad997b41d16cefe083831d62571ab9f741..cad57e4a45d8664bf4830d85711d355dc2600455`

## Purpose

This file is the long-lived inventory for the SUSTech-enhanced `ppt-master` line.

It has two jobs:

1. Record the functional changes that distinguish the SUSTech-enhanced source from the upstream skill.
2. Serve as the guard checklist for future upstream fusions and version updates so local enhancements are not lost.

Whenever version metadata changes, observable behavior changes, or upstream code is fused again, update this file in the same change set.

## Current Layering Model

| Layer | Meaning | Current State |
|---|---|---|
| Baseline | Official upstream release tag used as the release base | `v4.1.0` / `cad57e4a45d8664bf4830d85711d355dc2600455` |
| Post-tag tracking | Extra upstream commits after the baseline | None; `tracked_commit` equals the tag commit |
| Release disclosure | Full upstream range absorbed since the previous published cutoff | `c2cb78ad997b41d16cefe083831d62571ab9f741..cad57e4a45d8664bf4830d85711d355dc2600455` |
| Overlay | SUSTech local behavior, release identity, templates, and workflow extensions | Preserved on top of the formal baseline |

Rule of thumb:

- `RELEASE_META.json.upstream.commit` records the baseline tag commit.
- `RELEASE_META.json.upstream.tracked_commit` records the extra upstream cutoff; for this tag-only release it equals the baseline commit.
- `RELEASE_META.json.upstream.absorbed_range` records the disclosure range since the previous published cutoff.
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
- Current version is `r4.1.0-v0.4.0`.
- A Release Artifact always expands to the stable `ppt-master/` root; package verification rejects another root name or extra top-level entries.
- `scripts/template_brief_lock.py` remains in the Release Artifact for existing-artifact read compatibility and does not create new locks.

Fusion guard:

- Keep `.env.example` and `requirements.txt` aligned with the recorded release identity.
- Keep `VERSION`, `RELEASE_META.json`, README files, release notes, and this roadmap aligned.
- Keep the legacy lock reader and the stable package-root contract without restoring legacy-lock writing to new template creation.

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

SUSTech keeps compatible layout diagnostics while upstream v4.1 staged direct editing remains the source of truth.

Key files:

- `workflows/stages/live-preview.md`
- `scripts/svg_editor/server.py`
- `scripts/svg_editor/static/app.js`
- `scripts/svg_editor/static/index.html`
- `scripts/svg_editor/static/style.css`

Preserved local capabilities:

- static `layout_quality` diagnostics through `scripts/svg_quality_checker.py`
- optional browser geometry probe through `scripts/svg_layout_probe.py`
- annotation remains available for changes requiring AI judgment

Upstream v4.1 capabilities that must also stay present:

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
- Keep `ppt_text_normalize` limited to its supported `scan` / `apply` surface.
- Verify both API smoke and browser interaction when this area changes.

### 4. Legacy Template Brief Lock Compatibility

SUSTech keeps legacy template-lock inspection compatible while Create Template
uses the upstream v4.1 `design_spec.md`-only contract.

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

- New `/create-template` Brand, Layout, and Deck outputs use `design_spec.md` as their only semantic contract; library and project scope differ only in workspace location and index registration.
- `brief_lock.json` is retained only for existing-artifact read compatibility and optional explicit strict audits.
- Default template quality checking validates lock-free workspaces from `design_spec.md`, template assets, and registrar preflight; a present legacy lock remains validated.
- Template preview stays lock-optional and may retain a copied legacy lock as historical preview evidence.
- `design_spec.md` YAML frontmatter is the metadata source for template discovery and registration.

Fusion guard:

- Do not restore lock writing, lock preloading, or a default strict-lock gate to new Create Template routes.
- Preserve legacy lock reading, validation, workspace-root resolution, and the explicit strict audit option.
- Do not migrate, rewrite, or delete the existing `sustech_academic_official` lock without explicit approval.
- Preserve template preview feedback before registration.

### 5. Brand / Layout / Deck Template Model

The current template model follows the upstream `brand / layout / deck` structure while preserving SUSTech assets.

Key directories:

- `templates/brands/`
- `templates/layouts/`
- `templates/decks/`
- `templates/icons/`

Current state:

- `templates/layouts/presentation_core/` is the normalized structure-only workspace with 20 authored PowerPoint Layouts.
- `sustech_academic_official` is a normalized Deck workspace with a retained historical root `brief_lock.json`, nested `templates/`, and root `images/`.
- The Deck index is the v4.1 catalog plus the validated `sustech_academic_official` entry.
- Brand and Deck workspaces use nested `templates/` plus root `images/` / `icons/` assets.

Fusion guard:

- Do not reintroduce retired flat layout catalogs into `templates/layouts/`.
- Keep `sustech_academic_official` as a deck.
- Rebuild and validate `templates/brands/brands_index.json`, `templates/layouts/layouts_index.json`, and `templates/decks/decks_index.json` after template changes.

### 6. Local Template and Icon Assets

SUSTech keeps reusable visual assets in addition to upstream assets.

Important preserved assets:

- `templates/icons/chunk/`
- `templates/icons/chunk-filled/`
- SUSTech deck assets
- indexed organization Brand/Deck assets

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

### 7. v4.1.0 Baseline Adoption

The current line adopts the formal `v4.1.0@cad57e4a` tag with no post-tag upstream commits. The disclosed absorbed range is `c2cb78a..cad57e4a`; the intermediate `eccdca20` fusion branch was never published as a separate release.

Absorbed skill-root changes include:

- staged workflow routing under `workflows/stages/`, `profiles/`, and `governance/`
- versioned design/spec locks, bounded spec repair, and deterministic page context
- normalized Brand/Layout/Deck workspaces and explicit Master/Layout/placeholder contracts
- chart recall, native chart/data payloads, and template preview export
- closed SVG/native PowerPoint geometry, paint, effect, image, text, and typography hardening
- retirement of the strict text-contract modules, the old distillation workflow, and obsolete top-level workflow paths

Fusion guard:

- Keep `tracked_*` tag-only unless a separately approved post-tag cutoff is absorbed.
- Keep `absorbed_*` fields as release disclosure metadata; do not present them as post-tag tracking.

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

- The public command surface for `r4.1.0-v0.4.0` is `scan` / `apply`.
- Safe MVP semantics include Object Slot matching, hero freeze, weak-canonical restraint, safe field gating, report output, and OOXML namespace-preserving PPTX writes.

Fusion guard:

- Do not expand the public surface beyond `scan` / `apply` without separate implementation and validation.
- Keep `scan` / `apply` semantics aligned with `scripts/docs/ppt-text-normalize.md`, `scripts/ppt_text_normalize/README.md`, and release notes.
- Preserve the OOXML namespace-preservation rule and regression coverage when this module changes.

## Maintenance Rules

Update this roadmap when any of the following happens:

1. A release version is bumped.
2. `RELEASE_META.json` upstream baseline, tracked cutoff, or absorbed disclosure range changes.
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
- [ ] `VERSION` and `RELEASE_META.json` preserve baseline, post-tag tracking, and absorbed-range semantics.
- [ ] `.env.example` and `requirements.txt` stay aligned with `RELEASE_META.json.support_files`.
- [ ] Live preview keeps upstream lifecycle features and only compatible SUSTech layout diagnostics.
- [ ] `/create-template` remains `design_spec.md`-only for new Brand, Layout, and Deck workspaces.
- [ ] Existing locks remain readable through explicit strict audit, while lock-free workspaces pass default validation.
- [ ] `sustech_academic_official` remains a deck.
- [ ] Cleaned legacy layouts are not reintroduced without explicit decision.
- [ ] Local icon and deck assets remain present.
- [ ] Native object export, chart workbook generation, and source-intake changes remain present.

## Release Line Status

As of 2026-07-22:

- Current source release line: `r4.1.0-v0.4.0`
- `ppt_text_normalize` Safe MVP first enters the formal capability release line at `r2.8.0-v0.2.0`
- `r4.1.0-v0.4.0` is the first SUSTech line on the upstream v4.1 architecture and continues local version `v0.4.0`.
- For this release, `ppt_text_normalize` public wording is conservative: `scan` / `apply` only.

Release pages:

- <https://github.com/lengmh/ppt-master-sustech-skill/releases>
