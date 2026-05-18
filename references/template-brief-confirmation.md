# Template Brief Confirmation

## Core Mission

Turn the gathered metadata and reference-analysis findings into one **bundled Template Brief** for the `/create-template` workflow, then hold for explicit user confirmation before any template files are generated.

> This is a workflow gate for **global template library creation**. It is not the project-level design-spec confirmation used in the main PPT generation pipeline.

## Pipeline Context

| Previous Step | Current | Next Step |
|--------------|---------|-----------|
| Step 1 Reference Intake & Analysis + Step 2 Fact-Based Brief Proposal | **Step 3 User Confirmation Gate** | Create Directory → Template_Designer |

---

## 1. Confirmation Discipline

⛔ **BLOCKING**: Present the complete Template Brief as one bundled package, then **wait for explicit confirmation or modifications**.

> **Execution discipline**: This is the single user-facing blocking checkpoint in `/create-template`. Before the user confirms, the AI MUST NOT create template files, MUST NOT invoke `Template_Designer`, and MUST NOT register anything into `layouts_index.json`.

### Revision Loop Rule

If the user provides any modification request:

1. update the affected recommendation, extracted fact, or assumption
2. re-issue the **full revised Template Brief** (not only the diff)
3. wait again for explicit confirmation

Repeat until the user sends an explicit approval message in the current conversation language — for example, `确认` in Chinese or `confirm` / `approved` in English.

**Do not treat** partial agreement, silence, or inferred acceptance as confirmation.

After explicit confirmation, the confirmed brief becomes the single current-state machine-readable contract `templates/layouts/<template_id>/brief_lock.json`. This file is written only **after** Step 4 creates the final template directory — never during draft rounds.

If later feedback changes any brief-level contract (identity, scenarios, keywords, tone/style, theme mode/color, canvas format, asset policy, replication mode, fidelity level, or designer constraints), return to `/create-template` **Step 3**, reconfirm the full revised brief, then overwrite `brief_lock.json` with `revision + 1`. If later feedback is implementation-level only (layout polish, spacing, alignment, local SVG cleanup, higher-resolution replacement of the same approved asset), revise the outputs directly without rewriting `brief_lock.json`.

---

## 2. Required Template Brief Items

Provide professional recommendations for the following bundled items, clearly marking provenance as `[fact]`, `[suggested]`, or `[decision]` when the workflow prepares the user-facing brief.

### a. Template Identity

- `template_id`
- display name
- whether the naming is filesystem-safe and library-safe

### b. Library Positioning

- category: `brand` / `general` / `scenario` / `government` / `special`
- applicable scenarios
- why this template belongs in the **global** library instead of a one-off project

### c. Style Objective

- tone summary
- additional design-style cues
- what should feel distinctive when users pick this template later

### d. Canvas & Theme Mode

- canvas format
- theme mode
- any format-specific implication for spacing or page density

### e. Color & Typography Direction

- primary theme color (if known or inferred)
- secondary / accent direction if already clear
- font direction if extracted from references or strongly implied by the brand

If a factual source exists (for example, `manifest.json` from `.pptx` import), prefer extracted values over visual guessing.

### f. Reference Source Interpretation

- what the reference source actually contributes
- which findings are factual extractions vs. stylistic judgments
- whether the reference is sufficient, partial, or weak

### g. Asset Packaging Strategy

- logos / reusable backgrounds / textures / canonical imported assets to keep
- assets to exclude from the final template package
- whether complex original decoration should be simplified or preserved as background assets

### h. Discovery & Execution Notes

- 3–5 lookup keywords for `layouts_index.json`
- replication mode: `standard` / `fidelity` / `mirror`
- fidelity level: `literal` / `adapted` when replication mode is `standard` or `fidelity`; omit for `mirror`
- any important assumptions still carried into downstream generation
- any constraints that `Template_Designer` must obey

---

## 3. Output Shape

Present the Template Brief in a stable structure like this:

```markdown
## Template Brief

### I. Template Identity
- Template ID:
- Display Name:
- Naming Safety Check:

### II. Library Positioning
- Category:
- Applicable Scenarios:
- Global Library Rationale:

### III. Style Objective
- Tone Summary:
- Design Style:
- Distinctive Feel:

### IV. Canvas & Theme Mode
- Canvas Format:
- Theme Mode:
- Layout Implication:

### V. Color & Typography Direction
- Theme Color:
- Supporting Colors:
- Typography Direction:

### VI. Reference Source Interpretation
- Reference Source:
- Factual Findings:
- Style Judgments:
- Confidence:

### VII. Asset Packaging Strategy
- Include:
- Exclude:
- Simplification Plan:

### VIII. Discovery & Execution Notes
- Keywords:
- Replication Mode:
- Fidelity Level:
- Locked Constraints:
- Open Assumptions:

### Confirmation
Reply with explicit confirmation (for example: `确认`) to lock this brief, or send modifications and I will re-issue the full brief.
```

The exact wording may adapt to the user's language, but the structure and field coverage must remain complete.

When the brief is confirmed, distill the locked fields into `brief_lock.json` with this minimum structure:

```json
{
  "schema_version": "1.0",
  "artifact_type": "brief_lock",
  "revision": 1,
  "template_identity": {
    "template_id": "...",
    "display_name": "...",
    "category": "..."
  },
  "library_positioning": {
    "applicable_scenarios": ["..."],
    "keywords": ["..."]
  },
  "style_contract": {
    "tone_summary": "...",
    "design_style": "...",
    "theme_mode": "...",
    "theme_color": "..."
  },
  "canvas": {
    "format": "..."
  },
  "reference_source": {
    "type": "...",
    "factual_findings": ["..."]
  },
  "asset_policy": {
    "include": ["..."],
    "exclude": ["..."],
    "simplification_policy": "..."
  },
  "designer_constraints": {
    "placeholder_contract": "canonical_v1",
    "must_keep": ["..."],
    "must_avoid": ["..."]
  },
  "replication": {
    "mode": "standard",
    "fidelity_level": "literal"
  },
  "open_assumptions": ["..."]
}
```

Do not add history snapshots, status fields, or parallel human-readable lock files. The workflow keeps exactly one current-state `brief_lock.json`.
