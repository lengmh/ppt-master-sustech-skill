---
deck_id: sustech_academic_official
kind: deck
category: scenario
summary: Official academic template for course reports, research briefings, thesis defenses, and seminars.
keywords: [SUSTech, Academic, Official, University, Defense]
primary_color: "#003F43"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
source_canvas_width: 1280
source_canvas_height: 720
source_viewbox: "0 0 1280 720"
replication_mode: standard
native_structure_mode: structured
page_count: 8
---

# SUSTech Academic Official - Design Specification

## I. Template Overview

SUSTech Academic Official (`sustech_academic_official`, category `scenario`) is a light, school-official academic template for 学术汇报、课程汇报、研究汇报、论文答辩、组会分享. Design tone: Official, academic, restrained, school-branded. Chinese is the default language. Use university identity rather than a generic defense-deck appearance.

Reference: `ppt/materials/sustech_templates/SUSTech_Academic_Template.pptx`, slides 1, 2, 3, 5, 6, 8, 10, 12, 14, 16 reviewed.

Canvas: 1280 × 720 px, 16:9, `viewBox="0 0 1280 720"`. Content-family shell: title x=92; top divider y=76; section-name baseline y=106; footer divider y=688; footer text baseline y=704. Top-right logo: x=1060, y=13, width=220, height=66. Flexible content zone: x=72, y=132, width=1136, height=534. Visual and text-safe zones both keep a fixed 20 px safety edge from shell edges and the footer divider.

## II. Color Scheme

| Role | Value | Use |
|---|---|---|
| Primary Deep Teal | `#003F43` | Brand headings and strong emphasis |
| Primary Orange | `#E3660D` | Divider accents, arrows, emphasis strokes |
| Secondary Cyan | `#01ABA8` | Secondary corner cues |
| Warning Dark Red | `#B63742` | Key titles and cautionary emphasis |
| Background White | `#FFFFFF` | Main background and neutral cards |
| Soft Panel Gray | `#EAF1F0` | Cool-secondary cards |
| Warm Panel | `#F6EBDF` | Warm-secondary and emphasis cards |
| Soft Footer Ground | `#F8F7F5` | Cover lower/support field |
| Border Gray | `#CECECE` | Dividers, borders, shell outlines |
| Primary Text | `#1D1C1C` | Body text |
| Secondary Text | `#585555` | Descriptions and labels |
| Tertiary Text | `#9D9D9D` | Footer, helper text, captions |
| Placeholder Text | `#A8A4A1` | Template-only copy |

## III. Typography System

Primary stack: `"Microsoft YaHei", Arial, sans-serif`; title support: `Arial, sans-serif`; formulas: `"Cambria Math", "Times New Roman", serif`.

| Usage | Size | Weight |
|---|---|---|
| Cover title | 52px | Bold |
| Cover subtitle / ending | 34–60px | Bold |
| Content / TOC title | 32px | Bold |
| Chapter title | 50px | Bold |
| TOC item title | 27px | Bold |
| Card / block title | 20–24px | Bold |
| Section name | 26.7px / 20pt | Regular |
| Body | 15–22px | Regular |
| Annotation | 14–16px | Regular |
| Page number | 16px | Bold |
| Chapter number | 176px | Bold |

Manually wrap long Chinese/English text and mixed formula-symbol lines with multiple `<text>` nodes or `<tspan>`. Prefer readable multiline blocks; never assume a long formula or native PPT text box will fit automatically. Test line fit before export, preserving title hierarchy and the main visual area.

## IV. Signature Design Elements

Brand shell: standard top-left school motif where applicable; merged top-right logo; fixed footer text `Southern University of Science and Technology`.

Cover uses scenic campus imagery and the merged top-right logo, without the extra top-left motif. Ending uses scenic imagery, merged logo and a simplified closing structure. TOC, chapter and content families use motif + logo + footer rather than large scenic imagery, sharing divider/footer rhythm. Content titles use an orange lead divider and gray continuation.

### Fixed Assets

These are not generated-content placeholders. Paths resolve from the workspace `images/` directory.

| Asset | Status |
|---|---|
| `full_top_right_school_logo.png` | Active merged logo/structure |
| `cover_campus_bg.jpg` | Active cover scenery |
| `ending_campus_bg.jpg` | Active ending scenery |
| `top_left_motif_standard.png` | Active motif |
| `school_logo.png` | Legacy; not for current layouts |
| `top_left_motif.png` | Legacy; not for current layouts |
| `top_right_logo_structure.png` | Legacy; not for current layouts |

### Content-family Rules

Use weak framing and strong hierarchy. Default cards are white with gray borders, light cyan, or light warm. Parallel cards may mix cyan/warm or consistently use white-outline or one secondary family. Deep teal belongs primarily to headings; a deep-teal background is exceptional hero emphasis, usually at most one card and often none. Body text uses primary/secondary text colors; orange marks emphasis, connectors or short labels, not large paragraphs.

Content pages require a page number. Embed any section numbering in `{{PAGE_TITLE}}`; `SECTION_NUM` and `SOURCE` are not active fields. Use the working area fully before adding gutters, retaining its 20 px safety edge. `03_content.svg` is an open composition shell, not a prescribed card count, image/text-slot count or equal split.

## V. Page Roster

| File | Design and supported fields |
|---|---|
| `01_cover.svg` | Light official opening with scenic lower field and merged logo only. `{{TITLE}}`, `{{SUBTITLE}}`, `{{AUTHOR}}`, `{{DATE}}`; academic identity stays cover-only. No department/email. |
| `02_toc.svg` | Motif, logo, official footer and content-style title. Canonical indexed title/description fields `1..N`; six visible rows currently. Numbering may be decorative and needs no dedicated numeric field. |
| `02_chapter.svg` | Large chapter number and title: `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`. No subtitle or fixed descriptor. |
| `03_content.svg` | Free-composition summary/mixed-information base. `{{CONTENT_AREA}}` is an open stage; use light/white-outline parallel cards before exceptional dark hero emphasis. |
| `03_content_text_image.svg` | Image-led asymmetric reference: a dominant figure with compact reading guidance, not co-equal text mass or a rigid layout. |
| `03_content_formula_chart.svg` | Evidence-led reference: formula, chart, or balanced reasoning; neither requires the other. Weak derivation/logic/arrow anchors are allowed. |
| `03_content_process.svg` | Flexible process reference: process may dominate, guide, or fuse with content; the lower area may combine explanation, methods, results and applications. |
| `04_ending.svg` | Scenic official closing with `{{THANK_YOU}}` only; no contact field. |

## VI. Layout Modes (Recommended)

Choose free composition for mixed summaries/conclusions/overviews; image-led asymmetry for figures/screenshots; evidence-led reasoning for formulas/charts/proof/benchmarks; process-led or process-plus-content for methods, systems and staged explanations. Match hierarchy to the message, avoid forced equal splits, and expand the main visual/reasoning area rather than leave empty text boxes. Content variants are composition references, not fixed execution specifications.

## VII. Spacing Specification

Retain the shell coordinates in §I. Card padding: 18–30px; block gaps: 20–28px; caption strips: 28–36px; rounded corners: 12–22px. Use lower space before adding gutters, maintaining the 20 px footer/shell safety band. When text grows, prefer wrapping and vertical expansion over weakening title hierarchy. Editable text frames must contain their carriers; frame changes do not authorize changing locked brand assets.

## VIII. SVG Technical Constraints

Keep `viewBox="0 0 1280 720"`. Use inline attributes, semantic asset references and manual text wrapping; no `<style>`, `class` or `@font-face`. Use `fill-opacity`/`stroke-opacity`, not `rgba()`.

This template excludes `<foreignObject>`, `<textPath>`, `<clipPath>`, `mask`, `<script>`, `<animate*>`, `<iframe>`, `<symbol> + <use>`, and `<g opacity="...">` for PPT output. Check long text/formulas for fit; preserve image/evidence space against explanatory spillover.

## IX. Placeholder Specification

- Cover: `{{TITLE}}`, `{{SUBTITLE}}`, `{{AUTHOR}}`, `{{DATE}}`.
- TOC: `{{TOC_ITEM_1_TITLE}}` … `{{TOC_ITEM_N_TITLE}}`; `{{TOC_ITEM_1_DESC}}` … `{{TOC_ITEM_N_DESC}}`.
- Chapter: `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`.
- Content: `{{PAGE_TITLE}}` (including numbering if needed), `{{SECTION_NAME}}`, `{{CONTENT_AREA}}`, `{{PAGE_NUM}}`.
- Ending: `{{THANK_YOU}}` only.
- Excluded: `{{DEPARTMENT}}`, `{{EMAIL}}`, `{{SECTION_NUM}}`, `{{SOURCE}}`, `{{CONTACT_INFO}}`.

These are the authoritative content-family rules for validation decks. Do not expand academic identity onto other pages; keep indexed TOC naming and the simplified ending.
