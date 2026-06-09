# PPT Text Normalize

This context captures current domain language for the built-in Safe MVP text style normalization capability under `scripts/ppt_text_normalize/`. It extends the root `CONTEXT.md` without redefining its higher-level release or normalization vocabulary.

## Language

**Text Block**:
One text container instance that can be independently classified, analyzed, and normalized within Normalization Scope v1.
_Avoid_: Whole slide text, random paragraph fragment

**Style Fingerprint**:
The normalized style summary of one Text Block used for clustering and comparison.
_Avoid_: Raw XML dump, visual guess

**Page Type Confidence**:
The scored confidence that one slide belongs to one Page Type.
_Avoid_: Hard-coded truth, position-only guess

**Role Match Confidence**:
The scored confidence that one Text Block belongs to one semantic target class.
_Avoid_: Binary certainty, manual label only

**Page Submode**:
The layout family inside one Page Type, such as `toc@uniform_list` or `chapter@freeform_hero`, used to decide normalization aggressiveness.
_Avoid_: Pure mood tag, replacement for Page Type

**TOC Uniform Grid**:
The `toc@uniform_grid` Page Submode for directory pages whose numbered chapter items form a repeated multi-row, multi-column grid.
_Avoid_: Generic card layout, ordinary numbered question grid, timeline

**Chapter Opener**:
A chapter page pattern with a large numeric marker, adjacent large title, and optional subtitle or summary bullets.
_Avoid_: Ordinary content page with a big statistic

**Footer Variant**:
The refined footer slot family, such as `footer@org_name`, `footer@page_num`, or `footer@note`, used before any footer color vote.
_Avoid_: One mixed footer bucket for all bottom-band text

**Split Font Channel**:
The separate Latin and East Asian DrawingML font channels, represented as `font_family` and `east_asia_font_family` in Style Fingerprint.
_Avoid_: One string that silently overwrites both scripts

**Page Normalization Mode**:
The default mutation posture for one page before slot overrides, such as `frozen`, `conservative_text`, or `standard`.
_Avoid_: Per-block exception list, hidden policy

**Object Slot**:
The semantically stable text target to compare across similar pages, such as `page_title`, `toc_item`, `chapter_marker`, `header`, or `footer`.
_Avoid_: Generic title/body, raw coordinate band

**Slot Variant**:
The layout-specific refinement of one Object Slot, such as `page_title@standard_top` or `toc_item@uniform_list`.
_Avoid_: One-off ad hoc name, absolute position tag

**Content Intent Role**:
The finer-grained purpose of a text object inside the content area, such as `content_body`, `content_label`, `content_emphasis`, `content_caption`, or `content_stat`.
_Avoid_: Whole content blob, body-everything

**Mutation Permission Profile**:
The allowed mutation scope for one page or slot decision, such as `frozen`, `typography_only`, `conservative_text`, `slot_standard`, `list_standard`, `series_standard`, or `preserve_emphasis`.
_Avoid_: Implicit side effect, style free-for-all

**Core Cluster**:
The dominant cluster formed from core typographic fields within one semantic comparison group.
_Avoid_: Full-style exact match group, arbitrary bucket

**Style Outlier**:
A Text Block whose Style Fingerprint deviates enough from the dominant cluster that it should be excluded from canonical-style voting by default.
_Avoid_: Normal variation, manual exception only

**Weak Canonical**:
A canonical style produced from insufficient or weakly convergent evidence and therefore applied more conservatively.
_Avoid_: Stable default, trusted majority

**Uniformity Eligibility**:
Whether a slot or slot series is structurally suitable for normalization rather than bespoke composition.
_Avoid_: Assume every repeated label should unify

**Series Cohesion**:
The cross-page consistency score of the same slot family across a page series, used before stronger normalization.
_Avoid_: Single-page majority, visual hunch

**Neighborhood Pattern**:
The local arrangement of nearby text and graphics that helps infer a Text Block's semantic role.
_Avoid_: Isolated block guess, page-global guess only

**Anchor Object**:
The dominant visual or structural object around which nearby text roles are interpreted.
_Avoid_: Random big text, entire slide

**Hero Detection Policy**:
The dual-layer decision that scores both page-level and slot-level hero candidates and freezes them by default.
_Avoid_: Hidden heuristic, auto-edit hero

**Hero Freeze**:
The default behavior that reports hero-like content but does not mutate it unless the user explicitly overrides that decision.
_Avoid_: Silent skip, normal conservative handling

**Layout Risk**:
The estimated risk that applying a target style will introduce wrapping, truncation, or other layout drift while geometry stays fixed.
_Avoid_: Rendering truth, cosmetic preference

**Ambiguous Match**:
A classification result whose top candidate scores are too close to distinguish reliably.
_Avoid_: Confident match, unknown block

**Skip Reason**:
The normalized reason code explaining why Apply chose not to mutate a Text Block.
_Avoid_: Free-form excuse, hidden failure

**Mutation Permission Gate**:
The field-level safety decision that determines which style fields may be changed for one Text Block.
_Avoid_: UI approval, final user permission, free-form style editing

**Visual Review Gate**:
The live-preview review layer that lets users inspect overlays, exclude blocks, change target groups, create user groups, and save structured Review Decisions before Apply mutates a PPTX.
_Avoid_: Markdown-only confirmation, browser-side PPTX editing, geometry editor

**Review Model**:
The read-only browser input generated from current `rules.json`, `scan_report.json`, and extracted Text Blocks.
_Avoid_: User decision file, mutable rules file, replacement for scan semantics

**Review Decisions**:
The structured browser output saved as `review_decisions.json`.
_Avoid_: Free-form comments, SVG annotations, direct PPTX changes

**Reviewed Rules**:
The compiled `rules_reviewed.json` file that preserves original rules and adds `review_gate` plus `reviewed_overrides` for Apply.
_Avoid_: Mutated original `rules.json`, browser-authored rules, final PPTX output

## Relationships

- A **Text Block** has one **Style Fingerprint**
- A slide receives one **Page Type Confidence** during scan
- A **Text Block** receives one **Role Match Confidence** during scan
- One **Page Type** may resolve into one **Page Submode**
- A **TOC Uniform Grid** requires TOC context plus repeated chapter-number item structure, and excludes footer page numbers, timeline years, and ordinary numbered questions
- A **Chapter Opener** may resolve to `chapter@uniform_series`; its numeric marker becomes `chapter_marker@large_number`, and its adjacent title becomes `chapter_title@standard`
- A **Footer Variant** must be resolved before color normalization; organization names, page numbers, and notes do not share a color canonical
- A **Split Font Channel** is normalized under the `font_family` permission but writes `a:latin` and `a:ea` separately
- One **Page Submode** implies one default **Page Normalization Mode**
- One **Object Slot** may refine into one **Slot Variant**
- One **Slot Variant** may refine into one **Content Intent Role** when the slot belongs to the content area
- One **Object Slot** or **Slot Variant** may override the page default through a **Mutation Permission Profile**
- One **Core Cluster** may yield one canonical style candidate
- A **Style Outlier** is excluded from canonical-style voting by default
- A **Weak Canonical** triggers more conservative apply behavior; in the MVP it may apply font family only
- **Uniformity Eligibility** must be true before stronger normalization is allowed
- **Series Cohesion** gates stronger cross-page normalization for TOC and chapter series
- A **Neighborhood Pattern** helps resolve **Object Slot** and **Content Intent Role**
- An **Anchor Object** stabilizes nearby semantic interpretation
- The **Hero Detection Policy** may emit one **Hero Freeze**
- A **Layout Risk** assessment may trigger the Normalization Fallback Chain
- A skipped Text Block records exactly one **Skip Reason**
- An **Ambiguous Match** lowers trust in automatic canonical-style selection
- The **Visual Review Gate** consumes a **Review Model** and produces **Review Decisions**
- **Review Decisions** compile into **Reviewed Rules** before Apply can consume reviewed overrides
- The browser may save **Review Decisions**, but only Apply may mutate PPTX content

## Example dialogue

> **Dev:** "These two blocks are both near the top, so they should get the same style, right?"
> **Domain expert:** "Only if they resolve to the same **Object Slot** and compatible **Slot Variant**. Top position alone is not enough."

> **Dev:** "Why didn't the content paragraph color change to match the page title?"
> **Domain expert:** "Because that block resolved to `content_body`, whose **Mutation Permission Profile** is `typography_only`, so color is treated as destructive by default."

> **Dev:** "Why did the chapter opener remain mostly unchanged?"
> **Domain expert:** "It was classified as `chapter@freeform_hero`, the **Hero Detection Policy** raised confidence, and **Hero Freeze** kept the page in a frozen or near-frozen posture."

## Flagged ambiguities

- "same object location" could have meant raw coordinate proximity — resolved: it means the same **Object Slot** plus compatible **Slot Variant**.
- "content area" could have implied one undifferentiated body bucket — resolved: content-area text may refine into a **Content Intent Role** before normalization is decided.
- "hero page" could have implied an all-or-nothing page label — resolved: **Hero Detection Policy** works at both page and slot level, with **Hero Freeze** as the default behavior.


### Field Gate Override

A per-block visual review decision that widens the editable field set after the
user explicitly chooses advanced field override. It can open `font_family`,
`bold`, and `color`, but never `font_size_pt` in the MVP and never for
unsupported blocks. It does not itself mutate every opened field; it only
widens the gate so the per-block `fields` decision can include those fields.
