# PPT Master SUSTech Enhancement Roadmap

> Last updated: 2026-06-09  
> Current release line: `r2.8.0-v0.2.2`
> Upstream baseline: `hugohe3/ppt-master@v2.8.0`  
> Tracked upstream range: `v2.8.0..a8802cedc1477a0fecc7aa276b396508ba85bb79`

## Purpose

This file is the long-lived inventory for the SUSTech-enhanced `ppt-master` line.

It has two jobs:

1. Record the functional changes that distinguish the SUSTech-enhanced source from the upstream skill.
2. Serve as the guard checklist for future upstream fusions and version updates so local enhancements are not lost.

Whenever version metadata changes, observable behavior changes, or upstream code is fused again, update this file in the same change set.

## Current Layering Model

| Layer | Meaning | Current State |
|---|---|---|
| Baseline | Official upstream release tag used as the release base | `v2.8.0` / `0c0bdaf0dd953afc2c00322e92f26dc02fc1c51f` |
| Tracking | Upstream main commits after the baseline that have also been absorbed | `a8802cedc1477a0fecc7aa276b396508ba85bb79` / `fix(marketplace)` |
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
- Current version is `r2.8.0-v0.2.2`.

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

### 3. Live Preview Editing Enhancements

SUSTech extends upstream `live-preview` with browser-side editing assists.

Key files:

- `workflows/live-preview.md`
- `scripts/svg_editor/server.py`
- `scripts/svg_editor/static/app.js`
- `scripts/svg_editor/static/editor_logic.js`
- `scripts/svg_editor/static/index.html`
- `scripts/svg_editor/static/style.css`

Preserved capabilities:

- group / child selection mode
- single-element drag preview
- multi-element drag preview
- scale handle preview
- reset preview
- merged annotation generation
- text layout issue detection
- one-click layout suggestion annotation
- post-export annotation window

Upstream v2.8.0 capabilities that must also stay present:

- project-level `.live_preview.lock`
- slide/cache mechanism
- slide polling
- reload banner
- warning banner
- bilingual UI
- slide navigation toolbar

Fusion guard:

- Do not regress the SUSTech editing assists when accepting upstream `app.js`, `server.py`, HTML, or CSS changes.
- Keep `editor_logic.js` as the pure-logic home for annotation synthesis and text-layout helpers.
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
- `design_spec.md` YAML frontmatter is the primary metadata source for v2.8.0 template discovery and registration.

Fusion guard:

- Do not make `brief_lock.json` a universal hard dependency for all upstream templates.
- Do not remove strict mode for new SUSTech templates.
- Preserve template preview feedback before registration.

### 5. Brand / Layout / Deck Template Model

The current template model follows upstream v2.8.0 `brand / layout / deck` structure while preserving SUSTech assets.

Key directories:

- `templates/brands/`
- `templates/layouts/`
- `templates/decks/`
- `templates/icons/`

Current state:

- `templates/layouts/` keeps only upstream v2.8.0 layout presets:
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

Upstream v2.8.0 assets retained:

- `templates/icons/phosphor-duotone/`
- `templates/icons/simple-icons/`
- `templates/icons/tabler-filled/`
- `templates/icons/tabler-outline/`
- chart templates and indexes

Fusion guard:

- Take the asset union unless a user explicitly confirms cleanup.
- Do not overwrite SUSTech-specific decks or icon sets with upstream-only copies.
- Keep JSON indexes valid.

### 7. Post-v2.8.0 Tracked Additions

The SUSTech line currently includes selected upstream `main` changes after the `v2.8.0` tag.

Tracked cutoff:

- `a8802cedc1477a0fecc7aa276b396508ba85bb79`
- `fix(marketplace): drop duplicate skills spec to resolve manifest conflict`

Absorbed skill-root changes:

- `scripts/latex_render.py`
- LaTeX formula manifest flow through `images/formula_manifest.json`
- formula PNGs as image assets with `Acquire Via: formula`, `Type: Latex Formula`, and `no-crop`
- PDF vector figure crop/render fixes in `scripts/source_to_md/pdf_to_md.py`
- PPTX notes relationship guard in `scripts/svg_to_pptx/pptx_builder.py` and `scripts/svg_to_pptx/pptx_notes.py`
- Strategist / Image Generator text policy updates:
  - two-layer / three-layer `text_policy` judgment
  - subject-domain prompt depth
  - hero-page-only overlay reservation
  - removal of stale absolute “CJK fails / English-only” claims

Fusion guard:

- Treat `latex_render.py` as post-v2.8.0 tracking, not as part of the original v2.8.0 tag.
- Do not import upstream full-repository `.claude-plugin/` content into the skill root unless the release identity is explicitly changed.
- Keep `RELEASE_META.json.upstream.tracked_*` fields current when the tracked cutoff changes.

### 8. Built-in PPT Text Normalize Safe MVP

SUSTech now treats `scripts/ppt_text_normalize/` as a built-in repo capability with a conservative Safe MVP source command surface.

Key files:

- `scripts/ppt_text_normalize/scan.py`
- `scripts/ppt_text_normalize/build_review_workspace.py`
- `scripts/ppt_text_normalize/compile_review_decisions.py`
- `scripts/ppt_text_normalize/apply.py`
- `scripts/docs/ppt-text-normalize.md`
- `scripts/ppt_text_normalize/README.md`
- `scripts/ppt_text_normalize/CONTEXT.md`
- `scripts/ppt_text_normalize/tests/`

Current rules:

- The Safe MVP `scan` / `apply` capability release starts at `r2.8.0-v0.2.0`.
- The optional visual review gate enters the formal release line at `r2.8.0-v0.2.1`.
- `r2.8.0-v0.2.2` adds per-block visual-review field gate override for explicit manual color/style alignment while preserving Safe MVP field boundaries.
- `r2.8.0-v0.1.1` release assets had included related files, but that version did not define `ppt_text_normalize` as a formal supported repo capability.
- The current built-in command surface includes `scan`, optional `build_review_workspace`, optional `compile_review_decisions`, and `apply`.
- The current release scope is the Safe MVP conservative normalization flow plus the optional visual review gate: `Object Slot` matching, hero freeze, weak-canonical restraint, safe field gating, per-block field gate override, review decisions, reviewed rules, report output, and OOXML namespace-preserving PPTX writes.
- Browser review remains a review layer only: it writes `review_decisions.json` and does not mutate `rules.json`, SVG geometry, or PPTX files.

Fusion guard:

- Do not describe future review-gate expansion as shipped until the commands and browser flow actually exist in source and release docs.
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
- [ ] Live preview keeps both upstream lifecycle features and SUSTech editing assists.
- [ ] `/create-template` keeps `brief_lock.json` strict mode for new SUSTech templates.
- [ ] Upstream templates do not fail only because they lack `brief_lock.json`.
- [ ] `sustech_academic_official` remains a deck.
- [ ] Cleaned legacy layouts are not reintroduced without explicit decision.
- [ ] Local icon and deck assets remain present.
- [ ] Formula rendering, PDF vector figure crop, and PPTX notes guard are preserved if the tracked cutoff still includes them.

## Release Line Status

As of 2026-06-09:

- Current source release line: `r2.8.0-v0.2.2`
- `ppt_text_normalize` Safe MVP first enters the formal capability release line at `r2.8.0-v0.2.0`
- Optional visual review gate first enters the formal capability release line at `r2.8.0-v0.2.1`
- Per-block visual review field gate override enters the formal capability release line at `r2.8.0-v0.2.2`
- `r2.8.0-v0.2.0` remains the previous published Safe MVP release line

Release pages:

- <https://github.com/lengmh/ppt-master-sustech-skill/releases>
