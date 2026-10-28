# PPT Master SUSTech Enhancement Roadmap

> Last updated: 2026-10-25
> Current release line: `r6.7.3-v0.4.0`
> Upstream baseline: `hugohe3/ppt-master@v6.7.3` (`622bf0148bca4f697b0184322c7e2aa2a04520a2`)
> Post-tag tracked range: `v6.7.3..523e5bd972f94c3cac8742fec0d54d43824a17bb` (two commits)
> Absorbed release range: `c40bca58e168fcef2facdc7612cc352d1233679b..523e5bd972f94c3cac8742fec0d54d43824a17bb`

## Purpose

This file is the long-lived inventory for the SUSTech-enhanced `ppt-master` line.

It has two jobs:

1. Record the functional changes that distinguish the SUSTech-enhanced source from the upstream skill.
2. Serve as the guard checklist for future upstream fusions and version updates so local enhancements are not lost.

Whenever version metadata changes, observable behavior changes, or upstream code is fused again, update this file in the same change set.

## Current Layering Model

| Layer | Meaning | Current State |
|---|---|---|
| Baseline | Official upstream release tag used as the release base | `v6.7.3` / `622bf0148bca4f697b0184322c7e2aa2a04520a2` |
| Post-tag tracking | Extra upstream commits after the baseline | Two approved native roundtrip fixes through `523e5bd9` |
| Release disclosure | Ancestry range absorbed since the previous published cutoff | `c40bca58e168fcef2facdc7612cc352d1233679b..523e5bd972f94c3cac8742fec0d54d43824a17bb` |
| Overlay | SUSTech local behavior, release identity, templates, and workflow extensions | Preserved on top of the formal baseline |

Rule of thumb:

- `RELEASE_META.json.upstream.commit` records the baseline tag commit.
- `RELEASE_META.json.upstream.tracked_commit` records the extra upstream cutoff; for this release it includes two approved post-tag commits.
- `RELEASE_META.json.upstream.absorbed_range` records the disclosure range since the previous published cutoff.
- SUSTech-only capabilities are treated as overlay and must be checked explicitly during each upstream fusion.

## Upstream Fusion Contract

This section is the tracked, long-lived authority for upstream fusion semantics.
Version-specific fusion plans apply this contract to fixed refs, concrete exceptions,
and validation commands; they do not redefine it. If a fusion needs to deviate,
stop, make the decision explicit, and update this section or the owning ADR before
implementation continues.

### Contract union and overlap resolution

- Fusion produces a **Fusion Contract Union**, not a mechanical union of files,
  directories, APIs, tests, dependencies, or public surfaces.
- Start from every target upstream contract selected for the release.
- Add every **Qualified Local Enhancement** that still exists in current source
  and is supported by at least one current formal contract, active caller, asset
  index, or valid regression test.
- Historical plans and release notes may identify candidates, but cannot alone
  restore retired behavior.
- When upstream and local implementations cover the same capability, use the
  target upstream implementation and tests as the authority. Port only the
  evidenced local behavior that upstream does not cover.
- Do not retain parallel implementations, compatibility shims, fallback profiles,
  or duplicate implementation-detail tests without a concrete current requirement.
- A valid regression test is sufficient preservation evidence only when it is
  enabled, exercises a reachable production path, and asserts observable behavior.
  It does not by itself make the behavior a published capability.

If the upstream implementation fails a valid local regression, repair the upstream
base minimally and keep the gap assertion. If the two contracts cannot coexist,
stop that capability and explicitly choose one of:

1. preserve the current local contract while adapting the upstream base;
2. formally retire the local contract and adopt upstream behavior;
3. defer that part of the upstream fusion.

The default is to protect an already published local contract, never to break it
silently.

### Tests, deletion, and publication

- Upstream and local tests form a contract union. For overlapping coverage, retain
  the upstream test as the base and only add local assertions for uncovered behavior.
- Never delete, skip, xfail, or weaken an existing required test merely to make a
  fusion pass.
- An upstream deletion makes a local path a deletion candidate, not an automatic
  deletion. Migrate active callers first; deletion and contract retirement require
  separate confirmation.
- A source file temporarily retained pending deletion is not automatically an
  active capability.
- The public release is a **Public Capability Projection**: only explicitly
  released capabilities allowed by the package contract may enter the Release
  Artifact. Accidental source or ZIP presence does not create support intent.
- If an unresolved retired entry would still be exposed by packaging, stop public
  packaging until its publication status and deletion decision are resolved.

### Version-specific evidence

Each fusion uses an automatically generated upstream path diff plus a
version-specific **Fusion Exception Record**. The exception record defaults to
Markdown and records only decisions that need judgment:

- changed path or capability;
- current local evidence;
- final disposition;
- migration target and active callers, when applicable;
- focused validation result;
- active, retired, or not-public status;
- deletion, dependency, attribution/license, or asset-hash decision.

This is an execution record, not a permanent compatibility registry or a generic
fusion engine. Raw snapshots, diffs, logs, and generated evidence stay outside the
source and release artifacts. Durable outcomes are summarized in this Roadmap and
the release note.

### Stable fusion sequence

1. Lock the local source baseline and immutable upstream tag/commit.
2. Extract only the upstream `skills/ppt-master/` subtree and compare the recorded
   upstream snapshots.
3. Generate the raw path diff and close every exception before semantic edits.
4. Import non-conflicting upstream changes, then resolve overlaps using upstream
   authority plus qualified local gaps.
5. Rebuild template indexes and audit assets, dependencies, attribution, routes,
   support files, and publication status.
6. Validate in order: affected focused tests → full suite → representative route
   smoke → template/index and package contracts → real PowerPoint checks for the
   high-risk PPTX paths changed by the fusion.
7. Update version metadata, Roadmap, public documentation, and release notes from
   the validated result.
8. Stop at the reviewable fusion candidate. Commit, main integration, push, public
   synchronization, tag, and release retain their separate confirmation gates.

Each version plan selects the exact tests and checks required by its impact surface.
Do not build a general-purpose merger, speculative fallback system, or redundant
validation layer.

### Special data and asset rules

- Template and icon assets use union/no-overwrite. Same-path/different-hash assets
  require explicit review; indexes are rebuilt from the resulting workspaces.
- Dependencies are derived from actual fused imports and focused tests, not from a
  mechanical requirements-file union. Additions and removals require confirmation.
- An upstream attribution or integrity contract is fused as a complete closed set:
  protected files, metadata, bootstrap gate, implementation, and live CLI calls
  must agree. Partial guard integration is invalid.
- `tracked_*` fields describe post-tag tracking. `absorbed_*` fields describe release
  disclosure and must not be repurposed as post-tag tracking.
- When upstream history is not continuous, `absorbed_range` uses
  `snapshot:<previous-cutoff>=><target-commit>`. This is a **Snapshot Disclosure**,
  not a Git range, and must never be passed to a Git range command.

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
- Current source release line is `r6.7.3-v0.4.0`.
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

SUSTech keeps compatible layout diagnostics while upstream v6.1 staged direct editing remains the source of truth.

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

Upstream v6.1 capabilities that must also stay present:

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
uses the upstream v6.1 `design_spec.md`-only contract.

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

- New `/create-template` Brand, Style, Layout, and Deck outputs use `design_spec.md` as their only semantic contract; library and project scope differ only in workspace location and index registration.
- `brief_lock.json` is retained only for existing-artifact read compatibility and optional explicit strict audits.
- Default template quality checking validates lock-free workspaces from `design_spec.md`, template assets, and registrar preflight; a present legacy lock remains validated.
- Template preview stays lock-optional and may retain a copied legacy lock as historical preview evidence.
- `design_spec.md` YAML frontmatter is the metadata source for template discovery and registration.

Fusion guard:

- Do not restore lock writing, lock preloading, or a default strict-lock gate to new Create Template routes.
- Preserve legacy lock reading, validation, workspace-root resolution, and the explicit strict audit option.
- Do not migrate, rewrite, or delete the existing `sustech_academic_official` lock without explicit approval.
- Preserve template preview feedback before registration.

### 5. Brand / Style / Layout / Deck Template Model

The current template model follows the upstream `brand / style / layout / deck` structure while preserving SUSTech assets.

Key directories:

- `templates/brands/`
- `templates/styles/`
- `templates/layouts/`
- `templates/decks/`
- `templates/icons/`

Current state:

- `templates/layouts/presentation_core/` is the normalized structure-only workspace with 20 authored PowerPoint Layouts.
- `sustech_academic_official` is a normalized Deck workspace with a retained historical root `brief_lock.json`, nested `templates/`, and root `images/`.
- The Deck index is the v6.1 catalog plus the validated `sustech_academic_official` entry.
- Brand and Deck workspaces use nested `templates/` plus root `images/` / `icons/` assets.

Fusion guard:

- Do not reintroduce retired flat layout catalogs into `templates/layouts/`.
- Keep `sustech_academic_official` as a deck.
- Rebuild and validate `templates/brands/brands_index.json`, `templates/styles/styles_index.json`, `templates/layouts/layouts_index.json`, and `templates/decks/decks_index.json` after template changes.

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

### 7. v6.1.0 Fixed Snapshot Fusion

The previous release adopted the formal `v6.1.0@c40bca58` tag with no post-tag upstream commits. The previous published upstream cutoff `cad57e4a` and v6.1 tag do not form a continuous ancestry range, so the absorbed disclosure is `snapshot:cad57e4a=>c40bca58`, not a Git range.

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

- The public command surface for `r6.7.3-v0.4.0` is `scan` / `apply`.
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
- [ ] The version plan applies the tracked Upstream Fusion Contract and records any proposed deviation before implementation.
- [ ] The Fusion Contract Union uses upstream authority for overlap and preserves every evidenced local gap.
- [ ] Valid upstream and local tests are retained as a contract union without duplicate implementation-detail coverage.
- [ ] Every exception has current evidence, disposition, validation, publication status, and any required confirmation.
- [ ] `VERSION` and `RELEASE_META.json` preserve baseline, post-tag tracking, and absorbed-range semantics.
- [ ] `.env.example` and `requirements.txt` stay aligned with `RELEASE_META.json.support_files`.
- [ ] Live preview keeps upstream lifecycle features and only compatible SUSTech layout diagnostics.
- [ ] `/create-template` remains `design_spec.md`-only for new Brand, Style, Layout, and Deck workspaces.
- [ ] Existing locks remain readable through explicit strict audit, while lock-free workspaces pass default validation.
- [ ] `sustech_academic_official` remains a deck.
- [ ] Cleaned legacy layouts are not reintroduced without explicit decision.
- [ ] Local icon and deck assets remain present.
- [ ] Only explicitly released capabilities enter the Public Capability Projection and release package.
- [ ] Native object export, chart workbook generation, and source-intake changes remain present.

## v6.7.3 Release Adaptation

- Adopted upstream prompt-audit contracts, with standalone-root path mapping and unchanged numeric budgets. Retained local advisory grammar and the 76-entry chart registry.
- Adapted SUSTech text frames and three guidance baselines; kept font sizes, placeholders, images and historical brief-lock unchanged. Compressed duplicate design-spec prose without removing identity or usage rules.
- Full regression: 952 tests and 1350 subtests passed. Browser navigation/edit/draft restore/save and actual PowerPoint 16.0 eight-slide preview passed.
- Development uses a separate checkout. The former skill checkout and public checkout remain untouched.

## Release Line Status

As of 2026-10-24:

- Current source release line: `r6.7.3-v0.4.0`.
- `ppt_text_normalize` Safe MVP first enters the formal capability release line at `r2.8.0-v0.2.0`
- `r6.7.3-v0.4.0` continues local version `v0.4.0` on upstream v6.7.3 plus the approved cutoff.
- For this release, `ppt_text_normalize` public wording is conservative: `scan` / `apply` only.

Release pages:

- <https://github.com/lengmh/ppt-master-sustech-skill/releases>
