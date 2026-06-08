# PPT Text Normalize Safe MVP Design

## 1. Goal

Build an **Automation-First Pipeline** inside `scripts/ppt_text_normalize/` that performs **Text Style Normalization** on existing `.pptx` files while preserving text content, text-box geometry, and overall page layout. The current built-in capability targets only **Normalization Scope v1**:

- text boxes
- title/body placeholders
- table cell text

It must not mutate SmartArt text, chart text, notes text, or master/layout source text.

The upgraded semantic goal is no longer “broadly unify text within a page type.” The new goal is:

- preserve unique-page design unless strong structural evidence says otherwise
- normalize repeated **Object Slots** rather than generic `title/body` buckets
- treat `content_area` as a semantically layered region whose default mutations are limited to font family and font weight
- detect hero-like pages and hero-like slots, then freeze them by default

## 2. Design principles

1. **Automation-first** — `scan` generates machine-usable rules automatically; `apply` consumes them automatically by default.
2. **Style-only mutation** — only text appearance changes; content and layout do not.
3. **Slot-aware matching** — matching is by `Page Type → Page Submode → Object Slot → Slot Variant`, not by absolute coordinates across the entire deck.
4. **Permission-first normalization** — every page and slot resolves a **Mutation Permission Profile** before any style change is attempted.
5. **Content-area restraint** — inside `content_area`, default mutations are limited to `font_family` and `font_weight`; changes to `font_size` and `color` are destructive by default and should not happen automatically.
6. **Hero freeze by default** — hero-like pages and hero-like slots are reported, not mutated, unless a user explicitly overrides the freeze.
7. **Series-aware reasoning** — TOC and chapter normalization depend on **Uniformity Eligibility** and **Series Cohesion**, not just single-page local votes.
8. **Auditability** — every classification, canonical-style decision, mutation, fallback, freeze, and skip must be reportable.
9. **Conservative extension readiness** — keep CLI shape, contracts, and module boundaries stable for later built-in extensions.

## 3. Scope and non-goals

### In scope

- automatic slide scanning
- automatic `Page Type` inference
- automatic `Page Submode` inference
- hero page and hero slot detection
- automatic `Object Slot` inference
- automatic `Slot Variant` inference
- automatic `Content Intent Role` inference inside content areas
- style clustering and canonical-style suggestion
- rules generation (`rules.json`)
- automatic apply based on generated rules
- JSON + Markdown reporting for scan and apply
- conservative fallback, freeze, and skip behavior for layout safety

### Out of scope (current Safe MVP)

- SmartArt text normalization
- chart-label normalization
- notes-page normalization
- master/layout source-text normalization
- geometry edits
- content edits
- page redesign / beautification
- forcing 100% mutation success on every text block
- user-facing override UI beyond editable JSON contracts

## 4. Module directory structure

```text
scripts/ppt_text_normalize/
  CONTEXT.md
  design.md
  README.md

  scan.py
  apply.py

  contracts/
    rules.schema.json
    scan_report.schema.json
    apply_report.schema.json

  core/
    __init__.py
    model.py
    ooxml_package.py
    text_inventory.py
    role_classifier.py
    style_cluster.py
    canonical_style.py
    layout_guard.py
    apply_engine.py
    report_writer.py

  examples/
    rules.min.json
    rules.full.json
```

### Responsibility split

- `scan.py` — CLI entry point for read-only analysis.
- `apply.py` — CLI entry point for mutation using generated rules.
- `contracts/` — stable schemas for the **Normalization Rules Contract** and reports.
- `core/model.py` — shared typed structures such as `TextBlock`, `CanonicalStyle`, `LayoutRiskAssessment`, `ObjectSlotResolution`, `HeroDecision`, and `MutationPermissionProfile`.
- `core/ooxml_package.py` — PPTX package open/read/write helpers.
- `core/text_inventory.py` — extraction of all v1-scope text containers.
- `core/role_classifier.py` — page-type, page-submode, hero, slot, and content-intent scoring.
- `core/style_cluster.py` — style fingerprint aggregation and clustering.
- `core/canonical_style.py` — canonical-style source selection and synthesis.
- `core/layout_guard.py` — layout-risk estimation and fallback decisions.
- `core/apply_engine.py` — **Emphasis-Preserving Apply** implementation using permission profiles.
- `core/report_writer.py` — report generation in JSON and Markdown.

## 5. CLI and runtime model

### Scan

```bash
python scripts/ppt_text_normalize/scan.py <input.pptx> --task <task_name>
```

Optional:

```bash
python scripts/ppt_text_normalize/scan.py <input.pptx> \
  --task demo \
  --workdir <workdir>/ppt_text_normalize/demo
```

### Apply

```bash
python scripts/ppt_text_normalize/apply.py <input.pptx> --rules <rules.json> --task <task_name>
```

Optional:

```bash
python scripts/ppt_text_normalize/apply.py <input.pptx> \
  --rules <workdir>/ppt_text_normalize/demo/rules.json \
  --task demo \
  --output <workdir>/ppt_text_normalize/demo/output/demo_normalized.pptx
```

### Runtime rules

- `scan` never mutates the source PPTX.
- `apply` never overwrites the source PPTX.
- Generated artifacts default to `<workdir>/ppt_text_normalize/<task_name>/`.
- The built-in code lives in this directory; test PPTX files, reports, and outputs should live in a task work directory outside the source tree.

## 6. Contracts

### 6.1 Scan outputs

`scan` produces:

```text
<workdir>/
  scan_report.json
  scan_report.md
  rules.json
```

#### `scan_report.json`

Machine-readable report containing:

- deck fingerprint (filename, slide count)
- slide roster
- resolved `Page Type` + confidence per slide
- resolved `Page Submode` + confidence per slide
- hero page decision + confidence + reasons
- extracted `Text Block` inventory
- resolved `Object Slot` + confidence per text block
- resolved `Slot Variant` + confidence per text block
- resolved `Content Intent Role` where applicable
- resolved `Mutation Permission Profile`
- style fingerprints
- style-cluster summaries
- canonical-style suggestions
- ambiguity, weak-canonical, outlier, freeze, and ineligible-uniformity flags

#### `scan_report.md`

Human-readable summary containing:

- deck-level counts and ratios
- page-type and page-submode distribution
- hero detections
- `Object Slot × Slot Variant` distribution
- canonical-style recommendations
- low-confidence / ambiguous hotspots
- likely fallback / freeze / skip hotspots

### 6.2 Normalization Rules Contract (`rules.json`)

`rules.json` is auto-generated by `scan`, editable by humans if needed, and consumed by `apply` without requiring manual edits.

Recommended top-level structure:

```json
{
  "version": "0.2",
  "input_fingerprint": {
    "filename": "demo.pptx",
    "slide_count": 18
  },
  "defaults": {
    "page_modes": {
      "hero": "frozen",
      "cover": "conservative_text",
      "toc": "conservative_text",
      "chapter": "conservative_text",
      "ending": "conservative_text",
      "content": "standard",
      "unknown": "conservative_text"
    },
    "slot_overrides": {},
    "allow_size_shrink": true,
    "max_size_shrink_pt": 1.0,
    "preserve_local_emphasis": true
  },
  "page_rules": [],
  "slot_rules": [],
  "canonical_styles": [],
  "fallback_policy": {},
  "hero_policy": {}
}
```

#### `defaults`

Global policy defaults:

- page-type default normalization modes
- slot-level permission-profile overrides
- whether size shrink is allowed
- maximum size shrink
- whether local emphasis should be preserved

#### `page_rules`

Resolved page-level results, e.g.

```json
{
  "slide_index": 3,
  "resolved_page_type": "content",
  "page_type_confidence": 0.93,
  "resolved_page_submode": "content@standard",
  "page_submode_confidence": 0.88,
  "hero_page_confidence": 0.12,
  "page_normalization_mode": "standard",
  "source": "auto"
}
```

#### `slot_rules`

Resolved slot-level results, e.g.

```json
{
  "slide_index": 3,
  "block_id": "s3_sp14",
  "resolved_object_slot": "page_title",
  "slot_confidence": 0.91,
  "resolved_slot_variant": "page_title@standard_top",
  "slot_variant_confidence": 0.84,
  "content_intent_role": null,
  "hero_slot_confidence": 0.03,
  "uniformity_eligible": true,
  "mutation_permission_profile": "slot_standard",
  "source": "auto"
}
```

#### `canonical_styles`

Resolved canonical-style targets, e.g.

```json
{
  "page_type": "chapter",
  "page_submode": "chapter@uniform_series",
  "object_slot": "chapter_title",
  "slot_variant": "chapter_title@top_banner",
  "source": "majority_real_slide",
  "support": {
    "sample_count": 6,
    "core_cluster_ratio": 0.83,
    "series_cohesion": 0.79
  },
  "style": {
    "font_family": "DeckMajoritySans",
    "color": "#1F1F1F",
    "font_size_pt": 24,
    "bold": true,
    "italic": false
  },
  "permission_profile": "series_standard",
  "weak_canonical": false
}
```

#### `fallback_policy`

Explicit representation of the **Normalization Fallback Chain**:

```json
{
  "order": [
    "apply_color",
    "apply_font_family",
    "preserve_secondary_if_layout_risk",
    "shrink_size_within_limit",
    "skip_block"
  ]
}
```

#### `hero_policy`

Hero handling defaults:

```json
{
  "freeze_by_default": true,
  "page_threshold": 0.7,
  "slot_threshold": 0.72,
  "report_only": true
}
```

### 6.3 Apply outputs

`apply` produces:

```text
<workdir>/
  output/
    <input_stem>_normalized.pptx
  apply_report.json
  apply_report.md
```

#### `apply_report.json`

Per-block machine-readable mutation report with:

- resolved page type and page submode
- resolved object slot and slot variant
- content intent role when applicable
- resolved permission profile
- hero freeze decision when applicable
- confidence bundle
- before style
- target style
- applied fields
- preserved fields
- fallback steps used
- layout-risk classification
- result (`applied`, `applied_with_fallback`, `frozen`, `skipped`)
- skip or freeze reason (when present)

#### `apply_report.md`

Human-readable summary with:

- candidate block count
- applied count
- applied-with-fallback count
- frozen count
- skipped count
- field-level mutation summaries
- hero/freeze summary
- notable risky or skipped slides

## 7. Classification model

### 7.1 Overall order

Semantic resolution should follow this order:

1. `Page Type`
2. hero page detection
3. `Page Submode`
4. `Object Slot`
5. `Slot Variant`
6. `Content Intent Role` where applicable
7. `Mutation Permission Profile`

This keeps page-level context ahead of local text-slot interpretation.

### 7.2 Page Type

Supported page types in v1:

- `cover`
- `chapter`
- `toc`
- `content`
- `ending`
- `hero`
- `unknown`

`hero` is both a page-type possibility and a page-level confidence axis. A content page may still be `content` while carrying a high `hero_page_confidence` that forces a more conservative or frozen mode.

### 7.3 Hero page detection

Hero detection is two-layered.

#### Page-level hero signals

- extremely dominant slogan-like title
- very low text-block count with strong visual emphasis
- large whitespace fields
- text that behaves like a visual statement rather than structured information
- large design asymmetry with one anchor text object

#### Slot-level hero signals

- one text object dominates visual attention
- the object sits in the primary focus band or central field
- the object is visually unlike repeated informational slots nearby

Outputs:

- `hero_page_confidence`
- `hero_slot_confidence`
- `hero_reason_signals`

Default behavior:

- high hero confidence → `Hero Freeze`
- hero-like pages are reported explicitly before any mutation occurs

### 7.4 Page Submode

Supported page submodes:

- `toc@uniform_list`
- `toc@uniform_grid`
- `toc@freeform_composition`
- `chapter@uniform_series`
- `chapter@freeform_hero`
- `content@standard`
- `content@hero_mixed`
- `cover@standard`
- `cover@hero_like`
- `ending@standard`
- `ending@hero_like`

#### TOC submodes

`toc@uniform_list` signals:

- repeated items with consistent spacing and alignment
- list rhythm more than bespoke visual grouping
- styles close enough to support cross-item normalization

`toc@uniform_grid` signals:

- a TOC context marker exists, such as `目录`, `Contents`, `Agenda`, or `Outline`
- four or more numbered chapter items form two or more row and column clusters
- item title sizes and weights are close enough to imply one repeated TOC title object
- footer page numbers, ordinary numbered questions, and timeline years are excluded from the TOC vote
- title items use `toc_item@uniform_grid_title` and may normalize font family / weight only
- description items use `toc_item@uniform_grid_desc` and stay conservative

`toc@freeform_composition` signals:

- irregular item positions
- card/grid collage behavior
- substantial slot-to-slot visual variety

#### Chapter submodes

`chapter@uniform_series` signals:

- chapter pages repeat marker/title positions across the deck
- consistent series typography and geometry
- structural opener pattern can be enough even without chapter keywords:
  - large numeric chapter marker
  - adjacent large bold chapter title
  - optional subtitle / summary bullets
- marker resolves to `chapter_marker@large_number`
- title resolves to `chapter_title@standard`

`chapter@freeform_hero` signals:

- chapter pages behave like strong visual statements
- cross-chapter layout variety is too high for standardization

### 7.5 Object Slot

Supported slot candidates:

- `page_title`
- `section_title`
- `header`
- `footer`
- `toc_title`
- `toc_item`
- `chapter_title`
- `chapter_marker`
- `content_body`
- `content_label`
- `content_emphasis`
- `content_caption`
- `content_stat`
- `table_text`
- `hero`
- `unknown`

### 7.6 Slot inference sources

Use four fused signal classes:

1. **container structure** — placeholder type, table cell, text-bearing shape kind
2. **geometry** — top band, side rail, content field, footer band, center hero field
3. **style prominence** — font-size ranking, boldness, accent color use, contrast against siblings
4. **neighbor relationships** — position relative to anchor objects, lists, images, charts, and repeated card groups

This requires a new concept:

- **Neighborhood Pattern** — many slot meanings depend on local neighbors rather than isolated object features

### 7.7 Slot Variant

Variants capture layout-specific realizations of one slot, e.g.

- `page_title@standard_top`
- `page_title@left_banner`
- `toc_item@uniform_list`
- `toc_item@grid_card`
- `chapter_marker@left_rail`
- `content_body@two_col_text`
- `content_label@inline_lead`

Recognize variants from:

- alignment pattern
- repetition pattern
- sibling geometry similarity
- column/grid rhythm

### 7.8 Content Intent Role

Inside the content area, resolve:

- `content_body`
- `content_label`
- `content_emphasis`
- `content_caption`
- `content_stat`

#### Signals

`content_body`:
- longer, denser, informational prose
- main narrative text field

`content_label`:
- short label-like text
- often bold or lead-in style
- typically precedes or frames body text

`content_emphasis`:
- visually marked phrase or statement
- stronger contrast or weight relative to neighbors

`content_caption`:
- smaller supporting annotation near charts, images, or lower page bands

`content_stat`:
- number-heavy or KPI-like text
- visually isolated or paired with a short label

### 7.9 Uniformity Eligibility

A slot is not normalized just because its name repeats. First resolve:

- `uniformity_eligible = true / false`
- `uniformity_reason`

#### Usually eligible

- `header@top_chrome`
- `footer@bottom_note`
- `toc_item@uniform_list`
- `chapter_title@uniform_series`

#### Usually ineligible

- `hero@full_bleed`
- `toc_item@freeform_composition`
- `content_emphasis@visual_callout`
- `content_stat@bespoke_card`

Ineligible slots should either skip strong normalization or downgrade to a more conservative profile.

### 7.10 Series Cohesion

Introduce a **Series Cohesion** score for repeated page families such as TOC or chapter openers.

It measures:

- cross-page geometry similarity
- cross-page style similarity
- cross-page slot-pattern repeatability

Usage:

- high cohesion → stronger normalization allowed
- low cohesion → conservative text-only or freeze-like behavior

### 7.11 Anchor Object

Some pages organize nearby text around one dominant anchor object, such as:

- a hero title
- a large KPI
- a chapter marker

Detecting the **Anchor Object** improves neighboring slot interpretation and reduces accidental over-normalization of support text.

## 8. Mutation strategy matrix

### 8.1 Page defaults

#### `hero`
- `Page Normalization Mode = frozen`
- do not mutate font family, weight, size, or color by default
- only report hero page / hero slot / confidence

#### `cover`
- default mode: `conservative_text`
- prioritize `font_family`
- `font_weight` only when repeated series evidence exists
- do not change `font_size` or `color` automatically
- if strongly hero-like, downgrade to `frozen`

#### `toc`

Resolve `Page Submode` first.

`toc@uniform_list`:
- `toc_title`: may unify `font_family`, `font_weight`, and only cautiously `font_size`
- `toc_item`: prioritize `font_family`, `font_weight`, and possibly `font_size` if the list is structurally uniform
- `color` is decided last and only when the list behaves like a traditional unified TOC

`toc@uniform_grid`:
- `toc_title`: may unify `font_family`, `font_weight`, and color through `slot_standard`
- `toc_item@uniform_grid_title`: normalize `font_family` and `font_weight`; do not change `font_size` or `color`
- `toc_item@uniform_grid_desc`: normalize font family only if a canonical source exists; do not change `font_size` or `color`
- split font channels are preserved: the same `font_family` permission writes both DrawingML `a:latin` and `a:ea` from the canonical style when available

`toc@freeform_composition`:
- default to conservative behavior
- prioritize `font_family`
- avoid automatic changes to `font_size` or `color`

#### `chapter`

Resolve `Page Submode` first.

`chapter@uniform_series`:
- normalize `chapter_title` and `chapter_marker` across the series
- prioritize `font_family` and `color`
- allow `font_weight` or `font_size` only when **Series Cohesion** is strong enough

`chapter@freeform_hero`:
- treat as strongly conservative or frozen
- prioritize only `font_family` if any mutation happens at all
- freeze when hero confidence is high

#### `ending`
- similar to `cover`
- default to `font_family`-first conservative handling
- avoid automatic `font_size` and `color` changes

#### `content`
- default mode: `standard`
- actual behavior is mostly governed by **Object Slot** and **Content Intent Role** overrides

### 8.2 Slot-level defaults

#### `page_title@*`
- allowed: `font_family`, `font_weight`, `color`
- `font_size` only when repetition is strong and layout remains safe

#### `section_title@*`
- allowed: `font_family`, `font_weight`
- `color` conservative
- `font_size` not changed automatically unless the slot family is strongly repetitive

#### `header@*`
- allowed: `font_family`, `font_weight`, `color`
- `font_size` may unify when header chrome is clearly fixed across pages

#### `footer@*`
- footer must be split before color decisions:
  - `footer@org_name`
  - `footer@page_num`
  - `footer@note`
- `footer@org_name` and `footer@page_num` may use color only from their own stable variant cluster
- `footer@note` defaults to font-family only
- never mix organization names, page numbers, and notes into one color canonical

### 8.3 Content-area profiles

#### `content_body@*`
- **default profile = `typography_only`**
- mutate only:
  - `font_family`
  - `font_weight` when needed for consistency
- do **not** mutate automatically:
  - `font_size`
  - `color`
  - `italic`

This is a hard default rule because content-area size and color often encode intended information hierarchy.

#### `content_label@*`
- mutate:
  - `font_family`
  - `font_weight`
- do not mutate automatically:
  - `font_size`
  - `color`

#### `content_emphasis@*`
- preserve emphasis design by default
- mutate only `font_family` unless a stronger override is explicitly allowed
- do not automatically normalize emphasis color or size

#### `content_caption@*`
- lightly unify `font_family`
- keep size and color stable by default

#### `content_stat@*`
- may unify `font_family`
- `font_weight` only cautiously
- `font_size` and `color` remain stable by default because they often carry the visual emphasis of KPI design

#### `table_text@*`
- default to `font_family` and cautious `font_weight`
- keep `font_size` and `color` stable unless table series evidence is unusually strong

### 8.4 Permission-profile taxonomy

Recommended built-in profiles:

- `frozen`
- `typography_only`
- `conservative_text`
- `slot_standard`
- `list_standard`
- `series_standard`
- `preserve_emphasis`

Resolution order:

1. page default from `Page Type`
2. page override from `Page Submode`
3. slot override from `Object Slot`
4. slot variant override from `Slot Variant`
5. final local override from hero freeze or uniformity ineligibility

Most slots should use the defaults rather than requiring custom overrides.

## 9. Style clustering and canonical-style synthesis

### 9.1 Style Fingerprint

Each `Text Block` is normalized into a **Style Fingerprint**:

- `font_family`
- `color`
- `font_size_pt`
- `bold`
- `italic`
- `source_level` (`run`, `paragraph`, `shape/default`)

### 9.2 Two-level clustering

#### Level 1: Core Cluster

Cluster by core typographic fields first. In the upgraded model, “core” depends on the permission profile:

- in `slot_standard` or `series_standard`, core may include `font_family`, `color`, and sometimes `font_weight`
- in `typography_only`, core should be treated as `font_family` + allowed weight semantics only

#### Level 2: Secondary variation

Within one Core Cluster, observe:

- `font_size_pt`
- `bold`
- `italic`
- `color` when color is not core for that slot family

This keeps the design aligned with the permission-profile matrix rather than assuming one fixed global notion of “secondary.”

### 9.3 Voting filters

Exclude from majority voting by default:

- low-confidence slot matches
- ambiguous matches
- `unknown` slots
- style outliers
- high layout-risk blocks
- hero-frozen blocks
- uniformity-ineligible blocks
- trivial decorative text

### 9.4 Canonical Style Source order

1. `user_designated_sample`
2. `majority_real_slide`
3. `theme_or_layout_fallback`

The default path is `majority_real_slide` built from high-quality, eligible matches only.

Sample decks and tests may demonstrate defect patterns, but production logic must not
hard-code sample filenames, slide numbers, institution names, or specific font families
as correctness conditions. A font is only a target when it wins the eligible canonical
cluster for the current deck and slot.

### 9.5 Canonical-style synthesis

Canonical style is field-synthesized, not copied wholesale from one block.

- `font_family` almost always participates
- `font_weight` participates for slots where it encodes semantic consistency
- `font_size` and `color` participate only when the slot family and permission profile explicitly allow them

Canonical synthesis should therefore be profile-aware rather than globally identical across all slot types.

### 9.6 Weak Canonical

Mark a canonical style as **Weak Canonical** when:

- `sample_count < 3`, or
- `core_cluster_ratio < 0.6`, or
- `series_cohesion < threshold` for series-based slots

`apply` treats Weak Canonical sources conservatively: in the MVP, weak canonical style may apply `font_family` only and must not apply `bold`, `color`, or `font_size`.

## 10. Apply execution model

### 10.1 Apply contract

For each candidate `Text Block`, `apply` must:

1. resolve its page mode and final permission profile
2. honor any hero freeze or uniformity ineligibility first
3. apply only the fields allowed by that permission profile
4. preserve text content
5. preserve text-box geometry
6. avoid moving non-text objects
7. invoke the fallback chain when needed
8. produce a new PPTX instead of modifying the input in place

### 10.2 Emphasis-Preserving Apply

Use a paragraph/run hybrid mutation strategy:

- for blocks with effectively uniform style, mutate the allowed base style cleanly
- for blocks with meaningful local emphasis, normalize the allowed base style while preserving run-level emphasis where possible
- for table cells, follow the same rule at cell-text granularity
- for `content_emphasis` and hero-like slots, prefer preservation over normalization

### 10.3 Layout Risk model

The current Safe MVP uses heuristic estimation rather than renderer-accurate simulation.

Risk inputs:

- text-box width/height
- paragraph count
- run count
- current font and size
- target font and size
- text length
- CJK / Latin / numeric composition
- current density or near-capacity hints
- slot type and permission profile

Risk levels:

- `low`
- `medium`
- `high`

Risk reasons may include:

- `font_family_width_risk`
- `multi_paragraph_height_risk`
- `bold_expansion_risk`
- `near_capacity_risk`

### 10.4 Layout-risk estimation

Approximate width using character-class heuristics and font-family width coefficients:

- CJK ≈ `font_size * 1.0`
- Latin ≈ `font_size * 0.5~0.65`
- numeric ≈ `font_size * 0.55`

Estimate height from:

- expected line count
- paragraph count
- line-height approximation
- available box height margin

The goal is not render-perfect prediction; the goal is conservative detection of likely wrapping or truncation.

### 10.5 Hero Freeze

Hero handling happens before the normal fallback chain.

- high `hero_page_confidence` or `hero_slot_confidence` → default freeze
- freeze result is reported explicitly
- frozen blocks do not enter style mutation
- user overrides remain possible through `rules.json`, but they are not the default flow

### 10.6 Normalization Fallback Chain

Apply exactly this order **only when the permission profile allows the corresponding field**:

1. `apply_color`
2. `apply_font_family`
3. `preserve_secondary_if_layout_risk`
4. `shrink_size_within_limit`
5. `skip_block`

Interpretation:

- if a permission profile bans color changes, step 1 becomes a no-op
- if a permission profile bans size changes, step 4 becomes unavailable
- `content_body@*` normally skips both color and size mutation, even before layout-risk logic is considered

### 10.7 Skip Reason catalog

Use normalized codes, e.g.

- `role_low_confidence`
- `page_type_low_confidence`
- `page_submode_low_confidence`
- `hero_frozen`
- `uniformity_ineligible`
- `font_family_layout_risk`
- `secondary_style_layout_risk`
- `size_shrink_limit_exceeded`
- `table_cell_overflow_risk`
- `unsupported_text_structure`
- `style_source_weak_canonical`

## 11. Validation strategy

The current Safe MVP is successful only if it proves it is truly an automatic text-style normalization pipeline rather than a hidden layout editor.

### 11.1 Validation goals

- `scan` auto-generates reports and rules
- `apply` runs without requiring manual rule edits
- slot-appropriate style consistency improves
- hero-like content is reported and frozen by default
- content-area destructive mutations are avoided by default
- content, geometry, slide count, and non-text positions stay unchanged
- out-of-scope text structures remain untouched
- all changes, freezes, fallbacks, and skips are auditable

### 11.2 Validation layers

#### Layer 1: pure logic tests

Test:

- page-type and page-submode classification
- hero detection
- object-slot and content-intent inference
- style clustering
- canonical-style synthesis
- layout-risk estimation
- permission-profile gating
- fallback sequencing

#### Layer 2: OOXML integration tests

Run scan/apply on small PPTX fixtures, then compare unpacked OOXML before/after.

Expected changes:

- text style nodes (`rPr`, paragraph defaults, table cell text styling)

Expected invariants:

- text content unchanged
- shape geometry unchanged
- slide order unchanged
- non-text object XML unchanged
- SmartArt/chart/notes/master/layout source text unchanged

#### Layer 3: end-to-end deck validation

Use sample decks from an external task work directory to validate full pipeline behavior and reporting quality.

### 11.3 Sample matrix

At minimum, validate with:

1. happy-path content deck
2. mixed page-type deck
3. local-emphasis deck
4. high-risk layout deck
5. table-heavy deck
6. TOC uniform-list deck
7. TOC uniform-grid deck with mixed Latin / East Asian font channels
8. TOC freeform-composition deck
9. chapter uniform-series deck
10. hero-heavy or hero-mixed deck

### 11.4 Key metrics

`scan` metrics:

- `slide_count`
- `text_block_count`
- `page_type_resolved_ratio`
- `page_submode_resolved_ratio`
- `object_slot_resolved_ratio`
- `hero_page_count`
- `hero_slot_count`
- `low_confidence_block_ratio`
- `canonical_style_count`
- `weak_canonical_count`

`apply` metrics:

- `candidate_block_count`
- `applied_count`
- `applied_with_fallback_count`
- `frozen_count`
- `skipped_count`
- `font_family_changed_count`
- `font_weight_changed_count`
- `destructive_change_block_count`

Invariant metrics:

- `content_changed_count == 0`
- `geometry_changed_count == 0`
- `non_text_object_changed_count == 0`

### 11.5 Acceptance bar

Safe MVP passes when:

- the automation-first pipeline runs end-to-end by default
- slot-appropriate typography improves without over-flattening content-area styling
- hero-like content is frozen by default and reported clearly
- TOC and chapter pages avoid destructive over-normalization when they are freeform or low-cohesion
- all skips and freezes have normalized reasons
- no content or geometry drift occurs
- out-of-scope text structures are untouched

## 12. Risks and non-goals

### Key risks

1. page-type / slot / submode misclassification
2. heuristic font-width mismatch with real rendering
3. OOXML inheritance complexity
4. imperfect local-emphasis preservation
5. underestimated TOC/chapter variant complexity
6. false-positive hero detection

### Mitigations

- confidence + margin scoring
- voting filters
- weak-canonical handling
- conservative layout-risk policy
- permission-profile gating
- hero freeze defaults
- strict scope v1 boundaries
- normalized reporting

### Explicit non-goals

- redesigning slides
- changing page layout
- rewriting text content
- full OOXML text-surface coverage
- guaranteeing zero skip blocks
- forcing unique pages into traditional typography systems

## 13. Evolution path inside the built-in skill surface

### Phase A: current built-in slice

Deliver in `scripts/ppt_text_normalize/`:

- local `CONTEXT.md`
- this design document
- built-in code
- schemas
- report examples

### Phase B: contract stabilization

Once sample decks are stable:

- freeze the main schema structure
- normalize naming and reason codes
- remove unused fields
- verify page-submode and permission-profile vocabulary is stable enough for broader built-in reuse

### Phase C: optional command-surface expansion

Move toward:

- additional helper entrypoints only when the built-in contract genuinely expands
- documentation updates in `scripts/README.md` and script docs
- stricter review/apply contracts only after those commands are implemented

### Phase D: optional enhancements

Possible future enhancements:

- use `pptx_template_import` metadata as auxiliary signals
- add explicit sample-page overrides
- improve font-width calibration
- deepen table-role refinement
- add richer hero-override UI

These are future enhancements, not current Safe MVP requirements.

## 14. Final alignment check

This design remains aligned with the revised objective:

- it is **automation-first**
- it is focused on **text style normalization**
- it prefers **same-object-slot consistency** over bulk page-wide flattening
- it protects **content and layout**
- it freezes hero-like design by default
- it keeps content-area size and color changes conservative by default
- it is **auditable**
- it is structured for conservative extension inside the built-in `ppt-master` tool surface

## 15. OOXML namespace preservation rule

Generated PPTX files must remain PowerPoint-openable without repair. A known failure mode is rewriting slide XML through raw `ElementTree.tostring(...)`: ElementTree may rename namespace declarations such as `p14` to `ns4` while `mc:Choice Requires="p14"` still references the original prefix. PowerPoint then treats the markup-compatibility branch as invalid and may delete repaired content.

Implementation requirements:

- all modified slide XML must be serialized via `serialize_xml_preserving_prefixes()`
- `mc`, `p14`, `p15`, `p16`, `a14`, and `a16` prefixes must stay stable when present
- apply must run `validate_markup_compatibility_prefixes()` after saving the PPTX
- tests must cover `Requires="p14"` plus `xmlns:p14` preservation and reject `xmlns:ns*` leakage

This is a release-blocking invariant, not an optional cleanup.
