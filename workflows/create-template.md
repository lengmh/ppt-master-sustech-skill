---
description: Generate a new PPT layout template based on existing project files or reference templates
---

# Create New Template Workflow

> **Role invoked**: [Template_Designer](../references/template-designer.md)

Generate a complete set of reusable PPT layout templates for the **global template library**.

> This workflow is for **library asset creation**, not project-level one-off customization. The output must be reusable by future PPT projects and discoverable from `templates/layouts/layouts_index.json`.

## Process Overview

```
Reference Intake & Analysis -> Fact-Based Brief Proposal -> User Confirmation Gate -> Create Directory + Invoke Template_Designer -> Enhanced Validate -> Template Preview Feedback -> Register Index -> Output
```

The first three steps derive the brief from facts, not guesses. **No final template directory may be created and no template SVG / `design_spec.md` may be written until `[TEMPLATE_BRIEF_CONFIRMED]` is emitted in Step 3.** Reference-analysis intermediates produced by `pptx_template_import.py` (typically under `/tmp/pptx_template_import/`) are explicitly **not** subject to this gate — they are temporary workspaces feeding Step 2.

---

## Step 1: Reference Intake & Analysis

Branch by the type of reference source the user supplied. This step produces analysis artefacts only — it does **not** create the final template directory, write `design_spec.md`, or touch `layouts_index.json`.

### Input source taxonomy

| Type | What the user supplied | Tool / read path | Replication modes available |
|------|-------------------------|------------------|------------------------------|
| **A** `.pptx` reference | A `.pptx` file path | `pptx_template_import.py` → `manifest.json` + `svg/master_*.svg` + `svg/layout_*.svg` + `svg/slide_*.svg` + `svg-flat/slide_*.svg` + `assets/` | `standard` / `fidelity` / `mirror` |
| **B** Existing SVG assets | `projects/<x>/svg_output/`, `templates/layouts/<existing>`, or a loose `.svg` folder | `ls` + `Read` each `*.svg`; plus `design_spec.md` / `spec_lock.md` if present | `standard` / `fidelity` (AI visual clustering) / `mirror` (direct 1:1 copy) |
| **C** Image / visual references | Screenshot folder, single image, PDF pages | `ls` + `Read` each file (multimodal visual recognition) | `standard` only |
| **D** No reference source | Verbal description only ("McKinsey style", "tech blue", "dark minimal") | — | `standard` only |

`fidelity` and `mirror` are not available for type C / D — visual references and verbal-only briefs cannot drive page-by-page replication. Type A is the canonical path: `manifest.json` page-type candidates and the layered `svg/` workspace anchor cluster detection (fidelity) and verbatim copy (mirror) with factual data. Type B is supported with caveats:

- **mirror on type B** — direct 1:1 copy. B's SVGs are already self-contained (one file per page, equivalent to `svg-flat/slide_*.svg`). Page-type for the `<NNN>_<page_type>.svg` filename is read from the source filename when it follows the PPT Master naming convention (`01_cover.svg` → `cover`, `03a_content_two_col.svg` → `content`); fall back to `content` otherwise. Particularly natural when the source is `templates/layouts/<existing>` and the user wants to fork an existing template.
- **fidelity on type B** — clustering relies on the AI's visual judgement of the SVGs; there is no `manifest.json.pageTypeCandidates` to anchor it. Variant count and grouping are more subjective and may need iteration. If the input is already a PPT Master template (`templates/layouts/<existing>`), parse the existing variant filenames (`03a_content_two_col` etc.) as authoritative cluster hints rather than re-clustering visually.

### 1A. `.pptx` reference

Run the unified preparation helper:

```bash
python3 skills/ppt-master/scripts/pptx_template_import.py "<reference_template.pptx>"
```

This produces, in one workspace:

- `manifest.json` — single source of truth: slide size, theme colors, fonts, per-master theme summaries, asset inventory, placeholder metadata, SVG file paths, per-slide / per-layout / per-master metadata, page-type candidates
- `summary.md` — short human-readable digest derived from manifest.json (for quick scanning only)
- `assets/` — extracted reusable image assets; `manifest.json` owns the asset-name mapping and SVG `href` values reuse that mapping
- `svg/` — **primary view** (layered template view):
  - `svg/master_*.svg` — every slide master in the deck rendered once, including masters that no sample slide currently uses (template packages routinely ship more masters than the visible samples reference)
  - `svg/layout_*.svg` — every slide layout in the deck rendered once (its own contribution; master shapes do **not** repeat here)
  - `svg/slide_NN.svg` — each slide's own shapes and slide-local background; master / layout shapes and backgrounds are **not** inlined here
  - `svg/inheritance.json` — which layout & master each slide consumes
- `svg-flat/` — **companion view** (one self-contained SVG per slide):
  - `svg-flat/slide_NN.svg` — master + layout + slide painted into a single SVG so opening any slide on its own shows the full page like PowerPoint would. Use this for previews / screenshot pipelines / "what does the slide actually look like" sanity checks.
- The default `--inheritance-mode both` emits both views. Pass `layered` to skip `svg-flat/`, or `flat` for round-trip use cases (legacy: `svg/` becomes self-contained slides without the master/layout/inheritance files).

Import fidelity rules:

- Placeholder metadata is recorded in `manifest.json`; master / layout SVGs show lightweight dashed guides with labels only in `svg/`, not in `svg-flat/`.
- Charts, SmartArt, diagrams, and OLE objects are typed placeholders in `svg/`. In `svg-flat/`, they use a preview image with a small badge when one exists; otherwise they stay visible as placeholders. Tables are converted to real SVG.
- Missing media and external linked images fail the import. EMF / WMF Office vector media are converted to PNG previews when supported by the local toolchain; otherwise the import fails.

It is a reconstruction aid, not a final direct template conversion.

**Read order during analysis** (read everything below before composing Step 2):

1. `manifest.json` (factual metadata: slide size, theme, assets, layouts, masters, slide page-types)
2. `svg/master_*.svg` and `svg/layout_*.svg` — read these **before** any slide SVG; they show the deck's shared visual language (background, headers, footers, decorative bars). This is what the new template's fixed structure should adapt from.
3. `svg/inheritance.json` — confirms which slide uses which layout/master
4. exported `assets/`
5. cleaned slide SVG references `svg/slide_NN.svg` — content unique to each slide; consult after the master/layout language is understood
6. `summary.md` only as a quick orientation aid
7. user-provided screenshots or the original PPTX only for visual cross-checking

Interpretation rule (carries forward into Steps 2 and 4):

- `manifest.json` is the source of truth for slide size, theme colors, fonts, background inheritance, reusable asset inventory, unique layout/master structure, and slide reuse relationships
- `summary.md` is a quick scan; never treat it as the canonical fact source — go back to `manifest.json` if anything is unclear
- exported `assets/` are the canonical reusable image pool — `<image>` references in `svg/` already point at these files directly
- `svg/master_*.svg` / `svg/layout_*.svg` are the **primary source for fixed structural design** — recurring backgrounds, page chrome, decorative motifs that the template should preserve. The new template's `01_cover` / `02_chapter` / `03_content` / `04_ending` typically inherit elements from these layers.
- `svg/slide_NN.svg` shows page-specific content — useful for judging composition rhythm and content density, not for fixed structure. Read every slide regardless of count.
- `svg-flat/slide_NN.svg` is for human preview and screenshot comparison; do not treat duplicated master/layout chrome inside flat slides as separate reusable template structure.
- screenshots remain useful for judging composition and style, but should not override extracted factual metadata unless the import result is clearly incomplete

**Hard read gate** (`standard` / `fidelity` modes — `mirror` differs, see below):

- The agent MUST finish reading every `svg/master_*.svg`, `svg/layout_*.svg`, and `svg/slide_*.svg` file under `<import_workspace>/svg/` before moving on to Step 2
- The agent MUST list the read master / layout / slide filenames inside the Step 2 brief proposal as proof of the gate

Do **not** treat the imported PPTX or exported slide SVGs as direct final template assets — Step 4 reconstructs them as a clean, maintainable PPT Master template package, not a 1:1 shape translation.

> **Mirror-mode fast path** — when the user has indicated mirror replication (verbatim copy of every source slide):
> - Read **only** `svg-flat/slide_*.svg` (the self-contained, what-PowerPoint-shows view) and `manifest.json` (for theme colors, fonts, asset inventory).
> - Skip `svg/master_*.svg` / `svg/layout_*.svg` / `svg/inheritance.json` — chrome / content separation is irrelevant in mirror mode (no placeholder insertion happens).
> - Mirror is explicitly a verbatim copy flow — every slide becomes a template page as-is. The "reconstruct, don't translate" rule applies to `standard` / `fidelity` only.

### 1B. Existing SVG assets

`ls` the directory and `Read` every `*.svg` to extract:

- canvas size (`viewBox` on the root `<svg>`)
- recurring colors (`fill` / `stroke` values; identify the dominant 2–4 hex codes as candidate theme colors)
- fonts (`font-family` attributes on `<text>`)
- placeholder usage (existing `{{...}}` strings, if any)
- structural decoration (recurring `<rect>` bars, `<path>` motifs, embedded `<image>` references)

If a `design_spec.md` or `spec_lock.md` accompanies the SVGs, `Read` it too — it is a higher-confidence source than re-deriving from the SVG alone. Record the equivalent of a `manifest.json`'s factual fields in your own analysis notes (no actual file written) so Step 2 can label them `[fact]`.

### 1C. Image / visual references

`ls` the folder (or single file) and `Read` each image / PDF page. Extract what's visible:

- rough theme colors (eyeball the dominant 2–4 hues; do NOT report exact HEX as fact)
- page count (count the supplied images as an approximate slide count)
- dominant typography style (sans / serif / display) — never report a font name
- decorative motifs and composition rhythm

Be explicit in Step 2 that exact HEX values, font names, and placeholder structure are **estimates from visual inspection** (`[suggested]`), never `[fact]`.

### 1D. No reference source

Skip the analysis. Step 2 will list every Required item as `[decision]`; nothing is fact-derivable from a non-existent source.

---

## Step 2: Fact-Based Brief Proposal

Compose a single message that surfaces every Required brief item to the user, **labelling each value's provenance**:

- **`[fact]`** — extracted from Step 1 analysis (e.g. theme color from `manifest.json`)
- **`[suggested]`** — professional recommendation inferred from the source, but not directly extractable as fact
- **`[decision]`** — user choice required; the workflow cannot safely infer it

The proposal must include, at minimum:

- Template ID
- Display name
- Category
- Applicable scenarios
- Tone summary
- Theme mode
- Canvas format
- Replication mode (`standard` / `fidelity` / `mirror`)
- Fidelity level (`literal` / `adapted`) when replication mode is `standard` or `fidelity`; omit for `mirror`
- Keywords
- Theme color / typography direction / asset packaging notes when known
- For type A `.pptx`: the exact `svg/master_*.svg`, `svg/layout_*.svg`, `svg/slide_*.svg` filenames you read (proof of the hard read gate)
- A one-line summary of the master / layout structure you extracted

The goal of Step 2 is to move every user-visible brief field into one explicit bundle before the blocking confirmation gate.

---

## Step 3: User Confirmation Gate

🚧 **GATE**: Step 1 and Step 2 complete.

First, read the confirmation reference:

```
Read references/template-brief-confirmation.md
```

⛔ **BLOCKING**: Present the complete **Template Brief** to the user as one bundled package, then **wait for explicit confirmation or modifications**.

> **Execution discipline**: This is the single user-facing blocking checkpoint in `/create-template`. Before the user confirms, the AI MUST NOT create template files, MUST NOT invoke `Template_Designer`, and MUST NOT register anything into `layouts_index.json`.

The Template Brief MUST:

- follow the structure defined in `references/template-brief-confirmation.md`
- cover all required metadata from Step 2
- incorporate relevant extracted facts from the reference source when available
- clearly separate factual extraction from stylistic judgment

**Revision loop (mandatory)**:

1. If the user gives modification feedback, update the affected recommendations / assumptions
2. Re-present the **full revised Template Brief** (not only the changed lines)
3. Wait again for explicit confirmation

Repeat until the user sends an explicit approval message in the current conversation language — for example, `确认` in Chinese or `confirm` / `approved` in English.

Partial agreement, silence, or inferred acceptance do **not** count as confirmation.

After explicit confirmation, treat the confirmed Template Brief as the locked downstream input and emit `[TEMPLATE_BRIEF_CONFIRMED]`. `brief_lock.json` is written only after Step 4 creates the final template directory.

**✅ Checkpoint — Confirm the brief gate is closed, then proceed to Step 4**:

```markdown
## ✅ Template Brief Confirmation Complete
- [x] Bundled Template Brief presented
- [x] User feedback incorporated (if any)
- [x] Explicit confirmation received
- [x] `[TEMPLATE_BRIEF_CONFIRMED]` emitted
- [ ] **Next**: Auto-proceed to Create Directory / Template_Designer
```

---

## Step 4: Create Template Directory + Invoke Template_Designer

```bash
mkdir -p "skills/ppt-master/templates/layouts/<template_id>"
```

> **Output location**: Global templates go to `skills/ppt-master/templates/layouts/`; project templates go to `projects/<project>/templates/`
>
> The generated directory name must match the final template ID used in `layouts_index.json`. After Step 3 confirmation and directory creation, write the single current-state machine contract `brief_lock.json` into `templates/layouts/<template_id>/` before invoking `Template_Designer`.

**Switch to the Template_Designer role** and generate per role definition. The role input is the **confirmed Template Brief from Step 3** plus the just-written `brief_lock.json`, not a project design spec.

Pass the appropriate internal package based on Step 1 source type:

- Type A `.pptx`: confirmed Template Brief + `brief_lock.json` + `manifest.json` + `summary.md` + `assets/` + `svg/master_*.svg` + `svg/layout_*.svg` + `svg/slide_NN.svg` + `svg/inheritance.json` + `svg-flat/slide_NN.svg` + optional screenshots
- Type B SVG assets: confirmed Template Brief + `brief_lock.json` + source SVGs + any accompanying `design_spec.md` / `spec_lock.md`
- Type C images: confirmed Template Brief + `brief_lock.json` + image file list + visual analysis notes
- Type D no source: confirmed Template Brief + `brief_lock.json`

The role uses the analysis bundle to anchor objective facts such as theme colors, fonts, reusable backgrounds, and common branding assets, then rebuilds the final SVG templates in a simplified, maintainable form.

**Apply the visual-fidelity decision from Step 3**: pages marked `literal` (typically cover / chapter / ending) must reproduce the reference's geometry, decoration, and sprite-sheet crops as-is — "simplified, maintainable form" applies only to genuinely redundant structure, not to load-bearing layout. Pages marked `adapted` may use the reference for tone and structural rhythm but evolve the design.

**Mirror-mode override** (type A or B): when `Replication mode: mirror`, this step is a **verbatim copy** rather than a reconstruction. The Template_Designer role:

1. Copies the source pages into the template directory **without any modification** other than filename change and asset-path rewrites.
2. Renames each file using `<NNN>_<page_type>.svg`, zero-padded to 3 digits.
3. Copies bundled assets into the template directory and rewrites `<image href="...">` paths consistently.
4. Writes `design_spec.md` per `template-designer.md` — in mirror mode, **§V Page Roster is load-bearing** because the SVGs themselves contain no placeholder contract.

If later preview feedback changes any **brief-level** field (identity, scenarios, keywords, tone/style, theme mode/color, canvas format, asset policy, replication mode, fidelity level, or designer constraints), return to Step 3, reconfirm the revised full brief, overwrite `brief_lock.json`, and increment `revision` before generating again. If feedback is **implementation-level** only, revise `design_spec.md` / SVG outputs directly without changing `brief_lock.json`.

> **Role details**: See [template-designer.md](../references/template-designer.md)

---

## Step 5: Enhanced Validate

```bash
ls -la "skills/ppt-master/templates/layouts/<template_id>"
```

Run the template self-check first:

```bash
python3 skills/ppt-master/scripts/template_quality_checker.py "skills/ppt-master/templates/layouts/<template_id>" --format <canvas_format>
```

This self-check must cover:

- `brief_lock.json` → `design_spec.md` consistency
- `design_spec.md` → SVG / asset consistency
- upstream template-mode SVG validation via `svg_quality_checker.py`
- registrar preflight readiness (`register_template.py --dry-run`)

**Checklist**:

- [ ] `brief_lock.json` exists and matches the confirmed brief-level contract
- [ ] `design_spec.md` follows the personality-only template skeleton (Overview / Color / Signature / Page Roster); generic constraints are **not** redundantly restated
- [ ] Every page declared in `design_spec.md §V Page Roster` exists as an SVG file in the template directory (and vice versa)
- [ ] Placeholder names follow the canonical convention where applicable; overrides are declared explicitly when needed
- [ ] SVG viewBox matches the chosen canvas format (for `ppt169`: `0 0 1280 720`)
- [ ] Asset files referenced by SVGs actually exist in the template package
- [ ] For `fidelity` mode: sprite-sheet crop wrappers are preserved when required
- [ ] For `mirror` mode: file count matches the source page count and copied SVGs contain **no** `{{...}}` placeholders

This step is a **hard gate**. Do not proceed to preview or registration until validation passes.

---

## Step 5.5: Template Preview Feedback

🚧 **GATE**: Step 5 complete; the template directory passes validation.

⛔ **BLOCKING**: Before registration, export a preview workspace under the user's current working directory and wait for explicit feedback or confirmation.

```bash
python3 skills/ppt-master/scripts/template_preview.py "skills/ppt-master/templates/layouts/<template_id>"
```

The command exports a timestamped preview workspace containing `svg_output/` and `svg_final/`. Point the user to `<preview_workspace>/svg_final/` for review.

**Feedback routing rule**:

- If feedback is **implementation-level** only (spacing, alignment, local hierarchy, asset placement, page polish), return to Step 4 / Step 5, revise `design_spec.md` / SVG outputs, re-run validation, and re-export the preview. Do **not** rewrite `brief_lock.json`.
- If feedback changes any **brief-level** contract (identity, scenarios, keywords, tone/style, theme mode/color, canvas format, asset policy, replication mode, fidelity level, or designer constraints), return to Step 3, reconfirm the revised full brief, overwrite `brief_lock.json`, increment `revision`, then regenerate, revalidate, and re-export the preview.

Proceed to Step 6 only after the user explicitly confirms the preview result.

---

## Step 6: Register Template in Library Index

Run the unified registrar; it derives the `layouts_index.json` entry and refreshes the `README.md` Quick Index from `design_spec.md` (frontmatter when present, prose fallback otherwise) plus the actual SVG file list:

```bash
python3 skills/ppt-master/scripts/register_template.py <template_id>
```

Outputs:

- updates `skills/ppt-master/templates/layouts/layouts_index.json`
- refreshes the auto-managed Quick Index inside `skills/ppt-master/templates/layouts/README.md`
- prints a "Template Creation Complete" card you can reuse directly in Step 7

`layouts_index.json` is a **discovery index** — it lets the AI answer "what templates are available?" by listing names and paths. It is **not** consulted to trigger template consumption later; users still trigger template usage by passing an explicit directory path.

---

## Step 7: Output Confirmation

`register_template.py` already printed a "Template Creation Complete" card during Step 6 — copy it verbatim into the conversation. The card includes the template name, path, category, primary color, index status, and the full SVG file roster collected from disk.

---

## Color Scheme Quick Reference

| Style | Primary Color | Use Cases |
|-------|---------------|-----------|
| Tech Blue | `#004098` | Certification, evaluation |
| McKinsey | `#005587` | Strategic consulting |
| Government Blue | `#003366` | Government projects |
| Business Gray | `#2C3E50` | General business |

---

## Notes

1. **SVG technical constraints**: See [shared-standards.md](../references/shared-standards.md) — do not restate them in template `design_spec.md`
2. **Color consistency**: All SVG files must use the same color scheme as `design_spec.md §II Color Scheme`
3. **Placeholder consistency**: Use the canonical placeholder contract unless the template explicitly documents an override
4. **Mirror mode warning**: Mirror templates inherit any import limitations present in `pptx_template_import.py` / `pptx_to_svg`
5. **Troubleshooting**: If a `.pptx` import behaves unexpectedly, run `python3 skills/ppt-master/scripts/pptx_template_import.py <file> --inheritance-mode both` manually and inspect `manifest.json`, `svg/`, and `svg-flat/`
